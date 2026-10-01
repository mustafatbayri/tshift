# -*- coding: utf-8 -*-
"""
IHLAL VAKALARI  --  her kural icin bir kirmizi

NEDEN VAR
  `kural-kapsamasi.py` 28 Eylul'de sunu olctu: 350 kisilik veri setinde
  govdesi yazili 24 kuraldan yalnizca 7'si gercekten zorlaniyor. Kalan 17'si
  raporda YESIL gorunuyor ama bu yesil bir sey kanitlamiyor -- kural calisti,
  ihlal bulamadi, cunku veri onu hic zorlamadi.

  "Plan temiz" ile "bu kural hic sinanmadi" ayni renkte goruntuleniyordu.

NE YAPAR
  Her kural icin, o kurali -- ve YALNIZ onu -- cignemesi gereken kucuk bir
  plan bozmasi tanimlar. Sonra uc seyi birden sinar:

      1. Bozma sonrasi o kural IHLAL YAZIYOR mu   (kural gercekten calisiyor)
      2. Bozma ONCESI temiz miydi                 (ihlal bozmadan geliyor)
      3. Bozma BASKA kurallari da patlatti mi     (vaka dar mi)

  Ucuncusu bilerek bilgilendirici, hata degil: gercek bir plan bozmasi
  cogu zaman birden cok kurali ilgilendirir (7 gun calisan hem HAFTA_TATILI
  hem ARDISIK_CALISMA_GUNU'nu ciginer). Rapor yan etkiyi YAZAR ki vakayi
  okuyan, ihlalin nereden geldigini bilsin.

KULLANIM
  py ihlal-vakalari.py            -> hepsini kostur, tablo yaz
  py ihlal-vakalari.py -v         -> ihlal mesajlarini da yaz
"""

import copy
import io
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as _K                        # noqa: E402

VAKALAR = []

# Govdesi var ama IHLAL URETMEYEN kurallar: vakasi olamaz, bu bir bosluk
# degil. Her satir sebebini soyler.
IHLAL_URETMEZ = {
    "GECE_YARISI_ASAN": "hesaplama kurali (Z-1), zaman modeli uygular; ihlal uretmez (T-67)",
}


def vaka(kod, aciklama):
    """Bir kural icin ihlal vakasi kaydeder."""
    def sar(fn):
        VAKALAR.append((kod, aciklama, fn))
        return fn
    return sar


def _bul(atamalar, kosul):
    for a in atamalar:
        if kosul(a):
            return a
    return None


def _kural(g, kod):
    for k in g.get("kurallar", []):
        if k["kod"] == kod:
            return k
    return None


# ----------------------------------------------------------------------
# Calisan durumu
# ----------------------------------------------------------------------

@vaka("AKTIF_CALISAN", "Pasif calisana vardiya verilir")
def _(g, p):
    pasif = _bul(g["calisanlar"], lambda c: c.get("durum", "aktif") != "aktif")
    ornek = dict(p[0])
    ornek["calisan"] = pasif["id"]
    ornek["ekip"] = pasif["ekipler"][0]
    p.append(ornek)


@vaka("SOZLESME_GECERLI", "Sozlesme hafta baslamadan BITMIS gosterilir")
def _(g, p):
    # ⚠ Ilk yazimda `tip`i "mevsimlik" yapiyordum. Kural TIPE degil
    #   `sozlesme.bitis` TARIHINE bakiyor; vaka yanlis yere vuruyordu.
    #   Kural sessiz kaldi ve ben bunu once MOTOR HATASI sandim.
    kimlik = p[0]["calisan"]
    for c in g["calisanlar"]:
        if c["id"] == kimlik:
            c["sozlesme"] = dict(c["sozlesme"])
            c["sozlesme"]["bitis"] = "2026-10-01"      # hafta 12 Ekim'de


@vaka("ONAYLI_IZIN", "Onayli izin gunune vardiya yazilir")
def _(g, p):
    for c in g["calisanlar"]:
        izin = [z for z in (c.get("izinler") or [])
                if z.get("durum", "onayli") == "onayli"]
        if not izin:
            continue
        gun = izin[0]["gun"]
        t = _bul(g["vardiya_sablonlari"],
                 lambda s: s.get("ekip") == c["ekipler"][0]
                 and gun in s.get("gunler", list(range(7))))
        if not t:
            continue
        p.append({"calisan": c["id"], "ekip": c["ekipler"][0],
                  "sablon": t["id"], "gun": gun,
                  "bas": t["bas"], "bit": t["bit"], "molalar": []})
        return


