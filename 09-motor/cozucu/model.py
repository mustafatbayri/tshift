# -*- coding: utf-8 -*-
"""
COZUCU MODELI -- CP-SAT (Master Spec v1.4 #11.2, M-09)

BU DOSYA DOGRULAYICIDAN BAGIMSIZDIR -- #7.6, #16.1

  `dogrulayici/` altindaki HICBIR modul import edilmez. Zaman aritmetigi
  burada IKINCI KEZ, bagimsiz olarak yazildi. Bu bilerek yapilan bir
  tekrardir.

  Sebebi D-6 sinifi hata: kodu yazan testi de yazarsa ayni yanlis varsayim
  iki yere birden gecer ve hicbir test yakalamaz. Dogrulayici ancak
  cozucuden bagimsizsa onu denetleyebilir.

  "Ayni hesabi iki kez yazmayalim" diyip ortak bir modul cikarmak
  YASAKTIR. Tekrar burada maliyet degil, guvencedir.

  Bilerek FARKLI kuruldu: dogrulayici mutlak saat araliklariyla calisir,
  cozucu SAAT DILIMI (slot) tabanlidir. Ayni sonuca iki ayri yoldan
  varmalari, ikisinin birden yanlis olma ihtimalini dusurur.

MODEL
  x[e,d,t]      calisan e, gun d, sablon t ile calisiyor mu
  m[e,d,t,s]    o vardiyanin molasi s diliminde basliyor mu

  Sert kurallar kisit, yumusak kurallar amac fonksiyonunda ceza.
"""

from ortools.sat.python import cp_model

# Modelde saatler TAM SAYI dilimdir. Genisletilmis saat: 25 = ertesi gun 01:00.
HAFTA_GUN = 7

# ----------------------------------------------------------------------
# Plan profilleri -- Master Spec v1.4 #5.4
#
#   Ayni kural seti, farkli agirliklarla UC FARKLI plan uretir. Profil
#   motorun "neyi onemserim" ayaridir; kural listesini degistirmez.
#
#   A7 altin senaryosu tam olarak bunu siniyor: ayni girdi iki profille
#   kosuluyor ve IKISININ ESIT CIKMASI testi kirmizi yakiyor. Bu tablo
#   yokken A7 kirmiziydi ve dogru sebeple kirmiziydi -- motor profili
#   hic okumuyordu.
#
#   Kiraci bu tabloyu duzenleyebilir (#9.16, `plan_profiles`). Duzenlenmis
#   degerler girdiye `agirliklar: {KOD: sayi}` olarak gelir ve tabloyu ezer.
# ----------------------------------------------------------------------

PROFILLER = ("DENGELI", "KAPSAMA", "CALISAN")

AGIRLIK_TABLOSU = {
    "HEDEF_KAPSAMA":         {"DENGELI": 9, "KAPSAMA": 20, "CALISAN": 5},
    "SAAT_DENGESI":          {"DENGELI": 5, "KAPSAMA": 2,  "CALISAN": 8},
    "TERCIH_KARSILAMA":      {"DENGELI": 3, "KAPSAMA": 1,  "CALISAN": 9},
    "ADALET_DENGESI":        {"DENGELI": 5, "KAPSAMA": 2,  "CALISAN": 8},
    "EKIP_SUREKLILIGI":      {"DENGELI": 2, "KAPSAMA": 1,  "CALISAN": 4},
    "PLAN_KARARLILIGI":      {"DENGELI": 6, "KAPSAMA": 6,  "CALISAN": 6},
    "MOLA_KAPSAMASI":        {"DENGELI": 7, "KAPSAMA": 9,  "CALISAN": 6},
    "VARDIYA_ROTASYON_YONU": {"DENGELI": 3, "KAPSAMA": 1,  "CALISAN": 6},
}

