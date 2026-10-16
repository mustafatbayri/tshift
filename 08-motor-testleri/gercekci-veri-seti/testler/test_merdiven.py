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
    elif ad in ("tol1", "tol2"):                      # K-68: talep aynen, sinir hedef + k
        assert tur == {"SERT"} and c["talep"] == g["talep"] and d["eksik"] == 0
        hk = [k for k in c["kurallar"] if k["kod"] == "HEDEF_ASIMI"]
        assert [k["parametreler"]["ust_tolerans"] for k in hk] == [int(ad[3:])]
        assert all(not (k.get("parametreler") or {}).get("ust_tolerans")
                   for k in g["kurallar"] if k["kod"] == "HEDEF_ASIMI")   # kaynak sahne degismedi
    assert g["_merdiven"].get("referans_puani")       # kaynak sahne degismedi


# ----------------------------------------------------------------------
# Veri seti kaynagi (14 Ekim; Mustafa 13 Ekim 23:20: "bundan sonraki testler bu
# json veri seti ... kullanarak kossun") -- taban DEPODAKI veri setinden
# (10-veri-seti/<MD.VERI_SETI_SURUM>), dosyalar _sahne-L1-VS<n>-95*,
# _referans-L1-VS<n>-95*. 14 Ekim gunduz v1 (-VS1), aksam v2 (-VS2: K-71, K-72).
# ----------------------------------------------------------------------

def test_VS_TABAN_veri_setinden_donusturucu_ciktisi_HEDEF_ASIMI_YUMUSAK():
    import importlib
    if MD.VERI_SETI not in sys.path:
        sys.path.insert(0, MD.VERI_SETI)
    donustur = importlib.import_module("donustur")
    t = MD.taban_sahne(0.1, "veri-seti")
    g = donustur.motor_girdisi(donustur.yukle(os.path.join(MD.VERI_SETI, "veri", "tshift-49.json")))
    assert {k: v for k, v in t.items() if k not in ("_merdiven", "kurallar")} == \
        {k: v for k, v in g.items() if k != "kurallar"}
    assert [k["tur"] for k in t["kurallar"] if k["kod"] == "HEDEF_ASIMI"] == ["YUMUSAK"]
    assert [k["tur"] for k in g["kurallar"] if k["kod"] == "HEDEF_ASIMI"] == ["SERT"]     # firma ayari (K-67)
    assert t["_merdiven"]["kaynak"].startswith("veri-seti")
    assert t["_merdiven"]["cift_yetkinlikli"] == [c["id"] for c in t["calisanlar"] if len(c["ekipler"]) > 1]
    assert MD.VERI_SETI_SURUM == "v2" and MD.VERI_SETI_EKI == "-VS2"                   # 14 Ekim aksami
    assert os.path.isdir(MD.VERI_SETI) and MD.VERI_SETI.endswith(os.path.join("10-veri-seti", "v2"))
    assert MD.sahne_yolu(0.1, "veri-seti").endswith("_sahne-L1-VS2-95-0.1.json")
    assert MD.referans_yolu(1.0, "veri-seti").endswith("_referans-L1-VS2-95.json")
    assert t["_merdiven"]["kaynak"] == "veri-seti v2 (tshift-49.json)"
    # v2'nin motor girdisine getirdigi alanlar (K-71, K-72) tabanda da var
    assert all(c["sozlesme"].get("haftalik_saat") is not None for c in t["calisanlar"])
    assert all(0 < c["sozlesme"]["haftalik_saat"] <= 30 for c in t["calisanlar"]
               if c["sozlesme"]["tip"] == "yari_zamanli")
    assert MD.sahne_yolu(1.0).endswith("_sahne-L1-95.json")                              # eski adlar aynen
    with pytest.raises(SystemExit):
        MD.sahne_yolu(1.0, "baska")


def test_REFERANS_URETIMI_her_boyutta_IKI_ASAMA_ve_sert_kesim(monkeypatch):
    """15 Ekim (T-82 ilk bulgu): 25 kisilik kademede referans fazla mesaili cikti,
    cunku esigin altinda urun yolu tek asamali -- fazla mesaisiz arama yok.
    Referans uretimi `iki_asama_esigi: 0` ile her boyutta iki asamaya zorlanir;
    `fazla_mesai_sifirda_tut` ve tohum kaydirma yerinde kalir."""
    yakalanan = {}

    def sahte_coz(girdi, ayar):
        yakalanan.update(ayar)
        return {"durum": "sure_yetmedi"}
    import importlib
    C = importlib.import_module("cozucu.coz")     # paket `cozucu.coz` adini fonksiyonla golgeliyor
    monkeypatch.setattr(C, "coz", sahte_coz)
    with pytest.raises(SystemExit):
        MD.referans_uret(0.1, 5, tohum=7)
    assert yakalanan["iki_asama_esigi"] == 0 and yakalanan["fazla_mesai_sifirda_tut"] is True
    assert yakalanan["tohum_kaydirma"] == 6 and yakalanan["cozucu_parametreleri"] == {"random_seed": 7}
    assert yakalanan["azami_saniye"] == 5
    assert yakalanan["ilk_asama_saniye"] == 120 and yakalanan["ilk_asama_orani"] == 0.5   # kucuk butce: taban 120
    yakalanan.clear()
    with pytest.raises(SystemExit):
        MD.referans_uret(0.1, 1800, tohum=7)
    assert yakalanan["ilk_asama_saniye"] == 900                        # 1.800 sn -> fm'siz aramaya 900 (3 x 300)


