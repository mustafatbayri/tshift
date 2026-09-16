# -*- coding: utf-8 -*-
"""
PLAN PROFILLERI TESTI -- Master Spec v1.4 #5.4, #5.2

NEDEN BU DOSYA VAR
  16 Eylul kirmizi kanit turunda (#16.4) sekiz kirilma denendi, DORDU
  yakalanmadi. Altin senaryolar "iki profil farkli plan uretsin" diyor ve
  bu kosul, agirlik tablosu tamamen yok sayilsa bile baska bir sebeple
  saglanabiliyordu. Yani A7 yesildi ama "#5.4 agirliklari calisiyor"
  iddiasini KANITLAMIYORDU.

  Yakalanmayan dort kirilma:
    1. agirlik tablosu yok sayilir (hep DENGELI sutunu okunur)
    2. adalet gradyani kaldirilir (yalniz K-27 esigi kalir)
    3. orkestra bagimsiz dogrulayiciyi cagirmaz
    4. FAZLA_MESAI_TAVANI profile gore degil sabit alinir

  Buradaki her test bunlardan birini hedefliyor ve hepsi once KIRMIZI
  yandigi dogrulanarak yazildi.

OLCUM YONTEMI -- neden "kim secildi" degil "amac degeri"
  "Motor C04'u sectu" bicimindeki testler kirilgan: kisit gevsekse cozucu
  esit degerdeki secenekler arasinda arama sirasina gore secer. Gradyan
  kaldirildiginda bile ayni kisiyi secebilir -- ve test yanlis yesil yanar.
  Bu olculdu, varsayilmadi.

  Saglam olcum: ayni girdiyi iki kez, iki farkli secim SABITLENMIS halde
  cozup `cozum_istatistikleri.amac_degeri` karsilastirmak. Gradyan varsa
  yogun dagilim PAHALIDIR; yoksa ikisi esittir.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_profiller.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu import coz                                       # noqa: E402
from cozucu.model import (AGIRLIK_TABLOSU, FAZLA_MESAI_PROFIL,  # noqa: E402
                          Model, PROFILLER)
from orkestra import coz_ve_onar                             # noqa: E402


# ----------------------------------------------------------------------
# Kucuk sahne: tek gun, tek sablon, tek ekip
# ----------------------------------------------------------------------

def _sahne(devir, profil="DENGELI", esik=2, haftalik=45, asgari=3):
    return {
        "profil": profil,
        "calisanlar": [
            {"id": k, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": haftalik},
             "devir_yuk": {"cumartesi": v}}
            for k, v in sorted(devir.items())
        ],
        "vardiya_sablonlari": [
            {"id": "V", "bas": 9, "bit": 13, "mola_dk": 0, "gunler": [5]},
        ],
        "talep": [
            {"ekip": "E", "gunler": [5], "saatler": [9, 10, 11, 12],
             "asgari": asgari, "hedef": asgari},
        ],
        "kurallar": [
            {"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
             "yasal": False, "kabul_edilebilir": False},
            {"kod": "ADALET_DENGESI", "tur": "YUMUSAK", "aktif": True,
             "parametreler": {"boyutlar": ["cumartesi"],
                              "adaletsizlik_esigi": esik}},
        ],
    }


def _kilitle(girdi, calisanlar):
    """Verilen kisileri cumartesiye SABITLER, digerlerini o gune kapatir."""
    secilen = set(calisanlar)
    kilitler = []
    for c in girdi["calisanlar"]:
        if c["id"] in secilen:
            kilitler.append({"calisan": c["id"], "gun": 5, "bas": 9, "bit": 13})
        else:
            kilitler.append({"calisan": c["id"], "gun": 5, "tip": "yasak"})
    g = dict(girdi)
    g["kilitler"] = kilitler
    g["kurallar"] = girdi["kurallar"] + [
        {"kod": "KILIT_UYUMU", "tur": "SERT", "aktif": True}]
    return g


def _amac(girdi):
    c = coz(girdi, {"azami_saniye": 20})
    assert c["durum"] == "cozuldu", c.get("sebep") or c.get("teshis")
    return c["cozum_istatistikleri"]["amac_degeri"]


# ----------------------------------------------------------------------
# 1. Agirlik tablosu gercekten profile gore okunuyor mu  (kirilma 1)
# ----------------------------------------------------------------------

def test_agirlik_tablosu_profile_gore_degisir():
    """#5.4 tablosunun her satiri, her profilde dogru sutunu vermeli."""
    for kod, satir in AGIRLIK_TABLOSU.items():
        for profil in PROFILLER:
            m = Model(_sahne({"C1": 0}, profil=profil))
            assert m._agirlik(kod) == satir[profil], (
                "%s / %s: tablo %r diyor, model %r verdi"
                % (kod, profil, satir[profil], m._agirlik(kod)))


