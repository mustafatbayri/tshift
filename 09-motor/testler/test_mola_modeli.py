# -*- coding: utf-8 -*-
"""
MOLA MODELI -- K-32'nin kirmizi kaniti

NE KORUYORLAR
  K-32 (25 Eylul, Mustafa): molanin iki tipi var ve DORT ayri sure hesaplanir.

    yemek    : UCRETSIZ. Ucret hesabindan DA calisma suresinden DE dusulur.
               Tek blok (K-14).
    dinlenme : UCRETLI.  Ucret hesabindan dusulmez, calisma suresinden
               DUSULUR. En az 15'er dakikalik bloklara bolunebilir.

  KRITIK AYRIM: bir molanin UCRETLI olmasi, o sirada IS YAPILIYOR olmasi
  demek degildir. Ara dinlenme ucretli de olsa calisma suresinden dusulur.

    vardiya araligi  brut_saat   -- bastan sona
    calisma suresi   net_saat    -- BUTUN molalar dusuk   (yasal sayac)
    ucret hesabi     ucret_saat  -- yalniz UCRETSIZ dusuk (firma politikasi)
    gorev kapasitesi             -- molada kimse sahada sayilmaz

  YASAL ARA DINLENME: MOLA_HAKKI butun molalarin toplamina bakar; YEMEK DE
  SAYILIR. Sistem yemek arasinin uzerine otomatik bir saat EKLEMEZ.

BU DOSYA BIR KEZ YANLIS YAZILDI
  Ilk hali "yasal hakki yalniz dinlenme karsilar" ve "dinlenme ucretli oldugu
  icin calisma suresine dahildir" varsayimlarini siniyordu. Ikisi de yanlisti;
  dis inceleme yakaladi. Ayrintisi K-32'nin "Duzeltmenin kaydi" bolumunde.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_mola_modeli.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir, zaman                   # noqa: E402
from orkestra import coz_ve_onar                             # noqa: E402


# ----------------------------------------------------------------------
# Sahne
# ----------------------------------------------------------------------

def _girdi(sablon, yerlesim=None, haftalik=45):
    # Motor YALNIZ girdide aktif olan kurallari kosturur. Mola bicimi
    # kurallari (K-32) da girdiden gelir; burada hepsi aciktir.
    k = [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
          "yasal": False, "kabul_edilebilir": False},
         {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True,
          "yasal": True, "kabul_edilebilir": False},
         {"kod": "MOLA_TIPI_ZORUNLU", "tur": "SERT", "aktif": True,
          "yasal": False, "kabul_edilebilir": True},
         {"kod": "MOLA_ASGARI_BLOK", "tur": "SERT", "aktif": True,
          "yasal": False, "kabul_edilebilir": False},
         {"kod": "YEMEK_TEK_BLOK", "tur": "SERT", "aktif": True,
          "yasal": False, "kabul_edilebilir": False}]
    if yerlesim is not None:
        k.append({"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True,
                  "yasal": False, "parametreler": yerlesim})
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": haftalik},
             "izinler": [], "uygunluk": []},
        ],
        "vardiya_sablonlari": [sablon],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
                  for s in range(sablon["bas"], sablon["bit"])],
        "kurallar": k,
        "kilitler": [],
        "donmus_gunler": [],
    }


V9_18 = {"id": "V", "bas": 9, "bit": 18, "mola_dk": 60, "gunler": [0]}
V12_21 = {"id": "V", "bas": 12, "bit": 21, "mola_dk": 60, "gunler": [0]}

# K-32 ornegi: 60 dk yemek + 3x15 dk ucretli kisa mola
ORNEK_MOLALAR = [
    {"bas": 11, "bit": 11.25, "tip": "dinlenme"},
    {"bas": 12, "bit": 13, "tip": "yemek"},
    {"bas": 15, "bit": 15.25, "tip": "dinlenme"},
    {"bas": 16.5, "bit": 16.75, "tip": "dinlenme"},
]


def _atama(molalar, bas=9, bit=18):
    return {"calisan": "C1", "ekip": "E", "sablon": "V", "gun": 0,
            "bas": bas, "bit": bit, "molalar": molalar}


def _kodlar(rapor):
    return {i.get("kural") for i in rapor["ihlaller"]}


def _agirlik(rapor, kod):
    for i in rapor["ihlaller"]:
        if i.get("kural") == kod:
            return i.get("agirlik")
    return None


# ----------------------------------------------------------------------
# 1 · Dort sure ayri ayri -- K-32 kabul cumlesi 2
# ----------------------------------------------------------------------

def test_dort_sure_AYRI_hesaplanir():
    """Aritmetigin kendisi. YESIL olmali -- `ucret_saat` 25 Eylul'de eklendi.

    Kirmizi yanarsa K-32'nin cekirdegi bozulmus demektir.
    """
    a = _atama(ORNEK_MOLALAR)
    assert zaman.brut_saat(a) == 9, "vardiya araligi 9 saat olmali"
    assert zaman.net_saat(a) == 7.25, (
        "calisma suresi %.2f; 7,25 olmali -- BUTUN molalar dusulur"
        % zaman.net_saat(a))
    assert zaman.ucret_saat(a) == 8.0, (
        "ucret hesabi %.2f; 8 olmali -- yalniz UCRETSIZ mola dusulur"
        % zaman.ucret_saat(a))


def test_dort_sure_RAPORLANIR():
    """K-32: dordu de ayri ayri raporlanmali. Bugun `ucret_saat` ciktida yok.

    Tek bir "mesai suresi" toplami gostermek, firmanin ucretli molalari
    yuzunden "eksik calisti" uyarisi uretmeye yol acar.
    """
    rapor = degerlendir(_girdi(V9_18), [_atama(ORNEK_MOLALAR)])
    m = rapor["metrikler"]
    assert "ucret_saat" in m, (
        "ucret hesabina esas sure ciktida yok; tek bir toplam gosteriliyor "
        "(K-32 madde 2): %s" % sorted(m))


# ----------------------------------------------------------------------
# 2 · Yasal ara dinlenme -- YEMEK DE SAYILIR
# ----------------------------------------------------------------------

def test_yalniz_yemek_yasal_hakki_KARSILAR():
    """K-32 kabul cumlesi 7. YESIL olmali -- bugunku davranis DOGRU.

    9 saatlik vardiyada 1 saatlik ogle arasi md. 68'i karsilar. Sistem
    ustune 60 dk daha EKLEMEMELI.

    ⚠ Bu test 25 Eylul'de bir kez yanlis yazildi: "yalniz yemek verilmisse
    IHLAL yazilmali" deniyordu. Yanlisti; A08 altin senaryosunu kiriyordu ve
    A08 hakliydi. Bu haliyle bir GERILEME BEKCISI: birisi tekrar "yasal hakki
    yalniz dinlenme karsilar" derse burasi kirmizi yanar.
    """
    rapor = degerlendir(_girdi(V9_18),
                        [_atama([{"bas": 12, "bit": 13, "tip": "yemek"}])])
    assert "MOLA_HAKKI" not in _kodlar(rapor), (
        "yemek arasi md. 68'i karsilamali; sistem ustune mola ekliyor (K-32)")


def test_eksik_mola_hala_IHLAL():
    """Gerileme korumasi: kural gevsemedi. 9 saatlik vardiyada 30 dk yetmez."""
    rapor = degerlendir(_girdi(V9_18),
                        [_atama([{"bas": 12, "bit": 12.5, "tip": "yemek"}])])
    assert "MOLA_HAKKI" in _kodlar(rapor), (
        "9 saatlik vardiyada 30 dk mola verilmis, ihlal yazilmaliydi")


# ----------------------------------------------------------------------
# 3 · Tipsiz mola bildirilir -- kabul cumlesi 1
# ----------------------------------------------------------------------

def test_tipsiz_mola_BILDIRILIR():
    """Tipsiz mola `yemek` sayilir (eski davranis korunur) ama SESSIZ gecmez."""
    rapor = degerlendir(_girdi(V9_18), [_atama([{"bas": 12, "bit": 13}])])
    assert "MOLA_TIPI_ZORUNLU" in _kodlar(rapor), (
        "tipsiz mola sessizce gecti -- mola tipi diye bir kavram yok (K-32)")


# ----------------------------------------------------------------------
# 4 · Yemek penceresi GORELI -- kabul cumleleri 3, 4, 5
# ----------------------------------------------------------------------

def _yemek_baslangici(cikti):
    atamalar = cikti.get("atamalar") or []
    assert atamalar, "plan uretilmedi"
    for m in atamalar[0].get("molalar") or []:
        if m.get("tip") == "yemek":
            return m["bas"]
    raise AssertionError("planda `yemek` tipli mola yok (K-32)")


def test_sabah_vardiyasinda_yemek_3_ve_5_saat_ARASINDA():
    """K-32 kabul cumlesi 3. 09:00 basliyorsa yemek 12:00-14:00 arasi."""
    c = coz_ve_onar(_girdi(V9_18, yerlesim={"en_az_saat": 3, "en_gec_saat": 5}),
                    {"azami_saniye": 15})
    bas = _yemek_baslangici(c)
    assert 12 <= bas <= 14, (
        "yemek %s'te basladi; 09:00 vardiyasinda 12:00-14:00 bekleniyordu" % bas)


def test_OGLE_vardiyasinda_pencere_KAYAR():
    """K-32 kabul cumlesi 4 -- mutlak pencerenin patladigi yer.

    12:00-21:00 vardiyasinda yemek 15:00-17:00 arasi olmali. Eski mutlak
    model burada "12-14" diyordu: vardiyanin ilk iki saati.
    """
    c = coz_ve_onar(_girdi(V12_21, yerlesim={"en_az_saat": 3, "en_gec_saat": 5}),
                    {"azami_saniye": 15})
    bas = _yemek_baslangici(c)
    assert 15 <= bas <= 17, (
        "yemek %s'te basladi; 12:00 vardiyasinda 15:00-17:00 bekleniyordu -- "
        "pencere vardiyaya gore kaymiyor (K-32)" % bas)


def test_firma_parametresi_2_4_UYGULANIR():
    """K-32 kabul cumlesi 5."""
    c = coz_ve_onar(_girdi(V9_18, yerlesim={"en_az_saat": 2, "en_gec_saat": 4}),
                    {"azami_saniye": 15})
    bas = _yemek_baslangici(c)
    assert 11 <= bas <= 13, (
        "yemek %s'te basladi; 2/4 parametresiyle 11:00-13:00 bekleniyordu" % bas)


# ----------------------------------------------------------------------
# 5 · Yerlesim YUMUSAK -- kabul cumlesi 6
# ----------------------------------------------------------------------

def test_pencere_disi_yemek_YUMUSAK_ihlal():
    """Ihlal yazilmali ama SERT OLMAMALI. K-14'un mantigi: mola ciktisi
    oneridir; sert yapmak her gercek plani cokertir."""
    girdi = _girdi(V9_18, yerlesim={"en_az_saat": 3, "en_gec_saat": 5})
    a = _atama([{"bas": 9, "bit": 10, "tip": "yemek"}])
    rapor = degerlendir(girdi, [a])
    assert "MOLA_YERLESIMI" in _kodlar(rapor), (
        "pencere disina konmus yemek hic ihlal uretmedi (K-32)")
    assert _agirlik(rapor, "MOLA_YERLESIMI") == "YUMUSAK", (
        "MOLA_YERLESIMI %s cikti; K-14 geregi YUMUSAK olmali"
        % _agirlik(rapor, "MOLA_YERLESIMI"))


# ----------------------------------------------------------------------
# 6 · Blok kurallari -- kabul cumleleri 8, 9
# ----------------------------------------------------------------------

def test_15_dakikadan_KISA_dinlenme_SERT_ihlal():
    """K-32 kabul cumlesi 8. 10 dk'lik parcalara bolmek gecerli degil."""
    a = _atama([{"bas": 10, "bit": 10 + 1 / 6.0, "tip": "dinlenme"},
                {"bas": 12, "bit": 13, "tip": "yemek"}])
    rapor = degerlendir(_girdi(V9_18), [a])
    assert "MOLA_ASGARI_BLOK" in _kodlar(rapor), (
        "10 dakikalik dinlenme blogu sessizce gecti; en az 15 dk olmali (K-32)")


