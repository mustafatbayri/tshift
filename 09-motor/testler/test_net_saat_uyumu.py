# -*- coding: utf-8 -*-
"""
NET SAAT -- COZUCU ILE DOGRULAYICI AYNI SEYI ANLAMALI (T-57)

⚠ NE BULUNDU (29 Eylul, zor veri seti ilk kez cozulurken)
  Plan uretildi, bagimsiz dogrulayici 28 SERT `SAAT_DENGESI` ihlali yazdi.
  Sebep: iki taraf ayni kelimeye farkli anlam veriyordu.

      cozucu      _net_saat(sablon)      = brut - mola_dk
      dogrulayici zaman.net_saat(atama)  = brut - BUTUN molalar

  Cozucu yalniz UCRETSIZ yemegi dusuyordu; dogrulayici UCRETLI dinlenme
  molalarini da dusuyor. 8,5 saatlik bir vardiyada fark 0,75 saat; alti
  vardiyalik haftada 4,5 saat. Cozucu "45 saat oldu" derken dogrulayici
  "40,5" goruyordu.

HANGISI DOGRU -- DOGRULAYICI
  `dogrulayici/zaman.py` bu karari belgeliyor ve gerekcelendiriyor:

    "Bir molanin UCRETLI olmasi, o sirada is yapiliyor olmasi demek
     degildir. Ara dinlenme ucretli de olsa calisma suresinden dusulur;
     ucret tarafi AYRI bir buyuktur (`ucret_saat`)."

  ⚠ 25 Eylul'de bu satir bir kez YANLIS degistirilmis ve GERI ALINMIS.
    Yani karar bilincli; yanlis olan cozucu tarafiydi.

NEDEN BUGUNE KADAR GORUNMEDI
  Iki sey ayni gun degisti: `SAAT_DENGESI`'nin dogrulayici govdesi yazildi
  (K-39) ve veri seti ilk kez insanlari sozlesme saatine yaklastirdi.
  Ikisi olmadan bu ayrisma gorunmezdi -- #7.6'nin var olma sebebi tam
  olarak bu.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_net_saat_uyumu.py -v
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402
from cozucu.model import _net_saat                            # noqa: E402
from dogrulayici import degerlendir, zaman                    # noqa: E402

POLITIKA = [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]
# yemek 60 + 3x15 = 105 dk = 1,75 saat

KISA = {"id": "V-KISA", "ekip": "E", "bas": 8, "bit": 17.25, "mola_dk": 60,
        "mola_politikasi": POLITIKA}          # 9,25 brut -> 7,50 net
UZUN = {"id": "V-UZUN", "ekip": "E", "bas": 8, "bit": 18.75, "mola_dk": 60,
        "mola_politikasi": POLITIKA}          # 10,75 brut -> 9,00 net


def test_COZUCU_butun_molalari_duser():
    """⚠ En dogrudan kanit: iki tarafin ayni sayiyi uretmesi.

    Cozucu sablona, dogrulayici atamaya bakar; ama ikisi ayni vardiyayi
    anlatiyorsa ayni net saati vermelidir.
    """
    atama = {"calisan": "C1", "ekip": "E", "sablon": "V-KISA", "gun": 0,
             "bas": 8, "bit": 17.25,
             "molalar": [{"tip": "yemek", "bas": 12, "bit": 13,
                          "ucretli": False},
                         {"tip": "dinlenme", "bas": 10, "bit": 10.25,
                          "ucretli": True},
                         {"tip": "dinlenme", "bas": 14, "bit": 14.25,
                          "ucretli": True},
                         {"tip": "dinlenme", "bas": 16, "bit": 16.25,
                          "ucretli": True}]}
    assert abs(_net_saat(KISA) - zaman.net_saat(atama)) < 1e-6, (
        "cozucu %.2f saat diyor, dogrulayici %.2f saat"
        % (_net_saat(KISA), zaman.net_saat(atama)))


def test_net_saat_UCRETLI_molayi_da_duser():
    """9,25 brut - (60 + 3x15) dk = 7,50 net.

    Yanlis hesap 8,25 verirdi (yalniz yemek dusuk).
    """
    assert abs(_net_saat(KISA) - 7.5) < 1e-6, (
        "net saat %.2f -- ucretli dinlenme molalari dusulmemis" % _net_saat(KISA))


def _sahne():
    """Tam zamanli, 45 saat, 6 gunluk desen; iki sablon uzunlugu var.

    ⚠ SAHNE BILEREK BOYLE KURULDU
      Tek uzunluk olsaydi hatali hesap da tesadufen dogru sonuc verebilirdi.
      Iki uzunlukla cozucunun SECIMI degisiyor:

          yanlis hesap (8,25 / 9,75) -> 5 vardiya "yeter" saniliyor
                                        gercek: 4x9,0 + 7,5 = 43,5 < 45  IHLAL
          dogru hesap  (7,50 / 9,00) -> 5x9,0 = 45                        TAMAM
    """
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C1", "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45,
                          "gun_sayisi": 5},
             "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": [dict(KISA), dict(UZUN)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(5) for s in range(9, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 11}},
            {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True,
             "yasal": True, "parametreler": {"azami_saat": 45}},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "SAAT_DENGESI", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": True,
             "parametreler": {"tolerans_saat": 0}},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_UCTAN_UCA_iki_taraf_AYNI_plan_hakkinda_ANLASIR():
    """Asil sinav: cozucunun urettigi plani dogrulayici kabul etmeli.

    Bu test kirmiziyken 500 kisilik sahnede 28 sert ihlal cikiyordu --
    motor kendi olcusune gore dogru, denetciye gore yanlis bir plan
    uretiyordu.
    """
    g = _sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    sd = [i for i in r["ihlaller"] if i["kural"] == "SAAT_DENGESI"]
    sab = {t["id"]: t for t in g["vardiya_sablonlari"]}
    net = collections.Counter()
    for a in c["atamalar"]:
        net[a["calisan"]] += zaman.net_saat(a)
    assert not sd, (
        "cozucu 45 saat saniyor, dogrulayici %.2f saat goruyor: %r"
        % (net.get("C1", 0), [i.get("mesaj") for i in sd]))


# ----------------------------------------------------------------------
# T-78 (1 Ekim) -- CEYREGE SIGMAYAN MOLA: 20 dakika, iki tarafta iki olcu
# ----------------------------------------------------------------------
#
# ⚠ NE BULUNDU (30 Eylul gecesi, 500 kisi, %95, 1.200 sn)
#   Plan cozuldu, dogrulayici PART_TIME_LIMIT 1 ihlal yazdi; 900 saniyelik
#   kosu temizdi. Sebep sablonlarin bir kismindaki 3x20 dk dinlenme molasi:
#
#     cozucu   20 dk = round(1,33) = 1 CEYREK  (pencere arasi ve cakisma)
#     gercek   20 dk = 20 dk                   (dogrulayici gercek aralik)
#
#   08-17 vardiyasinda ikinci molanin son adayi 13:30 (13:50'de biter),
#   ucuncunun ilk adayi 13:45; 10:45'teki dinlenme (11:05'te biter) ile
#   11:00'deki yemek de cakismiyor "gorunuyordu". Dogrulayici ustuste binen
#   molayi TEK aralik sayar: calisma 5 dk fazla cikar. Tam 45,00 saatte
#   duran yari zamanli icin bu tek basina sert ihlal (tolerans 0).
#
#   Ikinci yuz: `_mola_dilimleri` 20 dk'lik molayi tek ceyrek kapali
#   sayiyordu; dogrulayici sahayi ceyrek anlarinda orneklerken 13:45 ve
#   14:00'da kisiyi yok sayar. SAHADA_ASGARI sert; ayni aile.
#
# Asagidaki testler PLAN KOSTURMAZ: cozucunun BIRLIKTE secmesine izin
# verdigi her mola cifti gercek zamanda ayrik olmali ve her molanin dilim
# kumesi dogrulayicinin orneklemesiyle birebir olmali. Bu, "cozucunun
# urettigi hicbir yerlesimde net saat ayrismaz" onermesinin kendisidir;
# CP-SAT'in o yerlesimi secmesini beklemek gerekmez.

from cozucu.model import (_mola_baslangiclari, _dinlenme_baslangiclari,   # noqa: E402
                          _mola_dilimleri, _gercek_kesisiyor, _q,
                          _ceyrek_yukari)

YIRMI_DK = [{"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 20, "adet": 3, "ucretli": True}]
M_SABAH = {"id": "M-SABAH", "ekip": "E", "bas": 8, "bit": 17, "mola_dk": 30,
           "mola_politikasi": YIRMI_DK}      # 9 brut -> 7,50 net; 6 gun = 45,00


def _adaylar(t, yemek_dk, adet, dk, pencere=(3, 5)):
    yemekler = [s for s in _mola_baslangiclari(t, pencere, yemek_dk)
                if s is not None]
    dinl = [a for a in (_dinlenme_baslangiclari(t, adet, dk) if adet else [])
            if a]
    return yemekler, dinl


def _birlikte_secilebilen_ciftler(t, yemek_dk, adet, dk):
    """Cozucunun aralarina kisit YAZMADIGI mola ciftleri -- model.py'deki
    `_dinlenme_degiskenleri` ile ayni kural: yemek-dinlenme ve ARDISIK
    dinlenmeler arasinda yalniz gercek kesisimde kisit var; ardisik
    olmayan dinlenmeler arasinda hic kisit yok."""
    yemekler, dinl = _adaylar(t, yemek_dk, adet, dk)
    sure, ysure = dk / 60.0, yemek_dk / 60.0
    for sy in yemekler:
        for adaylar in dinl:
            for s in adaylar:
                if not _gercek_kesisiyor(s, sure, sy, ysure):
                    yield (sy, ysure), (s, sure)
    for i in range(len(dinl)):
        for j in range(i + 1, len(dinl)):
            for s1 in dinl[i]:
                for s2 in dinl[j]:
                    if j == i + 1 and _gercek_kesisiyor(s1, sure, s2, sure):
                        continue
                    yield (s1, sure), (s2, sure)


def _tam_yerlesim_var_mi(t, yemek_dk, adet, dk):
    """Kisitlar altinda EN AZ BIR tam yerlesim (yemek + butun dinlenmeler)
    kaliyor mu? Kalmiyorsa sablon sessizce atanamaz olur -- bu bir
    daraltma olurdu ve acikca gorulmeli (calisma kurali 7)."""
    yemekler, dinl = _adaylar(t, yemek_dk, adet, dk)
    if not yemekler and yemek_dk:
        return False
    sure, ysure = dk / 60.0, yemek_dk / 60.0
    for sy in (yemekler or [None]):
        secim = []

        def geri(i):
            if i == len(dinl):
                return True
            for s in dinl[i]:
                if sy is not None and _gercek_kesisiyor(s, sure, sy, ysure):
                    continue
                if secim and _gercek_kesisiyor(secim[-1], sure, s, sure):
                    continue
                secim.append(s)
                if geri(i + 1):
                    return True
                secim.pop()
            return False

        if geri(0):
            return True
    return False


def _uyumsuzluklar(t, yemek_dk, adet, dk):
    hata = []
    if not _tam_yerlesim_var_mi(t, yemek_dk, adet, dk):
        # Politika bu vardiyaya sigmiyor: kabul, AMA sessiz olamaz -- model
        # nota yazmali (asagidaki SIGMAYAN testi). Kisa vardiyaya uzun
        # politika (3 saate 60 dk yemek + 3x20) gercekte de sigmaz.
        if (yemek_dk + adet * dk) / 60.0 <= 0.3 * (t["bit"] - t["bas"]):
            hata.append(("tam_yerlesim_yok_makul_politikada",))
    for (b1, d1), (b2, d2) in _birlikte_secilebilen_ciftler(t, yemek_dk, adet, dk):
        if _gercek_kesisiyor(b1, d1, b2, d2):
            hata.append(("ustuste", b1, d1, b2, d2))
        q1 = set(_mola_dilimleri(0, t, b1, int(round(d1 * 60))))
        q2 = set(_mola_dilimleri(0, t, b2, int(round(d2 * 60))))
        if q1 & q2:
            hata.append(("ayni_dilim", b1, d1, b2, d2))
    yemekler, dinl = _adaylar(t, yemek_dk, adet, dk)
    for s, dkk in ([(s, yemek_dk) for s in yemekler]
                   + [(s, dk) for a in dinl for s in a]):
        if s < t["bas"] - 1e-9 or s + dkk / 60.0 > t["bit"] + 1e-9:
            hata.append(("sigmadi", s, dkk))
        a = {"gun": 0, "bas": t["bas"], "bit": t["bit"],
             "molalar": [{"bas": s, "bit": s + dkk / 60.0, "tip": "dinlenme"}]}
        beklenen = {q for q in range(_q(0, t["bas"]), _q(0, t["bit"]))
                    if not zaman.sahada_mi(a, 0, q / 4.0)}
        if set(_mola_dilimleri(0, t, s, dkk)) != beklenen:
            hata.append(("dilim_ornekleme", s, dkk))
    return hata


def test_T78_YIRMI_dakikalik_mola_IKI_ceyrek_kaplar():
    """13:45-14:05 molasindaki kisi 13:45'te de 14:00'da da sahada degil."""
    assert _ceyrek_yukari(20 / 60.0) == 2
    assert _ceyrek_yukari(15 / 60.0) == 1
    assert _ceyrek_yukari(60 / 60.0) == 4
    assert _mola_dilimleri(0, M_SABAH, 13.75, 20) == [_q(0, 13.75), _q(0, 14.0)]


def test_T78_M_SABAH_yerlesimleri_GERCEK_zamanda_ayrik():
    """Tam olcekte bulunan sablon: 08-17, 30 dk yemek, 3x20 dk dinlenme.
    Eski pencere aritmetigiyle 13:30 ve 13:45 adaylari birlikte
    secilebiliyordu (5 dk ustuste)."""
    hata = _uyumsuzluklar(M_SABAH, 30, 3, 20)
    assert not hata, hata[:5]


def test_T78_tarama_uzunluk_ve_politika():
    """3-12 saat arasi ceyrek adimla her uzunluk x yemek {0,30,45,60} x
    dinlenme {1..4} x {5,10,15,20,30} dk: cozucunun birlikte secebildigi
    hicbir mola cifti gercek zamanda ustuste binmez, hicbiri vardiyadan
    tasmaz, her molanin dilim kumesi dogrulayicinin ceyrek orneklemesiyle
    birebir."""
    kotu = []
    for uz4 in range(12, 49, 3):
        uz = uz4 / 4.0
        for yemek_dk in (0, 30, 45, 60):
            for adet in (1, 2, 3, 4):
                for dk in (5, 10, 15, 20, 30):
                    pol = ([{"tip": "yemek", "dakika": yemek_dk, "adet": 1}]
                           if yemek_dk else []) + \
                          [{"tip": "dinlenme", "dakika": dk, "adet": adet,
                            "ucretli": True}]
                    t = {"id": "T", "bas": 8.0, "bit": 8.0 + uz,
                         "mola_dk": yemek_dk, "mola_politikasi": pol}
                    h = _uyumsuzluklar(t, yemek_dk, adet, dk)
                    if h:
                        kotu.append((uz, yemek_dk, adet, dk, h[:2]))
    assert not kotu, kotu[:10]


def _yirmi_dk_sahne():
    """Bir yari zamanli, 6 gun M-SABAH: cozucu hesabiyla tam 45,00 saat --
    tavanin ustunde sifir pay. Ustuste binen tek bir mola bile plani
    yayinlanamaz yapar."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "P1", "ekipler": ["E"], "sozlesme": {"tip": "yari_zamanli"},
             "izinler": [], "uygunluk": []}],
        "vardiya_sablonlari": [dict(M_SABAH)],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 1}
                  for d in range(6) for s in range(8, 17)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True, "yasal": False},
            {"kod": "MOLA_KAPSAMASI", "tur": "YUMUSAK", "aktif": True, "yasal": False},
            {"kod": "HAFTA_TATILI", "tur": "SERT", "aktif": True, "yasal": True},
            {"kod": "GUNLUK_AZAMI", "tur": "SERT", "aktif": True, "yasal": True,
             "parametreler": {"azami_saat": 11}},
            {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True,
             "yasal": True, "parametreler": {"azami_saat": 45}},
            {"kod": "PART_TIME_LIMIT", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "MOLA_HAKKI", "tur": "SERT", "aktif": True, "yasal": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def test_T78_UCTAN_UCA_45_saatteki_yari_zamanli_yayinlanabilir():
    """Cozucu 6 x 7,50 = 45,00 diyor; dogrulayici da 45,00 gormeli.
    Molalar ustuste binerse 45,08 gorur ve PART_TIME_LIMIT yazar."""
    g = _yirmi_dk_sahne()
    c = coz(g, {"azami_saniye": 30, "durgunluk_saniye": 10})
    assert c["durum"] == "cozuldu", c["durum"]
    r = degerlendir(g, c["atamalar"])
    pt = [i for i in r["ihlaller"] if i["kural"] == "PART_TIME_LIMIT"]
    net = sum(zaman.net_saat(a) for a in c["atamalar"])
    assert abs(net - 45.0) < 1e-6 and not pt, (
        "dogrulayici %.3f saat goruyor: %r" % (net, [i.get("mesaj") for i in pt]))
    for a in c["atamalar"]:
        mol = a.get("molalar") or []
        yazilan = sum(m["bit"] - m["bas"] for m in mol)
        # Ucu uca degen iki mola dogrulayicida tek aralik olur ama sure
        # toplami degismez; ustuste binen molada toplam DUSER.
        assert abs(zaman.mola_saat(a) - yazilan) < 1e-6, (
            "gun %d: %.3f saat mola yazildi, dogrulayici %.3f saat goruyor "
            "(ustuste binme): %r" % (a["gun"], yazilan, zaman.mola_saat(a), mol))


def test_T78_pencereler_gercek_sureyle_AYRILIR():
    """`_dinlenme_baslangiclari`nin sozu: pencereler birbirine DEGMEZ.
    Olcu artik molanin GERCEK suresi (yukari yuvarlanmis ceyrek), round
    degil: bir pencerenin son adayi + sure, sonrakinin ilk adayini
    gecemez. 08-17 / 3x20 dk'da eski hesap 13:30 ile 13:45'i veriyordu."""
    for adet in (1, 2, 3, 4):
        for dk in (5, 10, 15, 20, 30):
            for uz4 in range(12, 49, 2):
                t = {"id": "T", "bas": 8.0, "bit": 8.0 + uz4 / 4.0}
                pencereler = [a for a in _dinlenme_baslangiclari(t, adet, dk) if a]
                for a, b in zip(pencereler, pencereler[1:]):
                    assert max(a) + dk / 60.0 <= min(b) + 1e-9, (
                        "uzunluk %.2f, %dx%d dk: %s ile %s ustuste"
                        % (uz4 / 4.0, adet, dk, max(a), min(b)))


def test_T78_ucu_uca_degen_mola_KESISMEZ():
    """12:00-12:30 yemek ile 12:30-12:50 dinlenme birlikte secilebilir;
    kesisim saymak cozucunun secenegini bosuna daraltirdi."""
    assert not _gercek_kesisiyor(12.0, 0.5, 12.5, 20 / 60.0)
    assert not _gercek_kesisiyor(12.5, 20 / 60.0, 12.0, 0.5)
    assert _gercek_kesisiyor(12.0, 0.5, 12.25, 20 / 60.0)
    assert _gercek_kesisiyor(10.75, 20 / 60.0, 11.0, 0.5)     # 5 dk ustuste


def test_T78_EMNIYET_KEMERI_pencere_aritmetigi_yanilsa_da_tutar(monkeypatch):
    """Pencere aritmetigi bir gun yine ustuste binen adaylar uretirse
    (T-78'de uretti), ardisik dinlenmeler arasindaki kisit onu yakalar.

    Adaylar elle bozuluyor: birinci mola YALNIZ 10:15, ikincisi YALNIZ
    10:30 -- 20 dakikalik iki mola 5 dk ustuste. Kemer varsa bu sablona
    atama YAPILAMAZ (plan cozumsuz); kemer yoksa plan cozulur ve
    dogrulayici molalari ustuste gorur."""
    from cozucu import model as MODEL
    monkeypatch.setattr(MODEL.Model, "_dinlenme_adaylari",
                        lambda self, sablon: [[10.25], [10.5]])
    t = {"id": "T", "ekip": "E", "bas": 8, "bit": 12, "mola_dk": 0,
         "mola_politikasi": [{"tip": "dinlenme", "dakika": 20, "adet": 2,
                              "ucretli": True}]}
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": "C1", "ekipler": ["E"],
                         "sozlesme": {"tip": "tam_zamanli"},
                         "izinler": [], "uygunluk": []}],
         "vardiya_sablonlari": [t],
         "talep": [{"ekip": "E", "gun": 0, "saat": 9, "asgari": 1, "hedef": 1}],
         "kurallar": [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                       "yasal": False}],
         "kilitler": [], "donmus_gunler": []}
    c = coz(g, {"azami_saniye": 10, "durgunluk_saniye": 5})
    if c["durum"] == "cozuldu":
        for a in c["atamalar"]:
            mol = a.get("molalar") or []
            yazilan = sum(m["bit"] - m["bas"] for m in mol)
            assert abs(zaman.mola_saat(a) - yazilan) < 1e-6, (
                "kemer yok: molalar ustuste yazildi %r" % mol)
        raise AssertionError("ustuste binen tek secenekle plan cozulmemeliydi")
    assert c["durum"] == "cozumsuz", c["durum"]


