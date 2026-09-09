#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cpsat.py — aynı girdi.json'ın OR-Tools CP-SAT ile kesin çözümü.

AMAÇ: planla.py açgözlü (greedy) bir planlayıcıdır — iyi plan bulur ama
"daha iyisi yok" diyemez. CP-SAT kesin çözücüdür: bulduğu çözümün yanında
bir de ÜST SINIR verir. Aradaki fark = greedy'nin optimuma uzaklığı.

Kurulum:  pip install ortools
Çalıştırma:  py cpsat.py            (varsayılan 120 sn süre sınırı)
             py cpsat.py 300        (300 sn ver)
             py cpsat.py 120 KAPSAMA
             py cpsat.py 300 DENGELI girdi_otel.json    (otel veri seti)

Çıktı: plan_CPSAT_<profil>.json + ekranda greedy ile karşılaştırma.
Üretilen plan, planla.py'nin kullandığı AYNI bağımsız denetleyiciden geçirilir.

MODELLEME NOTLARI (dürüstlük için):
- Karar değişkeni x[çalışan, gün, şablon] ikili. Günde tek vardiya kısıtı var.
- Mola yerleşimi de karar değişkenidir (şablon bazında toplulaştırılmış sayaç).
  Molalar kapsamadan düşülür, yani MOLA_KAPSAMASI modelin içindedir.
- Greedy'de "sözleşme + profil toleransı" SERT bir kapı gibi çalışıyordu.
  Burada gerçek kural setine sadık kalındı: tam zamanlıda sert tavan yalnızca
  HAFTALIK_AZAMI (45 sa); sözleşme aşımı hedef fonksiyonunda CEZA'dır.
  Bu, CP-SAT'e greedy'de olmayan bir serbestlik verir — fark buradan da gelebilir,
  raporda ayrıca gösterilir.
- "Kararlılık" (vardiya saatinin günden güne oynamaması) 17 kuralın parçası
  değildir, sadece greedy'de bir puanlama ağırlığıydı. Modele KONULMADI.
  Bu yüzden ana karşılaştırma metriği hedef kapsama yüzdesidir.
