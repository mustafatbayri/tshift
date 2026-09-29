# -*- coding: utf-8 -*-
"""
CEKIRDEK / ISCI SAYISI OLCUMU  --  "daha guclu makine ise yarar mi?"

⚠ NEDEN YAZILDI (Mustafa, 29 Eylul)
    > "Bu 15 dk suren kosuyu daha hizli bir makinede kossak kisa surer mi?
    >  Cloud ortamdan ciddi kapasiteli bir sunucu alsam ise yarar mi?"

  Bu soruya tahminle cevap vermek yanlis olurdu. 28 Eylul'de tam bunu
  denedim: bir makinede olculen 117 saniyeyi "beklenen ~2 dakika" diye
  yazdim, Mustafa'nin makinesinde 10 dakikada bitmedi. Bir makinede
  olculen sure, baska makinede TAHMIN DEGILDIR.

  Bu betik tahmin etmez, OLCER. Sunucu karari sayilara dayansin diye var.

NE OLCER
  Ayni sahneyi, AYNI SURE butcesiyle, farkli isci sayilariyla coz. Sonra
  hangi isci sayisinin daha iyi plan urettigine bak.

  Cikan tablo iki soruyu birden cevaplar:
    1. Bu makinede kac isci en iyisi  -> motor zaten bunu otomatik secer
    2. Isci artinca plan iyilesiyor mu -> cevap "evet" ise cekirdek almak
                                          ise yarar, "hayir" ise yaramaz

⚠ ERKEN DURMA KAPALI -- olcumu bozar
  Motor normalde "yeter" deyip erken durur (K-28). Olcumde bu felaket olur:
  bir kosu 30 saniyede, digeri 120 saniyede durursa karsilastirdigimiz sey
  isci sayisi degil, SURE olur.

    hedef_bosluk = 0      optimuma yaklasinca durma
    durgunluk    = 0      iyilesme durunca durma

  Boylece her satir TAM OLARAK ayni sureyi harcar ve aradaki fark yalnizca
  isci sayisindan gelir.

⚠ IKI ASAMA VARSAYILAN OLARAK ACIK -- ilk yazimda KAPALIYDI, HATAYDI
  Ilk yazimda "ikinci bir kurulum suresi eklemesin" diye kapatilmisti. Ama
  iki asama her satirda AYNI sekilde calisir; yani karsilastirmayi bozmaz.
  Kapatmanin tek sonucu, urunun HIC KULLANMADIGI bir ayari olcmek oldu.

  Farki 350 kiside sayiyla gorulmustu ve fark edilmemisti:

      28 Eylul, 900 sn, iki asama ACIK  (urunun gercek ayari) -> %10,0
      29 Eylul, 360 sn, iki asama KAPALI                      -> %42,4

  Iki degisken birden degisti (sure ve iki asama), o yuzden hangisinin ne
  kadar payi oldugu hala ayrilmis degil. Artik varsayilan ACIK: rakamlar
  urunun gercekten urettigi rakamlar olsun. `--iki-asama kapali` ile eski
  davranis geri gelir.

⚠ AMAC DEGERI: KUCUK OLAN IYIDIR
  Ceza toplamidir. 1.010.039 ile 21.905 arasindaki fark "biraz daha iyi"
  degil, "bambaska bir plan" demektir.

⚠ "UZAKLIK%" TEK BASINA YANILTIR -- ALT SINIRA DA BAK
      uzaklik = (amac - alt sinir) / amac
  Bu oran IKI sekilde duser ve ikisi COK farkli sey:
      PLAN duzeldi   -> amac dustu       (sahada daha iyi vardiya)
      KANIT guclendi -> alt sinir cikti  (ayni plan, daha az suphe)
  350 kisilik sahnede olculdu: alt sinir 120 sn'den sonra neredeyse SABIT
  (~68.000). Yani orani dusuren sey kanit degil, planin kendisi.

⚠ "HAZIRLIK" SUTUNU NE ICERIR
  Model kurma + (iki asama acikken) BIRINCI ASAMA. Ikisi ayrilmadi; iki
  asama acikken bu sutunun buyumesi normaldir (350 kiside 27 sn -> 60 sn).
  Verilen sure butcesi yalniz IKINCI asama icindir.

⚠ PLAN URETEMEYEN SATIR COK UZUN SURER -- 29 Eylul'de olculdu
  Butce icinde plan bulunamazsa motor cozumsuzluk teshisi koyar: her sert
  kurali tek tek gevsetip yeniden cozer (kural basina 10 sn'ye kadar) ve
  ustune bir "en iyi plan" arar. Olculdu:

      45 saniyelik butce  ->  satir TOPLAM 470 saniye surdu

  Yani plan uretemeyen bir satirin bedeli butcesinin on kati olabilir.
  Tabloda "cozumsuz" goruyorsan ve bekleme uzadiysa sebep budur; o isci
  sayisini listeden cikar ya da --saniye degerini artir.

⚠ TEK KOSU OLCUM DEGILDIR -- `--tekrar` KULLAN
  Cozucu ayni girdiye her seferinde ayni plani vermez: isciler paralel
  calisir ve hangisinin once iyi bir plan buldugu her kosuda degisir.
  28 Eylul'de olculdu: ayni girdi, ayni 25 saniye -> 21.905 ve 22.715.

  Yani iki satir arasindaki kucuk fark, isci sayisindan degil ZARDAN
  geliyor olabilir. `--tekrar 3` her satiri uc kez kosar ve SATIR ICI
  yayilmayi gosterir. Satir ici yayilma, satirlar arasi farktan buyukse
  bu sahne o makinede ayrim yapmiyordur -- daha zor bir sahne gerekir.

⚠ MODEL KURMA COK CEKIRDEKTEN FAYDALANMAZ
  Tablodaki "kurma" sutunu tek cekirdekte kosan Python suresidir. Cekirdek
  eklemek onu KISALTMAZ; onu kisaltan sey saat hizidir. Sunucu kararinda
  ikisi ayri ayri dusunulmeli: arama cekirdek ister, kurma hiz ister.

IKI MAKINEDE OLCULEN (29 Eylul, 0.1 olcek, birer kosu)

  2 cekirdek, 45 sn butce                6 cekirdek, 60 sn butce
      isci   durum      uzaklik%             isci   durum     uzaklik%
      1      cozumsuz      -                 2      cozuldu     3,1
      2      cozuldu       7,0               4      cozuldu     2,9
      4      cozuldu      24,2               8      cozuldu     2,3
      8      cozuldu      23,6               16     cozuldu     1,4

  ⚠ IKI TABLO AYNI SEYI SOYLEMIYOR. Dar makinede fark BUYUK (7,0 -> 23,6).
    Genis makinede butun satirlar optimuma yakin ve aradaki fark, tek
    kosunun zar payindan kucuk. Yani: isci sayisi ancak makine DARSA
    onemli. Genis makinede bu sahne soruya cevap vermiyor -- daha buyuk
    olcek ve `--tekrar` gerekir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti

  py cekirdek-olc.py                        0.3 olcek, isci basina 120 sn
  py cekirdek-olc.py --saniye 60            daha kisa
  py cekirdek-olc.py --olcek 1.0 --saniye 300   tam olcek (COK uzun)
  py cekirdek-olc.py --isci 1,2,4,8,16      denenecek sayilar
  py cekirdek-olc.py --tekrar 3             her satir uc kez (zar payi gorunur)
  py cekirdek-olc.py --iki-asama kapali     iki asamasiz (ESKI davranis)

  TOPLAM SURE = saniye x isci adedi x tekrar  (+ her kosu icin model kurma)
  Varsayilanla: 120 x 4 x 1 = 8 dakika, artı kurulumlar.

SONUC NEREYE YAZILIR
  `cekirdek-olcumu.json` -- ayni klasore.
"""

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
from cozucu.model import cekirdek_sayisi                      # noqa: E402
from uret_veri_seti import sahne_uret                         # noqa: E402


