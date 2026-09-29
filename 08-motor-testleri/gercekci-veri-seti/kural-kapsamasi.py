# -*- coding: utf-8 -*-
"""
KURAL KAPSAMASI OLCUMU  --  "kullanmadigimiz hicbir kural olmamali"

NEDEN VAR (Mustafa, 28 Eylul)
  > "Kullanmadigimiz hic bir kural veya kriter vs olmamali. Her sey bu data
  >  setinde test edilebilecek sekilde tanimli olmali. Ancak bu sekilde
  >  dogru test sonuclari elde edebiliriz."

  Bu dosya o cumleyi bir IDDIA olmaktan cikarip OLCUME cevirir. Kural
  listesini elle yazmaz -- kayittan okur, calistirir, ve her kural icin
  UC AYRI SEYI ayirir:

      CALISTI + IHLAL BULDU   kural gercekten sinandi
      CALISTI + TEMIZ         kural calisti ama veri onu zorlamadi
                              -> "yesil" burada YANILTICIDIR
      HIC CALISMADI           govdesi yok, ya da girdi onu tetiklemiyor

  Ikinci satir en onemlisi. Bir kuralin ihlal yazmamasi iki ayri sey
  demek olabilir: "plan temiz" ya da "bu kural hic zorlanmadi". Ayni
  raporda ayni renkte gorunurler; bu olcum onlari ayirir.

KULLANIM
  py kural-kapsamasi.py                 -> fiksturdeki sahne uzerinde
  py kural-kapsamasi.py --plan X.json   -> hazir bir plan dosyasiyla
"""

import io
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402


def _bul_sablon(g, kimlik):
    for t in g["vardiya_sablonlari"]:
        if t["id"] == kimlik:
            return t
    return None


def kaba_plan(g):
    """Hizli, iyimser bir plan -- cozucu CALISTIRMADAN.

    Amac en iyi plani bulmak DEGIL, dogrulayiciyi 350 kisilik bir girdiyle
    gercekten calistirmak. Bilerek KUSURLU: kurallarin ihlal bulabilmesi
    icin plan gercekci olmali ama kusursuz olmamali.
    """
    sablon = {}
    for t in g["vardiya_sablonlari"]:
        sablon.setdefault(t.get("ekip"), []).append(t)
    politika = {}
    for t in g["vardiya_sablonlari"]:
        politika[t["id"]] = t.get("mola_politikasi") or []

    atamalar = []
    # KILITLI atamalar once konur: kaba plan bunlari yok sayarsa
    # KILIT_UYUMU temel planda zaten kirmizi olur ve o kural icin hicbir
    # vaka bir sey kanitlayamaz (28 Eylul'de boyle oldu).
    kilitli = {}
    for k in (g.get("kilitler") or []):
        t0 = _bul_sablon(g, k.get("sablon"))
        if not t0:
            continue
        kilitli.setdefault(k["calisan"], set()).add(k["gun"])
        atamalar.append({"calisan": k["calisan"],
                         "ekip": k.get("ekip") or t0.get("ekip"),
                         "sablon": t0["id"], "gun": k["gun"],
                         "bas": t0["bas"], "bit": t0["bit"], "molalar": []})

    for i, c in enumerate(g["calisanlar"]):
        if c.get("aktif") is False:
            continue
        ekip = (c.get("ekipler") or [None])[0]
        uygun = sablon.get(ekip) or []
        if not uygun:
            continue
        izinli = {z["gun"] for z in (c.get("izinler") or [])
                  if z.get("durum", "onayli") == "onayli"}
        kapali = {u["gun"] for u in (c.get("uygunluk") or [])
                  if u.get("tip") == "uygun_degil"}
        pt = c["sozlesme"].get("tip") == "part_time"
        gun_sayisi = 3 if pt else 5
        kondu = len(kilitli.get(c["id"]) or ())
        for gun in range(7):
            if (kondu >= gun_sayisi or gun in izinli or gun in kapali
                    or gun in (kilitli.get(c["id"]) or ())):
                continue
            t = uygun[(i + gun) % len(uygun)]
            if gun not in t.get("gunler", list(range(7))):
                continue
            a = {"calisan": c["id"], "ekip": ekip, "sablon": t["id"],
                 "gun": gun, "bas": t["bas"], "bit": t["bit"], "molalar": []}
            # Politikadan mola uret -- ceyrek izgarada (K-34)
            an = t["bas"] + 3
            for satir in politika[t["id"]]:
                for _ in range(satir.get("adet", 1)):
                    sure = satir.get("dakika", 0) / 60.0
                    if an + sure <= t["bit"]:
                        a["molalar"].append({"bas": an, "bit": an + sure,
                                             "tip": satir.get("tip")})
                        an += sure + 0.75
            atamalar.append(a)
            kondu += 1
    return atamalar


