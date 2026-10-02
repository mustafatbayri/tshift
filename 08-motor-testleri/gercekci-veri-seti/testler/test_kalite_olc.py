# -*- coding: utf-8 -*-
"""
KALITE OLCUMUNUN COZUCUDEN BAGIMSIZ TABANLARI (T-60, 2 Ekim)

`kalite-olc.py` iki alt sinir hesaplar: kapasite tabani (hedefin kac
kisi-saati hicbir planla kapanamaz) ve fazla mesai tabani (sablon
kesikliligi yuzunden kac dakika fazla mesai kacinilmaz). Ikisi de "plan
kotu" ile "kadro/sablon yetmiyor"u ayirmak icin var; YANLIS bir taban
"kadro yetmiyor" dedirtir. Bu yuzden:
  - bilinen sahnelerde tabanin DEGERI sinanir (8 kisi-saat, 300 dakika)
  - gece yarisini asan vardiya ve devreden kapsama tabana sayilir (yoksa
    taban sisirilir ve GECERSIZ olur)
  - cozulen plan tabanin altina inemez (gecerlilik)

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_kalite_olc.py -v
"""

import importlib.util
import os
import sys

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.model import Model                                # noqa: E402
from cozucu.coz import coz                                    # noqa: E402


def _yukle(ad):
    yol = os.path.join(BURASI, ad)
    spec = importlib.util.spec_from_file_location(ad.replace("-", "_").replace(".py", ""), yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KO = _yukle("kalite-olc.py")
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 3, "iki_asama_esigi": 10 ** 9}


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sablon(tid, bas, bit, ekip="E"):
    return {"id": tid, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": 60, "gece_vardiyasi": bit > 24,
            "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]}


def _kisi(cid, saat=45, ekipler=("E",)):
    return {"id": cid, "ekipler": list(ekipler),
            "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": saat, "gun_sayisi": 6},
            "izinler": [], "uygunluk": []}


