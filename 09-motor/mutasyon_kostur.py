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
    # ---- hafta olcekli kurallar (30 Eylul) -- GECE_POSTASI_DEVRI,
    #      ARDISIK_HAFTA_SONU_LIMIT; dogrulayici, K-42 raporu, cozucu
    ("hafta", K, 'hafta: sifira dogru yuvarla (int)',
     'def _hafta(gun):\n    return gun // 7',
     'def _hafta(gun):\n    return int(gun / 7)',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'geriye seri: bir hafta atla',
     '    while hafta - n in haftalar:',
     '    while hafta - 2 * n in haftalar:',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'devri: sinirda esitlik ihlal (>=)',
     '            if seri > azami:\n                ilk = min(a["gun"] for a in geceler',
     '            if seri >= azami:\n                ilk = min(a["gun"] for a in geceler',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'devri: gece degil calisma haftasi say',
     '        geceler = [a for a in liste if _yasal_gece_postasi_mi(a)]',
     '        geceler = list(liste)',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'devri: gecmis okunmasin',
     '    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):\n        geceler = [a for a in liste',
     '    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):\n        geceler = [a for a in liste',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'hsonu: yalniz cumartesi',
     '    return gun % 7 in (5, 6)',
     '    return gun % 7 == 5',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'hsonu: sinirda esitlik ihlal (>=)',
     '            if seri > azami:\n                ilk = min(a["gun"] for a in hafta_sonlari',
     '            if seri >= azami:\n                ilk = min(a["gun"] for a in hafta_sonlari',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'hsonu: cuma gecesi de say (bitis gunu)',
     '        hafta_sonlari = [a for a in liste if _hafta_sonu_mu(a["gun"])]',
     '        hafta_sonlari = [a for a in liste if _hafta_sonu_mu(a["gun"])\n                         or _hafta_sonu_mu(int(zaman.aralik(a)[1] // 24))]',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'hsonu: gecmis okunmasin',
     '    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):\n        hafta_sonlari = [a for a in liste',
     '    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):\n        hafta_sonlari = [a for a in liste',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: bilinen bos haftada durmasin',
     '        elif bos_mu(hafta):\n            return "guvenli", None',
     '        elif False:\n            return "guvenli", None',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: kanitli ihlal de raporlansin',
     '            if seri >= esik:\n                return "ihlal", None',
     '            if seri >= esik:\n                return "belirsiz", hafta',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: bu hafta gece yoksa da',
     '                _hafta(a["gun"]) == 0 and kurallar._yasal_gece_postasi_mi(a)\n                for a in liste):',
     '                _hafta(a["gun"]) == 0\n                for a in liste):',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: gece haftasinda bir gun bilinse yeter',
     '                lambda h: all(d in bilinen for d in range(7 * h, 7 * h + 7)),',
     '                lambda h: any(d in bilinen for d in range(7 * h, 7 * h + 7)),',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: hafta sonunun tek gunu bilinse yeter',
     '                lambda h: 7 * h + 5 in bilinen and 7 * h + 6 in bilinen,',
     '                lambda h: 7 * h + 5 in bilinen or 7 * h + 6 in bilinen,',
     'testler/test_hafta_kurallari.py'),
    ("hafta", D, 'rapor: bu hafta sonu bossa da',
     '                _hafta(a["gun"]) == 0 and kurallar._hafta_sonu_mu(a["gun"])\n                for a in liste):',
     '                _hafta(a["gun"]) == 0\n                for a in liste):',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: kisit yazilmasin',
     '                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)\n\n    def _ardisik_hafta_sonu(self):',
     '                        pass\n\n    def _ardisik_hafta_sonu(self):',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: sinirda (<=)',
     '            if seri < azami:\n                continue\n            for d in self.gunler:',
     '            if seri <= azami:\n                continue\n            for d in self.gunler:',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: hafta sifira yuvarlansin',
     '            gece_haftalari = {g // 7 for g, b0, b1, _ in _gecmis_kayitlari(c)',
     '            gece_haftalari = {int(g / 7) for g, b0, b1, _ in _gecmis_kayitlari(c)',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: her gecmis kayit gece sayilsin',
     '                              if _yasal_gece_postasi(b0, b1)}\n            seri = 0',
     '                              if True}\n            seri = 0',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu hsonu: kisit yazilmasin',
     '            for d in (5, 6):\n                for t in self.sablonlar:\n                    if (c["id"], d, t["id"]) in self.x:\n                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)',
     '            for d in (5, 6):\n                for t in self.sablonlar:\n                    if (c["id"], d, t["id"]) in self.x:\n                        pass',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu hsonu: yalniz cumartesi kapansin',
     '            for d in (5, 6):\n                for t in self.sablonlar:',
     '            for d in (5,):\n                for t in self.sablonlar:',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu hsonu: gecmiste yalniz cumartesi',
     '                         if g % 7 in (5, 6)}',
     '                         if g % 7 == 5}',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu hsonu: hafta sifira yuvarlansin',
     '            calisilan = {g // 7 for g, _, _, _ in _gecmis_kayitlari(c)',
     '            calisilan = {int(g / 7) for g, _, _, _ in _gecmis_kayitlari(c)',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu hsonu: sinirda (<=)',
     '            if seri < azami:\n                continue\n            for d in (5, 6):',
     '            if seri <= azami:\n                continue\n            for d in (5, 6):',
     'testler/test_hafta_kurallari.py'),
    # ---- yasal gece tanimi (md. 7/2) -- isaret DEGIL
    ("hafta", K, 'devri: K-40 isaretine bak (firma tanimi)',
     '        geceler = [a for a in liste if _yasal_gece_postasi_mi(a)]',
     '        geceler = [a for a in liste if _atama_gece_mi(girdi, a, None)]',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'yasal gece: yarisi da gece sayilsin',
     '    return 2 * gece > (bit - bas) + 1e-9\n',
     '    return 2 * gece >= (bit - bas) - 1e-9\n',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'yasal gece: en ufak ortusme yeter',
     '    return 2 * gece > (bit - bas) + 1e-9\n',
     '    return gece > 0\n',
     'testler/test_hafta_kurallari.py'),
    ("hafta", K, 'yasal gece: onceki gecenin donemine bakma',
     '    for d in (gun - 1, gun, gun + 1):\n        w0 = zaman.mutlak(d, p_bas)',
     '    for d in (gun, gun + 1):\n        w0 = zaman.mutlak(d, p_bas)',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: K-40 isaretine bak',
     '        geceler = [t for t in self.sablonlar\n                   if _yasal_gece_postasi(t["bas"], t["bit"])]',
     '        geceler = [t for t in self.sablonlar if _gece_sablonu(t)[0]]',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu devri: gecmis kaydin isaretine bak',
     '                              if _yasal_gece_postasi(b0, b1)}\n            seri = 0',
     '                              if _gecmis_gece_mi(b0, b1, _)}\n            seri = 0',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu yasal gece: en ufak ortusme yeter',
     '    return 2 * gece > (bit - bas) + 1e-9\n',
     '    return gece > 0\n',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu yasal gece: yarisi da gece sayilsin',
     '    return 2 * gece > (bit - bas) + 1e-9\n',
     '    return 2 * gece >= (bit - bas) - 1e-9\n',
     'testler/test_hafta_kurallari.py'),
    ("hafta", M, 'cozucu yasal gece: onceki gece yok',
     '    for w0 in (-4.0, 20.0, 44.0):',
     '    for w0 in (20.0, 44.0):',
     'testler/test_hafta_kurallari.py'),
    # ---- gece tespiti: isaretsiz tahmin (T-69), adalet boyutu (T-71)
    ("gece_tespiti", K, 'tahmin: eski olcu (ayni gun, en ufak degme)',
     '    return _yasal_gece_postasi_mi(\n        {"gun": 0, "bas": sablon["bas"], "bit": sablon["bit"]}), True',
     '    return (min(float(sablon["bit"]), 30.0) - max(float(sablon["bas"]), 20.0) > 0), True',
     'testler/test_gece_tespiti.py'),
    ("gece_tespiti", M, 'cozucu tahmin: eski olcu (ayni gun, en ufak degme)',
     '    return _yasal_gece_postasi(sablon["bas"], sablon["bit"]), True',
     '    return (min(float(sablon["bit"]), 30.0) - max(float(sablon["bas"]), 20.0) > 0), True',
     'testler/test_gece_tespiti.py'),
    ("gece_tespiti", K, 'adalet: sablon isaretine bakma',
     '        return lambda a: _atama_gece_mi(girdi, a, sablonlar)',
     '        return lambda a: _atama_gece_mi({}, a, {})',
     'testler/test_gece_tespiti.py'),
    ("gece_tespiti", K, 'adalet: girdi sayaca gecmesin',
     '        sayac = _boyut_sayaci(boyut, girdi)',
     '        sayac = _boyut_sayaci(boyut)',
     'testler/test_gece_tespiti.py'),
    # ---- sahte PDKS uretici (30 Eylul aksami) -- olcum aracinin kendisi
    ("pdks", '../08-motor-testleri/gercekci-veri-seti/sahte_pdks.py', 'yakalanan gerceklesende olmayan kayit icersin',
     '            k for k in yasanan if rnd.random() < ayar["kayit_orani"]]',
     '            k for k in yasanan if rnd.random() < ayar["kayit_orani"]] + [\n            {"gun": -1, "bas": 1, "bit": 2}]',
     '../08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py'),
    ("pdks", '../08-motor-testleri/gercekci-veri-seti/sahte_pdks.py', 'bilinen gun = planli gun',
     '        bilinen[kimlik] = sorted({k["gun"] for k in yakalanan})',
     '        bilinen[kimlik] = sorted({a["gun"] - kaydir for a in kisiye.get(kimlik, [])})',
     '../08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py'),
    ("pdks", '../08-motor-testleri/gercekci-veri-seti/sahte_pdks.py', 'uyum orani yok sayilsin',
     '            if r < ayar["uyum"]:',
     '            if r < 0.5:',
     '../08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py'),
    ("pdks", '../08-motor-testleri/gercekci-veri-seti/sahte_pdks.py', 'kayda gece isareti eklensin',
     '            yasanan.append({"gun": a["gun"] - kaydir, "bas": bas, "bit": bit})',
     '            yasanan.append({"gun": a["gun"] - kaydir, "bas": bas, "bit": bit,\n                            "gece": False})',
     '../08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py'),
    ("pdks", '../08-motor-testleri/gercekci-veri-seti/sahte_pdks.py', 'cakisma dinlenme satiriyla eslenmesin',
     'HABERCI = {"CAKISMA_YOK": "VARDIYA_ARASI_DINLENME"}',
     'HABERCI = {}',
     '../08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py'),
    # ---- sure butcesi (T-59, 30 Eylul aksami)
    ("butce", C, 'birinci asama eski butcesini alsin',
     '        c.parameters.max_time_in_seconds = _ilk_asama_payi(ayar)',
     '        c.parameters.max_time_in_seconds = float(ayar.get("ilk_asama_saniye", 120))',
     'testler/test_sure_butcesi.py'),
    ("butce", C, 'ana cozum butcenin tamamini alsin',
     '    ana_butce = max(1.0, float(ayar["azami_saniye"]) - ilk_asama)',
     '    ana_butce = float(ayar["azami_saniye"])',
     'testler/test_sure_butcesi.py'),
    ("butce", C, 'ana cozume sifir kalabilsin',
     '    ana_butce = max(1.0, float(ayar["azami_saniye"]) - ilk_asama)',
     '    ana_butce = max(0.0, float(ayar["azami_saniye"]) - ilk_asama)',
     'testler/test_sure_butcesi.py'),
    ("butce", C, 'durma sebebi eski kiyasla',
     '    if butce is None:\n        butce = ayar["azami_saniye"]',
     '    butce = ayar["azami_saniye"]',
     'testler/test_sure_butcesi.py'),
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
