# -*- coding: utf-8 -*-
"""
ALTIN SENARYO TESTLERI -- A1..A12 (A5 ertelendi, K-12)

Her test bir fikstur dosyasini okur, motoru cagirir ve fiksturdeki
`beklenen` blogunu sinar. Fikstur VERIDIR, test onu yorumlar.

SU AN HEPSI KIRMIZI -- cunku motor yazilmadi. Bu ISTENEN DURUM:
Master Spec #16.4 "kirmizi kanit" kurali, testin once kirmizi yanmasini
sart kosar. Motor yazildikca teker teker yesile doner.

⚠ Bu paket CI'da KOSMUYOR. CI su an yalniz `dotnet test` calistiriyor
   (A-4, 14 Eylul). Motor var olunca CI'a eklenecek; kirmizi bir paketi
   simdi kapiya baglamak "main her zaman yesil" kuralini bozardi.

KOSTURMA
  py -m pip install pytest          (bir kereligine)
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\v5\\testler
  py -m pytest -v
"""

import io
import os
import pytest

import fikstur_yukleyici as fy
import kontroller
import motor_istemci as mi
from conftest import fiksturler, fikstur_kimlik, karsilastir


# ----------------------------------------------------------------------
# solve -- motor plan uretir
# ----------------------------------------------------------------------

@pytest.mark.solve
@pytest.mark.parametrize("yol", fiksturler("solve"), ids=fikstur_kimlik)
def test_solve_senaryosu(yol, motor):
    fik, girdi = fy.fikstur_oku(yol)
    bek = fy.temiz(fik.get("beklenen", {}))

    # Alt durumlari olan fiksturler (A9) her alt durumu ayri kosar
    alt = fik.get("alt_durumlar")
    if alt:
        for ad in alt:
            alt_girdi = fy.sahne_uygula(girdi, ad.get("fark"))
            cikti = motor.solve(alt_girdi)
            _solve_dogrula(cikti, alt_girdi, fy.temiz(ad.get("beklenen", {})),
                           "%s/%s" % (fik["senaryo"], ad.get("ad", "?")))
        return

    # Birden cok profille kosanlar (A7)
    cagrilar = fik.get("cagrilar")
    if cagrilar:
        sonuclar = {}
        for c in cagrilar:
            g = dict(girdi, profil=c["profil"])
            sonuclar[c["ad"]] = motor.solve(g)
        for ad, cikti in sonuclar.items():
            _solve_dogrula(cikti, girdi,
                           fy.temiz(bek.get("her_iki_cagri", {})),
                           "%s/%s" % (fik["senaryo"], ad))
        _karsilastirmalar(sonuclar, bek.get("karsilastirma", []), fik["senaryo"])
        return

    cikti = motor.solve(girdi)
    _solve_dogrula(cikti, girdi, bek, fik["senaryo"])


def _solve_dogrula(cikti, girdi, bek, etiket):
    hatalar = []

    if "durum" in bek and cikti.get("durum") != bek["durum"]:
        hatalar.append("durum: %r olmaliydi, %r geldi"
                       % (bek["durum"], cikti.get("durum")))

    for blok in ("metrikler", "cozum_istatistikleri"):
        for alan, kosul in (bek.get(blok) or {}).items():
            if alan.startswith("_"):
                continue
            tamam, mesaj = karsilastir(
                (cikti.get(blok) or {}).get(alan), kosul, "%s.%s" % (blok, alan))
            if not tamam:
                hatalar.append(mesaj)

    if bek.get("en_iyi_plan", {}).get("var") and not cikti.get("en_iyi_plan"):
        hatalar.append("en_iyi_plan bekleniyordu (K-10) ama ciktida yok")

    for d in bek.get("degismezler", []):
        sonuc, mesaj = kontroller.calistir(d["kontrol"], cikti, girdi, d)
        if sonuc is False:
            hatalar.append("%s -> %s" % (d["ad"], mesaj))

    if hatalar:
        pytest.fail("[%s]\n  " % etiket + "\n  ".join(hatalar), pytrace=False)


