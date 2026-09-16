# -*- coding: utf-8 -*-
"""
DOGRULAYICI BIRIM TESTLERI

NE KORUYORLAR
  Her test, SESSIZCE bozulabilecek bir URUN KARARINI sabitler. Buradaki
  her iddia bir K-numarasina ya da sartname maddesine bagli; hicbiri
  "kod boyle yaziyor" diye yazilmadi.

  Altin senaryolar (A4, A8) bu kurallarin BIRLIKTE dogru calistigini
  sinar. Bunlar tek tek ve kenar durumlarda sinar. Ikisi ayri is:
  A4 yesil yanarken bu testlerden biri kirmizi yanabilir -- o zaman
  A4 dogru sebeple degil, sansla yesildir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogrulayici import degerlendir, yayin_kapisi          # noqa: E402
from dogrulayici import zaman                              # noqa: E402


# ----------------------------------------------------------------------
# Kucuk sahne kurucular -- fikstur dosyalarina BAGLI DEGIL
# ----------------------------------------------------------------------

def kural(kod, tur="SERT", yasal=False, kabul=False, **par):
    d = {"kod": kod, "tur": tur, "yasal": yasal, "kabul_edilebilir": kabul}
    if par:
        d["parametreler"] = par
    return d


def calisan(kimlik, tip="tam_zamanli", saat=45, **ek):
    d = {"id": kimlik, "ekipler": ["E1"],
         "sozlesme": {"tip": tip, "haftalik_saat": saat},
         "izinler": [], "uygunluk": []}
    d.update(ek)
    return d


def atama(kimlik, gun, bas, bit, molalar=(), ekip="E1"):
    return {"calisan": kimlik, "ekip": ekip, "gun": gun, "bas": bas, "bit": bit,
            "molalar": [{"bas": b, "bit": s} for b, s in molalar]}


def sahne(kurallar, calisanlar=None, talep=None):
    return {"calisanlar": calisanlar or [calisan("C1")],
            "talep": talep or [], "kurallar": kurallar,
            "kilitler": [], "donmus_gunler": []}


def kodlar(sonuc, agirlik=None):
    return [i["kural"] for i in sonuc["ihlaller"]
            if agirlik is None or i["agirlik"] == agirlik]


# ----------------------------------------------------------------------
# Zaman modeli -- #6.3 Z-1 ... Z-6
# ----------------------------------------------------------------------

def test_gece_yarisini_asan_vardiya_dogru_uzunlukta():
    """Z-1: 16:00-01:00 dokuz saattir, eksi yedi degil."""
    assert zaman.brut_saat(atama("C1", 1, 16, 25)) == 9


def test_gece_yarisini_asan_vardiya_BASLADIGI_gune_sayilir():
    """Z-2: Cumartesi 16:00-01:00 Pazar'a tasar ama CUMARTESI'ye yazilir.

    Bu satir bozulursa Cumartesi nobetleri Pazar'a kayar ve hafta tatili
    hesabi sessizce yanlis olur.
    """
    assert zaman.calisilan_gunler([atama("C1", 5, 16, 25)]) == {5}


def test_cakisma_mutlak_zamanda_olculur():
    """Z-3: gun sinirini asan vardiyalar dahil."""
    gece = atama("C1", 1, 16, 25)      # Pzt 16:00 - Sali 01:00
    sabah = atama("C1", 2, 0, 8)       # Sali 00:00 - 08:00
    assert zaman.ortusme(gece, sabah) == 1


def test_ucu_uca_degen_vardiyalar_cakismaz():
    """Biri 16'da biter, digeri 16'da baslar -- ortusme YOK."""
    assert not zaman.ortusuyor_mu(atama("C1", 1, 8, 16), atama("C1", 1, 16, 22))


def test_dinlenme_gercek_bitisten_olculur():
    """Z-4: 16:00-01:00 biten kisi 09:00 baslarsa 8 saat dinlenmistir."""
    assert zaman.ara_saat(atama("C1", 1, 16, 25), atama("C1", 2, 9, 18)) == 8


# ----------------------------------------------------------------------
# K-11 -- sinir degeri
# ----------------------------------------------------------------------

def test_tam_11_saat_dinlenme_IHLAL_DEGIL():
    """K-11: 'asgari 11 saat' 11'i KAPSAR.

    Bu, 15 Eylul'de geri alinan K-1'in yerine gecen karardir. Bozulursa
    sistem kurallara uyan planlari reddetmeye baslar.
    """
    s = degerlendir(
        sahne([kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=11)]),
        [atama("C1", 1, 16, 25), atama("C1", 2, 12, 21)])   # tam 11 saat
    assert kodlar(s) == []


def test_11_saatin_bir_dakika_altisi_IHLALDIR():
    """Sinirin altinda kalan gercekten yakalanmali -- yoksa ustteki test
    'hicbir ihlal bulamayan' bir dogrulayiciyla da yesil yanar."""
    s = degerlendir(
        sahne([kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=11)]),
        [atama("C1", 1, 16, 25), atama("C1", 2, 11.9, 20)])
    assert kodlar(s) == ["VARDIYA_ARASI_DINLENME"]


# ----------------------------------------------------------------------
# V-1 -- ortusmede yalniz cakisma yazilir
# ----------------------------------------------------------------------

def test_ortusmede_YALNIZ_cakisma_yazilir():
    """V-1: ayni olay iki kez raporlanmaz.

    Ortusen iki vardiyanin 'arasi' negatiftir; naif bir uygulama bunu
    'dinlenme ihlali' olarak da yazar ve kullanici tek sorunu iki kez gorur.
    """
    s = degerlendir(
        sahne([kural("CAKISMA_YOK"), kural("VARDIYA_ARASI_DINLENME", yasal=True)]),
        [atama("C1", 1, 16, 25), atama("C1", 2, 0, 8)])
    assert kodlar(s) == ["CAKISMA_YOK"]


# ----------------------------------------------------------------------
# K-4 -- mola hakki BRUT sureye bakar
# ----------------------------------------------------------------------

def test_mola_hakki_BRUT_sureye_bakar():
    """K-4: 9 saat sahada / 8 saat net olan vardiya 60 dk mola ister.

    Net sureye bakan bir uygulama 8 saat gorur, '4-7,5 ustu' bandina yine
    girer ve ayni sonucu verir -- bu yuzden ayirt edici vaka asagida.
    """
    s = degerlendir(sahne([kural("MOLA_HAKKI", yasal=True)]),
                    [atama("C1", 0, 9, 18, [(12, 13)])])      # 9 brut, 60 dk
    assert kodlar(s) == []


def test_mola_hakki_net_sureye_bakarsa_YAKALANIR():
    """Ayirt edici vaka: 8 saat brut, 30 dk mola -> net 7,5.

    BRUT okuma  : 8 > 7,5  -> 60 dk gerekir -> IHLAL
    NET okuma   : 7,5 <= 7,5 -> 30 dk yeter -> ihlal yok
    Bu test, K-4'un gercekten brut uygulandigini kanitlar.
    """
    s = degerlendir(sahne([kural("MOLA_HAKKI", yasal=True)]),
                    [atama("C1", 0, 8, 16, [(12, 12.5)])])
    assert kodlar(s) == ["MOLA_HAKKI"]


def test_dort_saatlik_vardiya_15_dk_ile_yeterli():
    """'<=4 saat' bandi. Cumartesi nobeti (V-CMT) bu banda giriyor."""
    s = degerlendir(sahne([kural("MOLA_HAKKI", yasal=True)]),
                    [atama("C1", 5, 9, 13, [(11, 11.25)])])
    assert kodlar(s) == []


# ----------------------------------------------------------------------
# K-18 -- gunluk azami 11, 9 degil
# ----------------------------------------------------------------------

def test_gunluk_azami_varsayilani_11():
    """K-18: kanunun degeri 11 (Is K. md. 63/2). 9 bizim eski
    varsayilanimizdi ve sartnamede yanlislikla 'kanun' diye etiketlenmisti."""
    s = degerlendir(sahne([kural("GUNLUK_AZAMI", yasal=True)]),
                    [atama("C1", 0, 8, 19, [(12, 13)])])       # 10 saat net
    assert kodlar(s) == []


def test_gunluk_azami_11_ustu_ihlal():
    s = degerlendir(sahne([kural("GUNLUK_AZAMI", yasal=True)]),
                    [atama("C1", 0, 7, 20, [(12, 13)])])       # 12 saat net
    assert kodlar(s) == ["GUNLUK_AZAMI"]


# ----------------------------------------------------------------------
# Kapsama -- asgari mola SAYAR, mola kapsamasi mola DUSER
# ----------------------------------------------------------------------

TALEP = [{"ekip": "E1", "gunler": [0], "saatler": [12], "asgari": 3, "hedef": 3}]


def test_asgari_kapsama_molayi_SAYMAZ_yani_dusurmez():
    """Uc kisi de 12:00'de molada ama UCU DE ATANMIS -> ASGARI_KAPSAMA tamam.

    Ikisini karistiran bir uygulama bu plani GECERSIZ yapardi; oysa dogru
    davranis yumusak MOLA_KAPSAMASI ihlali yazmaktir (K-14).
    """
    at = [atama("C%d" % i, 0, 9, 18, [(12, 13)]) for i in (1, 2, 3)]
    s = degerlendir(
        sahne([kural("ASGARI_KAPSAMA")],
              calisanlar=[calisan("C%d" % i) for i in (1, 2, 3)], talep=TALEP),
        at)
    assert kodlar(s) == []


def test_mola_kapsamasi_molayi_DUSER_ve_YUMUSAKTIR():
    at = [atama("C%d" % i, 0, 9, 18, [(12, 13)]) for i in (1, 2, 3)]
    s = degerlendir(
        sahne([kural("MOLA_KAPSAMASI", tur="YUMUSAK")],
              calisanlar=[calisan("C%d" % i) for i in (1, 2, 3)], talep=TALEP),
        at)
    assert kodlar(s, "YUMUSAK") == ["MOLA_KAPSAMASI"]
    assert kodlar(s, "SERT") == []
    assert s["metrikler"]["sert_ihlal"] == 0, "yumusak ihlal plani gecersiz KILMAZ"


# ----------------------------------------------------------------------
# PART_TIME_LIMIT -- toleranssiz (Fazla Calisma Yon. md. 8)
# ----------------------------------------------------------------------

def test_part_time_sozlesme_saati_toleranssiz():
    s = degerlendir(
        sahne([kural("PART_TIME_LIMIT", yasal=True, tolerans_saat=0)],
              calisanlar=[calisan("C1", tip="yari_zamanli", saat=20)]),
        [atama("C1", g, 9, 18, [(12, 13)]) for g in range(3)])   # 24 saat net
    assert kodlar(s) == ["PART_TIME_LIMIT"]


def test_tam_zamanliya_part_time_limiti_UYGULANMAZ():
    s = degerlendir(
        sahne([kural("PART_TIME_LIMIT", yasal=True)],
              calisanlar=[calisan("C1", tip="tam_zamanli", saat=45)]),
        [atama("C1", g, 9, 18, [(12, 13)]) for g in range(3)])
    assert kodlar(s) == []


# ----------------------------------------------------------------------
# K-24 -- yayin kapisi kabul_edilebilir'e bakar, yasal'a DEGIL
# ----------------------------------------------------------------------

def test_yayin_kapisi_imkansizligi_da_engeller():
    """CAKISMA_YOK yasal DEGIL ama kabul da EDILEMEZ.

    Kapi `yasal` alanina bakarsa bu plan yayinlanabilir gorunur -- K-24'un
    tam olarak engellemek icin var oldugu hata.
    """
    kapi = yayin_kapisi([{"kural": "CAKISMA_YOK", "agirlik": "SERT",
                          "yasal": False, "kabul_edilebilir": False}])
    assert kapi["yayinlanabilir"] is False
    assert kapi["kabul_secenegi_sunulur"] is False
    assert [i["kural"] for i in kapi["engelleyen_ihlaller"]] == ["CAKISMA_YOK"]


def test_yayin_kapisi_firma_kuralinda_kabul_secenegi_sunar():
    kapi = yayin_kapisi([{"kural": "ROL_KAPSAMASI", "agirlik": "SERT",
                          "yasal": False, "kabul_edilebilir": True}])
    assert kapi["yayinlanabilir"] is False
    assert kapi["kabul_secenegi_sunulur"] is True


def test_kabul_edilmis_ihlal_yayini_engellemez():
    kapi = yayin_kapisi([{"kural": "ROL_KAPSAMASI", "agirlik": "SERT",
                          "yasal": False, "kabul_edilebilir": True,
                          "durum": "kabul_edildi"}])
    assert kapi["yayinlanabilir"] is True


def test_yumusak_ihlal_yayini_engellemez():
    kapi = yayin_kapisi([{"kural": "MOLA_KAPSAMASI", "agirlik": "YUMUSAK",
                          "yasal": False, "kabul_edilebilir": False}])
    assert kapi["yayinlanabilir"] is True


# ----------------------------------------------------------------------
# Sessiz gecmeme ilkesi
# ----------------------------------------------------------------------

def test_govdesi_olmayan_kural_SESSIZCE_GECILMEZ():
    """'Ihlal bulamadim' ile 'bakmadim' ayni sey degildir.

    Bu testin korudugu sey, dogrulayicinin en tehlikeli basarisizlik
    bicimidir: bilmedigi kurali gormezden gelip plani temiz gostermek.
    """
    s = degerlendir(sahne([kural("HENUZ_YAZILMAMIS_KURAL")]), [])
    assert s["uygulanmayan_kurallar"] == ["HENUZ_YAZILMAMIS_KURAL"]


def test_pasif_kural_uygulanmayan_sayilmaz():
    t = kural("HENUZ_YAZILMAMIS_KURAL")
    t["aktif"] = False
    s = degerlendir(sahne([t]), [])
    assert s["uygulanmayan_kurallar"] == []


def test_adalet_dengesi_bilerek_yazilmadi():
    """ADALET_DENGESI'nin ihlal esigi sartnamede TANIMSIZ (T-12).

    Esigi koda gomup uydurmak, urun kararini gizlemek olurdu. Kural
    uygulanmayanlar listesinde gorunur. Bu test, birinin ilerde sessizce
    bir esik uydurmasini engeller -- yazarsa bu test kirmizi yanar ve
    T-12'nin kapatildigini kanitlamasi gerekir.
    """
    s = degerlendir(sahne([kural("ADALET_DENGESI", tur="YUMUSAK")]), [])
    assert "ADALET_DENGESI" in s["uygulanmayan_kurallar"], (
        "ADALET_DENGESI yazildiysa T-12 kapanmis olmali; bu testi guncelle")


# ----------------------------------------------------------------------
# Metrikler
# ----------------------------------------------------------------------

def test_talep_yokken_kapsama_yuzde_100_ama_bu_MUKEMMEL_DEMEK_DEGIL():
    """A4 gibi yalitilmis senaryolarda talep bilerek bostur.

    %100 burada 'sinanacak hucre yoktu' demektir. Bir raporda 'kapsama
    mukemmel' diye sunulursa yanlis olur; not olarak buraya yazildi.
    """
    s = degerlendir(sahne([kural("CAKISMA_YOK")]), [atama("C1", 0, 9, 18)])
    assert s["metrikler"]["asgari_kapsama_yuzde"] == 100.0


def test_eksik_hedef_dakika_hesaplanir():
    """T-4: A9 bu metrik olmadan olculemiyordu."""
    s = degerlendir(sahne([kural("HEDEF_KAPSAMA", tur="YUMUSAK")],
                          talep=[{"ekip": "E1", "gunler": [0], "saatler": [9, 10],
                                  "asgari": 1, "hedef": 3}]),
                    [atama("C1", 0, 9, 18)])
    assert s["metrikler"]["eksik_hedef_dakika"] == 240      # 2 saat x 2 eksik kisi x 60


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
