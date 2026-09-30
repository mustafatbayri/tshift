# -*- coding: utf-8 -*-
"""
DENETLEYICI -- /evaluate ucunun govdesi (Master Spec v1.4 #11.4)

NE YAPAR
  Girdi + atamalar alir, ihlal listesi ve metrikler dondurur. Plan URETMEZ.

NE YAPMAZ -- ve bu bir eksiklik degil
  * Plan uretmez. Uretmek cozucunun isi (#11.2 /solve).
  * Ihlali DUZELTMEZ, oneri vermez. Oneri /suggest'in isi (#11.5).
  * Kurali degistirmez. Neyin aktif oldugunu girdi soyler.

SESSIZ GECMEME ILKESI
  Girdide aktif ama govdesi yazilmamis bir kural varsa, sonuc
  `uygulanmayan_kurallar` listesinde bunu ACIKCA bildirir. "Ihlal yok"
  demekle "bakmadim" demek ayni sey degildir; ikisini karistiran bir
  dogrulayici, yesil yanan ama hicbir sey sinamayan testten daha
  tehlikelidir.

  Ucu ayni ilkenin uc kanali:
    `uygulanmayan_kurallar`  -- aktif ama govdesi yazilmamis KURAL
    `eksik_boyutlar`         -- yazilmis bir kuralin yazilmamis PARCASI (T-13)
    `okunmayan_alanlar`      -- gonderilmis ama okunmamis GIRDI ALANI (T-19)
  Ucu de bugun yalniz RAPOR. Yayin kapisinin bunlara ne yapacagi hala acik:
  T-18. Kapi bugun sadece `ihlaller`e bakiyor -- yani ucu de kapiyi gecer.
"""

from . import kurallar, zaman


def _aktif_kurallar(girdi):
    for k in girdi.get("kurallar", []) or []:
        if k.get("aktif", True):
            yield k


def degerlendir(girdi, atamalar):
    """Master Spec #11.4: {'ihlaller': [...], 'metrikler': {...}}"""
    atamalar = atamalar or []
    ihlaller = []
    uygulanmayan = []

    for tanim in _aktif_kurallar(girdi):
        kod = tanim.get("kod")
        govde = kurallar.KAYIT.get(kod)
        if govde is None:
            uygulanmayan.append(kod)
            continue
        ihlaller.extend(govde(girdi, atamalar, tanim))

    return {
        "ihlaller": ihlaller,
        "metrikler": _metrikler(girdi, atamalar, ihlaller),
        "uygulanmayan_kurallar": uygulanmayan,
        "eksik_boyutlar": _eksik_boyutlar(girdi),
        "okunmayan_alanlar": _okunmayan_alanlar(girdi),
        "gecmis_eksik": _gecmis_eksik(girdi, atamalar),
        "yayin_kapisi": yayin_kapisi(ihlaller),
    }


# ----------------------------------------------------------------------
# Okunmayan girdi alanlari -- T-19
# ----------------------------------------------------------------------
#
# NEDEN VAR
#   `uygulanmayan_kurallar` "aktif ama govdesi yazilmamis KURAL"i bildiriyor.
#   GIRDI ALANLARI icin ayni kanal yoktu: cagiran taraf sartnamedeki bir alani
#   gonderiyor, motor okumuyor, ve KIMSE bilmiyor. T-19'da bunun bedeli
#   olculdu -- sartname bicimindeki talep gorulmedi, sifir atamali plan "%100
#   kapsama, yayinlanabilir" dedi.
#
# BU LISTE BIR SOZ DEGIL, BIR ENVANTER
#   Asagidaki her ad, 23 Eylul taramasinda cozucu/ veya dogrulayici/ icinde
#   EN AZ BIR SATIRDA okundugu gorulerek yazildi. Bir adi buraya eklemek onu
#   okunur YAPMAZ. Once okuyan satiri yaz, sonra adi buraya ekle. Ters sira,
#   O-11'in ta kendisidir: olculmemis bir guvence beyani.
#
# HARITADA OLMAYAN KAP = SERBEST ANAHTAR
#   `agirliklar`, `devir_yuk`, `kurallar[].parametreler` gibi anahtari
#   veriden gelen kaplar bilerek haritada yok; icine inilmez.

