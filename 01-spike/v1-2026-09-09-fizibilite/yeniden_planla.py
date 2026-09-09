#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yeniden_planla.py — PLAN KARARLILIĞI TESTİ

SORU
Müdür yayınlanmış planı açıyor, cumadan iki kişiyi çıkarıyor, cumartesiden
birini çıkarıyor, cumadaki birini cumartesiye kaydırıyor ve onaylıyor.
Sonra sistem eldeki verilerle planı yeniden üretiyor.

RİSK
Çözücü serbest bırakılırsa bambaşka bir optimum bulur ve çizelgenin TAMAMINI
yeniden dizer. Müdür bir kişiyi oynatır, dört yüz vardiya değişir. Ertesi gün
personel kendi vardiyasını tanıyamaz. Hiçbir işletme bunu kabul etmez — ürünü
teknik değil, güven açısından bitiren şey budur.

ÖLÇÜLEN
  1. Müdürün düzenlemeleri plana AYNEN yansıdı mı  (KILIT_UYUMU, sert kural)
  2. Yeni plan hâlâ geçerli mi                      (sert ihlal)
  3. DEĞİŞİM ORANI: gereksiz yere kaç atama değişti (churn)
     - naif yeniden plan  : kararlılık ödülü yok
     - kararlı yeniden plan: referans plandaki atamalar ödüllendirilir
  4. Düzenleme çözümsüzlük yaratırsa sistem sebebini söylüyor mu

Kullanım:
    py yeniden_planla.py                    # çağrı merkezi
    py yeniden_planla.py girdi_otel.json    # otel
