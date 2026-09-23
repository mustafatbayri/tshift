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

from .model import Model


def teshis_koy(girdi, kuruldu, istatistik, ayar):
    kapsam, hucre, gereken, mumkun = _nerede_tikaniyor(girdi, kuruldu)
    engelleyen = _engelleyen_kurallar(girdi, kuruldu, hucre)
    en_iyi = _en_iyi_plan(girdi, ayar)

    return {
        "durum": "cozumsuz",
        "motor_surumu": "0.2.0-cozucu",
        "teshis": {
            "kapsam": kapsam,
            "hucre": hucre,
            "gereken": gereken,
            "mumkun": mumkun,
            "engelleyen_kurallar": engelleyen,
        },
        "en_iyi_plan": en_iyi,
        "cozum_istatistikleri": istatistik,
        "uygulanmayan_notlar": kuruldu.notlar,
    }


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

def _engelleyen_kurallar(girdi, kuruldu, hucre):
    """Sert kurallari TEKER TEKER gevsetip hangisinin cozumu actigina bakar.

    Yavas ama dogru: "muhtemelen sudur" tahmini yerine kanit uretir.
    Yalniz SERT kurallar denenir; yumusak zaten engellemez.
    """
    sert = [k for k in girdi.get("kurallar", []) or []
            if k.get("tur") == "SERT" and k.get("aktif", True)]
    cikan = []
    for k in sert:
        kalan = [x for x in girdi["kurallar"] if x is not k]
        deneme = dict(girdi, kurallar=kalan)
        if _cozulebilir_mi(deneme):
            cikan.append({
                "kod": k["kod"],
                "yasal": k.get("yasal", False),
                "kabul_edilebilir": k.get("kabul_edilebilir", False),
                "etkilenen_hucre": hucre,
            })
    return cikan


def _cozulebilir_mi(girdi, saniye=10):
    m = Model(girdi).kur()
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = 8
    return c.Solve(m.m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


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
    gevsek = dict(girdi, kurallar=kalan)

    m = Model(gevsek).kur()
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = 8
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
             if k.get("kod") in GEVSETILEBILIR and not k.get("yasal", False)}),
    }
