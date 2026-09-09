#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planla.py — Kısıt tabanlı vardiya planlayıcı (sezgisel / greedy + yerel iyileştirme).

Girdi : girdi.json
Çıktı : plan_DENGELI.json · plan_KAPSAMA.json · plan_CALISAN.json  +  konsol raporu

Tasarım notu:
  Bu planlayıcı SERT kuralları "üretim anında" uygular — ihlalli bir atamayı
  hiç oluşturmaz. Bu yüzden onarım döngüsüne ihtiyaç duymaz.
  Doğruluğu, bağımsız yazılmış degerlendirici.py ile ayrıca denetlenir.

Kullanım:  python3 planla.py
"""

import json
import sys
import time
from datetime import date

from degerlendirici import Degerlendirici, ozet, sf, hucre, gunler_arasi

def onek(yol: str) -> str:
    """girdi_otel.json -> 'otel_'  ·  girdi.json -> ''  (çıktı dosyası öneki)"""
    import os
    b = os.path.basename(yol)
    if b.startswith("girdi_") and b.endswith(".json"):
        return b[6:-5] + "_"
    return ""

MAX_CALISMA_GUNU = 6          # en az 1 tam boş gün → HAFTA_TATILI garantisi
DINLENME_SAAT = 11


# --------------------------------------------------------------------

class Planlayici:
    def __init__(self, girdi, profil_adi, agirlik):
        self.g = girdi
        self.profil = profil_adi
        self.w = agirlik
        self.gun_sayisi = girdi["donem"]["gun"]
        self.plan_baslangic = date.fromisoformat(girdi["donem"]["baslangic"])

        self.calisanlar = [c for c in girdi["calisanlar"] if c["durum"] == "AKTIF"]
        self.cal = {c["id"]: c for c in self.calisanlar}
        self.ekipler = girdi["ekipler"]
        self.ekip = {e["id"]: e for e in self.ekipler}

        self.sablon = {}
        for s in girdi["sablonlar"]:
            self.sablon.setdefault(s["ekip"], []).append({
                "id": s["id"], "bas": sf(s["bas"]), "bit": sf(s["bit"]),
                "mola_dk": s["mola_dk"],
                "net": (sf(s["bit"]) - sf(s["bas"])) - s["mola_dk"] / 60.0,
            })

        self.talep = {}
        for t in girdi["talep"]:
            self.talep[(t["ekip"], t["gun"], t["saat"])] = [t["asgari"], t["hedef"]]

        # geçmişin son vardiya bitişi (mutlak saat, plan başlangıcına göre)
        self.son_bitis = {}
        for h in girdi["gecmis"]:
            d = (date.fromisoformat(h["tarih"]) - self.plan_baslangic).days
            bit = d * 24 + sf(h["bit"])
            if bit > self.son_bitis.get(h["calisan"], -1e9):
                self.son_bitis[h["calisan"]] = bit

        # profil bazlı fazla mesai toleransı (saat)
        self.fm_tolerans = {"KAPSAMA": 5.0, "DENGELI": 2.0, "CALISAN": 0.0}[profil_adi]

        # durum
        self.atamalar = []
        self.net = {c["id"]: 0.0 for c in self.calisanlar}       # haftalık net saat
        self.gunler = {c["id"]: set() for c in self.calisanlar}  # çalışılan günler
        self.blok = {c["id"]: [] for c in self.calisanlar}       # (abs_bas, abs_bit)
        self.kapsama = {}                                        # (ekip,gun,saat) -> kişi
        self.lider = {}                                          # (ekip,gun,saat) -> lider
        self.mola_zorlandi = 0                                   # güvenli mola saati yok
        _rol = next((k for k in girdi["kurallar"] if k["kod"] == "ROL_KAPSAMASI"), None)
        self.rol_asgari = _rol["param"]["asgari"] if _rol else 1
        self.son_sablon = {}                                     # kararlılık için

        # gece kuralları (7/24 operasyonlarda var, çağrı merkezinde yok)
        _g = next((k for k in girdi["kurallar"]
                   if k["kod"] == "GECE_VARDIYASI_AZAMI"), None)
        _a = next((k for k in girdi["kurallar"]
                   if k["kod"] == "ARDISIK_GECE_LIMIT"), None)
        self.gece_lim = _g["param"]["saat"] if _g else None
        self.gece_pen = ((int(sf(_g["param"]["bas"])), int(sf(_g["param"]["bit"])))
                         if _g else None)
        self.gece_ardisik = _a["param"]["ardisik"] if _a else None
        self.gece_gunleri = {}

        # --- müdürün manuel düzenlemeleri (yeniden planlama) ---
        self.kilitler = girdi.get("kilitler") or []
        self.yasak = {(y["calisan"], y["gun"]) for y in (girdi.get("yasaklar") or [])}
        # referans plan: "az değiştir" ödülü için
        self.referans = {(r["calisan"], r["gun"], r["sablon"])
                         for r in (girdi.get("referans_atamalar") or [])}
        self.w_kararli = girdi.get("kararlilik_odulu", 0.0)
        # Kilitli atamalar onarım/takas geçişlerinde KALDIRILAMAZ.
        self.kilit_anahtar = {(k["calisan"], k["gun"], k["sablon"])
                              for k in self.kilitler if k.get("sablon")}

        # SABİT ATAMALAR — hafta ortası yeniden planlama.
        # Pzt-Çar artık KARAR değil GERÇEK. Bunlar kapsamaya sayılır, haftalık
        # saat bütçesinden düşer, dinlenme kuralını bağlar; ama motorun
        # oynayabileceği bir değişken DEĞİLDİR. Gerçekleşen saatler şablona
        # uymayabilir (07:12-15:40) — sabit atama bunu doğal olarak kaldırır.
        self.sabit = girdi.get("sabit_atamalar") or []
        # DONMUŞ GÜNLER — geçmiş, planlamaya kapalı.
        # Bunu koymazsak motor, hastalık yüzünden oluşmuş DÜNKÜ boşlukları
        # doldurmaya çalışır: olmamış bir geçmişi yazar. Ölçüm bunu yakaladı.
        self.donmus = set(girdi.get("donmus_gunler") or [])

        # DEVİR YÜKÜ — haftalar arası adalet.
        # Motorun haftalar arası hafızası yoksa her hafta AYNI kararı verir:
        # girdi aynı, kural aynı, algoritma deterministik. Dört hafta sonra
        # aynı kişiler bütün geceleri tutmuş olur. Geçen haftaların birikimi
        # puanlamaya girerse yük kişiler arasında döner.
        # YETKİNLİK GEREKSİNİMLERİ — rol kapsamasının genel hâli
        _y = next((k for k in girdi["kurallar"]
                   if k["kod"] == "YETKINLIK_KAPSAMASI"), None)
        self.yetk_gerek = (_y["param"].get("gereksinimler") or []) if _y else []
        self.yetk = {}          # (ekip,gun,saat,yetkinlik) -> kişi

        self.devir_yuk = girdi.get("devir_yuk") or {}
        self.w_devir = girdi.get("devir_adalet_odulu", 0.0)
        self._gece_sablon = set()
        if self.gece_pen is not None:
            for ek, lst in self.sablon.items():
                for s in lst:
                    if self._gece_saati(s) > 0:
                        self._gece_sablon.add(s["id"])
        if self.devir_yuk:
            g = [v.get("gece", 0) for v in self.devir_yuk.values()]
            h = [v.get("hafta_sonu", 0) for v in self.devir_yuk.values()]
            self._ort_gece = sum(g) / max(1, len(g))
            self._ort_hs = sum(h) / max(1, len(h))
        else:
            self._ort_gece = self._ort_hs = 0.0

    # ---------------- kısıt kontrolü ----------------

    def uygun(self, c, s, gun):
        """SERT kuralların tamamı — ihlalli atama hiç üretilmez."""
        cid = c["id"]

        if c["ekip"] != s_ekip(s, self.sablon):
            return False
        if gun in self.gunler[cid]:                       # günde tek vardiya
            return False
        if (cid, gun) in self.yasak:                      # müdür çıkardı
            return False
        if gun in self.donmus:                            # geçmiş gün
            return False
        if len(self.gunler[cid]) >= MAX_CALISMA_GUNU:
            return False

        # SOZLESME_GECERLI
        if c.get("sozlesme_bitis"):
            if self.plan_baslangic.toordinal() + gun > date.fromisoformat(c["sozlesme_bitis"]).toordinal():
                return False

        # ONAYLI_IZIN — gece vardiyası iki güne dokunur, ikisi de bağlar
        dokunulan = gunler_arasi(gun, s["bas"], s["bit"])
        for iz in c.get("izinler", []):
            if iz["gun"] in dokunulan:
                return False

        # UYGUNLUK_TAKVIMI — her saat kendi gününde sınanır
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

        # GUNLUK_AZAMI
        if s["net"] > self.g_lim() + 1e-6:
            return False

        # GECE_VARDIYASI_AZAMI / ARDISIK_GECE_LIMIT (varsa)
        if self.gece_lim is not None:
            gece = self._gece_saati(s)
            if gece > 0:
                if gece - self._gece_mola(s) > self.gece_lim + 1e-6:
                    return False
                if self.gece_ardisik is not None:
                    onceki = self.gece_gunleri.get(cid, set())
                    art = 1
                    d = gun - 1
                    while d in onceki:
                        art += 1; d -= 1
                    d = gun + 1
                    while d in onceki:
                        art += 1; d += 1
                    if art > self.gece_ardisik:
                        return False

        # HAFTALIK_AZAMI + PART_TIME_LIMIT + profil toleransı
        yeni = self.net[cid] + s["net"]
        if yeni > self.h_lim() + 1e-6:
            return False
        sozlesme = c["sozlesme_dk_hafta"] / 60.0
        tavan = sozlesme if c["tur"] == "YARI_ZAMANLI" else sozlesme + self.fm_tolerans
        if yeni > tavan + 1e-6:
            return False

        # VARDIYA_ARASI_DINLENME (geçmiş dahil, iki yönlü)
        ab, at = gun * 24 + s["bas"], gun * 24 + s["bit"]
        onceki = self.son_bitis.get(cid, -1e9)
        if ab - onceki < DINLENME_SAAT - 1e-6:
            return False
        for pb, pt in self.blok[cid]:
            if pb >= at:
                if pb - at < DINLENME_SAAT - 1e-6:
                    return False
            elif pt <= ab:
                if ab - pt < DINLENME_SAAT - 1e-6:
                    return False
            else:
                return False                              # çakışma
        return True

    def _gece_mi(self, h: int) -> bool:
        b, t = self.gece_pen
        x = h % 24
        return (b <= x or x < t) if b > t else (b <= x < t)

    def _gece_saati(self, s) -> int:
        return sum(1 for h in range(int(s["bas"]), int(s["bit"])) if self._gece_mi(h))

    def _gece_mola(self, s) -> float:
        return 0.0        # mola saati atama anında belli değil; ihtiyatlı davran

    def g_lim(self):
        return next(k["param"]["saat"] for k in self.g["kurallar"] if k["kod"] == "GUNLUK_AZAMI")

    def h_lim(self):
        return next(k["param"]["saat"] for k in self.g["kurallar"] if k["kod"] == "HAFTALIK_AZAMI")

    # ---------------- puanlama ----------------

    def puan(self, c, s, gun, acik):
        cid = c["id"]
        sozlesme = c["sozlesme_dk_hafta"] / 60.0

        # kapsama katkısı
        kk = 0.0
        for saat in range(int(s["bas"]), int(s["bit"])):
            kk += acik.get(hucre(gun, saat), 0.0)
        kk /= max(1.0, s["bit"] - s["bas"])

        # adalet: sözleşmesine göre az yüklenmiş olan öne geçer
        doluluk = self.net[cid] / sozlesme if sozlesme else 1.0
        adalet = 1.0 - min(1.0, doluluk)

        # fazla mesai: sözleşmeyi aşmaya yaklaşan cezalanır
        asim = max(0.0, (self.net[cid] + s["net"]) - sozlesme)
        fm = 1.0 - min(1.0, asim / 4.0)

        # kararlılık: önceki günlerdeki başlangıç saatine yakınlık
        onceki_sab = self.son_sablon.get(cid)
        kararlilik = 1.0 if onceki_sab is None else \
            max(0.0, 1.0 - abs(onceki_sab - s["bas"]) / 8.0)

        # "az değiştir": referans planda da olan atama ödüllendirilir
        ayni = 1.0 if (cid, gun, s["id"]) in self.referans else 0.0

        # devir adaleti: geçmiş haftalarda az gece/hafta sonu almış olan öne geçer
        devir = 0.0
        if self.w_devir:
            r = self.devir_yuk.get(cid, {})
            if s["id"] in self._gece_sablon:
                devir += self._ort_gece - r.get("gece", 0)
            if gun >= 5:
                devir += self._ort_hs - r.get("hafta_sonu", 0)

        w = self.w
        return (w["kapsama"] * kk + w["adalet"] * adalet +
                w["fazla_mesai"] * fm + w["kararlilik"] * kararlilik
                + self.w_kararli * ayni + self.w_devir * devir)

    # ---------------- açık hesabı ----------------

    def acik_haritasi(self, ekip, gun, hedefe_kadar):
        """Açık haritası (gun, saat) anahtarlıdır.

        Gece vardiyası ertesi güne taştığı için, o gün başlayan bir vardiyanın
        katkısı iki güne yayılabilir. Bu yüzden harita gun ve gun+1'i kapsar.
        """
        acik = {}
        for g in (gun, gun + 1):
            if g >= self.gun_sayisi:
                continue
            for saat in range(24):
                t = self.talep.get((ekip, g, saat))
                if not t:
                    continue
                asgari, hedef = t
                m = self.kapsama.get((ekip, g, saat), 0)
                if m < asgari:
                    acik[(g, saat)] = 10.0            # sert açık — yüksek öncelik
                elif hedefe_kadar and m < hedef:
                    acik[(g, saat)] = 1.0
        return acik

    # ---------------- atama ----------------

    def ata(self, c, s, gun):
        cid = c["id"]
        a = {
            "id": f"A{len(self.atamalar)+1:05d}",
            "calisan": cid, "ekip": c["ekip"], "gun": gun,
            "bas": hs(s["bas"]), "bit": hs(s["bit"]),
            "mola_dk": s["mola_dk"], "mola_saat": None, "sablon": s["id"],
        }
        self.atamalar.append(a)
        self.net[cid] += s["net"]
        self.gunler[cid].add(gun)
        self.blok[cid].append((gun * 24 + s["bas"], gun * 24 + s["bit"]))
        self.son_sablon[cid] = s["bas"]
        if self.gece_lim is not None and self._gece_saati(s) > 0:
            self.gece_gunleri.setdefault(cid, set()).add(gun)
        lider_mi = "TAKIM_LIDERI" in c["roller"]
        yetk = c.get("yetkinlikler") or []
        for saat in range(int(s["bas"]), int(s["bit"])):
            g2, s2 = hucre(gun, saat)
            k = (c["ekip"], g2, s2)
            self.kapsama[k] = self.kapsama.get(k, 0) + 1
            if lider_mi:
                self.lider[k] = self.lider.get(k, 0) + 1
            for y in yetk:
                self.yetk[k + (y,)] = self.yetk.get(k + (y,), 0) + 1
        return a

    def kaldir(self, a):
        """Bir atamayı geri al — tüm sayaçlarıyla birlikte.

        Greedy'nin doğal eksiği: verdiği kararı geri alamaz. Liderler haftalık
        gün sınırına dayandığında açığı kapatmanın tek yolu, GEREKSİZ bir lider
        vardiyasını açığın olduğu yere taşımaktır. Takas için önce kaldırma
        gerekir.
        """
        if (a["calisan"], a["gun"], a["sablon"]) in self.kilit_anahtar:
            raise RuntimeError("kilitli atama kaldırılamaz: "
                               f"{a['calisan']} gün {a['gun']} {a['sablon']}")
        c = self.cal[a["calisan"]]
        cid = a["calisan"]
        ab, at = sf(a["bas"]), sf(a["bit"])
        self.atamalar.remove(a)
        self.net[cid] -= (at - ab) - a["mola_dk"] / 60.0
        self.gunler[cid].discard(a["gun"])
        try:
            self.blok[cid].remove((a["gun"] * 24 + ab, a["gun"] * 24 + at))
        except ValueError:
            pass
        lider_mi = "TAKIM_LIDERI" in c["roller"]
        yetk = c.get("yetkinlikler") or []
        for h in range(int(ab), int(at)):
            k = (a["ekip"],) + hucre(a["gun"], h)
            self.kapsama[k] = self.kapsama.get(k, 0) - 1
            if lider_mi:
                self.lider[k] = self.lider.get(k, 0) - 1
            for y in yetk:
                self.yetk[k + (y,)] = self.yetk.get(k + (y,), 0) - 1
        if self.gece_lim is not None and cid in self.gece_gunleri:
            self.gece_gunleri[cid].discard(a["gun"])

    def _gereksiz_mi(self, a) -> bool:
        """Bu lider vardiyası kaldırılırsa rol kapsaması bozulur mu?

        Müdürün kilitlediği atama asla 'gereksiz' değildir: onu taşımak,
        kullanıcının kararını sessizce geri almak olur. Bu kontrol olmadan
        lider takası geçişi kilitli atamayı kaldırıyordu (otel veri setinde
        KILIT_UYUMU ihlali olarak yakalandı).
        """
        if (a["calisan"], a["gun"], a["sablon"]) in self.kilit_anahtar:
            return False
        for h in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            k = (a["ekip"],) + hucre(a["gun"], h)
            if not self.talep.get(k):
                continue
            if self.lider.get(k, 0) - 1 < self.rol_asgari:
                return False
        return True

    def _lider_takasi(self, ek, gun, saat) -> bool:
        """Gereksiz bir lider vardiyasını, açığın olduğu saate taşı."""
        adaylar = []
        for bas_gun in (gun, gun - 1):
            if bas_gun < 0:
                continue
            for s in self.sablon[ek]:
                if any(hucre(bas_gun, h) == (gun, saat)
                       for h in range(int(s["bas"]), int(s["bit"]))):
                    adaylar.append((s, bas_gun))
        if not adaylar:
            return False
        mevcut = [a for a in self.atamalar
                  if a["ekip"] == ek
                  and "TAKIM_LIDERI" in self.cal[a["calisan"]]["roller"]]
        for a in mevcut:
            if not self._gereksiz_mi(a):
                continue
            c = self.cal[a["calisan"]]
            self.kaldir(a)
            for s, bas_gun in adaylar:
                if self.uygun(c, s, bas_gun):
                    self.ata(c, s, bas_gun)
                    return True
            self.ata(c, {"id": a["sablon"], "bas": sf(a["bas"]),
                         "bit": sf(a["bit"]), "mola_dk": a["mola_dk"],
                         "net": (sf(a["bit"]) - sf(a["bas"]))
                         - a["mola_dk"] / 60.0}, a["gun"])   # geri koy
        return False

    def asama_rol_onarim(self, tur=3):
        """Kalan rol açıklarını önce kişi ekleyerek, olmazsa TAKAS ile kapat."""
        for _ in range(tur):
            acik = [k for k in self.talep
                    if self.lider.get(k, 0) < self.rol_asgari]
            if not acik:
                return
            duzeldi = 0
            for ek, gun, saat in acik:
                if self._ek_kisi(ek, gun, saat, sadece_lider=True):
                    duzeldi += 1
                elif self._lider_takasi(ek, gun, saat):
                    duzeldi += 1
            if duzeldi == 0:
                return

    # ---------------- aşamalar ----------------

    def asama_lider(self, hedef=None, tur=12):
        """Her açık saatte en az `hedef` takım lideri bulunsun (ROL_KAPSAMASI).

        DİKKAT — gece vardiyası: bir günün 00:00–06:00 saatlerini kapsayan
        vardiya BİR ÖNCEKİ gün başlar. İlk sürüm yalnız o gün başlayan
        şablonlara bakıyordu, dolayısıyla 7/24 departmanlarda gecenin ilk
        yarısına hiç lider atayamıyordu. Aday başlangıç günü artık {gun, gun-1}.

        İKİNCİ GEÇİŞ (hedef = asgari+1): tek liderin bulunduğu bir saatte o
        lider molaya çıkarsa rol kapsaması düşer ve bunu mola aşamasında
        onarmak çoğu zaman imkânsızdır (lider sayısı azdır). Bu yüzden lider
        vardiyaları bilerek ÇAKIŞTIRILIR — molaya çıkacak yer açılsın diye.
        Bu geçiş 'elden geldiğince'dir; başarısızlığı plan üretimini durdurmaz.
        """
        if hedef is None:
            hedef = self.rol_asgari
        for e in self.ekipler:
            ek = e["id"]
            acilis, kapanis = int(sf(e["acilis"])), int(sf(e["kapanis"]))
            liderler = [c for c in self.calisanlar
                        if c["ekip"] == ek and "TAKIM_LIDERI" in c["roller"]]
            if not liderler:
                continue
            for gun in range(self.gun_sayisi):
                for _ in range(tur):
                    bos = [s for s in range(acilis, kapanis)
                           if self.talep.get((ek, gun, s))
                           and self.lider.get((ek, gun, s), 0) < hedef]
                    if not bos:
                        break
                    acik = {(gun, s): 1.0 for s in bos}
                    en_iyi = None
                    for bas_gun in (gun, gun - 1):
                        if bas_gun < 0:
                            continue
                        for s in self.sablon[ek]:
                            kapsar = sum(1 for x in range(int(s["bas"]), int(s["bit"]))
                                         if hucre(bas_gun, x) in acik)
                            if kapsar == 0:
                                continue
                            for c in liderler:
                                if not self.uygun(c, s, bas_gun):
                                    continue
                                # Kalan kapasitesi çok olan lider öne geçsin.
                                # Aksi hâlde greedy ilk günlerde liderleri
                                # tüketiyor ve haftanın son gününe lider
                                # kalmıyordu (D4, 6. gün sabahı).
                                kalan = (MAX_CALISMA_GUNU
                                         - len(self.gunler[c["id"]]))
                                p = (kapsar * 5 + kalan * 2.0
                                     + self.puan(c, s, bas_gun, acik) * 0.1)
                                if en_iyi is None or p > en_iyi[0]:
                                    en_iyi = (p, c, s, bas_gun)
                    if en_iyi is None:
                        break
                    self.ata(en_iyi[1], en_iyi[2], en_iyi[3])

    def asama_lider_mola_payi(self):
        """Molaya çıkacak yeri olmayan lider vardiyalarına çakışma ekle.

        Bir lider, vardiyasının HİÇBİR saatinde ikinci bir lider yoksa molaya
        çıkamaz — çıkarsa ROL_KAPSAMASI düşer. Bunu mola aşamasında onarmak
        mümkün değildir; önceden yer açmak gerekir.

        Geçiş HEDEFLİDİR: "her saatte 2 lider" gibi geniş bir hedef, lider
        kapasitesini boşuna tüketiyor ve başka saatlerde açık yaratıyordu
        (çağrı merkezi veri setinde 0 ihlalden 2 ihlale düşmüştü). Burada
        yalnız gerçekten sıkışmış vardiyalara dokunulur.
        """
        for a in list(self.atamalar):
            c = self.cal[a["calisan"]]
            if "TAKIM_LIDERI" not in c["roller"]:
                continue
            if a["mola_dk"] < 30:
                continue
            ek, gun = a["ekip"], a["gun"]
            saatler = range(int(sf(a["bas"])), int(sf(a["bit"])))
            if any(self.lider.get((ek,) + hucre(gun, h), 0) > self.rol_asgari
                   for h in saatler):
                continue                       # zaten çakışan lider var
            liderler = [x for x in self.calisanlar
                        if x["ekip"] == ek and "TAKIM_LIDERI" in x["roller"]
                        and x["id"] != a["calisan"]]
            en_iyi = None
            for bas_gun in (gun, gun - 1):
                if bas_gun < 0:
                    continue
                for s in self.sablon[ek]:
                    ortak = sum(1 for h in range(int(s["bas"]), int(s["bit"]))
                                if hucre(bas_gun, h) in
                                {hucre(gun, x) for x in saatler})
                    if ortak == 0:
                        continue
                    for x in liderler:
                        if not self.uygun(x, s, bas_gun):
                            continue
                        p = ortak * 5 - self.net[x["id"]] * 0.01
                        if en_iyi is None or p > en_iyi[0]:
                            en_iyi = (p, x, s, bas_gun)
            if en_iyi:
                self.ata(en_iyi[1], en_iyi[2], en_iyi[3])
                continue

            # Boş lider yok → GEREKSİZ bir lider vardiyasını buraya taşı.
            hedef_hucre = {hucre(gun, x) for x in saatler}
            adaylar = []
            for bas_gun in (gun, gun - 1):
                if bas_gun < 0:
                    continue
                for s in self.sablon[ek]:
                    ortak = sum(1 for h in range(int(s["bas"]), int(s["bit"]))
                                if hucre(bas_gun, h) in hedef_hucre)
                    if ortak:
                        adaylar.append((ortak, s, bas_gun))
            adaylar.sort(key=lambda z: -z[0])
            if not adaylar:
                continue
            for b in [z for z in self.atamalar
                      if z is not a and z["ekip"] == ek
                      and "TAKIM_LIDERI" in self.cal[z["calisan"]]["roller"]]:
                if not self._gereksiz_mi(b):
                    continue
                cb = self.cal[b["calisan"]]
                eski = dict(b)
                self.kaldir(b)
                yerlesti = False
                for _o, s, bas_gun in adaylar:
                    if self.uygun(cb, s, bas_gun):
                        self.ata(cb, s, bas_gun)
                        yerlesti = True
                        break
                if yerlesti:
                    break
                self.ata(cb, {"id": eski["sablon"], "bas": sf(eski["bas"]),
                              "bit": sf(eski["bit"]), "mola_dk": eski["mola_dk"],
                              "net": (sf(eski["bit"]) - sf(eski["bas"]))
                              - eski["mola_dk"] / 60.0}, eski["gun"])

    def asama_yetkinlik(self, tur=14):
        """Her gerekli saatte istenen yetkinlikte kişi bulunsun.

        ROL_KAPSAMASI ile aynı mekanizma; tek fark çalışanın hangi özelliğine
        bakıldığı. Aynı gece-vardiyası tuzağı burada da var: bir günün erken
        saatlerini kapsayan vardiya bir ÖNCEKİ gün başlar.
        """
        for g in self.yetk_gerek:
            ek, yet, asgari = g["ekip"], g["yetkinlik"], g.get("asgari", 1)
            saatler = g.get("saatler")
            havuz = [c for c in self.calisanlar
                     if c["ekip"] == ek and yet in (c.get("yetkinlikler") or [])]
            if not havuz:
                continue
            for gun in range(self.gun_sayisi):
                for _ in range(tur):
                    bos = [s for s in range(24)
                           if self.talep.get((ek, gun, s))
                           and (saatler is None or s in saatler)
                           and self.yetk.get((ek, gun, s, yet), 0) < asgari]
                    if not bos:
                        break
                    acik = {(gun, s): 1.0 for s in bos}
                    en_iyi = None
                    for bas_gun in (gun, gun - 1):
                        if bas_gun < 0:
                            continue
                        for s in self.sablon[ek]:
                            kapsar = sum(1 for x in range(int(s["bas"]), int(s["bit"]))
                                         if hucre(bas_gun, x) in acik)
                            if kapsar == 0:
                                continue
                            for c in havuz:
                                if not self.uygun(c, s, bas_gun):
                                    continue
                                kalan = MAX_CALISMA_GUNU - len(self.gunler[c["id"]])
                                p = (kapsar * 5 + kalan * 2.0
                                     + self.puan(c, s, bas_gun, acik) * 0.1)
                                if en_iyi is None or p > en_iyi[0]:
                                    en_iyi = (p, c, s, bas_gun)
                    if en_iyi is None:
                        break
                    self.ata(en_iyi[1], en_iyi[2], en_iyi[3])

    def asama_kapsama(self, hedefe_kadar):
        for gun in range(self.gun_sayisi):
            for e in self.ekipler:
                ek = e["id"]
                havuz = [c for c in self.calisanlar if c["ekip"] == ek]
                for _ in range(400):
                    acik = self.acik_haritasi(ek, gun, hedefe_kadar)
                    if not acik:
                        break
                    en_iyi = None
                    for s in self.sablon[ek]:
                        kk = sum(acik.get(hucre(gun, x), 0.0)
                                 for x in range(int(s["bas"]), int(s["bit"])))
                        if kk <= 0:
                            continue
                        for c in havuz:
                            if not self.uygun(c, s, gun):
                                continue
                            p = self.puan(c, s, gun, acik)
                            if en_iyi is None or p > en_iyi[0]:
                                en_iyi = (p, c, s)
                    if en_iyi is None:
                        break
                    self.ata(en_iyi[1], en_iyi[2], gun)

    def asama_mola(self):
        """Molayı, asgari kapsamayı VE lider kapsamasını bozmayacak bir saate koy.

        Mola bir kişiyi o saat için kapsamadan düşürür. Önceki sürüm yalnızca
        'en bol saat'e bakıyordu; bolluk negatifse yine oraya koyuyordu. Artık
        güvenli saat yoksa mola penceresi tüm vardiyaya genişletilir, o da
        yetmezse mola yerleştirilemedi olarak sayılır (rapora yazılır).
        """
        self.mola_zorlandi = 0
        # Liderler önce: kıt kaynak oldukları için güvenli saatleri onlar seçsin.
        sirali = sorted(
            self.atamalar,
            key=lambda a: (0 if "TAKIM_LIDERI" in self.cal[a["calisan"]]["roller"] else 1,
                           -(sf(a["bit"]) - sf(a["bas"]))))
        for a in sirali:
            if a["mola_dk"] < 30:
                continue
            c = self.cal[a["calisan"]]
            lider_mi = "TAKIM_LIDERI" in c["roller"]
            b, t = sf(a["bas"]), sf(a["bit"])

            dar = [s for s in range(int(b) + 2, max(int(b) + 2, int(t - 1.5)) + 1)
                   if b <= s < t]
            genis = [s for s in range(int(b), int(t)) if b <= s < t]

            en_iyi = None
            for adaylar in (dar, genis):
                guvenli = []
                for s in adaylar:
                    g2, s2 = hucre(a["gun"], s)
                    k = (a["ekip"], g2, s2)
                    asgari = self.talep.get(k, (0, 0))[0]
                    if self.kapsama.get(k, 0) - 1 < asgari:
                        continue
                    if lider_mi and self.lider.get(k, 0) - 1 < self.rol_asgari:
                        continue
                    guvenli.append((self.kapsama.get(k, 0) - asgari, -s, s))
                if guvenli:
                    en_iyi = max(guvenli)[2]
                    break

            if en_iyi is None:
                # Güvenli saat yok. Yedek seçim LİDER KAPSAMASINI korumayı
                # önceler: eksik kalan kişiyi sonradan eklemek kolay, eksik
                # kalan lideri eklemek çok zor (lider sayısı azdır).
                self.mola_zorlandi += 1
                if not genis:
                    continue
                bosluk = (lambda s: self.kapsama.get((a["ekip"],) + hucre(a["gun"], s), 0)
                          - self.talep.get((a["ekip"],) + hucre(a["gun"], s), (0, 0))[0])
                lider_korur = [s for s in genis
                               if not lider_mi
                               or self.lider.get((a["ekip"],) + hucre(a["gun"], s), 0) - 1
                               >= self.rol_asgari]
                en_iyi = max(lider_korur or genis, key=bosluk)

            a["mola_saat"] = hs(float(en_iyi))
            k = (a["ekip"],) + hucre(a["gun"], en_iyi)
            self.kapsama[k] = self.kapsama.get(k, 0) - 1
            if lider_mi:
                self.lider[k] = self.lider.get(k, 0) - 1

    def _mola_guvenli(self, a, s, lider_mi):
        g2, s2 = hucre(a["gun"], s)
        k = (a["ekip"], g2, s2)
        asgari = self.talep.get(k, (0, 0))[0]
        if self.kapsama.get(k, 0) - 1 < asgari:
            return False
        if lider_mi and self.lider.get(k, 0) - 1 < self.rol_asgari:
            return False
        # molaya çıkan kişi tek yetkinlik sahibiyse kapsama düşer
        c = self.cal.get(a["calisan"])
        if c and self.yetk_gerek:
            sahip = set(c.get("yetkinlikler") or [])
            for g in self.yetk_gerek:
                if g["ekip"] != a["ekip"] or g["yetkinlik"] not in sahip:
                    continue
                if g.get("saatler") is not None and s2 not in g["saatler"]:
                    continue
                if self.yetk.get(k + (g["yetkinlik"],), 0) - 1 < g.get("asgari", 1):
                    return False
        return True

    def asama_mola_onarim(self, tur_sayisi: int = 4):
        """Molalardan doğan kapsama/lider açıklarını molayı taşıyarak kapat.

        asama_mola tek geçişlidir: erken yerleştirilen bir mola, sonraki bir
        molanın tüm güvenli saatlerini kapatabilir (iki liderin aynı saatte
        çakışması gibi). Bu geçiş, açık veren saatteki molaları tek tek başka
        bir güvenli saate taşır. Taşımak kimseye vardiya eklemez; yalnız mola
        saatini değiştirir, o yüzden diğer sert kuralları etkilemez.
        """
        for _ in range(tur_sayisi):
            acik = []
            for (ekip, gun, saat), (asgari, _h) in self.talep.items():
                k = (ekip, gun, saat)
                if self.kapsama.get(k, 0) < asgari:
                    acik.append((k, "KAPSAMA"))
                elif self.lider.get(k, 0) < self.rol_asgari:
                    acik.append((k, "LIDER"))
            if not acik:
                return
            tasindi = 0
            for (ekip, gun, saat), tip in acik:
                for a in self.atamalar:
                    if a["ekip"] != ekip or a["gun"] != gun:
                        continue
                    ms = a.get("mola_saat")
                    if ms is None or hucre(a["gun"], int(sf(ms))) != (gun, saat):
                        continue
                    c = self.cal[a["calisan"]]
                    lider_mi = "TAKIM_LIDERI" in c["roller"]
                    if tip == "LIDER" and not lider_mi:
                        continue
                    b, t = sf(a["bas"]), sf(a["bit"])
                    # molayı geçici olarak kaldır, sonra güvenli saat ara
                    eski = (ekip, gun, saat)
                    self.kapsama[eski] = self.kapsama.get(eski, 0) + 1
                    if lider_mi:
                        self.lider[eski] = self.lider.get(eski, 0) + 1
                    aday = [s for s in range(int(b), int(t))
                            if hucre(a["gun"], s) != (gun, saat)
                            and self._mola_guvenli(a, s, lider_mi)]
                    if aday:
                        yeni = max(aday, key=lambda s: self.kapsama.get(
                            (ekip,) + hucre(a["gun"], s), 0)
                            - self.talep.get((ekip,) + hucre(a["gun"], s), (0, 0))[0])
                        a["mola_saat"] = hs(float(yeni))
                        ky = (ekip,) + hucre(a["gun"], yeni)
                        self.kapsama[ky] = self.kapsama.get(ky, 0) - 1
                        if lider_mi:
                            self.lider[ky] = self.lider.get(ky, 0) - 1
                        tasindi += 1
                        break
                    # taşınamadı: molayı yerinde bırak
                    self.kapsama[eski] = self.kapsama.get(eski, 0) - 1
                    if lider_mi:
                        self.lider[eski] = self.lider.get(eski, 0) - 1
                else:
                    # hiçbir mola taşınamadı → o saate ek kişi ekle
                    if self._ek_kisi(ekip, gun, saat, sadece_lider=(tip == "LIDER")):
                        tasindi += 1
            if tasindi == 0:
                return

    def _ek_kisi(self, ekip, gun, saat, sadece_lider: bool) -> bool:
        """Molaların kapattığı açığı, o saati kapsayan yeni bir vardiya ile aç.

        Mola taşımanın çözemediği tek durum, o saatte tek kişinin (çoğunlukla
        tek liderin) bulunmasıdır: molası nereye konursa konsun açık doğar.
        Tek çare kişi sayısını artırmaktır — gerçek bir planlamacının yaptığı da
        budur.
        """
        havuz = [c for c in self.calisanlar
                 if c["ekip"] == ekip
                 and (not sadece_lider or "TAKIM_LIDERI" in c["roller"])]
        en_iyi = None
        # Hücreyi kapsayan vardiya, o gün ya da bir önceki gün başlamış olabilir
        # (gece vardiyası). İkisini de dene.
        for bas_gun in (gun, gun - 1):
            if bas_gun < 0:
                continue
            for s in self.sablon[ekip]:
                if not any(hucre(bas_gun, h) == (gun, saat)
                           for h in range(int(s["bas"]), int(s["bit"]))):
                    continue
                for c in havuz:
                    if not self.uygun(c, s, bas_gun):
                        continue
                    p = -self.net[c["id"]]      # en az yüklü kişi
                    if en_iyi is None or p > en_iyi[0]:
                        en_iyi = (p, c, s, bas_gun)
        if en_iyi is None:
            return False
        gun = en_iyi[3]
        a = self.ata(en_iyi[1], en_iyi[2], gun)
        lider_mi = "TAKIM_LIDERI" in en_iyi[1]["roller"]
        if a["mola_dk"] >= 30:
            b, t = sf(a["bas"]), sf(a["bit"])
            aday = [x for x in range(int(b), int(t))
                    if self._mola_guvenli(a, x, lider_mi)]
            if aday:
                yeni = max(aday, key=lambda x: self.kapsama.get(
                    (ekip,) + hucre(gun, x), 0)
                    - self.talep.get((ekip,) + hucre(gun, x), (0, 0))[0])
                a["mola_saat"] = hs(float(yeni))
                k = (ekip,) + hucre(gun, yeni)
                self.kapsama[k] = self.kapsama.get(k, 0) - 1
                if lider_mi:
                    self.lider[k] = self.lider.get(k, 0) - 1
        return True

    def asama_sabit(self):
        """Gerçekleşmiş atamaları plana yerleştir — bunlar olmuş bitmiş."""
        for a in self.sabit:
            c = self.cal.get(a["calisan"])
            if not c or a["gun"] in self.gunler[c["id"]]:
                continue
            b, t = sf(a["bas"]), sf(a["bit"])
            s = {"id": a.get("sablon", "GERCEKLESEN"), "bas": b, "bit": t,
                 "mola_dk": a.get("mola_dk", 0),
                 "net": (t - b) - a.get("mola_dk", 0) / 60.0}
            yeni = self.ata(c, s, a["gun"])
            if a.get("mola_saat"):
                yeni["mola_saat"] = a["mola_saat"]
                k = (c["ekip"],) + hucre(a["gun"], int(sf(a["mola_saat"])))
                self.kapsama[k] = self.kapsama.get(k, 0) - 1
                if "TAKIM_LIDERI" in c["roller"]:
                    self.lider[k] = self.lider.get(k, 0) - 1
            self.kilit_anahtar.add((c["id"], a["gun"], s["id"]))

    def asama_kilit(self):
        """Müdürün kilitlediği atamaları önce yerleştir — pazarlık konusu değil."""
        for k in self.kilitler:
            c = self.cal.get(k["calisan"])
            if not c:
                continue
            s = next((x for x in self.sablon.get(c["ekip"], [])
                      if x["id"] == k["sablon"]), None)
            if s is None:
                continue
            # uygun() kontrolünden GEÇMEZ: kilit, kuralların değil müdürün
            # kararıdır. Kural ihlali doğuruyorsa değerlendirici söyler —
            # sessizce görmezden gelmek yerine görünür olsun.
            if k["gun"] not in self.gunler[c["id"]]:
                self.ata(c, s, k["gun"])

    def calistir(self):
        t0 = time.time()
        self.asama_sabit()
        self.asama_kilit()
        self.asama_lider()                       # 1) her saatte en az 1 lider
        self.asama_yetkinlik()                   # 1b) gerekli yetkinlikler
        self.asama_kapsama(hedefe_kadar=False)   # önce asgari
        self.asama_kapsama(hedefe_kadar=True)    # sonra hedefe doğru
        self.asama_lider_mola_payi()             # 2) molaya çıkacak yer aç
        self.asama_rol_onarim()                  # 3) kalan rol açıkları: takas
        self.asama_mola()
        self.asama_mola_onarim()
        self.sure = time.time() - t0
        return {"profil": self.profil, "atamalar": self.atamalar}


def s_ekip(s, sablon_map):
    for ek, lst in sablon_map.items():
        if any(x["id"] == s["id"] for x in lst):
            return ek
    return None


def hs(x: float) -> str:
    h, m = int(x), int(round((x - int(x)) * 60))
    return f"{h:02d}:{m:02d}"


# --------------------------------------------------------------------
# Metrikler
# --------------------------------------------------------------------

def metrikler(girdi, plan, d: Degerlendirici):
    A = plan["atamalar"]
    var = {}
    for a in A:
        for s in range(int(sf(a["bas"])), int(sf(a["bit"]))):
            if a.get("mola_saat") and int(sf(a["mola_saat"])) == s:
                continue
            g2, s2 = hucre(a["gun"], s)
            k = (a["ekip"], g2, s2)
            var[k] = var.get(k, 0) + 1
    for h in girdi["gecmis"]:                      # devir vardiyaları
        c = next((x for x in girdi["calisanlar"] if x["id"] == h["calisan"]), None)
        if not c:
            continue
        d0 = (date.fromisoformat(h["tarih"])
              - date.fromisoformat(girdi["donem"]["baslangic"])).days
        for x in range(int(sf(h["bas"])), int(sf(h["bit"]))):
            hh = d0 * 24 + x
            if 0 <= hh < girdi["donem"]["gun"] * 24:
                k = (c["ekip"], hh // 24, hh % 24)
                var[k] = var.get(k, 0) + 1

    hedef_top = asgari_top = 0
    hedef_kar = asgari_kar = 0
    for t in girdi["talep"]:
        k = (t["ekip"], t["gun"], t["saat"])
        m = var.get(k, 0)
        hedef_top += t["hedef"]; asgari_top += t["asgari"]
        hedef_kar += min(m, t["hedef"]); asgari_kar += min(m, t["asgari"])

    net = {}
    for a in A:
        net[a["calisan"]] = net.get(a["calisan"], 0) + d.net_saat(a)

    fm = 0.0
    for cid, sa in net.items():
        c = d.calisan[cid]
        fm += max(0.0, sa - c["sozlesme_dk_hafta"] / 60.0)

    aktif = [c for c in girdi["calisanlar"] if c["durum"] == "AKTIF"]
    from statistics import pstdev
    gruplar = {}
    for c in aktif:
        gruplar.setdefault((c["ekip"], c["tur"]), []).append(net.get(c["id"], 0.0))
    sapmalar = [pstdev(v) for v in gruplar.values() if len(v) >= 3]
    adalet = sum(sapmalar) / len(sapmalar) if sapmalar else 0.0

    return {
        "atama": len(A),
        "calisan": len(net),
        "toplam_net_saat": round(sum(net.values()), 1),
        "asgari_karsilama": asgari_kar / asgari_top,
        "hedef_karsilama": hedef_kar / hedef_top,
        "eksik_kisi_saat": hedef_top - hedef_kar,
        "fazla_mesai_saat": round(fm, 1),
        "adalet_sapma": round(adalet, 2),
    }


def fark(p1, p2):
    a = {(x["calisan"], x["gun"], x["bas"]) for x in p1["atamalar"]}
    b = {(x["calisan"], x["gun"], x["bas"]) for x in p2["atamalar"]}
    return len(a ^ b) / max(1, len(a | b))


# --------------------------------------------------------------------

def main():
    yol = sys.argv[1] if len(sys.argv) > 1 else "girdi.json"
    p_onek = onek(yol)
    girdi = json.load(open(yol, encoding="utf-8"))
    d = Degerlendirici(girdi)

    profiller = dict(girdi["hedef_profilleri"])
    sonuc = {}
    for ad, w in profiller.items():
        w = dict(w)
        w.setdefault("kararlilik", w.pop("tercih", 5))
        p = Planlayici(girdi, ad, w)
        plan = p.calistir()
        json.dump(plan, open(f"plan_{p_onek}{ad}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

        ih = d.calistir(plan)                       # BAĞIMSIZ doğrulama
        o = ozet(ih)
        m = metrikler(girdi, plan, d)
        sonuc[ad] = {"plan": plan, "ihlal": ih, "ozet": o, "metrik": m, "sure": p.sure}

        print(f"\n=== {ad} ===  ({p.sure:.1f} sn)")
        print(f"  atama            : {m['atama']}  ({m['calisan']} çalışan, {m['toplam_net_saat']} net saat)")
        print(f"  asgari karşılama : %{100*m['asgari_karsilama']:.1f}")
        print(f"  hedef karşılama  : %{100*m['hedef_karsilama']:.1f}   (eksik {m['eksik_kisi_saat']} kişi-saat)")
        print(f"  fazla mesai      : {m['fazla_mesai_saat']} sa")
        print(f"  adalet (σ)       : {m['adalet_sapma']} sa")
        print(f"  SERT İHLAL       : {o['sert']}")
        print(f"  yumuşak uyarı    : {o['yumusak']}")
        if o["kod_bazinda"]:
            for kod, n in sorted(o["kod_bazinda"].items(), key=lambda x: -x[1])[:6]:
                print(f"      {kod:26s} {n}")

    print("\n=== PLAN FARKLARI ===")
    adlar = list(sonuc)
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            f = fark(sonuc[adlar[i]]["plan"], sonuc[adlar[j]]["plan"])
            print(f"  {adlar[i]:8s} ↔ {adlar[j]:8s} : %{100*f:.1f} atama farklı")

    json.dump(
        {ad: {"metrik": s["metrik"], "ozet": s["ozet"], "sure_sn": round(s["sure"], 2)}
         for ad, s in sonuc.items()},
        open(f"{p_onek}sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
