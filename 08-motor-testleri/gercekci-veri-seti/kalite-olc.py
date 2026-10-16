# -*- coding: utf-8 -*-
"""
PLAN KALITESI OLCUMU  --  T-60 (2 Ekim)

NEDEN AYRI BIR BETIK
  `coz-olc.py` "plan BULUNUYOR mu, kac saniyede, sert ihlal var mi" olcer.
  T-60'in acik kalan yarisi baska bir soru: bulunan plan IYI mi? Elimizdeki
  tek sayi `optimuma_uzaklik_yuzde` ve tam olcekte %97-99 cikiyor. Bu sayi
  "plan kotu" DEMEK DEGIL: CP-SAT'in kanitlayabildigi alt sinir cok zayif,
  oran o zayif sinira gore. Bu betik orani uc tarafindan kusatir:

  ⚠ 6 Ekim DUZELTMESI (T-60 bulgu 20): yukaridaki okuma YANLIS cikti. Sinir
    zayif degildi, PLANLAR kotuydu: tam modelin (ortak arama) bu sahnede
    kanitladigi en iyi sinir 21.098 (2 Ekim, 900 sn; oteki kosularda
    19.769-20.934; DENGELI). Bugun bilinen en iyi plan 26.589 (sinira en cok
    %21 uzak); o kosularin planlari 112 bin - 1,8 milyondu.
    Ayrica K-60'tan (4 Ekim) beri ana asama MOLA ADIMI: atamalar sabitken
    cozucunun siniri yalniz "bu atamalarla en iyi mola yerlesimi"ni kanitlar,
    planin tamami icin sinir DEGILDIR (O-16). O kosularda `alt_sinir` ve
    `optimuma_uzaklik_yuzde` None'dir; adimin siniri `mola_adimi_alt_sinir`.

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
                   ⚠ 6 Ekim, K-61: urunun hali artik ONCE FAZLA MESAISIZ
                     arar. `varsayilan`, `profil_*`, `cift_butce`, `lp_guclu`
                     bu tarihten sonra onu ICERIR; 6 Ekim oncesinin hali
                     `fm_once_kapali`. Eski kayit yapilandirmalari
                     (k59_hali, a_*, sabit_mola_480, mola_*, b_*, oran_90,
                     eski_urun_hali, fm_agirlik_*) kapali sabitlenmistir:
                     olctukleri sey degismesin. Her kosunun kaydinda
                     `once_fazla_mesaisiz` alani kosuda secenegin ACIK olup
                     olmadigini soyler (ayar; uygulanip uygulanmadigi
                     `fazla_mesai_once_sifir` alanindadir). Alan 6 Ekim
                     22:45'ten sonraki kayitlarda var; daha eski kayitlarda
                     secenek `ayar` sozlugunden okunur (bulgu 21'in
                     kaydinda acikca `true`, ondan oncekilerde yok = kapali).
                   ⚠ 7 Ekim, O-18: 6 Ekim gecesi olculen hal SERT KESIMDI
                     (fazla mesaisiz plan bulununca fazla mesai butun
                     asamalarda 0'da tutuluyordu). Bu Mustafa'nin ilkesini
                     cigniyordu (hakem agirliklardir); urun yolu duzeltildi:
                     bulunan plan yalniz baslangic noktasi, alanlar geri
                     acilir. Sert kesim olcum yapilandirmasi olarak duruyor
                     (`fm_sert`, `fm_sert_kapsama`; bulgu 21'in kaydi bu
                     haldir). Duzeltilmis yolun tam olcekli olcumu: `fm_once`
                     / `fm_once_kapsama` (= `varsayilan` / `profil_kapsama`).
                   ⚠ 7 Ekim, bulgu 25: fazla mesaisiz ilk arama 18 kosunun
                     1'inde 120 sn'de bulunamadi (plan 30 saat fazla mesaiyle).
                     `fm_once_deneme3` / `_kapsama`: ayni yol, arama 3 x 40 sn
                     farkli tohumla (`fazla_mesaisiz_deneme: 3`); kayitta
                     `fazla_mesai_once_sifir.denemeler`. K-63 ile ana asama
                     plansiz donerse ikinci asamanin plani alinir; kayitta
                     `ipucu_plani` ve `durma_sebebi: mola_adimi_yetismedi`.
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
  K-66 (11 Ekim): her cozulen kosunun CIZELGESI de yazilir --
  `planlar/<olcum-dosyasi-adi>/<yapilandirma>-<tekrar>.json` (urun bicimi:
  motorun #11.3 ciktisi + dogrulayicinin #11.4 raporu) ve `.html` (okunur).
  `--plansiz` kapatir. Ayrinti: cizelge.py.
"""

import copy
import importlib
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
import cizelge                                                # noqa: E402  (K-66: her kosu cizelge yazar)

# Motorun VARSAYILAN ayarlari: bir yapilandirma bir secenegi YAZMIYORSA
# kosuda gecerli olan deger budur (K-61: "once fazla mesaisiz" varsayilan
# acik). `cozucu.coz` adi fonksiyona cozuldugu icin modul boyle alinir.
COZ_VARSAYILAN = importlib.import_module("cozucu.coz").VARSAYILAN


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
KAPALI = {"fazla_mesai_once_sifir": False}     # 6 Ekim oncesinin yolu (kayit yapilandirmalari)
SERT = {"fazla_mesai_once_sifir": True,        # 6 Ekim gecesinin sert kesimi (bulgu 21; OLCUM)
        "fazla_mesai_sifirda_tut": True}
