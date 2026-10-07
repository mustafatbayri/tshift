# -*- coding: utf-8 -*-
"""
COZUCU GIRISI -- /solve (Master Spec v1.4 #11.2, #11.3)

DURMA KURALI -- K-28 (Mustafa, 16 Eylul): "erken dur, bekletme"
  Iki kosuldan biri olunca biter:
    * optimuma %2'den yakin      (nispi bosluk)
    * 2 dakikadir iyilesmiyor     (durgunluk)
  Ustte mutlak butce durur (varsayilan 15 dk).

  Gerekce: 3. dakikada bulunan planla 15. dakikadaki arasindaki fark sahada
  1-2 saatlik kapsama; plani bekleyen yonetici icin 12 dakika daha degerli.

AKIS -- K-60 (Mustafa, 4 Ekim): UC ASAMA
  1. gecerli plan   : molalar sablonun ideal yerinde SABIT, amac yok      (pay <= %20)
                      K-61 (6 Ekim): ONCE FAZLA MESAISIZ aranir (fazla mesai
                      degiskenleri [0,0]). Bulunursa o plan IPUCUDUR ve alanlar
                      GERI ACILIR -- hakem agirliklardir, fazla mesaili daha
                      iyi plan disarida kalmaz (7 Ekim duzeltmesi, O-18).
                      Bulunamazsa alanlar yine acilir, fazla mesai serbestken
                      bir kez daha aranir (en kotu halde iki pay: 2 x %20).
                      Bulgu 25 (7 Ekim): fazla mesaisiz aramanin payi
                      `fazla_mesaisiz_deneme` denemeye bolunebilir (farkli
                      tohum; varsayilan 1 = tek deneme) -- olcum secenegi.
  2. iyilestirme    : molalar hala sabit, amac geri konur, atamalar iyilesir (%80, kalibrasyon);
                      ipucu 1'in plani -- fazla mesaisiz bulunduysa fazla
                      mesai yalniz agirliklara gore KAZANIYORSA eklenir
  3. MOLA ADIMI     : atamalar 2'nin planina SABIT, yalniz molalarin yeri
                      aranir, o KISITLI problemin kanitli optimumunda durur
                      (hedef_bosluk 0); kalan sure kullaniciya geri doner
                      (tam olcekte ~45 sn)
                      K-63 (7 Ekim): mola adimi surede plan uretemezse 2'nin
                      plani doner (molalar sablonun ideal yerinde), notla ve
                      `durma_sebebi: mola_adimi_yetismedi` ile -- elde plan
                      varken "sure yetmedi" denmez (bulgu 24).
  ⚠ O-16 (6 Ekim): mola adiminin optimumu PLANIN optimumu DEGILDIR. Atamalar
    sabitken cozucunun alt siniri yalniz "bu atamalarla en iyi mola
    yerlesimi"ni kanitlar. Bu yuzden mola adimi kostugunda `alt_sinir` ve
    `optimuma_uzaklik_yuzde` None'dir (K-35'in "kanitlanmis yakinlik"i icin
    kuresel sinir YOK), adimin kendi siniri `mola_adimi_alt_sinir`e,
    durma sebebi `mola_adimi_optimum`a yazilir. 4-6 Ekim arasinda cikti
    "optimum, uzaklik %0" diyordu; olculdu (bulgu 20): ayni girdide 4-5,6
    kat daha iyi plan vardi. Ayni kural her kisitli model icin gecerlidir
    (bkz. `_sinir_kapsami`).
  Olculdu (T-60 bulgu 17-18): ortak arama (atamalar + molalar birlikte)
  molalari daha yavas ve daha kotu yerlestiriyordu, atamalara dokunan payi
  %6 idi. `mola_adimi: False` eski ortak aramayi OLCUM icin geri getirir.

BU DOSYA DOGRULAYICIDAN BAGIMSIZDIR (#7.6, #16.1).
"""

import time

from ortools.sat.python import cp_model

from .model import (Model, _mola_baslangiclari, _mola_dilimleri, _net_saat,
                    isci_sayisi)

VARSAYILAN = {
    "azami_saniye": 900,          # 15 dk mutlak butce
    "hedef_bosluk": 0.02,         # optimuma %2
    "durgunluk_saniye": 120,      # 2 dk iyilesme yoksa bitir
    "iki_asama_esigi": 50000,     # bu kadar degiskenden sonra ONCE gecerli plan
    "ilk_asama_saniye": 120,      # gecerli plan aramasina ayrilan sure --
                                  # BUTCENIN ICINDEN (T-59), en cok:
    "ilk_asama_orani": 0.2,       # azami_saniye'nin bu kadari
    # None = MAKINENIN cekirdek sayisi. Burada sabit 8 yaziyordu ve iki
    # cekirdekli makinelerde plani kotulestiriyordu (bkz. model.isci_sayisi).
    "isci_sayisi": None,
    # T-60 (2 Ekim): CP-SAT'in kendi parametreleri, OLCUM icin kapi.
    # {"linearization_level": 2} gibi; ad -> deger, cozucuye aynen gecer.
    # Urun kodu bunu BOS birakir; kalite-olc.py yapilandirmalari doldurur.
    # Sure ve isci sayisi buradan verilmez (yukaridaki alanlar esastir).
    "cozucu_parametreleri": {},
    # T-60 (2 Ekim, bulgu 8): birinci asamanin AMACSIZ plani ana aramayi kotu
    #   bir plana "demirliyor" (tam olcekte ipucusuz kosu fazla mesaiyi yariya
    #   indirdi) ama ipucusuz arama guvenilir degil (yedi kosunun ikisi plan
    #   buldu). Cozum (a): birinci asama gecerli plani bulduktan sonra molalar
    #   HALA SABITKEN amaci geri koyup iyilestirir; ana asamanin ipucu
    #   iyilesmis plan olur. Sure BUTCENIN ICINDEN gider (T-59).
    #
    # ⚠ K-59 (3 Ekim, Mustafa: "olsun") -- (a) URUNUN VARSAYILANI. Olculdu
    #   (500 kisi, 600 sn, ikiser kosu): yasal fazla mesai 475-511 saat ->
    #   120 sn'de 60-83, 240 sn'de 45-53, 480 sn'de 34-38; hedef eksigi
    #   1.199-1.248 -> 575-610 / 512-533 / 360-366 kisi-saat; hepsi 0 sert.
    #
    #   `ilk_asama_iyilestirme_saniye`: None = sure ORANDAN gelir (varsayilan);
    #   sayi = en cok bu kadar saniye; 0 = KAPALI (eski davranis, olcum icin).
    "ilk_asama_iyilestirme_saniye": None,
    #   Iyilestirme butcenin en cok bu kadarini alir. K-59'da %40 idi (ana
    #   asama molalari da ariyordu, suresi gerekiyordu). K-60 (4 Ekim) ile ana
    #   asama yalniz mola adimi oldu ve ~45 sn'de bitiyor; kalan sure buraya:
    #   %80 -- olculen `mola_adimi_tam` hali (bulgu 18: 480 sn iyilestirme +
    #   mola adimi, uc kosu, 0 sert). %80 bir KALIBRASYON, karar degil. %90
    #   da olculdu (bulgu 19, 5 Ekim; 600 sn, ucer kosu: %80 -> 113.947-
    #   163.346, %90 -> 111.289-161.378, araliklar ic ice): fark yok, %80
    #   kaldi. Ust sinir var ki mola adimina sure kalsin:
    #   tam olcekte adim ~45 sn (ilk plan 23 sn + arama 21 sn); 600 sn'de
    #   kalan ~107 sn. 0.1 olcekte 45 sn butceyle 60 sn istenince ana asamaya
    #   1 sn kaldi ve plan DONMEDI (olculdu, 2 Ekim) -- tavan bunun icin.
    "ilk_asama_iyilestirme_orani": 0.8,
    #     True: iyilestirme aramasi amacsiz plani ipucu ALMADAN baslar (kucuk
    #     modelde demirsiz arama). Plan bulamazsa amacsiz planin ipucu KALIR --
    #     guvenlik agi kaybolmaz.
    "ilk_asama_iyilestirme_ipucusuz": False,
    # (b) Ana asamada iki arama YAN YANA: biri ipuclu (guvenlik agi), biri
    #     ipucusuz; sure ayni, isciler bolusulur; iyi olan plan secilir.
    #     Deger = ipucusuz aramaya verilen isci sayisi. 0 = kapali.
    #     ⚠ Olculdu ve ELENDI (bulgu 13): ipucusuz kol plan bulamadi, isci
    #     bolmek ipuclu kolu kotulestirdi. Olcum secenegi olarak duruyor.
    "paralel_ipucusuz_isci": 0,
    # K-60 (4 Ekim, Mustafa: "evet"): MOLA ADIMI. Ana asama atamalari
    #   birinci asamanin planina SABITLER ve yalniz molalarin yerini arar.
    #   Sabit molali planda ayni sablondaki herkes ayni dakikada molada
    #   (hucre basina en kotu ceyrekte 5,8 kisi asgarinin altinda, %19);
    #   mola adimi bunu 0,4 kisiye indiriyor ve 44-46 sn'de KANITLI optimuma
    #   ulasiyor (bulgu 18). Ortak arama (False, eski davranis) ayni isi
    #   347 sn'de daha kotu yapiyordu (0,5) ve atamalara dokunan payi %6 idi.
    #   Ipucu yoksa (iki asama devreye girmediyse) uygulanamaz; atamalar ve
    #   molalar birlikte aranir (kucuk modelin olagan yolu, not dusulmez).
    "mola_adimi": True,
    #   Mola adiminin durma esigi. 0 = yalniz KANITLI optimumda durur (CP-SAT
    #   atamalar sabitken bunu saniyeler icinde kanitliyor). Genel
    #   `hedef_bosluk` (%2) burada kullanilmaz: toplam amacin %70-77'si sabit
    #   fazla mesai oldugundan %2'lik bosluk mola terimi daha inebilirken
    #   erken durduruyordu (bulgu 17: 445-535'te durdu; 0 ile 177-188).
    "mola_adimi_hedef_bosluk": 0.0,
    # K-61 (6 Ekim, Mustafa: "Evet") -- "ONCE FAZLA MESAISIZ" URUNUN
    #   VARSAYILANI. Birinci asama gecerli plani fazla mesai degiskenleri
    #   [0,0]'a SABITKEN arar. Bulursa o plan iyilestirmenin IPUCUDUR; alanlar
    #   geri acilir ve karari agirliklar verir (asagida "HAKEM AGIRLIKLARDIR").
    #   NEDEN (olculdu; 500 kisi, 900 sn, ucer kosu, Mustafa'nin makinesi):
    #     bulgu 20 -- CALISAN profili (fazla mesai tavani 0 -> SERT) uc kosuda
    #       da 0 saat fazla mesaiyle plan buldu; o planlar DENGELI'nin KENDI
    #       agirliklariyla 26.589-26.703, DENGELI'nin kendi buldugu
    #       105.742-148.431 (fazla mesai disi kismi 26.931-26.992). Fazla
    #       mesai verinin zorladigi bir sey degil, aramanin ARTIGI: yumusak
    #       cezayla (dakika basi 50) sifira itilemiyor, sert sinirla 13-33
    #       sn'de sifirlaniyor.
    #     bulgu 21 -- SERT KESIMLE (bulununca 0'da tutularak) alti kosunun
    #       altisinda fazla mesai 0; amac DENGELI 26.407-26.494, KAPSAMA
    #       13.834-13.914 (toplam iyilesti; adalet ve hedef asimi cok az
    #       kotulesti); kosudan kosuya fark DENGELI %40 -> %0,3, KAPSAMA
    #       %26 -> %0,6.
    #   Dayanak K-30 (Mustafa, 16 Eylul; "Zaten hedef hic gitmemek.
    #   Gidilecekse de minimum gitmek."), kararin tablosu:
    #     yalniz HEDEF kapsama iyilesecek        -> fazla mesai YAPILMAZ
    #     ASGARI (sert) fazla mesaisiz tutmuyor  -> YAPILIR, gereken kadar
    #   Bulamazsa (kanit ya da sure) alanlar GERI ACILIR, onceki yol aynen
    #   isler (ikinci satir; zorunlu fazla mesai yolu KAPANMAZ, K-38) ve not
    #   duser. ⚠ O yolun "gereken kadar"i KANITLI DEGIL: agirlikli arama
    #   azaltmaya calisir (kesif, 151 kisi, tek kosu: en az 3,5 saat
    #   zorunluyken 9,75-11,25 saat yazildi -- T-60 bulgu 22; merdivenin 4.
    #   seviyesi olcecek).
    #   ⚠ HAKEM AGIRLIKLARDIR (Mustafa, 6 Ekim 23:44): "...agirliklar baz
    #     alindiginda ornegin 3 saat fazla mesai iceren en optimum plan var
    #     ve fazla mesaisiz plandan oldukca daha optimum bir plan ise en
    #     optimum olani secmeliyiz." Bu yuzden bulunan fazla mesaisiz plan
    #     yalniz BASLANGIC NOKTASIDIR: alanlar geri acilir, iyilestirme tam
    #     agirlikli amacla o plandan baslar. Fazla mesai ancak agirliklara
    #     gore kazaniyorsa plana girer; K-30'un ilk satirini agirliklar
    #     saglar (bir saat fazla mesai 3.000 puan, hedefin bir kisi-saat
    #     altinda kalmak 9/20/5).
    #   ⚠ O-18 (7 Ekim): 6 Ekim gecesi yazilan hal bulununca fazla mesaiyi
    #     BUTUN asamalarda 0'da tutuyordu ("sert kesim") ve "urun
    #     agirliklarinda fazla mesaili plan daha iyi olamaz" deniyordu. YANLIS:
    #     15 dakikalik bir fazla mesai adimi bir haftalik duzenin kilidini
    #     acabiliyor (kanitli optimum 750 iken sert kesim 2.256; 12 kiside
    #     9.000'e karsi 12.000 -- Mustafa'nin 3 saatlik ornegi; bagimsiz
    #     inceleme, test_fazla_mesai_once_sifir.py bolum 5). Sert kesim
    #     OLCUM secenegi olarak kaldi (`fazla_mesai_sifirda_tut`).
    #   KAPSAM: yalniz iki asamali yol (`_ipucu_ver`). Esigin altindaki
    #   model ve baslangic plani verilen kosu (K-54, "Iyilestir") bu
    #   aramadan etkilenmez -- orada birinci asama yok. (Kucuk model tek
    #   aramada agirliklarla ayni karari verir; "Iyilestir" fazla mesaili
    #   bir plandan basliyorsa onu azaltmak aramaya kalir -- olculmedi.)
    #   ⚠ "Bu surede bulunamadi" halinde donen plan fazla mesaili olabilir
    #   ve fazla mesaisizi VAR olabilir; not bunu soyler, sessiz kalmaz.
    #   ⚠ Duzeltilmis yol (alanlar acik) tam olcekte HENUZ OLCULMEDI; bulgu
    #   21 sert kesimin olcumudur. Olcum: kalite-olc.py `fm_once` /
    #   `fm_sert` / `fm_once_kapali` yapilandirmalari.
    #   False = 6 Ekim oncesinin davranisi (olcum ve kiyas icin).
    "fazla_mesai_once_sifir": True,
    # OLCUM (T-60 bulgu 25, 7 Ekim): fazla mesaisiz aramanin YENIDEN
    #   BASLATILMASI. Birinci asamanin payi (en cok 120 sn) bu kadar denemeye
    #   bolunur (3 -> 3 x 40 sn), her deneme farkli CP-SAT tohumuyla
    #   (1 = kutuphanenin varsayilani = bugunku arama, sonra 2, 3...), ilk
    #   bulunan plan alinir; kanitli "yok" (INFEASIBLE) gelirse kalan denemeler
    #   yapilmaz. NEDEN: 7 Ekim gece kosusunda (500 kisi, 1200 sn) bu arama 18
    #   kosunun 1'inde 120 sn'de plan bulamadi ve motor fazla mesai serbest yola
    #   dustu -- plan 30 saat fazla mesaiyle dondu (116.976; otekiler 26,6-26,8
    #   bin). Kuyruk olcumu (kuyruk.py, 35 deneme, 6 isci): medyan 7,5 sn, %90
    #   13 sn, en uzun 62 sn, P(T > 40 sn) = 2/35 -- 3 x 40 sn ile hepsinin
    #   basarisiz olma tahmini ~%0,02 (denemeler bagimsiz sayilarak; offline).
    #   1 = BUGUNKU DAVRANIS (tek deneme, payin tamami). 3 motorda 900 sn x 3
    #   ile olculmeden varsayilan YAPILMAZ (karar kurali bulgu 25'te).
    "fazla_mesaisiz_deneme": 1,
    # OLCUM: True = 6 Ekim gecesinin SERT KESIMI -- fazla mesaisiz plan
    #   bulununca fazla mesai degiskenleri sonraki asamalarda da [0,0]'da
    #   kalir; cozulen model tam model degildir (kuresel sinir yazilmaz,
    #   `_sinir_kapsami` "fazla_mesaisiz"). Urun yolunda KAPALI (O-18).
    #   Yalniz `fazla_mesai_once_sifir` acikken anlamlidir.
    "fazla_mesai_sifirda_tut": False,
    # K-63 (7 Ekim, Mustafa: "2. asamanin plani notla donsun onerine ...
    #   katiliyorum"): ana asama (mola adimi) surede plan uretemezse ama elde
    #   ikinci asamanin TAM ipucusu varsa o plan doner (molalar sablonun ideal
    #   yerinde), notla ve `durma_sebebi: mola_adimi_yetismedi` ile. Ipucu plana
    #   cevrilir: KARAR degiskenleri (x, mola, dinlenme) ipucu degerine
    #   sabitlenir, ceza degiskenlerini amac en kucuge indirir -- amac_degeri
    #   planin SIKI amacidir (bkz. `_ipucu_planini_al`; bagimsiz inceleme 3).
    #   Bu adimin tavani -- butcenin DISINDA kalan tek kalem; olculdu: 0.2
    #   olcekte 0,6-0,8 sn (bulut, 1 isci), tam olcekte OLCULMEDI
    #   (disdegerleme ~4 sn); tavan guvenlik icin. Ipucu gecersiz cikarsa
    #   (olmamali: ayni modelin alani daraltilmis halinin cozumu) eski cevap
    #   ("sure yetmedi") aynen doner. NEDEN: bulgu 24 (7 Ekim) -- 20 sn'lik
    #   butcede mola adimina 1-2 sn kaliyor, ikinci asamanin gecerli plani
    #   eldeyken kullaniciya "sure yetmedi" donuyordu (0.2 olcekte dogal
    #   kosuda kendiliginden olustu: mola adimina 1,68 sn kaldi).
    "ipucu_plani_saniye": 30,
}


