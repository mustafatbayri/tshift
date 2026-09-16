# -*- coding: utf-8 -*-
"""
FIKSTUR YUKLEYICI -- ortak modul

NE YAPAR
  Bir fikstur dosyasini acar, ortak sahneyi (_sahne-S10.json) okur ve
  fiksturun "fark" blogunu sahneye uygulayarak BIRLESMIS girdiyi dondurur.

NEDEN AYRI DOSYA
  Ayni birlestirme mantigini hem fikstur-denetleyici.py hem testler
  kullaniyor. Iki yerde ayri ayri yazilsaydi zamanla ayrisir ve denetleyici
  ile testler FARKLI girdiler uzerinde calisirdi -- yani denetleyici yesil
  yanarken testler baska bir seyi sinardi.

BU NE DEGILDIR
  * Beklenen sonuc uretmez. Yalniz GIRDI hazirlar.
  * Urunun dogrulayicisi degildir.
"""

import os
import json
import copy

SAHNE_ADI = "_sahne-S10.json"

# fark blogunda taninan alanlar
TAMAMEN_DEGISTIR = ("talep", "sabit_atamalar", "kilitler", "profil",
                    "donmus_gunler", "kiraci_saat_dilimi", "hafta_baslangic")


def oku(yol):
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def temiz(d):
    """_ ile baslayan anahtarlari (yorumlari) atar."""
    if isinstance(d, dict):
        return {k: temiz(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, list):
        return [temiz(x) for x in d]
    return d


def sahne_uygula(sahne, fark):
    """Sahneye farki uygular, birlesmis girdiyi dondurur."""
    g = copy.deepcopy(sahne)
    fark = fark or {}

    if "calisanlar" in fark:
        indeks = {c["id"]: c for c in g["calisanlar"]}
        for cid, degisiklik in fark["calisanlar"].items():
            if cid not in indeks:
                raise KeyError("fark bilinmeyen calisani degistiriyor: %s" % cid)
            indeks[cid].update(copy.deepcopy(degisiklik))

    for alan in TAMAMEN_DEGISTIR:
        if alan in fark:
            g[alan] = copy.deepcopy(fark[alan])

    if "vardiya_sablonlari_ekle" in fark:
        g["vardiya_sablonlari"] += copy.deepcopy(fark["vardiya_sablonlari_ekle"])
    if "kurallar_ekle" in fark:
        g["kurallar"] += copy.deepcopy(fark["kurallar_ekle"])

    if "kurallar_cikar" in fark:
        cikar = set(fark["kurallar_cikar"])
        g["kurallar"] = [k for k in g["kurallar"] if k["kod"] not in cikar]

    return g


def sahne_oku(fikstur_klasoru):
    return oku(os.path.join(fikstur_klasoru, SAHNE_ADI))


def fikstur_oku(yol):
    """Fiksturu acar ve (fikstur, birlesmis_girdi) dondurur."""
    fik = oku(yol)
    sahne = sahne_oku(os.path.dirname(os.path.abspath(yol)))
    return fik, sahne_uygula(sahne, fik.get("fark"))


def fikstur_listesi(fikstur_klasoru):
    """_ ile baslamayan butun .json dosyalari, adina gore sirali."""
    import glob
    return sorted(y for y in glob.glob(os.path.join(fikstur_klasoru, "*.json"))
                  if not os.path.basename(y).startswith("_"))
