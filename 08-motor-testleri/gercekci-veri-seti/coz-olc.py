# -*- coding: utf-8 -*-
"""
TAM OLCEKLI COZUM OLCUMU  --  350 kisi

NEDEN AYRI BIR BETIK
  Model kurma tek basina ~117 saniye suruyor; cozum onun ustune biniyor.
  Bu, uzaktan calisan araclarin zaman siniriindan uzun. Olcumu bu yuzden
  senin makinende kosturuyoruz.

  py coz-olc.py --olcek 0.1     ~49 kisi   -- bir kac dakika
  py coz-olc.py --olcek 0.3     ~150 kisi
  py coz-olc.py                 500 kisi   -- COK uzun, bellek yiyor
  py coz-olc.py --doluluk 0.85  bolluk seti (varsayilan 0.95)

  ⚠ TAM OLCEK ICIN UYARI (28 Eylul)
    Bulut makinesinde model kurma 117 saniye olculdu ve ben bunu "beklenen
    ~2 dakika" diye yazdim. Mustafa'nin makinesinde 10 dakikada bitmedi.
    Ders: bir makinede olculen sure baska makinede TAHMIN degildir.

    968 bin degiskenlik model birkac GB tutar; makine takasa duserse
    onlarca kat yavaslar. Kucuk olcekle basla, buyuterek ilerle --
    her adimda sure YAZILIR, boylece nerede patladigi gorulur.

NE OLCER
  1. model kurma suresi ve buyuklugu
  2. cozum suresi ve durum
  3. cozulduyse: dogrulayicidan gecen plan kac sert ihlal veriyor

SONUC NEREYE YAZILIR
  `olcum-sonucu-<doluluk>.json` -- ayni klasore. Bir sonraki oturum okuyabilir.
"""

import io
import json
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI, os.path.abspath(BURASI)):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.model import Model                                # noqa: E402
from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

AZAMI_SANIYE = int(sys.argv[sys.argv.index("--saniye") + 1]) \
    if "--saniye" in sys.argv else 900
OLCEK = float(sys.argv[sys.argv.index("--olcek") + 1]) \
    if "--olcek" in sys.argv else 1.0
DOLULUK = float(sys.argv[sys.argv.index("--doluluk") + 1]) \
    if "--doluluk" in sys.argv else 0.95


def yaz(d):
    ad = ("olcum-sonucu-%d.json" % round(DOLULUK * 100) if OLCEK == 1.0
          else "olcum-sonucu-%g-%d.json" % (OLCEK, round(DOLULUK * 100)))
    with io.open(os.path.join(BURASI, ad), "w",
                 encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))