YAPILANDIRMALAR = {
    # ⚠ K-60 (4 Ekim): urunun varsayilani UC ASAMA -- gecerli plan, molalar
    #   sabitken iyilestirme (%80), MOLA ADIMI (atamalar sabit, kanitli
    #   optimum). Eski "ortak arama" yapilandirmalari anlamlarini korusun diye
    #   `mola_adimi: False` tasir; onlar 2-3 Ekim olcumlerinin kaydidir.
    # ⚠ K-61 (6 Ekim, Mustafa: "Evet"): "ONCE FAZLA MESAISIZ" urunun
    #   varsayilani. Urun halini olcen yapilandirmalar (`varsayilan`,
    #   `profil_*`, `cift_butce`, `lp_guclu`) onu motorun varsayilanindan
    #   ALIR. 6 Ekim oncesinin kayit yapilandirmalari `KAPALI` tasir.
    # ⚠ O-18 (7 Ekim): urun yolu = once fazla mesaisiz ARA, bulunca o plandan
    #   agirlikli aramaya devam et (alanlar acik). Sert kesim (`SERT`) yalniz
    #   olcum; bulgu 21 o haldir.
    "varsayilan":   ("urunun kostugu hal: once fazla mesaisiz 3 x 40 sn (K-61 kapanisi, 8 Ekim; asim sertken 1 x 20 sn, K-68 ayar 4), bulunca o plandan agirlikli arama (K-61/O-18), molalar sabitken iyilestirme (K-59, %80), gevsek yolda fazla mesai onarimi iyilestirmenin sonunda KOMSULUK aramasiyla (K-68 ayar 3; 15 Ekim), mola adimi (K-60)",
                     {}, {}),
    # K-68 ayar 2'nin olcum secenegi (13 Ekim 23:20): gevsek yolun acik adimi
    #   150 sn'lik parcalarla, her parcada baska tohumla (bulgu 25'in kuyruk
    #   dersi; acik adim 52-204 sn, bir kez > 300 sn). Geri kalani urun yolu.
    "gevsek_parca": ("urun yolu + gevsek acik adim 150 sn'lik parcalarla yeniden baslar (K-68 ayar 2 olcum secenegi)",
                     {"gevsek_acik_parca_saniye": 150}, {}),
    # Oneri 2b (14 Ekim, Mustafa: "ok"): VS1'de acik adim 287 / 793 / > 1.226 /
    #   > 1.226 sn. Ilk plani bulmaya yonelik CP-SAT ayarlari YALNIZ acik adimda
    #   (geri kalani urun yolu). OLCUM secenekleri; urun `{}`.
    "acik_lin0":    ("urun yolu + gevsek acik adimda LP yok (linearization_level 0) -- oneri 2b olcum secenegi",
                     {"gevsek_acik_cozucu_parametreleri": {"linearization_level": 0}}, {}),
    "acik_ls":      ("urun yolu + gevsek acik adim yalniz yerel arama (use_ls_only) -- oneri 2b olcum secenegi",
                     {"gevsek_acik_cozucu_parametreleri": {"use_ls_only": True}}, {}),
    # 15 Ekim: fazla mesai onarimi KOMSULUK aramasiyla urun yolu oldu (VS1 500'de
    #   butun-model onarimi 7/7 bulamadi). `onarim_tam` = 14 Ekim'in butun-model
    #   onarimi, kiyas icin ACIKCA yazili.
    # 16 Ekim (ekili 500: fm'siz plan KESIN varken acik adim 27 kisiye fazla mesai
    #   yazdi, onarim geri alamadi): acik adim fazla mesai [0,0] ile; bulursa 0'da
    #   tutulur, bulamazsa "sure yetmedi" (olcum; urun yolu degil).
    "gevsek_fm0":   ("urun yolu + gevsek yolun ACIK ADIMI fazla mesai 0 ile (bulursa 0'da tutulur; bulamazsa sure yetmedi) -- 16 Ekim olcum secenegi",
                     {"gevsek_fazla_mesai_sifir": True}, {}),
    "onarim_tam":   ("urun yolu + fazla mesai onarimi BUTUN modelle (14 Ekim davranisi) -- komsuluk kiyasi",
                     {"fazla_mesai_onarim_yontemi": "tam"}, {}),
    # ⚠ 8 Ekim (K-61 kapanisi): motorun varsayilani 3 deneme oldu. `fm_once*`
    #   bulgu 23'un kaydidir (7 Ekim sabahi, TEK deneme) -- anlami degismesin
    #   diye `fazla_mesaisiz_deneme: 1` ACIKCA yazili. Bugunku urun yolu
    #   `varsayilan` / `profil_kapsama` (= `fm_once_deneme3*`).
    "fm_once":      ("7 Ekim sabahinin urun yolu (bulgu 23 kaydi): once fazla mesaisiz plan TEK denemeyle, bulunursa ipucu -- alanlar GERI ACILIR, karari agirliklar verir; DENGELI",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False,
                      "fazla_mesaisiz_deneme": 1}, {}),
    "fm_once_kapsama": ("7 Ekim sabahinin urun yolu (bulgu 23 kaydi), KAPSAMA profili; TEK deneme",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False,
                      "fazla_mesaisiz_deneme": 1}, {"profil": "KAPSAMA"}),
    # T-60 bulgu 25 (7 Ekim): fazla mesaisiz ilk arama 18 kosunun 1'inde 120
    #   sn'de bulunamadi -> plan 30 saat fazla mesaiyle (116.976). Kuyruk
    #   olcumu (kuyruk.py, 35 deneme): medyan 7,5 sn, en uzun 62 sn. Yeniden
    #   baslatma: 120 sn'lik pay 3 x 40 sn'ye bolunur, her deneme farkli tohum
    #   (`fazla_mesaisiz_deneme: 3`). Karar kurali (kosudan once): 900 sn x
    #   3'te fazla mesai 0 ve amac `fm_once` duzeyinde, hicbir kosu
    #   "bulunamadi" yoluna dusmemis, politika kipinde 20'de 0 bulunamayan ->
    #   varsayilan 3, K-61 kapanir. OLCULDU (8 Ekim 00:10): 26.498 / 26.700 /
    #   26.736, fazla mesai 0, hepsi ilk denemede; politika 20/20 -> kural
    #   tuttu, varsayilan 3. Bu adlar 8 Ekim kaydinin adlari olarak duruyor
    #   (= bugunku `varsayilan`).
    "fm_once_deneme3": ("URUN YOLU + YENIDEN BASLATMA (bulgu 25; 8 Ekim'den beri = varsayilan): fazla mesaisiz arama 3 x 40 sn, farkli tohum; DENGELI",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False,
                      "fazla_mesaisiz_deneme": 3}, {}),
    "fm_once_deneme3_kapsama": ("URUN YOLU + YENIDEN BASLATMA (bulgu 25; = profil_kapsama), KAPSAMA profili",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False,
                      "fazla_mesaisiz_deneme": 3}, {"profil": "KAPSAMA"}),
    # K-65 (11 Ekim): VARDIYA_ROTASYON_YONU amac terimi. "Once/sonra" kiyasi icin
    #   kuralin agirligi 0 (terim susar; metrik ve dogrulayici yine sayar).
    #   Gercek "once" 11 Ekim'den onceki kodun kosusudur (rotasyon-once-900).
    "rotasyon_0":   ("URUN YOLU, VARDIYA_ROTASYON_YONU agirligi 0 (K-65 kiyasi; kural susar, metrik sayar); DENGELI",
                     {}, {"agirliklar": {"VARDIYA_ROTASYON_YONU": 0}}),
    "fm_sert":      ("SERT KESIM (6 Ekim gecesinin hali, bulgu 21; OLCUM): fazla mesaisiz plan bulunursa fazla mesai butun asamalarda 0'da TUTULUR; DENGELI",
                     dict(SERT), {}),
    "fm_sert_kapsama": ("SERT KESIM (bulgu 21; OLCUM), KAPSAMA profili",
                     dict(SERT), {"profil": "KAPSAMA"}),
    "fm_once_kapali": ("6 Ekim ONCESININ urun hali: once fazla mesaisiz KAPALI, DENGELI (kiyas; bulgu 20'nin kosulari)",
                     dict(KAPALI), {}),
    "fm_once_kapali_kapsama": ("6 Ekim ONCESININ urun hali: once fazla mesaisiz KAPALI, KAPSAMA profili",
                     dict(KAPALI), {"profil": "KAPSAMA"}),
    "k59_hali":     ("3 Ekim urun hali (K-59): %40 iyilestirme + ~347 sn ORTAK arama (atamalar + molalar birlikte)",
                     dict(KAPALI, ilk_asama_iyilestirme_orani=0.4, mola_adimi=False), {}),
    #   5 Ekim 21:28 olculdu (bulgu 19, 600 sn, ucer kosu): %90 ile %80
    #   arasinda fark yok (fazla mesai 28-45 saat her ikisinde, eksik/asim/
    #   mola ayni); mola adimina 44-47 sn kaldi, optimum 40,5-42,9 sn'de --
    #   pay 1-5 sn. %80 KALDI. Yapilandirma kayit icin duruyor.
    "oran_90":      ("K-60 kalibrasyon kaydi (bulgu 19): iyilestirme payi %90 -- fark yok, %80 kaldi",
                     dict(KAPALI, ilk_asama_iyilestirme_orani=0.9), {}),
    # URUN HALI, UC PROFIL (5 Ekim karari: urun hali olcumleri 900 sn'de --
    #   K-35'in onerilen secenegi; 600 sn A/B kiyaslari icin). Sahne DENGELI
    #   profille yazili; asagidakiler yalniz `profil` alanini degistirir.
    "profil_kapsama": ("urun hali, KAPSAMA profili (agirlik tablosu #5.4)",
                     {}, {"profil": "KAPSAMA"}),
    "profil_calisan": ("urun hali, CALISAN profili (agirlik tablosu #5.4; fazla mesai tavani 0)",
                     {}, {"profil": "CALISAN"}),
    # OLCUM (6 Ekim, bulgu 20): "ONCE FAZLA MESAISIZ". Uc profil olcumunde
    #   CALISAN (fazla mesai tavani 0 -> sert) uc kosuda da 0 saat fazla
    #   mesaiyle plan buldu; o planlar DENGELI agirliklariyla 26.589-26.703,
    #   DENGELI'nin kendi buldugu 105.742-148.431 (fazla mesai disi kismi
    #   26.931-26.992, %0,2 oynuyor). Birinci asama gecerli plani fazla mesai
    #   degiskenleri 0'a sabitken arar. 6 Ekim gecesinin hali: bulursa fazla
    #   mesai butun asamalarda 0'da kalir (SERT KESIM -- simdi yalniz olcum,
    #   `fm_sert*`). Urun yolu (7 Ekim, O-18): bulunan plan ipucudur, alanlar
    #   geri acilir, karari agirliklar verir (`fm_once*`). Bulamazsa her iki
    #   halde alanlar geri acilir, onceki yol isler.
    #   Kiyas: ayni profilin `varsayilan` / `profil_kapsama` kosulari
    #   (kalite-olcumu-95-profiller-900.json, 6 Ekim sabahi, ayni makine).
    #   Bulgu 21'in kaydi (kalite-olcumu-95-fmsifir-900.json) bu adlarla
    #   yazildi. O kosuda secenek 6 Ekim gecesinin SERT KESIMIYDI (O-18):
    #   ayni olcumu bugun `fm_sert` / `fm_sert_kapsama` verir; bu ikisi
    #   kaydin adlari olarak sert kesime SABITLENDI (olctukleri degismesin).
    "fm_once_sifir": ("bulgu 21 kaydi (6 Ekim, sert kesim = fm_sert): once fazla mesaisiz plan, DENGELI -- bulunursa fazla mesai 0'da TUTULUR; bulunamazsa onceki yol",
                     dict(SERT), {}),
    "fm_once_sifir_kapsama": ("bulgu 21 kaydi (6 Ekim, sert kesim = fm_sert_kapsama): KAPSAMA profili",
                     dict(SERT), {"profil": "KAPSAMA"}),
    "eski_urun_hali": ("K-59 oncesi urun hali (2 Ekim): iyilestirme KAPALI, ortak arama (kiyas icin)",
                     dict(KAPALI, ilk_asama_iyilestirme_saniye=0, mola_adimi=False), {}),
    "cift_butce":   ("ayni ayarlar, arama suresi iki kati",
                     {"azami_saniye": SANIYE * 2}, {}),
    "ipucu_kapali": ("birinci asama (gecerli plan ipucu) kapali -- K-61'den beri 'once fazla mesaisiz' da birinci asamada oldugundan o da kapali: varsayilandan IKI sey farkli",
                     {"iki_asama_esigi": 10 ** 9}, {}),
    "lp_guclu":     ("CP-SAT linearization_level=2 (daha guclu LP, daha iyi alt sinir)",
                     {"cozucu_parametreleri": {"linearization_level": 2}}, {}),
    #   K-61: bu agirliklarda kisayolun kosulu zaten tutmaz (5 < 9); 2
    #   Ekim'in kaydiyla birebir ayni kalsin diye acikca kapali.
    "fm_agirlik_5": ("TESHIS: fazla mesai agirligi 50 -> 5 (dakika basina)",
                     dict(KAPALI), {"agirliklar": {"FAZLA_MESAI": 5}}),
    "fm_agirlik_1": ("TESHIS: fazla mesai agirligi 50 -> 1 (dakika basina)",
                     dict(KAPALI), {"agirliklar": {"FAZLA_MESAI": 1}}),
    # T-60 bulgu 8 (2 Ekim): "ipucu demir atiyor, ipucusuz arama guvenilir
    # degil". Asagidakiler OLCUM secenekleridir. (a) 3 Ekim'den beri URUNUN
    # VARSAYILANI (K-59; K-60 ile %80); mola adimi 4 Ekim'den beri urunun
    # varsayilani (K-60). Ipucusuz (a) ve (b) olcum secenegi olarak duruyor
    # (09-motor/cozucu/coz.py VARSAYILAN, testler/test_demir_secenekleri.py).
    # Buradaki (a)/(b) kayitlari 2-3 Ekim'in ORTAK aramali halini olcer:
    # `mola_adimi: False`.
    #   (a) birinci asama gecerli plani bulduktan sonra, molalar sabitken
    #       amacli iyilestirir; ana asamanin ipucu iyilesmis plan olur.
    #       Sure arama butcesinin ICINDEN gider.
    "a_ipuclu_120":   ("(a) birinci asamada 120 sn amacli iyilestirme, amacsiz plandan baslayarak; ortak arama",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=120, mola_adimi=False), {}),
    "a_ipucusuz_120": ("(a) birinci asamada 120 sn amacli iyilestirme, IPUCUSUZ (bulamazsa amacsiz plan kalir); ortak arama",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=120,
                            ilk_asama_iyilestirme_ipucusuz=True, mola_adimi=False), {}),
    "a_ipuclu_60":    ("(a) birinci asamada 60 sn amacli iyilestirme, amacsiz plandan baslayarak; ortak arama",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=60, mola_adimi=False), {}),
    #   2 Ekim gecesi tam olcek sonucu: (a) fazla mesaiyi 475-511 saatten
    #   60-100 saate indirdi ve kazancin cogu SABIT MOLALI 120 saniyede geldi
    #   (amacsiz 1,9-2,9 milyon -> 236-354 bin; ana asama ustune %6-12 ekledi).
    #   Iki soru: daha uzun sabit molali arama daha da iyi mi; molalarin
    #   yerini aramaktan cikarmak (Mustafa'nin sorusu) ne kazandirir?
    "a_ipuclu_240":   ("(a) birinci asamada 240 sn amacli iyilestirme (butcenin %40'i); ortak arama (= k59_hali)",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=240, mola_adimi=False), {}),
    "sabit_mola_480": ("(a) aramanin neredeyse TAMAMI sabit molali modelde: 480 sn iyilestirme, kalan ORTAK arama",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=480,
                            ilk_asama_iyilestirme_orani=0.85, mola_adimi=False), {}),
    #   MOLA AYRI ADIM (3 Ekim, Mustafa'nin sorusu "molalar motorun hesabindan
    #   ciksin mi?"): sabit_mola_480 ile AYNI birinci asama (480 sn sabit
    #   molali iyilestirme), TEK FARK ana asamada ATAMALAR SABIT -- kalan
    #   ~107 sn'de yalniz molalar aranir. Ayri bir mola adiminin mola
    #   sirasinda kapsamayi ne kadar geri aldigini olcer; sabit_mola_480 ayni
    #   surede atamalari da oynatabildiginden ikisi yan yana kosulur
    #   (3 Ekim sabahki 480 kosularinda sabit molali planin mola kapsamasi
    #   kaydedilmiyordu; simdi `amac_dagilimi` ile kaydediliyor). Ana asamaya
    #   kalan 107 sn'nin plan verdigi olculdu: ilk plan 56-57 sn'de
    #   (kalite-olcumu-95-mola-600.json, bulgu 15-16).
    "mola_ayri_adim": ("mola ayri adim (bulgu 17 kaydi): sabit_mola_480 ile ayni ilk asama, atamalar SABIT, genel %2 boslukta erken durur",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=480,
                            ilk_asama_iyilestirme_orani=0.85,
                            mola_adimi=True, mola_adimi_hedef_bosluk=0.02), {}),
    #   3 Ekim 18:21 (bulgu 17): mola_ayri_adim 29 sn'de durdu -- "hedef
    #   boslugu %2" TOPLAM amacin boslugu, toplamin %70-77'si sabit fazla
    #   mesai; mola teriminin kendi boslugu daha genisti (en iyi ihtimalle
    #   ham ~170-186'ya inebilirdi, 445-535'te kaldi). KONTROLLU OLCUM
    #   (Mustafa, 19:09: "kontrollu olcumle gidelim"): ayni adim, erken
    #   durma KAPALI -- kalan ~107 sn'yi (ya da optimuma kadar) kullanir.
    #   Kiyas: varsayilan (K-59: 240 sn sabit molali + ~347 sn ortak arama).
    #   4 Ekim: bu yapilandirma K-60 ile URUNUN VARSAYILANI oldu (600 sn'de
    #   `varsayilan` ile ayni: %80 = 480 sn, mola adimi, hedef_bosluk 0).
    "mola_adimi_tam": ("mola adimi TAM (bulgu 18 kaydi; 600 sn'de 6 Ekim oncesinin varsayilani -- once fazla mesaisiz KAPALI): 480 sn iyilestirme, atamalar SABIT, kanitli optimuma kadar",
                       dict(KAPALI, ilk_asama_iyilestirme_saniye=480,
                            ilk_asama_iyilestirme_orani=0.85,
                            mola_adimi=True, mola_adimi_hedef_bosluk=0.0), {}),
    #   (b) ana asamada ipuclu ve ipucusuz arama YAN YANA, ayni surede;
    #       isciler bolusulur, iyi olan plan secilir. Model bellekte iki kez.
    "b_paralel_3":    ("(b) ipuclu + ipucusuz yan yana; ipucusuza 3 isci, kalani ipucluya; ortak arama",
                       dict(KAPALI, paralel_ipucusuz_isci=3, mola_adimi=False), {}),
    "b_paralel_2":    ("(b) ipuclu + ipucusuz yan yana; ipucusuza 2 isci, kalani ipucluya; ortak arama",
                       dict(KAPALI, paralel_ipucusuz_isci=2, mola_adimi=False), {}),
}
VARSAYILAN_SECIM = "varsayilan,cift_butce,ipucu_kapali,lp_guclu"
SECILEN = _arg("--yapilandirma", VARSAYILAN_SECIM).split(",")
KAPASITE_TABANI = None          # main() doldurur; kosu() sinar
FAZLA_MESAI_TABANI = None


