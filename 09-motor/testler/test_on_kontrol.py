# -*- coding: utf-8 -*-
"""
ON KONTROL -- ulasilamayan talep hucresi COZMEDEN bildirilir

NEDEN VAR (28 Eylul, gercekci veri setinde olculdu)
  350 kisilik 7/24 bir organizasyonda plan "cozumsuz" dondu. Sebep dogruydu
  ve motorun teshisi TAM YERINDEYDI:

      kapsam : hucre
      hucre  : SATIS, gun 0, saat 0
      gereken: 1   mumkun: 0
      engelleyen: ASGARI_KAPSAMA

  Pazartesi 00:00-06:00 arasinda talep var, ama o saatleri yalniz PAZAR
  GECESI baslayan bir vardiya kapatabilir -- ve Pazar, planlanan haftanin
  icinde degil. (Gercek hayattaki karsiligi T-28: onceki haftanin gece
  vardiyasi okunmuyor.)

  SORUN CEVAPTA DEGIL, CEVABIN FIYATINDA
    Bu teshis ancak cozucu cozumsuzlugu KANITLADIKTAN sonra hesaplaniyordu.
    Olculen sure: 105 kisilik sahnede **292 saniye**, 10 kisilik tek ekipte
    **73 saniye**. Ayni cevap, model kurulmadan, saniyenin altinda
    hesaplanabilir -- cunku soru basit: bu hucreye ULASAN bir sablon var mi.

  Kullanicinin gordugu fark: bes dakika bekleyip "cozumsuz" yerine, iki
  saniyede "gun 0 saat 0-6 hicbir vardiyayla kapatilamiyor".

NE DEGISMEDI
  Verilen CEVAP ayni. Degisen yalnizca ne zaman verildigi. Ulasilamayan
  hucre yoksa on kontrol sessizdir ve cozum normal akar.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_on_kontrol.py -v
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402


def _sahne(talep_saatleri, sablonlar=None):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, 5)
        ],
        "vardiya_sablonlari": sablonlar or [
            {"id": "V-GUNDUZ", "ekip": "E", "bas": 9, "bit": 17,
             "mola_dk": 60, "gunler": [0]},
        ],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 2}
                  for s in talep_saatleri],
        "kurallar": [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                      "yasal": False, "kabul_edilebilir": False}],
        "kilitler": [], "donmus_gunler": [],
    }


def test_ulasilamayan_hucre_COZUCU_CALISMADAN_bildirilir():
    """Cevap on kontrolden gelmeli -- cozucu hic kosmamali.

    ⚠ BU TESTIN ILK HALI SUREYE BAKIYORDU ve YAZILDIGI ANDA YESILDI:
      dort kisilik bir sahnede cozucu zaten milisaniyede bitiriyordu.
      Yani test, olcmek istedigi seyi hic olcmuyordu -- tam da Mustafa'nin
      "sahneler oyuncak oldugu icin sorun gorunmuyor" dedigi sey.

      Sure bir MAKINE ozelligidir, mekanizma degil. Test artik mekanizmayi
      sinar: `durma_sebebi` on kontrolu gostermeli ve cozucu SIFIR cozum
      denemis olmali.
    """
    g = _sahne([3, 4, 5])          # gece saatleri, yalniz gunduz sablonu var
    c = coz(g, {"azami_saniye": 60})
    assert c["durum"] == "cozumsuz", c["durum"]
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("durma_sebebi") == "on_kontrol", (
        "cevap on kontrolden gelmedi (durma_sebebi=%r) -- cozucu bosuna kostu"
        % ist.get("durma_sebebi"))
    assert ist.get("cozum_suresi_sn") == 0.0, (
        "cozucu calismis: %r sn" % ist.get("cozum_suresi_sn"))


def test_on_kontrol_TASLAK_uretmeye_calismaz():
    """Ulasilamayan hucre varsa `_en_iyi_plan` atlanir.

    Kurallari gevseterek taslak uretmek tam cozum suresi kadar surer ve
    ayni cevabi verir: o hucreyi HICBIR gevsetme kapatamaz, cunku
    kapatabilecek vardiya YOK. Sebep ciktida YAZILIR -- sessizce atlanmaz.
    """
    g = _sahne([3, 4, 5])
    c = coz(g, {"azami_saniye": 60})
    en_iyi = c.get("en_iyi_plan") or {}
    assert en_iyi.get("var") is False, "taslak uretilmeye calisilmis: %r" % en_iyi
    assert "sebep" in en_iyi, "taslagin neden yok oldugu yazilmamis: %r" % en_iyi


def test_teshis_HUCREYI_adiyla_soyluyor():
    """Cevap yalnizca 'cozumsuz' degil; hangi hucre oldugunu da soylemeli."""
    g = _sahne([3, 4, 5])
    c = coz(g, {"azami_saniye": 60})
    t = c.get("teshis") or {}
    assert t.get("kapsam") == "hucre", "teshis hucre seviyesinde degil: %r" % t
    h = t.get("hucre") or {}
    assert h.get("ekip") == "E" and h.get("saat") in (3, 4, 5), (
        "yanlis hucre gosterildi: %r" % h)
    assert t.get("mumkun") == 0, "mumkun %r olmali, %r geldi" % (0, t.get("mumkun"))


def test_ULASILABILIR_sahne_etkilenmez():
    """On kontrol sessiz kalmali: normal sahne normal cozulur.

    Geri donuk uyumun bekcisi. On kontrol fazla hevesli olursa cozulebilir
    planlari reddeder -- bu, cozumsuzlugu ge\u00e7 bildirmekten daha kotu olurdu.
    """
    g = _sahne([9, 10, 11, 12])
    c = coz(g, {"azami_saniye": 30})
    assert c["durum"] == "cozuldu", (
        "ulasilabilir sahne reddedildi: %s / %r"
        % (c.get("durum"), c.get("teshis")))
    assert c.get("atamalar"), "plan bos dondu"


def test_GECE_VARDIYASI_ulasabildigi_saatleri_kapatir():
    """Gece yarisini asan vardiya, TASTIGI gunun saatlerine ulasir.

    On kontrol Z-1'i bilmek zorunda: 23->07 vardiyasi gun 0'da baslarsa
    gun 1'in 00-06 saatlerini kapatir. Bunu bilmezse cozulebilir bir plani
    reddeder.
    """
    g = _sahne([0, 1, 2], sablonlar=[
        {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31,
         "mola_dk": 60, "gunler": [0, 1]},
    ])
    # Talep gun 0'in 00-02 saatlerinde; onu ancak gun -1 kapatabilir -> yok.
    c = coz(g, {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz", "gun 0'in gece saatleri kapatilamamali"

    # Ayni talep gun 1'de olsa, gun 0'in gece vardiyasi kapatir.
    g2 = _sahne([], sablonlar=[
        {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31,
         "mola_dk": 60, "gunler": [0, 1]},
    ])
    g2["talep"] = [{"ekip": "E", "gun": 1, "saat": s, "asgari": 1, "hedef": 1}
                   for s in (0, 1, 2)]
    c2 = coz(g2, {"azami_saniye": 30})
    assert c2["durum"] == "cozuldu", (
        "gun 0'da baslayan gece vardiyasi gun 1'in gece saatlerini "
        "kapatmaliydi: %s / %r" % (c2.get("durum"), c2.get("teshis")))
