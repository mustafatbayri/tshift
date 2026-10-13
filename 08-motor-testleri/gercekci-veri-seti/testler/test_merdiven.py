# -*- coding: utf-8 -*-
"""
MERDIVEN SEVIYE 1 -- bekciler (K-62, K-67; Mustafa 12 Ekim 22:03-22:11)

  (a) REFERANS BEKCISI: kayitli referans plan, kayitli seviye 1 sahnesinde
      bagimsiz dogrulayicidan 0 sert, 0 asim, 0 eksik, fazla mesai 0 ile
      gecer -- 500 kisilik ve kucuk kopya, COZUCUSUZ (saniyeler). Setin butun
      degeri "cevabi bilinen set" olmasi; dogrulayicida saat sayimi ya da bir
      kural degisir de referans artik gecmezse olcumlerin "bilinen cevabi"
      sessizce curur. Bu bekci onu yakalar.
  (b) KUCUK KOPYA: olcek 0.1 seviye 1 seti her test kosusunda SIFIRDAN cozulur;
      plan cikar, asim 0, sert 0, fazla mesai 0. Motorda HEDEF_ASIMI SERT'i
      bozan ya da siki seti cozulemez yapan degisiklik burada kirmizi yanar.
  (c) Eski S30 setleri ve bekcileri AYNEN (test_gercekci_olcek.py); burada
      yalniz tarihsel turlerinin degismedigine bakilir.
  500 kisilik COZUM bekcisi ayri ve haftalik (Mustafa 22:11):
  `TSHIFT_MERDIVEN_500=1` ile kosar (.github/workflows/haftalik-merdiven.yml);
  normal kosuda BILEREK atlanir ve atlandigi satirda bunu soyler.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_merdiven.py -v
"""

import copy
import io
import json
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import merdiven as MD                                          # noqa: E402

OLCEKLER = [1.0, 0.1]


def _yukle(yol):
    assert os.path.exists(yol), (
        "%s YOK -- seviye 1 seti uretilmemis. Uretim: py merdiven.py referans "
        "--olcek <olcek> --saniye 900 (K-62: referans Mustafa'nin makinesinde)" % yol)
    return json.load(io.open(yol, encoding="utf-8"))


@pytest.fixture(scope="module", params=OLCEKLER, ids=["500", "0.1"])
def set_ve_referans(request):
    o = request.param
    return o, _yukle(MD.sahne_yolu(o)), _yukle(MD.referans_yolu(o))


# ----------------------------------------------------------------------
# (a) Referans bekcisi
# ----------------------------------------------------------------------

def test_REFERANS_seviye1_sahnesinde_TEMIZ_sert_asim_eksik_fazla_mesai_SIFIR(set_ve_referans):
    o, g, ref = set_ve_referans
    d = MD.referans_denetle(g, ref["atamalar"])
    assert d == {"sert": 0, "sert_kurallar": [], "asim": 0, "eksik": 0,
                 "fazla_mesai_saat": 0.0, "yayinlanabilir": True}, (o, d)


def test_SEVIYE1_tabanla_AYNI_yalniz_talep_ve_HEDEF_ASIMI_turu_degisir(set_ve_referans):
    """Kisiler, sablonlar, kurallar (HEDEF_ASIMI turu haric) uretici tabaniyla
    birebir; talep hucreleri ayni, hedef referans sayimi, asgari = hedef - 1
    (en az 1; hedef 0 ise 0)."""
    o, g, ref = set_ve_referans
    t = MD.taban_sahne(o)
    for alan in ("calisanlar", "vardiya_sablonlari", "kilitler", "departmanlar"):
        assert g[alan] == t[alan], (o, alan)
    kg = {k["kod"] + str(i): k for i, k in enumerate(g["kurallar"])}
    kt = {k["kod"] + str(i): k for i, k in enumerate(t["kurallar"])}
    assert kg.keys() == kt.keys()
    for a in kg:
        if kg[a]["kod"] == "HEDEF_ASIMI":
            assert kt[a]["tur"] == "YUMUSAK" and kg[a]["tur"] == "SERT"      # K-67
            assert dict(kg[a], tur="X") == dict(kt[a], tur="X")
        else:
            assert kg[a] == kt[a], (o, a)
    assert [(x["ekip"], x["gun"], x["saat"]) for x in g["talep"]] == \
           [(x["ekip"], x["gun"], x["saat"]) for x in t["talep"]]
    sayim = MD.hucre_sayimi(t, ref["atamalar"])
    for x in g["talep"]:
        h = sayim[(x["ekip"], x["gun"], x["saat"])]
        assert x["hedef"] == h and x["asgari"] == MD.asgari_kurali(h), (o, x)


