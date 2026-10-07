# -*- coding: utf-8 -*-
"""Ortak yardimcilar: dondurulmus depo, sahne uretimi, model kurma."""
import copy, importlib, os, sys, time
# Depo icinde arsivlendi (7 Ekim 20:30): inceleme sirasinda "depo/" dondurulmus
# bir kopyaydi; burada depo kokune gore cozulur (kesif/<klasor>/deneme -> kok).
KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
D = os.path.join(KOK, "09-motor")
G = os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti")
for yol in (D, os.path.join(D, "testler"), G):
    if yol not in sys.path:
        sys.path.insert(0, yol)
from ortools.sat.python import cp_model          # noqa
from cozucu.model import Model                    # noqa
import dogrulayici                                # noqa
C = importlib.import_module("cozucu.coz")
from uret_veri_seti import sahne_uret             # noqa


def sahne(olcek=0.1, doluluk=0.95):
    return sahne_uret(olcek, doluluk)


def kur(g):
    t0 = time.time()
    k = Model(copy.deepcopy(g)).kur()
    return k, time.time() - t0


def ozet(k):
    p = k.m.Proto()
    return "degisken=%d kisit=%d x=%d mola=%d dinlenme=%d ceza=%d" % (
        len(p.variables), len(p.constraints), len(k.x), len(k.mola), len(k.dinlenme), len(k.cezalar))


def tam_amac(k, cozucu_veya_degerler):
    """Verilen x/mola/dinlenme degerleri icin ceza degiskenlerinin SIKI (en
    kucuk) degerleriyle amac: ayni modelin kopyasinda karar degiskenleri
    sabitlenir, amac en kucuklenir."""
    kopya = k.m.Clone()
    kopya.ClearHints()
    proto = kopya.Proto()
    al = (cozucu_veya_degerler.Value if hasattr(cozucu_veya_degerler, "Value")
          else (lambda v: cozucu_veya_degerler[v.Index()]))
    for sozluk in (k.x, k.mola, k.dinlenme):
        for v in sozluk.values():
            d = int(al(v))
            dom = proto.variables[v.Index()].domain
            dom.clear(); dom.extend([d, d])
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = 60
    c.parameters.num_search_workers = 2
    st = c.Solve(kopya)
    return c.StatusName(st), (int(round(c.ObjectiveValue())) if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None), c
