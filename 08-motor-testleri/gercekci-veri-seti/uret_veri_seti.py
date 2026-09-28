# -*- coding: utf-8 -*-
"""
V6 GERCEKCI VERI SETI URETICISI  --  S-20

NEDEN VAR (Mustafa, 28 Eylul)
  > "Test senaryolarini 15-20 kisilik bir ekip dusunerek yapiyorsun hep.
  >  Burada kurmamiz gereken senaryo daha kalabalik bir ekip uzerinden
  >  olmali... Kullanmadigimiz hicbir kural veya kriter olmamali. Her sey
  >  bu data setinde test edilebilecek sekilde tanimli olmali. Ancak bu
  >  sekilde dogru test sonuclari elde edebiliriz."

  Bugune kadarki en buyuk sahne S-10 idi: 10 kisi, 1 ekip, 3 sablon, 2 talep
  satiri, tek vardiya bicimi. Motorun 350 kisilik uc ekipli bir organizasyonda
  ne yaptigi HIC OLCULMEDI.

NE URETIR
  Tek bir sahne dosyasi (`fikstur/_sahne-S20.json`) -- 350 kisi, uc ekip,
  on dort vardiya sablonu, yedi gun, hafta ici/hafta sonu ayri esikler,
  ekip basina ayri mola politikasi, ve katalogdaki 39 kuralin TAMAMI tanimli.

TOHUM SABIT
  `random.Random(20260928)`. Ayni girdi her calistirmada ayni dosyayi uretir;
  yoksa "dun yesildi bugun kirmizi" tartismasi cozulemez.

KULLANIM
  py uret_veri_seti.py                 -> tam veri seti (350 kisi)
  py uret_veri_seti.py --olcek 0.1     -> ayni bicim, 35 kisi (olcekleme olcumu)
"""

import json
import random
import sys

TOHUM = 20260928

# ----------------------------------------------------------------------
# Organizasyon -- Mustafa'nin verdigi dagilim
# ----------------------------------------------------------------------
EKIPLER = [
    {"id": "SATIS",      "ad": "Satis",              "kisi": 200, "yedi_yirmidort": True},
    {"id": "BACKOFFICE", "ad": "Back Office",        "kisi": 100, "yedi_yirmidort": True},
    {"id": "MHIZMET",    "ad": "Musteri Hizmetleri", "kisi": 50,  "yedi_yirmidort": False},
]

# ----------------------------------------------------------------------
# Vardiya sablonlari
#
# ⚠ GUNU UC ESIT PARCAYA BOLMEK YASAK (Mustafa): "ilgili gunu direk 8 saat
#   araliklarla 3'e bolmemelisin, min 4 vardiya plani olmali." Asagidaki
#   sablonlar BILEREK ORTUSUR -- gercek operasyonda yogun saatte daha cok
#   kisi bulunur, vardiyalar birbirinin uzerine biner.
#
#   Ortusme ayni zamanda CAKISMA_YOK'u gercekten sinar: 11-19 ile 15-23
#   ayni kisiye verilemez ve motorun bunu gormesi gerekir.
# ----------------------------------------------------------------------
SABLONLAR = [
    # --- SATIS : 7/24, bes bicim, ucu ortusuyor ---
    {"id": "S-SABAH", "ekip": "SATIS", "bas": 7,  "bit": 15, "mola_dk": 60},
    {"id": "S-ARA",   "ekip": "SATIS", "bas": 11, "bit": 19, "mola_dk": 60,
     "_not": "Yogun saat takviyesi -- SABAH ve AKSAM ile bilerek ortusur."},
    {"id": "S-AKSAM", "ekip": "SATIS", "bas": 15, "bit": 23, "mola_dk": 60},
    {"id": "S-GECE",  "ekip": "SATIS", "bas": 23, "bit": 31, "mola_dk": 60,
     "_not": "23:00-07:00. Genisletilmis saat (Z-1): gun sinirini asar."},
    {"id": "S-KISA",  "ekip": "SATIS", "bas": 10, "bit": 16, "mola_dk": 30,
     "_not": "Part-time bicimi."},

    # --- BACKOFFICE : 7/24, bes bicim ---
    {"id": "B-SABAH", "ekip": "BACKOFFICE", "bas": 8,  "bit": 16, "mola_dk": 45},
    {"id": "B-ARA",   "ekip": "BACKOFFICE", "bas": 12, "bit": 20, "mola_dk": 45},
    {"id": "B-AKSAM", "ekip": "BACKOFFICE", "bas": 16, "bit": 24, "mola_dk": 45},
    {"id": "B-GECE",  "ekip": "BACKOFFICE", "bas": 0,  "bit": 8,  "mola_dk": 45,
     "_not": "00:00-08:00. Gece penceresiyle (20-06) kesisir."},
    {"id": "B-YARIM", "ekip": "BACKOFFICE", "bas": 9,  "bit": 13, "mola_dk": 0,
     "_not": "4 saat -- MOLA_HAKKI'nin en dusuk esigi (<=4sa: 15dk)."},

    # --- MUSTERI HIZMETLERI : 08-22, hafta sonu kisa ---
    {"id": "M-SABAH", "ekip": "MHIZMET", "bas": 8,  "bit": 17, "mola_dk": 60},
    {"id": "M-AKSAM", "ekip": "MHIZMET", "bas": 13, "bit": 22, "mola_dk": 60},
    {"id": "M-HSONU", "ekip": "MHIZMET", "bas": 10, "bit": 18, "mola_dk": 60,
     "gunler": [5, 6], "_not": "Yalniz hafta sonu -- `gunler` alani kisitlar."},
    {"id": "M-AKSAMK", "ekip": "MHIZMET", "bas": 17, "bit": 21, "mola_dk": 0,
     "_not": "Part-time aksam bicimi, 4 saat."},
]

