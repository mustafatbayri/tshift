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


def mola_araliklari(atama):
    """Molalarin mutlak araliklari. Mola vardiyanin gunune gore yazilir."""
    cikan = []
    for m in atama.get("molalar") or []:
        b = mutlak(atama["gun"], m["bas"])
        s = mutlak(atama["gun"], m["bit"])
        if s <= b:
            s += 24
        cikan.append((b, s))
    return cikan


def brut_saat(atama):
    """Sahada gecen toplam sure -- mola DAHIL."""
    bas, bit = aralik(atama)
    return bit - bas


def mola_saat(atama):
    return sum(s - b for b, s in mola_araliklari(atama))


def net_saat(atama):
    """Calisilan sure -- mola DUSULMUS.

    #6.2: GUNLUK_AZAMI ve HAFTALIK_AZAMI NET sureye bakar.
    #6.2 MOLA_HAKKI ise BRUT sureye bakar (K-4). Ikisi bilerek farkli.
    """
    return brut_saat(atama) - mola_saat(atama)


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
