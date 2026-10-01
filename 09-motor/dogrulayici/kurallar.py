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


# ----------------------------------------------------------------------
# Cok ekipli calisan -- K-50 (Mustafa, 1 Ekim)
# ----------------------------------------------------------------------
#
# "Sahada hem satis hem backoffice yapabilen elemanlar var. Bu elemanlar iki
#  yetkinlik grubuna da ait sayilir: o saatte o eleman iki birim elemani icin
#  yer doldurmus sayilir. Gece 12'den sonra backoffice talebi yok denecek
#  kadar azaliyor; oraya bir eleman koymak yerine asil isi satis ama
#  backoffice yetenegi olan bir eleman konuyor ve sorun sahada cozulmus
#  oluyor." -- Mustafa, 1 Ekim
#
# Yani talep sayisi "o yetenekte hazir bulunan kisi" demektir, "o ise
# adanmis beden" degil. Varsayilan sayim bu: `hepsi` -- bir atama, kisinin
# uye oldugu BUTUN ekiplerin kapsamasina sayilir (atamanin `ekip` alani
# vardiyanin ekibidir, sayimi sinirlamaz). Kiraci isterse `tek`: atama
# yalniz vardiyanin ekibine sayilir (ekipsiz sablonda kisinin ilk ekibine).
#
# ⚠ T-21 (16 Eylul dis incelemesi) bunu "modelin inanci yanlis" diye
#   acmisti: cozucu zaten `hepsi` gibi sayiyordu, dogrulayici `tek` gibi.
#   Iki taraf ayni plan hakkinda farkli konusuyordu. Karar cozucuyu degil
#   DOGRULAYICIYI degistirdi; ayrisma kapandi. Gorunurluk: baska ekibin
#   vardiyasiyla kapatilan hucreler `metrikler.baska_ekipten_kapsama`da.

COK_EKIPLI_SAYIM_VARSAYILAN = "hepsi"


def cok_ekipli_sayim(girdi):
    mod = (girdi or {}).get("cok_ekipli_sayim") or COK_EKIPLI_SAYIM_VARSAYILAN
    return mod if mod in ("hepsi", "tek") else COK_EKIPLI_SAYIM_VARSAYILAN


def uyelik_haritasi(girdi):
    """calisan -> ekip kumesi. Kural basina BIR kez kurulur; hucre dongusu
    icinde `_calisan` taramasi 2.500 atama x 415 hucrede milyonlarca olurdu."""
    return {c.get("id"): set(c.get("ekipler") or [])
            for c in (girdi or {}).get("calisanlar", []) or []}


