#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
talep.py — YÜK VERİSİNDEN TALEP ÜRETİMİ

Firmadan gelen "beklenen yük" verisini saatlik KİŞİ İHTİYACINA çevirir.
Motorun bugüne kadarki girdisi olan `talep` listesi artık elle değil, bu
katman tarafından üretilir.

İKİ MODEL — ve departman bazında seçilir, kurum bazında değil
    Bir otelin rezervasyon masası çağrı merkezi gibi davranır; kat hizmetleri
    doluluğa bağlıdır. Aynı müşteride iki model birden çalışır. Bu yüzden
    model tanımı EKİBE bağlanır.

    1) ERLANG  — işlem hacmi + ortalama işlem süresi + servis seviyesi hedefi
       "Saatte 45 çağrı, ortalama 240 sn, çağrıların %80'i 20 sn içinde
        karşılansın" → kaç kişi gerekir?
       Kuyruk teorisi (Erlang C). Çağrı merkezi, rezervasyon, destek masası.

    2) ORAN    — sürücü metriği × birim başına personel
       "180 dolu oda, 15 oda başına 1 kat görevlisi" → 12 kişi
       Otel, restoran (kuver), perakende (işlem/ciro).

DOĞRULAMA
    Erlang C bir FORMÜL. Formülü yanlış kodlarsak sistem kusursuz çalışır ve
    yanlış kadro söyler — bu projedeki en sinsi hata türü. Bu yüzden formül,
    bağımsız bir KUYRUK BENZETİMİYLE (simülasyon) doğrulanır: aynı yükte
    gerçekten hedeflenen servis seviyesi tutuyor mu?

    Aynı ilke: üreten kod ile doğrulayan kod ayrı.

Kullanım:
    py talep.py            # formül testleri + benzetim doğrulaması
    py talep.py --demo     # örnek yük verisinden talep üretimi
