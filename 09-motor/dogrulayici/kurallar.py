# -*- coding: utf-8 -*-
"""
KURAL GOVDELERI -- Master Spec v1.4 #6

NE YAPAR
  Katalogdaki her kuralin "bu plan bu kurali cigniyor mu" govdesi. Her kural
  bir fonksiyondur, ihlal listesi dondurur.

BU BAGIMSIZ DOGRULAYICIDIR -- #7.6 ve #16.1
  Kurallar SARTNAMEDEN okunarak yeniden yazildi. Cozucunun kisit kodunu
  cagirmaz, onunla hicbir yardimci fonksiyon paylasmaz. Sebep D-6 sinifi
  hata: kodu yazan testi de yazarsa ayni yanlis varsayim iki yere birden
  gecer ve hicbir test yakalamaz.

  Bu yuzden buradaki kod bilerek "aptal" ve dogrudan: her kural kendi
  sayimini kendi yapar, optimizasyon yok.

HENUZ YAZILMAYANLAR
  Katalogdaki 35 kuralin hepsi degil, su an gereken alt kume yazildi.
  KAYIT sozlugunde olmayan bir kural girdide aktif ise, denetle.py bunu
  SESSIZCE GECMEZ -- `uygulanmayan_kurallar` listesinde bildirir.
"""

from . import zaman

KAYIT = {}


def kural(kod):
    def sar(fn):
        KAYIT[kod] = fn
        return fn
    return sar


# ----------------------------------------------------------------------
# Yardimcilar -- yalniz bu dosyada kullanilir
# ----------------------------------------------------------------------

def _kisiye_gore(atamalar):
    g = {}
    for a in atamalar:
        g.setdefault(a["calisan"], []).append(a)
    for liste in g.values():
        liste.sort(key=lambda a: zaman.aralik(a)[0])
    return g


def _calisan(girdi, kimlik):
    for c in girdi.get("calisanlar", []):
        if c["id"] == kimlik:
            return c
    return None


def _p(tanim, ad, varsayilan):
    return (tanim.get("parametreler") or {}).get(ad, varsayilan)


def _ihlal(kod, tanim, **alanlar):
    d = {
        "kural": kod,
        "agirlik": tanim.get("tur", "SERT"),
        "yasal": tanim.get("yasal", False),
        "kabul_edilebilir": tanim.get("kabul_edilebilir", False),
        "calisan": None, "ekip": None, "gun": None, "saat": None,
    }
    d.update(alanlar)
    return d


# ----------------------------------------------------------------------
# 6.1 Uygunluk
# ----------------------------------------------------------------------

@kural("AKTIF_CALISAN")
def aktif_calisan(girdi, atamalar, tanim):
    cikan = []
    for a in atamalar:
        c = _calisan(girdi, a["calisan"])
        if c is None:
            cikan.append(_ihlal("AKTIF_CALISAN", tanim, calisan=a["calisan"],
                                gun=a["gun"],
                                mesaj="%s kadroda yok" % a["calisan"]))
        elif c.get("durum", "aktif") != "aktif":
            cikan.append(_ihlal("AKTIF_CALISAN", tanim, calisan=a["calisan"],
                                gun=a["gun"],
                                mesaj="%s aktif degil (%s)" % (a["calisan"], c.get("durum"))))
    return cikan


