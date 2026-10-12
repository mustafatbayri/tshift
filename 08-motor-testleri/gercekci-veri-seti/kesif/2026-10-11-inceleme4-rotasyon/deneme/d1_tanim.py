# -*- coding: utf-8 -*-
"""A. Tanim <-> kod uyumu: hedefli karsi ornekler (K-65 maddeleri 1-5).
Kullanim: python3 d1_tanim.py  (cikti: d1_tanim.out)"""
import copy
import json
from ortak import (coz, degerlendir, Model, AYAR, KURAL, kural, atama, rot_satirlari,
                   rot_kirilim, rotasyon_geri_saat, _rotasyon_geri_saat, dairesel_geri,
                   yuvarla, benim_say, _rotasyon_metrigi)

SABAH = {"id": "SABAH", "ekip": "E", "bas": 7, "bit": 15, "mola_dk": 60}
ORTA = {"id": "ORTA", "ekip": "E", "bas": 10, "bit": 18, "mola_dk": 60}
AKSAM = {"id": "AKSAM", "ekip": "E", "bas": 13.75, "bit": 22, "mola_dk": 60}
GECE = {"id": "GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60}


def sahne(talep, sablonlar=(SABAH, ORTA, AKSAM, GECE), rotasyon=True, dinlenme=11, kisiler=("P1",), **ek):
    kurallar = [kural("ASGARI_KAPSAMA"), kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                kural("HEDEF_ASIMI", tur="YUMUSAK"),
                kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=dinlenme)]
    if rotasyon:
        kurallar.append(kural(KURAL, tur="YUMUSAK", **ek.pop("rotasyon_par", {})))
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": p, "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                         "izinler": [], "uygunluk": []} for p in kisiler],
         "vardiya_sablonlari": [dict(t) for t in sablonlar],
         "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1} for d, s in talep],
         "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}
    g.update(ek)
    return g


def plan_ozeti(c):
    return sorted((a["calisan"], a["gun"], a["sablon"], a["bas"]) for a in c["atamalar"])


SONUC = {}


def kaydet(ad, **k):
    SONUC[ad] = k
    print("\n== %s ==" % ad)
    for a, b in k.items():
        print("  %-22s %s" % (a, b))


# ---------------------------------------------------------------------
# A1. Dairesel tanim: uc yazim (motor, dogrulayici, inceleme) sinir degerlerde ayni mi
# ---------------------------------------------------------------------
sinir = [(8, 20), (20, 8), (9, 21), (21, 9), (8, 20.25), (20.25, 8), (8, 19.75), (19.75, 8),
         (0, 7), (7, 0), (23, 7), (7, 23), (23, 0), (0, 23), (24.5, 7), (7, 24.5), (24.5, 23),
         (23, 24.5), (0, 0), (24, 0), (0, 24), (13.75, 11), (11, 13.75), (12, 0), (0, 12),
         (23.75, 11.75), (11.75, 23.75), (31, 7), (7, 31), (10, 22.25), (22.25, 10), (8, 23), (9, 0), (10, 13.75)]
fark = []
for a, b in sinir:
    m, d, i = rotasyon_geri_saat(a, b), _rotasyon_geri_saat(a, b), dairesel_geri(a, b)
    mg, dg, ig = rotasyon_geri_saat(a, b, "geri"), _rotasyon_geri_saat(a, b, "geri"), dairesel_geri(a, b, "geri")
    if not (m == d == i and mg == dg == ig):
        fark.append((a, b, m, d, i, mg, dg, ig))
kaydet("A1_dairesel_uc_yazim", cift_sayisi=len(sinir), farkli=fark,
       ornekler={str(k): rotasyon_geri_saat(*k) for k in [(8, 20), (20, 8), (24.5, 7), (0, 7), (23, 7), (13.75, 11), (10, 22.25), (8, 23), (9, 0), (10, 13.75)]},
       ornekler_yon_geri={str(k): rotasyon_geri_saat(k[0], k[1], "geri") for k in [(8, 20), (20, 8), (7, 10)]})

