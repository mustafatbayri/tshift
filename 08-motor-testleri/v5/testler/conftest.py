# -*- coding: utf-8 -*-
"""
pytest ortak ayarlari.

Fikstur klasorunu bulur, fiksturleri yukler ve motor istemcisini saglar.
"""

import os
import sys
import pytest

V5 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIKSTUR = os.path.join(V5, "fikstur")
sys.path.insert(0, V5)          # fikstur_yukleyici.py oradan gelir

import fikstur_yukleyici as fy  # noqa: E402
import motor_istemci as mi      # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "solve: motorun plan uretmesini sinar")
    config.addinivalue_line("markers", "evaluate: elle verilen plani sinar")
    config.addinivalue_line("markers", "backend: backend davranis senaryosu "
                                       "(xUnit tarafinda kosar, burada atlanir)")


@pytest.fixture(scope="session")
def fikstur_klasoru():
    return FIKSTUR


@pytest.fixture(scope="session")
def motor():
    return mi.MotorIstemci()


def fikstur_kimlik(yol):
    return os.path.basename(yol).replace(".json", "")


def fiksturler(tip=None):
    """Fikstur yollarini dondurur; istege bagli tipe gore suzer."""
    cikan = []
    for yol in fy.fikstur_listesi(FIKSTUR):
        fik = fy.oku(yol)
        if tip is None or fik.get("tip") == tip:
            cikan.append(yol)
    return cikan


def karsilastir(deger, beklenen, ad):
    """{'esit': 0} / {'en_az': 95} / {'en_fazla': 10} sozdizimini uygular.

    Doner: (tamam_mi, mesaj)
    """
    if not isinstance(beklenen, dict):
        return deger == beklenen, "%s: %r bekleniyordu, %r geldi" % (
            ad, beklenen, deger)
    for anahtar, esik in beklenen.items():
        if anahtar.startswith("_"):
            continue
        if deger is None:
            return False, "%s ciktida yok (beklenen %s %r)" % (ad, anahtar, esik)
        if anahtar == "esit" and deger != esik:
            return False, "%s: %r olmaliydi, %r geldi" % (ad, esik, deger)
        if anahtar == "en_az" and deger < esik:
            return False, "%s: en az %r olmaliydi, %r geldi" % (ad, esik, deger)
        if anahtar == "en_fazla" and deger > esik:
            return False, "%s: en fazla %r olmaliydi, %r geldi" % (ad, esik, deger)
    return True, "%s tamam (%r)" % (ad, deger)
