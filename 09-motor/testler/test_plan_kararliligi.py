# -*- coding: utf-8 -*-
"""
PLAN_KARARLILIGI -- ayni haftanin yeniden planlanmasinda mevcut plan korunsun
(K-70, 14 Ekim)

NE VARDI
  Sartname #6.5 "Yeniden planlamada mevcut atamalar korunsun" (agirlik 6/6/6)
  olculebilir tanimsizdi; govdesi yoktu. `mevcut_plan` (K-54) motora yalniz
  BASLANGIC IPUCU olarak gidiyordu: ondan uzaklasmanin bedeli yoktu -- bir
  kisi hastalandi diye onlarca kisinin vardiyasi degisebiliyordu.

KARAR (K-70, Mustafa 14 Ekim 15:26: "aynı haftanın yeniden planlanmasında
  çalışsın"): kural yalniz `mevcut_plan` varken; birim KISI-GUN; yalnız mola
  degisen gun sayilmaz; bos gune eklenen ve kaldirilan vardiya sayilir
  (oneri uygulandi). Haftadan haftaya benzerlik arayuzun isi (klonla +
  kilitle).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_plan_kararliligi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz, plan_degisikligi                  # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU               # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as KR                        # noqa: E402

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _plan(kisi_gunler, mola_bas=13):
    return [{"calisan": k, "ekip": "E", "sablon": "V", "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": mola_bas, "bit": mola_bas + 1, "tip": "yemek"}]}
            for k, g in kisi_gunler]


MEVCUT = [("P1", 0), ("P1", 1), ("P1", 2), ("P2", 3), ("P2", 4)]     # yayinlanmis plan: 5 gun x 1 kisi


def _sahne(kararlilik=True, mevcut=True, donmus=()):
    """Uc yari zamanli (sure yok), 5 gun x 1 kisi talep, HEDEF_ASIMI SERT.
    `mevcut_plan` MEVCUT; P1 gun 1'de izinli olur (hastalik) -> yeniden
    planlama: en az degisiklik = P1 gun 1 kaldirilir, biri gun 1'e eklenir."""
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HEDEF_ASIMI", tur="SERT"), _kural("HAFTA_TATILI", yasal=True),
                _kural("ADALET_DENGESI", tur="YUMUSAK")]
    if kararlilik:
        kurallar.append(_kural("PLAN_KARARLILIGI", tur="YUMUSAK"))
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": p, "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                         "izinler": [], "uygunluk": []} for p in ("P1", "P2", "P3")],
         "vardiya_sablonlari": [V],
         "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1 if d < 5 else 0, "hedef": 1 if d < 5 else 0}
                   for d in range(7) for s in range(9, 18)],
         "kurallar": kurallar, "kilitler": [], "donmus_gunler": list(donmus)}
    if mevcut:
        g["mevcut_plan"] = _plan(MEVCUT)
    return g


def _pk(r):
    return [i for i in r["ihlaller"] if i["kural"] == "PLAN_KARARLILIGI"]


def _kg(c):
    return sorted((a["calisan"], a["gun"]) for a in c["atamalar"])


# ----------------------------------------------------------------------
# 1. Dogrulayici
# ----------------------------------------------------------------------

