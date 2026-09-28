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


def _orta(adaylar):
    """Bir aday penceresinin ORTASI -- pencere ideal noktaya simetriktir."""
    return (adaylar[0] + adaylar[-1]) / 2.0


def test_dinlenme_molalari_ESIT_dagilir():
    """9 saatlik vardiyada 3 mola vardiyanin ceyreklerine dusmeli.

    ⚠ K-34'te bu test DEGISTI. Eski hali pencerenin ILK adayina bakip
    `[11, 13, 15]` bekliyordu -- yani saat izgarasinin YUVARLADIGI degerlere.
    Gercek ideal noktalar 11.25, 13.50, 15.75'tir ve ceyrek izgarada TAM
    ISABET ederler. Eski test, yuvarlama hatasini "dogru cevap" sayiyordu.

    Artik pencerenin ORTASINA bakiliyor, cunku esit dagitimi tasiyan sey
    pencerenin merkezidir, ilk elemani degil.
    """
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 18}, 3, 15)
    assert [_orta(a) for a in r] == [11.25, 13.5, 15.75], (
        "molalar esit dagilmadi: %s" % r)


def test_dinlenme_penceresi_VARDIYAYA_gore_kayar():
    """Mutlak saat degil: 12:00 baslayan vardiyada da esit dagilir."""
    r = _dinlenme_baslangiclari({"bas": 12, "bit": 21}, 3, 15)
    assert [_orta(a) for a in r] == [14.25, 16.5, 18.75], (
        "pencere vardiyaya gore kaymadi: %s" % r)


def test_her_molaya_BIRDEN_COK_aday():
    """Cozucuye kacacak yer birakilir -- yoksa yemekle cakisinca cozumsuz kalir.

    Birden cok aday, ayni zamanda kisiler arasinda KAYDIRMA imkani demektir:
    ayni sablondaki herkes ayni dakikada molaya cikmasin diye.

    ⚠ K-34'te bu test DEGISTI. Eski hali "tam iki aday" diyordu; iki aday
    saat izgarasinin ZORLADIGI bir sayiydi (daha fazlasi modeli sisirirdi).
    Ceyrek izgarada ayni sureye dort kat aday sigiyor ve T-44'un olctugu
    darlik da boylece kalkiyor. Test artik SAYIYI degil, sayinin VARLIK
    SEBEBINI koruyor: birden cok secenek olacak.
    """
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 18}, 3, 15)
    assert all(len(a) >= 2 for a in r), (
        "her molaya birden cok aday olmali: %s" % r)


def test_adaylar_AYRIK():
    """Iki dinlenme molasi ayni dilime dusemez -- pencereler kesismez.

    Boylece cozucude cakismama kisiti YAZMAK GEREKMIYOR; model kucuk kaliyor.

    ⚠ BU SUSLEME DEGIL, `_sahada` ARITMETIGININ KOSULU. Iki mola ayni dilimi
    kapsarsa oradaki dogrusal toplam eksiye duser ve kapsama sessizce yanlis
    hesaplanir.

    28 Eylul: K-34'un ILK yazimi bu testi kirmizi yakti -- pencereler uc
    noktada degiyordu (4 saatlik vardiyada 10.5 iki pencerede birden).
    Sebep: yaricap hesabina MOLA SURESI katilmamisti. Test dogru zamanda
    bagirdi; kayit `_dinlenme_baslangiclari` icinde.

    Artik yalniz aday kumeleri degil, MOLALARIN KAPSADIGI dilimler de
    sinaniyor -- 30 dk'lik molada ayrik adaylar yetmez.
    """
    for sablon, adet, dk in (({"bas": 9, "bit": 18}, 3, 15),
                             ({"bas": 9, "bit": 13}, 3, 15),
                             ({"bas": 12, "bit": 21}, 3, 15),
                             ({"bas": 9, "bit": 18}, 2, 15),
                             ({"bas": 9, "bit": 18}, 3, 30),
                             ({"bas": 9, "bit": 18}, 2, 60)):
        r = _dinlenme_baslangiclari(sablon, adet, dk)
        duz = [x for a in r for x in a]
        assert len(duz) == len(set(duz)), (
            "%s adet=%d %ddk: aday pencereleri cakisiyor -> %s"
            % (sablon, adet, dk, duz))
        # En kotu durum: her mola kendi penceresinin EN GEC adayina konsun.
        # O zaman bile bir sonraki molanin EN ERKEN adayini kapatmamali.
        for i in range(len(r) - 1):
            if not r[i] or not r[i + 1]:
                continue
            biter = r[i][-1] + dk / 60.0
            assert biter <= r[i + 1][0] + 1e-9, (
                "%s adet=%d %ddk: %d. mola en gec %.2f'de bitiyor ama "
                "%d. mola %.2f'de baslayabiliyor -- ust uste binerler"
                % (sablon, adet, dk, i, biter, i + 1, r[i + 1][0]))


