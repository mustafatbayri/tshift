# -*- coding: utf-8 -*-
"""
KALITE OLCUMUNUN IKI ARACI: AMAC DAGILIMI VE IYILESME EGRISI (T-60, 2 Ekim)

NEDEN
  `optimuma_uzaklik_yuzde` tek bir sayi ve iki soruya cevap vermiyor:
    1. Amac NEYDEN olusuyor? Hedef altinda kalan hucre mi, adalet mi,
       mola mi, fazla mesai mi? Bilinmeden "plan kotu" ile "kapasite
       yetmiyor" ayrilamaz.
    2. Plan NE ZAMAN iyilesti? Son 10 saniyede mi, ilk 30 saniyede mi?
       Bilinmeden "daha uzun sure ver" onerisinin dayanagi yok.
  Bu iki alan artik `cozum_istatistikleri` icinde donuyor:
    amac_dagilimi : kural -> {ceza, deger, degisken, pay_yuzde}
    iyilesme      : ilk/son amac, %50/%90/%99 saniyeleri, inceltilmis egri

SINANAN
  - Dagilimin kurallara gore toplami amac degerinin KENDISIDIR (ne eksik
    ne fazla); paylar 100'e toplanir; anahtarlar kural ADIDIR (he_ degil).
  - Egri ozeti: esikler, inceltme (son nokta korunur), bos egri -> None,
    hic iyilesmeyen egri -> esikler 0.
  - Plan yoksa (sure yetmedi) dagilim None, egri None -- "0" yazilmaz.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_kalite_olcumu.py -v
"""

import os
import sys