class _ErkenDur(cp_model.CpSolverSolutionCallback):
    """K-28'in govdesi. Her yeni cozumde bakar, yeter dedigi an durur."""

    def __init__(self, ayar):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.ayar = ayar
        self.baslangic = time.time()
        self.son_iyilesme = self.baslangic
        self.cozum_sayisi = 0
        self.durma_sebebi = None
        # Ilk cozumun amac degeri. Baslangic plani verildiyse ILK cozum
        # odur; boylece "nereden nereye" ciktida gosterilebilir.
        self.ilk_amac = None
        # T-60 (1 Ekim): ana asamada ILK PLANIN bulunma ani. Tam olcekte
        # birinci asama 120 saniyede plan bulamiyor ama ana asama buluyor;
        # "kacinci saniyede" bilinmeden bu cozulemez. `ana_basladi` cozum
        # baslamadan hemen once yazilir; yazilmadiysa kurulus ani esastir.
        self.ilk_cozum_sn = None
        self.ana_basladi = None
        # T-60 (2 Ekim): IYILESME EGRISI -- her cozumde (saniye, amac, alt sinir).
        # "Butce dolunca durdu" tek basina bir sey soylemiyor: plan son 10
        # saniyede mi, ilk 30 saniyede mi iyilesti? Egri olmadan kalite
        # olcumu yapilamaz.
        self.egri = []

    def on_solution_callback(self):
        self.cozum_sayisi += 1
        self.son_iyilesme = time.time()
        if self.ilk_amac is None:
            self.ilk_amac = self.ObjectiveValue()
            self.ilk_cozum_sn = time.time() - (self.ana_basladi or self.baslangic)
        sinir = self.BestObjectiveBound()
        deger = self.ObjectiveValue()
        self.egri.append((round(time.time() - (self.ana_basladi or self.baslangic), 2),
                          deger, sinir))
        if deger == sinir:
            # Kanitli optimum: alt sinir degere ulasti (0 == 0 dahil). K-60'in
            # mola adimi hedef_bosluk 0 ile kosar; "hedef_bosluk" yazmak
            # yaniltici olurdu -- bulgu 18'de uc kosunun ikisi oyle yazildi.
            self.durma_sebebi = "optimum"
            self.StopSearch()
        elif deger > 0 and abs(deger - sinir) / abs(deger) <= self.ayar["hedef_bosluk"]:
            self.durma_sebebi = "hedef_bosluk"
            self.StopSearch()


def _plandan_ipucu(kuruldu, plan):
    """Var olan bir plani cozucuye baslangic noktasi olarak verir.

    NEDEN (Mustafa, 28 Eylul)
      Motor ayni girdiye her seferinde ayni plani vermiyor: sekiz arama
      iscisi paralel calisiyor ve hangisinin once iyi bir plan buldugu her
      kosuda degisiyor (olculdu: 25 saniyede 21.905 ve 22.715). Tek isciyle
      tekrarlanabilir olur ama ayni surede uretilen plan 46 KAT kotu.

      Mustafa'nin sorusu: "Yonetici tekrar calistirdiginda daha iyi bir plan
      gelip gelmeyecegini nasil bilecek? Bunu bilmezse nasil guvenecek?"

      Cevap "yeniden uret" degil IYILESTIR. Plan ipucu olarak verilince
      CP-SAT onu bir baslangic cozumu sayar; amaci KUCULTTUGU icin
      donduregi sonuc ipucundan KOTU OLAMAZ. Yonetici zar atmiyor,
      biriktiriyor.

    DONEN DEGER
      Ipucu yazildiysa True. Plan bu modele oturmuyorsa (girdi degismis,
      sablon kalkmis, kisi ayrilmis) False -- ve cagiran taraf bunu
      CIKTIDA BILDIRIR. Sessizce sifirdan baslamak, kullaniciya
      "iyilestirdim" deyip aslinda zar atmak olurdu.
    """
    if not plan:
        return False

    degerler = {}
    for a in plan:
        anahtar = (a.get("calisan"), a.get("gun"), a.get("sablon"))
        if anahtar not in kuruldu.x:
            return False                      # plan bu modele oturmuyor
        degerler[kuruldu.x[anahtar]] = 1

        tid = a.get("sablon")
        sablon = kuruldu.sablon.get(tid)
        if sablon is None:
            return False
        yemek_dk = kuruldu.yemek_dk.get(tid, 0)
        _, dinlenme_dk = kuruldu.dinlenme_tanim.get(tid, (0, 0))

        for m in (a.get("molalar") or []):
            bas = m.get("bas")
            if m.get("tip") == "dinlenme":
                for i, adaylar in enumerate(kuruldu._dinlenme_adaylari(sablon)):
                    k = (a["calisan"], a["gun"], tid, i, bas)
                    if k in kuruldu.dinlenme:
                        degerler[kuruldu.dinlenme[k]] = 1
                        break
            else:
                k = (a["calisan"], a["gun"], tid, bas)
                if k in kuruldu.mola:
                    degerler[kuruldu.mola[k]] = 1

    # Plana girmeyen her sey SIFIR. Eksik birakmak ipucunu yarim birakir
    # ve CP-SAT onu bir baslangic cozumu olarak kullanamaz.
    kuruldu.m.ClearHints()
    for sozluk in (kuruldu.x, kuruldu.mola, kuruldu.dinlenme):
        for v in sozluk.values():
            kuruldu.m.AddHint(v, degerler.get(v, 0))
    return True