def test_sigmayan_mola_UYDURULMAZ():
    """Vardiyaya sigmayan mola icin BOS liste doner -- uydurulmaz.

    Motor olmayan bir yere mola koymaz; eksikligi dogrulayici kendi tarafinda
    gorur (MOLA_HAKKI). Sessizce sigdirmak, olmayan molayi varmis gibi
    gostermek olurdu -- T-27'nin ayni sinifi.

    ⚠ K-34'te bu testin SAHNESI degisti, ilkesi degismedi. Eski sahne
    "4 saatlik vardiyaya 3x15 dk sigmaz" diyordu; bu DOGRU DEGILDI -- 45
    dakika 4 saate elbette sigar. Sigmiyor gorunmesinin sebebi her molanin
    bir TAM SAAT tutmasiydi, yani saat izgarasinin kendi kusuru. Eski test
    o kusuru kural sanip sabitlemisti.

    Yeni sahne gercekten sigmayani kullanir: 2 saatlik vardiyaya 3x60 dk.
    """
    r = _dinlenme_baslangiclari({"bas": 9, "bit": 11}, 3, 60)
    assert any(a == [] for a in r), (
        "gercekten sigmayan mola icin bos liste bekleniyordu: %s" % r)
    # Eski sahne artik COZULEBILIR olmali -- bu da K-34'un kazanci.
    r2 = _dinlenme_baslangiclari({"bas": 9, "bit": 13}, 3, 15)
    assert all(a for a in r2), (
        "4 saatlik vardiyaya 3x15 dk sigmaliydi: %s" % r2)


# ----------------------------------------------------------------------
# 10 · Cozucu politikayi UYGULUYOR -- K-32 madde 6'nin kalan isi
# ----------------------------------------------------------------------
#
# 28 Eylul: dinlenme molalari cozucuye baglandi. `_sahada` yeniden kuruldu --
# "sahada olmak" artik (kapsamayan yemek secenekleri) - (kapsayan dinlenmeler)
# olarak DOGRUSAL yaziliyor. Yardimci degisken yok; sarti molalarin
# birbirini kesmemesi.

def _cok_kisili(politika, adet=3):
    g = {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, adet + 1)
        ],
        "vardiya_sablonlari": [dict(V9_18)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 3}
                  for s in range(9, 18)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True,
             "yasal": True, "kabul_edilebilir": False},
            {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True,
             "yasal": False},
            {"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True,
             "yasal": False,
             "parametreler": {"en_az_saat": 3, "en_gec_saat": 5}},
        ],
        "kilitler": [], "donmus_gunler": [],
        "mola_politikasi": politika,
    }
    return coz_ve_onar(g, {"azami_saniye": 20})


POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]


def test_cozucu_politikadaki_MOLALARI_uretir():
    """Politika 1 yemek + 3 dinlenme diyorsa plan da oyle olmali."""
    c = _cok_kisili(POLITIKA)
    assert c["durum"] == "cozuldu", c.get("durum")
    for a in c["atamalar"]:
        tipler = [m["tip"] for m in a["molalar"]]
        assert tipler.count("yemek") == 1, (
            "%s: %d yemek molasi (1 bekleniyordu) -- %s"
            % (a["calisan"], tipler.count("yemek"), a["molalar"]))
        assert tipler.count("dinlenme") == 3, (
            "%s: %d dinlenme molasi (3 bekleniyordu) -- %s"
            % (a["calisan"], tipler.count("dinlenme"), a["molalar"]))


def test_molalar_BIRBIRINI_kesmez():
    """`_sahada`'nin dogrusal aritmetigi buna DAYANIYOR.

    Iki mola ayni dilimi kapsarsa "sahada" ifadesi eksiye duser ve kapsama
    hesabi sessizce bozulur. Bu test o varsayimin bekcisidir.
    """
    c = _cok_kisili(POLITIKA)
    for a in c["atamalar"]:
        araliklar = sorted((m["bas"], m["bit"]) for m in a["molalar"])
        for (b1, s1), (b2, s2) in zip(araliklar, araliklar[1:]):
            assert s1 <= b2, (
                "%s: %s ile %s molalari cakisiyor"
                % (a["calisan"], (b1, s1), (b2, s2)))


