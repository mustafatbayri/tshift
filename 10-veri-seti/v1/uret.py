# -*- coding: utf-8 -*-
"""
TShift ornek veri seti v1 -- URETICI

NE YAPAR
  Bugune kadar olcumlerin kullandigi 500 kisilik (ve 0,1 olcekli 49 kisilik)
  sahneyi -- `merdiven.taban_sahne()`: S30-95 + K-62 kadro kararlari, motor
  girdisi bicimi -- SARTNAME #8 TABLOLARINA cevirir (kiracisiz, M-16) ve
  `veri/tshift-<kisi>.json` olarak yazar. Ayni veri bundan sonra
  `donustur.py` ile motor girdisine geri cevrilir: testler ve olcumler
  depodaki bu dosyadan kosar, her seferinde bellekte kurulmaz (Mustafa,
  13 Ekim 23:20).

BILEREK DEGISENLER (sahne "yeni set"tir -- T-80)
  1. K-58 + 14 Ekim: sozlesme tipi yalniz iki. Eski `sezonluk` (13 kisi,
     40 sa) -> tam zamanli (haftalik 6 gun, sozlesme bitisi 31.12.2026);
     eski `stajyer` (16 kisi, 30 sa) -> yari zamanli (bitis 30.06.2027).
     Tam zamanlinin `gun_sayisi` -> `employee_contracts.haftalik_gun`.
  2. GECMIS: iki yayinlanmis hafta (28 Eylul, 5 Ekim). Atamalari
     cevabi bilinen planlardan gelir (500: ayirma plani ve seviye 1
     referansi; 0,1: seviye 1 referansi iki hafta). Motor bunlari
     `gecmis_vardiyalar` (gun -14..-1) ve `gecmis_bilinen_gunler` olarak alir.
  3. `devir_yuk` (ADALET_DENGESI, takvim ayi) uretecin rastgele sayilari
     yerine bu gecmisten HESAPLANIR (1-11 Ekim; motorun kendi gun ve gece
     tanimiyla) ve `employee_balances`a yazilir. `yil_ici_fazla_mesai_saat`
     uretecin sayisi kalir (PDKS gecmisi veri setinde yok, K-55).
  4. HEDEF_ASIMI firmanin ayarinda katalog turunde (SERT, K-67); merdiven
     tabani referans uretmek icin onu YUMUSAK yapar (bugunku gibi).
  5. Isimler, e-posta, telefon, sicil disi kimlik UYDURMA (Mustafa: "isimler
     disinda gercekci"). Sicil no (`personel_no`) bugunku kimlik (C0001...):
     butun eski planlar, kilitler, referanslar ayni kimlikle okunur.

KOSTURMA
  cd C:\\Users\\PC\\Desktop\\Tshift\\10-veri-seti\\v1
  py uret.py                 # veri/tshift-500.json ve veri/tshift-49.json
Ayni girdiyle ayni dosya (tohumlu; kimlikler uuid5).
"""