@vaka("UYGUNLUK_TAKVIMI", "Calisanin kapali gunune vardiya yazilir")
def _(g, p):
    for c in g["calisanlar"]:
        kapali = [u for u in (c.get("uygunluk") or [])
                  if u.get("tip") == "uygun_degil"]
        if not kapali:
            continue
        gun = kapali[0]["gun"]
        t = _bul(g["vardiya_sablonlari"],
                 lambda s: s.get("ekip") == c["ekipler"][0]
                 and gun in s.get("gunler", list(range(7))))
        if not t:
            continue
        p.append({"calisan": c["id"], "ekip": c["ekipler"][0],
                  "sablon": t["id"], "gun": gun,
                  "bas": t["bas"], "bit": t["bit"], "molalar": []})
        return


# ----------------------------------------------------------------------
# Sure sinirlari
# ----------------------------------------------------------------------

@vaka("GUNLUK_AZAMI", "Bir gune 13 saatlik vardiya yazilir (tavan 11)")
def _(g, p):
    a = p[0]
    a["bit"] = a["bas"] + 13
    a["molalar"] = []


@vaka("HAFTALIK_AZAMI", "Bir kisiye yedi gun 10'ar saat yazilir (tavan 45)")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    p[:] = [a for a in p if a["calisan"] != c]
    for gun in range(7):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 9, "bit": 19, "molalar": []})


@vaka("YILLIK_FAZLA_MESAI_TAVANI",
      "Yil ici 268 saat fazla mesaisi olana 6 gun 10'ar saat yazilir (+9 > 270)")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    for k in g["calisanlar"]:
        if k["id"] == c:
            k["yil_ici_fazla_mesai_saat"] = 268
    p[:] = [a for a in p if a["calisan"] != c]
    for gun in range(6):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 9, "bit": 19, "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]})


@vaka("CALISMA_SAATLERI",
      "Musteri hizmetleri calisanina cumartesi 13-22 yazilir (departman 19'da kapanir)")
def _(g, p):
    a = _bul(p, lambda x: x.get("ekip") == "MHIZMET")
    if a is None:
        raise RuntimeError("temel planda MHIZMET atamasi yok")
    c = a["calisan"]
    p[:] = [x for x in p if not (x["calisan"] == c and x["gun"] == 5)]
    p.append({"calisan": c, "ekip": "MHIZMET", "sablon": "M-AKSAM", "gun": 5,
              "bas": 13, "bit": 22, "molalar": [{"bas": 17, "bit": 17.5, "tip": "yemek"}]})


@vaka("HEDEF_ASIMI", "Hedefi 1 olan hucreye ikinci kisi yazilir")
def _(g, p):
    # Hedefi en kucuk hucreyi bul, oraya temel planda olmayan birini ekle.
    hucre = min((t for t in g["talep"] if t.get("hedef")), key=lambda t: t["hedef"])
    ekip, gun, saat = hucre["ekip"], hucre["gun"], hucre["saat"]
    kisiler = [c for c in g["calisanlar"] if ekip in c["ekipler"]
               and c.get("durum", "aktif") == "aktif"]
    mesgul = {a["calisan"] for a in p if a["gun"] == gun}
    bos = next(c for c in kisiler if c["id"] not in mesgul)
    p.append({"calisan": bos["id"], "ekip": ekip, "sablon": "X", "gun": gun,
              "bas": max(0, saat - 4), "bit": saat + 4, "molalar": []})


@vaka("HAFTA_TATILI", "Bir kisi yedi gunun yedisinde de calisir")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    p[:] = [a for a in p if a["calisan"] != c]
    for gun in range(7):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 9, "bit": 14, "molalar": []})


@vaka("ARDISIK_CALISMA_GUNU", "Bir kisi yedi gun ust uste calisir (tavan 6)")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    p[:] = [a for a in p if a["calisan"] != c]
    for gun in range(7):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 9, "bit": 13, "molalar": []})


@vaka("FAZLA_MESAI_TAVANI", "Sozlesme ustu 20 saat fazla mesai yazilir")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    p[:] = [a for a in p if a["calisan"] != c]
    for gun in range(6):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 8, "bit": 19, "molalar": []})


