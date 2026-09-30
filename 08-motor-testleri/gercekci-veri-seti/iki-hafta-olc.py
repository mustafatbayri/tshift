# -*- coding: utf-8 -*-
"""
IKI HAFTA -- gecmis veri olmadan motor ne kaciriyordu? (T-28, olcum araci)

MUSTAFA'NIN ONERISI (30 Eylul)
  "Gecmis datayi test etmek amacli test planini iki asamali yaparsak...
   once 1 hafta sonrasini ve ondan sonra diger haftayi, bu sekilde elimizde
   gecmis data olur."

NE YAPAR
  1. Hafta 1 cozulur (%95 seti, 0.1 olcek -- bekcilerle ayni ayar).
  2. Hafta 1'in atamalari hafta 2'nin GECMISI olur: gun - 7.
     Gecmis TAM kabul edilir (`gecmis_bilinen_gunler` = -7..-1): plan
     bilindigi icin bilinmeyen gun yok.
  3. Hafta 2 IKI KEZ cozulur:
       * gecmissiz  -- 30 Eylul'e kadarki motor boyle calisiyordu
       * gecmisle   -- T-28'den sonra
  4. Ikisi de GECMISI BILEN dogrulayiciya sorulur -- gercegi o soyler.

⚠ GECMIS BURADA PLANDIR, PDKS DEGIL
  Gercek PDKS'te kayitlarin yalniz %18'i dolu (P-1) ve plandan sapma var.
  Bu arac mekanigi olcer: motor gecmisi okuyor mu, sinirda dogru mu
  davraniyor. Gercekci gecmis (sahte PDKS) ikinci asamadir.

KOSTURMA (uzun: uc cozum, ~10 dk)
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py iki-hafta-olc.py
  py iki-hafta-olc.py --uc-hafta     (bes cozum, ~20 dk)
  py iki-hafta-olc.py --uc-hafta --yalniz-gecmisle
                                     (gecmissiz kosular atlanir; hafta 3
                                      cozumsuz kalirsa aday kurallar tek tek
                                      kaldirilarak sebep aranir)

UCUNCU HAFTA (30 Eylul aksami)
  Ardisik hafta sonu limiti (azami 2) iki onceki hafta sonunu ister; iki
  haftalik olcumde hafta -2 BILINMIYOR ve kural K-42 geregi atlaniyor.
  `--uc-hafta` ucuncu haftayi iki haftalik gecmisle cozer
  (`gecmis_bilinen_gunler` = -14..-1), iki kural da tam veriyle calisir.
"""

import collections
import copy
import importlib.util
import io
import json
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "uret", os.path.join(BURASI, "uret_veri_seti.py"))
U = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(U)

AYAR = {"azami_saniye": 240, "durgunluk_saniye": 25}
SINIR_KURALLARI = ("VARDIYA_ARASI_DINLENME", "CAKISMA_YOK", "HAFTA_TATILI",
                   "ARDISIK_CALISMA_GUNU", "ARDISIK_GECE_LIMIT",
                   # 30 Eylul aksami -- hafta olcekli iki kural
                   "GECE_POSTASI_DEVRI", "ARDISIK_HAFTA_SONU_LIMIT")


def gecmis_ekle(g, *planlar):
    """Onceki haftalarin atamalarini bu haftanin gecmisi yapar. g YERINDE
    degisir. `planlar` kronolojik: SONUNCUSU gecen hafta (gun - 7), ondan
    oncekisi gun - 14 ... Gecmis TAM kabul edilir (plan bilindigi icin).

    Gece isareti sablondan tasinir -- plan bunu biliyor. PDKS bilmeyecek;
    o zaman saatten tahmin edilir (K-40, T-69).
    """
    sablon = {t["id"]: t for t in g["vardiya_sablonlari"]}
    kisi = collections.defaultdict(list)
    for geri, atamalar in enumerate(reversed(planlar), start=1):
        for a in atamalar:
            k = {"gun": a["gun"] - 7 * geri, "bas": a["bas"], "bit": a["bit"]}
            t = sablon.get(a.get("sablon")) or {}
            if "gece_vardiyasi" in t:
                k["gece"] = bool(t["gece_vardiyasi"])
            kisi[a["calisan"]].append(k)
    for c in g["calisanlar"]:
        c["gecmis_vardiyalar"] = kisi.get(c["id"], [])
        c["gecmis_bilinen_gunler"] = list(range(-7 * len(planlar), 0))
    return g


