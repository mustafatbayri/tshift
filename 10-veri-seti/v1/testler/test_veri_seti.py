# -*- coding: utf-8 -*-
"""
TShift veri seti v1 -- testler

Ne garanti eder:
  1. URETIM: depodaki veri dosyalari `uret.py`nin bugunku ciktisiyla AYNI
     (biri degisip oteki unutulamaz).
  2. BELGELER: JSON Schema ve veri sozlugu `tablolar.py`den uretilenle AYNI.
  3. SEMA: her satir tablonun butun kolonlarini tasir, zorunlular dolu,
     degerler izinli kumede, tipler dogru -- bagimliliksiz kendi
     denetimimiz; `jsonschema` kuruluysa resmi dogrulama da.
  4. BUTUNLUK: kimlikler benzersiz, yabanci anahtarlar var, sicil no
     benzersiz, kural tipi basina tek firma satiri, tek varsayilan profil,
     tek taslak plan, her calisanin sozlesmesi var.
  5. DONUSTURUCU: tablolardan kurulan motor girdisi bugunku olcum sahnesinden
     (`merdiven.taban_sahne`) YALNIZ bilerek degisen yerlerde ayrilir.
  6. COZULEBILIRLIK: 49 kisilik kopya (merdiven tabani gibi asim yumusak)
     60 sn'de cozulur, 0 sert ihlal, gecmis eksigi 0.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\10-veri-seti\\v1
  py -m pytest testler -q
"""

import collections
import copy
import datetime as dt
import io
import json
import os
import re
import sys

import pytest

V1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if V1 not in sys.path:
    sys.path.insert(0, V1)

import uret                                                       # noqa: E402  (yollari da kurar)
import donustur                                                   # noqa: E402
import belgeler                                                   # noqa: E402
from tablolar import TABLOLAR, kolonlar, tablo                    # noqa: E402

DOSYALAR = {1.0: "tshift-500.json", 0.1: "tshift-49.json"}


def _yukle(ad):
    return json.load(io.open(os.path.join(V1, "veri", ad), encoding="utf-8"))


@pytest.fixture(scope="module", params=sorted(DOSYALAR), ids=["500", "49"])
def veri(request):
    return request.param, _yukle(DOSYALAR[request.param])


# ----------------------------------------------------------------------
# 1-2. Uretim ve belgeler senkron
# ----------------------------------------------------------------------

def test_URETIM_dosya_uretecin_bugunku_ciktisiyla_AYNI(veri):
    olcek, v = veri
    assert json.loads(json.dumps(uret.uret(olcek), ensure_ascii=False)) == v, \
        "veri dosyasi eski -- `py uret.py` ile yeniden uret"


def test_BELGELER_sema_ve_sozluk_tablolar_py_ile_AYNI():
    s = json.load(io.open(belgeler.SEMA_YOLU, encoding="utf-8"))
    assert s == json.loads(json.dumps(belgeler.sema(), ensure_ascii=False)), "`py belgeler.py`"
    v = _yukle("tshift-500.json")
    assert io.open(belgeler.SOZLUK_YOLU, encoding="utf-8").read() == belgeler.sozluk(v), "`py belgeler.py`"


# ----------------------------------------------------------------------
# 3. Sema (bagimliliksiz) + jsonschema
# ----------------------------------------------------------------------

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _tip_dogru(tip, deger):
    if tip == "uuid":
        return isinstance(deger, str) and bool(UUID.match(deger))
    if tip == "text":
        return isinstance(deger, str)
    if tip == "int":
        return isinstance(deger, int) and not isinstance(deger, bool)
    if tip == "numeric":
        return isinstance(deger, (int, float)) and not isinstance(deger, bool)
    if tip == "bool":
        return isinstance(deger, bool)
    if tip == "date":
        try:
            dt.date.fromisoformat(deger)
            return True
        except (TypeError, ValueError):
            return False
    if tip == "timestamptz":
        try:
            return dt.datetime.fromisoformat(deger).tzinfo is not None
        except (TypeError, ValueError):
            return False
    if tip == "int[]":
        return isinstance(deger, list) and all(isinstance(x, int) for x in deger)
    if tip == "text[]":
        return isinstance(deger, list) and all(isinstance(x, str) for x in deger)
    return True                                                    # json


