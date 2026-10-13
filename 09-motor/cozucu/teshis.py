# -*- coding: utf-8 -*-
"""
COZUMSUZLUK TESHISI -- Master Spec v1.4 #11.3

NE YAPAR
  Cozum bulunamadiginda "cozulemedi" demekle yetinmez. Uc soruyu cevaplar:

    1. NEREDE tikaniyor       -- hucre mi, hafta toplami mi (teshis.kapsam)
    2. HANGI kural engelliyor -- ve o kural yasal mi, firma kurali mi
    3. ELDE NE VAR            -- en_iyi_plan (K-10: eller bos donulmez)

KAPSAM AYRIMI -- T-5 / K-7
  hucre : belirli bir ekip-gun-saat dolamiyor
  hafta : her hucre tek tek mumkun ama TOPLAM kapasite yetmiyor

  Ikisi ayni mesaji verirse kullanici yanlis yerde cozum arar. A9'un (b) ve
  (c) siklari tam olarak bu ayrimi siniyor.

EN IYI PLAN -- K-10
  "Sahada bazi durumlarda imkansizliklar olusuyor. Bu tur durumlarda
   yoneticilere onay ile cozumsuz dahi olsa en iyi plani sunmaliyiz."

  Sert kapsama kisitlari gevsetilerek ikinci bir model kosulur. Cikan plan
  TASLAKTIR, otomatik kaydedilmez ve icindeki her ihlal kabul_edilebilir
  bayragini tasir (#4.5 yayin kapisi).
"""

from ortools.sat.python import cp_model

from .model import Model, _q, _dilimler, cekirdek_sayisi, _kural, _par


def ulasilamayan_hucre(girdi, kuruldu):
    """Hicbir vardiya sablonunun ULASAMADIGI ilk talep hucresi -- ya da None.

    COZUCU CALISTIRMADAN sorulabilecek en basit soru: bu saati kapatabilecek
    bir vardiya var mi? Yoksa plan imkansizdir ve bunu kanitlamak icin
    arama yapmaya gerek yoktur.

    ⚠ NEDEN EKLENDI (28 Eylul, gercekci veri setinde olculdu)
      7/24 calisan bir organizasyonda Pazartesi 00:00-06:00 talebi vardi.
      O saatleri yalniz PAZAR GECESI baslayan bir vardiya kapatabilir ve
      Pazar planlanan haftanin icinde degil. Motor dogru cevabi veriyordu
      ama once cozumsuzlugu KANITLIYORDU: 105 kisilik sahnede 292 saniye,
      10 kisilik tek ekipte 73 saniye. Ayni cevap burada milisaniyede.

      (Bunun urun tarafindaki karsiligi T-28: onceki haftanin gece
       vardiyasi okunmuyor. Bu kontrol T-28'i COZMEZ, gorunur kilar.)

    Z-1'I BILIR: gece yarisini asan vardiya (23->31) bir sonraki gunun
    erken saatlerine ulasir. Bilmezse cozulebilir plani reddederdi --
    bu, gec cevap vermekten daha kotu olurdu.
    """
    gunler = list(kuruldu.gunler)
    # K-50 `hepsi`: baska ekibin sablonu da bu hucreye ulasabilir -- o
    # sablona girebilen VE bu ekibe uye bir calisan varsa. (Gece 00-06
    # satis vardiyasindaki cok ekipli kisi backoffice talebini kapatir.)
    hepsi = kuruldu.cok_ekipli_sayim == "hepsi"
    for t, gun, saat in kuruldu._hucreler():
        if not t.get("asgari"):
            continue
        if gun in kuruldu.donmus:
            continue          # K-54: donmus gunun kapsamasi olan oldu, plan degil
        if kuruldu._devir_sayisi(t.get("ekip"), gun, saat) >= t["asgari"]:
            continue          # K-56: onceki haftadan tasan vardiyalar zaten kapatiyor
        hedef = _q(gun, saat)
        for sablon in kuruldu.sablonlar:
            if sablon.get("ekip") is not None and sablon.get("ekip") != t.get("ekip"):
                if not hepsi or not any(
                        t.get("ekip") in (c.get("ekipler") or [])
                        and sablon.get("ekip") in (c.get("ekipler") or [])
                        for c in kuruldu.calisanlar):
                    continue
            izinli = sablon.get("gunler", gunler)
            for d in gunler:
                if d not in izinli:
                    continue
                if kuruldu._departman_kapali_mi(sablon, d):     # K-52
                    continue
                if hedef in _dilimler(d, sablon["bas"], sablon["bit"]):
                    break
            else:
                continue
            break
        else:
            return {"ekip": t.get("ekip"), "gun": gun, "saat": saat,
                    "gereken": t["asgari"]}
    return None


