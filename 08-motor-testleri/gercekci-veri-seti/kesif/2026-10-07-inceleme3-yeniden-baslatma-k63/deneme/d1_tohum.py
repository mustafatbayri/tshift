# -*- coding: utf-8 -*-
"""D1: random_seed yazilmamis vs acikca 1 -- birebir mi? (1 isci deterministik)
Ayrica ardisik Solve modeli degistiriyor mu (proto baytlari)."""
import importlib, os, sys, time
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "depo", "09-motor")
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, "testler"))
from ortools.sat.python import cp_model
from cozucu.model import Model
C = importlib.import_module("cozucu.coz")
from test_fazla_mesai_once_sifir import _sahne, _ornek_sahne

print("ortools", __import__("ortools").__version__)
p = cp_model.CpSolver().parameters
print("varsayilan random_seed:", p.random_seed)


def hazirla(g):
    k = Model(g).kur()
    k.m.ClearObjective()
    C._molalari_sabitle(k)
    C._fazla_mesaiyi_sifirla(k)
    return k


def coz(k, isci, seed=None, sure=20.0):
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = sure
    c.parameters.num_search_workers = isci
    if seed is not None:
        c.parameters.random_seed = seed
    t0 = time.time()
    d = c.Solve(k.m)
    r = c.ResponseProto()
    return (c.StatusName(d), round(time.time() - t0, 3), list(r.solution),
            r.num_branches, r.num_conflicts, r.num_booleans, round(r.deterministic_time, 6))


for ad, g in (("_sahne(5)", _sahne(gun=5)), ("_ornek(2000)", _ornek_sahne({"HEDEF_KAPSAMA": 2000}))):
    k = hazirla(g)
    once = str(k.m.Proto())
    print("\n==", ad, "degisken", len(k.m.Proto().variables))
    for isci in (1, 2):
        sonuc = {}
        for seed in (None, 1, 2, 3):
            sonuc[seed] = coz(k, isci, seed)
            st, sn, sol, br, cf, nb, dt = sonuc[seed]
            print("  isci=%d seed=%-4s %s %.3fs dal=%d catisma=%d bool=%d det=%s" % (isci, seed, st, sn, br, cf, nb, dt))
        ayni = sonuc[None][2] == sonuc[1][2]
        print("  -> isci=%d: cozum(yazilmamis)==cozum(seed 1)? %s ; dal/catisma esit? %s ; seed2 farkli cozum? %s ; seed3 farkli? %s"
              % (isci, ayni, sonuc[None][3:6] == sonuc[1][3:6],
                 sonuc[2][2] != sonuc[1][2], sonuc[3][2] != sonuc[1][2]))
    sonra = str(k.m.Proto())
    print("  model proto Solve sonrasi ayni mi:", once == sonra)
    # tekrar: ayni seed 1 isci -> ayni mi (deterministik mi)
    a = coz(k, 1, 1); b = coz(k, 1, 1)
    print("  1 isci seed=1 iki kosu ayni cozum:", a[2] == b[2], "dal:", a[3], b[3])
    a = coz(k, 1, None); b = coz(k, 1, None)
    print("  1 isci seed yazilmamis iki kosu ayni cozum:", a[2] == b[2], "dal:", a[3], b[3])
