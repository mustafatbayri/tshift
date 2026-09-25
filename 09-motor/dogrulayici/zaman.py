# -*- coding: utf-8 -*-
"""
ZAMAN MODELI -- Master Spec v1.4 #6.3 (Z-1 ... Z-6)

NE YAPAR
  Vardiya sureleri ve cakisma hesaplarinin TEK kaynagi. Sartnamedeki alti
  zaman kurali burada, baska hicbir yerde uygulanmaz.

NEDEN AYRI DOSYA
  Gercek musteri verisinde 182 atama gece yarisini asiyor. Bu bir kenar durum
  degil, olagan isleyis. Ayni aritmetigi birden cok yere yazmak, birini
  duzeltip digerini unutmak demektir.

SAAT GOSTERIMI
  Genisletilmis saat: 25 = ertesi gun 01:00. Vardiya `gun` + `bas` + `bit`
  ile verilir; `bit <= bas` ise ertesi gune tasar (Z-1).

  Ornek: gun 1, 16 -> 25  =  Pazartesi 16:00 - Sali 01:00, 9 saat.
"""


def mutlak(gun, saat):
    """Gun + genisletilmis saat -> hafta basindan itibaren mutlak saat.

    Z-6: sure hesaplari MUTLAK zamanda yapilir. gun -1 (onceki Pazar)
    negatif deger uretir; bu dogrudur, lookback penceresi icin gerekir.
    """
    return gun * 24 + saat


def aralik(atama):
    """Atamanin mutlak (baslangic, bitis) araligi. Z-1 burada uygulanir."""
    bas = mutlak(atama["gun"], atama["bas"])
    bit = mutlak(atama["gun"], atama["bit"])
    if bit <= bas:
        # Z-1: bitis baslangictan kucuk veya esitse ertesi gune tasar.
        # (Genisletilmis saat kullanildiysa bit zaten > bas olur; bu dal
        #  '16 -> 1' gibi ham yazimlar icin guvenlik agi.)
        bit += 24
    return bas, bit


def mola_araliklari(atama, tip=None):
    """Molalarin mutlak araliklari -- VARDIYANIN ICINE KIRPILMIS.

    T-27 (16 Eylul dis incelemesi): burasi eskiden molayi, vardiyanin
    icinde olup olmadigina BAKMADAN donduruyordu. 08:00-20:00 vardiyaya
    yazilmis 22:00-23:00 molasi net sureden dusuluyor, boylece YASAL
    gunluk sinir (K-18) sessizce deviriliyordu. Hata yonu tek tarafli ve
    yanlis tarafa: bozuk girdi motoru daha GEVSEK yapiyordu.

    Iki islem var, sirasi onemli:

      1. KAYDIRMA   -- gece yarisini asan vardiyada mola ham saatle
         yazilmis olabilir ("00:30"). Vardiya 16->25 ise mola gun+1'e
         aittir; 24 saat ileri kaydirilir. Z-1'in mola karsiligi.
      2. KIRPMA     -- kalan aralik vardiyayla KESISTIRILIR. Disarida
         kalan kisim molanin kendisi degil, veri hatasidir.
      3. BIRLESTIRME -- ust uste binen molalar tek araliga indirilir.
         Kirpma bunu cozmez: iki mola da vardiyanin icinde olabilir ve
         ayni saat iki kez dusulur. 10-12 ile 11-13 UC saattir, dort degil.

    Kismen disarida kalan mola YARI sayilir, sifir degil: 19:30-20:30
    molasinin 30 dakikasi vardiya icindedir ve gercekten kullanilmistir.

    DONEN DEGER ayrik ve sirali araliklardir. `sahada_mi` bundan
    etkilenmez (nokta kumesi ayni), `mola_saat` ise artik dogru toplar.

    TIP SUZGECI (K-32)
      `tip` verilirse yalniz o tipteki molalar toplanir. Birlestirme de
      TIP ICINDE yapilir: ust uste binen iki `yemek` birlesir, ama bir
      `yemek` ile bir `dinlenme` birlesmez -- ikisi ayri kovadir.
    """
    v_bas, v_bit = aralik(atama)
    ham = []
    for m in atama.get("molalar") or []:
        if tip is not None and mola_tipi(m) != tip:
            continue
        b = mutlak(atama["gun"], m["bas"])
        s = mutlak(atama["gun"], m["bit"])
        if s <= b:
            s += 24
        if b < v_bas and b + 24 < v_bit:
            # 1. kaydirma
            b += 24
            s += 24
        # 2. kirpma
        b = max(b, v_bas)
        s = min(s, v_bit)
        if s > b:
            ham.append((b, s))

    # 3. birlestirme -- ucu uca degenler de birlesir (11'de biten ile
    #    11'de baslayan tek bir mola blogudur; sure toplami degismez).
    cikan = []
    for b, s in sorted(ham):
        if cikan and b <= cikan[-1][1]:
            if s > cikan[-1][1]:
                cikan[-1] = (cikan[-1][0], s)
        else:
            cikan.append((b, s))
    return cikan


