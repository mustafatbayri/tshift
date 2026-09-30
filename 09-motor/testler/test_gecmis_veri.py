# -*- coding: utf-8 -*-
"""
GECMIS VERI -- HAFTA SINIRI ARTIK KOR DEGIL (T-28, K-42)

⚠ NE VARDI (T-28, risk listesinde birinci sira)
  `gecmis_vardiyalar` girdide vardi ama motor HIC okumuyordu. Sonucu:
  dort yazili kural pazartesi 00:00'da KORDU --
      vardiya arasi dinlenme · hafta tatili · ardisik calisma gunu ·
      ardisik gece limiti.
  Pazar 23:00'e kadar calismis biri pazartesi 07:00'ye yazilabiliyordu ve
  hicbir sey kirmizi yanmiyordu. Sartname #11.2 bunu tam boyle tarif
  ediyor: "Eksik gecmisle uretilen plan, dinlenme ihlalini sessizce kacirir."

BICIM (#11.2)
  calisanlar[].gecmis_vardiyalar: [{"gun": -1, "bas": 23, "bit": 31}]
  Gun negatif (-1 = onceki pazar), saat genisletilmis. SABLON YOK -- PDKS
  gibi gerceklesen kayit. Mustafa: "Realitede gecmis datayi PDKS v.b.
  sistemlerden alacagiz."

  Istege bagli: `gecmis_bilinen_gunler: [-7, ..., -1]` -- kaydi TAM olan
  gunler. Bilinen ama kaydi olmayan gun = CALISILMAMIS. Liste yoksa
  yalniz kaydi olan gunler bilinir.

TEMEL ILKE -- K-42
  Kayitli bir aralik calisildigini KANITLAR. Kaydin yoklugu HICBIR SEY
  kanitlamaz. Gercek veride kayitlarin yalniz %18'i dolu (P-1).

    * Bilinmeyen gun KISIT YARATMAZ: calisilmamis gibi davranilir.
      (Mustafa: "Gecmis veri yoksa ... gecmise dayanan kriterleri dikkate
      almadan ilerlemek." Yasal kurallar DAHIL.)
    * Ama SESSIZ GECMEZ: hangi kontrolun kimin icin yapilamadigi
      `gecmis_eksik` kanalinda yazilir.
    * Gecmisin KENDI ihlali plana yazilmaz -- gecmis yeniden planlanamaz.

RAPOR KESIN, GURULTULU DEGIL
  Gercek veride kisilerin cogunun pazari bilinmiyor. Her pazartesi
  calisani icin dort satir yazan bir kanal okunmaz olurdu (O-7). Bu
  yuzden rapor yalniz sonucu GERCEKTEN degistirebilecek bilinmeyen gunu
  yazar: pazartesi bossa hicbir sey yazilmaz; geriye dogru yururken
  bilinen bir bos gun gorulurse seri orada kirilir ve rapor yazilmaz.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_gecmis_veri.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402

GUNDUZ = {"id": "V-GUNDUZ", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60,
          "gece_vardiyasi": False}
GECE = {"id": "V-GECE", "ekip": "E", "bas": 23, "bit": 31, "mola_dk": 60,
        "gece_vardiyasi": True}


def _kural(kod, **par):
    k = {"kod": kod, "tur": "SERT", "aktif": True, "yasal": False,
         "kabul_edilebilir": True}
    if par:
        k["parametreler"] = par
    return k


DINLENME = _kural("VARDIYA_ARASI_DINLENME", asgari_saat=11)
CAKISMA = _kural("CAKISMA_YOK")
TATIL = _kural("HAFTA_TATILI", pencere_gun=7)
ARDISIK = _kural("ARDISIK_CALISMA_GUNU", azami_gun=6)
ARD_GECE = _kural("ARDISIK_GECE_LIMIT", azami_gece=3)


def _sahne(kurallar, gecmis=None, bilinen=None):
    c = {"id": "C1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    if gecmis is not None:
        c["gecmis_vardiyalar"] = gecmis
    if bilinen is not None:
        c["gecmis_bilinen_gunler"] = bilinen
    return {"profil": "DENGELI", "calisanlar": [c],
            "vardiya_sablonlari": [GUNDUZ, GECE], "talep": [],
            "kurallar": list(kurallar), "kilitler": [], "donmus_gunler": []}


def _g(gun, bas=8, bit=16, **ek):
    d = {"gun": gun, "bas": bas, "bit": bit}
    d.update(ek)
    return d


def _p(gun, sablon=GUNDUZ):
    return {"calisan": "C1", "ekip": "E", "sablon": sablon["id"], "gun": gun,
            "bas": sablon["bas"], "bit": sablon["bit"], "molalar": []}


def _ih(g, plan, kod):
    return [i for i in degerlendir(g, plan)["ihlaller"] if i["kural"] == kod]


def _eksik(g, plan, kod=None):
    r = degerlendir(g, plan).get("gecmis_eksik")
    assert r is not None, "cikti `gecmis_eksik` kanalini tasimiyor"
    return [x for x in r if kod is None or x["kural"] == kod]


# ----------------------------------------------------------------------
# 1. Alan artik okunuyor
# ----------------------------------------------------------------------

def test_gecmis_vardiyalar_ARTIK_OKUNUYOR():
    """T-28'in en dogrudan kaniti: alan `okunmayan_alanlar`da GORUNMEMELI."""
    r = degerlendir(_sahne([DINLENME], gecmis=[_g(-1)], bilinen=[-1]),
                    [_p(0)])
    adlar = " ".join(str(x) for x in r["okunmayan_alanlar"])
    assert "gecmis_vardiyalar" not in adlar, r["okunmayan_alanlar"]
    assert "gecmis_bilinen_gunler" not in adlar, r["okunmayan_alanlar"]


