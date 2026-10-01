# -*- coding: utf-8 -*-
"""
SABIT ATAMA VE SABITLEME KILIDI: SAAT+EKIP ILE ESLEME, IKI TARAFTA (T-38, 1 Ekim)

NEDEN
  #11.2 ornegi sabit atamayi `{calisan, ekip, gun, bas, bit}` yaziyor; motor
  onu yalniz `sablon` kimliginden esliyordu. Ornekteki satir "modele girmedi"
  notuyla sessizce dusuyordu ve dogrulayici sabit atamalari HIC
  denetlemiyordu: yonetici "bu kisi sali 08-16" dese, motor atlasa, kimse
  gormezdi. Sabitleme kilidi ise ekibe bakmadan ilk saat eslesmesini
  aliyordu: iki ekibin ayni saatli sablonu varsa yanlis ekip.

SIMDI
  Sabit atama = sabitleme kilidi. Ikisi de `sablon` ya da `ekip`+`bas`+`bit`
  ile eslenir (kisinin atanabilecegi sablonlar icinde, ekip verilmisse o
  ekibin), eslesmezse not; dogrulayici KILIT_UYUMU ikisini de denetler.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_sabit_atama.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 2, "iki_asama_esigi": 10 ** 9}


def _sahne():
    """Iki ekip (A, B); ikisinde de 08-16 sablonu var; C1 A'da, C2 B'de, C3 ikisinde."""
    kurallar = [{"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
                 "kabul_edilebilir": False}
                for k in ("ASGARI_KAPSAMA", "KILIT_UYUMU", "CAKISMA_YOK")]
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["A"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
            {"id": "C2", "ekipler": ["B"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
            {"id": "C3", "ekipler": ["A", "B"], "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
        ],
        "vardiya_sablonlari": [
            {"id": "A08", "ekip": "A", "bas": 8, "bit": 16, "mola_dk": 60, "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
            {"id": "B08", "ekip": "B", "bas": 8, "bit": 16, "mola_dk": 60, "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
            {"id": "A14", "ekip": "A", "bas": 14, "bit": 22, "mola_dk": 60, "gece_vardiyasi": True,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
        ],
        "talep": [{"ekip": e, "gun": 1, "saat": s, "asgari": 1, "hedef": 1}
                  for e in ("A", "B") for s in range(8, 16)],
        "kurallar": kurallar, "kilitler": [], "donmus_gunler": [], "sabit_atamalar": [],
    }


def _atama(c, gun):
    return [(a["calisan"], a["sablon"]) for a in c["atamalar"] if a["gun"] == gun]


# ---- cozucu -------------------------------------------------------------

def test_sabit_atama_SAAT_ve_EKIP_ile_eslenir():
    g = _sahne()
    # Talep yalniz gun 1'de; gun 3'e sabit atama -> kapsama istemese de C1 A08'de olmali.
    g["sabit_atamalar"] = [{"calisan": "C1", "ekip": "A", "gun": 3, "bas": 8, "bit": 16}]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert ("C1", "A08") in _atama(c, 3), _atama(c, 3)
    assert not any("sabit atama" in n for n in c["uygulanmayan_notlar"]), c["uygulanmayan_notlar"]


def test_sabit_atama_SABLON_kimligiyle_de_eslenir():
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C1", "gun": 3, "sablon": "A14"}]
    c = coz(g, AYAR)
    assert ("C1", "A14") in _atama(c, 3)


def test_cok_ekipli_kisi_icin_EKIP_dogru_sablonu_secer():
    """C3 iki ekipte; 'ekip B, 08-16' A08'e degil B08'e baglanmali."""
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C3", "ekip": "B", "gun": 3, "bas": 8, "bit": 16}]
    c = coz(g, AYAR)
    assert ("C3", "B08") in _atama(c, 3), _atama(c, 3)
    assert ("C3", "A08") not in _atama(c, 3)


def test_sabitleme_KILIDI_ekibe_bakar_yanlis_ekip_not_duser():
    """Eski kod ekibe bakmadan ilk saat eslesmesini aliyordu (A08) ve C2 icin
    'ekibinde olmayan sablon' notu dusuyordu; simdi B08'e eslenir."""
    g = _sahne()
    g["kilitler"] = [{"calisan": "C2", "ekip": "B", "gun": 3, "bas": 8, "bit": 16}]
    c = coz(g, AYAR)
    assert ("C2", "B08") in _atama(c, 3), (_atama(c, 3), c["uygulanmayan_notlar"])
    assert not any("kilit" in n for n in c["uygulanmayan_notlar"]), c["uygulanmayan_notlar"]


