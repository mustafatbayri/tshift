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

`down -v` sonrası kurulum sırası: `dotnet ef database update` → `01-rls.sql` → `02-uygulama-rolu.sql`.

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

| Uç | Ne yapar |
|---|---|
| `GET /health` | Ayakta mı |
| `GET /health/db` | Veritabanı bağlantısı ve kiracı sayısı |
| `POST /dev/seed` | İki örnek firma + 5 çalışan oluşturur |
| `GET /dev/tenants` | Kiracı listesi |
| `GET /api/v1/employees` | Çalışanlar — `X-Tenant-Id` başlığı zorunlu |

`/dev/*` uçları geçicidir, sürüm öncesi silinecek. `X-Tenant-Id` başlığı da
geçicidir; kimlik katmanı gelince kiracı **jetondan** okunacak, istekten değil
(spec §10).

## Testler

```powershell
cd backend
dotnet test
```

Veritabanı ayakta olmalı — testler gerçek PostgreSQL'e bağlanır, taklit
kullanmaz. Yalıtımın gerçekten çalıştığını ancak gerçek veritabanı gösterebilir.

## Yalıtımı gözle görme

API ayrı bir pencerede çalışıyorken:

```powershell
.\YALITIM-KANITI.ps1 -Api http://localhost:XXXX
```

Aynı adrese iki farklı kiracı kimliğiyle girip ne döndüğünü gösterir; başlıksız,
uydurma kimlikli ve çapraz erişim senaryolarını da dener.

## Kurallar

- `.env` dosyası **asla** git'e gitmez. Sırlar depoda durmaz.
- Parolalar `appsettings.json` içinde durmaz; ortam değişkeninden gelir.
- Tabloları elle oluşturmuyoruz — şema değişiklikleri migration ile gelir.
- Her şey **UTC** saklanır; saat dilimi çevirimi sunum katmanının işi.
- Vardiya saatleri genişletilmiş biçimde tutulur: `23:00–31:00` = ertesi gün 07:00.

## Sıradaki adımlar

- [x] Depo, `.gitignore`, veritabanı container'ı
- [x] .NET çözümü ve proje iskeleti
- [x] İlk migration: `tenants`, `users`, `departments`, `teams`, `employees`, `employee_contracts`
- [x] Satır seviyesi güvenlik (RLS) ve çok kiracılık testleri — 5/5 yeşil
- [ ] Kimlik katmanı: kayıt, giriş, jeton
- [ ] Çalışan API'si (yetkilendirme ile)
- [ ] Çalışan ekranı (Next.js)
- [ ] Yılmaz inceleme paketi
