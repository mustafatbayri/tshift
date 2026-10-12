# -*- coding: utf-8 -*-
"""B. Rastgele sahne avi: N kucuk sahne (2-4 kisi, 2-7 gun, 3-5 sablon; ceyrek saat
baslangiclar, gece yarisini asanlar, bas 0 ve bas >= 24; gecmis gun -1/-2; donmus gun +
mevcut_plan; yon=geri; agirlik 0; kural yok / aktif:false).

Her sahnede:
 (i)   agirlik > 0: amac kirilimi `deger` == dogrulayici satirlarinin (gecmis olmayan)
       yuvarlanmis toplami  (ve inceleme sayimi ile)
 (ii)  metrikler.rotasyon_geri_gecis/_saat == dogrulayici satir sayisi / kesin toplam (gecmis dahil)
 (iii) kural kapali/yok: metrik None, satir yok, kirilim anahtari yok
 (iv)  agirlik 0: (ii) yine tutuyor mu
Kullanim: python3 d2_rastgele.py [adet=320] [tohum=11] [asgari_olasilik=0.4] [cikti.json]
"""
import copy
import json
import random
import sys
import time

from ortak import (coz, degerlendir, AYAR, KURAL, kural, rot_satirlari, rot_kirilim,
                   yuvarla, benim_say, AGIRLIK_TABLOSU)

ADET = int(sys.argv[1]) if len(sys.argv) > 1 else 320
TOHUM = int(sys.argv[2]) if len(sys.argv) > 2 else 11
ASGARI_OLASILIK = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
CIKTI = sys.argv[4] if len(sys.argv) > 4 else __file__.replace(".py", ".json")
SURELER = [4.5, 5, 6, 7, 7.5]


def sablon_uret(rnd, i):
    r = rnd.random()
    if r < 0.08:
        bas = 0.0
    elif r < 0.18:
        bas = 24 + rnd.randrange(0, 8) * 0.25          # 24.00 .. 25.75 (genisletilmis baslangic)
    else:
        bas = rnd.randrange(0, 96) * 0.25
    sure = rnd.choice(SURELER)
    return {"id": "S%d" % i, "ekip": "E", "bas": bas, "bit": bas + sure,
            "mola_dk": rnd.choice([0, 0, 30])}


def dilimler(gun, bas, bit):
    return range(int(round((gun * 24 + bas) * 4)), int(round((gun * 24 + bit) * 4)))


def hedef_plan_uret(rnd, kisiler, gunler, sablonlar):
    plan = []
    for p in kisiler:
        k = rnd.randint(0, min(len(gunler), 6))
        secilen = sorted(rnd.sample(gunler, k))
        if len(secilen) == 7:
            secilen = secilen[:-1]
        toplam = 0.0
        for d in secilen:
            t = rnd.choice(sablonlar)
            if toplam + (t["bit"] - t["bas"]) > 45:
                continue
            toplam += t["bit"] - t["bas"]
            plan.append({"calisan": p, "ekip": "E", "sablon": t["id"], "gun": d,
                         "bas": t["bas"], "bit": t["bit"], "molalar": []})
    return plan


def talep_uret(plan, asgari_ac):
    sayim = {}
    for a in plan:
        for q in dilimler(a["gun"], a["bas"], a["bit"]):
            sayim[q] = sayim.get(q, 0) + 1
    hucre = {}
    for q, n in sayim.items():
        g, saat = q // 96, (q % 96) // 4
        if g >= 7:
            continue
        hucre[(g, saat)] = min(hucre.get((g, saat), n), n)      # saatin dort ceyreginin en azi
    # ceyregi eksik olan saat: en az 0 -> dort ceyrek de sayilmali
    for (g, saat) in list(hucre):
        if any(q not in sayim for q in range(g * 96 + saat * 4, g * 96 + saat * 4 + 4)):
            hucre[(g, saat)] = 0
    return [{"ekip": "E", "gun": g, "saat": s, "asgari": (h if asgari_ac else 0), "hedef": h}
            for (g, s), h in sorted(hucre.items()) if h > 0]


