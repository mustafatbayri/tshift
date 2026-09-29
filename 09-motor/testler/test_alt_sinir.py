# -*- coding: utf-8 -*-
"""
ALT SINIR -- "optimum en iyi ihtimalle bu kadar iyi olabilir"

⚠ NEDEN GEREKTI (29 Eylul, Mustafa'nin makinesinde olculdu)
  Cikti "optimuma %42 uzak" diyor ama bu tek sayi IKI ayri seyin oranindan
  cikiyor:

      uzaklik = (amac - alt sinir) / amac

  Yani yuzde iki sekilde duser: PLAN iyilesirse (amac duser) ya da KANIT
  guclenirse (alt sinir yukselir). Ciktida yalniz oran vardi, iki taraf
  yoktu -- ve bu yuzden 350 kisilik sahnede sunun cevabi verilemedi:

      "900 saniye 360 saniyeden neden daha iyi? Plan mi duzeldi, yoksa
       cozucu sadece daha iyi kanitladi mi?"

  Ikisi COK farkli sey. Birincisi sahada daha iyi vardiya demek; ikincisi
  ayni plan hakkinda daha az suphe demek. Yoneticiye sure sectirirken
  (K-35) hangisini sattigimizi bilmemiz gerekiyor.

NE SINAR
  Alt sinirin ciktida oldugunu, amactan buyuk olmadigini ve plan yoksa
  None dondugunu.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_alt_sinir.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402


def _sahne(kisi=10):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%02d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60,
             "mola_politikasi": [
                 {"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
                 {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]}
            for j, b in enumerate((8, 12))
        ],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 4}
                  for s in range(9, 17)],
        "kurallar": [
            {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
             "kabul_edilebilir": False}
            for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                      "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
        ] + [
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_ALT_SINIR_ciktida_var():
    """Oranin paydasi kadar payi da gorunmeli."""
    c = coz(_sahne(), {"azami_saniye": 20})
    ist = c.get("cozum_istatistikleri") or {}
    assert c["durum"] == "cozuldu", c["durum"]
    assert ist.get("alt_sinir") is not None, (
        "alt sinir ciktida yok -- 'optimuma %% uzak' sayisi tek basina "
        "planin mi kanitin mi degistigini soylemiyor: %r" % ist)


def test_alt_sinir_AMACTAN_buyuk_olamaz():
    """Alt sinir, bulunan planin degerinden buyukse bir sey ters demektir.

    ⚠ Bu testin gorevi cozucuyu degil, BIZIM okumamizi denetlemek: yanlis
      alani okusaydik (ornegin amaci iki kez yazsaydik) sessizce gecerdi.
    """
    c = coz(_sahne(), {"azami_saniye": 20})
    ist = c.get("cozum_istatistikleri") or {}
    amac, sinir = ist.get("amac_degeri"), ist.get("alt_sinir")
    assert amac is not None and sinir is not None, (amac, sinir)
    assert sinir <= amac + 1e-6, (
        "alt sinir amactan buyuk: %s > %s" % (sinir, amac))


def test_PLAN_YOKSA_alt_sinir_bildirilmez():
    """Plan yoksa "0" demek yaniltici olurdu -- None doner."""
    g = _sahne(kisi=1)
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 9, "hedef": 9}
                  for s in range(9, 17)]
    c = coz(g, {"azami_saniye": 10})
    assert c["durum"] == "cozumsuz", c["durum"]
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("alt_sinir") is None, (
        "plan yokken alt sinir bildirildi: %r" % ist.get("alt_sinir"))
