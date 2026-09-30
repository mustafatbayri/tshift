# -*- coding: utf-8 -*-
"""
HAFTA OLCEKLI IKI KURAL -- gece postasi devri (YASAL) ve ardisik hafta
sonu limiti (firma kurali)

NEDEN SIMDI (30 Eylul)
  Ikisi de plan haftasinin DISINA bakar: "gecen hafta da gece calisti mi",
  "gecen iki hafta sonu da calisti mi". Gecmis okunmadan (T-28) govdeleri
  yazilamazdi. T-28 ayni gun kapandi.

GECE_POSTASI_DEVRI -- YASAL, kabul edilemez (#6.3, K-25)
  Postalar Yonetmeligi md. 8, TAM METIN (30 Eylul'de okundu; sartnamede
  yalniz ilk fikranin bir parcasi aliniyordu):

    (1) "Gece ve gunduz isletilen ve nobetlese isci postalari
         calistirilarak yurutulen islerde postalar; en fazla bir is haftasi
         gece calistirilan iscilerin, ondan sonra gelen ikinci is haftasinda
         gunduz calistirilmalari suretiyle ve postalar birbirlerinin yerini
         alacak sekilde duzenlenir."
    (3) "Isin niteligi ve yurutumu, is sagligi ve guvenligi gozonunde
         tutularak, gece ve gunduz postalarinda iki haftalik nobetlesme
         esasi da uygulanabilir."

  ⚠ "BIR IS HAFTASI GECE CALISTIRILAN" YONETMELIKTE TANIMLI DEGIL.
    Burada EN SIKI okuma uygulandi: haftada TEK bir gece vardiyasi bile o
    haftayi "gece haftasi" yapar. Gevsek okumalar (cogunluk, esik) yasanin
    amacini delmeye acik: her hafta uc gece calisan biri hic "gece haftasi"
    yasamamis sayilirdi. Bu bir URUN KARARI -- Mustafa'ya sorulacak;
    cevap gelene kadar siki okuma.
  ⚠ GECE = YONETMELIGIN KENDI TANIMI, K-40 isareti DEGIL. md. 7/2:
      "Calisma suresinin yarisindan cogu gece donemine rastlayan bir
       postanin calismasi, gece calismasi sayilir."
    Ilk yazimda K-40 isareti kullanilmisti (ARDISIK_GECE_LIMIT gibi).
    md. 7/2 okununca degisti: yasal kuralda firma isareti ne kuraldan
    kacirabilir (22:00-06:00 "gece degil") ne de yasal olarak serbest bir
    vardiyayi kabul edilemez ihlale cevirebilir (15:15-24:00 "gece").
  ⚠ HAFTA = plan haftasi. Gun -1..-7 gecen hafta, -8..-14 ondan onceki.
    Vardiya BASLADIGI gunun haftasina yazilir (Z-2): pazar 23:00'te
    baslayan gece gecen haftanindir.

ARDISIK_HAFTA_SONU_LIMIT -- firma kurali, kabul edilebilir (#6.5)
  "Ust uste kac hafta sonu calisilabilir", varsayilan 2.
  ⚠ "HAFTA SONU CALISTI" = cumartesi YA DA pazar BASLAYAN bir vardiyasi
    var. ADALET_DENGESI'nin 'hafta_sonu' boyutuyla ayni tanim (iki tarafta
    da gun 5 ve 6). Cuma gecesi cumartesiye tasan vardiya SAYILMAZ -- bu
    bir secim, acikca yaziyorum.

K-42 IKISINDE DE GECERLI
  Bilinmeyen hafta kisit yaratmaz. Sonucu degistirebilecekse
  `gecmis_eksik` kanalinda yazilir; degistiremiyorsa yazilmaz.

⚠ TESTLER GOVDEDEN ONCE YAZILDI -- kirmizi kanit gercek. Cozucu testleri
  T-62'nin dersiyle kuruldu: talebi YALNIZ yasak secenek karsilayabiliyor,
  dogru sonuc "cozumsuz" olmak ZORUNDA.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_hafta_kurallari.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402

GUNDUZ = {"id": "V-GUNDUZ", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60,
          "gece_vardiyasi": False}
GECE = {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60,
        "gece_vardiyasi": True}


def _kural(kod, yasal=False, **par):
    k = {"kod": kod, "tur": "SERT", "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


DEVRI = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=1)
DEVRI_2 = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=2)
HSONU = _kural("ARDISIK_HAFTA_SONU_LIMIT", azami_ardisik=2)
HSONU_1 = _kural("ARDISIK_HAFTA_SONU_LIMIT", azami_ardisik=1)
ASGARI = {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
          "yasal": False}

GECEN_HAFTA = list(range(-7, 0))


def _kisi(kimlik="C1", gecmis=None, bilinen=None, **ek):
    c = {"id": kimlik, "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    if gecmis is not None:
        c["gecmis_vardiyalar"] = gecmis
    if bilinen is not None:
        c["gecmis_bilinen_gunler"] = bilinen
    c.update(ek)
    return c


def _sahne(kurallar, gecmis=None, bilinen=None):
    return {"profil": "DENGELI",
            "calisanlar": [_kisi(gecmis=gecmis, bilinen=bilinen)],
            "vardiya_sablonlari": [GUNDUZ, GECE], "talep": [],
            "kurallar": list(kurallar), "kilitler": [], "donmus_gunler": []}


def _g(gun, bas=8, bit=16, **ek):
    """Gecmis kaydi (#11.2 bicimi): gun negatif, saat genisletilmis."""
    d = {"gun": gun, "bas": bas, "bit": bit}
    d.update(ek)
    return d


def _gece(gun, **ek):
    return _g(gun, 23, 31, **ek)


def _p(gun, sablon=GUNDUZ, kimlik="C1"):
    return {"calisan": kimlik, "ekip": "E", "sablon": sablon["id"],
            "gun": gun, "bas": sablon["bas"], "bit": sablon["bit"],
            "molalar": []}


def _ih(g, plan, kod):
    return [i for i in degerlendir(g, plan)["ihlaller"] if i["kural"] == kod]


def _eksik(g, plan, kod):
    r = degerlendir(g, plan).get("gecmis_eksik")
    assert r is not None, "cikti `gecmis_eksik` kanalini tasimiyor"
    return [x for x in r if x["kural"] == kod]


# ======================================================================
# 1. GECE POSTASI DEVRI -- dogrulayici
# ======================================================================

def test_DEVRI_govdesi_YAZILI():
    r = degerlendir(_sahne([DEVRI]), [_p(0)])
    assert "GECE_POSTASI_DEVRI" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


def test_DEVRI_gecen_hafta_gece_BU_HAFTA_da_gece_IHLAL():
    """Gecen cuma gecesi calismis; bu carsamba yine gece. Yonetmelige gore
    bu hafta gunduz olmaliydi."""
    ih = _ih(_sahne([DEVRI], gecmis=[_gece(-3)]), [_p(2, GECE)],
             "GECE_POSTASI_DEVRI")
    assert len(ih) == 1, ih
    assert ih[0]["olculen"] == 2 and ih[0]["gereken"] == 1, ih[0]
    assert ih[0]["gun"] == 2 and ih[0]["calisan"] == "C1", ih[0]
    assert ih[0]["yasal"] is True and ih[0]["kabul_edilebilir"] is False, ih[0]


def test_DEVRI_TEK_gece_bile_haftayi_gece_haftasi_yapar():
    """SIKI OKUMA -- acik karar bekliyor. Gecen hafta yalniz pazartesi
    gecesi; bu hafta persembe gecesi. Gevsek bir okuma bunu serbest
    birakirdi. Karar degisirse DEGISECEK TEK TEST bu olmali."""
    ih = _ih(_sahne([DEVRI], gecmis=[_gece(-7)]), [_p(3, GECE)],
             "GECE_POSTASI_DEVRI")
    assert len(ih) == 1, "tek gecelik hafta gece haftasi sayilmadi"


def test_DEVRI_gecen_hafta_GUNDUZ_ise_ihlal_yok():
    g = _sahne([DEVRI], gecmis=[_g(d) for d in range(-7, -2)])
    assert not _ih(g, [_p(1, GECE), _p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_bu_hafta_GUNDUZE_gecilmisse_ihlal_yok():
    """Yonetmeligin istedigi tam bu: gece haftasindan sonra gunduz haftasi."""
    g = _sahne([DEVRI], gecmis=[_gece(d) for d in (-5, -4, -3)])
    assert not _ih(g, [_p(d) for d in range(5)], "GECE_POSTASI_DEVRI")


def test_DEVRI_arada_GUNDUZ_haftasi_seriyi_KIRAR():
    """Iki hafta once gece, gecen hafta gunduz (tam biliniyor), bu hafta
    gece -- nobetlesme tam istendigi gibi."""
    g = _sahne([DEVRI], gecmis=[_gece(-10), _gece(-9)]
               + [_g(d) for d in range(-7, -2)], bilinen=GECEN_HAFTA)
    assert not _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_gecmisin_KENDI_ihlali_plana_yazilmaz():
    """Iki onceki hafta da gece (gecmiste bir ihlal); bu hafta gunduz.
    Gecmis yeniden planlanamaz."""
    g = _sahne([DEVRI], gecmis=[_gece(-10), _gece(-3)])
    assert not _ih(g, [_p(0), _p(1)], "GECE_POSTASI_DEVRI")


def test_DEVRI_gecmis_kaydin_GECE_ISARETI_yasal_kurali_DELEMEZ():
    """⚠ YASAL KURALDA ISARET OKUNMAZ. 23:00-07:00 kaydi `gece: false`
    dese de calisma suresinin yarisindan cogu 20:00-06:00'da -- md. 7/2
    geregi gece calismasidir. Firma yasadan isaretle kacamaz (K-18).

    (K-40 isareti firma kurallarinda gecerli; ARDISIK_GECE_LIMIT'in ayni
    durumdaki testi tersini bekler ve o da dogrudur.)"""
    g = _sahne([DEVRI], gecmis=[_gece(-3, gece=False)])
    assert _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_ISARETSIZ_gecmis_kaydi_yasal_tanimla_olculur():
    """PDKS kaydinda isaret yok -- 23:00-07:00, 7/8'i gece doneminde."""
    g = _sahne([DEVRI], gecmis=[_gece(-3)])
    assert _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


AKSAM = {"id": "V-AKSAM", "ekip": "E", "bas": 15.25, "bit": 24, "mola_dk": 45,
         "gece_vardiyasi": True}
YANLIS_ISARET = {"id": "V-GECE-ISARETSIZ", "ekip": "E", "bas": 22, "bit": 30,
                 "mola_dk": 30, "gece_vardiyasi": False}


def test_DEVRI_gece_ISARETLI_aksam_vardiyasi_yasal_gece_DEGIL():
    """15:15-24:00 firmanin gozunde gece (veri setindeki B-AKSAM gibi) ama
    8,75 saatin 4'u gece doneminde: yarisindan az. Yasal kural bunu gece
    haftasi sayarsa yasal olarak serbest bir plani KABUL EDILEMEZ bir
    ihlalle kilitler (K-20)."""
    g = _sahne([DEVRI], gecmis=[_g(-3, 15.25, 24, gece=True)])
    g["vardiya_sablonlari"].append(AKSAM)
    assert not _ih(g, [_p(2, AKSAM)], "GECE_POSTASI_DEVRI")
    assert not _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_gece_DEGIL_isaretli_22_06_sablonu_yine_SAYILIR():
    g = _sahne([DEVRI], gecmis=[_gece(-3)])
    g["vardiya_sablonlari"].append(YANLIS_ISARET)
    assert _ih(g, [_p(2, YANLIS_ISARET)], "GECE_POSTASI_DEVRI"), (
        "gece degil isaretli 22:00-06:00 vardiyasi yasal kuraldan kacti")


def test_DEVRI_tam_YARISI_gece_calismasi_DEGIL():
    """'Yarisindan cogu' -- 16:00-24:00 (4 / 8) gece calismasi degil."""
    g = _sahne([DEVRI], gecmis=[_g(-3, 16, 24)])
    assert not _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_yarisindan_COGU_gece_calismasidir():
    """18:00-02:00 (6 / 8) gece calismasi."""
    g = _sahne([DEVRI], gecmis=[_g(-3, 18, 26)])
    assert _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_sabah_ERKEN_vardiya_onceki_gecenin_donemine_duser():
    """00:00-08:45 (6 / 8,75): gece donemi ONCEKI gunun 20:00'inde basladi.
    Yalniz ayni gunun 20:00-06:00'ina bakan bir olcu bunu kacirirdi
    (T-69'un bu kuraldaki karsiligi)."""
    g = _sahne([DEVRI], gecmis=[_g(-3, 0, 8.75)])
    assert _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_PAZAR_gecesi_GECEN_haftanindir():
    """Pazar 23:00'te baslayan gece gun -1'dir, yani GECEN hafta.

    Haftayi `int(gun / 7)` ile hesaplayan bir govde -1'i 0'a yuvarlar ve
    pazar gecesini bu haftaya koyar: seri 1 olur, ihlal kaybolur.
    """
    g = _sahne([DEVRI], gecmis=[_gece(-1)])
    ih = _ih(g, [_p(3, GECE)], "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 2, ih


def test_DEVRI_haftada_bir_ihlal_ilk_gece_gunune_yazilir():
    g = _sahne([DEVRI], gecmis=[_gece(-3)])
    ih = _ih(g, [_p(2, GECE), _p(4, GECE)], "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["gun"] == 2, ih


def test_DEVRI_azami_2_ikinci_gece_haftasi_SERBEST():
    """md. 8/3: iki haftalik nobetlesme de uygulanabilir."""
    g = _sahne([DEVRI_2], gecmis=[_gece(-3)])
    assert not _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_DEVRI_azami_2_ucuncu_gece_haftasi_IHLAL():
    g = _sahne([DEVRI_2], gecmis=[_gece(-10), _gece(-3)])
    ih = _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_DEVRI_BILINMEYEN_hafta_kisit_yaratmaz():
    """K-42: gecmis hic yok -> gecen hafta gece sayilmaz."""
    assert not _ih(_sahne([DEVRI]), [_p(2, GECE)], "GECE_POSTASI_DEVRI")


# ----------------------------------------------------------------------
# 2. GECE POSTASI DEVRI -- K-42 raporu
# ----------------------------------------------------------------------

def test_K42_DEVRI_gecmis_yok_plan_gece_RAPORLANIR():
    e = _eksik(_sahne([DEVRI]), [_p(2, GECE)], "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["calisan"] == "C1" and e[0]["gun"] == -1, e


def test_K42_DEVRI_gecen_hafta_TAM_biliniyorsa_rapor_yok():
    g = _sahne([DEVRI], gecmis=[], bilinen=GECEN_HAFTA)
    assert not _eksik(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_plan_haftasinda_gece_YOKSA_rapor_yok():
    """Bu hafta gece yoksa gecen haftanin ne oldugu sonucu degistiremez."""
    assert not _eksik(_sahne([DEVRI]), [_p(0), _p(1)], "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_gecen_haftanin_BIR_gunu_bilinmiyorsa_raporlanir():
    """Pazartesi-cumartesi biliniyor, bos; pazar bilinmiyor. Pazar gecesi
    calismis olabilir -- o zaman bu hafta gece yasakti."""
    g = _sahne([DEVRI], gecmis=[], bilinen=list(range(-7, -1)))
    e = _eksik(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_DEVRI_kanitli_ihlal_RAPORLANMAZ_ihlal_yazilir():
    g = _sahne([DEVRI], gecmis=[_gece(-3)])
    assert _ih(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")
    assert not _eksik(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_azami_2_onceki_hafta_BILINMIYORSA_raporlanir():
    """Gecen hafta gece (kanitli), ondan onceki hafta bilinmiyor. O da gece
    ise bu hafta ucuncu olur."""
    g = _sahne([DEVRI_2], gecmis=[_gece(-3)], bilinen=GECEN_HAFTA)
    e = _eksik(g, [_p(2, GECE)], "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["gun"] == -8, e


# ======================================================================
# 3. ARDISIK HAFTA SONU LIMITI -- dogrulayici
# ======================================================================

def test_HSONU_govdesi_YAZILI():
    r = degerlendir(_sahne([HSONU]), [_p(5)])
    assert "ARDISIK_HAFTA_SONU_LIMIT" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


def test_HSONU_UCUNCU_hafta_sonu_IHLAL():
    """Iki onceki cumartesi calismis; bu cumartesi ucuncu."""
    ih = _ih(_sahne([HSONU], gecmis=[_g(-9), _g(-2)]), [_p(5)],
             "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1, ih
    assert ih[0]["olculen"] == 3 and ih[0]["gereken"] == 2, ih[0]
    assert ih[0]["gun"] == 5 and ih[0]["kabul_edilebilir"] is True, ih[0]


def test_HSONU_ikinci_hafta_sonu_SERBEST():
    assert not _ih(_sahne([HSONU], gecmis=[_g(-2)]), [_p(5)],
                   "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_arada_BOS_hafta_sonu_seriyi_KIRAR():
    g = _sahne([HSONU], gecmis=[_g(-9)], bilinen=[-2, -1])
    assert not _ih(g, [_p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_PAZAR_da_hafta_sonudur():
    ih = _ih(_sahne([HSONU], gecmis=[_g(-8), _g(-1)]), [_p(6)],
             "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_HSONU_CUMA_gecesi_hafta_sonu_SAYILMAZ():
    """Cuma 23:00 - cumartesi 07:00 cumaya yazilir (Z-2). Secim acik."""
    g = _sahne([HSONU], gecmis=[_gece(-10), _gece(-3)])
    assert not _ih(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_iki_gun_calisilan_hafta_sonu_TEK_hafta_sonudur():
    g = _sahne([HSONU], gecmis=[_g(-9), _g(-8), _g(-2), _g(-1)])
    ih = _ih(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_HSONU_plan_hafta_sonu_BOSSA_ihlal_yok():
    """Gecmiste iki hafta sonu ust uste; bu hafta sonu bos -- plan temiz."""
    g = _sahne([HSONU], gecmis=[_g(-9), _g(-2)])
    assert not _ih(g, [_p(0), _p(4)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_gecmisin_KENDI_serisi_plana_yazilmaz():
    """Azami 1: gecmiste iki hafta sonu ust uste (bir ihlal). Plan bos
    hafta sonu -- yazilacak bir sey yok."""
    g = _sahne([HSONU_1], gecmis=[_g(-9), _g(-2)])
    assert not _ih(g, [_p(1)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_azami_1_ikinci_hafta_sonu_IHLAL():
    ih = _ih(_sahne([HSONU_1], gecmis=[_g(-1)]), [_p(5)],
             "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 2, ih


def test_HSONU_BILINMEYEN_hafta_sonu_kisit_yaratmaz():
    assert not _ih(_sahne([HSONU_1]), [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")


# ----------------------------------------------------------------------
# 4. ARDISIK HAFTA SONU -- K-42 raporu
# ----------------------------------------------------------------------

def test_K42_HSONU_gecmis_yok_RAPORLANIR():
    e = _eksik(_sahne([HSONU]), [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_HSONU_gecen_hafta_sonu_BILINEN_bos_ise_rapor_yok():
    g = _sahne([HSONU], gecmis=[], bilinen=[-2, -1])
    assert not _eksik(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_K42_HSONU_gecen_calisilmis_ONCEKI_bilinmiyor():
    g = _sahne([HSONU], gecmis=[_g(-2)], bilinen=[-2, -1])
    e = _eksik(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -8, e


def test_K42_HSONU_hafta_sonunun_YARISI_biliniyor():
    """Cumartesi bilinen bos, pazar bilinmiyor -- pazar calismis olabilir."""
    g = _sahne([HSONU_1], gecmis=[], bilinen=[-2])
    e = _eksik(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_HSONU_plan_hafta_sonu_YOKSA_rapor_yok():
    assert not _eksik(_sahne([HSONU]), [_p(0)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_K42_HSONU_kanitli_ihlal_RAPORLANMAZ():
    g = _sahne([HSONU], gecmis=[_g(-9), _g(-2)])
    assert _ih(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert not _eksik(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")


# ======================================================================
# 5. COZUCU TARAFI
# ======================================================================

def _cozucu_sahnesi(kurallar, gecmis=None, bilinen=None, sablonlar=None,
                    talep=()):
    g = _sahne([ASGARI] + list(kurallar), gecmis=gecmis, bilinen=bilinen)
    if sablonlar is not None:
        g["vardiya_sablonlari"] = list(sablonlar)
    g["talep"] = [{"ekip": "E", "gun": d, "saat": h, "asgari": 1, "hedef": 1}
                  for d, h in talep]
    return g


def _coz(g):
    from cozucu.coz import coz
    return coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})


def _cozuldu(g):
    return _coz(g)["durum"] == "cozuldu"


def test_COZUCU_DEVRI_gecen_hafta_gece_calisana_GECE_YAZMAZ():
    """Gecen cuma gecesi calismis TEK kisi; carsamba gecesi talebi yalniz
    onunla karsilanabilir -> plan cozumsuz kalmak ZORUNDA."""
    g = _cozucu_sahnesi([DEVRI], gecmis=[_gece(-3)], sablonlar=[GECE],
                        talep=[(2, 23)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "gecen hafta gece calismis kisiye bu hafta gece yazildi: %r"
        % c.get("atamalar"))


def test_COZUCU_DEVRI_gecmis_OLMADAN_ayni_sahne_cozulur():
    """Karsi kanit: onceki testteki cozumsuzlugun TEK sebebi gecmis."""
    assert _cozuldu(_cozucu_sahnesi([DEVRI], sablonlar=[GECE],
                                    talep=[(2, 23)]))


def test_COZUCU_DEVRI_gecen_hafta_GUNDUZ_ise_cozulur():
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=[_g(d) for d in range(-7, -2)], sablonlar=[GECE],
        talep=[(2, 23)]))


def test_COZUCU_DEVRI_gecmis_kaydin_GECE_ISARETI_yasal_kurali_DELEMEZ():
    g = _cozucu_sahnesi([DEVRI], gecmis=[_gece(-3, gece=False)],
                        sablonlar=[GECE], talep=[(2, 23)])
    assert _coz(g)["durum"] != "cozuldu", (
        "`gece: false` isaretli 23-07 kaydi yasal kuraldan kacti")


def test_COZUCU_DEVRI_gece_ISARETLI_aksam_sablonu_KISITLANMAZ():
    """16:00 talebini yalniz 15:15-24:00 kapatabilir; isaretli ama yasal
    olarak gece degil. Kisitlanirsa plan yasal olarak serbestken
    cozumsuz kalirdi."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=[_gece(-3)], sablonlar=[AKSAM], talep=[(2, 16)]))


def test_COZUCU_DEVRI_gece_DEGIL_isaretli_22_06_sablonu_KISITLANIR():
    g = _cozucu_sahnesi([DEVRI], gecmis=[_gece(-3)],
                        sablonlar=[YANLIS_ISARET], talep=[(2, 23)])
    assert _coz(g)["durum"] != "cozuldu", (
        "gece degil isaretli 22:00-06:00 sablonu yasal kuraldan kacti")


def test_COZUCU_DEVRI_sabah_ERKEN_gecmis_kaydi_sayilir():
    g = _cozucu_sahnesi([DEVRI], gecmis=[_g(-3, 0, 8.75)],
                        sablonlar=[GECE], talep=[(2, 23)])
    assert _coz(g)["durum"] != "cozuldu"


def test_COZUCU_DEVRI_tam_YARISI_gece_sayilmaz():
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=[_g(-3, 16, 24)], sablonlar=[GECE], talep=[(2, 23)]))


def test_COZUCU_DEVRI_PAZAR_gecesi_GECEN_haftanindir():
    g = _cozucu_sahnesi([DEVRI], gecmis=[_gece(-1)], sablonlar=[GECE],
                        talep=[(3, 23)])
    assert _coz(g)["durum"] != "cozuldu", "pazar gecesi gecen hafta sayilmadi"


def test_COZUCU_DEVRI_azami_2_ikinci_hafta_SERBEST():
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI_2], gecmis=[_gece(-3)], sablonlar=[GECE], talep=[(2, 23)]))


def test_COZUCU_DEVRI_azami_2_ucuncu_hafta_YAZMAZ():
    g = _cozucu_sahnesi([DEVRI_2], gecmis=[_gece(-10), _gece(-3)],
                        sablonlar=[GECE], talep=[(2, 23)])
    assert _coz(g)["durum"] != "cozuldu", "ucuncu gece haftasi yazildi"


def test_COZUCU_DEVRI_azami_2_ARADA_bilinmeyen_hafta_kisit_yaratmaz():
    """K-42: iki hafta onceki gece kanitli, gecen hafta BILINMIYOR ->
    seri gecen haftadan gecemez, kisit yok."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI_2], gecmis=[_gece(-10)], sablonlar=[GECE], talep=[(2, 23)]))


def test_UCTAN_UCA_DEVRI_cozucu_dogru_kisiyi_secer_denetci_onaylar():
    """C1 gecen hafta gece calisti, C2 gunduz. Carsamba gecesi talebi:
    cozucu C2'yi secmeli; denetci ayni plani temiz bulmali."""
    g = _cozucu_sahnesi([DEVRI], sablonlar=[GECE], talep=[(2, 23)])
    g["calisanlar"] = [
        _kisi("C1", gecmis=[_gece(-3)], bilinen=GECEN_HAFTA),
        _kisi("C2", gecmis=[_g(-3)], bilinen=GECEN_HAFTA)]
    c = _coz(g)
    assert c["durum"] == "cozuldu", c.get("durum")
    gececiler = {a["calisan"] for a in c["atamalar"]}
    assert "C1" not in gececiler, "gecen hafta gece calisana gece yazildi"
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"]
                if i["kural"] == "GECE_POSTASI_DEVRI"], r["ihlaller"]
    assert not [x for x in r["gecmis_eksik"]
                if x["kural"] == "GECE_POSTASI_DEVRI"], r["gecmis_eksik"]


def test_COZUCU_HSONU_UCUNCU_hafta_sonunu_YAZMAZ():
    g = _cozucu_sahnesi([HSONU], gecmis=[_g(-9), _g(-2)],
                        sablonlar=[GUNDUZ], talep=[(5, 8)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "ust uste ucuncu hafta sonu yazildi: %r" % c.get("atamalar"))


def test_COZUCU_HSONU_gecmis_OLMADAN_ayni_sahne_cozulur():
    assert _cozuldu(_cozucu_sahnesi([HSONU], sablonlar=[GUNDUZ],
                                    talep=[(5, 8)]))


def test_COZUCU_HSONU_ikinci_hafta_sonu_SERBEST():
    assert _cozuldu(_cozucu_sahnesi([HSONU], gecmis=[_g(-2)],
                                    sablonlar=[GUNDUZ], talep=[(5, 8)]))


def test_COZUCU_HSONU_PAZAR_da_sayilir():
    g = _cozucu_sahnesi([HSONU], gecmis=[_g(-8), _g(-1)],
                        sablonlar=[GUNDUZ], talep=[(6, 8)])
    assert _coz(g)["durum"] != "cozuldu", "pazar calismasi hafta sonu sayilmadi"


def test_COZUCU_HSONU_CUMA_gecesi_SAYILMAZ():
    assert _cozuldu(_cozucu_sahnesi(
        [HSONU], gecmis=[_gece(-10), _gece(-3)], sablonlar=[GUNDUZ],
        talep=[(5, 8)]))


def test_COZUCU_HSONU_azami_1_BILINMEYEN_hafta_sonu_kisit_yaratmaz():
    assert _cozuldu(_cozucu_sahnesi([HSONU_1], sablonlar=[GUNDUZ],
                                    talep=[(5, 8)]))


def test_COZUCU_HSONU_azami_1_gecen_hafta_sonu_calisana_YAZMAZ():
    g = _cozucu_sahnesi([HSONU_1], gecmis=[_g(-1)], sablonlar=[GUNDUZ],
                        talep=[(6, 8)])
    assert _coz(g)["durum"] != "cozuldu"


def test_UCTAN_UCA_HSONU_cozucu_dogru_kisiyi_secer_denetci_onaylar():
    g = _cozucu_sahnesi([HSONU], sablonlar=[GUNDUZ], talep=[(5, 8)])
    g["calisanlar"] = [
        _kisi("C1", gecmis=[_g(-9), _g(-2)], bilinen=list(range(-14, 0))),
        _kisi("C2", gecmis=[_g(-9)], bilinen=list(range(-14, 0)))]
    c = _coz(g)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert "C1" not in {a["calisan"] for a in c["atamalar"] if a["gun"] == 5}
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"]
                if i["kural"] == "ARDISIK_HAFTA_SONU_LIMIT"], r["ihlaller"]


# ======================================================================
# 6. IKI ASAMA -- cozucunun ciktisi gecmis olunca gece postasi devri
# ======================================================================
#
# Mustafa'nin yolu (30 Eylul): once bir hafta, sonra onun sonucunu gecmis
# sayarak ikinci hafta. Burada sinanan BORU HATTI: gun - 7 donusumu ve
# haftaya yazma. Hafta 1'in PAZAR gecesi (gun 6 -> -1) bilerek secildi --
# haftayi yanlis yuvarlayan bir govde onu bu haftaya koyardi.

def _iki_asama(talep, sabit=None, gecmis_atamalar=None):
    g = _cozucu_sahnesi([DEVRI, {"kod": "GECE_UYGUNLUGU", "tur": "SERT",
                                 "aktif": True, "yasal": False,
                                 "kabul_edilebilir": False}],
                        sablonlar=[GUNDUZ, GECE], talep=talep)
    g["calisanlar"] = [_kisi("C1"), _kisi("C2", gece_calisamaz=True)]
    if sabit:
        g["sabit_atamalar"] = sabit
    if gecmis_atamalar is not None:
        kisi = {}
        for a in gecmis_atamalar:
            k = {"gun": a["gun"] - 7, "bas": a["bas"], "bit": a["bit"]}
            if a.get("sablon") == GECE["id"]:
                k["gece"] = True
            elif a.get("sablon") == GUNDUZ["id"]:
                k["gece"] = False
            kisi.setdefault(a["calisan"], []).append(k)
        for c in g["calisanlar"]:
            c["gecmis_vardiyalar"] = kisi.get(c["id"], [])
            c["gecmis_bilinen_gunler"] = GECEN_HAFTA
    return g


def test_IKI_ASAMA_hafta_1in_pazar_gecesi_hafta_2de_geceyi_KAPATIR():
    h1 = _coz(_iki_asama(talep=[(6, 23)],
                         sabit=[{"calisan": "C1", "gun": 6,
                                 "sablon": GECE["id"]}]))
    assert h1["durum"] == "cozuldu", h1.get("durum")
    assert ("C1", 6) in [(a["calisan"], a["gun"]) for a in h1["atamalar"]
                         if a["sablon"] == GECE["id"]], h1["atamalar"]

    h2 = _coz(_iki_asama(talep=[(3, 23)], gecmis_atamalar=h1["atamalar"]))
    assert h2["durum"] != "cozuldu", (
        "hafta 1'de pazar gecesi calisan tek gececiye hafta 2'de gece "
        "yazildi: %r" % h2.get("atamalar"))


def test_IKI_ASAMA_gecmis_OLMADAN_hafta_2_cozulur():
    assert _cozuldu(_iki_asama(talep=[(3, 23)]))
