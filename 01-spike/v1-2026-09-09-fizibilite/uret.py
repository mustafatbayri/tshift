#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uret.py — Spike girdi verisi üreteci.

200 çalışan, 3 ekip, 7 günlük plan dönemi, 14 günlük geçmiş.
Çıktı: girdi.json  (motorun tek girdisi — şema dokümanı budur)

Kullanım:  python3 uret.py                    # 200 çalışan → girdi.json
           python3 uret.py 1000               # 1000 çalışan → girdi.json
           python3 uret.py 1000 girdi_1000.json

Çalışan sayısı değiştiğinde TALEP DE aynı oranda ölçeklenir (doluluk %86
sabit tutulur). Aksi halde büyük veri setinde kapasite bollaşır, problem
kolaylaşır ve süre eğrisi yanıltıcı olur.
"""

import json
import random
import sys
from datetime import date, timedelta

TOHUM = 20260907
rnd = random.Random(TOHUM)

# --------------------------------------------------------------------
# Dönem
# --------------------------------------------------------------------

PLAN_BASLANGIC = date(2026, 11, 2)          # Pazartesi
GUN_SAYISI = 7
GECMIS_GUN = 14

GUN_ADI = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

# --------------------------------------------------------------------
# Ekipler
# --------------------------------------------------------------------

EKIPLER = [
    {"id": "T1", "ad": "Müşteri Deneyimi", "acilis": 7,  "kapanis": 24, "kisi": 90},
    {"id": "T2", "ad": "Teknik Destek",    "acilis": 8,  "kapanis": 22, "kisi": 70},
    {"id": "T3", "ad": "Satış Destek",     "acilis": 9,  "kapanis": 21, "kisi": 40},
]

ROLLER = ["AGENT", "KIDEMLI", "TAKIM_LIDERI"]

TEMEL_KISI = sum(e["kisi"] for e in EKIPLER)      # 200


def olcekle(hedef_kisi: int):
    """Ekip mevcutlarını hedef toplama oranla. Ekip yapısı korunur."""
    if hedef_kisi == TEMEL_KISI:
        return
    kat = hedef_kisi / TEMEL_KISI
    kalan = hedef_kisi
    for e in EKIPLER[:-1]:
        e["kisi"] = max(6, round(e["kisi"] * kat))
        kalan -= e["kisi"]
    EKIPLER[-1]["kisi"] = max(6, kalan)

# --------------------------------------------------------------------
# Vardiya şablonları
# --------------------------------------------------------------------

SABLONLAR = [
    # id,   ekip, bas, bit, mola_dk
    ("S1",  "T1",  7, 15, 60),
    ("S2",  "T1",  9, 17, 60),
    ("S3",  "T1", 12, 20, 60),
    ("S4",  "T1", 16, 24, 60),
    ("S5",  "T1", 17, 22, 30),   # yarı zamanlı
    ("S6",  "T2",  8, 16, 60),
    ("S7",  "T2", 10, 18, 60),
    ("S8",  "T2", 14, 22, 60),
    ("S9",  "T2", 17, 22, 30),   # yarı zamanlı
    ("S10", "T3",  9, 17, 60),
    ("S11", "T3", 13, 21, 60),
    ("S12", "T3", 16, 21, 30),   # yarı zamanlı
]

# --------------------------------------------------------------------
# Talep eğrisi
# --------------------------------------------------------------------

def talep_katsayisi(ekip_id: str, gun: int, saat: int) -> float:
    """Saatlik yoğunluk profili (0–1 arası göreli)."""
    hafta_sonu = gun >= 5
    if ekip_id == "T1":          # çağrı yoğunluğu: sabah rampa, öğle düşüş, akşam tepe
        if saat < 9:    k = 0.35
        elif saat < 12: k = 0.80
        elif saat < 14: k = 0.62
        elif saat < 18: k = 0.85
        elif saat < 21: k = 1.00
        elif saat < 23: k = 0.62
        else:           k = 0.35
        if gun == 4 and 17 <= saat < 20:   # cuma akşam tepesi
            k *= 1.18
    elif ekip_id == "T2":        # teknik destek: mesai saatleri ağırlıklı
        if saat < 10:   k = 0.55
        elif saat < 13: k = 1.00
        elif saat < 15: k = 0.70
        elif saat < 19: k = 0.90
        else:           k = 0.50
    else:                        # satış: öğleden sonra
        if saat < 11:   k = 0.45
        elif saat < 14: k = 0.75
        elif saat < 18: k = 1.00
        else:           k = 0.65
    if hafta_sonu:
        k *= 0.58 if ekip_id != "T1" else 0.66
    return k


def talep_uret(hedef_doluluk: float, etkin_kapasite_sa: float):
    """Eğriyi, toplam talep ≈ hedef_doluluk × etkin kapasite olacak şekilde ölçekler."""
    ham = []
    toplam_ham = 0.0
    for e in EKIPLER:
        for g in range(GUN_SAYISI):
            for s in range(e["acilis"], e["kapanis"]):
                k = talep_katsayisi(e["id"], g, s) * e["kisi"]
                ham.append({"ekip": e["id"], "gun": g, "saat": s, "ham": k})
                toplam_ham += k
    olcek = (hedef_doluluk * etkin_kapasite_sa) / toplam_ham
    talep = []
    for h in ham:
        hedef = max(1, round(h["ham"] * olcek))
        asgari = max(1, round(hedef * 0.72))
        talep.append({
            "ekip": h["ekip"], "gun": h["gun"], "saat": h["saat"],
            "asgari": asgari, "hedef": hedef,
        })
    return talep


# --------------------------------------------------------------------
# Çalışanlar
# --------------------------------------------------------------------

AD = ["Elif","Mert","Zeynep","Burak","Ayşe","Can","Deniz","Emre","Selin","Kaan",
      "Nur","Onur","Ece","Serkan","Melis","Baran","İrem","Tolga","Sude","Ahmet",
      "Gizem","Yusuf","Pınar","Cem","Buse","Efe","Derya","Arda","Ceren","Berk",
      "Aslı","Umut","Naz","Ozan","Sıla","Barış","Duygu","Kerem","Esra","Hakan"]
SOYAD = ["Yılmaz","Demir","Şahin","Çelik","Yıldız","Aydın","Öztürk","Kaya","Arslan",
         "Doğan","Kılıç","Aslan","Çetin","Kurt","Özdemir","Şimşek","Polat","Korkmaz"]


def saat_str(x: float) -> str:
    """24.0 -> '24:00' (gün sonu). Modulo alınırsa vardiya sıfır uzunluğa düşer."""
    h = int(x)
    m = int(round((x - h) * 60))
    return f"{h:02d}:{m:02d}"


def calisanlar_uret():
    calisanlar = []
    no = 0
    for e in EKIPLER:
        # rol dağılımı: her ekipte ~%8 takım lideri, ~%18 kıdemli
        lider_sayisi = max(4, round(e["kisi"] * 0.09))
        kidemli_sayisi = round(e["kisi"] * 0.18)
        for i in range(e["kisi"]):
            no += 1
            eid = f"E{no:03d}"
            if i < lider_sayisi:
                roller = ["AGENT", "KIDEMLI", "TAKIM_LIDERI"]
            elif i < lider_sayisi + kidemli_sayisi:
                roller = ["AGENT", "KIDEMLI"]
            else:
                roller = ["AGENT"]

            # ~%18 yarı zamanlı (üniversite öğrencisi)
            ogrenci = "TAKIM_LIDERI" not in roller and rnd.random() < 0.20
            tur = "YARI_ZAMANLI" if ogrenci else "TAM_ZAMANLI"
            sozlesme = 1200 if ogrenci else 2400      # dakika/hafta

            uygunluk = []
            if ogrenci:
                # ders programı: 2–3 gün sabah/öğlen kapalı
                ders_gunleri = rnd.sample(range(5), rnd.choice([2, 3]))
                for g in ders_gunleri:
                    bit = rnd.choice([14, 15, 16, 17])
                    uygunluk.append({
                        "gun": g, "bas": "00:00", "bit": saat_str(bit),
                        "tip": "UYGUN_DEGIL", "sebep": "OKUL",
                    })
                if rnd.random() < 0.3:                # bir gün tamamen kapalı
                    g = rnd.choice([x for x in range(5) if x not in ders_gunleri])
                    uygunluk.append({
                        "gun": g, "bas": "00:00", "bit": "24:00",
                        "tip": "UYGUN_DEGIL", "sebep": "OKUL",
                    })
            else:
                # tam zamanlıların bir kısmında bakım/ulaşım kaynaklı pencere
                if rnd.random() < 0.10:
                    g = rnd.randrange(7)
                    uygunluk.append({
                        "gun": g, "bas": "00:00", "bit": "12:00",
                        "tip": "UYGUN_DEGIL", "sebep": "BAKIM",
                    })

            izinler = []
            if rnd.random() < 0.07:
                bas = rnd.randrange(7)
                for g in range(bas, min(7, bas + rnd.choice([1, 1, 2, 3]))):
                    izinler.append({"gun": g, "tum_gun": True})

            calisanlar.append({
                "id": eid,
                "ad": f"{rnd.choice(AD)} {rnd.choice(SOYAD)}",
                "ekip": e["id"],
                "durum": "PASIF" if rnd.random() < 0.02 else "AKTIF",
                "tur": tur,
                "sozlesme_dk_hafta": sozlesme,
                "sozlesme_bitis": None if rnd.random() > 0.06 else
                                  (PLAN_BASLANGIC + timedelta(days=rnd.randrange(2, 7))).isoformat(),
                "roller": roller,
                "uygunluk": uygunluk,
                "izinler": izinler,
            })
    return calisanlar


# --------------------------------------------------------------------
# Geçmiş (gerçekleşen)
# --------------------------------------------------------------------

def gecmis_uret(calisanlar):
    gecmis = []
    sablon_by_ekip = {}
    for sid, ekip, bas, bit, mola in SABLONLAR:
        sablon_by_ekip.setdefault(ekip, []).append((bas, bit))

    for c in calisanlar:
        if c["durum"] != "AKTIF":
            continue
        secenek = sablon_by_ekip[c["ekip"]]
        for d in range(GECMIS_GUN, 0, -1):
            tarih = PLAN_BASLANGIC - timedelta(days=d)
            hafta_sonu = tarih.weekday() >= 5
            calisma_olasi = 0.42 if hafta_sonu else 0.74
            if c["tur"] == "YARI_ZAMANLI":
                calisma_olasi *= 0.55
            if rnd.random() > calisma_olasi:
                continue
            bas, bit = rnd.choice(secenek)
            # gerçekleşen: plandan birkaç dakika sapar
            g_bas = bas + rnd.choice([0, 0, 0, 0.25])
            g_bit = bit + rnd.choice([-0.25, 0, 0, 0, 0.5])
            gecmis.append({
                "calisan": c["id"],
                "tarih": tarih.isoformat(),
                "bas": saat_str(g_bas),
                "bit": saat_str(min(24, g_bit)),
                "kaynak": "GERCEKLESEN",
            })
    return gecmis


# --------------------------------------------------------------------
# Kurallar (çekirdek 17)
# --------------------------------------------------------------------

KURALLAR = [
    {"kod": "AKTIF_CALISAN",           "tur": "SERT",    "param": {}},
    {"kod": "SOZLESME_GECERLI",        "tur": "SERT",    "param": {}},
    {"kod": "ONAYLI_IZIN",             "tur": "SERT",    "param": {}},
    {"kod": "UYGUNLUK_TAKVIMI",        "tur": "SERT",    "param": {"kayit_yoksa": "TAM_UYGUN"}},
    {"kod": "CAKISMA_YOK",             "tur": "SERT",    "param": {"tolerans_dk": 0}},
    {"kod": "CALISMA_SAATLERI",        "tur": "SERT",    "param": {}},
    {"kod": "GUNLUK_AZAMI",            "tur": "SERT",    "param": {"saat": 9}},
    {"kod": "HAFTALIK_AZAMI",          "tur": "SERT",    "param": {"saat": 45}},
    {"kod": "PART_TIME_LIMIT",         "tur": "SERT",    "param": {}},
    {"kod": "VARDIYA_ARASI_DINLENME",  "tur": "SERT",    "param": {"saat": 11}},
    {"kod": "HAFTA_TATILI",            "tur": "SERT",    "param": {"pencere_gun": 7, "saat": 24}},
    {"kod": "ASGARI_KAPSAMA",          "tur": "SERT",    "param": {}},
    {"kod": "ROL_KAPSAMASI",           "tur": "SERT",    "param": {"rol": "TAKIM_LIDERI", "asgari": 1}},
    {"kod": "MOLA_HAKKI",              "tur": "SERT",
     "param": {"bantlar": [[0, 4, 15], [4, 7.5, 30], [7.5, 24, 60]]}},
    {"kod": "MOLA_KAPSAMASI",          "tur": "SERT",    "param": {}},
    {"kod": "HEDEF_KAPSAMA",           "tur": "YUMUSAK", "agirlik": 9},
    {"kod": "SAAT_DENGESI",            "tur": "YUMUSAK", "agirlik": 6, "param": {"tolerans_saat": 2}},
]

HEDEF_PROFILLERI = {
    "DENGELI":  {"kapsama": 9,  "adalet": 6, "fazla_mesai": 6, "kararlilik": 5},
    "KAPSAMA":  {"kapsama": 10, "adalet": 2, "fazla_mesai": 2, "kararlilik": 2},
    "CALISAN":  {"kapsama": 6,  "adalet": 9, "fazla_mesai": 9, "kararlilik": 9},
}


# --------------------------------------------------------------------

def main(cikti="girdi.json"):
    calisanlar = calisanlar_uret()
    aktif = [c for c in calisanlar if c["durum"] == "AKTIF"]

    # etkin kapasite: sözleşme saati eksi mola payı (~%11)
    ham_kapasite_sa = sum(c["sozlesme_dk_hafta"] for c in aktif) / 60.0
    etkin_kapasite_sa = ham_kapasite_sa * 0.89

    talep = talep_uret(hedef_doluluk=0.86, etkin_kapasite_sa=etkin_kapasite_sa)
    gecmis = gecmis_uret(calisanlar)

    girdi = {
        "_aciklama": "TShift spike girdi paketi. Saatler 'HH:MM'. Gün 0=Pazartesi.",
        "donem": {
            "baslangic": PLAN_BASLANGIC.isoformat(),
            "gun": GUN_SAYISI,
            "cozunurluk_dk": 60,
            "hafta_baslangici": "PAZARTESI",
        },
        "ekipler": [
            {"id": e["id"], "ad": e["ad"],
             "acilis": saat_str(e["acilis"]), "kapanis": saat_str(e["kapanis"])}
            for e in EKIPLER
        ],
        "roller": ROLLER,
        "sablonlar": [
            {"id": s, "ekip": ek, "bas": saat_str(b), "bit": saat_str(t), "mola_dk": m}
            for s, ek, b, t, m in SABLONLAR
        ],
        "calisanlar": calisanlar,
        "talep": talep,
        "gecmis": gecmis,
        "kurallar": KURALLAR,
        "hedef_profilleri": HEDEF_PROFILLERI,
    }

    with open(cikti, "w", encoding="utf-8") as f:
        json.dump(girdi, f, ensure_ascii=False, indent=1)

    toplam_talep = sum(t["hedef"] for t in talep)
    toplam_asgari = sum(t["asgari"] for t in talep)
    ogrenci = sum(1 for c in aktif if c["tur"] == "YARI_ZAMANLI")
    izinli = sum(1 for c in aktif if c["izinler"])

    print(f"{cikti} yazıldı")
    print(f"  çalışan            : {len(calisanlar)} ({len(aktif)} aktif, {ogrenci} yarı zamanlı)")
    print(f"  ekip               : {len(EKIPLER)}")
    print(f"  izinli çalışan     : {izinli}")
    print(f"  uygunluk kısıtı    : {sum(1 for c in aktif if c['uygunluk'])} çalışanda")
    print(f"  talep hücresi      : {len(talep)}  (hedef {toplam_talep} / asgari {toplam_asgari} kişi-saat)")
    print(f"  ham kapasite       : {ham_kapasite_sa:.0f} kişi-saat")
    print(f"  etkin kapasite     : {etkin_kapasite_sa:.0f} kişi-saat (mola düşülmüş)")
    print(f"  doluluk            : %{100 * toplam_talep / etkin_kapasite_sa:.1f}")
    print(f"  geçmiş kayıt       : {len(gecmis)} ({GECMIS_GUN} gün, gerçekleşen)")
    print(f"  kural              : {len(KURALLAR)} ({sum(1 for k in KURALLAR if k['tur']=='SERT')} sert)")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else TEMEL_KISI
    yol = sys.argv[2] if len(sys.argv) > 2 else "girdi.json"
    olcekle(n)
    main(yol)
