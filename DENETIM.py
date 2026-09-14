# -*- coding: utf-8 -*-
"""
DEVIR PAKETI DENETIMI

NE YAPAR
  00-BURADAN-BASLA.md #5'teki "guncelleme ritueli"nin 5. maddesini -- yani
  elle yapilan denetimi -- otomatik hale getirir. Yedi kontrol:

    1. Test adlari    Dokumanda gecen her test adi, koddaki DisplayName ile
                      BIREBIR eslesiyor mu. (Kisaltilmis ad tam metin
                      aramasinda bulunamaz -- 14 Eylul D-3 hatasi.)
    2. Test sayisi    "39/39" gibi iddialar koddaki gercek test sayisini
                      tutuyor mu. (14 Eylul D-2 hatasi.)
    3. Dosya yollari  Dokumanlarin isaret ettigi yollar gercekten var mi.
    4. Degismez sayisi 02-DEGISMEZLER.md ozet tablosu, kendi satirlarini
                      tutuyor mu.
    5. Gunluk adlari  oturumlar/ altindaki dosyalar YYYY-AA-GG-<is>.md
                      kurallina uyuyor mu.
    6. Gunluk tazeligi En yeni oturum gunlugu, DEGISIM-GUNLUGU.md'deki en
                      yeni tarihten yeniyse gunluge satir eklenmemis olabilir.
    7. Commit durumu  00-DEVIR/ altinda commit edilmemis degisiklik var mi.
                      ("Yazdim != gonderdim != commit ettim" -- D-1 hatasi.)

  Ek olarak R7 kontrolu: 00-DEVIR dokuz dosyayi gecerse sadelestirme uyarisi.

NEDEN VAR
  Projenin kendi ilkesi: "asil guvence testlerdir, dokuman degil."
  00-DEVIR/ bu ilkenin disinda kalan tek parcaydi -- tamamen duz yazi ve tek
  denetim yontemi elle okumak. 14 Eylul denetiminde bulunan dort sorunun
  dordu de bu betikle yakalanabilirdi.

BU NE DEGILDIR
  * Urunun dogrulayicisi degildir.
  * Icerigin DOGRU oldugunu soylemez -- yalniz dokumanlarin birbiriyle ve
    kodla TUTARLI oldugunu soyler. Tutarli bir yanlis yine yakalanmaz.

CALISTIRMA
  cd C:\\Users\\PC\\Desktop\\Tshift
  py DENETIM.py

CIKIS KODU
  0 = hata yok (uyari olabilir)  |  1 = en az bir HATA
"""

import os
import re
import sys
import glob
import subprocess
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.abspath(__file__))
DEVIR = os.path.join(KOK, "00-DEVIR")
TESTLER = os.path.join(KOK, "04-kod", "backend", "tests")

UZANTILAR = (".md", ".cs", ".py", ".json", ".sql", ".ps1", ".ts", ".tsx",
             ".html", ".yml", ".yaml", ".csv", ".docx", ".pdf", ".slnx",
             ".props", ".http")

# Yol kontrolunde atlanacaklar: uretilen klasorler ve genel kalip adlari.
YOL_ATLA = ("bin/", "obj/", "node_modules/", ".next/", "dist/")

# TARIHSEL dosyalar: append-only, yeniden yazilmaz (00-BURADAN-BASLA #5b).
# Icindeki sayilar o gunun dogrusudur; bugunku sayiyla karsilastirilmaz.
# Test adi sorunlari burada HATA degil UYARI uretir -- duzeltilemez, cunku
# bu dosyalar tanim geregi degistirilmez.
TARIHSEL = ("oturumlar", "DEGISIM-GUNLUGU.md")


def tarihsel_mi(yol):
    n = yol.replace("\\", "/")
    return any(("/%s/" % t) in n or n.endswith(t) for t in TARIHSEL)

hatalar = []
uyarilar = []


def hata(baslik, ayrinti=""):
    hatalar.append((baslik, ayrinti))


def uyari(baslik, ayrinti=""):
    uyarilar.append((baslik, ayrinti))


def baslik_yaz(s):
    print("\n" + s)
    print("-" * len(s))


# ----------------------------------------------------------------------
# Toplama
# ----------------------------------------------------------------------

def dokumanlar():
    """Denetlenecek markdown dosyalari: 00-DEVIR/ ve depo kokundekiler."""
    yollar = sorted(glob.glob(os.path.join(DEVIR, "*.md")))
    yollar += sorted(glob.glob(os.path.join(DEVIR, "oturumlar", "*.md")))
    yollar += sorted(glob.glob(os.path.join(KOK, "*.md")))
    return yollar


