# -*- coding: utf-8 -*-
"""
HEDEF_ASIMI -- hedefi asan kisi-saat ceza (K-53, T-54)

NE VARDI (29 Eylul)
  Talep asgari 1 kisi, sahnede 4 yari zamanli: cozucu DORDUNU de 45 saate
  doldurdu. Modelde bir saatin bedeli yoktu; hicbir kural "gereksiz yere
  kisi yazma" demiyordu. 350 kisilik sahnede plan hedefin 2 katini sahaya
  koyuyordu.

KARAR (K-53, Mustafa, 1 Ekim): "Ceza ile ilerleyelim. Ucret tarafi hic
  gelmeyebilir." YUMUSAK kural: hedefin ustune cikan her kisi-saat ceza;
  hedefin altinda kalmak (HEDEF_KAPSAMA) her profilde daha pahali.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_hedef_asimi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU               # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(kisi=4, asim=True, profil="DENGELI"):
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HAFTA_TATILI", yasal=True)]
    if asim:
        kurallar.append(_kural("HEDEF_ASIMI", tur="YUMUSAK"))
    return {"profil": profil,
            "calisanlar": [{"id": "P%d" % i, "ekipler": ["E"],
                            "sozlesme": {"tip": "yari_zamanli"},
                            "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
            "vardiya_sablonlari": [V],
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                      for d in range(5) for s in range(9, 18)],
            "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


def _plan(kisiler, gunler=range(5)):
    return [{"calisan": k, "ekip": "E", "sablon": "V", "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]}
            for k in kisiler for g in gunler]


# ----------------------------------------------------------------------
# 1. Dogrulayici
# ----------------------------------------------------------------------

def test_hedefin_ustundeki_hucre_YUMUSAK_ihlal():
    r = degerlendir(_sahne(), _plan(["P1", "P2", "P3"]))     # hedef 1, 3 kisi, 5x9 hucre
    ih = [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert len(ih) == 45, len(ih)
    assert all(i["agirlik"] == "YUMUSAK" and i["olculen"] == 3 and i["gereken"] == 1 for i in ih)
    assert "2 kisi fazla" in ih[0]["mesaj"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True        # yumusak


def test_hedefe_ESIT_ihlal_degil():
    r = degerlendir(_sahne(), _plan(["P1"]))
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]


def test_kural_yokken_yazilmaz():
    r = degerlendir(_sahne(asim=False), _plan(["P1", "P2"]))
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert "HEDEF_ASIMI" not in r["uygulanmayan_kurallar"]


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_T54_SAHNESI_bir_kisilik_talebe_dort_kisi_YAZILMAZ():
    """4 yari zamanli, talep hedef 1: ceza varken her hucrede tam 1 kisi;
    toplam atama 5 (gun basina 1). Karsi kanit kurulmaz -- cezasiz sahnede
    cozucunun fazladan yazip yazmamasi rastgeledir (T-54'un kendisi)."""
    g = _sahne()
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    assert len(c["atamalar"]) == 5, [(a["calisan"], a["gun"]) for a in c["atamalar"]]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"], r["ihlaller"]
    assert r["metrikler"]["hedef_kapsama_yuzde"] == 100.0


def test_HEDEF_altinda_kalmak_her_profilde_asmaktan_PAHALI():
    for profil in ("DENGELI", "KAPSAMA", "CALISAN"):
        assert AGIRLIK_TABLOSU["HEDEF_KAPSAMA"][profil] > AGIRLIK_TABLOSU["HEDEF_ASIMI"][profil], profil
    k = Model(_sahne(profil="KAPSAMA"))
    assert k._agirlik("HEDEF_ASIMI") == 1
    k2 = Model(_sahne(profil="CALISAN"))
    assert k2._agirlik("HEDEF_ASIMI") == 4


def test_TAM_zamanli_45_saat_tabani_cezaya_ragmen_DOLAR():
    """Ceza, sert tabani esmez: 45 saatlik tam zamanli (SAAT_DENGESI sert,
    tolerans 0) talep 1 kisi olsa da 45 saate tamamlanir; ceza yalniz
    fazlaligi en az hucreye yayar."""
    g = _sahne(kisi=2)
    g["vardiya_sablonlari"] = [dict(V, bit=17.5)]            # 7,5 net x 6 = 45
    for c in g["calisanlar"]:
        c["sozlesme"] = {"tip": "tam_zamanli", "haftalik_saat": 45, "gun_sayisi": 6}
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(6) for s in range(9, 17)]
    g["kurallar"] += [_kural("SAAT_DENGESI", tolerans_saat=0),
                      _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=45)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"], r["ihlaller"]
    assert len(c["atamalar"]) == 12                           # 2 kisi x 6 gun = 90 saat
    # Ceza fazlaligi EN AZA indirir: ikisi de talepsiz 7. gunu calisip
    # tatillerini FARKLI talep gunlerine koyar -> 4 gun cakisir, 4 x 8 = 32
    # hucre asim. (Ayni gunu tatil yapsalar 5 x 8 = 40 olurdu.)
    assert len([i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]) == 32
