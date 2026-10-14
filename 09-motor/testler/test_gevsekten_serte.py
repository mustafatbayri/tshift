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


def _fazla_mesaili_gevsek(monkeypatch):
    """Gevsek yolun plani fazla mesaili olsun: gercek gevsek yoldan sonra bir
    fm degiskeni gecici olarak >= 60'a zorlanip plan yeniden aranir (seviye
    1'de gevsek planlar 5-12,5 sa fazla mesailiydi)."""
    asil = C._gevsekten_serte

    def fazla_mesaili(kuruldu, ayar, basladi, **kw):
        d, c = asil(kuruldu, ayar, basladi, **kw)
        v = _fm(kuruldu)[0]
        dom = kuruldu.m.Proto().variables[v.Index()].domain
        eski = list(dom)
        dom.clear()
        dom.extend([60, eski[-1]])
        try:
            c2 = cp_model.CpSolver()
            c2.parameters.max_time_in_seconds = 10
            d2 = c2.Solve(kuruldu.m)
        finally:
            dom.clear()
            dom.extend(eski)
        assert d2 in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        return d2, c2
    monkeypatch.setattr(C, "_gevsekten_serte", fazla_mesaili)


def test_AYAR3_gevsek_plan_fazla_mesailiyse_ONARIM_fazla_mesaisiz_plani_bulur(fm_siz_bulamaz,
                                                                            monkeypatch):
    _fazla_mesaili_gevsek(monkeypatch)
    g = _fm_sert()
    c = coz(g, dict(AYAR_FM))
    assert c["durum"] == "cozuldu"
    o = c["cozum_istatistikleri"]["fazla_mesai_onarimi"]
    assert o["denendi"] is True and o["bulundu"] is True and o["once_dakika"] >= 60
    assert o["durum"] == "OPTIMAL"                                 # amacsiz: ilk bulunan
    assert any("fazla mesai onarimi" in n for n in c["uygulanmayan_notlar"])
    assert c["metrikler"]["fazla_mesai_saat"] == 0
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"]


def test_AYAR3_onarim_ALANLARI_geri_acar_hakem_agirliklar(fm_siz_bulamaz, monkeypatch):
    """Onarim bulsa da bulmasa da fm alanlari eski haline doner (K-61/O-18)."""
    _fazla_mesaili_gevsek(monkeypatch)
    gorulen = {}
    asil = C._ilk_asamada_iyilestir

    def bak(kuruldu, ayar, amacsiz, *a, **k):
        proto = kuruldu.m.Proto()
        gorulen["fm"] = [list(proto.variables[v.Index()].domain) for v in _fm(kuruldu)]
        gorulen["baslangic_fm"] = sum(int(amacsiz.Value(v)) for v in _fm(kuruldu))
        return asil(kuruldu, ayar, amacsiz, *a, **k)
    monkeypatch.setattr(C, "_ilk_asamada_iyilestir", bak)
    c = coz(_fm_sert(), dict(AYAR_FM))
    assert gorulen["fm"] and all(d != [0, 0] for d in gorulen["fm"])
    # iyilestirmenin BASLANGIC plani onarilmis (fazla mesaisiz) plandir
    assert c["cozum_istatistikleri"]["fazla_mesai_onarimi"]["bulundu"] is True
    assert gorulen["baslangic_fm"] == 0


def test_AYAR3_onarim_suresi_AYARDAN_ve_yedegi_yemez(monkeypatch):
    """Onarim en cok `fazla_mesai_onarim_saniye` arar; yedek payina girmez."""
    k = Model(_fm_sert(gun=6)).kur()
    cz = cp_model.CpSolver()
    d = cz.Solve(k.m)                                              # fazla mesaili plan (zorunlu)
    asil = cp_model.CpSolver
    sureler = []

    class Kaydet(asil):
        def Solve(self, model, *a, **kw):
            sureler.append(self.parameters.max_time_in_seconds)
            return asil.Solve(self, model, *a, **kw)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    C._fazla_mesai_onar(k, {"azami_saniye": 100, "fazla_mesai_onarim_saniye": 13}, time.time(), d, cz)
    assert sureler == [13.0]
    sureler.clear()
    C._fazla_mesai_onar(k, {"azami_saniye": 100, "fazla_mesai_onarim_saniye": 500}, time.time(), d, cz)
    assert len(sureler) == 1 and abs(sureler[0] - 74.0) < 0.5        # 100 - 1 - %25 yedek


def test_AYAR3_fazla_mesaisiz_plan_YOKSA_gevsek_plan_AYNEN_doner(fm_siz_bulamaz):
    """Alti gun x alti kisi: herkes 48 saat, fazla mesai zorunlu. Gevsek plan
    fazla mesaili; onarim INFEASIBLE; plan aynen (eli bos donulmez)."""
    c = coz(_fm_sert(gun=6), dict(AYAR_FM))
    assert c["durum"] == "cozuldu"
    o = c["cozum_istatistikleri"]["fazla_mesai_onarimi"]
    assert o["denendi"] is True and o["bulundu"] is False and o["durum"] == "INFEASIBLE"
    assert c["metrikler"]["fazla_mesai_saat"] > 0


def test_AYAR3_KAPALIYKEN_ve_GEREK_YOKKEN_denenmez(fm_siz_bulamaz, monkeypatch):
    c = coz(_fm_sert(), dict(AYAR_FM, fazla_mesai_onarimi=False))
    assert c["cozum_istatistikleri"]["fazla_mesai_onarimi"] is None
    # gerek yok: plan zaten fazla mesaisiz -> denenmez, ayni cozucu doner
    k = Model(_fm_sert()).kur()
    eski = C._fazla_mesaiyi_sifirla(k)
    cz = cp_model.CpSolver()
    d = cz.Solve(k.m)
    C._fazla_mesaiyi_serbest_birak(k, eski)
    d2, c2 = C._fazla_mesai_onar(k, dict(AYAR_FM, fazla_mesai_onarim_saniye=20), time.time(), d, cz)
    assert c2 is cz and d2 == d
    assert k.fazla_mesai_onarimi == {"denendi": False, "once_dakika": 0, "bulundu": False,
                                     "saniye": 0.0, "durum": None}
