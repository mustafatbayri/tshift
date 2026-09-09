#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
degerlendirici.py — Bağımsız kural değerlendiricisi.

Bir planı 17 çekirdek kurala göre denetler ve ihlal listesi üretir.
Planı ÜRETEN kodla ortak hiçbir mantığı yoktur — kasıtlı olarak ayrı yazılmıştır.
Plancıyı yanıltan bir hata bu dosyayı yanıltmasın diye.

Kullanım (tek başına):  python3 degerlendirici.py girdi.json plan.json
"""

import json
import sys
from datetime import date
from statistics import pstdev

# --------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------

def sf(s: str) -> float:
    """'08:30' -> 8.5   ·  '24:00' -> 24.0"""
    h, m = s.split(":")
    return int(h) + int(m) / 60.0


def ss(x: float) -> str:
    h = int(x) % 24 if x < 24 else 24
    m = int(round((x - int(x)) * 60))
    return f"{int(x):02d}:{m:02d}" if x >= 24 else f"{h:02d}:{m:02d}"


# --------------------------------------------------------------------
# Gün aşan vardiyalar (otel / 7-24 operasyonlar)
# --------------------------------------------------------------------
#
# Bir gece vardiyası 23:00'te başlayıp ertesi sabah 07:00'de biter. Bunu
# "bit < bas" diye kodlarsak her saat hesabı negatife düşer. Bunun yerine
# bitişi GENİŞLETİLMİŞ saatle yazıyoruz: 23:00 -> "31:00". Böylece süre,
# çakışma, dinlenme gibi tüm aritmetik olduğu gibi çalışır; yalnız kapsama
# sayarken 24'ü aşan saatleri ertesi günün hücresine eşlemek gerekir.
#
# Mola saati de aynı gösterimi kullanır: gece 03:00'teki mola "27:00".

def hucreler(gun: int, bas: float, bit: float):
    """Vardiyanın kapsadığı (gun, saat) hücrelerini üret; taşma ertesi güne."""
    for h in range(int(bas), int(bit)):
        yield (gun + h // 24, h % 24)


def hucre(gun: int, h: int):
    """Genişletilmiş saati (gun, saat) hücresine çevir."""
    return (gun + h // 24, h % 24)


def gunler_arasi(gun: int, bas: float, bit: float):
    """Vardiyanın dokunduğu takvim günleri (gece vardiyası iki gün sürer)."""
    return sorted({gun + h // 24 for h in range(int(bas), max(int(bas) + 1, int(bit)))})


class Ihlal:
    __slots__ = ("kod", "tur", "calisan", "ekip", "gun", "saat", "beklenen", "gercek", "mesaj")

    def __init__(self, kod, tur, mesaj, calisan=None, ekip=None, gun=None, saat=None,
                 beklenen=None, gercek=None):
        self.kod, self.tur, self.mesaj = kod, tur, mesaj
        self.calisan, self.ekip, self.gun, self.saat = calisan, ekip, gun, saat
        self.beklenen, self.gercek = beklenen, gercek

    def dict(self):
        return {k: getattr(self, k) for k in self.__slots__ if getattr(self, k) is not None}


# --------------------------------------------------------------------
# Ana değerlendirici
# --------------------------------------------------------------------

class Degerlendirici:
    def __init__(self, girdi: dict):
        self.g = girdi
        self.gun_sayisi = girdi["donem"]["gun"]
        self.plan_baslangic = date.fromisoformat(girdi["donem"]["baslangic"])
        self.calisan = {c["id"]: c for c in girdi["calisanlar"]}
        self.ekip = {e["id"]: e for e in girdi["ekipler"]}
        self.kural = {k["kod"]: k for k in girdi["kurallar"]}

        # talep sözlüğü: (ekip, gun, saat) -> (asgari, hedef)
        self.talep = {}
        for t in girdi["talep"]:
            self.talep[(t["ekip"], t["gun"], t["saat"])] = (t["asgari"], t["hedef"])

        # geçmiş: calisan -> [(abs_bas, abs_bit)]
        self.gecmis = {}
        for h in girdi["gecmis"]:
            d = (date.fromisoformat(h["tarih"]) - self.plan_baslangic).days
            self.gecmis.setdefault(h["calisan"], []).append(
                (d * 24 + sf(h["bas"]), d * 24 + sf(h["bit"]))
            )
        for v in self.gecmis.values():
            v.sort()

    # ---------------- yardımcı hesaplar ----------------

    @staticmethod
    def net_saat(a) -> float:
        """Ara dinlenme hariç fiili çalışma süresi."""
        return (sf(a["bit"]) - sf(a["bas"])) - a.get("mola_dk", 0) / 60.0

    @staticmethod
    def brut_saat(a) -> float:
        return sf(a["bit"]) - sf(a["bas"])

    def gerekli_mola(self, brut: float) -> int:
        for alt, ust, dk in self.kural["MOLA_HAKKI"]["param"]["bantlar"]:
            if alt < brut <= ust:
                return dk
        return 0

    @staticmethod
    def kapsiyor(a, saat: int) -> bool:
        return sf(a["bas"]) <= saat < sf(a["bit"])

    @staticmethod
    def molada(a, saat: int) -> bool:
        ms = a.get("mola_saat")
        return ms is not None and int(sf(ms)) == saat

    # ---------------- kurallar ----------------

    def calistir(self, plan: dict):
        A = plan["atamalar"]
        ih = []
        ih += self._uygunluk(A)
        ih += self._cakisma(A)
        ih += self._sure_limitleri(A)
        ih += self._dinlenme(A)
        ih += self._hafta_tatili(A)
        ih += self._mola_hakki(A)
        ih += self._gece(A)
        ih += self._duzenleme(A)
        ih += self._yetkinlik(A)
        ih += self._kapsama(A)
        ih += self._yumusak(A)
        return ih

    # -- KILIT_UYUMU: müdürün manuel düzenlemeleri
    def _duzenleme(self, A):
        """Müdürün elle yaptığı düzenlemeler plana AYNEN yansımış mı?

        Yeniden planlamada en sinsi hata, motorun müdürün kararını sessizce
        geri almasıdır: kişiyi cumadan çıkarırsınız, motor 'daha iyi' bulup
        geri koyar. Kullanıcı güvenini bir kerede bitiren şey budur, o yüzden
        SERT kural olarak denetlenir — motorun kendi sözüne değil.
        """
        ih = []
        kilit = self.g.get("kilitler") or []
        yasak = self.g.get("yasaklar") or []
        if not kilit and not yasak:
            return ih

        var = {(a["calisan"], a["gun"], a["sablon"]) for a in A}
        gunler = {(a["calisan"], a["gun"]) for a in A}

        for k in kilit:
            if (k["calisan"], k["gun"], k["sablon"]) not in var:
                ih.append(Ihlal("KILIT_UYUMU", "SERT",
                                "Kilitli atama planda yok",
                                calisan=k["calisan"], gun=k["gun"],
                                beklenen=k["sablon"]))
        for y in yasak:
            if (y["calisan"], y["gun"]) in gunler:
                ih.append(Ihlal("KILIT_UYUMU", "SERT",
                                "Müdürün çıkardığı kişi plana geri konmuş",
                                calisan=y["calisan"], gun=y["gun"]))
        return ih

    # -- YETKINLIK_KAPSAMASI
    def _yetkinlik(self, A):
        """Belirli saatlerde belirli yetkinlikte en az N kişi sahada olmalı.

        Bu, ROL_KAPSAMASI ile AYNI mekanizmadır — tek fark çalışanın hangi
        özelliğine bakıldığıdır (rol mü, yetkinlik mi). Ürün tarafında iki
        ayrı kural değil, tek kural tipi + parametre olarak tasarlanmalıdır.
        Burada ikisi ayrı duruyor çünkü kural havuzu geriye dönük uyumlu
        kalsın istedim; motor açısından fark yok.
        """
        ih = []
        k = self.kural.get("YETKINLIK_KAPSAMASI")
        if not k:
            return ih
        gerekler = k["param"].get("gereksinimler") or []
        if not gerekler:
            return ih

        # (ekip, gun, saat, yetkinlik) -> molada olmayan kişi sayısı
        say = {}
        for a in A:
            c = self.calisan.get(a["calisan"])
            if not c:
                continue
            yet = c.get("yetkinlikler") or []
            if not yet:
                continue
            for s in range(int(sf(a["bas"])), int(sf(a["bit"]))):
                if self.molada(a, s):
                    continue
                g2, s2 = hucre(a["gun"], s)
                for y in yet:
                    say[(a["ekip"], g2, s2, y)] = say.get((a["ekip"], g2, s2, y), 0) + 1
        # devir vardiyaları da sahada sayılır
        for cid, araliklar in self.gecmis.items():
            c = self.calisan.get(cid)
            if not c or not c.get("yetkinlikler"):
                continue
            for ab, at in araliklar:
                for h in range(int(ab), int(at)):
                    if not (0 <= h < self.gun_sayisi * 24):
                        continue
                    for y in c["yetkinlikler"]:
                        k2 = (c["ekip"], h // 24, h % 24, y)
                        say[k2] = say.get(k2, 0) + 1

        for g in gerekler:
            ekip, yet, asgari = g["ekip"], g["yetkinlik"], g.get("asgari", 1)
            saatler = g.get("saatler")
            for (e2, gun, saat), _t in self.talep.items():
                if e2 != ekip:
                    continue
                if saatler is not None and saat not in saatler:
                    continue
                m = say.get((ekip, gun, saat, yet), 0)
                if m < asgari:
                    ih.append(Ihlal("YETKINLIK_KAPSAMASI", "SERT",
                                    f"{yet} yetkinliği sahada yok",
                                    ekip=ekip, gun=gun, saat=saat,
                                    beklenen=f"{asgari}×{yet}", gercek=m))
        return ih

    # -- GECE_VARDIYASI_AZAMI / ARDISIK_GECE_LIMIT
    def _gece(self, A):
        """7/24 operasyonlara özgü iki kural. Kural setinde yoksa çalışmaz.

        GECE_VARDIYASI_AZAMI, İş Kanunu md.69'a dayanır: işçilerin gece
        çalışması 7,5 saati geçemez. 'Gece' penceresi parametredir (20:00–06:00).
        Çağrı merkezi kural setinde bu kurallar yok; aynı kod iki sektörde
        çalışsın diye kurallar veriden gelir, koddan değil.
        """
        ih = []
        kg = self.kural.get("GECE_VARDIYASI_AZAMI")
        ka = self.kural.get("ARDISIK_GECE_LIMIT")
        if not kg and not ka:
            return ih

        def gece_saati(h_mutlak: int, pen) -> bool:
            s = h_mutlak % 24
            b, t = pen
            return (b <= s or s < t) if b > t else (b <= s < t)

        if kg:
            p = kg["param"]
            pen = (int(sf(p["bas"])), int(sf(p["bit"])))
            lim = p["saat"]
            for a in A:
                ab, at = sf(a["bas"]), sf(a["bit"])
                gece = sum(1 for h in range(int(ab), int(at)) if gece_saati(h, pen))
                if gece == 0:
                    continue
                mola_g = 0
                ms = a.get("mola_saat")
                if ms is not None and gece_saati(int(sf(ms)), pen):
                    mola_g = a.get("mola_dk", 0) / 60.0
                if gece - mola_g > lim + 1e-6:
                    ih.append(Ihlal("GECE_VARDIYASI_AZAMI", "SERT",
                                    "Gece çalışması azami süreyi aştı",
                                    calisan=a["calisan"], gun=a["gun"],
                                    beklenen=f"{lim} sa",
                                    gercek=f"{gece - mola_g:.2f} sa"))

        if ka:
            p = ka["param"]
            pen = (int(sf(p["bas"])), int(sf(p["bit"])))
            lim = p["ardisik"]
            gece_gun = {}
            for a in A:
                ab, at = sf(a["bas"]), sf(a["bit"])
                if any(gece_saati(h, pen) for h in range(int(ab), int(at))):
                    gece_gun.setdefault(a["calisan"], set()).add(a["gun"])
            for cid, gunler in gece_gun.items():
                sirali = sorted(gunler)
                art = 1
                for i in range(1, len(sirali)):
                    art = art + 1 if sirali[i] == sirali[i - 1] + 1 else 1
                    if art > lim:
                        ih.append(Ihlal("ARDISIK_GECE_LIMIT", "SERT",
                                        "Ardışık gece vardiyası sınırı aşıldı",
                                        calisan=cid, gun=sirali[i],
                                        beklenen=f"{lim} gece", gercek=f"{art} gece"))
                        break
        return ih

    # -- uygunluk ailesi (AKTIF, SOZLESME, IZIN, UYGUNLUK, CALISMA_SAATLERI)
    def _uygunluk(self, A):
        ih = []
        for a in A:
            c = self.calisan.get(a["calisan"])
            if c is None:
                ih.append(Ihlal("AKTIF_CALISAN", "SERT", "Tanımsız çalışan kimliği",
                                calisan=a["calisan"]))
                continue

            if c["durum"] != "AKTIF":
                ih.append(Ihlal("AKTIF_CALISAN", "SERT", "Pasif çalışana atama",
                                calisan=c["id"], gun=a["gun"]))

            if c.get("sozlesme_bitis"):
                bitis = date.fromisoformat(c["sozlesme_bitis"])
                gun_tarihi = self.plan_baslangic.toordinal() + a["gun"]
                if gun_tarihi > bitis.toordinal():
                    ih.append(Ihlal("SOZLESME_GECERLI", "SERT",
                                    "Sözleşme bitişinden sonraya atama",
                                    calisan=c["id"], gun=a["gun"],
                                    beklenen=c["sozlesme_bitis"]))

            ab, at = sf(a["bas"]), sf(a["bit"])
            dokunulan = gunler_arasi(a["gun"], ab, at)

            # Gece vardiyası iki güne dokunur; izin her iki gün için de bağlar.
            for iz in c.get("izinler", []):
                if iz["gun"] in dokunulan:
                    ih.append(Ihlal("ONAYLI_IZIN", "SERT", "Onaylı izin gününe atama",
                                    calisan=c["id"], gun=a["gun"]))
                    break

            # Uygunluk penceresi: vardiyanın her saati kendi gününde sınanır.
            kapali = {}
            for u in c.get("uygunluk", []):
                if u["tip"] != "UYGUN_DEGIL":
                    continue
                for s in range(int(sf(u["bas"])), int(sf(u["bit"]))):
                    kapali[(u["gun"], s)] = f"{u['bas']}–{u['bit']}"
            carpisan = next((kapali[k] for k in hucreler(a["gun"], ab, at) if k in kapali),
                            None)
            if carpisan:
                ih.append(Ihlal("UYGUNLUK_TAKVIMI", "SERT",
                                "Çalışanın uygun olmadığı aralığa atama",
                                calisan=c["id"], gun=a["gun"],
                                beklenen=f"{carpisan} kapalı",
                                gercek=f"{a['bas']}–{a['bit']}"))

            # Operasyon saatleri: her kapsanan saat açık olmalı. 7/24 ekipte
            # (00:00–24:00) bu koşul kendiliğinden sağlanır.
            e = self.ekip.get(a["ekip"])
            if e:
                ea, ek = sf(e["acilis"]), sf(e["kapanis"])
                if not (ea == 0 and ek >= 24):
                    disari = [s for _g, s in hucreler(a["gun"], ab, at)
                              if not (ea <= s < ek)]
                    if disari:
                        ih.append(Ihlal("CALISMA_SAATLERI", "SERT",
                                        "Operasyon saatleri dışına atama",
                                        calisan=a["calisan"], ekip=a["ekip"], gun=a["gun"],
                                        beklenen=f"{e['acilis']}–{e['kapanis']}",
                                        gercek=f"{a['bas']}–{a['bit']}"))
        return ih

    # -- CAKISMA_YOK
    def _cakisma(self, A):
        """Çakışma MUTLAK zamanda ölçülür.

        Gün bazında gruplarsak, pazartesi 23:00–07:00 gece vardiyası ile
        salı 06:00 vardiyası ayrı gruplara düşer ve çakışma görünmez.
        """
        ih = []
        by = {}
        for a in A:
            by.setdefault(a["calisan"], []).append(
                (a["gun"] * 24 + sf(a["bas"]), a["gun"] * 24 + sf(a["bit"]), a))
        for cid, lst in by.items():
            lst.sort(key=lambda z: (z[0], z[1]))    # dict'leri karşılaştırma
            for i in range(len(lst) - 1):
                if lst[i][1] > lst[i + 1][0] + 1e-6:
                    x, y = lst[i][2], lst[i + 1][2]
                    ih.append(Ihlal("CAKISMA_YOK", "SERT", "Aynı çalışana çakışan iki atama",
                                    calisan=cid, gun=y["gun"],
                                    gercek=f"{x['bas']}–{x['bit']} (gün {x['gun']}) ∩ "
                                           f"{y['bas']}–{y['bit']} (gün {y['gun']})"))
        return ih

    # -- GUNLUK_AZAMI / HAFTALIK_AZAMI / PART_TIME_LIMIT
    def _sure_limitleri(self, A):
        ih = []
        gunluk_lim = self.kural["GUNLUK_AZAMI"]["param"]["saat"]
        haftalik_lim = self.kural["HAFTALIK_AZAMI"]["param"]["saat"]

        gunluk, haftalik = {}, {}
        for a in A:
            gunluk[(a["calisan"], a["gun"])] = gunluk.get((a["calisan"], a["gun"]), 0) + self.net_saat(a)
            haftalik[a["calisan"]] = haftalik.get(a["calisan"], 0) + self.net_saat(a)

        for (cid, gun), sa in gunluk.items():
            if sa > gunluk_lim + 1e-6:
                ih.append(Ihlal("GUNLUK_AZAMI", "SERT", "Günlük azami çalışma aşıldı",
                                calisan=cid, gun=gun,
                                beklenen=f"{gunluk_lim} sa", gercek=f"{sa:.2f} sa"))

        for cid, sa in haftalik.items():
            c = self.calisan.get(cid)
            if sa > haftalik_lim + 1e-6:
                ih.append(Ihlal("HAFTALIK_AZAMI", "SERT", "Haftalık azami çalışma aşıldı",
                                calisan=cid, beklenen=f"{haftalik_lim} sa",
                                gercek=f"{sa:.2f} sa"))
            if c and c["tur"] == "YARI_ZAMANLI":
                lim = c["sozlesme_dk_hafta"] / 60.0
                if sa > lim + 1e-6:
                    ih.append(Ihlal("PART_TIME_LIMIT", "SERT",
                                    "Yarı zamanlı sözleşme limiti aşıldı",
                                    calisan=cid, beklenen=f"{lim:.0f} sa",
                                    gercek=f"{sa:.2f} sa"))
        return ih

    # -- VARDIYA_ARASI_DINLENME  (geçmiş dahil)
    def _dinlenme(self, A):
        ih = []
        lim = self.kural["VARDIYA_ARASI_DINLENME"]["param"]["saat"]
        olay = {}
        for a in A:
            olay.setdefault(a["calisan"], []).append(
                (a["gun"] * 24 + sf(a["bas"]), a["gun"] * 24 + sf(a["bit"]), a)
            )
        for cid, lst in olay.items():
            # geçmişin son vardiyasını sınır olarak ekle
            gec = self.gecmis.get(cid, [])
            tam = [(b, t, None) for b, t in gec] + lst
            tam.sort(key=lambda x: x[0])
            for i in range(len(tam) - 1):
                bosluk = tam[i + 1][0] - tam[i][1]
                a2 = tam[i + 1][2]
                if a2 is None:
                    continue          # geçmiş–geçmiş çifti: plandan kaynaklanmaz
                if bosluk < lim - 1e-6:
                    ih.append(Ihlal("VARDIYA_ARASI_DINLENME", "SERT",
                                    "İki vardiya arası dinlenme yetersiz",
                                    calisan=cid,
                                    gun=a2["gun"] if a2 else None,
                                    beklenen=f"{lim} sa", gercek=f"{bosluk:.2f} sa"))
        return ih

    # -- HAFTA_TATILI
    def _hafta_tatili(self, A):
        ih = []
        p = self.kural["HAFTA_TATILI"]["param"]
        gerek = p["saat"]
        son = self.gun_sayisi * 24

        olay = {}
        for a in A:
            olay.setdefault(a["calisan"], []).append(
                (a["gun"] * 24 + sf(a["bas"]), a["gun"] * 24 + sf(a["bit"]))
            )
        for cid, c in self.calisan.items():
            if c["durum"] != "AKTIF":
                continue
            lst = sorted(olay.get(cid, []))
            if not lst:
                continue                       # hiç atanmamış → zaten dinlenmiş
            gec = [x for x in self.gecmis.get(cid, []) if x[1] > -24]
            sinir = max([t for _, t in gec], default=0.0)

            en_uzun = lst[0][0] - max(sinir, 0.0)
            for i in range(len(lst) - 1):
                en_uzun = max(en_uzun, lst[i + 1][0] - lst[i][1])
            en_uzun = max(en_uzun, son - lst[-1][1])

            if en_uzun < gerek - 1e-6:
                ih.append(Ihlal("HAFTA_TATILI", "SERT",
                                "Haftalık kesintisiz dinlenme sağlanamadı",
                                calisan=cid, beklenen=f"{gerek} sa",
                                gercek=f"{en_uzun:.1f} sa"))
        return ih

    # -- MOLA_HAKKI
    def _mola_hakki(self, A):
        ih = []
        for a in A:
            brut = self.brut_saat(a)
            gerek = self.gerekli_mola(brut)
            if a.get("mola_dk", 0) < gerek:
                ih.append(Ihlal("MOLA_HAKKI", "SERT", "Mola hakkı eksik",
                                calisan=a["calisan"], gun=a["gun"],
                                beklenen=f"{gerek} dk", gercek=f"{a.get('mola_dk',0)} dk"))
            # molası olan vardiyada mola saati atanmış olmalı
            if gerek >= 30 and a.get("mola_saat") is None:
                ih.append(Ihlal("MOLA_HAKKI", "SERT", "Mola saati yerleştirilmemiş",
                                calisan=a["calisan"], gun=a["gun"]))
        return ih

    # -- ASGARI_KAPSAMA / MOLA_KAPSAMASI / ROL_KAPSAMASI
    def _kapsama(self, A):
        ih = []
        rol_p = self.kural["ROL_KAPSAMASI"]["param"]
        var, molasiz, lider = {}, {}, {}

        for a in A:
            c = self.calisan.get(a["calisan"])
            for s in range(int(sf(a["bas"])), int(sf(a["bit"]))):
                g2, s2 = hucre(a["gun"], s)
                k = (a["ekip"], g2, s2)
                molasiz[k] = molasiz.get(k, 0) + 1
                if not self.molada(a, s):
                    var[k] = var.get(k, 0) + 1
                    if c and rol_p["rol"] in c["roller"]:
                        lider[k] = lider.get(k, 0) + 1

        # DEVİR VARDİYALARI: plan haftasının ilk saatleri, önceki haftanın
        # gece vardiyasıyla kapanır. O kişiler zaten sahada; saymazsak 0. günün
        # sabahında olmayan bir açık görünür ve motor boşuna kişi eklemeye
        # çalışır. Bu kayıtlar geçmişten gelir, değiştirilemez.
        for cid, araliklar in self.gecmis.items():
            c = self.calisan.get(cid)
            if not c:
                continue
            for ab, at in araliklar:
                for h in range(int(ab), int(at)):
                    if h < 0 or h >= self.gun_sayisi * 24:
                        continue                      # plan penceresi dışında
                    k = (c["ekip"], h // 24, h % 24)
                    molasiz[k] = molasiz.get(k, 0) + 1
                    var[k] = var.get(k, 0) + 1
                    if rol_p["rol"] in c["roller"]:
                        lider[k] = lider.get(k, 0) + 1

        for (ekip, gun, saat), (asgari, _hedef) in self.talep.items():
            mevcut = var.get((ekip, gun, saat), 0)
            ham = molasiz.get((ekip, gun, saat), 0)
            if mevcut < asgari:
                if ham >= asgari:
                    ih.append(Ihlal("MOLA_KAPSAMASI", "SERT",
                                    "Molalar sırasında asgari kapsamanın altına düşüldü",
                                    ekip=ekip, gun=gun, saat=saat,
                                    beklenen=asgari, gercek=mevcut))
                else:
                    ih.append(Ihlal("ASGARI_KAPSAMA", "SERT", "Asgari kapsama sağlanamadı",
                                    ekip=ekip, gun=gun, saat=saat,
                                    beklenen=asgari, gercek=mevcut))
            if lider.get((ekip, gun, saat), 0) < rol_p["asgari"]:
                ih.append(Ihlal("ROL_KAPSAMASI", "SERT",
                                f"{rol_p['rol']} kapsaması sağlanamadı",
                                ekip=ekip, gun=gun, saat=saat,
                                beklenen=rol_p["asgari"],
                                gercek=lider.get((ekip, gun, saat), 0)))
        return ih

    # -- HEDEF_KAPSAMA / SAAT_DENGESI (yumuşak)
    def _yumusak(self, A):
        ih = []
        var = {}
        for a in A:
            for s in range(int(sf(a["bas"])), int(sf(a["bit"]))):
                if not self.molada(a, s):
                    g2, s2 = hucre(a["gun"], s)
                    var[(a["ekip"], g2, s2)] = var.get((a["ekip"], g2, s2), 0) + 1
        for cid, araliklar in self.gecmis.items():          # devir vardiyaları
            c = self.calisan.get(cid)
            if not c:
                continue
            for ab, at in araliklar:
                for h in range(int(ab), int(at)):
                    if 0 <= h < self.gun_sayisi * 24:
                        k = (c["ekip"], h // 24, h % 24)
                        var[k] = var.get(k, 0) + 1

        eksik = 0
        for k, (_asgari, hedef) in self.talep.items():
            d = hedef - var.get(k, 0)
            if d > 0:
                eksik += d
        if eksik > 0:
            ih.append(Ihlal("HEDEF_KAPSAMA", "YUMUSAK",
                            "Hedef kapsamanın altında kalan kişi-saat",
                            gercek=f"{eksik} kişi-saat"))

        tol = self.kural["SAAT_DENGESI"]["param"]["tolerans_saat"]
        saat = {}
        for a in A:
            saat[a["calisan"]] = saat.get(a["calisan"], 0) + self.net_saat(a)
        gruplar = {}
        for cid, c in self.calisan.items():
            if c["durum"] != "AKTIF":
                continue
            gruplar.setdefault((c["ekip"], c["tur"]), []).append(saat.get(cid, 0.0))
        for (ekip, tur), vals in gruplar.items():
            if len(vals) < 3:
                continue
            sapma = pstdev(vals)
            if sapma > tol:
                ih.append(Ihlal("SAAT_DENGESI", "YUMUSAK",
                                "Grup içi saat dağılımı toleransın üstünde",
                                ekip=ekip, beklenen=f"σ ≤ {tol} sa",
                                gercek=f"σ = {sapma:.2f} sa ({tur})"))
        return ih


# --------------------------------------------------------------------

def ozet(ihlaller):
    sert = [i for i in ihlaller if i.tur == "SERT"]
    yum = [i for i in ihlaller if i.tur == "YUMUSAK"]
    say = {}
    for i in ihlaller:
        say[i.kod] = say.get(i.kod, 0) + 1
    return {"sert": len(sert), "yumusak": len(yum), "kod_bazinda": say}


if __name__ == "__main__":
    girdi = json.load(open(sys.argv[1], encoding="utf-8"))
    plan = json.load(open(sys.argv[2], encoding="utf-8"))
    d = Degerlendirici(girdi)
    ih = d.calistir(plan)
    o = ozet(ih)
    print(f"sert ihlal: {o['sert']}   yumuşak: {o['yumusak']}")
    for kod, n in sorted(o["kod_bazinda"].items(), key=lambda x: -x[1]):
        print(f"  {kod:28s} {n}")
    for i in ih[:15]:
        print("   ·", i.kod, i.mesaj, i.dict().get("gercek", ""))
