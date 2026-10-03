# -*- coding: utf-8 -*-
"""
ZOR OLCEK -- otomatik kosuya bagli bekciler

NEDEN VAR (Mustafa, 29 Eylul)
  "Patlasa da catlasa da en zor senaryo ile test etmeliyiz, bunu asarsak
   konuyu cozmus olacagiz zaten. Konuyu cozmek icin problemi daraltma bir
   daha!"

  28 Eylul'de kurulan 350 kisilik set EKSIK cikmisti: 39 kuraldan 15'inin
  govdesi yoktu, 13'u hic zorlanmiyordu, kadro talebin IKI KATIYDI ve 45
  saatlik sozlesme sablonlarla tutturulamiyordu. Yani set bizi kiramiyordu.

  29 Eylul'de yeniden kuruldu: 500 kisi, iki doluluk (%85 ve %95), 40 kural.
  Daha kapiya baglanmadan UC hata buldu -- kesirli vardiya bitisi (T-58),
  net saat ayrismasi (T-57) ve K-38'in dogrulayiciya uygulanmamis olmasi.

IKI SET, TEK FARK
  `_sahne-S30-85.json`  kadroda bolluk -- olculen sey PARA
  `_sahne-S30-95.json`  kadro siki    -- fazla mesai zorunlu hale gelir
  Aralarindaki TEK fark talep tablosu. Ayni kisiler, ayni sablonlar,
  ayni kurallar; yoksa aradaki farkin neyden geldigi soylenemez.

⚠ NE KOSAR, NE KOSMAZ
  Tam olcekli COZUM (500 kisi) dakikalar suruyor; her push'ta kosamaz.

    COZMEDEN olculebilenler  -> TAM OLCEKTE kosar (model kurma ~65 sn)
    cozum gerektirenler      -> KUCULTULMUS olcekte, yalniz %95 seti

  Tam olcekli cozum elle: `py coz-olc.py --saniye 900`

⚠ KUCULTMEK KOLAYLASTIRMAZ
  Olcegi dusurmek sahneyi ZORLASTIRIR: kisi sayisi duser ama 7/24 kapsama
  yapisi aynen kalir. 0.1 olcek (49 kisi) alt sinir kabul edildi.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py -m pytest testler -q
"""

import importlib.util
import io
import json
import os
import sys

import pytest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOK = os.path.dirname(os.path.dirname(BURASI))
MOTOR = os.path.join(KOK, "09-motor")
for y in (MOTOR, BURASI):
    if y not in sys.path:
        sys.path.insert(0, y)

from cozucu.model import Model, _net_saat                     # noqa: E402
from cozucu.coz import coz                                    # noqa: E402
from cozucu.teshis import ulasilamayan_hucre                  # noqa: E402
from dogrulayici import degerlendir, zaman                    # noqa: E402
from uret_veri_seti import sahne_uret                         # noqa: E402

SAHNELER = {0.85: "_sahne-S30-85.json", 0.95: "_sahne-S30-95.json"}


