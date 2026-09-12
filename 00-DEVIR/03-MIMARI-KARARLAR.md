# MİMARİ KARARLAR

Her karar için: **ne**, **neden**, **hangi alternatif elendi**, **sonradan
değiştirmenin bedeli**, **nerede**.

> **Bu dosyanın amacı:** Yazılımların baştan yazılma sebebi kötü kod değil,
> **anlaşılmaz** koddur. Bir ekip devraldığında *"bu satır neden böyle?"* diye
> sorar; cevap yoksa dokunmaya korkar, kuşatır, sonra yeniden yazmayı teklif
> eder. Yeniden yazma kararı teknik değil **psikolojiktir**.
>
> Yapay zekâyla yazılan kodda bu risk daha yüksektir: kod hızlı üretilir,
> gerekçesi üretenin kafasında kalır, kafası da her oturumda sıfırlanır.
> Bu dosya o sigortadır.

---

## M-01 · Çok kiracılık: tek veritabanı + `tenant_id` + iki katmanlı yalıtım

**Karar (09 Eylül).** Bütün kiracılar tek PostgreSQL veritabanında, her
tabloda `tenant_id` kolonu. Yalıtım **iki katmanda** birden:

1. **EF Core global query filter** — uygulama katmanı, her sorguya otomatik
   `WHERE tenant_id = @current` ekler.
2. **PostgreSQL Row Level Security (RLS) + `FORCE ROW LEVEL SECURITY`** —
   veritabanı katmanı. Ham SQL'de bile geçerli.

Kiracı kimliği her bağlantı açılışında `app.tenant_id` oturum değişkenine
(GUC) yazılır — `DbConnectionInterceptor` ile.

**Neden iki katman?** Birincisi unutulabilir (yeni sorgu, ham SQL, yeni
geliştirici). İkincisi unutulamaz. Uygulama katmanı **açığın bulunacağı
katmandır**; asıl garanti veritabanında olmalı.

**Elenen alternatifler:** Kiracı başına ayrı veritabanı (yönetim ve migration
maliyeti; 100 müşteride 100 migration), kiracı başına ayrı şema (aynı sorun,
daha az belirgin).

**Geri alma bedeli:** 🔴 **Çok yüksek.** Tüm veri taşınır.

→ `04-kod/db/rls/`, `04-kod/backend/src/TShift.Infrastructure/Persistence/`

---

## M-02 · İki veritabanı rolü: `tshift` ve `tshift_app`

**Karar (10 Eylül) — bir hatanın sonucu.** Bkz. `05-HATA-OTOPSILERI.md` O-1.

| Rol | Ne yapar | Yetkisi |
|---|---|---|
| `tshift` | Migration, şema ve yetki betikleri | Sahip / süper |
| `tshift_app` | **Uygulamayı taşır** | `NOSUPERUSER`, `NOBYPASSRLS`, yalnız CRUD |

**Neden:** PostgreSQL'de süper kullanıcı RLS'i **tamamen** aşar — `FORCE`
bile durduramaz. Uygulama süper kullanıcıyla bağlanırsa M-01'in ikinci
katmanı **sessizce yok olur.**

`docker-compose.yml` içinde bağlantı dizeleri **kasıtlı olarak ayrı iki
değişkende** tutuluyor (`ConnectionStrings__TShift` ve
`TSHIFT_SAHIP_BAGLANTI`). İkisi karışırsa güvenlik sessizce kaybolur; ayrı
tutmak bu karışmayı zorlaştırır.

**Geri alma bedeli:** 🟢 Düşük, ama geri alınmamalı.

→ `04-kod/db/rls/02-uygulama-rolu.sql`

---

## M-03 · Kimlik katmanı kendi kodumuzda (Keycloak elendi)

**Karar (09 Eylül, spec v1.1).** Kimlik doğrulama dışarıdan alınmıyor.

**İçerik:** Argon2id parola saklama (64 MB / 3 tur / 4 paralellik), 15
dakikalık erişim jetonu (JWT), 30 günlük **döner** yenileme jetonu, jeton
yeniden kullanım tespiti, 5 deneme / 15 dakika kaba kuvvet kilidi.

**Neden Keycloak elendi:** Çok kiracılı yapımızda kiracı-kullanıcı eşleşmesi
ve kapsam modeli zaten bizde. Keycloak ek bir dağıtım birimi, ek bir hata
kaynağı ve kapsam modelimizi tam karşılamayan bir soyutlama getiriyordu.

