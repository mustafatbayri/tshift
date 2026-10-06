# -*- coding: utf-8 -*-
"""
KALITE OLCUMUNUN COZUCUDEN BAGIMSIZ TABANLARI (T-60, 2 Ekim)

`kalite-olc.py` iki alt sinir hesaplar: kapasite tabani (hedefin kac
kisi-saati hicbir planla kapanamaz) ve fazla mesai tabani (sablon
kesikliligi yuzunden kac dakika fazla mesai kacinilmaz). Ikisi de "plan
kotu" ile "kadro/sablon yetmiyor"u ayirmak icin var; YANLIS bir taban
"kadro yetmiyor" dedirtir. Bu yuzden:
  - bilinen sahnelerde tabanin DEGERI sinanir (8 kisi-saat, 300 dakika)
  - gece yarisini asan vardiya ve devreden kapsama tabana sayilir (yoksa
    taban sisirilir ve GECERSIZ olur)
  - cozulen plan tabanin altina inemez (gecerlilik)

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_kalite_olc.py -v
"""

import importlib.util
import os
import sys

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.model import Model                                # noqa: E402
from cozucu.coz import coz                                    # noqa: E402


def _yukle(ad):
    yol = os.path.join(BURASI, ad)
    spec = importlib.util.spec_from_file_location(ad.replace("-", "_").replace(".py", ""), yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KO = _yukle("kalite-olc.py")
AYAR = {"azami_saniye": 20, "durgunluk_saniye": 3, "iki_asama_esigi": 10 ** 9}


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sablon(tid, bas, bit, ekip="E"):
    return {"id": tid, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": 60, "gece_vardiyasi": bit > 24,
            "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]}


def _kisi(cid, saat=45, ekipler=("E",)):
    return {"id": cid, "ekipler": list(ekipler),
            "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": saat, "gun_sayisi": 6},
            "izinler": [], "uygunluk": []}


def _sahne(calisanlar, sablonlar, talep, kurallar):
    return {"profil": "DENGELI", "calisanlar": calisanlar, "vardiya_sablonlari": sablonlar,
            "talep": talep, "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


# ---- kapasite tabani ----------------------------------------------------

def test_kapasite_tabani_iki_kisi_hedef_uc_sekiz_kisi_saat():
    """Gun 0 08-16 hedef 3, iki kisi: her hucrede 1 eksik, 8 kisi-saat
    hicbir planla kapanamaz. Dort duzey de ayni sayiyi verir."""
    g = _sahne([_kisi("C1"), _kisi("C2")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 1, "hedef": 3} for s in range(8, 16)],
               [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"), _kural("HAFTA_TATILI")])
    k = Model(g).kur()
    kt = KO.kapasite_tabani(g, k)
    assert kt["hedef"]["taban_hucre"] == 8 and kt["hedef"]["taban_ekip_gun"] == 8
    assert kt["hedef"]["taban_gun"] == 8
    # Hafta duzeyi GEVSEK: iki kisi haftada 6'sar gun calisabilir (96 saat),
    # talep 24 -- bu duzey 0 der. Taban dort duzeyin EN BUYUGUDUR.
    assert kt["hedef"]["taban_hafta"] == 0
    assert kt["hedef"]["taban"] == 8 and kt["hedef"]["toplam_kisi_saat"] == 24
    assert kt["asgari"]["taban"] == 0
    # Gecerlilik: cozulen plan tabanin altina inemez.
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] >= 8


def test_kapasite_tabani_izinli_gun_arzdan_duser():
    g = _sahne([_kisi("C1"), _kisi("C2")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 2} for s in range(8, 16)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 0
    g["calisanlar"][1]["izinler"] = [{"gun": 0, "durum": "onayli"}]
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 8


def test_kapasite_tabani_gece_yarisini_asan_vardiya_ertesi_gune_sayilir():
    """Talep gun 1 00-07; tek sablon gun 0'da baslayan 23-31. 'Dun baslayan'
    parca sayilmazsa taban 7 cikar -- oysa plan onu sifirla kapatir."""
    g = _sahne([_kisi("C1")], [_sablon("GECE", 23, 31)],
               [{"ekip": "E", "gun": 1, "saat": s, "asgari": 0, "hedef": 1} for s in range(0, 7)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    k = Model(g).kur()
    kt = KO.kapasite_tabani(g, k)
    assert kt["hedef"]["taban"] == 0, kt
    c = coz(g, AYAR, kuruldu=k)
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["HEDEF_KAPSAMA"]["deger"] == 0


def test_kapasite_tabani_devreden_kapsama_sayilir():
    """K-56: onceki haftanin tasan vardiyasi gun 0 00-07'yi kapatir; bu
    haftanin sablonu o saatleri kapsamiyor. Devir sayilmazsa taban 7."""
    g = _sahne([_kisi("C1")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(0, 7)],
               [_kural("HEDEF_KAPSAMA", "YUMUSAK")])
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 7
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    assert KO.kapasite_tabani(g, Model(g).kur())["hedef"]["taban"] == 0


# ---- fazla mesai tabani -------------------------------------------------

def test_fazla_mesai_tabani_kesikli_sablon_bes_saat_kacinilmaz():
    """Tek sablon net 10 saat (08-19, 1 saat yemek); sozlesme 45, SAAT_DENGESI
    sert: 4 vardiya 40 (borcu tutmaz), 5 vardiya 50 -> 5 saat fazla mesai
    kacinilmaz. 7,5 saatlik sablon eklenince 6 x 7,5 = 45: taban 0."""
    # FAZLA_MESAI_TAVANI olmadan model fazla mesaiye HIC izin vermez (fm_pay 0,
    # 50 saat cozumsuz); taban yine gecerli kalir ama plan karsilastirmasi
    # icin tavan kurali eklenir (DENGELI profil: 10 saat).
    g = _sahne([_kisi("C1")], [_sablon("UZUN", 8, 19)],
               [{"ekip": "E", "gun": d, "saat": s, "asgari": 0, "hedef": 1}
                for d in range(7) for s in range(8, 19)],
               [_kural("SAAT_DENGESI", "SERT"), _kural("HAFTA_TATILI"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10)])
    k = Model(g).kur()
    fm = KO.fazla_mesai_tabani(g, k)
    assert fm["kisi"] == 1 and fm["saat_dengesi_sert"] is True
    assert fm["dakika"] == 300 and fm["saat"] == 5.0 and fm["ceza"] == 15000, fm
    c = coz(g, AYAR, kuruldu=k)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert c["cozum_istatistikleri"]["amac_dagilimi"]["FAZLA_MESAI"]["deger"] >= 300
    g["vardiya_sablonlari"].append(_sablon("NORMAL", 8, 16.5))
    assert KO.fazla_mesai_tabani(g, Model(g).kur())["dakika"] == 0


def test_fazla_mesai_tabani_saat_dengesi_sert_degilse_sifir():
    g = _sahne([_kisi("C1")], [_sablon("UZUN", 8, 19)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(8, 19)],
               [_kural("SAAT_DENGESI", "YUMUSAK"), _kural("HEDEF_KAPSAMA", "YUMUSAK")])
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["dakika"] == 0 and fm["saat_dengesi_sert"] is False


def test_fazla_mesai_tabani_borcunu_tutturamayan_sayilir():
    """Tek sablon net 7 saat, hafta tatili var: 6 x 7 = 42 < 45. Kisi borcunu
    hicbir karisimla tutturamaz: taban ona ceza yazmaz, ayri sayar."""
    g = _sahne([_kisi("C1")], [_sablon("T08", 8, 16)],
               [{"ekip": "E", "gun": 0, "saat": s, "asgari": 0, "hedef": 1} for s in range(8, 16)],
               [_kural("SAAT_DENGESI", "SERT"), _kural("HAFTA_TATILI")])
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["borcunu_tutturamayan"] == 1 and fm["dakika"] == 0, fm
    # Hafta tatili yoksa 7 x 7 = 49 >= 45: ulasilir, 4 saat fazla mesai kacinilmaz.
    g["kurallar"] = [_kural("SAAT_DENGESI", "SERT")]
    fm = KO.fazla_mesai_tabani(g, Model(g).kur())
    assert fm["borcunu_tutturamayan"] == 0 and fm["dakika"] == 240, fm


# ----------------------------------------------------------------------
# Hedef dokumu -- acik ve asim NEREDE (T-60 bulgu 10, 2 Ekim aksami)
# ----------------------------------------------------------------------

def test_hedef_dokumu_eksigi_ve_asimi_AYRI_sayar_ve_hucreyi_saklar():
    ihlaller = [
        {"kural": "HEDEF_KAPSAMA", "ekip": "S", "gun": 0, "saat": 7, "olculen": 38, "gereken": 58},
        {"kural": "HEDEF_ASIMI", "ekip": "S", "gun": 0, "saat": 8, "olculen": 102, "gereken": 58},
        {"kural": "HEDEF_KAPSAMA", "ekip": "B", "gun": 1, "saat": 20, "olculen": 17, "gereken": 26},
        {"kural": "ADALET_DENGESI", "calisan": "C1", "olculen": 3, "gereken": 2},      # sayilmaz
        {"kural": "ASGARI_KAPSAMA", "ekip": "S", "gun": 0, "saat": 7, "olculen": 1, "gereken": 2},  # sayilmaz
    ]
    d = KO.hedef_dokumu(ihlaller)
    assert d["toplam"] == {"eksik_kisi_saat": 29, "asim_kisi_saat": 44,
                           "eksik_hucre": 2, "asim_hucre": 1}, d["toplam"]
    assert d["ekip"]["S"] == {"eksik_kisi_saat": 20, "asim_kisi_saat": 44,
                              "eksik_hucre": 1, "asim_hucre": 1}, d["ekip"]
    assert d["ekip"]["B"]["eksik_kisi_saat"] == 9 and d["ekip"]["B"]["asim_kisi_saat"] == 0
    assert d["hucreler"] == [["B", 1, 20, 17, 26], ["S", 0, 7, 38, 58], ["S", 0, 8, 102, 58]]
    assert KO.hedef_dokumu([]) == {"ekip": {}, "hucreler": [],
                                   "toplam": {"eksik_kisi_saat": 0, "asim_kisi_saat": 0,
                                              "eksik_hucre": 0, "asim_hucre": 0}}


def test_hedef_dokumu_dogrulayicinin_eksik_dakikasiyla_AYNI_toplami_verir():
    """Cozulmus bir planda dokumun eksik toplami, dogrulayici metrigindeki
    `eksik_hedef_dakika` ile ayni olmali (ikisi de ayni hucreleri sayar).
    Sahne: 2 kisi, hedef 3 -- her hucrede en az 1 kisi-saat acik kalir."""
    from dogrulayici import degerlendir
    g = {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C%d" % i, "ekipler": ["E"],
                        "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}
                       for i in (1, 2)],
        "vardiya_sablonlari": [_sablon("GUN", 8, 17)],
        "talep": [{"ekip": "E", "gun": d, "saat": h, "asgari": 1, "hedef": 3}
                  for d in (0, 1) for h in range(8, 17)],
        "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                     _kural("HEDEF_ASIMI", "YUMUSAK")],
        "kilitler": [], "donmus_gunler": [],
    }
    c = coz(g, dict(AYAR))
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    d = KO.hedef_dokumu(r["ihlaller"])
    assert d["toplam"]["eksik_kisi_saat"] >= 18, d["toplam"]          # 18 hucre x en az 1
    assert d["toplam"]["eksik_kisi_saat"] * 60 == r["metrikler"]["eksik_hedef_dakika"], (
        d["toplam"], r["metrikler"])
    assert d["toplam"]["asim_kisi_saat"] == 0
    assert len(d["hucreler"]) == d["toplam"]["eksik_hucre"] == 18


# ----------------------------------------------------------------------
# Uc "fazla mesai" sayisi -- hangi ayrisma (2 Ekim gecesi)
# ----------------------------------------------------------------------

def test_fazla_mesai_uyumu_gevsek_cezayi_tanim_bozulmasindan_AYIRIR():
    # 2 Ekim, 900 sn ipucusuz kosu: cezalanan 206,5; motor ve dogrulayici 199
    assert KO.fazla_mesai_uyumu(206.5, 199.0, 199.0) == "ceza_gevsek"
    assert KO.fazla_mesai_uyumu(82.75, 82.75, 82.75) == "ayni"
    # K-57 oncesi hal: motor ile dogrulayici ayri sayiyordu
    assert KO.fazla_mesai_uyumu(9.0, 122.3, 125.5) == "tanim_ayrisiyor"
    # cezalanan plandan KUCUK olamaz (esitsizlik tek yonlu): olursa tanim ayrismis
    assert KO.fazla_mesai_uyumu(190.0, 199.0, 199.0) == "tanim_ayrisiyor"
    assert KO.fazla_mesai_uyumu(199.0, 199.0, None) == "tanim_ayrisiyor"


# ----------------------------------------------------------------------
# O-16 ve bulgu 20 (6 Ekim): mola adimi kosusunda kuresel sinir YAZILMAZ;
# fazla mesai disi amac ayri sayilir; "once fazla mesaisiz" kaydedilir
# ----------------------------------------------------------------------

def test_fm_disi_amac_fazla_mesai_cezasini_duser():
    # 6 Ekim, DENGELI #3: amac 105.742, fazla mesai cezasi 78.750 (1.575 dk x 50)
    s = {"amac_degeri": 105742, "amac_dagilimi": {"FAZLA_MESAI": {"ceza": 78750, "deger": 1575},
                                                  "ADALET_DENGESI": {"ceza": 12455, "deger": 2491}}}
    assert KO.fm_disi_amac(s) == 26992
    assert KO.fm_disi_amac({"amac_degeri": 500, "amac_dagilimi": {}}) == 500        # fazla mesai kurali yok
    assert KO.fm_disi_amac({"amac_degeri": None}) is None                          # plan yok


def test_sinir_yazisi_mola_adiminda_kuresel_sinir_DEMEZ():
    mola = KO.sinir_yazisi({"atamalar_sabit": True, "alt_sinir": None,
                            "optimuma_uzaklik_yuzde": None, "mola_adimi_alt_sinir": 105742})
    assert "kuresel alt sinir YOK" in mola and "105742" in mola and "uzaklik" not in mola
    ortak = KO.sinir_yazisi({"atamalar_sabit": False, "alt_sinir": 20646,
                             "optimuma_uzaklik_yuzde": 87.273})
    assert ortak == "alt sinir 20646  |  uzaklik %87.273"


def test_sinir_yazisi_fazla_mesaisiz_ortak_aramada_da_kuresel_sinir_DEMEZ():
    y = KO.sinir_yazisi({"atamalar_sabit": False, "alt_sinir": None,
                         "optimuma_uzaklik_yuzde": None, "fazla_mesaisiz_alt_sinir": 26000})
    assert "kuresel alt sinir YOK" in y and "26000" in y and "fazla mesaisiz" in y


def test_fm_once_yazisi_UYGULANMAYAN_secenegi_SESSIZ_gecmez():
    ayar = {"fazla_mesai_once_sifir": True}
    assert KO.fm_once_yazisi({"fazla_mesai_once_sifir": None}, {}) is None            # istenmedi
    assert KO.fm_once_yazisi({"fazla_mesai_once_sifir": None}, {"fazla_mesai_once_sifir": False}) is None
    assert "UYGULANMADI" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": None}, ayar)
    assert "UYGULANMADI" in KO.fm_once_yazisi({}, ayar)
    b = {"bulundu": True, "degisken": 359, "saniye": 21.4, "kanitlandi_yok": False, "molalar_sabit": True}
    assert "BULUNDU" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": b}, ayar)
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, bulundu=False, kanitlandi_yok=True)}, ayar)
    assert "YOK (molalar sabitken kanitlandi)" in y, y
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, bulundu=False, kanitlandi_yok=True,
                                                         molalar_sabit=False)}, ayar)
    assert "YOK (kanitlandi)" in y and "molalar sabitken" not in y, y
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, bulundu=False)}, ayar)
    assert "BULUNAMADI" in y and "kanit" not in y, y


