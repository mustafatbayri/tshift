#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cok_hafta.py — ÇOK HAFTALIK DEVİR VE ADALET

SORU
Dört haftayı üst üste planlıyoruz. Her hafta bir öncekini geçmiş olarak alıyor.
Gece nöbeti, hafta sonu ve tatil günü kişiler arasında DÖNÜYOR mu, yoksa hep
aynı kişilere mi düşüyor?

NEDEN ÖNEMLİ
Tek haftaya bakınca plan kusursuz görünür: kurallar sağlanmış, saatler dengeli.
Ama motorun haftalar arası hafızası yoksa her hafta AYNI kararı verir — çünkü
girdi aynı, kural aynı, çözücü deterministik. Dört hafta sonra aynı beş kişi
on iki gece nöbeti tutmuş olur ve İK "bu sistem adaletsiz" der. Haftalık
adalet ölçüsü bunu göremez; ancak haftalar üst üste konunca görünür.

ÇÖZÜM (ölçüldükten sonra eklendi)
Her haftanın planı, bir sonraki haftaya DEVİR YÜKÜ olarak taşınır: kim kaç
gece tuttu, kaç hafta sonu çalıştı. Motor bu birikimi puanlamada kullanır.
Adalet artık haftanın içinde değil, haftalar boyunca ölçülür.

Kullanım:
    py cok_hafta.py                    # çağrı merkezi (hafta sonu + tatil günü)
    py cok_hafta.py girdi_otel.json    # otel (gece nöbeti de ölçülür)
