# -*- coding: utf-8 -*-
"""
ONCE FAZLA MESAISIZ -- K-61: URUNUN VARSAYILANI; HAKEM AGIRLIKLARDIR
(6 Ekim karar; 7 Ekim duzeltme -- O-18)

NE BULUNDU (tam olcek, 500 kisi, %95 doluluk, 900 sn, ucer kosu, Mustafa'nin
makinesi; kalite-olcumu-95-profiller-900.json)
  CALISAN profili (fazla mesai tavani 0 -> SERT sinir) uc kosuda da 0 saat
  fazla mesaiyle plan buldu. O planlar DENGELI'nin KENDI agirliklariyla
  26.589-26.703 puan ediyor; DENGELI'nin kendi buldugu planlar
  105.742-148.431. Yani fazla mesai verinin zorladigi bir sey degil,
  aramanin ARTIGI: yumusak cezayla sifira itilemiyor, sert sinirla 13-33
  saniyede sifirlaniyor.

KARAR (K-61, Mustafa, 6 Ekim 23:44): "Evet" -- ve ilkesi:
  "...elimizdeki tum kriterleri karsilayan en iyi plan fazla mesaisiz olmali.
   Ama matematiksel olarak kurdugumuz modelde agirliklar baz alindiginda
   ornegin 3 saat fazla mesai iceren en optimum plan var ve fazla mesaisiz
   plandan oldukca daha optimum bir plan ise en optimum olani secmeliyiz."

⚠ O-18 (7 Ekim): 6 Ekim gecesi yazilan hal bu ilkeyi CIGNIYORDU. Fazla
  mesaisiz plan bulununca fazla mesai BUTUN asamalarda 0'da tutuluyordu
  ("sert kesim") ve bunu bir "agirlik kosulu" koruyordu. Bagimsiz inceleme
  (iki ajan) urun agirliklarinda karsi ornekler buldu: 15 dakikalik bir fazla
  mesai adimi bir haftalik duzenin kilidini acabiliyor (asagida bolum 5:
  kanitli optimum 750 iken sert kesim 2.256; 12 kiside 9.000'e karsi 12.000
  -- Mustafa'nin 3 saatlik ornegi). Duzeltme: fazla mesaisiz plan yalniz
  BASLANGIC NOKTASIDIR; bulununca alanlar geri acilir, iyilestirme tam
  agirlikli amacla o plandan baslar, karari agirliklar verir. Sert kesim
  OLCUM secenegi olarak kaldi (`fazla_mesai_sifirda_tut`), urun yolunda yok.

BU DOSYA NEYI SINAR
  `fazla_mesai_once_sifir` (varsayilan ACIK; False = 6 Ekim oncesinin yolu):
    * birinci asama gecerli plani fazla mesai degiskenleri [0,0]'a
      sabitken arar;
    * BULURSA o plan ipucudur, alanlar AYNEN geri acilir (bolum 1),
      iyilestirme ve mola adimi tam modelde kosar -- fazla mesaili daha iyi
      plan varsa agirliklar onu secer (bolum 5);
    * BULAMAZSA (kanit ya da sure) alanlar yine geri acilir, fazla mesai
      serbestken yeniden aranir, not duser -- zorunlu fazla mesai yolu
      KAPANMAZ (K-38) (bolum 2);
    * yalniz IKI ASAMALI yolda uygulanir (bolum 4);
    * `fazla_mesai_sifirda_tut: True` (OLCUM) 6 Ekim'in sert kesimidir:
      bulununca fazla mesai 0'da kalir, cozulen model tam model DEGILDIR,
      kuresel sinir yazilmaz (bolum 3b); urun yolunda KAPALI.
    * `fazla_mesaisiz_deneme` (OLCUM, T-60 bulgu 25, 7 Ekim; varsayilan 1):
      fazla mesaisiz aramanin payi N denemeye bolunur, her deneme farkli
      CP-SAT tohumuyla (1 = kutuphanenin varsayilani = bugunku arama), ilk
      bulunan alinir, INFEASIBLE kanittir (kalan denemeler yapilmaz);
      ciktida `denemeler` (bolum 7). NEDEN: 500 kisilik gece kosusunda bu
      arama 18 kosunun 1'inde 120 sn'de bulamadi ve plan 30 saat fazla
      mesaiyle dondu; kuyruk olcumu (35 deneme) medyan 7,5 sn, en uzun 62 sn.
  Tam olcekte ne kazandirdigi burada SINANMAZ -- o bir olcumdur
  (08-motor-testleri/gercekci-veri-seti/kalite-olc.py; kayit: T-60 bulgu
  21 sert kesim; duzeltilmis yolun 500 kisilik olcumu bekleniyor).

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
# URUNUN HALI: secenek ayarda YAZMAZ -- varsayilandan gelir (K-61).
AYAR_URUN = {k: v for k, v in AYAR.items() if k != "fazla_mesai_once_sifir"}
# OLCUM: 6 Ekim'in sert kesimi (bulununca fazla mesai 0'da KALIR).
AYAR_SERT = dict(AYAR, fazla_mesai_sifirda_tut=True)


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
# 0. Varsayilan ACIK (K-61); False verilirse 6 Ekim oncesinin yolu
# ----------------------------------------------------------------------

def test_varsayilan_ACIK_urun_once_fazla_mesaisiz_arar_K61(monkeypatch):
    """Secenek ayarda YAZMIYOR: urunun kendi hali. Fazla mesaisiz plan var
    (5 gun x 8 saat = 40): bulunur; sert kesim KAPALI (alanlar geri acilir)."""
    assert C.VARSAYILAN["fazla_mesai_once_sifir"] is True
    assert C.VARSAYILAN["fazla_mesai_sifirda_tut"] is False
    assert "fazla_mesai_once_sifir" not in AYAR_URUN
    g = _sahne(gun=5)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR_URUN), kuruldu=k)
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b is not None and b["bulundu"] is True and b["sifirda_tutuldu"] is False, b
    assert gorulen["fm"] == once, (gorulen["fm"], once)       # tam model
    assert c["metrikler"]["fazla_mesai_saat"] == 0, c["metrikler"]


def test_KAPALI_verilirse_onceki_yol_fazla_mesai_alanlarina_DOKUNULMAZ(monkeypatch):
    """`fazla_mesai_once_sifir: False` 6 Ekim oncesinin davranisidir (olcum
    ve kiyas icin): deneme yapilmaz, alanlar oldugu gibi, cikti None, not yok."""
    g = _sahne(gun=6)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    assert len(once) == 6 and all(a == [0, 600] for a in once), once      # tavan 10 saat
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR, fazla_mesai_once_sifir=False), kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"] is None
    assert gorulen["fm"] == once
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])


# ----------------------------------------------------------------------
# 1. Fazla mesaisiz plan VARSA: bulunur, IPUCU olur, alanlar GERI ACILIR
# ----------------------------------------------------------------------

def test_fazla_mesaisiz_plan_VARSA_bulunur_ipucu_olur_alanlar_GERI_ACILIR(monkeypatch):
    """Urun yolu (7 Ekim): bulunan fazla mesaisiz plan baslangic noktasidir;
    iyilestirme ve ana asama TAM modelde kosar (fazla mesai alanlari acik).
    Bu sahnede fazla mesai zaten kazandirmaz: sonuc 0 saat."""
    g = _sahne(gun=5)
    k = Model(g).kur()
    once = _alanlar(k, _fm(k))
    assert all(a == [0, 600] for a in once), once
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is True
    b = ist["fazla_mesai_once_sifir"]
    assert b["bulundu"] is True and b["degisken"] == 6 and b["kanitlandi_yok"] is False, b
    assert b["sifirda_tutuldu"] is False, b
    assert c["metrikler"]["fazla_mesai_saat"] == 0, c["metrikler"]
    # ana asamada fazla mesai alanlari GERI ACILMIS (tam model)
    assert gorulen["fm"] == once, (gorulen["fm"], once)
    # oteki cezalara zaten dokunulmaz: hedef cezasi serbest (kadro 6, hedef 7)
    assert gorulen["oteki"] and all(a[-1] > 0 for a in gorulen["oteki"]), gorulen["oteki"][:3]
    assert ist["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] > 0
    # ipucu fazla mesaisiz plandir: iyilestirme ondan basladi (amacsiz plan
    # fazla mesaisiz; iyilestirme onu kotulestiremez)
    iy = ist["ilk_asama_iyilestirme"]
    assert iy["plan_bulundu"] is True and iy["iyilesmis_amac"] <= iy["amacsiz_amac"], iy
    assert iy["amac_dagilimi"]["FAZLA_MESAI"]["deger"] == 0, iy["amac_dagilimi"]
    assert not any("fazla mesaisiz" in n for n in c["uygulanmayan_notlar"])
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_bulunan_fazla_mesaisiz_plan_iyilestirmeye_TAM_IPUCU_olarak_gider_fm_SIFIR(monkeypatch):
    """O-18'in kalbi: alanlar geri acildiktan sonra iyilestirmeye giden model
    fazla mesaisiz plani TAM ipucu olarak tasimali (butun degiskenler, fm_*
    degerleri 0). Ipucu silinir ya da yarim yazilirsa iyilestirme sifirdan
    baslar -- kucuk sahnede ayni plani bulabilecegi icin sonuc testleri bunu
    GORMEZ (7 Ekim: 'ipucu silinsin' mutasyonu 27 testten sag cikmisti).
    Burada iyilestirme aramasina giren modelin ipucusu dogrudan okunur."""
    g = _sahne(gun=5)
    k = Model(g).kur()
    fm_indeks = [v.Index() for v in _fm(k)]
    gorulen = {}
    asil = C._iyilestirme_coz

    def bak(model, saniye, isci):
        proto = model.Proto()
        gorulen["ipucu"] = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
        gorulen["degisken"] = len(proto.variables)
        gorulen["fm_alan"] = [list(proto.variables[i].domain) for i in fm_indeks]
        return asil(model, saniye, isci)
    monkeypatch.setattr(C, "_iyilestirme_coz", bak)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]["bulundu"] is True
    ipucu = gorulen["ipucu"]
    assert len(ipucu) == gorulen["degisken"] > 0, (len(ipucu), gorulen["degisken"])   # TAM ipucu
    assert all(ipucu[i] == 0 for i in fm_indeks), [ipucu[i] for i in fm_indeks]   # fazla mesaisiz
    assert all(a == [0, 600] for a in gorulen["fm_alan"]), gorulen["fm_alan"]       # alanlar ACIK


def test_SERT_KESIM_olcum_secenegi_bulununca_fazla_mesai_butun_asamalarda_SIFIR(monkeypatch):
    """`fazla_mesai_sifirda_tut: True` = 6 Ekim'in olculen hali (bulgu 21):
    bulununca alanlar [0,0]'da KALIR. Olcum ve kiyas icin; urun yolu degil."""
    g = _sahne(gun=5)
    k = Model(g).kur()
    gorulen = {}
    _ana_asamayi_izle(monkeypatch, k, gorulen)
    c = C.coz(g, dict(AYAR_SERT), kuruldu=k)
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is True and b["sifirda_tutuldu"] is True, b
    assert gorulen["fm"] == [[0, 0]] * 6, gorulen["fm"]
    assert gorulen["oteki"] and all(a[-1] > 0 for a in gorulen["oteki"])
    assert c["metrikler"]["fazla_mesai_saat"] == 0


