# -*- coding: utf-8 -*-
"""
CIZELGE KAYDI -- K-66 (Mustafa, 11 Ekim 2026)

"Testlerimizin ciktilari cizelge de uretmeli ... urunde kullanilacak cizelge
ciktisi uret ... tum kosumlarda hazir olsun." Olcum kosusu artik iki dosya
yazar: urun bicimindeki kayit (<ad>.json: motorun #11.3 ciktisi + #11.4
dogrulama raporu, alan adlari AYNEN) ve okunur sayfa (<ad>.html).

Burada sinanan:
  - saat gosterimi (genisletilmis saat -> okunur; ertesi gun +1)
  - kisi x gun tablosu: her calisan bir satir (atamasiz da), gun basina
    atamalar, brut/net saat (net = butun molalar dusuk, K-57)
  - kapsama izgarasi: gece yarisini asan vardiya ertesi gune sayilir, yalniz
    atamanin ekibi sayilir, asgari/hedef talepten
  - HTML'de satirlar, hucre metni, donmus isareti, dogrulayici ozeti
  - plan_kaydet: json'daki `cikti` MOTORUN CIKTISININ KENDISIDIR (alan
    eklenmez, adi degismez), `bagimsiz_denetim` orkestra ile AYNI ozet,
    `dogrulama` dogrulayici raporu aynen; CLI html'i yeniden uretir
  - kalite-olc.kosu: cizelgeyi yazar ve kayda yolunu koyar; --plansiz yazmaz

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler/test_cizelge.py -v
"""
import importlib.util
import io
import json
import os
import subprocess
import sys

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

import cizelge                                                # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402
import orkestra                                               # noqa: E402


