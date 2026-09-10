# TShift Backend

.NET 10 · PostgreSQL 17 · EF Core

## Proje ayrımı

| Proje | Sorumluluk | Bağımlılığı |
|---|---|---|
| `TShift.Domain` | Kavramlar: kiracı, kullanıcı, departman, ekip, çalışan, sözleşme. Saf iş mantığı. | **Hiçbir şey.** Veritabanını değiştirsek bu proje aynen kalır. |
| `TShift.Infrastructure` | EF Core, DbContext, tablo eşlemeleri, kiracı yalıtımı | Domain |
| `TShift.Api` | HTTP uçları, ara katmanlar | Infrastructure |
| `TShift.Tests` | Testler — özellikle çok kiracılık yalıtımı | Infrastructure |

Bağımlılık oku hep tek yönde: **Api → Infrastructure → Domain**.
Domain hiçbir şeye bakmaz. Bu kural bozulursa katmanlar birbirine sızmış demektir.

## Adlandırma kararı

Kod içinde **Türkçe kavram adları** (`Calisan`, `KiraciId`, `HaftalikSaat`),
veritabanında **İngilizce/snake_case tablo adları** (`employees`, `tenant_id`).

Sebep: spec Türkçe yazıldı ve ekip Türkçe konuşuyor; ama tablo adlarının
uluslararası standartta kalması ileride işe yarar. Eşleme `Yapilandirmalar/`
klasöründe tek yerde toplanmıştır, dağınık değil.

## Çok kiracılık — iki katmanlı savunma

Bu projenin en kritik tasarım kararı. Bir sorguda `tenant_id` filtresinin
unutulması, A firmasının B firmasının verisini görmesi demektir. Şirketi bitiren
hata budur. O yüzden tek savunmaya güvenmiyoruz:

**1. Uygulama katmanı — EF küresel sorgu filtresi**
`TShiftDbContext.OnModelCreating` içinde, `IKiraciVarligi` uygulayan **her** varlığa
otomatik filtre eklenir. Yeni tablo eklerken arayüzü uygulamak yeterli; filtre
yazmayı unutmak diye bir şey yoktur.

**2. Veritabanı katmanı — satır seviyesi güvenlik (RLS)**
Her bağlantı açılışında `app.tenant_id` oturum değişkeni yazılır
(`KiraciBaglantiKesici.cs`). PostgreSQL politikaları bu değeri okur.
Uygulama katmanı hata yapsa, hatta biri ham SQL yazsa bile veritabanı başka
kiracının satırını döndürmez.

`FORCE ROW LEVEL SECURITY` kullanıldı: PostgreSQL varsayılanında tablo sahibi
RLS'ten muaftır ve biz tablo sahibi olarak bağlanıyoruz. FORCE olmadan güvenlik
yalnızca kâğıt üzerinde kalırdı.

**Hangisi asıl garanti:** RLS. EF sorgu filtresi bir kolaylıktır — her sorguya
elle filtre yazma zahmetini kaldırır. Güvenlik iddiası veritabanı katmanına
dayanır, çünkü uygulama katmanı hata yapabilir; testler de bunu böyle sınar
(2, 3 ve 4 numaralı testler EF'i kasten devre dışı bırakır).

Testler: `TShift.Tests/CokKiracilikTestleri.cs` — dördü de geçmeden bu katman
"çalışıyor" sayılmaz.

## Bilinen geçici çözümler

Dürüstlük için açıkça yazıyorum; bunlar kapanacak:

| Konu | Şu an | Ne zaman düzelecek |
|---|---|---|
| Kiracı kimliği `X-Tenant-Id` başlığından okunuyor | Herkes istediği kiracıyı yazabilir | Kimlik katmanı — jetondan okunacak, başlık silinecek |
| RLS betiği elle çalıştırılıyor | Sürüm kontrolünde ama otomatik değil | EF migration'a taşınacak |
| `/dev/seed` ve `/dev/tenants` uçları açık | Geliştirme kolaylığı | Yayına çıkmadan kaldırılacak |
| Testler geliştirme veritabanına bağlanıyor | Kendi verisini temizliyor | Testcontainers ile ayrı veritabanı |

## Uçlar

| Metod | Yol | Ne yapar |
|---|---|---|
| GET | `/health` | Uygulama ayakta mı |
| GET | `/health/db` | Veritabanına bağlanabiliyor mu |
| POST | `/dev/seed` | İki örnek kiracı ve çalışanları oluşturur |
| GET | `/dev/tenants` | Kiracıları listeler (kimlik gelene kadar açık) |
| GET | `/api/v1/employees` | `X-Tenant-Id` başlığındaki kiracının çalışanları |
