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
  2. BOS GUN SIFIRLAR: araya bos gun girince kiyas yok. Gun tanimi D (12 Ekim):
     gece yarisini asan vardiya bittigi gune de aittir -- o gun "bos" degildir
     (bolum 5).
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
    # gece -> (gun 1: gece sabahina dokunur, D) -> gun 2 sabah: cift VAR ama 23:00 -> 07:00 ILERI (+8)
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


# ----------------------------------------------------------------------
# 5. Gun tanimi D (Mustafa, 12 Ekim 2026; K-65 madde 1 degisti, inceleme 4 B8):
#    vardiya BASLADIGI gune ve gece yarisini asiyorsa BITTIGI gune de aittir;
#    ardisik iki vardiya, ikincisi birincinin son gununde ya da ertesinde
#    basliyorsa kiyaslanir; arada dokunulmamis takvim gunu varsa sifirlanir.
#    Yon ve ceza aynen (baslangictan). Kabul olcutleri 1-8 (12 Ekim 17:06 onayi).
# ----------------------------------------------------------------------

GEC_BITEN = {"id": "GEC_BITEN", "ekip": "E", "bas": 16, "bit": 24, "mola_dk": 60}      # TAM 24:00: asmaz
ORTA_D = {"id": "ORTA_D", "ekip": "E", "bas": 9.75, "bit": 18, "mola_dk": 60}          # 23 -> 9.75: ileri 10,75
AKSAM_D = {"id": "AKSAM_D", "ekip": "E", "bas": 14, "bit": 22, "mola_dk": 60}          # 23 -> 14: geri 9; ORTA_D'den kisa


def test_D_olcut1_gece_bos_gorunen_gun_aksam_KIYASLANIR_dogrulayici_ve_metrik():
    """Sali 23:00-07:00 gecesi, Carsamba bos, Persembe 13:45: Carsamba geceye dokundu -> cift; 9,25 saat geri."""
    from cozucu.coz import _rotasyon_metrigi
    g = _sahne([])
    plan = [_atama(0, GECE), _atama(2, AKSAM)]
    ih = _ihlaller(degerlendir(g, plan))
    assert [(i["gun"], i["olculen"]) for i in ih] == [(2, 9.25)]
    assert "gun 0 23 -> gun 2 13:45, 9.25 saat geri" in ih[0]["mesaj"]
    assert _rotasyon_metrigi(Model(copy.deepcopy(g)).kur(), plan) == (1, 9.25)


def test_D_olcut2_ve_3_gece_yarisini_ASMAYAN_ve_TAM_24te_biten_bos_gunle_SIFIRLANIR():
    from cozucu.coz import _rotasyon_metrigi
    from cozucu.model import gece_yarisini_asar
    from dogrulayici.kurallar import _rotasyon_son_gun
    g = _sahne([], sablonlar=(SABAH, AKSAM, GECE, GEC_BITEN))
    k = Model(copy.deepcopy(g)).kur()
    for plan in ([_atama(0, AKSAM), _atama(2, SABAH)],          # 13:45-22:00, bos, 07:00
                 [_atama(0, GEC_BITEN), _atama(2, SABAH)]):     # 16:00-24:00, bos, 07:00 (9 saat geri olurdu)
        assert _ihlaller(degerlendir(g, plan)) == []
        assert _rotasyon_metrigi(k, plan) == (0, 0.0)
    # tanim iki tarafta ayni (ayri yazili): 24 asmaz, 24,25 asar, ham yazim 23 -> 7 asar
    for (b, e), asar in {(16, 24): False, (16, 24.25): True, (23, 7): True, (23, 31): True,
                         (0, 8): False, (13.75, 22): False}.items():
        assert gece_yarisini_asar(b, e) is asar and _rotasyon_son_gun(5, b, e) == 5 + int(asar), (b, e)


def test_D_olcut4_geceden_sonra_IKI_bos_gun_SIFIRLAR():
    g = _sahne([])
    assert _ihlaller(degerlendir(g, [_atama(0, GECE), _atama(3, AKSAM)])) == []


def test_D_olcut5_ara_gunde_calisiyorsa_ciftler_ardisik_gunlerdir():
    """Gece d, d+1'de calisiyor: ciftler (d, d+1) ve (d+1, d+2); d -> d+2 ayrica sayilmaz."""
    g = _sahne([])
    plan = [_atama(0, GECE), _atama(1, GECE), _atama(2, AKSAM)]   # 23 -> 23 (0), 23 -> 13:45 (9,25)
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g, plan))] == [(2, 9.25)]


def test_D_olcut1_motor_zorunlu_ciftte_bedel_ara_gunun_degiskeninde():
    # gun 0 saat 23 yalniz GECE; gun 2 saat 20 yalniz AKSAM; gun 1 talepsiz
    g = _sahne([(0, 23), (2, 20)], sablonlar=(SABAH, AKSAM, GECE))
    k = Model(copy.deepcopy(g)).kur()
    assert ("P1", 1) in k.rotasyon                                   # ro_P1_1 yeniden kullanilir
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "GECE", 2: "AKSAM"}
    assert _rot(c)["deger"] == 9 and _rot(c)["ceza"] == 9 * AGIRLIK_TABLOSU["VARDIYA_ROTASYON_YONU"]["DENGELI"]
    assert c["metrikler"]["rotasyon_geri_gecis"] == 1 and c["metrikler"]["rotasyon_geri_saat"] == 9.25
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g, c["atamalar"]))] == [(2, 9.25)]


