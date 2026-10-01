# -*- coding: utf-8 -*-
"""
DEPARTMAN CALISMA SAATLERI -- CALISMA_SAATLERI (K-52, 1 Ekim)

MUSTAFA: "Sistemde departman tanimi lazim ve ilgili departmana calisma
  gunleri ile saatlerini tanimlamaliyiz."

GIRDI
  departmanlar: [{"id", "ekipler": [...], "acik": "7/24" | [{"gunler",
  "bas", "bit"}, ...]}]. Pencere `bit` 24'u asabilir (31 = ertesi 07:00).
  Vardiya acik sayilir <=> basladigi gunun bir penceresi tamamini kapsar.

IKI TARAF
  Cozucu kapali sablon x gun ciftlerini kapatir ve not yazar; on kontrol
  kapali sablonu "ulasiyor" saymaz. Dogrulayici atamayi denetler (SERT,
  firma kurali, kabul edilebilir). Ekibin saatleri tanimsizsa: cozucu kisit
  yazmaz + not, dogrulayici `eksik_boyutlar` ile "denetlenemedi" (K-49
  kapiya tasir).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_calisma_saatleri.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model, departman_acik_mi             # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5}
SABAH = {"id": "V-SABAH", "ekip": "MH", "bas": 8, "bit": 17, "mola_dk": 60}
AKSAM = {"id": "V-AKSAM", "ekip": "MH", "bas": 13, "bit": 22, "mola_dk": 60}
GECE = {"id": "V-GECE", "ekip": "MH", "bas": 23, "bit": 31, "mola_dk": 60}
MH_SAATLERI = [{"gunler": [0, 1, 2, 3, 4], "bas": 7, "bit": 23},
               {"gunler": [5, 6], "bas": 8, "bit": 19}]


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(acik=MH_SAATLERI, talep=None, sablonlar=(SABAH, AKSAM), departmanlar=True,
           kisi=2):
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": "C%d" % i, "ekipler": ["MH"],
                         "sozlesme": {"tip": "tam_zamanli"},
                         "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
         "vardiya_sablonlari": [dict(t) for t in sablonlar],
         "talep": talep if talep is not None else
         [{"ekip": "MH", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
          for d in range(7) for s in range(10, 17)],
         "kurallar": [_kural("CALISMA_SAATLERI"), _kural("ASGARI_KAPSAMA"),
                      _kural("HAFTA_TATILI", yasal=True)],
         "kilitler": [], "donmus_gunler": []}
    if departmanlar:
        g["departmanlar"] = [{"id": "D-MH", "ad": "Musteri Hizmetleri",
                              "ekipler": ["MH"], "acik": acik}]
    return g


def _atama(gun, t, kimlik="C1"):
    return {"calisan": kimlik, "ekip": t["ekip"], "sablon": t["id"], "gun": gun,
            "bas": t["bas"], "bit": t["bit"],
            "molalar": [{"bas": t["bas"] + 4, "bit": t["bas"] + 5, "tip": "yemek"}]}


# ----------------------------------------------------------------------
# 1. Pencere mantigi -- iki tarafta ayni
# ----------------------------------------------------------------------

def test_pencere_mantigi_IKI_TARAFTA_AYNI():
    saatler = {"MH": MH_SAATLERI, "S": "7/24"}
    for fn in (departman_acik_mi, K.departman_acik_mi):
        assert fn(saatler, "MH", 0, 8, 17) is True          # hafta ici sabah
        assert fn(saatler, "MH", 5, 13, 22) is False        # cumartesi aksam -> 19'u asar
        assert fn(saatler, "MH", 5, 8, 17) is True
        assert fn(saatler, "MH", 0, 23, 31) is False        # gece: 23'u asar
        assert fn(saatler, "MH", 6, 7, 10) is False         # pazar 07 < 08
        assert fn(saatler, "S", 3, 23, 31) is True          # 7/24
        assert fn(saatler, "YOK", 0, 8, 17) is None         # tanimsiz


# ----------------------------------------------------------------------
# 2. Dogrulayici
# ----------------------------------------------------------------------

def test_KAPALI_saate_tasan_atama_ihlal():
    g = _sahne()
    r = degerlendir(g, [_atama(5, AKSAM)])                    # cumartesi 13-22, kapanis 19
    ih = [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"]
    assert len(ih) == 1 and ih[0]["kabul_edilebilir"] is True, r["ihlaller"]
    assert "13-22" in ih[0]["mesaj"] and "kapali" in ih[0]["mesaj"], ih[0]["mesaj"]
    assert r["yayin_kapisi"]["kabul_secenegi_sunulur"] is True


def test_ACIK_saatteki_atama_temiz():
    g = _sahne()
    r = degerlendir(g, [_atama(1, AKSAM), _atama(5, SABAH)])   # sali aksam, cumartesi sabah
    assert not [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"], r["ihlaller"]


def test_GECE_YARISINI_asan_vardiya_pencereyle_karsilastirilir():
    g = _sahne(acik=[{"gunler": [0, 1, 2, 3, 4, 5, 6], "bas": 6, "bit": 31}],
               sablonlar=(GECE,))
    r = degerlendir(g, [_atama(0, GECE)])                     # 23 -> 07 ertesi
    assert not [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"]
    g2 = _sahne(acik=[{"gunler": [0, 1, 2, 3, 4, 5, 6], "bas": 6, "bit": 30}],
                sablonlar=(GECE,))
    r2 = degerlendir(g2, [_atama(0, GECE)])
    assert len([i for i in r2["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"]) == 1


def test_TANIMSIZ_departman_denetlenemedi_ve_KAPI_bekler():
    g = _sahne(departmanlar=False)
    r = degerlendir(g, [_atama(5, AKSAM)])
    assert not [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"]
    e = [x for x in r["eksik_boyutlar"] if x["kural"] == "CALISMA_SAATLERI"]
    assert len(e) == 1 and e[0]["denetlenemedi"] is True and "MH" in e[0]["boyut"], r["eksik_boyutlar"]
    k = r["yayin_kapisi"]
    assert k["yayinlanabilir"] is False
    assert [d["etki"] for d in k["denetlenemeyen_kurallar"]] == ["kabul_bekliyor"]


def test_YEDI_YIRMIDORT_departman_hic_ihlal_yazmaz_ve_eksik_boyut_yok():
    g = _sahne(acik="7/24", sablonlar=(SABAH, AKSAM, GECE))
    r = degerlendir(g, [_atama(5, AKSAM), _atama(6, GECE)])
    assert not [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"]
    assert not [x for x in r["eksik_boyutlar"] if x["kural"] == "CALISMA_SAATLERI"]


# ----------------------------------------------------------------------
# 3. Cozucu
# ----------------------------------------------------------------------

def test_COZUCU_kapali_saate_vardiya_YAZMAZ_ve_not_yazar():
    """Hafta sonu yalniz sabah sablonu acik. 2 kisi, 7 gun 10-17 talep:
    cozulur, hafta sonu atamalari SABAH olur; dogrulayici kabul eder."""
    g = _sahne()
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    hs = [a for a in c["atamalar"] if a["gun"] in (5, 6)]
    assert hs and all(a["sablon"] == "V-SABAH" for a in hs), hs
    assert any("V-AKSAM gun 5" in n and "CALISMA_SAATLERI" in n for n in c["uygulanmayan_notlar"]), c["uygulanmayan_notlar"]
    r = degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


def test_COZUCU_kural_pasifken_kapatmaz():
    """Kural yokken departman saatleri yalniz bilgidir: cumartesi 20:00
    talebi AKSAM (13-22) ile karsilanir, not yazilmaz, on kontrol gecer."""
    g = _sahne(sablonlar=(AKSAM,),
               talep=[{"ekip": "MH", "gun": 5, "saat": 20, "asgari": 1, "hedef": 1}])
    g["kurallar"] = [k for k in g["kurallar"] if k["kod"] != "CALISMA_SAATLERI"]
    k = Model(g).kur()
    assert not any("CALISMA_SAATLERI" in n for n in k.notlar), k.notlar
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]


def test_COZUCU_kapali_sablon_tek_secenekse_COZUMSUZ():
    """Cumartesi 14-17 talebi; C1 cumartesi sabah uygun degil (08-12),
    yani SABAH giremez, yalniz AKSAM (13-22) kalir -- ama AKSAM cumartesi
    kapali saate tasar. Kisit yazilmazsa plan cozulur (yanlis); yazilirsa
    cozumsuz. Karsi kanit: departman 7/24 olunca cozulur."""
    talep = [{"ekip": "MH", "gun": 5, "saat": s, "asgari": 1, "hedef": 1}
             for s in range(14, 17)]
    g = _sahne(kisi=1, talep=talep)
    g["calisanlar"][0]["uygunluk"] = [{"tip": "uygun_degil", "gun": 5, "bas": 8, "bit": 12}]
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", (c["durum"], c.get("atamalar"))
    g2 = _sahne(kisi=1, talep=talep, acik="7/24")
    g2["calisanlar"][0]["uygunluk"] = [{"tip": "uygun_degil", "gun": 5, "bas": 8, "bit": 12}]
    c2 = coz(g2, AYAR)
    assert c2["durum"] == "cozuldu" and c2["atamalar"][0]["sablon"] == "V-AKSAM", c2.get("atamalar")


def test_COZUCU_tanimsiz_departmanda_kisit_yazmaz_NOT_yazar():
    g = _sahne(departmanlar=False)
    k = Model(g).kur()
    assert any("tanimsiz" in n and "MH" in n for n in k.notlar), k.notlar
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu"


def test_ON_KONTROL_kapali_sablonu_ulasiyor_SAYMAZ():
    """Cumartesi 20:00 talebi: tek sablon AKSAM (13-22) ama cumartesi 19'da
    kapaniyor -> hucre ulasilamaz (on kontrol), cozucu kosmadan cevap."""
    g = _sahne(sablonlar=(AKSAM,),
               talep=[{"ekip": "MH", "gun": 5, "saat": 20, "asgari": 1, "hedef": 1}])
    c = coz(g, AYAR)
    assert c["durum"] == "cozumsuz", c["durum"]
    assert c["cozum_istatistikleri"]["durma_sebebi"] == "on_kontrol", c["cozum_istatistikleri"]


def test_IKI_TARAF_tam_olcek_benzeri_ANLASIR():
    """Hafta ici 07-23, hafta sonu 08-19; sabah ve aksam sablonlari;
    3 kisi, 7 gun 10-17 talep asgari 2. Cozucunun plani dogrulayicidan
    kapali saat ihlalsiz gecer."""
    g = _sahne(kisi=3, talep=[{"ekip": "MH", "gun": d, "saat": s, "asgari": 2, "hedef": 2}
                               for d in range(7) for s in range(10, 17)])
    c = coz(g, AYAR)
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "CALISMA_SAATLERI"], r["ihlaller"]