def _yukle(ad):
    """Tireli betikleri modul olarak yukler (`kural-kapsamasi.py` gibi)."""
    yol = os.path.join(BURASI, ad)
    spec = importlib.util.spec_from_file_location(ad.replace("-", "_"), yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _diskten(doluluk):
    return json.load(io.open(os.path.join(BURASI, "fikstur", SAHNELER[doluluk]),
                             encoding="utf-8"))


@pytest.fixture(scope="module")
def tam():
    """%95 seti, tam olcek. BIR KEZ uretilir."""
    return sahne_uret(1.0, 0.95)


@pytest.fixture(scope="module")
def kurulu(tam):
    """Tam olcekli model BIR KEZ kurulur -- 500 kiside ~65 saniye."""
    return Model(tam).kur()


# ----------------------------------------------------------------------
# 1 · COZMEDEN olculenler -- TAM OLCEKTE
# ----------------------------------------------------------------------

@pytest.mark.parametrize("doluluk", [0.85, 0.95])
def test_fikstur_URETICIYLE_ayni(doluluk):
    """Diskteki sahne, ureticinin bugun urettigiyle ayni olmali.

    Tohum sabit oldugu icin ayni girdi ayni dosyayi uretir. Ayrisirlarsa
    ya uretici degismis ve fikstur tazelenmemistir, ya da fikstur elle
    duzenlenmistir -- ikisi de sessizce gecmemeli.
    """
    d = _diskten(doluluk)
    u = sahne_uret(1.0, doluluk)
    assert len(d["calisanlar"]) == len(u["calisanlar"])
    assert len(d["talep"]) == len(u["talep"])
    assert len(d["kurallar"]) == len(u["kurallar"])
    assert d["_hedef_kisi_saat"] == u["_hedef_kisi_saat"], (
        "talep toplami ayristi: diskte %s, ureticide %s"
        % (d["_hedef_kisi_saat"], u["_hedef_kisi_saat"]))


@pytest.mark.parametrize("doluluk", [0.85, 0.95])
def test_DOLULUK_hedeflenen_oranda(doluluk):
    """Iki setin tek farki bu olmali; oran kayarsa karsilastirma anlamsizlasir."""
    d = _diskten(doluluk)
    oran = float(d["_hedef_kisi_saat"]) / float(d["_kapasite_saat"])
    assert abs(oran - doluluk) < 0.01, (
        "doluluk %%%.1f olmali, %%%.1f cikti" % (100 * doluluk, 100 * oran))


def test_sahne_KATALOGUN_TAMAMINI_tanimlar(tam):
    """40 kuralin hepsi sahnede aktif olmali.

    Biri dusarse veri seti sessizce daralir ve "her sey test ediliyor"
    cumlesi yalan olur. 29 Eylul'de tam bu oldu: K-40 `GECE_UYGUNLUGU`'yu
    ekledi, set 39 kuralla kaldi ve bu bekci yakaladi.
    """
    from dogrulayici import kurallar as K
    aktif = {k["kod"] for k in tam["kurallar"] if k.get("aktif", True)}
    assert len(aktif) >= 40, "sahnede %d kural var, 40 bekleniyordu" % len(aktif)
    eksik = set(K.KAYIT) - aktif
    assert not eksik, "govdesi yazili ama sahnede tanimli olmayan: %s" % sorted(eksik)


def test_SABLONLAR_45_SAATI_tutturabiliyor(tam):
    """⚠ T-51 / T-57'nin bekcisi.

    45 saatlik sozlesme, sablonlar elvermiyorsa MATEMATIKSEL OLARAK
    tutturulamaz. 28 Eylul setinde SATIS'in en uzunu 7,0 netti: 6 gunde
    42 saat. 17 kisiden 45'i tutturan SIFIRDI ve plan yine de
    "0 sert ihlal, yayinlanabilir: True" donuyordu.

    Her ekipte 6x ya da 5x ile tam 45 eden bir sablon olmali. `_net_saat`
    butun molalari duser (T-57) -- yani bu test o duzeltmenin de bekcisi.
    """
    ekipler = {t.get("ekip") for t in tam["vardiya_sablonlari"]}
    for ekip in sorted(x for x in ekipler if x):
        netler = [_net_saat(t) for t in tam["vardiya_sablonlari"]
                  if t.get("ekip") == ekip and "gunler" not in t]
        tutar = [n for n in netler
                 if abs(6 * n - 45) < 1e-6 or abs(5 * n - 45) < 1e-6]
        assert tutar, (
            "%s ekibinde 45 saati tutturan sablon yok. Net sureler: %s"
            % (ekip, sorted(netler)))


def test_MODEL_BUYUKLUGU_beklenen_aralikta(kurulu):
    """Model buyuklugu regresyon bekcisi -- cozmeden, dakikalar icinde.

    ⚠ NEDEN BU TEST VAR
      28 Eylul'de motor her kisiye BUTUN sablonlarin degiskenini aciyordu;
      bir SATIS calisani icin BACKOFFICE'in sablonlari dahil. Degiskenlerin
      %64'u bosunaydi ve bu bir DOGRULUK hatasinin yan urunuydu.

      Olculen (29 Eylul, 500 kisi, 17 sablon): 638.572 degisken, 754.633
      kisit. Sinir genis birakildi: yeni bir kural degisken ekleyebilir.
      Amac kucuk dalgalanmayi degil KAT KAT buyumeyi yakalamak.
    """
    n = len(kurulu.m.Proto().variables)
    assert 450_000 <= n <= 900_000, (
        "model buyuklugu beklenen araligin disinda: %d degisken. "
        "Cok buyukse ekip suzgeci bozulmus olabilir, cok kucukse bir "
        "kural dusmustur." % n)


def test_TALEP_HUCRELERINE_ULASILABILIYOR(tam, kurulu):
    """Hicbir talep hucresi vardiyasiz kalmamali -- cozmeden.

    28 Eylul: Pazartesi 00:00-06:00'ya talep yazilmisti ama o saatleri
    yalniz Pazar gecesi baslayan bir vardiya kapatabilirdi. Plan
    cozumsuzdu ve sebebi 292 saniye sonra ogreniliyordu.
    """
    erisilmez = ulasilamayan_hucre(tam, kurulu)
    assert erisilmez is None, (
        "hicbir vardiyanin ulasamadigi talep hucresi var: %s" % erisilmez)


def test_HER_KURAL_kirmizi_yanabiliyor():
    """Govdesi yazili her kural, kendi ihlal vakasinda kirmizi yanmali.

    Bu, "kullanmadigimiz hicbir kural olmasin" cumlesinin olcumu.
    Bir kural sessiz kalirsa ya govdesi bozulmustur ya vakasi kaymistir.

    ⚠ 29 Eylul'de iki kez isirdi: K-40 yeni kural ekledi (vakasi yoktu) ve
      K-39 `PART_TIME_LIMIT`'in tavanini degistirdi (eski vaka artik
      ihlal uretmiyordu, SESSIZ kaldi).

    ⚠ 30 Eylul -- BU TESTIN KENDI BOSLUGU KAPANDI
      `eksik` eskiden yalniz "yazdigim vakalarin kaci sessiz kaldi"
      sayiyordu. Govdesi yazili ama VAKASI OLMAYAN bir kural bu sayida
      hic gorunmuyordu; yani yeni bir kural govdesi yazmak bu testi
      kirmizi yakmiyordu. ROL_KAPSAMASI ve YETKINLIK_KAPSAMASI govdeleri
      yazilinca bu gorundu: arac "EKSIK: 0" demeye devam etti.
      Arac artik evreni dogrulayicinin KAYIT sozlugunden aliyor.
    """
    kk = _yukle("kural-kapsamasi.py")
    iv = _yukle("ihlal-vakalari.py")
    g = _diskten(0.95)
    basarili, eksik = iv.kostur(g, kk.kaba_plan(g))
    assert eksik == 0, (
        "%d kural kendi ihlal vakasinda kirmizi YANMADI ya da vakasi hic "
        "YOK -- ayrinti icin `py ihlal-vakalari.py -v`" % eksik)
    # 30 Eylul: 31 -> 33 (gece postasi devri, ardisik hafta sonu). Ikisinin
    # vakasi GECMISE dokunur -- sahne gecmissiz oldugu icin temel planda
    # isiramazlar.
    assert basarili >= 33, "beklenen en az 33 kural, %d geldi" % basarili


# ----------------------------------------------------------------------
# 2 · COZUM gerektirenler -- KUCULTULMUS olcekte, YALNIZ %95 seti
# ----------------------------------------------------------------------
#
# ⚠ Olcek 0.1'de SABIT. Daha kucugu KOLAY DEGIL, ZOR: kisi sayisi duser
#   ama 7/24 kapsama yapisi ayni kalir.
# ⚠ Yalniz %95 kosar: iki seti de cozmek CI'da gereksiz uc dakika, ve
#   %95 olan ZOR olani.

@pytest.fixture(scope="module")
def kucuk_plan():
    """Kucultulmus %95 sahnesi BIR KEZ cozulur -- butce 240 sn tavanli.

    Butceler CI icin secildi: GitHub'in ucretsiz makineleri 2 cekirdeklidir.
    Sure: K-59'dan once ~170 sn idi; K-59 (3 Ekim) birinci asamada butcenin
    %40'ina kadar (96 sn) iyilestirme yapar, dosyanin tamami Mustafa'nin
    makinesinde (6 cekirdek) 361 sn olctu (31 test). Tavan degismedi.
    """
    g = sahne_uret(0.1, 0.95)
    return g, coz(g, {"azami_saniye": 240, "durgunluk_saniye": 25})


def test_KUCULTULMUS_olcekte_plan_uretilir_ve_TEMIZ(kucuk_plan):
    """Uctan uca: plan uretilir, sert ihlal cikmaz, yayinlanabilir olur.

    ⚠ "Sert ihlal yok" burada COZUCU ILE DOGRULAYICININ ANLASTIGI anlamina
      gelir. 29 Eylul'de bu test iki kez kirmizi yandi ve ikisinde de
      hakliydi: once net saat tanimlari ayrisiyordu (T-57), sonra K-38
      yalniz cozucuye uygulanmisti.
    """
    g, c = kucuk_plan
    assert c["durum"] == "cozuldu", (
        "kucultulmus olcekte plan uretilemedi: %s / %r"
        % (c.get("durum"), (c.get("teshis") or {}).get("hucre")))

    r = degerlendir(g, c["atamalar"])
    sert = [i for i in r["ihlaller"] if i.get("agirlik") == "SERT"]
    assert not sert, (
        "planda %d sert ihlal var: %s"
        % (len(sert), sorted({i["kural"] for i in sert})))

    kapi = r.get("yayin_kapisi") or {}
    assert kapi.get("yayinlanabilir") is True, (
        "plan yayinlanabilir degil: %r" % kapi)


def test_DONMUS_gun_yeniden_planlamada_korunur(kucuk_plan):
    """K-54 (T-29): gun 0 donmus, yayinlanmis plan motorun kendi plani.

    Gercek is akisi: hafta yayinlandi, pazartesi gecti, sali plan yeniden
    kosturuluyor. Gun 0 OLAN OLDU -- aynen kalmali; kalan gunler ona uyarak
    planlanmali; sert ihlal cikmamali; yayinlanabilir olmali. Ilk plan temiz
    oldugu icin gecmise ait SERT ihlal de olmamali (yumusak olabilir).
    """
    import copy
    g, c = kucuk_plan
    assert c["durum"] == "cozuldu"
    g2 = copy.deepcopy(g)
    g2["donmus_gunler"] = [0]
    g2["mevcut_plan"] = copy.deepcopy(c["atamalar"])
    c2 = coz(g2, {"azami_saniye": 120, "durgunluk_saniye": 20})
    assert c2["durum"] == "cozuldu", (c2.get("durum"), c2.get("uygulanmayan_notlar"))
    ist = c2["cozum_istatistikleri"]
    assert ist["baslangic_plani_kullanildi"] is True, "yayinlanmis plan ipucu olmali"
    assert ist["donmus_gun"]["gunler"] == [0] and ist["donmus_gun"]["dusen_kisit"] > 0

    def gun0(atamalar):
        return sorted((a["calisan"], float(a["bas"]), float(a["bit"]), a.get("sablon"))
                      for a in atamalar if a["gun"] == 0)
    assert gun0(c2["atamalar"]) == gun0(c["atamalar"]), "donmus gun degisti"
    assert all(a.get("donmus") is True for a in c2["atamalar"] if a["gun"] == 0)
    assert not any(a.get("donmus") for a in c2["atamalar"] if a["gun"] != 0)

    r = degerlendir(g2, c2["atamalar"])
    sert = [i for i in r["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    assert not sert, sorted({i["kural"] for i in sert})
    assert r["metrikler"]["gecmis_sert_ihlal"] == 0, r["gecmis_ihlaller"][:3]
    assert not [i for i in r["ihlaller"] if i["kural"] == "DONMUS_GUN"]
    assert (r.get("yayin_kapisi") or {}).get("yayinlanabilir") is True, r.get("yayin_kapisi")


def test_KUCULTULMUS_olcekte_kapsama_TAM(kucuk_plan):
    """Asgari kapsama %100 olmali -- sert kural, tavizi yok.

    ⚠ OLCU MOTORUN DEGIL, DOGRULAYICININ -- 30 Eylul'de degistirildi (T-65)
      Bu test eskiden `c["metrikler"]`e, yani MOTORUN KENDI raporuna
      bakiyordu. Motorun kendi isini kendi onaylamasi #7.6'nin yasakladigi
      sey ve bedeli olculdu: CI'da "sert_ihlal 0, asgari kapsama %99,76"
      diye bir cift cikti. Celiski gibi duruyordu, degildi -- iki sayinin
      ikisi de ayni yaniltici rapordan geliyordu.

      Gercek sebep motorun metriginde `int()` ile kirpilan kesirli vardiya
      bitisiydi (07:00-16:15 -> saat 16 sayilmiyor). Plan dogruydu, sayi
      yanlisti. Komsu test (`test_TAM_ZAMANLI_sozlesme_saatini_DOLDURUYOR`)
      bu dersi zaten ogrenmisti ve dogrulayicinin olcusune bakiyordu;
      burada atlanmisti.

      Ayrica iki tarafin ANLASMASI da ayrica siniyor: ayrisirlarsa sapan
      taraf hangisi olursa olsun gorunur.
    """
    g, c = kucuk_plan
    assert c["durum"] == "cozuldu"
    r = degerlendir(g, c["atamalar"])
    denetci = (r.get("metrikler") or {}).get("asgari_kapsama_yuzde")
    assert denetci == 100.0, (
        "bagimsiz denetciye gore asgari kapsama %%100 degil: %s" % denetci)
    motor = (c.get("metrikler") or {}).get("asgari_kapsama_yuzde")
    assert motor == denetci, (
        "motor %%%s diyor, denetci %%%s -- iki taraf ayni plan hakkinda "
        "ayrisiyor (T-65 ailesi)" % (motor, denetci))


def test_TAM_ZAMANLI_sozlesme_saatini_DOLDURUYOR(kucuk_plan):
    """K-39'un uctan uca bekcisi -- ve T-51'in asil dersi.

    ⚠ Olculen sey planin saatleri DEGIL, iki tarafin anlasmasi: saatler
      DOGRULAYICININ olcusuyle (butun molalar dusuk) hesaplanir. Cozucunun
      kendi olcusuyle bakmak, kendi isini kendi onaylamak olurdu (#7.6).
    """
    g, c = kucuk_plan
    assert c["durum"] == "cozuldu"
    net = {}
    for a in c["atamalar"]:
        net[a["calisan"]] = net.get(a["calisan"], 0.0) + zaman.net_saat(a)
    from dogrulayici.kurallar import _borc_saat
    eksik = []
    for p in g["calisanlar"]:
        soz = p.get("sozlesme") or {}
        if soz.get("tip") != "tam_zamanli" or p.get("durum", "aktif") != "aktif":
            continue
        borc = _borc_saat(p)
        if borc > 0 and net.get(p["id"], 0.0) + 1e-6 < borc:
            eksik.append((p["id"], round(net.get(p["id"], 0.0), 2), round(borc, 2)))
    assert not eksik, (
        "%d tam zamanli sozlesme saatini doldurmadi (ilk bes: %s)"
        % (len(eksik), eksik[:5]))


# ----------------------------------------------------------------------
# 3 · IKI HAFTA -- bilerek BURADA DEGIL (30 Eylul)
# ----------------------------------------------------------------------
#
# Mustafa'nin onerisiyle (once bir hafta, sonra onu gecmis sayarak ikinci
# hafta) gercekci olcekte uc test yazildi ve ILK KOSUDA KIRMIZI yandi --
# kod yuzunden degil, ZAMANLAMA yuzunden:
#
#   * ayni ikinci hafta bir kosuda 144 sn, bir kosuda 178 sn surdu; bekci
#     kosusunda 240 sn'lik butceye SIGMADI. Cok iscili CP-SAT deterministik
#     degil ve hafta 1'in plani her kosuda farkli -> hafta 2'nin gecmisi de.
#   * bekcileri 5 dk 54 sn'den 9 dk 31 sn'ye cikardi; CI 2 cekirdekli ve
#     `motor` isinin siniri 20 dakika.
#
# "Butce asimindan gelen kirmizi, gercek hatadan gelen kirmiziya benzer."
# Bu yuzden ikiye ayrildi:
#   * GERCEKCI OLCEK -> elle: `py iki-hafta-olc.py`. 30 Eylul olcumu:
#       hafta 2 gecmissiz -> gecmisi bilen denetciye gore 27 SERT ihlal
#                            (10 hafta tatili, 7 dinlenme, 10 ardisik gun)
#       hafta 2 gecmisle  -> 0
#   * CI -> kucuk ve deterministik iki asamali test:
#       `09-motor/testler/test_gecmis_veri.py`, bolum 8
