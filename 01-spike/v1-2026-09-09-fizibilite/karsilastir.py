#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
karsilastir.py — kaydedilmiş planları yeniden ÇÖZMEDEN karşılaştırır.

cpsat.py'yi tekrar çalıştırmak dakikalar sürer. Bu betik diskteki
plan_*.json ve plan_CPSAT_*.json dosyalarını okuyup tabloyu yeniden basar.
Tüm ölçümler planla.py'deki tek metrikler() fonksiyonundan gelir, böylece
her raporda aynı sayı görünür.

Çalıştırma:  py karsilastir.py
"""

import json
import os
import sys

from degerlendirici import Degerlendirici
from planla import metrikler

PROFILLER = ["DENGELI", "KAPSAMA", "CALISAN"]


def olc(girdi, yol):
    if not os.path.exists(yol):
        return None
    plan = json.load(open(yol, encoding="utf-8"))
    d = Degerlendirici(girdi)
    m = metrikler(girdi, plan, d)
    ihl = d.calistir(plan)
    m["sert"] = sum(1 for i in ihl if i.tur == "SERT")
    m["yumusak"] = sum(1 for i in ihl if i.tur != "SERT")
    return m


def onek(yol):
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    p_onek = onek(yol)
    girdi = json.load(open(yol, encoding="utf-8"))
    hedef_top = sum(t["hedef"] for t in girdi["talep"])

    satirlar = [
        ("sert ihlal",          lambda m: str(m["sert"])),
        ("asgari kapsama",      lambda m: f"%{100*m['asgari_karsilama']:.1f}"),
        ("hedef kapsama",       lambda m: f"%{100*m['hedef_karsilama']:.1f}"),
        ("eksik kişi-saat",     lambda m: f"{m['eksik_kisi_saat']}"),
        ("fazla mesai (sa)",    lambda m: f"{m['fazla_mesai_saat']}"),
        ("adalet σ (sa)",       lambda m: f"{m['adalet_sapma']}"),
        ("atama",               lambda m: str(m["atama"])),
        ("çalışan sayısı",      lambda m: str(m["calisan"])),
        ("toplam net saat",     lambda m: f"{m['toplam_net_saat']}"),
    ]

    for p in PROFILLER:
        g = olc(girdi, f"plan_{p_onek}{p}.json")
        c = olc(girdi, f"plan_CPSAT_{p_onek}{p}.json")
        if not g and not c:
            continue
        print("\n" + "=" * 60)
        print(f"PROFİL: {p}     (talep hedefi {hedef_top} kişi-saat)")
        print("=" * 60)
        print(f"  {'':22}{'GREEDY':>16}{'CP-SAT':>16}")
        print("  " + "-" * 54)
        for ad, bic in satirlar:
            gv = bic(g) if g else "—"
            cv = bic(c) if c else "—"
            print(f"  {ad:22}{gv:>16}{cv:>16}")
        if g and c:
            fark = (c["hedef_karsilama"] - g["hedef_karsilama"]) * 100
            print(f"\n  → hedef kapsama farkı: {fark:+.2f} puan "
                  f"({g['eksik_kisi_saat'] - c['eksik_kisi_saat']:+d} kişi-saat)")
            print(f"  → fazla mesai farkı  : "
                  f"{c['fazla_mesai_saat'] - g['fazla_mesai_saat']:+.1f} sa")

    # CP-SAT senaryoları birbirinden gerçekten farklı mı?
    planlar = {}
    for p in PROFILLER:
        y = f"plan_CPSAT_{p_onek}{p}.json"
        if os.path.exists(y):
            pl = json.load(open(y, encoding="utf-8"))
            planlar[p] = {(a["calisan"], a["gun"], a["sablon"])
                          for a in pl["atamalar"]}
    if len(planlar) >= 2:
        print("\n" + "=" * 60)
        print("CP-SAT SENARYOLARI BİRBİRİNDEN NE KADAR FARKLI?")
        print("=" * 60)
        adlar = list(planlar)
        for i in range(len(adlar)):
            for j in range(i + 1, len(adlar)):
                a, b = planlar[adlar[i]], planlar[adlar[j]]
                fark = len(a ^ b) / max(1, len(a | b))
                print(f"  {adlar[i]:8} ↔ {adlar[j]:8} : %{100*fark:.1f} atama farklı")
        print()
    print()


if __name__ == "__main__":
    main()
