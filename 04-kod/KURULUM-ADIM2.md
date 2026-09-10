# Adım 2 — kurulum sırası

Bu dosyadaki komutları sırayla çalıştır. Her başlıktan sonra çıktıyı kontrol et.

## 1 · Şablon dosyalarını sil

`dotnet new` bazı örnek dosyalar üretti, onlar bize lazım değil:

```powershell
cd "C:\Users\PC\Desktop\Tshift\04-kod\backend"
Remove-Item src\TShift.Domain\Class1.cs -ErrorAction SilentlyContinue
Remove-Item src\TShift.Infrastructure\Class1.cs -ErrorAction SilentlyContinue
Remove-Item tests\TShift.Tests\UnitTest1.cs -ErrorAction SilentlyContinue
```

## 2 · Derle

```powershell
dotnet build
```

`Build succeeded` görmelisin.

## 3 · Migration oluştur ve veritabanına uygula

```powershell
dotnet ef migrations add Ilk --project src\TShift.Infrastructure --startup-project src\TShift.Api
dotnet ef database update --project src\TShift.Infrastructure --startup-project src\TShift.Api
```

## 4 · Tabloları gör

```powershell
docker exec tshift-db psql -U tshift -d tshift -c "\dt"
```

Görmen gerekenler: `tenants`, `users`, `departments`, `teams`, `employees`,
`employee_contracts`, `__EFMigrationsHistory`.

## 5 · Satır seviyesi güvenliği aç

```powershell
cd "C:\Users\PC\Desktop\Tshift\04-kod"
docker exec -i tshift-db psql -U tshift -d tshift -f /dev/stdin < db\rls\01-rls.sql
```

Çıktının sonunda tablo listesi gelecek; `rls_acik` ve `sahibe_de_uygula`
sütunlarının **hepsi `t`** olmalı.

## 6 · API'yi çalıştır

```powershell
cd "C:\Users\PC\Desktop\Tshift\04-kod\backend\src\TShift.Api"
dotnet run
```

Ekranda `Now listening on: http://localhost:xxxx` yazacak. **O portu not al.**
Pencereyi açık bırak — API çalışıyor. Durdurmak için Ctrl+C.

## 7 · Dene (yeni bir PowerShell penceresi aç)

Port numarasını kendi gördüğünle değiştir:

```powershell
$p = 5080   # <-- kendi portunu yaz

# Sağlık
curl.exe "http://localhost:$p/health"
curl.exe "http://localhost:$p/health/db"

# Örnek veri oluştur (iki kiracı)
curl.exe -X POST "http://localhost:$p/dev/seed"

# Kiracıları listele - id'leri kopyala
curl.exe "http://localhost:$p/dev/tenants"
```

Sonra **çok kiracılık testini gözünle yap**. Yukarıdaki listeden iki kiracının
id'sini al ve sırayla dene:

```powershell
curl.exe -H "X-Tenant-Id: BIRINCI-KIRACI-ID" "http://localhost:$p/api/v1/employees"
curl.exe -H "X-Tenant-Id: IKINCI-KIRACI-ID"  "http://localhost:$p/api/v1/employees"
```

Birincide 3 çalışan (Mert, Selin, Burak), ikincide 2 çalışan (Ayşe, Emre)
görmelisin. **Hiçbiri diğerinin verisini göstermemeli.**

## 8 · Testleri çalıştır

```powershell
cd "C:\Users\PC\Desktop\Tshift\04-kod\backend"
dotnet test
```

Dört test de geçmeli. Bunlar Yılmaz'ın bakacağı testler.

## 9 · Git'e kaydet

```powershell
cd "C:\Users\PC\Desktop\Tshift"
git add .
git commit -m "Backend iskeleti: varliklar, DbContext, cok kiracilik, RLS, testler"
git push
```
