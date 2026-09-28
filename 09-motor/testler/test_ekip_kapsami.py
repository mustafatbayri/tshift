# -*- coding: utf-8 -*-
"""
EKIP KAPSAMI -- T-46'nin kirmizi kaniti

NE KORUYOR
  Bir calisan, YALNIZ kendi ekiplerinin vardiya sablonlarina atanabilir.

NEDEN BIR TEST GEREKTI (28 Eylul, olculdu)
  Motor bunu engellemiyordu. SATIS calisani BACKOFFICE vardiyasina
  atanabiliyordu:

      >>> k.m.Add(k.x[("S1", 0, "V-BO")] == 1)
      >>> cozucu.Solve(k.m)
      OPTIMAL

  Sonucu SESSIZ BIR KAPASITE KAYBI: kisinin saatleri dolar (HAFTALIK_AZAMI,
  HAFTA_TATILI, ARDISIK_CALISMA_GUNU hepsi sayar), ama HICBIR ekibin
  kapsamasina sayilmaz -- `_atanmis` ekibe gore suzuyor. Yani calisan
  "mesgul" ama kimseye faydasi yok.

  Cozucu bunu kendiliginden SECMEZ (hicbir kazanci yok), ama:
    - bir KILIT onu zorlayabilir
    - kapsama baskisi altinda beraberlik bozan olarak cikabilir
    - elle duzenlenmis ya da disaridan gelen bir plan bunu icerebilir

NEDEN 350 KISILIK VERI SETI OLMADAN GORUNMEDI
  Bugune kadarki butun test sahnelerinde TEK EKIP vardi. Capraz ekip
  atamasi tanimsizdi, dolayisiyla hicbir test onu deneyemezdi. Uc ekipli
  ilk sahne kurulunca bir dakikada goruldu.

  Ayni kok, ayni gun T-46'nin performans yuzunu de acikliyor: motor her
  kisiye BUTUN sablonlarin degiskenini aciyordu -- 350 kiside 968 bin
  degiskenin %64'u.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\09-motor
  py -m pytest testler/test_ekip_kapsami.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cozucu.model import Model                                # noqa: E402
from orkestra import coz_ve_onar                              # noqa: E402


def _iki_ekipli(ekipler=("SATIS",)):
    return {
        "profil": "DENGELI",
        "calisanlar": [
            {"id": "S1", "ekipler": list(ekipler),
             "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
             "izinler": [], "uygunluk": []},
        ],
        "vardiya_sablonlari": [
            {"id": "V-SAT", "ekip": "SATIS", "bas": 9, "bit": 17,
             "mola_dk": 60, "gunler": [0]},
            {"id": "V-BO", "ekip": "BACKOFFICE", "bas": 9, "bit": 17,
             "mola_dk": 60, "gunler": [0]},
        ],
        "talep": [], "kurallar": [], "kilitler": [], "donmus_gunler": [],
    }


def test_baska_ekibin_vardiyasina_DEGISKEN_uretilmez():
    """SATIS calisani icin BACKOFFICE sablonunun degiskeni hic olusmamali.

    Bu ayni zamanda T-46'nin performans yuzu: uretilmeyen degisken
    kurulmuyor, saklanmiyor, cozucuye verilmiyor.
    """
    k = Model(_iki_ekipli())
    k.kur()
    assert ("S1", 0, "V-SAT") in k.x, "kendi ekibinin vardiyasi kaybolmus"
    assert ("S1", 0, "V-BO") not in k.x, (
        "SATIS calisani icin BACKOFFICE vardiyasinin degiskeni uretilmis "
        "-- kisi baska ekibin vardiyasina atanabilir"
    )


def test_COK_EKIPLI_calisan_ikisini_de_alir():
    """`ekipler` bir LISTE. Iki ekipteki kisi iki sablonu da gorur.

    Suzgec ekip UYELIGINE bakar, tek bir ekibe degil -- yoksa cok ekipli
    calisan sessizce kisitlanirdi.
    """
    k = Model(_iki_ekipli(("SATIS", "BACKOFFICE")))
    k.kur()
    assert ("S1", 0, "V-SAT") in k.x
    assert ("S1", 0, "V-BO") in k.x, (
        "cok ekipli calisan ikinci ekibinin vardiyasini goremiyor")


def test_EKIPSIZ_sablon_herkese_acik():
    """`ekip` alani olmayan sablon kisitlanmaz -- geriye donuk uyum.

    Eski fiksturlerin cogunda sablonun `ekip` alani yok; onlar bozulmamali.
    """
    g = _iki_ekipli()
    g["vardiya_sablonlari"] = [
        {"id": "V-GENEL", "bas": 9, "bit": 17, "mola_dk": 60, "gunler": [0]}]
    k = Model(g)
    k.kur()
    assert ("S1", 0, "V-GENEL") in k.x, (
        "ekipsiz sablon suzulmus -- eski fiksturler bozulur")


def test_plan_uretilirken_capraz_atama_CIKMAZ():
    """Uctan uca: uretilen planda kimse baska ekibin vardiyasinda olmamali."""
    g = _iki_ekipli()
    g["calisanlar"].append(
        {"id": "B1", "ekipler": ["BACKOFFICE"],
         "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": 45},
         "izinler": [], "uygunluk": []})
    g["talep"] = [{"ekip": e, "gun": 0, "saat": s, "asgari": 1, "hedef": 1}
                  for e in ("SATIS", "BACKOFFICE") for s in range(9, 17)]
    g["kurallar"] = [{"kod": "ASGARI_KAPSAMA", "tur": "SERT", "aktif": True,
                      "yasal": False, "kabul_edilebilir": False}]
    c = coz_ve_onar(g, {"azami_saniye": 30})
    assert c["durum"] == "cozuldu", c.get("durum")
    sablon_ekip = {t["id"]: t.get("ekip") for t in g["vardiya_sablonlari"]}
    calisan_ekip = {x["id"]: set(x["ekipler"]) for x in g["calisanlar"]}
    for a in c["atamalar"]:
        e = sablon_ekip.get(a.get("sablon"))
        if e is None:
            continue
        assert e in calisan_ekip[a["calisan"]], (
            "%s (%s ekibinde) %s ekibinin vardiyasina atanmis"
            % (a["calisan"], ", ".join(calisan_ekip[a["calisan"]]), e))
