# -*- coding: utf-8 -*-
"""Cizelge (vardiya plani) kaydi ve OKUNUR hali -- K-66 (Mustafa, 11 Ekim 2026).

  "Bundan sonra testlerimizin ciktilari cizelge de uretmeli ... Sadece
   Yilmaz'in bakmasi icin degil, sonrasinda UI tarafinda bunu aktarabilmek
   icin de cizelge lazim. Uzun vadede yani urunde kullanilacak cizelge
   ciktisi uret. Tum kosumlarda bu cizelge hazir olsun artik."

Olcum araci (kalite-olc.py) 2 Ekim'den beri her kosunun yalniz OZETINI
yaziyordu; motorun urettigi plan dosyaya girmiyordu. Bu modul her kosu icin
URUN SOZLESMESINDEKI bicimde bir kayit ve ondan turetilmis okunur bir sayfa
yazar:

  <ad>.json : URUN BICIMI. {"kayit": {...}, "girdi_ozeti": {...},
              "cikti": <motorun /solve cevabi, sartname #11.3 -- atamalar,
              metrikler, cozum_istatistikleri, uygulanmayan_notlar,
              bagimsiz_denetim>, "dogrulama": <bagimsiz dogrulayicinin tam
              raporu, #11.4 -- ihlaller, metrikler, yayin_kapisi, ...>}.
              `cikti` bire bir servis.py'nin /solve'da dondurdugu yapidir
              (istek_id haric); arayuz ve arka uc BU dosyaya karsi
              gelistirilebilir. Hicbir alan yeniden adlandirilmaz.
  <ad>.html : okunur cizelge (goz icin, UI'nin yerine degil): (1) kisi x gun
              tablosu (vardiya saati, ekip, molalar; satir sonunda gun/brut/
              net saat), (2) ekip x gun x saat kapsama izgarasi (atanan /
              asgari / hedef), (3) bagimsiz dogrulayicinin ozeti (kural
              basina ihlal sayisi, yayin kapisi, sert ihlaller), (4) kosu
              kunyesi. Bagimliligi yok, tarayicida acilir.

KAPSAMA IZGARASI YAKLASIKTIR ve kural sayimi DEGILDIR: hucreye "atanan",
vardiyasi o saati kapsayan kisi sayisidir -- molalar DUSULMEZ (HEDEF_KAPSAMA /
ASGARI_KAPSAMA'nin `_atanmis` sayimi), cok ekipli sayim YALNIZ atamanin ekibi
(K-50'nin "hepsi" modu burada uygulanmaz). Kural ihlali bagimsiz
dogrulayicinindir (dogrulayici/kurallar.py); bu sayfa goz icindir.

Saat gosterimi: genisletilmis saat (#11.2) okunur saate cevrilir; 24'u asan
saat ertesi gunu belirtir ("07:00+1"). Gun indeksi 0 = Pazartesi.

Kullanim:
  python cizelge.py planlar/<klasor>/<ad>.json   -> yanina <ad>.html (yeniden uretir)
  kalite-olc.py her kosudan sonra `plan_kaydet` cagirir (--plansiz ile kapanir).
"""
import io
import json
import os
import sys

GUNLER = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"]
GUNLER_UZUN = ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"]


