# -*- coding: utf-8 -*-
"""
INSAN PLANI SAHNESI testleri (16 Ekim; A3) -- insan-plani.py

Gercek veri (06-veri) git disidir ve isim icerir; testler UYDURMA bir kanonik tabloyla
calisir: uc kisi, iki takim, lider, gece yarisini asan vardiya, izin kodu.
  * Turkce harf sadelestirme ve takim/rol eslemesi (I/İ tuzagi);
  * sahne anonim: isim/sicil hicbir ciktida yok, kimlikler I001..;
  * sablonlar (takim, desen) basina; gece yarisini asan vardiyanin bitisi > 24;
  * talep insan planindan (hedef = sayilan kisi, asgari <= hedef), HEDEF_ASIMI SERT;
  * sozlesme saati insan planinin net saati (<= 45), izin kodu -> onayli izin;
  * insan plani kendi sahnesinde eksiksiz ve asimsiz (kurulus geregi); denetim raporu dolu.
"""

import csv
import importlib.util
import io
import json
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor"))

_spec = importlib.util.spec_from_file_location("insan_plani", os.path.join(BURASI, "insan-plani.py"))
IP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IP)

BASLIK = ["sicil", "ad_soyad", "takim", "gorev", "gun", "tur", "baslangic", "bitis", "brut_saat", "gece_asan",
          "ham_deger", "revizyon", "kaynak_dosya", "sayfa"]


def _satir(sicil, ad, takim, gorev, gun, bas=None, bit=None, kod=None):
    if kod:
        return [sicil, ad, takim, gorev, gun, "DURUM", "", "", "", "", kod, "1", "x.xlsx", "Vardiya"]
    gece = bit[:10] > bas[:10]
    return [sicil, ad, takim, gorev, gun, "VARDIYA", bas, bit, "9", "1" if gece else "0", "%s-%s" % (bas[11:], bit[11:]), "1", "x.xlsx", "Vardiya"]


