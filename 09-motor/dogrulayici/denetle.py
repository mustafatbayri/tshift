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
         "agirliklar"),
    "calisanlar": ("id", "ekipler", "sozlesme", "izinler", "uygunluk",
                   "devir_yuk", "yetkinlikler", "operasyonel_rol"),
    "calisanlar.sozlesme": ("tip", "haftalik_saat"),
    "calisanlar.izinler": ("gun", "durum"),
    "calisanlar.uygunluk": ("tip", "gun", "bas", "bit"),
    "vardiya_sablonlari": ("id", "bas", "bit", "mola_dk", "mola_penceresi",
                           "gunler"),
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
# T-19 (kapandi), gecmis_vardiyalar T-28 (acik, oncelik 1).
SEBEPLER = {
    ("talep", "gunler"):
        "gruplu talep kisayolu; sartname #11.2 hucre basina bir satir ister (T-19)",
    ("talep", "saatler"):
        "gruplu talep kisayolu; sartname #11.2 hucre basina bir satir ister (T-19)",
    ("calisanlar", "tercihler"):
        "sartname #11.2'de tanimli, motorda tek satiri yok -- tercih plana etki etmez",
    ("calisanlar", "kural_degerleri"):
        "kisiye ozel kural degeri okunmuyor; herkese genel kural uygulanir",
    ("calisanlar", "gecmis_vardiyalar"):
        "lookback okunmuyor; hafta sinirini asan dinlenme ihlali gorulmez (T-28)",
    ("sabit_atamalar", "bas"):
        "motor sabit atamayi `sablon` kimliginden esliyor; bas/bit okunmuyor",
    ("sabit_atamalar", "bit"):
        "motor sabit atamayi `sablon` kimliginden esliyor; bas/bit okunmuyor",
    ("sabit_atamalar", "ekip"):
        "sabit atamanin ekibi okunmuyor; ekip calisanin kendi listesinden gelir",
    ("calisanlar.izinler", "tum_gun"):
        "izin her zaman TUM GUN sayiliyor; yarim gun izin tam gun gibi engeller",
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


def _eksik_boyutlar(girdi):
    """Aktif bir kuralin, govdesi olmayan boyutlari.

    Kuralin KENDISI yazilmis ama bir PARCASI yazilmamis olabilir --
    ADALET_DENGESI'nin 'saat' boyutu boyle (T-13). `uygulanmayan_kurallar`
    bunu goremez, cunku kural listede var. Ayri bir alan gerekiyor:
    yoksa kural 'yazilmis' gorunur, bir boyutu sessizce atlanir.
    """
    eksik = []
    for tanim in _aktif_kurallar(girdi):
        if tanim.get("kod") != "ADALET_DENGESI":
            continue
        for boyut in (tanim.get("parametreler") or {}).get(
                "boyutlar", ["gece", "hafta_sonu", "saat"]):
            if kurallar._boyut_sayaci(boyut) is None:
                eksik.append({"kural": "ADALET_DENGESI", "boyut": boyut,
                              "sebep": "sayilabilir boyut degil; T-13"})
    return eksik


# ----------------------------------------------------------------------
# Metrikler -- #11.3
# ----------------------------------------------------------------------

def _metrikler(girdi, atamalar, ihlaller):
    sert = [i for i in ihlaller if i.get("agirlik") == "SERT"]
    hucre = kapsama_yuzdeleri(girdi, atamalar)
    toplam_net = sum(zaman.net_saat(a) for a in atamalar)

    fazla = 0.0
    kisi_saat = {}
    for a in atamalar:
        kisi_saat[a["calisan"]] = kisi_saat.get(a["calisan"], 0.0) + zaman.net_saat(a)
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