def test_hedef_kapsama_agirligi_profiller_arasinda_farkli():
    """Tablonun TEK BIR satirinin somut degerleri -- #5.4'ten birebir.

    Yukaridaki test tabloyu kendisiyle karsilastiriyor; tablo yanlis
    doldurulsaydi yine yesil yanardi. Bu test sartnamedeki sayilari
    ELLE yaziyor, o yuzden tablo bozulursa yakalar.
    """
    beklenen = {"DENGELI": 9, "KAPSAMA": 20, "CALISAN": 5}
    for profil, deger in beklenen.items():
        m = Model(_sahne({"C1": 0}, profil=profil))
        assert m._agirlik("HEDEF_KAPSAMA") == deger


def test_kiraci_agirligi_profil_tablosunu_ezer():
    """#9.16: kiraci plan_profiles'i duzenleyebilir."""
    girdi = _sahne({"C1": 0}, profil="KAPSAMA")
    girdi["agirliklar"] = {"HEDEF_KAPSAMA": 3}
    assert Model(girdi)._agirlik("HEDEF_KAPSAMA") == 3


def test_taninmayan_profil_sessizce_yutulmaz():
    """Yanlis profil adi DENGELI'ye duser AMA notlarda bildirilir.

    Sessizce DENGELI'ye dusmek, kullanicinin 'calisan odakli plan istedim'
    deyip dengeli plan almasi demektir -- ve bunu hic ogrenmez.
    """
    m = Model(_sahne({"C1": 0}, profil="CALISAN_ODAKLI")).kur()
    assert m.profil == "DENGELI"
    assert any("profil taninmadi" in n for n in m.notlar), m.notlar


# ----------------------------------------------------------------------
# 2. Adalet gradyani gercekten var mi  (kirilma 2)
# ----------------------------------------------------------------------

def test_yogun_dagilim_esik_altinda_bile_daha_pahali():
    """K-27 esigini ASMAYAN iki dagilim -- ama biri digerinden pahali olmali.

    Devir: C1,C2,C3 = 2 · C4,C5,C6 = 0. Cumartesiye 3 kisi gerekiyor.
      * C4,C5,C6 secilirse sayilar 2,2,2,1,1,1 -> ortalama 1.5, sapma 0.5
      * C1,C2,C3 secilirse sayilar 3,3,3,0,0,0 -> ortalama 1.5, sapma 1.5

    Ikisi de K-27 esigini (2) ASMIYOR, yani IKISI DE IHLALSIZ. Esik tek
    basina kalsaydi motor icin ayni degerde olurlardi. Gradyan varsa
    yogun olan pahalidir.
    """
    devir = {"C1": 2, "C2": 2, "C3": 2, "C4": 0, "C5": 0, "C6": 0}
    girdi = _sahne(devir)
    adil = _amac(_kilitle(girdi, ["C4", "C5", "C6"]))
    yogun = _amac(_kilitle(girdi, ["C1", "C2", "C3"]))
    assert yogun > adil, (
        "esik altinda kalan iki dagilim ayni fiyatta (adil=%r, yogun=%r): "
        "ADALET_DENGESI'nin gradyani yok, agirligini degistirmek plani "
        "degistiremez (#5.4)" % (adil, yogun))


def test_adalet_agirligi_buyudukce_fark_buyur():
    """CALISAN profilinde adaletsizlik, KAPSAMA profilindekinden pahali.

    #5.4: ADALET_DENGESI agirligi KAPSAMA'da 2, CALISAN'da 8. Ayni iki
    dagilim arasindaki fiyat farki da o oranda buyumeli. Agirlik amac
    fonksiyonuna hic girmiyorsa iki fark esit cikar.
    """
    devir = {"C1": 2, "C2": 2, "C3": 2, "C4": 0, "C5": 0, "C6": 0}
    farklar = {}
    for profil in ("KAPSAMA", "CALISAN"):
        girdi = _sahne(devir, profil=profil)
        farklar[profil] = (_amac(_kilitle(girdi, ["C1", "C2", "C3"]))
                           - _amac(_kilitle(girdi, ["C4", "C5", "C6"])))
    assert farklar["CALISAN"] > farklar["KAPSAMA"], (
        "adaletsizligin bedeli iki profilde ayni (%r): agirlik amac "
        "fonksiyonuna girmiyor" % farklar)


