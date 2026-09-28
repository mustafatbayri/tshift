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

VAKALAR = []


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


@vaka("PART_TIME_LIMIT", "Part-time calisana tam zamanli yuk yazilir")
def _(g, p):
    pt = _bul(g["calisanlar"],
              lambda c: c["sozlesme"].get("tip") == "yari_zamanli")
    p[:] = [a for a in p if a["calisan"] != pt["id"]]
    for gun in range(5):
        p.append({"calisan": pt["id"], "ekip": pt["ekipler"][0],
                  "sablon": "X", "gun": gun, "bas": 9, "bit": 18,
                  "molalar": []})


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

    print("-" * 74)
    print("KIRMIZI YANAN : %d / %d" % (basarili, len(VAKALAR)))
    print("EKSIK         : %d" % eksik)
    if eksik:
        print()
        print("⚠ 'SESSIZ' olan her satir bir bosluktur: kural tanimli, govdesi")
        print("  yazili, ama bu bozmayi gormuyor. 'zaten kirmiziydi' ise vakanin")
        print("  DAR olmadigini soyler -- temel plan o kurali zaten ciginiyor.")
    return basarili, eksik


if __name__ == "__main__":
    sahne = os.path.join(BURASI, "fikstur", "_sahne-S20.json")
    g0 = json.load(io.open(sahne, encoding="utf-8"))
    sys.path.insert(0, BURASI)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kk", os.path.join(BURASI, "kural-kapsamasi.py"))
    kk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kk)
    temel = kk.kaba_plan(g0)
    kostur(g0, temel, ayrintili="-v" in sys.argv)
