# -*- coding: utf-8 -*-
"""
ONARIM DONGUSU -- Master Spec v1.4 #11.7

NE YAPAR
  /solve'un govdesi. Uc adim:

    1. Cozucu plan uretir            (cozucu/)
    2. BAGIMSIZ dogrulayici denetler (dogrulayici/)
    3. Sert ihlal varsa en fazla 2 onarim denemesi; hala varsa `cozumsuz`

NEDEN AYRI BIR DOSYA -- #7.6 bunu yasaklamiyor mu?
  Hayir, tersine: #7.6 DOGRULAYICININ COZUCUYLE MANTIK PAYLASMAMASINI sart
  kosar. `cozucu/` hala `dogrulayici/`den hicbir sey import etmiyor ve tersi
  de dogru. Ikisini de USTTEN cagiran bir katman, #11.7'nin tarif ettigi
  mimarinin ta kendisi:

      "Motor plan uretir, DOGRULAYICI denetler. Sert ihlal varsa..."

  Bu dongu cozucunun ICINE yazilsaydi motor kendi isini kendi onaylamis
  olurdu -- kacinilan sey tam olarak budur.

  Kural somut halde: cozucu/ ve dogrulayici/ birbirini import etmez.
  Bu dosya ikisini de import eder. testler/test_bagimsizlik.py bunu sinar.

ONARIM NE DEMEK
  Dogrulayici "C03, gun 2'de sert ihlal var" diyorsa, o calisan-gun cifti
  bir sonraki denemede KAPATILIR ve model yeniden kosar. Ihlal listesi
  geri beslenir -- #11.7 adim 2'nin "ihlal listesiyle birlikte" ifadesi
  budur.

  Denetim HER ZAMAN KULLANICININ GIRDISIYLE yapilir, onarim icin eklenen
  kilitlerle degil. Yoksa ikinci turda dogrulayici, motorun kendi koydugu
  koltuk degneklerini "kural" sanip onaylardi.

SINIR NEDEN VAR -- #11.7
  "Her deneme sure ve maliyet demektir. Sinirsiz deneme, kullaniciyi
   belirsiz sure bekletir." K-28 ile ayni gerekce.

ELLER BOS DONULMEZ -- K-10
  Uc deneme de yetmezse durum `cozumsuz` olur AMA uretilen son plan
  `en_iyi_plan` olarak dondurulur. Taslaktir, otomatik kaydedilmez.
"""

from cozucu import coz
from dogrulayici import degerlendir

AZAMI_ONARIM = 2          # #11.7 adim 2


def coz_ve_onar(girdi, ayar=None, azami_onarim=AZAMI_ONARIM):
    yasaklar = []
    gunluk = []
    cikti = None

    for tur in range(azami_onarim + 1):
        cikti = coz(_kilitle(girdi, yasaklar), ayar)
        cikti.setdefault("cozum_istatistikleri", {})["onarim_denemesi"] = tur

        if cikti.get("durum") != "cozuldu":
            # Cozucu teshis dondurdu (#11.3). Onarim burada biter -- ama
            # T-22: elde DENETLENECEK PLAN VAR. `en_iyi_plan` yoneticinin
            # gerekceyle onaylayacagi taslaktir (K-10) ve denetlenmeden
            # donuyordu. Onarim bitti demek, denetim bitti demek degil.
            cikti["onarim_gunlugu"] = gunluk
            return _taslagi_denetle(girdi, cikti)

        rapor = degerlendir(girdi, cikti.get("atamalar") or [])
        sert = [i for i in rapor["ihlaller"] if i.get("agirlik") == "SERT"]
        cikti["bagimsiz_denetim"] = _denetim_ozeti(rapor, sert)

        if not sert:
            cikti["onarim_gunlugu"] = gunluk
            return cikti

        yeni = _yasak_cikar(sert, yasaklar)
        gunluk.append({
            "tur": tur,
            "sert_ihlal": len(sert),
            "kurallar": sorted({i["kural"] for i in sert}),
            "yasaklanan": [{"calisan": e, "gun": g} for e, g in yeni],
        })

        if not yeni:
            # Ihlaller belirli bir calisan-gun ciftine baglanamadi (ornegin
            # kapsama ihlali). Kapatacak bir sey yok; tekrar denemek ayni
            # sonucu verir. Durup bildirmek, bos yere 2 tur donmekten iyi.
            cikti["onarim_gunlugu"] = gunluk
            return _cozumsuz(cikti, gunluk, "ihlal_hedeflenemedi")

        yasaklar.extend(yeni)

    # Butun denemeler tukendi, dogrulayici hala sert ihlal goruyor -- adim 3.
    return _cozumsuz(cikti, gunluk, "onarim_sinirina_ulasildi")


# ----------------------------------------------------------------------

