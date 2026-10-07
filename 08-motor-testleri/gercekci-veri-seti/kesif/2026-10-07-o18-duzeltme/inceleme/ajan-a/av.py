# -*- coding: utf-8 -*-
"""KARSI ORNEK AVI (ajan-a, 7 Ekim): rastgele kucuk sahnelerde TAM (kanitli
optimum, tek model) ile URUN (asamali varsayilan yol) kiyasi.

Kullanim: MOTOR=<motor> python3 av.py <tohum> <sahne_sayisi> <cikti.jsonl> <gap_dizini>
"""
import copy, importlib, json, os, random, sys, time
sys.dont_write_bytecode = True
MOTOR = os.environ["MOTOR"]
sys.path.insert(0, MOTOR)
from ortools.sat.python import cp_model
from cozucu.model import Model
import dogrulayici
C = importlib.import_module("cozucu.coz")

TOHUM, SAYI, CIKTI, GAP = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
os.makedirs(GAP, exist_ok=True)
R = random.Random(TOHUM)

TAM = {"azami_saniye": 40, "isci_sayisi": 2, "hedef_bosluk": 0.0, "fazla_mesai_once_sifir": False}
URUN = {"azami_saniye": 40, "iki_asama_esigi": 0, "durgunluk_saniye": 5, "isci_sayisi": 2}
KAPALI = dict(URUN, fazla_mesai_once_sifir=False)
SERT = dict(URUN, fazla_mesai_sifirda_tut=True)
YEMEK = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]


def q(x):
    return round(x * 4) / 4.0


def sablon(kimlik, ekip, bas, bit, gunler=None):
    s = {"id": kimlik, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": 60,
         "mola_politikasi": copy.deepcopy(YEMEK)}
    if gunler is not None:
        s["gunler"] = sorted(gunler)
    return s