@kural("ONAYLI_IZIN")
def onayli_izin(girdi, atamalar, tanim):
    cikan = []
    for a in atamalar:
        c = _calisan(girdi, a["calisan"]) or {}
        bas, bit = zaman.aralik(a)
        for izin in c.get("izinler", []):
            if izin.get("durum", "onayli") != "onayli":
                continue          # #8.3: yalniz onayli izinler motoru baglar
            # Gece vardiyasi iki gune dokunur; ikisinde de izin varsa ihlal.
            for gun in range(a["gun"], (bit - 1) // 24 + 1):
                if izin.get("gun") == gun:
                    cikan.append(_ihlal("ONAYLI_IZIN", tanim,
                                        calisan=a["calisan"], gun=gun,
                                        mesaj="%s gun %d'de onayli izinli" % (a["calisan"], gun)))
                    break
    return cikan


@kural("SOZLESME_GECERLI")
def sozlesme_gecerli(girdi, atamalar, tanim):
    """Sozlesme bitisinden sonraki gune atama yapilamaz.

    Sozlesmede tarih alani yoksa bu kural SESSIZ GECER -- ama bu bir
    atlama degil: tarihsiz sozlesme 'suresiz' demektir (#8.3), yani
    ihlal edilemez. Tarih varsa denetlenir.
    """
    hafta_bas = girdi.get("hafta_baslangic")
    if not hafta_bas:
        return []
    from datetime import date, timedelta
    try:
        y, ay, g = (int(x) for x in str(hafta_bas).split("-"))
        pazartesi = date(y, ay, g)
    except (ValueError, TypeError):
        return []
    cikan = []
    for a in atamalar:
        c = _calisan(girdi, a["calisan"]) or {}
        soz = c.get("sozlesme") or {}
        bitis = soz.get("bitis")
        if not bitis:
            continue
        try:
            y, ay, g = (int(x) for x in str(bitis).split("-"))
            son = date(y, ay, g)
        except (ValueError, TypeError):
            continue
        gun_tarihi = pazartesi + timedelta(days=a["gun"])
        if gun_tarihi > son:
            cikan.append(_ihlal("SOZLESME_GECERLI", tanim, calisan=a["calisan"],
                                gun=a["gun"],
                                mesaj="%s'in sozlesmesi %s'te bitiyor, gun %d ondan sonra"
                                      % (a["calisan"], bitis, a["gun"])))
    return cikan


@kural("UYGUNLUK_TAKVIMI")
def uygunluk_takvimi(girdi, atamalar, tanim):
    cikan = []
    for a in atamalar:
        c = _calisan(girdi, a["calisan"]) or {}
        for u in c.get("uygunluk", []):
            if u.get("tip") != "uygun_degil":
                continue
            sahte = {"gun": u["gun"], "bas": u["bas"], "bit": u["bit"]}
            if zaman.ortusuyor_mu(a, sahte):
                cikan.append(_ihlal("UYGUNLUK_TAKVIMI", tanim,
                                    calisan=a["calisan"], gun=a["gun"],
                                    mesaj="%s gun %d %s-%s araliginda uygun degil"
                                          % (a["calisan"], u["gun"], u["bas"], u["bit"])))
                break
    return cikan


# ----------------------------------------------------------------------
# 6.2 Sure ve dinlenme
# ----------------------------------------------------------------------

@kural("GUNLUK_AZAMI")
def gunluk_azami(girdi, atamalar, tanim):
    sinir = _p(tanim, "azami_saat", 11)       # #6.2 K-18: kanunun degeri
    toplam = {}
    for a in atamalar:
        toplam.setdefault((a["calisan"], a["gun"]), 0.0)
        toplam[(a["calisan"], a["gun"])] += zaman.net_saat(a)
    return [_ihlal("GUNLUK_AZAMI", tanim, calisan=k, gun=g,
                   olculen=v, gereken=sinir,
                   mesaj="%s gun %d'de %.1f saat net calisiyor (azami %s)" % (k, g, v, sinir))
            for (k, g), v in sorted(toplam.items()) if v > sinir]


@kural("HAFTALIK_AZAMI")
def haftalik_azami(girdi, atamalar, tanim):
    sinir = _p(tanim, "azami_saat", 45)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    return [_ihlal("HAFTALIK_AZAMI", tanim, calisan=k, olculen=v, gereken=sinir,
                   mesaj="%s haftada %.1f saat net calisiyor (azami %s)" % (k, v, sinir))
            for k, v in sorted(toplam.items()) if v > sinir]


@kural("PART_TIME_LIMIT")
def part_time_limit(girdi, atamalar, tanim):
    """Fazla Calisma Yon. md. 8 -- kismi sureliye fazla surelerle calisma da
    yaptirilamaz. Bu yuzden tolerans 0 (K-25 arastirmasi)."""
    tolerans = _p(tanim, "tolerans_saat", 0)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    cikan = []
    for kimlik, saat in sorted(toplam.items()):
        c = _calisan(girdi, kimlik) or {}
        soz = c.get("sozlesme") or {}
        if soz.get("tip") != "yari_zamanli":
            continue
        tavan = soz.get("haftalik_saat", 0) + tolerans
        if saat > tavan:
            cikan.append(_ihlal("PART_TIME_LIMIT", tanim, calisan=kimlik,
                                olculen=saat, gereken=tavan,
                                mesaj="%s yari zamanli, sozlesmesi %s saat; %.1f saat verilmis"
                                      % (kimlik, soz.get("haftalik_saat"), saat)))
    return cikan


@kural("CAKISMA_YOK")
def cakisma_yok(girdi, atamalar, tanim):
    """Z-3: mutlak zamanda olculur, gun sinirini asan vardiyalar dahil."""
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):
        for i in range(len(liste)):
            for j in range(i + 1, len(liste)):
                ort = zaman.ortusme(liste[i], liste[j])
                if ort > 0:
                    cikan.append(_ihlal("CAKISMA_YOK", tanim, calisan=kimlik,
                                        gun=liste[j]["gun"], olculen=ort,
                                        mesaj="%s'in iki vardiyasi %s saat cakisiyor"
                                              % (kimlik, ort)))
    return cikan