def gecmissiz(g):
    g = copy.deepcopy(g)
    for c in g["calisanlar"]:
        c.pop("gecmis_vardiyalar", None)
        c.pop("gecmis_bilinen_gunler", None)
    return g


def sinir_ihlalleri(g_gercek, atamalar):
    r = degerlendir(g_gercek, atamalar)
    say = collections.Counter(i["kural"] for i in r["ihlaller"]
                              if i["kural"] in SINIR_KURALLARI)
    sert = sum(1 for i in r["ihlaller"] if i.get("agirlik") == "SERT")
    return say, sert, r


def main():
    t0 = time.time()
    g1 = U.sahne_uret(0.1, 0.95)
    c1 = coz(g1, AYAR)
    print("HAFTA 1: %s · %d atama · %.0f sn"
          % (c1["durum"], len(c1.get("atamalar") or []), time.time() - t0))
    if c1["durum"] != "cozuldu":
        sys.exit("hafta 1 cozulemedi")

    pazar_gecesi = sum(1 for a in c1["atamalar"]
                       if a["gun"] == 6 and a["bit"] > 24)
    print("  pazar gecesi pazartesiye tasan vardiya: %d" % pazar_gecesi)

    # GECE_POSTASI_DEVRI icin: ekip basina gece calisabilen kac kisi var,
    # hafta 1'de kaci GECE HAFTASI yasadi (K-45: calisma saatlerinin
    # yarisindan cogu gece postasinda). Hafta 2'de gece haftasini yalniz
    # kalanlar yasayabilir.
    # ⚠ GECE = YONETMELIGIN TANIMI (md. 7/2: suresinin yarisindan cogu
    #   20:00-06:00'da), firma isareti DEGIL -- B-AKSAM isaretli ama sayilmaz.
    def _yasal_gece(t):
        bas, bit = float(t["bas"]), float(t["bit"])
        gece = sum(max(0.0, min(bit, w + 10) - max(bas, w))
                   for w in (-4.0, 20.0, 44.0))
        return 2 * gece > bit - bas

    gece_sablon = {t["id"] for t in g1["vardiya_sablonlari"]
                   if _yasal_gece(t)}
    saat = collections.defaultdict(lambda: [0.0, 0.0])      # kisi -> [gece, toplam]
    ekibi = {}
    for a in c1["atamalar"]:
        sure = a["bit"] - a["bas"]
        saat[a["calisan"]][1] += sure
        if a["sablon"] in gece_sablon:
            saat[a["calisan"]][0] += sure
        ekibi[a["calisan"]] = a["ekip"]
    gececi = collections.defaultdict(set)
    for kisi, (gece, toplam) in saat.items():
        if 2 * gece > toplam:
            gececi[ekibi[kisi]].add(kisi)
    for ekip in sorted({t["ekip"] for t in g1["vardiya_sablonlari"]
                        if t["id"] in gece_sablon}):
        uygun = [c for c in g1["calisanlar"]
                 if ekip in (c.get("ekipler") or [])
                 and not c.get("gece_calisamaz")
                 and c.get("durum", "aktif") == "aktif"]
        print("  %-10s gece calisabilen %2d kisi · hafta 1'de gece haftasi yasayan %2d"
              % (ekip, len(uygun), len(gececi[ekip])))

    g2 = gecmis_ekle(U.sahne_uret(0.1, 0.95), c1["atamalar"])
    sonuc = {}
    planlar = _hafta_kostur("HAFTA 2", g2, sonuc,
                            atla_gecmissiz="--yalniz-gecmisle" in sys.argv)

    if "--uc-hafta" in sys.argv:
        if sonuc["gecmisle"]["durum"] != "cozuldu":
            sys.exit("hafta 2 gecmisle cozulemedi -- ucuncu hafta kurulamaz")
        g3 = gecmis_ekle(U.sahne_uret(0.1, 0.95), c1["atamalar"],
                         planlar["gecmisle"])
        sonuc3 = {}
        planlar3 = _hafta_kostur("HAFTA 3", g3, sonuc3,
                                 atla_gecmissiz="--yalniz-gecmisle" in sys.argv)
        sonuc = {"hafta_2": sonuc, "hafta_3": sonuc3}
        # Planlar saklanir: hafta 3 cozumsuz cikarsa sebep, hafta 1-2'yi
        # yeniden cozmeden aranabilsin (CP-SAT her kosuda baska plan uretir).
        with io.open(os.path.join(BURASI, "uc-hafta-planlar.json"), "w",
                     encoding="utf-8") as f:
            json.dump({"hafta_1": c1["atamalar"],
                       "hafta_2": planlar["gecmisle"],
                       "hafta_3": planlar3.get("gecmisle")}, f)
        if sonuc3["gecmisle"]["durum"] != "cozuldu":
            sonuc["hafta_3_neden"] = _neden_cozumsuz(g3)

    ad = "uc-hafta-sonucu.json" if "--uc-hafta" in sys.argv \
        else "iki-hafta-sonucu.json"
    with io.open(os.path.join(BURASI, ad), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("\nToplam %.0f sn" % (time.time() - t0))


def _neden_cozumsuz(g):
    """Gecmisle cozumsuz kalan haftada HANGI kural kilitliyor -- deneyle.

    Cozucunun kendi teshisi her sert kurali 10 saniyelik butceyle dener;
    bu olcekte 10 saniye bir plan bulmaya yetmeyebilir ve "engellemiyor"
    sonucu yanlis olabilir. Burada ADAY kurallar TAM butceyle, tek tek ve
    birlikte kaldirilir.
    """
    adaylar = ("ARDISIK_HAFTA_SONU_LIMIT", "GECE_POSTASI_DEVRI")
    cikan = {}
    for kaldir in ((adaylar[0],), (adaylar[1],), adaylar):
        deneme = copy.deepcopy(g)
        deneme["kurallar"] = [k for k in deneme["kurallar"]
                              if k["kod"] not in kaldir]
        t = time.time()
        c = coz(deneme, AYAR)
        ad = " + ".join(kaldir)
        cikan[ad] = {"durum": c["durum"], "sn": round(time.time() - t)}
        print("  deney -- kaldirilan: %-45s -> %s (%.0f sn)"
              % (ad, c["durum"], time.time() - t))
    return cikan


def _hafta_kostur(baslik, g, sonuc, atla_gecmissiz=False):
    """Ayni haftayi gecmissiz ve gecmisle cozer; ikisini de GECMISI BILEN
    denetciye sorar. Donen: {ad: atamalar}."""
    planlar = {}
    kosular = (("gecmissiz", gecmissiz(g)), ("gecmisle", g))
    if atla_gecmissiz:
        kosular = kosular[1:]
    for ad, girdi in kosular:
        t = time.time()
        c = coz(girdi, AYAR)
        say, sert, r = sinir_ihlalleri(g, c.get("atamalar") or [])
        eksik = collections.Counter(x["kural"]
                                    for x in r.get("gecmis_eksik") or [])
        sonuc[ad] = {"durum": c["durum"], "atama": len(c.get("atamalar") or []),
                     "sinir": dict(say), "sert": sert,
                     "gecmis_eksik": sum(eksik.values()),
                     "gecmis_eksik_kural": dict(eksik),
                     "sn": round(time.time() - t)}
        planlar[ad] = c.get("atamalar") or []
        print("\n%s %-10s %s · %d atama · %.0f sn"
              % (baslik, ad, c["durum"], sonuc[ad]["atama"], time.time() - t))
        print("  gecmisi bilen denetciye gore sinir ihlali: %s"
              % (dict(say) or "YOK"))
        print("  toplam sert ihlal: %d · gecmis_eksik: %d %s"
              % (sert, sonuc[ad]["gecmis_eksik"], dict(eksik) or ""))
        if c["durum"] != "cozuldu":
            t_ = c.get("teshis") or {}
            sonuc[ad]["teshis"] = {
                "kapsam": t_.get("kapsam"), "hucre": t_.get("hucre"),
                "engelleyen": [k.get("kod") for k in
                               t_.get("engelleyen_kurallar") or []]}
            print("  ⚠ cozucunun teshisi: kapsam %s · hucre %s · engelleyen %s"
                  % (t_.get("kapsam"), t_.get("hucre"),
                     sonuc[ad]["teshis"]["engelleyen"] or "BOS"))
    return planlar


if __name__ == "__main__":
    main()