def _kilitle(girdi, yasaklar):
    """Onarim yasaklarini `kilitler` listesine ekleyip YENI bir girdi dondurur.

    Kullanicinin girdisi DEGISTIRILMEZ: denetim onunla yapilacak.
    """
    if not yasaklar:
        return girdi
    eklenen = [{"calisan": e, "gun": g, "tip": "yasak",
                "_kaynak": "onarim_dongusu"} for e, g in yasaklar]
    return dict(girdi, kilitler=list(girdi.get("kilitler") or []) + eklenen)


def _yasak_cikar(sert, zaten):
    """Ihlallerden kapatilabilir calisan-gun ciftlerini cikarir."""
    var = set(zaten)
    yeni = []
    for i in sert:
        e, g = i.get("calisan"), i.get("gun")
        if e is None or g is None:
            continue
        if (e, g) in var:
            continue
        var.add((e, g))
        yeni.append((e, g))
    return yeni


def _taslagi_denetle(girdi, cikti):
    """T-22: cozumsuzlukte sunulan taslagi bagimsiz dogrulayicidan gecirir.

    NEDEN GEREKLI
      `en_iyi_plan`in kendi notu "icindeki her ihlal bagimsiz dogrulayicidan
      gecirilmeli" diyordu; geciren yoktu. Sonuc: EN COK aciklama gereken
      plan, EN AZ denetlenen plandi. Yonetici K-10 uyarinca bu taslagi
      gerekceyle onayliyor ve neyi onayladigini goremiyordu.

    NEDEN `girdi` -- ve bu satir goruldugunden onemli
      `en_iyi_plan` uretilirken ASGARI_KAPSAMA gibi kapsama kurallari
      BILEREK gevsetilir (teshis._en_iyi_plan). Denetim o gevsetilmis
      girdiyle yapilsaydi dogrulayici gevsetilen kurali hic gormez, taslak
      tertemiz gorunurdu -- denetim eklenmis ama ise yaramaz olurdu.
      Kullanicinin girdisinde kural hala aktiftir; denetim onunla yapilir.
      Ayni gerekce onarim dongusunun kendisinde de yaziliydi.

    `var` ALANI
      Atama sayisi sifirsa plan yoktur. Bunu burada da duzeltiyoruz cunku
      bu yol `_cozumsuz`dan gecmez.
    """
    plan = cikti.get("en_iyi_plan")
    atamalar = (plan or {}).get("atamalar") or []
    if plan is not None:
        plan["var"] = bool(atamalar)

    rapor = degerlendir(girdi, atamalar)
    sert = [i for i in rapor["ihlaller"] if i.get("agirlik") == "SERT"]
    cikti["bagimsiz_denetim"] = _denetim_ozeti(rapor, sert)
    return cikti


def _denetim_ozeti(rapor, sert):
    """Motorun kendi metrigi DEGIL -- bagimsiz dogrulayicinin sayilari.

    #16.1: motorun "0 sert ihlal" bayragina bakilmaz. Bu blok ciktida ayri
    durur ki iki sayi karsilastirilabilsin.
    """
    return {
        "sert_ihlal": len(sert),
        "yumusak_ihlal": rapor["metrikler"]["yumusak_ihlal"],
        "ihlaller": sert,
        "uygulanmayan_kurallar": rapor["uygulanmayan_kurallar"],
        "eksik_boyutlar": rapor["eksik_boyutlar"],
        "yayin_kapisi": rapor["yayin_kapisi"],
    }


def _cozumsuz(cikti, gunluk, sebep):
    """#11.7 adim 3 + K-10: cozumsuz de, ama plani elde tut."""
    return {
        "durum": "cozumsuz",
        "motor_surumu": cikti.get("motor_surumu"),
        "sebep": sebep,
        "teshis": {
            "kapsam": "kural",
            "aciklama": ("Cozucu plan uretti ama BAGIMSIZ dogrulayici sert "
                         "ihlal buluyor. Ikisi ayni kurali farkli yorumluyor "
                         "olabilir; once bagimsiz_denetim.ihlaller okunmali."),
            "engelleyen_kurallar": sorted(
                {k for t in gunluk for k in t["kurallar"]}),
        },
        "en_iyi_plan": {
            # T-22: sifir atamali plan "var" diyemez. K-10'un sozu "eller
            # bos donulmez"ti; bos bir plani var saymak o sozu bosa cikarir.
            "var": bool(cikti.get("atamalar")),
            "atamalar": cikti.get("atamalar") or [],
            "not": ("K-10: bu bir TASLAKTIR, otomatik kaydedilmez. Icinde "
                    "dogrulayicinin bildirdigi sert ihlaller VARDIR; yayin "
                    "kapisi (#4.5) bunlara bakar."),
        },
        "metrikler": cikti.get("metrikler"),
        "bagimsiz_denetim": cikti.get("bagimsiz_denetim"),
        "cozum_istatistikleri": cikti.get("cozum_istatistikleri"),
        "onarim_gunlugu": gunluk,
        "uygulanmayan_notlar": cikti.get("uygulanmayan_notlar"),
    }