def brut_saat(atama):
    """Sahada gecen toplam sure -- mola DAHIL."""
    bas, bit = aralik(atama)
    return bit - bas


# ----------------------------------------------------------------------
# Mola tipleri -- K-32 (25 Eylul)
# ----------------------------------------------------------------------
#
# `yemek`    : UCRETSIZ. Calisma suresinden DUSULUR. Tek blok (K-14).
# `dinlenme` : UCRETLI.  Calisma suresinden DUSULMEZ. Is K. md. 68'in yasal
#              hakkini BU karsilar; en az 15'er dakikalik bloklara bolunebilir.
#
# TIPSIZ MOLA NE OLUR
#   `yemek` sayilir -- yani 25 Eylul oncesindeki davranis aynen korunur ve
#   eski girdiler sessizce DEGISMEZ. Ama tipsiz olmasi bir ihlaldir:
#   `MOLA_TIPI_ZORUNLU` bunu bildirir. Varsayilan davranisi korumak susmak
#   degil; susmayi engelleyen ayri bir kural var.

YEMEK = "yemek"
DINLENME = "dinlenme"
VARSAYILAN_MOLA_TIPI = YEMEK


def mola_tipi(mola):
    """Bir mola satirinin tipi. Yazilmamissa VARSAYILAN_MOLA_TIPI."""
    return mola.get("tip") or VARSAYILAN_MOLA_TIPI


def mola_saat(atama, tip=None):
    """Vardiya ICINDE gecen toplam mola suresi.

    Vardiya disina yazilmis mola buraya girmez -- yasanmamis bir molanin
    suresi dusulemez (T-27). Sonucu MOLA_HAKKI'nda da gorulur: disariya
    yazilan mola 'verilmis mola' sayilmaz.

    `tip` verilirse yalniz o tip toplanir (K-32).
    """
    return sum(s - b for b, s in mola_araliklari(atama, tip))


def yemek_saat(atama):
    """Ucretsiz mola suresi -- calisma suresinden DUSULEN kisim (K-32)."""
    return mola_saat(atama, YEMEK)


def dinlenme_saat(atama):
    """Ucretli mola suresi -- calisma suresinden DUSULMEYEN kisim (K-32).

    Is K. md. 68'in yasal hakkini bu karsilar; MOLA_HAKKI buna bakar.
    """
    return mola_saat(atama, DINLENME)


