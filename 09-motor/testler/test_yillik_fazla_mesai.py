# -*- coding: utf-8 -*-
"""
YILLIK FAZLA MESAI TAVANI -- 270 saat (Is K. md. 41) -- iki motor yarisi

NEDEN 1 EKIM'DE YAZILDI
  K-49 ile yayin kapisi "bakamadim"i gormeye basladi: govdesi olmayan yasal
  bir kural yayini ENGELLIYOR. Olcum setinde bu kural aktif ve govdesizdi;
  plan bir anda yayinlanamaz oldu. Dogru cevap kurali kapatmak degil
  govdesini yazmakti.

OLCU
  bu hafta fazla mesai = haftalik net calisma - HAFTALIK_AZAMI (45, K-38)
  yil ici toplam       = calisanlar[].yil_ici_fazla_mesai_saat (takvim yili)
  toplam + bu hafta > 270 -> SERT, YASAL, kabul edilemez
  yil ici toplam bilinmiyorsa -> kontrol atlanir, gecmis_eksik bildirir (K-42)

GECE_YARISI_ASAN da bu dosyada: hesaplama kuralidir, ihlal uretmez (T-67);
K-49 yuzunden "govdesi var, bakacak sey yok" diye kayitli olmali.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_yillik_fazla_mesai.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir, zaman                    # noqa: E402
from dogrulayici import kurallar as K                         # noqa: E402

V9 = {"id": "V9", "ekip": "E", "bas": 8, "bit": 18, "mola_dk": 60}   # 9 net


def _kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal,
         "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


YILLIK = _kural("YILLIK_FAZLA_MESAI_TAVANI", yasal=True, azami_saat_yil=270)
HAFTALIK = _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=45)
FM = _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10)


def _sahne(yil=None, gunler=6, kurallar=(YILLIK, HAFTALIK, FM)):
    c = {"id": "C1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    if yil is not None:
        c["yil_ici_fazla_mesai_saat"] = yil
    return {"profil": "DENGELI", "calisanlar": [c], "vardiya_sablonlari": [V9],
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                      for d in range(gunler) for s in range(8, 18)],
            "kurallar": [dict(k) for k in kurallar] + [
                _kural("ASGARI_KAPSAMA"), _kural("HAFTA_TATILI", yasal=True)],
            "kilitler": [], "donmus_gunler": []}


def _plan(gunler):
    return [{"calisan": "C1", "ekip": "E", "sablon": "V9", "gun": d, "bas": 8,
             "bit": 18, "molalar": [{"bas": 12, "bit": 13, "tip": "yemek"}]}
            for d in range(gunler)]


# ----------------------------------------------------------------------
# 1. Dogrulayici
# ----------------------------------------------------------------------

def test_tavani_ASAN_hafta_ihlal_yasal_kabul_edilemez():
    """6 gun x 9 net = 54 saat -> 9 saat fazla mesai. Yil ici 265 + 9 = 274 > 270."""
    r = degerlendir(_sahne(yil=265), _plan(6))
    ih = [i for i in r["ihlaller"] if i["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]
    assert len(ih) == 1, r["ihlaller"]
    assert ih[0]["agirlik"] == "SERT" and ih[0]["yasal"] is True
    assert ih[0]["kabul_edilebilir"] is False
    assert abs(ih[0]["olculen"] - 274.0) < 1e-6 and ih[0]["gereken"] == 270
    assert "265.0" in ih[0]["mesaj"] and "274.0" in ih[0]["mesaj"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is False
    assert r["yayin_kapisi"]["kabul_secenegi_sunulur"] is False


def test_tam_TAVANDA_ihlal_degil():
    r = degerlendir(_sahne(yil=261), _plan(6))          # 261 + 9 = 270
    assert not [i for i in r["ihlaller"] if i["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]


def test_fazla_mesai_YOKSA_yil_ici_asmis_olsa_da_ihlal_degil():
    """5 gun x 9 = 45 saat, fazla mesai sifir: plan durumu kotulestirmiyor."""
    r = degerlendir(_sahne(yil=300), _plan(5))
    assert not [i for i in r["ihlaller"] if i["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]


def test_yil_ici_toplam_BILINMIYORSA_atlanir_ve_bildirilir():
    r = degerlendir(_sahne(yil=None), _plan(6))
    assert not [i for i in r["ihlaller"] if i["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]
    satir = [x for x in r["gecmis_eksik"] if x["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]
    assert len(satir) == 1 and "9.0 saat fazla mesai" in satir[0]["mesaj"], r["gecmis_eksik"]
    oz = r["gecmis_eksik_ozet"]
    assert oz["yasal_kontrol_yapilamayan_kisi"] == 1 and oz["kisiler"][0]["yasal"] is True
    assert r["yayin_kapisi"]["yayinlanabilir"] is True       # K-42: kapi engellemez
    assert "YILLIK_FAZLA_MESAI_TAVANI" not in r["uygulanmayan_kurallar"]


def test_bilinmiyor_ama_fazla_mesai_YOKSA_satir_yazilmaz():
    r = degerlendir(_sahne(yil=None), _plan(5))
    assert not [x for x in r["gecmis_eksik"] if x["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]


def test_normal_sinir_HAFTALIK_AZAMI_dan_okunur():
    """Normal sinir 40 ise 6 x 9 = 54'un 14 saati fazla mesai: 258 + 14 = 272."""
    g = _sahne(yil=258, kurallar=(YILLIK, _kural("HAFTALIK_AZAMI", yasal=True, azami_saat=40),
                                  _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=15)))
    r = degerlendir(g, _plan(6))
    ih = [i for i in r["ihlaller"] if i["kural"] == "YILLIK_FAZLA_MESAI_TAVANI"]
    assert len(ih) == 1 and abs(ih[0]["olculen"] - 272.0) < 1e-6, r["ihlaller"]


