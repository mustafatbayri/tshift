# -*- coding: utf-8 -*-
"""D. Kurulum bedeli: 0.1 ve 0.2 olcekte model kurma suresi, degisken ve kisit sayisi,
kural acik (veri setinin varsayilani) / kapali (kural listeden cikarilmis). 3'er tekrar.
Ayrica 0.1 olcekte bir cozum: amac kirilimi `deger` vs dogrulayici satirlari (gercek sahnede).
Kullanim: python3 d4_kurulum.py [cozum_saniye=40]   -> d4_kurulum.out"""
import copy
import json
import sys
import time

from ortak import (model_kur, proto_ozeti, coz, degerlendir, KURAL, rot_satirlari, rot_kirilim,
                   yuvarla, benim_say, dairesel_geri)
from uret_veri_seti import sahne_uret

SANIYE = float(sys.argv[1]) if len(sys.argv) > 1 else 40

for olcek in (0.1, 0.2):
    g = sahne_uret(olcek, 0.95)
    g_kapali = copy.deepcopy(g)
    g_kapali["kurallar"] = [k for k in g_kapali["kurallar"] if k.get("kod") != KURAL]
    assert any(k["kod"] == KURAL for k in g["kurallar"]) and not any(k["kod"] == KURAL for k in g_kapali["kurallar"])
    print("\n=== olcek %s: %d kisi, %d sablon, %d ekip ===" % (olcek, len(g["calisanlar"]), len(g["vardiya_sablonlari"]),
                                                              len({t.get("ekip") for t in g["vardiya_sablonlari"]})))
    for ad, girdi in (("kural ACIK", g), ("kural KAPALI", g_kapali)):
        sureler, ozet = [], None
        for _ in range(3):
            k, sn = model_kur(girdi)
            sureler.append(sn)
            ozet = proto_ozeti(k)
        print("  %-13s kurma sn: %s | %s" % (ad, ["%.2f" % s for s in sureler], ozet))
    # sablon cifti analizi: kisi basina geri sablon cifti sayisi (ekip ici)
    k, _ = model_kur(g)
    ciftler = {}
    for c in k.calisanlar:
        s = k._sablonlari(c)
        n = sum(1 for a in s for b in s if yuvarla(dairesel_geri(a["bas"], b["bas"])) > 0)
        ciftler[c["id"]] = (len(s), n)
    print("  kisi basina (sablon sayisi, geri sablon cifti): dagilim", sorted({v: list(ciftler.values()).count(v) for v in set(ciftler.values())}.items()))
    print("  beklenen ro kisit = sum(kisi: geri cift x 6 gun cifti) =", sum(n * 6 for _, n in ciftler.values()),
          "(gecmis gun -1 kaydi olan kisi yok -> pazartesi terimi yok)" if not any(c.get("gecmis_vardiyalar") for c in g["calisanlar"]) else "")

# 0.1 olcekte gercek cozum: deger vs dogrulayici
g = sahne_uret(0.1, 0.95)
t0 = time.time()
c = coz(g, {"azami_saniye": SANIYE, "isci_sayisi": 2})
print("\n=== 0.1 olcek cozum (urun yolu varsayilanlari, %.0f sn): %s, %.0f sn, durma %s, mola_adimi %s ===" % (
    SANIYE, c["durum"], time.time() - t0, c["cozum_istatistikleri"].get("durma_sebebi"), c["cozum_istatistikleri"].get("mola_adimi")))
if c["durum"] == "cozuldu":
    r = degerlendir(g, c["atamalar"])
    satirlar = rot_satirlari(r)
    kir = rot_kirilim(c)
    print("  amac kirilimi:", kir)
    print("  metrik: gecis %s saat %s | dogrulayici: %d satir, %.2f saat | inceleme sayimi: %s"
          % (c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"], len(satirlar),
             sum(i["olculen"] for i in satirlar), [len(benim_say(g, c["atamalar"])), round(sum(s[2] for s in benim_say(g, c["atamalar"])), 2)]))
    print("  deger == yuvarlanmis toplam:", (kir or {}).get("deger", 0) == sum(yuvarla(i["olculen"]) for i in satirlar),
          "| satirlar:", [(i["calisan"], i["gun"], i["olculen"]) for i in satirlar])
    # "gece -> bos gun -> erken baslangic" deseni: baslangic gununde art arda degil, takvimde
    # (gece ertesi sabahi kapliyor) -- tanim bunu saymaz; kac kez olusuyor?
    bas = {}
    for a in c["atamalar"]:
        bas.setdefault(a["calisan"], {})[a["gun"]] = (a["bas"], a["bit"])
    desen = []
    for kisi, gunler in bas.items():
        for d in sorted(gunler):
            b0, e0 = gunler[d]
            if e0 > 24 and d + 1 not in gunler and d + 2 in gunler:
                b2 = gunler[d + 2][0]
                h = dairesel_geri(b0, b2)
                desen.append((kisi, d, b0, e0, b2, h))
    print("  gece (bitis > 24) -> ertesi gun bos -> iki gun sonra calisma: %d kez; bunlardan dairesel 'geri' olani: %d (%s)"
          % (len(desen), sum(1 for x in desen if x[5] > 0), [(x[0], x[1], x[2], x[4], x[5]) for x in desen if x[5] > 0][:8]))