@kural("VARDIYA_ARASI_DINLENME")
def vardiya_arasi_dinlenme(girdi, atamalar, tanim):
    """Postalar Yon. md. 9 -- en az 11 saat kesintisiz.

    K-11: 'asgari 11 saat' 11'i KAPSAR. Tam 11 saat ihlal DEGILDIR.
    V-1 : Iki vardiya ORTUSUYORSA yalniz CAKISMA_YOK yazilir, ayrica
          dinlenme ihlali yazilmaz -- ayni olay iki kez raporlanmaz.
    """
    asgari = _p(tanim, "asgari_saat", 11)
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):
        for onceki, sonraki in zip(liste, liste[1:]):
            if zaman.ortusuyor_mu(onceki, sonraki):
                continue                      # V-1
            ara = zaman.ara_saat(onceki, sonraki)
            if ara < asgari:                  # K-11: '<' , '<=' degil
                cikan.append(_ihlal("VARDIYA_ARASI_DINLENME", tanim,
                                    calisan=kimlik, gun=sonraki["gun"],
                                    olculen=ara, gereken=asgari,
                                    mesaj="%s iki vardiya arasi %s saat dinlenmis (en az %s)"
                                          % (kimlik, ara, asgari)))
    return cikan


@kural("HAFTA_TATILI")
def hafta_tatili(girdi, atamalar, tanim):
    """Is K. md. 46 -- yedi gunluk KAYAN pencerede kesintisiz 24 saat.

    T-11: pencere kayan. Her gun icin ayri ayri bakilir; hafta basina gore
    tek sefer bakilmaz. Y.22.HD 2019/1727: hafta tatili toplu kullandirilamaz.

    Basitlestirme -- BILEREK: gun bazinda calisildi/calisilmadi bakilir.
    Gercek 24 saatlik kesintisiz blok hesabi lookback penceresi gerektiriyor
    (#11.2) ve haftalik plan tek basina yetmiyor. Bu yaklasim, tam bir gun
    bos olmayan pencereyi yakalar -- daha gevsek, yanlis alarm uretmez.
    """
    pencere = _p(tanim, "pencere_gun", 7)
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):
        dolu = zaman.calisilan_gunler(liste)
        gunler = sorted(dolu)
        if not gunler:
            continue
        for bas in range(min(gunler), max(gunler) - pencere + 2):
            dilim = set(range(bas, bas + pencere))
            if dilim <= dolu:
                cikan.append(_ihlal("HAFTA_TATILI", tanim, calisan=kimlik,
                                    gun=bas, olculen=0, gereken=24,
                                    mesaj="%s gun %d-%d arasi hic dinlenme gunu yok"
                                          % (kimlik, bas, bas + pencere - 1)))
                break
    return cikan