"""

import copy
import json
import os
import sys
from datetime import date, timedelta
from statistics import pstdev

from degerlendirici import Degerlendirici, sf
from planla import Planlayici, metrikler

HAFTA = 4


def onek(yol):
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


def gece_sablonlari(girdi):
    """Gece penceresine düşen şablonlar (kural varsa)."""
    k = {x["kod"]: x for x in girdi["kurallar"]}.get("GECE_VARDIYASI_AZAMI")
    if not k:
        return set()
    b, t = int(sf(k["param"]["bas"])), int(sf(k["param"]["bit"]))

    def gece(h):
        x = h % 24
        return (b <= x or x < t) if b > t else (b <= x < t)

    out = set()
    for s in girdi["sablonlar"]:
        if any(gece(h) for h in range(int(sf(s["bas"])), int(sf(s["bit"])))):
            out.add(s["id"])
    return out


def plana_gecmis(plan, baslangic: date):
    """Bir haftanın planını, sonraki haftanın geçmiş kaydına çevir."""
    return [{"calisan": a["calisan"],
             "tarih": (baslangic + timedelta(days=a["gun"])).isoformat(),
             "bas": a["bas"], "bit": a["bit"], "kaynak": "GERCEKLESEN"}
            for a in plan["atamalar"]]


def yuk_topla(planlar, gece_sab):
    """Kişi bazında birikim: gece, hafta sonu, saat, tatil günleri."""
    y = {}
    for p in planlar:
        for a in p["atamalar"]:
            r = y.setdefault(a["calisan"],
                             {"gece": 0, "hafta_sonu": 0, "saat": 0.0,
                              "gunler": []})
            if a["sablon"] in gece_sab:
                r["gece"] += 1
            if a["gun"] >= 5:
                r["hafta_sonu"] += 1
            r["saat"] += (sf(a["bit"]) - sf(a["bas"])) - a.get("mola_dk", 0) / 60.0
            r["gunler"].append(a["gun"])
    return y


def dagilim(y, alan, aktif):
    """Bir yükün kişiler arasındaki dağılımı.

    DİKKAT: 'aktif' burada YÜKÜ ALABİLECEK kişilerdir. Gece nöbetini 295
    kişinin tamamı üzerinden ölçmek yanıltıcıydı — gece vardiyası yalnız iki
    departmanda var, geri kalanı yapısal olarak gece alamaz. Adalet, yükü
    taşıyabilecek grup içinde ölçülür.
    """
    d = [y.get(c["id"], {}).get(alan, 0) for c in aktif]
    toplam = sum(d)
    if toplam == 0:
        return None
    d_sirali = sorted(d, reverse=True)
    ust_dilim = max(1, len(d) // 10)
    return {
        "toplam": toplam,
        "en_cok": d_sirali[0],
        "en_az": d_sirali[-1],
        "ortalama": round(toplam / len(d), 2),
        "sapma": round(pstdev(d), 2),
        "hic_almayan": sum(1 for x in d if x == 0),
        "ust_yuzde10_payi": round(100 * sum(d_sirali[:ust_dilim]) / toplam, 1),
        "kisi": len(d),
    }


def hafta_bazinda_bos_gun(planlar, aktif):
    """Her hafta için kişinin boş günleri; kaç kişide hep aynı gün boş?"""
    hep_ayni = 0
    olculen = 0
    for c in aktif:
        haftalik = []
        for p in planlar:
            calisti = {a["gun"] for a in p["atamalar"] if a["calisan"] == c["id"]}
            bos = set(range(7)) - calisti
            haftalik.append(bos)
        if any(not b for b in haftalik):
            continue
        olculen += 1
        ortak = set.intersection(*haftalik)
        if ortak and len(ortak) == min(len(b) for b in haftalik):
            hep_ayni += 1
    return hep_ayni, olculen


# --------------------------------------------------------------------

def kos(girdi, hafta=HAFTA, devir_adalet=0.0):
    """Haftaları üst üste planla; her hafta öncekini geçmiş olarak alır."""
    planlar = []
    gece_sab = gece_sablonlari(girdi)
    baslangic = date.fromisoformat(girdi["donem"]["baslangic"])
    gecmis = list(girdi["gecmis"])
    birikim = {}

    for h in range(hafta):
        g = copy.deepcopy(girdi)
        hafta_bas = baslangic + timedelta(days=7 * h)
        g["donem"]["baslangic"] = hafta_bas.isoformat()
        # yalnız son 14 günü taşı (kural pencereleri o kadarını görüyor)
        sinir = (hafta_bas - timedelta(days=14)).isoformat()
        g["gecmis"] = [x for x in gecmis if x["tarih"] >= sinir]
        g["devir_yuk"] = birikim
        g["devir_adalet_odulu"] = devir_adalet

        w = dict(g["hedef_profilleri"]["DENGELI"])
        w.setdefault("kararlilik", w.pop("tercih", 5))
        p = Planlayici(g, "DENGELI", w).calistir()
        planlar.append(p)

        d = Degerlendirici(g)
        sert = sum(1 for i in d.calistir(p) if i.tur == "SERT")
        m = metrikler(g, p, d)
        print(f"    hafta {h+1}: sert ihlal {sert:>2} · "
              f"hedef kapsama %{100*m['hedef_karsilama']:.1f} · "
              f"{m['atama']} atama")

        gecmis += plana_gecmis(p, hafta_bas)
        birikim = yuk_topla(planlar, gece_sab)
    return planlar, gece_sab


def gece_ekipleri(girdi, gece_sab):
    return {s["ekip"] for s in girdi["sablonlar"] if s["id"] in gece_sab}


def rapor(planlar, gece_sab, aktif, baslik, gece_havuz=None):
    y = yuk_topla(planlar, gece_sab)
    print(f"\n  {baslik}")
    for alan, ad in (("gece", "GECE NÖBETİ"), ("hafta_sonu", "HAFTA SONU")):
        havuz = gece_havuz if (alan == "gece" and gece_havuz) else aktif
        d = dagilim(y, alan, havuz)
        if not d:
            continue
        if alan == "gece" and gece_havuz:
            print(f"    (gece alabilen {len(havuz)} kişi üzerinden)")
        print(f"    {ad}: toplam {d['toplam']} · kişi başı ort {d['ortalama']}"
              f" · sapma {d['sapma']}")
        print(f"       en çok alan {d['en_cok']}, hiç almayan {d['hic_almayan']} kişi"
              f" · en yüklü %10 toplamın %{d['ust_yuzde10_payi']}'ini taşıyor")
    ayni, olculen = hafta_bazinda_bos_gun(planlar, aktif)
    if olculen:
        print(f"    TATİL GÜNÜ: {olculen} kişiden {ayni} tanesinde boş gün "
              f"her hafta AYNI  (%{100*ayni/olculen:.0f})")
    return y


def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    girdi = json.load(open(yol, encoding="utf-8"))
    aktif = [c for c in girdi["calisanlar"] if c["durum"] == "AKTIF"]

    print("=" * 72)
    print(f"ÇOK HAFTALIK DEVİR — {HAFTA} hafta üst üste")
    print("=" * 72)
    print(f"  veri seti: {yol}  ({len(aktif)} aktif çalışan)\n")

    print("1) DEVİR ADALETİ KAPALI  (motorun haftalar arası hafızası yok)")
    p_naif, gece_sab = kos(girdi, HAFTA, devir_adalet=0.0)
    gece_ek = gece_ekipleri(girdi, gece_sab)
    gece_havuz = [c for c in aktif if c["ekip"] in gece_ek] if gece_ek else None
    y_naif = rapor(p_naif, gece_sab, aktif, "4 haftalık birikim:", gece_havuz)

    print("\n2) DEVİR ADALETİ AÇIK  (geçen haftaların yükü puanlamaya giriyor)")
    p_adil, _ = kos(girdi, HAFTA, devir_adalet=6.0)
    y_adil = rapor(p_adil, gece_sab, aktif, "4 haftalık birikim:", gece_havuz)

    print("\n" + "=" * 72)
    print("KARŞILAŞTIRMA")
    print("=" * 72)
    for alan, ad in (("gece", "gece nöbeti"), ("hafta_sonu", "hafta sonu")):
        havuz = gece_havuz if (alan == "gece" and gece_havuz) else aktif
        a = dagilim(y_naif, alan, havuz)
        b = dagilim(y_adil, alan, havuz)
        if not a or not b:
            continue
        print(f"  {ad}:")
        print(f"     sapma            {a['sapma']:>6}  →  {b['sapma']:>6}")
        print(f"     hiç almayan kişi {a['hic_almayan']:>6}  →  {b['hic_almayan']:>6}")
        print(f"     en çok alan      {a['en_cok']:>6}  →  {b['en_cok']:>6}")
        print(f"     %10'un payı      %{a['ust_yuzde10_payi']:>5}  →  "
              f"%{b['ust_yuzde10_payi']:>5}")
    an, on = hafta_bazinda_bos_gun(p_naif, aktif)
    bn, bo = hafta_bazinda_bos_gun(p_adil, aktif)
    if on and bo:
        print(f"  tatil günü hep aynı olan: {an}/{on} → {bn}/{bo}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
