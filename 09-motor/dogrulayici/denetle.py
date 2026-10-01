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

    gecmis_eksik = _gecmis_eksik(girdi, atamalar)
    eksik_boyutlar = _eksik_boyutlar(girdi)
    # K-54: yalniz donmus gunlere dayanan ihlal "olan oldu"dur -- isaretlenir,
    # ayri listelenir, kapi ve sert sayac onu saymaz. ISARET KAPIDAN ONCE.
    gecmis_ihlaller = _gecmis_ihlalleri_isaretle(girdi, atamalar, ihlaller)
    return {
        "ihlaller": ihlaller,
        "metrikler": _metrikler(girdi, atamalar, ihlaller),
        "uygulanmayan_kurallar": uygulanmayan,
        "eksik_boyutlar": eksik_boyutlar,
        "okunmayan_alanlar": _okunmayan_alanlar(girdi),
        "gecmis_eksik": gecmis_eksik,
        "gecmis_eksik_ozet": _gecmis_eksik_ozet(girdi, gecmis_eksik),
        "gecmis_ihlaller": gecmis_ihlaller,
        # T-18 / K-49: kapi artik "bakamadim"i da gorur.
        "yayin_kapisi": yayin_kapisi(ihlaller, girdi, uygulanmayan, eksik_boyutlar),
    }


# Gunsuz (haftalik) ihlallerden yalniz TAVAN turu kurallar gecmis sayilabilir:
# saat arttikca kotulesen kural, donmus gunler tek basina tavani asmissa
# gelecek bunu duzeltemez. Eksiklik ve karsilastirma kurallari (SAAT_DENGESI
# "eksik", ADALET_DENGESI) yalniz donmus gunlerle degerlendirilince HER ZAMAN
# daha kotu gorunur -- gelecek onlari duzeltebilir; o yuzden gunsuzken asla
# gecmis sayilmaz. (1 Ekim tam olcek kosusunda olculdu: adalet ihlalleri
# yanlis yere "olan oldu" isareti aliyordu.)
GUNSUZ_TAVAN_KURALLARI = frozenset((
    "HAFTALIK_AZAMI", "FAZLA_MESAI_TAVANI", "PART_TIME_LIMIT",
    "YILLIK_FAZLA_MESAI_TAVANI",
))