@kural("ARDISIK_CALISMA_GUNU")
def ardisik_calisma_gunu(girdi, atamalar, tanim):
    sinir = _p(tanim, "azami_gun", 6)
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):
        dolu = zaman.calisilan_gunler(liste)
        if not dolu:
            continue
        seri = en_uzun = 0
        basladi = None
        for g in range(min(dolu), max(dolu) + 1):
            if g in dolu:
                if seri == 0:
                    basladi = g
                seri += 1
                if seri > en_uzun:
                    en_uzun, en_uzun_bas = seri, basladi
            else:
                seri = 0
        if en_uzun > sinir:
            cikan.append(_ihlal("ARDISIK_CALISMA_GUNU", tanim, calisan=kimlik,
                                gun=en_uzun_bas, olculen=en_uzun, gereken=sinir,
                                mesaj="%s %d gun ust uste calisiyor (azami %s)"
                                      % (kimlik, en_uzun, sinir)))
    return cikan


# Is K. md. 68 -- BRUT sureye uygulanir (K-4, hukuk teyidi bekliyor: A-16)
MOLA_TABLOSU = ((4, 15), (7.5, 30), (float("inf"), 60))


@kural("MOLA_HAKKI")
def mola_hakki(girdi, atamalar, tanim):
    esikler = _p(tanim, "esikler", None)
    tablo = tuple((float(e["ustsinir_saat"]), e["mola_dk"]) for e in esikler) \
        if esikler else MOLA_TABLOSU
    cikan = []
    for a in atamalar:
        brut = zaman.brut_saat(a)
        gereken = next(dk for ust, dk in tablo if brut <= ust)
        verilen = zaman.mola_saat(a) * 60
        if verilen + 1e-9 < gereken:
            cikan.append(_ihlal("MOLA_HAKKI", tanim, calisan=a["calisan"],
                                gun=a["gun"], olculen=verilen, gereken=gereken,
                                mesaj="%s gun %d: %s saatlik vardiyada %.0f dk mola verilmis (en az %d dk)"
                                      % (a["calisan"], a["gun"], brut, verilen, gereken)))
    return cikan


# ----------------------------------------------------------------------
# 6.4 Kapsama
# ----------------------------------------------------------------------

def _talep_hucreleri(girdi):
    for t in girdi.get("talep", []) or []:
        for gun in t.get("gunler", []):
            for saat in t.get("saatler", []):
                yield t, gun, saat


@kural("ASGARI_KAPSAMA")
def asgari_kapsama(girdi, atamalar, tanim):
    """Atanmis kisi sayisina bakar -- MOLA DUSULMEZ.

    Molayi dusen kural MOLA_KAPSAMASI'dir ve o YUMUSAK'tir (K-14). Ikisi
    bilerek ayri: biri 'yeterli kisi planlandi mi', digeri 'o an sahada
    kac kisi var'.
    """
    cikan = []
    for t, gun, saat in _talep_hucreleri(girdi):
        asgari = t.get("asgari", 0)
        sayi = sum(1 for a in atamalar
                   if a.get("ekip") == t.get("ekip")
                   and zaman.atanmis_mi(a, gun, saat))
        if sayi < asgari:
            cikan.append(_ihlal("ASGARI_KAPSAMA", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, olculen=sayi, gereken=asgari,
                                mesaj="gun %d saat %d: %d kisi atanmis (asgari %d)"
                                      % (gun, saat, sayi, asgari)))
    return cikan


@kural("HEDEF_KAPSAMA")
def hedef_kapsama(girdi, atamalar, tanim):
    cikan = []
    for t, gun, saat in _talep_hucreleri(girdi):
        hedef = t.get("hedef")
        if hedef is None:
            continue
        sayi = sum(1 for a in atamalar
                   if a.get("ekip") == t.get("ekip")
                   and zaman.atanmis_mi(a, gun, saat))
        if sayi < hedef:
            cikan.append(_ihlal("HEDEF_KAPSAMA", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, olculen=sayi, gereken=hedef,
                                mesaj="gun %d saat %d: %d kisi (hedef %d)"
                                      % (gun, saat, sayi, hedef)))
    return cikan


