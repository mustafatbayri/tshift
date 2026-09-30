# -*- coding: utf-8 -*-
"""
GECMIS EKSIK RAPORUNUN OZETI (K-47) ve TESHISIN "BELIRSIZ" CEVABI (T-76)

K-47 (Mustafa, 30 Eylul gecesi): "Yonetici baksin."
  Sahte PDKS olcumunde 49 kisilik plan icin `gecmis_eksik` 141 satir
  yazdi; icinde 7 gercek ihlal vardi ve hepsi haberliydi (T-77). Satir
  satir okunmaz. Cikti artik KISI BASINA gruplanmis bir ozet de tasir:
  yasal kontrolu yapilamayanlar ONDE, sayilar tepede. Yayin kapisi bunu
  ENGELLEMEZ (K-42); ekran gosterir ve "gordum" onayi ister.

T-76 (30 Eylul aksami, uc haftalik olcum): teshis her sert kurali 10
  saniye deniyor; o olcekte yetmiyor ve "engelleyen kural yok" diyordu --
  oysa kural kaldirilinca 172 saniyede cozuluyordu. K-37'nin ailesi:
  "yetistiremedim" ile "yok" ayni kelimeye dusuyordu. Artik uc cevap:
  engelliyor (kanit) · engellemiyor (kanit) · BELIRSIZ (sure doldu).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402

GUNDUZ = {"id": "V-GUNDUZ", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60,
          "gece_vardiyasi": False}


def _kural(kod, yasal=False, **par):
    k = {"kod": kod, "tur": "SERT", "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


DINLENME = _kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=11)
ARDISIK = _kural("ARDISIK_CALISMA_GUNU", azami_gun=6)


def _kisi(kimlik, bilinen=None, gecmis=None):
    c = {"id": kimlik, "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    if bilinen is not None:
        c["gecmis_bilinen_gunler"] = bilinen
    if gecmis is not None:
        c["gecmis_vardiyalar"] = gecmis
    return c


# Pazar kaydi VAR (08-16): dinlenme kontrolu yapilabilir (yasal satir yok);
# ardisik gun serisi pazardan geriye cumartesiye uzanabilir, cumartesi
# bilinmiyor -> yalniz firma kurali raporlanir.
PAZAR_CALISTI = [{"gun": -1, "bas": 8, "bit": 16}]


def _p(gun, kimlik):
    return {"calisan": kimlik, "ekip": "E", "sablon": GUNDUZ["id"], "gun": gun,
            "bas": GUNDUZ["bas"], "bit": GUNDUZ["bit"], "molalar": []}


def _sahne(kurallar, kisiler):
    return {"profil": "DENGELI", "calisanlar": kisiler,
            "vardiya_sablonlari": [GUNDUZ], "talep": [],
            "kurallar": list(kurallar), "kilitler": [], "donmus_gunler": []}


# ----------------------------------------------------------------------
# 1. Ozet
# ----------------------------------------------------------------------

def test_OZET_kanali_ciktida_var():
    r = degerlendir(_sahne([DINLENME], [_kisi("C1")]), [_p(0, "C1")])
    assert "gecmis_eksik_ozet" in r, list(r)


def test_OZET_kisi_basina_gruplar_ve_sayar():
    """C1: iki kural (biri yasal), C2: yalniz firma kurali, C3: gecmisi
    tam biliniyor -> raporda yok."""
    g = _sahne([DINLENME, ARDISIK],
               [_kisi("C1"), _kisi("C2", gecmis=PAZAR_CALISTI),
                _kisi("C3", bilinen=list(range(-7, 0)))])
    plan = ([_p(d, "C1") for d in range(0, 3)]
            + [_p(d, "C2") for d in range(0, 3)]
            + [_p(d, "C3") for d in range(0, 3)])
    r = degerlendir(g, plan)
    oz = r["gecmis_eksik_ozet"]
    assert oz["satir"] == len(r["gecmis_eksik"]) >= 3, (oz, r["gecmis_eksik"])
    assert oz["kisi"] == 2, oz
    assert oz["yasal_kontrol_yapilamayan_kisi"] == 1, oz
    kisiler = {k["calisan"]: k for k in oz["kisiler"]}
    assert set(kisiler) == {"C1", "C2"}, kisiler
    assert kisiler["C1"]["yasal"] is True
    assert set(kisiler["C1"]["kurallar"]) == {"VARDIYA_ARASI_DINLENME",
                                              "ARDISIK_CALISMA_GUNU"}
    assert kisiler["C2"]["yasal"] is False
    assert kisiler["C2"]["kurallar"] == ["ARDISIK_CALISMA_GUNU"]


def test_OZET_yasal_olanlar_ONDE():
    g = _sahne([DINLENME, ARDISIK], [_kisi("A", gecmis=PAZAR_CALISTI), _kisi("B")])
    plan = [_p(d, "A") for d in range(0, 3)] + [_p(0, "B")]
    oz = degerlendir(g, plan)["gecmis_eksik_ozet"]
    assert [k["calisan"] for k in oz["kisiler"]] == ["B", "A"], oz["kisiler"]
    assert [k["yasal"] for k in oz["kisiler"]] == [True, False]


def test_OZET_bos_raporda_sifirlar():
    g = _sahne([DINLENME], [_kisi("C1", bilinen=[-1])])
    oz = degerlendir(g, [_p(0, "C1")])["gecmis_eksik_ozet"]
    assert oz == {"satir": 0, "kisi": 0, "yasal_kontrol_yapilamayan_kisi": 0,
                  "kisiler": []}, oz


def test_OZET_yayin_kapisini_DEGISTIRMEZ():
    """K-42/K-47: rapor yayini engellemez; kapi yalniz ihlallere bakar."""
    r = degerlendir(_sahne([DINLENME], [_kisi("C1")]), [_p(0, "C1")])
    assert r["gecmis_eksik_ozet"]["kisi"] == 1
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


# ----------------------------------------------------------------------
# 2. Teshis -- T-76
# ----------------------------------------------------------------------

def _cozumsuz_sahne():
    """Tek kisi, iki ayri kural ayni anda bagliyor: gece calisamaz VE
    talep yalniz gece sablonuyla karsilanabilir. Engelleyen kural
    GECE_UYGUNLUGU (kaldirilinca cozulur); ASGARI_KAPSAMA kaldirilinca da
    cozulur (talep kalmaz). Kanitlar aninda geliyor -- kucuk sahne."""
    gece = {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60,
            "gece_vardiyasi": True}
    c = _kisi("C1")
    c["gece_calisamaz"] = True
    return {"profil": "DENGELI", "calisanlar": [c],
            "vardiya_sablonlari": [gece],
            "talep": [{"ekip": "E", "gun": 0, "saat": 23, "asgari": 1, "hedef": 1}],
            "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("GECE_UYGUNLUGU")],
            "kilitler": [], "donmus_gunler": []}


def test_TESHIS_belirsiz_listesi_ciktida_var():
    from cozucu.coz import coz
    c = coz(_cozumsuz_sahne(), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozumsuz", c.get("durum")
    assert "belirsiz_kurallar" in c["teshis"], c["teshis"]
    kodlar = {k["kod"] for k in c["teshis"]["engelleyen_kurallar"]}
    assert "GECE_UYGUNLUGU" in kodlar, c["teshis"]
    assert c["teshis"]["belirsiz_kurallar"] == [], c["teshis"]


def test_TESHIS_sure_yetmezse_BELIRSIZ_der_yok_demez(monkeypatch):
    """Deneme cozucusu sure asimi (UNKNOWN) donerse kural 'engellemiyor'
    listesine DUSMEMELI; belirsiz listesine girmeli ve not yazilmali."""
    import importlib
    T = importlib.import_module("cozucu.teshis")
    monkeypatch.setattr(T, "_cozulebilir_mi", lambda girdi, saniye=10: None)
    from cozucu.coz import coz
    c = coz(_cozumsuz_sahne(), {"azami_saniye": 20, "durgunluk_saniye": 5,
                                "teshis_kural_saniye": 3})
    t = c["teshis"]
    assert t["engelleyen_kurallar"] == [], t
    assert {k["kod"] for k in t["belirsiz_kurallar"]} == {"ASGARI_KAPSAMA",
                                                          "GECE_UYGUNLUGU"}, t
    assert all(k["deneme_saniye"] == 3 for k in t["belirsiz_kurallar"]), t
    assert "KANITLANAMADI" in t.get("not", ""), t


def test_TESHIS_kural_basina_butce_AYARLANABILIR(monkeypatch):
    import importlib
    T = importlib.import_module("cozucu.teshis")
    gorulen = []

    def sahte(girdi, saniye=10):
        gorulen.append(saniye)
        return False

    monkeypatch.setattr(T, "_cozulebilir_mi", sahte)
    from cozucu.coz import coz
    coz(_cozumsuz_sahne(), {"azami_saniye": 20, "durgunluk_saniye": 5,
                            "teshis_kural_saniye": 42})
    assert gorulen and all(s == 42 for s in gorulen), gorulen
