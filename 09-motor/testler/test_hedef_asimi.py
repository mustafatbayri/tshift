# -*- coding: utf-8 -*-
"""
HEDEF_ASIMI -- hedefi asan kisi-saat ceza (K-53, T-54)

NE VARDI (29 Eylul)
  Talep asgari 1 kisi, sahnede 4 yari zamanli: cozucu DORDUNU de 45 saate
  doldurdu. Modelde bir saatin bedeli yoktu; hicbir kural "gereksiz yere
  kisi yazma" demiyordu. 350 kisilik sahnede plan hedefin 2 katini sahaya
  koyuyordu.

KARAR (K-53, Mustafa, 1 Ekim): "Ceza ile ilerleyelim. Ucret tarafi hic
  gelmeyebilir." YUMUSAK kural: hedefin ustune cikan her kisi-saat ceza;
  hedefin altinda kalmak (HEDEF_KAPSAMA) her profilde daha pahali.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_hedef_asimi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU               # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402

V = {"id": "V", "ekip": "E", "bas": 9, "bit": 18, "mola_dk": 60}


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def _sahne(kisi=4, asim=True, profil="DENGELI"):
    kurallar = [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", tur="YUMUSAK"),
                _kural("HAFTA_TATILI", yasal=True)]
    if asim:
        kurallar.append(_kural("HEDEF_ASIMI", tur="YUMUSAK"))
    return {"profil": profil,
            "calisanlar": [{"id": "P%d" % i, "ekipler": ["E"],
                            "sozlesme": {"tip": "yari_zamanli"},
                            "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
            "vardiya_sablonlari": [V],
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                      for d in range(5) for s in range(9, 18)],
            "kurallar": kurallar, "kilitler": [], "donmus_gunler": []}


def _plan(kisiler, gunler=range(5)):
    return [{"calisan": k, "ekip": "E", "sablon": "V", "gun": g, "bas": 9, "bit": 18,
             "molalar": [{"bas": 13, "bit": 14, "tip": "yemek"}]}
            for k in kisiler for g in gunler]


# ----------------------------------------------------------------------
# 1. Dogrulayici
# ----------------------------------------------------------------------

def test_hedefin_ustundeki_hucre_YUMUSAK_ihlal():
    r = degerlendir(_sahne(), _plan(["P1", "P2", "P3"]))     # hedef 1, 3 kisi, 5x9 hucre
    ih = [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert len(ih) == 45, len(ih)
    assert all(i["agirlik"] == "YUMUSAK" and i["olculen"] == 3 and i["gereken"] == 1 for i in ih)
    assert "2 kisi fazla" in ih[0]["mesaj"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True        # yumusak


def test_hedefe_ESIT_ihlal_degil():
    r = degerlendir(_sahne(), _plan(["P1"]))
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]


def test_kural_yokken_yazilmaz():
    r = degerlendir(_sahne(asim=False), _plan(["P1", "P2"]))
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert "HEDEF_ASIMI" not in r["uygulanmayan_kurallar"]


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_T54_SAHNESI_bir_kisilik_talebe_dort_kisi_YAZILMAZ():
    """4 yari zamanli, talep hedef 1: ceza varken her hucrede tam 1 kisi;
    toplam atama 5 (gun basina 1). Karsi kanit kurulmaz -- cezasiz sahnede
    cozucunun fazladan yazip yazmamasi rastgeledir (T-54'un kendisi)."""
    g = _sahne()
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    assert len(c["atamalar"]) == 5, [(a["calisan"], a["gun"]) for a in c["atamalar"]]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"], r["ihlaller"]
    assert r["metrikler"]["hedef_kapsama_yuzde"] == 100.0


def test_HEDEF_altinda_kalmak_her_profilde_asmaktan_PAHALI():
    for profil in ("DENGELI", "KAPSAMA", "CALISAN"):
        assert AGIRLIK_TABLOSU["HEDEF_KAPSAMA"][profil] > AGIRLIK_TABLOSU["HEDEF_ASIMI"][profil], profil
    k = Model(_sahne(profil="KAPSAMA"))
    assert k._agirlik("HEDEF_ASIMI") == 1
    k2 = Model(_sahne(profil="CALISAN"))
    assert k2._agirlik("HEDEF_ASIMI") == 4


def test_TAM_zamanli_45_saat_tabani_cezaya_ragmen_DOLAR():
    """Ceza, sert tabani esmez: 45 saatlik tam zamanli (SAAT_DENGESI sert,
    tolerans 0) talep 1 kisi olsa da 45 saate tamamlanir; ceza yalniz
    fazlaligi en az hucreye yayar."""
    g = _sahne(kisi=2)
    g["vardiya_sablonlari"] = [dict(V, bit=17.5)]            # 7,5 net x 6 = 45
    for c in g["calisanlar"]:
        c["sozlesme"] = {"tip": "tam_zamanli", "haftalik_saat": 45, "gun_sayisi": 6}
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(6) for s in range(9, 17)]
    g["kurallar"] += [_kural("SAAT_DENGESI", tolerans_saat=0),
                      _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=45)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["agirlik"] == "SERT"], r["ihlaller"]
    assert len(c["atamalar"]) == 12                           # 2 kisi x 6 gun = 90 saat
    # Ceza fazlaligi EN AZA indirir: ikisi de talepsiz 7. gunu calisip
    # tatillerini FARKLI talep gunlerine koyar -> 4 gun cakisir, 4 x 8 = 32
    # hucre asim. (Ayni gunu tatil yapsalar 5 x 8 = 40 olurdu.)
    assert len([i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]) == 32


