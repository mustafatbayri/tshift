# -*- coding: utf-8 -*-
"""Karsi ornekler: TAM (kanitli optimum) / URUN (asamali, varsayilan) / SERT (olcum: sifirda tut)."""
import copy, importlib, os, sys
sys.dont_write_bytecode = True
MOTOR = os.environ["MOTOR"]
sys.path.insert(0, MOTOR)
from cozucu.model import Model
import dogrulayici
C = importlib.import_module("cozucu.coz")

TAM = {"azami_saniye": 40, "isci_sayisi": 2, "hedef_bosluk": 0.0, "fazla_mesai_once_sifir": False}
URUN = {"azami_saniye": 40, "iki_asama_esigi": 0, "durgunluk_saniye": 5, "isci_sayisi": 2}
SERT = dict(URUN, fazla_mesai_sifirda_tut=True)
YEMEK = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False}]

def sablon(kimlik, bas, bit, gunler=None, ekip="E"):
    s = {"id": kimlik, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": 60, "mola_politikasi": copy.deepcopy(YEMEK)}
    if gunler is not None:
        s["gunler"] = list(gunler)
    return s

def kisi(kimlik, ekipler=("E",), saat=45):
    return {"id": kimlik, "ekipler": list(ekipler), "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": saat},
            "izinler": [], "uygunluk": []}

def kurallar(saat_dengesi=None):
    k = [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False, "kabul_edilebilir": False},
         {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
         {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
         {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True, "parametreler": {"azami_saat": 11}},
         {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True, "parametreler": {"azami_saat": 45}},
         {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True, "parametreler": {"azami_saat_hafta": 10}},
         {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True}]
    if saat_dengesi:
        k.append({"kod": "SAAT_DENGESI", "tur": saat_dengesi, "aktif": True, "yasal": False,
                  "kabul_edilebilir": True, "parametreler": {"tolerans_saat": 0}})
    return k

def aksam(profil, kisi_sayisi=1, ekipler=("E",), sd="SERT"):
    return {"profil": profil,
            "calisanlar": [kisi("P%d" % i, ekipler=ekipler) for i in range(1, kisi_sayisi + 1)],
            "vardiya_sablonlari": [sablon("ERKEN", 4, 12.5, gunler=range(6)),
                                   sablon("P9", 13, 23, gunler=[0, 1, 2, 3]),
                                   sablon("PL", 13, 23.25, gunler=[4])],
            "talep": [{"ekip": e, "gun": d, "saat": s, "asgari": 0, "hedef": kisi_sayisi}
                      for e in ekipler for d in range(5) for s in range(13, 23)],
            "kurallar": kurallar(sd), "kilitler": [], "donmus_gunler": []}

def tek(profil, sd):
    return {"profil": profil, "calisanlar": [kisi("P")],
            "vardiya_sablonlari": [sablon("A", 8, 16.5, range(5)), sablon("B", 8, 16.75, [5])] +
                                  ([sablon("E", 15, 25)] if sd == "SERT" else []),
            "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 0, "hedef": 1} for d in range(6) for s in range(8, 17)],
            "kurallar": kurallar(sd), "kilitler": [], "donmus_gunler": []}

SAHNELER = [
    ("S1  tek kisi, DENGELI, saat dengesi YUMUSAK", tek("DENGELI", "YUMUSAK")),
    ("F2  tek kisi, KAPSAMA, saat dengesi SERT", tek("KAPSAMA", "SERT")),
    ("S3b 12 kisi, KAPSAMA, saat dengesi SERT (3 saat)", aksam("KAPSAMA", 12)),
    ("S3c iki ekibe uye tek kisi, DENGELI", aksam("DENGELI", ekipler=("E", "F"))),
    ("S3d iki ekibe uye tek kisi, KAPSAMA", aksam("KAPSAMA", ekipler=("E", "F"))),
]
for ad, g in SAHNELER:
    print("== " + ad)
    for etiket, ayar in (("TAM ", TAM), ("URUN", URUN), ("SERT", SERT)):
        c = C.coz(copy.deepcopy(g), dict(ayar))
        ist = c["cozum_istatistikleri"]; m = c.get("metrikler") or {}
        r = dogrulayici.degerlendir(copy.deepcopy(g), c["atamalar"]) if c["durum"] == "cozuldu" else None
        print("   %s durum=%s amac=%s alt_sinir=%s sebep=%s iki_asama=%s fm=%s yayin=%s once=%s"
              % (etiket, c["durum"], ist.get("amac_degeri"), ist.get("alt_sinir"), ist.get("durma_sebebi"),
                 ist.get("iki_asama"), m.get("fazla_mesai_saat"),
                 r and r["yayin_kapisi"]["yayinlanabilir"], ist.get("fazla_mesai_once_sifir")))
    sys.stdout.flush()
