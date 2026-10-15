# -*- coding: utf-8 -*-
"""
TERCIH_KARSILAMA -- yari zamanli SOZLESME SURESINE getirilir (K-71, 14 Ekim)

NE VARDI
  Sartname #6.8'in kurali "calisan tercihi" diye yazilmisti; K-13 ile tercih
  kalkti, K-22 anlami "uygunluk esnekliginin kullanim orani" yapti ama
  olculebilir bir tanim hic yazilmadi: govdesi yoktu, `uygulanmayan_kurallar`
  listesindeydi. Motorda yari zamanlinin yalniz UST siniri vardi (45 sa,
  PART_TIME_LIMIT); 49 kisilik kesifte 33 yari zamanlinin 2'si haftayi hic
  vardiyasiz gecirdi.

KARAR (K-71, Mustafa, 14 Ekim 17:05 / 18:40): yari zamanlinin sozlesmesine
  haftalik sure girilir; motor onu bu sureye GETIRMEYE CALISIR (yumusak:
  talep yetmezse cozumsuz olmaz). Mevzuat (T-83): kismi sureli sozlesmenin
  suresi her hafta odenir -- eksik planlanan saat bosa odenen saattir.
  Agirlik: bosa odenen 1 saat ~ 2.000 puan (fazla mesai 3.000 ile ayni
  olcek), uc profilde ayni; CP-SAT tam sayi ister -> dakika basina 33.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_tercih_karsilama.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU               # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as KR                        # noqa: E402

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}     # 8 saat net
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(gun=5, tercih=True, tercih_par=None, asim="YUMUSAK"):
    """Uc yari zamanli: P1 16 sa, P2 24 sa sozlesme; P3 sozlesme suresi YOK
    (eski setlerin yari zamanlisi). Talep: `gun` gun, her saat 1 kisi.
    gun=5 -> 5 vardiya = P1'in 2 + P2'nin 3 vardiyasi: sureler TAM dolar,
    P3'e is kalmaz. gun=2 -> 2 vardiya: sureler dolamaz (yumusak)."""
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HEDEF_ASIMI", tur=asim), _kural("HAFTA_TATILI", yasal=True),
                _kural("PART_TIME_LIMIT", yasal=True)]
    if tercih:
        kurallar.append(_kural("TERCIH_KARSILAMA", tur="YUMUSAK", **(tercih_par or {})))
    return {"profil": "DENGELI",
            "calisanlar": [
                {"id": "P1", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli", "haftalik_saat": 16},
                 "izinler": [], "uygunluk": []},
                {"id": "P2", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli", "haftalik_saat": 24},
                 "izinler": [], "uygunluk": []},
                {"id": "P3", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                 "izinler": [], "uygunluk": []}],
            "vardiya_sablonlari": [V],
            # talepsiz gun yok: `gun`den sonraki gunlerde hedef 0 (asim sertse o
            # gunlere atama yazilamaz -- yoksa sure bos gunlerde doldurulur)
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1 if d < gun else 0,
                       "hedef": 1 if d < gun else 0}
                      for d in range(7) for s in range(9, 18)],
            "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


