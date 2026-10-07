# -*- coding: utf-8 -*-
"""D6: elle ek mutasyonlar -- dondurulmus kopyanin AYRI bir kopyasinda (mut/),
her mutasyon icin ilgili test dosyalari kosulur, sonra ozgun geri yazilir."""
import io, os, shutil, subprocess, sys
BURASI = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(BURASI, "depo", "09-motor")
MUT = os.path.join(BURASI, "mut", "09-motor")
if os.path.exists(os.path.join(BURASI, "mut")):
    shutil.rmtree(os.path.join(BURASI, "mut"))
shutil.copytree(os.path.join(BURASI, "depo"), os.path.join(BURASI, "mut"))
COZ = os.path.join(MUT, "cozucu", "coz.py")
ORJ = io.open(COZ, encoding="utf-8").read()
T_FM = "testler/test_fazla_mesai_once_sifir.py"
T_K63 = "testler/test_mola_adimi_yetismedi.py"

MUTASYONLAR = [
    ("M1 durum_kodu hep OPTIMAL (esdeger beklenir)",
     '                  "durum_kodu": durum,', '                  "durum_kodu": cp_model.OPTIMAL,', [T_K63]),
    ("M2 durum adi hep OPTIMAL",
     '"durum": c.StatusName(durum),\n                  "durum_kodu": durum,',
     '"durum": "OPTIMAL",\n                  "durum_kodu": durum,', [T_K63]),
    ("M3a tohum hep 1 yazilsin",
     'denemeler.append({"tohum": i + 1,', 'denemeler.append({"tohum": 1,', [T_FM]),
    ("M3b tohum kaymis (i+2)",
     'denemeler.append({"tohum": i + 1,', 'denemeler.append({"tohum": i + 2,', [T_FM]),
    ("M3c tohum = len(denemeler)+1 (esdeger)",
     'denemeler.append({"tohum": i + 1,', 'denemeler.append({"tohum": len(denemeler) + 1,', [T_FM]),
    ("M4 parca = pay/(adet+1)",
     '    parca = max(1.0, float(pay) / adet)', '    parca = max(1.0, float(pay) / (adet + 1))', [T_FM]),
    ("M5 not: mola adimi / ana asama ters",
     '% ("mola adimi" if atamalar_sabit else "ana asama"))', '% ("ana asama" if atamalar_sabit else "mola adimi"))', [T_K63]),
    ("M6 K-63 baslangic planinda da denensin",
     'cp_model.INFEASIBLE) and iki_asama:\n        ipucu_plani = _ipucu_planini_al(kuruldu, ayar)',
     'cp_model.INFEASIBLE) and (iki_asama or baslangic_kullanildi):\n        ipucu_plani = _ipucu_planini_al(kuruldu, ayar)', [T_K63]),
    ("M18 ipucu_plani ciktisi yalniz bulununca",
     '        "ipucu_plani": ({a: ipucu_plani[a] for a in ("bulundu", "saniye", "durum")}\n                        if ipucu_plani else None),',
     '        "ipucu_plani": ({a: ipucu_plani[a] for a in ("bulundu", "saniye", "durum")}\n                        if ipucu_plani and ipucu_plani["bulundu"] else None),', [T_K63]),
    ("M19 tavan: 0 -> 30 (or ile)",
     'c.parameters.max_time_in_seconds = max(1.0, float(ayar.get("ipucu_plani_saniye", 30)))',
     'c.parameters.max_time_in_seconds = float(ayar.get("ipucu_plani_saniye") or 30)', [T_K63]),
    ("M20 K-63 yalniz atamalar sabitken",
     'cp_model.INFEASIBLE) and iki_asama:\n        ipucu_plani = _ipucu_planini_al(kuruldu, ayar)',
     'cp_model.INFEASIBLE) and iki_asama and atamalar_sabit:\n        ipucu_plani = _ipucu_planini_al(kuruldu, ayar)', [T_K63]),
    ("M21 not tek denemede de '(1 denemede)' desin (>1 -> >=1)",
     '" (%d denemede)" % len(denemeler) if len(denemeler) > 1 else "")))',
     '" (%d denemede)" % len(denemeler) if len(denemeler) >= 1 else "")))', [T_FM]),
    ("M22 deneme_siniri = len(denemeler)",
     '                "deneme_siniri": _deneme_siniri(ayar),', '                "deneme_siniri": len(denemeler),', [T_FM]),
    ("M11 dusulecek = denemelerin toplami (olcumden degil)",
     '                dusulecek = deneme\n', '                dusulecek = sum(d["saniye"] for d in denemeler)\n', [T_FM]),
    ("M29 fm_once.saniye = yalniz son denemenin suresi",
     '                "saniye": round(deneme, 2),\n                # Bulgu 25',
     '                "saniye": denemeler[-1]["saniye"],\n                # Bulgu 25', [T_FM]),
    ("M30 K-63: cozum_suresi ipucu planinin suresini de kapsasin (sure += saniye)",
     '            cozucu, durum = ipucu_plani["cozucu"], ipucu_plani["durum_kodu"]\n',
     '            cozucu, durum = ipucu_plani["cozucu"], ipucu_plani["durum_kodu"]\n            sure += ipucu_plani["saniye"]\n', [T_K63]),
    ("M31 K-63 sebep: atamalar_sabit yerine mola_adimi ayarina bakilsin",
     '        sebep = "mola_adimi_yetismedi" if atamalar_sabit else "ana_asama_yetismedi"\n        sinir = None',
     '        sebep = "mola_adimi_yetismedi" if mola_adimi else "ana_asama_yetismedi"\n        sinir = None', [T_K63]),
    ("M32 ipucu eksik kontrolu <= (tam ipucu da eksik sayilsin)",
     '    if len(proto.solution_hint.vars) < len(proto.variables):', '    if len(proto.solution_hint.vars) <= len(proto.variables):', [T_K63]),
    ("M33 fm-siz aramada ilk deneme payin tamamini alsin, kalanlar 1 sn",
     '        c.parameters.max_time_in_seconds = parca\n        c.parameters.num_search_workers = isci\n        c.parameters.random_seed = i + 1',
     '        c.parameters.max_time_in_seconds = parca if i else float(pay)\n        c.parameters.num_search_workers = isci\n        c.parameters.random_seed = i + 1', [T_FM]),
    ("M34 denemeler listesi bos kalsin (None yerine [])",
     '        denemeler = None\n        if fm_eski:', '        denemeler = []\n        if fm_eski:', [T_FM, T_K63]),
]


def kos(testler):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-x", "--tb=line"] + testler
    r = subprocess.run(cmd, cwd=MUT, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    satirlar = [s for s in (r.stdout + r.stderr).splitlines() if s.strip()]
    ozet = satirlar[-1] if satirlar else "?"
    ilk = next((s for s in satirlar if s.startswith(("/", "E ", "FAILED")) or "Error" in s), "")
    return r.returncode, ozet, ilk


for ad, eski, yeni, testler in MUTASYONLAR:
    if ORJ.count(eski) != 1:
        print("%-70s CAPA %d kez (atlandi)" % (ad, ORJ.count(eski)))
        continue
    io.open(COZ, "w", encoding="utf-8").write(ORJ.replace(eski, yeni))
    try:
        kod, ozet, ilk = kos(testler)
    finally:
        io.open(COZ, "w", encoding="utf-8").write(ORJ)
    print("%-70s %s   %s\n%s" % (ad, "OLDU " if kod else "YASIYOR", ozet, ("      " + ilk[:200]) if kod else ""))
    sys.stdout.flush()

kod, ozet, _ = kos([T_FM, T_K63])
print("\nOZGUN KOD (son):", ozet)
