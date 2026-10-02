# -*- coding: utf-8 -*-
"""
PLAN KALITESI OLCUMU  --  T-60 (2 Ekim)

NEDEN AYRI BIR BETIK
  `coz-olc.py` "plan BULUNUYOR mu, kac saniyede, sert ihlal var mi" olcer.
  T-60'in acik kalan yarisi baska bir soru: bulunan plan IYI mi? Elimizdeki
  tek sayi `optimuma_uzaklik_yuzde` ve tam olcekte %97-99 cikiyor. Bu sayi
  "plan kotu" DEMEK DEGIL: CP-SAT'in kanitlayabildigi alt sinir cok zayif,
  oran o zayif sinira gore. Bu betik orani uc tarafindan kusatir:

    1. AMAC NEYDEN OLUSUYOR  -- kural basina ceza kirilimi (amac_dagilimi).
       Hedef altinda kalan hucre mi, fazla mesai mi, adalet mi, mola mi?
    2. NE ZAMAN IYILESTI      -- iyilesme egrisi: toplam kazancin %50/%90/
       %99'una kacinci saniyede ulasildi? Son 10 saniyede hala iyilesiyorsa
       sure yetmiyor; 30. saniyede bitmisse sure fazla.
    3. KAPASITE TABANI        -- cozucuden BAGIMSIZ bir alt sinir: kadro her
       gun azami brut saat calissa bile hedefin ne kadari ACIKTA kalir?
       Hucre / ekip-gun / gun / hafta duzeyinde sayilir, en buyugu alinir.
       Planin hedef acigi bu tabana yakinsa "plan kotu" degil "kadro
       yetmiyor" demektir. (Bu tabana sayilmayan sert kurallar var --
       dinlenme, ardisik gun, gece sinirlari -- yani taban IYIMSERDIR;
       gercek en iyi plan tabanin ustunde kalabilir.)

  Ustune YAPILANDIRMALAR karsilastirilir -- ayni sahne, ayni makine, yalniz
  bir sey degisir:
    varsayilan   : urunun kostugu hal (iki asama acik)
    cift_butce   : ayni, sure IKI KATI            -> sure mi yetmiyor?
    ipucu_kapali : birinci asama (ipucu) kapali   -> ipucu yardim mi ediyor,
                                                     koturuyor mu?
    lp_guclu     : CP-SAT linearization_level=2   -> alt sinir guclenir mi
                                                     (kanit mi zayif, plan mi)?
  `--tekrar N` ayni yapilandirmayi N kez kosar: kosudan kosuya oynama
  olculmeden iki yapilandirma arasindaki fark "gurultu mu, gercek mi"
  bilinemez (28 Eylul: ayni girdi 21.905 ve 22.715 vermisti).

KOSTURMA (PowerShell)
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py kalite-olc.py --olcek 0.1 --saniye 120            ~49 kisi, 4 yapilandirma
  py kalite-olc.py --saniye 600                         tam olcek, UZUN (~1 saat)
  py kalite-olc.py --saniye 600 --yapilandirma varsayilan,lp_guclu
  py kalite-olc.py --olcek 0.1 --saniye 120 --tekrar 3 --yapilandirma varsayilan,ipucu_kapali --etiket tekrar3

  ⚠ Butce = ARAMA suresi (K-48); model kurma her yapilandirma icin yeniden
    yapilir ve ayrica yazilir (model tek kullanimliktir: `coz` onu degistirir).

SONUC NEREYE YAZILIR
  `kalite-olcumu-<olcek>-<doluluk>[-etiket].json` -- ayni klasore, her
  adimda. `--etiket` verilmezse ayni olcekteki onceki sonucun USTUNE yazar.
"""

import copy
import io
import json
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.model import Model                                # noqa: E402
from cozucu.coz import coz                                    # noqa: E402
from dogrulayici import degerlendir                           # noqa: E402


def _arg(ad, varsayilan, tur=str):
    if ad in sys.argv:
        return tur(sys.argv[sys.argv.index(ad) + 1])
    return varsayilan


SANIYE = _arg("--saniye", 120, int)
OLCEK = _arg("--olcek", 1.0, float)
DOLULUK = _arg("--doluluk", 0.95, float)
TEKRAR = _arg("--tekrar", 1, int)
ISCI = _arg("--isci", None, int)

