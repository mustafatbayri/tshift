# -*- coding: utf-8 -*-
"""
ARAMA ISCISI SAYISI -- makineye uymali, sabit olmamali

⚠ NEDEN VAR (29 Eylul, olculdu)
  Cozucu sekiz arama iscisiyle kosuyordu ve bu sayi koda SABIT yazilmisti.
  Iki cekirdekli bir makinede ayni sahne, ayni surede:

      8 isci  ->  optimumun %50,0'sine kadar gelebildi
      2 isci  ->  optimumun %80,4'une kadar geldi

  Yani makinede olmayan cekirdegi istemek plani KOTULESTIRIYOR: sekiz isci
  iki cekirdek icin sirayla bekliyor, her biri digerinin isini bolerek
  ilerliyor. Bedeli soyut degil -- ayni sure, daha kotu vardiya plani.

  Mustafa'nin sorusu buydu:
    > "Bu 15 dk suren kosuyu daha hizli bir makinede kossak kisa surer mi?
    >  Cloud ortamdan ciddi kapasiteli bir sunucu alsam ise yarar mi?"

  Sunucu almadan once ucretsiz olan duzeltme bu: sayiyi makineye uydurmak.
  Aksi halde alinan sunucunun cekirdekleri de kullanilmazdi -- 32 cekirdekli
  bir makinede de sekiz isci kosardi.

NE SINAR
  Sayinin DOGRU OLDUGUNU degil, MAKINEDEN OKUNDUGUNU. "8 bekliyorum" diyen
  bir test, sekiz cekirdekli makinede sabit kod ile de yesil yanardi.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_isci_sayisi.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.coz import coz, VARSAYILAN                        # noqa: E402


def _sahne():
    """Kucuk ve hizli: burada olculen sey plan kalitesi degil, AYARDIR."""
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "C%02d" % i, "ekipler": ["E"],
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []} for i in range(1, 9)
        ],
        "vardiya_sablonlari": [
            {"id": "V%d" % j, "ekip": "E", "bas": b, "bit": b + 8,
             "mola_dk": 60,
             "mola_politikasi": [
                 {"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
                 {"tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": True}]}
            for j, b in enumerate((8, 12))
        ],
        "talep": [{"ekip": "E", "gun": 0, "saat": s, "asgari": 2, "hedef": 3}
                  for s in range(9, 17)],
        "kurallar": [
            {"kod": k, "tur": "SERT", "aktif": True, "yasal": False,
             "kabul_edilebilir": False}
            for k in ("ASGARI_KAPSAMA", "HAFTA_TATILI", "HAFTALIK_AZAMI",
                      "VARDIYA_ARASI_DINLENME", "MOLA_HAKKI")
        ] + [
            {"kod": "HEDEF_KAPSAMA", "tur": "YUMUSAK", "aktif": True},
        ],
        "kilitler": [], "donmus_gunler": [],
    }


def _bagimsiz_cekirdek():
    """Cekirdek sayisini motordan BAGIMSIZ olarak bir kez daha hesaplar.

    ⚠ Bilerek ikinci bir yol. Testin `cekirdek_sayisi()`'ni cagirip kendi
      cevabiyla karsilastirmasi hicbir sey olcmezdi: fonksiyon `return 8`
      olsa da yesil yanardi.
    """
    if hasattr(os, "sched_getaffinity"):          # Linux: CI makinesi
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


def test_isci_sayisi_CIKTIDA_bildirilir():
    """Kullanici kac isciyle kosuldugunu gorebilmeli.

    Ekranda gosterilen "335.072 degisken | 423.489 kisit" bilgisinin ayni
    ailesinden: plan neden bu kadar surdu sorusunun cevabi burada.
    """
    c = coz(_sahne(), {"azami_saniye": 10})
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("isci_sayisi"), (
        "kac arama iscisiyle kosuldugu ciktida bildirilmiyor: %r" % ist)


def test_VARSAYILAN_makinenin_cekirdegine_uyar():
    """Ayar verilmezse isci sayisi MAKINEDEN okunmali, sabit olmamali."""
    beklenen = _bagimsiz_cekirdek()
    c = coz(_sahne(), {"azami_saniye": 10})
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("isci_sayisi") == beklenen, (
        "isci sayisi makineye uymuyor: %r geldi, makinede %d cekirdek var"
        % (ist.get("isci_sayisi"), beklenen))


def test_ACIKCA_verilen_sayi_korunur():
    """Elle verilen deger makineye EZDIRILMEMELI -- olcum yapabilmek icin.

    Cekirdek sayisini olcen arac tam olarak bunu kullanacak: ayni sahneyi
    1, 2, 4, 8 isciyle kosup hangisinin daha iyi plan verdigini gorecek.
    """
    c = coz(_sahne(), {"azami_saniye": 10, "isci_sayisi": 1})
    ist = c.get("cozum_istatistikleri") or {}
    assert ist.get("isci_sayisi") == 1, (
        "elle verilen isci sayisi korunmadi: %r" % ist.get("isci_sayisi"))


def test_cekirdek_sayisi_HIC_sifir_donmez():
    """Cekirdek okunamazsa 1'e duser; 0 veya None cozucuyu patlatirdi."""
    from cozucu.model import cekirdek_sayisi
    n = cekirdek_sayisi()
    assert isinstance(n, int) and n >= 1, "gecersiz cekirdek sayisi: %r" % n


def test_VARSAYILANDA_sabit_sekiz_kalmadi():
    """Sabit 8 geri gelirse burasi kirmizi yanar.

    ⚠ Bu testin tek isi regresyon. `VARSAYILAN["isci_sayisi"] = 8` satiri
      "hizli olsun diye" geri konursa iki cekirdekli makinelerde plan
      sessizce kotulesir ve kimse sebebini aramaz.
    """
    assert VARSAYILAN.get("isci_sayisi") is None, (
        "isci sayisi yine sabit: %r -- makineden okunmali"
        % VARSAYILAN.get("isci_sayisi"))
