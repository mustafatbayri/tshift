cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/08-motor-testleri/gercekci-veri-seti && python3 - <<'PYEOF'
import io
p="kalite-olc.py"
s=io.open(p,encoding="utf-8").read()
R=[]
R.append(('''    varsayilan   : urunun kostugu hal (iki asama acik)
                   ⚠ 6 Ekim, K-61: urunun hali artik ONCE FAZLA MESAISIZ
                     arar. `varsayilan`, `profil_*`, `cift_butce`, `lp_guclu`
                     bu tarihten sonra onu ICERIR; 6 Ekim oncesinin hali
                     `fm_once_kapali`. Eski kayit yapilandirmalari
                     (k59_hali, a_*, sabit_mola_480, mola_*, b_*, oran_90,
                     eski_urun_hali, fm_agirlik_*) kapali sabitlenmistir:
                     olctukleri sey degismesin. Her kosunun kaydinda
                     `once_fazla_mesaisiz` alani o kosuda acik miydi soyler
                     (alan yoksa kosu 6 Ekim oncesidir: kapali).
''','''    varsayilan   : urunun kostugu hal (iki asama acik)
                   ⚠ 6 Ekim, K-61: urunun hali artik ONCE FAZLA MESAISIZ
                     arar. `varsayilan`, `profil_*`, `cift_butce`, `lp_guclu`
                     bu tarihten sonra onu ICERIR; 6 Ekim oncesinin hali
                     `fm_once_kapali`. Eski kayit yapilandirmalari
                     (k59_hali, a_*, sabit_mola_480, mola_*, b_*, oran_90,
                     eski_urun_hali, fm_agirlik_*) kapali sabitlenmistir:
                     olctukleri sey degismesin. Her kosunun kaydinda
                     `once_fazla_mesaisiz` alani kosuda secenegin ACIK olup
                     olmadigini soyler (ayar; uygulanip uygulanmadigi
                     `fazla_mesai_once_sifir` alanindadir). Alan 6 Ekim
                     22:45'ten sonraki kayitlarda var; daha eski kayitlarda
                     secenek `ayar` sozlugunden okunur (bulgu 21'in
                     kaydinda acikca `true`, ondan oncekilerde yok = kapali).
                   ⚠ 7 Ekim, O-18: 6 Ekim gecesi olculen hal SERT KESIMDI
                     (fazla mesaisiz plan bulununca fazla mesai butun
                     asamalarda 0'da tutuluyordu). Bu Mustafa'nin ilkesini
                     cigniyordu (hakem agirliklardir); urun yolu duzeltildi:
                     bulunan plan yalniz baslangic noktasi, alanlar geri
                     acilir. Sert kesim olcum yapilandirmasi olarak duruyor
                     (`fm_sert`, `fm_sert_kapsama`; bulgu 21'in kaydi bu
                     haldir). Duzeltilmis yolun tam olcekli olcumu: `fm_once`
                     / `fm_once_kapsama` (= `varsayilan` / `profil_kapsama`).
'''))
R.append(('''    # ⚠ K-61 (6 Ekim, Mustafa: "Evet"): "ONCE FAZLA MESAISIZ" urunun
    #   varsayilani. Urun halini olcen yapilandirmalar (`varsayilan`,
    #   `profil_*`, `cift_butce`, `lp_guclu`) onu motorun varsayilanindan
    #   ALIR. 6 Ekim oncesinin kayit yapilandirmalari `KAPALI` tasir.
    "varsayilan":   ("urunun kostugu hal: once fazla mesaisiz (K-61), molalar sabitken iyilestirme (K-59, %80), mola adimi (K-60)",
                     {}, {}),
''','''    # ⚠ K-61 (6 Ekim, Mustafa: "Evet"): "ONCE FAZLA MESAISIZ" urunun
    #   varsayilani. Urun halini olcen yapilandirmalar (`varsayilan`,
    #   `profil_*`, `cift_butce`, `lp_guclu`) onu motorun varsayilanindan
    #   ALIR. 6 Ekim oncesinin kayit yapilandirmalari `KAPALI` tasir.
    # ⚠ O-18 (7 Ekim): urun yolu = once fazla mesaisiz ARA, bulunca o plandan
    #   agirlikli aramaya devam et (alanlar acik). Sert kesim (`SERT`) yalniz
    #   olcum; bulgu 21 o haldir.
    "varsayilan":   ("urunun kostugu hal: once fazla mesaisiz, bulunca o plandan agirlikli arama (K-61/O-18), molalar sabitken iyilestirme (K-59, %80), mola adimi (K-60)",
                     {}, {}),
    "fm_once":      ("URUN YOLU (7 Ekim): once fazla mesaisiz plan, bulunursa ipucu -- alanlar GERI ACILIR, karari agirliklar verir; DENGELI (= varsayilan; adi olcumun kaydi icin)",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False}, {}),
    "fm_once_kapsama": ("URUN YOLU (7 Ekim), KAPSAMA profili (= profil_kapsama)",
                     {"fazla_mesai_once_sifir": True, "fazla_mesai_sifirda_tut": False}, {"profil": "KAPSAMA"}),
    "fm_sert":      ("SERT KESIM (6 Ekim gecesinin hali, bulgu 21; OLCUM): fazla mesaisiz plan bulunursa fazla mesai butun asamalarda 0'da TUTULUR; DENGELI",
                     dict(SERT), {}),
    "fm_sert_kapsama": ("SERT KESIM (bulgu 21; OLCUM), KAPSAMA profili",
                     dict(SERT), {"profil": "KAPSAMA"}),
'''))
R.append(('''KAPALI = {"fazla_mesai_once_sifir": False}     # 6 Ekim oncesinin yolu (kayit yapilandirmalari)
''','''KAPALI = {"fazla_mesai_once_sifir": False}     # 6 Ekim oncesinin yolu (kayit yapilandirmalari)
SERT = {"fazla_mesai_once_sifir": True,        # 6 Ekim gecesinin sert kesimi (bulgu 21; OLCUM)
        "fazla_mesai_sifirda_tut": True}
'''))
R.append(('''    #   K-61 (6 Ekim): bu ikisi artik `varsayilan` / `profil_kapsama` ile
    #   AYNI kosuyu verir; bulgu 21'in kaydi (kalite-olcumu-95-fmsifir-900.json)
    #   bu adlarla yazildigi icin duruyorlar.
    "fm_once_sifir": ("bulgu 21 kaydi (K-61'den beri = varsayilan): once fazla mesaisiz plan, DENGELI -- bulunursa fazla mesai 0'da kalir; bulunamazsa onceki yol",
                     {"fazla_mesai_once_sifir": True}, {}),
    "fm_once_sifir_kapsama": ("bulgu 21 kaydi (K-61'den beri = profil_kapsama): once fazla mesaisiz plan, KAPSAMA profili",
                     {"fazla_mesai_once_sifir": True}, {"profil": "KAPSAMA"}),
''','''    #   Bulgu 21'in kaydi (kalite-olcumu-95-fmsifir-900.json) bu adlarla
    #   yazildi. O kosuda secenek 6 Ekim gecesinin SERT KESIMIYDI (O-18):
    #   ayni olcumu bugun `fm_sert` / `fm_sert_kapsama` verir; bu ikisi
    #   kaydin adlari olarak sert kesime SABITLENDI (olctukleri degismesin).
    "fm_once_sifir": ("bulgu 21 kaydi (6 Ekim, sert kesim = fm_sert): once fazla mesaisiz plan, DENGELI -- bulunursa fazla mesai 0'da TUTULUR; bulunamazsa onceki yol",
                     dict(SERT), {}),
    "fm_once_sifir_kapsama": ("bulgu 21 kaydi (6 Ekim, sert kesim = fm_sert_kapsama): KAPSAMA profili",
                     dict(SERT), {"profil": "KAPSAMA"}),
'''))
R.append(('''    "mola_adimi_tam": ("mola adimi TAM (bulgu 18 kaydi; 600 sn'de = varsayilan): 480 sn iyilestirme, atamalar SABIT, kanitli optimuma kadar",''',
'''    "mola_adimi_tam": ("mola adimi TAM (bulgu 18 kaydi; 600 sn'de 6 Ekim oncesinin varsayilani -- once fazla mesaisiz KAPALI): 480 sn iyilestirme, atamalar SABIT, kanitli optimuma kadar",'''))
R.append(('''    "ipucu_kapali": ("birinci asama (gecerli plan ipucu) kapali",
                     {"iki_asama_esigi": 10 ** 9}, {}),''','''    "ipucu_kapali": ("birinci asama (gecerli plan ipucu) kapali -- K-61'den beri 'once fazla mesaisiz' da birinci asamada oldugundan o da kapali: varsayilandan IKI sey farkli",
                     {"iki_asama_esigi": 10 ** 9}, {}),'''))