def _gecmis_ihlalleri_isaretle(girdi, atamalar, ihlaller):
    """K-54 (T-29): donmus gunlerin ihlali 'olan oldu'dur; raporlanir, engellemez.

    MUSTAFA (1 Ekim): kapanan gunlerde plan "yoneticinin bilgisi dahilinde"
      degisebilir -- birini o gun ise cagirmistir. Yonetici gecmis gunleri
      duzenleyip motora gonderir; motor onlari OLDUGU GIBI alir.

    O duzenleme bir kurali cignemis olabilir (iki vardiya, izinli gunde
    calisma, 11 saatten az dinlenme). Bu GERCEKTIR ve rapora girer; ama
    yayin kapisini kapatirsa yonetici cikmaza girer: gecmisi degistiremez,
    gelecegi yayinlayamaz. Bu yuzden:

      * Ihlalin gunu donmus degilse  -> gecmis DEGIL (gelecek degisebilir).
      * Ihlalin gunu donmus ise, ya da gunsuz ama TAVAN turu bir kural ise
        (GUNSUZ_TAVAN_KURALLARI) -> ayni kural YALNIZ donmus gunlerin
        atamalariyla da ayni ihlali uretiyor mu diye bakilir. Uretiyorsa
        ihlal gecmise aittir: `gecmis: True`. (Donmus gunle serbest gun
        arasindaki dinlenme ihlali boyle isaretlenMEZ: serbest gun degisince
        ihlal kalkar. Gunsuz eksiklik/karsilastirma kurallari -- saat
        dengesi, adalet -- hic isaretlenmez: gelecek onlari duzeltebilir.)
      * DONMUS_GUN'un kendi ihlali ASLA gecmis sayilmaz -- o, planin
        degistirildigini soyler, gecmisin kusurunu degil.

    Isaretli ihlal `ihlaller` listesinde KALIR (sayilar eksilmez, metin
    kaybolmaz); kapi (`yayin_kapisi`) ve `metrikler.sert_ihlal` onu saymaz,
    `gecmis_ihlaller` listesi ve `metrikler.gecmis_sert_ihlal` ayrica sayar.
    """
    donmus = set(girdi.get("donmus_gunler", []) or [])
    if not donmus or not ihlaller:
        return []
    adaylar = [i for i in ihlaller
               if i.get("kural") != "DONMUS_GUN"
               and (i.get("gun") in donmus
                    or (i.get("gun") is None
                        and i.get("kural") in GUNSUZ_TAVAN_KURALLARI))]
    if not adaylar:
        return []
    gecmis_atamalar = [a for a in (atamalar or []) if a.get("gun") in donmus]
    gecmiste = set()
    for tanim in _aktif_kurallar(girdi):
        kod = tanim.get("kod")
        if kod == "DONMUS_GUN" or kod not in {i.get("kural") for i in adaylar}:
            continue
        govde = kurallar.KAYIT.get(kod)
        if govde is None:
            continue
        for i in govde(girdi, gecmis_atamalar, tanim):
            gecmiste.add((i.get("kural"), i.get("calisan"), i.get("gun")))
    isaretli = []
    for i in adaylar:
        if (i.get("kural"), i.get("calisan"), i.get("gun")) in gecmiste:
            i["gecmis"] = True
            i["gecmis_notu"] = ("donmus gune ait -- olan oldu; kapi saymaz, "
                                "yonetici bilgisine (K-54)")
            isaretli.append(i)
    return isaretli


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
         "agirliklar", "sektor", "denetim_disi_kabul", "cok_ekipli_sayim",
         "departmanlar", "istek_id", "sure_butcesi_sn", "mevcut_plan"),
    "calisanlar": ("id", "ekipler", "sozlesme", "izinler", "uygunluk",
                   "devir_yuk", "yetkinlikler", "operasyonel_rol",
                   "gece_calisamaz", "durum", "gece_calisma_onayi",
                   "gecmis_vardiyalar", "gecmis_bilinen_gunler",
                   "yil_ici_fazla_mesai_saat"),
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
    # T-18 / K-49: yetkilinin "denetlenemeyen kurali kabul ediyorum" kaydi.
    "denetim_disi_kabul": ("kod", "gerekce", "onaylayan"),
    # K-52: departman ve calisma saatleri (CALISMA_SAATLERI).
    "departmanlar": ("id", "ad", "ekipler", "acik"),
    "departmanlar.acik": ("gunler", "bas", "bit"),
    "kilitler": ("calisan", "gun", "tip", "bas", "bit"),
    # K-54: yayinlanmis plan -- cikti bicimiyle ayni satirlar (#11.3).
    "mevcut_plan": ("calisan", "ekip", "sablon", "gun", "bas", "bit",
                    "molalar", "donmus"),
    "mevcut_plan.molalar": ("bas", "bit", "tip"),
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