# ----------------------------------------------------------------------
# Mola politikalari -- EKIP BASINA AYRI (K-32, kapsam K/D)
#
# Ucu de farkli: ayni kodun uc ayri politikayi dogru cevirdigini gormek icin.
# ----------------------------------------------------------------------
MOLA_POLITIKALARI = {
    "SATIS": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
              {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}],
    "BACKOFFICE": [{"tip": "yemek", "dakika": 45, "adet": 1, "ucretli": False},
                   {"tip": "dinlenme", "dakika": 15, "adet": 2, "ucretli": True}],
    "MHIZMET": [{"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
                {"tip": "dinlenme", "dakika": 20, "adet": 3, "ucretli": True}],
}

# Yemek penceresi de ekibe gore ayri (MOLA_YERLESIMI, kapsam K/D)
YEMEK_PENCERESI = {
    "SATIS":      {"en_az_saat": 3, "en_gec_saat": 5},
    "BACKOFFICE": {"en_az_saat": 3, "en_gec_saat": 6},
    "MHIZMET":    {"en_az_saat": 2, "en_gec_saat": 5},
}

# ----------------------------------------------------------------------
# Talep -- HAFTA ICI / HAFTA SONU AYRI (Mustafa'nin acik istegi)
#
#   "Ozellikle hafta sonu icin, sahada olmasi gereken kisi sayisi gibi
#    degerler hafta icine gore farkli olmali."
#
# Bicim: ekip -> (gun tipi) -> saat araligi -> (asgari, hedef, sahada_taban)
# Saat araliklari BILEREK esit degil: sabah yogunlugu, ogle zirvesi, gece dip.
# ----------------------------------------------------------------------
TALEP_PROFILI = {
    "SATIS": {
        "haftaici": [((7, 10), 12, 18, 10), ((10, 13), 22, 32, 18),
                     ((13, 17), 26, 38, 22), ((17, 21), 18, 26, 15),
                     ((21, 23), 8, 12, 6),   ((23, 31), 5, 8, 4)],
        "haftasonu": [((7, 10), 6, 9, 5),    ((10, 13), 14, 20, 11),
                      ((13, 17), 16, 24, 13), ((17, 21), 11, 16, 9),
                      ((21, 23), 5, 8, 4),   ((23, 31), 3, 5, 2)],
    },
    "BACKOFFICE": {
        "haftaici": [((0, 8), 4, 6, 3), ((8, 12), 14, 20, 11),
                     ((12, 16), 16, 22, 13), ((16, 20), 10, 14, 8),
                     ((20, 24), 5, 8, 4)],
        "haftasonu": [((0, 8), 2, 4, 2), ((8, 12), 6, 9, 5),
                      ((12, 16), 7, 10, 6), ((16, 20), 5, 7, 4),
                      ((20, 24), 3, 4, 2)],
    },
    "MHIZMET": {
        "haftaici": [((8, 13), 8, 12, 6), ((13, 18), 10, 14, 8),
                     ((18, 22), 6, 9, 5)],
        "haftasonu": [((10, 14), 5, 7, 4), ((14, 18), 6, 8, 4)],
    },
}

