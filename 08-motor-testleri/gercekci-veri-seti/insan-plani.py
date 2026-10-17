# -*- coding: utf-8 -*-
"""
INSAN PLANI SAHNESI -- gercek musterinin ELLE yaptigi haftalik plan, motorun cetveli (16 Ekim; A3)

NEDEN
  Tanikli sahne (ekili.py) motordan bagimsiz ama yine bir ALGORITMANIN planidir.
  Elimizde daha iyisi var: musterinin (06-veri/ham/plan, 69 Excel, 15 hafta,
  haftada 58-83 kisi) planlamacilarinin ELLE yaptigi planlar. Mustafa 16 Ekim
  17:26: "Sana daha once attigim ... plan verileri isine yaramiyor mu?" -- yarar:
  bu, "motor gercek bir planlamacidan iyi mi?" sorusunun dogrudan olcusu.

NE YAPAR (bir hafta secilir; `--hafta 2026-06-22`, Pazartesi)
  1. 07-gercek-veri-analizi/donusturucu.py'nin kanonik tablosunu okur
     (06-veri/kanonik/plan.csv; git DISI, isim icerir).
  2. ANONIM motor girdisi kurar: kisi -> I001.. (esleme yalniz 06-veri/anonim
     altinda, git disi), takim -> ekip kodu, "Takim Lideri" -> operasyonel_rol,
     o haftanin izin kodlari -> onayli izin, sozlesme saati = insan planindaki net
     saat (<= 45; ustu musterinin ihlalidir), o haftada kullanilan her
     (takim, vardiya deseni) -> sablon (mola politikasi vardiya uzunlugundan).
  3. Insan planini motor bicimine cevirir (molalar VARSAYILAN yerlestirilir:
     musteri plani mola yazmaz; yemek bas+4 sa (60 dk; 7,5 sa alti 30 dk),
     dinlenme 15 dk) ve TALEBI ONDAN turetir -- ekili.ekili_sahne ile ayni yontem:
     hedef = o saatte sayilan kisi, asgari = en kotu ceyrekte sahadaki kisi,
     HEDEF_ASIMI SERT. Boylece motor, planlamacinin KAPATTIGI isi kapatmak zorunda.
  4. Insan planini DOGRULAYICIDAN gecirir: sert ihlaller kural kural (gercek planda
     529 ihlal bulunmustu -- 07-GERCEK-VERI-BULGULARI), fazla mesai, metrikler.
  5. Yazar (06-veri/anonim/insan/): _sahne-INSAN-<hafta>.json,
     _referans-INSAN-<hafta>.json (insan plani + rapor), esleme-<hafta>.json.
  `--puan` (ortools gerekir; Windows'ta `py`): insan planinin motor olcusuyle puani
     (merdiven.plan_puani) sahneye yazilir; sert ihlalli plan modele oturmaz ->
     puan yerine {"durum": "INFEASIBLE", ...} ve kalite-olc kiyasi yalniz kalemlerle.

OLCUM
  py kalite-olc.py --sahne ..\\..\\06-veri\\anonim\\insan\\_sahne-INSAN-2026-06-22.json --saniye 1800 --tekrar 3 --etiket insan-1800
  Okunacak: motor sert 0 mi (insan: N ihlal), fazla mesai (insan: X sa), kapsama (ayni,
  kurulus geregi), adalet / rotasyon / mola kalemleri.

SINIR -- bu sahne planlamacinin GIRDISI degil CIKTISINDAN geri kurulur (Mustafa 16 Ekim 22:40)
  Bilinmeyenler ve yerine konan varsayimlar: sozlesme saati (-> plandaki net saat), talep
  (-> plandaki saat basi kisi; Erlang-C ihtiyaci bilinmiyor), kurallar (-> bizim katalog;
  planlamacinin ic kurallari, calisan istekleri, yetkinlik zorunluluklari bilinmiyor), molalar
  (-> varsayilan yerlesim). Kiyas "motor planlamacidan iyi" DEMEZ. Saglam olan: ciktinin yasal
  eslere gore ihlalleri (dinlenme/ardisik gece brut aralikla olculur) ve ayni kadro, desen ve
  saat basi kisi sayisiyla yasal planin varligi / suresi. Musteriden istenecek: sozlesmeler,
  kural listesi, talep (HC hedefi), istek ve kisitlar.

GIZLILIK
  Isim, sicil, firma adi bu dosyadan DISARI CIKMAZ: sahnede yalniz anonim kimlik,
  ekip kodu, rol, saatler. Esleme dosyasi 06-veri altinda kalir (.gitignore).
"""