def _arg(ad, varsayilan):
    return sys.argv[sys.argv.index(ad) + 1] if ad in sys.argv else varsayilan


OLCEK = float(_arg("--olcek", 0.3))
SANIYE = int(_arg("--saniye", 120))
ISCILER = [int(x) for x in str(_arg("--isci", "1,2,4,8")).split(",") if x.strip()]
TEKRAR = max(1, int(_arg("--tekrar", 1)))
# Varsayilan ACIK: urunun gercekten kullandigi ayar. Bkz. baslikta
# "IKI ASAMA VARSAYILAN OLARAK ACIK".
IKI_ASAMA = str(_arg("--iki-asama", "acik")).lower() != "kapali"


def _ortanca(degerler):
    s = sorted(degerler)
    n = len(s)
    return float(s[n // 2]) if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def yaz(d):
    with io.open(os.path.join(BURASI, "cekirdek-olcumu.json"), "w",
                 encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))


def main():
    cekirdek = cekirdek_sayisi()
    print("MAKINE  : %d cekirdek kullanilabilir" % cekirdek)
    print("SAHNE   : olcek %.2f" % OLCEK)
    print("BUTCE   : isci basina %d saniye, erken durma KAPALI" % SANIYE)
    print("IKI ASAMA: %s%s"
          % ("ACIK (urunun gercek ayari)" if IKI_ASAMA else "KAPALI",
             "" if IKI_ASAMA else "  ⚠ urun boyle kosmuyor"))
    print("DENENEN : %s isci" % ", ".join(str(i) for i in ISCILER))
    print("TEKRAR  : her satir %d kez" % TEKRAR)
    if TEKRAR < 2:
        print("          ⚠ tek kosu olcum degildir -- `--tekrar 3` onerilir")
    print("TAHMINI TOPLAM: en az %d dakika\n"
          % max(1, SANIYE * len(ISCILER) * TEKRAR // 60))
    sys.stdout.flush()

    g = sahne_uret(OLCEK)
    rapor = {"cekirdek": cekirdek, "olcek": OLCEK, "saniye": SANIYE,
             "tekrar": TEKRAR, "iki_asama": IKI_ASAMA,
             "kisi": len(g["calisanlar"]), "kosular": []}
    yaz(rapor)

    print("%-5s %-5s %-9s %11s %11s %8s %6s %8s"
          % ("isci", "kosu", "durum", "amac", "alt sinir", "uzaklik%",
             "cozum", "hazirlik"))
    print("-" * 72)

    for n in ISCILER:
        for t in range(1, TEKRAR + 1):
            t0 = time.time()
            a = {"azami_saniye": SANIYE,
                 "isci_sayisi": n,
                 # Erken durma olcumu bozar -- bkz. baslik.
                 "hedef_bosluk": 0.0,
                 "durgunluk_saniye": 0}
            if not IKI_ASAMA:
                a["iki_asama_esigi"] = 10 ** 9
            c = coz(g, a)
            ist = c.get("cozum_istatistikleri") or {}
            met = c.get("metrikler") or {}
            toplam = round(time.time() - t0, 1)
            cozum_sn = ist.get("cozum_suresi_sn") or 0
            satir = {
                "isci": n, "kosu": t,
                "durum": c.get("durum"),
                "amac": ist.get("amac_degeri"),
                # Oranin diger tarafi: optimum bundan iyi OLAMAZ.
                "alt_sinir": ist.get("alt_sinir"),
                "uzaklik_yuzde": met.get("optimuma_uzaklik_yuzde"),
                "cozum_sayisi": ist.get("cozum_sayisi"),
                "iki_asama": ist.get("iki_asama"),
                "toplam_sn": toplam,
                "cozum_sn": cozum_sn,
                # Model kurma + (iki asama acikken) birinci asama. Ikisi
                # ayrilmadi; tek cekirdekte kosan kisim buranin icinde.
                "hazirlik_sn": round(max(0.0, toplam - cozum_sn), 1),
            }
            rapor["kosular"].append(satir)
            print("%-5d %-5s %-9s %11s %11s %8s %6s %7.0fs"
                  % (n, "%d/%d" % (t, TEKRAR), satir["durum"],
                     "-" if satir["amac"] is None else "%.0f" % satir["amac"],
                     "-" if satir["alt_sinir"] is None
                     else "%.0f" % satir["alt_sinir"],
                     "-" if satir["uzaklik_yuzde"] is None
                     else "%.1f" % satir["uzaklik_yuzde"],
                     satir["cozum_sayisi"], satir["hazirlik_sn"]))
            sys.stdout.flush()
            yaz(rapor)

    # --------------------------------------------------------------
    # Ozet -- tabloyu okumayi kolaylastirir, KARARI vermez
    # --------------------------------------------------------------
    print("-" * 72)
    gruplar = {}
    sinirlar = {}
    for k in rapor["kosular"]:
        if k["amac"] is not None:
            gruplar.setdefault(k["isci"], []).append(k["amac"])
            if k["alt_sinir"] is not None:
                sinirlar.setdefault(k["isci"], []).append(k["alt_sinir"])
    if not gruplar:
        print("\nHICBIR kosu plan uretmedi. Butce cok kisa ya da sahne cok")
        print("buyuk. --saniye degerini artir ya da --olcek degerini dusur.")
        yaz(rapor)
        return

    ozet = []
    for n in ISCILER:
        v = gruplar.get(n)
        if not v:
            continue
        sn = sinirlar.get(n)
        ozet.append({"isci": n, "en_iyi": min(v), "ortanca": _ortanca(v),
                     "en_kotu": max(v), "yayilma": max(v) - min(v),
                     "alt_sinir_ortanca": _ortanca(sn) if sn else None,
                     "kosu": len(v)})
    rapor["ozet"] = ozet

    print("\nOZET (amac: KUCUK olan iyi)")
    print("%-6s %12s %12s %12s %10s %12s"
          % ("isci", "en iyi", "ortanca", "en kotu", "yayilma", "alt sinir"))
    for s in ozet:
        print("%-6d %12.0f %12.0f %12.0f %10.0f %12s"
              % (s["isci"], s["en_iyi"], s["ortanca"], s["en_kotu"],
                 s["yayilma"],
                 "-" if s["alt_sinir_ortanca"] is None
                 else "%.0f" % s["alt_sinir_ortanca"]))

    # ⚠ Alt sinir butun satirlarda ayni cikiyorsa, satirlar arasindaki
    #   uzaklik% farki tamamen PLANDAN geliyor demektir -- kanit degismemis.
    sinir_degerleri = [s["alt_sinir_ortanca"] for s in ozet
                       if s["alt_sinir_ortanca"] is not None]
    if len(sinir_degerleri) > 1 and min(sinir_degerleri) > 0:
        oynama = (max(sinir_degerleri) - min(sinir_degerleri)) \
            / float(min(sinir_degerleri))
        if oynama < 0.05:
            print("\n  Alt sinir butun satirlarda ayni (%%%.1f oynama):"
                  % (100 * oynama))
            print("  aradaki uzaklik farki KANITTAN degil, PLANDAN geliyor.")

    # --------------------------------------------------------------
    # ⚠ ZAR PAYI KONTROLU -- bu betigin en onemli parcasi
    #
    #   Satirlar arasi fark, SATIR ICI yayilmadan kucukse tablo isci
    #   sayisini degil zari olcmustur. 29 Eylul'de tam bu tuzaga
    #   dusuldu: 2 cekirdekli makinede fark buyuktu (%7 -> %24) ve
    #   "fazla isci zararlidir" diye yazildi; 6 cekirdekli makinede
    #   butun satirlar %1,4-%3,1 arasinda cikti -- yani hicbir sey.
    # --------------------------------------------------------------
    en_iyi_s = min(ozet, key=lambda s: s["ortanca"])
    en_kotu_s = max(ozet, key=lambda s: s["ortanca"])
    fark = en_kotu_s["ortanca"] - en_iyi_s["ortanca"]
    en_buyuk_yayilma = max(s["yayilma"] for s in ozet)
    rapor["en_iyi_isci"] = en_iyi_s["isci"]
    rapor["satirlar_arasi_fark"] = round(fark, 1)
    rapor["satir_ici_en_buyuk_yayilma"] = round(en_buyuk_yayilma, 1)

    print("\nSATIRLAR ARASI FARK : %.0f   (en iyi %d isci, en kotu %d isci)"
          % (fark, en_iyi_s["isci"], en_kotu_s["isci"]))
    print("SATIR ICI YAYILMA   : %.0f   (ayni ayarla kosular arasi zar payi)"
          % en_buyuk_yayilma)

    if TEKRAR < 2:
        rapor["karar"] = "olculemedi_tek_kosu"
        print("\n⚠ HER SATIR BIR KEZ KOSULDU -- bu tablo KARAR VERDIRMEZ.")
        print("  Cozucu ayni girdiye ayni plani vermez; satirlar arasindaki")
        print("  fark zardan geliyor olabilir. `--tekrar 3` ile yeniden kos.")
    elif fark <= en_buyuk_yayilma:
        rapor["karar"] = "sahne_ayrim_yapmiyor"
        print("\nBU SAHNE BU MAKINEDE AYRIM YAPMIYOR.")
        print("  Satirlar arasi fark, ayni ayarin kendi zar payindan kucuk.")
        print("  Yani isci sayisi burada belirleyici degil -- makine bu")
        print("  sahne icin zaten yeterli. Sunucu sorusuna cevap icin DAHA")
        print("  ZOR bir sahne gerekir: --olcek 1.0 (ya da 0.5) dene.")
    else:
        rapor["karar"] = "isci_sayisi_belirleyici"
        print("\nISCI SAYISI BU SAHNEDE BELIRLEYICI.")
        print("  En iyi: %d isci. Makinede %d cekirdek var."
              % (en_iyi_s["isci"], cekirdek))
        if en_iyi_s["isci"] > cekirdek:
            print("  Cekirdekten FAZLA isci daha iyi cikti: cekirdek eklemek")
            print("  bu sahnede ise yarayabilir.")
        elif en_iyi_s["isci"] < cekirdek:
            print("  Cekirdekten AZ isci daha iyi cikti: sinir cekirdek degil,")
            print("  daha buyuk sunucu bu sahnede plani iyilestirmez.")

    # Sunucu kararinin ikinci yarisi -- cekirdek bunu HIC hizlandirmaz.
    hazirliklar = [k["hazirlik_sn"] for k in rapor["kosular"] if k["hazirlik_sn"]]
    if hazirliklar:
        print("\nHAZIRLIK : ortalama %.0f sn%s"
              % (sum(hazirliklar) / float(len(hazirliklar)),
                 "  (model kurma + birinci asama)" if IKI_ASAMA
                 else "  (yalniz model kurma)"))
        print("  Model kurma TEK cekirdekte kosar; cekirdek eklemek onu")
        print("  kisaltmaz, onu kisaltan saat hizidir. Sunucu secerken arama")
        print("  (cekirdek) ile kurma (hiz) ayri ayri dusunulmeli.")

    print("\nSonuc yazildi: cekirdek-olcumu.json")
    yaz(rapor)


if __name__ == "__main__":
    main()
