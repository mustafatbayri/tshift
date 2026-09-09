#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oneri.py — PLAN EDİTÖRÜ ÖNERİ MOTORU  (yerel onarım)

ÜRÜN AKIŞI
Müdür planı açar, birkaç kişiyi çıkarır/taşır. Sistem çizelgeyi baştan
kurmaz — sadece oluşan boşlukları bulur ve her boşluk için ADAY listesi
sunar. Her adayın yanında sonucu yazar. Kararı müdür verir.

MİMARİ KARARI — ürünün tüm vaadi buna dayanıyor
    Aday listesi iki aşamada üretilir:
      1) ÖN FİLTRE  — ucuz kural kontrolleri, havuzu 300'den ~20'ye indirir
      2) DOĞRULAMA  — hayatta kalanlar, planı denetleyen AYNI bağımsız
         değerlendiriciden geçirilir. Yeni bir sert ihlal doğuruyorsa aday
         listeye GİRMEZ.

    Yani müdüre gösterilen her aday, nihai planı denetleyecek kodla zaten
    doğrulanmıştır. YANLIŞ POZİTİF tanım gereği imkânsızdır — ürünü tek
    olayda bitirecek hata türü buydu.

    Ön filtrenin fazla katı olması YANLIŞ NEGATİF üretir (uygun biri listede
    çıkmaz). Bu öldürücü değil ama ölçülmesi gerekir; alttaki test onu ölçer.

YAPAY ZEKÂNIN YERİ
Aday listesi ve sonuç açıklamalarındaki SAYILAR bu dosyada hesaplanır.
LLM'in işi bu hesaplanmış veriyi cümleye çevirmektir — aday üretmek veya
uygunluk kararı vermek DEĞİL. Bu ayrım bozulursa sistem yalan söyler.

Kullanım:
    py oneri.py                      # çağrı merkezi
    py oneri.py girdi_otel.json      # otel
