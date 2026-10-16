# -*- coding: utf-8 -*-
"""
CAPRAZ DENETIM -- depodaki her referans / tanik / kayitli plan, BUGUNKU dogrulayicidan
gecer (16 Ekim; oturum 14 Ekim §18, D)

NEDEN
  Referanslar ve olcum planlari uretildikleri gunun dogrulayicisiyla "sert 0" aldi.
  Dogrulayici o gunden beri degisti (15 Ekim: dakika hassasiyeti `_dk`, K-39 yari
  zamanlida FAZLA_MESAI_TAVANI atlanir) ve degisecek. Eski "sert 0" cumlesi bugun de
  dogru mu? Kimse bakmiyordu. Bu arac bakar:

  1. FIKSTURLER  fikstur/_sahne-L1*.json + _referans-L1*.json ciftleri (tanikli -EK
     dahil): referans sahnede sert 0 / asim 0 / eksik 0, fm <= kayittaki izinli fm;
     sahnedeki referans_puani kalemlerin toplami; `--puan` ile puan motorun olcusuyle
     yeniden hesaplanir (plan_puani; 500 kiside dakikalar).
  2. PLANLAR     planlar/<olcum>/<yapilandirma-tekrar>.json (tshift-plan-kaydi/1):
     sahne dosya adindan bulunur (L1[-EK][-VSx][-cesit][-olcek] -> fikstur; S30 -> _sahne-S30-95);
     TAZE degerlendir sonucu KAYITLI `dogrulama` ile kiyaslanir: sert sayisi, yayinlanabilir,
     fazla mesai. Fark = dogrulayici o gunden beri bu plana BASKA diyor (bulgu; hata degil).
     Motorun kendi fm metrigi dogrulayicininkiyle de kiyaslanir (bagimsizlik, #7.6).

CIKTI
  Tablo + ozet; `--json <dosya>` ile makine okur. Cikis kodu: 0 temiz, 1 en az bir
  SART tutmadi (fikstur sert/asim/eksik/fm ya da plan kaydinda sert FARKI).

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py capraz-denetim.py                 (fiksturler + planlar)
  py capraz-denetim.py --yalniz fikstur --puan
  py capraz-denetim.py --yalniz plan --json capraz-denetim-sonucu.json
"""

import glob
import io
import json
import os
import re
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

FIKSTUR = os.path.join(BURASI, "fikstur")
PLANLAR = os.path.join(BURASI, "planlar")
L1_AD = re.compile(r"^_sahne-L1(?P<eki>(?:-EK)?(?:-VS\d)?)-95(?:-(?P<olcek>[0-9.]+))?\.json$")
# kalite-olc dosya adi: kalite-olcumu-L1[-EK][-VS<n>][-<cesit>][-<olcek>]-95-<etiket>.json
OLCUM_AD = re.compile(r"^kalite-olcumu-L1(?P<eki>(?:-EK)?(?:-VS\d)?)(?:-(?P<cesit>[a-z][a-z_0-9]*?))?(?:-(?P<olcek>0\.\d+))?-95-")


def _oku(yol):
    with io.open(yol, encoding="utf-8") as f:
        return json.load(f)


def _denetle(g, atamalar):
    from dogrulayici import degerlendir
    r = degerlendir(g, atamalar)
    sert = [i for i in r["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis")]
    return r, {"sert": len(sert), "sert_kurallar": sorted({i["kural"] for i in sert}),
               "asim": sum(1 for i in r["ihlaller"] if i["kural"] == "HEDEF_ASIMI"),
               "eksik": sum(1 for i in r["ihlaller"] if i["kural"] == "HEDEF_KAPSAMA"),
               "fazla_mesai_saat": round(r["metrikler"].get("fazla_mesai_saat") or 0.0, 2),
               "yayinlanabilir": bool(r["yayin_kapisi"]["yayinlanabilir"])}


# ----------------------------------------------------------------------
# 1. Fiksturler
# ----------------------------------------------------------------------

def fiksturler():
    cikan = []
    for yol in sorted(glob.glob(os.path.join(FIKSTUR, "_sahne-L1*.json"))):
        ad = os.path.basename(yol)
        ref_yol = os.path.join(FIKSTUR, ad.replace("_sahne-", "_referans-"))
        if os.path.exists(ref_yol):
            cikan.append((yol, ref_yol))
    return cikan


