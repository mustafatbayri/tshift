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


def talep_hucrelere_ac(talep):
    """Fikstur kisayolunu sartname bicimine acar (#11.2).

    NE YAPAR
      {"ekip": "E1", "gunler": [0,1], "saatler": [9,10]}
        -> dort satir: {"ekip": "E1", "gun": 0, "saat": 9}, (0,10), (1,9), (1,10)
      Zaten {gun, saat} yazilmis satira dokunmaz.

    NEDEN VAR
      Sartname talebi HUCRE BASINA tanimliyor. Hafta ici bir talep boyle
      yazilinca 45 satir eder; fikstur insan gozuyle okunamaz hale gelir ve
      okunmayan fikstur gozden gecirilmez. Kisayol FIKSTUR KATMANINDA kalir.

    NEDEN MOTORDA DEGIL -- T-19'un dersi
      Kisayolu motorun de anlamasi IKI DOGRULUK yaratirdi. T-19 tam olarak
      buydu: fikstur bir bicim secti, motor fiksture bakarak yazildi, ikisi
      birbiriyle tutarli ama sartnameyle tutarsiz oldu. Motor artik yalniz
      sartname bicimini okur. Gruplu bir satir motora ULASIRSA denetleyicinin
      `okunmayan_alanlar` raporu bunu bildirir -- sessizce gecmez.

    TANIMADIGI SATIRDA DURUR
      Ne {gun, saat} ne {gunler, saatler} olan satir hata verir. Sessizce
      atlamak, acilmayan talebi "talep yok" saymak olurdu.
    """
    cikan = []
    for t in talep or []:
        if "gun" in t and "saat" in t:
            cikan.append(copy.deepcopy(t))
            continue
        if "gunler" not in t or "saatler" not in t:
            raise ValueError(
                "talep satiri ne sartname bicimi ({gun, saat}) ne fikstur "
                "kisayolu ({gunler, saatler}): %r" % (t,))
        govde = {k: v for k, v in t.items() if k not in ("gunler", "saatler")}
        for gun in t["gunler"]:
            for saat in t["saatler"]:
                h = copy.deepcopy(govde)
                h["gun"] = gun
                h["saat"] = saat
                cikan.append(h)
    return cikan


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

    # Motora giden girdide talep HER ZAMAN sartname bicimindedir (T-19).
    # Sahne de fark da kisayol yazabilir; acma tek yerde, en sonda olur.
    g["talep"] = talep_hucrelere_ac(g.get("talep"))

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