def kurallar(saat_dengesi):
    k = [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False, "kabul_edilebilir": False},
         {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
         {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
         {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True, "parametreler": {"azami_saat": 11}},
         {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True, "parametreler": {"azami_saat": 45}},
         {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True, "parametreler": {"azami_saat_hafta": 10}},
         {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True}]
    if saat_dengesi:
        k.append({"kod": "SAAT_DENGESI", "tur": saat_dengesi, "aktif": True, "yasal": False,
                  "kabul_edilebilir": True, "parametreler": {"tolerans_saat": 0}})
    return k


def sahne_uret():
    n = R.randint(1, 6)
    iki_ekip = R.random() < 0.4
    ekipler = ["E", "F"] if iki_ekip else ["E"]
    profil = R.choice(["DENGELI", "KAPSAMA"])
    sd = R.choice([None, "YUMUSAK", "SERT"])
    # fazla mesaiye MEYILLI kip (yarisi): 45 saat sozlesme, 6 gun talep, hedef = kadro,
    # saat dengesi var -> ceyrek saatlik adimlar sozlesmeyi tam dolduramayabilir
    meyilli = R.random() < 0.5
    if meyilli:
        sd = R.choice(["YUMUSAK", "SERT"])
    # KILIT kipi (ajan-a, 2. tur): fm'siz plan VAR ama ceyrek saatlik adim haftayi kilitler --
    # SAAT_DENGESI YUMUSAK agirlikli; SERT ise talep DISINDA bir kacis sablonu eklenir.
    kilit = os.environ.get("KIP") == "kilit"
    if kilit:
        meyilli = True
        sd = "YUMUSAK" if R.random() < 0.7 else "SERT"
    calisanlar = []
    for i in range(1, n + 1):
        if iki_ekip:
            uye = R.choice([["E"], ["F"], ["E", "F"], ["E", "F"]])
        else:
            uye = ["E"]
        saat = 45 if meyilli else R.choice([45, 45, 40])
        calisanlar.append({"id": "P%d" % i, "ekipler": uye,
                           "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": saat},
                           "izinler": [], "uygunluk": []})
    sablonlar = []
    sira = 0
    kilit2 = os.environ.get("KIP") == "kilit2"
    if kilit2:
        # S1 yapisinin genellemesi: ana sablon (net x) 5 gun, tek sablon (net y) 6. gun;
        # 5x + y sozlesmeyi 15-45 dk ASAR, 4x + y ve 5x cok altinda kalir.
        meyilli = True
        kilit = True
        sd = "YUMUSAK" if R.random() < 0.7 else "SERT"
        soz = R.choice([45, 45, 40])
        for c in calisanlar:
            c["sozlesme"]["haftalik_saat"] = soz
        for e in ekipler:
            while True:
                x = q(R.uniform(6.5, 9.0))
                y = soz - 5 * x + R.choice([0.25, 0.5, 0.75])
                if 4.0 <= y <= 9.5:
                    break
            gun5 = sorted(R.sample(range(7), 5))
            gun1 = R.choice([d for d in range(7) if d not in gun5])
            bas = q(R.uniform(5.0, 12.0))
            sira += 1; sablonlar.append(sablon("ANA%d" % sira, e, bas, bas + x + 1.0, gun5))
            sira += 1; sablonlar.append(sablon("TEK%d" % sira, e, bas, bas + y + 1.0, [gun1]))
            if R.random() < 0.5:   # dikkat dagitici
                z = q(R.uniform(6.0, 9.5)); b2 = q(R.uniform(5.0, 13.0))
                sira += 1; sablonlar.append(sablon("EK%d" % sira, e, b2, b2 + z + 1.0, sorted(R.sample(range(7), R.randint(1, 3)))))
    for e in ([] if kilit2 else ekipler):
        for _ in range(R.randint(2, 4)):
            sira += 1
            net = q(R.uniform(7.0, 9.5)) if kilit else q(R.uniform(6.0, 9.5))
            bas = q(R.uniform(4.0, 15.0))
            bit = bas + net + 1.0        # 60 dk ucretsiz yemek
            if bit > 25.0:
                bit = 25.0
                bas = bit - net - 1.0
            gunler = None
            if R.random() < 0.6:
                gunler = sorted(R.sample(range(7), R.randint(3, 7)))
            sablonlar.append(sablon("S%d" % sira, e, bas, bit, gunler))
    if kilit and sd == "SERT":
        sira += 1
        sablonlar.append(sablon("KACIS%d" % sira, ekipler[0], 15.0, 25.0, None))   # 9 saat net, talep disinda
    talep = []
    for e in ekipler:
        uye_sayisi = sum(1 for c in calisanlar if e in c["ekipler"])
        if uye_sayisi == 0:
            uye_sayisi = 1
        kaplama = [t for t in sablonlar if t["ekip"] == e and not t["id"].startswith("KACIS")]
        lo = int(min(t["bas"] for t in kaplama))
        hi = int(max(min(t["bit"], 24) for t in kaplama))
        if meyilli:
            h0, h1 = lo, hi
            gunler = sorted(R.sample(range(7), 6))
        else:
            h0 = R.randint(lo, max(lo, hi - 4))
            h1 = R.randint(h0 + 3, max(h0 + 3, hi))
            gunler = sorted(R.sample(range(7), R.randint(4, 6)))
        asgari_mod = R.choice(["yok", "yok", "bir"])
        for d in gunler:
            hedef = uye_sayisi if meyilli else R.randint(1, uye_sayisi)
            for s in range(h0, min(h1, 24)):
                asgari = 0 if asgari_mod == "yok" else (1 if R.random() < 0.3 else 0)
                talep.append({"ekip": e, "gun": d, "saat": s, "asgari": min(asgari, hedef), "hedef": hedef})
    return {"profil": profil, "calisanlar": calisanlar, "vardiya_sablonlari": sablonlar,
            "talep": talep, "kurallar": kurallar(sd), "kilitler": [], "donmus_gunler": [],
            "_meta": {"n": n, "iki_ekip": iki_ekip, "sd": sd, "profil": profil, "meyilli": meyilli, "kilit": kilit, "kilit2": kilit2}}


def uygun_mu(g, sn=4.0):
    k = Model(copy.deepcopy(g)).kur()
    k.m.ClearObjective()
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = sn
    c.parameters.num_search_workers = 2
    d = c.Solve(k.m)
    return d in (cp_model.OPTIMAL, cp_model.FEASIBLE), len(k.m.Proto().variables)


