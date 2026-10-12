# -*- coding: utf-8 -*-
"""K-65 gun tanimi D (12 Ekim) -- kaydedilmis planlarda uc sayim yan yana.

Her plan (K-66 plan kaydi) icin:
  * D (bugunku dogrulayici): geri satir sayisi / saati -- `degerlendir`
  * ESKI tanim (11 Ekim, baslangic gunu): yalniz d -> d+1 baslangic ciftleri,
    gecmis gun -1 -- burada AYRICA sayilir (eski kodun dogrulayicisi)
  * motorun KENDI metrigi (`cikti.metrikler.rotasyon_*`) -- D kodunun plani ise
    dogrulayici ile BIREBIR olmali (kabul olcutu 7)
  * amac terimi (`amac_dagilimi.VARDIYA_ROTASYON_YONU.deger`) -- yuvarlanmis
    saat; satirlarin yuvarli toplamiyla kiyas
  * D'nin kazanci = D - eski: gece -> (dokunulmus ara gun) -> sonraki ciftleri

Kullanim: py say_D.py <plan.json> [...]
"""
import collections
import glob
import io
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURASI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "09-motor"))
sys.path.insert(0, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti"))
from dogrulayici import degerlendir                           # noqa: E402
from dogrulayici.kurallar import _rotasyon_geri_saat           # noqa: E402
from uret_veri_seti import sahne_uret                         # noqa: E402

_SAHNE = {}


def sahne(kayit):
    k = (float(kayit.get("olcek", 1.0)), float(kayit.get("doluluk", 0.95)))
    if k not in _SAHNE:
        _SAHNE[k] = sahne_uret(*k)
    return _SAHNE[k]


def eski_tanim(girdi, atamalar):
    bas = collections.defaultdict(dict)
    for a in atamalar:
        d = int(a["gun"])
        b = float(a["bas"])
        bas[a["calisan"]][d] = min(bas[a["calisan"]].get(d, b), b)
    for c in girdi.get("calisanlar", []):
        if c["id"] not in bas:
            continue
        onc = [float(k["bas"]) for k in c.get("gecmis_vardiyalar") or [] if k.get("gun") == -1]
        if onc:
            bas[c["id"]][-1] = min(onc)
    n, s = 0, 0.0
    for g in bas.values():
        for d in g:
            if d + 1 in g:
                h = _rotasyon_geri_saat(g[d], g[d + 1])
                if h > 0:
                    n, s = n + 1, s + h
    return n, round(s, 2)


def main(yollar):
    dosyalar = []
    for y in yollar:
        dosyalar.extend(sorted(glob.glob(y)) or [y])
    print("%-62s %8s %8s | %8s %8s | %8s %8s | %6s %6s | %s"
          % ("plan", "D adet", "D saat", "eski ad", "eski sa", "motor ad", "motor sa", "amac", "satir~", "D kazanci"))
    for yol in dosyalar:
        d = json.load(io.open(yol, encoding="utf-8"))
        g = sahne(d.get("kayit") or {})
        at = d["cikti"]["atamalar"]
        r = degerlendir(json.loads(json.dumps(g)), at)
        sat = [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ROTASYON_YONU"]
        dn, ds = len(sat), round(sum(i["olculen"] for i in sat), 2)
        en, es = eski_tanim(g, at)
        m = d["cikti"].get("metrikler") or {}
        mn, ms = m.get("rotasyon_geri_gecis"), m.get("rotasyon_geri_saat")
        ad = ((d["cikti"].get("cozum_istatistikleri") or {}).get("amac_dagilimi") or {}).get("VARDIYA_ROTASYON_YONU") or {}
        yuv = sum(int(i["olculen"] + 0.5) for i in sat if not i.get("gecmis"))
        ad_ = os.path.relpath(yol, os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti", "planlar"))
        print("%-62s %8d %8.2f | %8d %8.2f | %8s %8s | %6s %6d | +%d (%.2f sa)"
              % (ad_[-62:], dn, ds, en, es, mn, ms, ad.get("deger"), yuv, dn - en, ds - es))


if __name__ == "__main__":
    main(sys.argv[1:])