def test_dort_sure_GERCEK_planda_dogru():
    """K-32'nin ornegi, uretilmis bir plan uzerinde.

    9 saat vardiya · 1 sa yemek + 3x15 dk dinlenme
      -> calisma 7 sa 15 dk · ucret 8 saat
    """
    c = _cok_kisili(POLITIKA)
    a = c["atamalar"][0]
    assert zaman.brut_saat(a) == 9
    assert zaman.net_saat(a) == 7.25, (
        "calisma suresi %.2f; 7,25 bekleniyordu" % zaman.net_saat(a))
    assert zaman.ucret_saat(a) == 8.0, (
        "ucret hesabi %.2f; 8 bekleniyordu" % zaman.ucret_saat(a))


def test_yemekler_KISILER_ARASINDA_kaydirilir():
    """Adil plan: ayni sablondaki herkes ayni dakikada molaya cikmasin.

    Molalar sabit yerlestirilseydi ucu de ayni saatte molada olurdu ve
    kapsama coker. Karar degiskeni olmalarinin sebebi bu.
    """
    c = _cok_kisili(POLITIKA)
    yemekler = [m["bas"] for a in c["atamalar"]
                for m in a["molalar"] if m["tip"] == "yemek"]
    assert len(set(yemekler)) > 1, (
        "butun yemek molalari ayni saatte: %s -- cozucu kaydirmiyor" % yemekler)


def test_politika_YOKSA_dinlenme_URETILMEZ():
    """Gerileme korumasi: politika tanimlanmamis kiracida davranis degismez."""
    c = _cok_kisili([{"tip": "yemek", "dakika": 60, "adet": 1,
                      "ucretli": False}])
    for a in c["atamalar"]:
        assert all(m["tip"] == "yemek" for m in a["molalar"]), (
            "politikada dinlenme yokken uretildi: %s" % a["molalar"])


# ----------------------------------------------------------------------
# 11 · SAHADA_ASGARI -- her saatte sahada bulunmasi gereken kisi (K-33)
# ----------------------------------------------------------------------
#
# 28 Eylul, Mustafa: "Gercekte mesaide kalmasi gereken bir kisi sayisi tanimi
# gerekecek. Yani biz saat basi kafamiza gore kisileri yollayamayiz."
#
# OLCULEN DURUM (ayni gun, uc kisilik plan, asgari 2):
#     saat 12 -> sahada 0     saat 13 -> sahada 0
#     sert ihlal 0, yayinlanabilir True
# Ucu de ayni anda molada ve plan temiz gorunuyordu.
#
# SEBEP KOD DEGIL, K-14: MOLA_KAPSAMASI bilerek YUMUSAK. O karar kisi basina
# TEK ogle arasi varken verildi; motor artik kisi basina DORT mola uretiyor ve
# ayni dissiz kural tabani tamamen bosaltiyor.
#
# COZUM (b): MOLA_KAPSAMASI yumusak KALIR (K-14 ayakta, plani asgariye dogru
# iter); yanina SERT bir taban gelir. Ikisi ayri isi yapar.
#
# ⚠ BU BOLUM BIR KEZ YANLIS YAZILDI (28 Eylul, Mustafa yakaladi)
#   Ilk hali tabani `min(parametre, hucrenin asgarisi)` ile siniriyordu ve
#   `test_taban_hucre_ASGARISINI_asamaz` bunu TEST OLARAK SABITLIYORDU --
#   yani hatayi kalici hale getiren sey testin kendisiydi.
#
#   Mustafa: "Firma molada en az 5 demeyecek, firma sahada en az 5 diyecek,
#   yanlis mantik kurma lutfen."
#
#   Parametre bir mola kotasi degil SAHA TABANIDIR ve talep tablosuyla
#   sinirlanmaz. O test silinmedi, TERSINE CEVRILDI: artik tabanin talep
#   tablosuna BOYUN EGMEDIGINI koruyor (test_taban_TALEBE_boyun_egmez).
#
# EKIP BUYUKLUKLERI NEDEN 8/12 (3 degil)
#   28 Eylul olcumu: bugunku mola geometrisinde plan ancak N >= 4F iken
#   cozulur (15 senaryo, 15/15 tuttu). Taban 2 -> en az 8 kisi. Sahneler
#   bu yuzden buyuk; kucuk ekip "cozumsuz" doner ve bu bir KOD hatasi
#   degil, olculmus bir sinirdir -- bkz. test_bugunku_GEOMETRI_SINIRI.

