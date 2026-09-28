# -*- coding: utf-8 -*-
"""
CEYREK SAAT COZUNURLUGU -- K-34'un kirmizi kaniti

NE KORUYORLAR
  K-34 (28 Eylul, Mustafa): motorun zaman birimi SAAT degil CEYREK SAAT.

    > "Molalar zaten normalde planlanirken, gun icinde 15 dk lik dilimlere
    >  dagitiliyor. Yani 15:15'e de mola koyabiliyorlar, 15:30'a da 15:45'e
    >  de. Dogrusu bu."

  Yani saat dilimi bir MODELLEME KOLAYLIGI degil, gercege AYKIRI bir
  varsayimdi. Mola operasyonu ceyrek saatle yapiliyor.

⚠ YEMEK ILE DINLENME AYRI SEYLER -- KARISTIRILMAZ
  Mustafa, 28 Eylul: "Yemek ile molayi birbirine karistirma."

  Bu uyarinin sayisal karsiligi, benim yazdigim "2.29x sisme" rakaminin
  neyi gizledigi:

      yemek     60 dk gercek  ->  60 dk modelde   1.00x   HATA YOK
      dinlenme  45 dk gercek  -> 180 dk modelde   4.00x   HATA BURADA
      -------------------------------------------------------------
      TOPLAM   105 dk         -> 240 dk           2.29x   <- harmanlanmis

  2.29x, YEMEGIN DOGRULUGUNU dinlenmenin hatasiyla ortaliyor. Bu dosyadaki
  testler ikisini AYRI AYRI olcer; hicbir test ikisinin toplamina bakmaz.

BU TESTLER BUGUN KIRMIZI YANAR
  Yazildiklari anda motor saat dilimiyle calisiyordu. Kirmizi olmalari
  KANITTIR (#16.4): duzeltme yapilmadan once hatanin gorulmesi.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_ceyrek_saat.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir, zaman                   # noqa: E402
from orkestra import coz_ve_onar                             # noqa: E402


CEYREK = 0.25

V9_18 = {"id": "V", "bas": 9, "bit": 18, "mola_dk": 60, "gunler": [0]}

# 1 yemek (60 dk) + 3 dinlenme (15 dk). K-32'nin ornegi.
POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]


def _sahne(kisi=4, asgari=2, taban=None, politika=None, sablon=None):
    s = dict(sablon or V9_18)
    g = {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [s],
        "talep": [{"ekip": "E", "gun": 0, "saat": h, "asgari": asgari,
                   "hedef": kisi} for h in range(int(s["bas"]), int(s["bit"]))],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True,
             "yasal": True, "kabul_edilebilir": False},
            {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True,
             "yasal": False},
        ],
        "kilitler": [], "donmus_gunler": [],
        "mola_politikasi": politika or POLITIKA,
    }
    if taban is not None:
        g["kurallar"].append(
            {"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False,
             "parametreler": {"asgari_sahada": taban}})
    return g


def _molalar(atama, tip):
    return [m for m in (atama.get("molalar") or [])
            if zaman.mola_tipi(m) == tip]


def _ceyrege_oturuyor(x):
    """Bu saat degeri 15 dakikalik bir sinira mi denk geliyor."""
    return abs(round(x * 4) - x * 4) < 1e-9


# ----------------------------------------------------------------------
# 1 · DINLENME -- hatanin tamami burada
# ----------------------------------------------------------------------

def test_dinlenme_15_DAKIKA_surer_bir_saat_degil():
    """15 dk'lik dinlenme molasi 15 dk surer. Bugun 1 saat sayiliyor.

    Bu, 4.00x sismenin dogrudan olcumu. Yemege BAKMAZ.
    """
    c = coz_ve_onar(_sahne(), {"azami_saniye": 30})
    assert c["durum"] == "cozuldu", c.get("durum")
    a = c["atamalar"][0]
    for m in _molalar(a, zaman.DINLENME):
        sure_dk = (m["bit"] - m["bas"]) * 60
        assert abs(sure_dk - 15) < 1e-9, (
            "dinlenme molasi %g dk surdu, 15 dk olmaliydi -- motor hala "
            "tam saat dilimi kullaniyor (mola: %s)" % (sure_dk, m))


def test_dinlenme_CEYREK_sinirina_konabilir():
    """Dinlenme 11:15, 11:30, 11:45'e de konabilmeli -- yalniz 11:00'e degil.

    Mustafa'nin cumlesi: "15:15'e de mola koyabiliyorlar, 15:30'a da."
    Bugun butun dinlenmeler tam saatte basliyor.
    """
    from cozucu.model import _dinlenme_baslangiclari
    adaylar = _dinlenme_baslangiclari(V9_18, 3, 15)
    duz = [s for grup in adaylar for s in grup]
    assert duz, "hic dinlenme adayi uretilmedi"
    ceyrekli = [s for s in duz if abs(s - int(s)) > 1e-9]
    assert ceyrekli, (
        "butun dinlenme adaylari TAM SAATTE: %s -- ceyrek sinirlari "
        "(11.25, 11.5, 11.75 gibi) hic uretilmiyor" % duz)


def test_dinlenme_sahada_YALNIZ_kendi_ceyregini_dusurur():
    """11:15-11:30 molasi 11:00'i ve 11:45'i sahadan DUSURMEZ.

    Bugun 15 dk'lik mola koca saati kapatiyor; bu testin olctugu tam
    olarak o.
    """
    atama = {"calisan": "C1", "ekip": "E", "sablon": "V", "gun": 0,
             "bas": 9, "bit": 18,
             "molalar": [{"bas": 11.25, "bit": 11.5, "tip": "dinlenme"}]}
    assert zaman.sahada_mi(atama, 0, 11.0), "11:00'de sahada olmaliydi"
    assert not zaman.sahada_mi(atama, 0, 11.25), "11:15'te molada olmaliydi"
    assert zaman.sahada_mi(atama, 0, 11.5), "11:30'da sahada olmaliydi"
    assert zaman.sahada_mi(atama, 0, 11.75), "11:45'te sahada olmaliydi"


# ----------------------------------------------------------------------
# 2 · YEMEK -- burada hata YOKTU, bozulmamali
# ----------------------------------------------------------------------

def test_yemek_TEK_BLOK_ve_tam_suresinde_kalir():
    """Yemek zaten dogru modelleniyordu (1.00x). Ceyrek gecisi bunu BOZMAMALI.

    K-14 ayakta: yemek tek bloktur, bolunemez.
    """
    c = coz_ve_onar(_sahne(), {"azami_saniye": 30})
    assert c["durum"] == "cozuldu"
    for a in c["atamalar"]:
        y = _molalar(a, zaman.YEMEK)
        assert len(y) == 1, "yemek tek blok olmali, %d blok geldi" % len(y)
        sure_dk = (y[0]["bit"] - y[0]["bas"]) * 60
        assert abs(sure_dk - 60) < 1e-9, (
            "yemek %g dk surdu, 60 olmaliydi" % sure_dk)


def test_yemek_de_CEYREK_sinirina_konabilir():
    """Yemek 12:30'da da baslayabilmeli. Tek blok olmasi bunu engellemez.

    Yemek ile dinlenme ayri seylerdir ama ikisi de ayni ZAMAN IZGARASINI
    kullanir; izgara ceyrek saattir.
    """
    from cozucu.model import _mola_baslangiclari, MOLA_PENCERESI_VARSAYILAN
    adaylar = _mola_baslangiclari(V9_18, MOLA_PENCERESI_VARSAYILAN, 60)
    ceyrekli = [s for s in adaylar if s is not None and abs(s - int(s)) > 1e-9]
    assert ceyrekli, (
        "butun yemek adaylari TAM SAATTE: %s -- 12:30 secenegi yok" % adaylar)


def test_yemek_suresi_DEGISMEDI_dinlenme_duzelirken():
    """Regresyon bekcisi: dinlenmeyi duzeltirken yemegi kisaltmayalim.

    Bu test 28 Eylul'deki uyarinin dogrudan karsiligi:
    "Yemek ile molayi birbirine karistirma."
    """
    c = coz_ve_onar(_sahne(), {"azami_saniye": 30})
    assert c["durum"] == "cozuldu"
    a = c["atamalar"][0]
    yemek_dk = sum((m["bit"] - m["bas"]) * 60 for m in _molalar(a, zaman.YEMEK))
    dinl_dk = sum((m["bit"] - m["bas"]) * 60 for m in _molalar(a, zaman.DINLENME))
    assert abs(yemek_dk - 60) < 1e-9, "yemek toplami %g dk" % yemek_dk
    assert abs(dinl_dk - 45) < 1e-9, "dinlenme toplami %g dk" % dinl_dk


# ----------------------------------------------------------------------
# 3 · SONUC -- T-44'un esigi dusmeli
# ----------------------------------------------------------------------

def test_saha_tabani_KUCUK_ekipte_de_calisir():
    """T-44'un cozumu: taban 2 icin 8 kisi degil, ~3 kisi yetmeli.

    Bugunku esik N >= 4F (olculdu, 15/15). Ceyrek cozunurlukte kisi basina
    sahada olmama suresi 4 saatten 1 saat 45 dk'ya iner; esik ~1.24F'e
    dusmeli. 4 kisi / taban 2 rahat cozulmeli.
    """
    c = coz_ve_onar(_sahne(kisi=4, asgari=2, taban=2), {"azami_saniye": 45})
    assert c["durum"] == "cozuldu", (
        "4 kisi / taban 2 cozulemedi (%s) -- bugunku geometride N >= 4F "
        "gerekiyor, yani 8 kisi" % c.get("durum"))
    for h4 in range(9 * 4, 18 * 4):
        saat = h4 / 4.0
        sahada = sum(1 for a in c["atamalar"] if zaman.sahada_mi(a, 0, saat))
        assert sahada >= 2, (
            "saat %.2f: sahada %d kisi (taban 2)" % (saat, sahada))


def test_molalar_gunun_HER_yerine_dagilabilir():
    """9, 10 ve 17. saatlere de mola dusebilmeli.

    T-44'te olculdu: bugun bu uc saate HICBIR mola dusemiyor, cunku aday
    pencereleri gunun ortasina sikismis durumda.
    """
    c = coz_ve_onar(_sahne(kisi=8, asgari=2), {"azami_saniye": 45})
    assert c["durum"] == "cozuldu"
    dolu = set()
    for a in c["atamalar"]:
        for b, s in zaman.mola_araliklari(a):
            q = int(round(b * 4))
            while q < int(round(s * 4)):
                dolu.add(q / 4.0)
                q += 1
    kenar = {x / 4.0 for x in range(9 * 4, 11 * 4)} | \
            {x / 4.0 for x in range(17 * 4, 18 * 4)}
    assert dolu & kenar, (
        "vardiyanin ilk iki ve son bir saatine hic mola dusmedi -- "
        "dolu dilimler: %s" % sorted(dolu))


# ----------------------------------------------------------------------
# 4 · SESSIZ GECIS -- ceyrege saklanan ihlal
# ----------------------------------------------------------------------
#
# 28 Eylul, K-34 uygulanirken bulundu. K-33'u doguran sessiz gecisin
# AYNISI, bu kez bir ceyregin icine saklanmis:
#
#   Iki kisilik planda ikisi de 14:15-14:30 arasi molada. Saat 14:00'de
#   ve 15:00'te sahadalar; 14:15'te SIFIR kisi var.
#
#   Dogrulayici: ihlal YOK. Cunku `_talep_hucreleri` TAM SAAT uretiyor ve
#   kural yalniz o anlara bakiyordu.
#
# Ceyrek cozunurluk molayi ceyrege tasiyinca, ihlali de ceyrege tasidi.
# Kural saat basina bakmaya devam etseydi K-34 sessiz gecisi DUZELTMEZ,
# GIZLERDI.

def _iki_kisi_ayni_anda_molada(mola_bas, mola_bit):
    girdi = {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C%d" % i, "ekipler": ["E"],
                        "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
                        "izinler": [], "uygunluk": []} for i in (1, 2)],
        "vardiya_sablonlari": [dict(V9_18)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 2}
                  for s in range(9, 18)],
        "kurallar": [{"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
                      "yasal": False, "kabul_edilebilir": False,
                      "parametreler": {"asgari_sahada": 2}},
                     {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK",
                      "aktif": True, "yasal": False}],
        "kilitler": [], "donmus_gunler": [],
    }
    atamalar = [{"calisan": "C%d" % i, "ekip": "E", "sablon": "V", "gun": 0,
                 "bas": 9, "bit": 18,
                 "molalar": [{"bas": mola_bas, "bit": mola_bit,
                              "tip": "dinlenme"}]} for i in (1, 2)]
    return degerlendir(girdi, atamalar)


def test_taban_CEYREKTE_delinirse_de_gorulur():
    """14:15'te sahada sifir kisi -> SERT ihlal. Saat basi kontrolu yetmez."""
    r = _iki_kisi_ayni_anda_molada(14.25, 14.5)
    kodlar = {i["kural"] for i in r["ihlaller"]}
    assert "SAHADA_ASGARI" in kodlar, (
        "14:15'te sahada SIFIR kisi var ama ihlal yazilmadi -- dogrulayici "
        "hala yalniz TAM SAATE bakiyor (yazilan ihlaller: %s)" % (kodlar or "yok"))


def test_yumusak_kapsama_da_CEYREGE_bakar():
    """MOLA_KAPSAMASI (yumusak) ayni korlukten muzdarip olmamali.

    Yumusak olmasi gormemesini haklı cikarmaz: puan dusurmuyorsa plan
    'daha iyi' gorunur ve yanlis plan secilir.
    """
    r = _iki_kisi_ayni_anda_molada(14.25, 14.5)
    kodlar = {i["kural"] for i in r["ihlaller"]}
    assert "MOLA_KAPSAMASI" in kodlar, (
        "ceyrekteki kapsama bosulugu yumusak kurala da gorunmedi: %s"
        % (kodlar or "yok"))


def test_saat_basinda_delinen_taban_HALA_gorulur():
    """Geriye donuk uyum: tam saatteki ihlal elbette gorulmeye devam etmeli."""
    r = _iki_kisi_ayni_anda_molada(14.0, 15.0)
    kodlar = {i["kural"] for i in r["ihlaller"]}
    assert "SAHADA_ASGARI" in kodlar, "tam saatteki ihlal kayboldu: %s" % kodlar
