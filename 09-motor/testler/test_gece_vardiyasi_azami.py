# -*- coding: utf-8 -*-
"""
GECE_VARDIYASI_AZAMI -- YASAL SINIR VE SEKTOR ISTISNASI (K-26)

NE DIYOR
  Is K. md. 69 / Postalar Yonetmeligi md. 7: iscinin gece calismasi
  7,5 saati gecemez. Gece penceresi 20:00-06:00 (parametre).

  6645 sayili Kanun (23 Nisan 2015) ISTISNA getirdi: turizm, ozel
  guvenlik, saglik hizmeti ve petrol arama/sondaj islerinde, calisanin
  YAZILI ONAYIYLA sinir asilabilir.

      firma.sektor istisna listesinde  VE  calisanin yazili onayi var
          -> sinir O CALISAN icin uygulanmaz
      ikisinden biri eksikse
          -> 7,5 saat yururluktedir ve ihlali YASAL ihlaldir

  ⚠ Bu, K-24'un ucuncu bicimi: orada bayrak kural SATIRINA bagliydi,
    burada CALISANA bagli. Ayni ilke -- bir kuralin yasal olup olmamasi
    baglama gore degisiyor.

NEDEN ONEMLI (K-26'nin gerekcesi)
  Elimizdeki tek gercek musteri verisi bir SEYAHAT ACENTESINE ait --
  turizm -- ve o veride 182 atama gece yarisini asiyor. Istisna olmadan
  sistem o firmada gece 8 saatlik vardiyayi yasal ihlal sayar, K-20
  geregi kabul secenegi SUNMAZ ve plan yayinlanamaz. Oysa yazili onay
  varsa tamamen yasaldir.

OLCU: NET CALISMA, PENCEREYE DUSEN KISIM
  `GUNLUK_AZAMI` ile ayni gelenek: sure kurallari NET saate bakar
  (molalar dusuk). Buradaki fark yalnizca hangi aralikta olculdugu.
  Penceresine 4 saat dusen 8 saatlik bir aksam vardiyasi bu kurali
  ILGILENDIRMEZ.

  Z-5: pencere GUN SINIRINI ASARAK hesaplanir. 19:00-05:00 vardiyasinin
  gece kismi 20:00-05:00 = 9 saattir; yalniz takvim gunune bakan bir
  govde 20:00-24:00 = 4 saat gorur ve ihlali KACIRIR.

⚠ VERI SETI BU KURALI ZORLAMIYOR -- acikca yaziyorum
  500 kisilik sahnedeki en uzun gece ortusmesi S-GECE'de 7,00 saat,
  yani sinirin altinda. Kural veri setinde ihlal uretmez; zorlayan
  yalniz bu testler ve ihlal vakasi. T-63'un dersi: tanimli olmak,
  istemek degildir -- ve bu kez tanimliyi ISTEYEN taraf testler.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_gece_vardiyasi_azami.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir                            # noqa: E402

KURAL = {"kod": "GECE_VARDIYASI_AZAMI", "tur": "SERT", "aktif": True,
         "yasal": True, "kabul_edilebilir": False,
         "parametreler": {"azami_saat": 7.5, "pencere_bas": 20,
                          "pencere_bit": 6}}


def _c(kimlik="C1", onay=None):
    c = {"id": kimlik, "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
         "izinler": [], "uygunluk": []}
    if onay is not None:
        c["gece_calisma_onayi"] = onay
    return c


def _sahne(sektor=None, calisanlar=None):
    g = {
        "profil": "DENGELI",
        "calisanlar": list(calisanlar or [_c()]),
        "vardiya_sablonlari": [{"id": "V", "ekip": "E", "bas": 21, "bit": 30,
                                "mola_dk": 0}],
        "talep": [],
        "kurallar": [KURAL],
        "kilitler": [], "donmus_gunler": [],
    }
    if sektor is not None:
        g["sektor"] = sektor
    return g


def _atama(bas, bit, gun=0, kimlik="C1", molalar=None):
    return {"calisan": kimlik, "ekip": "E", "sablon": "V", "gun": gun,
            "bas": bas, "bit": bit, "molalar": molalar or []}


def _ihlaller(g, atamalar):
    r = degerlendir(g, atamalar)
    return [i for i in r["ihlaller"] if i["kural"] == "GECE_VARDIYASI_AZAMI"]


# ----------------------------------------------------------------------
# 1. Govde var mi
# ----------------------------------------------------------------------

def test_govdesi_ARTIK_VAR():
    """Kural `uygulanmayan_kurallar` listesinde GORUNMEMELI."""
    r = degerlendir(_sahne(), [_atama(22, 29)])
    assert "GECE_VARDIYASI_AZAMI" not in r["uygulanmayan_kurallar"], (
        "kural hala govdesiz: %r" % r["uygulanmayan_kurallar"])


# ----------------------------------------------------------------------
# 2. Sinirin kendisi
# ----------------------------------------------------------------------

def test_SINIR_asilirsa_ihlal():
    """21:00-06:00, molasiz -> gece penceresine 9 saat dusuyor."""
    ih = _ihlaller(_sahne(), [_atama(21, 30)])
    assert len(ih) == 1, "bir ihlal bekleniyordu, %d cikti" % len(ih)
    assert abs(ih[0]["olculen"] - 9.0) < 1e-6, ih[0]
    assert ih[0]["gereken"] == 7.5, ih[0]


def test_SINIR_altinda_ihlal_YOK():
    """22:00-05:00 = 7 saat, sinirin altinda."""
    assert not _ihlaller(_sahne(), [_atama(22, 29)])


def test_SINIRIN_TAM_USTUNDE_ihlal_yok():
    """22:00-05:30 = 7,5 saat. Kanun "gecemez" diyor; esit gecmek degildir."""
    assert not _ihlaller(_sahne(), [_atama(22, 29.5)])


# ----------------------------------------------------------------------
# 3. ⚠ Olcu NET -- molalar dusulur (GUNLUK_AZAMI ile ayni gelenek)
# ----------------------------------------------------------------------

def test_MOLA_gece_calismasindan_DUSULUR():
    """21:00-06:00 (9 saat) ama pencerenin icinde 2 saat mola var -> 7 saat.

    ⚠ Bu test olcuyu sabitliyor. Brut olcen bir govde burada ihlal
      yazardi; `GUNLUK_AZAMI` net saate baktigi icin bu kural da bakar.
    """
    ih = _ihlaller(_sahne(), [_atama(21, 30, molalar=[
        {"tip": "yemek", "bas": 1, "bit": 3, "ucretli": False}])])
    assert not ih, (
        "molasi dusulunce 7 saat kaliyor, ihlal olmamali: %r"
        % [i.get("olculen") for i in ih])


def test_PENCERE_DISINDAKI_mola_gece_saatini_azaltmaz():
    """Mola gunduze dusuyorsa gece calismasindan DUSULMEZ.

    19:00-05:00 vardiyasinda 19:00-19:30 molasi penceredeki 9 saati
    degistirmez -- o mola gece penceresinin icinde degil.
    """
    ih = _ihlaller(_sahne(), [_atama(19, 29, molalar=[
        {"tip": "dinlenme", "bas": 19, "bit": 19.5, "ucretli": True}])])
    assert len(ih) == 1, "ihlal bekleniyordu: %r" % ih
    # K-44 (30 Eylul gecesi): 19:00-05:00 gece postasidir (9/10); ihlal
    # BUTUN net sureyle yazilir: 10 - 0,5 = 9,5. Pencere olcusu (9,0) ayni
    # vardiya icin ikinci kez yazilmaz (V-1). Pencere hesabinin kendisi
    # asagida ayrica sinaniyor.
    assert abs(ih[0]["olculen"] - 9.5) < 1e-6, ih[0]
    from dogrulayici import kurallar as K
    w0, w1 = [(b, e) for g, b, e in K._gece_pencereleri(20, 6) if g == 0][0]
    assert abs(K._gece_net_saat(_atama(19, 29, molalar=[
        {"tip": "dinlenme", "bas": 19, "bit": 19.5, "ucretli": True}]),
        w0, w1) - 9.0) < 1e-6, "pencere disindaki mola pencereden dusuldu"


# ----------------------------------------------------------------------
# 4. Yalniz PENCEREYE DUSEN kisim sayilir
# ----------------------------------------------------------------------

def test_GUNDUZ_kismi_SAYILMAZ():
    """16:00-24:00 = 8 saat vardiya, ama gecesi 20:00-24:00 = 4 saat."""
    assert not _ihlaller(_sahne(), [_atama(16, 24)])


def test_Z5_pencere_GUN_SINIRINI_asarak_hesaplanir():
    """⚠ 19:00-05:00 -- gece kismi 20:00-05:00 = 9 saat.

    Yalniz takvim gunune bakan bir govde 20:00-24:00 = 4 saat gorur ve
    ihlali KACIRIR. Sartname Z-5 tam bunu soyluyor.
    """
    ih = _ihlaller(_sahne(), [_atama(19, 29)])
    assert len(ih) == 1, (
        "gun sinirini asan pencere hesaplanmamis -- ihlal kacirildi")
    # K-44: gece postasi -> butun sure (10 sa). Z-5'in kendisi pencere
    # hesabinda sinanir: 20:00-05:00 = 9 saat, takvim gunune bakan bir
    # hesap 4 gorurdu.
    assert abs(ih[0]["olculen"] - 10.0) < 1e-6, ih[0]
    from dogrulayici import kurallar as K
    w0, w1 = [(b, e) for g, b, e in K._gece_pencereleri(20, 6) if g == 0][0]
    assert abs(K._gece_net_saat(_atama(19, 29), w0, w1) - 9.0) < 1e-6, (
        "pencere gun sinirini asarak hesaplanmadi (Z-5)")


# ----------------------------------------------------------------------
# 4b. K-44 -- GECE POSTASININ BUTUN SURESI (30 Eylul gecesi)
# ----------------------------------------------------------------------
#
# Postalar Yon. md. 7/2: "Calisma suresinin yarisindan cogu gece donemine
# rastlayan bir postanin calismasi, gece calismasi sayilir." Yargitay 9. HD
# 2016/36126 E., 2020/17967 K.: 20:00-08:00 vardiyasinda gece hesabi
# 06:00'da kesilmez, fiili bitis 08:00'e kadar yapilir.
#
# 30 Eylul gecesine kadar yalniz pencereye dusen kisim olculuyordu; bu olcu
# hicbir durumda yonetmelikten SIKI degildi -- 22:00-08:00'i yasal sayiyordu.

def test_K44_gece_postasinin_BUTUN_suresi_sayilir_22_08():
    """22:00-08:00, 1 saat mola: pencerede 7 sa (eski olcu: yasal), butun
    net sure 9 sa -> IHLAL. Yargitay'in okumasi."""
    ih = _ihlaller(_sahne(), [_atama(22, 32, molalar=[
        {"tip": "yemek", "bas": 26, "bit": 27, "ucretli": False}])])
    assert len(ih) == 1, "gece postasinin gunduze tasan kismi sayilmadi (K-44)"
    assert abs(ih[0]["olculen"] - 9.0) < 1e-6, ih[0]
    assert "yarisindan cogu" in ih[0]["mesaj"], ih[0]["mesaj"]