def test_degisen_kaldirilan_eklenen_KISI_GUN_basina_YUMUSAK_ihlal():
    yeni = _plan([("P1", 0), ("P3", 1), ("P1", 2), ("P2", 3), ("P2", 4)])     # gun 1: P1 -> P3
    r = degerlendir(_sahne(), yeni)
    ih = _pk(r)
    assert [(i["calisan"], i["gun"]) for i in ih] == [("P1", 1), ("P3", 1)]
    assert "kaldirilan" in ih[0]["mesaj"] and "eklenen" in ih[1]["mesaj"]
    assert all(i["agirlik"] == "YUMUSAK" and i["olculen"] == 1 and i["gereken"] == 0 for i in ih)
    assert "PLAN_KARARLILIGI" not in r["uygulanmayan_kurallar"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True
    assert plan_degisikligi(_sahne(), yeni) == {"korunan": 4, "degisen": 0, "kaldirilan": 1, "eklenen": 1}


def test_yalniz_MOLA_degisen_gun_SAYILMAZ_ayni_plan_sifir():
    r = degerlendir(_sahne(), _plan(MEVCUT, mola_bas=14))
    assert _pk(r) == []
    assert plan_degisikligi(_sahne(), _plan(MEVCUT, mola_bas=14)) == {"korunan": 5, "degisen": 0, "kaldirilan": 0, "eklenen": 0}


def test_SABLON_degisirse_DEGISEN_ve_sablonsuz_satir_bas_bit_ile_kiyaslanir():
    g = _sahne()
    g["vardiya_sablonlari"].append({"id": "W", "ekip": "E", "bas": 10, "bit": 19, "mola_dk": 60})
    yeni = _plan(MEVCUT)
    yeni[0] = dict(yeni[0], sablon="W", bas=10, bit=19)                         # P1 gun 0: V -> W
    ih = _pk(degerlendir(g, yeni))
    assert [(i["calisan"], i["gun"]) for i in ih] == [("P1", 0)] and "degisen" in ih[0]["mesaj"]
    # sablon kimligi yok: ekip + bas + bit esitse korunmus
    g["mevcut_plan"] = [dict(a, sablon=None) for a in g["mevcut_plan"]]
    yeni2 = [dict(a, sablon=None) for a in _plan(MEVCUT)]
    assert _pk(degerlendir(g, yeni2)) == []


def test_DONMUS_gun_kiyas_disi_MEVCUT_PLAN_yoksa_kural_uygulanmaz():
    g = _sahne(donmus=(0,))
    yeni = _plan([("P3", 0), ("P1", 1), ("P1", 2), ("P2", 3), ("P2", 4)])     # gun 0 degisti ama donmus
    assert [(i["calisan"], i["gun"]) for i in _pk(degerlendir(g, yeni))] == []
    g = _sahne(mevcut=False)
    r = degerlendir(g, _plan([("P3", 0)]))
    assert _pk(r) == [] and "PLAN_KARARLILIGI" not in r["uygulanmayan_kurallar"]
    assert plan_degisikligi(g, _plan([("P3", 0)])) is None


def test_dogrulayici_dogrudan_cagri():
    g = _sahne()
    tanim = [k for k in g["kurallar"] if k["kod"] == "PLAN_KARARLILIGI"][0]
    ih = KR.plan_kararliligi(g, _plan([("P1", 0), ("P1", 1), ("P1", 2), ("P2", 3)]), tanim)    # gun 4 kaldirildi
    assert [(i["calisan"], i["gun"]) for i in ih] == [("P2", 4)]


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_motor_hastalik_sonrasi_EN_AZ_degisiklikle_yeniden_planlar():
    """P1 gun 1'de izinli: tek dogru hamle gun 1'e baskasini koymak (2
    kisi-gun degisim). Kural acikken motor baska hicbir gunu oynatmaz."""
    g = _sahne()
    g["calisanlar"][0]["izinler"] = [{"gun": 1, "durum": "onayli"}]
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    kg = _kg(c)
    assert ("P1", 0) in kg and ("P1", 2) in kg and ("P2", 3) in kg and ("P2", 4) in kg, kg
    assert ("P1", 1) not in kg and len(kg) == 5
    assert c["metrikler"]["plan_degisikligi"] == {"korunan": 4, "degisen": 0, "kaldirilan": 1, "eklenen": 1}
    dag = c["cozum_istatistikleri"]["amac_dagilimi"]["PLAN_KARARLILIGI"]
    assert dag["deger"] == 2 and dag["ceza"] == 2 * 6
    r = degerlendir(g, c["atamalar"])
    assert len(_pk(r)) == 2
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]


def test_KURAL_YOKKEN_motor_mevcut_plani_korumaz_kiyas():
    """Ayni sahne, kural kapali: ADALET (hafta sonu / gece sayilmiyor burada)
    ve HEDEF esit; motorun plani degistirmemesi icin sebep yok -- ipucu yalniz
    baslangic. Degisim >= 2 (en az hastalik kadar); kuralla tam 2."""
    g = _sahne(kararlilik=False)
    g["calisanlar"][0]["izinler"] = [{"gun": 1, "durum": "onayli"}]
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu"
    assert "PLAN_KARARLILIGI" not in c["cozum_istatistikleri"]["amac_dagilimi"]
    d = c["metrikler"]["plan_degisikligi"]
    assert d["kaldirilan"] + d["degisen"] + d["eklenen"] >= 2                 # metrik kural kapaliyken de yazilir


