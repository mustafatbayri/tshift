# -*- coding: utf-8 -*-
"""
DONMUS GUN DEGISMEZ -- "OLAN OLDU" (K-54, T-29, 1 Ekim)

NEDEN (T-29, dis inceleme 16 Eylul)
  `DONMUS_GUN` kurali yalniz `_yeni` bayragi tasiyan atamayi ihlal sayiyordu
  ve o bayragi hicbir sey uretmiyordu. Urunun "gecmis yeniden planlanamaz"
  sozunun tek bekcisi hic ateslenemiyordu; cozucu donmus gunleri ayrica
  korumuyordu.

KARAR (Mustafa, 1 Ekim): yayinlanmis plan (`mevcut_plan`) motora gelir;
  yonetici gecmis gunleri duzenlemis olabilir ("baska bir elemani o gun
  kendi inisiyatifiyle ise cagirabilir"); motor donmus gunleri OLDUGU GIBI
  alir, gelecek gunleri onlara uyarak planlar; gelecek gunlerde kilitler
  gecerlidir.

BU DOSYA NE SINAR
  cozucu   : donmus gun satirlari AYNEN gecer (molalariyla), yeni atama
             yazilmaz, gelecek gunler gecmise uyar (dinlenme, haftalik saat),
             gecmisin kusuru modeli cozumsuz BIRAKMAZ (eksik kapsama, asilmis
             tavan), plansiz donmus gun not dusurur, kilit donmus gunde
             uygulanmaz, sablona oturmayan satir aynen gecer.
  dogrulayici: DONMUS_GUN eklenen/silinen/degisen satiri bayraksiz yakalar;
             plan yoksa "denetlenemedi" (kabul bekler); yalniz donmus gune
             dayanan ihlal "gecmis" isaretlenir ve kapi onu saymaz; donmus
             gunle serbest gun arasindaki ihlal isaretlenMEZ.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_donmus_gun.py -v
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model                                # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402

AYAR = {"azami_saniye": 30, "durgunluk_saniye": 3, "iki_asama_esigi": 10 ** 9}


def _kurallar():
    sert = [
        {"kod": k, "tur": "SERT", "aktif": True, "yasal": y, "kabul_edilebilir": False}
        for k, y in (("ASGARI_KAPSAMA", False), ("GUNLUK_AZAMI", True),
                     ("HAFTALIK_AZAMI", True), ("VARDIYA_ARASI_DINLENME", True),
                     ("DONMUS_GUN", False), ("KILIT_UYUMU", False),
                     ("CAKISMA_YOK", False))
    ]
    sert[1]["parametreler"] = {"azami_saat": 11}
    sert[2]["parametreler"] = {"azami_saat": 45}
    sert[3]["parametreler"] = {"asgari_saat": 11}
    return sert + [{"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True}]


def _sahne(kisi=4, saatler=(8, 16), asgari=1):
    """Tek ekip, uc sablon (06-14, 08-16, 16-24), yedi gun, saat basi talep."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [
            {"id": "T06", "ekip": "E", "bas": 6, "bit": 14, "mola_dk": 60,
             "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
            {"id": "T08", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60,
             "gece_vardiyasi": False,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
            {"id": "T16", "ekip": "E", "bas": 16, "bit": 24, "mola_dk": 60,
             "gece_vardiyasi": True,
             "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]},
        ],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": asgari, "hedef": asgari}
                  for d in range(7) for s in range(*saatler)],
        "kurallar": _kurallar(),
        "kilitler": [], "donmus_gunler": [],
    }


def _satir(calisan, gun, sablon, yemek_bas=None):
    bas, bit = {"T06": (6, 14), "T08": (8, 16), "T16": (16, 24)}[sablon]
    molalar = ([{"bas": yemek_bas, "bit": yemek_bas + 1, "tip": "yemek"}]
               if yemek_bas is not None else [])
    return {"calisan": calisan, "ekip": "E", "sablon": sablon, "gun": gun,
            "bas": bas, "bit": bit, "molalar": molalar}


