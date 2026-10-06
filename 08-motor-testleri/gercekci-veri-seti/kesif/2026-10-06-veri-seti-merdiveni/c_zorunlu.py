# -*- coding: utf-8 -*-
"""Zorunlu fazla mesaili sahnede MOTOR: fazla mesaisi x'e ne kadar yakin?

    py c_zorunlu.py <olcek> <f> <saniye> [varsayilan|fm0]
"""
import sys
from ortak import *                              # noqa: F401,F403

olcek, f, saniye = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
yapi = sys.argv[4] if len(sys.argv) > 4 else "varsayilan"
g = asgariyi_carp(U.sahne_uret(olcek, 0.95), f)
c, kur, sure = coz_olc(g, dict({"azami_saniye": saniye}, **YAPILAR[yapi]))
s = ozet(g, c)
print("[%s]  olcek %.1f  f %.2f  butce %d sn  |  kurma %.1f sn  cozum %.1f sn" % (
    yapi, olcek, f, saniye, kur, sure))
print(json.dumps(s, ensure_ascii=False))
print("not:", [n for n in (c.get("uygulanmayan_notlar") or []) if "fazla mesaisiz" in n])
