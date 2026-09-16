# -*- coding: utf-8 -*-
"""
DENETLEYICI -- /evaluate ucunun govdesi (Master Spec v1.4 #11.4)

NE YAPAR
  Girdi + atamalar alir, ihlal listesi ve metrikler dondurur. Plan URETMEZ.

NE YAPMAZ -- ve bu bir eksiklik degil
  * Plan uretmez. Uretmek cozucunun isi (#11.2 /solve).
  * Ihlali DUZELTMEZ, oneri vermez. Oneri /suggest'in isi (#11.5).
  * Kurali degistirmez. Neyin aktif oldugunu girdi soyler.

SESSIZ GECMEME ILKESI
  Girdide aktif ama govdesi yazilmamis bir kural varsa, sonuc
  `uygulanmayan_kurallar` listesinde bunu ACIKCA bildirir. "Ihlal yok"
  demekle "bakmadim" demek ayni sey degildir; ikisini karistiran bir
  dogrulayici, yesil yanan ama hicbir sey sinamayan testten daha
  tehlikelidir.
"""

from . import kurallar, zaman


def _aktif_kurallar(girdi):
    for k in girdi.get("kurallar", []) or []:
        if k.get("aktif", True):
            yield k


def degerlendir(girdi, atamalar):
    """Master Spec #11.4: {'ihlaller': [...], 'metrikler': {...}}"""
    atamalar = atamalar or []
    ihlaller = []
    uygulanmayan = []

    for tanim in _aktif_kurallar(girdi):
        kod = tanim.get("kod")
        govde = kurallar.KAYIT.get(kod)
        if govde is None:
            uygulanmayan.append(kod)
            continue
        ihlaller.extend(govde(girdi, atamalar, tanim))

    return {
        "ihlaller": ihlaller,
        "metrikler": _metrikler(girdi, atamalar, ihlaller),
        "uygulanmayan_kurallar": uygulanmayan,
        "eksik_boyutlar": _eksik_boyutlar(girdi),
        "yayin_kapisi": yayin_kapisi(ihlaller),
    }


def _eksik_boyutlar(girdi):
    """Aktif bir kuralin, govdesi olmayan boyutlari.

    Kuralin KENDISI yazilmis ama bir PARCASI yazilmamis olabilir --
    ADALET_DENGESI'nin 'saat' boyutu boyle (T-13). `uygulanmayan_kurallar`
    bunu goremez, cunku kural listede var. Ayri bir alan gerekiyor:
    yoksa kural 'yazilmis' gorunur, bir boyutu sessizce atlanir.
    """
    eksik = []
    for tanim in _aktif_kurallar(girdi):
        if tanim.get("kod") != "ADALET_DENGESI":
            continue
        for boyut in (tanim.get("parametreler") or {}).get(
                "boyutlar", ["gece", "hafta_sonu", "saat"]):
            if kurallar._boyut_sayaci(boyut) is None:
                eksik.append({"kural": "ADALET_DENGESI", "boyut": boyut,
                              "sebep": "sayilabilir boyut degil; T-13"})
    return eksik


# ----------------------------------------------------------------------
# Metrikler -- #11.3
# ----------------------------------------------------------------------

def _metrikler(girdi, atamalar, ihlaller):
    sert = [i for i in ihlaller if i.get("agirlik") == "SERT"]
    hucre = kapsama_yuzdeleri(girdi, atamalar)
    toplam_net = sum(zaman.net_saat(a) for a in atamalar)

    fazla = 0.0
    kisi_saat = {}
    for a in atamalar:
        kisi_saat[a["calisan"]] = kisi_saat.get(a["calisan"], 0.0) + zaman.net_saat(a)
    for c in girdi.get("calisanlar", []):
        soz = (c.get("sozlesme") or {}).get("haftalik_saat")
        if soz is not None:
            fazla += max(0.0, kisi_saat.get(c["id"], 0.0) - soz)

    return {
        "sert_ihlal": len(sert),
        "yumusak_ihlal": len(ihlaller) - len(sert),
        "asgari_kapsama_yuzde": hucre["asgari_yuzde"],
        "hedef_kapsama_yuzde": hucre["hedef_yuzde"],
        "eksik_hedef_dakika": hucre["eksik_hedef_dakika"],
        "toplam_saat": toplam_net,
        "fazla_mesai_saat": fazla,
    }


def kapsama_yuzdeleri(girdi, atamalar):
    """Talep hucrelerinin ne kadarinin dolduguna bakar.

    Talep yoksa yuzde 100 doner -- 'sinanacak bir sey yoktu' demektir,
    'mukemmel' degil. A4 gibi yalitilmis senaryolarda talep bilerek bostur.
    """
    asgari_tut = asgari_top = hedef_tut = hedef_top = 0
    eksik_dk = 0
    for t in girdi.get("talep", []) or []:
        for gun in t.get("gunler", []):
            for saat in t.get("saatler", []):
                sayi = sum(1 for a in atamalar
                           if a.get("ekip") == t.get("ekip")
                           and zaman.atanmis_mi(a, gun, saat))
                if t.get("asgari") is not None:
                    asgari_top += 1
                    if sayi >= t["asgari"]:
                        asgari_tut += 1
                if t.get("hedef") is not None:
                    hedef_top += 1
                    if sayi >= t["hedef"]:
                        hedef_tut += 1
                    else:
                        eksik_dk += (t["hedef"] - sayi) * 60
    yuzde = lambda tut, top: 100.0 if top == 0 else round(100.0 * tut / top, 2)
    return {
        "asgari_yuzde": yuzde(asgari_tut, asgari_top),
        "hedef_yuzde": yuzde(hedef_tut, hedef_top),
        "eksik_hedef_dakika": eksik_dk,
    }


# ----------------------------------------------------------------------
# Yayin kapisi -- #4.5, K-16 / K-20 / K-24
# ----------------------------------------------------------------------

def yayin_kapisi(ihlaller):
    """Bu plan yayinlanabilir mi, yayinlanamazsa neden.

    Kapi `kabul_edilebilir` alanina bakar, `yasal`a DEGIL. Sebep K-24:
    CAKISMA_YOK yasal bir kural degil (hicbir kanun cakismayi yasaklamiyor)
    ama kabul de edilemez -- imkansizliktir.
    """
    acik_sert = [i for i in ihlaller
                 if i.get("agirlik") == "SERT" and i.get("durum") != "kabul_edildi"]
    engelleyen = [i for i in acik_sert if not i.get("kabul_edilebilir")]
    kabul_bekleyen = [i for i in acik_sert if i.get("kabul_edilebilir")]
    return {
        "yayinlanabilir": not acik_sert,
        "engelleyen_ihlaller": engelleyen,       # kabul secenegi SUNULMAZ
        "kabul_bekleyen_ihlaller": kabul_bekleyen,  # gerekceyle kabul edilebilir
        "kabul_secenegi_sunulur": bool(kabul_bekleyen) and not engelleyen,
    }