def test_REFERANS_fazla_mesaili_yalniz_KANITLI_imkansizsa_kabul(monkeypatch, tmp_path):
    """25 kisilik kademe (15 Ekim 00:09): fazla mesaisiz ilk arama INFEASIBLE ->
    fazla mesaisiz plan kanitli yok -> referans fazla mesaili kabul edilir, kayit
    soyler. Kanit yoksa (UNKNOWN) fazla mesaili referans REDDEDILIR (eski kural)."""
    import importlib
    C = importlib.import_module("cozucu.coz")
    taban = MD.taban_sahne(0.1)
    ref = _yukle(MD.referans_yolu(0.1))
    kisi = [a for a in ref["atamalar"] if a["gun"] == 0][0]["calisan"]
    fm_plan = copy.deepcopy(ref["atamalar"])
    for a in fm_plan:                                   # bir kisiye 2 saat fazla mesai yaz
        if a["calisan"] == kisi:
            a["bit"] += 2
            break

    def sahte(kanit):
        def sahte_coz(girdi, ayar):
            return {"durum": "cozuldu", "atamalar": fm_plan, "metrikler": {},
                    "cozum_istatistikleri": {"amac_degeri": 1, "amac_dagilimi": {},
                                             "fazla_mesai_once_sifir": {"kanitlandi_yok": kanit, "denemeler": []}}}
        return sahte_coz
    d = MD.referans_denetle(taban, fm_plan)
    assert d["fazla_mesai_saat"] > 0 and d["sert"] == 0, d
    monkeypatch.setattr(C, "coz", sahte(False))
    hata = tmp_path / "_referans-HATA-test.json"
    monkeypatch.setattr(MD, "hata_yolu", lambda olcek, kaynak="uretec": str(hata))
    with pytest.raises(SystemExit) as e:                # kanit yok: red; plan hata dosyasina
        MD.referans_uret(0.1, 5)
    assert str(hata) in str(e.value) and hata.exists()
    kayit = json.load(io.open(str(hata), encoding="utf-8"))
    assert kayit["atamalar"] == fm_plan and kayit["tabanda_denetim"]["fazla_mesai_saat"] == d["fazla_mesai_saat"]
    assert kayit["sert_ihlaller"] == [] and kayit["olcek"] == 0.1
    monkeypatch.setattr(C, "coz", sahte(True))
    r = MD.referans_uret(0.1, 5)                        # kanitli yok: kabul, kayitta
    assert r["kayit"]["fazla_mesaisiz_kanitli_yok"] is True
    assert r["kayit"]["fazla_mesai_saat"] == d["fazla_mesai_saat"] > 0
    assert "iki_asama_esigi 0" in r["kayit"]["yol"]


def test_VS_surumu_komut_satirindan_ve_ortamdan_SECILIR_bilinmeyen_REDDEDILIR(monkeypatch):
    """`--veri-seti v1` (kalite-olc.py ile paylasilan argv) ya da TSHIFT_VERI_SETI
    eski surumle kosturur -- 14 Ekim -VS1 kayitlariyla kiyas icin; varsayilan v2."""
    monkeypatch.setattr(sys, "argv", ["kalite-olc.py", "--kaynak", "veri-seti"])
    monkeypatch.delenv("TSHIFT_VERI_SETI", raising=False)
    assert MD._veri_seti_surumu() == "v2"
    monkeypatch.setenv("TSHIFT_VERI_SETI", "v1")
    assert MD._veri_seti_surumu() == "v1"
    monkeypatch.setattr(sys, "argv", ["kalite-olc.py", "--kaynak", "veri-seti", "--veri-seti", "v2"])
    assert MD._veri_seti_surumu() == "v2"                               # argv ortami ezer
    monkeypatch.setattr(sys, "argv", ["x", "--veri-seti", "v9"])
    with pytest.raises(SystemExit):
        MD._veri_seti_surumu()
    # modul sabitleri birbiriyle tutarli (surum -> klasor -> dosya eki)
    assert MD.VERI_SETI.endswith(MD.VERI_SETI_SURUM) and MD.VERI_SETI_EKI == "-VS" + MD.VERI_SETI_SURUM[1:]
    assert os.path.isdir(os.path.join(os.path.dirname(MD.VERI_SETI), "v1"))      # v1 dondu ama duruyor


@pytest.mark.parametrize("olcek", [1.0, 0.1], ids=["500", "0.1"])
def test_VS_REFERANS_bekcisi_seviye1_sahnesinde_TEMIZ(olcek):
    yol_s, yol_r = MD.sahne_yolu(olcek, "veri-seti"), MD.referans_yolu(olcek, "veri-seti")
    if olcek == 1.0 and not os.path.exists(yol_r):
        pytest.skip("500 kisilik %s referansi henuz uretilmedi (Mustafa'nin makinesi: " % MD.VERI_SETI_EKI[1:] +
                    "py merdiven.py referans --olcek 1.0 --kaynak veri-seti --saniye 900)")
    g, ref = _yukle(yol_s), _yukle(yol_r)
    d = MD.referans_denetle(g, ref["atamalar"])
    assert d == {"sert": 0, "sert_kurallar": [], "asim": 0, "eksik": 0,
                 "fazla_mesai_saat": 0.0, "yayinlanabilir": True}, (olcek, d)
    assert ref["kayit"]["kaynak"] == "veri-seti"
    t = MD.taban_sahne(olcek, "veri-seti")
    sayim = MD.hucre_sayimi(t, ref["atamalar"])
    for x in g["talep"]:
        h = sayim[(x["ekip"], x["gun"], x["saat"])]
        assert x["hedef"] == h and x["asgari"] == MD.asgari_kurali(h), (olcek, x)
