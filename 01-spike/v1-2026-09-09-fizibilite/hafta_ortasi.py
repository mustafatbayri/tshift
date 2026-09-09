#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hafta_ortasi.py — HAFTA ORTASI YENİDEN PLANLAMA

SENARYO
Pazartesi plan yayınlandı. Pzt-Çar yaşandı: çoğu kişi planlandığı gibi geldi,
bir kısmı hastalandı ve hiç gelmedi, bir kısmı farklı saatlerde çalıştı.
Perşembe sabahı kalan dört gün yeniden planlanıyor.

MİMARİ KARARI — bu testin asıl konusu
    Pzt-Çar artık KARAR değil GERÇEK. Onları "kilit" olarak modellemek yanlış
    olurdu, çünkü kilit hâlâ bir karar değişkenidir ve şablona uymak zorundadır.
    Gerçekleşen 07:12-15:40 hiçbir şablona uymaz.

    Doğrusu SABİT ATAMA: kapsamaya sayılır, haftalık saat bütçesinden düşer,
    11 saat dinlenme kuralını bağlar — ama motorun oynayabileceği bir değişken
    değildir. Böylece gerçek veri, şablon kalıbına zorlanmadan sisteme girer.

ÖLÇÜLEN
  1. Gerçekleşen günler plana AYNEN yansıdı mı
  2. Kalan günler hâlâ geçerli mi (sert ihlal)
  3. Hastalanan kişinin boşta kalan saatleri kalan günlerde kullanılabildi mi
  4. Kalan günlerde yayınlanmış plana göre ne kadar değişiklik oldu

Kullanım:
    py hafta_ortasi.py                    # çağrı merkezi
    py hafta_ortasi.py girdi_otel.json    # otel
