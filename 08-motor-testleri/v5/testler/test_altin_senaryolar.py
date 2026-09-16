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
        _karsilastirmalar(sonuclar, girdi, bek.get("karsilastirma", []),
                          fik["senaryo"])
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


def _karsilastirmalar(sonuclar, girdi, tanimlar, etiket):
    """A7: iki profilin sonuclarini karsilastirir.

    Fikstur `yon` alaninda "sol OP sag" yazar; sol ve sag `cagrilar`
    listesindeki cagri adlaridir:

        {"olcut": "hedef_kapsama_yuzde", "yon": "kapsama >= calisan"}

    Ozel bir yon var: `en_az_biri_kesin_buyuk`. Digerlerinden turetilir ve
    su soruyu sorar: iki profil GERCEKTEN farkli plan uretti mi? Butun
    olcutler esitse kosullar saglanir ama agirliklar hic calismiyordur --
    yesil yanan ama hicbir sey sinamayan testin tam kendisi. O yuzden
    esitlik burada BASARISIZLIKTIR.
    """
    hatalar = []
    kesin_fark = False

    for t in tanimlar:
        if t.get("yon") == "en_az_biri_kesin_buyuk":
            continue                    # dongu bitince bakilir
        olcut = t.get("olcut")
        hesap = OLCUTLER.get(olcut)
        if hesap is None:
            hatalar.append("olcut bilinmiyor: %r ('%s')" % (olcut, t.get("ad")))
            continue
        try:
            sol_ad, op, sag_ad = t["yon"].split()
        except ValueError:
            hatalar.append("yon okunamadi: %r ('%s')" % (t.get("yon"), t.get("ad")))
            continue
        if sol_ad not in sonuclar or sag_ad not in sonuclar:
            hatalar.append("yonde gecen cagri adi yok: %r" % t["yon"])
            continue

        sol = hesap(sonuclar[sol_ad], girdi)
        sag = hesap(sonuclar[sag_ad], girdi)
        if sol is None or sag is None:
            hatalar.append("%s: olcut hesaplanamadi (%s=%r, %s=%r)"
                           % (t.get("ad"), sol_ad, sol, sag_ad, sag))
            continue

        tamam = sol <= sag + TOLERANS if op == "<=" else sol >= sag - TOLERANS
        if not tamam:
            hatalar.append("%s: %s(%s)=%s %s %s(%s)=%s tutmadi"
                           % (t.get("ad"), olcut, sol_ad, sol, op,
                              olcut, sag_ad, sag))
        if abs(sol - sag) > TOLERANS:
            kesin_fark = True

    if any(t.get("yon") == "en_az_biri_kesin_buyuk" for t in tanimlar) \
            and not hatalar and not kesin_fark:
        hatalar.append(
            "iki profil de ayni sonucu verdi: hicbir olcutte kesin fark yok. "
            "Agirlik tablosu (#5.4) calismiyor demektir -- profil okunmuyor "
            "ya da agirliklar amac fonksiyonuna girmiyor.")

    if hatalar:
        pytest.fail("[%s]\n  " % etiket + "\n  ".join(hatalar), pytrace=False)


TOLERANS = 1e-9     # float karsilastirmasi icin; anlamli fark degil


def _adalet_sapmasi(cikti, girdi, boyut, gunler):
    """Devir yuku + bu haftaki atamalar -> kisi basi sayi -> STANDART SAPMA.

    Anakutle sapmasi (ddof=0) kullanilir: elimizdeki kadro ornek degil,
    kadronun kendisidir. A7 fiksturunun `turetilmis_degerler` blogundaki
    1.3 ve 0.7 sayilari da bu tanimla hesaplandi.
    """
    atamalar = cikti.get("atamalar") or []
    sayilar = []
    for c in girdi.get("calisanlar", []):
        devir = (c.get("devir_yuk") or {}).get(boyut, 0)
        bu_hafta = sum(1 for a in atamalar
                       if a.get("calisan") == c["id"] and a.get("gun") in gunler)
        sayilar.append(devir + bu_hafta)
    if not sayilar:
        return None
    ort = sum(sayilar) / float(len(sayilar))
    return (sum((s - ort) ** 2 for s in sayilar) / float(len(sayilar))) ** 0.5


OLCUTLER = {
    "adalet_sapmasi_cumartesi":
        lambda c, g: _adalet_sapmasi(c, g, "cumartesi", (5,)),
    "adalet_sapmasi_hafta_sonu":
        lambda c, g: _adalet_sapmasi(c, g, "hafta_sonu", (5, 6)),
    "hedef_kapsama_yuzde":
        lambda c, g: (c.get("metrikler") or {}).get("hedef_kapsama_yuzde"),
    "asgari_kapsama_yuzde":
        lambda c, g: (c.get("metrikler") or {}).get("asgari_kapsama_yuzde"),
    "fazla_mesai_saat":
        lambda c, g: (c.get("metrikler") or {}).get("fazla_mesai_saat"),
    "toplam_saat":
        lambda c, g: (c.get("metrikler") or {}).get("toplam_saat"),
}


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
