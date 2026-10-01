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

BU DOSYA DOGRULAYICIDAN BAGIMSIZDIR (#7.6, #16.1).
"""

import time

from ortools.sat.python import cp_model

from .model import (Model, _mola_baslangiclari, _mola_dilimleri,
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

    def on_solution_callback(self):
        self.cozum_sayisi += 1
        self.son_iyilesme = time.time()
        if self.ilk_amac is None:
            self.ilk_amac = self.ObjectiveValue()
            self.ilk_cozum_sn = time.time() - (self.ana_basladi or self.baslangic)
        sinir = self.BestObjectiveBound()
        deger = self.ObjectiveValue()
        if deger > 0 and abs(deger - sinir) / abs(deger) <= self.ayar["hedef_bosluk"]:
            self.durma_sebebi = "hedef_bosluk"
            self.StopSearch()
        elif deger == 0 and sinir == 0:
            self.durma_sebebi = "optimum"
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
    """
    if not kuruldu.cezalar:
        return False                      # amac yok; iki asamanin anlami yok

    def amaci_geri_koy():
        kuruldu.m.Minimize(sum(a * v for a, v in kuruldu.cezalar))

    kuruldu.m.ClearObjective()
    sabitlenen = _molalari_sabitle(kuruldu) if ayar.get("ilk_asama_sabit_mola", True) else []
    try:
        c = cp_model.CpSolver()
        c.parameters.max_time_in_seconds = _ilk_asama_payi(ayar)
        c.parameters.num_search_workers = isci_sayisi(ayar)
        if c.Solve(kuruldu.m) not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
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
        return True
    finally:
        _molalari_serbest_birak(kuruldu, sabitlenen)
        amaci_geri_koy()


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

    # T-59: ana cozume KALAN verilir. Iki asamanin toplami azami_saniye'yi
    # gecmez. En az 1 saniye: sifir sure CP-SAT'e "hic arama" demek olurdu.
    ilk_asama = time.time() - ilk_basladi
    ana_butce = max(1.0, float(ayar["azami_saniye"]) - ilk_asama)
    cozucu.parameters.max_time_in_seconds = ana_butce

    basladi = time.time()
    geri.ana_basladi = basladi
    durum = _durgunluk_bekcisiyle_coz(cozucu, kuruldu.m, geri, ayar)
    sure = time.time() - basladi

    istatistik = {
        "degisken_sayisi": len(kuruldu.x) + len(kuruldu.mola),
        "kisit_sayisi": kuruldu.m.Proto().constraints.__len__(),
        "cozum_sayisi": geri.cozum_sayisi,
        "motor": "CP-SAT",
        "profil": kuruldu.profil,     # #5.4 -- hangi agirlik sutunu kosuldu
        "amac_degeri": _amac_degeri(cozucu, durum),
        # Oranin diger tarafi. Bkz. _alt_sinir: plan mi duzeldi, kanit mi.
        "alt_sinir": _alt_sinir(cozucu, durum),
        "durma_sebebi": (geri.durma_sebebi
                         or _durma_sebebi(durum, cozucu, ayar, sure, ana_butce)),
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
        "baslangic_amac": (round(geri.ilk_amac) if baslangic_kullanildi
                           and geri.ilk_amac is not None else None),
    }

    if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        atamalar = _atamalari_cikar(kuruldu, cozucu)
        return {
            "durum": "cozuldu",
            "motor_surumu": SURUM,
            "atamalar": atamalar,
            "metrikler": _metrikler(kuruldu, atamalar, cozucu, sure),
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
        return int(cozucu.ObjectiveValue())
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

    net = {}
    for a in atamalar:
        s = kuruldu.sablon.get(a.get("sablon"))
        if s is None:        # K-54: aktarilan satir -- saati satirdan
            s = {"bas": a["bas"], "bit": a["bit"],
                 "mola_dk": sum((m.get("bit", 0) - m.get("bas", 0)) * 60
                                for m in (a.get("molalar") or [])
                                if m.get("tip") == "yemek")}
        net[a["calisan"]] = net.get(a["calisan"], 0.0) + (s["bit"] - s["bas"]) \
            - s.get("mola_dk", 0) / 60.0
    fazla = 0.0
    for c in kuruldu.calisanlar:
        soz = (c.get("sozlesme") or {}).get("haftalik_saat")
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


def _bosluk(cozucu):
    try:
        deger, sinir = cozucu.ObjectiveValue(), cozucu.BestObjectiveBound()
        if deger == 0:
            return 0.0
        return round(100.0 * abs(deger - sinir) / abs(deger), 3)
    except Exception:
        return None
