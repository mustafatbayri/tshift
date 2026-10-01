# -*- coding: utf-8 -*-
"""
COZUCU MODELI -- CP-SAT (Master Spec v1.4 #11.2, M-09)

BU DOSYA DOGRULAYICIDAN BAGIMSIZDIR -- #7.6, #16.1

  `dogrulayici/` altindaki HICBIR modul import edilmez. Zaman aritmetigi
  burada IKINCI KEZ, bagimsiz olarak yazildi. Bu bilerek yapilan bir
  tekrardir.

  Sebebi D-6 sinifi hata: kodu yazan testi de yazarsa ayni yanlis varsayim
  iki yere birden gecer ve hicbir test yakalamaz. Dogrulayici ancak
  cozucuden bagimsizsa onu denetleyebilir.

  "Ayni hesabi iki kez yazmayalim" diyip ortak bir modul cikarmak
  YASAKTIR. Tekrar burada maliyet degil, guvencedir.

  Bilerek FARKLI kuruldu: dogrulayici mutlak saat araliklariyla calisir,
  cozucu SAAT DILIMI (slot) tabanlidir. Ayni sonuca iki ayri yoldan
  varmalari, ikisinin birden yanlis olma ihtimalini dusurur.

MODEL
  x[e,d,t]      calisan e, gun d, sablon t ile calisiyor mu
  m[e,d,t,s]    o vardiyanin molasi s diliminde basliyor mu

  Sert kurallar kisit, yumusak kurallar amac fonksiyonunda ceza.
"""

import math
import os

from ortools.sat.python import cp_model

# Modelde saatler TAM SAYI dilimdir. Genisletilmis saat: 25 = ertesi gun 01:00.
HAFTA_GUN = 7


# ----------------------------------------------------------------------
# Arama iscisi sayisi -- 29 Eylul
# ----------------------------------------------------------------------

def cekirdek_sayisi():
    """Bu SURECIN kullanabilecegi cekirdek sayisi. Hicbir zaman 0 donmez.

    ⚠ NEDEN `os.cpu_count()` TEK BASINA YETMEZ
      `os.cpu_count()` MAKINENIN cekirdegini sayar, bu surece AYRILANI
      degil. Iki cekirdege sinirlanmis bir kap icinde de "32" cevabi
      gelebilir -- ve duzeltmeye calistigimiz hata tam olarak budur. Once
      surece ayrilan sayi sorulur, o okunamazsa makineninki kullanilir.

    Okunamazsa 1'e duser: cozucuye 0 vermek onu patlatirdi.
    """
    okuyucular = [getattr(os, "process_cpu_count", None)]
    if hasattr(os, "sched_getaffinity"):
        okuyucular.append(lambda: len(os.sched_getaffinity(0)))
    okuyucular.append(os.cpu_count)
    for oku in okuyucular:
        if oku is None:
            continue
        try:
            n = oku()
        except Exception:
            continue
        if n:
            return max(1, int(n))
    return 1


def isci_sayisi(ayar=None):
    """Kac arama iscisiyle kosulacagi.

    ⚠ NEDEN SABIT 8 DEGIL (29 Eylul, olculdu)
      Iki cekirdekli bir makinede ayni sahne, ayni surede:
          8 isci -> optimumun %50,0'si      2 isci -> optimumun %80,4'u
      Makinede olmayan cekirdegi istemek plani KOTULESTIRIYOR: isciler
      sirayla bekliyor ve her biri digerinin isini bolerek ilerliyor.

    Ayarda acik bir sayi varsa O KULLANILIR -- olcum araci ayni sahneyi
    1, 2, 4, 8 isciyle kosabilsin diye. Yoksa makineye uyulur.
    """
    deger = (ayar or {}).get("isci_sayisi")
    try:
        deger = int(deger)
    except (TypeError, ValueError):
        return cekirdek_sayisi()
    return deger if deger >= 1 else cekirdek_sayisi()


# ----------------------------------------------------------------------
# Plan profilleri -- Master Spec v1.4 #5.4
#
#   Ayni kural seti, farkli agirliklarla UC FARKLI plan uretir. Profil
#   motorun "neyi onemserim" ayaridir; kural listesini degistirmez.
#
#   A7 altin senaryosu tam olarak bunu siniyor: ayni girdi iki profille
#   kosuluyor ve IKISININ ESIT CIKMASI testi kirmizi yakiyor. Bu tablo
#   yokken A7 kirmiziydi ve dogru sebeple kirmiziydi -- motor profili
#   hic okumuyordu.
#
#   Kiraci bu tabloyu duzenleyebilir (#9.16, `plan_profiles`). Duzenlenmis
#   degerler girdiye `agirliklar: {KOD: sayi}` olarak gelir ve tabloyu ezer.
# ----------------------------------------------------------------------

PROFILLER = ("DENGELI", "KAPSAMA", "CALISAN")

AGIRLIK_TABLOSU = {
    "HEDEF_KAPSAMA":         {"DENGELI": 9, "KAPSAMA": 20, "CALISAN": 5},
    "SAAT_DENGESI":          {"DENGELI": 5, "KAPSAMA": 2,  "CALISAN": 8},
    "TERCIH_KARSILAMA":      {"DENGELI": 3, "KAPSAMA": 1,  "CALISAN": 9},
    "ADALET_DENGESI":        {"DENGELI": 5, "KAPSAMA": 2,  "CALISAN": 8},
    "EKIP_SUREKLILIGI":      {"DENGELI": 2, "KAPSAMA": 1,  "CALISAN": 4},
    "PLAN_KARARLILIGI":      {"DENGELI": 6, "KAPSAMA": 6,  "CALISAN": 6},
    "MOLA_KAPSAMASI":        {"DENGELI": 7, "KAPSAMA": 9,  "CALISAN": 6},
    "VARDIYA_ROTASYON_YONU": {"DENGELI": 3, "KAPSAMA": 1,  "CALISAN": 6},
    # HEDEF_ASIMI -- K-53 (Mustafa, 1 Ekim: "Ceza ile ilerleyelim. Ucret
    # tarafi hic gelmeyebilir."). Hedefin USTUNE cikan her kisi-saat ceza.
    # Hedefin ALTINDA kalmak (HEDEF_KAPSAMA) her profilde daha pahali:
    # eksik kisi musteri kaybidir, fazla kisi paradir; ikisi ayni kefede
    # degil. CALISAN profilinde fazlalik daha pahali (gereksiz saat
    # yazilmasin), KAPSAMA profilinde neredeyse bedava.
    "HEDEF_ASIMI":           {"DENGELI": 3, "KAPSAMA": 1,  "CALISAN": 4},
}

# #6 FAZLA_MESAI_TAVANI.azami_saat_hafta de profile baglidir (#5.2 tablosu):
# CALISAN 0 - DENGELI 10 - KAPSAMA 15. Bu bir SERT tavandir, agirlik degil.
FAZLA_MESAI_PROFIL = {"DENGELI": 10, "KAPSAMA": 15, "CALISAN": 0}


# ----------------------------------------------------------------------
# Zaman -- dogrulayicidan BAGIMSIZ ikinci uygulama
# ----------------------------------------------------------------------

# Zaman izgarasi -- K-34 (28 Eylul, Mustafa)
#
#   "Molalar zaten normalde planlanirken, gun icinde 15 dk lik dilimlere
#    dagitiliyor. Yani 15:15'e de mola koyabiliyorlar, 15:30'a da 15:45'e
#    de. Dogrusu bu."
#
# Dilim SAAT degil CEYREK SAATTIR. Bu bir hiz meselesi degil DOGRULUK
# meselesiydi: saat izgarasi 15 dk'lik bir molayi 60 dk sayiyordu.
#
# ⚠ YEMEK ILE DINLENME AYRI SEYLER (Mustafa, ayni gun). Eski izgaranin
#   hatasi ikisine ESIT DAGILMIYORDU:
#
#       yemek     60 dk gercek ->  60 dk modelde   1.00x   HATA YOK
#       dinlenme  45 dk gercek -> 180 dk modelde   4.00x   HATA BURADA
#
#   Eski kayitlardaki "2.29x" HARMANLANMIS bir rakamdir; yemegin
#   dogrulugunu dinlenmenin hatasiyla ortalar. Duzeltme dinlenmeyi
#   duzeltir, yemegi OLDUGU GIBI birakir.
CEYREK = 4          # bir saatte kac dilim


def _q(gun, saat):
    """Gun + genisletilmis saat -> mutlak CEYREK dilim indeksi.

    Genisletilmis saat dogrudan toplanir: gun 1, 16 -> 25  =>  164.

    Yuvarlama bilerek `round`: 11.25 ikilik gosterimde tam degildir ve
    `int()` onu asagi kirpabilir. Bir ceyreklik kayma molayi yanlis
    dilime koyar ve `_sahada` aritmetigini sessizce bozar.
    """
    return int(round((gun * 24 + saat) * CEYREK))


def _dilimler(gun, bas, bit):
    """Vardiyanin kapsadigi mutlak CEYREK dilimler.

    Bitis dilimi DAHIL DEGIL (bit=18 ise son dilim 17:45).
    """
    return list(range(_q(gun, bas), _q(gun, bit)))


def _mola_toplam_dk(sablon):
    """Vardiyada gecen TOPLAM mola dakikasi -- ucretli ucretsiz ayrimi YOK.

    ⚠ NEDEN UCRETLI MOLA DA SAYILIR (T-57, 29 Eylul)
      Bir molanin UCRETLI olmasi, o sirada is yapiliyor olmasi demek
      degildir. Ara dinlenme ucretli de olsa CALISMA SURESINDEN dusulur;
      ucret tarafi ayri bir buyuktur. Dogrulayici bunu 25 Eylul'den beri
      boyle hesapliyor ve karari `dogrulayici/zaman.py` icinde belgeli.

      Cozucu ise yalniz `mola_dk` (ucretsiz yemek) dusuyordu. 8,5 saatlik
      bir vardiyada fark 0,75 saat; alti vardiyalik haftada 4,5 saat.
      500 kisilik sahnede sonuc: cozucu "45 saat oldu" diyor, bagimsiz
      dogrulayici 28 SERT ihlal yaziyordu. Iki taraf ayni plan hakkinda
      farkli sey soyluyordu -- #7.6'nin yakalamak icin var oldugu sey.

    Politika yoksa `mola_dk`ya dusulur: eski sahneler kirilmasin.
    """
    pol = sablon.get("mola_politikasi")
    if not pol:
        return float(sablon.get("mola_dk", 0))
    return float(sum(int(m.get("dakika", 0)) * int(m.get("adet", 1))
                     for m in pol))


# GECE_VARDIYASI_AZAMI (K-26) -- istisna kapsamindaki sektorler.
#
# ⚠ BU LISTE DOGRULAYICIDA DA AYRICA YAZILI ve bu BILEREK. #7.6 iki tarafin
#   birbirini import etmesini de ortak yardimci modulu de yasakliyor
#   (test_bagimsizlik). Iki yerde yazilan bir liste iki yerde yanlis da
#   olabilir -- ama biri degisip digeri degismezse bagimsiz denetim o
#   ayrismayi GORUR. Tek yerde yazilsaydi gormezdi.
GECE_ISTISNA_SEKTORLERI = frozenset(("turizm", "ozel_guvenlik", "saglik",
                                     "petrol"))


def _gece_brut_ortusme(sablon, pencere_bas, pencere_bit):
    """Sablonun EN COK ortustugu gece penceresine dusen BRUT saat.

    Sablon gunune gore uc pencere yeter: onceki gece (pazar 20:00'den
    pazartesi 06:00'ya gibi), ayni gunun gecesi, ertesi gunun gecesi.
    Genisletilmis saatle yazilmis 23:00-32:25 gibi sablonlar dogrudan
    karsilastirilir (Z-1).
    """
    tasma = 24.0 if pencere_bit <= pencere_bas else 0.0
    en_cok = 0.0
    for kayma in (-24.0, 0.0, 24.0):
        w0 = pencere_bas + kayma
        w1 = pencere_bit + tasma + kayma
        ortusme = min(sablon["bit"], w1) - max(sablon["bas"], w0)
        en_cok = max(en_cok, ortusme)
    return en_cok


def _gece_onayi_var(calisan, girdi, gun):
    """Calisanin gece calisma yazili onayi O GECE gecerli mi (K-26).

    Dogrulayicidaki `_gece_onayi_gecerli` ile AYNI kurallar, AYRI yazim
    (#7.6). Tarihli onay + hafta tarihi yok -> GECERSIZ: dogrulanamayan bir
    istisna yasal bir siniri acmamali.
    """
    onay = calisan.get("gece_calisma_onayi")
    if onay is True:
        return True
    if not isinstance(onay, dict) or not onay.get("onay"):
        return False
    bitis = onay.get("gecerli_bitis")
    if not bitis:
        return True
    hafta_bas = girdi.get("hafta_baslangic")
    if not hafta_bas:
        return False
    from datetime import date, timedelta
    try:
        return (date.fromisoformat(bitis)
                >= date.fromisoformat(hafta_bas) + timedelta(days=gun))
    except (TypeError, ValueError):
        return False


def _gecmis_kayitlari(calisan):
    """Calisanin gecmis kayitlari -- (gun, bas, bit, gece_isareti) -- T-28.

    #11.2 bicimi: `gecmis_vardiyalar: [{"gun": -1, "bas": 23, "bit": 31}]`.
    Gun NEGATIF, saat genisletilmis, SABLON YOK (PDKS gibi gerceklesen).
    Gunu negatif olmayan kayit atlanir: plan haftasi gecmis degildir.

    ⚠ AYNI OKUMA DOGRULAYICIDA AYRICA YAZILI (#7.6).

    K-42: kayitli aralik calisildigini KANITLAR; kaydin yoklugu hicbir sey
    kanitlamaz. Bu yuzden cozucu YALNIZ kayitli araliktan kisit yazar --
    bilinmeyen gun kendiliginden kisitsiz kalir.
    """
    cikan = []
    for k in calisan.get("gecmis_vardiyalar") or []:
        gun, bas, bit = k.get("gun"), k.get("bas"), k.get("bit")
        if gun is None or bas is None or bit is None or gun >= 0:
            continue
        bas, bit = float(bas), float(bit)
        if bit <= bas:
            bit += 24.0                     # Z-1
        cikan.append((int(gun), bas, bit, k.get("gece")))
    return cikan


def _gecmis_gece_mi(bas, bit, isaret):
    """Gecmis kayit gece mi: yonetmelik tanimi, ustune kaydin isareti (K-43).
    Isaret yalniz EKLER -- "gece degil" isareti yasal olarak gece olan
    kaydi gece olmaktan cikaramaz."""
    return _yasal_gece_postasi(bas, bit) or bool(isaret)


def _cogunluk_gunu_kaymasi(bas, bit):
    """K-46: vardiya saatlerinin yarisindan cogu ERTESI gune tasiyorsa 1,
    yoksa 0. `bas`, `bit` genisletilmis saat. Cuma 23-30 -> 1 (cumartesi);
    cuma 16-25 -> 0. Tam yari -> 0. Yalniz hafta sonu kurallarinda.
    AYNI TANIM DOGRULAYICIDA AYRICA YAZILI (#7.6)."""
    bas, bit = float(bas), float(bit)
    if bit <= bas:
        bit += 24.0                       # Z-1
    tasan = max(0.0, bit - max(bas, 24.0))
    return 1 if 2 * tasan > (bit - bas) + 1e-9 else 0


def _hafta_sonu_gunu(gun, bas, bit):
    """5, 6 ya da None -- cogunluk gunune gore (K-46)."""
    g = gun + _cogunluk_gunu_kaymasi(bas, bit)
    return g % 7 if g % 7 in (5, 6) else None


def _bilinen_gunler(calisan):
    """Kaydi TAM olan gecmis gunler -- dogrulayicidakiyle ayni tanim, ayri
    yazim (#7.6): `gecmis_bilinen_gunler` + kaydi olan gunler."""
    return ({int(g) for g in (calisan.get("gecmis_bilinen_gunler") or []) if g < 0}
            | {g for g, _, _, _ in _gecmis_kayitlari(calisan)})


