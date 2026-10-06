# -*- coding: utf-8 -*-
"""
ONCE FAZLA MESAISIZ -- T-60 bulgu 20'nin OLCUM secenegi (6 Ekim)

NE BULUNDU (tam olcek, 500 kisi, %95 doluluk, 900 sn, ucer kosu, Mustafa'nin
makinesi; kalite-olcumu-95-profiller-900.json)
  CALISAN profili (fazla mesai tavani 0 -> SERT sinir) uc kosuda da 0 saat
  fazla mesaiyle plan buldu. O planlar DENGELI'nin KENDI agirliklariyla
  26.589-26.703 puan ediyor; DENGELI'nin kendi buldugu planlar
  105.742-148.431. DENGELI'nin uc kosusunda fazla mesai DISINDAKI toplam
  26.931 / 26.972 / 26.992 (%0,2 oynuyor); oynayan tek sey fazla mesai
  (26,25-40,5 saat). Yani fazla mesai verinin zorladigi bir sey degil,
  aramanin ARTIGI: yumusak cezayla sifira itilemiyor, sert sinirla 13-33
  saniyede sifirlaniyor.

BU DOSYA NEYI SINAR
  `fazla_mesai_once_sifir` (varsayilan KAPALI; urun davranisi degismez):
    * birinci asama gecerli plani fazla mesai degiskenleri [0,0]'a
      sabitken arar;
    * BULURSA fazla mesai butun asamalarda 0'da kalir (K-30'un tablosu:
      "yalniz hedef kapsama iyilesecek -> fazla mesai yapilmaz");
    * BULAMAZSA (kanit ya da sure) alanlar AYNEN geri acilir, bugunku yol
      isler (K-30: "asgari fazla mesaisiz tutmuyor -> yapilir, gereken
      kadar"), not duser -- zorunlu fazla mesai yolu KAPANMAZ (K-38);
    * yalniz IKI ASAMALI yolda uygulanir (esigin altindaki model ve
      baslangic plani verilen kosu etkilenmez).
  Tam olcekte ne kazandirdigi burada SINANMAZ -- o bir olcumdur
  (08-motor-testleri/gercekci-veri-seti/kalite-olc.py `fm_once_sifir`).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_fazla_mesai_once_sifir.py -v
"""

import importlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model                                # noqa: E402
import dogrulayici                                            # noqa: E402

C = importlib.import_module("cozucu.coz")

AYAR = {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5,
        "isci_sayisi": 2, "fazla_mesai_once_sifir": True}


def _sahne(gun=5, tip="tam_zamanli"):
    """Alti kisi, tek sablon (9 brut / 8 net saat), her gun alti kisi ZORUNLU.

    gun=5 -> herkes 40 saat: fazla mesai GEREKMEZ (45 saat sozlesme).
    gun=6 -> herkes 48 saat: 3'er saat fazla mesai ZORUNLU (K-38'in sahnesi,
             bkz. test_fazla_mesai_yolu.py).
    Hedef 7 kisi, kadro 6: HEDEF_KAPSAMA cezasi her hucrede en az 1 --
    fazla mesai disinda SIFIRLANAMAYAN bir ceza hep var (sifirlama yalniz
    fazla mesaiye dokunmali)."""
    sozlesme = {"tip": tip}
    if tip == "tam_zamanli":
        sozlesme["haftalik_saat"] = 45
    return {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C%d" % i, "ekipler": ["E"], "sozlesme": dict(sozlesme),
                        "izinler": [], "uygunluk": []} for i in range(1, 7)],
        "vardiya_sablonlari": [
            {"id": "V1", "ekip": "E", "bas": 8, "bit": 17, "mola_dk": 60,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1,
                                  "ucretli": False}]}],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 6, "hedef": 7}
                  for d in range(gun) for s in range(9, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 11}},
            {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 45}},
            {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True,
             "parametreler": {"azami_saat_hafta": 10}},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def _fm(k):
    return [v for _, v in k.cezalar if v.Name().startswith("fm_")]


def _alanlar(k, degiskenler):
    proto = k.m.Proto()
    return [list(proto.variables[v.Index()].domain) for v in degiskenler]