def ekibe_sayilir(atama, ekip, uyelik, mod):
    """Bu atama bu ekibin kapsamasina sayilir mi -- K-50."""
    if ekip is None or atama.get("ekip") == ekip:
        return True
    if mod != "hepsi":
        return False
    return ekip in uyelik.get(atama.get("calisan"), ())


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
            #
            # ⚠ `int(...)` -- 29 Eylul. K-34 ceyrek saat izgarasini
            #   getirdiginden beri vardiya bitisi KESIRLI olabiliyor
            #   (07:00-15:30 gibi) ve bu satir `range()`e float veriyordu:
            #   "TypeError: 'float' object cannot be interpreted as an
            #   integer". Kural, bitisin tam sayi oldugunu VARSAYIYORDU.
            #   Hicbir test kesirli bitis kullanmadigi icin aylarca
            #   gorunmedi; zor veri seti kurulurken ilk cozumde coktu.
            for gun in range(a["gun"], int((bit - 1) // 24) + 1):
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


@kural("YILLIK_FAZLA_MESAI_TAVANI")
def yillik_fazla_mesai_tavani(girdi, atamalar, tanim):
    """Yillik fazla mesai 270 saati gecemez -- Is K. md. 41, Fazla Calisma
    Yon. md. 5. SERT, YASAL, kabul edilemez (K-20).

    NEDEN SIMDI YAZILDI (1 Ekim, K-49)
      Kapi artik "bakamadim"i goruyor: govdesi olmayan yasal bir kural
      yayini ENGELLIYOR (dogru olan bu). Olcum setinde bu kural aktif ve
      govdesizdi; plan yayinlanamaz oldu. Kurali deaktive etmek yerine
      govdesi yazildi.

    OLCU
      Bu haftanin fazla mesaisi = haftalik net calisma - normal sinir
      (HAFTALIK_AZAMI, K-38: 45). Yil ici toplam `calisanlar[].yil_ici_
      fazla_mesai_saat` (takvim yili, bu haftadan onceki). Toplam + bu
      hafta > 270 ise ihlal. Yil ici toplam BILINMIYORSA kontrol atlanir ve
      `gecmis_eksik` bildirir (K-42) -- yillik toplam da bir gecmis veridir.

    Yil ici toplam tek basina 270'i asmis ve bu hafta fazla mesai YOKSA
    ihlal yazilmaz: plan durumu kotulestirmiyor; asim gecmiste olmus.
    """
    azami = _p(tanim, "azami_saat_yil", 270)
    normal = _p(next((k for k in (girdi.get("kurallar") or [])
                      if k.get("kod") == "HAFTALIK_AZAMI"), {}),
                "azami_saat", 45)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    cikan = []
    for kimlik, saat in sorted(toplam.items()):
        c = _calisan(girdi, kimlik) or {}
        yil = c.get("yil_ici_fazla_mesai_saat")
        if yil is None:
            continue                      # K-42: gecmis_eksik bildirir
        fazla = max(0.0, saat - normal)
        if fazla > 0 and float(yil) + fazla > azami + 1e-9:
            cikan.append(_ihlal(
                "YILLIK_FAZLA_MESAI_TAVANI", tanim, calisan=kimlik,
                olculen=round(float(yil) + fazla, 2), gereken=azami,
                mesaj=("%s yil icinde %.1f saat fazla mesai yapmis; bu hafta "
                       "%.1f saat daha veriliyor, toplam %.1f -- yillik tavan "
                       "%s saat (Is K. md. 41)"
                       % (kimlik, float(yil), fazla, float(yil) + fazla, azami))))
    return cikan


# ----------------------------------------------------------------------
# Departman calisma saatleri -- CALISMA_SAATLERI, K-52 (Mustafa, 1 Ekim)
# ----------------------------------------------------------------------
#
# Girdi `departmanlar[]`: {"id", "ekipler": [...], "acik": "7/24" | [
#   {"gunler": [0..6], "bas", "bit"}, ...]}. Pencere `bit` 24'u asabilir.
# Vardiya ACIK sayilir <=> basladigi gunun bir penceresi tamamini kapsar.
# Ekibin saatleri tanimsizsa kontrol YAPILAMAZ: `eksik_boyutlar` bildirir
# (denetlenemedi: True), K-49 kapiya tasir.
#
# ⚠ Cozucuda ayni mantik ayrica yazili (model.departman_acik_mi) -- #7.6.

def departman_saatleri(girdi):
    cikan = {}
    for d in girdi.get("departmanlar", []) or []:
        for e in d.get("ekipler") or []:
            cikan[e] = d.get("acik")
    return cikan


def departman_acik_mi(saatler, ekip, gun, bas, bit):
    """True/False, ya da None (tanimsiz)."""
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


@kural("CALISMA_SAATLERI")
def calisma_saatleri(girdi, atamalar, tanim):
    """Departman kapaliyken atama yapilamaz -- SERT, firma kurali (K-52).

    Olcu: atamanin (bas, bit) araligi, atamanin EKIBININ departmanindaki
    o gunun bir acik penceresine sigiyor mu. Gece yarisini asan vardiya
    genisletilmis saatle (23 -> 31) karsilastirilir; pencere de oyle
    yazilir. Ekibin saatleri tanimsizsa atama ATLANIR (kontrol yapilamadi;
    `eksik_boyutlar` soyler).
    """
    saatler = departman_saatleri(girdi)
    cikan = []
    for a in atamalar:
        ekip = a.get("ekip")
        bas, bit = zaman.aralik(a)
        bas, bit = bas - a["gun"] * 24, bit - a["gun"] * 24
        acik = departman_acik_mi(saatler, ekip, a["gun"], bas, bit)
        if acik is None or acik:
            continue
        cikan.append(_ihlal(
            "CALISMA_SAATLERI", tanim, calisan=a.get("calisan"), ekip=ekip,
            gun=a["gun"], olculen=0, gereken=1,
            mesaj="%s gun %d %s-%s: %s ekibinin departmani bu saatlerde kapali"
                  % (a.get("calisan"), a["gun"], _ss(bas), _ss(bit), ekip)))
    return cikan


@kural("GECE_YARISI_ASAN")
def gece_yarisi_asan(girdi, atamalar, tanim):
    """HESAPLAMA KURALI -- ihlal uretmez (T-67, sartname #6.3).

    "Bitisi baslangicindan kucuk olan vardiya ertesi gune tasar." Bunu
    zaman modeli her yerde uygular (zaman.aralik, Z-1); ayri bir denetim
    yoktur, cunku denetlenecek bir sey yoktur. Govdenin burada olmasinin
    tek sebebi K-49: kapi artik govdesiz aktif kurali "bakamadim" sayiyor;
    bu kural icin dogru cevap "bakacak bir sey yok, uygulandi"dir, "bakamadim"
    degil.
    """
    return []


@kural("HAFTALIK_AZAMI")
def haftalik_azami(girdi, atamalar, tanim):
    """Haftalik TOPLAM sinir = normal calisma siniri + fazla mesai tavani.

    ⚠ K-38 (Mustafa, 29 Eylul): "HAFTALIK_AZAMI normal calisma siniridir.
      Toplam tavan degildir." 45 saati asan kisim FAZLA MESAIDIR ve kendi
      tavanina tabidir.

    ⚠ BU DUZELTME COZUCUYE UYGULANIP DOGRULAYICIYA UYGULANMAMISTI.
      Zor veri seti yakaladi (29 Eylul): cozucu toplami 55'e kadar acti,
      bu kural hala 45'te kesiyordu ve motorun urettigi plana bagimsiz
      denetci "HAFTALIK_AZAMI ihlali" diyordu. 49 kisilik sahnede 9-13
      ihlal. T-57 ile ayni aile: iki taraf ayni plan hakkinda farkli sey
      soyluyor.

    ⚠ TAVAN KALKMADI, YERI DEGISTI. Fazla mesai MIKTARINI FAZLA_MESAI_TAVANI
      ayrica denetler (sozlesmenin ustu); bu kural MUTLAK tavandir.
    """
    normal = _p(tanim, "azami_saat", 45)
    fm = next((k for k in (girdi.get("kurallar") or [])
               if k.get("kod") == "FAZLA_MESAI_TAVANI" and k.get("aktif", True)),
              None)
    sinir = normal + (_p(fm, "azami_saat_hafta", 10) if fm else 0)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    return [_ihlal("HAFTALIK_AZAMI", tanim, calisan=k, olculen=v, gereken=sinir,
                   mesaj="%s haftada %.1f saat net calisiyor (azami %s)" % (k, v, sinir))
            for k, v in sorted(toplam.items()) if v > sinir]


def _borc_saat(c):
    """Bu calisanin bu hafta DOLDURMASI GEREKEN net saat -- K-39.

        gunluk norm = haftalik_saat / gun_sayisi   (gun_sayisi yoksa 6)
        borc        = haftalik_saat - (onayli izin gunu x gunluk norm)

    ⚠ AYNI HESAP COZUCUDE DE VAR VE BILEREK AYRI YAZILDI (#7.6).
      Ortak bir module cikarmak YASAKTIR: kodu yazan testi de yazarsa ayni
      yanlis varsayim iki yere birden gecer ve hicbir test yakalamaz.
      Burada saat, cozucude dakika cinsinden hesaplanir.
    """
    soz = c.get("sozlesme") or {}
    hafta = soz.get("haftalik_saat")
    if hafta is None:
        return 0.0
    gunluk = float(hafta) / max(1, int(soz.get("gun_sayisi") or 6))
    izin_gun = len({i["gun"] for i in (c.get("izinler") or [])
                    if i.get("durum", "onayli") == "onayli"})
    return max(0.0, float(hafta) - izin_gun * gunluk)


@kural("SAAT_DENGESI")
def saat_dengesi(girdi, atamalar, tanim):
    """Tam zamanli calisan sozlesme saatini DOLDURMUS mu -- K-39.

    ⚠ NEDEN VAR (29 Eylul)
      Bu kuralin cozucude govdesi vardi, DOGRULAYICIDA YOKTU. Yani #7.6'nin
      korumasi bu kuralda hic calismiyordu: motor kendi isini kendi
      onayliyordu.

      Bedeli olculdu -- 350 kisilik sahnede 45 saat sozlesmeli 17 kisiden
      45'i tutturan SIFIR, ortalama 38,2 saat; plan yine de "0 sert ihlal,
      yayinlanabilir: True" donuyordu. 17 kisi x ~3 saat = haftada ~51 saat,
      sozlesmeyle odenen ama planlanmayan zaman.

    ⚠ YARI ZAMANLIYA UYGULANMAZ. Onlarda kisiye ozel taban yoktur (Mustafa,
      29 Eylul); haftalarini UYGUNLUK_TAKVIMI ve talep sekillendirir.

    ⚠ PASIF CALISAN SAYILMAZ: kadroda gorunmeyen birinden saat beklenemez.
      Cozucu de onlari modele hic almiyor.
    """
    tolerans = _p(tanim, "tolerans_saat", 0)
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    cikan = []
    for c in girdi.get("calisanlar", []) or []:
        soz = c.get("sozlesme") or {}
        if soz.get("tip") != "tam_zamanli" or soz.get("haftalik_saat") is None:
            continue
        if c.get("durum", "aktif") != "aktif":
            continue
        gereken = _borc_saat(c) - tolerans
        if gereken <= 0:
            continue
        calisilan = toplam.get(c["id"], 0.0)
        if calisilan + 1e-6 < gereken:
            cikan.append(_ihlal(
                "SAAT_DENGESI", tanim, calisan=c["id"],
                olculen=round(calisilan, 2), gereken=round(gereken, 2),
                mesaj=("%s sozlesmesi %s saat, planda %.1f saat var (izin "
                       "dusuldukten sonra gereken %.1f) -- eksik planlanan "
                       "sure, odenmis sure demektir"
                       % (c["id"], soz.get("haftalik_saat"), calisilan,
                          gereken))))
    return cikan


def _gece_sablonu(sablon):
    """Bu sablon GECE VARDIYASI mi -- K-40. Donen: (gece_mi, tahmin_mi)

    ⚠ ISARET TAHMINI EZER (Mustafa, 29 Eylul: "Bunu kullanici isaretleyecek").
      Isaret yoksa saat araligina dusulur.

    ⚠ AYNI TESPIT COZUCUDE DE VAR VE BILEREK AYRI YAZILDI (#7.6).

    ⚠ OTOMATIK ISARET = YONETMELIGIN TANIMI (T-69, 30 Eylul aksami).
      Postalar Yon. md. 7/2: suresinin YARISINDAN COGU 20:00-06:00'da olan
      vardiya gece calismasidir. Eskiden yalniz AYNI gunun 20:00-06:00
      penceresine "en ufak degme" araniyordu: 00:00-08:45 gece DEGIL,
      13:00-21:00 GECE sayiliyordu -- ikisi de yanlis.

    ⚠ K-43 (Mustafa, 30 Eylul gecesi): OTOMATIK ISARET TABANDIR. Firma
      ustune EKLEYEBILIR ("15:15-24:00 bizde gece sayilir"), altina
      INEMEZ ("22:00-06:00 gece degil" yasal olarak gece olan vardiyayi
      gece calisamayan birine acamaz). Isaret yalniz ekler. Ikinci donen
      deger: isaret YOK, otomatik belirlendi (cozucu bunu nota cevirir).
    """
    yasal = _yasal_gece_postasi_mi(
        {"gun": 0, "bas": sablon["bas"], "bit": sablon["bit"]})
    if "gece_vardiyasi" in sablon:
        return (yasal or bool(sablon["gece_vardiyasi"])), False
    return yasal, True


@kural("GECE_UYGUNLUGU")
def gece_uygunlugu(girdi, atamalar, tanim):
    """Gece calisamayan biri gece vardiyasina atanmis mi -- K-40.

    ⚠ NEDEN VAR (Mustafa, 29 Eylul)
        "Kullanici kartinda gece vardiyasi yapamaz gibi bir ifadeye
         ihtiyacimiz var... gece vardiyalarina uygun olmayan calisanlari
         ilgili vardiyadan direkt elemis olacagiz."

      Bu alan hic yoktu. Bugune kadar ancak her gece icin ayri bir
      `uygunluk` araligi yazarak taklit edilebiliyordu -- zahmetli, ve
      unutuldugunda SESSIZ.
    """
    sablon = {t["id"]: t for t in (girdi.get("vardiya_sablonlari") or [])}
    cikan = []
    for a in atamalar:
        c = _calisan(girdi, a["calisan"]) or {}
        if not c.get("gece_calisamaz"):
            continue
        t = sablon.get(a.get("sablon"))
        if t is None:
            continue
        gece, _tahmin = _gece_sablonu(t)
        if gece:
            cikan.append(_ihlal(
                "GECE_UYGUNLUGU", tanim, calisan=a["calisan"], gun=a["gun"],
                mesaj=("%s gece vardiyasi yapamaz; %s (%s-%s) vardiyasina "
                       "atanmis" % (a["calisan"], t["id"], t["bas"], t["bit"]))))
    return cikan


# ----------------------------------------------------------------------
# GECE_VARDIYASI_AZAMI -- yasal gece siniri ve sektor istisnasi (K-26)
# ----------------------------------------------------------------------
#
# Is K. md. 69 / Postalar Yonetmeligi md. 7: iscinin gece calismasi 7,5
# saati gecemez. 6645 sayili Kanun (23 Nisan 2015) istisna getirdi: turizm,
# ozel guvenlik, saglik hizmeti ve petrol arama/sondaj islerinde, calisanin
# YAZILI ONAYIYLA sinir asilabilir.
#
# ⚠ ISTISNA KISI BAZLIDIR -- K-24'un ucuncu bicimi. Orada bayrak kural
#   SATIRINA bagliydi, burada CALISANA bagli. Ayni firmada ayni vardiyada
#   onayli olan muaf, onaysiz olan degil.
#
# ⚠ OLCU NET CALISMADIR -- `GUNLUK_AZAMI` ile ayni gelenek. Penceresine
#   dusen mola gece calismasindan DUSULUR; pencere disindaki mola dusulmez.
#
# ⚠ Z-5: pencere gun sinirini ASARAK hesaplanir. 19:00-05:00 vardiyasinin
#   gece kismi 20:00-05:00 = 9 saattir. Takvim gunune bakan bir govde
#   20:00-24:00 = 4 saat gorur ve ihlali KACIRIR.

GECE_ISTISNA_SEKTORLERI = frozenset(("turizm", "ozel_guvenlik", "saglik",
                                     "petrol"))


def _gece_pencereleri(pencere_bas, pencere_bit):
    """Planin gorebilecegi butun gece pencereleri -- (gun, bas, bit) mutlak.

    Gun -1 de dahil: pazartesi 00:00-06:00, PAZAR gecesinin penceresidir
    (Z-6: lookback negatif gun uretir, bu dogrudur).
    """
    cikan = []
    for gun in range(-1, 8):
        bas = zaman.mutlak(gun, pencere_bas)
        bit = zaman.mutlak(gun + (1 if pencere_bit <= pencere_bas else 0),
                           pencere_bit)
        cikan.append((gun, bas, bit))
    return cikan


def _kesisim(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def _gece_net_saat(atama, w0, w1):
    """Atamanin [w0, w1) penceresine dusen NET calisma saati."""
    bas, bit = zaman.aralik(atama)
    brut = _kesisim(bas, bit, w0, w1)
    if brut <= 0:
        return 0.0
    mola = sum(_kesisim(m0, m1, w0, w1)
               for m0, m1 in zaman.mola_araliklari(atama))
    return brut - mola


def _gece_onayi_gecerli(calisan, girdi, gun):
    """Calisanin gece calisma yazili onayi O GECE gecerli mi.

    Kabul edilen bicimler:
      True / False                      -> tarihsiz; True suresiz gecerli
      {"onay": True}                    -> tarihsiz, suresiz
      {"onay": True, "gecerli_bitis": "YYYY-AA-GG"}
                                        -> o geceye kadar gecerli

    ⚠ TARIHLI ONAY + HAFTA TARIHI YOK -> GECERSIZ SAYILIR.
      `SOZLESME_GECERLI` tarih yoksa hosgoruludur; burada DEGIL, bilerek.
      Bu bir YASAL sinirin kaldirilmasidir: dogrulanamayan bir istisna,
      yasal bir siniri acmamali. Tarihsiz onay "suresiz" demektir ve
      gecerlidir; tarihli ama kontrol edilemeyen onay degildir.
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
        gece = date.fromisoformat(hafta_bas) + timedelta(days=gun)
        return date.fromisoformat(bitis) >= gece
    except (TypeError, ValueError):
        return False


@kural("GECE_VARDIYASI_AZAMI")
def gece_vardiyasi_azami(girdi, atamalar, tanim):
    """Gece calismasi azami 7,5 saat -- YASAL, SERT. Iki olcu birden:

    1. GECE POSTASI (K-44, 30 Eylul gecesi): vardiya yasal anlamda gece
       calismasiysa (`_yasal_gece_postasi_mi` -- suresinin yarisindan cogu
       20:00-06:00'da) BUTUN net calisma suresi 7,5 saati gecemez.
       Yargitay 9. HD 2016/36126 E., 2020/17967 K.: 20:00-08:00
       vardiyasinda hesap 06:00'da kesilmez, 08:00'e kadar yapilir.
       22:00-08:00 (1 sa mola): eskiden 7 sa -> yasal; simdi 9 sa -> ihlal.
    2. PENCERE (30 Eylul gecesine kadarki tek olcu): 20:00-06:00'a dusen
       net calisma 7,5'i gecemez. Tek basina hicbir zaman ates almaz
       (pencerede 7,5'ten cogu olan vardiya zaten gece postasidir) -- ama
       durmasi kurali eskisinden hicbir durumda GEVSEK yapmaz.

    Ayni olay iki kez yazilmaz (V-1): posta olcusuyle yazilan vardiyanin
    kestigi pencereler ayrica yazilmaz.
    Kanun "gecemez" diyor: tam 7,5 saat ihlal DEGILDIR.
    """
    azami = float(_p(tanim, "azami_saat", 7.5))
    p_bas = float(_p(tanim, "pencere_bas", 20))
    p_bit = float(_p(tanim, "pencere_bit", 6))
    istisnali_sektor = girdi.get("sektor") in GECE_ISTISNA_SEKTORLERI

    cikan = []
    for kimlik, liste in sorted(_kisiye_gore(atamalar).items()):
        c = _calisan(girdi, kimlik) or {}
        yazilan = []                    # posta olcusuyle yazilan araliklar
        for a in liste:
            if not _yasal_gece_postasi_mi(a):
                continue
            if istisnali_sektor and _gece_onayi_gecerli(c, girdi, a["gun"]):
                continue
            net = zaman.net_saat(a)
            if net > azami + 1e-9:
                yazilan.append(zaman.aralik(a))
                cikan.append(_ihlal(
                    "GECE_VARDIYASI_AZAMI", tanim, calisan=kimlik, gun=a["gun"],
                    olculen=round(net, 2), gereken=azami,
                    mesaj="%s gun %d: gece postasinda %.2f saat calisiyor "
                          "(azami %s; vardiyanin yarisindan cogu gecede -- "
                          "Is K. md. 69, Postalar Yon. md. 7)"
                          % (kimlik, a["gun"], net, azami)))
        for gun, w0, w1 in _gece_pencereleri(p_bas, p_bit):
            if istisnali_sektor and _gece_onayi_gecerli(c, girdi, gun):
                continue
            if any(_kesisim(b0, b1, w0, w1) > 0 for b0, b1 in yazilan):
                continue                # V-1: ayni vardiya zaten yazildi
            gece = sum(_gece_net_saat(a, w0, w1) for a in liste)
            if gece > azami + 1e-9:
                cikan.append(_ihlal(
                    "GECE_VARDIYASI_AZAMI", tanim, calisan=kimlik, gun=gun,
                    olculen=round(gece, 2), gereken=azami,
                    mesaj="%s gun %d gecesi %.2f saat gece calisiyor "
                          "(azami %s; Is K. md. 69)"
                          % (kimlik, gun, gece, azami)))
    return cikan


@kural("PART_TIME_LIMIT")
def part_time_limit(girdi, atamalar, tanim):
    """Kismi sureli calisma tavani -- K-39.

    ⚠ TAVAN KISIDEN DEGIL MEVZUATTAN GELIR (Mustafa, 29 Eylul)
      Onceki hali kisinin KENDI sozlesme saatini tavan sayiyordu; 20 saatlik
      bir yari zamanli yogun bir haftada 24 saat calisamiyordu. Oysa
      mevzuatin koydugu sinir bu degil.

      SINIR (Mustafa, 29 Eylul): emsal tam surelinin TAMAMI = 45 saat.
      "Yasa da 45 saate kadar calistirabilirsin, bu fazla mesaiye girmez
      diyor." 30-45 arasi "fazla surelerle calisma"dir; fazla mesai ucreti
      dogurmaz. Oran `emsal_orani` ile kiraci basina degistirilebilir.

      Mustafa: "Kisi icin su kadar saat max veya min calisabilir diye kisit
      girmemize gerek yok. Yapmamiz gereken, calisanin calisabilecegi
      kisitli gunler veya saat araliklari varsa bunu tutmak." -- o da
      UYGUNLUK_TAKVIMI, ayri ve SERT.

    Fazla Calisma Yon. md. 8 geregi kismi sureliye fazla surelerle calisma
    yaptirilamaz; bu yuzden tavanin toleransi 0'dir (K-25 arastirmasi).
    """
    tolerans = _p(tanim, "tolerans_saat", 0)
    # HAFTALIK_AZAMI sahnede tanimli olmayabilir; o zaman kanunun degeri.
    emsal = _p(next((k for k in (girdi.get("kurallar") or [])
                     if k.get("kod") == "HAFTALIK_AZAMI"), {}),
               "azami_saat", 45)
    tavan = _p(tanim, "azami_saat", emsal * _p(tanim, "emsal_orani", 1.0))
    toplam = {}
    for a in atamalar:
        toplam[a["calisan"]] = toplam.get(a["calisan"], 0.0) + zaman.net_saat(a)
    cikan = []
    for kimlik, saat in sorted(toplam.items()):
        c = _calisan(girdi, kimlik) or {}
        soz = c.get("sozlesme") or {}
        if soz.get("tip") != "yari_zamanli":
            continue
        if saat > tavan + tolerans:
            cikan.append(_ihlal(
                "PART_TIME_LIMIT", tanim, calisan=kimlik,
                olculen=saat, gereken=tavan + tolerans,
                mesaj=("%s yari zamanli; mevzuat tavani %.1f saat, "
                       "%.1f saat verilmis" % (kimlik, tavan, saat))))
    return cikan


# ----------------------------------------------------------------------
# Gecmis veri -- T-28, K-42 (30 Eylul)
# ----------------------------------------------------------------------
#
# #11.2 bicimi: calisanlar[].gecmis_vardiyalar = [{"gun": -1, "bas", "bit"}]
# Gun NEGATIF, saat genisletilmis, SABLON YOK -- PDKS gibi gerceklesen kayit.
#
# TEMEL ILKE (K-42): kayitli bir aralik calisildigini KANITLAR; kaydin
# yoklugu HICBIR SEY kanitlamaz. Bilinmeyen gun kisit yaratmaz --
# calisilmamis gibi davranir. Hangi kontrolun yapilamadigini
# `denetle._gecmis_eksik` soyler.
#
# GECMISIN KENDI IHLALI PLANA YAZILMAZ. Asagidaki kurallar yalniz en az
# bir PLAN atamasinin karistigi ihlali yazar: gecmis yeniden planlanamaz.


def _gecmis_kayitlari(girdi, kimlik):
    """Kisinin gecmis kayitlari -- atama bicimine cevrilmis, `_gecmis` isaretli.

    Gunu negatif olmayan kayit ATLANIR: plan haftasi gecmis degildir.
    """
    c = _calisan(girdi, kimlik) or {}
    cikan = []
    for k in c.get("gecmis_vardiyalar") or []:
        gun, bas, bit = k.get("gun"), k.get("bas"), k.get("bit")
        if gun is None or bas is None or bit is None or gun >= 0:
            continue
        a = {"calisan": kimlik, "ekip": None, "sablon": None, "gun": gun,
             "bas": bas, "bit": bit, "molalar": k.get("molalar") or [],
             "_gecmis": True}
        if "gece" in k:
            a["_gece"] = bool(k["gece"])
        cikan.append(a)
    return cikan


def _bilinen_gunler(girdi, kimlik, kayitlar=None):
    """Kaydi TAM olan gecmis gunler.

    `gecmis_bilinen_gunler` verildiyse o gunler bilinir (kaydi olmayan
    bilinen gun = CALISILMAMIS). Kaydi olan gun her durumda bilinir.
    """
    c = _calisan(girdi, kimlik) or {}
    if kayitlar is None:
        kayitlar = _gecmis_kayitlari(girdi, kimlik)
    return ({g for g in (c.get("gecmis_bilinen_gunler") or []) if g < 0}
            | {k["gun"] for k in kayitlar})


def _kisiye_gore_gecmisli(girdi, atamalar):
    """`_kisiye_gore` + o kisilerin gecmis kayitlari.

    Yalniz PLANDA atamasi olan kisiler: gecmisi olup plani olmayan kisinin
    butun ihlalleri gecmistedir ve plana yazilmaz.
    """
    g = _kisiye_gore(atamalar)
    for kimlik, liste in g.items():
        liste.extend(_gecmis_kayitlari(girdi, kimlik))
        liste.sort(key=lambda a: zaman.aralik(a)[0])
    return g


def _atama_gece_mi(girdi, a, sablonlar=None):
    """Bir atama ya da gecmis kaydi GECE mi -- K-40.

    Plan atamasi: yonetmelik tanimi, ustune sablonun isareti (K-43).
    Gecmis kaydi: yonetmelik tanimi, ustune kaydin `gece` isareti.
    """
    if a.get("_gecmis"):
        yasal = _yasal_gece_postasi_mi(a)
        if "_gece" in a:
            return yasal or bool(a["_gece"])
        return yasal
    if sablonlar is None:
        sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari", []) or []}
    t = sablonlar.get(a.get("sablon")) or {"bas": a["bas"], "bit": a["bit"]}
    return _gece_sablonu(t)[0]


def _en_uzun_plan_serisi(gunler):
    """En uzun ardisik gun serisi -- YALNIZ bir plan gununu (>= 0) iceren.

    Donen: (uzunluk, baslangic_gunu). Tamamen gecmiste kalan seri sayilmaz.
    """
    if not gunler:
        return 0, None
    en_uzun, en_bas = 0, None
    seri, bas = 0, None
    for g in range(min(gunler), max(gunler) + 2):
        if g in gunler:
            if seri == 0:
                bas = g
            seri += 1
        else:
            if seri and g - 1 >= 0 and seri > en_uzun:
                en_uzun, en_bas = seri, bas
            seri = 0
    return en_uzun, en_bas


@kural("CAKISMA_YOK")
def cakisma_yok(girdi, atamalar, tanim):
    """Z-3: mutlak zamanda olculur, gun sinirini asan vardiyalar dahil.

    T-28 (30 Eylul): GECMIS KAYITLAR DA bakilir. Pazar 23:00 - pazartesi
    07:00 calismis kisi pazartesi 06:00'da hala calisiyor. Bu cakismayi
    `VARDIYA_ARASI_DINLENME` bilerek bu kurala birakiyor (V-1); bu kural
    gecmisi gormeseydi ikisi birden susardi.
    Iki GECMIS kaydi arasindaki cakisma plana yazilmaz.
    """
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        for i in range(len(liste)):
            for j in range(i + 1, len(liste)):
                if liste[i].get("_gecmis") and liste[j].get("_gecmis"):
                    continue
                ort = zaman.ortusme(liste[i], liste[j])
                if ort > 0:
                    plan = liste[i] if liste[j].get("_gecmis") else liste[j]
                    gecmisle = liste[i].get("_gecmis") or liste[j].get("_gecmis")
                    cikan.append(_ihlal("CAKISMA_YOK", tanim, calisan=kimlik,
                                        gun=plan["gun"], olculen=ort,
                                        mesaj="%s'in iki vardiyasi %s saat cakisiyor%s"
                                              % (kimlik, ort,
                                                 " (biri gecmis kayit)" if gecmisle else "")))
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
    # T-28: gecmis kayitlar da siraya girer -- pazar aksami ile pazartesi
    # sabahi arasi artik gorunur. Sonraki de gecmisse (ikisi de gecmis)
    # plana yazilmaz.
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        for onceki, sonraki in zip(liste, liste[1:]):
            if sonraki.get("_gecmis"):
                continue                      # gecmis kendi icinde
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
    # T-28: gecmis kayitlarin gunleri de dolu sayilir; bilinmeyen gun
    # SAYILMAZ (K-42). Tamamen gecmiste kalan pencere plana yazilmaz.
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        dolu = zaman.calisilan_gunler(liste)
        gunler = sorted(dolu)
        if not gunler:
            continue
        for bas in range(min(gunler), max(gunler) - pencere + 2):
            if bas + pencere - 1 < 0:
                continue                      # tamamen gecmiste
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
    # T-28: seri gecmise uzanabilir; yalniz bir PLAN gununu iceren seri
    # sayilir (`_en_uzun_plan_serisi`). Bilinmeyen gun seriyi KIRAR (K-42).
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        dolu = zaman.calisilan_gunler(liste)
        if not dolu:
            continue
        en_uzun, en_uzun_bas = _en_uzun_plan_serisi(dolu)
        if en_uzun > sinir:
            cikan.append(_ihlal("ARDISIK_CALISMA_GUNU", tanim, calisan=kimlik,
                                gun=en_uzun_bas, olculen=en_uzun, gereken=sinir,
                                mesaj="%s %d gun ust uste calisiyor (azami %s)"
                                      % (kimlik, en_uzun, sinir)))
    return cikan


@kural("ASGARI_VARDIYA_SURESI")
def asgari_vardiya_suresi(girdi, atamalar, tanim):
    """En kisa vardiya -- SERT, firma kurali, kabul edilebilir (#6.2).

    ⚠ OLCU BRUT: vardiyanin suresi, molalar DUSULMEDEN. Bilerek.
      Kaygi calisanin kisa bir is icin yola cikmasi -- sahada GECIRDIGI
      sure. `GUNLUK_AZAMI` net olcer cunku orada kaygi YORGUNLUK.

      Olculdu: net olcseydik firmanin KENDI 4 saatlik sablonlari (09-13,
      17-21) firmanin KENDI 4 saat kuralini her kullanimda cigneyecekti --
      ekip mola politikasi 4 saatlik vardiyaya 1,25-1,5 saat mola yaziyor.

    Tam asgaride ihlal YOK: "en kisa 4 saat" 4 saati kapsar.
    """
    asgari = float(_p(tanim, "asgari_saat", 4))
    cikan = []
    for a in atamalar:
        bas, bit = zaman.aralik(a)
        sure = bit - bas
        if sure < asgari - 1e-9:
            cikan.append(_ihlal(
                "ASGARI_VARDIYA_SURESI", tanim, calisan=a["calisan"],
                gun=a["gun"], olculen=round(sure, 2), gereken=asgari,
                mesaj="%s gun %d: %.2f saatlik vardiya (en kisa %s saat)"
                      % (a["calisan"], a["gun"], sure, asgari)))
    return cikan


@kural("ARDISIK_GECE_LIMIT")
def ardisik_gece_limit(girdi, atamalar, tanim):
    """Ust uste azami gece -- SERT, firma kurali, kabul edilebilir (#6.2).

    ⚠ GECE = K-40'IN ISARETI (`_gece_sablonu`). Sablonda `gece_vardiyasi`
      varsa o gecerli; yoksa saat araligindan tahmin edilir. ADALET_DENGESI
      ile ayni tespit -- iki yerde iki gece tanimi olmasin.
    ⚠ Z-2: vardiya BASLADIGI gune yazilir.
    ⚠ SERI GECE SERISIDIR: arada gunduz vardiyasi da seriyi kirar.
      Calisma gunlerini sayan bir govde yanlis ihlal yazardi.
    ⚠ GECMIS OKUNUR (T-28 kapandi, 30 Eylul): gecen haftanin son geceleri
      seriye girer; bilinmeyen gun seriyi kirar (K-42).
    """
    azami = int(_p(tanim, "azami_gece", 3))
    sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari", []) or []}
    cikan = []
    # T-28: gecmis geceler de sayilir -- cuma, cumartesi, pazar gecesi
    # calismis kisinin pazartesi gecesi DORDUNCUDUR. Gecmis kaydin kendi
    # `gece` isareti saati ezer (K-40).
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        geceler = {a["gun"] for a in liste
                   if _atama_gece_mi(girdi, a, sablonlar)}
        if not geceler:
            continue
        en_uzun, en_bas = _en_uzun_plan_serisi(geceler)
        if en_uzun > azami:
            cikan.append(_ihlal(
                "ARDISIK_GECE_LIMIT", tanim, calisan=kimlik, gun=en_bas,
                olculen=en_uzun, gereken=azami,
                mesaj="%s gun %d'den itibaren %d gece ust uste (azami %s)"
                      % (kimlik, en_bas, en_uzun, azami)))
    return cikan


# ----------------------------------------------------------------------
# Hafta olcekli kurallar -- GECE_POSTASI_DEVRI, ARDISIK_HAFTA_SONU_LIMIT
# (30 Eylul; T-28 kapaninca yazilabilir oldular; tanimlar 30 Eylul
#  gecesi Mustafa'nin kararlariyla K-45 ve K-46 oldu)
# ----------------------------------------------------------------------
#
# HAFTA = plan haftasi. Gun 0..6 -> hafta 0, -7..-1 -> -1, -14..-8 -> -2.
# ⚠ `gun // 7` TABAN BOLMEDIR ve bilerek boyle: `int(gun / 7)` sifira
#   dogru yuvarlar ve -1'i (gecen pazar) BU haftaya koyar.
# ⚠ Bilinmeyen hafta kisit yaratmaz (K-42): kaydin yoklugu calisilmadigini
#   kanitlamaz. Raporu `denetle._gecmis_eksik` yazar.


def _hafta(gun):
    return gun // 7


def _cogunluk_gunu(a):
    """Vardiya, saatlerinin YARISINDAN COGU hangi gune dusuyorsa o gunun
    vardiyasidir -- K-46 (Mustafa, 30 Eylul gecesi).

    Cuma 23:00-06:00 -> 7 saatin 6'si cumartesi -> CUMARTESI.
    Cuma 16:00-01:00 -> 9 saatin 1'i cumartesi -> cuma.
    Tam yari -> basladigi gun. Yonetmeligin gece icin kullandigi olcuyle
    ayni esik (md. 7/2); iki ayri esik icat edilmedi.

    ⚠ YALNIZ HAFTA SONU KURALLARINDA kullanilir (ardisik hafta sonu
      limiti, adaletin hafta sonu boyutu). Motorun genel kurali -- vardiya
      BASLADIGI gune yazilir (Z-2) -- ardisik gun, hafta tatili gibi
      kurallarda oldugu gibi kalir.
    """
    bas, bit = zaman.aralik(a)
    ertesi = zaman.mutlak(a["gun"] + 1, 0)
    tasan = max(0.0, bit - max(bas, ertesi))
    return a["gun"] + 1 if 2 * tasan > (bit - bas) + 1e-9 else a["gun"]


def _hafta_sonu_gunu(a):
    """5 (cumartesi), 6 (pazar) ya da None -- cogunluk gunune gore."""
    g = _cogunluk_gunu(a)
    return g % 7 if g % 7 in (5, 6) else None


def _calisilan_hafta_sonu_gunleri(liste):
    """{hafta: {5, 6} alt kumesi} -- o hafta cumartesi/pazar calisilanlar."""
    cikan = {}
    for a in liste:
        hg = _hafta_sonu_gunu(a)
        if hg is not None:
            cikan.setdefault(_hafta(_cogunluk_gunu(a)), set()).add(hg)
    return cikan


# Postalar Yon. md. 7/2 (TAM METIN, 30 Eylul'de okundu):
#   "Calisma suresinin yarisindan cogu gece donemine rastlayan bir postanin
#    calismasi, gece calismasi sayilir."
# Gece donemi Is K. md. 69/1 -- varsayilan 20:00-06:00.
YASAL_GECE_DONEMI = (20, 6)


def _yasal_gece_postasi_mi(a):
    """Bu atama (ya da gecmis kaydi) YASAL anlamda gece calismasi mi.

    ⚠ K-40 ISARETINE BAKILMAZ -- bilerek (K-43). Isaret FIRMANIN ek
      tanimidir ve firma kurallarinda (ARDISIK_GECE_LIMIT, GECE_UYGUNLUGU)
      yasal tanimin USTUNE eklenir. Yasal kuralda isaret iki yonde de
      yanlis sonuc verirdi:
        * 22:00-06:00'yi "gece degil" isaretleyen firma yasadan kacardi
          (K-18: firma kanunu esnetemez);
        * 15:15-24:00'u "gece" isaretleyen firmanin yasal olarak serbest
          plani, KABUL EDILEMEZ bir "yasal ihlal"le kilitlenirdi (K-20).
    ⚠ BRUT aralikla olculur: molanin yeri bir karar degiskenidir;
      siniflama onun yerine gore degismemeli. Cozucu ayni olcuyu AYRI
      yazar (#7.6).
    ⚠ YARISI DAHIL DEGIL ("yarisindan cogu"): 16:00-24:00 tam yari --
      gece calismasi DEGIL. 00:00-08:45 (6 / 8,75) gece calismasidir;
      onceki gecenin 00:00-06:00 kismi da sayilir.
    ⚠ YARGITAY BUNU BOYLE OKUYOR: 9. HD 2016/36126 E., 2020/17967 K. --
      20:00-08:00 vardiyasinda gece hesabi 06:00'da kesilmez, fiili bitis
      08:00'e kadar yapilir; "yarisindan fazlasi gece donemine denk gelince
      tum calisma gece kurallarina tabi" (K-44).
    """
    bas, bit = zaman.aralik(a)
    gun = a["gun"]
    p_bas, p_bit = YASAL_GECE_DONEMI
    gece = 0.0
    for d in (gun - 1, gun, gun + 1):
        w0 = zaman.mutlak(d, p_bas)
        w1 = zaman.mutlak(d + 1, p_bit)
        gece += max(0.0, min(bit, w1) - max(bas, w0))
    return 2 * gece > (bit - bas) + 1e-9


# Yonetmelik md. 8/3 iki haftalik nobetlesmeye izin veriyor; ucu vermiyor.
# Kural yonetimi ekrani 3 yazdirmamali; motor yine de savunur (K-45).
GECE_HAFTASI_YASAL_UST_SINIR = 2


def _gece_haftasi_azami(tanim):
    """Parametre, yasal ust sinira KIRPILMIS. Kirpildiysa ikinci deger
    verilen sayidir (denetle bunu `eksik_boyutlar`da bildirir)."""
    verilen = int(_p(tanim, "azami_ardisik_gece_haftasi", 1))
    return max(1, min(verilen, GECE_HAFTASI_YASAL_UST_SINIR)), verilen


def _gece_haftasi_mi(hafta_listesi, asgari_gece=None):
    """Bu hafta GECE HAFTASI mi -- K-45 (Mustafa, 30 Eylul gecesi):
    haftanin calisma saatlerinin YARISINDAN COGU gece postasindaysa.

    Yonetmeligin tek vardiya icin kullandigi olcunun haftaya uygulanmis
    hali (md. 7/2). "Bir is haftasi gece calistirilan"i hicbir kaynak
    karma hafta icin tanimlamiyor; kaynaklarin hepsi kuralin amacini ayni
    cumleyle veriyor -- SUREKLI gece calistirma yasagi (Yargitay 22. HD
    2017/24339 E., 2019/18396 K.: bir ay aralıksız gece = ihlal).

    `asgari_gece` (istege bagli, `gece_haftasi_asgari_gece`): haftada bu
    kadar gece vardiyasi da haftayi gece haftasi yapar -- YALNIZ EKLER,
    cogunluk olcusunu gevsetemez (K-18).

    Olcu BRUT saat: gecmis (PDKS) kaydinda mola olmayabilir.
    """
    if not hafta_listesi:
        return False
    gece = [a for a in hafta_listesi if _yasal_gece_postasi_mi(a)]
    if asgari_gece is not None and len(gece) >= int(asgari_gece) > 0:
        return True
    gece_saat = sum(zaman.brut_saat(a) for a in gece)
    toplam = sum(zaman.brut_saat(a) for a in hafta_listesi)
    return 2 * gece_saat > toplam + 1e-9


def _haftaya_gore(liste):
    cikan = {}
    for a in liste:
        cikan.setdefault(_hafta(a["gun"]), []).append(a)
    return cikan


def _hafta_tam_bilinen_mi(hafta, bilinen):
    return all(d in bilinen for d in range(7 * hafta, 7 * hafta + 7))


def _gecmis_gece_haftalari(girdi, kimlik, haftalar, asgari_gece=None):
    """Gecmiste KANITLI gece haftalari -- K-42: yalniz TAM bilinen hafta
    degerlendirilir. Bir gunu bile bilinmeyen haftada cogunluk
    hesaplanamaz; o hafta kisit yaratmaz, raporlanir."""
    bilinen = _bilinen_gunler(girdi, kimlik)
    return {h for h, hl in haftalar.items()
            if h < 0 and _hafta_tam_bilinen_mi(h, bilinen)
            and _gece_haftasi_mi(hl, asgari_gece)}


@kural("GECE_POSTASI_DEVRI")
def gece_postasi_devri(girdi, atamalar, tanim):
    """Is K. md. 69 / Postalar Yon. md. 8 -- gece haftasindan sonra gunduz.

    YASAL, kabul edilemez (#6.3, K-25). Madde metni (tam, 30 Eylul):
      (1) "...en fazla bir is haftasi gece calistirilan iscilerin, ondan
           sonra gelen ikinci is haftasinda gunduz calistirilmalari
           suretiyle ve postalar birbirlerinin yerini alacak sekilde
           duzenlenir."
      (3) "...gece ve gunduz postalarinda iki haftalik nobetlesme esasi da
           uygulanabilir."

    KURAL (K-45): art arda 2 x azami haftalik her pencerede en fazla
    `azami` gece haftasi.
      azami 1 -> gece, gunduz, gece, gunduz
      azami 2 -> gece, gece, gunduz, gunduz (iki haftalik nobetlesme);
                 gece, gece, gunduz, gece YASAK (dortte uc)
    Ust sinir 2 (`GECE_HAFTASI_YASAL_UST_SINIR`).

    GECE HAFTASI = `_gece_haftasi_mi` (cogunluk). GECE = yonetmeligin
    tanimi (`_yasal_gece_postasi_mi`), K-40 isareti degil.
    Yalniz PLAN haftasi yazilir; gecmisin kendi ihlali plana yazilmaz.
    Bilinmeyen gecmis hafta 0 sayilir (K-42) -- rapor denetle'de.
    """
    azami, _ = _gece_haftasi_azami(tanim)
    asgari_gece = _p(tanim, "gece_haftasi_asgari_gece", None)
    pencere = 2 * azami
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        haftalar = _haftaya_gore(liste)
        kanitli = _gecmis_gece_haftalari(girdi, kimlik, haftalar, asgari_gece)
        plan_haftalari = sorted(h for h in haftalar if h >= 0)
        for hafta in plan_haftalari:
            if not _gece_haftasi_mi(haftalar[hafta], asgari_gece):
                continue
            gece_haftalari = kanitli | {h for h in plan_haftalari
                                        if _gece_haftasi_mi(haftalar[h], asgari_gece)}
            sayi = sum(1 for h in range(hafta - pencere + 1, hafta + 1)
                       if h in gece_haftalari)
            if sayi > azami:
                geceler = [a for a in haftalar[hafta]
                           if _yasal_gece_postasi_mi(a)]
                cikan.append(_ihlal(
                    "GECE_POSTASI_DEVRI", tanim, calisan=kimlik,
                    gun=min(a["gun"] for a in geceler),
                    olculen=sayi, gereken=azami,
                    mesaj="%s son %d haftanin %d'inde gece haftasi (en fazla "
                          "%d; gece haftasindan sonra gunduz -- Is K. md. 69, "
                          "Postalar Yon. md. 8)" % (kimlik, pencere, sayi, azami)))
    return cikan


def _geriye_seri(haftalar, hafta):
    """`hafta`dan geriye kesintisiz isaretli hafta sayisi (kendisi dahil)."""
    n = 0
    while hafta - n in haftalar:
        n += 1
    return n


@kural("ARDISIK_HAFTA_SONU_LIMIT")
def ardisik_hafta_sonu_limit(girdi, atamalar, tanim):
    """Ust uste azami hafta sonu -- SERT, firma kurali, kabul edilebilir (#6.5).

    K-46 (Mustafa, 30 Eylul gecesi):
      * "HAFTA SONU CALISTI" = HEM cumartesi HEM pazar calisildi. Tek gun
        yetmez. Haftada 6 gun calisan kisi izin gununu iki gun arasinda
        donusumlu alirsa hic birikmez; kural yalniz iki gunu de ust uste
        calisanlari yakalar -- "uc hafta ust uste tam hafta sonu calismasin".
        ⚠ Onceki tanim (bir gun yeter) hafta hafta planlamada UCUNCU
          haftayi cozumsuz birakiyordu (T-75): 6 gunluk desende herkes her
          hafta sonu "calismis" sayiliyordu.
      * Gun = vardiyanin saatlerinin yarisindan cogunun dustugu gun
        (`_cogunluk_gunu`): cuma 23:00-06:00 cumartesidir.
    Gecmiste yalniz KANITLI (iki gunu de kayitli) hafta sonu sayilir (K-42).
    """
    azami = int(_p(tanim, "azami_ardisik", 2))
    cikan = []
    for kimlik, liste in sorted(_kisiye_gore_gecmisli(girdi, atamalar).items()):
        gunler = _calisilan_hafta_sonu_gunleri(liste)
        tam = {h for h, g in gunler.items() if g >= {5, 6}}
        for hafta in sorted(h for h in tam if h >= 0):
            seri = _geriye_seri(tam, hafta)
            if seri > azami:
                ilk = min(_cogunluk_gunu(a) for a in liste
                          if not a.get("_gecmis")
                          and _hafta_sonu_gunu(a) is not None
                          and _hafta(_cogunluk_gunu(a)) == hafta)
                cikan.append(_ihlal(
                    "ARDISIK_HAFTA_SONU_LIMIT", tanim, calisan=kimlik, gun=ilk,
                    olculen=seri, gereken=azami,
                    mesaj="%s ust uste %d hafta sonu (cumartesi ve pazar) "
                          "calisiyor (azami %d)" % (kimlik, seri, azami)))
    return cikan


# Is K. md. 68 -- BRUT sureye uygulanir (K-4, hukuk teyidi bekliyor: A-16)
MOLA_TABLOSU = ((4, 15), (7.5, 30), (float("inf"), 60))


@kural("MOLA_HAKKI")
def mola_hakki(girdi, atamalar, tanim):
    """Yasal ara dinlenme -- BUTUN molalarin toplamina bakar (K-32).

    ⚠ 25 Eylul'de bu kural bir kez "yalniz `dinlenme` sayilsin" diye
    degistirilmek uzereydi ve YANLIS olurdu: yemek arasi da bir ara
    dinlenmedir ve md. 68'i karsilar. Sistem yemek arasinin uzerine
    otomatik bir saat daha EKLEMEZ. Hatayi A08 altin senaryosu ve dis
    inceleme birlikte yakaladi; ayrintisi K-32'nin duzeltme kaydinda.
    `test_mola_modeli.test_yalniz_yemek_yasal_hakki_KARSILAR` bekcisidir.
    """
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
# Mola bicimi -- K-32 (25 Eylul)
# ----------------------------------------------------------------------

@kural("MOLA_TIPI_ZORUNLU")
def mola_tipi_zorunlu(girdi, atamalar, tanim):
    """Her molanin tipi olmali: `dinlenme` ya da `yemek` (K-32).

    Tipsiz mola motorda `yemek` sayilir -- yani 25 Eylul oncesi davranis
    korunur ve eski girdiler sessizce DEGISMEZ. Ama varsayilana dusmek
    susmak degildir: bu kural onu bildirir. Ucret hesabi tipe bagli oldugu
    icin tipsiz veri, ucreti sessizce yanlis hesaplatabilir.
    """
    gecerli = (zaman.DINLENME, zaman.YEMEK)
    cikan = []
    for a in atamalar:
        kotu = [m for m in (a.get("molalar") or [])
                if m.get("tip") not in gecerli]
        if kotu:
            cikan.append(_ihlal("MOLA_TIPI_ZORUNLU", tanim,
                                calisan=a["calisan"], gun=a["gun"],
                                olculen=len(kotu),
                                mesaj="%s gun %d: %d molanin tipi yok ya da taninmiyor "
                                      "(gecerli: %s). `yemek` sayildi."
                                      % (a["calisan"], a["gun"], len(kotu),
                                         ", ".join(gecerli))))
    return cikan


@kural("MOLA_ASGARI_BLOK")
def mola_asgari_blok(girdi, atamalar, tanim):
    """Bir mola blogu cok kisa olamaz -- varsayilan 15 dk (K-32).

    KAPSAM NOTU: K-32'nin kabul cumlesi yalniz `dinlenme` icin 15 dakika
    diyor. Burasi BUTUN molalara uyguluyor ve bu bilerek daha genis: bes
    dakikalik bir yemek arasi da gercek bir mola degildir. Mevcut hicbir
    fikstur ya da testte 15 dakikadan kisa blok yok, yani genisletme kimseyi
    kirmiyor. Daraltilmasi istenirse `tip` suzgeci eklenir.
    """
    asgari = _p(tanim, "asgari_dakika", 15) / 60.0
    cikan = []
    for a in atamalar:
        for b, s in zaman.mola_araliklari(a):
            if s - b + 1e-9 < asgari:
                cikan.append(_ihlal("MOLA_ASGARI_BLOK", tanim,
                                    calisan=a["calisan"], gun=a["gun"],
                                    olculen=round((s - b) * 60),
                                    gereken=round(asgari * 60),
                                    mesaj="%s gun %d: %.0f dakikalik mola blogu var "
                                          "(en az %.0f dk)"
                                          % (a["calisan"], a["gun"],
                                             (s - b) * 60, asgari * 60)))
    return cikan


@kural("SAHADA_ASGARI")
def sahada_asgari(girdi, atamalar, tanim):
    """Her saatte sahada fiilen bulunmasi gereken kisi sayisi -- SERT (K-33).

    FIRMANIN CUMLESI
      "Sahada en az 5 kisi olacak." Bu bir MOLA kurali degil, SAHA kuralidir:
      firma molayi degil, tezgahta duran kisi sayisini soyler. Molalar bu
      sayiyi tutturmanin onundeki kisittir, konusu degil.

    NEDEN ASGARI_KAPSAMA YETMIYOR
      Ikisi FARKLI BUYUKLUK sayar ve fark tam da molalardir:
          ASGARI_KAPSAMA  -> o saate ATANMIS kisi (mola sayilir)
          SAHADA_ASGARI   -> o saatte SAHADA olan kisi (mola dusulur)
      Vardiyaya yazilmis ama molada olan kisi ilkinde vardir, ikincisinde
      yoktur. Musterinin gordugu ikincisidir.

    NEDEN AYRI BIR KURAL (MOLA_KAPSAMASI degil)
      `MOLA_KAPSAMASI` bilerek YUMUSAK (K-14): mola ciktisi oneridir, sert
      yapmak kendisiyle celisirdi. O karar kisi basina TEK ogle arasi varken
      verildi. Motor artik kisi basina DORT mola uretiyor ve ayni dissiz
      kural tabani tamamen bosaltabiliyor -- 28 Eylul'de olculdu: uc kisilik
      bir planda saat 12 ve 13'te SAHADA SIFIR KISI vardi, sert ihlal 0,
      "yayinlanabilir" True.

      Cozum MOLA_KAPSAMASI'ni sertlestirmek DEGIL: o zaman sahada tam asgari
      kadar kisi varken hic mola verilemez ve plan cozumsuz kalirdi. Ikisi
      ayri isi yapar: yumusak olan plani `asgari`ye dogru iter, bu kural
      tabanin COKMESINI engeller.

    ⚠ DUZELTMENIN KAYDI (28 Eylul, Mustafa)
      Bu kural ilk yazildiginda `min(parametre, hucrenin asgarisi)` ile
      sinirlaniyordu ve hem burada hem cozucude "firma MOLADA en az 5 dese
      de..." diye aciklanmisti. Iki ayri hata:

        1. YANLIS CUMLE. Firma "molada en az 5" demez, "SAHADA en az 5" der.
           Parametre bir mola kotasi degil, saha tabanidir.
        2. YANLIS MANTIK. min(...) firmanin sayisini sessizce talep
           tablosunun sayisiyla degistiriyordu: firma 5 der, hucre 2
           isterse motor 2 uygular ve firmanin cumlesi buharlasirdi.

      Mustafa'nin sozu: "Firma molada en az 5 demeyecek, firma sahada en az
      5 diyecek." Sinir kaldirildi; parametre oldugu gibi uygulanir.

    TABAN TALEBI YUKARI CEKEBILIR -- BU KASITLIDIR
      Firma 5 derken hucre 2 kisi istiyorsa iki SERT kural ayni anda
      gecerlidir ve KATI OLAN baglar: o saatte en az 5 kisi sahada olmak
      zorundadir, dolayisiyla en az 5 kisi atanir. Talep tablosu isin
      gerektirdigini soyler, firma tezgahta gormek istedigini; ikisi
      celisirse motor birini otekine tercih etmez, katiya uyar.

      Celisi plani cozumsuz birakabilir. Cozumsuzluk SESSIZ DEGILDIR --
      teshis katmani sebebi yazar. Sessizce gevsetmek yerine yuksek sesle
      durmak bu projenin tercihi (#7.6).

    NEREYE UYGULANIR
      Talep hucresi OLAN her saate; hucrenin kendi `asgari`sine BAKILMAZ.
      Firmanin talep yazmadigi saatte (kapali donem) taban da yoktur --
      o saatte saha diye bir sey yoktur.

    Kural tanimli degilse taban YOKTUR -- eski davranis aynen korunur.
    """
    taban = _p(tanim, "asgari_sahada", 0)
    if taban <= 0:
        return []
    cikan = []
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    # CEYREK bazinda (K-34): 14:15'te cokup 14:00'de duran bir saha,
    # tabani tutmus SAYILMAZ. Gerekcesi `_talep_anlari`da.
    for t, gun, saat in _talep_anlari(girdi):
        sahada = sum(1 for a in atamalar
                     if ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
                     and zaman.sahada_mi(a, gun, saat))
        if sahada < taban:
            cikan.append(_ihlal("SAHADA_ASGARI", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, olculen=sahada,
                                gereken=taban,
                                mesaj="gun %d saat %s: sahada %d kisi var "
                                      "(en az %d olmali; molada olanlar "
                                      "sahada sayilmaz)"
                                      % (gun, _ss(saat), sahada, taban)))
    return cikan


@kural("MOLA_YERLESIMI")
def mola_yerlesimi(girdi, atamalar, tanim):
    """Yemek molasi kisinin KENDI vardiyasina gore konumlanir (K-32).

    Parametre firma tercihidir: en erken `en_az_saat`, en gec `en_gec_saat`
    -- vardiya BASINDAN itibaren. Mutlak saat degil: 12:00'de baslayan bir
    vardiyada "12-14 arasi" penceresi vardiyanin ilk iki saatine denk gelir
    ve kural kendi kendini patlatir.

    YUMUSAK OLMASI BILEREK (K-14):
      "Mola ciktisi oneri niteligindeyse, mola sirasindaki kapsamayi sert
      kisit yapmak kendi kendisiyle celisirdi."
    Kurumlar molayi bes dakika one, bes dakika arkaya alacak. Sert yapmak
    her gercek plani cokertirdi. SERT olan hakkin VERILMIS olmasidir
    (MOLA_HAKKI); NEREYE kondugu yumusaktir.

    Agirlik girdiden gelir (`tur`), burada sabitlenmez -- kural tanimini
    girdi soyler (#5.1).

    Cozucu ayni pencereyi KENDI tarafinda ayri hesaplar
    (cozucu.model._mola_penceresi_sec). #7.6: tekrar maliyet degil guvence.
    """
    en_az = _p(tanim, "en_az_saat", 3)
    en_gec = _p(tanim, "en_gec_saat", 5)
    cikan = []
    for a in atamalar:
        v_bas, _ = zaman.aralik(a)
        for b, s in zaman.mola_araliklari(a, zaman.YEMEK):
            gecen = b - v_bas
            if gecen + 1e-9 < en_az or gecen - 1e-9 > en_gec:
                cikan.append(_ihlal("MOLA_YERLESIMI", tanim,
                                    calisan=a["calisan"], gun=a["gun"],
                                    olculen=round(gecen, 2),
                                    mesaj="%s gun %d: yemek molasi vardiyanin "
                                          "%.2f. saatinde; %s-%s saat arasi "
                                          "bekleniyordu"
                                          % (a["calisan"], a["gun"], gecen,
                                             en_az, en_gec)))
    return cikan


@kural("YEMEK_TEK_BLOK")
def yemek_tek_blok(girdi, atamalar, tanim):
    """Ogle arasi bolunemez -- K-14 madde 2.

    Ucu uca degen iki blok `mola_araliklari`nda ZATEN birlesir (12:00-12:30
    ile 12:30-13:00 kesintisiz bir saattir). Burada yakalanan, aralarinda
    calisma olan AYRI bloklardir.

    K-14'un gerekcesi 25 Eylul'de duzeltildi: kural ayakta ama sebebi
    mevzuat degil OPERASYON -- bolunmus bir ogle arasi ne calisana dinlenme
    saglar ne operasyona ongorulebilirlik (K-32).
    """
    cikan = []
    for a in atamalar:
        blok = zaman.mola_araliklari(a, zaman.YEMEK)
        if len(blok) > 1:
            cikan.append(_ihlal("YEMEK_TEK_BLOK", tanim,
                                calisan=a["calisan"], gun=a["gun"],
                                olculen=len(blok), gereken=1,
                                mesaj="%s gun %d: yemek molasi %d bloga bolunmus "
                                      "(tek blok olmali)"
                                      % (a["calisan"], a["gun"], len(blok))))
    return cikan


# ----------------------------------------------------------------------
# 6.4 Kapsama
# ----------------------------------------------------------------------

def _talep_hucreleri(girdi):
    """Sartname #11.2: talep hucre basinadir -- {ekip, gun, saat, asgari, hedef}.

    T-19. Cozucu ayni yorumu kendi tarafinda AYRI yapiyor (cozucu.model
    ._hucreler). Buradaki tekrar maliyet degil, #7.6'nin istedigi guvencedir:
    iki taraf ayni girdiyi birbirine sormadan okur; ayrisirlarsa bagimsiz
    denetim ayrismayi gorur. Ortak bir yardimci modul CIKARILAMAZ --
    test_bagimsizlik.test_ortak_yardimci_modul_yok bunu yasakliyor.

    Okunamayan satir atlanir; bildirmek denetle._okunmayan_alanlar'in isi.
    """
    for t in girdi.get("talep", []) or []:
        if t.get("gun") is None or t.get("saat") is None:
            continue
        yield t, t["gun"], t["saat"]


def _ss(an):
    """Kesirli saati insan okusun diye bicimler: 14.25 -> '14:15'."""
    saat = int(an)
    dk = int(round((an - saat) * 60))
    return "%02d:%02d" % (saat % 24, dk) if dk else "%d" % saat


# Talep SAATLIK gelir (#11.2 degismedi), ama kapsama artik CEYREK SAATTE
# olculur -- K-34.
CEYREK = 4


def _talep_anlari(girdi):
    """Talep hucresinin kapsadigi CEYREK anlar -- (hucre, gun, an).

    ⚠ NEDEN VAR (28 Eylul, K-34 uygulanirken bulundu)
      K-33'u doguran sessiz gecisin AYNISI, bu kez bir ceyregin icine
      saklanmisti. Olculdu: iki kisilik planda ikisi de 14:15-14:30 arasi
      molada. 14:00'de ve 15:00'te sahadalar, 14:15'te SIFIR kisi var.
      Dogrulayici HICBIR ihlal yazmiyordu -- cunku yalniz tam saatlere
      bakiyordu.

      Molayi ceyrege tasiyip kontrolu saatte birakmak, sessiz gecisi
      duzeltmek degil GIZLEMEK olurdu: ihlal artik daha kolay saklanirdi.

    GIRDI SOZLESMESI DEGISMEZ
      Talep yine saatlik okunur (#11.2). Bir saatlik hucrenin degeri o
      saatin DORT ceyreginin her birine uygulanir; hucre bolunmez, yalniz
      daha sik ORNEKLENIR.
    """
    for t, gun, saat in _talep_hucreleri(girdi):
        for ceyrek in range(CEYREK):
            yield t, gun, saat + ceyrek / float(CEYREK)


@kural("ASGARI_KAPSAMA")
def asgari_kapsama(girdi, atamalar, tanim):
    """Atanmis kisi sayisina bakar -- MOLA DUSULMEZ.

    Molayi dusen kural MOLA_KAPSAMASI'dir ve o YUMUSAK'tir (K-14). Ikisi
    bilerek ayri: biri 'yeterli kisi planlandi mi', digeri 'o an sahada
    kac kisi var'.
    """
    cikan = []
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    for t, gun, saat in _talep_hucreleri(girdi):
        asgari = t.get("asgari", 0)
        sayi = sum(1 for a in atamalar
                   if ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
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
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    for t, gun, saat in _talep_hucreleri(girdi):
        hedef = t.get("hedef")
        if hedef is None:
            continue
        sayi = sum(1 for a in atamalar
                   if ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
                   and zaman.atanmis_mi(a, gun, saat))
        if sayi < hedef:
            cikan.append(_ihlal("HEDEF_KAPSAMA", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, olculen=sayi, gereken=hedef,
                                mesaj="gun %d saat %d: %d kisi (hedef %d)"
                                      % (gun, saat, sayi, hedef)))
    return cikan


@kural("HEDEF_ASIMI")
def hedef_asimi(girdi, atamalar, tanim):
    """YUMUSAK (K-53, 1 Ekim). Hucreye hedeften FAZLA kisi atanmissa puan
    duser -- plan gecersiz OLMAZ. Fazla kisi paradir: bir saatin bedeli
    olmayinca cozucu gereksiz yere kisi yaziyordu (T-54).

    Hucre basina tek satir, `olculen` atanan kisi, `gereken` hedef; fazla
    kisi sayisi mesajda. Kim sayilir: K-50 (`ekibe_sayilir`).
    """
    cikan = []
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    for t, gun, saat in _talep_hucreleri(girdi):
        hedef = t.get("hedef")
        if hedef is None:
            continue
        sayi = sum(1 for a in atamalar
                   if ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
                   and zaman.atanmis_mi(a, gun, saat))
        if sayi > hedef:
            cikan.append(_ihlal("HEDEF_ASIMI", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=saat, olculen=sayi, gereken=hedef,
                                mesaj="gun %d saat %d: %d kisi atanmis, hedef %d "
                                      "(%d kisi fazla)" % (gun, saat, sayi, hedef,
                                                           sayi - hedef)))
    return cikan


@kural("MOLA_KAPSAMASI")
def mola_kapsamasi(girdi, atamalar, tanim):
    """YUMUSAK (K-14). Mola DUSULDUKTEN sonra sahadaki kisi asgarinin
    altina inerse puan duser -- plan gecersiz OLMAZ."""
    cikan = []
    # CEYREK bazinda olculur (K-34) ama hucre basina TEK ihlal yazilir:
    # o saatin EN KOTU ceyregi. Dort ayri satir yazmak ayni bosuluğu dort
    # kez sayar ve puani sessizce dort katina cikarirdi.
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    for t, gun, saat in _talep_hucreleri(girdi):
        asgari = t.get("asgari", 0)
        en_kotu, en_kotu_an = None, saat
        for ceyrek in range(CEYREK):
            an = saat + ceyrek / float(CEYREK)
            sahada = sum(1 for a in atamalar
                         if ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
                         and zaman.sahada_mi(a, gun, an))
            if en_kotu is None or sahada < en_kotu:
                en_kotu, en_kotu_an = sahada, an
        if en_kotu is not None and en_kotu < asgari:
            cikan.append(_ihlal("MOLA_KAPSAMASI", tanim, ekip=t.get("ekip"),
                                gun=gun, saat=en_kotu_an, sahada=en_kotu,
                                asgari=asgari,
                                olculen=en_kotu, gereken=asgari,
                                mesaj="gun %d saat %s: molalar dusulunce sahada %d kisi kaliyor (asgari %d)"
                                      % (gun, _ss(en_kotu_an), en_kotu, asgari)))
    return cikan


# ----------------------------------------------------------------------
# 6.4 Kapsama -- NITELIK bazli (ROL / YETKINLIK)
# ----------------------------------------------------------------------
#
# BU IKI KURAL COZUCUDE VARDI, BURADA YOKTU (30 Eylul)
#   Sonucu: cozucu kisiti kendi kuruyordu, plan zorunlu olarak uyuyordu,
#   ve bu dosyada govde olmadigi icin denetci "ihlal yok" diyordu -- HIC
#   BAKMADAN. Motor kendi isini kendi onayliyordu, yani #7.6'nin iki
#   yariyi ayirma sebebi bu iki kural icin islemiyordu.
#
#   29 Eylul'deki tam olcekli kosumda "0 sert ihlal, yayinlanabilir True"
#   yaziyordu. Dogru ama eksik: denetci bu iki kurala bakmadi.
#
# SARTNAMEDEN OKUNARAK YAZILDI -- COZUCU KODUNDAN DEGIL
#   #6.4 katalogu iki kuralin isini soyle tanimliyor:
#     ROL_KAPSAMASI        "Belirli operasyonel rolun her ACIK saatte
#                           SAHADA bulunmasi"
#     YETKINLIK_KAPSAMASI  "Belirli SAATLERDE belirli yetkinligin SAHADA
#                           olmasi"
#   Iki kelime belirleyici:
#     ACIK SAAT  -> talep hucresi olan saat. Kapali donemde saha yoktur.
#     SAATLERDE  -> yetkinlik kuralinda saat listesi parametreden gelir;
#                   rol kuralinda liste yoksa ACIK SAATLERIN HEPSI gecerlidir.
#
# MOLA BU IKI KURALDA SAHADAN CIKARMAZ -- K-41 (Mustafa, 30 Eylul)
#   Sartname §6.4 iki kuralda da "SAHADA" diyor ve govde ilk yazilista bunu
#   `zaman.sahada_mi` ile uyguladi. Olculdu: cozucu ATANMIS kisiyi sayiyordu,
#   yani iki taraf ayrisiyordu (T-61). Karar Mustafa'ya soruldu ve olcu
#   DEGISTI -- cozucu hakliydi:
#
#     "Sahada bir mudurun isi 15 dk mola suresini bekleyebilir. Bu 'sahada
#      olmali' kuralini bozmaz. Molalar sahada sayilir olarak gecebilir.
#      Zaten mola oneri gibi bir kurgu olacagindan bu kadar derine inmemize
#      gerek yok."
#
#   Yani bu iki kural "o saatte o nitelik VARDIYADA mi" diye sorar.
#   ⚠ AYRIM BILEREK BIRAKILDI: `SAHADA_ASGARI` (K-33) molayi DUSMEYE devam
#     ediyor. Ikisi farkli sey soyluyor ve bu celiski degil: saha tabani
#     "tezgahta kac kisi var" sorusudur (musteri gorur), nitelik kapsamasi
#     "o nitelik o saat icinde ulasilabilir mi" sorusudur.
#   ⚠ ACIK KALAN: yasal bayrakli bir satirda (ornek: "her vardiyada 1 ilk
#     yardim sertifikali kisi") molanin sayilmasi hukuken tartisilabilir.
#     Mustafa bugun daha derine inilmemesini istedi; gerekirse gereklilik
#     satirina kendi secenegi eklenir (K-41'in ucuncu secenegi).
#
#   Cozucunun kisit kodu bilerek okunmadi. T-19'un dersi: iki taraf ayni
#   yanlis gelenegi paylasirsa ikisi birbiriyle tutarli ve ikisi de yanlis
#   olur; bagimsiz denetim de o yanlisi goremez.
#
# TEK MEKANIZMA, IKI KURAL -- #6.4 notu
#   Ikisi ayni isi yapar; tek fark calisanin hangi niteligine bakildigidir
#   (`operasyonel_rol` tek deger, `yetkinlikler` liste). Kullanici icin iki
#   ayri kavram oldugu icin katalogda iki satir olarak gorunur.
#
# BAYRAK SATIR BAZLI -- K-24, #5.3
#   Bu iki kuralda `yasal` kuralin degil SATIRIN ozelligidir: "her vardiyada
#   1 ilk yardim sertifikali kisi" muhtemelen yasaldir, "kahvaltida 1
#   barista" ticari tercihtir. Burada ek bir is gerekmiyor: her gereklilik
#   satiri girdide ayri bir kural tanimi oldugu icin `_ihlal` her satirin
#   kendi bayragini tasir (denetle.degerlendir her tanimi ayri cagirir).


def _nitelik_anlari(girdi, ekip, gun, saat_kumesi):
    """Denetlenecek (gun, an) ciftleri. Talep hucrelerinden turetilir.

    Hucreler CEYREK olarak orneklenir (K-34): 14:15'te nitelik sahadan
    cikip 14:00'de duruyorsa kural tutmus sayilmaz. `SAHADA_ASGARI` ile
    ayni gerekce -- `_talep_anlari`nin basindaki kayda bakin.

    Ayni (gun, an) birden fazla ekip hucresinden gelebilir; kume ile
    tekillestirilir, yoksa ayni acik icin ekip sayisi kadar satir yazilirdi.
    """
    anlar = set()
    for t, g, an in _talep_anlari(girdi):
        if ekip is not None and t.get("ekip") != ekip:
            continue
        if gun is not None and g != gun:
            continue
        if saat_kumesi is not None and int(an) not in saat_kumesi:
            continue
        anlar.add((g, an))
    return sorted(anlar)


def _nitelik_tasiyanlar(girdi, alan, aranan, ekip):
    """Aranan niteligi tasiyan calisan kimlikleri."""
    kimlikler = set()
    for c in girdi.get("calisanlar", []) or []:
        if ekip is not None and ekip not in (c.get("ekipler") or []):
            continue
        if alan == "yetkinlikler":
            if aranan in (c.get("yetkinlikler") or []):
                kimlikler.add(c.get("id"))
        elif c.get(alan) == aranan:
            kimlikler.add(c.get("id"))
    return kimlikler


def _nitelik_kapsamasi(girdi, atamalar, tanim, kod, alan, parametre_adi):
    """ROL_KAPSAMASI / YETKINLIK_KAPSAMASI -- ortak govde.

    `ekip` YAZILMAMISSA kural SAHA CAPINDA okunur: hangi ekipte olursa
    olsun niteligi tasiyan ve o an sahada olan herkes sayilir. Satir bir
    ekip adi vermiyorsa kelimenin duz anlami budur. Ekip adi verilirse hem
    denetlenen saatler hem sayilan kisiler o ekibe daralir.

    Parametre yoksa govde SESSIZ GECMEZ ama ihlal de YAZMAZ: hangi rolun
    arandigi bilinmiyorsa plan hakkinda bir sey soylenemez. Bildiren kanal
    `denetle._eksik_boyutlar` -- "kural yazili, bir parcasi eksik".

    Olcu ATANMIS olmaktir, sahada olmak degil -- K-41. Gerekcesi dosyanin
    bu bolumunun basindaki kayitta.

    CEYREK ORNEKLEME MOLA ICIN DEGIL, VARDIYA SINIRI ICIN GEREKLI
      Mola artik dusulmedigine gore saat icinde tek degisen sey vardiyanin
      baslamasi/bitmesidir -- ve K-34'ten beri bunlar ceyrekli olabiliyor
      (07:00-15:30). 15:30'da biten tek lider, saat 15'in ilk iki ceyregini
      kapatir, son ikisini kapatmaz. Yalniz tam saate bakan bir govde bunu
      goremez.
    """
    p = tanim.get("parametreler") or {}
    aranan = p.get(parametre_adi)
    if aranan is None:
        return []
    asgari = p.get("asgari", 1)
    if asgari <= 0:
        return []
    ekip = p.get("ekip")
    saatler = p.get("saatler")
    saat_kumesi = None if saatler is None else {int(s) for s in saatler}

    tasiyanlar = _nitelik_tasiyanlar(girdi, alan, aranan, ekip)
    uyelik, mod = uyelik_haritasi(girdi), cok_ekipli_sayim(girdi)
    # K-50: `hepsi`de niteligi tasiyan cok ekipli kisi, baska ekibin
    # vardiyasindayken de bu ekibin gerekliligini karsilar.
    ilgili = [a for a in atamalar
              if a.get("calisan") in tasiyanlar
              and ekibe_sayilir(a, ekip, uyelik, mod)]

    cikan = []
    for gun, an in _nitelik_anlari(girdi, ekip, p.get("gun"), saat_kumesi):
        varlik = sum(1 for a in ilgili if zaman.atanmis_mi(a, gun, an))
        if varlik < asgari:
            cikan.append(_ihlal(
                kod, tanim, ekip=ekip, gun=gun, saat=an, nitelik=aranan,
                olculen=varlik, gereken=asgari,
                mesaj="gun %d saat %s: '%s' niteligini tasiyan %d kisi "
                      "vardiyada (en az %d olmali; molada olan sayilir "
                      "-- K-41)" % (gun, _ss(an), aranan, varlik, asgari)))
    return cikan


@kural("ROL_KAPSAMASI")
def rol_kapsamasi(girdi, atamalar, tanim):
    """Belirli operasyonel rol her acik saatte sahada -- SERT.

    Ornek: "her acik saatte en az 1 takim lideri sahada olsun".
    Saat listesi verilmezse talep hucresi olan BUTUN saatler denetlenir.
    """
    return _nitelik_kapsamasi(girdi, atamalar, tanim,
                              "ROL_KAPSAMASI", "operasyonel_rol", "rol")


@kural("YETKINLIK_KAPSAMASI")
def yetkinlik_kapsamasi(girdi, atamalar, tanim):
    """Belirli saatlerde belirli yetkinlik sahada -- SERT.

    Ornek: "on buroda her saat yabanci dil", "kahvaltida en az 1 barista".
    """
    return _nitelik_kapsamasi(girdi, atamalar, tanim,
                              "YETKINLIK_KAPSAMASI", "yetkinlikler",
                              "yetkinlik")


# ----------------------------------------------------------------------
# 6.6 Duzenleme
# ----------------------------------------------------------------------

@kural("KILIT_UYUMU")
def kilit_uyumu(girdi, atamalar, tanim):
    """Yoneticinin elle verdigi karar plana aynen yansir; motor geri alamaz.

    IKI KILIT BICIMI VAR ve ikisi de desteklenir:

      sabitleme  {calisan, ekip, gun, bas, bit}   -> bu atama MUTLAKA olacak
      yasak      {calisan, gun, tip: "yasak"}     -> o gun HICBIR atama olmayacak

    16 Eylul: ilk yazimda yalniz sabitleme biciminde dusunulmustu ve 'yasak'
    kilidi KeyError ile cokuyordu. A06 fiksturu tam da bu bicimi kullaniyor.
    Cokme sessiz bir hata degil ama yanlis yerde patliyordu.
    """
    def anahtar(a):
        return (a["calisan"], a.get("ekip"), a["gun"], a["bas"], a["bit"])

    var = {anahtar(a) for a in atamalar}
    cikan = []

    def sabitleme_var_mi(k):
        """Sabitleme satiri planda var mi: `sablon` kimligiyle ya da saatle;
        `ekip` yazilmamissa ekibe bakilmaz (T-38, 1 Ekim)."""
        for a in atamalar:
            if a["calisan"] != k.get("calisan") or a["gun"] != k.get("gun"):
                continue
            if k.get("sablon") is not None and a.get("sablon") == k.get("sablon"):
                return True
            if "bas" in k and "bit" in k and \
                    abs(float(a["bas"]) - float(k["bas"])) < 1e-6 and \
                    abs(float(a["bit"]) - float(k["bit"])) < 1e-6 and \
                    (k.get("ekip") is None or a.get("ekip") == k.get("ekip")):
                return True
        return False

    # #11.2'nin `sabit_atamalar` listesi de bir sabitleme kilididir (T-38):
    # ayni soz -- yoneticinin verdigi atama planda MUTLAKA olur.
    for a in girdi.get("sabit_atamalar", []) or []:
        if ("bas" in a and "bit" in a) or a.get("sablon") is not None:
            if not sabitleme_var_mi(a):
                cikan.append(_ihlal("KILIT_UYUMU", tanim, calisan=a.get("calisan"),
                                    gun=a.get("gun"),
                                    mesaj="sabit atama planda yok: %s gun %s"
                                          % (a.get("calisan"), a.get("gun"))))
        else:
            cikan.append(_ihlal("KILIT_UYUMU", tanim, calisan=a.get("calisan"),
                                gun=a.get("gun"),
                                mesaj="sabit atama bicimi taninmadi: %r" % sorted(a)))
    for k in girdi.get("kilitler", []) or []:
        if k.get("tip") == "yasak":
            calisiyor = [a for a in atamalar
                         if a["calisan"] == k["calisan"] and a["gun"] == k["gun"]]
            if calisiyor:
                cikan.append(_ihlal("KILIT_UYUMU", tanim, calisan=k["calisan"],
                                    gun=k["gun"],
                                    mesaj="%s gun %d'de calismamali (kilit: yasak) ama %d atama var"
                                          % (k["calisan"], k["gun"], len(calisiyor))))
        elif "bas" in k and "bit" in k:
            if not sabitleme_var_mi(k):
                cikan.append(_ihlal("KILIT_UYUMU", tanim, calisan=k["calisan"],
                                    gun=k["gun"],
                                    mesaj="kilitli atama planda yok: %s gun %d"
                                          % (k["calisan"], k["gun"])))
        else:
            cikan.append(_ihlal("KILIT_UYUMU", tanim, calisan=k.get("calisan"),
                                gun=k.get("gun"),
                                mesaj="kilit bicimi taninmadi: %r" % sorted(k)))
    return cikan


@kural("DONMUS_GUN")
def donmus_gun(girdi, atamalar, tanim):
    """Donmus gun degismez -- K-54 (T-29, 1 Ekim).

    ⚠ ESKI GOVDE OLUYDU (T-29, dis inceleme 16 Eylul): yalniz `_yeni`
      bayragi tasiyan atamayi ihlal sayiyordu ve o bayragi hicbir sey
      uretmiyordu. Kural katalogda vardi, pratikte hic ateslenemiyordu.

    SIMDI: donmus gunlerin atamalari `mevcut_plan` (yayinlanmis plan,
    yoneticinin duzenledigi haliyle) ile KARSILASTIRILIR -- ozel bayrak yok.
    Planda olup ciktida olmayan satir "silinmis", ciktida olup planda
    olmayan satir "eklenmis"; degistirilmis satir ikisi birden. Uc durum da
    yakalanir (kabul cumlesi: "donmus gun degismez"). Kabul edilemez: motor
    gecmisi yeniden yazamaz.

    Donmus gun var ama `mevcut_plan` YOKSA kural DENETLENEMEZ -- bos liste
    "ihlal yok" demek degildir; `denetle._eksik_boyutlar` bunu
    `denetlenemedi` diye bildirir ve kapi K-49 ile kabul bekletir.
    """
    donmus = set(girdi.get("donmus_gunler", []) or [])
    plan = girdi.get("mevcut_plan")
    if not donmus or plan is None:
        return []

    def anahtar(a):
        return (a.get("calisan"), a.get("gun"),
                round(float(a.get("bas", 0)), 4), round(float(a.get("bit", 0)), 4))

    beklenen = {}
    for a in plan:
        if a.get("gun") in donmus:
            beklenen[anahtar(a)] = beklenen.get(anahtar(a), 0) + 1
    bulunan = {}
    for a in atamalar:
        if a.get("gun") in donmus:
            bulunan[anahtar(a)] = bulunan.get(anahtar(a), 0) + 1
    cikan = []
    for k in sorted(set(beklenen) | set(bulunan), key=lambda k: (str(k[0]), k[1], k[2])):
        b, v = beklenen.get(k, 0), bulunan.get(k, 0)
        if b == v:
            continue
        calisan, gun, bas, bit = k
        if v > b:
            mesaj = ("gun %d donmus: %s icin %s-%s atamasi mevcut planda YOK -- "
                     "donmus gune yeni atama yazilamaz (olan oldu)"
                     % (gun, calisan, _ss(bas), _ss(bit)))
        else:
            mesaj = ("gun %d donmus: %s icin %s-%s atamasi mevcut planda VARDI, "
                     "plandan cikmis -- donmus gunden atama silinemez (olan oldu)"
                     % (gun, calisan, _ss(bas), _ss(bit)))
        cikan.append(_ihlal("DONMUS_GUN", tanim, calisan=calisan, gun=gun, mesaj=mesaj))
    return cikan


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

# ⚠ T-71 (30 Eylul aksami): "gece" boyutu burada eskiden KENDI olcusunu
#   kullaniyordu -- "herhangi bir parcasi 20:00-06:00'ya degiyorsa gece" --
#   ve K-40 isaretini HIC okumuyordu. Cozucu isareti okuyordu: firmanin
#   "gece degil" dedigi 13:45-23:00 dogrulayicida gece sayiliyordu. Artik
#   ARDISIK_GECE_LIMIT ile ayni tespit (`_atama_gece_mi`): isaret, yoksa
#   md. 7/2.


def _boyut_sayaci(boyut, girdi=None):
    """Bir boyutun 'bu atama sayilir mi' olcusu. Sayilamayan boyut -> None."""
    if boyut == "gece":
        girdi = girdi or {}
        sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari", []) or []}
        return lambda a: _atama_gece_mi(girdi, a, sablonlar)
    # K-46: gun = saatlerinin yarisindan cogunun dustugu gun (cuma
    # 23:00-06:00 cumartesidir). Hafta sonu kurallariyla ayni tanim.
    if boyut == "hafta_sonu":
        return lambda a: _hafta_sonu_gunu(a) is not None
    if boyut == "cumartesi":
        return lambda a: _hafta_sonu_gunu(a) == 5
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
        sayac = _boyut_sayaci(boyut, girdi)
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