"""

import json
import sys
from datetime import date

from degerlendirici import Degerlendirici, sf, hucre, gunler_arasi

MAX_CALISMA_GUNU = 6
DINLENME_SAAT = 11


# --------------------------------------------------------------------
# Veri hazırlığı
# --------------------------------------------------------------------

class Veri:
    def __init__(self, girdi):
        self.g = girdi
        self.baslangic = date.fromisoformat(girdi["donem"]["baslangic"])
        self.gun_sayisi = girdi["donem"]["gun"]

        self.calisanlar = [c for c in girdi["calisanlar"] if c["durum"] == "AKTIF"]
        self.cal = {c["id"]: c for c in self.calisanlar}
        self.ekipler = girdi["ekipler"]

        self.kural = {k["kod"]: k for k in girdi["kurallar"]}
        self.g_lim = self.kural["GUNLUK_AZAMI"]["param"]["saat"]
        self.h_lim = self.kural["HAFTALIK_AZAMI"]["param"]["saat"]
        self.rol = self.kural["ROL_KAPSAMASI"]["param"]
        self.tol_dk = int(self.kural["SAAT_DENGESI"]["param"]["tolerans_saat"] * 60)

        # gece kuralları (7/24 operasyonlarda tanımlı, çağrı merkezinde değil)
        _g = self.kural.get("GECE_VARDIYASI_AZAMI")
        _a = self.kural.get("ARDISIK_GECE_LIMIT")
        self.gece_lim = _g["param"]["saat"] if _g else None
        self.gece_pen = ((int(sf(_g["param"]["bas"])), int(sf(_g["param"]["bit"])))
                         if _g else None)
        self.gece_ardisik = _a["param"]["ardisik"] if _a else None

        # yetkinlik gereksinimleri (rol kapsamasının genel hâli)
        _y = self.kural.get("YETKINLIK_KAPSAMASI")
        self.yetk_gerek = (_y["param"].get("gereksinimler") or []) if _y else []

        # --- müdürün manuel düzenlemeleri (yeniden planlama) ---
        self.kilitler = girdi.get("kilitler") or []
        self.yasak = {(y["calisan"], y["gun"]) for y in (girdi.get("yasaklar") or [])}
        self.referans = {(r["calisan"], r["gun"], r["sablon"])
                         for r in (girdi.get("referans_atamalar") or [])}
        self.w_kararli = int(girdi.get("kararlilik_odulu", 0))

        # SABİT ATAMALAR (hafta ortası yeniden plan): gerçekleşmiş, değişmez.
        # Karar değişkeni DEĞİLLER — kapsamaya sabit katkı verirler, haftalık
        # bütçeden düşerler, dinlenme kuralını bağlarlar. Böylece gerçekleşen
        # saatlerin şablona uyma zorunluluğu ortadan kalkar.
        self.sabit = girdi.get("sabit_atamalar") or []
        self.donmus = set(girdi.get("donmus_gunler") or [])
        self.sabit_dk = {}          # calisan -> tüketilen net dakika
        for a in self.sabit:
            self.yasak.add((a["calisan"], a["gun"]))
            b, t = sf(a["bas"]), sf(a["bit"])
            net = int(round((t - b) * 60 - a.get("mola_dk", 0)))
            self.sabit_dk[a["calisan"]] = self.sabit_dk.get(a["calisan"], 0) + net

        # şablonlar
        self.sab = []
        for s in girdi["sablonlar"]:
            b, t = sf(s["bas"]), sf(s["bit"])
            self.sab.append({
                "id": s["id"], "ekip": s["ekip"], "bas": b, "bit": t,
                "mola_dk": s["mola_dk"],
                "net_dk": int(round((t - b) * 60 - s["mola_dk"])),
                "saatler": list(range(int(b), int(t))),
            })
        self.sab_ix = {s["id"]: i for i, s in enumerate(self.sab)}

        # talep
        self.talep = {}
        for t in girdi["talep"]:
            self.talep[(t["ekip"], t["gun"], t["saat"])] = (t["asgari"], t["hedef"])

        # geçmişin son bitişi (mutlak saat) — sabit atamalar da dahil
        self.son_bitis = {}
        for h in girdi["gecmis"]:
            d = (date.fromisoformat(h["tarih"]) - self.baslangic).days
            bit = d * 24 + sf(h["bit"])
            if bit > self.son_bitis.get(h["calisan"], -1e9):
                self.son_bitis[h["calisan"]] = bit
        for a in self.sabit:
            bit = a["gun"] * 24 + sf(a["bit"])
            if bit > self.son_bitis.get(a["calisan"], -1e9):
                self.son_bitis[a["calisan"]] = bit

    def lider_mi(self, c):
        return self.rol["rol"] in c["roller"]

    def sozlesme_dk(self, c):
        return c["sozlesme_dk_hafta"]

    def izinli(self, c, gun, s=None):
        """Gece vardiyası iki güne dokunur; ikisinde de izin varsa bağlar."""
        gunler = gunler_arasi(gun, s["bas"], s["bit"]) if s else [gun]
        return any(iz["gun"] in gunler for iz in c.get("izinler", []))

    def sozlesme_bitti(self, c, gun):
        if not c.get("sozlesme_bitis"):
            return False
        return (self.baslangic.toordinal() + gun
                > date.fromisoformat(c["sozlesme_bitis"]).toordinal())

    def uygunluk_engeli(self, c, gun, s):
        if not c.get("uygunluk"):
            return False
        kapali = set()
        for u in c["uygunluk"]:
            if u["tip"] != "UYGUN_DEGIL":
                continue
            for x in range(int(sf(u["bas"])), int(sf(u["bit"]))):
                kapali.add((u["gun"], x))
        return any(hucre(gun, h) in kapali for h in s["saatler"])

    def izinli_atama(self, c, gun, s):
        """Bu (çalışan, gün, şablon) üçlüsü sert kurallara göre mümkün mü?"""
        if c["ekip"] != s["ekip"]:
            return False
        if (c["id"], gun) in self.yasak:          # müdür bu kişiyi çıkardı
            return False
        if gun in self.donmus:                    # geçmiş gün, karar değil
            return False
        if self.izinli(c, gun, s) or self.sozlesme_bitti(c, gun):
            return False
        if self.uygunluk_engeli(c, gun, s):
            return False
        if s["net_dk"] > self.g_lim * 60 + 1:
            return False
        # GECE_VARDIYASI_AZAMI — molasız en kötü hâl üzerinden ön eleme
        if self.gece_lim is not None and self.gece_saati(s) > self.gece_lim + 1e-6:
            return False
        # yarı zamanlıda sözleşme SERT tavandır (PART_TIME_LIMIT)
        if c["tur"] == "YARI_ZAMANLI" and s["net_dk"] > self.sozlesme_dk(c):
            return False
        # geçmişe karşı 11 saat dinlenme (yalnız 0. gün etkilenir)
        onceki = self.son_bitis.get(c["id"])
        if onceki is not None and gun * 24 + s["bas"] - onceki < DINLENME_SAAT - 1e-6:
            return False
        return True

    def gece_mi(self, h: int) -> bool:
        b, t = self.gece_pen
        x = h % 24
        return (b <= x or x < t) if b > t else (b <= x < t)

    def gece_saati(self, s) -> int:
        if self.gece_pen is None:
            return 0
        return sum(1 for h in s["saatler"] if self.gece_mi(h))

    def gece_sablonu(self, s) -> bool:
        return self.gece_saati(s) > 0

    def mola_saatleri(self, s):
        """Molanın konabileceği saatler = vardiyanın tüm saatleri.

        İlk sürümde ilk ve son saat hariç tutulmuştu; cpsat_kontrol.py bunu
        yakaladı. MOLA_HAKKI kuralı molanın SÜRESİNİ şart koşar, YERİNİ değil.
        Modeli kuraldan katı yapmak, çözücüyü yanlış problemi çözmeye zorlar.
        """
        if s["mola_dk"] < 30:
            return []
        return list(s["saatler"])


# --------------------------------------------------------------------
# Model kurulumu  (cp_model dışarıdan verilir → sahte modülle test edilebilir)
# --------------------------------------------------------------------

def kur_model(v: Veri, profil: str, cp_model):
    w = v.g["hedef_profilleri"][profil]
    w_kapsama = int(w["kapsama"])
    w_adalet = int(w["adalet"])
    w_fm = int(w["fazla_mesai"])

    m = cp_model.CpModel()
    D = range(v.gun_sayisi)

    # --- x[e, d, s] + endeksler ---
    #
    # ENDEKS NEDEN VAR: ilk sürümde her kısıt "for k in x if k[0]==cid" gibi
    # tüm sözlüğü baştan tarıyordu. Bu, model kurulumunu çalışan sayısında
    # KARESEL yapıyordu — 2.000 çalışanda kurulum 37 saniye sürüyor, çözümün
    # kendisi kadar zaman yiyordu. Endekslerle kurulum doğrusala iner.
    x = {}
    x_c = {}        # cid            -> [(d, si, var)]
    x_cd = {}       # (cid, d)       -> [var]
    x_ds = {}       # (d, si)        -> [(cid, var)]
    for c in v.calisanlar:
        cid = c["id"]
        for d in D:
            for si, s in enumerate(v.sab):
                if not v.izinli_atama(c, d, s):
                    continue
                var = m.NewBoolVar(f"x_{cid}_{d}_{si}")
                x[(cid, d, si)] = var
                x_c.setdefault(cid, []).append((d, si, var))
                x_cd.setdefault((cid, d), []).append(var)
                x_ds.setdefault((d, si), []).append((cid, var))

    # --- 0) KİLİTLER: müdürün elle sabitlediği atamalar ---
    # Bunlar pazarlık konusu değildir; değişken sabitlenir.
    kilit_disi = []
    for k in v.kilitler:
        si = v.sab_ix.get(k["sablon"])
        anahtar = (k["calisan"], k["gun"], si)
        if si is not None and anahtar in x:
            m.Add(x[anahtar] == 1)
        else:
            kilit_disi.append(k)
    if kilit_disi:
        print(f"  UYARI: {len(kilit_disi)} kilitli atama modelin izinli kümesinde "
              f"değil — kural ihlali doğuruyor (ör. {kilit_disi[0]}).")
        print("         Model bunları uygulayamaz; değerlendirici KILIT_UYUMU olarak")
        print("         raporlayacaktır. Müdüre 'bu düzenleme kuralı çiğniyor' denmeli.")

    # --- 1) günde en fazla bir vardiya ---
    for c in v.calisanlar:
        for d in D:
            gunun = x_cd.get((c["id"], d), [])
            if len(gunun) > 1:
                m.Add(sum(gunun) <= 1)

    # --- 2) HAFTA_TATILI: haftada en fazla 6 çalışma günü ---
    for c in v.calisanlar:
        hepsi = [var for _d, _si, var in x_c.get(c["id"], [])]
        if len(hepsi) > MAX_CALISMA_GUNU:
            m.Add(sum(hepsi) <= MAX_CALISMA_GUNU)

    # --- 3) HAFTALIK_AZAMI (+ yarı zamanlıda sözleşme tavanı) ---
    for c in v.calisanlar:
        hepsi = [(var, v.sab[si]["net_dk"]) for _d, si, var in x_c.get(c["id"], [])]
        if not hepsi:
            continue
        tavan = v.h_lim * 60
        if c["tur"] == "YARI_ZAMANLI":
            tavan = min(tavan, v.sozlesme_dk(c))
        # gerçekleşmiş saatler bütçeden düşer
        tavan -= v.sabit_dk.get(c["id"], 0)
        m.Add(sum(dk * var for var, dk in hepsi) <= max(0, tavan))

    # --- 4) VARDIYA_ARASI_DINLENME (ardışık günler) ---
    # Yasak şablon çiftleri çalışandan bağımsızdır; bir kez hesaplanır.
    yasak_cift = [
        (si, sj)
        for si, s1 in enumerate(v.sab)
        for sj, s2 in enumerate(v.sab)
        if (24 + s2["bas"]) - s1["bit"] < DINLENME_SAAT - 1e-6
    ]
    for c in v.calisanlar:
        cid = c["id"]
        for d in range(v.gun_sayisi - 1):
            for si, sj in yasak_cift:
                v1 = x.get((cid, d, si))
                if v1 is None:
                    continue
                v2 = x.get((cid, d + 1, sj))
                if v2 is None:
                    continue
                m.Add(v1 + v2 <= 1)

    # --- 4b) ARDISIK_GECE_LIMIT (7/24 operasyonlarda) ---
    if v.gece_ardisik is not None:
        gece_si = [si for si, s in enumerate(v.sab) if v.gece_sablonu(s)]
        lim = v.gece_ardisik
        for c in v.calisanlar:
            cid = c["id"]
            for d0 in range(v.gun_sayisi - lim):
                pencere = [x[(cid, d0 + k, si)]
                           for k in range(lim + 1) for si in gece_si
                           if (cid, d0 + k, si) in x]
                if len(pencere) > lim:
                    m.Add(sum(pencere) <= lim)

    # --- şablon bazında sayaçlar ---
    n = {}      # (d, si) -> kişi sayısı
    nl = {}     # (d, si) -> lider sayısı
    for d in D:
        for si, s in enumerate(v.sab):
            grup = x_ds.get((d, si), [])
            uyeler = [var for _cid, var in grup]
            liderler = [var for _cid, var in grup if v.lider_mi(v.cal[_cid])]
            ust = max(1, len(uyeler))
            n[(d, si)] = m.NewIntVar(0, ust, f"n_{d}_{si}")
            m.Add(n[(d, si)] == (sum(uyeler) if uyeler else 0))
            nl[(d, si)] = m.NewIntVar(0, max(1, len(liderler)), f"nl_{d}_{si}")
            m.Add(nl[(d, si)] == (sum(liderler) if liderler else 0))

    # --- 5) mola yerleşimi (toplulaştırılmış) ---
    bk, bl = {}, {}
    for d in D:
        for si, s in enumerate(v.sab):
            saatler = v.mola_saatleri(s)
            if not saatler:
                continue
            for h in saatler:
                bk[(d, si, h)] = m.NewIntVar(0, 400, f"bk_{d}_{si}_{h}")
                bl[(d, si, h)] = m.NewIntVar(0, 400, f"bl_{d}_{si}_{h}")
                m.Add(bl[(d, si, h)] <= bk[(d, si, h)])
            # herkes molasını bir kez kullanır
            m.Add(sum(bk[(d, si, h)] for h in saatler) == n[(d, si)])
            m.Add(sum(bl[(d, si, h)] for h in saatler) == nl[(d, si)])

    # --- 5b) YETKİNLİK SAYAÇLARI ---
    # Rol kapsamasıyla aynı desen: şablon bazında "bu yetkinlikte kaç kişi"
    # ve "kaçı molada". Yalnız gereksinimde geçen yetkinlikler için kurulur.
    yetk_ekip = {}
    for g in v.yetk_gerek:
        yetk_ekip.setdefault(g["ekip"], set()).add(g["yetkinlik"])
    ny, by = {}, {}
    for d in D:
        for si, s in enumerate(v.sab):
            for y in yetk_ekip.get(s["ekip"], ()):
                grup = [var for cid, var in x_ds.get((d, si), [])
                        if y in (v.cal[cid].get("yetkinlikler") or [])]
                ny[(d, si, y)] = m.NewIntVar(0, max(1, len(grup)), f"ny_{d}_{si}_{y}")
                m.Add(ny[(d, si, y)] == (sum(grup) if grup else 0))
                saatler = v.mola_saatleri(s)
                if not saatler:
                    continue
                for h in saatler:
                    by[(d, si, h, y)] = m.NewIntVar(0, 400, f"by_{d}_{si}_{h}_{y}")
                    m.Add(by[(d, si, h, y)] <= bk[(d, si, h)])
                m.Add(sum(by[(d, si, h, y)] for h in saatler) == ny[(d, si, y)])

    # --- 6) ASGARI_KAPSAMA + MOLA_KAPSAMASI + ROL_KAPSAMASI ---
    #
    # Gece vardiyası ertesi güne taşar: (d, h) hücresini o gün BAŞLAYAN bir
    # vardiya da, bir önceki gün başlayan bir gece vardiyası da kapsayabilir.
    # kapsayan[(ekip, ofset, saat)] = o hücreyi 'ofset' gün önce başlayarak
    # kapsayan şablonlar ve bunun karşılık geldiği genişletilmiş saat.
    kapsayan = {}
    for si, s in enumerate(v.sab):
        for gh in s["saatler"]:                 # gh: genişletilmiş saat
            kapsayan.setdefault((s["ekip"], gh // 24, gh % 24), []).append((si, gh))

    # devir kapsaması: geçmiş vardiyaların plan penceresine düşen saatleri
    # + gerçekleşmiş (sabit) atamaların katkısı
    devir, devir_lider = {}, {}
    for a in v.sabit:
        c = v.cal.get(a["calisan"])
        if not c:
            continue
        mh = int(sf(a["mola_saat"])) if a.get("mola_saat") else None
        for gh in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            if gh == mh:
                continue
            k = (a["ekip"],) + hucre(a["gun"], gh)
            devir[k] = devir.get(k, 0) + 1
            if v.lider_mi(c):
                devir_lider[k] = devir_lider.get(k, 0) + 1
    for hh in v.g["gecmis"]:
        c = v.cal.get(hh["calisan"])
        if not c:
            continue
        d0 = (date.fromisoformat(hh["tarih"]) - v.baslangic).days
        for gh in range(int(sf(hh["bas"])), int(sf(hh["bit"]))):
            t_abs = d0 * 24 + gh
            if not (0 <= t_abs < v.gun_sayisi * 24):
                continue
            k = (c["ekip"], t_abs // 24, t_abs % 24)
            devir[k] = devir.get(k, 0) + 1
            if v.lider_mi(c):
                devir_lider[k] = devir_lider.get(k, 0) + 1

    kapsanan, sabit_acik = {}, []
    for (ekip, d, h), (asgari, hedef) in v.talep.items():
        kisiler, liderler = [], []
        for ofset in (0, 1):
            bd = d - ofset
            if bd < 0:
                continue
            for si, gh in kapsayan.get((ekip, ofset, h), []):
                kisiler.append(n[(bd, si)])
                liderler.append(nl[(bd, si)])
                if (bd, si, gh) in bk:
                    kisiler.append(-bk[(bd, si, gh)])
                    liderler.append(-bl[(bd, si, gh)])
        sabit = devir.get((ekip, d, h), 0)
        sabit_l = devir_lider.get((ekip, d, h), 0)
        if not kisiler and not sabit:
            continue
        # 0. günün ilk saatlerinde karar değişkeni olmayabilir: o saatler
        # yalnız GEÇMİŞTEN devreden gece vardiyasıyla kapanır. O durumda
        # kısıt sabittir — Add() edilemez, doğrudan sınanır.
        if not kisiler:
            if sabit < asgari:
                sabit_acik.append((ekip, d, h, asgari, sabit))
            if sabit_l < v.rol["asgari"]:
                sabit_acik.append((ekip, d, h, "rol", sabit_l))
            continue
        toplam = sum(kisiler) + sabit
        toplam_l = (sum(liderler) if liderler else 0) + sabit_l
        m.Add(toplam >= asgari)                             # SERT
        if liderler:
            m.Add(toplam_l >= v.rol["asgari"])              # SERT
        elif sabit_l < v.rol["asgari"]:
            sabit_acik.append((ekip, d, h, "rol", sabit_l))
        kv = m.NewIntVar(0, hedef, f"kap_{ekip}_{d}_{h}")   # hedefe katkı
        m.Add(kv <= toplam)
        kapsanan[(ekip, d, h)] = kv

    # --- 7) fazla mesai ve saat dengesi (yumuşak) ---
    fm, sap = {}, {}
    for c in v.calisanlar:
        hepsi = [(var, v.sab[si]["net_dk"]) for _d, si, var in x_c.get(c["id"], [])]
        if not hepsi:
            continue
        toplam = sum(dk * var for var, dk in hepsi)
        soz = v.sozlesme_dk(c)
        f = m.NewIntVar(0, 60 * 60, f"fm_{c['id']}")
        m.Add(f >= toplam - soz)
        fm[c["id"]] = f
        sp = m.NewIntVar(0, 60 * 60, f"sap_{c['id']}")
        m.Add(sp >= toplam - (soz + v.tol_dk))
        m.Add(sp >= (soz - v.tol_dk) - toplam)
        sap[c["id"]] = sp

    # --- "AZ DEĞİŞTİR" ödülü ---
    # Yeniden planlamada çözücü serbest bırakılırsa bambaşka bir optimum bulur
    # ve çizelgenin tamamını yeniden dizer. Müdür bir kişiyi oynatır, 400 vardiya
    # değişir — hiçbir işletme bunu kabul etmez. Referans plandaki atamaları
    # korumak ödüllendirilir; ödül ağırlığı veriden gelir.
    korunan = [x[(r[0], r[1], v.sab_ix[r[2]])]
               for r in v.referans
               if r[2] in v.sab_ix and (r[0], r[1], v.sab_ix[r[2]]) in x]

    hedef = (w_kapsama * 60 * sum(kapsanan.values())
             - w_fm * sum(fm.values())
             - w_adalet * sum(sap.values()))
    if korunan and v.w_kararli:
        hedef = hedef + v.w_kararli * sum(korunan)
    m.Maximize(hedef)

    # --- 6b) YETKINLIK_KAPSAMASI ---
    for g in v.yetk_gerek:
        ekip, yet, asg = g["ekip"], g["yetkinlik"], g.get("asgari", 1)
        saatler = g.get("saatler")
        for (e2, d, h), _t in v.talep.items():
            if e2 != ekip or (saatler is not None and h not in saatler):
                continue
            terim, sabit_y = [], 0
            for ofset in (0, 1):
                bd = d - ofset
                if bd < 0:
                    continue
                for si, gh in kapsayan.get((ekip, ofset, h), []):
                    if (bd, si, yet) not in ny:
                        continue
                    terim.append(ny[(bd, si, yet)])
                    if (bd, si, gh, yet) in by:
                        terim.append(-by[(bd, si, gh, yet)])
            for a in v.sabit:                      # gerçekleşmiş atamalar
                c = v.cal.get(a["calisan"])
                if not c or a["ekip"] != ekip or yet not in (c.get("yetkinlikler") or []):
                    continue
                mh = int(sf(a["mola_saat"])) if a.get("mola_saat") else None
                for gh in range(int(sf(a["bas"])), int(sf(a["bit"]))):
                    if gh != mh and hucre(a["gun"], gh) == (d, h):
                        sabit_y += 1
            if terim:
                m.Add(sum(terim) + sabit_y >= asg)
            elif sabit_y < asg:
                sabit_acik.append((ekip, d, h, yet, sabit_y))

    if sabit_acik:
        print(f"  NOT: {len(sabit_acik)} talep hücresi yalnız geçmişten devreden "
              f"vardiyalarla kapanabiliyor ve devir yetersiz —")
        print(f"       bu hücreler plan tarafından KAPATILAMAZ (ör. {sabit_acik[0]}).")

    return m, {"x": x, "x_c": x_c, "x_cd": x_cd, "x_ds": x_ds,
               "sabit_acik": sabit_acik,
               "n": n, "nl": nl, "bk": bk, "bl": bl,
               "kapsanan": kapsanan, "fm": fm, "sap": sap,
               "agirlik": (w_kapsama, w_adalet, w_fm)}


# --------------------------------------------------------------------
# Çözümden plan çıkarma
# --------------------------------------------------------------------

def hs(x_):
    h, mm = int(x_), int(round((x_ - int(x_)) * 60))
    return f"{h:02d}:{mm:02d}"


def plan_cikar(v: Veri, dv, solver, profil):
    x_ds = dv["x_ds"]
    atamalar = []
    for d in range(v.gun_sayisi):
        for si, s in enumerate(v.sab):
            kisiler = [cid for cid, var in x_ds.get((d, si), [])
                       if solver.Value(var) == 1]
            if not kisiler:
                continue
            liderler = [e for e in kisiler if v.lider_mi(v.cal[e])]
            digerler = [e for e in kisiler if e not in set(liderler)]

            # mola saatlerini dağıt: önce liderler (bl), sonra kalanlar
            atanan = {}
            saatler = v.mola_saatleri(s)
            lp, dp = list(liderler), list(digerler)
            for h in saatler:
                nl_h = solver.Value(dv["bl"][(d, si, h)])
                nk_h = solver.Value(dv["bk"][(d, si, h)])
                for _ in range(nl_h):
                    if lp:
                        atanan[lp.pop()] = h
                for _ in range(nk_h - nl_h):
                    if dp:
                        atanan[dp.pop()] = h

            for e in kisiler:
                atamalar.append({
                    "id": f"A{len(atamalar)+1:05d}",
                    "calisan": e, "ekip": s["ekip"], "gun": d,
                    "bas": hs(s["bas"]), "bit": hs(s["bit"]),
                    "mola_dk": s["mola_dk"],
                    "mola_saat": hs(float(atanan[e])) if e in atanan else None,
                    "sablon": s["id"],
                })
    return {"profil": profil, "motor": "CPSAT", "atamalar": atamalar}


# --------------------------------------------------------------------
# Karşılaştırma metrikleri
# --------------------------------------------------------------------

def olc(girdi, plan):
    """Ölçüm için planla.py'nin metrikler() fonksiyonu kullanılır.

    İlk sürümde burada ayrı bir ölçüm kodu vardı ve adaleti tüm çalışanlar
    üzerinden tek bir σ olarak hesaplıyordu — tam zamanlı (45 sa) ile yarı
    zamanlıyı (20 sa) aynı torbaya koyduğu için σ'yı şişiriyordu ve
    planla.py'nin raporladığı sayıyla uyuşmuyordu. İki ölçüm fonksiyonu
    olması hatanın kaynağıydı; tek kaynağa indirildi.
    """
    from planla import metrikler
    d = Degerlendirici(girdi)
    m = metrikler(girdi, plan, d)
    ihl = d.calistir(plan)
    return {
        "sert": sum(1 for i in ihl if i.tur == "SERT"),
        "hedef": m["hedef_karsilama"],
        "asgari": m["asgari_karsilama"],
        "fm": m["fazla_mesai_saat"],
        "sigma": m["adalet_sapma"],
        "atama": m["atama"],
        "calisan": m["calisan"],
    }


# --------------------------------------------------------------------

def main():
    sure = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
    profil = sys.argv[2] if len(sys.argv) > 2 else "DENGELI"
    yol = sys.argv[3] if len(sys.argv) > 3 else "girdi.json"
    import os
    _b = os.path.basename(yol)
    p_onek = _b[6:-5] + "_" if _b.startswith("girdi_") and _b.endswith(".json") else ""

    try:
        from ortools.sat.python import cp_model
    except ImportError:
        print("OR-Tools kurulu değil.  Kurulum:  pip install ortools")
        print("(Windows'ta: py -m pip install ortools)")
        return 1

    girdi = json.load(open(yol, encoding="utf-8"))
    v = Veri(girdi)

    print(f"Model kuruluyor  (profil {profil}) ...")
    m, dv = kur_model(v, profil, cp_model)
    print(f"  karar değişkeni x : {len(dv['x'])}")
    print(f"  mola değişkeni    : {len(dv['bk']) * 2}")
    print(f"  talep hücresi     : {len(dv['kapsanan'])}")

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = sure
    solver.parameters.num_search_workers = 8
    print(f"\nÇözülüyor (en fazla {sure:.0f} sn) ...")
    st = solver.Solve(m)
    ad = solver.StatusName(st)
    print(f"  durum: {ad}")

    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("\n  ÇÖZÜM BULUNAMADI.")
        print("  INFEASIBLE ise: kurallar bu veriyle çelişiyor demektir —")
        print("  sinav.py'deki teşhis yordamı hangi kuralın bağladığını söyler.")
        return 1

    plan = plan_cikar(v, dv, solver, profil)
    json.dump(plan, open(f"plan_CPSAT_{p_onek}{profil}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    c = olc(girdi, plan)
    try:
        gp = json.load(open(f"plan_{p_onek}{profil}.json", encoding="utf-8"))
        gm = olc(girdi, gp)
    except FileNotFoundError:
        gm = None

    obj = solver.ObjectiveValue()
    bound = solver.BestObjectiveBound()
    bosluk = 0.0 if not bound else abs(bound - obj) / abs(bound) * 100

    print("\n" + "=" * 62)
    print(f"KARŞILAŞTIRMA — profil {profil}")
    print("=" * 62)
    basliklar = ("", "GREEDY (planla.py)", "CP-SAT")
    print(f"  {basliklar[0]:24}{basliklar[1]:>20}{basliklar[2]:>16}")
    print("  " + "-" * 58)

    def sat(ad_, key, bicim):
        g = bicim(gm[key]) if gm else "—"
        print(f"  {ad_:24}{g:>20}{bicim(c[key]):>16}")

    sat("sert ihlal", "sert", lambda z: str(z))
    sat("asgari kapsama", "asgari", lambda z: f"%{100*z:.1f}")
    sat("hedef kapsama", "hedef", lambda z: f"%{100*z:.1f}")
    sat("fazla mesai (sa)", "fm", lambda z: f"{z}")
    sat("adalet σ (sa)", "sigma", lambda z: f"{z}")
    sat("atama", "atama", lambda z: str(z))

    print("\n  CP-SAT hedef değeri : {:,.0f}".format(obj))
    print("  Üst sınır (bound)   : {:,.0f}".format(bound))
    print(f"  Optimuma uzaklık    : %{bosluk:.2f}"
          + ("   (OPTIMAL — kanıtlanmış en iyi)" if ad == "OPTIMAL" else
             "   (süre sınırı; daha uzun süre verilirse daralır)"))

    if gm:
        fark = (c["hedef"] - gm["hedef"]) * 100
        print(f"\n  → Greedy'nin hedef kapsama açığı: {fark:+.2f} puan")
        if c["sert"] > 0:
            print("  ! CP-SAT planında sert ihlal var — model kodlaması ile kural")
            print("    setinin arasında fark var demektir; cpsat_kontrol.py çalıştırın.")
        elif abs(fark) < 2:
            print("    Fark küçük: greedy motor üretim için yeterli, ürün hızlı kalır.")
        else:
            print("    Fark anlamlı: motoru CP-SAT'e taşımak gerekçeli.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