# Yapilandirmalar: ad -> (aciklama, coz ayarlari, girdiye eklenen alanlar).
# Sure `SANIYE`ye gore. Girdi degisikligi sahnenin KOPYASINA uygulanir.
#
# ⚠ AGIRLIK DENEYI (fm_agirlik_*) -- urun karari DEGIL, teshis (Mustafa, 2
#   Ekim: "olcup karar vermeliyiz"). Urunde fazla mesai dakikasi 50 puan,
#   hedef altinda kalan kisi-saat 9 puan: motor 5,5 kisi-saat hedef acigini
#   1 dakika fazla mesaiye tercih eder. Agirlik `agirliklar` kapisiyla
#   dusurulup OLCULUR: hedef kapsamasi ne kadar yukseliyor, fazla mesai ne
#   kadar artiyor. Amac degerleri bu yapilandirmalarda KARSILASTIRILAMAZ
#   (olcek degisti); ham buyukluklere bakilir (ozet tablosu).
#     50 -> 5 : 1 saat fazla mesai = 300 puan = 33 kisi-saat hedef acigi
#     50 -> 1 : 1 saat fazla mesai =  60 puan =  6,7 kisi-saat hedef acigi
YAPILANDIRMALAR = {
    "varsayilan":   ("urunun kostugu hal: iki asama acik",
                     {}, {}),
    "cift_butce":   ("ayni ayarlar, arama suresi iki kati",
                     {"azami_saniye": SANIYE * 2}, {}),
    "ipucu_kapali": ("birinci asama (gecerli plan ipucu) kapali",
                     {"iki_asama_esigi": 10 ** 9}, {}),
    "lp_guclu":     ("CP-SAT linearization_level=2 (daha guclu LP, daha iyi alt sinir)",
                     {"cozucu_parametreleri": {"linearization_level": 2}}, {}),
    "fm_agirlik_5": ("TESHIS: fazla mesai agirligi 50 -> 5 (dakika basina)",
                     {}, {"agirliklar": {"FAZLA_MESAI": 5}}),
    "fm_agirlik_1": ("TESHIS: fazla mesai agirligi 50 -> 1 (dakika basina)",
                     {}, {"agirliklar": {"FAZLA_MESAI": 1}}),
    # T-60 bulgu 8 (2 Ekim): "ipucu demir atiyor, ipucusuz arama guvenilir
    # degil". Asagidakiler OLCUM secenekleridir; urunun varsayilani hicbirini
    # acmaz (09-motor/cozucu/coz.py VARSAYILAN, testler/test_demir_secenekleri.py).
    #   (a) birinci asama gecerli plani bulduktan sonra, molalar sabitken
    #       amacli iyilestirir; ana asamanin ipucu iyilesmis plan olur.
    #       Sure arama butcesinin ICINDEN gider.
    "a_ipuclu_120":   ("(a) birinci asamada 120 sn amacli iyilestirme, amacsiz plandan baslayarak",
                       {"ilk_asama_iyilestirme_saniye": 120}, {}),
    "a_ipucusuz_120": ("(a) birinci asamada 120 sn amacli iyilestirme, IPUCUSUZ (bulamazsa amacsiz plan kalir)",
                       {"ilk_asama_iyilestirme_saniye": 120,
                        "ilk_asama_iyilestirme_ipucusuz": True}, {}),
    "a_ipuclu_60":    ("(a) birinci asamada 60 sn amacli iyilestirme, amacsiz plandan baslayarak",
                       {"ilk_asama_iyilestirme_saniye": 60}, {}),
    #   2 Ekim gecesi tam olcek sonucu: (a) fazla mesaiyi 475-511 saatten
    #   60-100 saate indirdi ve kazancin cogu SABIT MOLALI 120 saniyede geldi
    #   (amacsiz 1,9-2,9 milyon -> 236-354 bin; ana asama ustune %6-12 ekledi).
    #   Iki soru: daha uzun sabit molali arama daha da iyi mi; molalarin
    #   yerini aramaktan cikarmak (Mustafa'nin sorusu) ne kazandirir?
    "a_ipuclu_240":   ("(a) birinci asamada 240 sn amacli iyilestirme (butcenin %40'i)",
                       {"ilk_asama_iyilestirme_saniye": 240}, {}),
    "sabit_mola_480": ("(a) aramanin neredeyse TAMAMI sabit molali modelde: 480 sn iyilestirme, kalan ana asama",
                       {"ilk_asama_iyilestirme_saniye": 480,
                        "ilk_asama_iyilestirme_orani": 0.85}, {}),
    #   (b) ana asamada ipuclu ve ipucusuz arama YAN YANA, ayni surede;
    #       isciler bolusulur, iyi olan plan secilir. Model bellekte iki kez.
    "b_paralel_3":    ("(b) ipuclu + ipucusuz yan yana; ipucusuza 3 isci, kalani ipucluya",
                       {"paralel_ipucusuz_isci": 3}, {}),
    "b_paralel_2":    ("(b) ipuclu + ipucusuz yan yana; ipucusuza 2 isci, kalani ipucluya",
                       {"paralel_ipucusuz_isci": 2}, {}),
}
VARSAYILAN_SECIM = "varsayilan,cift_butce,ipucu_kapali,lp_guclu"
SECILEN = _arg("--yapilandirma", VARSAYILAN_SECIM).split(",")
KAPASITE_TABANI = None          # main() doldurur; kosu() sinar
FAZLA_MESAI_TABANI = None


ETIKET = _arg("--etiket", "")       # dosya adina ek: --etiket tekrar3 -> ...-tekrar3.json


def dosya_adi():
    ad = ("kalite-olcumu-%d" % round(DOLULUK * 100) if OLCEK == 1.0
          else "kalite-olcumu-%g-%d" % (OLCEK, round(DOLULUK * 100)))
    if ETIKET:
        ad += "-" + ETIKET
    return os.path.join(BURASI, ad + ".json")