def _ana_asamayi_izle(monkeypatch, k, gorulen):
    """Ana asamaya giden modelde fazla mesai ve oteki ceza degiskenlerinin
    alanlarini kaydeder, sonra asil aramayi cagirir."""
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        gorulen["fm"] = _alanlar(k, _fm(k))
        gorulen["oteki"] = _alanlar(k, [v for _, v in k.cezalar
                                        if not v.Name().startswith("fm_")])
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)


# ----------------------------------------------------------------------
# 0. Varsayilan KAPALI: urun ayni
# ----------------------------------------------------------------------

def test_varsayilan_KAPALI_urun_davranisi_ayni(monkeypatch):
    assert C.VARSAYILAN["fazla_mesai_once_sifir"] is False
    g = _sahne(gun=6)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    assert len(once) == 6 and all(a == [0, 600] for a in once), once      # tavan 10 saat
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    ayar = dict(AYAR)
    del ayar["fazla_mesai_once_sifir"]
    c = C.coz(g, ayar, kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"] is None
    assert gorulen["fm"] == once
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])


# ----------------------------------------------------------------------
# 1. Fazla mesaisiz plan VARSA: bulunur, fazla mesai 0'da KALIR
# ----------------------------------------------------------------------

def test_fazla_mesaisiz_plan_VARSA_fazla_mesai_butun_asamalarda_SIFIR(monkeypatch):
    g = _sahne(gun=5)
    k = Model(g).kur()
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is True
    b = ist["fazla_mesai_once_sifir"]
    assert b["bulundu"] is True and b["degisken"] == 6 and b["kanitlandi_yok"] is False, b
    assert c["metrikler"]["fazla_mesai_saat"] == 0, c["metrikler"]
    # ana asamada (mola adimi) fazla mesai degiskenleri HALA [0,0]
    assert gorulen["fm"] == [[0, 0]] * 6, gorulen["fm"]
    # ... ve YALNIZ onlar: hedef cezasi serbest (kadro 6, hedef 7 -> sifirlanamaz)
    assert gorulen["oteki"] and all(a[-1] > 0 for a in gorulen["oteki"]), gorulen["oteki"][:3]
    assert ist["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] > 0
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


# ----------------------------------------------------------------------
# 2. Fazla mesai ZORUNLUYSA: yol KAPANMAZ (K-38), alanlar geri acilir
# ----------------------------------------------------------------------

def test_fazla_mesai_ZORUNLUYSA_kanitlanir_alanlar_GERI_ACILIR_plan_doner(monkeypatch):
    g = _sahne(gun=6)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu", (
        "fazla mesaisiz deneme zorunlu fazla mesai yolunu kapatti: %s" % c["durum"])
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is False and b["kanitlandi_yok"] is True, b
    assert b["molalar_sabit"] is True, b            # kanit molalar sabitken aranan modelin
    # fazla mesai serbestken YENIDEN arandi ve birinci asama ipucunu verdi
    assert c["cozum_istatistikleri"]["iki_asama"] is True
    assert c["metrikler"]["fazla_mesai_saat"] > 0, c["metrikler"]
    assert gorulen["fm"] == once, (gorulen["fm"], once)
    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (molalar sabitken kanitlandi)" in notlar[0], \
        c["uygulanmayan_notlar"]
    assert "serbest birakildi" in notlar[0], notlar
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_fazla_mesaisiz_deneme_SUREYE_takilirsa_kanit_DENMEZ_butce_asilmaz(monkeypatch):
    """Ilk arama UNKNOWN donerse (sure yetmedi): "yok" DENMEZ, alanlar geri
    acilir, ikinci arama birinci asamanin payini ve kalan butceyi ASMAZ."""
    cagri = []
    asil = C.cp_model.CpSolver

    class IlkiSureyeTakilir(asil):
        def Solve(self, model, *a, **kw):
            cagri.append(self.parameters.max_time_in_seconds)
            if len(cagri) == 1:
                return cp_model.UNKNOWN
            return asil.Solve(self, model, *a, **kw)

    monkeypatch.setattr(C.cp_model, "CpSolver", IlkiSureyeTakilir)
    g = _sahne(gun=5)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is False and b["kanitlandi_yok"] is False, b
    assert c["cozum_istatistikleri"]["iki_asama"] is True
    assert len(cagri) >= 2, cagri
    assert gorulen["fm"] == once
    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "bu surede bulunamadi" in notlar[0], notlar
    pay = C._ilk_asama_payi(dict(C.VARSAYILAN, **AYAR))                   # 30 x %20 = 6 sn
    assert abs(cagri[0] - pay) < 1e-6, cagri
    assert 1.0 <= cagri[1] <= pay + 1e-6, cagri
    ist = c["cozum_istatistikleri"]
    assert ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"] <= AYAR["azami_saniye"] + 0.05, ist


