# -*- coding: utf-8 -*-
"""
FIKSTUR DENETLEYICI (v5)

NE YAPAR
  Altin senaryo fiksturlerini ACAR ve KENDI ICINDE tutarli mi diye bakar:

    1. Yapi        Zorunlu alanlar var mi, tip taninan bir tip mi
    2. Sahne       _sahne-S10.json cozuluyor mu, fark uygulanabiliyor mu
    3. Referans    Atamalardaki calisan/sablon kimlikleri sahnede var mi
    4. Capa        kabul_olcutu, KABUL-OLCUTLERI.md'de gercekten bir basliga
                   isaret ediyor mu
    5. Turetilmis  "turetilmis_degerler" bloguna yazilan sayilar girdiden
                   gercekten cikiyor mu
    6. Beklenen    'evaluate' tipi fiksturlerde yazili ihlal listesi girdiden
                   turetilebiliyor mu, sayisi tutuyor mu

  Amac: fiksturun BEKLENEN blogu ile GIRDI blogu zamanla birbirinden kaymasin.
  Elle yazilan bir beklenen liste, girdi degistiginde sessizce yanlis kalir.

NEYI DENETLEYEMEZ -- durustluk notu
  'solve' ve 'backend' tipi fiksturlerde beklenen sonuc bir OZELLIKTIR
  ("cozuldu", "hedef kapsama >= %95", "bildirim gider"), girdiden turetilemez.
  Onlarda yalniz yapi, referans ve capa kontrol edilir. Asil dogrulama motor
  ve backend yazildiginda testlerin kendisiyle olur.

BU NE DEGILDIR  <-- ONEMLI, IKI KEZ YANLIS ISIMLENDIRME YASANDI
  * Urunun dogrulayicisi DEGILDIR. (Master Spec #16.1, 03-MIMARI-KARARLAR M-09.)
  * Motor DEGILDIR. Plan uretmez.
  * Bu dosyanin mantigi urun dogrulayicisina KOPYALANMAZ. Kopyalanirsa
    "uygulama ile dogrulayici ayni varsayimdan beslenmez" ilkesi bozulur ve
    testler yanlis sebeple yesil yanar.

KURAL YORUMLARI -- onaylanmis kararlara gore
  K-11  "Asgari 11 saat" 11'i KAPSAR. Tam sinir ihlal DEGIL.
        Ayni sekilde "azami 9 saat" 9'u kapsar.
  K-14  MOLA_KAPSAMASI YUMUSAK. MOLA_HAKKI SERT kalir.
  K-4   MOLA_HAKKI esigi BRUT vardiya suresine uygulanir.
  V-1   Ortusen iki vardiyada YALNIZ cakisma yazilir, ayrica dinlenme ihlali
        yazilmaz.

CALISTIRMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\v5
  py fikstur-denetleyici.py                 (fikstur/ altindaki hepsi)
  py fikstur-denetleyici.py fikstur/A04.json

CIKIS KODU
  0 = hepsi tutarli  |  1 = en az bir fikstur tutarsiz
"""

import os
import re
import sys
import json
import glob
import copy
import math
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.abspath(__file__))
FIKSTUR = os.path.join(KOK, "fikstur")
OLCUT = os.path.join(KOK, "KABUL-OLCUTLERI.md")

TIPLER = ("solve", "evaluate", "backend")
ZORUNLU = ("senaryo", "ad", "tip", "sahne", "kabul_olcutu")


# ----------------------------------------------------------------------
# Yardimcilar
# ----------------------------------------------------------------------