def net_saat(atama):
    """CALISMA SURESI -- butun molalar dusulmus.

    #6.2: GUNLUK_AZAMI ve HAFTALIK_AZAMI NET sureye bakar.
    #6.2 MOLA_HAKKI'nin ESIGI ise BRUT sureye bakar (K-4). Ikisi bilerek
    farkli.

    ⚠ 25 Eylul'de bu satir bir kez YANLIS degistirildi ve geri alindi.
    Degisiklik "dinlenme molasi ucretlidir, o halde calisma suresine
    dahildir" varsayimina dayaniyordu. Varsayim yanlis: bir molanin
    UCRETLI olmasi, o sirada is yapiliyor olmasi demek degildir. Ara
    dinlenme ucretli de olsa calisma suresinden dusulur; ucret tarafi
    AYRI bir buyuktur (bkz. `ucret_saat`). Dordu ayri sayilir:

        brut_saat  : vardiya araligi          9 saat
        net_saat   : calisma suresi (yasal)   butun molalar dusuk
        ucret_saat : ucret hesabina esas      yalniz UCRETSIZ mola dusuk
        (gorev kapasitesi = net_saat; molada kimse sahada sayilmaz)
    """
    return brut_saat(atama) - mola_saat(atama)


def ucret_saat(atama):
    """UCRET HESABINA ESAS sure -- yalniz UCRETSIZ mola dusulmus (K-32).

    `net_saat`ten farki bilerek: ucretli kisa molalar calisma suresinden
    dusulur ama ucretten dusulmez. 09:00-18:00 vardiyada 1 saat yemek ve
    3x15 dk ucretli kisa mola varsa:

        brut  9 saat  ·  calisma 7 saat 15 dk  ·  ucret 8 saat

    Bu bir FIRMA POLITIKASIDIR, yasal varsayilan degil: kisa molanin
    ucretli sayilip sayilmayacagi sozlesmeye ve isyeri uygulamasina
    baglidir. Motor bunu girdiden okur, kendisi varsaymaz.
    """
    return brut_saat(atama) - yemek_saat(atama)


def ortusme(a, b):
    """Iki atamanin mutlak zamanda ortustugu saat sayisi. Z-3.

    Sifir ya da negatifse ortusme yoktur. Ucu uca degen iki vardiya
    (biri 16'da biter, digeri 16'da baslar) ortusmez.
    """
    a1, a2 = aralik(a)
    b1, b2 = aralik(b)
    return min(a2, b2) - max(a1, b1)


def ortusuyor_mu(a, b):
    return ortusme(a, b) > 0


def ara_saat(onceki, sonraki):
    """Iki atama arasindaki kesintisiz dinlenme suresi. Z-4.

    Tasan vardiyanin GERCEK bitisinden olculur:
    16:00-01:00 biten kisi ertesi gun 09:00 baslarsa 8 saat dinlenmistir.
    """
    return aralik(sonraki)[0] - aralik(onceki)[1]


def sahada_mi(atama, gun, saat):
    """Bu kisi, o gun o saat diliminde SAHADA mi (molada degil).

    Kapsama kurallarinin ikisi de bunu kullanir ama farkli bicimde:
      ASGARI_KAPSAMA / HEDEF_KAPSAMA  ->  atanmis mi (mola SAYILIR)
      MOLA_KAPSAMASI                  ->  sahada mi (mola DUSULUR)
    Ayrimi cagiran taraf yapar; bu fonksiyon molayi duser.
    """
    if not atanmis_mi(atama, gun, saat):
        return False
    an = mutlak(gun, saat)
    return not any(b <= an < s for b, s in mola_araliklari(atama))


def atanmis_mi(atama, gun, saat):
    """Bu kisi o gun o saat dilimine ATANMIS mi -- mola dikkate ALINMAZ."""
    an = mutlak(gun, saat)
    bas, bit = aralik(atama)
    return bas <= an < bit


def calisilan_gunler(atamalar):
    """Hangi gunlerde calisildi. Z-2: vardiya BASLADIGI gune sayilir.

    Cumartesi 16:00-01:00 Pazar'a tasar ama CUMARTESI'ye yazilir.
    """
    return {a["gun"] for a in atamalar}