# ----------------------------------------------------------------------
# 2. Vardiya arasi dinlenme -- pazartesi sinirinda
# ----------------------------------------------------------------------

def test_DINLENME_pazar_aksami_pazartesi_sabahi_IHLAL():
    """Pazar 16:00-24:00, pazartesi 08:00 -> 8 saat ara, 11'in altinda.

    Bugune kadar bu IHLAL GORUNMUYORDU: pazar gecesi planin disindaydi.
    """
    ih = _ih(_sahne([DINLENME], gecmis=[_g(-1, 16, 24)]), [_p(0)],
             "VARDIYA_ARASI_DINLENME")
    assert len(ih) == 1, "pazartesi sinirindaki dinlenme ihlali gorulmedi"
    assert ih[0]["gun"] == 0 and abs(ih[0]["olculen"] - 8) < 1e-6, ih[0]


def test_DINLENME_ara_yeterliyse_ihlal_YOK():
    assert not _ih(_sahne([DINLENME], gecmis=[_g(-1)]), [_p(0)],
                   "VARDIYA_ARASI_DINLENME")


def test_DINLENME_gecmisin_KENDI_ihlali_plana_yazilmaz():
    """Cumartesi aksami + pazar sabahi 8 saat -- gecmiste bir ihlal.

    Plan onu duzeltemez; plana yazilirsa yonetici yapamayacagi bir seyle
    suclanir. Gecmis yeniden planlanamaz.
    """
    ih = _ih(_sahne([DINLENME], gecmis=[_g(-2, 16, 24), _g(-1, 8, 16)]),
             [_p(0)], "VARDIYA_ARASI_DINLENME")
    assert not ih, "gecmisin kendi ihlali plana yazilmis: %r" % ih


# ----------------------------------------------------------------------
# 3. Cakisma -- pazar gece vardiyasi pazartesiye tasiyor
# ----------------------------------------------------------------------

def test_CAKISMA_pazar_gecesi_pazartesiye_TASIYORSA():
    """Pazar 23:00 - pazartesi 07:00 kayitli; pazartesi 06:00 vardiyasi.

    Kisi o saatte hala calisiyor. Dinlenme kurali ortusen cifti CAKISMA'ya
    birakiyor (V-1); cakisma gecmisi gormezse ikisi de susar.
    """
    sabah = dict(GUNDUZ, id="V-ERKEN", bas=6, bit=14)
    g = _sahne([CAKISMA, DINLENME], gecmis=[_g(-1, 23, 31)])
    g["vardiya_sablonlari"].append(sabah)
    ih = _ih(g, [_p(0, sabah)], "CAKISMA_YOK")
    assert len(ih) == 1, "pazartesiye tasan pazar gecesi ile cakisma gorulmedi"