def test_K44_gercek_musterinin_16_01_deseni_IHLAL():
    """16:00-01:00, 1 saat mola: 9 saatin 5'i gecede -> gece postasi ->
    8 saat net > 7,5. Gercek veride 82 kez (B-2); yazili onaysiz yasa disi."""
    ih = _ihlaller(_sahne(), [_atama(16, 25, molalar=[
        {"tip": "yemek", "bas": 20, "bit": 21, "ucretli": False}])])
    assert len(ih) == 1 and abs(ih[0]["olculen"] - 8.0) < 1e-6, ih


def test_K44_yarisi_gecede_olan_posta_GECE_DEGIL_sinir_yok():
    """15:00-01:00 (10 sa, tam yarisi gecede): gece postasi degil; 9 saat
    net calisma bu kurala takilmaz (GUNLUK_AZAMI'ye takilir, o ayri)."""
    ih = _ihlaller(_sahne(), [_atama(15, 25, molalar=[
        {"tip": "yemek", "bas": 19, "bit": 20, "ucretli": False}])])
    assert not ih, ih


def test_K44_gece_postasi_tam_7_5_saat_IHLAL_DEGIL():
    """23:00-07:30, 1 saat mola: 7,5 net -- kanun 'gecemez' diyor."""
    assert not _ihlaller(_sahne(), [_atama(23, 31.5, molalar=[
        {"tip": "yemek", "bas": 26, "bit": 27, "ucretli": False}])])


