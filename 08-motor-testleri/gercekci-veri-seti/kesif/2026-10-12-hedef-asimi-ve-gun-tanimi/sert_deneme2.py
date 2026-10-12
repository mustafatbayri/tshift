# -*- coding: utf-8 -*-
"""Catisma hangi kuralda? SERT ha=0 + SAAT_DENGESI (K-39 tabani) kaldirilinca cozulebilir mi?"""
import copy, os, sys, time
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor")); sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
from ortools.sat.python import cp_model
from cozucu.model import Model
from uret_veri_seti import sahne_uret
olcek = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
g = sahne_uret(olcek, 0.95)
for kaldir in (["SAAT_DENGESI"], ["SAAT_DENGESI", "ROL_KAPSAMASI", "YETKINLIK_KAPSAMASI"], ["SAAT_DENGESI", "ROL_KAPSAMASI", "YETKINLIK_KAPSAMASI", "ASGARI_KAPSAMA"]):
    g2 = copy.deepcopy(g)
    g2["kurallar"] = [k for k in g2["kurallar"] if k["kod"] not in kaldir]
    t0 = time.time()
    k = Model(g2).kur(); k.m.ClearObjective()
    n = 0
    for _, v in k.cezalar:
        if hasattr(v, "Name") and v.Name().startswith("ha_"):
            k.m.Add(v == 0); n += 1
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 120; s.parameters.num_workers = 2
    durum = s.Solve(k.m)
    print("olcek %.2f, SERT ha=0 (%d hucre), %s KALDIRILDI: %s, %.1f sn" % (olcek, n, "+".join(kaldir), s.StatusName(durum), time.time() - t0))
