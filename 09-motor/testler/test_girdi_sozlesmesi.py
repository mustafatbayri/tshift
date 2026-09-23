# -*- coding: utf-8 -*-
"""
GIRDI SOZLESMESI TESTLERI -- T-19

NE KORUYORLAR
  16 Eylul dis incelemesi: sartname #11.2 talebi HUCRE BASINA BIR SATIR
  diye tanimliyor ({ekip, gun, saat, asgari, hedef}); motor ise gruplu
  bicim ({gunler: [], saatler: []}) okuyordu. Sartname biciminde bir istek
  gelince motor talebi HIC gormuyor, sifir atamali plan uretiyor ve
  "%100 kapsama, yayinlanabilir" diyordu.

  Kimse yanlis degildi: fikstur bir bicim secti, motor fiksture bakarak
  yazildi. Ikisi birbiriyle tutarli, ikisi de SARTNAMEYLE tutarsiz. #7.6
  bagimsizligi kural MANTIGINI ayiriyor, GIRDI YORUMUNU ayirmiyor.

  Karar (23 Eylul, Mustafa): SARTNAME KAZANIR.

OKUNMAYAN ALANLAR -- ayni ailenin geri kalani
  Tarama sonucu: sartnamenin BES alani motorda hicbir satirda gecmiyor
  (tercihler, kural_degerleri, devir_kapsama, mola_tek_blok,
  gecmis_vardiyalar). Cagiran taraf onlari gonderiyor, motor bakmiyor,
  ve kimse bilmiyor.

  Motor bunu KURALLAR icin zaten bildiriyor (`uygulanmayan_kurallar`).
  Girdi alanlari icin ayni kanal yoktu. Karar: bildirilsin, isi durdurmasin.

NEDEN DOGRULAYICIDA
  "Neye bakmadim" demek dogrulayicinin isi; `uygulanmayan_kurallar` ve
  `eksik_boyutlar` da orada. Ayri bir ortak modul CIKARILAMAZ: #7.6 ve
  test_bagimsizlik.test_ortak_yardimci_modul_yok bunu yasakliyor.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_girdi_sozlesmesi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                          # noqa: E402
from orkestra import coz_ve_onar                             # noqa: E402


# ----------------------------------------------------------------------
# Sahne: tek gun, tek sablon, uc kisi -- talep SARTNAME bicimiyle
# ----------------------------------------------------------------------

def _sahne(talep, ek=None):
    girdi = {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": k, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []}
            for k in ("C1", "C2", "C3")
        ],
        "vardiya_sablonlari": [
            {"id": "V", "bas": 9, "bit": 13, "mola_dk": 0, "gunler": [5]},
        ],
        "talep": talep,
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
        ],
        "kilitler": [],
        "donmus_gunler": [],
    }
    if ek:
        girdi.update(ek)
    return girdi


# Sartname #11.2: hucre basina BIR satir.
SARTNAME_TALEBI = [
    {"ekip": "E", "gun": 5, "saat": s, "asgari": 3, "hedef": 3}
    for s in (9, 10, 11, 12)
]

# Motorun 23 Eylul'e kadar okudugu bicim. Artik OKUNMAMALI.
GRUPLU_TALEP = [
    {"ekip": "E", "gunler": [5], "saatler": [9, 10, 11, 12],
     "asgari": 3, "hedef": 3},
]


# ----------------------------------------------------------------------
# 1. Sartname bicimi gercekten okunuyor mu  (T-19'un cekirdegi)
# ----------------------------------------------------------------------

def test_sartname_bicimindeki_talep_OKUNUR():
    """T-19: sartname bicimi verilince motor talebi gormeli.

    23 Eylul'e kadar gormuyordu: sifir atamali plan uretip "%100 kapsama"
    diyordu.

    OLCU BIRIMI NOTU -- ilk yazimda burada 12 yaziyordu ("4 saat x 3 kisi").
    Yanlisti: bir ATAMA kisi x VARDIYA'dir, kisi x SAAT degil. Uc kisi tek
    bir 09-13 vardiyasini alinca dort talep hucresi de dolar ama atama sayisi
    UCtur. Sayiyi degil, KAPSAMAYI sinamak daha dogru: asagisi birimden
    bagimsiz.
    """
    c = coz_ve_onar(_sahne(SARTNAME_TALEBI), {"azami_saniye": 15})
    assert c["durum"] == "cozuldu"
    assert c["atamalar"], (
        "sartname bicimindeki talep okunmuyor -- hic atama uretilmedi (T-19)")
    for saat in (9, 10, 11, 12):
        kisi = sum(1 for a in c["atamalar"]
                   if a["ekip"] == "E" and a["gun"] == 5
                   and a["bas"] <= saat < a["bit"])
        assert kisi >= 3, (
            "gun 5 saat %d: asgari 3 istendi, %d kisi atandi -- sartname "
            "bicimindeki talep okunmuyor (T-19)" % (saat, kisi))


def test_bos_plan_yuzde_yuz_kapsama_DIYEMEZ():
    """T-19'un asil zarari: sessizce atlanan talep, plani MUKEMMEL gosteriyordu.

    Atama yokken kapsama %100 cikiyorsa yayin kapisi da acik demektir.
    """
    c = coz_ve_onar(_sahne(SARTNAME_TALEBI), {"azami_saniye": 15})
    assert c["metrikler"]["asgari_kapsama_yuzde"] == 100.0
    assert len(c["atamalar"]) > 0, (
        "kapsama %100 ama atama YOK -- bos plan mukemmel gorunuyor (T-19)")


# ----------------------------------------------------------------------
# 2. Okunmayan alanlar bildiriliyor mu
# ----------------------------------------------------------------------

def test_okunmayan_alan_BILDIRILIR():
    """Sartnamede olup motorun okumadigi alan sessizce gecilemez.

    `tercihler` sartname #11.2'de tanimli, motorda tek satiri yok.
    Cagiran taraf gonderiyor ve hesaba katildigini saniyor.
    """
    girdi = _sahne(SARTNAME_TALEBI)
    girdi["calisanlar"][0]["tercihler"] = [
        {"gun": 5, "bas": 9, "bit": 13, "agirlik": 3}]

    rapor = degerlendir(girdi, [])
    assert "okunmayan_alanlar" in rapor, (
        "dogrulayici okunmayan girdi alanlarini bildirmiyor (T-19)")
    adlar = {a["alan"] for a in rapor["okunmayan_alanlar"]}
    assert "tercihler" in adlar, (
        "gonderilen 'tercihler' alani bildirilmedi: %s" % sorted(adlar))


def test_GRUPLU_bicim_artik_sessizce_calismaz():
    """Sessiz tuzak: eski bicim calismaya devam ederse IKI DOGRULUK olur.

    T-32'nin dersi. Sartname kazandiysa gruplu bicim ya okunmamali ya da
    okunmadigi BILDIRILMELI -- sessizce kabul edilmemeli.
    """
    rapor = degerlendir(_sahne(GRUPLU_TALEP), [])
    adlar = {a["alan"] for a in rapor.get("okunmayan_alanlar") or []}
    assert "gunler" in adlar or "saatler" in adlar, (
        "eski gruplu bicim sessizce gecti -- iki dogruluk kaynagi olustu")


def test_temiz_girdide_okunmayan_alan_YOK():
    """Gerileme korumasi: kapi gurultu uretmemeli.

    Yalniz motorun okudugu alanlar gonderildiginde liste BOS olmali;
    yoksa rapor her istekte dolu gelir ve okunmaz hale gelir (O-7).
    """
    rapor = degerlendir(_sahne(SARTNAME_TALEBI), [])
    assert rapor.get("okunmayan_alanlar") == [], (
        "temiz girdide bile alan bildiriliyor: %s" % rapor.get("okunmayan_alanlar"))
