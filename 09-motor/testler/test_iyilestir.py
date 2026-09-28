# -*- coding: utf-8 -*-
"""
PLANI IYILESTIR -- kaldigi yerden devam

NE YAPAR
  Var olan bir plani baslangic noktasi alarak daha iyisini arar. Sifirdan
  baslamaz; elde olani korur ve uzerine koyar.

NEDEN (Mustafa, 28 Eylul)
  Motor ayni girdiye her seferinde AYNI plani vermiyor -- sekiz arama iscisi
  paralel calisiyor ve hangisinin once iyi bir plan buldugu her kosuda
  degisiyor. Olculdu: 25 saniyede 21.905 ve 22.715.

  Tek isciyle tekrarlanabilir olur ama ayni surede uretilen plan 46 KAT
  kotu (olculdu: 1.010.039). Yani "her seferinde ayni" istemek, "her
  seferinde cok daha kotu" demek.

  Mustafa'nin sorusu buydu:
    > "Yonetici tekrar calistirdiginda daha iyi bir plan gelip
    >  gelmeyecegini nasil bilecek? Bunu bilmezse nasil guvenecek?"

  Cevap "yeniden uret" degil "IYILESTIR": plan ASLA KOTULESMEZ. Yonetici
  zar atmiyor, biriktiriyor.

NASIL
  Plan cozucuye ipucu (hint) olarak verilir. CP-SAT ipucunu bir baslangic
  cozumu olarak alir ve amaci KUCULTTUGU icin dondurdugu sonuc ipucundan
  kotu olamaz.

  Ipucu artik gecerli degilse (girdi degistiyse) sessizce yok sayilir --
  ama ciktida BILDIRILIR. Sessizce sifirdan baslamak, kullaniciya
  "iyilestirdim" deyip aslinda zar atmak olurdu.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_iyilestir.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402


def _sahne(kisi=20, gun=4):
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
            for j, b in enumerate((7, 10, 13))
        ],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 4, "hedef": 12}
                  for d in range(gun) for s in range(7, 21)],
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


def _amac(c):
    return (c.get("cozum_istatistikleri") or {}).get("amac_degeri")


def test_plan_IYILESTIRILEBILIR():
    """Kisa kosuyla plan uret, sonra onu baslangic alarak devam et."""
    g = _sahne()
    ilk = coz(g, {"azami_saniye": 4, "hedef_bosluk": 0.0, "durgunluk_saniye": 999})
    assert ilk["durum"] == "cozuldu", ilk["durum"]

    ikinci = coz(g, {"azami_saniye": 20, "hedef_bosluk": 0.0,
                     "durgunluk_saniye": 999},
                 baslangic_plani=ilk["atamalar"])
    assert ikinci["durum"] == "cozuldu", ikinci["durum"]
    assert _amac(ikinci) <= _amac(ilk), (
        "iyilestirme plani KOTULESTIRDI: %s -> %s" % (_amac(ilk), _amac(ikinci)))


def test_baslangic_plani_CIKTIDA_bildirilir():
    """Kullanici nereden baslandigini ve ne kazanildigini gormeli."""
    g = _sahne()
    ilk = coz(g, {"azami_saniye": 4, "hedef_bosluk": 0.0, "durgunluk_saniye": 999})
    ikinci = coz(g, {"azami_saniye": 15, "hedef_bosluk": 0.0,
                     "durgunluk_saniye": 999},
                 baslangic_plani=ilk["atamalar"])
    ist = ikinci.get("cozum_istatistikleri") or {}
    assert ist.get("baslangic_plani_kullanildi") is True, (
        "baslangic plani kullanilmadi ya da bildirilmedi: %r" % ist)
    assert ist.get("baslangic_amac") is not None, (
        "baslangic plani puani bildirilmedi: %r" % ist)


def test_GECERSIZ_baslangic_plani_sessizce_gecmez():
    """Ipucu tutmuyorsa bildirilir -- sessizce sifirdan baslanmaz.

    Kullaniciya "iyilestirdim" deyip aslinda zar atmak, guveni bu ozelligin
    cozmeye calistigindan daha cok bozardi.
    """
    g = _sahne()
    sahte = [{"calisan": "YOK", "ekip": "E", "sablon": "YOKSABLON",
              "gun": 0, "bas": 7, "bit": 15, "molalar": []}]
    c = coz(g, {"azami_saniye": 10}, baslangic_plani=sahte)
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("baslangic_plani_kullanildi") is False, (
        "gecersiz plan kullanilmis gibi bildirildi: %r" % ist)


def test_baslangic_plani_YOKSA_davranis_degismez():
    """Geriye donuk uyum: plan verilmezse her sey eskisi gibi."""
    g = _sahne(kisi=10, gun=1)
    c = coz(g, {"azami_saniye": 15})
    assert c["durum"] == "cozuldu", c["durum"]
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("baslangic_plani_kullanildi") is False
    assert ist.get("baslangic_amac") is None
