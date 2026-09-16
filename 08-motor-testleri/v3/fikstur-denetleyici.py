# -*- coding: utf-8 -*-
"""
FIKSTUR DENETLEYICI

NE YAPAR
  Bir altin senaryo fiksturunu ACAR ve KENDI ICINDE tutarli mi diye bakar:
    1. JSON gecerli mi, calisan/sablon referanslari tutuyor mu
    2. "turetilmis_degerler" bloguna yazilan sayilar girdiden gercekten cikiyor mu
    3. "beklenen.ihlaller" listesi girdiden turetilebiliyor mu, sayisi tutuyor mu

  Amac: fiksturun BEKLENEN blogu ile GIRDI blogu zamanla birbirinden
  kaymasin. Elle yazilan bir beklenen liste, girdi degistiginde sessizce
  yanlis kalir.

BU NE DEGILDIR  <-- ONEMLI, IKI KEZ YANLIS ISIMLENDIRME YASANDI
  * Urunun dogrulayicisi DEGILDIR. (Bkz. Master Spec #16.1 ve
    00-DEVIR/03-MIMARI-KARARLAR.md M-09.)
  * Motor DEGILDIR. Plan uretmez.
  * Bu dosyanin mantigi urun dogrulayicisina KOPYALANMAZ. Kopyalanirsa
    sartnamenin "uygulama ile dogrulayici ayni varsayimdan beslenmez"
    ilkesi bozulur ve testler yanlis sebeple yesil yanar.

  Urun dogrulayicisi yazildiginda bu dosya yerinde kalir ve YALNIZ
  fikstur tutarliligini kontrol etmeye devam eder.

CALISTIRMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\v2
  py fikstur-denetleyici.py                (fikstur/ altindaki hepsi)
  py fikstur-denetleyici.py fikstur/A04.json

CIKIS KODU
  0 = hepsi tutarli | 1 = en az bir fikstur tutarsiz
"""

import os
import sys
import json
import glob
from collections import defaultdict

KOK = os.path.dirname(os.path.abspath(__file__))


def mola_gerekli_dk(brut_saat):
    """Master Spec #6.2 MOLA_HAKKI tablosu. Esik BRUT sureye uygulanir (karar K-4)."""
    if brut_saat <= 4:
        return 15
    if brut_saat <= 7.5:
        return 30
    return 60


def mutlak(gun, saat):
    """Genisletilmis saat -> mutlak saat. gun 1 bit 25 = Carsamba 01:00."""
    return gun * 24 + saat


def turet(girdi, sinir_dahil):
    """Girdiden ihlal listesi turetir. Bkz. dosya basindaki 'BU NE DEGILDIR'."""
    kural = {k["kod"]: k.get("parametreler", {}) for k in girdi["kurallar"]}
    ihlal = []

    def alt_sinir_asildi(olculen, gereken):
        # dinlenme gibi ALT sinirlar
        return olculen < gereken if sinir_dahil else olculen <= gereken

    def ust_sinir_asildi(olculen, gereken):
        # gunluk/haftalik azami gibi UST sinirlar
        return olculen > gereken if sinir_dahil else olculen >= gereken

    kisi_vardiya = defaultdict(list)
    gunluk_net = defaultdict(float)
    haftalik_net = defaultdict(float)

    for a in girdi["atamalar"]:
        brut = a["bit"] - a["bas"]
        mola_saat = sum(m["bit"] - m["bas"] for m in a.get("molalar", []))
        net = brut - mola_saat
        if "MOLA_HAKKI" in kural and mola_saat * 60 < mola_gerekli_dk(brut):
            ihlal.append(("MOLA_HAKKI", a["calisan"], a["gun"], None))
        gunluk_net[(a["calisan"], a["gun"])] += net
        haftalik_net[a["calisan"]] += net
        kisi_vardiya[a["calisan"]].append(
            (mutlak(a["gun"], a["bas"]), mutlak(a["gun"], a["bit"]), a["gun"]))

    if "GUNLUK_AZAMI" in kural:
        sinir = kural["GUNLUK_AZAMI"]["azami_saat"]
        for (c, g), v in gunluk_net.items():
            if ust_sinir_asildi(v, sinir):
                ihlal.append(("GUNLUK_AZAMI", c, g, v))

    if "HAFTALIK_AZAMI" in kural:
        sinir = kural["HAFTALIK_AZAMI"]["azami_saat"]
        for c, v in haftalik_net.items():
            if ust_sinir_asildi(v, sinir):
                ihlal.append(("HAFTALIK_AZAMI", c, None, v))

    dinlenme_sinir = kural.get("VARDIYA_ARASI_DINLENME", {}).get("asgari_saat")
    for c in kisi_vardiya:
        vardiyalar = sorted(kisi_vardiya[c])
        for i in range(len(vardiyalar) - 1):
            bitis = vardiyalar[i][1]
            sonraki_bas = vardiyalar[i + 1][0]
            sonraki_gun = vardiyalar[i + 1][2]
            if sonraki_bas < bitis:
                # V-1: ortusmede YALNIZ cakisma yazilir, ayrica dinlenme ihlali yazilmaz
                ihlal.append(("CAKISMA_YOK", c, sonraki_gun, None))
            elif dinlenme_sinir is not None:
                dinlenme = sonraki_bas - bitis
                if alt_sinir_asildi(dinlenme, dinlenme_sinir):
                    ihlal.append(
                        ("VARDIYA_ARASI_DINLENME", c, sonraki_gun, dinlenme))

    return sorted(ihlal)


