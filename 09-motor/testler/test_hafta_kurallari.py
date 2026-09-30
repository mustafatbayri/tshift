# -*- coding: utf-8 -*-
"""
HAFTA OLCEKLI IKI KURAL -- gece postasi devri (YASAL) ve ardisik hafta
sonu limiti (firma kurali)

NEDEN SIMDI (30 Eylul)
  Ikisi de plan haftasinin DISINA bakar: "gecen hafta da gece calisti mi",
  "gecen iki hafta sonu da calisti mi". Gecmis okunmadan (T-28) govdeleri
  yazilamazdi. T-28 ayni gun kapandi.

GECE_POSTASI_DEVRI -- YASAL, kabul edilemez (#6.3, K-25, K-45)
  Is K. md. 69 / Postalar Yonetmeligi md. 8, TAM METIN (30 Eylul'de okundu):
    (1) "...en fazla bir is haftasi gece calistirilan iscilerin, ondan sonra
         gelen ikinci is haftasinda gunduz calistirilmalari suretiyle ve
         postalar birbirlerinin yerini alacak sekilde duzenlenir."
    (3) "...gece ve gunduz postalarinda iki haftalik nobetlesme esasi da
         uygulanabilir."

  K-45 (Mustafa, 30 Eylul gecesi -- hukukcu yok, cevrimici kaynaklarla):
    * GECE HAFTASI = haftanin calisma saatlerinin YARISINDAN COGU gece
      postasinda. Yonetmeligin tek vardiya olcusu (md. 7/2) haftaya
      uygulandi. Hicbir kaynak karma haftayi tanimlamiyor; hepsi kuralin
      amacini SUREKLI gece calistirma yasagi olarak veriyor (Yargitay
      22. HD 2019/18396: bir ay araliksiz gece = ihlal).
      `gece_haftasi_asgari_gece` yalniz EKLER (daha siki).
    * KURAL: art arda 2 x azami haftada en fazla azami gece haftasi.
      azami 1: G-D-G-D · azami 2: G-G-D-D; G-G-D-G yasak. Ust sinir 2.
    * GECE = YONETMELIGIN TANIMI (md. 7/2), K-40 isareti DEGIL (K-43:
      isaret yasal kuralda ne kacirir ne kilitler).
    * Gecmis hafta yalniz TAM bilinen ise degerlendirilir (K-42).

ARDISIK_HAFTA_SONU_LIMIT -- firma kurali, kabul edilebilir (#6.5, K-46)
  "Ust uste kac hafta sonu calisilabilir", varsayilan 2.
  K-46 (Mustafa, 30 Eylul gecesi):
    * "HAFTA SONU CALISTI" = HEM cumartesi HEM pazar. Onceki tanim (bir gun
      yeter) hafta hafta planlamada ucuncu haftayi cozumsuz birakiyordu
      (T-75): 6 gunluk desende herkes her hafta sonu "calismis" sayiliyordu.
    * GUN = vardiyanin saatlerinin yarisindan cogunun dustugu gun:
      cuma 23:00-06:00 cumartesidir, cuma 16:00-01:00 cumadir.

K-42 IKISINDE DE GECERLI
  Bilinmeyen hafta kisit yaratmaz. Sonucu degistirebilecekse
  `gecmis_eksik` kanalinda yazilir; degistiremiyorsa yazilmaz.

⚠ TESTLER GOVDEDEN ONCE YAZILDI (ilk surum) ve tanim degisince YENIDEN
  YAZILDI. Cozucu testleri T-62'nin dersiyle kuruldu: talebi YALNIZ yasak
  secenek karsilayabiliyor, dogru sonuc "cozumsuz" olmak ZORUNDA.

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
AKSAM = {"id": "V-AKSAM", "ekip": "E", "bas": 15.25, "bit": 24, "mola_dk": 45,
         "gece_vardiyasi": True}                  # firma gece der, yasa demez
YANLIS_ISARET = {"id": "V-GECE-ISARETSIZ", "ekip": "E", "bas": 22, "bit": 30,
                 "mola_dk": 30, "gece_vardiyasi": False}  # firma inkar eder


def _kural(kod, yasal=False, **par):
    k = {"kod": kod, "tur": "SERT", "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


DEVRI = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=1)
DEVRI_2 = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=2)
DEVRI_3 = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=3)
DEVRI_SIKI = _kural("GECE_POSTASI_DEVRI", yasal=True,
                    azami_ardisik_gece_haftasi=1, gece_haftasi_asgari_gece=1)
HSONU = _kural("ARDISIK_HAFTA_SONU_LIMIT", azami_ardisik=2)
HSONU_1 = _kural("ARDISIK_HAFTA_SONU_LIMIT", azami_ardisik=1)
ASGARI = {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
          "yasal": False}

GECEN_HAFTA = list(range(-7, 0))
IKI_HAFTA = list(range(-14, 0))
UC_HAFTA = list(range(-21, 0))


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


def _gece_haftasi(hafta, gunler=(0, 1, 2, 3, 4)):
    """Gecmis hafta: verilen gunler gece (tam bilinen hafta ile kullan)."""
    return [_gece(7 * hafta + g) for g in gunler]


def _gunduz_haftasi(hafta, gunler=(0, 1, 2, 3, 4)):
    return [_g(7 * hafta + g) for g in gunler]


def _p(gun, sablon=GUNDUZ, kimlik="C1"):
    return {"calisan": kimlik, "ekip": "E", "sablon": sablon["id"],
            "gun": gun, "bas": sablon["bas"], "bit": sablon["bit"],
            "molalar": []}


def _plan_gece_haftasi(gunler=(0, 1, 2, 3, 4)):
    return [_p(g, GECE) for g in gunler]


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
    """Gecen hafta bes gece; bu hafta bes gece. Ikinci hafta gunduz
    olmaliydi."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    ih = _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(ih) == 1, ih
    assert ih[0]["olculen"] == 2 and ih[0]["gereken"] == 1, ih[0]
    assert ih[0]["gun"] == 0 and ih[0]["calisan"] == "C1", ih[0]
    assert ih[0]["yasal"] is True and ih[0]["kabul_edilebilir"] is False, ih[0]