def _karsilastirmalar(sonuclar, tanimlar, etiket):
    """A7: iki profilin sonuclarini karsilastirir."""
    hatalar = []
    for t in tanimlar:
        if t.get("yon") == "en_az_biri_kesin_buyuk":
            continue        # digerlerinden turetiliyor
        hatalar.append("karsilastirma '%s' henuz sinanmiyor: motor yok"
                       % t.get("ad"))
    if hatalar:
        pytest.fail("[%s]\n  " % etiket + "\n  ".join(hatalar), pytrace=False)


# ----------------------------------------------------------------------
# evaluate -- elle verilen plan denetlenir
# ----------------------------------------------------------------------

@pytest.mark.evaluate
@pytest.mark.parametrize("yol", fiksturler("evaluate"), ids=fikstur_kimlik)
def test_evaluate_senaryosu(yol, motor):
    fik, girdi = fy.fikstur_oku(yol)

    kumeler = []
    if "atamalar" in fik:
        kumeler.append(("-", girdi, fik["atamalar"],
                        fy.temiz(fik.get("beklenen", {}))))
    for ad in fik.get("alt_durumlar", []):
        if "atamalar" not in ad:
            continue
        kumeler.append((ad.get("ad", "?"),
                        fy.sahne_uygula(girdi, ad.get("fark")),
                        ad["atamalar"], fy.temiz(ad.get("beklenen", {}))))

    for etiket, alt_girdi, atamalar, bek in kumeler:
        cikti = motor.evaluate(alt_girdi, atamalar)
        _evaluate_dogrula(cikti, bek, "%s/%s" % (fik["senaryo"], etiket))


def _evaluate_dogrula(cikti, bek, etiket):
    hatalar = []
    ihlaller = cikti.get("ihlaller", []) or []
    sert = [i for i in ihlaller if i.get("agirlik", "SERT") == "SERT"]
    yumusak = [i for i in ihlaller if i.get("agirlik") == "YUMUSAK"]

    if "sert_ihlal_sayisi" in bek and len(sert) != bek["sert_ihlal_sayisi"]:
        hatalar.append("sert ihlal sayisi: %d olmaliydi, %d geldi"
                       % (bek["sert_ihlal_sayisi"], len(sert)))

    for beklenen_ihlal in bek.get("ihlaller", []):
        if not any(i.get("kural") == beklenen_ihlal["kural"]
                   and i.get("calisan") == beklenen_ihlal.get("calisan")
                   for i in sert):
            hatalar.append("beklenen sert ihlal yok: %s / %s"
                           % (beklenen_ihlal["kural"],
                              beklenen_ihlal.get("calisan")))

    for beklenen_ihlal in bek.get("yumusak_ihlaller", []):
        if not any(i.get("kural") == beklenen_ihlal["kural"] for i in yumusak):
            hatalar.append("beklenen yumusak ihlal yok: %s"
                           % beklenen_ihlal["kural"])

    for ad, deger in (bek.get("olmamasi_gerekenler") or {}).items():
        if ad.startswith("_"):
            continue
        hatalar.append("olmamasi gereken kontrolu henuz sinanmiyor: %s" % ad)

    if hatalar:
        pytest.fail("[%s]\n  " % etiket + "\n  ".join(hatalar), pytrace=False)


# ----------------------------------------------------------------------
# backend -- burada kosmaz
# ----------------------------------------------------------------------

@pytest.mark.backend
@pytest.mark.parametrize("yol", fiksturler("backend"), ids=fikstur_kimlik)
def test_backend_senaryosu_burada_kosmaz(yol):
    fik = fy.oku(yol)
    pytest.skip(
        "%s bir BACKEND senaryosu; xUnit tarafinda kosacak. "
        "Taslak: ../testler/backend-taslak/" % fik["senaryo"])