import collections
import csv
import datetime as dt
import io
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
MOTOR = os.path.join(KOK, "09-motor")
for _y in (MOTOR, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

KANONIK = os.path.join(KOK, "06-veri", "kanonik", "plan.csv")
CIKTI = os.path.join(KOK, "06-veri", "anonim", "insan")

# Takim adi -> ekip kodu (Turkce harfler sadelestirilerek; `sade`). Lider takimlari ana ekibe baglanir (rol ayrica).
EKIPLER = [("satis destek", "SATIS_DESTEK"), ("backoffice", "BACKOFFICE"), ("yerinde cozum", "YCM"),
           ("kontrat", "KONTRAT"), ("fiyatlandirma", "FIYATLANDIRMA"), ("urun analiz", "URUN_ANALIZ"),
           ("ant-yurtici", "ANT_URUN"), ("rezervasyon", "REZERVASYON")]
_TR = str.maketrans({"ç": "c", "ö": "o", "ü": "u", "ş": "s", "ğ": "g", "ı": "i", "Ç": "c", "Ö": "o", "Ü": "u",
                     "Ş": "s", "Ğ": "g", "İ": "i", "I": "i"})


def sade(metin):
    """Turkce harfleri sadelestirip kucuk harfe indirir ('Yerinde Çözüm' -> 'yerinde cozum');
    Python'un upper()/lower()'i I/İ'de yaniltir, bu yuzden once harf tablosu."""
    return (metin or "").translate(_TR).lower().replace("i\u0307", "i").strip()


IZIN_KODLARI = {   # DURUM kodu -> izin tipi (onayli); OFF / Uzaktan Calisma izin DEGIL
    "RAPORLU": "rapor", "Raporlu": "rapor", "D.İZNİ": "idari", "Y.İZİN": "yillik", "YILLIK İZİN": "yillik",
    "T.İZNİ": "yillik", "EĞİTİM": "egitim", "R.TATİL": "resmi_tatil", "E.İZNİ": "idari", "S.İZNİ": "idari",
    "Ü.Lİ.İZİN": "idari", "Ü.SİZ.İZİN": "idari", "MAZERET": "idari", "TŞ.İZNİ": "idari", "C.İZNİ": "idari",
    "D.GÖREV": "idari", "DEVAMSIZ": "devamsiz", "İSTİFA": "ayrildi", "FESİH": "ayrildi",
}
ATILAN_KURALLAR = ("ROL_KAPSAMASI", "YETKINLIK_KAPSAMASI", "CALISMA_SAATLERI")   # veri yok (yetkinlik, departman saati)


def ekip_kodu(takim):
    t = sade(takim)
    for anahtar, kod in EKIPLER:
        if anahtar in t:
            return kod
    return "DIGER"


def lider_mi(takim, gorev):
    return "takim lideri" in sade((takim or "") + " " + (gorev or ""))


def saat(s):
    """'2026-06-22 09:00' -> 9.0"""
    hh, mm = s[11:].split(":")
    return int(hh) + int(mm) / 60.0


def sablon_kimligi(ekip, bas, bit):
    return "%s-%02d%02d-%02d%02d" % (ekip, int(bas), round((bas % 1) * 60), int(bit) % 24, round((bit % 1) * 60))


def mola_politikasi(brut):
    if brut >= 7.5:
        return [{"tip": "yemek", "dakika": 60, "adet": 1, "ucretli": False},
                {"tip": "dinlenme", "dakika": 15, "adet": 2, "ucretli": True}]
    return [{"tip": "yemek", "dakika": 30, "adet": 1, "ucretli": False},
            {"tip": "dinlenme", "dakika": 15, "adet": 1, "ucretli": True}]


def varsayilan_molalar(bas, bit):
    """Musteri plani mola yazmaz; degerlendirme icin yasal asgariyi saglayan varsayilan
    yerlesim: yemek vardiya basindan 4 sa sonra (MOLA_YERLESIMI 3-5 sa penceresi), 7,5 sa
    altinda 3 sa sonra 30 dk; dinlenmeler yemekle cakismaz."""
    brut = bit - bas
    if brut >= 7.5:
        m = [{"bas": bas + 1.5, "bit": bas + 1.75, "tip": "dinlenme"},
             {"bas": bas + 4.0, "bit": bas + 5.0, "tip": "yemek"},
             {"bas": bas + 6.5, "bit": bas + 6.75, "tip": "dinlenme"}]
    else:
        m = [{"bas": bas + 1.5, "bit": bas + 1.75, "tip": "dinlenme"},
             {"bas": bas + 3.0, "bit": bas + 3.5, "tip": "yemek"}]
    return [x for x in m if x["bit"] <= bit - 0.25]


def oku(kanonik, hafta):
    bas = dt.date.fromisoformat(hafta)
    if bas.weekday() != 0:
        raise SystemExit("--hafta Pazartesi olmali: %s" % hafta)
    gunler = {bas + dt.timedelta(days=i): i for i in range(7)}
    vardiya, durum, kisi = [], [], {}
    with io.open(kanonik, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            g = dt.date.fromisoformat(r["gun"])
            if g not in gunler:
                continue
            r = dict(r, gun_no=gunler[g])
            kisi.setdefault(r["sicil"], {"takimlar": collections.Counter(), "gorev": r.get("gorev", ""), "takim": r.get("takim", "")})
            if r["tur"] == "VARDIYA":
                vardiya.append(r)
                kisi[r["sicil"]]["takimlar"][ekip_kodu(r.get("takim"))] += 1
            else:
                durum.append(r)
    return vardiya, durum, kisi


def kur(kanonik=KANONIK, hafta="2026-06-22"):
    import ekili as E
    import merdiven as MD
    from dogrulayici import zaman, degerlendir
    vardiya, durum, kisi = oku(kanonik, hafta)
    if not vardiya:
        raise SystemExit("bu haftada vardiya yok: %s" % hafta)
    # --- kisiler (anonim) ---
    siciller = sorted(s for s, k in kisi.items() if k["takimlar"])          # o hafta en az bir vardiya
    esleme = {s: "I%03d" % (i + 1) for i, s in enumerate(siciller)}
    izin = collections.defaultdict(list)
    for r in durum:
        tip = IZIN_KODLARI.get((r.get("ham_deger") or "").strip())
        if tip and r["sicil"] in esleme:
            izin[r["sicil"]].append({"gun": r["gun_no"], "tip": tip, "durum": "onayli"})
    # --- insan plani (motor bicimi) + sablonlar ---
    sablonlar, atamalar = {}, []
    for r in vardiya:
        bas, bit = saat(r["baslangic"]), saat(r["bitis"])
        if r["bitis"][:10] > r["baslangic"][:10]:
            bit += 24.0                                      # gece yarisini asan
        ekip = ekip_kodu(r.get("takim"))
        sid = sablon_kimligi(ekip, bas, bit)
        if sid not in sablonlar:
            sablonlar[sid] = {"id": sid, "ekip": ekip, "bas": bas, "bit": bit, "mola_dk": mola_politikasi(bit - bas)[0]["dakika"],
                              "gece_vardiyasi": bool(bit > 24 or bas >= 20), "mola_politikasi": mola_politikasi(bit - bas)}
        atamalar.append({"calisan": esleme[r["sicil"]], "ekip": ekip, "sablon": sid, "gun": r["gun_no"],
                         "bas": bas, "bit": bit, "molalar": varsayilan_molalar(bas, bit)})
    atamalar.sort(key=lambda a: (a["calisan"], a["gun"], a["bas"]))
    net = collections.defaultdict(float); gun_sayisi = collections.defaultdict(set)
    for a in atamalar:
        net[a["calisan"]] += zaman.net_saat(a); gun_sayisi[a["calisan"]].add(a["gun"])
    calisanlar = []
    for s in siciller:
        k, kid = kisi[s], esleme[s]
        ekipler = [e for e, _ in k["takimlar"].most_common()]
        h = min(45.0, round(net[kid] * 4) / 4.0)
        calisanlar.append({"id": kid, "ekipler": ekipler, "birincil_ekip": ekipler[0],
                           "operasyonel_rol": "takim_lideri" if lider_mi(k["takim"], k["gorev"]) else None,
                           "yetkinlikler": [], "durum": "aktif",
                           "sozlesme": {"tip": "tam_zamanli", "haftalik_saat": h, "gun_sayisi": max(5, min(6, len(gun_sayisi[kid])))},
                           "izinler": sorted(izin.get(s, []), key=lambda x: x["gun"]), "uygunluk": []})
    # --- kurallar: katalog (uretec sahnesinden), veri olmayanlar atilir ---
    kurallar = [k for k in MD.taban_sahne(0.1, "uretec")["kurallar"] if k["kod"] not in ATILAN_KURALLAR]
    for k in kurallar:
        if k["kod"] == "SAHADA_ASGARI":
            k["parametreler"] = {"asgari_sahada": 0}
    # --- talep: once kaba sayim (hucre iskeleti), sonra ekili_sahne dogrulayicinin sayimiyla ---
    ekipler_set = sorted({a["ekip"] for a in atamalar})
    sayim = collections.Counter()
    for a in atamalar:
        q = a["bas"]
        while q < a["bit"] - 1e-9:
            g, h = a["gun"] + int(q) // 24, int(q) % 24
            if g <= 6:
                sayim[(a["ekip"], g, h)] += 1
            q = int(q) + 1
    talep = [{"ekip": e, "gun": g, "saat": h, "asgari": 0, "hedef": int(sayim.get((e, g, h), 0))}
             for e in ekipler_set for g in range(7) for h in range(24)]
    taban = {"ad": "INSAN-%s" % hafta, "surum": "1.0", "hafta_baslangic": hafta, "sektor": "turizm",
             "kiraci_saat_dilimi": "Europe/Istanbul", "profil": "DENGELI", "cok_ekipli_sayim": "hepsi",
             "calisanlar": calisanlar, "vardiya_sablonlari": sorted(sablonlar.values(), key=lambda s: s["id"]),
             "talep": talep, "kurallar": kurallar, "kilitler": [], "donmus_gunler": [], "sabit_atamalar": [],
             "devir_kapsama": [], "denetim_disi_kabul": [],
             "_aciklama": ["Gercek musterinin elle yaptigi haftalik plandan turetilmis ANONIM sahne (A3).",
                           "Talep insan planinin sayimindan (ekili yontemi); sozlesme saati insan planinin net saati (<= 45).",
                           "Molalar varsayilan yerlestirildi (musteri plani mola yazmaz)."],
             "_merdiven": {"seviye": "insan", "kaynak": "insan plani %s" % hafta}}
    g = E.ekili_sahne(taban, atamalar)
    g["_merdiven"]["seviye"] = "insan"
    g["_merdiven"]["kaynak"] = "insan plani (%s): talep ve sozlesmeler planlamacinin planindan; molalar varsayilan" % hafta
    # --- insan planinin denetimi (bugunku dogrulayici) ---
    r = degerlendir(g, atamalar)
    sert = collections.Counter(i["kural"] for i in r["ihlaller"] if i.get("agirlik") == "SERT" and not i.get("gecmis"))
    yumusak = collections.Counter(i["kural"] for i in r["ihlaller"] if i.get("agirlik") != "SERT" and not i.get("gecmis"))
    rapor = {"hafta": hafta, "kisi": len(calisanlar), "atama": len(atamalar), "ekipler": ekipler_set,
             "sablon": len(sablonlar), "lider": sum(1 for c in calisanlar if c["operasyonel_rol"]),
             "izinli_kisi_gun": sum(len(c["izinler"]) for c in calisanlar),
             "sert_ihlal": sum(sert.values()), "sert_kural": dict(sert.most_common()),
             "yumusak_ihlal": sum(yumusak.values()), "yumusak_kural": dict(yumusak.most_common()),
             "metrikler": r.get("metrikler"), "yayinlanabilir": r["yayin_kapisi"]["yayinlanabilir"],
             "hedef_kisi_saat": g["_merdiven"]["hedef_kisi_saat"], "asgari_kisi_saat": g["_merdiven"]["asgari_kisi_saat"],
             "net_saat_dagilimi": dict(collections.Counter(round(net[c["id"]]) for c in calisanlar)),
             "45_ustu_kisi": sum(1 for c in calisanlar if net[c["id"]] > 45 + 1e-6),
             "uyari": "molalar varsayilan yerlestirildi; sert ihlaller insan planinin kendi ihlalleri + mola varsayimimizin etkisi olabilir"}
    return g, {"atamalar": atamalar, "kayit": rapor}, esleme


def puanla(sahne_yolu, referans_yolu):
    """--puan (ortools): insan planinin motor olcusuyle puani -> sahne._merdiven.referans_puani."""
    import merdiven as MD
    g = json.load(io.open(sahne_yolu, encoding="utf-8"))
    ref = json.load(io.open(referans_yolu, encoding="utf-8"))
    p = MD.plan_puani(g, ref["atamalar"])
    g["_merdiven"]["referans_puani"] = p if (p and p.get("durum") == "OPTIMAL") else {
        "durum": (p or {}).get("durum", "MODELE_OTURMADI"), "amac": None, "dagilim": {},
        "not": "insan plani sert kural ihlalleriyle modele oturmuyor; kiyas kalem kalem dogrulayici raporuyla (kayit)"}
    with io.open(sahne_yolu, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=1)
    return g["_merdiven"]["referans_puani"]


def _arg(ad, varsayilan, tur=str):
    return tur(sys.argv[sys.argv.index(ad) + 1]) if ad in sys.argv else varsayilan


if __name__ == "__main__":
    hafta = _arg("--hafta", "2026-06-22")
    cikti = _arg("--cikti", CIKTI)
    os.makedirs(cikti, exist_ok=True)
    sahne_yolu = os.path.join(cikti, "_sahne-INSAN-%s.json" % hafta)
    referans_yolu = os.path.join(cikti, "_referans-INSAN-%s.json" % hafta)
    if "--puan" in sys.argv:
        print("INSAN PLANI PUANI:", puanla(sahne_yolu, referans_yolu))
        sys.exit(0)
    g, ref, esleme = kur(_arg("--kanonik", KANONIK), hafta)
    for yol, veri in ((sahne_yolu, g), (referans_yolu, ref), (os.path.join(cikti, "esleme-%s.json" % hafta), esleme)):
        with io.open(yol, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=1)
    k = ref["kayit"]
    print("INSAN PLANI SAHNESI yazildi: %s" % sahne_yolu)
    print("  %d kisi (%d lider), %d atama, %d sablon, ekipler %s | izin %d kisi-gun" % (
        k["kisi"], k["lider"], k["atama"], k["sablon"], ", ".join(k["ekipler"]), k["izinli_kisi_gun"]))
    print("  hedef %d kisi-saat, asgari %d | 45 sa ustu kisi %d | net saat dagilimi %s" % (
        k["hedef_kisi_saat"], k["asgari_kisi_saat"], k["45_ustu_kisi"], k["net_saat_dagilimi"]))
    print("  INSAN PLANI DENETIMI: sert %d %s | yumusak %d %s | fm %.2f sa | yayinlanabilir %s" % (
        k["sert_ihlal"], k["sert_kural"], k["yumusak_ihlal"], k["yumusak_kural"],
        (k["metrikler"] or {}).get("fazla_mesai_saat") or 0.0, k["yayinlanabilir"]))