def asim_sert_mi(girdi):
    """HEDEF_ASIMI aktif ve SERT mi -- K-67 (12 Ekim 2026)."""
    k = _kural(girdi, "HEDEF_ASIMI")
    return bool(k) and k.get("tur") == "SERT"


def _ust_tolerans(girdi):
    """K-68: HEDEF_ASIMI SERT'in `ust_tolerans`i (plan parametresi; kisi,
    varsayilan 0). Okunamazsa 0 -- model notu ayrica yazar."""
    if not asim_sert_mi(girdi):
        return 0
    try:
        return max(0, int(_par(_kural(girdi, "HEDEF_ASIMI"), "ust_tolerans", 0) or 0))
    except (TypeError, ValueError):
        return 0


def celisen_talep(girdi, kuruldu):
    """K-67 ON KONTROLU: HEDEF_ASIMI SERT iken hedefin ASILMADAN tutulamayacagi
    bir hucre -- ya da None. COZUCU CALISTIRMADAN.

    Uc kaynak hucreye hedeften fazla kisi DAYATABILIR:
      * talep satirinin `asgari`si (ASGARI_KAPSAMA aktifse) hedeften buyuk,
      * firmanin saha tabani (SAHADA_ASGARI, K-33) hedeften buyuk,
      * onceki haftadan tasan vardiyalar (K-56 devir) zaten hedeften fazla.
    Ucu de girdinin kendi celiskisidir; aramaya gerek yoktur. Donmus gun
    atlanir (K-54: olan oldu). Hedefi olmayan satir atlanir.
    """
    if not asim_sert_mi(girdi):
        return None
    tol = _ust_tolerans(girdi)       # K-68: sert ust sinir = hedef + tolerans
    asgari_aktif = bool(_kural(girdi, "ASGARI_KAPSAMA"))
    taban = _par(_kural(girdi, "SAHADA_ASGARI"), "asgari_sahada", 0) or 0
    for t, gun, saat in kuruldu._hucreler():
        hedef = t.get("hedef")
        if hedef is None or gun in kuruldu.donmus:
            continue
        ust = hedef + tol
        ek = " (+ tolerans %d)" % tol if tol else ""
        adaylar = []
        if asgari_aktif and (t.get("asgari") or 0) > ust:
            adaylar.append(("ASGARI_KAPSAMA", t["asgari"],
                            "talep satirinin asgarisi %d, hedefi %d%s" % (t["asgari"], hedef, ek)))
        if taban > ust:
            adaylar.append(("SAHADA_ASGARI", taban,
                            "sahada en az %d kisi kurali, hedef %d%s" % (taban, hedef, ek)))
        devir = kuruldu._devir_sayisi(t.get("ekip"), gun, saat)
        if devir > ust:
            adaylar.append(("GECMIS_DEVIR", devir,
                            "onceki haftadan tasan %d vardiya zaten sahada, hedef %d%s"
                            % (devir, hedef, ek)))
        if adaylar:
            return {"ekip": t.get("ekip"), "gun": gun, "saat": saat,
                    "gereken": max(a[1] for a in adaylar), "hedef": hedef,
                    "ust_sinir": ust,
                    "neden": "celisen_talep",
                    "kurallar": [a[0] for a in adaylar if a[0] != "GECMIS_DEVIR"] + ["HEDEF_ASIMI"],
                    "gerekce": "hedef asilmadan tutulamaz: " + "; ".join(a[2] for a in adaylar)}
    return None