def test_T78_yemek_ile_dinlenme_GERCEK_zamanda_cakisamaz(monkeypatch):
    """Yemek tek secenek 11:00-11:30 (MOLA_YERLESIMI 3-3), dinlenme tek
    secenek 10:45-11:05: 5 dk ustuste. Kisit gercek zamana bakiyorsa bu
    sablona atama yapilamaz; ceyrek kumesine baksaydi (eski) 10:45 dilimi
    ile 11:00 dilimi ayri gorunur, plan cozulur ve dogrulayici 5 dk fazla
    calisma gorurdu."""
    from cozucu import model as MODEL
    monkeypatch.setattr(MODEL.Model, "_dinlenme_adaylari",
                        lambda self, sablon: [[10.75]])
    t = {"id": "T", "ekip": "E", "bas": 8, "bit": 12, "mola_dk": 30,
         "mola_politikasi": [{"tip": "yemek", "dakika": 30, "adet": 1},
                             {"tip": "dinlenme", "dakika": 20, "adet": 1,
                              "ucretli": True}]}
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": "C1", "ekipler": ["E"],
                         "sozlesme": {"tip": "tam_zamanli"},
                         "izinler": [], "uygunluk": []}],
         "vardiya_sablonlari": [t],
         "talep": [{"ekip": "E", "gun": 0, "saat": 9, "asgari": 1, "hedef": 1}],
         "kurallar": [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                       "yasal": False},
                      {"kod": "MOLA_YERLESIMI", "tur": "YUMUSAK", "aktif": True,
                       "yasal": False,
                       "parametreler": {"en_az_saat": 3, "en_gec_saat": 3}}],
         "kilitler": [], "donmus_gunler": []}
    c = coz(g, {"azami_saniye": 10, "durgunluk_saniye": 5})
    if c["durum"] == "cozuldu":
        mol = c["atamalar"][0].get("molalar") or []
        raise AssertionError("ustuste binen tek secenekle plan cozulmemeliydi: %r"
                             % mol)
    assert c["durum"] == "cozumsuz", c["durum"]


