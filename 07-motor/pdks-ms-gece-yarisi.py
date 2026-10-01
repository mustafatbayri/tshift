# -*- coding: utf-8 -*-
r"""
PDKS: "MS" alani plan mi, takvim mi?  Gece yarisini asan vardiya hangi gune
yaziliyor?  (K-47'nin acik sorusu -- 1 Ekim 2026)

NE YAPAR
  Verilen klasorlerdeki pdks_*.csv dosyalarini (UTF-8 BOM, ';' ayracli) okur,
  ayni (SID, mesaitarih) satirini en SON ihracat kazanacak sekilde tekillestirir
  ve YALNIZ sayi yazar. Ihracatlar gunluk/haftalik/aylik ust uste bindigi icin
  ayni gunun "gunden once" ve "gunden sonra" halleri karsilastirilabiliyor;
  MS'in plan mi yoksa sonradan degisen bir takvim mi oldugu buradan anlasilir.

NE YAPMAZ
  Isim, sicil, SID, firma adi, bolum adi YAZMAZ. Firmalar F1..F7 diye etiketlenir.
  Hicbir dosyayi kopyalamaz.

CALISTIRMA (PowerShell)
  cd C:\Users\PC\Desktop\Tshift\07-motor
  py pdks-ms-gece-yarisi.py "C:\...\pdks\2026-07" "C:\...\pdks\2026-08" "C:\...\pdks\2026-09"
  Klasor verilmezse ..\06-veri\ham altinda arar.
CIKTI
  ekrana + ..\06-veri\pdks-ms-gece-yarisi-raporu.txt (06-veri git'e girmez)

BULGULARIN YORUMU: 00-DEVIR/07-GERCEK-VERI-BULGULARI.md  bolum 7
"""
import csv
import glob
import io
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

BURASI = os.path.dirname(os.path.abspath(__file__))
VARSAYILAN = os.path.join(BURASI, "..", "06-veri", "ham")
RAPOR = os.path.join(BURASI, "..", "06-veri", "pdks-ms-gece-yarisi-raporu.txt")
G = "Giri\u015f"
C = "\u00c7\u0131k\u0131\u015f"
AC = "Mesai A\u00e7\u0131klama"
IZ = "\u0130zin A\u00e7\u0131klama"
RMA = "RM A\u00e7\u0131klama"
GUN = "PSCPCCP"  # Pzt Sal Car Per Cum Cmt Paz
satirlar = []


def yaz(s=""):
    satirlar.append(str(s))
    print(s)


def ihracat_zamani(yol):
    m = re.search(r"pdks_(\d{8})_(\d{4})", os.path.basename(yol))
    if not m:
        return datetime.fromtimestamp(os.path.getmtime(yol))
    return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")


def tarih(s):
    return datetime.strptime(s.strip(), "%d-%m-%Y")


def dk(s):
    s = (s or "").strip()
    if not s:
        return None
    p = s.split(":")
    try:
        return int(p[0]) * 60 + int(p[1])
    except (ValueError, IndexError):
        return None