def test_DEVRI_gece_haftasi_COGUNLUK_ister_tek_gece_yetmez():
    """K-45: gecen hafta bir gece dort gunduz -- gece haftasi DEGIL. Bu
    hafta bes gece serbest. (Eski siki okumada ihlaldi.)"""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1, (0,)) + _gunduz_haftasi(-1, (1, 2, 3, 4)),
               bilinen=GECEN_HAFTA)
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_bu_haftanin_da_cogunlugu_gece_olmali():
    """Gecen hafta gece haftasi; bu hafta iki gece uc gunduz -> bu hafta
    gece haftasi degil -> ihlal yok."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    plan = [_p(0, GECE), _p(1, GECE), _p(2), _p(3), _p(4)]
    assert not _ih(g, plan, "GECE_POSTASI_DEVRI")


def test_DEVRI_tam_YARISI_gece_haftasi_DEGIL():
    """Yarisindan COGU: dort gece dort gunduz (esit saat) gece haftasi degil."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    plan = [_p(d, GECE) for d in (0, 1, 2, 3)] + [_p(d) for d in (4, 5, 6)]
    # 4 x 8 sa gece = 32, 3 x 8 sa gunduz = 24 -> gece haftasi. Yariyi
    # kurmak icin ucuncu gunduz yerine bir gece daha degil, esitlik:
    plan = [_p(d, GECE) for d in (0, 1, 2)] + [_p(d) for d in (3, 4, 5)]
    assert not _ih(g, plan, "GECE_POSTASI_DEVRI"), "24 = 24 gece haftasi sayildi"