import datetime as dt
import io
import json
import os
import random
import re
import sys
import uuid

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BURASI))
GERCEKCI = os.path.join(KOK, "08-motor-testleri", "gercekci-veri-seti")
MOTOR = os.path.join(KOK, "09-motor")
for _y in (MOTOR, GERCEKCI, BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

SURUM = "1.0"
NS = uuid.UUID("6f1c2b1e-5d0a-4c1e-9a77-1e5a7e5f0c68")    # sabit: kimlikler her uretimde ayni
HAFTA = dt.date(2026, 10, 12)                                # plan haftasi (Pazartesi)
GECMIS = [dt.date(2026, 9, 28), dt.date(2026, 10, 5)]        # yayinlanmis iki hafta
OLUSTURMA = "2026-10-01T09:00:00+03:00"
TOHUM = 20261014

# ----------------------------------------------------------------------
# Uydurma isimler (gercek kisi degil; yaygin ad ve soyadlarin rastgele esi)
# ----------------------------------------------------------------------
KADIN = ["Ayşe", "Fatma", "Zeynep", "Elif", "Merve", "Esra", "Büşra", "Gizem", "Derya", "Seda", "Özge",
         "Gamze", "Ebru", "Tuğba", "Sibel", "Hülya", "Şeyma", "Nur", "Ece", "İrem", "Damla", "Pınar",
         "Burcu", "Ceren", "Selin", "Duygu", "Aslı", "Gülşen", "Yasemin", "Emine", "Hatice", "Sevgi",
         "Canan", "Dilek", "Nazlı", "Melike", "Rabia", "Sevda", "Yıldız", "Çiğdem", "Gökçe", "Ilgın",
         "Şule", "Aylin", "Berna", "Didem", "Funda", "Hande", "Kübra", "Leyla"]
ERKEK = ["Mehmet", "Mustafa", "Ahmet", "Ali", "Hüseyin", "Hasan", "İbrahim", "Murat", "Emre", "Burak",
         "Onur", "Serkan", "Volkan", "Kerem", "Barış", "Cem", "Can", "Deniz", "Efe", "Eren", "Furkan",
         "Gökhan", "Halil", "İsmail", "Kaan", "Kemal", "Levent", "Mert", "Oğuz", "Ozan", "Selim",
         "Sinan", "Tolga", "Tuncay", "Uğur", "Ümit", "Yasin", "Yusuf", "Çağrı", "Şahin", "Erdem",
         "Fatih", "Gürkan", "Harun", "Koray", "Okan", "Recep", "Taner", "Umut", "Zafer"]
SOYAD = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
         "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek", "Polat",
         "Özcan", "Korkmaz", "Çakır", "Erdoğan", "Yavuz", "Can", "Acar", "Şen", "Aktaş", "Güler", "Yalçın",
         "Güneş", "Bozkurt", "Bulut", "Keskin", "Ünal", "Turan", "Gül", "Özer", "Işık", "Kaplan", "Avcı",
         "Sarı", "Tekin", "Taş", "Köse", "Yüksel", "Ateş", "Aksoy", "Uçar", "Ekinci", "Altun", "Kocaman",
         "Erkan", "Karaca", "Tunç", "Sezer", "Akın", "Bayram", "Eren", "Duman", "Karataş", "Uysal",
         "Ceylan", "Gündoğdu", "Başaran", "Toprak", "Sönmez", "Çınar", "Ergün", "Kalkan", "Önal", "Akgül",
         "Durmaz", "Gökçe", "Soylu", "Tok", "Sevim", "Oral"]
_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")

ROLLER = [("agent", "Müşteri Temsilcisi", "Çağrı karşılayan temsilci."),
          ("kidemli_agent", "Kıdemli Müşteri Temsilcisi", "Zor çağrılar ve yeni başlayanlara destek."),
          ("takim_lideri", "Takım Lideri", "Vardiyada ekibi yönetir; ROL_KAPSAMASI saatlerinde sahada en az 1."),
          ("uzman", "Uzman", "Süreç ve ürün uzmanı.")]
YETKINLIKLER = [("almanca", "Almanca", "Almanca çağrı karşılama."),
                ("ingilizce", "İngilizce", "İngilizce çağrı karşılama."),
                ("iade", "İade süreçleri", "İade ve iptal işlemleri."),
                ("teknik", "Teknik destek", "Teknik sorun giderme."),
                ("kurumsal", "Kurumsal müşteri", "Kurumsal hesap hattı.")]
EKIP_ADI = {"SATIS": "Satış", "BACKOFFICE": "Back Office", "MHIZMET": "Müşteri Hizmetleri"}
EKIP_ACIKLAMA = {"SATIS": "Satış hattı (7/24).", "BACKOFFICE": "Arka ofis işlemleri (7/24; gece az).",
                 "MHIZMET": "Müşteri hizmetleri hattı (hafta içi 07–23, hafta sonu 08–19)."}
SABLON_ON = {"S": "Satış", "B": "Back Office", "M": "Müşteri Hizmetleri"}
SABLON_SON = {"SABAH": "Sabah", "ARA": "Ara", "AKSAM": "Akşam", "GECE": "Gece", "UZUN": "Uzun",
              "KISA": "Kısa", "HSONU": "Hafta Sonu", "OGLE": "Öğle", "ERKEN": "Erken", "GEC": "Geç",
              "YARIM": "Yarım Gün", "AKSAMK": "Akşam Kısa"}
RENK = {"SABAH": "#F6C344", "ARA": "#7FB77E", "AKSAM": "#E07A5F", "GECE": "#3D5A80", "UZUN": "#98C1D9",
        "KISA": "#C9ADA7", "HSONU": "#9A8C98", "YARIM": "#C9ADA7", "AKSAMK": "#E07A5F"}
UYGUNLUK_ACIKLAMA = ["Üniversite dersi", "İkinci iş", "Çocuk bakımı", "Kişisel", "Üniversite dersi"]