def test_yeniden_arama_suresi_PAY_ve_KALAN_butceyle_sinirlidir(monkeypatch):
    """Ikinci arama en cok birinci asamanin payi kadar surer; fazla mesaisiz
    deneme butcenin cogunu yediyse KALANI alir (1 sn pay birakarak), en az
    1 sn (sifir sure CP-SAT'e "hic arama" demek olurdu -- ana asamadaki
    taban ile ayni)."""
    gorulen = []
    asil = C.cp_model.CpSolver

    class Kaydet(asil):
        def Solve(self, model, *a, **kw):
            gorulen.append(self.parameters.max_time_in_seconds)
            return asil.Solve(self, model, *a, **kw)

    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    k = Model(_sahne(gun=5)).kur()
    k.m.ClearObjective()
    ayar = dict(C.VARSAYILAN, **AYAR)                       # azami 30 -> pay 6 sn
    pay = C._ilk_asama_payi(ayar)
    assert abs(pay - 6.0) < 1e-6, pay
    durum, c = C._gecerli_plan_yeniden_ara(k, ayar, time.time())           # kalan ~29
    assert durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    assert abs(gorulen[-1] - pay) < 1e-6, gorulen
    C._gecerli_plan_yeniden_ara(k, ayar, time.time() - 25.0)               # kalan ~4
    assert 3.0 <= gorulen[-1] <= 4.0 + 1e-6, gorulen
    C._gecerli_plan_yeniden_ara(k, ayar, time.time() - 40.0)               # kalan < 0
    assert gorulen[-1] == 1.0, gorulen


def _yavas_ilk_arama(monkeypatch, saniye, ilk_durum=None):
    """Birinci aramayi `saniye` kadar geciktirir; `ilk_durum` verilirse o
    durumu dondurur (UNKNOWN: "sure yetmedi"). Iyilestirmeye verilen sureyi
    kaydeder, iyilestirmeyi kosturmaz."""
    cagri = []
    asil = C.cp_model.CpSolver

    class Yavas(asil):
        def Solve(self, model, *a, **kw):
            cagri.append(1)
            if len(cagri) == 1:
                time.sleep(saniye)
                if ilk_durum is not None:
                    return ilk_durum
            return asil.Solve(self, model, *a, **kw)

    monkeypatch.setattr(C.cp_model, "CpSolver", Yavas)
    gorulen = {}

    def kaydet(model, saniye, isci):
        gorulen["saniye"] = saniye
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", kaydet)
    return gorulen


# ⚠ O-12 dersi: asagidaki uc test saatin cozunurlugune ya da makinenin hizina
#   GUVENMEZ. Beklenen deger "1,5 sn" sabitinden degil, motorun OLCTUGU deneme
#   suresinden (`fazla_mesai_once_sifir.saniye`) hesaplanir; butce 100 sn
#   secildi ki kalan butce (≈97 sn) payi (80 sn) hicbir makinede sinirlamasin.
UZUN = dict(AYAR, azami_saniye=100)                          # iyilestirme payi %80 = 80 sn


def test_BASARISIZ_denemenin_suresi_iyilestirmenin_payindan_DUSER(monkeypatch):
    """Fazla mesaisiz deneme plan bulamadan sure harcadiysa o sure
    iyilestirmenin payindan (%80) duser: mola adimina kalan sure bugunku
    yolla ayni kalmali. Dusulmezse en kotu halde birinci asama butcenin
    tamamini yer ve mola adimina 1 sn kalir (elde plan varken "sure yetmedi")."""
    gorulen = _yavas_ilk_arama(monkeypatch, 1.5, ilk_durum=cp_model.UNKNOWN)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **UZUN)) is True
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is False and 1.0 < b["saniye"] < 30.0, b
    # pay 80 sn - OLCULEN deneme suresi (cikti 2 haneye yuvarli: pay 0,02)
    assert abs(gorulen["saniye"] - (80.0 - b["saniye"])) <= 0.02, (gorulen, b)