def _yukle(ad):
    yol = os.path.join(BURASI, ad)
    spec = importlib.util.spec_from_file_location(ad.replace("-", "_").replace(".py", ""), yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _kural(kod, tur="SERT", **p):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": False, "kabul_edilebilir": False}
    if p:
        k["parametreler"] = p
    return k


def _sablon(tid, bas, bit, ekip="E"):
    return {"id": tid, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": 60, "gece_vardiyasi": bit > 24,
            "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]}


def _kisi(cid, ekipler=("E",), tip="tam_zamanli"):
    return {"id": cid, "ekipler": list(ekipler),
            "sozlesme": {"tip": tip, "haftalik_saat": 45, "gun_sayisi": 6},
            "izinler": [], "uygunluk": []}


def _girdi():
    return {"profil": "DENGELI", "hafta_baslangic": "2026-10-12", "donmus_gunler": [],
            "calisanlar": [_kisi("B1", ("B",)), _kisi("A2", tip="yari_zamanli"), _kisi("A1")],
            "vardiya_sablonlari": [_sablon("GUN", 8, 17), _sablon("GECE", 22, 30), _sablon("B-GUN", 9, 13, "B")],
            "talep": [{"ekip": "E", "gun": 0, "saat": h, "asgari": 1, "hedef": 2} for h in (9, 10, 22, 23)]
                     + [{"ekip": "E", "gun": 1, "saat": 0, "asgari": 1, "hedef": 1}],
            "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                         _kural("VARDIYA_ARASI_DINLENME", asgari_saat=11)],
            "kilitler": []}


def _atamalar():
    return [
        {"calisan": "A1", "ekip": "E", "sablon": "GUN", "gun": 0, "bas": 8, "bit": 17,
         "molalar": [{"bas": 12, "bit": 13, "tip": "yemek"}, {"bas": 10, "bit": 10.25, "tip": "dinlenme"}]},
        {"calisan": "A1", "ekip": "E", "sablon": "GECE", "gun": 1, "bas": 22, "bit": 30,
         "molalar": [{"bas": 26, "bit": 27, "tip": "yemek"}], "donmus": True},
        {"calisan": "A2", "ekip": "E", "sablon": "GUN", "gun": 0, "bas": 8, "bit": 17, "molalar": []},
        {"calisan": "B1", "ekip": "B", "sablon": "B-GUN", "gun": 0, "bas": 9, "bit": 13, "molalar": []},
    ]


# ---- saat ve tablolar ----------------------------------------------------

def test_saat_yaz_genisletilmis_saati_okunur_yapar_ertesi_gun_arti_bir():
    assert cizelge.saat_yaz(7) == "07:00"
    assert cizelge.saat_yaz(16.25) == "16:15"
    assert cizelge.saat_yaz(23.75) == "23:45"
    assert cizelge.saat_yaz(24) == "00:00+1"
    assert cizelge.saat_yaz(31) == "07:00+1"
    assert cizelge.saat_yaz(49.5) == "01:30+2"


def test_kisi_gun_tablosu_her_calisan_satir_brut_net_K57_siralama_ekip_sonra_kimlik():
    satirlar = cizelge.kisi_gun_tablosu(_girdi(), _atamalar())
    assert [s["id"] for s in satirlar] == ["B1", "A1", "A2"]            # ekip B < E; E icinde A1 < A2
    a1 = satirlar[1]
    assert sorted(a1["gunler"]) == [0, 1] and a1["gun_sayisi"] == 2
    assert a1["brut"] == 9 + 8
    assert a1["net"] == (9 - 1 - 0.25) + (8 - 1)                       # butun molalar dusuk (K-57)
    a2 = satirlar[2]
    assert a2["tip"] == "yari_zamanli" and a2["brut"] == a2["net"] == 9
    # atamasi olmayan calisan da satirda (bos hafta gorunsun)
    bos = cizelge.kisi_gun_tablosu(_girdi(), [])
    assert [s["id"] for s in bos] == ["B1", "A1", "A2"] and all(s["gun_sayisi"] == 0 for s in bos)


def test_kapsama_tablosu_gece_yarisini_asan_vardiya_ertesi_gune_sayilir_yalniz_atamanin_ekibi():
    k = cizelge.kapsama_tablosu(_girdi(), _atamalar())
    e0 = {c["saat"]: c for c in k[("E", 0)]}
    assert e0[9]["atanan"] == 2 and e0[9]["asgari"] == 1 and e0[9]["hedef"] == 2
    assert e0[16]["atanan"] == 2 and e0[16]["hedef"] is None               # talep satiri yok
    assert e0[22]["atanan"] == 0                                           # gece vardiyasi gun 1'de basliyor
    e1 = {c["saat"]: c for c in k[("E", 1)]}
    assert e1[22]["atanan"] == 1 and e1[23]["atanan"] == 1
    e2 = {c["saat"]: c for c in k[("E", 2)]}
    assert e2[0]["atanan"] == 1 and e2[5]["atanan"] == 1 and e2[6]["atanan"] == 0   # 22-30 -> ertesi gun 00-05
    b0 = {c["saat"]: c for c in k[("B", 0)]}
    assert b0[9]["atanan"] == 1 and e0[9]["atanan"] == 2                   # B'nin atamasi E'ye sayilmaz


# ---- html -------------------------------------------------------------------

def test_cizelge_html_satirlar_hucre_metni_donmus_isareti_ve_dogrulayici_ozeti():
    g, atamalar = _girdi(), _atamalar()
    rapor = degerlendir(g, atamalar)
    cikti = {"durum": "cozuldu", "motor_surumu": "x", "atamalar": atamalar,
             "metrikler": {"hedef_kapsama_yuzde": 50.0}, "cozum_istatistikleri": {"amac_degeri": 12, "durma_sebebi": "optimum"},
             "uygulanmayan_notlar": []}
    h = cizelge.cizelge_html(g, cikti, rapor, {"baslik": "deneme", "yapilandirma": "varsayilan", "tekrar": 2})
    assert "<title>deneme</title>" in h and "<b>amac</b>: 12" in h and "<b>tekrar</b>: 2" in h
    for kimlik in ("A1", "A2", "B1"):
        assert h.count("<td>%s</td>" % kimlik) == 1, kimlik               # kisi tablosunda bir satir
    assert "<th>Pzt</th>" in h and "<th>Sal</th>" in h and "<th>Car</th>" in h
    assert "08:00&ndash;17:00" in h and "22:00&ndash;06:00+1" in h
    assert "(donmus)" in h                                            # K-54 satiri isaretli
    assert "y12:00 d10:00" in h                                       # molalar: y = yemek, d = dinlenme
    assert "Bagimsiz dogrulayici" in h and "Yayin kapisi" in h
    assert "Kosu kunyesi" in h and "varsayilan" in h


def test_cizelge_html_dogrulama_yokken_de_calisir_ve_kunye_bos():
    g, atamalar = _girdi(), _atamalar()
    h = cizelge.cizelge_html(g, {"atamalar": atamalar})
    assert "Bagimsiz dogrulayici" not in h and "Kosu kunyesi" not in h
    assert h.count("<td>A1</td>") == 1


# ---- urun bicimi -------------------------------------------------------------

def test_plan_kaydet_URUN_BICIMI_cikti_aynen_bagimsiz_denetim_orkestrayla_ayni_dogrulama_aynen(tmp_path):
    g, atamalar = _girdi(), _atamalar()
    rapor = degerlendir(g, atamalar)
    cikti = {"durum": "cozuldu", "motor_surumu": "0.2.0", "atamalar": atamalar,
             "metrikler": {"hedef_kapsama_yuzde": 50.0, "ozel_alan": 1},
             "cozum_istatistikleri": {"amac_degeri": 12}, "uygulanmayan_notlar": ["n"]}
    jy, hy = cizelge.plan_kaydet(str(tmp_path), "varsayilan-1", g, cikti, rapor,
                                 {"yapilandirma": "varsayilan", "tekrar": 1, "saniye": 900})
    assert os.path.basename(jy) == "varsayilan-1.json" and os.path.exists(hy)
    d = json.load(io.open(jy, encoding="utf-8"))
    assert set(d) == {"kayit", "girdi_ozeti", "cikti", "dogrulama"}
    # motorun ciktisi AYNEN + bagimsiz_denetim (servis.py'nin /solve cevabi gibi)
    assert set(d["cikti"]) == set(cikti) | {"bagimsiz_denetim"}
    for alan in cikti:
        assert d["cikti"][alan] == cikti[alan], alan
    sert = [i for i in rapor["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    assert d["cikti"]["bagimsiz_denetim"] == json.loads(json.dumps(orkestra._denetim_ozeti(rapor, sert)))
    assert d["dogrulama"] == json.loads(json.dumps(rapor))
    assert d["girdi_ozeti"] == {"kisi": 3, "hucre": 5, "kural": 3, "sablon": 3, "hafta_baslangic": "2026-10-12",
                                "profil": "DENGELI", "donmus_gunler": [], "sure_butcesi_sn": 900}
    assert d["kayit"]["bicim"] == "tshift-plan-kaydi/1" and d["kayit"]["baslik"] == "varsayilan-1"
    # girdi (cikti) degismedi: plan_kaydet kopya uzerinde calisir
    assert "bagimsiz_denetim" not in cikti


def test_plan_kaydet_bagimsiz_denetim_varsa_DOKUNMAZ(tmp_path):
    g, atamalar = _girdi(), _atamalar()
    cikti = {"durum": "cozuldu", "atamalar": atamalar, "bagimsiz_denetim": {"sert_ihlal": 7}}
    jy, _ = cizelge.plan_kaydet(str(tmp_path), "x", g, cikti, degerlendir(g, atamalar))
    assert json.load(io.open(jy, encoding="utf-8"))["cikti"]["bagimsiz_denetim"] == {"sert_ihlal": 7}


def test_cli_json_dan_html_yeniden_uretir(tmp_path):
    g, atamalar = _girdi(), _atamalar()
    sahne = tmp_path / "sahne.json"
    sahne.write_text(json.dumps(g), encoding="utf-8")
    jy, hy = cizelge.plan_kaydet(str(tmp_path), "p", g, {"atamalar": atamalar}, None,
                                 {"sahne": str(sahne), "baslik": "yeniden"})
    os.remove(hy)
    r = subprocess.run([sys.executable, os.path.join(BURASI, "cizelge.py"), jy],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    assert os.path.exists(hy) and "<title>yeniden</title>" in io.open(hy, encoding="utf-8").read()


# ---- olcum araci --------------------------------------------------------------

def test_kalite_olc_kosu_cizelgeyi_yazar_ve_kayda_yolunu_koyar_plansiz_yazmaz(tmp_path, capsys):
    KO = _yukle("kalite-olc.py")
    g = {"profil": "DENGELI", "hafta_baslangic": "2026-10-12", "donmus_gunler": [], "kilitler": [],
         "calisanlar": [_kisi("C%d" % i) for i in range(1, 7)],
         "vardiya_sablonlari": [_sablon("GUN", 8, 17)],
         "talep": [{"ekip": "E", "gun": d, "saat": h, "asgari": 6, "hedef": 7}
                   for d in range(5) for h in range(9, 17)],
         "kurallar": [_kural("ASGARI_KAPSAMA"), _kural("HEDEF_KAPSAMA", "YUMUSAK"),
                      _kural("HAFTA_TATILI"), _kural("FAZLA_MESAI_TAVANI", azami_saat_hafta=10)]}
    ayar = dict(azami_saniye=20, durgunluk_saniye=3, iki_asama_esigi=0, isci_sayisi=2)
    KO.PLANSIZ, KO.PLAN_KLASORU = False, str(tmp_path / "planlar")
    s = KO.kosu(g, "varsayilan", dict(ayar), tekrar=2)
    assert s["durum"] == "cozuldu"
    yol = os.path.join(BURASI, s["plan_dosyasi"])
    assert os.path.basename(yol) == "varsayilan-2.json" and os.path.exists(yol)
    assert os.path.exists(yol[:-5] + ".html")
    d = json.load(io.open(yol, encoding="utf-8"))
    assert d["kayit"]["yapilandirma"] == "varsayilan" and d["kayit"]["tekrar"] == 2
    assert d["kayit"]["saniye"] == 20 and d["kayit"]["arac"] == "kalite-olc.py"
    assert d["cikti"]["durum"] == "cozuldu" and len(d["cikti"]["atamalar"]) > 0
    assert d["cikti"]["bagimsiz_denetim"]["sert_ihlal"] == s["sert_ihlal"] == 0
    assert d["dogrulama"]["yayin_kapisi"]["yayinlanabilir"] is s["yayinlanabilir"] is True
    assert "cizelge: " in capsys.readouterr().out
    # --plansiz: dosya yok, kayitta alan yok
    KO.PLANSIZ = True
    s2 = KO.kosu(g, "varsayilan", dict(ayar), tekrar=3)
    assert "plan_dosyasi" not in s2
    assert not os.path.exists(str(tmp_path / "planlar" / "varsayilan-3.json"))
    assert "cizelge: " not in capsys.readouterr().out