# ⚠ SOZLUK SARTNAMEDEN (#8.3 tablosu): tam_zamanli | yari_zamanli |
#   sezonluk | stajyer. Ilk yazimda "part_time" uydurmustum; motor o degeri
#   TANIMIYOR ve PART_TIME_LIMIT 90 kisiyi SESSIZCE atlamisti. Hicbir kanal
#   bunu bildirmedi -- `okunmayan_alanlar` OKUNMAYAN ALANI bildirir,
#   TANINMAYAN DEGERI degil. Bulgu: T-45.
#
#   Dordu de kullanilir: sezonluk ve stajyer de sartnamede var ve
#   PART_TIME_LIMIT onlari da kapsamiyor -- bu da T-45'in konusu.
SOZLESMELER = [
    ({"tip": "tam_zamanli",  "haftalik_saat": 45}, 0.58),
    ({"tip": "tam_zamanli",  "haftalik_saat": 40}, 0.10),
    ({"tip": "yari_zamanli", "haftalik_saat": 20}, 0.16),
    ({"tip": "yari_zamanli", "haftalik_saat": 30}, 0.08),
    ({"tip": "sezonluk",     "haftalik_saat": 40}, 0.05),
    ({"tip": "stajyer",      "haftalik_saat": 30}, 0.03),
]

ROLLER = ["agent", "kidemli_agent", "takim_lideri", "uzman"]
YETKINLIKLER = ["ingilizce", "almanca", "kurumsal", "iade", "teknik"]


def _sec(rnd, dagilim):
    x = rnd.random()
    top = 0.0
    for deger, pay in dagilim:
        top += pay
        if x <= top:
            return deger
    return dagilim[-1][0]


def calisanlar_uret(rnd, olcek):
    """Calisan listesi -- sozlesme, rol, yetkinlik, izin, uygunluk, devir yuku."""
    cikan = []
    sira = 1
    for ekip in EKIPLER:
        adet = max(3, int(round(ekip["kisi"] * olcek)))
        for _ in range(adet):
            soz = dict(_sec(rnd, SOZLESMELER))
            c = {
                "id": "C%04d" % sira,
                "ekipler": [ekip["id"]],
                "operasyonel_rol": _sec(rnd, [("agent", .62), ("kidemli_agent", .22),
                                              ("takim_lideri", .08), ("uzman", .08)]),
                "yetkinlikler": rnd.sample(YETKINLIKLER, rnd.choice([0, 0, 1, 1, 2])),
                "sozlesme": soz,
                "izinler": [],
                "uygunluk": [],
                "devir_yuk": {"gece": 0, "hafta_sonu": 0, "saat": 0, "cumartesi": 0},
                "gecmis_vardiyalar": [],
            }

            # PART_TIME_LIMIT + UYGUNLUK_TAKVIMI: part-time'lerin bir kisminin
            # calisabilecegi gunler SECILI (Mustafa'nin acik istegi).
            if soz["tip"] == "yari_zamanli" and rnd.random() < 0.65:
                calisabilir = sorted(rnd.sample(range(7), rnd.choice([2, 3, 3, 4])))
                for g in range(7):
                    if g not in calisabilir:
                        c["uygunluk"].append(
                            {"tip": "uygun_degil", "gun": g, "bas": 0, "bit": 24})
                c["_calisabilir_gunler"] = calisabilir

            # ONAYLI_IZIN: ~%8 izinli, biri REDDEDILMIS (durum alani sinansin)
            if rnd.random() < 0.08:
                g = rnd.randrange(7)
                c["izinler"].append({"gun": g, "tip": "yillik",
                                     "durum": "onayli" if rnd.random() < 0.85
                                     else "reddedildi"})

            # ADALET_DENGESI: devir yuku bilerek DENGESIZ dagitilir, yoksa
            # kural hic ateslenmez ve "yesil" yanilticidir.
            if rnd.random() < 0.25:
                c["devir_yuk"] = {"gece": rnd.randrange(0, 6),
                                  "hafta_sonu": rnd.randrange(0, 5),
                                  "saat": rnd.randrange(0, 40),
                                  "cumartesi": rnd.randrange(0, 4)}

            # AKTIF_CALISAN: birkac kisi pasif.
            # ⚠ Alan adi `durum` (#8.3), `aktif` DEGIL. Ilk yazimda
            #   `aktif: False` yazmistim; motor o alani okumuyor ve kural
            #   hic ateslenmiyordu. Bunu `okunmayan_alanlar` YAKALADI --
            #   kanal calisiyor (23 Eylul, T-19).
            if rnd.random() < 0.03:
                c["durum"] = "pasif" if rnd.random() < 0.7 else "ayrildi"

            cikan.append(c)
            sira += 1
    return cikan


