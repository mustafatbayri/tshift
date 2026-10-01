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

import copy
import json
import random
import sys

TOHUM = 20260928

# ----------------------------------------------------------------------
# Organizasyon -- Mustafa'nin verdigi dagilim
# ----------------------------------------------------------------------
EKIPLER = [
    {"id": "SATIS",      "ad": "Satis",              "kisi": 285, "yedi_yirmidort": True,  "departman": "D-SATIS"},
    {"id": "BACKOFFICE", "ad": "Back Office",        "kisi": 145, "yedi_yirmidort": True,  "departman": "D-BACK"},
    {"id": "MHIZMET",    "ad": "Musteri Hizmetleri", "kisi": 70,  "yedi_yirmidort": False, "departman": "D-MHIZMET"},
]

# DEPARTMANLAR -- CALISMA_SAATLERI icin (K-52, Mustafa 1 Ekim: "Sistemde
# departman tanimi lazim ve ilgili departmana calisma gunleri ile saatlerini
# tanimlamaliyiz").
#
#   Satis ve back office 7/24 (cagri merkezi). Musteri hizmetleri hafta ici
#   07:00-23:00, hafta sonu 08:00-19:00 -- yani hafta sonu M-AKSAM (13-22) ve
#   M-AKSAMK (17-21) KAPALI SAATE tasar, kural orada gercekten isirir;
#   hafta sonu talebi (10-18) M-SABAH, M-UZUN ve M-HSONU ile karsilanir.
#
#   Pencere `bit` 24'u asabilir (31 = ertesi gun 07:00): gece yarisini
#   asan vardiya acik sayilsin diye.
DEPARTMANLAR = [
    {"id": "D-SATIS",   "ad": "Satis Departmani",     "ekipler": ["SATIS"],
     "acik": "7/24"},
    {"id": "D-BACK",    "ad": "Back Office",           "ekipler": ["BACKOFFICE"],
     "acik": "7/24"},
    {"id": "D-MHIZMET", "ad": "Musteri Hizmetleri",    "ekipler": ["MHIZMET"],
     "acik": [{"gunler": [0, 1, 2, 3, 4], "bas": 7, "bit": 23},
              {"gunler": [5, 6], "bas": 8, "bit": 19}]},
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
# Gunduz penceresi -- ROL_KAPSAMASI gereklilik satirlari bunu kullanir.
# 08:00-20:00. Gece postasinda takim lideri zorunlu degil (T-63).
GUNDUZ_BAS, GUNDUZ_BIT = 8, 20

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


# Gereklilik satiri "gunduz boyunca 1 takim lideri" istiyor (T-63). Kac
# lider gerekir, sayarak:
#
#   gunduz penceresi 12 saat, en uzun vardiya ~10,5 saat
#     -> bir gunu kapatmak icin EN AZ 2 lider
#   HAFTA_TATILI her calisana 1 gun tatil verir
#     -> haftada 2x7 = 14 lider-gunu gerekiyor, kisi basina 6 gun var
#     -> ceil(14/6) = 3 lider
#   izin/rapor payi
#     -> +1  =>  EKIP BASINA 4
#
# ⚠ BU BIR ORAN DEGIL, TABAN. Rol dagilimi %8 lider veriyor; 500 kiside
#   bu 21/15/6 ediyor ve taban zaten asiliyor. Ama 0.1 olcekte 2/2/0
#   ediyor ve gereklilik KANITLANARAK cozumsuz kaliyor: 2 lider x 6 gun =
#   12 lider-gunu, gereken 14.
#
# ⚠ OLCULDU (30 Eylul): 0.1 olcekte ekip basina 4 TAM ZAMANLI ve izinsiz
#   lider varken sahne 79 saniyede cozuldu. Yalniz sayiyi 4'e cikarmak
#   YETMEDI -- promosyon yari zamanliya ya da izinliye denk gelince plan
#   yine cozumsuz kaldi. Yani taban "4 kisi" degil, "gunduz vardiyasi
#   yazilabilecek 4 kisi".
#
# ⚠ KUCUK OLCEKTE BU ORANI BOZAR: 7 kisilik MHIZMET ekibinde 4 lider
#   demek kisilerin yarisindan fazlasi lider demektir. Gercekci degil --
#   ama 7 kisiyle 7/24 kapsama da gercekci degil; o sahne zaten bir
#   kucultme yapisidir. Alternatif, firmanin kendi kuralini tutamayan bir
#   veri seti olurdu.
LIDER_TABANI = 4


def _lider_tabani_uygula(calisanlar):
    """Her ekipte gunduz vardiyasi yazilabilecek en az LIDER_TABANI lider.

    Aday sirasi bilerek dar: tam zamanli, aktif, izinsiz. Boyle bir aday
    kalmazsa taban tutulmaz -- sessizce zorlamak yerine eksik birakilir ve
    sahne kendi sinirini gosterir.
    """
    ekipler = {}
    for c in calisanlar:
        for e in (c.get("ekipler") or []):
            ekipler.setdefault(e, []).append(c)
    for kisiler in ekipler.values():
        lider = [c for c in kisiler
                 if c.get("operasyonel_rol") == "takim_lideri"
                 and c.get("durum", "aktif") == "aktif"
                 and not c.get("izinler")
                 and (c.get("sozlesme") or {}).get("tip") == "tam_zamanli"]
        if len(lider) >= LIDER_TABANI:
            continue
        adaylar = [c for c in kisiler
                   if c.get("operasyonel_rol") != "takim_lideri"
                   and c.get("durum", "aktif") == "aktif"
                   and not c.get("izinler")
                   and (c.get("sozlesme") or {}).get("tip") == "tam_zamanli"]
        for c in adaylar:
            if len(lider) >= LIDER_TABANI:
                break
            c["operasyonel_rol"] = "takim_lideri"
            lider.append(c)
    return calisanlar


# YETKINLIK GEREKLILIKLERI (K-52'nin yetkinlik yarisi, Mustafa 1 Ekim:
# "her birim icin tanimlamaliyiz bu ingilizce kuralini... olabildigince
# kompleks kurgu"). Her satir: ekip, yetkinlik, saatler, asgari, taban.
#
#   Taban hesabi liderdekiyle ayni: pencere / en uzun vardiya -> gunde kac
#   kisi; x7 gun / 6 is gunu; +1 izin payi; asgari ile carp.
#     SATIS   ingilizce 08-20 asgari 2 : 2 kisi/gun -> 14/6 -> 3+1 = 4, x2 = 8
#     BACK    ingilizce 08-18 asgari 1 : 1 kisi/gun ->  7/6 -> 2+1 = 3
#     MHIZMET ingilizce 08-22 asgari 1 : 2 kisi/gun -> 14/6 -> 3+1 = 4
#     MHIZMET almanca   10-16 asgari 1 : 1 kisi/gun ->  7/6 -> 2+1 = 3
YETKINLIK_GEREKLILIKLERI = [
    {"ekip": "SATIS",      "yetkinlik": "ingilizce", "saatler": list(range(8, 20)),  "asgari": 2, "taban": 8},
    {"ekip": "BACKOFFICE", "yetkinlik": "ingilizce", "saatler": list(range(8, 18)),  "asgari": 1, "taban": 3},
    {"ekip": "MHIZMET",    "yetkinlik": "ingilizce", "saatler": list(range(8, 22)),  "asgari": 1, "taban": 4},
    {"ekip": "MHIZMET",    "yetkinlik": "almanca",   "saatler": list(range(10, 16)), "asgari": 1, "taban": 3},
]


def _yetkinlik_tabani_uygula(calisanlar):
    """Her gereklilik icin ekipte gunduz yazilabilecek en az `taban` kisi o
    yetkinligi tasisin -- lider tabaniyla ayni mantik ve ayni dar aday
    sirasi (tam zamanli, aktif, izinsiz). Var olan tasiyici sayilir; eksik
    kalirsa adaylara yetkinlik EKLENIR (listeye; var olanlar silinmez)."""
    ekipler = {}
    for c in calisanlar:
        for e in (c.get("ekipler") or []):
            ekipler.setdefault(e, []).append(c)
    for g in YETKINLIK_GEREKLILIKLERI:
        kisiler = ekipler.get(g["ekip"], [])
        uygun = [c for c in kisiler
                 if c.get("durum", "aktif") == "aktif" and not c.get("izinler")
                 and (c.get("sozlesme") or {}).get("tip") == "tam_zamanli"]
        tasiyan = [c for c in uygun if g["yetkinlik"] in (c.get("yetkinlikler") or [])]
        if len(tasiyan) >= g["taban"]:
            continue
        for c in uygun:
            if len(tasiyan) >= g["taban"]:
                break
            if g["yetkinlik"] not in (c.get("yetkinlikler") or []):
                c["yetkinlikler"] = list(c.get("yetkinlikler") or []) + [g["yetkinlik"]]
                tasiyan.append(c)
    return calisanlar


def calisanlar_uret(rnd, olcek, rnd_yil=None):
    """Calisan listesi -- sozlesme, rol, yetkinlik, izin, uygunluk, devir yuku."""
    rnd_yil = rnd_yil or random.Random(TOHUM + 1)
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
                # YILLIK_FAZLA_MESAI_TAVANI (1 Ekim, K-49 ile govdesi yazildi):
                # yil ici fazla mesai toplami. Ekim ortasi icin cogunluk 0-150
                # saat (tavana uzak, kural zorlanmaz); her 50 kisiden biri
                # 262-269 saatte -- tavana 1-8 saat kalmis, kural ISIRIR.
                # ⚠ VARSAYIM: gercek dagilim bilinmiyor (06-veri/anonim bos).
                # Ayri tohumlu uretecle: ana uretecin sirasi bozulmasin, 30
                # Eylul'den beri uretilen sahne (izin, yetkinlik, uygunluk)
                # AYNEN kalsin.
                "yil_ici_fazla_mesai_saat": (rnd_yil.randint(262, 269)
                                             if rnd_yil.random() < 0.02
                                             else rnd_yil.randint(0, 150)),
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

    GOVDESI YAZILI 33 -> gercekten degerlendirilir.
    YAZILMAMIS 7      -> aktif tanimlanir ki `uygulanmayan_kurallar` kanali
                         gercekten atessin. Sessizce dislamak, kanali test
                         etmemek demektir (T-18 tam bu kapida bekliyor).

    ⚠ TANIMLI OLMAK, ISTEMEK DEGILDIR -- T-63 (30 Eylul)
      30 Eylul'e kadar `ROL_KAPSAMASI` ve `YETKINLIK_KAPSAMASI` burada
      `parametreler` ALANI OLMADAN tanimliydi: aktif, ama hicbir sey
      istemiyor. Govdeleri yazildiginda bekciler yesil kaldi ve sebebi
      buydu. `SAHADA_ASGARI` de ayni durumda (asgari_sahada 0).

      Yani "40 kuralin hepsi tanimli" cumlesi dogruydu ve HICBIR SEY
      soylemiyordu. Bu, 29 Eylul'de kod tarafinda yapilan hatanin veri
      tarafindaki ayni hali.
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

    # --- Firma sinirlari (30 Eylul) -- katalogun varsayilanlariyla ---
    #
    # ⚠ ASGARI_VARDIYA_SURESI veri setinde ISIRMAZ: en kisa sablonlar
    #   (B-YARIM 09-13, M-AKSAMK 17-21) tam 4 saat. Zorlayan ihlal vakasi.
    # ⚠ ARDISIK_GECE_LIMIT ISIRABILIR: B-AKSAM (15:15-24:00) gece isaretli;
    #   backoffice'te ust uste 4 aksam artik yazilamaz.
    ek("ASGARI_VARDIYA_SURESI", "SERT", kabul=True, asgari_saat=4)
    ek("ARDISIK_GECE_LIMIT", "SERT", kabul=True, azami_gece=3)

    # --- GECE_VARDIYASI_AZAMI: YASAL, Is K. md. 69 (K-26) ---
    #
    # ⚠ BU SAHNEDE KURAL IHLAL URETMEZ -- acikca yaziyorum.
    #   En uzun gece ortusmesi S-GECE'de 7,00 saat, sinir 7,5. Yani kural
    #   aktif ve tanimli ama veri setinin sablonlari onu ZORLAMIYOR; onu
    #   zorlayan ihlal vakasi ve birim testleri. Sablonlari sinirin
    #   ustune cikarmak yasadisi bir firma kurmak olurdu.
    #
    # ⚠ SEKTOR BILEREK ISTISNA DISI (`cagri_merkezi`, asagida). Istisnali
    #   bir sektorde yazili onayli calisanlar icin sinir kalkar; en zor
    #   hal sinirin herkes icin yururlukte oldugu haldir.
    ek("GECE_VARDIYASI_AZAMI", "SERT", yasal=True, kabul=False,
       azami_saat=7.5, pencere_bas=20, pencere_bit=6)

    # --- ROL_KAPSAMASI: gerceklilik satirlari (T-63, Mustafa 30 Eylul) ---
    #
    # Mustafa'nin secimi: "Yalniz gunduz saatlerinde 1 lider."
    #
    # ⚠ SAAT ARALIGI BENIM SECIMIM, MUSTAFA SAAT VERMEDI -- acikca yaziyorum.
    #   GUNDUZ = 08:00-20:00, yani saat 8'den 19'a kadarki hucreler.
    #   Gece postasinda takim lideri ZORUNLU DEGIL; 7/24 kapsamada her
    #   saate lider istemek 42 liderle tutulamazdi ve olculmeden
    #   varsayilmis bir gereklilik olurdu.
    #
    # ⚠ HER EKIP AYRI SATIR. K-24: bu kuralda gereklilik SATIR bazlidir ve
    #   her satir kendi `yasal` bayragini tasir. "Ekipte lider olsun" ticari
    #   bir tercihtir, yasal degil -- bu yuzden kabul edilebilir isaretli:
    #   yonetici gorup onaylayabilir, plan bu yuzden yayindan dusmez.
    #
    # ⚠ OLCU ATANMIS OLMAKTIR, SAHADA OLMAK DEGIL -- K-41. Molada olan
    #   lider de sayilir.
    for e in EKIPLER:
        ek("ROL_KAPSAMASI", "SERT", kabul=True,
           rol="takim_lideri", ekip=e["id"], asgari=1,
           saatler=list(range(GUNDUZ_BAS, GUNDUZ_BIT)))

    # --- YETKINLIK_KAPSAMASI: her gereklilik AYRI satir (1 Ekim, T-63 kapandi) ---
    #
    # Mustafa: "her birim icin tanimlamaliyiz bu ingilizce kuralini."
    # Satirlar YETKINLIK_GEREKLILIKLERI'nde; ticari tercih, kabul edilebilir
    # (K-24 satir bazli bayrak). Olcu atanmis olmaktir (K-41).
    for g in YETKINLIK_GEREKLILIKLERI:
        ek("YETKINLIK_KAPSAMASI", "SERT", kabul=True,
           yetkinlik=g["yetkinlik"], ekip=g["ekip"], asgari=g["asgari"],
           saatler=list(g["saatler"]))

    # --- Hafta olcekli iki kural (30 Eylul) -- katalogun varsayilanlariyla ---
    #
    # ⚠ BU SAHNEDE IKISI DE ISIRMAZ -- acikca yaziyorum. Sahne TEK HAFTA
    #   ve GECMISSIZ; ikisi de planin DISINA bakar ("gecen hafta da gece
    #   calisti mi", "gecen iki hafta sonu da calisti mi"). Bilinmeyen
    #   gecmis kisit yaratmaz (K-42); yalniz `gecmis_eksik` raporu yazilir.
    #   Ikisini zorlayan: ihlal vakalari (gecmis ekleyerek) ve
    #   `iki-hafta-olc.py` (hafta 1'in plani hafta 2'nin gecmisi olur).
    # ⚠ ARDISIK_HAFTA_SONU_LIMIT 30 Eylul'e kadar burada "kabul edilemez"
    #   tanimliydi; sartname #6.5 KABUL EDILEBILIR diyor. Duzeltildi.
    ek("GECE_POSTASI_DEVRI", "SERT", yasal=True, kabul=False,
       azami_ardisik_gece_haftasi=1)
    ek("ARDISIK_HAFTA_SONU_LIMIT", "SERT", kabul=True, azami_ardisik=2)

    # --- 1 Ekim'de govdesi yazilanlar (K-49 kapiyi kapatinca) ---
    # YILLIK_FAZLA_MESAI_TAVANI: yasal, 270 saat; calisanlarda yil ici toplam
    # var, her 50 kisiden biri tavanin kiyisinda. GECE_YARISI_ASAN: hesaplama
    # kurali, govdesi "ihlal uretmez" diye kayitli (T-67).
    ek("YILLIK_FAZLA_MESAI_TAVANI", "SERT", yasal=True, kabul=False,
       azami_saat_yil=270)
    ek("GECE_YARISI_ASAN", "SERT", kabul=False)

    # HEDEF_ASIMI (K-53, 1 Ekim, T-54): hedefi asan kisi-saat ceza --
    # YUMUSAK; agirlik profilden (#5.4). Bir saatin bedeli artik var.
    ek("HEDEF_ASIMI", "YUMUSAK")

    # CALISMA_SAATLERI (K-52, 1 Ekim): departman calisma saatleri
    # DEPARTMANLAR'da; kapali saate tasan vardiya yazilamaz. Firma kurali,
    # kabul edilebilir.
    ek("CALISMA_SAATLERI", "SERT", kabul=True)

    # --- govdesi YAZILMAMIS olanlar (uygulanmayan_kurallar atessin) ---
    # Dort yumusak kural: K-49 ile yalniz raporlanir, kapiyi etkilemez.
    for kod, tur, yasal in (
            ("EKIP_SUREKLILIGI", "YUMUSAK", False),
            ("PLAN_KARARLILIGI", "YUMUSAK", False),
            ("TERCIH_KARSILAMA", "YUMUSAK", False),
            ("VARDIYA_ROTASYON_YONU", "YUMUSAK", False)):
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
    rnd_yil = random.Random(TOHUM + 1)       # yil ici fazla mesai icin ayri akis
    calisanlar = _yetkinlik_tabani_uygula(
        _lider_tabani_uygula(calisanlar_uret(rnd, olcek, rnd_yil)))

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

    # KILIT_UYUMU: birkac atama kilitli (gun 2 sabitleme, gun 3 yasak).
    #
    # ⚠ DONMUS GUN BU SAHNEDE YOK (K-54, 1 Ekim). 1 Ekim'e kadar sahne
    #   `donmus_gunler: [0]` yaziyordu ama kural OLUYDU (T-29): ne cozucu ne
    #   dogrulayici gun 0'a farkli davraniyordu -- alan sahneyi hic
    #   etkilemedi. Kural canlaninca donmus gun, yayinlanmis plan
    #   (`mevcut_plan`) ister; plansiz donmus gun dogrulayicida
    #   "denetlenemedi" olur ve kapi kabul bekler. Bu sahne TAZE HAFTA
    #   planlar (yayinlanmis plan yok), o yuzden alan artik bos.
    #   Donmus gun yolu ayrica olculur: `coz-olc.py --donmus` (tam olcek,
    #   motorun kendi gun 0 planini dondurup yeniden planlar) ve
    #   bekci `test_DONMUS_gun_yeniden_planlamada_korunur` (0.1 olcek).
    #   Cozucu icin sahnenin zorlugu DEGISMEDI: onceki olcumlerle
    #   karsilastirilabilir.
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
            "Katalogdaki 41 kuralin TAMAMI tanimli: 37'si degerlendirilir,",
            "4 yumusak kural `uygulanmayan_kurallar` kanalini atesler (yalniz",
            "rapor -- K-49).",
            "Departman calisma saatleri: satis ve back office 7/24, musteri",
            "hizmetleri hafta ici 07-23, hafta sonu 08-19 (K-52).",
            "Donmus gun YOK: taze hafta; donmus gun yolu coz-olc.py --donmus",
            "ve bekcideki yeniden planlama testiyle olculur (K-54).",
            "Yetkinlik gereklilikleri: satis 2 ingilizce (08-20), back office",
            "1 ingilizce (08-18), musteri hizmetleri 1 ingilizce (08-22) ve",
            "1 almanca (10-16) -- tabanlar lider tabaniyla ayni hesapla.",
            "Sektor istisna DISI (cagri merkezi): gece 7,5 saat siniri herkese.",
            "Tohum sabit (%d) -- ayni girdi ayni dosyayi uretir." % TOHUM,
        ],
        "hafta_baslangic": "2026-10-12",
        # K-26: GECE_VARDIYASI_AZAMI'nin sektor istisnasi buna bakar.
        # Bilerek istisna DISI -- sinir herkes icin yururlukte (en zor hal).
        "sektor": "cagri_merkezi",
        "_hafta_notu": "12 Ekim Pazartesi = gun 0 ... 18 Ekim Pazar = gun 6",
        "kiraci_saat_dilimi": "Europe/Istanbul",
        "profil": "DENGELI",
        "calisanlar": calisanlar,
        "vardiya_sablonlari": sablonlar,
        "talep": talep,
        "kurallar": kurallar_uret(),
        "donmus_gunler": [],          # K-54: taze hafta -- bkz. yukaridaki not
        "kilitler": kilitler,
        "sabit_atamalar": [],
        "devir_kapsama": [],
        # K-49 / T-18: kontrol edilemeyen kural kapidan gecemez. Bu sette
        # artik kabul kaydi GEREKMIYOR -- yetkinlik gereklilikleri yazildi
        # (T-63), calisma saatleri departman tanimiyla geldi (K-52). Alan
        # bos ama acikca yazili: okuyan "yok" ile "unutulmus"u ayirsin.
        "denetim_disi_kabul": [],
        # K-52: departmanlar ve calisma saatleri.
        "departmanlar": copy.deepcopy(DEPARTMANLAR),
        # K-50: cok ekipli calisan sayimi. Bu sette herkes TEK ekipte;
        # varsayilan (`hepsi`) acikca yazili ki okuyan bilsin.
        "cok_ekipli_sayim": "hepsi",
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
