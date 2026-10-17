# -*- coding: utf-8 -*-
"""
VARDIYA KAYMASI -- K-73 (Mustafa, 17 Ekim 2026)

NEDEN VAR
  Mustafa (17 Ekim 14:46): "Insanlar plani duzenlerken vardiya dahi kaydirabilir.
  ... oglen 1'deki vardiyada kisi eksik ya, o kisi eksigini yasal kurallari da
  dikkate alarak 2 kisinin mesaisini 2 saat uzatir, bir sonraki mesaiye gelecek
  kisinin vardiyasini 2 saat erken baslatir."

  Motorda vardiya SABIT SABLONDU (09-18, molasi dahil); karar degiskeni yalniz
  (kisi, gun, sablon). Bir atamaya "2 saat erken basla" ya da "2 saat gec bit"
  diyecek hicbir sey yoktu. Bu yuzden raporlu bir gunun tek caresi YENI BIR
  BEDENDI (izinli olani cagirmak, baska takimdan birini almak); beden yoksa
  "cozumsuz". Insan planlamaci ise once komsu vardiyalari kaydirir.

NASIL -- TURETILMIS SABLON
  Her kayma bir yeni sablondur: tabanin ERKEN baslayan ve/veya GEC biten
  kopyasi. Motor icin yeni bir sablon; kisiye gun basina yine tek vardiya
  atanir (`_gunde_tek_vardiya`), yalniz secenek cogalir. Butun yasal kurallar
  (gunluk 11 saat, iki vardiya arasi 11 saat dinlenme, gece vardiyasi 7,5
  saat, haftalik 45 ustu fazla mesai, yillik 270, departman acik saatleri,
  kisinin uygunluk penceresi) ZATEN sablonun baslangic ve bitisine bakar --
  kopyalarda kendiliginden isler, yeni kural kodu yok. Ciktidaki atama kendi
  `bas`/`bit`ini tasir; bagimsiz dogrulayici kaymis vardiyayi aynen denetler.

  Kopya YALNIZCA su kisi-gunler icin uretilir (`kisiler` + `gunler` alanlari):
  etkilenen (ekip, gun) ciftlerinde MEVCUT PLANDA calisan kisiler, o gun,
  kendi vardiyalarinin kopyasi. Yani kayma "elindeki vardiyayi uzat/kaydir"
  demektir; yeni beden eski yoldan (taban sablonlar) gelir.

  SINIR -- Mustafa (17 Ekim 14:52): "En fazla kaymayi da kafamiza gore
  belirlememeliyiz; olcumler karar vermeli. Motor elindeki veriyle bu karari
  vermeli." Kayma alani yalniz YASAL sinirla kirpilir (net saat <= GUNLUK_AZAMI,
  varsayilan 11); kac saat kayilacagina puanlama karar verir (sozlesme ustu
  saatin bedeli: tam zamanlida FAZLA_MESAI, yari zamanlida FAZLA_SURELER --
  K-73 olcum kalemi). `tavan_saat` yalniz OLCUM icin (tavan 1 / 2 / sinirsiz
  kiyasi); urunde firma isterse koyar, varsayilan yok.
  Adim 1 saat: talep ve kapsama saatlik hucre; yarim saatlik kayma kapsamaya
  katki vermez ama ucret yazar, motor zaten secmezdi.

  URUN: firma ayari, varsayilan KAPALI; sifirdan planda kapali (500 kisilik
  modeli katlardi: 647 bin degisken). Edit akisinda onay sorusu ("vardiya
  kaydirmaya izin veriyor musunuz?"), cevaba gore `kayma_ekle` cagrilir.
  Herkes uzatmaya acik varsayilir; kisinin sozlesme penceresi `uygunluk`
  (uygun_degil gun+saat) ile verilirse kopya o pencereyi kendiliginden tanir.

KULLANIM
  etk = etkilenen_bul(girdi, mevcut_plan, [(kisi, gun), ...])   # raporlu -> (ekip, gun)
  h = kayma_ekle(girdi, etk)                                     # yeni girdi (kopya)
  c = coz(h, ayar)                                               # motor
  degerlendir(h, c["atamalar"])                                  # dogrulayici AYNI girdiyle
  kayma_ozeti(c["atamalar"])                                     # kim kac saat kaydi
"""

import copy

from .model import _gece_sablonu, _kural, _net_saat, _par

AYIRAC = "~k~"


def _sablon_bul(sablonlar, satir):
    """Mevcut plan satirinin sablonu: once `sablon` kimligi, yoksa ekip + bas + bit."""
    tid = satir.get("sablon")
    if tid is not None and tid in sablonlar:
        return sablonlar[tid]
    for t in sablonlar.values():
        if satir.get("ekip") is not None and t.get("ekip") is not None and t.get("ekip") != satir.get("ekip"):
            continue
        if t.get("bas") == satir.get("bas") and t.get("bit") == satir.get("bit"):
            return t
    return None


