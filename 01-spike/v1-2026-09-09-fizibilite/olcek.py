#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
olcek.py — motor kaç çalışana kadar dayanıyor?

200 çalışanda CP-SAT 120 sn'de optimuma %0,01 yaklaştı. Asıl soru şu:
bu süre çalışan sayısıyla nasıl büyüyor? Doğrusal mı, patlıyor mu?
Cevap fiyatlandırmayı da mimariyi de belirler — 2.000 kişilik bir müşteri
için haftalık plan 5 dakikada çıkıyorsa mesele yok, 4 saat sürüyorsa
problemi parçalara bölmek gerekir.

Kullanım:
    py olcek.py                    # 200, 500, 1000, 2000 · her biri 60 sn
    py olcek.py 90                 # süre sınırını 90 sn yap
    py olcek.py 60 200 500         # sadece bu boyutlar
    py olcek.py 60 2000 --det      # deterministik süre (makine yükünden bağımsız)

DUVAR SAATİ TUZAĞI: --det olmadan CP-SAT'e 60 SANİYE verilir. Makine o an
meşgulse 60 saniyede daha az iş yapar ve sonuç kötü çıkar — motorun değil
makinenin sonucudur bu. Greedy süresi bunun göstergesidir: aynı veride
greedy süresi koşudan koşuya değişiyorsa CP-SAT sonuçları kıyaslanamaz.

OR-Tools kurulu değilse CP-SAT adımları atlanır; greedy süresi ve model
boyutu yine ölçülür (bunlar da eğrinin yarısıdır).

ÖLÇÜLEN
  - veri üretimi süresi
  - greedy planlama süresi + hedef kapsama
  - CP-SAT model kurulum süresi, değişken/kısıt sayısı
  - CP-SAT: ilk çözüme kadar geçen süre, süre sınırındaki boşluk (gap),
    hedef kapsama, ve "iyileşme eğrisi" (hangi saniyede hangi değere ulaştı)