ETIKET = _arg("--etiket", "")       # dosya adina ek: --etiket tekrar3 -> ...-tekrar3.json
# K-66 (Mustafa, 11 Ekim): "tum kosumlarda cizelge hazir olsun". Her cozulen
#   kosunun plani urun biciminde (#11.3 cikti + #11.4 dogrulama) ve okunur
#   HTML olarak planlar/<olcum-dosyasi-adi>/<yapilandirma>-<tekrar>.json|.html
#   dosyalarina yazilir. --plansiz ile kapatilir (yalniz hizli duman icin).
PLANSIZ = "--plansiz" in sys.argv
# K-62 / K-67 (12 Ekim): `--seviye 1` -> merdivenin seviye 1 seti
#   (fikstur/_sahne-L1-95[-olcek].json; talep referans plandan, HEDEF_ASIMI
#   SERT). Referansin bu sahnedeki puani kayittan okunur ve her kosunun
#   yanina kalem kalem yazilir (K-62 ilke 3). Verilmezse S30 seti (tarihsel).
SEVIYE = _arg("--seviye", None)
# 13 Ekim (bulgu 31): `--cesit asim_yumusak|eski_asgari|pay1|tol1|tol2` -> seviye 1.den
#   turetilmis ayirma cesidi (merdiven.CESITLER); referans puani o sahnede
#   yeniden hesaplanir. Dosya adina cesit eklenir.
CESIT = _arg("--cesit", None)
# 14 Ekim: `--kaynak veri-seti` -> seviye 1 seti depodaki veri setinden
#   (10-veri-seti/<merdiven.VERI_SETI_SURUM>; merdiven.py --kaynak). Dosya adina
#   -VS<n> eklenir (14 Ekim gunduz -VS1, aksamdan sonra -VS2). `--veri-seti v1`
#   eski surumle kosar (merdiven okur; kiyas icin).
KAYNAK = _arg("--kaynak", "uretec")
# 14 Ekim 22:09 (Mustafa): "kosu sonuclarina optimum hesaplamasinin detaylarini
#   ekle -- puan puan, % bilgileriyle, ne ne kadar etkiledi". Her kosunun
#   sonunda OPTIMUM HESABI bolumu (optimum_hesabi / optimum_yazisi); kayitli
#   bir sonuc dosyasi icin: `py kalite-olc.py --optimum-raporu <sonuc.json>`.
OPTIMUM_RAPORU = _arg("--optimum-raporu", None)
# 15 Ekim 08:48: gece blogu bilgisayarin kendi kendine yeniden baslamasiyla
#   kesildi (3.600 x 3 adimi 39. dakikada). `--devam`: ayni adla kayitli sonuc
#   dosyasi varsa yuklenir, tamamlanmis (yapilandirma, tekrar) ciftleri
#   ATLANIR, eksikler kosulur; kesilen blok ayni komutla kaldigi yerden surer.
DEVAM = "--devam" in sys.argv
# 16 Ekim (A3): `--sahne <dosya>` -> hazir bir sahne dosyasi (insan plani sahnesi, 06-veri/anonim/insan;
#   `_merdiven.referans_puani` varsa kiyas yapilir, yoksa/oturmadiysa yalniz kalemler). Dosya adina
#   sahnenin `ad`i gelir (kalite-olcumu-INSAN-2026-06-22-...). --seviye ile birlikte verilmez.
SAHNE_DOSYASI = _arg("--sahne", None)
PLAN_KLASORU = _arg("--plan-klasoru", None)   # verilmezse planlar/<olcum-dosyasi-adi>/ (testler gecici klasor verir)


