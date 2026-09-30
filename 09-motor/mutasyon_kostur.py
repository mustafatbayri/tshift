# -*- coding: utf-8 -*-
"""
MUTASYON KOSTURUCU -- elle secilmis bozmalar, TEKRARLANABILIR bicimde

NEDEN VAR (30 Eylul)
  Bu oturumda her yeni kural icin bozmalar elle, satir ici bir betikle
  denendi. O yontemin sessiz bir acigi CIKTI:

    Python derlenmis bytecode'u (__pycache__) gecerli sayarken kaynagin
    DEGISIKLIK ZAMANINA (saniye) ve BOYUTUNA bakar. Bir mutasyon AYNI
    UZUNLUKTA bir degisiklikse (`plan_geceler` -> `plan_gunleri`, ikisi de
    12 harf) ve dosya AYNI SANIYEDE geri yazilirsa, mutasyonlu bytecode
    ozgun kaynak icin de gecerli sayilir.

  Olculdu: `_gecmis_eksik` diskte dogruydu ama Python on ikinci
  mutasyonun bytecode'unu calistiriyordu; dogru bir test kirmizi yandi.
  Ters yon de mumkun: bir mutasyon bir oncekinin bytecode'uyla kosup
  sahte "oldu" ya da sahte "yasadi" verebilir.

BU BETIK NE YAPAR
  * her kosudan once __pycache__ silinir ve bytecode HIC yazilmaz
    (PYTHONDONTWRITEBYTECODE=1)
  * ozgun kod BASTA ve SONDA kosulur; ikisi de yesil olmak ZORUNDA --
    yoksa mutasyon sonuclari anlamsizdir ve betik durur
  * her mutasyondan sonra dosya geri yazilir ve md5 ile dogrulanir
  * capa bulunamazsa ATLANDI yazar -- sessizce gecmez

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py mutasyon_kostur.py            -> hepsi
  py mutasyon_kostur.py gecmis     -> adinda "gecmis" gecen gruplar
"""

import hashlib
import io
import os
import shutil
import subprocess
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)


def _md5(yol):
    return hashlib.md5(io.open(yol, "rb").read()).hexdigest()


def _onbellegi_sil():
    for kok in (BURASI, os.path.join(KOK, "08-motor-testleri")):
        for dizin, alt, _ in os.walk(kok):
            for a in list(alt):
                if a in ("__pycache__", ".pytest_cache"):
                    shutil.rmtree(os.path.join(dizin, a), ignore_errors=True)
                    alt.remove(a)


def _kostur(test):
    _onbellegi_sil()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-m", "pytest", test, "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       cwd=BURASI, env=env, capture_output=True, text=True)
    satirlar = [s for s in p.stdout.strip().splitlines() if s.strip()]
    return p.returncode, (satirlar[-1] if satirlar else p.stderr[-200:])


# (grup, dosya, ad, eski, yeni, test)
K = "dogrulayici/kurallar.py"
D = "dogrulayici/denetle.py"
M = "cozucu/model.py"
C = "cozucu/coz.py"

