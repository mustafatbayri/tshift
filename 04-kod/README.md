# Kod

Gerçek yazılım. Demo v2'de akış onaylandıktan sonra başlayacak.

## Kararlaştırılan yığın

| Katman | Seçim |
|---|---|
| Veritabanı | PostgreSQL — tek veritabanı + tenant_id + satır seviyesi güvenlik |
| Backend | .NET 10 |
| Kimlik | **Kendi kimlik katmanımız** (Argon2id, döner yenileme jetonu). SSO faz 2 |
| Planlama motoru | Python + OR-Tools CP-SAT, ayrı servis |
| Kuyruk | RabbitMQ |
| Frontend | Next.js + TypeScript · Tailwind · shadcn/ui · TanStack Table |
| Yapay zekâ katmanı | Claude API (yalnız açıklama ve gerekçe üretimi) |
| Barındırma | Yerli sağlayıcı — demo ve gölge pilot için satın alınacak |

Ayrıntı: `02-spec/v1.1-master-spec.md` bölüm 7.

## Sıfırdan yazılacak tek karmaşık bileşen

Plan editörü takvimi (spec §9.6). Geri kalan 24 ekran bileşen kütüphanesinden
kurulur. Frontend desteği buraya harcanacak.