def _yemek_adayi(girdi, sablon_id):
    """Cozucunun o sablon icin kullandigi ILK yemek aday saati."""
    m = Model(girdi)
    t = m.sablon[sablon_id]
    sy, _ = m.sabit_mola_secimi(t)
    return sy


def _gun(atamalar, d):
    return sorted((a["calisan"], a["bas"], a["bit"]) for a in atamalar if a["gun"] == d)


# ----------------------------------------------------------------------
# COZUCU
# ----------------------------------------------------------------------

def test_donmus_gun_satirlari_AYNEN_gecer_molalariyla():
    g = _sahne()
    sy = _yemek_adayi(g, "T08")
    plan = [_satir("C1", 0, "T08", yemek_bas=sy)]
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = plan
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    gun0 = [a for a in c["atamalar"] if a["gun"] == 0]
    assert len(gun0) == 1, gun0
    assert gun0[0]["calisan"] == "C1" and gun0[0]["sablon"] == "T08"
    assert gun0[0]["molalar"] == plan[0]["molalar"], "molalar plandan aynen gecmeli"
    assert gun0[0].get("donmus") is True
    # Diger gunler planlandi.
    assert all(_gun(c["atamalar"], d) for d in range(1, 7))
    ist = c["cozum_istatistikleri"]["donmus_gun"]
    assert ist["gunler"] == [0] and ist["aktarilan_satir"] == 1
    assert ist["dusen_kisit"] > 0, "donmus gunun kisitlari dusmeliydi"


def test_donmus_gune_YENI_atama_yazilmaz_eksik_kapsama_cozumsuz_etmez():
    """Gun 0'da talep 08-24 ama planda yalniz 08-16 var: olan oldu."""
    g = _sahne(saatler=(8, 24))
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", yemek_bas=_yemek_adayi(g, "T08"))]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert _gun(c["atamalar"], 0) == [("C1", 8, 16)]
    r = degerlendir(g, c["atamalar"])
    eksik = [i for i in r["ihlaller"] if i["kural"] == "ASGARI_KAPSAMA" and i.get("gun") == 0]
    assert eksik, "gun 0'daki eksik kapsama raporlanmali (gercek)"
    assert all(i.get("gecmis") for i in eksik), "gun 0 donmus: ihlal gecmis isaretli olmali"
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["yayin_kapisi"]
    assert r["metrikler"]["sert_ihlal"] == 0
    assert r["metrikler"]["gecmis_sert_ihlal"] >= len(eksik)
    assert r["gecmis_ihlaller"]


def test_donmus_saatler_HAFTALIK_tavana_sayilir():
    """C1 gun 0-4'te 7'ser saat net calismis (35 h); kalan iki gunde en fazla 10 h."""
    g = _sahne(kisi=5)
    sy = _yemek_adayi(g, "T08")
    g["donmus_gunler"] = [0, 1, 2, 3, 4]
    g["mevcut_plan"] = [_satir("C1", d, "T08", yemek_bas=sy) for d in range(5)] + \
                       [_satir("C2", d, "T08", yemek_bas=sy) for d in range(5)]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    c1_serbest = [a for a in c["atamalar"] if a["calisan"] == "C1" and a["gun"] >= 5]
    assert len(c1_serbest) <= 1, "35 h dolu: iki gunde iki 7 saatlik vardiya 45'i asar: %r" % c1_serbest
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "HAFTALIK_AZAMI"], r["ihlaller"]


def test_tavan_GECMISTE_asilmissa_model_cozumsuz_olmaz_kalan_gunlere_pay_kalmaz():
    """C1 gun 0-5'te 42 h; 6. gunde 7 h daha 45'i asar -> C1 gun 6'da calismaz."""
    g = _sahne(kisi=5)
    sy = _yemek_adayi(g, "T08")
    g["kurallar"][2]["parametreler"] = {"azami_saat": 40}       # tavan 40
    g["donmus_gunler"] = [0, 1, 2, 3, 4, 5]
    g["mevcut_plan"] = [_satir("C1", d, "T08", yemek_bas=sy) for d in range(6)]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", "gecmis 42 h > 40 h tavan modeli cozumsuz etmemeli: %s" % c.get("durum")
    assert not [a for a in c["atamalar"] if a["calisan"] == "C1" and a["gun"] == 6]
    ist = c["cozum_istatistikleri"]["donmus_gun"]
    assert ist["kirpilan_kisit"] >= 1, ist
    assert any("kirpildi" in n for n in c["uygulanmayan_notlar"])
    r = degerlendir(g, c["atamalar"])
    haftalik = [i for i in r["ihlaller"] if i["kural"] == "HAFTALIK_AZAMI" and i.get("calisan") == "C1"]
    assert haftalik and all(i.get("gecmis") for i in haftalik), haftalik
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


