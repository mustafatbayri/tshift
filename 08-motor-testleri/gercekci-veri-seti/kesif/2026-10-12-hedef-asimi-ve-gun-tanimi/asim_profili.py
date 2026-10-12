# -*- coding: utf-8 -*-
"""Asim nerede? Hucre basina (atanan - hedef) dagilimi, ekip x saat profili, en buyuk hucrelerdeki sablonlar."""
import collections, io, json, os, sys
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor")); sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
from dogrulayici import kurallar as K, zaman
from uret_veri_seti import sahne_uret
g = sahne_uret(1.0, 0.95)
uyelik, mod = K.uyelik_haritasi(g), K.cok_ekipli_sayim(g)
for yol in sys.argv[1:]:
    d = json.load(io.open(yol, encoding="utf-8"))
    at = K._kapsama_atamalari(g, d["cikti"]["atamalar"])
    fark = collections.Counter(); profil = collections.defaultdict(list); enb = []
    talep = collections.defaultdict(dict)
    for t, gun, saat in K._talep_hucreleri(g):
        h = t.get("hedef")
        if h is None: continue
        kisiler = [a for a in at if K.ekibe_sayilir(a, t.get("ekip"), uyelik, mod) and zaman.atanmis_mi(a, gun, saat)]
        f = len(kisiler) - h
        fark[max(f, 0)] += 1
        profil[(t["ekip"], saat)].append(f)
        talep[(t["ekip"], saat)][gun] = (h, t.get("asgari"))
        if f > 0:
            enb.append((f, t["ekip"], gun, saat, h, collections.Counter(a.get("sablon") for a in kisiler)))
    enb.sort(reverse=True)
    print("==== %s" % os.path.basename(yol))
    print("  hucre basina asim dagilimi (asim -> hucre sayisi):", dict(sorted(fark.items())))
    print("  en buyuk 8 hucre (asim, ekip, gun, saat, hedef, sablonlar):")
    for e in enb[:8]:
        print("    ", e)
    print("  ekip x saat ortalama asim (gunler uzerinden; >= 1 olanlar):")
    for (ekip, saat), v in sorted(profil.items()):
        ort = sum(v) / len(v)
        if ort >= 1.0:
            h = sorted(set(x[0] for x in talep[(ekip, saat)].values()))
            print("    %-10s saat %2d: ort. asim %+.1f (hedef %s)" % (ekip, saat, ort, h))
