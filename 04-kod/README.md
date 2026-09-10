# Kod

TShift'in gerçek yazılımı. Ayrıntılı tanım: `../02-spec/v1.1-master-spec.md`

## Kararlaştırılan yığın

| Katman | Seçim |
|---|---|
| Veritabanı | PostgreSQL 17 — tek veritabanı + `tenant_id` + satır seviyesi güvenlik |
| Backend | .NET 10 |
| Kimlik | **Kendi kimlik katmanımız** (Argon2id, döner yenileme jetonu). SSO faz 2 |
| Planlama motoru | Python + OR-Tools CP-SAT, ayrı servis |
| Kuyruk | RabbitMQ |
| Frontend | Next.js + TypeScript · Tailwind · shadcn/ui · TanStack Table |
| Yapay zekâ katmanı | Claude API (yalnız açıklama ve gerekçe üretimi) |
| Barındırma | Yerli sağlayıcı — demo ve gölge pilot için satın alınacak |

## Sıfırdan yazılacak tek karmaşık bileşen

Plan editörü takvimi (spec §9.6). Geri kalan 24 ekran bileşen kütüphanesinden
kurulur. Frontend desteği buraya harcanacak.

## Klasörler

| Klasör | İçinde |
|---|---|
| `db/init/` | Container ilk açılışta çalışan betikler (eklentiler) |
| `db/rls/` | Satır seviyesi güvenlik ve uygulama rolü |
| `backend/` | .NET çözümü — Domain · Infrastructure · Api · Tests |
| `frontend/` | Next.js arayüz — henüz kurulmadı |
| `motor/` | Python planlama servisi — henüz kurulmadı |

## Veritabanını çalıştırma

PowerShell'i **bu klasörde** aç.

```powershell
docker compose up -d        # Başlat
docker compose ps           # Durum
docker compose logs db      # Kayıtlara bak (hata ararken)
docker compose down         # Durdur — veri kalır
docker compose down -v      # SIFIRLA — veritabanını tamamen siler
```

`down -v` sonrası kurulum sırası: `dotnet ef database update` → `01-rls.sql` →
`02-uygulama-rolu.sql` → `03-kimlik-tablolari.sql` → `04-yetki-tablolari.sql`.

## İki veritabanı rolü — dikkat

| Rol | Ne yapar | RLS'e tabi mi |
|---|---|---|
| `tshift` | Tablo sahibi. Migration çalıştırır, şema değiştirir. | **Hayır** — süper kullanıcı |
| `tshift_app` | Uygulamanın ve testlerin bağlandığı rol. | **Evet** |

Bu ayrım şart, süs değil. PostgreSQL'de **süper kullanıcı satır seviyesi
güvenliği tamamen aşar**; `ENABLE` de `FORCE` de onu durdurmaz. Uygulamayı
`tshift` ile bağlarsan RLS yazılmış olur ama hiç devreye girmez — güvenlik
yalnızca kâğıt üstünde kalır. (Bu hata bir kez yapıldı, 10 Eylül'de testler
yakaladı. Bkz. `../DEGISIM-GUNLUGU.md`.)

Bunu koruyan bir bekçi test var: `0 - Baglanan rol super kullanici degil`.
Biri bağlantı dizesini `tshift`e çevirirse test paketi anında kırmızı yanar.

## Bağlantı bilgileri (yerel geliştirme)

| Alan | Değer |
|---|---|
| Sunucu | `localhost` |
| Port | **`5433`** |
| Veritabanı | `tshift` |
| Migration kullanıcısı | `tshift` — parola `.env` içindeki `DB_PASSWORD` |
| Uygulama kullanıcısı | `tshift_app` — parola `.env` içindeki `APP_DB_PASSWORD` |

Port 5433 seçildi (5432 değil) — bilgisayarda önceden kurulmuş bir PostgreSQL
varsa çakışmasın diye.

## API'yi çalıştırma

```powershell
cd backend\src\TShift.Api
dotnet run
```

Açılışta yazılan `Now listening on: http://localhost:XXXX` satırındaki portu al.

| Uç | Ne yapar | Jeton |
|---|---|---|
| `GET /health` | Ayakta mı | — |
| `GET /health/db` | Veritabanı bağlantısı ve kiracı sayısı | — |
| `POST /api/v1/auth/login` | Firma + e-posta + parola → jeton çifti | — |
| `POST /api/v1/auth/refresh` | Yenileme jetonu → yeni çift | — |
| `POST /api/v1/auth/logout` | Bu oturumu kapatır | — |
| `GET /api/v1/me` | Oturum sahibinin profili | gerekli |
| `GET /api/v1/employees` | Çalışanlar — kapsama göre filtreli | `calisan.gor` |
| `POST /dev/seed` | İki örnek firma + kullanıcı + 5 çalışan | — |
| `GET /dev/tenants` | Kiracı listesi | — |

`/dev/*` uçları geçicidir, sürüm öncesi silinecek.

### Giriş isteği neden firma adı istiyor

```json
{ "firma": "anadolu-cm", "eposta": "mudur@anadolu-cm.test", "parola": "..." }
```

`users` benzersizliği `(tenant_id, eposta)` — yani aynı e-posta iki farklı
firmada kullanıcı olabilir (spec §8.1). Bu yüzden e-posta tek başına kimlik
değildir. Canlıda firma **alt alan adından** gelecek
(`anadolu-cm.tshift.com/giris`) ve kullanıcı hiç yazmayacak; şimdilik istek
gövdesinde duruyor.

### Kimlik kuralları (spec §7.4)