# ---------------------------------------------------------------------
# A2. Yuvarlama: amac terimi int(h+0.5) mi -- uctan uca (zorunlu cift, agirlik 1)
#     0,25 -> 0 ; 0,5 -> 1 ; 0,75 -> 1 ; 2,5 -> 3 ; 2,75 -> 3 ; 9,25 -> 9 ; 11,75 -> 12 ; 12 (yon=geri) -> 12
# ---------------------------------------------------------------------
yuv = []
for b0, b1, yon in [(10.25, 10, "ileri"), (10.5, 10, "ileri"), (10.75, 10, "ileri"), (13.5, 11, "ileri"),
                    (13.75, 11, "ileri"), (23, 13.75, "ileri"), (10, 22.25, "ileri"), (8, 20, "geri"),
                    (20, 8, "geri"), (11.5, 23.5, "ileri")]:
    S0 = {"id": "S0", "ekip": "E", "bas": b0, "bit": b0 + 4, "mola_dk": 0}
    S1 = {"id": "S1", "ekip": "E", "bas": b1, "bit": b1 + 4, "mola_dk": 0}
    # cift sabit atamayla ZORLANIR (talep yok): gun 0 S0, gun 1 S1; agirlik 1 -> deger = yuvarlanmis saat
    g = sahne([], sablonlar=(S0, S1), dinlenme=0, agirliklar={KURAL: 1}, rotasyon_par={"yon": yon},
              sabit_atamalar=[{"calisan": "P1", "gun": 0, "sablon": "S0"}, {"calisan": "P1", "gun": 1, "sablon": "S1"}])
    c = coz(g, AYAR)
    beklenen = yuvarla(dairesel_geri(b0, b1, yon))
    plan = plan_ozeti(c) if c["durum"] == "cozuldu" else None
    rk = rot_kirilim(c) if c["durum"] == "cozuldu" else None
    deger = (rk or {}).get("deger", 0) if c["durum"] == "cozuldu" else None
    zorunlu = plan is not None and {(p[1], p[2]) for p in plan} >= {(0, "S0"), (1, "S1")}
    yuv.append({"b0": b0, "b1": b1, "yon": yon, "kesin": dairesel_geri(b0, b1, yon), "beklenen_yuvarlanmis": beklenen,
                "durum": c["durum"], "cift_kuruldu": zorunlu, "deger": deger,
                "metrik_saat": c.get("metrikler", {}).get("rotasyon_geri_saat"),
                "uyum": (deger == beklenen) if zorunlu else "cift kurulmadi"})
kaydet("A2_yuvarlama_uctan_uca", satirlar=json.dumps(yuv, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------------
# A3. "Ayni gunde birden cok atama -> ILK baslangic" -- donmus gunde iki satir (yonetici iki vardiya yazmis)
#     Model: her sablon ciftine kisit -> g = EN BUYUK geri; dogrulayici/metrik: en kucuk bas.
# ---------------------------------------------------------------------
plan = [atama(0, SABAH), atama(0, AKSAM), atama(1, ORTA)]
g = sahne([(1, 10), (1, 16)], donmus_gunler=[0], mevcut_plan=copy.deepcopy(plan[:2]), sablonlar=(SABAH, ORTA, AKSAM))   # gun 1: yalniz ORTA 10 ve 16'yi birlikte kapatir
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A3_donmus_gunde_iki_satir_ilk_baslangic", durum=c["durum"], plan=plan_ozeti(c),
       amac_kirilimi=rot_kirilim(c), metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)],
       benim=benim_say(g, c["atamalar"]), notlar=[n for n in c["uygulanmayan_notlar"] if "K-54" in n])

# ---------------------------------------------------------------------
# A4. Donmus gun 0 ama mevcut_plan YOK (serbest planlanir) + gecmis gun -1:
#     model (-1,0) terimini yazar mi; dogrulayici satiri "gecmis" isaretler mi
# ---------------------------------------------------------------------
g = sahne([(0, 8)], donmus_gunler=[0])
g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]
k = Model(copy.deepcopy(g)).kur()
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A4_donmus_gun0_plansiz_gecmisli", model_rotasyon_anahtarlari=sorted(k.rotasyon), model_donmus=sorted(k.donmus),
       durum=c["durum"], plan=plan_ozeti(c), amac_kirilimi=rot_kirilim(c),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)],
       gecmis_ihlaller=[(i["kural"], i["gun"]) for i in r["gecmis_ihlaller"]])

# ---------------------------------------------------------------------
# A5. Aktif olmayan calisanin donmus satiri + gecmisi: metrik (yalniz aktif kisinin gecmisi) vs dogrulayici
# ---------------------------------------------------------------------
plan = [atama(0, SABAH, "P2")]
g = sahne([(1, 8)], donmus_gunler=[0], mevcut_plan=copy.deepcopy(plan), kisiler=("P1", "P2"))
g["calisanlar"][1]["durum"] = "pasif"
g["calisanlar"][1]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A5_pasif_calisan_donmus_satir_gecmis", durum=c["durum"], plan=plan_ozeti(c), amac_kirilimi=rot_kirilim(c),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["calisan"], i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)],
       benim=benim_say(g, c["atamalar"]), notlar=[n for n in c["uygulanmayan_notlar"] if "K-54" in n])

# ---------------------------------------------------------------------
# A6. Donmus satir hicbir sablona oturmuyor (10:00-14:00): model cifti gormez, dogrulayici/metrik gorur
# ---------------------------------------------------------------------
plan = [{"calisan": "P1", "ekip": "E", "sablon": None, "gun": 0, "bas": 10, "bit": 14, "molalar": []}]
g = sahne([(1, 8)], donmus_gunler=[0], mevcut_plan=copy.deepcopy(plan))
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A6_donmus_satir_sablona_oturmuyor", durum=c["durum"], plan=plan_ozeti(c), amac_kirilimi=rot_kirilim(c),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)],
       notlar=[n for n in c["uygulanmayan_notlar"] if "K-54" in n])