def test_bolunmus_yemek_SERT_ihlal():
    """K-32 kabul cumlesi 9 / K-14 madde 2. 30+30 yemek verilemez."""
    a = _atama([{"bas": 12, "bit": 12.5, "tip": "yemek"},
                {"bas": 15, "bit": 15.5, "tip": "yemek"}])
    rapor = degerlendir(_girdi(V9_18), [a])
    assert "YEMEK_TEK_BLOK" in _kodlar(rapor), (
        "yemek iki bloga bolunmus, ihlal yazilmadi (K-14 / K-32)")


# ----------------------------------------------------------------------
# 7 · Sozlesme saati UCRET hesabina bakar -- kabul cumlesi 10
# ----------------------------------------------------------------------

def test_sozlesme_karsilastirmasi_UCRET_saatine_bakar():
    """K-32 kabul cumlesi 10.

    Haftada 40 saatlik sozlesme. Bes gun x (9 saat brut, 1 sa yemek,
    3x15 dk ucretli dinlenme) = ucret hesabinda 40 saat, calisma suresinde
    36 saat 15 dk. Sozlesme karsilastirmasi UCRETE bakmali: eksik calisma
    uyarisi CIKMAMALI.

    Bugun `fazla_mesai_saat` net (calisma) suresine bakiyor.
    """
    atamalar = [dict(_atama(ORNEK_MOLALAR), gun=g) for g in range(5)]
    rapor = degerlendir(_girdi(V9_18, haftalik=40), atamalar)
    assert rapor["metrikler"].get("ucret_saat") == 40.0, (
        "haftalik ucret hesabi %s; 40 olmali (5 x 8 saat)"
        % rapor["metrikler"].get("ucret_saat"))


