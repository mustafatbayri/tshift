# -*- coding: utf-8 -*-
"""Kaydedilmis planlardan (K-66 plan kaydi) VARDIYA_ROTASYON_YONU sayimi -- K-65 "once/sonra".

11 Ekim'den onceki kodun kosulari (ornegin `rotasyon-once-900`) kuralin
govdesini bilmiyordu: `dogrulama` raporunda rotasyon satiri, `cikti.metrikler`de
`rotasyon_*` alani yok. Bu betik plan dosyalarini okur, BAGIMSIZ DOGRULAYICIYI
(bugunku kod) kural aktifken yeniden kosturur ve kisi x gun ciftlerini sayar:
geri gecis sayisi, toplam/ortalama geri saat, buyuklik dagilimi, sabah->gece
atlamasi payi. Boylece "once" ile "sonra" AYNI olcuyle kiyaslanir.

Kullanim:
  py plandan_say.py ..\\..\\planlar\\kalite-olcumu-95-rotasyon-once-900\\*.json
  py plandan_say.py <plan.json> [<plan.json> ...]
Sahne: plan dosyasinin `kayit.olcek` / `kayit.doluluk` degerleriyle
`uret_veri_seti.sahne_uret` (fikstur dosyasi bire bir ayni sahneyi uretir;
`kayit.sahne` dolu ise o dosya okunur).
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


def sahne(kayit):
    yol = kayit.get("sahne")
    if yol and os.path.exists(yol):
        return json.load(io.open(yol, encoding="utf-8"))
    from uret_veri_seti import sahne_uret
    return sahne_uret(float(kayit.get("olcek", 1.0)), float(kayit.get("doluluk", 0.95)))


def say(girdi, atamalar):
    """Dogrulayicinin sayimi + cift ayrintisi (buyukluk, sabah->gece atlamasi)."""
    g = json.loads(json.dumps(girdi))
    if not any(k.get("kod") == "VARDIYA_ROTASYON_YONU" for k in g.get("kurallar", [])):
        g.setdefault("kurallar", []).append({"kod": "VARDIYA_ROTASYON_YONU", "tur": "YUMUSAK", "aktif": True})
    r = degerlendir(g, atamalar)
    satirlar = [i for i in r["ihlaller"] if i["kural"] == "VARDIYA_ROTASYON_YONU"]
    bas = collections.defaultdict(dict)
    for a in atamalar:
        d = int(a["gun"])
        bas[a["calisan"]][d] = min(bas[a["calisan"]].get(d, 99), float(a["bas"]))
    cift = sum(1 for k in bas for d in bas[k] if d + 1 in bas[k])
    atlama = 0
    buyukluk = collections.Counter()
    for i in satirlar:
        d = i["gun"]
        b0, b1 = bas[i["calisan"]].get(d - 1), bas[i["calisan"]].get(d)
        if b0 is not None and b1 is not None and ((b1 % 24) - (b0 % 24)) > 12:
            atlama += 1                      # duz fark > 12: sabah->gece atlamasi (dairesel geri)
        buyukluk[round(i["olculen"], 2)] += 1
    toplam = sum(i["olculen"] for i in satirlar)
    return {"cift": cift, "geri": len(satirlar), "geri_saat": round(toplam, 2),
            "ortalama": round(toplam / len(satirlar), 2) if satirlar else 0.0,
            "sabah_gece_atlamasi": atlama, "buyukluk": dict(sorted(buyukluk.items())),
            "yumusak_ihlal": r["metrikler"].get("yumusak_ihlal"),
            "hedef_kapsama_yuzde": r["metrikler"].get("hedef_kapsama_yuzde"),
            "fazla_mesai_saat": round(r["metrikler"].get("fazla_mesai_saat") or 0.0, 2)}


def main(yollar):
    dosyalar = []
    for y in yollar:
        dosyalar.extend(sorted(glob.glob(y)) or [y])
    onceki = None
    for yol in dosyalar:
        d = json.load(io.open(yol, encoding="utf-8"))
        kayit = d.get("kayit") or {}
        anahtar = (kayit.get("olcek"), kayit.get("doluluk"), kayit.get("sahne"))
        if onceki is None or onceki[0] != anahtar:
            onceki = (anahtar, sahne(kayit))
        g = onceki[1]
        s = say(g, (d.get("cikti") or {}).get("atamalar") or [])
        m = (d.get("cikti") or {}).get("metrikler") or {}
        print("%s\n   %s/%s tekrar %s | art arda cift %d | GERI %d (%.1f%%) | %.2f saat, ort. %.2f | sabah->gece %d | "
              "buyukluk %s\n   motor metrigi: gecis %s, saat %s | hedef kapsama %%%s | fazla mesai %s sa | yumusak ihlal %s"
              % (os.path.relpath(yol, KOK), kayit.get("olcum_dosyasi"), kayit.get("yapilandirma"), kayit.get("tekrar"),
                 s["cift"], s["geri"], 100.0 * s["geri"] / s["cift"] if s["cift"] else 0.0, s["geri_saat"], s["ortalama"],
                 s["sabah_gece_atlamasi"], s["buyukluk"], m.get("rotasyon_geri_gecis"), m.get("rotasyon_geri_saat"),
                 s["hedef_kapsama_yuzde"], s["fazla_mesai_saat"], s["yumusak_ihlal"]))
        if m.get("rotasyon_geri_gecis") is not None and m.get("rotasyon_geri_gecis") != s["geri"]:
            print("   !! motor metrigi ile dogrulayici sayimi FARKLI (gecmis gun -1 kaydi: metrik sayar, "
                  "dogrulayici da sayar -- bakilmali)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
