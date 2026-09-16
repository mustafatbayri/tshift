# -*- coding: utf-8 -*-
"""
BAGIMSIZLIK TESTI -- Master Spec v1.4 #7.6, #16.1

NE KORUR
  Dogrulayici, cozucuyle HICBIR MANTIK PAYLASMAZ. Bu kural kod yorumunda
  yazili olmakla korunmaz -- bir gun biri "ayni hesabi iki kez yazmayalim"
  diyip ortak bir modul cikarir ve kimse fark etmez.

  Bu test o gunu yakalar.

NEDEN ONEMLI -- D-6 sinifi hata
  Kodu yazan testi de yazarsa, ayni yanlis varsayim iki yere birden gecer
  ve hicbir test yakalamaz. Dogrulayici ancak cozucuden BAGIMSIZSA onu
  denetleyebilir. Tekrar burada maliyet degil, guvencedir.

ORKESTRA ISTISNA DEGIL
  orkestra.py ikisini de import eder ve bu DOGRUDUR: #11.7'nin tarif ettigi
  "motor uretir, dogrulayici denetler" mimarisi tam olarak budur. Yasak
  olan, ikisinin BIRBIRINI import etmesidir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_bagimsizlik.py -v
"""

import ast
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _import_edilenler(yol):
    """Dosyadaki butun import adlarini dondurur (from X import Y dahil)."""
    with open(yol, encoding="utf-8") as f:
        agac = ast.parse(f.read(), filename=yol)
    adlar = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            for a in dugum.names:
                adlar.add(a.name)
        elif isinstance(dugum, ast.ImportFrom):
            # `from . import zaman`  -> modul None, level 1
            adlar.add(dugum.module or "")
            for a in dugum.names:
                adlar.add(((dugum.module or "") + "." + a.name).lstrip("."))
    return adlar


def _paket_dosyalari(paket):
    klasor = os.path.join(KOK, paket)
    return [os.path.join(klasor, ad) for ad in sorted(os.listdir(klasor))
            if ad.endswith(".py")]


def test_cozucu_dogrulayiciyi_import_etmez():
    """Cozucu, dogrulayicidan tek satir kod almaz."""
    suclu = []
    for yol in _paket_dosyalari("cozucu"):
        for ad in _import_edilenler(yol):
            if "dogrulayici" in ad:
                suclu.append("%s -> %s" % (os.path.basename(yol), ad))
    assert not suclu, (
        "cozucu/ dogrulayici/dan import ediyor -- #7.6 bagimsizligi kirildi:\n"
        + "\n".join(suclu))


def test_dogrulayici_cozucuyu_import_etmez():
    """Dogrulayici, cozucunun kisit kodunu cagirmaz."""
    suclu = []
    for yol in _paket_dosyalari("dogrulayici"):
        for ad in _import_edilenler(yol):
            if "cozucu" in ad:
                suclu.append("%s -> %s" % (os.path.basename(yol), ad))
    assert not suclu, (
        "dogrulayici/ cozucu/dan import ediyor -- #7.6 bagimsizligi kirildi:\n"
        + "\n".join(suclu))


def test_ortak_yardimci_modul_yok():
    """Iki paketin de import ettigi UCUNCU bir yerel modul olmamali.

    'Ortak zaman modulu cikaralim' fikrini yakalar: her iki paket de ayni
    yerel modulu import ediyorsa, mantik yeniden paylasilmaya baslamistir.
    Standart kutuphane ve ortools disaridadir -- onlar mantik degil altyapi.
    """
    DISARIDA = {"ortools", "ast", "os", "sys", "time", "json", "math",
                "collections", "itertools", "datetime", "functools"}

    def yerel(paket):
        cikan = set()
        for yol in _paket_dosyalari(paket):
            for ad in _import_edilenler(yol):
                kok = ad.split(".")[0]
                if kok and kok not in DISARIDA and kok != paket:
                    cikan.add(kok)
        return cikan

    ortak = yerel("cozucu") & yerel("dogrulayici")
    assert not ortak, (
        "iki paket de ayni yerel modulu kullaniyor: %s\n"
        "#7.6: tekrar burada maliyet degil, guvencedir." % sorted(ortak))


def test_orkestra_ikisini_de_cagirir():
    """Onarim dongusu (#11.7) gercekten iki tarafi da kullaniyor mu.

    Bu testin ters yonu onemli: orkestra dogrulayiciyi cagirmayi birakirsa
    /solve, motorun kendi 'sert_ihlal: 0' bayragina guvenmeye baslar --
    #16.1'in yasakladigi sey.
    """
    adlar = _import_edilenler(os.path.join(KOK, "orkestra.py"))
    assert any("cozucu" in a for a in adlar), "orkestra cozucuyu cagirmiyor"
    assert any("dogrulayici" in a for a in adlar), (
        "orkestra BAGIMSIZ dogrulayiciyi cagirmiyor -- /solve kendi kendini "
        "onayliyor demektir (#16.1)")
