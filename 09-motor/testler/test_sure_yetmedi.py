# -*- coding: utf-8 -*-
"""
"IMKANSIZ" ILE "YETISTIREMEDIM" AYRI SEYLERDIR

⚠ NEDEN (Mustafa, 29 Eylul)
  Cozucu iki bambaska sebeple plansiz donebilir:

    INFEASIBLE : KANITLADI -- bu kurallarla, bu kadroyla boyle bir plan yok
    UNKNOWN    : SURE DOLDU -- arıyordu, yetistiremedi

  Ikisi de `durum: "cozumsuz"` diye cikiyordu. Ustelik ikisinde de motor
  TESHIS koyuyordu: her sert kurali tek tek gevsetip yeniden cozerek
  "engelleyen kural" ariyordu.

  Bunun iki ayri bedeli olculdu (29 Eylul, 35 kisilik sahne):

    1. YANLIS OLABILECEK CUMLE
       Teshis "su hucreyi su kural engelliyor" diyor. Ama hicbir sey
       kanitlanmadi. Bir yoneticiye "bu talebi bu kadroyla karsilamak
       imkansiz" demek, personel alimina kadar giden bir karardir.

    2. USTELIK BEDAVA DEGIL
       45 saniyelik butce -> satir TOPLAM 470 saniye surdu. Kullanici
       butcesini bekledikten sonra 7 dakika daha bekliyor, sonunda
       muhtemelen yanlis bir cumle aliyor.

BU DOSYA NE SINAR
  * kanitlanmis cozumsuzluk hala `cozumsuz` ve teshisi var
  * butce dolunca `sure_yetmedi` ve teshis KOSMUYOR
  * kullanici ISTERSE teshis kosuyor ("neden oldugunu arastir")
  * istenerek kosan teshis KESIN DEGIL diye isaretleniyor

⚠ 1 EKIM: "BUTCE DOLDU" ARTIK YARISLA DEGIL, ENJEKSIYONLA KURULUYOR
  Dort test "60 kisilik sahne + 0.1 sn butce" ile butcenin dolmasini
  bekliyordu. Iki sey bunu bir YARISA ceviriyordu:
    1. `coz` ana aramaya en az 1 saniye verir (T-59 tabani: sifir sure
       CP-SAT'e "hic arama" demek olurdu) -- 0.1 yazan test aslinda 1 sn
       aliyordu.
    2. Bu sahnede ilk plan 2 cekirdekli konteynerde 1,9 saniyede geliyor;
       GitHub'in makinesi 1 Ekim'de 1 saniyenin altinda buldu ve dort test
       orada kirmizi yandi ("cozuldu" bekleniyordu "sure_yetmedi").
  Motorda hata yok; test makine hizina bagliydi -- bu dosyanin kendi
  uyarisinin ("sure olcerek degil YAPIYI sinayarak") tam tersi. Simdi
  `sure_dolmus` fikstur'u CP-SAT'e aramadan UNKNOWN dedirtiyor: "sure
  doldu, plan bulamadim, yoklugunu da kanitlayamadim". Sinanan sey
  mekanizmanin kendisi; hangi makinede kostugu fark etmez.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_sure_yetmedi.py -v
"""

import os
import sys

import pytest
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz                                    # noqa: E402


@pytest.fixture
def sure_dolmus(monkeypatch):
    """CP-SAT'e aramadan UNKNOWN dedirtir: sure dolmus, plan yok, kanit yok.

    Gercek CP-SAT butce dolunca tam olarak bunu dondurur (UNKNOWN); fark,
    burada bunun makine hizina bakmadan HER zaman olmasi. `coz` bu duruma
    ne yapiyor -- sinanan o. Kanitlanmis cozumsuzluk testleri bu fikstur'u
    KULLANMAZ: orada gercek cozucu INFEASIBLE kanitini kendi uretir.
    """
    def aramadan_bilmiyorum(self, model, solution_callback=None):
        return cp_model.UNKNOWN

    monkeypatch.setattr(cp_model.CpSolver, "Solve", aramadan_bilmiyorum)


def _kurallar():
    return [
        {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
         "kabul_edilebilir": False}
        for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                  "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
    ] + [
        {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
         "parametreler": {"esik": 2}},
    ]


def _sahne(kisi, gun=7, asgari=3, hedef=6, saatler=(7, 23)):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%03d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, kisi + 1)
        ],
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60,
             # ⚠ 30 Eylul aksami (T-69): gece isareti ACIKCA yazildi -- 20:00'yi
             #   asan sablon gece. Eski tahmin ("pencereye en ufak degme") bunu
             #   kendiliginden yapiyordu; yeni tahmin (md. 7/2, "yarisindan
             #   cogu") yapmiyor. Isaretsiz birakilsaydi ADALET_DENGESI'nin
             #   gece terimleri kaybolur, sahne sessizce degisirdi.
             "gece_vardiyasi": b + 8 > 20,
             "mola_politikasi": [
                 {"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
                 {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]}
            for j, b in enumerate((7, 9, 11, 13, 15))
        ],
        "talep": [{"ekip": "E", "gun": d, "saat": s,
                   "asgari": asgari, "hedef": hedef}
                  for d in range(gun) for s in range(*saatler)],
        "kurallar": _kurallar(),
        "kilitler": [], "donmus_gunler": [],
    }


