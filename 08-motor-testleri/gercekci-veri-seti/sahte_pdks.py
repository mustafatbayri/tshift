# -*- coding: utf-8 -*-
"""
SAHTE PDKS -- gecmis veri GERCEKTE nasil gelecek (T-28'in ikinci asamasi)

MUSTAFA'NIN ONERISI (30 Eylul)
  "Veya kicimizdan bir pdks verisi uretiriz, plana %80-85 uyumlu olarak
   gerceklesmis, ve bunun uzerine yeni bir plan yapariz."

NEDEN GEREKLI
  `iki-hafta-olc.py` gecmisi PLANDAN kuruyor: tam ve kusursuz. Gercekte
  gecmis PDKS'ten gelecek ve iki bakimdan farkli olacak:
    1. PLANDAN SAPAR  -- gelmeyen, gec cikan, vardiya degistiren, cagrilan
    2. EKSIKTIR       -- kart okutulmayan gun hic kayit uretmez

  K-42 bu ikinciyi karara bagladi: kayit calisildigini kanitlar, kaydin
  yoklugu hicbir sey kanitlamaz; bilinmeyen gun kisit yaratmaz ama sonucu
  degistirebilecekse `gecmis_eksik` kanalinda RAPORLANIR.

  Bu aracin asil sorusu: O RAPOR YETIYOR MU? Eksik gecmisle yapilan planda,
  GERCEK gecmise gore ihlal olan her durum, raporda o kisi ve kural icin
  bir satirla haber verilmis mi -- yoksa sessizce mi kaciyor?

ORANLAR -- NEREDEN GELDI, ACIKCA
  ⚠ `06-veri/anonim/` BOS. Gercek veriden olcum YAPILMADI. `06-veri/ham/`'a
    bakilmadi ve bakilmayacak. Elde yalniz belgelenmis turetilmis
    istatistikler var (`00-DEVIR/07-GERCEK-VERI-BULGULARI.md`, P-1):
      * giris/cikis kaydi satirlarin %18'inde; CAGRI MERKEZINDE %46
      * 781 calisanin 411'inde (%53) hic kayit yok
  Asagidaki varsayilanlar bu iki sayidan ve Mustafa'nin %80-85 cumlesinden
  turetildi; geri kalan her oran VARSAYIMDIR ve oyle isaretlidir.

    uyum         0.825  Mustafa: "%80-85 uyumlu" -- planli vardiyalarin bu
                        kadari AYNEN gerceklesir
    devamsizlik  0.05   VARSAYIM -- sapmalarin bir kismi gelmemek
    kaydirma_dk  15..60 VARSAYIM -- geri kalan sapma: gec giris / gec cikis
    ek_vardiya   0.03   VARSAYIM -- planli bos gunde cagrilan kisi orani
    kayitsiz     0.30   VARSAYIM -- cagri merkezinde hic kaydi olmayan kisi
                        (genel oran %53; cagri merkezinde daha dusuk)
    kayit_orani  0.66   kaydi olan kiside calisilan gunun okutulma orani.
                        0.70 x 0.66 ~ %46 -- cagri merkezi satirlariyla ayni
                        mertebe (satir oranina bos gunler de girer; birebir
                        karsilik degil, MERTEBE)

  ⚠ BILINEN GUN = KAYDI OLAN GUN (K-42'nin ruhu). Planli bos gun
    "calismadi" diye BILINMEZ: kart okutulmamis olabilir. Entegrasyon
    katmani bunu farkli yorumlarsa (ornegin PDKS satirinda MS 00:00 ise
    "bilinen bos gun") sonuc degisir -- o bir URUN kararidir, burada yok.

KOSTURMA (uzun: iki cozum, ~8 dk)
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py sahte_pdks.py
"""

import collections
import copy
import importlib.util
import io
import json
import os
import random
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

VARSAYILAN = {
    "uyum": 0.825,
    "devamsizlik": 0.05,
    "kaydirma_dk": (15, 30, 45, 60),
    "ek_vardiya": 0.03,
    "kayitsiz": 0.30,
    "kayit_orani": 0.66,
}
TOHUM = 20260930

# Kayip sinir ihlallerini hangi rapor satirinin haber vermesi gerekir.
# CAKISMA_YOK'un kendi rapor satiri yok: pazar gecesinin pazartesiye tasmasi
# pazartesi dinlenme kontrolunun yapilamadigini yazan satirla haber verilir.
HABERCI = {"CAKISMA_YOK": "VARDIYA_ARASI_DINLENME"}


