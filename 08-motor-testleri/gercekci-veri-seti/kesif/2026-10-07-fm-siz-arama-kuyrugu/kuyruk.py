# -*- coding: utf-8 -*-
"""FAZLA MESAISIZ ILK ARAMANIN KUYRUGU -- T-60 bulgu 25 (7 Ekim)  [kesif; motor degismez]

NEDEN
  Urun yolu (K-61) birinci asamada gecerli plani fazla mesai degiskenleri
  [0,0]'a sabitken arar; payi en cok 120 sn (`_ilk_asama_payi`). 7 Ekim gece
  kosusunda bu arama 18 kosunun 17'sinde 8,6-21 sn surdu, 1'inde 120 sn'de
  bulamadi -> motor fazla mesai serbest yola dustu, plan 30 saat fazla
  mesaiyle dondu (116.976; otekiler 26,6-26,8 bin). Soru: bu kuyruk ne kadar
  kalin, ve 120 sn'yi kac deneme halinde harcamak (yeniden baslatma) kuyrugu
  keser mi?

NE YAPAR (iki kip)
  TOHUM KIPI (varsayilan): 500 kisilik fiksturu bir kez kurar, birinci
  asamayi MOTORUN KENDI yardimcilariyla aynen hazirlar (amac silinir, molalar
  sablonun ideal yerine sabitlenir, fm_* alanlari [0,0]) ve ayni modeli N
  farkli `random_seed` ile cozer; her denemede sure ve durum yazilir.
  Varsayilan isci sayisi motorunkiyle aynidir (makinenin cekirdegi).
  ⚠ DUZELTME (7 Ekim 18:40): 18:00 kosusunda "seed 0 motorun kullandigi
    deger (CP-SAT varsayilani)" yaziliydi -- YANLIS. CP-SAT'in varsayilan
    tohumu 1'dir (ortools 9.15, `CpSolver().parameters.random_seed` -> 1) ve
    motor tohum yazmadigi icin 1 ile ariyordu. 18:00 kosusundaki "5 x tohum 0"
    motorun tohumunun degil, tohum 0'in tekrariydi; vardigi sonuc (ayni
    tohumda bile 7x fark -> rastgelelik paralel iscilerin zamanlamasindan)
    gecerliligini korur. Tekrarlanan tohum artik `--tekrar-tohum` (varsayilan
    1 = motorun tohumu); `--sifir-tekrar` adi 18:00 kaydinin komut satiri
    gecerli kalsin diye duruyor (anlami: tekrar SAYISI).
  POLITIKA KIPI (`--politika N`): motorun KENDI `_fazla_mesaisiz_ara`
  fonksiyonunu (yeniden baslatma: pay N'e bolunur, tohum 1..N, ilk bulunan
  alinir) `--deneme` kez kosturur; her kosuda bulundu mu, toplam sure, kac
  denemede. Bu, politikanin motor disinda ama motorun koduyla olcumudur;
  asil olcum kalite-olc.py `fm_once_deneme3` (900 sn x 3).

KULLANIM (Mustafa'nin makinesi; bulutta kosturulmaz -- 500 kisi)
  cd 08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-fm-siz-arama-kuyrugu
  py kuyruk.py --deneme 30 --tavan 120 --sifir-tekrar 5 --cikti kuyruk-30.jsonl      (18:00 kosusu)
  py kuyruk.py --politika 3 --deneme 20 --tavan 120 --cikti politika-3x40.jsonl       (3 x 40 sn, 20 kez)
  (~1 dk kurma + deneme basina 9-120 sn)
  Duman testi (kucuk sahne, sayilari anlamsiz): py kuyruk.py --olcek 0.1 --deneme 3 --tavan 30 --sifir-tekrar 1 --cikti duman.jsonl

CIKTI
  tohum kipi jsonl: {"seed", "durum", "saniye", "cozum_bulundu"}; sonda ozet:
  kantiller, P(T > 20/40/60/120 sn) ve yeniden-baslatma politikalarinin
  OFFLINE tahmini (ornegin 3 x 40 sn: deneme bagimsiz sayilarak P(hepsi > 40)).
  politika kipi jsonl: {"kip": "politika", "bulundu", "saniye", "denemeler"}.
"""
import io, json, os, sys, time
sys.dont_write_bytecode = True
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor"))
from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model, isci_sayisi                  # noqa: E402
import importlib                                             # noqa: E402
C = importlib.import_module("cozucu.coz")                    # paket `coz` adini fonksiyona verir; modul boyle alinir


def _arg(ad, varsayilan, tur=str):
    if ad in sys.argv:
        return tur(sys.argv[sys.argv.index(ad) + 1])
    return varsayilan


DENEME = _arg("--deneme", 30, int)
TAVAN = _arg("--tavan", 120.0, float)
SIFIR_TEKRAR = _arg("--sifir-tekrar", 5, int)       # tekrar SAYISI (ad 18:00 kaydindan)
TEKRAR_TOHUM = _arg("--tekrar-tohum", 1, int)       # tekrarlanan tohum; 1 = motorun tohumu (CP-SAT varsayilani)
POLITIKA = _arg("--politika", 0, int)               # 0 = tohum kipi; N = motorun yeniden baslatmasi, N deneme
ISCI = _arg("--isci", 0, int) or isci_sayisi(dict(C.VARSAYILAN))
CIKTI = _arg("--cikti", "kuyruk.jsonl")
OLCEK = _arg("--olcek", 1.0, float)          # 1.0 = 500 kisilik fikstur; kucuk deger = uretilmis sahne (duman testi)
FIKSTUR = os.path.join(BURASI, "..", "..", "fikstur", "_sahne-S30-95.json")

