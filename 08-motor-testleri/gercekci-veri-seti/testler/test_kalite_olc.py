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
    # O-18 (7 Ekim): bulununca iki hal -- urun yolu (ipucu, alanlar acik) ve
    # sert kesim (olcum); 6 Ekim kaydinda alan yok = sert kesimdi
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, sifirda_tutuldu=False)}, ayar)
    assert "BULUNDU" in y and "alanlar geri acildi" in y and "agirliklar" in y and "SERT" not in y, y
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": dict(b, sifirda_tutuldu=True)}, ayar)
    assert "BULUNDU" in y and "SERT KESIM" in y and "0'da tutuldu" in y, y
    assert "SERT KESIM" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": b}, ayar)   # 6 Ekim kaydi
    # 7 Ekim 00:45 surumunun kaydi (agirlik kosulu, `uygulandi: False`; Mustafa
    # hic kosmadi) -- KeyError vermesin, okunsun (inceleme A, 04:45)
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": {"uygulandi": False, "sebep": "agirlik",
                                                      "fazla_mesai_agirligi": 5,
                                                      "en_buyuk_oteki_agirlik": 9}}, ayar)
    assert "UYGULANMADI" in y and "agirlik" in y and "00:45" in y, y


def test_fm_once_yazisi_bulgu_25_denemeleri_yazar_eski_kayitta_alan_yok():
    """Yeniden baslatma (bulgu 25): `denemeler` varsa her denemenin tohumu,
    durumu ve suresi satira girer; 7 Ekim sabahindan eski kayitlarda alan
    yoktur, satir eskisi gibi biter."""
    ayar = {"fazla_mesai_once_sifir": True}
    b = {"bulundu": True, "degisken": 359, "saniye": 47.3, "kanitlandi_yok": False,
         "molalar_sabit": True, "sifirda_tutuldu": False, "deneme_siniri": 3,
         "denemeler": [{"tohum": 1, "saniye": 40.0, "durum": "UNKNOWN"},
                       {"tohum": 2, "saniye": 7.3, "durum": "OPTIMAL"}]}
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": b}, ayar)
    assert "deneme 2/3" in y and "tohum 1 UNKNOWN 40.0s" in y and "tohum 2 OPTIMAL 7.3s" in y, y
    eski = {k: v for k, v in b.items() if k not in ("denemeler", "deneme_siniri")}
    y = KO.fm_once_yazisi({"fazla_mesai_once_sifir": eski}, ayar)
    assert "deneme" not in y and y.endswith("359 fazla mesai degiskeni"), y


def test_ipucu_plani_yazisi_K63_alinan_ve_alinamayan_eski_kayitta_None():
    assert KO.ipucu_plani_yazisi({}) is None
    assert KO.ipucu_plani_yazisi({"ipucu_plani": None}) is None
    y = KO.ipucu_plani_yazisi({"ipucu_plani": {"bulundu": True, "saniye": 0.4, "durum": "OPTIMAL"},
                               "durma_sebebi": "mola_adimi_yetismedi"})
    assert "IKINCI ASAMANIN PLANI alindi" in y and "0.4 sn" in y and "mola_adimi_yetismedi" in y, y
    y = KO.ipucu_plani_yazisi({"ipucu_plani": {"bulundu": False, "saniye": 0.1, "durum": "INFEASIBLE"}})
    assert "ALINAMADI" in y and "INFEASIBLE" in y, y


def test_K61_etkin_ayar_secenegi_MOTORUN_varsayilanindan_alir():
    """Yapilandirma secenegi YAZMIYORSA kosuda gecerli olan motorun
    varsayilanidir (K-61: acik; sert kesim KAPALI -- O-18). Satir ona gore
    yazilir; yazilan deger ezer."""
    assert KO.COZ_VARSAYILAN["fazla_mesai_once_sifir"] is True
    assert KO.COZ_VARSAYILAN["fazla_mesai_sifirda_tut"] is False
    assert KO.etkin_ayar({})["fazla_mesai_sifirda_tut"] is False
    assert KO.etkin_ayar(KO.SERT)["fazla_mesai_sifirda_tut"] is True
    assert KO.etkin_ayar({})["fazla_mesai_once_sifir"] is True
    assert KO.etkin_ayar(None)["fazla_mesai_once_sifir"] is True
    assert KO.etkin_ayar({"fazla_mesai_once_sifir": False})["fazla_mesai_once_sifir"] is False
    assert KO.etkin_ayar({"azami_saniye": 7})["azami_saniye"] == 7
    assert "UYGULANMADI" in KO.fm_once_yazisi({"fazla_mesai_once_sifir": None}, KO.etkin_ayar({}))
    assert KO.fm_once_yazisi({"fazla_mesai_once_sifir": None}, KO.etkin_ayar(KO.KAPALI)) is None


