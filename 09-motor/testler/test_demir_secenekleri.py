# -*- coding: utf-8 -*-
"""
DEMIR SECENEKLERI -- T-60 bulgu 8'in iki OLCUM secenegi (2 Ekim)

NE BULUNDU (tam olcek, 500 kisi, 600 sn, Mustafa'nin makinesi)
  Urunun hali (birinci asamanin AMACSIZ plani ipucu) haftada 475-511 saat
  fazla mesai yaziyor; ipucu kapatilinca ayni hedef eksigiyle 227,75 saat --
  ama ipucusuz arama iki kosudan birinde 600 saniyede HIC plan bulamadi.
  Ipucu aramayi kotu plana demirliyor; demirsiz arama guvenilir degil.

BU DOSYA NEYI SINAR
  Iki secenegin de VARSAYILANI KAPALI; urunun davranisi degismez.
  (a) `ilk_asama_iyilestirme_saniye`: birinci asama gecerli plani bulduktan
      sonra, molalar hala sabitken amaci geri koyup iyilestirir; ipucu
      iyilesmis plan olur. Plan bulamazsa amacsiz planin ipucu KALIR.
  (b) `paralel_ipucusuz_isci`: ana asamada ipuclu ve ipucusuz arama yan
      yana, ayni surede; iyi olan secilir.
  Hangisinin tam olcekte ise yaradigi burada SINANMAZ -- o bir olcumdur
  (08-motor-testleri/gercekci-veri-seti/kalite-olc.py).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_demir_secenekleri.py -v
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model                                # noqa: E402
import dogrulayici                                            # noqa: E402

C = importlib.import_module("cozucu.coz")

POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]
SABAH = {"id": "SABAH", "ekip": "E", "bas": 7, "bit": 16.25, "mola_dk": 60,
         "mola_politikasi": POLITIKA}
AKSAM = {"id": "AKSAM", "ekip": "E", "bas": 13.75, "bit": 23, "mola_dk": 60,
         "mola_politikasi": POLITIKA}


def _sahne(kisi=6, gunler=range(3), mola_kapsamasi=False):
    """Hedef asgarinin ustunde: amacsiz bir plan asgariyi tutturup durabilir,
    amacli arama hedefi de kapatmaya calisir -- iki plan arasinda fark OLUR."""
    kurallar = [
        {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False},
        {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        {"kod": "HEDEF_ASIMI", "tur": "YUMUSAK", "aktif": True},
        {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
        {"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True, "yasal": False,
         "parametreler": {"en_az_saat": 3, "en_gec_saat": 5}},
    ]
    if mola_kapsamasi:
        kurallar.append({"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True})
    return {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C%d" % i, "ekipler": ["E"],
                        "sozlesme": {"tip": "yari_zamanli"},
                        "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
        "vardiya_sablonlari": [dict(SABAH), dict(AKSAM)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 2}
                  for d in gunler for s in range(7, 23)],
        "kurallar": kurallar, "kilitler": [], "donmus_gunler": [],
    }


AYAR = {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5,
        "isci_sayisi": 2}


def _ipucu_amaci(k):
    proto = k.m.Proto()
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    return int(sum(a * ipucu[v.Index()] for a, v in k.cezalar)), ipucu


def _kapali_alan(k):
    proto = k.m.Proto()
    return [i for i in range(len(proto.variables)) if list(proto.variables[i].domain) == [0, 0]]


# ----------------------------------------------------------------------
# 0. Varsayilan: iki secenek de KAPALI, urun ayni
# ----------------------------------------------------------------------

def test_varsayilan_K59_a_ACIK_orandan_b_ve_atama_sabitleme_KAPALI():
    """K-59 (3 Ekim, Mustafa: "olsun"): birinci asamada iyilestirme urunun
    varsayilani; suresi butcenin %40'i (kalibrasyon). (b) ve atama sabitleme
    olcum secenegi olarak kapali."""
    assert C.VARSAYILAN["ilk_asama_iyilestirme_saniye"] is None
    assert C.VARSAYILAN["ilk_asama_iyilestirme_orani"] == 0.4
    assert C.VARSAYILAN["ilk_asama_iyilestirme_ipucusuz"] is False
    assert C.VARSAYILAN["paralel_ipucusuz_isci"] == 0
    assert C.VARSAYILAN["ana_asama_atamalar_sabit"] is False
    c = C.coz(_sahne(), dict(AYAR))
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu" and ist["iki_asama"] is True
    b = ist["ilk_asama_iyilestirme"]
    assert b is not None and b["plan_bulundu"] is True, b
    assert abs(b["istenen_saniye"] - 0.4 * AYAR["azami_saniye"]) < 1e-6, b   # 30 sn -> 12 sn
    assert b["saniye"] <= 0.4 * AYAR["azami_saniye"] + 0.5, b
    assert "amac_dagilimi" in b and sum(d["ceza"] for d in b["amac_dagilimi"].values()) == b["iyilesmis_amac"], b
    assert ist["paralel"] is None, ist["paralel"]
    assert ist["atamalar_sabit"] is False


def test_iyilestirme_SIFIR_ile_kapatilir_eski_davranis():
    c = C.coz(_sahne(), dict(AYAR, ilk_asama_iyilestirme_saniye=0))
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu" and ist["iki_asama"] is True
    assert ist["ilk_asama_iyilestirme"] is None, ist["ilk_asama_iyilestirme"]


# ----------------------------------------------------------------------
# Olcum: ana asama atamalari sabitler, yalniz molalari arar
# ----------------------------------------------------------------------

def test_atamalar_sabit_ana_asama_x_i_DEGISTIREMEZ_molalari_arar(monkeypatch):
    gorulen = {}
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        proto = model.Proto()
        gorulen["sabit_x"] = {i for i in range(len(proto.variables))
                              if len(proto.variables[i].domain) == 2
                              and proto.variables[i].domain[0] == proto.variables[i].domain[1]}
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    g = _sahne(kisi=4, gunler=[0], mola_kapsamasi=True)
    k = Model(g).kur()
    c = C.coz(g, dict(AYAR, ana_asama_atamalar_sabit=True), kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["atamalar_sabit"] is True
    x_indisleri = {v.Index() for v in k.x.values()}
    assert x_indisleri <= gorulen["sabit_x"], "atama degiskenleri sabitlenmedi"
    mola_indisleri = {v.Index() for v in k.mola.values()} | {v.Index() for v in k.dinlenme.values()}
    assert not (mola_indisleri & gorulen["sabit_x"]), "mola degiskenleri de sabitlendi"
    # donen plan = sabitlenen atamalar (ipucu 1 olanlar)
    proto = k.m.Proto()
    sabit_bir = {anahtar for anahtar, v in k.x.items() if list(proto.variables[v.Index()].domain) == [1, 1]}
    donen = {(a["calisan"], a["gun"], a["sablon"]) for a in c["atamalar"]}
    assert donen == sabit_bir, (donen, sabit_bir)
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_atamalar_sabit_ipucu_yoksa_UYGULANMAZ_not_duser():
    c = C.coz(_sahne(), dict(AYAR, iki_asama_esigi=10 ** 9, ana_asama_atamalar_sabit=True))
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["atamalar_sabit"] is False
    assert any("ana_asama_atamalar_sabit yok sayildi" in n for n in c["uygulanmayan_notlar"])


# ----------------------------------------------------------------------
# (a) birinci asamada iyilestirme
# ----------------------------------------------------------------------

def test_a_ipucu_IYILESMIS_plandir_ve_amacsizdan_KOTU_degildir():
    k = Model(_sahne()).kur()
    ayar = dict(C.VARSAYILAN, **AYAR)
    ayar["ilk_asama_iyilestirme_saniye"] = 10
    assert C._ipucu_ver(k, ayar) is True
    b = k.ilk_asama_iyilestirme
    assert b["plan_bulundu"] is True and b["cozum_sayisi"] >= 1, b
    assert b["iyilesmis_amac"] <= b["amacsiz_amac"], b
    amac, ipucu = _ipucu_amaci(k)
    proto = k.m.Proto()
    # ipucu TAM ve iyilesmis planin kendisi
    assert len(proto.solution_hint.vars) == len(proto.variables)
    assert amac == b["iyilesmis_amac"], (amac, b)
    # amac geri konmus, alanlar geri acilmis
    assert len(proto.objective.vars) > 0 or len(proto.floating_point_objective.vars) > 0
    assert not _kapali_alan(k)
    # iyilestirme molalari SABIT tutar: ipucudaki her vardiya sabit secimde
    for t in k.sablonlar:
        sy, dinl = k.sabit_mola_secimi(t)
        for (e, d, tid), v in k.x.items():
            if tid != t["id"] or ipucu[v.Index()] != 1:
                continue
            yemek = [s for (e2, d2, t2, s), mv in k.mola.items()
                     if (e2, d2, t2) == (e, d, tid) and ipucu[mv.Index()] == 1]
            assert yemek == [sy], (tid, yemek, sy)


def test_a_iyilestirme_sabit_molali_modelin_OPTIMUMUNA_ulasir():
    """Mola kapsamasi kapaliyken molanin yeri amaci degistirmez: sabit molali
    kucuk modelin optimumu tam modelin optimumudur. Iyilestirme o degere
    ulasmali -- ulasmiyorsa amac geri konmamis ya da sure verilmemistir."""
    g = _sahne()
    tam = C.coz(g, dict(AYAR, iki_asama_esigi=10 ** 9))["cozum_istatistikleri"]
    assert tam["amac_degeri"] == tam["alt_sinir"], tam           # kanitli optimum
    k = Model(g).kur()
    ayar = dict(C.VARSAYILAN, **AYAR)
    ayar["ilk_asama_iyilestirme_saniye"] = 15
    assert C._ipucu_ver(k, ayar) is True
    b = k.ilk_asama_iyilestirme
    assert b["optimum"] is True, b
    assert b["iyilesmis_amac"] == tam["amac_degeri"], (b, tam["amac_degeri"])


def test_a_plan_bulunamazsa_amacsiz_ipucu_KALIR(monkeypatch):
    """Guvenlik agi: ipucusuz baslatilan iyilestirme plan bulamazsa, ana
    asama yine amacsiz planin TAM ipucuyla baslar."""
    def bulamadi(model, saniye, isci):
        assert len(model.Proto().solution_hint.vars) == 0, "ipucusuz istenmisti"
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", bulamadi)
    k = Model(_sahne()).kur()
    ayar = dict(C.VARSAYILAN, **AYAR)
    ayar.update(ilk_asama_iyilestirme_saniye=5, ilk_asama_iyilestirme_ipucusuz=True)
    assert C._ipucu_ver(k, ayar) is True
    b = k.ilk_asama_iyilestirme
    assert b["plan_bulundu"] is False and b["iyilesmis_amac"] is None, b
    proto = k.m.Proto()
    assert len(proto.solution_hint.vars) == len(proto.variables), "ipucu kayboldu"
    amac, _ = _ipucu_amaci(k)
    assert amac == b["amacsiz_amac"], (amac, b)
    assert len(proto.objective.vars) > 0 or len(proto.floating_point_objective.vars) > 0
    assert not _kapali_alan(k)


def test_a_ipuclu_iyilestirme_ipucuyu_SILMEZ(monkeypatch):
    gorulen = {}

    def bak(model, saniye, isci):
        gorulen["ipucu"] = len(model.Proto().solution_hint.vars)
        gorulen["amac"] = len(model.Proto().objective.vars)
        gorulen["saniye"] = saniye
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", bak)
    k = Model(_sahne()).kur()
    ayar = dict(C.VARSAYILAN, **AYAR)
    ayar.update(ilk_asama_iyilestirme_saniye=5)
    C._ipucu_ver(k, ayar)
    assert gorulen["ipucu"] == len(k.m.Proto().variables), gorulen
    assert gorulen["amac"] > 0, "iyilestirme AMACSIZ kosuldu"
    assert gorulen["saniye"] == 5, gorulen


def test_a_sure_BUTCENIN_ICINDEN_ve_en_cok_YUZDE_KIRKI(monkeypatch):
    gorulen = {}

    def bak(model, saniye, isci):
        gorulen["saniye"] = saniye
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", bak)
    k = Model(_sahne()).kur()
    ayar = dict(C.VARSAYILAN, **AYAR)
    ayar.update(azami_saniye=8, ilk_asama_iyilestirme_saniye=500)
    C._ipucu_ver(k, ayar)
    # istenen 500 sn; butce 8 sn -> en cok %40'i (3,2 sn). Ana asamaya sure kalir.
    assert 0 < gorulen["saniye"] <= 3.2 + 1e-6, gorulen
    b = k.ilk_asama_iyilestirme
    assert b["istenen_saniye"] == 500, b


def test_a_uctan_uca_iki_asamanin_toplami_butceyi_GECMEZ():
    c = C.coz(_sahne(), dict(AYAR, azami_saniye=12, ilk_asama_iyilestirme_saniye=4))
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu"
    assert ist["ilk_asama_iyilestirme"]["plan_bulundu"] is True
    assert ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"] <= 12.05, ist


def test_a_uctan_uca_plan_yayinlanabilir_ve_molalar_SERBEST():
    """Ana asama molalari serbest arar (K-32): MOLA_KAPSAMASI acikken iki
    kisinin molasi ayni dakikada kalmamali; plan dogrulayicidan gecmeli."""
    g = _sahne(kisi=4, gunler=[0], mola_kapsamasi=True)
    c = C.coz(g, dict(AYAR, ilk_asama_iyilestirme_saniye=5))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is True and ist["ilk_asama_iyilestirme"]["plan_bulundu"]
    assert ist["amac_degeri"] <= ist["ilk_asama_iyilestirme"]["iyilesmis_amac"], ist
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    assert sum(d["ceza"] for d in ist["amac_dagilimi"].values()) == ist["amac_degeri"]


# ----------------------------------------------------------------------
# (b) ipuclu + ipucusuz yan yana
# ----------------------------------------------------------------------

def test_b_iki_arama_kosar_IYI_olan_secilir_plan_gecerlidir():
    g = _sahne()
    c = C.coz(g, dict(AYAR, paralel_ipucusuz_isci=1))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    p = ist["paralel"]
    assert p["secilen"] in ("ipuclu", "ipucusuz"), p
    assert p["ipuclu"]["isci"] == 1 and p["ipucusuz"]["isci"] == 1, p
    # Biri optimumu kanitlayip otekini durdurabilir; durdurulan plansiz
    # kalabilir. Soz: SECILENIN plani vardir.
    assert p[p["secilen"]]["plan_bulundu"] is True, p
    amaclar = [p[a]["amac_degeri"] for a in ("ipuclu", "ipucusuz") if p[a]["plan_bulundu"]]
    assert ist["amac_degeri"] == min(amaclar), (ist["amac_degeri"], p)
    assert p[p["secilen"]]["amac_degeri"] == ist["amac_degeri"], p
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    assert sum(d["ceza"] for d in ist["amac_dagilimi"].values()) == ist["amac_degeri"]


def test_b_KOPYAYI_cozen_cozucunun_plani_asil_modelden_dogru_okunur():
    """(b)'de secilen arama modelin KOPYASINI cozmus olabilir; atamalar ve
    amac kirilimi yine asil modelin degiskenleriyle okunur. Burada kopya tek
    basina cozulur (yaris yok) ve okunan plan dogrulayiciya gosterilir."""
    g = _sahne(kisi=4, gunler=[0], mola_kapsamasi=True)
    k = Model(g).kur()
    kopya = k.m.Clone()
    c2 = cp_model.CpSolver()
    c2.parameters.max_time_in_seconds = 20
    c2.parameters.num_search_workers = 2
    assert c2.Solve(kopya) == cp_model.OPTIMAL
    atamalar = C._atamalari_cikar(k, c2)
    assert len(atamalar) >= 2, atamalar
    dagilim = C._amac_dagilimi(k, c2)
    assert sum(d["ceza"] for d in dagilim.values()) == int(c2.ObjectiveValue()), dagilim
    r = dogrulayici.degerlendir(g, atamalar)
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    # ayni sahnenin urun yoluyla bulunan optimumu ayni olmali
    urun = C.coz(g, dict(AYAR))["cozum_istatistikleri"]
    assert urun["amac_degeri"] == urun["alt_sinir"] == int(c2.ObjectiveValue()), urun


def test_b_ipucusuz_arama_plansiz_kalsa_da_plan_DONER():
    """Guvenlik agi: ipuclu arama optimumu kanitlayip otekini durdurdugunda
    ipucusuz arama plansiz kalabilir; donen plan ipuclunun planidir."""
    for _ in range(4):
        c = C.coz(_sahne(kisi=4, gunler=[0], mola_kapsamasi=True),
                  dict(AYAR, paralel_ipucusuz_isci=1))
        p = c["cozum_istatistikleri"]["paralel"]
        assert c["durum"] == "cozuldu", p
        assert p[p["secilen"]]["plan_bulundu"] is True, p


def test_b_secim_kurali_amaci_KUCUK_olan_esitlikte_ipuclu_plansizsa_oteki():
    class S(object):
        def __init__(self, v):
            self.v = v

        def ObjectiveValue(self):
            return self.v
    F, U = cp_model.FEASIBLE, cp_model.UNKNOWN
    a = lambda sira, durum, v: {"sira": sira, "durum": durum, "cozucu": S(v)}
    assert C._paralel_sec([a(0, F, 100), a(1, F, 60)])["sira"] == 1
    assert C._paralel_sec([a(0, F, 60), a(1, F, 100)])["sira"] == 0
    assert C._paralel_sec([a(0, F, 60), a(1, F, 60)])["sira"] == 0
    assert C._paralel_sec([a(0, F, 60), a(1, U, 0)])["sira"] == 0
    assert C._paralel_sec([a(0, U, 0), a(1, F, 60)])["sira"] == 1
    assert C._paralel_sec([a(0, U, 0), a(1, U, 0)])["sira"] == 0


def test_b_ipucu_yoksa_paralel_KOSMAZ_ve_not_duser():
    c = C.coz(_sahne(), dict(AYAR, iki_asama_esigi=10 ** 9, paralel_ipucusuz_isci=1))
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["paralel"] is None
    assert any("paralel_ipucusuz_isci yok sayildi" in n for n in c["uygulanmayan_notlar"])


def test_b_asil_modelin_ipucu_durur_kopyanin_ipucu_SILINIR(monkeypatch):
    gorulen = []
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        gorulen.append((len(model.Proto().solution_hint.vars), len(model.Proto().variables),
                        cozucu.parameters.num_search_workers,
                        cozucu.parameters.max_time_in_seconds))
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    c = C.coz(_sahne(), dict(AYAR, isci_sayisi=4, paralel_ipucusuz_isci=1))
    assert c["durum"] == "cozuldu"
    assert len(gorulen) == 2, gorulen
    ipuclu = [g for g in gorulen if g[0] > 0]
    ipucusuz = [g for g in gorulen if g[0] == 0]
    assert len(ipuclu) == 1 and len(ipucusuz) == 1, gorulen
    assert ipuclu[0][0] == ipuclu[0][1]                         # tam ipucu
    assert ipuclu[0][2] == 3 and ipucusuz[0][2] == 1, gorulen   # 4 isci: 3 + 1
    assert abs(ipuclu[0][3] - ipucusuz[0][3]) < 1e-6, gorulen   # AYNI sure
