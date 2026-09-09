#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uret_otel.py — OTEL operasyonu girdi üreteci (7/24, gece vardiyalı).

Çağrı merkezi veri seti tek sektörü test ediyordu ve 07:00–24:00 arası
çalışıyordu; hiçbir vardiya gün aşmıyordu. Otel senaryosu ürünün asıl
iddiasını sınar: AYNI kural havuzu, AYNI motor, farklı sektör.

Yeni olan ne
  - 7/24 departmanlar (ön büro, güvenlik) → gece vardiyası 23:00–07:00
  - Gün aşan vardiya: bitiş "31:00" olarak yazılır (bkz. degerlendirici.hucreler)
  - Geçmiş veride pazar gecesi başlayan vardiya, planın 0. gününe DEVREDER
  - İki yeni kural: GECE_VARDIYASI_AZAMI (İş Kanunu md.69) ve
    ARDISIK_GECE_LIMIT — kural havuzundan seçiliyor, koda gömülü değil

Çıktı: girdi_otel.json   (şema çağrı merkezi girdisiyle birebir aynı)
Kullanım:  py uret_otel.py  [çalışan_sayısı]  [çıktı_dosyası]
"""

import json
import random
import sys
from datetime import date, timedelta

TOHUM = 20261103
rnd = random.Random(TOHUM)

PLAN_BASLANGIC = date(2026, 11, 2)          # Pazartesi
GUN_SAYISI = 7
GECMIS_GUN = 14

# --------------------------------------------------------------------
# Departmanlar
# --------------------------------------------------------------------

EKIPLER = [
    {"id": "D1", "ad": "Ön Büro",         "acilis": 0,  "kapanis": 24, "kisi": 45},
    {"id": "D2", "ad": "Kat Hizmetleri",  "acilis": 7,  "kapanis": 20, "kisi": 110},
    {"id": "D3", "ad": "Yiyecek-İçecek",  "acilis": 6,  "kapanis": 24, "kisi": 70},
    {"id": "D4", "ad": "Mutfak",          "acilis": 5,  "kapanis": 23, "kisi": 45},
    {"id": "D5", "ad": "Güvenlik",        "acilis": 0,  "kapanis": 24, "kisi": 30},
]

ROLLER = ["PERSONEL", "KIDEMLI", "TAKIM_LIDERI"]

# YETKİNLİK ≠ EKİP.  Ekip "kim kiminle çalışır"ı, yetkinlik "kim neyi
# yapabilir"i söyler. Aynı ekipte farklı yetkinlikler bulunur ve bazı
# saatlerde belirli bir yetkinliğin sahada olması zorunludur.
YETKINLIKLER = ["YABANCI_DIL", "ILK_YARDIM", "BARISTA", "HACCP"]

# departman -> {yetkinlik: o departmanda görülme oranı}
YETKINLIK_ORANI = {
    "D1": {"YABANCI_DIL": 0.55, "ILK_YARDIM": 0.20},
    "D2": {"YABANCI_DIL": 0.10, "ILK_YARDIM": 0.15},
    "D3": {"YABANCI_DIL": 0.30, "BARISTA": 0.35, "ILK_YARDIM": 0.15},
    "D4": {"HACCP": 0.45, "ILK_YARDIM": 0.15},
    "D5": {"ILK_YARDIM": 0.55, "YABANCI_DIL": 0.20},
}
TEMEL_KISI = sum(e["kisi"] for e in EKIPLER)


def olcekle(hedef):
    if hedef == TEMEL_KISI:
        return
    kat = hedef / TEMEL_KISI
    kalan = hedef
    for e in EKIPLER[:-1]:
        e["kisi"] = max(8, round(e["kisi"] * kat))
        kalan -= e["kisi"]
    EKIPLER[-1]["kisi"] = max(8, kalan)


# --------------------------------------------------------------------
# Vardiya şablonları  (bit > 24 => ertesi güne taşar)
# --------------------------------------------------------------------
# Hiçbir şablon 9 saatlik günlük azamiyi aşmaz.
# Gece şablonu 23–31: gece penceresine (20:00–06:00) düşen 7 saat,
# 60 dk molayla 6 saate iner → GECE_VARDIYASI_AZAMI (7,5 sa) sağlanır.

SABLONLAR = [
    # id,    ekip,  bas, bit, mola_dk
    ("O1",   "D1",   7,  15, 60),   # sabah — check-out yoğunluğu
    ("O2",   "D1",  15,  23, 60),   # akşam — check-in yoğunluğu
    ("O3",   "D1",  23,  31, 60),   # GECE
    ("O4",   "D1",  11,  16, 30),   # yarı zamanlı destek

    ("K1",   "D2",   7,  15, 60),
    ("K2",   "D2",   9,  17, 60),
    ("K3",   "D2",  12,  20, 60),
    ("K4",   "D2",  10,  15, 30),   # yarı zamanlı

    ("F1",   "D3",   6,  14, 60),   # kahvaltı
    ("F2",   "D3",  14,  22, 60),   # akşam servisi
    ("F3",   "D3",  16,  24, 60),
    ("F4",   "D3",  18,  23, 30),   # yarı zamanlı

    ("M1",   "D4",   5,  13, 60),   # kahvaltı hazırlık
    ("M2",   "D4",  11,  19, 60),
    ("M3",   "D4",  15,  23, 60),
    ("M4",   "D4",  17,  22, 30),   # yarı zamanlı

    ("G1",   "D5",   7,  15, 60),
    ("G2",   "D5",  15,  23, 60),
    ("G3",   "D5",  23,  31, 60),   # GECE
]

GECE_SABLON = {"O3", "G3"}


def saat_str(x: float) -> str:
    """24.0 -> '24:00', 31.0 -> '31:00' (ertesi gün 07:00)."""
    h = int(x)
    m = int(round((x - h) * 60))
    return f"{h:02d}:{m:02d}"


# --------------------------------------------------------------------
# Talep eğrisi — otele özgü tepeler
# --------------------------------------------------------------------

def talep_katsayisi(ekip: str, gun: int, saat: int) -> float:
    hafta_sonu = gun >= 4          # otelde cuma-pazar yoğun
    if ekip == "D1":               # ön büro: check-out sabah, check-in akşam
        if saat < 6:    k = 0.22   # gece nöbeti — düşük ama sıfır değil
        elif saat < 8:  k = 0.45
        elif saat < 12: k = 0.95   # check-out
        elif saat < 14: k = 0.55
        elif saat < 19: k = 1.00   # check-in
        elif saat < 23: k = 0.60
        else:           k = 0.25
    elif ekip == "D2":             # kat hizmetleri: check-out sonrası
        if saat < 9:    k = 0.45
        elif saat < 15: k = 1.00
        elif saat < 18: k = 0.70
        else:           k = 0.35
    elif ekip == "D3":             # F&B: kahvaltı ve akşam yemeği
        if saat < 10:   k = 1.00   # kahvaltı
        elif saat < 12: k = 0.55
        elif saat < 15: k = 0.70   # öğle
        elif saat < 18: k = 0.45
        elif saat < 22: k = 0.95   # akşam
        else:           k = 0.40
    elif ekip == "D4":             # mutfak: servisin bir saat önü
        if saat < 9:    k = 0.95
        elif saat < 12: k = 0.55
        elif saat < 15: k = 0.75
        elif saat < 17: k = 0.50
        elif saat < 22: k = 1.00
        else:           k = 0.35
    else:                          # güvenlik: neredeyse düz, gece hafif artar
        k = 0.85 if 22 <= saat or saat < 6 else 0.70
    if hafta_sonu:
        k *= 1.15 if ekip in ("D1", "D3") else 1.05
    return k


def talep_uret(hedef_doluluk, etkin_kapasite_sa):
    ham, toplam = [], 0.0
    for e in EKIPLER:
        for g in range(GUN_SAYISI):
            for s in range(e["acilis"], e["kapanis"]):
                k = talep_katsayisi(e["id"], g, s) * e["kisi"]
                ham.append({"ekip": e["id"], "gun": g, "saat": s, "ham": k})
                toplam += k
    olcek = (hedef_doluluk * etkin_kapasite_sa) / toplam
    talep = []
    for h in ham:
        hedef = max(1, round(h["ham"] * olcek))
        talep.append({
            "ekip": h["ekip"], "gun": h["gun"], "saat": h["saat"],
            "asgari": max(1, round(hedef * 0.72)), "hedef": hedef,
        })
    return talep


# --------------------------------------------------------------------
# Çalışanlar
# --------------------------------------------------------------------

AD = ["Elif", "Mert", "Zeynep", "Burak", "Ayşe", "Can", "Deniz", "Emre", "Selin",
      "Kaan", "Nur", "Onur", "Ece", "Serkan", "Melis", "Baran", "İrem", "Tolga",
      "Sude", "Ahmet", "Gizem", "Yusuf", "Pınar", "Cem", "Buse", "Efe", "Derya",
      "Arda", "Ceren", "Berk", "Aslı", "Umut", "Naz", "Ozan", "Sıla", "Barış"]
SOYAD = ["Yılmaz", "Demir", "Şahin", "Çelik", "Yıldız", "Aydın", "Öztürk", "Kaya",
         "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kurt", "Özdemir", "Polat"]


def calisanlar_uret():
    calisanlar, no = [], 0
    for e in EKIPLER:
        # 7/24 departmanda lider oranı yüksek olmak ZORUNDA: 168 saatin
        # tamamında en az bir lider bulunacak ve o lider molaya da çıkacak.
        # Yani her lider vardiyasında ikinci bir liderin çakışması gerekir.
        # Bu bir kural gevşetmesi değil, kadro gerçeği — 24 saat açık bir
        # departman, 9-5 çalışandan daha çok süpervizör ister.
        yedi_yirmidort = e["acilis"] == 0 and e["kapanis"] == 24
        # Uzun açık departmanda da lider ihtiyacı yüksek: 11 saatlik dinlenme
        # kuralı akşam→ertesi sabah geçişini yasakladığı için bir lider ardışık
        # günlerde farklı vardiyalara serbestçe konamıyor.
        lider_sayisi = max(10 if yedi_yirmidort else 6,
                           round(e["kisi"] * (0.26 if yedi_yirmidort else 0.15)))
        kidemli_sayisi = round(e["kisi"] * 0.18)
        for i in range(e["kisi"]):
            no += 1
            eid = f"H{no:03d}"
            if i < lider_sayisi:
                roller = ["PERSONEL", "KIDEMLI", "TAKIM_LIDERI"]
            elif i < lider_sayisi + kidemli_sayisi:
                roller = ["PERSONEL", "KIDEMLI"]
            else:
                roller = ["PERSONEL"]

            # yarı zamanlı: otelde çoğunlukla F&B ve kat hizmetlerinde
            pt_oran = {"D2": 0.22, "D3": 0.25, "D4": 0.15}.get(e["id"], 0.05)
            ogrenci = "TAKIM_LIDERI" not in roller and rnd.random() < pt_oran
            tur = "YARI_ZAMANLI" if ogrenci else "TAM_ZAMANLI"
            sozlesme = 1200 if ogrenci else 2400        # dakika/hafta

            uygunluk = []
            if ogrenci:
                ders = rnd.sample(range(5), rnd.choice([2, 3]))
                for g in ders:
                    uygunluk.append({"gun": g, "bas": "00:00",
                                     "bit": saat_str(rnd.choice([14, 15, 16])),
                                     "tip": "UYGUN_DEGIL", "sebep": "OKUL"})
            elif rnd.random() < 0.08:
                uygunluk.append({"gun": rnd.randrange(7), "bas": "00:00",
                                 "bit": "12:00", "tip": "UYGUN_DEGIL",
                                 "sebep": "ULASIM"})

            izinler = []
            if rnd.random() < 0.06:
                izinler.append({"gun": rnd.randrange(7), "tum_gun": True})

            durum = "PASIF" if rnd.random() < 0.03 else "AKTIF"
            sozlesme_bitis = None
            if rnd.random() < 0.04:                     # sezonluk sözleşme
                sozlesme_bitis = (PLAN_BASLANGIC + timedelta(
                    days=rnd.choice([3, 4, 5]))).isoformat()

            yetk = [y for y, p in YETKINLIK_ORANI.get(e["id"], {}).items()
                    if rnd.random() < p]
            if "TAKIM_LIDERI" in roller and "ILK_YARDIM" not in yetk:
                yetk.append("ILK_YARDIM")      # liderlerde ilk yardım standart

            calisanlar.append({
                "id": eid,
                "yetkinlikler": yetk,
                "ad": f"{rnd.choice(AD)} {rnd.choice(SOYAD)}",
                "ekip": e["id"], "durum": durum, "tur": tur,
                "sozlesme_dk_hafta": sozlesme,
                "sozlesme_bitis": sozlesme_bitis,
                "roller": roller,
                "uygunluk": uygunluk,
                "izinler": izinler,
            })
    return calisanlar


# --------------------------------------------------------------------
# Geçmiş (gerçekleşen) — pazar gecesi vardiyası plana DEVREDER
# --------------------------------------------------------------------

def gecmis_uret(calisanlar, talep):
    """Geçmiş = gerçekleşen vardiyalar.

    ÖNEMLİ: son gecenin (plan başlangıcından bir önceki gün) gece vardiyası,
    plan haftasının 0. gününün ilk saatlerini kapsar. Bunu rastgele bırakırsak
    0. günün sabahında GERÇEK OLMAYAN bir açık doğar — oysa önceki haftanın
    planı da geçerli bir plandı. Bu yüzden son gece, 0. günün asgari talebini
    karşılayacak kadar kişiyle (lider dahil) doldurulur.
    """
    kayit = []
    sab = {}
    for sid, ek, b, t, mola in SABLONLAR:
        sab.setdefault(ek, []).append((sid, b, t))
    aktif = [c for c in calisanlar if c["durum"] == "AKTIF"]
    son_gece = PLAN_BASLANGIC - timedelta(days=1)

    # --- son gece: devir kadrosu ---
    asgari0 = {}
    for t in talep:
        if t["gun"] == 0 and t["saat"] < 7:
            k = t["ekip"]
            asgari0[k] = max(asgari0.get(k, 0), t["asgari"])
    devredenler = set()
    for sid, ek, b, t_, m in SABLONLAR:
        if sid not in GECE_SABLON:
            continue
        gerek = asgari0.get(ek, 0)
        if not gerek:
            continue
        havuz = [c for c in aktif if c["ekip"] == ek]
        liderler = [c for c in havuz if "TAKIM_LIDERI" in c["roller"]]
        digerler = [c for c in havuz if "TAKIM_LIDERI" not in c["roller"]]
        rnd.shuffle(liderler); rnd.shuffle(digerler)
        # en az 2 lider (biri molada olabilir) + kalanı personel
        secim = liderler[:2] + digerler[:max(0, gerek + 1 - 2)]
        for c in secim:
            devredenler.add(c["id"])
            kayit.append({"calisan": c["id"], "tarih": son_gece.isoformat(),
                          "bas": saat_str(b), "bit": saat_str(t_),
                          "kaynak": "GERCEKLESEN"})

    # --- geri kalan geçmiş: rastgele ama gerçekçi ---
    for gun_ofset in range(-GECMIS_GUN, 0):
        tarih = PLAN_BASLANGIC + timedelta(days=gun_ofset)
        for c in aktif:
            if gun_ofset == -1 and c["id"] in devredenler:
                continue                      # zaten gece vardiyasına yazıldı
            if rnd.random() > (0.62 if c["tur"] == "TAM_ZAMANLI" else 0.42):
                continue
            adaylar = [x for x in sab[c["ekip"]]
                       if not (gun_ofset == -1 and x[0] in GECE_SABLON)]
            if not adaylar:
                continue
            sid, b, t_ = rnd.choice(adaylar)
            kayit.append({
                "calisan": c["id"],
                "tarih": tarih.isoformat(),
                "bas": saat_str(b), "bit": saat_str(t_),
                "kaynak": "GERCEKLESEN",
            })
    return kayit


# --------------------------------------------------------------------

KURALLAR = [
    {"kod": "AKTIF_CALISAN", "tur": "SERT", "param": {}},
    {"kod": "SOZLESME_GECERLI", "tur": "SERT", "param": {}},
    {"kod": "ONAYLI_IZIN", "tur": "SERT", "param": {}},
    {"kod": "UYGUNLUK_TAKVIMI", "tur": "SERT", "param": {"kayit_yoksa": "TAM_UYGUN"}},
    {"kod": "CAKISMA_YOK", "tur": "SERT", "param": {"tolerans_dk": 0}},
    {"kod": "CALISMA_SAATLERI", "tur": "SERT", "param": {}},
    {"kod": "GUNLUK_AZAMI", "tur": "SERT", "param": {"saat": 9}},
    {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "param": {"saat": 45}},
    {"kod": "PART_TIME_LIMIT", "tur": "SERT", "param": {}},
    {"kod": "VARDIYA_ARASI_DINLENME", "tur": "SERT", "param": {"saat": 11}},
    {"kod": "HAFTA_TATILI", "tur": "SERT", "param": {"pencere_gun": 7, "saat": 24}},
    {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "param": {}},
    {"kod": "ROL_KAPSAMASI", "tur": "SERT",
     "param": {"rol": "TAKIM_LIDERI", "asgari": 1}},
    {"kod": "MOLA_HAKKI", "tur": "SERT",
     "param": {"bantlar": [[0, 4, 15], [4, 7.5, 30], [7.5, 24, 60]]}},
    {"kod": "MOLA_KAPSAMASI", "tur": "SERT", "param": {}},
    # --- otel/7-24 operasyonlarına özgü, havuzdan seçilen iki kural ---
    {"kod": "GECE_VARDIYASI_AZAMI", "tur": "SERT",
     "param": {"saat": 7.5, "bas": "20:00", "bit": "06:00"}},
    {"kod": "ARDISIK_GECE_LIMIT", "tur": "SERT",
     "param": {"ardisik": 3, "bas": "20:00", "bit": "06:00"}},
    # YETKİNLİK KAPSAMASI — ROL_KAPSAMASI ile AYNI mekanizmadır; tek fark
    # çalışanın hangi özelliğine bakıldığıdır. Ürün tarafında tek bir kural
    # tipi olarak tasarlanmalı, iki ayrı kural olarak değil.
    {"kod": "YETKINLIK_KAPSAMASI", "tur": "SERT", "param": {"gereksinimler": [
        {"ekip": "D1", "yetkinlik": "YABANCI_DIL", "asgari": 1},
        {"ekip": "D3", "yetkinlik": "BARISTA", "asgari": 1,
         "saatler": [6, 7, 8, 9, 10]},
        {"ekip": "D4", "yetkinlik": "HACCP", "asgari": 1},
        {"ekip": "D5", "yetkinlik": "ILK_YARDIM", "asgari": 1},
    ]}},
    {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "agirlik": 9},
    {"kod": "SAAT_DENGESI", "tur": "YUMUSAK", "agirlik": 6,
     "param": {"tolerans_saat": 2}},
]

PROFILLER = {
    "DENGELI": {"kapsama": 9, "adalet": 6, "fazla_mesai": 6, "kararlilik": 5},
    "KAPSAMA": {"kapsama": 10, "adalet": 2, "fazla_mesai": 2, "kararlilik": 2},
    "CALISAN": {"kapsama": 6, "adalet": 9, "fazla_mesai": 9, "kararlilik": 9},
}


def main(cikti="girdi_otel.json"):
    calisanlar = calisanlar_uret()
    aktif = [c for c in calisanlar if c["durum"] == "AKTIF"]
    ham = sum(c["sozlesme_dk_hafta"] for c in aktif) / 60.0
    etkin = ham * 0.88
    talep = talep_uret(0.84, etkin)
    gecmis = gecmis_uret(calisanlar, talep)

    girdi = {
        "_aciklama": "TShift OTEL girdi paketi. 7/24 operasyon; gece vardiyası "
                     "bitişi 24'ü aşabilir (23:00-31:00 = ertesi gün 07:00).",
        "donem": {"baslangic": PLAN_BASLANGIC.isoformat(), "gun": GUN_SAYISI,
                  "cozunurluk_dk": 60, "hafta_baslangici": "PAZARTESI"},
        "ekipler": [{"id": e["id"], "ad": e["ad"],
                     "acilis": saat_str(e["acilis"]),
                     "kapanis": saat_str(e["kapanis"])} for e in EKIPLER],
        "roller": ROLLER,
        "yetkinlikler": YETKINLIKLER,
        "sablonlar": [{"id": s, "ekip": ek, "bas": saat_str(b),
                       "bit": saat_str(t), "mola_dk": m}
                      for s, ek, b, t, m in SABLONLAR],
        "calisanlar": calisanlar,
        "talep": talep,
        "gecmis": gecmis,
        "kurallar": KURALLAR,
        "hedef_profilleri": PROFILLER,
    }

    with open(cikti, "w", encoding="utf-8") as f:
        json.dump(girdi, f, ensure_ascii=False, indent=1)

    devir = sum(1 for h in gecmis
                if h["tarih"] == (PLAN_BASLANGIC - timedelta(days=1)).isoformat()
                and float(h["bit"].split(":")[0]) >= 24)
    gece_sab = sum(1 for s, _e, _b, _t, _m in SABLONLAR if s in GECE_SABLON)

    print(f"{cikti} yazıldı")
    print(f"  çalışan            : {len(calisanlar)} ({len(aktif)} aktif, "
          f"{sum(1 for c in aktif if c['tur']=='YARI_ZAMANLI')} yarı zamanlı)")
    print(f"  departman          : {len(EKIPLER)}  "
          f"({sum(1 for e in EKIPLER if e['acilis']==0 and e['kapanis']==24)} tanesi 7/24)")
    print(f"  takım lideri       : {sum(1 for c in aktif if 'TAKIM_LIDERI' in c['roller'])}")
    print(f"  şablon             : {len(SABLONLAR)}  ({gece_sab} gece, gün aşan)")
    print(f"  talep hücresi      : {len(talep)}  "
          f"(hedef {sum(t['hedef'] for t in talep)} / "
          f"asgari {sum(t['asgari'] for t in talep)} kişi-saat)")
    print(f"  etkin kapasite     : {etkin:.0f} kişi-saat")
    print(f"  geçmiş kayıt       : {len(gecmis)} ({GECMIS_GUN} gün, gerçekleşen)")
    print(f"  plana devreden     : {devir} gece vardiyası (0. günün ilk saatleri)")
    import collections as _c
    yc = _c.Counter(y for x in aktif for y in x.get("yetkinlikler", []))
    print(f"  yetkinlik dağılımı : {dict(yc)}")
    print(f"  kural              : {len(KURALLAR)} "
          f"({sum(1 for k in KURALLAR if k['tur']=='SERT')} sert, "
          f"2'si otele özgü)")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else TEMEL_KISI
    yol = sys.argv[2] if len(sys.argv) > 2 else "girdi_otel.json"
    olcekle(n)
    main(yol)