OKUNAN_ALANLAR = {
    "": ("profil", "calisanlar", "vardiya_sablonlari", "talep", "kurallar",
         "kilitler", "sabit_atamalar", "donmus_gunler", "hafta_baslangic",
         "agirliklar", "sektor"),
    "calisanlar": ("id", "ekipler", "sozlesme", "izinler", "uygunluk",
                   "devir_yuk", "yetkinlikler", "operasyonel_rol",
                   "gece_calisamaz", "durum", "gece_calisma_onayi",
                   "gecmis_vardiyalar", "gecmis_bilinen_gunler"),
    # T-28 (30 Eylul): gecmis kayit PDKS bicimindedir -- sablon yok.
    "calisanlar.gecmis_vardiyalar": ("gun", "bas", "bit", "molalar", "gece"),
    "calisanlar.sozlesme": ("tip", "haftalik_saat", "gun_sayisi"),
    "calisanlar.izinler": ("gun", "durum"),
    "calisanlar.uygunluk": ("tip", "gun", "bas", "bit"),
    "vardiya_sablonlari": ("id", "bas", "bit", "mola_dk", "mola_penceresi",
                           "gunler", "gece_vardiyasi"),
    "vardiya_sablonlari.mola_penceresi": ("en_erken", "en_gec_bitis"),
    "talep": ("ekip", "gun", "saat", "asgari", "hedef"),
    "kurallar": ("kod", "tur", "aktif", "yasal", "kabul_edilebilir",
                 "parametreler", "agirlik"),
    "kilitler": ("calisan", "gun", "tip", "bas", "bit"),
    # Motor sabit atamayi SABLON kimliginden esliyor (cozucu.model
    # ._sabit_atamalar). Sartname #11.2 ornegi `sablon` yazmiyor, `bas`/`bit`
    # yaziyor -- T-38. Eslesmeyen satir `uygulanmayan_notlar`a dusuyor, yani
    # sessiz degil; ama gonderilen bas/bit sablonunkinden FARKLIYSA kimse
    # gormez. Bu yuzden ikisi de bilerek listede YOK.
    "sabit_atamalar": ("calisan", "gun", "sablon"),
}

# Sebebi bilinen alanlar. Bilinmeyen bir ad da bildirilir -- yazim hatasi
# ("ekpiler") da bu kanaldan gorunsun diye liste DEGIL, harita disi her sey
# raporlanir.
#
# Asagidaki adlarin cogu tek bir bulgunun uyeleri: T-38 (sartnamenin
# karsiligi yazilmamis alanlari). Ayri numarasi olan ikisi: talep bicimi
# T-19 (kapandi), gecmis_vardiyalar T-28 (30 Eylul'de okunur oldu).
SEBEPLER = {
    ("talep", "gunler"):
        "gruplu talep kisayolu; sartname #11.2 hucre basina bir satir ister (T-19)",
    ("talep", "saatler"):
        "gruplu talep kisayolu; sartname #11.2 hucre basina bir satir ister (T-19)",
    ("calisanlar", "tercihler"):
        "sartname #11.2'de tanimli, motorda tek satiri yok -- tercih plana etki etmez",
    ("calisanlar", "kural_degerleri"):
        "kisiye ozel kural degeri okunmuyor; herkese genel kural uygulanir",
    ("sabit_atamalar", "bas"):
        "motor sabit atamayi `sablon` kimliginden esliyor; bas/bit okunmuyor",
    ("sabit_atamalar", "bit"):
        "motor sabit atamayi `sablon` kimliginden esliyor; bas/bit okunmuyor",
    ("sabit_atamalar", "ekip"):
        "sabit atamanin ekibi okunmuyor; ekip calisanin kendi listesinden gelir",
    ("calisanlar.izinler", "tum_gun"):
        "motora YALNIZ tam gun izin gonderilir (K-31). Bu alan geldiyse yarim "
        "gunluk izin ayiklanmamis olabilir; motor onu TAM GUN sayar ve kisiyi "
        "o gun hic planlamaz. Yarim gun plan editoruyle yonetilir",
    ("vardiya_sablonlari", "mola_tek_blok"):
        "mola tek blok zorunlulugu modele girmiyor; mola bolunebilir",
    ("vardiya_sablonlari", "mola_en_erken"):
        "sartname duz alan yaziyor, motor mola_penceresi.en_erken okuyor",
    ("vardiya_sablonlari", "mola_en_gec_bitis"):
        "sartname duz alan yaziyor, motor mola_penceresi.en_gec_bitis okuyor",
    ("", "devir_kapsama"):
        "sartname #11.2'de tanimli, motorda karsiligi yok",
    ("", "istek_id"):
        "motor istek kimligini okumuyor ve ciktiya GERI YAZMIYOR (#11.3 yaziyor)",
    ("", "sure_butcesi_sn"):
        "motor sureyi _cozucu_ayari'ndan aliyor; bu alan etkisiz (T-38)",
}


