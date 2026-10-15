# -*- coding: utf-8 -*-
"""
GEVSEKTEN SERTE -- K-68 eki (Mustafa, 13 Ekim 17:15-17:31)

NE OLDU (bulgu 31)
  Merdiven seviye 1'de (her hucre [hedef - 1, hedef], HEDEF_ASIMI SERT) motor
  500 kiside birinci asamada HIC gecerli plan bulamadi -- plan VAR (referans),
  ama sifirdan bulmak bosluksuz bir yapboz. Ayni sahnede asim yumusatilinca
  plan daha kolay bulundu.

KARAR (Mustafa 17:15): "gevsek plandan serte gecis dogru bir yaklasim ...
  Once gevsegi bulup sertlige giderse nerede tikandigimizi gorur". (ii) 17:31:
  tam serte inilemezse plan TASLAK doner, asan hucreler listelenir,
  "kanitlanmadi" notuyla.

NASIL (cozucu/coz.py `_gevsekten_serte`)
  Birinci asama plan bulamazsa (UNKNOWN -- INFEASIBLE kanittir, o yol
  teshistir) HEDEF_ASIMI SERT degiskenlerinin alani acilir, toplam asim
  enazlanir; sonra tavan tolerans + 3, + 1, + 0. Her adim oncekinin planini
  ipucu alir.

Testler birinci asamanin "bu surede bulunamadi" sonucunu ZORLAR
(`_ilk_arama` / `_fazla_mesaisiz_ara` / `_gecerli_plan_yeniden_ara`): kucuk
sahnede gercek arama saniyenin altinda bulur.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_gevsekten_serte.py -v
"""

import importlib
import os
import sys
import time

import pytest
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

C = importlib.import_module("cozucu.coz")   # paket `coz` fonksiyonunu disa verir   # noqa: E402
from cozucu.coz import coz                                      # noqa: E402
from dogrulayici import degerlendir                             # noqa: E402
from cozucu.model import Model                                  # noqa: E402
from test_hedef_asimi import _sahne, _sert, _tam_zamanli_sahne, _tolerans   # noqa: E402

# iki_asama_esigi 0: birinci asama (ve gevsek yol) yalniz iki asamali aramada
# vardir; urunde 50 000 degiskenden buyuk modelde (500 kisi ~1,5 milyon).
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5, "iki_asama_esigi": 0}


@pytest.fixture
def ilk_arama_bulamaz(monkeypatch):
    """Birinci asamanin butun gecerli plan aramalari 'bu surede bulunamadi'
    (UNKNOWN) doner -- urunde 500 kiside olan sey (bulgu 31)."""
    def bos(*a, **k):
        return cp_model.UNKNOWN, cp_model.CpSolver()

    def fm_bos(kuruldu, ayar, pay):
        return cp_model.UNKNOWN, cp_model.CpSolver(), [{"tohum": 1, "saniye": 0.0, "durum": "UNKNOWN"}]
    monkeypatch.setattr(C, "_ilk_arama", bos)
    monkeypatch.setattr(C, "_gecerli_plan_yeniden_ara", bos)
    monkeypatch.setattr(C, "_fazla_mesaisiz_ara", fm_bos)


def _hedef_asimi(r):
    return [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]


# ----------------------------------------------------------------------
# 1. Tetiklenme
# ----------------------------------------------------------------------

def test_ilk_plan_normal_yoldan_bulunursa_DENENMEZ():
    c = coz(_sert(_sahne()), dict(AYAR))
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None
    assert "taslak" not in c


def test_ilk_arama_bulamazsa_GEVSEKTEN_baslar_TAM_serte_iner(ilk_arama_bulamaz):
    """4 yari zamanli, hedef 1: sert plan var. Acik adim toplam asimi
    enazlar, 0 bulur -> erken durur; plan sert kurala uyar, taslak degil."""
    g = _sert(_sahne())
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    gs = c["cozum_istatistikleri"]["gevsekten_serte"]
    assert gs["denendi"] is True and gs["tam_sert"] is True and gs["kalan_asim"] == 0
    assert [a["tavan"] for a in gs["adimlar"]] == ["acik"]          # asim 0 bulundu: erken durur
    assert gs["adimlar"][-1]["toleransin_ustunde_asim"] == 0
    # 14 Ekim: adimin ilk plani kacinci saniyede buldugu ve cozum sayisi kayitli (olcum)
    a0 = gs["adimlar"][0]
    assert a0["ilk_cozum_saniye"] is not None and 0 <= a0["ilk_cozum_saniye"] <= a0["saniye"] + 0.01
    assert a0["cozum_sayisi"] >= 1
    assert "taslak" not in c and "taslak_asim" not in c
    r = degerlendir(g, c["atamalar"])
    assert _hedef_asimi(r) == []
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]
    assert "HEDEF_ASIMI_TOLERANS_USTU" not in c["cozum_istatistikleri"]["amac_dagilimi"]


def test_KAPALIYKEN_denenmez(ilk_arama_bulamaz):
    c = coz(_sert(_sahne()), dict(AYAR, gevsekten_serte=False))
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None
    assert "taslak" not in c


def test_ASIM_YUMUSAKKEN_denenmez(ilk_arama_bulamaz):
    """Sinirli (SERT) asim degiskeni yoksa acilacak bir sey yok."""
    c = coz(_sahne(), dict(AYAR))                  # HEDEF_ASIMI YUMUSAK
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None


def test_KANITLI_cozumsuzlukte_denenmez_TESHIS_yolu():
    """INFEASIBLE kanittir (K-37): gevsek yol degil teshis kosar."""
    c = coz(_sert(_tam_zamanli_sahne()), dict(AYAR, teshis_kural_saniye=10))
    assert c["durum"] == "cozumsuz"
    assert c["teshis"]["asim_hucreleri"]["toplam_fazla"] == 32


