# -*- coding: utf-8 -*-
"""
FAZLA MESAI YOLU ACIK OLMALI -- K-38

⚠ NEDEN (Mustafa, 29 Eylul)
    > "Bir calisan gunluk 11 saatten fazla calistirilamaz. Amacimiz hic
    >  fazla mesai yaptirmamak. Tabii ki cozumsuz ise buna basvuracak ama
    >  en son care."

  Bu kacis yolu KAPALIYDI. `_sure_sinirlari()` iki kisit koyuyordu:

      dakika <= HAFTALIK_AZAMI              -> 45 saat
      dakika <= sozlesme + fazla mesai tavani -> 45 + 10 = 55 saat

  Baglayici olan BIRINCISIYDI. 45 saat sozlesmeli bir calisan zaten 45'te
  duruyordu -- yani fazla mesai matematiksel olarak IMKANSIZDI. K-30'un
  "asgari zorlarsa minimum fazla mesai" dali, ceza degiskeni ve profile
  bagli tavan, bu calisanlar icin OLU KODDU.

  Olculdu (29 Eylul) -- tek degisken izole edilerek, ayni sahne:
      HAFTALIK_AZAMI 45 -> cozumsuz
      HAFTALIK_AZAMI 55 -> cozuldu, 48 saat, fazla mesai bildirildi

KARAR (Mustafa, 29 Eylul)
  "HAFTALIK_AZAMI NORMAL CALISMA SINIRIDIR. Toplam tavan degildir."

  Yani toplam saat 45'i asabilir; asan kisim FAZLA MESAIDIR ve kendi
  tavanina tabidir (profile bagli: CALISAN 0 - DENGELI 10 - KAPSAMA 15),
  ustune gunluk 11 saat siniri ayrica gecerlidir.

⚠ BU TESTLER "FAZLA MESAI IYIDIR" DEMIYOR
  K-30 duruyor: hedef hic yapmamak. Buradaki sinav, ZORUNLU oldugunda
  yolun ACIK olmasi. Kapali bir kacis yolu, plani "cozumsuz" gosterir --
  yoneticiye yanlis bir cumle kurdurur.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_fazla_mesai_yolu.py -v
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import _net_saat                            # noqa: E402


def _sahne(haftalik_saat=45, gun=6, profil="DENGELI", gunluk_azami=11):
    """Herkesin `gun` gun x 8 net saat calismasi ZORUNLU olan sahne.

    6 gun -> 48 net saat. 45 saat sozlesmeli biri icin bu 3 saat fazla
    mesai demektir; tavan 10 oldugu icin izinli OLMALIDIR.
    """
    return {
        "profil": profil,
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": haftalik_saat},
             "izinler": [], "uygunluk": []} for i in range(1, 7)],
        "vardiya_sablonlari": [
            {"id": "V1", "ekip": "E", "bas": 8, "bit": 17, "mola_dk": 60,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                                  "ucretli": False}]}],      # 9 brut / 8 net
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 6, "hedef": 6}
                  for d in range(gun) for s in range(9, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": gunluk_azami}},
            {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 45}},
            {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True,
             "parametreler": {"azami_saat_hafta": 10}},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def _saatler(g, c):
    sab = {t["id"]: t for t in g["vardiya_sablonlari"]}
    net = collections.Counter()
    for a in c.get("atamalar") or []:
        net[a["calisan"]] += _net_saat(sab[a["sablon"]])
    return net


def test_ZORUNLU_fazla_mesai_YAPILABILIR():
    """Asil sinav: 45 saat sozlesmeli biri 48 saat calisabilmeli.

    Bu test kirmiziyken motor "cozumsuz" diyordu -- yoneticiye
    "bu talebi bu kadroyla karsilayamazsiniz" dedirtiyordu, oysa
    3 saatlik fazla mesai kanunen de sozlesmece de mumkundu.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", (
        "zorunlu fazla mesai hala imkansiz: %s" % c["durum"])
    net = _saatler(g, c)
    assert max(net.values()) > 45, (
        "kimse 45 saati asmamis: %r" % dict(net))


def test_fazla_mesai_CIKTIDA_bildirilir():
    """Yonetici kac saat fazla mesai yazildigini gormeli."""
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c["durum"]
    fm = (c.get("metrikler") or {}).get("fazla_mesai_saat")
    assert fm and fm > 0, "fazla mesai bildirilmedi: %r" % fm


def test_FAZLA_MESAI_TAVANI_hala_baglayici():
    """Yol acildi diye tavan kalkmis olmamali.

    ⚠ Bu testin gorevi, duzeltmenin FAZLA ileri gitmedigini kanitlamak.
      CALISAN profilinde tavan 0'dir; ayni sahne cozulememeli.
    """
    g = _sahne(profil="CALISAN")
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] != "cozuldu", (
        "CALISAN profilinde tavan 0 iken fazla mesaili plan uretildi")


def test_GUNLUK_11_SAAT_hala_baglayici():
    """Gunluk yasal sinir yerinde durmali -- yol acildi diye gevsememeli."""
    g = _sahne(gunluk_azami=7)      # 8 net saatlik vardiya artik yasak
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    if c["durum"] == "cozuldu":
        net = _saatler(g, c)
        assert not net, "gunluk sinirin ustundeki vardiya atanmis: %r" % dict(net)