@vaka("PART_TIME_LIMIT", "Yari zamanliya MEVZUAT TAVANININ ustu yazilir")
def _(g, p):
    """⚠ BU VAKA 29 EYLUL'DE YENIDEN YAZILDI (K-39).

    Eski hali "part-time'a bes gun x 9 saat yaz" diyordu ve o zaman ihlal
    sayiliyordu, cunku tavan KISININ SOZLESME SAATIYDI (20/24). Mustafa
    tavani mevzuata bagladi: emsal tam surelinin tamami, 45 saat. 5x8 = 40
    saat artik ihlal DEGIL -- ve vaka SESSIZ kaldi, kural gormez oldu.

    Yeni vaka tavanin USTUNE cikar: 7 gun x 9 net = 63 saat.
    """
    pt = _bul(g["calisanlar"],
              lambda c: c["sozlesme"].get("tip") == "yari_zamanli")
    p[:] = [a for a in p if a["calisan"] != pt["id"]]
    for gun in range(7):
        p.append({"calisan": pt["id"], "ekip": pt["ekipler"][0],
                  "sablon": "X", "gun": gun, "bas": 8, "bit": 18,
                  "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                               "ucretli": False}]})       # 9 net x 7 = 63


@vaka("VARDIYA_ARASI_DINLENME", "Gece vardiyasindan sonra ertesi sabah vardiya")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    p[:] = [a for a in p if a["calisan"] != c]
    p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": 1,
              "bas": 23, "bit": 31, "molalar": []})
    p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": 2,
              "bas": 9, "bit": 17, "molalar": []})


@vaka("CAKISMA_YOK", "Ayni kisiye ayni gun ortusen iki vardiya")
def _(g, p):
    a = p[0]
    p.append({"calisan": a["calisan"], "ekip": a["ekip"], "sablon": "X",
              "gun": a["gun"], "bas": a["bas"] + 1, "bit": a["bas"] + 5,
              "molalar": []})


# ----------------------------------------------------------------------
# Plan butunlugu
# ----------------------------------------------------------------------

@vaka("DONMUS_GUN", "Donmus gune YENI atama yazilir")
def _(g, p):
    a = dict(p[0])
    a["gun"] = g["donmus_gunler"][0]
    a["_yeni"] = True
    p.append(a)


@vaka("KILIT_UYUMU", "Kilitli atama plandan cikarilir")
def _(g, p):
    k = g["kilitler"][0]
    p[:] = [a for a in p
            if not (a["calisan"] == k["calisan"] and a["gun"] == k["gun"])]


# ----------------------------------------------------------------------
# Molalar
# ----------------------------------------------------------------------

@vaka("MOLA_HAKKI", "Dokuz saatlik vardiyadan butun molalar silinir")
def _(g, p):
    a = _bul(p, lambda x: x["bit"] - x["bas"] >= 8)
    a["molalar"] = []


@vaka("MOLA_TIPI_ZORUNLU", "Bir molanin `tip` alani silinir")
def _(g, p):
    a = _bul(p, lambda x: x.get("molalar"))
    a["molalar"][0].pop("tip", None)


@vaka("MOLA_ASGARI_BLOK", "Bes dakikalik mola yazilir (asgari 15)")
def _(g, p):
    a = _bul(p, lambda x: x.get("molalar"))
    a["molalar"][0]["bit"] = a["molalar"][0]["bas"] + 5 / 60.0


@vaka("YEMEK_TEK_BLOK", "Yemek molasi ikiye bolunur (K-14)")
def _(g, p):
    a = _bul(p, lambda x: any(m.get("tip") == "yemek"
                              for m in (x.get("molalar") or [])))
    y = _bul(a["molalar"], lambda m: m.get("tip") == "yemek")
    orta = (y["bas"] + y["bit"]) / 2.0
    son = y["bit"]
    y["bit"] = orta - 0.25
    a["molalar"].append({"bas": orta + 0.25, "bit": son + 0.25,
                         "tip": "yemek"})


@vaka("MOLA_YERLESIMI", "Yemek molasi vardiyanin ilk saatine konur")
def _(g, p):
    a = _bul(p, lambda x: any(m.get("tip") == "yemek"
                              for m in (x.get("molalar") or [])))
    y = _bul(a["molalar"], lambda m: m.get("tip") == "yemek")
    sure = y["bit"] - y["bas"]
    y["bas"] = a["bas"]
    y["bit"] = a["bas"] + sure


