# -*- coding: utf-8 -*-
"""Elle secilmis mutasyonlar (ajan-a). Her biri ajan-a/calisir/09-motor/cozucu/coz.py'ye
uygulanir, test dosyasi kosulur, dosya geri yazilir (md5 ile dogrulanir)."""
import hashlib, io, os, shutil, subprocess, sys, time
BURASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calisir", "09-motor")
COZ = os.path.join(BURASI, "cozucu", "coz.py")
T = "testler/test_fazla_mesai_once_sifir.py"
TD = "testler/test_demir_secenekleri.py"

def md5(p):
    return hashlib.md5(io.open(p, "rb").read()).hexdigest()

def temizle():
    for dizin, alt, _ in os.walk(BURASI):
        for a in list(alt):
            if a in ("__pycache__", ".pytest_cache"):
                shutil.rmtree(os.path.join(dizin, a), ignore_errors=True); alt.remove(a)

def kostur(test, k=None):
    temizle()
    cmd = [sys.executable, "-m", "pytest", test, "-q", "--no-header", "-p", "no:cacheprovider", "-x"]
    if k:
        cmd += ["-k", k]
    p = subprocess.run(cmd, cwd=BURASI, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                       capture_output=True, text=True)
    sat = [s for s in p.stdout.strip().splitlines() if s.strip()]
    fails = [s for s in p.stdout.splitlines() if s.startswith("FAILED")]
    return p.returncode, (sat[-1] if sat else p.stderr[-300:]), fails[:3]

FM_IDX = '    _fmi = [v.Index() for _, v in kuruldu.cezalar if v.Name().startswith("fm_")]\n'

MUTASYONLAR = [
    # (ad, eski, yeni, test, -k)
    ("M-A sifirda = False (olcum secenegi de 0'da tutmasin) [listede #27]",
     '            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))',
     '            sifirda = False', T, None),
    ("M-B serbest birakma yalniz bulunamayinca (if not bulundu) [listede #43]",
     '            if not sifirda:\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     '            if not bulundu:\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).', T, None),
    ("M-C ipucu yazildiktan sonra silinsin [listede #60]",
     '        _tam_ipucu_yaz(kuruldu, c)\n        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)',
     '        _tam_ipucu_yaz(kuruldu, c)\n        if fm_eski:\n            kuruldu.m.ClearHints()\n        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)', T, None),
    ("M-D sifirda = bulundu (sert kesim hep) [listede #23]",
     '            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))',
     '            sifirda = bulundu', T, None),
    ("G-1 iyilestirme sonucu ipucuya YAZILMASIN (mola adimi fm'siz plana sabitlenir)",
     '        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi\n        _tam_ipucu_yaz(kuruldu, c2)',
     '        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi\n        pass', T, None),
    ("G-2 iyilestirme fm'siz modelde kossun (alanlar iyilestirme icin yeniden [0,0], sonra acilir)",
     '    t0 = time.time()\n    durum, c2, sayac = _iyilestirme_coz(kuruldu.m, saniye, isci_sayisi(ayar))',
     '    t0 = time.time()\n    _fme = _fazla_mesaiyi_sifirla(kuruldu)\n    durum, c2, sayac = _iyilestirme_coz(kuruldu.m, saniye, isci_sayisi(ayar))\n    _fazla_mesaiyi_serbest_birak(kuruldu, _fme)', T, None),
    ("G-3 _tam_ipucu_yaz fm ipucularini hep 0 yazsin (mola adimina giden ipucu yanlis)",
     '    proto.solution_hint.vars.extend(list(range(len(degerler))))\n    proto.solution_hint.values.extend(degerler)',
     FM_IDX + '    degerler = [0 if i in _fmi else d for i, d in enumerate(degerler)]\n    proto.solution_hint.vars.extend(list(range(len(degerler))))\n    proto.solution_hint.values.extend(degerler)', T, None),
    ("G-4 iyilestirme SONRASI ipucudan fm degerleri silinsin (mola adimina yarim ipucu)",
     '        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi\n        _tam_ipucu_yaz(kuruldu, c2)',
     '        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi\n        _tam_ipucu_yaz(kuruldu, c2)\n' + FM_IDX.replace("    _fmi", "        _fmi") +
     '        _p = kuruldu.m.Proto(); _cift = [(a, b) for a, b in zip(_p.solution_hint.vars, _p.solution_hint.values) if a not in set(_fmi)]\n        del _p.solution_hint.vars[:]; del _p.solution_hint.values[:]; _p.solution_hint.vars.extend([a for a, _ in _cift]); _p.solution_hint.values.extend([b for _, b in _cift])', T, None),
    ("G-5 _sinir_kapsami: sert kesim mola adimindan ONCE baksin (sira degissin)",
     '    if atamalar_sabit:\n        return "mola_adimi"\n    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):\n        return "fazla_mesaisiz"',
     '    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):\n        return "fazla_mesaisiz"\n    if atamalar_sabit:\n        return "mola_adimi"', TD, "sinir_kapsami"),
    ("G-6 serbest birakma yalniz BULUNUNCA (if bulundu) -- bulunamayinca yol kapanir",
     '            if not sifirda:\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).',
     '            if bulundu:\n                # ⚠ HAKEM AGIRLIKLARDIR (K-61).', T, None),
    ("G-7 iyilestirme kapsamsiz: bulununca iyilestirme ATLANSIN (fm'siz plan dogrudan mola adimina)",
     '        _tam_ipucu_yaz(kuruldu, c)\n        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)',
     '        _tam_ipucu_yaz(kuruldu, c)\n        if not (fm_eski and bulundu):\n            _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)', T, None),
]