# Kural katalogu -- sartname #6 bolumleri -> kategori; gorunen adlar
KATEGORI = {"6.1": "uygunluk", "6.2": "sure", "6.3": "gece", "6.4": "kapsama", "6.5": "adalet",
            "6.6": "duzenleme", "6.7": "fazla_mesai", "6.8": "tercih"}
KURAL_ADI = {
    "AKTIF_CALISAN": "Aktif çalışan", "SOZLESME_GECERLI": "Sözleşme geçerli", "ONAYLI_IZIN": "Onaylı izin",
    "UYGUNLUK_TAKVIMI": "Uygunluk takvimi", "CALISMA_SAATLERI": "Departman çalışma saatleri",
    "GUNLUK_AZAMI": "Günlük azami çalışma", "HAFTALIK_AZAMI": "Haftalık azami çalışma",
    "PART_TIME_LIMIT": "Yarı zamanlı haftalık sınır", "VARDIYA_ARASI_DINLENME": "Vardiya arası dinlenme",
    "HAFTA_TATILI": "Hafta tatili", "CAKISMA_YOK": "Çakışma yok", "MOLA_HAKKI": "Mola hakkı",
    "MOLA_YERLESIMI": "Mola yerleşimi", "MOLA_TIPI_ZORUNLU": "Mola tipi zorunlu",
    "MOLA_ASGARI_BLOK": "Mola asgari blok", "YEMEK_TEK_BLOK": "Yemek tek blok",
    "SAHADA_ASGARI": "Sahada asgari kişi", "ASGARI_VARDIYA_SURESI": "Asgari vardiya süresi",
    "ARDISIK_CALISMA_GUNU": "Ardışık çalışma günü", "YILLIK_FAZLA_MESAI_TAVANI": "Yıllık fazla mesai tavanı",
    "GECE_VARDIYASI_AZAMI": "Gece vardiyası azami süre", "GECE_POSTASI_DEVRI": "Gece postası devri",
    "ARDISIK_GECE_LIMIT": "Ardışık gece sınırı", "GECE_UYGUNLUGU": "Gece uygunluğu",
    "VARDIYA_ROTASYON_YONU": "Vardiya rotasyon yönü", "GECE_YARISI_ASAN": "Gece yarısını aşan vardiya",
    "ASGARI_KAPSAMA": "Asgari kapsama", "HEDEF_KAPSAMA": "Hedef kapsama", "HEDEF_ASIMI": "Hedef aşımı",
    "MOLA_KAPSAMASI": "Mola sırasında kapsama", "ROL_KAPSAMASI": "Rol kapsaması",
    "YETKINLIK_KAPSAMASI": "Yetkinlik kapsaması", "SAAT_DENGESI": "Sözleşme saati dengesi",
    "ADALET_DENGESI": "Adalet dengesi", "ARDISIK_HAFTA_SONU_LIMIT": "Ardışık hafta sonu sınırı",
    "EKIP_SUREKLILIGI": "Ekip sürekliliği", "PLAN_KARARLILIGI": "Plan kararlılığı",
    "KILIT_UYUMU": "Kilit uyumu", "DONMUS_GUN": "Dondurulmuş gün", "FAZLA_MESAI_TAVANI": "Haftalık fazla mesai tavanı",
    "TERCIH_KARSILAMA": "Tercih karşılama"}
SATIR_BAZLI = {"ROL_KAPSAMASI", "YETKINLIK_KAPSAMASI"}
PROFIL_ADI = {"DENGELI": ("Dengeli", "Kapsama, çalışan ve adalet arasında denge (varsayılan)."),
              "KAPSAMA": ("Kapsama öncelikli", "Hedef kapsamayı en üste koyar."),
              "CALISAN": ("Çalışan öncelikli", "Tercih, adalet ve saat dengesini öne alır.")}


def kimlik(tur, anahtar):
    return str(uuid.uuid5(NS, "%s:%s" % (tur, anahtar)))


def _satir(tablo_adi, anahtar, **alanlar):
    s = {"id": kimlik(tablo_adi, anahtar), "created_at": OLUSTURMA, "updated_at": None}
    s.update(alanlar)
    return s


def _md_temizle(metin):
    metin = re.sub(r"\*\*|`|🆕|🔄|⚠️?|✅|❌|🔒", "", metin)
    metin = re.sub(r"\s+", " ", metin).strip(" —-")
    return metin