def test_SEMA_her_satir_butun_kolonlar_zorunlular_dolu_tip_ve_deger_dogru(veri):
    _, v = veri
    assert set(k for k in v if not k.startswith("_")) == {t["ad"] for t in TABLOLAR}
    hatalar = []
    for t in TABLOLAR:
        kol = {k[0]: k for k in kolonlar(t)}
        for i, s in enumerate(v[t["ad"]]):
            if set(s) != set(kol):
                hatalar.append("%s[%d]: kolonlar %s" % (t["ad"], i, sorted(set(s) ^ set(kol))))
                continue
            for ad, (_, tip, zorunlu, _, ek) in kol.items():
                d = s[ad]
                if d is None:
                    if zorunlu:
                        hatalar.append("%s[%d].%s zorunlu ama bos" % (t["ad"], i, ad))
                    continue
                if not _tip_dogru(tip, d):
                    hatalar.append("%s[%d].%s tip %s degil: %r" % (t["ad"], i, ad, tip, d))
                if "enum" in ek and d not in ek["enum"]:
                    hatalar.append("%s[%d].%s izinsiz deger %r" % (t["ad"], i, ad, d))
    assert hatalar == [], hatalar[:10]


def test_SEMA_jsonschema_ile_resmi_dogrulama(veri):
    js = pytest.importorskip("jsonschema", reason="`py -m pip install jsonschema` ile resmi dogrulama da kosar")
    _, v = veri
    s = json.load(io.open(belgeler.SEMA_YOLU, encoding="utf-8"))
    hatalar = list(js.Draft202012Validator(s, format_checker=js.FormatChecker()).iter_errors(v))
    assert hatalar == [], [h.message for h in hatalar[:5]]


# ----------------------------------------------------------------------
# 4. Butunluk
# ----------------------------------------------------------------------

def test_BUTUNLUK_kimlik_benzersiz_yabanci_anahtar_var(veri):
    _, v = veri
    kimlikler = {}
    for t in TABLOLAR:
        anahtar = "kod" if t.get("ortak_yok") else "id"
        degerler = [s[anahtar] for s in v[t["ad"]]]
        assert len(degerler) == len(set(degerler)), t["ad"]
        kimlikler[t["ad"]] = set(degerler)
    eksik = []
    for t in TABLOLAR:
        for ad, _, _, _, ek in kolonlar(t):
            if not ek.get("ref"):
                continue
            for s in v[t["ad"]]:
                if s[ad] is not None and s[ad] not in kimlikler[ek["ref"]]:
                    eksik.append("%s.%s -> %s: %s" % (t["ad"], ad, ek["ref"], s[ad]))
    assert eksik == [], eksik[:10]


def test_BUTUNLUK_is_kurallari(veri):
    _, v = veri
    assert len(v["tenants"]) == 1                                         # M-16
    pno = [e["personel_no"] for e in v["employees"]]
    assert len(pno) == len(set(pno))
    kodlar = [r["rule_type_kod"] for r in v["tenant_rules"]]
    assert len(kodlar) == len(set(kodlar))                                 # kural tipi basina tek satir
    assert sum(p["varsayilan_mi"] for p in v["plan_profiles"]) == 1
    assert [p["durum"] for p in v["plans"]].count("taslak") == 1
    soz = collections.Counter(s["employee_id"] for s in v["employee_contracts"])
    assert set(soz) == {e["id"] for e in v["employees"]}
    for s in v["employee_contracts"]:                                      # K-58 + 14 Ekim
        assert (s["haftalik_gun"] in (5, 6)) == (s["tip"] == "tam_zamanli"), s
    for e in v["employees"]:
        assert (e["isten_cikis"] is not None) == (e["durum"] == "ayrildi"), e["personel_no"]
        assert e["eposta"].endswith("@tshift-ornek.test") and e["telefon"].startswith("+90 000 ")
    birincil = {u["employee_id"]: u["team_id"] for u in v["employee_teams"] if u["oncelik"] == 1}
    assert all(birincil[e["id"]] == e["birincil_team_id"] for e in v["employees"])
    assert {k["kod"] for k in v["rule_types"]} >= set(kodlar) and len(v["rule_types"]) == 41
    for m in v["assignment_breaks"]:
        assert m["dakika"] == round((m["bitis_saat"] - m["baslangic_saat"]) * 60)


def test_ESKI_TIPLER_K58_cevirisi_ve_isimler_UYDURMA():
    import merdiven as MD
    v = _yukle("tshift-500.json")
    eski = {c["id"]: c["sozlesme"]["tip"] for c in MD.taban_sahne(1.0)["calisanlar"]}
    emp = {e["id"]: e["personel_no"] for e in v["employees"]}
    for s in v["employee_contracts"]:
        tip = eski[emp[s["employee_id"]]]
        if tip == "sezonluk":
            assert (s["tip"], s["haftalik_gun"], s["bitis"]) == ("tam_zamanli", 6, "2026-12-31")
        elif tip == "stajyer":
            assert (s["tip"], s["haftalik_gun"], s["bitis"]) == ("yari_zamanli", None, "2027-06-30")
    assert v["_meta"]["donusum"]["sezonluk_tam_zamanliya"] == 13
    assert v["_meta"]["donusum"]["stajyer_yari_zamanliya"] == 16
    assert "UYDURMA" in v["_meta"]["uyari"]