def test_D_olcut7_motor_secim_varken_geceden_sonra_GERI_olmayani_secer():
    """Gun 2 saat 17: ORTA_D (09:45, gece 23:00'ten ILERI) ya da AKSAM_D (14:00, 9 saat GERI).
    AKSAM_D bir ceyrek kisa (hedef asimi ucuz) -- D olmasaydi motor onu secerdi."""
    g = _sahne([(0, 23), (2, 17)], sablonlar=(GECE, ORTA_D, AKSAM_D))
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "GECE", 2: "ORTA_D"}
    assert c["metrikler"]["rotasyon_geri_gecis"] == 0 and _rot(c)["ceza"] == 0
    g0 = _sahne([(0, 23), (2, 17)], sablonlar=(GECE, ORTA_D, AKSAM_D), agirliklar={"VARDIYA_ROTASYON_YONU": 0})
    c0 = coz(g0, AYAR)                                                # kanit: kural susunca kisa olan secilir
    assert {a["gun"]: a["sablon"] for a in c0["atamalar"]} == {0: "GECE", 2: "AKSAM_D"}
    assert c0["metrikler"]["rotasyon_geri_gecis"] == 1 and c0["metrikler"]["rotasyon_geri_saat"] == 9


def test_D_ara_gunde_calisilirsa_D_kisiti_SUSAR():
    """Gece d, d+1'de calisiyor, d+2: D kisiti `- calisiyor(d+1)` ile susar; bedel yalniz ardisik ciftlerden.
    Sablonlar gunlere baglandi (`gunler`) ki plan tek olsun: gun 0 N (21:00-05:00), gun 1 X (16:00-24:00;
    05:00'ten 11 saat), gun 2 AKSAM (13:45). Ciftler: N -> X 5 geri, X -> AKSAM 2,25 geri. D cifti
    N -> AKSAM (7,25) EKLENMEZ -- eklenseydi amac terimi 14 olurdu."""
    n = {"id": "N", "ekip": "E", "bas": 21, "bit": 29, "mola_dk": 60, "gunler": [0]}
    x = {"id": "X", "ekip": "E", "bas": 16, "bit": 24, "mola_dk": 60, "gunler": [1]}
    ak = dict(AKSAM, gunler=[2])
    g = _sahne([(0, 23), (1, 20), (2, 21)], sablonlar=(n, x, ak))
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("teshis")
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "N", 1: "X", 2: "AKSAM"}
    assert _rot(c)["deger"] == 5 + 2
    assert c["metrikler"]["rotasyon_geri_gecis"] == 2 and c["metrikler"]["rotasyon_geri_saat"] == 7.25
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g, c["atamalar"]))] == [(1, 5), (2, 2.25)]


def test_D_olcut6a_gecmis_gun_eksi_iki_gecesi_pazar_kaydi_yokken_pazartesiyle_KIYASLANIR():
    g = _sahne([(0, 20)], sablonlar=(SABAH, AKSAM))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -2, "bas": 23, "bit": 31}]     # Cmt 23:00 - Paz 07:00
    r = degerlendir(g, [_atama(0, AKSAM)])
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(r)] == [(0, 9.25)]
    assert not [e for e in r["gecmis_eksik"] if e["kural"] == "VARDIYA_ROTASYON_YONU"]
    c = coz(g, AYAR)
    assert _rot(c)["deger"] == 9 and c["metrikler"]["rotasyon_geri_saat"] == 9.25
    # Pazar kaydi VARSA cift onunla (gun -1 SABAH 07:00 -> 13:45 ileri): satir yok
    g2 = copy.deepcopy(g)
    g2["calisanlar"][0]["gecmis_vardiyalar"].append({"gun": -1, "bas": 7, "bit": 15})
    assert _ihlaller(degerlendir(g2, [_atama(0, AKSAM)])) == []
    c2 = coz(g2, AYAR)
    assert c2["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c2) is None or _rot(c2)["deger"] == 0)
    # gun -2 kaydi gece yarisini ASMIYORSA: sifirlanir (eski test_..._gun_-2 ile ayni)
    g3 = copy.deepcopy(g)
    g3["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -2, "bas": 15, "bit": 23}]
    assert _ihlaller(degerlendir(g3, [_atama(0, AKSAM)])) == []
    c3 = coz(g3, AYAR)
    assert c3["metrikler"]["rotasyon_geri_gecis"] == 0 and (_rot(c3) is None or _rot(c3)["deger"] == 0)


def test_D_olcut6b_gecmis_gun_eksi_bir_gecesi_pazartesi_bosken_saliyla_KIYASLANIR():
    g = _sahne([(1, 20)], sablonlar=(SABAH, AKSAM))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 7}]      # ham yazim (Z-1)
    r = degerlendir(g, [_atama(1, AKSAM)])
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(r)] == [(1, 9.25)]
    k = Model(copy.deepcopy(g)).kur()
    assert ("P1", 0) in k.rotasyon
    c = coz(g, AYAR)
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {1: "AKSAM"}
    assert _rot(c)["deger"] == 9 and c["metrikler"]["rotasyon_geri_saat"] == 9.25