RESMI_64_ESKI = '        _tam_ipucu_yaz(kuruldu, c)\n        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)'
RESMI_64_YENI = '        _tam_ipucu_yaz(kuruldu, c)\n        if fm_eski:\n            _p = kuruldu.m.Proto(); _fmi = {i for i, _ in fm_eski}\n            _cift = [(a, b) for a, b in zip(_p.solution_hint.vars, _p.solution_hint.values) if a not in _fmi]\n            del _p.solution_hint.vars[:]; del _p.solution_hint.values[:]; _p.solution_hint.vars.extend([a for a, _ in _cift]); _p.solution_hint.values.extend([b for _, b in _cift])\n        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)'
DUZ_64_YENI = RESMI_64_YENI.replace("del _p.solution_hint.vars[:]; del _p.solution_hint.values[:];", "_p.solution_hint.vars.clear(); _p.solution_hint.values.clear();")
G4_ESKI = '        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi\n        _tam_ipucu_yaz(kuruldu, c2)'
G4_YENI = G4_ESKI + '\n        _fmi = {v.Index() for _, v in kuruldu.cezalar if v.Name().startswith("fm_")}\n        _p = kuruldu.m.Proto(); _cift = [(a, b) for a, b in zip(_p.solution_hint.vars, _p.solution_hint.values) if a not in _fmi]\n        _p.solution_hint.vars.clear(); _p.solution_hint.values.clear(); _p.solution_hint.vars.extend([a for a, _ in _cift]); _p.solution_hint.values.extend([b for _, b in _cift])'
MUTASYONLAR += [
    ("R-64 RESMI #64 oldugu gibi (del [:] ile)", RESMI_64_ESKI, RESMI_64_YENI, T, None),
    ("R-64b RESMI #64 DUZELTILMIS (.clear() ile): iyilestirme girisinde yarim ipucu", RESMI_64_ESKI, DUZ_64_YENI, T, None),
    ("G-4b iyilestirme SONRASI fm ipuclari silinsin (.clear() ile): mola adimina yarim ipucu", G4_ESKI, G4_YENI, T, None),
]

secim = sys.argv[1:]
orijinal = io.open(COZ, encoding="utf-8").read()
once = md5(COZ)
for ad, eski, yeni, test, k in MUTASYONLAR:
    if secim and not any(s in ad for s in secim):
        continue
    if orijinal.count(eski) != 1:
        print("[ATLANDI capa %d] %s" % (orijinal.count(eski), ad), flush=True); continue
    t0 = time.time()
    try:
        io.open(COZ, "w", encoding="utf-8", newline="").write(orijinal.replace(eski, yeni))
        rc, son, fails = kostur(test, k)
    finally:
        io.open(COZ, "w", encoding="utf-8", newline="").write(orijinal)
    assert md5(COZ) == once
    print("[%s] %s\n      %s %s (%.0f sn)" % ("OLDU" if rc else "*** YASADI ***", ad, son, fails, time.time() - t0), flush=True)
temizle()
