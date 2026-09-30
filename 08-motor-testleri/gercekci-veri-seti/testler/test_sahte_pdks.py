# -*- coding: utf-8 -*-
"""
SAHTE PDKS URETICISININ KENDI TESTLERI

Uretici bir OLCUM ARACI besliyor: uretici yanlissa olcum de yanlis olur ve
bunu kimse gormez (T-64'un dersi: araci da sinamak gerekir). Bu testler
cozucu calistirmaz -- saniyenin altinda biter, CI'da kosar.

Olcum araci (`sahte_pdks.py`) elle kosar; bunlar yalniz uretecinin
sozlerini sinar:
  * ayni tohum ayni ciktiyi verir
  * PDKS'in yakaladigi, gerceklesenin ALT KUMESIDIR
  * kayit bicimi #11.2'dir: sablon yok, gece isareti yok, gun negatif
  * bilinen gun = kaydi olan gun (K-42) -- baska hicbir gun bilinmez
  * uyum orani istenen orana yakindir
  * "haber verilmeden kacan" hesabi rapor satiriyla eslesir
"""

import os
import sys

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BURASI not in sys.path:
    sys.path.insert(0, BURASI)

import sahte_pdks as P                                         # noqa: E402

SABLONLAR = ((7, 16.25), (13.75, 23), (23, 32.25), (0, 8.75))


def _sahne(kisi=40):
    calisanlar = [{"id": "C%03d" % i} for i in range(kisi)]
    plan = []
    for i, c in enumerate(calisanlar):
        for gun in range(6):                     # pazar bos
            bas, bit = SABLONLAR[(i + gun) % len(SABLONLAR)]
            plan.append({"calisan": c["id"], "ekip": "E", "sablon": "S",
                         "gun": gun, "bas": bas, "bit": bit, "molalar": []})
    return plan, calisanlar


def test_AYNI_tohum_AYNI_cikti():
    plan, cs = _sahne()
    assert P.pdks_uret(plan, cs, tohum=7) == P.pdks_uret(plan, cs, tohum=7)
    assert P.pdks_uret(plan, cs, tohum=7) != P.pdks_uret(plan, cs, tohum=8)


def test_yakalanan_GERCEKLESENIN_alt_kumesi():
    plan, cs = _sahne()
    gercek, kayit, _ = P.pdks_uret(plan, cs)
    for kimlik, liste in kayit.items():
        for k in liste:
            assert k in gercek[kimlik], (kimlik, k)


def test_kayit_bicimi_PDKS_gibi():
    """Sablon yok, gece isareti yok, gun negatif (#11.2)."""
    plan, cs = _sahne()
    gercek, kayit, _ = P.pdks_uret(plan, cs)
    for liste in list(gercek.values()) + list(kayit.values()):
        for k in liste:
            assert set(k) == {"gun", "bas", "bit"}, k
            assert -7 <= k["gun"] < 0, k


def test_BILINEN_gun_yalniz_kaydi_olan_gun():
    """K-42'nin ruhu: kaydin yoklugu hicbir sey kanitlamaz. Planli bos gun
    de BILINMEZ -- kart okutulmamis olabilir."""
    plan, cs = _sahne()
    _, kayit, bilinen = P.pdks_uret(plan, cs)
    for kimlik in kayit:
        assert bilinen[kimlik] == sorted({k["gun"] for k in kayit[kimlik]})


def test_KAYITSIZ_kisinin_hic_kaydi_yok():
    plan, cs = _sahne()
    _, kayit, bilinen = P.pdks_uret(plan, cs, ayar={"kayitsiz": 1.0})
    assert not any(kayit.values()) and not any(bilinen.values())


def test_KUSURSUZ_ayarda_gecmis_PLANIN_kendisi():
    """Sapma yok, kayip yok: gecmis, planin 7 gun geri kaydirilmis hali."""
    plan, cs = _sahne()
    ayar = {"uyum": 1.0, "devamsizlik": 0.0, "ek_vardiya": 0.0,
            "kayitsiz": 0.0, "kayit_orani": 1.0}
    gercek, kayit, _ = P.pdks_uret(plan, cs, ayar=ayar)
    beklenen = {}
    for a in plan:
        beklenen.setdefault(a["calisan"], []).append(
            {"gun": a["gun"] - 7, "bas": a["bas"], "bit": a["bit"]})
    for kimlik, liste in beklenen.items():
        liste.sort(key=lambda k: (k["gun"], k["bas"]))
        assert gercek[kimlik] == liste and kayit[kimlik] == liste, kimlik


def test_UYUM_orani_istenen_oranda():
    """Mustafa: "plana %80-85 uyumlu". Varsayilan 0,825; 1.200 vardiyada
    aynen gerceklesenin payi +-0,04 icinde olmali."""
    plan, cs = _sahne(kisi=200)
    gercek, _, _ = P.pdks_uret(plan, cs, ayar={"ek_vardiya": 0.0})
    planli = {(a["calisan"], a["gun"] - 7, a["bas"], a["bit"]) for a in plan}
    aynen = sum(1 for kimlik, liste in gercek.items() for k in liste
                if (kimlik, k["gun"], k["bas"], k["bit"]) in planli)
    oran = aynen / float(len(plan))
    assert abs(oran - P.VARSAYILAN["uyum"]) < 0.04, oran


def test_HABER_verilmeyen_hesabi():
    rapor = [{"kural": "VARDIYA_ARASI_DINLENME", "calisan": "C1"},
             {"kural": "HAFTA_TATILI", "calisan": "C2"}]
    ihlaller = [
        {"kural": "VARDIYA_ARASI_DINLENME", "calisan": "C1"},  # haberli
        {"kural": "CAKISMA_YOK", "calisan": "C1"},             # dinlenme satiri haber verir
        {"kural": "HAFTA_TATILI", "calisan": "C3"},            # HABERSIZ
        {"kural": "ARDISIK_CALISMA_GUNU", "calisan": "C2"},    # HABERSIZ (kural farkli)
    ]
    kacan = P.haber_verilmeyen(ihlaller, rapor)
    assert [(i["kural"], i["calisan"]) for i in kacan] == [
        ("HAFTA_TATILI", "C3"), ("ARDISIK_CALISMA_GUNU", "C2")], kacan
