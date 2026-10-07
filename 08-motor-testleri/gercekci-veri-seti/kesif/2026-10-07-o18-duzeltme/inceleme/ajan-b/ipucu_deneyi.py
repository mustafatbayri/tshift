"""Mikro deney: CP-SAT 9.15'te TAM ve GECERLI ipucu ilk cozum olarak raporlanir mi?
Kucuk bir kapsama modeli: 30 kisi x 7 gun atama, hedef kapsama ile 'eksik' gevsek
degiskeni; ipucu = gecerli ama kotu bir plan. Iki varyant: (a) ipucudaki gevsek
degiskenler SIKI, (b) gevsek degiskenler GEVSEK (amacsiz cozumden alinmis gibi)."""
import time
from ortools.sat.python import cp_model

class Sayac(cp_model.CpSolverSolutionCallback):
    def __init__(s):
        super().__init__(); s.egri=[]; s.t0=time.time()
    def on_solution_callback(s):
        s.egri.append((round(time.time()-s.t0,3), s.ObjectiveValue()))

def kur(gevsek_ipucu, isci):
    m=cp_model.CpModel(); N,G=30,7
    x={(i,g):m.NewBoolVar(f"x{i}_{g}") for i in range(N) for g in range(G)}
    for i in range(N):
        m.Add(sum(x[i,g] for g in range(G))<=5)
    hedef=[22,22,22,22,22,10,10]
    eksik=[m.NewIntVar(0,N,f"eksik{g}") for g in range(G)]
    fazla=[m.NewIntVar(0,N,f"fazla{g}") for g in range(G)]
    for g in range(G):
        m.Add(eksik[g] >= hedef[g]-sum(x[i,g] for i in range(N)))
        m.Add(fazla[g] >= sum(x[i,g] for i in range(N))-hedef[g])
    m.Minimize(sum(9*e for e in eksik)+sum(3*f for f in fazla))
    # ipucu: herkes Pzt-Cum calisir (hafta sonu bos) -> hafta ici 30>22 fazla 8x5, hafta sonu eksik 10x2
    hint={}
    for i in range(N):
        for g in range(G):
            hint[x[i,g]] = 1 if g<5 else 0
    for g in range(G):
        kap = sum(hint[x[i,g]] for i in range(N))
        e_siki = max(0,hedef[g]-kap); f_siki=max(0,kap-hedef[g])
        if gevsek_ipucu:
            hint[eksik[g]] = min(N, e_siki+7); hint[fazla[g]] = min(N, f_siki+7)
        else:
            hint[eksik[g]] = e_siki; hint[fazla[g]] = f_siki
    for v,d in hint.items(): m.AddHint(v,d)
    ipucu_amac = sum(9*hint[e] for e in eksik)+sum(3*hint[f] for f in fazla)
    return m, ipucu_amac

for gevsek in (False, True):
    for isci in (1, 8):
        m, ia = kur(gevsek, isci)
        s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=3; s.parameters.num_search_workers=isci
        cb=Sayac(); st=s.Solve(m, cb)
        print(f"gevsek_ipucu={gevsek} isci={isci} ipucu_amac={ia} durum={s.StatusName(st)} ilk_cozumler={cb.egri[:3]} son={cb.egri[-1] if cb.egri else None} n={len(cb.egri)}")