def test_ozet_plansiz_ve_istisna_kosusunda_COKMEZ(capsys):
    """`main()` bir kosu istisnayla biterse yalniz dort alanli bir kayit
    yazar; plan bulunamayan kosuda amac yoktur. Ozet ikisinde de basilir."""
    KO.ozet({"kosular": [
        {"yapilandirma": "fm_once_sifir", "durum": "ISTISNA", "hata": "x", "tekrar": 1},
        {"yapilandirma": "fm_once_sifir_kapsama", "durum": "sure_yetmedi",
         "durma_sebebi": "butce_doldu", "toplam_sn": 900.0, "amac_degeri": None,
         "alt_sinir": None, "tekrar": 1}]})
    cikti = capsys.readouterr().out
    assert cikti.count("plan yok") == 2, cikti
    assert "fm_once_sifir_kapsama" in cikti


def _fm_sahnesi():
    """Alti tam zamanli kisi (45 saat), tek sablon 08-17 (8 net saat), bes
    gun asgari 6 / hedef 7: fazla mesai GEREKMEZ, hedef cezasi sifirlanamaz."""
    return _sahne([_kisi("C%d" % i) for i in range(1, 7)], [_sablon("GUN", 8, 17)],
                  [{"ekip": "E", "gun": d, "saat": h, "asgari": 6, "hedef": 7}
                   for d in range(5) for h in range(9, 17)],
                  [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                   _kural("HAFTA_TATILI"), _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10)])