def test_gereksiz_atama_bedava_degil():
    """Hedef 3 iken motor 3'ten fazla kisi koymamali.

    Ilk yazilan gradyan ORTALAMAYA gore ceza veriyordu ve motor cumartesiye
    5 kisi koyuyordu: ortalamayi yukseltmek herkesin sapmasini dusuruyordu.
    Yani ceza, cezalandirdigi seyi odullendiriyordu. Bu test o acigi kapatir.
    """
    girdi = _sahne({"C%d" % i: 0 for i in range(1, 9)}, asgari=3)
    c = coz(girdi, {"azami_saniye": 20})
    assert c["durum"] == "cozuldu"
    assert len(c["atamalar"]) == 3, (
        "hedef 3 iken %d atama yapildi -- fazla atama bedava"
        % len(c["atamalar"]))


# ----------------------------------------------------------------------
# 3. /solve bagimsiz dogrulayiciyi gercekten cagiriyor mu  (kirilma 3)
# ----------------------------------------------------------------------

def test_solve_ciktisinda_bagimsiz_denetim_var():
    """#16.1: motorun kendi 'sert_ihlal: 0' bayragina bakilmaz.

    orkestra dogrulayiciyi cagirmayi birakirsa bu blok kaybolur. Import
    satirini kontrol eden test bunu YAKALAMAZ -- import durur, cagri
    kaybolur. O yuzden ciktinin kendisine bakiliyor.
    """
    c = coz_ve_onar(_sahne({"C1": 0, "C2": 0, "C3": 0}), {"azami_saniye": 20})
    assert c["durum"] == "cozuldu"
    assert "bagimsiz_denetim" in c, "cikti bagimsiz denetim ozeti tasimiyor"
    assert "sert_ihlal" in c["bagimsiz_denetim"]
    assert "yayin_kapisi" in c["bagimsiz_denetim"]


def test_onarim_denemesi_her_zaman_bildirilir():
    """#11.7: kac kez yeniden denendigi musteriye gosterilen bir sayidir."""
    c = coz_ve_onar(_sahne({"C1": 0, "C2": 0, "C3": 0}), {"azami_saniye": 20})
    assert c["cozum_istatistikleri"]["onarim_denemesi"] == 0


# ----------------------------------------------------------------------
# 4. Fazla mesai tavani profile bagli mi  (kirilma 4)
# ----------------------------------------------------------------------

def test_fazla_mesai_tavani_profile_gore():
    """#5.2: CALISAN 0 · DENGELI 10 · KAPSAMA 15."""
    assert FAZLA_MESAI_PROFIL == {"DENGELI": 10, "KAPSAMA": 15, "CALISAN": 0}


def _fm_sahne(asgari, hedef, profil="DENGELI"):
    """Sozlesme 8 saat = 2 vardiya. Gunde `asgari` kisi x 3 gun gerekiyorsa
    kisi basi 3 vardiya = 12 saat duser -> 4 saat fazla mesai ZORUNLU olur."""
    g = _sahne({"C1": 0, "C2": 0, "C3": 0}, profil=profil, haftalik=8)
    g["vardiya_sablonlari"] = [{"id": "V", "bas": 9, "bit": 13, "mola_dk": 0}]
    g["talep"] = [{"ekip": "E", "gunler": [0, 1, 2], "saatler": [9, 10, 11, 12],
                   "asgari": asgari, "hedef": hedef}]
    g["kurallar"] = g["kurallar"] + [
        {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True,
         "parametreler": {"azami_saat": 45}},
        {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True,
         "parametreler": {"azami_saat_hafta": 10}},
    ]
    return g


def test_fazla_mesai_hedef_kapsama_icin_KULLANILMAZ():
    """K-30 (Mustafa, 16 Eylul): "hedef hic gitmemek."

    Asgari kapsama tutuyor, yalniz HEDEF kapsama fazla mesaiyle
    iyilesecek. Motor fazla mesai yapmamali -- hedefi eksik birakmali.

    BU TESTIN GUCU OLCULDU -- ve sinirli oldugu bilerek birakildi.
      Ceza 50 -> 0 yapilinca test KIRMIZI yaniyor.
      Ceza 50 -> 1 yapilinca test YESIL kaliyor.

    Yani test "ceza SIFIR OLMASIN" diyor, "ceza tam olarak 50 olsun"
    demiyor. Dogrusu da bu: K-30 bir DAVRANIS karari ("hedef icin fazla
    mesai yapma"), bir sayi karari degil. Sayiyi teste civilemek, ileride
    kalibrasyon degistiginde ürün karari degismemis olsa bile testi
    kirmizi yakardi -- yanlis alarm veren kapi, olmayan kapidan kotudur
    (O-7).
    """
    c = coz(_fm_sahne(asgari=2, hedef=3), {"azami_saniye": 20})
    assert c["durum"] == "cozuldu"
    assert c["metrikler"]["fazla_mesai_saat"] == 0, (
        "hedef kapsama ugruna fazla mesai yapildi (%r saat) -- K-30'a aykiri"
        % c["metrikler"]["fazla_mesai_saat"])