def _gecmis_eksik(girdi, atamalar):
    aktif = {t.get("kod"): t for t in _aktif_kurallar(girdi)}
    sinir_kurallari = ("VARDIYA_ARASI_DINLENME", "HAFTA_TATILI",
                       "ARDISIK_CALISMA_GUNU", "ARDISIK_GECE_LIMIT",
                       "GECE_POSTASI_DEVRI", "ARDISIK_HAFTA_SONU_LIMIT",
                       "YILLIK_FAZLA_MESAI_TAVANI")
    if not any(k in aktif for k in sinir_kurallari):
        return []
    sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari", []) or []}
    cikan = []

    def yaz(kod, kimlik, gun, ne):
        cikan.append({"kural": kod, "calisan": kimlik, "gun": gun,
                      "mesaj": "%s icin %s yapilamadi -- gun %d icin gecmis "
                               "kayit yok (K-42: atlandi)" % (kimlik, ne, gun)})

    normal = kurallar._p(aktif.get("HAFTALIK_AZAMI") or {}, "azami_saat", 45)
    for kimlik, liste in sorted(kurallar._kisiye_gore(atamalar).items()):
        kayitlar = kurallar._gecmis_kayitlari(girdi, kimlik)
        bilinen = kurallar._bilinen_gunler(girdi, kimlik, kayitlar)
        plan_gunleri = {a["gun"] for a in liste}

        # Yillik fazla mesai (K-49 ile yazildi): yil ici toplam bilinmiyorsa
        # ve bu hafta fazla mesai VARSA kontrol yapilamadi. Fazla mesai
        # yoksa bilinmeyen toplam bir sey degistirmez -- satir yazilmaz.
        if "YILLIK_FAZLA_MESAI_TAVANI" in aktif:
            c = kurallar._calisan(girdi, kimlik) or {}
            if c.get("yil_ici_fazla_mesai_saat") is None:
                hafta_net = sum(zaman.net_saat(a) for a in liste)
                if hafta_net > normal + 1e-9:
                    cikan.append({
                        "kural": "YILLIK_FAZLA_MESAI_TAVANI", "calisan": kimlik,
                        "gun": None,
                        "mesaj": "%s icin yillik fazla mesai kontrolu yapilamadi"
                                 " -- yil ici fazla mesai toplami bilinmiyor "
                                 "(yil_ici_fazla_mesai_saat yok), bu hafta %.1f "
                                 "saat fazla mesai var (K-42: atlandi)"
                                 % (kimlik, hafta_net - normal)})

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

        # HAFTA OLCEKLI IKI KURAL (30 Eylul; tanimlar K-45, K-46). Rapor
        # yalniz plan haftasi sonucu DEGISTIREBILECEKSE yazilir: bu hafta
        # gece haftasi degilse (hafta sonu tam calisilmadiysa) gecmisin ne
        # oldugu sonucu degistiremez.
        _hafta = kurallar._hafta
        haftalar = kurallar._haftaya_gore(liste + kayitlar)
        if "GECE_POSTASI_DEVRI" in aktif:
            tanim = aktif["GECE_POSTASI_DEVRI"]
            asgari_gece = kurallar._p(tanim, "gece_haftasi_asgari_gece", None)
            if kurallar._gece_haftasi_mi(haftalar.get(0, []), asgari_gece):
                azami, _ = kurallar._gece_haftasi_azami(tanim)
                kanitli = kurallar._gecmis_gece_haftalari(
                    girdi, kimlik, haftalar, asgari_gece)
                bilinmeyen = [h for h in range(-(2 * azami - 1), 0)
                              if not kurallar._hafta_tam_bilinen_mi(h, bilinen)]
                # Kanitli gece haftalari zaten esige ulastiysa ihlal kanali
                # soyler; bilinmeyen haftalar eklenince ulasabiliyorsa rapor.
                if (len(kanitli) < azami
                        and len(kanitli) + len(bilinmeyen) >= azami):
                    en_yakin = max(bilinmeyen)
                    yaz("GECE_POSTASI_DEVRI", kimlik,
                        max(d for d in range(7 * en_yakin, 7 * en_yakin + 7)
                            if d not in bilinen),
                        "gece postasi devri kontrolu (gece haftasi mi, "
                        "haftanin tamami bilinmeden hesaplanamaz)")

        if "ARDISIK_HAFTA_SONU_LIMIT" in aktif:
            gunler = kurallar._calisilan_hafta_sonu_gunleri(liste + kayitlar)
            if gunler.get(0, set()) >= {5, 6}:
                azami = int(kurallar._p(aktif["ARDISIK_HAFTA_SONU_LIMIT"],
                                        "azami_ardisik", 2))
                # Geriye `azami` hafta sonu yurunur: hepsi tam calisilmissa
                # ihlal kanali soyler; bilinen ve tam calisilmamis olan
                # seriyi kirar; ILK bilinmeyen hafta sonu rapordur --
                # kalan hafta sonlari calisilmis olsa esige ulasilirdi.
                for h in range(-1, -azami - 1, -1):
                    if gunler.get(h, set()) >= {5, 6}:
                        continue                # kanitli
                    if 7 * h + 5 in bilinen and 7 * h + 6 in bilinen:
                        break                   # bilinen, tam calisilmamis
                    yaz("ARDISIK_HAFTA_SONU_LIMIT", kimlik,
                        max(d for d in (7 * h + 5, 7 * h + 6)
                            if d not in bilinen),
                        "ardisik hafta sonu kontrolu")
                    break
    return cikan


