# -*- coding: utf-8 -*-
"""
"FAZLA MESAI" TEK TANIMDIR: YASAL (K-57, 2 Ekim)

NE VARDI (T-60 olcumu, 2 Ekim)
  Ayni plan icin uc ayri "fazla mesai" sayisi vardi:
    cozucunun cezaladigi (`fm_`)    : calisma suresi (butun molalar dusuk)
                                      sozlesme ustu            ->   5-10 saat
    dogrulayici metrigi             : UCRET saati (yalniz ucretsiz mola
                                      dusuk) sozlesme ustu     -> 116-125 saat
    motorun kendi metrigi           : brut - sablonun mola_dk'si -> 117-127 saat
  Ucu de `fazla_mesai_saat` adini tasiyordu. Yonetici ekranda 120 saat
  gorup "motor fazla mesaiyi optimize etmiyor" diyecekti; motor 5 saati
  optimize ediyordu.

KARAR (Mustafa, 2 Ekim): "Fazla mesai bizim icin cok onemli bir kriter ...
  yasal tanimi kabul edecegiz." Yani:
    fazla mesai = CALISMA SURESI (ara dinlenmeleri dusulmus, Is K. md. 68)
                  - sozlesme saati, sifirdan kucukse sifir.
    yari zamanliya fazla mesai yazilmaz: 45 saate kadar carpan ayni, bu
    "yari zamanlinin ek mesaisi"dir, firma icin risk degildir.
  Ucret saati farki kaybolmaz: `sozlesme_ustu_ucret_saat` (K-32 cumle 10).

SINANAN
  - dogrulayici metrigi yasal tanimla sayar; ucret farki ayri alanda
  - yari zamanli iki alanda da sayilmaz
  - motorun metrigi == cezaladigi dakika / 60 == dogrulayicinin metrigi
    (ucu AYNI plan uzerinde, ucretli dinlenme molasi olan sablonla)

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_fazla_mesai_tanimi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 3, "iki_asama_esigi": 10 ** 9}

# 09-18: 60 dk ucretsiz yemek + 2 x 15 dk UCRETLI dinlenme.
#   brut 9 · calisma 7,5 · ucret 8
POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 2, "ucretli": True}]
# `mola_dk` BILEREK 60 (yalniz yemek): eski motor metrigi "brut - mola_dk"
# sayiyordu ve 8 saat verirdi; dogrusu politikadan 7,5. Mutasyon bunu yakalar.
SABLON = {"id": "V9", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60,
          "gece_vardiyasi": False, "mola_politikasi": POLITIKA}


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sahne(tip="tam_zamanli", haftalik=36):
    soz = {"tip": tip, "gun_sayisi": 5}
    if haftalik is not None:
        soz["haftalik_saat"] = haftalik
    return {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C1", "ekipler": ["E"], "sozlesme": soz, "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": [dict(SABLON)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(5) for s in range(9, 18)],
        "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HAFTA_TATILI"),
                     _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10), _kural("CAKISMA_YOK")],
        "kilitler": [], "donmus_gunler": [],
    }


def _atama(gun):
    return {"calisan": "C1", "ekip": "E", "sablon": "V9", "gun": gun, "bas": 9, "bit": 18,
            "molalar": [{"bas": 12, "bit": 13, "tip": "yemek"},
                        {"bas": 10.5, "bit": 10.75, "tip": "dinlenme"},
                        {"bas": 15.5, "bit": 15.75, "tip": "dinlenme"}]}


# ---- dogrulayici --------------------------------------------------------

def test_dogrulayici_fazla_mesai_YASAL_tanimla_ucret_farki_ayri_alanda():
    """5 gun x 7,5 saat calisma = 37,5; sozlesme 36 -> fazla mesai 1,5.
    Ucret: 5 x 8 = 40 -> sozlesme ustu ucret 4,0. Ikisi ayni anda dogru."""
    r = degerlendir(_sahne(), [_atama(d) for d in range(5)])
    m = r["metrikler"]
    assert m["fazla_mesai_saat"] == 1.5, m
    assert m["sozlesme_ustu_ucret_saat"] == 4.0, m
    assert m["toplam_saat"] == 37.5 and m["ucret_saat"] == 40.0 and m["brut_saat"] == 45.0, m


def test_dogrulayici_sozlesme_altinda_kalan_sifir():
    r = degerlendir(_sahne(haftalik=45), [_atama(d) for d in range(5)])
    m = r["metrikler"]
    assert m["fazla_mesai_saat"] == 0.0 and m["sozlesme_ustu_ucret_saat"] == 0.0, m


def test_dogrulayici_yari_zamanliya_fazla_mesai_YAZILMAZ():
    """Sozlesme saati olsa bile (eski veri): 45 saate kadar ek mesai, carpan
    ayni (Mustafa, K-57). Iki alanda da 0."""
    r = degerlendir(_sahne(tip="yari_zamanli", haftalik=20), [_atama(d) for d in range(5)])
    m = r["metrikler"]
    assert m["fazla_mesai_saat"] == 0.0 and m["sozlesme_ustu_ucret_saat"] == 0.0, m
    assert m["toplam_saat"] == 37.5


# ---- cozucu: uc sayi ayni plan uzerinde AYNI ------------------------------

def test_motor_metrigi_cezaladigi_dakikayla_ve_dogrulayiciyla_AYNI():
    """Asgari kapsama 5 gun 09-18'i zorlar: 5 x 7,5 = 37,5 calisma, sozlesme
    36 -> 1,5 saat fazla mesai. Uc kaynak ayni sayiyi vermeli:
      motorun metrigi, cezaladigi dakika / 60, dogrulayicinin metrigi."""
    g = _sahne()
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", (c.get("durum"), c.get("uygulanmayan_notlar"))
    fm_ceza = c["cozum_istatistikleri"]["amac_dagilimi"]["FAZLA_MESAI"]
    assert fm_ceza["deger"] == 90, fm_ceza                       # dakika
    assert c["metrikler"]["fazla_mesai_saat"] == 1.5, c["metrikler"]
    assert c["metrikler"]["toplam_saat"] == 37.5, c["metrikler"]
    r = degerlendir(g, c["atamalar"])
    assert r["metrikler"]["fazla_mesai_saat"] == 1.5, r["metrikler"]
    assert r["metrikler"]["sozlesme_ustu_ucret_saat"] == 4.0, r["metrikler"]
    # Ceza agirligi tablodan: 50/dakika (urun davranisi degismedi).
    assert fm_ceza["ceza"] == 90 * 50, fm_ceza


def test_motor_metrigi_yari_zamanliya_fazla_mesai_YAZMAZ():
    """Eski veride yari zamanlinin sozlesme saati olabilir (20): 37,5 saat
    calissa da fazla mesai 0 -- ceza da metrik de yazmaz."""
    g = _sahne(tip="yari_zamanli", haftalik=20)
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert c["metrikler"]["fazla_mesai_saat"] == 0.0, c["metrikler"]
    assert "FAZLA_MESAI" not in (c["cozum_istatistikleri"]["amac_dagilimi"] or {})


def test_fazla_mesai_agirligi_tablodan_ve_kiraci_ezebilir():
    """T-60 agirlik dengesi deneyi bu kapidan olcer: `agirliklar` ile
    FAZLA_MESAI agirligi ezilince ceza o agirlikla hesaplanir."""
    g = _sahne()
    g["agirliklar"] = {"FAZLA_MESAI": 5}
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    fm = c["cozum_istatistikleri"]["amac_dagilimi"]["FAZLA_MESAI"]
    assert fm["deger"] == 90 and fm["ceza"] == 90 * 5, fm
