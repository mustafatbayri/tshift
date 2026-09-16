# -*- coding: utf-8 -*-
"""
DEGISMEZ KONTROLLERI

NE YAPAR
  'solve' tipi fiksturlerdeki `degismezler` listesinde gecen `kontrol`
  adlarinin govdesi burada. Her biri motorun URETTIGI plana bakar ve
  "bu iddia tutuyor mu" sorusunu cevaplar.

  Her fonksiyon (tamam_mi, mesaj) dondurur. Mesaj, test kirildiginda
  Mustafa'nin okuyacagi cumledir -- teknik degil, is dilinde.

NEDEN AYRI DOSYA
  Fikstur bir VERIDIR: "C08 hicbir Sali calismaz" cumlesini tasir ama
  nasil kontrol edilecegini bilmez. Kontrolun govdesi koddur ve burada
  durur. Yeni bir degismez eklemek = fiksture bir satir + buraya bir
  fonksiyon.

BU NE DEGILDIR
  * Urunun dogrulayicisi DEGILDIR. Burasi testin yardimcisi.
  * Motorun ihlal listesini YENIDEN URETMEZ. Ihlal denetimi motorun
    kendi dogrulayicisinin isi; burasi ondan bagimsiz, kaba ve dar
    kontroller yapar (spec #16.1).
"""

from collections import defaultdict

KAYIT = {}


def kontrol(ad):
    def sar(fn):
        KAYIT[ad] = fn
        return fn
    return sar


# ----------------------------------------------------------------------
# Yardimcilar
# ----------------------------------------------------------------------

def _atamalar(cikti):
    return cikti.get("atamalar", []) or []


def _net_saat(a):
    brut = a["bit"] - a["bas"]
    mola = sum(m["bit"] - m["bas"] for m in a.get("molalar", []))
    return brut - mola


def _kisi_gunleri(cikti):
    g = defaultdict(set)
    for a in _atamalar(cikti):
        g[a["calisan"]].add(a["gun"])
    return g


# ----------------------------------------------------------------------
# Kontroller
# ----------------------------------------------------------------------

@kontrol("calisan_gun_atamasi_yok")
def calisan_gun_atamasi_yok(cikti, girdi, tanim):
    c, gun = tanim["calisan"], tanim["gun"]
    bulunan = [a for a in _atamalar(cikti)
               if a["calisan"] == c and a["gun"] == gun]
    if bulunan:
        return False, ("%s'e gun %d'de %d atama yapilmis; hic olmamaliydi"
                       % (c, gun, len(bulunan)))
    return True, "%s gun %d'de calismiyor" % (c, gun)


@kontrol("calisan_vardiya_bitisi_en_fazla")
def calisan_vardiya_bitisi_en_fazla(cikti, girdi, tanim):
    c, sinir = tanim["calisan"], tanim["bit"]
    kotu = [a for a in _atamalar(cikti)
            if a["calisan"] == c and a["bit"] > sinir]
    if kotu:
        return False, ("%s'e %d'den sonra biten %d vardiya verilmis "
                       "(en gec %d olmaliydi)" % (c, sinir, len(kotu), sinir))
    return True, "%s'in butun vardiyalari en gec %d'de bitiyor" % (c, sinir)


@kontrol("haftalik_net_saat_sozlesme_alti")
def haftalik_net_saat_sozlesme_alti(cikti, girdi, tanim):
    sozlesme = {c["id"]: c["sozlesme"]["haftalik_saat"]
                for c in girdi["calisanlar"]}
    toplam = defaultdict(float)
    for a in _atamalar(cikti):
        toplam[a["calisan"]] += _net_saat(a)
    asanlar = [(c, v, sozlesme.get(c))
               for c, v in toplam.items()
               if sozlesme.get(c) is not None and v > sozlesme[c]]
    if asanlar:
        satir = "; ".join("%s %.1f saat (sozlesme %d)" % x for x in asanlar)
        return False, "Sozlesme saatini asanlar: " + satir
    return True, "Kimsenin haftalik saati sozlesmesini asmiyor"


@kontrol("ardisik_gun_en_fazla")
def ardisik_gun_en_fazla(cikti, girdi, tanim):
    sinir = tanim["deger"]
    for c, gunler in _kisi_gunleri(cikti).items():
        seri, en_uzun = 0, 0
        for g in range(0, 7):
            seri = seri + 1 if g in gunler else 0
            en_uzun = max(en_uzun, seri)
        if en_uzun > sinir:
            return False, ("%s %d gun ust uste calisiyor (en fazla %d)"
                           % (c, en_uzun, sinir))
    return True, "Kimse %d gunden fazla ust uste calismiyor" % sinir


@kontrol("gunde_tek_vardiya")
def gunde_tek_vardiya(cikti, girdi, tanim):
    say = defaultdict(int)
    for a in _atamalar(cikti):
        say[(a["calisan"], a["gun"])] += 1
    cift = [k for k, v in say.items() if v > 1]
    if cift:
        return False, ("Ayni gun birden cok vardiya verilenler: %s"
                       % ", ".join("%s gun %d" % k for k in cift))
    return True, "Kimseye ayni gun iki vardiya verilmemis"


@kontrol("sabit_atamalar_birebir_var")
def sabit_atamalar_birebir_var(cikti, girdi, tanim):
    def anahtar(a):
        return (a["calisan"], a.get("ekip"), a["gun"], a["bas"], a["bit"])
    ciktidakiler = {anahtar(a) for a in _atamalar(cikti)}
    eksik = [s for s in girdi.get("sabit_atamalar", [])
             if anahtar(s) not in ciktidakiler]
    if eksik:
        return False, ("Sabit atamalardan %d tanesi ciktida yok: %s"
                       % (len(eksik),
                          ", ".join("%s gun %d" % (e["calisan"], e["gun"])
                                    for e in eksik)))
    return True, "Butun sabit atamalar ciktida birebir duruyor"


