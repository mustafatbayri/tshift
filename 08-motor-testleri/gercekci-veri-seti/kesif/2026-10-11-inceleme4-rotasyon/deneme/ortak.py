# -*- coding: utf-8 -*-
"""Inceleme 4 (VARDIYA_ROTASYON_YONU, K-65) -- ortak yardimcilar.

Depo kokune gore calisir: kesif/<klasor>/deneme -> kok (bes ust).
Urun koduna dokunmaz; yalniz okur ve cagirir.
"""
import copy
import importlib
import os
import sys
import time

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "..", ".."))
MOTOR = os.path.join(KOK, "09-motor")
VERI = os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti")
for yol in (MOTOR, VERI):
    if yol not in sys.path:
        sys.path.insert(0, yol)

from ortools.sat.python import cp_model                      # noqa: E402
from cozucu.model import Model, AGIRLIK_TABLOSU, rotasyon_geri_saat   # noqa: E402
from cozucu.coz import coz, _CEZA_ONEKI, _rotasyon_metrigi   # noqa: E402
from dogrulayici import degerlendir                          # noqa: E402
from dogrulayici.kurallar import _rotasyon_geri_saat         # noqa: E402

AYAR = {"azami_saniye": 20, "durgunluk_saniye": 5, "iki_asama_esigi": 10 ** 9, "isci_sayisi": 2}
KURAL = "VARDIYA_ROTASYON_YONU"


def kural(kod, tur="SERT", yasal=False, **par):
    k = {"kod": kod, "tur": tur, "aktif": True, "yasal": yasal, "kabul_edilebilir": not yasal}
    if par:
        k["parametreler"] = par
    return k


def atama(gun, sablon, kisi="P1", ekip="E"):
    return {"calisan": kisi, "ekip": ekip, "sablon": sablon["id"], "gun": gun,
            "bas": sablon["bas"], "bit": sablon["bit"], "molalar": []}


def rot_satirlari(rapor):
    return [i for i in rapor["ihlaller"] if i["kural"] == KURAL]


def rot_kirilim(cikti):
    return ((cikti.get("cozum_istatistikleri") or {}).get("amac_dagilimi") or {}).get(KURAL)


def yuvarla(h):
    """Sartname #6.3 madde 3: en yakin tam saate, 0,5 yukari."""
    return int(h + 0.5)


def dairesel_geri(b0, b1, yon="ileri"):
    """Tanimin UCUNCU, bagimsiz yazimi (inceleme): fark 24'e indirgenmis,
    (-12, 12]; eksi = geri; yon=geri isareti cevirir."""
    f = (float(b1) % 24.0) - (float(b0) % 24.0)
    if f > 12.0:
        f -= 24.0
    elif f <= -12.0:
        f += 24.0
    if yon == "geri":
        f = -f
    return -f if f < 0 else 0.0


def benim_say(girdi, atamalar, donmus=None):
    """Tanimi plandan BAGIMSIZ sayar: kisi -> gun -> ilk baslangic (ayni gunde
    birden cok atama: en kucuk bas); gecmis gun -1 (en kucuk bas) dahil;
    art arda gun ciftleri; dairesel; yon. Donen: satir listesi
    [(kisi, ikinci_gun, kesin_saat, iki_gun_de_donmus)]."""
    k = next((k for k in girdi.get("kurallar") or [] if k.get("kod") == KURAL and k.get("aktif", True)), None)
    if k is None:
        return None
    yon = (k.get("parametreler") or {}).get("yon", "ileri")
    if yon not in ("ileri", "geri"):
        yon = "ileri"
    donmus = set(donmus if donmus is not None else (girdi.get("donmus_gunler") or []))
    bas = {}
    for a in atamalar:
        g = bas.setdefault(a["calisan"], {})
        d = int(a["gun"])
        b = float(a["bas"])
        g[d] = min(g.get(d, b), b)
    for c in girdi.get("calisanlar") or []:
        onceki = [float(x["bas"]) for x in (c.get("gecmis_vardiyalar") or [])
                  if x.get("gun") is not None and int(x["gun"]) == -1 and x.get("bas") is not None]
        if onceki and c["id"] in bas:
            bas[c["id"]][-1] = min(onceki)
    satirlar = []
    for kisi in sorted(bas):
        g = bas[kisi]
        for d in sorted(g):
            if d + 1 not in g:
                continue
            h = dairesel_geri(g[d], g[d + 1], yon)
            if h > 0:
                iki_donmus = ((d in donmus or d == -1) and (d + 1) in donmus)
                satirlar.append((kisi, d + 1, round(h, 2), iki_donmus))
    return satirlar


def model_kur(girdi):
    t0 = time.time()
    k = Model(copy.deepcopy(girdi)).kur()
    return k, time.time() - t0


def proto_ozeti(k):
    p = k.m.Proto()
    ro = [v for _, v in k.cezalar if v.Name().startswith("ro_")]
    ro_kisit = 0
    ro_idx = {v.Index() for v in ro}
    for c in p.constraints:
        if c.has_linear() and any((i if i >= 0 else -i - 1) in ro_idx for i in c.linear.vars):
            ro_kisit += 1
    return {"degisken": len(p.variables), "kisit": len(p.constraints), "x": len(k.x),
            "mola": len(k.mola), "dinlenme": len(k.dinlenme), "ceza": len(k.cezalar),
            "ro_degisken": len(ro), "ro_kisit": ro_kisit}
