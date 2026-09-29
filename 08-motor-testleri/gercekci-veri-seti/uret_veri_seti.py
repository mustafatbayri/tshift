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
    {"id": "SATIS",      "ad": "Satis",              "kisi": 285, "yedi_yirmidort": True},
    {"id": "BACKOFFICE", "ad": "Back Office",        "kisi": 145, "yedi_yirmidort": True},
    {"id": "MHIZMET",    "ad": "Musteri Hizmetleri", "kisi": 70,  "yedi_yirmidort": False},
]
# ⚠ 500 KISI (Mustafa: "350-500"). Oran 200/100/50 ile ayni; en zor ucu
#   secildi. 28 Eylul setinde 350 kisi vardi.

# ----------------------------------------------------------------------
# Vardiya sablonlari
#
# ⚠ SURELER 45 SAATI TUTTURACAK SEKILDE SECILDI -- K-39 / T-51 (29 Eylul)
#   28 Eylul setinde SATIS'in en uzun vardiyasi 7,0 netti; 6 gunde 42 saat
#   ediyordu ve 45 saatlik sozlesme MATEMATIKSEL OLARAK tutturulamiyordu.
#   17 kisiden 45'i tutturan SIFIRDI -- ve plan yine de "0 sert ihlal,
#   yayinlanabilir: True" donuyordu.
#
#   Iki desen kuruldu, ikisi de tam 45 eder:
#       6 gun x 7,5 net       5 gun x 9,0 net
#
# ⚠ BRUT = NET + BUTUN MOLALAR (T-57, 29 Eylul -- BIR KEZ YANLIS KURULDU)
#   Ilk yazimda brut hesabina yalniz YEMEK katilmisti (7,5 + 1,0 = 8,5).
#   Oysa ucretli dinlenme molasi da calisma suresinden dusulur. Sonuc:
#   cozucu "45 saat oldu" derken bagimsiz dogrulayici 40,5 goruyordu ve
#   28 SERT ihlal yaziyordu. Dogru brut, mola politikasinin TAMAMINI
#   icerir:
#       SATIS      yemek 60 + 3x15 = 1,75 sa -> 9,25 ve 10,75 brut
#       BACKOFFICE yemek 45 + 2x15 = 1,25 sa -> 8,75 ve 10,25 brut
#       MHIZMET    yemek 30 + 3x20 = 1,50 sa -> 9,00 ve 10,50 brut
#   Hepsi ceyrek saat izgarasina (K-34) uyar.
#
# ⚠ GECE ISARETI KULLANICININ -- K-40 (29 Eylul)
#   `gece_vardiyasi` alani saat araligindan TAHMIN EDILMEZ, yazilir.
#   B-AKSAM (15:45-24:00) bilerek gece isaretli: saat penceresi onu "gece"
#   sayardi ama firmanin tanimi onceliklidir -- test edilen sey bu.
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
    # --- SATIS : 7/24 ---
    # Yemek 60 dk -> net = brut - 1,0
    {"id": "S-SABAH", "ekip": "SATIS", "bas": 7,     "bit": 16.25, "mola_dk": 60,
     "gece_vardiyasi": False},
    {"id": "S-ARA",   "ekip": "SATIS", "bas": 11,    "bit": 20.25, "mola_dk": 60,
     "gece_vardiyasi": False,
     "_not": "Yogun saat takviyesi -- SABAH ve AKSAM ile bilerek ortusur."},
    {"id": "S-AKSAM", "ekip": "SATIS", "bas": 13.75, "bit": 23,    "mola_dk": 60,
     "gece_vardiyasi": False},
    {"id": "S-GECE",  "ekip": "SATIS", "bas": 23,    "bit": 32.25, "mola_dk": 60,
     "gece_vardiyasi": True,
     "_not": "23:00-07:30. Genisletilmis saat (Z-1): gun sinirini asar."},
    {"id": "S-UZUN",  "ekip": "SATIS", "bas": 8,     "bit": 18.75, "mola_dk": 60,
     "gece_vardiyasi": False,
     "_not": "5 gunluk desen: 9,0 net x 5 = 45 saat."},
    {"id": "S-KISA",  "ekip": "SATIS", "bas": 10,   "bit": 16,   "mola_dk": 30,
     "gece_vardiyasi": False, "_not": "Yari zamanli bicimi, 5,5 net."},

    # --- BACKOFFICE : 7/24 ; yemek 45 dk -> net = brut - 0,75 ---
    {"id": "B-SABAH", "ekip": "BACKOFFICE", "bas": 8,     "bit": 16.75, "mola_dk": 45,
     "gece_vardiyasi": False},
    {"id": "B-ARA",   "ekip": "BACKOFFICE", "bas": 11.25, "bit": 20,    "mola_dk": 45,
     "gece_vardiyasi": False},
    {"id": "B-AKSAM", "ekip": "BACKOFFICE", "bas": 15.25, "bit": 24,    "mola_dk": 45,
     "gece_vardiyasi": True,
     "_not": "15:45-24:00 -- aksam ama gece penceresine giriyor; isaret KULLANICININ."},
    {"id": "B-GECE",  "ekip": "BACKOFFICE", "bas": 0,     "bit": 8.75,  "mola_dk": 45,
     "gece_vardiyasi": True, "_not": "00:00-08:15."},
    {"id": "B-UZUN",  "ekip": "BACKOFFICE", "bas": 8,     "bit": 18.25, "mola_dk": 45,
     "gece_vardiyasi": False, "_not": "5 gunluk desen: 9,0 net x 5 = 45."},
    {"id": "B-YARIM", "ekip": "BACKOFFICE", "bas": 9,     "bit": 13,    "mola_dk": 0,
     "gece_vardiyasi": False,
     "_not": "4 saat -- MOLA_HAKKI'nin en dusuk esigi (<=4sa: 15dk)."},

    # --- MUSTERI HIZMETLERI : 08-22 ; yemek 30 dk -> net = brut - 0,5 ---
    {"id": "M-SABAH",  "ekip": "MHIZMET", "bas": 8,    "bit": 17,   "mola_dk": 30,
     "gece_vardiyasi": False},
    {"id": "M-AKSAM",  "ekip": "MHIZMET", "bas": 13,   "bit": 22,   "mola_dk": 30,
     "gece_vardiyasi": False},
    {"id": "M-UZUN",   "ekip": "MHIZMET", "bas": 8,    "bit": 18.5, "mola_dk": 30,
     "gece_vardiyasi": False, "_not": "5 gunluk desen: 9,0 net x 5 = 45."},
    {"id": "M-HSONU",  "ekip": "MHIZMET", "bas": 10,   "bit": 18,   "mola_dk": 30,
     "gece_vardiyasi": False, "gunler": [5, 6],
     "_not": "Yalniz hafta sonu -- `gunler` alani kisitlar."},
    {"id": "M-AKSAMK", "ekip": "MHIZMET", "bas": 17,   "bit": 21,   "mola_dk": 0,
     "gece_vardiyasi": False, "_not": "Yari zamanli aksam bicimi, 4 saat."},
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
#
# ⚠ K-39 (29 Eylul) IKI SEYI DEGISTIRDI
#   1. Tam zamanlinin sozlesmesine `gun_sayisi` girdi. Onsuz izin saate
#      cevrilemiyor: ayni 45 saat, 6 gunluk desende bir izin gunu 7,5
#      saat; 5 gunluk desende 9,0 saat eder.
#   2. Yari zamanlida `haftalik_saat` alani KALKTI. Mustafa: "Hicbir
#      calisan icin bu 20 saat calisir gibi bir deger atamayacagiz.
#      Sadece calisanin calisabilecegi uygun olmayan gunler var ise
#      bunlari belirtecegiz." Tavan mevzuattan gelir (45 saat).
#
# Oran 70/30 (Mustafa): tam zamanli %70, yari zamanli %30 civari.
SOZLESMELER = [
    ({"tip": "tam_zamanli",  "haftalik_saat": 45, "gun_sayisi": 6}, 0.42),
    ({"tip": "tam_zamanli",  "haftalik_saat": 45, "gun_sayisi": 5}, 0.28),
    ({"tip": "yari_zamanli"},                                       0.26),
    ({"tip": "sezonluk",     "haftalik_saat": 40},                  0.02),
    ({"tip": "stajyer",      "haftalik_saat": 30},                  0.02),
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

            # GECE_UYGUNLUGU (K-40): birkac kisi gece calisamaz.
            # ⚠ Mustafa: "Gece vardiyalari genelde yari zamanlilara
            #   yaptiriliyor" -- o yuzden oran yari zamanlida DAHA DUSUK
            #   tutuldu; kural yine de ikisinde de ateslenir.
            if rnd.random() < (0.08 if soz["tip"] == "yari_zamanli" else 0.14):
                c["gece_calisamaz"] = True

            # ONAYLI_IZIN: ~%8 izinli, biri REDDEDILMIS (durum alani sinansin)
            # ⚠ Oran %8 -> %12: gercek bir haftada izin yogunlugu bu civarda
            #   ve K-39 ile izin artik SOZLESME BORCUNU dusuruyor -- yani
            #   bu oran kuralin en kritik yolunu besliyor.
            if rnd.random() < 0.12:
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


PART_TIME_PLANLAMA_SAATI = 30
# ⚠ Yari zamanlinin sozlesmesinde artik saat YOK (K-39). Kapasite hesabi
#   icin bir sayi gerekiyor ve o sayi 30: mevzuatin kismi sureli tanimindaki
#   esik (emsalin 2/3'u) ve Mustafa'nin "yari zamanlilari 30 saat planlamaya
#   calis, 30'u olabildigince asma" dedigi deger. TAVAN degil, PLANLAMA
#   varsayimi -- sert tavan 45'tir.


def kapasite_saat(calisanlar):
    """Haftalik planlanabilir saat toplami -- talep olceklemesinin paydasi."""
    top = 0.0
    for c in calisanlar:
        if c.get("durum", "aktif") != "aktif":
            continue
        soz = c.get("sozlesme") or {}
        if soz.get("tip") == "yari_zamanli":
            top += PART_TIME_PLANLAMA_SAATI
        else:
            top += float(soz.get("haftalik_saat") or 0)
    return top


def talep_uret(olcek, carpan=1.0):
    """Hucre basina talep -- hafta ici / hafta sonu AYRI esiklerle.

    `carpan` DOLULUK icin: talep toplami kapasitenin istenen yuzdesine
    gelsin diye butun esikler ayni oranda olceklenir. Gunun sekli
    (sabah yogunlugu, gece dip) bozulmaz.
    """
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
                        "asgari": max(1, int(round(asgari * olcek * carpan))),
                        "hedef": max(1, int(round(hedef * olcek * carpan))),
                        "_sahada_taban": max(1, int(round(taban * olcek * carpan))),
                        "_gun_tipi": tip,
                    })
    return cikan