def test_DEVRI_asgari_gece_ayari_YALNIZ_EKLER():
    """`gece_haftasi_asgari_gece: 1` -> tek gece bile haftayi gece haftasi
    yapar (eski siki okuma, firma isterse). Gevsetme yonu yok."""
    g = _sahne([DEVRI_SIKI], gecmis=_gece_haftasi(-1, (0,)) + _gunduz_haftasi(-1, (1, 2, 3, 4)),
               bilinen=GECEN_HAFTA)
    ih = _ih(g, [_p(2, GECE)] + [_p(d) for d in (0, 1, 3, 4)], "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 2, ih


def test_DEVRI_saat_agirlikli_iki_uzun_gece_uc_kisa_gunduzu_gecer():
    """Olcu SAAT, vardiya sayisi degil: 2 x 8 sa gece > 3 x 4 sa gunduz."""
    kisa = dict(GUNDUZ, id="V-KISA", bas=9, bit=13, mola_dk=0)
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    g["vardiya_sablonlari"].append(kisa)
    plan = [_p(0, GECE), _p(1, GECE), _p(2, kisa), _p(3, kisa), _p(4, kisa)]
    ih = _ih(g, plan, "GECE_POSTASI_DEVRI")
    assert len(ih) == 1, "saat agirligi yerine vardiya sayisi kullanildi"


def test_DEVRI_gecen_hafta_GUNDUZ_ise_ihlal_yok():
    g = _sahne([DEVRI], gecmis=_gunduz_haftasi(-1), bilinen=GECEN_HAFTA)
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_bu_hafta_GUNDUZE_gecilmisse_ihlal_yok():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    assert not _ih(g, [_p(d) for d in range(5)], "GECE_POSTASI_DEVRI")


def test_DEVRI_arada_GUNDUZ_haftasi_seriyi_KIRAR():
    """Gece, gunduz, gece -- tam istenen nobetlesme."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-2) + _gunduz_haftasi(-1),
               bilinen=IKI_HAFTA)
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_gecmisin_KENDI_ihlali_plana_yazilmaz():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-2) + _gece_haftasi(-1),
               bilinen=IKI_HAFTA)
    assert not _ih(g, [_p(0), _p(1)], "GECE_POSTASI_DEVRI")


def test_DEVRI_gecmis_kaydin_GECE_DEGIL_isareti_yasal_kurali_DELEMEZ():
    """K-43: 23:00-07:00 kaydi `gece: false` dese de md. 7/2'ye gore gece."""
    g = _sahne([DEVRI], gecmis=[_gece(d, gece=False) for d in range(-7, -2)],
               bilinen=GECEN_HAFTA)
    assert _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_ISARETSIZ_gecmis_kaydi_yasal_tanimla_olculur():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    assert _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_gece_ISARETLI_aksam_vardiyasi_yasal_gece_DEGIL():
    """15:15-24:00 firmanin gozunde gece ama 8,75 saatin 4'u gece
    doneminde -- yasal kural saymaz (K-20: yasal plan kilitlenmesin)."""
    g = _sahne([DEVRI], gecmis=[_g(d, 15.25, 24, gece=True) for d in range(-7, -2)],
               bilinen=GECEN_HAFTA)
    g["vardiya_sablonlari"].append(AKSAM)
    assert not _ih(g, [_p(d, AKSAM) for d in range(5)], "GECE_POSTASI_DEVRI")
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_gece_DEGIL_isaretli_22_06_sablonu_yine_SAYILIR():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    g["vardiya_sablonlari"].append(YANLIS_ISARET)
    assert _ih(g, [_p(d, YANLIS_ISARET) for d in range(5)], "GECE_POSTASI_DEVRI"), (
        "gece degil isaretli 22:00-06:00 vardiyasi yasal kuraldan kacti")


def test_DEVRI_sabah_ERKEN_vardiya_onceki_gecenin_donemine_duser():
    """00:00-08:45 (6 / 8,75): gece donemi onceki gunun 20:00'inde basladi."""
    g = _sahne([DEVRI], gecmis=[_g(d, 0, 8.75) for d in range(-7, -2)],
               bilinen=GECEN_HAFTA)
    assert _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_PAZAR_gecesi_GECEN_haftanindir():
    """Pazar 23:00'te baslayan gece gun -1'dir, GECEN hafta. `int(gun / 7)`
    -1'i 0'a yuvarlar ve pazar gecesini bu haftaya koyardi."""
    g = _sahne([DEVRI], gecmis=[_gece(d) for d in (-5, -4, -3, -2, -1)],
               bilinen=GECEN_HAFTA)
    ih = _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 2, ih


def test_DEVRI_haftada_bir_ihlal_ilk_gece_gunune_yazilir():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    ih = _ih(g, _plan_gece_haftasi((2, 3, 4)), "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["gun"] == 2, ih


def test_DEVRI_azami_2_ikinci_gece_haftasi_SERBEST():
    """md. 8/3: iki haftalik nobetlesme."""
    g = _sahne([DEVRI_2], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_azami_2_ucuncu_gece_haftasi_IHLAL():
    g = _sahne([DEVRI_2], gecmis=_gece_haftasi(-2) + _gece_haftasi(-1),
               bilinen=IKI_HAFTA)
    ih = _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_DEVRI_azami_2_gece_gece_gunduz_GECE_yasak():
    """K-45: 'iki haftalik nobetlesme' G-G-D-D'dir; G-G-D-G dort haftada
    uc gece -> ihlal. Kesintisiz seriye bakan bir govde bunu kacirirdi."""
    g = _sahne([DEVRI_2], gecmis=_gece_haftasi(-3) + _gece_haftasi(-2)
               + _gunduz_haftasi(-1), bilinen=UC_HAFTA)
    ih = _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_DEVRI_azami_2_gece_gece_gunduz_gunduz_GECE_serbest():
    g = _sahne([DEVRI_2], gecmis=_gece_haftasi(-4) + _gece_haftasi(-3)
               + _gunduz_haftasi(-2) + _gunduz_haftasi(-1),
               bilinen=list(range(-28, 0)))
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_ust_sinir_2_ucu_KIRPAR_ve_bildirir():
    """K-45: 3 verilirse 2 uygulanir; sessiz gecmez (eksik_boyutlar)."""
    g = _sahne([DEVRI_3], gecmis=_gece_haftasi(-2) + _gece_haftasi(-1),
               bilinen=IKI_HAFTA)
    r = degerlendir(g, _plan_gece_haftasi())
    ih = [i for i in r["ihlaller"] if i["kural"] == "GECE_POSTASI_DEVRI"]
    assert len(ih) == 1 and ih[0]["gereken"] == 2, ih
    eb = [e for e in r["eksik_boyutlar"] if e["kural"] == "GECE_POSTASI_DEVRI"]
    assert len(eb) == 1 and "3" in eb[0]["sebep"] and "2" in eb[0]["sebep"], eb


def test_DEVRI_BILINMEYEN_hafta_kisit_yaratmaz():
    """K-42: gecmis hic yok -> gecen hafta gece haftasi sayilmaz."""
    assert not _ih(_sahne([DEVRI]), _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_DEVRI_YARIM_bilinen_hafta_gece_haftasi_SAYILMAZ():
    """K-42 + K-45: bes gece kayitli ama iki gun bilinmiyor -> cogunluk
    hesaplanamaz -> kisit yok. Kaydin yoklugundan kisit uretilmez."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=list(range(-7, -2)))
    assert not _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


# ----------------------------------------------------------------------
# 2. GECE POSTASI DEVRI -- K-42 raporu
# ----------------------------------------------------------------------

def test_K42_DEVRI_gecmis_yok_plan_gece_haftasi_RAPORLANIR():
    e = _eksik(_sahne([DEVRI]), _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["calisan"] == "C1" and e[0]["gun"] == -1, e


def test_K42_DEVRI_gecen_hafta_TAM_biliniyorsa_rapor_yok():
    g = _sahne([DEVRI], gecmis=[], bilinen=GECEN_HAFTA)
    assert not _eksik(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_plan_gece_haftasi_DEGILSE_rapor_yok():
    """Bu hafta iki gece uc gunduz -- gece haftasi degil; gecen haftanin
    ne oldugu sonucu degistiremez."""
    plan = [_p(0, GECE), _p(1, GECE), _p(2), _p(3), _p(4)]
    assert not _eksik(_sahne([DEVRI]), plan, "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_yarim_bilinen_hafta_RAPORLANIR():
    """Bes gece kayitli, iki gun bilinmiyor: kisit yok (ustte) ama sonucu
    degistirebilecek bilinmeyen gun var -> rapor, en son bilinmeyen gun."""
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=list(range(-7, -2)))
    e = _eksik(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_DEVRI_kanitli_ihlal_RAPORLANMAZ_ihlal_yazilir():
    g = _sahne([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    assert _ih(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert not _eksik(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


def test_K42_DEVRI_azami_2_onceki_hafta_BILINMIYORSA_raporlanir():
    """Gecen hafta gece (kanitli), ondan onceki iki hafta bilinmiyor:
    biri gece ise bu hafta ucuncu olur."""
    g = _sahne([DEVRI_2], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA)
    e = _eksik(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")
    assert len(e) == 1 and e[0]["gun"] == -8, e


def test_K42_DEVRI_azami_2_TEK_bilinmeyen_hafta_esige_yetmez_rapor_yok():
    """Pencere dort hafta: -1 ve -2 bilinen gunduz, -3 bilinmiyor. Kanitli
    0 + bilinmeyen 1 < 2 -> sonuc degisemez -> rapor YOK."""
    g = _sahne([DEVRI_2], gecmis=_gunduz_haftasi(-2) + _gunduz_haftasi(-1),
               bilinen=IKI_HAFTA)
    assert not _eksik(g, _plan_gece_haftasi(), "GECE_POSTASI_DEVRI")


# ======================================================================
# 3. ARDISIK HAFTA SONU LIMITI -- dogrulayici
# ======================================================================

def _hsonu(hafta, gunler=(5, 6)):
    return [_g(7 * hafta + d) for d in gunler]


def test_HSONU_govdesi_YAZILI():
    r = degerlendir(_sahne([HSONU]), [_p(5)])
    assert "ARDISIK_HAFTA_SONU_LIMIT" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


def test_HSONU_UCUNCU_tam_hafta_sonu_IHLAL():
    """Iki onceki hafta sonu iki gunu de calismis; bu hafta sonu iki gunu
    de -> ucuncu."""
    ih = _ih(_sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1)), [_p(5), _p(6)],
             "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1, ih
    assert ih[0]["olculen"] == 3 and ih[0]["gereken"] == 2, ih[0]
    assert ih[0]["gun"] == 5 and ih[0]["kabul_edilebilir"] is True, ih[0]


def test_HSONU_TEK_gun_calisilan_hafta_sonu_SAYILMAZ():
    """K-46: gecmis iki hafta sonu tam; bu hafta yalniz cumartesi -> hafta
    sonu 'calisilmis' degil -> ihlal yok. (Eski tanimda ihlaldi.)"""
    g = _sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1))
    assert not _ih(g, [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert not _ih(g, [_p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_gecmiste_TEK_gunlu_hafta_sonu_seriyi_KIRAR():
    g = _sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1, (5,)))
    assert not _ih(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_ikinci_hafta_sonu_SERBEST():
    assert not _ih(_sahne([HSONU], gecmis=_hsonu(-1)), [_p(5), _p(6)],
                   "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_arada_BOS_hafta_sonu_seriyi_KIRAR():
    g = _sahne([HSONU], gecmis=_hsonu(-2), bilinen=[-2, -1])
    assert not _ih(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_CUMA_gecesi_CUMARTESIDIR():
    """K-46: cuma 23:00-06:00'nin 6/7'si cumartesi. Cuma gecesi + pazar =
    tam hafta sonu."""
    # Cuma: -10 ve -3 (pazartesi -14/-7). -9 CUMARTESI olurdu -- ilk
    # yazimda oyleydi ve test yanlis sebeple kirmiziydi.
    g = _sahne([HSONU], gecmis=[_gece(-10), _g(-8), _gece(-3), _g(-1)])
    ih = _ih(g, [_p(4, GECE), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_HSONU_CUMA_aksami_CUMADIR():
    """Cuma 16:00-01:00: 9 saatin 1'i cumartesi -> cuma. Hafta sonu degil."""
    aksam = dict(GUNDUZ, id="V-CA", bas=16, bit=25)
    g = _sahne([HSONU], gecmis=[_g(-10, 16, 25), _g(-8), _g(-3, 16, 25), _g(-1)])
    g["vardiya_sablonlari"].append(aksam)
    assert not _ih(g, [_p(4, aksam), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_PAZAR_gecesi_PAZARTESIDIR():
    """Pazar 23:00-06:00 -> pazartesi; cumartesi + pazar gecesi tam hafta
    sonu DEGIL."""
    g = _sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1))
    assert not _ih(g, [_p(5), _p(6, GECE)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_CUMARTESI_gecesi_PAZARDIR():
    """Cumartesi 23:00-06:00 -> pazar. Cumartesi gunduz + cumartesi gecesi:
    ikisi ayri gun (cakisma yok) -> tam hafta sonu."""
    g = _sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1))
    ih = _ih(g, [_p(5), _p(5, GECE)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 3, ih


def test_HSONU_gecmisin_KENDI_serisi_plana_yazilmaz():
    g = _sahne([HSONU_1], gecmis=_hsonu(-2) + _hsonu(-1))
    assert not _ih(g, [_p(1)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_azami_1_ikinci_tam_hafta_sonu_IHLAL():
    ih = _ih(_sahne([HSONU_1], gecmis=_hsonu(-1)), [_p(5), _p(6)],
             "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 2, ih


def test_HSONU_BILINMEYEN_hafta_sonu_kisit_yaratmaz():
    assert not _ih(_sahne([HSONU_1]), [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_HSONU_gecmiste_yalniz_cumartesi_kayitli_PAZAR_bilinmiyor_SAYILMAZ():
    """K-42: pazar kaydi yok -> tam hafta sonu KANITLI degil -> kisit yok."""
    g = _sahne([HSONU_1], gecmis=_hsonu(-1, (5,)))
    assert not _ih(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


# ----------------------------------------------------------------------
# 4. ARDISIK HAFTA SONU -- K-42 raporu
# ----------------------------------------------------------------------

def test_K42_HSONU_gecmis_yok_plan_tam_hafta_sonu_RAPORLANIR():
    e = _eksik(_sahne([HSONU]), [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_HSONU_plan_TEK_gun_ise_rapor_yok():
    """Bu hafta sonu tam calisilmiyor -> gecmis sonucu degistiremez."""
    assert not _eksik(_sahne([HSONU]), [_p(5)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_K42_HSONU_gecen_hafta_sonu_BILINEN_bos_ise_rapor_yok():
    g = _sahne([HSONU], gecmis=[], bilinen=[-2, -1])
    assert not _eksik(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


def test_K42_HSONU_gecen_calisilmis_ONCEKI_bilinmiyor():
    g = _sahne([HSONU], gecmis=_hsonu(-1), bilinen=[-2, -1])
    e = _eksik(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -8, e


def test_K42_HSONU_hafta_sonunun_YARISI_biliniyor():
    """Cumartesi kayitli, pazar bilinmiyor -- pazar calismis olabilir."""
    g = _sahne([HSONU_1], gecmis=_hsonu(-1, (5,)))
    e = _eksik(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert len(e) == 1 and e[0]["gun"] == -1, e


def test_K42_HSONU_kanitli_ihlal_RAPORLANMAZ():
    g = _sahne([HSONU], gecmis=_hsonu(-2) + _hsonu(-1))
    assert _ih(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")
    assert not _eksik(g, [_p(5), _p(6)], "ARDISIK_HAFTA_SONU_LIMIT")


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


GECE_TALEBI = [(d, 23) for d in range(5)]        # bes gece: gece haftasi


def test_COZUCU_DEVRI_gecen_hafta_gece_haftasiysa_bu_hafta_gece_haftasi_YAZMAZ():
    """Tek kisi, gecen hafta bes gece (tam bilinen); bes gece talebini yalniz
    o karsilayabilir -> bu hafta gece haftasi olurdu -> cozumsuz ZORUNLU."""
    g = _cozucu_sahnesi([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
                        sablonlar=[GECE], talep=GECE_TALEBI)
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "gecen hafta gece haftasi olan kisiye bu hafta gece haftasi yazildi: %r"
        % c.get("atamalar"))


def test_COZUCU_DEVRI_gecmis_OLMADAN_ayni_sahne_cozulur():
    assert _cozuldu(_cozucu_sahnesi([DEVRI], sablonlar=[GECE], talep=GECE_TALEBI))


def test_COZUCU_DEVRI_gecen_hafta_GUNDUZ_ise_cozulur():
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gunduz_haftasi(-1), bilinen=GECEN_HAFTA,
        sablonlar=[GECE], talep=GECE_TALEBI))


def test_COZUCU_DEVRI_gecen_hafta_TEK_gece_ise_gece_haftasi_degil_cozulur():
    """K-45 cogunluk: bir gece dort gunduz gece haftasi degil."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gece_haftasi(-1, (0,)) + _gunduz_haftasi(-1, (1, 2, 3, 4)),
        bilinen=GECEN_HAFTA, sablonlar=[GECE], talep=GECE_TALEBI))


# ⚠ Karma haftali sahnelerde gunduz ile gece ARASINDA BOS GUN birakildi:
#   cozucu 11 saatlik dinlenmeyi kural yokken de VARSAYILAN olarak uygular
#   (VARDIYA_ARASI_DINLENME yazilmasa da). 08-16 gunduzun ardindan ayni gun
#   23:00 gecesi 7 saat ara demek; sahne kendiliginden cozumsuz olur ve
#   test bir sey olcmez. Ilk yazimda tam bu oldu -- karsi kanit yakaladi.
AZINLIK_GECE = [(0, 9), (1, 9), (2, 9), (4, 23), (5, 23)]      # 24 sa gunduz, 16 sa gece
COGUNLUK_GECE = [(0, 9), (1, 9), (3, 23), (4, 23), (5, 23)]    # 16 sa gunduz, 24 sa gece
TEK_GECE = [(0, 9), (1, 9), (2, 9), (4, 23)]


def test_COZUCU_DEVRI_bu_hafta_AZINLIK_gece_serbest():
    """Gecen hafta gece haftasi; bu hafta iki gece + uc gunduz talebi (tek
    kisi) -> gece azinlikta -> gece haftasi degil -> cozulur."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
        sablonlar=[GUNDUZ, GECE], talep=AZINLIK_GECE))


HAFTALIK_40 = _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=40)


def test_COZUCU_DEVRI_bu_hafta_COGUNLUK_gece_yasak():
    """⚠ T-54'un tuzagi burada da isirdi: fazladan atama BEDAVA. Ilk
    yazimda cozucu talepte olmayan bir gunduz vardiyasi daha ekleyip
    dengeyi 24-24'e getirdi ve 'gece haftasi degil' diye plani cozdu.
    Haftalik tavan (40 saat = bes vardiya) altinci vardiyayi kapatir;
    o zaman uc gece iki gunduz KACINILMAZ ve plan cozumsuz olmak zorunda."""
    g = _cozucu_sahnesi([DEVRI, HAFTALIK_40], gecmis=_gece_haftasi(-1),
                        bilinen=GECEN_HAFTA, sablonlar=[GUNDUZ, GECE],
                        talep=COGUNLUK_GECE)
    assert _coz(g)["durum"] != "cozuldu", "uc gece iki gunduz gece haftasidir"
    # Karsi kanit: sahne gecmissiz cozulur; cozumsuzlugun tek sebebi gecmis.
    assert _cozuldu(_cozucu_sahnesi([DEVRI, HAFTALIK_40],
                                    sablonlar=[GUNDUZ, GECE], talep=COGUNLUK_GECE))


def test_COZUCU_DEVRI_asgari_gece_ayari_EKLER():
    """Firma 'haftada 1 gece yeter' dediyse tek gece de yasak; ayar yokken
    ayni sahne cozulur (8 sa gece, 24 sa gunduz -- cogunluk degil)."""
    kural = _kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=1,
                   gece_haftasi_asgari_gece=1)
    g = _cozucu_sahnesi([kural], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
                        sablonlar=[GUNDUZ, GECE], talep=TEK_GECE)
    assert _coz(g)["durum"] != "cozuldu", "asgari gece ayari uygulanmadi"
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
        sablonlar=[GUNDUZ, GECE], talep=TEK_GECE))


def test_COZUCU_DEVRI_gecmis_hafta_SAAT_agirlikli():
    """Gecen hafta 2 gece (16 sa) + 3 kisa gunduz (12 sa): saatle gece
    haftasi, sayiyla degil. Bu hafta bes gece -> cozumsuz olmali."""
    gecmis = [_gece(-7), _gece(-6)] + [_g(d, 9, 13) for d in (-5, -4, -3)]
    g = _cozucu_sahnesi([DEVRI], gecmis=gecmis, bilinen=GECEN_HAFTA,
                        sablonlar=[GECE], talep=GECE_TALEBI)
    assert _coz(g)["durum"] != "cozuldu", "gecmis hafta vardiya sayisiyla olculdu"


def test_COZUCU_DEVRI_gecmis_hafta_TAM_YARISI_gece_haftasi_degil():
    """Gecen hafta 3 gece (24 sa) + 3 gunduz (24 sa): esit -> gece haftasi
    DEGIL -> bu hafta bes gece serbest."""
    gecmis = [_gece(d) for d in (-7, -6, -5)] + [_g(d) for d in (-4, -3, -2)]
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=gecmis, bilinen=GECEN_HAFTA,
        sablonlar=[GECE], talep=GECE_TALEBI))


def test_COZUCU_DEVRI_gecmis_kaydin_GECE_DEGIL_isareti_yasal_kurali_DELEMEZ():
    g = _cozucu_sahnesi([DEVRI], gecmis=[_gece(d, gece=False) for d in range(-7, -2)],
                        bilinen=GECEN_HAFTA, sablonlar=[GECE], talep=GECE_TALEBI)
    assert _coz(g)["durum"] != "cozuldu", (
        "`gece: false` isaretli 23-07 kayitlari yasal kuraldan kacti")


def test_COZUCU_DEVRI_gece_ISARETLI_aksam_sablonu_KISITLANMAZ():
    """16:00 talebini yalniz 15:15-24:00 kapatabilir; isaretli ama yasal
    olarak gece degil."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
        sablonlar=[AKSAM], talep=[(d, 16) for d in range(5)]))


def test_COZUCU_DEVRI_gece_DEGIL_isaretli_22_06_sablonu_KISITLANIR():
    g = _cozucu_sahnesi([DEVRI], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
                        sablonlar=[YANLIS_ISARET], talep=GECE_TALEBI)
    assert _coz(g)["durum"] != "cozuldu", (
        "gece degil isaretli 22:00-06:00 sablonu yasal kuraldan kacti")


def test_COZUCU_DEVRI_YARIM_bilinen_gecmis_hafta_kisit_yaratmaz():
    """K-42: bes gece kayitli ama iki gun bilinmiyor -> cogunluk yok."""
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI], gecmis=_gece_haftasi(-1), bilinen=list(range(-7, -2)),
        sablonlar=[GECE], talep=GECE_TALEBI))


def test_COZUCU_DEVRI_azami_2_ikinci_hafta_SERBEST():
    assert _cozuldu(_cozucu_sahnesi(
        [DEVRI_2], gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA,
        sablonlar=[GECE], talep=GECE_TALEBI))


def test_COZUCU_DEVRI_azami_2_ucuncu_hafta_YAZMAZ():
    g = _cozucu_sahnesi([DEVRI_2], gecmis=_gece_haftasi(-2) + _gece_haftasi(-1),
                        bilinen=IKI_HAFTA, sablonlar=[GECE], talep=GECE_TALEBI)
    assert _coz(g)["durum"] != "cozuldu", "ucuncu gece haftasi yazildi"


def test_COZUCU_DEVRI_azami_2_gece_gece_gunduz_GECE_yazmaz():
    g = _cozucu_sahnesi([DEVRI_2], gecmis=_gece_haftasi(-3) + _gece_haftasi(-2)
                        + _gunduz_haftasi(-1), bilinen=UC_HAFTA,
                        sablonlar=[GECE], talep=GECE_TALEBI)
    assert _coz(g)["durum"] != "cozuldu", "G-G-D-G dizisine izin verildi"


def test_COZUCU_DEVRI_azami_3_ikiye_KIRPILIR_ve_not_yazilir():
    g = _cozucu_sahnesi([DEVRI_3], gecmis=_gece_haftasi(-2) + _gece_haftasi(-1),
                        bilinen=IKI_HAFTA, sablonlar=[GECE], talep=GECE_TALEBI)
    c = _coz(g)
    assert c["durum"] != "cozuldu", "ust sinir 2 uygulanmadi"
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "GECE_POSTASI_DEVRI" in notlar and "2" in notlar, notlar


def test_UCTAN_UCA_DEVRI_cozucu_dogru_kisiyi_secer_denetci_onaylar():
    g = _cozucu_sahnesi([DEVRI], sablonlar=[GECE], talep=GECE_TALEBI)
    g["calisanlar"] = [
        _kisi("C1", gecmis=_gece_haftasi(-1), bilinen=GECEN_HAFTA),
        _kisi("C2", gecmis=_gunduz_haftasi(-1), bilinen=GECEN_HAFTA)]
    c = _coz(g)
    assert c["durum"] == "cozuldu", c.get("durum")
    c1 = sum(1 for a in c["atamalar"] if a["calisan"] == "C1")
    assert c1 <= 2, "gecen hafta gece haftasi olan C1 bu hafta yine gece haftasi"
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"]
                if i["kural"] == "GECE_POSTASI_DEVRI"], r["ihlaller"]


def test_COZUCU_HSONU_UCUNCU_tam_hafta_sonunu_YAZMAZ():
    """Iki hafta sonu tam kayitli; cumartesi ve pazar talebi tek kiside
    -> cozumsuz."""
    g = _cozucu_sahnesi([HSONU], gecmis=_hsonu(-2) + _hsonu(-1),
                        sablonlar=[GUNDUZ], talep=[(5, 8), (6, 8)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "ust uste ucuncu tam hafta sonu yazildi: %r" % c.get("atamalar"))


def test_COZUCU_HSONU_gecmis_OLMADAN_ayni_sahne_cozulur():
    assert _cozuldu(_cozucu_sahnesi([HSONU], sablonlar=[GUNDUZ],
                                    talep=[(5, 8), (6, 8)]))


def test_COZUCU_HSONU_TEK_gun_talebi_serbest():
    """K-46: iki hafta sonu tam kayitli; bu hafta yalniz cumartesi -> olur."""
    assert _cozuldu(_cozucu_sahnesi([HSONU], gecmis=_hsonu(-2) + _hsonu(-1),
                                    sablonlar=[GUNDUZ], talep=[(5, 8)]))


def test_COZUCU_HSONU_ikinci_hafta_sonu_SERBEST():
    assert _cozuldu(_cozucu_sahnesi([HSONU], gecmis=_hsonu(-1),
                                    sablonlar=[GUNDUZ], talep=[(5, 8), (6, 8)]))


def test_COZUCU_HSONU_gecmiste_tek_gunlu_hafta_sonu_seriyi_KIRAR():
    assert _cozuldu(_cozucu_sahnesi([HSONU], gecmis=_hsonu(-2) + _hsonu(-1, (6,)),
                                    sablonlar=[GUNDUZ], talep=[(5, 8), (6, 8)]))


def test_COZUCU_HSONU_CUMA_gecesi_CUMARTESIDIR():
    """Cuma gecesi + pazar gunduzu tam hafta sonu: gecmis iki tam hafta
    sonuysa yasak. Talep: cuma 23:00 ve pazar 08:00, tek kisi."""
    g = _cozucu_sahnesi([HSONU], gecmis=_hsonu(-2) + _hsonu(-1),
                        sablonlar=[GUNDUZ, GECE], talep=[(4, 23), (6, 8)])
    assert _coz(g)["durum"] != "cozuldu", "cuma gecesi cumartesi sayilmadi"


def test_COZUCU_HSONU_CUMA_aksami_CUMADIR():
    """Cuma 16:00-01:00 (1 sa cumartesiye tasar) + pazar: cuma aksami
    cumadir, tam hafta sonu degil -> cozulur. En ufak tasmayi ertesi gune
    yazan bir govde bunu yasaklardi."""
    aksam = dict(GUNDUZ, id="V-CA", bas=16, bit=25)
    assert _cozuldu(_cozucu_sahnesi(
        [HSONU], gecmis=_hsonu(-2) + _hsonu(-1),
        sablonlar=[GUNDUZ, aksam], talep=[(4, 16), (6, 8)]))


def test_IKI_TARAF_hafta_sonu_gununu_AYNI_siniflar():
    """#7.6: cogunluk gunu iki tarafta ayri yazili; ayni sonuca varmali.
    Adaletin hafta sonu boyutu da (iki tarafta) bu tanimi kullanir."""
    from cozucu import model
    from dogrulayici import kurallar
    m = model.Model(_cozucu_sahnesi([HSONU], sablonlar=[GUNDUZ, GECE]))
    sayac = m._boyut_sayaci("hafta_sonu")
    beklenen = [(GUNDUZ, 4, False), (GECE, 4, True), (GUNDUZ, 5, True),
                (GECE, 5, True), (GECE, 6, False), (GUNDUZ, 6, True),
                (dict(GUNDUZ, bas=16, bit=25), 4, False)]
    for t, d, hs in beklenen:
        assert sayac(t, d) is hs, ("cozucu", t["bas"], t["bit"], d)
        a = {"gun": d, "bas": t["bas"], "bit": t["bit"], "molalar": []}
        assert (kurallar._hafta_sonu_gunu(a) is not None) is hs, ("dogrulayici", t, d)


def test_COZUCU_HSONU_PAZAR_gecesi_PAZARTESIDIR():
    """Cumartesi gunduz + pazar gecesi: pazar gecesi pazartesidir -> tam
    hafta sonu degil -> cozulur."""
    assert _cozuldu(_cozucu_sahnesi(
        [HSONU], gecmis=_hsonu(-2) + _hsonu(-1),
        sablonlar=[GUNDUZ, GECE], talep=[(5, 8), (6, 23)]))


def test_COZUCU_HSONU_gecmiste_cuma_gecesi_CUMARTESI_sayilir():
    """Gecmiste cuma gecesi + pazar = tam hafta sonu (iki hafta) -> bu
    hafta cumartesi + pazar yasak."""
    g = _cozucu_sahnesi([HSONU], gecmis=[_gece(-10), _g(-8), _gece(-3), _g(-1)],
                        sablonlar=[GUNDUZ], talep=[(5, 8), (6, 8)])
    assert _coz(g)["durum"] != "cozuldu"


def test_COZUCU_HSONU_azami_1_BILINMEYEN_hafta_sonu_kisit_yaratmaz():
    assert _cozuldu(_cozucu_sahnesi([HSONU_1], sablonlar=[GUNDUZ],
                                    talep=[(5, 8), (6, 8)]))


def test_COZUCU_HSONU_azami_1_gecen_tam_hafta_sonu_calisana_YAZMAZ():
    g = _cozucu_sahnesi([HSONU_1], gecmis=_hsonu(-1), sablonlar=[GUNDUZ],
                        talep=[(5, 8), (6, 8)])
    assert _coz(g)["durum"] != "cozuldu"


def test_UCTAN_UCA_HSONU_cozucu_dogru_kisiyi_secer_denetci_onaylar():
    g = _cozucu_sahnesi([HSONU], sablonlar=[GUNDUZ], talep=[(5, 8), (6, 8)])
    g["calisanlar"] = [
        _kisi("C1", gecmis=_hsonu(-2) + _hsonu(-1), bilinen=IKI_HAFTA),
        _kisi("C2", gecmis=_hsonu(-2), bilinen=IKI_HAFTA)]
    c = _coz(g)
    assert c["durum"] == "cozuldu", c.get("durum")
    c1 = {a["gun"] for a in c["atamalar"] if a["calisan"] == "C1"}
    assert not ({5, 6} <= c1), "C1'e ucuncu tam hafta sonu yazildi"
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"]
                if i["kural"] == "ARDISIK_HAFTA_SONU_LIMIT"], r["ihlaller"]


# ======================================================================
# 6. IKI ASAMA -- cozucunun ciktisi gecmis olunca gece postasi devri
# ======================================================================
#
# Mustafa'nin yolu (30 Eylul): once bir hafta, sonra onun sonucunu gecmis
# sayarak ikinci hafta. Burada sinanan BORU HATTI: gun - 7 donusumu, tam
# bilinen hafta, cogunluk hesabi. Hafta 1'de C1 bes gece SABIT; hafta 2'de
# gece talebini yalniz C1 karsilayabilir (C2 gece calisamaz).

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
            kisi.setdefault(a["calisan"], []).append(k)
        for c in g["calisanlar"]:
            c["gecmis_vardiyalar"] = kisi.get(c["id"], [])
            c["gecmis_bilinen_gunler"] = GECEN_HAFTA
    return g


def test_IKI_ASAMA_hafta_1in_gece_haftasi_hafta_2de_geceyi_KAPATIR():
    h1 = _coz(_iki_asama(talep=GECE_TALEBI,
                         sabit=[{"calisan": "C1", "gun": d, "sablon": GECE["id"]}
                                for d in range(5)]))
    assert h1["durum"] == "cozuldu", h1.get("durum")
    geceler = sorted(a["gun"] for a in h1["atamalar"]
                     if a["calisan"] == "C1" and a["sablon"] == GECE["id"])
    assert geceler == [0, 1, 2, 3, 4], h1["atamalar"]

    h2 = _coz(_iki_asama(talep=GECE_TALEBI, gecmis_atamalar=h1["atamalar"]))
    assert h2["durum"] != "cozuldu", (
        "hafta 1'de gece haftasi calisan tek gececiye hafta 2'de gece "
        "haftasi yazildi: %r" % h2.get("atamalar"))


def test_IKI_ASAMA_gecmis_OLMADAN_hafta_2_cozulur():
    assert _cozuldu(_iki_asama(talep=GECE_TALEBI))