def pdks_uret(plan, calisanlar, ayar=None, tohum=TOHUM, kaydir=7):
    """Bir haftalik PLANDAN sahte PDKS uretir.

    plan       : o haftanin atamalari (gun 0..6)
    calisanlar : sahnenin calisanlari (kimlik listesi icin)
    kaydir     : gun kaydirmasi -- plan gunu g, gecmiste g - kaydir olur

    Donen: (gercek, kayit, bilinen)
      gercek  {kisi: [kayit]}  GERCEKTE ne oldu -- hic kaybi olmayan hal
      kayit   {kisi: [kayit]}  PDKS'in YAKALADIGI -- gercek'in alt kumesi
      bilinen {kisi: [gun]}    kaydi olan gunler (K-42: yalniz bunlar bilinir)

    Kayit bicimi #11.2: {"gun": -k, "bas": s, "bit": s} -- SABLON YOK,
    GECE ISARETI YOK. Gercek PDKS bunlari bilmez; gece tahminle bulunur.
    """
    ayar = dict(VARSAYILAN, **(ayar or {}))
    rnd = random.Random(tohum)
    kisiye = collections.defaultdict(list)
    for a in sorted(plan, key=lambda a: (a["calisan"], a["gun"], a["bas"])):
        kisiye[a["calisan"]].append(a)

    gercek, kayit, bilinen = {}, {}, {}
    for c in sorted(calisanlar, key=lambda c: c["id"]):
        kimlik = c["id"]
        kayitsiz = rnd.random() < ayar["kayitsiz"]
        yasanan = []
        for a in kisiye.get(kimlik, []):
            r = rnd.random()
            if r < ayar["uyum"]:
                bas, bit = a["bas"], a["bit"]
            elif r < ayar["uyum"] + ayar["devamsizlik"]:
                continue                                  # gelmedi
            else:
                dk = rnd.choice(ayar["kaydirma_dk"]) / 60.0
                if rnd.random() < 0.5:
                    bas, bit = a["bas"] + dk, a["bit"]    # gec geldi
                else:
                    bas, bit = a["bas"], a["bit"] + dk    # gec cikti
            yasanan.append({"gun": a["gun"] - kaydir, "bas": bas, "bit": bit})
        # Cagrilma: planli bos bir gunde, planli vardiyalarindan birinin
        # saatleriyle. Ardisik gun ve dinlenme kurallarini zorlar -- bilerek.
        planli_gunler = {a["gun"] for a in kisiye.get(kimlik, [])}
        bos = [g for g in range(7) if g not in planli_gunler]
        if kisiye.get(kimlik) and bos and rnd.random() < ayar["ek_vardiya"]:
            ornek = rnd.choice(kisiye[kimlik])
            yasanan.append({"gun": rnd.choice(bos) - kaydir,
                            "bas": ornek["bas"], "bit": ornek["bit"]})
        yasanan.sort(key=lambda k: (k["gun"], k["bas"]))
        gercek[kimlik] = yasanan
        yakalanan = [] if kayitsiz else [
            k for k in yasanan if rnd.random() < ayar["kayit_orani"]]
        kayit[kimlik] = yakalanan
        bilinen[kimlik] = sorted({k["gun"] for k in yakalanan})
    return gercek, kayit, bilinen


def gecmis_yaz(g, kayitlar, bilinen=None, hepsi_bilinir=False, gun_sayisi=7):
    """Sahneye gecmisi yazar. g YERINDE degisir.

    hepsi_bilinir=True -> GERCEK hal: her gecmis gun bilinir (kaydi olmayan
    gun calisilmamistir). Karsilastirma icin -- urun bunu hic gormez.
    """
    for c in g["calisanlar"]:
        c["gecmis_vardiyalar"] = [dict(k) for k in kayitlar.get(c["id"], [])]
        if hepsi_bilinir:
            c["gecmis_bilinen_gunler"] = list(range(-gun_sayisi, 0))
        else:
            c["gecmis_bilinen_gunler"] = list((bilinen or {}).get(c["id"], []))
    return g


def haber_verilmeyen(gercek_ihlaller, gecmis_eksik):
    """GERCEK gecmise gore ihlal olup, eksik gecmisle bakan denetcinin
    raporunda o KISI ve KURAL icin satiri olmayanlar -- sessiz kacaklar."""
    rapor = {(x["kural"], x["calisan"]) for x in gecmis_eksik}
    cikan = []
    for i in gercek_ihlaller:
        kural = HABERCI.get(i["kural"], i["kural"])
        if (kural, i["calisan"]) not in rapor:
            cikan.append(i)
    return cikan


