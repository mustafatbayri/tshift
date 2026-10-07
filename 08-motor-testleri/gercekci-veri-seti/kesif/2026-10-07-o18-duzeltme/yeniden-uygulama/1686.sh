cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/08-motor-testleri/gercekci-veri-seti && python3 - <<'PYEOF'
import io
p="testler/test_kalite_olc.py"
s=io.open(p,encoding="utf-8").read()
R=[]
R.append(('''    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, bulundu=False)}, ayar)
    assert "BULUNAMADI" in y and "kanit" not in y, y
    # K-61: agirlik kosulu tutmadiysa deneme yapilmaz -- bu da SESSIZ gecmez
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": {
        "uygulandi": False, "sebep": "agirlik",
        "fazla_mesai_agirligi": 5, "en_buyuk_oteki_agirlik": 9}}, ayar)
    assert "UYGULANMADI" in y and "agirlik kosulu" in y and " 5," in y and " 9)" in y, y
    assert "BULUNDU" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, uygulandi=True)}, ayar)
''','''    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, bulundu=False)}, ayar)
    assert "BULUNAMADI" in y and "kanit" not in y, y
    # O-18 (7 Ekim): bulununca iki hal -- urun yolu (ipucu, alanlar acik) ve
    # sert kesim (olcum); 6 Ekim kaydinda alan yok = sert kesimdi
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, sifirda_tutuldu=False)}, ayar)
    assert "BULUNDU" in y and "alanlar geri acildi" in y and "agirliklar" in y and "SERT" not in y, y
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, sifirda_tutuldu=True)}, ayar)
    assert "BULUNDU" in y and "SERT KESIM" in y and "0'da tutuldu" in y, y
    assert "SERT KESIM" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": b}, ayar)   # 6 Ekim kaydi
'''))
R.append(('''def test_K61_etkin_ayar_secenegi_MOTORUN_varsayilanindan_alir():
    """Yapilandirma secenegi YAZMIYORSA kosuda gecerli olan motorun
    varsayilanidir (K-61: acik). Satir ona gore yazilir; yazilan deger ezer."""
    assert KO.COZ_VARSAYILAN["fazla_mesai_once_sifir"] is True
''','''def test_K61_etkin_ayar_secenegi_MOTORUN_varsayilanindan_alir():
    """Yapilandirma secenegi YAZMIYORSA kosuda gecerli olan motorun
    varsayilanidir (K-61: acik; sert kesim KAPALI -- O-18). Satir ona gore
    yazilir; yazilan deger ezer."""
    assert KO.COZ_VARSAYILAN["fazla_mesai_once_sifir"] is True
    assert KO.COZ_VARSAYILAN["fazla_mesai_sifirda_tut"] is False
    assert KO.etkin_ayar({})["fazla_mesai_sifirda_tut"] is False
    assert KO.etkin_ayar(KO.SERT)["fazla_mesai_sifirda_tut"] is True
'''))
R.append(('''    urun = {"varsayilan", "profil_kapsama", "profil_calisan", "cift_butce", "lp_guclu"}
    acik = {"fm_once_sifir", "fm_once_sifir_kapsama"}                  # bulgu 21 kaydi
    kayit = {"fm_once_kapali", "fm_once_kapali_kapsama", "k59_hali", "oran_90",
             "eski_urun_hali", "fm_agirlik_5", "fm_agirlik_1", "a_ipuclu_120",
             "a_ipucusuz_120", "a_ipuclu_60", "a_ipuclu_240", "sabit_mola_480",
             "mola_ayri_adim", "mola_adimi_tam", "b_paralel_3", "b_paralel_2"}
    iki_asamasiz = {"ipucu_kapali"}                                     # deneme zaten yapilmaz
    assert set(KO.YAPILANDIRMALAR) == urun | acik | kayit | iki_asamasiz
    for ad in urun | iki_asamasiz:
        assert "fazla_mesai_once_sifir" not in KO.YAPILANDIRMALAR[ad][1], ad
    for ad in acik:
        assert KO.YAPILANDIRMALAR[ad][1]["fazla_mesai_once_sifir"] is True, ad
    for ad in kayit:
        assert KO.YAPILANDIRMALAR[ad][1]["fazla_mesai_once_sifir"] is False, ad
    assert KO.KAPALI == {"fazla_mesai_once_sifir": False}
''','''    urun = {"varsayilan", "profil_kapsama", "profil_calisan", "cift_butce", "lp_guclu"}
    # 7 Ekim urun yolu, ACIKCA yazilmis (olcum kaydinin adi): alanlar acik
    acik = {"fm_once", "fm_once_kapsama"}
    # SERT KESIM (6 Ekim gecesinin hali; bulgu 21'in kaydi) -- yalniz olcum
    sert = {"fm_sert", "fm_sert_kapsama", "fm_once_sifir", "fm_once_sifir_kapsama"}
    kayit = {"fm_once_kapali", "fm_once_kapali_kapsama", "k59_hali", "oran_90",
             "eski_urun_hali", "fm_agirlik_5", "fm_agirlik_1", "a_ipuclu_120",
             "a_ipucusuz_120", "a_ipuclu_60", "a_ipuclu_240", "sabit_mola_480",
             "mola_ayri_adim", "mola_adimi_tam", "b_paralel_3", "b_paralel_2"}
    iki_asamasiz = {"ipucu_kapali"}                                     # deneme zaten yapilmaz
    assert set(KO.YAPILANDIRMALAR) == urun | acik | sert | kayit | iki_asamasiz
    for ad in urun | iki_asamasiz:
        assert "fazla_mesai_once_sifir" not in KO.YAPILANDIRMALAR[ad][1], ad
        assert "fazla_mesai_sifirda_tut" not in KO.YAPILANDIRMALAR[ad][1], ad
    for ad in acik:
        assert KO.YAPILANDIRMALAR[ad][1] == {"fazla_mesai_once_sifir": True,
                                             "fazla_mesai_sifirda_tut": False}, ad
    for ad in sert:
        assert KO.YAPILANDIRMALAR[ad][1] == KO.SERT and KO.YAPILANDIRMALAR[ad][1] is not KO.SERT, ad
    for ad in kayit:
        assert KO.YAPILANDIRMALAR[ad][1]["fazla_mesai_once_sifir"] is False, ad
    assert KO.KAPALI == {"fazla_mesai_once_sifir": False}
    assert KO.SERT == {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": True}
'''))
R.append(('''def test_kosu_ve_ozet_mola_adimi_kosusunda_None_sinirla_COKMEZ_yeni_alanlari_SAKLAR(capsys):
    """Urun yolu (iki asama + mola adimi) ile kosulan yapilandirmada `kosu`
    kuresel sinir yazmaz, mola adiminin sinirini ve "once fazla mesaisiz"
    sonucunu saklar; `ozet` None sinirla tablo basar (eskiden "None%")."""
    assert "fm_once_sifir" in KO.YAPILANDIRMALAR and "fm_once_sifir_kapsama" in KO.YAPILANDIRMALAR
    assert KO.YAPILANDIRMALAR["fm_once_sifir"][1] == {"fazla_mesai_once_sifir": True}
    assert KO.YAPILANDIRMALAR["fm_once_sifir"][2] == {}
    assert KO.YAPILANDIRMALAR["fm_once_sifir_kapsama"][2] == {"profil": "KAPSAMA"}
    g = _fm_sahnesi()
    ayar = dict(KO.YAPILANDIRMALAR["fm_once_sifir"][1],
                azami_saniye=20, durgunluk_saniye=3, iki_asama_esigi=0, isci_sayisi=2)
    s = KO.kosu(g, "fm_once_sifir", ayar)
    assert s["durum"] == "cozuldu" and s["iki_asama"] is True and s["atamalar_sabit"] is True, s
    assert s["alt_sinir"] is None and s["optimuma_uzaklik_yuzde"] is None
    assert s["mola_adimi_alt_sinir"] == s["amac_degeri"]
    assert s["durma_sebebi"] == "mola_adimi_optimum"
    assert s["fazla_mesai_once_sifir"]["bulundu"] is True, s["fazla_mesai_once_sifir"]
    assert s["once_fazla_mesaisiz"] is True
    assert s["metrikler"]["fazla_mesai_saat"] == 0
    assert s["sert_ihlal"] == 0 and s["yayinlanabilir"] is True
    assert s["uygulanmayan_notlar"] == []
    assert KO.fm_disi_amac(s) == s["amac_degeri"] > 0
    # ayni sahne, urunun varsayilani (K-61): secenek YAZILMADAN da acik --
    # motorun varsayilanindan gelir, kosu kaydi bunu soyler, satir yazilir
    kucuk_ayar = dict(azami_saniye=20, durgunluk_saniye=3, iki_asama_esigi=0, isci_sayisi=2)
    assert KO.YAPILANDIRMALAR["varsayilan"][1] == {}
    v = KO.kosu(g, "varsayilan", dict(kucuk_ayar))
    assert v["once_fazla_mesaisiz"] is True and "fazla_mesai_once_sifir" not in v["ayar"]
    assert v["fazla_mesai_once_sifir"]["bulundu"] is True and v["atamalar_sabit"] is True
    assert v["metrikler"]["fazla_mesai_saat"] == 0 and v["amac_degeri"] == s["amac_degeri"]
    ekran = capsys.readouterr().out                 # iki kosunun ekrani
    assert ekran.count("kuresel alt sinir YOK") == 2, ekran
    assert ekran.count("once fazla mesaisiz: BULUNDU") == 2, ekran
''','''def test_kosu_ve_ozet_mola_adimi_kosusunda_None_sinirla_COKMEZ_yeni_alanlari_SAKLAR(capsys):
    """Urun yolu (iki asama + mola adimi) ile kosulan yapilandirmada `kosu`
    kuresel sinir yazmaz, mola adiminin sinirini ve "once fazla mesaisiz"
    sonucunu saklar; `ozet` None sinirla tablo basar (eskiden "None%")."""
    assert "fm_once_sifir" in KO.YAPILANDIRMALAR and "fm_once_sifir_kapsama" in KO.YAPILANDIRMALAR
    assert KO.YAPILANDIRMALAR["fm_once_sifir"][1] == KO.SERT               # bulgu 21: sert kesim
    assert KO.YAPILANDIRMALAR["fm_once_sifir"][2] == {}
    assert KO.YAPILANDIRMALAR["fm_once_sifir_kapsama"][2] == {"profil": "KAPSAMA"}
    g = _fm_sahnesi()
    ayar = dict(KO.YAPILANDIRMALAR["fm_once_sifir"][1],
                azami_saniye=20, durgunluk_saniye=3, iki_asama_esigi=0, isci_sayisi=2)
    s = KO.kosu(g, "fm_once_sifir", ayar)
    assert s["durum"] == "cozuldu" and s["iki_asama"] is True and s["atamalar_sabit"] is True, s
    assert s["alt_sinir"] is None and s["optimuma_uzaklik_yuzde"] is None
    assert s["mola_adimi_alt_sinir"] == s["amac_degeri"]
    assert s["durma_sebebi"] == "mola_adimi_optimum"
    assert s["fazla_mesai_once_sifir"]["bulundu"] is True, s["fazla_mesai_once_sifir"]
    assert s["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is True          # sert kesim (olcum)
    assert s["once_fazla_mesaisiz"] is True and s["sert_kesim"] is True
    assert s["metrikler"]["fazla_mesai_saat"] == 0
    assert s["sert_ihlal"] == 0 and s["yayinlanabilir"] is True
    assert s["uygulanmayan_notlar"] == []
    assert KO.fm_disi_amac(s) == s["amac_degeri"] > 0
    # ayni sahne, urunun varsayilani (K-61/O-18): secenek YAZILMADAN da acik --
    # motorun varsayilanindan gelir, sert kesim KAPALI, kosu kaydi bunu soyler
    kucuk_ayar = dict(azami_saniye=20, durgunluk_saniye=3, iki_asama_esigi=0, isci_sayisi=2)
    assert KO.YAPILANDIRMALAR["varsayilan"][1] == {}
    v = KO.kosu(g, "varsayilan", dict(kucuk_ayar))
    assert v["once_fazla_mesaisiz"] is True and "fazla_mesai_once_sifir" not in v["ayar"]
    assert v["sert_kesim"] is False and "fazla_mesai_sifirda_tut" not in v["ayar"]
    assert v["fazla_mesai_once_sifir"]["bulundu"] is True and v["atamalar_sabit"] is True
    assert v["fazla_mesai_once_sifir"]["sifirda_tutuldu"] is False
    assert v["metrikler"]["fazla_mesai_saat"] == 0 and v["amac_degeri"] == s["amac_degeri"]
    ekran = capsys.readouterr().out                 # iki kosunun ekrani
    assert ekran.count("kuresel alt sinir YOK") == 2, ekran
    assert ekran.count("once fazla mesaisiz: BULUNDU") == 2, ekran
    assert ekran.count("SERT KESIM") == 1 and ekran.count("alanlar geri acildi; karari agirliklar") == 1, ekran
'''))
R.append(('''    e = KO.kosu(g, "fm_once_kapali", dict(KO.YAPILANDIRMALAR["fm_once_kapali"][1], **kucuk_ayar))
    assert e["once_fazla_mesaisiz"] is False and e["ayar"]["fazla_mesai_once_sifir"] is False
''','''    e = KO.kosu(g, "fm_once_kapali", dict(KO.YAPILANDIRMALAR["fm_once_kapali"][1], **kucuk_ayar))
    assert e["once_fazla_mesaisiz"] is False and e["ayar"]["fazla_mesai_once_sifir"] is False
    assert e["sert_kesim"] is False
'''))
for old,new in R:
    assert s.count(old)==1, old[:80]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
cd testler && PYTHONDONTWRITEBYTECODE=1 timeout 600 python3 -m pytest test_kalite_olc.py -q -p no:cacheprovider 2>&1 | tail -5; tail -3 ../../../../log/depo-09-motor-1.log