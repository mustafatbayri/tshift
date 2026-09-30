# -*- coding: utf-8 -*-
"""
ASGARI_VARDIYA_SURESI ve ARDISIK_GECE_LIMIT -- FIRMA SINIRLARI

IKISI DE FIRMA KURALI: SERT, yasal DEGIL, kabul edilebilir. Yonetici
ihlali gorup onaylayabilir; plan bu yuzden yayindan dusmez.

ASGARI_VARDIYA_SURESI (#6.2, varsayilan 4 saat)
  "Bir kisiye verilebilecek en kisa vardiya. Cok kisa vardiya calisan
   icin maliyetli."

  ⚠ OLCU BRUT -- vardiyanin suresi, molalar DUSULMEDEN. Bilerek.
    Kaygi calisanin 2 saat is icin yola cikmasi: sahada GECIRDIGI sure.
    Ve olculdu: net olcseydik firmanin KENDI 4 saatlik sablonlari
    (B-YARIM 09-13, M-AKSAMK 17-21) firmanin KENDI 4 saat kuralini her
    kullanimda cigneyecekti -- ekip mola politikasi 4 saatlik vardiyaya
    1,25-1,5 saat mola yaziyor ve net 2,5-2,75 saate dusuyor.
    `GUNLUK_AZAMI` net olcer cunku orada kaygi YORGUNLUK; burada kaygi
    YOL, ve yol molada da gidilmis olur.

ARDISIK_GECE_LIMIT (#6.2, varsayilan 3 gece)
  "Ayni kisiye ust uste verilebilecek azami gece. Firma uyku sagligi
   politikasi."

  ⚠ GECE = K-40'IN ISARETI. Sablonda `gece_vardiyasi` varsa o gecerli;
    yoksa saat araligindan tahmin edilir (ve not yazilir). Iki yerde iki
    farkli gece tanimi olmasin diye ADALET_DENGESI de ayni tespiti
    kullaniyor.
  ⚠ Z-2: vardiya BASLADIGI gune yazilir. Pazartesi 23:00-07:00, pazartesi
    gecesidir.
  ⚠ YALNIZ PLAN HAFTASI. Gecen haftanin son gecelerini gormek icin gecmis
    veri lazim (T-28, acik). `ARDISIK_CALISMA_GUNU` ile ayni sinir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_firma_sinirlari.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402

KISA_KURAL = {"kod": "ASGARI_VARDIYA_SURESI", "tur": "SERT", "aktif": True,
              "yasal": False, "kabul_edilebilir": True,
              "parametreler": {"asgari_saat": 4}}
GECE_KURAL = {"kod": "ARDISIK_GECE_LIMIT", "tur": "SERT", "aktif": True,
              "yasal": False, "kabul_edilebilir": True,
              "parametreler": {"azami_gece": 3}}

GECE = {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60,
        "gece_vardiyasi": True}
GUNDUZ = {"id": "V-GUNDUZ", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60,
          "gece_vardiyasi": False}


def _sahne(kurallar, sablonlar=None):
    return {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C1", "ekipler": ["E"],
                        "sozlesme": {"tip": "tam_zamanli"},
                        "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": list(sablonlar or [GECE, GUNDUZ]),
        "talep": [],
        "kurallar": list(kurallar),
        "kilitler": [], "donmus_gunler": [],
    }


def _a(gun, sablon, bas, bit, molalar=None):
    return {"calisan": "C1", "ekip": "E", "sablon": sablon, "gun": gun,
            "bas": bas, "bit": bit, "molalar": molalar or []}


def _ih(g, atamalar, kod):
    return [i for i in degerlendir(g, atamalar)["ihlaller"]
            if i["kural"] == kod]


# ======================================================================
# ASGARI_VARDIYA_SURESI
# ======================================================================

def test_KISA_govdesi_ARTIK_VAR():
    r = degerlendir(_sahne([KISA_KURAL]), [_a(0, "V", 9, 12)])
    assert "ASGARI_VARDIYA_SURESI" not in r["uygulanmayan_kurallar"]


def test_KISA_asgarinin_altinda_ihlal():
    """3 saatlik vardiya, asgari 4 -> ihlal."""
    ih = _ih(_sahne([KISA_KURAL]), [_a(0, "V", 9, 12)],
             "ASGARI_VARDIYA_SURESI")
    assert len(ih) == 1, ih
    assert abs(ih[0]["olculen"] - 3.0) < 1e-6 and ih[0]["gereken"] == 4, ih[0]


def test_KISA_tam_asgaride_ihlal_YOK():
    """Tam 4 saat -> "en kisa 4" kosulunu saglar."""
    assert not _ih(_sahne([KISA_KURAL]), [_a(0, "V", 9, 13)],
                   "ASGARI_VARDIYA_SURESI")


def test_KISA_olcu_BRUT_molalar_dusulmez():
    """⚠ Olcuyu sabitleyen test.

    09:00-13:00 (4 saat) icinde 1,5 saat mola: net 2,5 saat. Brut olcu
    ihlal YAZMAZ -- firmanin kendi 4 saatlik sablonu kendi 4 saat kuralini
    cignemez. Net olcen bir govde burada ihlal yazardi.
    """
    ih = _ih(_sahne([KISA_KURAL]), [_a(0, "V", 9, 13, molalar=[
        {"tip": "yemek", "bas": 10, "bit": 11, "ucretli": False},
        {"tip": "dinlenme", "bas": 12, "bit": 12.5, "ucretli": True}])],
        "ASGARI_VARDIYA_SURESI")
    assert not ih, "brut 4 saat, ihlal olmamali: %r" % ih


def test_KISA_gece_yarisini_asan_vardiya_DOGRU_olculur():
    """22:00-01:00 = 3 saat (Z-1). `bit - bas` negatif cikmamali."""
    ih = _ih(_sahne([KISA_KURAL]), [_a(0, "V", 22, 25)],
             "ASGARI_VARDIYA_SURESI")
    assert len(ih) == 1 and abs(ih[0]["olculen"] - 3.0) < 1e-6, ih


def test_KISA_ihlal_KABUL_EDILEBILIR():
    """Firma kurali: yonetici gorup onaylayabilir, yayin DURMAZ."""
    r = degerlendir(_sahne([KISA_KURAL]), [_a(0, "V", 9, 12)])
    ih = [i for i in r["ihlaller"] if i["kural"] == "ASGARI_VARDIYA_SURESI"]
    assert ih and ih[0]["yasal"] is False and ih[0]["kabul_edilebilir"] is True


# ======================================================================
# ARDISIK_GECE_LIMIT
# ======================================================================

def _geceler(gunler):
    return [_a(d, "V-GECE", 23, 31) for d in gunler]


def test_GECE_govdesi_ARTIK_VAR():
    r = degerlendir(_sahne([GECE_KURAL]), _geceler([0]))
    assert "ARDISIK_GECE_LIMIT" not in r["uygulanmayan_kurallar"]


def test_GECE_dort_ust_uste_ihlal():
    """Pazartesi-persembe 4 gece, azami 3 -> ihlal."""
    ih = _ih(_sahne([GECE_KURAL]), _geceler([0, 1, 2, 3]),
             "ARDISIK_GECE_LIMIT")
    assert len(ih) == 1, ih
    assert ih[0]["olculen"] == 4 and ih[0]["gereken"] == 3, ih[0]
    assert ih[0]["gun"] == 0, "serinin basladigi gun yazilmali: %r" % ih[0]


def test_GECE_uc_ust_uste_ihlal_YOK():
    assert not _ih(_sahne([GECE_KURAL]), _geceler([0, 1, 2]),
                   "ARDISIK_GECE_LIMIT")


def test_GECE_ARADA_bos_gun_seriyi_KIRAR():
    """0,1,2 + 4,5,6: iki ayri 3'luk seri -- ihlal yok."""
    assert not _ih(_sahne([GECE_KURAL]), _geceler([0, 1, 2, 4, 5, 6]),
                   "ARDISIK_GECE_LIMIT")