def test_D_olcut6b_pazartesi_CALISIYORSA_gun_eksi_bir_gecesi_saliyla_kiyaslanmaz():
    """Gun -1 23:00-07:00, gun 0 Y 18:00-24:00 (11 saat dinlenme), gun 1 AKSAM 13:45. Ciftler:
    (-1, 0) 23 -> 18 = 5 geri; (0, 1) 18 -> 13:45 = 4,25 geri (4). Gun -1 -> sali D cifti (9,25)
    eklenmez -- eklenseydi amac 5 + 9 = 14 olurdu."""
    y = {"id": "Y", "ekip": "E", "bas": 18, "bit": 24, "mola_dk": 60, "gunler": [0]}
    ak = dict(AKSAM, gunler=[1])
    g = _sahne([(0, 20), (1, 21)], sablonlar=(y, ak))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c.get("teshis")
    assert {a["gun"]: a["sablon"] for a in c["atamalar"]} == {0: "Y", 1: "AKSAM"}
    assert _rot(c)["deger"] == 5 + 4
    assert c["metrikler"]["rotasyon_geri_gecis"] == 2 and c["metrikler"]["rotasyon_geri_saat"] == 9.25
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g, c["atamalar"]))] == [(0, 5), (1, 4.25)]


def test_D_tek_sablonlu_kisinin_gecmis_pazartesi_terimi_motorda_da_var():
    """12 Ekim bulgusu: `if not geri: continue` tek sablonlu kisinin gecmis -> pazartesi terimini
    atliyordu; dogrulayici ve metrik sayiyordu (#7.6 ayriligi)."""
    g = _sahne([(0, 8)], sablonlar=(SABAH,))
    g["calisanlar"][0]["gecmis_vardiyalar"] = [{"gun": -1, "bas": 13.75, "bit": 20}]
    c = coz(g, AYAR)
    assert _rot(c) is not None and _rot(c)["deger"] == 7
    assert c["metrikler"]["rotasyon_geri_saat"] == 6.75
    assert [(i["gun"], i["olculen"]) for i in _ihlaller(degerlendir(g, c["atamalar"]))] == [(0, 6.75)]


def test_D_K54_donmus_gece_serbest_aksam_terime_girer_hepsi_donmusse_GECMIS():
    plan = [_atama(0, GECE), _atama(2, AKSAM)]
    g = _sahne([(0, 23), (2, 20)], sablonlar=(SABAH, AKSAM, GECE), donmus_gunler=[0, 1],
               mevcut_plan=copy.deepcopy(plan[:1]))
    k = Model(copy.deepcopy(g)).kur()
    assert ("P1", 1) in k.rotasyon                                   # donmus -> serbest: girer
    ih = _ihlaller(degerlendir(g, plan))
    assert [(i["gun"], i["olculen"], bool(i.get("gecmis"))) for i in ih] == [(2, 9.25, False)]
    g2 = _sahne([(0, 23), (2, 20)], sablonlar=(SABAH, AKSAM, GECE), donmus_gunler=[0, 1, 2],
                mevcut_plan=copy.deepcopy(plan))
    k2 = Model(copy.deepcopy(g2)).kur()
    assert ("P1", 1) not in k2.rotasyon                              # olan oldu
    ih2 = _ihlaller(degerlendir(g2, plan))
    assert [(i["gun"], i.get("gecmis")) for i in ih2] == [(2, True)]


def test_D_olcut7_rastgele_planlarda_metrik_ve_dogrulayici_AYNI_cifti_sayar():
    """Uc sayim ayni ciftleri sayar: 400 rastgele plan (gece, 24:00'da biten, bos gunler, gecmis
    -1/-2). Motor tarafi yukaridaki zorunlu/secim testlerinde."""
    import random
    from cozucu.coz import _rotasyon_metrigi
    rnd = random.Random(20261012)
    sablonlar = (SABAH, ORTA, AKSAM, GECE, GEC_BITEN)
    for _ in range(400):
        g = _sahne([], sablonlar=sablonlar)
        gecmis = []
        for gun in (-2, -1):
            if rnd.random() < 0.5:
                t = rnd.choice(sablonlar)
                gecmis.append({"gun": gun, "bas": t["bas"], "bit": t["bit"]})
        g["calisanlar"][0]["gecmis_vardiyalar"] = gecmis
        plan = [_atama(d, rnd.choice(sablonlar)) for d in range(7) if rnd.random() < 0.6]
        if not plan:
            continue
        ih = _ihlaller(degerlendir(g, plan))
        gecis, saat = _rotasyon_metrigi(Model(copy.deepcopy(g)).kur(), plan)
        assert (gecis, saat) == (len(ih), round(sum(i["olculen"] for i in ih), 2)), (gecmis, plan)