**Bedeli kabul edildi:** Güvenlik kodunu kendimiz taşıyoruz. Bu yüzden kimlik
katmanı testleri (K1–K7) diğerlerinden daha ayrıntılı.

**Geri alma bedeli:** 🟡 Orta.

→ `04-kod/backend/src/TShift.Infrastructure/Kimlik/`

---

## M-04 · İzin kodları jetonda, kapsam veritabanında

**Karar (10 Eylül).**

- **İzinler** (ne yapabilir) JWT'ye yazılır — spec §7.4.
- **Kapsam** (nerede yapabilir) jetona konmaz, **her istekte veritabanından
  okunur.**

**Neden ayrı:** İzin listesi kısa ve seyrek değişir. Kapsam listesi uzayabilir
(çok departman/ekip) ve kapsam değişikliğinin **anında** etkili olması iyidir.

**Kabul edilen bedel:** Geri alınan bir izin, jeton süresi dolana kadar
(≤15 dk) taşınmaya devam eder. Acil iptalde yenileme jetonları da düşürülmeli.

**Geri alma bedeli:** 🟢 Düşük.

---

## M-05 · Tek `KapsamKurali`: hem listeleme hem yazma kontrolü

**Karar (11 Eylül).** Kapsam kuralı **tek bir yerde** tanımlı:

```
KapsamKurali(yetki) → Expression<Func<Calisan, bool>>
   ├─ KapsamUygula(IQueryable)  → listeyi filtreler
   └─ Kapsamda(Calisan)         → derlenip tek kayda uygulanır
```

**İlke: göremeyeceğin kaydı oluşturamazsın.**

**Neden:** İki ayrı yerde yazılsaydı zamanla ayrışır ve bir gün *"listede
göremediğim ama oluşturabildiğim kayıt"* ortaya çıkardı —
`RISKLER-VE-ONLEMLER.md`'deki 4 numaralı hata sınıfı (kopyalanmış mantık).

⚠️ **Bu birliği sabitleyen bir test yok.** Bkz. `06-ACIK-RISKLER.md` A-2.

→ `04-kod/backend/src/TShift.Infrastructure/Yetki/KapsamFiltresi.cs`

---

## M-06 · Denetim kaydı: otomatik, aynı işlemde, sadece-eklenir

**Karar (11 Eylül).** Üç kasıtlı özellik:

1. **Otomatik** — uçlarda tek tek çağrılmaz, EF'in `SaveChanges` akışına
   bağlı. Yeni tablo ya da yeni uç **kendiliğinden** kapsanır.
2. **Aynı işlemde** — değişiklik ve denetim satırı tek `SaveChanges`'te
   gider; biri yazılıp diğeri yazılamaz. (İstemcide üretilen UUIDv7
   kimlikler sayesinde mümkün.)
3. **Sadece eklenir** — `tshift_app` rolünün `audit_log` üzerinde UPDATE ve
   DELETE yetkisi **yok**. Kısıt uygulamada değil **veritabanında**.

**Neden şimdi yazıldı:** Tutulmayan geçmiş sonradan üretilemez. Sonraya
bırakılsaydı aradaki dönem kalıcı olarak karanlıkta kalırdı.

**Geri alma bedeli:** 🔴 Geri alınamaz (geçmiş kaybolur).

→ `04-kod/backend/src/TShift.Infrastructure/Denetim/`, `04-kod/db/rls/05-denetim-kaydi.sql`

---

## M-07 · Jetonlar `httpOnly` çerezde; arayüz API'ye doğrudan gitmez

**Karar (11 Eylül).** Tarayıcı hiçbir zaman API'ye doğrudan gitmiyor;
istekleri Next.js sunucusu taşıyor (BFF deseni).

**Neden:** `localStorage` kolaydır ama sayfadaki **herhangi bir betik**
jetonu okuyabilir. Çerezde tarayıcı jetonu isteğe ekler, sayfa kodu göremez.
**Yan fayda:** CORS ayarı gerekmiyor.

**Geri alma bedeli:** 🟡 Orta.

---

## M-08 · Mimari testleri: özellik değil **yasa** sınayan katman

**Karar (10 Eylül).** Normal testler "şu özellik çalışıyor mu" der.
`MimariTestleri` "şu kural hâlâ geçerli mi" der.

M1 RLS zorunluluğu · M2 RLS istisna listesi kapalı · M3 korumasız uç yok ·
M4 Türkçe `I` tuzağı · M5 ayar dosyasında sır yok · M6 denetim kaydı
sadece-eklenir.

