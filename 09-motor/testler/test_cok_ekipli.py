# -*- coding: utf-8 -*-
"""
COK EKIPLI CALISAN -- kime sayilir? (T-21, K-50)

NE VARDI (16 Eylul dis incelemesi)
  Cozucu `x[calisan, gun, sablon]` tutuyor; iki ekibe uye biri tek
  vardiyayla IKI ekibin kapsama toplamina giriyordu. Dogrulayici ise
  atamanin `ekip` alanina (ilk ekip) bakiyordu: ayni plan icin cozucu
  "%100", dogrulayici "%50" diyordu. Kayit bunu "modelin inanci yanlis"
  diye acti.

KARAR (K-50, 1 Ekim, Mustafa) -- modelin inanci DOGRUYMUS:
  "Sahada hem satis hem backoffice yapabilen elemanlar var. O saatte o
   eleman iki birim elemani icin yer doldurmus sayilir. Gece 12'den sonra
   backoffice talebi yok denecek kadar azaliyor; oraya asil isi satis ama
   backoffice yetenegi olan bir eleman konuyor, sorun sahada cozulmus
   oluyor. Zaten firmalar da eleman acigini boyle yapiyor."

  Varsayilan sayim `hepsi`: atama, kisinin uye oldugu BUTUN ekiplere
  sayilir; dogrulayici da ayni olcuyu kullanir (degisen taraf dogrulayici).
  Baska ekibin vardiyasiyla kapatilan hucreler `metrikler.baska_ekipten_
  kapsama`da gorunur. Kiraci `cok_ekipli_sayim: "tek"` derse atama yalniz
  vardiyanin ekibine sayilir (ekipsiz sablonda ilk ekibe).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_cok_ekipli.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model                                # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5}
KURALLAR = [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False,
             "kabul_edilebilir": False}]


def _sahne(calisanlar, sablonlar, talep, mod=None):
    g = {"profil": "DENGELI", "calisanlar": calisanlar,
         "vardiya_sablonlari": sablonlar, "talep": talep,
         "kurallar": list(KURALLAR), "kilitler": [], "donmus_gunler": []}
    if mod is not None:
        g["cok_ekipli_sayim"] = mod
    return g


def _kisi(kimlik, ekipler):
    return {"id": kimlik, "ekipler": list(ekipler),
            "sozlesme": {"tip": "tam_zamanli"}, "izinler": [], "uygunluk": []}


V_SATIS = {"id": "V-SATIS", "ekip": "SATIS", "bas": 8, "bit": 16, "mola_dk": 0}
V_BACK = {"id": "V-BACK", "ekip": "BACKOFFICE", "bas": 8, "bit": 16, "mola_dk": 0}
V_GECE_S = {"id": "V-GECE-S", "ekip": "SATIS", "bas": 0, "bit": 8, "mola_dk": 0}
V_ORTAK = {"id": "V-ORTAK", "bas": 8, "bit": 16, "mola_dk": 0}      # ekipsiz


def _talep(ekip, gun, saat, asgari, hedef=None):
    return {"ekip": ekip, "gun": gun, "saat": saat, "asgari": asgari,
            "hedef": asgari if hedef is None else hedef}


# ----------------------------------------------------------------------
# 1. Varsayilan: `hepsi` -- Mustafa'nin sahasi
# ----------------------------------------------------------------------

def test_MUSTAFANIN_ORNEGI_gece_backoffice_talebini_satisci_karsilar():
    """Gece 00-08: satis 1 kisi, backoffice 1 kisi istiyor. Tek kisi var:
    asil isi satis, backoffice yetenegi de var. Eski dogrulayici %50 derdi;
    simdi iki taraf da 'tamam' der ve baska ekipten kapsama GORUNUR."""
    g = _sahne([_kisi("C1", ["SATIS", "BACKOFFICE"])], [V_GECE_S],
               [_talep("SATIS", 0, 2, 1), _talep("BACKOFFICE", 0, 2, 1)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    assert len(c["atamalar"]) == 1 and c["atamalar"][0]["ekip"] == "SATIS"
    assert c["metrikler"]["asgari_kapsama_yuzde"] == 100.0, c["metrikler"]
    r = degerlendir(g, c["atamalar"])
    assert not r["ihlaller"], r["ihlaller"]
    assert r["metrikler"]["asgari_kapsama_yuzde"] == 100.0
    bk = r["metrikler"]["baska_ekipten_kapsama"]
    assert bk == {"mod": "hepsi", "hucre": 1, "kisi_saat": 1}, bk


def test_T21_SAHNESI_iki_taraf_ANLASIR():
    """Risk kaydindaki sahne: tek kisi, iki ekip, ayni saat, her ekip 1 kisi.
    Cozucu 'cozuldu, 1 atama' diyordu, dogrulayici '%50'. Artik ikisi de
    '%100' der -- modelin inanci dogruydu, dogrulayici degisti."""
    g = _sahne([_kisi("C1", ["E1", "E2"])],
               [dict(V_SATIS, id="V-E1", ekip="E1"), dict(V_BACK, id="V-E2", ekip="E2")],
               [_talep("E1", 0, 10, 1), _talep("E2", 0, 10, 1)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu" and len(c["atamalar"]) == 1, c.get("atamalar")
    r = degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    assert r["metrikler"]["asgari_kapsama_yuzde"] == c["metrikler"]["asgari_kapsama_yuzde"] == 100.0


def test_VARSAYILAN_mod_hepsi_dir():
    g = _sahne([_kisi("C1", ["E1", "E2"])], [V_ORTAK], [])
    assert "cok_ekipli_sayim" not in g
    assert Model(g).cok_ekipli_sayim == "hepsi"
    from dogrulayici.kurallar import cok_ekipli_sayim
    assert cok_ekipli_sayim(g) == "hepsi"
    assert cok_ekipli_sayim(dict(g, cok_ekipli_sayim="sacma")) == "hepsi"


def test_tek_ekipli_kisi_BASKA_ekibe_sayilmaz():
    """Yetenek yoksa yer doldurma da yok: C1 yalniz satista. Backoffice
    talebi karsilanamaz -> cozumsuz; iki taraf da ayni seyi soyler."""
    g = _sahne([_kisi("C1", ["SATIS"])], [V_SATIS, V_BACK],
               [_talep("SATIS", 0, 10, 1), _talep("BACKOFFICE", 0, 10, 1)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", c["durum"]
    plan = [{"calisan": "C1", "ekip": "SATIS", "sablon": "V-SATIS", "gun": 0,
             "bas": 8, "bit": 16, "molalar": []}]
    r = degerlendir(g, plan)
    assert [i["kural"] for i in r["ihlaller"]] == ["ASGARI_KAPSAMA"]
    assert r["metrikler"]["baska_ekipten_kapsama"]["hucre"] == 0


def test_NITELIK_de_ekiplerin_hepsine_sayilir():
    """Backoffice 'ingilizce' istiyor; tek ingilizce bilen C1 satis
    vardiyasinda ama backoffice uyesi de. `hepsi`: gereklilik karsilanir."""
    c1 = _kisi("C1", ["SATIS", "BACKOFFICE"]); c1["yetkinlikler"] = ["ingilizce"]
    g = _sahne([c1, _kisi("C2", ["BACKOFFICE"])], [V_SATIS, V_BACK],
               [_talep("SATIS", 0, 10, 1), _talep("BACKOFFICE", 0, 10, 1)])
    g["kurallar"].append({"kod": "YETKINLIK_KAPSAMASI", "tur": "SERT", "aktif": True,
                          "yasal": False, "kabul_edilebilir": True,
                          "parametreler": {"yetkinlik": "ingilizce", "ekip": "BACKOFFICE",
                                           "asgari": 1, "saatler": [10]}})
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not r["ihlaller"], r["ihlaller"]
    # Dogrulayici tek basina: C1 SATIS vardiyasinda, C2 BACKOFFICE'te.
    # Backoffice'in ingilizce gerekliligini SATIS vardiyasindaki C1 karsilar.
    plan = [{"calisan": "C1", "ekip": "SATIS", "sablon": "V-SATIS", "gun": 0,
             "bas": 8, "bit": 16, "molalar": []},
            {"calisan": "C2", "ekip": "BACKOFFICE", "sablon": "V-BACK", "gun": 0,
             "bas": 8, "bit": 16, "molalar": []}]
    r2 = degerlendir(g, plan)
    assert not [i for i in r2["ihlaller"] if i["kural"] == "YETKINLIK_KAPSAMASI"], r2["ihlaller"]


def test_SAHA_TABANI_ve_MOLA_KAPSAMASI_da_ayni_olcuyle():
    """SAHADA_ASGARI backoffice icin taban 1; sahadaki tek kisi satis
    vardiyasindaki cok ekipli C1. `hepsi`: taban tutar."""
    g = _sahne([_kisi("C1", ["SATIS", "BACKOFFICE"])], [V_SATIS, V_BACK],
               [_talep("SATIS", 0, 10, 1), _talep("BACKOFFICE", 0, 10, 0, 0)])
    g["kurallar"].append({"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
                          "yasal": False, "kabul_edilebilir": True,
                          "parametreler": {"asgari_sahada": 1}})
    g["kurallar"].append({"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True})
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] in ("SAHADA_ASGARI", "MOLA_KAPSAMASI")], r["ihlaller"]


def test_cikti_ekibi_VARDIYANIN_ekibidir():
    """Cok ekipli C1 backoffice vardiyasina atanirsa cikti BACKOFFICE yazar
    (eskiden kisinin ilk ekibi SATIS yazilirdi). Ekipsiz sablonda ilk ekip."""
    g = _sahne([_kisi("C1", ["SATIS", "BACKOFFICE"])], [V_BACK],
               [_talep("BACKOFFICE", 0, 10, 1)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu" and c["atamalar"][0]["ekip"] == "BACKOFFICE", c.get("atamalar")
    g2 = _sahne([_kisi("C1", ["SATIS", "BACKOFFICE"])], [V_ORTAK],
                [_talep("BACKOFFICE", 0, 10, 1)])
    c2 = coz(g2, AYAR)
    assert c2["durum"] == "cozuldu" and c2["atamalar"][0]["ekip"] == "SATIS", c2.get("atamalar")
    assert not any("K-50" in n for n in c2["uygulanmayan_notlar"])


# ----------------------------------------------------------------------
# 2. Kiraci secimi: `tek` -- atama yalniz vardiyanin ekibine
# ----------------------------------------------------------------------

def test_TEK_tek_kisi_iki_ekibi_ayni_anda_DOLDURAMAZ():
    g = _sahne([_kisi("C1", ["E1", "E2"])],
               [dict(V_SATIS, id="V-E1", ekip="E1"), dict(V_BACK, id="V-E2", ekip="E2")],
               [_talep("E1", 0, 10, 1), _talep("E2", 0, 10, 1)], mod="tek")
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", (c["durum"], c.get("atamalar"))


def test_TEK_farkli_gunlerde_iki_ekibe_de_atanir_cikti_dogru():
    g = _sahne([_kisi("C1", ["E1", "E2"])],
               [dict(V_SATIS, id="V-E1", ekip="E1"), dict(V_BACK, id="V-E2", ekip="E2")],
               [_talep("E1", 0, 10, 1), _talep("E2", 1, 10, 1)], mod="tek")
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    assert {(a["gun"], a["ekip"]) for a in c["atamalar"]} == {(0, "E1"), (1, "E2")}
    r = degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_TEK_dogrulayici_da_tek_sayar():
    """`tek` modda satis vardiyasindaki cok ekipli kisi backoffice
    kapsamasina SAYILMAZ -- dogrulayici ihlal yazar."""
    g = _sahne([_kisi("C1", ["SATIS", "BACKOFFICE"])], [V_SATIS],
               [_talep("SATIS", 0, 10, 1), _talep("BACKOFFICE", 0, 10, 1)], mod="tek")
    plan = [{"calisan": "C1", "ekip": "SATIS", "sablon": "V-SATIS", "gun": 0,
             "bas": 8, "bit": 16, "molalar": []}]
    r = degerlendir(g, plan)
    assert [i["kural"] for i in r["ihlaller"]] == ["ASGARI_KAPSAMA"], r["ihlaller"]
    assert r["metrikler"]["baska_ekipten_kapsama"] == {"mod": "tek", "hucre": 0, "kisi_saat": 0}


def test_TEK_ekipsiz_sablon_ILK_ekibe_sayilir_ve_NOT_yazar():
    g = _sahne([_kisi("C1", ["E1", "E2"])], [V_ORTAK],
               [_talep("E2", 0, 10, 1)], mod="tek")
    k = Model(g).kur()
    assert any("K-50" in n and "V-ORTAK" in n for n in k.notlar), k.notlar
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", c["durum"]


def test_TEK_nitelik_ve_saha_tabani_da_tek_sayar():
    c1 = _kisi("C1", ["E1", "E2"]); c1["yetkinlikler"] = ["ingilizce"]
    g = _sahne([c1, _kisi("C2", ["E2"])],
               [dict(V_SATIS, id="V-E1", ekip="E1"), dict(V_BACK, id="V-E2", ekip="E2")],
               [_talep("E1", 0, 10, 1), _talep("E2", 0, 10, 1)], mod="tek")
    g["kurallar"].append({"kod": "YETKINLIK_KAPSAMASI", "tur": "SERT", "aktif": True,
                          "yasal": False, "kabul_edilebilir": True,
                          "parametreler": {"yetkinlik": "ingilizce", "ekip": "E2",
                                           "asgari": 1, "saatler": [10]}})
    assert coz(g, AYAR)["durum"] == "cozumsuz"
    g2 = _sahne([_kisi("C1", ["E1", "E2"]), _kisi("C2", ["E1"])],
                [dict(V_SATIS, id="V-E1", ekip="E1"), dict(V_BACK, id="V-E2", ekip="E2")],
                [_talep("E1", 0, 10, 2), _talep("E2", 0, 10, 0, 0)], mod="tek")
    g2["kurallar"].append({"kod": "SAHADA_ASGARI", "tur": "SERT", "aktif": True,
                           "yasal": False, "kabul_edilebilir": True,
                           "parametreler": {"asgari_sahada": 1}})
    assert coz(g2, AYAR)["durum"] == "cozumsuz"


def test_TEK_teshis_mumkun_sayisi_baska_ekibin_vardiyasini_SAYMAZ():
    """E2 14:00'te 1 kisi istiyor; V-E2 (12-20) ulasiyor. C1 (E1+E2) 16-20
    arasi uygun degil -- V-E2'ye giremez; V-E1 (8-16) saat 14'u kapsar ama
    `tek` modda E2'ye sayilmaz -> mumkun 0."""
    v_e2 = {"id": "V-E2", "ekip": "E2", "bas": 12, "bit": 20, "mola_dk": 0}
    c1 = _kisi("C1", ["E1", "E2"])
    c1["uygunluk"] = [{"tip": "uygun_degil", "gun": 0, "bas": 16, "bit": 20}]
    g = _sahne([c1], [dict(V_SATIS, id="V-E1", ekip="E1"), v_e2],
               [_talep("E2", 0, 14, 1)], mod="tek")
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", c["durum"]
    assert c["teshis"].get("kapsam") == "hucre" and c["teshis"].get("mumkun") == 0, c["teshis"]
