# -*- coding: utf-8 -*-
"""SERT HEDEF_ASIMI olabilirlik sondasi: ha_* degiskenleri [0,0]'a cekilince
model cozulebilir mi? Amac fonksiyonu silinir (yalniz olabilirlik).
Kullanim: python3 sert_deneme.py <olcek> <saniye>
"""
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor"))
sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model                               # noqa: E402
from uret_veri_seti import sahne_uret                        # noqa: E402

olcek = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
saniye = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
g = sahne_uret(olcek, 0.95)
print("olcek %.2f: %d calisan, %d talep hucresi" % (olcek, len(g["calisanlar"]), len(g["talep"])))

for sert in (False, True):
    t0 = time.time()
    k = Model(g).kur()
    k.m.ClearObjective()
    n = 0
    if sert:
        for _, v in k.cezalar:
            if hasattr(v, "Name") and v.Name().startswith("ha_"):
                k.m.Add(v == 0)
                n += 1
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = saniye
    s.parameters.num_workers = 2
    durum = s.Solve(k.m)
    print("  %s (ha_ sifirlanan %d): %s, %.1f sn (kurma dahil %.1f)"
          % ("SERT ha=0" if sert else "bugunku (yumusak, amacsiz)", n, s.StatusName(durum),
             s.WallTime(), time.time() - t0))
    if sert and durum == cp_model.INFEASIBLE:
        print("  -> SERT mutlak kural bu olcekte COZUMSUZ")
