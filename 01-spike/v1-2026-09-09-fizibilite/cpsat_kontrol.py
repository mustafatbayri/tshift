#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cpsat_kontrol.py — CP-SAT modelinin KODLAMASINI, OR-Tools kurmadan test eder.

NEDEN GEREKLİ
Bir optimizasyon modelinde en sinsi hata "çözücü çalışmadı" değil, "çözücü
çalıştı ama yanlış problemi çözdü"dür. Model kuralları yanlış kodlarsa,
CP-SAT kusursuz bir çözüm üretir — yanlış bir problemin çözümünü.

YÖNTEM
1. Sahte bir cp_model modülü kurulur. Değişken ve kısıt üretmek yerine
   hepsini KAYDEDER (doğrusal ifade cebiri dahil).
2. cpsat.py'nin kur_model() fonksiyonu bu sahte modülle çalıştırılır.
3. planla.py'nin ürettiği, BAĞIMSIZ denetleyiciye göre 0 sert ihlalli plan
   alınır ve modelin değişkenlerine çevrilir.
4. Kaydedilen HER kısıt bu değerlerle tek tek sınanır.

Geçerli bir planın modelin bir kısıtını ihlal etmesi = model yanlış kodlanmış.
Bu test kurulum gerektirmez: py cpsat_kontrol.py
"""

import json
import sys

from degerlendirici import Degerlendirici, sf, hucre


# --------------------------------------------------------------------
# Sahte cp_model — doğrusal ifade cebiri + kısıt kaydı
# --------------------------------------------------------------------

class Ifade:
    """katsayi_haritasi (degisken_adi -> katsayi) + sabit."""

    def __init__(self, kats=None, sabit=0):
        self.k = dict(kats or {})
        self.s = sabit

    @staticmethod
    def cevir(o):
        if isinstance(o, Ifade):
            return o
        if isinstance(o, Degisken):
            return Ifade({o.ad: 1})
        if isinstance(o, (int, float)):
            return Ifade({}, o)
        raise TypeError(f"beklenmeyen tip: {type(o)}")

    def __add__(self, o):
        o = Ifade.cevir(o)
        k = dict(self.k)
        for a, c in o.k.items():
            k[a] = k.get(a, 0) + c
        return Ifade(k, self.s + o.s)

    __radd__ = __add__

    def __sub__(self, o):
        return self + (Ifade.cevir(o) * -1)

    def __rsub__(self, o):
        return Ifade.cevir(o) + (self * -1)

    def __mul__(self, o):
        if not isinstance(o, (int, float)):
            raise TypeError("yalnız sabitle çarpım")
        return Ifade({a: c * o for a, c in self.k.items()}, self.s * o)

    __rmul__ = __mul__

    def __neg__(self):
        return self * -1

    def deger(self, atama):
        t = self.s
        for a, c in self.k.items():
            t += c * atama.get(a, 0)
        return t

    def __le__(self, o): return Kisit(self - o, "<=")
    def __ge__(self, o): return Kisit(self - o, ">=")
    def __eq__(self, o): return Kisit(self - o, "==")


class Degisken(Ifade):
    def __init__(self, ad, alt, ust):
        super().__init__({ad: 1}, 0)
        self.ad, self.alt, self.ust = ad, alt, ust

    def __hash__(self):
        return hash(self.ad)

    def __repr__(self):
        return f"<{self.ad}>"


class Kisit:
    def __init__(self, ifade, yon):
        self.i, self.y = ifade, yon

    def saglandi(self, atama, tol=1e-6):
        d = self.i.deger(atama)
        if self.y == "<=":
            return d <= tol
        if self.y == ">=":
            return d >= -tol
        return abs(d) <= tol

    def __repr__(self):
        return f"{self.i.k} {self.i.s:+g} {self.y} 0"


class CpModel:
    def __init__(self):
        self.degiskenler = {}
        self.kisitlar = []
        self.hedef = None

    def _yeni(self, ad, alt, ust):
        if ad in self.degiskenler:
            raise ValueError(f"değişken adı iki kez kullanıldı: {ad}")
        v = Degisken(ad, alt, ust)
        self.degiskenler[ad] = v
        return v

    def NewBoolVar(self, ad):
        return self._yeni(ad, 0, 1)

    def NewIntVar(self, alt, ust, ad):
        return self._yeni(ad, alt, ust)

    def Add(self, kisit):
        if not isinstance(kisit, Kisit):
            raise TypeError("Add() bir karşılaştırma bekler")
        self.kisitlar.append(kisit)
        return kisit

    def Maximize(self, ifade):
        self.hedef = Ifade.cevir(ifade)


class SahteModul:
    CpModel = CpModel


# --------------------------------------------------------------------
# Greedy planı → model değişken değerleri
# --------------------------------------------------------------------

def plandan_atama(v, dv, plan):
    """Geçerli planı modelin değişken uzayına taşı."""
    atama = {ad: 0 for ad in dv["_model"].degiskenler}
    sab_ix = {s["id"]: i for i, s in enumerate(v.sab)}

    n_say, nl_say, bk_say, bl_say = {}, {}, {}, {}
    ny_say, by_say = {}, {}          # yetkinlik sayaçları
    eksik_x = []

    for a in plan["atamalar"]:
        si = sab_ix[a["sablon"]]
        anahtar = (a["calisan"], a["gun"], si)
        ad = f"x_{a['calisan']}_{a['gun']}_{si}"
        if ad not in atama:
            eksik_x.append(anahtar)      # model bu atamayı hiç mümkün görmemiş
            continue
        atama[ad] = 1
        d = a["gun"]
        n_say[(d, si)] = n_say.get((d, si), 0) + 1
        lider = v.lider_mi(v.cal[a["calisan"]])
        if lider:
            nl_say[(d, si)] = nl_say.get((d, si), 0) + 1
        yetk = v.cal[a["calisan"]].get("yetkinlikler") or []
        for y in yetk:
            ny_say[(d, si, y)] = ny_say.get((d, si, y), 0) + 1
        if a.get("mola_saat"):
            h = int(sf(a["mola_saat"]))
            bk_say[(d, si, h)] = bk_say.get((d, si, h), 0) + 1
            if lider:
                bl_say[(d, si, h)] = bl_say.get((d, si, h), 0) + 1
            for y in yetk:
                by_say[(d, si, h, y)] = by_say.get((d, si, h, y), 0) + 1

    for (d, si), val in n_say.items():
        atama[f"n_{d}_{si}"] = val
    for (d, si), val in nl_say.items():
        atama[f"nl_{d}_{si}"] = val
    for (d, si, h), val in bk_say.items():
        ad = f"bk_{d}_{si}_{h}"
        if ad in atama:
            atama[ad] = val
    for (d, si, h), val in bl_say.items():
        ad = f"bl_{d}_{si}_{h}"
        if ad in atama:
            atama[ad] = val
    for (d, si, y), val in ny_say.items():
        ad = f"ny_{d}_{si}_{y}"
        if ad in atama:
            atama[ad] = val
    for (d, si, h, y), val in by_say.items():
        ad = f"by_{d}_{si}_{h}_{y}"
        if ad in atama:
            atama[ad] = val

    # türev değişkenler: kapsanan / fm / sap — bunlar karar değil sonuç
    # değişkenleridir; hedef fonksiyonunun onları iteceği değerle doldurulur,
    # böylece greedy planının model hedef değeri CP-SAT ile kıyaslanabilir olur.
    molasiz = {}
    for a in plan["atamalar"]:
        mh = int(sf(a["mola_saat"])) if a.get("mola_saat") else None
        for h in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            if h == mh:
                continue
            k = (a["ekip"],) + hucre(a["gun"], h)      # gece vardiyası taşar
            molasiz[k] = molasiz.get(k, 0) + 1
    for (ekip, d, h), var in dv["kapsanan"].items():
        hedef = v.talep[(ekip, d, h)][1]
        atama[var.ad] = min(molasiz.get((ekip, d, h), 0), hedef)
    net_dk = {}
    for a in plan["atamalar"]:
        si = sab_ix[a["sablon"]]
        net_dk[a["calisan"]] = net_dk.get(a["calisan"], 0) + v.sab[si]["net_dk"]
    for cid, var in dv["fm"].items():
        soz = v.sozlesme_dk(v.cal[cid])
        atama[var.ad] = max(0, net_dk.get(cid, 0) - soz)
    for cid, var in dv["sap"].items():
        soz = v.sozlesme_dk(v.cal[cid])
        t = net_dk.get(cid, 0)
        atama[var.ad] = max(0, t - (soz + v.tol_dk), (soz - v.tol_dk) - t)

    return atama, eksik_x


# --------------------------------------------------------------------

def onek(yol):
    import os
    b = os.path.basename(yol)
    return b[6:-5] + "_" if b.startswith("girdi_") and b.endswith(".json") else ""


def sinif(kisit):
    """Kısıtı, içindeki değişken adlarına bakarak sınıfla."""
    adlar = set(kisit.i.k)
    if any(a.startswith(("ny_", "by_")) for a in adlar):
        return "YETKINLIK_KAPSAMASI"
    if any(a.startswith(("nl_", "bl_")) for a in adlar):
        return "ROL_KAPSAMASI"
    if any(a.startswith(("n_", "bk_")) for a in adlar):
        return "KAPSAMA"
    return "DIGER"


def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    p_onek = onek(yol)
    girdi = json.load(open(yol, encoding="utf-8"))
    try:
        plan = json.load(open(f"plan_{p_onek}DENGELI.json", encoding="utf-8"))
    except FileNotFoundError:
        print(f"Önce planla.py {yol} çalıştırın.")
        return 1

    import cpsat
    v = cpsat.Veri(girdi)

    print("=" * 64)
    print("CP-SAT MODEL KODLAMA TESTİ  (OR-Tools gerekmez)")
    print("=" * 64)

    print(f"  veri seti: {yol}")
    sahte = SahteModul()
    m, dv = cpsat.kur_model(v, "DENGELI", sahte)
    dv["_model"] = m

    print(f"\n  model kuruldu: {len(m.degiskenler)} değişken, "
          f"{len(m.kisitlar)} kısıt")
    print(f"    x (atama)      : {len(dv['x'])}")
    print(f"    mola sayaçları : {len(dv['bk']) + len(dv['bl'])}")
    print(f"    kapsama hücresi: {len(dv['kapsanan'])}")

    # Referans planın bağımsız denetleyiciye göre ihlalleri
    d = Degerlendirici(girdi)
    ref_ihl = [i for i in d.calistir(plan) if i.tur == "SERT"]
    ref_kod = {}
    for i in ref_ihl:
        ref_kod[i.kod] = ref_kod.get(i.kod, 0) + 1
    print(f"\n  referans plan (greedy) sert ihlal: {len(ref_ihl)}"
          + (f"  {ref_kod}" if ref_kod else "  (temiz)"))

    atama, eksik = plandan_atama(v, dv, plan)
    if eksik:
        print(f"\n  [HATA] Model {len(eksik)} geçerli atamayı 'imkânsız' saymış.")
        for k in eksik[:5]:
            print(f"         {k}")
        print("         izinli_atama() kural setinden daha katı.")
        return 1
    print("  geçerli planın her ataması modelde mevcut: ✓")

    ihlal = [k for k in m.kisitlar if not k.saglandi(atama)]
    print(f"\n  sınanan kısıt : {len(m.kisitlar)}")
    print(f"  ihlal edilen  : {len(ihlal)}")

    # ---- İKİ YÖNLÜ TUTARLILIK ----
    # Referans plan temizse model HİÇBİR kısıtı ihlal etmemeli.
    # Referans planda bilinen ihlaller varsa, modelin ihlal ettiği kısıtlar
    # TAM OLARAK onlara karşılık gelmeli: ne fazla (model gereksiz katı),
    # ne eksik (model gevşek — asıl tehlikeli yön).
    m_sinif = {}
    for k in ihlal:
        t = sinif(k)
        m_sinif[t] = m_sinif.get(t, 0) + 1

    beklenen = {}
    for kod, n in ref_kod.items():
        t = ("YETKINLIK_KAPSAMASI" if kod == "YETKINLIK_KAPSAMASI" else
             "ROL_KAPSAMASI" if kod == "ROL_KAPSAMASI" else
             "KAPSAMA" if kod in ("ASGARI_KAPSAMA", "MOLA_KAPSAMASI") else "DIGER")
        beklenen[t] = beklenen.get(t, 0) + n

    print(f"  denetleyiciye göre beklenen : {beklenen or '{}'}")
    print(f"  modelin ihlal ettikleri     : {m_sinif or '{}'}")

    if m_sinif != beklenen:
        eksik = {t: beklenen.get(t, 0) - m_sinif.get(t, 0)
                 for t in set(beklenen) | set(m_sinif)
                 if beklenen.get(t, 0) != m_sinif.get(t, 0)}
        print("\n  [HATA] Model ile denetleyici aynı şeyi söylemiyor:", eksik)
        print("         Pozitif fark = model GEVŞEK (denetleyicinin gördüğü ihlali")
        print("         model olurlu sayıyor) — en tehlikeli durum budur.")
        print("         Negatif fark = model gereksiz KATI.")
        for k in ihlal[:6]:
            print(f"         {sinif(k)}: {k}")
        return 1

    if not ihlal:
        print("\n  ✓ Geçerli plan modelin 'olurlu bölgesi' içinde.")
    else:
        print("\n  ✓ Model ile bağımsız denetleyici BİREBİR aynı ihlalleri görüyor.")
        print("    Referans plan temiz olmasa da bu, kodlamanın doğruluğunu gösterir:")
        print("    model ne gevşek ne fazla katı.")
    print("    CP-SAT doğru problemi çözecek.")

    if m.hedef is not None:
        print(f"\n  greedy planının model hedef değeri: {m.hedef.deger(atama):,.0f}")
        print("  (CP-SAT bunu aşamıyorsa greedy zaten optimuma çok yakın demektir)")

    # ---- 2. aşama: çözümden plan çıkarma yolu ----
    print("\n" + "-" * 64)
    print("  ÇÖZÜM → PLAN dönüşümü testi")
    print("-" * 64)

    class SahteCozucu:
        def Value(self, var):
            return int(round(atama.get(var.ad, 0)))

    geri = cpsat.plan_cikar(v, dv, SahteCozucu(), "DENGELI")
    ihl2 = Degerlendirici(girdi).calistir(geri)
    sert2 = sum(1 for i in ihl2 if i.tur == "SERT")
    beklenen_sert = len(ref_ihl)
    molasiz_sayi = sum(1 for a in geri["atamalar"]
                       if a["mola_dk"] >= 30 and not a.get("mola_saat"))

    print(f"  yeniden kurulan atama sayısı : {len(geri['atamalar'])} "
          f"(kaynak plan: {len(plan['atamalar'])})")
    print(f"  molası atanmamış vardiya     : {molasiz_sayi}  (0 olmalı)")
    print(f"  sert ihlal                   : {sert2}  "
          f"({beklenen_sert} olmalı — referansla aynı)")

    if (len(geri["atamalar"]) != len(plan["atamalar"]) or molasiz_sayi
            or sert2 != beklenen_sert):
        print("\n  [HATA] Toplu mola sayaçları kişi bazına doğru dağıtılmıyor.")
        for i in ihl2[:5]:
            if i.tur == "SERT":
                print(f"         {i.kod} {i.ekip} gün{i.gun} saat{i.saat}")
        return 1

    print("\n  ✓ Toplu sayaçlar kişi bazına sorunsuz dağıtılıyor;")
    print("    CP-SAT çözümü geçerli bir plan JSON'una dönüşecek.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