def test_K44_ayni_vardiya_IKI_KEZ_yazilmaz():
    """20:00-08:00, 1,5 sa mola: posta olcusu 10,5 sa ihlal; pencere olcusu
    (20-06: 10 sa - mola) de asar. Tek ihlal yazilir (V-1)."""
    ih = _ihlaller(_sahne(), [_atama(20, 32, molalar=[
        {"tip": "yemek", "bas": 24, "bit": 25.5, "ucretli": False}])])
    assert len(ih) == 1, ih
    assert abs(ih[0]["olculen"] - 10.5) < 1e-6, ih[0]


def test_K44_istisnali_calisan_gece_postasinda_da_MUAF():
    """Turizm + yazili onay: 22:00-08:00 (9 sa net) serbest."""
    g = _sahne(sektor="turizm", calisanlar=[_c(onay=True)])
    assert not _ihlaller(g, [_atama(22, 32, molalar=[
        {"tip": "yemek", "bas": 26, "bit": 27, "ucretli": False}])])


def test_K44_firmanin_gece_DEGIL_isareti_yasal_kurali_delemez():
    """Sablon 'gece degil' isaretli olsa da 22:00-08:00 yonetmelige gore
    gece postasidir (K-43 + K-44)."""
    g = _sahne()
    g["vardiya_sablonlari"][0]["gece_vardiyasi"] = False
    assert _ihlaller(g, [_atama(22, 32, molalar=[
        {"tip": "yemek", "bas": 26, "bit": 27, "ucretli": False}])])


