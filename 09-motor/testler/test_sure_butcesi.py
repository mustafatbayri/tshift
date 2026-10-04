# -*- coding: utf-8 -*-
"""
SURE BUTCESI -- birinci asama butcenin ICINDEN pay alir (T-59)

NE VARDI (29 Eylul, Mustafa'nin makinesinde, 500 kisilik tam olcek)
  900 saniye istenen kosu 1078 saniye surdu. Birinci asamanin suresi
  (`ilk_asama_saniye`, 120 sn) verilen butcenin USTUNE ekleniyordu:

      _ipucu_ver  -> max_time = ilk_asama_saniye   (120)
      ana cozum   -> max_time = azami_saniye       (900)

  900 + 120 + model kurma 51 ~ 1071 -- olculen 1078 ile tutuyor.
  K-35 kullaniciya sure SECTIRIYOR (10/15/30 dk); "15 dakika" diyen
  yonetici 18 dakika bekliyordu. Vaat edilen sureden uzun suren bir sure
  vaadi vaat degildir.

NE OLDU (30 Eylul aksami)
  * birinci asamanin payi: min(ilk_asama_saniye, azami_saniye x %20)
  * ana cozume KALAN verilir: azami_saniye - birinci asamada gecen
  * iki asamanin toplami azami_saniye'yi GECMEZ
  * model kurma suresi AYRI kalem olarak cikar (`model_kurma_sn`) --
    kullaniciya ayrica gosterilebilsin (T-59'un onerisi)

K-59 (3 Ekim): birinci asama artik IKI arama -- gecerli plan (pay %20) ve
  molalar sabitken amacli iyilestirme (pay `ilk_asama_iyilestirme_orani`;
  K-59'da %40, K-60 ile %80). Ikisinin toplami `ilk_asama_sn`e yazilir; ana
  asamaya (K-60: mola adimi) yine KALAN verilir, soz degismez: birinci
  asamada GECEN + ana asamaya VERILEN <= azami.

⚠ BU TESTLER SAAT OLCMEZ -- bilerek. CI makinesi paylasimli ve 2
  cekirdekli; "5 saniyeden kisa surdu" diyen bir test yuk altinda rastgele
  kirmizi yanar (bkz. iki haftalik testin CI'dan cikarilmasi, 30 Eylul).
  Sinanan sey BUTCENIN BOLUNUSU: cikti hangi payi verdigini yaziyor ve
  bu paylar aritmetik olarak dogru mu. Birinci asama yapay olarak
  yavaslatilir (uyku), yani "gecen sure" belirlidir.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib                                              # noqa: E402

# `cozucu/__init__.py` `coz` FONKSIYONUNU disari veriyor; `import
# cozucu.coz as C` modulu degil o fonksiyonu getirir. Modulun kendisi:
C = importlib.import_module("cozucu.coz")


def _sahne(kisi=6):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)],
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60, "gece_vardiyasi": False}
            for j, b in enumerate((7, 11))],
        "talep": [{"ekip": "E", "gun": d, "saat": s, "asgari": 1, "hedef": 2}
                  for d in range(7) for s in (8, 12, 16)],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True}],
        "kilitler": [], "donmus_gunler": [],
    }


def test_birinci_asamanin_payi_BUTCENIN_ICINDEN():
    pay = C._ilk_asama_payi
    assert pay({"azami_saniye": 900, "ilk_asama_saniye": 120}) == 120
    assert pay({"azami_saniye": 240, "ilk_asama_saniye": 120}) == 48
    assert pay({"azami_saniye": 60, "ilk_asama_saniye": 25}) == 12
    assert pay({"azami_saniye": 900, "ilk_asama_saniye": 5}) == 5


def test_ana_cozume_KALAN_verilir(monkeypatch):
    """Birinci asama 2 saniye surerse ana cozume 5 - 2 = 3 saniye kalir.

    Eskiden ana cozum her durumda azami_saniye'nin TAMAMINI aliyordu.
    """
    def yavas_ipucu(kuruldu, ayar):
        time.sleep(2.0)
        return False

    monkeypatch.setattr(C, "_ipucu_ver", yavas_ipucu)
    c = C.coz(_sahne(), {"azami_saniye": 5, "iki_asama_esigi": 0,
                        "durgunluk_saniye": 0})
    ist = c["cozum_istatistikleri"]
    assert ist.get("ilk_asama_sn") is not None, (
        "birinci asamanin suresi ciktida yok -- butce bolunmuyor (T-59)")
    assert ist["ilk_asama_sn"] >= 2.0, ist
    assert ist["ana_asama_butce_sn"] <= 5 - ist["ilk_asama_sn"] + 1e-6, ist


def test_birinci_asama_butceyi_YIYEMEZ(monkeypatch):
    """Birinci asama butcenin tamamini tuketse bile ana cozume en az 1 sn
    kalir -- sifir sure CP-SAT'e 'hic arama' demek olurdu."""
    def yavas_ipucu(kuruldu, ayar):
        time.sleep(1.5)
        return False

    monkeypatch.setattr(C, "_ipucu_ver", yavas_ipucu)
    c = C.coz(_sahne(), {"azami_saniye": 1, "iki_asama_esigi": 0,
                        "durgunluk_saniye": 0})
    assert c["cozum_istatistikleri"]["ana_asama_butce_sn"] >= 1.0