# #6 FAZLA_MESAI_TAVANI.azami_saat_hafta de profile baglidir (#5.2 tablosu):
# CALISAN 0 - DENGELI 10 - KAPSAMA 15. Bu bir SERT tavandir, agirlik degil.
FAZLA_MESAI_PROFIL = {"DENGELI": 10, "KAPSAMA": 15, "CALISAN": 0}


# ----------------------------------------------------------------------
# Zaman -- dogrulayicidan BAGIMSIZ ikinci uygulama
# ----------------------------------------------------------------------

def _dilimler(gun, bas, bit):
    """Vardiyanin kapsadigi mutlak saat dilimleri.

    Genisletilmis saat dogrudan toplanir: gun 1, 16 -> 25  =>  40..48.
    Bitis dilimi DAHIL DEGIL (bit=18 ise son dilim 17).
    """
    return list(range(gun * 24 + int(bas), gun * 24 + int(bit)))


def _net_saat(sablon):
    return (sablon["bit"] - sablon["bas"]) - (sablon.get("mola_dk", 0) / 60.0)


def _brut_saat(sablon):
    return sablon["bit"] - sablon["bas"]


def _mola_baslangiclari(sablon):
    """Molanin baslayabilecegi TAM SAAT dilimleri.

    Pencere yoksa vardiyanin ortasina yakin her yer serbesttir.
    Mola suresi 0 ise tek bir sahte secenek dondurulur (model basit kalsin).
    """
    mola_saat = sablon.get("mola_dk", 0) / 60.0
    if mola_saat <= 0:
        return [None]
    p = sablon.get("mola_penceresi") or {}
    erken = p.get("en_erken", sablon["bas"])
    gec = p.get("en_gec_bitis", sablon["bit"])
    son = int(gec - mola_saat)
    adaylar = [s for s in range(int(erken), son + 1)
               if s >= sablon["bas"] and s + mola_saat <= sablon["bit"]]
    return adaylar or [int(erken)]


def _mola_dilimleri(gun, sablon, baslangic):
    """Molanin kapsadigi dilimler. 15 dk'lik mola da o saat dilimini kaplar.

    Dogrulayici ile AYNI anlami tasir ama farkli yoldan: orada
    `mola.bas <= saat < mola.bit` diye bakilir, burada dilim uretilir.
    15 dk mola 11:00'de baslarsa 11. dilim doludur -- kisi o saatte
    sahada sayilmaz. Kaba ama iki tarafta da ayni kaba.
    """
    if baslangic is None:
        return []
    mola_saat = sablon.get("mola_dk", 0) / 60.0
    bitis = baslangic + mola_saat
    return [d for d in range(gun * 24 + int(baslangic),
                             gun * 24 + int(bitis) + (1 if bitis % 1 else 0))]


def _gece_mi(sablon, gun, pencere=(20, 30)):
    s = set(_dilimler(gun, sablon["bas"], sablon["bit"]))
    p = set(range(gun * 24 + pencere[0], gun * 24 + pencere[1]))
    return bool(s & p)


# ----------------------------------------------------------------------
# Girdi okuma
# ----------------------------------------------------------------------

def _kural(girdi, kod):
    for k in girdi.get("kurallar", []) or []:
        if k.get("kod") == kod and k.get("aktif", True):
            return k
    return None


def _par(kural, ad, varsayilan):
    if not kural:
        return varsayilan
    return (kural.get("parametreler") or {}).get(ad, varsayilan)


def _calisabilir(c):
    return c.get("durum", "aktif") == "aktif"


