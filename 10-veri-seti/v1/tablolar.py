# -*- coding: utf-8 -*-
"""
TShift veri seti v1 -- TABLO TANIMLARI (tek kaynak)

JSON Schema (`sema/tshift-veri-semasi.schema.json`), veri sozlugunun tablo
bolumleri (`VERI-SOZLUGU.md`) ve Excel import sablonunun kolonlari BU
dosyadan uretilir (`belgeler.py`). Bir kolon degisirse yalniz burasi
degisir; uc cikti birbirinden kopamaz. (Kod yorumlari ASCII; kullaniciya
giden metinler Turkce karakterli.)

Kaynak: sartname `02-spec/v1.4-master-spec.md` #8, su kararlarla:
  * M-16 (11 Ekim): her musteri ayri konteyner -> `tenant_id` YOK; `tenants`
    tek satirdir (firmanin kendisi).
  * K-58 (2 Ekim) + 14 Ekim kapanisi: sozlesme tipi yalniz `tam_zamanli` |
    `yari_zamanli`; kisiye saat yok; tam zamanlida haftalik GUN sayisi
    (5 | 6) sozlesmede.
  * Sartname #8'de olmayan ama motorun okudugu alanlar `yeni=True`
    (veri sozlugunde "Şartnameden farklar").

Kolon: (ad, tip, zorunlu, aciklama, ek)
  tip : uuid | text | int | numeric | bool | date | timestamptz | json | int[] | text[]
  ek  : enum=[...], ref="tablo", motor="motor girdisindeki karsiligi",
        yeni=True, ornek=..., json_sema={...}
Tablo: ad, bolum, kaynak (import | ayar | sistem | hesap), aciklama, kolonlar,
       ortak_yok (rule_types: birincil anahtar kod), yeni (tablo sartnamede yok).
"""

ORTAK = [
    ("id", "uuid", True, "Birincil anahtar.", {}),
    ("created_at", "timestamptz", True, "Kaydın oluşturulma zamanı.", {}),
    ("updated_at", "timestamptz", False, "Son güncelleme; hiç güncellenmediyse boş.", {}),
]

MOLA_POLITIKASI_SEMA = {
    "type": "array",
    "items": {"type": "object", "required": ["tip", "dakika", "adet", "ucretli"],
              "additionalProperties": False,
              "properties": {"tip": {"enum": ["yemek", "dinlenme"]},
                             "dakika": {"type": "integer", "minimum": 1},
                             "adet": {"type": "integer", "minimum": 1},
                             "ucretli": {"type": "boolean"}}}}

ACIK_SEMA = {
    "oneOf": [{"const": "7/24"},
              {"type": "array",
               "items": {"type": "object", "required": ["gunler", "bas", "bit"],
                         "additionalProperties": False,
                         "properties": {"gunler": {"type": "array",
                                                   "items": {"type": "integer", "minimum": 0, "maximum": 6}},
                                        "bas": {"type": "number", "minimum": 0, "maximum": 24},
                                        "bit": {"type": "number", "minimum": 0, "maximum": 48}}}}]}