def _okunmayan_alanlar(girdi):
    """Gonderilmis ama motorun okumadigi girdi alanlari.

    Isi DURDURMAZ. Karar (Mustafa, 23 Eylul): bildirilsin, reddedilmesin --
    reddetmek, tanimadigi bir alan yuzunden calisan bir plani yok eder.
    """
    cikan = []
    gorulen = set()

    def gez(kap, dugum):
        if isinstance(dugum, list):
            for e in dugum:
                gez(kap, e)
            return
        if not isinstance(dugum, dict):
            return
        okunan = OKUNAN_ALANLAR.get(kap)
        if okunan is None:
            return                        # serbest anahtarli kap
        for ad in sorted(dugum):
            if ad.startswith("_"):        # fikstur yorumu, veri degil
                continue
            if ad not in okunan:
                if (kap, ad) not in gorulen:
                    gorulen.add((kap, ad))
                    cikan.append({
                        "alan": ad,
                        "yer": kap or "girdi",
                        "sebep": SEBEPLER.get((kap, ad),
                                              "motor bu alani okumuyor"),
                    })
                continue
            gez((kap + "." + ad) if kap else ad, dugum[ad])

    gez("", girdi)
    return cikan


# ----------------------------------------------------------------------
# Gecmis veri eksik -- K-42 (Mustafa, 30 Eylul)
# ----------------------------------------------------------------------
#
# KARAR: "Gecmis veri yoksa ... gecmise dayanan kriterleri dikkate almadan
# ilerlemek." Yasal kurallar DAHIL -- ayni gun ayrica soruldu ve boyle
# kararlastirildi. Motor durmaz, bilinmeyen gun kisit yaratmaz.
#
# AMA SESSIZ GECMEZ: bu kanal hangi kontrolun kimin icin yapilamadigini
# yazar. Yalniz RAPOR -- ihlal degil, yayin kapisina girmez (T-18).
#
# ⚠ GURULTU DEGIL, KESIN SATIR. Gercek veride kayitlarin yalniz %18'i dolu
#   (P-1). Her pazartesi calisani icin dort satir yazan bir kanal okunmaz
#   olurdu (O-7). Bu yuzden satir yalniz SONUCU GERCEKTEN DEGISTIREBILECEK
#   bilinmeyen gun icin yazilir:
#     * pazartesi bossa sinir kurallari etkilenemez -> satir yok
#     * geriye yururken BILINEN bos gun gorulurse seri orada kirilir -> yok
#     * gecmisle birlikte ihlal ZATEN kanitliysa -> ihlal kanali soyler, yok
#     * ilk BILINMEYEN gun, seri hala esige yetisebilecekken -> SATIR

def _geri_yuru(dolu, bilinen, plan_serisi, esik):
    """Pazartesiden geriye yuru. Donen: (durum, gun).

    dolu         : gecmiste "sayilan" gunler (calisilan ya da gece olan)
    bilinen      : kaydi tam olan gecmis gunler
    plan_serisi  : pazartesiden baslayan planli seri uzunlugu
    esik         : serinin ihlal sayildigi uzunluk

    durum -- "ilgisiz" · "ihlal" (kanitli) · "guvenli" · "belirsiz"
    """
    if plan_serisi == 0 or plan_serisi >= esik:
        return "ilgisiz", None
    k = 0
    for d in range(-1, -esik, -1):
        if d in dolu:
            k += 1
            if k + plan_serisi >= esik:
                return "ihlal", None
        elif d in bilinen:
            return "guvenli", None
        else:
            return "belirsiz", d
    return "guvenli", None


def _plan_serisi(gunler):
    """Pazartesiden (gun 0) baslayan kesintisiz seri."""
    n = 0
    while n in gunler:
        n += 1
    return n