def talep_uret(olcek):
    """Hucre basina talep -- hafta ici / hafta sonu AYRI esiklerle."""
    cikan = []
    for ekip in EKIPLER:
        prof = TALEP_PROFILI[ekip["id"]]
        for gun in range(7):
            tip = "haftasonu" if gun in (5, 6) else "haftaici"
            for (bas, bit), asgari, hedef, taban in prof[tip]:
                for saat in range(bas, bit):
                    # ⚠ GECE YARISINI ASAN TALEP HANGI GUNE YAZILIR
                    #   Ilk yazimda `saat % 24` yapip `gun`u AYNEN
                    #   birakiyordum. Sonuc: gun 0'in 00:00-06:00 saatlerine
                    #   talep yaziliyordu -- ama o saatleri yalniz PAZAR
                    #   GECESI baslayan bir vardiya kapatabilir ve Pazar
                    #   planlanan haftanin icinde degil.
                    #
                    #   Plan COZUMSUZ kaliyordu ve motor hakliydi: imkansiz
                    #   bir sey isteniyordu. (Motorun teshisi de yerindeydi:
                    #   "hucre SATIS gun 0 saat 0, gereken 1, mumkun 0".)
                    #
                    #   Dogrusu: 24'u asan saat ERTESI GUNE aittir. Haftanin
                    #   son gununden tasan kisim bu planin disinda kalir --
                    #   onu gelecek hafta karsilar.
                    gercek_gun, gercek_saat = gun + saat // 24, saat % 24
                    if gercek_gun > 6:
                        continue
                    cikan.append({
                        "ekip": ekip["id"], "gun": gercek_gun,
                        "saat": gercek_saat,
                        "asgari": max(1, int(round(asgari * olcek))),
                        "hedef": max(1, int(round(hedef * olcek))),
                        "_sahada_taban": max(1, int(round(taban * olcek))),
                        "_gun_tipi": tip,
                    })
    return cikan


