# -*- coding: utf-8 -*-
"""D2 (0.1 olcek, 49 kisi): fazla mesaisiz + molalar sabit AMACSIZ arama.
  a) 1 isci: seed yazilmamis vs 1 vs 2 vs 3 -- cozum/dal/catisma/det. sure
  b) 2 isci: seed yazilmamis x3 vs 1 x3 -- sure ve cozum
  c) Solve modeli degistiriyor mu (proto metni)"""
import sys, time
from ortak import *

g = sahne(0.1)
k, _ = kur(g)
print(ozet(k))
k.m.ClearObjective()
sab = C._molalari_sabitle(k)
fm = C._fazla_mesaiyi_sifirla(k)
print("mola sabitlenen", len(sab), "fm sifirlanan", len(fm))
once = str(k.m.Proto())


def coz(isci, seed=None, sure=60.0):
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = sure
    c.parameters.num_search_workers = isci
    if seed is not None:
        c.parameters.random_seed = seed
    t0 = time.time()
    d = c.Solve(k.m)
    r = c.ResponseProto()
    return dict(durum=c.StatusName(d), sn=round(time.time() - t0, 2), sol=tuple(r.solution),
                dal=r.num_branches, catisma=r.num_conflicts, det=round(r.deterministic_time, 4),
                bool=r.num_booleans)


def yaz(etiket, s):
    print("  %-22s %s %6.2fs dal=%d catisma=%d det=%s bool=%d" % (etiket, s["durum"], s["sn"], s["dal"], s["catisma"], s["det"], s["bool"]))
    sys.stdout.flush()


print("\n(a) 1 isci")
a = {}
for seed in (None, 1, 2, 3):
    a[seed] = coz(1, seed); yaz("seed=%s" % seed, a[seed])
a["None2"] = coz(1, None); yaz("seed=None tekrar", a["None2"])
print("  yazilmamis == seed1 cozum:", a[None]["sol"] == a[1]["sol"], "| dal/catisma/det esit:", (a[None]["dal"], a[None]["catisma"], a[None]["det"]) == (a[1]["dal"], a[1]["catisma"], a[1]["det"]))
print("  yazilmamis tekrar ayni:", a[None]["sol"] == a["None2"]["sol"])
print("  seed2 != seed1 cozum:", a[2]["sol"] != a[1]["sol"], "| seed3 != seed1:", a[3]["sol"] != a[1]["sol"])
print("  seed2 vs seed1 x farki:", sum(1 for v in k.x.values() if a[2]["sol"][v.Index()] != a[1]["sol"][v.Index()]), "/", len(k.x))

print("\n(b) 2 isci")
for seed in (None, 1, 2):
    for i in range(3):
        yaz("seed=%s #%d" % (seed, i + 1), coz(2, seed))

print("\n(c) model proto Solve sonrasi ayni mi:", once == str(k.m.Proto()))