def main():
    from cozucu.coz import coz
    from dogrulayici import degerlendir

    spec = importlib.util.spec_from_file_location(
        "uret", os.path.join(BURASI, "uret_veri_seti.py"))
    U = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(U)
    iki = importlib.util.spec_from_file_location(
        "iki", os.path.join(BURASI, "iki-hafta-olc.py"))
    I = importlib.util.module_from_spec(iki)
    iki.loader.exec_module(I)

    t0 = time.time()
    g1 = U.sahne_uret(0.1, 0.95)
    c1 = coz(g1, I.AYAR)
    print("HAFTA 1: %s · %d atama · %.0f sn"
          % (c1["durum"], len(c1.get("atamalar") or []), time.time() - t0))
    if c1["durum"] != "cozuldu":
        sys.exit("hafta 1 cozulemedi")

    gercek, kayit, bilinen = pdks_uret(c1["atamalar"], g1["calisanlar"])
    planli = len(c1["atamalar"])
    yasanan = sum(len(v) for v in gercek.values())
    yakalanan = sum(len(v) for v in kayit.values())
    kayitsiz_kisi = sum(1 for c in g1["calisanlar"]
                        if gercek.get(c["id"]) and not kayit.get(c["id"]))
    print("SAHTE PDKS: planli %d · gerceklesen %d · PDKS'in yakaladigi %d (%%%.0f)"
          % (planli, yasanan, yakalanan, 100.0 * yakalanan / max(1, yasanan)))
    print("  calisip HIC kaydi olmayan kisi: %d" % kayitsiz_kisi)

    g_kayit = gecmis_yaz(U.sahne_uret(0.1, 0.95), kayit, bilinen)
    g_gercek = gecmis_yaz(U.sahne_uret(0.1, 0.95), gercek, hepsi_bilinir=True)

    t = time.time()
    c2 = coz(g_kayit, I.AYAR)
    atamalar = c2.get("atamalar") or []
    print("\nHAFTA 2 (sahte PDKS ile): %s · %d atama · %.0f sn"
          % (c2["durum"], len(atamalar), time.time() - t))

    r_kayit = degerlendir(g_kayit, atamalar)
    r_gercek = degerlendir(g_gercek, atamalar)
    sinir = set(I.SINIR_KURALLARI)
    gorulen = [i for i in r_kayit["ihlaller"] if i["kural"] in sinir]
    gercek_ih = [i for i in r_gercek["ihlaller"] if i["kural"] in sinir]
    eksik = r_kayit.get("gecmis_eksik") or []
    kacak = haber_verilmeyen(gercek_ih, eksik)

    sonuc = {
        "oranlar": {k: (list(v) if isinstance(v, tuple) else v)
                    for k, v in VARSAYILAN.items()},
        "tohum": TOHUM,
        "hafta_1": {"durum": c1["durum"], "atama": planli},
        "pdks": {"gerceklesen": yasanan, "yakalanan": yakalanan,
                 "kayitsiz_kisi": kayitsiz_kisi},
        "hafta_2": {"durum": c2["durum"], "atama": len(atamalar)},
        "eksik_gecmisle_gorulen_sinir_ihlali": dict(
            collections.Counter(i["kural"] for i in gorulen)),
        "gercek_gecmise_gore_sinir_ihlali": dict(
            collections.Counter(i["kural"] for i in gercek_ih)),
        "gecmis_eksik": dict(collections.Counter(x["kural"] for x in eksik)),
        "haber_verilmeden_kacan": dict(
            collections.Counter(i["kural"] for i in kacak)),
        "sn": round(time.time() - t0),
    }
    print("  eksik gecmisle bakan denetci -- sinir ihlali: %s"
          % (sonuc["eksik_gecmisle_gorulen_sinir_ihlali"] or "YOK"))
    print("  GERCEK gecmisle bakan denetci -- sinir ihlali: %s"
          % (sonuc["gercek_gecmise_gore_sinir_ihlali"] or "YOK"))
    print("  gecmis_eksik raporu: %d satir %s"
          % (len(eksik), sonuc["gecmis_eksik"] or ""))
    print("  RAPORDA HABERI OLMADAN KACAN: %d %s"
          % (len(kacak), sonuc["haber_verilmeden_kacan"] or ""))
    for i in kacak[:10]:
        print("    - %s" % i.get("mesaj", i))

    with io.open(os.path.join(BURASI, "sahte-pdks-sonucu.json"), "w",
                 encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    print("\nToplam %.0f sn" % (time.time() - t0))


if __name__ == "__main__":
    main()
