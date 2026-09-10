# Sürümleme ve geri alma

Bu depoda iki farklı şeyi iki farklı yöntemle saklıyoruz. Karıştırmamak önemli.

| Ne | Nasıl versiyonlanır | Neden |
|---|---|---|
| Doküman (spec, demo, föy) | **Klasörde kopya** — `v1.0`, `v1.1` yan yana durur | İki sürümü aynı anda açıp karşılaştırmak istiyoruz |
| Kod | **Git** — eski sürüm klasörde durmaz, komutla geri çağrılır | Kopyalanan kod derlenmez: aynı sınıf iki kez tanımlanır, migration'lar çakışır |

Kodun eski hâli kaybolmuyor. Sadece görünmüyor. `git` her satırın her hâlini,
kimin ne zaman değiştirdiğiyle birlikte tutuyor.

---

## 1. Git'in dört aracı

| Araç | Ne işe yarar | Günlük hayattaki karşılığı |
|---|---|---|
| **commit** | Bir anı kaydeder, numara verir | "Kaydet" |
| **branch** (dal) | Ana gövdeye dokunmadan denemek | Müsvedde nüsha |
| **tag** (etiket) | Bir commit'e isim vermek | "Sürüm 0.1" yazan yer imi |
| **revert** | Yapılan bir değişikliği geri almak | "Geri al" — ama silmeden |

---

## 2. Çalışma ritmi

Kural tek cümle: **`main` her zaman yeşildir.**

`main` dalındaki kod her an derlenir ve bütün testleri geçer. Bir işi bitirene
kadar oraya dokunulmaz. Bitmemiş iş kendi dalında yaşar.

```powershell
# 1) Yeni iş = yeni dal. İsim ne yaptığını söylesin.
git switch -c dilim/kimlik-katmani

# 2) Çalış. Ara ara kaydet — küçük commit iyidir, büyük commit kötü.
git add .
git commit -m "Kullanici kaydi ve Argon2id parola saklama"

# 3) Birleştirmeden ÖNCE testler yeşil olmalı. Kırmızıysa birleştirilmez.
cd backend; dotnet test

# 4) Ana gövdeye al. --no-ff, bu işin nerede başlayıp bittiğini gecmise yazar.
git switch main
git merge --no-ff dilim/kimlik-katmani

# 5) Gonder.
git push
```

Adım 3 pazarlığa açık değil. Testin kırmızı olduğu bir dal `main`'e girmez.
Girerse `main` artık "her zaman yeşil" olmaz ve tüm sistem anlamını kaybeder.

---

## 3. Kilometre taşları

Önemli noktalara isim veriyoruz ki "o günkü hâline dön" demek tek komut olsun.

```powershell
git tag -a v0.1-kiracilik -m "Cok kiracilik yalitimi uctan uca calisiyor"
git push --tags
```

| Etiket | Ne demek |
|---|---|
| `v0.1-kiracilik` | Veritabanı, RLS, API, testler — yalıtım kanıtlandı |
| `v0.2-kimlik` | Kayıt, giriş, jeton. `X-Tenant-Id` başlığı kalktı |
| `v0.3-calisanlar` | Çalışan yönetimi uçtan uca, ilk gerçek ekran |
| `v0.4-motor` | Planlama motoru bağlandı, ilk plan üretildi |

Her etiketle birlikte `DEGISIM-GUNLUGU.md`'ye bir satır düşülür. Etiket
makinenin okuduğu, günlük insanın okuduğu kayıttır.

---

## 4. Geri alma el kitabı

| Durum | Komut | Not |
|---|---|---|
| Son değişiklik yanlıştı | `git revert HEAD` | **En güvenlisi.** Silmez; "bunu iptal ediyorum" diye yeni bir kayıt açar |
| Belli bir commit yanlıştı | `git revert <numara>` | Aradan tek bir değişikliği çıkarır |
| Tek bir dosyayı eski hâline döndür | `git checkout <numara> -- yol/dosya.cs` | Sadece o dosya döner |
| Eski bir günü görmek istiyorum | `git switch --detach v0.1-kiracilik` | Bakıp `git switch main` ile dönersin |
| Henüz kaydetmedim, hepsini iptal | `git restore .` | Kaydedilmemiş değişiklikler gider |
| Bu dal tamamen çöp oldu | `git switch main` + `git branch -D <dal>` | `main` etkilenmez |

`revert` ile `reset --hard` arasındaki fark önemli: **revert geçmişi korur,
reset geçmişi siler.** Bu projede `reset --hard` kullanmıyoruz. Bir şeyi geri
almanın kaydının kalması, alınmış olmasından daha değerli.

### Veritabanı

Kod geri alındığında veritabanı kendiliğinden geri gelmez.

```powershell
# Belli bir migration'a don
dotnet ef database update 20260910002040_Ilk --project src\TShift.Infrastructure --startup-project src\TShift.Api

# Son migration'i tamamen sil (henuz paylasilmadiysa)
dotnet ef migrations remove --project src\TShift.Infrastructure --startup-project src\TShift.Api

# Yerel veritabanini sifirdan kur - GELISTIRME MAKINESINDE, baska yerde asla
docker compose down -v
```

---

## 5. Geri almanın işe yaramadığı hata

Yukarıdakilerin hepsi **gürültülü** hatalar içindir: derlenmez, test kırılır,
uygulama patlar. Onlar kolaydır; makine bağırır, geri alırsın.

Asıl risk **sessiz** hatadır. Kod derlenir, testler geçer, uygulama çalışır —
ama ürettiği plan yanlıştır. Üç hafta kimse fark etmez.

Buna karşı geri alma bir işe yaramaz, çünkü geri alacak bir şey olduğunu
bilmezsin. Savunma başka yerde:

- **Bağımsız denetleyici.** Planı üreten kodla, planı denetleyen kod hiçbir
  mantığı paylaşmaz (spec §11). Planlayıcı kuralı yanlış anladıysa denetleyici
  aynı yanlışı tekrarlamaz, çünkü aynı kodu okumaz.
- **Kurallar veride, kodda değil.** Bir kural yanlışsa düzeltmek için kod
  değiştirmek gerekmez; parametre değişir, sürümü kayıtta kalır.
- **Değişmez denetim kaydı.** Her plan, hangi kural sürümüyle hangi veriden
  üretildiğini taşır. "Neden böyle planladı" sorusu her zaman cevaplanabilir.
- **Kuralı testin kendisi yazmaz.** Test, spec'teki kuralı kontrol eder.
  Kodu yazan kişi testi de yazarsa aynı yanlış varsayım iki yerde birden
  bulunur ve test hiçbir şey ispatlamaz.

Son madde en önemlisi ve en kolay ihlal edileni. 10 Eylül'deki RLS açığı tam
olarak bu yüzden bir gün gizli kaldı: "RLS açık mı" diye kontrol ettik, açıktı.
Yanlış soruydu. Doğru soru "bağlanan rol RLS'e tabi mi" idi ve onu ancak
davranışı ölçen bir test sorabildi.

---

## 6. Asla

- `main` dalına doğrudan yazmak
- Testler kırmızıyken birleştirmek
- `git push --force` (paylaşılan geçmişi ezer)
- `git reset --hard` (geçmişi siler)
- Gerçek veri üzerinde `docker compose down -v` benzeri bir komut
- Anlamadığın bir komutu internetten kopyalayıp çalıştırmak —
  özellikle içinde `rm`, `del`, `format`, `Remove-Item`, `--force` geçenleri
