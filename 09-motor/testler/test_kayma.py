# -*- coding: utf-8 -*-
"""
VARDIYA KAYMASI -- K-73 (17 Ekim) -- cozucu/kayma.py + model kancalari

Mustafa (17 Ekim 14:46): "oglen 1'deki vardiyada kisi eksik ya, o kisi eksigini yasal
kurallari da dikkate alarak 2 kisinin mesaisini 2 saat uzatir, bir sonraki mesaiye gelecek
kisinin vardiyasini 2 saat erken baslatir."

SAHNE: tek ekip, uc kisi, uc sablon -- S 08-16 (P1), O 12-20 (P3), A 14-22 (P2); hafta ici.
Talep insan planinin sayimi (08-12: 1, 12-14: 2, 14-16: 3, 16-20: 2, 20-22: 1), 14-16'da asgari 2
(oraya kimse eklenemez). Carsamba P3 raporlu:
  * kayma KAPALI -> beden yok, asgari sert -> cozumsuz (kanitli);
  * kayma ACIK   -> P1 08-16 -> 08-20 (gec 4; net 11 = gunluk sinir), P2 14-22 -> 12-22 (erken 2);
                    sert 0; cikti satirlari `kayma` tasir; K-70 iki kisi-gunu DEGISEN sayar.
Kayma kopyalari yalniz etkilenen (ekip, gun)deki kisilere, o gune; yasal sinir net <= 11.
FAZLA_SURELER (olcum kalemi): agirlik 0 -> degisken yok; 42 -> yari zamanlinin sozlesme ustu dakikasi.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_kayma.py -v
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu import kayma as KY                                # noqa: E402
from cozucu.coz import coz, plan_degisikligi                  # noqa: E402
from cozucu.model import Model                                # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

AYAR = {"azami_saniye": 30, "durgunluk_saniye": 5}
SABLONLAR = [{"id": "S", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60},
             {"id": "O", "ekip": "E", "bas": 12, "bit": 20, "mola_dk": 60},
             {"id": "A", "ekip": "E", "bas": 14, "bit": 22, "mola_dk": 60}]
HEDEF = {8: 1, 9: 1, 10: 1, 11: 1, 12: 2, 13: 2, 14: 3, 15: 3, 16: 2, 17: 2, 18: 2, 19: 2, 20: 1, 21: 1}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _plan():
    return [{"calisan": p, "ekip": "E", "sablon": t, "gun": g, "bas": b, "bit": e,
             "molalar": [{"bas": b + 4, "bit": b + 5, "tip": "yemek"}]}
            for p, t, b, e in (("P1", "S", 8, 16), ("P3", "O", 12, 20), ("P2", "A", 14, 22)) for g in range(5)]


def _sahne(sozlesme=None, raporlu=("P3", 2)):
    soz = sozlesme or {"tip": "tam_zamanli", "haftalik_saat": 35, "gun_sayisi": 5}
    talep = []
    for d in range(7):
        for s in range(8, 22):
            h = HEDEF[s] if d < 5 else 0
            talep.append({"ekip": "E", "gun": d, "saat": s, "hedef": h,
                          "asgari": (2 if s in (14, 15) else h) if d < 5 else 0})
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": p, "ekipler": ["E"], "birincil_ekip": "E", "sozlesme": dict(soz),
                         "izinler": [], "uygunluk": []} for p in ("P1", "P2", "P3")],
         "vardiya_sablonlari": copy.deepcopy(SABLONLAR), "talep": talep,
         "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                      _kural("HEDEF_ASIMI", tur="SERT"), _kural("GUNLUK_AZAMI", yasal=True, azami_saat=11),
                      _kural("VARDIYA_ARASI_DINLENME", yasal=True, saat=11),
                      _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10),      # yoksa sozlesme ustu HIC yok (K-38)
                      _kural("HAFTA_TATILI", yasal=True), _kural("PLAN_KARARLILIGI", tur="YUMUSAK")],
         "kilitler": [], "mevcut_plan": _plan()}
    if raporlu:
        kisi, gun = raporlu
        next(c for c in g["calisanlar"] if c["id"] == kisi)["izinler"].append(
            {"gun": gun, "tip": "rapor", "durum": "onayli"})
    return g


def _kaymali(g, tavan=None):
    etk = KY.etkilenen_bul(g, g["mevcut_plan"], [("P3", 2)])
    assert etk == [("E", 2)]
    return KY.kayma_ekle(g, etk, tavan_saat=tavan)


def test_KAYMA_sekiller_ve_yasal_sinir():
    assert KY.kayma_sekilleri(0) == []
    assert KY.kayma_sekilleri(2) == [(0, 1), (1, 0), (0, 2), (1, 1), (2, 0)]
    g = _sahne()
    # S 08-16: brut 8, mola 60 -> net 7; gunluk 11 -> en fazla 4 saat
    assert KY.kayma_azami_saat(g, g["vardiya_sablonlari"][0]) == 4
    g["kurallar"] = [k if k["kod"] != "GUNLUK_AZAMI" else _kural("GUNLUK_AZAMI", yasal=True, azami_saat=9)
                     for k in g["kurallar"]]
    assert KY.kayma_azami_saat(g, g["vardiya_sablonlari"][0]) == 2


def test_KAYMA_kopyalar_yalniz_etkilenen_kisi_gun_ve_alanlar():
    g = _sahne()
    h = _kaymali(g)
    kopyalar = [t for t in h["vardiya_sablonlari"] if t.get("kayma")]
    assert len(h["vardiya_sablonlari"]) == 3 + len(kopyalar) and kopyalar
    # ozgun girdi degismedi
    assert len(g["vardiya_sablonlari"]) == 3 and "_kayma" not in g
    assert h["_kayma"] == {"etkilenen": [["E", 2]], "tavan_saat": None, "sablon": len(kopyalar)}
    # yalniz Carsamba (gun 2) calisan P1 (S) ve P2 (A) -- raporlu P3'un O'su da uretilir (izin kapatir)
    assert {t["kisiler"][0] for t in kopyalar} == {"P1", "P2", "P3"}
    assert all(t["gunler"] == [2] and t["ekip"] == "E" and t["mola_dk"] == 60 for t in kopyalar)
    p1 = [t for t in kopyalar if t["kayma"]["kisi"] == "P1"]
    assert len(p1) == len(KY.kayma_sekilleri(4)) == 14
    uzun = next(t for t in p1 if t["kayma"] == {"taban": "S", "kisi": "P1", "gun": 2, "erken": 0, "gec": 4, "saat": 4})
    assert (uzun["bas"], uzun["bit"]) == (8.0, 20.0) and uzun["id"] == "S~k~P1~g2~e0~u4"
    assert uzun["gece_vardiyasi"] is False
    # tavan OLCUM icin: 1 saat -> kisi basina iki kopya
    h1 = _kaymali(g, tavan=1)
    assert sorted((t["kayma"]["erken"], t["kayma"]["gec"]) for t in h1["vardiya_sablonlari"]
                  if t.get("kayma") and t["kayma"]["kisi"] == "P1") == [(0, 1), (1, 0)]
    # raporlu kisi o gun planda calismiyorsa etkilenen cift YOK (Cumartesi kimse yok)
    assert KY.etkilenen_bul(g, g["mevcut_plan"], [("P3", 5)]) == []
    assert KY.etkilenen_bul(g, g["mevcut_plan"], [("P3", 2), ("P1", 2), ("P2", 4)]) == [("E", 2), ("E", 4)]
    # etkilenen cift yoksa kopya yok
    bos = KY.kayma_ekle(g, [])
    assert len(bos["vardiya_sablonlari"]) == 3 and bos["_kayma"]["sablon"] == 0
    # gece yarisinda baslayan vardiya ERKEN baslayamaz (gun oncesi modelde yok): yalniz gec kopyalar
    gn = copy.deepcopy(g)
    gn["vardiya_sablonlari"].append({"id": "N", "ekip": "E", "bas": 0, "bit": 8, "mola_dk": 60})
    plan_n = [{"calisan": "P1", "ekip": "E", "sablon": "N", "gun": 2, "bas": 0, "bit": 8, "molalar": []}]
    kn = KY.kayma_sablonlari(gn, plan_n, [("E", 2)])
    assert kn and all(t["kayma"]["erken"] == 0 for t in kn) and {t["kayma"]["gec"] for t in kn} == {1, 2, 3, 4}


def test_KAYMA_model_kopyayi_yalniz_o_kisiye_acar():
    h = _kaymali(_sahne())
    m = Model(h)
    adlar = {t["id"] for t in m._sablonlari(next(c for c in m.calisanlar if c["id"] == "P1"))}
    assert "S~k~P1~g2~e0~u4" in adlar and not any(KY.AYIRAC + "P2" in a for a in adlar)
    assert {t["id"] for t in m._sablonlari(next(c for c in m.calisanlar if c["id"] == "P2"))} >= {"S", "O", "A"}
    m.kur()
    assert ("P1", 2, "S~k~P1~g2~e0~u4") in m.x and ("P2", 2, "S~k~P1~g2~e0~u4") not in m.x


def test_KAYMA_kapaliyken_cozumsuz_ACIKKEN_iki_kisi_kayar():
    g = _sahne()
    kapali = coz(g, dict(AYAR))
    assert kapali["durum"] == "cozumsuz" and kapali["teshis_kesin"] is True
    h = _kaymali(g)
    c = coz(h, dict(AYAR))
    assert c["durum"] == "cozuldu", c.get("durum")
    car = {a["calisan"]: a for a in c["atamalar"] if a["gun"] == 2}
    assert set(car) == {"P1", "P2"}
    assert car["P1"]["kayma"] == {"taban": "S", "erken": 0, "gec": 4, "saat": 4} and (car["P1"]["bas"], car["P1"]["bit"]) == (8.0, 20.0)
    assert car["P2"]["kayma"] == {"taban": "A", "erken": 2, "gec": 0, "saat": 2} and (car["P2"]["bas"], car["P2"]["bit"]) == (12.0, 22.0)
    # obur gunler aynen (kayma yok)
    assert not any(a.get("kayma") for a in c["atamalar"] if a["gun"] != 2)
    r = degerlendir(h, c["atamalar"])
    assert r["metrikler"]["sert_ihlal"] == 0, [i for i in r["ihlaller"] if i.get("agirlik") == "SERT"]
    assert c["metrikler"]["kayma_atama"] == 2 and c["metrikler"]["kayma_saat"] == 6
    oz = KY.kayma_ozeti(c["atamalar"])
    assert oz["kisi_sayisi"] == 2 and oz["toplam_saat"] == 6 and oz["en_buyuk_saat"] == 4 and oz["dagilim"] == {"2": 1, "4": 1}
    # K-70: kaymis iki kisi-gun DEGISEN, raporlunun gunu KALDIRILAN; baska dokunus yok
    d = plan_degisikligi(dict(h, mevcut_plan=g["mevcut_plan"]), c["atamalar"])
    assert d == {"korunan": 12, "degisen": 2, "kaldirilan": 1, "eklenen": 0}


def test_KAYMA_yasal_sinir_kopyayi_kapatir():
    """Gunluk sinir 10 saat: P1'in +4 kopyasi (net 11) uretilmez; +3 (net 10) ile 19'a kadar,
    16-20 hucresinde 19-20 acik kalir -> asgari sert tutmaz -> cozumsuz. Kayma yasayi asmaz."""
    g = _sahne()
    g["kurallar"] = [k if k["kod"] != "GUNLUK_AZAMI" else _kural("GUNLUK_AZAMI", yasal=True, azami_saat=10)
                     for k in g["kurallar"]]
    h = _kaymali(g)
    assert not any(t["kayma"]["saat"] > 3 for t in h["vardiya_sablonlari"] if t.get("kayma"))
    c = coz(h, dict(AYAR))
    assert c["durum"] == "cozumsuz"


def test_KAYMA_fazla_sureler_kalemi_yalniz_agirlikla_ve_yari_zamanlida():
    g = _sahne(sozlesme={"tip": "yari_zamanli", "haftalik_saat": 30, "gun_sayisi": 5})
    h = _kaymali(g)
    m0 = Model(h).kur()
    assert not any(v.Name().startswith("fs_") for _, v in m0.cezalar if hasattr(v, "Name"))
    h2 = dict(h, agirliklar={"FAZLA_SURELER": 42})
    m = Model(h2).kur()
    fs = [v for a, v in m.cezalar if hasattr(v, "Name") and v.Name().startswith("fs_")]
    assert len(fs) == 3 and all(a == 42 for a, v in m.cezalar if hasattr(v, "Name") and v.Name().startswith("fs_"))
    c = coz(h2, dict(AYAR))
    assert c["durum"] == "cozuldu"
    dag = c["cozum_istatistikleri"]["amac_dagilimi"]["FAZLA_SURELER"]
    # P1: 5 x 7 = 35 net -> 30 ustu 5 saat + 4 saat kayma = 9 saat; P2: 35 + 2 = 37 -> 7 saat;
    # P3: izin gunu borcu duser (30 - 6 = 24), 4 x 7 = 28 -> 4 saat. Toplam 20 saat.
    assert dag["deger"] == (9 + 7 + 4) * 60 and dag["ceza"] == 42 * (9 + 7 + 4) * 60
    # tam zamanlida kalem yazilmaz (sozlesme ustu zaten FAZLA_MESAI)
    t = Model(dict(_kaymali(_sahne()), agirliklar={"FAZLA_SURELER": 42})).kur()
    assert not any(v.Name().startswith("fs_") for _, v in t.cezalar if hasattr(v, "Name"))
