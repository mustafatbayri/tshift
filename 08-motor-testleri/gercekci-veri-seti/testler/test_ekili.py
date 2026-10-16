# -*- coding: utf-8 -*-
"""
EKILI SAHNE testleri (16 Ekim; A1) -- ekili.py

  * turetim: hedef = dogrulayicinin saydigi kisi, asgari = en kotu ceyrekte sahadaki
    kisi (<= hedef), yari zamanli sozlesme = tanikta calistigi saat, HEDEF_ASIMI SERT;
  * fikstur (49 kisi) tutarli: tanik yeni sahnede sert 0 / asim 0 / eksik 0 / fm 0, bes
    kalem sifir, puan = kalemlerin toplami, kayit alanlari dolu;
  * turetim DETERMINISTIK: fiksturdeki sahne, taniktan yeniden turetilenle ayni;
  * desen cozucu 25 kiside COZUMSUZ (ROL/YETKINLIK_KAPSAMASI fm'siz tutmaz -- T-82'nin
    25 kisi bulgusuyla ayni; ekili sahne orada kurulamaz, bu BILINEN bir sinir);
  * uretim tutarsiz tanigi REDDEDER (sessiz kabul yok);
  * merdiven kaynaklari: "ekili" -> -EK, "ekili-veri-seti" -> -EK-VS<n>; taban uretec / veri seti.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_ekili.py -v
"""

import copy
import io
import json
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor"))

import ekili as E                                              # noqa: E402
import merdiven as MD                                          # noqa: E402

SAHNE = os.path.join(BURASI, "fikstur", "_sahne-L1-EK-95-0.1.json")
TANIK = os.path.join(BURASI, "fikstur", "_referans-L1-EK-95-0.1.json")