TABLOLAR = [
    # ---- 8.1 firma (M-16: tek satir)
    {"ad": "tenants", "bolum": "8.1 Firma", "kaynak": "ayar",
     "aciklama": "Firmanın kendisi. M-16 ile her müşteri ayrı konteynerde olduğu için **tek satır**; "
                 "başka tablolar buna anahtar tutmaz.",
     "kolonlar": [
         ("ad", "text", True, "Firma adı.", {}),
         ("slug", "text", True, "Kısa ad (adres / alt alan adı).", {}),
         ("sektor_paketi", "text", True, "Kurulum sihirbazının yüklediği hazır kural seti; hiçbir kuralı bağlamaz.",
          {"enum": ["cagri_merkezi", "otel", "perakende", "saglik", "uretim", "bos"]}),
         ("birim_adi", "text", True, "Arayüzde \"departman\" yerine kullanılan kelime.",
          {"enum": ["Departman", "Şube", "Birim"]}),
         ("zaman_dilimi", "text", True, "IANA zaman dilimi.", {"motor": "kiraci_saat_dilimi"}),
         ("hafta_baslangic", "int", True, "Haftanın ilk günü (1 = Pazartesi). Motorda gün 0 bu gündür.", {}),
         ("sektor", "text", False, "**Yasal** sektör (K-26): gece 7,5 saat istisnasını açar. Boş = istisna yok.",
          {"enum": ["turizm", "ozel_guvenlik", "saglik", "petrol", None], "motor": "sektor"}),
         ("durum", "text", True, "Firma hesabının durumu.", {"enum": ["aktif", "askida", "deneme"]}),
         ("deneme_bitis", "date", False, "Deneme süresinin bitişi.", {}),
         ("cok_ekipli_sayim", "text", True, "K-50: birden çok ekibe üye çalışan bütün ekiplerine mi (`hepsi`), "
          "yalnız vardiyanın ekibine mi (`tek`) sayılır.",
          {"enum": ["hepsi", "tek"], "motor": "cok_ekipli_sayim", "yeni": True}),
     ]},
    # ---- 8.2 organizasyon
    {"ad": "departments", "bolum": "8.2 Organizasyon", "kaynak": "import",
     "aciklama": "Departmanlar; `ust_department_id` ile hiyerarşi. Plan bir departman için üretilir ve **alt "
                 "departmanlarını kapsar** (örnekte \"Operasyon\" → Satış, Back Office, Müşteri Hizmetleri).",
     "kolonlar": [
         ("ad", "text", True, "Görünen ad.", {}),
         ("kod", "text", True, "Kısa kod; dış sistemle eşleştirme anahtarı.", {"motor": "departmanlar[].id"}),
         ("ust_department_id", "uuid", False, "Üst departman (hiyerarşi). Boş = en üst.", {"ref": "departments"}),
         ("calisma_tipi", "text", True, "7/24 mü, saatli mi (`acik` alanından türer).",
          {"enum": ["yedi_yirmidort", "saatli"]}),
         ("acik", "json", False, "K-52 çalışma günleri ve saatleri: `\"7/24\"` ya da pencereler "
          "`[{gunler, bas, bit}]` (`bit` 24'ü aşabilir). Boş = kural uygulanmaz (üst departman gibi). "
          "Şartnamedeki `acilis_saat` / `kapanis_saat` bunun yerine geçti.",
          {"motor": "departmanlar[].acik", "yeni": True, "json_sema": ACIK_SEMA}),
         ("aktif", "bool", True, "Pasif departman planlanmaz.", {}),
     ]},
    {"ad": "teams", "bolum": "8.2 Organizasyon", "kaynak": "import",
     "aciklama": "Ekipler. Talep (`demand_cells`) ve vardiya şablonları ekibe bağlıdır; motorda \"ekip\".",
     "kolonlar": [
         ("department_id", "uuid", True, "Bağlı olduğu departman.", {"ref": "departments"}),
         ("ad", "text", True, "Görünen ad.", {}),
         ("kod", "text", True, "Kısa kod; motorda ekip kimliği.",
          {"motor": "calisanlar[].ekipler[], talep[].ekip, vardiya_sablonlari[].ekip"}),
         ("aciklama", "text", False, "Serbest açıklama.", {}),
         ("aktif", "bool", True, "Pasif ekip planlanmaz.", {}),
     ]},
    {"ad": "operational_roles", "bolum": "8.2 Organizasyon", "kaynak": "import",
     "aciklama": "Operasyonel roller (takım lideri vb.). `ROL_KAPSAMASI` kuralı bunları sayar.",
     "kolonlar": [
         ("ad", "text", True, "Görünen ad.", {}),
         ("kod", "text", True, "Kısa kod; motorda rol kimliği.", {"motor": "calisanlar[].operasyonel_rol"}),
         ("aciklama", "text", False, "Serbest açıklama.", {}),
     ]},
    {"ad": "skills", "bolum": "8.2 Organizasyon", "kaynak": "import",
     "aciklama": "Yetkinlikler (dil, ürün bilgisi…). `YETKINLIK_KAPSAMASI` kuralı bunları sayar.",
     "kolonlar": [
         ("ad", "text", True, "Görünen ad.", {}),
         ("kod", "text", True, "Kısa kod; motorda yetkinlik kimliği.", {"motor": "calisanlar[].yetkinlikler[]"}),
         ("aciklama", "text", False, "Serbest açıklama.", {}),
         ("sertifika_gerekli", "bool", True, "Öyleyse çalışanda geçerlilik tarihi tutulur.", {}),
     ]},
    # ---- 8.3 calisan
    {"ad": "employees", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "Çalışan kartı. LDAP / API / Excel import'unun ana tablosu; eşleştirme anahtarı `personel_no`.",
     "kolonlar": [
         ("personel_no", "text", True, "Firma sicil no — İK entegrasyonunun eşleştirme anahtarı; benzersiz. "
          "Motorda çalışan kimliği olarak gider.", {"motor": "calisanlar[].id"}),
         ("ad", "text", True, "Ad (veri setinde **uydurma**).", {}),
         ("soyad", "text", True, "Soyad (veri setinde **uydurma**).", {}),
         ("eposta", "text", False, "E-posta (veri setinde `.test` alan adı).", {}),
         ("telefon", "text", False, "Telefon (veri setinde uydurma).", {}),
         ("department_id", "uuid", True, "Departman (birincil ekibinin departmanı).", {"ref": "departments"}),
         ("birincil_team_id", "uuid", False, "Birincil ekip; `employee_teams`'te önceliği 1 olan.", {"ref": "teams"}),
         ("operational_role_id", "uuid", False, "Operasyonel rol.",
          {"ref": "operational_roles", "motor": "calisanlar[].operasyonel_rol"}),
         ("ise_giris", "date", True, "İşe giriş tarihi.", {}),
         ("isten_cikis", "date", False, "İşten çıkış tarihi; durum `ayrildi` ise dolu.", {}),
         ("durum", "text", True, "Pasif ve ayrılmış çalışana atama yapılmaz (`AKTIF_CALISAN`).",
          {"enum": ["aktif", "pasif", "ayrildi"], "motor": "calisanlar[].durum (aktifse gönderilmez)"}),
         ("user_id", "uuid", False, "Uygulamaya girişi varsa kullanıcı (kimlik tabloları veri setinde yok).", {}),
         ("dis_sistem_id", "text", False, "İK / LDAP sistemindeki kimlik.", {}),
         ("gece_calisma_onayi", "bool", True, "Gece 7,5 saati aşmaya yazılı onay (§6.3; sektör istisnasıyla birlikte).", {}),
         ("gece_calisma_onay_tarihi", "date", False, "Onayın tarihi.", {}),
         ("gece_calisma_onay_belge", "text", False, "Onay belgesi referansı.", {}),
         ("gece_calisamaz", "bool", True, "K-40: \"gece vardiyası yapamaz\" işareti (`GECE_UYGUNLUGU`). Kartta "
          "tutulur, tahmin edilmez.", {"motor": "calisanlar[].gece_calisamaz", "yeni": True}),
     ]},
    {"ad": "employee_contracts", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "Sözleşmeler (dönemsel; bir çalışanın birden çok sözleşmesi olabilir, motor plan haftasında "
                 "geçerli olanı kullanır). K-58: kişiye **saat tanımlanmaz** — tam zamanlı 45, yarı zamanlı baz 30 / "
                 "tavan 45 kanundan gelir.",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("tip", "text", True, "Sözleşme tipi (K-58: yalnız iki).",
          {"enum": ["tam_zamanli", "yari_zamanli"], "motor": "calisanlar[].sozlesme.tip"}),
         ("haftalik_gun", "int", False, "Tam zamanlının haftalık çalışma günü (5 | 6) — saat değil, çalışma düzeni; "
          "izin gününü saate çevirmek için (45/6 = 7,5; 45/5 = 9). Yarı zamanlıda boş. (K-58'in açık sorusu, "
          "14 Ekim: sözleşmede tutulur.)",
          {"enum": [5, 6, None], "motor": "calisanlar[].sozlesme.gun_sayisi", "yeni": True}),
         ("baslangic", "date", True, "Sözleşme başlangıcı.", {}),
         ("bitis", "date", False, "Sözleşme bitişi; boş = süresiz (sezonluk çalışanda dolu).", {}),
         ("aktif", "bool", True, "Yürürlükte mi.", {}),
     ]},
    {"ad": "employee_teams", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "Ekip üyelikleri (çoğul). K-50: çalışan üye olduğu **bütün** ekiplerin kapsamasına sayılır.",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("team_id", "uuid", True, "Ekip.", {"ref": "teams", "motor": "calisanlar[].ekipler[]"}),
         ("oncelik", "int", True, "1 = birincil ekip; motorda listedeki sıra.", {}),
     ]},
    {"ad": "employee_skills", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "Çalışanın yetkinlikleri.",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("skill_id", "uuid", True, "Yetkinlik.", {"ref": "skills", "motor": "calisanlar[].yetkinlikler[]"}),
         ("seviye", "int", True, "1–5.", {}),
         ("sertifika_bitis", "date", False, "Geçmişse yetkinlik sayılmaz.", {}),
     ]},
    {"ad": "employee_availability", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "Uygunluk takvimi: uygun olmadığı (sert) ya da tercih ettiği / etmediği (yumuşak) zamanlar.",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("tip", "text", True, "`uygun_degil` sert (`UYGUNLUK_TAKVIMI`); tercihler yumuşak.",
          {"enum": ["uygun_degil", "tercih_ediyor", "tercih_etmiyor"], "motor": "calisanlar[].uygunluk[].tip"}),
         ("tekrar", "text", True, "Her hafta mı, belli tarihler mi.", {"enum": ["haftalik", "tarihli"]}),
         ("gun", "int", False, "`haftalik` ise 0–6 (0 = Pazartesi).", {"motor": "calisanlar[].uygunluk[].gun"}),
         ("baslangic_tarih", "date", False, "`tarihli` ise.", {}),
         ("bitis_tarih", "date", False, "`tarihli` ise.", {}),
         ("baslangic_saat", "numeric", True, "Genişletilmiş saat (0–24).", {"motor": "calisanlar[].uygunluk[].bas"}),
         ("bitis_saat", "numeric", True, "Genişletilmiş saat (24'ü aşabilir).", {"motor": "calisanlar[].uygunluk[].bit"}),
         ("aciklama", "text", False, "Örnek: \"Üniversite dersi\".", {}),
     ]},
    {"ad": "leaves", "bolum": "8.3 Çalışan", "kaynak": "import",
     "aciklama": "İzinler. Motora yalnız plan haftasına düşen **tüm gün** izinler gider (K-31); onaylı olanlar "
                 "bağlar, öteki durumlar bilgi olarak gider.",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("tip", "text", True, "İzin tipi.", {"enum": ["yillik", "mazeret", "rapor", "ucretsiz", "dogum", "diger"],
                                              "motor": "calisanlar[].izinler[].tip"}),
         ("baslangic", "date", True, "İlk izin günü.", {}),
         ("bitis", "date", True, "Son izin günü (dahil).", {}),
         ("tum_gun", "bool", True, "Değilse saat aralığı (motora gitmez, K-31).", {}),
         ("baslangic_saat", "numeric", False, "`tum_gun` değilse.", {}),
         ("bitis_saat", "numeric", False, "`tum_gun` değilse.", {}),
         ("durum", "text", True, "Yalnız onaylı izin motoru bağlar.",
          {"enum": ["talep", "onayli", "reddedildi", "iptal"], "motor": "calisanlar[].izinler[].durum"}),
         ("onaylayan_user_id", "uuid", False, "Onaylayan kullanıcı.", {}),
         ("aciklama", "text", False, "Serbest açıklama.", {}),
     ]},
    {"ad": "employee_balances", "bolum": "8.3 Çalışan", "kaynak": "hesap", "yeni": True,
     "aciklama": "**Hesaplanmış ara sonuçlar** (şartname §8'de yok — öneri). Backend bunları plan geçmişinden "
                 "(yayınlanmış planların atamaları) ve PDKS ham verisinden (K-55) hesaplar; veri setinde hesaplanmış "
                 "hâli verilir. Dönem = takvim ayı (`ADALET_DENGESI` penceresi).",
     "kolonlar": [
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("donem", "text", True, "Takvim ayı, `YYYY-AA`.", {}),
         ("yil_ici_fazla_mesai_saat", "numeric", True, "Yıl başından plan haftasına kadar fazla mesai (K-55: PDKS "
          "hamından TShift hesabı). `YILLIK_FAZLA_MESAI_TAVANI` (270) bunu okur.",
          {"motor": "calisanlar[].yil_ici_fazla_mesai_saat"}),
         ("devir_gece", "int", True, "Bu ay plan haftasından önce tutulan gece vardiyası sayısı (`ADALET_DENGESI`).",
          {"motor": "calisanlar[].devir_yuk.gece"}),
         ("devir_hafta_sonu", "int", True, "Bu ay önce çalışılan hafta sonu günü sayısı (K-46 gün tanımı).",
          {"motor": "calisanlar[].devir_yuk.hafta_sonu"}),
         ("devir_cumartesi", "int", True, "Bu ay önce çalışılan cumartesi sayısı.",
          {"motor": "calisanlar[].devir_yuk.cumartesi"}),
         ("devir_saat", "numeric", True, "Saat boyutu — T-13 (yazılmadı); 0.", {"motor": "calisanlar[].devir_yuk.saat"}),
         ("hesaplanma_zamani", "timestamptz", True, "Ne zaman hesaplandı.", {}),
     ]},
    # ---- 8.4 vardiya ve kural
    {"ad": "shift_templates", "bolum": "8.4 Vardiya ve kural", "kaynak": "ayar",
     "aciklama": "Vardiya şablonları. Saatler **genişletilmiş saattir**: 23 – 32,25 = 23:00 – ertesi gün 08:15.",
     "kolonlar": [
         ("department_id", "uuid", False, "Boş = tüm departmanlar.", {"ref": "departments"}),
         ("team_id", "uuid", False, "Şablonun ekibi (motor şablonu ekibe bağlar). Boş = ekipsiz (kişinin ilk ekibi).",
          {"ref": "teams", "motor": "vardiya_sablonlari[].ekip", "yeni": True}),
         ("ad", "text", True, "Görünen ad.", {}),
         ("kod", "text", True, "Kısa kod; motorda şablon kimliği.", {"motor": "vardiya_sablonlari[].id"}),
         ("baslangic_saat", "numeric", True, "Başlangıç (0–24).", {"motor": "vardiya_sablonlari[].bas"}),
         ("bitis_saat", "numeric", True, "Bitiş; gece yarısını aşan vardiyada 24'ten büyük.",
          {"motor": "vardiya_sablonlari[].bit"}),
         ("mola_dk", "int", True, "Toplam mola süresi.", {"motor": "vardiya_sablonlari[].mola_dk"}),
         ("mola_politikasi", "json", False, "Mola tipleri, süreleri, adetleri (K-32). Boş = firma politikası.",
          {"motor": "vardiya_sablonlari[].mola_politikasi", "json_sema": MOLA_POLITIKASI_SEMA}),
         ("gunler", "int[]", False, "Kullanılabileceği günler (0 = Pazartesi). Boş = her gün.",
          {"motor": "vardiya_sablonlari[].gunler"}),
         ("gece_mi", "bool", True, "**Yasal** gece postası mı — yönetmelikten hesaplanır (md. 7/2), saklanır.", {}),
         ("gece_vardiyasi", "bool", False, "Firma işareti (K-40 / K-43): `true` yasal olmayan şablonu da gece sayar; "
          "`false` yasal geceyi geri alamaz.", {"motor": "vardiya_sablonlari[].gece_vardiyasi"}),
         ("aciklama", "text", False, "Serbest açıklama.", {"yeni": True}),
         ("renk", "text", False, "Takvim rengi.", {}),
         ("aktif", "bool", True, "Pasif şablon kullanılmaz.", {}),
     ]},
    {"ad": "rule_types", "bolum": "8.4 Vardiya ve kural", "kaynak": "sistem", "ortak_yok": True,
     "aciklama": "Kural kataloğu (sistem tablosu, firmadan bağımsız) — şartname §6'nın 41 satırı. Birincil anahtar `kod`.",
     "kolonlar": [
         ("kod", "text", True, "Kural kodu (birincil anahtar).", {"motor": "kurallar[].kod"}),
         ("ad", "text", True, "Görünen ad.", {}),
         ("aciklama", "text", True, "Katalogdaki tanım (şartname §6).", {}),
         ("tur", "text", True, "Varsayılan tür.", {"enum": ["SERT", "YUMUSAK"]}),
         ("kategori", "text", True, "Katalog bölümü.",
          {"enum": ["uygunluk", "sure", "gece", "kapsama", "adalet", "duzenleme", "fazla_mesai", "tercih"]}),
         ("yasal", "bool", True, "Kanundan mı geliyor (K-18). Satır bazlı kurallarda `false`; bayrak satırda.",
          {"motor": "kurallar[].yasal"}),
         ("kabul_edilebilir", "bool", False, "Yönetici bu ihlali kabul edip yayınlayabilir mi (K-20). Yumuşakta boş.",
          {"motor": "kurallar[].kabul_edilebilir"}),
         ("bayrak_satir_bazli", "bool", True, "Bayraklar her gereklilik satırında mı (§5.3).", {}),
         ("kapsam_seviyeleri", "text[]", True, "Değerin belirlenebildiği kademeler (S sistem, K kiracı, D departman, "
          "Z sözleşme tipi, C çalışan).", {}),
     ]},
    {"ad": "tenant_rules", "bolum": "8.4 Vardiya ve kural", "kaynak": "ayar",
     "aciklama": "Firmanın kural ayarları — her kural tipi için **tek satır**. Satır bazlı kurallarda "
                 "(`ROL_KAPSAMASI`, `YETKINLIK_KAPSAMASI`) her gereklilik `parametreler.gereklilikler[]` içinde; "
                 "motora her biri ayrı kural olarak gider.",
     "kolonlar": [
         ("rule_type_kod", "text", True, "Kural tipi.", {"ref": "rule_types", "motor": "kurallar[].kod"}),
         ("aktif", "bool", True, "Kapalı kural motora gönderilmez.", {"motor": "kurallar[].aktif"}),
         ("tur_gecersiz_kilma", "text", False, "Firma türü değiştirdiyse; boş = katalog türü.",
          {"enum": ["SERT", "YUMUSAK", None], "motor": "kurallar[].tur"}),
         ("agirlik", "int", False, "Yumuşaksa özel ağırlık; boş = profil ağırlığı.", {}),
         ("parametreler", "json", True, "Kural parametreleri. Satır bazlıda `{gereklilikler: [...]}`.",
          {"motor": "kurallar[].parametreler"}),
         ("not", "text", False, "Neden değiştirildi.", {}),
     ]},
    {"ad": "plan_profiles", "bolum": "8.4 Vardiya ve kural", "kaynak": "ayar",
     "aciklama": "Plan profilleri ve yumuşak kural ağırlıkları (§5.4).",
     "kolonlar": [
         ("kod", "text", True, "Profil.", {"enum": ["DENGELI", "KAPSAMA", "CALISAN"], "motor": "profil"}),
         ("ad", "text", True, "Görünen ad.", {}),
         ("aciklama", "text", False, "Kullanıcıya açıklama.", {}),
         ("agirliklar", "json", True, "Kural kodu → ağırlık.", {"motor": "agirliklar"}),
         ("varsayilan_mi", "bool", True, "Varsayılan profil (tek).", {}),
     ]},
    # ---- 8.5 talep
    {"ad": "demand_profiles", "bolum": "8.5 Talep", "kaynak": "import",
     "aciklama": "Talep profilleri (\"Normal hafta\", \"Yaz sezonu\"…). Plan bir profili seçer.",
     "kolonlar": [
         ("department_id", "uuid", True, "Departman (üst departman olabilir; hücreler ekibe bağlı).", {"ref": "departments"}),
         ("ad", "text", True, "Görünen ad.", {}),
         ("kaynak", "text", True, "Talep nereden geldi.", {"enum": ["dogrudan", "hacim", "gecmis"]}),
         ("kapanma_payi", "numeric", False, "Erlang C için (kaynak = hacim).", {}),
         ("aktif", "bool", True, "Kullanımda mı.", {}),
     ]},
    {"ad": "demand_cells", "bolum": "8.5 Talep", "kaynak": "import",
     "aciklama": "Saatlik talep: ekip × gün × saat için asgari (sert) ve hedef (yumuşak; üstü K-67 ile sert) kişi.",
     "kolonlar": [
         ("demand_profile_id", "uuid", True, "Talep profili.", {"ref": "demand_profiles"}),
         ("team_id", "uuid", True, "Ekip.", {"ref": "teams", "motor": "talep[].ekip"}),
         ("gun", "int", True, "0–6 (0 = Pazartesi).", {"motor": "talep[].gun"}),
         ("saat", "int", True, "0–23.", {"motor": "talep[].saat"}),
         ("asgari_kisi", "int", True, "Altına inilemez (`ASGARI_KAPSAMA`).", {"motor": "talep[].asgari"}),
         ("hedef_kisi", "int", True, "İdeal sayı (`HEDEF_KAPSAMA`; üstü `HEDEF_ASIMI`).", {"motor": "talep[].hedef"}),
         ("elle_duzeltildi", "bool", True, "Erlang'dan üretilen sayı elle değiştirildi mi.", {}),
     ]},
    # ---- 8.6 plan
    {"ad": "plans", "bolum": "8.6 Plan", "kaynak": "sistem",
     "aciklama": "Haftalık plan (departman + hafta). Örnekte iki yayınlanmış geçmiş hafta ve üretilecek hafta.",
     "kolonlar": [
         ("department_id", "uuid", True, "Planın departmanı; alt departmanları da kapsar.", {"ref": "departments"}),
         ("hafta_baslangic", "date", True, "Pazartesi.", {"motor": "hafta_baslangic"}),
         ("durum", "text", True, "Plan durumu.",
          {"enum": ["taslak", "adaylar_hazir", "secildi", "onayda", "onayli", "yayinda", "arsiv"]}),
         ("demand_profile_id", "uuid", False, "Talep profili.", {"ref": "demand_profiles"}),
         ("secili_version_id", "uuid", False, "Seçilen versiyon.", {"ref": "plan_versions"}),
         ("olusturan_user_id", "uuid", False, "Kimlik tabloları veri setinde yok; boş.", {}),
         ("onaylayan_user_id", "uuid", False, "Kimlik tabloları veri setinde yok; boş.", {}),
         ("onay_zamani", "timestamptz", False, "Onay zamanı.", {}),
         ("yayin_zamani", "timestamptz", False, "Yayın zamanı.", {}),
         ("kural_degerleri", "json", False, "K-68: bu planın kural değerleri (zaman kademesi; tatil / sezon). Örnek "
          "`{\"HEDEF_ASIMI\": {\"ust_tolerans\": 1}}`. Genellemesi T-81.",
          {"motor": "kurallar[].parametreler (birleştirilir)", "yeni": True}),
     ]},
    {"ad": "plan_versions", "bolum": "8.6 Plan", "kaynak": "sistem",
     "aciklama": "Bir planın aday versiyonları; seçili olan yayınlanır.",
     "kolonlar": [
         ("plan_id", "uuid", True, "Plan.", {"ref": "plans"}),
         ("plan_run_id", "uuid", False, "Üreten motor koşusu (veri setinde yok).", {}),
         ("profil_kod", "text", True, "Profil.", {"enum": ["DENGELI", "KAPSAMA", "CALISAN"]}),
         ("metrikler", "json", True, "Özet metrikler.", {}),
         ("secili_mi", "bool", True, "Seçili versiyon.", {}),
         ("ai_aciklama", "text", False, "Üretilmiş özet.", {}),
     ]},
    {"ad": "assignments", "bolum": "8.6 Plan", "kaynak": "sistem",
     "aciklama": "Atamalar. Yayınlanmış geçen haftanın atamaları motora `gecmis_vardiyalar` (gün −7…−1) olarak gider.",
     "kolonlar": [
         ("plan_version_id", "uuid", True, "Versiyon.", {"ref": "plan_versions"}),
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees"}),
         ("team_id", "uuid", True, "Vardiyanın ekibi.", {"ref": "teams"}),
         ("shift_template_id", "uuid", False, "Şablon; serbest saatte boş.", {"ref": "shift_templates"}),
         ("gun", "int", True, "0–6.", {"motor": "calisanlar[].gecmis_vardiyalar[].gun (geçen hafta: gün − 7)"}),
         ("baslangic_saat", "numeric", True, "Genişletilmiş saat.", {"motor": "calisanlar[].gecmis_vardiyalar[].bas"}),
         ("bitis_saat", "numeric", True, "Genişletilmiş saat.", {"motor": "calisanlar[].gecmis_vardiyalar[].bit"}),
         ("kilitli", "bool", True, "Elle yapılan atamalar kilitli.", {}),
         ("kaynak", "text", True, "Atamanın kaynağı.", {"enum": ["motor", "manuel", "sabit", "devir"]}),
         ("olusturan_user_id", "uuid", False, "Manuelse.", {}),
     ]},
    {"ad": "assignment_breaks", "bolum": "8.6 Plan", "kaynak": "sistem",
     "aciklama": "Atamanın molaları.",
     "kolonlar": [
         ("assignment_id", "uuid", True, "Atama.", {"ref": "assignments"}),
         ("tip", "text", True, "Mola tipi (motor çıktısında var).", {"enum": ["yemek", "dinlenme"], "yeni": True}),
         ("baslangic_saat", "numeric", True, "Genişletilmiş saat.", {}),
         ("bitis_saat", "numeric", True, "Genişletilmiş saat.", {}),
         ("dakika", "int", True, "Süre.", {}),
     ]},
    {"ad": "plan_locks", "bolum": "8.6 Plan", "kaynak": "sistem",
     "aciklama": "Kilitler: yöneticinin \"bunu buraya koy\" (`sabit`) ya da \"koyma\" (`yasak`) dediği atamalar.",
     "kolonlar": [
         ("plan_id", "uuid", True, "Plan.", {"ref": "plans"}),
         ("employee_id", "uuid", True, "Çalışan.", {"ref": "employees", "motor": "kilitler[].calisan"}),
         ("team_id", "uuid", False, "Kilidin ekibi (motor kilidi ekiple alır).",
          {"ref": "teams", "motor": "kilitler[].ekip", "yeni": True}),
         ("tip", "text", True, "`sabit` = buraya koy; `yasak` = koyma.", {"enum": ["sabit", "yasak"]}),
         ("gun", "int", True, "0–6.", {"motor": "kilitler[].gun"}),
         ("baslangic_saat", "numeric", False, "Genişletilmiş saat.", {"motor": "kilitler[].bas"}),
         ("bitis_saat", "numeric", False, "Genişletilmiş saat.", {"motor": "kilitler[].bit"}),
         ("ekleyen_user_id", "uuid", False, "Kimlik tabloları veri setinde yok; boş.", {}),
         ("not", "text", False, "Serbest not.", {}),
     ]},
]