def _hafta_geriye(isaretli, bos_mu, esik):
    """Plan haftasindan (0) geriye HAFTA HAFTA yuru -- K-42, hafta olcekli.

    Plan haftasi serinin ilk halkasidir (cagiran bunu garanti eder).
    isaretli : gecmiste KANITLI isaretli haftalar (gece haftasi, calisilan
               hafta sonu)
    bos_mu   : hafta -> o haftanin isaretsiz oldugu KANITLI mi (ilgili
               butun gunleri biliniyor)
    esik     : serinin ihlal sayildigi uzunluk (azami + 1)

    Donen: (durum, hafta) -- durum `_geri_yuru` ile ayni dort deger.
    """
    if esik <= 1:
        return "ilgisiz", None
    seri = 1
    for hafta in range(-1, -esik, -1):
        if hafta in isaretli:
            seri += 1
            if seri >= esik:
                return "ihlal", None
        elif bos_mu(hafta):
            return "guvenli", None
        else:
            return "belirsiz", hafta
    return "guvenli", None


def _gecmis_eksik(girdi, atamalar):
    aktif = {t.get("kod"): t for t in _aktif_kurallar(girdi)}
    sinir_kurallari = ("VARDIYA_ARASI_DINLENME", "HAFTA_TATILI",
                       "ARDISIK_CALISMA_GUNU", "ARDISIK_GECE_LIMIT",
                       "GECE_POSTASI_DEVRI", "ARDISIK_HAFTA_SONU_LIMIT")
    if not any(k in aktif for k in sinir_kurallari):
        return []
    sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari", []) or []}
    cikan = []

    def yaz(kod, kimlik, gun, ne):
        cikan.append({"kural": kod, "calisan": kimlik, "gun": gun,
                      "mesaj": "%s icin %s yapilamadi -- gun %d icin gecmis "
                               "kayit yok (K-42: atlandi)" % (kimlik, ne, gun)})

    for kimlik, liste in sorted(kurallar._kisiye_gore(atamalar).items()):
        kayitlar = kurallar._gecmis_kayitlari(girdi, kimlik)
        bilinen = kurallar._bilinen_gunler(girdi, kimlik, kayitlar)
        plan_gunleri = {a["gun"] for a in liste}

        if ("VARDIYA_ARASI_DINLENME" in aktif and 0 in plan_gunleri
                and -1 not in bilinen):
            yaz("VARDIYA_ARASI_DINLENME", kimlik, -1,
                "pazartesi dinlenme kontrolu")

        gecmis_gunler = {k["gun"] for k in kayitlar}
        seri = _plan_serisi(plan_gunleri)
        for kod, esik, ne in (
                ("HAFTA_TATILI",
                 kurallar._p(aktif.get("HAFTA_TATILI") or {}, "pencere_gun", 7),
                 "hafta tatili kontrolu (kayan pencere)"),
                ("ARDISIK_CALISMA_GUNU",
                 kurallar._p(aktif.get("ARDISIK_CALISMA_GUNU") or {},
                             "azami_gun", 6) + 1,
                 "ardisik calisma gunu kontrolu")):
            if kod not in aktif:
                continue
            durum, gun = _geri_yuru(gecmis_gunler, bilinen, seri, esik)
            if durum == "belirsiz":
                yaz(kod, kimlik, gun, ne)

        if "ARDISIK_GECE_LIMIT" in aktif:
            plan_geceler = {a["gun"] for a in liste
                            if kurallar._atama_gece_mi(girdi, a, sablonlar)}
            gecmis_geceler = {k["gun"] for k in kayitlar
                              if kurallar._atama_gece_mi(girdi, k, sablonlar)}
            esik = int(kurallar._p(aktif["ARDISIK_GECE_LIMIT"],
                                   "azami_gece", 3)) + 1
            durum, gun = _geri_yuru(gecmis_geceler, bilinen,
                                    _plan_serisi(plan_geceler), esik)
            if durum == "belirsiz":
                yaz("ARDISIK_GECE_LIMIT", kimlik, gun,
                    "ardisik gece kontrolu")

        # HAFTA OLCEKLI IKI KURAL (30 Eylul). Rapor yalniz plan haftasi
        # serinin ilk halkasiysa yazilir: bu hafta gece yoksa (hafta sonu
        # bos ise) gecmisin ne oldugu sonucu degistiremez.
        _hafta = kurallar._hafta
        if "GECE_POSTASI_DEVRI" in aktif and any(
                _hafta(a["gun"]) == 0 and kurallar._yasal_gece_postasi_mi(a)
                for a in liste):
            gece_haftalari = {_hafta(k["gun"]) for k in kayitlar
                              if kurallar._yasal_gece_postasi_mi(k)}
            azami = int(kurallar._p(aktif["GECE_POSTASI_DEVRI"],
                                    "azami_ardisik_gece_haftasi", 1))
            durum, hafta = _hafta_geriye(
                gece_haftalari,
                lambda h: all(d in bilinen for d in range(7 * h, 7 * h + 7)),
                azami + 1)
            if durum == "belirsiz":
                yaz("GECE_POSTASI_DEVRI", kimlik,
                    max(d for d in range(7 * hafta, 7 * hafta + 7)
                        if d not in bilinen),
                    "gece postasi devri kontrolu")

        if "ARDISIK_HAFTA_SONU_LIMIT" in aktif and any(
                _hafta(a["gun"]) == 0 and kurallar._hafta_sonu_mu(a["gun"])
                for a in liste):
            hs_haftalari = {_hafta(k["gun"]) for k in kayitlar
                            if kurallar._hafta_sonu_mu(k["gun"])}
            azami = int(kurallar._p(aktif["ARDISIK_HAFTA_SONU_LIMIT"],
                                    "azami_ardisik", 2))
            durum, hafta = _hafta_geriye(
                hs_haftalari,
                lambda h: 7 * h + 5 in bilinen and 7 * h + 6 in bilinen,
                azami + 1)
            if durum == "belirsiz":
                yaz("ARDISIK_HAFTA_SONU_LIMIT", kimlik,
                    max(d for d in (7 * hafta + 5, 7 * hafta + 6)
                        if d not in bilinen),
                    "ardisik hafta sonu kontrolu")
    return cikan