"""

import copy
import json
import os
import sys
import time

from degerlendirici import Degerlendirici, sf, hucre, gunler_arasi
from planla import Planlayici, MAX_CALISMA_GUNU, DINLENME_SAAT


# --------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------

def onek(yol):
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


def hs(x: float) -> str:
    h, m = int(x), int(round((x - int(x)) * 60))
    return f"{h:02d}:{m:02d}"


class Aday:
    __slots__ = ("calisan", "gun", "sablon", "bas", "bit", "etki", "puan", "zincir")

    def __init__(self, calisan, gun, sablon, bas, bit, zincir=None):
        self.calisan, self.gun, self.sablon = calisan, gun, sablon
        self.bas, self.bit = bas, bit
        self.etki, self.puan, self.zincir = {}, 0.0, zincir

    def dict(self):
        d = {k: getattr(self, k) for k in self.__slots__ if k != "zincir"}
        if self.zincir:
            d["zincir"] = self.zincir
        return d


# --------------------------------------------------------------------

class OneriMotoru:
    def __init__(self, girdi, plan):
        self.g = girdi
        self.plan = plan
        self.d = Degerlendirici(girdi)
        self.cal = {c["id"]: c for c in girdi["calisanlar"]}
        self.aktif = [c for c in girdi["calisanlar"] if c["durum"] == "AKTIF"]

        self.sab = {}
        for s in girdi["sablonlar"]:
            self.sab.setdefault(s["ekip"], []).append({
                "id": s["id"], "bas": sf(s["bas"]), "bit": sf(s["bit"]),
                "mola_dk": s["mola_dk"],
                "net": (sf(s["bit"]) - sf(s["bas"])) - s["mola_dk"] / 60.0,
            })
        self.sab_id = {s["id"]: s for lst in self.sab.values() for s in lst}

        self.talep = {(t["ekip"], t["gun"], t["saat"]): (t["asgari"], t["hedef"])
                      for t in girdi["talep"]}
        self.gun_sayisi = girdi["donem"]["gun"]

        _k = {k["kod"]: k for k in girdi["kurallar"]}
        self.h_lim = _k["HAFTALIK_AZAMI"]["param"]["saat"]
        self.g_lim = _k["GUNLUK_AZAMI"]["param"]["saat"]

        # planın mevcut durumu
        self._durum_kur()

        # temel ihlal imzası: öneri bunun ÜZERİNE yeni ihlal eklememeli
        self.temel = self.imza(plan)

    def _durum_kur(self):
        self.gunler, self.net, self.bloklar = {}, {}, {}
        for a in self.plan["atamalar"]:
            cid = a["calisan"]
            self.gunler.setdefault(cid, set()).add(a["gun"])
            self.net[cid] = self.net.get(cid, 0.0) + self.d.net_saat(a)
            self.bloklar.setdefault(cid, []).append(
                (a["gun"] * 24 + sf(a["bas"]), a["gun"] * 24 + sf(a["bit"])))
        for cid, lst in self.d.gecmis.items():
            self.bloklar.setdefault(cid, []).extend(lst)

        self.kapsama, self.lider = {}, {}
        rol = self.d.kural["ROL_KAPSAMASI"]["param"]
        self.rol_adi, self.rol_asgari = rol["rol"], rol["asgari"]
        for a in self.plan["atamalar"]:
            c = self.cal.get(a["calisan"])
            for h in range(int(sf(a["bas"])), int(sf(a["bit"]))):
                if self.d.molada(a, h):
                    continue
                k = (a["ekip"],) + hucre(a["gun"], h)
                self.kapsama[k] = self.kapsama.get(k, 0) + 1
                if c and self.rol_adi in c["roller"]:
                    self.lider[k] = self.lider.get(k, 0) + 1

        # DEVİR VARDİYALARI — değerlendirici bunları kapsamaya sayıyor;
        # öneri motoru saymazsa 0. günün ilk saatlerinde HAYALET boşluk
        # gösterir ve müdürü olmayan bir açığı doldurmaya çalıştırır.
        for cid, araliklar in self.d.gecmis.items():
            c = self.cal.get(cid)
            if not c:
                continue
            for ab, at in araliklar:
                for h in range(int(ab), int(at)):
                    if not (0 <= h < self.gun_sayisi * 24):
                        continue
                    k = (c["ekip"], h // 24, h % 24)
                    self.kapsama[k] = self.kapsama.get(k, 0) + 1
                    if self.rol_adi in c["roller"]:
                        self.lider[k] = self.lider.get(k, 0) + 1

    def imza(self, plan):
        """İhlallerin KİMLİĞİ — sayısı değil.

        İlk sürümde 'ihlal sayısı arttı mı' diye bakıyordum. Bu, bir ihlali
        başka bir ihlalle TAKAS etmeye izin veriyordu: aday rol açığını kapatır
        ama dinlenme ihlali doğurur, toplam değişmez, kontrol 'sorun yok' der.
        Doğruluk testi bunu yakaladı. Artık imza karşılaştırılıyor: adayın
        ÖNCEDEN OLMAYAN bir ihlal doğurmaması gerekir.
        """
        from collections import Counter
        return Counter((i.kod, i.calisan, i.ekip, i.gun, i.saat)
                       for i in self.d.calistir(plan) if i.tur == "SERT")

    def _ihlal_sayisi(self, plan):
        return sum(1 for i in self.d.calistir(plan) if i.tur == "SERT")

    # ---------------- 1) BOŞLUKLAR ----------------

    def acikliklar(self):
        """Planda asgari kapsama veya rol kapsaması altında kalan hücreler."""
        acik = []
        for (ekip, gun, saat), (asgari, hedef) in self.talep.items():
            k = (ekip, gun, saat)
            m = self.kapsama.get(k, 0)
            l = self.lider.get(k, 0)
            if m < asgari:
                acik.append({"ekip": ekip, "gun": gun, "saat": saat,
                             "tip": "KAPSAMA", "gereken": asgari, "mevcut": m,
                             "eksik": asgari - m})
            elif l < self.rol_asgari:
                acik.append({"ekip": ekip, "gun": gun, "saat": saat,
                             "tip": "ROL", "gereken": self.rol_asgari, "mevcut": l,
                             "eksik": self.rol_asgari - l})
        acik.sort(key=lambda a: (-a["eksik"], a["gun"], a["saat"]))
        return acik

    # ---------------- 2) HAM ADAYLAR ----------------

    def ham_adaylar(self, ekip, gun, saat):
        """Bu hücreyi kapsayan (çalışan, şablon, başlangıç günü) üçlüleri."""
        out = []
        for bas_gun in (gun, gun - 1):
            if bas_gun < 0:
                continue
            for s in self.sab.get(ekip, []):
                if not any(hucre(bas_gun, h) == (gun, saat)
                           for h in range(int(s["bas"]), int(s["bit"]))):
                    continue
                for c in self.aktif:
                    if c["ekip"] != ekip:
                        continue
                    out.append((c, s, bas_gun))
        return out

    # ---------------- 3) ÖN FİLTRE (ucuz) ----------------

    def on_filtre(self, c, s, gun, rol_gerek=False):
        """Kesinlikle imkânsız olanları ucuza ele. Şüphe varsa GEÇİR —
        son sözü doğrulama aşaması söyler (yanlış negatif üretmemek için)."""
        cid = c["id"]
        if rol_gerek and self.rol_adi not in c["roller"]:
            return False
        if gun in self.gunler.get(cid, set()):
            return False
        # NOT: "haftada en fazla 6 gün" bir KURAL DEĞİL, planlayıcının
        # sezgisidir. Gerçek kural HAFTA_TATILI'dir (24 saat kesintisiz).
        # Filtreye koyduğumda uygun adayların %30'unu eliyordu — ön filtre
        # kuraldan katı olmamalı; son sözü doğrulama aşaması söyler.
        for iz in c.get("izinler", []):
            if iz["gun"] in gunler_arasi(gun, s["bas"], s["bit"]):
                return False
        if c.get("uygunluk"):
            kapali = set()
            for u in c["uygunluk"]:
                if u["tip"] != "UYGUN_DEGIL":
                    continue
                for x in range(int(sf(u["bas"])), int(sf(u["bit"]))):
                    kapali.add((u["gun"], x))
            for h in range(int(s["bas"]), int(s["bit"])):
                if hucre(gun, h) in kapali:
                    return False
        if self.net.get(cid, 0.0) + s["net"] > self.h_lim + 1e-6:
            return False
        if c["tur"] == "YARI_ZAMANLI":
            if self.net.get(cid, 0.0) + s["net"] > c["sozlesme_dk_hafta"] / 60.0 + 1e-6:
                return False
        ab, at = gun * 24 + s["bas"], gun * 24 + s["bit"]
        for pb, pt in self.bloklar.get(cid, []):
            if pb >= at:
                if pb - at < DINLENME_SAAT - 1e-6:
                    return False
            elif pt <= ab:
                if ab - pt < DINLENME_SAAT - 1e-6:
                    return False
            else:
                return False
        return True

    # ---------------- 4) DOĞRULAMA (pahalı ama kesin) ----------------

    def atama_yap(self, c, s, gun, mola_saat=None):
        return {"id": "ONERI", "calisan": c["id"], "ekip": c["ekip"], "gun": gun,
                "bas": hs(s["bas"]), "bit": hs(s["bit"]),
                "mola_dk": s["mola_dk"],
                "mola_saat": hs(float(mola_saat)) if mola_saat is not None else None,
                "sablon": s["id"]}

    def mola_sec(self, s, ekip, gun):
        """Kapsamayı en az bozan mola saati."""
        if s["mola_dk"] < 30:
            return None
        adaylar = list(range(int(s["bas"]), int(s["bit"])))
        if not adaylar:
            return None
        return max(adaylar, key=lambda h: self.kapsama.get((ekip,) + hucre(gun, h), 0)
                   - self.talep.get((ekip,) + hucre(gun, h), (0, 0))[0])

    def dogrula(self, ek_atamalar, temel_imza):
        """Bu atamalar ÖNCEDEN OLMAYAN bir sert ihlal doğuruyor mu?

        Dönen: (yeni_ihlal_sayısı, yeni_ihlallerin_listesi).
        0 ise aday güvenle gösterilebilir.
        """
        p = {"atamalar": self.plan["atamalar"] + ek_atamalar}
        sonra = self.imza(p)
        yeni = sonra - temel_imza          # Counter farkı: yalnız ARTANLAR
        return sum(yeni.values()), list(yeni.elements())

    # ---------------- 5) ETKİLER (açıklama verisi) ----------------

    def etkiler(self, c, s, gun, acik):
        cid = c["id"]
        soz = c["sozlesme_dk_hafta"] / 60.0
        sonra = self.net.get(cid, 0.0) + s["net"]

        # ekip ortalaması (adalet)
        ayni = [self.net.get(x["id"], 0.0) for x in self.aktif
                if x["ekip"] == c["ekip"] and x["tur"] == c["tur"]]
        ort = sum(ayni) / max(1, len(ayni))

        # kaç boşluk kapanıyor — hem kapsama hem ROL açığı sayılır
        kapatilan = 0
        lider_mi = self.rol_adi in c["roller"]
        for h in range(int(s["bas"]), int(s["bit"])):
            k = (c["ekip"],) + hucre(gun, h)
            t = self.talep.get(k)
            if not t:
                continue
            if self.kapsama.get(k, 0) < t[0]:
                kapatilan += 1
            elif lider_mi and self.lider.get(k, 0) < self.rol_asgari:
                kapatilan += 1

        # yan etki: bu atama hangi günleri kilitler (11 saat dinlenme)
        ab, at = gun * 24 + s["bas"], gun * 24 + s["bit"]
        kilitlenen = []
        for d2 in range(self.gun_sayisi):
            if d2 == gun or d2 in self.gunler.get(cid, set()):
                continue
            oncesi = any(self.on_filtre(c, s2, d2) for s2 in self.sab.get(c["ekip"], []))
            if not oncesi:
                continue
            hala = False
            for s2 in self.sab.get(c["ekip"], []):
                b2, t2 = d2 * 24 + s2["bas"], d2 * 24 + s2["bit"]
                if b2 >= at:
                    ok = b2 - at >= DINLENME_SAAT - 1e-6
                elif t2 <= ab:
                    ok = ab - t2 >= DINLENME_SAAT - 1e-6
                else:
                    ok = False
                if ok and self.on_filtre(c, s2, d2):
                    hala = True
                    break
            if not hala:
                kilitlenen.append(d2)

        return {
            "haftalik_sonra": round(sonra, 1),
            "haftalik_limit": self.h_lim,
            "sozlesme": round(soz, 1),
            "fazla_mesai": round(max(0.0, sonra - soz), 1),
            "vardiya_sayisi": len(self.gunler.get(cid, set())),
            "ekip_ortalama_saat": round(ort, 1),
            "kapatilan_bosluk": kapatilan,
            "kilitlenen_gunler": kilitlenen,
            "lider_mi": self.rol_adi in c["roller"],
        }

    # ---------------- 6) ÖNERİ ÜRETİMİ ----------------

    def oner(self, acik, n=5, dogrulama_ustu=40):
        """Bir boşluk için doğrulanmış aday listesi."""
        ekip, gun, saat = acik["ekip"], acik["gun"], acik["saat"]
        rol_gerek = acik["tip"] == "ROL"
        temel = self.imza(self.plan)

        gecen = []
        for c, s, bas_gun in self.ham_adaylar(ekip, gun, saat):
            if self.on_filtre(c, s, bas_gun, rol_gerek):
                gecen.append((c, s, bas_gun))

        # önce ucuz puanla sırala, sadece en iyi N×2 adayı doğrula
        def on_puan(t):
            c, s, bg = t
            soz = c["sozlesme_dk_hafta"] / 60.0
            bosluk_katkisi = sum(
                1 for h in range(int(s["bas"]), int(s["bit"]))
                if self.talep.get((ekip,) + hucre(bg, h))
                and self.kapsama.get((ekip,) + hucre(bg, h), 0)
                < self.talep[(ekip,) + hucre(bg, h)][0])
            bosta = max(0.0, soz - self.net.get(c["id"], 0.0))
            return bosluk_katkisi * 10 + bosta
        gecen.sort(key=on_puan, reverse=True)

        adaylar = []
        for c, s, bas_gun in gecen[:dogrulama_ustu]:
            mola = self.mola_sec(s, ekip, bas_gun)
            at = self.atama_yap(c, s, bas_gun, mola)
            fark, ihl = self.dogrula([at], temel)
            if fark > 0:
                continue                       # yeni ihlal doğuruyor → gösterme
            a = Aday(c["id"], bas_gun, s["id"], hs(s["bas"]), hs(s["bit"]))
            a.etki = self.etkiler(c, s, bas_gun, acik)
            a.puan = (a.etki["kapatilan_bosluk"] * 10
                      - a.etki["fazla_mesai"] * 3
                      - len(a.etki["kilitlenen_gunler"]) * 2
                      + max(0.0, a.etki["ekip_ortalama_saat"]
                            - a.etki["haftalik_sonra"]))
            adaylar.append(a)
            if len(adaylar) >= n:
                break
        adaylar.sort(key=lambda x: -x.puan)
        return adaylar

    # ---------------- 7) ZİNCİR ÖNERİ (iki adım) ----------------

    def zincir_oner(self, acik, n=3):
        """Doğrudan aday yoksa: başka bir günden birini bu boşluğa AL,
        onun boşalan yerini başkasıyla doldur.

        Tek adımlı öneri sık sık 'aday yok' der; oysa iki adımlı çözüm
        vardır. Bunu sunmayan bir editör, çizelgeciden geri kalır.
        """
        ekip, gun, saat = acik["ekip"], acik["gun"], acik["saat"]
        rol_gerek = acik["tip"] == "ROL"
        temel = self.imza(self.plan)
        cikti = []

        hedefler = self.ham_adaylar(ekip, gun, saat)
        # taşınabilecek mevcut atamalar (aynı ekip)
        mevcut = [a for a in self.plan["atamalar"] if a["ekip"] == ekip]

        for c, s, bas_gun in hedefler:
            if rol_gerek and self.rol_adi not in c["roller"]:
                continue
            if bas_gun not in self.gunler.get(c["id"], set()):
                continue          # zaten boşta — tek adımlı öneri işi görür
            eski = next((a for a in mevcut
                         if a["calisan"] == c["id"] and a["gun"] == bas_gun), None)
            if eski is None:
                continue
            # eski atamayı kaldır, yenisini koy
            kalan = [a for a in self.plan["atamalar"] if a is not eski]
            mola = self.mola_sec(s, ekip, bas_gun)
            yeni_at = self.atama_yap(c, s, bas_gun, mola)
            p = {"atamalar": kalan + [yeni_at]}
            sonra = self.imza(p)
            if sum((sonra - temel).values()) > 0:
                continue
            sert = sum(sonra.values())
            cikti.append({
                "tasinan": c["id"],
                "eski": f"gün {eski['gun']} {eski['bas']}–{eski['bit']} ({eski['sablon']})",
                "yeni": f"gün {bas_gun} {hs(s['bas'])}–{hs(s['bit'])} ({s['id']})",
                "kalan_ihlal": sert,
            })
            if len(cikti) >= n:
                break
        return cikti


# --------------------------------------------------------------------
# DOĞRULUK TESTİ — yanlış pozitif / yanlış negatif
# --------------------------------------------------------------------

def dogruluk_testi(motor, acikliklar, ornek=3):
    """Öneri motorunun listesini MUTLAK GERÇEKLE karşılaştır.

    Mutlak gerçek: ekipteki HER çalışan × hücreyi kapsayan HER şablon tek tek
    plana eklenir ve bağımsız değerlendiriciden geçirilir. Yeni sert ihlal
    doğurmayanlar 'gerçekten uygun' kümesidir.

    yanlış pozitif = motorun önerdiği ama gerçekte uygun olmayan  → SIFIR OLMALI
    yanlış negatif = gerçekte uygun olan ama motorun kaçırdığı    → ölçülür
    """
    print("=" * 72)
    print("ÖNERİ DOĞRULUK TESTİ")
    print("=" * 72)
    print("  Mutlak gerçek: her aday tek tek plana eklenip bağımsız")
    print("  değerlendiriciden geçiriliyor. Motorun listesiyle karşılaştırılıyor.\n")

    temel = motor.imza(motor.plan)
    top_yp = top_yn = top_gercek = 0

    for acik in acikliklar[:ornek]:
        ekip, gun, saat = acik["ekip"], acik["gun"], acik["saat"]
        rol_gerek = acik["tip"] == "ROL"

        # --- mutlak gerçek ---
        gercek = set()
        t0 = time.time()
        for c, s, bas_gun in motor.ham_adaylar(ekip, gun, saat):
            if rol_gerek and motor.rol_adi not in c["roller"]:
                continue
            mola = motor.mola_sec(s, ekip, bas_gun)
            at = motor.atama_yap(c, s, bas_gun, mola)
            fark, _ = motor.dogrula([at], temel)
            if fark == 0:
                gercek.add((c["id"], bas_gun, s["id"]))
        t_gercek = time.time() - t0

        # --- motorun önerisi ---
        t1 = time.time()
        adaylar = motor.oner(acik, n=999, dogrulama_ustu=10 ** 9)
        t_motor = time.time() - t1
        onerilen = {(a.calisan, a.gun, a.sablon) for a in adaylar}

        yp = onerilen - gercek
        yn = gercek - onerilen
        top_yp += len(yp); top_yn += len(yn); top_gercek += len(gercek)

        print(f"  {ekip} gün {gun} saat {saat:02d}  ({acik['tip']}, "
              f"{acik['mevcut']}/{acik['gereken']})")
        print(f"      gerçekten uygun : {len(gercek):>4}   ({t_gercek:.2f} sn — kaba kuvvet)")
        print(f"      motorun önerisi : {len(onerilen):>4}   ({t_motor:.2f} sn)")
        print(f"      YANLIŞ POZİTİF  : {len(yp):>4}   (0 olmalı)")
        print(f"      yanlış negatif  : {len(yn):>4}"
              + (f"   (%{100*len(yn)/max(1,len(gercek)):.1f} kayıp)" if gercek else ""))
        if yp:
            print(f"        ! {list(yp)[:3]}")
        print()

    print(f"  TOPLAM: yanlış pozitif {top_yp}, yanlış negatif {top_yn} "
          f"/ {top_gercek} gerçek aday")
    if top_yp == 0:
        print("  ✓ Müdüre gösterilen hiçbir aday kural ihlal etmiyor.")
    else:
        print("  ✗ GÜVEN SORUNU: listede kural çiğneyen aday var.")
    return top_yp == 0


# --------------------------------------------------------------------

def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    girdi = json.load(open(yol, encoding="utf-8"))

    # 1) yayınlanmış plan
    w = dict(girdi["hedef_profilleri"]["DENGELI"])
    w.setdefault("kararlilik", w.pop("tercih", 5))
    plan = Planlayici(girdi, "DENGELI", w).calistir()

    # 2) müdürün düzenlemeleri: birkaç kişiyi çıkar
    from yeniden_planla import duzenleme_uret
    duz = duzenleme_uret(plan)
    cikar = {(d["calisan"], d["gun"]) for d in duz if d["tip"] in ("CIKAR", "TASI")}
    plan2 = {"atamalar": [a for a in plan["atamalar"]
                          if (a["calisan"], a["gun"]) not in cikar]}

    print("=" * 72)
    print("PLAN EDİTÖRÜ — YEREL ONARIM ÖNERİLERİ")
    print("=" * 72)
    print(f"  veri seti : {yol}")
    print(f"  müdür {len(cikar)} atamayı kaldırdı\n")

    motor = OneriMotoru(girdi, plan2)
    acik = motor.acikliklar()
    print(f"  Oluşan boşluk: {len(acik)} hücre")
    if not acik:
        print("  Kaldırılan atamalar asgari kapsamayı bozmamış — onarım gerekmiyor.")
        return 0

    # 3) ilk boşluk için öneri + açıklama
    for a in acik[:2]:
        print("\n" + "-" * 72)
        print(f"  BOŞLUK: {a['ekip']} · gün {a['gun']} · saat {a['saat']:02d}:00 "
              f"— {a['tip']} ({a['mevcut']}/{a['gereken']})")
        print("-" * 72)
        t0 = time.time()
        adaylar = motor.oner(a, n=4)
        sure = time.time() - t0
        if not adaylar:
            print("  Doğrudan aday yok. Zincir öneriler aranıyor...")
            for z in motor.zincir_oner(a):
                print(f"    ↻ {z['tasinan']}: {z['eski']} → {z['yeni']}")
            continue
        for i, ad in enumerate(adaylar, 1):
            e = ad.etki
            c = motor.cal[ad.calisan]
            print(f"\n  {i}. {ad.calisan} ({c['ad']}) — gün {ad.gun} "
                  f"{ad.bas}–{ad.bit} [{ad.sablon}]"
                  + ("  ★ takım lideri" if e["lider_mi"] else ""))
            print(f"       • {e['kapatilan_bosluk']} saatlik açığı kapatır")
            print(f"       • Haftalık {e['haftalik_sonra']} sa olur "
                  f"(sözleşme {e['sozlesme']}, sınır {e['haftalik_limit']})"
                  + (f" — {e['fazla_mesai']} sa fazla mesai"
                     if e["fazla_mesai"] else ""))
            print(f"       • Bu hafta {e['vardiya_sayisi']} vardiyası var; "
                  f"ekip ortalaması {e['ekip_ortalama_saat']} sa")
            if e["kilitlenen_gunler"]:
                print(f"       • YAN ETKİ: bu atama {e['kilitlenen_gunler']} "
                      f"günlerini kapatır (11 saat dinlenme)")
            else:
                print("       • Yan etki yok — diğer günlere müsait kalır")
        print(f"\n  ({sure:.2f} sn'de üretildi)")

    # 4) doğruluk testi
    print()
    ok = dogruluk_testi(motor, acik, ornek=3)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
