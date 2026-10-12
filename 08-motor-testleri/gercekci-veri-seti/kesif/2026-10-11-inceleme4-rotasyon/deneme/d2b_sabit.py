# -*- coding: utf-8 -*-
"""B (ek). Hedef plan `sabit_atamalar` ile ZORLANIR: motorun plani rastgele hedef planin
kendisi olur (sert kurallari tutuyorsa). Boylece amac terimi (i) cok sayida geri ciftle
sinanir: deger == gecmis olmayan satirlarin yuvarlanmis toplami, her sahnede.
Kullanim: python3 d2b_sabit.py [adet=300] [tohum=5]  -> d2b_sabit.json"""
import copy
import json
import random
import sys
import time

import d2_rastgele as D
from ortak import degerlendir, KURAL, kural

ADET = int(sys.argv[1]) if len(sys.argv) > 1 else 300
TOHUM = int(sys.argv[2]) if len(sys.argv) > 2 else 5


def main():
    rnd = random.Random(TOHUM)
    kayit = []
    t0 = time.time()
    uretilen = 0
    while len(kayit) < ADET:
        uretilen += 1
        g, bilgi = D.sahne_uret(rnd)
        if bilgi["kural"] != "acik":
            continue
        # hedef plani yeniden kur (sahne_uret icinde uretilen plan talebe dondu; buradan ayri bir plan)
        plan = D.hedef_plan_uret(rnd, [c["id"] for c in g["calisanlar"]], list(range(bilgi["gun"])), g["vardiya_sablonlari"])
        if not plan:
            continue
        # ortusme CAKISMA_YOK ile raporlanir (V-1): temizlik kontrolune o kural da girer;
        # donmus gunlerin satirlari da kontrole dahil (sabit satirla cakismasin)
        g["kurallar"].append(kural("CAKISMA_YOK"))
        donmus = set(g.get("donmus_gunler") or [])
        kontrol = [a for a in plan if a["gun"] not in donmus] + [a for a in (g.get("mevcut_plan") or []) if a.get("sablon")]
        rapor = degerlendir(g, kontrol)
        if any(i["agirlik"] == "SERT" for i in rapor["ihlaller"]):
            continue
        g["sabit_atamalar"] = [{"calisan": a["calisan"], "gun": a["gun"], "sablon": a["sablon"]}
                               for a in plan if a["gun"] not in (g.get("donmus_gunler") or [])]
        g["talep"] = D.talep_uret(plan, False)
        bilgi["no"] = len(kayit)
        bilgi["sabit"] = len(g["sabit_atamalar"])
        try:
            D.incele(g, bilgi)
        except Exception as e:                      # noqa
            bilgi["durum"] = "HATA"
            bilgi["hata"] = repr(e)
        bilgi["girdi"] = g if (bilgi.get("farklar") or bilgi["durum"] != "cozuldu") else None
        kayit.append(bilgi)
        if bilgi.get("farklar") or bilgi["durum"] == "HATA":
            print("sahne %d: %s %s" % (bilgi["no"], bilgi["durum"], bilgi.get("farklar") or bilgi.get("hata")))
    json.dump(kayit, open(__file__.replace(".py", ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0, default=str)
    cozulen = [k for k in kayit if k["durum"] == "cozuldu"]
    print("\nTOPLAM %d sahne (%d uretildi), cozuldu %d, sure %.0f sn" % (len(kayit), uretilen, len(cozulen), time.time() - t0))
    print("durma sebepleri:", {s: len([k for k in cozulen if k.get("durma_sebebi") == s]) for s in {k.get("durma_sebebi") for k in cozulen}})
    agirlikli = [k for k in cozulen if k["agirlik"] > 0]
    print("agirlik>0: %d sahne; deger>0: %d; deger toplami %d; satir (gecmis haric) %d; gecmis isaretli %d; yon=geri %d; donmuslu %d; gecmisli %d"
          % (len(agirlikli), len([k for k in agirlikli if (k.get("kirilim") or {}).get("deger")]),
             sum((k.get("kirilim") or {}).get("deger", 0) for k in agirlikli),
             sum(k["dogrulayici"][0] - k["dogrulayici_gecmis_satir"] for k in agirlikli),
             sum(k["dogrulayici_gecmis_satir"] for k in agirlikli),
             len([k for k in agirlikli if k.get("yon") == "geri"]), len([k for k in agirlikli if k["donmus"]]),
             len([k for k in agirlikli if k["gecmis"]])))
    sifir = [k for k in cozulen if k["agirlik"] == 0]
    print("agirlik 0: %d sahne; satir %d" % (len(sifir), sum(k["dogrulayici"][0] for k in sifir)))
    farkli = [k for k in cozulen if k.get("farklar")]
    print("FARKLI sahne: %d" % len(farkli))
    for k in farkli:
        print("  sahne %d: %s | agirlik %s yon %s donmus %s cift_satir %s oturmayan %s | metrik %s dogrulayici %s benim %s deger %s beklenen %s"
              % (k["no"], k["farklar"], k.get("agirlik"), k.get("yon"), k["donmus"], k["donmus_cift_satir"], k["donmus_oturmayan"],
                 k["metrik"], k["dogrulayici"], k["benim"], (k.get("kirilim") or {}).get("deger"), k.get("i_beklenen")))


if __name__ == "__main__":
    main()
