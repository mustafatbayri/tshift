# -*- coding: utf-8 -*-
"""
NET SAAT -- COZUCU ILE DOGRULAYICI AYNI SEYI ANLAMALI (T-57)

⚠ NE BULUNDU (29 Eylul, zor veri seti ilk kez cozulurken)
  Plan uretildi, bagimsiz dogrulayici 28 SERT `SAAT_DENGESI` ihlali yazdi.
  Sebep: iki taraf ayni kelimeye farkli anlam veriyordu.

      cozucu      _net_saat(sablon)      = brut - mola_dk
      dogrulayici zaman.net_saat(atama)  = brut - BUTUN molalar

  Cozucu yalniz UCRETSIZ yemegi dusuyordu; dogrulayici UCRETLI dinlenme
  molalarini da dusuyor. 8,5 saatlik bir vardiyada fark 0,75 saat; alti
  vardiyalik haftada 4,5 saat. Cozucu "45 saat oldu" derken dogrulayici
  "40,5" goruyordu.

HANGISI DOGRU -- DOGRULAYICI
  `dogrulayici/zaman.py` bu karari belgeliyor ve gerekcelendiriyor:

    "Bir molanin UCRETLI olmasi, o sirada is yapiliyor olmasi demek
     degildir. Ara dinlenme ucretli de olsa calisma suresinden dusulur;
     ucret tarafi AYRI bir buyuktur (`ucret_saat`)."

  ⚠ 25 Eylul'de bu satir bir kez YANLIS degistirilmis ve GERI ALINMIS.
    Yani karar bilincli; yanlis olan cozucu tarafiydi.

NEDEN BUGUNE KADAR GORUNMEDI
  Iki sey ayni gun degisti: `SAAT_DENGESI`'nin dogrulayici govdesi yazildi
  (K-39) ve veri seti ilk kez insanlari sozlesme saatine yaklastirdi.
  Ikisi olmadan bu ayrisma gorunmezdi -- #7.6'nin var olma sebebi tam
  olarak bu.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_net_saat_uyumu.py -v
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import _net_saat                            # noqa: E402
from dogrulayici import degerlendir, zaman                    # noqa: E402

POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]
# yemek 60 + 3x15 = 105 dk = 1,75 saat

KISA = {"id": "V-KISA", "ekip": "E", "bas": 8, "bit": 17.25, "mola_dk": 60,
        "mola_politikasi": POLITIKA}          # 9,25 brut -> 7,50 net
UZUN = {"id": "V-UZUN", "ekip": "E", "bas": 8, "bit": 18.75, "mola_dk": 60,
        "mola_politikasi": POLITIKA}          # 10,75 brut -> 9,00 net


def test_COZUCU_butun_molalari_duser():
    """⚠ En dogrudan kanit: iki tarafin ayni sayiyi uretmesi.

    Cozucu sablona, dogrulayici atamaya bakar; ama ikisi ayni vardiyayi
    anlatiyorsa ayni net saati vermelidir.
    """
    atama = {"calisan": "C1", "ekip": "E", "sablon": "V-KISA", "gun": 0,
             "bas": 8, "bit": 17.25,
             "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                          "ucretli": False},
                         {"tip": "dinlenme", "bas": 10, "bit": 10.25,
                          "ucretli": True},
                         {"tip": "dinlenme", "bas": 14, "bit": 14.25,
                          "ucretli": True},
                         {"tip": "dinlenme", "bas": 16, "bit": 16.25,
                          "ucretli": True}]}
    assert abs(_net_saat(KISA) - zaman.net_saat(atama)) < 1e-6, (
        "cozucu %.2f saat diyor, dogrulayici %.2f saat"
        % (_net_saat(KISA), zaman.net_saat(atama)))


def test_net_saat_UCRETLI_molayi_da_duser():
    """9,25 brut - (60 + 3x15) dk = 7,50 net.

    Yanlis hesap 8,25 verirdi (yalniz yemek dusuk).
    """
    assert abs(_net_saat(KISA) - 7.5) < 1e-6, (
        "net saat %.2f -- ucretli dinlenme molalari dusulmemis" % _net_saat(KISA))


def _sahne():
    """Tam zamanli, 45 saat, 6 gunluk desen; iki sablon uzunlugu var.

    ⚠ SAHNE BILEREK BOYLE KURULDU
      Tek uzunluk olsaydi hatali hesap da tesadufen dogru sonuc verebilirdi.
      Iki uzunlukla cozucunun SECIMI degisiyor:

          yanlis hesap (8,25 / 9,75) -> 5 vardiya "yeter" saniliyor
                                        gercek: 4x9,0 + 7,5 = 43,5 < 45  IHLAL
          dogru hesap  (7,50 / 9,00) -> 5x9,0 = 45                        TAMAM
    """
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45,
                          "gun_sayisi": 5},
             "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": [dict(KISA), dict(UZUN)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(5) for s in range(9, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 11}},
            {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True,
             "yasal": True, "parametreler": {"azami_saat": 45}},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "SAAT_DENGESI", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": True,
             "parametreler": {"tolerans_saat": 0}},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_UCTAN_UCA_iki_taraf_AYNI_plan_hakkinda_ANLASIR():
    """Asil sinav: cozucunun urettigi plani dogrulayici kabul etmeli.

    Bu test kirmiziyken 500 kisilik sahnede 28 sert ihlal cikiyordu --
    motor kendi olcusune gore dogru, denetciye gore yanlis bir plan
    uretiyordu.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    sd = [i for i in r["ihlaller"] if i["kural"] == "SAAT_DENGESI"]
    sab = {t["id"]: t for t in g["vardiya_sablonlari"]}
    net = collections.Counter()
    for a in c["atamalar"]:
        net[a["calisan"]] += zaman.net_saat(a)
    assert not sd, (
        "cozucu 45 saat saniyor, dogrulayici %.2f saat goruyor: %r"
        % (net.get("C1", 0), [i.get("mesaj") for i in sd]))