# ----------------------------------------------------------------------
# 4c. PENCERE olcusu hala gerekli: ayni geceyi paylasan IKI vardiya
# ----------------------------------------------------------------------
#
# Posta olcusu vardiya basinadir. Pazartesi 16:00-24:00 (4/8, gece postasi
# degil) + sali 00:00-06:00 (6/6 gece postasi ama 6 sa) -- ikisi de tek
# basina yasal, ayni geceye 10 saat. Bunu yalniz PENCERE olcusu gorur.
# (Dinlenme kurali aktifken bu iki vardiya zaten yan yana gelemez; bu
#  test yalniz gece sinirini calistirir.)

def _bolunmus_gece(kimlik="C1"):
    return [_atama(16, 24, gun=0, kimlik=kimlik), _atama(0, 6, gun=1, kimlik=kimlik)]


def test_PENCERE_bolunmus_geceyi_toplar():
    ih = _ihlaller(_sahne(), _bolunmus_gece())
    assert len(ih) == 1 and abs(ih[0]["olculen"] - 10.0) < 1e-6, ih


def test_PENCERE_istisna_sektor_VE_onay_ister():
    """Istisnanin iki sarti pencere olcusunde de birlikte aranir."""
    assert not _ihlaller(_sahne(sektor="turizm", calisanlar=[_c(onay=True)]),
                         _bolunmus_gece())
    assert _ihlaller(_sahne(sektor="turizm", calisanlar=[_c()]),
                     _bolunmus_gece()), "yalniz sektorle pencere olcusu kalkti"
    assert _ihlaller(_sahne(sektor="cagri_merkezi", calisanlar=[_c(onay=True)]),
                     _bolunmus_gece()), "yalniz onayla pencere olcusu kalkti"