@kural("MOLA_KAPSAMASI")
def mola_kapsamasi(girdi, atamalar, tanim):
    """YUMUSAK (K-14). Mola DUSULDUKTEN sonra sahadaki kisi asgarinin
    altina inerse puan duser -- plan gecersiz OLMAZ."""
    cikan = []
    for t, gun, saat in _talep_hucreleri(girdi):
        asgari = t.get("asgari", 0)
        sahada = sum(1 for a in atamalar
                     if a.get("ekip") == t.get("ekip")
                     and zaman.sahada_mi(a, gun, saat))
        if sahada < asgari:
            cikan.append(_ihlal("MOLA_KAPSAMASI", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, sahada=sahada, asgari=asgari,
                                olculen=sahada, gereken=asgari,
                                mesaj="gun %d saat %d: molalar dusulunce sahada %d kisi kaliyor (asgari %d)"
                                      % (gun, saat, sahada, asgari)))
    return cikan


# ----------------------------------------------------------------------
# 6.6 Duzenleme
# ----------------------------------------------------------------------

@kural("KILIT_UYUMU")
def kilit_uyumu(girdi, atamalar, tanim):
    def anahtar(a):
        return (a["calisan"], a.get("ekip"), a["gun"], a["bas"], a["bit"])
    var = {anahtar(a) for a in atamalar}
    return [_ihlal("KILIT_UYUMU", tanim, calisan=k["calisan"], gun=k["gun"],
                   mesaj="kilitli atama planda yok: %s gun %d" % (k["calisan"], k["gun"]))
            for k in girdi.get("kilitler", []) or [] if anahtar(k) not in var]


@kural("DONMUS_GUN")
def donmus_gun(girdi, atamalar, tanim):
    donmus = set(girdi.get("donmus_gunler", []) or [])
    return [_ihlal("DONMUS_GUN", tanim, calisan=a["calisan"], gun=a["gun"],
                   mesaj="gun %d donmus, degistirilemez" % a["gun"])
            for a in atamalar if a["gun"] in donmus and a.get("_yeni")]


# ----------------------------------------------------------------------
# 6.7 Fazla mesai
# ----------------------------------------------------------------------

@kural("FAZLA_MESAI_TAVANI")
def fazla_mesai_tavani(girdi, atamalar, tanim):
    tavan = _p(tanim, "azami_saat_hafta", 10)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    cikan = []
    for kimlik, saat in sorted(toplam.items()):
        c = _calisan(girdi, kimlik) or {}
        soz = (c.get("sozlesme") or {}).get("haftalik_saat")
        if soz is None:
            continue
        fazla = saat - soz
        if fazla > tavan:
            cikan.append(_ihlal("FAZLA_MESAI_TAVANI", tanim, calisan=kimlik,
                                olculen=fazla, gereken=tavan,
                                mesaj="%s %.1f saat fazla mesai (tavan %s)" % (kimlik, fazla, tavan)))
    return cikan


# ----------------------------------------------------------------------
# 6.5 Adalet -- K-27 (16 Eylul 2026)
# ----------------------------------------------------------------------

# Hangi vardiya "gece" sayilir. #6.3 GECE_VARDIYASI_AZAMI penceresiyle AYNI
# tanim kullanilir: genisletilmis saatle 20 -> 30 (20:00 - ertesi gun 06:00).
GECE_PENCERESI = (20, 30)


def _gece_mi(a, pencere=GECE_PENCERESI):
    """Vardiyanin herhangi bir parcasi gece penceresine dusuyor mu."""
    bas, bit = zaman.aralik(a)
    gun = a["gun"]
    for kaydirma in (-24, 0, 24):
        p_bas = zaman.mutlak(gun, pencere[0]) + kaydirma
        p_bit = zaman.mutlak(gun, pencere[1]) + kaydirma
        if min(bit, p_bit) - max(bas, p_bas) > 0:
            return True
    return False