def test_K61_kayit_yapilandirmalari_KAPALI_sabit_urun_hali_varsayilandan_ALIR():
    """Varsayilan degisince eski kayit yapilandirmalari SESSIZCE baska bir
    sey olcmesin: 6 Ekim oncesini olcen her yapilandirma secenegi acikca
    kapatir; urun halini olcenler hic yazmaz (motorun varsayilanini alir).
    Yeni yapilandirma eklenirse bu listelerden birine YAZILMAK zorundadir."""
    urun = {"varsayilan", "profil_kapsama", "profil_calisan", "cift_butce", "lp_guclu"}
    # 7 Ekim sabahinin urun yolu (bulgu 23 kaydi): alanlar acik, TEK deneme --
    # 8 Ekim'de varsayilan 3 olunca anlami degismesin diye 1 ACIKCA yazili
    acik = {"fm_once", "fm_once_kapsama"}
    # bulgu 25 / K-61 kapanisi: urun yolu + yeniden baslatma (3 x 40 sn) = bugunku varsayilan
    yeniden = {"fm_once_deneme3", "fm_once_deneme3_kapsama"}
    # SERT KESIM (6 Ekim gecesinin hali; bulgu 21'in kaydi) -- yalniz olcum
    sert = {"fm_sert", "fm_sert_kapsama", "fm_once_sifir", "fm_once_sifir_kapsama"}
    kayit = {"fm_once_kapali", "fm_once_kapali_kapsama", "k59_hali", "oran_90",
             "eski_urun_hali", "fm_agirlik_5", "fm_agirlik_1", "a_ipuclu_120",
             "a_ipucusuz_120", "a_ipuclu_60", "a_ipuclu_240", "sabit_mola_480",
             "mola_ayri_adim", "mola_adimi_tam", "b_paralel_3", "b_paralel_2"}
    iki_asamasiz = {"ipucu_kapali"}                                     # deneme zaten yapilmaz
    assert set(KO.YAPILANDIRMALAR) == urun | acik | yeniden | sert | kayit | iki_asamasiz
    for ad in urun | iki_asamasiz:
        assert "fazla_mesai_once_sifir" not in KO.YAPILANDIRMALAR[ad][1], ad
        assert "fazla_mesai_sifirda_tut" not in KO.YAPILANDIRMALAR[ad][1], ad
        assert "fazla_mesaisiz_deneme" not in KO.YAPILANDIRMALAR[ad][1], ad   # motorun varsayilani (1)
    for ad in acik:
        assert KO.YAPILANDIRMALAR[ad][1] == {"fazla_mesai_once_sifir": True,
                                             "fazla_mesai_sifirda_tut": False,
                                             "fazla_mesaisiz_deneme": 1}, ad
    for ad in yeniden:
        assert KO.YAPILANDIRMALAR[ad][1] == {"fazla_mesai_once_sifir": True,
                                             "fazla_mesai_sifirda_tut": False,
                                             "fazla_mesaisiz_deneme": 3}, ad
    assert KO.YAPILANDIRMALAR["fm_once_deneme3_kapsama"][2] == {"profil": "KAPSAMA"}
    assert KO.COZ_VARSAYILAN["fazla_mesaisiz_deneme"] == 3       # K-61 kapanisi (8 Ekim); `urun` kumesi varsayilani alir
    assert KO.etkin_ayar({})["fazla_mesaisiz_deneme"] == 3
    assert KO.etkin_ayar(KO.YAPILANDIRMALAR["fm_once"][1])["fazla_mesaisiz_deneme"] == 1
    for ad in sert:
        assert KO.YAPILANDIRMALAR[ad][1] == KO.SERT and KO.YAPILANDIRMALAR[ad][1] is not KO.SERT, ad
    for ad in kayit:
        assert KO.YAPILANDIRMALAR[ad][1]["fazla_mesai_once_sifir"] is False, ad
    assert KO.KAPALI == {"fazla_mesai_once_sifir": False}
    assert KO.SERT == {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": True}
    assert KO.YAPILANDIRMALAR["fm_once_kapali"][1] == KO.KAPALI
    assert KO.YAPILANDIRMALAR["fm_once_kapali"][1] is not KO.KAPALI        # kopya: kosu degistirmesin
    assert KO.YAPILANDIRMALAR["fm_once_kapali_kapsama"][2] == {"profil": "KAPSAMA"}
    # kayit yapilandirmalarinin KENDI ayarlari yerinde
    assert KO.YAPILANDIRMALAR["k59_hali"][1] == {
        "fazla_mesai_once_sifir": False, "ilk_asama_iyilestirme_orani": 0.4, "mola_adimi": False}
    assert KO.YAPILANDIRMALAR["mola_adimi_tam"][1] == {
        "fazla_mesai_once_sifir": False, "ilk_asama_iyilestirme_saniye": 480,
        "ilk_asama_iyilestirme_orani": 0.85, "mola_adimi": True, "mola_adimi_hedef_bosluk": 0.0}
    assert KO.YAPILANDIRMALAR["fm_agirlik_5"][2] == {"agirliklar": {"FAZLA_MESAI": 5}}


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
    # 6 Ekim oncesinin hali: kapali, alan None, durum satiri YOK
    e = KO.kosu(g, "fm_once_kapali", dict(KO.YAPILANDIRMALAR["fm_once_kapali"][1], **kucuk_ayar))
    assert e["once_fazla_mesaisiz"] is False and e["ayar"]["fazla_mesai_once_sifir"] is False
    assert e["sert_kesim"] is False
    assert e["fazla_mesai_once_sifir"] is None and e["atamalar_sabit"] is True
    assert "once fazla mesaisiz: " not in capsys.readouterr().out
    KO.ozet({"kosular": [s, v, e], "kapasite_tabani": {}, "fazla_mesai_tabani": {}})
    cikti = capsys.readouterr().out
    # ayni sahne esigin altinda (iki asama yok): secenek uygulanmaz, ekrana yazilir
    kucuk = KO.kosu(g, "fm_once_sifir", dict(ayar, iki_asama_esigi=10 ** 9))
    assert kucuk["fazla_mesai_once_sifir"] is None and kucuk["atamalar_sabit"] is False
    assert kucuk["alt_sinir"] is not None                          # tam model: kuresel sinir var
    assert "once fazla mesaisiz: UYGULANMADI" in capsys.readouterr().out
    assert "None%" not in cikti and "%None" not in cikti, cikti
    assert "fm disi" in cikti