"""

import copy
import json
import os
import sys

from degerlendirici import Degerlendirici
from planla import Planlayici, metrikler


def onek(yol):
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


# --------------------------------------------------------------------
# Müdürün düzenlemeleri
# --------------------------------------------------------------------

def duzenleme_uret(plan, gun_cikar=(4, 4, 5), tasi_gun=(4, 5)):
    """Gerçekçi bir müdür müdahalesi üret.

    Varsayılan: cumadan (gün 4) iki kişi çıkar, cumartesiden (gün 5) bir kişi
    çıkar, cumadaki bir kişiyi cumartesiye kaydır. Kullanıcının tarif ettiği
    senaryonun birebir karşılığı.
    """
    A = plan["atamalar"]
    duz = []
    kullanilan = set()

    for g in gun_cikar:
        for a in A:
            if a["gun"] == g and a["calisan"] not in kullanilan:
                duz.append({"tip": "CIKAR", "calisan": a["calisan"], "gun": g})
                kullanilan.add(a["calisan"])
                break

    kaynak, hedef = tasi_gun
    for a in A:
        if a["gun"] == kaynak and a["calisan"] not in kullanilan:
            # aynı ekipte, hedef günde kullanılabilecek bir şablon seç
            duz.append({"tip": "TASI", "calisan": a["calisan"], "gun": kaynak,
                        "yeni_gun": hedef, "sablon": a["sablon"]})
            kullanilan.add(a["calisan"])
            break
    return duz


def duzenleme_uygula(girdi, plan, duzenlemeler, kararlilik_odulu=0):
    """Düzenlemeleri motorun anlayacağı kısıtlara çevir.

    kilitler  : bu atama planda MUTLAKA olacak
    yasaklar  : bu kişi o gün ÇALIŞMAYACAK
    referans  : "az değiştir" ödülü için önceki plan
    """
    g = copy.deepcopy(girdi)
    kilit, yasak = [], []

    for d in duzenlemeler:
        if d["tip"] == "CIKAR":
            yasak.append({"calisan": d["calisan"], "gun": d["gun"]})
        elif d["tip"] == "TASI":
            yasak.append({"calisan": d["calisan"], "gun": d["gun"]})
            kilit.append({"calisan": d["calisan"], "gun": d["yeni_gun"],
                          "sablon": d["sablon"]})
        elif d["tip"] == "KILIT":
            kilit.append({"calisan": d["calisan"], "gun": d["gun"],
                          "sablon": d["sablon"]})

    g["kilitler"] = kilit
    g["yasaklar"] = yasak
    g["referans_atamalar"] = [
        {"calisan": a["calisan"], "gun": a["gun"], "sablon": a["sablon"]}
        for a in plan["atamalar"]
    ]
    g["kararlilik_odulu"] = kararlilik_odulu
    return g


def degisim(p0, p1):
    """İki plan arasındaki atama farkı (churn)."""
    a = {(x["calisan"], x["gun"], x["sablon"]) for x in p0["atamalar"]}
    b = {(x["calisan"], x["gun"], x["sablon"]) for x in p1["atamalar"]}
    return {
        "kaldirilan": len(a - b),
        "eklenen": len(b - a),
        "korunan": len(a & b),
        "oran": len(a ^ b) / max(1, len(a | b)),
        "etkilenen_kisi": len({k[0] for k in (a ^ b)}),
    }


def cpsat_var():
    try:
        import importlib
        importlib.import_module("ortools.sat.python.cp_model")
        return True
    except ImportError:
        return False


def plan_uret_cpsat(girdi, sure=180.0, profil="DENGELI"):
    """CP-SAT ile yeniden plan. Asgari kapsama SERT kısıttır: çözücü onu
    ihlal eden bir plan ÜRETEMEZ. Müdürün düzenlemesi kapsamayı imkânsız
    kılıyorsa sonuç INFEASIBLE olur — ürün için doğru davranış budur:
    'bu düzenleme uygulanamaz' demek, sessizce açık bırakmaktan iyidir.
    """
    from ortools.sat.python import cp_model
    import cpsat
    v = cpsat.Veri(girdi)
    m, dv = cpsat.kur_model(v, profil, cp_model)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = sure
    solver.parameters.num_search_workers = 8
    st = solver.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, solver.StatusName(st)
    return cpsat.plan_cikar(v, dv, solver, profil), solver.StatusName(st)


def plan_uret(girdi, profil="DENGELI"):
    w = dict(girdi["hedef_profilleri"][profil])
    w.setdefault("kararlilik", w.pop("tercih", 5))
    p = Planlayici(girdi, profil, w)
    return p.calistir()


def rapor_satiri(girdi, plan, etiket, p0=None):
    d = Degerlendirici(girdi)
    ihl = d.calistir(plan)
    sert = [i for i in ihl if i.tur == "SERT"]
    kod = {}
    for i in sert:
        kod[i.kod] = kod.get(i.kod, 0) + 1
    m = metrikler(girdi, plan, d)
    print(f"  {etiket}")
    print(f"      sert ihlal      : {len(sert)}  {kod if kod else ''}")
    print(f"      asgari kapsama  : %{100*m['asgari_karsilama']:.1f}")
    print(f"      hedef kapsama   : %{100*m['hedef_karsilama']:.1f}")
    print(f"      atama           : {m['atama']}")
    if p0:
        dg = degisim(p0, plan)
        print(f"      DEĞİŞİM         : %{100*dg['oran']:.1f}  "
              f"({dg['kaldirilan']} kaldırıldı, {dg['eklenen']} eklendi, "
              f"{dg['etkilenen_kisi']} kişi etkilendi)")
        return len(sert), dg
    return len(sert), None


# --------------------------------------------------------------------

def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    p_onek = onek(yol)
    girdi = json.load(open(yol, encoding="utf-8"))

    print("=" * 70)
    print("PLAN KARARLILIĞI TESTİ — müdür düzenledikten sonra ne oluyor?")
    print("=" * 70)
    print(f"  veri seti: {yol}\n")

    # --- 1) İlk plan (yayınlanmış plan) ---
    p0 = plan_uret(girdi)
    print("1) YAYINLANMIŞ PLAN")
    rapor_satiri(girdi, p0, "   ilk plan")

    # --- 2) Müdürün düzenlemeleri ---
    duz = duzenleme_uret(p0)
    print(f"\n2) MÜDÜRÜN DÜZENLEMELERİ ({len(duz)} işlem)")
    for d in duz:
        if d["tip"] == "CIKAR":
            print(f"   • {d['calisan']} → gün {d['gun']}'den ÇIKARILDI")
        elif d["tip"] == "TASI":
            print(f"   • {d['calisan']} → gün {d['gun']}'den gün {d['yeni_gun']}'e "
                  f"TAŞINDI ({d['sablon']})")

    # --- 3) Naif yeniden plan: kararlılık ödülü YOK ---
    print("\n3) NAİF YENİDEN PLAN  (çözücü serbest)")
    g_naif = duzenleme_uygula(girdi, p0, duz, kararlilik_odulu=0)
    p_naif = plan_uret(g_naif)
    s_naif, d_naif = rapor_satiri(g_naif, p_naif, "   sonuç", p0)

    # --- 4) Kararlı yeniden plan: "az değiştir" ödülü VAR ---
    print("\n4) KARARLI YENİDEN PLAN  (az değiştir ödülü açık)")
    g_kar = duzenleme_uygula(girdi, p0, duz, kararlilik_odulu=40)
    p_kar = plan_uret(g_kar)
    s_kar, d_kar = rapor_satiri(g_kar, p_kar, "   sonuç", p0)

    json.dump(p_kar, open(f"plan_{p_onek}YENIDEN.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # --- 5) Karşılaştırma ---
    print("\n" + "=" * 70)
    print("SONUÇ")
    print("=" * 70)
    print(f"  Naif yeniden plan   : %{100*d_naif['oran']:.1f} değişim, "
          f"{d_naif['etkilenen_kisi']} kişi etkilendi")
    print(f"  Kararlı yeniden plan: %{100*d_kar['oran']:.1f} değişim, "
          f"{d_kar['etkilenen_kisi']} kişi etkilendi")
    if d_naif["oran"] > 0:
        kazanc = (d_naif["oran"] - d_kar["oran"]) / d_naif["oran"] * 100
        print(f"  → Kararlılık ödülü gereksiz değişimin %{kazanc:.0f}'ini önledi.")
    print(f"\n  Müdürün düzenlemeleri uygulandı mı: "
          f"{'EVET' if s_kar == 0 else 'HAYIR — KILIT_UYUMU ihlali var'}")

    # --- 6) Çözümsüzlük yaratan düzenleme ---
    # --- 5b) AYNI TEST, GERÇEK MOTORLA (CP-SAT) ---
    if cpsat_var():
        print("\n" + "=" * 70)
        print("AYNI TEST — GERÇEK MOTOR (CP-SAT)")
        print("=" * 70)
        c0, d0 = plan_uret_cpsat(girdi)
        if c0 is None:
            print(f"  İlk plan çözülemedi: {d0}")
        else:
            rapor_satiri(girdi, c0, "   ilk plan (CP-SAT)")
            gc_naif = duzenleme_uygula(girdi, c0, duz, kararlilik_odulu=0)
            gc_kar = duzenleme_uygula(girdi, c0, duz, kararlilik_odulu=600)
            cn, dn = plan_uret_cpsat(gc_naif)
            ck, dk = plan_uret_cpsat(gc_kar)
            print("\n   naif yeniden plan (kararlılık ödülü YOK)")
            if cn is None:
                print(f"      ÇÖZÜM YOK: {dn} — düzenleme uygulanamıyor")
            else:
                rapor_satiri(gc_naif, cn, "   sonuç", c0)
            print("\n   kararlı yeniden plan (ödül açık)")
            if ck is None:
                print(f"      ÇÖZÜM YOK: {dk} — düzenleme uygulanamıyor")
            else:
                rapor_satiri(gc_kar, ck, "   sonuç", c0)
                json.dump(ck, open(f"plan_CPSAT_{p_onek}YENIDEN.json", "w",
                                   encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        print("\n  (OR-Tools kurulu değil — gerçek motorla test atlandı.")
        print("   Asgari kapsama CP-SAT'te SERT kısıttır; greedy'de görülen")
        print("   ASGARI_KAPSAMA açıkları orada yapısal olarak oluşamaz.)")

    print("\n" + "=" * 70)
    print("ÇÖZÜMSÜZ DÜZENLEME — müdür imkânsız bir şey isterse?")
    print("=" * 70)
    kotu = imkansiz_duzenleme(girdi, p0)
    if kotu is None:
        print("  Veri setinde uygun örnek kurulamadı.")
        return 0
    aciklama, duz2 = kotu
    print(f"  Senaryo: {aciklama}")
    g_kotu = duzenleme_uygula(girdi, p0, duz2, kararlilik_odulu=40)
    p_kotu = plan_uret(g_kotu)
    d2 = Degerlendirici(g_kotu)
    ihl2 = [i for i in d2.calistir(p_kotu) if i.tur == "SERT"]
    kod2 = {}
    for i in ihl2:
        kod2[i.kod] = kod2.get(i.kod, 0) + 1
    print(f"  Sonuç  : {len(ihl2)} sert ihlal  {kod2}")
    if kod2:
        print("\n  → Sistem düzenlemeyi sessizce uygulamıyor; hangi kuralın")
        print("    çiğnendiğini kural koduyla söylüyor. Üründe bu, müdüre")
        print("    'bu değişiklik şu kuralı ihlal eder, onaylıyor musunuz?'")
        print("    uyarısı olarak çıkar.")
    else:
        print("  → Bu düzenleme aslında çözümsüz değilmiş; plan geçerli kaldı.")
    print()
    return 0


def imkansiz_duzenleme(girdi, plan):
    """Kural çiğneyen bir müdür düzenlemesi kur.

    En temiz örnek: bir çalışanı, ONAYLI İZİNLİ olduğu güne kilitlemek.
    """
    sab = {s["id"]: s for s in girdi["sablonlar"]}
    for c in girdi["calisanlar"]:
        if c["durum"] != "AKTIF" or not c.get("izinler"):
            continue
        gun = c["izinler"][0]["gun"]
        s = next((x for x in girdi["sablonlar"] if x["ekip"] == c["ekip"]), None)
        if not s:
            continue
        return (f"{c['calisan'] if 'calisan' in c else c['id']} izinli olduğu "
                f"gün {gun}'e elle kilitlendi ({s['id']})",
                [{"tip": "KILIT", "calisan": c["id"], "gun": gun,
                  "sablon": s["id"]}])
    return None


if __name__ == "__main__":
    sys.exit(main())