def kurallar_uret():
    """Katalogdaki 39 kuralin TAMAMI.

    GOVDESI YAZILI 24 -> gercekten degerlendirilir.
    YAZILMAMIS 15     -> aktif tanimlanir ki `uygulanmayan_kurallar` kanali
                         gercekten atessin. Sessizce dislamak, kanali test
                         etmemek demektir (T-18 tam bu kapida bekliyor).
    """
    K = []

    def ek(kod, tur, yasal=False, kabul=False, **par):
        k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal}
        if tur == "SERT":
            k["kabul_edilebilir"] = kabul
        if par:
            k["parametreler"] = par
        K.append(k)

    # --- govdesi YAZILI olanlar ---
    ek("AKTIF_CALISAN", "SERT")
    ek("SOZLESME_GECERLI", "SERT")
    ek("CAKISMA_YOK", "SERT")
    ek("ASGARI_KAPSAMA", "SERT")
    ek("HEDEF_KAPSAMA", "YUMUSAK")
    ek("GUNLUK_AZAMI", "SERT", yasal=True, azami_saat=11)
    ek("HAFTALIK_AZAMI", "SERT", yasal=True, azami_saat=45)
    ek("HAFTA_TATILI", "SERT", yasal=True, asgari_gun=1)
    ek("VARDIYA_ARASI_DINLENME", "SERT", yasal=True, asgari_saat=11)
    ek("ARDISIK_CALISMA_GUNU", "SERT", kabul=True, azami_gun=6)
    ek("FAZLA_MESAI_TAVANI", "SERT", azami_saat_hafta=10)
    ek("ONAYLI_IZIN", "SERT")
    ek("UYGUNLUK_TAKVIMI", "SERT", kabul=True)
    ek("PART_TIME_LIMIT", "SERT")
    ek("DONMUS_GUN", "SERT")
    ek("KILIT_UYUMU", "SERT")
    ek("ADALET_DENGESI", "YUMUSAK", esik=2)
    ek("MOLA_HAKKI", "SERT", yasal=True)
    ek("MOLA_KAPSAMASI", "YUMUSAK")
    ek("MOLA_TIPI_ZORUNLU", "SERT", kabul=True)
    ek("MOLA_ASGARI_BLOK", "SERT", asgari_dakika=15)
    ek("YEMEK_TEK_BLOK", "SERT")
    ek("MOLA_YERLESIMI", "YUMUSAK", **YEMEK_PENCERESI["SATIS"])
    ek("SAHADA_ASGARI", "SERT", asgari_sahada=0)   # hucre basina ezilir

    # --- govdesi YAZILMAMIS olanlar (uygulanmayan_kurallar atessin) ---
    for kod, tur, yasal in (
            ("GECE_VARDIYASI_AZAMI", "SERT", True),
            ("GECE_POSTASI_DEVRI", "SERT", True),
            ("GECE_YARISI_ASAN", "SERT", False),
            ("ARDISIK_GECE_LIMIT", "SERT", False),
            ("ARDISIK_HAFTA_SONU_LIMIT", "SERT", False),
            ("ASGARI_VARDIYA_SURESI", "SERT", False),
            ("CALISMA_SAATLERI", "SERT", False),
            ("EKIP_SUREKLILIGI", "YUMUSAK", False),
            ("PLAN_KARARLILIGI", "YUMUSAK", False),
            ("ROL_KAPSAMASI", "SERT", False),
            ("YETKINLIK_KAPSAMASI", "SERT", False),
            ("SAAT_DENGESI", "YUMUSAK", False),
            ("TERCIH_KARSILAMA", "YUMUSAK", False),
            ("VARDIYA_ROTASYON_YONU", "YUMUSAK", False),
            ("YILLIK_FAZLA_MESAI_TAVANI", "SERT", True)):
        ek(kod, tur, yasal=yasal, kabul=False)
    return K