def oku(yol):
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def temiz(d):
    """_ ile baslayan anahtarlari (yorumlari) atar."""
    if isinstance(d, dict):
        return {k: temiz(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, list):
        return [temiz(x) for x in d]
    return d


def mola_gerekli_dk(brut_saat):
    """Master Spec #6.2 MOLA_HAKKI tablosu. Esik BRUT sureye uygulanir (K-4)."""
    if brut_saat <= 4:
        return 15
    if brut_saat <= 7.5:
        return 30
    return 60


def mutlak(gun, saat):
    """Genisletilmis saat -> mutlak saat. gun 1, bit 25 = Carsamba 01:00."""
    return gun * 24 + saat


def capa_uret(baslik):
    """Markdown basligindan GitHub tarzi capa uretir."""
    s = baslik.strip().lower()
    s = s.replace("\u00b7", "").replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
    s = s.strip().replace(" ", "-")
    return s


# ----------------------------------------------------------------------
# Sahne cozumu
# ----------------------------------------------------------------------

def sahne_uygula(sahne, fark):
    """Sahneye farki uygular, birlesmis girdiyi dondurur."""
    g = copy.deepcopy(sahne)
    fark = fark or {}

    # calisanlar: kimlige gore birlestirme
    if "calisanlar" in fark:
        indeks = {c["id"]: c for c in g["calisanlar"]}
        for cid, degisiklik in fark["calisanlar"].items():
            if cid not in indeks:
                raise KeyError("fark bilinmeyen calisani degistiriyor: %s" % cid)
            indeks[cid].update(copy.deepcopy(degisiklik))

    # tamamen degistirilenler
    for alan in ("talep", "sabit_atamalar", "kilitler", "profil",
                 "donmus_gunler", "kiraci_saat_dilimi", "hafta_baslangic"):
        if alan in fark:
            g[alan] = copy.deepcopy(fark[alan])

    # eklenenler
    if "vardiya_sablonlari_ekle" in fark:
        g["vardiya_sablonlari"] += copy.deepcopy(fark["vardiya_sablonlari_ekle"])
    if "kurallar_ekle" in fark:
        g["kurallar"] += copy.deepcopy(fark["kurallar_ekle"])

    # cikarilanlar
    if "kurallar_cikar" in fark:
        cikar = set(fark["kurallar_cikar"])
        g["kurallar"] = [k for k in g["kurallar"] if k["kod"] not in cikar]

    return g


# ----------------------------------------------------------------------
# Bagimsiz turetme -- yalniz 'evaluate' icin
# ----------------------------------------------------------------------

def turet(girdi, atamalar):
    """Girdi + atamalardan ihlal listesi turetir.

    Doner: (sert, yumusak) -- ikisi de sirali liste.
    Bkz. dosya basindaki 'BU NE DEGILDIR' ve 'KURAL YORUMLARI'.
    """
    kural = {k["kod"]: k for k in girdi["kurallar"]}
    par = lambda kod, ad, vars_=None: kural.get(kod, {}).get("parametreler", {}).get(ad, vars_)
    sert, yumusak = [], []

    kisi_vardiya = defaultdict(list)
    gunluk_net = defaultdict(float)
    haftalik_net = defaultdict(float)

    for a in atamalar:
        brut = a["bit"] - a["bas"]
        mola_saat = sum(m["bit"] - m["bas"] for m in a.get("molalar", []))
        net = brut - mola_saat
        if "MOLA_HAKKI" in kural and mola_saat * 60 < mola_gerekli_dk(brut):
            sert.append(("MOLA_HAKKI", a["calisan"], a["gun"], None))
        gunluk_net[(a["calisan"], a["gun"])] += net
        haftalik_net[a["calisan"]] += net
        kisi_vardiya[a["calisan"]].append(
            (mutlak(a["gun"], a["bas"]), mutlak(a["gun"], a["bit"]), a["gun"]))

    # K-11: sinir DAHILDIR -> yalniz kesin asma ihlal
    if "GUNLUK_AZAMI" in kural:
        s = par("GUNLUK_AZAMI", "azami_saat")
        for (c, g), v in gunluk_net.items():
            if s is not None and v > s:
                sert.append(("GUNLUK_AZAMI", c, g, v))
    if "HAFTALIK_AZAMI" in kural:
        s = par("HAFTALIK_AZAMI", "azami_saat")
        for c, v in haftalik_net.items():
            if s is not None and v > s:
                sert.append(("HAFTALIK_AZAMI", c, None, v))

    dinlenme_sinir = par("VARDIYA_ARASI_DINLENME", "asgari_saat")
    for c in kisi_vardiya:
        v = sorted(kisi_vardiya[c])
        for i in range(len(v) - 1):
            bitis, sonraki_bas, sonraki_gun = v[i][1], v[i + 1][0], v[i + 1][2]
            if sonraki_bas < bitis:
                # V-1: ortusmede YALNIZ cakisma
                sert.append(("CAKISMA_YOK", c, sonraki_gun, None))
            elif dinlenme_sinir is not None:
                d = sonraki_bas - bitis
                if d < dinlenme_sinir:          # K-11: tam sinir ihlal degil
                    sert.append(("VARDIYA_ARASI_DINLENME", c, sonraki_gun, d))

    # MOLA_KAPSAMASI -- K-14 geregi YUMUSAK
    if "MOLA_KAPSAMASI" in kural:
        for t in girdi.get("talep", []):
            for gun in t.get("gunler", []):
                for saat in t.get("saatler", []):
                    sahada = 0
                    for a in atamalar:
                        if a["gun"] != gun:
                            continue
                        if not (a["bas"] <= saat < a["bit"]):
                            continue
                        molada = any(m["bas"] <= saat < m["bit"]
                                     for m in a.get("molalar", []))
                        if not molada:
                            sahada += 1
                    if sahada < t["asgari"]:
                        yumusak.append(("MOLA_KAPSAMASI", gun, saat,
                                        sahada, t["asgari"]))

    return sorted(sert), sorted(yumusak)


# ----------------------------------------------------------------------
# Kontroller
# ----------------------------------------------------------------------

def capalar():
    """KABUL-OLCUTLERI.md icindeki basliklardan uretilen capa kumesi."""
    if not os.path.exists(OLCUT):
        return None
    k = set()
    with open(OLCUT, "r", encoding="utf-8") as f:
        for satir in f:
            m = re.match(r"^#{1,6}\s+(.*)$", satir)
            if m:
                k.add(capa_uret(m.group(1)))
    return k


def denetle(yol, sahne, capa_kumesi):
    ad = os.path.basename(yol)
    sorunlar = []
    fik = oku(yol)

    # 1) yapi
    for alan in ZORUNLU:
        if alan not in fik:
            sorunlar.append("zorunlu alan eksik: %s" % alan)
    if fik.get("tip") not in TIPLER:
        sorunlar.append("bilinmeyen tip: %r (taninan: %s)"
                        % (fik.get("tip"), ", ".join(TIPLER)))
    if sorunlar:
        return bitir(ad, sorunlar, fik)

    # 2) sahne + fark
    try:
        girdi = sahne_uygula(sahne, fik.get("fark"))
    except Exception as e:
        return bitir(ad, ["sahne/fark uygulanamadi: %s" % e], fik)

    calisanlar = {c["id"] for c in girdi["calisanlar"]}
    sablonlar = {s["id"] for s in girdi["vardiya_sablonlari"]}

    # 4) capa
    if capa_kumesi is not None:
        capa = fik["kabul_olcutu"].split("#", 1)[-1]
        if capa not in capa_kumesi:
            sorunlar.append("kabul_olcutu capasi KABUL-OLCUTLERI.md'de yok: #%s" % capa)

    # atamalari topla: dogrudan ya da alt_durumlar icinde
    atama_kumeleri = []
    if "atamalar" in fik:
        atama_kumeleri.append(("-", fik["atamalar"], fik.get("beklenen", {}), girdi))
    for ad_ in fik.get("alt_durumlar", []):
        if "atamalar" in ad_:
            alt_girdi = sahne_uygula(girdi, ad_.get("fark"))
            atama_kumeleri.append((ad_.get("ad", "?"), ad_["atamalar"],
                                   ad_.get("beklenen", {}), alt_girdi))

    # 3) referans butunlugu
    for etiket, atamalar, _, _ in atama_kumeleri:
        for a in atamalar:
            if a["calisan"] not in calisanlar:
                sorunlar.append("%s: bilinmeyen calisan %s" % (etiket, a["calisan"]))
            if a.get("sablon") is not None and a["sablon"] not in sablonlar:
                sorunlar.append("%s: bilinmeyen sablon %s" % (etiket, a["sablon"]))

    # 5) turetilmis_degerler
    td = temiz(fik.get("turetilmis_degerler", {}))
    if td and atama_kumeleri:
        hesap = {}
        for _, atamalar, _, _ in atama_kumeleri:
            kisi = defaultdict(list)
            for a in atamalar:
                kisi[a["calisan"]].append(a)
            for c, lst in kisi.items():
                lst = sorted(lst, key=lambda x: mutlak(x["gun"], x["bas"]))
                for i in range(len(lst) - 1):
                    bitis = mutlak(lst[i]["gun"], lst[i]["bit"])
                    bas = mutlak(lst[i + 1]["gun"], lst[i + 1]["bas"])
                    if bas < bitis:
                        hesap["%s_ortusme_saat" % c] = bitis - bas
                    else:
                        hesap["%s_dinlenme_saat" % c] = bas - bitis
                for a in lst:
                    brut = a["bit"] - a["bas"]
                    mola = sum(m["bit"] - m["bas"] for m in a.get("molalar", []))
                    hesap["%s_gun%d_brut_saat" % (c, a["gun"])] = brut
                    hesap["%s_gun%d_net_saat" % (c, a["gun"])] = brut - mola
                    hesap["%s_tasma_gunu_yazilan_gun" % c] = a["gun"]
        for anahtar, beklenen in td.items():
            if anahtar in hesap and hesap[anahtar] != beklenen:
                sorunlar.append("turetilmis_degerler.%s = %s, hesaplanan %s"
                                % (anahtar, beklenen, hesap[anahtar]))

    # 6) beklenen ihlal listesi (yalniz evaluate)
    if fik["tip"] == "evaluate":
        for etiket, atamalar, bek, alt_girdi in atama_kumeleri:
            bek = temiz(bek)
            if not bek:
                continue
            sert, yumusak = turet(alt_girdi, atamalar)
            if "sert_ihlal_sayisi" in bek and len(sert) != bek["sert_ihlal_sayisi"]:
                sorunlar.append("%s: sert_ihlal_sayisi %s yazili, turetilen %d"
                                % (etiket, bek["sert_ihlal_sayisi"], len(sert)))
            if "ihlaller" in bek:
                yazili = sorted((i["kural"], i["calisan"], i["gun"], i.get("olculen"))
                                for i in bek["ihlaller"])
                if yazili != sert:
                    sorunlar.append("%s: sert ihlal listesi tutmuyor"
                                    "\n        yazili   : %s"
                                    "\n        turetilen: %s" % (etiket, yazili, sert))
            if "yumusak_ihlaller" in bek:
                yazili_y = sorted((i["kural"], i["gun"], i["saat"],
                                   i.get("sahada"), i.get("asgari"))
                                  for i in bek["yumusak_ihlaller"])
                if yazili_y != yumusak:
                    sorunlar.append("%s: yumusak ihlal listesi tutmuyor"
                                    "\n        yazili   : %s"
                                    "\n        turetilen: %s" % (etiket, yazili_y, yumusak))

    return bitir(ad, sorunlar, fik, atama_kumeleri)


def bitir(ad, sorunlar, fik, atama_kumeleri=None):
    if sorunlar:
        print("[TUTARSIZ] %s" % ad)
        for s in sorunlar:
            print("    - %s" % s)
        return False
    atama_sayisi = sum(len(a) for _, a, _, _ in (atama_kumeleri or []))
    ek = ""
    if atama_sayisi:
        ek = ", %d atama" % atama_sayisi
    if fik.get("alt_durumlar"):
        ek += ", %d alt durum" % len(fik["alt_durumlar"])
    if fik.get("adimlar"):
        ek += ", %d adim" % len(fik["adimlar"])
    print("[TAMAM]    %-10s %-9s (%s%s)" % (ad, fik.get("tip", "?"),
                                            fik.get("senaryo", "?"), ek))
    return True


def main():
    sahne_yolu = os.path.join(FIKSTUR, "_sahne-S10.json")
    if not os.path.exists(sahne_yolu):
        print("Ortak sahne bulunamadi: %s" % sahne_yolu)
        return 1
    sahne = oku(sahne_yolu)
    capa_kumesi = capalar()
    if capa_kumesi is None:
        print("UYARI: KABUL-OLCUTLERI.md bulunamadi, capa kontrolu atlandi.\n")

    if len(sys.argv) > 1:
        dosyalar = sys.argv[1:]
    else:
        dosyalar = sorted(y for y in glob.glob(os.path.join(FIKSTUR, "*.json"))
                          if not os.path.basename(y).startswith("_"))
    if not dosyalar:
        print("Fikstur bulunamadi.")
        return 1

    sonuc = [denetle(y, sahne, capa_kumesi) for y in dosyalar]
    print("\n%d/%d fikstur tutarli." % (sum(sonuc), len(sonuc)))
    if all(sonuc):
        print("NOT: 'solve' ve 'backend' tipinde beklenen sonuc bir OZELLIKTIR,")
        print("     girdiden turetilemez. Onlarda yalniz yapi/referans/capa bakildi.")
    return 0 if all(sonuc) else 1


if __name__ == "__main__":
    sys.exit(main())
