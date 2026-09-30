# -*- coding: utf-8 -*-
"""
IKI HAFTA -- gecmis veri olmadan motor ne kaciriyordu? (T-28, olcum araci)

MUSTAFA'NIN ONERISI (30 Eylul)
  "Gecmis datayi test etmek amacli test planini iki asamali yaparsak...
   once 1 hafta sonrasini ve ondan sonra diger haftayi, bu sekilde elimizde
   gecmis data olur."

NE YAPAR
  1. Hafta 1 cozulur (%95 seti, 0.1 olcek -- bekcilerle ayni ayar).
  2. Hafta 1'in atamalari hafta 2'nin GECMISI olur: gun - 7.
     Gecmis TAM kabul edilir (`gecmis_bilinen_gunler` = -7..-1): plan
     bilindigi icin bilinmeyen gun yok.
  3. Hafta 2 IKI KEZ cozulur:
       * gecmissiz  -- 30 Eylul'e kadarki motor boyle calisiyordu
       * gecmisle   -- T-28'den sonra
  4. Ikisi de GECMISI BILEN dogrulayiciya sorulur -- gercegi o soyler.

⚠ GECMIS BURADA PLANDIR, PDKS DEGIL
  Gercek PDKS'te kayitlarin yalniz %18'i dolu (P-1) ve plandan sapma var.
  Bu arac mekanigi olcer: motor gecmisi okuyor mu, sinirda dogru mu
  davraniyor. Gercekci gecmis (sahte PDKS) ikinci asamadir.

KOSTURMA (uzun: uc cozum, ~10 dk)
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py iki-hafta-olc.py
"""

import collections
import copy
import importlib.util
import io
import json
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "uret", os.path.join(BURASI, "uret_veri_seti.py"))
U = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(U)

AYAR = {"azami_saniye": 240, "durgunluk_saniye": 25}
SINIR_KURALLARI = ("VARDIYA_ARASI_DINLENME", "CAKISMA_YOK", "HAFTA_TATILI",
                   "ARDISIK_CALISMA_GUNU", "ARDISIK_GECE_LIMIT")


def gecmis_ekle(g, atamalar):
    """Hafta 1'in atamalarini hafta 2'nin gecmisi yapar. g YERINDE degisir.

    Gece isareti sablondan tasinir -- plan bunu biliyor. PDKS bilmeyecek;
    o zaman saatten tahmin edilir (K-40).
    """
    sablon = {t["id"]: t for t in g["vardiya_sablonlari"]}
    kisi = collections.defaultdict(list)
    for a in atamalar:
        k = {"gun": a["gun"] - 7, "bas": a["bas"], "bit": a["bit"]}
        t = sablon.get(a.get("sablon")) or {}
        if "gece_vardiyasi" in t:
            k["gece"] = bool(t["gece_vardiyasi"])
        kisi[a["calisan"]].append(k)
    for c in g["calisanlar"]:
        c["gecmis_vardiyalar"] = kisi.get(c["id"], [])
        c["gecmis_bilinen_gunler"] = list(range(-7, 0))
    return g


def gecmissiz(g):
    g = copy.deepcopy(g)
    for c in g["calisanlar"]:
        c.pop("gecmis_vardiyalar", None)
        c.pop("gecmis_bilinen_gunler", None)
    return g


def sinir_ihlalleri(g_gercek, atamalar):
    r = degerlendir(g_gercek, atamalar)
    say = collections.Counter(i["kural"] for i in r["ihlaller"]
                              if i["kural"] in SINIR_KURALLARI)
    sert = sum(1 for i in r["ihlaller"] if i.get("agirlik") == "SERT")
    return say, sert, r


def main():
    t0 = time.time()
    g1 = U.sahne_uret(0.1, 0.95)
    c1 = coz(g1, AYAR)
    print("HAFTA 1: %s · %d atama · %.0f sn"
          % (c1["durum"], len(c1.get("atamalar") or []), time.time() - t0))
    if c1["durum"] != "cozuldu":
        sys.exit("hafta 1 cozulemedi")

    pazar_gecesi = sum(1 for a in c1["atamalar"]
                       if a["gun"] == 6 and a["bit"] > 24)
    print("  pazar gecesi pazartesiye tasan vardiya: %d" % pazar_gecesi)

    g2 = gecmis_ekle(U.sahne_uret(0.1, 0.95), c1["atamalar"])

    sonuc = {}
    for ad, girdi in (("gecmissiz", gecmissiz(g2)), ("gecmisle", g2)):
        t = time.time()
        c = coz(girdi, AYAR)
        say, sert, r = sinir_ihlalleri(g2, c.get("atamalar") or [])
        sonuc[ad] = {"durum": c["durum"], "atama": len(c.get("atamalar") or []),
                     "sinir": dict(say), "sert": sert,
                     "gecmis_eksik": len(r.get("gecmis_eksik") or []),
                     "sn": round(time.time() - t)}
        print("\nHAFTA 2 %-10s %s · %d atama · %.0f sn"
              % (ad, c["durum"], sonuc[ad]["atama"], time.time() - t))
        print("  gecmisi bilen denetciye gore sinir ihlali: %s"
              % (dict(say) or "YOK"))
        print("  toplam sert ihlal: %d · gecmis_eksik: %d"
              % (sert, sonuc[ad]["gecmis_eksik"]))

    with io.open(os.path.join(BURASI, "iki-hafta-sonucu.json"), "w",
                 encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("\nToplam %.0f sn" % (time.time() - t0))


if __name__ == "__main__":
    main()
