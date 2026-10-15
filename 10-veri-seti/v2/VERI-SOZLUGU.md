# TShift veri seti v2 — veri sözlüğü

> Yazılım ekibine (Yılmaz: LDAP / API / Excel import'u ve kuyruk) ve ürün
> tarafına. Bu dosya `belgeler.py` ile **üretilir** — elle düzeltme
> yapmayın; değişiklik `tablolar.py`'ye (tablolar) ya da `belgeler.py`'deki
> giriş metnine yazılır.

## İçindekiler

1. Bu klasör ne
2. Dosyalar
3. Veri setinin içeriği
4. Uyulan kararlar
5. Şartnameden farklar (öneri — şartnameye işlenecek)
6. Açık sorular
7. Motor girdisine dönüşüm
8. Bulgular (veri seti kurulurken çıkanlar)
9. Yeniden üretme ve test
10. Tablolar (kolon kolon)

## 1 · Bu klasör ne

**v2 (14 Ekim akşamı)** — v1'den farkı iki alan: `employee_contracts.haftalik_saat`
yarı zamanlıda **zorunlu** (K-71: sözleşme süresi; motor çalışanı bu süreye
getirmeye çalışır) ve `employee_teams.oncelik` eşit olabilen çok ekipli kişiler
(K-72: eşit öncelik = gezici; motor `birincil_ekip`i türetir). İsimler ve öteki
tablolar v1 ile aynı. v1 dondu (`../v1/`), referansı onu alanlar için durur.

Çalışan verisi ve planın bütün girdisi **şartname §8'in tablolarında**,
gerçekçi bir çağrı merkezi örneğiyle: 500 kişi, üç ekip, iki yayınlanmış
geçmiş hafta, üretilecek hafta. İsimler, e-postalar, telefonlar ve İK
kimlikleri **uydurmadır** (Mustafa, 13 Ekim: *"isimler dışında gerçekçi"*);
geri kalan her şey ölçümlerin kullandığı sahneden gelir.

İki kullanımı var:

- **Yazılım:** import'un (LDAP / API / Excel) dolduracağı tabloların biçimi
  ve örnek verisi; JSON Schema ile doğrulanır; Excel örneği aynı veriyi
  import dosyası biçiminde verir.
- **Motor testleri:** bundan sonra testler ve ölçümler bu dosyadan koşar
  (`donustur.py` motor girdisini kurar); veri her seferinde bellekte
  yeniden üretilmez (Mustafa, 13 Ekim 23:20).

## 2 · Dosyalar

| dosya | ne |
|---|---|
| `veri/tshift-500.json` | 500 kişilik veri seti (bütün tablolar, tek dosya) |
| `veri/tshift-49.json` | 49 kişilik küçük kopya (0,1 ölçek; hızlı testler) |
| `sema/tshift-veri-semasi.schema.json` | JSON Schema 2020-12 — her tablo `$defs` altında |
| `excel/tshift-calisan-import-ornegi.xlsx` | Çalışan tarafının Excel import örneği (doğal anahtarlarla) |
| `tablolar.py` | Tablo tanımları — **tek kaynak** (şema, sözlük, Excel buradan) |
| `uret.py` | Veri setini üretir (tohumlu; aynı girdiyle aynı dosya) |
| `donustur.py` | Tablolar → motor girdisi (backend'in yapacağı işin referansı) |
| `belgeler.py` | Şema, bu sözlük ve Excel'i üretir |
| `testler/test_veri_seti.py` | Bütünlük, şema, dönüştürücü ve çözülebilirlik testleri |

## 3 · Veri setinin içeriği

- **Firma:** Örnek Çağrı Merkezi A.Ş. (tek satır; M-16). Plan haftası
  **12 Ekim 2026** (Pazartesi = gün 0).
- **Organizasyon:** "Operasyon" üst departmanı; altında Satış (7/24), Back
  Office (7/24) ve Müşteri Hizmetleri (hafta içi 07–23, hafta sonu 08–19).
  Plan üst departman için üretilir ve üçünü birlikte kapsar (çift yetkinlikli
  çalışanlar iki ekibe sayılır, K-50).
- **Çalışanlar:** 500 kişi; 354 tam zamanlı, 146 yarı zamanlı
  (sözleşme süreleri 16 / 20 / 24 / 30 saat; K-71); 12 pasif, 4 ayrılmış;
  10 kişi iki ekipte (2 gezici — eşit öncelik, K-72); 60 kişi
  "gece çalışamaz".
- **Vardiya şablonları:** 17 (ekip başına sabah / ara / akşam / gece /
  uzun / kısa…), genişletilmiş saatle.
- **Kurallar:** katalogdaki 41 kuralın tamamı firmada tanımlı (41
  satır; rol ve yetkinlik kapsaması satır bazlı gereklilikler).
- **Talep:** "Normal hafta (Ekim 2026)" profili, 415 hücre (ekip × gün ×
  saat).
- **Geçmiş:** iki yayınlanmış hafta (28 Eylül, 5 Ekim) — 4804 atama,
  17782 mola. Bunlar motora `gecmis_vardiyalar` (gün −14…−1) olarak gider;
  Ekim'in ilk 11 gününden adalet devri (`employee_balances`) hesaplanır.
- **Kilitler:** üretilecek haftada 6 kilit (sabit ve yasak).

## 4 · Uyulan kararlar

| karar | veri setinde |
|---|---|
| **M-16** (11 Ekim): her müşteri ayrı konteyner | `tenant_id` hiçbir tabloda yok; `tenants` tek satır |
| **K-58** (2 Ekim) + 14 Ekim kapanışı | Sözleşme tipi yalnız `tam_zamanli` / `yari_zamanli`; tam zamanlıya saat yok (45 kanundan), haftalık gün (5 / 6) sözleşmede. Eski "sezonluk" 13 kişi → tam zamanlı (sözleşme bitişi 31.12.2026), "stajyer" 16 kişi → yarı zamanlı |
| **K-71** (14 Ekim, v2) | Yarı zamanlının **sözleşme süresi** `employee_contracts.haftalik_saat`ta (zorunlu; 16 / 20 / 24 / 30 saat, en çok emsalin 2/3'ü). Süre **müsaitlikle tutarlı** üretilir (üst sınır = uygun gün × 9 sa; 2 gün müsait öğrenciye 30 saat yazılmaz — 14 Ekim 20:45 düzeltmesi). Motor çalışanı bu süreye getirmeye çalışır (`TERCIH_KARSILAMA`, yumuşak, 2.000 puan / boşa ödenen saat). Mevzuat: İş K. m. 13, Kısmi Süreli Çalışma Yön. m. 6 (T-83; hukukçu teyidi bekliyor). Çağrı üzerine çalışma (m. 14) **kapsam dışı** |
| **K-72** (14 Ekim, v2) | `EKIP_SUREKLILIGI`: çok ekipli kişi **birincil ekibinde** (en düşük `oncelik`) çalışsın; öncelikler eşitse kişi **gezici**, kural uygulanmaz. Motor girdisinde türetilmiş `birincil_ekip` |
| **K-70** (14 Ekim) | `PLAN_KARARLILIGI` yalnız **aynı haftanın yeniden planlanmasında** (`mevcut_plan` verildiğinde; K-54 akışı), birim kişi-gün. Veri setinde yeniden planlama sahnesi yok (plan koşusu girdisi); haftadan haftaya benzerlik arayüzün işi (klonla + kilitle) |
| **K-50** çok ekipli sayım | `employee_teams` çoğul; firmada `cok_ekipli_sayim = hepsi` |
| **K-52** departman çalışma saatleri | `departments.acik` |
| **K-40** gece çalışamaz | `employees.gece_calisamaz` |
| **K-55** geçmişin kaynağı | TShift'in kendi yayınlanmış planları (`plans` / `assignments`); yıl içi fazla mesai PDKS'ten hesaplanır → `employee_balances` |
| **K-67** hedef aşımı sert | `tenant_rules`'ta `HEDEF_ASIMI` katalog türünde (SERT); merdiven tabanı referans üretmek için onu yumuşatır |
| **K-68** üst tolerans plan bazında | `plans.kural_degerleri` (örnekte boş) |

## 5 · Şartnameden farklar (öneri — şartnameye işlenecek)

Şartname §8'de **olmayan**, ama motorun okuduğu ya da kararla gelen alanlar
(şemada `x-sartnamede-yok: true`):

- `tenants.cok_ekipli_sayim` — K-50: birden çok ekibe üye çalışan bütün ekiplerine mi (`hepsi`), yalnız vardiyanın ekibine mi (`tek`) sayılır.
- `departments.acik` — K-52 çalışma günleri ve saatleri: `"7/24"` ya da pencereler `[{gunler, bas, bit}]` (`bit` 24'ü aşabilir). Boş = kural uygulanmaz (üst departman gibi). Şartnamedeki `acilis_saat` / `kapanis_saat` bunun yerine geçti.
- `employees.gece_calisamaz` — K-40: "gece vardiyası yapamaz" işareti (`GECE_UYGUNLUGU`). Kartta tutulur, tahmin edilmez.
- `employee_contracts.haftalik_gun` — Tam zamanlının haftalık çalışma günü (5 | 6) — saat değil, çalışma düzeni; izin gününü saate çevirmek için (45/6 = 7,5; 45/5 = 9). Yarı zamanlıda boş. (K-58'in açık sorusu, 14 Ekim: sözleşmede tutulur.)
- **`employee_balances`** (tablo) — **Hesaplanmış ara sonuçlar** (şartname §8'de yok — öneri).
- `shift_templates.team_id` — Şablonun ekibi (motor şablonu ekibe bağlar). Boş = ekipsiz (kişinin ilk ekibi).
- `shift_templates.aciklama` — Serbest açıklama.
- `plans.kural_degerleri` — K-68: bu planın kural değerleri (zaman kademesi; tatil / sezon). Örnek `{"HEDEF_ASIMI": {"ust_tolerans": 1}}`. Genellemesi T-81.
- `assignment_breaks.tip` — Mola tipi (motor çıktısında var).
- `plan_locks.team_id` — Kilidin ekibi (motor kilidi ekiple alır).

Ayrıca: `departments.acilis_saat` / `kapanis_saat` yerine `acik` (K-52; çok
pencereli saatleri iki kolon taşıyamıyor); `employee_contracts.haftalik_saat`
**yalnız yarı zamanlıda** dolu (K-58 tam zamanlıdan kaldırdı, K-71 yarı
zamanlıda sözleşme süresi olarak geri getirdi — şartnamedeki kolon duruyor,
anlamı daraldı).

## 6 · Açık sorular

1. **Plan kapsamı:** şartname planı tek departmana bağlıyor; motor üç ekibi
   birlikte çözüyor (çift yetkinlikliler yüzünden ayrı çözülemezler). Veri
   setinde plan **üst departmana** bağlı ve alt departmanları kapsıyor. Bu
   yorum doğru mu (Yılmaz)?
2. **`employee_balances`:** devir ve yıl içi fazla mesai her plan koşusunda
   mı hesaplanacak, ay sonunda mı saklanacak? Tablo önerisi bu yüzden
   "hesaplanmış ara sonuç" (Yılmaz).
3. **Kimlik tabloları** (`users` vb.) veri setinde yok; `*_user_id` kolonları
   boş. Import'un kullanıcı eşleştirmesi ayrıca konuşulmalı (Yılmaz).
4. **Kural değerlerinin plan kademesi** (T-81): şimdilik yalnız
   `ust_tolerans`; genel kural Mustafa'da.
5. **`yasak` kilidi:** şartnamede var, motor girdisi `tip: "yasak"` ile
   alıyor; doğrulayıcı tarafı ayrıca bakılmalı.

## 7 · Motor girdisine dönüşüm

`donustur.py` — backend'in plan koşusu için yapacağı işin referans
uygulaması; kuyruğa konacak iş mesajı bu çıktıdır (şartname §11.2):

- **Kapsam:** planın departmanı + bütün alt departmanları. Çalışan,
  departmanı kapsamdaysa gider; durumu ne olursa olsun (pasif / ayrılmış
  kişiyi `AKTIF_CALISAN` dışlar).
- **Sözleşme:** plan haftasının ilk günü geçerli olan; yoksa en son
  başlayan. Tam zamanlı → `haftalik_saat: 45` (kanun), `gun_sayisi =
  haftalik_gun`; yarı zamanlı → `haftalik_saat` sözleşmeden (K-71).
- **Birincil ekip (K-72):** `employee_teams`'te tek bir en düşük öncelik varsa
  o ekip `birincil_ekip`; eşit öncelik (gezici) ya da tek ekip → alan yok.
- **İzin:** plan haftasına düşen **tüm gün** izinler, gün gün (K-31).
- **Uygunluk:** haftalık satırlar aynen; tarihli satırlar haftaya açılır.
- **Geçmiş:** plandan önceki iki yayınlanmış haftanın seçili versiyonu →
  `gecmis_vardiyalar` (molalarıyla) ve `gecmis_bilinen_gunler` (−14…−1).
- **Kurallar:** aktif `tenant_rules`; tür = geçersiz kılma ya da katalog;
  yasal / kabul edilebilir **katalogdan**; satır bazlı kuralın her
  gerekliliği ayrı kural; planın `kural_degerleri` parametrelere eklenir.
- **Ağırlıklar:** varsayılan profilin ağırlıkları.

Bugünkü ölçüm sahnesiyle (`merdiven.taban_sahne`) farkı yalnız bilerek
değişen şeylerdir (test `test_DONUSTURUCU_eski_sahneden_YALNIZ_bilinen_farklar`):
sözleşmeler (29 kişi K-58 + bütün yarı zamanlılarda süre, K-71),
`birincil_ekip` (çok ekipli, gezici olmayan — K-72), geçmiş (yeni), devir
(geçmişten), 6 kuralın bayrakları (katalogdan, §8), `HEDEF_ASIMI` türü,
`sektor`, departman adları, `agirliklar` (yeni anahtar).

## 8 · Bulgular (veri seti kurulurken çıkanlar)

- **Üreticinin kural bayrakları katalogdan sapmış** (6 kural): `ASGARI_KAPSAMA`; `FAZLA_MESAI_TAVANI`; `ONAYLI_IZIN`; `PART_TIME_LIMIT`; `GECE_YARISI_ASAN`; `HEDEF_ASIMI`.
  Veri setinde katalog geçerli (sistem tablosu, K-18 / K-20). Motorun
  planını değiştirmez; yayın kapısının "kabul edilebilir" ve "yasal"
  cümlelerini değiştirir.
- **Geçmiş + sert hedef aşımı:** geçen haftanın Pazar gecesi vardiyası
  Pazartesi sabahını kapatıyor (K-56); bu talep eğrisiyle (hedef 5,
  sahada 7) `HEDEF_ASIMI` sertken plan **ön kontrolde çözümsüz** — talep
  geçmişi bilmeden girilmiş. Merdiven tabanı (aşım yumuşak) sorunsuz
  çözülüyor; seviye 1 talebi yeni referanstan türeyince tutarlı olur.

## 9 · Yeniden üretme ve test

```powershell
cd C:\Users\PC\Desktop\Tshift\10-veri-seti\v2
py uret.py        # veri/tshift-500.json, veri/tshift-49.json
py belgeler.py    # şema, bu sözlük, Excel
py -m pytest testler -q
```

## 10 · Tablolar (kolon kolon)

Her tabloda (kural kataloğu hariç) ortak kolonlar: `id` (UUID, birincil
anahtar), `created_at`, `updated_at`. Aşağıda **Z** = zorunlu (boş olamaz),
**→** = ilişki (yabancı anahtar), 🆕 = şartnamede yok.

### 8.1 Firma

#### `tenants`

Firmanın kendisi. M-16 ile her müşteri ayrı konteynerde olduğu için **tek satır**; başka tablolar buna anahtar tutmaz.

Kaynak: **firma ayarı (ekrandan)** · Örnekte 1 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `ad` | text | Z | Firma adı. |  |
| `slug` | text | Z | Kısa ad (adres / alt alan adı). |  |
| `sektor_paketi` | text | Z | Kurulum sihirbazının yüklediği hazır kural seti; hiçbir kuralı bağlamaz. Değerler: `cagri_merkezi`, `otel`, `perakende`, `saglik`, `uretim`, `bos`. |  |
| `birim_adi` | text | Z | Arayüzde "departman" yerine kullanılan kelime. Değerler: `Departman`, `Şube`, `Birim`. |  |
| `zaman_dilimi` | text | Z | IANA zaman dilimi. | `kiraci_saat_dilimi` |
| `hafta_baslangic` | int | Z | Haftanın ilk günü (1 = Pazartesi). Motorda gün 0 bu gündür. |  |
| `sektor` | text |  | **Yasal** sektör (K-26): gece 7,5 saat istisnasını açar. Boş = istisna yok. Değerler: `turizm`, `ozel_guvenlik`, `saglik`, `petrol`, `boş`. | `sektor` |
| `durum` | text | Z | Firma hesabının durumu. Değerler: `aktif`, `askida`, `deneme`. |  |
| `deneme_bitis` | date |  | Deneme süresinin bitişi. |  |
| `cok_ekipli_sayim` 🆕 | text | Z | K-50: birden çok ekibe üye çalışan bütün ekiplerine mi (`hepsi`), yalnız vardiyanın ekibine mi (`tek`) sayılır. Değerler: `hepsi`, `tek`. | `cok_ekipli_sayim` |

### 8.2 Organizasyon

#### `departments`

Departmanlar; `ust_department_id` ile hiyerarşi. Plan bir departman için üretilir ve **alt departmanlarını kapsar** (örnekte "Operasyon" → Satış, Back Office, Müşteri Hizmetleri).

Kaynak: **import (LDAP / API / Excel)** · Örnekte 4 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `ad` | text | Z | Görünen ad. |  |
| `kod` | text | Z | Kısa kod; dış sistemle eşleştirme anahtarı. | `departmanlar[].id` |
| `ust_department_id` | uuid → `departments` |  | Üst departman (hiyerarşi). Boş = en üst. |  |
| `calisma_tipi` | text | Z | 7/24 mü, saatli mi (`acik` alanından türer). Değerler: `yedi_yirmidort`, `saatli`. |  |
| `acik` 🆕 | json |  | K-52 çalışma günleri ve saatleri: `"7/24"` ya da pencereler `[{gunler, bas, bit}]` (`bit` 24'ü aşabilir). Boş = kural uygulanmaz (üst departman gibi). Şartnamedeki `acilis_saat` / `kapanis_saat` bunun yerine geçti. | `departmanlar[].acik` |
| `aktif` | bool | Z | Pasif departman planlanmaz. |  |

#### `teams`

Ekipler. Talep (`demand_cells`) ve vardiya şablonları ekibe bağlıdır; motorda "ekip".

Kaynak: **import (LDAP / API / Excel)** · Örnekte 3 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `department_id` | uuid → `departments` | Z | Bağlı olduğu departman. |  |
| `ad` | text | Z | Görünen ad. |  |
| `kod` | text | Z | Kısa kod; motorda ekip kimliği. | `calisanlar[].ekipler[], talep[].ekip, vardiya_sablonlari[].ekip` |
| `aciklama` | text |  | Serbest açıklama. |  |
| `aktif` | bool | Z | Pasif ekip planlanmaz. |  |

#### `operational_roles`

Operasyonel roller (takım lideri vb.). `ROL_KAPSAMASI` kuralı bunları sayar.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 4 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `ad` | text | Z | Görünen ad. |  |
| `kod` | text | Z | Kısa kod; motorda rol kimliği. | `calisanlar[].operasyonel_rol` |
| `aciklama` | text |  | Serbest açıklama. |  |

#### `skills`

Yetkinlikler (dil, ürün bilgisi…). `YETKINLIK_KAPSAMASI` kuralı bunları sayar.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 5 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `ad` | text | Z | Görünen ad. |  |
| `kod` | text | Z | Kısa kod; motorda yetkinlik kimliği. | `calisanlar[].yetkinlikler[]` |
| `aciklama` | text |  | Serbest açıklama. |  |
| `sertifika_gerekli` | bool | Z | Öyleyse çalışanda geçerlilik tarihi tutulur. |  |

### 8.3 Çalışan

#### `employees`

Çalışan kartı. LDAP / API / Excel import'unun ana tablosu; eşleştirme anahtarı `personel_no`.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 500 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `personel_no` | text | Z | Firma sicil no — İK entegrasyonunun eşleştirme anahtarı; benzersiz. Motorda çalışan kimliği olarak gider. | `calisanlar[].id` |
| `ad` | text | Z | Ad (veri setinde **uydurma**). |  |
| `soyad` | text | Z | Soyad (veri setinde **uydurma**). |  |
| `eposta` | text |  | E-posta (veri setinde `.test` alan adı). |  |
| `telefon` | text |  | Telefon (veri setinde uydurma). |  |
| `department_id` | uuid → `departments` | Z | Departman (birincil ekibinin departmanı). |  |
| `birincil_team_id` | uuid → `teams` |  | İdari ana ekip (departmanını belirler); `employee_teams`'te önceliği 1 olan ekiplerden biri. **K-72:** motorun `birincil_ekip`i buradan değil `employee_teams.oncelik`ten türetilir; gezicide (eşit öncelik) bu alan yine doludur, motor ceza uygulamaz. |  |
| `operational_role_id` | uuid → `operational_roles` |  | Operasyonel rol. | `calisanlar[].operasyonel_rol` |
| `ise_giris` | date | Z | İşe giriş tarihi. |  |
| `isten_cikis` | date |  | İşten çıkış tarihi; durum `ayrildi` ise dolu. |  |
| `durum` | text | Z | Pasif ve ayrılmış çalışana atama yapılmaz (`AKTIF_CALISAN`). Değerler: `aktif`, `pasif`, `ayrildi`. | `calisanlar[].durum (aktifse gönderilmez)` |
| `user_id` | uuid |  | Uygulamaya girişi varsa kullanıcı (kimlik tabloları veri setinde yok). |  |
| `dis_sistem_id` | text |  | İK / LDAP sistemindeki kimlik. |  |
| `gece_calisma_onayi` | bool | Z | Gece 7,5 saati aşmaya yazılı onay (§6.3; sektör istisnasıyla birlikte). |  |
| `gece_calisma_onay_tarihi` | date |  | Onayın tarihi. |  |
| `gece_calisma_onay_belge` | text |  | Onay belgesi referansı. |  |
| `gece_calisamaz` 🆕 | bool | Z | K-40: "gece vardiyası yapamaz" işareti (`GECE_UYGUNLUGU`). Kartta tutulur, tahmin edilmez. | `calisanlar[].gece_calisamaz` |

#### `employee_contracts`

Sözleşmeler (dönemsel; bir çalışanın birden çok sözleşmesi olabilir, motor plan haftasında geçerli olanı kullanır). K-58: tam zamanlıya **saat tanımlanmaz** — 45 kanundan gelir. **K-71 (14 Ekim, v2):** yarı zamanlının **sözleşme süresi** `haftalik_saat`ta tutulur (zorunlu; İş K. m. 13: haftalık süre sözleşmede belirlenir, her hafta ödenir) — motor çalışanı bu süreye getirmeye çalışır (`TERCIH_KARSILAMA`, yumuşak); üst sınır 45 (K-39) ayrı. Çağrı üzerine çalışma (m. 14) kapsam dışı.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 500 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `tip` | text | Z | Sözleşme tipi (K-58: yalnız iki). Değerler: `tam_zamanli`, `yari_zamanli`. | `calisanlar[].sozlesme.tip` |
| `haftalik_saat` | numeric |  | **Yarı zamanlıda zorunlu (K-71):** sözleşmedeki haftalık süre (saat; en çok emsalin 2/3'ü = 30, Kısmi Süreli Çalışma Yön. m. 6). Tam zamanlıda **boş** (45 kanundan, K-58). Motor eksik kalan dakikayı cezalar (2.000 puan / saat ≈ 33 / dk); fazlası 45'e kadar serbest (K-39). | `calisanlar[].sozlesme.haftalik_saat (yalnız yarı zamanlı; tam zamanlıda 45 sabit)` |
| `haftalik_gun` 🆕 | int |  | Tam zamanlının haftalık çalışma günü (5 \| 6) — saat değil, çalışma düzeni; izin gününü saate çevirmek için (45/6 = 7,5; 45/5 = 9). Yarı zamanlıda boş. (K-58'in açık sorusu, 14 Ekim: sözleşmede tutulur.) Değerler: `5`, `6`, `boş`. | `calisanlar[].sozlesme.gun_sayisi` |
| `baslangic` | date | Z | Sözleşme başlangıcı. |  |
| `bitis` | date |  | Sözleşme bitişi; boş = süresiz (sezonluk çalışanda dolu). |  |
| `aktif` | bool | Z | Yürürlükte mi. |  |

#### `employee_teams`

Ekip üyelikleri (çoğul). K-50: çalışan üye olduğu **bütün** ekiplerin kapsamasına sayılır.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 510 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `team_id` | uuid → `teams` | Z | Ekip. | `calisanlar[].ekipler[]` |
| `oncelik` | int | Z | 1 = birincil ekip; motorda listedeki sıra. **K-72 (14 Ekim, v2):** tek bir en düşük öncelik varsa o ekip `calisanlar[].birincil_ekip` olur ve `EKIP_SUREKLILIGI` kişiyi orada tutar; öncelikler **eşitse** kişi gezicidir, alan yazılmaz, ceza yok. | `calisanlar[].birincil_ekip (türetilir)` |

#### `employee_skills`

Çalışanın yetkinlikleri.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 451 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `skill_id` | uuid → `skills` | Z | Yetkinlik. | `calisanlar[].yetkinlikler[]` |
| `seviye` | int | Z | 1–5. |  |
| `sertifika_bitis` | date |  | Geçmişse yetkinlik sayılmaz. |  |

#### `employee_availability`

Uygunluk takvimi: uygun olmadığı (sert) ya da tercih ettiği / etmediği (yumuşak) zamanlar.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 338 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `tip` | text | Z | `uygun_degil` sert (`UYGUNLUK_TAKVIMI`); tercihler yumuşak. Değerler: `uygun_degil`, `tercih_ediyor`, `tercih_etmiyor`. | `calisanlar[].uygunluk[].tip` |
| `tekrar` | text | Z | Her hafta mı, belli tarihler mi. Değerler: `haftalik`, `tarihli`. |  |
| `gun` | int |  | `haftalik` ise 0–6 (0 = Pazartesi). | `calisanlar[].uygunluk[].gun` |
| `baslangic_tarih` | date |  | `tarihli` ise. |  |
| `bitis_tarih` | date |  | `tarihli` ise. |  |
| `baslangic_saat` | numeric | Z | Genişletilmiş saat (0–24). | `calisanlar[].uygunluk[].bas` |
| `bitis_saat` | numeric | Z | Genişletilmiş saat (24'ü aşabilir). | `calisanlar[].uygunluk[].bit` |
| `aciklama` | text |  | Örnek: "Üniversite dersi". |  |

#### `leaves`

İzinler. Motora yalnız plan haftasına düşen **tüm gün** izinler gider (K-31); onaylı olanlar bağlar, öteki durumlar bilgi olarak gider.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 59 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `tip` | text | Z | İzin tipi. Değerler: `yillik`, `mazeret`, `rapor`, `ucretsiz`, `dogum`, `diger`. | `calisanlar[].izinler[].tip` |
| `baslangic` | date | Z | İlk izin günü. |  |
| `bitis` | date | Z | Son izin günü (dahil). |  |
| `tum_gun` | bool | Z | Değilse saat aralığı (motora gitmez, K-31). |  |
| `baslangic_saat` | numeric |  | `tum_gun` değilse. |  |
| `bitis_saat` | numeric |  | `tum_gun` değilse. |  |
| `durum` | text | Z | Yalnız onaylı izin motoru bağlar. Değerler: `talep`, `onayli`, `reddedildi`, `iptal`. | `calisanlar[].izinler[].durum` |
| `onaylayan_user_id` | uuid |  | Onaylayan kullanıcı. |  |
| `aciklama` | text |  | Serbest açıklama. |  |

#### `employee_balances` 🆕

**Hesaplanmış ara sonuçlar** (şartname §8'de yok — öneri). Backend bunları plan geçmişinden (yayınlanmış planların atamaları) ve PDKS ham verisinden (K-55) hesaplar; veri setinde hesaplanmış hâli verilir. Dönem = takvim ayı (`ADALET_DENGESI` penceresi).

Kaynak: **hesaplanır (backend)** · Örnekte 500 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `donem` | text | Z | Takvim ayı, `YYYY-AA`. |  |
| `yil_ici_fazla_mesai_saat` | numeric | Z | Yıl başından plan haftasına kadar fazla mesai (K-55: PDKS hamından TShift hesabı). `YILLIK_FAZLA_MESAI_TAVANI` (270) bunu okur. | `calisanlar[].yil_ici_fazla_mesai_saat` |
| `devir_gece` | int | Z | Bu ay plan haftasından önce tutulan gece vardiyası sayısı (`ADALET_DENGESI`). | `calisanlar[].devir_yuk.gece` |
| `devir_hafta_sonu` | int | Z | Bu ay önce çalışılan hafta sonu günü sayısı (K-46 gün tanımı). | `calisanlar[].devir_yuk.hafta_sonu` |
| `devir_cumartesi` | int | Z | Bu ay önce çalışılan cumartesi sayısı. | `calisanlar[].devir_yuk.cumartesi` |
| `devir_saat` | numeric | Z | Saat boyutu — T-13 (yazılmadı); 0. | `calisanlar[].devir_yuk.saat` |
| `hesaplanma_zamani` | timestamptz | Z | Ne zaman hesaplandı. |  |

### 8.4 Vardiya ve kural

#### `shift_templates`

Vardiya şablonları. Saatler **genişletilmiş saattir**: 23 – 32,25 = 23:00 – ertesi gün 08:15.

Kaynak: **firma ayarı (ekrandan)** · Örnekte 17 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `department_id` | uuid → `departments` |  | Boş = tüm departmanlar. |  |
| `team_id` 🆕 | uuid → `teams` |  | Şablonun ekibi (motor şablonu ekibe bağlar). Boş = ekipsiz (kişinin ilk ekibi). | `vardiya_sablonlari[].ekip` |
| `ad` | text | Z | Görünen ad. |  |
| `kod` | text | Z | Kısa kod; motorda şablon kimliği. | `vardiya_sablonlari[].id` |
| `baslangic_saat` | numeric | Z | Başlangıç (0–24). | `vardiya_sablonlari[].bas` |
| `bitis_saat` | numeric | Z | Bitiş; gece yarısını aşan vardiyada 24'ten büyük. | `vardiya_sablonlari[].bit` |
| `mola_dk` | int | Z | Toplam mola süresi. | `vardiya_sablonlari[].mola_dk` |
| `mola_politikasi` | json |  | Mola tipleri, süreleri, adetleri (K-32). Boş = firma politikası. | `vardiya_sablonlari[].mola_politikasi` |
| `gunler` | int[] |  | Kullanılabileceği günler (0 = Pazartesi). Boş = her gün. | `vardiya_sablonlari[].gunler` |
| `gece_mi` | bool | Z | **Yasal** gece postası mı — yönetmelikten hesaplanır (md. 7/2), saklanır. |  |
| `gece_vardiyasi` | bool |  | Firma işareti (K-40 / K-43): `true` yasal olmayan şablonu da gece sayar; `false` yasal geceyi geri alamaz. | `vardiya_sablonlari[].gece_vardiyasi` |
| `aciklama` 🆕 | text |  | Serbest açıklama. |  |
| `renk` | text |  | Takvim rengi. |  |
| `aktif` | bool | Z | Pasif şablon kullanılmaz. |  |

#### `rule_types`

Kural kataloğu (sistem tablosu, firmadan bağımsız) — şartname §6'nın 41 satırı. Birincil anahtar `kod`.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 41 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `kod` | text | Z | Kural kodu (birincil anahtar). | `kurallar[].kod` |
| `ad` | text | Z | Görünen ad. |  |
| `aciklama` | text | Z | Katalogdaki tanım (şartname §6). |  |
| `tur` | text | Z | Varsayılan tür. Değerler: `SERT`, `YUMUSAK`. |  |
| `kategori` | text | Z | Katalog bölümü. Değerler: `uygunluk`, `sure`, `gece`, `kapsama`, `adalet`, `duzenleme`, `fazla_mesai`, `tercih`. |  |
| `yasal` | bool | Z | Kanundan mı geliyor (K-18). Satır bazlı kurallarda `false`; bayrak satırda. | `kurallar[].yasal` |
| `kabul_edilebilir` | bool |  | Yönetici bu ihlali kabul edip yayınlayabilir mi (K-20). Yumuşakta boş. | `kurallar[].kabul_edilebilir` |
| `bayrak_satir_bazli` | bool | Z | Bayraklar her gereklilik satırında mı (§5.3). |  |
| `kapsam_seviyeleri` | text[] | Z | Değerin belirlenebildiği kademeler (S sistem, K kiracı, D departman, Z sözleşme tipi, C çalışan). |  |

#### `tenant_rules`

Firmanın kural ayarları — her kural tipi için **tek satır**. Satır bazlı kurallarda (`ROL_KAPSAMASI`, `YETKINLIK_KAPSAMASI`) her gereklilik `parametreler.gereklilikler[]` içinde; motora her biri ayrı kural olarak gider.

Kaynak: **firma ayarı (ekrandan)** · Örnekte 41 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `rule_type_kod` | text → `rule_types` | Z | Kural tipi. | `kurallar[].kod` |
| `aktif` | bool | Z | Kapalı kural motora gönderilmez. | `kurallar[].aktif` |
| `tur_gecersiz_kilma` | text |  | Firma türü değiştirdiyse; boş = katalog türü. Değerler: `SERT`, `YUMUSAK`, `boş`. | `kurallar[].tur` |
| `agirlik` | int |  | Yumuşaksa özel ağırlık; boş = profil ağırlığı. |  |
| `parametreler` | json | Z | Kural parametreleri. Satır bazlıda `{gereklilikler: [...]}`. | `kurallar[].parametreler` |
| `not` | text |  | Neden değiştirildi. |  |

#### `plan_profiles`

Plan profilleri ve yumuşak kural ağırlıkları (§5.4).

Kaynak: **firma ayarı (ekrandan)** · Örnekte 3 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `kod` | text | Z | Profil. Değerler: `DENGELI`, `KAPSAMA`, `CALISAN`. | `profil` |
| `ad` | text | Z | Görünen ad. |  |
| `aciklama` | text |  | Kullanıcıya açıklama. |  |
| `agirliklar` | json | Z | Kural kodu → ağırlık. | `agirliklar` |
| `varsayilan_mi` | bool | Z | Varsayılan profil (tek). |  |

### 8.5 Talep

#### `demand_profiles`

Talep profilleri ("Normal hafta", "Yaz sezonu"…). Plan bir profili seçer.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 1 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `department_id` | uuid → `departments` | Z | Departman (üst departman olabilir; hücreler ekibe bağlı). |  |
| `ad` | text | Z | Görünen ad. |  |
| `kaynak` | text | Z | Talep nereden geldi. Değerler: `dogrudan`, `hacim`, `gecmis`. |  |
| `kapanma_payi` | numeric |  | Erlang C için (kaynak = hacim). |  |
| `aktif` | bool | Z | Kullanımda mı. |  |

#### `demand_cells`

Saatlik talep: ekip × gün × saat için asgari (sert) ve hedef (yumuşak; üstü K-67 ile sert) kişi.

Kaynak: **import (LDAP / API / Excel)** · Örnekte 415 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `demand_profile_id` | uuid → `demand_profiles` | Z | Talep profili. |  |
| `team_id` | uuid → `teams` | Z | Ekip. | `talep[].ekip` |
| `gun` | int | Z | 0–6 (0 = Pazartesi). | `talep[].gun` |
| `saat` | int | Z | 0–23. | `talep[].saat` |
| `asgari_kisi` | int | Z | Altına inilemez (`ASGARI_KAPSAMA`). | `talep[].asgari` |
| `hedef_kisi` | int | Z | İdeal sayı (`HEDEF_KAPSAMA`; üstü `HEDEF_ASIMI`). | `talep[].hedef` |
| `elle_duzeltildi` | bool | Z | Erlang'dan üretilen sayı elle değiştirildi mi. |  |

### 8.6 Plan

#### `plans`

Haftalık plan (departman + hafta). Örnekte iki yayınlanmış geçmiş hafta ve üretilecek hafta.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 3 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `department_id` | uuid → `departments` | Z | Planın departmanı; alt departmanları da kapsar. |  |
| `hafta_baslangic` | date | Z | Pazartesi. | `hafta_baslangic` |
| `durum` | text | Z | Plan durumu. Değerler: `taslak`, `adaylar_hazir`, `secildi`, `onayda`, `onayli`, `yayinda`, `arsiv`. |  |
| `demand_profile_id` | uuid → `demand_profiles` |  | Talep profili. |  |
| `secili_version_id` | uuid → `plan_versions` |  | Seçilen versiyon. |  |
| `olusturan_user_id` | uuid |  | Kimlik tabloları veri setinde yok; boş. |  |
| `onaylayan_user_id` | uuid |  | Kimlik tabloları veri setinde yok; boş. |  |
| `onay_zamani` | timestamptz |  | Onay zamanı. |  |
| `yayin_zamani` | timestamptz |  | Yayın zamanı. |  |
| `kural_degerleri` 🆕 | json |  | K-68: bu planın kural değerleri (zaman kademesi; tatil / sezon). Örnek `{"HEDEF_ASIMI": {"ust_tolerans": 1}}`. Genellemesi T-81. | `kurallar[].parametreler (birleştirilir)` |

#### `plan_versions`

Bir planın aday versiyonları; seçili olan yayınlanır.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 2 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `plan_id` | uuid → `plans` | Z | Plan. |  |
| `plan_run_id` | uuid |  | Üreten motor koşusu (veri setinde yok). |  |
| `profil_kod` | text | Z | Profil. Değerler: `DENGELI`, `KAPSAMA`, `CALISAN`. |  |
| `metrikler` | json | Z | Özet metrikler. |  |
| `secili_mi` | bool | Z | Seçili versiyon. |  |
| `ai_aciklama` | text |  | Üretilmiş özet. |  |

#### `assignments`

Atamalar. Yayınlanmış geçen haftanın atamaları motora `gecmis_vardiyalar` (gün −7…−1) olarak gider.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 4804 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `plan_version_id` | uuid → `plan_versions` | Z | Versiyon. |  |
| `employee_id` | uuid → `employees` | Z | Çalışan. |  |
| `team_id` | uuid → `teams` | Z | Vardiyanın ekibi. |  |
| `shift_template_id` | uuid → `shift_templates` |  | Şablon; serbest saatte boş. |  |
| `gun` | int | Z | 0–6. | `calisanlar[].gecmis_vardiyalar[].gun (geçen hafta: gün − 7)` |
| `baslangic_saat` | numeric | Z | Genişletilmiş saat. | `calisanlar[].gecmis_vardiyalar[].bas` |
| `bitis_saat` | numeric | Z | Genişletilmiş saat. | `calisanlar[].gecmis_vardiyalar[].bit` |
| `kilitli` | bool | Z | Elle yapılan atamalar kilitli. |  |
| `kaynak` | text | Z | Atamanın kaynağı. Değerler: `motor`, `manuel`, `sabit`, `devir`. |  |
| `olusturan_user_id` | uuid |  | Manuelse. |  |

#### `assignment_breaks`

Atamanın molaları.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 17782 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `assignment_id` | uuid → `assignments` | Z | Atama. |  |
| `tip` 🆕 | text | Z | Mola tipi (motor çıktısında var). Değerler: `yemek`, `dinlenme`. |  |
| `baslangic_saat` | numeric | Z | Genişletilmiş saat. |  |
| `bitis_saat` | numeric | Z | Genişletilmiş saat. |  |
| `dakika` | int | Z | Süre. |  |

#### `plan_locks`

Kilitler: yöneticinin "bunu buraya koy" (`sabit`) ya da "koyma" (`yasak`) dediği atamalar.

Kaynak: **sistem (TShift'in ürettiği)** · Örnekte 6 satır.

| kolon | tip | Z | açıklama | motor girdisi |
|---|---|---|---|---|
| `plan_id` | uuid → `plans` | Z | Plan. |  |
| `employee_id` | uuid → `employees` | Z | Çalışan. | `kilitler[].calisan` |
| `team_id` 🆕 | uuid → `teams` |  | Kilidin ekibi (motor kilidi ekiple alır). | `kilitler[].ekip` |
| `tip` | text | Z | `sabit` = buraya koy; `yasak` = koyma. Değerler: `sabit`, `yasak`. |  |
| `gun` | int | Z | 0–6. | `kilitler[].gun` |
| `baslangic_saat` | numeric |  | Genişletilmiş saat. | `kilitler[].bas` |
| `bitis_saat` | numeric |  | Genişletilmiş saat. | `kilitler[].bit` |
| `ekleyen_user_id` | uuid |  | Kimlik tabloları veri setinde yok; boş. |  |
| `not` | text |  | Serbest not. |  |