def teshis_koy(girdi, kuruldu, istatistik, ayar, on_kontrol=None, kesin=True):
    """Cozumsuzluk teshisi. `kesin` KANIT olup olmadigini soyler -- K-37.

    ⚠ NEDEN `kesin` PARAMETRESI VAR (29 Eylul)
      Bu fonksiyon iki ayri yerden cagriliyor:

        kesin=True  -- cozucu INFEASIBLE dedi, ya da on kontrol yakaladi.
                       "Boyle bir plan yok" cumlesinin ARKASINDA KANIT VAR.
        kesin=False -- butce doldu, kullanici "neden oldugunu arastir"
                       dedi. Cikan cumle bir TAHMINDIR.

      Ikincisinde de aynen "su hucreyi su kural engelliyor" yaziliyor ama
      hicbir sey kanitlanmadi: gevsetilmis modeli cozmek de 10 saniyeyle
      sinirli. Bulunan sey "bu kurali kaldirinca 10 saniyede cozuluyor";
      bulunamayan sey "kaldirmasam da 20 saniyede cozulecekti".

      Bu yuzden ayrim CIKTIDA durur (`teshis_kesin`). Dugme arkasina
      saklanmis yanlis bir cumle, ekranda duran yanlis cumleden daha iyi
      degildir.
    """
    asim_hucreleri = None
    if on_kontrol and on_kontrol.get("neden") == "celisen_talep":
        # K-67 ON KONTROLU: hedef asilmadan tutulamayan hucre. Engelleyen
        # kurallar celiskinin iki tarafidir; taslak plan da yok -- hucreyi
        # hedefte tutmak, girdinin kendisini degistirmeden mumkun degil.
        kapsam = "hucre"
        hucre = {"ekip": on_kontrol["ekip"], "gun": on_kontrol["gun"],
                 "saat": on_kontrol["saat"]}
        gereken, mumkun = on_kontrol["gereken"], on_kontrol.get("ust_sinir", on_kontrol["hedef"])
        engelleyen = [{"kod": k["kod"],
                       "yasal": k.get("yasal", False),
                       "kabul_edilebilir": k.get("kabul_edilebilir", False),
                       "etkilenen_hucre": hucre,
                       "gerekce": on_kontrol["gerekce"]}
                      for k in (girdi.get("kurallar") or [])
                      if k.get("kod") in on_kontrol["kurallar"]
                      and k.get("aktif", True)]
        belirsiz = []
        en_iyi = {"var": False,
                  "sebep": "on kontrol: girdi celiskisi -- " + on_kontrol["gerekce"]}
    elif on_kontrol:
        # ON KONTROL yolu: hucre zaten belli, aramaya gerek yok.
        kapsam = "hucre"
        hucre = {"ekip": on_kontrol["ekip"], "gun": on_kontrol["gun"],
                 "saat": on_kontrol["saat"]}
        gereken, mumkun = on_kontrol["gereken"], 0
        # ⚠ `_engelleyen_kurallar` BILEREK cagrilmaz. O fonksiyon her SERT
        #   kurali tek tek gevsetip yeniden cozer (kural basina 10 sn'ye
        #   kadar); 20 sert kurali olan bir sahnede dakikalar surer ve
        #   on kontrolun butun kazancini yer.
        #
        #   Burada aramaya gerek yok: hucreye ULASAN vardiya yoksa onu
        #   kapatmayi zorunlu kilan kural ASGARI_KAPSAMA'dir, tanimi geregi.
        #   Baska hicbir kuralin gevsetilmesi bu hucreyi kapatamaz.
        engelleyen = [{"kod": k["kod"],
                       "yasal": k.get("yasal", False),
                       "kabul_edilebilir": k.get("kabul_edilebilir", False),
                       "etkilenen_hucre": hucre,
                       "gerekce": "hucreye ulasan vardiya sablonu yok"}
                      for k in (girdi.get("kurallar") or [])
                      if k.get("kod") == "ASGARI_KAPSAMA"
                      and k.get("aktif", True)]
        belirsiz = []
        # `_en_iyi_plan` BILEREK atlanir: kurallari gevseterek bir taslak
        # uretir ama bu hucreyi HICBIR gevsetme kapatamaz -- kapatabilecek
        # vardiya YOK. Tam cozum suresini odeyip ayni cevabi almak olurdu.
        en_iyi = {"var": False,
                  "sebep": "on kontrol: hucreye ulasan vardiya sablonu yok"}
    else:
        kapsam, hucre, gereken, mumkun = _nerede_tikaniyor(girdi, kuruldu)
        engelleyen, belirsiz = _engelleyen_kurallar(girdi, kuruldu, hucre, ayar)
        en_iyi = None
        if asim_sert_mi(girdi):
            # K-67: once YALNIZ HEDEF_ASIMI yumusatilir. Plan cikarsa tikanma
            # asimdir: hangi hucrede en az kac kisi fazla gerektigi ve o plan
            # (taslak, K-10) doner. Cikmazsa tikanma baska yerdedir.
            en_iyi, asim_hucreleri = _asim_gevsek_plan(girdi, ayar)
        if not en_iyi or not en_iyi.get("var"):
            en_iyi = _en_iyi_plan(girdi, ayar)

    cevap = {
        "durum": "cozumsuz" if kesin else "sure_yetmedi",
        "motor_surumu": "0.2.0-cozucu",
        "teshis_kesin": bool(kesin),
        "teshis": {
            "kapsam": kapsam,
            "hucre": hucre,
            "gereken": gereken,
            "mumkun": mumkun,
            "engelleyen_kurallar": engelleyen,
            # T-76: denemesi sureye yetmeyen kurallar. "Engelleyen yok"
            # cumlesi ancak bu liste de bossa kanittir.
            "belirsiz_kurallar": belirsiz,
        },
        "en_iyi_plan": en_iyi,
        "cozum_istatistikleri": istatistik,
        "uygulanmayan_notlar": kuruldu.notlar,
    }
    if asim_hucreleri is not None:
        cevap["teshis"]["asim_hucreleri"] = asim_hucreleri
    if not engelleyen and belirsiz:
        cevap["teshis"]["not"] = (
            "Engelleyen kural KANITLANAMADI: %d sert kuralin denemesi %s "
            "saniyeye yetmedi (T-76). Daha uzun deneme icin "
            "`teshis_kural_saniye` verin." % (len(belirsiz),
                                             belirsiz[0]["deneme_saniye"]))
    if not kesin:
        # Ekranda "imkansiz" yazmamali: sure doldu, teshis istendigi icin
        # kosturuldu ve cikan sey bir TAHMIN.
        cevap["aciklama"] = (
            "Verilen surede plan bulunamadi. Asagidaki teshis bir TAHMINDIR; "
            "boyle bir planin olmadigi KANITLANMIS degildir.")
        cevap["verilen_saniye"] = ayar.get("azami_saniye")
        cevap["teshis_istenebilir"] = False      # zaten kosturuldu
    return cevap


