# -*- coding: utf-8 -*-
"""
TShift motor - BAGIMSIZ DOGRULAYICI

NE YAPAR
  Kanonik bir plani kurallara karsi denetler ve IHLAL LISTESI dondurur.

NEDEN "BAGIMSIZ"
  Bu dosya cozucunun (solver) kodunu HIC paylasmaz ve cozucunun "gecerli plan
  urettim" bayragina BAKMAZ. Plani sifirdan kurallara karsi denetler.
  Sebep: cozucuyu ve testini ayni kafa yazarsa, yanlis kural yorumu ikisinde
  de tutarli bicimde tekrar eder ve test yesil yanar.
  Bkz. 00-DEVIR/03-MIMARI-KARARLAR.md M-09.

  BU YUZDEN: bu dosyaya cozucudan hicbir sey import edilmez. Kurallar
  kurallar.json'dan okunur (M-10: kurallar veride, kodda degil).

CALISTIRMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\07-motor
  py donusturucu.py      (once)
  py dogrulayici.py

GIRDI   ../06-veri/kanonik/plan.csv  + kurallar.json
CIKTI   ../06-veri/rapor/ihlaller.csv
        ../06-veri/rapor/dogrulama.txt
"""

import os
import csv
import json
import datetime
import statistics
from collections import defaultdict, Counter

KOK = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(KOK, "..", "06-veri", "kanonik", "plan.csv")
KURAL = os.path.join(KOK, "kurallar.json")
CIKTI = os.path.join(KOK, "..", "06-veri", "rapor")

rapor = []


def yaz(s=""):
    rapor.append(str(s))
    print(s)


