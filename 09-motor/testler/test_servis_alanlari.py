# -*- coding: utf-8 -*-
"""
SERVIS -- sartname #11.2'nin iki alani: istek_id ve sure_butcesi_sn (T-38, 1 Ekim)

  istek_id        -> /solve cevabina aynen geri yazilir (#11.3)
  sure_butcesi_sn -> arama butcesi (K-35 sure secimi; K-48: model kurma
                     disinda). `_cozucu_ayari.azami_saniye` verilmisse o
                     kazanir -- olcum araclari icin.

Servis gercekten ayaga kaldirilir (rastgele portta) ve HTTP ile cagrilir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_servis_alanlari.py -v
"""

import json
import os
import socket
import sys
import threading
import urllib.request
from http.server import HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import servis                                                  # noqa: E402

SAHNE = {
    "profil": "DENGELI",
    "calisanlar": [{"id": "C1", "ekipler": ["E"], "sozlesme": {"tip": "tam_zamanli"},
                    "izinler": [], "uygunluk": []}],
    "vardiya_sablonlari": [{"id": "V", "ekip": "E", "bas": 8, "bit": 16, "mola_dk": 60}],
    "talep": [{"ekip": "E", "gun": 0, "saat": 9, "asgari": 1, "hedef": 1}],
    "kurallar": [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False}],
    "kilitler": [], "donmus_gunler": [],
}


def _sunucu():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    httpd = HTTPServer(("127.0.0.1", port), servis.Ucler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


def _post(port, yol, govde):
    veri = json.dumps(govde).encode("utf-8")
    istek = urllib.request.Request("http://127.0.0.1:%d%s" % (port, yol), data=veri,
                                   headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(istek, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def test_istek_id_cevaba_GERI_yazilir_ve_okunmayan_alan_DEGIL():
    httpd, port = _sunucu()
    try:
        g = dict(SAHNE, istek_id="abc-123", sure_butcesi_sn=5)
        c = _post(port, "/solve", g)
        assert c.get("istek_id") == "abc-123", list(c)
        assert c["durum"] == "cozuldu", c["durum"]
        okunmayan = {(x.get("yer"), x.get("alan")) for x in
                     (c.get("bagimsiz_denetim") or {}).get("okunmayan_alanlar", [])}
        assert not any(a in ("istek_id", "sure_butcesi_sn") for _, a in okunmayan), okunmayan
    finally:
        httpd.shutdown()


def test_sure_butcesi_sn_arama_butcesi_olur():
    httpd, port = _sunucu()
    try:
        c = _post(port, "/solve", dict(SAHNE, sure_butcesi_sn=4))
        ist = c["cozum_istatistikleri"]
        assert ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"] <= 4 + 0.01, ist
    finally:
        httpd.shutdown()


def test_cozucu_ayari_verilmisse_O_kazanir():
    httpd, port = _sunucu()
    try:
        c = _post(port, "/solve", dict(SAHNE, sure_butcesi_sn=4,
                                       _cozucu_ayari={"azami_saniye": 2}))
        ist = c["cozum_istatistikleri"]
        assert ist["ilk_asama_sn"] + ist["ana_asama_butce_sn"] <= 2 + 0.01, ist
    finally:
        httpd.shutdown()