def oku(yol):
    with open(yol, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def koddaki_test_adlari():
    """DisplayName = "..." -> {ad: dosya}"""
    bulunan = {}
    if not os.path.isdir(TESTLER):
        return bulunan
    for kok, _, dosyalar in os.walk(TESTLER):
        if "bin" in kok or "obj" in kok:
            continue
        for d in dosyalar:
            if not d.endswith(".cs"):
                continue
            yol = os.path.join(kok, d)
            for ad in re.findall(r'DisplayName\s*=\s*"([^"]+)"', oku(yol)):
                bulunan[ad] = d
    return bulunan


# Bir test adina benzeyen ters tirnakli metin: "M0 - ...", "1 - ...", "K7 - ..."
TEST_ADI_KALIBI = re.compile(r"^(?:[A-Z]{1,2}\d{1,2}|\d{1,2})\s+-\s+\S")


def ters_tirnakli(metin):
    return re.findall(r"`([^`\n]+)`", metin)


# ----------------------------------------------------------------------
# 1. Test adlari
# ----------------------------------------------------------------------

def kontrol_test_adlari(kod_adlari):
    baslik_yaz("1. Test adlari (dokuman <-> DisplayName)")
    if not kod_adlari:
        uyari("Test dosyalari bulunamadi",
              "aranan yol: %s" % TESTLER)
        print("   ATLANDI - test dosyasi bulunamadi")
        return

    gecen = defaultdict(set)          # ad -> {dokuman}
    for yol in dokumanlar():
        ad_dosya = os.path.relpath(yol, KOK)
        for parca in ters_tirnakli(oku(yol)):
            if TEST_ADI_KALIBI.match(parca.strip()):
                gecen[parca.strip()].add(ad_dosya)

    eksik = sorted(a for a in gecen if a not in kod_adlari)
    for ad in eksik:
        yerler = sorted(gecen[ad])
        # Yalniz tarihsel dosyalarda geciyorsa duzeltilemez -> uyari
        bildir = uyari if all(tarihsel_mi(y) for y in yerler) else hata
        adaylar = [k for k in kod_adlari if k.startswith(ad)]
        if adaylar:
            bildir("Kisaltilmis test adi: \"%s\"" % ad,
                   "koddaki tam ad: \"%s\"\n      gectigi yer : %s"
                   % (adaylar[0], ", ".join(yerler)))
        else:
            bildir("Kodda olmayan test adi: \"%s\"" % ad,
                   "gectigi yer: %s" % ", ".join(yerler))

    belgesiz = sorted(a for a in kod_adlari if a not in gecen)
    for ad in belgesiz:
        uyari("Hicbir dokumanda gecmeyen test: \"%s\"" % ad,
              "dosya: %s" % kod_adlari[ad])

    print("   kodda %d test  |  dokumanlarda %d ad  |  eslesmeyen %d  |  belgesiz %d"
          % (len(kod_adlari), len(gecen), len(eksik), len(belgesiz)))


# ----------------------------------------------------------------------
# 2. Test sayisi
# ----------------------------------------------------------------------

def kontrol_test_sayisi(kod_adlari):
    baslik_yaz("2. Test sayisi iddialari")
    gercek = len(kod_adlari)
    if gercek == 0:
        print("   ATLANDI")
        return

    # Yalniz "toplam" iddialari: N/N ciftleri (N >= 20)
    kalip = re.compile(r"(?<![\d/])(\d{2,3})\s*/\s*(\d{2,3})(?![\d/])")
    iddia_sayisi = 0
    for yol in dokumanlar():
        if tarihsel_mi(yol):
            continue              # gecmis kayit: o gunun sayisi dogrudur
        ad_dosya = os.path.relpath(yol, KOK)
        for satir_no, satir in enumerate(oku(yol).splitlines(), 1):
            for a, b in kalip.findall(satir):
                a, b = int(a), int(b)
                if a != b or a < 20:
                    continue          # 39/45 gibi oranlar bu kontrolde degil
                iddia_sayisi += 1
                if a != gercek:
                    hata("Test sayisi tutmuyor: \"%d/%d\"" % (a, b),
                         "%s:%d  |  kodda %d test var" % (ad_dosya, satir_no, gercek))

    print("   kodda %d test  |  denetlenen 'N/N' iddiasi: %d"
          % (gercek, iddia_sayisi))
    dosya_basina = defaultdict(int)
    for ad, d in kod_adlari.items():
        dosya_basina[d] += 1
    for d in sorted(dosya_basina):
        print("      %-28s %2d" % (d, dosya_basina[d]))


# ----------------------------------------------------------------------
# 3. Dosya yollari
# ----------------------------------------------------------------------

def yol_var_mi(aday, dokuman_klasoru, tum_dosyalar):
    aday = aday.rstrip("/")
    for taban in (KOK, dokuman_klasoru, DEVIR):
        if os.path.exists(os.path.join(taban, aday)):
            return True
    if "/" not in aday:
        return aday in tum_dosyalar
    return False


def kontrol_dosya_yollari():
    baslik_yaz("3. Isaret edilen dosya yollari")
    tum_dosyalar = set()
    for kok, klasorler, dosyalar in os.walk(KOK):
        klasorler[:] = [k for k in klasorler
                        if k not in (".git", "node_modules", "bin", "obj", ".next")]
        for d in dosyalar:
            tum_dosyalar.add(d)

    bakilan = 0
    kirik = 0
    for yol in dokumanlar():
        ad_dosya = os.path.relpath(yol, KOK)
        klasor = os.path.dirname(yol)
        for parca in set(ters_tirnakli(oku(yol))):
            p = parca.strip()
            if "\\" in p or "://" in p or " " in p:
                continue
            if "<" in p or ">" in p or "..." in p or "\u2026" in p:
                continue                      # kalip/kisaltma, gercek yol degil
            if p.startswith(".") and "/" not in p:
                continue                      # ".ps1", ".gitignore" gibi tur adlari
            if p in YOL_ATLA:
                continue                      # uretilen klasorler
            if not (p.endswith(UZANTILAR) or p.endswith("/")):
                continue
            bakilan += 1
            if not yol_var_mi(p, klasor, tum_dosyalar):
                kirik += 1
                # Tarihsel dosyada silinmis bir yola atif normaldir: o gun vardi.
                bildir = uyari if tarihsel_mi(yol) else hata
                bildir("Bulunamayan yol: `%s`" % p, "gectigi yer: %s" % ad_dosya)

    print("   denetlenen yol: %d  |  bulunamayan: %d" % (bakilan, kirik))


# ----------------------------------------------------------------------
# 4. Degismez sayisi
# ----------------------------------------------------------------------

def kontrol_degismezler():
    baslik_yaz("4. Degismez ozet tablosu")
    yol = os.path.join(DEVIR, "02-DEGISMEZLER.md")
    if not os.path.exists(yol):
        print("   ATLANDI - 02-DEGISMEZLER.md yok")
        return
    metin = oku(yol)

    satir_kalibi = re.compile(r"^\|\s*\*{0,2}([KYIDG])-(\d+)\*{0,2}\s*\|(.*)$")
    gorulen = {}                       # "K-1" -> bekcili mi
    grup = defaultdict(int)
    for satir in metin.splitlines():
        m = satir_kalibi.match(satir)
        if not m:
            continue
        kimlik = "%s-%s" % (m.group(1), m.group(2))
        if kimlik in gorulen:
            continue                   # ayni degismez birden cok tabloda anilabilir
        gorulen[kimlik] = "\u2705" in m.group(3)
        grup[m.group(1)] += 1
    toplam = len(gorulen)
    bekcili = sum(1 for v in gorulen.values() if v)
    print("   gruplar: " + "  ".join("%s=%d" % (g, grup[g]) for g in sorted(grup)))

    m = re.search(r"\|\s*\*{0,2}TOPLAM\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|"
                  r"\s*\*{0,2}(\d+)\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", metin)
    if not m:
        uyari("02-DEGISMEZLER.md TOPLAM satiri okunamadi")
        print("   sayilan: %d degismez, %d bekcili (TOPLAM satiri okunamadi)"
              % (toplam, bekcili))
        return

    y_toplam, y_bekcili, y_acik = int(m.group(1)), int(m.group(2)), int(m.group(3))
    print("   sayilan: %d degismez, %d bekcili  |  yazili: %d / %d / %d acik"
          % (toplam, bekcili, y_toplam, y_bekcili, y_acik))
    if toplam != y_toplam:
        hata("Degismez sayisi tutmuyor",
             "tabloda %d yaziyor, satir sayisi %d" % (y_toplam, toplam))
    if bekcili != y_bekcili:
        hata("Bekcili degismez sayisi tutmuyor",
             "tabloda %d yaziyor, sayilan %d" % (y_bekcili, bekcili))
    if y_toplam - y_bekcili != y_acik:
        hata("Ozet tablosu kendi icinde tutarsiz",
             "%d - %d = %d, ama acik sutununda %d yaziyor"
             % (y_toplam, y_bekcili, y_toplam - y_bekcili, y_acik))


# ----------------------------------------------------------------------
# 5-6. Oturum gunlukleri
# ----------------------------------------------------------------------

GUNLUK_ADI = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9\-]+\.md$")