def test_fazla_mesai_asgari_kapsama_zorlarsa_KULLANILIR():
    """K-30: "gidilecekse de minimum gitmek."

    Asgari kapsama SERT ve fazla mesai olmadan tutmuyor. Motor plan
    uretmekten vazgecmemeli; fazla mesaiyi GEREKTIGI KADAR kullanmali.

    Bu testin ters yonu onemli: motor burada da 0 fazla mesai yapsaydi
    plan cozumsuz olurdu -- yani "hic fazla mesai yapma" kurali asgari
    kapsamayi da oldururdu. K-30 bunu istemiyor.
    """
    c = coz(_fm_sahne(asgari=3, hedef=3), {"azami_saniye": 20})
    assert c["durum"] == "cozuldu"
    # 3 kisi x 3 gun x 4 saat = 36 saat; sozlesme 3 x 8 = 24 saat.
    # Aradaki 12 saat ZORUNLU asimdir -- ne eksigi ne fazlasi.
    assert c["metrikler"]["fazla_mesai_saat"] == 12, (
        "zorunlu fazla mesai %r saat cikti, 12 olmaliydi"
        % c["metrikler"]["fazla_mesai_saat"])
    assert c["metrikler"]["asgari_kapsama_yuzde"] == 100


def test_profil_tavani_zorunlu_fazla_mesainin_SINIRIDIR():
    """#5.2 tavani olu bir sayi degil: zorunlu asimin ne kadarina izin
    verildigini o soyluyor.

    Ayni sahne, uc profil. CALISAN'da tavan 0 oldugu icin 12 saatlik
    zorunlu asim mumkun degil -> plan cozumsuz. Digerlerinde tavan
    yetiyor -> plan uretiliyor.
    """
    assert coz(_fm_sahne(3, 3, "KAPSAMA"), {"azami_saniye": 20})["durum"] == "cozuldu"
    assert coz(_fm_sahne(3, 3, "DENGELI"), {"azami_saniye": 20})["durum"] == "cozuldu"
    assert coz(_fm_sahne(3, 3, "CALISAN"), {"azami_saniye": 20})["durum"] == "cozumsuz"


@pytest.mark.parametrize("profil,cozulur", [
    ("KAPSAMA", True),      # tavan 15 saat -> 4 saatlik asim serbest
    ("DENGELI", True),      # tavan 10 saat -> serbest
    ("CALISAN", False),     # tavan 0 saat  -> sozlesme asilamaz
])
def test_sozlesme_asimi_yalniz_tavan_izin_verdiginde_mumkun(profil, cozulur):
    """Sozlesmesi 8 saat olan kisiye 12 saatlik hafta SABITLENIR.

    Tavan 0 ise (CALISAN) model cozumsuz olmali; tavan varsa cozulmeli.
    Ceza degil KISIT sinaniyor: cezanin buyuklugu ayri bir mesele (T-15).
    """
    girdi = _sahne({"C1": 0, "C2": 0, "C3": 0}, profil=profil, haftalik=8,
                   asgari=3)
    girdi["vardiya_sablonlari"] = [
        {"id": "V", "bas": 9, "bit": 13, "mola_dk": 0},          # 4 saat, her gun
    ]
    girdi["talep"] = [{"ekip": "E", "gunler": [0, 1, 2], "saatler": [9, 10, 11, 12],
                       "asgari": 3, "hedef": 3}]
    girdi["kurallar"] = girdi["kurallar"] + [
        {"kod": "FAZLA_MESAI_TAVANI", "tur": "SERT", "aktif": True,
         "parametreler": {"azami_saat_hafta": 10}},
        {"kod": "HAFTALIK_AZAMI", "tur": "SERT", "aktif": True,
         "parametreler": {"azami_saat": 45}},
    ]
    c = coz(girdi, {"azami_saniye": 20})
    assert (c["durum"] == "cozuldu") is cozulur, (
        "%s profilinde durum %r (beklenen cozulur=%r): FAZLA_MESAI_TAVANI "
        "profile gore uygulanmiyor" % (profil, c["durum"], cozulur))
