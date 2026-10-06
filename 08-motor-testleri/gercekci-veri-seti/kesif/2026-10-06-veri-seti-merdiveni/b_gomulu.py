# -*- coding: utf-8 -*-
"""ADIM B -- hedefi A planinin varligindan TURET, sifirdan coz, karsilastir.

    py b_gomulu.py <etiket> <saniye> [varsayilan|fm0]

Degisen TEK sey talep tablosunun `hedef` sutunu: her hucrenin hedefi, A
planinda o hucreye atanmis kisi sayisi olur. Asgari, kisiler, sablonlar,
kurallar AYNEN kalir. Boylece A plani yeni sahnede hedefi TAM tutan,
fazla mesaisiz, gecerli bir plandir -- puani bilinen bir REFERANS.

Referans puan = A planinin adalet + mola kapsamasi + fazla mesai cezasi
(hedef eksigi ve hedef asimi yapim geregi 0). Referans bir UST sinirdir:
en iyi plan bundan kotu olamaz, daha iyi olabilir.
"""
import sys
from ortak import *                              # noqa: F401,F403

etiket, saniye = sys.argv[1], int(sys.argv[2])
yapi = sys.argv[3] if len(sys.argv) > 3 else "varsayilan"
d = json.load(open(yol("A-%s.json" % etiket)))
g, P0, o0 = d["g"], d["c"]["atamalar"], d["ozet"]
v = varlik(g, P0)
g2 = copy.deepcopy(g)
degisen = 0
for t in g2["talep"]:
    yeni = v[(t["ekip"], t["gun"], t["saat"])]
    assert yeni >= t["asgari"], (t, yeni)        # A plani asgariyi tutuyordu
    if yeni != t["hedef"]:
        degisen += 1
    t["hedef"] = yeni
print("hedef toplami: eski %d  yeni %d  |  degisen hucre %d (toplam %d hucre)" % (
    sum(t["hedef"] for t in g["talep"]), sum(t["hedef"] for t in g2["talep"]),
    degisen, len(g2["talep"])))
r = degerlendir(g2, P0)
say = {}
for i in r.get("ihlaller", []):
    say[i["kural"]] = say.get(i["kural"], 0) + 1
sert = sum(1 for i in r.get("ihlaller", [])
           if i.get("agirlik") == "SERT" and not i.get("gecmis"))
R = sum(o0["dagilim"][k][0] for k in ("ADALET_DENGESI", "MOLA_KAPSAMASI", "FAZLA_MESAI"))
print("REFERANS plan yeni sahnede (bagimsiz dogrulayici): sert %d  ihlal %s" % (sert, say))
print("REFERANS puan: %d" % R)
json.dump({"g": g2, "referans_plan": P0, "referans_puan": R},
          open(yol("B-%s-sahne.json" % etiket), "w"), ensure_ascii=False)
c, kur, sure = coz_olc(g2, dict({"azami_saniye": saniye}, **YAPILAR[yapi]))
s = ozet(g2, c)
print("SIFIRDAN [%s]  kurma %.1f sn  cozum %.1f sn" % (yapi, kur, sure))
print(json.dumps(s, ensure_ascii=False))
if s.get("amac_degeri") is not None:
    print("MOTOR %d  |  REFERANS %d  |  motor referansin %.2f kati (%+.1f%%)" % (
        s["amac_degeri"], R, s["amac_degeri"] / float(R),
        100.0 * (s["amac_degeri"] - R) / R))