def test_SERT_KESIM_bulunamazsa_alanlar_yine_geri_acilir():
    """Sert kesim de zorunlu fazla mesai yolunu kapatmaz: plan bulunamadiysa
    `sifirda_tutuldu` False, alanlar acik, plan fazla mesaili doner."""
    g = _sahne(gun=6)
    c = C.coz(g, dict(AYAR_SERT))
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is False and b["sifirda_tutuldu"] is False, b
    assert c["metrikler"]["fazla_mesai_saat"] == 18.0, c["metrikler"]


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
    assert b["sifirda_tutuldu"] is False, b
    assert b["molalar_sabit"] is True, b            # kanit molalar sabitken aranan modelin
    # fazla mesai serbestken YENIDEN arandi ve birinci asama ipucunu verdi
    assert c["cozum_istatistikleri"]["iki_asama"] is True
    assert c["metrikler"]["fazla_mesai_saat"] > 0, c["metrikler"]
    assert gorulen["fm"] == once, (gorulen["fm"], once)
    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (molalar sabitken kanitlandi)" in notlar[0], \
        c["uygulanmayan_notlar"]
    assert "serbest birakildi" in notlar[0], notlar
    # ⚠ not "en aza indirilir" DEMEZ: agirlikli arama azaltmaya calisir,
    #   en azi oldugu kanitli degildir (kesif, 151 kisi: en az 3,5 saat
    #   zorunluyken 9,75-11,25 saat yazildi -- T-60 bulgu 22).
    assert "en aza indirilir" not in notlar[0], notlar
    assert "kanitli degildir" in notlar[0], notlar
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
    assert "denemede" not in notlar[0], notlar          # tek denemede deneme sayisi yazilmaz (bulgu 25)
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["deneme_siniri"] == 1 and len(b["denemeler"]) == 1 and b["denemeler"][0]["durum"] == "UNKNOWN", b
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