def test_T78_SIGMAYAN_politika_sessiz_kalmaz():
    """4 saatlik vardiyaya 60 dk yemek + 4x20 dk dinlenme ustuste binmeden
    yerlesemiyor. Eskiden molalar ustuste bindirilip 'sigiyordu' (gecersiz
    plan); simdi sablona atama yapilamaz -- ve bu NOTA yazilir, cozumsuzluk
    sessiz kalmaz."""
    from cozucu.model import Model
    t = {"id": "T-KISA", "ekip": "E", "bas": 8, "bit": 12, "mola_dk": 60,
         "mola_politikasi": [{"tip": "yemek", "dakika": 60, "adet": 1},
                             {"tip": "dinlenme", "dakika": 20, "adet": 4,
                              "ucretli": True}]}
    g = {"profil": "DENGELI",
         "calisanlar": [{"id": "C1", "ekipler": ["E"],
                         "sozlesme": {"tip": "tam_zamanli"},
                         "izinler": [], "uygunluk": []}],
         "vardiya_sablonlari": [t, dict(M_SABAH)],
         "talep": [], "kurallar": [], "kilitler": [], "donmus_gunler": []}
    m = Model(g).kur()
    ilgili = [n for n in m.notlar if "SIGMIYOR" in n]
    assert len(ilgili) == 1 and "T-KISA" in ilgili[0], m.notlar
    assert not any("M-SABAH" in n for n in ilgili)