@vaka("SAHADA_ASGARI", "Bir ekibin tamami ayni ceyrekte molaya cikar")
def _(g, p):
    k = _kural(g, "SAHADA_ASGARI")
    k["parametreler"] = {"asgari_sahada": 2}
    hedef = [a for a in p if a["ekip"] == "MHIZMET" and a["gun"] == 2]
    for a in hedef:
        a["molalar"] = [{"bas": 14.25, "bit": 14.5, "tip": "dinlenme"}]


@vaka("MOLA_KAPSAMASI", "Yumusak kapsama -- ayni sahne, taban kuralsiz")
def _(g, p):
    hedef = [a for a in p if a["gun"] == 3]
    for a in hedef:
        a["molalar"] = [{"bas": a["bas"] + 3, "bit": a["bas"] + 4,
                         "tip": "yemek"}]


# ----------------------------------------------------------------------
# Kapsama
# ----------------------------------------------------------------------

@vaka("ASGARI_KAPSAMA", "Bir gunun butun atamalari silinir")
def _(g, p):
    p[:] = [a for a in p if a["gun"] != 4]


@vaka("HEDEF_KAPSAMA", "Hedefin altinda kalinir (yumusak)")
def _(g, p):
    p[:] = [a for a in p if a["gun"] != 3]


@vaka("ADALET_DENGESI", "Bir kisiye butun hafta sonu vardiyalari yigilir")
def _(g, p):
    c = p[0]["calisan"]
    ekip = p[0]["ekip"]
    for gun in (5, 6):
        p.append({"calisan": c, "ekip": ekip, "sablon": "X", "gun": gun,
                  "bas": 9, "bit": 17, "molalar": []})


@vaka("GECE_UYGUNLUGU", "Gece calisamayan kisi gece vardiyasina yazilir")
def _(g, p):
    """K-40. Iki sey birden gerekiyor: `gece_calisamaz` bir kisi ve
    `gece_vardiyasi` isaretli bir sablon."""
    gece_sablon = next((t for t in g["vardiya_sablonlari"]
                        if t.get("gece_vardiyasi")), None)
    kisi = next((c for c in g["calisanlar"]
                 if c.get("gece_calisamaz")
                 and gece_sablon and gece_sablon["ekip"] in (c.get("ekipler") or [])),
                None)
    if not (gece_sablon and kisi):
        return
    p.append({"calisan": kisi["id"], "ekip": gece_sablon["ekip"],
              "sablon": gece_sablon["id"], "gun": 2,
              "bas": gece_sablon["bas"], "bit": gece_sablon["bit"],
              "molalar": []})


def _nitelik_vakasi(g, p, kod, alan, parametre_adi, aranan_secici):
    """ROL_KAPSAMASI / YETKINLIK_KAPSAMASI vakalarinin ortak govdesi.

    ⚠ VERI SETINDE GEREKLILIK SATIRI YOK -- VAKA ONU KENDISI YAZIYOR
      Iki kural sahnede `parametreler` alani OLMADAN tanimli: yani aktif
      ama hicbir sey istemiyor. Govde de haklı olarak hicbir sey
      denetlemiyor. Bu, "40 kuralin hepsi tanimli" cumlesinin sinirini
      gosteriyor: TANIMLI olmak ISTEMEK degildir.

      Bu yuzden vaka iki isi birden yapiyor: gereklilik satirini yaziyor
      ve sonra onu bozuyor. Yani su an olculen sey GOVDENIN ATESLENDIGI,
      veri setinin bu kurali ZORLADIGI degil. Ikincisi acik is.

      Ayni tuzak `SAHADA_ASGARI`'de de var: sahnede `asgari_sahada` 0,
      yani o kural da aktif ama hicbir sey istemiyor.
    """
    kural = _kural(g, kod)
    if kural is None:
        return
    hucre = next((t for t in g.get("talep", [])
                  if t.get("ekip") and t.get("gun") is not None
                  and t.get("saat") is not None), None)
    if hucre is None:
        return
    ekip, gun, saat = hucre["ekip"], hucre["gun"], hucre["saat"]

    aranan = aranan_secici(g, ekip)
    if aranan is None:
        return
    tasiyanlar = {c["id"] for c in g["calisanlar"]
                  if ekip in (c.get("ekipler") or [])
                  and (aranan in (c.get(alan) or []) if alan == "yetkinlikler"
                       else c.get(alan) == aranan)}
    if not tasiyanlar:
        return

    kural["parametreler"] = {parametre_adi: aranan, "ekip": ekip,
                             "gun": gun, "saatler": [saat], "asgari": 1}

    # O saati kapsayabilecek butun atamalari kaldir. `gun-1` de dahil:
    # gece yarisini asan bir vardiya onceki gunde baslar ama bu saati
    # kapsayabilir (Z-2).
    p[:] = [a for a in p
            if not (a.get("calisan") in tasiyanlar
                    and a.get("ekip") == ekip
                    and a.get("gun") in (gun - 1, gun))]


