# -*- coding: utf-8 -*-
"""Veri seti merdiveni ON DENEMESI -- ortak parcalar (6 Ekim 2026).

KESIF ARSIVIDIR, olcum araci degildir: testi yok, tek oturumda yazildi.
Ne oldugu ve sonuclari: ayni klasordeki OKU-BENI.md.

Ciktilar depoya YAZILMAZ; isletim sisteminin gecici klasorune gider
(`CIKTI`). Motorun ve dogrulayicinin KENDI kodu kullanilir, kopyasi degil.
"""
import copy
import json
import os
import sys
import tempfile
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
for _y in (os.path.join(KOK, "09-motor"),
           os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti")):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import uret_veri_seti as U                      # noqa: E402
from cozucu.model import Model                  # noqa: E402
from cozucu.coz import coz                      # noqa: E402
from dogrulayici import degerlendir             # noqa: E402

CIKTI = os.path.join(tempfile.gettempdir(), "tshift-merdiven")
if not os.path.isdir(CIKTI):
    os.makedirs(CIKTI)

YAPILAR = {"varsayilan": {}, "fm0": {"fazla_mesai_once_sifir": True}}


def yol(ad):
    return os.path.join(CIKTI, ad)


def coz_olc(g, ayar):
    """Modeli kurar, cozer; (cikti, kurma sn, cozum sn)."""
    t0 = time.time()
    k = Model(copy.deepcopy(g)).kur()
    kur = time.time() - t0
    t1 = time.time()
    c = coz(g, ayar, kuruldu=k)
    return c, round(kur, 1), round(time.time() - t1, 1)


def ozet(g, c):
    """Motorun istatistikleri + BAGIMSIZ dogrulayicinin sayimi."""
    ist = c.get("cozum_istatistikleri") or {}
    s = {"durum": c.get("durum")}
    for a in ("durma_sebebi", "amac_degeri", "alt_sinir", "mola_adimi_alt_sinir",
              "fazla_mesaisiz_alt_sinir", "iki_asama", "atamalar_sabit",
              "cozum_sayisi", "fazla_mesai_once_sifir"):
        s[a] = ist.get(a)
    s["dagilim"] = {k: (v.get("ceza"), v.get("deger"))
                    for k, v in (ist.get("amac_dagilimi") or {}).items()}
    if c.get("durum") == "cozuldu":
        r = degerlendir(g, c["atamalar"])
        say = {}
        for i in r.get("ihlaller", []):
            say[i["kural"]] = say.get(i["kural"], 0) + 1
        s["ihlal"] = say
        s["sert"] = sum(1 for i in r.get("ihlaller", [])
                        if i.get("agirlik") == "SERT" and not i.get("gecmis"))
        m = r.get("metrikler") or {}
        s["fm_saat"] = m.get("fazla_mesai_saat")
        s["toplam_saat"] = m.get("toplam_saat")
    return s


def varlik(g, atamalar):
    """Hucre basina ATANMIS kisi sayisi -- bagimsiz dogrulayicinin sayimi.

    Dogrulayici hedeften SAPAN hucreyi `olculen` (atanan kisi) ile yazar;
    sapmayan hucrede atanan kisi hedefin kendisidir."""
    r = degerlendir(g, atamalar)
    sapan = {}
    for i in r.get("ihlaller", []):
        if i.get("kural") in ("HEDEF_KAPSAMA", "HEDEF_ASIMI"):
            sapan[(i.get("ekip"), i.get("gun"), i.get("saat"))] = i.get("olculen")
    v = {}
    for t in g["talep"]:
        a = (t["ekip"], t["gun"], t["saat"])
        v[a] = sapan.get(a, t.get("hedef"))
    return v


def asgariyi_carp(g, f, ekipler=None):
    """Asgari talebi f ile carpar; hedef asgarinin altinda kalmaz."""
    g2 = copy.deepcopy(g)
    for t in g2["talep"]:
        if ekipler and t["ekip"] not in ekipler:
            continue
        t["asgari"] = int(round(t["asgari"] * f))
        t["hedef"] = max(t["hedef"], t["asgari"])
    return g2