def _gecmis_eksik_ozet(girdi, gecmis_eksik):
    """K-47 (Mustafa, 30 Eylul gecesi): "Yonetici baksin."

    Sahte PDKS olcumunde 49 kisilik plan icin 141 satir cikti; icinde 7
    gercek ihlal vardi (T-77). Satir satir okunmaz; KISI BASINA gruplanir,
    YASAL kontrolu yapilamayanlar one alinir. Yayin kapisi bunu ENGELLEMEZ
    (K-42: atlanir, raporlanir); ekran yoneticiye gosterir ve "gordum"
    onayi ister -- o kisim backend/arayuzun isi.
    """
    yasal = {t.get("kod"): bool(t.get("yasal")) for t in _aktif_kurallar(girdi)}
    kisiler = {}
    for x in gecmis_eksik:
        k = kisiler.setdefault(x["calisan"], {"calisan": x["calisan"],
                                             "kurallar": set(), "yasal": False})
        k["kurallar"].add(x["kural"])
        if yasal.get(x["kural"]):
            k["yasal"] = True
    liste = [dict(k, kurallar=sorted(k["kurallar"])) for k in kisiler.values()]
    liste.sort(key=lambda k: (not k["yasal"], k["calisan"]))
    return {
        "satir": len(gecmis_eksik),
        "kisi": len(liste),
        "yasal_kontrol_yapilamayan_kisi": sum(1 for k in liste if k["yasal"]),
        "kisiler": liste,
    }


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
                                  "sebep": "sayilabilir boyut degil; T-13",
                                  "denetlenemedi": True})

        # K-45: yasal ust sinir 2. Fazlasi verildiyse 2 uygulanir ve bu
        # SESSIZ GECMEZ -- firma yasal kurali gevsetmis gibi gorunurdu.
        if kod == "GECE_POSTASI_DEVRI":
            azami, verilen = kurallar._gece_haftasi_azami(tanim)
            if verilen != azami:
                eksik.append({
                    "kural": kod, "boyut": "azami_ardisik_gece_haftasi",
                    "sebep": "verilen %d yasal ust siniri (%d) asiyor; %d "
                             "uygulandi -- firma yasal kurali gevsetemez "
                             "(K-18, K-45)" % (verilen, azami, azami),
                    # Kural DENETLENDI (yasal degerle); bu bir kirpma raporu.
                    "denetlenemedi": False})

        # CALISMA_SAATLERI (K-52): ekibin departman saatleri tanimsizsa o
        # ekip icin kontrol YAPILAMAZ -- "ihlal yok" degil, "bakamadim".
        if kod == "CALISMA_SAATLERI":
            saatler = kurallar.departman_saatleri(girdi)
            ekipler = sorted({t.get("ekip") for t in girdi.get("talep", []) or []
                              if t.get("ekip") is not None}
                             | {t.get("ekip") for t in girdi.get("vardiya_sablonlari", []) or []
                                if t.get("ekip") is not None})
            for ekip in ekipler:
                if ekip not in saatler or saatler[ekip] is None:
                    eksik.append({
                        "kural": kod, "boyut": "departman:%s" % ekip,
                        "sebep": "%s ekibinin departman calisma saatleri "
                                 "tanimsiz (`departmanlar`); kapali saat "
                                 "kontrolu yapilamadi" % ekip,
                        "denetlenemedi": True})

        # DONMUS_GUN (K-54): donmus gun var ama yayinlanmis plan verilmemisse
        # "donmus gun degismedi" kontrolu YAPILAMAZ -- bos liste "ihlal yok"
        # degil, "bakamadim"dir. SERT + firma kurali: kapi kabul bekletir.
        if kod == "DONMUS_GUN":
            if (girdi.get("donmus_gunler") or []) and girdi.get("mevcut_plan") is None:
                eksik.append({
                    "kural": kod, "boyut": "mevcut_plan",
                    "sebep": "donmus gun var (%s) ama `mevcut_plan` verilmedi; "
                             "donmus gunlerin degismedigi kontrol edilemedi"
                             % sorted(girdi.get("donmus_gunler") or []),
                    "denetlenemedi": True})

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
                             % ad,
                    "denetlenemedi": True})
    return eksik


# ----------------------------------------------------------------------
# Metrikler -- #11.3
# ----------------------------------------------------------------------

