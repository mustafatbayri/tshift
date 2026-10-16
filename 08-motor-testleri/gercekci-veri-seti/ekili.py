# -*- coding: utf-8 -*-
"""
EKILI SAHNE -- bilinen TANIK planli olcum sahnesi (16 Ekim; oturum 14 Ekim §18, A1)

NEDEN
  Bugune kadarki butun kalite olcumleri "referansa gore"ydi ve referans AYNI
  motorun baska tohumla, sert kesimle kostugu plan (K-62 ilke 1). Bu dongusel:
  agirliklar ya da arama yanlissa referans da yanlis yerde durur; "referanstan
  %20 iyi" cumlesi "kendi kendimizden iyi" demektir. Mustafa 16 Ekim 01:54:
  "Ben hala bu optimum ... suphelere sahibim."

  Ekili sahne bu donguyu kirar: once motorun ARAMASI kullanilmadan, DESENLI
  bir cozucuyle gecerli bir plan (TANIK) bulunur; talep ONDAN turetilir. Boylece
  tanigin su kalemleri KURULUS GEREGI sifirdir:
    HEDEF_KAPSAMA, HEDEF_ASIMI   hedef = tanikta o saate sayilan kisi
    MOLA_KAPSAMASI               asgari = tanikta o saatin en kotu ceyreginde sahadaki kisi
    FAZLA_MESAI                  tanik aranirken fm alanlari [0,0]
    TERCIH_KARSILAMA             yari zamanlinin sozlesme saati = tanikta calistigi saat
  Geri kalan kalemler (ADALET_DENGESI, EKIP_SUREKLILIGI, MOLA_YERLESIMI, ...)
  tanikta OLCULUR ve TANIK PUANI yazilir. Bu sahnede:
    * fazla mesaisiz, asimsiz, eksiksiz bir plan KESIN vardir (tanik);
      motor fazla mesaili plan veriyorsa bu veri imkansizligi degil ARAMA
      zaafidir (15 Ekim 500 kisi bulgusunun ayirici testi);
    * gercek optimum <= tanik puani; motorun plani tanigin ALTINA inmeli.
      Inemiyorsa fark kalem kalem okunur (kalite-olc OPTIMUM HESABI / REFERANS
      KIYASI) ve bu fark motorun KENDI referansina degil disaridan kurulmus bir
      plana gore acigidir -- optimuma uzakligin ALT siniri.

TANIK NASIL BULUNUR -- "desen cozucu"
  Motorun iki asamali aramasi, ipuclari, gevsek yolu, onarimi KULLANILMAZ.
  Tabanin modeli (cozucu.model.Model: sert kurallarin tamami, ceza terimleri)
  aynen kurulur, ustune iki DESEN kisidi gelir:
    (1) her kisi haftada EN COK `DESEN_UST` (2) sablon kullanir (gunler
        serbest) -- arama uzayi cok kuculur. Tek sablon istenirdi (rotasyon 0)
        ama 25 ve 49 kiside COZUMSUZ: ROL/YETKINLIK_KAPSAMASI her gun 08-19
        lider/ingilizce ister, tek sablonlu kisi gunu kapatamaz (16 Ekim olcumu);
    (2) fazla mesai alanlari [0,0] (kimse sozlesme saatini asamaz).
  Talep tabanin talebidir ama `asgari` 0'a cekilir ve HEDEF_ASIMI YUMUSAK
  (desenli arama tutturamayacagi sert asgariyle cozumsuz kalmasin; tanigin
  sahada biraktigi kisi zaten yeni asgari olur). Amac: modelin kendi ceza
  toplami (puan tanimi motorunkiyle AYNI olmali ki tanik puani motorun
  puanlariyla kiyaslanabilsin). Tek CP-SAT cagrisi, verilen sure; bulunan en
  iyi plan tanik olur. Kilitler, gecmis, devir, izinler, uygunluk AYNEN kalir
  (tanik da onlara uyar).

  Gecerlilik motorun degil DOGRULAYICININ sozudur: tanik turetilmis sahnede
  `merdiven.referans_denetle` ile denetlenir (sert 0, asim 0, eksik 0, fm 0) ve
  `merdiven.plan_puani` ile puanlanir; sifir olmasi gereken bes kalem sifir
  degilse uretim DURUR (sessiz kabul yok).

DOSYALAR (merdiven kaynak "ekili" / "ekili-veri-seti"; eki -EK / -EK-VS2)
  fikstur/_sahne-L1-EK[-VS2]-95[-olcek].json    sahne (referans_puani = tanik puani)
  fikstur/_referans-L1-EK[-VS2]-95[-olcek].json tanik: {"atamalar", "kayit"}
  kalite-olc: py kalite-olc.py --seviye 1 --kaynak ekili --olcek 0.1 --saniye 600 --tekrar 3

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\08-motor-testleri\\gercekci-veri-seti
  py ekili.py --olcek 0.1 --saniye 120            (uretec tabani; --desen 2 varsayilan)
  py ekili.py --olcek 1.0 --saniye 600 --taban veri-seti
"""

