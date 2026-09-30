# -*- coding: utf-8 -*-
"""
DURGUNLUK DURDURMASI -- K-28'in yazilmamis ikinci kosulu (T-24a)

NE KORUYOR
  Cozucu, belirli bir sure yeni ve daha iyi bir plan bulamiyorsa arar.
  K-28: "erken dur, bekletme."

⚠ BU KURAL YAZILI SANILIYORDU AMA YOKTU
  `coz.py` icindeki `VARSAYILAN` sozlugunde su satir duruyordu:

      "durgunluk_saniye": 120,      # 2 dk iyilesme yoksa bitir

  Parametre TANIMLI, aciklamasi YAZILI, `_ErkenDur.son_iyilesme` alani her
  cozumde GUNCELLENIYOR -- ama hicbir yerde OKUNMUYORDU. Yani karar
  verilmis, belgelenmis ve hic uygulanmamisti.

  Bu T-24a/T-26'nin ta kendisi: "karar kayitli ama yururlukte degil."
  28 Eylul'de gercekci veri setinde OLCULDU: 35 kisilik bir sahnede cozucu
  butcenin TAMAMINI (900 sn) kullandi, planı cok daha once bulmustu.

NEDEN CALLBACK TEK BASINA YETMEZ
  CP-SAT'in cozum callback'i yalniz YENI COZUM bulununca tetiklenir.
  Cozucu tikandiginda callback hic cagrilmaz -- yani durgunlugu callback'in
  KENDISI fark edemez. Disaridan bakan bir bekci gerekir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_durgunluk.py -v
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz, VARSAYILAN                        # noqa: E402


def _zor_sahne(kisi=60, gun=7):
    """Cozulebilir ama optimumu kanitlamasi uzun suren bir sahne."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%02d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        # ⚠ 30 Eylul aksami (T-69): 15:00-23:00 ARTIK ACIKCA gece isaretli.
        #   Bu sahnenin zorlugu ADALET_DENGESI'nin "gece" boyutundan geliyordu
        #   ve o boyut isaretsiz sablonu TAHMINLE sayiyordu: eski tahmin
        #   ("pencereye en ufak degme") 15-23'u gece sayiyordu, yeni tahmin
        #   (md. 7/2, "yarisindan cogu") saymiyor. Isaret konmadan sahne
        #   kolaylasti, cozucu optimumu kanitladi ve bu test 'hedef_bosluk'
        #   gordu -- yani durgunlugu hic sinamadi. Isaretle model eskisiyle
        #   AYNI kaldi.
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60, "gece_vardiyasi": b == 15}
            for j, b in enumerate((6, 9, 12, 15))
        ],
        # ⚠ Sahne BILEREK tikaniyor: asgari 10 / hedef 30 ile cozucu
        #   hedef boslugunu kapatamiyor ve butcenin tamamini kullaniyor.
        #   Ilk yazimda 24 kisi / asgari 5 idi ve cozucu 3 saniyede
        #   `hedef_bosluk` ile bitiyordu -- yani test durgunlugu HIC
        #   sinamiyordu, YESIL olmasi bir sey kanitlamiyordu.
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 10, "hedef": 30}
                  for d in range(gun) for s in range(6, 23)],
        "kurallar": [
            {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
             "kabul_edilebilir": False}
            for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                      "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
        ] + [
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
            {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
             "parametreler": {"esik": 2}},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_durgunluk_parametresi_OKUNUYOR():
    """En temel sinav: parametre gercekten etkili mi.

    ⚠ Bu test yazildiginda KIRMIZIYDI. `durgunluk_saniye` tanimliydi ama
      kodda hicbir yerde okunmuyordu -- degeri ne olursa olsun davranis
      degismiyordu.
    """
    g = _zor_sahne()
    t0 = time.time()
    c = coz(g, {"azami_saniye": 90, "durgunluk_saniye": 3, "hedef_bosluk": 0.0})
    sure = time.time() - t0
    assert c["durum"] == "cozuldu", c["durum"]
    assert sure < 60, (
        "durgunluk 3 sn iken cozucu %.0f saniye kostu -- parametre "
        "okunmuyor (butce 90 sn idi)" % sure)


def test_durgunlukta_DURMA_SEBEBI_yazilir():
    """Neden durdugunu soylemeli -- sessizce kisa kesmek de bir sessiz gecistir."""
    g = _zor_sahne()
    c = coz(g, {"azami_saniye": 90, "durgunluk_saniye": 3, "hedef_bosluk": 0.0})
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("durma_sebebi") == "durgunluk", (
        "durma sebebi 'durgunluk' olmali, %r geldi" % ist.get("durma_sebebi"))


def test_varsayilan_durgunluk_TANIMLI():
    """K-28'in kararı varsayilanlarda durmali; sessizce kaybolmasin."""
    assert VARSAYILAN.get("durgunluk_saniye"), (
        "durgunluk_saniye varsayilanlardan kaybolmus -- K-28 yururlukten kalkar")


def test_HIZLI_sahne_durgunluktan_etkilenmez():
    """Geriye donuk uyum: kolay sahne yine optimumu bulup normal bitmeli.

    Durgunluk bekcisi fazla hevesli olursa iyi planlari yarida keser --
    bu, gec bitirmekten daha kotu olurdu.
    """
    g = _zor_sahne(kisi=8, gun=1)
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 3}
                  for s in range(9, 17)]
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 120})
    assert c["durum"] == "cozuldu", c["durum"]
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("durma_sebebi") != "durgunluk", (
        "kolay sahne durgunluk diye kesilmis: %r" % ist.get("durma_sebebi"))