def _metrikler(girdi, atamalar, ihlaller):
    # K-54: donmus gune ait ihlal (olan oldu) sert sayaca girmez, ayri sayilir.
    sert = [i for i in ihlaller if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    gecmis_sert = [i for i in ihlaller if i.get("agirlik") == "SERT" and i.get("gecmis")]
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
        "gecmis_sert_ihlal": len(gecmis_sert),          # K-54
        "yumusak_ihlal": len(ihlaller) - len(sert) - len(gecmis_sert),
        "asgari_kapsama_yuzde": hucre["asgari_yuzde"],
        "hedef_kapsama_yuzde": hucre["hedef_yuzde"],
        "eksik_hedef_dakika": hucre["eksik_hedef_dakika"],
        "baska_ekipten_kapsama": hucre["baska_ekipten_kapsama"],   # K-50
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
    uyelik, mod = kurallar.uyelik_haritasi(girdi), kurallar.cok_ekipli_sayim(girdi)
    # K-50 gorunurlugu: baska ekibin vardiyasiyla kapatilan hucreler.
    baska_hucre = baska_kisi_saat = 0
    for t in girdi.get("talep", []) or []:
        gun, saat = t.get("gun"), t.get("saat")
        if gun is None or saat is None:
            continue                      # T-19: bildirmek okunmayan_alanlar'in isi
        kendi = sum(1 for a in atamalar
                    if a.get("ekip") == t.get("ekip")
                    and zaman.atanmis_mi(a, gun, saat))
        sayi = sum(1 for a in atamalar
                   if kurallar.ekibe_sayilir(a, t.get("ekip"), uyelik, mod)
                   and zaman.atanmis_mi(a, gun, saat))
        if sayi > kendi:
            baska_hucre += 1
            baska_kisi_saat += sayi - kendi
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
        # K-50: kac hucre baska ekibin vardiyasindaki (cok ekipli) kisiyle
        # kapatildi, toplam kac kisi-saat. Sessiz kalmasin diye.
        "baska_ekipten_kapsama": {"mod": mod, "hucre": baska_hucre,
                                  "kisi_saat": baska_kisi_saat},
    }


# ----------------------------------------------------------------------
# Yayin kapisi -- #4.5, K-16 / K-20 / K-24
# ----------------------------------------------------------------------

def yayin_kapisi(ihlaller, girdi=None, uygulanmayan=None, eksik_boyutlar=None):
    """Bu plan yayinlanabilir mi, yayinlanamazsa neden.

    Kapi `kabul_edilebilir` alanina bakar, `yasal`a DEGIL. Sebep K-24:
    CAKISMA_YOK yasal bir kural degil (hicbir kanun cakismayi yasaklamiyor)
    ama kabul de edilemez -- imkansizliktir.

    ⚠ "BAKAMADIM" DA KAPIDAN GECEMEZ (T-18, K-49, 1 Ekim)
      16 Eylul'den beri kapi yalniz `ihlaller`e bakiyordu: aktif ama govdesi
      yazilmamis SERT bir kural varken cevap ayni anda "bu kurali kontrol
      edemedim" ve "yayinlayabilirsin" diyordu. Ilke bu dosyanin basinda
      yazili, kapiya bagli degildi. Artik iki kanal daha kapidan gecer:

        uygulanmayan_kurallar       -- govdesi yazilmamis aktif kural
        eksik_boyutlar[denetlenemedi] -- yazilmis kuralin bakilamayan parcasi

      UC KADEME (Mustafa, 1 Ekim):
        SERT + yasal  -> ENGELLER. Firma yasal kontrolu onaylayarak gecemez
                         (K-18, K-20).
        SERT + firma  -> KABUL BEKLER. Yetkili gerekce yazarak kabul eder;
                         kabul `girdi.denetim_disi_kabul` listesinde gelir
                         ({"kod", "gerekce", "onaylayan"}); gerekcesiz kabul
                         kabul degildir.
        YUMUSAK       -> yalniz RAPOR; kapiyi etkilemez.

      `okunmayan_alanlar` (T-19) kapiya BAGLANMADI: o bir girdi alani
      meselesidir, kural denetimi degil; rapor olarak kalir.
    """
    acik_sert = [i for i in ihlaller
                 if i.get("agirlik") == "SERT" and i.get("durum") != "kabul_edildi"
                 and not i.get("gecmis")]          # K-54: olan oldu, kapi saymaz
    engelleyen = [i for i in acik_sert if not i.get("kabul_edilebilir")]
    kabul_bekleyen = [i for i in acik_sert if i.get("kabul_edilebilir")]

    denetlenemeyen = _denetlenemeyen_kurallar(girdi, uygulanmayan, eksik_boyutlar)
    d_engelleyen = [d for d in denetlenemeyen if d["etki"] == "engelliyor"]
    d_bekleyen = [d for d in denetlenemeyen if d["etki"] == "kabul_bekliyor"]
    return {
        "yayinlanabilir": not acik_sert and not d_engelleyen and not d_bekleyen,
        "engelleyen_ihlaller": engelleyen,       # kabul secenegi SUNULMAZ
        "kabul_bekleyen_ihlaller": kabul_bekleyen,  # gerekceyle kabul edilebilir
        # T-18: "bakamadim" satirlari -- her birinde `etki` ve cumle var
        "denetlenemeyen_kurallar": denetlenemeyen,
        "kabul_secenegi_sunulur": (bool(kabul_bekleyen) or bool(d_bekleyen))
                                  and not engelleyen and not d_engelleyen,
        # K-54: donmus gune ait sert ihlaller -- bilgi, engel degil.
        "gecmis_sert_ihlal": len([i for i in ihlaller
                                  if i.get("agirlik") == "SERT" and i.get("gecmis")]),
    }