def test_URUN_yolunda_bulunsa_da_ortak_arama_TAM_modeldir_kuresel_sinir_YAZILIR():
    """Alanlar geri acildigi icin ana asama (burada ortak arama,
    `mola_adimi: False`) TAM MODELI cozer: siniri kureseldir, yazilir;
    durma sebebi on ek almaz. 6 Ekim'de burasi kisitliydi (sert kesim)."""
    g = _sahne(gun=5)
    c = C.coz(g, dict(AYAR, mola_adimi=False))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["bulundu"] is True
    assert ist["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is False
    assert ist["atamalar_sabit"] is False
    assert ist["alt_sinir"] is not None and ist["alt_sinir"] <= ist["amac_degeri"], ist
    assert ist["fazla_mesaisiz_alt_sinir"] is None and ist["mola_adimi_alt_sinir"] is None
    assert c["metrikler"]["optimuma_uzaklik_yuzde"] is not None
    assert ist["durma_sebebi"] in ("optimum", "hedef_bosluk"), ist["durma_sebebi"]


def test_SERT_KESIMDE_ortak_arama_KISITLIDIR_kuresel_sinir_YAZILMAZ():
    """Sert kesimde (olcum) fazla mesai degiskenleri ana asamada da 0'dadir.
    Cozulen model TAM MODEL DEGILDIR: siniri "fazla mesaisiz planlarin en
    iyisi"ni kanitlar. Kuresel alanlara yazilmaz (O-16)."""
    g = _sahne(gun=5)
    c = C.coz(g, dict(AYAR_SERT, mola_adimi=False))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is True
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


# ----------------------------------------------------------------------
# 5. HAKEM AGIRLIKLARDIR (K-61): fazla mesaisiz plan bulunsa bile
#    agirliklara gore daha iyi fazla mesaili plan varsa O secilir
# ----------------------------------------------------------------------

def _ornek_sahne(agirliklar=None):
    """MUSTAFA'NIN ORNEGI (6 Ekim): "...3 saat fazla mesai iceren en optimum
    plan var ve fazla mesaisiz plandan oldukca daha optimum bir plan ise en
    optimum olani secmeliyiz."

    Alti kisi (45 saat sozlesme), tek sablon (8 net saat), alti gun talep:
    her saat asgari 5 ve hedef 5; yalniz gun 2'de hedef 6.

      fazla mesaisiz plan : herkes 5 gun (40 saat), her gun 5 kisi; gun 2'de
                            hedefin 1 kisi altinda, 8 saat -> 8 kisi-saat eksik
      3 saat fazla mesaili : biri 6 gun calisir (48 saat = 3 saat fazla
                            mesai), gun 2'de 6 kisi -> hedef eksigi 0

      urun agirliklari (hedef 9, fazla mesai dakikasi 50):
          fazla mesaisiz 8 x 9 = 72      fazla mesaili 180 x 50 = 9.000
          -> fazla mesaisiz KAZANIR (K-30: hedef icin fazla mesai yapilmaz)
      hedef agirligi 2.000'e cikarilirsa:
          fazla mesaisiz 8 x 2.000 = 16.000      fazla mesaili 9.000
          -> 3 saat fazla mesaili plan KAZANIR; motor ONU secmeli
    """
    g = _sahne(gun=6)
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 5,
                   "hedef": 6 if d == 2 else 5}
                  for d in range(6) for s in range(9, 17)]
    if agirliklar:
        g["agirliklar"] = dict(agirliklar)
    return g