def test_TABAN_K62_kadro_kararlari_10_cift_yetkinlikli_BO_gece_2_3():
    t = MD.taban_sahne(1.0)
    cift = [c for c in t["calisanlar"] if c["ekipler"] == ["SATIS", "BACKOFFICE"]]
    assert len(cift) == 10                                   # Mustafa 22:03: "10 yapalim"
    assert sorted(c["id"] for c in cift) == sorted(t["_merdiven"]["cift_yetkinlikli"])
    gece = [x for x in t["talep"] if x["ekip"] == "BACKOFFICE" and x["saat"] < 8]
    assert gece and all((x["asgari"], x["hedef"]) == (2, 3) for x in gece)
    assert {k["tur"] for k in t["kurallar"] if k["kod"] == "HEDEF_ASIMI"} == {"YUMUSAK"}
    assert len(MD.taban_sahne(0.1)["_merdiven"]["cift_yetkinlikli"]) == 1


def test_ASGARI_kurali_hedefe_yakin():
    assert [MD.asgari_kurali(h) for h in (0, 1, 2, 3, 122)] == [0, 1, 1, 2, 121]


def test_REFERANS_PUANI_sahnede_kayitli_ve_yeniden_hesaplaninca_AYNI():
    """Kucuk kopyada (saniyeler): sahneye yazilan referans puani, planin bu
    sahnedeki amaci; yeniden hesaplaninca birebir. 500'de ayni fonksiyon
    uretimde kosar (merdiven.py turet)."""
    g = _yukle(MD.sahne_yolu(0.1))
    ref = _yukle(MD.referans_yolu(0.1))
    p = MD.plan_puani(g, ref["atamalar"])
    assert p["durum"] == "OPTIMAL"
    assert p == g["_merdiven"]["referans_puani"]
    assert p["dagilim"].get("HEDEF_KAPSAMA", {"ceza": 0})["ceza"] == 0   # tam oturan talep
    assert "HEDEF_ASIMI" not in p["dagilim"]                             # SERT: kirilimda yok


def test_S30_setleri_TARIHSEL_HEDEF_ASIMI_YUMUSAK_kalir():
    """K-67 madde 4 / K-62: S30 setleri uzerine yazilmaz; turleri YUMUSAK."""
    for ad in ("_sahne-S30-85.json", "_sahne-S30-95.json"):
        g = json.load(io.open(os.path.join(BURASI, "fikstur", ad), encoding="utf-8"))
        assert {k["tur"] for k in g["kurallar"] if k["kod"] == "HEDEF_ASIMI"} == {"YUMUSAK"}, ad


# ----------------------------------------------------------------------
# (b) Kucuk kopya: motor SIFIRDAN cozer
# ----------------------------------------------------------------------

def _coz_ve_denetle(olcek, saniye):
    from cozucu.coz import coz
    g = _yukle(MD.sahne_yolu(olcek))
    c = coz(copy.deepcopy(g), {"azami_saniye": saniye})
    assert c["durum"] == "cozuldu", (c["durum"], (c.get("teshis") or {}))
    return g, c, MD.referans_denetle(g, c["atamalar"])


def test_KUCUK_KOPYA_motor_sifirdan_cozer_ASIM_0_sert_0_fazla_mesai_0():
    g, c, d = _coz_ve_denetle(0.1, 60)
    assert d["sert"] == 0 and d["asim"] == 0 and d["fazla_mesai_saat"] == 0.0, d
    assert d["yayinlanabilir"] is True
    assert "HEDEF_ASIMI" not in c["cozum_istatistikleri"]["amac_dagilimi"]