import pytest
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
# Paket `cozucu.coz` adini FONKSIYONA veriyor (__init__); modulun kendisi
# sys.modules'tan alinir.
C = sys.modules["cozucu.coz"]

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 3, "iki_asama_esigi": 10 ** 9}


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sahne():
    """Iki kisi, tek sablon 08-16, gun 0-1'de hedef 3 (asgari 1): hedef
    HICBIR zaman tutmaz -> HEDEF_KAPSAMA cezasi kesin > 0. Gun 2'de hedef 1
    asgari 0: kisi koymak HEDEF_ASIMI'na girmez, koymamak hedef eksigi.
    Boylece dagilimda en az iki kural gorunur."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
            {"id": "C2", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
        ],
        "vardiya_sablonlari": [
            {"id": "T08", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60, "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
        ],
        "talep": ([{"ekip": "E", "gun": g, "saat": s, "asgari": 1, "hedef": 3}
                   for g in (0, 1) for s in range(8, 16)]
                  + [{"ekip": "E", "gun": 2, "saat": s, "asgari": 0, "hedef": 1}
                     for s in range(8, 16)]),
        "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                     _kural("HEDEF_ASIMI", "YUMUSAK"), _kural("CAKISMA_YOK"),
                     _kural("SAAT_DENGESI", "YUMUSAK")],
        "kilitler": [], "donmus_gunler": [],
    }


# ---- amac dagilimi ------------------------------------------------------

def test_dagilim_toplami_amac_degerinin_kendisidir():
    c = coz(_sahne(), AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    ist = c["cozum_istatistikleri"]
    d = ist["amac_dagilimi"]
    assert d, ist
    assert sum(v["ceza"] for v in d.values()) == ist["amac_degeri"], (d, ist["amac_degeri"])
    assert abs(sum(v["pay_yuzde"] for v in d.values()) - 100.0) < 0.5, d
    # Anahtar kural ADI, degisken oneki degil.
    assert set(d) <= set(C._CEZA_ONEKI.values()), set(d)
    assert "HEDEF_KAPSAMA" in d and d["HEDEF_KAPSAMA"]["ceza"] > 0, d
    # Gun 0-1'de 16 hucre, hedef 3, en cok 2 kisi var: hucre basina en az 1
    # kisi eksik = en az 16 kisi-saat eksik hedef. `deger` ham toplamdir
    # (agirliksiz); `ceza` agirlikli.
    assert d["HEDEF_KAPSAMA"]["deger"] >= 16, d
    assert d["HEDEF_KAPSAMA"]["ceza"] >= d["HEDEF_KAPSAMA"]["deger"], d
    # Ceza vermeyen kural da gorunur (degisken sayisiyla): "modellendi ama
    # bedeli sifir" ile "hic modellenmedi" ayrilsin.
    assert "HEDEF_ASIMI" in d and d["HEDEF_ASIMI"]["degisken"] == 24, d
    # Buyukten kucuge sirali.
    cezalar = [v["ceza"] for v in d.values()]
    assert cezalar == sorted(cezalar, reverse=True), cezalar
    # Her kayit uc sayac + pay tasir.
    for v in d.values():
        assert set(v) == {"ceza", "deger", "degisken", "pay_yuzde"}, v
        assert v["degisken"] > 0


def test_dagilim_yumusak_kural_yoksa_butun_cezalar_sifir():
    """Yumusak kural yoksa amac 0'dir; dagilim None DEGIL (plan var), her
    kaydin cezasi 0. (Fazla mesai degiskeni kural olmasa da kurulur; sifir
    ceza ile gorunmesi dogru: modellendi, bedeli yok.)"""
    g = _sahne()
    g["kurallar"] = [_kural("ASGARI_KAPSAMA"), _kural("CAKISMA_YOK")]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    d = ist["amac_dagilimi"]
    assert d is not None and all(v["ceza"] == 0 for v in d.values()), d
    assert ist["amac_degeri"] == 0
    assert "HEDEF_KAPSAMA" not in d and "SAAT_DENGESI" not in d, d


# ---- iyilesme egrisi ----------------------------------------------------

def test_egri_ozeti_esikler_ve_son_nokta():
    # 100 -> 0: %50'ye 2. sn'de, %90'a 5. sn'de, %99'a 9. sn'de ulasilir.
    egri = [(0.5, 100, 0), (2.0, 50, 0), (3.0, 30, 0), (5.0, 10, 0),
            (7.0, 2, 0), (9.0, 1, 0), (12.0, 0, 0)]
    o = C._iyilesme_ozeti(egri)
    assert o["ilk_amac"] == 100 and o["son_amac"] == 0 and o["cozum"] == 7
    assert o["yuzde50_sn"] == 2.0 and o["yuzde90_sn"] == 5.0 and o["yuzde99_sn"] == 9.0, o
    assert o["son_iyilesme_sn"] == 12.0 and o["alt_sinir_son"] == 0
    assert o["egri"][-1] == [12.0, 0, 0]


def test_egri_inceltme_son_noktayi_korur():
    egri = [(round(i * 0.1, 2), 1000 - i, 0) for i in range(500)]
    o = C._iyilesme_ozeti(egri, nokta=40)
    assert len(o["egri"]) <= 41, len(o["egri"])
    assert o["egri"][0] == [0.0, 1000, 0]
    assert o["egri"][-1] == [49.9, 501, 0]
    assert o["cozum"] == 500
    # Inceltilmis egri zamanda artan sirada kalir.
    saniyeler = [n[0] for n in o["egri"]]
    assert saniyeler == sorted(saniyeler)


def test_egri_bos_ise_none_iyilesme_yoksa_esikler_sifir():
    assert C._iyilesme_ozeti([]) is None
    o = C._iyilesme_ozeti([(1.0, 7, 7)])
    assert o["ilk_amac"] == o["son_amac"] == 7
    assert o["yuzde50_sn"] == 0.0 and o["yuzde90_sn"] == 0.0 and o["yuzde99_sn"] == 0.0


def test_cozum_ciktisinda_egri_cozum_sayisiyla_ve_amacla_tutarli():
    c = coz(_sahne(), AYAR)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    i = ist["iyilesme"]
    assert i is not None, ist
    assert i["cozum"] == ist["cozum_sayisi"] >= 1, (i, ist["cozum_sayisi"])
    assert i["son_amac"] == ist["amac_degeri"], (i, ist["amac_degeri"])
    assert i["ilk_amac"] >= i["son_amac"]
    assert i["alt_sinir_son"] <= i["son_amac"]
    assert all(len(n) == 3 for n in i["egri"])


# ---- cozucu parametreleri (olcum kapisi) --------------------------------

def test_cozucu_parametreleri_gecer_sure_ve_isci_gecmez():
    g = _sahne()
    c = coz(g, dict(AYAR, cozucu_parametreleri={"linearization_level": 2,
                                                "num_search_workers": 1}))
    assert c["durum"] == "cozuldu", c.get("durum")
    notlar = [n for n in c["uygulanmayan_notlar"] if "cozucu parametresi yok sayildi" in n]
    assert len(notlar) == 1 and "num_search_workers" in notlar[0], c["uygulanmayan_notlar"]


def test_taninmayan_cozucu_parametresi_sessiz_gecmez():
    with pytest.raises(AttributeError):
        coz(_sahne(), dict(AYAR, cozucu_parametreleri={"boyle_bir_parametre_yok": 1}))


# ---- plan yoksa ---------------------------------------------------------

@pytest.fixture
def sure_dolmus(monkeypatch):
    """CP-SAT'e aramadan UNKNOWN dedirtir (test_sure_yetmedi.py ile ayni)."""
    def aramadan_bilmiyorum(self, model, solution_callback=None):
        return cp_model.UNKNOWN

    monkeypatch.setattr(cp_model.CpSolver, "Solve", aramadan_bilmiyorum)


def test_plan_yoksa_dagilim_ve_egri_none(sure_dolmus):
    c = coz(_sahne(), dict(AYAR, azami_saniye=1))
    assert c["durum"] == "sure_yetmedi", c.get("durum")
    ist = c["cozum_istatistikleri"]
    assert ist["amac_dagilimi"] is None
    assert ist["iyilesme"] is None
    assert ist["amac_degeri"] is None
