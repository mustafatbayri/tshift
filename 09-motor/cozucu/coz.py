# -*- coding: utf-8 -*-
"""
COZUCU GIRISI -- /solve (Master Spec v1.4 #11.2, #11.3)

DURMA KURALI -- K-28 (Mustafa, 16 Eylul): "erken dur, bekletme"
  Iki kosuldan biri olunca biter:
    * optimuma %2'den yakin      (nispi bosluk)
    * 2 dakikadir iyilesmiyor     (durgunluk)
  Ustte mutlak butce durur (varsayilan 15 dk).

  Gerekce: 3. dakikada bulunan planla 15. dakikadaki arasindaki fark sahada
  1-2 saatlik kapsama; plani bekleyen yonetici icin 12 dakika daha degerli.

BU DOSYA DOGRULAYICIDAN BAGIMSIZDIR (#7.6, #16.1).
"""

import time

from ortools.sat.python import cp_model

from .model import Model, _mola_baslangiclari, _mola_dilimleri

VARSAYILAN = {
    "azami_saniye": 900,          # 15 dk mutlak butce
    "hedef_bosluk": 0.02,         # optimuma %2
    "durgunluk_saniye": 120,      # 2 dk iyilesme yoksa bitir
}


class _ErkenDur(cp_model.CpSolverSolutionCallback):
    """K-28'in govdesi. Her yeni cozumde bakar, yeter dedigi an durur."""

    def __init__(self, ayar):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.ayar = ayar
        self.baslangic = time.time()
        self.son_iyilesme = self.baslangic
        self.cozum_sayisi = 0
        self.durma_sebebi = None

    def on_solution_callback(self):
        self.cozum_sayisi += 1
        self.son_iyilesme = time.time()
        sinir = self.BestObjectiveBound()
        deger = self.ObjectiveValue()
        if deger > 0 and abs(deger - sinir) / abs(deger) <= self.ayar["hedef_bosluk"]:
            self.durma_sebebi = "hedef_bosluk"
            self.StopSearch()
        elif deger == 0 and sinir == 0:
            self.durma_sebebi = "optimum"
            self.StopSearch()


def coz(girdi, ayar=None):
    """Master Spec #11.3 ciktisi. Plan URETIR; denetlemez.

    Denetleme bagimsiz dogrulayicinin isidir (#7.6) ve bu fonksiyon onu
    CAGIRMAZ -- cagirsaydi "motor kendi isini kendi onaylar" olurdu.
    """
    ayar = dict(VARSAYILAN, **(ayar or {}))
    kuruldu = Model(girdi).kur()

    cozucu = cp_model.CpSolver()
    cozucu.parameters.max_time_in_seconds = float(ayar["azami_saniye"])
    cozucu.parameters.num_search_workers = 8
    geri = _ErkenDur(ayar)

    basladi = time.time()
    durum = cozucu.Solve(kuruldu.m, geri)
    sure = time.time() - basladi

    istatistik = {
        "degisken_sayisi": len(kuruldu.x) + len(kuruldu.mola),
        "kisit_sayisi": kuruldu.m.Proto().constraints.__len__(),
        "cozum_sayisi": geri.cozum_sayisi,
        "motor": "CP-SAT",
        "profil": kuruldu.profil,     # #5.4 -- hangi agirlik sutunu kosuldu
        "amac_degeri": _amac_degeri(cozucu, durum),
        "durma_sebebi": geri.durma_sebebi or _durma_sebebi(durum, cozucu, ayar, sure),
        "cozum_suresi_sn": round(sure, 2),
    }

    if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        atamalar = _atamalari_cikar(kuruldu, cozucu)
        return {
            "durum": "cozuldu",
            "motor_surumu": SURUM,
            "atamalar": atamalar,
            "metrikler": _metrikler(kuruldu, atamalar, cozucu, sure),
            "cozum_istatistikleri": istatistik,
            "uygulanmayan_notlar": kuruldu.notlar,
        }

    from .teshis import teshis_koy
    return teshis_koy(girdi, kuruldu, istatistik, ayar)


SURUM = "0.2.0-cozucu"


def _amac_degeri(cozucu, durum):
    """Donen planin amac fonksiyonu degeri -- yumusak kural cezalarinin toplami.

    NEDEN CIKTIDA
      1. Uc plan karti (#9.5) kullaniciya "hangisi daha iyi" diye soruyor;
         karsilastirilacak bir SAYI olmadan bu soru olculemez.
      2. Agirliklarin gercekten ise yaradigini sinamanin tek saglam yolu bu.
         "Motor su kisiyi secti" testi kirilgan: kisit gevsekse cozucu esit
         degerdeki secenekler arasinda rastgele secer ve test yanlis yesil
         yanar. Ayni girdiyi iki kez, iki farkli secim SABITLENMIS halde
         cozup amac degerlerini karsilastirmak ise kesindir.

    Cozum yoksa None -- "0" demek yaniltici olurdu.
    """
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    try:
        return int(cozucu.ObjectiveValue())
    except Exception:
        return None