def etkilenen_bul(girdi, mevcut_plan, bozulma):
    """(kisi, gun) bozulmalarindan etkilenen (ekip, gun) ciftleri -- raporlu kisinin o gun
    mevcut planda calistigi ekip(ler). Planda o gun satiri yoksa cift uretilmez."""
    sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari") or []}
    kisiler = {c["id"]: c for c in girdi.get("calisanlar") or []}
    cikan = []
    for kid, gun in bozulma:
        for a in mevcut_plan or []:
            if a.get("calisan") != kid or int(a.get("gun", -1)) != int(gun):
                continue
            ekip = a.get("ekip")
            if ekip is None:
                t = _sablon_bul(sablonlar, a)
                ekip = t.get("ekip") if t else None
            if ekip is None:
                c = kisiler.get(kid) or {}
                ekip = c.get("birincil_ekip") or ((c.get("ekipler") or [None])[0])
            if ekip is not None and (ekip, int(gun)) not in cikan:
                cikan.append((ekip, int(gun)))
    return cikan


def kayma_azami_saat(girdi, taban):
    """Bu tabanin kopyasi en fazla kac saat uzayabilir: GUNLUK_AZAMI (net, varsayilan 11)
    eksi tabanin net saati, asagi yuvarlanir; eksi ise 0."""
    gunluk = float(_par(_kural(girdi, "GUNLUK_AZAMI"), "azami_saat", 11))
    return max(0, int(gunluk - _net_saat(taban) + 1e-9))


def kayma_sekilleri(azami):
    """(erken, gec) ciftleri, saat; (0, 0) yok; erken + gec <= azami. Siralama kararli."""
    return [(e, u) for toplam in range(1, azami + 1)
            for e in range(toplam + 1) for u in [toplam - e]]


def kayma_kimligi(taban_id, kisi, gun, erken, gec):
    return "%s%s%s~g%d~e%d~u%d" % (taban_id, AYIRAC, kisi, gun, erken, gec)


def kayma_sablonlari(girdi, mevcut_plan, etkilenen, tavan_saat=None):
    """Turetilmis sablonlar. `etkilenen`: [(ekip, gun)]. Dönen liste girdiye EKLENIR."""
    sablonlar = {t["id"]: t for t in girdi.get("vardiya_sablonlari") or []}
    kisiler = {c["id"]: c for c in girdi.get("calisanlar") or []}
    etk = {(e, int(g)) for e, g in etkilenen}
    cikan, gorulen = [], set()
    for a in mevcut_plan or []:
        if a.get("donmus"):
            continue
        gun = int(a.get("gun", -1))
        taban = _sablon_bul(sablonlar, a)
        if taban is None or taban.get("kayma"):
            continue
        ekip = a.get("ekip") if a.get("ekip") is not None else taban.get("ekip")
        if (ekip, gun) not in etk or a.get("calisan") not in kisiler:
            continue
        kisi = a["calisan"]
        anahtar = (kisi, gun, taban["id"])
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        azami = kayma_azami_saat(girdi, taban)
        if tavan_saat is not None:
            azami = min(azami, int(tavan_saat))
        for erken, gec in kayma_sekilleri(azami):
            bas = float(taban["bas"]) - erken
            bit = float(taban["bit"]) + gec
            if bas < 0:
                continue                      # gun oncesine tasan baslangic modelde yok
            t = copy.deepcopy(taban)
            t.pop("gece_vardiyasi", None)     # saatler degisti; isaret yeniden hesaplanir
            gece, _ = _gece_sablonu(dict(t, bas=bas, bit=bit))
            t.update({"id": kayma_kimligi(taban["id"], kisi, gun, erken, gec),
                      "bas": bas, "bit": bit,
                      "gunler": [gun], "kisiler": [kisi],
                      "gece_vardiyasi": bool(gece) or bool(taban.get("gece_vardiyasi")),
                      "kayma": {"taban": taban["id"], "kisi": kisi, "gun": gun,
                                "erken": erken, "gec": gec, "saat": erken + gec}})
            cikan.append(t)
    return cikan


def kayma_ekle(girdi, etkilenen, tavan_saat=None, mevcut_plan=None):
    """Girdinin KOPYASI + turetilmis sablonlar. `mevcut_plan` verilmezse girdininki.
    Etkilenen cift yoksa ya da mevcut plan yoksa kopya degismeden doner."""
    h = copy.deepcopy(girdi)
    plan = mevcut_plan if mevcut_plan is not None else h.get("mevcut_plan")
    yeni = kayma_sablonlari(h, plan, etkilenen, tavan_saat)
    if yeni:
        h["vardiya_sablonlari"] = list(h.get("vardiya_sablonlari") or []) + yeni
    h["_kayma"] = {"etkilenen": [[e, int(g)] for e, g in etkilenen], "tavan_saat": tavan_saat,
                   "sablon": len(yeni)}
    return h


def kayma_ozeti(atamalar):
    """Plandaki kaymalar: {kisi_sayisi, toplam_saat, en_buyuk_saat, dagilim{saat: adet}, satirlar}."""
    satirlar = [dict(a["kayma"], calisan=a.get("calisan"), bas=a.get("bas"), bit=a.get("bit"))
                for a in atamalar or [] if a.get("kayma")]
    dagilim = {}
    for s in satirlar:
        dagilim[s["saat"]] = dagilim.get(s["saat"], 0) + 1
    return {"kisi_sayisi": len({s["calisan"] for s in satirlar}),
            "atama_sayisi": len(satirlar),
            "toplam_saat": sum(s["saat"] for s in satirlar),
            "en_buyuk_saat": max([s["saat"] for s in satirlar] or [0]),
            "dagilim": {str(k): dagilim[k] for k in sorted(dagilim)},
            "satirlar": satirlar}