def kontrol_gunlukler():
    baslik_yaz("5. Oturum gunlugu adlandirmasi")
    klasor = os.path.join(DEVIR, "oturumlar")
    if not os.path.isdir(klasor):
        print("   ATLANDI - oturumlar/ yok")
        return []
    dosyalar = sorted(os.listdir(klasor))
    for d in dosyalar:
        if not d.endswith(".md"):
            continue
        if not GUNLUK_ADI.match(d):
            hata("Gunluk adlandirma kuralina uymuyor: %s" % d,
                 "beklenen bicim: YYYY-AA-GG-<is-parcasi>.md")
    print("   %d gunluk dosyasi denetlendi" % len(dosyalar))
    return dosyalar


def kontrol_gunluk_tazeligi(gunlukler):
    baslik_yaz("6. Degisim gunlugu tazeligi")
    yol = os.path.join(KOK, "DEGISIM-GUNLUGU.md")
    if not os.path.exists(yol) or not gunlukler:
        print("   ATLANDI")
        return
    tarihler = [d[:10] for d in gunlukler if GUNLUK_ADI.match(d)]
    if not tarihler:
        print("   ATLANDI")
        return
    en_yeni_oturum = max(tarihler)
    gunluk_tarihleri = re.findall(r"(\d{4}-\d{2}-\d{2})", oku(yol))
    en_yeni_gunluk = max(gunluk_tarihleri) if gunluk_tarihleri else "0000-00-00"
    print("   en yeni oturum: %s  |  degisim gunlugunde en yeni: %s"
          % (en_yeni_oturum, en_yeni_gunluk))
    if en_yeni_oturum > en_yeni_gunluk:
        uyari("DEGISIM-GUNLUGU.md geride",
              "%s tarihli oturum var, gunlukte en yeni satir %s"
              % (en_yeni_oturum, en_yeni_gunluk))