def yaz(d):
    with io.open(dosya_adi(), "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))


def sahne_yukle():
    from uret_veri_seti import sahne_uret
    if OLCEK == 1.0:
        ad = "_sahne-S30-%d.json" % round(DOLULUK * 100)
        g = json.load(io.open(os.path.join(BURASI, "fikstur", ad), encoding="utf-8"))
        print("SAHNE : %s" % ad)
    else:
        g = sahne_uret(OLCEK, DOLULUK)
        print("OLCEK %.2f (doluluk %%%d) -- sahne bellekten uretildi"
              % (OLCEK, round(DOLULUK * 100)))
    return g


# ---------------------------------------------------------------------------
# KAPASITE TABANI -- cozucuden bagimsiz alt sinir (kisi-saat)
# ---------------------------------------------------------------------------

def _izinli_gunler(c):
    return {i["gun"] for i in (c.get("izinler") or [])
            if i.get("durum", "onayli") == "onayli"}


def kapasite_tabani(g, k):
    """Hedefin (ve asgarinin) kac kisi-saati HICBIR planla kapanamaz?

    Dort duzeyde sayilir, her biri gecerli bir alt sinirdir, en buyugu alinir:
      hucre    : hucreyi kapatabilecek (o gun izinli olmayan, o saati kapsayan
                 bir sablona atanabilen) kisi sayisi hedeften azsa fark.
      ekip-gun : ekibin o gunku toplam hedef saati - ekibin sablonlarina
                 atanabilen kisilerin o gun verebilecegi azami brut saat.
      gun      : ayni sey butun ekipler birlikte (kisi bir kez sayilir).
      hafta    : haftalik toplam hedef - her kisinin en cok 6 gun x azami
                 brut saati (HAFTA_TATILI: bir gun bos).
    Kisi birden cok ekipte/hucrede sayilabilir -- bu bir GEVSETMEdir, taban
    bu yuzden iyimser kalir; gercek en iyi plan tabanin ALTINA inemez ama
    ustunde kalabilir. Sahada/molada ayrimi yapilmaz: HEDEF_KAPSAMA atanmis
    kisiyi sayar (molada olsa da), taban da oyle sayar.
    """
    from cozucu.model import _kural as kural_bul
    kisiler = {c["id"]: c for c in k.calisanlar}
    izin = {cid: _izinli_gunler(c) for cid, c in kisiler.items()}
    # (kisi, gun) -> o gun BASLAYABILECEGI sablonlar (modelin degisken
    # kumesinden: ekip suzgeci orada uygulanmis; izinli gun dusulur).
    secenek = {}
    for (cid, d, tid) in k.x:
        if d in izin[cid]:
            continue
        secenek.setdefault((cid, d), []).append(k.sablon[tid])
    # HAFTA_TATILI aktifse haftada en cok 6 gun, degilse 7. Gunde tek vardiya
    # modelde kosulsuz (_gunde_tek_vardiya).
    azami_gun = 6 if kural_bul(g, "HAFTA_TATILI") else 7

    def brut(t):
        return float(t["bit"]) - float(t["bas"])

    def gunde(t, bas_gun, d):
        """`bas_gun`de baslayan t sablonunun d gununde kalan saati (gece
        yarisini asan vardiya iki gune bolunur)."""
        a, b = bas_gun * 24 + float(t["bas"]), bas_gun * 24 + float(t["bit"])
        return max(0.0, min(b, (d + 1) * 24) - max(a, d * 24))

    def kapsiyor(t, bas_gun, d, saat):
        an = d * 24 + saat
        return bas_gun * 24 + float(t["bas"]) <= an < bas_gun * 24 + float(t["bit"])

    def arz_kisi(c, d, ekip=None):
        """c'nin d gununde verebilecegi en cok brut saat: o gun baslayan en
        uzun vardiya + onceki gun baslayip d'ye tasan en uzun parca."""
        cid = c["id"]
        bugun = max([gunde(s, d, d) for s in secenek.get((cid, d), [])
                     if ekip is None or k._sayilir(c, s, ekip)] or [0.0])
        dun = max([gunde(s, d - 1, d) for s in secenek.get((cid, d - 1), [])
                   if ekip is None or k._sayilir(c, s, ekip)] or [0.0])
        return bugun + dun

    sonuc = {}
    for alan in ("hedef", "asgari"):
        hucre = ekip_gun = gun = 0.0
        talep_eg, talep_g, devir_eg, toplam = {}, {}, {}, 0.0
        for t, d, saat in k._hucreler():
            istenen = t.get(alan) or 0
            if not istenen:
                continue
            ekip = t.get("ekip")
            toplam += istenen
            talep_eg[(ekip, d)] = talep_eg.get((ekip, d), 0) + istenen
            talep_g[d] = talep_g.get(d, 0) + istenen
            # K-56: onceki haftadan devreden kisi bu hucreyi zaten kapatiyor.
            devir = k._devir_sayisi(ekip, d, saat)
            devir_eg[(ekip, d)] = devir_eg.get((ekip, d), 0) + devir
            # hucre duzeyi: bu saati kapsayan bir sablona (bugun ya da dun
            # baslayan) atanabilen, ekibe sayilan kisiler
            aday = devir
            for cid, c in kisiler.items():
                if any(kapsiyor(s, d, d, saat) and k._sayilir(c, s, ekip)
                       for s in secenek.get((cid, d), [])) \
                   or any(kapsiyor(s, d - 1, d, saat) and k._sayilir(c, s, ekip)
                          for s in secenek.get((cid, d - 1), [])):
                    aday += 1
            hucre += max(0, istenen - aday)
        # ekip-gun duzeyi
        for (ekip, d), istenen in talep_eg.items():
            arz = sum(arz_kisi(c, d, ekip) for c in kisiler.values()) + devir_eg.get((ekip, d), 0)
            ekip_gun += max(0.0, istenen - arz)
        # gun duzeyi (kisi ekipten bagimsiz bir kez; devir ekip basina --
        # cok ekipli devir iki kez sayilabilir, bu gevsetmedir)
        for d, istenen in talep_g.items():
            arz = sum(arz_kisi(c, d) for c in kisiler.values()) \
                + sum(v for (e, dd), v in devir_eg.items() if dd == d)
            gun += max(0.0, istenen - arz)
        # hafta duzeyi: kisi basina en cok `azami_gun` vardiya, her biri o
        # gunun en uzun sablonu kadar brut saat (tasan parca dahil).
        arz_hafta = float(sum(devir_eg.values()))
        for cid in kisiler:
            gunluk = sorted((max([brut(s) for s in secenek.get((cid, d), [])] or [0.0])
                             for d in k.gunler), reverse=True)
            arz_hafta += sum(gunluk[:azami_gun])
        hafta = max(0.0, toplam - arz_hafta)
        sonuc[alan] = {"toplam_kisi_saat": toplam,
                       "taban_hucre": hucre, "taban_ekip_gun": round(ekip_gun, 1),
                       "taban_gun": round(gun, 1), "taban_hafta": round(hafta, 1),
                       "taban": round(max(hucre, ekip_gun, gun, hafta), 1)}
    return sonuc


def fazla_mesai_tabani(g, k):
    """Fazla mesainin kac dakikasi KACINILMAZ? (cozucuden bagimsiz alt sinir)

    SAAT_DENGESI SERT ise her tam zamanli en az borcu kadar (sozlesme saati,
    izin dusulmus) net dakika calismak ZORUNDA; vardiyalar ise kesikli (7,5
    saat, 9,5 saat...). Borcu tam tutturan bir vardiya karisimi yoksa asim
    kacinilmazdir: 5 x 7,5 + 1 x 9,5 = 47 saat, 2 saat fazla mesai -- bu
    plan kotu oldugu icin degil, sablonlar oyle oldugu icin.

    Kisi basina: gunlere o gun atanabilecegi sablonlarin net dakikalari ya
    da bos; en cok `azami_gun` calisma gunu; ulasilabilen toplamlar arasinda
    borcu karsilayan en kucuk asim. Dinlenme, ardisik gun, gece, kapsama
    kisitlari YOK SAYILIR -- taban bu yuzden iyimserdir (gercek en iyi plan
    tabanin ustunde kalabilir), ama hicbir plan altina inemez.
    """
    from cozucu.model import _kural as kural_bul, _net_saat, _borc_dakika
    sd = kural_bul(g, "SAAT_DENGESI")
    sert = bool(sd) and sd.get("tur") == "SERT"
    azami_gun = 6 if kural_bul(g, "HAFTA_TATILI") else 7
    izin = {c["id"]: _izinli_gunler(c) for c in k.calisanlar}
    secenek = {}
    for (cid, d, tid) in k.x:
        if d not in izin[cid]:
            secenek.setdefault((cid, d), set()).add(int(round(_net_saat(k.sablon[tid]) * 60)))
    toplam_dk, kisi, ulasilamayan, borc_toplam = 0, 0, 0, 0
    for c in k.calisanlar:
        soz = c.get("sozlesme") or {}
        tavan = soz.get("haftalik_saat")
        if soz.get("tip") == "yari_zamanli" or tavan is None:
            continue                       # model bu kisiye fm cezasi yazmaz
        kisi += 1
        tavan_dk = int(tavan * 60)
        borc = _borc_dakika(c) if (sert and soz.get("tip") == "tam_zamanli") else 0
        borc_toplam += borc
        # ulasilabilir[w] = w calisma gunuyle ulasilabilen toplam dakikalarin bit kumesi
        ulasilabilir = [1] + [0] * azami_gun
        for d in k.gunler:
            yeni = list(ulasilabilir)
            for w in range(azami_gun):
                if ulasilabilir[w]:
                    for dk in secenek.get((c["id"], d), ()):
                        yeni[w + 1] |= ulasilabilir[w] << dk
            ulasilabilir = yeni
        hepsi = 0
        for b in ulasilabilir:
            hepsi |= b
        # borcu karsilayan en kucuk toplam
        en_kucuk = None
        kalan = hepsi >> borc
        if kalan:
            # en dusuk set bit
            en_kucuk = borc + ((kalan & -kalan).bit_length() - 1)
        if en_kucuk is None:
            ulasilamayan += 1
            continue
        toplam_dk += max(0, en_kucuk - tavan_dk)
    return {"kisi": kisi, "saat": round(toplam_dk / 60.0, 2), "dakika": toplam_dk,
            "ceza": 50 * toplam_dk, "borcunu_tutturamayan": ulasilamayan,
            "saat_dengesi_sert": sert, "borc_toplam_saat": round(borc_toplam / 60.0, 1)}


def fazla_mesai_uyumu(model_saat, motor_saat, dogrulayici_saat):
    """Uc "fazla mesai" sayisi ayni mi; degilse HANGI ayrisma? (2 Ekim gecesi)

    Uc sayi: cozucunun CEZALADIGI (ceza degiskenlerinin toplami), motorun
    metrigi (plandan sayilir), dogrulayicinin metrigi (bagimsiz, plandan).

    ⚠ NEDEN TEK "BOZULDU" UYARISI YETMEDI
      900 sn'lik ipucusuz kosuda (2 Ekim) cezalanan 206,50, motor ve
      dogrulayici 199,00 cikti ve betik "K-57 bozuldu" yazdi. Tanim bozuk
      degildi: cozucu ceza degiskenini "fazla >= net - sozlesme" diye
      ESITSIZLIKLE tanimlar (cozucu/model.py); arama bitmeden kesilen
      planda degisken gercek degerin USTUNDE kalabilir. Plan dogru, cozucunun
      kendi hesabi siskin -- ve amac degeri de o kadar siskin.

    Donen: "ayni" | "ceza_gevsek" (motor == dogrulayici < cezalanan: plan
    saglam, amac degeri siskin) | "tanim_ayrisiyor" (motor != dogrulayici ya
    da cezalanan plandan KUCUK: K-57 gercekten bozulmus olabilir).
    """
    esit = lambda a, b: a is not None and b is not None and abs(a - b) < 0.01
    if esit(motor_saat, dogrulayici_saat):
        if esit(model_saat, motor_saat):
            return "ayni"
        if model_saat is not None and model_saat > motor_saat:
            return "ceza_gevsek"
    return "tanim_ayrisiyor"


def hedef_dokumu(ihlaller):
    """Hedef acigi ve asimi NEREDE? -- T-60 bulgu 10 (2 Ekim aksami).

    Toplam "1.200 kisi-saat eksik" acigin yerini soylemiyor: hangi ekip,
    hangi gun, hangi saat. 1 Ekim planinda 900 kisi-saat eksigin yaninda
    3.903 kisi-saat ASIM vardi -- saat yetmiyor degil, yanlis yere yazilmis.
    Bu ayrim hucre dokumu olmadan gorulemiyor ve 2 Ekim'in kalite dosyasi
    dokumu saklamiyordu.

    Kaynak BAGIMSIZ DOGRULAYICININ ihlal listesidir (HEDEF_KAPSAMA ve
    HEDEF_ASIMI satirlari: ekip, gun, saat, olculen = atanan kisi, gereken =
    hedef); cozucunun kendi sayimi degil.

    Donen: {"ekip": {ekip: {"eksik_kisi_saat", "asim_kisi_saat",
    "eksik_hucre", "asim_hucre"}}, "toplam": {...ayni dort alan},
    "hucreler": [[ekip, gun, saat, atanan, hedef], ...]} -- yalniz hedeften
    SAPAN hucreler, (ekip, gun, saat) sirali.
    """
    bos = lambda: {"eksik_kisi_saat": 0, "asim_kisi_saat": 0, "eksik_hucre": 0, "asim_hucre": 0}
    ekip, toplam, hucreler = {}, bos(), []
    for i in ihlaller or []:
        if i.get("kural") not in ("HEDEF_KAPSAMA", "HEDEF_ASIMI"):
            continue
        atanan, hedef = i.get("olculen"), i.get("gereken")
        if atanan is None or hedef is None or atanan == hedef:
            continue
        e = ekip.setdefault(i.get("ekip"), bos())
        if atanan < hedef:
            alan, hucre, fark = "eksik_kisi_saat", "eksik_hucre", hedef - atanan
        else:
            alan, hucre, fark = "asim_kisi_saat", "asim_hucre", atanan - hedef
        for d in (e, toplam):
            d[alan] += fark
            d[hucre] += 1
        hucreler.append([i.get("ekip"), i.get("gun"), i.get("saat"), atanan, hedef])
    hucreler.sort(key=lambda h: (str(h[0]), h[1], h[2]))
    return {"ekip": ekip, "toplam": toplam, "hucreler": hucreler}


def fazla_mesai_kisiler(k, c):
    """Planda fazla mesaisi olan kisiler: sozlesme, borc, net saat, fazla ve
    gun gun vardiya karisimi (gun:sablon). Modelin kendi net tanimiyla
    (_net_saat: butun molalar dusuk)."""
    from cozucu.model import _net_saat, _borc_dakika
    kisiler = {x["id"]: x for x in k.calisanlar}
    net = {}
    vardiya = {}
    for a in c.get("atamalar") or []:
        t = k.sablon.get(a.get("sablon"))
        if t is None:
            continue
        net[a["calisan"]] = net.get(a["calisan"], 0.0) + _net_saat(t)
        vardiya.setdefault(a["calisan"], []).append("%d:%s" % (a["gun"], a["sablon"]))
    cikan = []
    for cid, x in kisiler.items():
        soz = x.get("sozlesme") or {}
        tavan = soz.get("haftalik_saat")
        if tavan is None or soz.get("tip") == "yari_zamanli":
            continue
        fazla = net.get(cid, 0.0) - tavan
        if fazla > 1e-6:
            cikan.append({"calisan": cid, "sozlesme": tavan, "borc_saat": _borc_dakika(x) / 60.0,
                          "net_saat": round(net.get(cid, 0.0), 2), "fazla_saat": round(fazla, 2),
                          "vardiyalar": sorted(vardiya.get(cid, []), key=lambda v: int(v.split(":")[0])),
                          "kilit": sum(1 for kk in (k.girdi.get("kilitler") or []) if kk.get("calisan") == cid),
                          "uygunluk": len(x.get("uygunluk") or []),
                          "izin": len(x.get("izinler") or [])})
    return sorted(cikan, key=lambda r: -r["fazla_saat"])


# ---------------------------------------------------------------------------
# TEK KOSU
# ---------------------------------------------------------------------------

def kosu(g, ad, ayar, girdi_ek=None):
    print("\n  [%s]  %s" % (ad, YAPILANDIRMALAR[ad][0]))
    print("         kuruluyor...")
    sys.stdout.flush()
    if girdi_ek:
        g = copy.deepcopy(g)
        g.update(copy.deepcopy(girdi_ek))        # ornegin agirliklar (teshis deneyi)
    t0 = time.time()
    k = Model(copy.deepcopy(g)).kur()
    kurma = time.time() - t0
    tam_ayar = {"azami_saniye": SANIYE}
    if ISCI:
        tam_ayar["isci_sayisi"] = ISCI
    tam_ayar.update(ayar)
    print("         kurma %.0f sn  |  cozuluyor (arama en fazla %d sn)..."
          % (kurma, tam_ayar["azami_saniye"]))
    sys.stdout.flush()
    t1 = time.time()
    c = coz(g, tam_ayar, kuruldu=k)
    sure = time.time() - t1
    ist = c.get("cozum_istatistikleri") or {}
    m = c.get("metrikler") or {}
    s = {"yapilandirma": ad, "ayar": {a: v for a, v in tam_ayar.items()},
         "girdi_ek": girdi_ek or {},
         "kurma_sn": round(kurma, 1), "toplam_sn": round(sure, 1),
         "durum": c.get("durum")}
    for alan in ("durma_sebebi", "iki_asama", "cozum_sayisi", "amac_degeri", "alt_sinir",
                 "ilk_asama_sn", "ana_asama_butce_sn", "ilk_cozum_sn", "isci_sayisi",
                 "amac_dagilimi", "iyilesme", "ilk_asama_iyilestirme", "paralel"):
        s[alan] = ist.get(alan)
    s["optimuma_uzaklik_yuzde"] = m.get("optimuma_uzaklik_yuzde")
    s["metrikler"] = m
    if c.get("durum") != "cozuldu":
        print("         DURUM: %s  (%s)" % (c.get("durum"), ist.get("durma_sebebi")))
        return s
    r = degerlendir(g, c["atamalar"])
    sayi = {}
    for i in r.get("ihlaller", []):
        sayi[i["kural"]] = sayi.get(i["kural"], 0) + 1
    s["ihlal"] = sayi
    s["sert_ihlal"] = sum(1 for i in r.get("ihlaller", [])
                          if i.get("agirlik") == "SERT" and not i.get("gecmis"))
    s["yayinlanabilir"] = (r.get("yayin_kapisi") or {}).get("yayinlanabilir")
    s["hedef_dokumu"] = hedef_dokumu(r.get("ihlaller", []))
    s["dogrulayici_metrikler"] = {a: (r.get("metrikler") or {}).get(a)
                                  for a in ("hedef_kapsama_yuzde", "asgari_kapsama_yuzde",
                                            "fazla_mesai_saat", "sozlesme_ustu_ucret_saat",
                                            "toplam_saat")}
    iy = s["iyilesme"] or {}
    print("         %.0f sn  |  %s  |  amac %s  |  alt sinir %s  |  uzaklik %%%s  |  cozum %s"
          % (sure, s["durma_sebebi"], s["amac_degeri"], s["alt_sinir"],
             s["optimuma_uzaklik_yuzde"], s["cozum_sayisi"]))
    print("         ilk plan %s sn  |  kazancin %%50'si %s sn, %%90'i %s sn, %%99'u %s sn  |  son iyilesme %s sn"
          % (s["ilk_cozum_sn"], iy.get("yuzde50_sn"), iy.get("yuzde90_sn"),
             iy.get("yuzde99_sn"), iy.get("son_iyilesme_sn")))
    print("         sert ihlal %d  |  yayinlanabilir %s  |  hedef kapsama %%%s  |  eksik hedef %s kisi-saat  |  fazla mesai (motor metrigi) %s saat"
          % (s["sert_ihlal"], s["yayinlanabilir"], m.get("hedef_kapsama_yuzde"),
             (m.get("eksik_hedef_dakika") or 0) / 60.0, m.get("fazla_mesai_saat")))
    hd = s["hedef_dokumu"]
    print("         hedef dokumu (dogrulayici): eksik %d kisi-saat (%d hucre)  |  ASIM %d kisi-saat (%d hucre)"
          % (hd["toplam"]["eksik_kisi_saat"], hd["toplam"]["eksik_hucre"],
             hd["toplam"]["asim_kisi_saat"], hd["toplam"]["asim_hucre"]))
    for e_ad, e in sorted(hd["ekip"].items(), key=lambda kv: str(kv[0])):
        print("           %-12s eksik %5d kisi-saat (%3d hucre)   asim %5d kisi-saat (%3d hucre)"
              % (e_ad, e["eksik_kisi_saat"], e["eksik_hucre"], e["asim_kisi_saat"], e["asim_hucre"]))
    b = s.get("ilk_asama_iyilestirme")
    if b:
        print("         (a) birinci asama iyilestirmesi: %s sn (%s)  |  amacsiz plan %s -> iyilesmis %s  |  plan %s, cozum %s"
              % (b["saniye"], "ipucusuz" if b["ipucusuz"] else "ipuclu", b["amacsiz_amac"],
                 b["iyilesmis_amac"], "bulundu" if b["plan_bulundu"] else "BULUNAMADI (amacsiz ipucu kaldi)",
                 b["cozum_sayisi"]))
    p = s.get("paralel")
    if p:
        for ad in ("ipuclu", "ipucusuz"):
            print("         (b) %-8s %d isci  |  %s  |  amac %s  |  ilk plan %s sn  |  cozum %s%s"
                  % (ad, p[ad]["isci"], "plan var" if p[ad]["plan_bulundu"] else "PLAN YOK",
                     p[ad]["amac_degeri"], p[ad]["ilk_cozum_sn"], p[ad]["cozum_sayisi"],
                     "   <-- SECILEN" if p["secilen"] == ad else ""))
    for kural, d in (s["amac_dagilimi"] or {}).items():
        print("           %-16s ceza %10d  (%%%5.1f)   ham %8d   degisken %6d"
              % (kural, d["ceza"], d["pay_yuzde"], d["deger"], d["degisken"]))
    # FAZLA MESAI KIMDE, HANGI VARDIYA KARISIMIYLA? Taban sifirsa bile plan
    # fazla mesai yaziyorsa sebebi kisi duzeyinde gorulmeli (kilit mi,
    # uygunluk mu, dinlenme mi, yoksa cozucu mu bulamadi).
    s["fazla_mesai_kisiler"] = fazla_mesai_kisiler(k, c)
    for satir in s["fazla_mesai_kisiler"][:8]:
        print("           fm %-10s sozlesme %2s saat, borc %5.1f, net %5.1f, fazla %4.1f saat | %s"
              % (satir["calisan"], satir["sozlesme"], satir["borc_saat"], satir["net_saat"],
                 satir["fazla_saat"], " ".join(satir["vardiyalar"])))
    # TABANIN GECERLILIK SINAMASI: hicbir plan tabanin altina inemez. Inerse
    # taban YANLIS hesaplanmistir ve "kadro yetmiyor" cumlesi kurulamaz.
    kt = KAPASITE_TABANI or {}
    d = (s["amac_dagilimi"] or {}).get("HEDEF_KAPSAMA")
    if d and kt.get("hedef") and d["deger"] < kt["hedef"]["taban"]:
        s["taban_gecersiz"] = True
        print("         !!! KAPASITE TABANI GECERSIZ: plan %d kisi-saat acik birakti, taban %s diyordu"
              % (d["deger"], kt["hedef"]["taban"]))
    d = (s["amac_dagilimi"] or {}).get("FAZLA_MESAI")
    fm = FAZLA_MESAI_TABANI or {}
    if d and fm and d["deger"] < fm["dakika"]:
        s["taban_gecersiz"] = True
        print("         !!! FAZLA MESAI TABANI GECERSIZ: plan %d dakika, taban %d dakika diyordu"
              % (d["deger"], fm["dakika"]))
    return s


def ozet(sonuc):
    """Yapilandirmalari yan yana: amac, alt sinir, uzaklik, egri esikleri."""
    kosular = sonuc["kosular"]
    if not kosular:
        return
    print("\n%-14s %6s %10s %10s %8s %7s %7s %7s %7s %7s %5s"
          % ("yapilandirma", "sn", "amac", "alt sinir", "uzaklik", "ilk sn",
             "%50 sn", "%90 sn", "%99 sn", "cozum", "sert"))
    taban = kosular[0].get("amac_degeri")
    for s in kosular:
        if s.get("amac_degeri") is None:
            print("%-14s %6s  plan yok: %s (%s)" % (s["yapilandirma"], s.get("toplam_sn"),
                                                   s.get("durum"), s.get("durma_sebebi")))
            continue
        iy = s.get("iyilesme") or {}
        fark = ("%+.1f%%" % (100.0 * (s["amac_degeri"] - taban) / taban)
                if taban and s.get("amac_degeri") is not None else "")
        print("%-14s %6s %10s %10s %7s%% %7s %7s %7s %7s %7s %5s  %s"
              % (s["yapilandirma"], s.get("toplam_sn"), s.get("amac_degeri"),
                 s.get("alt_sinir"), s.get("optimuma_uzaklik_yuzde"),
                 s.get("ilk_cozum_sn"), iy.get("yuzde50_sn"), iy.get("yuzde90_sn"),
                 iy.get("yuzde99_sn"), s.get("cozum_sayisi"), s.get("sert_ihlal"), fark))
    # Kapasite tabani ile kiyas: planin hedef acigi tabanin kac kati?
    kt = sonuc.get("kapasite_tabani") or {}
    for s in kosular:
        d = (s.get("amac_dagilimi") or {}).get("HEDEF_KAPSAMA")
        if d and kt.get("hedef"):
            taban_ks = kt["hedef"]["taban"]
            print("  %-14s hedef acigi %d kisi-saat, kapasite tabani %s kisi-saat%s"
                  % (s["yapilandirma"], d["deger"], taban_ks,
                     ("  -> acigin en az %%%.0f'i kadro yetersizliginden"
                      % (100.0 * taban_ks / d["deger"])) if d["deger"] and taban_ks else ""))
    # Fazla mesai: plan tabanin ne kadar ustunde? Modelin cezasindan
    # turetilen saat ile motor metrigi / dogrulayici metrigi ayni sayi mi?
    fm = sonuc.get("fazla_mesai_tabani") or {}
    for s in kosular:
        d = (s.get("amac_dagilimi") or {}).get("FAZLA_MESAI")
        m = s.get("metrikler") or {}
        if d and m.get("fazla_mesai_saat") is not None:
            model_saat = d["deger"] / 60.0
            dogrulayici_saat = (s.get("dogrulayici_metrikler") or {}).get("fazla_mesai_saat")
            uyum = fazla_mesai_uyumu(model_saat, m["fazla_mesai_saat"], dogrulayici_saat)
            s["fazla_mesai_uyumu"] = uyum
            uyari = {"ayni": "",
                     "ceza_gevsek": "   <-- CEZA DEGISKENI GEVSEK: plan %.2f saat, cozucu %.2f saat cezaladi (amac degeri %d puan siskin; K-57 bozulmadi)"
                                    % (m["fazla_mesai_saat"], model_saat,
                                       round((model_saat - m["fazla_mesai_saat"]) * 60 * (d["ceza"] / float(d["deger"]) if d["deger"] else 0))),
                     "tanim_ayrisiyor": "   <-- UC SAYI AYNI DEGIL (K-57 bozuldu)"}[uyum]
            print("  %-14s fazla mesai (yasal, K-57): modelin cezaladigi %.2f saat (kacinilmaz taban %.1f saat) | motor metrigi %.2f saat | dogrulayici metrigi %s saat%s"
                  % (s["yapilandirma"], model_saat, fm.get("saat", 0.0), m["fazla_mesai_saat"],
                     ("%.2f" % dogrulayici_saat) if dogrulayici_saat is not None else None,
                     uyari))
            sou = (s.get("dogrulayici_metrikler") or {}).get("sozlesme_ustu_ucret_saat")
            if sou is not None:
                print("  %-14s sozlesme ustu ucretli saat (ayri alan, fazla mesai DEGIL): %.1f saat" % (s["yapilandirma"], sou))
    # Bagimsiz alt sinir: HEDEF_KAPSAMA tabani x agirligi + fazla mesai tabani.
    # Oteki kurallarin tabani 0 sayilir. CP-SAT'in sinirindan buyukse,
    # "optimuma uzaklik" en az bu kadar KUCULUR.
    he_agirlik = None
    for s in kosular:
        d = (s.get("amac_dagilimi") or {}).get("HEDEF_KAPSAMA")
        if d and d["deger"]:
            he_agirlik = d["ceza"] / float(d["deger"])
            break
    bagimsiz = (fm.get("ceza") or 0) + (he_agirlik or 0) * ((kt.get("hedef") or {}).get("taban") or 0)
    for s in kosular:
        if s.get("amac_degeri"):
            print("  %-14s bagimsiz alt sinir %d  ->  uzaklik en cok %%%.1f  (CP-SAT siniri %s -> %%%s)"
                  % (s["yapilandirma"], bagimsiz,
                     100.0 * (s["amac_degeri"] - max(bagimsiz, s.get("alt_sinir") or 0)) / s["amac_degeri"],
                     s.get("alt_sinir"), s.get("optimuma_uzaklik_yuzde")))
    sonuc["bagimsiz_alt_sinir"] = bagimsiz
    # HAM BUYUKLUKLER: amac degeri agirliga bagli, bu tablo degil. Agirlik
    # deneyinde (fm_agirlik_*) karsilastirma YALNIZ burada yapilir.
    print("\n%-14s %10s %10s %9s %9s %9s %8s %8s" % (
        "yapilandirma", "fm saat", "hedef eks.", "hedef %", "asim k-s", "adalet", "mola", "sert"))
    for s in kosular:
        d = s.get("amac_dagilimi") or {}
        m = s.get("metrikler") or {}
        if not d:
            continue
        ham = lambda kural: (d.get(kural) or {}).get("deger", 0)
        print("%-14s %10.1f %10d %9s %9d %9d %8d %8s" % (
            s["yapilandirma"], ham("FAZLA_MESAI") / 60.0, ham("HEDEF_KAPSAMA"),
            m.get("hedef_kapsama_yuzde"), ham("HEDEF_ASIMI"), ham("ADALET_DENGESI"),
            ham("MOLA_KAPSAMASI"), s.get("sert_ihlal")))


def main():
    g = sahne_yukle()
    sonuc = {"olcek": OLCEK, "doluluk": DOLULUK, "saniye": SANIYE, "tekrar": TEKRAR,
             "kisi": len(g["calisanlar"]), "hucre": len(g["talep"]),
             "kural": len(g["kurallar"]), "yapilandirmalar": SECILEN,
             # Hangi makinede, ne zaman: baska makinede olculen sure/amac
             # bu makine icin TAHMIN degildir (28 Eylul dersi).
             "tarih": time.strftime("%Y-%m-%d %H:%M"), "cekirdek": os.cpu_count(),
             "kosular": []}
    print("SAHNE : %(kisi)d kisi, %(hucre)d hucre, %(kural)d kural  |  arama %(saniye)d sn  |  tekrar %(tekrar)d" % sonuc)
    for ad in SECILEN:
        if ad not in YAPILANDIRMALAR:
            print("bilinmeyen yapilandirma: %s (olanlar: %s)" % (ad, ", ".join(YAPILANDIRMALAR)))
            return

    print("\n0/%d  Kapasite tabani (cozucuden bagimsiz)..." % len(SECILEN))
    t = time.time()
    global KAPASITE_TABANI, FAZLA_MESAI_TABANI
    k0 = Model(copy.deepcopy(g)).kur()
    kt = kapasite_tabani(g, k0)
    sonuc["kapasite_tabani"] = KAPASITE_TABANI = kt
    fm = fazla_mesai_tabani(g, k0)
    sonuc["fazla_mesai_tabani"] = FAZLA_MESAI_TABANI = fm
    sonuc["degisken"] = len(k0.m.Proto().variables)
    sonuc["kisit"] = len(k0.m.Proto().constraints)
    del k0
    for alan in ("hedef", "asgari"):
        v = kt[alan]
        print("     %-6s toplam %.0f kisi-saat | taban: hucre %.0f, ekip-gun %.0f, gun %.0f, hafta %.0f  ->  EN AZ %.0f kisi-saat acik kalir"
              % (alan, v["toplam_kisi_saat"], v["taban_hucre"], v["taban_ekip_gun"],
                 v["taban_gun"], v["taban_hafta"], v["taban"]))
    print("     fazla mesai: %d sozlesmeli kisi, SAAT_DENGESI sert: %s, borc toplami %.0f saat  ->  EN AZ %.1f saat fazla mesai kacinilmaz (ceza en az %d)%s"
          % (fm["kisi"], fm["saat_dengesi_sert"], fm["borc_toplam_saat"], fm["saat"], fm["ceza"],
             ("  | borcunu HICBIR karisimla tutturamayan: %d kisi" % fm["borcunu_tutturamayan"])
             if fm["borcunu_tutturamayan"] else ""))
    print("     (%.0f sn; %d degisken, %d kisit)" % (time.time() - t, sonuc["degisken"], sonuc["kisit"]))
    yaz(sonuc)

    for n, ad in enumerate(SECILEN, 1):
        for tekrar in range(TEKRAR):
            print("\n%d/%d  %s%s" % (n, len(SECILEN), ad,
                                     ("  (tekrar %d/%d)" % (tekrar + 1, TEKRAR)) if TEKRAR > 1 else ""))
            try:
                s = kosu(g, ad, dict(YAPILANDIRMALAR[ad][1]), YAPILANDIRMALAR[ad][2])
            except Exception as e:                       # olcum devam etsin, hata yazilsin
                s = {"yapilandirma": ad, "durum": "ISTISNA", "hata": str(e)[:400]}
                print("         ISTISNA: %s" % s["hata"])
            s["tekrar"] = tekrar + 1
            sonuc["kosular"].append(s)
            yaz(sonuc)

    ozet(sonuc)
    yaz(sonuc)
    print("\nSonuc yazildi: %s" % os.path.basename(dosya_adi()))


if __name__ == "__main__":
    main()