# ----------------------------------------------------------------------
# 4. Ardisik calisma gunu / hafta tatili
# ----------------------------------------------------------------------

def test_ARDISIK_gecmiste_bes_planda_iki_gun_IHLAL():
    """Salidan pazara 5 gun + pazartesi-sali 2 gun = 7 gun ust uste."""
    g = _sahne([ARDISIK], gecmis=[_g(d) for d in range(-5, 0)])
    ih = _ih(g, [_p(0), _p(1)], "ARDISIK_CALISMA_GUNU")
    assert len(ih) == 1, "hafta sinirini asan seri gorulmedi"
    assert ih[0]["olculen"] == 7, ih[0]


def test_HAFTA_TATILI_gecmisle_birlikte_IHLAL():
    g = _sahne([TATIL], gecmis=[_g(d) for d in range(-5, 0)])
    assert _ih(g, [_p(0), _p(1)], "HAFTA_TATILI"), (
        "gecmisle birlikte 7 gun dinlenmesiz -- hafta tatili gorulmedi")


def test_ARDISIK_bilinmeyen_gun_seriyi_UZATMAZ():
    """⚠ K-42: bilinmeyen gun KISIT YARATMAZ.

    Sali-cuma kayitli, cumartesi ve pazar BILINMIYOR. Seri pazartesiye
    uzanamaz -- bilinmeyen gun calisilmamis gibi davranir.
    """
    g = _sahne([ARDISIK], gecmis=[_g(d) for d in range(-6, -2)])
    assert not _ih(g, [_p(d) for d in range(4)], "ARDISIK_CALISMA_GUNU")


def test_ARDISIK_gecmisin_KENDI_serisi_plana_yazilmaz():
    """Gecmiste 8 gun ust uste (bir ihlal), pazartesi bos."""
    g = _sahne([ARDISIK], gecmis=[_g(d) for d in range(-8, 0)])
    assert not _ih(g, [_p(1)], "ARDISIK_CALISMA_GUNU")


def test_HAFTA_TATILI_tamamen_GECMISTEKI_pencere_plana_yazilmaz():
    """Gecmiste 7 gun dinlenmesiz (bir ihlal), pazartesi bos, sali calisiyor.

    Pencere tamamen gecmiste -- plan onu duzeltemez.
    """
    g = _sahne([TATIL], gecmis=[_g(d) for d in range(-8, 0)])
    assert not _ih(g, [_p(1)], "HAFTA_TATILI")


def test_gun_degeri_NEGATIF_olmayan_kayit_gecmis_SAYILMAZ():
    """Plan haftasi gecmis degildir: gun 0 ile gelen 'gecmis' kaydi atlanir.

    Atlanmasaydi pazartesi 08:00 kaydi plandaki pazartesi 08:00 vardiyasiyla
    cakisir ve olmayan bir ihlal yazilirdi.
    """
    g = _sahne([CAKISMA], gecmis=[_g(0)])
    assert not _ih(g, [_p(0)], "CAKISMA_YOK")


# ----------------------------------------------------------------------
# 5. Ardisik gece -- Mustafa'nin senaryosu
# ----------------------------------------------------------------------

def test_GECE_cuma_cumartesi_pazar_ve_PAZARTESI_dorduncu():
    """Cuma, cumartesi, pazar gecesi calismis; pazartesi gecesi DORDUNCU.

    Plan haftasina bakan bir govde yalniz pazartesiyi gorur: 1 gece.
    """
    g = _sahne([ARD_GECE], gecmis=[_g(d, 23, 31) for d in (-3, -2, -1)])
    ih = _ih(g, [_p(0, GECE)], "ARDISIK_GECE_LIMIT")
    assert len(ih) == 1 and ih[0]["olculen"] == 4, ih