# ----------------------------------------------------------------------
# 1. Nerede tikaniyor
# ----------------------------------------------------------------------

def _uygun_kisiler(girdi, kuruldu, ekip, gun, saat):
    """O hucreye ATANABILECEK kisi sayisi -- kural kisitlari ONCESI degil,
    kisisel engeller SONRASI. Izin, uygunluk ve yasak kilitleri dusulur."""
    dilim = gun * 24 + saat
    yasakli = {(k["calisan"], k["gun"]) for k in girdi.get("kilitler", []) or []
               if k.get("tip") == "yasak"}
    sayi = 0
    for c in kuruldu.calisanlar:
        if ekip not in (c.get("ekipler") or []):
            continue
        if (c["id"], gun) in yasakli:
            continue
        if any(i.get("gun") == gun and i.get("durum", "onayli") == "onayli"
               for i in c.get("izinler") or []):
            continue
        uygun_mu = False
        for t in kuruldu.sablonlar:
            # K-50: yalniz bu ekibe SAYILAN sablonlar -- cozucunun kapsama
            # sayimiyla ayni olcu (`hepsi`: uyelik; `tek`: vardiyanin ekibi).
            if not kuruldu._sayilir(c, t, ekip):
                continue
            kapsiyor = gun * 24 + int(t["bas"]) <= dilim < gun * 24 + int(t["bit"])
            if not kapsiyor:
                continue
            engelli = any(u.get("tip") == "uygun_degil" and u["gun"] == gun
                          and not (t["bit"] <= u["bas"] or t["bas"] >= u["bit"])
                          for u in c.get("uygunluk") or [])
            if not engelli:
                uygun_mu = True
                break
        if uygun_mu:
            sayi += 1
    return sayi


