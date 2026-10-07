cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/09-motor/testler && cat >> test_fazla_mesai_once_sifir.py <<'PYEOF'
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
PYEOF
cd .. && PYTHONDONTWRITEBYTECODE=1 timeout 900 python3 -m pytest testler/test_fazla_mesai_once_sifir.py -q -p no:cacheprovider -x 2>&1 | tail -15