# TShift — mimari inceleme paketi

**Tarih:** 11 Eylül 2026 · **Sürüm:** `v0.5-arayuz` · **Depo:** github.com/mustafatbayri/tshift

Yılmaz, iki hafta önce konuştuğumuz şeyin sonucu bu. Uzun okuma değil; asıl
istediğim şey en sondaki sorulara cevabın.

---

## İçindekiler

1. [Bir sayfada durum](#1-bir-sayfada-durum)
2. [Ne denedik, neden](#2-ne-denedik-neden)
3. [Mimari](#3-mimari)
4. [Tartışmaya açık kararlar](#4-tartışmaya-açık-kararlar)
5. [Çıkan hatalar ve şimdi onları tutan şey](#5-çıkan-hatalar-ve-şimdi-onları-tutan-şey)
6. [Bilinen boşluklar](#6-bilinen-boşluklar)
7. [Sana sorularım](#7-sana-sorularım)
8. [10 dakikada kendin çalıştır](#8-10-dakikada-kendin-çalıştır)

---

## 1. Bir sayfada durum

Çok kiracılı bir vardiya planlama SaaS'ının **dikey dilimi** ayakta:
veritabanından ekrana kadar her katman bağlı ve çalışıyor.

| Katman | Durum |
|---|---|
| PostgreSQL 17 + satır seviyesi güvenlik | 15 tablo, 5 migration |
| .NET 10 · EF Core | Alan modeli, sorgu filtreleri, bağlantı kesici |
| Kimlik | Argon2id, JWT 15 dk, döner yenileme jetonu 30 gün |
| Yetki | 5 rol, 19 izin, departman/ekip kapsamı, süreli devir |
| Denetim | Otomatik, aynı işlemde, **sadece eklenir** |
| API | ~12 uç, izin politikalarıyla korunuyor |
| Arayüz | Next.js 16 · giriş, çalışan listesi, yeni kayıt |
| Test | **38 test**, hepsi gerçek PostgreSQL'e bağlanıyor |

Etiketli beş sürüm: `v0.1-kiracilik` · `v0.2-kimlik` · `v0.3-yetki` ·
`v0.4-denetim` · `v0.5-arayuz`

**Henüz yok:** planlama motoru (Python + OR-Tools, ayrı serviste kalacak),
plan editörü, gerçek müşteri verisi.

---

## 2. Ne denedik, neden

Senin itirazın şuydu, olabildiğince aslına sadık aktarıyorum:

> *"Zor olan yapay zekânın bunu yapması değil. Bağlamdan hiç kopmadan prompt
> yazabilmek... blokların birbiri ile ilişkisini o kuramaz. Bağlamın tamamı
> onda olmadığı için. İlişkileri hiçbir zaman tam bilmeyecek."*

Bunu tartışmak yerine **ölçülebilir hale getirdik**. Soru şu şekilde kuruldu:

> Uçtan uca yapay zekâ ile yazılan katmanlar birbiriyle tutarlı kalıyor mu?
> Kalmadığında bu **sessiz mi** kalıyor, yoksa **yakalanıyor** mu?

İkinci yarısı asıl soru. "Hata yapılır mı" sorusunun cevabı zaten evet —
insan da yapar. Fark, hatanın fark edilip edilmediğinde.

Bu yüzden dikey bir dilim seçtik: tek bir işlevi (çalışan yönetimi) tüm
katmanlardan geçirmek. Yatay ilerleseydik (önce tüm veritabanı, sonra tüm
API) katmanlar arası kopmalar aylarca görünmezdi.

**Sonuç, sayılarla:** dört ciddi hata çıktı. Dördü de katmanlar arası
ilişkiyle ilgiliydi — tam senin tarif ettiğin sınıf. Dördü de otomatik bir
kontrol tarafından, Mustafa fark etmeden önce yakalandı. Ayrıntısı §5'te.

---

## 3. Mimari

### 3.1 Çok kiracılık — iki katman

Tek veritabanı, her tabloda `tenant_id`, ve **iki bağımsız savunma**:

**Uygulama katmanı.** EF Core küresel sorgu filtresi. `IKiraciVarligi`
arayüzünü uygulayan her varlık otomatik filtreleniyor — filtre elle
yazılmıyor, yansımayla model kurulurken ekleniyor. Yeni tablo eklendiğinde
arayüzü uygulamak yeterli.

**Veritabanı katmanı.** PostgreSQL Row Level Security, `FORCE` ile.
`app.tenant_id` oturum değişkeni her bağlantı açılışında bir
`DbConnectionInterceptor` tarafından yazılıyor. Politika:
`USING (tenant_id = app_tenant_id()) WITH CHECK (aynısı)`.

İkincisi asıl garanti. Uygulama katmanı hata yapsa, hatta biri ham SQL yazsa
bile veritabanı reddediyor. Testler bunu **kasten EF'i devre dışı bırakarak**
sınıyor.

**Kritik ayrıntı:** iki veritabanı rolü var. `tshift` migration çalıştırır
(süper kullanıcı), `tshift_app` uygulamayı taşır (`NOSUPERUSER`,
`NOBYPASSRLS`). PostgreSQL'de süper kullanıcı RLS'i tamamen aşar — bu bir
gün canımızı yaktı, §5'te anlatıyorum.

### 3.2 Kimlik

Hazır kimlik sunucusu (Keycloak, Auth0) kullanmıyoruz; kimlik doğrulama
API'nin içinde bir modül. Gerekçe ve kabul edilen bedeller spec §7.4'te.

- Argon2id, 64 MB / 3 yineleme / 4 paralellik
- Erişim jetonu: JWT, 15 dakika, `kiraci` + izin kodlarını taşıyor
- Yenileme jetonu: 30 gün, **döner** — her kullanımda yenisi veriliyor,
  yalnız SHA-256 özeti saklanıyor
- Kullanılmış bir yenileme jetonu tekrar gelirse: hırsızlık kabul edilip
  o kullanıcının **tüm oturumları** düşürülüyor
- Kaba kuvvet: e-posta veya IP başına 5 başarısız denemede 15 dakika kilit
- Kullanıcı bulunamasa bile Argon2 çalıştırılıyor (zamanlama saldırısına karşı)

### 3.3 Yetki

İzin *"neyi yapabilir"*, kapsam *"nerede yapabilir"* sorusunu cevaplıyor;
ikisi ayrı kavram olarak modellenmiş.

- 5 sistem rolü her kiracıya ayrı ayrı kuruluyor (kiracı kendi rolünü
  tanımlayabilsin diye)
- İzin kataloğu geneldir, RLS dışındadır — müşteri verisi değil, sistem sözlüğü
- Uçlar `.RequireAuthorization("plan.uret")` gibi izin politikalarıyla korunuyor
- Kapsam sorgulara `IQueryable` üzerinden uygulanıyor
- Süreli yetki devri tarihe bağlı; kendiliğinden bitiyor

### 3.4 Denetim kaydı

- **Otomatik:** uçlarda çağrılmıyor, EF'in `SaveChanges` akışına bağlı
- **Aynı işlemde:** değişiklikle denetim satırı tek `SaveChanges`'te gidiyor
  (kimlikler istemci tarafında üretildiği için mümkün — UUIDv7)
- **Sadece eklenir:** `tshift_app` rolünün `audit_log` üzerinde `UPDATE` ve
  `DELETE` yetkisi **yok**
- Parola ve jeton özetleri kayda girmiyor: alanın *değiştiği* kaydediliyor,
  *değeri* kaydedilmiyor

### 3.5 Arayüz

- Jetonlar `httpOnly` çerezde; tarayıcı JavaScript'ine hiç girmiyor
- API çağrıları Next.js sunucusundan gidiyor → CORS ayarı gerekmiyor
- `proxy.ts` içindeki kontrol bir güvenlik sınırı **değil**, yalnız çerezin
  varlığına bakıyor. Asıl kontrol API'de.

---

## 4. Tartışmaya açık kararlar

Bunları savunmaya değil, sınamaya açıyorum.

| # | Karar | Alternatifi | Neden böyle |
|---|---|---|---|
| 1 | Tek DB + RLS | Kiracı başına şema/veritabanı | Operasyon yükü; 50 kiracıya kadar yeterli görünüyor |
| 2 | Kendi kimlik katmanımız | Keycloak / Auth0 | Tek sistem, tek veritabanı; SSO faz 2'ye bırakıldı |
| 3 | İzin kodları jetonda | Her istekte veritabanından | Hız; bedeli 15 dakikalık gecikme |
| 4 | Kurallar veride, kodda değil | Kod içinde kural sınıfları | Yanlış kural kod değişikliği gerektirmesin |
| 5 | Motor ayrı servis (Python) | .NET içinde | OR-Tools'un resmî bağlayıcısı Python |
| 6 | Testler gerçek veritabanına bağlanıyor | Taklit (mock) | RLS taklitle sınanamaz |
| 7 | Türkçe alan adları, İngilizce kolon adları | Tek dil | Kod ürün diliyle, şema sektör standardıyla konuşsun |

**Spec'ten bilinçli bir sapma var** ve senin görüşünü özellikle istiyorum:

Spec §3.2 "kapsamı olmayan kullanıcı tüm kiracıyı görür" diyor. Uygulama
tersini yapıyor: kapsam seviyesi `Kapsam` olup hiç kapsam satırı olmayan
kullanıcı **hiçbir şey** görmüyor. Gerekçe: kapsamı atanmayı unutulan bir
departman müdürü, spec'teki davranışla sessizce tüm firmayı görürdü —
yapılandırma eksikliğinin yetki genişlemesine dönüşmesi. Eksik yapılandırma
artık "göremiyorum" şikâyeti üretiyor, sızıntı değil.

---

## 5. Çıkan hatalar ve şimdi onları tutan şey

Bu bölüm paketin en önemli kısmı. Hepsi senin tarif ettiğin sınıftan:
bloklar tek tek doğru, aralarındaki ilişki yanlış.

### Hata 1 — EF sürüm çakışması

Infrastructure projesi EF 10.0.12'ye karşı derlendi (Design paketi öyle
çekmişti), Tests projesi 10.0.4 görüyordu. **Yakalayan:** derleyici, CS1705.
**Şimdi tutan:** sabitlenmiş paket sürümleri.

### Hata 2 — Süper kullanıcı RLS'i aşıyordu ⚠

En ciddisi. RLS doğru yazılmış, açılmış, `pg_class` üzerinden `t/t` diye
doğrulanmıştı. Ama uygulama Docker imajının süper kullanıcısıyla bağlanıyordu
ve **PostgreSQL'de süper kullanıcı RLS'i tamamen aşar** — `FORCE` bile
durdurmaz. Güvenlik kâğıt üstünde vardı, çalışmada yoktu.

Dikkat çekici olan: "RLS açık mı" diye kontrol etmiştik ve cevap evetti.
**Yanlış soruydu.** Doğru soru "bağlanan rol RLS'e tabi mi" idi ve onu ancak
davranışı ölçen bir test sorabildi.

**Yakalayan:** çok kiracılık testleri. **Şimdi tutan:** iki ayrı rol
(`tshift` / `tshift_app`) + bir bekçi test: *"Baglanan rol super kullanici
degil"*. Biri bağlantı dizesini değiştirirse test paketi anında kırmızı yanar.

### Hata 3 — JWT `sub` talebi yeniden adlandırılıyordu

21 test yeşilken korumalı bütün uçlar 401 dönüyordu. JwtBearer, gelen jetonun
`sub` talebini eski Microsoft/WS-Federation şemasına çeviriyor; kod `sub`
diye aradığı için kullanıcı kimliği `null` geliyor ve uç "yetkisiz" diyordu.
Yetki mantığı kusursuzdu; kırılan yer iki katmanın buluştuğu sınırdı.

**Testler bunu yakalamadı** — hepsi servisleri doğrudan çağırıyordu, HTTP
katmanından geçmiyordu. Yakalayan şey elle çalıştırdığımız uçtan uca betik
oldu.

**Şimdi tutan:** `HttpSinirTestleri` — uygulamayı bellek içinde ayağa
kaldırıp gerçek istek atan bir test sınıfı. Ders: birim testi katmanın
**içini**, uçtan uca test katmanların **arasını** doğrular.

### Hata 4 — Kapsam kuralının iki kopyası (önlendi)

Çalışan oluşturma ucu yazılırken, listeyi filtreleyen kuralın ikinci bir
kopyası çıkacaktı. İki kopya zamanla ayrışır ve bir gün "listede göremediğim
ama oluşturabildiğim kayıt" ortaya çıkardı.

**Şimdi tutan:** tek bir `Expression<Func<Calisan,bool>>`; biri `IQueryable`'a
uygulanıyor, diğeri derlenip tek kayda. Ayrışmaları yapısal olarak imkânsız.

### Sistemleştirilmiş hali

Her hata için kural şu oldu: **düzeltmek yetmez; o hatanın bir daha sessizce
geri gelmesini engelleyen bir kontrol eklenir.**

Bunun genelleştirilmiş hali `MimariTestleri`: özellik değil **yasa** sınayan
altı test.

- Kiracıya ait her tabloda RLS açık ve `FORCE`'lu mu
- RLS dışı tablolar yalnız bilinen üç istisna mı
- Korumasız uç var mı (açık liste dışında)
- Kültüre bağımlı `ToLower()` kullanılmış mı (Türkçe `I` tuzağı)
- Ayar dosyalarında sır var mı
- Denetim kaydı hâlâ sadece-eklenir mi

Bunlar bugün bir şey yakalamak için değil, altı ay sonra unutulacak bir
kuralı hatırlatmak için var.

---

## 6. Bilinen boşluklar

Dürüst liste. Gizlemeye çalıştığım bir şey yok.

| Konu | Durum | Önem |
|---|---|---|
| **Bağlantı havuzu ve `SET app.tenant_id`** | Düşünülmedi | ⚠ Yüksek |
| Eşzamanlılık (satır sürümü, idempotency) | Yazılmadı | Orta |
| Denetim kaydı hacim yönetimi (bölümleme, saklama) | Yazılmadı | Orta |
| Motor sözleşmesi (zaman aşımı, kuyruk, geri basınç) | Tasarlandı, yazılmadı | Yüksek |
| SSO / OIDC istemcisi | Faz 2 | Düşük |
| Performans: gerçek hacimle sınanmadı | Yapılmadı | Orta |
| Sürekli entegrasyon (CI) | Yok | Orta |
| KVKK: saklama, silme talebi, anonimleştirme | Yapılmadı | Yüksek (pilot öncesi) |

**Birinci maddeyi özellikle işaretliyorum**, çünkü kendi kendime yakaladığım
ama henüz çözmediğim bir risk: kiracı bağlamı `set_config('app.tenant_id',
..., false)` ile **oturum düzeyinde** yazılıyor. Önümüze bir bağlantı havuzu
(PgBouncer gibi) *transaction* kipinde girerse, oturum değişkenleri
isteklerin arasında karışabilir — ve bu, çok kiracılıkta akla gelebilecek en
kötü hata sınıfıdır: **sessiz ve çapraz.**

Muhtemel çözümler: havuzu *session* kipinde çalıştırmak, ya da `set_config`'i
`true` (işlem düzeyinde) yapıp her sorguyu açık bir işleme almak. Hangisini
seçeceğimizi bilmiyorum; senin görüşün burada değerli.

---

## 7. Sana sorularım

Genel yorum yerine bunlara cevap versen benim için çok daha kıymetli.

**Temel hakkında**

1. Bu temel üzerine bir yıl inşa edilir mi? Yoksa şimdi dönmemiz gereken
   bir şey mi görüyorsun?
2. Tek veritabanı + RLS kararı ne zaman duvara toslar? 50 kiracı × 5.000
   çalışan senaryosunda ne olur?
3. Bağlantı havuzu / `app.tenant_id` riskini nasıl çözerdin? Oturum kipi mi,
   işlem düzeyi mi, başka bir şey mi?

**Kimlik ve yetki hakkında**

4. Kendi kimlik katmanımızı yazmak hata mı? Kurumsal müşteri kapıya
   dayandığında bunun bedelini nasıl öderiz?
5. İzin kodlarını jetona koymanın 15 dakikalık gecikmesi kabul edilebilir mi,
   yoksa her istekte veritabanına gitmek mi doğru?
6. Spec'ten yaptığım sapma (kapsamsız kullanıcı hiçbir şey görmez) doğru mu?

**Süreç hakkında**

7. Yakaladığımız dört hatayı görünce ilk itirazın hakkında ne düşünüyorsun?
   Değişen bir şey var mı, yoksa "bunlar kolay olanlardı" mı diyorsun?
8. **En çok merak ettiğim:** senin gözünle, bu yaklaşımın sessizce
   kaybedeceği yer neresi? Hangi hata sınıfı buradaki kontrollerin hiçbirine
   takılmaz?
9. İlk üç ayda sen olsan neyi farklı yapardın?

Sekizinci soru en önemlisi. Yakaladığımız hataları biliyorum; bilmediğim,
**hangi hataların hiç yakalanmadığı.**

---

## 8. 10 dakikada kendin çalıştır

### Tek komut (önerilen) — yalnız Docker gerekiyor

.NET SDK, Node, hiçbiri gerekmiyor.

```bash
git clone https://github.com/mustafatbayri/tshift.git
cd tshift/04-kod
docker compose --profile tam up --build
```

İlk derleme birkaç dakika (imajlar iniyor). Sonra:

**http://localhost:3000**

| Firma | `anadolu-cm` |
|---|---|
| Parola (hepsi) | `TShift2026!Deneme` |
| Kullanıcılar | `mudur@` · `sef@` · `calisan@` · `izleyici@` (hepsi `@anadolu-cm.test`) |

Dördüyle sırayla gir. **Aynı ekran, dört farklı davranış:** müdür üç çalışanı ve
"Yeni çalışan" butonunu görür; şef yalnız kendi ekibindeki ikisini ve buton yok;
çalışan yalnız kendini; izleyici üçünü ama hiçbir eylem düğmesi olmadan.
Sayfanın altındaki "izinler" bölümü her rol için farklı doluyor.

İkinci firma `marmara-perakende` — aynı kullanıcı adları, tamamen ayrı veri.

Kapatmak: `Ctrl+C`, sonra `docker compose --profile tam down -v`
(`-v` veritabanını da siler, makinede iz kalmaz).

### Testleri koşmak

```bash
cd tshift/04-kod
docker compose up -d                 # yalniz veritabani
cd backend && dotnet test            # 38 test — .NET 10 SDK gerekiyor
```

Testler gerçek PostgreSQL'e bağlanır, taklit kullanmaz. RLS taklitle
sınanamaz — sınandığı iddia edilen şey veritabanının davranışıdır.

### Yalıtımı komut satırından görmek

API çalışırken, PowerShell'de:

```powershell
.\YALITIM-KANITI.ps1 -Api http://localhost:5146
```

On adım: iki firmadan giriş, dört rolün karşılaştırması, jetonsuz istek,
**sahte `X-Tenant-Id` başlığı denemesi**, yanlış parola, döner jeton,
çalınmış jeton senaryosu.

**Bakmaya değer dosyalar** (kod okumak istersen, öncelik sırasıyla):

| Dosya | Neden |
|---|---|
| `backend/tests/TShift.Tests/MimariTestleri.cs` | Sistemin kendi kendine koyduğu yasalar |
| `backend/src/TShift.Infrastructure/Persistence/TShiftDbContext.cs` | Sorgu filtresi + denetim kancası |
| `backend/src/TShift.Infrastructure/Yetki/KapsamFiltresi.cs` | Tek ifadeden iki kullanım |
| `db/rls/02-uygulama-rolu.sql` | Süper kullanıcı hatasının çözümü |
| `db/rls/05-denetim-kaydi.sql` | Sadece-eklenir kısıtı |
| `RISKLER-VE-ONLEMLER.md` | Hata sınıfları ve savunma hatları |
| `DEGISIM-GUNLUGU.md` | Her kararın gerekçesi, tarih sırasıyla |

Sondaki iki doküman özellikle önemli: bu projede kural, **her sıra dışı
kararın yanındaki yorumda gerekçesiyle durması.** Altı ay sonra biri
"burayı neden böyle yapmışlar" diye sorduğunda cevabın kodda olması lazım —
yoksa dokunmaya korkar, korktuğu kodu kuşatır, sonunda yeniden yazmayı
teklif eder.