def test_MUSTAFANIN_ORNEGI_fazla_mesaisiz_plan_BULUNSA_DA_agirliklar_fazla_mesaili_plani_SECER():
    """Hedef agirligi 2.000: 3 saat fazla mesaili plan 9.000, fazla mesaisiz
    plan 16.000 puan. Urunun hali: birinci asama fazla mesaisiz plani BULUR
    (`bulundu: True`) ama bu yalniz baslangic noktasidir; sonuc 3 saat
    fazla mesaili plandir. 6 Ekim'in sert kesimi burada 16.000 donduruyordu."""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    c = C.coz(g, dict(AYAR_URUN))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    b = ist["fazla_mesai_once_sifir"]
    assert b["bulundu"] is True and b["sifirda_tutuldu"] is False, b
    assert c["metrikler"]["fazla_mesai_saat"] == 3.0, c["metrikler"]
    assert ist["amac_degeri"] == 9000, ist["amac_degeri"]
    assert ist["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] == 0
    assert ist["amac_dagilimi"]["FAZLA_MESAI"]["deger"] == 180
    r = dogrulayici.degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]

    sert = C.coz(_ornek_sahne({"HEDEF_KAPSAMA": 2000}), dict(AYAR_SERT))
    si = sert["cozum_istatistikleri"]
    assert si["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is True
    assert sert["metrikler"]["fazla_mesai_saat"] == 0
    assert si["amac_degeri"] == 16000, si["amac_degeri"]       # ilkeyi cigneyen hal


def test_mola_adimina_giden_ipucu_TAM_ve_fazla_mesai_degerleri_iyilestirmenin_planindan(monkeypatch):
    """Inceleme A (7 Ekim 04:45): mola adimina giden ipucu denetlenmiyordu --
    `_tam_ipucu_yaz` fm degerlerini hep 0 yazsa ya da iyilestirmeden sonra fm
    ipuclari silinse (yarim ipucu; T-60 1 Ekim'in tuzagi: onarim 57-101 sn)
    kucuk modelde hicbir test gormuyordu. Burada ana aramaya (mola adimi)
    giren modelin ipucusu dogrudan okunur: TAM (butun degiskenler) ve fm
    ipuclari iyilestirmenin planini tasiyor -- Mustafa'nin orneginde 3 saat =
    180 dk, fazla mesaisiz ipucunun 0'i degil."""
    g = _ornek_sahne({"HEDEF_KAPSAMA": 2000})
    k = Model(g).kur()
    fm_indeks = [v.Index() for v in _fm(k)]
    gorulen = {}
    asil = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        proto = model.Proto()
        gorulen["ipucu"] = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
        gorulen["degisken"] = len(proto.variables)
        return asil(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    c = C.coz(g, dict(AYAR_URUN), kuruldu=k)
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["bulundu"] is True
    iy = ist["ilk_asama_iyilestirme"]
    assert iy["plan_bulundu"] is True and iy["amac_dagilimi"]["FAZLA_MESAI"]["deger"] == 180, iy
    ipucu = gorulen["ipucu"]
    assert len(ipucu) == gorulen["degisken"] > 0, (len(ipucu), gorulen["degisken"])   # TAM
    assert all(i in ipucu for i in fm_indeks), "fm ipuclari eksik (yarim ipucu)"
    assert sum(ipucu[i] for i in fm_indeks) == 180, [ipucu[i] for i in fm_indeks]    # iyilestirmenin plani
    assert ist["amac_degeri"] == 9000 and c["metrikler"]["fazla_mesai_saat"] == 3.0


def test_iyilestirme_ipucudan_KOTU_plan_dondururse_ipucu_KORUNUR(monkeypatch):
    """Inceleme B (7 Ekim 04:45): "ipucundan kotu plan donemez" bir garanti
    degildi -- `_ilk_asamada_iyilestir` kotu plani ipucunun ustune
    yaziyordu. Simdi: iyilestirmenin plani amacsiz (fazla mesaisiz) plandan
    kotuyse ipucu korunur, cikti `ipucu_korundu: True` der. Kotu plan,
    gercek cozucunun amac degerini sisirerek taklit edilir."""
    g = _sahne(gun=5)
    k = Model(g).kur()
    asil = C._iyilestirme_coz

    class Sisik:
        def __init__(self, c):
            self._c = c
        def ObjectiveValue(self):
            return self._c.ObjectiveValue() + 1_000_000
        def __getattr__(self, ad):
            return getattr(self._c, ad)

    def kotu(model, saniye, isci):
        durum, c2, sayac = asil(model, saniye, isci)
        return durum, Sisik(c2), sayac
    monkeypatch.setattr(C, "_iyilestirme_coz", kotu)
    gorulen = {}
    asil_ana = C._durgunluk_bekcisiyle_coz

    def bak(cozucu, model, geri, ayar):
        proto = model.Proto()
        gorulen["ipucu"] = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
        return asil_ana(cozucu, model, geri, ayar)
    monkeypatch.setattr(C, "_durgunluk_bekcisiyle_coz", bak)
    c = C.coz(g, dict(AYAR), kuruldu=k)
    assert c["durum"] == "cozuldu"
    iy = c["cozum_istatistikleri"]["ilk_asama_iyilestirme"]
    assert iy["plan_bulundu"] is True and iy["iyilesmis_amac"] > iy["amacsiz_amac"], iy
    assert iy["ipucu_korundu"] is True, iy
    # korunan ipucu amacsiz (fazla mesaisiz) plandir: fm ipuclari 0, TAM
    fm_indeks = [v.Index() for v in _fm(k)]
    assert all(gorulen["ipucu"].get(i) == 0 for i in fm_indeks), [gorulen["ipucu"].get(i) for i in fm_indeks]
    assert len(gorulen["ipucu"]) == len(k.m.Proto().variables)


def test_iyilestirme_ipucudan_iyi_plan_dondururse_ipucu_YENILENIR_korundu_False():
    g = _sahne(gun=5)
    c = C.coz(g, dict(AYAR))
    iy = c["cozum_istatistikleri"]["ilk_asama_iyilestirme"]
    assert iy["plan_bulundu"] is True and iy["iyilesmis_amac"] <= iy["amacsiz_amac"]
    assert iy["ipucu_korundu"] is False


def test_AYNI_ornekte_URUN_agirliklariyla_fazla_mesai_YAPILMAZ_K30():
    """Ayni sahne, urunun kendi agirliklari: 8 kisi-saat hedef eksigi 72 puan,
    3 saat fazla mesai 9.000 puan. Hedef icin fazla mesai yapilmaz (K-30'un
    ilk satiri) -- bunu agirliklar sagliyor, sert bir kesim degil."""
    g = _ornek_sahne()
    c = C.coz(g, dict(AYAR_URUN))
    assert c["durum"] == "cozuldu"
    ist = c["cozum_istatistikleri"]
    assert ist["fazla_mesai_once_sifir"]["bulundu"] is True
    assert c["metrikler"]["fazla_mesai_saat"] == 0
    assert ist["amac_degeri"] == 72, ist["amac_degeri"]
    assert ist["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] == 8


# ---- O-18'in karsi ornekleri: URUN AGIRLIKLARINDA 15 dakikalik fazla mesai
# ---- adimi bir haftalik duzenin kilidini aciyor. Bagimsiz incelemenin
# ---- (7 Ekim, iki ajan) sahneleri; sayilar oradan.

def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True}
    if p:
        k["parametreler"] = p
    return k


def _sablon(tid, bas, bit, gunler=None):
    """60 dk ucretsiz yemek: net = brut - 1 saat."""
    t = {"id": tid, "ekip": "E", "bas": bas, "bit": bit, "mola_dk": 60,
         "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]}
    if gunler is not None:
        t["gunler"] = list(gunler)
    return t


def _kurallar(saat_dengesi=None):
    k = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
         _kural("HAFTA_TATILI"), _kural("GUNLUK_AZAMI", azami_saat=11),
         _kural("HAFTALIK_AZAMI", azami_saat=45),
         _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10), _kural("MOLA_HAKKI")]
    if saat_dengesi:
        k.append(_kural("SAAT_DENGESI", saat_dengesi, tolerans_saat=0))
    return k


def _kisi(cid, ekipler=("E",)):
    return {"id": cid, "ekipler": list(ekipler), "izinler": [], "uygunluk": [],
            "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45}}


def _tek_kisi(profil, saat_dengesi):
    """Bir kisi. A = 7,5 saat net (Pzt-Cum), B = 7,75 saat net (Cmt):
    5A + B = 45 saat 15 dakika -> 15 dk fazla mesai (750 puan) ile sozlesme
    dolar ve talep tam kapanir. Fazla mesaisiz: bir A gunu dusulur -> 7,25
    saat sozlesme altinda (SAAT_DENGESI yumusak: 435 dk x 5 = 2.175) + 9
    hucre hedef eksigi (81) = 2.256. SAAT_DENGESI SERT ise tek fazla mesaisiz
    dolum 15:00-01:00 (9 saat net) sablonudur: talebin disinda, 44 hucre x 20
    = 880."""
    sablonlar = [_sablon("A", 8, 16.5, range(5)), _sablon("B", 8, 16.75, [5])]
    if saat_dengesi == "SERT":
        sablonlar.append(_sablon("E", 15, 25))
    return {"profil": profil, "calisanlar": [_kisi("P")], "kilitler": [], "donmus_gunler": [],
            "vardiya_sablonlari": sablonlar,
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 0, "hedef": 1}
                      for d in range(6) for s in range(8, 17)],
            "kurallar": _kurallar(saat_dengesi)}


