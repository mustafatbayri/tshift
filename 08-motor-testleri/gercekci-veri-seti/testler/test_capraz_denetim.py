# -*- coding: utf-8 -*-
"""
CAPRAZ DENETIM testleri (16 Ekim; D) -- capraz-denetim.py

  * her kucuk fikstur cifti (olcek < 1: 25 / 49 / 151 / 200 kisi; uretec, VS2, EK) bugunku
    dogrulayicida SART tutar (sert 0, asim 0, eksik 0, fm <= izinli, puan = toplam);
    500 kisilikler burada degil (4 sn/plan): gece blogunda `py capraz-denetim.py`;
  * olcum dosya adi -> sahne cozumlemesi (L1, -EK, -VS<n>, cesit, olcek, S30);
  * kayitli plan kaydi: taze degerlendir ile kayitli dogrulama kiyasi; sahnesi olmayan
    kayit ATLANIR (hata degil); bozulmus bir plan (fm'li satir) SERT FARKI olarak gorunur.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_capraz_denetim.py -v
"""

import copy
import glob
import importlib.util
import io
import json
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor"))

_spec = importlib.util.spec_from_file_location("capraz_denetim", os.path.join(BURASI, "capraz-denetim.py"))
CD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CD)


def _kucuk_ciftler():
    return [(s, r) for s, r in CD.fiksturler() if CD.L1_AD.match(os.path.basename(s)).group("olcek")]


@pytest.mark.parametrize("sahne_yolu,referans_yolu", _kucuk_ciftler(),
                         ids=[os.path.basename(s) for s, _ in _kucuk_ciftler()])
def test_CAPRAZ_kucuk_fikstur_bugunku_dogrulayicida_SART_tutar(sahne_yolu, referans_yolu):
    s = CD.fikstur_denetle(sahne_yolu, referans_yolu)
    assert s["temiz"], s
    assert s["sert"] == 0 and s["asim"] == 0 and s["eksik"] == 0 and s["fm"] <= s["izinli_fm"] + 1e-9
    assert s["puan_toplam_tutuyor"] is True and s["yayinlanabilir"] is True


def test_CAPRAZ_fikstur_ciftleri_eksiksiz():
    sahneler = sorted(glob.glob(os.path.join(CD.FIKSTUR, "_sahne-L1*.json")))
    assert len(CD.fiksturler()) == len(sahneler), "referansi olmayan L1 sahnesi var"
    assert any("-EK-" in s for s, _ in CD.fiksturler()), "tanikli (EK) fikstur yok"


def test_CAPRAZ_olcum_adi_sahne_cozumlemesi():
    m = CD.OLCUM_AD.match("kalite-olcumu-L1-EK-0.1-95-ekili-bulut-300.json").groupdict()
    assert m == {"eki": "-EK", "cesit": None, "olcek": "0.1"}
    assert CD.OLCUM_AD.match("kalite-olcumu-L1-VS2-0.1-95-bulut.json").groupdict() == {"eki": "-VS2", "cesit": None, "olcek": "0.1"}
    assert CD.OLCUM_AD.match("kalite-olcumu-L1-asim_yumusak-95-ayirma-900.json").groupdict() == {"eki": "", "cesit": "asim_yumusak", "olcek": None}
    assert CD.OLCUM_AD.match("kalite-olcumu-L1-VS1-95-k68b-1800.json").groupdict() == {"eki": "-VS1", "cesit": None, "olcek": None}
    assert CD.OLCUM_AD.match("kalite-olcumu-95-rotasyon-once-900.json") is None       # S30 yolu
    g, acik = CD.plan_sahnesi("kalite-olcumu-L1-EK-0.1-95-ekili-bulut-300.json", {})
    assert g is not None and acik == "_sahne-L1-EK-95-0.1.json" and len(g["calisanlar"]) == 49
    g2, acik2 = CD.plan_sahnesi("kalite-olcumu-L1-tol1-95-gevsek-900.json", {})
    assert g2 is not None and "cesit tol1" in acik2
    g3, acik3 = CD.plan_sahnesi("kalite-olcumu-0.2-95-d-sonra-bulut.json", {"olcek": 0.2, "doluluk": 0.95})
    assert g3 is None and "atlandi" in acik3
    g4, acik4 = CD.plan_sahnesi("kalite-olcumu-L1-VS9-95-x.json", {})
    assert g4 is None and "yok" in acik4


def _ekili_plan_kaydi():
    yollar = sorted(glob.glob(os.path.join(CD.PLANLAR, "kalite-olcumu-L1-EK-0.1-95-*", "*.json")))
    return yollar[0] if yollar else None


@pytest.mark.skipif(_ekili_plan_kaydi() is None, reason="EK 0.1 plan kaydi yok")
def test_CAPRAZ_kayitli_plan_taze_denetim_kayitla_AYNI_ve_bozulmus_plan_FARK_verir(tmp_path):
    yol = _ekili_plan_kaydi()
    s = CD.plan_denetle(yol, {})
    assert not s.get("atlandi"), s
    assert s["temiz"] and s["sert_taze"] == s["sert_kayitli"] == 0 and s["fm_taze"] == s["fm_kayitli"] == s["fm_motor"]
    # ayni kaydin bir satirina 6 saat fazla mesai eklenmis kopyasi: taze denetim SERT farki yazar
    with io.open(yol, encoding="utf-8") as f:
        p = json.load(f)
    bozuk = copy.deepcopy(p)
    a = bozuk["cikti"]["atamalar"][0]
    a["bit"] = float(a["bit"]) + 6
    byol = tmp_path / "kalite-olcumu-L1-EK-0.1-95-ekili-bulut-300" / "bozuk-1.json"
    byol.parent.mkdir()
    with io.open(str(byol), "w", encoding="utf-8") as f:
        json.dump(bozuk, f)
    b = CD.plan_denetle(str(byol), {})
    assert not b.get("atlandi") and not b["temiz"]
    assert b["sert_taze"] > 0 and b["sert_farki"] is True


def test_CAPRAZ_bicimi_bilinmeyen_kayit_ATLANIR(tmp_path):
    yol = tmp_path / "x" / "eski.json"
    yol.parent.mkdir()
    with io.open(str(yol), "w", encoding="utf-8") as f:
        json.dump({"kayit": {"bicim": "eski/0"}}, f)
    s = CD.plan_denetle(str(yol), {})
    assert s["atlandi"].startswith("bicim")
