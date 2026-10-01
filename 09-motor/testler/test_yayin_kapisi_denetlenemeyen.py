# -*- coding: utf-8 -*-
"""
YAYIN KAPISI -- "BAKAMADIM" DA KAPIDAN GECEMEZ (T-18, K-49)

NE VARDI (16 Eylul dis incelemesi, T-18)
  Dogrulayiciya govdesi yazilmamis ama aktif ve SERT bir kural verildiginde
  cevap ayni anda sunlari soyluyordu:

      uygulanmayan_kurallar : ['GECE_VARDIYASI_AZAMI']
      sert_ihlal            : 0
      YAYINLANABILIR        : True

  "Bu kurali kontrol edemedim" ile "yayinlayabilirsin" ayni cevapta. Ilke
  denetle.py'nin basinda yaziliydi, kapiya bagli degildi.

KARAR (K-49, 1 Ekim, Mustafa): uc kademe
  SERT + yasal  -> engeller (firma yasal kontrolu onaylayarak gecemez)
  SERT + firma  -> kabul bekler (yetkili gerekceyle kabul eder)
  YUMUSAK       -> yalniz rapor

  Iki kanal kapiya baglandi: `uygulanmayan_kurallar` (govdesi yok) ve
  `eksik_boyutlar` icinde `denetlenemedi: True` olanlar (yazilmis kuralin
  bakilamayan parcasi). GECE_POSTASI_DEVRI'nin kirpma raporu (K-45) kurali
  DENETLEDIGI icin `denetlenemedi: False` -- kapiyi etkilemez.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_yayin_kapisi_denetlenemeyen.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402
from dogrulayici.denetle import yayin_kapisi                   # noqa: E402

GUNDUZ = {"id": "V", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60}
YAZILMAMIS = "BOYLE_BIR_KURAL_YOK"      # KAYIT'ta govdesi olmayan kod


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(kurallar, kabul=None):
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": "C1", "ekipler": ["E"],
                         "sozlesme": {"tip": "tam_zamanli"},
                         "izinler": [], "uygunluk": []}],
         "vardiya_sablonlari": [GUNDUZ], "talep": [],
         "kurallar": list(kurallar), "kilitler": [], "donmus_gunler": []}
    if kabul is not None:
        g["denetim_disi_kabul"] = kabul
    return g


PLAN = [{"calisan": "C1", "ekip": "E", "sablon": "V", "gun": 0,
         "bas": 8, "bit": 16, "molalar": [{"bas": 12, "bit": 13, "tip": "yemek"}]}]


def _kapi(kurallar, kabul=None):
    r = degerlendir(_sahne(kurallar, kabul), PLAN)
    assert not r["ihlaller"], r["ihlaller"]        # sahne ihlalsiz; kapi yalniz "bakamadim"a bakiyor
    return r


# ----------------------------------------------------------------------
# 1. Govdesi yazilmamis kural
# ----------------------------------------------------------------------

def test_SERT_YASAL_govdesiz_kural_yayini_ENGELLER():
    r = _kapi([_kural(YAZILMAMIS, yasal=True)])
    assert r["uygulanmayan_kurallar"] == [YAZILMAMIS]
    k = r["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert k["kabul_secenegi_sunulur"] is False
    assert [d["etki"] for d in k["denetlenemeyen_kurallar"]] == ["engelliyor"]
    assert "yasal" in k["denetlenemeyen_kurallar"][0]["mesaj"].lower()


def test_SERT_FIRMA_govdesiz_kural_KABUL_BEKLER():
    k = _kapi([_kural(YAZILMAMIS)])["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert k["kabul_secenegi_sunulur"] is True
    assert [d["etki"] for d in k["denetlenemeyen_kurallar"]] == ["kabul_bekliyor"]


def test_SERT_FIRMA_gerekceli_kabul_yayini_ACAR():
    k = _kapi([_kural(YAZILMAMIS)],
              kabul=[{"kod": YAZILMAMIS, "gerekce": "bu donem elle kontrol edildi",
                      "onaylayan": "vardiya muduru"}])["yayin_kapisi"]
    assert k["yayinlanabilir"] is True
    d = k["denetlenemeyen_kurallar"][0]
    assert d["etki"] == "kabul_edildi" and d["kabul"]["onaylayan"] == "vardiya muduru"


def test_GEREKCESIZ_kabul_kabul_DEGILDIR():
    k = _kapi([_kural(YAZILMAMIS)],
              kabul=[{"kod": YAZILMAMIS, "gerekce": "  ", "onaylayan": "x"}])["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert k["denetlenemeyen_kurallar"][0]["etki"] == "kabul_bekliyor"


def test_YASAL_kural_kabulle_ACILAMAZ():
    """K-18/K-20: firma yasal kontrolu onaylayarak gecemez."""
    k = _kapi([_kural(YAZILMAMIS, yasal=True)],
              kabul=[{"kod": YAZILMAMIS, "gerekce": "olsun", "onaylayan": "x"}])["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert k["denetlenemeyen_kurallar"][0]["etki"] == "engelliyor"


def test_YUMUSAK_govdesiz_kural_yalniz_RAPOR():
    k = _kapi([_kural(YAZILMAMIS, tur="YUMUSAK")])["yayin_kapisi"]
    assert k["yayinlanabilir"] is True
    assert [d["etki"] for d in k["denetlenemeyen_kurallar"]] == ["rapor"]


def test_PASIF_govdesiz_kural_kapiyi_ETKILEMEZ():
    r = _kapi([dict(_kural(YAZILMAMIS, yasal=True), aktif=False)])
    assert r["uygulanmayan_kurallar"] == []
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


# ----------------------------------------------------------------------
# 2. Yazilmis kuralin bakilamayan parcasi (eksik_boyutlar)
# ----------------------------------------------------------------------

def test_PARAMETRESIZ_yetkinlik_kurali_KABUL_BEKLER():
    """YETKINLIK_KAPSAMASI gereklilik satirsiz: govde bos liste donuyor
    ('ihlal yok' gibi). Artik kapi 'bakamadim' der."""
    r = _kapi([_kural("YETKINLIK_KAPSAMASI")])
    assert any(e["kural"] == "YETKINLIK_KAPSAMASI" and e.get("denetlenemedi")
               for e in r["eksik_boyutlar"]), r["eksik_boyutlar"]
    k = r["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    d = k["denetlenemeyen_kurallar"][0]
    assert d["etki"] == "kabul_bekliyor" and d["parca"] == "yetkinlik"


def test_KIRPMA_raporu_kapiyi_ETKILEMEZ():
    """GECE_POSTASI_DEVRI azami 3 -> 2 uygulandi (K-45). Kural DENETLENDI;
    rapor kirpma raporudur, 'bakamadim' degil."""
    r = _kapi([_kural("GECE_POSTASI_DEVRI", yasal=True, azami_ardisik_gece_haftasi=3)])
    assert any(e["kural"] == "GECE_POSTASI_DEVRI" and e.get("denetlenemedi") is False
               for e in r["eksik_boyutlar"]), r["eksik_boyutlar"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True
    assert r["yayin_kapisi"]["denetlenemeyen_kurallar"] == []


def test_ADALET_saat_boyutu_YUMUSAK_rapor():
    r = _kapi([_kural("ADALET_DENGESI", tur="YUMUSAK", boyutlar=["gece", "saat"])])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True
    assert [d["etki"] for d in r["yayin_kapisi"]["denetlenemeyen_kurallar"]] == ["rapor"]


# ----------------------------------------------------------------------
# 3. Eski cagri bicimi ve karisik durumlar
# ----------------------------------------------------------------------

def test_kapi_ESKI_cagri_bicimiyle_ayni_davranir():
    k = yayin_kapisi([{"kural": "ROL_KAPSAMASI", "agirlik": "SERT",
                       "yasal": False, "kabul_edilebilir": True}])
    assert k["yayinlanabilir"] is False and k["kabul_secenegi_sunulur"] is True
    assert k["denetlenemeyen_kurallar"] == []


def test_engelleyen_denetlenemeyen_varken_kabul_secenegi_SUNULMAZ():
    k = _kapi([_kural(YAZILMAMIS, yasal=True), _kural(YAZILMAMIS + "_2")])["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert k["kabul_secenegi_sunulur"] is False
    assert sorted(d["etki"] for d in k["denetlenemeyen_kurallar"]) == ["engelliyor", "kabul_bekliyor"]


def test_her_satirda_okunur_CUMLE_var():
    k = _kapi([_kural(YAZILMAMIS, yasal=True), _kural("YETKINLIK_KAPSAMASI")])["yayin_kapisi"]
    for d in k["denetlenemeyen_kurallar"]:
        assert d["kod"] in d["mesaj"] and "denetlenemedi" in d["mesaj"], d