"""

import copy
import json
import os
import random
import sys

from degerlendirici import Degerlendirici, sf
from planla import Planlayici, metrikler

DONMUS_GUN = 3           # Pzt, Sal, Çar gerçekleşti
TOHUM = 4242


def onek(yol):
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


def plan_uret(girdi, profil="DENGELI"):
    w = dict(girdi["hedef_profilleri"][profil])
    w.setdefault("kararlilik", w.pop("tercih", 5))
    return Planlayici(girdi, profil, w).calistir()


# --------------------------------------------------------------------
# Gerçekleşme benzetimi
# --------------------------------------------------------------------

def gerceklesen_uret(plan, gun_sayisi=DONMUS_GUN, tohum=TOHUM):
    """Planın ilk günlerinin nasıl GERÇEKLEŞTİĞİNİ üret.

    %90 planlandığı gibi · %6 hiç gelmedi (hastalık) · %4 farklı saatlerde
    çalıştı (geç geldi / geç çıktı). Gerçek hayatta olan tam olarak budur;
    bu yüzden gerçekleşen veri plana eşit varsayılamaz.
    """
    rnd = random.Random(tohum)
    sabit, gelmeyen, kayan = [], [], []
    for a in plan["atamalar"]:
        if a["gun"] >= gun_sayisi:
            continue
        z = rnd.random()
        if z < 0.06:
            gelmeyen.append(a)
            continue
        b, t = sf(a["bas"]), sf(a["bit"])
        if z < 0.10:
            b += rnd.choice([0.25, 0.5])          # geç geldi
            t += rnd.choice([0.0, 0.25, 0.5])     # geç çıktı
            kayan.append(a)
        sabit.append({
            "calisan": a["calisan"], "ekip": a["ekip"], "gun": a["gun"],
            "bas": f"{int(b):02d}:{int(round((b-int(b))*60)):02d}",
            "bit": f"{int(t):02d}:{int(round((t-int(t))*60)):02d}",
            "mola_dk": a.get("mola_dk", 0), "mola_saat": a.get("mola_saat"),
            "sablon": a.get("sablon"), "kaynak": "GERCEKLESEN",
        })
    return sabit, gelmeyen, kayan


def gun_metrigi(girdi, plan, gunler):
    """Yalnız belirli günler için kapsama ölçümü."""
    d = Degerlendirici(girdi)
    var = {}
    from degerlendirici import hucre
    for a in plan["atamalar"]:
        mh = int(sf(a["mola_saat"])) if a.get("mola_saat") else None
        for h in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            if h == mh:
                continue
            var[(a["ekip"],) + hucre(a["gun"], h)] = \
                var.get((a["ekip"],) + hucre(a["gun"], h), 0) + 1
    ht = at = hk = ak = 0
    for t in girdi["talep"]:
        if t["gun"] not in gunler:
            continue
        m = var.get((t["ekip"], t["gun"], t["saat"]), 0)
        ht += t["hedef"]; at += t["asgari"]
        hk += min(m, t["hedef"]); ak += min(m, t["asgari"])
    return {"hedef": hk / max(1, ht), "asgari": ak / max(1, at),
            "eksik": ht - hk}


def degisim(p0, p1, gunler):
    a = {(x["calisan"], x["gun"], x["sablon"]) for x in p0["atamalar"]
         if x["gun"] in gunler}
    b = {(x["calisan"], x["gun"], x["sablon"]) for x in p1["atamalar"]
         if x["gun"] in gunler}
    return {"oran": len(a ^ b) / max(1, len(a | b)),
            "kisi": len({k[0] for k in (a ^ b)})}


# --------------------------------------------------------------------

def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    p_onek = onek(yol)
    girdi = json.load(open(yol, encoding="utf-8"))
    gun_sayisi = girdi["donem"]["gun"]
    donmus = list(range(DONMUS_GUN))
    kalan = list(range(DONMUS_GUN, gun_sayisi))

    print("=" * 72)
    print("HAFTA ORTASI YENİDEN PLANLAMA")
    print("=" * 72)
    print(f"  veri seti : {yol}")
    print(f"  donmuş    : gün {donmus}  (gerçekleşti)")
    print(f"  planlanan : gün {kalan}\n")

    # --- 1) Pazartesi yayınlanan plan ---
    p0 = plan_uret(girdi)
    d = Degerlendirici(girdi)
    s0 = sum(1 for i in d.calistir(p0) if i.tur == "SERT")
    m0 = metrikler(girdi, p0, d)
    print("1) PAZARTESİ YAYINLANAN PLAN")
    print(f"     sert ihlal {s0} · hedef kapsama "
          f"%{100*m0['hedef_karsilama']:.1f} · {m0['atama']} atama")

    # --- 2) Pzt-Çar nasıl gerçekleşti ---
    sabit, gelmeyen, kayan = gerceklesen_uret(p0)
    print(f"\n2) GÜN {donmus} GERÇEKLEŞMESİ")
    print(f"     planlandığı gibi : {len(sabit) - len(kayan)}")
    print(f"     gelmeyen (hasta) : {len(gelmeyen)}")
    print(f"     saati kayan      : {len(kayan)}  (şablona uymayan gerçek veri)")
    if kayan:
        k = next(x for x in sabit
                 if x["calisan"] == kayan[0]["calisan"] and x["gun"] == kayan[0]["gun"])
        print(f"     örnek: {k['calisan']} planda "
              f"{kayan[0]['bas']}–{kayan[0]['bit']}, gerçekte "
              f"{k['bas']}–{k['bit']}")

    kayip = {}
    for a in gelmeyen:
        kayip[a["calisan"]] = kayip.get(a["calisan"], 0) + \
            (sf(a["bit"]) - sf(a["bas"])) - a.get("mola_dk", 0) / 60.0

    # --- 3) Perşembe: kalan günleri yeniden planla ---
    g2 = copy.deepcopy(girdi)
    g2["sabit_atamalar"] = sabit
    g2["donmus_gunler"] = donmus
    g2["referans_atamalar"] = [
        {"calisan": a["calisan"], "gun": a["gun"], "sablon": a["sablon"]}
        for a in p0["atamalar"] if a["gun"] in kalan]
    g2["kararlilik_odulu"] = 40
    p1 = plan_uret(g2)

    d2 = Degerlendirici(g2)
    ihl = [i for i in d2.calistir(p1) if i.tur == "SERT"]
    kod = {}
    for i in ihl:
        kod[i.kod] = kod.get(i.kod, 0) + 1

    print("\n3) PERŞEMBE — KALAN GÜNLER YENİDEN PLANLANDI")
    gecmis_ihl = [i for i in ihl if i.gun in donmus]
    plan_ihl = [i for i in ihl if i.gun not in donmus]
    kodp = {}
    for i in plan_ihl:
        kodp[i.kod] = kodp.get(i.kod, 0) + 1
    print(f"     kalan günlerde sert ihlal   : {len(plan_ihl)}  "
          f"{kodp if kodp else ''}")
    print(f"     geçmiş günlerde sert ihlal  : {len(gecmis_ihl)}  "
          f"(gerçekleşmiş; düzeltilemez, raporlanır)")

    # gerçekleşen günler aynen duruyor mu
    yeni_donmus = {(a["calisan"], a["gun"], a["bas"], a["bit"])
                   for a in p1["atamalar"] if a["gun"] in donmus}
    beklenen = {(a["calisan"], a["gun"], a["bas"], a["bit"]) for a in sabit}
    print(f"     gerçekleşen günler korundu : "
          f"{'EVET' if yeni_donmus == beklenen else 'HAYIR'}"
          f"  ({len(beklenen)} atama)")

    mk0 = gun_metrigi(girdi, p0, kalan)
    mk1 = gun_metrigi(g2, p1, kalan)
    dg = degisim(p0, p1, kalan)
    print(f"\n     kalan günlerde hedef kapsama:")
    print(f"        yayınlanan plan : %{100*mk0['hedef']:.1f}")
    print(f"        yeniden plan    : %{100*mk1['hedef']:.1f}")
    print(f"     kalan günlerde değişim : %{100*dg['oran']:.1f} "
          f"({dg['kisi']} kişi etkilendi)")

    # --- 4) Hastalananların boşta kalan saatleri kullanıldı mı ---
    print("\n4) HASTALANANLARIN BOŞTA KALAN SAATLERİ")
    if not kayip:
        print("     Gelmeyen yok.")
    else:
        net0, net1 = {}, {}
        for a in p0["atamalar"]:
            if a["gun"] in kalan:
                net0[a["calisan"]] = net0.get(a["calisan"], 0) + d.net_saat(a)
        for a in p1["atamalar"]:
            if a["gun"] in kalan:
                net1[a["calisan"]] = net1.get(a["calisan"], 0) + d.net_saat(a)
        artan = azalan = 0
        toplam_artis = 0.0
        for cid, sa in kayip.items():
            f = net1.get(cid, 0.0) - net0.get(cid, 0.0)
            if f > 0.01:
                artan += 1; toplam_artis += f
            elif f < -0.01:
                azalan += 1
        print(f"     {len(kayip)} kişi hastalandı, toplam {sum(kayip.values()):.1f} "
              f"saat boşa çıktı")
        print(f"     kalan günlerde daha çok çalışan : {artan} kişi "
              f"(+{toplam_artis:.1f} sa)")
        print(f"     kalan günlerde daha az çalışan  : {azalan} kişi")
        if artan:
            print("     → Motor, hastalıktan boşalan kapasiteyi kalan günlerde")
            print("       kullanabiliyor. Haftalık saat bütçesi doğru güncelleniyor.")

    json.dump(p1, open(f"plan_{p_onek}HAFTAORTASI.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("\n" + "=" * 72)
    ok = (yeni_donmus == beklenen)
    print("SONUÇ: gerçekleşen günler korunuyor, kalan günler yeniden planlanıyor."
          if ok else "SONUÇ: GERÇEKLEŞEN GÜNLER BOZULDU — kabul edilemez.")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