# ----------------------------------------------------------------------
# 5. Donusturucu
# ----------------------------------------------------------------------

def _temiz(x):
    if isinstance(x, dict):
        return {k: _temiz(w) for k, w in x.items() if not k.startswith("_")}
    if isinstance(x, list):
        return [_temiz(w) for w in x]
    return x


def _sirasiz(liste):
    return sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in liste)


BAYRAK_SAPMASI = {"ASGARI_KAPSAMA", "FAZLA_MESAI_TAVANI", "ONAYLI_IZIN", "PART_TIME_LIMIT",
                  "GECE_YARISI_ASAN", "HEDEF_ASIMI"}


def test_DONUSTURUCU_eski_sahneden_YALNIZ_bilinen_farklar(veri):
    import merdiven as MD
    olcek, v = veri
    yeni = donustur.motor_girdisi(v)
    eski = _temiz(MD.taban_sahne(olcek))
    assert set(yeni) - set(eski) == {"agirliklar"} and set(eski) - set(yeni) == set()
    for k in ("hafta_baslangic", "kiraci_saat_dilimi", "profil", "cok_ekipli_sayim", "kilitler",
              "donmus_gunler", "sabit_atamalar", "devir_kapsama", "denetim_disi_kabul"):
        assert yeni[k] == eski[k], k
    assert eski["sektor"] == "cagri_merkezi" and yeni["sektor"] is None      # yasal sektor degil (K-26)
    assert [(d["id"], d["ekipler"], d["acik"]) for d in yeni["departmanlar"]] == \
        [(d["id"], d["ekipler"], d["acik"]) for d in eski["departmanlar"]]  # adlar Turkcelesti
    assert _sirasiz(yeni["vardiya_sablonlari"]) == _sirasiz(eski["vardiya_sablonlari"])
    assert _sirasiz(yeni["talep"]) == _sirasiz(eski["talep"])
    # kurallar: bayragi katalogdan sapan 6 kural ve HEDEF_ASIMI turu disinda ayni
    ayni = lambda L: _sirasiz([k for k in L if k["kod"] not in BAYRAK_SAPMASI])  # noqa: E731
    assert ayni(yeni["kurallar"]) == ayni(eski["kurallar"])
    assert {k["kod"]: k["tur"] for k in yeni["kurallar"]}["HEDEF_ASIMI"] == "SERT"
    # calisanlar
    E = {c["id"]: c for c in eski["calisanlar"]}
    Y = {c["id"]: c for c in yeni["calisanlar"]}
    assert list(E) == list(Y)
    fark = collections.Counter()
    for i in E:
        for alan in set(E[i]) | set(Y[i]):
            a, b = E[i].get(alan), Y[i].get(alan)
            if alan == "yetkinlikler":
                a, b = sorted(a or []), sorted(b or [])
            if a != b:
                fark[alan] += 1
    assert set(fark) <= {"sozlesme", "devir_yuk", "gecmis_vardiyalar", "gecmis_bilinen_gunler"}, fark
    assert fark["sozlesme"] == v["_meta"]["donusum"]["sezonluk_tam_zamanliya"] + \
        v["_meta"]["donusum"]["stajyer_yari_zamanliya"]
    assert all(c["gecmis_bilinen_gunler"] == list(range(-14, 0)) for c in yeni["calisanlar"])


def test_DONUSTURUCU_gecmis_ve_devir_tablolardan():
    v = _yukle("tshift-49.json")
    g = donustur.motor_girdisi(v)
    gecmis = sum(len(c["gecmis_vardiyalar"]) for c in g["calisanlar"])
    assert gecmis == len(v["assignments"])                                 # iki gecmis haftanin hepsi
    assert all(-14 <= k["gun"] <= -1 for c in g["calisanlar"] for k in c["gecmis_vardiyalar"])
    denge = {b["employee_id"]: b for b in v["employee_balances"]}
    emp = {e["personel_no"]: e["id"] for e in v["employees"]}
    for c in g["calisanlar"]:
        b = denge[emp[c["id"]]]
        assert c["devir_yuk"] == {"gece": b["devir_gece"], "hafta_sonu": b["devir_hafta_sonu"],
                                  "saat": b["devir_saat"], "cumartesi": b["devir_cumartesi"]}
        assert c["yil_ici_fazla_mesai_saat"] == b["yil_ici_fazla_mesai_saat"]