def dosya_adi():
    ad = ("kalite-olcumu-%d" % round(DOLULUK * 100) if OLCEK == 1.0
          else "kalite-olcumu-%g-%d" % (OLCEK, round(DOLULUK * 100)))
    if SEVIYE:
        import merdiven
        ad = ad.replace("kalite-olcumu-", "kalite-olcumu-L%s%s%s-" % (SEVIYE, merdiven._set_eki(KAYNAK),
                                                                     ("-" + CESIT) if CESIT else ""))
    elif SAHNE_DOSYASI:
        ad = "kalite-olcumu-" + sahne_adi(SAHNE_DOSYASI)
    if ETIKET:
        ad += "-" + ETIKET
    return os.path.join(BURASI, ad + ".json")


def plan_klasoru():
    if PLAN_KLASORU:
        return PLAN_KLASORU
    return os.path.join(BURASI, "planlar", os.path.splitext(os.path.basename(dosya_adi()))[0])


def yaz(d):
    with io.open(dosya_adi(), "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=1))


def sahne_adi(yol):
    """--sahne dosyasinin kisa adi: `_sahne-INSAN-2026-06-22.json` -> INSAN-2026-06-22."""
    ad = os.path.splitext(yol.replace("\\", "/").rsplit("/", 1)[-1])[0]     # Windows yolu Linux'ta da ayrisir
    return ad[len("_sahne-"):] if ad.startswith("_sahne-") else ad


def sahne_yukle():
    from uret_veri_seti import sahne_uret
    if SAHNE_DOSYASI:
        if SEVIYE or CESIT:
            raise SystemExit("--sahne ile --seviye/--cesit birlikte verilmez")
        if not os.path.exists(SAHNE_DOSYASI):
            raise SystemExit("%s yok -- insan plani sahnesi icin: py insan-plani.py --hafta <pazartesi>" % SAHNE_DOSYASI)
        g = json.load(io.open(SAHNE_DOSYASI, encoding="utf-8"))
        g.setdefault("_merdiven", {})
        p = g["_merdiven"].get("referans_puani") or {}
        print("SAHNE : %s (dosyadan; seviye %s; referans puani %s)"
              % (os.path.basename(SAHNE_DOSYASI), g["_merdiven"].get("seviye", "?"),
                 p.get("amac") if p.get("amac") is not None else ("yok" if not p else p.get("durum"))))
        return g
    if SEVIYE:
        if SEVIYE != "1" or DOLULUK != 0.95:
            raise SystemExit("yalniz --seviye 1 (doluluk 0.95) var")
        import merdiven
        yol = merdiven.sahne_yolu(OLCEK, KAYNAK)
        if not os.path.exists(yol):
            if KAYNAK.startswith("ekili"):               # 16 Ekim: tanikli sahne ekili.py ile uretilir
                raise SystemExit("%s yok -- once: py ekili.py --olcek %g --taban %s"
                                 % (yol, OLCEK, "veri-seti" if KAYNAK.endswith("veri-seti") else "uretec"))
            raise SystemExit("%s yok -- once: py merdiven.py referans --olcek %g --kaynak %s" % (yol, OLCEK, KAYNAK))
        g = json.load(io.open(yol, encoding="utf-8"))
        if CESIT:
            g = merdiven.cesit_sahne(g, CESIT, OLCEK)
            ref = json.load(io.open(merdiven.referans_yolu(OLCEK, KAYNAK), encoding="utf-8"))
            t0 = time.time()
            p = merdiven.plan_puani(g, ref["atamalar"])
            if not p or p.get("durum") != "OPTIMAL":
                raise SystemExit("cesitte referans puani hesaplanamadi: %s" % p)
            g["_merdiven"]["referans_puani"] = p
            print("CESIT : %s -- %s (referans puani %d sn'de yeniden hesaplandi)"
                  % (CESIT, merdiven.CESITLER[CESIT], time.time() - t0))
        print("SAHNE : %s (merdiven seviye %s%s; %s puani %s)"
              % (os.path.basename(yol), g.get("_merdiven", {}).get("seviye", 1),
                 (", cesit " + CESIT) if CESIT else "",
                 "TANIK" if KAYNAK.startswith("ekili") else "referans",
                 g["_merdiven"]["referans_puani"]["amac"]))
        return g
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

def fm_disi_amac(s):
    """Amac degerinin FAZLA MESAI disindaki kismi (plan yoksa None).

    Bulgu 20: tam olcekte DENGELI kosularinda amacin %74-82'si fazla mesai
    cezasiydi ve kosudan kosuya oynayan tek kalem oydu (fazla mesai disi
    kisim 26.931-26.992, %0,2). Iki plani "fazla mesai haric" kiyaslamak
    icin bu sayi ayri yazilir."""
    if s.get("amac_degeri") is None:
        return None
    fm = (s.get("amac_dagilimi") or {}).get("FAZLA_MESAI") or {}
    return s["amac_degeri"] - fm.get("ceza", 0)


# ----------------------------------------------------------------------
# OPTIMUM HESABI -- Mustafa 14 Ekim 22:09: "kosu sonuclarina optimum
# hesaplamasinin detaylarini ekle; puan puan, % bilgileriyle; ne ne kadar
# etkiledi". Iki tablo: (1) KALEM KALEM -- her yumusak kuralin ham degeri,
# birimi, agirligi (puan/birim), cezasi, amactaki payi; referans varsa
# referansin ayni kalemi, fark (puan ve %), ve bu farkin toplam farktaki payi;
# ilk asama sonundaki cezasi (mola adimi neyi degistirdi). (2) ASAMA ASAMA --
# ilk plan -> ilk asama iyilestirmesi -> fazla mesai onarimi -> devam -> mola
# adimi: her adimda amac, fark (puan, %), sure. Sayilar hep motorun kendi
# kaydindan (amac_dagilimi, ilk_asama_iyilestirme, fazla_mesai_onarimi,
# iyilesme); yeniden hesap yok. Kayitli bir dosya icin `--optimum-raporu`.
# ----------------------------------------------------------------------

BIRIM = {"FAZLA_MESAI": "dakika", "HEDEF_KAPSAMA": "kisi-saat eksik", "HEDEF_ASIMI": "kisi-saat asim",
         "HEDEF_ASIMI_TOLERANS_USTU": "kisi-saat (tolerans ustu)", "MOLA_KAPSAMASI": "hucre x en kotu ceyrek eksik kisi",
         "ADALET_DENGESI": "ucgensel sapma birimi", "VARDIYA_ROTASYON_YONU": "geri kaydirilan saat",
         "TERCIH_KARSILAMA": "dakika (sozlesme alti)", "EKIP_SUREKLILIGI": "birincil disi atama",
         "PLAN_KARARLILIGI": "degisen kisi-gun", "SAAT_DENGESI": "saat"}


def _yuzde(pay, butun):
    if pay is None or not butun:
        return None
    return round(100.0 * pay / butun, 1) + 0.0          # -0.0 -> 0.0


def optimum_hesabi(s, ref=None):
    """Amacin nasil olustugu -- kalem kalem ve asama asama (bkz. ustteki not).
    `ref`: merdiven referans puani {"amac", "dagilim"} ya da None. Plan yoksa
    None. Yalniz kayittaki sayilari duzenler; hesaplamaz."""
    if s.get("amac_degeri") is None:
        return None
    toplam = s["amac_degeri"]
    dag = s.get("amac_dagilimi") or {}
    ref_amac = ref.get("amac") if ref else None
    ref_dag = (ref or {}).get("dagilim") or {}
    ilk_dag = ((s.get("ilk_asama_iyilestirme") or {}).get("amac_dagilimi")) or {}
    toplam_fark = (toplam - ref_amac) if ref_amac is not None else None
    kalemler = []
    for kural in sorted(set(dag) | set(ref_dag), key=lambda k: -(dag.get(k, {}).get("ceza", 0))):
        d = dag.get(kural) or {}
        ceza = d.get("ceza", 0)
        ham = d.get("deger")
        r = ref_dag.get(kural, {}).get("ceza") if ref else None
        fark = (ceza - r) if r is not None else None
        kalemler.append({
            "kural": kural, "birim": BIRIM.get(kural, "birim"), "ham": ham,
            "agirlik": (round(float(ceza) / ham, 2) if ham else None),      # puan / birim
            "ceza": ceza, "pay_yuzde": _yuzde(ceza, toplam),
            "ilk_asama_ceza": ilk_dag.get(kural, {}).get("ceza") if ilk_dag else None,
            "referans_ceza": r, "fark": fark, "fark_yuzde": _yuzde(fark, r),
            "toplam_farka_pay_yuzde": _yuzde(fark, toplam_fark) if toplam_fark else None})
    asamalar = []

    def ekle(ad, amac, saniye=None, aciklama=None):
        onceki = next((x["amac"] for x in reversed(asamalar) if x["amac"] is not None), None)
        fark = (amac - onceki) if (amac is not None and onceki is not None) else None
        asamalar.append({"asama": ad, "amac": amac, "saniye": saniye, "fark": fark,
                         "fark_yuzde": _yuzde(fark, onceki), "aciklama": aciklama})

    fm0 = s.get("fazla_mesai_once_sifir") or {}
    gs = s.get("gevsekten_serte") or {}
    b = s.get("ilk_asama_iyilestirme") or {}
    if b:
        if gs.get("denendi") and gs.get("adimlar"):
            son_adim = gs["adimlar"][-1]
            kaynak, sn = "gevsek yol, acik adim", gs.get("saniye")
            acik = "adim %s sn%s" % (son_adim.get("saniye"),
                                     ("; ilk plan %s. sn" % son_adim["ilk_cozum_saniye"])
                                     if son_adim.get("ilk_cozum_saniye") is not None else "")
        elif fm0.get("bulundu"):
            kaynak, sn, acik = "fazla mesaisiz arama", fm0.get("saniye"), "fazla mesai 0 ile bulundu"
        else:
            kaynak, sn, acik = "ilk arama", None, None
        ekle("ilk plan (%s)" % kaynak, b.get("amacsiz_amac"), sn,
             (acik + "; " if acik else "") + "amacsiz plan, amac degeri bu plandan")
        ekle("ilk asama iyilestirmesi", b.get("iyilesmis_amac"), b.get("saniye"),
             "%s cozum%s" % (b.get("cozum_sayisi"), "; OPTIMUM" if b.get("optimum") else ""))
    o = s.get("fazla_mesai_onarimi")
    if o and o.get("denendi"):
        if o.get("bulundu") and o.get("kabul"):
            ekle("fazla mesai onarimi (KABUL)", o.get("sonra_amac"), o.get("saniye"),
                 "fazla mesaisiz plan amaci kucultt\u00fc")
        elif o.get("bulundu"):
            ekle("fazla mesai onarimi (RED)", o.get("once_amac"), o.get("saniye"),
                 "fazla mesaisiz plan bulundu (%s) ama amac buyuyordu, eski plan kaldi" % o.get("sonra_amac"))
        else:
            ekle("fazla mesai onarimi (BULUNAMADI)", o.get("once_amac"), o.get("saniye"),
                 "%s dk fazla mesai kaldi" % o.get("once_dakika"))
    dv = b.get("devam") if b else None
    if dv and dv.get("saniye"):
        ekle("iyilestirmeye devam (%s)" % ("alindi" if dv.get("alindi") else "iyilesme yok"),
             dv.get("sonra_amac") if dv.get("alindi") else dv.get("once_amac"), dv.get("saniye"), None)
    iy = s.get("iyilesme") or {}
    if s.get("mola_adimi"):
        ekle("mola adimi (atamalar sabit)", toplam, s.get("ana_asama_butce_sn"),
             "%s cozum; adimin kaniti %s (planin tamami icin degil, O-16)"
             % (iy.get("cozum"), s.get("mola_adimi_alt_sinir")))
    elif iy or not asamalar:
        ekle("ana asama", toplam, s.get("ana_asama_butce_sn"), "%s cozum" % iy.get("cozum"))
    fm = dag.get("FAZLA_MESAI", {}).get("ceza", 0)
    ref_fm = ref_dag.get("FAZLA_MESAI", {}).get("ceza", 0) if ref else None
    ozet = {"amac": toplam, "referans": ref_amac, "fark": toplam_fark,
            "fark_yuzde": _yuzde(toplam_fark, ref_amac),
            "fm_disi_amac": toplam - fm,
            "fm_disi_referans": (ref_amac - ref_fm) if ref_amac is not None else None,
            "fm_disi_fark_yuzde": _yuzde((toplam - fm) - (ref_amac - ref_fm), ref_amac - ref_fm)
            if ref_amac is not None else None}
    return {"kalemler": kalemler, "asamalar": asamalar, "ozet": ozet}


def optimum_yazisi(h, girinti="         "):
    """optimum_hesabi() ciktisini satir satir yazar (konsol)."""
    if not h:
        return
    oz = h["ozet"]
    print(girinti + "OPTIMUM HESABI -- amac %s%s" % (
        oz["amac"],
        ("  |  referans %s  ->  fark %+d puan (%+.1f%%)  |  fazla mesai haric %s / %s (%+.1f%%)"
         % (oz["referans"], oz["fark"], oz["fark_yuzde"], oz["fm_disi_amac"], oz["fm_disi_referans"],
            oz["fm_disi_fark_yuzde"])) if oz.get("referans") is not None else
        ("  |  fazla mesai haric %s" % oz["fm_disi_amac"])))
    ref_var = oz.get("referans") is not None
    bas = girinti + "  %-24s %10s %-30s %8s %10s %6s %10s" % ("kalem", "ham", "birim", "agirlik", "ceza", "pay%", "ilk asama")
    if ref_var:
        bas += " %10s %9s %8s %8s" % ("referans", "fark", "fark%", "farkta%")
    print(bas)
    for k in h["kalemler"]:
        satir = girinti + "  %-24s %10s %-30s %8s %10s %6s %10s" % (
            k["kural"], _tire(k["ham"]), k["birim"][:30], _tire(k["agirlik"]), k["ceza"],
            _tire(k["pay_yuzde"]), _tire(k["ilk_asama_ceza"]))
        if ref_var:
            satir += " %10s %9s %8s %8s" % (_tire(k["referans_ceza"]),
                                            ("%+d" % k["fark"]) if k["fark"] is not None else "-",
                                            ("%+.1f" % k["fark_yuzde"]) if k["fark_yuzde"] is not None else "-",
                                            _tire(k["toplam_farka_pay_yuzde"]))
        print(satir)
    print(girinti + "  (ceza = ham x agirlik; pay% = amactaki payi; ilk asama = mola adimindan onceki ceza; "
          "fark = motor - referans; farkta% = bu kalemin toplam farktaki payi)")
    print(girinti + "  %-44s %10s %10s %8s %8s  %s" % ("asama", "amac", "fark", "fark%", "sn", "aciklama"))
    for a in h["asamalar"]:
        print(girinti + "  %-44s %10s %10s %8s %8s  %s" % (
            a["asama"][:44], _tire(a["amac"]),
            ("%+d" % a["fark"]) if a["fark"] is not None else "-",
            ("%+.1f" % a["fark_yuzde"]) if a["fark_yuzde"] is not None else "-",
            _tire(a["saniye"]), a.get("aciklama") or ""))


def optimum_raporu(yol):
    """Kayitli bir olcum dosyasinin her kosusu icin OPTIMUM HESABI (konsol).
    Referans dosyada varsa (`referans`, seviye 1 kosulari) kiyas da yazilir."""
    r = json.load(io.open(yol, encoding="utf-8"))
    ref = r.get("referans")
    print("DOSYA : %s  |  %s kisi, %s hucre, arama %s sn, %s cekirdek, %s"
          % (os.path.basename(yol), r.get("kisi"), r.get("hucre"), r.get("saniye"), r.get("cekirdek"), r.get("tarih")))
    for s in r.get("kosular", []):
        print("\n%s (tekrar %s): %s" % (s.get("yapilandirma"), s.get("tekrar", 1), s.get("durum")))
        h = optimum_hesabi(s, ref)
        if h is None:
            print("         plan yok -- optimum hesabi yok")
            continue
        optimum_yazisi(h)


def sinir_yazisi(s):
    """Kosu satirindaki "alt sinir / uzaklik" parcasi -- O-16 (6 Ekim).

    Ana asama mola adimi olarak kostuysa (`atamalar_sabit`) cozucunun siniri
    KISITLI problemindir; "alt sinir" / "uzaklik %0" diye yazmak planin
    optimum oldugunu soylemek olurdu (4-6 Ekim ciktilari oyle yazdi)."""
    if s.get("atamalar_sabit"):
        return ("kuresel alt sinir YOK (mola adimi siniri %s: yalniz bu atamalarla en iyi mola yerlesimi)"
                % s.get("mola_adimi_alt_sinir"))
    if s.get("fazla_mesaisiz_alt_sinir") is not None:
        # "once fazla mesaisiz" plan buldu, ana asama ortak arama (olcum):
        # cozulen modelde fazla mesai degiskenleri 0'da -- tam model degil.
        return ("kuresel alt sinir YOK (fazla mesaisiz modelin siniri %s: yalniz fazla mesaisiz planlarin en iyisi)"
                % s.get("fazla_mesaisiz_alt_sinir"))
    return "alt sinir %s  |  uzaklik %%%s" % (s.get("alt_sinir"), s.get("optimuma_uzaklik_yuzde"))


def fm_once_yazisi(s, ayar):
    """ "Once fazla mesaisiz" satiri; kosuda secenek KAPALIYSA None.

    `ayar` kosuda GECERLI olan ayardir (motorun varsayilani + yapilandirma;
    bkz. `etkin_ayar`): K-61'den beri secenek yazilmasa da aciktir.

    ⚠ Secenek acik oldugu halde motor denemediyse kosu fazla mesaisiz aramayi
      YAPMAMISTIR -- bu SESSIZ gecmez, satira yazilir: deneme hic yapilmadi
      (iki asama devreye girmedi: kucuk olcek, baslangic plani; ya da
      daraltilacak fazla mesai degiskeni yok: CALISAN profili, yari zamanli
      kadro) -> cikti None.
    O-18 (7 Ekim): bulununca iki hal var -- urun yolu (ipucu, alanlar geri
      acildi, karari agirliklar verdi) ve sert kesim (`sifirda_tutuldu`,
      olcum). Eski kayitlarda (6 Ekim) alan yok: o kosular sert kesimdi."""
    if not ayar.get("fazla_mesai_once_sifir"):
        return None
    f = s.get("fazla_mesai_once_sifir")
    if not f:
        return ("once fazla mesaisiz: UYGULANMADI (iki asama yok ya da daraltilacak fazla mesai "
                "degiskeni yok) -- bu kosuda fazla mesaisiz arama yapilmadi")
    if f.get("uygulandi") is False:
        # 7 Ekim 00:45 surumunun kaydi (agirlik kosulu; Mustafa hic kosmadi,
        # kayit yok) -- yine de okunabilsin (inceleme A, 04:45).
        return ("once fazla mesaisiz: UYGULANMADI (00:45 surumunun agirlik kosulu: %s) "
                "-- bu kosuda fazla mesaisiz arama yapilmadi" % f.get("sebep"))
    if f.get("bulundu"):
        if f.get("sifirda_tutuldu", True):
            sonuc = "BULUNDU -- SERT KESIM: fazla mesai butun asamalarda 0'da tutuldu (olcum)"
        else:
            sonuc = "BULUNDU -- ipucu oldu, alanlar geri acildi; karari agirliklar verdi"
    elif f.get("atlandi"):
        sonuc = "ATLANDI (gevsek yol; `gevsek_fazla_mesaisiz_saniye` 0) -- alanlar geri acildi"
    elif f["kanitlandi_yok"]:
        sonuc = ("YOK (%skanitlandi) -- alanlar geri acildi"
                 % ("molalar sabitken " if f.get("molalar_sabit", True) else ""))
    else:
        sonuc = "bu surede BULUNAMADI -- alanlar geri acildi"
    # Bulgu 25: denemeler (yeniden baslatma). Eski kayitlarda alan yok.
    denemeler = f.get("denemeler")
    deneme = ""
    if denemeler:
        deneme = "  |  deneme %d/%s: %s" % (
            len(denemeler), f.get("deneme_siniri", "?"),
            ", ".join("tohum %s %s %ss" % (d.get("tohum"), d.get("durum"), d.get("saniye"))
                      for d in denemeler))
    # K-68 ayar 4 (14 Ekim): gevsek yol mumkunken tek kisa deneme
    kisa = ("  |  gevsek yol: tek deneme, en cok %s sn" % f["gevsek_kisa_saniye"]
            if f.get("gevsek_kisa_saniye") is not None else "")
    return ("once fazla mesaisiz: %s  |  %s sn  |  %d fazla mesai degiskeni%s%s"
            % (sonuc, f["saniye"], f["degisken"], deneme, kisa))


def ipucu_plani_yazisi(s):
    """K-63 satiri: ana asama plansiz donup ikinci asamanin plani alindiysa.
    None = gerek olmadi (eski kayitlarda alan yok)."""
    ip = s.get("ipucu_plani")
    if not ip:
        return None
    if ip.get("bulundu"):
        return ("K-63: ana asama plansiz dondu, IKINCI ASAMANIN PLANI alindi (%s sn; molalar "
                "sablonun ideal yerinde; sebep %s)" % (ip.get("saniye"), s.get("durma_sebebi")))
    return "K-63: ana asama plansiz dondu, ipucu plani ALINAMADI (%s)" % ip.get("durum")


def onarim_yazisi(o):
    """K-68 ayar 3: fazla mesai onarimi. 14 Ekim'den once gevsek plandan hemen
    sonra (alan `asama` yok), sonra iyilestirmenin sonunda (`asama`,
    `kabul`, `once_amac` / `sonra_amac`)."""
    yer = " (iyilestirme sonu)" if o.get("asama") == "iyilestirme_sonu" else ""
    if not o.get("once_dakika"):
        return "fazla mesai onarimi%s: gerek yok" % yer
    if not o.get("denendi"):
        return "fazla mesai onarimi%s: %d dk, denenmedi (sure yok)" % (yer, o["once_dakika"])
    if not o.get("bulundu"):
        sonuc = "BULUNAMADI"
    elif "kabul" not in o:
        sonuc = "0"                                  # eski kayit: bulunan plan hep alinirdi
    elif o["kabul"]:
        sonuc = "0, amac %s -> %s ALINDI" % (o.get("once_amac"), o.get("sonra_amac"))
    else:
        sonuc = "0 ama amac %s -> %s (daha kotu), ALINMADI" % (o.get("once_amac"), o.get("sonra_amac"))
    ek = ""
    if o.get("yontem"):                                  # 15 Ekim: komsuluk / tam
        ek = " | yontem %s" % o["yontem"]
        if o.get("turlar"):
            ek += ", %d fm'li kisi, turlar: %s" % (
                o.get("fazla_mesaili_kisi", 0),
                "; ".join("%d. %d kisi serbest %s %s sn" % (t["tur"], t["serbest_kisi"], t["durum"], t["saniye"])
                          for t in o["turlar"]))
    return "fazla mesai onarimi%s: %d dk -> %s (%s, %s sn)%s" % (
        yer, o["once_dakika"], sonuc, o.get("durum"), o.get("saniye"), ek)


def gevsek_yazisi(s):
    """K-68 eki: gevsekten serte denendiyse adimlari ve sonucu tek satir."""
    gs = s.get("gevsekten_serte")
    if not gs:
        return None
    adim = ", ".join("%s %s %s sn%s%s" % (a["tavan"], a["durum"], a["saniye"],
                                         "" if a.get("ilk_cozum_saniye") is None
                                         else " (ilk plan %s. sn, %s cozum)" % (a["ilk_cozum_saniye"], a.get("cozum_sayisi")),
                                         "" if a["toleransin_ustunde_asim"] is None
                                         else " (ustu %d)" % a["toleransin_ustunde_asim"])
                     for a in gs.get("adimlar") or [])
    if s.get("taslak"):
        son = "TASLAK: %d hucre, %s kisi-saat tolerans ustu (%s)" % (
            s["taslak_asim"]["hucre"], s["taslak_asim"]["toplam_fazla"],
            "yok KANITLI" if s["taslak_asim"]["kanitlandi_yok"] else "kanitlanmadi")
    elif gs.get("tam_sert"):
        son = "tam serte inildi"
    elif gs.get("kalan_asim") is None:
        son = "gevsek yolda da plan YOK"
    else:
        son = "iyilestirme tolerans ustunu sifirladi (taslak degil)"
    ek = []
    if gs.get("yeniden_arama_atlandi"):
        ek.append("yeniden arama atlandi")
    if gs.get("acik_parcalar"):
        ek.append("acik adim parcalari: " + ", ".join(
            "tohum %s %s %s sn" % (p["tohum"], p["durum"], p["saniye"]) for p in gs["acik_parcalar"]))
    if gs.get("acik_parametreler"):
        ek.append("acik adim parametreleri %s" % gs["acik_parametreler"])
    if gs.get("fazla_mesai_sifirda"):                     # 16 Ekim olcum secenegi (gevsek_fm0)
        fs = gs["fazla_mesai_sifirda"]
        ek.append("acik adim fazla mesai 0 ile: %s (%d fm degiskeni)"
                  % ("plan bulundu, 0'da tutuldu" if fs.get("bulundu") else "plan YOK, alanlar acildi", fs.get("degisken", 0)))
    o = s.get("fazla_mesai_onarimi")
    if o:
        ek.append(onarim_yazisi(o))
    return "GEVSEKTEN SERTE (%s sn; yedek %s sn): %s  ->  %s%s" % (
        gs.get("saniye"), gs.get("yedek_saniye"), adim or "adim yok", son,
        ("  |  " + "  |  ".join(ek)) if ek else "")


def etkin_ayar(ayar):
    """Kosuda GECERLI olan ayar: motorun varsayilani + yapilandirmanin
    yazdiklari. Bir yapilandirmanin YAZMADIGI secenek varsayilandan gelir;
    kayit bunu soylemezse "o kosuda acik miydi" sonradan bilinemez."""
    return dict(COZ_VARSAYILAN, **(ayar or {}))


def _tire(v):
    return "-" if v is None else v


def kosu(g, ad, ayar, girdi_ek=None, tekrar=1):
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
    etkin = etkin_ayar(tam_ayar)
    s = {"yapilandirma": ad, "ayar": {a: v for a, v in tam_ayar.items()},
         # K-61: secenek varsayilandan da gelebilir; kosuda ACIK MIYDI?
         # (AYAR. Uygulanip uygulanmadigi `fazla_mesai_once_sifir`te.)
         "once_fazla_mesaisiz": bool(etkin.get("fazla_mesai_once_sifir")),
         # O-18: sert kesim mi (olcum) -- urun yolunda False.
         "sert_kesim": bool(etkin.get("fazla_mesai_sifirda_tut")),
         "girdi_ek": girdi_ek or {},
         "kurma_sn": round(kurma, 1), "toplam_sn": round(sure, 1),
         "durum": c.get("durum")}
    for alan in ("durma_sebebi", "iki_asama", "cozum_sayisi", "amac_degeri", "alt_sinir",
                 "ilk_asama_sn", "ana_asama_butce_sn", "ilk_cozum_sn", "isci_sayisi",
                 "amac_dagilimi", "iyilesme", "ilk_asama_iyilestirme", "paralel",
                 "mola_adimi", "atamalar_sabit", "mola_adimi_alt_sinir",
                 "fazla_mesaisiz_alt_sinir", "fazla_mesai_once_sifir", "ipucu_plani",
                 "gevsekten_serte", "fazla_mesai_onarimi"):   # K-68 eki ve ayar 3 (13 Ekim)
        s[alan] = ist.get(alan)
    # K-68 eki (ii): tam serte inilemediyse plan TASLAK; asan hucreler.
    s["taslak"] = bool(c.get("taslak"))
    ta = c.get("taslak_asim") or {}
    s["taslak_asim"] = ({"hucre": len(ta.get("hucreler") or []), "toplam_fazla": ta.get("toplam_fazla"),
                         "kanitlandi_yok": ta.get("kanitlandi_yok")} if ta else None)
    s["uygulanmayan_notlar"] = list(c.get("uygulanmayan_notlar") or [])
    s["optimuma_uzaklik_yuzde"] = m.get("optimuma_uzaklik_yuzde")
    s["metrikler"] = m
    if c.get("durum") != "cozuldu":
        print("         DURUM: %s  (%s)" % (c.get("durum"), ist.get("durma_sebebi")))
        if fm_once_yazisi(s, etkin):
            print("         " + fm_once_yazisi(s, etkin))
        if ipucu_plani_yazisi(s):
            print("         " + ipucu_plani_yazisi(s))
        if gevsek_yazisi(s):
            print("         " + gevsek_yazisi(s))
        return s
    r = degerlendir(g, c["atamalar"])
    if not PLANSIZ:                                   # K-66: cizelge her kosuda
        kayit = {"arac": "kalite-olc.py", "yapilandirma": ad, "tekrar": tekrar, "saniye": tam_ayar["azami_saniye"],
                 "etiket": ETIKET, "olcek": OLCEK, "doluluk": DOLULUK, "ayar": {a: v for a, v in tam_ayar.items()},
                 "girdi_ek": girdi_ek or {}, "tarih": time.strftime("%Y-%m-%d %H:%M"), "cekirdek": os.cpu_count(),
                 "olcum_dosyasi": os.path.basename(dosya_adi())}
        try:
            jy, hy = cizelge.plan_kaydet(plan_klasoru(), "%s-%d" % (ad, tekrar), g, c, r, kayit)
            s["plan_dosyasi"] = os.path.relpath(jy, BURASI)
            print("         cizelge: %s (+ .html)" % s["plan_dosyasi"])
        except Exception as e:                        # cizelge yazilamadi diye olcum durmaz; sessiz de degil
            s["plan_dosyasi"] = None
            s["plan_hatasi"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("         CIZELGE YAZILAMADI: %s" % s["plan_hatasi"])
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
    print("         %.0f sn  |  %s  |  amac %s (fazla mesai disi %s)  |  %s  |  cozum %s"
          % (sure, s["durma_sebebi"], s["amac_degeri"], fm_disi_amac(s), sinir_yazisi(s),
             s["cozum_sayisi"]))
    if fm_once_yazisi(s, etkin):
        print("         " + fm_once_yazisi(s, etkin))
    if ipucu_plani_yazisi(s):
        print("         " + ipucu_plani_yazisi(s))
    if gevsek_yazisi(s):
        print("         " + gevsek_yazisi(s))
    # Notlarin hepsi dosyaya yazilir; ekrana yalniz bu secenegin notu (tam
    # olcekte "departman kapali" notlari onlarca satir).
    for n in s["uygulanmayan_notlar"]:
        if "fazla mesaisiz" in n or "ikinci asamanin plani" in n or n.startswith("HEDEF_ASIMI"):
            print("         not: %s" % n)
    print("         ilk plan %s sn  |  kazancin %%50'si %s sn, %%90'i %s sn, %%99'u %s sn  |  son iyilesme %s sn"
          % (s["ilk_cozum_sn"], iy.get("yuzde50_sn"), iy.get("yuzde90_sn"),
             iy.get("yuzde99_sn"), iy.get("son_iyilesme_sn")))
    print("         sert ihlal %d  |  yayinlanabilir %s  |  hedef kapsama %%%s  |  eksik hedef %s kisi-saat  |  fazla mesai (motor metrigi) %s saat"
          % (s["sert_ihlal"], s["yayinlanabilir"], m.get("hedef_kapsama_yuzde"),
             (m.get("eksik_hedef_dakika") or 0) / 60.0, m.get("fazla_mesai_saat")))
    if m.get("rotasyon_geri_gecis") is not None:                      # K-65
        print("         rotasyon: %s geri gecis, %s saat (dogrulayici satiri %s)"
              % (m.get("rotasyon_geri_gecis"), m.get("rotasyon_geri_saat"),
                 s["ihlal"].get("VARDIYA_ROTASYON_YONU", 0)))
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
        sm = (b.get("amac_dagilimi") or {}).get("MOLA_KAPSAMASI")
        sa = (s.get("amac_dagilimi") or {}).get("MOLA_KAPSAMASI")
        if sm and sa:
            print("         mola sirasinda kapsama (ham): sabit molali plan %d  ->  ana asama sonu %d%s"
                  % (sm["deger"], sa["deger"],
                     "   (ana asamada ATAMALAR SABIT: yalniz molalar arandi)" if s.get("atamalar_sabit") else ""))
            # Ham sayi = her talep hucresinde (ekip-gun-saat) EN KOTU ceyrekte
            # asgarinin altinda kalan kisi, hucreler toplami. Okunur hali:
            # hucre basina kac kisi eksik, asgarinin yuzde kaci.
            hucreler = [t for t in (g.get("talep") or []) if t.get("asgari")]
            if hucreler:
                n = float(len(hucreler))
                asg = sum(t["asgari"] for t in hucreler) / n
                print("           = hucre basina en kotu ceyrekte ort. %.1f -> %.1f kisi eksik (asgari ort. %.1f kisi; %%%.1f -> %%%.1f)"
                      % (sm["deger"] / n, sa["deger"] / n, asg,
                         100.0 * sm["deger"] / n / asg, 100.0 * sa["deger"] / n / asg))
    p = s.get("paralel")
    if p:
        for ad in ("ipuclu", "ipucusuz"):
            print("         (b) %-8s %d isci  |  %s  |  amac %s  |  ilk plan %s sn  |  cozum %s%s"
                  % (ad, p[ad]["isci"], "plan var" if p[ad]["plan_bulundu"] else "PLAN YOK",
                     p[ad]["amac_degeri"], p[ad]["ilk_cozum_sn"], p[ad]["cozum_sayisi"],
                     "   <-- SECILEN" if p["secilen"] == ad else ""))
    for kural, d in (s["amac_dagilimi"] or {}).items():
        print("           %-16s ceza %10d  (%%%5.1f)   ham %8s   degisken %6d"
              % (kural, d["ceza"], d["pay_yuzde"], "-" if d["deger"] is None else d["deger"], d["degisken"]))
    # OPTIMUM HESABI (Mustafa 14 Ekim 22:09). Yazim hatasi olcumu durdurmasin:
    # kosu bitti, plan ve sayilar kayitta; bu yalniz sunum.
    try:
        s["optimum_hesabi"] = optimum_hesabi(s, (g.get("_merdiven") or {}).get("referans_puani"))
        optimum_yazisi(s["optimum_hesabi"])
    except Exception as e:                           # noqa: BLE001
        s["optimum_hesabi_hatasi"] = str(e)[:300]
        print("         optimum hesabi yazilamadi: %s" % s["optimum_hesabi_hatasi"])
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
    # Ad sutunu en uzun yapilandirma adina gore genisler (en az 14): uzun
    # adlar tabloyu kaydirmasin.
    G = max([14] + [len(k["yapilandirma"]) for k in kosular])
    ad = lambda k: k["yapilandirma"].ljust(G)
    print("\n%-14s %6s %10s %10s %8s %7s %7s %7s %7s %7s %5s"
          % ("yapilandirma".ljust(G), "sn", "amac", "alt sinir", "uzaklik", "ilk sn",
             "%50 sn", "%90 sn", "%99 sn", "cozum", "sert"))
    taban = kosular[0].get("amac_degeri")
    for s in kosular:
        if s.get("amac_degeri") is None:
            print("%-14s %6s  plan yok: %s (%s)" % (ad(s), s.get("toplam_sn"),
                                                   s.get("durum"), s.get("durma_sebebi")))
            continue
        iy = s.get("iyilesme") or {}
        fark = ("%+.1f%%" % (100.0 * (s["amac_degeri"] - taban) / taban)
                if taban and s.get("amac_degeri") is not None else "")
        # O-16: mola adimi kosusunda kuresel sinir yoktur -- "-" yazilir.
        uzaklik = s.get("optimuma_uzaklik_yuzde")
        print("%-14s %6s %10s %10s %8s %7s %7s %7s %7s %7s %5s  %s"
              % (ad(s), s.get("toplam_sn"), s.get("amac_degeri"),
                 _tire(s.get("alt_sinir")), "-" if uzaklik is None else "%s%%" % uzaklik,
                 s.get("ilk_cozum_sn"), iy.get("yuzde50_sn"), iy.get("yuzde90_sn"),
                 iy.get("yuzde99_sn"), s.get("cozum_sayisi"), s.get("sert_ihlal"), fark))
    # Kapasite tabani ile kiyas: planin hedef acigi tabanin kac kati?
    kt = sonuc.get("kapasite_tabani") or {}
    for s in kosular:
        d = (s.get("amac_dagilimi") or {}).get("HEDEF_KAPSAMA")
        if d and kt.get("hedef"):
            taban_ks = kt["hedef"]["taban"]
            print("  %-14s hedef acigi %d kisi-saat, kapasite tabani %s kisi-saat%s"
                  % (ad(s), d["deger"], taban_ks,
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
                  % (ad(s), model_saat, fm.get("saat", 0.0), m["fazla_mesai_saat"],
                     ("%.2f" % dogrulayici_saat) if dogrulayici_saat is not None else None,
                     uyari))
            sou = (s.get("dogrulayici_metrikler") or {}).get("sozlesme_ustu_ucret_saat")
            if sou is not None:
                print("  %-14s sozlesme ustu ucretli saat (ayri alan, fazla mesai DEGIL): %.1f saat" % (ad(s), sou))
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
            print("  %-14s bagimsiz alt sinir %d  ->  uzaklik en cok %%%.1f  (CP-SAT siniri %s -> %s)"
                  % (ad(s), bagimsiz,
                     100.0 * (s["amac_degeri"] - max(bagimsiz, s.get("alt_sinir") or 0)) / s["amac_degeri"],
                     _tire(s.get("alt_sinir")),
                     "kuresel sinir yok" if s.get("alt_sinir") is None
                     else "%%%s" % s.get("optimuma_uzaklik_yuzde")))
    sonuc["bagimsiz_alt_sinir"] = bagimsiz
    # HAM BUYUKLUKLER: amac degeri agirliga bagli, bu tablo degil. Agirlik
    # deneyinde (fm_agirlik_*) karsilastirma YALNIZ burada yapilir.
    print("\n%-14s %10s %10s %9s %9s %9s %8s %8s %10s %10s" % (
        "yapilandirma".ljust(G), "fm saat", "hedef eks.", "hedef %", "asim k-s", "adalet", "mola", "sert",
        "amac", "fm disi"))
    for s in kosular:
        d = s.get("amac_dagilimi") or {}
        m = s.get("metrikler") or {}
        if not d:
            continue
        ham = lambda kural: (d.get(kural) or {}).get("deger", 0)
        print("%-14s %10.1f %10d %9s %9d %9d %8d %8s %10s %10s" % (
            ad(s), ham("FAZLA_MESAI") / 60.0, ham("HEDEF_KAPSAMA"),
            m.get("hedef_kapsama_yuzde"), ham("HEDEF_ASIMI"), ham("ADALET_DENGESI"),
            ham("MOLA_KAPSAMASI"), s.get("sert_ihlal"), s.get("amac_degeri"), fm_disi_amac(s)))


def tamamlanmis(kosular, ad, tekrar):
    """`--devam` icin: bu (yapilandirma, tekrar) kayitta bitmis mi? Plansiz
    biten (sure_yetmedi) de bitmistir -- olcumun sonucu o. ISTISNA ve yarim
    kayit (durum yok) bitmemistir."""
    for s in kosular:
        if s.get("yapilandirma") == ad and s.get("tekrar") == tekrar and s.get("durum") not in (None, "ISTISNA"):
            return True
    return False


def main():
    if OPTIMUM_RAPORU:                                # kayitli dosya: yalniz rapor, kosu yok
        optimum_raporu(OPTIMUM_RAPORU)
        return
    g = sahne_yukle()
    sonuc = {"olcek": OLCEK, "doluluk": DOLULUK, "saniye": SANIYE, "tekrar": TEKRAR,
             "kisi": len(g["calisanlar"]), "hucre": len(g["talep"]),
             "kural": len(g["kurallar"]), "yapilandirmalar": SECILEN,
             # Hangi makinede, ne zaman: baska makinede olculen sure/amac
             # bu makine icin TAHMIN degildir (28 Eylul dersi).
             "tarih": time.strftime("%Y-%m-%d %H:%M"), "cekirdek": os.cpu_count(),
             "kosular": []}
    if DEVAM and os.path.exists(dosya_adi()):
        onceki = json.load(io.open(dosya_adi(), encoding="utf-8"))
        sonuc["kosular"] = [k for k in onceki.get("kosular", []) if k.get("durum") not in (None, "ISTISNA")]
        sonuc["tarih"] = onceki.get("tarih", sonuc["tarih"])
        sonuc["devam"] = (onceki.get("devam") or []) + [time.strftime("%Y-%m-%d %H:%M")]
        print("DEVAM : %s -- kayitta %d bitmis kosu, eksikler kosulur (devam %s)"
              % (os.path.basename(dosya_adi()), len(sonuc["kosular"]), ", ".join(sonuc["devam"])))
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
            if DEVAM and tamamlanmis(sonuc["kosular"], ad, tekrar + 1):
                print("\n%d/%d  %s  (tekrar %d/%d)  -- kayitta var, ATLANDI" % (n, len(SECILEN), ad, tekrar + 1, TEKRAR))
                continue
            print("\n%d/%d  %s%s" % (n, len(SECILEN), ad,
                                     ("  (tekrar %d/%d)" % (tekrar + 1, TEKRAR)) if TEKRAR > 1 else ""))
            try:
                s = kosu(g, ad, dict(YAPILANDIRMALAR[ad][1]), YAPILANDIRMALAR[ad][2], tekrar=tekrar + 1)
            except Exception as e:                       # olcum devam etsin, hata yazilsin
                s = {"yapilandirma": ad, "durum": "ISTISNA", "hata": str(e)[:400]}
                print("         ISTISNA: %s" % s["hata"])
            s["tekrar"] = tekrar + 1
            sonuc["kosular"].append(s)
            yaz(sonuc)

    ozet(sonuc)
    if SEVIYE or SAHNE_DOSYASI:
        referans_kiyasi(g, sonuc)
    yaz(sonuc)
    print("\nSonuc yazildi: %s" % os.path.basename(dosya_adi()))


def referans_kiyasi(g, sonuc):
    """K-62 ilke 3: her kosu referansla KALEM KALEM (ayni sahne, ayni olcu)."""
    ref = (g.get("_merdiven") or {}).get("referans_puani")
    sonuc["referans"] = ref
    if not ref or ref.get("amac") is None:
        # 16 Ekim (A3): insan plani sert ihlalleriyle modele oturmaz -> puani yok; kiyas
        # dogrulayici raporuyla (referans kayit) kalem kalem yapilir, burada atlanir.
        print("\nREFERANS KIYASI ATLANDI: referans puani yok (%s)" % ((ref or {}).get("durum") or "sahnede referans_puani yok"))
        return
    kalemler = sorted(set(ref["dagilim"]) | {k for s in sonuc["kosular"]
                                              for k in (s.get("amac_dagilimi") or {})})
    print("\nREFERANS KIYASI (seviye 1; referans 'en az bu kadar iyisi var' -- K-62)")
    print("  %-22s %10s" % ("kalem", "referans") + "".join(
        " %12s" % ("%s-%s" % (s["yapilandirma"][:8], s.get("tekrar", 1))) for s in sonuc["kosular"]))
    for k in ["AMAC"] + kalemler:
        r = ref["amac"] if k == "AMAC" else ref["dagilim"].get(k, {}).get("ceza", 0)
        satir = "  %-22s %10s" % (k, r)
        for s in sonuc["kosular"]:
            v = s.get("amac_degeri") if k == "AMAC" else (s.get("amac_dagilimi") or {}).get(k, {}).get("ceza", 0)
            satir += " %12s" % v
        print(satir)
    for s in sonuc["kosular"]:
        if s.get("amac_degeri") is not None:
            s["referansa_gore_yuzde"] = round(100.0 * (s["amac_degeri"] - ref["amac"]) / ref["amac"], 2)
            print("  %s-%s: motor %s, referans %s -> %+.2f%% (eksi = motor daha iyi)%s"
                  % (s["yapilandirma"], s.get("tekrar", 1), s["amac_degeri"], ref["amac"],
                     s["referansa_gore_yuzde"],
                     ("  [TASLAK: amacta tolerans ustu x %d]"
                      % importlib.import_module("cozucu.coz").GEVSEK_KALAN_AGIRLIGI)
                     if s.get("taslak") else ""))


if __name__ == "__main__":
    main()
