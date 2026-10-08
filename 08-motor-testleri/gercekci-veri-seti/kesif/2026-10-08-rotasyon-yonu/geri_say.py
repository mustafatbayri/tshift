"""VARDIYA_ROTASYON_YONU kesfi (8 Ekim 2026): urun yolunun plani kucuk olcekte
cozulur, art arda CALISMA gunlerinde baslangic saati geriye kayan gecisler
sayilir (dairesel fark: 24 saatlik cemberde (-12, 12]; eksi = geri).
Sayilar kucuk olcek -- kaliteyi degil yapiyi gosterir (geri gecis sikligi,
buyuklugu). Kullanim: py geri_say.py [olcek=0.1] [saniye=40]
Kayit: geri-<olcek>.json (bu klasore). Okuma: 02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md bolum 5."""
import io, json, os, sys, time, collections
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))   # depo koku
sys.path.insert(0, os.path.join(KOK, "09-motor"))
sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
import importlib
C = importlib.import_module("cozucu.coz")
from uret_veri_seti import sahne_uret

OLCEK = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
SANIYE = float(sys.argv[2]) if len(sys.argv) > 2 else 40
g = sahne_uret(OLCEK, 0.95)
t0 = time.time()
sonuc = C.coz(g, dict(C.VARSAYILAN, azami_saniye=SANIYE, isci_sayisi=2))
print("kisi", len(g["calisanlar"]), "durum", sonuc.get("durum"), "amac", sonuc.get("amac_degeri"),
      "sure %.0f sn" % (time.time() - t0))
atamalar = sonuc.get("atamalar") or sonuc.get("plan", {}).get("atamalar") or []
print("atama", len(atamalar), "ornek", atamalar[0] if atamalar else None)
# kisi -> gun -> baslangic
bas = collections.defaultdict(dict)
for a in atamalar:
    bas[a["calisan"]][a["gun"]] = a["bas"]
geri = []; ileri = []; ayni = 0; cift = 0
for k, gunler in bas.items():
    for d in sorted(gunler):
        if d + 1 in gunler:
            cift += 1
            s1, s2 = gunler[d], gunler[d + 1]
            fark = s2 - s1
            # dairesel: (-12, 12]
            if fark > 12: fark -= 24
            if fark <= -12: fark += 24
            if fark < 0: geri.append((-fark, s1, s2))
            elif fark > 0: ileri.append((fark, s1, s2))
            else: ayni += 1
print("art arda calisma gunu cifti", cift, "| ileri", len(ileri), "| ayni", ayni, "| geri", len(geri))
if geri:
    buy = collections.Counter(round(x[0], 2) for x in geri)
    print("geri buyuklukleri (saat: adet)", sorted(buy.items()))
    print("geri toplam saat %.2f, ortalama %.2f" % (sum(x[0] for x in geri), sum(x[0] for x in geri) / len(geri)))
    print("en sik geri gecisler", collections.Counter((x[1], x[2]) for x in geri).most_common(8))
if ileri:
    buy = collections.Counter(round(x[0], 2) for x in ileri)
    print("ileri buyuklukleri", sorted(buy.items())[:12])
json.dump({"olcek": OLCEK, "saniye": SANIYE, "kisi": len(g["calisanlar"]), "durum": sonuc.get("durum"),
           "amac": sonuc.get("amac_degeri"), "cift": cift, "ileri": len(ileri), "ayni": ayni,
           "geri": [list(x) for x in geri]}, io.open(os.path.join(BURASI, "geri-%s.json" % OLCEK), "w", encoding="utf-8"), indent=1)