# Excel import sablonuna giren tablolar (Yilmaz'in import'u calisan tarafini doldurur).
EXCEL_TABLOLARI = ["employees", "employee_contracts", "employee_teams", "employee_skills",
                   "employee_availability", "leaves"]


def tablo(ad):
    for t in TABLOLAR:
        if t["ad"] == ad:
            return t
    raise KeyError(ad)


def kolonlar(t):
    """Tablonun butun kolonlari (ortak + kendi)."""
    return ([] if t.get("ortak_yok") else ORTAK) + t["kolonlar"]


# ----------------------------------------------------------------------
# Excel import sablonu -- DOGAL ANAHTARLARLA (IK dosyasinda bizim UUID'lerimiz
# olmaz): calisan personel_no ile, ekip / departman / rol / yetkinlik kodla.
# Her sayfa: (sayfa adi, tablo, [(excel kolonu, tablo kolonu ya da donusum)])
# Donusum: "ref:<tablo>.kod" -> kod uzerinden id; "calisan" -> personel_no.
# ----------------------------------------------------------------------
EXCEL_SAYFALARI = [
    ("Calisanlar", "employees", [
        ("personel_no", "personel_no"), ("ad", "ad"), ("soyad", "soyad"), ("eposta", "eposta"),
        ("telefon", "telefon"), ("departman_kodu", "ref:departments.kod:department_id"),
        ("birincil_ekip_kodu", "ref:teams.kod:birincil_team_id"),
        ("rol_kodu", "ref:operational_roles.kod:operational_role_id"), ("ise_giris", "ise_giris"),
        ("isten_cikis", "isten_cikis"), ("durum", "durum"), ("dis_sistem_id", "dis_sistem_id"),
        ("gece_calisamaz", "gece_calisamaz"), ("gece_calisma_onayi", "gece_calisma_onayi"),
        ("gece_calisma_onay_tarihi", "gece_calisma_onay_tarihi"),
        ("gece_calisma_onay_belge", "gece_calisma_onay_belge")]),
    ("Sozlesmeler", "employee_contracts", [
        ("personel_no", "calisan"), ("tip", "tip"), ("haftalik_gun", "haftalik_gun"),
        ("baslangic", "baslangic"), ("bitis", "bitis"), ("aktif", "aktif")]),
    ("Ekip_Uyelikleri", "employee_teams", [
        ("personel_no", "calisan"), ("ekip_kodu", "ref:teams.kod:team_id"), ("oncelik", "oncelik")]),
    ("Yetkinlikler", "employee_skills", [
        ("personel_no", "calisan"), ("yetkinlik_kodu", "ref:skills.kod:skill_id"), ("seviye", "seviye"),
        ("sertifika_bitis", "sertifika_bitis")]),
    ("Uygunluk", "employee_availability", [
        ("personel_no", "calisan"), ("tip", "tip"), ("tekrar", "tekrar"), ("gun", "gun"),
        ("baslangic_tarih", "baslangic_tarih"), ("bitis_tarih", "bitis_tarih"),
        ("baslangic_saat", "baslangic_saat"), ("bitis_saat", "bitis_saat"), ("aciklama", "aciklama")]),
    ("Izinler", "leaves", [
        ("personel_no", "calisan"), ("tip", "tip"), ("baslangic", "baslangic"), ("bitis", "bitis"),
        ("tum_gun", "tum_gun"), ("baslangic_saat", "baslangic_saat"), ("bitis_saat", "bitis_saat"),
        ("durum", "durum"), ("aciklama", "aciklama")]),
]