if OLCEK == 1.0:
    g = json.load(io.open(FIKSTUR, encoding="utf-8"))
else:
    sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
    from uret_veri_seti import sahne_uret
    g = sahne_uret(OLCEK, 0.95)
    print("DUMAN TESTI: olcek %s (%d kisi) -- 500 kisilik olcum degildir" % (OLCEK, len(g["calisanlar"])), flush=True)
t0 = time.time()
k = Model(g).kur()
varsayilan_tohum = cp_model.CpSolver().parameters.random_seed
print("kurma %.0f sn | %d degisken | isci %d | tavan %.0f sn | CP-SAT varsayilan tohumu %d (motorun tohumu)"
      % (time.time() - t0, len(k.m.Proto().variables), ISCI, TAVAN, varsayilan_tohum), flush=True)

# Birinci asamanin hazirligi -- `_ipucu_ver` ile ayni sira, ayni yardimcilar
k.m.ClearObjective()
sabitlenen = C._molalari_sabitle(k)
fm_eski = C._fazla_mesaiyi_sifirla(k)
print("molalar sabit: %d aday kapatildi | fazla mesai degiskeni [0,0]: %d" % (len(sabitlenen), len(fm_eski)), flush=True)

if POLITIKA > 0:
    # ---- POLITIKA KIPI: motorun kendi yeniden baslatmasi, DENEME kez
    ayar = dict(C.VARSAYILAN, fazla_mesaisiz_deneme=POLITIKA, isci_sayisi=ISCI)
    print("POLITIKA: %d x %.0f sn (pay %.0f sn), %d kosu" % (POLITIKA, TAVAN / POLITIKA, TAVAN, DENEME), flush=True)
    bulunan, toplamlar, ikinci_ve_sonrasi = 0, [], 0
    with open(CIKTI, "a") as f:
        for i in range(1, DENEME + 1):
            t1 = time.time()
            durum, c, denemeler = C._fazla_mesaisiz_ara(k, ayar, TAVAN)
            sure = time.time() - t1
            bulundu = durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)
            kayit = {"kip": "politika", "sira": i, "politika": POLITIKA, "tavan": TAVAN, "isci": ISCI,
                     "bulundu": bulundu, "saniye": round(sure, 2), "denemeler": denemeler}
            f.write(json.dumps(kayit) + "\n"); f.flush()
            bulunan += bulundu
            toplamlar.append(sure)
            ikinci_ve_sonrasi += len(denemeler) > 1
            print("%3d  %-10s %7.2f sn  denemeler: %s%s" % (
                i, "BULUNDU" if bulundu else "YOK", sure,
                " / ".join("t%d %s %.1fs" % (d["tohum"], d["durum"], d["saniye"]) for d in denemeler),
                "" if bulundu else "   <-- BULUNAMADI"), flush=True)
    n = len(toplamlar)
    sirali = sorted(toplamlar)
    print("\nOZET (politika %d x %.0f sn): %d kosu | bulunamayan %d | 2+ deneme gereken %d | medyan %.1f sn | en uzun %.1f sn"
          % (POLITIKA, TAVAN / POLITIKA, n, n - bulunan, ikinci_ve_sonrasi,
             sirali[len(sirali) // 2], sirali[-1]))
    print("Kayit:", CIKTI)
    sys.exit(0)

# ---- TOHUM KIPI
seedler = [TEKRAR_TOHUM] * SIFIR_TEKRAR + list(range(1, DENEME + 1))
sureler = []
with open(CIKTI, "a") as f:
    for i, seed in enumerate(seedler, 1):
        c = cp_model.CpSolver()
        c.parameters.max_time_in_seconds = TAVAN
        c.parameters.num_search_workers = ISCI
        c.parameters.random_seed = seed
        t1 = time.time()
        durum = c.Solve(k.m)
        sure = time.time() - t1
        bulundu = durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        kayit = {"sira": i, "seed": seed, "durum": c.StatusName(durum), "saniye": round(sure, 2),
                 "cozum_bulundu": bulundu, "isci": ISCI, "tavan": TAVAN}
        f.write(json.dumps(kayit) + "\n"); f.flush()
        sureler.append(sure if bulundu else float("inf"))
        print("%3d  seed %3d  %-10s %7.2f sn%s" % (i, seed, c.StatusName(durum), sure, "" if bulundu else "   <-- BULUNAMADI"), flush=True)

# Ozet
n = len(sureler)
bitti = sorted(s for s in sureler if s != float("inf"))
def kantil(p):
    if not bitti:
        return None
    i = min(len(bitti) - 1, int(round(p * (len(bitti) - 1))))
    return bitti[i]
print("\nOZET: %d deneme | bulunamayan %d | medyan %.1f sn | %%90 %.1f sn | en uzun %.1f sn"
      % (n, n - len(bitti), kantil(0.5) or -1, kantil(0.9) or -1, (bitti[-1] if bitti else -1)))
for esik in (10, 20, 40, 60, 90, 120):
    p = sum(1 for s in sureler if s > esik) / n
    print("  P(T > %3d sn) = %.3f  (%d/%d)" % (esik, p, sum(1 for s in sureler if s > esik), n))
print("\nYENIDEN BASLATMA (offline tahmin; denemeler bagimsiz sayildi, 120 sn toplam):")
for parca, adet in ((120, 1), (60, 2), (40, 3), (30, 4)):
    p_bir = sum(1 for s in sureler if s > parca) / n
    print("  %d x %3d sn : tek denemede basarisizlik %.3f -> hepsinde %.4f" % (adet, parca, p_bir, p_bir ** adet))
print("\nKayit:", CIKTI)
