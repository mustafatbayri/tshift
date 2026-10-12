# -*- coding: utf-8 -*-
"""
VARDIYA_ROTASYON_YONU -- vardiya saati ileri kaysin, geriye degil (K-65, 11 Ekim 2026)

SARTNAME #6.3 tek satirdi: "Vardiya saati ileri kaysin (sabah->aksam->gece),
geriye degil. Uyku sagligi literaturunde standart." Motorda ve dogrulayicida
govdesi yoktu (K-49 ile "rapor" kademesinde). Mustafa'nin uc karari (8 ve 11
Ekim; literatur okumasi 02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md):

  1. GERI = ayni kisinin ART ARDA IKI CALISMA GUNUNDE sonraki vardiyanin
     baslangici oncekinden ERKEN. Fark 24 saatlik CEMBERDE okunur ((-12, 12]):
     08:00 -> ertesi gun 23:00 = +15 degil -9, yani GERI (sabah->gece atlamasi;
     IARC 2020 madde 8). Mustafa: "dairesel, evet".
  2. BOS GUN SIFIRLAR: araya bos gun girince kiyas yok.
  3. CEZA = agirlik x GERI KAYDIRILAN SAAT (Mustafa: "onerin"). Motor tam sayi
     ister: saat EN YAKIN TAM SAATE yuvarlanir (2,75 -> 3); dogrulayici ve
     metrik KESIN saati yazar.
  Pazar->Pazartesi: gecmis gun -1 kaydi varsa sayilir, yoksa sessizce atlanir.
  K-54: iki gunu de donmus cift amac terimine girmez; dogrulayici onu "gecmis"
  isaretler.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_rotasyon_yonu.py -v
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz, _CEZA_ONEKI                       # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU, rotasyon_geri_saat   # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici.kurallar import _rotasyon_geri_saat          # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5, "iki_asama_esigi": 10 ** 9, "isci_sayisi": 2}

SABAH = {"id": "SABAH", "ekip": "E", "bas": 7, "bit": 15, "mola_dk": 60}
ORTA = {"id": "ORTA", "ekip": "E", "bas": 10, "bit": 18, "mola_dk": 60}
AKSAM = {"id": "AKSAM", "ekip": "E", "bas": 13.75, "bit": 22, "mola_dk": 60}
GECE = {"id": "GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(talep, rotasyon=True, profil="DENGELI", sablonlar=(SABAH, ORTA, AKSAM, GECE), **ek):
    """Tek kisi, tek ekip. `talep`: [(gun, saat), ...] -- o saatte asgari 1 / hedef 1."""
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HEDEF_ASIMI", tur="YUMUSAK"), _kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=11)]
    if rotasyon:
        kurallar.append(_kural("VARDIYA_ROTASYON_YONU", tur="YUMUSAK", **ek.pop("rotasyon_par", {})))
    g = {"profil": profil,
         "calisanlar": [{"id": "P1", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
                         "izinler": [], "uygunluk": []}],
         "vardiya_sablonlari": [dict(t) for t in sablonlar],
         "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1} for d, s in talep],
         "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}
    g.update(ek)
    return g


def _atama(gun, sablon, kisi="P1"):
    return {"calisan": kisi, "ekip": "E", "sablon": sablon["id"], "gun": gun,
            "bas": sablon["bas"], "bit": sablon["bit"], "molalar": []}


def _ihlaller(r):
    return [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ROTASYON_YONU"]


def _rot(c):
    return c["cozum_istatistikleri"]["amac_dagilimi"].get("VARDIYA_ROTASYON_YONU")


# ----------------------------------------------------------------------
# 1. Tanim: dairesel fark -- iki taraf ayni, ayri yazili (#7.6)
# ----------------------------------------------------------------------

def test_dairesel_geri_saat_tanimi_motor_ve_dogrulayici_AYNI_sonucu_verir():
    cases = {(13.75, 11): 2.75, (10, 13.75): 0, (9, 0): 9, (8, 23): 9, (23, 7): 0, (7, 7): 0,
             (8, 20): 0, (20, 8): 0, (23, 13.75): 9.25, (11.25, 8): 3.25, (24.5, 7): 0, (22, 9): 0}
    for (a, b), beklenen in cases.items():
        assert rotasyon_geri_saat(a, b) == beklenen == _rotasyon_geri_saat(a, b), (a, b)
    # sabah->gece atlamasi GERI (IARC madde 8): duz fark +15 olsaydi "ileri" cikardi
    assert rotasyon_geri_saat(8, 23) == 9 and _rotasyon_geri_saat(8, 23) == 9
    # yon=geri: isaret ters -- ileri kaymalar cezalanir
    assert rotasyon_geri_saat(7, 10, "geri") == 3 == _rotasyon_geri_saat(7, 10, "geri")
    assert rotasyon_geri_saat(10, 7, "geri") == 0 == _rotasyon_geri_saat(10, 7, "geri")


# ----------------------------------------------------------------------
# 2. Dogrulayici
# ----------------------------------------------------------------------

def test_dogrulayici_geri_gecis_YUMUSAK_ihlal_kesin_saat_ikinci_gun():
    g = _sahne([])
    r = degerlendir(g, [_atama(0, AKSAM), _atama(1, ORTA), _atama(2, SABAH)])
    ih = _ihlaller(r)
    assert [(i["gun"], i["olculen"], i["gereken"], i["agirlik"]) for i in ih] == [(1, 3.75, 0, "YUMUSAK"), (2, 3, 0, "YUMUSAK")]
    assert "13:45 -> gun 1 10" in ih[0]["mesaj"] and "3.75 saat geri" in ih[0]["mesaj"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True                 # yumusak: kapi kapanmaz
    assert "VARDIYA_ROTASYON_YONU" not in r["uygulanmayan_kurallar"]  # govde var (K-49 "rapor" kademesinden cikti)
    assert not [d for d in r["yayin_kapisi"]["denetlenemeyen_kurallar"] if d["kod"] == "VARDIYA_ROTASYON_YONU"]


def test_dogrulayici_ileri_ve_ayni_saat_ihlal_DEGIL_bos_gun_SIFIRLAR():
    g = _sahne([])
    assert _ihlaller(degerlendir(g, [_atama(0, SABAH), _atama(1, ORTA), _atama(2, AKSAM), _atama(3, AKSAM)])) == []
    # Pzt aksam, Sali bos, Car sabah: bos gun sifirlar
    assert _ihlaller(degerlendir(g, [_atama(0, AKSAM), _atama(2, SABAH)])) == []


def test_dogrulayici_sabah_gece_atlamasi_GERI_dairesel():
    g = _sahne([])
    ih = _ihlaller(degerlendir(g, [_atama(0, SABAH), _atama(1, GECE)]))
    assert [(i["gun"], i["olculen"]) for i in ih] == [(1, 8)]        # 07:00 -> 23:00: +16 = -8
    # gece -> (ertesi gun bos: gece sabahi kaplar) -> sabah: cift yok
    assert _ihlaller(degerlendir(g, [_atama(0, GECE), _atama(2, SABAH)])) == []


def test_dogrulayici_pazar_pazartesi_gecmis_gun_eksi_bir_varsa_sayilir_yoksa_SESSIZ():
    g = _sahne([])
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 22}]
    r = degerlendir(g, [_atama(0, SABAH)])
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(r)] == [(0, 6.75)]
    assert not [e for e in r["gecmis_eksik"] if e["kural"] == "VARDIYA_ROTASYON_YONU"]
    g2 = _sahne([])
    r2 = degerlendir(g2, [_atama(0, SABAH)])
    assert _ihlaller(r2) == [] and not [e for e in r2["gecmis_eksik"] if e["kural"] == "VARDIYA_ROTASYON_YONU"]
    # gun -2 kaydi pazartesiyle art arda degil
    g3 = _sahne([])
    g3["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -2, "bas": 13.75, "bit": 22}]
    assert _ihlaller(degerlendir(g3, [_atama(0, SABAH)])) == []


def test_dogrulayici_yon_geri_isareti_cevirir_bilinmeyen_yon_ileri_sayilir():
    g = _sahne([], rotasyon_par={"yon": "geri"})
    ih = _ihlaller(degerlendir(g, [_atama(0, SABAH), _atama(1, ORTA)]))
    assert [(i["gun"], i["olculen"]) for i in ih] == [(1, 3)] and "yon=geri" in ih[0]["mesaj"]
    assert _ihlaller(degerlendir(g, [_atama(0, ORTA), _atama(1, SABAH)])) == []
    g2 = _sahne([], rotasyon_par={"yon": "saga"})
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g2, [_atama(0, ORTA), _atama(1, SABAH)]))] == [(1, 3)]


def test_dogrulayici_kural_yokken_yazmaz():
    r = degerlendir(_sahne([], rotasyon=False), [_atama(0, AKSAM), _atama(1, SABAH)])
    assert _ihlaller(r) == []


def test_dogrulayici_K54_iki_gunu_donmus_cift_GECMIS_isaretli_donmus_serbest_cifti_degil():
    plan = [_atama(0, AKSAM), _atama(1, SABAH), _atama(2, SABAH), _atama(3, ORTA), _atama(4, SABAH)]
    g = _sahne([], donmus_gunler=[0, 1], mevcut_plan=copy.deepcopy(plan[:2]))
    r = degerlendir(g, plan)
    ih = {i["gun"]: i for i in _ihlaller(r)}
    assert sorted(ih) == [1, 4]
    assert ih[1].get("gecmis") is True and not ih[4].get("gecmis")


# ----------------------------------------------------------------------
# 3. Motor -- amac terimi
# ----------------------------------------------------------------------

def test_motor_zorunlu_geri_gecisin_bedeli_agirlik_x_YUVARLANMIS_saat_metrik_KESIN():
    # gun 0 yalniz AKSAM (13:45) kapatir (saat 20); gun 1'de saat 10 VE 16 yalniz ORTA (10:00)
    # ile kapanir (SABAH 16'yi, AKSAM 10'u kapatmaz): 13:45 -> 10:00 = 3,75 saat geri
    # -> amacta 4 x agirlik (yuvarlanmis); metrik 3,75 (kesin)
    g = _sahne([(0, 20), (1, 10), (1, 16)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    plan = {a["gun"]: a["sablon"] for a in c["atamalar"]}
    assert plan == {0: "AKSAM", 1: "ORTA"}
    rot = _rot(c)
    assert rot == {"ceza": 4 * AGIRLIK_TABLOSU["VARDIYA_ROTASYON_YONU"]["DENGELI"], "deger": 4,
                   "degisken": rot["degisken"], "pay_yuzde": rot["pay_yuzde"]}
    assert c["metrikler"]["rotasyon_geri_gecis"] == 1 and c["metrikler"]["rotasyon_geri_saat"] == 3.75
    ih = _ihlaller(degerlendir(g, c["atamalar"]))
    assert [(i["gun"], i["olculen"]) for i in ih] == [(1, 3.75)]
    assert _CEZA_ONEKI["ro"] == "VARDIYA_ROTASYON_YONU"


def test_motor_secim_varken_GERI_olmayani_secer():
    # gun 0 yalniz AKSAM; gun 1 saat 16-17 ORTA (10:00, geri 3,75) ya da AKSAM (13:45, ayni saat) kapatir
    g = _sahne([(0, 20), (1, 16), (1, 17)], sablonlar=(SABAH, ORTA, AKSAM))
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "AKSAM", 1: "AKSAM"}
    assert c["metrikler"]["rotasyon_geri_gecis"] == 0 and c["metrikler"]["rotasyon_geri_saat"] == 0
    assert _rot(c)["ceza"] == 0


def test_motor_sabah_gece_atlamasi_dairesel_8_saat_geri():
    # gun 0 yalniz SABAH (saat 8), gun 1 yalniz GECE (saat 23): 07:00 -> 23:00 = 8 saat geri
    g = _sahne([(0, 8), (1, 23)])
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "SABAH", 1: "GECE"}
    assert _rot(c)["deger"] == 8 and c["metrikler"]["rotasyon_geri_saat"] == 8


def test_motor_bos_gun_sifirlar_ve_ileri_gecis_cezasiz():
    g = _sahne([(0, 20), (2, 8)])                  # AKSAM, bos, SABAH
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "AKSAM", 2: "SABAH"}
    assert c["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c) is None or _rot(c)["ceza"] == 0)
    g2 = _sahne([(0, 8), (1, 20)])                 # SABAH -> AKSAM: ileri
    c2 = coz(g2, AYAR)
    assert c2["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c2) is None or _rot(c2)["ceza"] == 0)


def test_motor_pazar_pazartesi_gecmisle_sayilir_gecmissiz_sayilmaz():
    g = _sahne([(0, 8)])                            # yalniz SABAH kapatir
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]   # bitis 20: 11 saat dinlenme tutar
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("teshis")
    assert _rot(c)["deger"] == 7 and c["metrikler"]["rotasyon_geri_saat"] == 6.75     # 13:45 -> 07:00
    assert c["metrikler"]["rotasyon_geri_gecis"] == 1
    c2 = coz(_sahne([(0, 8)]), AYAR)
    assert c2["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c2) is None or _rot(c2)["ceza"] == 0)
    # pazartesi teriminde de tam ,5 YUKARI: gun -1 09:30 -> SABAH 07:00 = 2,5 -> 3 (bankaci 2 olurdu)
    g3 = _sahne([(0, 8)])
    g3["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 9.5, "bit": 17.5}]
    c3 = coz(g3, AYAR)
    assert _rot(c3)["deger"] == 3 and c3["metrikler"]["rotasyon_geri_saat"] == 2.5


def test_motor_agirlik_profilden_ve_kiracidan_sifir_agirlik_kurali_susturur():
    g = _sahne([(0, 20), (1, 10), (1, 16)], profil="CALISAN")
    c = coz(g, AYAR)
    assert _rot(c)["ceza"] == 4 * AGIRLIK_TABLOSU["VARDIYA_ROTASYON_YONU"]["CALISAN"]
    g0 = _sahne([(0, 20), (1, 10), (1, 16)], agirliklar={"VARDIYA_ROTASYON_YONU": 0})
    c0 = coz(g0, AYAR)
    assert _rot(c0)["ceza"] == 0                                       # terim var, bedeli yok
    # agirlik 0 iken degisken serbest kalir (cozucu 0..12'de herhangi bir deger birakabilir):
    # `deger` None yazilir (inceleme 4, B9) -- plani anlatan sayi metriktir
    assert _rot(c0)["deger"] is None and _rot(c0)["pay_yuzde"] == 0
    assert c0["metrikler"]["rotasyon_geri_gecis"] == 1 and c0["metrikler"]["rotasyon_geri_saat"] == 3.75


def test_motor_kural_yokken_terim_ve_metrik_YOK():
    g = _sahne([(0, 20), (1, 10), (1, 16)], rotasyon=False)
    k = Model(copy.deepcopy(g)).kur()
    assert k.rotasyon == {} and not [v for _, v in k.cezalar if v.Name().startswith("ro_")]
    c = coz(g, AYAR)
    assert c["metrikler"]["rotasyon_geri_gecis"] is None and c["metrikler"]["rotasyon_geri_saat"] is None
    assert "VARDIYA_ROTASYON_YONU" not in c["cozum_istatistikleri"]["amac_dagilimi"]


def test_motor_yon_geri_ileri_kaymayi_cezalar_bilinmeyen_yon_not_duser():
    g = _sahne([(0, 8), (1, 16), (1, 17)], rotasyon_par={"yon": "geri"}, sablonlar=(SABAH, ORTA))
    c = coz(g, AYAR)                                 # SABAH -> ORTA zorunlu: ileri 3 -> yon=geri ile ceza
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "SABAH", 1: "ORTA"}
    assert _rot(c)["deger"] == 3 and c["metrikler"]["rotasyon_geri_saat"] == 3
    g2 = _sahne([(0, 20), (1, 10), (1, 16)], rotasyon_par={"yon": "saga"})
    c2 = coz(g2, AYAR)
    assert _rot(c2)["deger"] == 4
    assert any("yon 'saga' taninmadi" in n for n in c2["uygulanmayan_notlar"])


def test_motor_K54_iki_donmus_gunun_cifti_terime_girmez_donmus_serbest_girer():
    plan = [_atama(0, AKSAM), _atama(1, SABAH)]
    g = _sahne([(0, 20), (1, 8), (2, 8)], donmus_gunler=[0, 1], mevcut_plan=copy.deepcopy(plan))
    k = Model(copy.deepcopy(g)).kur()
    assert ("P1", 0) not in k.rotasyon and ("P1", 1) in k.rotasyon
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "AKSAM", 1: "SABAH", 2: "SABAH"}
    assert _rot(c)["deger"] == 0                      # SABAH -> SABAH: 0; donmus cift sayilmadi
    assert c["metrikler"]["rotasyon_geri_gecis"] == 1  # metrik plani anlatir: AKSAM -> SABAH (gecmis)


def test_motor_kisit_sayisi_yalniz_geri_ciftler_icin_yazilir():
    """Kurulum bedeli: kisi basina gun cifti x GERI sablon cifti kadar kisit, carpim degiskeni yok."""
    g = _sahne([], sablonlar=(SABAH, ORTA, AKSAM, GECE))
    k = Model(copy.deepcopy(g)).kur()
    # 4 sablon: geri ciftler (s->t, geri>0): ORTA->SABAH 3, AKSAM->SABAH 6.75, AKSAM->ORTA 3.75,
    # GECE->ORTA? 23->10: +11 ileri; GECE->SABAH 23->7: +8 ileri; GECE->AKSAM 23->13.75: -9.25 geri;
    # SABAH->GECE 7->23: -8 geri; ORTA->GECE 10->23: +13 -> -11 geri; AKSAM->GECE 13.75->23: +9.25 ileri
    # -> 6 geri cift; 6 gun cifti -> 36 kisit, 6 degisken
    assert len(k.rotasyon) == 6
    assert len([v for _, v in k.cezalar if v.Name().startswith("ro_")]) == 6


# ----------------------------------------------------------------------
# 4. Inceleme 4'un bulduklari (11 Ekim, B5): yuvarlama kenarlari, ilk baslangic,
#    alan siniri, donmus pazartesi, pasif kisi, aktif:false, 1 saatlik cift
# ----------------------------------------------------------------------

SABAH_YARIM = {"id": "SABAH_YARIM", "ekip": "E", "bas": 7.5, "bit": 15.5, "mola_dk": 60}     # 10 -> 7.5 = 2,5
SABAH_CEYREK = {"id": "SABAH_CEYREK", "ekip": "E", "bas": 7.75, "bit": 15.75, "mola_dk": 60}  # 10 -> 7.75 = 2,25
ORTA_CEYREK = {"id": "ORTA_CEYREK", "ekip": "E", "bas": 9.75, "bit": 17.75, "mola_dk": 60}    # 10 -> 9.75 = 0,25
SEKIZ = {"id": "SEKIZ", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60}                      # 8 -> 7 = 1
GEC_AKSAM = {"id": "GEC_AKSAM", "ekip": "E", "bas": 21.75, "bit": 22.75, "mola_dk": 0}        # 1 saatlik; 21.75 -> 10 = -11,75 (11 sa dinlenme tutar)


def _zorunlu(gun0_saat, gun1_saatler, sablonlar, **ek):
    """gun 0'da `gun0_saat`, gun 1'de `gun1_saatler` zorunlu (asgari 1)."""
    return _sahne([(0, gun0_saat)] + [(1, h) for h in gun1_saatler], sablonlar=sablonlar, **ek)


def test_motor_tam_yarim_saat_YUKARI_yuvarlanir_bankaci_degil():
    # ORTA (10:00) -> SABAH_YARIM (07:30) = 2,5 saat: int(h + 0.5) = 3; round(2.5) = 2 olurdu
    g = _zorunlu(16, [8, 15], (ORTA, SABAH_YARIM))        # gun 0: saat 16 yalniz ORTA; gun 1: 8 ve 15 yalniz SABAH_YARIM
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "ORTA", 1: "SABAH_YARIM"}
    assert _rot(c)["deger"] == 3 and c["metrikler"]["rotasyon_geri_saat"] == 2.5


def test_motor_yarimdan_kucuk_kesir_ASAGI_yuvarlanir_ceyrek_geri_sifir():
    # ORTA (10:00) -> SABAH_CEYREK (07:45) = 2,25 -> 2 (hep yukari olsaydi 3)
    g = _zorunlu(16, [8, 15], (ORTA, SABAH_CEYREK))
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "ORTA", 1: "SABAH_CEYREK"}
    assert _rot(c)["deger"] == 2 and c["metrikler"]["rotasyon_geri_saat"] == 2.25
    # ORTA (10:00) -> ORTA_CEYREK (09:45) = 0,25: motor 0 -- geri cift YOK, terim hic kurulmaz;
    # dogrulayici satiri 0.25, metrik 0.25 (kesin)
    from cozucu.coz import _rotasyon_metrigi
    g2 = _sahne([], sablonlar=(ORTA, ORTA_CEYREK))
    k = Model(copy.deepcopy(g2)).kur()
    assert k.rotasyon == {}
    plan = [_atama(0, ORTA), _atama(1, ORTA_CEYREK)]
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g2, plan))] == [(1, 0.25)]
    assert _rotasyon_metrigi(k, plan) == (1, 0.25)


def test_motor_bir_saatlik_geri_cift_de_cezalanir():
    # SEKIZ (08:00) -> SABAH (07:00) = 1 saat: deger 1
    g = _zorunlu(15, [7], (SABAH, SEKIZ))                 # gun 0 saat 15 yalniz SEKIZ (SABAH 15'te biter); gun 1 saat 7 yalniz SABAH
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "SEKIZ", 1: "SABAH"}
    assert _rot(c)["deger"] == 1 and c["metrikler"]["rotasyon_geri_saat"] == 1


def test_motor_geri_saat_alani_12_ye_kadar_yon_geri_ile_tam_12():
    # yon=geri: SEKIZ (08:00) -> 20:00 baslayan sablon = +12 -> isaret ters -> 12 saat "geri"; alan 0..12 yeter
    YIRMI = {"id": "YIRMI", "ekip": "E", "bas": 20, "bit": 28, "mola_dk": 60}
    g = _zorunlu(15, [21], (SEKIZ, YIRMI), rotasyon_par={"yon": "geri"})
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "SEKIZ", 1: "YIRMI"}
    assert _rot(c)["deger"] == 12 and c["metrikler"]["rotasyon_geri_saat"] == 12
    # 11,75 de 12'ye yuvarlanir (yon=ileri): GEC_AKSAM (21:45, 1 saat) -> ORTA (10:00) = -11,75 -> 12
    g2 = _zorunlu(22, [16], (ORTA, GEC_AKSAM))            # gun 0 saat 22 yalniz GEC_AKSAM; gun 1 saat 16 yalniz ORTA
    c2 = coz(g2, AYAR)
    assert {a["gun"]: a["sablon"] for a in c2["atamalar"]} == {0: "GEC_AKSAM", 1: "ORTA"}
    assert _rot(c2)["deger"] == 12 and c2["metrikler"]["rotasyon_geri_saat"] == 11.75


def test_ayni_gunde_iki_kayit_ILK_BASLANGIC_alinir_dogrulayici_metrik_ve_motor():
    from cozucu.coz import _rotasyon_metrigi
    g = _sahne([])
    # gun 0'da iki satir (13:45 ve 07:00) -> ilk baslangic 07:00; gun 1 ORTA 10:00 -> ileri, satir yok
    plan = [_atama(0, AKSAM), _atama(0, SABAH), _atama(1, ORTA)]
    assert _ihlaller(degerlendir(g, plan)) == []
    k = Model(copy.deepcopy(g)).kur()
    assert _rotasyon_metrigi(k, plan) == (0, 0.0)
    # gecmis gun -1'de iki kayit (05:00 ve 13:45) -> ilk baslangic 05:00; gun 0 SABAH 07:00 -> ileri
    g2 = _sahne([(0, 8)])
    g2["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}, {"gun": -1, "bas": 5, "bit": 9}]
    assert _ihlaller(degerlendir(g2, [_atama(0, SABAH)])) == []
    c = coz(g2, AYAR)
    assert c["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c) is None or _rot(c)["deger"] == 0)


def test_gun_0_donmusken_pazartesi_terimi_yazilmaz_dogrulayici_gecmis_isaretler():
    plan = [_atama(0, SABAH)]
    g = _sahne([(0, 8), (1, 8)], donmus_gunler=[0], mevcut_plan=copy.deepcopy(plan))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]
    k = Model(copy.deepcopy(g)).kur()
    assert ("P1", -1) not in k.rotasyon and ("P1", 0) in k.rotasyon      # 0 donmus -> (-1,0) yok; (0,1) var
    c = coz(g, AYAR)
    assert c["metrikler"]["rotasyon_geri_gecis"] == 1                   # metrik plani anlatir: 13:45 -> 07:00
    r = degerlendir(g, c["atamalar"])
    ih = _ihlaller(r)
    assert [(i["gun"], i["olculen"], i.get("gecmis")) for i in ih] == [(0, 6.75, True)]


def test_pasif_calisanin_aktarilan_donmus_satiri_metrikte_de_sayilir():
    from cozucu.coz import _rotasyon_metrigi
    plan = [_atama(0, AKSAM, "P2"), _atama(1, SABAH, "P2")]
    g = _sahne([], donmus_gunler=[0, 1], mevcut_plan=copy.deepcopy(plan))
    g["calisanlar"].append({"id": "P2", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"}, "durum": "pasif",
                            "izinler": [], "uygunluk": [],
                            "gecmis_vardiyalar": [{"gun": -1, "bas": 15, "bit": 20}]})
    k = Model(copy.deepcopy(g)).kur()
    assert [c["id"] for c in k.calisanlar] == ["P1"]                   # pasif modele girmez (AKTIF_CALISAN)
    gecis, saat = _rotasyon_metrigi(k, plan)
    assert (gecis, saat) == (2, 8.0)                                   # 15:00 -> 13:45 (1,25) ve 13:45 -> 07:00 (6,75)
    # dogrulayici da ayni iki satir
    ih = _ihlaller(degerlendir(g, plan))
    assert [(i["calisan"], i["gun"], i["olculen"]) for i in ih] == [("P2", 0, 1.25), ("P2", 1, 6.75)]


def test_kural_aktif_false_terim_metrik_satir_YOK():
    g = _sahne([(0, 20), (1, 10), (1, 16)])
    for k in g["kurallar"]:
        if k["kod"] == "VARDIYA_ROTASYON_YONU":
            k["aktif"] = False
    m = Model(copy.deepcopy(g)).kur()
    assert m.rotasyon == {} and not [v for _, v in m.cezalar if v.Name().startswith("ro_")]
    c = coz(g, AYAR)
    assert c["metrikler"]["rotasyon_geri_gecis"] is None
    assert "VARDIYA_ROTASYON_YONU" not in c["cozum_istatistikleri"]["amac_dagilimi"]
    assert _ihlaller(degerlendir(g, c["atamalar"])) == []