def ss(m):
    return "--:--" if m is None else "%02d:%02d" % (m // 60, m % 60)


def main(klasorler):
    dosyalar = []
    for k in klasorler:
        dosyalar += glob.glob(os.path.join(k, "**", "pdks_*.csv"), recursive=True)
    dosyalar = sorted(set(dosyalar))
    if not dosyalar:
        yaz("pdks_*.csv bulunamadi: %s" % klasorler)
        return 1
    gecmis = defaultdict(list)  # (sid, tarih) -> [(ihracat, row)] ihracat sirali
    ham_satir = 0
    for yol in dosyalar:
        iz = ihracat_zamani(yol)
        with open(yol, "r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f, delimiter=";"):
                ham_satir += 1
                gecmis[(row["SID"].strip(), row["mesaitarih"].strip())].append((iz, row))
    for v in gecmis.values():
        v.sort(key=lambda x: x[0])
    son = {k: v[-1] for k, v in gecmis.items()}
    kisiler = set(k[0] for k in son)
    gunler = sorted(set(tarih(k[1]) for k in son))
    firma_say = Counter(row["Firma"].strip() for iz, row in son.values())
    etiket = {f: "F%d" % (i + 1) for i, (f, n) in enumerate(firma_say.most_common())}

    yaz("PDKS -- MS ALANI VE GECE YARISI KONTROLU (yalniz sayilar)")
    yaz("dosya %d  ham satir %d  tekil (kisi,gun) satir %d  kisi %d  gun %s .. %s"
        % (len(dosyalar), ham_satir, len(son), len(kisiler),
           gunler[0].strftime("%d-%m-%Y"), gunler[-1].strftime("%d-%m-%Y")))

    yaz("\nA. MS x haftanin gunu (Pzt..Paz):")
    ct = Counter((row["MS"].strip(), tarih(t).weekday()) for (sid, t), (iz, row) in son.items())
    for ms in sorted(set(k[0] for k in ct)):
        yaz("   MS %-6s %s" % (ms, [ct[(ms, d)] for d in range(7)]))

    yaz("\nB. MS x Mesai Aciklama (ilk 8):")
    ct = Counter((row["MS"].strip(), row[AC].strip()[:14]) for iz, row in son.values())
    for k, v in ct.most_common(8):
        yaz("   %-8s %-16s %d" % (k[0], k[1], v))

    yaz("\nC. MS plan mi? Ayni gun icin gunden ONCE alinmis ihracattaki MS -> gunden SONRA alinmis son ihracattaki MS")
    for ad, hs in (("hafta sonu", True), ("hafta ici", False)):
        gecis = Counter()
        kartli = Counter()
        for (sid, t), liste in gecmis.items():
            if (tarih(t).weekday() >= 5) != hs:
                continue
            once = [x for x in liste if x[0].date() < tarih(t).date()]
            sonra = [x for x in liste if x[0].date() > tarih(t).date()]
            if not once or not sonra:
                continue
            o, s = once[-1][1]["MS"].strip(), sonra[-1][1]["MS"].strip()
            gecis[(o, s)] += 1
            if dk(sonra[-1][1][G]) is not None:
                kartli[(o, s)] += 1
        yaz("   %s:" % ad)
        for k, v in sorted(gecis.items()):
            yaz("      once %-6s sonra %-6s : %6d satir, kart kaydi olan %d" % (k[0], k[1], v, kartli[k]))

    yaz("\nD. Giris/Cikis dolulugu:")
    d = Counter()
    for iz, row in son.values():
        g, c = dk(row[G]), dk(row[C])
        d["ikisi dolu" if g is not None and c is not None else
          "yalniz giris" if g is not None else
          "yalniz cikis" if c is not None else "ikisi bos"] += 1
    for k, v in d.most_common():
        yaz("   %-14s %d" % (k, v))

    tam = []
    for (sid, t), (iz, row) in son.items():
        g, c = dk(row[G]), dk(row[C])
        if g is None or c is None:
            continue
        tam.append((row["MS"].strip(), g, c, dk(row["NM"]) or 0, dk(row["EM"]) or 0,
                    dk(row["FM"]) or 0, tarih(t).weekday()))

    yaz("\nE. Cikis < Giris (gece yarisini TEK satirda asan kayit), MS'e gore:")
    cg = Counter(("cikis<giris" if c < g else "cikis>=giris", ms) for ms, g, c, *_ in tam)
    for k, v in sorted(cg.items()):
        yaz("   %-13s MS %-6s %d" % (k[0], k[1], v))
    yaz("   en sik 10 (giris saati -> cikis saati):")
    cift = Counter((g // 60, c // 60) for ms, g, c, *_ in tam if c < g)
    for (gh, ch), n in cift.most_common(10):
        yaz("      %02d:xx -> %02d:xx  %d" % (gh, ch, n))

    yaz("\nF. Sure (cikis - giris; gece yarisini asanda +24 saat), saat dilimi: satir")
    sd = defaultdict(Counter)
    for ms, g, c, *_ in tam:
        s = (c - g) if c >= g else (c + 1440 - g)
        sd[ms][s // 60] += 1
    for ms in sorted(sd):
        yaz("   MS %s: %s" % (ms, sorted(sd[ms].items())))

    yaz("\nG. Giris saati dagilimi (00..23), MS'e gore:")
    gs = defaultdict(Counter)
    for ms, g, c, *_ in tam:
        gs[ms][g // 60] += 1
    for ms in sorted(gs):
        yaz("   MS %s: %s" % (ms, [gs[ms][h] for h in range(24)]))

    yaz("\nH. Giris 00:00-01:59 olan satirlar (supheli: gece vardiyasi sonrasi cift kart?):")
    n = 0
    cs = Counter()
    onc = Counter()
    for (sid, t), (iz, row) in son.items():
        g, c = dk(row[G]), dk(row[C])
        if g is None or g >= 120:
            continue
        n += 1
        if c is not None:
            cs[c // 60] += 1
        o = son.get((sid, (tarih(t) - timedelta(days=1)).strftime("%d-%m-%Y")))
        if o is None:
            onc["onceki gun satiri yok"] += 1
            continue
        og, oc = dk(o[1][G]), dk(o[1][C])
        if og is None:
            onc["onceki gun giris bos"] += 1
        elif og < 120:
            onc["onceki gun de 00-02 girisli"] += 1
        elif oc is not None and oc < og:
            onc["onceki gun aksam girisli, cikis<giris"] += 1
        else:
            onc["onceki gun diger"] += 1
    yaz("   satir %d; cikis saati dilimi: %s" % (n, sorted(cs.items())))
    for k, v in onc.most_common():
        yaz("   %-42s %d" % (k, v))

    yaz("\nI. PDKS'in saat kovalari (NM normal / EM eksik / FM fazla), ortalama saat:")
    for ad, sec in (("cikis<giris, MS 10:00 (aksam/gece vardiyasi)", lambda ms, g, c: c < g and ms == "10:00"),
                    ("08-10 arasi giren gunduz satirlari, MS 10:00", lambda ms, g, c: c >= g and ms == "10:00" and 480 <= g < 600)):
        a = [0, 0.0, 0.0, 0.0]
        for ms, g, c, nm, em, fm, wd in tam:
            if sec(ms, g, c):
                a[0] += 1
                a[1] += nm
                a[2] += em
                a[3] += fm
        if a[0]:
            yaz("   %-48s n=%5d  NM %.2f  EM %.2f  FM %.2f" % (ad, a[0], a[1] / 60 / a[0], a[2] / 60 / a[0], a[3] / 60 / a[0]))

    yaz("\nJ. Kart kaydi olan satir, haftanin gunune gore (Pzt..Paz), MS'e gore:")
    hg = defaultdict(Counter)
    for (sid, t), (iz, row) in son.items():
        if dk(row[G]) is not None:
            hg[row["MS"].strip()][tarih(t).weekday()] += 1
    for ms in sorted(hg):
        yaz("   MS %s: %s" % (ms, [hg[ms][d] for d in range(7)]))

    yaz("\nK. Izin aciklamasi (>= 20 satir) ve resmi tatil isareti:")
    izin = Counter(row[IZ].strip() for iz, row in son.values())
    for k, v in izin.most_common(20):
        if v >= 20:
            yaz("   %-32s %d" % (k.replace("#Z_#", "").replace("#__#", "<izin yok>")[:32], v))
    rm = Counter(row[RMA].strip() for iz, row in son.values())
    yaz("   RM aciklama: %s" % [(k or "<bos>", v) for k, v in rm.most_common(5)])

    yaz("\nL. Firmalar (etiket, satir, kisi, kart kaydi olan satir):")
    for f, n in firma_say.most_common():
        kisi = set()
        kart = 0
        for (sid, t), (iz, row) in son.items():
            if row["Firma"].strip() != f:
                continue
            kisi.add(sid)
            if dk(row[G]) is not None:
                kart += 1
        yaz("   %s satir %6d kisi %4d kart %6d" % (etiket[f], n, len(kisi), kart))

    try:
        with io.open(RAPOR, "w", encoding="utf-8") as f:
            f.write("\n".join(satirlar) + "\n")
        yaz("\nRapor yazildi: %s" % os.path.normpath(RAPOR))
    except OSError as e:
        yaz("\nRapor yazilamadi (%s); ekran ciktisi yeterli." % e)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or [VARSAYILAN]))