def _ilk_asama_payi(ayar):
    """Birinci asamanin payi -- BUTCENIN ICINDEN (T-59, 30 Eylul aksami).

    ⚠ NE VARDI: birinci asama `ilk_asama_saniye` (120 sn) kadar sure aliyor,
      ana cozum ayrica `azami_saniye`nin TAMAMINI aliyordu. 900 saniye
      istenen tam olcekli kosu 1078 saniye surdu (29 Eylul, olculdu).
      K-35 kullaniciya sure sectiriyor; vaat edilen sure asiliyordu.

    Pay: min(ilk_asama_saniye, azami_saniye x ilk_asama_orani). %20 bir
    KALIBRASYON: 900 sn'de eski 120 sn aynen kalir; 240 sn'lik bekci
    butcesinde 48 sn olur (0.1 olcekte gecerli plan saniyeler icinde
    bulunuyor).
    """
    return float(min(float(ayar.get("ilk_asama_saniye", 120)),
                     float(ayar["azami_saniye"])
                     * float(ayar.get("ilk_asama_orani", 0.2))))


def _ipucu_ver(kuruldu, ayar):
    """Once GECERLI bir plan bul, sonra onu cozucuye baslangic olarak ver.

    ⚠ NEDEN GEREKTI (28 Eylul, 350 kisilik gercekci sahnede olculdu)
      Buyuk modelde cozucu HIC plan uretemiyordu:

          amac VAR : 45 saniyede hic cozum yok (UNKNOWN)
          amac YOK : 32 saniyede OPTIMAL

      Yani GECERLI plan bulmak kolay, IYILESTIRMEK zor. Cozucu butun
      butceyi iyilestirmeye harciyor ve eli bos donuyordu. Kullaniciya bu
      "cozumsuz" olarak gorunuyordu -- yani "imkansiz" ile "yetistiremedim"
      ayni cevaba cikiyordu.

    NASIL
      Amac GECICI olarak kaldirilir, uygun bir plan aranir, bulunan degerler
      ipucu (hint) olarak yazilir ve amac GERI KONUR. Iyilestirme artik
      elde bir planla baslar; butce dolsa bile cikti bos kalmaz.

    ⚠ AMAC HER YOLDA GERI KONUR. Konmazsa motor sessizce "herhangi bir
      plan" uretmeye baslar ve butun yumusak kurallar etkisiz kalir --
      plan gecerli ama kalitesiz olur ve bunu kimse fark etmez.

    Ipucu bulunamazsa sessizce vazgecilir: ipucu bir HIZLANDIRMADIR,
    dogrulugun parcasi degil.

    ⚠ MOLALAR SABITLENEREK ARANIR (T-60, 1 Ekim)
      Tam olcekte (500 kisi) bu asama uc kosuda da 120 saniyede plan
      bulamadi; T-78 duzeltmesinden sonra ana asama da 778 saniyede
      bulamadi. Degiskenlerin ucte ikisi mola yerlesimi (her vardiyada
      ~9 yemek + 3x7-9 dinlenme adayi) ve gecerli bir plan icin bunlarin
      SECILMESI gerekmiyor -- herhangi bir yerlesim olur. Birinci asamada
      her sablonun molalari ideale en yakin tek noktaya SABITLENIR
      (Model.sabit_mola_secimi): secilmeyen adaylarin alani [0,0] yapilir,
      sum == x kisiti seciliyi kendiliginden x'e esitler. Yeni kisit
      YAZILMAZ, model buyumez; asama bitince alanlar [0,1]'e geri alinir.
      Ana asama molalari yine SERBEST arar -- K-32'nin "ayni sablondaki
      herkes ayni dakikada molaya cikmasin" karari degismedi; ipucu
      yalnizca baslangic noktasi.

    ⚠ ONCE FAZLA MESAISIZ (K-61) ve YENIDEN BASLATMA (bulgu 25, 7 Ekim)
      Secenek acikken bu arama fm_* alanlari [0,0]'a sabitken yapilir ve
      `_fazla_mesaisiz_ara` ile payi `fazla_mesaisiz_deneme` denemeye
      bolunebilir (varsayilan 1). Bulunursa plan yalniz IPUCUDUR (alanlar
      geri acilir); bulunamazsa alanlar acilir, `_gecerli_plan_yeniden_ara`.
    """
    if not kuruldu.cezalar:
        return False                      # amac yok; iki asamanin anlami yok

    def amaci_geri_koy():
        kuruldu.m.Minimize(sum(a * v for a, v in kuruldu.cezalar))

    basladi = time.time()
    kuruldu.ilk_asama_iyilestirme = None
    kuruldu.m.ClearObjective()
    mola_sabit = bool(ayar.get("ilk_asama_sabit_mola", True))
    sabitlenen = _molalari_sabitle(kuruldu) if mola_sabit else []
    kuruldu.fazla_mesai_once_sifir = None
    fm_eski = (_fazla_mesaiyi_sifirla(kuruldu)
               if ayar.get("fazla_mesai_once_sifir") else [])
    try:
        pay = _ilk_asama_payi(ayar)
        denemeler = None
        if fm_eski:
            # Fazla mesaisiz arama: payi `fazla_mesaisiz_deneme` denemeye boler
            # (bulgu 25; varsayilan 1 = tek deneme, payin tamami).
            durum, c, denemeler = _fazla_mesaisiz_ara(kuruldu, ayar, pay)
        else:
            c = cp_model.CpSolver()
            c.parameters.max_time_in_seconds = pay
            c.parameters.num_search_workers = isci_sayisi(ayar)
            durum = c.Solve(kuruldu.m)
        dusulecek = 0.0
        if fm_eski:
            bulundu = durum in (cp_model.OPTIMAL, cp_model.FEASIBLE)
            deneme_sn = time.time() - basladi     # butun denemelerin toplami
            # OLCUM ("sert kesim"): plan bulunduysa fazla mesai 0'da KALSIN mi?
            # Urunun yolunda HAYIR -- bkz. VARSAYILAN["fazla_mesai_sifirda_tut"].
            sifirda = bulundu and bool(ayar.get("fazla_mesai_sifirda_tut"))
            kuruldu.fazla_mesai_once_sifir = {
                "bulundu": bulundu, "degisken": len(fm_eski),
                # Toplam: butun denemelerin suresi (bulunan dahil).
                "saniye": round(deneme_sn, 2),
                # Bulgu 25: her denemenin tohumu, suresi, durumu; `deneme_siniri`
                # istenen en cok deneme (politika). Tek denemede de yazilir ki
                # kuyruk urun kosularinda gorunur kalsin.
                "deneme_siniri": _deneme_siniri(ayar),
                "denemeler": denemeler,
                # INFEASIBLE = fazla mesaisiz plan YOK (kanit); UNKNOWN = sure
                # yetmedi, var mi yok mu bilinmiyor.
                # ⚠ Kanit ARANAN MODELINDIR: molalar sablonun ideal yerinde
                #   sabitken (`molalar_sabit`). Mola yerine bagli sert kural
                #   (SAHADA_ASGARI tabani > 0) varsa molalar serbestken
                #   fazla mesaisiz plan yine de bulunabilir.
                "kanitlandi_yok": durum == cp_model.INFEASIBLE,
                "molalar_sabit": mola_sabit,
                # True = fazla mesai degiskenleri sonraki asamalarda da
                # [0,0]'da (yalniz olcum secenegiyle); o zaman cozulen model
                # tam model DEGILDIR (bkz. `_sinir_kapsami`).
                "sifirda_tutuldu": sifirda}
            if not sifirda:
                # ⚠ HAKEM AGIRLIKLARDIR (K-61). Plan bulunduysa o yalniz
                #   BASLANGIC NOKTASIDIR: alanlar geri acilir, iyilestirme tam
                #   agirlikli amacla o plandan baslar ve fazla mesaili daha
                #   iyi plan disarida kalmaz. Bulunamadiysa yeniden arama
                #   icin zaten acilmasi gerekir (K-38: zorunlu fazla mesai
                #   yolu kapanmaz). Ipucu (fazla mesai = 0) acik alanda da
                #   gecerli bir cozumdur.
                _fazla_mesaiyi_serbest_birak(kuruldu, fm_eski)
            if not bulundu:
                kuruldu.notlar.append(
                    "fazla mesaisiz plan %s; fazla mesai serbest birakildi "
                    "(agirlikli arama azaltmaya calisir; en azi oldugu kanitli degildir)"
                    % ("yok (%skanitlandi)" % ("molalar sabitken " if mola_sabit else "")
                       if durum == cp_model.INFEASIBLE
                       else "bu surede bulunamadi" + (
                           # bulgu 25: kac denemede (yeniden baslatma acikken)
                           " (%d denemede)" % len(denemeler) if len(denemeler) > 1 else "")))
                # ⚠ BASARISIZ DENEMENIN SURESI IYILESTIRMENIN PAYINDAN DUSER.
                #   Dusulmezse en kotu halde (deneme payini doldurdu, yeniden
                #   arama da) birinci asama butcenin tamamini yer, mola
                #   adimina 1 sn kalir ve elde plan varken "sure yetmedi"
                #   doner (900 sn'de: 120 + 120 + 659). Dusulunce mola adimina
                #   kalan sure deneme yapilmamis gibi kalir (120 + 720).
                dusulecek = deneme_sn
                durum, c = _gecerli_plan_yeniden_ara(kuruldu, ayar, basladi)
        if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return False
        # ⚠ IPUCU TAM YAZILIR (T-60, 1 Ekim). Eskiden yalniz x/mola/dinlenme
        #   ipucu aliyordu; ceza degiskenleri (eksik, fazla, adalet...) bos
        #   kaliyordu. Yarim ipucuyu CP-SAT "onarmaya" calisir ve 10
        #   celiskiden sonra vazgecer (hint_conflict_limit): 0.2 olcekte
        #   ipucu ELDEYKEN ana asamanin ilk plani 57-101 saniyede geldi.
        #   Birinci asama ayni modelin amacsiz halini cozdugu icin BUTUN
        #   degiskenlerin degeri var; hepsi yazilir, ipucu tam ve gecerli
        #   olur, ana asama onu ilk cozum olarak hemen alir.
        _tam_ipucu_yaz(kuruldu, c)
        _ilk_asamada_iyilestir(kuruldu, ayar, c, amaci_geri_koy, basladi, dusulecek)
        return True
    finally:
        _molalari_serbest_birak(kuruldu, sabitlenen)
        amaci_geri_koy()


def _deneme_siniri(ayar):
    """`fazla_mesaisiz_deneme`: en cok kac deneme (en az 1; bos/0/eksi = 1)."""
    try:
        return max(1, int(ayar.get("fazla_mesaisiz_deneme") or 1))
    except (TypeError, ValueError):
        return 1