def plani_oku(yol):
    kayitlar = []
    with open(yol, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            r["gun"] = datetime.date.fromisoformat(r["gun"])
            r["brut_saat"] = float(r["brut_saat"] or 0)
            for k in ("baslangic", "bitis"):
                r[k] = datetime.datetime.strptime(r[k], "%Y-%m-%d %H:%M") if r[k] else None
            kayitlar.append(r)
    return kayitlar


def dogrula(kayitlar, kurallar):
    """Ihlal listesi dondurur. BOS LISTE = plan gecerli."""
    ih = []
    sk = kurallar["sert_kisitlar"]
    mola = kurallar["mola"]
    disi = kurallar["calisma_disi_kodlar"]
    yok = set(disi["tam_gun_yok"])

    vardiyalar = defaultdict(list)
    durumlar = defaultdict(dict)
    for k in kayitlar:
        if k["tur"] == "VARDIYA":
            vardiyalar[k["sicil"]].append(k)
        else:
            durumlar[k["sicil"]][k["gun"]] = k["ham_deger"]
    for s in vardiyalar:
        vardiyalar[s].sort(key=lambda x: x["baslangic"])

    def ekle(kod, sicil, gun, mesaj, agirlik="SERT"):
        ih.append({"kural": kod, "agirlik": agirlik, "sicil": sicil,
                   "gun": gun.isoformat() if hasattr(gun, "isoformat") else gun,
                   "mesaj": mesaj})

    # --- V02 cakisma -------------------------------------------------------
    if sk["cakisma_yasak"]["aktif"]:
        for sicil, vs in vardiyalar.items():
            for a, b in zip(vs, vs[1:]):
                if b["baslangic"] < a["bitis"]:
                    ekle("V02_CAKISMA", sicil, b["gun"],
                         "%s-%s ile %s-%s cakisiyor" % (
                             a["baslangic"].strftime("%d.%m %H:%M"),
                             a["bitis"].strftime("%H:%M"),
                             b["baslangic"].strftime("%d.%m %H:%M"),
                             b["bitis"].strftime("%H:%M")))

    # --- V03 asgari dinlenme ----------------------------------------------
    k3 = sk["asgari_dinlenme_saat"]
    if k3["aktif"]:
        esik = k3["deger"]
        for sicil, vs in vardiyalar.items():
            for a, b in zip(vs, vs[1:]):
                ara = (b["baslangic"] - a["bitis"]).total_seconds() / 3600
                if 0 <= ara < esik:
                    ekle("V03_DINLENME", sicil, b["gun"],
                         "Onceki vardiya %s bitti, yenisi %s basladi -> %.1f saat (asgari %g)"
                         % (a["bitis"].strftime("%d.%m %H:%M"),
                            b["baslangic"].strftime("%d.%m %H:%M"), ara, esik))

    # --- V04a azami gunluk -------------------------------------------------
    k4 = sk["azami_gunluk_saat"]
    if k4["aktif"]:
        for sicil, vs in vardiyalar.items():
            gunluk = defaultdict(float)
            for v in vs:
                gunluk[v["gun"]] += v["brut_saat"]
            for g, sa in gunluk.items():
                if sa > k4["deger"]:
                    ekle("V04_GUNLUK", sicil, g,
                         "Gunluk brut %.1f saat (azami %g)" % (sa, k4["deger"]))

    # --- V04b azami haftalik (NET: mola dusulur) ---------------------------
    k5 = sk["azami_haftalik_saat"]
    if k5["aktif"]:
        dusum = mola["varsayilan_dusum_saat"] if not mola["ucretli_mi"] else 0.0
        for sicil, vs in vardiyalar.items():
            hafta = defaultdict(lambda: [0.0, 0])
            for v in vs:
                iso = v["gun"].isocalendar()
                a = hafta[(iso[0], iso[1])]
                a[0] += max(v["brut_saat"] - dusum, 0)
                a[1] += 1
            for (yil, h), (net, adet) in hafta.items():
                if net > k5["deger"]:
                    ekle("V04_HAFTALIK", sicil, "%d-H%02d" % (yil, h),
                         "Haftalik net %.1f saat (%d vardiya, mola -%.1f sa/vardiya, azami %g)"
                         % (net, adet, dusum, k5["deger"]))

    # --- Haftalik tatil ----------------------------------------------------
    k6 = sk["haftalik_tatil_zorunlu"]
    if k6["aktif"]:
        for sicil, vs in vardiyalar.items():
            hafta = defaultdict(set)
            for v in vs:
                iso = v["gun"].isocalendar()
                hafta[(iso[0], iso[1])].add(v["gun"])
            for (yil, h), gunler in hafta.items():
                if len(gunler) > 7 - k6["asgari_off_gun"]:
                    ekle("V_HAFTATATIL", sicil, "%d-H%02d" % (yil, h),
                         "Haftada %d gun calisma, tatil gunu yok" % len(gunler))

    # --- Ardisik calisma gunu ---------------------------------------------
    k7 = sk["azami_ardisik_calisma_gunu"]
    if k7["aktif"]:
        for sicil, vs in vardiyalar.items():
            gunler = sorted(set(v["gun"] for v in vs))
            seri = 1
            for a, b in zip(gunler, gunler[1:]):
                seri = seri + 1 if (b - a).days == 1 else 1
                if seri > k7["deger"]:
                    ekle("V_ARDISIK", sicil, b,
                         "%d gun arka arkaya calisma (azami %d)" % (seri, k7["deger"]))
    return ih


def adalet_olc(kayitlar, kurallar):
    """IHLAL DEGIL OLCUM. Pencere: takvim ayi (Mustafa karari, 14 Eylul)."""
    disi = set(kurallar["calisma_disi_kodlar"]["tam_gun_yok"])
    gece_esik = int(kurallar["zaman"]["gece_vardiyasi_esigi"].split(":")[0])
    ay = defaultdict(lambda: defaultdict(lambda: Counter()))
    for k in kayitlar:
        a = k["gun"].strftime("%Y-%m")
        m = ay[a][k["sicil"]]
        if k["tur"] == "VARDIYA":
            m["vardiya"] += 1
            m["saat"] += k["brut_saat"]
            if k["gun"].weekday() >= 5:
                m["hafta_sonu"] += 1
            if k["bitis"] and (k["bitis"].hour >= gece_esik or k["bitis"].day != k["gun"].day):
                m["gece"] += 1
        elif k["ham_deger"] in ("OFF", "G-OFF"):
            m["off"] += 1
    return ay


def main():
    if not os.path.exists(PLAN):
        print("Kanonik plan yok. Once calistir:  py donusturucu.py")
        return
    kurallar = json.load(open(KURAL, encoding="utf-8"))
    kayitlar = plani_oku(PLAN)

    yaz("=" * 74)
    yaz("BAGIMSIZ DOGRULAYICI - kurallar surum %s" % kurallar["surum"])
    yaz("=" * 74)
    yaz("Kayit: %d | calisan: %d" % (len(kayitlar), len(set(k["sicil"] for k in kayitlar))))
    mola = kurallar["mola"]
    yaz("Mola varsayimi: vardiya basina -%.1f saat (%s)"
        % (mola["varsayilan_dusum_saat"], "ucretli" if mola["ucretli_mi"] else "ucretsiz"))
    yaz("UYARI: Plan dosyalarinda mola bilgisi YOK. Net saatler bu varsayima dayanir.")
    yaz("")

    # --- VERI TAMLIGI KONTROLU -------------------------------------------
    # Eksik veriyle yapilan denetim TEHLIKELIDIR: toplamlara dayanan kurallar
    # (haftalik saat, adalet) eksik gunler yuzunden OLDUGUNDAN AZ gorunur.
    # Dogrulayici kendi girdisinin ne kadar tam oldugunu bilmek zorunda.
    gunler = sorted(set(k["gun"] for k in kayitlar))
    donem = (gunler[-1] - gunler[0]).days + 1 if gunler else 0
    kisi_gun = defaultdict(set)
    for k in kayitlar:
        kisi_gun[k["sicil"]].add(k["gun"])
    kapsama = [len(v) for v in kisi_gun.values()]
    ort = sum(kapsama) / len(kapsama) if kapsama else 0
    tam = sum(1 for n in kapsama if n >= donem * 0.6)

    yaz("-" * 74)
    yaz("VERI TAMLIGI")
    yaz("-" * 74)
    yaz("  Donem: %d gun | kisi basina ortalama kayit: %.1f gun (%%%.0f)"
        % (donem, ort, 100 * ort / donem if donem else 0))
    yaz("  Doneminin %%60'indan fazlasi kayitli olan kisi: %d / %d"
        % (tam, len(kapsama)))
    if ort < donem * 0.6:
        yaz("")
        yaz("  !! UYARI: Veri KISMI. Sonuclari soyle oku:")
        yaz("     - V03 (dinlenme) ve V_ARDISIK yerel kontroldur; eksik gun")
        yaz("       bunlari GIZLER, uydurmaz. Bulunanlar gercektir, ALT SINIRDIR.")
        yaz("     - V04_HAFTALIK ve ADALET toplamlara dayanir; eksik gun")
        yaz("       toplamlari DUSURUR. Bulunanlar yine alt sinirdir ama")
        yaz("       ADALET olcumleri GUVENILIR DEGILDIR (0 saat = veri yok).")
        yaz("     Tum plan dosyalarini 06-veri/ham/plan altina koyup tekrar calistir.")
    yaz("")

    ihlaller = dogrula(kayitlar, kurallar)

    yaz("-" * 74)
    if not ihlaller:
        yaz("IHLAL YOK - plan kurallara uygun.")
    else:
        yaz("TOPLAM %d IHLAL" % len(ihlaller))
        yaz("-" * 74)
        ozet = Counter(i["kural"] for i in ihlaller)
        kisi = defaultdict(set)
        for i in ihlaller:
            kisi[i["kural"]].add(i["sicil"])
        yaz("%-16s %8s %8s" % ("KURAL", "VAKA", "KISI"))
        for k, n in ozet.most_common():
            yaz("%-16s %8d %8d" % (k, n, len(kisi[k])))
        yaz("")
        yaz("Ilk 15 ornek:")
        for i in ihlaller[:15]:
            yaz("  [%s] sicil %s  %s" % (i["kural"], i["sicil"], i["mesaj"]))

    # --- adalet ---
    yaz("")
    yaz("-" * 74)
    yaz("ADALET OLCUMU (ihlal degil) - pencere: takvim ayi")
    yaz("-" * 74)
    ay = adalet_olc(kayitlar, kurallar)
    esik = kurallar["adalet"]["uyari_esigi_std_sapma"]
    for a in sorted(ay):
        kisiler = ay[a]
        if len(kisiler) < 3:
            continue
        yaz("")
        yaz("  %s  (%d kisi)" % (a, len(kisiler)))
        for olcu in ("off", "hafta_sonu", "gece", "saat"):
            d = [k[olcu] for k in kisiler.values()]
            if not any(d):
                continue
            ort = statistics.mean(d)
            ss = statistics.pstdev(d)
            uc = [s for s, k in kisiler.items() if ss > 0 and abs(k[olcu] - ort) > esik * ss]
            yaz("    %-11s ort=%5.1f  min=%4.1f  max=%5.1f  std=%4.2f  | %d kisi esik disi"
                % (olcu, ort, min(d), max(d), ss, len(uc)))

    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, "ihlaller.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["kural", "agirlik", "sicil", "gun", "mesaj"],
                           delimiter=";")
        w.writeheader()
        w.writerows(ihlaller)
    with open(os.path.join(CIKTI, "dogrulama.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rapor))
    print("\nYazildi: %s" % os.path.normpath(os.path.join(CIKTI, "ihlaller.csv")))


if __name__ == "__main__":
    main()
