# -*- coding: utf-8 -*-
"""
GECE TESPITI -- isaretsiz vardiyanin tahmini (T-69) ve adalet dengesinin
"gece" boyutu (T-71)

NE VARDI
  T-69: `gece_vardiyasi` isareti YOKSA iki motor yarisi da vardiyayi yalniz
        AYNI GUNUN 20:00-06:00 penceresine bakarak tahmin ediyordu. Onceki
        gecenin 00:00-06:00 kismi gorunmuyordu:
            00:00-08:45 -> "gece degil"   (6 saati gece doneminde)
        Ve tersi: pencereye EN UFAK degen vardiya "gece" sayiliyordu:
            13:00-21:00 -> "gece"         (1 saati gece doneminde)
        Ikisi tutarli, ikisi de yanlis (T-19 ailesi). PDKS kaydinda isaret
        OLMAYACAK -- gecmis kayitlar hep bu tahminden gecer.
  T-71: dogrulayicida ADALET_DENGESI'nin "gece" boyutu K-40 isaretini hic
        okumuyordu; "herhangi bir parcasi 20:00-06:00'ya degiyorsa gece"
        diyordu. Cozucu isareti okuyordu. K-40'in kaydindaki "iki yerde iki
        gece tanimi kalmadi" cumlesi yarisi dogruydu.

NE OLDU (30 Eylul aksami)
  Isaret yoksa tahmin YONETMELIGIN KENDI TANIMINA dayanir -- Postalar Yon.
  md. 7/2: "Calisma suresinin yarisindan cogu gece donemine rastlayan bir
  postanin calismasi, gece calismasi sayilir." Ayni olcu gece postasi
  devrinde (yasal kural) zaten kullaniliyor.

  ⚠ ISARET HALA TAHMINI EZER (K-40). Bu dosya yalniz ISARETSIZ vardiyayi
    ve dogrulayicinin adalet boyutunu ilgilendirir. Isaretli sablonlarin
    sonucu degismez -- veri setinde butun sablonlar isaretli.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_gece_tespiti.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                           # noqa: E402


def _sablon(kimlik, bas, bit, isaret=None):
    t = {"id": kimlik, "ekip": "E", "bas": bas, "bit": bit, "mola_dk": 0}
    if isaret is not None:
        t["gece_vardiyasi"] = isaret
    return t


ERKEN = _sablon("V-ERKEN", 0, 8.75)          # 6 / 8,75 gece doneminde
OGLEN = _sablon("V-OGLEN", 13, 21)           # 1 / 8
AKSAM_YARI = _sablon("V-AKSAM", 16, 24)      # 4 / 8 -- tam yari
GEC = _sablon("V-GEC", 18, 26)               # 6 / 8
GECE = _sablon("V-GECE", 23, 31)             # 7 / 8
SABAH = _sablon("V-SABAH", 5, 13)            # 1 / 8

BEKLENEN = [(ERKEN, True), (OGLEN, False), (AKSAM_YARI, False), (GEC, True),
            (GECE, True), (SABAH, False)]


def _kural(kod, **par):
    k = {"kod": kod, "tur": "SERT", "aktif": True, "yasal": False,
         "kabul_edilebilir": False}
    if par:
        k["parametreler"] = par
    return k


def _kisi(kimlik, **ek):
    c = {"id": kimlik, "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    c.update(ek)
    return c


def _sahne(sablonlar, kurallar, kisiler=None, talep=()):
    return {"profil": "DENGELI",
            "calisanlar": kisiler or [_kisi("C1", gece_calisamaz=True)],
            "vardiya_sablonlari": list(sablonlar),
            "talep": [{"ekip": "E", "gun": d, "saat": h, "asgari": 1,
                       "hedef": 1} for d, h in talep],
            "kurallar": list(kurallar), "kilitler": [], "donmus_gunler": []}


def _p(gun, t, kimlik="C1"):
    return {"calisan": kimlik, "ekip": "E", "sablon": t["id"], "gun": gun,
            "bas": t["bas"], "bit": t["bit"], "molalar": []}


def _ih(g, plan, kod):
    return [i for i in degerlendir(g, plan)["ihlaller"] if i["kural"] == kod]


def _coz(g):
    from cozucu.coz import coz
    return coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})


UYGUNLUK = _kural("GECE_UYGUNLUGU")


# ----------------------------------------------------------------------
# 1. Iki taraf ayni siniflamayi yapiyor mu -- dogrudan
# ----------------------------------------------------------------------

def test_IKI_TARAF_isaretsiz_sablonu_AYNI_siniflar():
    """#7.6: iki taraf ayri yazilir ama AYNI sonuca varmali. Bu test ikisini
    yan yana koyar -- biri kayarsa burada gorunur."""
    from cozucu import model
    from dogrulayici import kurallar
    for t, gece in BEKLENEN:
        c = model._gece_sablonu(t)
        d = kurallar._gece_sablonu(t)
        assert c == (gece, True), ("cozucu", t["id"], c)
        assert d == (gece, True), ("dogrulayici", t["id"], d)


def test_ISARET_tahmini_EZER_iki_tarafta_da():
    from cozucu import model
    from dogrulayici import kurallar
    for t, gece in BEKLENEN:
        ters = dict(t, gece_vardiyasi=not gece)
        assert model._gece_sablonu(ters) == (not gece, False), t["id"]
        assert kurallar._gece_sablonu(ters) == (not gece, False), t["id"]


# ----------------------------------------------------------------------
# 2. T-69 -- sabah erken vardiya
# ----------------------------------------------------------------------

def test_DOGRULAYICI_gece_calisamayana_isaretsiz_00_08_IHLAL():
    g = _sahne([ERKEN], [UYGUNLUK])
    assert _ih(g, [_p(1, ERKEN)], "GECE_UYGUNLUGU"), (
        "00:00-08:45 gece sayilmadi (T-69)")


def test_COZUCU_gece_calisamayana_isaretsiz_00_08_YAZMAZ():
    """Tek kisi, gece calisamiyor; 02:00 talebini yalniz 00:00-08:45
    kapatabilir -> cozumsuz kalmak ZORUNDA."""
    g = _sahne([ERKEN], [_kural("ASGARI_KAPSAMA"), UYGUNLUK], talep=[(1, 2)])
    assert _coz(g)["durum"] != "cozuldu", "00:00-08:45 gece sayilmadi (T-69)"


def test_PDKS_kaydi_00_08_ardisik_geceye_SAYILIR():
    """Gecmis kaydinda isaret yok. Pazar 00:00-08:00 + pazartesi-carsamba
    gecesi = dort gece ust uste."""
    c = _kisi("C1", gecmis_vardiyalar=[{"gun": -1, "bas": 0, "bit": 8}],
              gecmis_bilinen_gunler=[-1])
    g = _sahne([GECE], [_kural("ARDISIK_GECE_LIMIT", azami_gece=3)],
               kisiler=[c])
    ih = _ih(g, [_p(d, GECE) for d in (0, 1, 2)], "ARDISIK_GECE_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 4, ih


# ----------------------------------------------------------------------
# 3. Tahmin "en ufak degme" degil, "yarisindan cogu"
# ----------------------------------------------------------------------

def test_DOGRULAYICI_13_21_gece_DEGIL():
    """Eskiden 20:00-21:00 yuzunden 'gece' sayiliyordu ve gece calisamayan
    birine 13:00-21:00 verilemiyordu."""
    g = _sahne([OGLEN], [UYGUNLUK])
    assert not _ih(g, [_p(1, OGLEN)], "GECE_UYGUNLUGU")


def test_COZUCU_13_21_gece_calisamayana_VERILEBILIR():
    g = _sahne([OGLEN], [_kural("ASGARI_KAPSAMA"), UYGUNLUK], talep=[(1, 14)])
    assert _coz(g)["durum"] == "cozuldu", "13:00-21:00 hala gece sayiliyor"


def test_tam_YARISI_gece_sayilmaz_16_24():
    g = _sahne([AKSAM_YARI], [UYGUNLUK])
    assert not _ih(g, [_p(1, AKSAM_YARI)], "GECE_UYGUNLUGU")


def test_yarisindan_COGU_gece_sayilir_18_02():
    g = _sahne([GEC], [UYGUNLUK])
    assert _ih(g, [_p(1, GEC)], "GECE_UYGUNLUGU")


# ----------------------------------------------------------------------
# 4. T-71 -- adalet dengesinin "gece" boyutu isareti okur
# ----------------------------------------------------------------------

ADALET = {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
          "yasal": False, "parametreler": {"boyutlar": ["gece"],
                                           "adaletsizlik_esigi": 2}}


def _adalet_sahnesi(sablon):
    kisiler = [_kisi("C%d" % i) for i in (1, 2, 3)]
    g = _sahne([sablon], [ADALET], kisiler=kisiler)
    plan = [_p(d, sablon, "C1") for d in (0, 1, 2)]
    return g, plan


def test_ADALET_gece_DEGIL_isaretli_aksam_gece_SAYILMAZ():
    """Veri setindeki S-AKSAM gibi: 13:45-23:00, firma 'gece degil' diyor.
    C1'e uc tane -> ortalamadan 2 fazla; gece sayilirsa ihlal yazilir."""
    aksam = _sablon("V-S-AKSAM", 13.75, 23, isaret=False)
    g, plan = _adalet_sahnesi(aksam)
    assert not _ih(g, plan, "ADALET_DENGESI"), (
        "firmanin 'gece degil' dedigi vardiya adalette gece sayildi (T-71)")