import copy
import io
import json
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.join(os.path.dirname(os.path.dirname(BURASI)), "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import merdiven as MD                                          # noqa: E402

SIFIR_KALEMLER = ("HEDEF_KAPSAMA", "HEDEF_ASIMI", "MOLA_KAPSAMASI", "FAZLA_MESAI", "TERCIH_KARSILAMA")
TABANLAR = {"uretec": "ekili", "veri-seti": "ekili-veri-seti"}   # taban kaynagi -> merdiven kaynagi


def arama_sahnesi(taban):
    """Tanik aramasinin sahnesi: taban aynen, `asgari` 0, HEDEF_ASIMI YUMUSAK.
    Hedef DEGISMEZ -- tanik tabanin talebini kovalar ki turetilen sahne tabana
    benzesin (kapatilan saat, bos hucre az)."""
    g = copy.deepcopy(taban)
    for t in g["talep"]:
        t["asgari"] = 0
        t.pop("_sahada_taban", None)
    for k in g["kurallar"]:
        if k["kod"] == "HEDEF_ASIMI":
            k["tur"] = "YUMUSAK"
    return g


DESEN_UST = 2   # 16 Ekim olcumu: 1 sablon/kisi 25 ve 49 kiside COZUMSUZ (ROL/YETKINLIK_KAPSAMASI
                # 08-19 her gun: tek sablonlu lider gunu kapatamaz); 2 sablon 49 kiside 90 sn'de plan.


def desen_kisitlari(k, ust=DESEN_UST):
    """Her kisi haftada en cok `ust` sablon: u[e,t] >= x[e,d,t], sum_t u[e,t] <= ust.
    Donen: eklenen desen degiskeni sayisi."""
    sablon_kullanimi = {}
    for (e, d, t), v in k.x.items():
        sablon_kullanimi.setdefault(e, {}).setdefault(t, []).append(v)
    sayac = 0
    for e, sablonlar in sorted(sablon_kullanimi.items()):
        kullanilan = []
        for t, xs in sorted(sablonlar.items()):
            u = k.m.NewBoolVar("desen_%s_%s" % (e, t))
            for v in xs:
                k.m.Add(v <= u)
            kullanilan.append(u)
            sayac += 1
        k.m.Add(sum(kullanilan) <= int(ust))
    return sayac


def tanik_ara(taban, saniye=120, tohum=11, isci=None, desen_ust=DESEN_UST):
    """Desen cozucu. Donen (atamalar | None, bilgi)."""
    from ortools.sat.python import cp_model
    from cozucu.model import Model
    from cozucu.coz import _fazla_mesaiyi_sifirla, _fazla_mesaiyi_serbest_birak, _atamalari_cikar
    k = Model(arama_sahnesi(taban)).kur()
    desen = desen_kisitlari(k, desen_ust)
    eski = _fazla_mesaiyi_sifirla(k)
    k.m.Minimize(sum(a * v for a, v in k.cezalar))
    c = cp_model.CpSolver()
    c.parameters.max_time_in_seconds = float(saniye)
    c.parameters.num_search_workers = int(isci or os.cpu_count() or 1)
    c.parameters.random_seed = int(tohum)
    t0 = time.time()
    try:
        durum = c.Solve(k.m)
    finally:
        _fazla_mesaiyi_serbest_birak(k, eski)
    bilgi = {"durum": c.StatusName(durum), "saniye": round(time.time() - t0, 1), "tohum": int(tohum),
             "butce_saniye": int(saniye), "desen_ust": int(desen_ust), "desen_degiskeni": desen, "fm_alani_sifirlanan": len(eski),
             "degisken": len(k.m.Proto().variables), "isci": c.parameters.num_search_workers}
    if durum not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, bilgi
    bilgi["arama_amaci"] = int(round(c.ObjectiveValue()))
    bilgi["arama_alt_siniri"] = int(round(c.BestObjectiveBound()))
    return _atamalari_cikar(k, c), bilgi


def ceyrek_sahada(g, atamalar):
    """(ekip, gun, saat) -> o saatin DORT ceyreginde sahada (molada olmayan)
    kisinin EN AZI -- dogrulayicinin MOLA_KAPSAMASI olcusuyle AYNI fonksiyonlar
    (ekibe_sayilir, _kapsama_atamalari, zaman.sahada_mi, CEYREK)."""
    from dogrulayici import kurallar as KR, zaman
    uyelik, mod = KR.uyelik_haritasi(g), KR.cok_ekipli_sayim(g)
    atamalar = KR._kapsama_atamalari(g, atamalar)
    cikan = {}
    for t, gun, saat in KR._talep_hucreleri(g):
        en_az = None
        for ceyrek in range(KR.CEYREK):
            an = saat + ceyrek / float(KR.CEYREK)
            sahada = sum(1 for a in atamalar
                         if KR.ekibe_sayilir(a, t.get("ekip"), uyelik, mod) and zaman.sahada_mi(a, gun, an))
            en_az = sahada if en_az is None else min(en_az, sahada)
        cikan[(t.get("ekip"), gun, saat)] = en_az or 0
    return cikan


def ekili_sahne(taban, tanik):
    """Talep taniktan: hedef = sayilan kisi (merdiven.hucre_sayimi, dogrulayicinin
    sayimi), asgari = en kotu ceyrekte sahadaki kisi (<= hedef), _sahada_taban =
    asgari; yari zamanli sozlesme saati = tanikta calistigi saat (ceyrek saate
    yuvarli; 0 ise alan kalkar); HEDEF_ASIMI SERT (K-67)."""
    from dogrulayici import zaman
    g = copy.deepcopy(taban)
    hedef = MD.hucre_sayimi(taban, tanik)
    sahada = ceyrek_sahada(taban, tanik)
    for t in g["talep"]:
        h = (t["ekip"], t["gun"], t["saat"])
        t["hedef"] = int(hedef.get(h, 0) or 0)
        t["asgari"] = min(int(sahada.get(h, 0)), t["hedef"])
        t["_sahada_taban"] = t["asgari"]
    saat = {}
    for a in tanik:
        saat[a["calisan"]] = saat.get(a["calisan"], 0.0) + zaman.net_saat(a)
    for c in g["calisanlar"]:
        soz = c.get("sozlesme") or {}
        if soz.get("tip") == "yari_zamanli":
            s = round(saat.get(c["id"], 0.0) * 4) / 4.0
            if s > 0:
                soz["haftalik_saat"] = s
            else:
                soz.pop("haftalik_saat", None)
            c["sozlesme"] = soz
    for k in g["kurallar"]:
        if k["kod"] == "HEDEF_ASIMI":
            k["tur"] = "SERT"
    g["_merdiven"] = dict(taban.get("_merdiven") or {}, seviye="1-ekili",
                          hedef_kisi_saat=sum(t["hedef"] for t in g["talep"]),
                          asgari_kisi_saat=sum(t["asgari"] for t in g["talep"]))
    g["_hedef_kisi_saat"] = g["_merdiven"]["hedef_kisi_saat"]
    return g


def ekili_uret(olcek, saniye=120, tohum=11, taban_kaynagi="uretec", isci=None, desen_ust=DESEN_UST):
    """Taban -> tanik -> ekili sahne -> dogrulayici denetimi -> tanik puani.
    Donen (sahne, referans). Sart tutmazsa SystemExit (sessiz kabul yok)."""
    if taban_kaynagi not in TABANLAR:
        raise SystemExit("bilinmeyen taban %s (olanlar: %s)" % (taban_kaynagi, ", ".join(TABANLAR)))
    taban = MD.taban_sahne(olcek, taban_kaynagi)
    t0 = time.time()
    tanik, bilgi = tanik_ara(taban, saniye, tohum, isci, desen_ust)
    if tanik is None:
        raise SystemExit("TANIK BULUNAMADI (desen cozucu %s): %s" % (bilgi.get("durum"), bilgi))
    g = ekili_sahne(taban, tanik)
    d = MD.referans_denetle(g, tanik)
    if d["sert"] or d["asim"] or d["eksik"] or d["fazla_mesai_saat"]:
        raise SystemExit("TANIK EKILI SAHNEDE TUTARSIZ: %s" % d)
    p = MD.plan_puani(g, tanik)
    if not p or p.get("durum") != "OPTIMAL":
        raise SystemExit("TANIK PUANI HESAPLANAMADI: %s" % p)
    bozuk = {kod: p["dagilim"][kod] for kod in SIFIR_KALEMLER if p["dagilim"].get(kod, {}).get("ceza", 0)}
    if bozuk:
        raise SystemExit("TANIKTA SIFIR OLMASI GEREKEN KALEM SIFIR DEGIL: %s" % bozuk)
    g["_merdiven"]["referans_puani"] = p
    g["_merdiven"]["kaynak"] = ("ekili: tanik desen cozucuden (en cok %d sablon/kisi, fm 0, tohum %d, %d sn), talep taniktan"
                               % (int(desen_ust), int(tohum), int(saniye)))
    kayit = dict(bilgi, olcek=olcek, doluluk=MD.DOLULUK, taban=taban_kaynagi, kaynak=TABANLAR[taban_kaynagi],
                 sure_sn=round(time.time() - t0, 1), tarih=time.strftime("%Y-%m-%d %H:%M"),
                 cekirdek=os.cpu_count(), makine=os.environ.get("COMPUTERNAME") or "bulut",
                 kisi=len(g["calisanlar"]), atama=len(tanik),
                 hedef_kisi_saat=g["_merdiven"]["hedef_kisi_saat"], asgari_kisi_saat=g["_merdiven"]["asgari_kisi_saat"],
                 taban_hedef_kisi_saat=sum(int(t.get("hedef") or 0) for t in taban["talep"]),
                 amac_degeri=p["amac"], amac_dagilimi=p["dagilim"], tabanda_denetim=d,
                 fazla_mesai_saat=0.0, fazla_mesaisiz_kanitli_yok=False,
                 yol="desen cozucu: Model + her kisi en cok %d sablon + fm [0,0]; amac modelin ceza toplami; tek CP-SAT cagrisi" % int(desen_ust),
                 **{"not": ("Tanik gercek optimum DEGIL, ust sinirdir: bu sahnede en az tanik kadar iyi plan vardir ve "
                            "fazla mesaisiz/asimsiz/eksiksiz plan KESIN vardir. Motor tanigin ustunde kaliyorsa fark "
                            "motorun kendi referansina degil disaridan kurulmus plana gore acigidir.")})
    return g, {"atamalar": tanik, "kayit": kayit}


def _arg(ad, varsayilan, tur=str):
    return tur(sys.argv[sys.argv.index(ad) + 1]) if ad in sys.argv else varsayilan


if __name__ == "__main__":
    olcek = _arg("--olcek", 0.1, float)
    taban_kaynagi = _arg("--taban", "uretec")
    g, ref = ekili_uret(olcek, _arg("--saniye", 120, int), _arg("--tohum", 11, int), taban_kaynagi,
                        _arg("--isci", None, int), _arg("--desen", DESEN_UST, int))
    kaynak = TABANLAR[taban_kaynagi]
    MD._yaz(MD.referans_yolu(olcek, kaynak), ref)
    MD._yaz(MD.sahne_yolu(olcek, kaynak), g)
    k, p = ref["kayit"], g["_merdiven"]["referans_puani"]
    print("EKILI SAHNE yazildi: %s" % os.path.basename(MD.sahne_yolu(olcek, kaynak)))
    print("TANIK yazildi      : %s" % os.path.basename(MD.referans_yolu(olcek, kaynak)))
    print("  %d kisi | tanik %d atama | desen cozucu %s, %s sn (arama amaci %s, alt sinir %s) | toplam %.0f sn"
          % (k["kisi"], k["atama"], k["durum"], k["saniye"], k.get("arama_amaci"), k.get("arama_alt_siniri"), k["sure_sn"]))
    print("  hedef %d kisi-saat (taban %d), asgari %d | ekili sahnede denetim %s"
          % (k["hedef_kisi_saat"], k["taban_hedef_kisi_saat"], k["asgari_kisi_saat"], k["tabanda_denetim"]))
    print("  TANIK PUANI %d  %s" % (p["amac"], {kod: d["ceza"] for kod, d in sorted(p["dagilim"].items()) if d["ceza"]}))
