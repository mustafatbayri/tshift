# -*- coding: utf-8 -*-
"""
MOTOR ISTEMCISI

NE YAPAR
  Altin senaryo testleri ile planlama motoru arasindaki tek temas noktasi.
  /solve ve /evaluate uclarini cagirir (Master Spec #11.1).

SU AN NE YAPIYOR
  HICBIR SEY -- cunku MOTOR YAZILMADI. Her cagri MotorYok firlatir ve
  testler KIRMIZI yanar.

  Bu bir eksiklik degil, ISTENEN DURUM: spec #16.4 "kirmizi kanit" kurali,
  kodun once testi kirmizi yakmasini sart kosar. Testler once yazilir,
  kirmizi yanar, sonra motor onlari yesile cevirir.

MOTOR YAZILDIGINDA NE DEGISECEK
  Yalniz bu dosya. `_cagir` gercekten HTTP istegi atacak; testlerin ve
  fiksturlerin tek satiri degismeyecek. Temas noktasinin tek olmasinin
  sebebi bu.

  Adres ortam degiskeninden okunur:
      set TSHIFT_MOTOR_URL=http://localhost:8000

BU NE DEGILDIR
  * Urunun dogrulayicisi degildir.
  * Motor degildir. Plan uretmez, yalniz cagirir.
"""

import os
import json

ORTAM_DEGISKENI = "TSHIFT_MOTOR_URL"


class MotorYok(Exception):
    """Motor henuz yazilmadi ya da adresi tanimli degil."""


def motor_adresi():
    return os.environ.get(ORTAM_DEGISKENI, "").strip()


def motor_var_mi():
    return bool(motor_adresi())


class MotorIstemci(object):
    """Master Spec #11.1'deki uclarin istemcisi."""

    def __init__(self, adres=None):
        self.adres = (adres or motor_adresi()).rstrip("/")

    # ---- kamuya acik ucler -------------------------------------------

    def solve(self, girdi, istek_anahtari=None):
        """POST /solve -- plan uret. Master Spec #11.2 / #11.3."""
        govde = dict(girdi)
        if istek_anahtari:
            govde["istek_anahtari"] = istek_anahtari
        return self._cagir("/solve", govde)

    def evaluate(self, girdi, atamalar):
        """POST /evaluate -- var olan plani denetle. Master Spec #11.4."""
        govde = dict(girdi)
        govde["atamalar"] = atamalar
        return self._cagir("/evaluate", govde)

    def health(self):
        """GET /health -- saglik + surum."""
        return self._cagir("/health", None, metot="GET")

    # ---- ic ----------------------------------------------------------

    def _cagir(self, yol, govde, metot="POST"):
        if not self.adres:
            raise MotorYok(
                "MOTOR YAZILMADI.\n"
                "  Bu test, motor var oldugunda yesile donecek sekilde yazildi.\n"
                "  Kirmizi olmasi BEKLENEN durumdur (spec #16.4 kirmizi kanit).\n"
                "  Motor hazir oldugunda: set %s=http://localhost:8000"
                % ORTAM_DEGISKENI)

        # Motor yazildiginda burasi gercek HTTP istegine donusecek.
        # Simdilik adres tanimli olsa bile cagri yapilmiyor -- yanlislikla
        # var olmayan bir servise istek atip belirsiz hata almayalim.
        raise MotorYok(
            "Motor adresi tanimli (%s) ama istemci govdesi henuz yazilmadi.\n"
            "  Yapilacak: bu metodu requests/httpx ile %s %s cagrisina cevir."
            % (self.adres, metot, yol))