def _taban_sahnesi(taban, kisi=8, asgari=2):
    g = {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [dict(V9_18)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": asgari,
                   "hedef": kisi} for s in range(9, 18)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True,
             "yasal": True, "kabul_edilebilir": False},
            {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True,
             "yasal": False},
            {"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True,
             "yasal": False,
             "parametreler": {"en_az_saat": 3, "en_gec_saat": 5}},
        ],
        "kilitler": [], "donmus_gunler": [],
        "mola_politikasi": POLITIKA,
    }
    if taban is not None:
        g["kurallar"].append(
            {"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False,
             "parametreler": {"asgari_sahada": taban}})
    return g


def _sahada_sayilari(atamalar):
    return {s: sum(1 for a in atamalar if zaman.sahada_mi(a, 0, s))
            for s in range(9, 18)}


def test_taban_YOKSA_saha_bosalabiliyor():
    """Bugunku durumun kaydi -- kural yokken hicbir sey engellemiyor.

    Bu test YESIL kalmali: taban tanimlanmamis kiracida davranis degismez.
    Kotu bir davranisi degil, GERI DONUK UYUMU sabitliyor.
    """
    g = _taban_sahnesi(None)
    c = coz_ve_onar(g, {"azami_saniye": 20})
    assert c["durum"] == "cozuldu"
    rapor = degerlendir(g, c["atamalar"])
    assert "SAHADA_ASGARI" not in {i["kural"] for i in rapor["ihlaller"]}, (
        "kural tanimli degilken ihlal yazildi")


def test_taban_delinirse_SERT_ihlal():
    """Dogrulayici tarafi: molada taban altina inen plan sert ihlal yazar."""
    g = _taban_sahnesi(2)
    # Ucu de 12:00-13:00 arasinda yemekte -- sahada sifir
    atamalar = [{"calisan": "C%d" % i, "ekip": "E", "sablon": "V", "gun": 0,
                 "bas": 9, "bit": 18,
                 "molalar": [{"bas": 12, "bit": 13, "tip": "yemek"}]}
                for i in (1, 2, 3)]
    rapor = degerlendir(g, atamalar)
    kodlar = {i["kural"] for i in rapor["ihlaller"]}
    assert "SAHADA_ASGARI" in kodlar, (
        "ucu de ayni anda molada, sahada sifir kisi -- sert ihlal yazilmadi")
    agirlik = next(i["agirlik"] for i in rapor["ihlaller"]
                   if i["kural"] == "SAHADA_ASGARI")
    assert agirlik == "SERT", "taban ihlali SERT olmali, %s geldi" % agirlik


def test_cozucu_TABANI_korur():
    """Cozucu tarafi: taban verilince plan onu delmez.

    Ayni sahne, ayni politika -- tek fark tabanin tanimli olmasi.
    """
    g = _taban_sahnesi(2)
    c = coz_ve_onar(g, {"azami_saniye": 30})
    assert c["durum"] == "cozuldu", (
        "taban verilince plan uretilemedi: %s" % c.get("durum"))
    sayilar = _sahada_sayilari(c["atamalar"])
    kotu = {s: n for s, n in sayilar.items() if n < 2}
    assert not kotu, (
        "taban 2 iken sahada eksik kalan saatler: %s (butun saatler: %s)"
        % (kotu, sayilar))


def test_taban_TALEBE_boyun_egmez():
    """Taban talep tablosunun `asgari`si ile SINIRLANMAZ (28 Eylul duzeltmesi).

    Bu testin eski hali TAM TERSINI koruyordu: firma 5 dese de hucre 2
    istiyorsa taban 2 olsun diyordu. Mustafa yakaladi -- firma "molada en az
    5" demiyor, "SAHADA en az 5" diyor; bu bir mola kotasi degil saha
    tabani ve talep tablosu onu asagi cekemez.

    SAHNE: hucre 3 kisi istiyor, firma sahada 4 kisi istiyor. Ikisi de SERT,
    kati olan baglar -> her saatte en az 4 kisi SAHADA olmali. Eski mantik
    burada 3'e razi olurdu ve firmanin cumlesi buharlasirdi.
    """
    g = _taban_sahnesi(4, kisi=16, asgari=3)
    c = coz_ve_onar(g, {"azami_saniye": 45})
    assert c["durum"] == "cozuldu", (
        "taban 4 / hucre asgarisi 3 senaryosu cozulemedi: %s" % c.get("durum"))
    sayilar = _sahada_sayilari(c["atamalar"])
    kotu = {s: n for s, n in sayilar.items() if n < 4}
    assert not kotu, (
        "taban 4 iken sahada 4'un altina dusen saatler: %s -- eski min(...) "
        "mantigi geri gelmis olabilir (butun saatler: %s)" % (kotu, sayilar))