# ----------------------------------------------------------------------
# 3. K-67 (Mustafa, 12 Ekim 2026): HEDEF_ASIMI SERT -- "Hicbir isletme talebin
#    ustunde eleman calistirmaz." Tur girdiden okunur; YUMUSAK yol (ustteki
#    testler) aynen kalir. Kabul olcutleri 1-5 (12 Ekim 22:03 onayi) ve eki
#    (22:09): yoneticinin elle ekledigi fazla kisi yayini DURDURMAZ, kabul
#    ISTEMEZ -- `bilgi_ihlaller`de gorunur.
# ----------------------------------------------------------------------

from cozucu.teshis import _en_iyi_plan                        # noqa: E402


def _sert(g):
    for k in g["kurallar"]:
        if k["kod"] == "HEDEF_ASIMI":
            k["tur"] = "SERT"
    return g


def _tam_zamanli_sahne():
    """Iki 45 saatlik tam zamanli, 6 gun x 7,5 net; talep 6 gun 09-17 hedef 1.
    Ikisi 12 vardiya yazmak zorunda; asim yasakken talepli gunlere en fazla
    6 + talepsiz 7. gune 2 = 8 sigar -> SERT'te COZUMSUZ. En az asim: 4 gun x
    8 hucre = 32 (yumusak yolun buldugu sayi; ust test)."""
    g = _sahne(kisi=2)
    g["vardiya_sablonlari"] = [dict(V, bit=17.5)]
    for c in g["calisanlar"]:
        c["sozlesme"] = {"tip": "tam_zamanli", "haftalik_saat": 45, "gun_sayisi": 6}
    g["talep"] = [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(6) for s in range(9, 17)]
    g["kurallar"] += [_kural("SAAT_DENGESI", tolerans_saat=0),
                      _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=45)]
    return g


def test_K67_SERT_motor_hedefin_ustune_HIC_yazmaz_amac_kiriliminda_yok():
    g = _sert(_sahne())
    m = Model(dict(g)).kur()
    assert m.asim == {} and not [v for _, v in m.cezalar if v.Name().startswith("ha_")]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert "HEDEF_ASIMI" not in c["cozum_istatistikleri"]["amac_dagilimi"]
    # yumusak yolda degisken ve kirilim var (ayni sahne)
    m2 = Model(_sahne()).kur()
    assert len(m2.asim) == 45


def test_K67_SERT_dogrulayici_SERT_satir_yayini_DURDURMAZ_bilgi_verir():
    g = _sert(_sahne())
    r = degerlendir(g, _plan(["P1", "P2", "P3"]))
    ih = [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert len(ih) == 45 and all(i["agirlik"] == "SERT" for i in ih)
    k = r["yayin_kapisi"]
    assert k["yayinlanabilir"] is True                          # K-67 eki: durdurmaz
    assert len(k["bilgi_ihlaller"]) == 45
    assert k["kabul_bekleyen_ihlaller"] == [] and k["engelleyen_ihlaller"] == []
    assert k["kabul_secenegi_sunulur"] is False                  # kabul istemez
    # obur sert kurallar kapiyi eskisi gibi kapatir: bilgi yolu yalniz HEDEF_ASIMI
    g2 = _sert(_sahne())
    g2["kurallar"].append(_kural("GUNLUK_AZAMI", yasal=True, azami_saat=4))
    r2 = degerlendir(g2, _plan(["P1"]))
    assert r2["yayin_kapisi"]["yayinlanabilir"] is False


def test_K67_SERT_sablon_geometrisi_COZUMSUZ_teshis_asim_hucreleri_ve_taslak():
    g = _sert(_tam_zamanli_sahne())
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5, "teshis_kural_saniye": 10})
    assert c["durum"] == "cozumsuz", c["durum"]
    t = c["teshis"]
    kodlar = {k["kod"] for k in t["engelleyen_kurallar"]}
    assert "HEDEF_ASIMI" in kodlar, kodlar
    a = t["asim_hucreleri"]
    assert a["toplam_fazla"] == 32 and a["en_az_kanitli"] is True
    assert len(a["hucreler"]) == 32 and all(h["fazla"] == 1 and h["hedef"] == 1 for h in a["hucreler"])
    ei = c["en_iyi_plan"]
    assert ei["var"] is True and ei["gevsetilen_kurallar"] == ["HEDEF_ASIMI"]
    r = degerlendir(g, ei["atamalar"])
    sert_disi = [i for i in r["ihlaller"] if i["agirlik"] == "SERT" and i["kural"] != "HEDEF_ASIMI"]
    assert sert_disi == []                                       # obur sert kurallar AYNEN tuttu
    assert len([i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]) == 32
    assert r["yayin_kapisi"]["yayinlanabilir"] is True           # taslagi yayinlamak yoneticinin karari


