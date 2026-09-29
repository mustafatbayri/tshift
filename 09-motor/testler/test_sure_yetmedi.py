# -*- coding: utf-8 -*-
"""
"IMKANSIZ" ILE "YETISTIREMEDIM" AYRI SEYLERDIR

⚠ NEDEN (Mustafa, 29 Eylul)
  Cozucu iki bambaska sebeple plansiz donebilir:

    INFEASIBLE : KANITLADI -- bu kurallarla, bu kadroyla boyle bir plan yok
    UNKNOWN    : SURE DOLDU -- arıyordu, yetistiremedi

  Ikisi de `durum: "cozumsuz"` diye cikiyordu. Ustelik ikisinde de motor
  TESHIS koyuyordu: her sert kurali tek tek gevsetip yeniden cozerek
  "engelleyen kural" ariyordu.

  Bunun iki ayri bedeli olculdu (29 Eylul, 35 kisilik sahne):

    1. YANLIS OLABILECEK CUMLE
       Teshis "su hucreyi su kural engelliyor" diyor. Ama hicbir sey
       kanitlanmadi. Bir yoneticiye "bu talebi bu kadroyla karsilamak
       imkansiz" demek, personel alimina kadar giden bir karardir.

    2. USTELIK BEDAVA DEGIL
       45 saniyelik butce -> satir TOPLAM 470 saniye surdu. Kullanici
       butcesini bekledikten sonra 7 dakika daha bekliyor, sonunda
       muhtemelen yanlis bir cumle aliyor.

BU DOSYA NE SINAR
  * kanitlanmis cozumsuzluk hala `cozumsuz` ve teshisi var
  * butce dolunca `sure_yetmedi` ve teshis KOSMUYOR
  * kullanici ISTERSE teshis kosuyor ("neden oldugunu arastir")
  * istenerek kosan teshis KESIN DEGIL diye isaretleniyor

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_sure_yetmedi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402


def _kurallar():
    return [
        {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
         "kabul_edilebilir": False}
        for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                  "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
    ] + [
        {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
         "parametreler": {"esik": 2}},
    ]


def _sahne(kisi, gun=7, asgari=3, hedef=6, saatler=(7, 23)):
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
            for j, b in enumerate((7, 9, 11, 13, 15))
        ],
        "talep": [{"ekip": "E", "gun": d, "saat": s,
                   "asgari": asgari, "hedef": hedef}
                  for d in range(gun) for s in range(*saatler)],
        "kurallar": _kurallar(),
        "kilitler": [], "donmus_gunler": [],
    }


def _imkansiz():
    """KANITLANABILIR cozumsuzluk: tek kisi, her saat 9 kisi isteniyor.

    Cozucu bunu saniyeler icinde KANITLAR -- "yetistiremedim" degil.
    """
    g = _sahne(1, gun=1, saatler=(9, 17))
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 9, "hedef": 9}
                  for s in range(9, 17)]
    return g


def _yetismez():
    """Cozulebilir ama COK KISA butce: cozucu bakmaya firsat bulamaz.

    ⚠ Sahne bilerek buyuk, butce bilerek 0.1 saniye. Amac "zor sahne"
      degil, MEKANIZMA: butce dolunca ne oluyor.

    ⚠ Iki asama bilerek KAPALI: acik kalsaydi birinci asama kendi
      butcesini (varsayilan 120 sn) harcar ve test dakikalarca surerdi.
    """
    return _sahne(60, gun=7)


KISA = {"azami_saniye": 0.1, "durgunluk_saniye": 0,
        "iki_asama_esigi": 10 ** 9}


def test_KANITLANMIS_cozumsuzluk_hala_cozumsuz():
    """Kanit varsa cevap degismemeli -- bu degisiklik onu bozmamali."""
    c = coz(_imkansiz(), {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz", c["durum"]
    assert c.get("teshis"), "kanitlanmis cozumsuzlukte teshis olmali"


def test_BUTCE_dolunca_SURE_YETMEDI_der():
    """Plan bulunamadiysa ama kanitlanmadiysa, adi baska olmali."""
    c = coz(_yetismez(), KISA)
    assert c["durum"] == "sure_yetmedi", (
        "butce dolunca 'sure_yetmedi' beklenirdi: %r" % c["durum"])


def test_sure_yetmedigi_zaman_TESHIS_KOSMAZ():
    """Asil kazanc bu: cevapsiz soruya 7 dakika harcanmasin.

    ⚠ Sure olcerek degil YAPIYI sinayarak: zamana bagli test yavas bir
      makinede ilgisiz bir sebeple kirmizi yanar.
    """
    c = coz(_yetismez(), KISA)
    assert c["durum"] == "sure_yetmedi"
    t = c.get("teshis") or {}
    assert not t.get("engelleyen_kurallar"), (
        "sure yetmedigi halde kural gevsetme turu kosmus: %r" % t)
    assert not c.get("en_iyi_plan"), (
        "sure yetmedigi halde en iyi plan aranmis: %r" % c.get("en_iyi_plan"))


def test_sure_yetmedi_NE_YAPILACAGINI_soyler():
    """Kullanici ekranda ne gorecegini bilmeli: sure uzatilabilir."""
    c = coz(_yetismez(), KISA)
    assert c.get("verilen_saniye"), (
        "kac saniye verildigi bildirilmiyor: %r" % sorted(c))
    assert c.get("teshis_istenebilir") is True, (
        "'neden oldugunu arastir' secenegi bildirilmiyor: %r" % sorted(c))


def test_ISTENIRSE_teshis_kosar_ama_KESIN_DEGIL_der():
    """"Neden oldugunu arastir" dugmesi: teshis kullanici isterse kosar.

    ⚠ Kosan teshis yine de KANIT DEGILDIR -- ciktida boyle isaretlenir.
      Aksi halde ayni yanlis cumleyi bu kez dugme arkasindan soylerdik.
    """
    ayar = dict(KISA, teshis_iste=True)
    c = coz(_yetismez(), ayar)
    assert c["durum"] == "sure_yetmedi", c["durum"]
    assert c.get("teshis"), "istenmesine ragmen teshis yok"
    assert c.get("teshis_kesin") is False, (
        "butce dolmusken kosan teshis 'kesin' diye isaretlenmis: %r"
        % c.get("teshis_kesin"))


def test_KANITLANMIS_teshis_KESIN_der():
    """Kanitlanmis cozumsuzlukte teshis kesindir -- ayrim ciktida gorunmeli."""
    c = coz(_imkansiz(), {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz"
    assert c.get("teshis_kesin") is True, (
        "kanitlanmis cozumsuzlukte teshis kesin olmaliydi: %r"
        % c.get("teshis_kesin"))