# ----------------------------------------------------------------------
# 5. SEKTOR ISTISNASI -- K-26
# ----------------------------------------------------------------------

def test_ISTISNA_sektor_VE_onay_varsa_sinir_UYGULANMAZ():
    """Turizm + yazili onay -> o calisan icin sinir yok."""
    g = _sahne(sektor="turizm", calisanlar=[_c(onay=True)])
    assert not _ihlaller(g, [_atama(21, 30)]), (
        "turizmde yazili onayli calisan icin sinir uygulanmamali")


def test_ISTISNA_sektor_dogru_ama_ONAY_yoksa_sinir_ISLER():
    """⚠ Ikisinden biri eksikse sinir yururluktedir (K-26)."""
    g = _sahne(sektor="turizm", calisanlar=[_c()])
    assert _ihlaller(g, [_atama(21, 30)]), (
        "onayi olmayan calisan icin sinir islemeli")


def test_ISTISNA_onay_var_ama_SEKTOR_disindaysa_sinir_ISLER():
    """Cagri merkezi istisna listesinde yok; onay tek basina yetmez."""
    g = _sahne(sektor="cagri_merkezi", calisanlar=[_c(onay=True)])
    assert _ihlaller(g, [_atama(21, 30)]), (
        "istisna disi sektorde onay tek basina sinirı kaldirmamali")


def test_ISTISNA_KISI_BAZLI_ayni_sahnede_biri_muaf_biri_degil():
    """⚠ Bayrak CALISANA bagli, kurala degil -- K-24'un ucuncu bicimi.

    Ayni firmada, ayni vardiyada, biri onayli biri onaysiz: ihlal
    yalniz onaysiz kisi icin yazilmali.
    """
    g = _sahne(sektor="turizm",
               calisanlar=[_c("C1", onay=True), _c("C2")])
    ih = _ihlaller(g, [_atama(21, 30, kimlik="C1"),
                       _atama(21, 30, kimlik="C2")])
    assert {i["calisan"] for i in ih} == {"C2"}, (
        "istisna kisi bazli uygulanmiyor: %r" % [i["calisan"] for i in ih])


def test_ONAYIN_SURESI_gecmisse_sinir_ISLER():
    """Onay tarihsizse suresiz sayilir; bitis tarihi varsa denetlenir.

    `SOZLESME_GECERLI` ile ayni gelenek: tarih yoksa sessiz gecmek bir
    atlama degil, "suresiz" demektir.
    """
    g = _sahne(sektor="turizm", calisanlar=[
        _c(onay={"onay": True, "gecerli_bitis": "2026-01-01"})])
    g["hafta_baslangic"] = "2026-09-28"
    assert _ihlaller(g, [_atama(21, 30)]), (
        "suresi gecmis onay istisnayi acmamali")


def test_SURESIZ_onay_gecerlidir():
    g = _sahne(sektor="turizm", calisanlar=[_c(onay={"onay": True})])
    g["hafta_baslangic"] = "2026-09-28"
    assert not _ihlaller(g, [_atama(21, 30)])


# ----------------------------------------------------------------------
# 6. YASAL ihlal kabul secenegi ALMAZ -- K-20
# ----------------------------------------------------------------------

def test_YASAL_ihlal_kabul_edilebilir_DEGIL():
    """K-20: yasal ihlal icin yoneticiye "kabul et" secenegi sunulmaz.

    Sartname #5.3: yasal true ise kabul_edilebilir HER ZAMAN false.
    """
    r = degerlendir(_sahne(), [_atama(21, 30)])
    ih = [i for i in r["ihlaller"] if i["kural"] == "GECE_VARDIYASI_AZAMI"]
    assert ih and ih[0]["yasal"] is True, ih
    assert ih[0]["kabul_edilebilir"] is False, ih[0]
    kapi = r["yayin_kapisi"]
    assert kapi["yayinlanabilir"] is False, kapi
    assert any(i["kural"] == "GECE_VARDIYASI_AZAMI"
               for i in kapi["engelleyen_ihlaller"]), (
        "yasal ihlal yayini ENGELLEMELI, kabul bekleyene dusmemeli: %r" % kapi)