def test_parametre_azami_saat_yil_OKUNUR():
    g = _sahne(yil=100, kurallar=(_kural("YILLIK_FAZLA_MESAI_TAVANI", yasal=True, azami_saat_yil=105),
                                  HAFTALIK, FM))
    r = degerlendir(g, _plan(6))                          # 100 + 9 = 109 > 105
    assert [i["kural"] for i in r["ihlaller"] if i["kural"].startswith("YILLIK")] == ["YILLIK_FAZLA_MESAI_TAVANI"]


# ----------------------------------------------------------------------
# 2. Cozucu
# ----------------------------------------------------------------------

def test_COZUCU_kalan_payi_asan_fazla_mesaiyi_VERMEZ():
    """Talep 6 gun; 6 gun = 9 saat fazla mesai. Yil ici 265 -> 5 saat kaldi:
    6. gun verilemez -> cozumsuz (asgari kapsama). Karsi kanit: yil ici 200
    ile cozulur ve dogrulayici kabul eder."""
    c = coz(_sahne(yil=265), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozumsuz", c["durum"]
    c2 = coz(_sahne(yil=200), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c2["durum"] == "cozuldu", c2["durum"]
    r = degerlendir(_sahne(yil=200), c2["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
    assert abs(sum(zaman.net_saat(a) for a in c2["atamalar"]) - 54.0) < 1e-6


def test_COZUCU_bilinmeyen_toplamda_kisit_YOK_dogrulayici_bildirir():
    c = coz(_sahne(yil=None), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(_sahne(yil=None), c["atamalar"])
    assert r["gecmis_eksik_ozet"]["yasal_kontrol_yapilamayan_kisi"] == 1


def test_COZUCU_kirpilan_payi_NOTA_yazar():
    c = coz(_sahne(yil=265, gunler=5), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    assert any("YILLIK_FAZLA_MESAI_TAVANI" in n and "5.0 saat kaldi" in n
               for n in c["uygulanmayan_notlar"]), c["uygulanmayan_notlar"]


def test_IKI_TARAF_tavanin_kiyisinda_ANLASIR():
    """Yil ici 261 -> 9 saat kaldi = tam 6 gun. Cozucu 54 saat verir,
    dogrulayici 270'i asilmamis sayar."""
    c = coz(_sahne(yil=261), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(_sahne(yil=261), c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]


# ----------------------------------------------------------------------
# 3. GECE_YARISI_ASAN -- govdesi var, ihlal uretmez
# ----------------------------------------------------------------------

def test_GECE_YARISI_ASAN_kayitli_ve_ihlal_uretmez():
    assert "GECE_YARISI_ASAN" in K.KAYIT
    g = _sahne(kurallar=(_kural("GECE_YARISI_ASAN"),))
    plan = [{"calisan": "C1", "ekip": "E", "sablon": "V9", "gun": 0, "bas": 22,
             "bit": 6, "molalar": []}]                       # ham yazim: 22 -> 06
    r = degerlendir(g, plan)
    assert "GECE_YARISI_ASAN" not in r["uygulanmayan_kurallar"]
    assert not [i for i in r["ihlaller"] if i["kural"] == "GECE_YARISI_ASAN"]
    assert not [d for d in r["yayin_kapisi"]["denetlenemeyen_kurallar"]
                if d["kod"] == "GECE_YARISI_ASAN"]
    assert zaman.brut_saat(plan[0]) == 8                     # Z-1 uygulandi
