# -*- coding: utf-8 -*-
"""
GECE UYGUNLUGU -- "bu kisi gece vardiyasi yapamaz" (K-40)

⚠ NEDEN (Mustafa, 29 Eylul)
    > "Kullanici kartinda gece vardiyasi yapamaz gibi bir ifadeye ihtiyacimiz
    >  var. Vardiya plani yapilirken de vardiya gece vardiyasidir diye bir
    >  isaret koymamiz gerekiyor. Bunu KULLANICI isaretleyecek. Boylelikle
    >  gece vardiyalarina uygun olmayan calisanlari ilgili vardiyadan
    >  direkt elemis olacagiz."

  Bu alan YOKTU. Motor gece vardiyasini SAAT ARALIGINDAN tahmin ediyordu
  (`GECE_PENCERESI`) ve bunu yalniz ADALET_DENGESI'nin "gece" boyutunda,
  yani adil dagitim icin kullaniyordu. "Gece calisamaz" diye bir kayit
  hicbir yerde yoktu; ancak her gece icin ayri `uygunluk` araligi yazarak
  taklit edilebilirdi -- zahmetli ve hataya acik.

IKI YENI ALAN (girdi sozlesmesi)
    vardiya_sablonlari[].gece_vardiyasi : bu sablon gece vardiyasidir
    calisanlar[].gece_calisamaz         : bu kisi gece vardiyasi yapamaz

⚠ ISARET, TAHMINI EZER
  23:00-07:00 tahmini cogu zaman dogru calisir ama 22:00-06:00 ya da
  00:00-08:00 gibi sinir durumlarinda firmanin kendi tanimiyla celisebilir.
  Mustafa'nin istedigi ISARET: kullanici soyler, motor tahmin etmez.

⚠ ISARET YOKSA TAHMINE DUSULUR -- ve BILDIRILIR
  Gecisi olmayan depolar kirilmasin diye: `gece_vardiyasi` yazilmamis bir
  sablon, saat araligina gore degerlendirilir. Ama bu SESSIZ OLMAZ; not
  yazilir. Isaretlenmemis bir gece vardiyasi, korunmasi gereken birini
  sessizce geceye koyabilirdi.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_gece_uygunlugu.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

GUNDUZ = {"id": "V-GUN", "ekip": "E", "bas": 9, "bit": 17, "mola_dk": 60,
          "gece_vardiyasi": False,
          "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                               "ucretli": False}]}
GECE = {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60,
        "gece_vardiyasi": True,
        "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                             "ucretli": False}]}


def _sahne(sablonlar, gece_calisamaz=("C1",), talep_saatleri=(9, 16),
           gece_talebi=False, kisi=2):
    talep = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
             for s in range(*talep_saatleri)]
    if gece_talebi:
        talep += [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
                  for s in range(23, 24)]
    return {
        "profil": "DENGELI",
        "calisanlar": [
            dict({"id": "C%d" % i, "ekipler": ["E"],
                  "sozlesme": {"tip": "yari_zamanli"},
                  "izinler": [], "uygunluk": []},
                 **({"gece_calisamaz": True} if "C%d" % i in gece_calisamaz
                    else {}))
            for i in range(1, kisi + 1)],
        "vardiya_sablonlari": [dict(t) for t in sablonlar],
        "talep": talep,
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GECE_UYGUNLUGU", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def _kimler(c, sablon):
    return {a["calisan"] for a in (c.get("atamalar") or [])
            if a["sablon"] == sablon}


# ----------------------------------------------------------------------
# Cozucu
# ----------------------------------------------------------------------

def test_GECE_CALISAMAYAN_gece_vardiyasina_ATANMAZ():
    """Asil sinav. C1 gece calisamaz; gece talebini C2 karsilamali."""
    g = _sahne([GUNDUZ, GECE], gece_talebi=True)
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] == "cozuldu", c["durum"]
    assert "C1" not in _kimler(c, "V-GECE"), (
        "gece calisamayan kisi gece vardiyasina atandi")


def test_GECE_CALISAMAYAN_GUNDUZ_vardiyasina_ATANABILIR():
    """⚠ Fazla kisitlamadigimizin kaniti. Kural yalniz GECEYI kapatir."""
    g = _sahne([GUNDUZ], gece_calisamaz=("C1", "C2"), kisi=2)
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] == "cozuldu", (
        "gece calisamayanlar gunduz vardiyasindan da elendi: %s" % c["durum"])
    assert c.get("atamalar"), "plan bos"


def test_TEK_KISI_gece_calisamiyorsa_plan_URETILMEZ():
    """Gece talebini karsilayacak kimse kalmiyorsa cozumsuz olmali.

    Bu, kisitin gercekten SERT oldugunu kanitlar: yumusak olsaydi motor
    C1'i geceye koyup ceza yazar ve plan "cozuldu" donerdi.
    """
    g = _sahne([GUNDUZ, GECE], gece_calisamaz=("C1", "C2"),
               gece_talebi=True, kisi=2)
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] != "cozuldu", (
        "kimse gece calisamazken gece talebi karsilandi: %r"
        % _kimler(c, "V-GECE"))


def test_ISARET_TAHMINI_EZER():
    """Saat araligi geceye giriyor ama kullanici "gece degil" demis.

    ⚠ ILK YAZIMI HICBIR SEY OLCMUYORDU
      Sonu `assert True` ile bitiyordu. Mutasyon yakaladi: isaret tamamen
      yok sayilip hep tahmine dusuldugunde butun testler YESIL kaldi.
      "Isaret tahmini ezer" cumlesini hicbir satir kanitlamiyordu.

      Simdi sahne oyle kuruldu ki cevap TEK: 23:00-07:00 araligindaki
      sablon "gece degil" diye isaretli ve o saati kapatabilecek TEK kisi
      gece calisamayan C1. Isaret gecerliyse plan cikar; tahmin galip
      gelirse C1 elenir ve plan cozumsuz olur.
    """
    gece_degil = dict(GECE, id="V-SAYILMAZ", gece_vardiyasi=False)
    g = _sahne([gece_degil], gece_talebi=True, talep_saatleri=(23, 24),
               gece_calisamaz=("C1",), kisi=1)
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert c["durum"] == "cozuldu", (
        "kullanici 'gece degil' dedigi halde sablon gece sayildi: %s"
        % c["durum"])
    assert "C1" in _kimler(c, "V-SAYILMAZ"), (
        "isaret yok sayildi, C1 elendi: %r" % (c.get("atamalar") or []))


def test_DOGRULAYICI_da_ISARETE_uyar():
    """Ayni kural dogrulayicida da isarete uymali -- yoksa motor ile
    denetci ayni plan hakkinda farkli sey soyler."""
    gece_degil = dict(GECE, id="V-SAYILMAZ", gece_vardiyasi=False)
    g = _sahne([gece_degil], gece_talebi=True, talep_saatleri=(23, 24),
               gece_calisamaz=("C1",), kisi=1)
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V-SAYILMAZ",
                 "gun": 0, "bas": 23, "bit": 31,
                 "molalar": [{"tip": "yemek", "bas": 26, "bit": 27,
                              "ucretli": False}]}]
    r = degerlendir(g, atamalar)
    gece = [i for i in r["ihlaller"] if i["kural"] == "GECE_UYGUNLUGU"]
    assert not gece, (
        "dogrulayici 'gece degil' isaretini yok saydi: %r" % gece)


def test_ISARET_YOKSA_SAAT_ARALIGINDAN_tahmin_edilir_ve_BILDIRILIR():
    """Gecisi olmayan depolar kirilmasin; ama sessiz kalmasin.

    ⚠ Sessiz kalsaydi: isaretlenmemis bir gece vardiyasi, korunmasi
      gereken birini sessizce geceye koyardi.
    """
    isaretsiz = dict(GECE)
    del isaretsiz["gece_vardiyasi"]
    g = _sahne([GUNDUZ, isaretsiz], gece_talebi=True)
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 8})
    assert "C1" not in _kimler(c, "V-GECE"), (
        "isaretsiz gece vardiyasina gece calisamayan kisi atandi")
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "gece_vardiyasi" in notlar, (
        "isaretsiz sablon sessizce tahmin edildi, not yazilmadi: %r"
        % (c.get("uygulanmayan_notlar") or []))


# ----------------------------------------------------------------------
# Dogrulayici (#7.6 -- cozucu kendi isini kendi onaylayamaz)
# ----------------------------------------------------------------------

def test_DOGRULAYICI_gece_ihlalini_gorur():
    g = _sahne([GUNDUZ, GECE], gece_talebi=True)
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V-GECE", "gun": 0,
                 "bas": 23, "bit": 31,
                 "molalar": [{"tip": "yemek", "bas": 26, "bit": 27,
                              "ucretli": False}]}]
    r = degerlendir(g, atamalar)
    kodlar = [i["kural"] for i in r["ihlaller"]]
    assert "GECE_UYGUNLUGU" in kodlar, (
        "dogrulayici gece ihlalini gormedi. Bulunanlar: %r" % sorted(set(kodlar)))


def test_DOGRULAYICI_gunduz_atamasini_SUCLAMAZ():
    g = _sahne([GUNDUZ, GECE], gece_talebi=True)
    atamalar = [{"calisan": "C1", "ekip": "E", "sablon": "V-GUN", "gun": 0,
                 "bas": 9, "bit": 17,
                 "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                              "ucretli": False}]}]
    r = degerlendir(g, atamalar)
    gece = [i for i in r["ihlaller"] if i["kural"] == "GECE_UYGUNLUGU"]
    assert not gece, "gunduz atamasi gece ihlali sayildi: %r" % gece