@vaka("ROL_KAPSAMASI",
      "Sahnenin KENDI gerekliliginden bir gunun liderleri cikarilir")
def _(g, p):
    """⚠ BU VAKA ARTIK GEREKLILIGI KENDISI YAZMIYOR (T-63 sonrasi).

    30 Eylul'e kadar sahnede gereklilik satiri yoktu, bu yuzden vaka onu
    kendisi yaziyordu -- yani "govde atesliyor mu" olculuyordu, "veri seti
    bu kurali zorluyor mu" degil. Mustafa'nin karariyla sahneye gercek bir
    satir kondu ("gunduz saatlerinde 1 lider"), dolayisiyla vaka artik
    yalnizca PLANI bozuyor: bir gunun liderlerini plandan cikarir.

    Vaka DAR: tek gun, tek ekip. Butun haftaya dokunmak, ihlali gurultuye
    bogar ve vakanin ne olctugunu belirsizlestirir.
    """
    kural = next((k for k in g.get("kurallar", [])
                  if k.get("kod") == "ROL_KAPSAMASI"
                  and (k.get("parametreler") or {}).get("rol")), None)
    if kural is None:
        return
    par = kural["parametreler"]
    ekip, rol = par.get("ekip"), par["rol"]
    tasiyanlar = {c["id"] for c in g["calisanlar"]
                  if c.get("operasyonel_rol") == rol
                  and (ekip is None or ekip in (c.get("ekipler") or []))}
    if not tasiyanlar:
        return
    gunler = sorted({a["gun"] for a in p
                     if a.get("calisan") in tasiyanlar
                     and (ekip is None or a.get("ekip") == ekip)})
    if not gunler:
        return
    gun = gunler[0]
    p[:] = [a for a in p
            if not (a.get("calisan") in tasiyanlar
                    and (ekip is None or a.get("ekip") == ekip)
                    and a.get("gun") in (gun - 1, gun))]


@vaka("YETKINLIK_KAPSAMASI",
      "Yetkinlik gerekliligi yazilir, o saatte sahada tasiyan birakilmaz")
def _(g, p):
    def _yetkinlik_sec(g, ekip):
        for c in g["calisanlar"]:
            if ekip in (c.get("ekipler") or []):
                for y in (c.get("yetkinlikler") or []):
                    return y
        return None
    _nitelik_vakasi(g, p, "YETKINLIK_KAPSAMASI", "yetkinlikler",
                    "yetkinlik", _yetkinlik_sec)


@vaka("GECE_VARDIYASI_AZAMI",
      "Bir kisiye gece penceresine 10 saat dusen molasiz vardiya yazilir")
def _(g, p):
    """K-26. YASAL sinir: gece penceresine dusen net calisma 7,5 saat.

    ⚠ VERI SETININ SABLONLARI BU KURALI ZORLAMIYOR -- en uzun gece
      ortusmesi 7,00 saat. Bu yuzden vaka yeni bir atama ekliyor:
      20:00-06:00, molasiz, o gun baska isi olmayan bir kisiye.
      Sahnenin sektoru istisna disi, yani sinir herkes icin yururlukte.

    Vaka DAR: tek kisi, tek gece.
    """
    dolu = {(a["calisan"], a["gun"]) for a in p}
    for c in g["calisanlar"]:
        if c.get("durum", "aktif") != "aktif" or c.get("gece_calisamaz"):
            continue
        for gun in (2, 3, 4):
            if any((c["id"], d) in dolu for d in (gun - 1, gun, gun + 1)):
                continue
            p.append({"calisan": c["id"], "ekip": c["ekipler"][0],
                      "sablon": "VAKA-GECE", "gun": gun,
                      "bas": 20, "bit": 30, "molalar": []})
            return


