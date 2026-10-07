# -*- coding: utf-8 -*-
"""D7 (kapsam disi gozlem): donmus gun + oturmayan mevcut plan -> iki asama yolu.
`_molalari_sabitle` donmus gunun [1,1]/[0,0] mola alanlarina dokunuyor mu, sonra
[0,1]'e mi aciyor? Ilk asama yanlis 'kanit' uretiyor mu?"""
import copy
from ortak import *
from test_fazla_mesai_once_sifir import _sahne, AYAR_URUN

g = _sahne(gun=5)
once = C.coz(g, dict(AYAR_URUN))
assert once["durum"] == "cozuldu"
g2 = copy.deepcopy(g)
g2["donmus_gunler"] = [0]
plan = copy.deepcopy(once["atamalar"])
# gun 0'in molasini ideal yerden baska bir yere kaydir (sahada olabilecek bir plan)
k0 = Model(copy.deepcopy(g)).kur()
ideal = k0.sabit_mola_secimi(k0.sablonlar[0])
print("ideal yemek slotu:", ideal[0], "| adaylar:", sorted({s for (_, _, _, s) in k0.mola if s is not None})[:8])
for a in plan:
    if a["gun"] == 0:
        for m in a["molalar"]:
            if m["tip"] == "yemek":
                m["bas"] = ideal[0] + 1.0; m["bit"] = m["bas"] + 1.0
# oturmayan bir satir: sablon yok -> _plandan_ipucu False -> iki asama yolu
plan.append({"calisan": "C1", "gun": 3, "sablon": "YOK", "bas": 8, "bit": 17, "molalar": []})
g2["mevcut_plan"] = plan
k = Model(copy.deepcopy(g2)).kur()
p = k.m.Proto()
donmus_mola = {ix: list(p.variables[ix].domain) for ix in [v.Index() for (e, d, t, s), v in k.mola.items() if d == 0]}
print("donmus gun 0 mola alanlari (once):", sorted(set(map(tuple, donmus_mola.values()))), "| [1,1] sayisi:", sum(1 for d in donmus_mola.values() if d == [1, 1]))
c = C.coz(g2, dict(AYAR_URUN), kuruldu=k)
ist = c["cozum_istatistikleri"]
print("durum:", c["durum"], "| baslangic_plani_kullanildi:", ist["baslangic_plani_kullanildi"], "| iki_asama:", ist["iki_asama"])
print("fm_once:", {a: (ist["fazla_mesai_once_sifir"] or {}).get(a) for a in ("bulundu", "kanitlandi_yok", "denemeler")})
print("notlar:", [n for n in c["uygulanmayan_notlar"] if "fazla" in n or "baslangic" in n or "donmus" in n])
p = k.m.Proto()
sonra = {ix: list(p.variables[ix].domain) for ix in donmus_mola}
degisen = [(ix, donmus_mola[ix], sonra[ix]) for ix in donmus_mola if donmus_mola[ix] != sonra[ix]]
print("donmus gun 0 mola alanlari DEGISEN sayisi:", len(degisen), "| ornek:", degisen[:3])
