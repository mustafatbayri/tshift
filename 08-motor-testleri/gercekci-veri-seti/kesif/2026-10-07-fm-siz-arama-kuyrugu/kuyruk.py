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

NE YAPAR
  500 kisilik fiksturu bir kez kurar, birinci asamayi MOTORUN KENDI
  yardimcilariyla aynen hazirlar (amac silinir, molalar sablonun ideal
  yerine sabitlenir, fm_* alanlari [0,0]) ve ayni modeli N farkli
  `random_seed` ile cozer; her denemede sure ve durum yazilir. Varsayilan
  isci sayisi motorunkiyle aynidir (makinenin cekirdegi). Seed 0 motorun
  kullandigi degerdir (CP-SAT varsayilani); paralel iscilerle zamanlama
  yine de rastgeledir, o yuzden seed 0 birkac kez tekrarlanir.

KULLANIM (Mustafa'nin makinesi; bulutta kosturulmaz -- 500 kisi)
  cd 08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-fm-siz-arama-kuyrugu
  py kuyruk.py --deneme 30 --tavan 120 --sifir-tekrar 5 --cikti kuyruk-30.jsonl
  (~1 dk kurma + deneme basina 9-120 sn; 30 deneme tipik 10-25 dk)
  Duman testi (kucuk sahne, sayilari anlamsiz): py kuyruk.py --olcek 0.1 --deneme 3 --tavan 30 --sifir-tekrar 1 --cikti duman.jsonl

CIKTI
  jsonl: {"seed", "durum", "saniye", "cozum_bulundu"}; sonda ozet: kantiller,
  P(T > 20/40/60/120 sn) ve yeniden-baslatma politikalarinin OFFLINE tahmini
  (ornegin 3 x 40 sn: deneme bagimsiz sayilarak P(hepsi > 40)). Tahmin,
  karar icin yeter; politika secilince motorda gercekten olculur.
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
SIFIR_TEKRAR = _arg("--sifir-tekrar", 5, int)
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
print("kurma %.0f sn | %d degisken | isci %d | tavan %.0f sn | deneme %d (+ seed 0 x %d)"
      % (time.time() - t0, len(k.m.Proto().variables), ISCI, TAVAN, DENEME, SIFIR_TEKRAR), flush=True)

# Birinci asamanin hazirligi -- `_ipucu_ver` ile ayni sira, ayni yardimcilar
k.m.ClearObjective()
sabitlenen = C._molalari_sabitle(k)
fm_eski = C._fazla_mesaiyi_sifirla(k)
print("molalar sabit: %d aday kapatildi | fazla mesai degiskeni [0,0]: %d" % (len(sabitlenen), len(fm_eski)), flush=True)

seedler = [0] * SIFIR_TEKRAR + list(range(1, DENEME + 1))
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
