import time
from ortak import *
g = sahne(0.2); k, _ = kur(g)
ayar = dict(C.VARSAYILAN, azami_saniye=30, isci_sayisi=2)
C._ipucu_ver(k, ayar); C._atamalari_sabitle(k)
p = k.m.Proto(); h = dict(zip(p.solution_hint.vars, p.solution_hint.values))
t0 = time.time(); kopya = k.m.Clone(); t_clone = time.time() - t0
pr = kopya.Proto()
t0 = time.time()
n = 0
for sozluk in (k.x, k.mola, k.dinlenme):
    for v in sozluk.values():
        d = int(h[v.Index()]); dom = pr.variables[v.Index()].domain; dom.clear(); dom.extend([d, d]); n += 1
t_edit = time.time() - t0
c = cp_model.CpSolver(); c.parameters.max_time_in_seconds = 30; c.parameters.num_search_workers = 1
t0 = time.time(); st = c.Solve(kopya); t_solve = time.time() - t0
print("clone %.2fs | %d alan duzenleme %.2fs | solve %s %.2fs | toplam %.2fs" % (t_clone, n, t_edit, c.StatusName(st), t_solve, t_clone + t_edit + t_solve))