def test_ipucu_aramasi_KENDI_payiyla_sinirli(monkeypatch):
    """Birinci asamanin iki aramasina giden CP-SAT butceleri paylarini asmamali.

    K-59'dan once iki arama vardi (ipucu + ana); 3 Ekim'den beri uc:
    ipucu (%20), molalar sabitken iyilestirme (K-60 ile %80), ana asama =
    mola adimi (kalan)."""
    gorulen = []
    asil = C.cp_model.CpSolver

    class Kayitci(asil):
        def Solve(self, model, *a, **k):
            gorulen.append(self.parameters.max_time_in_seconds)
            return asil.Solve(self, model, *a, **k)

    monkeypatch.setattr(C.cp_model, "CpSolver", Kayitci)
    c = C.coz(_sahne(), {"azami_saniye": 10, "ilk_asama_saniye": 120,
                         "iki_asama_esigi": 0, "durgunluk_saniye": 0})
    assert len(gorulen) == 3, gorulen
    assert gorulen[0] <= 2.0 + 1e-6, (
        "gecerli plan aramasi %s sn aldi; pay en cok 10 x %%20 = 2 sn" % gorulen[0])
    assert gorulen[1] <= 8.0 + 1e-6, (
        "K-59 iyilestirmesi %s sn aldi; pay en cok 10 x %%80 = 8 sn (K-60)" % gorulen[1])
    # Butceler TOPLANMAZ: birinci asama paylarinin tamamini kullanmayabilir.
    # Soz su: birinci asamada GECEN + ana asamaya VERILEN <= azami.
    ist = c["cozum_istatistikleri"]
    assert abs(gorulen[2] - ist["ana_asama_butce_sn"]) < 0.01, (gorulen, ist)
    assert ist["ilk_asama_sn"] + gorulen[2] <= 10 + 0.01, (gorulen, ist)
    assert ist["ilk_asama_iyilestirme"]["istenen_saniye"] == 8.0, ist["ilk_asama_iyilestirme"]


def test_model_kurma_suresi_AYRI_kalem():
    c = C.coz(_sahne(), {"azami_saniye": 5})
    ist = c["cozum_istatistikleri"]
    assert ist.get("model_kurma_sn") is not None, ist
    assert ist["model_kurma_sn"] >= 0


def test_butce_dolunca_DURMA_SEBEBI_dogru(monkeypatch):
    """Ana asama kendi payini doldurunca sebep 'butce_doldu' olmali.

    Eski kiyas `sure >= azami_saniye x 0,95` idi; ana asamanin payi artik
    azami'den kucuk oldugu icin o kiyas hic tutmazdi ve sebep 'bilinmiyor'
    yazilirdi."""
    assert C._durma_sebebi(None, None, {"azami_saniye": 10}, 7.9, 8.0) \
        == "butce_doldu"
    assert C._durma_sebebi(None, None, {"azami_saniye": 10}, 3.0, 8.0) \
        == "bilinmiyor"


def test_ana_asamada_ILK_PLANIN_ani_yazilir():
    """T-60 (1 Ekim): tam olcekte birinci asama 120 saniyede plan bulamiyor,
    ana asama buluyor -- ama kacinci saniyede bulundugu hicbir yerde
    yazmiyordu. Sayi ana asamanin baslangicindan olculur ve cozum
    suresini asamaz; plan yoksa None."""
    c = C.coz(_sahne(), {"azami_saniye": 10, "durgunluk_saniye": 3})
    ist = c["cozum_istatistikleri"]
    assert c["durum"] == "cozuldu", c["durum"]
    assert ist.get("ilk_cozum_sn") is not None, ist
    assert 0 <= ist["ilk_cozum_sn"] <= ist["cozum_suresi_sn"] + 0.05, ist