def fikstur_denetle(sahne_yolu, referans_yolu, puan=False):
    import merdiven as MD
    g, ref = _oku(sahne_yolu), _oku(referans_yolu)
    t0 = time.time()
    _, d = _denetle(g, ref["atamalar"])
    k = ref.get("kayit") or {}
    izinli_fm = float(k.get("fazla_mesai_saat") or 0) if k.get("fazla_mesaisiz_kanitli_yok") else 0.0
    p = (g.get("_merdiven") or {}).get("referans_puani") or {}
    toplam = sum(x.get("ceza", 0) for x in (p.get("dagilim") or {}).values())
    s = {"dosya": os.path.basename(sahne_yolu), "kisi": len(g["calisanlar"]), "atama": len(ref["atamalar"]),
         "sert": d["sert"], "sert_kurallar": d["sert_kurallar"], "asim": d["asim"], "eksik": d["eksik"],
         "fm": d["fazla_mesai_saat"], "izinli_fm": izinli_fm, "yayinlanabilir": d["yayinlanabilir"],
         "puan": p.get("amac"), "puan_toplam_tutuyor": (p.get("amac") == toplam) if p else None,
         "saniye": round(time.time() - t0, 1)}
    s["temiz"] = (d["sert"] == 0 and d["asim"] == 0 and d["eksik"] == 0
                  and d["fazla_mesai_saat"] <= izinli_fm + 1e-9 and s["puan_toplam_tutuyor"] is not False)
    if puan and p:
        t1 = time.time()
        yeni = MD.plan_puani(g, ref["atamalar"])
        s["puan_yeniden"] = (yeni or {}).get("amac")
        s["puan_ayni"] = bool(yeni and yeni.get("durum") == "OPTIMAL" and yeni["amac"] == p.get("amac"))
        s["puan_saniye"] = round(time.time() - t1, 1)
        s["temiz"] = s["temiz"] and s["puan_ayni"]
    return s


# ----------------------------------------------------------------------
# 2. Kayitli planlar
# ----------------------------------------------------------------------

def plan_sahnesi(olcum_adi, kayit):
    """Olcum dosyasinin adindan sahne. Donen (yol | None, aciklama)."""
    import merdiven as MD
    m = OLCUM_AD.match(olcum_adi)
    if m:
        eki, cesit, olcek = m.group("eki"), m.group("cesit"), m.group("olcek")
        yol = os.path.join(FIKSTUR, "_sahne-L1%s-95%s.json" % (eki, ("-" + olcek) if olcek else ""))
        if not os.path.exists(yol):
            return None, "sahne dosyasi yok: " + os.path.basename(yol)
        g = _oku(yol)
        if cesit:
            if cesit not in MD.CESITLER:
                return None, "bilinmeyen cesit %s" % cesit
            g = MD.cesit_sahne(g, cesit, float(olcek or 1.0))
        return g, os.path.basename(yol) + ((" + cesit " + cesit) if cesit else "")
    if float(kayit.get("olcek") or 1.0) == 1.0:
        yol = os.path.join(FIKSTUR, "_sahne-S30-%d.json" % round(float(kayit.get("doluluk") or 0.95) * 100))
        if os.path.exists(yol):
            return _oku(yol), os.path.basename(yol)
        return None, "sahne dosyasi yok: " + os.path.basename(yol)
    return None, "olcek %s sahnesi bellekte uretilmisti (dosya yok) -- atlandi" % kayit.get("olcek")


def planlar():
    return sorted(y for y in glob.glob(os.path.join(PLANLAR, "*", "*.json")))


def plan_denetle(yol, sahne_onbellek=None):
    p = _oku(yol)
    k = p.get("kayit") or {}
    s = {"dosya": os.path.relpath(yol, PLANLAR).replace(os.sep, "/"), "bicim": k.get("bicim"),
         "tarih": k.get("tarih"), "olcum": k.get("olcum_dosyasi")}
    if k.get("bicim") != "tshift-plan-kaydi/1":
        s["atlandi"] = "bicim %s" % k.get("bicim")
        return s
    olcum = k.get("olcum_dosyasi") or os.path.basename(os.path.dirname(yol)) + ".json"
    anahtar = (olcum,)
    if sahne_onbellek is not None and anahtar in sahne_onbellek:
        g, acik = sahne_onbellek[anahtar]
    else:
        g, acik = plan_sahnesi(olcum, k)
        if sahne_onbellek is not None:
            sahne_onbellek[anahtar] = (g, acik)
    s["sahne"] = acik
    if g is None:
        s["atlandi"] = acik
        return s
    cikti = p.get("cikti") or {}
    atamalar = cikti.get("atamalar")
    if not atamalar:
        s["atlandi"] = "plan yok (durum %s)" % cikti.get("durum")
        return s
    if len(g["calisanlar"]) != (p.get("girdi_ozeti") or {}).get("kisi", len(g["calisanlar"])):
        s["atlandi"] = "kisi sayisi uymuyor (sahne %d, kayit %s)" % (len(g["calisanlar"]), p["girdi_ozeti"].get("kisi"))
        return s
    t0 = time.time()
    r, d = _denetle(g, atamalar)
    eski = p.get("dogrulama") or {}
    eski_sert = len([i for i in eski.get("ihlaller", []) if i.get("agirlik") == "SERT" and not i.get("gecmis")])
    eski_fm = round((eski.get("metrikler") or {}).get("fazla_mesai_saat") or 0.0, 2)
    motor_fm = round(((cikti.get("metrikler") or {}).get("fazla_mesai_saat") or 0.0), 2)
    s.update({"kisi": len(g["calisanlar"]), "atama": len(atamalar), "saniye": round(time.time() - t0, 1),
              "sert_taze": d["sert"], "sert_kayitli": eski_sert, "sert_kurallar_taze": d["sert_kurallar"],
              "yayinlanabilir_taze": d["yayinlanabilir"],
              "yayinlanabilir_kayitli": bool((eski.get("yayin_kapisi") or {}).get("yayinlanabilir")),
              "fm_taze": d["fazla_mesai_saat"], "fm_kayitli": eski_fm, "fm_motor": motor_fm,
              "asim_taze": d["asim"], "eksik_taze": d["eksik"]})
    s["sert_farki"] = d["sert"] != eski_sert
    s["fm_farki"] = abs(d["fazla_mesai_saat"] - eski_fm) > 0.01
    s["motor_fm_farki"] = abs(d["fazla_mesai_saat"] - motor_fm) > 0.01
    s["temiz"] = not (s["sert_farki"] or s["fm_farki"] or s["motor_fm_farki"])
    return s