def test_GECE_gecmis_kaydin_ISARETI_saati_ezer():
    """K-40 kaydin kendisine de uyar: `gece: false` diyorsa gece degildir."""
    g = _sahne([ARD_GECE],
               gecmis=[_g(d, 23, 31, gece=False) for d in (-3, -2, -1)])
    assert not _ih(g, [_p(0, GECE)], "ARDISIK_GECE_LIMIT")


# ----------------------------------------------------------------------
# 6. K-42 raporu -- `gecmis_eksik`
# ----------------------------------------------------------------------

def test_K42_pazar_BILINMIYOR_pazartesi_calisiyor_RAPORLANIR():
    """Gecmis yok, pazartesi vardiya var -> dinlenme kontrolu yapilamadi."""
    e = _eksik(_sahne([DINLENME]), [_p(0)], "VARDIYA_ARASI_DINLENME")
    assert len(e) == 1 and e[0]["calisan"] == "C1" and e[0]["gun"] == -1, e
    assert "C1" in e[0]["mesaj"], e[0]


def test_K42_pazar_BILINEN_bos_gun_raporlanmaz():
    """Pazar bilinen gunler arasinda ve kaydi yok -> calismamis, kontrol tamam."""
    assert not _eksik(_sahne([DINLENME], gecmis=[], bilinen=[-1]), [_p(0)],
                      "VARDIYA_ARASI_DINLENME")


def test_K42_pazartesi_BOSSA_hicbir_sey_raporlanmaz():
    """Gecmis hic yok ama pazartesi bos -- sinir kurallari etkilenemez."""
    g = _sahne([DINLENME, TATIL, ARDISIK, ARD_GECE])
    assert not _eksik(g, [_p(1), _p(2)]), _eksik(g, [_p(1), _p(2)])


def test_K42_geri_yuruyus_BILINEN_bos_gunde_durur():
    """Pazar ve cumartesi calisilmis, cuma BILINEN bos -> seri kirildi.

    Daha oncesi bilinmese de sonuc degismez; rapor yazilmamali.
    """
    g = _sahne([ARDISIK], gecmis=[_g(-1), _g(-2)], bilinen=[-3, -2, -1])
    assert not _eksik(g, [_p(d) for d in range(3)], "ARDISIK_CALISMA_GUNU")


def test_K42_geri_yuruyus_BILINMEYEN_gunu_raporlar():
    """Pazar calisilmis, cumartesi BILINMIYOR -> seri uzayabilirdi."""
    g = _sahne([ARDISIK], gecmis=[_g(-1)], bilinen=[-1])
    e = _eksik(g, [_p(d) for d in range(3)], "ARDISIK_CALISMA_GUNU")
    assert len(e) == 1 and e[0]["gun"] == -2, e


def test_K42_ihlal_KANITLIYSA_rapor_degil_ihlal_yazilir():
    """Seri gecmisle zaten 7 -- bu belirsizlik degil, ihlaldir. Iki kez
    yazilmaz: ihlal kanali soyler, `gecmis_eksik` susar."""
    g = _sahne([ARDISIK], gecmis=[_g(d) for d in range(-5, 0)])
    assert _ih(g, [_p(0), _p(1)], "ARDISIK_CALISMA_GUNU")
    assert not _eksik(g, [_p(0), _p(1)], "ARDISIK_CALISMA_GUNU")


def test_K42_raporu_IHLAL_DEGILDIR_yayini_durdurmaz():
    """Yapilamayan kontrol ihlal degil; yayin kapisi ona bakmaz (T-18)."""
    r = degerlendir(_sahne([DINLENME]), [_p(0)])
    assert r["gecmis_eksik"], "rapor bekleniyordu"
    assert not r["ihlaller"], r["ihlaller"]
    assert r["yayin_kapisi"]["yayinlanabilir"] is True, r["yayin_kapisi"]


