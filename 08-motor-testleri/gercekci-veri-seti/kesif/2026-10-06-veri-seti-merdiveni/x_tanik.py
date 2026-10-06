# -*- coding: utf-8 -*-
"""x'in TANIGI -- en az fazla mesaili plani cikar, BAGIMSIZ dogrulayiciya sor.

    py x_tanik.py <olcek> <f> <saniye>

x_kanit.py alt siniri verir (motorun modelinden); bu betik ust sinirin
gercek bir plan oldugunu dogrulayiciyla gosterir: sert ihlal 0 mi, onun
saydigi fazla mesai ayni mi.
"""
import sys
from ortak import *                              # noqa: F401,F403
from x_kanit import x_kanitla, cozmod

olcek, f, saniye = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
g = asgariyi_carp(U.sahne_uret(olcek, 0.95), f)
k, c, r = x_kanitla(g, saniye)
print(json.dumps(r, ensure_ascii=False))
at = cozmod._atamalari_cikar(k, c)
d = degerlendir(g, at)
say = {}
for i in d.get("ihlaller", []):
    if i.get("agirlik") == "SERT" and not i.get("gecmis"):
        say[i["kural"]] = say.get(i["kural"], 0) + 1
m = d.get("metrikler") or {}
print("TANIK: atama %d  |  sert ihlal %s  |  dogrulayicinin fazla mesaisi %.2f saat  |  yayinlanabilir %s" % (
    len(at), say or 0, m.get("fazla_mesai_saat"),
    (d.get("yayin_kapisi") or {}).get("yayinlanabilir")))