def main():
    # ⚠ 29 Eylul: iki set var (%85 ve %95). Varsayilan ZOR olan.
    #   `--doluluk 0.85` ile digeri kosulur.
    from uret_veri_seti import sahne_uret
    if OLCEK == 1.0:
        ad = "_sahne-S30-%d.json" % round(DOLULUK * 100)
        sahne = os.path.join(BURASI, "fikstur", ad)
        g = json.load(io.open(sahne, encoding="utf-8"))
        print("SAHNE : %s" % ad)
    else:
        g = sahne_uret(OLCEK, DOLULUK)
        print("OLCEK %.2f (doluluk %%%d) -- sahne bellekten uretildi"
              % (OLCEK, round(DOLULUK * 100)))
    sonuc = {"olcek": OLCEK, "doluluk": DOLULUK,
             "kisi": len(g["calisanlar"]),
             "sablon": len(g["vardiya_sablonlari"]),
             "hucre": len(g["talep"]),
             "kural": len(g["kurallar"]),
             "azami_saniye": AZAMI_SANIYE}
    print("SAHNE : %(kisi)d kisi, %(sablon)d sablon, %(hucre)d hucre, "
          "%(kural)d kural" % sonuc)
    yaz(sonuc)

    # ⚠ Model BIR KEZ kurulur. Ilk yazimda burada bir kez olcum icin,
    #   sonra `coz()` icinde bir kez daha kuruluyordu -- sureyi iki katina
    #   cikariyordu ve o sure "cozum suresi" diye raporlaniyordu.
    print("\n1/3  Model kuruluyor...")
    sys.stdout.flush()
    t0 = time.time()
    k = Model(g)
    k.kur()
    p = k.m.Proto()
    sonuc["kurma_sn"] = round(time.time() - t0, 1)
    sonuc["degisken"] = len(p.variables)
    sonuc["kisit"] = len(p.constraints)
    print("     %.0f sn  |  %d degisken  |  %d kisit"
          % (sonuc["kurma_sn"], sonuc["degisken"], sonuc["kisit"]))
    yaz(sonuc)

    print("\n2/3  Cozuluyor... (en fazla %d sn)" % AZAMI_SANIYE)
    sys.stdout.flush()
    t1 = time.time()
    try:
        c = coz(g, {"azami_saniye": AZAMI_SANIYE})
        sonuc["cozum_sn"] = round(time.time() - t1, 1)
        sonuc["durum"] = c.get("durum")
        sonuc["atama"] = len(c.get("atamalar") or [])
        sonuc["metrikler"] = c.get("metrikler")
    except Exception as e:
        sonuc["cozum_sn"] = round(time.time() - t1, 1)
        sonuc["durum"] = "ISTISNA"
        sonuc["hata"] = str(e)[:400]
        print("     ISTISNA: %s" % sonuc["hata"])
        yaz(sonuc)
        return
    # Cozucunun KENDI istatistikleri de kaydedilir: hangi yoldan gelindigi
    # (iki asama), neden durdugu (butce mi durgunluk mu), optimuma uzaklik.
    # Bunlar olmadan "964 saniye surdu" cumlesi hicbir sey anlatmiyor.
    ist = c.get("cozum_istatistikleri") or {}
    for k in ("durma_sebebi", "iki_asama", "cozum_sayisi", "amac_degeri",
              "model_kurma_sn", "ilk_asama_sn", "ana_asama_butce_sn"):
        if k in ist:
            sonuc[k] = ist[k]
    print("     %.0f sn  |  durum: %s  |  %d atama"
          % (sonuc["cozum_sn"], sonuc["durum"], sonuc["atama"]))
    print("     durma: %-14s iki asama: %-6s optimuma uzaklik: %s"
          % (ist.get("durma_sebebi"), ist.get("iki_asama"),
             (c.get("metrikler") or {}).get("optimuma_uzaklik_yuzde")))
    # T-59 (30 Eylul aksami): sure uc kaleme ayrildi. Birinci asama +
    # ana asama verilen butceyi GECMEMELI; model kurma ayri kalem.
    print("     model kurma %s sn · birinci asama %s sn · ana asamaya verilen %s sn"
          % (ist.get("model_kurma_sn"), ist.get("ilk_asama_sn"),
             ist.get("ana_asama_butce_sn")))
    yaz(sonuc)

    if sonuc["durum"] != "cozuldu":
        # ⚠ TESHIS HER ZAMAN YAZILIR.
        #   Bu betigin ilk iki halinde yazilmiyordu ve Mustafa iki kez
        #   "cozumsuz" gorup hicbir sebep goremedi -- biri 292 saniye
        #   bekledikten sonra. Motorun teshisi ikisinde de TAM YERINDEYDI;
        #   gizleyen sey bu betikti.
        t = c.get("teshis") or {}
        sonuc["teshis"] = t
        print("\n3/3  Plan uretilmedi. MOTORUN TESHISI:")
        print("     kapsam      : %s" % t.get("kapsam"))
        if t.get("hucre"):
            h = t["hucre"]
            print("     hucre       : ekip %s, gun %s, saat %s"
                  % (h.get("ekip"), h.get("gun"), h.get("saat")))
        print("     gereken     : %s   mumkun: %s"
              % (t.get("gereken"), t.get("mumkun")))
        for k in (t.get("engelleyen_kurallar") or []):
            print("     engelleyen  : %-22s %s"
                  % (k.get("kod"), k.get("gerekce", "")))
        en_iyi = c.get("en_iyi_plan") or {}
        if en_iyi:
            print("     en iyi plan : var=%s %s"
                  % (en_iyi.get("var"), en_iyi.get("sebep", "")))
        for n in (c.get("uygulanmayan_notlar") or [])[:5]:
            print("     not         : %s" % n)
        yaz(sonuc)
        return

    print("\n3/3  Dogrulaniyor...")
    t2 = time.time()
    r = degerlendir(g, c["atamalar"])
    sayi = {}
    for i in r.get("ihlaller", []):
        sayi[i["kural"]] = sayi.get(i["kural"], 0) + 1
    sonuc["dogrulama_sn"] = round(time.time() - t2, 1)
    sonuc["ihlal"] = sayi
    sonuc["sert_ihlal"] = sum(1 for i in r.get("ihlaller", [])
                              if i.get("agirlik") == "SERT")
    # ⚠ YAYIN KARARI `yayin_kapisi` ICINDE, en ustte DEGIL.
    #   Ilk yazimda `r.get("yayinlanabilir")` diyordum ve hep None
    #   geliyordu -- Mustafa hakli olarak "yayinlanamaz mi, neden?" diye
    #   sordu. Motor yayinlanabilir diyordu; gostermeyen bu betikti.
    kapi = r.get("yayin_kapisi") or {}
    sonuc["yayinlanabilir"] = kapi.get("yayinlanabilir")
    sonuc["engelleyen"] = len(kapi.get("engelleyen_ihlaller") or [])
    sonuc["kabul_bekleyen"] = len(kapi.get("kabul_bekleyen_ihlaller") or [])
    print("     %.0f sn  |  sert ihlal: %d  |  YAYINLANABILIR: %s"
          % (sonuc["dogrulama_sn"], sonuc["sert_ihlal"],
             sonuc["yayinlanabilir"]))
    if sonuc["engelleyen"] or sonuc["kabul_bekleyen"]:
        print("     engelleyen: %d   yonetici kabulu bekleyen: %d"
              % (sonuc["engelleyen"], sonuc["kabul_bekleyen"]))
    if sayi:
        print("\n     ihlal dagilimi:")
        for kod, n in sorted(sayi.items(), key=lambda x: -x[1]):
            print("       %-26s %d" % (kod, n))
    yaz(sonuc)

    print("\nTOPLAM: %.0f sn" % (time.time() - t0))
    print("Sonuc yazildi: %s" % ("olcum-sonucu-%d.json" % round(DOLULUK * 100)
                                 if OLCEK == 1.0 else
                                 "olcum-sonucu-%g-%d.json" % (OLCEK, round(DOLULUK * 100))))


if __name__ == "__main__":
    main()