# ----------------------------------------------------------------------
# 7. COZUCU TARAFI
# ----------------------------------------------------------------------
#
# ⚠ Govde testlerden once yazildi; kirmizi kanitlar MUTASYONLA uretildi.
#
# ⚠ SAHNELER T-62'NIN DERSIYLE KURULDU: "dogru sablonu secti mi" sorusu bu
#   motorda tesadufe acik (fazladan atamanin maliyeti yok, T-54). Onun
#   yerine talep oyle konuyor ki onu YALNIZ yasak sablon karsilayabiliyor:
#   kisit yaziliysa plan cozumsuz kalmak ZORUNDA.

UZUN = {"id": "V-UZUN", "ekip": "E", "bas": 21, "bit": 30, "mola_dk": 0}
KISA = {"id": "V-KISA", "ekip": "E", "bas": 22, "bit": 29, "mola_dk": 0}


def _cozucu_sahnesi(sektor=None, onay=None):
    """Talep 21:00 ve 05:00'te -- bu iki saati YALNIZ 21:00-06:00 kapatir.

    22:00-05:00 sablonu ikisini de kapatmiyor. Yani uzun sablon
    yasaksa plan cozumsuz; yasak degilse cozulur.
    """
    g = {
        "profil": "DENGELI",
        "calisanlar": [_c(onay=onay)],
        "vardiya_sablonlari": [dict(UZUN), dict(KISA)],
        "talep": [{"ekip": "E", "gun": 0, "saat": 21, "asgari": 1, "hedef": 1},
                  {"ekip": "E", "gun": 0, "saat": 29, "asgari": 1, "hedef": 1}],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            KURAL,
        ],
        "kilitler": [], "donmus_gunler": [],
    }
    if sektor is not None:
        g["sektor"] = sektor
    return g