def _imkansiz():
    """KANITLANABILIR cozumsuzluk: tek kisi, her saat 9 kisi isteniyor.

    Cozucu bunu saniyeler icinde KANITLAR -- "yetistiremedim" degil.
    """
    g = _sahne(1, gun=1, saatler=(9, 17))
    g["talep"] = [{"ekip": "E", "gun": 0, "saat": s, "asgari": 9, "hedef": 9}
                  for s in range(9, 17)]
    return g


def _yetismez():
    """Cozulebilir sahne; butcenin dolmasi `sure_dolmus` fikstur'uyle kurulur.

    ⚠ 1 Ekim'e kadar "60 kisi + 0.1 sn" ile cozucunun yetisememesi
      BEKLENIYORDU; bu makine hizina bagli bir yaristi (dosya basindaki
      not). Sahne ayni kaldi -- model gercekten kuruluyor, on kontrol
      gercekten kosuyor -- yalniz aramanin sonucu artik enjekte ediliyor.

    ⚠ Iki asama bilerek KAPALI: acik kalsaydi birinci asama kendi
      butcesini (varsayilan 120 sn) harcar ve test dakikalarca surerdi.
    """
    return _sahne(60, gun=7)


KISA = {"azami_saniye": 0.1, "durgunluk_saniye": 0,
        "iki_asama_esigi": 10 ** 9}


def test_KANITLANMIS_cozumsuzluk_hala_cozumsuz():
    """Kanit varsa cevap degismemeli -- bu degisiklik onu bozmamali."""
    c = coz(_imkansiz(), {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz", c["durum"]
    assert c.get("teshis"), "kanitlanmis cozumsuzlukte teshis olmali"


def test_BUTCE_dolunca_SURE_YETMEDI_der(sure_dolmus):
    """Plan bulunamadiysa ama kanitlanmadiysa, adi baska olmali."""
    c = coz(_yetismez(), KISA)
    assert c["durum"] == "sure_yetmedi", (
        "butce dolunca 'sure_yetmedi' beklenirdi: %r" % c["durum"])


def test_sure_yetmedigi_zaman_TESHIS_KOSMAZ(sure_dolmus):
    """Asil kazanc bu: cevapsiz soruya 7 dakika harcanmasin.

    ⚠ Sure olcerek degil YAPIYI sinayarak: zamana bagli test yavas bir
      makinede ilgisiz bir sebeple kirmizi yanar.
    """
    c = coz(_yetismez(), KISA)
    assert c["durum"] == "sure_yetmedi"
    t = c.get("teshis") or {}
    assert not t.get("engelleyen_kurallar"), (
        "sure yetmedigi halde kural gevsetme turu kosmus: %r" % t)
    assert not c.get("en_iyi_plan"), (
        "sure yetmedigi halde en iyi plan aranmis: %r" % c.get("en_iyi_plan"))


def test_sure_yetmedi_NE_YAPILACAGINI_soyler(sure_dolmus):
    """Kullanici ekranda ne gorecegini bilmeli: sure uzatilabilir."""
    c = coz(_yetismez(), KISA)
    assert c.get("verilen_saniye"), (
        "kac saniye verildigi bildirilmiyor: %r" % sorted(c))
    assert c.get("teshis_istenebilir") is True, (
        "'neden oldugunu arastir' secenegi bildirilmiyor: %r" % sorted(c))


def test_ISTENIRSE_teshis_kosar_ama_KESIN_DEGIL_der(sure_dolmus):
    """"Neden oldugunu arastir" dugmesi: teshis kullanici isterse kosar.

    ⚠ Kosan teshis yine de KANIT DEGILDIR -- ciktida boyle isaretlenir.
      Aksi halde ayni yanlis cumleyi bu kez dugme arkasindan soylerdik.
    """
    ayar = dict(KISA, teshis_iste=True)
    c = coz(_yetismez(), ayar)
    assert c["durum"] == "sure_yetmedi", c["durum"]
    assert c.get("teshis"), "istenmesine ragmen teshis yok"
    assert c.get("teshis_kesin") is False, (
        "butce dolmusken kosan teshis 'kesin' diye isaretlenmis: %r"
        % c.get("teshis_kesin"))


def test_KANITLANMIS_teshis_KESIN_der():
    """Kanitlanmis cozumsuzlukte teshis kesindir -- ayrim ciktida gorunmeli."""
    c = coz(_imkansiz(), {"azami_saniye": 30})
    assert c["durum"] == "cozumsuz"
    assert c.get("teshis_kesin") is True, (
        "kanitlanmis cozumsuzlukte teshis kesin olmaliydi: %r"
        % c.get("teshis_kesin"))