MUTASYONLAR = [
    # ---- nitelik kapsamasi (30 Eylul) -- dogrulayici
    ("nitelik", K, "yalniz tam saate bak (ceyregi atla)",
     "    for t, g, an in _talep_anlari(girdi):\n        if ekip is not None and t.get(\"ekip\") != ekip:",
     "    for t, g, an in _talep_hucreleri(girdi):\n        if ekip is not None and t.get(\"ekip\") != ekip:",
     "testler/test_nitelik_kapsamasi.py"),
    ("nitelik", K, "saat listesini yok say",
     "    saat_kumesi = None if saatler is None else {int(s) for s in saatler}",
     "    saat_kumesi = None",
     "testler/test_nitelik_kapsamasi.py"),
    ("nitelik", K, "satirin yasal bayragini yok say",
     "                kod, tanim, ekip=ekip, gun=gun, saat=an, nitelik=aranan,",
     "                kod, tanim, ekip=ekip, gun=gun, saat=an, nitelik=aranan,\n                yasal=False, kabul_edilebilir=True,",
     "testler/test_nitelik_kapsamasi.py"),
    ("nitelik", K, "ekip kadrosu suzgecini yok say",
     "        if ekip is not None and ekip not in (c.get(\"ekipler\") or []):\n            continue",
     "        if False:\n            continue",
     "testler/test_nitelik_kapsamasi.py"),
    ("nitelik", K, "K-41 geri: molayi dus (sahada say)",
     "        varlik = sum(1 for a in ilgili if zaman.atanmis_mi(a, gun, an))",
     "        varlik = sum(1 for a in ilgili if zaman.sahada_mi(a, gun, an))",
     "testler/test_nitelik_kapsamasi.py"),
    # ---- nitelik kapsamasi -- cozucu (T-62)
    ("nitelik", M, "cozucu: saatler yoksa hic saat denetlenmesin",
     "                saat_kumesi = (None if saatler is None\n                               else {int(x) for x in saatler})",
     "                saat_kumesi = ({-1} if saatler is None\n                               else {int(x) for x in saatler})",
     "testler/test_nitelik_kapsamasi.py"),
    ("nitelik", M, "cozucu: nitelik tasiyan yoksa yine kisit yazilsin",
     "                if not uygun:\n                    self.notlar.append(\n                        \"%s: '%s' niteligini tasiyan uygun calisan yok, \"\n                        \"kisit yazilmadi\" % (kod, aranan))\n                    continue\n",
     "",
     "testler/test_nitelik_kapsamasi.py"),
    # ---- motorun kendi metrigi (T-65)
    ("metrik", C, "int() geri gelsin (kesirli siniri kirp)",
     "                   and a[\"gun\"] * 24 + a[\"bas\"] <= an\n                   < a[\"gun\"] * 24 + a[\"bit\"])",
     "                   and a[\"gun\"] * 24 + int(a[\"bas\"]) <= an\n                   < a[\"gun\"] * 24 + int(a[\"bit\"]))",
     "testler/test_motor_metrigi.py"),
    # ---- gece vardiyasi azami (K-26) -- dogrulayici
    ("gece_azami", K, "brut olc (molayi dusme)",
     "    return brut - mola\n", "    return brut\n",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "butun molalari dus (pencere disi dahil)",
     "    mola = sum(_kesisim(m0, m1, w0, w1)\n               for m0, m1 in zaman.mola_araliklari(atama))",
     "    mola = sum(m1 - m0 for m0, m1 in zaman.mola_araliklari(atama))",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "pencere gun sinirini asmasin (Z-5)",
     "        bit = zaman.mutlak(gun + (1 if pencere_bit <= pencere_bas else 0),\n                           pencere_bit)",
     "        bit = zaman.mutlak(gun, 24.0)",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "istisnayi hic uygulama",
     "            if istisnali_sektor and _gece_onayi_gecerli(c, girdi, gun):\n                continue",
     "            if False:\n                continue",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "yalniz sektore bak",
     "            if istisnali_sektor and _gece_onayi_gecerli(c, girdi, gun):",
     "            if istisnali_sektor:",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "yalniz onaya bak",
     "            if istisnali_sektor and _gece_onayi_gecerli(c, girdi, gun):",
     "            if _gece_onayi_gecerli(c, girdi, gun):",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "sinirda esitlik ihlal (>=)",
     "            if gece > azami + 1e-9:", "            if gece >= azami:",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", K, "suresi gecmis onay gecerli",
     "        return date.fromisoformat(bitis) >= gece", "        return True",
     "testler/test_gece_vardiyasi_azami.py"),
    # ---- gece vardiyasi azami -- cozucu
    ("gece_azami", M, "cozucu: kisit yazilmasin",
     "                    if (c[\"id\"], d, t[\"id\"]) in self.x:\n                        self.m.Add(self.x[(c[\"id\"], d, t[\"id\"])] == 0)\n\n    def _izin(self):",
     "                    pass\n\n    def _izin(self):",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", M, "cozucu: istisna hic uygulanmasin",
     "                if istisnali and _gece_onayi_var(c, self.girdi, d):\n                    continue",
     "                if False:\n                    continue",
     "testler/test_gece_vardiyasi_azami.py"),
    ("gece_azami", M, "cozucu: yalniz onaya bak",
     "                if istisnali and _gece_onayi_var(c, self.girdi, d):",
     "                if _gece_onayi_var(c, self.girdi, d):",
     "testler/test_gece_vardiyasi_azami.py"),
    # ---- firma sinirlari -- dogrulayici
    ("firma", K, "asgari sure: net olc",
     "        bas, bit = zaman.aralik(a)\n        sure = bit - bas\n        if sure < asgari - 1e-9:",
     "        sure = zaman.net_saat(a)\n        if sure < asgari - 1e-9:",
     "testler/test_firma_sinirlari.py"),
    ("firma", K, "asgari sure: esitlik ihlal (<=)",
     "        if sure < asgari - 1e-9:", "        if sure <= asgari:",
     "testler/test_firma_sinirlari.py"),
    ("firma", K, "ardisik gece: calisma gunu say",
     "        geceler = {a[\"gun\"] for a in liste\n                   if _atama_gece_mi(girdi, a, sablonlar)}",
     "        geceler = {a[\"gun\"] for a in liste}",
     "testler/test_firma_sinirlari.py"),
    ("firma", M, "cozucu: gece kisiti yok",
     "                if terim:\n                    self.m.Add(sum(terim) <= azami)",
     "                pass",
     "testler/test_firma_sinirlari.py"),
    ("firma", M, "cozucu: kisa sablon serbest",
     "                    if (c[\"id\"], d, t[\"id\"]) in self.x:\n                        self.m.Add(self.x[(c[\"id\"], d, t[\"id\"])] == 0)\n\n    # ---- kapsama",
     "                    pass\n\n    # ---- kapsama",
     "testler/test_firma_sinirlari.py"),
    # ---- gecmis veri (T-28, K-42) -- dogrulayici
    ("gecmis", K, "gecmis listeye eklenmesin",
     "        liste.extend(_gecmis_kayitlari(girdi, kimlik))", "        pass",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "dinlenme: gecmis-gecmis cifti atlanmasin",
     "            if sonraki.get(\"_gecmis\"):\n                continue                      # gecmis kendi icinde",
     "            if False:\n                continue",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "cakisma: karisik cift de atlansin",
     "                if liste[i].get(\"_gecmis\") and liste[j].get(\"_gecmis\"):\n                    continue\n                ort",
     "                if liste[i].get(\"_gecmis\") or liste[j].get(\"_gecmis\"):\n                    continue\n                ort",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "tatil: gecmisteki pencere atlanmasin",
     "            if bas + pencere - 1 < 0:\n                continue                      # tamamen gecmiste",
     "            if False:\n                continue",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "seri: gecmisteki seri de sayilsin",
     "            if seri and g - 1 >= 0 and seri > en_uzun:",
     "            if seri and seri > en_uzun:",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "gecmis kaydin gece isareti yok sayilsin",
     "        if \"_gece\" in a:\n            return a[\"_gece\"]", "        pass",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "gun>=0 kaydi da gecmis sayilsin",
     "        if gun is None or bas is None or bit is None or gun >= 0:",
     "        if gun is None or bas is None or bit is None:",
     "testler/test_gecmis_veri.py"),
    ("gecmis", K, "bilinen gunler listesi yok sayilsin",
     "    return ({g for g in (c.get(\"gecmis_bilinen_gunler\") or []) if g < 0}\n            | {k[\"gun\"] for k in kayitlar})",
     "    return {k[\"gun\"] for k in kayitlar}",
     "testler/test_gecmis_veri.py"),
    ("gecmis", D, "geri yuruyus bilinen bos gunde durmasin",
     "        elif d in bilinen:\n            return \"guvenli\", None",
     "        elif False:\n            return \"guvenli\", None",
     "testler/test_gecmis_veri.py"),
    ("gecmis", D, "kanitli ihlal de raporlansin",
     "            if k + plan_serisi >= esik:\n                return \"ihlal\", None",
     "            if k + plan_serisi >= esik:\n                return \"belirsiz\", d",
     "testler/test_gecmis_veri.py"),
    ("gecmis", D, "pazartesi bossa da raporlansin",
     "        if (\"VARDIYA_ARASI_DINLENME\" in aktif and 0 in plan_gunleri\n                and -1 not in bilinen):",
     "        if (\"VARDIYA_ARASI_DINLENME\" in aktif\n                and -1 not in bilinen):",
     "testler/test_gecmis_veri.py"),
    ("gecmis", D, "gece raporu pazartesi gece degilse de",
     "                                    _plan_serisi(plan_geceler), esik)",
     "                                    _plan_serisi(plan_gunleri), esik)",
     "testler/test_gecmis_veri.py"),
    # ---- gecmis veri -- cozucu
    ("gecmis", M, "cozucu: pazartesi dinlenme siniri yazilmasin",
     "                        if (d * 24 + t[\"bas\"] - bitis < asgari\n                                and (c[\"id\"], d, t[\"id\"]) in self.x):\n                            self.m.Add(self.x[(c[\"id\"], d, t[\"id\"])] == 0)",
     "                        pass",
     "testler/test_gecmis_veri.py"),
    ("gecmis", M, "cozucu: ardisik gun gecmis penceresi yazilmasin",
     "                plan = range(0, min(HAFTA_GUN, bas + azami + 1))\n                self.m.Add(sabit + sum(self._calisiyor(c[\"id\"], d)\n                                       for d in plan) <= azami)",
     "                pass",
     "testler/test_gecmis_veri.py"),
    ("gecmis", M, "cozucu: ardisik gece gecmis penceresi yazilmasin",
     "                if terim:\n                    self.m.Add(sabit + sum(terim) <= azami)",
     "                pass",
     "testler/test_gecmis_veri.py"),
    ("gecmis", M, "cozucu: gecmis kaydin gece isareti yok sayilsin",
     "    if isaret is not None:\n        return bool(isaret)\n    return _gece_sablonu",
     "    if False:\n        return bool(isaret)\n    return _gece_sablonu",
     "testler/test_gecmis_veri.py"),
    ("gecmis", M, "cozucu: gecmisi HIC okumasin",
     "    cikan = []\n    for k in calisan.get(\"gecmis_vardiyalar\") or []:",
     "    cikan = []\n    for k in []:",
     "testler/test_gecmis_veri.py"),
    ("gecmis", M, "cozucu: gun>=0 kaydi da gecmis sayilsin",
     "        if gun is None or bas is None or bit is None or gun >= 0:\n            continue\n        bas, bit = float(bas), float(bit)",
     "        if gun is None or bas is None or bit is None:\n            continue\n        bas, bit = float(bas), float(bit)",
     "testler/test_gecmis_veri.py"),
]


