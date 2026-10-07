# -*- coding: utf-8 -*-
"""D8: B6 onerisinin prototipi (depo disinda): yalniz karar degiskenleri (x/mola/
dinlenme) ipucuya sabit + amac, 1 isci -> sure, durum, atamalar ipucuyla ayni mi,
amac siki mi. Fix-all ile yan yana."""
import time
from ortak import *
g = sahne(0.2); k, _ = kur(g)
ayar = dict(C.VARSAYILAN, azami_saniye=30, isci_sayisi=2)
C._ipucu_ver(k, ayar); C._atamalari_sabitle(k)
p = k.m.Proto(); h = dict(zip(p.solution_hint.vars, p.solution_hint.values))
def oneri(k, isci=1):
    kopya = k.m.Clone(); kopya.ClearHints(); pr = kopya.Proto()
    for sozluk in (k.x, k.mola, k.dinlenme):
        for v in sozluk.values():
            d = int(h[v.Index()]); dom = pr.variables[v.Index()].domain; dom.clear(); dom.extend([d, d])
    c = cp_model.CpSolver(); c.parameters.max_time_in_seconds = 30; c.parameters.num_search_workers = isci
    t0 = time.time(); st = c.Solve(kopya); return c, st, time.time() - t0
for i in range(3):
    b = C._ipucu_planini_al(k, ayar)
    c, st, sn = oneri(k)
    sol = c.ResponseProto().solution
    karar_farkli = sum(1 for sozluk in (k.x, k.mola, k.dinlenme) for v in sozluk.values() if sol[v.Index()] != h[v.Index()])
    print("fix-all: %s %.2fs amac=%d | oneri(1 isci): %s %.2fs amac=%d bound=%d | karar degiskeni farki=%d"
          % (b["durum"], b["saniye"], round(b["cozucu"].ObjectiveValue()), c.StatusName(st), sn,
             round(c.ObjectiveValue()), round(c.BestObjectiveBound()), karar_farkli))