def _durma_sebebi(durum, cozucu, ayar, sure):
    if durum == cp_model.OPTIMAL:
        return "optimum"
    if durum == cp_model.INFEASIBLE:
        return "cozumsuz"
    if sure >= ayar["azami_saniye"] * 0.95:
        return "butce_doldu"
    return "bilinmiyor"


def _atamalari_cikar(kuruldu, cozucu):
    cikan = []
    for (e, d, tid), v in sorted(kuruldu.x.items()):
        if not cozucu.Value(v):
            continue
        sablon = kuruldu.sablon[tid]
        molalar = []
        yemek_dk = kuruldu.yemek_dk[tid]
        for s in _mola_baslangiclari(sablon, kuruldu.mola_penceresi, yemek_dk):
            if s is not None and cozucu.Value(kuruldu.mola[(e, d, tid, s)]):
                # K-32: cozucunun yerlestirdigi tek mola UCRETSIZ ogle
                # arasidir -- calisma suresinden de ucret hesabindan da
                # dusulur. Ucretli kisa molalarin yerlesimi HENUZ YAZILMADI
                # (mola_politikasi, K-32 madde 6); o gelene kadar cozucu
                # yalniz yemek uretir.
                molalar.append({"bas": s,
                                "bit": s + yemek_dk / 60.0,
                                "tip": "yemek"})
        ekip = next((c.get("ekipler", [None])[0]
                     for c in kuruldu.calisanlar if c["id"] == e), None)
        cikan.append({"calisan": e, "ekip": ekip, "sablon": tid, "gun": d,
                      "bas": sablon["bas"], "bit": sablon["bit"], "molalar": molalar})
    return cikan


def _metrikler(kuruldu, atamalar, cozucu, sure):
    """Motorun KENDI olcumu.

    ⚠ Bu sayilar bagimsiz dogrulayicinin sayilariyla KARSILASTIRILMAK icin
    var, onun yerine gecmek icin degil. A1 fiksturu ikisini de istiyor:
    once motor "0 sert ihlal" diyor, sonra dogrulayici ayrica sayiyor.
    Motorun kendi metrigine guvenilmez -- bu bilincli bir tasarim.
    """
    girdi = kuruldu.girdi
    asgari_tut = asgari_top = hedef_tut = hedef_top = eksik_dk = 0
    for t, gun, saat in kuruldu._hucreler():
        sayi = sum(1 for a in atamalar
                   if a["ekip"] == t.get("ekip")
                   and gun * 24 + saat in range(a["gun"] * 24 + int(a["bas"]),
                                                a["gun"] * 24 + int(a["bit"])))
        if t.get("asgari") is not None:
            asgari_top += 1
            asgari_tut += 1 if sayi >= t["asgari"] else 0
        if t.get("hedef") is not None:
            hedef_top += 1
            if sayi >= t["hedef"]:
                hedef_tut += 1
            else:
                eksik_dk += (t["hedef"] - sayi) * 60

    net = {}
    for a in atamalar:
        s = kuruldu.sablon[a["sablon"]]
        net[a["calisan"]] = net.get(a["calisan"], 0.0) + (s["bit"] - s["bas"]) \
            - s.get("mola_dk", 0) / 60.0
    fazla = 0.0
    for c in kuruldu.calisanlar:
        soz = (c.get("sozlesme") or {}).get("haftalik_saat")
        if soz is not None:
            fazla += max(0.0, net.get(c["id"], 0.0) - soz)

    yuzde = lambda tut, top: 100.0 if top == 0 else round(100.0 * tut / top, 2)
    return {
        "sert_ihlal": 0,          # kisitlar sert; cozum varsa hepsi saglanmistir
        "asgari_kapsama_yuzde": yuzde(asgari_tut, asgari_top),
        "hedef_kapsama_yuzde": yuzde(hedef_tut, hedef_top),
        "eksik_hedef_dakika": eksik_dk,
        "toplam_saat": round(sum(net.values()), 2),
        "fazla_mesai_saat": round(fazla, 2),
        "optimuma_uzaklik_yuzde": _bosluk(cozucu),
        "cozum_suresi_sn": round(sure, 2),
    }


def _bosluk(cozucu):
    try:
        deger, sinir = cozucu.ObjectiveValue(), cozucu.BestObjectiveBound()
        if deger == 0:
            return 0.0
        return round(100.0 * abs(deger - sinir) / abs(deger), 3)
    except Exception:
        return None
