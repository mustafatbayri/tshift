# -*- coding: utf-8 -*-
"""E. Eksik mutant avi -- URUN KODUNA DOKUNMADAN: 09-motor GECICI BIR KOPYAYA alinir
(deneme/mut_kopya/), mutasyon kopyada uygulanir, test_rotasyon_yonu.py kopyada kosulur,
kopya sonda silinir. `mutasyon_kostur.py` CALISTIRILMAZ.
Kullanim: python3 d5_mutasyon.py  -> d5_mutasyon.out"""
import os
import shutil
import subprocess
import sys

from ortak import MOTOR

BURASI = os.path.dirname(os.path.abspath(__file__))
KOPYA = os.path.join(BURASI, "mut_kopya")

# (ad, dosya, eski, yeni, beklenti)
MUTANTLAR = [
    ("M1 motor: yuvarlama round() -- tam ,5'te asagi (2,5 -> 2; Python bankaci yuvarlamasi)", "cozucu/model.py",
     "                    hy = int(h + 0.5)\n", "                    hy = int(round(h))\n", "ölmeli (0,5 yukari)"),
    ("M1b motor: pazartesi teriminde de round()", "cozucu/model.py",
     "                        hy = int(rotasyon_geri_saat(bas_onceki, t_[\"bas\"], yon) + 0.5)\n",
     "                        hy = int(round(rotasyon_geri_saat(bas_onceki, t_[\"bas\"], yon)))\n", "ölmeli"),
    ("M2 motor: yuvarlama hep yukari (0,25 -> 1; 9,25 -> 10)", "cozucu/model.py",
     "                    hy = int(h + 0.5)\n", "                    hy = int(h) + (1 if h > int(h) else 0)\n", "ölmeli (0,25 -> 0)"),
    ("M3 motor: gun 0 donmusken de pazartesi terimi yazilsin (K-54 ihlali)", "cozucu/model.py",
     "            if 0 in self.gunler and 0 not in self.donmus:\n", "            if 0 in self.gunler:\n", "ölmeli"),
    ("M4 motor: gun -1'de birden cok kayit -> SON baslangic (max)", "cozucu/model.py",
     "                    bas_onceki = min(onceki)     # ayni gunde birden cok kayit: ilk baslangic\n",
     "                    bas_onceki = max(onceki)     # MUTANT\n", "ölmeli (ilk baslangic)"),
    ("M5 dogrulayici: gun -1'de birden cok kayit -> max", "dogrulayici/kurallar.py",
     "            bas[-1] = min(onceki)\n", "            bas[-1] = max(onceki)\n", "ölmeli"),
    ("M6 dogrulayici: ayni gunde birden cok atama -> SON baslangic (max)", "dogrulayici/kurallar.py",
     "            bas[d] = min(bas[d], float(a[\"bas\"])) if d in bas else float(a[\"bas\"])\n",
     "            bas[d] = max(bas[d], float(a[\"bas\"])) if d in bas else float(a[\"bas\"])\n", "ölmeli"),
    ("M7 metrik (coz.py): ayni gunde birden cok atama -> max", "cozucu/coz.py",
     "        g[d] = min(g[d], float(a[\"bas\"])) if d in g else float(a[\"bas\"])\n",
     "        g[d] = max(g[d], float(a[\"bas\"])) if d in g else float(a[\"bas\"])\n", "ölmeli"),
    ("M8 metrik (coz.py): gun -1'de birden cok kayit -> max", "cozucu/coz.py",
     "            bas.setdefault(c[\"id\"], {})[-1] = min(onceki)\n", "            bas.setdefault(c[\"id\"], {})[-1] = max(onceki)\n", "ölmeli"),
    ("M9 motor: g alani 0..11 (12 saatlik geri sigmaz)", "cozucu/model.py",
     "                        g = self.m.NewIntVar(0, 12, \"ro_%s_%d\" % (c[\"id\"], d))\n",
     "                        g = self.m.NewIntVar(0, 11, \"ro_%s_%d\" % (c[\"id\"], d))\n", "ölmeli (11,75 -> 12)"),
    ("M10 motor: donmus->serbest cifti de atlansin (K-54 yanlis)", "cozucu/model.py",
     "                if d in self.donmus and d + 1 in self.donmus:\n", "                if d in self.donmus or d + 1 in self.donmus:\n", "ölmeli"),
    ("M11 metrik (coz.py): donmus satirlar sayilmasin", "cozucu/coz.py",
     "    for a in atamalar:\n        g = bas.setdefault(a[\"calisan\"], {})\n",
     "    for a in atamalar:\n        if a.get(\"donmus\"):\n            continue\n        g = bas.setdefault(a[\"calisan\"], {})\n", "ölmeli"),
    ("M13 motor: sinir fark <= -12 yerine < -12 (tam -12 geri sayilir)", "cozucu/model.py",
     "    elif fark <= -12.0:\n        fark += 24.0\n    if yon == \"geri\":\n        fark = -fark\n    return -fark if fark < 0 else 0.0\n\n\ndef rotasyon_yonu(",
     "    elif fark < -12.0:\n        fark += 24.0\n    if yon == \"geri\":\n        fark = -fark\n    return -fark if fark < 0 else 0.0\n\n\ndef rotasyon_yonu(", "ölmeli"),
    ("M14 motor: sinir fark > 12 yerine >= 12 (tam +12 geri sayilir)", "cozucu/model.py",
     "    if fark > 12.0:\n        fark -= 24.0\n    elif fark <= -12.0:\n        fark += 24.0\n    if yon == \"geri\":\n        fark = -fark\n    return -fark if fark < 0 else 0.0\n\n\ndef rotasyon_yonu(",
     "    if fark >= 12.0:\n        fark -= 24.0\n    elif fark <= -12.0:\n        fark += 24.0\n    if yon == \"geri\":\n        fark = -fark\n    return -fark if fark < 0 else 0.0\n\n\ndef rotasyon_yonu(", "ölmeli"),
    ("M18 dogrulayici: 0,5 saatten kucuk geri satir yazilmasin", "dogrulayici/kurallar.py",
     "            h = _rotasyon_geri_saat(bas[d], bas[d + 1], yon)\n            if h > 0:\n",
     "            h = _rotasyon_geri_saat(bas[d], bas[d + 1], yon)\n            if h >= 0.5:\n", "ölmeli (0,25 satiri)"),
    ("M19 motor: 1 saatlik geri cift kisit yazmasin (hy > 1)", "cozucu/model.py",
     "                    hy = int(h + 0.5)\n                    if hy > 0:\n", "                    hy = int(h + 0.5)\n                    if hy > 1:\n", "ölmeli"),
    ("M20 metrik (coz.py): yalniz AKTIF kisinin satirlari sayilsin (aktarilan pasif kisi satiri dussun)", "cozucu/coz.py",
     "    for a in atamalar:\n        g = bas.setdefault(a[\"calisan\"], {})\n",
     "    aktif = {c[\"id\"] for c in kuruldu.calisanlar}\n    for a in atamalar:\n        if a[\"calisan\"] not in aktif:\n            continue\n        g = bas.setdefault(a[\"calisan\"], {})\n", "ölmeli?"),
    ("M21 motor: yon notu dusulmesin (sessiz ileri)", "cozucu/model.py",
     "        if notlar is not None:\n            notlar.append(\"VARDIYA_ROTASYON_YONU: yon '%s' taninmadi, 'ileri' uygulandi\" % yon)\n",
     "        pass\n", "ölmeli"),
    ("M22 dogrulayici: olculen kesin yerine 1 ondalik", "dogrulayici/kurallar.py",
     "                                    olculen=round(h, 2), gereken=0,\n", "                                    olculen=round(h, 1), gereken=0,\n", "ölmeli"),
]


