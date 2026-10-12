# -*- coding: utf-8 -*-
"""Kaydedilmis 'once' planlarindan iki olcum (12 Ekim 04:30):

1. HEDEF_ASIMI'nin kimden geldigi: asim hucrelerinde atanan kisiler sozlesme
   tipine gore ayrilir. 'Batik' = tam zamanli (45 saat zaten odenmis, K-39);
   'saatlik' = yari zamanli / sezonluk / stajyer (saat basi odenir).
   Hucre basina saatlik ust sinir = min(asim, saatlik kisi sayisi).
2. Rotasyon gun tanimi: baslangic gunu (bugunku kod) / K-46 cogunluk (C) /
   dokunulan gunler (D, Mustafa 04:13) -- ayni planda hangi ciftler sayilir.
"""
import collections
import io
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor"))
sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
from dogrulayici import kurallar as K, zaman                 # noqa: E402
from dogrulayici.kurallar import _rotasyon_geri_saat         # noqa: E402
from uret_veri_seti import sahne_uret                        # noqa: E402

PLANLAR = sys.argv[1:]
g = sahne_uret(1.0, 0.95)
tip = {c["id"]: (c.get("sozlesme") or {}).get("tip") for c in g["calisanlar"]}
gereken_ft = 0.0
for c in g["calisanlar"]:
    s = c.get("sozlesme") or {}
    if s.get("tip") == "tam_zamanli" and s.get("haftalik_saat"):
        norm = float(s["haftalik_saat"]) / float(s.get("gun_sayisi") or 6)
        izin = sum(1 for i in (c.get("izinler") or []) if i.get("tip") in ("yillik", "ucretli", "rapor") or True)
        gereken_ft += float(s["haftalik_saat"]) - izin * norm
hedef_toplam = sum(float(t.get("hedef") or 0) for t in g["talep"])
print("sahne: %d calisan, tipler %s | talep hedef %.0f kisi-saat | tam zamanli gereken (izin dusulmus) ~%.0f"
      % (len(g["calisanlar"]), dict(collections.Counter(tip.values())), hedef_toplam, gereken_ft))


def net_saat(a):
    bas, bit = zaman.aralik(a)
    mola = sum(float(m.get("bit", 0)) - float(m.get("bas", 0)) for m in a.get("molalar") or [])
    return bit - bas - mola


for yol in PLANLAR:
    d = json.load(io.open(yol, encoding="utf-8"))
    atamalar = d["cikti"]["atamalar"]
    print("\n==== %s  (%d atama)" % (os.path.basename(yol), len(atamalar)))
    saat_tip = collections.Counter()
    for a in atamalar:
        saat_tip[tip.get(a["calisan"])] += net_saat(a)
    print("  net saat / tip: %s" % {k: round(v) for k, v in saat_tip.items()})

    # ---- 1. HEDEF_ASIMI ayristirmasi (dogrulayicinin sayimi ile ayni hucre/kisi)
    uyelik, mod = K.uyelik_haritasi(g), K.cok_ekipli_sayim(g)
    kap = K._kapsama_atamalari(g, atamalar)
    asim_toplam = hucre = saatlik_ust = 0
    asim_tip = collections.Counter()      # asim hucrelerinde kisi-saat / tip (hucredeki herkes)
    sadece_ft = 0                           # asim hucrelerinden yalniz tam zamanli olanlar
    for t, gun, saat in K._talep_hucreleri(g):
        hedef = t.get("hedef")
        if hedef is None:
            continue
        kisiler = [a for a in kap if K.ekibe_sayilir(a, t.get("ekip"), uyelik, mod) and zaman.atanmis_mi(a, gun, saat)]
        sayi = len(kisiler)
        if sayi > hedef:
            asim = sayi - hedef
            asim_toplam += asim
            hucre += 1
            tipler = collections.Counter(tip.get(a.get("calisan"), "devir") for a in kisiler)
            saatlik = sum(v for k, v in tipler.items() if k not in ("tam_zamanli",))
            saatlik_ust += min(asim, saatlik)
            if saatlik == 0:
                sadece_ft += asim
            for k, v in tipler.items():
                asim_tip[k] += v
    print("  HEDEF_ASIMI: %d kisi-saat, %d hucre | saatlik (yz/sezonluk/stajyer) ile ACIKLANABILIR ust sinir %d kisi-saat (%.0f%%)"
          "; hucrede yalniz tam zamanli olan asim %d kisi-saat (%.0f%%)"
          % (asim_toplam, hucre, saatlik_ust, 100.0 * saatlik_ust / asim_toplam if asim_toplam else 0,
             sadece_ft, 100.0 * sadece_ft / asim_toplam if asim_toplam else 0))
    print("  asim hucrelerindeki kisi-saat / tip: %s" % dict(asim_tip))

    # ---- 2. Rotasyon gun tanimlari
    # kisi -> [(bas_mutlak, bit_mutlak, gun)] siralanmis
    vard = collections.defaultdict(list)
    for a in atamalar:
        bas, bit = zaman.aralik(a)
        vard[a["calisan"]].append((bas, bit, int(a["gun"])))
    for k in vard:
        vard[k].sort()
    sayim = collections.Counter()
    for k, liste in vard.items():
        for i in range(len(liste) - 1):
            b0, e0, g0 = liste[i]
            b1, e1, g1 = liste[i + 1]
            h = _rotasyon_geri_saat(b0 % 24, b1 % 24)
            if h <= 0:
                continue
            son_gun0 = int((e0 - 1e-9) // 24)        # dokunulan son gun (bit=24 -> ayni gun)
            # K-46: yarisindan cogu sonraki gune dusuyorsa sonraki gun; esit -> basladigi gun
            uzun = e0 - b0
            sonraki_pay = max(0.0, e0 - (g0 + 1) * 24)
            cog0 = g0 + 1 if sonraki_pay > uzun / 2 else g0
            sonraki_pay1 = max(0.0, e1 - (g1 + 1) * 24)
            cog1 = g1 + 1 if sonraki_pay1 > (e1 - b1) / 2 else g1
            simdi = (g1 == g0 + 1)
            c = (cog1 == cog0 + 1)
            dd = (g1 == son_gun0 or g1 == son_gun0 + 1)
            sayim["simdi"] += simdi
            sayim["C"] += c
            sayim["D"] += dd
            sayim["D_kazanc(B8: gece->bos gorunen->ertesi)"] += (dd and not simdi)
            sayim["C_kayip(sabah->ertesi gece)"] += (simdi and not c)
            sayim["C_kazanc"] += (c and not simdi)
            sayim["ayni_gun_cift"] += (g1 == g0)
    print("  rotasyon geri cift (saat>0): bugunku tanim %d | C (K-46 cogunluk) %d | D (dokunulan gun) %d | "
          "D'nin kazanci %d | C'nin kaybi %d, kazanci %d | ayni gun ciftleri %d"
          % (sayim["simdi"], sayim["C"], sayim["D"], sayim["D_kazanc(B8: gece->bos gorunen->ertesi)"],
             sayim["C_kayip(sabah->ertesi gece)"], sayim["C_kazanc"], sayim["ayni_gun_cift"]))