def _plan(kisi_gunler):
    return [{"calisan": k, "ekip": "E", "sablon": "V", "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]}
            for k, g in kisi_gunler]


def _tk(r):
    return [i for i in r["ihlaller"] if i["kural"] == "TERCIH_KARSILAMA"]


def _saat(c, kisi):
    return sum(a["bit"] - a["bas"] - 1 for a in c["atamalar"] if a["calisan"] == kisi)   # 1 sa yemek


# ----------------------------------------------------------------------
# 1. Dogrulayici -- kural artik GOVDELI
# ----------------------------------------------------------------------

def test_kural_artik_uygulanmayan_listesinde_DEGIL():
    r = degerlendir(_sahne(), _plan([("P1", 0), ("P1", 1), ("P2", 2), ("P2", 3), ("P2", 4)]))
    assert "TERCIH_KARSILAMA" not in r["uygulanmayan_kurallar"], r["uygulanmayan_kurallar"]
    assert _tk(r) == []                                        # 16 + 24 saat tam


def test_sozlesmenin_altinda_kalan_yari_zamanli_YUMUSAK_ihlal_eksik_saatle():
    r = degerlendir(_sahne(gun=2), _plan([("P1", 0), ("P2", 1)]))   # P1 8/16, P2 8/24; talep dolu
    ih = {i["calisan"]: i for i in _tk(r)}
    assert set(ih) == {"P1", "P2"}
    assert ih["P1"]["olculen"] == 8 and ih["P1"]["gereken"] == 16
    assert ih["P2"]["olculen"] == 8 and ih["P2"]["gereken"] == 24
    assert all(i["agirlik"] == "YUMUSAK" for i in ih.values())
    assert "16.0 saat bosa odenir" in ih["P2"]["mesaj"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True        # yumusak: kapi durmaz


def test_sozlesme_suresi_OLMAYAN_yari_zamanli_ve_TAM_zamanli_DENETLENMEZ():
    g = _sahne()
    g["calisanlar"].append({"id": "T1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
                            "izinler": [], "uygunluk": []})
    r = degerlendir(g, _plan([("P1", 0), ("P1", 1), ("P2", 2), ("P2", 3), ("P2", 4)]))
    assert {i["calisan"] for i in _tk(r)} == set()             # P3 (sure yok) ve T1 yok
    sd = [i for i in r["ihlaller"] if i["kural"] == "SAAT_DENGESI"]
    assert sd == []                                            # SAAT_DENGESI kurali sahnede yok


def test_IZIN_borcu_dusurur_PASIF_sayilmaz_TOLERANS_okunur():
    g = _sahne(tercih_par={"tolerans_saat": 2})
    g["calisanlar"][1]["izinler"] = [{"gun": 4, "durum": "onayli"}]            # P2: 24 - 24/6 = 20 sa
    g["calisanlar"][0]["durum"] = "pasif"                                       # P1 denetlenmez
    r = degerlendir(g, _plan([("P2", 0), ("P2", 1)]))                           # P2 16 sa
    ih = _tk(r)
    assert [i["calisan"] for i in ih] == ["P2"]
    assert ih[0]["gereken"] == 18 and ih[0]["olculen"] == 16                   # 20 - 2 tolerans
    r = degerlendir(g, _plan([("P2", 0), ("P2", 1), ("P2", 2)]))                # 24 >= 18
    assert _tk(r) == []


def test_kural_yokken_yazilmaz():
    r = degerlendir(_sahne(tercih=False), _plan([("P1", 0)]))
    assert _tk(r) == []
    assert "TERCIH_KARSILAMA" not in r["uygulanmayan_kurallar"]


def test_dogrulayici_dogrudan_cagri_motordan_bagimsiz():
    """#7.6: kural govdesi tek basina, motor olmadan ayni sonucu verir."""
    g = _sahne()
    tanim = [k for k in g["kurallar"] if k["kod"] == "TERCIH_KARSILAMA"][0]
    ih = KR.tercih_karsilama(g, _plan([("P1", 0), ("P1", 1), ("P1", 2), ("P2", 3)]), tanim)
    assert [(i["calisan"], i["olculen"], i["gereken"]) for i in ih] == [("P2", 8, 24)]   # P1 24 >= 16


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_motor_yari_zamanlilari_SOZLESME_SURESINE_getirir_suresizi_bos_birakir():
    """5 vardiya = 2 + 3: P1 16 sa, P2 24 sa, P3 (suresiz) 0 sa."""
    g = _sahne()
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    assert _saat(c, "P1") == 16 and _saat(c, "P2") == 24 and _saat(c, "P3") == 0, c["atamalar"]
    r = degerlendir(g, c["atamalar"])
    assert _tk(r) == []
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["TERCIH_KARSILAMA"]["deger"] == 0


def test_KURAL_YOKKEN_motor_sureye_bakmaz_kiyas():
    """Kural kapaliyken motorun 5 vardiyayi sureye gore dagitmasi icin bir
    sebep yok: ADALET dengesi herkese esit dagitir (2/2/1 gibi). Kural acikken
    sonuc 2/3/0 (ustteki test). Fark kuralin isidir."""
    c = coz(_sahne(tercih=False), dict(AYAR))
    assert c["durum"] == "cozuldu"
    assert not (_saat(c, "P1") == 16 and _saat(c, "P2") == 24 and _saat(c, "P3") == 0)
    assert "TERCIH_KARSILAMA" not in c["cozum_istatistikleri"]["amac_dagilimi"]


def test_talep_YETMEZSE_plan_yine_cozulur_YUMUSAK_eksik_cezalanir():
    """2 vardiya, 40 saatlik sozlesme: cozumsuz DEGIL (Mustafa: 'getirmeye
    calissin'); eksik dakika amacta TERCIH_KARSILAMA olarak gorunur ve
    dogrulayici ihlal yazar. HEDEF_ASIMI SERT (urun, K-67): motor eksigi
    hedefin ustune kisi yazarak kapatamaz."""
    g = _sahne(gun=2, asim="SERT")
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    assert _saat(c, "P1") + _saat(c, "P2") == 16                # 2 vardiyanin ikisi de sureli kisilere
    assert _saat(c, "P3") == 0
    dag = c["cozum_istatistikleri"]["amac_dagilimi"]["TERCIH_KARSILAMA"]
    # eksik toplam (16 + 24) - 16 = 24 saat = 1440 dk; agirlik 33 -> 47.520
    assert dag["deger"] == 1440 and dag["ceza"] == 1440 * 33, dag
    r = degerlendir(g, c["atamalar"])
    assert sum(i["gereken"] - i["olculen"] for i in _tk(r)) == 24
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


def test_BIRIM_degisken_yalniz_SURELI_yari_zamanliya_ust_sinir_borc_izin_duser():
    g = _sahne()
    g["calisanlar"][1]["izinler"] = [{"gun": 4, "durum": "onayli"}]            # P2 borc 20 sa = 1200 dk
    g["calisanlar"].append({"id": "T1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
                            "izinler": [], "uygunluk": []})                      # tam zamanli: bu kural degil (K-39)
    k = Model(g).kur()
    adlar = {v.Name(): v for _, v in k.cezalar if v.Name().startswith("tk_")}
    assert set(adlar) == {"tk_P1", "tk_P2"}                                   # P3 (suresiz) ve T1 yok
    assert list(k.m.Proto().variables[adlar["tk_P1"].Index()].domain) == [0, 960]
    assert list(k.m.Proto().variables[adlar["tk_P2"].Index()].domain) == [0, 1200]
    assert [a for a, v in k.cezalar if v.Name() == "tk_P1"] == [33]


def test_AGIRLIK_tablosu_uc_profilde_33_dakika_ve_kiraci_ezebilir():
    assert AGIRLIK_TABLOSU["TERCIH_KARSILAMA"] == {"DENGELI": 33, "KAPSAMA": 33, "CALISAN": 33}
    g = _sahne()
    g["agirliklar"] = {"TERCIH_KARSILAMA": 0}                   # kiraci susturdu
    k = Model(g).kur()
    assert [a for a, v in k.cezalar if v.Name().startswith("tk_")] == [0, 0]
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu"
    assert "TERCIH_KARSILAMA" in c["cozum_istatistikleri"]["amac_dagilimi"]   # terim var, agirligi 0


def test_UST_sinir_hala_SERT_sozlesme_45i_asamaz():
    """K-71 yalniz alt tarafa bakar; ust sinir PART_TIME_LIMIT (K-39) kalir:
    7 gun x 8 sa = 56 sa talep, tek yari zamanli 56 sa sozlesmeli olsa da
    45 sa'yi asamaz; HAFTA_TATILI zaten 6 gune indirir -> 48 > 45."""
    g = _sahne(gun=7)
    g["calisanlar"] = [{"id": "P1", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli", "haftalik_saat": 56},
                        "izinler": [], "uygunluk": []}]
    g["kurallar"] = [k for k in g["kurallar"] if k["kod"] != "ASGARI_KAPSAMA"]
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    assert _saat(c, "P1") <= 45
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]
    assert _tk(r) and _tk(r)[0]["olculen"] <= 45                # eksik kalir, yumusak


def test_HEDEF_ASIMI_YUMUSAKKEN_sure_doldurma_hedefin_ustune_kisi_yazdirir_K67_gerekcesi():
    """Yan etki, kayit icin: asim yumusakken (eski S30 setleri; 3 puan /
    kisi-saat) sozlesme suresi (33 puan / dk) agir basar ve motor eksigi
    HEDEFIN USTUNE kisi yazarak kapatir. Urunde HEDEF_ASIMI SERT (K-67) --
    orada olmaz; yumusak setlerde olcum okunurken bilinmeli."""
    c = coz(_sahne(gun=2, asim="YUMUSAK"), dict(AYAR))
    assert c["durum"] == "cozuldu"
    assert _saat(c, "P1") + _saat(c, "P2") > 16
