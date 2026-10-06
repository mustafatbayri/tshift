# -*- coding: utf-8 -*-
"""ADIM A -- taban sahneyi uret, FAZLA MESAISIZ bir plan bul ve sakla.

    py a_plan.py <olcek> <saniye> <etiket> [tohum]

`tohum` verilirse CP-SAT'a random_seed olarak gecer: gomulecek plan,
urunun varsayilan aramasinin ilk bulacagi plandan FARKLI bir yerden gelsin
diye (ayni tohumla motor kendi planini yeniden buluyor -- OKU-BENI #4).
"""
import sys
from ortak import *                              # noqa: F401,F403

olcek, saniye, etiket = float(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ayar = {"azami_saniye": saniye, "fazla_mesai_once_sifir": True}
if len(sys.argv) > 4:
    ayar["cozucu_parametreleri"] = {"random_seed": int(sys.argv[4])}
g = U.sahne_uret(olcek, 0.95)
print("kisi %d  hucre %d  hedef %d  asgari %d" % (
    len(g["calisanlar"]), len(g["talep"]),
    sum(t["hedef"] for t in g["talep"]), sum(t["asgari"] for t in g["talep"])))
c, kur, sure = coz_olc(g, ayar)
s = ozet(g, c)
print("kurma %.1f sn  cozum %.1f sn" % (kur, sure))
print(json.dumps(s, ensure_ascii=False))
json.dump({"g": g, "c": c, "ozet": s}, open(yol("A-%s.json" % etiket), "w"),
          ensure_ascii=False)
print("yazildi:", yol("A-%s.json" % etiket))