def _fazla_mesaisiz_ara(kuruldu, ayar, pay):
    """Fazla mesaisiz (fm_* alanlari [0,0]) GECERLI plan aramasi -- T-60 bulgu
    25 (7 Ekim). Donen: (durum, cozucu, denemeler).

    Pay `fazla_mesaisiz_deneme` esit parcaya bolunur; her deneme AYNI modeli
    farkli CP-SAT tohumuyla (1, 2, 3...; 1 kutuphanenin varsayilani, yani
    bugunku arama) arar. Ilk bulunan plan doner. INFEASIBLE kanittir ("fazla
    mesaisiz plan yok" -- molalar sabitken): kalan denemeler yapilmaz, tohum
    bunu degistirmez. UNKNOWN ("bu parcada bulunamadi") sonraki denemeye
    gecer. Varsayilan 1: tek deneme, payin tamami -- davranis 7 Ekim sabahiyla
    ayni.

    ⚠ NEDEN TOHUM: 500 kisilik modelde bu aramanin suresi agir kuyruklu
      (medyan 7,5 sn, 53 gozlemde 1 x > 120 sn; kuyruk.py). Ayni tohumla bile
      sure 7 kat oynuyor (paralel iscilerin zamanlamasi); farkli tohum
      aramanin baslangicini da degistirir -- yeniden baslatma, tek uzun
      aramaya gore kuyrugu keser (offline tahmin 3 x 40 sn: %0,02; motorda
      900 sn x 3 ile dogrulanacak, bulgu 25).
    ⚠ Toplam sure payi asmaz (parcalar esit; 1 sn tabani yalniz birden cok
      denemede ve pay deneme sayisindan kucukse devreye girer -- tek denemede
      pay aynen verilir, bugunku aramayla birebir). Bu arama birinci
      asamanin kendisidir: basarili denemenin suresi iyilestirmeden
      dusulmez; basarisiz denemelerin toplami duser (`_ipucu_ver`,
      `dusulecek`).
    Arac: kesif/2026-10-07-fm-siz-arama-kuyrugu/kuyruk.py `--politika N` ayni
    fonksiyonu motor disinda tekrar tekrar kosturur (politika olcumu).
    """
    adet = _deneme_siniri(ayar)
    parca = float(pay) if adet == 1 else max(1.0, float(pay) / adet)
    isci = isci_sayisi(ayar)
    denemeler = []
    durum, c = cp_model.UNKNOWN, None
    for i in range(adet):
        c = cp_model.CpSolver()
        c.parameters.max_time_in_seconds = parca
        c.parameters.num_search_workers = isci
        c.parameters.random_seed = i + 1          # 1 = CP-SAT varsayilani (bugunku arama)
        t0 = time.time()
        durum = c.Solve(kuruldu.m)
        denemeler.append({"tohum": i + 1, "saniye": round(time.time() - t0, 2),
                          "durum": c.StatusName(durum)})
        if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.INFEASIBLE):
            break                                 # plan var, ya da yoklugu kanitli
    return durum, c, denemeler


def _fazla_mesaiyi_sifirla(kuruldu):
    """Fazla mesai ceza degiskenlerinin (fm_*) alanini [0,0] yapar; donen
    liste (indeks, eski alan) -- geri acmak icin; bos liste = daraltilacak
    alan yok (secenek islemsiz). `fazla >= dakika - tavan` kisiti sayesinde
    bu, "kimse sozlesme saatini asamaz" demektir. Kisit EKLENMEZ, alan
    daraltilir (bkz. _molalari_sabitle)."""
    proto = kuruldu.m.Proto()
    eski = []
    for _, v in kuruldu.cezalar:
        if not v.Name().startswith("fm_"):
            continue
        dom = proto.variables[v.Index()].domain
        # Alani ZATEN [0,0] olan (CALISAN profili: tavan 0) sayilmaz: orada
        # deneme ile birinci asamanin aramasi AYNI modeldir; "serbest
        # birakildi" notu ve ikinci arama anlamsiz olurdu.
        if list(dom) == [0, 0]:
            continue
        eski.append((v.Index(), list(dom)))
        dom.clear()
        dom.extend([0, 0])
    return eski


def _fazla_mesaiyi_serbest_birak(kuruldu, eski):
    proto = kuruldu.m.Proto()
    for ix, alan in eski:
        dom = proto.variables[ix].domain
        dom.clear()
        dom.extend(alan)


def _gecerli_plan_yeniden_ara(kuruldu, ayar, basladi):
    """Fazla mesaisiz deneme plan bulamayinca, fazla mesai serbestken BIR
    KEZ daha gecerli plan arar. Sure yine butcenin icinden: birinci asamanin
    payi kadar, ama kalan butceyi asmadan (T-59)."""
    kalan = float(ayar["azami_saniye"]) - (time.time() - basladi) - 1.0
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = max(1.0, min(_ilk_asama_payi(ayar), kalan))
    c.parameters.num_search_workers = isci_sayisi(ayar)
    return c.Solve(kuruldu.m), c


def _iyilestirme_coz(model, saniye, isci):
    """Sabit molali modelde AMACLI kisa arama. Ayri fonksiyon: testler
    "plan bulunamadi" yolunu buradan zorlar."""
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = isci
    geri = _CozumSayaci()
    return c.Solve(model, geri), c, geri