@vaka("ASGARI_VARDIYA_SURESI", "Bir atama 3 saate kisaltilir")
def _(g, p):
    """Veri setinde en kisa sablon tam 4 saat; kural isirmaz. Vaka bir
    atamanin bitisini baslangicindan 3 saat sonraya ceker. DAR: tek atama."""
    a = next((a for a in p if a["bit"] - a["bas"] >= 4), None)
    if a is None:
        return
    a["bit"] = a["bas"] + 3
    a["molalar"] = []


@vaka("ARDISIK_GECE_LIMIT", "Bir kisiye dort gece ust uste yazilir")
def _(g, p):
    """Gece isaretli bir sablonla, gecesi olmayan bir kisiye 0-3. gunler.

    DAR: tek kisi. Kisinin o gunlerdeki baska atamalari silinir ki
    `CAKISMA_YOK` gibi yan ihlaller vakayi bulandirmasin.
    """
    gece = next((t for t in g["vardiya_sablonlari"]
                 if t.get("gece_vardiyasi")), None)
    if gece is None:
        return
    kisi = next((c for c in g["calisanlar"]
                 if c.get("durum", "aktif") == "aktif"
                 and not c.get("gece_calisamaz") and not c.get("izinler")
                 and gece["ekip"] in (c.get("ekipler") or [])), None)
    if kisi is None:
        return
    p[:] = [a for a in p if not (a["calisan"] == kisi["id"] and a["gun"] <= 4)]
    for d in range(4):
        p.append({"calisan": kisi["id"], "ekip": gece["ekip"],
                  "sablon": gece["id"], "gun": d,
                  "bas": gece["bas"], "bit": gece["bit"], "molalar": []})


@vaka("GECE_POSTASI_DEVRI",
      "Bu hafta gece calisan birinin haftasi geceye cevrilir, gecen hafta "
      "tam bilinen bir gece haftasi eklenir")
def _(g, p):
    """YASAL -- Is K. md. 69 / Postalar Yon. md. 8 (K-25, K-45).

    Sahne TEK HAFTA ve gecmissiz: kural temel planda ISIRAMAZ. Vaka iki
    seye dokunur:
      1. Gecen hafta: bes gece kaydi (pazartesi-cuma) ve haftanin TAMAMI
         bilinen -- K-45 cogunluk olcusu yarim bilinen haftada hesaplanmaz.
      2. Bu hafta: kisinin gece disi atamalari silinir ki bu hafta da gece
         haftasi olsun (calisma saatlerinin yarisindan cogu gece).
    Cuma gecesi (gun -3) pazartesiye 48+ saat uzak: pazartesi sinirindaki
    dinlenme ve ardisik gece kurallari etkilenmez.

    ⚠ GECE = YONETMELIGIN TANIMI (md. 7/2), firma isareti DEGIL. Isarete
      baksaydik B-AKSAM'i (15:15-24:00, isaretli) secebilirdik -- o yasal
      olarak gece degil ve kural hakli olarak susardi. Secim burada,
      dogrulayicidan bagimsiz hesaplanir.
    """
    def _yasal_gece(t):
        bas, bit = float(t["bas"]), float(t["bit"])
        gece = sum(max(0.0, min(bit, w + 10) - max(bas, w))
                   for w in (-4.0, 20.0, 44.0))
        return 2 * gece > bit - bas

    geceler = {t["id"] for t in g["vardiya_sablonlari"] if _yasal_gece(t)}
    a = next((a for a in p if a.get("sablon") in geceler), None)
    if a is None:
        return
    kimlik = a["calisan"]
    p[:] = [x for x in p if x["calisan"] != kimlik or x.get("sablon") in geceler]
    c = next(c for c in g["calisanlar"] if c["id"] == kimlik)
    c["gecmis_vardiyalar"] = [{"gun": d, "bas": 23, "bit": 31}
                              for d in (-7, -6, -5, -4, -3)]
    c["gecmis_bilinen_gunler"] = list(range(-7, 0))


@vaka("ARDISIK_HAFTA_SONU_LIMIT",
      "Bu hafta cumartesi ve pazari calisan birine onceki iki TAM hafta "
      "sonu eklenir")
