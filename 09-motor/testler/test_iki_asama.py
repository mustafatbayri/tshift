# -*- coding: utf-8 -*-
"""
IKI ASAMALI COZUM -- once gecerli plan, sonra iyilestirme

NEDEN VAR (28 Eylul, 350 kisilik gercekci sahnede olculdu)
  Buyuk sahnede cozucu hic plan uretemiyordu. Olcum sunu gosterdi:

      amac VAR  : 45 saniyede HIC COZUM YOK  (UNKNOWN)
      amac YOK  : 32 saniyede OPTIMAL

  Yani GECERLI bir plan bulmak kolay; IYILESTIRMEK zor. Cozucu butun
  zamanini iyilestirmeye harcayip elini bos donuyordu.

  Bunun kullaniciya maliyeti sadece bekleme degil: elde HICBIR plan
  olmadigi icin "cozumsuz" deniyordu -- yani "imkansiz" ile "yetistiremedim"
  ayni cevaba cikiyordu.

NASIL CALISIR
  1. Amac gecici olarak kaldirilir, YALNIZCA uygun bir plan aranir.
  2. Bulunan plan cozucuye ipucu (hint) olarak verilir.
  3. Amac geri konur ve iyilestirme o plandan baslar.

  Boylece butce dolsa bile elde HER ZAMAN bir plan olur.

NE ZAMAN DEVREYE GIRER
  Yalniz BUYUK modellerde. Kucuk sahnede iki asama gereksiz yere iki kat
  kurulum demektir; esik `iki_asama_esigi` ile ayarlanir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_iki_asama.py -v
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz, VARSAYILAN                        # noqa: E402


def _sahne(kisi, gun=7, asgari=8, hedef=25):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%03d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60,
             "mola_politikasi": [
                 {"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
                 {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]}
            for j, b in enumerate((6, 9, 12, 15))
        ],
        "talep": [{"ekip": "E", "gun": d, "saat": s,
                   "asgari": asgari, "hedef": hedef}
                  for d in range(gun) for s in range(6, 23)],
        "kurallar": [
            {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
             "kabul_edilebilir": False}
            for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                      "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
        ] + [
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
            {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True},
            {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
             "parametreler": {"esik": 2}},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_esik_asilinca_IKI_ASAMA_devreye_girer():
    """Mekanizma sinavı: esik asilinca iki asamali yol kullanilir.

    ⚠ TEST OLCEGI DEGIL MEKANIZMAYI SINAR. 350 kisilik gercek sahneyi
      teste koymak dakikalar surerdi ve bir test suiti oyle beklenemez.
      Esik parametreyle dusurulur; calisan sey ayni koddur.

      (Bugun uc kez, "sahne kucuk oldugu icin test olcmek istedigini hic
       olcmedi" tuzagina dusuldu. Buradaki cozum sahneyi buyutmek degil,
       esigi indirip mekanizmayi dogrudan sinamak.)
    """
    g = _sahne(14, gun=2, asgari=3, hedef=8)
    # Butceler CI icin bilerek genis: yavas bir makinede kisa butce
    # mekanizmayla ilgisiz bir kirmizi uretirdi.
    c = coz(g, {"azami_saniye": 60, "durgunluk_saniye": 8,
                "ilk_asama_saniye": 25, "iki_asama_esigi": 1000})
    ist = c.get("cozum_istatistikleri") or {}
    assert c["durum"] == "cozuldu", c["durum"]
    assert c.get("atamalar"), "plan bos"
    assert ist.get("iki_asama") is True, (
        "esik asildigi halde iki asamali yol kullanilmadi: %r" % ist)


def test_iki_asamadan_sonra_AMAC_geri_konur():
    """En sinsi hata buysa: amac geri konmazsa motor 'herhangi bir plan'
    uretmeye baslar ve butun yumusak kurallar sessizce etkisiz kalir.

    Plan gecerli gorunur, kalitesi cokerdi ve kimse fark etmezdi.
    """
    g = _sahne(14, gun=2, asgari=3, hedef=8)
    # Butceler CI icin bilerek genis: yavas bir makinede kisa butce
    # mekanizmayla ilgisiz bir kirmizi uretirdi.
    c = coz(g, {"azami_saniye": 60, "durgunluk_saniye": 8,
                "ilk_asama_saniye": 25, "iki_asama_esigi": 1000})
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("amac_degeri") is not None, (
        "amac degeri yok -- amac geri konmamis olabilir: %r" % ist)


def test_KUCUK_sahne_tek_asamada_kalir():
    """Kucuk sahnede iki asama gereksiz maliyet -- devreye girmemeli."""
    g = _sahne(8, gun=1, asgari=2, hedef=3)
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 3}
                  for s in range(9, 17)]
    c = coz(g, {"azami_saniye": 30})   # varsayilan esik 50.000
    assert c["durum"] == "cozuldu", c["durum"]
    ist = c.get("cozum_istatistikleri") or {}
    assert not ist.get("iki_asama"), (
        "kucuk sahnede iki asama devreye girdi: %r" % ist)


def test_esik_AYARLANABILIR():
    """Esik varsayilanlarda tanimli olmali; sessizce kaybolmasin."""
    assert VARSAYILAN.get("iki_asama_esigi"), (
        "iki_asama_esigi varsayilanlardan kaybolmus")