def test_taban_talep_ASGARISININ_USTUNDE_atama_zorlar():
    """Taban hucrenin asgarisinden buyukse ATAMAYI yukari ceker -- kasitli.

    Talep tablosu isin gerektirdigini soyler (3), firma tezgahta gormek
    istedigini (4). Motor birini otekine tercih etmez: sahada 4 kisi olmasi
    icin en az 4 kisi ATANMAK zorundadir. Yani taban, ASGARI_KAPSAMA'nin
    sayisini fiilen yukari tasir.
    """
    g = _taban_sahnesi(4, kisi=16, asgari=3)
    c = coz_ve_onar(g, {"azami_saniye": 45})
    assert c["durum"] == "cozuldu"
    atanan = {s: sum(1 for a in c["atamalar"] if zaman.atanmis_mi(a, 0, s))
              for s in range(9, 18)}
    kotu = {s: n for s, n in atanan.items() if n < 4}
    assert not kotu, (
        "taban 4 iken 4'ten az kisi ATANMIS saatler: %s (hepsi: %s)"
        % (kotu, atanan))


def test_GEOMETRI_SINIRI():
    """OLCULMUS SINIR: plan ancak `N >= 12F/7` (~1.71xF) iken cozulur.

    Bu bir dogruluk testi DEGIL, bir SINIR KAYDIDIR. Kirmizi olmasi "kod
    bozuldu" demek degil; "sinir degisti, kaydi guncelle" demektir.

    ⚠ SINIR BIR KEZ DEGISTI (28 Eylul, K-34)
      Eski kayit `N >= 4F` idi ve iki sebebi vardi: saat yuvarlamasi ile
      aday pencerelerinin darligi. K-34 zaman izgarasini CEYREK SAATE
      indirince ikisi birden kalkti:

          taban 2 ->  8 kisi  yerine  4 kisi
          taban 3 -> 12 kisi  yerine  6 kisi
          taban 5 -> 20 kisi  yerine  9 kisi

    KALAN SINIR NEREDEN GELIYOR (olculdu, tahmin edilmedi)
      5 kisi / taban 3 senaryosunda kisitlar TEK TEK gevsetildi:

          oldugu gibi                     -> cozumsuz
          MOLA_HAKKI kapali               -> cozumsuz   (yasal hak degil)
          yemek YOK, yalniz 3x15 dinlenme -> cozumsuz   (dinlenme tek basina degil)
          dinlenme YOK, yalniz yemek      -> COZULDU
          yemek 60 -> 30 dk               -> COZULDU

      Yani bagli olan sey YEMEK ile DINLENME #1'in AYNI dilimler icin
      yarismasi. Yemek 4 ceyrek kaplar ve penceresi vardiyanin ortasindadir;
      ortadaki dinlenme molasi da orada. {12:00..15:00} araligindaki 12
      ceyrekte:

          4N (yemek) + N (dinlenme#1)  <=  12(N - F)   ->   N >= 12F/7

      Cozucuye karsi sinandi: 15 senaryo, 15/15.

    ⚠ BU BIR MODELLEME HATASI DEGIL
      Gercek bir planlama gerilimi: insanlar ogle yemegini gunun ortasinda
      ister, ortadaki dinlenme molasi da oradadir. Yemek penceresini
      genisletmek esigi DEGISTIRMEDI (olculdu: 3-5, 3-6 ve 2-7 saat
      pencerelerinin ucu de taban 3 icin 6 kisi verdi).
    """
    import math
    cozulen, cozulmeyen = [], []
    for F in (2, 3, 5):
        esik = int(math.ceil(12 * F / 7.0))
        for N in (esik - 1, esik):
            g = _taban_sahnesi(F, kisi=N, asgari=F)
            c = coz_ve_onar(g, {"azami_saniye": 30})
            (cozulen if c["durum"] == "cozuldu" else cozulmeyen).append((N, F))
    assert cozulen == [(4, 2), (6, 3), (9, 5)], (
        "N >= 12F/7 olan senaryolar cozulmedi: gelen %s" % cozulen)
    assert cozulmeyen == [(3, 2), (5, 3), (8, 5)], (
        "N < 12F/7 olan senaryolar cozuldu -- SINIR DEGISMIS olabilir (iyi "
        "haber olabilir!): gelen %s" % cozulmeyen)