| Konu | Değer |
|---|---|
| Parola özeti | Argon2id · 64 MB · 3 yineleme · 4 paralellik |
| Erişim jetonu | JWT, **15 dakika**, `kiraci` talebini taşır |
| Yenileme jetonu | 30 gün, **döner** — her kullanımda yenisi verilir |
| Jeton yeniden kullanımı | Kullanılmış jeton tekrar gelirse **tüm oturumlar** iptal |
| Kaba kuvvet | Aynı e-posta veya IP için 5 başarısız denemede 15 dakika kilit |
| İmza anahtarı | Ortam değişkeni `JWT_SECRET` — koda yazılmaz |

### Roller ve kapsam (spec §3.2)

İzin "neyi yapabilir", kapsam "nerede yapabilir" sorusunu cevaplar. İkisi ayrı.

| Rol | Kapsam | İzin sayısı |
|---|---|---|
| `kiraci_yonetici` | Tüm kiracı | 18 |
| `departman_muduru` | Kendi departman/ekipleri | 15 |
| `sef` | Kendi ekipleri | 8 |
| `calisan` | Yalnız kendi kaydı | 4 |
| `izleyici` | Tüm kiracı, salt okunur | 2 |

Sistem rolleri **her kiracıya ayrı ayrı kurulur** (`KiraciKurulumServisi`).
İzin kataloğu (`permissions`) ise geneldir ve RLS dışındadır — içinde müşteri
verisi yok, yalnız sistemin tanıdığı işlem kodları var.

**Spec'ten bilinçli sapma:** spec §3.2 "kapsamı olmayan kullanıcı tüm kiracıyı
görür" diyor. Uygulama tersini yapar: kapsam seviyesi `Kapsam` olup hiç kapsam
satırı olmayan kullanıcı **hiçbir şey görmez**. Sebep, kapsamı atanmayı
unutulan bir müdürün sessizce tüm firmayı görmesini engellemek. Y8 testi
bunu sabitliyor.

**İzinler jetonda taşınır.** Geri alınan bir yetki, kullanıcının elindeki jeton
süresi dolana kadar (en fazla 15 dakika) etkili kalır. Acil iptalde o
kullanıcının yenileme jetonları da düşürülmeli. Kapsam jetona konmaz, her
istekte veritabanından okunur — kapsam değişikliği anında etkilidir.

## Testler

```powershell
cd backend
dotnet test
```

Veritabanı ayakta olmalı — testler gerçek PostgreSQL'e bağlanır, taklit
kullanmaz. Yalıtımın gerçekten çalıştığını ancak gerçek veritabanı gösterebilir.

| Sınıf | Ne sınar |
|---|---|
| `CokKiracilikTestleri` | Başka firmanın satırı hiç gelmiyor mu (RLS) |
| `KimlikTestleri` | Parola, jeton, kilit, jeton hırsızlığı |
| `YetkiTestleri` | İzin ve kapsam mantığı |
| `HttpSinirTestleri` | Uygulamayı ayağa kaldırıp **gerçek istek** atar |

Sonuncusu ayrı duruyor çünkü ayrı bir şey sınıyor: diğerleri servisleri
doğrudan çağırıp katmanın **içini** doğrular; bu, katmanların **arasını**.
10 Eylül'de 21 test yeşilken bütün korumalı uçlar 401 dönüyordu — hata
mantıkta değil, JWT talep adlarındaydı ve hiçbir birim testi oraya bakmıyordu.

## Yalıtımı gözle görme

API ayrı bir pencerede çalışıyorken:

```powershell
.\YALITIM-KANITI.ps1 -Api http://localhost:XXXX
```

İki firmadan giriş yapıp aynı adresin farklı veri döndürdüğünü gösterir.
Ayrıca: jetonsuz istek, sahte `X-Tenant-Id` başlığı, yanlış parola, döner
jeton ve çalınmış jeton senaryoları. Kaba kuvvet kilidini de görmek için
`-KabaKuvvet` ekle (localhost'u 15 dakika kilitler).

**Betik yazarken:** bu makinede **Windows PowerShell 5.1** var, 7 değil.
`.ps1` dosyaları saf ASCII olmalı — 5.1 betikleri ANSI okur, UTF-8 türkçe
karakterler ayrıştırıcıyı bozar. `-SkipHttpErrorCheck` gibi 7'ye özgü
parametreler kullanılamaz.

## Kurallar

- `.env` dosyası **asla** git'e gitmez. Sırlar depoda durmaz.
- Parolalar ve `JWT_SECRET` `appsettings.json` içinde durmaz; ortam değişkeninden gelir.
- Kiracı kimliği **jetondan** okunur, istekten asla.
- Tabloları elle oluşturmuyoruz — şema değişiklikleri migration ile gelir.
- Her şey **UTC** saklanır; saat dilimi çevirimi sunum katmanının işi.
- Vardiya saatleri genişletilmiş biçimde tutulur: `23:00–31:00` = ertesi gün 07:00.

## Sıradaki adımlar

- [x] Depo, `.gitignore`, veritabanı container'ı
- [x] .NET çözümü ve proje iskeleti
- [x] İlk migration: `tenants`, `users`, `departments`, `teams`, `employees`, `employee_contracts`
- [x] Satır seviyesi güvenlik (RLS) ve çok kiracılık testleri — 5/5 yeşil
- [x] Kimlik katmanı: giriş, jeton, döner yenileme, kaba kuvvet kilidi — 12/12 yeşil
- [x] Roller ve izinler: izin politikaları, departman/ekip kapsamı — 26/26 yeşil
- [ ] Kullanıcı ve rol yönetimi uçları (`/users`, `/users/{id}/roles`)
- [ ] Çalışan API'si (yetkilendirme ile)
- [ ] Çalışan ekranı (Next.js)
- [ ] Yılmaz inceleme paketi