def katalog():
    """Sartname #6'nin kural tablolari -> rule_types satirlari (41)."""
    s = io.open(os.path.join(KOK, "02-spec", "v1.4-master-spec.md"), encoding="utf-8").read()
    blk = s[s.index("## 6.1 Uygunluk kuralları"):s.index("## 6.9 Yasal dayanaklar")]
    cikan, bolum = [], None
    for satir in blk.splitlines():
        m = re.match(r"## (6\.\d) ", satir)
        if m:
            bolum = m.group(1)
            continue
        if not satir.startswith("| `"):
            continue
        h = [c.strip() for c in satir.strip().strip("|").split("|")]
        kod = re.search(r"`([A-Z_]+)`", h[0]).group(1)
        tur = "YUMUSAK" if "YUMU" in h[1] else "SERT"
        satir_bazli = "satır bazlı" in h[2]
        yasal = (not satir_bazli) and "✅" in h[2]
        if tur == "YUMUSAK" or h[3].strip() in ("—", "-"):
            kabul = None
        else:
            kabul = (not satir_bazli) and ("✅" in h[3])
        kapsam = [k.strip() for k in re.sub(r"[*`]", "", h[4]).split(",") if k.strip()]
        cikan.append({"kod": kod, "ad": KURAL_ADI.get(kod, kod), "aciklama": _md_temizle(h[6]) if len(h) > 6 else "",
                      "tur": tur, "kategori": KATEGORI[bolum], "yasal": yasal, "kabul_edilebilir": kabul,
                      "bayrak_satir_bazli": satir_bazli, "kapsam_seviyeleri": kapsam})
    assert len(cikan) == 41, len(cikan)
    return cikan


def _gecmis_planlari(olcek):
    """Iki gecmis haftanin atamalari: (28 Eylul, 5 Ekim)."""
    def yukle(yol):
        return json.load(io.open(yol, encoding="utf-8"))
    ek = "" if olcek == 1.0 else "-%g" % olcek
    ref = yukle(os.path.join(GERCEKCI, "fikstur", "_referans-L1-95%s.json" % ek))["atamalar"]
    if olcek == 1.0:
        ayirma = yukle(os.path.join(GERCEKCI, "planlar", "kalite-olcumu-L1-asim_yumusak-95-ayirma-900",
                                    "varsayilan-1.json"))["cikti"]["atamalar"]
        return [("ayirma-asim_yumusak-varsayilan-1", ayirma), ("referans-L1-95", ref)]
    return [("referans-L1-95%s" % ek, ref), ("referans-L1-95%s" % ek, ref)]


def _isim_uret(rnd, n):
    gorulen, cikan = set(), []
    for i in range(n):
        while True:
            ad = rnd.choice(KADIN if rnd.random() < 0.58 else ERKEK)
            if rnd.random() < 0.06:                      # ikinci ad
                ad += " " + rnd.choice(KADIN if ad in KADIN else ERKEK)
            soyad = rnd.choice(SOYAD)
            if (ad, soyad) not in gorulen:
                gorulen.add((ad, soyad))
                break
        cikan.append((ad, soyad))
    return cikan


def _eposta(ad, soyad, kullanilan):
    yerel = ("%s.%s" % (ad.split()[0], soyad)).lower().translate(_ASCII)
    yerel = re.sub(r"[^a-z.]", "", yerel)
    aday, n = yerel, 1
    while aday in kullanilan:
        n += 1
        aday = "%s%d" % (yerel, n)
    kullanilan.add(aday)
    return aday + "@tshift-ornek.test"


def _tarih(rnd, bas, bit):
    return bas + dt.timedelta(days=rnd.randrange((bit - bas).days + 1))