class Model(object):
    """CP-SAT modeli ve onu girdiye baglayan her sey."""

    def __init__(self, girdi):
        self.girdi = girdi
        self.m = cp_model.CpModel()
        self.calisanlar = [c for c in girdi.get("calisanlar", []) if _calisabilir(c)]
        self.sablonlar = list(girdi.get("vardiya_sablonlari", []) or [])
        self.sablon = {s["id"]: s for s in self.sablonlar}
        self.gunler = list(range(HAFTA_GUN))
        self.x = {}          # (e,d,t) -> BoolVar
        self.mola = {}       # (e,d,t,s) -> BoolVar
        self.cezalar = []    # (agirlik, IntVar) ciftleri
        self.notlar = []     # uygulanmayan/atlanan seyler -- sessiz gecmemek icin
        self.profil = self._profil_sec(girdi.get("profil"))

    # ---- profil -------------------------------------------------------

    def _profil_sec(self, gelen):
        """Girdideki profil adini dogrular. Taninmayan ad SESSIZCE yutulmaz."""
        if gelen is None:
            return "DENGELI"
        ad = str(gelen).upper()
        if ad in PROFILLER:
            return ad
        self.notlar.append(
            "profil taninmadi: %r -> DENGELI kullanildi (#5.4)" % gelen)
        return "DENGELI"

    def _agirlik(self, kod, kural=None):
        """Yumusak kuralin agirligi. Oncelik sirasi:

          1. girdi['agirliklar'][kod]  -- kiracinin duzenledigi plan_profiles
          2. #5.4 profil tablosu       -- profil zaten "bu agirliklar" demektir
          3. kuralin kendi 'agirlik'i  -- tabloda olmayan kurallar icin
          4. 5                         -- ve bu durum NOT olarak bildirilir

        Profilin kuralin kendi agirligindan ONCE gelmesi bilincli: "KAPSAMA
        profiliyle coz" demek, kapsama agirligini yukseltmek demektir. Kural
        katalogundaki sayi DENGELI sutununun yazili halidir.
        """
        ozel = (self.girdi.get("agirliklar") or {}).get(kod)
        if ozel is not None:
            return ozel
        satir = AGIRLIK_TABLOSU.get(kod)
        if satir:
            return satir[self.profil]
        if kural and kural.get("agirlik") is not None:
            return kural["agirlik"]
        self.notlar.append("%s agirligi #5.4 tablosunda yok, 5 kullanildi" % kod)
        return 5

    # ---- kurulum ------------------------------------------------------

    def kur(self):
        self._degiskenler()
        self._gun_disi_sablonlari_kapat()
        self._gunde_tek_vardiya()
        self._uygunluk()
        self._izin()
        self._kilitler()
        self._sabit_atamalar()
        self._sure_sinirlari()
        self._dinlenme()
        self._ardisik_gun()
        self._kapsama()
        self._yetkinlik()
        self._amac()
        return self

    def _degiskenler(self):
        for c in self.calisanlar:
            for d in self.gunler:
                for t in self.sablonlar:
                    v = self.m.NewBoolVar("x_%s_%d_%s" % (c["id"], d, t["id"]))
                    self.x[(c["id"], d, t["id"])] = v
                    for s in _mola_baslangiclari(t):
                        self.mola[(c["id"], d, t["id"], s)] = self.m.NewBoolVar(
                            "m_%s_%d_%s_%s" % (c["id"], d, t["id"], s))
                    # Vardiya secildiyse TAM BIR mola yerlesimi secilir.
                    self.m.Add(sum(self.mola[(c["id"], d, t["id"], s)]
                                   for s in _mola_baslangiclari(t)) == v)

    def _calisiyor(self, e, d):
        return sum(self.x[(e, d, t["id"])] for t in self.sablonlar)

    # ---- sert kurallar ------------------------------------------------

    def _sablon_gunleri(self, sablon):
        """Sablonun kullanilabilecegi gunler.

        `gunler` alani yoksa HER GUN kullanilabilir -- geriye donuk uyumlu.
        Varsa yalniz o gunlerde.

        16 Eylul, A9 bulgusunun sonucu (T-14): "Cumartesi nobeti" adli
        4 saatlik sablon hafta ici de kullanilabiliyordu ve kapasiteyi
        42'den 49'a cikariyordu. Fiksturun beklentisi sablonun Cumartesiye
        ait olduguydu ama VERI MODELINDE bunu soyleyecek alan yoktu.
        """
        g = sablon.get("gunler")
        return self.gunler if g is None else [d for d in self.gunler if d in g]

    def _gun_disi_sablonlari_kapat(self):
        for c in self.calisanlar:
            for t in self.sablonlar:
                izinli = set(self._sablon_gunleri(t))
                for d in self.gunler:
                    if d not in izinli:
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

    def _gunde_tek_vardiya(self):
        """CAKISMA_YOK + gunde tek vardiya.

        Ayni gune tek sablon seciliyor; gece yarisini asan vardiyalar ertesi
        gunun vardiyasiyla cakisabilir -- o _dinlenme() icinde yakalanir.
        """
        for c in self.calisanlar:
            for d in self.gunler:
                self.m.Add(self._calisiyor(c["id"], d) <= 1)

    def _uygunluk(self):
        for c in self.calisanlar:
            for u in c.get("uygunluk", []) or []:
                if u.get("tip") != "uygun_degil":
                    continue
                yasak = set(_dilimler(u["gun"], u["bas"], u["bit"]))
                for d in self.gunler:
                    for t in self.sablonlar:
                        if set(_dilimler(d, t["bas"], t["bit"])) & yasak:
                            self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

    def _izin(self):
        for c in self.calisanlar:
            izinli = {i["gun"] for i in c.get("izinler", []) or []
                      if i.get("durum", "onayli") == "onayli"}
            for d in self.gunler:
                for t in self.sablonlar:
                    dokundugu = {g // 24 for g in _dilimler(d, t["bas"], t["bit"])}
                    if dokundugu & izinli:
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

    def _kilitler(self):
        for k in self.girdi.get("kilitler", []) or []:
            e, d = k.get("calisan"), k.get("gun")
            if k.get("tip") == "yasak":
                if any(c["id"] == e for c in self.calisanlar):
                    self.m.Add(self._calisiyor(e, d) == 0)
            elif "bas" in k and "bit" in k:
                eslesen = [t for t in self.sablonlar
                           if t["bas"] == k["bas"] and t["bit"] == k["bit"]]
                if eslesen:
                    self.m.Add(self.x[(e, d, eslesen[0]["id"])] == 1)
                else:
                    self.notlar.append("kilit sablona eslesmedi: %s gun %s" % (e, d))
            else:
                self.notlar.append("kilit bicimi taninmadi: %r" % sorted(k))

    def _sabit_atamalar(self):
        for a in self.girdi.get("sabit_atamalar", []) or []:
            anahtar = (a["calisan"], a["gun"], a.get("sablon"))
            if anahtar in [(k[0], k[1], k[2]) for k in self.x]:
                self.m.Add(self.x[anahtar] == 1)
            else:
                self.notlar.append("sabit atama modele girmedi: %r" % (anahtar,))

    def _sure_sinirlari(self):
        gunluk = _par(_kural(self.girdi, "GUNLUK_AZAMI"), "azami_saat", 11)
        haftalik = _par(_kural(self.girdi, "HAFTALIK_AZAMI"), "azami_saat", 45)
        pt_tol = _par(_kural(self.girdi, "PART_TIME_LIMIT"), "tolerans_saat", 0)
        fm_kural = _kural(self.girdi, "FAZLA_MESAI_TAVANI")
        # #5.2: tavan profile baglidir. Kuralin kendi parametresi DENGELI
        # sutununun yazili halidir; profil onu ezer (bkz. _agirlik notu).
        fm_tavan = FAZLA_MESAI_PROFIL[self.profil]

        for c in self.calisanlar:
            for d in self.gunler:
                for t in self.sablonlar:
                    if _net_saat(t) > gunluk:
                        self.m.Add(self.x[(c["id"], d, t["id"])] == 0)

            # Dakika cinsinden tam sayi calisilir; float kisit CP-SAT'e girmez.
            dakika = sum(int(round(_net_saat(t) * 60)) * self.x[(c["id"], d, t["id"])]
                         for d in self.gunler for t in self.sablonlar)
            self.m.Add(dakika <= int(haftalik * 60))

            soz = c.get("sozlesme") or {}
            tavan = soz.get("haftalik_saat")
            if tavan is not None:
                if soz.get("tip") == "yari_zamanli":
                    # Fazla Calisma Yon. md. 8 -- kismi sureliye fazla
                    # surelerle calisma da yaptirilamaz. Toleranssiz.
                    self.m.Add(dakika <= int((tavan + pt_tol) * 60))
                else:
                    self.m.Add(dakika <= int((tavan + (fm_tavan if fm_kural else 0)) * 60))
                    # Fazla mesai YUMUSAK cezayla sifira itilir (A1: esit 0).
                    #
                    # K-30 (Mustafa, 16 Eylul): "Zaten hedef hic gitmemek.
                    # Gidilecekse de minimum gitmek."
                    #
                    #   `fazla` DAKIKA cinsinden, agirlik 50. Bir saat fazla
                    #   mesai 3000 puan; kacirilan bir hedef hucresi 9-20 puan.
                    #   Yani HEDEF kapsama ugruna fazla mesai yapilmaz.
                    #
                    #   ASGARI kapsama SERT oldugu icin ceza hesabina girmez:
                    #   fazla mesai olmadan tutmuyorsa motor onu yapar, hem de
                    #   tam gerektigi kadar. Karar tam olarak bunu istiyor.
                    #
                    #   Yukaridaki `dakika <= (tavan + fm_tavan)` kisiti ise
                    #   ZORUNLU asimin sinirini cizer: CALISAN profilinde
                    #   fm_tavan 0 oldugu icin boyle bir plan cozumsuz olur.
                    #   Tavan olu bir sayi degil -- isteğe bagli fazla mesai
                    #   icin kullanilmiyor, zorunlu olan icin belirleyici.
                    #
                    #   50 sayisi bir KALIBRASYON, karar degil. Testler
                    #   "ceza sifir olmasin" diyor, "tam olarak 50 olsun"
                    #   demiyor (testler/test_profiller.py).
                    fazla = self.m.NewIntVar(0, int(fm_tavan * 60), "fm_%s" % c["id"])
                    self.m.Add(fazla >= dakika - int(tavan * 60))
                    self.cezalar.append((50, fazla))

    def _dinlenme(self):
        """VARDIYA_ARASI_DINLENME -- ardisik gunlerdeki her sablon cifti.

        Cakisan cift de burada yakalanir: ara negatif olur, esigin altindadir.
        """
        asgari = _par(_kural(self.girdi, "VARDIYA_ARASI_DINLENME"), "asgari_saat", 11)
        for c in self.calisanlar:
            for d in self.gunler[:-1]:
                for t1 in self.sablonlar:
                    bitis = d * 24 + t1["bit"]
                    for t2 in self.sablonlar:
                        baslangic = (d + 1) * 24 + t2["bas"]
                        if baslangic - bitis < asgari:
                            self.m.Add(self.x[(c["id"], d, t1["id"])]
                                       + self.x[(c["id"], d + 1, t2["id"])] <= 1)

    def _ardisik_gun(self):
        azami = _par(_kural(self.girdi, "ARDISIK_CALISMA_GUNU"), "azami_gun", 6)
        ht = _kural(self.girdi, "HAFTA_TATILI")
        if ht:
            # Kayan 7 gunluk pencerede kesintisiz dinlenme (T-11).
            # Yedi gunluk planda karsiligi: en az bir gun bos.
            azami = min(azami, _par(ht, "pencere_gun", 7) - 1)
        for c in self.calisanlar:
            for bas in range(0, HAFTA_GUN - azami):
                self.m.Add(sum(self._calisiyor(c["id"], d)
                               for d in range(bas, bas + azami + 1)) <= azami)

    # ---- kapsama ------------------------------------------------------

    def _hucreler(self):
        """Sartname #11.2: BIR talep satiri = BIR hucre {ekip, gun, saat}.

        T-19 (23 Eylul). Bu satirlar 23 Eylul'e kadar gruplu bicim okuyordu
        ({gunler: [...], saatler: [...]}). Sartname biciminde bir istek
        gelince motor talebi HIC gormuyor, sifir atamali plan uretiyor ve
        kapsama %100 cikiyordu. Kimse yanlis degildi: fikstur bir bicim
        secti, motor fiksture bakarak yazildi; ikisi birbiriyle tutarli,
        ikisi de sartnameyle tutarsizdi. Karar (Mustafa): SARTNAME KAZANIR.

        Okunamayan satir burada SESSIZCE atlanir, ve bu bilerekdir: "neye
        bakmadim" demek #7.6 geregi dogrulayicinin isi
        (dogrulayici.denetle._okunmayan_alanlar). Cozucu rapor uretmez.
        """
        for t in self.girdi.get("talep", []) or []:
            gun, saat = t.get("gun"), t.get("saat")
            if gun is None or saat is None:
                continue
            yield t, gun, saat

    def _atanmis(self, ekip, gun, saat):
        """O hucreye ATANMIS kisiler -- mola DUSULMEZ (ASGARI/HEDEF_KAPSAMA)."""
        dilim = gun * 24 + saat
        return [self.x[(c["id"], d, t["id"])]
                for c in self.calisanlar
                if ekip in (c.get("ekipler") or [])
                for d in self.gunler
                for t in self.sablonlar
                if dilim in _dilimler(d, t["bas"], t["bit"])]

    def _sahada(self, ekip, gun, saat):
        """O hucrede SAHADA olanlar -- mola DUSULUR (MOLA_KAPSAMASI)."""
        dilim = gun * 24 + saat
        cikan = []
        for c in self.calisanlar:
            if ekip not in (c.get("ekipler") or []):
                continue
            for d in self.gunler:
                for t in self.sablonlar:
                    if dilim not in _dilimler(d, t["bas"], t["bit"]):
                        continue
                    for s in _mola_baslangiclari(t):
                        if dilim not in _mola_dilimleri(d, t, s):
                            cikan.append(self.mola[(c["id"], d, t["id"], s)])
        return cikan

    def _kapsama(self):
        asgari_kural = _kural(self.girdi, "ASGARI_KAPSAMA")
        hedef_kural = _kural(self.girdi, "HEDEF_KAPSAMA")
        mola_kural = _kural(self.girdi, "MOLA_KAPSAMASI")
        hedef_agirlik = self._agirlik("HEDEF_KAPSAMA", hedef_kural)
        mola_agirlik = self._agirlik("MOLA_KAPSAMASI", mola_kural)

        for t, gun, saat in self._hucreler():
            atanmis = self._atanmis(t.get("ekip"), gun, saat)
            if asgari_kural and t.get("asgari"):
                self.m.Add(sum(atanmis) >= t["asgari"])
            if hedef_kural and t.get("hedef"):
                eksik = self.m.NewIntVar(0, t["hedef"], "he_%d_%d" % (gun, saat))
                self.m.Add(eksik >= t["hedef"] - sum(atanmis))
                self.cezalar.append((hedef_agirlik, eksik))
            if mola_kural and t.get("asgari"):
                sahada = self._sahada(t.get("ekip"), gun, saat)
                eksik = self.m.NewIntVar(0, t["asgari"], "me_%d_%d" % (gun, saat))
                self.m.Add(eksik >= t["asgari"] - sum(sahada))
                self.cezalar.append((mola_agirlik, eksik))

    def _yetkinlik(self):
        """ROL_KAPSAMASI / YETKINLIK_KAPSAMASI -- satir bazli gereklilikler."""
        for kod, alan in (("YETKINLIK_KAPSAMASI", "yetkinlikler"),
                          ("ROL_KAPSAMASI", "operasyonel_rol")):
            for k in self.girdi.get("kurallar", []) or []:
                if k.get("kod") != kod or not k.get("aktif", True):
                    continue
                p = k.get("parametreler") or {}
                aranan = p.get("yetkinlik") or p.get("rol")
                if aranan is None:
                    self.notlar.append("%s parametresiz, atlandi" % kod)
                    continue
                uygun = [c for c in self.calisanlar
                         if (aranan in (c.get(alan) or [])
                             if alan == "yetkinlikler" else c.get(alan) == aranan)]
                for gun in ([p["gun"]] if "gun" in p else self.gunler):
                    for saat in p.get("saatler", []):
                        dilim = gun * 24 + saat
                        var = [self.x[(c["id"], d, t["id"])]
                               for c in uygun
                               if p.get("ekip") in (c.get("ekipler") or [])
                               for d in self.gunler
                               for t in self.sablonlar
                               if dilim in _dilimler(d, t["bas"], t["bit"])]
                        self.m.Add(sum(var) >= p.get("asgari", 1))

    # ---- amac ---------------------------------------------------------

    def _amac(self):
        self._adalet()
        self._saat_dengesi()
        if self.cezalar:
            self.m.Minimize(sum(a * v for a, v in self.cezalar))

    def _adalet(self):
        """ADALET_DENGESI -- IKI KATMANLI ceza.

        K-27 (Mustafa, 16 Eylul) IHLAL esigini koydu: ortalamadan 2 fazla
        calismak adaletsizliktir. Ama esik tek basina AMAC FONKSIYONU olamaz.

        ESIK BURADA YOK -- YALNIZ DOGRULAYICIDA VAR
          Ilk yazilista esik amac fonksiyonuna da konmustu. Iki bulgu
          uzerine cikarildi:

          1. OLCULDU: esik terimi tamamen kapatildiginda 57 birim testinin
             ve 12 altin senaryonun HICBIRI degismedi. Terim atildi.
             Sebebi matematiksel: atama sayisi kapsama tarafindan sabitken
             ucgensel maliyet en duz dagilimda en kucuktur, en duz dagilim
             da en yuksek kisiyi en kucuk yapar -- yani gradyan zaten esik
             ihlalini enazliyor. Esik ayrica bir sey eklemiyor.

          2. EKLESEYDI YANLIS SEY EKLERDI: esik ORTALAMAYA gore tanimli.
             Motorun ihlali kaldirmanin ucuz bir yolu var: ortalamayi
             yukseltmek, yani BASKALARINA GEREKSIZ CUMARTESI VERMEK.
             "C01 bu ay uc cumartesi calismis; o goze batmasin diye uc
             kisiyi daha cumartesiye koyalim" -- sahada sacma, modelde
             ucuz. Gradyanda bu acik yok: her ek atama para eder.

          K-27 IPTAL DEGIL: ihlali sayan ve yayin kapisina bildiren yer
          bagimsiz dogrulayicidir (dogrulayici/kurallar.py ADALET_DENGESI).
          Motorun tercihi ile kuralin tanimi ayri seylerdir; #7.6'nin
          ayirdigi sey de tam olarak budur.

        NEDEN GEREKLI -- A7'de somut olarak goruldu
          Esik tek basinayken esigin ALTINDAKI butun dagilimlar sifir ceza
          aliyordu. Yani "C01 ucuncu kez cumartesi" ile "C04 ilk kez
          cumartesi" motor icin ESIT degerdeydi ve cozucu aralarinda arama
          sirasina gore seciyordu. Agirligi 2'den 8'e cikarmak da bir sey
          degistirmiyordu: sifirin sekiz kati yine sifir. Iki profil ayni
          plani uretiyordu -- #5.4'un "ayni kural seti, uc farkli plan"
          iddiasi calismiyordu.

        CEZANIN BICIMI: ARTAN MARJINAL MALIYET
          Ucuncu cumartesi ikinciden, ikinci birinciden pahalidir. Ucgensel
          maliyet -- T(v) = v + (v-1) + ... + 1 -- ve `y_j >= sayi - j`
          seklinde DOGRUSAL kurulur. Uc ozelligi birden verir:

            * yuku zaten agir olana bir tane daha vermek PAHALI  (dagitir)
            * gereksiz atama ucuza gelmez                        (sismez)
            * ortalamaya bakmaz                                  (oyunlanmaz)

          Ilk denenen bicim "ortalamanin ustundeki sapma" idi ve olculdugunde
          sasirtici bir davranis cikti: motor cumartesiye gerekenden fazla
          kisi koyuyordu (3 yerine 5). Ortalamayi yukseltmek herkesin
          sapmasini dusurduyor -- ceza, cezalandirdigi seyi odullendiriyordu.
          Mutlak sapma da ayni acigi veriyor. Ucgensel maliyette bu acik yok.

        > KARAR BEKLIYOR (K-29): "adalet" yalniz esik midir (taban), yoksa
        > esik alti da tercih midir (gradyan)? Bu kod gradyani varsayiyor
        > cunku #5.4 agirliklarin farkli plan uretmesini sart kosuyor.
        """
        k = _kural(self.girdi, "ADALET_DENGESI")
        if not k:
            return
        agirlik = self._agirlik("ADALET_DENGESI", k)
        if not self.calisanlar:
            return
        for boyut in _par(k, "boyutlar", ["gece", "hafta_sonu"]):
            sayac = self._boyut_sayaci(boyut)
            if sayac is None:
                self.notlar.append("ADALET_DENGESI boyutu sayilamiyor: %s (T-13)" % boyut)
                continue
            sayim = {}
            en_yuksek_devir = 0
            for c in self.calisanlar:
                devir = (c.get("devir_yuk") or {}).get(boyut, 0)
                en_yuksek_devir = max(en_yuksek_devir, devir)
                sayim[c["id"]] = devir + sum(
                    self.x[(c["id"], d, t["id"])]
                    for d in self.gunler for t in self.sablonlar if sayac(t, d))

            # Bu boyutta bir kisinin alabilecegi en yuksek sayi: devri +
            # boyuta giren gun sayisi. "cumartesi" icin 1, "hafta_sonu" icin 2.
            gun_sayisi = len([d for d in self.gunler
                              if any(sayac(t, d) for t in self.sablonlar)])
            azami = en_yuksek_devir + gun_sayisi

            for c in self.calisanlar:
                for j in range(azami):
                    y = self.m.NewIntVar(0, azami, "ag_%s_%s_%d"
                                         % (boyut, c["id"], j))
                    self.m.Add(y >= sayim[c["id"]] - j)
                    self.cezalar.append((agirlik, y))

    def _boyut_sayaci(self, boyut):
        if boyut == "gece":
            return lambda t, d: _gece_mi(t, d)
        if boyut == "hafta_sonu":
            return lambda t, d: d in (5, 6)
        if boyut == "cumartesi":
            return lambda t, d: d == 5
        return None

    def _saat_dengesi(self):
        k = _kural(self.girdi, "SAAT_DENGESI")
        if not k:
            return
        tolerans = _par(k, "tolerans_saat", 2)
        agirlik = self._agirlik("SAAT_DENGESI", k)
        for c in self.calisanlar:
            soz = (c.get("sozlesme") or {}).get("haftalik_saat")
            if soz is None:
                continue
            dakika = sum(int(round(_net_saat(t) * 60)) * self.x[(c["id"], d, t["id"])]
                         for d in self.gunler for t in self.sablonlar)
            sapma = self.m.NewIntVar(0, 100000, "sd_%s" % c["id"])
            self.m.Add(sapma >= int((soz - tolerans) * 60) - dakika)
            self.cezalar.append((agirlik, sapma))