def sahne_uret(olcek=1.0):
    rnd = random.Random(TOHUM)
    calisanlar = calisanlar_uret(rnd, olcek)
    talep = talep_uret(olcek)

    sablonlar = []
    for s in SABLONLAR:
        d = dict(s)
        d["mola_politikasi"] = MOLA_POLITIKALARI[s["ekip"]]
        sablonlar.append(d)

    # KILIT_UYUMU + DONMUS_GUN: gun 0 donmus, birkac atama kilitli
    #
    # ⚠ KILIT BICIMI (#11.2). Iki bicim var, ucuncusu YOK:
    #     sabitleme {calisan, ekip, gun, bas, bit}   -> bu atama MUTLAKA olacak
    #     yasak     {calisan, gun, tip: "yasak"}     -> o gun hic atama olmayacak
    #
    #   Ilk yazimda `sablon` alani veriyordum -- ikisi de degil. Sonuc:
    #   cozucu kilidi TANIMADI (`notlar`a yazdi ve uygulamadi), dogrulayici
    #   da TANIMADI ve alti SERT ihlal yazdi. Ikisi de bagimsiz olarak ayni
    #   seyi soyledi (#7.6) -- motor bozuk girdiyi sessizce gecmedi.
    #
    #   T-45'in TERSI: orada taninmayan bir DEGER sessizce gecmisti,
    #   burada taninmayan bir BICIM iki taraftan da bildirildi.
    # ⚠ KILITLENECEK KISI O GUN CALISABILIYOR OLMALI
    #   Ilk yazimda `calisanlar[:4]` aliyordum. Ilk ikisi yari zamanliydi
    #   ve gun 2'de `uygun_degil` isaretliydi -- yani onlari gun 2'ye
    #   kilitlemek IKI SERT KURALI celistiriyordu. Plan gercekten
    #   imkansizdi ve motor hakliydi.
    #
    #   Celiskili kilit AYRI bir test konusudur (motor bunu duzgun
    #   bildiriyor mu). Ana veri setinin isi kilitlerin UYGULANDIGINI
    #   sinamak; o yuzden burada tutarli kisiler secilir.
    def _musait(c, gun):
        if c.get("durum", "aktif") != "aktif":
            return False
        if any(u.get("tip") == "uygun_degil" and u.get("gun") == gun
               for u in (c.get("uygunluk") or [])):
            return False
        if any(z.get("gun") == gun and z.get("durum", "onayli") == "onayli"
               for z in (c.get("izinler") or [])):
            return False
        return True

    kilitler = []
    for c in calisanlar:
        if len(kilitler) >= 4 or not _musait(c, 2):
            continue
        ek = c["ekipler"][0]
        uygun = [s for s in SABLONLAR if s["ekip"] == ek and "gunler" not in s]
        if not uygun:
            continue
        kilitler.append({"calisan": c["id"], "ekip": ek, "gun": 2,
                         "bas": uygun[0]["bas"], "bit": uygun[0]["bit"]})
    # Iki tane de YASAK kilidi -- ikinci bicim de sinansin. Yasak kilidi
    # celiski uretmez: zaten "calismasin" diyor.
    secili = {k["calisan"] for k in kilitler}
    for c in calisanlar:
        if len([k for k in kilitler if k.get("tip") == "yasak"]) >= 2:
            break
        if c["id"] not in secili:
            kilitler.append({"calisan": c["id"], "gun": 3, "tip": "yasak"})

    return {
        "ad": "S-20",
        "surum": "1.0",
        "_aciklama": [
            "GERCEKCI OLCEK -- Mustafa'nin 28 Eylul istegi.",
            "350 kisi, uc ekip, on dort vardiya sablonu, yedi gun.",
            "Hafta ici ve hafta sonu esikleri AYRI.",
            "Ekip basina ayri mola politikasi ve ayri yemek penceresi.",
            "Katalogdaki 39 kuralin TAMAMI tanimli: 24'u degerlendirilir,",
            "15'i `uygulanmayan_kurallar` kanalini atesler.",
            "Tohum sabit (%d) -- ayni girdi ayni dosyayi uretir." % TOHUM,
        ],
        "hafta_baslangic": "2026-10-12",
        "_hafta_notu": "12 Ekim Pazartesi = gun 0 ... 18 Ekim Pazar = gun 6",
        "kiraci_saat_dilimi": "Europe/Istanbul",
        "profil": "DENGELI",
        "calisanlar": calisanlar,
        "vardiya_sablonlari": sablonlar,
        "talep": talep,
        "kurallar": kurallar_uret(),
        "donmus_gunler": [0],
        "kilitler": kilitler,
        "sabit_atamalar": [],
        "devir_kapsama": [],
        "_olcek": olcek,
    }


if __name__ == "__main__":
    olcek = 1.0
    if "--olcek" in sys.argv:
        olcek = float(sys.argv[sys.argv.index("--olcek") + 1])
    s = sahne_uret(olcek)
    yol = sys.argv[sys.argv.index("--cikti") + 1] if "--cikti" in sys.argv \
        else "fikstur/_sahne-S20.json"
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    pt = sum(1 for c in s["calisanlar"]
             if c["sozlesme"]["tip"] in ("yari_zamanli", "stajyer"))
    print("%s yazildi" % yol)
    print("  calisan   : %d  (part-time %d, gunu kisitli %d)"
          % (len(s["calisanlar"]), pt,
             sum(1 for c in s["calisanlar"] if c.get("_calisabilir_gunler"))))
    print("  sablon    : %d" % len(s["vardiya_sablonlari"]))
    print("  talep     : %d hucre" % len(s["talep"]))
    print("  kural     : %d" % len(s["kurallar"]))
    print("  izinli    : %d" % sum(1 for c in s["calisanlar"] if c["izinler"]))
    print("  pasif     : %d" % sum(1 for c in s["calisanlar"]
                                    if c.get("durum", "aktif") != "aktif"))
    tipler = {}
    for c in s["calisanlar"]:
        t = c["sozlesme"]["tip"]
        tipler[t] = tipler.get(t, 0) + 1
    print("  sozlesme  : %s" % tipler)