def olc(g, atamalar):
    """Her kural icin: calisti mi, ihlal buldu mu."""
    rapor = degerlendir(g, atamalar)
    ihlal_sayisi = {}
    for i in rapor.get("ihlaller", []):
        ihlal_sayisi[i["kural"]] = ihlal_sayisi.get(i["kural"], 0) + 1

    govdeli = set(K.KAYIT)
    tanimli = [k["kod"] for k in g.get("kurallar", []) if k.get("aktif", True)]

    satirlar = []
    for kod in sorted(tanimli):
        if kod not in govdeli:
            durum = "GOVDE YOK"
        elif ihlal_sayisi.get(kod):
            durum = "SINANDI"
        else:
            durum = "TEMIZ (zorlanmadi?)"
        satirlar.append((kod, durum, ihlal_sayisi.get(kod, 0)))
    return rapor, satirlar, govdeli, set(tanimli)


def yaz(g, atamalar):
    rapor, satirlar, govdeli, tanimli = olc(g, atamalar)

    print("SAHNE : %d calisan, %d sablon, %d talep hucresi, %d kural tanimli"
          % (len(g["calisanlar"]), len(g["vardiya_sablonlari"]),
             len(g["talep"]), len(g["kurallar"])))
    print("PLAN  : %d atama, %d mola blogu"
          % (len(atamalar), sum(len(a.get("molalar") or []) for a in atamalar)))
    print()
    print("%-28s %-22s %s" % ("KURAL", "DURUM", "ihlal"))
    print("-" * 62)
    for kod, durum, n in satirlar:
        print("%-28s %-22s %s" % (kod, durum, n or ""))

    sinandi = [k for k, d, _ in satirlar if d == "SINANDI"]
    temiz = [k for k, d, _ in satirlar if d.startswith("TEMIZ")]
    govdesiz = [k for k, d, _ in satirlar if d == "GOVDE YOK"]

    print("-" * 62)
    print("SINANDI            : %2d  (kural gercekten zorlandi)" % len(sinandi))
    print("TEMIZ              : %2d  (calisti ama veri zorlamadi)" % len(temiz))
    print("GOVDE YOK          : %2d  (uygulanmayan_kurallar kanalinin isi)" % len(govdesiz))
    print()
    if temiz:
        print("⚠ BU KURALLAR ICIN 'YESIL' BIR SEY KANITLAMAZ:")
        for k in temiz:
            print("    %s" % k)
        print("  Veri seti bunlari ihlal ettirecek bir durum icermiyor.")
    eksik = govdeli - tanimli
    if eksik:
        print()
        print("⚠ GOVDESI VAR AMA SAHNEDE TANIMLI DEGIL (hic calismadi):")
        for k in sorted(eksik):
            print("    %s" % k)
    return rapor


if __name__ == "__main__":
    sahne = os.path.join(BURASI, "fikstur", "_sahne-S30-95.json")
    g = json.load(io.open(sahne, encoding="utf-8"))
    if "--plan" in sys.argv:
        atamalar = json.load(io.open(sys.argv[sys.argv.index("--plan") + 1],
                                     encoding="utf-8"))
        if isinstance(atamalar, dict):
            atamalar = atamalar.get("atamalar") or []
    else:
        atamalar = kaba_plan(g)
    yaz(g, atamalar)