def _yasal_gece_postasi(bas, bit):
    """YASAL gece calismasi mi -- Postalar Yon. md. 7/2.

    "Calisma suresinin yarisindan cogu gece donemine rastlayan bir
     postanin calismasi, gece calismasi sayilir." Gece donemi 20:00-06:00
    (Is K. md. 69/1). `bas`, `bit` o gunun genisletilmis saati.

    ⚠ K-40 ISARETINE BAKILMAZ: yasal kuralda firma isareti ne kural
      disina cikarabilir ne de yasal olarak serbest bir vardiyayi
      kabul edilemez ihlale cevirebilir. Firma kurallari isareti kullanir.
    ⚠ BRUT: mola yeri karar degiskeni, siniflama ona bagli olmamali.
    ⚠ YARISI DAHIL DEGIL: 16:00-24:00 gece calismasi degil.
    ⚠ AYNI TANIM DOGRULAYICIDA AYRICA YAZILI (#7.6).
    """
    bas, bit = float(bas), float(bit)
    if bit <= bas:
        bit += 24.0                       # Z-1: ham yazim
    gece = 0.0
    for w0 in (-4.0, 20.0, 44.0):         # onceki gece, bu gece, ertesi gece
        gece += max(0.0, min(bit, w0 + 10.0) - max(bas, w0))
    return 2 * gece > (bit - bas) + 1e-9


def _net_saat(sablon):
    """CALISMA SURESI -- butun molalar dusuk. Dogrulayici ile AYNI tanim."""
    return (sablon["bit"] - sablon["bas"]) - (_mola_toplam_dk(sablon) / 60.0)


def _ucret_saat(sablon):
    """UCRET HESABINA ESAS sure -- yalniz UCRETSIZ mola dusuk (K-32).

    `net_saat`ten bilerek farkli. Burada yalniz raporlama icin duruyor;
    kisitlar net saate bakar.
    """
    pol = sablon.get("mola_politikasi")
    if not pol:
        return (sablon["bit"] - sablon["bas"]) - (sablon.get("mola_dk", 0) / 60.0)
    ucretsiz = sum(int(m.get("dakika", 0)) * int(m.get("adet", 1))
                   for m in pol if not m.get("ucretli"))
    return (sablon["bit"] - sablon["bas"]) - (ucretsiz / 60.0)


def _brut_saat(sablon):
    return sablon["bit"] - sablon["bas"]


MOLA_PENCERESI_VARSAYILAN = (3, 5)   # vardiyaya GORE saat -- K-32

# Dinlenme molasinin ideal noktasi etrafindaki aday penceresinin yaricapi,
# CEYREK cinsinden. 4 = +-1 saat. UST SINIR; ideal noktalar birbirine daha
# yakinsa `_dinlenme_baslangiclari` bunu kirpar (pencereler DEGMEZ).
PENCERE_YARICAPI_Q = 4


def _mola_politikasi(girdi, sablon):
    """Firmanin mola politikasi -- SABLON ezer, firma varsayilan verir (K-32).

    Bicimi:
        [ {"tip": "yemek",    "dakika": 60, "adet": 1, "ucretli": false},
          {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": true } ]

    NEDEN IKI KADEME (K-32 madde 6, Mustafa 25 Eylul)
      "Biz 3x15 veriyoruz" bir SIRKET kararidir; ama 4 saatlik cumartesi
      nobetine 1 saatlik yemek konamaz -- sablonun kendi gercegi vardir.
      Yeni bir mekanizma degil: #5.2 cozunurluk merdiveninin (kapsam K
      firma, D departman) bu alandaki karsiligidir.

    POLITIKA YOKSA
      Eski `mola_dk` alanina duser: tek bir `yemek` molasi. Boylece
      politika tanimlanmamis kiracilarda davranis DEGISMEZ.

    ⚠ Politika yasal tavani EZEMEZ: MOLA_HAKKI kapsami `S`. Politika
    md. 68'in altina inen bir toplam uretirse dogrulayici sert ihlal yazar.
    Burasi onu engellemez, cunku engellemek politikayi sessizce degistirmek
    olurdu -- yanlis politika GORUNUR kalmali.
    """
    p = sablon.get("mola_politikasi") or girdi.get("mola_politikasi")
    if p:
        return list(p)
    dk = sablon.get("mola_dk", 0)
    if dk > 0:
        return [{"tip": "yemek", "dakika": dk, "adet": 1, "ucretli": False}]
    return []


def _mola_baslangiclari(sablon, pencere=MOLA_PENCERESI_VARSAYILAN,
                       yemek_dk=None):
    """YEMEK molasinin baslayabilecegi CEYREK dilimler (saat olarak).

    K-32 (25 Eylul): pencere MUTLAK SAAT degil, kisinin KENDI vardiyasina
    GORELIDIR. `pencere` = (en_az_saat, en_gec_saat): vardiya basindan
    itibaren gecmesi gereken en az / en cok sure.

    Eskiden `sablon["mola_penceresi"]` mutlak saat okunuyordu (12-14 gibi).
    Sablon paylasildigi icin 12:00'de baslayip 20:00'de biten bir vardiyada
    o pencere vardiyanin ILK IKI SAATINE denk geliyordu -- kural kendi
    kendini patlatiyordu.

    K-34 (28 Eylul): adim CEYREK SAAT. Yemek 12:30'da da baslayabilir.
    Yemegin SURESI ve TEK BLOK olmasi (K-14) degismedi -- degisen yalnizca
    baslangicin izgarasi. Yemek zaten dogru modelleniyordu (1.00x); burasi
    onu bozmamak icin degil, yalnizca izgarayi ortaklastirmak icin degisti.

    Mola suresi 0 ise tek bir sahte secenek dondurulur (model basit kalsin).
    """
    dk = sablon.get("mola_dk", 0) if yemek_dk is None else yemek_dk
    mola_saat = dk / 60.0
    if mola_saat <= 0:
        return [None]
    en_az, en_gec = pencere
    erken = sablon["bas"] + en_az
    gec = sablon["bas"] + en_gec
    adaylar = [s / float(CEYREK)
               for s in range(int(round(erken * CEYREK)),
                              int(round(gec * CEYREK)) + 1)
               if s / float(CEYREK) >= sablon["bas"]
               and s / float(CEYREK) + mola_saat <= sablon["bit"]]
    # Pencere vardiyaya sigmiyorsa (kisa vardiya) molayi yine de bir yere
    # koymak gerekir; yerlesim ihlali dogrulayicida YUMUSAK olarak yazilir.
    if adaylar:
        return adaylar
    esnek = [s / float(CEYREK)
             for s in range(_q(0, sablon["bas"]), _q(0, sablon["bit"]) + 1)
             if s / float(CEYREK) + mola_saat <= sablon["bit"]]
    return esnek or [sablon["bas"]]


