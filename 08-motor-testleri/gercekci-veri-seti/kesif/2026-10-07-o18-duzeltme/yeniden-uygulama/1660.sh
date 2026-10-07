cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/testler && python3 - <<'PYEOF'
import io
p="test_fazla_mesai_once_sifir.py"
s=io.open(p,encoding="utf-8").read()

# ---------------- header ----------------
a=s.index('# -*- coding: utf-8 -*-'); b=s.index('import importlib')
header='''# -*- coding: utf-8 -*-
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
  Tam olcekte ne kazandirdigi burada SINANMAZ -- o bir olcumdur
  (08-motor-testleri/gercekci-veri-seti/kalite-olc.py; kayit: T-60 bulgu
  21 sert kesim; duzeltilmis yolun 500 kisilik olcumu bekleniyor).

KOSTURMA
  cd C:\\\\Users\\\\PC\\\\Desktop\\\\Tshift\\\\09-motor
  py -m pytest testler/test_fazla_mesai_once_sifir.py -v
"""

'''
s=header+s[b:]

# ---------------- AYAR ----------------
old='''AYAR = {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5,
        "isci_sayisi": 2, "fazla_mesai_once_sifir": True}
# URUNUN HALI: secenek ayarda YAZMAZ -- varsayilandan gelir (K-61).
AYAR_URUN = {k: v for k, v in AYAR.items() if k != "fazla_mesai_once_sifir"}
'''
new='''AYAR = {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5,
        "isci_sayisi": 2, "fazla_mesai_once_sifir": True}
# URUNUN HALI: secenek ayarda YAZMAZ -- varsayilandan gelir (K-61).
AYAR_URUN = {k: v for k, v in AYAR.items() if k != "fazla_mesai_once_sifir"}
# OLCUM: 6 Ekim'in sert kesimi (bulununca fazla mesai 0'da KALIR).
AYAR_SERT = dict(AYAR, fazla_mesai_sifirda_tut=True)
'''
assert s.count(old)==1; s=s.replace(old,new)

# ---------------- section 0 ----------------
old=s[s.index('def test_varsayilan_ACIK_urun_once_fazla_mesaisiz_arar_K61(monkeypatch):'):s.index('def test_KAPALI_verilirse_onceki_yol_fazla_mesai_alanlarina_DOKUNULMAZ(monkeypatch):')]
new='''def test_varsayilan_ACIK_urun_once_fazla_mesaisiz_arar_K61(monkeypatch):
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


'''
s=s.replace(old,new)

# ---------------- section 1 ----------------
old=s[s.index('# ----------------------------------------------------------------------\n# 1. Fazla mesaisiz plan VARSA'):s.index('# ----------------------------------------------------------------------\n# 2. Fazla mesai ZORUNLUYSA')]
new='''# ----------------------------------------------------------------------
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


'''
s=s.replace(old,new)

# ---------------- section 2: remove the stale 'uygulandi' asserts ----------------
old='''    assert b["bulundu"] is False and b["kanitlandi_yok"] is True, b
    assert b["uygulandi"] is True, b                # denendi; "yok" denemenin SONUCU
    assert b["molalar_sabit"] is True, b            # kanit molalar sabitken aranan modelin
'''
new='''    assert b["bulundu"] is False and b["kanitlandi_yok"] is True, b
    assert b["sifirda_tutuldu"] is False, b
    assert b["molalar_sabit"] is True, b            # kanit molalar sabitken aranan modelin
'''
assert s.count(old)==1; s=s.replace(old,new)
old='''    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (molalar sabitken kanitlandi)" in notlar[0], \\
        c["uygulanmayan_notlar"]
    assert "serbest birakildi" in notlar[0], notlar
'''
new='''    notlar = [n for n in c["uygulanmayan_notlar"] if "fazla mesaisiz" in n]
    assert len(notlar) == 1 and "yok (molalar sabitken kanitlandi)" in notlar[0], \\
        c["uygulanmayan_notlar"]
    assert "serbest birakildi" in notlar[0], notlar
    # ⚠ not "en aza indirilir" DEMEZ: agirlikli arama azaltmaya calisir,
    #   en azi oldugu kanitli degildir (kesif, 151 kisi: en az 3,5 saat
    #   zorunluyken 9,75-11,25 saat yazildi -- T-60 bulgu 22).
    assert "en aza indirilir" not in notlar[0], notlar
    assert "kanitli degildir" in notlar[0], notlar
'''
assert s.count(old)==1; s=s.replace(old,new)

# ---------------- section 3b ----------------
old=s[s.index('def test_fazla_mesaisiz_ORTAK_arama_da_KISITLIDIR_kuresel_sinir_YAZILMAZ():'):s.index('def test_deneme_BASARISIZSA_ortak_arama_TAM_modeldir_kuresel_sinir_yazilir():')]
new='''def test_URUN_yolunda_bulunsa_da_ortak_arama_TAM_modeldir_kuresel_sinir_YAZILIR():
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


'''
s=s.replace(old,new)

# ---------------- section 5: rewrite from the header to end ----------------
a=s.index('# ----------------------------------------------------------------------\n# 5. HAKEM AGIRLIKLARDIR')
s=s[:a]
io.open(p,"w",encoding="utf-8").write(s)
print("ok", len(s.splitlines()))
PYEOF