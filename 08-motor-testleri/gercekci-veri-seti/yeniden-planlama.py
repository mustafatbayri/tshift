# -*- coding: utf-8 -*-
"""
YENIDEN PLANLAMA OLCUMU -- "edit" sahnesi: yayinlanmis plan + bozulma -> motor K-70 ile yeniden planlar
(16 Ekim; Mustafa: "benim icin 3 konu var: 1 motor 2 edit 3 suggest")

NEDEN
  Urunun ikinci cekirdegi EDIT: plan yayinlandi, Carsamba uc kisi raporlu -- motor en az
  degisiklikle yeniden planlasin (K-70 PLAN_KARARLILIGI, kisi-gun). Bugune kadar bu yol
  yalniz birim testlerde (test_plan_kararliligi, 3 kisi) olculdu. Burada GERCEK sahnede
  olculur: insan plani sahnesi (A3) ya da tanikli sahne, yayinlanmis plan = referans
  (insan plani / tanik).

NE YAPAR (her ornek icin)
  1. Bozulma: `--hastalik k` -> k rastgele kisi, planda calistigi rastgele bir gunde
     onayli RAPOR izni alir (ONAYLI_IZIN sert: o gun calisamaz). Tohum sabit; ornekler
     farkli kisiler.
  2. A -- URUN YOLU: `mevcut_plan` = yayinlanmis plan, PLAN_KARARLILIGI aktif -> motor.
     Olculen: plan_degisikligi (korunan / degisen / kaldirilan / eklenen kisi-gun),
     FAZLADAN DOKUNULAN kisi-gun = (degisen + kaldirilan + eklenen) - zorunlu (k kisinin
     o gunu kaldirilir: k; yerine en az k eklenir -> 2k), sert, fm, eksik hedef, amac, sure.
  3. B -- KIYAS (sifirdan): mevcut_plan verilmez, ayni bozuk sahne -> plan; ayni olculer
     (degisiklik yayinlanmis plana gore). A ile B arasindaki fark K-70'in degeri.
  Yayinlanmis plan bozuk sahnede gecersizdir (raporlu kisi calisiyor) -- motorun ipucu
  olarak alip onarmasi beklenen davranis.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py yeniden-planlama.py --sahne ..\\..\\06-veri\\anonim\\insan\\_sahne-INSAN-2026-06-22.json --hastalik 3 --ornek 5 --saniye 120
  (referans: sahnenin yanindaki _referans-… dosyasi; --referans ile baska yol)
  Cikti: yeniden-planlama-<sahne adi>[-etiket].json (+ ekran tablosu)
"""

import copy
import io
import json
import os
import random
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

AYAR = {"azami_saniye": 120, "durgunluk_saniye": 30}


def referans_dosyasi(sahne_yolu):
    klasor, ad = os.path.split(sahne_yolu)
    if not ad.startswith("_sahne-"):
        return None
    yol = os.path.join(klasor, "_referans-" + ad[len("_sahne-"):])
    return yol if os.path.exists(yol) else None


def sahne_adi(yol):
    ad = os.path.splitext(yol.replace("\\", "/").rsplit("/", 1)[-1])[0]
    return ad[len("_sahne-"):] if ad.startswith("_sahne-") else ad


def bozulma_sec(plan, k, rnd):
    """k farkli kisi, her biri planda calistigi bir gun -> [(kisi, gun)]."""
    gunler = {}
    for a in plan:
        gunler.setdefault(a["calisan"], set()).add(int(a["gun"]))
    kisiler = sorted(gunler)
    if k > len(kisiler):
        raise SystemExit("hastalik %d > planda calisan kisi %d" % (k, len(kisiler)))
    secilen = rnd.sample(kisiler, k)
    return [(kisi, rnd.choice(sorted(gunler[kisi]))) for kisi in secilen]


def bozuk_sahne(g, plan, bozulma, mevcut_plan=True):
    """Secilen (kisi, gun) ciftlerine onayli RAPOR izni; mevcut_plan = yayinlanmis plan
    (A) ya da yok (B). PLAN_KARARLILIGI kuralı yoksa eklenir (YUMUSAK)."""
    h = copy.deepcopy(g)
    kisi = {c["id"]: c for c in h["calisanlar"]}
    for kid, gun in bozulma:
        kisi[kid].setdefault("izinler", []).append({"gun": int(gun), "tip": "rapor", "durum": "onayli"})
    if not any(k["kod"] == "PLAN_KARARLILIGI" for k in h["kurallar"]):
        h["kurallar"].append({"kod": "PLAN_KARARLILIGI", "tur": "YUMUSAK", "aktif": True, "yasal": False})
    if mevcut_plan:
        h["mevcut_plan"] = copy.deepcopy(plan)
    else:
        h.pop("mevcut_plan", None)
    h.pop("_merdiven", None)
    return h


