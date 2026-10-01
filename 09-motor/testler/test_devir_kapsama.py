# -*- coding: utf-8 -*-
"""
DEVREDEN KAPSAMA: ONCEKI HAFTANIN TASAN VARDIYASI BU HAFTANIN ILK SAATLERINI
KAPATIR (K-56, T-38, 1 Ekim gecesi)

NEDEN
  Pazar 23:00'te baslayan vardiya pazartesi 07:00'de biter. Bu hafta
  planlanirken pazartesi 00:00-06:00 talebi o vardiyayla ZATEN kapali; motor
  bunu bilmezse ya bu haftadan kisi arar ya da "ulasilamayan hucre" der
  (28 Eylul'de yasandi). #11.2'deki `devir_kapsama` alani vardi ama anlami
  yazili degildi ve iki tarafta da okunmuyordu.

KARAR (Mustafa, 1 Ekim gecesi: "sana katiliyorum"): sayi gecmis vardiyalardan
  (K-42) turetilir; `devir_kapsama` yalniz gecmis verisi olmayan ilk haftada
  elle verilir. Iki yarida da sayilir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_devir_kapsama.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model                                # noqa: E402
from cozucu.teshis import ulasilamayan_hucre                  # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 2, "iki_asama_esigi": 10 ** 9}


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sahne():
    """Tek ekip E; tek sablon 08-16 (gece sablonu YOK). Gun 0'da talep 00-07 ve
    08-16; 00-07'yi bu haftanin hicbir sablonu kapatamaz."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"], "yetkinlikler": ["ing"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45}, "izinler": [], "uygunluk": []},
            {"id": "C2", "ekipler": ["E"], "yetkinlikler": [],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45}, "izinler": [], "uygunluk": []},
        ],
        "vardiya_sablonlari": [
            {"id": "T08", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60, "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
        ],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
                  for s in list(range(0, 7)) + list(range(8, 16))],
        "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                     _kural("VARDIYA_ARASI_DINLENME", asgari_saat=11), _kural("CAKISMA_YOK")],
        "kilitler": [], "donmus_gunler": [],
    }


def _erken(ihlaller, kod="ASGARI_KAPSAMA"):
    return [i for i in ihlaller if i["kural"] == kod and i.get("gun") == 0 and i.get("saat") < 7]


# ---- cozucu -------------------------------------------------------------

def test_devir_YOKSA_erken_saatler_ulasilamaz():
    g = _sahne()
    k = Model(g).kur()
    h = ulasilamayan_hucre(g, k)
    assert h and h["gun"] == 0 and h["saat"] == 0, h


def test_GECMIS_tasan_vardiya_erken_saatleri_kapatir_iki_tarafta():
    g = _sahne()
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]   # pazar 23 -> pzt 07
    k = Model(g).kur()
    assert ulasilamayan_hucre(g, k) is None
    assert k._devir_sayisi("E", 0, 0) == 1 and k._devir_sayisi("E", 0, 6.75) == 1
    assert k._devir_sayisi("E", 0, 7) == 0
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu", (c.get("durum"), c.get("uygulanmayan_notlar"))
    r = degerlendir(g, c["atamalar"])
    assert not _erken(r["ihlaller"]), _erken(r["ihlaller"])
    assert r["metrikler"]["asgari_kapsama_yuzde"] == 100.0, r["metrikler"]
    # Motorun kendi metrigi de ayni seyi soyler.
    assert c["metrikler"]["asgari_kapsama_yuzde"] == 100.0


