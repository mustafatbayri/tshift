# -*- coding: utf-8 -*-
"""KUCUK OLCEKLI ON OLCUM (bulut, 2 cekirdek) -- URUN OLCUMU DEGILDIR.
Ayni sahnede uc yol:
  kapali : 6 Ekim oncesi (once fazla mesaisiz YOK)
  sert   : once fazla mesaisiz + fazla mesai 0'da TUTULUR (6 Ekim'de olculen hal)
  yeni   : once fazla mesaisiz, sonra alanlar ACIK (7 Ekim duzeltmesi; urunun varsayilani)
Kullanim: python3 olc3.py <depo> <olcek> <doluluk> <butce_sn> <tekrar> <cikti.jsonl> [yollar]
"""
import copy, importlib, json, os, sys, time
sys.dont_write_bytecode = True
DEPO, OLCEK, DOLULUK, BUTCE, TEKRAR, CIKTI = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
YOLLAR = sys.argv[7].split(",") if len(sys.argv) > 7 else ["kapali", "sert", "yeni"]
sys.path.insert(0, os.path.join(DEPO, "09-motor"))
sys.path.insert(0, os.path.join(DEPO, "08-motor-testleri", "gercekci-veri-seti"))
from ortools.sat.python import cp_model
from cozucu.model import Model
import dogrulayici
C = importlib.import_module("cozucu.coz")
import uret_veri_seti as U

AYARLAR = {
    "kapali": {"fazla_mesai_once_sifir": False},
    "sert": {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": True},
    "yeni": {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False},
}
FM = []

class Izleyici(C._CozumSayaci):
    """Iyilestirme sirasinda fazla mesai toplaminin (dk) DEGISTIGI anlar."""
    def __init__(self):
        C._CozumSayaci.__init__(self)
        self.fm_izi = []
    def on_solution_callback(self):
        C._CozumSayaci.on_solution_callback(self)
        dk = int(sum(self.Value(v) for v in FM))
        if not self.fm_izi or self.fm_izi[-1][1] != dk:
            self.fm_izi.append((round(time.time() - self.basladi, 1), dk))

SON = {}
def izli(model, saniye, isci):
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = isci
    geri = Izleyici()
    durum = c.Solve(model, geri)
    SON["fm_izi"] = geri.fm_izi
    return durum, c, geri
C._iyilestirme_coz = izli

g0 = U.sahne_uret(OLCEK, DOLULUK)
print("sahne: %d kisi, olcek %s, doluluk %s, butce %s sn, isci %s" % (
    len(g0["calisanlar"]), OLCEK, DOLULUK, BUTCE, C.isci_sayisi(dict(C.VARSAYILAN))), flush=True)
for t in range(TEKRAR):
    for yol in YOLLAR:
        g = copy.deepcopy(g0)
        t0 = time.time()
        k = Model(g).kur()
        kurma = time.time() - t0
        FM[:] = [v for _, v in k.cezalar if v.Name().startswith("fm_")]
        SON.clear()
        c = C.coz(g, dict(AYARLAR[yol], azami_saniye=BUTCE), kuruldu=k)
        ist = c.get("cozum_istatistikleri") or {}
        m = c.get("metrikler") or {}
        kayit = {"yol": yol, "tekrar": t + 1, "durum": c["durum"], "kurma_sn": round(kurma, 1),
                 "degisken": len(k.m.Proto().variables),
                 "amac": ist.get("amac_degeri"), "fm_saat": m.get("fazla_mesai_saat"),
                 "sebep": ist.get("durma_sebebi"), "iki_asama": ist.get("iki_asama"),
                 "ilk_asama_sn": ist.get("ilk_asama_sn"), "ana_sn": ist.get("cozum_suresi_sn"),
                 "once": ist.get("fazla_mesai_once_sifir"),
                 "dagilim": {a: [b["ceza"], b["deger"]] for a, b in (ist.get("amac_dagilimi") or {}).items()},
                 "fm_izi": SON.get("fm_izi"),
                 "notlar": [n for n in (c.get("uygulanmayan_notlar") or []) if "fazla mesai" in n]}
        iy = ist.get("ilk_asama_iyilestirme") or {}
        kayit["iyilestirme"] = {a: iy.get(a) for a in ("saniye", "amacsiz_amac", "iyilesmis_amac", "cozum_sayisi", "optimum")}
        e = iy.get("iyilesme") or {}
        kayit["iyilestirme"].update({a: e.get(a) for a in ("yuzde50_sn", "yuzde90_sn", "yuzde99_sn", "son_iyilesme_sn")})
        kayit["iyilestirme"]["egri"] = [[p[0], int(p[1])] for p in (e.get("egri") or [])]
        kayit["iyilestirme"]["fm"] = (iy.get("amac_dagilimi") or {}).get("FAZLA_MESAI", {}).get("deger")
        if c["durum"] == "cozuldu":
            r = dogrulayici.degerlendir(copy.deepcopy(g), c["atamalar"])
            kayit["yayinlanabilir"] = r["yayin_kapisi"]["yayinlanabilir"]
            kayit["sert_ihlal"] = r["metrikler"].get("sert_ihlal")
            kayit["dog_fm"] = r["metrikler"].get("fazla_mesai_saat")
        with open(CIKTI, "a") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        print("%-6s #%d amac=%-7s fm=%-5s sebep=%s yayin=%s iyilestirme: %s -> %s (%ss, %s cozum) fm_izi=%s" % (
            yol, t + 1, kayit["amac"], kayit["fm_saat"], kayit["sebep"], kayit.get("yayinlanabilir"),
            kayit["iyilestirme"]["amacsiz_amac"], kayit["iyilestirme"]["iyilesmis_amac"],
            kayit["iyilestirme"]["saniye"], kayit["iyilestirme"]["cozum_sayisi"],
            (kayit["fm_izi"] or [])[:3] + (["..."] if len(kayit["fm_izi"] or []) > 6 else []) + (kayit["fm_izi"] or [])[-3:]), flush=True)