def test_K42_ardisik_gece_icin_pazartesi_GECE_degilse_raporlanmaz():
    """Pazartesi gunduz vardiyasi -- gece serisi pazartesiye uzanamaz."""
    assert not _eksik(_sahne([ARD_GECE]), [_p(0, GUNDUZ)],
                      "ARDISIK_GECE_LIMIT")


# ======================================================================
# 7. COZUCU TARAFI
# ======================================================================
#
# ⚠ Testler govdeden ONCE yazildi -- kirmizi kanit gercek.
# ⚠ T-62'nin dersiyle kuruldu: talep oyle ki onu YALNIZ yasak secenek
#   karsilayabiliyor. "Dogru secti mi" sorusu bu motorda tesadufe acik
#   (fazladan atamanin maliyeti yok, T-54).

ASGARI = {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
          "yasal": False}


def _cozucu_sahnesi(kurallar, gecmis=None, bilinen=None, sablonlar=None,
                    talep=()):
    g = _sahne([ASGARI] + list(kurallar), gecmis=gecmis, bilinen=bilinen)
    if sablonlar is not None:
        g["vardiya_sablonlari"] = list(sablonlar)
    g["talep"] = [{"ekip": "E", "gun": d, "saat": h, "asgari": 1, "hedef": 1}
                  for d, h in talep]
    return g


def _coz(g):
    from cozucu.coz import coz
    return coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})