def kos(g, ayar):
    g2 = copy.deepcopy(g)
    g2.pop("_meta", None)
    t0 = time.time()
    c = C.coz(g2, dict(ayar))
    sure = time.time() - t0
    ist = c.get("cozum_istatistikleri") or {}
    m = c.get("metrikler") or {}
    yayin = None
    if c["durum"] == "cozuldu":
        g3 = copy.deepcopy(g); g3.pop("_meta", None)
        r = dogrulayici.degerlendir(g3, c["atamalar"])
        yayin = r["yayin_kapisi"]["yayinlanabilir"]
    return {"durum": c["durum"], "amac": ist.get("amac_degeri"), "alt_sinir": ist.get("alt_sinir"),
            "sebep": ist.get("durma_sebebi"), "fm": m.get("fazla_mesai_saat"), "yayin": yayin,
            "once": ist.get("fazla_mesai_once_sifir"), "iy": ist.get("ilk_asama_iyilestirme"),
            "dagilim": ist.get("amac_dagilimi"), "sure": round(sure, 2),
            "notlar": c.get("uygulanmayan_notlar")}


say = {"uretilen": 0, "uygunsuz": 0, "kanitsiz": 0, "kiyas": 0, "esit": 0, "urun_kotu": 0, "urun_iyi": 0,
       "a_fm_kaynakli": 0, "b_asamali": 0, "c_gurultu": 0}
out = open(CIKTI, "a")
basla = time.time()
i = 0
while say["kiyas"] < SAYI:
    i += 1
    g = sahne_uret()
    say["uretilen"] += 1
    ok, nvar = uygun_mu(g)
    if not ok:
        say["uygunsuz"] += 1
        continue
    tam = kos(g, TAM)
    kanitli = (tam["durum"] == "cozuldu" and tam["sebep"] == "optimum" and tam["alt_sinir"] == tam["amac"])
    if not kanitli:
        say["kanitsiz"] += 1
        out.write(json.dumps({"i": i, "tohum": TOHUM, "meta": g["_meta"], "nvar": nvar, "tam": tam, "sinif": "kanitsiz"}) + "\n")
        out.flush()
        continue
    urun = kos(g, URUN)
    say["kiyas"] += 1
    kayit = {"i": i, "tohum": TOHUM, "meta": g["_meta"], "nvar": nvar, "tam": tam, "urun": urun}
    if urun["durum"] != "cozuldu":
        kayit["sinif"] = "urun_plansiz"
        say["urun_kotu"] += 1
    elif urun["amac"] == tam["amac"]:
        kayit["sinif"] = "esit"
        say["esit"] += 1
    elif urun["amac"] < tam["amac"]:
        kayit["sinif"] = "URUN_DAHA_IYI_(kanit_hatasi?)"
        say["urun_iyi"] += 1
    else:
        say["urun_kotu"] += 1
        # siniflandir: kapali yol ve ikinci urun kosusu
        kapali = kos(g, KAPALI)
        urun2 = kos(g, URUN)
        kayit["kapali"] = kapali
        kayit["urun2"] = urun2
        fm_tam = tam["fm"] or 0
        fm_urun = urun["fm"] or 0
        if urun2["amac"] != urun["amac"]:
            kayit["sinif"] = "c_gurultu"
            say["c_gurultu"] += 1
        elif fm_tam > 0 and fm_urun == 0 and (kapali["amac"] is not None and kapali["amac"] < urun["amac"]):
            kayit["sinif"] = "a_fm_kaynakli"
            say["a_fm_kaynakli"] += 1
        elif kapali["amac"] == urun["amac"]:
            kayit["sinif"] = "b_asamali_yol_siniri"
            say["b_asamali"] += 1
        else:
            kayit["sinif"] = "belirsiz"
        kayit["sahne"] = {k: v for k, v in g.items() if k != "_meta"}
        with open(os.path.join(GAP, "sahne-%d-%d.json" % (TOHUM, i)), "w") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=1)
    out.write(json.dumps(kayit) + "\n")
    out.flush()
    if say["kiyas"] % 10 == 0:
        print("%d kiyas, %.0f sn: %s" % (say["kiyas"], time.time() - basla, say), flush=True)
print("BITTI %.0f sn: %s" % (time.time() - basla, say), flush=True)
