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
    sure_q = int(round(sure * CEYREK))
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
    """
    if baslangic is None:
        return []
    dk = sablon.get("mola_dk", 0) if dakika is None else dakika
    if dk <= 0:
        return []
    return list(range(_q(gun, baslangic), _q(gun, baslangic + dk / 60.0)))


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
    """
    if "gece_vardiyasi" in sablon:
        return bool(sablon["gece_vardiyasi"]), False
    return _gece_penceresinde(sablon, 0), True


def _gece_penceresinde(sablon, gun, pencere=(20, 30)):
    s = set(_dilimler(gun, sablon["bas"], sablon["bit"]))
    p = set(range(_q(gun, pencere[0]), _q(gun, pencere[1])))
    return bool(s & p)


# ----------------------------------------------------------------------
# Girdi okuma
# ----------------------------------------------------------------------

def _kural(girdi, kod):
    for k in girdi.get("kurallar", []) or []:
        if k.get("kod") == kod and k.get("aktif", True):
            return k
    return None


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
        self.yemek_dk = {t["id"]: self._yemek_dk_sec(t) for t in self.sablonlar}
        self.dinlenme_tanim = {t["id"]: self._dinlenme_sec(t) for t in self.sablonlar}
        self.dinlenme = {}   # (e,d,t,i,s) -> BoolVar

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
        self._asgari_vardiya()
        self._kapsama()
        self._yetkinlik()
        self._amac()
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

    def _X(self, kimlik, gun, sablon_id):
        """x degiskeni; kisi o sablona atanamiyorsa SABIT SIFIR.

        Boylece cagiran taraflarin dongulerini degistirmek gerekmez:
        olmayan degisken aritmetikte zaten sifirdir.
        """
        return self.x.get((kimlik, gun, sablon_id), 0)

    def _degiskenler(self):
        for c in self.calisanlar:
            for d in self.gunler:
                for t in self._sablonlari(c):
                    v = self.m.NewBoolVar("x_%s_%d_%s" % (c["id"], d, t["id"]))
                    self.x[(c["id"], d, t["id"])] = v
                    yemek_dk = self.yemek_dk[t["id"]]
                    yemekler = _mola_baslangiclari(t, self.mola_penceresi, yemek_dk)
                    for s in yemekler:
                        self.mola[(c["id"], d, t["id"], s)] = self.m.NewBoolVar(
                            "m_%s_%d_%s_%s" % (c["id"], d, t["id"], s))
                    # Vardiya secildiyse TAM BIR mola yerlesimi secilir.
                    self.m.Add(sum(self.mola[(c["id"], d, t["id"], s)]
                                   for s in yemekler) == v)
                    self._dinlenme_degiskenleri(c, d, t, v, yemekler, yemek_dk)

    def _dinlenme_degiskenleri(self, c, d, t, v, yemekler, yemek_dk):
        """Ucretli kisa molalarin degiskenleri ve kisitlari -- K-32.

        NEDEN KARAR DEGISKENI
          Molalar sabit yerlestirilseydi ayni sablondaki HERKES ayni dakikada
          molaya cikardi ve kapsama coker; "adil plan" tam bunun tersi. Her
          molaya IKI aday verilir, cozucu kisileri kaydirir.

        NEDEN MODEL BUYUMUYOR
          Aday pencereleri ESIT DAGITIMDAN geliyor ve birbirini kesmiyor
          (_dinlenme_baslangiclari). Bu yuzden dinlenme molalari arasinda
          cakismama kisiti YAZILMIYOR -- yalniz YEMEKLE cakismama yaziliyor.

        SIGMAYAN MOLA
          Aday listesi bosalirsa mola URETILMEZ ve `notlar`a yazilir. Olmayan
          yere mola koymak, yasanmamis molayi varmis gibi gostermek olurdu
          (T-27'nin ayni sinifi). Eksikligi dogrulayici MOLA_HAKKI'nda gorur.
        """
        adet, dk = self.dinlenme_tanim[t["id"]]
        if adet <= 0 or dk <= 0:
            return
        for i, adaylar in enumerate(self._dinlenme_adaylari(t)):
            if not adaylar:
                not_ = ("dinlenme molasi %d/%d sablon %s'e sigmadi"
                        % (i + 1, adet, t["id"]))
                if not_ not in self.notlar:
                    self.notlar.append(not_)
                continue
            for s in adaylar:
                self.dinlenme[(c["id"], d, t["id"], i, s)] = self.m.NewBoolVar(
                    "dm_%s_%d_%s_%d_%s" % (c["id"], d, t["id"], i, s))
            self.m.Add(sum(self.dinlenme[(c["id"], d, t["id"], i, s)]
                           for s in adaylar) == v)
            # Dinlenme yemekle CAKISAMAZ. Bu kisit yalniz "adil plan" icin
            # degil, ARITMETIK icin de sart: _sahada "molada olmak" durumunu
            # bir TOPLAM olarak yaziyor; iki mola ayni dilimi kapsarsa toplam
            # ikiye cikar ve sahadaki kisi sayisi eksi degere duser.
            for s in adaylar:
                dil = set(_mola_dilimleri(d, t, s, dk))
                for sy in yemekler:
                    if sy is None:
                        continue
                    if dil & set(_mola_dilimleri(d, t, sy, yemek_dk)):
                        self.m.Add(self.dinlenme[(c["id"], d, t["id"], i, s)]
                                   + self.mola[(c["id"], d, t["id"], sy)] <= 1)

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
                            self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

    def _gunde_tek_vardiya(self):
        """CAKISMA_YOK + gunde tek vardiya.

        Ayni gune tek sablon seciliyor; gece yarisini asan vardiyalar ertesi
        gunun vardiyasiyla cakisabilir -- o _dinlenme() icinde yakalanir.
        """
        for c in self.calisanlar:
            for d in self.gunler:
                self.m.Add(self._calisiyor(c["id"], d) <= 1)

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
                                self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

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
        geceler, tahminler = [], []
        for t in self.sablonlar:
            gece, tahmin = _gece_sablonu(t)
            if gece:
                geceler.append(t)
            if tahmin:
                tahminler.append(t["id"])
        if tahminler:
            self.notlar.append(
                "gece_vardiyasi isareti yok, saat araligindan tahmin edildi: "
                + ", ".join(sorted(tahminler)))
        if not geceler:
            return
        for c in self.calisanlar:
            if not c.get("gece_calisamaz"):
                continue
            for d in self.gunler:
                for t in geceler:
                    if (c["id"], d, t["id"]) in self.x:
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

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
        if not asanlar:
            return
        self.notlar.append(
            "GECE_VARDIYASI_AZAMI: su sablonlarin gece ortusmesi %s saati "
            "asiyor ve istisnasi olmayan calisana verilmeyecek (BRUT olculdu; "
            "penceredeki mola dusulseydi yasal olabilirdi): %s"
            % (azami, ", ".join("%s (%.2f sa)" % (t["id"], b)
                                for t, b in asanlar)))

        istisnali = self.girdi.get("sektor") in GECE_ISTISNA_SEKTORLERI
        for c in self.calisanlar:
            for d in self.gunler:
                if istisnali and _gece_onayi_var(c, self.girdi, d):
                    continue
                for t, _ in asanlar:
                    if (c["id"], d, t["id"]) in self.x:
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

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
                            self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

    def _kilitler(self):
        for k in self.girdi.get("kilitler", []) or []:
            e, d = k.get("calisan"), k.get("gun")
            if k.get("tip") == "yasak":
                if any(c["id"] == e for c in self.calisanlar):
                    self.m.Add(self._calisiyor(e, d) == 0)
            elif "bas" in k and "bit" in k:
                eslesen = [t for t in self.sablonlar
                           if t["bas"] == k["bas"] and t["bit"] == k["bit"]]
                if eslesen:
                    if (e, d, eslesen[0]["id"]) in self.x:
                        self.m.Add(self.x[(e, d, eslesen[0]["id"])] == 1)
                    else:
                        # T-46: kilit, kisinin ekibinde OLMAYAN bir sablona
                        # isaret ediyor. Sessizce `0 == 1` yazip plani
                        # cozumsuz birakmak yanlis cevap olurdu -- sebebi
                        # gorunmezdi. Not birakip geciyoruz.
                        self.notlar.append(
                            "kilit calisanin ekibinde olmayan sablona isaret "
                            "ediyor: %s gun %s sablon %s"
                            % (e, d, eslesen[0]["id"]))
                else:
                    self.notlar.append("kilit sablona eslesmedi: %s gun %s" % (e, d))
            else:
                self.notlar.append("kilit bicimi taninmadi: %r" % sorted(k))

    def _sabit_atamalar(self):
        for a in self.girdi.get("sabit_atamalar", []) or []:
            anahtar = (a["calisan"], a["gun"], a.get("sablon"))
            # Dogrudan sozluk aramasi: eskiden her sabit atama icin butun
            # anahtarlar listeleniyordu (350 kiside 346 bin anahtar).
            if anahtar in self.x:
                self.m.Add(self.x[anahtar] == 1)
            else:
                self.notlar.append("sabit atama modele girmedi: %r" % (anahtar,))

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

        for c in self.calisanlar:
            for d in self.gunler:
                for t in self.sablonlar:
                    if _net_saat(t) > gunluk:
                        if (c["id"], d, t["id"]) in self.x:
                            self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

            # Dakika cinsinden tam sayi calisilir; float kisit CP-SAT'e girmez.
            dakika = sum(int(round(_net_saat(t) * 60)) * self._X(c["id"], d, t["id"])
                         for d in self.gunler for t in self._sablonlari(c))

            # K-38 -- HAFTALIK_AZAMI *NORMAL CALISMA* SINIRIDIR, TOPLAM TAVAN DEGIL
            #
            # ⚠ NE VARDI (29 Eylul'e kadar)
            #     self.m.Add(dakika <= int(haftalik * 60))       # 45 saat
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
            self.m.Add(dakika <= int((haftalik + (fm_tavan if fm_kural else 0)) * 60))

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
                self.m.Add(dakika <= int(pt_tavan * 60))
            elif tavan is not None:
                self.m.Add(dakika <= int((tavan + (fm_tavan if fm_kural else 0)) * 60))
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
                self.m.Add(fazla >= dakika - int(tavan * 60))
                self.cezalar.append((50, fazla))

    def _dinlenme(self):
        """VARDIYA_ARASI_DINLENME -- ardisik gunlerdeki her sablon cifti.

        Cakisan cift de burada yakalanir: ara negatif olur, esigin altindadir.
        """
        asgari = _par(_kural(self.girdi, "VARDIYA_ARASI_DINLENME"), "asgari_saat", 11)
        for c in self.calisanlar:
            for d in self.gunler[:-1]:
                for t1 in self.sablonlar:
                    bitis = d * 24 + t1["bit"]
                    for t2 in self.sablonlar:
                        baslangic = (d + 1) * 24 + t2["bas"]
                        if baslangic - bitis < asgari:
                            self.m.Add(self._X(c["id"], d, t1["id"])
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
                self.m.Add(sum(self._calisiyor(c["id"], d)
                               for d in range(bas, bas + azami + 1)) <= azami)

    def _ardisik_gece(self):
        """ARDISIK_GECE_LIMIT -- ust uste azami gece (firma kurali, SERT).

        Kayan pencere: her `azami+1` gunluk dilimde en fazla `azami` gece.
        `_ardisik_gun` ile ayni kalip.

        GECE = K-40'in tespiti (`_gece_sablonu`): isaret varsa o, yoksa
        saat araligi. Dogrulayicida ayni tespit AYRI yazili (#7.6).

        ⚠ YALNIZ PLAN HAFTASI (T-28): gecen haftanin son geceleri
          gorulmuyor. Pazartesi baslayan seri, pazar gecesinin devami
          olabilir -- motor bunu bilemez.
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
                    self.m.Add(sum(terim) <= azami)

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
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

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

    def _atanmis(self, ekip, gun, saat):
        """O hucreye ATANMIS kisiler -- mola DUSULMEZ (ASGARI/HEDEF_KAPSAMA)."""
        dilim = _q(gun, saat)
        return [self._X(c["id"], d, t["id"])
                for c in self.calisanlar
                if ekip in (c.get("ekipler") or [])
                for d in self.gunler
                for t in self._sablonlari(c)
                if dilim in _dilimler(d, t["bas"], t["bit"])]

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
        """
        dilim = _q(gun, saat)
        cikan = []
        for c in self.calisanlar:
            if ekip not in (c.get("ekipler") or []):
                continue
            for d in self.gunler:
                for t in self._sablonlari(c):
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
        # SAHADA_ASGARI (K-33): firmanin "sahada en az N kisi" cumlesi.
        # Talep tablosunun `asgari`si ile SINIRLANMAZ -- ikisi ayri sey
        # soyler, ikisi de SERT, kati olan baglar. Ayrintisi ve bir kez
        # yapilan min(...) hatasinin kaydi kurallar.py::sahada_asgari'de.
        taban_kisi = _par(_kural(self.girdi, "SAHADA_ASGARI"),
                          "asgari_sahada", 0)

        for t, gun, saat in self._hucreler():
            atanmis = self._atanmis(t.get("ekip"), gun, saat)
            if asgari_kural and t.get("asgari"):
                self.m.Add(sum(atanmis) >= t["asgari"])
            if hedef_kural and t.get("hedef"):
                eksik = self.m.NewIntVar(0, t["hedef"], "he_%d_%d" % (gun, saat))
                self.m.Add(eksik >= t["hedef"] - sum(atanmis))
                self.cezalar.append((hedef_agirlik, eksik))
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
                    self.m.Add(eksik >= t["asgari"]
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
                    self.m.Add(sum(self._sahada(t.get("ekip"), gun, an))
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

        ⚠ COK EKIPLI CALISAN -- T-21'in kapsami, burada COZULMEDI.
          Bu govde kisiyi `ekipler` uyeligine gore suzuyor (`_atanmis` ile
          ayni gelenek). Cikti tarafinda atamanin `ekip` alani kisinin
          ILK ekibi olarak yaziliyor (coz.py), yani cok ekipli bir kiside
          iki taraf ayrisabilir. Bugunku veri setinde 500 calisanin
          hepsi TEK ekipte, yani ayrisma teorik. Karar T-21'de bekliyor.
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
                    var = [self._X(c["id"], d, t["id"])
                           for c in uygun
                           for d in self.gunler
                           for t in self._sablonlari(c)
                           if dilim in _dilimler(d, t["bas"], t["bit"])]
                    self.m.Add(sum(var) >= asgari)

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
                    self.m.Add(y >= sayim[c["id"]] - j)
                    self.cezalar.append((agirlik, y))

    def _boyut_sayaci(self, boyut):
        if boyut == "gece":
            return lambda t, d: _gece_sablonu(t)[0]
        if boyut == "hafta_sonu":
            return lambda t, d: d in (5, 6)
        if boyut == "cumartesi":
            return lambda t, d: d == 5
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
                self.m.Add(dakika >= gereken_dk)
            else:
                sapma = self.m.NewIntVar(0, 100000, "sd_%s" % c["id"])
                self.m.Add(sapma >= gereken_dk - dakika)
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
