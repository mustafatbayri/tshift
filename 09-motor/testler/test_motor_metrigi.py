# -*- coding: utf-8 -*-
"""
MOTORUN KENDI METRIGI -- KESIRLI VARDIYA SINIRI (T-65)

⚠ NE BULUNDU (30 Eylul, CI kirmizi yandi)
  Zor veri seti bekcisi kirmizi yandi:

      sert_ihlal: 0   ·   asgari_kapsama_yuzde: 99.76

  Ilk bakista bu bir celiski gibi duruyor: `ASGARI_KAPSAMA` SERT bir
  kural, ihlal yoksa kapsama %100 olmali. Celiski DEGIL -- iki sayinin
  ikisi de motorun KENDI raporundan geliyor ve ikisi de yaniltici.

SEBEP -- `int()` KESIRLI SINIRI KIRPIYOR
  `coz.py::_metrikler` kapsamayi soyle sayiyordu:

      range(a["gun"] * 24 + int(a["bas"]), a["gun"] * 24 + int(a["bit"]))

  Vardiya 07:00-16:15 ise `int(16.25)` = 16 ve `range(7, 16)` saat 16'yi
  DISARIDA birakiyor. Oysa vardiya 16:00-16:15 arasi sahada. Kisit tarafi
  (`_atanmis` -> `_dilimler` -> `_q`) ceyrek dilimle calisiyor ve saat
  16'yi kapsiyor. Yani KISIT saglanmis, METRIK "kapanmadi" diyor.

  Sahnedeki sablonlarin cogu kesirli bitiyor: 16.25, 16.75, 18.25, 18.75,
  20.25, 22.00, 23.00... K-34 ceyrek izgarasini getirdiginden beri bu
  normal. 415 talep hucresinin BIRI bu yuzden eksik sayildi:
  414/415 = %99,76.

  ⚠ T-58 ILE AYNI AILE. 29 Eylul'de kesirli vardiya bitisi
  DOGRULAYICIYI cokertiyordu (`range()`e float gidiyordu) ve orada
  duzeltildi. Cozucudeki bu KOPYASINA kimse bakmadi.

IKINCI BULGU -- `sert_ihlal` OLCULMUYOR, SABIT YAZILIYOR
  Ayni fonksiyonda:

      "sert_ihlal": 0,   # kisitlar sert; cozum varsa hepsi saglanmistir

  Cumle mantik olarak dogru ama alan adi bir OLCUM vaat ediyor. Ekranda
  "0 sert ihlal" yazdiginda insan bunu sayilmis sanir. Sayilmadi.
  Motorun kendi isini kendi onaylamasi tam olarak #7.6'nin yasakladigi
  sey; bu yuzden bekciler artik DOGRULAYICININ sayisina bakiyor.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_motor_metrigi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                     # noqa: E402
from dogrulayici import degerlendir                            # noqa: E402

# 07:00-16:15 -- bitisi KESIRLI. `int(16.25)` = 16, yani eski sayim saat
# 16'yi disarida birakiyordu.
SABLON = {"id": "V-KESIRLI", "ekip": "E", "bas": 7, "bit": 16.25,
          "mola_dk": 60}


def _sahne():
    """Tek kisi, tek vardiya, talep 07:00-16:00 -- son hucre KESIRLI kapanir.

    ⚠ SAHNE BILEREK BOYLE: saat 16 hucresini kapatan tek sey vardiyanin
      16:00-16:15 arasi. Kirpan bir sayim o hucreyi "kapanmadi" sayar.
    """
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli"},
             "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
                  for s in range(7, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True,
             "yasal": True},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_MOTORUN_metrigi_kesirli_bitisi_KIRPMIYOR():
    """⚠ T-65'in dogrudan kaniti.

    Motor plani uretti demek, kendi kisitlarini sagladi demektir. Kendi
    metriginin de ayni seyi soylemesi gerekir; soylemiyorsa ekranda
    gorunen sayi yanlis.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    m = c.get("metrikler") or {}
    assert m.get("asgari_kapsama_yuzde") == 100.0, (
        "motor kendi plani icin %%%s kapsama diyor -- kesirli vardiya "
        "bitisi kirpiliyor" % m.get("asgari_kapsama_yuzde"))


def test_MOTOR_ile_DOGRULAYICI_ayni_kapsamayi_soyler():
    """Asil olcu: iki taraf ayni plan icin ayni sayiyi vermeli.

    Dogrulayici `zaman.atanmis_mi` ile kesirli sinirla dogru calisiyor
    (T-58'de duzeltildi). Motorun sayisi ondan sapiyorsa sapan taraf
    motordur.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    motor = (c.get("metrikler") or {}).get("asgari_kapsama_yuzde")
    denetci = (degerlendir(g, c["atamalar"])
               .get("metrikler") or {}).get("asgari_kapsama_yuzde")
    assert motor == denetci, (
        "motor %%%s diyor, bagimsiz denetci %%%s -- iki taraf ayni plan "
        "hakkinda ayrisiyor" % (motor, denetci))


def test_ASGARI_KAPSAMA_kurali_da_ihlal_YAZMIYOR():
    """Ucuncu bakis: kural govdesi de temiz demeli.

    Uc sayi (motor metrigi, denetci metrigi, kural govdesi) ayni plan
    hakkinda ayni seyi soylemek zorunda. Ikisi anlasip ucuncusu ayrilirsa
    ayrilan yanlistir.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c.get("durum")
    r = degerlendir(g, c["atamalar"])
    ak = [i for i in r["ihlaller"] if i["kural"] == "ASGARI_KAPSAMA"]
    assert not ak, [i.get("mesaj") for i in ak][:3]