# ---------------------------------------------------------------------
# A7. Serbest -> donmus cift (donmus_gunler=[2], on ek degil): model terime alir mi, dogrulayici isaretler mi
# ---------------------------------------------------------------------
plan = [atama(2, SABAH)]
g = sahne([(1, 20)], donmus_gunler=[2], mevcut_plan=copy.deepcopy(plan), dinlenme=0)   # gun 1 yalniz AKSAM kapatir; 13:45 -> 07:00 (9 sa dinlenme) icin dinlenme 0
k = Model(copy.deepcopy(g)).kur()
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A7_serbest_donmus_cifti", model_rotasyon_anahtarlari=sorted(k.rotasyon), durum=c["durum"], plan=plan_ozeti(c),
       amac_kirilimi=rot_kirilim(c), metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)])

# ---------------------------------------------------------------------
# A8. Gun -1'de iki kayit: ILK baslangic (min) -- model ve dogrulayici
# ---------------------------------------------------------------------
g = sahne([(0, 8)])
g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 18}, {"gun": -1, "bas": 5, "bit": 9}]
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A8_gun_eksi1_iki_kayit", durum=c["durum"], plan=plan_ozeti(c), amac_kirilimi=rot_kirilim(c),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"]) for i in rot_satirlari(r)],
       aciklama="min(5, 13.75)=5 -> 05:00 -> 07:00 ileri: satir yok beklenir; 13.75 alinsaydi 6,75 geri")

# ---------------------------------------------------------------------
# A9. yon: buyuk harf / None / sayi -> 'ileri' + not; dogrulayici da ileri
# ---------------------------------------------------------------------
yonler = {}
for y in ("GERI", "Geri", None, 1, "geri "):
    g = sahne([(0, 20), (1, 10), (1, 16)], rotasyon_par={"yon": y})
    c = coz(g, AYAR)
    r = degerlendir(g, c["atamalar"])
    yonler[repr(y)] = {"deger": (rot_kirilim(c) or {}).get("deger"), "not": [n for n in c["uygulanmayan_notlar"] if "yon" in n],
                       "dogrulayici": [(i["gun"], i["olculen"]) for i in rot_satirlari(r)]}
kaydet("A9_yon_degerleri", sonuc=json.dumps(yonler, ensure_ascii=False))

# ---------------------------------------------------------------------
# A10. Gun 0 donmus (mevcut_plan ile) + gecmis -1: model (-1,0) atlar, dogrulayici gecmis isaretler
# ---------------------------------------------------------------------
plan = [atama(0, SABAH)]
g = sahne([(1, 8)], donmus_gunler=[0], mevcut_plan=copy.deepcopy(plan))
g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]
k = Model(copy.deepcopy(g)).kur()
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A10_gun0_donmus_planli_gecmisli", model_rotasyon_anahtarlari=sorted(k.rotasyon), durum=c["durum"], plan=plan_ozeti(c),
       amac_kirilimi=rot_kirilim(c), metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"], i.get("gecmis")) for i in rot_satirlari(r)])

# ---------------------------------------------------------------------
# A11. Kural `aktif: false` -- model terimi, metrik, dogrulayici satiri, kirilim anahtari
# ---------------------------------------------------------------------
g = sahne([(0, 20), (1, 10), (1, 16)])
g["kurallar"][-1]["aktif"] = False
k = Model(copy.deepcopy(g)).kur()
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A11_aktif_false", model_rotasyon=len(k.rotasyon), ro_ceza=len([v for _, v in k.cezalar if v.Name().startswith("ro_")]),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       kirilim_anahtari=KURAL in c["cozum_istatistikleri"]["amac_dagilimi"], dogrulayici=rot_satirlari(r),
       uygulanmayan=r["uygulanmayan_kurallar"])

# ---------------------------------------------------------------------
# A12. g alani 0..12: yon=geri ile tam 12 saatlik "geri" (8 -> 20): hy=12, alan yeter mi
# ---------------------------------------------------------------------
S0 = {"id": "S0", "ekip": "E", "bas": 8, "bit": 12, "mola_dk": 0}
S1 = {"id": "S1", "ekip": "E", "bas": 20, "bit": 24, "mola_dk": 0}
g = sahne([(0, 11), (1, 23)], sablonlar=(S0, S1), dinlenme=0, rotasyon_par={"yon": "geri"})
c = coz(g, AYAR)
r = degerlendir(g, c["atamalar"])
kaydet("A12_alan_12", durum=c["durum"], plan=plan_ozeti(c), amac_kirilimi=rot_kirilim(c),
       metrik=(c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
       dogrulayici=[(i["gun"], i["olculen"]) for i in rot_satirlari(r)])

json.dump(SONUC, open(__file__.replace(".py", ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