class _CozumSayaci(cp_model.CpSolverSolutionCallback):
    """Iyilestirme aramasinin sayaci ve EGRISI: her cozumde (saniye, amac,
    alt sinir). Egri 7 Ekim'de eklendi: iyilestirme butcenin %80'ini aliyor
    ve yalniz ilk/son amaci yaziliyordu -- plan hangi saniyede duzeldi,
    nerede duzlesti bilinmeden sure paylari olculemez (ana asamada ayni is
    `_ErkenDur.egri`)."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.cozum_sayisi = 0
        self.basladi = time.time()
        self.egri = []

    def on_solution_callback(self):
        self.cozum_sayisi += 1
        self.egri.append((round(time.time() - self.basladi, 2),
                          self.ObjectiveValue(), self.BestObjectiveBound()))


def _ilk_asamada_iyilestir(kuruldu, ayar, amacsiz, amaci_geri_koy, basladi, dusulecek=0.0):
    """(a) secenegi -- T-60 bulgu 8 (2 Ekim). K-59 (3 Ekim): URUNUN
    VARSAYILANI; K-60 (4 Ekim) ile sure butcenin %80'i
    (`ilk_asama_iyilestirme_orani`, kalibrasyon); `ilk_asama_iyilestirme_saniye: 0`
    kapatir (olcum: eski davranis).

    Cagrildiginda: molalar SABIT, amac SILINMIS, amacsiz planin ipucu TAM
    yazilmis. Burada amac geri konur ve ayni (kucuk) modelde
    `ilk_asama_iyilestirme_saniye` kadar iyilestirilir; plan bulunursa ipucu
    onunla DEGISIR. Sabit molali planin her cozumu tam modelin de cozumudur
    (alan daraltildi, kisit eklenmedi), yani ipucu yine tam ve gecerlidir.

    ⚠ GUVENLIK AGI KAYBOLMAZ: iyilestirme plan bulamazsa (ipucusuz
      baslatildiysa olabilir) amacsiz planin ipucu GERI YAZILIR.
    ⚠ SURE BUTCENIN ICINDEN: birinci asamanin toplami `ilk_asama_sn`e
      yazilir, ana asamaya kalan verilir (T-59). Iyilestirme butcenin en cok
      `ilk_asama_iyilestirme_orani` (%80) kadarini alir: ana asama ipucunu
      plana cevirmeye yetecek sureyi bulamazsa elde plan varken "sure
      yetmedi" doner.
      `dusulecek`: iyilestirmenin suresinden dusulen saniye -- "once fazla
      mesaisiz" denemesi BASARISIZ olduysa onun suresi (bkz. `_ipucu_ver`).
      Hem paydan hem acikca istenen sureden duser: mola adimina kalan sure
      deneme yapilmamis gibi kalir. Deneme plan bulduysa 0'dir (o arama
      birinci asamanin kendisidir).
    Ne oldugu `kuruldu.ilk_asama_iyilestirme`e yazilir (ciktiya gider).
    """
    tavan = float(ayar["azami_saniye"]) * float(ayar.get("ilk_asama_iyilestirme_orani", 0.8))
    istenen = ayar.get("ilk_asama_iyilestirme_saniye")
    istenen = tavan if istenen is None else float(istenen)   # K-59: None = orandan
    if istenen <= 0:
        return                                   # 0 = kapali (olcum: eski davranis)
    kalan = float(ayar["azami_saniye"]) - (time.time() - basladi) - 1.0
    saniye = min(min(istenen, tavan) - dusulecek, kalan)
    amacsiz_amac = int(sum(a * amacsiz.Value(v) for a, v in kuruldu.cezalar))
    bilgi = {"istenen_saniye": istenen, "saniye": 0.0,
             "ipucusuz": bool(ayar.get("ilk_asama_iyilestirme_ipucusuz")),
             "amacsiz_amac": amacsiz_amac, "iyilesmis_amac": None,
             "plan_bulundu": False, "cozum_sayisi": 0, "optimum": False}
    kuruldu.ilk_asama_iyilestirme = bilgi
    if saniye <= 0:
        return
    proto = kuruldu.m.Proto()
    yedek = (list(proto.solution_hint.vars), list(proto.solution_hint.values))
    amaci_geri_koy()
    if bilgi["ipucusuz"]:
        kuruldu.m.ClearHints()
    t0 = time.time()
    durum, c2, sayac = _iyilestirme_coz(kuruldu.m, saniye, isci_sayisi(ayar))
    bilgi["saniye"] = round(time.time() - t0, 2)
    bilgi["cozum_sayisi"] = sayac.cozum_sayisi
    # ⚠ O-16: egrideki sinirlar SABIT MOLALI modelindir, planin tamami icin
    #   kanit degil.
    bilgi["iyilesme"] = _iyilesme_ozeti(sayac.egri, nokta=24)
    bilgi["ipucu_korundu"] = False
    if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        bilgi["plan_bulundu"] = True
        bilgi["optimum"] = (durum == cp_model.OPTIMAL)
        bilgi["iyilesmis_amac"] = int(round(c2.ObjectiveValue()))
        bilgi["amac_dagilimi"] = _amac_dagilimi(kuruldu, c2)   # sabit molali planin kiriligi
        if bilgi["iyilesmis_amac"] > amacsiz_amac:
            # ⚠ IPUCU KORUNUR (7 Ekim, bagimsiz inceleme). CP-SAT tam ve
            #   gecerli ipucuyu ilk cozum olarak almaya CALISIR; bu bir
            #   garanti degil (ipucunun ceza degiskenleri gevsekse ilk cozum
            #   daha iyi de olabilir, onarilamazsa baska bir plan da). Donen
            #   plan ipucudan (fazla mesaisiz baslangic, K-61) KOTUYSE ipucu
            #   ezilmez: amacsiz planin ipucusu kalir, ciktida isaretlenir.
            #   Olculen kosularda hic olmadi; kural buna ragmen yazildi.
            bilgi["ipucu_korundu"] = True
            proto.solution_hint.vars.clear()
            proto.solution_hint.values.clear()
            proto.solution_hint.vars.extend(yedek[0])
            proto.solution_hint.values.extend(yedek[1])
        else:
            _tam_ipucu_yaz(kuruldu, c2)
    else:
        proto.solution_hint.vars.clear()
        proto.solution_hint.values.clear()
        proto.solution_hint.vars.extend(yedek[0])
        proto.solution_hint.values.extend(yedek[1])


def _atamalari_sabitle(kuruldu):
    """Atama degiskenlerini (x) ipucudaki degerlerine SABITLER; donen sayi
    sabitlenen degisken sayisi (ipucu yoksa 0). Mola degiskenleri serbest
    kalir -- ana asama yalniz molalari arar. Model tek kullanimlik (bkz.
    `coz`), alanlar geri acilmaz."""
    proto = kuruldu.m.Proto()
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    if not ipucu:
        return 0
    sayi = 0
    for v in kuruldu.x.values():
        deger = ipucu.get(v.Index())
        if deger is None:
            continue
        dom = proto.variables[v.Index()].domain
        dom.clear()
        dom.extend([int(deger), int(deger)])
        sayi += 1
    return sayi


def _ipucu_planini_al(kuruldu, ayar):
    """K-63 (7 Ekim): modeldeki TAM ipucunun PLANINI cozume cevirir. Donen
    sozluk: {"bulundu", "saniye", "durum", "durum_kodu", "sabitlenen", "cozucu"}.

    NASIL: KARAR degiskenleri (x, mola, dinlenme) ipucu degerine SABITLENIR
    (alan daraltma, `_atamalari_sabitle` gibi; model `coz` icinde tek
    kullanimlik), ceza degiskenleri SERBEST kalir ve amac onlari en kucuge
    indirir. Boylece plan ipucunun planidir (atamalar ve molalar birebir) ve
    `amac_degeri` o planin SIKI amacidir. Tek isci: karar degiskenleri
    sabitken arama yok, yayilim var.

    ⚠ NEDEN BUTUN DEGISKENLER SABITLENMEZ (bagimsiz inceleme 3, 7 Ekim
      aksami): ipucunun ceza degerleri GEVSEK olabilir -- ikinci asamanin
      planinda az (0.2 olcekte +%1,2), birinci asamanin AMACSIZ planinda cok
      (0.1-0.2 olcekte +%85-89, tamami mola kapsamasi). Butun degiskenler
      ipucuya sabitlenseydi (`fix_variables_to_their_hinted_value`) donen
      `amac_degeri` o gevsek toplam olurdu; K-35 karti planlari bu sayiyla
      kiyasliyor. Olculdu (0.2 olcek, bulut, 1 isci): karar degiskenleri sabit
      0,63 sn, amac = alt sinir, karar degiskenlerinde 0 fark; butun
      degiskenler sabit 0,8 sn.
    ⚠ IPUCU TAM OLMALI: `_tam_ipucu_yaz` butun degiskenleri yazar; yarim
      ipucu (baslangic plani, `_plandan_ipucu`: yalniz x/mola/dinlenme) bu
      yoldan gecmez -- bu "ikinci asamanin plani" olmazdi (K-54 yolu icin
      ayri karar gerekir).
    ⚠ Ipucu gecersiz cikarsa (INFEASIBLE/UNKNOWN) `bulundu: False` doner;
      cagiran eski cevabi ("sure yetmedi") aynen verir. Gecersiz olmamali:
      ipucu ayni modelin alani DARALTILMIS halinin cozumudur ve alanlar
      yalniz genisletildi ya da ipucu degerine sabitlendi.
    Sure: 0.1 olcekte 0,33 sn, 0.2 olcekte 0,7-0,8 sn (bulut, 2 cekirdek);
    tam olcekte olculmedi (dogrusal disdegerleme ~4 sn); tavan
    `ipucu_plani_saniye`.
    """
    proto = kuruldu.m.Proto()
    bilgi = {"bulundu": False, "saniye": 0.0, "durum": None, "durum_kodu": None,
             "sabitlenen": 0, "cozucu": None}
    if len(proto.solution_hint.vars) < len(proto.variables):
        bilgi["durum"] = "ipucu_eksik"
        return bilgi
    ipucu = dict(zip(proto.solution_hint.vars, proto.solution_hint.values))
    for sozluk in (kuruldu.x, kuruldu.mola, kuruldu.dinlenme):
        for v in sozluk.values():
            deger = ipucu.get(v.Index())
            if deger is None:
                continue
            dom = proto.variables[v.Index()].domain
            dom.clear()
            dom.extend([int(deger), int(deger)])
            bilgi["sabitlenen"] += 1
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = max(1.0, float(ayar.get("ipucu_plani_saniye", 30)))
    c.parameters.num_search_workers = 1
    t0 = time.time()
    durum = c.Solve(kuruldu.m)
    bilgi.update({"saniye": round(time.time() - t0, 2), "durum": c.StatusName(durum),
                  "durum_kodu": durum,
                  "bulundu": durum in (cp_model.OPTIMAL, cp_model.FEASIBLE),
                  "cozucu": c})
    return bilgi


def _ipucu_kaynagi(kuruldu):
    """Modeldeki tam ipucu hangi asamanin plani: "ikinci_asama" (iyilestirme
    plan buldu ve ipucu onunla yenilendi), "birinci_asama_korundu"
    (iyilestirmenin plani ipucudan kotuydu, amacsiz plan kaldi) ya da
    "birinci_asama" (iyilestirme kapali / plan bulamadi: amacsiz plan)."""
    iy = getattr(kuruldu, "ilk_asama_iyilestirme", None) or {}
    if iy.get("plan_bulundu") and not iy.get("ipucu_korundu"):
        return "ikinci_asama"
    if iy.get("ipucu_korundu"):
        return "birinci_asama_korundu"
    return "birinci_asama"


def _tam_ipucu_yaz(kuruldu, cozucu):
    """Birinci asamanin cozumunu BUTUN degiskenler icin ipucu yapar."""
    proto = kuruldu.m.Proto()
    degerler = list(cozucu.ResponseProto().solution)
    proto.solution_hint.vars.clear()
    proto.solution_hint.values.clear()
    proto.solution_hint.vars.extend(list(range(len(degerler))))
    proto.solution_hint.values.extend(degerler)


def _molalari_sabitle(kuruldu):
    """Secilmeyen mola adaylarinin alanini [0,0] yapar; donen liste geri
    almak icin. Degisken alani proto uzerinde duzenlenir (cp_model_helper
    `domain.clear()/extend()`); kisit eklenmez."""
    proto = kuruldu.m.Proto()
    sabitlenen = []
    secimler = {t["id"]: kuruldu.sabit_mola_secimi(t) for t in kuruldu.sablonlar}
    for (e, d, tid, s), v in kuruldu.mola.items():
        sy, _ = secimler[tid]
        if sy is not None and s is not None and s != sy:
            sabitlenen.append(v.Index())
    for (e, d, tid, i, s), v in kuruldu.dinlenme.items():
        _, dinl = secimler[tid]
        if i < len(dinl) and dinl[i] is not None and s != dinl[i]:
            sabitlenen.append(v.Index())
    for ix in sabitlenen:
        dom = proto.variables[ix].domain
        dom.clear()
        dom.extend([0, 0])
    return sabitlenen


def _molalari_serbest_birak(kuruldu, sabitlenen):
    proto = kuruldu.m.Proto()
    for ix in sabitlenen:
        dom = proto.variables[ix].domain
        dom.clear()
        dom.extend([0, 1])


def _durgunluk_bekcisiyle_coz(cozucu, model, geri, ayar):
    """K-28'in ikinci kosulu: iyilesme durursa arama biter (T-24a).

    ⚠ NEDEN AYRI BIR BEKCI GEREKTI
      `durgunluk_saniye` parametresi `VARSAYILAN` icinde TANIMLIYDI,
      aciklamasi yaziliydi ("2 dk iyilesme yoksa bitir") ve
      `_ErkenDur.son_iyilesme` her cozumde guncelleniyordu -- ama hicbir
      yerde OKUNMUYORDU. Karar verilmis, belgelenmis, hic uygulanmamis.
      T-24a/T-26'nin ta kendisi.

      28 Eylul'de bedeli olculdu: 35 kisilik gercekci bir sahnede cozucu
      butcenin TAMAMINI (900 sn) kullandi; plani cok daha once bulmustu.

    ⚠ CALLBACK TEK BASINA YETMEZ
      CP-SAT'in cozum callback'i yalniz YENI COZUM bulununca tetiklenir.
      Cozucu tikandiginda callback hic cagrilmaz -- durgunlugu callback'in
      KENDISI fark edemez. Disaridan bakan bir bekci sart.

    Bekci ayri bir is parcaciginda saniyede bir bakar; son iyilesmenin
    uzerinden `durgunluk_saniye` gectiyse `cozucu.StopSearch()` cagirir.
    En az bir cozum bulunmus olmasi sarti var: hicbir plan yokken durmak,
    "cozumsuz" ile "bakmadim"i karistirmak olurdu (T-48'in ayni ailesi).
    """
    import threading

    sinir = ayar.get("durgunluk_saniye") or 0
    if sinir <= 0:
        return cozucu.Solve(model, geri)

    dur = threading.Event()

    def bekci():
        while not dur.wait(1.0):
            if geri.cozum_sayisi == 0:
                continue          # hic plan yok -- durmak yanlis olur
            if time.time() - geri.son_iyilesme >= sinir:
                geri.durma_sebebi = geri.durma_sebebi or "durgunluk"
                cozucu.StopSearch()
                return

    is_parcacigi = threading.Thread(target=bekci, daemon=True)
    is_parcacigi.start()
    try:
        return cozucu.Solve(model, geri)
    finally:
        dur.set()


def _paralel_sec(adaylar):
    """Iki aramadan hangisinin plani donecek: plani olanlardan amaci KUCUK
    olan; esitlikte ipuclu (guvenlik agi). Hicbirinde plan yoksa ipuclu."""
    planli = [a for a in adaylar if a["durum"] in (cp_model.OPTIMAL, cp_model.FEASIBLE)]
    if not planli:
        return adaylar[0]
    return min(planli, key=lambda a: (a["cozucu"].ObjectiveValue(), a["sira"]))


def _paralel_coz(kuruldu, cozucu, geri, ayar, isci):
    """(b) secenegi -- T-60 bulgu 8 (2 Ekim). VARSAYILAN KAPALI.

    Ayni model iki kez, AYNI SUREDE, yan yana aranir:
      ipuclu   : bugunku urun -- birinci asamanin plani ipucu (plan garantisi)
      ipucusuz : ayni modelin KOPYASI, ipucu silinmis (demirsiz arama)
    Isciler bolusulur: ipucusuza `paralel_ipucusuz_isci`, kalani ipucluya
    (en az 1). Biri optimumu/hedef boslugu bulup durursa oteki de durdurulur.
    Donen plan `_paralel_sec`in sectigidir.

    ⚠ MODEL IKI KEZ BELLEKTE durur (kopya). Tam olcekte bellek ve cekirdek
      paylasiminin bedeli OLCULMEDEN bu secenek urune alinmaz.
    ⚠ Kopyanin degisken sirasi asil modelle aynidir; secilen cozucu hangisi
      olursa olsun atamalar asil modelin degiskenleriyle okunur.
    """
    import threading

    ipucusuz_isci = max(1, min(int(ayar["paralel_ipucusuz_isci"]), max(1, isci - 1)))
    ipuclu_isci = max(1, isci - ipucusuz_isci)
    cozucu.parameters.num_search_workers = ipuclu_isci

    kopya = kuruldu.m.Clone()
    kopya.ClearHints()
    cozucu2 = cp_model.CpSolver()
    cozucu2.parameters.copy_from(cozucu.parameters)
    cozucu2.parameters.num_search_workers = ipucusuz_isci
    geri2 = _ErkenDur(ayar)
    geri2.ana_basladi = geri.ana_basladi

    adaylar = [
        {"ad": "ipuclu", "sira": 0, "cozucu": cozucu, "geri": geri, "model": kuruldu.m,
         "isci": ipuclu_isci, "durum": None, "hata": None},
        {"ad": "ipucusuz", "sira": 1, "cozucu": cozucu2, "geri": geri2, "model": kopya,
         "isci": ipucusuz_isci, "durum": None, "hata": None},
    ]

    kanit = threading.Event()

    def kostur(a):
        try:
            a["durum"] = _durgunluk_bekcisiyle_coz(a["cozucu"], a["model"], a["geri"], ayar)
        except Exception as e:                       # pragma: no cover
            a["durum"], a["hata"] = cp_model.UNKNOWN, repr(e)
        # Kanitli bitis (optimum / hedef bosluk): otekinin aramasi gereksiz.
        if a["geri"].durma_sebebi in ("optimum", "hedef_bosluk") \
                or a["durum"] == cp_model.OPTIMAL:
            kanit.set()

    isler = [threading.Thread(target=kostur, args=(a,)) for a in adaylar]
    for i in isler:
        i.start()
    # ⚠ Durdurma TEKRARLANIR: oteki arama henuz baslamamissa tek bir
    #   StopSearch bosa gider ve o arama butcenin tamamini kosar.
    while any(i.is_alive() for i in isler):
        if kanit.wait(0.2):
            for a in adaylar:
                a["cozucu"].StopSearch()
            time.sleep(0.05)
    for i in isler:
        i.join()

    secilen = _paralel_sec(adaylar)
    bilgi = {"secilen": secilen["ad"]}
    for a in adaylar:
        planli = a["durum"] in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        bilgi[a["ad"]] = {
            "isci": a["isci"],
            "plan_bulundu": planli,
            "amac_degeri": int(round(a["cozucu"].ObjectiveValue())) if planli else None,
            "alt_sinir": int(round(a["cozucu"].BestObjectiveBound())) if planli else None,
            "cozum_sayisi": a["geri"].cozum_sayisi,
            "ilk_cozum_sn": (round(a["geri"].ilk_cozum_sn, 2)
                             if a["geri"].ilk_cozum_sn is not None else None),
            "durma_sebebi": a["geri"].durma_sebebi,
            "iyilesme": _iyilesme_ozeti(a["geri"].egri, nokta=12),
            "hata": a["hata"],
        }
    return secilen["cozucu"], secilen["geri"], secilen["durum"], bilgi


def coz(girdi, ayar=None, baslangic_plani=None, kuruldu=None):
    """Master Spec #11.3 ciktisi. Plan URETIR; denetlemez.

    Denetleme bagimsiz dogrulayicinin isidir (#7.6) ve bu fonksiyon onu
    CAGIRMAZ -- cagirsaydi "motor kendi isini kendi onaylar" olurdu.

    `kuruldu`: ayni girdiden ONCEDEN kurulmus Model (1 Ekim). Olcum betigi
    modeli sayim icin bir kez kuruyor, sonra `coz` bir kez daha kuruyordu --
    tam olcekte 55-80 saniye bosa. Verilirse yeniden kurulmaz; model_kurma
    0 yazilir (kurma suresini cagiran olcmustur). Model tek kullanimliktir:
    `coz` ipucu, amac ve alan duzenlemeleriyle onu degistirir.
    """
    ayar = dict(VARSAYILAN, **(ayar or {}))
    # T-59: model kurma AYRI bir kalemdir -- tam olcekte ~50 sn. Kullaniciya
    # ayrica gosterilebilsin diye olculur; cozum butcesinden dusulmez (K-48).
    kurma_basladi = time.time()
    if kuruldu is None:
        kuruldu = Model(girdi).kur()
    model_kurma = time.time() - kurma_basladi

    # ON KONTROL -- cozucuyu calistirmadan once (28 Eylul)
    #
    # Hicbir vardiya sablonunun ULASAMADIGI bir talep hucresi varsa plan
    # imkansizdir ve bunu kanitlamak icin cozucuye gerek yoktur. Ayni cevabi
    # cozucu de veriyordu, ama ancak cozumsuzlugu KANITLADIKTAN sonra:
    # 105 kisilik gercek sahnede 292 saniye, 10 kisilik tek ekipte 73 saniye.
    #
    # Verilen cevap DEGISMEDI, yalnizca fiyati dustu. Ulasilamayan hucre
    # yoksa bu kontrol sessizdir.
    from .teshis import ulasilamayan_hucre, teshis_koy
    erisilmez = ulasilamayan_hucre(girdi, kuruldu)
    if erisilmez:
        return teshis_koy(girdi, kuruldu,
                          {"degisken_sayisi": len(kuruldu.x) + len(kuruldu.mola),
                           "kisit_sayisi": len(kuruldu.m.Proto().constraints),
                           "cozum_sayisi": 0, "motor": "CP-SAT",
                           "profil": kuruldu.profil, "amac_degeri": None,
                           "durma_sebebi": "on_kontrol",
                           "isci_sayisi": isci_sayisi(ayar),
                           "cozum_suresi_sn": 0.0},
                          ayar, on_kontrol=erisilmez)

    cozucu = cp_model.CpSolver()
    cozucu.parameters.max_time_in_seconds = float(ayar["azami_saniye"])
    isci = isci_sayisi(ayar)
    cozucu.parameters.num_search_workers = isci
    # T-60: olcum yapilandirmalarinin CP-SAT parametreleri. Sure ve isci
    # sayisi yukarida yazildi; buradan gelen ayni adli deger onlari EZMEZ.
    for ad, deger in (ayar.get("cozucu_parametreleri") or {}).items():
        if ad in ("max_time_in_seconds", "num_search_workers", "num_workers"):
            kuruldu.notlar.append("cozucu parametresi yok sayildi: %s (sure ve "
                                  "isci sayisi ayar alanlarindan verilir)" % ad)
            continue
        setattr(cozucu.parameters, ad, deger)
    geri = _ErkenDur(ayar)

    # BASLANGIC PLANI varsa onu ipucu yap; yoksa buyuk modelde iki asama.
    # Ikisi ayni mekanizmayi kullanir (solution hint) ama amaclari farkli:
    #   baslangic plani -> KULLANICININ elindeki plandan devam et
    #   iki asama       -> cozucu hic plan bulamiyorsa ona bir tane ver
    baslangic_kullanildi = False
    iki_asama = False
    ilk_basladi = time.time()
    # K-54: yayinlanmis plan (`mevcut_plan`) ayrica verilmis bir baslangic
    # plani yoksa ipucudur -- donmus gunleri zaten sabit, kalan gunler icin
    # "iyilestir, zar atma" (28 Eylul karari) buradan devam eder.
    if not baslangic_plani and girdi.get("mevcut_plan"):
        baslangic_plani = girdi.get("mevcut_plan")
    if baslangic_plani:
        baslangic_kullanildi = _plandan_ipucu(kuruldu, baslangic_plani)
        if not baslangic_kullanildi:
            kuruldu.notlar.append(
                "baslangic plani bu girdiye oturmadi; sifirdan aranacak")
    if not baslangic_kullanildi:
        iki_asama = (len(kuruldu.m.Proto().variables) >= ayar["iki_asama_esigi"]
                     and _ipucu_ver(kuruldu, ayar))

    # K-60 (4 Ekim): ANA ASAMA = MOLA ADIMI. Atamalar birinci asamanin
    # (iyilesmis) planina sabitlenir, yalniz molalarin yeri aranir, kanitli
    # optimumda durur -- hedef_bosluk bu adimda `mola_adimi_hedef_bosluk` (0).
    # Olculdu (bulgu 17-18): 44-46 sn'de optimum, mola acigi 177-188; ortak
    # arama 347 sn'de 193-202. `mola_adimi: False` = eski ortak arama (OLCUM).
    # Iki asama devreye girmediyse (model esigin altinda ya da baslangic
    # plani var, K-54) sabitlenecek plan yoktur: atamalar ve molalar birlikte
    # aranir. Bu bir "uygulanmayan" DEGIL, kucuk modelin olagan yolu -- not
    # dusulmez; ciktida `atamalar_sabit: False` yeter.
    atamalar_sabit = False
    mola_adimi = bool(ayar.get("mola_adimi", True))
    if mola_adimi and iki_asama:
        atamalar_sabit = _atamalari_sabitle(kuruldu) > 0
        geri.ayar = dict(ayar, hedef_bosluk=float(ayar.get("mola_adimi_hedef_bosluk", 0.0)))

    # T-59: ana cozume KALAN verilir. Iki asamanin toplami azami_saniye'yi
    # gecmez. En az 1 saniye: sifir sure CP-SAT'e "hic arama" demek olurdu.
    ilk_asama = time.time() - ilk_basladi
    ana_butce = max(1.0, float(ayar["azami_saniye"]) - ilk_asama)
    cozucu.parameters.max_time_in_seconds = ana_butce

    basladi = time.time()
    geri.ana_basladi = basladi
    paralel = None
    if int(ayar.get("paralel_ipucusuz_isci") or 0) > 0:
        if iki_asama:
            cozucu, geri, durum, paralel = _paralel_coz(kuruldu, cozucu, geri, ayar, isci)
        else:
            kuruldu.notlar.append("paralel_ipucusuz_isci yok sayildi: ipucu yok "
                                  "(iki asama devreye girmedi), yan yana "
                                  "kosturulacak iki arama ayni olurdu")
            durum = _durgunluk_bekcisiyle_coz(cozucu, kuruldu.m, geri, ayar)
    else:
        durum = _durgunluk_bekcisiyle_coz(cozucu, kuruldu.m, geri, ayar)
    sure = time.time() - basladi

    # K-63 (7 Ekim): ANA ASAMA YETISMEDIYSE IKINCI ASAMANIN PLANI DONER.
    # Ana asama plansiz dondu (UNKNOWN: sure yetmedi) ama iki asama ikinci
    # asamanin TAM ipucusunu yazdiysa, o plan gecerlidir ve eldedir: ipucu
    # plana cevrilir, notla doner. Molalar o planda sablonun ideal yerindedir
    # (mola adimi aranmadi). "Sure yetmedi" demek elde plan varken yanlisti
    # (bulgu 24). INFEASIBLE kanittir, buraya girmez (K-37: imkansiz ayri).
    ipucu_plani = None
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.INFEASIBLE) and iki_asama:
        ipucu_plani = _ipucu_planini_al(kuruldu, ayar)
        if ipucu_plani["bulundu"]:
            cozucu, durum = ipucu_plani["cozucu"], ipucu_plani["durum_kodu"]
            # Ipucu hangi asamanin plani? Iyilestirme plan bulduysa ve ipucu
            # korunmadiysa ikincinin; yoksa birincinin AMACSIZ plani (bagimsiz
            # inceleme 3: not yanlis asamayi soylemesin).
            ipucu_plani["kaynak"] = _ipucu_kaynagi(kuruldu)
            kuruldu.notlar.append(
                "%s surede plan uretemedi; %s dondu "
                "(molalar %s, mola yerlesimi aranmadi; optimuma yakinlik kaniti yok)"
                % ("mola adimi" if atamalar_sabit else "ana asama",
                   {"ikinci_asama": "ikinci asamanin plani",
                    "birinci_asama_korundu": "birinci asamanin plani (iyilestirmenin plani ondan kotuydu, ipucu korundu)",
                    "birinci_asama": "birinci asamanin AMACSIZ plani (iyilestirme plan bulamadi)"}[ipucu_plani["kaynak"]],
                   "sablonun ideal yerinde" if ayar.get("ilk_asama_sabit_mola", True)
                   else "birinci asamanin buldugu yerde"))

    # O-16 (6 Ekim): ana asamanin cozdugu model TAM MODEL degilse cozucunun
    # alt siniri ve "optimum"u o KISITLI problemindir -- planin tamami icin
    # kanit DEGIL. Iki kisitli hal var (bkz. `_sinir_kapsami`):
    #   mola_adimi     : atamalar sabit (K-60) -- "bu atamalarla en iyi mola
    #                    yerlesimi"
    #   fazla_mesaisiz : YALNIZ olcum secenegi `fazla_mesai_sifirda_tut`
    #                    (sert kesim): "once fazla mesaisiz" plan buldu ve
    #                    fazla mesai degiskenleri 0'da TUTULDU -- "fazla
    #                    mesaisiz planlarin en iyisi". Urun yolunda (O-18)
    #                    alanlar geri acilir, model tamdir, bu hal olusmaz.
    # K-35 sonuc kartinda "kanitlanmis yakinlik" gosteriyor; kisitli siniri
    # oraya yazmak yalan bir garanti olurdu (olculdu, bulgu 20: "optimum, %0"
    # denen planlarin 4-5,6 kat iyisi vardi). Kuresel sinir yoksa None
    # yazilir; kisitli sinir, kisitin adini tasiyan alana gider.
    kapsam = _sinir_kapsami(atamalar_sabit, kuruldu)
    sinir = _alt_sinir(cozucu, durum)
    sebep = geri.durma_sebebi or _durma_sebebi(durum, cozucu, ayar, sure, ana_butce)
    if kapsam and sebep in _KANIT_SEBEPLERI:
        sebep = kapsam + "_" + sebep
    if paralel and kapsam:
        _paralel_kisitli_isaretle(paralel, kapsam)
    ipucu_plani_dondu = bool(ipucu_plani and ipucu_plani["bulundu"])
    if ipucu_plani_dondu:
        # K-63: donen plan ikinci asamanindir; ana asama hic plan bulmadi.
        # Sabitlenmis ipucunun "optimum"u ve siniri kanit DEGILDIR (tek
        # noktali model): kuresel de kisitli da sinir yazilmaz.
        sebep = "mola_adimi_yetismedi" if atamalar_sabit else "ana_asama_yetismedi"
        sinir = None

    istatistik = {
        "degisken_sayisi": len(kuruldu.x) + len(kuruldu.mola),
        "kisit_sayisi": kuruldu.m.Proto().constraints.__len__(),
        "cozum_sayisi": geri.cozum_sayisi,
        "motor": "CP-SAT",
        "profil": kuruldu.profil,     # #5.4 -- hangi agirlik sutunu kosuldu
        "amac_degeri": _amac_degeri(cozucu, durum),
        # Oranin diger tarafi. Bkz. _alt_sinir: plan mi duzeldi, kanit mi.
        # Ana asama kisitli bir model cozduyse KURESEL sinir yok (None);
        # kisitli sinir kendi alaninda.
        "alt_sinir": sinir if kapsam is None else None,
        "mola_adimi_alt_sinir": sinir if kapsam == "mola_adimi" else None,
        "fazla_mesaisiz_alt_sinir": sinir if kapsam == "fazla_mesaisiz" else None,
        "durma_sebebi": sebep,
        "cozum_suresi_sn": round(sure, 2),
        # T-59: sure uc kaleme ayrildi. Toplam bekleme = model kurma +
        # birinci asama + ana asama; son ikisi azami_saniye'yi gecmez.
        "model_kurma_sn": round(model_kurma, 2),
        "ilk_asama_sn": round(ilk_asama, 2),
        "ana_asama_butce_sn": round(ana_butce, 2),
        # T-60: ana asamada ilk plan kacinci saniyede geldi (plan yoksa None).
        "ilk_cozum_sn": (round(geri.ilk_cozum_sn, 2)
                         if geri.ilk_cozum_sn is not None else None),
        # Kac isciyle kosuldugu. Ekranda gosterilen "degisken | kisit"
        # bilgisinin ayni ailesinden: "neden bu kadar surdu" sorusunun
        # cevabi bunsuz eksik kalir.
        "isci_sayisi": isci,
        "iki_asama": iki_asama,
        # T-60 bulgu 8 olcum secenekleri; kapaliyken None.
        "ilk_asama_iyilestirme": getattr(kuruldu, "ilk_asama_iyilestirme", None),
        "paralel": paralel,
        # K-60: ana asama mola adimi olarak kostu mu (atamalar sabit)?
        "mola_adimi": mola_adimi,
        "atamalar_sabit": atamalar_sabit,
        # K-61 "once fazla mesaisiz". None = denenmedi (iki asama yok,
        # daraltilacak fazla mesai degiskeni yok ya da kapali). Sozluk:
        # `bulundu` / `kanitlandi_yok` / `saniye` denemenin sonucu;
        # `sifirda_tutuldu` yalniz olcum secenegiyle True (sert kesim).
        "fazla_mesai_once_sifir": getattr(kuruldu, "fazla_mesai_once_sifir", None),
        # K-63: ana asama plansizken ikinci asamanin plani alindi mi; None =
        # gerek olmadi. {"bulundu", "saniye", "durum"} -- `saniye` butcenin
        # disindaki tek kalem.
        "ipucu_plani": ({a: ipucu_plani.get(a) for a in ("bulundu", "saniye", "durum", "kaynak")}
                        if ipucu_plani else None),
        "baslangic_plani_kullanildi": baslangic_kullanildi,
        # K-54: donmus gunler -- kac satir aynen gecti, kac kisit gecmise
        # dusuldu/kirpildi (sifirsa alan yine yazilir: "yok" ile "unutuldu"
        # ayrilsin).
        "donmus_gun": {
            "gunler": sorted(kuruldu.donmus),
            "aktarilan_satir": len(kuruldu.donmus_satirlar),
            "dusen_kisit": kuruldu._donmus_dusen,
            "kirpilan_kisit": kuruldu._donmus_kirpilan,
        } if kuruldu.donmus else None,
        # T-60 (2 Ekim): kalite olcumunun iki araci -- amac neyden olusuyor,
        # ne zaman iyilesti. Plan yoksa None.
        "amac_dagilimi": (_amac_dagilimi(kuruldu, cozucu)
                          if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None),
        "iyilesme": _iyilesme_ozeti(geri.egri),
        "baslangic_amac": (round(geri.ilk_amac) if baslangic_kullanildi
                           and geri.ilk_amac is not None else None),
    }

    if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        atamalar = _atamalari_cikar(kuruldu, cozucu)
        metrikler = _metrikler(kuruldu, atamalar, cozucu, sure)
        if kapsam or ipucu_plani_dondu:
            metrikler["optimuma_uzaklik_yuzde"] = None      # O-16 / K-63: kuresel kanit yok
        return {
            "durum": "cozuldu",
            "motor_surumu": SURUM,
            "atamalar": atamalar,
            "metrikler": metrikler,
            "cozum_istatistikleri": istatistik,
            "uygulanmayan_notlar": kuruldu.notlar,
        }

    # ------------------------------------------------------------------
    # K-37 -- "IMKANSIZ" ile "YETISTIREMEDIM" ayri cevaplardir
    #
    # ⚠ NEDEN (Mustafa, 29 Eylul)
    #   Burada eskiden tek satir vardi: plan yoksa teshis koy, "cozumsuz" de.
    #   Oysa cozucu iki bambaska sebeple plansiz doner:
    #
    #     INFEASIBLE : KANITLADI -- boyle bir plan yok
    #     UNKNOWN    : SURE DOLDU -- ariyordu, yetistiremedi
    #
    #   Ikisine de "cozumsuz" demek, yoneticiye "bu talebi bu kadroyla
    #   karsilamak imkansiz" dedirtiyordu -- personel alimina kadar giden
    #   bir karar, ve dayanagi olmayabilirdi.
    #
    #   Ustelik teshis ucuz degil: her sert kurali tek tek gevsetip yeniden
    #   cozer. Olculdu -- 45 saniyelik butce TOPLAM 470 saniye surdu.
    #   Kullanici butcesini bekledikten sonra 7 dakika daha bekleyip
    #   muhtemelen yanlis bir cumle aliyordu.
    #
    #   Artik: kanit varsa teshis kosar; yoksa kosmaz ve kullaniciya
    #   "neden oldugunu arastir" secenegi sunulur (`teshis_iste`).
    # ------------------------------------------------------------------
    if durum == cp_model.INFEASIBLE:
        return teshis_koy(girdi, kuruldu, istatistik, ayar)

    if ayar.get("teshis_iste"):
        # Kullanici dugmeye basti: bekleme onun SECIMI. Ama cikan teshis
        # yine de kanit degildir ve oyle isaretlenir -- aksi halde ayni
        # yanlis cumleyi bu kez dugme arkasindan soylerdik.
        return teshis_koy(girdi, kuruldu, istatistik, ayar, kesin=False)

    return {
        "durum": "sure_yetmedi",
        "motor_surumu": SURUM,
        "aciklama": ("Verilen surede plan bulunamadi. Boyle bir planin "
                     "OLMADIGI kanitlanmis DEGILDIR -- daha uzun sure ile "
                     "bulunabilir."),
        "verilen_saniye": ayar["azami_saniye"],
        "teshis_istenebilir": True,
        "cozum_istatistikleri": istatistik,
        "uygulanmayan_notlar": kuruldu.notlar,
    }


SURUM = "0.2.0-cozucu"

# Kanit iddia eden durma sebepleri (O-16): kisitli bir model cozulduyse bunlar
# kisitin adini on ek olarak alir. "durgunluk" / "butce_doldu" kanit iddia
# etmez, aynen kalir.
_KANIT_SEBEPLERI = ("optimum", "hedef_bosluk")


def _sinir_kapsami(atamalar_sabit, kuruldu):
    """Ana asamanin cozdugu model TAM MODEL mi? None = evet (alt sinir
    kureseldir). Degilse kisitin adi -- O-16:

      "mola_adimi"     atamalar sabit (K-60)
      "fazla_mesaisiz" "once fazla mesaisiz" denemesi plan BULDU ve fazla
                       mesai degiskenleri 0'da kaldi. Deneme basarisizsa
                       alanlar geri acilmistir: model tamdir.
    Ikisi birden gecerliyse (urun yolu + secenek) "mola_adimi": atamalar
    sabitken fazla mesai zaten belirlidir."""
    if atamalar_sabit:
        return "mola_adimi"
    if (getattr(kuruldu, "fazla_mesai_once_sifir", None) or {}).get("sifirda_tutuldu"):
        return "fazla_mesaisiz"
    return None


def _paralel_kisitli_isaretle(paralel, kapsam):
    """(b) kollari da ayni kisitli modeli cozer (kopya, alanlar
    daraltildiktan SONRA alinir): sinirlari kuresel diye yazilmaz, kanit
    iddia eden sebepleri on ek alir."""
    for kol in ("ipuclu", "ipucusuz"):
        b = paralel.get(kol)
        if not b:
            continue
        b["alt_sinir"] = None
        if b.get("durma_sebebi") in _KANIT_SEBEPLERI:
            b["durma_sebebi"] = kapsam + "_" + b["durma_sebebi"]


def _amac_degeri(cozucu, durum):
    """Donen planin amac fonksiyonu degeri -- yumusak kural cezalarinin toplami.

    NEDEN CIKTIDA
      1. Uc plan karti (#9.5) kullaniciya "hangisi daha iyi" diye soruyor;
         karsilastirilacak bir SAYI olmadan bu soru olculemez.
      2. Agirliklarin gercekten ise yaradigini sinamanin tek saglam yolu bu.
         "Motor su kisiyi secti" testi kirilgan: kisit gevsekse cozucu esit
         degerdeki secenekler arasinda rastgele secer ve test yanlis yesil
         yanar. Ayni girdiyi iki kez, iki farkli secim SABITLENMIS halde
         cozup amac degerlerini karsilastirmak ise kesindir.

    Cozum yoksa None -- "0" demek yaniltici olurdu.
    """
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    try:
        return int(round(cozucu.ObjectiveValue()))
    except Exception:
        return None


def _alt_sinir(cozucu, durum):
    """Cozucunun KANITLADIGI alt sinir: optimum bundan iyi OLAMAZ.

    ⚠ NEDEN CIKTIDA (29 Eylul)
      `optimuma_uzaklik_yuzde` = (amac - alt sinir) / amac. Tek bir oran
      olarak bakildiginda IKI ayri iyilesme ayni gorunuyor:

          PLAN duzeldi   -> amac dustu      (sahada daha iyi vardiya)
          KANIT guclendi -> alt sinir cikti (ayni plan, daha az suphe)

      350 kisilik sahnede tam bu soru cevapsiz kaldi: 900 saniye 360
      saniyeden neden daha iyi? Oranin iki tarafi da yazilmadan bu
      ayrilamiyor -- ve K-35 kullaniciya sure sectirirken hangisini
      vaat ettigimizi bilmemiz gerekiyor.

    Plan yoksa None -- "0" demek "optimum sifir olabilir" anlamina gelirdi.
    """
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    try:
        return int(round(cozucu.BestObjectiveBound()))
    except Exception:
        return None


def _durma_sebebi(durum, cozucu, ayar, sure, butce=None):
    """⚠ T-59: kiyas ANA ASAMANIN PAYIYLA yapilir. Pay artik azami_saniye'den
    kucuk olabilir; eski kiyas (`azami_saniye x 0,95`) o zaman hic tutmaz
    ve butcesini dolduran kosu 'bilinmiyor' diye raporlanirdi."""
    if durum == cp_model.OPTIMAL:
        return "optimum"
    if durum == cp_model.INFEASIBLE:
        return "cozumsuz"
    if butce is None:
        butce = ayar["azami_saniye"]
    if sure >= butce * 0.95:
        return "butce_doldu"
    return "bilinmiyor"


def _atamalari_cikar(kuruldu, cozucu):
    cikan = []
    for (e, d, tid), v in sorted(kuruldu.x.items()):
        if d in kuruldu.donmus:
            continue          # K-54: donmus gun satirlari plandan AYNEN gecer
        if not cozucu.Value(v):
            continue
        sablon = kuruldu.sablon[tid]
        molalar = []
        yemek_dk = kuruldu.yemek_dk[tid]
        for s in _mola_baslangiclari(sablon, kuruldu.mola_penceresi, yemek_dk):
            if s is not None and cozucu.Value(kuruldu.mola[(e, d, tid, s)]):
                # K-32: cozucunun yerlestirdigi tek mola UCRETSIZ ogle
                # arasidir -- calisma suresinden de ucret hesabindan da
                # dusulur. Ucretli kisa molalarin yerlesimi HENUZ YAZILMADI
                # (mola_politikasi, K-32 madde 6); o gelene kadar cozucu
                # yalniz yemek uretir.
                molalar.append({"bas": s,
                                "bit": s + yemek_dk / 60.0,
                                "tip": "yemek"})
        # Ucretli kisa molalar -- vardiyaya ESIT dagitilmis (K-32, 28 Eylul)
        _, dinlenme_dk = kuruldu.dinlenme_tanim[tid]
        for i, adaylar in enumerate(kuruldu._dinlenme_adaylari(sablon)):
            for s in adaylar:
                anahtar = (e, d, tid, i, s)
                if anahtar in kuruldu.dinlenme and cozucu.Value(kuruldu.dinlenme[anahtar]):
                    molalar.append({"bas": s,
                                    "bit": s + dinlenme_dk / 60.0,
                                    "tip": "dinlenme"})
        molalar.sort(key=lambda mm: mm["bas"])
        # K-50 (T-21): atamanin ekibi SABLONUN ekibidir, yoksa kisinin ilk
        # ekibi -- modelin kapsama sayimiyla (Model._atama_ekibi) AYNI.
        kisi = next((c for c in kuruldu.calisanlar if c["id"] == e), None)
        ekip = kuruldu._atama_ekibi(kisi or {}, sablon)
        cikan.append({"calisan": e, "ekip": ekip, "sablon": tid, "gun": d,
                      "bas": sablon["bas"], "bit": sablon["bit"], "molalar": molalar})
    if kuruldu.donmus_satirlar:
        # Mevcut planin donmus gun satirlari: cozucu URETMEDI, AKTARDI.
        # Molalar dahil yoneticinin biraktigi haliyle; `donmus: True` isareti
        # okuyana "bu satir bu kosuda uretilmedi" der.
        import copy as _copy
        cikan.extend(_copy.deepcopy(kuruldu.donmus_satirlar))
        cikan.sort(key=lambda a: (str(a.get("calisan")), a.get("gun", 0),
                                  float(a.get("bas", 0))))
    return cikan


def _metrikler(kuruldu, atamalar, cozucu, sure):
    """Motorun KENDI olcumu.

    ⚠ Bu sayilar bagimsiz dogrulayicinin sayilariyla KARSILASTIRILMAK icin
    var, onun yerine gecmek icin degil. A1 fiksturu ikisini de istiyor:
    once motor "0 sert ihlal" diyor, sonra dogrulayici ayrica sayiyor.
    Motorun kendi metrigine guvenilmez -- bu bilincli bir tasarim.
    """
    girdi = kuruldu.girdi
    asgari_tut = asgari_top = hedef_tut = hedef_top = eksik_dk = 0
    kisiler = {c["id"]: c for c in kuruldu.calisanlar}
    for t, gun, saat in kuruldu._hucreler():
        # ⚠ BURADA `int()` VARDI VE KESIRLI VARDIYA SINIRINI KIRPIYORDU (T-65)
        #   Eski satir: `gun*24 + saat in range(... int(a["bas"]), ... int(a["bit"]))`
        #   Vardiya 07:00-16:15 ise `int(16.25)` = 16 ve `range(7, 16)` saat
        #   16'yi DISARIDA birakiyordu -- oysa vardiya 16:00-16:15 arasi
        #   sahada ve kisit tarafi (`_atanmis` -> `_dilimler` -> `_q`) o
        #   ceyregi sayiyor. Sonuc: kisit saglanmis, metrik "kapanmadi"
        #   diyor. 415 hucreli sahnede BIR hucre bu yuzden eksik sayildi
        #   ve CI kirmizi yandi (%99,76).
        #
        #   K-34 ceyrek izgarasindan beri sablonlarin cogu kesirli bitiyor
        #   (16.25, 18.75, 20.25...), yani bu kirpma artik istisna degil
        #   kural. Karsilastirma mutlak zamanda ve KESIRLI yapilir --
        #   dogrulayicinin `zaman.atanmis_mi`si de boyle calisiyor.
        #
        #   ⚠ T-58 ILE AYNI AILE: 29 Eylul'de ayni `int()` varsayimi
        #   dogrulayiciyi cokertiyordu, orada duzeltildi, buradaki
        #   kopyasina bakilmadi. Ayni hatayi iki yerde aramak gerekiyor --
        #   #7.6'nin bedeli bu.
        an = gun * 24 + saat
        # K-50: kim sayilir -- modelle ayni olcu (`hepsi`: uyelik).
        sayi = sum(1 for a in atamalar
                   if kuruldu._sayilir(kisiler.get(a["calisan"], {}),
                                       # K-54: aktarilan satirin sablonu
                                       # modelde olmayabilir; ekibi satirdan.
                                       kuruldu.sablon.get(a.get("sablon"),
                                                          {"ekip": a.get("ekip")}),
                                       t.get("ekip"))
                   and a["gun"] * 24 + a["bas"] <= an
                   < a["gun"] * 24 + a["bit"])
        sayi += kuruldu._devir_sayisi(t.get("ekip"), gun, saat)      # K-56
        if t.get("asgari") is not None:
            asgari_top += 1
            asgari_tut += 1 if sayi >= t["asgari"] else 0
        if t.get("hedef") is not None:
            hedef_top += 1
            if sayi >= t["hedef"]:
                hedef_tut += 1
            else:
                eksik_dk += (t["hedef"] - sayi) * 60

    # ⚠ FAZLA MESAI = YASAL TANIM (K-57, 2 Ekim): CALISMA SURESI (butun
    #   molalar dusuk -- modelin `_net_saat`i, `fm_` cezasiyla AYNI olcu)
    #   sozlesme saatinin ustu; yari zamanliya yazilmaz (45 saate kadar
    #   "ek mesai", carpan ayni). 2 Ekim'e kadar burasi "brut - sablonun
    #   mola_dk'si" sayiyordu: ucretli dinlenme molalari dusulmuyordu ve
    #   sayi cezadan 10 kat buyuk cikiyordu (0.1 olcekte 117-127 saat
    #   karsiliginda ceza 5-10 saat; T-60 olcumu).
    net = {}
    for a in atamalar:
        s = kuruldu.sablon.get(a.get("sablon"))
        if s is not None:
            saat = _net_saat(s)
        else:                # K-54: aktarilan satir -- molalar satirdan
            saat = (a["bit"] - a["bas"]) - sum(
                (m.get("bit", 0) - m.get("bas", 0)) for m in (a.get("molalar") or []))
        net[a["calisan"]] = net.get(a["calisan"], 0.0) + saat
    fazla = 0.0
    for c in kuruldu.calisanlar:
        sozlesme = c.get("sozlesme") or {}
        if sozlesme.get("tip") == "yari_zamanli":
            continue
        soz = sozlesme.get("haftalik_saat")
        if soz is not None:
            fazla += max(0.0, net.get(c["id"], 0.0) - soz)

    yuzde = lambda tut, top: 100.0 if top == 0 else round(100.0 * tut / top, 2)
    return {
        # ⚠ `sert_ihlal` BURADAN KALDIRILDI -- K-51 (Mustafa, 1 Ekim):
        #   "Kaldiralim; ihlaller degisken degil sonucta, birinin saptamasi
        #   bizim icin yeterlidir." Alan sabit sifir yaziyordu, olculmuyordu
        #   (T-66). Tek dogru sayi bagimsiz dogrulayicininki
        #   (`dogrulayici.degerlendir` -> metrikler.sert_ihlal / yayin_kapisi).
        #   Motorun kendi isini kendi onaylamasi #7.6'nin yasakladigi sey.
        "asgari_kapsama_yuzde": yuzde(asgari_tut, asgari_top),
        "hedef_kapsama_yuzde": yuzde(hedef_tut, hedef_top),
        "eksik_hedef_dakika": eksik_dk,
        "toplam_saat": round(sum(net.values()), 2),
        "fazla_mesai_saat": round(fazla, 2),
        "optimuma_uzaklik_yuzde": _bosluk(cozucu),
        "cozum_suresi_sn": round(sure, 2),
    }


# Ceza degiskeni adi -> kural (model.py'deki NewIntVar adlari).
_CEZA_ONEKI = {"he": "HEDEF_KAPSAMA", "ha": "HEDEF_ASIMI", "me": "MOLA_KAPSAMASI",
               "fm": "FAZLA_MESAI", "ag": "ADALET_DENGESI", "sd": "SAAT_DENGESI"}


def _amac_dagilimi(kuruldu, cozucu):
    """Amac degerinin KURAL BASINA kirilimi -- T-60 (2 Ekim).

    `optimuma_uzaklik_yuzde` tek sayi: amacin neyden olustugunu soylemiyor.
    Kalite karari icin once "ceza nereden geliyor" bilinmeli: hedef altinda
    kalan hucreler mi (kapasite yetmiyor olabilir), adalet mi (dagitim),
    mola kapsamasi mi (asgari == hedef hucrelerde her mola bir dip), fazla
    mesai mi. Her kural icin: ceza (agirlik x deger toplami) ve ham deger
    toplami (kac kisi-saat / kac birim).
    """
    dagilim = {}
    for agirlik, v in kuruldu.cezalar:
        try:
            deger = cozucu.Value(v)
        except Exception:
            continue
        onek = (v.Name().split("_", 1)[0] if hasattr(v, "Name") else "?")
        kural = _CEZA_ONEKI.get(onek, onek)
        d = dagilim.setdefault(kural, {"ceza": 0, "deger": 0, "degisken": 0})
        d["ceza"] += agirlik * deger
        d["deger"] += deger
        d["degisken"] += 1
    toplam = sum(d["ceza"] for d in dagilim.values()) or 1
    for d in dagilim.values():
        d["pay_yuzde"] = round(100.0 * d["ceza"] / toplam, 1)
    return dict(sorted(dagilim.items(), key=lambda kv: -kv[1]["ceza"]))


def _iyilesme_ozeti(egri, nokta=40):
    """Iyilesme egrisinin ozeti -- T-60 (2 Ekim).

    Donen: ilk/son amac, kacinci saniyede toplam iyilesmenin %50/%90/%99'una
    ulasildigi, ve en cok `nokta` noktaya inceltilmis egri [(sn, amac,
    alt_sinir)]. Egri bos ise None.

    ⚠ O-16: egri ANA ASAMANIN egrisidir. Ana asama kisitli bir model
      cozduyse (mola adimi: `atamalar_sabit: True`; ya da fazla mesaisiz
      kosu: `fazla_mesaisiz_alt_sinir` dolu) buradaki sinirlar
      (`alt_sinir_son`, egrinin ucuncu sutunu) o KISITLI modelin siniridir --
      planin tamami icin kanit DEGIL.
    """
    if not egri:
        return None
    ilk, son = egri[0][1], egri[-1][1]
    kazanc = ilk - son
    esikler = {}
    for ad, oran in (("yuzde50_sn", 0.5), ("yuzde90_sn", 0.9), ("yuzde99_sn", 0.99)):
        hedef = ilk - kazanc * oran
        esikler[ad] = next((sn for sn, amac, _ in egri if amac <= hedef), None) if kazanc > 0 else 0.0
    if len(egri) > nokta:
        adim = len(egri) / float(nokta)
        secilen = [egri[int(i * adim)] for i in range(nokta)]
        if secilen[-1] != egri[-1]:
            secilen.append(egri[-1])
    else:
        secilen = list(egri)
    return {"ilk_amac": ilk, "son_amac": son, "cozum": len(egri),
            "son_iyilesme_sn": egri[-1][0], "alt_sinir_son": egri[-1][2],
            "egri": [[sn, a, b] for sn, a, b in secilen], **esikler}


def _bosluk(cozucu):
    try:
        deger, sinir = cozucu.ObjectiveValue(), cozucu.BestObjectiveBound()
        if deger == 0:
            return 0.0
        return round(100.0 * abs(deger - sinir) / abs(deger), 3)
    except Exception:
        return None
