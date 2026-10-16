# -*- coding: utf-8 -*-
"""
METAMORFIK TESTLER -- "dogru cevabi bilmeden" motoru sinayan iliskiler (16 Ekim; oturum 14 Ekim §18, E)

NEDEN
  Kalite olcumleri "referanstan iyi mi" diye bakar; birim testler tek tek kurali
  sinar. Ikisi de su soruya cevap vermez: motor, girdinin ANLAMSIZ degisimine
  kayitsiz, ANLAMLI degisimine dogru yonde tepki veriyor mu? Metamorfik test
  iki kosunun SONUCLARI ARASINDAKI iliskiyi dogrular; optimumun degerini bilmek
  gerekmez. Kucuk sahne, tek isci, OPTIMAL durum: iliskiler o zaman KESINDIR
  (yaklasik cozumde "esit" degil "kucuk esit" bile garanti degildir).

ILISKILER
  M1  Kimlik degisimi (kisi / ekip / sablon adlari) amaci ve kalem dagilimini DEGISTIRMEZ.
  M2  Calismak zorunda olmayan bir kisi EKLEMEK (yari zamanli, sure yok) amaci KOTULESTIRMEZ
      (eski plan hala gecerli: yeni kisi bos kalir).
  M3  Bir YUMUSAK kurali (HEDEF_KAPSAMA) kapatmak amaci KOTULESTIRMEZ (eski plan hala gecerli, bir kalem dustu).
  M4  Cozumun KENDISI `mevcut_plan` olarak verilince PLAN_KARARLILIGI (K-70) 0 ve amac AYNI.
  M5  Ayni girdi, ayni ayar -> ayni plan (tek isci; CP-SAT deterministik).
  M6  Kilit olarak cozumun kendi satirlari verilince plan ve amac AYNI (kilit mevcut cozumle celismez).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_metamorfik.py -v
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                     # noqa: E402

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}
W = {"id": "W", "ekip": "E", "bas": 12, "bit": 21, "mola_dk": 60}
AYAR = {"azami_saniye": 30, "durgunluk_saniye": 10, "isci_sayisi": 1}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne():
    """Uc yari zamanli (sure yok), iki sablon (V 09-18, W 12-21). Talep hafta ici
    3 vardiya/gun (09-12: 2, 12-18: 3, 18-21: 1), hafta sonu 2 vardiya/gun -> 19
    vardiya; kapasite 3 kisi x 6 gun (HAFTA_TATILI) = 18 -> en az bir vardiya
    EKSIK kalir: amac 0 olamaz, iliskiler ayirt edici. HEDEF_ASIMI SERT; yumusak:
    HEDEF_KAPSAMA, ADALET_DENGESI, VARDIYA_ROTASYON_YONU. Optimum saniyeler icinde."""
    talep = []
    for d in range(7):
        for s in range(9, 21):
            if d < 5:
                h = 2 if s < 12 else (3 if s < 18 else 1)
            else:
                h = 1 if s < 12 else (2 if s < 18 else 1)
            talep.append({"ekip": "E", "gun": d, "saat": s, "asgari": 0, "hedef": h})
    return {"profil": "DENGELI",
            "calisanlar": [{"id": p, "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                            "izinler": [], "uygunluk": []} for p in ("P1", "P2", "P3")],
            "vardiya_sablonlari": [V, W],
            "talep": talep,
            "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                         _kural("HEDEF_ASIMI", tur="SERT"), _kural("HAFTA_TATILI", yasal=True),
                         _kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=11),
                         _kural("ADALET_DENGESI", tur="YUMUSAK"),
                         _kural("VARDIYA_ROTASYON_YONU", tur="YUMUSAK")],
            "kilitler": [], "donmus_gunler": []}


def _coz(g):
    c = coz(copy.deepcopy(g), dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    ist = c["cozum_istatistikleri"]
    assert ist["durma_sebebi"] == "optimum", ist["durma_sebebi"]    # iliskiler yalniz optimumda kesin
    assert ist["alt_sinir"] == ist["amac_degeri"], (ist["alt_sinir"], ist["amac_degeri"])
    return c


def _amac(c):
    return c["cozum_istatistikleri"]["amac_degeri"]


def _dagilim(c):
    return {k: v["ceza"] for k, v in c["cozum_istatistikleri"]["amac_dagilimi"].items()}


def _iskelet(c, ad=lambda s: s):
    """Plan iskeleti: (kisi, gun, bas, bit) kumesi -- `ad` kisi adini geri cevirir (M1)."""
    return sorted((ad(a["calisan"]), a["gun"], float(a["bas"]), float(a["bit"])) for a in c["atamalar"])


def test_M0_sahne_optimumda_cozuluyor_ve_amac_sifir_degil():
    c = _coz(_sahne())
    assert _amac(c) > 0, "sahne cok kolay: iliskiler ayirt edici olmaz"
    assert c["atamalar"]


def test_M1_kimlik_degisimi_amaci_ve_dagilimi_DEGISTIRMEZ():
    g = _sahne()
    a = _coz(g)
    h = copy.deepcopy(g)
    ad = {"P1": "Q1", "P2": "Q2", "P3": "Q3"}
    for c in h["calisanlar"]:
        c["id"] = ad[c["id"]]
        c["ekipler"] = ["SAHA"]
    for s in h["vardiya_sablonlari"]:
        s["ekip"] = "SAHA"
        s["id"] = s["id"] + "-2"
    for t in h["talep"]:
        t["ekip"] = "SAHA"
    b = _coz(h)
    assert _amac(a) == _amac(b)
    assert _dagilim(a) == _dagilim(b)
    ters = {v: k for k, v in ad.items()}
    assert _iskelet(a) == _iskelet(b, ters.get)


def test_M2_bos_kalabilen_kisi_eklemek_amaci_KOTULESTIRMEZ():
    g = _sahne()
    a = _coz(g)
    h = copy.deepcopy(g)
    h["calisanlar"].append({"id": "P4", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                            "izinler": [], "uygunluk": []})
    b = _coz(h)
    assert _amac(b) <= _amac(a), (_amac(a), _amac(b))


def test_M3_yumusak_kurali_kapatmak_amaci_KOTULESTIRMEZ():
    g = _sahne()
    a = _coz(g)
    assert _dagilim(a).get("HEDEF_KAPSAMA", 0) > 0, "kapsama cezasi yoksa test ayirt edici degil"
    h = copy.deepcopy(g)
    h["kurallar"] = [k for k in h["kurallar"] if k["kod"] != "HEDEF_KAPSAMA"]
    b = _coz(h)
    assert "HEDEF_KAPSAMA" not in _dagilim(b)
    assert _amac(b) <= _amac(a), (_amac(a), _amac(b))


def test_M4_cozumun_kendisi_mevcut_plan_olunca_PLAN_KARARLILIGI_sifir_amac_AYNI():
    g = _sahne()
    a = _coz(g)
    h = copy.deepcopy(g)
    h["kurallar"].append(_kural("PLAN_KARARLILIGI", tur="YUMUSAK"))
    h["mevcut_plan"] = copy.deepcopy(a["atamalar"])
    b = _coz(h)
    assert _dagilim(b).get("PLAN_KARARLILIGI", 0) == 0, _dagilim(b)
    assert _amac(b) == _amac(a), (_amac(a), _amac(b))
    assert _iskelet(b) == _iskelet(a)


def test_M5_ayni_girdi_ayni_plan_DETERMINIZM():
    g = _sahne()
    a, b = _coz(g), _coz(g)
    assert _amac(a) == _amac(b) and _dagilim(a) == _dagilim(b)
    assert _iskelet(a) == _iskelet(b)


def test_M6_cozumun_satirlari_kilit_olunca_plan_ve_amac_AYNI():
    g = _sahne()
    a = _coz(g)
    h = copy.deepcopy(g)
    h["kurallar"].append(_kural("KILIT_UYUMU"))
    h["kilitler"] = [{"calisan": x["calisan"], "ekip": x["ekip"], "gun": x["gun"], "bas": x["bas"], "bit": x["bit"]}
                     for x in a["atamalar"]]
    b = _coz(h)
    assert _amac(b) == _amac(a), (_amac(a), _amac(b))
    assert _iskelet(b) == _iskelet(a)
