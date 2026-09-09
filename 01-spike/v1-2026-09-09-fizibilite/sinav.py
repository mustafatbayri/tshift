#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sinav.py — spike'ın iki kritik testi.

1) SABOTAJ TESTİ
   Geçerli bir planı bilerek bozarız. Değerlendirici her bozmayı DOĞRU kural
   koduyla yakalamalıdır. Yakalayamazsa "0 ihlal" sonucu hiçbir şey ifade etmez.
   Bu test, değerlendiricinin gerçekten çalıştığının kanıtıdır.

2) ÇÖZÜMSÜZLÜK TEŞHİSİ
   Kısıtları bilerek çelişkili hale getiririz. Sistem sessizce kötü bir plan
   üretmemeli; "yapılamaz" demeli ve HANGİ KURALIN bağladığını söylemelidir.
   Teşhis yöntemi: her sert kuralı tek tek gevşetip yeniden planla; açığı
   kapatan kural, bağlayan kuraldır.

Çalıştırma:  python3 sinav.py       (önce uret.py, sonra planla.py çalışmalı)
"""

import copy
import json
import sys

from degerlendirici import Degerlendirici, sf, hucre
from planla import Planlayici, metrikler

GIRDI = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"


def onek(yol):
    import os
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


# --------------------------------------------------------------------
# 1) SABOTAJ TESTİ
# --------------------------------------------------------------------

def sabotajlar(girdi, plan):
    """Her biri (ad, beklenen_kod, plan_bozan_fonksiyon)."""

    cal = {c["id"]: c for c in girdi["calisanlar"]}

    def ilk(A, kosul):
        for a in A:
            if kosul(a):
                return a
        return None

    def s_gunluk_azami(p):
        a = ilk(p["atamalar"], lambda a: True)
        a["bit"] = "23:59"
        a["bas"] = "07:00"
        return "9 saatlik sınırı aşan 16:59'luk vardiya"

    def s_dinlenme(p):
        A = p["atamalar"]
        a = ilk(A, lambda a: a["gun"] == 0 and sf(a["bit"]) >= 22)
        b = ilk(A, lambda x: x["gun"] == 1 and sf(x["bas"]) <= 9
                and x["calisan"] != a["calisan"])
        b["calisan"] = a["calisan"]          # aynı kişi: 22:00 → ertesi 07:00
        return "22:00 bitişten sonra ertesi sabah erken vardiya (< 11 saat)"

    def s_cakisma(p):
        A = p["atamalar"]
        a = ilk(A, lambda a: a["gun"] == 2)
        b = ilk(A, lambda x: x["gun"] == 2 and x["calisan"] != a["calisan"]
                and sf(x["bas"]) < sf(a["bit"]) and sf(x["bit"]) > sf(a["bas"]))
        b["calisan"] = a["calisan"]
        return "aynı kişiye aynı gün çakışan iki vardiya"

    def s_izin(p):
        for c in girdi["calisanlar"]:
            for iz in c.get("izinler", []):
                a = ilk(p["atamalar"],
                        lambda a, g=iz["gun"], e=c["ekip"]: a["gun"] == g and a["ekip"] == e)
                if a:
                    a["calisan"] = c["id"]
                    return f"izinli çalışan ({c['id']}) izin gününe (gün {iz['gun']}) atandı"
        return None

    def s_uygunluk(p):
        for c in girdi["calisanlar"]:
            for u in c.get("uygunluk", []):
                if u["tip"] != "UYGUN_DEGIL":
                    continue
                ub, ut = sf(u["bas"]), sf(u["bit"])
                a = ilk(p["atamalar"],
                        lambda a, g=u["gun"], e=c["ekip"]: a["gun"] == g and a["ekip"] == e
                        and sf(a["bas"]) < ut and sf(a["bit"]) > ub)
                if a:
                    a["calisan"] = c["id"]
                    return (f"{c['id']} gün {u['gun']} {u['bas']}–{u['bit']} arası "
                            f"uygun değilken o aralığa atandı")
        return None

    def s_asgari_kapsama(p):
        """Asgarinin ALTINA düşene kadar sil.

        Sabit sayıda (4) silmek veri setine bağımlıydı: otelde kadro daha
        kalabalık olduğu için 4 kişi eksilince asgari hâlâ sağlanıyordu ve
        test sahte biçimde 'kaldı' veriyordu. Artık gereken sayı hesaplanır.
        """
        t = max(girdi["talep"], key=lambda t: t["asgari"])
        hedef_hucre = (t["ekip"], t["gun"], t["saat"])
        kapsayan = [a for a in p["atamalar"]
                    if a["ekip"] == t["ekip"]
                    and any(hucre(a["gun"], h) == (t["gun"], t["saat"])
                            for h in range(int(sf(a["bas"])), int(sf(a["bit"]))))]
        gerek = len(kapsayan) - t["asgari"] + 1
        n = 0
        for a in kapsayan[:max(1, gerek)]:
            p["atamalar"].remove(a)
            n += 1
        return (f"{hedef_hucre} hücresinden {n} kişi silindi "
                f"(asgari {t['asgari']}, kalan {len(kapsayan)-n})")

    def s_rol(p):
        for a in p["atamalar"]:
            c = cal.get(a["calisan"])
            if c and "TAKIM_LIDERI" in c["roller"]:
                a["calisan"] = next(x["id"] for x in girdi["calisanlar"]
                                    if x["ekip"] == a["ekip"]
                                    and "TAKIM_LIDERI" not in x["roller"])
        return "tüm takım liderleri plandan çıkarıldı"

    def s_mola_hakki(p):
        a = ilk(p["atamalar"], lambda a: sf(a["bit"]) - sf(a["bas"]) >= 8)
        a["mola_dk"] = 15
        return "8 saatlik vardiyaya 15 dk mola (bant 60 dk gerektirir)"

    def s_gece_azami(p):
        """Gece penceresine 7,5 saatten fazla düşen bir vardiya üret."""
        if not any(k["kod"] == "GECE_VARDIYASI_AZAMI" for k in girdi["kurallar"]):
            return None
        a = ilk(p["atamalar"], lambda a: sf(a["bit"]) > 24)
        if a is None:
            return None
        a["bas"] = "21:00"; a["bit"] = "30:00"; a["mola_dk"] = 60
        a["mola_saat"] = "22:00"      # mola gece penceresinde ama yetmez
        return "21:00–06:00 vardiya: gece penceresinde 8 saat (sınır 7,5)"

    def s_ardisik_gece(p):
        """Aynı kişiye limitten fazla ardışık gece ver."""
        kural = next((k for k in girdi["kurallar"]
                      if k["kod"] == "ARDISIK_GECE_LIMIT"), None)
        if not kural:
            return None
        lim = kural["param"]["ardisik"]
        geceler = [a for a in p["atamalar"] if sf(a["bit"]) > 24]
        if len(geceler) < lim + 1:
            return None
        gun_bazinda = {}
        for a in geceler:
            gun_bazinda.setdefault(a["gun"], []).append(a)
        gunler = sorted(gun_bazinda)[:lim + 1]
        if len(gunler) < lim + 1 or gunler != list(range(gunler[0], gunler[0] + lim + 1)):
            return None
        cid = gun_bazinda[gunler[0]][0]["calisan"]
        for g in gunler:
            gun_bazinda[g][0]["calisan"] = cid
        return f"{cid} kişisine {lim + 1} ardışık gece (sınır {lim})"

    def s_yetkinlik(p):
        """Gerekli yetkinliğe sahip herkesi plandan çıkar."""
        kural = next((k for k in girdi["kurallar"]
                      if k["kod"] == "YETKINLIK_KAPSAMASI"), None)
        if not kural or not kural["param"].get("gereksinimler"):
            return None
        g = kural["param"]["gereksinimler"][0]
        yedek = next((x for x in girdi["calisanlar"]
                      if x["ekip"] == g["ekip"] and x["durum"] == "AKTIF"
                      and g["yetkinlik"] not in (x.get("yetkinlikler") or [])), None)
        if not yedek:
            return None
        n = 0
        for a in p["atamalar"]:
            c = cal.get(a["calisan"])
            if (a["ekip"] == g["ekip"] and c
                    and g["yetkinlik"] in (c.get("yetkinlikler") or [])):
                a["calisan"] = yedek["id"]
                n += 1
        return (f"{g['ekip']} ekibinde {g['yetkinlik']} yetkinliği olan "
                f"{n} atama, yetkinliği olmayan biriyle değiştirildi")

    def s_haftalik_azami(p):
        cid = p["atamalar"][0]["calisan"]
        n = 0
        for a in p["atamalar"]:
            if a["gun"] != p["atamalar"][0]["gun"] and n < 6:
                a["calisan"] = cid
                n += 1
        return f"tek kişiye 7 güne yayılmış {n+1} vardiya"

    return [
        ("Günlük azami aşımı",      "GUNLUK_AZAMI",           s_gunluk_azami),
        ("Vardiya arası dinlenme",  "VARDIYA_ARASI_DINLENME", s_dinlenme),
        ("Çakışan vardiya",         "CAKISMA_YOK",            s_cakisma),
        ("İzinli güne atama",       "ONAYLI_IZIN",            s_izin),
        ("Uygunluk dışı gün",       "UYGUNLUK_TAKVIMI",       s_uygunluk),
        ("Asgari kapsama açığı",    "ASGARI_KAPSAMA",         s_asgari_kapsama),
        ("Lider yok",               "ROL_KAPSAMASI",          s_rol),
        ("Mola hakkı eksik",        "MOLA_HAKKI",             s_mola_hakki),
        ("Gece azami aşımı",        "GECE_VARDIYASI_AZAMI",   s_gece_azami),
        ("Ardışık gece aşımı",      "ARDISIK_GECE_LIMIT",     s_ardisik_gece),
        ("Yetkinlik sahada yok",    "YETKINLIK_KAPSAMASI",    s_yetkinlik),
        ("Haftalık azami / tatil",  None,                     s_haftalik_azami),
    ]


def sabotaj_testi(girdi, temiz_plan):
    d = Degerlendirici(girdi)
    baz = [i for i in d.calistir(temiz_plan) if i.tur == "SERT"]
    print("=" * 66)
    print("1) SABOTAJ TESTİ — değerlendirici gerçekten yakalıyor mu?")
    print("=" * 66)
    if baz:
        kod = {}
        for i in baz:
            kod[i.kod] = kod.get(i.kod, 0) + 1
        print(f"  Referans plandaki sert ihlal: {len(baz)}  {kod}")
        print("  (Bunlar her sabotaj sonucunda da görünür — sabotajın kendi")
        print("   ürettiği ihlalle karıştırmayın; test beklenen KODU arar.)\n")
    else:
        print("  Referans plan temiz: 0 sert ihlal\n")

    gecti = basarisiz = 0
    for ad, kod, fn in sabotajlar(girdi, temiz_plan):
        p = copy.deepcopy(temiz_plan)
        aciklama = fn(p)
        if aciklama is None:
            print(f"  [ATLANDI] {ad}: veri setinde uygun örnek yok")
            continue
        ihl = [i for i in Degerlendirici(girdi).calistir(p) if i.tur == "SERT"]
        kodlar = {}
        for i in ihl:
            kodlar[i.kod] = kodlar.get(i.kod, 0) + 1
        if kod is None:
            ok = len(ihl) > 0
            beklenen = "herhangi bir sert ihlal"
        else:
            ok = kodlar.get(kod, 0) > 0
            beklenen = kod
        gecti += ok
        basarisiz += (not ok)
        isaret = "GEÇTİ " if ok else "KALDI "
        print(f"  [{isaret}] {ad}")
        print(f"           bozma   : {aciklama}")
        print(f"           beklenen: {beklenen}")
        print(f"           bulunan : {', '.join(f'{k}×{v}' for k, v in sorted(kodlar.items(), key=lambda x:-x[1])[:4]) or '—'}")
    print(f"\n  SONUÇ: {gecti} geçti, {basarisiz} kaldı\n")
    return basarisiz == 0


# --------------------------------------------------------------------
# 2) ÇÖZÜMSÜZLÜK TEŞHİSİ
# --------------------------------------------------------------------

GEVSETILEBILIR = [
    ("GUNLUK_AZAMI",           lambda k: k["param"].update(saat=24)),
    ("HAFTALIK_AZAMI",         lambda k: k["param"].update(saat=168)),
    ("VARDIYA_ARASI_DINLENME", lambda k: k["param"].update(saat=0)),
    ("HAFTA_TATILI",           lambda k: k["param"].update(saat=0)),
    ("PART_TIME_LIMIT",        None),
    ("UYGUNLUK_TAKVIMI",       None),
    ("ONAYLI_IZIN",            None),
    ("ROL_KAPSAMASI",          lambda k: k["param"].update(asgari=0)),
]


def acik_olc(girdi, profil="KAPSAMA"):
    """Planla ve karşılanamayan asgari kişi-saati döndür."""
    w = dict(girdi["hedef_profilleri"][profil])
    w.setdefault("kararlilik", w.pop("tercih", 5))
    p = Planlayici(girdi, profil, w)
    plan = p.calistir()
    d = Degerlendirici(girdi)
    m = metrikler(girdi, plan, d)
    ihl = d.calistir(plan)
    sert = sum(1 for i in ihl if i.tur == "SERT")
    var = {}
    for a in plan["atamalar"]:
        for s in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            if a.get("mola_saat") and int(sf(a["mola_saat"])) == s:
                continue
            k = (a["ekip"], a["gun"], s)
            var[k] = var.get(k, 0) + 1
    acik = sum(max(0, t["asgari"] - var.get((t["ekip"], t["gun"], t["saat"]), 0))
               for t in girdi["talep"])
    return acik, sert, m


def gevset(girdi, kod):
    g = copy.deepcopy(girdi)
    for k in g["kurallar"]:
        if k["kod"] == kod:
            fn = dict((a, b) for a, b in GEVSETILEBILIR)[kod]
            if fn:
                fn(k)
            else:
                k["tur"] = "KAPALI"
    return g


def cozumsuzluk_testi(girdi):
    print("=" * 66)
    print("2) ÇÖZÜMSÜZLÜK TEŞHİSİ — 'yapılamaz' diyebiliyor mu, sebebini söylüyor mu?")
    print("=" * 66)

    # Kısıtı bilerek imkânsız hale getir: günlük azami 9 → 5 saat.
    # 5 saatlik vardiya şablonu az; talep aynı → asgari kapsama tutmaz.
    zor = copy.deepcopy(girdi)
    for k in zor["kurallar"]:
        if k["kod"] == "GUNLUK_AZAMI":
            k["param"]["saat"] = 5
        if k["kod"] == "HAFTALIK_AZAMI":
            k["param"]["saat"] = 25

    acik0, sert0, m0 = acik_olc(zor)
    print(f"\n  Senaryo: GUNLUK_AZAMI 9→5 sa, HAFTALIK_AZAMI 45→25 sa (talep sabit)")
    print(f"  Sonuç  : asgari karşılama %{100*m0['asgari_karsilama']:.1f}, "
          f"kapatılamayan {acik0} kişi-saat")
    if acik0 == 0:
        print("  → Plan yine de yapılabildi; bu senaryo çözümsüz değil.\n")
        return True
    print(f"  → PLAN YAPILAMAZ. Şimdi hangi kuralın bağladığını arıyoruz:\n")

    satir = []
    for kod, _ in GEVSETILEBILIR:
        if kod not in {k["kod"] for k in zor["kurallar"]}:
            continue
        a, s, m = acik_olc(gevset(zor, kod))
        kazanc = acik0 - a
        satir.append((kazanc, kod, a))
    satir.sort(reverse=True)

    print(f"  {'gevşetilen kural':26} {'kalan açık':>11} {'kapanan':>9}")
    print("  " + "-" * 48)
    for kazanc, kod, a in satir:
        isaret = "  ← BAĞLAYAN" if kazanc > 0 else ""
        print(f"  {kod:26} {a:>11} {kazanc:>9}{isaret}")

    baglayan = [k for kz, k, _ in satir if kz > 0]
    print()
    if baglayan:
        print(f"  TEŞHİS: açığı kapatan kural(lar) → {', '.join(baglayan)}")
        print(f"  Ürün dilinde: \"Bu hafta planlanamıyor. Sebep: {baglayan[0]}. "
              f"Bu kuralı gevşetirseniz {satir[0][0]} kişi-saatlik açık kapanır.\"")
    else:
        print("  TEŞHİS: tek bir kuralı gevşetmek yetmiyor — açık KAPASİTE kaynaklı.")
        print("  Ürün dilinde: \"Bu hafta planlanamıyor. Tek bir kural sebep değil; "
              "mevcut kadro talebi karşılamıyor.\"")
    print()
    return True


# --------------------------------------------------------------------

def main():
    girdi = json.load(open(GIRDI, encoding="utf-8"))
    try:
        plan = json.load(open(f"plan_{onek(GIRDI)}DENGELI.json", encoding="utf-8"))
    except FileNotFoundError:
        print(f"Önce planla.py {GIRDI} çalıştırın.")
        return 1
    ok1 = sabotaj_testi(girdi, plan)
    ok2 = cozumsuzluk_testi(girdi)
    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(main())