def _dinlenme_baslangiclari(sablon, adet, dakika):
    """Ucretli kisa molalarin aday baslangic dilimleri -- ESIT DAGITIM (K-32).

    Karar (Mustafa, 25 Eylul): dinlenme molalari vardiyaya ESIT dagitilir.
    Serbest birakilsa cozucu en ucuz yeri secer ve ucunu de vardiyanin basina
    yigardi -- "adil plan" tam bunun tersi.

    NASIL
      Vardiya N+1 esit parcaya bolunur; i. mola i/(N+1) noktasina konur.
      9 saatlik vardiyada 3 mola -> 11.25, 13.50, 15.75. CEYREK izgarada
      bu noktalar TAM ISABET eder (K-34); saat izgarasinda 11, 13, 15'e
      yuvarlaniyorlardi.

      Her molaya ideal noktanin etrafinda bir PENCERE verilir (varsayilan
      +-1 saat = +-4 ceyrek). Pencereler birbirine DEGMEZ.

    ⚠ AYRIK PENCERE SARTI -- SUSLEME DEGIL, ARITMETIGIN KOSULU
      Pencereler kesisirse iki dinlenme molasi ayni dilime dusebilir ve
      `_sahada`nin dogrusal toplami eksiye duser (oradaki nota bak). Bu
      yuzden pencere genisligi ideal noktalar arasi mesafenin YARISINI
      asamaz; asarsa buradan kirpilir.

    T-44 ILE ILISKISI
      Esigi (N >= 4F) yukselten iki sebep vardi: aday penceresinin darligi
      ve saat yuvarlamasi. K-34 ikisini birden kaldirir -- yuvarlama
      dogrudan, pencere ise ceyrek izgarada ayni sure icine dort kat aday
      sigdigi icin.

    DONEN DEGER
      [[aday, ...], ...] -- mola basina bir aday listesi, sirali.
      Vardiyaya sigmayan mola icin bos liste doner; cagiran taraf onu atlar
      ve dogrulayici eksikligi kendi tarafinda gorur.
    """
    if adet <= 0 or dakika <= 0:
        return []
    bas, bit = sablon["bas"], sablon["bit"]
    uzunluk = bit - bas
    sure = dakika / 60.0
    # PENCERE YARICAPI -- iki komsu pencere ne kesisebilir ne de molalari
    # ust uste binebilir. Sart:
    #
    #     (ideal_i + yaricap) + sure_q  <=  ideal_(i+1) - yaricap
    #     2*yaricap <= aralik_q - sure_q
    #
    # ⚠ MOLA SURESI HESABA KATILMAK ZORUNDA. Ilk yazimda yalniz
    #   `aralik_q // 2` kullandim: 4 saatlik vardiyada pencereler
    #   [9.5..10.5] ve [10.5..11.5] cikiyor, 10.5 IKISINDE de var ve iki
    #   dinlenme ayni dilime dusebiliyordu. `test_adaylar_AYRIK` yakaladi.
    #   30 dk'lik molada uc nokta esitligi bile yetmez, sure kadar bosluk
    #   gerekir -- o yuzden `- sure_q`.
    aralik_q = uzunluk / float(adet + 1) * CEYREK
    # ⚠ YUKARI YUVARLANIR (T-78, 1 Ekim). `round` 20 dakikayi 1 ceyrek
    #   (15 dk) sayiyordu; pencereler o hesapla ayriliyor, mola ise gercek
    #   suresiyle uzuyordu. 08-17 vardiyasinda ikinci molanin son adayi
    #   13:30 (biter 13:50), ucuncunun ilk adayi 13:45 -- BES DAKIKA USTUSTE.
    #   Dogrulayici ustuste binen molayi TEK aralik sayar (zaman.mola_
    #   araliklari) ve net calisma 5 dk fazla cikar; 45 saatlik tavanda
    #   duran yari zamanli icin bu tek basina SERT ihlaldir. Tam olcekte
    #   boyle bulundu: cozucu "45,00" dedi, dogrulayici "45,08" yazdi.
    sure_q = _ceyrek_yukari(sure)
    yaricap = max(0, int(min(PENCERE_YARICAPI_Q, (aralik_q - sure_q) // 2)))
    cikan = []
    for i in range(1, adet + 1):
        ideal_q = int(round((bas + uzunluk * i / float(adet + 1)) * CEYREK))
        adaylar = []
        for q in range(ideal_q - yaricap, ideal_q + yaricap + 1):
            s = q / float(CEYREK)
            if bas <= s and s + sure <= bit:
                adaylar.append(s)
        cikan.append(adaylar)
    return cikan


def _mola_dilimleri(gun, sablon, baslangic, dakika=None):
    """Molanin kapsadigi CEYREK dilimler -- GERCEK suresi kadar (K-34).

    Dogrulayici ile AYNI anlami tasir ama farkli yoldan: orada
    `mola.bas <= saat < mola.bit` diye bakilir, burada dilim uretilir.

    ⚠ 28 Eylul'e kadar burasi molayi TAM SAATE yuvarliyordu: 11:00'de
    baslayan 15 dk'lik mola 11. saatin tamamini kapatiyordu. Yemek icin
    dogru sonuc veriyordu (60 dk zaten bir saat), dinlenme icin DORT KAT
    yanlisti. Iki tipin ayni koda girip farkli sonuc almasi, hatanin bu
    kadar uzun sure gorunmez kalmasinin sebebi.

    Artik yuvarlama YOK: 15 dk bir ceyrek, 60 dk dort ceyrek kaplar.

    ⚠ CEYREGE SIGMAYAN MOLA (T-78, 1 Ekim): 20 dakikalik mola `_q`nun
      `round`u ile 1 ceyrek kapliyordu; oysa 13:45-14:05 molasindaki kisi
      hem 13:45 hem 14:00 aninda sahada DEGILDIR. Dogrulayici sahayi ceyrek
      ANLARINDA orneklerken (`zaman.sahada_mi`) iki anda da yok sayar;
      cozucu tek anda yok sayiyordu. SAHADA_ASGARI sert oldugu icin bu
      fark bir sert ihlale donusebilirdi. Olcu artik dogrulayicininkiyle
      AYNI: molanin icine dusen her ceyrek ANI kapali sayilir, yani bitis
      YUKARI yuvarlanir (20 dk -> 2 ceyrek, 15 dk -> 1, 60 dk -> 4).
    """
    if baslangic is None:
        return []
    dk = sablon.get("mola_dk", 0) if dakika is None else dakika
    if dk <= 0:
        return []
    return list(range(_q(gun, baslangic),
                      _q(gun, baslangic) + _ceyrek_yukari(dk / 60.0)))


def _ss(saat):
    """Genisletilmis saati HH:MM yazar (25.5 -> 25:30)."""
    return "%02d:%02d" % (int(saat), int(round((saat - int(saat)) * 60)))


def _ceyrek_yukari(saat):
    """Sure kac CEYREK kaplar -- kesirli ceyrek YUKARI yuvarlanir (T-78).

    Bir molanin icine dusen her ceyrek ANI kapalidir: 20 dk = 1,33 ceyrek
    -> 2. `round` 1 derdi; 1e-9 payi 0,25'in ikilik gosterimi icindir.
    """
    return int(math.ceil(saat * CEYREK - 1e-9))


def _gercek_kesisiyor(bas1, sure1_sa, bas2, sure2_sa):
    """Iki mola GERCEK zamanda ustuste biniyor mu -- ceyrek izgarasinda
    degil (T-78). Ucu uca degen iki mola kesismez."""
    return bas1 < bas2 + sure2_sa - 1e-9 and bas2 < bas1 + sure1_sa - 1e-9


def _gece_sablonu(sablon):
    """Bu sablon GECE VARDIYASI mi -- K-40 (Mustafa, 29 Eylul).

    Donen: (gece_mi, tahmin_mi)

    ⚠ ISARET TAHMINI EZER. Kullanici `gece_vardiyasi` yazdiysa o gecerlidir.
      22:00-06:00 ya da 00:00-08:00 gibi sinir durumlarinda bizim saat
      penceremiz firmanin kendi tanimiyla celisebilir; Mustafa'nin istedigi
      sey tam olarak buydu: "Bunu KULLANICI isaretleyecek."

    ⚠ ISARET YOKSA tahmine dusulur -- ama SESSIZ DEGIL. Cagiran taraf
      `tahmin_mi` bayragini nota cevirir. Isaretlenmemis bir gece
      vardiyasi, korunmasi gereken birini sessizce geceye koyabilirdi.

    ⚠ OTOMATIK ISARET = YONETMELIGIN TANIMI (T-69, 30 Eylul aksami):
      suresinin yarisindan cogu 20:00-06:00'da (Postalar Yon. md. 7/2).
      Eskiden yalniz ayni gunun penceresine "en ufak degme" araniyordu:
      00:00-08:45 gece DEGIL, 13:00-21:00 GECE sayiliyordu.

    ⚠ K-43 (Mustafa, 30 Eylul gecesi): OTOMATIK ISARET TABANDIR, firma
      ustune EKLER, altina INEMEZ. "gece_vardiyasi: false" yasal olarak
      gece olan sablonu gece olmaktan cikaramaz -- cikarsaydi gece
      calisamayan biri 22:00-06:00'ya yazilabilirdi. Ikinci deger: isaret
      yok, otomatik belirlendi (nota cevrilir).
    """
    yasal = _yasal_gece_postasi(sablon["bas"], sablon["bit"])
    if "gece_vardiyasi" in sablon:
        return (yasal or bool(sablon["gece_vardiyasi"])), False
    return yasal, True


# ----------------------------------------------------------------------
# Girdi okuma
# ----------------------------------------------------------------------

def _kural(girdi, kod):
    for k in girdi.get("kurallar", []) or []:
        if k.get("kod") == kod and k.get("aktif", True):
            return k
    return None


# ----------------------------------------------------------------------
# Departman calisma saatleri -- CALISMA_SAATLERI, K-52 (Mustafa, 1 Ekim)
# ----------------------------------------------------------------------
#
# "Sistemde departman tanimi lazim ve ilgili departmana calisma gunleri ile
#  saatlerini tanimlamaliyiz." Girdi:
#
#   "departmanlar": [
#     {"id": "D-SATIS", "ekipler": ["SATIS"], "acik": "7/24"},
#     {"id": "D-MH", "ekipler": ["MHIZMET"],
#      "acik": [{"gunler": [0,1,2,3,4], "bas": 7, "bit": 23},
#               {"gunler": [5, 6], "bas": 8, "bit": 19}]}]
#
# Pencere `bit` 24'u asabilir (31 = ertesi gun 07:00). Vardiya acik sayilir
# <=> basladigi gunun BIR penceresi vardiyanin tamamini kapsar. Ekibin
# departmani ya da departmanin saatleri yoksa TANIMSIZ: kisit yazilmaz,
# dogrulayici `eksik_boyutlar` ile "denetlenemedi" der (K-49 kapiya tasir).
#
# ⚠ Dogrulayicida AYNI mantik ayrica yazili (kurallar.py, departman_acik_mi)
#   -- #7.6 iki tarafin ortak modul kullanmasini yasakliyor.

def departman_saatleri(girdi):
    """ekip -> "7/24" | [ {gunler, bas, bit}, ... ] | None (tanimsiz)."""
    cikan = {}
    for d in girdi.get("departmanlar", []) or []:
        acik = d.get("acik")
        for e in d.get("ekipler") or []:
            cikan[e] = acik
    return cikan


def departman_acik_mi(saatler, ekip, gun, bas, bit):
    """True/False, ya da None (ekibin saatleri tanimsiz)."""
    acik = saatler.get(ekip)
    if acik is None:
        return None
    if acik == "7/24":
        return True
    for pencere in acik:
        if gun % 7 in (pencere.get("gunler") or range(7)) \
                and pencere["bas"] - 1e-9 <= bas and bit <= pencere["bit"] + 1e-9:
            return True
    return False


def _par(kural, ad, varsayilan):
    if not kural:
        return varsayilan
    return (kural.get("parametreler") or {}).get(ad, varsayilan)


def _calisabilir(c):
    return c.get("durum", "aktif") == "aktif"


class Model(object):
    """CP-SAT modeli ve onu girdiye baglayan her sey."""

    def __init__(self, girdi):
        self.girdi = girdi
        self.m = cp_model.CpModel()
        self.calisanlar = [c for c in girdi.get("calisanlar", []) if _calisabilir(c)]
        # ⚠ Politika sablona TASINIR (T-57): `_net_saat` yalniz sablona
        #   bakiyor; firma varsayilani sahne seviyesindeyse goremezdi ve
        #   net saati yine yanlis hesaplardi.
        self.sablonlar = []
        for _s in (girdi.get("vardiya_sablonlari", []) or []):
            if "mola_politikasi" not in _s:
                _pol = _mola_politikasi(girdi, _s)
                if _pol:
                    _s = dict(_s, mola_politikasi=_pol)
            self.sablonlar.append(_s)
        self.sablon = {s["id"]: s for s in self.sablonlar}
        self.gunler = list(range(HAFTA_GUN))
        self.x = {}          # (e,d,t) -> BoolVar
        self.mola = {}       # (e,d,t,s) -> BoolVar
        self.cezalar = []    # (agirlik, IntVar) ciftleri
        self.notlar = []     # uygulanmayan/atlanan seyler -- sessiz gecmemek icin
        self.profil = self._profil_sec(girdi.get("profil"))
        self.mola_penceresi = self._mola_penceresi_sec()
        # K-52: departman calisma saatleri (CALISMA_SAATLERI aktifse).
        self._calisma_saatleri_aktif = _kural(girdi, "CALISMA_SAATLERI") is not None
        self._departman_saatleri = departman_saatleri(girdi)
        # K-50: cok ekipli calisan sayimi -- "hepsi" (varsayilan) | "tek".
        # Dogrulayici ayni alani ayni varsayilanla okur (kurallar.cok_ekipli_sayim).
        mod = girdi.get("cok_ekipli_sayim") or "hepsi"
        self.cok_ekipli_sayim = mod if mod in ("hepsi", "tek") else "hepsi"
        if girdi.get("cok_ekipli_sayim") not in (None, "hepsi", "tek"):
            self.notlar.append("cok_ekipli_sayim %r taninmadi; 'hepsi' uygulandi"
                               % (girdi.get("cok_ekipli_sayim"),))
        self.yemek_dk = {t["id"]: self._yemek_dk_sec(t) for t in self.sablonlar}
        self.dinlenme_tanim = {t["id"]: self._dinlenme_sec(t) for t in self.sablonlar}
        self.dinlenme = {}   # (e,d,t,i,s) -> BoolVar
        # K-54 (T-29): donmus gunler OLAN OLDU gunleridir. Mevcut planin o
        # gunlerdeki satirlari aynen gecer, modelde sabit sayilir; o gunlere
        # yeni atama yazilmaz. Ayrintisi _donmus_plani_esle ve _kisit'te.
        self.donmus = {int(d) for d in (girdi.get("donmus_gunler") or [])
                       if d in self.gunler}
        self.mevcut_plan = girdi.get("mevcut_plan")
        self._var_gun = {}        # degisken indeksi -> gun (x, mola, dinlenme)
        self._donmus_deger = {}   # sabitlenmis donmus degisken -> degeri
        self._proto = self.m.Proto()
        self._donmus_plan = {}    # (calisan, gun) -> [(sablon_id, molalar), ...]
        self.donmus_satirlar = [] # ciktiya AYNEN gececek mevcut plan satirlari
        self._donmus_dusen = 0    # tamamen gecmise ait oldugu icin dusen kisit
        self._donmus_kirpilan = 0 # siniri gecmise gore kirpilan kisit
        self._donmus_mola_oturmayan = 0
        self._donmus_plani_esle()

    def _dinlenme_sec(self, sablon):
        """(adet, dakika) -- ucretli kisa molalar, politikadan (K-32).

        Politika yoksa (0, 0): motor dinlenme molasi URETMEZ ve davranis
        25 Eylul oncesiyle ayni kalir.
        """
        for satir in _mola_politikasi(self.girdi, sablon):
            if satir.get("tip") == "dinlenme":
                return (int(satir.get("adet", 0)), int(satir.get("dakika", 0)))
        return (0, 0)

    def _dinlenme_adaylari(self, sablon):
        """Bu sablonun dinlenme molalari icin aday dilimler."""
        adet, dk = self.dinlenme_tanim[sablon["id"]]
        return _dinlenme_baslangiclari(sablon, adet, dk)

    def _yemek_dk_sec(self, sablon):
        """Bu sablonda yemek molasi kac dakika -- politikadan (K-32).

        Politika yoksa eski `mola_dk` alanina duser; yani politika
        tanimlanmamis kiracida davranis DEGISMEZ.
        """
        for satir in _mola_politikasi(self.girdi, sablon):
            if satir.get("tip") == "yemek":
                return satir.get("dakika", 0) * max(1, satir.get("adet", 1))
        return sablon.get("mola_dk", 0)

    def _mola_penceresi_sec(self):
        """Yemek molasinin GORELI penceresi -- MOLA_YERLESIMI'nden (K-32).

        Kural yoksa varsayilan (3, 5). Kural firma parametresidir: kapsam K.
        Yasal kural MOLA_HAKKI'dir ve kapsami S -- bu pencere onu EZEMEZ,
        yalniz molanin nereye konacagini soyler (K-18'in ayni gerekcesi).
        """
        k = _kural(self.girdi, "MOLA_YERLESIMI")
        if not k:
            return MOLA_PENCERESI_VARSAYILAN
        en_az, en_gec = MOLA_PENCERESI_VARSAYILAN
        return (_par(k, "en_az_saat", en_az), _par(k, "en_gec_saat", en_gec))

    # ---- profil -------------------------------------------------------

    def _profil_sec(self, gelen):
        """Girdideki profil adini dogrular. Taninmayan ad SESSIZCE yutulmaz."""
        if gelen is None:
            return "DENGELI"
        ad = str(gelen).upper()
        if ad in PROFILLER:
            return ad
        self.notlar.append(
            "profil taninmadi: %r -> DENGELI kullanildi (#5.4)" % gelen)
        return "DENGELI"

    def _agirlik(self, kod, kural=None):
        """Yumusak kuralin agirligi. Oncelik sirasi:

          1. girdi['agirliklar'][kod]  -- kiracinin duzenledigi plan_profiles
          2. #5.4 profil tablosu       -- profil zaten "bu agirliklar" demektir
          3. kuralin kendi 'agirlik'i  -- tabloda olmayan kurallar icin
          4. 5                         -- ve bu durum NOT olarak bildirilir

        Profilin kuralin kendi agirligindan ONCE gelmesi bilincli: "KAPSAMA
        profiliyle coz" demek, kapsama agirligini yukseltmek demektir. Kural
        katalogundaki sayi DENGELI sutununun yazili halidir.
        """
        ozel = (self.girdi.get("agirliklar") or {}).get(kod)
        if ozel is not None:
            return ozel
        satir = AGIRLIK_TABLOSU.get(kod)
        if satir:
            return satir[self.profil]
        if kural and kural.get("agirlik") is not None:
            return kural["agirlik"]
        self.notlar.append("%s agirligi #5.4 tablosunda yok, 5 kullanildi" % kod)
        return 5

    # ---- kurulum ------------------------------------------------------

    def kur(self):
        self._degiskenler()
        self._donmus_kilitleri_ele()
        self._gun_disi_sablonlari_kapat()
        self._gunde_tek_vardiya()
        self._uygunluk()
        self._gece_uygunlugu()
        self._gece_azami()
        self._izin()
        self._kilitler()
        self._sabit_atamalar()
        self._sure_sinirlari()
        self._dinlenme()
        self._ardisik_gun()
        self._ardisik_gece()
        self._gece_postasi_devri()
        self._ardisik_hafta_sonu()
        self._asgari_vardiya()
        self._kapsama()
        self._yetkinlik()
        self._amac()
        self._donmus_ozeti()
        return self

    def _sablonlari(self, c):
        """Bu calisanin ATANABILECEGI sablonlar -- T-46 (28 Eylul).

        Kisi yalniz KENDI ekiplerinin vardiyalarina atanabilir. `ekipler`
        bir listedir: cok ekipli calisan hepsini gorur. `ekip` alani
        olmayan sablon HERKESE aciktir -- eski fiksturlerde o alan yok.

        ⚠ NEDEN BU SUZGEC VAR
          28 Eylul'e kadar yoktu ve motor SATIS calisanini BACKOFFICE
          vardiyasina atayabiliyordu. Teorik degil: uretilen planda
          gercekten oldu (test_ekip_kapsami).

          Sonucu SESSIZ BIR KAPASITE KAYBI -- kisinin saatleri dolar
          (HAFTALIK_AZAMI, HAFTA_TATILI, ARDISIK_CALISMA_GUNU hepsi sayar)
          ama `_atanmis` ekibe gore suzdugu icin HICBIR ekibin kapsamasina
          sayilmaz. Calisan mesgul, kimseye faydasi yok.

          Performans yuzu ayni kokten (T-46): 350 kisilik sahnede 968 bin
          degiskenin %64'u kisinin calisamayacagi sablonlar icindi.

          Neden simdiye kadar gorulmedi: butun test sahnelerinde TEK EKIP
          vardi, capraz atama tanimsizdi.
        """
        ekipler = set(c.get("ekipler") or [])
        return [t for t in self.sablonlar
                if t.get("ekip") is None or t.get("ekip") in ekipler]

    def _calisan_sablonlari(self, kimlik):
        """Kimlikten sablon listesi -- yalniz id bilen cagiranlar icin."""
        for c in self.calisanlar:
            if c["id"] == kimlik:
                return self._sablonlari(c)
        return self.sablonlar

    # ---- K-54 (T-29): donmus gun -- "olan oldu" ---------------------------
    #
    # MUSTAFA (1 Ekim): "Kapanan gunlerdeki plan uyumu yoneticinin bilgisi
    #   dahilinde degisebilir -- baska bir elemani o gun kendi inisiyatifiyle
    #   ise cagirabilir. Yonetici plani guncellerken gecmis gunler icin
    #   duzenleme yapabilir, gelecek gunler icin istedigi calisanlari
    #   kilitleyebilir. Yonetici duzenlemelerini bitirdikten sonra motora
    #   ilgili verilerin gitmesi gerekiyor."
    #
    # MEKANIZMA
    #   `mevcut_plan` (yayinlanmis plan, yoneticinin duzenledigi haliyle) ve
    #   `donmus_gunler` birlikte gelir. Donmus gunun satirlari:
    #     * ciktiya AYNEN gecer (molalariyla; cozucu uretmez, aktarir),
    #     * modelde SABITTIR: x = 1 (plandaki sablon), diger x = 0 -- domain
    #       daraltilarak, kisitla degil (kisitlar suzgecten gecer, domain gecmez),
    #     * gunler arasi kurallar onlari GERCEK sayar: dinlenme, ardisik gun,
    #       haftalik saat, adalet -- gelecek gunler gecmise uyar.
    #   Gecmisin KENDISI yargilanmaz: butun degiskenleri donmus gunlere ait
    #   olan kisit DUSER (olan oldu -- o gun eksik kapsanmissa, iki vardiya
    #   yazilmissa, izinli gunde calisilmissa model cozumsuz olmaz). Gecmisle
    #   gelecegi birlikte tutan kisit kalir; gecmis siniri zaten asmissa sinir
    #   ulasilabilir en iyi noktaya KIRPILIR: 45 saatlik tavan 50 saatle
    #   dolmussa kalan gunlere pay kalmaz, plan yine cozulur.
    #   Dogrulayici ayni gercegi "gecmis ihlal" diye ayri raporlar ve yayin
    #   kapisi onu saymaz (denetle._gecmis_ihlalleri_isaretle).
    #
    # NE YAPMAZ
    #   Plansiz donmus gun (mevcut_plan yok) SERBEST planlanir ve not dusulur;
    #   dogrulayici DONMUS_GUN'u denetleyemez der (K-49: kabul bekler).
    #   Hicbir sablona oturmayan satir (yonetici 10:00-14:00 yazmis, sablon
    #   yok) ciktiya aynen gecer ama modele GIRMEZ -- saat ve dinlenme
    #   kurallari onu gormez; dogrulayici gorur. Not dusulur.

    def _yeni_bool(self, ad, gun):
        v = self.m.NewBoolVar(ad)
        if self.donmus:
            self._var_gun[v.Index()] = gun
        return v

    def _domain_sabitle(self, v, deger):
        dom = self._proto.variables[v.Index()].domain
        dom.clear()
        dom.extend([int(deger), int(deger)])
        self._donmus_deger[v.Index()] = int(deger)

    def _sablon_esle(self, c, satir):
        """Bir satiri (plan satiri, kilit, sabit atama) bu kisinin atanabilecegi
        bir sablona esler: once `sablon` kimligi, yoksa `bas`+`bit` (satirda
        `ekip` varsa yalniz o ekibin sablonlari). Eslesmezse None.

        T-38 (1 Ekim): sabit atama ve sabitleme kilidi #11.2 ornegindeki gibi
        `ekip`+`bas`+`bit` ile gelebilir; eskiden sabit atama yalniz `sablon`
        kimliginden, kilit ise ekibe bakmadan ilk saat eslesmesinden
        bulunuyordu (iki ekibin ayni saatli sablonu varsa yanlis ekibi
        secip "ekibinde olmayan sablon" notu dusuyordu).
        """
        adaylar = self._sablonlari(c)
        tid = satir.get("sablon")
        for t in adaylar:
            if tid is not None and t["id"] == tid:
                return t
        bas, bit = satir.get("bas"), satir.get("bit")
        if bas is None or bit is None:
            return None
        ekip = satir.get("ekip")
        for t in adaylar:
            if ekip is not None and t.get("ekip") is not None and t.get("ekip") != ekip:
                continue
            if abs(float(t["bas"]) - float(bas)) < 1e-6 and abs(float(t["bit"]) - float(bit)) < 1e-6:
                return t
        return None

    def _donmus_plani_esle(self):
        if not self.donmus:
            return
        if self.mevcut_plan is None:
            self.notlar.append(
                "donmus gun var (%s) ama `mevcut_plan` verilmedi: donmus gunler "
                "SERBEST planlandi, gecmis korunamadi; dogrulayici DONMUS_GUN'u "
                "denetleyemez (K-54, K-49)" % sorted(self.donmus))
            self.donmus = set()      # korunacak gecmis yok: model gunleri serbest planlar
            return
        kisiler = {c["id"]: c for c in self.calisanlar}
        for a in self.mevcut_plan or []:
            d = a.get("gun")
            if d not in self.donmus:
                continue
            self.donmus_satirlar.append(dict(a, donmus=True))
            e = a.get("calisan")
            c = kisiler.get(e)
            if c is None:
                self.notlar.append(
                    "donmus gun %s: mevcut plandaki %s calisan listesinde yok "
                    "(ya da aktif degil); satir ciktiya aynen gecti, modele "
                    "girmedi (K-54)" % (d, e))
                continue
            t = self._sablon_esle(c, a)
            if t is None:
                self.notlar.append(
                    "donmus gun %s: %s'in %s-%s atamasi hicbir sablona oturmadi; "
                    "satir ciktiya aynen gecti, saat ve dinlenme kurallarinda "
                    "modele girmedi (K-54)" % (d, e, _ss(a.get("bas", 0)),
                                               _ss(a.get("bit", 0))))
                continue
            self._donmus_plan.setdefault((e, d), []).append(
                (t["id"], list(a.get("molalar") or [])))

    def _donmus_sabitle(self, c, d, t, v, yemekler):
        """Donmus gunun degiskenlerini mevcut plana gore sabitler."""
        secilen = [(tid, mol) for tid, mol in self._donmus_plan.get((c["id"], d), [])
                   if tid == t["id"]]
        if not secilen:
            self._domain_sabitle(v, 0)
            for s in yemekler:
                self._domain_sabitle(self.mola[(c["id"], d, t["id"], s)], 0)
            for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
                for s in adaylar:
                    k = (c["id"], d, t["id"], i, s)
                    if k in self.dinlenme:
                        self._domain_sabitle(self.dinlenme[k], 0)
            return
        self._domain_sabitle(v, 1)
        molalar = secilen[0][1]
        yemek = [m for m in molalar if m.get("tip") == "yemek"]
        dinlenmeler = sorted((m for m in molalar if m.get("tip") == "dinlenme"),
                             key=lambda m: m.get("bas", 0))
        oturdu = True
        yemek_bas = yemek[0].get("bas") if yemek else None
        yemek_var = False
        for s in yemekler:
            esit = (s is not None and yemek_bas is not None
                    and abs(float(s) - float(yemek_bas)) < 1e-6)
            self._domain_sabitle(self.mola[(c["id"], d, t["id"], s)], 1 if esit else 0)
            yemek_var = yemek_var or esit
        if yemek_bas is not None and not yemek_var:
            oturdu = False
        for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
            hedef = dinlenmeler[i].get("bas") if i < len(dinlenmeler) else None
            bulundu = False
            for s in adaylar:
                k = (c["id"], d, t["id"], i, s)
                if k not in self.dinlenme:
                    continue
                esit = hedef is not None and abs(float(s) - float(hedef)) < 1e-6
                self._domain_sabitle(self.dinlenme[k], 1 if esit else 0)
                bulundu = bulundu or esit
            if hedef is not None and not bulundu:
                oturdu = False
        if not oturdu:
            self._donmus_mola_oturmayan += 1

    def _donmus_kilitleri_ele(self):
        if not self.donmus:
            return
        for k in self.girdi.get("kilitler", []) or []:
            if k.get("gun") in self.donmus:
                self.notlar.append(
                    "kilit donmus gune (%s) isaret ediyor: %s -- mevcut plan "
                    "gecerli, kilit uygulanmadi (K-54)" % (k.get("gun"), k.get("calisan")))
        for a in self.girdi.get("sabit_atamalar", []) or []:
            if a.get("gun") in self.donmus:
                self.notlar.append(
                    "sabit atama donmus gune (%s) isaret ediyor: %s -- mevcut "
                    "plan gecerli, uygulanmadi (K-54)" % (a.get("gun"), a.get("calisan")))

    def _donmus_ozeti(self):
        if not self.donmus:
            return
        if self._donmus_mola_oturmayan:
            self.notlar.append(
                "%d donmus atamada molalar motorun aday noktalarina oturmadi; "
                "molalar ciktiya plandan aynen gecti, modelde sahada sayildi "
                "(K-54)" % self._donmus_mola_oturmayan)
        if self._donmus_kirpilan:
            self.notlar.append(
                "donmus gunler %d kisitin sinirini zaten asmisti; sinir "
                "ulasilabilir en yakin noktaya kirpildi (olan oldu, kalan "
                "gunlere pay kalmadi) (K-54)" % self._donmus_kirpilan)

    def _kisit(self, ct):
        """self.m.Add + K-54 suzgeci. Butun kisitlar buradan gecer."""
        kisit = self.m.Add(ct)
        if self.donmus:
            self._donmus_suz(kisit)
        return kisit

    def _donmus_suz(self, kisit):
        proto = self._proto
        c = proto.constraints[kisit.Index()]
        if not c.has_linear():
            return
        lin = c.linear
        vars_ = list(lin.vars)
        coeffs = list(lin.coeffs)
        if not vars_:
            return
        sabit = 0
        serbest_lo = serbest_hi = 0
        donmus_var = 0
        deger = self._donmus_deger
        var_gun = self._var_gun
        donmus = self.donmus
        for i, k in zip(vars_, coeffs):
            idx = i if i >= 0 else -i - 1
            gun = var_gun.get(idx)
            if gun in donmus:                      # donmus gun degiskeni
                donmus_var += 1
                if idx in deger:
                    d_ = deger[idx]
                else:                              # henuz sabitlenmedi (_degiskenler ici)
                    dom = list(proto.variables[idx].domain)
                    d_ = dom[0]
                sabit += k * ((1 - d_) if i < 0 else d_)
                continue
            if gun is not None:                    # serbest gun bool
                lo, hi = 0, 1
            else:                                  # yardimci tam sayi degisken
                dom = list(proto.variables[idx].domain)
                lo, hi = dom[0], dom[-1]
            if i < 0:
                lo, hi = 1 - hi, 1 - lo
            a, b = k * lo, k * hi
            serbest_lo += min(a, b)
            serbest_hi += max(a, b)
        if donmus_var == 0:
            return
        if donmus_var == len(vars_):
            c.clear_linear()          # yalniz gecmis: olan oldu, kisit duser
            self._donmus_dusen += 1
            return
        dom = list(lin.domain)
        if len(dom) != 2:
            return
        lo, hi = dom
        yeni_lo, yeni_hi = lo, hi
        if sabit + serbest_hi < lo:
            yeni_lo = sabit + serbest_hi
            yeni_hi = max(hi, yeni_lo)
        if sabit + serbest_lo > hi:
            yeni_hi = sabit + serbest_lo
            yeni_lo = min(lo, yeni_hi)
        if (yeni_lo, yeni_hi) != (lo, hi):
            lin.domain.clear()
            lin.domain.extend([int(yeni_lo), int(yeni_hi)])
            self._donmus_kirpilan += 1

    def _X(self, kimlik, gun, sablon_id):
        """x degiskeni; kisi o sablona atanamiyorsa SABIT SIFIR.

        Boylece cagiran taraflarin dongulerini degistirmek gerekmez:
        olmayan degisken aritmetikte zaten sifirdir.
        """
        return self.x.get((kimlik, gun, sablon_id), 0)

    def _mola_politikasi_yerlesir_mi(self, t):
        """Yemek + BUTUN dinlenmeler bu sablona ustuste binmeden sigiyor mu?

        ⚠ T-78 (1 Ekim): cakisma kisiti gercek zamana gecince, kisa bir
          vardiyaya uzun bir politika (4 saate 60 dk yemek + 4x20 dk gibi)
          hicbir yerlesimle sigmayabilir. O zaman sablona atama YAPILAMAZ
          -- kisitlar bunu zaten uygular ama SESSIZCE: plan cozumsuz doner
          ve teshis yanlis kurali gosterir. Bu kontrol sebebi nota yazar.
          Eskiden ayni sablonlar molalari USTUSTE bindirerek "siginiyordu";
          o plan gecerli degildi, dogrulayici fazla calisma goruyordu.
        """
        yemek_dk = self.yemek_dk[t["id"]]
        yemekler = _mola_baslangiclari(t, self.mola_penceresi, yemek_dk)
        dinl = [a for a in self._dinlenme_adaylari(t) if a]
        _, dk = self.dinlenme_tanim[t["id"]]
        sure, ysure = dk / 60.0, yemek_dk / 60.0
        for sy in yemekler:
            secim = []

            def geri(i):
                if i == len(dinl):
                    return True
                for s_ in dinl[i]:
                    if sy is not None and _gercek_kesisiyor(s_, sure, sy, ysure):
                        continue
                    if secim and _gercek_kesisiyor(secim[-1], sure, s_, sure):
                        continue
                    secim.append(s_)
                    if geri(i + 1):
                        return True
                    secim.pop()
                return False

            if geri(0):
                return True
        return False

    def sabit_mola_secimi(self, t):
        """Bu sablon icin TEK bir mola yerlesimi -- birinci asama icin (T-60).

        Donen: (yemek_baslangici | None, [dinlenme_i baslangici | None, ...])

        Secim ideale en yakin olandir: yemek pencerenin ortasina, her
        dinlenme kendi esit-dagitim noktasina en yakin aday; ustuste binme
        kisitlari (gercek zamanda, _dinlenme_degiskenleri ile AYNI) burada da
        uygulanir ki secim modelin kisitlariyla celismesin. Sigmayan mola
        None kalir (serbest birakilir).
        """
        yemek_dk = self.yemek_dk[t["id"]]
        yemekler = [s_ for s_ in _mola_baslangiclari(t, self.mola_penceresi, yemek_dk)
                    if s_ is not None]
        en_az, en_gec = self.mola_penceresi
        orta = t["bas"] + (en_az + en_gec) / 2.0
        sy = min(yemekler, key=lambda s_: (abs(s_ - orta), s_)) if yemekler else None
        adet, dk = self.dinlenme_tanim[t["id"]]
        sure, ysure = dk / 60.0, yemek_dk / 60.0
        uzunluk = t["bit"] - t["bas"]
        secim = []
        onceki = None
        for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
            ideal = t["bas"] + uzunluk * (i + 1) / float(adet + 1)
            uygun = [s_ for s_ in adaylar
                     if not (sy is not None and _gercek_kesisiyor(s_, sure, sy, ysure))
                     and not (onceki is not None and _gercek_kesisiyor(s_, sure, onceki, sure))]
            if not uygun:
                secim.append(None)
                continue
            sec = min(uygun, key=lambda s_: (abs(s_ - ideal), s_))
            secim.append(sec)
            onceki = sec
        return sy, secim

    def _degiskenler(self):
        # K-50 `tek` sayimda ekibi yazilmamis sablon cok ekipli calisanda
        # kisinin ILK ekibine sayilir -- sessiz degil, nota yazilir.
        cok_ekipli = [c["id"] for c in self.calisanlar
                      if len(c.get("ekipler") or []) > 1]
        if self.cok_ekipli_sayim == "tek":
            for t in self.sablonlar:
                if t.get("ekip") is None and cok_ekipli:
                    self.notlar.append(
                        "sablon %s ekipsiz; cok ekipli calisan (%s) bu sablonda "
                        "yalniz ILK ekibine sayilir (K-50, tek sayim)"
                        % (t["id"], ", ".join(cok_ekipli[:5])
                           + (" ..." if len(cok_ekipli) > 5 else "")))
        for t in self.sablonlar:
            if not self._mola_politikasi_yerlesir_mi(t):
                self.notlar.append(
                    "sablon %s: mola politikasi vardiyaya SIGMIYOR (yemek ve "
                    "dinlenmeler ustuste binmeden yerlesemiyor); bu sablona "
                    "atama yapilamaz -- politikayi ya da vardiyayi uzat (T-78)"
                    % t["id"])
        for c in self.calisanlar:
            for d in self.gunler:
                for t in self._sablonlari(c):
                    v = self._yeni_bool("x_%s_%d_%s" % (c["id"], d, t["id"]), d)
                    self.x[(c["id"], d, t["id"])] = v
                    yemek_dk = self.yemek_dk[t["id"]]
                    yemekler = _mola_baslangiclari(t, self.mola_penceresi, yemek_dk)
                    for s in yemekler:
                        self.mola[(c["id"], d, t["id"], s)] = self._yeni_bool(
                            "m_%s_%d_%s_%s" % (c["id"], d, t["id"], s), d)
                    # Vardiya secildiyse TAM BIR mola yerlesimi secilir.
                    self._kisit(sum(self.mola[(c["id"], d, t["id"], s)]
                                   for s in yemekler) == v)
                    self._dinlenme_degiskenleri(c, d, t, v, yemekler, yemek_dk)
                    if d in self.donmus:
                        self._donmus_sabitle(c, d, t, v, yemekler)

    def _dinlenme_degiskenleri(self, c, d, t, v, yemekler, yemek_dk):
        """Ucretli kisa molalarin degiskenleri ve kisitlari -- K-32.

        NEDEN KARAR DEGISKENI
          Molalar sabit yerlestirilseydi ayni sablondaki HERKES ayni dakikada
          molaya cikardi ve kapsama coker; "adil plan" tam bunun tersi. Her
          molaya IKI aday verilir, cozucu kisileri kaydirir.

        NEDEN MODEL BUYUMUYOR
          Aday pencereleri ESIT DAGITIMDAN geliyor ve birbirini kesmiyor
          (_dinlenme_baslangiclari). Bu yuzden dinlenme molalari arasinda
          cakismama kisiti normalde YAZILMIYOR -- yalniz YEMEKLE cakismama
          yaziliyor. Asagidaki ikinci dongu bir EMNIYET KEMERI: pencere
          aritmetigi bir gun yine yanilirsa (T-78'de yanildi) ustuste binen
          iki aday icin kisit yazar; pencereler ayriksa hic calismaz.

        ⚠ CAKISMA GERCEK ZAMANDA OLCULUR, CEYREK IZGARASINDA DEGIL (T-78)
          Eskiden iki molanin ceyrek dilim kumeleri kesisiyor mu diye
          bakiliyordu. 20 dakikalik mola tek ceyrek sayildigi icin 10:45'te
          baslayan dinlenme (biter 11:05) ile 11:00'de baslayan yemek
          kesismiyor gorunuyordu. Dogrulayici gercek araliklara bakar ve
          bes dakikayi tek mola sayar: net calisma cozucunun sandigindan
          fazla cikar. Tam olcekte bir yari zamanli tam 45 saatte dururken
          bu bes dakika onu 45,08'e cikardi ve plan yayinlanamadi.

        SIGMAYAN MOLA
          Aday listesi bosalirsa mola URETILMEZ ve `notlar`a yazilir. Olmayan
          yere mola koymak, yasanmamis molayi varmis gibi gostermek olurdu
          (T-27'nin ayni sinifi). Eksikligi dogrulayici MOLA_HAKKI'nda gorur.
        """
        adet, dk = self.dinlenme_tanim[t["id"]]
        if adet <= 0 or dk <= 0:
            return
        sure = dk / 60.0
        yemek_sure = yemek_dk / 60.0
        onceki = []          # bir onceki molanin (i, s) adaylari -- emniyet kemeri
        for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
            if not adaylar:
                not_ = ("dinlenme molasi %d/%d sablon %s'e sigmadi"
                        % (i + 1, adet, t["id"]))
                if not_ not in self.notlar:
                    self.notlar.append(not_)
                continue
            for s in adaylar:
                self.dinlenme[(c["id"], d, t["id"], i, s)] = self._yeni_bool(
                    "dm_%s_%d_%s_%d_%s" % (c["id"], d, t["id"], i, s), d)
            self._kisit(sum(self.dinlenme[(c["id"], d, t["id"], i, s)]
                           for s in adaylar) == v)
            # Dinlenme yemekle CAKISAMAZ. Bu kisit yalniz "adil plan" icin
            # degil, ARITMETIK icin de sart: _sahada "molada olmak" durumunu
            # bir TOPLAM olarak yaziyor; iki mola ayni dilimi kapsarsa toplam
            # ikiye cikar ve sahadaki kisi sayisi eksi degere duser.
            for s in adaylar:
                for sy in yemekler:
                    if sy is None:
                        continue
                    if _gercek_kesisiyor(s, sure, sy, yemek_sure):
                        self._kisit(self.dinlenme[(c["id"], d, t["id"], i, s)]
                                   + self.mola[(c["id"], d, t["id"], sy)] <= 1)
                # Emniyet kemeri: bir onceki dinlenmenin gercek zamanda
                # ustuste binen adaylariyla da cakisamaz.
                for j, so in onceki:
                    if _gercek_kesisiyor(s, sure, so, sure):
                        self._kisit(self.dinlenme[(c["id"], d, t["id"], i, s)]
                                   + self.dinlenme[(c["id"], d, t["id"], j, so)] <= 1)
            onceki = [(i, s) for s in adaylar]

    def _calisiyor(self, e, d):
        return sum(self._X(e, d, t["id"])
                   for t in self._calisan_sablonlari(e))

    # ---- sert kurallar ------------------------------------------------

    def _sablon_gunleri(self, sablon):
        """Sablonun kullanilabilecegi gunler.

        `gunler` alani yoksa HER GUN kullanilabilir -- geriye donuk uyumlu.
        Varsa yalniz o gunlerde.

        16 Eylul, A9 bulgusunun sonucu (T-14): "Cumartesi nobeti" adli
        4 saatlik sablon hafta ici de kullanilabiliyordu ve kapasiteyi
        42'den 49'a cikariyordu. Fiksturun beklentisi sablonun Cumartesiye
        ait olduguydu ama VERI MODELINDE bunu soyleyecek alan yoktu.
        """
        g = sablon.get("gunler")
        return self.gunler if g is None else [d for d in self.gunler if d in g]

    def _gun_disi_sablonlari_kapat(self):
        for c in self.calisanlar:
            for t in self._sablonlari(c):
                izinli = set(self._sablon_gunleri(t))
                for d in self.gunler:
                    if d not in izinli:
                        if (c["id"], d, t["id"]) in self.x:
                            self._kisit(self.x[(c["id"], d, t["id"])] == 0)
        self._kapali_saatleri_kapat()

    def _departman_kapali_mi(self, t, d):
        """Bu sablon bu gun departmanin KAPALI saatine tasiyor mu (K-52).
        Ekibin saatleri tanimsizsa False -- kisit yazilmaz, dogrulayici
        bildirir. Sablonun ekibi yoksa kural bakamaz (False)."""
        if not self._calisma_saatleri_aktif:
            return False
        ekip = t.get("ekip")
        if ekip is None:
            return False
        acik = departman_acik_mi(self._departman_saatleri, ekip, d, t["bas"], t["bit"])
        return acik is False

    def _kapali_saatleri_kapat(self):
        """CALISMA_SAATLERI (K-52): departman kapaliyken atama yapilamaz.
        Sablon x gun ciftleri kapatilir, her cift icin bir not yazilir."""
        kapali = set()
        for t in self.sablonlar:
            for d in self.gunler:
                if self._departman_kapali_mi(t, d):
                    kapali.add((t["id"], d))
                    self.notlar.append(
                        "sablon %s gun %d: departman kapali (%s ekibi, %s-%s), "
                        "atama yapilamaz (CALISMA_SAATLERI)"
                        % (t["id"], d, t.get("ekip"), _ss(t["bas"]), _ss(t["bit"])))
        for (e, d, tid), v in self.x.items():
            if (tid, d) in kapali:
                self._kisit(v == 0)
        tanimsiz = sorted({t.get("ekip") for t in self.sablonlar
                           if self._calisma_saatleri_aktif
                           and t.get("ekip") is not None
                           and t.get("ekip") not in self._departman_saatleri})
        for ekip in tanimsiz:
            self.notlar.append(
                "%s ekibinin departman calisma saatleri tanimsiz; "
                "CALISMA_SAATLERI bu ekip icin kisit yazamadi (K-52)" % ekip)

    def _gunde_tek_vardiya(self):
        """CAKISMA_YOK + gunde tek vardiya.

        Ayni gune tek sablon seciliyor; gece yarisini asan vardiyalar ertesi
        gunun vardiyasiyla cakisabilir -- o _dinlenme() icinde yakalanir.
        """
        for c in self.calisanlar:
            for d in self.gunler:
                self._kisit(self._calisiyor(c["id"], d) <= 1)

    def _uygunluk(self):
        for c in self.calisanlar:
            for u in c.get("uygunluk", []) or []:
                if u.get("tip") != "uygun_degil":
                    continue
                yasak = set(_dilimler(u["gun"], u["bas"], u["bit"]))
                for d in self.gunler:
                    for t in self.sablonlar:
                        if set(_dilimler(d, t["bas"], t["bit"])) & yasak:
                            if (c["id"], d, t["id"]) in self.x:
                                self._kisit(self.x[(c["id"], d, t["id"])] == 0)

    def _gece_uygunlugu(self):
        """K-40 -- "bu kisi gece vardiyasi yapamaz" SERT kisiti.

        ⚠ NEDEN (Mustafa, 29 Eylul)
            "Kullanici kartinda gece vardiyasi yapamaz gibi bir ifadeye
             ihtiyacimiz var... Boylelikle gece vardiyalarina uygun olmayan
             calisanlari ilgili vardiyadan direkt elemis olacagiz."

          Bu alan yoktu. Motor geceyi yalniz ADALET_DENGESI'nin dagitimi
          icin tahmin ediyordu; "gece calisamaz" diye bir kayit hicbir
          yerde tutulmuyordu.

        ⚠ ISARETSIZ SABLON SESSIZ GECMEZ: tahmine dusuldugunde not yazilir.
        """
        if not _kural(self.girdi, "GECE_UYGUNLUGU"):
            return
        geceler, tahminler, ezilenler = [], [], []
        for t in self.sablonlar:
            gece, tahmin = _gece_sablonu(t)
            if gece:
                geceler.append(t)
            if tahmin:
                tahminler.append(t["id"])
            elif gece and not t.get("gece_vardiyasi"):
                ezilenler.append(t["id"])
        if tahminler:
            self.notlar.append(
                "gece_vardiyasi isareti yok, yonetmelik tanimiyla (md. 7/2, "
                "yarisindan cogu 20:00-06:00) belirlendi: "
                + ", ".join(sorted(tahminler)))
        if ezilenler:
            self.notlar.append(
                "firma 'gece degil' isaretlemis ama yonetmelige gore gece; "
                "yasal tanim uygulandi (K-43, isaret yalniz ekler): "
                + ", ".join(sorted(ezilenler)))
        if not geceler:
            return
        for c in self.calisanlar:
            if not c.get("gece_calisamaz"):
                continue
            for d in self.gunler:
                for t in geceler:
                    if (c["id"], d, t["id"]) in self.x:
                        self._kisit(self.x[(c["id"], d, t["id"])] == 0)

    def _gece_azami(self):
        """GECE_VARDIYASI_AZAMI -- yasal 7,5 saat, sektor istisnasi (K-26).

        ⚠ BU TARAF DOGRULAYICIDAN BILEREK DAHA KATI -- acikca yaziyorum.
          Dogrulayici gece penceresine dusen NET calismayi olcer: penceredeki
          mola dusulur. Burada ise sablonun BRUT ortusmesi siniri asiyorsa o
          sablon, istisnasi olmayan calisana HIC verilmez.

          Neden: net olcu molanin NEREYE dustugune bagli ve mola yeri bir
          karar degiskeni. Onu kisitlamak kisi x gece x ceyrek kadar terim
          demek -- 500 kiside on binlerce. T-60'a gore model zaten optimuma
          %98,3 uzak; ona yuk eklemek bugun yanlis yon.

          Bedeli: brutu 8, penceresindeki molayla neti 7 saat olan bir
          sablon burada YASAKLANIR, oysa yasaldir. Yani cozucu yasal bir
          plani REDDEDEBILIR -- ama hicbir zaman yasadisi bir plan URETMEZ.
          Ayrisma guvenli yonde. Boyle bir sablon varsa not yazilir.

          Bugunku veri setinde boyle sablon YOK: en uzun gece ortusmesi
          S-GECE'de 7,00 saat.

        ⚠ BILINEN BOSLUK -- iki vardiya ayni pencereyi paylasirsa.
          Kontrol SABLON basinadir. Dogrulayici ise pencere basina TOPLAR.
          Pazartesi 16:00-24:00 + Sali 00:00-06:00 ayni geceye 10 saat
          yazar. `VARDIYA_ARASI_DINLENME` aktifken bu imkansiz (11 saat ara
          gerekir); kapatilirsa iki taraf ayrisabilir ve dogrulayici gorur.
        """
        kural = _kural(self.girdi, "GECE_VARDIYASI_AZAMI")
        if not kural:
            return
        azami = float(_par(kural, "azami_saat", 7.5))
        p_bas = float(_par(kural, "pencere_bas", 20))
        p_bit = float(_par(kural, "pencere_bit", 6))

        asanlar = [(t, _gece_brut_ortusme(t, p_bas, p_bit))
                   for t in self.sablonlar]
        asanlar = [(t, b) for t, b in asanlar if b > azami + 1e-9]
        if asanlar:
            self.notlar.append(
                "GECE_VARDIYASI_AZAMI: su sablonlarin gece ortusmesi %s saati "
                "asiyor ve istisnasi olmayan calisana verilmeyecek (BRUT "
                "olculdu; penceredeki mola dusulseydi yasal olabilirdi): %s"
                % (azami, ", ".join("%s (%.2f sa)" % (t["id"], b)
                                    for t, b in asanlar)))
        # K-44 (30 Eylul gecesi): GECE POSTASI olan sablonun (suresinin
        # yarisindan cogu 20:00-06:00'da) BUTUN net suresi 7,5'i gecemez --
        # Yargitay 9. HD 2020/17967. 16:00-01:00, 1 sa mola: 8 sa -> yasak.
        # Burada net sure sablondan kesin hesaplanir (mola politikasi
        # sablonda), bu yuzden bu olcu dogrulayiciyla AYNI, daha kati degil.
        yasal_asanlar = [t for t in self.sablonlar
                         if _yasal_gece_postasi(t["bas"], t["bit"])
                         and _net_saat(t) > azami + 1e-9
                         and all(t is not u for u, _ in asanlar)]
        if yasal_asanlar:
            self.notlar.append(
                "GECE_VARDIYASI_AZAMI: su sablonlar gece postasi ve net "
                "suresi %s saati asiyor; istisnasi olmayan calisana "
                "verilmeyecek (K-44): %s"
                % (azami, ", ".join("%s (%.2f sa)" % (t["id"], _net_saat(t))
                                    for t in yasal_asanlar)))
        asanlar = asanlar + [(t, _net_saat(t)) for t in yasal_asanlar]
        if not asanlar:
            return

        istisnali = self.girdi.get("sektor") in GECE_ISTISNA_SEKTORLERI
        for c in self.calisanlar:
            for d in self.gunler:
                if istisnali and _gece_onayi_var(c, self.girdi, d):
                    continue
                for t, _ in asanlar:
                    if (c["id"], d, t["id"]) in self.x:
                        self._kisit(self.x[(c["id"], d, t["id"])] == 0)

    def _izin(self):
        for c in self.calisanlar:
            izinli = {i["gun"] for i in c.get("izinler", []) or []
                      if i.get("durum", "onayli") == "onayli"}
            for d in self.gunler:
                for t in self.sablonlar:
                    dokundugu = {g // (24 * CEYREK)
                                 for g in _dilimler(d, t["bas"], t["bit"])}
                    if dokundugu & izinli:
                        if (c["id"], d, t["id"]) in self.x:
                            self._kisit(self.x[(c["id"], d, t["id"])] == 0)

    def _kilitler(self):
        for k in self.girdi.get("kilitler", []) or []:
            e, d = k.get("calisan"), k.get("gun")
            if d in self.donmus:
                continue      # K-54: donmus gunde mevcut plan gecerli (_donmus_kilitleri_ele)
            if k.get("tip") == "yasak":
                if any(c["id"] == e for c in self.calisanlar):
                    self._kisit(self._calisiyor(e, d) == 0)
            elif "bas" in k and "bit" in k:
                self._sabitle_satir(k, "kilit")
            else:
                self.notlar.append("kilit bicimi taninmadi: %r" % sorted(k))

    def _sabitle_satir(self, satir, ad):
        """Sabitleme kilidi / sabit atama: satir bir sablona eslenir, x = 1.

        T-46: kisinin ekibinde olmayan sablona isaret eden satir sessizce
        `0 == 1` yazip plani cozumsuz birakmaz; not dusulur. Ayni sekilde
        hicbir sablona eslesmeyen satir da not olur (T-38).
        """
        e, d = satir.get("calisan"), satir.get("gun")
        c = next((c_ for c_ in self.calisanlar if c_["id"] == e), None)
        if c is None:
            self.notlar.append("%s calisan listesinde olmayan kisiye isaret ediyor: %s gun %s"
                               % (ad, e, d))
            return
        t = self._sablon_esle(c, satir)
        if t is None:
            self.notlar.append("%s sablona eslesmedi: %s gun %s (%s)"
                               % (ad, e, d,
                                  "sablon %s" % satir.get("sablon") if satir.get("sablon")
                                  else "%s-%s%s" % (_ss(satir.get("bas", 0)), _ss(satir.get("bit", 0)),
                                                   " ekip %s" % satir.get("ekip") if satir.get("ekip") else "")))
            return
        if (e, d, t["id"]) in self.x:
            self._kisit(self.x[(e, d, t["id"])] == 1)
        else:
            self.notlar.append("%s modele girmedi: %s gun %s sablon %s" % (ad, e, d, t["id"]))

    def _sabit_atamalar(self):
        """`sabit_atamalar` = sabitleme kilidi (#11.2): `sablon` ya da
        `ekip`+`bas`+`bit` ile gelir, ayni esleme ve ayni not (T-38, 1 Ekim).
        Dogrulayici KILIT_UYUMU ile denetler."""
        for a in self.girdi.get("sabit_atamalar", []) or []:
            if a.get("gun") in self.donmus:
                continue      # K-54: donmus gunde mevcut plan gecerli
            self._sabitle_satir(a, "sabit atama")

    def _sure_sinirlari(self):
        gunluk = _par(_kural(self.girdi, "GUNLUK_AZAMI"), "azami_saat", 11)
        haftalik = _par(_kural(self.girdi, "HAFTALIK_AZAMI"), "azami_saat", 45)
        # K-39: yari zamanli tavani emsal tam sureliye ORANLA hesaplanir.
        # `azami_saat` acikca verilmisse o kullanilir (kiraci ayari).
        pt_kural = _kural(self.girdi, "PART_TIME_LIMIT")
        pt_oran = _par(pt_kural, "emsal_orani", 1.0)
        pt_tavan = _par(pt_kural, "azami_saat", haftalik * pt_oran)
        fm_kural = _kural(self.girdi, "FAZLA_MESAI_TAVANI")
        # #5.2: tavan profile baglidir. Kuralin kendi parametresi DENGELI
        # sutununun yazili halidir; profil onu ezer (bkz. _agirlik notu).
        fm_tavan = FAZLA_MESAI_PROFIL[self.profil]
        # YILLIK_FAZLA_MESAI_TAVANI (Is K. md. 41, 270 saat) -- 1 Ekim, K-49
        # ile yazildi. Yil ici toplami BILINEN calisanda bu haftanin fazla
        # mesaisi kalan payi asamaz; bilinmeyende kisit yok, dogrulayici
        # `gecmis_eksik` ile bildirir (K-42).
        yillik_kural = _kural(self.girdi, "YILLIK_FAZLA_MESAI_TAVANI")
        yillik_azami = _par(yillik_kural, "azami_saat_yil", 270)

        for c in self.calisanlar:
            for d in self.gunler:
                for t in self.sablonlar:
                    if _net_saat(t) > gunluk:
                        if (c["id"], d, t["id"]) in self.x:
                            self._kisit(self.x[(c["id"], d, t["id"])] == 0)

            # Dakika cinsinden tam sayi calisilir; float kisit CP-SAT'e girmez.
            dakika = sum(int(round(_net_saat(t) * 60)) * self._X(c["id"], d, t["id"])
                         for d in self.gunler for t in self._sablonlari(c))
            # Bu kisinin fazla mesai payi: profil tavani, yillik kalanla kirpilir.
            fm_pay = fm_tavan if fm_kural else 0
            if yillik_kural and c.get("yil_ici_fazla_mesai_saat") is not None:
                kalan = max(0.0, float(yillik_azami)
                            - float(c["yil_ici_fazla_mesai_saat"]))
                if kalan < fm_pay:
                    fm_pay = kalan
                    self.notlar.append(
                        "%s: yil ici fazla mesai %.1f saat, yillik tavana %.1f "
                        "saat kaldi; bu hafta fazla mesai payi %.1f saate "
                        "indirildi (YILLIK_FAZLA_MESAI_TAVANI)"
                        % (c["id"], float(c["yil_ici_fazla_mesai_saat"]),
                           kalan, fm_pay))

            # K-38 -- HAFTALIK_AZAMI *NORMAL CALISMA* SINIRIDIR, TOPLAM TAVAN DEGIL
            #
            # ⚠ NE VARDI (29 Eylul'e kadar)
            #     self._kisit(dakika <= int(haftalik * 60))       # 45 saat
            #   Bu satir toplam saati 45'te kesiyordu. 45 saat sozlesmeli bir
            #   calisan zaten 45'te duruyordu -- yani FAZLA MESAI MATEMATIKSEL
            #   OLARAK IMKANSIZDI. Asagidaki `fazla` ceza degiskeni, profile
            #   bagli tavan ve K-30'un butun "zorunlu ise minimum yap" dali
            #   bu calisanlar icin OLU KODDU.
            #
            # ⚠ OLCULDU -- tek degisken izole edilerek, ayni sahne:
            #     HAFTALIK_AZAMI 45 -> cozumsuz
            #     HAFTALIK_AZAMI 55 -> cozuldu, 48 saat, fazla mesai bildirildi
            #
            #   Yani motor, Mustafa'nin "cozumsuzse fazla mesaiye basvuracak"
            #   dedigi kacis yolunu kullanamiyor, onun yerine yoneticiye
            #   "bu talebi bu kadroyla karsilayamazsiniz" dedirtiyordu.
            #
            # KARAR (Mustafa, 29 Eylul): "Normal calisma siniri. Toplam tavan
            #   degil. Yani minimum 45 saat calismali." Asan kisim FAZLA
            #   MESAIDIR; kendi tavanina (profile bagli) ve gunluk 11 saat
            #   sinirina tabidir -- ikisi de asagida/yukarida duruyor.
            #
            # ⚠ TAVAN KALKMADI, YERI DEGISTI: toplam hala sinirli, ama sinir
            #   artik "normal calisma + fazla mesai tavani".
            self._kisit(dakika <= int(round((haftalik + fm_pay) * 60)))

            soz = c.get("sozlesme") or {}
            tavan = soz.get("haftalik_saat")
            # ⚠ TAVAN TIPTEN GELIR, SOZLESME SAATINDEN DEGIL (K-39, 29 Eylul)
            #   Onceki kurulus `if tavan is not None:` idi. Mustafa yari
            #   zamanlida `haftalik_saat` alanini TAMAMEN kaldirinca o kosul
            #   sessizce yanlis cevap verecekti: alan yok -> blok atlanir ->
            #   yari zamanliya HIC tavan kalmaz. Kosul artik tipe bakiyor.
            if soz.get("tip") == "yari_zamanli":
                # K-39 -- TAVAN KISIDEN DEGIL MEVZUATTAN GELIR
                #
                # ⚠ NE VARDI: tavan = kisinin kendi sozlesme saati.
                #   20 saatlik bir yari zamanli, yogun bir haftada 24
                #   saat calisamiyordu -- oysa mevzuatin koydugu sinir
                #   bu degil.
                #
                # Mustafa (29 Eylul): "Kisi icin su kadar saat max veya
                #   min calisabilir diye kisit girmemize gerek yok.
                #   Yapmamiz gereken, calisanin calisabilecegi kisitli
                #   gunler veya saat araliklari varsa bunu tutmak."
                #   (O da UYGUNLUK_TAKVIMI, ayri ve SERT.)
                #
                # SINIR (Mustafa, 29 Eylul): emsal tam surelinin TAMAMI,
                # yani 45 saat. Gerekcesi: "Yasa da 45 saate kadar
                # calistirabilirsin, bu fazla mesaiye girmez diyor."
                #
                # ⚠ Once 2/3 (30 saat) yazilmisti -- kismi sureli calismanin
                #   TANIMINDAKI oran. Mustafa 45'i secti: 30-45 arasi "fazla
                #   surelerle calisma"dir ve fazla mesai ucreti dogurmaz.
                #   Oran `emsal_orani` ile kiraci basina degistirilebilir.
                #
                # ⚠ BURADA BIR FREN YOK: modelde yari zamanli saatinin
                #   MALIYETI tanimli degil. Onlari sinirlayan tek sey eskiden
                #   kendi sozlesme saatleriydi; o kalkti. Cozucunun yari
                #   zamanliyi gereksiz yere 45 saate kadar yazmamak icin bir
                #   sebebi yok -- hedef asimini cezalandiran bir kural
                #   gelene kadar bu acik durur (bkz. 06-ACIK-RISKLER T-54).
                self._kisit(dakika <= int(pt_tavan * 60))
            elif tavan is not None:
                self._kisit(dakika <= int(round((tavan + fm_pay) * 60)))
                # Fazla mesai YUMUSAK cezayla sifira itilir (A1: esit 0).
                #
                # K-30 (Mustafa, 16 Eylul): "Zaten hedef hic gitmemek.
                # Gidilecekse de minimum gitmek."
                #
                #   `fazla` DAKIKA cinsinden, agirlik 50. Bir saat fazla
                #   mesai 3000 puan; kacirilan bir hedef hucresi 9-20 puan.
                #   Yani HEDEF kapsama ugruna fazla mesai yapilmaz.
                #
                #   ASGARI kapsama SERT oldugu icin ceza hesabina girmez:
                #   fazla mesai olmadan tutmuyorsa motor onu yapar, hem de
                #   tam gerektigi kadar. Karar tam olarak bunu istiyor.
                #
                #   Yukaridaki `dakika <= (tavan + fm_tavan)` kisiti ise
                #   ZORUNLU asimin sinirini cizer: CALISAN profilinde
                #   fm_tavan 0 oldugu icin boyle bir plan cozumsuz olur.
                #   Tavan olu bir sayi degil -- isteğe bagli fazla mesai
                #   icin kullanilmiyor, zorunlu olan icin belirleyici.
                #
                #   50 sayisi bir KALIBRASYON, karar degil. Testler
                #   "ceza sifir olmasin" diyor, "tam olarak 50 olsun"
                #   demiyor (testler/test_profiller.py).
                fazla = self.m.NewIntVar(0, int(fm_tavan * 60), "fm_%s" % c["id"])
                self._kisit(fazla >= dakika - int(tavan * 60))
                self.cezalar.append((50, fazla))

    def _dinlenme(self):
        """VARDIYA_ARASI_DINLENME -- ardisik gunlerdeki her sablon cifti.

        Cakisan cift de burada yakalanir: ara negatif olur, esigin altindadir.
        """
        asgari = _par(_kural(self.girdi, "VARDIYA_ARASI_DINLENME"), "asgari_saat", 11)

        # T-28: gecmis kaydin BITISINDEN sonra `asgari` saat dolmadan
        # baslayan plan vardiyasi yazilamaz. Ortusen (hala calisiyorken
        # baslayan) vardiya da burada yakalanir: ara negatif olur.
        for c in self.calisanlar:
            for gun, _, bit, _ in _gecmis_kayitlari(c):
                bitis = gun * 24 + bit
                for d in self.gunler:
                    for t in self.sablonlar:
                        if (d * 24 + t["bas"] - bitis < asgari
                                and (c["id"], d, t["id"]) in self.x):
                            self._kisit(self.x[(c["id"], d, t["id"])] == 0)

        for c in self.calisanlar:
            for d in self.gunler[:-1]:
                for t1 in self.sablonlar:
                    bitis = d * 24 + t1["bit"]
                    for t2 in self.sablonlar:
                        baslangic = (d + 1) * 24 + t2["bas"]
                        if baslangic - bitis < asgari:
                            self._kisit(self._X(c["id"], d, t1["id"])
                                       + self._X(c["id"], d + 1, t2["id"]) <= 1)

    def _ardisik_gun(self):
        azami = _par(_kural(self.girdi, "ARDISIK_CALISMA_GUNU"), "azami_gun", 6)
        ht = _kural(self.girdi, "HAFTA_TATILI")
        if ht:
            # Kayan 7 gunluk pencerede kesintisiz dinlenme (T-11).
            # Yedi gunluk planda karsiligi: en az bir gun bos.
            azami = min(azami, _par(ht, "pencere_gun", 7) - 1)
        for c in self.calisanlar:
            for bas in range(0, HAFTA_GUN - azami):
                self._kisit(sum(self._calisiyor(c["id"], d)
                               for d in range(bas, bas + azami + 1)) <= azami)
            # T-28: gecmise uzanan pencere. Kayitli gecmis gunleri SABIT
            # olarak sayilir; bilinmeyen gun 0'dir (K-42).
            gecmis = {g for g, _, _, _ in _gecmis_kayitlari(c)}
            for bas in range(-azami, 0):
                sabit = sum(1 for d in range(bas, 0) if d in gecmis)
                if not sabit:
                    continue
                plan = range(0, min(HAFTA_GUN, bas + azami + 1))
                self._kisit(sabit + sum(self._calisiyor(c["id"], d)
                                       for d in plan) <= azami)

    def _ardisik_gece(self):
        """ARDISIK_GECE_LIMIT -- ust uste azami gece (firma kurali, SERT).

        Kayan pencere: her `azami+1` gunluk dilimde en fazla `azami` gece.
        `_ardisik_gun` ile ayni kalip.

        GECE = K-40'in tespiti (`_gece_sablonu`): isaret varsa o, yoksa
        saat araligi. Dogrulayicida ayni tespit AYRI yazili (#7.6).

        ⚠ GECMIS OKUNUR (T-28 kapandi, 30 Eylul): kayitli gecmis geceler
          pencereye SABIT olarak girer; bilinmeyen gun 0'dir (K-42).
        """
        kural = _kural(self.girdi, "ARDISIK_GECE_LIMIT")
        if not kural:
            return
        azami = int(_par(kural, "azami_gece", 3))
        geceler = [t for t in self.sablonlar if _gece_sablonu(t)[0]]
        if not geceler or azami >= HAFTA_GUN:
            return
        for c in self.calisanlar:
            for bas in range(0, HAFTA_GUN - azami):
                terim = [self.x[(c["id"], d, t["id"])]
                         for d in range(bas, bas + azami + 1)
                         for t in geceler
                         if (c["id"], d, t["id"]) in self.x]
                if terim:
                    self._kisit(sum(terim) <= azami)
            # T-28: cuma-cumartesi-pazar gecesi kayitliysa pazartesi gecesi
            # dorduncudur. Kayitli gecmis geceler SABIT sayilir (K-42).
            gecmis_geceler = {g for g, b0, b1, isaret in _gecmis_kayitlari(c)
                              if _gecmis_gece_mi(b0, b1, isaret)}
            for bas in range(-azami, 0):
                sabit = sum(1 for d in range(bas, 0) if d in gecmis_geceler)
                if not sabit:
                    continue
                terim = [self.x[(c["id"], d, t["id"])]
                         for d in range(0, min(HAFTA_GUN, bas + azami + 1))
                         for t in geceler
                         if (c["id"], d, t["id"]) in self.x]
                if terim:
                    self._kisit(sabit + sum(terim) <= azami)

    # ---- hafta olcekli kurallar (30 Eylul; tanimlar K-45, K-46) ----------
    #
    # Ikisi de planin DISINA bakar. Cozucunun ufku tek hafta oldugu icin
    # ikisinin kisiti da ayni bicimde: gecmisteki KANITLI haftalar sinira
    # ulasmissa bu haftaya ilgili kisit yazilir. Bilinmeyen hafta 0 sayilir
    # -- kisit yok (K-42); raporu dogrulayici yazar.
    #
    # ⚠ HAFTA `gun // 7` ile: -1..-7 -> -1. `int(gun / 7)` -1'i 0'a
    #   yuvarlar ve gecen pazari BU haftaya koyardi.
    # ⚠ AYNI TANIMLAR DOGRULAYICIDA AYRICA YAZILI (#7.6).

    def _gece_haftasi_gecmiste(self, c, hafta, asgari_gece):
        """Gecmis hafta KANITLI gece haftasi mi -- K-45 + K-42.

        Yalniz TAM bilinen hafta degerlendirilir (yedi gunu de
        `gecmis_bilinen_gunler`de ya da kayitli). Cogunluk olcusu yarim
        bilgiyle hesaplanamaz: bir gunu bilinmeyen haftada "gece" demek,
        kaydin yoklugundan kisit uretmek olurdu.
        Olcu BRUT saat (PDKS kaydinda mola yok).
        """
        bilinen = _bilinen_gunler(c)
        if not all(d in bilinen for d in range(7 * hafta, 7 * hafta + 7)):
            return False
        kayitlar = [(g, b0, b1) for g, b0, b1, _ in _gecmis_kayitlari(c)
                    if g // 7 == hafta]
        if not kayitlar:
            return False
        gece = [(b0, b1) for _, b0, b1 in kayitlar
                if _yasal_gece_postasi(b0, b1)]
        if asgari_gece is not None and len(gece) >= int(asgari_gece) > 0:
            return True
        gece_saat = sum(b1 - b0 for b0, b1 in gece)
        toplam = sum(b1 - b0 for _, b0, b1 in kayitlar)
        return 2 * gece_saat > toplam + 1e-9

    def _gece_postasi_devri(self):
        """GECE_POSTASI_DEVRI -- YASAL, Is K. md. 69 / Postalar Yon. md. 8.

        K-45 (Mustafa, 30 Eylul gecesi):
          * GECE HAFTASI = haftanin calisma saatlerinin YARISINDAN COGU gece
            postasinda (yonetmeligin tek vardiya olcusu haftaya uygulandi).
            `gece_haftasi_asgari_gece` verildiyse o kadar gece de yeter --
            yalniz EKLER.
          * KURAL: art arda 2 x azami haftada en fazla azami gece haftasi.
            azami 1: gece-gunduz-gece-gunduz; azami 2: gece-gece-gunduz-
            gunduz (md. 8/3). Ust sinir 2 -- fazlasi 2'ye kirpilir, not.
          * GECE = yonetmeligin tanimi (`_yasal_gece_postasi`), K-40
            isareti DEGIL; gecmis kaydin isareti de okunmaz.

        Plan haftasina kisit: son (2 x azami - 1) haftada KANITLI gece
        haftasi sayisi azami'ye ulastiysa bu hafta gece haftasi OLAMAZ:
            2 x (gece postasi saatleri) <= (butun saatler)   [ceyrek dilim]
        ve varsa: gece postasi sayisi <= asgari_gece - 1.
        """
        kural = _kural(self.girdi, "GECE_POSTASI_DEVRI")
        if not kural:
            return
        verilen = int(_par(kural, "azami_ardisik_gece_haftasi", 1))
        azami = max(1, min(verilen, 2))
        if verilen != azami:
            self.notlar.append(
                "GECE_POSTASI_DEVRI: azami_ardisik_gece_haftasi %d verildi, "
                "yasal ust sinir %d uygulandi (K-45)" % (verilen, azami))
        asgari_gece = _par(kural, "gece_haftasi_asgari_gece", None)
        geceler = [t for t in self.sablonlar
                   if _yasal_gece_postasi(t["bas"], t["bit"])]
        if not geceler:
            return
        gece_kimlik = {t["id"] for t in geceler}
        for c in self.calisanlar:
            kanitli = sum(1 for h in range(-(2 * azami - 1), 0)
                          if self._gece_haftasi_gecmiste(c, h, asgari_gece))
            if kanitli < azami:
                continue
            gece_terim, toplam_terim, gece_sayi = [], [], []
            for d in self.gunler:
                for t in self._calisan_sablonlari(c["id"]):
                    x = self.x.get((c["id"], d, t["id"]))
                    if x is None:
                        continue
                    sure = len(_dilimler(d, t["bas"], t["bit"]))
                    toplam_terim.append(sure * x)
                    if t["id"] in gece_kimlik:
                        gece_terim.append(sure * x)
                        gece_sayi.append(x)
            if gece_terim:
                self._kisit(2 * sum(gece_terim) <= sum(toplam_terim))
                if asgari_gece is not None and int(asgari_gece) > 0:
                    self._kisit(sum(gece_sayi) <= int(asgari_gece) - 1)

    def _hafta_sonu_gecmiste_tam(self, c, hafta):
        """Gecmis hafta sonu KANITLI olarak iki gunu de calisilmis mi
        (K-46, cogunluk gunuyle). Kaydin yoklugu calisilmadigini kanitlamaz
        ama burada yalniz "kanitli calisildi" sayilir (K-42)."""
        gunler = set()
        for g, b0, b1, _ in _gecmis_kayitlari(c):
            hg = _hafta_sonu_gunu(g, b0, b1)
            if hg is not None and (g + _cogunluk_gunu_kaymasi(b0, b1)) // 7 == hafta:
                gunler.add(hg)
        return gunler >= {5, 6}

    def _ardisik_hafta_sonu(self):
        """ARDISIK_HAFTA_SONU_LIMIT -- firma kurali, SERT (#6.5).

        K-46 (Mustafa, 30 Eylul gecesi): "hafta sonu calisti" = HEM
        cumartesi HEM pazar; gun = saatlerinin yarisindan cogunun dustugu
        gun (cuma 23:00-06:00 cumartesidir). Onceki tanim (bir gun yeter)
        ucuncu haftayi cozumsuz birakiyordu (T-75).

        Gecmiste son `azami` hafta sonu KANITLI olarak tam calisildiysa bu
        hafta sonu tam calisilamaz: cumartesi-vardiyasi ile pazar-vardiyasi
        ciftlerinden en fazla biri.
        """
        kural = _kural(self.girdi, "ARDISIK_HAFTA_SONU_LIMIT")
        if not kural:
            return
        azami = int(_par(kural, "azami_ardisik", 2))
        for c in self.calisanlar:
            if not all(self._hafta_sonu_gecmiste_tam(c, h)
                       for h in range(-1, -azami - 1, -1)):
                continue
            cumartesi, pazar = [], []
            for d in self.gunler:
                for t in self._calisan_sablonlari(c["id"]):
                    x = self.x.get((c["id"], d, t["id"]))
                    if x is None:
                        continue
                    hg = _hafta_sonu_gunu(d, t["bas"], t["bit"])
                    if hg == 5:
                        cumartesi.append(x)
                    elif hg == 6:
                        pazar.append(x)
            for x1 in cumartesi:
                for x2 in pazar:
                    self._kisit(x1 + x2 <= 1)

    def _asgari_vardiya(self):
        """ASGARI_VARDIYA_SURESI -- en kisa vardiya (firma kurali, SERT).

        Sablonlar sabit oldugu icin bu bir SABLON suzgecidir: asgarinin
        altindaki sablon HIC atanmaz ve bunu not olarak soyler -- firma
        kendi sablonunun neden kullanilmadigini gormeli.

        Olcu BRUT (vardiya suresi). Gerekcesi dogrulayicida.
        """
        kural = _kural(self.girdi, "ASGARI_VARDIYA_SURESI")
        if not kural:
            return
        asgari = float(_par(kural, "asgari_saat", 4))
        kisalar = []
        for t in self.sablonlar:
            sure = float(t["bit"]) - float(t["bas"])
            if sure <= 0:
                sure += 24.0          # Z-1: ham yazimli gece yarisi tasmasi
            if sure < asgari - 1e-9:
                kisalar.append((t, sure))
        if not kisalar:
            return
        self.notlar.append(
            "ASGARI_VARDIYA_SURESI: su sablonlar %s saatten kisa ve "
            "kullanilmayacak: %s"
            % (asgari, ", ".join("%s (%.2f sa)" % (t["id"], s)
                                 for t, s in kisalar)))
        for c in self.calisanlar:
            for d in self.gunler:
                for t, _ in kisalar:
                    if (c["id"], d, t["id"]) in self.x:
                        self._kisit(self.x[(c["id"], d, t["id"])] == 0)

    # ---- kapsama ------------------------------------------------------

    def _hucreler(self):
        """Sartname #11.2: BIR talep satiri = BIR hucre {ekip, gun, saat}.

        T-19 (23 Eylul). Bu satirlar 23 Eylul'e kadar gruplu bicim okuyordu
        ({gunler: [...], saatler: [...]}). Sartname biciminde bir istek
        gelince motor talebi HIC gormuyor, sifir atamali plan uretiyor ve
        kapsama %100 cikiyordu. Kimse yanlis degildi: fikstur bir bicim
        secti, motor fiksture bakarak yazildi; ikisi birbiriyle tutarli,
        ikisi de sartnameyle tutarsizdi. Karar (Mustafa): SARTNAME KAZANIR.

        Okunamayan satir burada SESSIZCE atlanir, ve bu bilerekdir: "neye
        bakmadim" demek #7.6 geregi dogrulayicinin isi
        (dogrulayici.denetle._okunmayan_alanlar). Cozucu rapor uretmez.
        """
        for t in self.girdi.get("talep", []) or []:
            gun, saat = t.get("gun"), t.get("saat")
            if gun is None or saat is None:
                continue
            yield t, gun, saat

    def _atama_ekibi(self, c, t):
        """Atamanin VARDIYA EKIBI -- ciktidaki `ekip` alani (K-50, 1 Ekim).

        Sablonun ekibi varsa o; yoksa calisanin ILK ekibi. Bu alan atamanin
        hangi vardiyada oldugunu soyler; KAPSAMAYA KIMIN SAYILDIGINI
        `_sayilir` soyler, ikisi ayri sey.
        """
        ekip = t.get("ekip")
        if ekip is not None:
            return ekip
        ekipler = c.get("ekipler") or []
        return ekipler[0] if ekipler else None

    def _sayilir(self, c, t, ekip):
        """Bu kisi bu sablondayken BU EKIBIN kapsamasina sayilir mi -- K-50.

        MUSTAFA (1 Ekim): "Sahada hem satis hem backoffice yapabilen
          elemanlar var. O saatte o eleman iki birim elemani icin yer
          doldurmus sayilir. Gece 12'den sonra backoffice talebi yok denecek
          kadar azaliyor; oraya asil isi satis ama backoffice yetenegi olan
          bir eleman konuyor, sorun sahada cozulmus oluyor."

        Varsayilan `hepsi`: kisi uye oldugu BUTUN ekiplere sayilir -- talep
        sayisi "o yetenekte hazir bulunan kisi"dir, adanmis beden degil.
        Kiraci `tek` derse (girdi.cok_ekipli_sayim) atama yalniz vardiyanin
        ekibine sayilir (ekipsiz sablonda kisinin ilk ekibine).

        ⚠ T-21 (16 Eylul dis incelemesi) bunu "modelin inanci yanlis" diye
          acmisti: cozucu `hepsi` gibi sayiyor, dogrulayici `tek` gibi
          sayiyordu; iki taraf ayni plan icin farkli konusuyordu. Karar
          cozucuyu degil dogrulayiciyi degistirdi. Gorunurluk dogrulayicida:
          `metrikler.baska_ekipten_kapsama`.
        """
        if self.cok_ekipli_sayim == "tek":
            return self._atama_ekibi(c, t) == ekip
        return ekip in (c.get("ekipler") or [])

    def _atanmis(self, ekip, gun, saat):
        """O hucreye ATANMIS kisiler -- mola DUSULMEZ (ASGARI/HEDEF_KAPSAMA).

        K-50: kim sayilir, `_sayilir` soyler."""
        dilim = _q(gun, saat)
        return [self._X(c["id"], d, t["id"])
                for c in self.calisanlar
                if ekip in (c.get("ekipler") or [])
                for d in self.gunler
                for t in self._sablonlari(c)
                if self._sayilir(c, t, ekip)
                and dilim in _dilimler(d, t["bas"], t["bit"])]

    def _sahada(self, ekip, gun, saat):
        """O hucrede SAHADA olanlar -- BUTUN molalar dusulur (MOLA_KAPSAMASI).

        ARITMETIK NOTU (K-32, 28 Eylul)
          "Sahada" = atanmis VE hicbir mola bu dilimi kapsamiyor. Bu bir VE
          bagladir ve carpim gerektiriyor gibi gorunur -- gerektirmiyor,
          cunku molalar birbirini KESMIYOR: _dinlenme_degiskenleri yemekle
          cakismayi yasakliyor, dinlenmeler arasi cakisma ise aday
          pencereleri ayrik oldugu icin zaten imkansiz.

          Kesismeyen olaylarda "molada olmak" bir TOPLAMDIR:

              sahada = (kapsamayan yemek secenekleri) - (kapsayan dinlenmeler)

          Ilk terim atanmissa 1, atanmamissa 0. Ikinci terim dinlenme o
          dilimi kapsiyorsa 1. Ikisi de dogrusal; yardimci degisken ve
          reification GEREKMIYOR. Cakismama kisiti bu yuzden yalniz "adil
          plan" icin degil, bu aritmetigin GECERLILIGI icin de sarttir --
          iki mola ayni dilimi kapsarsa sonuc eksiye duser.

          K-34 (28 Eylul): `dilim` artik CEYREK SAAT. Aritmetik aynen
          gecerli -- degisen yalnizca izgaranin sikligi. `saat` kesirli
          gelebilir (14.25 gibi); `_q` onu dogru dilime cevirir.

          T-78 (1 Ekim): "kesismiyor" GERCEK ZAMANDA saglanir
          (_dinlenme_degiskenleri, _gercek_kesisiyor) ve bir molanin
          kapladigi dilimler YUKARI yuvarlanir (_mola_dilimleri). Ikisi
          birlikte bu toplamin eksiye dusmemesini garanti eder: baslangic
          ceyrek izgarasinda oldugu icin gercek zamanda ayrik iki molanin
          dilim kumeleri de ayriktir.
        """
        dilim = _q(gun, saat)
        cikan = []
        for c in self.calisanlar:
            if ekip not in (c.get("ekipler") or []):
                continue
            for d in self.gunler:
                for t in self._sablonlari(c):
                    if not self._sayilir(c, t, ekip):        # K-50
                        continue
                    if dilim not in _dilimler(d, t["bas"], t["bit"]):
                        continue
                    yemek_dk = self.yemek_dk[t["id"]]
                    terim = [self.mola[(c["id"], d, t["id"], s)]
                             for s in _mola_baslangiclari(t, self.mola_penceresi,
                                                          yemek_dk)
                             if dilim not in _mola_dilimleri(d, t, s, yemek_dk)]
                    if not terim:
                        continue      # her secenekte yemekte -- hic sahada degil
                    ifade = sum(terim)
                    _, dk = self.dinlenme_tanim[t["id"]]
                    for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
                        for s in adaylar:
                            anahtar = (c["id"], d, t["id"], i, s)
                            if (anahtar in self.dinlenme
                                    and dilim in _mola_dilimleri(d, t, s, dk)):
                                ifade = ifade - self.dinlenme[anahtar]
                    cikan.append(ifade)
        return cikan

    def _kapsama(self):
        asgari_kural = _kural(self.girdi, "ASGARI_KAPSAMA")
        hedef_kural = _kural(self.girdi, "HEDEF_KAPSAMA")
        mola_kural = _kural(self.girdi, "MOLA_KAPSAMASI")
        hedef_agirlik = self._agirlik("HEDEF_KAPSAMA", hedef_kural)
        mola_agirlik = self._agirlik("MOLA_KAPSAMASI", mola_kural)
        # HEDEF_ASIMI (K-53, T-54): hedefi ASAN kisi-saat ceza. Bu olmadan
        # bir saatin bedeli yoktu; 4 yari zamanli, 1 kisilik talep icin
        # dordu de 45 saate dolduruluyordu (29 Eylul'de olculdu).
        asim_kural = _kural(self.girdi, "HEDEF_ASIMI")
        asim_agirlik = self._agirlik("HEDEF_ASIMI", asim_kural) if asim_kural else 0
        kisi_sayisi = max(1, len(self.calisanlar))
        # SAHADA_ASGARI (K-33): firmanin "sahada en az N kisi" cumlesi.
        # Talep tablosunun `asgari`si ile SINIRLANMAZ -- ikisi ayri sey
        # soyler, ikisi de SERT, kati olan baglar. Ayrintisi ve bir kez
        # yapilan min(...) hatasinin kaydi kurallar.py::sahada_asgari'de.
        taban_kisi = _par(_kural(self.girdi, "SAHADA_ASGARI"),
                          "asgari_sahada", 0)

        for t, gun, saat in self._hucreler():
            atanmis = self._atanmis(t.get("ekip"), gun, saat)
            if asgari_kural and t.get("asgari"):
                self._kisit(sum(atanmis) >= t["asgari"])
            if hedef_kural and t.get("hedef"):
                eksik = self.m.NewIntVar(0, t["hedef"], "he_%d_%d" % (gun, saat))
                self._kisit(eksik >= t["hedef"] - sum(atanmis))
                self.cezalar.append((hedef_agirlik, eksik))
            if asim_kural and t.get("hedef") is not None:
                asim = self.m.NewIntVar(0, kisi_sayisi, "ha_%d_%d" % (gun, saat))
                self._kisit(asim >= sum(atanmis) - t["hedef"])
                self.cezalar.append((asim_agirlik, asim))
            # MOLA_KAPSAMASI (yumusak) -- K-34: hucrenin DORT ceyregi ayri
            # ayri olculur ama CEZA DEGISKENI TEK KALIR ve hucrenin EN KOTU
            # anini tasir.
            #
            # ⚠ Neden ceyrek basina ayri ceza degil: `self.cezalar` agirlikli
            #   bir toplamdir. Ceyrek basina bir degisken koymak bu kuralin
            #   agirligini otekilere gore DORT KATINA cikarirdi -- plan
            #   secimi sessizce degisirdi. Tek degisken + dort kisit ayni
            #   olcegi korur ve bilgiyi INCELTIR: eskiden saatin tek bir
            #   degeri bakiliyordu, simdi en kotu ceyregi.
            if mola_kural and t.get("asgari"):
                eksik = self.m.NewIntVar(0, t["asgari"], "me_%d_%d" % (gun, saat))
                for ceyrek in range(CEYREK):
                    an = saat + ceyrek / float(CEYREK)
                    self._kisit(eksik >= t["asgari"]
                               - sum(self._sahada(t.get("ekip"), gun, an)))
                self.cezalar.append((mola_agirlik, eksik))
            # SERT saha tabani (K-33). MOLA_KAPSAMASI (yumusak) plani
            # `asgari`ye dogru iter; bu kural tabanin COKMESINI engeller.
            # Ikisi ayri isi yapar, biri otekinin yerine gecmez.
            #
            # `t.get("asgari")` KOSUL DEGIL: talep hucresi varsa taban da
            # vardir. Taban hucrenin asgarisinden buyukse atamayi YUKARI
            # ceker -- kasitli, cunku ikisi de SERT ve kati olan baglar.
            #
            # K-34: SERT oldugu icin her CEYREGE ayri kisit yazilir. Olcek
            # sorunu yok (ceza degil kisit), ve taban "saatin bir aninda"
            # degil "her aninda" tutmali -- 14:15'te cokup 14:00'de duran
            # bir saha, tabani tutmus sayilmaz.
            if taban_kisi:
                for ceyrek in range(CEYREK):
                    an = saat + ceyrek / float(CEYREK)
                    self._kisit(sum(self._sahada(t.get("ekip"), gun, an))
                               >= taban_kisi)

    def _yetkinlik(self):
        """ROL_KAPSAMASI / YETKINLIK_KAPSAMASI -- satir bazli gereklilikler.

        Olcu ATANMIS olmaktir, sahada olmak degil -- K-41 (Mustafa,
        30 Eylul): "Sahada bir mudurun isi 15 dk mola suresini bekleyebilir."
        Dogrulayici tarafi da ayni olcuyu kullanir.

        ⚠ 30 Eylul -- BU GOVDEDE IKI AYRI SESSIZLIK VARDI (T-62)
          Ikisi de bagimsiz dogrulayici yazilinca gorundu; o gune kadar
          bu kural icin denetci yoktu, yani kimse fark edemezdi.

          1. `saatler` YAZILMAMISSA HICBIR KISIT YAZILMIYORDU.
             Eski satir `for saat in p.get("saatler", [])` idi: liste yoksa
             dongu hic calismiyor, aktif bir SERT kural modele TEK kisit
             koymuyordu. Sartname rol kuralini "her ACIK saatte" diye
             tanimliyor -- yani liste yoksa acik saatlerin HEPSI gecerli
             olmali, hicbiri degil. Olculdu: 49 kisilik sahnede gereklilik
             konunca plan DEGISMEDI (ayni 221 atama) ve bagimsiz denetci
             1.238 sert ihlal yazdi.

          2. `ekip` YAZILMAMISSA PLAN COZUMSUZ KALIYORDU.
             Eski suzgec `p.get("ekip") in (c.get("ekipler") or [])` idi:
             ekip yoksa karsilastirma None ile yapiliyor, hic kimse uygun
             sayilmiyor ve modele "bos toplam >= 1" kisiti giriyordu.
             Yoneticinin gordugu cumle "bu talebi bu kadroyla karsilamak
             imkansiz" olurdu; sebebi bir eksik parametre.
             Artik ekip yoksa kural SAHA CAPINDA okunur -- dogrulayici
             govdesi de boyle okuyor.

          3. Kontrol artik CEYREK bazinda. K-34'ten beri vardiya 15:30'da
             bitebiliyor; yalniz tam saate bakmak, saatin son yarisinda
             niteligin sahada olmadigini goremez. `_talep_anlari`nin
             gerekcesiyle ayni.

        ⚠ NITELIGI TASIYAN KIMSE YOKSA KISIT YAZILMAZ, NOT YAZILIR.
          Kisit yazmak plani sessizce cozumsuz yapardi ve sebebi
          gorunmezdi. Karsiligini dogrulayici soyler: gereklilik
          tutulmuyorsa ihlal yazar. Yuksek sesle yanlis, sessizce
          cozumsuzdan iyidir (#7.6).

        ⚠ COK EKIPLI CALISAN -- T-21, K-50 (1 Ekim) ile KAPANDI.
          Kim sayilir, `_sayilir` soyler (varsayilan: uye oldugu butun
          ekiplere); dogrulayici ayni olcuyu kullanir.
        """
        for kod, alan in (("YETKINLIK_KAPSAMASI", "yetkinlikler"),
                          ("ROL_KAPSAMASI", "operasyonel_rol")):
            for k in self.girdi.get("kurallar", []) or []:
                if k.get("kod") != kod or not k.get("aktif", True):
                    continue
                p = k.get("parametreler") or {}
                aranan = p.get("yetkinlik") or p.get("rol")
                if aranan is None:
                    self.notlar.append("%s parametresiz, atlandi" % kod)
                    continue
                asgari = p.get("asgari", 1)
                if asgari <= 0:
                    self.notlar.append(
                        "%s asgari %r, kisit yazilmadi" % (kod, asgari))
                    continue
                ekip = p.get("ekip")
                uygun = [c for c in self.calisanlar
                         if (aranan in (c.get(alan) or [])
                             if alan == "yetkinlikler"
                             else c.get(alan) == aranan)
                         and (ekip is None
                              or ekip in (c.get("ekipler") or []))]
                if not uygun:
                    self.notlar.append(
                        "%s: '%s' niteligini tasiyan uygun calisan yok, "
                        "kisit yazilmadi" % (kod, aranan))
                    continue

                saatler = p.get("saatler")
                saat_kumesi = (None if saatler is None
                               else {int(x) for x in saatler})
                gun_suzgeci = p.get("gun")

                # Denetlenecek dilimler talep hucrelerinden turetilir:
                # "acik saat" = talep hucresi olan saat.
                dilimler = set()
                for t, gun, saat in self._hucreler():
                    if ekip is not None and t.get("ekip") != ekip:
                        continue
                    if gun_suzgeci is not None and gun != gun_suzgeci:
                        continue
                    if saat_kumesi is not None and int(saat) not in saat_kumesi:
                        continue
                    for ceyrek in range(CEYREK):
                        dilimler.add(_q(gun, saat + ceyrek / float(CEYREK)))

                if not dilimler:
                    self.notlar.append(
                        "%s: '%s' icin denetlenecek acik saat yok "
                        "(ekip/gun/saat suzgeci hic hucre birakmadi)"
                        % (kod, aranan))
                    continue

                for dilim in sorted(dilimler):
                    # K-50: ekip verildiyse yalniz o ekibe SAYILAN atamalar.
                    var = [self._X(c["id"], d, t["id"])
                           for c in uygun
                           for d in self.gunler
                           for t in self._sablonlari(c)
                           if (ekip is None or self._sayilir(c, t, ekip))
                           and dilim in _dilimler(d, t["bas"], t["bit"])]
                    self._kisit(sum(var) >= asgari)

    # ---- amac ---------------------------------------------------------

    def _amac(self):
        self._adalet()
        self._saat_dengesi()
        if self.cezalar:
            self.m.Minimize(sum(a * v for a, v in self.cezalar))

    def _adalet(self):
        """ADALET_DENGESI -- IKI KATMANLI ceza.

        K-27 (Mustafa, 16 Eylul) IHLAL esigini koydu: ortalamadan 2 fazla
        calismak adaletsizliktir. Ama esik tek basina AMAC FONKSIYONU olamaz.

        ESIK BURADA YOK -- YALNIZ DOGRULAYICIDA VAR
          Ilk yazilista esik amac fonksiyonuna da konmustu. Iki bulgu
          uzerine cikarildi:

          1. OLCULDU: esik terimi tamamen kapatildiginda 57 birim testinin
             ve 12 altin senaryonun HICBIRI degismedi. Terim atildi.
             Sebebi matematiksel: atama sayisi kapsama tarafindan sabitken
             ucgensel maliyet en duz dagilimda en kucuktur, en duz dagilim
             da en yuksek kisiyi en kucuk yapar -- yani gradyan zaten esik
             ihlalini enazliyor. Esik ayrica bir sey eklemiyor.

          2. EKLESEYDI YANLIS SEY EKLERDI: esik ORTALAMAYA gore tanimli.
             Motorun ihlali kaldirmanin ucuz bir yolu var: ortalamayi
             yukseltmek, yani BASKALARINA GEREKSIZ CUMARTESI VERMEK.
             "C01 bu ay uc cumartesi calismis; o goze batmasin diye uc
             kisiyi daha cumartesiye koyalim" -- sahada sacma, modelde
             ucuz. Gradyanda bu acik yok: her ek atama para eder.

          K-27 IPTAL DEGIL: ihlali sayan ve yayin kapisina bildiren yer
          bagimsiz dogrulayicidir (dogrulayici/kurallar.py ADALET_DENGESI).
          Motorun tercihi ile kuralin tanimi ayri seylerdir; #7.6'nin
          ayirdigi sey de tam olarak budur.

        NEDEN GEREKLI -- A7'de somut olarak goruldu
          Esik tek basinayken esigin ALTINDAKI butun dagilimlar sifir ceza
          aliyordu. Yani "C01 ucuncu kez cumartesi" ile "C04 ilk kez
          cumartesi" motor icin ESIT degerdeydi ve cozucu aralarinda arama
          sirasina gore seciyordu. Agirligi 2'den 8'e cikarmak da bir sey
          degistirmiyordu: sifirin sekiz kati yine sifir. Iki profil ayni
          plani uretiyordu -- #5.4'un "ayni kural seti, uc farkli plan"
          iddiasi calismiyordu.

        CEZANIN BICIMI: ARTAN MARJINAL MALIYET
          Ucuncu cumartesi ikinciden, ikinci birinciden pahalidir. Ucgensel
          maliyet -- T(v) = v + (v-1) + ... + 1 -- ve `y_j >= sayi - j`
          seklinde DOGRUSAL kurulur. Uc ozelligi birden verir:

            * yuku zaten agir olana bir tane daha vermek PAHALI  (dagitir)
            * gereksiz atama ucuza gelmez                        (sismez)
            * ortalamaya bakmaz                                  (oyunlanmaz)

          Ilk denenen bicim "ortalamanin ustundeki sapma" idi ve olculdugunde
          sasirtici bir davranis cikti: motor cumartesiye gerekenden fazla
          kisi koyuyordu (3 yerine 5). Ortalamayi yukseltmek herkesin
          sapmasini dusurduyor -- ceza, cezalandirdigi seyi odullendiriyordu.
          Mutlak sapma da ayni acigi veriyor. Ucgensel maliyette bu acik yok.

        > KARAR BEKLIYOR (K-29): "adalet" yalniz esik midir (taban), yoksa
        > esik alti da tercih midir (gradyan)? Bu kod gradyani varsayiyor
        > cunku #5.4 agirliklarin farkli plan uretmesini sart kosuyor.
        """
        k = _kural(self.girdi, "ADALET_DENGESI")
        if not k:
            return
        agirlik = self._agirlik("ADALET_DENGESI", k)
        if not self.calisanlar:
            return
        for boyut in _par(k, "boyutlar", ["gece", "hafta_sonu"]):
            sayac = self._boyut_sayaci(boyut)
            if sayac is None:
                self.notlar.append("ADALET_DENGESI boyutu sayilamiyor: %s (T-13)" % boyut)
                continue
            sayim = {}
            en_yuksek_devir = 0
            for c in self.calisanlar:
                devir = (c.get("devir_yuk") or {}).get(boyut, 0)
                en_yuksek_devir = max(en_yuksek_devir, devir)
                sayim[c["id"]] = devir + sum(
                    self._X(c["id"], d, t["id"])
                    for d in self.gunler for t in self._sablonlari(c) if sayac(t, d))

            # Bu boyutta bir kisinin alabilecegi en yuksek sayi: devri +
            # boyuta giren gun sayisi. "cumartesi" icin 1, "hafta_sonu" icin 2.
            gun_sayisi = len([d for d in self.gunler
                              if any(sayac(t, d) for t in self.sablonlar)])
            azami = en_yuksek_devir + gun_sayisi

            for c in self.calisanlar:
                for j in range(azami):
                    y = self.m.NewIntVar(0, azami, "ag_%s_%s_%d"
                                         % (boyut, c["id"], j))
                    self._kisit(y >= sayim[c["id"]] - j)
                    self.cezalar.append((agirlik, y))

    def _boyut_sayaci(self, boyut):
        if boyut == "gece":
            return lambda t, d: _gece_sablonu(t)[0]
        # K-46: gun = saatlerinin yarisindan cogunun dustugu gun.
        if boyut == "hafta_sonu":
            return lambda t, d: _hafta_sonu_gunu(d, t["bas"], t["bit"]) is not None
        if boyut == "cumartesi":
            return lambda t, d: _hafta_sonu_gunu(d, t["bas"], t["bit"]) == 5
        return None

    def _saat_dengesi(self):
        """K-39 -- tam zamanli calisan SOZLESME SAATINI DOLDURUR.

        ⚠ NE VARDI (29 Eylul'e kadar)
          Kural YUMUSAK, TEK TARAFLI ve 2 SAAT TOLERANSLIYDI. Yani 43 saat
          bedava, 42 saat cok ucuzdu. 350 kisilik sahnede olculdu: 45 saat
          sozlesmeli 17 kisiden 45'i tutturan SIFIR, ortalama 38,2 saat --
          ve plan "0 sert ihlal, yayinlanabilir: True" donuyordu.

        ⚠ NEDEN SERT (Mustafa, 29 Eylul)
            "Turkiye'de saat basina degil net maas verildigi icin, tam
             zamanli bir calisanin 43 saat calismasi demek ona 2 saat
             fazla para veriyorum demektir. Boyle plan yapilmaz."
          Yani eksik planlama kanunu degil BUTCEYI deler -- ama yapilmaz.

        ⚠ IZIN BORCU DUSURUR, MUSAITSIZLIK DUSURMEZ
          Yillik izin UCRETLIDIR: o saatin parasi zaten odeniyor. Uygunluk
          takvimi ("o gun calisamam") ise bir odeme degil bir kisittir;
          borcu dusurmez. Ikisini ayni saymak, calisani eksik calistirip
          "olsun, zaten musait degildi" demek olurdu.

        TABAN YALNIZ TAM ZAMANLIYA UYGULANIR (Mustafa): yari zamanlida
        kisiye ozel taban yoktur; onlar yogun saatlere gore cagrilir.
        """
        k = _kural(self.girdi, "SAAT_DENGESI")
        if not k:
            return
        sert = (k.get("tur") == "SERT")
        agirlik = self._agirlik("SAAT_DENGESI", k)
        for c in self.calisanlar:
            soz = c.get("sozlesme") or {}
            if soz.get("tip") != "tam_zamanli":
                continue
            if soz.get("haftalik_saat") is None:
                continue
            gereken_dk = _borc_dakika(c)
            if gereken_dk <= 0:
                continue
            dakika = sum(int(round(_net_saat(t) * 60)) * self._X(c["id"], d, t["id"])
                         for d in self.gunler for t in self._sablonlari(c))
            if sert:
                self._kisit(dakika >= gereken_dk)
            else:
                sapma = self.m.NewIntVar(0, 100000, "sd_%s" % c["id"])
                self._kisit(sapma >= gereken_dk - dakika)
                self.cezalar.append((agirlik, sapma))


def _borc_dakika(c):
    """Bu calisanin bu hafta DOLDURMASI GEREKEN net dakika.

        gunluk norm = haftalik_saat / gun_sayisi
        borc        = haftalik_saat - (onayli izin gunu x gunluk norm)

    ⚠ `gun_sayisi` OLMADAN IZIN SAATE CEVRILEMEZ. Ayni 45 saat, 6 gunluk
      desende bir izin gunu 7,5 saat; 5 gunluk desende 9,0 saat eder.
      Alan yoksa 6 varsayilir (Turkiye'de yaygin desen).

    ⚠ BU HESAP DOGRULAYICIDA IKINCI KEZ, BAGIMSIZ OLARAK YAZILMISTIR
      (#7.6). Ortak bir module cikarmak YASAKTIR: ayni yanlis varsayim iki
      yere birden gecerse hicbir test yakalamaz.
    """
    soz = c.get("sozlesme") or {}
    hafta = soz.get("haftalik_saat")
    if hafta is None:
        return 0
    gun_sayisi = soz.get("gun_sayisi") or 6
    gunluk = float(hafta) / max(1, int(gun_sayisi))
    izin_gun = len({i["gun"] for i in (c.get("izinler") or [])
                    if i.get("durum", "onayli") == "onayli"})
    return max(0, int(round((float(hafta) - izin_gun * gunluk) * 60)))