def kurallar_uret():
    """Katalogdaki 40 kuralin TAMAMI.

    GOVDESI YAZILI 26 -> gercekten degerlendirilir.
    YAZILMAMIS 14     -> aktif tanimlanir ki `uygulanmayan_kurallar` kanali
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
    # K-39: SAAT_DENGESI artik SERT ve govdesi IKI tarafta da yazili.
    ek("SAAT_DENGESI", "SERT", kabul=True, tolerans_saat=0)
    # K-40: gece uygunlugu.
    ek("GECE_UYGUNLUGU", "SERT", kabul=False)

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
            ("TERCIH_KARSILAMA", "YUMUSAK", False),
            ("VARDIYA_ROTASYON_YONU", "YUMUSAK", False),
            ("YILLIK_FAZLA_MESAI_TAVANI", "SERT", True)):
        ek(kod, tur, yasal=yasal, kabul=False)
    return K


def sahne_uret(olcek=1.0, doluluk=0.95):
    """Sahneyi uretir. `doluluk` = hedef talep / planlanabilir kapasite.

    ⚠ NEDEN IKI SET (Mustafa, 29 Eylul: "2 veri seti yapalim biri %85 biri %95")
      %95 : kadro sikidir; izinlerle birlikte fazla mesai ZORUNLU hale gelir.
            Turkiye gercegi -- "eleman yetmiyor, fazla mesaiye gidiliyor."
      %85 : kadroda bolluk var. Burada olculen sey solver'in kirilmasi degil,
            PARA: sozlesmeyle odenen ama talebin emmedigi saat.

      Ikisi arasindaki TEK fark talep tablosudur. Ayni kisiler, ayni
      sablonlar, ayni kurallar -- yoksa aradaki farkin neyden geldigi
      soylenemez.
    """
    rnd = random.Random(TOHUM)
    calisanlar = calisanlar_uret(rnd, olcek)

    # Talep, kapasitenin `doluluk` katina gelecek sekilde olceklenir.
    kapasite = kapasite_saat(calisanlar)
    ham = sum(t["hedef"] for t in talep_uret(olcek, 1.0))
    carpan = (doluluk * kapasite / ham) if ham else 1.0
    talep = talep_uret(olcek, carpan)

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
        "ad": "S-30-%d" % round(doluluk * 100),
        "surum": "2.0",
        "_doluluk": round(doluluk, 4),
        "_carpan": round(carpan, 4),
        "_kapasite_saat": round(kapasite, 1),
        "_hedef_kisi_saat": sum(t["hedef"] for t in talep),
        "_aciklama": [
            "ZOR OLCEK -- Mustafa'nin 29 Eylul istegi.",
            "500 kisi, uc ekip, on yedi vardiya sablonu, yedi gun.",
            "Tam zamanli %70 / yari zamanli %30.",
            "Sablonlar 45 saati TUTTURABILIR (6x7,5 ve 5x9,0 desenleri).",
            "Yari zamanlida sozlesme saati YOK; haftayi uygunluk sekillendirir.",
            "Gece vardiyalari ISARETLI; bir kisim calisan gece calisamaz.",
            "Hafta ici ve hafta sonu esikleri AYRI.",
            "Ekip basina ayri mola politikasi ve ayri yemek penceresi.",
            "Katalogdaki 40 kuralin TAMAMI tanimli: 26'si degerlendirilir,",
            "14'u `uygulanmayan_kurallar` kanalini atesler.",
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
    hedefler = [("fikstur/_sahne-S30-85.json", 0.85),
                ("fikstur/_sahne-S30-95.json", 0.95)]
    if "--doluluk" in sys.argv:
        d = float(sys.argv[sys.argv.index("--doluluk") + 1])
        yol = sys.argv[sys.argv.index("--cikti") + 1] if "--cikti" in sys.argv \
            else "fikstur/_sahne-S30-%d.json" % round(d * 100)
        hedefler = [(yol, d)]

    for yol, doluluk in hedefler:
        s = sahne_uret(olcek, doluluk)
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
        tipler = {}
        for c in s["calisanlar"]:
            t = c["sozlesme"]["tip"]
            tipler[t] = tipler.get(t, 0) + 1
        print("%s  (doluluk %%%d)" % (yol, round(doluluk * 100)))
        print("  calisan   : %d   %s" % (len(s["calisanlar"]), tipler))
        print("  kapasite  : %.0f kisi-saat/hafta" % s["_kapasite_saat"])
        print("  hedef     : %d kisi-saat  (kapasitenin %%%.1f'i)"
              % (s["_hedef_kisi_saat"],
                 100.0 * s["_hedef_kisi_saat"] / s["_kapasite_saat"]))
        print("  sablon    : %d   talep: %d hucre   kural: %d"
              % (len(s["vardiya_sablonlari"]), len(s["talep"]),
                 len(s["kurallar"])))
        print("  izinli    : %d   gece calisamaz: %d   pasif: %d"
              % (sum(1 for c in s["calisanlar"] if c["izinler"]),
                 sum(1 for c in s["calisanlar"] if c.get("gece_calisamaz")),
                 sum(1 for c in s["calisanlar"]
                     if c.get("durum", "aktif") != "aktif")))