def test_GECE_ARADA_GUNDUZ_vardiyasi_da_seriyi_KIRAR():
    """⚠ Seri GECE serisidir, calisma serisi degil.

    0,1,2 gece + 3 gunduz + 4 gece: gece serisi 3'te kirilir.
    Calisma gunlerini sayan bir govde burada 5 gorur ve yanlis ihlal yazar.
    """
    atamalar = _geceler([0, 1, 2, 4]) + [_a(3, "V-GUNDUZ", 8, 16)]
    assert not _ih(_sahne([GECE_KURAL]), atamalar, "ARDISIK_GECE_LIMIT")


def test_GECE_ISARET_yalniz_EKLER_yasal_geceyi_inkar_edemez():
    """⚠ K-43 (30 Eylul gecesi): otomatik isaret TABANDIR. 23:00-07:00
    yonetmelige gore gece; firma "gece degil" dese de gece sayilir.

    ⚠ Bu test 30 Eylul aksamina kadar TERSINI bekliyordu (K-40: "isaret
      tahmini ezer"). Mustafa'nin karari degistirdi: isaret yalniz ekler,
      altina inemez -- inebilseydi gece calisamayan biri 22:00-06:00'ya
      yazilabilirdi.
    """
    inkar = dict(GECE, id="V-X", gece_vardiyasi=False)
    g = _sahne([GECE_KURAL], sablonlar=[inkar, GUNDUZ])
    atamalar = [_a(d, "V-X", 23, 31) for d in (0, 1, 2, 3)]
    assert _ih(g, atamalar, "ARDISIK_GECE_LIMIT"), (
        "firma 'gece degil' dedi diye yasal gece sayilmadi (K-43)")


