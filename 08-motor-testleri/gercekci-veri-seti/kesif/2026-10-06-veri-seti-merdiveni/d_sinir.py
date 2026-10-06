# -*- coding: utf-8 -*-
"""Gomulu sahnede ORTAK arama (tek model): KURESEL alt sinir ne diyor?

    py d_sinir.py <etiket> <saniye>

Once b_gomulu.py kosmus olmali (sahneyi o yazar). Iki asamali akis
kapatilir (esik cok buyuk) ki cozulen model TAM model olsun ve alt sinir
kuresel alana yazilsin (O-16). Bu yolun PLANI kotudur (bilinen sey);
buradan yalniz alt sinir okunur.
"""
import sys
from ortak import *                              # noqa: F401,F403

etiket, saniye = sys.argv[1], int(sys.argv[2])
d = json.load(open(yol("B-%s-sahne.json" % etiket)))
g, R = d["g"], d["referans_puan"]
c, kur, sure = coz_olc(g, {"azami_saniye": saniye, "iki_asama_esigi": 10 ** 9,
                           "durgunluk_saniye": saniye, "hedef_bosluk": 0.0})
s = ozet(g, c)
print("ORTAK ARAMA  kurma %.1f sn  cozum %.1f sn  |  referans %d" % (kur, sure, R))
print(json.dumps(s, ensure_ascii=False))
