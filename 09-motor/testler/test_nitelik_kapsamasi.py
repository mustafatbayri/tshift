# -*- coding: utf-8 -*-
"""
ROL_KAPSAMASI ve YETKINLIK_KAPSAMASI -- DOGRULAYICI TARAFI

⚠ NEDEN BU DOSYA VAR (30 Eylul, Mustafa'nin secimi)
  Bu iki kural COZUCUDE vardi, DOGRULAYICIDA yoktu. Sonucu sudur:

      cozucu kisiti kendi kuruyor  ->  plan zorunlu olarak uyuyor
      dogrulayici govdesi yok     ->  "ihlal yok" diyor, HIC BAKMADAN

  Yani motor kendi isini kendi onayliyordu. Sartname #7.6 ve #16.1 iki
  yariyi tam olarak bunu engellemek icin ayiriyor. Bir kuralin yalniz
  uretici tarafta olmasi, o kural icin bagimsiz denetimin HIC OLMAMASI
  demektir -- ve bunu kimse kirmizi goremez.

  Tam olcekli kosumda (29 Eylul) "0 sert ihlal, yayinlanabilir True"
  yaziyordu. Dogru ama eksik: denetci bu iki kurala bakmadi.

SARTNAMEDEN OKUNARAK YAZILDI -- COZUCU KODUNDAN DEGIL
  #6.4 katalogu:
    ROL_KAPSAMASI       "Belirli operasyonel rolun her acik saatte
                         SAHADA bulunmasi"
    YETKINLIK_KAPSAMASI "Belirli saatlerde belirli yetkinligin SAHADA
                         olmasi"
  Iki kelime belirleyici:
    SAHADA      -> molada olan sayilmaz (SAHADA_ASGARI ile ayni olcu)
    ACIK SAAT   -> talep hucresi olan saat (kapali donemde saha yoktur)

  Cozucu kodu bilerek okunmadi. T-19'un dersi: iki taraf ayni yanlis
  gelenegi paylasirsa ikisi birbiriyle tutarli ve ikisi de yanlis olur.

KIRMIZI KANIT KAYDI -- VE BIR UYARI
  Govde yazilmadan once 12 testin 9'u kirmizi yandi. Uc tanesi YANMADI ve
  bu bilerek yaziliyor: "ihlal yok" diyen testler, kural HIC YOKKEN de
  yesil yanar. Yani o uc test govde yazilmadan once HICBIR SEY olcmuyordu.

    kirmizi yanan  ->  govde var mi (2) · ihlal yaziliyor mu (5) ·
                       ceyrek hassasiyeti · K-24 bayragi · eksik parametre
    yanmayan       ->  "sahadaysa ihlal yok" (2) · uctan uca

  ⚠ AYNI GUN IKI TEST TERSINE CEVRILDI -- K-41. Mola artik bu iki kuralda
    sahadan cikarmiyor; gerekcesi ilgili testlerin basinda yazili.

  Bu oturumda ayni tuzaga iki kez dusuldu (`assert True` ile biten testler).
  Ucu de govde yazildiktan SONRA anlam kazaniyor: fazla ihlal yazilmasini
  engelliyorlar. Ama kirmizi kanit sayisi 12 degil 9'dur.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_nitelik_kapsamasi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                             # noqa: E402

SABLON = {"id": "V1", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60}
SABLON_F = {"id": "VF", "ekip": "F", "bas": 8, "bit": 16, "mola_dk": 60}


def _c(kimlik, rol=None, yetkinlikler=None, ekipler=("E",)):
    return {"id": kimlik, "ekipler": list(ekipler),
            "operasyonel_rol": rol, "yetkinlikler": list(yetkinlikler or []),
            "sozlesme": {"tip": "tam_zamanli"}, "izinler": [], "uygunluk": []}


LIDER = _c("C1", rol="takim_lideri", yetkinlikler=["ing"])
UZMAN = _c("C2", rol="uzman")


def _atama(kimlik, ekip="E", sablon="V1", molalar=None):
    return {"calisan": kimlik, "ekip": ekip, "sablon": sablon, "gun": 0,
            "bas": 8, "bit": 16, "molalar": molalar or []}


def _sahne(kural_listesi, calisanlar=None, talep=None, sablonlar=None):
    return {
        "profil": "DENGELI",
        "calisanlar": list(calisanlar if calisanlar is not None
                           else [LIDER, UZMAN]),
        "vardiya_sablonlari": list(sablonlar or [SABLON]),
        "talep": list(talep if talep is not None else
                      [{"ekip": "E", "gun": 0, "saat": s,
                        "asgari": 1, "hedef": 1} for s in range(8, 16)]),
        "kurallar": list(kural_listesi),
        "kilitler": [], "donmus_gunler": [],
    }


def _rol(parametreler, yasal=False, kabul=True):
    return {"kod": "ROL_KAPSAMASI", "tur": "SERT", "aktif": True,
            "yasal": yasal, "kabul_edilebilir": (False if yasal else kabul),
            "parametreler": parametreler}


def _yetkinlik(parametreler, yasal=False, kabul=True):
    return {"kod": "YETKINLIK_KAPSAMASI", "tur": "SERT", "aktif": True,
            "yasal": yasal, "kabul_edilebilir": (False if yasal else kabul),
            "parametreler": parametreler}


def _ihlaller(sonuc, kod):
    return [i for i in sonuc["ihlaller"] if i["kural"] == kod]


# ----------------------------------------------------------------------
# 1. Kural artik SESSIZ GECMIYOR
# ----------------------------------------------------------------------

def test_ROL_govdesi_ARTIK_VAR():
    """En temel iddia: kural `uygulanmayan_kurallar`da GORUNMEMELI.

    Bu test kirmiziyken motor bu kurali hic denetlemiyordu -- ve bunu
    yalniz bu kanaldan soyluyordu, kimse de bakmiyordu.
    """
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})])
    r = degerlendir(g, [_atama("C1")])
    assert "ROL_KAPSAMASI" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


def test_YETKINLIK_govdesi_ARTIK_VAR():
    g = _sahne([_yetkinlik({"yetkinlik": "ing", "ekip": "E",
                            "saatler": [9]})])
    r = degerlendir(g, [_atama("C1")])
    assert "YETKINLIK_KAPSAMASI" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


# ----------------------------------------------------------------------
# 2. Rol yoksa ihlal, varsa ihlal yok
# ----------------------------------------------------------------------

def test_ROL_hic_atanmamissa_HER_ACIK_SAAT_ihlal():
    """Yalniz uzman atanmis; takim lideri hicbir saatte sahada degil.

    ⚠ `saatler` parametresi BILEREK verilmedi. Sartname rol kuralini
      "her ACIK saatte" diye tanimliyor -- yani saat listesi yoksa kural
      butun talep saatlerine uygulanir, HICBIR saate degil.
    """
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})])
    r = degerlendir(g, [_atama("C2")])
    ih = _ihlaller(r, "ROL_KAPSAMASI")
    assert len(ih) == 8 * 4, (
        "8 acik saatin 4 ceyreginde ihlal bekleniyordu, %d cikti" % len(ih))
    assert "takim_lideri" in ih[0]["mesaj"], ih[0]["mesaj"]


def test_ROL_sahadaysa_ihlal_YOK():
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})])
    r = degerlendir(g, [_atama("C1"), _atama("C2")])
    assert not _ihlaller(r, "ROL_KAPSAMASI"), (
        "lider butun vardiya sahada, ihlal olmamali: %r"
        % [i["mesaj"] for i in _ihlaller(r, "ROL_KAPSAMASI")][:3])


# ----------------------------------------------------------------------
# 3. ⚠ ASIL AYRIM: molada olan SAHADA SAYILMAZ
# ----------------------------------------------------------------------

def test_ROL_MOLADA_olan_da_SAYILIR():
    """K-41 -- TERSINE CEVRILEN TEST (30 Eylul, Mustafa'nin karari).

    ⚠ ONCEKI HALI BUNUN TAM TERSIYDI ve dogru sebeple yesildi: sartname
      §6.4 "SAHADA" diyor, govde molayi dusuyordu, tek lider 12:00-13:00
      arasi molada oldugu icin o dort ceyrekte ihlal yaziliyordu.

      Olculdu ki cozucu ATANMIS kisiyi sayiyor -- iki taraf ayrisiyordu
      (T-61). Karar Mustafa'ya soruldu:

        "Sahada bir mudurun isi 15 dk mola suresini bekleyebilir. Bu
         'sahada olmali' kuralini bozmaz. Molalar sahada sayilir olarak
         gecebilir."

      Degisen taraf DOGRULAYICI oldu, cozucu hakliydi. Bu, K-33'te yapilanin
      aynisi: kararla celisen test silinmedi, TERSINE cevrildi ve gerekcesi
      yanina yazildi -- yoksa alti ay sonra "acaba neden boyle?" diye
      sorulacak ve kimse bilemeyecek.

    ⚠ AYRIM DURUYOR: `SAHADA_ASGARI` molayi DUSMEYE devam ediyor (K-33).
      Ikisi farkli soru soruyor ve bu celiski degil.
    """
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})])
    atamalar = [_atama("C1", molalar=[{"tip": "yemek", "bas": 12, "bit": 13,
                                       "ucretli": False}]),
                _atama("C2")]
    ih = _ihlaller(degerlendir(g, atamalar), "ROL_KAPSAMASI")
    assert not ih, (
        "mola artik sahadan cikarmiyor (K-41) ama %d ihlal yazilmis: %r"
        % (len(ih), [i.get("saat") for i in ih]))


def test_CEYREK_orneklemesi_VARDIYA_SINIRINDA_gerekli():
    """Mola dusulmuyor, ama vardiya sinirlari CEYREKLI olabiliyor (K-34).

    ⚠ NEDEN BU TEST VAR
      K-41 molayi devre disi birakinca "saat icinde ne degisir ki" sorusu
      akla geliyor ve ceyrek ornekleme gereksiz gorunuyor. Gereksiz degil:
      K-34'ten beri vardiya 15:30'da bitebiliyor. 12:30'da biten tek lider
      saat 12'nin ilk iki ceyregini kapatir, son ikisini KAPATMAZ.

      Yalniz tam saate bakan bir govde bunu goremez -- ve o boyle bir
      govdeyi mutasyonla sinadik: 12:00'de lider "var" gorunuyor.
    """
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})],
               talep=[{"ekip": "E", "gun": 0, "saat": s, "asgari": 1,
                       "hedef": 1} for s in (11, 12)])
    erken_biten = dict(_atama("C1"))
    erken_biten["bit"] = 12.5
    ih = _ihlaller(degerlendir(g, [erken_biten, _atama("C2")]),
                   "ROL_KAPSAMASI")
    assert {i["saat"] for i in ih} == {12.5, 12.75}, (
        "12:30'da biten vardiya saat 12'nin son iki ceyregini kapatmiyor; "
        "beklenen iki ihlal, gelen: %r" % sorted(i["saat"] for i in ih))


# ----------------------------------------------------------------------
# 4. Saat listesi verilirse YALNIZ o saatler
# ----------------------------------------------------------------------

def test_YETKINLIK_yalniz_LISTEDEKI_saatler_denetlenir():
    """"Kahvaltida barista" -- kural gun boyu degil, o saatlerde gecerli."""
    g = _sahne([_yetkinlik({"yetkinlik": "ing", "ekip": "E",
                            "saatler": [9, 10]})])
    ih = _ihlaller(degerlendir(g, [_atama("C2")]), "YETKINLIK_KAPSAMASI")
    assert len(ih) == 2 * 4, (
        "iki saatin dort ceyregi = 8 ihlal bekleniyordu, %d cikti" % len(ih))
    assert {int(i["saat"]) for i in ih} == {9, 10}, (
        "listede olmayan saat denetlenmis: %r" % sorted(i["saat"] for i in ih))


def test_YETKINLIK_sahadaysa_ihlal_YOK():
    g = _sahne([_yetkinlik({"yetkinlik": "ing", "ekip": "E",
                            "saatler": [9, 10]})])
    r = degerlendir(g, [_atama("C1")])
    assert not _ihlaller(r, "YETKINLIK_KAPSAMASI")


def test_YETKINLIK_asgari_IKIYSE_bir_kisi_yetmez():
    """Asgari sayi parametreden gelir; varsayilan 1, ama 2 de yazilabilir."""
    g = _sahne([_yetkinlik({"yetkinlik": "ing", "ekip": "E",
                            "saatler": [9], "asgari": 2})],
               calisanlar=[LIDER, UZMAN])
    ih = _ihlaller(degerlendir(g, [_atama("C1"), _atama("C2")]),
                   "YETKINLIK_KAPSAMASI")
    assert len(ih) == 4, "asgari 2 iken tek kisi yetmemeli, %d ihlal" % len(ih)
    assert ih[0]["olculen"] == 1 and ih[0]["gereken"] == 2, ih[0]


# ----------------------------------------------------------------------
# 5. K-24 -- bayrak SATIRIN ozelligi, kuralin degil
# ----------------------------------------------------------------------

def test_K24_her_satir_KENDI_yasal_bayragini_tasir():
    """⚠ Sartname #5.3: bu iki kuralda `yasal` SATIR bazlidir.

    "Her vardiyada 1 ilk yardim sertifikali kisi" muhtemelen yasaldir;
    "kahvaltida 1 barista" ticari tercihtir. Ikisi ayni kural kodunu
    kullanir ama yayin kapisinda ayni cevabi ALMAMALIDIR: yasal olan
    kabul edilemez (#5.3: yasal ise kabul_edilebilir her zaman false).
    """
    g = _sahne([
        _yetkinlik({"yetkinlik": "ilk_yardim", "ekip": "E", "saatler": [9]},
                   yasal=True),
        _yetkinlik({"yetkinlik": "barista", "ekip": "E", "saatler": [10]},
                   yasal=False),
    ])
    ih = _ihlaller(degerlendir(g, [_atama("C1")]), "YETKINLIK_KAPSAMASI")
    yasal = {int(i["saat"]) for i in ih if i["yasal"]}
    ticari = {int(i["saat"]) for i in ih if not i["yasal"]}
    assert yasal == {9}, "yasal satirin ihlali 9'da olmali: %r" % sorted(yasal)
    assert ticari == {10}, "ticari satir 10'da olmali: %r" % sorted(ticari)
    for i in ih:
        if i["yasal"]:
            assert i["kabul_edilebilir"] is False, (
                "yasal ihlal kabul edilebilir gorunuyor: %r" % i)


# ----------------------------------------------------------------------
# 6. Ekip kapsami
# ----------------------------------------------------------------------

def test_EKIP_verilmisse_baska_ekibin_lideri_SAYILMAZ():
    """E ekibinin lideri isteniyor; F ekibinde lider olmasi yetmez."""
    f_lider = _c("C3", rol="takim_lideri", ekipler=["F"])
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})],
               calisanlar=[UZMAN, f_lider],
               sablonlar=[SABLON, SABLON_F])
    ih = _ihlaller(degerlendir(g, [_atama("C2"),
                                   _atama("C3", ekip="F", sablon="VF")]),
                   "ROL_KAPSAMASI")
    assert len(ih) == 8 * 4, (
        "F ekibinin lideri E'nin acigini kapatmamali, %d ihlal" % len(ih))


def test_EKIP_KADROSUNDA_olmayan_kisi_o_ekibin_rolunu_KARSILAMAZ():
    """⚠ MUTASYONLA BULUNDU (30 Eylul) -- ilk turda bu test YOKTU.

    Ekip suzgeci iki yerde uygulaniyor: niteligi tasiyanlar secilirken
    (kadroda mi) ve atamalar suzulurken (atama o ekibe mi). Mutasyon
    birincisini tamamen kaldirdi ve BUTUN testler yesil kaldi -- cunku
    her sahnede ikinci suzgec zaten yetiyordu.

    Fark ancak su veride ortaya cikiyor: kisi E kadrosunda DEGIL ama
    E'ye atanmis (veri hatasi ya da baska bir kuralin ihlali). O kisi
    E'nin takim lideri gerekliligini KARSILAMAZ -- orada olmamasi
    gerekiyor. Iki kural ayni bozuk veri uzerinde ayri ayri konusur:
    `EKIP_KAPSAMI` yanlis atamayi, bu kural kapanmayan acigi soyler.
    """
    yabanci = _c("C4", rol="takim_lideri", ekipler=["F"])
    g = _sahne([_rol({"rol": "takim_lideri", "ekip": "E"})],
               calisanlar=[UZMAN, yabanci])
    ih = _ihlaller(degerlendir(g, [_atama("C2"), _atama("C4")]),
                   "ROL_KAPSAMASI")
    assert len(ih) == 8 * 4, (
        "E kadrosunda olmayan kisi E'nin rolunu karsilamis gibi sayilmis, "
        "%d ihlal" % len(ih))


# ----------------------------------------------------------------------
# 7. Parametresiz satir SESSIZ GECMEZ
# ----------------------------------------------------------------------

def test_PARAMETRESIZ_satir_sessiz_GECMEZ():
    """⚠ Hangi rol istendigi yazilmamissa kural denetlenemez.

    Denetlenemedigini SOYLEMEK zorunda: "ihlal yok" ile "bakamadim" ayni
    sey degil (denetle.py'nin ilkesi). Kanal `eksik_boyutlar` -- kuralin
    kendisi yazili ama bir parcasi eksik.

    Bu, kurali ihlal SAYMAK degildir: veri eksikligi plan hatasi degil.
    """
    g = _sahne([_rol({"ekip": "E"})])
    r = degerlendir(g, [_atama("C1")])
    assert not _ihlaller(r, "ROL_KAPSAMASI"), (
        "eksik parametre plan ihlali gibi yazilmis")
    metinler = " ".join(str(x) for x in r["eksik_boyutlar"])
    assert "ROL_KAPSAMASI" in metinler, (
        "parametresiz kural hicbir kanalda bildirilmemis: %r"
        % r["eksik_boyutlar"])


# ----------------------------------------------------------------------
# 8. UCTAN UCA -- cozucu ile dogrulayici ayni plan hakkinda anlasiyor mu
# ----------------------------------------------------------------------

def test_UCTAN_UCA_cozucunun_urettigi_plan_DENETIMDEN_gecer():
    """Cozucunun urettigi plan, bagimsiz denetimden gecmeli.

    ⚠ SAHNE BILEREK AYRISMANIN OLAMAYACAGI SEKILDE KURULDU
      Cozucu bu kuralda ATANMIS kisiyi sayiyor, bu govde SAHADAKI kisiyi
      sayiyor (T-61). O ayrimin bu testte GORULMEMESI icin sahne oyle
      kuruldu ki fark ortaya cikamaz:

        * ucu de `takim_lideri` -- kim atanirsa nitelik sahada olur
        * `SAHADA_ASGARI` 1 -- cozucu her ceyrekte en az bir kisiyi
          sahada tutmak zorunda, yani "hepsi ayni anda molada" olamaz

      Boylece bu test PLUMBING'i olcer (kural aktif, govde kosuyor, gecerli
      plan temiz cikiyor) ve ayrismayi olcmez. Ayrismanin kendisi ayri bir
      olcumdur ve T-61 olarak kayitli -- bir testin iki isi birden yapmasi,
      kirmizi yandiginda hangi sebepten yandiginin anlasilmamasi demektir.
    """
    from cozucu.coz import coz

    g = {
        "profil": "DENGELI",
        "calisanlar": [
            _c("C1", rol="takim_lideri", yetkinlikler=["ing"]),
            _c("C2", rol="takim_lideri", yetkinlikler=["ing"]),
            _c("C3", rol="takim_lideri", yetkinlikler=["ing"]),
        ],
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 2}
                  for s in range(8, 16)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
             "yasal": False, "parametreler": {"asgari_sahada": 1}},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True,
             "yasal": True},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            _rol({"rol": "takim_lideri", "ekip": "E",
                  "saatler": list(range(8, 16)), "gun": 0}),
        ],
        "kilitler": [], "donmus_gunler": [],
    }
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    ih = _ihlaller(degerlendir(g, c["atamalar"]), "ROL_KAPSAMASI")
    assert not ih, (
        "cozucu plani uretti, bagimsiz denetci %d ROL_KAPSAMASI ihlali "
        "yazdi: %r" % (len(ih), [i["mesaj"] for i in ih][:3]))


def test_UCTAN_UCA_tek_lider_molaya_girse_de_plan_TEMIZ():
    """K-41'in uctan uca kaniti -- ve TERSINE CEVRILEN ikinci test.

    ⚠ ONCEKI HALI `test_AYRISMA_OLCUMU_cozucu_molayi_dusmuyor` idi ve
      ayrismanin GERCEK oldugunu kanitliyordu: tek lider, `SAHADA_ASGARI`
      yok, cozucu ucunun yemegini de ayni saate koyuyor ve o saatte sahada
      lider kalmiyordu. Denetci dort ceyrekte ihlal yaziyordu.

      K-41 ile olcu degisti: mola sahadan cikarmiyor. Ayni sahne artik
      TEMIZ cikmali. Test silinmedi, iddiasi ters cevrildi -- ayni sahne,
      ayni mekanizma, karsit beklenti. Karar geri alinirsa bu test tek
      basina onu yakalar.
    """
    from cozucu.coz import coz

    g = {
        "profil": "DENGELI",
        "calisanlar": [
            _c("C1", rol="takim_lideri", yetkinlikler=["ing"]),
            _c("C2", rol="uzman"),
            _c("C3", rol="uzman"),
        ],
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 2}
                  for s in range(8, 16)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True,
             "yasal": True},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            _rol({"rol": "takim_lideri", "ekip": "E",
                  "saatler": list(range(8, 16)), "gun": 0}),
        ],
        "kilitler": [], "donmus_gunler": [],
    }
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    lider = [a for a in c["atamalar"] if a["calisan"] == "C1"]
    assert lider, "cozucu tek lideri atamadi, sahne beklendigi gibi kurulmadi"
    assert lider[0].get("molalar"), (
        "lidere mola verilmemis -- sahne K-41'i sinamiyor")
    ih = _ihlaller(degerlendir(g, c["atamalar"]), "ROL_KAPSAMASI")
    assert not ih, (
        "K-41'e gore mola ihlal uretmemeli, %d ihlal var: %r"
        % (len(ih), [i["mesaj"] for i in ih][:2]))

# ----------------------------------------------------------------------
# 9. COZUCU TARAFI -- T-62'nin kirmizi kaniti
# ----------------------------------------------------------------------
#
# ⚠ Bu uc test yazilmadan once govde YENIDEN YAZILMISTI, yani kirmizi
#   kanitlari MUTASYONLA uretildi: eski davranis geri kondu ve ucu de
#   kirmizi yandi. Sira tersine dondu ve bunu yazmak zorundayim -- kirmizi
#   once kurali burada uygulanmadi.


def _cozucu_sahnesi(kural, calisanlar, asgari_talep=1):
    return {
        "profil": "DENGELI",
        "calisanlar": list(calisanlar),
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": asgari_talep,
                   "hedef": asgari_talep} for s in range(8, 16)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True,
             "yasal": True},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            kural,
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_COZUCU_saat_listesi_YOKSA_acik_saatlerin_hepsini_kisitlar():
    """⚠ T-62'nin birinci yarisi.

    Eski govde saat listesini `p.get("saatler", [])` ile okuyordu: liste
    yoksa dongu hic calismiyor, aktif bir SERT kural modele TEK kisit
    koymuyordu.

    ⚠ BU TESTIN ILK HALI MUTASYONDAN SAG KURTULDU -- ve sebebi ogretici.
      Ilk hali "kural iki lider istiyor, ikisi de atanmis mi" diye
      soruyordu. Kisit tamamen kaldirildiginda test YINE YESIL kaldi:
      cozucunun fazladan atama yapmasinin BIR MALIYETI YOK (T-54), yani
      iki lideri zaten kendiliginden atiyordu. "Atandi mi" sorusu bu
      motorda hicbir sey kanitlamiyor.

      Yerine IMKANSIZ bir gereklilik konuyor: iki lider varken UC lider
      isteniyor. Kisit yaziliyorsa plan cozumsuz kalmak ZORUNDA; kisit
      yazilmiyorsa plan rahatca cozulur. Cevap tek ve tesadufe kapali.

      Kural sunu da soyluyor: "olmasi gerekeni yapti mi" diye sormak
      yetmez, "yapmamis olsa test kirmizi yanar mi" diye sormak gerekir.
    """
    from cozucu.coz import coz

    liderler = [_c("C1", rol="takim_lideri"), _c("C2", rol="takim_lideri")]
    digerleri = [_c("C3", rol="uzman"), _c("C4", rol="uzman")]

    # (a) Iki lider isteniyor, iki lider var -> cozulebilir olmali.
    g = _cozucu_sahnesi(_rol({"rol": "takim_lideri", "ekip": "E",
                              "asgari": 2}),
                        liderler + digerleri)
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", (
        "iki lider varken iki lider istemek cozulebilir olmali: %s"
        % c.get("durum"))

    # (b) UC lider isteniyor, iki lider var -> kisit yazildiysa COZUMSUZ.
    g = _cozucu_sahnesi(_rol({"rol": "takim_lideri", "ekip": "E",
                              "asgari": 3}),
                        liderler + digerleri)
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] != "cozuldu", (
        "iki lider varken UC lider isteyen SERT kural plani engellemedi -- "
        "saat listesi olmadan kisit hic yazilmamis (durum: %s, atama: %d)"
        % (c.get("durum"), len(c.get("atamalar") or [])))


def test_COZUCU_ekip_YAZILMAZSA_plan_cozumsuz_kalmaz():
    """⚠ T-62'nin ikinci yarisi -- ve daha sinsi olani.

    Eski suzgec `p.get("ekip") in (c.get("ekipler") or [])` idi. Ekip
    yazilmazsa karsilastirma None ile yapiliyor, hic kimse uygun sayilmiyor
    ve modele "bos toplam >= 1" kisiti giriyordu: plan COZUMSUZ.

    Yoneticinin gordugu cumle "bu talebi bu kadroyla karsilamak imkansiz"
    olurdu -- personel alimina kadar giden bir karar, sebebi bir eksik
    parametre.
    """
    from cozucu.coz import coz

    g = _cozucu_sahnesi(_rol({"rol": "takim_lideri"}),
                        [_c("C1", rol="takim_lideri"), _c("C2", rol="uzman")])
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", (
        "ekip yazilmayan gereklilik plani cozumsuz birakti: %s / %s"
        % (c.get("durum"), str(c.get("aciklama"))[:120]))
    assert "C1" in {a["calisan"] for a in c["atamalar"]}, (
        "kural saha capinda okunmali ve tek lideri atamali")


def test_COZUCU_niteligi_tasiyan_YOKSA_not_yazar_cozumsuz_BIRAKMAZ():
    """Kimsede olmayan bir nitelik istenirse ne olmali.

    Kisit yazmak plani sessizce cozumsuz yapar ve sebebi gorunmez. Dogru
    davranis: kisit yazilmaz, NOT yazilir. Karsiligini dogrulayici soyler --
    gereklilik tutulmuyorsa ihlal yazar.

    "Yuksek sesle yanlis, sessizce cozumsuzdan iyidir" (#7.6).
    """
    from cozucu.coz import coz

    g = _cozucu_sahnesi(_rol({"rol": "bolge_muduru", "ekip": "E"}),
                        [_c("C1", rol="takim_lideri"), _c("C2", rol="uzman")])
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "bolge_muduru" in notlar, (
        "olmayan nitelik sessizce atlandi, not yazilmadi: %r"
        % (c.get("uygulanmayan_notlar"),))
    ih = _ihlaller(degerlendir(g, c["atamalar"]), "ROL_KAPSAMASI")
    assert ih, (
        "cozucu kisit yazmadi, dogrulayici da ihlal yazmadiysa gereklilik "
        "tamamen kayboldu -- iki taraf da sessiz kaldi")