@pytest.mark.skipif(os.environ.get("TSHIFT_MERDIVEN_500") != "1",
                    reason="500 kisilik COZUM bekcisi haftalik CI isinde kosar "
                           "(TSHIFT_MERDIVEN_500=1; Mustafa 12 Ekim 22:11)")
def test_HAFTALIK_500_motor_sifirdan_cozer_ASIM_0_sert_0():
    """Yalniz SERT kurallar zorlanir. Fazla mesai RAPORLANIR, zorlanmaz:
    12 Ekim bulutta olculdu -- 2 cekirdekte fazla mesaisiz ilk arama 500
    kiside 3 x 40 sn'de bulamiyor (eski S30'da da), urun yolu fazla mesaiyle
    doner. GitHub'in makinesi 2 cekirdek; "fazla mesai 0" burada yanlis
    kirmizi olurdu. O kontrol Mustafa'nin makinesindeki olcumde (K-62)."""
    g, c, d = _coz_ve_denetle(1.0, int(os.environ.get("TSHIFT_MERDIVEN_SANIYE", "900")))
    assert d["sert"] == 0 and d["asim"] == 0, d
    ref = g["_merdiven"]["referans_puani"]["amac"]
    amac = c["cozum_istatistikleri"]["amac_degeri"]
    print("HAFTALIK 500: motor %s  referans %s  (%+.1f%%)  eksik %d  fazla mesai %s sa  kirilim %s"
          % (amac, ref, 100.0 * (amac - ref) / ref, d["eksik"], d["fazla_mesai_saat"],
             {k: v["ceza"] for k, v in c["cozum_istatistikleri"]["amac_dagilimi"].items()}))


# ----------------------------------------------------------------------
# Ayirma cesitleri (13 Ekim, bulgu 31) -- seviye 1'den turer, referans gecerli kalir
# ----------------------------------------------------------------------

@pytest.mark.parametrize("ad", sorted(MD.CESITLER))
def test_CESIT_referans_gecerli_kalir_ve_tanimi_tutar(ad):
    g = _yukle(MD.sahne_yolu(0.1))
    ref = _yukle(MD.referans_yolu(0.1))
    c = MD.cesit_sahne(g, ad, 0.1)
    assert c["_merdiven"]["cesit"] == ad and "referans_puani" not in c["_merdiven"]
    d = MD.referans_denetle(c, ref["atamalar"])
    assert d["sert"] == 0 and d["asim"] == 0 and d["fazla_mesai_saat"] == 0.0, (ad, d)
    tur = {k["tur"] for k in c["kurallar"] if k["kod"] == "HEDEF_ASIMI"}
    eski = {(t["ekip"], t["gun"], t["saat"]): t for t in g["talep"]}
    if ad == "asim_yumusak":
        assert tur == {"YUMUSAK"} and c["talep"] == g["talep"]
        assert d["eksik"] == 0
    elif ad == "eski_asgari":
        taban = {(t["ekip"], t["gun"], t["saat"]): t["asgari"] for t in MD.taban_sahne(0.1)["talep"]}
        assert tur == {"SERT"} and d["eksik"] == 0
        for t in c["talep"]:
            a = (t["ekip"], t["gun"], t["saat"])
            assert t["hedef"] == eski[a]["hedef"] and t["asgari"] == min(eski[a]["hedef"], taban[a])
    elif ad == "pay1":
        assert tur == {"SERT"}
        for t in c["talep"]:
            a = (t["ekip"], t["gun"], t["saat"])
            assert t["hedef"] == eski[a]["hedef"] + 1 and t["asgari"] == MD.asgari_kurali(eski[a]["hedef"])
        assert d["eksik"] == len(c["talep"])          # referans her hucrede tam 1 eksik (bilinen)
    assert g["_merdiven"].get("referans_puani")       # kaynak sahne degismedi