def saat_yaz(h):
    """Genisletilmis saat -> 'SS:DD'; 24'u asan saat '+1' alir. 16.25 -> '16:15', 31 -> '07:00+1'."""
    h = float(h)
    gun = 0
    while h >= 24.0:
        h -= 24.0
        gun += 1
    dakika = int(round(h * 60))
    s = "%02d:%02d" % (dakika // 60, dakika % 60)
    return s + ("+%d" % gun if gun else "")


def brut_saat(a):
    return float(a["bit"]) - float(a["bas"])


def net_saat(a):
    """Calisma suresi: BUTUN molalar dusulmus (K-57; dogrulayici/zaman.net_saat ile ayni tanim,
    ayrica yazili -- #7.6)."""
    return brut_saat(a) - sum(float(m.get("bit", 0)) - float(m.get("bas", 0))
                              for m in (a.get("molalar") or []))


def kisi_gun_tablosu(girdi, atamalar):
    """Satir basina bir calisan: {'id', 'ekipler', 'tip', 'gunler': {gun: [atama, ...]},
    'brut', 'net', 'gun_sayisi'}. Siralama: ilk ekip, sonra kimlik. Hic atamasi
    olmayan calisan da satirdadir (bos hafta gorunsun)."""
    satirlar = {}
    for c in girdi.get("calisanlar", []) or []:
        satirlar[c["id"]] = {"id": c["id"], "ekipler": list(c.get("ekipler") or []),
                             "tip": (c.get("sozlesme") or {}).get("tip", "?"),
                             "gunler": {}, "brut": 0.0, "net": 0.0, "gun_sayisi": 0}
    for a in atamalar or []:
        s = satirlar.setdefault(a["calisan"], {"id": a["calisan"], "ekipler": [], "tip": "?",
                                               "gunler": {}, "brut": 0.0, "net": 0.0, "gun_sayisi": 0})
        s["gunler"].setdefault(int(a["gun"]), []).append(a)
        s["brut"] += brut_saat(a)
        s["net"] += net_saat(a)
    for s in satirlar.values():
        s["gun_sayisi"] = len(s["gunler"])
        for liste in s["gunler"].values():
            liste.sort(key=lambda x: float(x["bas"]))
    return sorted(satirlar.values(), key=lambda s: ((s["ekipler"] or ["~"])[0], s["id"]))


def kapsama_tablosu(girdi, atamalar):
    """(ekip, gun) -> 24 hucre: {'saat', 'atanan', 'asgari', 'hedef'}.
    Talep satiri olmayan saat de yazilir (asgari/hedef None). Atanan: vardiyasi
    o saati kapsayan (bas <= saat < bit, genisletilmis) atamalar -- molalar
    dusulmez, yalniz atamanin ekibi sayilir (bkz. modul notu). Gece yarisini
    asan vardiya ertesi gunun saatlerine de sayilir."""
    talep = {}
    for t in girdi.get("talep", []) or []:
        talep[(t.get("ekip"), int(t["gun"]), int(t["saat"]))] = t
    ekipler = sorted({t.get("ekip") for t in girdi.get("talep", []) or []}
                     | {a.get("ekip") for a in atamalar or []}, key=lambda e: str(e))
    gunler = sorted({int(t["gun"]) for t in girdi.get("talep", []) or []}
                    | {int(a["gun"]) for a in atamalar or []})
    sayac = {}
    for a in atamalar or []:
        bas, bit = float(a["bas"]), float(a["bit"])
        h = int(bas)
        while h < bit:
            gun, saat = int(a["gun"]) + h // 24, h % 24
            anahtar = (a.get("ekip"), gun, saat)
            sayac[anahtar] = sayac.get(anahtar, 0) + 1
            h += 1
    gunler = sorted(set(gunler) | {g for _, g, _ in sayac})      # tasan gece ertesi gunu de acar
    cikan = {}
    for e in ekipler:
        for g in gunler:
            cikan[(e, g)] = [{"saat": s, "atanan": sayac.get((e, g, s), 0),
                              "asgari": (talep.get((e, g, s)) or {}).get("asgari"),
                              "hedef": (talep.get((e, g, s)) or {}).get("hedef")}
                             for s in range(24)]
    return cikan


def _k(s):
    """HTML kacis."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


_STIL = """
body{font-family:Segoe UI,Arial,sans-serif;font-size:12px;margin:16px;color:#111}
h1{font-size:18px;margin:0 0 4px} h2{font-size:15px;margin:22px 0 6px}
.meta{color:#333;margin-bottom:10px} .meta b{color:#000}
table{border-collapse:collapse} th,td{border:1px solid #bbb;padding:2px 5px;vertical-align:top}
th{background:#eee;position:sticky;top:0} td.bos{color:#bbb;text-align:center}
td.v{white-space:nowrap} .mola{color:#666;font-size:10px} .ekip{color:#555;font-size:10px}
tr.ekipbasi td{border-top:2px solid #777}
.kap td{text-align:center;min-width:26px;padding:1px 3px;font-size:11px}
.eksik{background:#f8d0d0} .fazla{background:#d6e4f7} .tam{background:#e3f2e3} .yok{color:#bbb}
.not{color:#555;font-size:11px;margin:4px 0 10px}
"""


def _kunye(cikti, dogrulama, kayit):
    """HTML basligindaki kunye satiri: kayit + motor istatistikleri + dogrulayici metrikleri."""
    ist = (cikti or {}).get("cozum_istatistikleri") or {}
    mm = (cikti or {}).get("metrikler") or {}
    dm = (dogrulama or {}).get("metrikler") or {}
    kapi = (dogrulama or {}).get("yayin_kapisi") or {}
    m = []
    for ad, deger in (("yapilandirma", (kayit or {}).get("yapilandirma")),
                      ("tekrar", (kayit or {}).get("tekrar")),
                      ("arama", ("%s sn" % (kayit or {}).get("saniye")) if (kayit or {}).get("saniye") else None),
                      ("durum", (cikti or {}).get("durum")),
                      ("durma sebebi", ist.get("durma_sebebi")),
                      ("amac", ist.get("amac_degeri")),
                      ("sert ihlal (dogrulayici)", dm.get("sert_ihlal")),
                      ("yumusak ihlal", dm.get("yumusak_ihlal")),
                      ("yayinlanabilir", kapi.get("yayinlanabilir")),
                      ("hedef kapsama %", dm.get("hedef_kapsama_yuzde", mm.get("hedef_kapsama_yuzde"))),
                      ("fazla mesai saat (dogrulayici)", dm.get("fazla_mesai_saat")),
                      ("toplam saat", dm.get("toplam_saat", mm.get("toplam_saat"))),
                      ("tarih", (kayit or {}).get("tarih")),
                      ("motor", (cikti or {}).get("motor_surumu"))):
        if deger is not None:
            m.append("<b>%s</b>: %s" % (_k(ad), _k(deger)))
    return " &middot; ".join(m)


def cizelge_html(girdi, cikti, dogrulama=None, kayit=None):
    """Okunur cizelge. `cikti` motorun /solve cevabi (atamalar burada), `dogrulama`
    bagimsiz dogrulayicinin raporu (olmayabilir), `kayit` kosu kunyesi."""
    cikti = cikti or {}
    atamalar = cikti.get("atamalar") or []
    kayit = dict(kayit or {})
    baslik = kayit.get("baslik") or "Cizelge"
    satirlar = kisi_gun_tablosu(girdi, atamalar)
    kapsama = kapsama_tablosu(girdi, atamalar)
    gunler = sorted({g for s in satirlar for g in s["gunler"]} | {g for _, g in kapsama}) or list(range(7))
    h = ["<!doctype html><html lang='tr'><head><meta charset='utf-8'>",
         "<title>%s</title><style>%s</style></head><body>" % (_k(baslik), _STIL),
         "<h1>%s</h1>" % _k(baslik)]
    h.append("<div class='meta'>%s</div>" % _kunye(cikti, dogrulama, kayit))
    h.append("<div class='not'>Kisi &times; gun tablosu: hucrede vardiya saati (baslangic&ndash;bitis; +1 = ertesi gun), "
             "ekip ve molalar (y = yemek, d = dinlenme). Satir sonu: calisilan gun, brut saat, net saat "
             "(butun molalar dusulmus, K-57). Kapsama izgarasi YAKLASIKTIR (molalar dusulmez, yalniz "
             "atamanin ekibi sayilir); kural sayimi bagimsiz dogrulayicinindir.</div>")
    # --- kisi x gun
    h.append("<h2>1 &middot; Kisi &times; gun (%d calisan, %d atama)</h2>" % (len(satirlar), len(atamalar or [])))
    h.append("<table><tr><th>Calisan</th><th>Ekip</th><th>Tip</th>" +
             "".join("<th>%s</th>" % GUNLER[g % 7] + ("" if g < 7 else "+%d" % (g // 7)) for g in gunler) +
             "<th>Gun</th><th>Brut</th><th>Net</th></tr>")
    onceki_ekip = None
    for s in satirlar:
        ekip = (s["ekipler"] or ["-"])[0]
        sinif = " class='ekipbasi'" if onceki_ekip is not None and ekip != onceki_ekip else ""
        onceki_ekip = ekip
        hucreler = []
        for g in gunler:
            liste = s["gunler"].get(g)
            if not liste:
                hucreler.append("<td class='bos'>&middot;</td>")
                continue
            parca = []
            for a in liste:
                molalar = " ".join("%s%s" % ("y" if mm.get("tip") == "yemek" else "d", saat_yaz(mm["bas"]))
                                   for mm in (a.get("molalar") or []))
                parca.append("<div class='v'>%s&ndash;%s</div><div class='ekip'>%s%s</div>%s"
                             % (saat_yaz(a["bas"]), saat_yaz(a["bit"]), _k(a.get("ekip") or ""),
                                " (donmus)" if a.get("donmus") else "",
                                ("<div class='mola'>%s</div>" % _k(molalar)) if molalar else ""))
            hucreler.append("<td>%s</td>" % "".join(parca))
        h.append("<tr%s><td>%s</td><td>%s</td><td>%s</td>%s<td>%d</td><td>%.2f</td><td>%.2f</td></tr>"
                 % (sinif, _k(s["id"]), _k(", ".join(s["ekipler"])), _k(s["tip"]), "".join(hucreler),
                    s["gun_sayisi"], s["brut"], s["net"]))
    h.append("</table>")
    # --- kapsama
    h.append("<h2>2 &middot; Kapsama izgarasi (atanan / asgari / hedef)</h2>")
    h.append("<div class='not'>Hucre: atanan kisi; altinda asgari&ndash;hedef. Kirmizi: hedefin altinda "
             "(asgarinin alti da ayni renk -- sayiya bak). Mavi: hedefin ustunde. Yesil: tam hedef. "
             "Talep satiri yok: soluk.</div>")
    for (e, g), hucreler in sorted(kapsama.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        if g >= 7:
            continue
        h.append("<div><b>%s &middot; %s</b></div>" % (_k(e), GUNLER_UZUN[g % 7]))
        h.append("<table class='kap'><tr>" + "".join("<th>%02d</th>" % c["saat"] for c in hucreler) + "</tr><tr>")
        for c in hucreler:
            if c["hedef"] is None and c["asgari"] is None:
                h.append("<td class='yok'>%d</td>" % c["atanan"] if c["atanan"] else "<td class='yok'>&middot;</td>")
                continue
            hedef = c["hedef"] if c["hedef"] is not None else c["asgari"]
            sinif = "tam" if c["atanan"] == hedef else ("eksik" if c["atanan"] < hedef else "fazla")
            h.append("<td class='%s'>%d<br><span class='ekip'>%s&ndash;%s</span></td>"
                     % (sinif, c["atanan"], c["asgari"] if c["asgari"] is not None else "",
                        c["hedef"] if c["hedef"] is not None else ""))
        h.append("</tr></table>")
    # --- dogrulayici ozeti
    if dogrulama:
        ihlaller = dogrulama.get("ihlaller") or []
        sayi = {}
        for i in ihlaller:
            anahtar = (i.get("kural"), i.get("agirlik"))
            sayi[anahtar] = sayi.get(anahtar, 0) + 1
        h.append("<h2>3 &middot; Bagimsiz dogrulayici (%d ihlal satiri)</h2>" % len(ihlaller))
        h.append("<table><tr><th>Kural</th><th>Tur</th><th>Satir</th></tr>" +
                 "".join("<tr><td>%s</td><td>%s</td><td>%d</td></tr>" % (_k(k), _k(t), n)
                         for (k, t), n in sorted(sayi.items(), key=lambda kv: (-kv[1], str(kv[0])))) +
                 "</table>")
        kapi = dogrulama.get("yayin_kapisi") or {}
        h.append("<div class='not'>Yayin kapisi: %s &middot; uygulanmayan kurallar: %s &middot; "
                 "denetlenemeyen: %s &middot; gecmis (donmus gune ait) ihlal: %d</div>"
                 % (_k(kapi.get("yayinlanabilir")), _k(", ".join(dogrulama.get("uygulanmayan_kurallar") or []) or "yok"),
                    len(kapi.get("denetlenemeyen_kurallar") or []), len(dogrulama.get("gecmis_ihlaller") or [])))
        sert = [i for i in ihlaller if i.get("agirlik") == "SERT"]
        if sert:
            h.append("<table><tr><th>Sert ihlal</th><th>Calisan</th><th>Gun</th><th>Mesaj</th></tr>" +
                     "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                             % (_k(i.get("kural")), _k(i.get("calisan", "")), _k(i.get("gun", "")), _k(i.get("mesaj", "")))
                             for i in sert[:200]) + "</table>")
            if len(sert) > 200:
                h.append("<div class='not'>... %d sert ihlal daha (json'da)</div>" % (len(sert) - 200))
    # --- kunye
    if kayit:
        h.append("<h2>4 &middot; Kosu kunyesi</h2><table>" +
                 "".join("<tr><td>%s</td><td>%s</td></tr>" % (_k(a), _k(v)) for a, v in sorted(kayit.items())
                         if a != "baslik") + "</table>")
    h.append("</body></html>")
    return "\n".join(h)


def girdi_ozeti(girdi, sure_butcesi_sn=None):
    """#8.6 plan_runs.girdi_ozeti ruhunda: kac kisi, kac hucre, kac kural, donmus gunler."""
    return {"kisi": len(girdi.get("calisanlar", []) or []),
            "hucre": len(girdi.get("talep", []) or []),
            "kural": len(girdi.get("kurallar", []) or []),
            "sablon": len(girdi.get("vardiya_sablonlari", []) or []),
            "hafta_baslangic": girdi.get("hafta_baslangic"),
            "profil": girdi.get("profil"),
            "donmus_gunler": list(girdi.get("donmus_gunler") or []),
            "sure_butcesi_sn": sure_butcesi_sn if sure_butcesi_sn is not None else girdi.get("sure_butcesi_sn")}


def plan_kaydet(klasor, ad, girdi, cikti, dogrulama=None, kayit=None):
    """<klasor>/<ad>.json (urun bicimi) ve <ad>.html (okunur) yazar; (json_yolu, html_yolu) doner.

    `cikti`: motorun /solve cevabi (#11.3). `dogrulama`: dogrulayici.degerlendir raporu (#11.4);
    verilirse `cikti.bagimsiz_denetim` servis.py/orkestra ile ayni ozetle doldurulur (yoksa
    dokunulmaz). Alan adlari degistirilmez, eklenmez: dosya urun ciktisinin kendisidir.
    """
    if not os.path.isdir(klasor):
        os.makedirs(klasor)
    cikti = dict(cikti or {})
    kayit = dict(kayit or {})
    kayit.setdefault("baslik", ad)
    kayit.setdefault("bicim", "tshift-plan-kaydi/1")
    if dogrulama is not None and "bagimsiz_denetim" not in cikti:
        sert = [i for i in (dogrulama.get("ihlaller") or [])
                if i.get("agirlik") == "SERT" and not i.get("gecmis")]
        cikti["bagimsiz_denetim"] = {           # orkestra._denetim_ozeti ile ayni alanlar
            "sert_ihlal": len(sert),
            "yumusak_ihlal": (dogrulama.get("metrikler") or {}).get("yumusak_ihlal"),
            "ihlaller": sert,
            "uygulanmayan_kurallar": dogrulama.get("uygulanmayan_kurallar"),
            "eksik_boyutlar": dogrulama.get("eksik_boyutlar"),
            "gecmis_ihlaller": dogrulama.get("gecmis_ihlaller", []),
            "yayin_kapisi": dogrulama.get("yayin_kapisi"),
        }
    json_yolu = os.path.join(klasor, ad + ".json")
    html_yolu = os.path.join(klasor, ad + ".html")
    with io.open(json_yolu, "w", encoding="utf-8") as f:
        f.write(json.dumps({"kayit": kayit, "girdi_ozeti": girdi_ozeti(girdi, kayit.get("saniye")),
                            "cikti": cikti, "dogrulama": dogrulama},
                           ensure_ascii=False, indent=1))
    with io.open(html_yolu, "w", encoding="utf-8") as f:
        f.write(cizelge_html(girdi, cikti, dogrulama, kayit))
    return json_yolu, html_yolu


def _sahneyi_bul(meta):
    """Plan dosyasindan HTML'i yeniden uretmek icin sahne: meta['sahne'] (dosya yolu) ya da
    uret_veri_seti ile ayni olcek/doluluk."""
    sahne = meta.get("sahne")
    if sahne and os.path.exists(sahne):
        return json.load(io.open(sahne, encoding="utf-8"))
    burasi = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, burasi)
    from uret_veri_seti import sahne_uret
    return sahne_uret(float(meta.get("olcek", 1.0)), float(meta.get("doluluk", 0.95)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    yol = sys.argv[1]
    d = json.load(io.open(yol, encoding="utf-8"))
    kayit = d.get("kayit") or {}
    g = _sahneyi_bul(kayit)
    cikti = os.path.splitext(yol)[0] + ".html"
    with io.open(cikti, "w", encoding="utf-8") as f:
        f.write(cizelge_html(g, d.get("cikti") or {}, d.get("dogrulama"), kayit))
    print("yazildi:", cikti)