def test_ADALET_gece_ISARETLI_vardiya_SAYILIR():
    """Karsi kanit: ayni sahne, isaretli gece -> ihlal."""
    g, plan = _adalet_sahnesi(_sablon("V-G", 23, 31, isaret=True))
    ih = _ih(g, plan, "ADALET_DENGESI")
    assert len(ih) == 1 and ih[0]["calisan"] == "C1", ih


# ⚠ Yukaridaki S-AKSAM testi ISARETI OKUMAYAN bir govdeyi de gecirir: yeni
#   tahmin (md. 7/2) 13:45-23:00'u zaten gece saymiyor. Mutasyon yakaladi --
#   isaret yok sayildiginda o test yesil kaldi. Isaretin GERCEKTEN okundugunu
#   yalniz isaretle tahminin AYRISTIGI vardiya kanitlar:

def test_ADALET_ISARET_gece_degil_diyorsa_22_06_SAYILMAZ():
    """Tahmin 'gece' der (8/8), firma 'gece degil' der -- firma kurali
    firmanin tanimini kullanir (K-40)."""
    g, plan = _adalet_sahnesi(_sablon("V-22", 22, 30, isaret=False))
    assert not _ih(g, plan, "ADALET_DENGESI"), (
        "firmanin 'gece degil' isareti adalet boyutunda okunmadi")


def test_ADALET_ISARET_gece_diyorsa_15_24_SAYILIR():
    """Tahmin 'gece degil' der (4/8,75 -- veri setindeki B-AKSAM), firma
    'gece' der."""
    g, plan = _adalet_sahnesi(_sablon("V-B-AKSAM", 15.25, 24, isaret=True))
    assert _ih(g, plan, "ADALET_DENGESI"), (
        "firmanin 'gece' isareti adalet boyutunda okunmadi")


def test_ADALET_isaretsiz_sabah_ERKEN_vardiya_SAYILIR():
    g, plan = _adalet_sahnesi(ERKEN)
    assert _ih(g, plan, "ADALET_DENGESI"), "00:00-08:45 adalette gece sayilmadi"