def test_GECE_ISARET_ekler_yasal_olmayan_aksami_gece_yapar():
    """Firma 15:15-24:00'u gece sayiyorsa (veri setindeki B-AKSAM) firma
    kurali icin gecedir -- yonetmelik saymasa da. Daha siki olmak serbest."""
    aksam = dict(GECE, id="V-A", bas=15.25, bit=24, gece_vardiyasi=True)
    g = _sahne([GECE_KURAL], sablonlar=[aksam, GUNDUZ])
    atamalar = [_a(d, "V-A", 15.25, 24) for d in (0, 1, 2, 3)]
    assert _ih(g, atamalar, "ARDISIK_GECE_LIMIT"), (
        "firmanin 'gece' isareti okunmadi")
    isaretsiz = dict(aksam, id="V-B")
    del isaretsiz["gece_vardiyasi"]
    g2 = _sahne([GECE_KURAL], sablonlar=[isaretsiz, GUNDUZ])
    assert not _ih(g2, [_a(d, "V-B", 15.25, 24) for d in (0, 1, 2, 3)],
                   "ARDISIK_GECE_LIMIT"), "isaretsiz 15:15-24:00 gece sayildi"


def test_GECE_isaretsiz_sablon_SAATTEN_tahmin_edilir():
    """Isaret yoksa saat araligi karar verir -- ve bu durumda gecedir."""
    isaretsiz = {k: v for k, v in GECE.items() if k != "gece_vardiyasi"}
    isaretsiz["id"] = "V-Y"
    g = _sahne([GECE_KURAL], sablonlar=[isaretsiz, GUNDUZ])
    atamalar = [_a(d, "V-Y", 23, 31) for d in (0, 1, 2, 3)]
    assert _ih(g, atamalar, "ARDISIK_GECE_LIMIT"), (
        "isaretsiz 23:00 vardiyasi gece sayilmali")


# ======================================================================
# COZUCU TARAFI
# ======================================================================
#
# ⚠ T-62'nin dersiyle kuruldu: talep oyle ki onu YALNIZ yasak secenek
#   karsilayabiliyor -- kisit yaziliysa plan cozumsuz kalmak ZORUNDA.

def test_COZUCU_asgarinin_altindaki_sablonu_ATAMAZ():
    """Talebi yalniz 3 saatlik sablon karsilayabiliyor -> cozumsuz."""
    from cozucu.coz import coz
    kisa = {"id": "V-KISA", "ekip": "E", "bas": 9, "bit": 12, "mola_dk": 0}
    g = _sahne([{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                 "yasal": False}, KISA_KURAL], sablonlar=[kisa])
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": 9, "asgari": 1, "hedef": 1}]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu", (
        "asgarinin altindaki sablon atanmis: %r" % c.get("atamalar"))


def test_COZUCU_kisa_sablonu_NOT_olarak_soyler():
    from cozucu.coz import coz
    kisa = {"id": "V-KISA", "ekip": "E", "bas": 9, "bit": 12, "mola_dk": 0}
    g = _sahne([KISA_KURAL], sablonlar=[kisa, GUNDUZ])
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "V-KISA" in notlar, (
        "kisa sablonun kullanilmayacagi soylenmemis: %r"
        % (c.get("uygulanmayan_notlar"),))


def test_COZUCU_dorduncu_geceyi_YAZMAZ():
    """Talep 4 gece ust uste, tek kisi, yalniz gece sablonu -> cozumsuz."""
    from cozucu.coz import coz
    g = _sahne([{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                 "yasal": False}, GECE_KURAL], sablonlar=[GECE])
    g["talep"] = [{"ekip": "E", "gun": d, "saat": 23, "asgari": 1, "hedef": 1}
                  for d in range(4)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu", (
        "tek kisiye 4 gece ust uste yazilmis: %r"
        % sorted(a["gun"] for a in c.get("atamalar") or []))


def test_COZUCU_uc_geceyi_YAZABILIR():
    from cozucu.coz import coz
    g = _sahne([{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                 "yasal": False}, GECE_KURAL], sablonlar=[GECE])
    g["talep"] = [{"ekip": "E", "gun": d, "saat": 23, "asgari": 1, "hedef": 1}
                  for d in range(3)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c.get("durum")
    assert not _ih(g, c["atamalar"], "ARDISIK_GECE_LIMIT")