def test_kosu_ve_ozet_mola_adimi_kosusunda_None_sinirla_COKMEZ_yeni_alanlari_SAKLAR(capsys):
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
    assert s["metrikler"]["fazla_mesai_saat"] == 0
    assert s["sert_ihlal"] == 0 and s["yayinlanabilir"] is True
    assert s["uygulanmayan_notlar"] == []
    assert KO.fm_disi_amac(s) == s["amac_degeri"] > 0
    # ayni sahne, urunun varsayilani: secenek kapali, alan None
    v = KO.kosu(g, "varsayilan", dict(azami_saniye=20, durgunluk_saniye=3,
                                      iki_asama_esigi=0, isci_sayisi=2))
    assert v["fazla_mesai_once_sifir"] is None and v["atamalar_sabit"] is True
    KO.ozet({"kosular": [s, v], "kapasite_tabani": {}, "fazla_mesai_tabani": {}})
    cikti = capsys.readouterr().out
    assert "kuresel alt sinir YOK" in cikti
    assert "once fazla mesaisiz: BULUNDU" in cikti
    # ayni sahne esigin altinda (iki asama yok): secenek uygulanmaz, ekrana yazilir
    kucuk = KO.kosu(g, "fm_once_sifir", dict(ayar, iki_asama_esigi=10 ** 9))
    assert kucuk["fazla_mesai_once_sifir"] is None and kucuk["atamalar_sabit"] is False
    assert kucuk["alt_sinir"] is not None                          # tam model: kuresel sinir var
    assert "once fazla mesaisiz: UYGULANMADI" in capsys.readouterr().out
    assert "None%" not in cikti and "%None" not in cikti, cikti
    assert "fm disi" in cikti