def test_HAFTALIK_TAVAN_sozlesmesiz_calisanda_da_baglar():
    """Haftalik tavan gercekten duruyor mu -- MUTASYONLA yakalandi.

    ⚠ NEDEN BU TEST SONRADAN EKLENDI
      Duzeltme yazildiktan sonra mutasyon denendi: haftalik kisit TAMAMEN
      silindiginde butun testler YESIL kaldi. Yani "tavan kalkmadi, yeri
      degisti" cumlesini hicbir test kanitlamiyordu.

      Sebebi: sozlesmesi olan bir calisanda `sozlesme + tavan` kisiti zaten
      daha dar. Haftalik tavan ancak `haftalik_saat` verilmemis bir
      calisanda TEK sinir olarak kalir -- ve bu testin sinadigi yol odur.

    Sahne: 10 net saatlik vardiya x 6 gun = 60 saat. Tavan 45 + 10 = 55.
    """
    g = _sahne()
    for c in g["calisanlar"]:
        c["sozlesme"] = {"tip": "tam_zamanli"}        # haftalik_saat YOK
    g["vardiya_sablonlari"] = [
        {"id": "V1", "ekip": "E", "bas": 8, "bit": 19, "mola_dk": 60,
         "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                              "ucretli": False}]}]     # 11 brut / 10 net
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 6, "hedef": 6}
                  for d in range(6) for s in range(9, 19)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    if c["durum"] == "cozuldu":
        net = _saatler(g, c)
        assert max(net.values()) <= 55, (
            "haftalik tavan (45 normal + 10 fazla mesai) asilmis: %.0f saat"
            % max(net.values()))


def test_FAZLA_MESAI_GEREKMEYEN_planda_sifir_kalir():
    """K-30 duruyor: gerek yoksa fazla mesai yazilmaz.

    5 gunluk talep -> 40 net saat, 45 saatlik sozlesmenin altinda.
    """
    g = _sahne(gun=5)
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c["durum"]
    fm = (c.get("metrikler") or {}).get("fazla_mesai_saat")
    assert fm == 0.0, "gereksiz yere fazla mesai yazilmis: %r" % fm


# ----------------------------------------------------------------------
# Dogrulayici tarafi -- K-38 yalniz COZUCUYE uygulanmisti (29 Eylul)
# ----------------------------------------------------------------------

def test_DOGRULAYICI_da_45i_NORMAL_SINIR_sayar():
    """⚠ K-38 dogrulayiciya UYGULANMAMISTI -- zor veri seti yakaladi.

    Cozucu 45'i normal calisma siniri sayip toplami 55'e kadar acti;
    dogrulayicinin `HAFTALIK_AZAMI` kurali ise toplami hala 45'te
    kesiyordu. Sonuc: motorun urettigi plana bagimsiz denetci
    "HAFTALIK_AZAMI ihlali" diyordu -- T-57 ile ayni aile, iki taraf
    ayni plan hakkinda farkli sey soyluyor.

    48 saat: sozlesme 45 + 3 saat zorunlu fazla mesai. Tavan 10 oldugu
    icin ne HAFTALIK_AZAMI ne FAZLA_MESAI_TAVANI ihlal olmali.
    """
    from dogrulayici import degerlendir
    g = _sahne()
    g["kurallar"].append({"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK",
                          "aktif": True})
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": d,
                 "bas": 8, "bit": 17,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}
                for d in range(6)]        # 6 x 8 net = 48 saat
    r = degerlendir(g, atamalar)
    kodlar = {i["kural"] for i in r["ihlaller"]}
    assert "HAFTALIK_AZAMI" not in kodlar, (
        "48 saat, 45 normal + 10 fazla mesai tavani icinde; yine de "
        "HAFTALIK_AZAMI ihlali yazildi")


def test_DOGRULAYICI_TAVANIN_USTUNU_yine_de_yakalar():
    """Sinir kalkmadi, yeri degisti: 45 + 10 = 55'in ustu ihlal.

    ⚠ Bu test olmadan ustteki duzeltme "kurali kaldir" ile de yesil
      yanardi.
    """
    from dogrulayici import degerlendir
    g = _sahne()
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": d,
                 "bas": 8, "bit": 18,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}
                for d in range(6)]        # 6 x 9 net = 54... +1 gun yok
    # 6 gun x 9 = 54 <= 55 ; yedinci gun HAFTA_TATILI yuzunden plana
    # konmaz ama DOGRULAYICI elle verilen plana bakar.
    atamalar.append({"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": 6,
                     "bas": 8, "bit": 18,
                     "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                                  "ucretli": False}]})   # 63 saat
    r = degerlendir(g, atamalar)
    kodlar = {i["kural"] for i in r["ihlaller"]}
    assert "HAFTALIK_AZAMI" in kodlar, (
        "63 saat yazildigi halde HAFTALIK_AZAMI susuyor: %r" % sorted(kodlar))