"""

import importlib
import json
import os
import subprocess
import sys
import time

VARSAYILAN_BOYUTLAR = [200, 500, 1000, 2000]
VARSAYILAN_SURE = 60.0


def ortools_var():
    try:
        importlib.import_module("ortools.sat.python.cp_model")
        return True
    except ImportError:
        return False


def veri_uret(n, yol):
    t0 = time.time()
    r = subprocess.run([sys.executable, "uret.py", str(n), yol],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit(f"veri üretimi başarısız (n={n})")
    return time.time() - t0


def greedy_calistir(girdi):
    import planla
    from degerlendirici import Degerlendirici
    w = dict(girdi["hedef_profilleri"]["DENGELI"])
    w.setdefault("kararlilik", w.pop("tercih", 5))
    t0 = time.time()
    p = planla.Planlayici(girdi, "DENGELI", w)
    plan = p.calistir()
    sure = time.time() - t0
    d = Degerlendirici(girdi)
    m = planla.metrikler(girdi, plan, d)
    sert = sum(1 for i in d.calistir(plan) if i.tur == "SERT")
    return sure, m, sert, plan


def model_boyutu_sahte(girdi):
    """OR-Tools YOKKEN model boyutunu ölç.

    Sahte modül saf Python'dur; ölçtüğü SÜRE gerçek CP-SAT'in model kurulum
    süresini YANSITMAZ (gerçeği C++ tarafındadır, çok daha hızlı). Buradan
    yalnız değişken/kısıt SAYILARI anlamlıdır.
    """
    import cpsat
    from cpsat_kontrol import SahteModul
    v = cpsat.Veri(girdi)
    m, dv = cpsat.kur_model(v, "DENGELI", SahteModul())
    return len(m.degiskenler), len(m.kisitlar)


def cpsat_calistir(girdi, sure_siniri, det=False):
    from ortools.sat.python import cp_model
    import cpsat
    from degerlendirici import Degerlendirici
    import planla

    v = cpsat.Veri(girdi)
    t0 = time.time()
    m, dv = cpsat.kur_model(v, "DENGELI", cp_model)
    kurulum = time.time() - t0
    try:
        proto = m.Proto()
        nd, nk = len(proto.variables), len(proto.constraints)
    except Exception:
        nd = nk = None

    class Izleyici(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.kayit = []
            self.bas = time.time()

        def on_solution_callback(self):
            gecen = time.time() - self.bas
            try:
                sinir = self.BestObjectiveBound()
            except Exception:
                sinir = None
            self.kayit.append((gecen, self.ObjectiveValue(), sinir))

    solver = cp_model.CpSolver()
    if det:
        # Deterministik süre: duvar saati yerine yapılan İŞ miktarı sayılır.
        # Makine yükünden etkilenmez, dolayısıyla koşular kıyaslanabilir olur.
        solver.parameters.max_deterministic_time = sure_siniri
    else:
        solver.parameters.max_time_in_seconds = sure_siniri
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 20260907
    izl = Izleyici()
    t1 = time.time()
    st = solver.Solve(m, izl)
    cozum_suresi = time.time() - t1
    durum = solver.StatusName(st)

    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"durum": durum, "kurulum": kurulum, "sure": cozum_suresi,
                "kayit": izl.kayit, "degisken": nd, "kisit": nk}

    plan = cpsat.plan_cikar(v, dv, solver, "DENGELI")
    d = Degerlendirici(girdi)
    met = planla.metrikler(girdi, plan, d)
    sert = sum(1 for i in d.calistir(plan) if i.tur == "SERT")
    obj = solver.ObjectiveValue()
    bound = solver.BestObjectiveBound()
    gap = abs(bound - obj) / abs(bound) * 100 if bound else 0.0
    return {"durum": durum, "kurulum": kurulum, "sure": cozum_suresi,
            "kayit": izl.kayit, "metrik": met, "sert": sert, "gap": gap,
            "degisken": nd, "kisit": nk,
            "ilk_cozum": izl.kayit[0][0] if izl.kayit else None}


def main():
    args = [a for a in sys.argv[1:]]
    det = "--det" in args
    args = [a for a in args if not a.startswith("--")]
    sure = float(args[0]) if args else VARSAYILAN_SURE
    boyutlar = [int(a) for a in args[1:]] or VARSAYILAN_BOYUTLAR

    ort = ortools_var()
    print("=" * 74)
    print("ÖLÇEK TESTİ — motor çalışan sayısıyla nasıl büyüyor?")
    print("=" * 74)
    print(f"  boyutlar        : {boyutlar}")
    print(f"  CP-SAT süre sın.: {sure:.0f} "
          + ("DETERMİNİSTİK birim / boyut  (makine yükünden bağımsız)"
             if det else "sn (duvar saati) / boyut"))
    if not det:
        print("  UYARI           : duvar saati ölçümü makine yüküne duyarlıdır.")
        print("                    Karşılaştırılabilir sonuç için --det kullanın")
        print("                    ya da makineyi boşken koşturun.")
    if not ort:
        print("  OR-Tools YOK    : CP-SAT adımları atlanacak "
              "(greedy + model boyutu yine ölçülür)")
    print()

    sonuc = []
    for n in boyutlar:
        yol = f"girdi_{n}.json"
        print(f"--- {n} çalışan ---")
        t_veri = veri_uret(n, yol)
        girdi = json.load(open(yol, encoding="utf-8"))
        aktif = sum(1 for c in girdi["calisanlar"] if c["durum"] == "AKTIF")
        hedef_top = sum(t["hedef"] for t in girdi["talep"])
        print(f"    veri  : {t_veri:5.1f} sn  ({aktif} aktif, "
              f"{hedef_top} kişi-saat talep)")

        t_g, m_g, sert_g, _ = greedy_calistir(girdi)
        print(f"    greedy: {t_g:5.1f} sn  hedef %{100*m_g['hedef_karsilama']:.1f}"
              f"  sert ihlal {sert_g}"
              + ("   ← greedy tek çekirdekli ve deterministiktir;"
                 " bu süre makine hızı göstergesidir" if n == boyutlar[0] else ""))

        satir = {"n": n, "aktif": aktif, "t_veri": t_veri,
                 "t_greedy": t_g, "greedy_hedef": m_g["hedef_karsilama"],
                 "greedy_sert": sert_g, "degisken": 0, "kisit": 0}

        if not ort:
            nd, nk = model_boyutu_sahte(girdi)
            satir["degisken"], satir["kisit"] = nd, nk
            print(f"    model : {nd:,} değişken, {nk:,} kısıt  "
                  f"(süre ölçülmedi — sahte modül)")
        else:
            r = cpsat_calistir(girdi, sure, det)
            satir["cpsat"] = r
            satir["degisken"] = r.get("degisken") or 0
            satir["kisit"] = r.get("kisit") or 0
            print(f"    model : {r['kurulum']:5.1f} sn  "
                  f"{satir['degisken']:,} değişken, {satir['kisit']:,} kısıt")
            if "metrik" in r:
                print(f"    CP-SAT: {r['sure']:5.1f} sn  "
                      f"hedef %{100*r['metrik']['hedef_karsilama']:.1f}"
                      f"  gap %{r['gap']:.2f}  ({r['durum']})"
                      f"  sert ihlal {r['sert']}")
                if r["kayit"]:
                    print(f"            ilk çözüm {r['ilk_cozum']:.1f} sn'de, "
                          f"{len(r['kayit'])} iyileştirme")
                    for gecen, deg, _s in r["kayit"][:1] + r["kayit"][-1:]:
                        print(f"              {gecen:6.1f} sn → {deg:,.0f}")
            else:
                print(f"    CP-SAT: ÇÖZÜM YOK ({r['durum']}) — "
                      f"{r['sure']:.1f} sn")
        sonuc.append(satir)
        print()

    # ---- özet tablo ----
    print("=" * 74)
    print("ÖZET")
    print("=" * 74)
    bas = f"  {'çalışan':>8}{'değişken':>11}{'kısıt':>10}{'greedy sn':>11}"
    if ort:
        bas += f"{'CPSAT sn':>10}{'gap %':>8}{'hedef %':>9}"
    print(bas)
    print("  " + "-" * 70)
    for s in sonuc:
        sat = (f"  {s['n']:>8}{s['degisken']:>11,}{s['kisit']:>10,}"
               f"{s['t_greedy']:>11.1f}")
        if ort and "metrik" in s.get("cpsat", {}):
            c = s["cpsat"]
            sat += (f"{c['sure']:>10.1f}{c['gap']:>8.2f}"
                    f"{100*c['metrik']['hedef_karsilama']:>9.1f}")
        elif ort:
            sat += f"{'—':>10}{'—':>8}{'—':>9}"
        print(sat)

    if ort and len(sonuc) >= 2:
        print("\n  YORUM")
        ilk, son = sonuc[0], sonuc[-1]
        kat_n = son["n"] / ilk["n"]
        kat_v = son["degisken"] / max(1, ilk["degisken"])
        print(f"    çalışan {kat_n:.0f}× arttığında değişken sayısı {kat_v:.1f}× arttı")
        tamam = [s for s in sonuc if "metrik" in s.get("cpsat", {})]
        if tamam:
            kotu = [s for s in tamam if s["cpsat"]["gap"] > 1.0]
            if kotu:
                print(f"    süre sınırında %1'in altına inemeyen ilk boyut: "
                      f"{kotu[0]['n']} çalışan")
                print("    → bu boyuttan sonra ya daha uzun süre ya da problemi")
                print("      ekip/gün bazında parçalara bölmek gerekir.")
            else:
                print(f"    tüm boyutlarda gap %1'in altında — "
                      f"{sure:.0f} sn bu ölçekler için yeterli.")

    with open("olcek_sonuc.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "cpsat"}
                   | ({"cpsat_gap": s["cpsat"].get("gap"),
                       "cpsat_sure": s["cpsat"].get("sure"),
                       "cpsat_durum": s["cpsat"].get("durum")}
                      if "cpsat" in s else {})
                   for s in sonuc], f, ensure_ascii=False, indent=1)
    print("\n  olcek_sonuc.json yazıldı\n")


if __name__ == "__main__":
    main()