"""

import math
import random
import sys

# --------------------------------------------------------------------
# 1) ERLANG C
# --------------------------------------------------------------------

def erlang_b(n: int, a: float) -> float:
    """Erlang B — yinelemeli, taşma yok.

    B(0,A)=1 ·  B(n,A) = A·B(n-1,A) / (n + A·B(n-1,A))
    """
    b = 1.0
    for i in range(1, n + 1):
        b = (a * b) / (i + a * b)
    return b


def erlang_c(n: int, a: float) -> float:
    """Bir çağrının BEKLEME olasılığı (n kişi, a Erlang yük)."""
    if n <= a:
        return 1.0                       # sistem doymuş: herkes bekler
    b = erlang_b(n, a)
    payda = n - a * (1.0 - b)
    if payda <= 0:
        return 1.0
    return (n * b) / payda


def servis_seviyesi(n: int, a: float, aht_sn: float, hedef_sn: float) -> float:
    """Çağrıların hedef süre içinde karşılanma oranı."""
    if n <= a:
        return 0.0
    c = erlang_c(n, a)
    return 1.0 - c * math.exp(-(n - a) * hedef_sn / aht_sn)


def ortalama_bekleme(n: int, a: float, aht_sn: float) -> float:
    """ASA — ortalama cevaplama süresi (saniye)."""
    if n <= a:
        return float("inf")
    return erlang_c(n, a) * aht_sn / (n - a)


def gerekli_kisi(hacim_saatlik: float, aht_sn: float,
                 hedef_yuzde: float = 0.80, hedef_sn: float = 20.0,
                 azami_doluluk: float = 0.90, tavan: int = 500) -> dict:
    """Bu saatte kaç kişi gerekir?

    hacim_saatlik : saatteki işlem adedi
    aht_sn        : ortalama işlem süresi (saniye)
    hedef_yuzde   : ör. 0.80  →  çağrıların %80'i
    hedef_sn      : ör. 20    →  20 saniye içinde
    azami_doluluk : kişi başı meşguliyet tavanı (tükenmişlik koruması)
    """
    a = (hacim_saatlik * aht_sn) / 3600.0        # Erlang cinsinden yük
    if a <= 0:
        return {"kisi": 0, "yuk_erlang": 0.0, "servis": 1.0,
                "asa_sn": 0.0, "doluluk": 0.0}
    n = max(1, math.ceil(a))
    while n < tavan:
        sl = servis_seviyesi(n, a, aht_sn, hedef_sn)
        dol = a / n
        if sl >= hedef_yuzde and dol <= azami_doluluk:
            break
        n += 1
    return {"kisi": n, "yuk_erlang": round(a, 2),
            "servis": round(servis_seviyesi(n, a, aht_sn, hedef_sn), 4),
            "asa_sn": round(ortalama_bekleme(n, a, aht_sn), 1),
            "doluluk": round(a / n, 3)}


# --------------------------------------------------------------------
# 2) ORAN MODELİ
# --------------------------------------------------------------------

def oran_kisi(surucu: float, birim_basina: float, taban: int = 0) -> int:
    """Sürücü metriğinden kişi sayısı.

    birim_basina : bir sürücü birimi başına personel
                   (15 oda başına 1 kişi  →  1/15 = 0.0667)
    taban        : sürücü sıfır olsa bile bulunması gereken asgari kişi
                   (resepsiyon boş otelde bile kapanmaz)
    """
    return max(taban, math.ceil(surucu * birim_basina))


def oran_kalibre(gozlemler):
    """Geçmiş veriden birim_basina oranını tahmin et.

    gozlemler: [(surucu_degeri, o_saatte_calisan_kisi), ...]
    Müşteri "15 oda başına 1 kişi" diyemiyorsa oran geçmişten öğrenilir.
    En küçük kareler, sabitsiz doğru: kisi = k · surucu
    """
    pay = sum(s * k for s, k in gozlemler if s > 0)
    payda = sum(s * s for s, k in gozlemler if s > 0)
    if payda == 0:
        return None
    return pay / payda


# --------------------------------------------------------------------
# 3) YÜK → TALEP
# --------------------------------------------------------------------

def talep_uret(yuk, modeller, hedef_carpani: float = 1.0,
               asgari_orani: float = 0.72):
    """Yük kayıtlarını motorun beklediği talep listesine çevir.

    yuk      : [{"ekip","gun","saat","hacim"|"surucu"}]
    modeller : {"<ekip>": {...}}   ekip bazında model tanımı
    """
    out = []
    for y in yuk:
        mdl = modeller.get(y["ekip"])
        if not mdl:
            continue
        if mdl["tip"] == "ERLANG":
            r = gerekli_kisi(
                y.get("hacim", 0), mdl["aht_sn"],
                mdl.get("hedef_yuzde", 0.80), mdl.get("hedef_sn", 20.0),
                mdl.get("azami_doluluk", 0.90))
            kisi = r["kisi"]
            ek = {"yuk_erlang": r["yuk_erlang"], "servis": r["servis"]}
        else:
            kisi = oran_kisi(y.get("surucu", 0), mdl["birim_basina"],
                             mdl.get("taban", 0))
            ek = {"surucu": y.get("surucu", 0)}

        # KAPANMA PAYI (shrinkage): mola, eğitim, devamsızlık.
        # Erlang "aynı anda kaç kişi telefonda olmalı" der; çizelgeye
        # yazılacak kişi sayısı bundan FAZLADIR.
        kayip = mdl.get("kapanma_payi", 0.0)
        if kayip > 0:
            kisi = math.ceil(kisi / (1.0 - kayip))

        hedef = max(1, math.ceil(kisi * hedef_carpani))
        out.append({"ekip": y["ekip"], "gun": y["gun"], "saat": y["saat"],
                    "asgari": max(1, round(hedef * asgari_orani)),
                    "hedef": hedef, **ek})
    return out


# --------------------------------------------------------------------
# 4) BAĞIMSIZ DOĞRULAMA — kuyruk benzetimi
# --------------------------------------------------------------------

def benzetim(hacim_saatlik: float, aht_sn: float, kisi: int,
             hedef_sn: float, sure_saat: float = 400.0, tohum: int = 7):
    """M/M/N kuyruğunu olay bazlı benzet ve servis seviyesini ÖLÇ.

    Erlang C formülünü doğrulamak için kullanılır. Formülle ortak hiçbir
    kod paylaşmaz — planlayıcı/değerlendirici ayrımının aynısı.
    """
    rnd = random.Random(tohum)
    lam = hacim_saatlik / 3600.0                 # çağrı/saniye
    mu = 1.0 / aht_sn
    if kisi <= 0:
        return 0.0

    musait = [0.0] * kisi                        # her kişinin boşalma anı
    t = 0.0
    son = sure_saat * 3600.0
    toplam = hedef_icinde = 0

    while t < son:
        t += rnd.expovariate(lam)
        if t >= son:
            break
        i = min(range(kisi), key=lambda j: musait[j])
        basla = max(t, musait[i])
        bekleme = basla - t
        musait[i] = basla + rnd.expovariate(mu)
        toplam += 1
        if bekleme <= hedef_sn:
            hedef_icinde += 1
    return hedef_icinde / max(1, toplam)


# --------------------------------------------------------------------
# TESTLER
# --------------------------------------------------------------------

def test_erlang():
    print("=" * 72)
    print("1) ERLANG C — FORMÜL, BAĞIMSIZ BENZETİMLE DOĞRULANIYOR")
    print("=" * 72)
    print("  Formül 'şu kadar kişiyle %80/20 tutar' diyor. Benzetim aynı yükte")
    print("  gerçekten tutuyor mu diye ölçüyor. İkisi tutmuyorsa formül yanlış")
    print("  kodlanmıştır — sistem kusursuz çalışıp yanlış kadro söyler.\n")
    print(f"  {'çağrı/sa':>9}{'AHT sn':>8}{'kişi':>6}{'formül SL':>11}"
          f"{'benzetim SL':>13}{'fark':>8}")
    print("  " + "-" * 56)

    senaryolar = [(30, 180), (60, 240), (120, 300), (200, 200), (400, 150)]
    en_buyuk_fark = 0.0
    for hacim, aht in senaryolar:
        r = gerekli_kisi(hacim, aht, 0.80, 20.0)
        sim = benzetim(hacim, aht, r["kisi"], 20.0, sure_saat=600.0)
        fark = abs(sim - r["servis"])
        en_buyuk_fark = max(en_buyuk_fark, fark)
        print(f"  {hacim:>9}{aht:>8}{r['kisi']:>6}{r['servis']:>11.3f}"
              f"{sim:>13.3f}{fark:>8.3f}")

    print(f"\n  En büyük sapma: {en_buyuk_fark:.3f}")
    ok = en_buyuk_fark < 0.05
    print("  ✓ Formül benzetimle tutuyor (sapma < 0.05)." if ok
          else "  ✗ Formül ile benzetim ayrışıyor — Erlang kodlaması şüpheli.")

    # tutarlılık kontrolleri
    print("\n  Tutarlılık kontrolleri:")
    a = (120 * 300) / 3600.0
    sl = [servis_seviyesi(n, a, 300, 20) for n in range(math.ceil(a) + 1,
                                                        math.ceil(a) + 12)]
    artan = all(sl[i] <= sl[i + 1] + 1e-9 for i in range(len(sl) - 1))
    print(f"    kişi arttıkça servis seviyesi artıyor : {'✓' if artan else '✗'}")
    r1 = gerekli_kisi(120, 300, 0.80, 20.0)
    r2 = gerekli_kisi(120, 300, 0.95, 20.0)
    print(f"    daha yüksek hedef daha çok kişi ister : "
          f"{'✓' if r2['kisi'] >= r1['kisi'] else '✗'}"
          f"   (%80→{r1['kisi']} kişi, %95→{r2['kisi']} kişi)")
    r3 = gerekli_kisi(120, 600, 0.80, 20.0)
    print(f"    işlem süresi 2× → kişi ~2×            : "
          f"{'✓' if r3['kisi'] > r1['kisi'] else '✗'}"
          f"   ({r1['kisi']} → {r3['kisi']})")
    print(f"    kişi sayısı yükün altına düşmüyor     : "
          f"{'✓' if r1['kisi'] > r1['yuk_erlang'] else '✗'}"
          f"   (yük {r1['yuk_erlang']} Erlang, {r1['kisi']} kişi)")
    return ok and artan


def test_oran():
    print("\n" + "=" * 72)
    print("2) ORAN MODELİ — geçmişten kalibrasyon")
    print("=" * 72)
    print("  Müşteri '15 oda başına 1 kişi' diyemiyorsa oran geçmiş veriden")
    print("  öğrenilir. Bilinen bir oranla veri üretip geri bulabiliyor muyuz?\n")

    gercek = 1 / 15
    rnd = random.Random(11)
    gozlem = []
    for _ in range(200):
        oda = rnd.randint(40, 240)
        kisi = max(1, round(oda * gercek + rnd.gauss(0, 0.8)))   # gürültülü
        gozlem.append((oda, kisi))
    tahmin = oran_kalibre(gozlem)
    hata = abs(tahmin - gercek) / gercek
    print(f"    gerçek oran   : {gercek:.4f}  (15 oda başına 1 kişi)")
    print(f"    tahmin edilen : {tahmin:.4f}  ({1/tahmin:.1f} oda başına 1 kişi)")
    print(f"    hata          : %{100*hata:.1f}")
    ok = hata < 0.05
    print("    ✓ Oran geçmiş veriden geri bulunuyor." if ok
          else "    ✗ Kalibrasyon sapıyor.")
    print(f"\n    180 dolu oda → {oran_kisi(180, tahmin)} kat görevlisi")
    print(f"      0 dolu oda → {oran_kisi(0, tahmin, taban=1)} kişi "
          f"(taban=1: resepsiyon boş otelde de kapanmaz)")
    return ok


def test_kapanma_payi():
    print("\n" + "=" * 72)
    print("3) KAPANMA PAYI — en sık yapılan hata")
    print("=" * 72)
    print("  Erlang 'aynı anda kaç kişi TELEFONDA olmalı' der. Çizelgeye")
    print("  yazılacak kişi bundan fazladır: mola, eğitim, devamsızlık.")
    print("  Bu payı unutmak, kadroyu sistematik olarak eksik hesaplar.\n")
    mdl_yok = {"T": {"tip": "ERLANG", "aht_sn": 240}}
    mdl_var = {"T": {"tip": "ERLANG", "aht_sn": 240, "kapanma_payi": 0.30}}
    yuk = [{"ekip": "T", "gun": 0, "saat": 10, "hacim": 120}]
    a = talep_uret(yuk, mdl_yok)[0]
    b = talep_uret(yuk, mdl_var)[0]
    print(f"    kapanma payı yok  : {a['hedef']} kişi")
    print(f"    kapanma payı %30  : {b['hedef']} kişi  "
          f"(+%{100*(b['hedef']/a['hedef']-1):.0f})")
    print("\n    Bu fark 300 kişilik bir operasyonda haftada onlarca kişi-saat")
    print("    eder. Payın değeri müşteriye özgüdür ve ölçülmelidir.")
    return b["hedef"] > a["hedef"]


def demo():
    print("\n" + "=" * 72)
    print("4) UÇTAN UCA — bir otelin bir günü")
    print("=" * 72)
    modeller = {
        "REZERVASYON": {"tip": "ERLANG", "aht_sn": 210, "hedef_yuzde": 0.80,
                        "hedef_sn": 20, "kapanma_payi": 0.25},
        "KAT": {"tip": "ORAN", "birim_basina": 1 / 15, "kapanma_payi": 0.15},
        "ON_BURO": {"tip": "ORAN", "birim_basina": 1 / 60, "taban": 2,
                    "kapanma_payi": 0.20},
    }
    # cumartesi: sabah check-out, akşam check-in
    cagri = {8: 55, 9: 80, 10: 95, 11: 70, 12: 45, 13: 40,
             14: 60, 15: 85, 16: 100, 17: 90, 18: 65, 19: 40}
    oda = {8: 190, 9: 190, 10: 185, 11: 160, 12: 120, 13: 90,
           14: 110, 15: 150, 16: 180, 17: 195, 18: 200, 19: 200}

    yuk = []
    for s, v in cagri.items():
        yuk.append({"ekip": "REZERVASYON", "gun": 5, "saat": s, "hacim": v})
    for s, v in oda.items():
        yuk.append({"ekip": "KAT", "gun": 5, "saat": s, "surucu": v})
        yuk.append({"ekip": "ON_BURO", "gun": 5, "saat": s, "surucu": v})

    talep = talep_uret(yuk, modeller)
    print(f"  {'saat':>5}{'çağrı':>7}{'REZ':>6}{'servis':>9}"
          f"{'oda':>6}{'KAT':>6}{'ÖN BÜRO':>9}")
    print("  " + "-" * 48)
    ix = {(t["ekip"], t["saat"]): t for t in talep}
    for s in sorted(cagri):
        r = ix[("REZERVASYON", s)]
        print(f"  {s:>4}:00{cagri[s]:>7}{r['hedef']:>6}{r['servis']:>9.2f}"
              f"{oda[s]:>6}{ix[('KAT', s)]['hedef']:>6}"
              f"{ix[('ON_BURO', s)]['hedef']:>9}")
    print(f"\n  Toplam gün: {sum(t['hedef'] for t in talep)} kişi-saat")
    print("  Bu tablo artık motorun `talep` girdisidir — elle yazılmış bir")
    print("  sayı değil, firmanın verdiği yükten hesaplanmış bir ihtiyaç.")


def main():
    if "--demo" in sys.argv:
        demo()
        return 0
    ok1 = test_erlang()
    ok2 = test_oran()
    ok3 = test_kapanma_payi()
    demo()
    print("\n" + "=" * 72)
    print(f"SONUÇ: {'hepsi geçti' if all((ok1, ok2, ok3)) else 'BAŞARISIZ test var'}")
    print("=" * 72)
    return 0 if all((ok1, ok2, ok3)) else 1


if __name__ == "__main__":
    sys.exit(main())
