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
  2. Her YAPILANDIRMA icin motor kosar (asagidaki tablo). Olculen: plan_degisikligi
     (korunan / degisen / kaldirilan / eklenen kisi-gun), FAZLADAN DOKUNULAN kisi-gun =
     (degisen + kaldirilan + eklenen) - zorunlu (k kisinin o gunu kaldirilir: k; yerine en
     az k eklenir -> 2k), sert, fm, eksik hedef (kisi-saat, dogrulayicidan), amac, sure,
     KAYMA ozeti (kim kac saat kaydi; K-73).
  3. Plan cikmazsa motorun cevabi ATILMAZ (17 Ekim; Mustafa: "cozumsuz diye bir sey yok,
     olmamali"): TESHIS (hangi hucre, gereken / mumkun, engelleyen kurallar, kanitli mi) ve
     TASLAK (K-10: asgari gevsetilmis en iyi plan -- sert, eksik kisi-saat, fazla mesai,
     kayma) kaydedilir. 16 Ekim gecesi 3 kisi raporlu orneklerinde yalniz "cozumsuz"
     kelimesi kaydedilmisti; teshis ve taslak copte kalmisti.

YAPILANDIRMALAR (`--yapilandirma A_urun,B_sifirdan,...`; varsayilan A_urun,B_sifirdan)
  A_urun            urun yolu: mevcut_plan = yayinlanmis plan, PLAN_KARARLILIGI aktif
  B_sifirdan        kiyas: mevcut_plan yok, ayni bozuk sahne (A - B farki K-70'in degeri)
  A_kayma           A + VARDIYA KAYMASI (K-73): raporlunun ekibinde o gun calisanlarin
                    vardiyalarinin erken baslayan / gec biten kopyalari; sinir yalniz yasal
  A_kayma_tavan1    A_kayma, kayma en fazla 1 saat  (OLCUM: tavanin degeri var mi?)
  A_kayma_tavan2    A_kayma, kayma en fazla 2 saat
  A_yumusak         A + ASGARI_KAPSAMA kaldirildi + HEDEF_KAPSAMA 3000/kisi-saat ("kapsama
                    once": 1 kisi-saat acik = 1 saat fazla mesai) -- kaymasiz kontrol
  A_kayma_yumusak   A_kayma + ayni gevsetme (3000): beden yoksa komsular uzar, kalan acik yazilir
  A_kayma_yumusak6  A_kayma + gevsetme, HEDEF_KAPSAMA 6000 (acik, fazla mesainin iki kati)
  Olcum yapilandirmalari URUN degil (K-62 ilkesi): her gevsetme burada acikca yazili.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py yeniden-planlama.py --sahne ..\\..\\06-veri\\anonim\\insan\\_sahne-INSAN-2026-06-22.json --hastalik 3 --ornek 5 --saniye 120
  py yeniden-planlama.py --sahne ... --hastalik 3 --ornek 5 --saniye 120 --yapilandirma A_urun,A_kayma,A_kayma_yumusak --etiket kayma
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
KAPSAMA_ONCE = 3000          # 1 kisi-saat hedef acigi = 1 saat fazla mesai (3.000 puan)

# ad -> (aciklama, degisiklik); degisiklik anahtarlari: mevcut_plan, kayma, kayma_tavan,
# asgari_kaldir, agirliklar
YAPILANDIRMALAR = {
    "A_urun":           ("urun yolu: mevcut_plan + PLAN_KARARLILIGI (K-70)", {"mevcut_plan": True}),
    "B_sifirdan":       ("kiyas: mevcut_plan yok, ayni bozuk sahne", {"mevcut_plan": False}),
    "A_kayma":          ("A + vardiya kaymasi (K-73), sinir yalniz yasal", {"mevcut_plan": True, "kayma": True}),
    "A_kayma_tavan1":   ("A + kayma en fazla 1 saat (olcum)", {"mevcut_plan": True, "kayma": True, "kayma_tavan": 1}),
    "A_kayma_tavan2":   ("A + kayma en fazla 2 saat (olcum)", {"mevcut_plan": True, "kayma": True, "kayma_tavan": 2}),
    "A_yumusak":        ("A + ASGARI_KAPSAMA kaldirildi + HEDEF_KAPSAMA %d/kisi-saat (kaymasiz kontrol)" % KAPSAMA_ONCE,
                         {"mevcut_plan": True, "asgari_kaldir": True, "agirliklar": {"HEDEF_KAPSAMA": KAPSAMA_ONCE}}),
    "A_kayma_yumusak":  ("A + kayma + ASGARI_KAPSAMA kaldirildi + HEDEF_KAPSAMA %d/kisi-saat" % KAPSAMA_ONCE,
                         {"mevcut_plan": True, "kayma": True, "asgari_kaldir": True, "agirliklar": {"HEDEF_KAPSAMA": KAPSAMA_ONCE}}),
    "A_kayma_yumusak6": ("A + kayma + ASGARI_KAPSAMA kaldirildi + HEDEF_KAPSAMA %d/kisi-saat" % (2 * KAPSAMA_ONCE),
                         {"mevcut_plan": True, "kayma": True, "asgari_kaldir": True, "agirliklar": {"HEDEF_KAPSAMA": 2 * KAPSAMA_ONCE}}),
}


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


def bozuk_sahne(g, plan, bozulma, mevcut_plan=True, kayma=False, kayma_tavan=None,
                asgari_kaldir=False, agirliklar=None):
    """Secilen (kisi, gun) ciftlerine onayli RAPOR izni; mevcut_plan = yayinlanmis plan
    (A) ya da yok (B). PLAN_KARARLILIGI kurali yoksa eklenir (YUMUSAK).
    kayma (K-73): raporlunun ekibinde o gun calisanlarin vardiya kopyalari (cozucu/kayma.py);
    kopyalar sahneye EKLENIR ki motor ve dogrulayici ayni girdiyi gorsun.
    asgari_kaldir: ASGARI_KAPSAMA kurali cikar (olcum; K-10 taslagin gevsetmesi).
    agirliklar: girdi `agirliklar` ustune yazilir (olcum)."""
    h = copy.deepcopy(g)
    kisi = {c["id"]: c for c in h["calisanlar"]}
    for kid, gun in bozulma:
        kisi[kid].setdefault("izinler", []).append({"gun": int(gun), "tip": "rapor", "durum": "onayli"})
    if not any(k["kod"] == "PLAN_KARARLILIGI" for k in h["kurallar"]):
        h["kurallar"].append({"kod": "PLAN_KARARLILIGI", "tur": "YUMUSAK", "aktif": True, "yasal": False})
    if asgari_kaldir:
        h["kurallar"] = [k for k in h["kurallar"] if k.get("kod") != "ASGARI_KAPSAMA"]
    if agirliklar:
        h["agirliklar"] = dict(h.get("agirliklar") or {}, **agirliklar)
    if mevcut_plan:
        h["mevcut_plan"] = copy.deepcopy(plan)
    else:
        h.pop("mevcut_plan", None)
    if kayma:
        from cozucu.kayma import etkilenen_bul, kayma_ekle
        etk = etkilenen_bul(h, plan, bozulma)
        h = kayma_ekle(h, etk, tavan_saat=kayma_tavan, mevcut_plan=plan)
    h.pop("_merdiven", None)
    return h


def eksik_kisi_saat(ihlaller):
    """Dogrulayicinin HEDEF_KAPSAMA satirlarindan toplam acik (kisi-saat) ve hucre sayisi."""
    toplam, hucre = 0, 0
    for i in ihlaller or []:
        if i.get("kural") != "HEDEF_KAPSAMA" or i.get("gecmis"):
            continue
        olculen, gereken = i.get("olculen"), i.get("gereken")
        if olculen is None or gereken is None or gereken <= olculen:
            continue
        toplam += gereken - olculen
        hucre += 1
    return toplam, hucre


def _plan_olcusu(h, plan, bozulma, atamalar):
    """Bir plan (motor plani ya da taslak) icin ortak olculer: degisiklik, sert, eksik, fm, kayma."""
    from cozucu.coz import plan_degisikligi
    from cozucu.kayma import kayma_ozeti
    from dogrulayici import degerlendir
    r = degerlendir(h, atamalar)
    ih = [i for i in r["ihlaller"] if not i.get("gecmis")]
    d = plan_degisikligi(dict(h, mevcut_plan=plan), atamalar)     # degisiklik her zaman YAYINLANMIS plana gore
    zorunlu = 2 * len(bozulma)
    eksik, eksik_hucre = eksik_kisi_saat(ih)
    oz = kayma_ozeti(atamalar)
    oz.pop("satirlar", None)
    return {"degisiklik": d,
            "dokunulan": d["degisen"] + d["kaldirilan"] + d["eklenen"],
            "fazladan_dokunulan": d["degisen"] + d["kaldirilan"] + d["eklenen"] - zorunlu,
            "sert_ihlal": sum(1 for i in ih if i.get("agirlik") == "SERT"),
            "ihlal": {k: sum(1 for i in ih if i["kural"] == k) for k in sorted({i["kural"] for i in ih})},
            "fazla_mesai_saat": round((r["metrikler"] or {}).get("fazla_mesai_saat") or 0.0, 2),
            "eksik_kisi_saat": eksik, "eksik_hucre": eksik_hucre,
            "raporlu_gunde_calisan": sum(1 for a in atamalar for kid, gun in bozulma
                                         if a["calisan"] == kid and int(a["gun"]) == int(gun)),
            "kayma": oz,
            "kayma_satirlari": [{"calisan": a["calisan"], "gun": a["gun"], "bas": a["bas"], "bit": a["bit"],
                                 "erken": a["kayma"]["erken"], "gec": a["kayma"]["gec"]}
                                for a in atamalar if a.get("kayma")]}


def _kosu(h, plan, bozulma, ayar):
    from cozucu.coz import coz
    t0 = time.time()
    c = coz(h, dict(ayar))
    sure = round(time.time() - t0, 1)
    s = {"durum": c.get("durum"), "sure_sn": sure, "kayma_sablon": (h.get("_kayma") or {}).get("sablon", 0)}
    if c.get("durum") != "cozuldu":
        # 17 Ekim: motorun cevabi atilmaz -- teshis + taslak (K-10 / K-37)
        t = c.get("teshis") or {}
        s["teshis"] = {"kesin": c.get("teshis_kesin"), "kapsam": t.get("kapsam"), "hucre": t.get("hucre"),
                       "gereken": t.get("gereken"), "mumkun": t.get("mumkun"),
                       "engelleyen": [{"kod": k.get("kod"), "yasal": k.get("yasal"), "gerekce": k.get("gerekce")}
                                      for k in (t.get("engelleyen_kurallar") or [])],
                       "belirsiz": [k.get("kod") for k in (t.get("belirsiz_kurallar") or [])],
                       "not": t.get("not")}
        e = c.get("en_iyi_plan") or {}
        if e.get("var") and e.get("atamalar"):
            s["taslak"] = dict(_plan_olcusu(h, plan, bozulma, e["atamalar"]),
                               gevsetilen=e.get("gevsetilen_kurallar"), atama=len(e["atamalar"]))
        else:
            s["taslak"] = {"var": False, "sebep": e.get("sebep")}
        return s
    ist = c.get("cozum_istatistikleri") or {}
    s.update(_plan_olcusu(h, plan, bozulma, c["atamalar"]))
    s.update({"amac": ist.get("amac_degeri"),
              "eksik_hedef_dakika": (c.get("metrikler") or {}).get("eksik_hedef_dakika"),
              "ilk_cozum_sn": ist.get("ilk_cozum_sn"),
              "kararlilik_cezasi": ((ist.get("amac_dagilimi") or {}).get("PLAN_KARARLILIGI") or {}).get("ceza"),
              "amac_dagilimi": {k: v.get("ceza") for k, v in (ist.get("amac_dagilimi") or {}).items()}})
    return s


def olc(g, plan, hastalik=3, ornek=3, saniye=120, tohum=16, kiyas=True, yapilandirmalar=None):
    adlar = list(yapilandirmalar) if yapilandirmalar else (["A_urun", "B_sifirdan"] if kiyas else ["A_urun"])
    for ad in adlar:
        if ad not in YAPILANDIRMALAR:
            raise SystemExit("bilinmeyen yapilandirma %s; secenekler: %s" % (ad, ", ".join(YAPILANDIRMALAR)))
    rnd = random.Random(tohum)
    for i in range(ornek):
        bozulma = bozulma_sec(plan, hastalik, rnd)
        ayar = dict(AYAR, azami_saniye=saniye)
        o = {"ornek": i + 1, "bozulma": [{"kisi": k, "gun": gn} for k, gn in bozulma]}
        for ad in adlar:
            o[ad] = _kosu(bozuk_sahne(g, plan, bozulma, **YAPILANDIRMALAR[ad][1]), plan, bozulma, ayar)
        yield o


def _ort(v, anahtar):
    return sum(x.get(anahtar) or 0 for x in v) / float(len(v))


def ozet(ornekler, adlar=None):
    adlar = adlar or [a for a in YAPILANDIRMALAR if any(a in o for o in ornekler)]
    satirlar = []
    for ad in adlar:
        hepsi = [o[ad] for o in ornekler if o.get(ad)]
        v = [x for x in hepsi if x.get("durum") == "cozuldu"]
        if not v:
            satirlar.append("  %-17s plan 0/%d" % (ad, len(hepsi)))
        else:
            kay = [x["kayma"]["toplam_saat"] for x in v]
            satirlar.append("  %-17s plan %d/%d | dokunulan kisi-gun ort %.1f (fazladan %.1f) | sert %d | fm ort %.2f sa | acik ort %.1f kisi-saat | kayma ort %.1f sa (%d planda) | raporlu gunde calisan %d | sure ort %.0f sn"
                            % (ad, len(v), len(hepsi), _ort(v, "dokunulan"), _ort(v, "fazladan_dokunulan"),
                               sum(x["sert_ihlal"] for x in v), _ort(v, "fazla_mesai_saat"), _ort(v, "eksik_kisi_saat"),
                               sum(kay) / float(len(v)), sum(1 for k in kay if k), sum(x["raporlu_gunde_calisan"] for x in v),
                               _ort(v, "sure_sn")))
        taslaklar = [x["taslak"] for x in hepsi if x.get("durum") != "cozuldu" and (x.get("taslak") or {}).get("dokunulan") is not None]
        if taslaklar:
            satirlar.append("  %-17s   cozumsuz %d: taslak (asgari gevsek) acik ort %.1f kisi-saat | sert %d | fm ort %.2f sa | kayma ort %.1f sa"
                            % ("", len([x for x in hepsi if x.get("durum") != "cozuldu"]), _ort(taslaklar, "eksik_kisi_saat"),
                               sum(t["sert_ihlal"] for t in taslaklar), _ort(taslaklar, "fazla_mesai_saat"),
                               sum(t["kayma"]["toplam_saat"] for t in taslaklar) / float(len(taslaklar))))
    return "\n".join(satirlar)


def _satir(o, ad, s):
    if s["durum"] != "cozuldu":
        t = s.get("teshis") or {}
        h = t.get("hucre") or {}
        tas = s.get("taslak") or {}
        tas_m = ("taslak acik %s kisi-saat, sert %s, fm %s, kayma %s sa" % (tas.get("eksik_kisi_saat"), tas.get("sert_ihlal"),
                 tas.get("fazla_mesai_saat"), (tas.get("kayma") or {}).get("toplam_saat"))
                 if tas.get("dokunulan") is not None else "taslak yok (%s)" % tas.get("sebep"))
        return ("  ornek %d %-17s %s (%s sn) | teshis%s: %s gun %s saat %s gereken %s mumkun %s, engelleyen %s | %s"
                % (o["ornek"], ad, s["durum"], s["sure_sn"], "" if t.get("kesin") else " (TAHMIN)",
                   h.get("ekip"), h.get("gun"), h.get("saat"), t.get("gereken"), t.get("mumkun"),
                   ",".join(k["kod"] for k in (t.get("engelleyen") or [])) or "-", tas_m))
    d = s["degisiklik"]
    k = s["kayma"]
    kayma_m = ("kayma %d kisi %d sa %s" % (k["kisi_sayisi"], k["toplam_saat"], k["dagilim"])) if k["toplam_saat"] else "kayma yok"
    return ("  ornek %d %-17s dokunulan %3d (degisen %d, kaldirilan %d, eklenen %d; fazladan %d) | sert %d | fm %.2f | acik %s kisi-saat | %s | amac %s | kararlilik %s | %s sn"
            % (o["ornek"], ad, s["dokunulan"], d["degisen"], d["kaldirilan"], d["eklenen"], s["fazladan_dokunulan"],
               s["sert_ihlal"], s["fazla_mesai_saat"], s["eksik_kisi_saat"], kayma_m, s["amac"], s["kararlilik_cezasi"], s["sure_sn"]))


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
    adlar = [a.strip() for a in _arg("--yapilandirma", "A_urun,B_sifirdan").split(",") if a.strip()]
    print("YENIDEN PLANLAMA: %s | yayinlanmis plan %d atama | bozulma: %d kisi raporlu (birer gun) | %d ornek | %d sn | %s"
          % (sahne_adi(sahne), len(plan), hastalik, ornek, saniye, ", ".join(adlar)))
    for ad in adlar:
        print("  [%s] %s" % (ad, YAPILANDIRMALAR.get(ad, ("?",))[0]))
    sonuc = {"sahne": sahne_adi(sahne), "referans": os.path.basename(ref_yol), "hastalik": hastalik, "ornek": ornek,
             "saniye": saniye, "tohum": tohum, "yapilandirmalar": adlar, "tarih": time.strftime("%Y-%m-%d %H:%M"),
             "cekirdek": os.cpu_count(), "ornekler": []}
    for o in olc(g, plan, hastalik, ornek, saniye, tohum, yapilandirmalar=adlar):
        sonuc["ornekler"].append(o)
        for ad in adlar:
            print(_satir(o, ad, o[ad]))
        sys.stdout.flush()
    print("OZET")
    print(ozet(sonuc["ornekler"], adlar))
    yol = os.path.join(BURASI, "yeniden-planlama-%s%s.json" % (sahne_adi(sahne), ("-" + etiket) if etiket else ""))
    with io.open(yol, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("Sonuc yazildi: %s" % os.path.basename(yol))