def kopyala():
    if os.path.exists(KOPYA):
        shutil.rmtree(KOPYA)
    shutil.copytree(MOTOR, KOPYA, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))


def kostur():
    p = subprocess.run([sys.executable, "-m", "pytest", "testler/test_rotasyon_yonu.py", "-q", "-p", "no:cacheprovider", "-x"],
                       cwd=KOPYA, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=600)
    son = [s for s in p.stdout.strip().splitlines() if s.strip()]
    return p.returncode, (son[-1] if son else p.stderr[-300:])


def main():
    kopyala()
    rc, ozet = kostur()
    print("temiz kopya: rc=%d %s" % (rc, ozet))
    assert rc == 0, "temiz kopya yesil degil"
    sonuc = []
    for ad, dosya, eski, yeni, beklenti in MUTANTLAR:
        yol = os.path.join(KOPYA, dosya)
        metin = open(yol, encoding="utf-8").read()
        if metin.count(eski) == 0:
            print("%-90s | CAPA BULUNAMADI" % ad)
            sonuc.append((ad, "capa yok"))
            continue
        open(yol, "w", encoding="utf-8").write(metin.replace(eski, yeni, 1))
        rc, ozet = kostur()
        durum = "OLDU" if rc != 0 else "YASIYOR"
        print("%-90s | %-8s | beklenti: %-22s | %s" % (ad, durum, beklenti, ozet[:70]))
        sonuc.append((ad, durum))
        open(yol, "w", encoding="utf-8").write(metin)          # geri al
    rc, ozet = kostur()
    print("geri alinmis kopya: rc=%d %s" % (rc, ozet))
    shutil.rmtree(KOPYA)
    print("\nYASAYAN: %d / %d" % (len([s for s in sonuc if s[1] == "YASIYOR"]), len(sonuc)))
    for ad, d in sonuc:
        if d == "YASIYOR":
            print("  -", ad)


if __name__ == "__main__":
    main()