def test_devreden_kisi_ERTESI_vardiyadan_once_dinlenir_ve_planda_iki_kez_sayilmaz():
    """C1 pazar 23-07 calismis: pazartesi 08'de baslayamaz (1 saat dinlenme);
    plani C2 alir. Devreden sahte satir saat/dinlenme kurallarina GIRMEZ."""
    g = _sahne()
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    assert [a["calisan"] for a in c["atamalar"] if a["gun"] == 0] == ["C2"]
    # Dogrulayici: C1'i 08-16'ya yazsak dinlenme ihlali TEK olmali (iki kez sayilmaz).
    plan = [{"calisan": "C1", "ekip": "E", "sablon": "T08", "gun": 0, "bas": 8, "bit": 16, "molalar": []}]
    r = degerlendir(g, plan)
    dinlenme = [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ARASI_DINLENME"]
    assert len(dinlenme) == 1, dinlenme
    assert not [i for i in r["ihlaller"] if i["kural"] == "CAKISMA_YOK"]


def test_ELLE_devir_kapsama_gecmis_yokken_sayilir():
    g = _sahne()
    g["devir_kapsama"] = [{"ekip": "E", "gun": 0, "saat": s, "kisi": 1} for s in range(0, 7)]
    k = Model(g).kur()
    assert ulasilamayan_hucre(g, k) is None
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu", c.get("durum")
    r = degerlendir(g, c["atamalar"])
    assert not _erken(r["ihlaller"])
    assert r["metrikler"]["asgari_kapsama_yuzde"] == 100.0
    assert not c["uygulanmayan_notlar"], c["uygulanmayan_notlar"]


def test_GECMIS_varken_elle_devir_YOK_sayilir_not_duser():
    g = _sahne()
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 27}]   # yalniz 00-03
    g["devir_kapsama"] = [{"ekip": "E", "gun": 0, "saat": s, "kisi": 3} for s in range(0, 7)]
    k = Model(g).kur()
    assert k._devir_sayisi("E", 0, 1) == 1          # 3 degil
    assert k._devir_sayisi("E", 0, 5) == 0
    assert any("devir_kapsama yok sayildi" in n for n in k.notlar), k.notlar
    r = degerlendir(g, [])
    erken = _erken(r["ihlaller"])
    assert {i["saat"] for i in erken} == {3, 4, 5, 6}, erken


def test_niteligi_tasiyan_devreden_kisi_YETKINLIK_kapsamasina_sayilir():
    g = _sahne()
    g["talep"] = [t for t in g["talep"] if t["saat"] < 7]            # yalniz 00-07
    g["kurallar"].append(_kural("YETKINLIK_KAPSAMASI", yetkinlik="ing", asgari=1,
                                ekip="E", saatler=list(range(0, 7))))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]   # C1 'ing'
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", (c.get("durum"), c.get("uygulanmayan_notlar"))
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "YETKINLIK_KAPSAMASI"], r["ihlaller"]
    # Ayni gecmis C2'de (niteliksiz) olsaydi: kapsama tamam ama nitelik eksik.
    g["calisanlar"][0].pop("gecmis_vardiyalar")
    g["calisanlar"][1]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    r2 = degerlendir(g, [])
    assert not _erken(r2["ihlaller"])
    assert [i for i in r2["ihlaller"] if i["kural"] == "YETKINLIK_KAPSAMASI"]
    # Elle verilen sayinin niteligi bilinmez: yetkinlik kapsamasina sayilmaz.
    g["calisanlar"][1].pop("gecmis_vardiyalar")
    g["devir_kapsama"] = [{"ekip": "E", "gun": 0, "saat": s, "kisi": 1} for s in range(0, 7)]
    r3 = degerlendir(g, [])
    assert not _erken(r3["ihlaller"])
    assert [i for i in r3["ihlaller"] if i["kural"] == "YETKINLIK_KAPSAMASI"]


def test_TEK_sayimda_devreden_kisi_yalniz_ilk_ekibine_sayilir():
    g = _sahne()
    g["calisanlar"][0]["ekipler"] = ["B", "E"]           # ilk ekip B
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    g["cok_ekipli_sayim"] = "tek"
    k = Model(g).kur()
    assert k._devir_sayisi("E", 0, 1) == 0 and k._devir_sayisi("B", 0, 1) == 1
    r = degerlendir(g, [])
    assert len(_erken(r["ihlaller"])) == 7                # E'ye sayilmadi
    g["cok_ekipli_sayim"] = "hepsi"
    k2 = Model(g).kur()
    assert k2._devir_sayisi("E", 0, 1) == 1
    r2 = degerlendir(g, [])
    assert not _erken(r2["ihlaller"])


def test_devir_atamalari_bicimi():
    g = _sahne()
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31},
                                               {"gun": -3, "bas": 8, "bit": 16}]     # tasmiyor
    d = K.devir_atamalari(g)
    assert len(d) == 1 and d[0]["calisan"] == "C1" and d[0]["gun"] == 0
    assert d[0]["bas"] == -1 and d[0]["bit"] == 7 and d[0]["_devir"] is True
