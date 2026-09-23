# -*- coding: utf-8 -*-
"""
MOTOR SERVISI -- Master Spec v1.4 #11.1

SU AN NE VAR
  GET  /health     saglik + surum
  POST /evaluate   var olan plani denetler (#11.4)

  POST /solve      plan uretir (#11.2). 16 Eylul'de yazildi.
                   Govdesi orkestra.py: cozucu uretir, BAGIMSIZ dogrulayici
                   denetler, sert ihlal varsa en fazla 2 onarim (#11.7).

SU AN NE YOK -- ve bunu SESSIZCE gizlemez
  POST /suggest    bosluk icin aday uretir (#11.5). Yazilmadi; 501 doner.

NEDEN STDLIB
  Disaridan tek bir paket gerektirmiyor. Kurulum adimi olmayan bir servis,
  "bende calismadi" ile gecen saatleri de ortadan kaldirir. Yuk altinda
  calisacak surum icin ASGI'ye tasinabilir; sozlesme degismez.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py servis.py                       (varsayilan 8000)
  py servis.py 8080                  (baska port)

TESTLERI YESILE CEVIRMEK ICIN
  Once bu servisi ayri bir pencerede baslat, sonra:
    $env:TSHIFT_MOTOR_URL = "http://localhost:8000"    (PowerShell)
    set TSHIFT_MOTOR_URL=http://localhost:8000         (cmd)
    cd ..\\08-motor-testleri\\v5\\testler
    py -m pytest -v -k "A04 or A08"
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from dogrulayici import SURUM, degerlendir
from orkestra import coz_ve_onar

AZAMI_GOVDE = 32 * 1024 * 1024        # 32 MB -- 2.000 kisilik plan bunun altinda


class Ucler(BaseHTTPRequestHandler):

    server_version = "TShiftMotor/" + SURUM

    # ---- yardimcilar --------------------------------------------------

    def _cevap(self, kod, govde):
        veri = json.dumps(govde, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(veri)))
        self.end_headers()
        self.wfile.write(veri)

    def _istek_govdesi(self):
        uzunluk = int(self.headers.get("Content-Length") or 0)
        if uzunluk > AZAMI_GOVDE:
            raise ValueError("govde cok buyuk: %d byte" % uzunluk)
        if uzunluk == 0:
            return {}
        return json.loads(self.rfile.read(uzunluk).decode("utf-8"))

    def log_message(self, bicim, *args):
        # Istek GOVDELERI kayda yazilmaz -- icinde kisisel veri olabilir.
        sys.stderr.write("  %s %s\n" % (self.command, self.path))

    # ---- ucler --------------------------------------------------------

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", ""):
            return self._cevap(200, {
                "durum": "ayakta",
                "surum": SURUM,
                "ucler": {"health": True, "evaluate": True,
                          "solve": True, "suggest": False},
                "not": "/suggest yazilmadi, 501 doner.",
            })
        return self._cevap(404, {"hata": "bilinmeyen uc", "yol": self.path})

    def do_POST(self):
        yol = self.path.rstrip("/")
        try:
            govde = self._istek_govdesi()
        except ValueError as e:
            return self._cevap(400, {"hata": "govde okunamadi", "ayrinti": str(e)})

        if yol == "/evaluate":
            atamalar = govde.pop("atamalar", []) or []
            try:
                return self._cevap(200, degerlendir(govde, atamalar))
            except (KeyError, TypeError) as e:
                return self._cevap(400, {
                    "hata": "girdi eksik ya da bicimi yanlis",
                    "ayrinti": "%s: %s" % (type(e).__name__, e),
                })

        if yol == "/solve":
            ayar = govde.pop("_cozucu_ayari", None)
            govde.pop("atamalar", None)          # /solve atama ALMAZ, URETIR
            try:
                # Cozucu + bagimsiz dogrulayici + onarim dongusu (#11.7).
                return self._cevap(200, coz_ve_onar(govde, ayar))
            except (KeyError, TypeError, ValueError) as e:
                return self._cevap(400, {
                    "hata": "girdi eksik ya da bicimi yanlis",
                    "ayrinti": "%s: %s" % (type(e).__name__, e),
                })

        if yol in ("/suggest",):
            return self._cevap(501, {
                "hata": "cozucu yazilmadi",
                "uc": yol,
                "aciklama": ("Oneri uretimi (#11.5) henuz yazilmadi. "
                             "Bu bir hata degil, bilinen ve kayitli durum."),
            })

        return self._cevap(404, {"hata": "bilinmeyen uc", "yol": yol})


def main(argv):
    port = int(argv[1]) if len(argv) > 1 else 8000
    sunucu = HTTPServer(("127.0.0.1", port), Ucler)
    print("TShift dogrulayici %s  ->  http://127.0.0.1:%d" % (SURUM, port))
    print("  GET  /health")
    print("  POST /evaluate")
    print("  POST /solve")
    print("  POST /suggest  ->  501 (yazilmadi)")
    print("Durdurmak icin Ctrl+C")
    try:
        sunucu.serve_forever()
    except KeyboardInterrupt:
        print("\nkapatildi")
        sunucu.server_close()


if __name__ == "__main__":
    main(sys.argv)