# ----------------------------------------------------------------------
# 8 · Mola politikasi -- K-32 madde 6
# ----------------------------------------------------------------------
#
# ⚠ Bu testler once YANLIS kuruldu: 9 saatlik vardiyaya 30 dk'lik politika
# verildi ve plan COZULEMEDI. Sebep dogruydu -- brut > 7,5 saat icin md. 68
# 60 dk istiyor, 30 dk'lik politika yasal tabanin altinda kaliyor ve SERT
# ihlal uretiyor. Yani motor haklyidi, test yanlisti. O davranis artik
# `test_politika_yasal_tabanin_ALTINA_inemez` ile kiliklandi.

V9_14 = {"id": "V", "bas": 9, "bit": 14, "mola_dk": 60, "gunler": [0]}


def _tek_mola(cikti):
    assert cikti.get("durum") == "cozuldu", (
        "plan cozulemedi: %s" % cikti.get("durum"))
    molalar = cikti["atamalar"][0].get("molalar") or []
    assert molalar, "planda mola yok"
    return molalar[0]["bit"] - molalar[0]["bas"]


def test_politika_yemek_suresini_BELIRLER():
    """Politika varsa yemek suresi ORADAN gelir, `mola_dk`dan degil.

    5 saatlik vardiya: md. 68 30 dk istiyor, politika da 30 dk veriyor --
    yasal taban asiliyor, `mola_dk`daki 60 gecersiz kaliyor.
    """
    girdi = _girdi(V9_14, yerlesim={"en_az_saat": 3, "en_gec_saat": 5})
    girdi["mola_politikasi"] = [
        {"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
    ]
    assert _tek_mola(coz_ve_onar(girdi, {"azami_saniye": 15})) == 0.5, (
        "politika 30 dk diyor; `mola_dk` degil politika gecerli olmali "
        "(K-32 madde 6)")


def test_sablon_politikasi_FIRMAYI_EZER():
    """K-32: firma varsayilan verir, sablon gerekirse ezer (#5.2 merdiveni).

    Gerekce: "biz 3x15 veriyoruz" sirket kararidir ama 4 saatlik cumartesi
    nobetine 1 saatlik yemek konamaz.
    """
    sablon = dict(V9_14)
    sablon["mola_politikasi"] = [
        {"tip": "yemek", "dakika": 45, "adet": 1, "ucretli": False},
    ]
    girdi = _girdi(sablon, yerlesim={"en_az_saat": 3, "en_gec_saat": 5})
    girdi["mola_politikasi"] = [
        {"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
    ]
    assert _tek_mola(coz_ve_onar(girdi, {"azami_saniye": 15})) == 0.75, (
        "sablon 45 dk diyor ve firmayi ezmeli")


def test_politika_YOKSA_eski_davranis():
    """Gerileme korumasi: politika tanimlanmamis kiracida hicbir sey degismez."""
    girdi = _girdi(V9_18, yerlesim={"en_az_saat": 3, "en_gec_saat": 5})
    assert _tek_mola(coz_ve_onar(girdi, {"azami_saniye": 15})) == 1.0, (
        "politika yokken `mola_dk` = 60 dk gecerli olmali")


def test_politika_yasal_tabanin_ALTINA_inemez():
    """Politika firma tercihidir; MOLA_HAKKI kapsami `S` ve yasaldir (K-18).

    9 saatlik vardiyaya 30 dk'lik politika verilirse md. 68 saglanmaz.
    Motor bunu SESSIZCE duzeltmez ve gecerli bir plan da uretmez --
    cozumsuzluk dogru cevaptir. Yanlis politika GORUNUR kalmali.
    """
    girdi = _girdi(V9_18, yerlesim={"en_az_saat": 3, "en_gec_saat": 5})
    girdi["mola_politikasi"] = [
        {"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
    ]
    c = coz_ve_onar(girdi, {"azami_saniye": 15})
    assert c.get("durum") != "cozuldu", (
        "yasal tabanin altinda bir politika ile gecerli plan uretildi -- "
        "politika MOLA_HAKKI'yi ezmis olur (K-18)")


# ----------------------------------------------------------------------
# 9 · Dinlenme molalarinin ESIT dagitimi -- K-32, secenek (b)
# ----------------------------------------------------------------------
#
# ⚠ Bu aritmetik YAZILDI ama cozucuye HENUZ BAGLANMADI. Asagidaki testler
# fonksiyonun kendisini siniyor; motor bugun hala tek mola (yemek) uretiyor.
# Baglanmasi icin `_sahada` yeniden kurgulanmali: "yemek kapsamiyor VE hicbir
# dinlenme kapsamiyor" bir VE bagladir ve bugunku boolean toplamiyla ifade
# edilemez. Kayit: K-32 madde 6'nin kalan isi.

from cozucu.model import _dinlenme_baslangiclari                # noqa: E402


def test_dinlenme_molalari_ESIT_dagilir():
    """9 saatlik vardiyada 3 mola vardiyanin ceyreklerine dusmeli."""
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 18}, 3, 15)
    assert [a[0] for a in r] == [11, 13, 15], (
        "molalar esit dagilmadi: %s" % r)


def test_dinlenme_penceresi_VARDIYAYA_gore_kayar():
    """Mutlak saat degil: 12:00 baslayan vardiyada da esit dagilir."""
    r = _dinlenme_baslangiclari({"bas": 12, "bit": 21}, 3, 15)
    assert [a[0] for a in r] == [14, 16, 18], (
        "pencere vardiyaya gore kaymadi: %s" % r)


def test_her_molaya_IKI_aday():
    """Cozucuye kacacak yer birakilir -- yoksa yemekle cakisinca cozumsuz kalir.

    Iki aday, ayni zamanda kisiler arasinda KAYDIRMA imkani demektir: ayni
    sablondaki herkes ayni dakikada molaya cikmasin diye.
    """
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 18}, 3, 15)
    assert all(len(a) == 2 for a in r), "her molaya iki aday olmali: %s" % r