def test_donmus_gece_vardiyasi_ertesi_gunun_DINLENMESINI_belirler():
    """C1 gun 0'da 16-24 calismis; gun 1'de 11 saat dinlenmeden once baslayamaz."""
    g = _sahne(kisi=3, saatler=(6, 24), asgari=1)
    g["talep"] = [t for t in g["talep"] if t["gun"] <= 1]        # iki gun yeter
    # Gun 1'de 06-24 uc vardiya ister (06-14, 08-16, 16-24); C1 11:00'den
    # once baslayamayacagi icin ona yalniz 16-24 kalir.
    sy = _yemek_adayi(g, "T16")
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T16", yemek_bas=sy),
                        _satir("C2", 0, "T06", yemek_bas=_yemek_adayi(g, "T06")),
                        _satir("C2", 0, "T08", yemek_bas=_yemek_adayi(g, "T08"))]
    # C2 gun 0'da iki vardiya (yonetici oyle yazmis): gecmis, cozumsuz etmez.
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert _gun(c["atamalar"], 0) == [("C1", 16, 24), ("C2", 6, 14), ("C2", 8, 16)]
    c1_gun1 = [a for a in c["atamalar"] if a["calisan"] == "C1" and a["gun"] == 1]
    assert all(a["bas"] >= 11 for a in c1_gun1), "C1 gun 1'de 11:00'den once baslayamaz: %r" % c1_gun1
    r = degerlendir(g, c["atamalar"])
    dinlenme = [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ARASI_DINLENME"]
    assert not [i for i in dinlenme if not i.get("gecmis")], dinlenme


def test_PLANSIZ_donmus_gun_serbest_planlanir_not_duser_kapi_kabul_bekler():
    g = _sahne()
    g["donmus_gunler"] = [0]                 # mevcut_plan YOK
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    assert any("mevcut_plan" in n and "SERBEST" in n for n in c["uygulanmayan_notlar"]), \
        c["uygulanmayan_notlar"]
    assert _gun(c["atamalar"], 0), "plansiz donmus gun serbest planlanmali"
    r = degerlendir(g, c["atamalar"])
    d = [x for x in r["yayin_kapisi"]["denetlenemeyen_kurallar"] if x["kod"] == "DONMUS_GUN"]
    assert d and d[0]["etki"] == "kabul_bekliyor", r["yayin_kapisi"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is False
    g["denetim_disi_kabul"] = [{"kod": "DONMUS_GUN", "gerekce": "ilk hafta, yayinlanmis plan yok",
                                "onaylayan": "u1"}]
    r2 = degerlendir(g, c["atamalar"])
    assert r2["yayin_kapisi"]["yayinlanabilir"] is True, r2["yayin_kapisi"]


def test_KILIT_donmus_gunde_uygulanmaz_mevcut_plan_gecerli():
    g = _sahne()
    sy = _yemek_adayi(g, "T08")
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", yemek_bas=sy)]
    g["kilitler"] = [{"calisan": "C1", "gun": 0, "tip": "yasak"},            # planla celisir
                     {"calisan": "C2", "gun": 1, "tip": "yasak"}]           # gelecek: gecerli
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert _gun(c["atamalar"], 0) == [("C1", 8, 16)]
    assert any("kilit donmus gune" in n for n in c["uygulanmayan_notlar"])
    assert not [a for a in c["atamalar"] if a["calisan"] == "C2" and a["gun"] == 1]
    r = degerlendir(g, c["atamalar"])
    kilit = [i for i in r["ihlaller"] if i["kural"] == "KILIT_UYUMU"]
    assert kilit and all(i.get("gecmis") for i in kilit), kilit
    assert r["yayin_kapisi"]["yayinlanabilir"] is True


def test_sablona_OTURMAYAN_satir_aynen_gecer_not_duser():
    g = _sahne()
    g["donmus_gunler"] = [0]
    tuhaf = {"calisan": "C1", "ekip": "E", "sablon": None, "gun": 0,
             "bas": 10, "bit": 14, "molalar": []}
    g["mevcut_plan"] = [tuhaf, _satir("C2", 0, "T08", yemek_bas=_yemek_adayi(g, "T08"))]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    assert _gun(c["atamalar"], 0) == [("C1", 10, 14), ("C2", 8, 16)]
    assert any("hicbir sablona oturmadi" in n for n in c["uygulanmayan_notlar"])
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "DONMUS_GUN"]


def test_donmus_gun_YOKSA_mevcut_plan_yalniz_ipucudur():
    g = _sahne()
    sy = _yemek_adayi(g, "T08")
    g["mevcut_plan"] = [_satir("C1", 0, "T08", yemek_bas=sy)]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    assert c["cozum_istatistikleri"]["donmus_gun"] is None
    assert not any(a.get("donmus") for a in c["atamalar"])
    assert c["cozum_istatistikleri"]["baslangic_plani_kullanildi"] is True


# ----------------------------------------------------------------------
# DOGRULAYICI -- DONMUS_GUN govdesi (bayraksiz)
# ----------------------------------------------------------------------

def _tanim():
    return {"kod": "DONMUS_GUN", "tur": "SERT", "aktif": True, "kabul_edilebilir": False}


def test_dogrulayici_AYNI_plan_ihlal_yok():
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", 12), _satir("C2", 0, "T16", 20)]
    plan = copy.deepcopy(g["mevcut_plan"]) + [_satir("C3", 1, "T08", 12)]
    assert K.donmus_gun(g, plan, _tanim()) == []


def test_dogrulayici_EKLENEN_SILINEN_DEGISEN_satiri_yakalar():
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", 12), _satir("C2", 0, "T16", 20)]
    eklenen = copy.deepcopy(g["mevcut_plan"]) + [_satir("C3", 0, "T06", 10)]
    i = K.donmus_gun(g, eklenen, _tanim())
    assert len(i) == 1 and i[0]["calisan"] == "C3" and "YOK" in i[0]["mesaj"]
    silinen = [g["mevcut_plan"][0]]
    i = K.donmus_gun(g, silinen, _tanim())
    assert len(i) == 1 and i[0]["calisan"] == "C2" and "cikmis" in i[0]["mesaj"]
    degisen = [g["mevcut_plan"][0], _satir("C2", 0, "T06", 10)]
    i = K.donmus_gun(g, degisen, _tanim())
    assert len(i) == 2 and {x["calisan"] for x in i} == {"C2"}
    assert all(i_["agirlik"] == "SERT" and not i_.get("kabul_edilebilir") for i_ in i)
    # Serbest gundeki fark ihlal DEGIL.
    serbest = copy.deepcopy(g["mevcut_plan"]) + [_satir("C3", 2, "T08", 12)]
    assert K.donmus_gun(g, serbest, _tanim()) == []


def test_dogrulayici_plan_YOKSA_bos_doner_ve_eksik_boyut_bildirir():
    g = _sahne()
    g["donmus_gunler"] = [0]
    assert K.donmus_gun(g, [_satir("C1", 0, "T08", 12)], _tanim()) == []
    r = degerlendir(g, [_satir("C1", 0, "T08", 12)])
    e = [x for x in r["eksik_boyutlar"] if x["kural"] == "DONMUS_GUN"]
    assert e and e[0]["denetlenemedi"] is True and e[0]["boyut"] == "mevcut_plan"
    g["donmus_gunler"] = []
    r = degerlendir(g, [_satir("C1", 0, "T08", 12)])
    assert not [x for x in r["eksik_boyutlar"] if x["kural"] == "DONMUS_GUN"]


def test_DONMUS_GUN_ihlali_ASLA_gecmis_sayilmaz():
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", 12)]
    r = degerlendir(g, [_satir("C1", 0, "T06", 10)])      # degistirilmis
    d = [i for i in r["ihlaller"] if i["kural"] == "DONMUS_GUN"]
    assert len(d) == 2 and not any(i.get("gecmis") for i in d)
    assert r["yayin_kapisi"]["yayinlanabilir"] is False
    assert d[0] in r["yayin_kapisi"]["engelleyen_ihlaller"]


def test_donmus_ile_SERBEST_gun_arasindaki_ihlal_gecmis_sayilMAZ():
    """Gun 0 (donmus) 16-24, gun 1 (serbest) 06-14: 6 saat dinlenme -> gelecek degisebilir."""
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T16", 20)]
    plan = [_satir("C1", 0, "T16", 20), _satir("C1", 1, "T06", 10)]
    r = degerlendir(g, plan)
    dinlenme = [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ARASI_DINLENME"]
    assert dinlenme, "6 saat dinlenme ihlal olmali"
    assert not any(i.get("gecmis") for i in dinlenme), dinlenme
    assert r["yayin_kapisi"]["yayinlanabilir"] is False


def test_yalniz_donmus_gune_dayanan_ihlal_GECMIS_isaretlenir_kapi_saymaz():
    """Gun 0'da iki vardiya ust uste (yonetici yazmis): CAKISMA/GUNLUK gecmis."""
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T06", 10), _satir("C1", 0, "T08", 12)]
    plan = copy.deepcopy(g["mevcut_plan"]) + [_satir("C2", 1, "T08", 12)]
    r = degerlendir(g, plan)
    sert = [i for i in r["ihlaller"] if i["agirlik"] == "SERT" and i.get("gun") == 0]
    assert sert, "gun 0'da sert ihlal bekleniyordu (cakisma / gunluk azami)"
    assert all(i.get("gecmis") for i in sert), [i for i in sert if not i.get("gecmis")]
    assert r["metrikler"]["sert_ihlal"] == len([i for i in r["ihlaller"]
                                              if i["agirlik"] == "SERT" and not i.get("gecmis")])
    assert r["yayin_kapisi"]["gecmis_sert_ihlal"] == len(sert)
    assert r["gecmis_ihlaller"] == sert


def test_mola_aday_noktasina_OTURMAYAN_plan_cozumsuz_etmez_not_duser():
    """Yonetici yemegi 09:10'a yazmis (aday degil): satir aynen gecer, model cozulur."""
    g = _sahne()
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T08", yemek_bas=9.17)]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("durum")
    gun0 = [a for a in c["atamalar"] if a["gun"] == 0]
    assert len(gun0) == 1 and gun0[0]["molalar"][0]["bas"] == 9.17
    assert any("aday noktalarina oturmadi" in n for n in c["uygulanmayan_notlar"]), \
        c["uygulanmayan_notlar"]


def test_donmus_gece_vardiyasi_ertesi_gunun_erken_vardiyasini_IMKANSIZ_kilar():
    """Gun 1'de 06-14'u yalniz C1 alabilir (C2 o gun uygun degil); C1 gun 0'da
    16-24 calismis -> 11 saat dinlenme 06:00'ya izin vermez -> plan YOK.

    Donmus gun sayilmasaydi motor C1'i 06-14'e yazar ve "cozuldu" derdi;
    o plan dogrulayicida dinlenme ihlali verirdi. Gecmis gercekten sayiliyor.
    """
    g = _sahne(kisi=2, saatler=(6, 14))
    g["talep"] = [t for t in g["talep"] if t["gun"] == 1]
    g["calisanlar"][1]["uygunluk"] = [{"tip": "uygun_degil", "gun": 1, "bas": 0, "bit": 24}]
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = [_satir("C1", 0, "T16", yemek_bas=_yemek_adayi(g, "T16"))]
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", (c.get("durum"), [a for a in c.get("atamalar", []) if a["gun"] == 1])