def _eksik_boyutlar(girdi):
    """Aktif bir kuralin, govdesi olmayan boyutlari.

    Kuralin KENDISI yazilmis ama bir PARCASI yazilmamis olabilir --
    ADALET_DENGESI'nin 'saat' boyutu boyle (T-13). `uygulanmayan_kurallar`
    bunu goremez, cunku kural listede var. Ayri bir alan gerekiyor:
    yoksa kural 'yazilmis' gorunur, bir boyutu sessizce atlanir.
    """
    eksik = []
    for tanim in _aktif_kurallar(girdi):
        kod = tanim.get("kod")
        p = tanim.get("parametreler") or {}

        if kod == "ADALET_DENGESI":
            for boyut in p.get("boyutlar", ["gece", "hafta_sonu", "saat"]):
                if kurallar._boyut_sayaci(boyut) is None:
                    eksik.append({"kural": "ADALET_DENGESI", "boyut": boyut,
                                  "sebep": "sayilabilir boyut degil; T-13"})

        # ROL_KAPSAMASI / YETKINLIK_KAPSAMASI: gereklilik satirinda hangi
        # nitelik arandigi yazilmamissa kural DENETLENEMEZ. Govde bos liste
        # donuyor -- yani "ihlal yok" gibi gorunuyor. Ayrimi burada yapmak
        # zorunlu: "ihlal yok" ile "bakamadim" ayni sey degil.
        for k, ad in (("ROL_KAPSAMASI", "rol"),
                      ("YETKINLIK_KAPSAMASI", "yetkinlik")):
            if kod == k and p.get(ad) is None:
                eksik.append({
                    "kural": k, "boyut": ad,
                    "sebep": "gereklilik satirinda `%s` yazili degil; hangi "
                             "niteligin arandigi bilinmiyor -- denetlenemedi"
                             % ad})
    return eksik


# ----------------------------------------------------------------------
# Metrikler -- #11.3
# ----------------------------------------------------------------------