def test_K67_en_iyi_plan_HEDEF_ASIMI_SILMEZ_yumusatir():
    g = _sert(_tam_zamanli_sahne())
    ei = _en_iyi_plan(g, {"azami_saniye": 20})
    assert ei["var"] is True and "HEDEF_ASIMI" in ei["gevsetilen_kurallar"]
    r = degerlendir(g, ei["atamalar"])
    # yumusatilinca en az asimli dagilim (32); silinseydi asim bedava olurdu ve
    # 12 Ekim'de olculdu: 5 kosuda 5'i 48 (iki kisi alti gunun hepsinde ust uste)
    assert len([i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]) == 32


def test_K67_ON_KONTROL_asgari_hedeften_buyuk_COZUCU_CALISMADAN_cozumsuz():
    g = _sert(_sahne())
    g["talep"][10]["asgari"] = 2                                  # gun 1 saat 10: asgari 2, hedef 1
    c = coz(g, {"azami_saniye": 20})
    assert c["durum"] == "cozumsuz"
    assert c["cozum_istatistikleri"]["durma_sebebi"] == "on_kontrol"
    t = c["teshis"]
    assert t["hucre"] == {"ekip": "E", "gun": 1, "saat": 10} and t["gereken"] == 2 and t["mumkun"] == 1
    assert {k["kod"] for k in t["engelleyen_kurallar"]} == {"ASGARI_KAPSAMA", "HEDEF_ASIMI"}
    assert "asgarisi 2, hedefi 1" in t["engelleyen_kurallar"][0]["gerekce"]
    assert c["en_iyi_plan"]["var"] is False
    # YUMUSAK'ta celiski degildir: plan cikar (asgari 2, 1 kisi asim cezasi)
    g2 = _sahne(kisi=4)
    g2["talep"][10]["asgari"] = 2
    assert coz(g2, {"azami_saniye": 20, "durgunluk_saniye": 5})["durum"] == "cozuldu"


def test_K67_ON_KONTROL_saha_tabani_ve_gecmis_devir_hedefi_asiyorsa():
    g = _sert(_sahne())
    g["kurallar"].append(_kural("SAHADA_ASGARI", asgari_sahada=2))
    c = coz(g, {"azami_saniye": 20})
    assert c["durum"] == "cozumsuz" and c["cozum_istatistikleri"]["durma_sebebi"] == "on_kontrol"
    assert "SAHADA_ASGARI" in {k["kod"] for k in c["teshis"]["engelleyen_kurallar"]}
    # onceki haftanin iki gecesi pazartesi 00-07'yi kapliyor; o saatlerin hedefi 1
    g2 = _sert(_sahne())
    for cc in g2["calisanlar"][:2]:
        cc["gecmis_vardiyalar"] = [{"gun": -1, "bas": 23, "bit": 31}]
    g2["talep"].append({"ekip": "E", "gun": 0, "saat": 3, "asgari": 0, "hedef": 1})
    c2 = coz(g2, {"azami_saniye": 20})
    assert c2["durum"] == "cozumsuz" and c2["cozum_istatistikleri"]["durma_sebebi"] == "on_kontrol"
    assert c2["teshis"]["hucre"] == {"ekip": "E", "gun": 0, "saat": 3}
    assert "onceki haftadan tasan 2" in c2["teshis"]["engelleyen_kurallar"][0]["gerekce"]


def test_K67_K54_donmus_gundeki_asim_cozumu_KILITLEMEZ_gecmis_isaretli():
    plan0 = _plan(["P1", "P2"], gunler=[0])                      # gun 0'da iki kisi (hedef 1)
    g = _sert(_sahne())
    g["donmus_gunler"] = [0]
    g["mevcut_plan"] = plan0
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    ih = [i for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"]
    assert ih and all(i["gun"] == 0 and i.get("gecmis") for i in ih)   # olan oldu
    assert r["yayin_kapisi"]["bilgi_ihlaller"] == []             # gecmis bilgiye de girmez