def _boyut_sayaci(boyut):
    """Bir boyutun 'bu atama sayilir mi' olcusu. Sayilamayan boyut -> None."""
    if boyut == "gece":
        return _gece_mi
    if boyut == "hafta_sonu":
        return lambda a: a["gun"] in (5, 6)
    if boyut == "cumartesi":
        return lambda a: a["gun"] == 5
    return None          # 'saat' sayilabilir bir boyut degil -- asagiya bak


@kural("ADALET_DENGESI")
def adalet_dengesi(girdi, atamalar, tanim):
    """Yuk calisanlar arasinda dengeli dagilsin. YUMUSAK.

    K-27 (Mustafa, 16 Eylul): olcu ORTALAMADAN SAPMA'dir.

      > "Bazi kisilerin zaman zaman digerlerinden 1 gun fazla calismasi
      >  gerekebilir ama ortalamadan 2 gece fazla calisiyorsa bu
      >  adaletsizliktir."

    Bu yuzden esik 2 ve karsilastirma `>=`: sapma 1 SORUN DEGIL, 2 ihlaldir.

    DIKKAT -- K-11 ile karistirmayin. Orada 'asgari 11 saat' 11'i KAPSAR (ihlal
    degil), burada 'esik 2' 2'yi KAPSAMAZ (ihlaldir). Ikisi ayri cumleler:
    biri bir TABAN, digeri bir SAPMA TAVANI. Mustafa'nin cumlesi acik --
    "2 gece fazla calisiyorsa adaletsizliktir".

    TEK YONLU: yalniz ortalamanin USTU sayilir. Altta kalan biri varsa, bu
    zaten ustte kalan birini uretir (ortalama sabittir) ve o yakalanir.
    Iki yonlu saymak ayni olayi iki kez raporlardi.

    DEVIR YUKU dahildir: adalet penceresi takvim ayidir (#6.5), plan haftasi
    degil. Ayin ilk haftasinda kimse gece calismamissa sapma sifirdir; ucuncu
    haftada gecmis yuk belirleyicidir.
    """
    esik = _p(tanim, "adaletsizlik_esigi", 2)
    boyutlar = _p(tanim, "boyutlar", ["gece", "hafta_sonu", "saat"])
    kisiler = [c["id"] for c in girdi.get("calisanlar", [])]
    if not kisiler:
        return []

    cikan = []
    for boyut in boyutlar:
        sayac = _boyut_sayaci(boyut)
        if sayac is None:
            continue          # 'saat' -- bkz. asagidaki not
        yuk = {}
        for kimlik in kisiler:
            devir = (next((c for c in girdi["calisanlar"] if c["id"] == kimlik), {})
                     .get("devir_yuk") or {}).get(boyut, 0)
            bu_hafta = sum(1 for a in atamalar if a["calisan"] == kimlik and sayac(a))
            yuk[kimlik] = devir + bu_hafta
        ortalama = sum(yuk.values()) / float(len(yuk))
        for kimlik in sorted(yuk):
            sapma = yuk[kimlik] - ortalama
            if sapma >= esik:
                cikan.append(_ihlal("ADALET_DENGESI", tanim, calisan=kimlik,
                                    boyut=boyut, olculen=round(sapma, 2),
                                    gereken=esik,
                                    mesaj="%s bu ay ortalamadan %.1f %s fazla calisiyor (esik %s)"
                                          % (kimlik, sapma, boyut, esik)))
    return cikan


# 'saat' BOYUTU YAZILMADI -- ve bu ayri bir eksik, T-12 degil.
#
# K-27 esigi SAYI olarak verdi: "ortalamadan 2 gece fazla". 'saat' boyutu
# sayilabilir bir sey degil, suredir; "ortalamadan 2 saat fazla" bambaska
# bir buyukluk ve Mustafa onu soylemedi.
#
# Ayrica SAAT_DENGESI zaten saat dengesine bakiyor (tolerans +-2 saat).
# Ikisinin ayni seyi mi olctugu, oluyorsa hangisinin kalacagi acik.
#
# Sayi boyutlari (gece, hafta_sonu, cumartesi) K-27 ile calisiyor.
# 'saat' boyutu sessizce atlanmaz: denetle.py onu eksik_boyutlar'da bildirir.
#
# Kaydedildi: T-13.
