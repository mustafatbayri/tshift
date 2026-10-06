# -*- coding: utf-8 -*-
"""Zorunlu fazla mesai -- asgari talebi f ile carp, EN AZ toplam fazla
mesaiyi (x, dakika) cozucuye kanitlat.

    py x_kanit.py <olcek> <saniye> <f1,f2,...> [ekip1,ekip2]

Model motorun KENDI modelidir (butun sert kurallar); amac yalniz fazla
mesai degiskenlerinin toplamidir. Molalar sablon idealinde sabitlenir:
saha tabani (`SAHADA_ASGARI.asgari_sahada`) 0 oldugu icin mola yeri hicbir
sert kurali etkilemez, yani x'i degistirmez.

OPTIMAL   : x kanitli (alt sinir = bulunan).
FEASIBLE  : bulunan x bir UST sinir; alt sinir yanindaki sayi.
INFEASIBLE: bu asgari, profil tavaniyla bile karsilanamaz (plan imkansiz).
"""
import importlib
import sys
from ortak import *                              # noqa: F401,F403
from ortools.sat.python import cp_model

cozmod = importlib.import_module("cozucu.coz")   # `cozucu.coz` adi fonksiyona cozulur


def x_kanitla(g, saniye, isci=2):
    k = Model(copy.deepcopy(g)).kur()
    fm = [v for (a, v) in k.cezalar if v.Name().startswith("fm_")]
    cozmod._molalari_sabitle(k)
    k.m.Minimize(sum(fm))
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = saniye
    c.parameters.num_search_workers = isci
    t0 = time.time()
    d = c.Solve(k.m)
    var = d in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return k, c, {
        "durum": c.StatusName(d),
        "x_dk": c.ObjectiveValue() if var else None,
        "alt_sinir_dk": c.BestObjectiveBound() if var else None,
        "fm_degisken": len(fm), "sn": round(time.time() - t0, 1),
        "kisi_dk": (sorted([int(c.Value(v)) for v in fm if c.Value(v)], reverse=True)
                    if var else None)}


if __name__ == "__main__":
    olcek, saniye = float(sys.argv[1]), int(sys.argv[2])
    ekipler = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    g = U.sahne_uret(olcek, 0.95)
    for f in [float(x) for x in sys.argv[3].split(",")]:
        g2 = asgariyi_carp(g, f, ekipler)
        _, _, r = x_kanitla(g2, saniye)
        print("f=%.2f  ekip=%s  asgari toplam %d  ->  %s" % (
            f, ",".join(ekipler) if ekipler else "hepsi",
            sum(t["asgari"] for t in g2["talep"]), json.dumps(r, ensure_ascii=False)))
        sys.stdout.flush()