# ----------------------------------------------------------------------
# 2. Tam serte inilemezse: TASLAK (ii)
# ----------------------------------------------------------------------

def test_inilemezse_TASLAK_asan_hucreler_listelenir_KANITLI_yok(ilk_arama_bulamaz):
    """Iki tam zamanli, sertte cozumsuz, en az asim 32 (test_hedef_asimi).
    Acik adim 32 bulur; tavan +3 ve +1'de 32 kalir; +0 INFEASIBLE (kanit,
    molalar sabitken). Plan TASLAK: 32 hucre x 1 fazla."""
    g = _sert(_tam_zamanli_sahne())
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    gs = c["cozum_istatistikleri"]["gevsekten_serte"]
    assert [a["tavan"] for a in gs["adimlar"]] == ["acik", "tolerans+3", "tolerans+1", "tolerans+0"]
    assert [a["durum"] for a in gs["adimlar"]] == ["OPTIMAL", "OPTIMAL", "OPTIMAL", "INFEASIBLE"]
    assert gs["ulasilan_tavan"] == "tolerans+1" and gs["tam_sert"] is False
    assert gs["kalan_asim"] == 32 and gs["kanitlandi_yok"] is True and gs["molalar_sabit"] is True
    assert c["taslak"] is True
    ta = c["taslak_asim"]
    assert ta["toplam_fazla"] == 32 and len(ta["hucreler"]) == 32
    assert all(h["fazla"] == 1 for h in ta["hucreler"])
    assert ta["kanitlandi_yok"] is True and "YOK" in ta["aciklama"]
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is None
    assert any("TASLAKTIR" in n for n in c["uygulanmayan_notlar"])
    # amacta tolerans ustu ayri kalem; hucre cozucuden, dogrulayicidan ayni
    d = c["cozum_istatistikleri"]["amac_dagilimi"]["HEDEF_ASIMI_TOLERANS_USTU"]
    assert d["deger"] == 32 and d["ceza"] == 32 * C.GEVSEK_KALAN_AGIRLIGI
    r = degerlendir(g, c["atamalar"])
    ih = _hedef_asimi(r)
    assert len(ih) == 32 and all(i["agirlik"] == "SERT" for i in ih)
    assert sorted((i["gun"], i["saat"]) for i in ih) == \
        sorted((h["gun"], h["saat"]) for h in ta["hucreler"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT" and i["kural"] != "HEDEF_ASIMI"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True        # K-67 eki: bilgi verir


def test_TASLAKTA_optimuma_uzaklik_YAZILMAZ_ortak_aramada_da(ilk_arama_bulamaz):
    """Mola adimi kapaliyken (ortak arama) cozucu gevsetilmis modelde OPTIMAL
    der ve alt sinir = amac olur; "%0 uzak" yazilsaydi sert kurala uymayan
    plana "en iyisi" denmis olurdu. Mola adimi acikken None zaten (O-16)."""
    c = coz(_sert(_tam_zamanli_sahne()), dict(AYAR, mola_adimi=False))
    assert c["taslak"] is True
    assert c["cozum_istatistikleri"]["alt_sinir"] == c["cozum_istatistikleri"]["amac_degeri"]
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is None


def test_son_adim_SURE_doldurursa_KANITLANMADI_der(ilk_arama_bulamaz, monkeypatch):
    """Tavan + 0 adimi plan bulamadan biterse (UNKNOWN) "yok" denmez."""
    asil = C.cp_model.CpSolver

    class Kisa(asil):
        def Solve(self, model, *a, **k):
            d = asil.Solve(self, model, *a, **k)
            return cp_model.UNKNOWN if d == cp_model.INFEASIBLE else d
    monkeypatch.setattr(C.cp_model, "CpSolver", Kisa)
    c = coz(_sert(_tam_zamanli_sahne()), dict(AYAR))
    assert c["taslak"] is True
    gs = c["cozum_istatistikleri"]["gevsekten_serte"]
    assert gs["kanitlandi_yok"] is False
    assert c["taslak_asim"]["kanitlandi_yok"] is False
    assert "kanitlanmadi" in c["taslak_asim"]["aciklama"].lower()


def test_TASLAK_karari_SON_plandan_iyilestirme_asimi_eritirse_TASLAK_DEGIL(ilk_arama_bulamaz,
                                                                          monkeypatch):
    """Gevsek adimlar tolerans ustunu sifirlayamadi diye isaretlense de son
    plan sert kurala uyuyorsa taslak DEGILDIR (karar cevap adiminda, son
    plandan). Burada `_sert_disi_asim` gevsek yolun icinde hep 5 doner."""
    monkeypatch.setattr(C, "_sert_disi_asim", lambda kuruldu, c: 5)
    g = _sert(_sahne())
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu"
    gs = c["cozum_istatistikleri"]["gevsekten_serte"]
    assert gs["tam_sert"] is False and gs["son_plan_toleransin_ustunde"] == 0
    assert "taslak" not in c
    assert any("sert kurala uyar" in n for n in c["uygulanmayan_notlar"])
    assert _hedef_asimi(degerlendir(g, c["atamalar"])) == []


def test_EKLI_COZUM_ipucu_TAM_ve_degisken_sirasi_bekcisi():
    """`_EkliCozum` sonradan eklenen degiskeni cozumun SONUNA ekler; sira
    bozuksa sessiz yanlis ipucu yerine hata."""
    m = cp_model.CpModel()
    a = m.NewIntVar(0, 3, "a")
    m.Add(a == 2)
    c = cp_model.CpSolver()
    assert c.Solve(m) == cp_model.OPTIMAL
    b = m.NewIntVar(0, 5, "b")
    e = C._EkliCozum(c, [(b, 4)])
    assert e.Value(a) == 2 and e.Value(b) == 4
    assert list(e.ResponseProto().solution) == [2, 4]
    m2 = cp_model.CpModel()
    x = m2.NewIntVar(0, 1, "x")
    with pytest.raises(AssertionError):
        C._EkliCozum(c, [(x, 1)])                   # indeks 0: cozumun sonunda degil


def test_TOLERANS_1_taslakta_yalniz_UST_SINIRIN_ustu_cezalanir(ilk_arama_bulamaz):
    """Uc tam zamanli, hedef 1, tolerans 1: sertte cozumsuz. Taslakta sayilan
    ve 1000'le cezalanan ust sinirin (2) USTUdur; bant ici fazla (hedef ile
    sinir arasi) HEDEF_ASIMI agirligiyla, dogrulayicida YUMUSAK."""
    g = _tolerans(_sert(_tam_zamanli_sahne()), 1)
    g["calisanlar"].append(dict(g["calisanlar"][0], id="P3"))
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu" and c["taslak"] is True, c["durum"]
    ta = c["taslak_asim"]
    d = c["cozum_istatistikleri"]["amac_dagilimi"]
    assert d["HEDEF_ASIMI_TOLERANS_USTU"]["deger"] == ta["toplam_fazla"] > 0
    assert d["HEDEF_ASIMI"]["deger"] > ta["toplam_fazla"]            # bant ici + ustu
    r = degerlendir(g, c["atamalar"])
    sert = [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI" and i["agirlik"] == "SERT"]
    assert sum(i["olculen"] - 2 for i in sert) == ta["toplam_fazla"]
    assert len(sert) == len(ta["hucreler"])


# ----------------------------------------------------------------------
# 3. Birim: `_gevsekten_serte` modeli hangi halde birakir
# ----------------------------------------------------------------------

def _alan(k, v):
    return list(k.m.Proto().variables[v.Index()].domain)


def test_BIRIM_tam_sertte_alanlar_SERT_haline_doner():
    k = Model(_sert(_sahne())).kur()
    d, c = C._gevsekten_serte(k, {"azami_saniye": 10}, time.time())
    assert d == cp_model.OPTIMAL and isinstance(c, cp_model.CpSolver)
    assert k.gevsekten_serte["tam_sert"] is True
    assert all(_alan(k, v) == [0, t] for v, t in k.asim_sinirli.values())


def test_BIRIM_taslakta_alanlar_ULASILAN_tavanda_ve_gk_degerleri_TAM():
    k = Model(_sert(_tam_zamanli_sahne())).kur()
    once = len(k.cezalar)
    d, c = C._gevsekten_serte(k, {"azami_saniye": 10}, time.time())
    assert k.gevsekten_serte["ulasilan_tavan"] == "tolerans+1"
    assert all(_alan(k, v) == [0, 1] for v, _ in k.asim_sinirli.values())
    yeni = k.cezalar[once:]
    assert len(yeni) == len(k.asim_sinirli) == 48
    assert all(a == C.GEVSEK_KALAN_AGIRLIGI and v.Name().startswith("gk_") for a, v in yeni)
    assert isinstance(c, C._EkliCozum)
    asim = sorted(c.Value(v) for v, _ in k.asim_sinirli.values())
    assert sorted(c.Value(g) for _, g in yeni) == asim and sum(asim) == 32
    assert len(c.ResponseProto().solution) == len(k.m.Proto().variables)   # ipucu TAM


def test_BIRIM_plan_bulunamazsa_alanlar_SERT_haline_doner_UNKNOWN(monkeypatch):
    """Acik adim da plan bulamazsa (bulgu 31'in en kotu hali) daraltma
    denenmez, alanlar sert haline doner, UNKNOWN."""
    class Bos(cp_model.CpSolver):
        def Solve(self, model, *a, **k):
            return cp_model.UNKNOWN
    monkeypatch.setattr(C.cp_model, "CpSolver", Bos)
    k = Model(_sert(_sahne())).kur()
    d, c = C._gevsekten_serte(k, {"azami_saniye": 10}, time.time())
    assert d == cp_model.UNKNOWN and c is None
    assert [(a["tavan"], a["durum"]) for a in k.gevsekten_serte["adimlar"]] == [("acik", "UNKNOWN")]
    assert k.gevsekten_serte["adimlar"][0]["ilk_cozum_saniye"] is None        # plan yok -> sure yok
    assert k.gevsekten_serte["adimlar"][0]["cozum_sayisi"] == 0
    assert k.gevsekten_serte["tam_sert"] is False and k.gevsekten_serte["kalan_asim"] is None
    assert all(_alan(k, v) == [0, t] for v, t in k.asim_sinirli.values())


def test_BIRIM_BUTCE_yedek_ayrilir_acik_adim_kalanin_TAMAMINI_daraltma_esit_boler(monkeypatch):
    """K-68 ayar 2: butcenin gevsek_yedek_orani'si iyilestirme + mola adimina
    ayrilir; acik adim kalanin tamamini alabilir, daraltma adimlari o anki
    kalani esit boler (sure kaydi CpSolver'dan)."""
    sureler = []
    asil = cp_model.CpSolver

    class Kaydet(asil):
        def Solve(self, model, *a, **k):
            sureler.append(self.parameters.max_time_in_seconds)
            return asil.Solve(self, model, *a, **k)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    k = Model(_sert(_tam_zamanli_sahne())).kur()             # her adim saniyenin altinda biter
    C._gevsekten_serte(k, {"azami_saniye": 100, "gevsek_yedek_orani": 0.4}, time.time())
    beklenen = [59.0, 59.0 / 3, 59.0 / 2, 59.0]               # 100 - 1 - 100 x 0,4
    assert len(sureler) == 4
    assert all(abs(s_ - b_) < 1.0 for s_, b_ in zip(sureler, beklenen)), sureler


# ----------------------------------------------------------------------
# 4. K-68 ayarlari (Mustafa, 13 Ekim 23:20: "olur") -- olcum bulgu 31 son
#    bolum: (1) yeniden arama seviye 1'de 5/5 bosa gitti, (2) acik adim bir
#    kosuda 300 sn'de vazgecti ve sure sert modelde 654 sn bosa gitti, (3)
#    gevsek yolun planlari 5-12,5 sa fazla mesaili (referans 0).
#    Sahne: alti tam zamanli, tek sablon (test_fazla_mesai_once_sifir) +
#    HEDEF_ASIMI SERT (hedef 7, kadro 6: sinir hic baglamaz ama sinirli
#    degiskenler var, gevsek yol acilabilir).
# ----------------------------------------------------------------------

from test_fazla_mesai_once_sifir import _sahne as _fm_sahne, _fm  # noqa: E402

AYAR_FM = {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5, "isci_sayisi": 2}


def _fm_sert(gun=5):
    g = _fm_sahne(gun=gun)
    g["kurallar"].append({"kod": "HEDEF_ASIMI", "tur": "SERT", "aktif": True,
                          "yasal": False, "kabul_edilebilir": True})
    return g


@pytest.fixture
def fm_siz_bulamaz(monkeypatch):
    """Fazla mesaisiz ilk arama 'bu surede bulunamadi' (seviye 1'de 6/6)."""
    def fm_bos(kuruldu, ayar, pay):
        return cp_model.UNKNOWN, cp_model.CpSolver(), [{"tohum": 1, "saniye": 0.0, "durum": "UNKNOWN"}]
    monkeypatch.setattr(C, "_fazla_mesaisiz_ara", fm_bos)


@pytest.fixture
def yeniden_arama_kaydi(monkeypatch):
    cagri = []
    asil = C._gecerli_plan_yeniden_ara

    def kaydet(*a, **k):
        cagri.append(1)
        return asil(*a, **k)
    monkeypatch.setattr(C, "_gecerli_plan_yeniden_ara", kaydet)
    return cagri


def test_AYAR1_fazla_mesaisiz_arama_SURE_doldurunca_yeniden_arama_ATLANIR(fm_siz_bulamaz,
                                                                          yeniden_arama_kaydi):
    c = coz(_fm_sert(), dict(AYAR_FM))
    assert c["durum"] == "cozuldu", c["durum"]
    assert yeniden_arama_kaydi == []
    gs = c["cozum_istatistikleri"]["gevsekten_serte"]
    assert gs["yeniden_arama_atlandi"] is True and gs["tam_sert"] is True


def test_AYAR1_kapaliyken_ve_asim_YUMUSAKken_yeniden_arama_KOSAR(fm_siz_bulamaz, yeniden_arama_kaydi):
    c = coz(_fm_sert(), dict(AYAR_FM, gevsek_yeniden_arama_atla=False))
    assert yeniden_arama_kaydi == [1] and c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None     # yeniden arama buldu
    g = _fm_sahne()                                                 # HEDEF_ASIMI yok: sinirli degisken yok
    coz(g, dict(AYAR_FM))
    assert yeniden_arama_kaydi == [1, 1]


def test_AYAR1_fazla_mesaisiz_arama_INFEASIBLE_ise_ATLANMAZ(yeniden_arama_kaydi):
    """Alti gun talep, alti kisi: herkes 48 saat, fazla mesaisiz plan YOK
    (gercek arama INFEASIBLE). Yeniden arama kosar ve plani bulur -- kanitli
    durumda yol degismez (K-37: cozumsuzlukte teshis, taslak degil)."""
    c = coz(_fm_sert(gun=6), dict(AYAR_FM))
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]["kanitlandi_yok"] is True
    assert yeniden_arama_kaydi == [1]
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None


def test_AYAR2_adimlar_DURGUNLUK_bekcisiyle_kosar(monkeypatch):
    gorulen = []
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        gorulen.append(ayar["durgunluk_saniye"])
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    k = Model(_sert(_tam_zamanli_sahne())).kur()
    C._gevsekten_serte(k, {"azami_saniye": 30, "gevsek_durgunluk_saniye": 17}, time.time())
    assert gorulen == [17.0] * 4                                    # acik + uc daraltma


def test_AYAR2_PARCALI_acik_adim_bulamayan_parcadan_sonra_BASKA_TOHUMLA_yeniden_baslar(monkeypatch):
    asil = cp_model.CpSolver
    tohumlar = []

    class IkiKezBos(asil):
        def Solve(self, model, *a, **k):
            tohumlar.append((self.parameters.random_seed, self.parameters.max_time_in_seconds))
            if len(tohumlar) <= 2:
                return cp_model.UNKNOWN
            return asil.Solve(self, model, *a, **k)
    monkeypatch.setattr(C.cp_model, "CpSolver", IkiKezBos)
    k = Model(_sert(_sahne())).kur()
    d, c = C._gevsekten_serte(k, {"azami_saniye": 100, "gevsek_acik_parca_saniye": 7}, time.time())
    assert d == cp_model.OPTIMAL
    p = k.gevsekten_serte["acik_parcalar"]
    assert [x["tohum"] for x in p] == [1, 2, 3]
    assert [x["durum"] for x in p] == ["UNKNOWN", "UNKNOWN", "OPTIMAL"]
    assert [t for t, _ in tohumlar[:3]] == [1, 2, 3] and all(abs(s_ - 7) < 0.01 for _, s_ in tohumlar[:3])
    assert k.gevsekten_serte["tam_sert"] is True


def test_AYAR2_PARCALI_tohum_kaydirma_eklenir(monkeypatch):
    asil = cp_model.CpSolver
    tohumlar = []

    class Kaydet(asil):
        def Solve(self, model, *a, **k):
            tohumlar.append(self.parameters.random_seed)
            return asil.Solve(self, model, *a, **k)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    k = Model(_sert(_sahne())).kur()
    C._gevsekten_serte(k, {"azami_saniye": 100, "gevsek_acik_parca_saniye": 7, "tohum_kaydirma": 6},
                       time.time())
    assert tohumlar[0] == 7


def _fazla_mesaili_plan(kuruldu, amaci_geri_koy=None):
    """Bir fm degiskeni gecici olarak >= 60'a zorlanip plan aranir (amacli
    ya da amacsiz); alan geri acilir. Seviye 1'de iyilestirmenin planlari 5-9
    sa fazla mesailiydi (14 Ekim)."""
    v = _fm(kuruldu)[0]
    dom = kuruldu.m.Proto().variables[v.Index()].domain
    eski = list(dom)
    dom.clear()
    dom.extend([60, eski[-1]])
    try:
        if amaci_geri_koy:
            amaci_geri_koy()
        c2 = cp_model.CpSolver()
        c2.parameters.max_time_in_seconds = 10
        d2 = c2.Solve(kuruldu.m)
    finally:
        dom.clear()
        dom.extend(eski)
    assert d2 in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return c2


def _fazla_mesaili_iyilestirme(monkeypatch):
    """Iyilestirme fazla mesaili bir plan birakssin: gercek iyilestirmeden
    sonra fm >= 60 zorlanmis plan ipucu yazilir ve DONER (onarim onu alir)."""
    asil = C._ilk_asamada_iyilestir

    def fazla_mesaili(kuruldu, ayar, amacsiz, amaci_geri_koy, basladi, dusulecek=0.0, ayrilan=0.0):
        asil(kuruldu, ayar, amacsiz, amaci_geri_koy, basladi, dusulecek, ayrilan=ayrilan)
        c2 = _fazla_mesaili_plan(kuruldu, amaci_geri_koy)
        C._tam_ipucu_yaz(kuruldu, c2)
        return c2
    monkeypatch.setattr(C, "_ilk_asamada_iyilestir", fazla_mesaili)


def _amac(k):
    return lambda: k.m.Minimize(sum(a * v for a, v in k.cezalar))


# ---- Ayar 3, 14 Ekim surumu (Mustafa: "ok", oneri 1): onarim IYILESTIRMENIN
# ---- SONUNDA. Eski yerinde (gevsek plandan hemen sonra) 500'de 0/7 tuttu:
# ---- gevsek planda 326-465 sa fazla mesai vardi, ipucu cok uzaktaydi.

def test_AYAR3_onarim_IYILESTIRMENIN_SONUNDA_fazla_mesaisiz_plani_bulur_ve_ALIR(fm_siz_bulamaz,
                                                                                monkeypatch):
    _fazla_mesaili_iyilestirme(monkeypatch)
    g = _fm_sert()
    c = coz(g, dict(AYAR_FM))
    assert c["durum"] == "cozuldu", c["durum"]
    assert c["cozum_istatistikleri"]["gevsekten_serte"]["tam_sert"] is True
    o = c["cozum_istatistikleri"]["fazla_mesai_onarimi"]
    assert o["asama"] == "iyilestirme_sonu"
    assert o["denendi"] is True and o["bulundu"] is True and o["kabul"] is True
    assert o["once_dakika"] >= 60 and o["sonra_amac"] < o["once_amac"]
    assert any("fazla mesai onarimi" in n and "sifirlandi" in n for n in c["uygulanmayan_notlar"])
    assert c["metrikler"]["fazla_mesai_saat"] == 0
    assert c["cozum_istatistikleri"]["ilk_asama_iyilestirme"]["onarima_ayrilan_saniye"] > 0
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]


def test_AYAR3_BIRIM_onarim_AMACLA_arar_alirsa_ipucu_onun_alanlar_GERI_ACIK():
    k = Model(_fm_sert()).kur()
    fm = _fm(k)
    alan_once = [list(k.m.Proto().variables[v.Index()].domain) for v in fm]
    cz = _fazla_mesaili_plan(k, _amac(k))
    C._tam_ipucu_yaz(k, cz)
    k.m.ClearObjective()                         # iyilestirme kapaliysa amac silinmis olur: onarim KOYAR
    r = C._fazla_mesai_onar(k, dict(AYAR_FM, fazla_mesai_onarim_saniye=20), time.time(), cz, _amac(k))
    o = k.fazla_mesai_onarimi
    assert r is not None and o["kabul"] is True and o["sonra_amac"] < o["once_amac"]
    assert o["sonra_amac"] == int(sum(a * int(r.Value(v)) for a, v in k.cezalar)) > 0   # amacli arama
    assert sum(int(r.Value(v)) for v in fm) == 0
    p = k.m.Proto()
    assert list(p.solution_hint.values) == list(r.ResponseProto().solution)   # ipucu onarilmis plan
    assert [list(p.variables[v.Index()].domain) for v in fm] == alan_once     # K-61/O-18


def test_AYAR3_BIRIM_onarim_plani_amaci_DAHA_KOTUYSE_ALINMAZ_hakem_agirliklar(monkeypatch):
    """Bulunan fazla mesaisiz plan agirliklara gore kotuyse fazla mesaili plan
    kalir (Mustafa 6 Ekim: "en optimum olani secmeliyiz")."""
    k = Model(_fm_sert()).kur()
    cz = _fazla_mesaili_plan(k, _amac(k))
    C._tam_ipucu_yaz(k, cz)
    ipucu = list(k.m.Proto().solution_hint.values)
    asil = cp_model.CpSolver

    class Kotu(asil):
        def ObjectiveValue(self):
            return 10 ** 9
    monkeypatch.setattr(C.cp_model, "CpSolver", Kotu)
    r = C._fazla_mesai_onar(k, dict(AYAR_FM, fazla_mesai_onarim_saniye=20), time.time(), cz, _amac(k))
    o = k.fazla_mesai_onarimi
    assert r is None and o["bulundu"] is True and o["kabul"] is False
    assert list(k.m.Proto().solution_hint.values) == ipucu
    assert any("daha kotu" in n for n in k.notlar)


def test_AYAR3_onarim_suresi_AYARDAN_ve_mola_adiminin_payina_GIRMEZ(monkeypatch):
    """Onarim en cok `fazla_mesai_onarim_saniye`; mola adiminin payi (butcenin
    1 - `ilk_asama_iyilestirme_orani`) ayrilir."""
    k = Model(_fm_sert(gun=6)).kur()
    cz = cp_model.CpSolver()
    cz.Solve(k.m)                                                  # fazla mesaili plan (zorunlu)
    asil = cp_model.CpSolver
    sureler = []

    class Kaydet(asil):
        def Solve(self, model, *a, **kw):
            sureler.append(self.parameters.max_time_in_seconds)
            return asil.Solve(self, model, *a, **kw)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    C._fazla_mesai_onar(k, {"azami_saniye": 100, "fazla_mesai_onarim_saniye": 13}, time.time(), cz, _amac(k))
    assert sureler == [13.0]
    sureler.clear()
    C._fazla_mesai_onar(k, {"azami_saniye": 100, "fazla_mesai_onarim_saniye": 500}, time.time(), cz, _amac(k))
    assert len(sureler) == 1 and abs(sureler[0] - 79.0) < 0.5        # 100 - 1 - %20 mola payi
    sureler.clear()
    C._fazla_mesai_onar(k, {"azami_saniye": 100, "fazla_mesai_onarim_saniye": 500,
                            "ilk_asama_iyilestirme_orani": 0.5}, time.time(), cz, _amac(k))
    assert len(sureler) == 1 and abs(sureler[0] - 49.0) < 0.5        # oran okunur


def test_AYAR3_onarim_DURGUNLUK_bekcisiyle_kosar(monkeypatch):
    gorulen = []
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        gorulen.append(ayar["durgunluk_saniye"])
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    k = Model(_fm_sert()).kur()
    cz = _fazla_mesaili_plan(k, _amac(k))
    C._fazla_mesai_onar(k, dict(AYAR_FM, gevsek_durgunluk_saniye=17, fazla_mesai_onarim_saniye=20),
                        time.time(), cz, _amac(k))
    assert gorulen == [17.0]


def test_AYAR3_fazla_mesaisiz_plan_YOKSA_plan_AYNEN_doner(fm_siz_bulamaz):
    """Alti gun x alti kisi: herkes 48 saat, fazla mesai zorunlu. Iyilestirmenin
    plani fazla mesaili; onarim INFEASIBLE; plan aynen (eli bos donulmez)."""
    c = coz(_fm_sert(gun=6), dict(AYAR_FM))
    assert c["durum"] == "cozuldu"
    o = c["cozum_istatistikleri"]["fazla_mesai_onarimi"]
    assert o["denendi"] is True and o["bulundu"] is False and o["durum"] == "INFEASIBLE"
    assert o["kabul"] is False and o["once_dakika"] > 0
    assert c["metrikler"]["fazla_mesai_saat"] > 0


def test_AYAR3_KAPALIYKEN_GEREK_YOKKEN_ve_GEVSEK_YOL_YOKKEN_denenmez(fm_siz_bulamaz):
    c = coz(_fm_sert(), dict(AYAR_FM, fazla_mesai_onarimi=False))
    assert c["cozum_istatistikleri"]["fazla_mesai_onarimi"] is None
    # gevsek yol yok (HEDEF_ASIMI yok): yeniden arama yolu -- onarim denenmez
    c = coz(_fm_sahne(), dict(AYAR_FM))
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None
    assert c["cozum_istatistikleri"]["fazla_mesai_onarimi"] is None
    # gerek yok: plan zaten fazla mesaisiz -> denenmez
    k = Model(_fm_sert()).kur()
    eski = C._fazla_mesaiyi_sifirla(k)
    cz = cp_model.CpSolver()
    cz.Solve(k.m)
    C._fazla_mesaiyi_serbest_birak(k, eski)
    r = C._fazla_mesai_onar(k, dict(AYAR_FM, fazla_mesai_onarim_saniye=20), time.time(), cz, _amac(k))
    assert r is None
    assert k.fazla_mesai_onarimi["denendi"] is False and k.fazla_mesai_onarimi["once_dakika"] == 0


def test_AYAR3_iyilestirme_onarima_SURE_AYIRIR_en_cok_YARISI_ve_ipucuyu_yazan_cozucuyu_DONDURUR(
        monkeypatch):
    k = Model(_fm_sert()).kur()
    k.m.ClearObjective()
    amacsiz = cp_model.CpSolver()
    amacsiz.Solve(k.m)
    C._tam_ipucu_yaz(k, amacsiz)
    asil = C._iyilestirme_coz
    sureler = []

    def kaydet(model, saniye, isci):
        sureler.append(saniye)
        return asil(model, saniye, isci)
    monkeypatch.setattr(C, "_iyilestirme_coz", kaydet)
    ayar = {"azami_saniye": 100, "ilk_asama_iyilestirme_saniye": 40}
    r = C._ilk_asamada_iyilestir(k, ayar, amacsiz, _amac(k), time.time(), 0.0, ayrilan=300)
    assert abs(sureler[-1] - 20.0) < 0.5                               # 40'in yarisi
    assert k.ilk_asama_iyilestirme["onarima_ayrilan_saniye"] == 20.0
    assert r is not None                                               # iyilesmis plan ipucu oldu
    assert list(k.m.Proto().solution_hint.values) == list(r.ResponseProto().solution)
    r = C._ilk_asamada_iyilestir(k, ayar, amacsiz, _amac(k), time.time(), 0.0, ayrilan=5)
    assert abs(sureler[-1] - 35.0) < 0.5
    C._ilk_asamada_iyilestir(k, ayar, amacsiz, _amac(k), time.time(), 0.0)
    assert abs(sureler[-1] - 40.0) < 0.5 and "onarima_ayrilan_saniye" not in k.ilk_asama_iyilestirme


# ---- Ayar 4 (14 Ekim, Mustafa: "ok", oneri 2a): gevsek yol mumkunken fazla
# ---- mesaisiz ilk arama TEK kisa deneme (500'de 0/10); sure acik adima.

@pytest.fixture
def fm_arama_kaydi(monkeypatch):
    cagri = []

    def kaydet(kuruldu, ayar, pay):
        cagri.append((C._deneme_siniri(ayar), pay))
        return cp_model.UNKNOWN, cp_model.CpSolver(), [{"tohum": 1, "saniye": 0.0, "durum": "UNKNOWN"}]
    monkeypatch.setattr(C, "_fazla_mesaisiz_ara", kaydet)
    return cagri


def test_AYAR4_gevsek_yol_mumkunken_fazla_mesaisiz_arama_TEK_ve_KISA(fm_arama_kaydi):
    c = coz(_fm_sert(), dict(AYAR_FM, gevsek_fazla_mesaisiz_saniye=3))
    assert fm_arama_kaydi == [(1, 3.0)]                             # pay 30 x 0,2 = 6 -> 3
    f = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert f["gevsek_kisa_saniye"] == 3.0 and f["deneme_siniri"] == 1 and f["atlandi"] is False
    assert c["cozum_istatistikleri"]["gevsekten_serte"]["denendi"] is True


def test_AYAR4_varsayilan_20_sn_paydan_buyukse_PAY_kalir(fm_arama_kaydi):
    assert C.VARSAYILAN["gevsek_fazla_mesaisiz_saniye"] == 20
    coz(_fm_sert(), dict(AYAR_FM))
    assert fm_arama_kaydi == [(1, 6.0)]                             # min(6, 20)


def test_AYAR4_gevsek_yol_YOKKEN_eski_politika_3_deneme_TAM_pay(fm_arama_kaydi):
    c = coz(_fm_sahne(), dict(AYAR_FM, gevsek_fazla_mesaisiz_saniye=3))   # HEDEF_ASIMI yok
    assert fm_arama_kaydi == [(3, 6.0)]
    f = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert f["gevsek_kisa_saniye"] is None and f["deneme_siniri"] == 3
    fm_arama_kaydi.clear()
    coz(_fm_sert(), dict(AYAR_FM, gevsek_fazla_mesaisiz_saniye=3, gevsekten_serte=False))
    assert fm_arama_kaydi == [(3, 6.0)]


def test_AYAR4_sifir_fazla_mesaisiz_aramayi_ATLAR(fm_arama_kaydi):
    c = coz(_fm_sert(), dict(AYAR_FM, gevsek_fazla_mesaisiz_saniye=0))
    assert fm_arama_kaydi == []
    assert c["durum"] == "cozuldu"
    f = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert f["atlandi"] is True and f["bulundu"] is False and f["denemeler"] == []
    assert any("atlandi" in n for n in c["uygulanmayan_notlar"])
    assert c["cozum_istatistikleri"]["gevsekten_serte"]["yeniden_arama_atlandi"] is True


def test_AYAR4_KANITLI_yol_DEGISMEZ_gercek_kisa_arama_INFEASIBLE_kanitlar():
    """Gercek (yamasiz) kisa arama kucuk sahnede fazla mesaisiz planin YOKLUGUNU
    kanitlar; yeniden arama kosar, gevsek yol denenmez (K-37)."""
    c = coz(_fm_sert(gun=6), dict(AYAR_FM))
    f = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert f["kanitlandi_yok"] is True and f["deneme_siniri"] == 1
    assert c["cozum_istatistikleri"]["gevsekten_serte"] is None


def test_AYAR3_fazla_mesaisiz_baslangic_KAPALIYKEN_onarim_denenmez(ilk_arama_bulamaz):
    """`fazla_mesai_once_sifir` kapali (eski yol): gevsek yol kossa da onarim
    yok -- onarim, fazla mesaisiz BASLANGICIN yerini tutar."""
    c = coz(_fm_sert(), dict(AYAR_FM, fazla_mesai_once_sifir=False))
    assert c["cozum_istatistikleri"]["gevsekten_serte"]["denendi"] is True
    assert c["cozum_istatistikleri"]["fazla_mesai_onarimi"] is None


# ---- Oneri 2b (14 Ekim, olcum): acik adimin ek CP-SAT parametreleri

def _parametre_kaydi(monkeypatch):
    asil = cp_model.CpSolver
    gorulen = []

    class Kaydet(asil):
        def Solve(self, model, *a, **k):
            gorulen.append(self.parameters.linearization_level)
            return asil.Solve(self, model, *a, **k)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    return gorulen


def test_ONERI2B_acik_adim_parametreleri_YALNIZ_acik_adimda(monkeypatch):
    assert C.VARSAYILAN["gevsek_acik_cozucu_parametreleri"] == {}
    gorulen = _parametre_kaydi(monkeypatch)
    k = Model(_sert(_tam_zamanli_sahne())).kur()
    C._gevsekten_serte(k, {"azami_saniye": 30,
                           "gevsek_acik_cozucu_parametreleri": {"linearization_level": 0}}, time.time())
    assert gorulen == [0, 1, 1, 1]                                  # acik + uc daraltma (varsayilan 1)
    assert k.gevsekten_serte["acik_parametreler"] == {"linearization_level": 0}
    gorulen.clear()
    k = Model(_sert(_tam_zamanli_sahne())).kur()
    C._gevsekten_serte(k, {"azami_saniye": 30}, time.time())
    assert gorulen == [1, 1, 1, 1] and k.gevsekten_serte["acik_parametreler"] == {}


def test_ONERI2B_parcali_acik_adimda_da_uygulanir(monkeypatch):
    gorulen = _parametre_kaydi(monkeypatch)
    k = Model(_sert(_sahne())).kur()
    C._gevsekten_serte(k, {"azami_saniye": 100, "gevsek_acik_parca_saniye": 7,
                           "gevsek_acik_cozucu_parametreleri": {"linearization_level": 0}}, time.time())
    assert gorulen[0] == 0 and k.gevsekten_serte["acik_parcalar"]


# ---- Ayar 3'un tamamlayicisi (14 Ekim): onarimin kullanmadigi sure
# ---- iyilestirmeye geri doner (bulut, 49 kisi: devam yokken 180 sn'lik kosu
# ---- 87. sn'de bitiyordu).

def test_AYAR3_onarima_gerek_yoksa_ayrilan_sure_IYILESTIRMEYE_DEVAM_eder(fm_siz_bulamaz):
    c = coz(_fm_sert(), dict(AYAR_FM))
    ist = c["cozum_istatistikleri"]
    assert ist["gevsekten_serte"]["denendi"] is True
    assert ist["fazla_mesai_onarimi"]["denendi"] is False             # plan zaten fazla mesaisiz
    d = ist["ilk_asama_iyilestirme"]["devam"]
    assert d["pay"] > 0 and d["sonra_amac"] is not None              # kostu, plan buldu


def _amacsiz_plan(k):
    k.m.ClearObjective()
    cz = cp_model.CpSolver()
    cz.parameters.max_time_in_seconds = 10
    cz.Solve(k.m)
    C._tam_ipucu_yaz(k, cz)
    return cz


def test_AYAR3_BIRIM_devam_DAHA_IYIYSE_alir_amac_KONUR_ve_mola_payina_GIRMEZ(monkeypatch):
    k = Model(_fm_sert()).kur()
    cz = _fazla_mesaili_plan(k, _amac(k))         # iyilesebilir plan (fazla mesaili)
    C._tam_ipucu_yaz(k, cz)
    k.m.ClearObjective()                          # amac silinmis: devam geri koyar
    k.ilk_asama_iyilestirme = {"istenen_saniye": 10}
    asil = C._iyilestirme_coz
    sureler = []

    def kaydet(model, saniye, isci):
        sureler.append(saniye)
        return asil(model, saniye, isci)
    monkeypatch.setattr(C, "_iyilestirme_coz", kaydet)
    r = C._iyilestirmeye_devam(k, {"azami_saniye": 30}, time.time(), cz, _amac(k))
    d = k.ilk_asama_iyilestirme["devam"]
    assert abs(sureler[0] - 23.0) < 0.5                            # 30 - 1 - %20 mola payi
    assert r is not None and d["alindi"] is True and d["sonra_amac"] < d["once_amac"]
    assert d["sonra_amac"] == int(sum(a * int(r.Value(v)) for a, v in k.cezalar))   # amacli arama
    assert list(k.m.Proto().solution_hint.values) == list(r.ResponseProto().solution)
    sureler.clear()
    C._iyilestirmeye_devam(k, {"azami_saniye": 30, "ilk_asama_iyilestirme_orani": 0.5}, time.time(), r, _amac(k))
    assert abs(sureler[0] - 14.0) < 0.5                            # oran okunur: 30 - 1 - 15


def test_AYAR3_BIRIM_devam_DAHA_KOTUYSE_ipucu_DEGISMEZ_iyilestirme_KAPALIYSA_kosmaz(monkeypatch):
    k = Model(_fm_sert()).kur()
    cz = _amacsiz_plan(k)
    ipucu = list(k.m.Proto().solution_hint.values)
    k.ilk_asama_iyilestirme = {"istenen_saniye": 0}
    assert C._iyilestirmeye_devam(k, {"azami_saniye": 30}, time.time(), cz, _amac(k)) is None
    assert "devam" not in k.ilk_asama_iyilestirme
    asil = cp_model.CpSolver

    class Kotu(asil):
        def ObjectiveValue(self):
            return 10 ** 9
    monkeypatch.setattr(C.cp_model, "CpSolver", Kotu)
    k.ilk_asama_iyilestirme = {"istenen_saniye": 10}
    r = C._iyilestirmeye_devam(k, {"azami_saniye": 30}, time.time(), cz, _amac(k))
    assert r is None and k.ilk_asama_iyilestirme["devam"]["alindi"] is False
    assert list(k.m.Proto().solution_hint.values) == ipucu