# ----------------------------------------------------------------------
# 7. Commit durumu + R7
# ----------------------------------------------------------------------

def kontrol_commit():
    baslik_yaz("7. Commit durumu (yazdim != gonderdim != commit ettim)")
    if not os.path.isdir(os.path.join(KOK, ".git")):
        print("   ATLANDI - git deposu degil")
        return
    try:
        cikti = subprocess.run(["git", "status", "--porcelain"], cwd=KOK,
                               capture_output=True, text=True, timeout=30)
    except Exception as e:                       # git yoksa ya da yavassa
        uyari("git calistirilamadi", str(e))
        print("   ATLANDI - git calistirilamadi")
        return
    if cikti.returncode != 0:
        uyari("git status basarisiz", cikti.stderr.strip()[:200])
        print("   ATLANDI")
        return

    ilgili = []
    for satir in cikti.stdout.splitlines():
        yol = satir[3:].strip().strip('"')
        if yol.startswith(("00-DEVIR/", "08-motor-testleri/", "02-spec/")) \
           or yol in ("DEGISIM-GUNLUGU.md", "RISKLER-VE-ONLEMLER.md",
                      "SURUMLEME.md", "DENETIM.py"):
            ilgili.append(satir)
    if ilgili:
        uyari("Commit edilmemis devir dosyasi var (%d)" % len(ilgili),
              "\n      ".join(ilgili))
    print("   commit bekleyen devir dosyasi: %d" % len(ilgili))


def kontrol_r7():
    baslik_yaz("R7. Devir paketi buyuklugu")
    if not os.path.isdir(DEVIR):
        print("   ATLANDI")
        return
    dosyalar = [d for d in os.listdir(DEVIR) if d.endswith(".md")]
    print("   00-DEVIR kokunde %d dosya" % len(dosyalar))
    if len(dosyalar) > 9:
        uyari("00-DEVIR dokuz dosyayi gecti (%d)" % len(dosyalar),
              "R7 kurali: sadelestirme zamani. Yeni dosya acmadan once sor: "
              "bu, var olan bir dosyanin bolumu olabilir mi?")
    elif len(dosyalar) == 9:
        print("   (R7 esigindesiniz: dokuzuncu dosya. Onuncusu uyari uretir.)")


# ----------------------------------------------------------------------

def main():
    print("=" * 62)
    print("DEVIR PAKETI DENETIMI")
    print("kok: %s" % KOK)
    print("=" * 62)

    kod_adlari = koddaki_test_adlari()
    kontrol_test_adlari(kod_adlari)
    kontrol_test_sayisi(kod_adlari)
    kontrol_dosya_yollari()
    kontrol_degismezler()
    gunlukler = kontrol_gunlukler()
    kontrol_gunluk_tazeligi(gunlukler)
    kontrol_commit()
    kontrol_r7()

    print("\n" + "=" * 62)
    if hatalar:
        print("HATA (%d) - devir 'tamam' denmeden once duzeltilmeli" % len(hatalar))
        for b, a in hatalar:
            print("  * %s" % b)
            if a:
                print("      %s" % a)
    if uyarilar:
        print("\nUYARI (%d) - bakilmali, ama devri durdurmaz" % len(uyarilar))
        for b, a in uyarilar:
            print("  - %s" % b)
            if a:
                print("      %s" % a)
    if not hatalar and not uyarilar:
        print("TEMIZ - butun kontroller gecti.")
    print("=" * 62)
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
