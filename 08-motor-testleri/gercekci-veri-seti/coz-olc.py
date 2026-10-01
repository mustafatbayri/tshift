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
  py coz-olc.py --donmus        cozdukten sonra gun 0'i DONDURUP yeniden
                                planlar (K-54): motorun kendi gun 0 plani
                                `mevcut_plan` olur; gun 0 aynen kalmali,
                                sert ihlal 0, yayinlanabilir. Ikinci cozum
                                `--donmus-saniye` (varsayilan 300) alir.

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
DONMUS = "--donmus" in sys.argv
DONMUS_SANIYE = int(sys.argv[sys.argv.index("--donmus-saniye") + 1]) \
    if "--donmus-saniye" in sys.argv else 300


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

    # ⚠ Model BIR KEZ kurulur (1 Ekim): burada sayim icin kurulan model
    #   `coz()`a verilir; eskiden `coz()` bir kez daha kuruyordu -- tam
    #   olcekte 55-80 saniye bosa gidiyor ve "cozum suresi" icinde
    #   gorunuyordu (981 sn = 78 kurma + 900 arama + 3).
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
        c = coz(g, {"azami_saniye": AZAMI_SANIYE}, kuruldu=k)
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
              "model_kurma_sn", "ilk_asama_sn", "ana_asama_butce_sn",
              "ilk_cozum_sn"):
        if k in ist:
            sonuc[k] = ist[k]
    print("     %.0f sn  |  durum: %s  |  %d atama"
          % (sonuc["cozum_sn"], sonuc["durum"], sonuc["atama"]))
    print("     durma: %-14s iki asama: %-6s optimuma uzaklik: %s"
          % (ist.get("durma_sebebi"), ist.get("iki_asama"),
             (c.get("metrikler") or {}).get("optimuma_uzaklik_yuzde")))
    # T-59 (30 Eylul aksami): sure uc kaleme ayrildi. Birinci asama +
    # ana asama verilen butceyi GECMEMELI; model kurma ayri kalem.
    # K-48: model kurma AYRI kalem (yukaridaki 1/3 adiminin suresi), arama
    # butcesi = birinci asama + ana asama.
    print("     model kurma %s sn (butce DISI, K-48) · birinci asama %s sn · ana asamaya verilen %s sn"
          % (sonuc["kurma_sn"], ist.get("ilk_asama_sn"),
             ist.get("ana_asama_butce_sn")))
    # T-60 (1 Ekim): birinci asama plan bulamiyorsa ana asama ilk plani
    # kacinci saniyede buldu? Bu sayi olmadan "120 saniye yetmiyor" ile
    # "hic bulamiyor" ayrilamaz.
    print("     ana asamada ilk plan: %s sn" % ist.get("ilk_cozum_sn"))
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
    # K-54: donmus gune ait ihlal "olan oldu" -- sert sayaca girmez, ayri yazilir.
    sonuc["sert_ihlal"] = sum(1 for i in r.get("ihlaller", [])
                              if i.get("agirlik") == "SERT" and not i.get("gecmis"))
    sonuc["gecmis_sert_ihlal"] = sum(1 for i in r.get("ihlaller", [])
                                     if i.get("agirlik") == "SERT" and i.get("gecmis"))
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
    # SERT ihlallerin cumleleri ekrana ve dosyaya: 30 Eylul gecesi tam
    # olcekli kosu 1 sert ihlal (PART_TIME_LIMIT) verdi ve sebebi
    # arastirilamadi -- ne kisi ne saat kaydedilmisti (T-78).
    sertler = [i for i in r.get("ihlaller", [])
               if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    if sertler:
        print("\n     SERT ihlaller:")
        for i in sertler[:20]:
            print("       %s" % i.get("mesaj", i))
        sonuc["sert_ihlal_cumleleri"] = [i.get("mesaj", str(i)) for i in sertler]
    yaz(sonuc)
    # PLAN da yazilir: bir ihlalin sebebi ancak planla arastirilabilir.
    plan_yolu = os.path.join(BURASI, "olcum-plan-%d.json" % round(DOLULUK * 100)) \
        if OLCEK == 1.0 else os.path.join(BURASI, "olcum-plan-%s.json" % OLCEK)
    with io.open(plan_yolu, "w", encoding="utf-8") as f:
        json.dump({"atamalar": c["atamalar"], "ihlaller": r.get("ihlaller", []),
                   "uygulanmayan_notlar": c.get("uygulanmayan_notlar")},
                  f, ensure_ascii=False)
    print("     plan yazildi: %s" % os.path.basename(plan_yolu))

    if DONMUS:
        donmus_olc(g, c["atamalar"])

    print("\nTOPLAM: %.0f sn" % (time.time() - t0))
    print("Sonuc yazildi: %s" % ("olcum-sonucu-%d.json" % round(DOLULUK * 100)
                                 if OLCEK == 1.0 else
                                 "olcum-sonucu-%g-%d.json" % (OLCEK, round(DOLULUK * 100))))


def donmus_olc(g, plan):
    """4/4 -- gun 0 donmus, motorun kendi plani yayinlanmis plan (K-54).

    Gercek is akisi: hafta yayinlandi, pazartesi gecti, yonetici sali gunu
    plani yeniden kosturuyor. Gun 0 OLAN OLDU; motor onu aynen almali, kalan
    gunleri ona uyarak planlamali. Olculen: gun 0 degisti mi, model gecmisin
    kac kisitini dusurdu/kirpti, sert ihlal (gecmis haric), yayinlanabilir mi.
    """
    import copy
    print("\n4/4  Donmus gun yeniden planlamasi (gun 0 donmus, mevcut plan = 3/3'un plani)")
    g2 = copy.deepcopy(g)
    g2["donmus_gunler"] = [0]
    g2["mevcut_plan"] = copy.deepcopy(plan)
    t = time.time()
    k2 = Model(g2).kur()
    kurma = time.time() - t
    print("     model kurma %.0f sn  |  dusen kisit %d  |  kirpilan kisit %d"
          % (kurma, k2._donmus_dusen, k2._donmus_kirpilan))
    t = time.time()
    c2 = coz(g2, {"azami_saniye": DONMUS_SANIYE}, kuruldu=k2)
    sure = time.time() - t
    ist = c2.get("cozum_istatistikleri", {})
    print("     %.0f sn  |  durum: %s  |  %d atama  |  ipucu kullanildi: %s  |  ilk plan: %s sn"
          % (sure, c2.get("durum"), len(c2.get("atamalar") or []),
             ist.get("baslangic_plani_kullanildi"), ist.get("ilk_cozum_sn")))
    sonuc = {"donmus_gunler": [0], "kurma_sn": round(kurma, 1),
             "dusen_kisit": k2._donmus_dusen, "kirpilan_kisit": k2._donmus_kirpilan,
             "cozum_sn": round(sure, 1), "durum": c2.get("durum"),
             "notlar": [n for n in (c2.get("uygulanmayan_notlar") or []) if "K-54" in n]}
    if c2.get("durum") == "cozuldu":
        def gun0(atamalar):
            return sorted((a["calisan"], float(a["bas"]), float(a["bit"]))
                          for a in atamalar if a["gun"] == 0)
        ayni = gun0(plan) == gun0(c2["atamalar"])
        r2 = degerlendir(g2, c2["atamalar"])
        sert = [i for i in r2.get("ihlaller", []) if i.get("agirlik") == "SERT" and not i.get("gecmis")]
        gecmis = [i for i in r2.get("ihlaller", []) if i.get("gecmis")]
        kapi = r2.get("yayin_kapisi") or {}
        sonuc.update({"gun0_ayni": ayni, "sert_ihlal": len(sert),
                      "gecmis_ihlal": len(gecmis),
                      "donmus_gun_ihlali": sum(1 for i in sert if i["kural"] == "DONMUS_GUN"),
                      "yayinlanabilir": kapi.get("yayinlanabilir"),
                      "optimuma_uzaklik": (c2.get("metrikler") or {}).get("optimuma_uzaklik_yuzde")})
        print("     gun 0 AYNI mi: %s  |  sert ihlal: %d (DONMUS_GUN %d)  |  gecmis ihlal: %d  |  YAYINLANABILIR: %s"
              % (ayni, len(sert), sonuc["donmus_gun_ihlali"], len(gecmis), kapi.get("yayinlanabilir")))
        if sert:
            for i in sert[:10]:
                print("       %s" % i.get("mesaj", i))
    for n in sonuc["notlar"][:5]:
        print("     not: %s" % n)
    yol = os.path.join(BURASI, "olcum-donmus-%d.json" % round(DOLULUK * 100)) \
        if OLCEK == 1.0 else os.path.join(BURASI, "olcum-donmus-%g-%d.json" % (OLCEK, round(DOLULUK * 100)))
    with io.open(yol, "w", encoding="utf-8") as f:
        f.write(json.dumps(sonuc, ensure_ascii=False, indent=1))
    print("     donmus gun sonucu yazildi: %s" % os.path.basename(yol))


if __name__ == "__main__":
    main()