def uret(olcek=1.0):
    import merdiven as MD
    from cozucu.model import AGIRLIK_TABLOSU, _gece_sablonu, _hafta_sonu_gunu, _yasal_gece_postasi
    g = MD.taban_sahne(olcek)
    rnd = random.Random(TOHUM + int(olcek * 1000))

    veri = {"_meta": {
        "ad": "TShift örnek veri seti", "surum": SURUM, "olcek": olcek,
        "uretim": "10-veri-seti/v1/uret.py (tohumlu; aynı girdiyle aynı dosya)",
        "kaynak": "merdiven.taban_sahne(%g) -- S30-95 + K-62; şartname §8 tablolarına çevrildi" % olcek,
        "plan_haftasi": HAFTA.isoformat(),
        "uyari": "İsimler, e-posta, telefon ve dış sistem kimlikleri UYDURMADIR; gerçek kişilere ait değildir.",
        "tablolar": None}}

    # ---- firma
    veri["tenants"] = [_satir("tenants", "firma", ad="Örnek Çağrı Merkezi A.Ş.", slug="ornek-cagri",
                              sektor_paketi="cagri_merkezi", birim_adi="Departman",
                              zaman_dilimi=g.get("kiraci_saat_dilimi", "Europe/Istanbul"), hafta_baslangic=1,
                              sektor=None, durum="aktif", deneme_bitis=None,
                              cok_ekipli_sayim=g.get("cok_ekipli_sayim", "hepsi"))]

    # ---- organizasyon
    ust = _satir("departments", "OPERASYON", ad="Operasyon", kod="OPERASYON", ust_department_id=None,
                 calisma_tipi="yedi_yirmidort", acik=None, aktif=True)
    deps, ekip_dep = [ust], {}
    for d in g["departmanlar"]:
        deps.append(_satir("departments", d["id"], ad={"D-SATIS": "Satış", "D-BACK": "Back Office",
                                                        "D-MHIZMET": "Müşteri Hizmetleri"}.get(d["id"], d["ad"]),
                           kod=d["id"], ust_department_id=ust["id"],
                           calisma_tipi="yedi_yirmidort" if d["acik"] == "7/24" else "saatli",
                           acik=d["acik"], aktif=True))
        for e in d["ekipler"]:
            ekip_dep[e] = deps[-1]["id"]
    veri["departments"] = deps
    veri["teams"] = [_satir("teams", e, department_id=ekip_dep[e], ad=EKIP_ADI.get(e, e), kod=e,
                            aciklama=EKIP_ACIKLAMA.get(e), aktif=True) for e in ekip_dep]
    ekip_id = {t["kod"]: t["id"] for t in veri["teams"]}
    veri["operational_roles"] = [_satir("operational_roles", k, ad=a, kod=k, aciklama=x) for k, a, x in ROLLER]
    rol_id = {r["kod"]: r["id"] for r in veri["operational_roles"]}
    veri["skills"] = [_satir("skills", k, ad=a, kod=k, aciklama=x, sertifika_gerekli=False) for k, a, x in YETKINLIKLER]
    yet_id = {s["kod"]: s["id"] for s in veri["skills"]}

    # ---- calisanlar
    isimler = _isim_uret(rnd, len(g["calisanlar"]))
    epostalar = set()
    emp, soz, ekipler, yet, uyg, izin, sayac = [], [], [], [], [], [], {"sezonluk": 0, "stajyer": 0}
    for c, (ad, soyad) in zip(g["calisanlar"], isimler):
        pno = c["id"]
        eid = kimlik("employees", pno)
        durum = c.get("durum", "aktif")
        tip_eski = c["sozlesme"]["tip"]
        if tip_eski == "sezonluk":
            ise_giris = dt.date(2026, 6, 1)
        elif tip_eski == "stajyer":
            ise_giris = dt.date(2026, 9, 1)
        else:
            ise_giris = _tarih(rnd, dt.date(2014, 1, 6), dt.date(2026, 8, 31)) if rnd.random() < 0.7 \
                else _tarih(rnd, dt.date(2024, 1, 1), dt.date(2026, 8, 31))
        cikis = _tarih(rnd, dt.date(2026, 9, 7), dt.date(2026, 10, 9)) if durum == "ayrildi" else None
        onay = rnd.random() < 0.05 and not c.get("gece_calisamaz")
        emp.append({"id": eid, "created_at": OLUSTURMA, "updated_at": None,
                    "personel_no": pno, "ad": ad, "soyad": soyad, "eposta": _eposta(ad, soyad, epostalar),
                    "telefon": "+90 000 %03d %02d %02d" % (rnd.randrange(1000), rnd.randrange(100), rnd.randrange(100)),
                    "department_id": ekip_dep[c["ekipler"][0]], "birincil_team_id": ekip_id[c["ekipler"][0]],
                    "operational_role_id": rol_id[c["operasyonel_rol"]],
                    "ise_giris": ise_giris.isoformat(), "isten_cikis": cikis.isoformat() if cikis else None,
                    "durum": durum, "user_id": None, "dis_sistem_id": "IK-%06d" % (100000 + int(pno[1:])),
                    "gece_calisma_onayi": onay,
                    "gece_calisma_onay_tarihi": _tarih(rnd, ise_giris, dt.date(2026, 9, 30)).isoformat() if onay else None,
                    "gece_calisma_onay_belge": ("BELGE-%s-GECE" % pno) if onay else None,
                    "gece_calisamaz": bool(c.get("gece_calisamaz"))})
        # sozlesme (K-58 + 14 Ekim)
        if tip_eski == "sezonluk":
            tip, gun, bas, bit = "tam_zamanli", 6, dt.date(2026, 6, 1), dt.date(2026, 12, 31)
            sayac["sezonluk"] += 1
        elif tip_eski == "stajyer":
            tip, gun, bas, bit = "yari_zamanli", None, dt.date(2026, 9, 1), dt.date(2027, 6, 30)
            sayac["stajyer"] += 1
        else:
            tip, gun, bas, bit = tip_eski, c["sozlesme"].get("gun_sayisi"), ise_giris, None
            if tip == "tam_zamanli":
                assert c["sozlesme"].get("haftalik_saat") == 45, c
        if cikis:
            bit = cikis
        soz.append(_satir("employee_contracts", pno, employee_id=eid, tip=tip, haftalik_gun=gun,
                          baslangic=bas.isoformat(), bitis=bit.isoformat() if bit else None,
                          aktif=durum != "ayrildi"))
        for i, e in enumerate(c["ekipler"]):
            ekipler.append(_satir("employee_teams", "%s:%s" % (pno, e), employee_id=eid, team_id=ekip_id[e],
                                  oncelik=i + 1))
        for y in c["yetkinlikler"]:
            yet.append(_satir("employee_skills", "%s:%s" % (pno, y), employee_id=eid, skill_id=yet_id[y],
                              seviye=rnd.randint(2, 5), sertifika_bitis=None))
        neden = rnd.choice(UYGUNLUK_ACIKLAMA)
        for u in c["uygunluk"]:
            uyg.append(_satir("employee_availability", "%s:%s:%s" % (pno, u["gun"], u["bas"]), employee_id=eid,
                              tip=u["tip"], tekrar="haftalik", gun=u["gun"], baslangic_tarih=None, bitis_tarih=None,
                              baslangic_saat=u["bas"], bitis_saat=u["bit"], aciklama=neden))
        for i in c["izinler"]:
            gun_t = (HAFTA + dt.timedelta(days=i["gun"])).isoformat()
            izin.append(_satir("leaves", "%s:%s" % (pno, gun_t), employee_id=eid, tip=i["tip"], baslangic=gun_t,
                               bitis=gun_t, tum_gun=True, baslangic_saat=None, bitis_saat=None, durum=i["durum"],
                               onaylayan_user_id=None, aciklama=None))
    veri["employees"], veri["employee_contracts"], veri["employee_teams"] = emp, soz, ekipler
    veri["employee_skills"], veri["employee_availability"], veri["leaves"] = yet, uyg, izin
    emp_id = {e["personel_no"]: e["id"] for e in emp}

    # ---- vardiya sablonlari
    sab = []
    for t in g["vardiya_sablonlari"]:
        on, _, son = t["id"].partition("-")
        sab.append(_satir("shift_templates", t["id"], department_id=ekip_dep.get(t.get("ekip")),
                          team_id=ekip_id.get(t.get("ekip")),
                          ad="%s %s" % (SABLON_ON.get(on, on), SABLON_SON.get(son, son.capitalize())),
                          kod=t["id"], baslangic_saat=t["bas"], bitis_saat=t["bit"], mola_dk=t["mola_dk"],
                          mola_politikasi=t.get("mola_politikasi"), gunler=t.get("gunler"),
                          gece_mi=bool(_yasal_gece_postasi(t["bas"], t["bit"])),
                          gece_vardiyasi=t.get("gece_vardiyasi"), aciklama=t.get("_not"),
                          renk=RENK.get(son), aktif=True))
    veri["shift_templates"] = sab
    sab_id = {s["kod"]: s["id"] for s in sab}
    sablon = {t["id"]: t for t in g["vardiya_sablonlari"]}

    # ---- kurallar
    kat = katalog()
    veri["rule_types"] = kat
    katd = {k["kod"]: k for k in kat}
    kurallar, sirali, farklar = {}, [], []
    for k in g["kurallar"]:
        kod = k["kod"]
        kk = katd[kod]
        if kod in SATIR_BAZLI:
            sat = dict(k.get("parametreler") or {}, yasal=k.get("yasal", False),
                       kabul_edilebilir=k.get("kabul_edilebilir"))
            if kod not in kurallar:
                kurallar[kod] = {"tur": k["tur"], "aktif": k.get("aktif", True), "parametreler": {"gereklilikler": []}}
                sirali.append(kod)
            kurallar[kod]["parametreler"]["gereklilikler"].append(sat)
            continue
        assert kod not in kurallar, kod
        # Bayraklar (yasal, kabul edilebilir) KATALOGDAN gelir (sistem tablosu,
        # K-18 / K-20); firma ayari onlari degistiremez. Ureticinin motor
        # girdisine yazdigi bayrak katalogdan sapmissa kayda gecer (bulgu).
        if bool(k.get("yasal", False)) != kk["yasal"]:
            farklar.append("%s: yasal -- uretici %s, katalog %s" % (kod, k.get("yasal", False), kk["yasal"]))
        if (k.get("kabul_edilebilir") if "kabul_edilebilir" in k else None) != kk["kabul_edilebilir"]:
            farklar.append("%s: kabul edilebilir -- uretici %s, katalog %s"
                           % (kod, k.get("kabul_edilebilir", "yok"), "yok (yumusak / ihlal uretmez)"
                              if kk["kabul_edilebilir"] is None else kk["kabul_edilebilir"]))
        tur = k["tur"]
        if kod == "HEDEF_ASIMI":
            tur = kk["tur"]                  # firma ayari: katalog (K-67); merdiven tabani YUMUSAK yapar
        kurallar[kod] = {"tur": tur, "aktif": k.get("aktif", True), "parametreler": dict(k.get("parametreler") or {})}
        sirali.append(kod)
    veri["tenant_rules"] = [_satir("tenant_rules", kod, rule_type_kod=kod, aktif=kurallar[kod]["aktif"],
                                   tur_gecersiz_kilma=(kurallar[kod]["tur"] if kurallar[kod]["tur"] != katd[kod]["tur"]
                                                       else None),
                                   agirlik=None, parametreler=kurallar[kod]["parametreler"], **{"not": None})
                            for kod in sirali]
    veri["plan_profiles"] = [_satir("plan_profiles", p, kod=p, ad=PROFIL_ADI[p][0], aciklama=PROFIL_ADI[p][1],
                                    agirliklar={kod: s[p] for kod, s in AGIRLIK_TABLOSU.items()},
                                    varsayilan_mi=(p == g.get("profil", "DENGELI")))
                             for p in ("DENGELI", "KAPSAMA", "CALISAN")]

    # ---- talep
    dp = _satir("demand_profiles", "normal-hafta", department_id=ust["id"], ad="Normal hafta (Ekim 2026)",
                kaynak="dogrudan", kapanma_payi=None, aktif=True)
    veri["demand_profiles"] = [dp]
    veri["demand_cells"] = [_satir("demand_cells", "%s:%s:%s" % (t["ekip"], t["gun"], t["saat"]),
                                   demand_profile_id=dp["id"], team_id=ekip_id[t["ekip"]], gun=t["gun"],
                                   saat=t["saat"], asgari_kisi=t["asgari"], hedef_kisi=t["hedef"],
                                   elle_duzeltildi=False) for t in g["talep"]]

    # ---- planlar: iki yayinlanmis gecmis hafta + uretilecek hafta
    planlar, surumler, atamalar, molalar = [], [], [], []
    devir = {p: {"gece": 0, "hafta_sonu": 0, "cumartesi": 0} for p in emp_id}
    for hafta, (kaynak, plan) in zip(GECMIS, _gecmis_planlari(olcek)):
        pk = hafta.isoformat()
        p = _satir("plans", pk, department_id=ust["id"], hafta_baslangic=pk, durum="yayinda",
                   demand_profile_id=dp["id"], secili_version_id=kimlik("plan_versions", pk),
                   olusturan_user_id=None, onaylayan_user_id=None,
                   onay_zamani=(hafta - dt.timedelta(days=3)).isoformat() + "T17:00:00+03:00",
                   yayin_zamani=(hafta - dt.timedelta(days=3)).isoformat() + "T17:30:00+03:00",
                   kural_degerleri=None)
        planlar.append(p)
        surumler.append(_satir("plan_versions", pk, plan_id=p["id"], plan_run_id=None, profil_kod="DENGELI",
                               metrikler={"kaynak_plan": kaynak, "atama": len(plan)}, secili_mi=True,
                               ai_aciklama=None))
        for a in plan:
            if a["calisan"] not in emp_id:
                continue
            ak = "%s:%s:%s:%s" % (pk, a["calisan"], a["gun"], a["bas"])
            aid = kimlik("assignments", ak)
            atamalar.append({"id": aid, "created_at": OLUSTURMA, "updated_at": None,
                             "plan_version_id": surumler[-1]["id"], "employee_id": emp_id[a["calisan"]],
                             "team_id": ekip_id[a["ekip"]], "shift_template_id": sab_id.get(a.get("sablon")),
                             "gun": a["gun"], "baslangic_saat": a["bas"], "bitis_saat": a["bit"],
                             "kilitli": False, "kaynak": "motor", "olusturan_user_id": None})
            for j, m in enumerate(a.get("molalar") or []):
                molalar.append(_satir("assignment_breaks", "%s:%d" % (ak, j), assignment_id=aid, tip=m["tip"],
                                      baslangic_saat=m["bas"], bitis_saat=m["bit"],
                                      dakika=int(round((m["bit"] - m["bas"]) * 60))))
            tarih = hafta + dt.timedelta(days=a["gun"])
            if tarih.month == HAFTA.month and tarih < HAFTA:        # ADALET_DENGESI: takvim ayi, plan haftasindan once
                t = sablon[a["sablon"]]
                d = devir[a["calisan"]]
                d["gece"] += 1 if _gece_sablonu(t)[0] else 0
                hs = _hafta_sonu_gunu(a["gun"], a["bas"], a["bit"])
                d["hafta_sonu"] += 1 if hs is not None else 0
                d["cumartesi"] += 1 if hs == 5 else 0
    pk = HAFTA.isoformat()
    planlar.append(_satir("plans", pk, department_id=ust["id"], hafta_baslangic=pk, durum="taslak",
                          demand_profile_id=dp["id"], secili_version_id=None, olusturan_user_id=None,
                          onaylayan_user_id=None, onay_zamani=None, yayin_zamani=None, kural_degerleri={}))
    veri["plans"], veri["plan_versions"], veri["assignments"], veri["assignment_breaks"] = planlar, surumler, atamalar, molalar
    veri["plan_locks"] = [_satir("plan_locks", "%s:%s:%s" % (pk, k["calisan"], k["gun"]), plan_id=planlar[-1]["id"],
                                 employee_id=emp_id[k["calisan"]], team_id=ekip_id.get(k.get("ekip")),
                                 tip=k.get("tip", "sabit"),
                                 gun=k["gun"], baslangic_saat=k.get("bas"), bitis_saat=k.get("bit"),
                                 ekleyen_user_id=None, **{"not": None})
                          for k in g.get("kilitler") or []]

    # ---- hesaplanmis dengeler (donem: plan ayi)
    veri["employee_balances"] = [_satir("employee_balances", "%s:%s" % (c["id"], HAFTA.strftime("%Y-%m")),
                                        employee_id=emp_id[c["id"]], donem=HAFTA.strftime("%Y-%m"),
                                        yil_ici_fazla_mesai_saat=c["yil_ici_fazla_mesai_saat"],
                                        devir_gece=devir[c["id"]]["gece"], devir_hafta_sonu=devir[c["id"]]["hafta_sonu"],
                                        devir_cumartesi=devir[c["id"]]["cumartesi"], devir_saat=0,
                                        hesaplanma_zamani="2026-10-11T23:00:00+03:00")
                                 for c in g["calisanlar"]]

    from tablolar import TABLOLAR
    veri["_meta"]["tablolar"] = {t["ad"]: len(veri[t["ad"]]) for t in TABLOLAR}
    veri["_meta"]["donusum"] = {"sezonluk_tam_zamanliya": sayac["sezonluk"], "stajyer_yari_zamanliya": sayac["stajyer"],
                                "gecmis_haftalar": [h.isoformat() for h in GECMIS],
                                "gecmis_kaynaklari": [k for k, _ in _gecmis_planlari(olcek)],
                                "katalogdan_sapan_uretici_bayraklari": farklar}
    # tablo sirasi tablolar.py ile ayni
    return {"_meta": veri["_meta"], **{t["ad"]: veri[t["ad"]] for t in TABLOLAR}}


def dosya_yolu(olcek):
    kisi = {1.0: 500, 0.1: 49}[olcek]
    return os.path.join(BURASI, "veri", "tshift-%d.json" % kisi)


def yaz(olcek):
    v = uret(olcek)
    yol = dosya_yolu(olcek)
    with io.open(yol, "w", encoding="utf-8", newline="\n") as f:
        json.dump(v, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return yol, v


if __name__ == "__main__":
    for o in (1.0, 0.1):
        yol, v = yaz(o)
        print("%s  %s" % (os.path.relpath(yol, BURASI), v["_meta"]["tablolar"]))