def _(g, p):
    """Azami 2: bu hafta sonu UCUNCU tam hafta sonu olur (K-46: iki gun de).

    Kisinin plandaki cumartesi ve pazar atamalari yoksa eklenir (kendi
    ekibinin gunduz sablonuyla, 10:00-18:00). Gecmis: iki onceki hafta
    sonunun dort gunu, 10:00-18:00 -- pazartesi sinirina 14+ saat, dinlenme
    ve hafta tatili etkilenmez. DAR: tek kisi.
    """
    hs = {}
    for a in p:
        if a["gun"] in (5, 6):
            hs.setdefault(a["calisan"], set()).add(a["gun"])
    kimlik = next((k for k, gunler in hs.items() if gunler >= {5, 6}), None)
    if kimlik is None:
        kimlik = next(iter(hs))
        ekip = next(a["ekip"] for a in p if a["calisan"] == kimlik)
        for d in (5, 6):
            if d not in hs[kimlik]:
                p.append({"calisan": kimlik, "ekip": ekip, "sablon": "VAKA-HS",
                          "gun": d, "bas": 10, "bit": 18, "molalar": []})
    c = next(c for c in g["calisanlar"] if c["id"] == kimlik)
    c.setdefault("gecmis_vardiyalar", []).extend(
        [{"gun": d, "bas": 10, "bit": 18} for d in (-9, -8, -2, -1)])