def test_BASARISIZ_denemenin_suresi_ACIKCA_istenen_sureden_de_DUSER(monkeypatch):
    """`ilk_asama_iyilestirme_saniye` acikca verildiyse (olcum yapilandirmalari)
    deneme suresi ONDAN da duser; yalniz paydan dusulurse istenen sure paydan
    kisayken hic dusulmemis olur ve mola adiminin suresi kisalir."""
    gorulen = _yavas_ilk_arama(monkeypatch, 1.5, ilk_durum=cp_model.UNKNOWN)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **dict(UZUN, ilk_asama_iyilestirme_saniye=10))) is True
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is False and 1.0 < b["saniye"] < 9.0, b
    assert abs(gorulen["saniye"] - (10.0 - b["saniye"])) <= 0.02, (gorulen, b)


def test_BASARILI_denemenin_suresi_DUSMEZ_o_zaten_birinci_asamanin_aramasidir(monkeypatch):
    """Deneme plan bulduysa ayri bir "deneme" yoktur: o arama birinci asamanin
    gecerli plan aramasinin kendisidir, iyilestirmenin payi (%80) aynen kalir."""
    gorulen = _yavas_ilk_arama(monkeypatch, 1.5)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **UZUN)) is True
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is True and 1.0 < b["saniye"] < 30.0, b
    assert abs(gorulen["saniye"] - 80.0) < 1e-6, gorulen


def test_secenek_KAPALIYKEN_iyilestirmenin_payi_AYNEN(monkeypatch):
    """Urunun varsayilan yolu: yavas birinci arama iyilestirmenin payini
    kisaltmaz (pay %80; yalniz kalan butce sinirlar)."""
    gorulen = _yavas_ilk_arama(monkeypatch, 1.5)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **dict(UZUN, fazla_mesai_once_sifir=False))) is True
    assert k.fazla_mesai_once_sifir is None
    assert abs(gorulen["saniye"] - 80.0) < 1e-6, gorulen


# ----------------------------------------------------------------------
# 3. Sifirlama YALNIZ fazla mesai degiskenlerine dokunur; geri alma TAMDIR
# ----------------------------------------------------------------------

def test_sifirlama_YALNIZ_fm_degiskenlerine_dokunur_geri_alma_AYNEN():
    k = Model(_sahne(gun=6)).kur()
    proto = k.m.Proto()
    once = [list(v.domain) for v in proto.variables]
    eski = C._fazla_mesaiyi_sifirla(k)
    fm_ix = {v.Index() for v in _fm(k)}
    assert {ix for ix, _ in eski} == fm_ix and len(fm_ix) == 6
    for i, v in enumerate(proto.variables):
        if i in fm_ix:
            assert list(v.domain) == [0, 0], (i, list(v.domain))
        else:
            assert list(v.domain) == once[i], (i, list(v.domain), once[i])
    C._fazla_mesaiyi_serbest_birak(k, eski)
    assert [list(v.domain) for v in proto.variables] == once


def test_fazla_mesai_degiskeni_YOKSA_secenek_sessizce_gecer():
    """Yari zamanlida fazla mesai degiskeni yoktur (K-57): sabitlenecek sey
    yok, deneme yapilmaz, cikti None kalir."""
    g = _sahne(gun=5, tip="yari_zamanli")
    k = Model(g).kur()
    assert not _fm(k)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["iki_asama"] is True      # birinci asama KOSTU
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"] is None
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])