def _sahne(calisanlar, sablonlar, talep, kurallar):
    return {"profil": "DENGELI", "calisanlar": calisanlar, "vardiya_sablonlari": sablonlar,
            "talep": talep, "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


# ---- kapasite tabani ----------------------------------------------------

def test_kapasite_tabani_iki_kisi_hedef_uc_sekiz_kisi_saat():
    """Gun 0 08-16 hedef 3, iki kisi: her hucrede 1 eksik, 8 kisi-saat
    hicbir planla kapanamaz. Dort duzey de ayni sayiyi verir."""
    g = _sahne([_kisi("C1"), _kisi("C2")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 3} for s in range(8, 16)],
               [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"), _kural("HAFTA_TATILI")])
    k = Model(g).kur()
    kt = KO.kapasite_tabani(g, k)
    assert kt["hedef"]["taban_hucre"] == 8 and kt["hedef"]["taban_ekip_gun"] == 8
    assert kt["hedef"]["taban_gun"] == 8
    # Hafta duzeyi GEVSEK: iki kisi haftada 6'sar gun calisabilir (96 saat),
    # talep 24 -- bu duzey 0 der. Taban dort duzeyin EN BUYUGUDUR.
    assert kt["hedef"]["taban_hafta"] == 0
    assert kt["hedef"]["taban"] == 8 and kt["hedef"]["toplam_kisi_saat"] == 24
    assert kt["asgari"]["taban"] == 0
    # Gecerlilik: cozulen plan tabanin altina inemez.
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] >= 8


def test_kapasite_tabani_izinli_gun_arzdan_duser():
    g = _sahne([_kisi("C1"), _kisi("C2")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 2} for s in range(8, 16)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 0
    g["calisanlar"][1]["izinler"] = [{"gun": 0, "durum": "onayli"}]
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 8


def test_kapasite_tabani_gece_yarisini_asan_vardiya_ertesi_gune_sayilir():
    """Talep gun 1 00-07; tek sablon gun 0'da baslayan 23-31. 'Dun baslayan'
    parca sayilmazsa taban 7 cikar -- oysa plan onu sifirla kapatir."""
    g = _sahne([_kisi("C1")], [_sablon("GECE", 23, 31)],
               [{"ekip": "E", "gun": 1, "saat": s, "asgari": 0, "hedef": 1} for s in range(0, 7)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    k = Model(g).kur()
    kt = KO.kapasite_tabani(g, k)
    assert kt["hedef"]["taban"] == 0, kt
    c = coz(g, AYAR, kuruldu=k)
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] == 0


def test_kapasite_tabani_devreden_kapsama_sayilir():
    """K-56: onceki haftanin tasan vardiyasi gun 0 00-07'yi kapatir; bu
    haftanin sablonu o saatleri kapsamiyor. Devir sayilmazsa taban 7."""
    g = _sahne([_kisi("C1")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(0, 7)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 7
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 0


# ---- fazla mesai tabani -------------------------------------------------

def test_fazla_mesai_tabani_kesikli_sablon_bes_saat_kacinilmaz():
    """Tek sablon net 10 saat (08-19, 1 saat yemek); sozlesme 45, SAAT_DENGESI
    sert: 4 vardiya 40 (borcu tutmaz), 5 vardiya 50 -> 5 saat fazla mesai
    kacinilmaz. 7,5 saatlik sablon eklenince 6 x 7,5 = 45: taban 0."""
    # FAZLA_MESAI_TAVANI olmadan model fazla mesaiye HIC izin vermez (fm_pay 0,
    # 50 saat cozumsuz); taban yine gecerli kalir ama plan karsilastirmasi
    # icin tavan kurali eklenir (DENGELI profil: 10 saat).
    g = _sahne([_kisi("C1")], [_sablon("UZUN", 8, 19)],
               [{"ekip": "E", "gun": d, "saat": s, "asgari": 0, "hedef": 1}
                for d in range(7) for s in range(8, 19)],
               [_kural("SAAT_DENGESI", "SERT"), _kural("HAFTA_TATILI"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10)])
    k = Model(g).kur()
    fm = KO.fazla_mesai_tabani(g, k)
    assert fm["kisi"] == 1 and fm["saat_dengesi_sert"] is True
    assert fm["dakika"] == 300 and fm["saat"] == 5.0 and fm["ceza"] == 15000, fm
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["FAZLA_MESAI"]["deger"] >= 300
    g["vardiya_sablonlari"].append(_sablon("NORMAL", 8, 16.5))
    assert KO.fazla_mesai_tabani(g, Model(g).kur())["dakika"] == 0


def test_fazla_mesai_tabani_saat_dengesi_sert_degilse_sifir():
    g = _sahne([_kisi("C1")], [_sablon("UZUN", 8, 19)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(8, 19)],
               [_kural("SAAT_DENGESI", "YUMUSAK"), _kural("HEDEF_KAPSAMA", "YUMUSAK")])
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["dakika"] == 0 and fm["saat_dengesi_sert"] is False


def test_fazla_mesai_tabani_borcunu_tutturamayan_sayilir():
    """Tek sablon net 7 saat, hafta tatili var: 6 x 7 = 42 < 45. Kisi borcunu
    hicbir karisimla tutturamaz: taban ona ceza yazmaz, ayri sayar."""
    g = _sahne([_kisi("C1")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(8, 16)],
               [_kural("SAAT_DENGESI", "SERT"), _kural("HAFTA_TATILI")])
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["borcunu_tutturamayan"] == 1 and fm["dakika"] == 0, fm
    # Hafta tatili yoksa 7 x 7 = 49 >= 45: ulasilir, 4 saat fazla mesai kacinilmaz.
    g["kurallar"] = [_kural("SAAT_DENGESI", "SERT")]
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["borcunu_tutturamayan"] == 0 and fm["dakika"] == 240, fm