def test_adaylar_AYRIK():
    """Iki dinlenme molasi ayni dilime dusemez -- pencereler kesismez.

    Boylece cozucude cakismama kisiti YAZMAK GEREKMIYOR; model kucuk kaliyor.
    """
    for sablon, adet in (({"bas": 9, "bit": 18}, 3), ({"bas": 9, "bit": 13}, 3),
                         ({"bas": 12, "bit": 21}, 3), ({"bas": 9, "bit": 18}, 2)):
        duz = [x for a in _dinlenme_baslangiclari(sablon, adet, 15) for x in a]
        assert len(duz) == len(set(duz)), (
            "%s adet=%d: aday pencereleri cakisiyor -> %s"
            % (sablon, adet, duz))


def test_sigmayan_mola_UYDURULMAZ():
    """4 saatlik vardiyaya 3 mola sigmaz; ucuncu icin BOS liste doner.

    Motor olmayan bir yere mola koymaz; eksikligi dogrulayici kendi tarafinda
    gorur (MOLA_HAKKI). Sessizce sigdirmak, olmayan molayi varmis gibi
    gostermek olurdu -- T-27'nin ayni sinifi.
    """
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 13}, 3, 15)
    assert r[-1] == [], "sigmayan mola icin bos liste bekleniyordu: %s" % r