def _oku(yol):
    with io.open(yol, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def fikstur():
    return _oku(SAHNE), _oku(TANIK)


# ----------------------------------------------------------------------
# 1. Turetim
# ----------------------------------------------------------------------

def test_EKILI_turetim_hedef_asgari_sozlesme_ve_SERT_asim(fikstur):
    g, ref = fikstur
    taban = MD.taban_sahne(0.1, "uretec")
    tanik = ref["atamalar"]
    turetilen = E.ekili_sahne(taban, tanik)
    sayim, sahada = MD.hucre_sayimi(taban, tanik), E.ceyrek_sahada(taban, tanik)
    for t in turetilen["talep"]:
        h = (t["ekip"], t["gun"], t["saat"])
        assert t["hedef"] == int(sayim[h])
        assert t["asgari"] == min(int(sahada[h]), t["hedef"]) <= t["hedef"]
        assert t["_sahada_taban"] == t["asgari"]
    assert any(t["asgari"] < t["hedef"] for t in turetilen["talep"]), "molalar hic ceyrek dusurmemis olamaz"
    from dogrulayici import zaman
    saat = {}
    for a in tanik:
        saat[a["calisan"]] = saat.get(a["calisan"], 0.0) + zaman.net_saat(a)
    for c in turetilen["calisanlar"]:
        soz = c["sozlesme"]
        if soz["tip"] == "yari_zamanli":
            s = round(saat.get(c["id"], 0.0) * 4) / 4.0
            assert soz.get("haftalik_saat") == (s if s > 0 else None)
    assert [k["tur"] for k in turetilen["kurallar"] if k["kod"] == "HEDEF_ASIMI"] == ["SERT"]
    assert turetilen["_merdiven"]["seviye"] == "1-ekili"
    assert turetilen["_merdiven"]["hedef_kisi_saat"] == sum(t["hedef"] for t in turetilen["talep"])


def test_EKILI_turetim_DETERMINISTIK_fiksturle_ayni(fikstur):
    g, ref = fikstur
    turetilen = E.ekili_sahne(MD.taban_sahne(0.1, "uretec"), ref["atamalar"])
    for ad in ("talep", "calisanlar", "kurallar", "vardiya_sablonlari", "kilitler"):
        assert turetilen[ad] == g[ad], ad
    assert {k: v for k, v in turetilen["_merdiven"].items()} == \
           {k: v for k, v in g["_merdiven"].items() if k not in ("referans_puani", "kaynak")}


def test_EKILI_arama_sahnesi_asgari_SIFIR_asim_YUMUSAK_hedef_AYNI():
    taban = MD.taban_sahne(0.05, "uretec")
    a = E.arama_sahnesi(taban)
    assert all(t["asgari"] == 0 and "_sahada_taban" not in t for t in a["talep"])
    assert [t["hedef"] for t in a["talep"]] == [t["hedef"] for t in taban["talep"]]
    assert [k["tur"] for k in a["kurallar"] if k["kod"] == "HEDEF_ASIMI"] == ["YUMUSAK"]
    assert taban["talep"][0]["asgari"] >= 0 and any(t["asgari"] for t in taban["talep"])   # taban degismedi


# ----------------------------------------------------------------------
# 2. Fikstur tutarliligi (49 kisi)
# ----------------------------------------------------------------------

def test_EKILI_fikstur_tanik_yeni_sahnede_SERT_0_asim_0_eksik_0_fm_0(fikstur):
    g, ref = fikstur
    d = MD.referans_denetle(g, ref["atamalar"])
    assert (d["sert"], d["asim"], d["eksik"], d["fazla_mesai_saat"]) == (0, 0, 0, 0.0), d
    assert d["yayinlanabilir"] is True


def test_EKILI_fikstur_bes_kalem_SIFIR_puan_toplam_kayit_dolu(fikstur):
    g, ref = fikstur
    p = g["_merdiven"]["referans_puani"]
    assert p["durum"] == "OPTIMAL"
    for kod in E.SIFIR_KALEMLER:
        assert p["dagilim"].get(kod, {"ceza": 0})["ceza"] == 0, kod
    assert p["amac"] == sum(d["ceza"] for d in p["dagilim"].values()) > 0
    k = ref["kayit"]
    assert k["kaynak"] == "ekili" and k["taban"] == "uretec" and k["desen_ust"] == E.DESEN_UST
    assert k["fazla_mesai_saat"] == 0.0 and k["fazla_mesaisiz_kanitli_yok"] is False
    assert k["amac_degeri"] == p["amac"] and k["kisi"] == len(g["calisanlar"]) == 49
    assert k["atama"] == len(ref["atamalar"]) and k["durum"] in ("OPTIMAL", "FEASIBLE")
    assert k["hedef_kisi_saat"] == g["_merdiven"]["hedef_kisi_saat"]
    assert "ekili" in g["_merdiven"]["kaynak"] and "tanik" in g["_merdiven"]["kaynak"]


# ----------------------------------------------------------------------
# 3. Desen cozucu
# ----------------------------------------------------------------------

def test_EKILI_desen_kisitlari_kisi_sablon_basina_bir_degisken():
    from cozucu.model import Model
    taban = MD.taban_sahne(0.05, "uretec")
    k = Model(E.arama_sahnesi(taban)).kur()
    ciftler = {(e, t) for (e, _, t) in k.x}
    once = len(k.m.Proto().variables)
    assert E.desen_kisitlari(k, 1) == len(ciftler)
    assert len(k.m.Proto().variables) == once + len(ciftler)


def test_EKILI_desen_cozucu_25_kiside_COZUMSUZ_bilinen_sinir():
    """T-82 (15 Ekim): 25 kiside fm'siz plan kanitli yok (ROL/YETKINLIK_KAPSAMASI her gun
    08-19 lider/ingilizce ister). Desen cozucu de ayni sonucu verir -> ekili sahne 25'te
    kurulamaz; ekili_uret bunu SystemExit ile soyler, sessizce fm'li tanik kabul etmez."""
    taban = MD.taban_sahne(0.05, "uretec")
    tanik, bilgi = E.tanik_ara(taban, saniye=30, isci=1)
    assert tanik is None and bilgi["durum"] == "INFEASIBLE", bilgi
    assert bilgi["fm_alani_sifirlanan"] > 0 and bilgi["desen_ust"] == E.DESEN_UST
    with pytest.raises(SystemExit) as hata:
        E.ekili_uret(0.05, saniye=30, isci=1)
    assert "TANIK BULUNAMADI" in str(hata.value)


# ----------------------------------------------------------------------
# 4. Uretim tutarsizligi REDDEDER
# ----------------------------------------------------------------------

def test_EKILI_uretim_tutarsiz_sahneyi_ve_sifir_olmayan_kalemi_REDDEDER(fikstur, monkeypatch):
    g, ref = fikstur
    tanik = ref["atamalar"]
    monkeypatch.setattr(E, "tanik_ara", lambda *a, **k: (copy.deepcopy(tanik), {"durum": "FEASIBLE", "saniye": 0.0}))
    # (a) turetim bozuk: bir hucrenin hedefi +1 -> tanik o hucrede EKSIK kalir
    gercek = E.ekili_sahne

    def bozuk(taban, t):
        s = gercek(taban, t)
        hucre = next(x for x in s["talep"] if x["hedef"] > 0)
        hucre["hedef"] += 1
        return s
    monkeypatch.setattr(E, "ekili_sahne", bozuk)
    with pytest.raises(SystemExit) as hata:
        E.ekili_uret(0.1, saniye=1)
    assert "TUTARSIZ" in str(hata.value)
    # (b) turetim dogru ama puanda sifir olmasi gereken kalem sifir degil
    monkeypatch.setattr(E, "ekili_sahne", gercek)
    monkeypatch.setattr(MD, "plan_puani", lambda g_, a_, saniye=120: {
        "durum": "OPTIMAL", "amac": 7, "dagilim": {"FAZLA_MESAI": {"ceza": 7, "deger": 1}}})
    with pytest.raises(SystemExit) as hata:
        E.ekili_uret(0.1, saniye=1)
    assert "SIFIR DEGIL" in str(hata.value) and "FAZLA_MESAI" in str(hata.value)


def test_EKILI_bilinmeyen_taban_REDDEDILIR():
    with pytest.raises(SystemExit):
        E.ekili_uret(0.1, saniye=1, taban_kaynagi="baska")


# ----------------------------------------------------------------------
# 5. merdiven kaynaklari
# ----------------------------------------------------------------------

def test_EKILI_merdiven_kaynak_ekleri_ve_tabani():
    assert "ekili" in MD.KAYNAKLAR and "ekili-veri-seti" in MD.KAYNAKLAR
    assert MD._set_eki("ekili") == "-EK"
    assert MD._set_eki("ekili-veri-seti") == "-EK" + MD.VERI_SETI_EKI
    assert os.path.basename(MD.sahne_yolu(0.1, "ekili")) == "_sahne-L1-EK-95-0.1.json"
    assert os.path.basename(MD.referans_yolu(1.0, "ekili-veri-seti")) == "_referans-L1-EK%s-95.json" % MD.VERI_SETI_EKI
    assert MD.taban_sahne(0.05, "ekili") == MD.taban_sahne(0.05, "uretec")
    assert E.TABANLAR == {"uretec": "ekili", "veri-seti": "ekili-veri-seti"}