def test_BIRIM_degiskenler_kisi_gun_basina_DONMUS_disinda_MEVCUT_yoksa_hic():
    k = Model(_sahne(donmus=(0,))).kur()
    pk = [v for _, v in k.cezalar if v.Name().startswith("pk_")]
    assert len(pk) == 3 * 6                                                   # 3 kisi x (7 - 1 donmus) gun
    assert not [v for v in pk if v.Name().endswith("_0")]
    assert [a for a, v in k.cezalar if v.Name() == "pk_P1_1"] == [6]
    k = Model(_sahne(mevcut=False)).kur()
    assert not [v for _, v in k.cezalar if v.Name().startswith("pk_")]


def test_mevcut_plandaki_KADRO_DISI_kisi_ve_OTURMAYAN_satir_not_duser():
    g = _sahne()
    g["mevcut_plan"].append({"calisan": "ESKI", "ekip": "E", "sablon": "V", "gun": 2, "bas": 9, "bit": 18, "molalar": []})
    g["mevcut_plan"].append({"calisan": "P3", "ekip": "E", "sablon": "YOK", "gun": 5, "bas": 1, "bit": 3, "molalar": []})
    k = Model(g).kur()
    assert any("kadroda yok" in n and "ESKI" in n for n in k.notlar)
    assert any("oturmadi" in n and "P3" in n for n in k.notlar)
    assert plan_degisikligi(g, _plan(MEVCUT))["kaldirilan"] == 2                # ESKI gun 2, P3 gun 5


def test_AGIRLIK_tablosu_6_6_6():
    assert AGIRLIK_TABLOSU["PLAN_KARARLILIGI"] == {"DENGELI": 6, "KAPSAMA": 6, "CALISAN": 6}


def test_SABLON_degisikligi_motor_icin_de_DEGISIMDIR_kilitle_zorlanir():
    """P1 gun 0 kilitle W sablonuna (10-19) alinir: ayni gun calisiyor ama
    sablon degisti -> pk_P1_0 = 1 (metrik: degisen 1). 'Calisiyor olmasi
    yeter' okumasi yanlis olurdu."""
    g = _sahne()
    g["vardiya_sablonlari"].append({"id": "W", "ekip": "E", "bas": 10, "bit": 19, "mola_dk": 60})
    g["talep"] = [t for t in g["talep"] if not (t["gun"] == 0 and t["saat"] == 9)] + \
                 [{"ekip": "E", "gun": 0, "saat": 18, "asgari": 1, "hedef": 1}]        # gun 0 talebi 10-19'a kaydi
    g["kilitler"] = [{"calisan": "P1", "gun": 0, "ekip": "E", "sablon": "W", "bas": 10, "bit": 19}]
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    assert ("P1", 0, "W") in {(a["calisan"], a["gun"], a["sablon"]) for a in c["atamalar"]}
    assert c["metrikler"]["plan_degisikligi"] == {"korunan": 4, "degisen": 1, "kaldirilan": 0, "eklenen": 0}
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["PLAN_KARARLILIGI"]["deger"] == 1


def test_DONMUS_gunun_mevcut_satiri_OKUNMAZ_oturmayan_satir_notu_dusmez():
    g = _sahne(donmus=(0,))
    g["mevcut_plan"][0] = dict(g["mevcut_plan"][0], sablon="YOK", bas=1, bit=3)     # P1 gun 0 (donmus) oturmaz
    k = Model(g).kur()
    assert not [n for n in k.notlar if "PLAN_KARARLILIGI" in n and "oturmadi" in n]
    g2 = _sahne()
    g2["mevcut_plan"][0] = dict(g2["mevcut_plan"][0], sablon="YOK", bas=1, bit=3)   # ayni satir, gun donmus degil
    assert [n for n in Model(g2).kur().notlar if "PLAN_KARARLILIGI" in n and "oturmadi" in n]
