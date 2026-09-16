# -*- coding: utf-8 -*-
"""
MOTOR ISTEMCISI

NE YAPAR
  Altin senaryo testleri ile planlama motoru arasindaki tek temas noktasi.
  /solve ve /evaluate uclarini cagirir (Master Spec #11.1).

SU AN NE YAPIYOR
  Adres tanimliysa GERCEK HTTP istegi atar. 16 Eylul'de yazildi -- ve
  soz verildigi gibi YALNIZ BU DOSYA degisti: testlerin, fiksturlerin
  ve kontrollerin tek satiri degismedi.

  Adres tanimli degilse MotorYok firlatir ve testler kirmizi yanar.
  Bu hala ISTENEN DURUM: spec #16.4 "kirmizi kanit" kurali.

HANGI UCLER GERCEK
  /health, /evaluate   -> 09-motor/servis.py bunlari cevapliyor
  /solve, /suggest     -> cozucu YAZILMADI; servis 501 doner ve istemci
                          bunu MotorYok'a cevirir. A1/A3/A6/A7/A9 bu
                          yuzden hala kirmizi -- dogru sebeple.

KOSTURMA
      cd 09-motor  ve  py servis.py          (ayri bir pencerede)
      set TSHIFT_MOTOR_URL=http://localhost:8000

BU NE DEGILDIR
  * Urunun dogrulayicisi degildir.
  * Motor degildir. Plan uretmez, yalniz cagirir.
"""

import os
import json
import urllib.error
import urllib.request

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
        """adres=None  -> ortam degiskenine bak
        adres=""       -> ACIKCA adressiz (testler bunu kullanir)

        Ikisi ayri anlam tasir. 16 Eylul'de bir test bu ayrimin olmadigini
        yakaladi: adres="" verildiginde istemci yine de ortam degiskenine
        dusuyor, yani 'adressiz davranisi' sinanamiyordu.
        """
        if adres is None:
            adres = motor_adresi()
        self.adres = (adres or "").rstrip("/")

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

    ZAMAN_ASIMI = 120          # #13.4: /evaluate hedefi < 1 sn; bu tavan

    def _cagir(self, yol, govde, metot="POST"):
        if not self.adres:
            raise MotorYok(
                "MOTOR ADRESI TANIMLI DEGIL.\n"
                "  Bu test, motor ayaktayken yesile doner.\n"
                "  Kirmizi olmasi BEKLENEN durumdur (spec #16.4 kirmizi kanit).\n"
                "  Baslatmak icin:\n"
                "    1) ayri pencerede:  cd 09-motor  &&  py servis.py\n"
                "    2) bu pencerede:    set %s=http://localhost:8000"
                % ORTAM_DEGISKENI)

        veri = None if govde is None else json.dumps(govde).encode("utf-8")
        istek = urllib.request.Request(
            self.adres + yol, data=veri, method=metot,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(istek, timeout=self.ZAMAN_ASIMI) as cevap:
                return json.loads(cevap.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            govde_metni = e.read().decode("utf-8", "replace")
            if e.code == 501:
                # Servis ayakta ama bu uc YAZILMADI. Testin kirmizi yanmasi
                # dogru; ama sebebi "motor cokmus" degil "cozucu yok".
                raise MotorYok(
                    "COZUCU YAZILMADI -- servis ayakta ama %s ucu yok.\n"
                    "  Bu BEKLENEN durumdur: su an yalniz bagimsiz dogrulayici\n"
                    "  (/evaluate) yazildi. A1/A3/A6/A7/A9 cozucu gelince yesile doner.\n"
                    "  Servis cevabi: %s" % (yol, govde_metni))
            raise MotorYok("Motor %s icin HTTP %d dondu: %s" % (yol, e.code, govde_metni))
        except urllib.error.URLError as e:
            raise MotorYok(
                "Motora ULASILAMADI: %s%s\n"
                "  Sebep: %s\n"
                "  Servis ayakta mi?  cd 09-motor  &&  py servis.py"
                % (self.adres, yol, e.reason))
