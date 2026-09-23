# -*- coding: utf-8 -*-
"""
YOL ON KONTROLU (T-35 sonrasi, 23 Eylul)

NE ISE YARAR
  Dokumanlarda ters tirnak icinde yazilmis dosya yollarini, dosyalari
  Mustafa'ya vermeden ONCE kontrol eder. Kisa yol hatasi bu hafta ALTI kez
  tekrarlandi; her seferinde DENETIM.py yakaladi ve bedeli bir gidis-gelis
  oldu.

NEDEN KENDI KURALINI YAZMIYOR
  Bir kez denendi: kendi yazdigim kural DENETIM'den KATI cikti ve 72 yanlis
  alarm verdi (betik 3 diyordu). Yanlis alarm veren kontrol, olmayan
  kontroldan kotudur (O-7). Bu yuzden burada DENETIM.py'nin KENDI
  fonksiyonlari ice aktariliyor -- ikinci bir dogruluk kaynagi uretilmiyor
  (T-32'nin dersi).

NE YAPMAZ
  git calistirmaz, yani .git/index.lock birakmaz. Yalniz 3. kontrolun
  mantigini kosar; devrin tamami icin yine `py DENETIM.py` gerekir.
"""
import importlib.util, os, sys

KOK = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("denetim", os.path.join(KOK, "DENETIM.py"))
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)

tum_dosyalar = set()
for kok, klasorler, dosyalar in os.walk(KOK):
    klasorler[:] = [k for k in klasorler
                    if k not in (".git", "node_modules", "bin", "obj", ".next")]
    for d in dosyalar:
        tum_dosyalar.add(d)

hedefler = sys.argv[1:] or [os.path.relpath(y, KOK) for y in D.dokumanlar()]
kirik = 0
for rel in hedefler:
    yol = os.path.join(KOK, rel)
    if not os.path.exists(yol):
        continue
    klasor = os.path.dirname(yol)
    for parca in sorted(set(D.ters_tirnakli(D.govde(yol)))):
        p = parca.strip()
        if "\\" in p or "://" in p or " " in p:              continue
        if "<" in p or ">" in p or "..." in p or u"\u2026" in p: continue
        if p.startswith(".") and "/" not in p:                continue
        if p in D.YOL_ATLA or p in D.YOK_AMA_KASITLI:         continue
        if not (p.endswith(D.UZANTILAR) or p.endswith("/")):  continue
        if not D.yol_var_mi(p, klasor, tum_dosyalar):
            print("  KIRIK  %-52s <- %s" % (p, rel)); kirik += 1

print("kirik yol: %d  (DENETIM.py'nin KENDI kuralina gore)" % kirik)
sys.exit(1 if kirik else 0)