def _aksam(profil, kisi_sayisi=1, ekipler=("E",)):
    """Talep 13-23 arasi, hedef = kadro. ERKEN (04:00-12:30, 7,5 saat net x 6
    = 45) talebin DISINDA; P9 (13-23, 9 saat) x 4 + PL (13-23:15, 9,25) = 45
    saat 15 dk -> kisi basi 15 dk fazla mesai ile talep tam kapanir.
    SAAT_DENGESI SERT: fazla mesaisiz tek dolum 6 x ERKEN. 12 kisi -> tam
    3 SAAT fazla mesai (Mustafa'nin ornegindeki miktar)."""
    return {"profil": profil, "kilitler": [], "donmus_gunler": [],
            "calisanlar": [_kisi("P%d" % i, ekipler) for i in range(1, kisi_sayisi + 1)],
            "vardiya_sablonlari": [_sablon("ERKEN", 4, 12.5, range(6)),
                                   _sablon("P9", 13, 23, [0, 1, 2, 3]),
                                   _sablon("PL", 13, 23.25, [4])],
            "talep": [{"ekip": e, "gun": d, "saat": s, "asgari": 0, "hedef": kisi_sayisi}
                      for e in ekipler for d in range(5) for s in range(13, 23)],
            "kurallar": _kurallar("SERT")}


TAM_MODEL = {"azami_saniye": 40, "isci_sayisi": 2, "hedef_bosluk": 0.0,
             "fazla_mesai_once_sifir": False}       # esik varsayilan: tek model, ortak arama
AYAR_40 = dict(AYAR_URUN, azami_saniye=40)
SERT_40 = dict(AYAR_SERT, azami_saniye=40)

KARSI_ORNEKLER = [
    # ad, sahne, kanitli optimum, optimumun fazla mesaisi (saat), sert kesimin puani
    ("S1 tek kisi DENGELI, SAAT_DENGESI yumusak", lambda: _tek_kisi("DENGELI", "YUMUSAK"), 750, 0.25, 2256),
    ("F2 tek kisi KAPSAMA, SAAT_DENGESI sert", lambda: _tek_kisi("KAPSAMA", "SERT"), 750, 0.25, 880),
    ("S3b 12 kisi KAPSAMA: 3 saat fazla mesai", lambda: _aksam("KAPSAMA", 12), 9000, 3.0, 12000),
    ("S3c iki ekibe uye tek kisi DENGELI (K-50)", lambda: _aksam("DENGELI", 1, ("E", "F")), 750, 0.25, 900),
]


def _kanitli_optimum(g):
    tam = C.coz(g, dict(TAM_MODEL))
    ti = tam["cozum_istatistikleri"]
    assert tam["durum"] == "cozuldu" and ti["iki_asama"] is False
    assert ti["durma_sebebi"] == "optimum" and ti["alt_sinir"] == ti["amac_degeri"], ti
    return tam