def main():
    suzgec = sys.argv[1] if len(sys.argv) > 1 else None
    secilen = [m for m in MUTASYONLAR if suzgec is None or suzgec in m[0]]
    testler = sorted({m[5] for m in secilen})

    print("OZGUN KOD (baslangic):")
    for t in testler:
        rc, son = _kostur(t)
        print("  %-42s %s" % (t, son))
        if rc:
            print("\n⚠ OZGUN KOD KIRMIZI -- mutasyon sonuclari anlamsiz olur. DURDU.")
            sys.exit(2)

    yasayan = atlanan = 0
    print("\nMUTASYONLAR:")
    for grup, dosya, ad, eski, yeni, test in secilen:
        yol = os.path.join(BURASI, dosya)
        orijinal = io.open(yol, encoding="utf-8").read()
        once = _md5(yol)
        if orijinal.count(eski) != 1:
            print("  [%-10s] %-46s ATLANDI (capa %d kez)"
                  % (grup, ad, orijinal.count(eski)))
            atlanan += 1
            continue
        try:
            io.open(yol, "w", encoding="utf-8", newline="").write(
                orijinal.replace(eski, yeni))
            rc, son = _kostur(test)
        finally:
            io.open(yol, "w", encoding="utf-8", newline="").write(orijinal)
        assert _md5(yol) == once, "%s geri yazilamadi!" % dosya
        durum = "OLDU" if rc else "*** YASADI ***"
        if not rc:
            yasayan += 1
        print("  [%-10s] %-46s %-14s %s" % (grup, ad, durum, son))

    print("\nOZGUN KOD (bitis):")
    for t in testler:
        rc, son = _kostur(t)
        print("  %-42s %s" % (t, son))
        if rc:
            print("\n⚠ OZGUN KOD SONDA KIRMIZI -- bir dosya geri yazilamamis olabilir.")
            sys.exit(2)
    _onbellegi_sil()

    print("\nOZET: %d mutasyon · yasayan %d · atlanan %d"
          % (len(secilen), yasayan, atlanan))
    sys.exit(1 if (yasayan or atlanan) else 0)


if __name__ == "__main__":
    main()