@pytest.fixture
def kanonik(tmp_path):
    """22-28 Haziran 2026 (Pazartesi 22). Uc kisi: 1001 Satış Destek uzmani (5 gun 09-18),
    1002 'BACKOFFİCE TAKIM LİDERİ' lideri (5 gun 14-23, Cuma 16-01 gece asan), 1003 Satış Destek
    (4 gun 09-15 + Persembe RAPORLU)."""
    satirlar = []
    gunler = ["2026-06-%02d" % d for d in range(22, 29)]
    for i, g in enumerate(gunler[:5]):
        satirlar.append(_satir("1001", "Ayşe Gizli", "Satış Destek", "Satış Destek Uzmanı", g, g + " 09:00", g + " 18:00"))
    for i, g in enumerate(gunler[:4]):
        satirlar.append(_satir("1002", "Mehmet Saklı", "BACKOFFİCE TAKIM LİDERİ", "Takım Lideri", g, g + " 14:00", g + " 23:00"))
    satirlar.append(_satir("1002", "Mehmet Saklı", "BACKOFFİCE TAKIM LİDERİ", "Takım Lideri", gunler[4], gunler[4] + " 16:00", gunler[5] + " 01:00"))
    for g in (gunler[0], gunler[1], gunler[2], gunler[4]):
        satirlar.append(_satir("1003", "Zeynep Örnek", "Satış Destek", "Satış Destek Uzman Yardımcısı", g, g + " 09:00", g + " 15:00"))
    satirlar.append(_satir("1003", "Zeynep Örnek", "Satış Destek", "Satış Destek Uzman Yardımcısı", gunler[3], kod="RAPORLU"))
    satirlar.append(_satir("1001", "Ayşe Gizli", "Satış Destek", "Satış Destek Uzmanı", gunler[5], kod="OFF"))
    satirlar.append(_satir("1001", "Ayşe Gizli", "Satış Destek", "Satış Destek Uzmanı", "2026-06-15", "2026-06-15 09:00", "2026-06-15 18:00"))   # baska hafta
    yol = tmp_path / "plan.csv"
    with io.open(str(yol), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(BASLIK)
        w.writerows(satirlar)
    return str(yol)


def test_INSAN_turkce_harf_sadelestirme_takim_ve_rol():
    assert IP.sade("Yerinde Çözüm Merkezi") == "yerinde cozum merkezi"
    assert IP.ekip_kodu("YERİNDE ÇÖZÜM MERKEZİ TAKIM LİDERİ") == "YCM"
    assert IP.ekip_kodu("Ant-Yurtiçi Ürün Müdürlüğü") == "ANT_URUN"
    assert IP.ekip_kodu("Ürün Analiz") == "URUN_ANALIZ" and IP.ekip_kodu("Backoffice") == "BACKOFFICE"
    assert IP.ekip_kodu("bilinmeyen") == "DIGER"
    assert IP.lider_mi("FİYATLANDIRMA TAKIM LİDERİ", "") and IP.lider_mi("", "Takım Lideri")
    assert not IP.lider_mi("Satış Destek", "Satış Destek Uzmanı")


def test_INSAN_saat_sablon_kimligi_mola_politikasi():
    assert IP.saat("2026-06-22 13:30") == 13.5
    assert IP.sablon_kimligi("YCM", 16.0, 25.0) == "YCM-1600-0100"
    assert IP.mola_politikasi(9.0)[0] == {"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}
    assert IP.mola_politikasi(6.0)[0]["dakika"] == 30
    m = IP.varsayilan_molalar(9.0, 18.0)
    assert [x["tip"] for x in m] == ["dinlenme", "yemek", "dinlenme"] and m[1]["bas"] == 13.0 and m[1]["bit"] == 14.0
    m6 = IP.varsayilan_molalar(9.0, 15.0)
    assert [x["tip"] for x in m6] == ["dinlenme", "yemek"] and m6[1]["bit"] == 12.5
    assert all(x["bit"] <= 15.0 for x in m6)


def test_INSAN_sahne_anonim_sablonlar_talep_sozlesme_izin(kanonik):
    g, ref, esleme = IP.kur(kanonik, "2026-06-22")
    metin = json.dumps(g, ensure_ascii=False) + json.dumps(ref, ensure_ascii=False)
    for gizli in ("Ayşe", "Gizli", "Mehmet", "Saklı", "Zeynep", "Örnek", "1001", "1002", "1003"):
        assert gizli not in metin, gizli
    assert esleme == {"1001": "I001", "1002": "I002", "1003": "I003"}
    kisi = {c["id"]: c for c in g["calisanlar"]}
    assert set(kisi) == {"I001", "I002", "I003"}
    assert kisi["I002"]["operasyonel_rol"] == "takim_lideri" and kisi["I002"]["ekipler"] == ["BACKOFFICE"]
    assert kisi["I001"]["operasyonel_rol"] is None and kisi["I001"]["birincil_ekip"] == "SATIS_DESTEK"
    assert kisi["I003"]["izinler"] == [{"gun": 3, "tip": "rapor", "durum": "onayli"}]
    assert kisi["I001"]["izinler"] == []                                      # OFF izin degil
    # sozlesme = insan planinin NET saati (butun molalar dusuk, SAAT_DENGESI'nin olcusu):
    # 5 x (9 - 1 yemek - 2 x 0,25 dinlenme) = 37,5; 4 x (6 - 0,5 - 0,25) = 21
    assert kisi["I001"]["sozlesme"] == {"tip": "tam_zamanli", "haftalik_saat": 37.5, "gun_sayisi": 5}
    assert kisi["I003"]["sozlesme"]["haftalik_saat"] == 21.0
    sablon = {s["id"]: s for s in g["vardiya_sablonlari"]}
    assert set(sablon) == {"SATIS_DESTEK-0900-1800", "SATIS_DESTEK-0900-1500", "BACKOFFICE-1400-2300", "BACKOFFICE-1600-0100"}
    assert sablon["BACKOFFICE-1600-0100"]["bit"] == 25.0 and sablon["BACKOFFICE-1600-0100"]["gece_vardiyasi"] is True
    assert sablon["SATIS_DESTEK-0900-1500"]["mola_politikasi"][0]["dakika"] == 30
    assert len(ref["atamalar"]) == 14 and all(a["calisan"].startswith("I") for a in ref["atamalar"])
    # talep insan planindan: Pazartesi 10:00 SATIS_DESTEK 2 kisi (09-18 ve 09-15), BACKOFFICE 0
    talep = {(t["ekip"], t["gun"], t["saat"]): t for t in g["talep"]}
    assert talep[("SATIS_DESTEK", 0, 10)]["hedef"] == 2 and talep[("BACKOFFICE", 0, 10)]["hedef"] == 0
    assert talep[("BACKOFFICE", 0, 22)]["hedef"] == 1 and talep[("BACKOFFICE", 5, 0)]["hedef"] == 1   # gece asan: Cumartesi 00-01
    assert all(0 <= t["asgari"] <= t["hedef"] for t in g["talep"])
    assert [k["tur"] for k in g["kurallar"] if k["kod"] == "HEDEF_ASIMI"] == ["SERT"]
    assert not any(k["kod"] in IP.ATILAN_KURALLAR for k in g["kurallar"])
    assert g["_merdiven"]["seviye"] == "insan" and g["hafta_baslangic"] == "2026-06-22"
    assert "2026-06-15" not in metin                                          # baska hafta disarida
    k = ref["kayit"]
    assert k["kisi"] == 3 and k["lider"] == 1 and k["atama"] == 14 and k["izinli_kisi_gun"] == 1
    assert k["sert_ihlal"] >= 0 and isinstance(k["sert_kural"], dict) and "fazla_mesai_saat" in (k["metrikler"] or {})


def test_INSAN_insan_plani_kendi_sahnesinde_EKSIKSIZ_ve_ASIMSIZ(kanonik):
    import merdiven as MD
    g, ref, _ = IP.kur(kanonik, "2026-06-22")
    d = MD.referans_denetle(g, ref["atamalar"])
    assert d["asim"] == 0 and d["eksik"] == 0
    assert d["fazla_mesai_saat"] == 0.0


def test_INSAN_pazartesi_olmayan_hafta_ve_bos_hafta_REDDEDILIR(kanonik):
    with pytest.raises(SystemExit):
        IP.kur(kanonik, "2026-06-23")
    with pytest.raises(SystemExit):
        IP.kur(kanonik, "2026-09-28")
