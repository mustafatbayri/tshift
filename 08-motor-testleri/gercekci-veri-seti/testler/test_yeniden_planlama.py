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


# ---- 17 Ekim: teshis + taslak kaydi, vardiya kaymasi (K-73) yapilandirmalari ----------------

_kspec = importlib.util.spec_from_file_location(
    "test_kayma_sahne", os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor", "testler", "test_kayma.py"))
TK = importlib.util.module_from_spec(_kspec)
_kspec.loader.exec_module(TK)


def test_yapilandirmalar_bozuk_sahneyi_dogru_kurar():
    g = TK._sahne(raporlu=None)
    plan = g["mevcut_plan"]
    a = YP.bozuk_sahne(g, plan, [("P3", 2)], **YP.YAPILANDIRMALAR["A_kayma"][1])
    assert a["_kayma"]["etkilenen"] == [["E", 2]] and a["_kayma"]["sablon"] > 0
    assert a["mevcut_plan"] == plan and any(t.get("kayma") for t in a["vardiya_sablonlari"])
    t1 = YP.bozuk_sahne(g, plan, [("P3", 2)], **YP.YAPILANDIRMALAR["A_kayma_tavan1"][1])
    assert all(t["kayma"]["saat"] <= 1 for t in t1["vardiya_sablonlari"] if t.get("kayma"))
    y = YP.bozuk_sahne(g, plan, [("P3", 2)], **YP.YAPILANDIRMALAR["A_kayma_yumusak"][1])
    assert not any(k["kod"] == "ASGARI_KAPSAMA" for k in y["kurallar"]) and y["agirliklar"] == {"HEDEF_KAPSAMA": 3000}
    assert any(k["kod"] == "ASGARI_KAPSAMA" for k in g["kurallar"]) and "agirliklar" not in g     # kaynak degismedi
    with pytest.raises(SystemExit):
        list(YP.olc(g, plan, hastalik=1, ornek=1, saniye=5, yapilandirmalar=["yok_boyle"]))


def test_UCTAN_UCA_cozumsuzde_teshis_ve_taslak_kaydedilir_kaymayla_plan_cikar():
    g = TK._sahne(raporlu=None)
    plan = g["mevcut_plan"]
    # tohum secimi: bozulma_sec rastgele; P3 / gun 2 olmasi icin dogrudan kuruyoruz
    ayar = dict(YP.AYAR, azami_saniye=20)
    bozulma = [("P3", 2)]
    A = YP._kosu(YP.bozuk_sahne(g, plan, bozulma, **YP.YAPILANDIRMALAR["A_urun"][1]), plan, bozulma, ayar)
    assert A["durum"] == "cozumsuz" and A["teshis"]["kesin"] is True
    assert A["teshis"]["kapsam"] in ("kural", "hucre")              # kucuk sahnede kural duzeyinde kanit
    assert "ASGARI_KAPSAMA" in {k["kod"] for k in A["teshis"]["engelleyen"]}
    assert A["taslak"]["dokunulan"] is not None and A["taslak"]["eksik_kisi_saat"] > 0
    assert A["taslak"]["kayma"]["toplam_saat"] == 0 and "ASGARI_KAPSAMA" in A["taslak"]["gevsetilen"]
    K = YP._kosu(YP.bozuk_sahne(g, plan, bozulma, **YP.YAPILANDIRMALAR["A_kayma"][1]), plan, bozulma, ayar)
    assert K["durum"] == "cozuldu" and K["sert_ihlal"] == 0 and K["raporlu_gunde_calisan"] == 0
    assert K["kayma"] == {"kisi_sayisi": 2, "atama_sayisi": 2, "toplam_saat": 6, "en_buyuk_saat": 4, "dagilim": {"2": 1, "4": 1}}
    assert sorted((s["calisan"], s["erken"], s["gec"]) for s in K["kayma_satirlari"]) == [("P1", 0, 4), ("P2", 2, 0)]
    assert K["dokunulan"] == 3 and K["fazladan_dokunulan"] == 1 and K["eksik_kisi_saat"] == 2    # 14-16: 2/3
    assert K["kayma_sablon"] > 0 and A["kayma_sablon"] == 0
    T2 = YP._kosu(YP.bozuk_sahne(g, plan, bozulma, **YP.YAPILANDIRMALAR["A_kayma_tavan2"][1]), plan, bozulma, ayar)
    assert T2["durum"] == "cozumsuz"                     # P1'in +4'u yok; tavan plani kacirdi
    # asgari gevsek + 1 kisi-saat acik = 1 saat fazla mesai (3000): BERABERE -- kararlilik cezasi (6)
    # teraziyi acik birakmaya dogru iter, motor UZATMAZ (acik 8). 6000'de uzatir (acik 2, kayma 6 sa).
    # Mustafa'nin agirlik karari icin olculen gercek: kapsama, fazla mesai bedelinin USTUNDE olmali.
    Y = YP._kosu(YP.bozuk_sahne(g, plan, bozulma, **YP.YAPILANDIRMALAR["A_kayma_yumusak"][1]), plan, bozulma, ayar)
    assert Y["durum"] == "cozuldu" and Y["eksik_kisi_saat"] == 8 and Y["kayma"]["toplam_saat"] == 0
    Y6 = YP._kosu(YP.bozuk_sahne(g, plan, bozulma, **YP.YAPILANDIRMALAR["A_kayma_yumusak6"][1]), plan, bozulma, ayar)
    assert Y6["durum"] == "cozuldu" and Y6["eksik_kisi_saat"] == 2 and Y6["kayma"]["toplam_saat"] == 6 and Y6["fazla_mesai_saat"] == 6.0
    o = {"ornek": 1, "A_urun": A, "A_kayma": K}
    metin = YP.ozet([o], ["A_urun", "A_kayma"])
    assert "plan 0/1" in metin and "cozumsuz 1: taslak" in metin and "kayma ort 6.0 sa (1 planda)" in metin
    assert "teshis" in YP._satir(o, "A_urun", A) and "kayma 2 kisi 6 sa" in YP._satir(o, "A_kayma", K)