def _nerede_tikaniyor(girdi, kuruldu):
    """Once HUCRE seviyesine bakilir; hicbir hucre imkansiz degilse HAFTA."""
    for t, gun, saat in kuruldu._hucreler():
        gereken = t.get("asgari")
        if not gereken:
            continue
        mumkun = _uygun_kisiler(girdi, kuruldu, t.get("ekip"), gun, saat)
        if mumkun < gereken:
            return "hucre", {"ekip": t.get("ekip"), "gun": gun, "saat": saat}, \
                   gereken, mumkun

    gerekli, kapasite = _hafta_toplami(girdi, kuruldu)
    if gerekli > kapasite:
        return "hafta", None, gerekli, kapasite

    # Hucre de hafta da yetiyor -> tikanma baska bir kuraldan geliyor.
    return "kural", None, None, None


def _hafta_toplami(girdi, kuruldu):
    """Kac kisi-vardiya gerekiyor, kadro kac tane verebilir.

    Kaba ama dogru yonlu bir ust sinir: her kisi haftalik saatini en kisa
    sablona bolerek en fazla kac vardiya alabilir.
    """
    gerekli = 0
    for t, gun, saat in kuruldu._hucreler():
        gerekli = max(gerekli, 0) + 0
    # Hucre-saat degil, GUN bazinda kisi-vardiya gereksinimi:
    gun_ekip = {}
    for t, gun, saat in kuruldu._hucreler():
        if t.get("asgari"):
            gun_ekip[(t.get("ekip"), gun)] = max(
                gun_ekip.get((t.get("ekip"), gun), 0), t["asgari"])
    gerekli = sum(gun_ekip.values())

    if not kuruldu.sablonlar:
        return gerekli, 0
    en_kisa = min((s["bit"] - s["bas"]) - s.get("mola_dk", 0) / 60.0
                  for s in kuruldu.sablonlar)
    kapasite = 0
    for c in kuruldu.calisanlar:
        soz = (c.get("sozlesme") or {}).get("haftalik_saat", 45)
        kapasite += int(soz // en_kisa) if en_kisa else 0
    return gerekli, kapasite


# ----------------------------------------------------------------------
# 2. Hangi kural engelliyor
# ----------------------------------------------------------------------

def _engelleyen_kurallar(girdi, kuruldu, hucre, ayar=None):
    """Sert kurallari TEKER TEKER gevsetip hangisinin cozumu actigina bakar.

    Yavas ama dogru: "muhtemelen sudur" tahmini yerine kanit uretir.
    Yalniz SERT kurallar denenir; yumusak zaten engellemez.

    ⚠ T-76 (30 Eylul aksami, 49 kisilik uc haftalik olcumde):
      Her deneme 10 saniyeydi ve o olcekte 10 saniye plan bulmaya
      yetmiyordu; "bulamadim" sonucu "bu kural engellemiyor" diye
      okunuyor, teshis "engelleyen: yok" donuyordu. Oysa kural
      kaldirilinca plan 172 saniyede cozuluyordu. K-37'nin ailesi:
      "yetistiremedim" ile "yok" ayni kelimeye dusuyordu -- teshisin
      icinde. Artik uc cevap var:
        cozuldu     -> ENGELLIYOR (kanit)
        cozumsuz    -> engellemiyor (kanit)
        sure doldu  -> BELIRSIZ (kanit yok; ayri listede)
      Deneme butcesi `teshis_kural_saniye` ile ayarlanabilir.

    Donen: (engelleyen, belirsiz)
    """
    saniye = float((ayar or {}).get("teshis_kural_saniye", 10))
    sert = [k for k in girdi.get("kurallar", []) or []
            if k.get("tur") == "SERT" and k.get("aktif", True)]
    engelleyen, belirsiz = [], []
    for k in sert:
        kalan = [x for x in girdi["kurallar"] if x is not k]
        deneme = dict(girdi, kurallar=kalan)
        satir = {"kod": k["kod"],
                 "yasal": k.get("yasal", False),
                 "kabul_edilebilir": k.get("kabul_edilebilir", False),
                 "etkilenen_hucre": hucre}
        durum = _cozulebilir_mi(deneme, saniye)
        if durum is True:
            engelleyen.append(satir)
        elif durum is None:
            belirsiz.append(dict(satir, deneme_saniye=saniye))
    return engelleyen, belirsiz


def _cozulebilir_mi(girdi, saniye=10):
    """True: plan var (kanit) · False: plan yok (kanit) · None: sure doldu."""
    m = Model(girdi).kur()
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = cekirdek_sayisi()
    durum = c.Solve(m.m)
    if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return True
    if durum == cp_model.INFEASIBLE:
        return False
    return None


# ----------------------------------------------------------------------
# 3. En iyi plan -- K-10
# ----------------------------------------------------------------------

def _en_iyi_plan(girdi, ayar, saniye=30):
    """Sert KAPSAMA kisitlari gevsetilerek en iyi plan aranir.

    Gevsetilen yalniz kapsama: yasal kurallar (izin, dinlenme, gunluk azami)
    ASLA gevsetilmez -- gevsetilseydi K-20'yi cigneyen bir plan uretilirdi.
    """
    GEVSETILEBILIR = {"ASGARI_KAPSAMA", "ROL_KAPSAMASI", "YETKINLIK_KAPSAMASI"}
    kalan = [k for k in girdi.get("kurallar", []) or []
             if not (k.get("kod") in GEVSETILEBILIR and not k.get("yasal", False))]
    # K-67: HEDEF_ASIMI silinmez, YUMUSAK'a cevrilir -- silinse asim bedava
    # olurdu ve taslak plan hedefin cok ustune yazardi.
    kalan = [dict(k, tur="YUMUSAK") if (k.get("kod") == "HEDEF_ASIMI"
                                         and k.get("tur") == "SERT"
                                         and not k.get("yasal", False)) else k
             for k in kalan]
    gevsek = dict(girdi, kurallar=kalan)

    m = Model(gevsek).kur()
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = cekirdek_sayisi()
    if c.Solve(m.m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"var": False,
                "sebep": "kapsama gevsetildiginde bile cozum bulunamadi"}

    from .coz import _atamalari_cikar
    atamalar = _atamalari_cikar(m, c)
    return {
        # T-22: gevsetilmis model cozulebilir ama hicbir atama uretmeyebilir
        # (hicbir kural atamayi odullendirmiyorsa bos plan en ucuzudur).
        # Boyle bir plani "var" diye sunmak K-10'un sozunu bosa cikarir.
        "var": bool(atamalar),
        "atamalar": atamalar,
        "not": ("K-10: bu bir TASLAKTIR, otomatik kaydedilmez. Icindeki her "
                "ihlal bagimsiz dogrulayicidan gecirilmeli; yayin kapisi "
                "(#4.5) kabul_edilebilir bayragina bakar."),
        "gevsetilen_kurallar": sorted(
            {k["kod"] for k in girdi.get("kurallar", []) or []
             if (k.get("kod") in GEVSETILEBILIR or
                 (k.get("kod") == "HEDEF_ASIMI" and k.get("tur") == "SERT"))
             and not k.get("yasal", False)}),
    }


# ----------------------------------------------------------------------
# 4. Hedef asimi -- K-67
# ----------------------------------------------------------------------

def _asim_gevsek_plan(girdi, ayar, saniye=None):
    """K-67: HEDEF_ASIMI SERT iken cozumsuzluk -- YALNIZ asim YUMUSAK'a cevrilip
    model yeniden kurulur; obur butun sert kurallar AYNEN kalir. Iki adim:

      1. Amac YALNIZ toplam asim (kisi-saat): en az kac kisi fazla gerekiyor?
         Cozucu OPTIMAL derse bu sayi KANITLIDIR (`en_az_kanitli`); sure
         dolarsa bulunan en iyi sayidir, TAHMINDIR (K-37).
      2. Toplam asim o sayida sabitlenir, ilk adimin plani ipucu olur ve
         urunun normal amaci (obur yumusak kurallar) iyilestirilir -- taslak
         plan (K-10) "en az asimli planlarin en iyisi"ne yaklassin. Bu adim
         plan bulamazsa ilk adimin plani doner.

    Butce `teshis_asim_saniye` (varsayilan 30), iki adima yari yariya.
    Donen: (en_iyi_plan, asim_hucreleri); `asim_hucreleri`:
      {"hucreler": [{ekip, gun, saat, hedef, atanan, fazla}],
       "toplam_fazla", "en_az_kanitli", "saniye"}
    Yumusatilmis model de cozulemiyorsa tikanma asimda degildir: (None, None).
    """
    saniye = float(saniye if saniye is not None else (ayar or {}).get("teshis_asim_saniye", 30))
    tol = _ust_tolerans(girdi)
    kurallar = [dict(k, tur="YUMUSAK") if k.get("kod") == "HEDEF_ASIMI" else k
                for k in girdi.get("kurallar", []) or []]
    m = Model(dict(girdi, kurallar=kurallar)).kur()
    # K-68: sayilan, UST SINIRIN (hedef + tolerans) ustudur. Tolerans 0'da
    # m.asim'in kendisi (eski davranis birebir); degilse u >= asim - tolerans.
    if tol:
        ust = {}
        for k, v in m.asim.items():
            u = m.m.NewIntVar(0, max(0, len(m.calisanlar)), "ut_%d_%d" % (k[1], k[2]))
            m.m.Add(u >= v - tol)
            ust[k] = u
    else:
        ust = m.asim
    toplam_asim = sum(ust.values())
    normal_amac = sum(a * v for a, v in m.cezalar)

    # 1. adim: yalniz asim
    m.m.Minimize(toplam_asim)
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = saniye / 2.0
    c.parameters.num_search_workers = cekirdek_sayisi()
    durum = c.Solve(m.m)
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, None
    en_az = int(round(c.ObjectiveValue()))
    kanitli = durum == cp_model.OPTIMAL
    degerler = {}
    for t, gun, saat in m._hucreler():
        v = m.asim.get((t.get("ekip"), gun, saat))
        if v is not None:
            degerler[(t.get("ekip"), gun, saat)] = int(c.Value(v))   # hedefin ustu
    from .coz import _atamalari_cikar
    atamalar = _atamalari_cikar(m, c)

    # 2. adim: asim o sayida, normal amac
    proto = m.m.Proto()
    for i in range(len(proto.variables)):
        v = m.m.GetIntVarFromProtoIndex(i)
        m.m.AddHint(v, c.Value(v))
    m.m.Add(toplam_asim <= en_az)
    m.m.Minimize(normal_amac)
    c2 = cp_model.CpSolver()
    c2.parameters.max_time_in_seconds = saniye / 2.0
    c2.parameters.num_search_workers = cekirdek_sayisi()
    if c2.Solve(m.m) in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        atamalar = _atamalari_cikar(m, c2)
        for k, v in m.asim.items():
            degerler[k] = int(c2.Value(v))

    hucreler = []
    for t, gun, saat in m._hucreler():
        hedef_ustu = degerler.get((t.get("ekip"), gun, saat), 0)
        fazla = hedef_ustu - tol                 # ust sinirin ustu (K-68)
        if fazla > 0:
            h = {"ekip": t.get("ekip"), "gun": gun, "saat": saat,
                 "hedef": t.get("hedef"), "atanan": t.get("hedef") + hedef_ustu,
                 "fazla": fazla}
            if tol:
                h["ust_sinir"] = t.get("hedef") + tol
            hucreler.append(h)
    en_iyi = {
        "var": bool(atamalar),
        "atamalar": atamalar,
        "not": ("K-10/K-67: bu bir TASLAKTIR, otomatik kaydedilmez. HEDEF_ASIMI "
                "yumusatilarak bulundu; asim satirlari bagimsiz dogrulayicida "
                "SERT gorunur ve yayin kapisinda BILGI verir (durdurmaz) -- bu "
                "taslagi yayinlamak yoneticinin kararidir."),
        "gevsetilen_kurallar": ["HEDEF_ASIMI"],
    }
    asim = {"hucreler": hucreler,
            "toplam_fazla": sum(h["fazla"] for h in hucreler),
            "en_az_kanitli": kanitli,
            "saniye": saniye}
    return en_iyi, asim
