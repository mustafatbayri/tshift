# -*- coding: utf-8 -*-
"""D3: uctan uca butce -- `coz()` ile kucuk butce, fazla_mesaisiz_deneme=3.
  (i)  dogal kosu (denemeler aninda bulur)
  (ii) ilk 3 Solve (fm-siz denemeler) SURESINI DOLDURUP UNKNOWN donsun (uyku),
       sonrasi gercek: ilk_asama_sn + ana_asama_butce_sn <= azami ? toplam duvar
       saati?  azami 10 / 5 / 4 ve deneme 1 / 3 kiyasi."""
import sys, time
from ortak import *
from test_fazla_mesai_once_sifir import _sahne, AYAR_URUN

asil = cp_model.CpSolver


def zorla(ilk_unknown):
    """Ilk `ilk_unknown` Solve: max_time kadar uyur, UNKNOWN doner."""
    cagri = []

    class Uyuyan(asil):
        def Solve(self, model, *a, **kw):
            cagri.append(round(self.parameters.max_time_in_seconds, 3))
            if len(cagri) <= ilk_unknown:
                time.sleep(self.parameters.max_time_in_seconds)
                return cp_model.UNKNOWN
            return asil.Solve(self, model, *a, **kw)
    C.cp_model.CpSolver = Uyuyan
    return cagri


def kos(azami, deneme, ilk_unknown):
    cagri = zorla(ilk_unknown)
    try:
        g = _sahne(gun=5)
        t0 = time.time()
        c = C.coz(g, dict(AYAR_URUN, azami_saniye=azami, fazla_mesaisiz_deneme=deneme, isci_sayisi=2))
        duvar = time.time() - t0
    finally:
        C.cp_model.CpSolver = asil
    ist = c["cozum_istatistikleri"]
    b = ist["fazla_mesai_once_sifir"] or {}
    top = ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"]
    print("azami=%2d deneme=%d zorla=%d | durum=%-12s ilk_asama=%.2f ana_butce=%.2f toplam=%.2f %s | duvar=%.2f | fm: bulundu=%s sn=%s denemeler=%s | iyilestirme_sn=%s | cagri sureleri=%s"
          % (azami, deneme, ilk_unknown, c["durum"], ist["ilk_asama_sn"], ist["ana_asama_butce_sn"], top,
             "OK" if top <= azami + 0.05 else "ASIM(+%.2f)" % (top - azami), duvar,
             b.get("bulundu"), b.get("saniye"), [(d["tohum"], d["saniye"], d["durum"]) for d in (b.get("denemeler") or [])],
             (ist["ilk_asama_iyilestirme"] or {}).get("saniye"), cagri))
    sys.stdout.flush()
    return c


print("(i) dogal")
kos(10, 3, 0)
kos(10, 1, 0)
print("\n(ii) fm-siz denemeler sureyi doldurup UNKNOWN")
kos(10, 3, 3)
kos(10, 1, 1)
kos(5, 3, 3)
kos(5, 1, 1)
kos(4, 3, 3)
kos(4, 1, 1)
kos(30, 3, 3)
