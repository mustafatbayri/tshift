# Testler

## Çalıştırma

Veritabanı ayakta olmalı (`docker compose up -d`) ve RLS betiği çalıştırılmış olmalı.

```powershell
cd C:\Users\PC\Desktop\Tshift\04-kod\backend
dotnet test
```

## Şu an ne test ediliyor

`CokKiracilikTestleri.cs` — projenin en kritik testi. Dört soru soruyor:

| # | Soru | Hangi katmanı sınıyor |
|---|---|---|
| 1 | A kiracısı sorgu yaptığında yalnız kendi verisi mi geliyor? | EF sorgu filtresi (uygulama) |
| 2 | EF'i atlayıp ham SQL yazarsak veritabanı tutuyor mu? | RLS (veritabanı) |
| 3 | Kiracı bağlamı yokken hiçbir şey görünmüyor mu? | RLS |
| 4 | Başka kiracının kimliğiyle kayıt yazılabiliyor mu? | RLS `WITH CHECK` |

2 ve 3 numaralı testler önemlidir: uygulama katmanı hata yapsa bile veritabanının
tutması gerekir. Bu testler geçmiyorsa çok kiracılık **güvenli değildir**.

## Bilinen eksik

Testler yerel geliştirme veritabanına bağlanıyor ve bağlantı dizesi dosyada sabit.
Kendi verisini oluşturup sonunda temizliyor. İleride ayrı bir test veritabanı
(Testcontainers) kurulacak.