def test_O18_urun_agirliklarinda_15_dakikalik_fazla_mesai_adimi_KAZANIR_urun_yolu_optimumu_verir():
    """Her sahnede: tam model (tek arama) optimumu KANITLAR ve optimum fazla
    mesaili; urunun asamali yolu (once fazla mesaisiz, sonra alanlar acik)
    AYNI puani verir. 6 Ekim'in sert kesimi daha kotu plani donduruyordu."""
    for ad, sahne, beklenen, fm_saat, _ in KARSI_ORNEKLER:
        tam = _kanitli_optimum(sahne())
        assert tam["cozum_istatistikleri"]["amac_degeri"] == beklenen, (ad, tam["cozum_istatistikleri"]["amac_degeri"])
        assert tam["metrikler"]["fazla_mesai_saat"] == fm_saat, (ad, tam["metrikler"])
        g = sahne()
        urun = C.coz(g, dict(AYAR_40))
        ui = urun["cozum_istatistikleri"]
        assert urun["durum"] == "cozuldu" and ui["iki_asama"] is True, ad
        assert ui["fazla_mesai_once_sifir"]["bulundu"] is True, (ad, ui["fazla_mesai_once_sifir"])
        assert ui["amac_degeri"] == beklenen, (ad, ui["amac_degeri"], beklenen)
        assert urun["metrikler"]["fazla_mesai_saat"] == fm_saat, (ad, urun["metrikler"])
        r = dogrulayici.degerlendir(g, urun["atamalar"])
        assert r["yayin_kapisi"]["yayinlanabilir"] is True, (ad, r["ihlaller"])


