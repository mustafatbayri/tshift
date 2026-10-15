# -*- coding: utf-8 -*-
"""
EKIP_SUREKLILIGI -- cok ekipli kisi BIRINCIL ekibinde calissin (K-72, 14 Ekim)

NE VARDI
  Sartname #6.5 "ayni kisiler mumkun oldugunca ayni ekiple calissin" (agirlik
  2 / 1 / 4) olculebilir tanimsizdi; govdesi yoktu. Fiksturlerde herkes tek
  ekipteydi; veri setinde (VS1) 10 kisi iki ekipte (satis + back office).

KARAR (K-72, Mustafa 14 Ekim 17:05: "Ekip surekliligi ok"): tanim (a) --
  `birincil_ekip` dolu kisinin baska ekibin vardiyasina her atamasi 1 x
  agirlik; `birincil_ekip` yoksa kisi gezicidir (employee_teams onceligi
  esit), ceza yok. Ayrim sozlesme tipine degil veriye gore.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_ekip_surekliligi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU               # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as KR                        # noqa: E402

VA = {"id": "VA", "ekip": "A", "bas": 9, "bit": 18, "mola_dk": 60}
VB = {"id": "VB", "ekip": "B", "bas": 9, "bit": 18, "mola_dk": 60}
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(ekip_sur=True, birincil="A", gun=5):
    """M (cok ekipli: A + B) ve A1 (yalniz A), B1 (yalniz B). Talep: A ve B
    ekiplerinde her gun 1 kisi, `gun` gun. Yari zamanli, sure yok (K-71
    etkisiz) -> dagilimi yalniz bu kural ve adalet belirler.

    ⚠ `cok_ekipli_sayim: "tek"`: K-50'nin varsayilani "hepsi"nde M hangi
      sablonda calissa da IKI ekibe de sayilir -- B'nin kapsamasi icin M'yi B
      sablonuna koymaya gerek kalmaz, "odunc" kavrami kapsamada gorunmez.
      "tek"te yalniz sablonun ekibine sayilir; odunc gercek bir karardir."""
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HEDEF_ASIMI", tur="SERT"), _kural("HAFTA_TATILI", yasal=True)]
    if ekip_sur:
        kurallar.append(_kural("EKIP_SUREKLILIGI", tur="YUMUSAK"))
    m = {"id": "M", "ekipler": ["A", "B"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}
    if birincil is not None:
        m["birincil_ekip"] = birincil
    return {"profil": "DENGELI", "cok_ekipli_sayim": "tek",
            "calisanlar": [m,
                           {"id": "A1", "ekipler": ["A"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []},
                           {"id": "B1", "ekipler": ["B"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}],
            "vardiya_sablonlari": [VA, VB],
            "talep": [{"ekip": e, "gun": d, "saat": s, "asgari": 1 if d < gun else 0, "hedef": 1 if d < gun else 0}
                      for e in ("A", "B") for d in range(7) for s in range(9, 18)],
            "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


def _plan(satirlar):
    return [{"calisan": k, "ekip": e, "sablon": "V" + e, "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]}
            for k, e, g in satirlar]


def _es(r):
    return [i for i in r["ihlaller"] if i["kural"] == "EKIP_SUREKLILIGI"]


def _ekip_gun(c, kisi):
    return sorted((a["ekip"], a["gun"]) for a in c["atamalar"] if a["calisan"] == kisi)


# ----------------------------------------------------------------------
# 1. Dogrulayici
# ----------------------------------------------------------------------

def test_birincil_disi_atamalar_kisi_basina_YUMUSAK_ihlal():
    r = degerlendir(_sahne(gun=3), _plan([("M", "A", 0), ("M", "B", 1), ("M", "B", 2),
                                          ("A1", "A", 1), ("A1", "A", 2), ("B1", "B", 0)]))
    ih = _es(r)
    assert len(ih) == 1 and ih[0]["calisan"] == "M"
    assert ih[0]["olculen"] == 2 and ih[0]["gereken"] == 0 and ih[0]["agirlik"] == "YUMUSAK"
    assert "gun 1 B, gun 2 B" in ih[0]["mesaj"]
    assert "EKIP_SUREKLILIGI" not in r["uygulanmayan_kurallar"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


def test_GEZICI_birincil_yok_ve_TEK_ekipli_denetlenmez():
    r = degerlendir(_sahne(birincil=None), _plan([("M", "B", 0), ("M", "B", 1), ("A1", "A", 0)]))
    assert _es(r) == []
    # birincil ekibi B olan kisi B'de: ihlal yok
    r = degerlendir(_sahne(birincil="B"), _plan([("M", "B", 0), ("M", "B", 1)]))
    assert _es(r) == []


def test_birincil_ekip_UYELIKTE_degilse_denetlenmez_kural_yokken_yazilmaz():
    g = _sahne(birincil="Z")
    r = degerlendir(g, _plan([("M", "B", 0)]))
    assert _es(r) == []
    r = degerlendir(_sahne(ekip_sur=False), _plan([("M", "B", 0)]))
    assert _es(r) == [] and "EKIP_SUREKLILIGI" not in r["uygulanmayan_kurallar"]


def test_dogrulayici_dogrudan_cagri():
    g = _sahne()
    tanim = [k for k in g["kurallar"] if k["kod"] == "EKIP_SUREKLILIGI"][0]
    ih = KR.ekip_surekliligi(g, _plan([("M", "B", 3), ("M", "A", 4)]), tanim)
    assert [(i["calisan"], i["olculen"]) for i in ih] == [("M", 1)]


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_motor_cok_ekipliyi_BIRINCIL_ekibinde_tutar_oduncu_gerekince_verir():
    """A'da 5, B'de 5 vardiya; M + A1 + B1, HAFTA_TATILI (en cok 6 gun).
    Kural acikken M'nin vardiyalari A'da (birincil); B'nin 5 gununu B1 tek
    basina kapatabilir."""
    g = _sahne()
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    assert all(e == "A" for e, _ in _ekip_gun(c, "M")), _ekip_gun(c, "M")
    r = degerlendir(g, c["atamalar"])
    assert _es(r) == []
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["EKIP_SUREKLILIGI"]["deger"] == 0


def test_motor_B_tek_basina_yetmezse_ODUNC_verir_ve_ihlal_yazilir():
    """B1'e izin: B'nin 5 gununu kimse tek basina kapatamaz -> M odunc gider
    (ASGARI sert), ceza odenir; kural plani cozumsuz yapmaz."""
    g = _sahne()
    g["calisanlar"][2]["izinler"] = [{"gun": d, "durum": "onayli"} for d in range(3)]   # B1 gun 0-2 izinli
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    b_gunleri = [gn for e, gn in _ekip_gun(c, "M") if e == "B"]
    assert sorted(b_gunleri) == [0, 1, 2]
    r = degerlendir(g, c["atamalar"])
    assert [(i["calisan"], i["olculen"]) for i in _es(r)] == [("M", 3)]
    dag = c["cozum_istatistikleri"]["amac_dagilimi"]["EKIP_SUREKLILIGI"]
    assert dag["deger"] == 3 and dag["ceza"] == 3 * AGIRLIK_TABLOSU["EKIP_SUREKLILIGI"]["DENGELI"]


def test_GEZICI_kisi_icin_degisken_yok_kural_KAPALIYKEN_de_yok():
    k = Model(_sahne(birincil=None)).kur()
    assert not [v for _, v in k.cezalar if v.Name().startswith("es_")]
    k = Model(_sahne(ekip_sur=False)).kur()
    assert not [v for _, v in k.cezalar if v.Name().startswith("es_")]
    k = Model(_sahne()).kur()
    es = [(a, v) for a, v in k.cezalar if v.Name().startswith("es_")]
    assert [v.Name() for _, v in es] == ["es_M"] and es[0][0] == 2            # DENGELI 2


def test_birincil_UYELIKTE_degilse_NOT_duser_ve_uygulanmaz():
    k = Model(_sahne(birincil="Z")).kur()
    assert not [v for _, v in k.cezalar if v.Name().startswith("es_")]
    assert any("EKIP_SUREKLILIGI" in n and "M" in n for n in k.notlar)


def test_AGIRLIK_tablosu_sartname_2_1_4_ve_profil():
    assert AGIRLIK_TABLOSU["EKIP_SUREKLILIGI"] == {"DENGELI": 2, "KAPSAMA": 1, "CALISAN": 4}
    g = _sahne()
    g["profil"] = "CALISAN"
    k = Model(g).kur()
    assert [a for a, v in k.cezalar if v.Name() == "es_M"] == [4]