**Neden:** Bunlar bugün bir şey yakalamak için değil, **altı ay sonra
unutulacak bir kuralı hatırlatmak** için varlar. Yeni tablo ekleyip RLS
betiğini güncellemeyi unutmak mükemmel çalışan, veri dönen, hiçbir testi
kırmayan bir hatadır — ve bir gün bir firma diğerinin verisini görür.

**Tasarım detayı:** M1 elle yazılmış tablo listesi kullanmaz; EF modelinden
`IKiraciVarligi` uygulayan varlıkları okur. Yeni varlık **kendiliğinden**
kapsanır.

⚠️ **Bu testleri hiçbir şey zorla koşturmuyor.** CI yok. Bkz. A-4.

---

## M-09 · Planlama motoru ayrı servis: Python + OR-Tools CP-SAT

**Karar (spike sonrası, Eylül).** Motor .NET içinde değil, ayrı bir Python
servisi. İletişim sözleşme üzerinden.

**Ölçülmüş dayanak:** CP-SAT %99,5 hedef kapsama + 0 fazla mesai; greedy
%95,7 + 92 saat. Optimuma uzaklık %0,01. 2000 çalışanda 60 saniyede %98,9
kapsama (greedy 2000'de **geçersiz plan** üretti).

**Elenen alternatif:** Go — resmî OR-Tools bağlayıcısı yok.

**Geri alma bedeli:** 🔴 Yüksek (motorun tamamı yeniden yazılır).

### Henüz yazılmadı — yazılmadan önce karar verilmiş olan

Motor **dört bağımsız parçaya** ayrılacak:

```
girdi şema doğrulaması → çözücü → BAĞIMSIZ doğrulayıcı → puan hesaplayıcı
                                        ↑
                        çözücünün koduyla HİÇBİR ŞEY paylaşmaz
```

**Doğrulayıcı önce yazılır, çözücü sonra.** Doğrulayıcı, çözücünün "geçerli
plan ürettim" bayrağına bakmaz; planı sıfırdan kurallara karşı denetler.
Hiçbir plan doğrulayıcıdan geçmeden kullanıcıya gösterilmez.

**Neden:** Optimizasyonda "doğru çıktı" tek bir beklenen listeyle sınanamaz —
aynı girdiye birden çok geçerli plan vardır. Çözücüyü ve testini aynı oturum
yazarsa, yanlış kural yorumu **ikisinde de tutarlı biçimde** tekrar eder ve
test yeşil yanar.

---

## M-10 · Kurallar veride, kodda değil

**Karar (spec v1.0).** Vardiya kuralları parametre olarak veritabanında.

**Kanıtlandı:** Otel senaryosunda gece vardiyası kuralları koda tek satır
eklenmeden, yalnız veri ile devreye girdi — 0 sert ihlal, %99,6 kapsama.
"Tek üründe çok sektör" iddiasının teknik dayanağı budur.

**Yan fayda:** Yanlış bir kural kod değişikliği gerektirmez; parametre
değişir ve **sürümü kayıtta kalır** (denetim kaydı sayesinde "bu plan hangi
kural sürümüyle üretildi" sorusu cevaplanabilir).

**Geri alma bedeli:** 🔴 Yüksek (motorun tamamı).

---

## M-11 · Zaman: UTC + genişletilmiş saat modeli

**Karar (spec).** Saklama UTC; vardiya gece yarısını aşabildiği için
genişletilmiş saat gösterimi.

**Geri alma bedeli:** 🔴 **Her plan yeniden yorumlanır.**

⚠️ **Hiçbir test bunu sınamıyor.** Bir vardiya ürününde yaz saati geçişi ve
gece yarısını aşan vardiya birinci sınıf doğruluk sorunudur. Bkz. A-5.

---

## M-12 · Benzersizlik kodda değil, veritabanı kısıtında

**Karar (11 Eylül).** "Bu personel no var mı?" diye sorup sonra yazmak
yetmez: iki istek aynı anda gelirse ikisi de "yok" görür.

Veritabanı kısıtı yapısal olarak engelliyor; kod yalnızca hatayı anlaşılır
mesaja çeviriyor (`23505` → `PERSONEL_NO_TEKRAR`, HTTP 409).

⚠️ Bekçisi yok. Bkz. A-3.

---

## M-13 · `login_attempts` bilerek RLS dışında

**Karar (10 Eylül).** Kaba kuvvet sayacı, kiracının kim olduğu **bilinmeden**
yazılmak zorunda — aksi halde saldırgan var olmayan bir firma adı yazarak
kilidi tamamen atlar.

Tablo hiçbir API ucundan dışarı açılmaz; parola ya da jeton içermez.

Gerekçe hem koda hem SQL betiğine yazıldı ki ileride *"RLS unutulmuş"* diye
"düzeltilmesin". M2 testi bu istisnayı **tanıdığı için** sessizce dördüncü
bir istisna eklenemiyor.

---

## M-15 · Kapsam zorunluluğu: engelle **ve** güvenli davran

**Karar (12 Eylül).** Kapsamsız kullanıcı sorununa **iki katmanlı** yaklaşım:

| Katman | Ne yapar |
|---|---|
| **Y-13/Y-14** (yeni) | Kötü yapılandırmanın **oluşmasını zorlaştırır** — arayüz ve API engeller, oluşursa görünür kılar |
| **Y-8** (mevcut) | Kötü yapılandırma **oluştuğunda güvenli davranır** — kapsamsız kullanıcı hiçbir şey görmez |

**Neden ikisi birden:** Engellemenin delikleri var. En belirleyicisi:
**bir departman silindiğinde kapsam satırları onunla gider** — kimse
kapsamsız kullanıcı oluşturmaz, durum kendiliğinden doğar. Engelleme
mekanizması bu senaryoda hiç devreye girmez.

**Elenen alternatif — veritabanı seviyesinde yasaklayıcı kısıt:** Ertelenmiş
kısıt tetikleyicisi teknik olarak mümkün, ama içe aktarma politikasıyla
(kapsamsız satır kabul edilir) çelişiyor. Muafiyet bayrağı gerektirirdi ve
"güvenlik kuralını atlatan bayrak" tam olarak O-1'i doğuran kalıptır.
Veritabanının işi burada **yasaklamak değil görünür kılmak** olarak
tanımlandı (bir view).

**Asıl sınır API'dir**, arayüz değil — arayüz hiçbir zaman güvenlik sınırı
sayılmaz.

**Durum:** ⏳ Kullanıcı yönetimi ekranı yazılırken uygulanacak.
Kabul ölçütleri: `06-ACIK-RISKLER.md` A-12.

---

## M-14 · Giriş isteği firma kısa adını (slug) taşır

**Karar (10 Eylül).** `users` benzersizliği `(tenant_id, eposta)` olduğu için
e-posta tek başına kimlik değil; **aynı kişi iki firmada kullanıcı olabilir.**

Canlıda firma alt alan adından gelecek (`anadolu-cm.tshift.com`); kullanıcı
elle yazmayacak.

---

## Karar geri alma maliyeti — özet

| Karar | Durum | Sonradan değiştirmenin bedeli |
|---|---|---|
| M-01 Kiracılık modeli | ✅ Çalışıyor | 🔴 Tüm veri taşınır |
| M-02 İki DB rolü | ✅ Çalışıyor | 🟢 Düşük |
| M-03 Kendi kimlik katmanımız | ✅ Çalışıyor | 🟡 Orta |
| M-04 İzin jetonda / kapsam DB'de | ✅ Çalışıyor | 🟢 Düşük |
| M-05 Tek `KapsamKurali` | ✅ Çalışıyor | 🟢 Düşük |
| M-06 Denetim kaydı | ✅ Çalışıyor | 🔴 Geçmiş kaybolur |
| M-07 `httpOnly` çerez | ✅ Çalışıyor | 🟡 Orta |
| M-08 Mimari testleri | ✅ Çalışıyor | 🟢 Düşük |
| M-09 Motor: Python/CP-SAT, ayrı servis | ⏳ Yazılmadı | 🔴 Yeniden yazım |
| M-10 Kurallar veride | ✅ Karar verildi | 🔴 Motorun tamamı |
| M-11 UTC + genişletilmiş saat | ✅ Karar verildi | 🔴 Her plan yeniden yorumlanır |
| M-12 Benzersizlik DB kısıtında | ✅ Çalışıyor | 🟢 Düşük |
| **Eşzamanlılık (satır sürümü, idempotency)** | ⚠️ **Yazılmadı** | 🟡 Bozulan veriyi tespit etmek zor |
| Para ve yuvarlama kuralları | Gündemde değil | 🔴 Geçmiş hesaplamalar yeniden yapılır |
| Barındırma | Ertelendi (satış sonrası) | 🟡 Orta |
