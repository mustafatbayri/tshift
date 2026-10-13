# -*- coding: utf-8 -*-
"""
VERI SETI MERDIVENI -- SEVIYE 1: TAM OTURAN TALEP  (K-62, K-67)

NEDEN VAR
  K-62 (Mustafa, 6 Ekim): plan kalitesi CEVABI BILINEN veri setleriyle
  olculur. Seviye 1'de "hedef, gecerli ve fazla mesaisiz bir planin
  kendisidir" -- sette sifir asimli, sifir eksikli bir plan oldugu KURGU
  GEREGI kesindir; motorun plani bu referansla kalem kalem kiyaslanir.

  K-67 (Mustafa, 12 Ekim): "Hicbir isletme talebin ustunde eleman
  calistirmaz." HEDEF_ASIMI SERT oldu. Eski S30 setlerinde talep egrisi
  sablonlara oturmuyor (SATIS 14-16: hedef 122, atanan 186) ve SERT kuralla
  cozumsuz (bulgu 29). Seviye 1 bu yuzden one cekildi ve yeni olcumlerin
  TABANI oldu. S30 setleri AYNEN kalir (HEDEF_ASIMI YUMUSAK; tarihsel).

UC ADIM
  1. TABAN  = bugunku 500 kisilik %95 sahnesi (uret_veri_seti.sahne_uret)
             + K-62 kadro kararlari:
               * 10 satisci ayni zamanda BACKOFFICE uyesi (Mustafa, 12 Ekim
                 22:03: "20 satisci fazla bence bunu 10 yapalim"; K-50 ile
                 iki ekibe de sayilir),
               * BACKOFFICE gece 00:00-08:00: asgari 2, hedef 3 (Mustafa,
                 6 Ekim "en az 2 olsun"; 12 Ekim 21:58 "Backoffice 3 ok").
             Kisiler, sablonlar, kurallar baska hicbir yerde degismez.
             HEDEF_ASIMI tabanda YUMUSAK (referans bu sette bulunur).
  2. REFERANS = motorun bu tabanda, VARSAYILAN ARAMADAN BASKA BIR TOHUMLA
             buldugu plan (K-62 ilke 1: ayni baslangicla motor kendi planini
             yeniden bulur ve olcu motoru kayirir -- bulgu 22). Sartlar:
             bagimsiz dogrulayicida 0 sert ihlal, fazla mesai 0. Referans en
             iyi plan DEGILDIR; "en az bu kadar iyisi var" demektir.
  3. SEVIYE 1 = taban + talep referanstan turer:
               hedef  = referans planda o hucreye SAYILAN kisi (dogrulayicinin
                        kendi sayimi, HEDEF_KAPSAMA / HEDEF_ASIMI satirlarindan),
               asgari = hedef - 1, en az 1 (hedef 0 ise 0) -- Mustafa, 12 Ekim
                        15:55: "asgariyi hedefe yakin tutalim",
               HEDEF_ASIMI SERT.
             Talep tablosunda olmayan saat EKLENMEZ.

BEKCILER (testler/test_merdiven.py)
  (a) kayitli referans, kayitli seviye 1 sahnesinde: 0 sert, 0 asim, 0 eksik,
      fazla mesai 0 -- 500 kisilik, cozucusuz, saniyeler;
  (b) kucuk kopya (olcek 0.1) her test kosusunda cozulur, asim 0;
  500 kisilik COZUM bekcisi ayri, haftalik CI isi (Mustafa, 12 Ekim 22:11).

KULLANIM (PowerShell, 08-motor-testleri\\gercekci-veri-seti icinde)
  py merdiven.py referans --olcek 1.0 --saniye 900 --tohum 7
      -> fikstur/_referans-L1-95.json   (cozucu kosar; ~15-20 dk)
  py merdiven.py turet --olcek 1.0
      -> fikstur/_sahne-L1-95.json      (referans dosyasindan; saniyeler)
  Kucuk kopya: --olcek 0.1 (dosya adlarina -0.1 eklenir).
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

import uret_veri_seti as U                                     # noqa: E402

CIFT_YETKINLIKLI_SATISCI = 10          # Mustafa, 12 Ekim 22:03 (K-62'deki 20'nin yerine)
BO_GECE_SAATLERI = range(0, 8)
BO_GECE_ASGARI, BO_GECE_HEDEF = 2, 3   # K-62; hedef 3 Mustafa 12 Ekim 21:58
DOLULUK = 0.95
VARSAYILAN_TOHUM = 7                   # 6 Ekim on denemesinde de 7 (varsayilan arama 0..)


def dosya_eki(olcek):
    return "" if float(olcek) == 1.0 else "-%s" % ("%g" % float(olcek))


def sahne_yolu(olcek):
    return os.path.join(BURASI, "fikstur", "_sahne-L1-95%s.json" % dosya_eki(olcek))


def referans_yolu(olcek):
    return os.path.join(BURASI, "fikstur", "_referans-L1-95%s.json" % dosya_eki(olcek))


# ----------------------------------------------------------------------
# 1. Taban
# ----------------------------------------------------------------------

def cift_yetkinlikli_sayisi(olcek):
    return max(1, int(round(CIFT_YETKINLIKLI_SATISCI * float(olcek))))


def taban_sahne(olcek=1.0):
    """S30-95 sahnesi + K-62 kadro kararlari. HEDEF_ASIMI YUMUSAK kalir."""
    g = U.sahne_uret(olcek, DOLULUK)
    satiscilar = [c for c in g["calisanlar"]
                  if c.get("ekipler") == ["SATIS"] and c.get("durum", "aktif") == "aktif"]
    rnd = random.Random(U.TOHUM + 62)                  # K-62; ayri akis, tabani bozmaz
    secilen = sorted(rnd.sample(range(len(satiscilar)), cift_yetkinlikli_sayisi(olcek)))
    for i in secilen:
        satiscilar[i]["ekipler"] = ["SATIS", "BACKOFFICE"]     # SATIS birincil kalir
    asgari = max(1, int(round(BO_GECE_ASGARI * float(olcek))))
    hedef = max(asgari, int(round(BO_GECE_HEDEF * float(olcek))))
    for t in g["talep"]:
        if t["ekip"] == "BACKOFFICE" and t["saat"] in BO_GECE_SAATLERI:
            t["asgari"], t["hedef"] = asgari, hedef
            t["_sahada_taban"] = min(t.get("_sahada_taban", asgari), asgari)
    g["_merdiven"] = {"seviye": "taban-1", "cift_yetkinlikli": [satiscilar[i]["id"] for i in secilen],
                      "bo_gece": {"asgari": asgari, "hedef": hedef}}
    return g


# ----------------------------------------------------------------------
# 2. Hucre sayimi -- BAGIMSIZ DOGRULAYICININ kendi ciktisindan
# ----------------------------------------------------------------------

def hucre_sayimi(g, atamalar):
    """(ekip, gun, saat) -> o hucreye SAYILAN kisi.

    Kendi sayimimizi yazmiyoruz: dogrulayici hedeften SAPAN hucreyi
    HEDEF_KAPSAMA (eksik) ya da HEDEF_ASIMI (fazla) satiriyla `olculen` alaninda
    yazar; sapmayan hucrede sayilan kisi hedefin kendisidir. Boylece hedef,
    motorun ve dogrulayicinin ayri ayri yazdigi sayimla degil, KAPIDA kullanilan
    sayimla turer (K-41 atanmis, K-50 cok ekipli, K-56 devir dahil)."""
    from dogrulayici import degerlendir
    r = degerlendir(g, atamalar)
    sapan = {}
    for i in r.get("ihlaller", []):
        if i.get("kural") in ("HEDEF_KAPSAMA", "HEDEF_ASIMI"):
            sapan[(i.get("ekip"), i.get("gun"), i.get("saat"))] = i.get("olculen")
    return {(t["ekip"], t["gun"], t["saat"]): sapan.get((t["ekip"], t["gun"], t["saat"]), t.get("hedef"))
            for t in g["talep"]}


def asgari_kurali(hedef):
    """Mustafa, 12 Ekim 15:55: asgari hedefe yakin -- hedef - 1, en az 1; hedef 0 ise 0."""
    return hedef - 1 if hedef >= 2 else hedef


# ----------------------------------------------------------------------
# 3. Seviye 1
# ----------------------------------------------------------------------

def seviye1_sahne(taban, referans_atamalar):
    g = copy.deepcopy(taban)
    sayim = hucre_sayimi(taban, referans_atamalar)
    for t in g["talep"]:
        h = int(sayim[(t["ekip"], t["gun"], t["saat"])])
        t["hedef"] = h
        t["asgari"] = asgari_kurali(h)
        if "_sahada_taban" in t:
            t["_sahada_taban"] = min(t["_sahada_taban"], t["asgari"]) if t["asgari"] else 0
    for k in g["kurallar"]:
        if k["kod"] == "HEDEF_ASIMI":
            k["tur"] = "SERT"                                    # K-67
    g["_merdiven"] = dict(taban.get("_merdiven") or {}, seviye=1,
                          hedef_kisi_saat=sum(t["hedef"] for t in g["talep"]),
                          asgari_kisi_saat=sum(t["asgari"] for t in g["talep"]))
    g["_hedef_kisi_saat"] = g["_merdiven"]["hedef_kisi_saat"]
    return g


# ----------------------------------------------------------------------
# 3b. Cesitler -- AYIRMA OLCUMU (13 Ekim; bulgu 31)
# ----------------------------------------------------------------------
#
# 13 Ekim taban olcumu: seviye 1'de (500 kisi, 900 sn x 3) yalniz 1 kosu plan
# buldu (fazla mesai 7,5 sa); 2 kosu HIC plan bulamadi. Bulutta (2 cekirdek)
# asim yumusatilinca da, eski asgariyle de bulamadi; eski S30 buldu. Mustafa
# (13 Ekim 14:00): "C secmek istiyorum ama olcerek gitmek istiyorum" -- sebep
# onun 6 cekirdeginde ayrilir. Cesitler seviye 1'den TURER; seviye 1 dosyasi
# degismez. "pay1" (a) adayi: setin KOLAYLASTIRILMIS hali (sartname #6
# madde 7: kolaylastiran ayar acikca yazilir).
CESITLER = {
    "asim_yumusak": "HEDEF_ASIMI YUMUSAK; asgari hedef - 1 AYNEN (ayirma: sert asim mi tikiyor?)",
    "eski_asgari": "asgari = min(hedef, taban asgarisi); HEDEF_ASIMI SERT (ayirma: dar asgari mi tikiyor?)",
    "pay1": "hedef = referans + 1, asgari = referans - 1 (en az 1; 0 ise 0); HEDEF_ASIMI SERT "
            "-- (a) adayi, KOLAYLASTIRILMIS (referansin eksigi = hucre basina 1)",
    # K-68 (13 Ekim): ust tolerans -- talep AYNEN, sert ust sinir hedef + k;
    # hedef ile sinir arasi YUMUSAK ceza. Referans (asim 0) gecerli ve ayni puanda.
    "tol1": "HEDEF_ASIMI SERT, ust_tolerans 1 (hucre [hedef - 1, hedef + 1]; ust bant cezali) -- K-68",
    "tol2": "HEDEF_ASIMI SERT, ust_tolerans 2 (hucre [hedef - 1, hedef + 2]; ust bant cezali) -- K-68",
}


def cesit_sahne(g, ad, olcek=1.0):
    """Seviye 1 sahnesinden ayirma cesidi. Referans plan her cesitte GECERLIDIR
    (0 sert); `pay1`de hedefin 1 altinda kalir (eksik bilinir)."""
    if ad not in CESITLER:
        raise SystemExit("bilinmeyen cesit %s (olanlar: %s)" % (ad, ", ".join(CESITLER)))
    g = copy.deepcopy(g)
    if ad == "asim_yumusak":
        for k in g["kurallar"]:
            if k["kod"] == "HEDEF_ASIMI":
                k["tur"] = "YUMUSAK"
    elif ad == "eski_asgari":
        eski = {(t["ekip"], t["gun"], t["saat"]): t["asgari"] for t in taban_sahne(olcek)["talep"]}
        for t in g["talep"]:
            t["asgari"] = min(t["hedef"], eski[(t["ekip"], t["gun"], t["saat"])])
    elif ad == "pay1":
        for t in g["talep"]:
            ref = t["hedef"]                       # seviye 1'de hedef = referans sayimi
            t["hedef"] = ref + 1
            t["asgari"] = asgari_kurali(ref)
    elif ad in ("tol1", "tol2"):
        for k in g["kurallar"]:
            if k["kod"] == "HEDEF_ASIMI":
                k["parametreler"] = dict(k.get("parametreler") or {}, ust_tolerans=int(ad[3:]))
    for t in g["talep"]:
        if "_sahada_taban" in t:
            t["_sahada_taban"] = min(t["_sahada_taban"], t["asgari"]) if t["asgari"] else 0
    g["_merdiven"] = dict(g["_merdiven"], cesit=ad, cesit_aciklama=CESITLER[ad],
                          hedef_kisi_saat=sum(t["hedef"] for t in g["talep"]),
                          asgari_kisi_saat=sum(t["asgari"] for t in g["talep"]))
    g["_merdiven"].pop("referans_puani", None)    # cesitte yeniden hesaplanir (plan_puani)
    return g


def referans_denetle(g, atamalar):
    """Referansin sartlari -- bekci (a) ve uretim ayni fonksiyonu kullanir.
    Donen: {sert, asim, eksik, fazla_mesai_saat} (hepsi 0 beklenir)."""
    from dogrulayici import degerlendir
    r = degerlendir(g, atamalar)
    sert = [i for i in r["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    return {"sert": len(sert),
            "sert_kurallar": sorted({i["kural"] for i in sert}),
            "asim": sum(1 for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"),
            "eksik": sum(1 for i in r["ihlaller"] if i["kural"] == "HEDEF_KAPSAMA"),
            "fazla_mesai_saat": round(r["metrikler"].get("fazla_mesai_saat") or 0.0, 2),
            "yayinlanabilir": r["yayin_kapisi"]["yayinlanabilir"]}


def plan_puani(g, atamalar, saniye=120):
    """Verilen planin BU SAHNEDEKI amac degeri ve kural kirilimi -- motorun
    kendi olcusuyle. Atamalar ve molalar modele SABITLENIR (ipucu degil,
    esitlik kisiti); yalniz ceza degiskenleri serbest kalir ve en kucuge
    iner, yani her ceza tam olarak plandaki ihlali olcer.

    NEDEN: referansin tabandaki puani seviye 1'de gecersizdir -- MOLA_KAPSAMASI
    asgariye bakar ve asgari degisti; hedef eksigi/asimi da 0'a indi. Kalem
    kalem kiyas (K-62 ilke 3) ayni sahnede ayni olcuyle yapilmali.
    Plan modele oturmazsa (sablon/kisi yok) None."""
    from ortools.sat.python import cp_model
    from cozucu.model import Model
    from cozucu.coz import _plandan_ipucu, _amac_dagilimi
    k = Model(copy.deepcopy(g)).kur()
    if not _plandan_ipucu(k, atamalar):
        return None
    proto = k.m.Proto()
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    for sozluk in (k.x, k.mola, k.dinlenme):
        for v in sozluk.values():
            k.m.Add(v == ipucu.get(v.Index(), 0))
    k.m.Minimize(sum(a * v for a, v in k.cezalar))
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = os.cpu_count() or 1
    durum = c.Solve(k.m)
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"durum": c.StatusName(durum)}
    return {"durum": c.StatusName(durum), "amac": int(round(c.ObjectiveValue())),
            "dagilim": {kod: {"ceza": d["ceza"], "deger": d["deger"]}
                        for kod, d in _amac_dagilimi(k, c).items()}}


def referans_uret(olcek, saniye, tohum=VARSAYILAN_TOHUM):
    """Tabanda motoru BASKA TOHUMLA kostur; sartlari saglamazsa hata ver."""
    from cozucu.coz import coz
    taban = taban_sahne(olcek)
    # Baska baslangic: birinci asamanin fazla mesaisiz denemeleri `tohum`dan
    # baslar (urun 1'den), ana aramanin tohumu da `tohum` (K-62 ilke 1).
    # Fazla mesaisiz plan bulununca fazla mesai BUTUN asamalarda 0'da tutulur
    # (`fazla_mesai_sifirda_tut`, olcum secenegi "sert kesim" -- O-18). Urun
    # yolu bunu yapmaz (K-61: hakem agirliklar); referansin urun yolu olmasi
    # gerekmez, GECERLI ve FAZLA MESAISIZ olmasi gerekir (K-62 seviye 1).
    # 12 Ekim bulut denemesi: urun yoluyla tohum 7 plani 16 saat fazla
    # mesaiyle dondu (2 cekirdekte fazla mesaisiz ilk arama 3 x 40 sn'de
    # bulamadi -- eski S30'da da; Mustafa'nin 6 cekirdeginde 9-21 sn).
    ayar = {"azami_saniye": int(saniye), "tohum_kaydirma": int(tohum) - 1,
            "fazla_mesai_sifirda_tut": True,
            "cozucu_parametreleri": {"random_seed": int(tohum)}}
    basla = time.time()
    c = coz(copy.deepcopy(taban), ayar)
    sure = time.time() - basla
    if c.get("durum") != "cozuldu":
        raise SystemExit("REFERANS BULUNAMADI: durum %s" % c.get("durum"))
    d = referans_denetle(taban, c["atamalar"])
    ist = c.get("cozum_istatistikleri") or {}
    if d["sert"] or d["fazla_mesai_saat"]:
        raise SystemExit("REFERANS SARTI TUTMADI (tabanda): %s | fazla mesaisiz ilk arama: %s"
                         % (d, (ist.get("fazla_mesai_once_sifir") or {}).get("denemeler")))
    return {
        "atamalar": c["atamalar"],
        "kayit": {"olcek": olcek, "doluluk": DOLULUK, "tohum": int(tohum), "saniye": int(saniye),
                  "sure_sn": round(sure, 1), "tarih": time.strftime("%Y-%m-%d %H:%M"),
                  "cekirdek": os.cpu_count(), "makine": os.environ.get("COMPUTERNAME") or "bulut",
                  "amac_degeri": ist.get("amac_degeri"),
                  "amac_dagilimi": ist.get("amac_dagilimi"),
                  "metrikler": c.get("metrikler"),
                  "fazla_mesaisiz_ilk_arama": (ist.get("fazla_mesai_once_sifir") or {}).get("denemeler"),
                  "yol": "tohum_kaydirma + fazla_mesai_sifirda_tut (sert kesim; urun yolu degil)",
                  "tabanda_denetim": d,
                  "not": ("K-62 ilke 1: referans en iyi plan degil, 'en az bu kadar iyisi "
                          "var'. Tohum varsayilan aramadan farkli (baska baslangic).")},
    }


def _yaz(yol, veri):
    with io.open(yol, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1)


def _arg(ad, varsayilan, tur=str):
    return tur(sys.argv[sys.argv.index(ad) + 1]) if ad in sys.argv else varsayilan


if __name__ == "__main__":
    komut = sys.argv[1] if len(sys.argv) > 1 else ""
    olcek = _arg("--olcek", 1.0, float)
    if komut == "referans":
        ref = referans_uret(olcek, _arg("--saniye", 900, int), _arg("--tohum", VARSAYILAN_TOHUM, int))
        _yaz(referans_yolu(olcek), ref)
        k = ref["kayit"]
        print("REFERANS yazildi: %s" % referans_yolu(olcek))
        print("  %d atama | amac %s | %.0f sn | tabanda denetim %s"
              % (len(ref["atamalar"]), k["amac_degeri"], k["sure_sn"], k["tabanda_denetim"]))
        komut = "turet"                                 # referanstan hemen turet
    if komut == "turet":
        ref = json.load(io.open(referans_yolu(olcek), encoding="utf-8"))
        g = seviye1_sahne(taban_sahne(olcek), ref["atamalar"])
        d = referans_denetle(g, ref["atamalar"])
        if d["sert"] or d["asim"] or d["eksik"] or d["fazla_mesai_saat"]:
            raise SystemExit("SEVIYE 1 TUTARSIZ: referans yeni sahnede %s" % d)
        p = plan_puani(g, ref["atamalar"])
        if not p or p.get("durum") != "OPTIMAL":
            raise SystemExit("REFERANSIN SEVIYE 1 PUANI HESAPLANAMADI: %s" % p)
        g["_merdiven"]["referans_puani"] = p
        _yaz(sahne_yolu(olcek), g)
        m = g["_merdiven"]
        print("SEVIYE 1 yazildi: %s" % sahne_yolu(olcek))
        print("  %d kisi | %d hucre | hedef %d kisi-saat | asgari %d | cift yetkinlikli %d | "
              "referans yeni sahnede %s"
              % (len(g["calisanlar"]), len(g["talep"]), m["hedef_kisi_saat"],
                 m["asgari_kisi_saat"], len(m["cift_yetkinlikli"]), d))
        print("  referansin seviye 1 puani %d  %s" % (p["amac"], {k: v["ceza"] for k, v in p["dagilim"].items()}))
    elif komut not in ("referans",):
        print(__doc__)