def test_COZUCU_siniri_asan_sablonu_istisnasiz_kisiye_ATAMAZ():
    """Istisna yok -> 9 saatlik gece sablonu yasak -> plan cozumsuz."""
    from cozucu.coz import coz
    c = coz(_cozucu_sahnesi(), {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu", (
        "gece penceresine 9 saat dusen sablon istisnasiz calisana verildi: "
        "%r" % [(a["sablon"], a["bas"], a["bit"])
                for a in c.get("atamalar") or []])


def test_COZUCU_istisnada_ayni_sablonu_ATAYABILIR():
    """Turizm + yazili onay -> ayni sablon serbest -> plan cozulur."""
    from cozucu.coz import coz
    c = coz(_cozucu_sahnesi(sektor="turizm", onay=True),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", (
        "istisnali calisana izinli sablon verilemedi: %s" % c.get("durum"))
    assert any(a["sablon"] == "V-UZUN" for a in c["atamalar"]), (
        "talebi yalniz uzun sablon karsilayabilir, atanmamis")


def test_COZUCU_istisna_icin_IKI_SART_da_gerekli():
    """Onay var ama sektor disinda -> yasak kalir -> cozumsuz."""
    from cozucu.coz import coz
    c = coz(_cozucu_sahnesi(sektor="cagri_merkezi", onay=True),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu", (
        "istisna disi sektorde onay tek basina sablonu acmamali")


def test_COZUCU_yasakladigini_NOT_olarak_soyler():
    """Brut olcum daha katidir; bunu sessizce yapmamali."""
    from cozucu.coz import coz
    c = coz(_cozucu_sahnesi(sektor="turizm", onay=True),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "V-UZUN" in notlar and "BRUT" in notlar, (
        "sablon yasagi not olarak yazilmamis: %r"
        % (c.get("uygulanmayan_notlar"),))


GUNDUZE_TASAN = {"id": "V-TASAN", "ekip": "E", "bas": 22, "bit": 32, "mola_dk": 60}
YARIM = {"id": "V-YARIM", "ekip": "E", "bas": 15, "bit": 25, "mola_dk": 60}


def _posta_sahnesi(sablon, saatler, sektor=None, onay=None):
    g = _cozucu_sahnesi(sektor=sektor, onay=onay)
    g["vardiya_sablonlari"] = [dict(sablon)]
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": h, "asgari": 1, "hedef": 1}
                  for h in saatler]
    return g


MUSTERI_DESENI = {"id": "V-16-01", "ekip": "E", "bas": 16, "bit": 25, "mola_dk": 60}


def test_COZUCU_K44_gece_postasinin_butun_suresi_sinira_girer():
    """16:00-01:00, 1 sa mola (gercek musterinin deseni): pencerede BRUT 5
    sa -- eski olcu (T-68) serbest birakirdi; ama 9 saatin 5'i gecede ->
    gece postasi -> 8 sa net > 7,5 -> yasak. Talep 16:00 ve 00:00; tek
    sablon, tek kisi -> cozumsuz ZORUNLU. Not K-44'u anmali."""
    from cozucu.coz import coz
    c = coz(_posta_sahnesi(MUSTERI_DESENI, (16, 24)),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu", "8 saatlik gece postasi yazildi (K-44)"
    notlar = " ".join(c.get("uygulanmayan_notlar") or [])
    assert "V-16-01" in notlar and "K-44" in notlar, notlar


MUSTERI_DESENI_YASAL = {"id": "V-16-01-Y", "ekip": "E", "bas": 16, "bit": 25,
                        "mola_dk": 90}


def test_COZUCU_K44_net_olcer_1_5_saat_molali_16_01_YASAL():
    """16:00-01:00, 1,5 sa mola: net 7,5 -> yasal. Brut (9 sa) olcen bir
    govde bunu yasaklardi; plan cozulmeli."""
    from cozucu.coz import coz
    c = coz(_posta_sahnesi(MUSTERI_DESENI_YASAL, (16, 24)),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c.get("durum")


def test_COZUCU_K44_22_08_de_yasak():
    """22:00-08:00: brut pencere olcusu (8 sa) zaten yakalar; K-44 ile ayni
    sonuc. Iki olcu birbirini bozmuyor."""
    from cozucu.coz import coz
    c = coz(_posta_sahnesi(GUNDUZE_TASAN, (22, 31)),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] != "cozuldu"


def test_COZUCU_K44_istisnali_calisana_ayni_sablon_serbest():
    from cozucu.coz import coz
    c = coz(_posta_sahnesi(MUSTERI_DESENI, (16, 24), sektor="turizm", onay=True),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c.get("durum")


def test_COZUCU_K44_yarisi_gecede_olan_posta_serbest():
    """15:00-01:00 (10 sa, tam yari): gece postasi degil -> bu kural
    kisitlamaz (ne posta ne pencere olcusu asiliyor)."""
    from cozucu.coz import coz
    c = coz(_posta_sahnesi(YARIM, (15, 24)),
            {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c.get("durum")


def test_UCTAN_UCA_cozucunun_plani_DENETIMDEN_gecer():
    """Yasal sablonla uretilen plan bagimsiz denetimde temiz cikmali."""
    from cozucu.coz import coz
    g = _cozucu_sahnesi()
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": h, "asgari": 1, "hedef": 1}
                  for h in range(22, 29)]
    c = coz(g, {"azami_saniye": 20, "durgunluk_saniye": 5})
    assert c["durum"] == "cozuldu", c.get("durum")
    assert all(a["sablon"] == "V-KISA" for a in c["atamalar"]), (
        "istisnasiz calisana yasak sablon verilmis")
    assert not _ihlaller(g, c["atamalar"])