@vaka("SAAT_DENGESI", "Tam zamanli calisanin vardiyalarinin yarisi silinir")
def _(g, p):
    """K-39. Sozlesme saati doldurulmazsa ihlal.

    ⚠ Vaka DAR olmali: butun tam zamanlilara dokunmak yerine BIR kisinin
      atamalarinin yarisini siliyoruz. Genis bir bozma, kuralin gercekten
      o sebepten yandigini kanitlamaz.
    """
    tz = next((c for c in g["calisanlar"]
               if (c.get("sozlesme") or {}).get("tip") == "tam_zamanli"
               and c.get("durum", "aktif") == "aktif"
               and sum(1 for a in p if a["calisan"] == c["id"]) >= 4), None)
    if not tz:
        return
    onun = [a for a in p if a["calisan"] == tz["id"]]
    birak = set(id(a) for a in onun[:len(onun) // 2])
    p[:] = [a for a in p if a["calisan"] != tz["id"] or id(a) in birak]


# ----------------------------------------------------------------------
# Kosturucu
# ----------------------------------------------------------------------

def _dokunulan(once, sonra):
    """Vakanin hangi calisanlara dokundugu -- eklenen/silinen/degisen atamalar."""
    def anahtar(a):
        return (a["calisan"], a["gun"], a.get("bas"), a.get("bit"),
                json.dumps(a.get("molalar") or [], sort_keys=True))
    o, y = {anahtar(a) for a in once}, {anahtar(a) for a in sonra}
    return {k[0] for k in (o ^ y)}


def kostur(g0, temel_plan, ayrintili=False):
    from importlib import import_module
    kk = import_module("kural-kapsamasi".replace("-", "_")) \
        if False else None   # kaba_plan disaridan gelir

    temel = degerlendir(g0, temel_plan)
    temel_kodlar = {}
    for i in temel.get("ihlaller", []):
        temel_kodlar[i["kural"]] = temel_kodlar.get(i["kural"], 0) + 1

    print("TEMEL PLAN: %d atama, %d ihlal (%d ayri kural)"
          % (len(temel_plan), len(temel.get("ihlaller", [])), len(temel_kodlar)))
    print()
    print("%-26s %-9s %-9s %s" % ("KURAL", "TEMELDE", "VAKADA", "SONUC"))
    print("-" * 74)

    basarili = eksik = 0
    for kod, aciklama, fn in VAKALAR:
        g = copy.deepcopy(g0)
        p = copy.deepcopy(temel_plan)
        try:
            fn(g, p)
        except Exception as e:
            print("%-26s %-9s %-9s VAKA HATASI: %s"
                  % (kod, "-", "-", str(e)[:28]))
            eksik += 1
            continue
        r = degerlendir(g, p)
        sayi = {}
        for i in r.get("ihlaller", []):
            sayi[i["kural"]] = sayi.get(i["kural"], 0) + 1
        once, sonra = temel_kodlar.get(kod, 0), sayi.get(kod, 0)
        # ⚠ SAYI DEGIL FARK yeterli degildi: temel plan zaten kusurlu, bazi
        #   kurallar 190+ ihlalle basliyordu ve vakanin ekledigi tek ihlal
        #   gurultude kayboluyordu. Vakanin DOKUNDUGU kisiyi ayrica izleriz.
        dokunulan = _dokunulan(temel_plan, p)
        if dokunulan:
            oz_once = sum(1 for i in temel.get("ihlaller", [])
                          if i["kural"] == kod and i.get("calisan") in dokunulan)
            oz_sonra = sum(1 for i in r.get("ihlaller", [])
                           if i["kural"] == kod and i.get("calisan") in dokunulan)
            if oz_sonra > oz_once:
                once, sonra = oz_once, oz_sonra
        if sonra > once:
            sonuc = "KIRMIZI YANDI"
            basarili += 1
        elif sonra:
            # Kural temel planda ZATEN atesleniyor: kapsama acisindan
            # sinanmis sayilir, ama vaka DAR degil -- ikisi ayri sey.
            sonuc = "temelde zaten sinaniyor (vaka dar degil)"
            basarili += 1
        else:
            sonuc = "SESSIZ -- kural bu bozmayi GORMUYOR"
            eksik += 1
        print("%-26s %-9s %-9s %s" % (kod, once or "-", sonra or "-", sonuc))
        if ayrintili:
            print("      vaka: %s" % aciklama)
            yan = sorted(k for k in sayi
                         if k != kod and sayi[k] > temel_kodlar.get(k, 0))
            if yan:
                print("      yan etki: %s" % ", ".join(yan))
            ornek = next((i for i in r.get("ihlaller", [])
                          if i["kural"] == kod), None)
            if ornek:
                print("      mesaj: %s" % ornek.get("mesaj", "")[:90])

    # ⚠ 30 Eylul -- BU ARACIN KENDI BOSLUGU
    #   Ozet eskiden `basarili / len(VAKALAR)` yaziyordu: yani "yazdigim
    #   vakalarin kaci atesledi". Govdesi yazili ama VAKASI OLMAYAN bir kural
    #   bu paydada hic gorunmuyordu -- arac "EKSIK: 0" diyordu ve kapsama
    #   tam sanilyordu. 29 Eylul'de "26 kuralin tamami kendi vakasinda
    #   kirmizi yaniyor, eksik sifir" diye yazdigim cumlenin dayanagi buydu.
    #
    #   Evren artik dogrulayicinin KAYIT sozlugu: govdesi yazili her kural.
    #   Vakasi olmayan bir govde de bir bosluktur, cunku o kural icin
    #   "kirmizi yanabiliyor mu" sorusu hic sorulmamis olur.
    vakasiz = sorted(set(_K.KAYIT) - {k for k, _, _ in VAKALAR})
    for kod in vakasiz:
        if kod in IHLAL_URETMEZ:
            # Bilerek vakasiz: kural hesaplama kuralidir, kirmizi yanamaz.
            print("%-26s %-9s %-9s bilerek vakasiz -- %s"
                  % (kod, "-", "-", IHLAL_URETMEZ[kod]))
            continue
        print("%-26s %-9s %-9s VAKASI YOK -- hic sinanmadi" % (kod, "-", "-"))
        eksik += 1

    print("-" * 74)
    print("GOVDESI YAZILI KURAL : %d  (ihlal uretmeyen %d)"
          % (len(_K.KAYIT), len([k for k in _K.KAYIT if k in IHLAL_URETMEZ])))
    print("VAKASI OLAN          : %d" % len({k for k, _, _ in VAKALAR}))
    print("KIRMIZI YANAN        : %d" % basarili)
    print("EKSIK                : %d" % eksik)
    if eksik:
        print()
        print("⚠ 'SESSIZ' olan her satir bir bosluktur: kural tanimli, govdesi")
        print("  yazili, ama bu bozmayi gormuyor. 'zaten kirmiziydi' ise vakanin")
        print("  DAR olmadigini soyler -- temel plan o kurali zaten ciginiyor.")
        print("  'VAKASI YOK' ise soru hic sorulmamis.")
    return basarili, eksik


if __name__ == "__main__":
    ad = sys.argv[sys.argv.index("--sahne") + 1] if "--sahne" in sys.argv \
        else "_sahne-S30-95.json"
    sahne = os.path.join(BURASI, "fikstur", ad)
    g0 = json.load(io.open(sahne, encoding="utf-8"))
    sys.path.insert(0, BURASI)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kk", os.path.join(BURASI, "kural-kapsamasi.py"))
    kk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kk)
    temel = kk.kaba_plan(g0)
    kostur(g0, temel, ayrintili="-v" in sys.argv)