def _metrikler(girdi, atamalar, ihlaller):
    sert = [i for i in ihlaller if i.get("agirlik") == "SERT"]
    hucre = kapsama_yuzdeleri(girdi, atamalar)

    # K-32: TEK bir "mesai suresi" toplami YOK. Ucu ayri ayri raporlanir,
    # cunku ayni calisanin ucu de farkli olabilir:
    #   toplam_saat  -- CALISMA suresi, butun molalar dusuk (yasal sayac)
    #   ucret_saat   -- UCRET hesabi, yalniz ucretsiz mola dusuk
    #   brut_saat    -- vardiya araligi, hic mola dusulmemis
    toplam_net = sum(zaman.net_saat(a) for a in atamalar)
    toplam_ucret = sum(zaman.ucret_saat(a) for a in atamalar)
    toplam_brut = sum(zaman.brut_saat(a) for a in atamalar)

    # Sozlesme saati bir UCRET buyuklugudur: firmanin ucretli saydigi kisa
    # molalar yuzunden "eksik calisti" denmemeli (K-32 kabul cumlesi 10).
    # Tipsiz veride ucret_saat == net_saat oldugu icin eski davranis aynen
    # korunur.
    fazla = 0.0
    kisi_saat = {}
    for a in atamalar:
        kisi_saat[a["calisan"]] = kisi_saat.get(a["calisan"], 0.0) + zaman.ucret_saat(a)
    for c in girdi.get("calisanlar", []):
        soz = (c.get("sozlesme") or {}).get("haftalik_saat")
        if soz is not None:
            fazla += max(0.0, kisi_saat.get(c["id"], 0.0) - soz)

    return {
        "sert_ihlal": len(sert),
        "yumusak_ihlal": len(ihlaller) - len(sert),
        "asgari_kapsama_yuzde": hucre["asgari_yuzde"],
        "hedef_kapsama_yuzde": hucre["hedef_yuzde"],
        "eksik_hedef_dakika": hucre["eksik_hedef_dakika"],
        "toplam_saat": toplam_net,
        "ucret_saat": toplam_ucret,
        "brut_saat": toplam_brut,
        "fazla_mesai_saat": fazla,
    }


def kapsama_yuzdeleri(girdi, atamalar):
    """Talep hucrelerinin ne kadarinin dolduguna bakar.

    Talep yoksa yuzde 100 doner -- 'sinanacak bir sey yoktu' demektir,
    'mukemmel' degil. A4 gibi yalitilmis senaryolarda talep bilerek bostur.

    T-19 TUZAGI: bu ayrimi yuzde TEK BASINA tasiyamaz. 'Talep yok' ile
    'talep vardi, okuyamadim' ikisi de sifir hucre demek, ikisi de %100
    gosterir. Okuyamama durumunu `okunmayan_alanlar` bildirir; yuzdeyi
    okuyan taraf (yayin kapisi dahil) o listeye de bakmak zorunda -- T-18.
    """
    asgari_tut = asgari_top = hedef_tut = hedef_top = 0
    eksik_dk = 0
    for t in girdi.get("talep", []) or []:
        gun, saat = t.get("gun"), t.get("saat")
        if gun is None or saat is None:
            continue                      # T-19: bildirmek okunmayan_alanlar'in isi
        sayi = sum(1 for a in atamalar
                   if a.get("ekip") == t.get("ekip")
                   and zaman.atanmis_mi(a, gun, saat))
        if t.get("asgari") is not None:
            asgari_top += 1
            if sayi >= t["asgari"]:
                asgari_tut += 1
        if t.get("hedef") is not None:
            hedef_top += 1
            if sayi >= t["hedef"]:
                hedef_tut += 1
            else:
                eksik_dk += (t["hedef"] - sayi) * 60
    yuzde = lambda tut, top: 100.0 if top == 0 else round(100.0 * tut / top, 2)
    return {
        "asgari_yuzde": yuzde(asgari_tut, asgari_top),
        "hedef_yuzde": yuzde(hedef_tut, hedef_top),
        "eksik_hedef_dakika": eksik_dk,
    }


# ----------------------------------------------------------------------
# Yayin kapisi -- #4.5, K-16 / K-20 / K-24
# ----------------------------------------------------------------------

def yayin_kapisi(ihlaller):
    """Bu plan yayinlanabilir mi, yayinlanamazsa neden.

    Kapi `kabul_edilebilir` alanina bakar, `yasal`a DEGIL. Sebep K-24:
    CAKISMA_YOK yasal bir kural degil (hicbir kanun cakismayi yasaklamiyor)
    ama kabul de edilemez -- imkansizliktir.
    """
    acik_sert = [i for i in ihlaller
                 if i.get("agirlik") == "SERT" and i.get("durum") != "kabul_edildi"]
    engelleyen = [i for i in acik_sert if not i.get("kabul_edilebilir")]
    kabul_bekleyen = [i for i in acik_sert if i.get("kabul_edilebilir")]
    return {
        "yayinlanabilir": not acik_sert,
        "engelleyen_ihlaller": engelleyen,       # kabul secenegi SUNULMAZ
        "kabul_bekleyen_ihlaller": kabul_bekleyen,  # gerekceyle kabul edilebilir
        "kabul_secenegi_sunulur": bool(kabul_bekleyen) and not engelleyen,
    }
