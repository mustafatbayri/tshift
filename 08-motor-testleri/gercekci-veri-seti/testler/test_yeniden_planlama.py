# -*- coding: utf-8 -*-
"""
YENIDEN PLANLAMA olcumu testleri (16 Ekim; "edit") -- yeniden-planlama.py

  * bozulma secimi deterministik ve gecerli (kisi o gun planda calisiyor; k farkli kisi);
  * bozuk sahne: onayli RAPOR izni, mevcut_plan (A) / yok (B), PLAN_KARARLILIGI eklenir, _merdiven kalkar;
  * kucuk sahnede uctan uca: A ve B plan bulur, raporlu kisi o gun calismaz, degisiklik
    yayinlanmis plana gore sayilir, zorunlu dokunma 2k; A'nin dokundugu kisi-gun B'ninkinden fazla DEGIL.
"""

import copy
import importlib.util
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor"))

_spec = importlib.util.spec_from_file_location("yeniden_planlama", os.path.join(BURASI, "yeniden-planlama.py"))
YP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(YP)

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne():
    """Dort yari zamanli (sure yok), 5 gun x 1 kisi talep, HEDEF_ASIMI SERT, ONAYLI_IZIN SERT."""
    return {"profil": "DENGELI",
            "calisanlar": [{"id": p, "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}
                           for p in ("P1", "P2", "P3", "P4")],
            "vardiya_sablonlari": [V],
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1 if d < 5 else 0, "hedef": 1 if d < 5 else 0}
                      for d in range(7) for s in range(9, 18)],
            "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"), _kural("HEDEF_ASIMI", tur="SERT"),
                         _kural("HAFTA_TATILI", yasal=True), _kural("ONAYLI_IZIN"), _kural("ADALET_DENGESI", tur="YUMUSAK")],
            "kilitler": [], "donmus_gunler": []}


def _plan(kisi_gunler):
    return [{"calisan": k, "ekip": "E", "sablon": "V", "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]} for k, g in kisi_gunler]


YAYIN = _plan([("P1", 0), ("P1", 1), ("P1", 2), ("P2", 3), ("P2", 4)])


def test_bozulma_secimi_deterministik_ve_planda_calisilan_gun():
    import random
    b1 = YP.bozulma_sec(YAYIN, 2, random.Random(7))
    b2 = YP.bozulma_sec(YAYIN, 2, random.Random(7))
    assert b1 == b2 and len({k for k, _ in b1}) == 2
    calisilan = {(a["calisan"], a["gun"]) for a in YAYIN}
    assert all((k, g) in calisilan for k, g in b1)
    with pytest.raises(SystemExit):
        YP.bozulma_sec(YAYIN, 3, random.Random(1))          # planda yalniz 2 kisi var


def test_bozuk_sahne_izin_mevcut_plan_ve_kararlilik_kurali():
    g = _sahne()
    g["_merdiven"] = {"x": 1}
    a = YP.bozuk_sahne(g, YAYIN, [("P1", 1)], mevcut_plan=True)
    b = YP.bozuk_sahne(g, YAYIN, [("P1", 1)], mevcut_plan=False)
    p1 = next(c for c in a["calisanlar"] if c["id"] == "P1")
    assert p1["izinler"] == [{"gun": 1, "tip": "rapor", "durum": "onayli"}]
    assert a["mevcut_plan"] == YAYIN and "mevcut_plan" not in b
    assert any(k["kod"] == "PLAN_KARARLILIGI" for k in a["kurallar"]) and "_merdiven" not in a
    assert g["calisanlar"][0]["izinler"] == [] and "mevcut_plan" not in g       # kaynak degismedi


def test_referans_dosyasi_ve_sahne_adi(tmp_path):
    s = tmp_path / "_sahne-INSAN-2026-06-22.json"; r = tmp_path / "_referans-INSAN-2026-06-22.json"
    s.write_text("{}"); r.write_text("{}")
    assert YP.referans_dosyasi(str(s)) == str(r)
    assert YP.referans_dosyasi(str(tmp_path / "baska.json")) is None
    assert YP.sahne_adi(r"C:\x\_sahne-INSAN-2026-06-22.json") == "INSAN-2026-06-22"


def test_UCTAN_UCA_raporlu_kisi_calismaz_degisiklik_yayinlanmis_plana_gore_A_B_den_fazla_dokunmaz():
    g = _sahne()
    sonuclar = list(YP.olc(g, YAYIN, hastalik=1, ornek=1, saniye=20, tohum=3))
    o = sonuclar[0]
    assert len(o["bozulma"]) == 1
    A, B = o["A_urun"], o["B_sifirdan"]
    assert A["durum"] == "cozuldu" and B["durum"] == "cozuldu", (A, B)
    assert A["raporlu_gunde_calisan"] == 0 and B["raporlu_gunde_calisan"] == 0
    assert A["sert_ihlal"] == 0 and A["eksik_hedef_dakika"] == 0
    d = A["degisiklik"]
    assert set(d) == {"korunan", "degisen", "kaldirilan", "eklenen"}
    assert d["kaldirilan"] >= 1 and d["eklenen"] >= 1                    # raporlu gun kaldirildi, biri kondu
    assert A["dokunulan"] == d["degisen"] + d["kaldirilan"] + d["eklenen"]
    assert A["fazladan_dokunulan"] == A["dokunulan"] - 2
    assert A["dokunulan"] <= B["dokunulan"]                               # K-70 degisikligi artirmaz
    assert A["kararlilik_cezasi"] is not None and B["kararlilik_cezasi"] is None
    print(YP.ozet(sonuclar))