# ----------------------------------------------------------------------
# 3. Rapor
# ----------------------------------------------------------------------

def _arg(ad, varsayilan, tur=str):
    return tur(sys.argv[sys.argv.index(ad) + 1]) if ad in sys.argv else varsayilan


def main():
    yalniz = _arg("--yalniz", None)
    puan = "--puan" in sys.argv
    sonuc = {"tarih": time.strftime("%Y-%m-%d %H:%M"), "fiksturler": [], "planlar": []}
    kirli = 0
    if yalniz in (None, "fikstur"):
        print("FIKSTURLER (referans / tanik sahnesinde bugunku dogrulayiciyla)")
        print("  %-34s %5s %6s %4s %4s %5s %6s %6s %9s %6s  %s" % ("dosya", "kisi", "atama", "sert", "asim", "eksik", "fm", "izinli", "puan", "sn", "sonuc"))
        for sy, ry in fiksturler():
            s = fikstur_denetle(sy, ry, puan)
            sonuc["fiksturler"].append(s)
            kirli += 0 if s["temiz"] else 1
            print("  %-34s %5d %6d %4d %4d %5d %6.1f %6.1f %9s %6.1f  %s%s" % (
                s["dosya"], s["kisi"], s["atama"], s["sert"], s["asim"], s["eksik"], s["fm"], s["izinli_fm"],
                s["puan"] if s["puan"] is not None else "-", s["saniye"], "TEMIZ" if s["temiz"] else "SART TUTMADI",
                (" (puan yeniden %s, %s)" % (s.get("puan_yeniden"), "ayni" if s.get("puan_ayni") else "FARKLI")) if puan else ""))
            if s["sert_kurallar"]:
                print("      sert kurallar: %s" % ", ".join(s["sert_kurallar"]))
    if yalniz in (None, "plan"):
        print("\nKAYITLI PLANLAR (taze degerlendir vs kayitli dogrulama; fm: taze / kayitli / motor)")
        print("  %-58s %5s %4s %4s %6s %6s %6s %6s  %s" % ("plan", "kisi", "sertT", "sertK", "fmT", "fmK", "fmM", "sn", "sonuc"))
        onbellek = {}
        for y in planlar():
            s = plan_denetle(y, onbellek)
            sonuc["planlar"].append(s)
            if s.get("atlandi"):
                print("  %-58s  atlandi: %s" % (s["dosya"], s["atlandi"]))
                continue
            kirli += 0 if s["temiz"] else 1
            notlar = []
            if s["sert_farki"]:
                notlar.append("SERT FARKI %d -> %d (%s)" % (s["sert_kayitli"], s["sert_taze"], ", ".join(s["sert_kurallar_taze"]) or "-"))
            if s["fm_farki"]:
                notlar.append("fm farki kayitli %.2f taze %.2f" % (s["fm_kayitli"], s["fm_taze"]))
            if s["motor_fm_farki"]:
                notlar.append("motor fm %.2f != dogrulayici %.2f" % (s["fm_motor"], s["fm_taze"]))
            print("  %-58s %5d %4d %4d %6.2f %6.2f %6.2f %6.1f  %s" % (
                s["dosya"], s["kisi"], s["sert_taze"], s["sert_kayitli"], s["fm_taze"], s["fm_kayitli"], s["fm_motor"],
                s["saniye"], "TEMIZ" if s["temiz"] else "; ".join(notlar)))
    sonuc["sart_tutmayan"] = kirli
    print("\nOZET: %d fikstur, %d plan kaydi (%d atlandi); SART TUTMAYAN %d" % (
        len(sonuc["fiksturler"]), len(sonuc["planlar"]), sum(1 for s in sonuc["planlar"] if s.get("atlandi")), kirli))
    js = _arg("--json", None)
    if js:
        with io.open(js, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=1)
        print("JSON yazildi: %s" % js)
    return 1 if kirli else 0


if __name__ == "__main__":
    sys.exit(main())