def sahne_uret(rnd):
    n_kisi, n_gun, n_sablon = rnd.randint(2, 4), rnd.randint(2, 7), rnd.randint(3, 5)
    kisiler = ["P%d" % i for i in range(1, n_kisi + 1)]
    gunler = list(range(n_gun))
    sablonlar = [sablon_uret(rnd, i) for i in range(n_sablon)]
    calisanlar = [{"id": p, "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}
                  for p in kisiler]
    bilgi = {"kisi": n_kisi, "gun": n_gun, "sablon": n_sablon, "gecmis": 0, "gecmis_cift": 0}
    for c in calisanlar:
        if rnd.random() < 0.35:
            kayit = []
            for gun in ([-1], [-2], [-1, -2])[rnd.randrange(3)]:
                b = rnd.randrange(0, 96) * 0.25
                kayit.append({"gun": gun, "bas": b, "bit": b + rnd.choice(SURELER)})
            if -1 in [k["gun"] for k in kayit] and rnd.random() < 0.15:
                b = rnd.randrange(0, 96) * 0.25
                kayit.append({"gun": -1, "bas": b, "bit": b + 4})
                bilgi["gecmis_cift"] += 1
            c["gecmis_vardiyalar"] = kayit
            bilgi["gecmis"] += 1
    dinlenme = rnd.choice([0, 4, 8, 11])
    kurallar = [kural("ASGARI_KAPSAMA"), kural("HEDEF_KAPSAMA", tur="YUMUSAK"), kural("HEDEF_ASIMI", tur="YUMUSAK"),
                kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=dinlenme)]
    r = rnd.random()
    g = {"profil": rnd.choice(["DENGELI", "DENGELI", "KAPSAMA", "CALISAN"]), "calisanlar": calisanlar,
         "vardiya_sablonlari": sablonlar, "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}
    if r < 0.15:
        bilgi["kural"] = "yok"
    elif r < 0.30:
        k = kural(KURAL, tur="YUMUSAK"); k["aktif"] = False; kurallar.append(k)
        bilgi["kural"] = "aktif_false"
    else:
        par = {}
        if rnd.random() < 0.2:
            par["yon"] = "geri"
        kurallar.append(kural(KURAL, tur="YUMUSAK", **par))
        bilgi["kural"] = "acik"
        bilgi["yon"] = par.get("yon", "ileri")
        r2 = rnd.random()
        if r2 < 0.2:
            g["agirliklar"] = {KURAL: 0}
        elif r2 < 0.4:
            g["agirliklar"] = {KURAL: rnd.randint(1, 10)}
    bilgi["agirlik"] = (g.get("agirliklar") or {}).get(KURAL, AGIRLIK_TABLOSU[KURAL][g["profil"]]) if bilgi["kural"] == "acik" else None
    bilgi["dinlenme"] = dinlenme
    plan = hedef_plan_uret(rnd, kisiler, gunler, sablonlar)
    bilgi["hedef_plan_atama"] = len(plan)
    # donmus gun + mevcut plan (hedef plandan)
    bilgi["donmus"] = []
    bilgi["donmus_cift_satir"] = False
    bilgi["donmus_oturmayan"] = False
    if rnd.random() < 0.25 and n_gun >= 2:
        if rnd.random() < 0.8:
            donmus = list(range(rnd.randint(1, min(3, n_gun - 1))))
        else:
            donmus = [rnd.randrange(1, n_gun)]
        mevcut = [copy.deepcopy(a) for a in plan if a["gun"] in donmus]
        if mevcut and rnd.random() < 0.15:
            a = rnd.choice(mevcut)
            digerleri = [t for t in sablonlar if t["id"] != a["sablon"]
                         and not (t["bas"] < a["bit"] and a["bas"] < t["bit"])]
            if digerleri:
                t = rnd.choice(digerleri)
                mevcut.append({"calisan": a["calisan"], "ekip": "E", "sablon": t["id"], "gun": a["gun"],
                               "bas": t["bas"], "bit": t["bit"], "molalar": []})
                bilgi["donmus_cift_satir"] = True
        if rnd.random() < 0.1:
            p = rnd.choice(kisiler)
            d = rnd.choice(donmus)
            if not any(a["calisan"] == p and a["gun"] == d for a in mevcut):
                mevcut.append({"calisan": p, "ekip": "E", "sablon": None, "gun": d, "bas": 10.5, "bit": 14.5, "molalar": []})
                bilgi["donmus_oturmayan"] = True
        g["donmus_gunler"] = donmus
        g["mevcut_plan"] = mevcut
        bilgi["donmus"] = donmus
        bilgi["mevcut_satir"] = len(mevcut)
    asgari_ac = rnd.random() < ASGARI_OLASILIK
    if asgari_ac:
        # hedef plan sert kurallari tutuyor mu? tutmuyorsa asgari 0
        rapor = degerlendir(g, plan)
        if any(i["agirlik"] == "SERT" for i in rapor["ihlaller"]):
            asgari_ac = False
    g["talep"] = talep_uret(plan, asgari_ac)
    bilgi["asgari_ac"] = asgari_ac
    bilgi["talep_hucre"] = len(g["talep"])
    bilgi["sablon_bas0"] = sum(1 for t in sablonlar if t["bas"] == 0)
    bilgi["sablon_bas24"] = sum(1 for t in sablonlar if t["bas"] >= 24)
    bilgi["sablon_gece_asan"] = sum(1 for t in sablonlar if t["bas"] < 24 < t["bit"])
    return g, bilgi


def incele(g, bilgi):
    t0 = time.time()
    c = coz(copy.deepcopy(g), AYAR)
    bilgi["sure"] = round(time.time() - t0, 2)
    bilgi["durum"] = c["durum"]
    if c["durum"] != "cozuldu":
        bilgi["sebep"] = (c.get("cozum_istatistikleri") or {}).get("durma_sebebi")
        return bilgi
    ist = c["cozum_istatistikleri"]
    bilgi["durma_sebebi"] = ist.get("durma_sebebi")
    bilgi["atama"] = len(c["atamalar"])
    r = degerlendir(g, c["atamalar"])
    satirlar = rot_satirlari(r)
    benim = benim_say(g, c["atamalar"])
    m = c["metrikler"]
    kir = rot_kirilim(c)
    bilgi["metrik"] = [m.get("rotasyon_geri_gecis"), m.get("rotasyon_geri_saat")]
    bilgi["dogrulayici"] = [len(satirlar), round(sum(i["olculen"] for i in satirlar), 2)]
    bilgi["dogrulayici_gecmis_satir"] = len([i for i in satirlar if i.get("gecmis")])
    bilgi["benim"] = [len(benim), round(sum(s[2] for s in benim), 2)] if benim is not None else None
    bilgi["kirilim"] = kir
    bilgi["sert_ihlal"] = r["metrikler"].get("sert_ihlal")
    farklar = []
    if bilgi["kural"] == "acik":
        # (ii) metrik == dogrulayici (gecmis dahil)
        if bilgi["metrik"] != bilgi["dogrulayici"]:
            farklar.append("ii_metrik!=dogrulayici")
        if bilgi["benim"] != bilgi["dogrulayici"]:
            farklar.append("ii_benim!=dogrulayici")
        # satir-satir: dogrulayici satirlari ile inceleme sayimi ayni mi
        ds = sorted((i["calisan"], i["gun"], i["olculen"]) for i in satirlar)
        bs = sorted((s[0], s[1], s[2]) for s in benim)
        if ds != bs:
            farklar.append("ii_satirlar_farkli")
        # K-54 isareti: iki gunu de donmus satirlar gecmis mi, digerleri degil mi
        d_gecmis = sorted((i["calisan"], i["gun"]) for i in satirlar if i.get("gecmis"))
        b_gecmis = sorted((s[0], s[1]) for s in benim if s[3])
        if d_gecmis != b_gecmis:
            farklar.append("k54_isaret_farkli")
        if bilgi["agirlik"] > 0:
            # (i) deger == gecmis olmayan satirlarin yuvarlanmis toplami
            beklenen = sum(yuvarla(i["olculen"]) for i in satirlar if not i.get("gecmis"))
            deger = (kir or {}).get("deger", 0)
            bilgi["i_beklenen"] = beklenen
            if deger != beklenen:
                farklar.append("i_deger!=yuvarlanmis_toplam")
            if kir is not None and kir["ceza"] != bilgi["agirlik"] * kir["deger"]:
                farklar.append("i_ceza!=agirlik*deger")
        else:
            bilgi["iv_deger_serbest"] = (kir or {}).get("deger")
    else:
        if bilgi["metrik"] != [None, None]:
            farklar.append("iii_metrik_None_degil")
        if satirlar:
            farklar.append("iii_satir_var")
        if kir is not None:
            farklar.append("iii_kirilim_var")
        if benim is not None:
            farklar.append("iii_benim_hata")
    bilgi["farklar"] = farklar
    return bilgi


def main():
    rnd = random.Random(TOHUM)
    kayit = []
    t0 = time.time()
    for i in range(ADET):
        g, bilgi = sahne_uret(rnd)
        bilgi["no"] = i
        try:
            incele(g, bilgi)
        except Exception as e:                      # noqa
            bilgi["durum"] = "HATA"
            bilgi["hata"] = repr(e)
        # girdi yalniz farkli/cozumsuz/hatali sahnelerde saklanir; digerleri tohum + sira no ile yeniden uretilir
        bilgi["girdi"] = g if (bilgi.get("farklar") or bilgi["durum"] != "cozuldu") else None
        kayit.append(bilgi)
        if bilgi.get("farklar") or bilgi["durum"] in ("HATA",):
            print("sahne %d: %s %s" % (i, bilgi["durum"], bilgi.get("farklar") or bilgi.get("hata")))
        if i % 25 == 24:
            print("... %d sahne, %.0f sn" % (i + 1, time.time() - t0))
    json.dump(kayit, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=0, default=str)
    # ozet
    cozulen = [k for k in kayit if k["durum"] == "cozuldu"]
    print("\nTOPLAM %d sahne, cozuldu %d, cozumsuz %d, hata %d, sure %.0f sn"
          % (len(kayit), len(cozulen), len([k for k in kayit if k["durum"] not in ("cozuldu", "HATA")]),
             len([k for k in kayit if k["durum"] == "HATA"]), time.time() - t0))
    print("durma sebepleri:", {s: len([k for k in cozulen if k.get("durma_sebebi") == s]) for s in {k.get("durma_sebebi") for k in cozulen}})
    print("kural dagilimi:", {s: len([k for k in cozulen if k["kural"] == s]) for s in ("acik", "yok", "aktif_false")})
    acik = [k for k in cozulen if k["kural"] == "acik"]
    print("acik: agirlik 0: %d, yon=geri: %d, gecmisli: %d, donmuslu: %d (cift satir %d, oturmayan %d), asgari acik: %d"
          % (len([k for k in acik if k["agirlik"] == 0]), len([k for k in acik if k.get("yon") == "geri"]),
             len([k for k in acik if k["gecmis"]]), len([k for k in acik if k["donmus"]]),
             len([k for k in acik if k["donmus_cift_satir"]]), len([k for k in acik if k["donmus_oturmayan"]]),
             len([k for k in acik if k["asgari_ac"]])))
    print("acik sahnelerde dogrulayici geri satiri olan: %d, toplam satir %d, gecmis isaretli %d"
          % (len([k for k in acik if k["dogrulayici"][0]]), sum(k["dogrulayici"][0] for k in acik),
             sum(k["dogrulayici_gecmis_satir"] for k in acik)))
    print("sablon ozellikleri (tum sahneler): bas 0: %d, bas>=24: %d, gece yarisini asan: %d"
          % (sum(k["sablon_bas0"] for k in kayit), sum(k["sablon_bas24"] for k in kayit), sum(k["sablon_gece_asan"] for k in kayit)))
    agirlikli = [k for k in acik if k["agirlik"] > 0]
    print("agirlik>0 sahne: %d; deger>0 olan: %d; deger toplami %d; satir toplami (gecmis haric) %d"
          % (len(agirlikli), len([k for k in agirlikli if (k.get("kirilim") or {}).get("deger")]),
             sum((k.get("kirilim") or {}).get("deger", 0) for k in agirlikli),
             sum(k["dogrulayici"][0] - k["dogrulayici_gecmis_satir"] for k in agirlikli)))
    print("agirlik 0 sahnelerde satir: %d, deger (serbest) toplami: %s"
          % (sum(k["dogrulayici"][0] for k in acik if k["agirlik"] == 0),
             sum((k.get("iv_deger_serbest") or 0) for k in acik if k["agirlik"] == 0)))
    farkli = [k for k in cozulen if k.get("farklar")]
    print("FARKLI sahne: %d" % len(farkli))
    sayac = {}
    for k in farkli:
        for f in k["farklar"]:
            sayac[f] = sayac.get(f, 0) + 1
    print("fark turleri:", sayac)
    for k in farkli:
        print("  sahne %d: %s | kural %s agirlik %s yon %s donmus %s cift_satir %s oturmayan %s gecmis %d | metrik %s dogrulayici %s benim %s deger %s beklenen %s durma %s"
              % (k["no"], k["farklar"], k["kural"], k.get("agirlik"), k.get("yon"), k["donmus"], k["donmus_cift_satir"],
                 k["donmus_oturmayan"], k["gecmis"], k["metrik"], k["dogrulayici"], k["benim"],
                 (k.get("kirilim") or {}).get("deger"), k.get("i_beklenen"), k.get("durma_sebebi")))


if __name__ == "__main__":
    main()