def _kosu(h, plan, bozulma, ayar):
    from cozucu.coz import coz, plan_degisikligi
    from dogrulayici import degerlendir
    t0 = time.time()
    c = coz(h, dict(ayar))
    sure = round(time.time() - t0, 1)
    s = {"durum": c.get("durum"), "sure_sn": sure}
    if c.get("durum") != "cozuldu":
        return s
    ist = c.get("cozum_istatistikleri") or {}
    r = degerlendir(h, c["atamalar"])
    ih = [i for i in r["ihlaller"] if not i.get("gecmis")]
    kiyas = dict(h, mevcut_plan=plan)                       # degisiklik her zaman YAYINLANMIS plana gore
    d = plan_degisikligi(kiyas, c["atamalar"])
    zorunlu = 2 * len(bozulma)
    raporlu_calisti = sum(1 for a in c["atamalar"] for kid, gun in bozulma if a["calisan"] == kid and int(a["gun"]) == int(gun))
    s.update({"amac": ist.get("amac_degeri"), "degisiklik": d,
              "dokunulan": d["degisen"] + d["kaldirilan"] + d["eklenen"],
              "fazladan_dokunulan": d["degisen"] + d["kaldirilan"] + d["eklenen"] - zorunlu,
              "sert_ihlal": sum(1 for i in ih if i.get("agirlik") == "SERT"),
              "ihlal": {k: sum(1 for i in ih if i["kural"] == k) for k in sorted({i["kural"] for i in ih})},
              "fazla_mesai_saat": round((r["metrikler"] or {}).get("fazla_mesai_saat") or 0.0, 2),
              "eksik_hedef_dakika": (c.get("metrikler") or {}).get("eksik_hedef_dakika"),
              "raporlu_gunde_calisan": raporlu_calisti,
              "ilk_cozum_sn": ist.get("ilk_cozum_sn"), "kararlilik_cezasi": ((ist.get("amac_dagilimi") or {}).get("PLAN_KARARLILIGI") or {}).get("ceza")})
    return s


def olc(g, plan, hastalik=3, ornek=3, saniye=120, tohum=16, kiyas=True):
    rnd = random.Random(tohum)
    ornekler = []
    for i in range(ornek):
        bozulma = bozulma_sec(plan, hastalik, rnd)
        ayar = dict(AYAR, azami_saniye=saniye)
        o = {"ornek": i + 1, "bozulma": [{"kisi": k, "gun": gn} for k, gn in bozulma],
             "A_urun": _kosu(bozuk_sahne(g, plan, bozulma, True), plan, bozulma, ayar)}
        if kiyas:
            o["B_sifirdan"] = _kosu(bozuk_sahne(g, plan, bozulma, False), plan, bozulma, ayar)
        ornekler.append(o)
        yield o


def ozet(ornekler):
    def sat(ad, anahtar):
        v = [o[anahtar] for o in ornekler if o.get(anahtar, {}).get("durum") == "cozuldu"]
        if not v:
            return "  %-12s plan yok" % ad
        return ("  %-12s plan %d/%d | dokunulan kisi-gun ort %.1f (fazladan %.1f) | sert %s | fm %.2f sa | raporlu gunde calisan %d | sure ort %.0f sn"
                % (ad, len(v), len(ornekler), sum(x["dokunulan"] for x in v) / len(v), sum(x["fazladan_dokunulan"] for x in v) / len(v),
                   sum(x["sert_ihlal"] for x in v), sum(x["fazla_mesai_saat"] for x in v) / len(v),
                   sum(x["raporlu_gunde_calisan"] for x in v), sum(x["sure_sn"] for x in v) / len(v)))
    return "\n".join([sat("A urun (K-70)", "A_urun"), sat("B sifirdan", "B_sifirdan")])


def _arg(ad, varsayilan, tur=str):
    return tur(sys.argv[sys.argv.index(ad) + 1]) if ad in sys.argv else varsayilan


if __name__ == "__main__":
    sahne = _arg("--sahne", None)
    if not sahne:
        raise SystemExit("--sahne <dosya> gerekli")
    ref_yol = _arg("--referans", referans_dosyasi(sahne))
    if not ref_yol:
        raise SystemExit("referans (yayinlanmis plan) bulunamadi: sahnenin yaninda _referans-… yok; --referans ver")
    g = json.load(io.open(sahne, encoding="utf-8"))
    plan = json.load(io.open(ref_yol, encoding="utf-8"))["atamalar"]
    hastalik, ornek, saniye, tohum = _arg("--hastalik", 3, int), _arg("--ornek", 3, int), _arg("--saniye", 120, int), _arg("--tohum", 16, int)
    etiket = _arg("--etiket", "")
    print("YENIDEN PLANLAMA: %s | yayinlanmis plan %d atama | bozulma: %d kisi raporlu (birer gun) | %d ornek | %d sn (A urun + B sifirdan)"
          % (sahne_adi(sahne), len(plan), hastalik, ornek, saniye))
    sonuc = {"sahne": sahne_adi(sahne), "referans": os.path.basename(ref_yol), "hastalik": hastalik, "ornek": ornek,
             "saniye": saniye, "tohum": tohum, "tarih": time.strftime("%Y-%m-%d %H:%M"), "cekirdek": os.cpu_count(), "ornekler": []}
    for o in olc(g, plan, hastalik, ornek, saniye, tohum):
        sonuc["ornekler"].append(o)
        for ad in ("A_urun", "B_sifirdan"):
            s = o.get(ad)
            if not s:
                continue
            if s["durum"] != "cozuldu":
                print("  ornek %d %-10s %s (%s sn)" % (o["ornek"], ad, s["durum"], s["sure_sn"]))
                continue
            d = s["degisiklik"]
            print("  ornek %d %-10s dokunulan %3d (degisen %d, kaldirilan %d, eklenen %d; fazladan %d) | sert %d | fm %.2f | eksik %s dk | amac %s | kararlilik cezasi %s | %s sn"
                  % (o["ornek"], ad, s["dokunulan"], d["degisen"], d["kaldirilan"], d["eklenen"], s["fazladan_dokunulan"],
                     s["sert_ihlal"], s["fazla_mesai_saat"], s["eksik_hedef_dakika"], s["amac"], s["kararlilik_cezasi"], s["sure_sn"]))
    print("OZET")
    print(ozet(sonuc["ornekler"]))
    yol = os.path.join(BURASI, "yeniden-planlama-%s%s.json" % (sahne_adi(sahne), ("-" + etiket) if etiket else ""))
    with io.open(yol, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("Sonuc yazildi: %s" % os.path.basename(yol))
