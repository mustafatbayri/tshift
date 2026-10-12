# -*- coding: utf-8 -*-
"""C. Dairesel tanimin sinirlari -- uctan uca (motor + dogrulayici + metrik).
Kullanim: python3 d3_sinir.py  (cikti: d3_sinir.out)"""
import json
from ortak import coz, degerlendir, AYAR, KURAL, kural, rot_satirlari, rot_kirilim, dairesel_geri


def sahne(sablonlar, sabit, dinlenme=11, yon=None):
    kurallar = [kural("ASGARI_KAPSAMA"), kural("HEDEF_KAPSAMA", tur="YUMUSAK"), kural("HEDEF_ASIMI", tur="YUMUSAK"),
                kural("VARDIYA_ARASI_DINLENME", yasal=True, asgari_saat=dinlenme), kural("CAKISMA_YOK"),
                kural(KURAL, tur="YUMUSAK", **({"yon": yon} if yon else {}))]
    return {"profil": "DENGELI", "agirliklar": {KURAL: 1},
            "calisanlar": [{"id": "P1", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"}, "izinler": [], "uygunluk": []}],
            "vardiya_sablonlari": sablonlar, "talep": [], "kurallar": kurallar, "kilitler": [], "donmus_gunler": [],
            "sabit_atamalar": [{"calisan": "P1", "gun": d, "sablon": s} for d, s in sabit]}


def T(id_, bas, bit):
    return {"id": id_, "ekip": "E", "bas": bas, "bit": bit, "mola_dk": 0}


VAKALAR = [
    ("C1 fark tam +12: 08:00 -> ertesi gun 20:00 (sabah->aksam)", [T("A", 8, 16), T("B", 20, 28)], [(0, "A"), (1, "B")], 11, None),
    ("C2 fark tam -12: 20:00 -> ertesi gun 08:00 (aksam->sabah; dinlenme 0 ile kurulabilir)", [T("A", 20, 24), T("B", 8, 12)], [(0, "A"), (1, "B")], 0, None),
    ("C3 fark -11.75: 20:00 -> ertesi gun 08:15", [T("A", 20, 24), T("B", 8.25, 12.25)], [(0, "A"), (1, "B")], 0, None),
    ("C4 fark +12.25: 08:00 -> ertesi gun 20:15 (dairesel -11.75 geri)", [T("A", 8, 12), T("B", 20.25, 24.25)], [(0, "A"), (1, "B")], 0, None),
    ("C5 bas 24.5 (gun 0'a yazili, saat olarak gun 1 00:30-08:30) -> gun 1 10:00 (ayni takvim gunu!)", [T("A", 24.5, 32.5), T("B", 10, 18)], [(0, "A"), (1, "B")], 0, None),
    ("C5b bas 24.5 gun 0 (saatte gun 1 00:30) -> gun 2 07:00: takvimde art arda, gun alaninda degil", [T("A", 24.5, 32.5), T("B", 7, 15)], [(0, "A"), (2, "B")], 11, None),
    ("C6 23:00 -> ertesi gun bas 24.5", [T("A", 23, 31), T("B", 24.5, 32.5)], [(0, "A"), (1, "B")], 0, None),
    ("C7 bas 0 (gece yarisi gecesi 00-08) -> ertesi gun 07:00", [T("A", 0, 8), T("B", 7, 15)], [(0, "A"), (1, "B")], 11, None),
    ("C8 gece 23:00-07:00 -> ertesi gun BOS -> iki gun sonra 07:00", [T("A", 23, 31), T("B", 7, 15)], [(0, "A"), (2, "B")], 11, None),
    ("C9 gece 23:00-07:00 -> bos -> iki gun sonra 13:45 (sayilsaydi 9,25 geri)", [T("A", 23, 31), T("B", 13.75, 22)], [(0, "A"), (2, "B")], 11, None),
    ("C10 09:00-13:00 -> ertesi gun 00:00 gecesi (bas 0; tam 11 saat, 9 geri; sartname ornegi)", [T("A", 9, 13), T("B", 0, 8)], [(0, "A"), (1, "B")], 11, None),
    ("C10b 09:00-13:00 gun 0 -> gun 1'e yazili bas 24 (saatte gun 2 00:00, 35 saat ara)", [T("A", 9, 13), T("B", 24, 32)], [(0, "A"), (1, "B")], 11, None),
    ("C11 yon=geri, fark tam +12 (08 -> 20): 12 saat 'geri'", [T("A", 8, 16), T("B", 20, 28)], [(0, "A"), (1, "B")], 11, "geri"),
    ("C12 yon=geri, fark tam -12 (20 -> 08)", [T("A", 20, 24), T("B", 8, 12)], [(0, "A"), (1, "B")], 0, "geri"),
    ("C13 ayni saat (0 fark) 13:45 -> 13:45", [T("A", 13.75, 22)], [(0, "A"), (1, "A")], 11, None),
    ("C14 0,25 geri (10:15 -> 10:00): amacta 0, metrikte 0,25", [T("A", 10.25, 14.25), T("B", 10, 14)], [(0, "A"), (1, "B")], 11, None),
]

print("%-95s | %-10s | %-8s | %-12s | %s" % ("vaka", "plan", "deger", "metrik", "dogrulayici satirlari"))
for ad, sablonlar, sabit, dinlenme, yon in VAKALAR:
    g = sahne(sablonlar, sabit, dinlenme, yon)
    c = coz(g, AYAR)
    if c["durum"] != "cozuldu":
        print("%-95s | %s" % (ad, c["durum"]))
        continue
    r = degerlendir(g, c["atamalar"])
    plan = {a["gun"]: a["sablon"] for a in c["atamalar"]}
    kuruldu = all(plan.get(d) == s for d, s in sabit)
    print("%-95s | %-10s | %-8s | %-12s | %s" % (
        ad, "zorlandi" if kuruldu else "FARKLI " + str(plan), (rot_kirilim(c) or {}).get("deger", 0),
        (c["metrikler"]["rotasyon_geri_gecis"], c["metrikler"]["rotasyon_geri_saat"]),
        [(i["gun"], i["olculen"], i["mesaj"]) for i in rot_satirlari(r)]))