def _denetlenemeyen_kurallar(girdi, uygulanmayan, eksik_boyutlar):
    """T-18: bakilamayan kural/parca satirlari, kapidaki etkisiyle."""
    if not girdi:
        return []
    tanimlar = {k.get("kod"): k for k in girdi.get("kurallar", []) or []}
    kabuller = {}
    for k in girdi.get("denetim_disi_kabul", []) or []:
        if (k.get("gerekce") or "").strip():
            kabuller[k.get("kod")] = k
    satirlar = []
    for kod in (uygulanmayan or []):
        satirlar.append(_denetlenemeyen_satir(
            tanimlar.get(kod, {"kod": kod}), kabuller, parca=None,
            sebep="dogrulayicida govdesi yok"))
    for e in (eksik_boyutlar or []):
        if not e.get("denetlenemedi"):
            continue
        satirlar.append(_denetlenemeyen_satir(
            tanimlar.get(e["kural"], {"kod": e["kural"]}), kabuller,
            parca=e.get("boyut"), sebep=e.get("sebep", "")))
    return satirlar


def _denetlenemeyen_satir(tanim, kabuller, parca, sebep):
    kod = tanim.get("kod")
    sert = (tanim.get("tur") or "SERT").upper() == "SERT"
    yasal = bool(tanim.get("yasal"))
    ne = "%s kurali%s" % (kod, (" (%s parcasi)" % parca) if parca else "")
    if not sert:
        etki = "rapor"
        mesaj = ("%s aktif ama denetlenemedi (%s); kural yumusak, yayin "
                 "etkilenmez -- yalniz bildirilir" % (ne, sebep))
    elif yasal:
        etki = "engelliyor"
        mesaj = ("%s aktif, SERT ve YASAL ama denetlenemedi (%s): plan bu "
                 "kural icin kontrol edilmedi; yasal kural onaylanarak "
                 "gecilemez, yayin engellendi (T-18, K-49)" % (ne, sebep))
    elif kod in kabuller:
        etki = "kabul_edildi"
        k = kabuller[kod]
        mesaj = ("%s denetlenemedi (%s); yetkili kabul etti: %s"
                 % (ne, sebep, k.get("gerekce")))
    else:
        etki = "kabul_bekliyor"
        mesaj = ("%s aktif ve SERT ama denetlenemedi (%s): plan bu kural icin "
                 "kontrol edilmedi; firma kurali -- yetkili gerekce yazarak "
                 "kabul edebilir, kabul edilene kadar yayinlanamaz (T-18, K-49)"
                 % (ne, sebep))
    satir = {"kod": kod, "parca": parca, "tur": "SERT" if sert else "YUMUSAK",
             "yasal": yasal, "etki": etki, "mesaj": mesaj}
    if etki == "kabul_edildi":
        satir["kabul"] = kabuller[kod]
    return satir