def test_COZUCU_pazar_aksami_varsa_pazartesi_sabahini_YAZMAZ():
    """Pazar 16:00-24:00 kayitli; pazartesi 08:00 talebi YALNIZ bu kisiyle
    karsilanabilir -> 8 saat ara -> plan cozumsuz kalmak ZORUNDA."""
    g = _cozucu_sahnesi([DINLENME], gecmis=[_g(-1, 16, 24)],
                        sablonlar=[GUNDUZ], talep=[(0, 8)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "pazar aksamindan 8 saat sonra vardiya yazildi: %r" % c.get("atamalar"))


def test_COZUCU_ara_yeterliyse_pazartesi_sabahini_YAZAR():
    g = _cozucu_sahnesi([DINLENME], gecmis=[_g(-1)],
                        sablonlar=[GUNDUZ], talep=[(0, 8)])
    assert _coz(g)["durum"] == "cozuldu"


def test_COZUCU_gecmisle_YEDINCI_gunu_yazmaz():
    """Sali-pazar 5 gun kayitli; pazartesi ve sali talebi yalniz bu kiside
    -> 7 gun ust uste -> cozumsuz."""
    g = _cozucu_sahnesi([ARDISIK, TATIL],
                        gecmis=[_g(d) for d in range(-5, 0)],
                        sablonlar=[GUNDUZ], talep=[(0, 8), (1, 8)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", (
        "gecmisle birlikte 7. gun yazildi: %r"
        % sorted(a["gun"] for a in c.get("atamalar") or []))


def test_COZUCU_BILINMEYEN_gun_kisit_yaratmaz():
    """⚠ K-42: cumartesi-pazar bilinmiyor -> seri pazartesiye uzanamaz."""
    g = _cozucu_sahnesi([ARDISIK, TATIL],
                        gecmis=[_g(d) for d in range(-6, -2)],
                        sablonlar=[GUNDUZ], talep=[(0, 8), (1, 8)])
    assert _coz(g)["durum"] == "cozuldu"


def test_COZUCU_gecmisle_DORDUNCU_geceyi_yazmaz():
    """Mustafa'nin senaryosu, cozucu tarafi: cuma-cumartesi-pazar gecesi
    kayitli; pazartesi gecesi talebi yalniz bu kiside -> cozumsuz."""
    g = _cozucu_sahnesi([ARD_GECE],
                        gecmis=[_g(d, 23, 31) for d in (-3, -2, -1)],
                        sablonlar=[GECE], talep=[(0, 23)])
    c = _coz(g)
    assert c["durum"] != "cozuldu", "gecmisle dorduncu gece yazildi"


def test_COZUCU_gecmis_kaydin_GECE_ISARETI_saati_ezer():
    g = _cozucu_sahnesi([ARD_GECE],
                        gecmis=[_g(d, 23, 31, gece=False) for d in (-3, -2, -1)],
                        sablonlar=[GECE], talep=[(0, 23)])
    assert _coz(g)["durum"] == "cozuldu"


def test_UCTAN_UCA_gecmisli_plan_DENETIMDEN_gecer():
    """Iki kisi: biri pazar aksami calismis, digeri bos. Pazartesi sabahi
    talebi var. Cozucu dogru kisiyi secmeli; denetci ayni plani temiz
    bulmali -- iki taraf gecmis hakkinda ANLASMALI."""
    g = _cozucu_sahnesi([DINLENME, CAKISMA], sablonlar=[GUNDUZ],
                        talep=[(0, 8)])
    ikinci = dict(g["calisanlar"][0], id="C2")
    ikinci.pop("gecmis_vardiyalar", None)
    ikinci["gecmis_bilinen_gunler"] = [-1]
    g["calisanlar"][0]["gecmis_vardiyalar"] = [_g(-1, 16, 24)]
    g["calisanlar"].append(ikinci)
    c = _coz(g)
    assert c["durum"] == "cozuldu", c.get("durum")
    pazartesi = {a["calisan"] for a in c["atamalar"] if a["gun"] == 0}
    assert "C1" not in pazartesi, "pazar aksami calisan kisi pazartesi sabahina yazildi"
    r = degerlendir(g, c["atamalar"])
    assert not [i for i in r["ihlaller"]
                if i["kural"] in ("VARDIYA_ARASI_DINLENME", "CAKISMA_YOK")], r["ihlaller"]


def test_COZUCU_gun_degeri_NEGATIF_olmayan_kaydi_yok_sayar():
    """Plan haftasi gecmis degildir. Gun 0 ile gelen 'gecmis' kaydi dikkate
    alinsaydi pazartesi 08:00-16:00 kaydi ayni saatteki vardiyayi yasaklardi
    ve tek kisilik talep cozumsuz kalirdi."""
    g = _cozucu_sahnesi([DINLENME], gecmis=[_g(0)],
                        sablonlar=[GUNDUZ], talep=[(0, 8)])
    assert _coz(g)["durum"] == "cozuldu"


# ======================================================================
# 8. IKI ASAMA -- Mustafa'nin onerisi, KUCUK ve DETERMINISTIK
# ======================================================================
#
# "Once 1 hafta sonrasini ve ondan sonra diger haftayi, bu sekilde
#  elimizde gecmis data olur." (Mustafa, 30 Eylul)
#
# Gercekci olcekte yapildi ve olculdu (27 ihlal -> 0; `iki-hafta-olc.py`),
# ama CI'da zamanlamaya bagli kirmizi uretiyordu. Burada sinanan BORU
# HATTI: COZUCUNUN CIKTISI gecmis bicimine, oradan yine COZUCUYE
# tasininca hafta 2'yi gercekten kisitliyor mu.
#
# ⚠ ILK HALI HICBIR SEY OLCMUYORDU -- ve bunu mutasyon degil soru buldu.
#   Ilk test "hafta 2 gecmisle temiz mi" diye soruyordu. Cozucu gecmisi
#   HIC okumayacak sekilde bozuldu: test YINE YESIL kaldi. Sahnede bosluk
#   coktu, cozucu siniri sans eseri cignemiyordu. Bu oturumda ayni tuzaga
#   ucuncu kez dusuldu (T-62'nin "atandi mi" testi, `assert True` ile
#   biten testler).
#
#   Yerine SABIT ATAMALI bir hafta 1 kondu: C1 cuma, cumartesi, pazar
#   gecesi calisir. Hafta 2'de geceyi YALNIZ C1 calisabilir. Gecmis
#   okunuyorsa pazartesi gecesi dorduncu olur ve plan cozumsuz kalmak
#   ZORUNDA; okunmuyorsa plan cozulur. Cevap tek, tesadufe kapali.


def _iki_asama_sahnesi(talep):
    kurallar = [CAKISMA, ARD_GECE,
                {"kod": "GECE_UYGUNLUGU", "tur": "SERT", "aktif": True,
                 "yasal": False, "kabul_edilebilir": False}]
    g = _cozucu_sahnesi(kurallar, sablonlar=[GUNDUZ, GECE], talep=talep)
    sablon_kisi = g["calisanlar"][0]
    g["calisanlar"] = []
    for i, gece_yok in ((1, False), (2, True), (3, True)):
        c = dict(sablon_kisi, id="C%d" % i, gece_calisamaz=gece_yok)
        c.pop("gecmis_vardiyalar", None)
        c.pop("gecmis_bilinen_gunler", None)
        g["calisanlar"].append(c)
    return g


def _gecmise_cevir(g, atamalar):
    """Hafta 1'in atamalari -> hafta 2'nin gecmisi (gun - 7), gecmis TAM."""
    sablon = {t["id"]: t for t in g["vardiya_sablonlari"]}
    kisi = {}
    for a in atamalar:
        t = sablon.get(a.get("sablon")) or {}
        k = {"gun": a["gun"] - 7, "bas": a["bas"], "bit": a["bit"]}
        if "gece_vardiyasi" in t:
            k["gece"] = bool(t["gece_vardiyasi"])
        kisi.setdefault(a["calisan"], []).append(k)
    for c in g["calisanlar"]:
        c["gecmis_vardiyalar"] = kisi.get(c["id"], [])
        c["gecmis_bilinen_gunler"] = list(range(-7, 0))
    return g


def _hafta_1():
    g1 = _iki_asama_sahnesi(talep=[(d, 23) for d in (4, 5, 6)])
    g1["sabit_atamalar"] = [{"calisan": "C1", "gun": d, "sablon": GECE["id"]}
                            for d in (4, 5, 6)]
    h1 = _coz(g1)
    assert h1["durum"] == "cozuldu", h1.get("durum")
    geceler = sorted(a["gun"] for a in h1["atamalar"]
                     if a["calisan"] == "C1" and a["sablon"] == GECE["id"])
    assert geceler == [4, 5, 6], (
        "hafta 1 beklendigi gibi kurulmadi -- C1 geceleri: %r" % geceler)
    return h1


def test_IKI_ASAMA_cozucunun_ciktisi_hafta_2yi_GERCEKTEN_kisitlar():
    """Hafta 1'in COZUCU CIKTISI gecmis olunca pazartesi gecesi yasaklanir."""
    h1 = _hafta_1()
    g2 = _gecmise_cevir(_iki_asama_sahnesi(talep=[(0, 23)]), h1["atamalar"])
    h2 = _coz(g2)
    assert h2["durum"] != "cozuldu", (
        "cuma-cumartesi-pazar gecesi calismis tek gece calisanina pazartesi "
        "gecesi yazildi: %r" % [(a["calisan"], a["gun"])
                                for a in h2.get("atamalar") or []])


def test_IKI_ASAMA_gecmis_OLMADAN_ayni_hafta_cozulur():
    """Karsi kanit: ayni hafta 2, gecmis verilmeden cozulur. Yani onceki
    testteki cozumsuzlugun TEK sebebi gecmistir -- sahnenin kendisi degil."""
    g2 = _iki_asama_sahnesi(talep=[(0, 23)])
    assert _coz(g2)["durum"] == "cozuldu"


def test_IKI_ASAMA_denetci_de_AYNI_seyi_gorur():
    """Iki taraf ayni gecmis hakkinda anlasmali: gecmissiz uretilen hafta 2
    plani, gecmisi bilen denetciye gore IHLALDIR."""
    h1 = _hafta_1()
    g2_bez = _iki_asama_sahnesi(talep=[(0, 23)])
    h2 = _coz(g2_bez)
    assert h2["durum"] == "cozuldu", h2.get("durum")
    g2 = _gecmise_cevir(_iki_asama_sahnesi(talep=[(0, 23)]), h1["atamalar"])
    ih = [i for i in degerlendir(g2, h2["atamalar"])["ihlaller"]
          if i["kural"] == "ARDISIK_GECE_LIMIT"]
    assert len(ih) == 1 and ih[0]["olculen"] == 4, ih