# ----------------------------------------------------------------------
# Paketin kendi saglik kontrolu -- motor olmadan da YESIL olmali
# ----------------------------------------------------------------------

def test_butun_fiksturler_yukleniyor(fikstur_klasoru):
    """Motor olmasa bile fiksturler acilip sahneye baglanabilmeli."""
    yollar = fy.fikstur_listesi(fikstur_klasoru)
    assert yollar, "Hic fikstur bulunamadi"
    for yol in yollar:
        fik, girdi = fy.fikstur_oku(yol)
        assert fik["tip"] in ("solve", "evaluate", "backend")
        assert girdi["calisanlar"], "%s: sahne cozulmedi" % fik["senaryo"]


def test_her_kontrol_adinin_govdesi_var(fikstur_klasoru):
    """Fiksturde gecen her `kontrol` adi kontroller.py'de tanimli olmali."""
    eksik = set()
    for yol in fy.fikstur_listesi(fikstur_klasoru):
        fik = fy.oku(yol)
        yerler = [fik.get("beklenen", {})]
        yerler += [a.get("beklenen", {}) for a in fik.get("alt_durumlar", [])]
        yerler.append(fik.get("beklenen", {}).get("her_iki_cagri", {}))
        for y in yerler:
            for d in (y or {}).get("degismezler", []):
                if d.get("kontrol") not in kontroller.KAYIT:
                    eksik.add(d.get("kontrol"))
    assert not eksik, ("kontroller.py'de govdesi olmayan kontrol adlari: %s"
                       % ", ".join(sorted(eksik)))


def test_motor_yoksa_acikca_soylenir():
    """Motor adresi yokken istemci sessizce degil, ACIKCA hata vermeli.

    Mesaj yalniz 'olmadi' demez, NE YAPILACAGINI da yazar. Bu testin asil
    korudugu sey o: belirsiz bir hata mesaji, insani yanlis yere bakmaya
    gonderir.
    """
    istemci = mi.MotorIstemci(adres="")
    with pytest.raises(mi.MotorYok) as e:
        istemci.solve({})
    metin = str(e.value)
    assert "TSHIFT_MOTOR_URL" in metin, "hangi ortam degiskeni gerektigi yazmali"
    assert "servis.py" in metin, "servisin nasil baslatilacagi yazmali"


def test_cozucu_yokken_sebep_acikca_ayirt_edilir():
    """501 (cozucu yok) ile baglanti hatasi KARISTIRILMAMALI.

    Ikisi de testi kirmizi yakar ama sebepleri bambaska: biri 'daha
    yazilmadi', digeri 'servis cokmus'. Ayni mesaji verirlerse saatler
    yanlis yerde aranir.
    """
    import urllib.error
    istemci = mi.MotorIstemci(adres="http://ornek.gecersiz")

    def sahte_501(*a, **k):
        raise urllib.error.HTTPError(
            "http://ornek.gecersiz/solve", 501, "Not Implemented", {},
            io.BytesIO(b'{"hata":"cozucu yazilmadi"}'))

    import io as _io, urllib.request
    eski = urllib.request.urlopen
    urllib.request.urlopen = sahte_501
    try:
        with pytest.raises(mi.MotorYok) as e:
            istemci.solve({})
        assert "COZUCU YAZILMADI" in str(e.value)
    finally:
        urllib.request.urlopen = eski


def test_dogrulayici_ucu_gercekten_cagriliyor(motor):
    """Motor adresliyken /health gercekten cevap vermeli.

    Motor adresi tanimli DEGILSE bu test atlanir -- yoklugu kirmizi
    yakmaz, cunku motorsuz kosu da gecerli bir kosudur.
    """
    if not mi.motor_var_mi():
        pytest.skip("TSHIFT_MOTOR_URL tanimli degil")
    saglik = motor.health()
    assert saglik.get("durum") == "ayakta"
    assert "evaluate" in saglik.get("ucler", {}), "saglik cevabi hangi uclerin var oldugunu soylemeli"