def denetle(yol):
    ad = os.path.basename(yol)
    sorunlar = []
    with open(yol, "r", encoding="utf-8") as f:
        fik = json.load(f)

    girdi = fik["girdi"]

    # 1) referans butunlugu
    calisanlar = {c["id"] for c in girdi["calisanlar"]}
    sablonlar = {s["id"] for s in girdi["vardiya_sablonlari"]}
    for a in girdi["atamalar"]:
        if a["calisan"] not in calisanlar:
            sorunlar.append("bilinmeyen calisan: %s" % a["calisan"])
        if a.get("sablon") is not None and a["sablon"] not in sablonlar:
            sorunlar.append("bilinmeyen sablon: %s" % a["sablon"])

    # 2) turetilmis_degerler
    td = {k: v for k, v in fik.get("turetilmis_degerler", {}).items()
          if not k.startswith("_")}
    hesap = {}
    kisi = defaultdict(list)
    for a in girdi["atamalar"]:
        kisi[a["calisan"]].append(a)
    for c, atamalar in kisi.items():
        atamalar = sorted(atamalar, key=lambda x: mutlak(x["gun"], x["bas"]))
        for i in range(len(atamalar) - 1):
            bitis = mutlak(atamalar[i]["gun"], atamalar[i]["bit"])
            bas = mutlak(atamalar[i + 1]["gun"], atamalar[i + 1]["bas"])
            if bas < bitis:
                hesap["%s_ortusme_saat" % c] = bitis - bas
            else:
                hesap["%s_dinlenme_saat" % c] = bas - bitis
        for a in atamalar:
            brut = a["bit"] - a["bas"]
            mola = sum(m["bit"] - m["bas"] for m in a.get("molalar", []))
            hesap["%s_gun%d_brut_saat" % (c, a["gun"])] = brut
            hesap["%s_gun%d_net_saat" % (c, a["gun"])] = brut - mola
    for anahtar, beklenen in td.items():
        if anahtar in hesap and hesap[anahtar] != beklenen:
            sorunlar.append("turetilmis_degerler.%s = %s, hesaplanan %s"
                            % (anahtar, beklenen, hesap[anahtar]))

    # 3) varyantlarin beklenen listesi
    for var in fik.get("varyantlar", []):
        sinir_dahil = var["kural_ayari"]["sinir_dahil"]
        bulunan = turet(girdi, sinir_dahil)
        bek = sorted((i["kural"], i["calisan"], i["gun"], i.get("olculen"))
                     for i in var["beklenen"]["ihlaller"])
        if len(bulunan) != var["beklenen"]["sert_ihlal_sayisi"]:
            sorunlar.append("%s: sert_ihlal_sayisi %s yazili, turetilen %d"
                            % (var["ad"], var["beklenen"]["sert_ihlal_sayisi"],
                               len(bulunan)))
        if bek != bulunan:
            sorunlar.append("%s: ihlal listesi tutmuyor\n      yazili : %s\n      turetilen: %s"
                            % (var["ad"], bek, bulunan))

    if sorunlar:
        print("[TUTARSIZ] %s" % ad)
        for s in sorunlar:
            print("    - %s" % s)
        return False
    varyant_sayisi = len(fik.get("varyantlar", []))
    print("[TAMAM]    %s  (%d atama, %d varyant)"
          % (ad, len(girdi["atamalar"]), varyant_sayisi))
    return True


def main():
    if len(sys.argv) > 1:
        dosyalar = sys.argv[1:]
    else:
        dosyalar = sorted(glob.glob(os.path.join(KOK, "fikstur", "*.json")))
    if not dosyalar:
        print("Fikstur bulunamadi.")
        return 1
    sonuc = [denetle(y) for y in dosyalar]
    print("\n%d/%d fikstur tutarli." % (sum(sonuc), len(sonuc)))
    return 0 if all(sonuc) else 1


if __name__ == "__main__":
    sys.exit(main())