@kontrol("haftalik_fazla_mesai_en_fazla")
def haftalik_fazla_mesai_en_fazla(cikti, girdi, tanim):
    sinir = tanim["deger"]
    fm = cikti.get("metrikler", {}).get("fazla_mesai_saat")
    if fm is None:
        return False, "Ciktida fazla_mesai_saat metrigi yok"
    kisi = len(girdi["calisanlar"])
    if fm > sinir * kisi:
        return False, ("Toplam fazla mesai %.1f saat; tavan kisi basi %d "
                       "(en fazla %d)" % (fm, sinir, sinir * kisi))
    return True, "Fazla mesai tavani asilmamis"


@kontrol("her_atamada_mola_var")
def her_atamada_mola_var(cikti, girdi, tanim):
    yok = [a for a in _atamalar(cikti) if not a.get("molalar")]
    if yok:
        return False, "%d atamanin molasi yok" % len(yok)
    return True, "Her atamanin molasi var"


@kontrol("mola_penceresi_icinde")
def mola_penceresi_icinde(cikti, girdi, tanim):
    erken, gec = tanim["en_erken"], tanim["en_gec_bitis"]
    kotu = []
    for a in _atamalar(cikti):
        for m in a.get("molalar", []):
            if m["bas"] < erken or m["bit"] > gec:
                kotu.append((a["calisan"], a["gun"], m["bas"], m["bit"]))
    if kotu:
        return False, ("Mola penceresi (%d-%d) disina cikan %d mola: %s"
                       % (erken, gec, len(kotu),
                          ", ".join("%s gun %d %s-%s" % k for k in kotu[:3])))
    return True, "Butun molalar %d-%d penceresi icinde" % (erken, gec)


@kontrol("mola_tek_blok")
def mola_tek_blok(cikti, girdi, tanim):
    bolunmus = [a for a in _atamalar(cikti) if len(a.get("molalar", [])) > 1]
    if bolunmus:
        return False, ("%d atamanin molasi bolunmus; mevzuat tek blok istiyor "
                       "(K-14)" % len(bolunmus))
    return True, "Butun molalar tek blok"


@kontrol("mola_sonrasi_kapsama_en_az")
def mola_sonrasi_kapsama_en_az(cikti, girdi, tanim):
    asgari = tanim["deger"]
    kotu = []
    for t in girdi.get("talep", []):
        for gun in t.get("gunler", []):
            for saat in t.get("saatler", []):
                sahada = 0
                for a in _atamalar(cikti):
                    if a["gun"] != gun or not (a["bas"] <= saat < a["bit"]):
                        continue
                    if any(m["bas"] <= saat < m["bit"]
                           for m in a.get("molalar", [])):
                        continue
                    sahada += 1
                if sahada < asgari:
                    kotu.append((gun, saat, sahada))
    if kotu:
        return False, ("Mola dusuldukten sonra %d hucrede sahadaki kisi "
                       "%d'un altina indi: %s"
                       % (len(kotu), asgari,
                          ", ".join("gun %d saat %d -> %d kisi" % k
                                    for k in kotu[:3])))
    return True, "Mola sirasinda da sahada en az %d kisi kaliyor" % asgari


@kontrol("evaluate_ile_sifir_sert_ihlal")
def evaluate_ile_sifir_sert_ihlal(cikti, girdi, tanim):
    """Bagimsiz dogrulayici cagrisi. Testin kendisi yapar, burasi yalniz isaret."""
    return None, ("Bu kontrol /evaluate cagrisi gerektiriyor; "
                  "test govdesinde yapiliyor")


@kontrol("evaluate_ile_dogrula")
def evaluate_ile_dogrula(cikti, girdi, tanim):
    return None, ("Bu kontrol /evaluate cagrisi gerektiriyor; "
                  "test govdesinde yapiliyor")


@kontrol("adalet_ihlali_sert_sayilmaz")
def adalet_ihlali_sert_sayilmaz(cikti, girdi, tanim):
    """ADALET_DENGESI YUMUSAK; ihlali sert sayilmamali.

    /solve ciktisi ihlal LISTESI tasimaz (spec #11.3: yalniz metrikler),
    o yuzden burada karar verilemez -- /evaluate cagrisi gerekiyor.
    Test govdesinde yapiliyor.
    """
    return None, ("ADALET_DENGESI'nin sert sayilmadigi /evaluate ile "
                  "dogrulanir; test govdesinde yapiliyor")


@kontrol("kural_listesiz_de_ayni_sonuc")
def kural_listesiz_de_ayni_sonuc(cikti, girdi, tanim):
    return None, ("Bu kontrol ikinci bir /solve cagrisi gerektiriyor; "
                  "test govdesinde yapiliyor")


@kontrol("gunluk_net_saat")
def gunluk_net_saat(cikti, girdi, tanim):
    toplam = sum(_net_saat(a) for a in _atamalar(cikti))
    return True, "Toplam net calisma: %.1f saat" % toplam


def calistir(ad, cikti, girdi, tanim):
    """Adi verilen kontrolu kosar. Bilinmeyen ad = testin hatasi."""
    if ad not in KAYIT:
        raise KeyError(
            "Bilinmeyen kontrol adi: %r\n"
            "  Fiksturde gecen her 'kontrol' adinin kontroller.py'de bir\n"
            "  govdesi olmali. Taninanlar: %s" % (ad, ", ".join(sorted(KAYIT))))
    return KAYIT[ad](cikti, girdi, tanim)
