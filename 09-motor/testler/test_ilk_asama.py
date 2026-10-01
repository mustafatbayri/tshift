# -*- coding: utf-8 -*-
"""
BIRINCI ASAMA -- molalar sabit, ipucu TAM (T-60, 1 Ekim)

NE BULUNDU
  Tam olcekte (500 kisi) birinci asama uc kosuda da 120 saniyede plan
  bulamadi; T-78 duzeltmesinden sonra ana asama 778 saniyede de bulamadi
  (0 atama, sure_yetmedi). Degiskenlerin ucte ikisi mola yerlesimi; gecerli
  plan icin bunlarin SECILMESI gerekmiyor.

  Ikinci bulgu (0.2 olcek, 100 kisi, iki kod surumuyle olculdu): birinci
  asama 18 saniyede plan bulup ipucu verdigi halde ana asamanin ILK plani
  57-101 saniyede geldi. Ipucu yarimdi (ceza degiskenleri yoktu); CP-SAT
  yarim ipucuyu onarmaya calisip 10 celiskide vazgeciyor.

NE DEGISTI
  * Birinci asamada her sablonun molalari ideale en yakin TEK noktaya
    sabitlenir: secilmeyen adaylarin alani [0,0]; kisit eklenmez; asama
    bitince alanlar geri [0,1].
  * Ipucu BUTUN degiskenlere yazilir (birinci asama ayni modeli cozdugu
    icin hepsinin degeri var).
  * Ana asama molalari SERBEST arar (K-32 degismedi).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_ilk_asama.py -v
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.model import Model, _gercek_kesisiyor             # noqa: E402
from dogrulayici import zaman                                 # noqa: E402

C = importlib.import_module("cozucu.coz")

YIRMI_DK = [{"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 20, "adet": 3, "ucretli": True}]
ONBES_DK = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]
M_SABAH = {"id": "M-SABAH", "ekip": "E", "bas": 8, "bit": 17, "mola_dk": 30,
           "mola_politikasi": YIRMI_DK}
S_SABAH = {"id": "S-SABAH", "ekip": "E", "bas": 7, "bit": 16.25, "mola_dk": 60,
           "mola_politikasi": ONBES_DK}


def _sahne(kisi=2, sablonlar=(M_SABAH,), gunler=range(5), saatler=range(8, 17),
           asgari=1, hedef=1, mola_kapsamasi=False):
    kurallar = [
        {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False},
        {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
        {"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True, "yasal": False,
         "parametreler": {"en_az_saat": 3, "en_gec_saat": 5}},
    ]
    if mola_kapsamasi:
        kurallar.append({"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True})
    return {
        "profil": "DENGELI",
        "calisanlar": [{"id": "C%d" % i, "ekipler": ["E"],
                        "sozlesme": {"tip": "tam_zamanli"},
                        "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
        "vardiya_sablonlari": [dict(t) for t in sablonlar],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": asgari, "hedef": hedef}
                  for d in gunler for s in saatler],
        "kurallar": kurallar, "kilitler": [], "donmus_gunler": [],
    }


# ----------------------------------------------------------------------
# 1. Sabit secim modelin kisitlariyla tutarli
# ----------------------------------------------------------------------

def test_sabit_secim_adaylarin_icinden_ve_AYRIK():
    k = Model(_sahne(sablonlar=(M_SABAH, S_SABAH)))
    for t in k.sablonlar:
        sy, dinl = k.sabit_mola_secimi(t)
        yemek_dk = k.yemek_dk[t["id"]]
        adet, dk = k.dinlenme_tanim[t["id"]]
        assert sy is not None and len(dinl) == adet and all(s is not None for s in dinl), (t["id"], sy, dinl)
        adaylar = k._dinlenme_adaylari(t)
        for i, s in enumerate(dinl):
            assert s in adaylar[i], (t["id"], i, s, adaylar[i])
            assert not _gercek_kesisiyor(s, dk / 60.0, sy, yemek_dk / 60.0), (t["id"], s, sy)
            if i:
                assert not _gercek_kesisiyor(dinl[i - 1], dk / 60.0, s, dk / 60.0), (t["id"], dinl)
        # dogrulayici da ayni yerlesimi N ayrik mola olarak gormeli
        a = {"gun": 0, "bas": t["bas"], "bit": t["bit"],
             "molalar": [{"bas": sy, "bit": sy + yemek_dk / 60.0, "tip": "yemek"}]
             + [{"bas": s, "bit": s + dk / 60.0, "tip": "dinlenme"} for s in dinl]}
        assert abs(zaman.mola_saat(a) - (yemek_dk + adet * dk) / 60.0) < 1e-6, a


def test_sabit_secim_ideale_YAKIN():
    """08-17 / 3x20: idealler 10:15, 12:30, 14:45; yemek penceresi 3-5 sa
    -> orta 12:00. Dinlenme 2 (12:30) yemekle (12:00-12:30) uc uca deger,
    kesismez; secim ideallerin kendisi olmali."""
    k = Model(_sahne())
    sy, dinl = k.sabit_mola_secimi(k.sablonlar[0])
    assert sy == 12.0, sy
    assert dinl == [10.25, 12.5, 14.75], dinl


# ----------------------------------------------------------------------
# 2. Sabitleme alanlari daraltir, geri birakma hepsini acar
# ----------------------------------------------------------------------

def test_sabitleme_yalniz_secilmeyen_adaylari_kapatir_ve_GERI_ACAR():
    k = Model(_sahne(kisi=1, gunler=[0])).kur()
    proto = k.m.Proto()
    sabitlenen = C._molalari_sabitle(k)
    yemek_sayisi = len([1 for (e, d, tid, s) in k.mola if s is not None])
    dinlenme_sayisi = len(k.dinlenme)
    assert len(sabitlenen) == (yemek_sayisi - 7) + (dinlenme_sayisi - 7 * 3), (
        len(sabitlenen), yemek_sayisi, dinlenme_sayisi)
    kapali = [i for i in range(len(proto.variables)) if list(proto.variables[i].domain) == [0, 0]]
    assert sorted(kapali) == sorted(sabitlenen)
    C._molalari_serbest_birak(k, sabitlenen)
    assert not [i for i in range(len(proto.variables)) if list(proto.variables[i].domain) == [0, 0]]


# ----------------------------------------------------------------------
# 3. Ipucu TAM yazilir
# ----------------------------------------------------------------------

def test_ipucu_BUTUN_degiskenlere_yazilir():
    k = Model(_sahne(kisi=1, gunler=[0])).kur()
    assert C._ipucu_ver(k, {"azami_saniye": 10, "ilk_asama_saniye": 10}) is True
    proto = k.m.Proto()
    assert len(proto.solution_hint.vars) == len(proto.variables), (
        len(proto.solution_hint.vars), len(proto.variables))
    # amac geri konmus olmali
    assert len(proto.objective.vars) > 0 or len(proto.floating_point_objective.vars) > 0
    # alanlar geri acilmis olmali
    assert not [i for i in range(len(proto.variables)) if list(proto.variables[i].domain) == [0, 0]]
    # ipucudaki plan SABIT secimle ayni olmali (molalar sabitlenerek arandi)
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    t = k.sablonlar[0]
    sy, dinl = k.sabit_mola_secimi(t)
    atanan = [(e, d) for (e, d, tid), v in k.x.items() if ipucu[v.Index()] == 1]
    assert atanan, "ipucuda atama yok"
    for (e, d) in atanan:
        secilen_yemek = [s_ for (e2, d2, tid, s_), v in k.mola.items()
                         if (e2, d2) == (e, d) and ipucu[v.Index()] == 1]
        assert secilen_yemek == [sy], (secilen_yemek, sy)
        secilen_dinl = sorted(s_ for (e2, d2, tid, i, s_), v in k.dinlenme.items()
                              if (e2, d2) == (e, d) and ipucu[v.Index()] == 1)
        assert secilen_dinl == sorted(dinl), (secilen_dinl, dinl)


# ----------------------------------------------------------------------
# 4. Ana asama molalari SERBEST arar (K-32 korunur)
# ----------------------------------------------------------------------

def test_ana_asama_molalari_SERBEST_arar_sabit_secimde_KALMAZ():
    """Iki kisi, ayni sablon, her saatte 2 kisi isteniyor, MOLA_KAPSAMASI
    acik. Birinci asama molalari ideale sabitler (ikisi de 10:15, 12:00,
    12:30, 14:45); ana asama molalari ayirarak optimuma gider. Alanlar
    geri acilmasaydi plan sabit secimde kalir ve optimuma ulasamazdi."""
    g = _sahne(kisi=2, gunler=[0], asgari=2, hedef=2, mola_kapsamasi=True)
    c = C.coz(g, {"azami_saniye": 30, "iki_asama_esigi": 0, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c["durum"]
    ist = c["cozum_istatistikleri"]
    assert ist["iki_asama"] is True
    assert ist["amac_degeri"] == ist["alt_sinir"], ist      # kanitli optimum
    k = Model(g)
    sy, dinl = k.sabit_mola_secimi(k.sablonlar[0])
    sabit = sorted([sy] + dinl)
    gercek = [sorted(m["bas"] for m in a["molalar"]) for a in c["atamalar"]]
    assert any(y != sabit for y in gercek), (
        "ana asama molalari sabit secimde birakti: %r" % gercek)
    # sabit secimle ayni amac degerine ulasilamaz mi? -- ulasilamaz:
    # ipucusuz kosu da ayni optimumu ayri molalarla buluyor
    c2 = C.coz(g, {"azami_saniye": 30, "iki_asama_esigi": 10 ** 9,
                   "durgunluk_saniye": 5})
    assert c2["cozum_istatistikleri"]["amac_degeri"] == ist["amac_degeri"], (
        c2["cozum_istatistikleri"], ist)
    r = __import__("dogrulayici").degerlendir(g, c["atamalar"])
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["ihlaller"]