def test_O18_SERT_KESIM_ayni_sahnelerde_daha_KOTU_plani_dondurur():
    """Sert kesim (olcum secenegi) fazla mesaisiz plani bulup orada kalir:
    puan kanitli optimumun ustunde. Bu, 6 Ekim gecesinin yanlisini
    belgeler -- 'bu kurda olusmaz' denmisti, urun agirliklarinda olusuyor."""
    for ad, sahne, optimum, _, sert_puan in KARSI_ORNEKLER:
        sert = C.coz(sahne(), dict(SERT_40))
        si = sert["cozum_istatistikleri"]
        assert sert["durum"] == "cozuldu" and si["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is True, ad
        assert sert["metrikler"]["fazla_mesai_saat"] == 0, (ad, sert["metrikler"])
        assert si["amac_degeri"] == sert_puan > optimum, (ad, si["amac_degeri"], sert_puan, optimum)


def test_K61_urun_agirliklarinda_asamali_yolun_plani_KANITLI_optimumla_AYNI_puanda():
    """Fazla mesainin gerekmedigi ornekte de (72), zorunlu oldugu sahnede de
    (18 saat) asamali urun yolu tam modelin kanitli optimumuyla ayni puani
    verir."""
    for sahne, beklenen_fm in ((_ornek_sahne, 0.0), (lambda: _sahne(gun=6), 18.0)):
        tam = _kanitli_optimum(sahne())
        ti = tam["cozum_istatistikleri"]
        urun = C.coz(sahne(), dict(AYAR_URUN))
        ui = urun["cozum_istatistikleri"]
        assert urun["durum"] == "cozuldu" and ui["iki_asama"] is True
        assert ui["amac_degeri"] == ti["amac_degeri"], (ui["amac_degeri"], ti["amac_degeri"])
        assert urun["metrikler"]["fazla_mesai_saat"] == tam["metrikler"]["fazla_mesai_saat"] == beklenen_fm


# ----------------------------------------------------------------------
# 6. Iyilestirme egrisi ve amac degerinin yuvarlanmasi (7 Ekim, inceleme)
# ----------------------------------------------------------------------

def test_iyilestirmenin_EGRISI_ciktiya_yazilir():
    """Iyilestirme butcenin %80'ini alir; hangi saniyede ne kadar duzeldigi
    olmadan sure paylari olculemez. Egri: (sn, amac, alt sinir); son nokta
    iyilesmis amactir."""
    c = C.coz(_ornek_sahne(), dict(AYAR_URUN))
    iy = c["cozum_istatistikleri"]["ilk_asama_iyilestirme"]
    assert iy["plan_bulundu"] is True
    e = iy["iyilesme"]
    assert e is not None and e["cozum"] >= 1 and len(e["egri"]) == min(e["cozum"], 25), e
    assert e["son_amac"] == iy["iyilesmis_amac"], (e, iy)
    assert e["ilk_amac"] >= e["son_amac"]
    assert all(len(nokta) == 3 for nokta in e["egri"])


def test_amac_degeri_YUVARLANIR_kirpilmaz():
    """CP-SAT amac degerini ondalikli dondurebilir (65154.99999...);
    `int()` kirpinca 65154 yaziliyordu, alt sinir 65155 -- plan 'optimumun
    altinda' gorunuyordu (inceleme, 7 Ekim)."""
    class Sahte:
        def ObjectiveValue(self):
            return 65154.999999
    assert C._amac_degeri(Sahte(), cp_model.OPTIMAL) == 65155
    assert C._amac_degeri(Sahte(), cp_model.UNKNOWN) is None


# ----------------------------------------------------------------------
# 7. YENIDEN BASLATMA -- T-60 bulgu 25 (7 Ekim): `fazla_mesaisiz_deneme`
#    Varsayilan 1 = tek deneme (bugunku arama). Olcumde 3: pay uce bolunur,
#    her deneme farkli tohum, ilk bulunan alinir; INFEASIBLE kanittir.
# ----------------------------------------------------------------------

def _kaydeden_cozucu(monkeypatch, ilk_unknown=0, bekle=0.0):
    """CpSolver'in her Solve cagrisinda (sure, tohum) kaydeder; ilk
    `ilk_unknown` cagri aramadan UNKNOWN doner (`bekle` sn bekleyerek)."""
    cagri = []
    asil = C.cp_model.CpSolver

    class Kaydet(asil):
        def Solve(self, model, *a, **kw):
            cagri.append((self.parameters.max_time_in_seconds, self.parameters.random_seed))
            if len(cagri) <= ilk_unknown:
                if bekle:
                    time.sleep(bekle)
                return cp_model.UNKNOWN
            return asil.Solve(self, model, *a, **kw)

    monkeypatch.setattr(C.cp_model, "CpSolver", Kaydet)
    return cagri


def test_VARSAYILAN_tek_deneme_payin_tamami_TOHUM_1_kutuphanenin_varsayilani(monkeypatch):
    """Varsayilan 1: davranis 7 Ekim sabahiyla ayni -- tek arama, sure = pay,
    tohum 1 (CP-SAT'in varsayilani; motor bugune kadar hic yazmadi, yani 1
    ile aradi). Ciktida `denemeler` tek denemede de yazilir (kuyruk urun
    kosularinda gorunur kalsin)."""
    assert C.VARSAYILAN["fazla_mesaisiz_deneme"] == 1
    assert cp_model.CpSolver().parameters.random_seed == 1          # kutuphanenin varsayilani
    cagri = _kaydeden_cozucu(monkeypatch)
    k = Model(_sahne(gun=5)).kur()
    assert C._ipucu_ver(k, dict(C.VARSAYILAN, **UZUN)) is True
    pay = C._ilk_asama_payi(dict(C.VARSAYILAN, **UZUN))                 # 100 x %20 = 20 sn
    assert cagri[0] == (pay, 1), cagri
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is True and b["deneme_siniri"] == 1, b
    assert len(b["denemeler"]) == 1, b["denemeler"]
    d = b["denemeler"][0]
    assert d["tohum"] == 1 and d["durum"] in ("OPTIMAL", "FEASIBLE") and d["saniye"] >= 0, d


def test_UC_deneme_pay_UCE_bolunur_tohumlar_FARKLI_ilk_bulunan_alinir(monkeypatch):
    """Ilk iki deneme aramadan UNKNOWN doner, ucuncusu gercek arama: uc cagri,
    her biri pay/3 sn, tohumlar 1-2-3; plan BULUNDU sayilir, not dusulmez,
    ipucu fazla mesaisiz plandir ve iyilestirmenin payi AYNEN kalir (bulan
    arama birinci asamanin kendisidir; basarisiz parcalar da onun icinde)."""
    cagri = _kaydeden_cozucu(monkeypatch, ilk_unknown=2)
    gorulen = {}

    def kaydet(model, saniye, isci):
        proto = model.Proto()
        gorulen["saniye"] = saniye
        gorulen["ipucu"] = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
        gorulen["degisken"] = len(proto.variables)
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", kaydet)
    k = Model(_sahne(gun=5)).kur()
    fm_indeks = [v.Index() for v in _fm(k)]
    ayar = dict(C.VARSAYILAN, **dict(UZUN, fazla_mesaisiz_deneme=3))
    assert C._ipucu_ver(k, ayar) is True
    pay = C._ilk_asama_payi(ayar)                                          # 20 sn
    assert [s for s, _ in cagri[:3]] == [pay / 3] * 3, cagri
    assert [t for _, t in cagri[:3]] == [1, 2, 3], cagri
    assert len(cagri) == 3, cagri                        # yeniden arama YOK (bulundu)
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is True and b["kanitlandi_yok"] is False and b["deneme_siniri"] == 3, b
    assert [d["tohum"] for d in b["denemeler"]] == [1, 2, 3], b["denemeler"]
    assert [d["durum"] for d in b["denemeler"]][:2] == ["UNKNOWN", "UNKNOWN"], b["denemeler"]
    assert b["denemeler"][2]["durum"] in ("OPTIMAL", "FEASIBLE"), b["denemeler"]
    assert not any("fazla mesaisiz" in n for n in k.notlar), k.notlar
    assert abs(gorulen["saniye"] - 80.0) < 1e-6, gorulen                  # pay %80 AYNEN
    assert len(gorulen["ipucu"]) == gorulen["degisken"] > 0
    assert all(gorulen["ipucu"][i] == 0 for i in fm_indeks)                # ipucu fazla mesaisiz


def test_UC_deneme_HEPSI_bulamazsa_eski_yol_not_KAC_DENEMEDE_der_sure_DUSER(monkeypatch):
    """Uc parca da UNKNOWN: alanlar geri acilir, fazla mesai serbestken
    yeniden aranir (4. cagri), not "bu surede bulunamadi (3 denemede)" der,
    uc parcanin toplam suresi iyilestirmenin payindan duser (O-12: beklenen
    deger motorun OLCTUGU sureden hesaplanir)."""
    cagri = _kaydeden_cozucu(monkeypatch, ilk_unknown=3, bekle=0.4)
    gorulen = {}

    def kaydet(model, saniye, isci):
        gorulen["saniye"] = saniye
        return cp_model.UNKNOWN, None, C._CozumSayaci()
    monkeypatch.setattr(C, "_iyilestirme_coz", kaydet)
    k = Model(_sahne(gun=5)).kur()
    ayar = dict(C.VARSAYILAN, **dict(UZUN, fazla_mesaisiz_deneme=3))
    assert C._ipucu_ver(k, ayar) is True                 # yeniden arama buldu
    assert len(cagri) == 4, cagri
    b = k.fazla_mesai_once_sifir
    assert b["bulundu"] is False and b["kanitlandi_yok"] is False, b
    assert [d["durum"] for d in b["denemeler"]] == ["UNKNOWN"] * 3, b["denemeler"]
    assert 1.0 < b["saniye"] < 30.0, b                    # ~1,2 sn (3 x 0,4)
    assert abs(sum(d["saniye"] for d in b["denemeler"]) - b["saniye"]) <= 0.05, b
    notlar = [n for n in k.notlar if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "bu surede bulunamadi (3 denemede)" in notlar[0], notlar
    assert abs(gorulen["saniye"] - (80.0 - b["saniye"])) <= 0.02, (gorulen, b)


def test_INFEASIBLE_KANITTIR_kalan_denemeler_YAPILMAZ_not_deneme_saymaz():
    """Fazla mesai zorunluyken (gun=6) ilk deneme INFEASIBLE doner: tohum bunu
    degistirmez, kalan iki deneme yapilmaz; not "yok (kanitlandi)" der,
    "(3 denemede)" demez."""
    g = _sahne(gun=6)
    c = C.coz(g, dict(AYAR, fazla_mesaisiz_deneme=3))
    assert c["durum"] == "cozuldu"
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is False and b["kanitlandi_yok"] is True and b["deneme_siniri"] == 3, b
    assert len(b["denemeler"]) == 1 and b["denemeler"][0]["durum"] == "INFEASIBLE", b["denemeler"]
    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (molalar sabitken kanitlandi)" in notlar[0], notlar
    assert "denemede" not in notlar[0], notlar


def test_parcalar_ESIT_toplam_PAYI_asmaz_taban_1_sn(monkeypatch):
    """`_fazla_mesaisiz_ara` dogrudan: pay 6 sn, 3 deneme -> 2'ser sn; pay 2
    sn, 4 deneme -> taban 1 sn (sifir/kesirli sure CP-SAT'e 'hic arama'
    demek olurdu; pay denemeden kucukse toplam payi asabilir, belgelidir)."""
    cagri = _kaydeden_cozucu(monkeypatch, ilk_unknown=10 ** 6)        # hep UNKNOWN
    k = Model(_sahne(gun=5)).kur()
    k.m.ClearObjective()
    durum, c, denemeler = C._fazla_mesaisiz_ara(k, dict(C.VARSAYILAN, fazla_mesaisiz_deneme=3), 6.0)
    assert durum == cp_model.UNKNOWN and len(denemeler) == 3
    assert [s for s, _ in cagri[-3:]] == [2.0, 2.0, 2.0], cagri
    assert [t for _, t in cagri[-3:]] == [1, 2, 3], cagri
    _, _, denemeler = C._fazla_mesaisiz_ara(k, dict(C.VARSAYILAN, fazla_mesaisiz_deneme=4), 2.0)
    assert len(denemeler) == 4 and [s for s, _ in cagri[-4:]] == [1.0] * 4, cagri
    _, _, denemeler = C._fazla_mesaisiz_ara(k, dict(C.VARSAYILAN), 6.0)        # varsayilan 1
    assert len(denemeler) == 1 and cagri[-1] == (6.0, 1), cagri
    # tek denemede 1 sn tabani YOK: pay aynen (bugunku aramayla birebir; inceleme 3 B4)
    C._fazla_mesaisiz_ara(k, dict(C.VARSAYILAN), 0.8)
    assert cagri[-1] == (0.8, 1), cagri
    C._fazla_mesaisiz_ara(k, dict(C.VARSAYILAN, fazla_mesaisiz_deneme=2), 0.8)
    assert [s for s, _ in cagri[-2:]] == [1.0, 1.0], cagri


def test_deneme_sayisi_GECERSIZSE_1_sayilir():
    """Bos, 0, eksi, sayi olmayan -> 1 (tek deneme); "3" -> 3."""
    for deger, beklenen in ((None, 1), (0, 1), (-2, 1), ("3", 3), ("x", 1), (2.9, 2), (3, 3)):
        assert C._deneme_siniri({"fazla_mesaisiz_deneme": deger}) == beklenen, (deger, beklenen)
    assert C._deneme_siniri({}) == 1


def test_URUN_yolunda_ciktida_denemeler_tek_kayit_tohum_1():
    """Urunun hali (secenek yazilmaz): tek deneme, tohum 1, plan bulundu;
    `deneme_siniri` 1. Kuyruk olcumunun karsiligi ciktida okunur."""
    c = C.coz(_sahne(gun=5), dict(AYAR_URUN))
    b = c["cozum_istatistikleri"]["fazla_mesai_once_sifir"]
    assert b["bulundu"] is True and b["deneme_siniri"] == 1, b
    assert len(b["denemeler"]) == 1 and b["denemeler"][0]["tohum"] == 1, b["denemeler"]
    assert b["denemeler"][0]["durum"] in ("OPTIMAL", "FEASIBLE")


def test_UCTAN_UCA_uc_deneme_butceyi_ASMAZ(monkeypatch):
    """`coz()` ile: azami 10 sn, 3 deneme; uc parca da suresini doldurup
    UNKNOWN doner (gercek uyku), sonra yeniden arama ve asamalar gercek.
    `ilk_asama_sn + ana_asama_butce_sn <= azami` (T-59) ve plan doner.
    Inceleme 3 (B4) olctu: azami 10/5/30'da toplam = azami."""
    cagri = []
    asil = C.cp_model.CpSolver

    class ParcayiDoldur(asil):
        def Solve(self, model, *a, **kw):
            cagri.append(self.parameters.max_time_in_seconds)
            if len(cagri) <= 3:
                time.sleep(self.parameters.max_time_in_seconds)
                return cp_model.UNKNOWN
            return asil.Solve(self, model, *a, **kw)
    monkeypatch.setattr(C.cp_model, "CpSolver", ParcayiDoldur)
    g = _sahne(gun=5)
    c = C.coz(g, dict(AYAR, azami_saniye=10, fazla_mesaisiz_deneme=3))
    assert c["durum"] == "cozuldu", c.get("durum")
    ist = c["cozum_istatistikleri"]
    b = ist["fazla_mesai_once_sifir"]
    assert b["bulundu"] is False and [d["durum"] for d in b["denemeler"]] == ["UNKNOWN"] * 3, b
    assert cagri[:3] == [1.0, 1.0, 1.0], cagri                  # pay 2 sn / 3 -> taban 1 sn
    assert 2.9 < b["saniye"] < 3.6, b
    assert ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"] <= 10.0 + 0.05, ist
    assert c["metrikler"]["fazla_mesai_saat"] == 0
