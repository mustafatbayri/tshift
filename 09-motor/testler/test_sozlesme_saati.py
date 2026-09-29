# -*- coding: utf-8 -*-
"""
SOZLESME SAATI DOLDURULUR -- K-39

⚠ NEDEN (Mustafa, 29 Eylul)
    > "Turkiye'de calisma saati basina maas verilmedigi, direkt net maas
    >  verildigi icin, tam zamanli bir calisanin 43 saat calismasi demek
    >  ona 2 saat fazla para veriyorum demektir. Boyle plan yapilmaz.
    >  Bunu esnetemeyiz."

  Yani eksik planlama KANUNU degil BUTCEYI deler -- ama yine de yapilmaz.

  Olculdu (29 Eylul, 350 kisilik sahne): 45 saat sozlesmeli 17 kisiden
  45'i tutturan SIFIR, ortalama 38,2 saat. Plan yine de "0 sert ihlal,
  yayinlanabilir: True" donuyordu. Uc sebepten:
    1. SAAT_DENGESI yumusakti   -> ihlal degil, ceza
    2. tek tarafli + 2 saat tolerans -> 43 saat bedavaydi
    3. DOGRULAYICIDA GOVDESI YOKTU   -> bagimsiz denetci hic bakamiyordu

IZIN NASIL SAYILIR
  Yillik izin UCRETLIDIR: izin gunu de "parasi odenen saat"tir. Dolayisiyla
  eksik planlama sayilmaz.

      gunluk norm = haftalik_saat / gun_sayisi
      gereken     = haftalik_saat - (izin gunu x gunluk norm)

  `gun_sayisi` sozlesmeden gelir (6 gun x 7,5 saat, ya da 5 gun x 9 saat).
  ⚠ Bu alan olmadan izin saate cevrilemez: ayni 45 saat, 6 gunluk desende
    bir izin gunu 7,5 saat, 5 gunluk desende 9,0 saat eder.

YARI ZAMANLI
  Kisiye ozel taban YOKTUR ve sozlesmede saat de YAZILMAZ (Mustafa,
  29 Eylul: "Hicbir calisan icin bu 20 saat calisir gibi bir deger
  atamayacagiz"). Tavan emsal tam surelinin tamami: 45 saat.
  "Yasa da 45 saate kadar calistirabilirsin, bu fazla mesaiye girmez
  diyor." 30-45 arasi "fazla surelerle calisma"dir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_sozlesme_saati.py -v
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import _net_saat                            # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

# 08:00-16:30 = 8,5 brut ; 60 dk ucretsiz yemek -> 7,5 net ; 6 gun = 45 saat
SABLON = {"id": "V1", "ekip": "E", "bas": 8, "bit": 16.5, "mola_dk": 60,
          "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                               "ucretli": False}]}


def _kurallar():
    return [
        {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False},
        {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
        {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
         "parametreler": {"azami_saat": 11}},
        {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
         "parametreler": {"azami_saat": 45}},
        {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
        {"kod": "SAAT_DENGESI", "tur": "SERT", "aktif": True, "yasal": False,
         "kabul_edilebilir": True},
        {"kod": "PART_TIME_LIMIT", "tur": "SERT", "aktif": True, "yasal": True},
    ]


def _sahne(kisi=4, izinli=(), musait_degil=(), tip="tam_zamanli",
           haftalik=45, gun_sayisi=6):
    """⚠ TALEP BILEREK DUSUK: asgari 1 kisi.

    Kapsama kimseyi 45 saate zorlamiyor. Yani planda 45 saat cikiyorsa
    sebebi SOZLESME kuralidir, talep degil -- olculen sey tam olarak bu.
    """
    calisanlar = []
    for i in range(1, kisi + 1):
        soz = {"tip": tip, "haftalik_saat": haftalik}
        if tip == "tam_zamanli":
            soz["gun_sayisi"] = gun_sayisi
        calisanlar.append({
            "id": "C%d" % i, "ekipler": ["E"], "sozlesme": soz,
            "izinler": [{"gun": g, "tip": "yillik", "durum": "onayli"}
                        for g in (izinli if i == 1 else ())],
            "uygunluk": [{"tip": "uygun_degil", "gun": g, "bas": 0, "bit": 24}
                         for g in (musait_degil if i == 1 else ())]})
    return {
        "profil": "DENGELI",
        "calisanlar": calisanlar,
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(6) for s in range(9, 16)],
        "kurallar": _kurallar(),
        "kilitler": [], "donmus_gunler": [],
    }


def _saatler(g, c):
    sab = {t["id"]: t for t in g["vardiya_sablonlari"]}
    net = collections.Counter()
    for a in c.get("atamalar") or []:
        net[a["calisan"]] += _net_saat(sab[a["sablon"]])
    return net


# ----------------------------------------------------------------------
# 1 - Cozucu tarafi
# ----------------------------------------------------------------------

def test_SOZLESME_SAATI_TUTTURULAMAZSA_plan_REDDEDILIR():
    """Kural SERT oldu: 45 saat tutmuyorsa plan uretilmez.

    ⚠ NEDEN BOYLE KURULDU
      Ilk yazimda test "planda 45 saat cikmali" diyordu ve YAZILDIGI ANDA
      YESILDI: kural yumusak olsa bile, talep dusuk oldugu icin cozucunun
      45 saat yazmamak icin bir sebebi yoktu. Yani test hicbir sey
      olcmuyordu. Bugun ayni tuzaga bir kez daha dusuldu.

      Sinanacak sey SONUC degil SERTLIK: tutturulamadiginda ne oluyor?
      Yumusak kural ceza yazar ve plani gene de uretir; sert kural
      reddeder.

    Sahne: C1 iki gun MUSAIT DEGIL (izin degil!). Elinde 7 - 2 - 1 (hafta
    tatili) = 4 gun kaliyor -> en cok 30 saat. Sozlesme 45.
    """
    g = _sahne(kisi=1, musait_degil=(0, 1))
    # ⚠ Talep yalniz C1'in MUSAIT oldugu gunlere konur. Ilk yazimda 0. ve
    #   1. gune de talep vardi; sahne ASGARI_KAPSAMA yuzunden zaten
    #   cozumsuzdu ve test YANLIS SEBEPLE yesil yaniyordu.
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(2, 6) for s in range(9, 16)]
    c = coz(g, {"azami_saniye": 25, "durgunluk_saniye": 8})
    assert c["durum"] != "cozuldu", (
        "sozlesme saati tutturulamadigi halde plan uretildi -- kural hala "
        "yumusak. Uretilen saatler: %r" % dict(_saatler(g, c)))


def test_IZIN_ayni_sahneyi_COZULUR_HALE_getirir():
    """Ayni fiziksel durum, farkli SEBEP: izin borcu dusurur, musaitsizlik dusurmez.

    Ustteki sahnede C1 iki gun musait degildi ve plan reddedildi. Burada
    ayni iki gun ONAYLI YILLIK IZIN. Yillik izin ucretlidir -- yani o
    saatlerin parasi zaten odeniyor, eksik planlama sayilmaz:

        gereken = 45 - (2 gun x 7,5) = 30 saat

    ⚠ Bu iki test BIRLIKTE anlamlidir. Tek baslarina "cozuldu / cozulmedi"
      derler; yan yana konduklarinda kuralin izni DOGRU sebeple dusurdugunu
      kanitlarlar.
    """
    g = _sahne(kisi=1, izinli=(0, 1))
    # Ustteki sahneyle AYNI talep -- tek fark sebep (izin / musaitsizlik).
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(2, 6) for s in range(9, 16)]
    c = coz(g, {"azami_saniye": 25, "durgunluk_saniye": 8})
    assert c["durum"] == "cozuldu", (
        "izin gunleri sozlesme saatinden dusulmedi: %s" % c["durum"])
    net = _saatler(g, c)
    assert net.get("C1", 0) >= 30, (
        "izin dusuldukten sonraki 30 saatlik borc doldurulmadi: %s"
        % net.get("C1"))


def test_YARI_ZAMANLI_az_calismasi_IHLAL_DEGIL():
    """Yari zamanlida taban yok: az calismak kural ihlali sayilmaz.

    ⚠ ILK YAZIMI YANLIS SEYI OLCUYORDU
      Once "uretilen planda yari zamanli 20 saatin altinda kalmali" diye
      yazilmisti. Tavan 45'e cikinca test kirmizi yandi -- ama dogru
      sebepten degil: cozucu DORT yari zamanlinin da 45 saatini yazmisti.
      Talep asgari 1 kisiydi.

      Sebebi su: modelde yari zamanli saatinin MALIYETI YOK. Onlari
      sinirlayan tek sey eskiden kendi sozlesme saatleriydi; o kalkti.
      Yani cozucunun az yazmak icin hicbir sebebi yok (bkz. T-54).

      Kuralin gercek iddiasi "az calisirsa ihlal yazilmaz" -- ve bu,
      cozucunun keyfine birakilmadan DOGRULAYICIYA sorularak olculur.
    """
    g = _sahne(kisi=1, tip="yari_zamanli", haftalik=20)
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": 0,
                 "bas": 8, "bit": 16.5,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}]     # tek gun, 7,5 saat
    r = degerlendir(g, atamalar)
    sd = [i for i in r["ihlaller"] if i["kural"] == "SAAT_DENGESI"]
    assert not sd, (
        "yari zamanli az calisti diye ihlal yazilmis: %r" % sd)


def test_YARI_ZAMANLI_tavani_KISIDEN_degil_MEVZUATTAN_gelir():
    """Mustafa: "Kisi icin su kadar saat max diye kisit girmemize gerek yok."

    Tavan emsal tam surelinin tamami = 45 saat. Yani 20 saat sozlesmeli
    biri gerektiginde 30 saat de calisabilir.

    Sahne: 4 gun talep -> 30 saat gerekiyor. Kisinin sozlesmesi 20 saat.
    ESKI davranis (tavan = kisinin sozlesmesi) bunu REDDEDERDI.
    """
    g = _sahne(kisi=1, tip="yari_zamanli", haftalik=20)
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(4) for s in range(9, 16)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] == "cozuldu", (
        "yari zamanli hala KENDI sozlesmesiyle sinirlaniyor: %s" % c["durum"])
    net = _saatler(g, c)
    assert net.get("C1", 0) >= 30, (
        "4 gunluk talep karsilanmamis: %s" % net.get("C1"))


def test_YARI_ZAMANLI_45_saat_tavani_HALA_baglar():
    """Tavan kalkmadi, yeri degisti: 45 saatin ustu yine yasak.

    ⚠ Bu test tavan 30'ken de vardi; 45'e cikarilinca sahnesi buyutuldu.
      Gorevi ayni: "kisiye ozel tavan kalkti" ile "tavan kalkti" ayri
      seylerdir.

    6 gun talep -> 45 saat gerekiyor; ustune hafta tatili de var, yani
    6 gun calisip 45'i gecmek gerekir: plan uretilmemeli.
    """
    g = _sahne(kisi=1, tip="yari_zamanli", haftalik=20)
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(7) for s in range(9, 16)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] != "cozuldu", (
        "yari zamanli 30 saatlik mevzuat tavanini asti: %r"
        % dict(_saatler(g, c)))


# ----------------------------------------------------------------------
# 2 - Dogrulayici tarafi (#7.6: cozucu kendi isini kendi onaylayamaz)
# ----------------------------------------------------------------------

def test_DOGRULAYICI_eksik_sozlesme_saatini_gorur():
    """Kural cozucude var, dogrulayicida YOKTU -- yani denetlenmiyordu.

    Elle kurulmus bir plan veriyoruz: kisi 45 yerine 37,5 saat calisiyor
    ve izni de yok. Bagimsiz denetci bunu SERT ihlal olarak yazmali.
    """
    g = _sahne(kisi=1)
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": d,
                 "bas": 8, "bit": 16.5,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}
                for d in range(5)]          # 5 gun x 7,5 = 37,5 saat
    r = degerlendir(g, atamalar)
    kodlar = [i["kural"] for i in r["ihlaller"]]
    assert "SAAT_DENGESI" in kodlar, (
        "dogrulayici eksik sozlesme saatini gormedi. Bulunanlar: %r"
        % sorted(set(kodlar)))


def test_DOGRULAYICI_izinli_calisani_SUCLAMAZ():
    """37,5 saat, ama bir gun onayli izin var -> ihlal YOK."""
    g = _sahne(kisi=1, izinli=(5,))
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V1", "gun": d,
                 "bas": 8, "bit": 16.5,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}
                for d in range(5)]
    r = degerlendir(g, atamalar)
    sd = [i for i in r["ihlaller"] if i["kural"] == "SAAT_DENGESI"]
    assert not sd, (
        "izin gunu dusulmedigi icin izinli calisan ihlalli gorunuyor: %r" % sd)


def test_SOZLESME_SAATI_OLMAYAN_yari_zamanli_da_tavana_tabi():
    """Mustafa (29 Eylul): "Yari zamanli icin sozlesmede saat girilmeyecek."

    ⚠ NEDEN BU TEST VAR
      Tavan kosulu once `haftalik_saat` alaninin VARLIGINA bakiyordu. Alan
      kaldirilinca kosul sessizce atlanacak ve yari zamanliya HIC tavan
      kalmayacakti -- kural kagitta durur, kodda calismazdi. Kosul artik
      sozlesme TIPINE bakiyor; bu test onu civiliyor.

    Sahne: 7 gun talep -> hafta tatili yuzunden zaten cozumsuz olmali;
    olculen sey tavanin TIPE bagli uygulandigidir.
    """
    g = _sahne(kisi=1, tip="yari_zamanli", haftalik=20)
    for c in g["calisanlar"]:
        c["sozlesme"] = {"tip": "yari_zamanli"}      # haftalik_saat YOK
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(7) for s in range(9, 16)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] != "cozuldu", (
        "sozlesmede saat yazmayan yari zamanliya tavan uygulanmadi: %r"
        % dict(_saatler(g, c)))
