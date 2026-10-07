# -*- coding: utf-8 -*-
"""
MOLA ADIMI YETISMEZSE IKINCI ASAMANIN PLANI DONER -- K-63 (7 Ekim)

NE BULUNDU (T-60 bulgu 24, 7 Ekim; bulut, 20 sn butce, 0.2 olcek)
  Ucuncu asama (mola adimi) butcenin sonunda kosar; kisa butcede ona 1-2 sn
  kaliyor ve plansiz (UNKNOWN) donuyor. Oysa ikinci asama gecerli bir plan
  bulmus ve TAM ipucu olarak yazmisti: molalar sablonun ideal yerinde, butun
  sert kurallar saglanmis. Motor bu plan eldeyken kullaniciya "sure yetmedi"
  diyordu.

KARAR (K-63, Mustafa, 7 Ekim 07:18): "2. asamanin plani notla donsun onerine
  notumla birlikte katiliyorum." (Notu: musteriye bir sure ARALIGI vermek --
  15-20 dk gibi; o kisim olculdukten sonra spec'e girer, burada sinanmaz.)

NASIL
  Ana asama plansiz donerse (UNKNOWN; INFEASIBLE kanittir, K-37 yolu
  degismez) ve iki asama ikinci asamanin TAM ipucusunu yazdiysa, ipucu
  CP-SAT `fix_variables_to_their_hinted_value` ile plana cevrilir (arama
  yok, yayilim); plan `durma_sebebi: mola_adimi_yetismedi` (ortak aramada
  `ana_asama_yetismedi`) ve notla doner. Sabitlenmis modelin "optimum"u ve
  siniri kanit DEGILDIR: `alt_sinir`, `mola_adimi_alt_sinir`,
  `optimuma_uzaklik_yuzde` None (O-16'nin ayni ailesi). `ipucu_plani`
  ciktida: {bulundu, saniye, durum}; `saniye` butcenin disindaki tek kalem.

BU DOSYA NEYI SINAR
  * yol: plan ikinci asamanin planidir (ipucuyla BIREBIR), notla, sebep adi
    dogru, sinir ve yakinlik yazilmaz, dogrulayici yayinlanabilir der;
  * kapsam: iki asama yoksa (esik alti, baslangic plani) eski cevap aynen
    ("sure_yetmedi"); INFEASIBLE'da K-37 yolu; yarim ipucu bu yoldan gecmez;
  * guvenlik: ipucu gecersiz cikarsa eski cevap; cevirme adimi aramaz
    (sabitleme acik, tek isci, tavan `ipucu_plani_saniye`).
  Tam olcekte cevirme adiminin suresi burada SINANMAZ (olcum: kalite-olc.py
  kayitlarinda `ipucu_plani`).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_mola_adimi_yetismedi.py -v
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model                                # noqa: E402
import dogrulayici                                            # noqa: E402

C = importlib.import_module("cozucu.coz")

from test_fazla_mesai_once_sifir import _sahne, _ornek_sahne, AYAR_URUN   # noqa: E402


def _ana_asama_plansiz(monkeypatch, durum=cp_model.UNKNOWN, gorulen=None):
    """Ana aramaya giden modelin ipucusunu kaydeder, aramayi YAPMADAN
    `durum` dondurur (sure yetmedi / kanit)."""
    def bak(cozucu, model, geri, ayar):
        if gorulen is not None:
            proto = model.Proto()
            gorulen["ipucu"] = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
            gorulen["degisken"] = len(proto.variables)
        return durum
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)


def _plan_ipucuyla_birebir(k, gorulen, atamalar):
    """Donen atamalar VE molalar ipucudaki degerlerle ayni mi? (Inceleme 3:
    yalniz x kiyaslansaydi "molalar yeniden aransin" mutanti yasardi.)"""
    ipucu = gorulen["ipucu"]
    assert len(ipucu) == gorulen["degisken"] > 0                 # TAM ipucu
    secili = {(a["calisan"], a["gun"], a["sablon"]) for a in atamalar}
    for anahtar, v in k.x.items():
        assert (anahtar in secili) == bool(ipucu[v.Index()]), anahtar
    molalar = {(a["calisan"], a["gun"], a["sablon"], m["tip"], m["bas"])
               for a in atamalar for m in a["molalar"]}
    for (e, d, tid, s), v in k.mola.items():
        if (e, d, tid) in secili and s is not None:
            assert ((e, d, tid, "yemek", s) in molalar) == bool(ipucu[v.Index()]), (e, d, tid, s)
    for (e, d, tid, i, s), v in k.dinlenme.items():
        if (e, d, tid) in secili:
            assert ((e, d, tid, "dinlenme", s) in molalar) == bool(ipucu[v.Index()]), (e, d, tid, i, s)


# ----------------------------------------------------------------------
# 1. Yol: mola adimi plansiz -> ikinci asamanin plani, notla
# ----------------------------------------------------------------------

def test_mola_adimi_PLANSIZ_donerse_IKINCI_asamanin_plani_doner_notla_K63(monkeypatch):
    """Mustafa'nin ornegi (hedef agirligi 2.000): ikinci asamanin plani 3 saat
    fazla mesaili, 9.000 puan. Mola adimi UNKNOWN donunce o plan doner:
    durum "cozuldu", sebep `mola_adimi_yetismedi`, atamalar ipucuyla
    birebir, amac 9.000, sinir ve yakinlik YOK, not var, yayinlanabilir."""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    k = Model(g).kur()
    gorulen = {}
    _ana_asama_plansiz(monkeypatch, gorulen=gorulen)
    c = C.coz(g, dict(AYAR_URUN), kuruldu=k)
    assert c["durum"] == "cozuldu", c.get("durum")
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is True and ist["atamalar_sabit"] is True
    assert ist["durma_sebebi"] == "mola_adimi_yetismedi", ist["durma_sebebi"]
    assert ist["amac_degeri"] == 9000 and c["metrikler"]["fazla_mesai_saat"] == 3.0
    assert ist["cozum_sayisi"] == 0 and ist["ilk_cozum_sn"] is None     # ana asama hic plan bulmadi
    assert ist["alt_sinir"] is None and ist["mola_adimi_alt_sinir"] is None
    assert ist["fazla_mesaisiz_alt_sinir"] is None
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is None
    ip = ist["ipucu_plani"]
    assert ip["bulundu"] is True and ip["saniye"] >= 0 and ip["durum"] == "OPTIMAL", ip
    assert ip["kaynak"] == "ikinci_asama", ip
    _plan_ipucuyla_birebir(k, gorulen, c["atamalar"])
    notlar = [n for n in c["uygulanmayan_notlar"] if "ikinci asamanin plani dondu" in n]
    assert len(notlar) == 1 and notlar[0].startswith("mola adimi surede plan uretemedi"), c["uygulanmayan_notlar"]
    assert "molalar sablonun ideal yerinde" in notlar[0] and "kaniti yok" in notlar[0], notlar
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    # amac dagilimi donen planin: fazla mesai 180 dk
    assert ist["amac_dagilimi"]["FAZLA_MESAI"]["deger"] == 180, ist["amac_dagilimi"]


def test_ORTAK_aramada_sebep_ana_asama_yetismedi_kuresel_sinir_YINE_yazilmaz(monkeypatch):
    """`mola_adimi: False` (olcum): atamalar sabit degil, ana asama ortak
    aramadir. O da plansiz donerse ayni yol; sebep `ana_asama_yetismedi`.
    Sabitlenmis ipucunun 'optimum'u tam modelin kaniti DEGILDIR: alt_sinir
    ve yakinlik None (O-16)."""
    g = _sahne(gun=5)
    k = Model(g).kur()
    gorulen = {}
    _ana_asama_plansiz(monkeypatch, gorulen=gorulen)
    c = C.coz(g, dict(AYAR_URUN, mola_adimi=False), kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["atamalar_sabit"] is False
    assert ist["durma_sebebi"] == "ana_asama_yetismedi", ist["durma_sebebi"]
    assert ist["alt_sinir"] is None and ist["mola_adimi_alt_sinir"] is None
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is None
    assert ist["ipucu_plani"]["bulundu"] is True
    _plan_ipucuyla_birebir(k, gorulen, c["atamalar"])
    assert any(n.startswith("ana asama surede plan uretemedi") for n in c["uygulanmayan_notlar"]), c["uygulanmayan_notlar"]


def test_PARALEL_yolda_iki_kol_da_plansizsa_ikinci_asamanin_plani_doner(monkeypatch):
    """(b) secenegi acikken iki arama da UNKNOWN: secilen kolun cozucusu
    plansiz; ipucu plani yine devreye girer."""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    _ana_asama_plansiz(monkeypatch)
    c = C.coz(g, dict(AYAR_URUN, paralel_ipucusuz_isci=1))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["paralel"] is not None and ist["paralel"]["ipuclu"]["plan_bulundu"] is False
    assert ist["durma_sebebi"] == "mola_adimi_yetismedi" and ist["amac_degeri"] == 9000


# ----------------------------------------------------------------------
# 2. Kapsam: iki asama yoksa eski cevap; INFEASIBLE K-37; yarim ipucu
# ----------------------------------------------------------------------

def test_iki_asama_YOKSA_eski_cevap_sure_yetmedi_ipucu_plani_DENENMEZ(monkeypatch):
    """Esigin altindaki model: birinci asama yok, ipucu yok -> "sure_yetmedi"
    aynen (K-37), `ipucu_plani` None (denenmedi bile)."""
    g = _sahne(gun=5)
    _ana_asama_plansiz(monkeypatch)
    ayar = dict(AYAR_URUN)
    del ayar["iki_asama_esigi"]                          # varsayilan esik: 50.000
    c = C.coz(g, ayar)
    assert c["durum"] == "sure_yetmedi", c.get("durum")
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is False and ist["ipucu_plani"] is None, ist["ipucu_plani"]
    assert c.get("teshis_istenebilir") is True


def test_BASLANGIC_plani_yolunda_yarim_ipucu_bu_yoldan_GECMEZ(monkeypatch):
    """K-54 "Iyilestir": baslangic plani ipucudur ama YARIM (x/mola/dinlenme;
    ceza degiskenleri yok) ve iki asama kosmaz. Ana asama plansiz donerse
    eski cevap: "sure_yetmedi", `ipucu_plani` None. (Kullanicinin planini
    geri vermek ayri bir karardir -- burada sinanan, sessizce yapilmadigi.)"""
    g = _sahne(gun=5)
    once = C.coz(g, dict(AYAR_URUN))
    assert once["durum"] == "cozuldu"
    _ana_asama_plansiz(monkeypatch)
    c = C.coz(_sahne(gun=5), dict(AYAR_URUN), baslangic_plani=once["atamalar"])
    assert c["durum"] == "sure_yetmedi", c.get("durum")
    ist = c["cozum_istatistikleri"]
    assert ist["baslangic_plani_kullanildi"] is True and ist["iki_asama"] is False
    assert ist["ipucu_plani"] is None


def test_yarim_ipucu_DOGRUDAN_ipucu_eksik_der_cozmez(monkeypatch):
    """`_ipucu_planini_al` ipucu TAM degilse cozucuyu hic cagirmaz."""
    k = Model(_sahne(gun=5)).kur()
    v = next(iter(k.x.values()))
    k.m.AddHint(v, 1)                                    # tek degisken: yarim
    cagri = []
    monkeypatch.setattr(C.cp_model.CpSolver, "Solve", lambda self, *a, **kw: cagri.append(1) or cp_model.OPTIMAL)
    b = C._ipucu_planini_al(k, dict(C.VARSAYILAN))
    assert b["bulundu"] is False and b["durum"] == "ipucu_eksik" and b["cozucu"] is None, b
    assert cagri == []


def test_INFEASIBLE_kanittir_K37_yolu_degismez_ipucu_plani_DENENMEZ(monkeypatch):
    """Ana asama INFEASIBLE derse bu kanittir (K-37): teshis yolu kosar,
    ipucu planina bakilmaz -- "imkansiz" ile "yetistiremedim" ayri cevaplardir.
    (Gercekte gecerli ipucu varken INFEASIBLE gelmez; sinanan, kodun kanit
    cevabini plana cevirmemesi.)"""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    _ana_asama_plansiz(monkeypatch, durum=cp_model.INFEASIBLE)
    c = C.coz(g, dict(AYAR_URUN))
    assert c["durum"] != "cozuldu", c.get("durum")
    assert c["cozum_istatistikleri"]["ipucu_plani"] is None


# ----------------------------------------------------------------------
# 3. Guvenlik: ipucu gecersizse eski cevap; cevirme adimi ARAMAZ
# ----------------------------------------------------------------------

def test_ipucu_GECERSIZSE_eski_cevap_sure_yetmedi_bulundu_False(monkeypatch):
    """Ipucu bozulursa (butun x degerleri 1: herkes her gun her sablonda --
    kisitlari ihlal eder) sabitleme INFEASIBLE verir; plan UYDURULMAZ, eski
    cevap doner ve `ipucu_plani.bulundu` False yazilir."""
    g = _sahne(gun=5)
    k = Model(g).kur()

    def boz_ve_plansiz(cozucu, model, geri, ayar):
        proto = model.Proto()
        x_ix = {v.Index() for v in k.x.values()}
        degerler = [1 if i in x_ix else d for i, d in zip(proto.solution_hint.vars, proto.solution_hint.values)]
        proto.solution_hint.values.clear()
        proto.solution_hint.values.extend(degerler)
        return cp_model.UNKNOWN
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", boz_ve_plansiz)
    c = C.coz(g, dict(AYAR_URUN, mola_adimi=False), kuruldu=k)      # atamalar sabitlenmesin (ipucu bozulabilsin)
    assert c["durum"] == "sure_yetmedi", c.get("durum")
    ip = c["cozum_istatistikleri"]["ipucu_plani"]
    assert ip["bulundu"] is False and ip["durum"] == "INFEASIBLE", ip
    assert c.get("teshis_istenebilir") is True


def test_cevirme_adimi_ARAMAZ_karar_degiskenleri_SABIT_tek_isci_tavan_ipucu_plani_saniye(monkeypatch):
    """Cevirme adimi bir arama DEGILDIR: butun karar degiskenleri (x, mola,
    dinlenme) ipucu degerine sabitlenir (alan daraltma), ceza degiskenleri
    serbest kalir (amac onlari sikar); tek isci; sure tavani
    `ipucu_plani_saniye` (varsayilan 30; 0/eksi verilirse taban 1 sn). Butce
    (`azami_saniye`) buraya gecmez. `fix_variables_to_their_hinted_value`
    KULLANILMAZ (butun degiskenleri sabitler, gevsek cezalari da -- inceleme 3)."""
    gorulen = []
    asil = C.cp_model.CpSolver

    class Kaydet(asil):
        def Solve(self, model, *a, **kw):
            p = self.parameters
            gorulen.append((p.fix_variables_to_their_hinted_value, p.num_search_workers,
                            p.max_time_in_seconds))
            return asil.Solve(self, model, *a, **kw)
    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **AYAR_URUN)) is True
    assert all(not f for f, _, _ in gorulen)              # hicbir asamada sabitleme parametresi yok
    assert C.VARSAYILAN["ipucu_plani_saniye"] == 30
    proto = k.m.Proto()
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    karar = [v.Index() for sozluk in (k.x, k.mola, k.dinlenme) for v in sozluk.values()]
    ceza_once = {v.Index(): list(proto.variables[v.Index()].domain) for _, v in k.cezalar}
    b = C._ipucu_planini_al(k, dict(C.VARSAYILAN, azami_saniye=900, isci_sayisi=6))
    assert b["bulundu"] is True and gorulen[-1] == (False, 1, 30.0), gorulen[-1]
    assert b["sabitlenen"] == len(karar) > 0, (b["sabitlenen"], len(karar))
    for ix in karar:                                       # karar degiskenleri ipucuya SABIT
        assert list(proto.variables[ix].domain) == [ipucu[ix], ipucu[ix]], ix
    for ix, alan in ceza_once.items():                     # ceza degiskenlerine dokunulmadi
        assert list(proto.variables[ix].domain) == alan, ix
    b = C._ipucu_planini_al(k, dict(C.VARSAYILAN, ipucu_plani_saniye=0))
    assert b["bulundu"] is True and gorulen[-1] == (False, 1, 1.0), gorulen[-1]
    b = C._ipucu_planini_al(k, dict(C.VARSAYILAN, ipucu_plani_saniye=5))
    assert gorulen[-1][2] == 5.0


def test_ipucunun_ceza_degerleri_GEVSEKSE_amac_yine_SIKI_yazilir():
    """Inceleme 3 (B6): ipucunun ceza degerleri gevsek olabilir (birinci
    asamanin amacsiz planinda 0.1-0.2 olcekte +%85-89). Butun degiskenler
    ipucuya sabitlenseydi `amac_degeri` o gevsek toplam olurdu (ornekte
    30.360). Karar degiskenleri sabit, cezalar amacla sikilir: 360."""
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **AYAR_URUN)) is True
    proto = k.m.Proto()
    fm = next(v for _, v in k.cezalar if v.Name().startswith("fm_"))
    konum = list(proto.solution_hint.vars).index(fm.Index())
    gevsek = list(proto.solution_hint.values)
    siki_amac = int(sum(a * gevsek[v.Index()] for a, v in k.cezalar))
    gevsek[konum] = 600                                    # alanin ust siniri (tavan 10 saat)
    proto.solution_hint.values.clear()
    proto.solution_hint.values.extend(gevsek)
    gevsek_amac = int(sum(a * gevsek[v.Index()] for a, v in k.cezalar))
    assert gevsek_amac == siki_amac + 50 * 600, (gevsek_amac, siki_amac)
    b = C._ipucu_planini_al(k, dict(C.VARSAYILAN))
    assert b["bulundu"] is True
    assert int(round(b["cozucu"].ObjectiveValue())) == siki_amac, (b["cozucu"].ObjectiveValue(), siki_amac, gevsek_amac)
    assert int(round(b["cozucu"].Value(fm))) == 0


def test_iyilestirme_plan_BULAMADIYSA_donen_birinci_asamanin_AMACSIZ_plani_not_oyle_der(monkeypatch):
    """Inceleme 3 (B7): iyilestirme plansiz donerse ipucu birinci asamanin
    amacsiz planidir; K-63 onu dondurur ama "ikinci asamanin plani" DEMEZ:
    `kaynak: birinci_asama`, not "AMACSIZ plani (iyilestirme plan bulamadi)"."""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    monkeypatch.setattr(C, "_iyilestirme_coz",
                        lambda model, saniye, isci: (cp_model.UNKNOWN, None, C._CozumSayaci()))
    _ana_asama_plansiz(monkeypatch)
    c = C.coz(g, dict(AYAR_URUN))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["ilk_asama_iyilestirme"]["plan_bulundu"] is False
    assert ist["durma_sebebi"] == "mola_adimi_yetismedi"
    assert ist["ipucu_plani"]["kaynak"] == "birinci_asama", ist["ipucu_plani"]
    notlar = [n for n in c["uygulanmayan_notlar"] if "surede plan uretemedi" in n]
    assert len(notlar) == 1 and "birinci asamanin AMACSIZ plani" in notlar[0], notlar
    assert "ikinci asamanin plani" not in notlar[0], notlar
    # amac SIKI: fazla mesaisiz amacsiz plan, hedef eksigi 8 kisi-saat x 2.000
    assert c["metrikler"]["fazla_mesai_saat"] == 0 and ist["amac_degeri"] == 16000, ist["amac_degeri"]
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_ipucu_KORUNDUYSA_donen_birinci_asamanin_plani_kaynak_korundu(monkeypatch):
    """Iyilestirmenin plani ipucudan kotuyse ipucu korunur (K-61); mola adimi
    de yetismezse donen plan birinci asamanin planidir: `kaynak:
    birinci_asama_korundu`, not bunu soyler."""
    g = _sahne(gun=5)
    asil = C._iyilestirme_coz

    class Sisik:
        def __init__(self, c):
            self._c = c
        def ObjectiveValue(self):
            return self._c.ObjectiveValue() + 1_000_000
        def __getattr__(self, ad):
            return getattr(self._c, ad)

    monkeypatch.setattr(C, "_iyilestirme_coz",
                        lambda m, s, i: (lambda d, c2, say: (d, Sisik(c2), say))(*asil(m, s, i)))
    _ana_asama_plansiz(monkeypatch)
    c = C.coz(g, dict(AYAR_URUN))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["ilk_asama_iyilestirme"]["ipucu_korundu"] is True
    assert ist["ipucu_plani"]["kaynak"] == "birinci_asama_korundu", ist["ipucu_plani"]
    notlar = [n for n in c["uygulanmayan_notlar"] if "surede plan uretemedi" in n]
    assert len(notlar) == 1 and "ipucu korundu" in notlar[0] and "birinci asamanin plani" in notlar[0], notlar


def test_cevirme_suresi_COZUM_SURESINE_girmez_butce_disi_ayri_kalem(monkeypatch):
    """`ipucu_plani.saniye` butcenin disindaki tek kalemdir; `cozum_suresi_sn`
    ana asamanin (plansiz) suresidir. Cevirme 0,6 sn surmus gibi gosterilir:
    cozum suresi degismemeli."""
    asil = C._ipucu_planini_al

    def yavas(kuruldu, ayar):
        b = asil(kuruldu, ayar)
        b["saniye"] = b["saniye"] + 0.6
        return b
    monkeypatch.setattr(C, "_ipucu_planini_al", yavas)
    _ana_asama_plansiz(monkeypatch)
    c = C.coz(_sahne(gun=5), dict(AYAR_URUN))
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu" and ist["ipucu_plani"]["saniye"] >= 0.6
    assert ist["cozum_suresi_sn"] < 0.5, ist["cozum_suresi_sn"]          # ana asama aramadan dondu
    assert c["metrikler"]["cozum_suresi_sn"] == ist["cozum_suresi_sn"]


def test_ana_asama_plan_BULDUYSA_ipucu_planina_bakilmaz_cikti_None():
    """Olagan yol degismez: ana asama plan bulunca `ipucu_plani` None,
    durma sebebi mola adiminin kendi sebebi."""
    c = C.coz(_ornek_sahne({"HEDEF_KAPSAMA": 2000}), dict(AYAR_URUN))
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu" and ist["ipucu_plani"] is None
    assert ist["durma_sebebi"].startswith("mola_adimi_") and ist["durma_sebebi"] != "mola_adimi_yetismedi"