def test_DONUSTURUCU_plan_kural_degerleri_ve_tarihli_uygunluk_ve_cok_gunluk_izin():
    v = copy.deepcopy(_yukle("tshift-49.json"))
    plan = [p for p in v["plans"] if p["durum"] == "taslak"][0]
    plan["kural_degerleri"] = {"HEDEF_ASIMI": {"ust_tolerans": 1}}         # K-68: plan bazinda
    izinli = {l["employee_id"] for l in v["leaves"]}
    e = [x for x in v["employees"] if x["id"] not in izinli and x["durum"] == "aktif"][0]
    v["employee_availability"].append(dict(v["employee_availability"][0], id="00000000-0000-4000-8000-000000000001",
                                           employee_id=e["id"], tekrar="tarihli", gun=None,
                                           baslangic_tarih="2026-10-13", bitis_tarih="2026-10-14",
                                           baslangic_saat=18, bitis_saat=24))
    v["leaves"].append(dict(v["leaves"][0], id="00000000-0000-4000-8000-000000000002", employee_id=e["id"],
                            baslangic="2026-10-17", bitis="2026-10-20", durum="onayli"))
    g = donustur.motor_girdisi(v)
    assert {k["kod"]: k for k in g["kurallar"]}["HEDEF_ASIMI"]["parametreler"] == {"ust_tolerans": 1}
    c = [x for x in g["calisanlar"] if x["id"] == e["personel_no"]][0]
    assert {"tip": "uygun_degil", "gun": 1, "bas": 18, "bit": 24} in c["uygunluk"]
    assert {"tip": "uygun_degil", "gun": 2, "bas": 18, "bit": 24} in c["uygunluk"]
    assert [i["gun"] for i in c["izinler"] if i["durum"] == "onayli" and i["gun"] >= 5] == [5, 6]


# ----------------------------------------------------------------------
# 6. Cozulebilirlik
# ----------------------------------------------------------------------

def test_COZULEBILIR_49_kisi_merdiven_tabani_gibi_60_sn_SERT_0():
    from cozucu.coz import coz
    from dogrulayici import degerlendir
    g = donustur.motor_girdisi(_yukle("tshift-49.json"))
    for k in g["kurallar"]:
        if k["kod"] == "HEDEF_ASIMI":
            k["tur"] = "YUMUSAK"                     # merdiven tabani (referans uretimi) boyle kosar
    c = coz(copy.deepcopy(g), {"azami_saniye": 60})
    assert c["durum"] == "cozuldu", (c["durum"], c.get("teshis"))
    r = degerlendir(g, c["atamalar"])
    sert = [i for i in r["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    assert sert == [], sert[:3]
    assert not r.get("gecmis_eksik")


def test_SERT_hedef_asimi_ile_ON_KONTROL_gecmisi_gorur():
    """Bulgu (veri sozlugu #8): gecen haftanin Pazar gecesi Pazartesi sabahini
    kapatiyor; bu talep egrisi gecmisi bilmeden girilmis -> sertte on kontrol."""
    from cozucu.coz import coz
    g = donustur.motor_girdisi(_yukle("tshift-49.json"))
    c = coz(copy.deepcopy(g), {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz"
    assert c["cozum_istatistikleri"]["durma_sebebi"] == "on_kontrol"
    assert "onceki haftadan tasan" in c["teshis"]["engelleyen_kurallar"][0]["gerekce"]


# ----------------------------------------------------------------------
# Excel
# ----------------------------------------------------------------------

def test_EXCEL_sayfalar_ve_satir_sayilari_veriyle_AYNI():
    openpyxl = pytest.importorskip("openpyxl")
    from tablolar import EXCEL_SAYFALARI
    v = _yukle("tshift-500.json")
    wb = openpyxl.load_workbook(belgeler.EXCEL_YOLU)
    assert wb.sheetnames == ["Aciklama"] + [s for s, _, _ in EXCEL_SAYFALARI] + ["Kodlar"]
    pno = {e["id"]: e["personel_no"] for e in v["employees"]}
    for sayfa, tablo_adi, eslem in EXCEL_SAYFALARI:
        ws = wb[sayfa]
        assert [c.value for c in ws[1]] == [e for e, _ in eslem]
        assert ws.max_row - 1 == len(v[tablo_adi]), sayfa
        ilk = v[tablo_adi][0]
        assert ws.cell(row=2, column=1).value == (ilk["personel_no"] if sayfa == "Calisanlar"
                                                  else pno[ilk["employee_id"]]), sayfa