def test_CALISAN_profilinde_secenek_ISLEMSIZ_alanlar_zaten_sifir():
    """CALISAN'da fazla mesai tavani 0'dir: degiskenlerin alani ZATEN [0,0].
    Deneme ile birinci asamanin aramasi ayni modeldir -- "sabitlendi",
    "serbest birakildi" denmez, ikinci arama yapilmaz, cikti None kalir."""
    g = _sahne(gun=5)
    g["profil"] = "CALISAN"
    k = Model(g).kur()
    assert len(_fm(k)) == 6 and all(a == [0, 0] for a in _alanlar(k, _fm(k)))
    assert C._fazla_mesaiyi_sifirla(k) == []
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu" and c["cozum_istatistikleri"]["iki_asama"] is True
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"] is None
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])


def test_kanit_molalar_SERBESTKEN_bulunduysa_not_MOLALAR_SABITKEN_demez():
    """`ilk_asama_sabit_mola: False` (olcum anahtari) ile birinci asama
    molalari sabitlemez: "yok" kaniti tam modelindir, not ve cikti oyle der."""
    g = _sahne(gun=6)
    c = C.coz(g, dict(AYAR, ilk_asama_sabit_mola=False))
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["kanitlandi_yok"] is True and b["molalar_sabit"] is False, b
    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (kanitlandi)" in notlar[0], notlar
    assert "molalar sabitken" not in notlar[0], notlar


# ----------------------------------------------------------------------
# 3b. O-16'nin ayni sinifi: fazla mesaisiz kosunun siniri KISITLI modelindir
# ----------------------------------------------------------------------

def test_fazla_mesaisiz_ORTAK_arama_da_KISITLIDIR_kuresel_sinir_YAZILMAZ():
    """Deneme plan bulduysa fazla mesai degiskenleri ana asamada da 0'dadir.
    Ana asama ortak arama olsa bile (`mola_adimi: False`, olcum) cozdugu
    model TAM MODEL DEGILDIR: siniri "fazla mesaisiz planlarin en iyisi"ni
    kanitlar. Kuresel alanlara yazilmaz (O-16)."""
    g = _sahne(gun=5)
    c = C.coz(g, dict(AYAR, mola_adimi=False))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["bulundu"] is True
    assert ist["atamalar_sabit"] is False
    assert ist["alt_sinir"] is None, ist["alt_sinir"]
    assert ist["mola_adimi_alt_sinir"] is None
    assert ist["fazla_mesaisiz_alt_sinir"] is not None
    assert ist["fazla_mesaisiz_alt_sinir"] <= ist["amac_degeri"]
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is None, c["metrikler"]
    assert ist["durma_sebebi"] in ("fazla_mesaisiz_optimum",
                                   "fazla_mesaisiz_hedef_bosluk"), ist["durma_sebebi"]


def test_deneme_BASARISIZSA_ortak_arama_TAM_modeldir_kuresel_sinir_yazilir():
    """Deneme basarisizsa alanlar geri acilmistir: ortak arama tam modeli
    cozer, siniri kureseldir ve yazilir (kanit varken susmak da yanlis)."""
    g = _sahne(gun=6)
    c = C.coz(g, dict(AYAR, mola_adimi=False))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["bulundu"] is False
    assert ist["alt_sinir"] is not None and ist["alt_sinir"] <= ist["amac_degeri"]
    assert ist["fazla_mesaisiz_alt_sinir"] is None and ist["mola_adimi_alt_sinir"] is None
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is not None
    assert not str(ist["durma_sebebi"]).startswith(("fazla_mesaisiz_", "mola_adimi_")), ist["durma_sebebi"]


# ----------------------------------------------------------------------
# 4. KAPSAM: yalniz iki asamali yol
# ----------------------------------------------------------------------

def test_iki_asama_YOKSA_secenek_uygulanmaz_alanlara_dokunulmaz(monkeypatch):
    """Esigin altindaki modelde birinci asama yoktur: deneme yapilmaz,
    fazla mesai alanlari oldugu gibi kalir, cikti None'dir. (Kucuk modelde
    cozucu zaten kanitli optimuma ulasiyor; secenek buyuk modelin arama
    artigi icin.)"""
    g = _sahne(gun=6)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    ayar = dict(AYAR)
    del ayar["iki_asama_esigi"]                      # varsayilan esik: 50.000
    c = C.coz(g, ayar, kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is False
    assert ist["fazla_mesai_once_sifir"] is None
    assert gorulen["fm"] == once
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])