def test_eslesmeyen_sabit_atama_NOT_duser_plani_cozumsuz_etmez():
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C1", "ekip": "A", "gun": 3, "bas": 9, "bit": 17},   # sablon yok
                           {"calisan": "C1", "ekip": "B", "gun": 4, "bas": 8, "bit": 16}]   # C1 B'de degil
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    notlar = [n for n in c["uygulanmayan_notlar"] if n.startswith("sabit atama")]
    assert len(notlar) == 2, c["uygulanmayan_notlar"]
    assert any("09:00-17" in n or "9-17" in n for n in notlar), notlar
    assert not _atama(c, 3) and not _atama(c, 4)


# ---- dogrulayici --------------------------------------------------------

def _tanim():
    return {"kod": "KILIT_UYUMU", "tur": "SERT", "aktif": True, "kabul_edilebilir": False}


def _satir(c, ekip, sablon, gun, bas, bit):
    return {"calisan": c, "ekip": ekip, "sablon": sablon, "gun": gun, "bas": bas, "bit": bit,
            "molalar": []}


def test_dogrulayici_sabit_atama_planda_YOKSA_ihlal():
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C1", "ekip": "A", "gun": 3, "bas": 8, "bit": 16}]
    assert K.kilit_uyumu(g, [_satir("C1", "A", "A08", 3, 8, 16)], _tanim()) == []
    i = K.kilit_uyumu(g, [_satir("C1", "A", "A14", 3, 14, 22)], _tanim())
    assert len(i) == 1 and "sabit atama planda yok" in i[0]["mesaj"] and i[0]["gun"] == 3
    assert i[0]["agirlik"] == "SERT" and not i[0].get("kabul_edilebilir")


def test_dogrulayici_sabit_atama_SABLON_biciminde_de_denetlenir():
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C1", "gun": 3, "sablon": "A14"}]
    assert K.kilit_uyumu(g, [_satir("C1", "A", "A14", 3, 14, 22)], _tanim()) == []
    assert len(K.kilit_uyumu(g, [_satir("C1", "A", "A08", 3, 8, 16)], _tanim())) == 1


def test_dogrulayici_EKIP_yazilmamissa_ekibe_bakmaz_yazilmissa_bakar():
    g = _sahne()
    g["kilitler"] = [{"calisan": "C3", "gun": 3, "bas": 8, "bit": 16}]          # ekipsiz
    assert K.kilit_uyumu(g, [_satir("C3", "A", "A08", 3, 8, 16)], _tanim()) == []
    g["kilitler"] = [{"calisan": "C3", "ekip": "B", "gun": 3, "bas": 8, "bit": 16}]
    assert len(K.kilit_uyumu(g, [_satir("C3", "A", "A08", 3, 8, 16)], _tanim())) == 1
    assert K.kilit_uyumu(g, [_satir("C3", "B", "B08", 3, 8, 16)], _tanim()) == []


def test_dogrulayici_bicimi_taninmayan_sabit_atama_ihlal():
    g = _sahne()
    g["sabit_atamalar"] = [{"calisan": "C1", "gun": 3}]
    i = K.kilit_uyumu(g, [], _tanim())
    assert len(i) == 1 and "bicimi taninmadi" in i[0]["mesaj"]