R.append(('''    ⚠ Secenek acik oldugu halde motor denemediyse kosu fazla mesaisiz aramayi
      YAPMAMISTIR -- bu SESSIZ gecmez, satira yazilir. Iki sebep:
        * deneme hic yapilmadi (iki asama devreye girmedi: kucuk olcek,
          baslangic plani; ya da daraltilacak fazla mesai degiskeni yok:
          CALISAN profili, yari zamanli kadro)  -> cikti None
        * agirlik kosulu tutmadi (K-61, hakem agirliklardir)
                                               -> `uygulandi: False`"""
    if not ayar.get("fazla_mesai_once_sifir"):
        return None
    f = s.get("fazla_mesai_once_sifir")
    if not f:
        return ("once fazla mesaisiz: UYGULANMADI (iki asama yok ya da daraltilacak fazla mesai "
                "degiskeni yok) -- bu kosuda fazla mesaisiz arama yapilmadi")
    if f.get("uygulandi") is False:
        return ("once fazla mesaisiz: UYGULANMADI -- agirlik kosulu tutmadi (fazla mesai dakikasi %s, "
                "oteki en buyuk agirlik %s); karari agirlikli arama verdi"
                % (f.get("fazla_mesai_agirligi"), f.get("en_buyuk_oteki_agirlik")))
    if f["bulundu"]:
        sonuc = "BULUNDU -- fazla mesai butun asamalarda 0"
    elif f["kanitlandi_yok"]:''','''    ⚠ Secenek acik oldugu halde motor denemediyse kosu fazla mesaisiz aramayi
      YAPMAMISTIR -- bu SESSIZ gecmez, satira yazilir: deneme hic yapilmadi
      (iki asama devreye girmedi: kucuk olcek, baslangic plani; ya da
      daraltilacak fazla mesai degiskeni yok: CALISAN profili, yari zamanli
      kadro) -> cikti None.
    O-18 (7 Ekim): bulununca iki hal var -- urun yolu (ipucu, alanlar geri
      acildi, karari agirliklar verdi) ve sert kesim (`sifirda_tutuldu`,
      olcum). Eski kayitlarda (6 Ekim) alan yok: o kosular sert kesimdi."""
    if not ayar.get("fazla_mesai_once_sifir"):
        return None
    f = s.get("fazla_mesai_once_sifir")
    if not f:
        return ("once fazla mesaisiz: UYGULANMADI (iki asama yok ya da daraltilacak fazla mesai "
                "degiskeni yok) -- bu kosuda fazla mesaisiz arama yapilmadi")
    if f["bulundu"]:
        if f.get("sifirda_tutuldu", True):
            sonuc = "BULUNDU -- SERT KESIM: fazla mesai butun asamalarda 0'da tutuldu (olcum)"
        else:
            sonuc = "BULUNDU -- ipucu oldu, alanlar geri acildi; karari agirliklar verdi"
    elif f["kanitlandi_yok"]:'''))
R.append(('''         # K-61: secenek varsayilandan da gelebilir; kosuda ACIK MIYDI?
         "once_fazla_mesaisiz": bool(etkin.get("fazla_mesai_once_sifir")),''','''         # K-61: secenek varsayilandan da gelebilir; kosuda ACIK MIYDI?
         # (AYAR. Uygulanip uygulanmadigi `fazla_mesai_once_sifir`te.)
         "once_fazla_mesaisiz": bool(etkin.get("fazla_mesai_once_sifir")),
         # O-18: sert kesim mi (olcum) -- urun yolunda False.
         "sert_kesim": bool(etkin.get("fazla_mesai_sifirda_tut")),'''))
for old,new in R:
    assert s.count(old)==1, old[:80]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
python3 -c "import ast,io;ast.parse(io.open('kalite-olc.py',encoding='utf-8').read());print('syntax ok')"; grep -n "fm_once\b\|fm_sert\|SERT\b" kalite-olc.py | head -20; grep -n "VARSAYILAN_SECIM\|def ozet" kalite-olc.py | head