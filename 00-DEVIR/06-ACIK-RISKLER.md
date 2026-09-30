# AÇIK RİSKLER

**Bilinen ama henüz kapatılmamış** maddeler. Kanıtı olmayan her şey buraya
yazılır — `00`–`05` arası dosyalar yalnız **kanıtlanmış** bilgiyi taşır.

**Son güncelleme:** 2026-09-16

## Öncelik anahtarı

| İşaret | Anlamı |
|---|---|
| 🔴 | Şimdi kapatılmalı. Bozulursa sessiz ve pahalı. |
| 🟡 | Motor/pilot öncesi kapatılmalı |
| 🟢 | Bilinen borç, takvimli değil |

---

## ✅ A-1 · KAPANDI (12 Eylül 2026) — süper kullanıcı bekçisi eklendi

**Çözüm:** `MimariTestleri.cs` içine `M0 - Baglanan rol super kullanici degil
(RLS gercekten yururlukte)` testi eklendi. Test paketi 38 → **39**, hepsi
yeşil.

Test rol **adına** değil, `current_user`'ın **yetkisine** bakıyor
(`pg_roles.rolsuper`, `rolbypassrls`). Doğrulandı: `tshift` → `t`/`t`,
`tshift_app` → `f`/`f`. Uygulama sahibi rolle bağlansa M0 iki iddiadan
birden kırılır.

`RISKLER-VE-ONLEMLER.md`'deki yanlış bekçi satırı da düzeltildi.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

**Ne:** `02-DEGISMEZLER.md` K-9 diyor ki *"uygulama `tshift_app` ile bağlanır,
`tshift` ile asla"*. `RISKLER-VE-ONLEMLER.md` ise bunun bekçisinin
`M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` adlı bir test olduğunu yazıyor.

**Bulgu (12 Eylül):** **Böyle bir test yok.** Ne `MimariTestleri` içinde, ne
`CokKiracilikTestleri` içinde, ne `YALITIM-KANITI.ps1` betiğinde. Test
dosyaları bağlantı dizesinde `tshift_app` **kullanıyor** — ama o rolün
gerçekten `NOSUPERUSER`/`NOBYPASSRLS` olduğunu **kimse doğrulamıyor**.

**Neden kritik:** Bu, projedeki **en ciddi hatanın** (O-1) tekrar etme
yoludur. Biri `04-kod/db/rls/02-uygulama-rolu.sql` betiğini değiştirse, ya da yeni
bir ortamda `tshift_app` yanlışlıkla süper yetkiyle kurulsa:

- Bütün RLS korumaları sessizce devre dışı kalır
- `M1` testi yine yeşil yanar (RLS **tanımlı**, sadece etkisiz)
- `1`, `2`, `3`, `4` numaralı kiracılık testleri de yeşil yanabilir — çünkü
  onlar EF'in uygulama katmanı filtresiyle de geçer
- **Hiçbir şey kırmızı yanmaz**

Yani `02-DEGISMEZLER.md`'deki 8 kiracılık değişmezinin tamamı tek bir
korumasız noktaya bağlı.

**Çözüm (basit):** Test paketine bir bekçi eklemek — bağlanan rolü
`pg_roles`'a sorup `rolsuper` ve `rolbypassrls` alanlarının `false` olduğunu
doğrulamak. ~15 satır.

**Ek olarak:** Bu bulgunun kendisi, dokümanın koddan sapabileceğinin
kanıtıdır. `00-BURADAN-BASLA.md` §5'teki kural (*"karşılığında
çalıştırılabilir kanıt gösteremediğin cümle yazılmaz"*) tam bu yüzden var.
Bu boşluk, devir paketi hazırlanırken doküman ile kod karşılaştırıldığı için
ortaya çıktı.

</details>

---

## ✅ A-4 · KAPANDI (14 Eylül 2026) — CI yeşil

`.github/workflows/testler.yml` GitHub Actions'ta **koştu ve yeşil yandı.**
Artık her `git push` sonrası 39 test ve 7 mimari kuralı kendiliğinden koşuyor.

**Neden bu madde kritikti:** Kurallar artık öneri değil **kapı**. Ve pencere
protokolünün (bkz. `00-BURADAN-BASLA.md` §5b) önkoşulu buydu — pencere
değişince "testleri çalıştırmayı hatırlayan bağlam" ortadan kalkar; otomatik
kapı o boşluğu doldurur.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-4 · Hiçbir kapı zorlayıcı değil: CI yok

**Ne:** 39 test ve 7 mimari kuralı yalnız `TEST.ps1` elle çalıştırıldığında
koşuyor. `git push` sırasında hiçbir şey çalışmıyor.

**Neden kritik:** `MimariTestleri` iyi tasarlanmış kapılar — ama kapıyı kimse
zorla açtırmıyor. Unutulan bir gün, kırık kod GitHub'a girer ve kimse görmez.
`main` her zaman yeşil kuralının **hiçbir teknik dayanağı yok**, yalnız
alışkanlık.

**Çözüm:** GitHub Actions — her `push`'ta PostgreSQL servisi ayağa kalkar,
migration + RLS betikleri çalışır, `dotnet test` koşar. Repo zaten GitHub'da.
Tek dosya, ~1 saat.

</details>

---

## 🔴 A-6 · Testlerin gerçek gücü ölçülmedi

**Ne:** 39 test yeşil. Ama bu testlerin kodu **kasten bozsak** fark edip
etmeyeceğini bilmiyoruz.

**Neden kritik:** "39 test var" ile "39 test bir şeyi koruyor" aynı şey değil.
Zayıf bir iddia (örn. yalnız "hata fırlatmadı" kontrolü) yeşil yanar ama
hiçbir şey garanti etmez.

**Çözüm:** **Stryker.NET** — kodu kasten bozar (`>` yerine `>=`, `true` yerine
`false`, sabit dönüş) ve testlerin yakalayıp yakalamadığını ölçer. Sonuç tek
bir yüzde: *"testleriniz kasten bozulmuş kodun %X'ini yakalıyor."*

Kritik modüller: `Yetki`, `Persistence` (kiracılık), `Denetim`.

**Yan fayda:** Mustafa'nın C# okumadan test kalitesini denetleyebileceği tek
sayı budur. Yılmaz'a *"testler yeşil"* demek yerine *"testler kasten bozulmuş
kodun %X'ini yakalıyor"* demek bambaşka bir iddiadır.

---

## 🟢 A-5 · Zaman modeli — A4 KOŞUYOR ve YEŞİL (16 Eylül), A5 ertelendi

**16 Eylül:** Gece yarısını aşan vardiya modeli artık **sınanıyor.**
`09-motor/dogrulayici/zaman.py` Z-1…Z-6'yı uyguluyor ve **A4 altın senaryosu
yeşil.** Ayrıca beş birim testi zaman modelinin kendisini sabitliyor:

| Test | Ne koruyor |
|---|---|
| `test_gece_yarisini_asan_vardiya_dogru_uzunlukta` | Z-1: 16:00–01:00 dokuz saattir |
| `test_gece_yarisini_asan_vardiya_BASLADIGI_gune_sayilir` | Z-2: Cumartesi nöbeti Pazar'a kaymaz |
| `test_cakisma_mutlak_zamanda_olculur` | Z-3: gün sınırını aşan çakışma yakalanır |
| `test_ucu_uca_degen_vardiyalar_cakismaz` | Sınır: 16'da biten ve 16'da başlayan örtüşmez |
| `test_dinlenme_gercek_bitisten_olculur` | Z-4: 8 saatlik dinlenme ihlali görülür |

**Kırmızı kanıt yapıldı:** zaman hesabı kasten bozulduğunda testler yakaladı.

**Kalan:** **A5 (DST geçişi) ertelendi** — K-12, Türkiye'de yaz saati yok ve
yurt dışı müşteri yok. Altyapı korunuyor (IANA bölge adı, mutlak zaman),
kural katalogda pasif duruyor. Yurt dışında ilk müşteri açıldığında yazılacak.

**Neden artık 🟢:** Asıl risk *"zaman modeli hiç sınanmıyor"*du. Sınanıyor.
Kalan kısım bilinen ve kayıtlı bir erteleme.

<details>
<summary>Maddenin 14 Eylül hâli (kayıt için)</summary>

### A-5 · Zaman modeli — v1.3'te TANIMLANDI, test hâlâ yok

**14 Eylül:** Master Spec **§6.3**'e gece yarısını aşan vardiya kuralı tam
olarak yazıldı (Z-1…Z-6) ve DST taşınabilir-pasif olarak modellendi. Ayrıca
§16'da **A4** (gece yarısı → 8 saat dinlenme ihlali) ve **A5** (DST geçişi)
altın senaryoları tanımlandı.

**Kalan iş:** tanım var, **test yok.** A4 ve A5 çalıştırılabilir teste
çevrilmeli.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-5 · Zaman modeli hiç sınanmıyor (G-6)

**Ne:** UTC + genişletilmiş saat modeli karar verildi (M-11) ama **tek bir
test bile yok**.

**Neden bir vardiya ürününde kritik:**

- Yaz saati geçişinde "minimum dinlenme 11 saat" kuralı gerçekte 10 veya 12
  saat olur
- Gece yarısını aşan vardiya iki güne yayılır; çakışma ve günlük saat
  hesapları bundan etkilenir
- Haftalık saat toplamı hafta sınırının hangi tarafına düştüğüne bağlı
- Türkiye kalıcı UTC+3'te, ama çok uluslu müşteride bu gerçek bir hata
  kaynağı

**Neden şimdi ucuz:** Motor henüz yazılmadı. Zaman modelini sonradan
düzeltmenin bedeli: **her plan yeniden yorumlanır** (🔴 en yüksek geri alma
maliyetlerinden biri).

</details>

</details>
---

## 🟡 A-2 · Y-12'nin bekçisi yok: "göremeyeceğin kaydı oluşturamazsın"

**Ne:** Liste filtresi ile yazma kontrolünün **tek** `KapsamKurali`'ndan
geldiği tasarım gereği doğru (M-05) — ama bunu sabitleyen test yok.

**Risk:** Biri iki kontrolü ayırırsa hiçbir şey kırılmaz. Zamanla ayrışır ve
*"listede göremediğim ama oluşturabildiğim kayıt"* ortaya çıkar.

**Çözüm:** Şefin, kapsamı dışındaki bir departmana çalışan eklemeye
çalışırken 403 aldığını doğrulayan bir HTTP sınırı testi.

---

## 🟡 A-3 · G-5'in bekçisi yok: eşzamanlı çift kayıt

**Ne:** Benzersizlik veritabanı kısıtında (M-12) ama eşzamanlılık senaryosu
test edilmiyor.

**Çözüm:** İki isteği paralel gönderip birinin 201, diğerinin
`PERSONEL_NO_TEKRAR` (409) aldığını doğrulayan test.

---

## 🟡 A-7 · Eşzamanlılık: satır sürümü ve idempotency yazılmadı

**Ne:** İki kullanıcı aynı planı aynı anda düzenlerse ne olacağı tanımsız.
Aynı istek iki kez gelirse (ağ tekrarı, kullanıcı çift tıklaması) ne olacağı
tanımsız.

**Neden:** `RISKLER-VE-ONLEMLER.md` §4'te "şimdi ucuz, sonra pahalı"
listesinde **tek açık madde** bu. Bozulan veriyi sonradan tespit etmek zordur
— ama en azından mümkündür (bu yüzden 🔴 değil 🟡).

**Ne gerek:** Satır sürümü (optimistic concurrency), idempotency anahtarı,
`409 Conflict` sözleşmesi.

**Vardiya ürününde neden şart:** Plan editöründe sürükle-bırak var; iki
kullanıcının aynı anda aynı vardiyayı düzenlemesi **beklenen** bir durum,
istisna değil.

---

## 🟡 A-8 · PgBouncer / oturum değişkeni riski — **çözülmedi**

**Ne:** Kiracı kimliği `set_config('app.tenant_id', …, false)` ile
**oturum seviyesinde** yazılıyor. Bir **işlem kipli** (transaction-mode)
bağlantı havuzlayıcı (PgBouncer) araya girerse, aynı fiziksel bağlantı
farklı kiracıların işlemlerine verilebilir.

**Sonucu:** Kiracı bağlamının karışması — yani **çapraz kiracı veri
sızıntısı**. Bu ürünün en ciddi hata sınıfı.

**Durum:** Bilinen, belgelenmiş, **çözülmemiş**. Şu anda havuzlayıcı yok, o
yüzden aktif bir risk değil. Ama yayına çıkarken havuzlayıcı büyük
ihtimalle devreye girecek.

**Olası yönler (hiçbiri denenmedi):** oturum kipli havuzlama; `SET LOCAL` ile
işlem seviyesine taşıma; kiracı kimliğini GUC yerine her sorguya parametre
olarak geçirme.

**Ne zaman:** Barındırma kararı verilirken — yayından önce.

---

## 🟡 A-9 · KVKK ve kişisel veri çalışması yapılmadı

**Ne:** Çalışan verisi kişisel veridir. Anonimleştirme, saklama süresi,
erişim kaydı, silme talebi — bunlar ürün özelliği değil **yasal
yükümlülük**.

**Ne zaman:** Gerçek veri girmeden **önce**. Bir kere yanlış kurulursa geri
dönüşü zor. `RISKLER-VE-ONLEMLER.md` §5'te "dış göz gereken üç an"dan biri.

**Mevcut koruma:** Denetim kaydı yazıldı (erişim kaydının altyapısı hazır).
Pilot verisi anonimleştirilmiş gelecek — kırmızı çizgi.

---

## 🟡 A-10 · Motor sözleşmesi — DÜZELTME: spec §11'de var, v1.3'te tamamlandı

⚠ **Bu madde yanlış açılmıştı (14 Eylül).** *"Motor sözleşmesi yazılmadı"*
deniyordu; Master Spec §11'de 138 satırlık sözleşme zaten vardı.

**v1.3'te eklenenlerle sözleşme tamamlandı:**

| Eksikti | v1.3'te |
|---|---|
| Geçmiş penceresi | **§11.2** — en az 14 gün atama, yıllık fazla mesai, aylık adalet sayacı. Eksikse motor çalışmaz. |
| Onarım döngüsü | **§11.7** — ilk üretim + en fazla 2 onarım, sonra `cozumsuz` |
| İdempotency | **§11.7** — `istek_anahtari`; çift tıklama iki plan üretmez |
| Tekrarlanabilirlik | **§11.7** — garanti **edilmiyor**, gerekçesiyle. Yerine plan kopyalama (§9.7) |
| Gece yarısı zaman modeli | **§6.3** — altı maddelik kural seti |
| Kabul senaryoları | **§16** — A1–A12 |

**Geriye kalan iş sözleşme yazmak değil, uygulamak:** §16'daki 12 altın
senaryoyu çalıştırılabilir teste çevirmek, sonra doğrulayıcı, sonra çözücü.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-10 · Motor sözleşmesi yazılmadı

**Ne:** M-09'da mimari kararlaştırıldı (dört parça, doğrulayıcı önce) ama
sözleşme yazılmadı: girdi şeması, çıktı şeması, hata/UNSAT biçimi, zaman
aşımı davranışı, tekrarlanabilirlik garantisi.

**Yazılması gerekenler — sırasıyla:**

1. **Değişmez listesi (V01–V12).** Çalışan müsait olmadığı aralığa atanamaz ·
   aynı çalışan çakışan iki vardiyada olamaz · minimum dinlenme korunur ·
   günlük/haftalık azami saat aşılmaz · yetkinlik gereksinimi karşılanır ·
   lokasyon/seyahat kuralı · minimum kapsama · hiçbir sert kısıt amaç
   ağırlığıyla çiğnenmez · imkansız girdi **illegal plan üretmez, UNSAT
   döner ve çatışmayı açıklar** · aynı seed → aynı sonuç · **manuel düzenleme
   de aynı doğrulayıcıdan geçer** · denetim kaydı tam ve değiştirilemez.
2. **Bağımsız doğrulayıcı** — çözücünün koduyla hiçbir şey paylaşmaz.
3. **Çözücü.**

**Kritik sıra:** Doğrulayıcı **önce** yazılır. Önce "neyin yanlış olduğunu
bilen" parça, sonra "çözmeye çalışan" parça.

</details>

### Ölçek matrisi — alt uç dahil (karar: 12 Eylül)

Spike'ta yalnız üst uç test edildi. Motor sözleşmesi **her iki ucu** kapsamalı:

| Senaryo | Kişi | Ne sınar | Durum |
|---|---|---|---|
| **Mikro** | 5–8 | Tek kişilik ekip, bir kişinin tüm haftayı kapsaması, 0/1 sınırları | ❌ Hiç test edilmedi |
| **Küçük** | ~20 | Bar/havuz ekibi. Sıkı kısıt, **sık UNSAT**, adalet görünür, manuel düzenleme yoğun | ❌ Hiç test edilmedi |
| **Orta** | 80–120 | Otel departmanı | ❌ Hiç test edilmedi |
| **Nominal** | 350 | Çağrı merkezi | ✅ Spike'ta geçti |
| **Üst** | 500–2000 | Ölçek sınırı, P95 süre ve bellek | ✅ Spike'ta geçti (2000'de 60 sn, %98,9) |
| **Yetersiz kaynak** | herhangi | Talep > kapasite → **illegal plan değil, UNSAT + çatışma açıklaması** | ❌ Hiç test edilmedi |

**Alt uç, üst uçtan daha zor olabilir** — çünkü orada asıl soru "hızlı çözüyor
mu" değil, **"çözemediğinde ne söylüyor"**. Küçük müşterinin en sık göreceği
ekran UNSAT ekranıdır.

---

## 🟡 A-12 · Kapsam zorunluluğu (Y-13/Y-14) — karar verildi, uygulanmadı

**Karar tarihi:** 12 Eylül 2026 (Mustafa) · **Uygulanacak:** kullanıcı
yönetimi ekranı ve uçları yazılırken

**Ne:** Kapsam seviyesindeki bir kullanıcı, kapsam atanmadan tek tek
oluşturulamaz. İçe aktarmada izinli, ama işaretlenir ve görünür olur.

**Neden şimdi uygulanamıyor:** Kullanıcı/rol yönetim uçları ve ekranı henüz
yazılmadı; roller şu an örnek veriden geliyor. Uygulanacak bir yer yok.
Karar burada kayıtlı ki ekran yazılırken atlanmasın.

### Kabul ölçütleri — Mustafa'nın onayına sunuldu

| # | Ölçüt | Katman |
|---|---|---|
| KK-1 | Kullanıcı oluşturma/düzenleme ekranında kapsam seviyesi "Kapsam" seçildiğinde, en az bir departman veya ekip seçilmeden form kaydedilemez | Arayüz |
| KK-2 | API'ye doğrudan, "Kapsam" seviyesi + boş kapsam listesiyle istek gelirse **400 `KAPSAM_ZORUNLU`** döner | **API — asıl sınır** |
| KK-3 | Aynı kural düzenlemede de geçerli: var olan bir kullanıcının **son** kapsam satırı kaldırılamaz | API |
| KK-4 | İçe aktarmada kapsamsız satır kabul edilir, kullanıcı "kapsam atanmamış" olarak işaretlenir | API |
| KK-5 | Kapsam atanmamış kullanıcılar listede uyarı rozetiyle görünür; sayıları ekranın üstünde uyarı şeridinde toplanır | Arayüz + sorgu |
| KK-6 | Bir departman/ekip silindiğinde kapsamsız kalan kullanıcılar da aynı uyarıya düşer | Sorgu |
| KK-7 | **Y-8 değişmez kalır:** kapsamsız kullanıcı hiçbir kayıt görmez | Zaten var (Y8 testi) |

**KK-3 ve KK-6 dikkat gerektirenler:** İlki, kuralın yalnız oluşturmada değil
düzenlemede de geçerli olduğunu söylüyor — atlanması kolay. İkincisi,
engelleme mekanizmasının hiç devreye girmediği hâlde kapsamsız kullanıcı
oluşabilen tek senaryo.

### Veritabanı katmanı: "yasakla" değil "görünür kıl"

Mustafa'nın önerisi veritabanının da aynı uyarıyı vermesiydi. **Yasaklayıcı
bir kısıt önerilmiyor**, gerekçesiyle:

- Kapsam satırları ayrı tabloda. "Bu kullanıcının başka bir tabloda en az bir
  satırı olmalı" kuralı basit bir `NOT NULL`/`CHECK` ile ifade edilemez;
  ertelenmiş (`DEFERRABLE INITIALLY DEFERRED`) bir kısıt tetikleyicisi gerekir.
- Bu tetikleyici **KK-4 ile doğrudan çelişir**: içe aktarma kapsamsız satır
  yazabilmeli. Muafiyet için oturum bayrağı gerekir — ve "güvenlik kuralını
  atlatan bayrak" tam olarak O-1'i (süper kullanıcı) doğuran kalıptır.
- API katmanı zaten gerçek sınır (KK-2). Tetikleyici onu ikinci kez yazmak
  olur; iki yerde yazılan kural zamanla ayrışır (hata sınıfı 4).

**Bunun yerine veritabanının işi görünürlük:** kapsamsız kalmış, kapsam
seviyesindeki kullanıcıları listeleyen bir görünüm (view). KK-5 ve KK-6 bunu
okur. Ayrıca durumun **sonucu** zaten veritabanı seviyesinde güvenli: RLS +
kapsam filtresi kapsamsız kullanıcıya sıfır satır döndürür.

### Spec etkisi

Spec §3.2'ye ek gerekiyor. Y-8 zaten spec'ten bilinçli bir sapmaydı; Y-13/
Y-14 onun tamamlayıcısı. **Spec v1.3 yazılırken bu bölüm birlikte
güncellenmeli.**

---

## 📌 Araç kararı (12 Eylül · 15 Eylül'de eklendi) — ne kullanılacak, ne kullanılmayacak

Mustafa: *"Kaptan sensin, yönlendir."* Karar ve gerekçeleri:

### Kullanılacak

| Araç | Ne için | Sıra |
|---|---|---|
| **GitHub Actions** | Kapıları zorlayıcı yapmak | 1 — yazıldı, doğrulanacak |
| **CsCheck** (property-based) | Girdileri makine üretir, ben değil. 14 boş senaryo sınıfının çoğunu kapatır **ve motorun metamorfik testleri de bununla yazılır** | 2 |
| **Bruno** (API koleksiyonu) | **Mustafa'nın kendi elleriyle** koşacağı API senaryoları — "bağımsız oracle"ın bizde uygulanabilir hâli | 3 |
| **Stryker.NET** (mutasyon) | Testlerin gerçek gücü, tek sayı. **Dar kapsamda, tek seferlik** | 4 |

**Stryker uyarısı:** Testlerimiz gerçek PostgreSQL'e gidiyor (~10 sn/paket).
Mutasyon testi her bozulmuş kopya için paketi yeniden koşar → yüzlerce kopya
× 10 sn = saatler. Bu yüzden **gecelik değil, tek seferlik** ve yalnız saf
mantık içeren yerlerde (`Yetki/KapsamFiltresi`).

### Şimdilik kullanılmayacak — ve nedeni

| Araç | Neden şimdi değil |
|---|---|
| **Schemathesis** (API fuzzing) | OpenAPI şeması yok ve uç sayısı az (5-6). CsCheck aynı boşluğun çoğunu daha ucuza kapatıyor. Uç sayısı artınca yeniden bakılacak. |
| **SBOM, bağımlılık allowlist, lisans tarama** | Bir avuç paket var, hepsi Microsoft. Kurulum maliyeti bugünkü riskten büyük. |
| **k6 / NBomber** (yük testi) | Motor yokken yük testi anlamsız. Motor sözleşmesiyle birlikte. |
| **SonarQube / CodeQL** | `MimariTestleri` zaten kritik kuralları tutuyor. Ek gürültü, ek bakım. |
| **opencode** — paralel ikinci ajan | **Yazıcı olarak kapalı** (R5). **Salt-okunur inceleyici olarak da reddedildi — 23 Eylül**, ama yerine bir şey kondu: haftalık elle tarama. Gerekçe aşağıda, 📌 *İnceleme döngüsü*. Tarihçe: `00-DEVIR/oturumlar/2026-09-15-calisma-bicimi-opencode.md` ve `00-DEVIR/oturumlar/2026-09-23-inceleme-karari.md` |

**İlke:** Her araç bir bakım yüküdür. Yanlış alarm veren araç, bir süre sonra
bakılmayan araca dönüşür (bkz. O-7). Kullanılan araç sayısı değil, kapatılan
açık sayısı ölçülür.

⚠ **Araç olmayan karar — karıştırılmasın (15 Eylül).** Aynı gün alınan
"iki pencere / geri bildirim yüzeyleri" kararı bir **araç** kararı değildir:
yeni bir şey kurulmuyor, var olan `.\TEST.ps1` ve `docker compose logs -f`
komutlarının nerede durduğu belirleniyor. Yeri `00-BURADAN-BASLA.md` §5b
(pencere protokolü), burası değil.

---

## 🟡 A-13 · Kapsam envanteri — DÜZELTME: kısmen var

⚠ **Bu madde yanlış açılmıştı (14 Eylül'de düzeltildi).** *"Kapsam envanteri
hiç hesaplanmadı"* deniyordu. Gerçekte iki yerde var:

- **Master Spec §14** — fazlama ve teslim planı
- **Köken dokümanı §3** (MVP / P1 / P2 ayrımı) ve **§25** (12 haftalık yol
  haritası, her hafta için gösterilebilir kabul ölçütüyle)

**Gerçekten eksik olan:** bu planların **bugünkü duruma göre güncellenmesi.**
12 haftalık yol haritası projenin başında yazıldı; o zamandan beri dikey dilim
tamamlandı, gerçek veri geldi, kapsam kararları değişti (mola, 3 alternatif,
bildirim kanalları). Yol haritasının neresindeyiz — bu ölçülmedi.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-13 · Kapsam envanteri yapılmadı — Ocak hedefi ölçülmedi

**Ne:** Spec'te 44 tablo, 24 ekran, 27 kural, motor, içe aktarma ve 4 kanallı
bildirim var. **MVP yapılmayacak** (karar: `01-PROJE-KIMLIGI.md` §4) — yani
kapsam sabit. Ama bu kapsamın Ocak sonuna sığıp sığmadığı **hiç
hesaplanmadı**.

**Neden 🔴:** Sığmıyorsa bunu Eylül'de öğrenmek ile Aralık'ta öğrenmek
arasında dağlar kadar fark var. Eylül'de öğrenilirse karar planlı verilir
(takvim uzatma, ilk sektörü daraltma, ekran sadeleştirme — hepsi Mustafa'nın
kararı). Aralık'ta öğrenilirse panikle kesilir.

**Ne yapılacak:** Spec'teki her ekran ve özelliği çıkarıp haftalara yayan bir
envanter. **Amacı kesmek değil görmek.** Kapsam kesme önerisi, Mustafa açıkça
istemedikçe yapılmaz.

**Dikkat edilecek:** Riskin ağırlığı motorda değil, **24 ekran ve
CRUD/yönetim kuyruğunda.**

</details>

---

## ✅ A-14 · KAPANDI (13–14 Eylül 2026) — gerçek veri geldi ve analiz edildi

Bir seyahat acentesinin 3,5 aylık PDKS + vardiya planı alındı, analiz edildi.
**529 kural ihlali** bulundu (274 haftalık saat, 167 ardışık gün, 88 dinlenme).
Bulgular, Mustafa'nın kapsam kararları ve süreç kuralı:
**`07-GERCEK-VERI-BULGULARI.md`**.

Veri `06-veri/ham` altında, **git'e girmiyor** (`.gitignore`).
Analiz araçları `07-motor/` altında (⚠ orada motor yok — `OKU-BENI.md`).

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-14 · Çağrı merkezi veri örneği hâlâ gelmedi

**Ne:** Mustafa'nın eski işvereninden alınacak gerçek (anonimleştirilmiş)
çağrı merkezi verisi bekleniyor. Gölge pilotun girdisi bu.

**Neden 🔴 — ve neden kod işi değil:** Bu pazarda ret sebebinin bir numarası
eksik özellik değil, **ürünün operasyonun gerçek işleyişine oturmaması**.
Spec eksiksiz uygulansa bile, tek bir gerçek operasyonun verisi görülmeden
bu risk kapanmaz. Kodla telafi edilemeyen tek açık madde budur.

**Sahibi:** Mustafa. Geliştirmeden bağımsız ilerleyebilir — ve ne kadar erken
gelirse o kadar çok karar etkiler.

</details>

---

## 📌 İnceleme döngüsü (23 Eylül) — tadımcı kararı kapandı

**15 Eylül'de ertelenen karar bugün kapandı.** O günkü metin şuydu:

> *"Motorun bağımsız doğrulayıcısı (M-09) yazıldığında yeniden bakılacak, iki
> haftalık ölçüm şartıyla: on incelemede kayda değer bulgu yoksa bırakılır."*

**M-09'un doğrulayıcısı 16 Eylül'de yazıldı. Tetikleyici ateşlendi, kimse
fark etmedi** — T-26'nın üçüncü örneği ve ilk kez bir **ürün** kararında değil,
**sürecin** kendisinde.

### Ölçüm şartı fazlasıyla karşılandı

16 Eylül'de deney elle yapıldı: farklı sağlayıcı (GPT), salt-okunur, üç tur.

| Şart | Gerçekleşen |
|---|---|
| On incelemede bulgu yoksa bırak | **Üç incelemede 19 bulgu** |
| Yanlış alarm riski (O-7) | **Sıfır** — 19'u da bu tarafta ölçülerek doğrulandı |

### Ama tasarım değişti — ölçüldü

15 Eylül'ün kurgusu *"birleştirme öncesi **dal farkını** incele"* idi. `git log`
ile bakıldı: 16 Eylül'de `09-motor/` klasörünün **tamamı o gün doğdu**, yani o
günün dal farkı motorun kendisiydi ve tasarım tesadüfen çalışırdı.

**Bir daha çalışmaz.** Şu sınıflar hiçbir dal farkında görünmez:

| Bulgu | Neden |
|---|---|
| **T-19** talep biçimi | Kod eski, değişmiyor; yanlış olan **gelenek** |
| **T-28** `gecmis_vardiyalar` | Bir **yokluk** — olmayan şey diff'te görünmez |
| **T-29** `DONMUS_GUN` ölü | Ölü kod yolu; kimse dokunmuyor |
| **T-34, T-35** 🔴 | `04-kod`'da, 11 Eylül'den; motor dalının dışında |

> **Dal farkı incelemesi ile şartname-kod taraması iki ayrı alettir.** Birincisi
> yeni işteki gerilemeyi, ikincisi **birikmiş sapmayı ve eksikliği** yakalar.

### Karar

| | |
|---|---|
| **Kalıcı araç** (opencode vb.) | ❌ **Reddedildi.** Değeri üreten şey ikinci ajan değil **soğukluk**; depoda bağlam biriktiren inceleyici onu kaybeder. Makalenin kendi uyarısı: *"talimatlar bayatsa iyi yapılandırılmış ama kötü bağlama dayanan karar çıkar"* |
| **Haftalık elle tarama** | ✅ Mustafa + farklı sağlayıcının modeli. **İki geçiş:** haftanın farkı · şartname-kod taraması |
| **Yöntem nerede yazılı** | `05-inceleme/beceriler/` — dört dosya. `00-DEVIR/` dışında, çünkü R7 eşikte |
| **Yeni ölçüm şartı** | Arka arkaya **üç haftada** kayda değer bulgu yoksa sıklık düşer (**bırakılmaz**). İki geçiş ayrı ayrı ölçülür |

### ⚠ Bu düzenlemenin açık tarafı

Mimar (Yılmaz) şu an ulaşılamıyor. Geri alma bedeli 🔴 olan beş karar —
**M-01** kiracılık · **M-06** denetim kaydı · **M-09** motor mimarisi ·
**M-10** kurallar veride · **M-11** zaman modeli — için **ikinci bir teknik
insan görüşü yok.**

Dış tarama bunu karşılamaz: kodun şartnameye uyup uymadığına bakar, **kararın
kendisinin doğru olup olmadığına** değil. Yılmaz'a ulaşılınca ilk gösterilecek
şey bu beş satır.

---

## 📌 T-37 · Giriş dokümanı hiçbir tazelik kontrolünün kapsamında değil

**Bulundu:** 23 Eylül, `README.md` düzenlenirken · **Ölçüldü:** evet

`README.md` deponun **ilk okunan** dosyası ve içeriği aylardır bayat:

| README diyor ki | Gerçek |
|---|---|
| *"`04-kod/` — Gerçek yazılım. **Henüz boş.**"* | 39 test, çalışan API, RLS, denetim kaydı |
| *"Kod \| **Başlamadı**"* | 8 Eylül'den beri yazılıyor |
| *"Master spec \| **Yazılıyor**"* | v1.4 bitti (A-15, 16 Eylül) |
| Teknoloji listesinde **Keycloak** | **M-03'te elendi** — kimlik katmanı kendi kodumuzda |
| Klasör tablosu `04-kod/`'da bitiyor | `00-DEVIR/`, `05-inceleme/`, `06-veri/`, `07-motor/`, `08-motor-testleri/`, `09-motor/` yok |

**Neden kimse yakalamadı.** `DENETIM.py`'nin 6. kontrolü tazeliğe bakıyor ama
yalnız **oturum günlüğü ile değişim günlüğü arasında**. `README.md` hiçbir
kontrolün kapsamında değil — ne tazelik, ne tutarlılık.

**Bu, 16 Eylül'ün *"17 kural"* hatasıyla aynı sınıf** ve dış incelemenin
uyarısının tam hedefi: *bayat bağlam, iyi yapılandırılmış yanlış karar üretir.*
README'yi okuyup *"kod başlamamış"* sanan biri projeye yanlış yerden girer.

**Bugün yapılan:** yalnız ölçülebilir olgular düzeltildi (klasör listesi,
durum tablosu, elenen teknoloji). **Yapılmayan:** bir tazelik kontrolü
eklenmedi — `DENETIM.py`'nin neyi doğru sayacağı karar gerektiriyor.

---

## 📌 SÜREÇ KURALI (14 Eylül) · Veri kapsam kararı vermez

**Mustafa'nın uyarısı:** *"Bu dataları analiz amaçlı attım, bu datalardan bir
varsayım çıkarıp kapsamı değiştirmen için değil."*

**Kural:** Veriden **bulgu** çıkarılır, **kapsam kararı** çıkarılmaz. İkisi
ayrı ayrı işaretlenir:
- **Bulgu** = "veride şu var" (ölçüm, tartışmasız)
- **Öneri** = "buna göre şunu yapabiliriz, **karar senin**"

*Neden yazıldı:* Claude "plan ufku 7–35 gün arası değişiyor, modelimiz bunu
desteklemeli" önerisini bulgu gibi sundu. Mustafa reddetti; gerekçesi daha
güçlüydü (adalet penceresi sabit olmalı). Veride görülen esneklik aslında
düzensizlikti.

---

## 🟢 A-11 · Diğer bilinen borçlar

| Ne | Not |
|---|---|
| `/dev/*` uçları | Yayından önce kaldırılmalı. Şu an `IsDevelopment() \|\| TSHIFT_KURULUM=="true"` ile kapalı. `TSHIFT_KURULUM=true` canlıda **asla** olmaz. |
| `Directory.Packages.props` | Merkezî paket sürüm yönetimi yok |
| `01-rls.sql` migration'a katlanmadı | Şema ve güvenlik iki ayrı yerden geliyor |
| Kullanıcı/rol yönetim uçları | Yazılmadı; roller şu an örnek veriden geliyor |
| Denetim kaydı hacim yönetimi | Arşivleme/bölümleme politikası yok |
| Gerçek hacimde performans | Spike'ta ölçüldü, üründe ölçülmedi |
| G15 secret sızıntısı — log tarafı | D3 yalnız denetim kaydını kapsıyor; uygulama logu ve hata çıktısı sınanmıyor |
| I-8 `httpOnly` çerez bekçisi | Arayüz tarafında hiç test yok |
| Yılmaz'ın GitHub işbirlikçisi olarak eklenmesi | Mustafa'nın yapması gereken |
| Çağrı merkezi veri örneği | Mustafa'nın eski işvereninden bekleniyor |
| Demoda telefon yerleşimi | Kenar çubuğu → alt, tablolar → kart (opsiyonel) |

---

## ✅ A-15 · Şartname v1.4 yazılmadı — **KAPANDI (16 Eylül 2026)**

> **Kapanış:** `02-spec/v1.4-master-spec.md` yazıldı. On maddelik listenin
> tamamı işlendi, artı araştırmada çıkan iki madde daha. v1.3'e dokunulmadı.
>
> **Listeye sonradan eklenenler:** `GECE_POSTASI_DEVRI` (katalogda hiç
> olmayan yasal kural) · gece sınırının sektör istisnası · `HAFTA_TATILI`
> penceresinin kayan olması (T-11) · kural sayısının 27 değil 35 olması (T-10).
>
> **Listede olup gereksiz çıkan:** `leaves` durum alanı — v1.3 §8.3'te
> **zaten vardı** (`talep | onayli | reddedildi | iptal`). K-9'un gerçek
> eksiği alan değil, yayınlanmış planı düşüren akıştı; o da §4.6'ya yazıldı.
>
> *Ders: "eksik" diye kaydedilen bir madde, kapatılmadan önce gerçekten
> eksik mi diye bakılmalı. Bu maddede on maddenin biri zaten yapılmıştı.*

*Özgün metin, kayıt için:*

### ~~Şartname v1.4 yazılmadı — on maddelik birikmiş fark~~

**Ne:** Altın senaryo onay turu (15 Eylül) on ürün kararı doğurdu ve bunların
çoğu **şartnamede karşılığı olmayan** şeyler. Yürürlükteki şartname v1.3, artık
alınmış kararları **yansıtmıyor.**

**Neden kırmızı:** Şartname "son karar" olmaktan çıktı. Bir sonraki pencere
v1.3'ü okuyup çalışmaya başlarsa, on karar boyunca yanlış yere gider.
`08-URUN-KARARLARI.md` K-serisi şu an gerçeğin tek kaynağı, ama orası bir
**sicil**, şartname değil.

| Ne eklenecek | Nereye | Karar |
|---|---|---|
| `leaves` tablosuna durum alanı (talep/onaylı/iptal/reddedildi) | §8.3 | K-9 |
| `plan_violations`'a kabul edilmiş ihlal + kabul eden + zaman + gerekçe | §8.6 | K-10 |
| `/solve` çözümsüz çıktısına `en_iyi_plan` | §11.3 | K-10 |
| Vardiya şablonuna mola penceresi (süre + min/max) | §8.4 | K-14 |
| `MOLA_KAPSAMASI` **SERT → YUMUŞAK** + §5.4 ağırlık satırı (7/9/6) | §6.4, §5.4 | K-14 |
| **§6 kataloğuna `yasal` sütunu** + yasal kurallara "yasal sınır" değeri | §6, §8.4 | K-16, K-17 |
| Yayın kapısı kuralı | §4.5, §9.6 | K-16 |
| `TERCIH_KARSILAMA` yeniden değerlendirmesi (çalışan tercihi yok) | §6.8 | K-13 |
| Hedef kapsama kabul eşiği %95 | §13.4 | K-8 |
| Önceki sekiz tutarsızlık | T-1…T-8 | v4 §4 |

**En kritik satır `yasal` sütunu:** K-10 (ihlal kabulü) ve K-16 (yayın kapısı)
tamamen ona dayanıyor. Bayrak olmadan **ikisi de uygulanamaz** — sistem hangi
ihlalin kabul edilebileceğini bilemez.

**Ayrıca çözülmemiş bir tasarım sorusu var:** bayrak kurala mı ait, eşiğe mi?
`GUNLUK_AZAMI` örneği: kanunun tavanı 11 saat, bizim varsayılanımız 9. 9–11
arası aşım firma politikasının ihlali, 11 üstü kanunun. Yani yasal kuralların
ayrıca bir "yasal sınır" değeri olmalı. K-17'de açık bırakıldı.

**v1.3'e dokunulmayacak** — yeni sürüm dosyası açılacak (versiyonlama kuralı).

---

## 🟡 A-16 · İki hukuki yorum uzman gözü bekliyor

**Ne:** İki karar hukuki yoruma dayanıyor ve ikisini de yapay zekâ türetti.

| # | Konu | Karar | Risk yönü |
|---|---|---|---|
| 1 | Mola hakkı eşiğinin **brüt** vardiya süresine uygulanması (K-4) | İş Kanunu md. 68 | **Düşük.** Hata yönü tek taraflı: brüt hesap kanunun istediğinden asla az mola vermez |
| 2 | Hangi kuralların `yasal = true` olduğu (K-17) | İş Kanunu geneli | **Orta.** Yanlış sınıflandırılan bir yasal kuralın ihlali kabul edilebilir hâle gelir |

**İkincisi için alınan önlem:** belirsiz bırakılan kurallar **yasal gibi**
davranılıyor (K-17 güvenli varsayılanı) — yani hata yönü "kabul edemedim"
şikâyeti, "sessizce kabul ettim" sızıntısı değil.

**Fikstürleri bloke etmiyor.** Sahaya çıkmadan önce hukukçu bakmalı; o zamana
kadar ikisi de `[çıkarım]` etiketini koruyor.

### 16 Eylül güncellemesi — araştırma yapıldı, madde daraldı

Mustafa'nın isteğiyle (*"hukuki konuları benden daha iyi araştırabilirsin"*)
birincil mevzuat kaynaklarından araştırma yapıldı:
`02-spec/v1.4-hazirlik/02-mevzuat-arastirmasi.md`.

**Çözülenler:**

| Konu | Sonuç | Dayanak |
|---|---|---|
| `PART_TIME_LIMIT` yasal mı | ✅ **Evet** | Fazla Çalışma Yön. md. 8 |
| `ARDISIK_CALISMA_GUNU` yasal mı | ❌ **Hayır**, türev | İş K. md. 46 + Y.22.HD 2019/1727 |
| `VARDIYA_ARASI_DINLENME` 11 saat | ✅ Doğrulandı | Postalar Yön. md. 9 |
| Eksik yasal kural | `GECE_POSTASI_DEVRI` bulundu | Postalar Yön. md. 8 |
| Gece 7,5 saat mutlak mı | ❌ **Sektör istisnası var** | 6645 s. K. |

**Hâlâ açık — bu madde bu ikisi için duruyor:**

1. **Mola eşiği brüt süreye mi uygulanır (K-4).** İş K. md. 68 ara dinlenmesini
   *"günlük çalışma süresi"*ne bağlıyor ama aynı madde *"ara dinlenmeleri
   çalışma süresinden sayılmaz"* diyor — tanım kendine dönüyor. Kararımız
   **brüt**; hata yönü tek taraflı (kanunun istediğinden asla az mola vermez).
2. **Yazılı onayın fazla mesai ücretine etkisi.** Turizmde gece 7,5 saati aşan
   kısım için onay alınmış olması, o sürenin fazla çalışma ücreti doğurup
   doğurmadığını değiştirmiyor olabilir. Akademik kaynaklar bunu açık uygulama
   sorunu sayıyor. **Bugün bizi bağlamıyor** — plan yapıyoruz, bordro
   hesaplamıyoruz; ücret modülü gelirse ilk bakılacak yer.

**Risk yönü değişmedi:** güvenli varsayılan yürürlükte (K-17) — emin
olunamayan kural yasal gibi davranır, ihlali kabul edilemez.

⚠ **Araştırma uzman görüşünün yerine geçmez.** Artık uzmana boş sayfayla değil,
madde numaralı bir tabloyla gidilecek — görüşme kısalır, gerekliliği kalkmaz.

---

## ✅ A-17 · `ADALET_DENGESI` ihlal eşiği — **KAPANDI (16 Eylül 2026)**

**Karar K-27:** eşik **2**, ölçü ortalamadan sapma, tek yönlü, devir yükü
dâhil. Kural doğrulayıcıda yazıldı, sekiz birim testiyle sabitlendi.

**Kırmızı kanıtta üç test zayıf çıktı ve güçlendirildi** — ayrıntı
`oturumlar/2026-09-16-bagimsiz-dogrulayici.md` EK bölümünde.

**Devam eden dar parça → T-13:** `saat` boyutu. K-27 eşiği sayı olarak verdi;
süre boyutu karara bağlanmadı ve `SAAT_DENGESI` ile örtüşme açık. Sessizce
atlanmıyor — `/evaluate` cevabı `eksik_boyutlar` alanında bildiriyor.

<details>
<summary>Maddenin özgün hâli (kayıt için)</summary>

### A-17 · `ADALET_DENGESI` ihlal eşiği tanımsız *(T-12)*

**Ne:** Şartname §6.5 kuralı tanımlıyor — *"yük çalışanlar arasında dengeli
dağılsın"*, pencere aylık, boyutlar gece + hafta sonu + saat. Ama **ihlal
eşiğini** tanımlamıyor: dağılım ne kadar sapınca ihlal sayılır?

| Kural | Eşik var mı |
|---|---|
| `SAAT_DENGESI` | ✅ `tolerans_saat`, varsayılan ±2 |
| `ADALET_DENGESI` | ❌ yalnız ağırlık (5) |

**Ne yapıldı:** Doğrulayıcıda bu kural **bilerek yazılmadı.** Eşiği koda gömüp
uydurmak, bir ürün kararını kodun içine gizlemek olurdu. Kural
`uygulanmayan_kurallar` listesinde açıkça görünüyor ve bir test
(`test_adalet_dengesi_bilerek_yazilmadi`) birinin ileride sessizce eşik
uydurmasını engelliyor.

**Neden 🟢:** Yumuşak bir kural. Yazılmamış olması hiçbir planı yanlış yere
**geçerli** göstermiyor; yalnız puan hesabı eksik kalıyor. A7 senaryosu
(adalet karşılaştırması) çözücüyle birlikte bunu gerektirecek.

**Ne gerek:** Mustafa'nın kararı — *"aynı kişi ayda kaç gece / kaç hafta sonu
fazladan çalışırsa bu adaletsizliktir?"*

</details>

---

## ✅ T-15 · Fazla mesai ayarı — **KAPANDI (16 Eylül 2026)**

**Kapanış:** K-30. Mustafa: *"Zaten hedef hiç gitmemek. Gidilecekse de
minimum gitmek. Mantığımız değişmedi."*

**Sonuç: kod değişmedi, çünkü mevcut davranış zaten karara uygunmuş.**

| Durum | Davranış | Doğrulandı |
|---|---|---|
| Yalnız hedef kapsama iyileşecek | Fazla mesai yapılmaz | `test_fazla_mesai_hedef_kapsama_icin_KULLANILMAZ` |
| Asgari kapsama zorluyor | Gereken kadar yapılır | `test_fazla_mesai_asgari_kapsama_zorlarsa_KULLANILIR` |
| Tavan zorunlu aşıma yetmiyor | Plan çözümsüz | `test_profil_tavani_zorunlu_fazla_mesainin_SINIRIDIR` |

### ⚠ Maddeyi açarken yazdığım teşhis yanlıştı

*"§5.2'nin profil tavanı pratikte hiç kullanılmıyor"* demiştim. Tavan ölü
bir sayı değil: **zorunlu** aşımın ne kadarına izin verildiğini o söylüyor.
Aynı sahnede CALISAN profilinde (tavan 0) plan çözümsüz, DENGELI (10) ve
KAPSAMA'da (15) çözülüyor.

Doğrusu: tavan **isteğe bağlı** fazla mesai için hiç kullanılmıyor,
**zorunlu** fazla mesai için belirleyici.

**Kendi dersim:** riski açarken *"motor 150 hücre kazanacak olsa bile fazla
mesai yapmıyor"* diye yazdım ve bunu bir **kusur** gibi sundum. Ölçüm doğruydu,
**yorumu** yanlıştı — ürünün istediği tam olarak oydu. Ölçtüğüm sayıyı ürün
kararı yerine koymuşum.

---

## 🟢 T-16 · Adalet eşiği ortalamaya göre; şişirilerek aşılabilir

**Bulundu:** 16 Eylül 2026 · **Durum:** motorda etkisiz, doğrulayıcıda **var**

**Ne.** K-27 adaletsizliği *"ortalamadan 2 fazla"* diye tanımlıyor. Ortalama
sabit değil, **plandan çıkan** bir sayı. Dolayısıyla bir ihlali kaldırmanın
matematiksel olarak geçerli ama sahada saçma bir yolu var: *başkalarına
gereksiz cumartesi vererek ortalamayı yükseltmek.*

**Motorda kapatıldı** — eşik terimi amaç fonksiyonundan çıkarıldı (K-29),
yerine artan marjinal maliyet kondu. Motor artık ortalamayı oyunlayamaz.

**Doğrulayıcıda duruyor ve durması doğru:** doğrulayıcı planı *sayar*,
üretmez. K-27 neyin ihlal olduğunu söylüyor; doğrulayıcı ona uyuyor.

**Kalan risk:** plan elle düzenlendiğinde (§4.4 yerel onarım) bir yönetici,
farkında olmadan, birine gereksiz hafta sonu vererek başkasının adaletsizlik
bayrağını düşürebilir. Küçük bir risk ama kaydı olsun.

**Neden 🟢:** Kimseyi yanlış yere geçerli göstermiyor; ters yönde çalışıyor
(fazladan çalıştırma, eksik değil). Tanım değişirse (K-29 onayıyla birlikte)
yeniden bakılır.

---

## ✅ T-17 · Actions eylemleri — **KAPANDI (16 Eylül 2026)**

**Ne vardı.** Her iki CI işi de aynı uyarıyı veriyordu: `actions/checkout@v4`,
`actions/setup-python@v5` ve `actions/setup-dotnet@v4` Node 20 hedefliyordu,
GitHub onları Node 24'te **zorla** koşturuyordu. Kapı çalışıyordu ama zorlama
kalktığında çalışmayacaktı — **kendi kendine kırmızıya dönecek** bir madde.

**Ne yapıldı.**

| Eylem | Önce | Sonra | Node 24'e geçen ilk sürüm |
|---|---|---|---|
| `actions/checkout` | v4 | **v7** | v5 |
| `actions/setup-python` | v5 | **v7** | v6 |
| `actions/setup-dotnet` | v4 | **v6** | v6 |

En güncel ana sürümlere çıkıldı ki aynı iş birkaç ay sonra tekrarlanmasın.
`checkout` v7'nin kırıcı değişikliği fork PR'larıyla ilgili
(`pull_request_target` / `workflow_run`) — bu depoda o tetikleyiciler yok.

### Önce dalda denendi — `main` her zaman yeşil

Değişiklik doğrudan `main`'e atılmadı. Workflow zaten `branches: ["**"]` ile
her dalda koştuğu için `ci/node24` dalına push edildi, orada **yeşil yandığı
görüldü**, sonra `main`'e alındı.

> **Gerekçe bir değişmez:** *"`main` her zaman yeşildir"* (`SURUMLEME.md`).
> Bir CI değişikliğini doğrudan `main`'e atmak, o kuralı bozma ihtimalini
> bedava kabul etmek demektir — oysa dal denemesi üç komut.

---

## 🔴 T-18 · Denetlenmeyen kural yayın kapısını kapatmıyor

**Bulundu:** 16 Eylül 2026, **dış inceleme** (GPT) · **Yeniden üretildi:** evet

**Ne.** Doğrulayıcıya gövdesi yazılmamış ama **aktif ve SERT** bir kural
verildiğinde cevap aynı anda şunları söylüyor:

```
uygulanmayan_kurallar : ['GECE_VARDIYASI_AZAMI']
sert_ihlal            : 0
YAYINLANABILIR        : True
```

*"Bu kuralı kontrol edemedim"* ile *"yayınlayabilirsin"* **aynı cevapta**.

**Neden bu kadar ciddi.** `09-motor/dogrulayici/denetle.py` içinde, kendi
elimizle yazdığımız cümle şu:

> *"'İhlal bulamadım' ile 'bakmadım' aynı şey değildir. İkisini karıştıran
> bir doğrulayıcı, yeşil yanan ama hiçbir şey sınamayan testten daha
> tehlikelidir — çünkü planı temiz gösterir."*

İlke **yazılmış**, kapıya **bağlanmamış**. `yayin_kapisi()` yalnız `ihlaller`
listesine bakıyor; `uygulanmayan_kurallar` dolu olsa bile umursamıyor.
**O-1'in tam şekli:** koruma tanımlı, etkisiz.

Şu an kataloğun **34** kuralının 19'u yazılı. Kalan 15'i bir kiracıda aktif
edilirse, plan o kurallara **hiç bakılmadan** yayınlanabilir görünür.

**Ürün kararı gerekiyor:** gövdesi olmayan aktif bir kural varken kapı ne
yapmalı? Seçenekler: (a) yayını engelle, (b) `kabul_bekleyen` gibi davran —
yetkili gerekçeyle onaylasın, (c) yalnız SERT olanlarda engelle. Uydurulmadı.

---

## ✅ T-19 · Şartnamedeki talep biçimi sessizce gözden kaçıyordu — **KAPANDI (23 Eylül 2026)**

**Bulundu:** 16 Eylül 2026, **dış inceleme** (GPT) · **Yeniden üretildi:** evet

**Ne.** Şartname §11.2 talebi şöyle tarif ediyor:

```json
"talep": [ { "ekip": "uuid", "gun": 0, "saat": 8, "asgari": 3, "hedef": 5 } ]
```

Motor ise `gunler: []` ve `saatler: []` (çoğul, liste) okuyor. Şartname
biçimindeki girdi verildiğinde:

| Girdi biçimi | Atama | Asgari kapsama | Yayın |
|---|---|---|---|
| Şartnamedeki (`gun`, `saat`) | **0** | **%100** | ✅ yayınlanabilir |
| Motorun beklediği (`gunler`, `saatler`) | 3 | %100 | ✅ yayınlanabilir |

*"Pazartesi 08:00'de üç kişi gerekiyor"* dendi, motor **sıfır kişilik plan**
üretti ve *"%100 kapsama, yayınlanabilir"* dedi.

### Bu, bağımsızlık kuralının sınırını gösteriyor

§7.6 çözücü ile doğrulayıcıyı **kural mantığında** ayırıyor ve bu işe
yarıyor. Ama ikisi de girdiyi **aynı fikstür geleneğiyle** okuyor —
fikstürleri de aynı kişi yazdı. Birbirleriyle tutarlılar, ikisi de
**şartnameyle** tutarsız.

> **Ders:** D-6'ya karşı kurulan bağımsızlık, ortak yanlış bir **girdi
> yorumuna** karşı hiçbir şey yapmıyor. Mantığı iki kez yazmak yetmiyor;
> sözleşmenin kendisinin sınanması gerekiyor.

**Kök sebep aynı aileden:** `kapsama_yuzdeleri()` *"talep yoksa %100 döner"*
diyor ve bunu bilinçli bir karar olarak belgeliyor. Ama **"talep yok"** ile
**"talebi okuyamadım"** ayrımı yok. T-18 ile birebir aynı sınıf.

### Karar (23 Eylül, Mustafa): **şartname kazanır** + okunmayan alan **bildirilir**

Reddedilen seçenek *"tanınmayan girdiyi reddet"*ti. Reddetmek, motorun
tanımadığı **tek bir alan** yüzünden çalışan bir planı yok eder.

| Ne yapıldı | Nerede |
|---|---|
| Talep hücre başına okunuyor (`gun`, `saat`) | `09-motor/cozucu/model.py` · `09-motor/dogrulayici/kurallar.py` · `09-motor/dogrulayici/denetle.py` — **üç ayrı yerde, üç ayrı yazım**; ortak yardımcı modül §7.6 gereği çıkarılamaz |
| Okunmayan girdi alanları raporlanıyor | `09-motor/dogrulayici/denetle.py` → `okunmayan_alanlar` |
| Fikstür kısayolu açılıyor | `08-motor-testleri/v5/fikstur_yukleyici.py` → `talep_hucrelere_ac()` |
| Kırmızı kanıt | `09-motor/testler/test_girdi_sozlesmesi.py` — 5 test, **beşi de kırmızı yandı** |

### Kırmızı kanıt — bulgunun kendisi iki satırda

```
assert c["metrikler"]["asgari_kapsama_yuzde"] == 100.0   -> GEÇTİ
assert len(c["atamalar"]) > 0                            -> KALDI
```

Sıfır atamalı plan, **%100 kapsama**, yayınlanabilir.

### Kayıtta yazan ile ölçülen — üçüncü kez

| | Kayıtta | Ölçülen |
|---|---|---|
| Kaç yer talebi okuyor | 2 (çözücü + doğrulayıcı) | **5** — `denetle.py` de okuyormuş; ayrıca fikstür katmanında 2 |
| Kaç fikstür dönüşecek | 11 | **0 fikstür dosyası** — kısayol yükleyicide açıldı. Ama motorun **kendi** testlerinde 5 yer dönüştü |
| Kaç alan sessiz | 5 | **12** (+ `gecmis_vardiyalar`, T-28) |

T-34 (2 satır → 16 yer), T-35 (kiracı → kurulum çapı), şimdi T-19.
**Bir bulgunun kaydı, bulgunun kendisi değildir.** Kayıt, yazıldığı anda ne
kadar bakıldıysa onu taşır — eksiğini değil.

### Bu turun açtığı dört yeni kayıt

* **T-38** — şartnamenin on iki alanı daha motorda karşılıksız.
* **T-39** — aynı hücreye iki talep satırı gelirse ne olacağı yazılı değil.
* **T-40** — `tercih_karsilama_yuzde` çıktı sözleşmesinde var, motorda yok;
  onu gerektirdiği söylenen **A7 onsuz yeşil**.
* **T-26'ya kanıt** — `08-motor-testleri/v5/fikstur-denetleyici.py`, ortak
  olduğu yazılı modülü hiç kullanmıyormuş; kendi kopyası vardı. Aşağıda.

### Hâlâ açık olan

`okunmayan_alanlar` bugün **yalnız rapor**. Yayın kapısı ona bakmıyor —
`uygulanmayan_kurallar` ve `eksik_boyutlar`'a da bakmıyor. **Üçü de kapıyı
geçiyor.** Bu **T-18**'dir, ve T-18'in cevabı artık bir değil **üç** kanalı
bağlıyor.

---

## 🟡 T-20 · M0 testinin kapsamı, anlatılan güvenceden dar olabilir

**Bulundu:** 16 Eylül 2026, dış inceleme (GPT) · **Doğrulanmadı** — kod
incelemesi bulgusu, veritabanında denenmedi

**İddia.** `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` testi, uygulamanın
kullandığı bağlantıyı almak yerine **kendi sabit bağlantısını** kuruyor.
Doğruysa test kendi bağlantısının yetkisini ölçüyor demektir; uygulamanın
bağlantı ayarı değiştiğinde bunu M0'ın tek başına yakalayacağı söylenemez.

**Neden önemli.** M0, **A-1'i kapatan test.** O-1 (projenin en ciddi hatası)
tekrar etmesin diye 12 Eylül'de eklendi. Kapsamı sanıldığından darsa, A-1
düşündüğümüz kadar kapalı değil.

**Ne gerek:** testi okumak ve deneyerek doğrulamak. Doğruysa test,
uygulamanın **gerçekten kullandığı** bağlantı dizesini alacak şekilde
düzeltilmeli.

---

## 🔴 T-21 · Çok ekipli çalışan iki ekibi aynı anda dolduruyor

**Bulundu:** 16 Eylül 2026, dış inceleme · **Yeniden üretildi:** evet

**Ne.** Model `x[calisan, gun, sablon]` tutuyor — **ekip boyutu yok.** Bir
çalışan birden çok ekibe bağlıysa, aynı vardiya değişkeni **her ekibin**
kapsama toplamına giriyor. Çıktı hazırlanırken ise kişi yalnızca listesindeki
**ilk** ekibe yazılıyor.

Tek kişi, iki ekip, aynı saat, her ekip 1 kişi istiyor:

```
durum          : cozuldu     <- motorun kendi modeli "oldu" diyor
atama sayisi   : 1
atamalar       : [('C1', 'E1', 0)]
asgari_kapsama : 50.0        <- gercekte yarisi bos
```

**Neden ciddi.** Bu bir raporlama hatası değil, **modelin kendi inancı yanlış.**
Motor bir kişinin aynı anda iki yerde olabileceğini varsayıyor. Sonuçları:

- Gerçekte eksik kadrolu bir planı SERT kısıt açısından geçerli sayabilir
- Bağımsız doğrulayıcı açığı yakalar (yakaladı), ama bu sefer de **gerçekte
  mümkün olan** bir plan gereksiz yere onarıma ya da çözümsüzlüğe gidebilir
- Otel/çağrı merkezi gibi çok ekipli operasyonlarda kural değil **istisna**
  değil, olağan durum

**Ürün kararı gerekiyor:** bir çalışan bir vardiyada **tek bir ekibe** mi
sayılır (o zaman değişken `x[calisan, gun, sablon, ekip]` olur), yoksa ekipler
iç içe geçebilir mi? Şartname §8'de `ekipler` çoğul; anlamı tanımlı değil.

---

## ✅ T-22 · Çözümsüzlükte sunulan plan denetlenmiyordu — **KAPANDI (23 Eylül 2026)**

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Kapandı:** 23 Eylül

`orkestra.py`, çözücü `cozumsuz` dediğinde **erken dönüyor** ve bağımsız
doğrulayıcıyı hiç çağırmıyordu. Oysa `en_iyi_plan`ın kendi notu şunu diyordu:

> *"K-10: bu bir TASLAKTIR… İçindeki her ihlal bağımsız doğrulayıcıdan
> geçirilmeli."*

Geçiren yoktu. **En çok açıklama gereken plan, en az denetlenen plandı** —
yönetici K-10 uyarınca bu taslağı *gerekçeyle* onaylıyor ve neyi onayladığını
göremiyordu.

### Kabul cümlesi üç şart içeriyordu

| Şart | Nasıl karşılandı |
|---|---|
| Taslak `degerlendir()`'den geçsin | `orkestra._taslagi_denetle()` — erken dönüş artık buradan geçiyor |
| Denetim **özgün** girdiyle yapılsın | `girdi` kullanılıyor, gevşetilmiş kopya değil |
| Sıfır atamalı plan `var: False` desin | İki üretici yerde de düzeltildi: `teshis._en_iyi_plan` ve `orkestra._cozumsuz` |

**İkinci şart sessiz tuzak.** `en_iyi_plan` üretilirken `ASGARI_KAPSAMA` gibi
kurallar **bilerek gevşetilir**. Denetim o gevşetilmiş girdiyle yapılsaydı
doğrulayıcı gevşetilen kuralı hiç görmez, taslak tertemiz görünürdü — denetim
eklenmiş ama işe yaramaz olurdu. `test_taslak_denetimi_OZGUN_girdiyle_yapilir`
tam bunun bekçisi.

### Kalıcı bekçi

`09-motor/testler/test_profiller.py` içinde **4 test**: denetimin varlığı,
özgün girdiyle yapılması, boş planın `var: False` demesi, dolu planın `var:
True` demeye devam etmesi (gerileme koruması — düzeltme *"hep False de"* diye
yapılamaz).

**Kırmızı kanıt:** düzeltmeden önce 3 kırmızı / 1 yeşil (yeşil olan gerileme
koruması). Sonrasında 4/4. **72 birim testi** · **7 altın senaryo** ·
fikstür denetleyicisi 0.

### ⚠ Düzeltme bir şeyi görünür kıldı — A03

A03 (*"İmkânsız durum ve yöneticinin kararı"*) tam bu yoldan geçiyor. Artık
denetim raporu geliyor ve **şunu söylüyor:**

```
uygulanmayan_kurallar : ['YETKINLIK_KAPSAMASI']
sert_ihlal            : 0
yayinlanabilir        : true
```

`YETKINLIK_KAPSAMASI` A03'ün girdisinde **aktif ve SERT**; gövdesi
doğrulayıcıda **yok**. Yani aynı cevapta *"bu SERT kuralı kontrol edemedim"*
ve *"yayınlanabilir"* yazıyor — üstelik A03'ün **tamamı** o kural
sağlanamadığı için çözümsüz.

> **Bu T-18'dir ve kanıtı güçlendi.** Daha önce kurulmuş bir girdiyle
> gösteriliyordu; artık **onaylanmış bir altın senaryoda** görünüyor.
> T-22 düzeltmesi hatayı üretmedi — **görünmez olmaktan çıkardı.** Denetim
> hiç koşmadığı için kimse bu çelişkiyi göremiyordu.

T-18 hâlâ açık: kapının bilinmeyen kuralda ne yapacağı **ürün kararı**.

---

## ✅ T-23 · ~~"Süre yetmedi" ile "imkânsız" aynı cevabı alıyor~~ — **KAPANDI (29 Eylül, K-37)**

**Bulundu:** 16 Eylül 2026, dış inceleme · **Kod okumasıyla kesin**,
deneyle üretilemedi (iki denemede de CP-SAT gerçekten çözümsüzlüğü kanıtladı)

**Ne.** `coz.py` yalnız `OPTIMAL` ve `FEASIBLE` durumlarını "çözüldü" sayıyor;
geri kalan **her şey** — `INFEASIBLE` de, süre dolduğu için çözüm bulunamayan
`UNKNOWN` de — aynı `teshis_koy()` çağrısına gidiyor. O da `"durum":
"cozumsuz"` sabitliyor.

**Operasyon açısından fark büyük:**

| Gerçek durum | Yöneticinin yapması gereken |
|---|---|
| Bu kadroyla imkânsız | Personel al ya da kuralı gevşet |
| Verilen sürede bulamadım | **Süreyi uzat, tekrar dene** |

Yanlış açıklama, yöneticiyi gereksiz personel alımına ya da kural
değiştirmeye yönlendirebilir.

**Not:** bilgi aslında çıktıda **var** — `cozum_istatistikleri.durma_sebebi`
`butce_doldu` diyebiliyor. Ama `durum` alanı `cozumsuz` diyor ve ekranda
okunacak olan o.

### ✅ Kapanış — 29 Eylül, K-37

Mustafa'nın kararı: iki durum **iki ayrı cevap** alır.

| CP-SAT | `durum` | teşhis koşar mı | yöneticinin gördüğü |
|---|---|---|---|
| `INFEASIBLE` | `cozumsuz` | evet, `teshis_kesin` **True** | *"böyle bir plan yok"* |
| `UNKNOWN` | `sure_yetmedi` | **hayır** | *"süreyi uzat"* + **"neden olduğunu araştır"** düğmesi |

Teşhis artık yalnız **istenirse** koşuyor (`teshis_iste`) ve o yolda
`teshis_kesin` **False** — cümlenin kanıtlanmadığı çıktının kendisinde yazılı.

⚠ **Ekran tarafı yazılmadı.** Plan editörü henüz hiç yok; K-37 motorun çıktı
sözleşmesini ve düğmenin davranışını tanımlıyor.

Bekçisi altı test: `09-motor/testler/test_sure_yetmedi.py`. Asıl kazancı
ölçen `test_sure_yetmedigi_zaman_TESHIS_KOSMAZ`.

→ K-37 · T-48 (aynı bulgunun ölçülmüş hâli) · T-59

---

## 🟡 T-24 · K-28'in ikinci durma koşulu yazılmadı; süre bütçesi istek bütçesi değil

**Bulundu:** 16 Eylül 2026, dış inceleme · **İkisi de doğrulandı**

### 24a — durgunluk koşulu kodda yok

K-28 iki koşul verdi: *"optimuma %2'den yakın"* **veya** *"2 dakikadır
iyileşmiyor"*. `coz.py` `durgunluk_saniye: 120` tanımlıyor, `son_iyilesme`
alanını her çözümde güncelliyor — ama **hiçbir yerde karşılaştırmıyor.**
İkinci koşul **hiç uygulanmadı.**

Üstelik yapısal bir engel de var: geri çağrı yalnız **yeni çözüm
bulununca** tetikleniyor. İyileşme olmadığında zaten çağrılmıyor, dolayısıyla
durgunluğu o noktadan ölçmek mümkün değil.

> Bu, kayda geçmiş ama yürürlüğe girmemiş bir karar. Ürün kararları sicili
> "K-28 kapandı" diyor; `coz.py`'nin başındaki açıklama *"iki koşuldan biri
> olunca biter"* diyor. İkincisi yok. Bkz. **T-26**.

### 24b — `azami_saniye` bir istek bütçesi değil

Ölçüldü:

```
butce 0.05 saniye  ->  cagri 57.4 saniye surdu
```

**Bin kat aşım.** `azami_saniye` tek bir `Solve()` çağrısına uygulanıyor.
Çözüm bulunamayınca teşhis devreye giriyor ve **kendi süresini** harcıyor:
her SERT kural için ayrı bir çözüm denemesi (10'ar saniye) + `en_iyi_plan`
(30 saniye). Onarım döngüsü de `coz()`'u üç kez çağırabiliyor.

Yani §11.2'deki *"süre bütçesi (varsayılan 15 dk)"* ifadesi **isteğin
tamamını kapsamıyor** ve kullanıcıya verilen süre sözü tutulmuyor.

**Ne gerek:** tek bir istek bütçesi ve onu paylaşan bir sayaç — çözücü,
onarım ve teşhis aynı bütçeden harcamalı.

---

## 🟡 T-25 · Servis tek iş parçacıklı: plan üretimi editörü bekletir

**Bulundu:** 16 Eylül 2026, dış inceleme · **Kod okumasıyla kesin**,
bekleme süresi ölçülmedi

**Ne.** `servis.py` `HTTPServer` kullanıyor — istekleri **sırayla** işler.
Plan üretimi isteğin içinde tamamlanıyor. O sırada aynı servise gelen
`/evaluate` ve `/health` **bekler**.

Şartnamenin akışı *"plan üretimi uzun sürebilir"* diyor ve editörün ayrı
çalışmasını varsayıyor. Mevcut kurulum bunu karşılamıyor.

**Şu an neden acil değil:** tek kiracı, tek kullanıcı, pilot öncesi.
`servis.py`'nin kendi açıklaması zaten *"yük altında koşacak sürüm için
ASGI'ye taşınabilir; sözleşme değişmez"* diyor. Ama `/health`'in de
bloklanması CI ve izleme açısından ayrı bir sorun.

**En küçük adım:** `ThreadingHTTPServer`. Tek satır, sözleşme değişmez.

---

## ✅ T-27 · Olmayan mola yasal sınırı deviriyordu — **KAPANDI (16 Eylül 2026)**

**Bulundu:** 16 Eylül, dış inceleme (3. tur) · **Yeniden üretildi:** evet ·
**Kapandı:** aynı gün

`zaman.mola_araliklari()` molayı, vardiyanın **içinde olup olmadığına
bakmadan** döndürüyordu; `mola_saat()` hepsini topluyor, `net_saat = brüt −
mola` bunu düşüyordu.

```
vardiya 08:00-20:00, mola 22:00-23:00 (vardiyanin DISINDA)
ESKI : brut 12 · mola 1 · net 11 · GUNLUK_AZAMI (11 saat) ihlali: 0
YENI : brut 12 · mola 0 · net 12 · GUNLUK_AZAMI ihlali: 1
```

**12 saat çalışıldı, hiç yaşanmamış bir mola sayesinde 11 görünüyordu.**
`GUNLUK_AZAMI` sınıflandırmamızda `yasal: true, kabul_edilebilir: false` —
K-20'ye göre ihlali **hiçbir koşulda kabul edilemeyen** kategori. Hata yönü
tek taraflı ve yanlış tarafaydı: **bozuk girdi motoru daha gevşek yapıyordu.**

### Kabul cümlesi üç şart içeriyordu, üçü de yazıldı

| Şart | Nasıl karşılandı |
|---|---|
| Vardiya **dışındaki** mola sayılmaz | Aralık vardiyayla kesiştiriliyor (kırpma) |
| Vardiyadan **uzun** mola sayılmaz | Aynı kırpma bunu da çözüyor |
| **Üst üste binen** molalar iki kez sayılmaz | Kırpma bunu çözmüyordu — **birleştirme** eklendi |

> ⚠ **Üçüncü şart ilk turda atlandı.** Kırpma yazıldı, testler yeşil yandı,
> "T-27 kapandı" denecekti. Kabul cümlesi tekrar okununca üçüncü şartın
> yazılmadığı görüldü: 10:00–12:00 ile 11:00–13:00 molaları **dört saat**
> sayılıyordu, üç değil. T-26'nın tam örneği — *kayıt ile yürürlük ayrı
> şeyler.* Bu kez kaydın kendisi yakaladı.

### Kısmen dışarıda kalan mola yarı sayılır

19:30–20:30 molasının 30 dakikası vardiyanın içindedir ve **gerçekten
kullanılmıştır**. "Ya hep ya hiç" uygulaması bunu sıfırlardı; onun da bekçisi
var.

### Gece yarısını aşan vardiya bozulmadı

Vardiya 16:00–01:00 ise mola ham saatle (`00:30`) yazılmış olabilir. Kırpma
öncesi 24 saat ileri **kaydırma** eklendi — yoksa düzeltme, gerçek işleyişin
en yaygın hâlini (182 atama) kırardı. Bekçisi bilerek **düzeltmeden önce**
yazıldı ve o tek test kırmızı kanıt turunda **yeşil** yandı.

### Kapsamı: üretilen planlar değil, içe aktarılanlar

Çözücü molayı zaten vardiya içine zorluyordu (`09-motor/cozucu/model.py`, mola
adaylarında `s >= sablon["bas"] and s + mola <= sablon["bit"]`). Yani hata
**üretilen planlarda** pratikte çıkmıyordu. Riski taşıyan yol: **içe
aktarılan gerçek veri ve elle düzenlenen planlar** — yani plan editörü
yazıldığında tam da bu yol açılacaktı.

### Kalıcı bekçi

`09-motor/testler/test_kurallar.py` içinde **8 test**: aritmetik (3), ürün
sonucu (3 — `GUNLUK_AZAMI` ve `MOLA_HAKKI` gerçekten ateşleniyor mu),
gerileme koruması (2 — gece yarısı ve ayrık molalar).

Aritmetik testleri ile kural testleri **bilerek ayrı**: `net_saat` düzeltilip
kural başka sebeple susarsa aritmetik testi yeşil kalır, kural testi kırmızı
yanar.

**Kırmızı kanıt:** düzeltmeden önce 6 test kırmızı, 2 yeşil (koruma
testleri). Düzeltmeden sonra 8/8 yeşil, toplam **68 birim testi** ve **7
altın senaryo** yeşil, fikstür denetleyicisi 0 döndü.

---

## ✅ T-28 · ~~Geçmiş vardiyalar hiç okunmuyor~~ — **KAPANDI (30 Eylül, K-42)**

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Doğrulandı:** `09-motor/`
altında `gecmis_vardiyalar` **hiçbir dosyada geçmiyor**

Şartname §11.2 geçmiş vardiyaları ayrı bir alanla gönderiyor. Ne çözücü ne
doğrulayıcı okuyor. `VARDIYA_ARASI_DINLENME` yalnız kendisine verilen haftanın
atamalarını karşılaştırıyor.

Pazar gecesi başlayıp pazartesi 07:00'de biten vardiyadan sonra pazartesi
09:00 ataması — **iki saatlik dinlenme** — görünmüyor. Bu da yasal bir kural.

**A11'den farkı:** o *"geçmiş veri eksikse engelle"* işi. Bu ise **veri
gönderilse bile kullanılmıyor**.

**Kabul cümlesi:** *"Geçmiş vardiya sonucu değiştirir."* Aynı pazartesi planı,
önceki pazar vardiyası eklenmeden ve eklenerek değerlendirilmeli; sonuç
değişmeli.


### Ek — 30 Eylül: Mustafa'nın test önerisi ve gerçek verinin söylediği

**Mustafa'nın ürün cümlesi:** *"Realitede geçmiş datayı PDKS vb. sistemlerden
alacağız, plan datası olmayacak."* Şartnamenin lookback biçimi
(`{"gun": -1, "bas": 23, "bit": 31}` — şablonsuz aralık) gerçekleşen veriye
zaten uygun.

**Test önerisi (iki yol):** (A) önce bir hafta planla, sonraki haftayı onu geçmiş
sayarak planla; (B) plana %80–85 uyumlu sahte bir PDKS üret, yeni planı onun
üzerine kur.

**⚠ Gerçek veri (B)'nin varsayımını değiştiriyor** — `07-GERCEK-VERI-BULGULARI.md`
P-1: giriş/çıkış kaydı satırların yalnız **%18'inde** var; 781 çalışanın
**411'inde** hiç kayıt yok; kişi başına dönemin ~**%58'i** kayıtlı. Yani baskın
sorun plandan **sapma** değil, **eksik kayıt**. Sahte PDKS boşluk içermezse
gerçeği temsil etmez.

**⚠ Şartnameyle çarpışma:** §11.2 *"Lookback verisi eksikse motor çalışmaz"*
diyor. Gerçek PDKS'te eksik kayıt **normal durum** — bu kural uygulanırsa motor
çoğu gerçek koşumda durur. Bugün ise tersi oluyor: motor geçmişi hiç okumuyor
ve her koşumda çalışıyor, yani üretilen her plan şartnamenin *"dinlenme ihlalini
sessizce kaçırır"* dediği durum.

**Geçmişin ne açtığı — kesin liste:**

| | kurallar | gereken |
|---|---|---|
| bugün hafta sınırında **kör** olan yazılı kurallar | vardiya arası dinlenme · hafta tatili (kayan pencere) · ardışık çalışma günü · ardışık gece limiti | son 14 gün |
| gövdesi yazılabilecek hale gelenler | gece postası devri (**yasal**) · ardışık hafta sonu limiti | son 14 gün |
| haftalık geçmişle **açılmayanlar** | yıllık fazla mesai tavanı (**yasal**) | yıl içi **toplam** (tek sayı) |
| | plan kararlılığı | **aynı haftanın** yayındaki planı (yeniden planlama) |

⚠ 30 Eylül'de *"dördü T-28'e bağlı"* diye yazılmıştı — yanlış: ikisi ayrı
girdiye bağlı.


### ✅ Kapanış — 30 Eylül

**Ölçülen — Mustafa'nın önerdiği iki aşamalı yolla** (`08-motor-testleri/gercekci-veri-seti/iki-hafta-olc.py`,
%95 seti, 49 kişi): hafta 1 çözüldü, hafta 1'in planı hafta 2'nin geçmişi
oldu, hafta 2 iki kez çözüldü ve ikisi de **geçmişi bilen** denetçiye soruldu.

| hafta 2 | atama | geçmişi bilen denetçiye göre sert ihlal |
|---|---|---|
| geçmişsiz (30 Eylül'e kadarki motor) | 217 | **27** — 10 hafta tatili · 7 vardiya arası dinlenme · 10 ardışık çalışma günü |
| geçmişle | 217 | **0** |

Yani 49 kişilik tek bir haftada 27 **yasal** ihlal vardı ve **hiçbiri görünmüyordu**
— eski denetçi de geçmişe bakmıyordu.

**Ne yapıldı:**

* İki motor yarısı da `gecmis_vardiyalar`'ı okuyor (ayrı ayrı, §7.6).
  Biçim şartnamedeki gibi: şablonsuz aralık, negatif gün — PDKS'e uygun.
* **Beş kural** pazartesi 00:00'da artık kör değil: vardiya arası dinlenme,
  çakışma (pazar gecesi pazartesiye taşıyorsa), hafta tatili, ardışık çalışma
  günü, ardışık gece limiti. Çözücüde geçmiş günler kayan pencerelerde
  **sabit** olarak sayılıyor.
* **Geçmişin kendi ihlali plana yazılmıyor** — geçmiş yeniden planlanamaz.
* **K-42:** kayıtlı aralık çalışıldığını kanıtlar, kaydın yokluğu hiçbir şey
  kanıtlamaz. Bilinmeyen gün kısıt yaratmaz; `gecmis_eksik` kanalı hangi
  kontrolün kimin için yapılamadığını yazar — **yalnız sonucu değiştirebilecek**
  bilinmeyen gün için (gürültü değil; ayrıntısı K-42'de).
* Yeni isteğe bağlı alan: `gecmis_bilinen_gunler` — kaydı tam olan günler.

**32 test, 19'u kırmızı kanıt.** 18 mutasyon, hepsi öldü.

⚠ **İki aşamalı testin ilk hâli hiçbir şey ölçmüyordu.** Çözücü geçmişi **hiç
okumayacak** şekilde bozuldu, test **yine yeşil** kaldı — sahnede boşluk çoktu.
Yerine sabit atamalı bir hafta 1 kondu (C1 cuma-cumartesi-pazar gecesi) ve
hafta 2'de geceyi yalnız C1 çalışabiliyor: geçmiş okunuyorsa plan çözümsüz
kalmak **zorunda**.

⚠ **Gerçek ölçekli iki hafta testi CI'a konmadı** — ilk koşuda zamanlamadan
kırmızı yandı (aynı hafta 144, 178 sn; bekçide 240 sn'ye sığmadı) ve bekçileri
9,5 dakikaya çıkardı. Gerçek ölçek elle koşulan araçta; CI'da küçük,
deterministik sürüm var.

**Açık kalanlar — ayrı işler:**

| | ne gerekiyor |
|---|---|
| gece postası devri (**yasal**) · ardışık hafta sonu limiti | gövdeleri artık yazılabilir |
| yıllık fazla mesai tavanı (**yasal**) | yıl içi **toplam** (tek sayı) — yeni girdi |
| plan kararlılığı | **aynı haftanın** yayındaki planı — yeni girdi |
| adalet devir yükü (`devir_yuk`) | geçmişten hesaplanabilir; bugün elle geliyor |
| sahte PDKS (Mustafa'nın ikinci yolu) | boşluk ve sapma oranları **anonim gerçek veriden ölçülerek** |
| erken saatli gece kaydı | T-69 |

→ K-42 · T-69 · T-70 · `09-motor/testler/test_gecmis_veri.py`
---

## 🔴 T-29 · `DONMUS_GUN` hiç ateşlenemez

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Yeniden üretildi:** evet

```
donmus gune atama (isaretsiz) -> ihlal: 0
ayni atama '_yeni' isaretli   -> ihlal: 1
'_yeni' isaretini ureten kod  : YOK
```

Kural yalnız `_yeni` bayrağı taşıyan atamayı ihlal sayıyor; o bayrağı
**hiçbir şey üretmiyor**. Eski planla yeni planı karşılaştırmak gibi bir şey
de yapmıyor. Çözücü donmuş günleri ayrıca korumuyor.

Katalogda var, dokümanda "yazıldı", **pratikte ölü**. `DONMUS_GUN` ürünün
*"geçmiş yeniden planlanamaz — olan oldu"* sözünün tek bekçisiydi.

**Kabul cümlesi:** *"Donmuş gün değişmez."* Donmuş gündeki atamayı
değiştirmek, silmek ve yeni atama eklemek — üçü de özel bayrak gerektirmeden
yakalanmalı.

---

## 🟡 T-30 · `HAFTA_TATILI` kesintisiz 24 saati ölçmüyor

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Kod bunu zaten itiraf ediyor**

`hafta_tatili()` gün bazında *"çalışıldı/çalışılmadı"* bakıyor; kesintisiz
dinlenme aralığını hesaplamıyor. Fonksiyonun kendi açıklaması:

> *"Basitleştirme — BİLEREK: gün bazında çalışıldı/çalışılmadı bakılır.
> Gerçek 24 saatlik kesintisiz blok hesabı lookback penceresi gerektiriyor."*

**Kod dürüst, doküman değil.** Devir paketi kuralı "yazılanlar" listesinde
koşulsuz sayıyor. Gece vardiyası pazar sabahına taşmışsa, pazarda yeni
vardiya başlamaması pazartesiye kadar 24 saat dinlenildiği anlamına gelmez.

T-28 çözülmeden bu da tam çözülemez — ikisi aynı eksiğe bağlı.

---

## 🟡 T-31 · Adalet penceresi takvim ayında sıfırlanmıyor

**Bulundu:** 16 Eylül, dış inceleme (2. tur)

§6.5 *"pencere takvim ayıdır, ayın 1'inde sıfırlanır"* diyor. `adalet_dengesi`
devir yükünü **haftanın tamamına** ekliyor; haftanın iki aya dağılıp
dağılmadığına bakmıyor. Ayın 1'ini içeren haftada önceki ayın yükü yeni ayın
dağılımını etkiliyor.

Mevcut test devir yükünün **hesaba katılmasını** çiviliyor; **doğru ayda
bırakılmasını** çivilemiyor.

---

## 🟡 T-32 · Fazla mesai tavanını çözücü ve doğrulayıcı farklı yerden okuyor

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **16 Eylül'de bu oturumda
oluşturuldu**

K-30 uygulanırken çözücü `FAZLA_MESAI_PROFIL[profil]` okuyacak şekilde
değiştirildi ve kuralın kendi `azami_saat_hafta` parametresini **tamamen
görmezden gelir** oldu. Doğrulayıcı hâlâ parametreyi okuyor (varsayılan 10).

Kiracı 10 yazıp KAPSAMA profili seçerse: çözücü 15'e kadar izin veriyor,
doğrulayıcı 10'un üstünü reddediyor → gereksiz onarım, gereksiz *"çözümsüz"*.

Bağımsızlık bunu **görünür** kılıyor (faydası bu) ama kullanıcıya yanlış
sonuç gitmeden çözülmeli.

---

## 🟡 T-33 · Zaman hassasiyeti: yarım saatler kayboluyor

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Doğrulandı**

```
_dilimler(0, 8.5, 12.5) -> [8, 9, 10, 11]
```

Çözücü kapsama hesabında saatleri tam sayıya indiriyor; 08:30 ile 08:00
arasındaki fark kayboluyor. Ayrıca doğrulayıcının izin kontrolünde ondalıklı
bitişten üretilen değer tam sayı isteyen gün döngüsüne veriliyor.

Şartname §8.4 `baslangic_saat`/`bitis_saat` alanlarını `numeric` tanımlıyor —
yarım saat **veri modelinde mümkün**, motorda değil.

---

## ✅ T-34 · Sırlar kodda varsayılana düşüyordu — **KAPANDI (23 Eylül 2026)**

**Bulundu:** 16 Eylül, dış inceleme (3. tur) · **Kapandı:** 23 Eylül ·
**Kanıt:** `fix/t34-sirlar` dalı, CI

Ortam değişkeni verilmediğinde uygulama **hata vermiyor, bilinen bir anahtarla
açılıyordu**. `Program.cs`'in kendi yorumu *"Parola koda ve appsettings'e
YAZILMAZ"* diyordu — bir satır altında koda yazılmıştı. K-28 ve T-18 ile aynı
sınıf: **yazılı, yürürlükte değil.**

### Kayıttaki tarif eksikti — gerçek kapsam beş katman

`grep` ile tarandı: aynı sabit **16 yerde** duruyordu.

| Katman | Yer |
|---|---|
| Uygulama kodu | `Program.cs` ×2, `KurulumHizmeti.cs`, `TasarimZamaniFabrika.cs` |
| **Test kodu** | 7 test dosyasında sabit bağlantı dizesi |
| Orkestrasyon | `docker-compose.yml` ×4 (`${VAR:-varsayilan}`) |
| **Veritabanı betiği** | `04-kod/db/rls/02-uygulama-rolu.sql` — rol bu parolayla **yaratılıyordu** |
| CI | Hiç sır vermiyordu, tamamen compose varsayılanlarına dayanıyordu |

> Yalnız C# tarafını düzeltmek **düzeltilmiş görünüp düzeltmemek** olurdu:
> compose aynı bilinen değerleri enjekte etmeye, veritabanı rolü aynı
> parolayla yaratılmaya devam ederdi. T-32'nin aynısı — tek gerçeğin
> birden çok kaynağı.

### Yazılanlar

**`04-kod/backend/src/TShift.Infrastructure/Sirlar.cs`** —
`Sirlar.Zorunlu(ad, enAzUzunluk)`.
Varsayılan yok; sır yoksa **açılmaz** ve hata **değişkenin adını** söyler.
Değerin kendisi asla yazılmaz, yalnız uzunluğu. `JWT_SECRET` için 32 karakter
alt sınırı (`KimlikAyarlari`'nın istediği).

**SQL betiği yer tutucuya geçti** (`{APP_DB_PASSWORD}`), `KurulumHizmeti`
dolduruyor — `{DB_PASSWORD}` için zaten kurulu olan desen. Ayrıca
`ALTER ROLE tshift_app PASSWORD` eklendi: rol zaten varsa yaratma bloğu
atlanıyordu ve **eski parolayla kalıyordu**.

**CI her koşuda `openssl rand` ile üretiyor.** Depoda sır yok, GitHub
secret'ı da gerekmiyor — ve uygulamanın **keyfi bir değerle** çalıştığı da
böylece kanıtlanmış oluyor.

**`.env.example`'a `JWT_SECRET` eklendi.** Daha önce **yoktu**: örneği takip
eden biri imza anahtarsız kalır ve farkında olmadan koddaki sabiti kullanırdı.

**`TEST.ps1` artık `.env`'i okuyor**, eksik değişkende açık hata veriyor.

### Kalıcı bekçi

`04-kod/backend/tests/TShift.Tests/SirTestleri.cs` — **3 test**, kendi
koleksiyonunda (ortam değişkeni süreç geneli; paralellik kapalı).

| | Ne |
|---|---|
| `S1` | `APP_DB_PASSWORD` silinince açılmaz, hata değişkenin adını söyler |
| `S2` | `JWT_SECRET` için aynısı |
| `S3` | **Gerileme koruması** — düzeltme *"her koşulda patla"* diye yapılamaz |

**Kırmızı kanıt CI'da, kalıcı.** `48583e4` (yalnız test): *42 test, 40 geçti,
S1 ve S2 kırmızı — "No exception was thrown"*. `3ec5d42` (düzeltme):
**o günkü 42 testin tamamı yeşil.**

### ⚠ M5 bu ailenin tek üyesini koruyordu ve yeşil yanıyordu

`M5 - appsettings icinde gercek parola yok` doğruydu — parola `appsettings`'te
değil, **başka beş yerdeydi**. Kapı vardı; başka bir kapıydı. O-1 (RLS
tanımlıydı ama etkisizdi) ve O-9 (git temizdi ama yanlış şeye bakıyordu) ile
aynı sınıf: *kontrolün yokluğu değil, kontrolün yanlış şeye bakması.*

### Açık kalan — Mustafa'nın işi

`.env`'deki değerler herkese açık bir depoda aylardır duruyordu; **artık sır
değiller.** Üçünün de değiştirilmesi ve `TSHIFT_KURULUM=true` ile bir kurulum
koşusuyla veritabanı rolünün yeni parolaya senkronlanması gerekiyor.

---

## ✅ T-35 · Kurulum çapında kilitlenme — **KAPANDI (23 Eylül 2026)**

**Bulundu:** 16 Eylül, dış inceleme (3. tur) · **Kapandı:** 23 Eylül

### Kayıt olduğundan küçük yazmıştı — iki yerde

**Etki.** Kayıt *"bütün kiracıyı kilitliyor"* diyordu. Ölçüldü: `KilitliMi`
sorgusunda **kiracı filtresi yok** ve olmaması bilinçli (M-13). Gerçek etki
**kurulum çapında**:

> Herhangi bir kiracıda, herhangi biri, 15 dakikada 5 kez yanlış parola
> girerse — **kurulumdaki herkes** 15 dakika giriş yapamaz.

**Kapsam.** Kayıt yalnız `04-kod/frontend/src/app/api/giris/route.ts`'i anıyordu. `grep`: API'ye **beş
yerden** gidiliyor — `giris`, `yenile`, `cikis`, `calisan` ve `04-kod/frontend/src/lib/api.ts`
içindeki `apiGet()` (bütün sunucu tarafı GET'ler; denetim kaydındaki IP
oradan). *(`proxy.ts` ara katmanı kontrol edildi — API'ye gitmiyor, çağrı
yeri değil.)*

### Kural doğruydu, gördüğü IP yanlıştı

Şartname (§ satır 1403): *"aynı e-posta **veya IP** için 5 başarısız denemede
15 dakika kilit."* Kod bunu doğru uygulamış. Kusur: tarayıcı API'ye doğrudan
gitmediği için `ctx.Connection.RemoteIpAddress` **her zaman ön yüzün adresi**.

### ⚠ "Mekanik" etiketi yanlıştı

Bu madde *"karar gerektirmiyor"* diye kaydedilmişti. **Değildi.**
`X-Forwarded-For` istemcinin yazdığı bir başlıktır; körlemesine güvenmek
saldırganın kendini istediği IP gibi göstermesine izin verir — hem kilitten
kaçar hem denetim kaydını kirletir. Güvenilen vekil listesi **şart**, o liste
de barındırmaya bağlı ve barındırma ertelenmiş. Karar Mustafa'ya soruldu:
*gerçek IP + yapılandırılabilir vekil listesi.*

### Yazılanlar

| Taraf | Ne |
|---|---|
| API | `UseForwardedHeaders`, `TSHIFT_GUVENILEN_VEKILLER`'den okunan `KnownProxies`/`KnownIPNetworks`, `ForwardLimit = 1` |
| Ön yüz | `04-kod/frontend/src/lib/api.ts` → `istemciBasliklari()`; **beş çağrı yeri de** kullanıyor |
| Compose | Sabit alt ağ (`172.28.9.0/24`), web kutusuna sabit adres, `TSHIFT_GUVENILEN_VEKILLER` = **yalnız o adres** |
| `.env.example` | Değişken belgelendi (sır değil, topoloji bilgisi) |

**Liste boşsa başlık hiç okunmaz.** Güvenli varsayılan bilerek seçildi: yanlış
yapılandırma *"herkese güven"* değil, *"kimseye güvenme"* tarafına düşsün.

### Kalıcı bekçi

`04-kod/backend/tests/TShift.Tests/IstemciIpTestleri.cs` — **3 test**:

| | Ne |
|---|---|
| `IP1` | Güvenilen vekilden gelen gerçek IP kaydedilir |
| `IP2` | **Güvenilmeyen kaynaktan gelen başlık yok sayılır** — sessiz tuzak bu |
| `IP3` | Başlık yoksa istek yine de kayda geçer (gerileme koruması) |

### Kırmızı kanıt ve ölçümler

| Aşama | Sonuç |
|---|---|
| Yalnız test | `IP1` kırmızı — `Expected: "203.0.113.9", Actual: null` |
| Düzeltme, 1. deneme | Derleme hatası: `IPNetwork` iki ad alanında birden |
| Düzeltme, 2. deneme | **45/45 yeşil**, uyarı yok |
| Ön yüz | `next build` temiz |
| **Uçtan uca (elle), 1. tur** | Next'e `198.51.100.7` → `login_attempts.ip` aynısı ✅ |
| **Sahte başlık (elle), 1. tur** | Host'tan API'ye `203.0.113.99` → **kaydedildi ❌ koruma çalışmıyor** |
| Yapılandırma düzeltildi | Aralık → tek adres |
| **Uçtan uca (elle), 2. tur** | Next'e `198.51.100.8` → aynısı ✅ |
| **Sahte başlık (elle), 2. tur** | Host'tan `203.0.113.55` → `::ffff:172.28.9.1` yazıldı, **başlık yok sayıldı** ✅ |

### ⚠ İlk yapılandırma yanlıştı ve testler yakalayamazdı

Güvenilen vekil olarak `172.16.0.0/12` konmuştu ve yanına şu yorum
yazılmıştı: *"host'tan atılan bir istek bu aralığa girmez."* **Ölçüldü,
yanlıştı:**

```
host -> yayinlanmis port -> api   =>  ::ffff:172.18.0.1   (docker AG GECIDI)
web kutusu                        =>  172.18.0.4
```

İkisi de `/12` içinde. Yani aralık ağ geçidini — dolayısıyla host'taki her
şeyi — güvenilir sayıyordu ve **sahte başlık geçiyordu.**

`IP2` testi bunu yakalayamazdı: test doğru şeyi sınıyor ve doğru çalışıyor.
Yanlış olan **kod değil yapılandırma**, ve yapılandırma yalnız gerçek
kurulumda görünüyor. Otopsisi **O-11**.

> **Topoloji değişirse bu iki ölçüm yeniden koşturulur.** Birim testi
> mantığı doğrular, topolojiyi doğrulayamaz.

### ⚠ Ön yüz tarafının otomatik testi YOK

`IP1`–`IP3` API'ye doğrudan gidiyor; ön yüzden geçmiyor. Beş çağrı yerinin
başlığı ilettiği **elle doğrulandı** (yukarıdaki uçtan uca ölçüm) ama bir
gerileme bekçisi yok. Next.js route handler test altyapısı kurulmadı —
T-35'ten büyük bir iş olduğu için bilerek ertelendi.

### Test sunucusuna dair bir not — sınır ince

`WebApplicationFactory` içinde gerçek soket olmadığı için
`Connection.RemoteIpAddress` **null** geliyor ve `UseForwardedHeaders`
güvenilen vekil listesini tam o adresle karşılaştırıyor. `TestUygulamasi`'na
bir başlangıç filtresi eklendi: boş adresi loopback'e dolduruyor.

> **Yapılan:** testin *ortamını* gerçeğe benzetmek. **Yapılmayan:** bir
> iddiayı gevşetmek. `IP1`/`IP2`/`IP3`'ün iddiaları aynen duruyor.
> Bu ayrım `02-DEGISMEZLER.md` §6'daki *"kırılan test iddiayı zayıflatarak
> düzeltilmez"* kuralının sınırında; o yüzden kayda geçiyor.

---

## 🟡 T-36 · Eşzamanlı oturum yenilemesi için koruma yok *(`04-kod`)*

**Bulundu:** 16 Eylül, dış inceleme (2. tur) · **Kod okumasıyla doğrulandı**,
eşzamanlı deney yapılmadı

`KimlikServisi.YenileAsync` oku → kontrol et → işaretle → kaydet yapıyor.
Dosyada `RowVersion`, `BeginTransaction`, `Serializable` — **hiçbiri yok**.

İki sekme aynı anda yenilerse iki sonuç mümkün: ya iki geçerli jeton üretilir,
ya da meşru tekrar **hırsızlık sayılıp bütün oturumlar kapatılır**
(`TumOturumlariKapatAsync`). İkincisi kullanıcıyı sebepsiz dışarı atar.

Mevcut testler işlemleri **sırayla** yapıyor; bu yolu sınamıyor.

---

## 🔴 T-38 · Şartnamenin on iki alanı daha motorda karşılıksız

**Bulundu:** 23 Eylül 2026, T-19 kapatılırken · **Ölçüldü:** evet — her ad
`09-motor/` içinde tek tek arandı

**Ne.** T-19 tek bir alanın sessizce atlanmasıydı. Kapatırken §11.2'nin
**bütün** alanları tarandı. `talep` yalnızca ilk örnekmiş.

| Alan | Gönderilirse ne olur |
|---|---|
| `calisanlar[].kural_degerleri` | **§5.2'nin `C` kademesi motorda hiç çözülmüyor.** Çözücü de doğrulayıcı da düz `kurallar[]` listesinden okuyor. ⚠ **Bu satır 23 Eylül'de yanlış yazılmıştı** — bkz. aşağıdaki düzeltme |
| `calisanlar[].izinler[].tum_gun` | ✅ **Kapsam kararı verildi (K-31, 25 Eylül):** yarım günlük izin motora **gönderilmez**, elle yönetilir. Alan yine de gelirse motor bütün günü kapatır — ve `okunmayan_alanlar` bunu bildirir. Kanal burada **bekçi** görevi görüyor |
| `calisanlar[].tercihler` | Tercih plana hiç etki etmez; ekran topluyorsa boşuna topluyor |
| `devir_kapsama` | Devreden kapsama yükü yok sayılır |
| `vardiya_sablonlari[].mola_tek_blok` | Mola bölünebilir; şablonun *"tek blok"* şartı uygulanmaz |
| ~~`vardiya_sablonlari[].mola_en_erken` · `.mola_en_gec_bitis`~~ | ✅ **ÇÖZÜLDÜ (25 Eylül, K-32).** Düzeltilmedi, **kaldırıldı**: mutlak saatli pencere şablona bağlıydı ve 12:00'de başlayan vardiyada kendi kendini patlatıyordu. Yerine `MOLA_YERLESIMI` — vardiyaya göre göreli, firma parametresi |
| `sabit_atamalar[].bas` · `.bit` · `.ekip` | Motor sabit atamayı `sablon` kimliğinden eşliyor; §11.2 örneğinde `sablon` **yok**. Eşleşmeyen satır `uygulanmayan_notlar`a düşüyor — sessiz değil; ama gönderilen `bas`/`bit` şablonunkinden **farklıysa** kimse görmez |
| `istek_id` | Motor okumuyor **ve çıktıya geri yazmıyor**; §11.3 yazdığını söylüyor |
| `sure_butcesi_sn` | **Çağıranın süre bütçesi yok sayılıyor.** Motor süreyi `_cozucu_ayari`'ndan alıyor |

`calisanlar[].gecmis_vardiyalar` de bu ailenin üyesi ama ayrı numarası var:
**T-28**, öncelik 1.

### Artık sessiz değil

`09-motor/dogrulayici/denetle.py` → `okunmayan_alanlar` bunların hepsini
**her istekte** sayıyor. Liste bir **borç defteri**: uzun olması bilgidir,
gürültü değil, ve her madde uygulandıkça kısalır.

Kanal tanımadığı **her** adı bildiriyor, yalnız bilinen listeyi değil —
`ekpiler` gibi bir yazım hatası da bu kanaldan görünüyor.

### ⚠ Mekanizmanın kendi ilk sürümü iki yanlış alarm üretti

`yetkinlikler` ve `operasyonel_rol`'ü *"okunmuyor"* diye bildirdi. Oysa
`09-motor/cozucu/model.py` `_yetkinlik()` içinde ikisini de okuyor. Listeyi yazarken
kendi koyduğum kurala — *"önce okuyan satırı bul, sonra adı listeye ekle"* —
iki adda uymadım; tek tek `grep` ile yakalandı.

> **O-7 tam da budur:** yanlış alarm üreten bir uyarı, bir süre sonra
> okunmayan bir uyarıdır. Sessizliğe karşı kurulan mekanizmanın ilk hatası
> gürültü olmak oldu.

Listenin kendisi hâlâ **elle bakımlı** ve bir adın gerçekten okunup
okunmadığını tam doğrulayan otomatik kontrol yok — metin araması kap
bağlamını ayırt edemiyor. Bu bilinen sınır, kaydı burada.

### Yan bulgu — tek taraflı kural

`YETKINLIK_KAPSAMASI` ve `ROL_KAPSAMASI` **yalnız çözücüde** var;
doğrulayıcıda gövdeleri yok. Çözücü bunları sert kısıt olarak sağlıyor ama
bağımsız denetleyen yok. Sessiz değil — `uygulanmayan_kurallar` bildiriyor;
kapının ne yapacağı **T-18**.

### ⚠ Düzeltme (25 Eylül) — bu kaydın kendi gerekçesi yanlıştı

23 Eylül'de `kural_degerleri` satırına *"sözleşmesi günde 9 saat diyen kişi
genel kuralın 11 saatine planlanabilir — yasal tarafta yanlış plan"*
yazmıştım. **Şartname okunmadan yazılmıştı ve yanlıştı.**

§5.2 ve §6.1 birlikte okunduğunda:

| İddia | Gerçek |
|---|---|
| Kişiye özel günlük sınır `kural_degerleri` ile verilir | `GUNLUK_AZAMI` **kapsamı `S`** — hiçbir kademede ezilemez (K-18). O satır zaten olmamalı |
| Yasal tarafta yanlış plan üretiyor | Üretmiyor. 16 Eylül'de bunun yolu `SAGLIK_KISITI` idi; **25 Eylül'de o kural da kaldırıldı** (K-21 geri alındı) — ürün kalıcı süre kısıtını hiç ifade etmiyor |

**Gerçek etki neyse o:** §5.2'nin `C` kademesi hiç çözülmüyor. Bu kademeye
açık **iki** kural kaldı — `PART_TIME_LIMIT` (Z,C) ve `UYGUNLUK_TAKVIMI`
(K,C). Motor `UYGUNLUK_TAKVIMI`'nin **verisini** kişi başına okuyor;
`PART_TIME_LIMIT`'in `Z` kademesini sözleşme tipinden okuyor ama `C`
kademesini okumuyor. Üçüncüsü `SAGLIK_KISITI` idi, 25 Eylül'de kaldırıldı.

**`izinler[].tum_gun` de aynı gün kapsam kararına bağlandı** (K-31): yarım
günlük izin motora gönderilmeyecek, plan editörüyle yönetilecek. Gerekçe:
yarım günlük izin plan yapılırken **bilinemez** — aynı gün ya da bir gün önce
doğar, plan çoktan yayınlanmıştır.

### ⚠ Seviye önerisi — Mustafa'nın onayını bekliyor

T-38 öncelik listesinde **2. sırada ve 🔴**. Bu, iki satırın ağırlığından
geliyordu: `kural_degerleri` ve `tum_gun`. **25 Eylül'de ikisi de kapsam
kararına bağlandı** — biri kural kaldırılarak (K-21 geri alındı), biri elle
yönetime bırakılarak (K-31).

Kalan satırlar: `tercihler`, `devir_kapsama`, `mola_tek_blok`,
`mola_en_erken`/`mola_en_gec_bitis` (ad uyuşmazlığı),
`sabit_atamalar[].bas`/`.bit`/`.ekip`, `istek_id`, `sure_butcesi_sn`.

**Hiçbiri yasadışı ya da sessizce yanlış bir plan üretmiyor** — yazılmamış
özellikler ve ad uyuşmazlıkları. Ölçüme göre **T-38 artık 🟡**.

Tek taraflı düşürmedim: seviye kararı Mustafa'da. Onaylanana kadar listede
🔴 olarak duruyor ve bu satır **neden şüpheli olduğunu** söylüyor.

> **Dördüncü kez, ama ilk kez ters yönde.** T-34, T-35 ve T-19'un kayıtları
> gerçeği **eksik** söylüyordu; bu kayıt **fazla** söyledi. Ders *"hafife
> alıyorum"* değil: **ölçmeden yazıyorum**, ve bu iki yöne de sapıyor.
> Kaydı yazan da düzelten de aynı taraf — dış inceleme değil.

⚠ **Bu düzeltme T-38'in 🔴 seviyesini tartışmaya açıyor.** Öncelik
listesinde 2. sırada duruyor ve gerekçesi buydu. Kalan en ağır satır
`izinler[].tum_gun` (yarım gün izin tam gün gibi engelliyor) — yanlış plan
üretiyor ama **kısıtlayıcı** yönde, yasadışı yönde değil. **Seviye kararı
Mustafa'da**; ölçüm değişti diye sırayı tek taraflı değiştirmedim.

**Ne gerek:** on iki satır, on iki ürün kararı. Hepsi aynı anda gerekmiyor.

---

## 🟡 T-39 · Aynı hücreye iki talep satırı gelirse ne olacağı yazılı değil

**Bulundu:** 23 Eylül 2026, T-19 uygulanırken · **Ölçülmedi** — bugün
oluşamıyor, ileride oluşabilir

**Ne.** Talep artık hücre başına bir satır (§11.2). Şartname satırların
**benzersiz** olduğunu hiçbir yerde söylemiyor. Aynı `(ekip, gün, saat)` için
iki satır gelirse bugün olan:

* hücre kapsama paydasında **iki kez** sayılır → yüzde bozulur;
* iki ayrı ihlal yazılır → aynı olay iki kez raporlanır (V-1'in başka bir
  yerde yasakladığı şeyin aynısı);
* hangi `asgari` geçerli — büyüğü mü, sonuncusu mu — **tanımsız**.

**Neden bugün görünmüyor.** Fikstür kısayolu kartezyen çarpım ürettiği için
yinelenen hücre çıkmıyor; ürünün talep ekranı ise henüz yok.

**Neden şimdi yazıldı.** Talep ekranı yazıldığında bu karar **verilmiş
olmalı**, sonra değil. Seçenekler: (a) benzersizlik şartname kuralı olsun,
girişte engellensin; (b) motor birleştirsin — en büyük `asgari` kazansın;
(c) yinelenen satır ayrı bir kanaldan bildirilsin. Uydurulmadı.

**Kapı şartı:** talep ekranı yazılmadan önce karara bağlanacak.

---

## 🟡 T-40 · `tercih_karsilama_yuzde` çıktıda yazılı, motorda yok — A7 onsuz yeşil

**Bulundu:** 23 Eylül 2026, §11.3 okunurken · **Ölçüldü:** evet

**Ne.** Şartname §11.3 çıktı metriklerinde `tercih_karsilama_yuzde` var ve
gerekçesi şöyle yazılmış:

> *"**A7** altın senaryosu iki plan profilini karşılaştırıyor; bu metrik
> olmadan 'CALISAN profili gerçekten çalışan lehine mi' sorusu ölçülemiyor."*

Ölçülen:

| | |
|---|---|
| Motorda `tercih_karsilama_yuzde` | **hiçbir satırda yok** |
| A07 fikstüründe | **beklenmiyor** |
| A07 | **yeşil** |

A07 aynı soruyu başka bir ölçüyle cevaplıyor: `adalet_sapmasi_cumartesi` +
`hedef_kapsama_yuzde`. Yani metrik **yetim**: sözleşmede duruyor, üretilmiyor,
ve onu gerektirdiği söylenen test onsuz kurulmuş.

**İki ayrı zarar:**

1. §11.3'ü okuyup arayüz yazan biri bu alanı bekler, bulamaz.
2. *"CALISAN profili çalışan lehine mi"* sorusu bugün **tek boyuttan**
   cevaplanıyor (cumartesi adaleti). Tercih karşılama hiç ölçülmüyor — zaten
   `calisanlar[].tercihler` de okunmuyor (**T-38**). İkisi aynı boşluğun iki
   ucu.

**Ne gerek:** ya metrik yazılacak (önce `tercihler` okunacak — T-38), ya
§11.3'ten çıkarılacak. Üçüncü seçenek yok: sözleşmede durup üretilmemesi
T-19'un çıktı tarafındaki hâli.

---

## 🟡 T-41 · `DENETIM.py` uyarılarının 13'ü kalıcı; düzeltilemeyenle iş düşen aynı listede

**Bulundu:** 23 Eylül 2026, T-19 commit'i öncesi · **Ölçüldü:** evet

**Ne.** 23 Eylül koşusu: **0 HATA, 14 UYARI.** Uyarı bloğunun başlığı
*"bakılmalı, ama devri durdurmaz"*. Ama 14'ün **13'ü bakılamaz**:

| Kaynak | Adet | Neden düzeltilemez |
|---|---|---|
| Test adı uyuşmazlığı | 5 | Hepsi `oturumlar/` ve `DEGISIM-GUNLUGU.md` içinde |
| Bulunamayan yol | 8 | Aynı iki yer |
| **Gerçekten iş düşen** | **1** | *"Commit bekleyen 19 dosya"* |

Bu dosyalar `00-BURADAN-BASLA.md` #5b gereği **append-only**: tanım gereği
yeniden yazılmazlar.

### Tasarım zaten doğru — eksik olan tek şey etiket

`DENETIM.py` bunu biliyor ve doğru davranıyor:

```python
TARIHSEL = ("oturumlar", "DEGISIM-GUNLUGU.md")
bildir = uyari if tarihsel_mi(yol) else hata
```

Yani *"tarihsel dosyadaysa hata sayma, uyar"* kuralı **yazılmış ve
çalışıyor** — 0 HATA çıkmasının sebebi bu. Kusur yalnızca **çıktıda**: iki
`bildir` çağrısının ürettiği 13 kalıcı uyarı, iş düşen uyarılarla aynı listede
ve aynı başlık altında basılıyor.

Uç bir örnek: `DEGISIM-GUNLUGU.md` 832. satır, geçmişte yaşanan bir test-adı
uyarısını **anlatan** cümle. DENETIM açıklamayı kusurun kendisi sanıp tekrar
bayrak kaldırıyor. Kaydın kendisi uyarı üretiyor.

### Neden bugün yazıldı

Zarar bugün yok — 0 HATA, koşu temiz. Zarar **alışkanlıkta**: her koşuda aynı
13 satır aktığında uyarı bloğu okunmayı bırakır, ve o blokta bir gün gerçek
bir şey belirdiğinde görünmez. **O-7'nin kendisi**, bu kez projenin kendi
bekçisinde.

Aynı gün `okunmayan_alanlar` da ilk sürümünde iki yanlış alarm üretmişti
(**T-38**). İkisi aynı dersin iki örneği: *sessizliğe karşı kurulan her
mekanizma, gürültüyle kendini iptal edebilir.*

### Önerilen düzeltme — yeni kural değil, ayrı sayaç

`uyari()`'ye üçüncü bir argüman (`tarihsel=False`); iki `bildir` çağrısında
`True` geçilir; çıktıda iki blok basılır:

```
UYARI (1) - sana is dusuyor
UYARI (13) - tarihsel dosyalarda, DUZELTILEMEZ (append-only)
```

Yeni liste, yeni beyaz liste, yeni eşik yok. Ayrım kodda **zaten
hesaplanıyor**; yalnız basılmıyor.

**Karar bekliyor:** `DENETIM.py` her şeyin bekçisi; ona dokunmak Mustafa'nın
onayıyla olur.

---

## 🟡 T-42 · §11.2'nin `kural_degerleri` örneği §5.2 ile çelişiyor

**Bulundu:** 25 Eylül 2026, T-38'e bakılırken · **Ölçüldü:** evet

**Ne.** §11.2 girdi örneği kişiye özel kural değerlerini şöyle gösteriyor:

```json
"kural_degerleri": { "GUNLUK_AZAMI": 9, "HAFTALIK_AZAMI": 45 }
```

§6 kataloğunda **ikisinin de kapsamı `S`**. §5.2 bunun ne demek olduğunu
yazıyor: *"Kapsamı `S` olan bir kural hiçbir kademede değiştirilemez."* Ve
aynı bölüm `GUNLUK_AZAMI`'yi **ismen** örnek olmaktan çıkarıyor:

> *"v1.3'te bu bölümün örneği `GUNLUK_AZAMI` idi... Kademeli olması
> yanlıştı. `GUNLUK_AZAMI` artık kapsamı `S` olan, 11 saatlik,
> değiştirilemez bir kuraldır."*

**Mekanizma doğru, örnek yanlış.** `kural_degerleri` §5.2'nin `C` kademesinin
taşıyıcısıdır ve gereklidir; sadece onu **şartnamenin kendi yasakladığı iki
kuralla** anlatıyor. v1.3'ten kalan bir örnek, v1.4'te düzeltilen kuralın
yanında durmuş.

### Taşıyıcı biçim sorunu 25 Eylül'de kendiliğinden çözüldü

Bu kayıt açıldığında ikinci bir taraf daha vardı: `{KOD: sayı}` biçimi
`SAGLIK_KISITI`'nın beş zorunlu alanını taşıyamıyordu. **`SAGLIK_KISITI`
aynı gün kataloğdan kaldırıldı** (K-21 geri alındı, T-43), ve `C` kademesinde
taşınacak karmaşık bir şey kalmadı: geriye `PART_TIME_LIMIT` toleransı ve
`UYGUNLUK_TAKVIMI` verisi kalıyor, ikisi de bugünkü biçime sığar.

**Geriye kalan tek sorun örnek.** `kural_degerleri` mekanizması doğru ve
gerekli; sadece §11.2 onu şartnamenin kendi yasakladığı iki kuralla
anlatıyor. Düzeltme küçük: örneği `C` kademesine gerçekten açık bir kuralla
değiştirmek.

**Karar bekliyor:** örnek hangi kuralla yazılsın — yoksa `kural_degerleri`
hiç kullanılmıyorsa §11.2'den tümüyle çıkarılsın mı?

---

## ✅ T-43 · ~~`SAGLIK_KISITI` yazılmadı~~ — **GERİ ÇEKİLDİ (25 Eylül)**

**Açıldı ve kapandı:** 25 Eylül 2026, aynı gün.

**Ne oldu.** Kural yazılmadı diye 🔴 açıldı. Yazmadan önce üç ürün kararı
soruldu. İkinci soruya Mustafa'nın cevabı **kuralın kendisini gereksiz
kıldı**: ürünün gördüğü sağlık durumu kalıcı bir *süre kısıtı* değil,
**dönemsel bir rapor** — ve o zaten bir izin satırı.

`SAGLIK_KISITI` kataloğdan kaldırıldı, **K-21 geri alındı**. Katalog 35 → **34**
(sayılarak doğrulandı). Şartnamede dokunulan sekiz yer K-21 kaydında listeli.

### Bunun yerine ne var

| Durum | Nerede |
|---|---|
| İki günlük rapor | `leaves` satırı, `tip = rapor`, `tum_gun = true` (§8.3) |
| Yarım günlük rapor | Aynı satır, `tum_gun = false` + saat aralığı |
| Motoru bağlaması | `ONAYLI_IZIN` — **yazılı ve testli** |

**Plan yayınlandıktan sonra gelen rapor** (yerine kim geçecek) bir kural
değil; plan editörü + `/suggest` işi. İkisi de yazılmadı, ikisi de ayrı.

### Geriye kalan gerçek iş

**Yarım gün motora hiç gelmiyor.** `tum_gun = false` ve saat aralığı
veritabanında var; §11.2 yalnız `tum_gun` gönderiyor ve motor her koşulda
bütün günü kapatıyor. Yarım gün rapor alan kişi o gün hiç planlanamıyor.
Kayıt: **T-38**'in `izinler[].tum_gun` satırı — ve Mustafa'nın 25 Eylül'deki
kullanımı onu ikincil olmaktan çıkarıp **asıl iş** yaptı.

> **Kaydedilen ders:** bir kuralı yazmadan önce *"bu hangi gerçek vakayı
> çözüyor"* diye sormak, yazdıktan sonra çıkarmaktan ucuz. T-43 bir gün
> yaşadı ve maliyeti üç sorudan ibaret kaldı.

---

## 📌 T-26 · Kayıt ile yürürlük arasında kontrol yok

**Bulundu:** 16 Eylül 2026, dış incelemenin **yöntem önerisinden**

**Ne.** Bir ürün kararı verildiğinde sicile yazılıyor, şartnameye işleniyor,
koda yorum olarak giriyor ve devir paketinde "kapandı" deniyor. **Hiçbir
kontrol, o kararın gerçekten uygulandığını sormuyor.**

K-28 bunun canlı örneği (T-24a): karar kayıtlı, şartnamede yazılı, kodun
başında anlatılmış — ikinci koşulu **hiç yazılmamış**. Kırmızı kanıt turu,
`DENETIM.py` ve CI'nın üçü de kaçırdı, çünkü hiçbiri *"her K-kararının onu
çiviyen bir testi var mı"* diye sormuyor.

> **Bu O-1'in genel hali.** O-1'de RLS tanımlıydı ama etkisizdi. Burada karar
> kayıtlı ama yürürlükte değil. İkisinde de belge doğru, gerçek farklı.

**Öneri (dış incelemeden):** her kritik ürün kararı bir **karşı örnekle**
eşleştirilsin — kararın çiğnendiği durumda kırmızı yanan bir test. Bugün
K-27, K-29 ve K-30'un böyle testleri **var**; K-28'in **yok**.

**Ne gerek:** ürün kararları sicilinde her K maddesine *"bekçi"* sütunu, ve
`DENETIM.py`'ye bekçisi olmayan K maddelerini **uyarı** olarak listeleyen bir
kontrol. Uyarı seviyesinde kalmalı — hata yaparsa O-7'ye düşer.

### İkinci canlı örnek — 23 Eylül'de ölçüldü ve düzeltildi

`08-motor-testleri/v5/fikstur_yukleyici.py` tam da bu riski önlemek için
yazılmıştı. Kendi başlığı şöyle diyor:

> *"Aynı birleştirme mantığını hem `fikstur-denetleyici.py` hem testler
> kullanıyor. İki yerde ayrı ayrı yazılsaydı zamanla ayrışır ve denetleyici
> ile testler FARKLI girdiler üzerinde çalışırdı."*

**`08-motor-testleri/v5/fikstur-denetleyici.py` o modülü hiç import
etmiyordu.** `sahne_uygula`'nın
birebir kopyasını kendi içinde taşıyordu. Yani ortak modül vardı, gerekçesi
yazılıydı, **tek kullanıcısı vardı.**

Ayrışma 23 Eylül'de gerçekleşti: T-19 kısayol açmayı yükleyiciye ekledi,
denetleyicideki kopya eski kaldı, **A08 tutarsız** gösterdi. Kopya silindi,
ortak modül çağrılıyor; 11/11 fikstür tutarlı.

> **Dikkat:** paylaşılan şey **girdi inşası**. `turet` — beklenen sonucun
> bağımsız türetilmesi — paylaşılmadı ve paylaşılmamalı. Girdiyi paylaşmamak
> iki tarafın farklı şeyi denetlemesine yol açar; sonucu paylaşmak denetimin
> kendisini yok eder.
>
> Bu bulgu bir **teste** bağlanmadı. T-26'nın kendi teşhisi: kayıt yeter
> sanılıyor. `DENETIM.py`'ye *"ortak diye yazılmış modülün kaç kullanıcısı
> var"* kontrolü eklenebilir — bekçisi olmayan üçüncü kayıt bu.

---

## 📌 Dış inceleme — yöntem olarak kayda geçiyor *(16 Eylül)*

T-18 ve T-19'u **bizim kırmızı kanıt turumuz bulamadı** ve bulamaması
tesadüf değil.

| | İç kırmızı kanıt | Dış inceleme |
|---|---|---|
| Ne yapar | Kodu bozar, test yakalıyor mu bakar | Şartnameden girdi verir, motor doğru mu bakar |
| Neyi bulur | Kendi varsayımlarımızın korunup korunmadığını | **Varsayımlarımızın kendisinin yanlış olduğunu** |
| 16 Eylül sonucu | 12/12 yakalandı | **19 sessiz hata** (üç tur), 9'u 🔴 |

Kırmızı kanıt turu **kendi kurduğumuz dünyanın içinde** kusursuzdu. Dışarıdan
şartnameyle gelen bir göz, o dünyanın şartnameyle uyuşmadığını gördü.

> **Kural:** bir iş parçası bittiğinde, **şartnameden türetilmiş** girdilerle
> dışarıdan bir inceleme yapılır. Tercihen başka bir modelle — aynı model,
> aynı kör noktayı iki kez taşır.

**Üçüncü tur bu kuralın ikinci gerekçesini verdi.** T-34, T-35 ve T-36'yı
önce *"doğrulayamıyorum, o dosyalar bende yok"* diye geçiştirdim. Köprü
bütün gün elimdeydi; dosyaları **hiç istememiştim**. Mustafa itiraz etti,
çektim, üçü de doğru çıktı. Otopsisi **O-10**.

> Denenmemiş bir erişimin raporu bulgu değil **tahmindir** — ve tahmin,
> kaydedilirken bulgu gibi görünür. Bu T-18'in insan tarafındaki hâli:
> *"kontrol edemedim"* ile *"sorun yok"* aynı cümlede.

## ✅ T-44 · ~~Mola geometrisi `SAHADA_ASGARI`'yi boğuyor~~ — **KAPANDI (28 Eylül, K-34)**

> **Kapanış.** Motorun zaman birimi çeyrek saate indirildi (**K-34**). Eşik
> `N ≥ 4F` → **`N ≥ 12F/7`** (~1.71×F), 15 senaryoda 15/15. Taban 2 için 8
> kişi yerine **4**, taban 5 için 20 yerine **9**. Çözüm süresi 40 kişi /
> taban 5'te **0.78 sn** — model dört kat büyüdü, maliyeti pratikte yok.
> Kalan ~1.71×F bir modelleme hatası değil, yemek ile ortadaki dinlenme
> molasının aynı dilimler için yarışması; ölçüm K-34'te.

> ⚠ **Bu kayıttaki "2.29×" rakamı yanıltıcıydı, düzeltildi.** Mustafa:
> *"Yemek ile molayı birbirine karıştırma."* Ayrıştırınca yemeğin şişmesi
> **1.00×** (hata yok), dinlenmeninki **4.00×**. Harmanlanmış rakam yemeğin
> doğruluğunu dinlenmenin hatasıyla ortalıyordu.


**Bulundu:** 28 Eylül 2026, K-33 yazılırken ölçümle

**Ne.** `SAHADA_ASGARI` (K-33) yazıldı ve çalışıyor, ama bugünkü mola
yerleşimiyle plan **ancak `N ≥ 4F` iken çözülüyor** — N ekipteki kişi, F
taban. Taban 3 isteyen bir firmanın o vardiyada **12 kişisi** olmak zorunda.
Gerçekçi değil.

**Ölçüm.** 15 senaryo çözücüye verildi, formül **15/15** tuttu. İlk tahminim
(`N ≥ 3F`, toplam kapasite hesabı) **10/15** tutmuştu — yani kaba kapasite
hesabı yanlış cevap veriyordu; bağlayan kısıt **pencerelerin örtüşmesi**.

09:00–18:00 vardiya, 1 yemek + 3×15 dk dinlenme:

| mola | aday saatler |
|---|---|
| yemek | 12, 13, 14 |
| dinlenme #0 | 11, 12 |
| dinlenme #1 | 13, 14 |
| dinlenme #2 | 15, 16 |

Kişi başına dört molanın **üçü** `{11,12,13,14}` dört saatine sıkışıyor:
`4(N−F) ≥ 3N` → `N ≥ 4F`. Saat **9, 10 ve 17'ye hiçbir mola düşemiyor**.

**İki ayrı maliyet, ayrı ayrı ölçüldü:**

| kaynak | eşiğe etkisi | ne gerektirir |
|---|---|---|
| **pencere darlığı** | `4F` → `~1.8F` | aday penceresini ±2 saate açmak — `_dinlenme_baslangiclari` içinde yerel değişiklik |
| **saat yuvarlaması** | `~1.8F` → `~1.24F` | 15 dk'lık mola tam saat dilimi kaplıyor. ⚠ Düzeltme: şişme **yemekte 1.00×, dinlenmede 4.00×** — önceki "2.29×" ikisini harmanlıyordu. → K-34 ile kaldırıldı |

**Baskın maliyet pencere darlığı** — bu beklenmiyordu, ölçüm gösterdi.
Sezgi saat yuvarlamasını suçluyordu.

**Pencereyi açmanın adalet maliyeti de ölçüldü** (K-32'nin *"eşit dağıtım"*
kararına karşı): dinlenmeler arası ortalama boşluk **2.12 sa → 2.83 sa**
(ideal 2.25), en küçük boşluk iki durumda da **1.00 sa**. Adalet çökmüyor.
Üstelik saha kullanımı düzeliyor: bugün 12 kişilik planda saat 9, 10 ve
17'de **12 kişi birden** sahada (taban 3 iken), ±2 ile gün boyu düz **3**.

**Karar bekliyor.** Seçenekler:

- **(a)** Aday penceresini ±2'ye aç — eşik `4F → ~1.8F`, adalet maliyeti
  ölçüldü ve küçük. Yerel değişiklik.
- **(b)** Ayrıca zaman çözünürlüğünü inceltip (15 dk dilim) yuvarlamayı da
  kaldır — `~1.24F`'e iner ama modelin büyüklüğü ve çözüm süresi artar,
  şartnamenin saat dilimi varsayımı (#6.3) değişir.
- **(c)** Bugünkü hali kalsın, sınır belgelensin — küçük ekiplerde taban
  kullanılamaz.

`test_bugunku_GEOMETRI_SINIRI` bu sınırı **kayıt olarak** tutuyor: kırmızı
olması *"kod bozuldu"* değil, *"sınır değişti, kaydı güncelle"* demektir.

→ K-33 · K-32 (*"eşit dağıtım"*) · `09-motor/cozucu/model.py::_dinlenme_baslangiclari`

---

## 🟡 T-45 · Tanınmayan **değer** sessizce geçiyor — **seviye düşürüldü (29 Eylül, Mustafa)**

> **Mustafa'nın değerlendirmesi.** *"Data girişleri ekrandan olacak, entegrasyonla gelen data zaten bizim uygulamamıza göre DB'ye yazılacak, Excel import'ta da aynı mantık var — hatalı datayı yükleme aşamasında kullanıcıya bildirerek ilerleyeceğiz. Yine de böyle bir kontrol olması tabii ki iyi. Ben sadece risk görmüyorum fazla."*
>
> **Doğrulama.** .NET tarafında `enum SozlesmeTipi { TamZamanli = 1, YariZamanli = 2, Sezonluk = 3, Stajyer = 4 }` var ve veritabanında **sayı** olarak tutuluyor. Kullanıcı ekrandan seçiyor, elle yazamıyor. Yani *"müdür `part_time` yazar"* senaryosu **yok**.
>
> **Kalan gerçek risk, dar ama sıfır değil:** motor ayrı bir servis ve girdisini JSON olarak alıyor; veritabanındaki `2` değerini `"yari_zamanli"` metnine çeviren katman **henüz yazılmadı**. O çevirici yazılırken bir uyuşmazlık olursa (ya da enum'a beşinci tip eklenip çeviriye eklenmezse) motor sessizce atlar. **Kanıtı var: 28 Eylül'de tam bu hata yapıldı.**
>
> **Karar:** önceliği düşük. Çevirici yazılmadan ÖNCE koymak en ucuzu; sonra koyarsak önce hatayı yaşarız.


**Bulundu:** 28 Eylül 2026, v6 gerçekçi veri seti kurulurken

**Ne.** Veri setini yazarken sözleşme tipini `part_time` diye uydurdum.
Şartnamedeki sözlük (§8.3) `tam_zamanli | yari_zamanli | sezonluk | stajyer`.
Motor `part_time` değerini **tanımadı**, `PART_TIME_LIMIT` kuralı **90 kişiyi
sessizce atladı** ve rapor tertemiz geldi.

**Üç sessizlik kanalının hiçbiri bunu yakalamadı:**

| kanal | neyi yakalar | bunu yakalar mı |
|---|---|---|
| `okunmayan_alanlar` | gönderilen ama **okunmayan alan** | ❌ alan okunuyor |
| `uygulanmayan_kurallar` | gövdesi **yazılmamış kural** | ❌ kuralın gövdesi var |
| `eksik_boyutlar` | yazılı kuralın **eksik boyutu** | ❌ boyut eksik değil |

Boşluk tam ortada: **alan okunuyor, kural çalışıyor, ama değer tanınmıyor.**
Kural `if tip != "yari_zamanli": continue` diyor ve tanımadığı her değeri
sessizce atlıyor.

**Karşılaştırma — kanal çalışınca ne oluyor.** Aynı veri setinde `aktif: false`
diye de yanlış yazmıştım (doğrusu `durum: pasif`). Onu `okunmayan_alanlar`
**yakaladı**: *"alan: aktif, yer: calisanlar, sebep: motor bu alani okumuyor"*.
Yani mekanizma çalışıyor; kapsamı dar.

**Neden önemli.** Bu bir test verisi kazası değil, kiracı entegrasyonunun
olagan hali. Başka bir sistemden gelen `part-time`, `PartTime`, `yarizamanli`
gibi bir değer: plan üretilir, rapor temiz çıkar, **yasal bir tavan hiç
uygulanmamış olur.** Hata yönü yine tek taraflı ve yanlış tarafa — bozuk
girdi motoru daha GEVŞEK yapıyor (T-27'nin aynı sınıfı).

**Ayrıca:** `PART_TIME_LIMIT` yalnız `yari_zamanli`ye bakıyor. Şartnamedeki
`sezonluk` ve `stajyer` tiplerinin **hiçbir haftalık tavanı yok** — ayrı bir
soru, aynı kökten.

**Ne gerek.** Dördüncü bir kanal: `taninmayan_degerler`. Şartnamede
sayılabilir (enum) olarak tanımlı her alan için geçerli değer kümesi bilinir;
girdide o kümenin dışında bir değer varsa bildirilir. `okunmayan_alanlar` ile
aynı desen, aynı yer (`09-motor/dogrulayici/denetle.py`).

⚠ **T-18 ile bağlantılı:** yayın kapısında bekleyen kanal sayısı **üçten
dörde** çıkar. T-18 kararı verilirken bu da hesaba katılmalı.

→ T-18 · T-19 (`okunmayan_alanlar`) · T-27 · `02-spec/v1.4-master-spec.md` §8.3

---

## ✅ T-46 · ~~Motor gerçekçi ölçekte çok yavaş~~ — **KAPANDI (28 Eylül)**

> ⚠ **Açıldığında performans bulgusu sanıldı; ölçünce DOĞRULUK hatası çıktı.**
> Motor SATIŞ çalışanını BACKOFFICE vardiyasına atamayı **engellemiyordu**.
> Teorik değil: üretilen planda gerçekten oldu (`test_ekip_kapsami`).
> Sonucu sessiz bir kapasite kaybı — kişinin saatleri dolar
> (`HAFTALIK_AZAMI`, `HAFTA_TATILI`, `ARDISIK_CALISMA_GUNU` hepsi sayar)
> ama `_atanmis` ekibe göre süzdüğü için **hiçbir ekibin kapsamasına
> sayılmaz**. Çalışan meşgul, kimseye faydası yok.
>
> **Neden şimdiye kadar görülmedi:** bütün test sahnelerinde TEK EKİP
> vardı, çapraz atama tanımsızdı. Üç ekipli ilk sahne kurulunca bir
> dakikada görüldü. Mustafa'nın *"testlerimiz yetersiz"* sezgisinin
> en net kanıtı.
>
> **Çözüm.** `_sablonlari(c)` süzgeci: kişi yalnız kendi ekiplerinin
> vardiyalarına atanabilir. `ekipler` bir listedir (çok ekipli çalışan
> hepsini görür); `ekip` alanı olmayan şablon herkese açık kalır
> (eski fikstürler bozulmaz). Okuma noktaları `_X()` erişicisine çevrildi:
> olmayan değişken aritmetikte sabit sıfır, böylece 16 döngünün hepsini
> yeniden yazmak gerekmedi.
>
> **Ölçülen kazanç (350 kişi):**
>
> | | önce | sonra | |
> |---|---|---|---|
> | değişken | 968.244 | **335.086** | 2.9× küçük |
> | model kurma | 117 sn | **41 sn** | 2.8× hızlı |
>
> Tahmin (~346.545 / ~42 sn) tuttu — çünkü bu kez **sayarak** tahmin
> edilmişti, akıl yürüterek değil.
>
> Motor **124 test** yeşil. Kilit çapraz ekibe işaret ederse model sessizce
> çözümsüz olmaz, `notlar`a sebep yazılır.
>
> 🔴 **Açık kalan:** doğrulayıcı tarafında çapraz ekip atamasını yakalayan
> **hiçbir kural yok**. §7.6 gereği iki taraf bağımsız: elle düzenlenmiş ya
> da dışarıdan gelen bir plan bu ihlali taşırsa **sessizce geçer**.
> Katalogda karşılığı olmayan bir kural gerekiyor — Mustafa'nın kararı.
> (T-45 ile aynı aile: motor tanımadığı şeyi sessizce geçiyor.)


**Bulundu:** 28 Eylül 2026, v6 veri seti ilk kez çalıştırıldığında

**Ne.** 350 kişilik gerçekçi sahnede (3 ekip, 14 şablon, 7 gün):

| | |
|---|---|
| model **kurma** süresi | **117 saniye** (çözmeye başlamadan) |
| değişken | **968.244** |
| kısıt | **965.563** |

**Sebebin büyük kısmı ölçüldü.** `_degiskenler` her kişi için **bütün**
şablonlara değişken açıyor — kişinin ekibinde olmayanlar dahil. Bir SATIŞ
çalışanı için 14 şablonun **9'u anlamsız**:

| | şimdi | ekip süzgeciyle |
|---|---|---|
| `x` değişkeni | 32.550 | 11.650 |
| toplam değişken | 968.244 | ~346.545 |
| kurma süresi | 117 sn | ~42 sn |

**Doğruluk hatası DEĞİL** — sınandı: çapraz ekip ataması kapsamaya
sayılmıyor (`_atanmis` ekibe göre süzüyor). İsraf yalnızca kurma süresi ve
bellek. Ama çözücüye gereksiz serbestlik derecesi de veriyor.

**Düzeltme küçük değil:** `self.sablonlar` üzerinde dönüp `self.x`i indeksleyen
**15+ nokta** var; hepsi kişiye özel listeye çevrilmeli. Aceleye getirilmedi.

⚠ **Neden şimdiye kadar görülmedi:** en büyük test sahnesi **S-10** idi —
10 kişi, 1 ekip, 3 şablon. Mustafa'nın *"test senaryolarımız yetersiz"*
sezgisinin doğrudan karşılığı. Ayrıca K-34 (çeyrek saat) kapsama maliyetini
dört katına çıkardı ve bu **hiçbir testte görünmedi**, çünkü her sahne oyuncaktı.

**Tam ölçekli ÇÖZÜM süresi henüz ölçülmedi** (kurma ölçüldü: 41 sn). Ölçmek için: `08-motor-testleri/gercekci-veri-seti/coz-olc.py`.

→ T-45 · K-34 · `08-motor-testleri/gercekci-veri-seti/` · `09-motor/cozucu/model.py::_degiskenler`

---

## ✅ T-47 · Çözümsüzlük **beş dakika sonra** bildiriliyordu — **KAPANDI (28 Eylül)**

**Bulundu:** gerçekçi veri seti ilk kez çalıştırıldığında, Mustafa'nın makinesinde

**Ne oldu.** 105 kişilik sahne **292 saniye** sonra *"çözümsüz"* döndü. Sebep
gerçekti ve motorun teşhisi **tam yerindeydi**:

```
kapsam : hucre        hucre  : SATIS, gun 0, saat 0
gereken: 1            mumkun : 0
engelleyen: ASGARI_KAPSAMA
```

Pazartesi 00:00–06:00 arasında talep vardı ama o saatleri yalnız **Pazar
gecesi** başlayan bir vardiya kapatabilir — Pazar, planlanan haftanın içinde
değil. (Gerçek hayattaki karşılığı **T-28**: önceki haftanın gece vardiyası
okunmuyor. Bu bulgu T-28'i çözmez, ne kadar erken çarptığını gösterir.)

**Sorun cevapta değil, cevabın fiyatında.** Teşhis ancak çözücü
çözümsüzlüğü KANITLADIKTAN sonra hesaplanıyordu. Üstelik
`_engelleyen_kurallar` her SERT kuralı tek tek gevşetip **yeniden çözüyor**
(kural başına 10 sn'ye kadar; 20 sert kuralda dakikalar).

**Çözüm.** `teshis.ulasilamayan_hucre()` — model kurulduktan hemen sonra,
çözücü çalışmadan önce sorulan basit soru: *bu saate ulaşan bir vardiya
şablonu var mı?* Yoksa plan imkânsızdır ve aramaya gerek yoktur. Kontrol
Z-1'i bilir (gece yarısını aşan vardiya ertesi günün erken saatlerine
ulaşır), yoksa çözülebilir planı reddederdi.

Bu yolda `_engelleyen_kurallar` ve `_en_iyi_plan` da **atlanır**: hiçbir
gevşetme o hücreyi kapatamaz çünkü kapatabilecek vardiya YOK. Engelleyen
kural analitik olarak bellidir (`ASGARI_KAPSAMA`), aranmasına gerek yok.

**Ölçülen (aynı cevap, aynı hücre):**

| sahne | önce | sonra | |
|---|---|---|---|
| 35 kişi | 73 sn | **3.7 sn** | 20× |
| 105 kişi | 292 sn | **10.7 sn** | 27× |
| 350 kişi | ölçülemedi | **37 sn** | — |

**⚠ Testin ilk hali yanlıştı ve yazıldığı anda yeşildi.** SÜREYE bakıyordu;
dört kişilik bir sahnede çözücü zaten milisaniyede bitiriyordu, yani test
ölçmek istediği şeyi hiç ölçmüyordu. Süre bir MAKİNE özelliğidir,
mekanizma değil. Test `durma_sebebi == "on_kontrol"` ve
`cozum_suresi_sn == 0.0`'a bakacak şekilde yeniden yazıldı; mutasyonla
sınandı (ön kontrol kapatılınca iki test kırmızı).

Bu, aynı gün üçüncü kez: **küçük sahne sorunu gizliyor.**

**Veri tarafı da düzeltildi.** Üretici gece talebini `saat % 24` yapıp günü
aynen bırakıyordu; 24'ü aşan saat **ertesi güne** aittir. Haftanın son
gününden taşan kısım planın dışında kalır. Düzeltme sonrası sahne
**çözülüyor** (35 kişi → 165 atama).

→ T-28 · T-46 · `09-motor/cozucu/teshis.py::ulasilamayan_hucre`

---

## ✅ T-48 · ~~*"Çözümsüz"* iki ayrı şeyi aynı kelimeyle söylüyor~~ — **KAPANDI (29 Eylül, K-37)**

**⚠ 28 Eylül'de bu madde hipotezdi.** Kod okunarak çıkarılmıştı, uçtan uca
bir vaka kurulamamıştı ve *"kapatmadan önce kanıtı üretilmeli"* yazıyordu.
29 Eylül'de çekirdek ölçüm aracı yazılırken kanıt kendiliğinden çıktı — ve
beklenenden **pahalı** olduğu görüldü.

**Ne.** `09-motor/cozucu/coz.py`:

```python
if durum in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    return {"durum": "cozuldu", ...}
return teshis_koy(...)          # -> "durum": "cozumsuz"
```

CP-SAT'ın iki farklı sonucu aynı kapıya çıkıyor:

| CP-SAT | anlamı | motorun dediği |
|---|---|---|
| `INFEASIBLE` | **kanıtlandı**: böyle bir plan yok | `cozumsuz` |
| `UNKNOWN` | **bütçe doldu**, plan bulunamadı | `cozumsuz` |

Ayrım `cozum_istatistikleri.durma_sebebi` içinde duruyor, ama **başlıkta yok**.

### Ölçülen (29 Eylül, 35 kişilik sahne, tek arama işçisi)

| | |
|---|---|
| verilen bütçe | 45 sn |
| satırın **toplam** süresi | **470 sn** |
| bulunan plan | yok |

Bütçe dolduğunda motor teşhis koyuyor: her sert kuralı tek tek gevşetip
yeniden çözüyor (kural başına 10 sn'ye kadar) ve üstüne bir *"en iyi plan"*
arıyor. Yani kullanıcı 45 saniyeyi bekledikten sonra **7 dakika daha**
bekliyor — bütçesinin **on katı**.

### İki ayrı zarar, tek sebepten

1. **Yanlış olabilecek cümle.** Teşhis *"şu hücreyi şu kural engelliyor"*
   diyor. Ama hiçbir şey kanıtlanmadı — çözücü yalnızca yetiştiremedi.
   Yöneticiye *"çözümsüz"* demek, *"bu talebi bu kadroyla karşılamak
   imkânsız"* demektir — personel alımına kadar giden bir karar.
2. **Üstelik bedava değil.** Yanlış olabilecek bu cevap, zaten dolmuş
   bütçenin on katı sürede veriliyor.

### Önerilen — **ürün kararı, Mustafa'ya sorulacak**

| CP-SAT | motorun diyeceği | teşhis koşsun mu |
|---|---|---|
| `INFEASIBLE` | `cozumsuz` — böyle bir plan yok | **evet**, soru anlamlı |
| `UNKNOWN` | `sure_yetmedi` — bulamadım | **hayır**, cevaplanacak soru yok |

Kazanç iki taraflı: cümle doğrulaşır **ve** kullanıcı 7 dakikayı beklemez.
Onun yerine *"süreyi uzat"* anlamlı hâle gelir — K-35'in süre seçimiyle
aynı aile.

Şartname §11.3 çıktı sözleşmesini değiştirir.

### ✅ Kapanış — 29 Eylül, K-37

**Önerilen tablo aynen uygulandı.** `UNKNOWN` artık `sure_yetmedi` diyor ve o
yolda teşhis **koşmuyor**. `INFEASIBLE` `cozumsuz` diyor ve teşhis
`teshis_kesin` **True** ile koşuyor. Kullanıcı yine de sorabiliyor:
*"neden olduğunu araştır"* → teşhis koşuyor ama cevap `teshis_kesin` **False**.

**Kazanılan:** 45 saniyelik bütçe artık 45 saniye sürüyor. 470 saniyelik yol
kapanmadı, **isteğe bağlandı** — bekleyen ne beklediğini biliyor.

Bekçisi altı test: `09-motor/testler/test_sure_yetmedi.py`.

⚠ **Bütçe aşımının ikinci kaynağı açık, başka numarada.** Iki aşamalı
çözümde ilk aşamanın süresi ana bütçenin **üstüne** ekleniyor — **T-59**.
Yani *"15 dakika"* diyen yönetici henüz 15 dakikada cevap almıyor; sebebi
artık teşhis değil.

→ T-22 (çözümsüzlükteki taslak) · T-45 · K-35 · `02-spec/v1.4-master-spec.md` §11.3 · K-37 · T-23 · T-59

---

## ✅ T-49 · ~~Çözücü iyileşme durduğu hâlde aramaya devam ediyordu~~ — **KAPANDI (28 Eylül)**

**Bulundu:** gerçekçi veri seti çalıştırılırken, Mustafa'nın makinesinde

**Ne.** `09-motor/cozucu/coz.py` içindeki ayarlarda şu satır duruyordu:

```python
"durgunluk_saniye": 120,      # 2 dk iyilesme yoksa bitir
```

Parametre **tanımlı**, açıklaması **yazılı**, `_ErkenDur.son_iyilesme` alanı her
çözümde **güncelleniyor** — ama hiçbir yerde **okunmuyordu**. Karar verilmiş,
belgelenmiş, hiç uygulanmamış.

Bu, T-24a/T-26'nın (*"karar kayıtlı ama yürürlükte değil"*) canlı örneği — ve
bu kez **bedeli ölçüldü**: 35 kişilik gerçekçi bir sahnede çözücü bütçenin
tamamını (**903 saniye**) kullandı; planı çok daha önce bulmuştu.

**Neden basit bir kontrol yetmedi.** CP-SAT'in çözüm callback'i yalnız **yeni
çözüm** bulununca tetiklenir. Çözücü tıkandığında callback hiç çağrılmaz —
yani durgunluğu callback'in **kendisi fark edemez**. Dışarıdan saniyede bir
bakan ayrı bir bekçi gerekti (`_durgunluk_bekcisiyle_coz`).

**Bekçinin şartı:** en az bir plan bulunmuş olmalı. Hiç plan yokken durmak,
*"imkânsız"* ile *"bakmadım"*ı karıştırmak olurdu (T-48'in aynı ailesi).

**Ölçülen (35 kişi, aynı sahne, aynı plan):**

| | önce | sonra |
|---|---|---|
| çözüm süresi | 903 sn | **111–135 sn** |
| atama | 164 | 164 |
| sert ihlal | 0 | 0 |

Aynı plan, sekizde bir sürede. Motor **133 test** yeşil.

**⚠ Testin ilk hali yine yanlıştı** — bugün üçüncü kez. Sahne 24 kişilikti ve
çözücü 3 saniyede `hedef_bosluk` ile bitiyordu; test durgunluğu **hiç
sınamadan** yeşil geliyordu. Sahne gerçekten tıkanan bir şekle (60 kişi,
asgari 10 / hedef 30) çevrildi ve mutasyonla sınandı.

→ T-24a · T-26 · T-48 · `09-motor/cozucu/coz.py::_durgunluk_bekcisiyle_coz`

---

---

## 🟡 T-50 · 350 kişide plan optimuma **çok uzak** — ve sebebi henüz ayrılmadı

**Bulundu:** 29 Eylül akşamı, çekirdek ölçümü yapılırken, Mustafa'nın makinesinde.

**Ne.** 350 kişilik gerçek sahnede iki ölçüm çok farklı rakam verdi:

| ne zaman | süre | iki aşama | işçi | optimuma uzaklık |
|---|---|---|---|---|
| 28 Eylül | 900 sn | **açık** | 8 | **%10,0** |
| 29 Eylül | 360 sn | **kapalı** | 6 | **%42,4** |
| 29 Eylül | 120 sn | kapalı | 6 | %69,3 |

⚠ **İki değişken aynı anda değişti** (süre ve iki aşama), bu yüzden %10 ile
%42 arasındaki farkın ne kadarı hangisinden geliyor **bilinmiyor**. Sürenin
tek başına etkisi ölçüldü: 120 → 360 saniye, %69 → %42. Bu eğrinin 900
saniyede %10'a inmesi zor görünüyor — yani farkın büyük kısmı muhtemelen
**iki aşamadan** geliyor. **Muhtemelen — ölçülmedi.**

**Neden önemli.** K-35 kullanıcıya *"bu plan teorik en iyisinin %X'i kadar
iyi"* diyeceksek, 350 kişilik bir müşteride o X'in ne olduğunu bilmemiz
gerekiyor. %10 ile %42 arasındaki fark, ekranda görülecek cümlenin
*"neredeyse en iyisi"* ile *"kabaca bir plan"* arasındaki farkıdır.

Ayrıca **iki aşama** şu an yalnız *"çözücü hiç plan bulamıyorsa ona bir tane
ver"* diye konumlandırılmıştı. Eğer plan **kalitesini** de bu kadar
değiştiriyorsa, eşiği ve rolü yeniden düşünülmeli.

**Kapatmak için gereken tek koşu.** ⚠ Süresini tahmin etmiyorum: iki aşama açıkken her koşu, verilen bütçeye ek olarak birinci aşamaya ayrılan süreyi de harcar (`ilk_asama_saniye`, varsayılan 120 sn), artı ~27 sn model kurma. Yani iki koşu için kabaca 2 × (360 + 120 + 27) saniye — ama gerçeği ekranda görülecek:

```
py cekirdek-olc.py --olcek 1 --saniye 360 --isci 6 --tekrar 2
```

Araçta iki aşama artık **varsayılan açık**, yani bu koşu 29 Eylül'ün %42,4'ü
ile doğrudan karşılaştırılabilir: tek değişen iki aşama olur.

→ K-35 · K-36 · `09-motor/cozucu/coz.py` (`_ipucu_ver`, `iki_asama_esigi`)

---

## 🟡 T-51 · 45 saatlik sözleşme tutturulamıyor — **KURAL TARAFI KAPANDI (29 Eylül, K-39), VERİ TARAFI AÇIK**

**Kapanan:** kural artık sert, izin düşülüyor ve **doğrulayıcıda gövdesi var** — eksik planlanan saat artık sessizce geçmiyor.

**Açık kalan:** veri seti. Şablonlar 45 saati taşımıyor (SATIŞ 6 günde 42, BACKOFFICE 43,5). Yeni şablonlarla (6×7,5 ve 5×9) birlikte zor veri setinde çözülecek.

**Bulundu:** 29 Eylül, Mustafa'nın sorusuyla: *"Tam zamanlı çalışanların
haftada 45 saati doldurmaları gerekli. Yani 42 saat olarak planlayamayız."*

**Ölçüldü.** Veri setindeki şablonların net süreleri ve hafta tatili (1 gün)
birlikte bir **tavan** koyuyor:

| ekip | en uzun vardiya (net) | 6 günde azami | 45 saat tutar mı |
|---|---|---|---|
| SATIŞ *(200 kişi)* | 7,0 | **42,0** | **hayır** |
| BACKOFFICE *(100 kişi)* | 7,2 | **43,5** | **hayır** |
| MÜŞTERİ HİZMETLERİ *(50 kişi)* | 8,0 | 48,0 | evet |

350 kişinin 300'ü için 45 saat **ulaşılamaz bir hedef**. Plandaki sonuç
(0.1 ölçek, 17 kişi 45 saat sözleşmeli):

| | |
|---|---|
| 45 saati tutturan | **0** |
| 43–45 arası | 8 |
| 43'ün altında | 9 |
| ortalama | **38,2 saat** |

### ⚠ Asıl bulgu: hiçbir kapı bunu görmedi

Plan **`0 sert ihlal`**, **`yayınlanabilir: True`** döndü. Üç sebepten:

1. `SAAT_DENGESI` **yumuşak** — ihlal değil, ceza.
2. **Tek taraflı**: yalnız *eksik* çalışmayı cezalandırıyor, üstelik
   **2 saat toleransla**. Yani 43 saat bedava, 42 saat çok ucuz.
3. **Doğrulayıcıda gövdesi YOK.** Bağımsız denetçi bu kuralı hiç
   bakamıyor — yani §7.6'nın koruması bu kuralda çalışmıyor.

17 kişi × ~3 saat = haftada ~51 saat, sözleşmeyle ödenen ama planlanmayan
zaman. 350 kişilik gerçek ölçekte bunun karşılığı çok daha büyük.

### Bu, fazla kadro bulgusuyla AYNI bulgunun iki yüzü

Aynı gün ölçülmüştü: hedef talep 5.815 kişi-saat, sözleşme kapasitesi
13.520 saat (**%43**), ve plan hedefin **2,00 katı** kişiyi sahaya koyuyor.
Sebebi tam olarak bu: `SAAT_DENGESI` sözleşmeleri doldurmaya çalışıyor,
hedefi aşmayı cezalandıran bir kural yok, ve şablonlar zaten yetmiyor.

### Kapatmak için gereken — ve bunların ikisi **ürün kararı**

1. **Veri**: 45 saatlik sözleşmeyi taşıyabilen şablonlar (ör. 9 saat brüt /
   8 saat net × 6 gün, ya da 10/9 × 5 gün). Şu anki set bu sözleşmeyi
   **tanımlıyor ama karşılayamıyor**.
2. **Kural sertliği (Mustafa)**: `SAAT_DENGESI` sert mi, yumuşak mı; tolerans
   kaç saat; üst taraf (sözleşmeden fazla çalıştırma) ayrı mı yönetilecek.
3. **Yasal mı — CEVAPLANDI (Mustafa, 29 Eylül): hayır, `yasal: false`.**
   Gerekçesi ticari: *"Türkiye'de çalışma saati başına maaş verilmediği,
   direkt net maaş verildiği için, tam zamanlı bir çalışanın 43 saat
   çalışması demek ona 2 saat fazla para veriyorum demektir."*
   Yani eksik planlama **kanunu değil bütçeyi** deler; kural gevşetilebilir
   ama gevşetmenin bir **para karşılığı** vardır. Üst taraf (sözleşmeden
   fazla çalışma) ayrı bir konudur: o **fazla mesaidir** ve yasal
   sınırları vardır (bkz. T-52).
4. **Doğrulayıcı gövdesi**: karar ne olursa olsun yazılmalı. Kontrol
   edilmeyen bir kural, kural değildir.

→ K-36 · `09-motor/cozucu/model.py` (`_saat_dengesi`) ·
  `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py`

---

## ✅ T-52 · ~~45 saatlik tam zamanlı çalışana fazla mesai yaptırılamıyor~~ — **KAPANDI (29 Eylül, K-38)**

**Çözüm:** `HAFTALIK_AZAMI` artık normal çalışma sınırı; toplam tavan *normal + fazla mesai tavanı*. 6 test, ikisi kırmızı başladı; mutasyon bir boşluk yakaladı ve altıncı test onu kapattı. Ayrıntı K-38'de.

**Bulundu:** 29 Eylül, Mustafa'nın *"çözümsüzse fazla mesaiye başvuracak,
en son çare"* cümlesi üzerine bakılırken.

**Ne.** `09-motor/cozucu/model.py` → `_sure_sinirlari()` iki kisit koyuyor:

```python
self.m.Add(dakika <= int(haftalik * 60))                    # HAFTALIK_AZAMI = 45
self.m.Add(dakika <= int((tavan + fm_tavan) * 60))          # 45 + 10 = 55
```

Bağlayıcı olan **birincisi**. 45 saat sözleşmeli bir çalışan zaten 45'te
duruyor — yani **fazla mesai matematiksel olarak imkânsız**. K-30'un
*"asgari zorlarsa minimum fazla mesai"* dalı, `fazla` ceza değişkeni ve
profile bağlı `FAZLA_MESAI_PROFIL` tavanı bu çalışanlar için **ölü kod**.

**Ölçüldü — tek değişken izole edildi.** Aynı sahne (6 kişi, 6 gün, herkesin
48 net saat çalışması gerekiyor; sözleşme 40 saat, fazla mesai tavanı 10 —
yani 48 saat **izinli olmalı**). Tek değişen `HAFTALIK_AZAMI` parametresi:

| `HAFTALIK_AZAMI` | sonuç | en çok çalışan | fazla mesai |
|---|---|---|---|
| **45** | **çözümsüz** | — | — |
| **55** | çözüldü | 48 saat | 48 saat *(6 kişi × 8)* |

**Neden önemli.** Mustafa'nın tarif ettiği Türkiye gerçeği şu: *"eleman
yetmiyor, fazla mesaiye gidiliyor."* Motor bugün bunu **yapamaz**; onun
yerine `cozumsuz` ya da `sure_yetmedi` döner. Yani en çok ihtiyacımız
olacak kaçış yolu kapalı.

Ve fark edilmemesinin sebebi tanıdık: veri seti kimseyi 45 saate
yaklaştırmıyordu (herkes 38–42 saatteydi, bkz. T-51).

**Karar — ürün + hukuk (Mustafa).** `HAFTALIK_AZAMI` neyin tavanı?

* **normal çalışma sınırı** ise 45 doğrudur, ama o zaman fazla mesai
  **ayrı bir tavanla** modellenmeli ve toplam saat 45'i aşabilmeli;
* **toplam saat tavanı** ise 45 fazla mesaiyi tanımdan imkânsız kılar.

Mustafa'nın söylediği iki sınır ayrıca modelde **zaten var**: günlük 11
saat (`GUNLUK_AZAMI`, SERT + yasal) ve haftalık fazla mesai tavanı
(`FAZLA_MESAI_TAVANI`, profile bağlı: CALISAN 0 · DENGELI 10 · KAPSAMA 15).
Yıllık tavan (`YILLIK_FAZLA_MESAI_TAVANI`) **SERT ve yasal işaretli ama
gövdesi yok** — geçmiş dönem verisi gerektiriyor.

⚠ **Bu, zor veri setinin ÖNKOŞULU.** Talep kapasitenin %95'ine
çıkarıldığında izinlerle birlikte fazla mesai **zorunlu** hale gelir;
bu kisit düzeltilmezse yeni set yanlış sebeple çözümsüz döner.

→ K-30 · T-51 · `09-motor/cozucu/model.py` (`_sure_sinirlari`)

---

## ✅ T-53 · ~~K-39 üç altın senaryoyu gevşetti~~ — **KAPANDI (29 Eylül)**

### Ortak kök sebep (29 Eylül'de ölçüldü)

Altın senaryoların **kıtlık mekanizması** yarı zamanlıların sözleşme saatiydi
(20, 24 saat). K-39 o alanı kaldırınca üç sahne birden gevşedi ve
*"kadro yetmiyor"* / *"iki profil farklı plan üretir"* iddiaları doğru olmaktan
çıktı. Hata değil; onaylanmış bir kararın onaylanmış sahneleri gevşetmesi.

### ✅ A1 — kapandı

Yarı zamanlılarda `haftalik_saat` alanı kaldırıldı (Mustafa onayı), kontrol
alanı `.get()` ile okuyor (alan yokken **KeyError** veriyordu — düpEDüz hata).

### ✅ A9 — kapandı

Yarı zamanlılara **gerçekçi uygunluk** kondu (Mustafa'nın seçimi): C08 3,
C09 2, C10 2 gün hafta içi müsait → 7 atama. 7 tam zamanlı × 5 gün = 35;
toplam **42** — fikstürün kendi hesabı aynen korundu.

⚠ Uygunluk **A9'un kendi `fark`ına** kondu, paylaşılan S10 sahnesine
dokunulmadı. İlk denemede S10'a konmuştu ve **A7'yi de bozdu**; geri alındı.

### ✅ A7 — kapandı (29 Eylül)

A7 aynı girdiyi iki profille koşturur ve **farklı plan çıkmasını** şart koşar
(eşitlik = ağırlık tablosu çalışmıyor demektir → kırmızı).

⚠ **Tek başına hiçbir seçenek yetmedi — ölçüldü:**

| ayar | KAPSAMA | CALISAN | fark |
|---|---|---|---|
| cmt 3, uygunluk yok | %100,0 / sapma 2 | %100,0 / sapma 2 | yok |
| cmt 4, uygunluk yok | %100,0 / sapma 2 | %100,0 / sapma 2 | yok |
| cmt 5, uygunluk yok | %100,0 / sapma 1 | %100,0 / sapma 1 | yok |
| cmt 3, uygunluk VAR | %95,92 / sapma 2 | %95,92 / sapma 2 | yok |
| cmt 4, uygunluk VAR | %95,92 / sapma 2 | %91,84 / sapma 2 | kısmi |
| **cmt 5, uygunluk VAR** | **%95,92 / sapma 2** | **%91,84 / sapma 1** | **iki eksende de** |

Mustafa'nın seçtiği 1. seçenek (cumartesi talebini artır) **tek başına
çalışmıyor**: 6 kişiye kadar çıkarıldı, iki profil yine aynı planı verdi.
Sahnede o kadar boşluk var ki hedef her ayarda %100 tutuyordu.

Çözüm iki şeyin BİRLİKTE uygulanmasıydı ve **deneme-yanılmayla değil
ızgara ölçümüyle** seçildi: **cumartesi 5 kişi + yarı zamanlılara gerçekçi
uygunluk** (A9'dakinin aynısı). Sonuçta A7'nin iki onaylı cümlesi de doğru
yönde ayrışıyor:

* *"Çalışan profili cumartesiyi daha adil dağıtır"* — sapma 1 ≤ 2 ✓
* *"Kapsama profili hedefi daha iyi tutturur"* — %95,92 ≥ %91,84 ✓

Üç ardışık koşuda da yeşil (kararlılık kontrolü). İkisi de A7'nin **kendi
`fark`ında**; paylaşılan S10 sahnesine dokunulmadı.

**Altın senaryolar 12/12 yeşil.**

→ K-39 · `08-motor-testleri/v5/fikstur/A07.json`

**Bulundu:** 29 Eylül, K-39 uygulandıktan hemen sonra, altın senaryolar koşulunca.

⚠ **Bunlar hata değil.** Mustafa'nın bugün verdiği kararın, 15 Eylül'de yine
onun onayladığı iki cümleyle çelişmesi. Fikstürlere **dokunulmadı**:
onaylanmış cümleyi değiştirmek Mustafa'nın işi.

### A1 — *"Haftalık saat sözleşmeyi aşmaz"*

```
metrikler.fazla_mesai_saat: 0 olmalıydı, 3.0 geldi
Sözleşme saatini aşanlar: C08 23.0 saat (sözleşme 20)
```

C08 yarı zamanlı. K-39'dan sonra kişinin **kendi** sözleşmesi tavan değil;
tavan mevzuattan geliyor (30 saat). 23 saat artık ihlal değil.

**Karar (Mustafa):** A1'in cümlesi mi değişecek (*"haftalık saat **mevzuat
tavanını** aşmaz"*), yoksa yarı zamanlıda sözleşme yine tavan mı olacak?

⚠ Yan soru: `fazla_mesai_saat` metriği **sözleşmenin üstündeki her saati**
sayıyor. Yarı zamanlı için bu yanlış ad: Mustafa'nın kendi aktardığına göre
30–45 saat arası *"fazla sürelerle çalışma"*, *"fazla mesai"* değil. Metriğin
ikiye ayrılması gerekebilir.

### A9/a — *"hedef yetmiyor"* senaryosu artık yetiyor

```
hedef_kapsama_yuzde: en fazla 99.9 olmalıydı, 100.0 geldi
eksik_hedef_dakika : en az 1 olmalıydı, 0 geldi
```

Senaryonun **ön kabulü** bozuldu: yarı zamanlılar artık 20 yerine 30 saate
kadar çalışabildiği için kadro, hedefi karşılamaya yetiyor. Yani senaryo
*"hedef yetmiyor"* demeyi bıraktı.

**Karar (Mustafa):** sahne yeniden sıkılaştırılacak mı (kadro azalt / talep
artır), yoksa senaryonun anlamı mı değişecek?

⚠ **Bu iki kırmızı çözülmeden `main`'e push edilmemeli** — *"main her zaman
yeşil"* kuralı.

→ K-39 · `08-motor-testleri/v5/fikstur/A01.json` · `.../A09.json` ·
  `08-motor-testleri/v5/KABUL-OLCUTLERI.md`

---

## 🔴 T-54 · Yarı zamanlı saatinin **maliyeti yok** — çözücü onları bedava sanıyor

**Bulundu:** 29 Eylül, yarı zamanlı tavanı 45'e çıkarıldıktan hemen sonra,
kendi testim kırmızı yanınca.

**Ölçülen.** Talep **asgari 1 kişi**. Sahnede 4 yarı zamanlı var. Üretilen plan:

```
C1: 45.0   C2: 45.0   C3: 45.0   C4: 45.0   saat
```

Dördünü de tavana kadar doldurdu — 1 kişilik talep için.

**Neden.** Modelde bir saatin **parası tanımlı değil**. Hiçbir kural
*"gereksiz yere kişi yazma"* demiyor; hedefi **aşmayı** cezalandıran kural da
yok. Yarı zamanlıları eskiden sınırlayan tek şey kendi sözleşme saatleriydi
(20, 24 saat) — K-39 ile o kalktı, yerine 45 geldi.

**Aynı açığın daha önce ölçülen yüzü:** 350 kişilik sahnede plan, hedefin
**2,00 katı** kişiyi sahaya koyuyordu (415 hücrenin 324'ünde hedef aşılmıştı).
O zaman fazlalık tam zamanlılardan geliyordu (sözleşme doldurma baskısı);
şimdi yarı zamanlılardan da gelebilir — ve **her saati para**.

⚠ Mustafa'nın mantığı (*"önce tam zamanlıları 45'e tamamlarız, sonra yarı
zamanlılara geçeriz"*) tam zamanlı tarafı için **kendiliğinden çalışıyor**:
45 saat tabanı SERT, yani onlar zaten dolar. Fren eksik olan yer **ondan
sonrası**: asgariyi tutturduktan sonra dur diyen bir şey yok.

**Çözüm adayı (ürün kararı — Mustafa).** Hedefi aşmayı cezalandıran bir kural
(ör. `HEDEF_ASIMI`, yumuşak). Bugün katalogda **yok**. Alternatifi, saat
başına maliyet terimi — ama o, ücret verisini motora sokmak demek.

→ K-39 · `09-motor/cozucu/model.py` (`_sure_sinirlari`) ·
  `09-motor/testler/test_sozlesme_saati.py`

---

## ✅ T-55 · ~~*"Gece vardiyası yapamaz"* işareti yok~~ — **KAPANDI (29 Eylül, K-40)**

**Çözüm:** `gece_vardiyasi` (şablon) + `gece_calisamaz` (çalışan) alanları ve `GECE_UYGUNLUGU` kuralı (SERT, katalog 40). İşaret tahmini ezer; işaret yoksa tahmine düşülür ve not yazılır. 8 test, 3 mutasyon. Ayrıntı K-40'ta.

<details><summary>ilk kayıt</summary>


**İstek (Mustafa, 29 Eylül).**

> *"Kullanıcı kartında gece vardiyası yapamaz gibi bir ifadeye ihtiyacımız var.
> Vardiya planı yapılırken de vardiya gece vardiyasıdır diye bir işaret koymamız
> gerekiyor. Bunu kullanıcı işaretleyecek. Böylelikle gece vardiyalarına uygun
> olmayan çalışanları ilgili vardiyadan direkt elemiş olacağız."*

**Bugün ne var, ne yok.** Motor gece vardiyasını **saat aralığından tahmin
ediyor** (`_gece_mi`, `GECE_PENCERESI`) ve bunu yalnız `ADALET_DENGESI`'nin
"gece" boyutunda, yani **adil dağıtım** için kullanıyor. Çalışan tarafında
*"gece çalışamaz"* diye bir alan **yok**; bugün ancak `uygunluk` ile, her gece
için ayrı saat aralığı yazılarak taklit edilebilir — zahmetli ve hataya açık.

**Gereken iki alan (girdi sözleşmesi — §8.3 / §11.2):**

| nerede | alan | anlamı |
|---|---|---|
| vardiya şablonu | `gece_vardiyasi: true` | bu şablon gece vardiyasıdır — **kullanıcı işaretler** |
| çalışan | `gece_calisamaz: true` | bu kişi gece vardiyasına atanamaz |

⚠ **Tahmin ile işaret ayrı şeylerdir.** Saat aralığından çıkarmak
(ör. 23:00-07:00) çoğu zaman doğru çalışır ama 22:00-06:00 ya da 00:00-08:00
gibi sınır durumlarında firmanın kendi tanımıyla çelişebilir. Mustafa'nın
istediği **işaret**: kullanıcı söyler, motor tahmin etmez.

**Yeni kural** (katalog **40**'a çıkar): `GECE_UYGUNLUGU`, SERT.
Gerekçesi firma-çalışan anlaşması ya da sağlık raporu olabilir — `yasal`
bayrağı Mustafa'nın kararı.

⚠ `ADALET_DENGESI`'nin "gece" boyutu da bu işaretten beslenmeli; iki yerde
iki farklı gece tanımı kalmamalı.

**Sırada nereye giriyor.** Veri setlerinden önce: yarı zamanlılara gece
vardiyası verilecekse (Mustafa: *"gece vardiyaları genelde bu arkadaşlara
yaptırılıyor"*) bu işaret olmadan set gerçekçi olmaz.

→ K-39 · K-40

</details>

---

## 🟡 T-56 · Veri seti yenilendi — **500 KİŞİLİK İKİ SET KURULDU, BEKÇİLER BAĞLANDI**

**29 Eylül akşamı kurulan:** `_sahne-S30-85.json` ve `_sahne-S30-95.json`.

| | |
|---|---|
| kişi | **500** (285 satış / 145 backoffice / 70 müşteri hizmetleri) |
| sözleşme | tam zamanlı 341, yarı zamanlı 130, sezonluk 13, stajyer 16 |
| şablon | **17** — 6×7,5 ve 5×9,0 net desenleri; gece vardiyaları **işaretli** |
| kural | **40**, hepsi tanımlı |
| izinli 59 · gece çalışamaz 60 · pasif 16 | |
| kapasite | 19.630 kişi-saat/hafta |
| **%85 seti** | hedef 16.654 (%84,8) |
| **%95 seti** | hedef 18.660 (%95,1) |

İki set arasındaki **tek fark talep tablosu**.

**0.1 ölçekte ölçüm (49 kişi):**

| | %85 | %95 |
|---|---|---|
| durum | çözüldü | çözüldü |
| asgari kapsama | %100 | %100 |
| hedef kapsama | %97,35 | **%89,4** |
| sert ihlal | **YOK** | **YOK** |
| yayınlanabilir | True | True |
| fazla mesai | 124 sa | 128 sa |

Set kurulurken **üç hata buldu**: kesirli vardiya bitişi (T-58), net saat
ayrışması (T-57) ve K-38'in doğrulayıcıya uygulanmamış olması.

**✅ BEKÇİLER BAĞLANDI (29 Eylül akşamı)**

**12 bekçi, ~4 dk 47 sn, hepsi yeşil.** Yeni eklenenler:

* `test_SABLONLAR_45_SAATI_tutturabiliyor` — her ekipte 6× ya da 5× ile
  tam 45 eden bir şablon olmalı. T-51 ve T-57'nin ortak bekçisi.
* `test_TAM_ZAMANLI_sozlesme_saatini_DOLDURUYOR` — saatler **doğrulayıcının**
  ölçüsüyle hesaplanır; çözücünün kendi ölçüsüyle bakmak kendi işini kendi
  onaylamak olurdu (§7.6).
* `test_DOLULUK_hedeflenen_oranda` — iki setin tek farkı bu; oran kayarsa
  karşılaştırma anlamsızlaşır.
* `test_fikstur_URETICIYLE_ayni` ve `test_sahne_KATALOGUN_TAMAMINI_tanimlar`
  iki set için ayrı ayrı koşuyor.

**Gövdesi yazılı 26 kuralın hepsi kendi ihlal vakasında kırmızı yanıyor** (eksik: sıfır). İki vaka eklendi
(`GECE_UYGUNLUGU`, `SAAT_DENGESI`), biri **yeniden yazıldı**:
`PART_TIME_LIMIT`'in eski vakası "5 gün × 9 saat" diyordu ve tavan kişinin
sözleşmesi olduğu için ihlal sayılıyordu; K-39 tavanı 45'e çıkarınca vaka
**SESSİZ** kaldı ve kural görmez oldu. Yeni vaka 7 gün × 9 net = 63 saat.

**CI adımı güncellendi**: *"Zor veri seti (500 kişi, %85 ve %95)"*.
Yol aynı olduğu için komut değişmedi; süre sınırı 20 dakika yeterli
(motor 110 sn + altın 10 sn + bekçiler 287 sn).

**AÇIK KALAN İŞ:**
1. ⚠ **Fazla mesai 49 kişide 124 saat** (kişi başı ~2,5 sa) — %85 doluluktaki
   bir sahnede bu çok. T-54'ün (saatin maliyeti yok) yeni ölçümü; taban 45
   iken kimse üzerine çıkmayı engellemiyor.
2. ✅ **Tam ölçek çözüldü** — 29 Eylül gecesi, Mustafa'nın makinesinde:
   638.572 değişken, 754.633 kısıt, kurma **51 sn**, çözüm **1.078 sn**,
   2.493 atama, **0 sert ihlal**, `yayınlanabilir` **True** — ama optimuma
   **%98,3** uzak. İki yeni bulgu açtı: **T-59** (bütçe aşımı) ve **T-60**
   (plan yasal çıkıyor, *iyi* çıkmıyor). Eski 350 kişilik setin 1,9 katı.

<details><summary>ilk kayıt</summary>

**Bulundu:** 29 Eylül, K-40'tan sonra bütün paketler koşturulunca.

Motor **178 test** yeşil, altın senaryolar **12/12** yeşil; kırmızı olan
yalnız gerçekçi ölçek bekçileri (3/7). Üçü de **veri setinin eski olduğunu**
söylüyor, motorda bir bozukluk değil:

| bekçi | ne diyor | sebep |
|---|---|---|
| kural kataloğu tam mı | `GECE_UYGUNLUGU` sahnede tanımlı değil | K-40 yeni kuralı ekledi, set 39 kuralla kuruldu |
| her kural kırmızı yanabiliyor mu | 1 kural ihlal vakasında yanmadı | aynı sebep — `GECE_UYGUNLUGU`'nun vakası yok |
| plan temiz mi | `FAZLA_MESAI_TAVANI` sert ihlali | yarı zamanlıların sözleşmesinde hâlâ saat var (20/24); tavan 45 olunca "sözleşme üstü" 10 saati aşıyor |

⚠ **Üçü de bekçilerin görevini yaptığının kanıtı.** Set 28 Eylül'de elle
çalıştırılıyordu ve bu tür kaymalar aylarca görünmez kalıyordu; artık her
push'ta görünüyor.

**Çözümü sıradaki iş:** veri setinin yeniden kurulması (%85 ve %95). Yeni
setin taşıması gerekenler:

* 45 saati taşıyan şablonlar (6×7,5 ya da 5×9) — T-51'in veri tarafı
* yarı zamanlılarda `haftalik_saat` **yok** — K-39
* tam zamanlı sözleşmesinde `gun_sayisi` — K-39
* `gece_vardiyasi` işaretli şablonlar + bazı çalışanlarda `gece_calisamaz` — K-40
* 40 kuralın hepsi + her biri için ihlal vakası

</details>

→ K-38 · K-39 · K-40 · T-51 · T-54 · T-57 · `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py`

---

## ✅ T-57 · ~~Çözücü ile doğrulayıcı "net saat"i farklı hesaplıyor~~ — **KAPANDI (29 Eylül)**

**Çözüm.** Çözücünün `_net_saat`'i artık mola politikasının **tamamını**
düşüyor — doğrulayıcıyla aynı tanım. Politika sahne seviyesindeyse şablona
taşınıyor (yoksa `_net_saat` onu göremezdi). Yanına `_ucret_saat` kondu:
ücret hesabı yalnız **ücretsiz** molayı düşer (K-32'nin dört ayrı süresi).

3 test, üçü de kırmızı başladı; iki mutasyon (yalnız `mola_dk`; yalnız
ücretsiz molalar) ikisi de öldü.

⚠ **Veri setinin şablon aritmetiği de düzeltildi.** Brüt = net + **bütün**
molalar: SATIŞ 9,25/10,75 · BACKOFFICE 8,75/10,25 · MHİZMET 9,00/10,50.
Artık her tam zamanlı şablon tam 7,50 ya da 9,00 net veriyor (6×7,5 = 5×9 = 45).

⚠ **Aynı turda ikinci bir ayrışma çıktı:** K-38 (45 = normal çalışma sınırı)
yalnız **çözücüye** uygulanmıştı; doğrulayıcının `HAFTALIK_AZAMI` kuralı toplamı
hâlâ 45'te kesiyordu ve motorun ürettiği plana 9-13 ihlal yazıyordu. Sınır
artık *normal + fazla mesai tavanı*. 2 test, 2 mutasyon.

<details><summary>ilk kayıt</summary>

### Ölçülen ayrışma

**Bulundu:** 29 Eylül, zor veri seti ilk kez çözüldüğünde. Plan çıktı, ama
bağımsız doğrulayıcı **28 sert `SAAT_DENGESI` ihlali** yazdı.

**Ne.** İki taraf aynı kelimeye farklı anlam veriyor:

| | formül | 8,5 saatlik SATIŞ vardiyası |
|---|---|---|
| **çözücü** `_net_saat(sablon)` | brüt − `mola_dk` | 8,5 − 1,00 = **7,50** |
| **doğrulayıcı** `zaman.net_saat(atama)` | brüt − **bütün molalar** | 8,5 − 1,75 = **6,75** |

Çözücü yalnız **ücretsiz yemeği** düşüyor; doğrulayıcı **ücretli dinlenme
molalarını da** düşüyor. Altı vardiyalık bir haftada fark **4,5 saat**:
çözücü "45 saat oldu" derken doğrulayıcı "40,5" görüyor.

**Hangisi doğru?** Doğrulayıcının tanımı belgeli ve gerekçeli
(`09-motor/dogrulayici/zaman.py`): *"Bir molanın ücretli olması, o sırada iş yapılıyor
olması demek değildir. Ara dinlenme ücretli de olsa çalışma süresinden
düşülür; ücret tarafı AYRI bir büyüktür (`ucret_saat`)."* ⚠ 25 Eylül'de bu
satır bir kez yanlış değiştirilmiş ve geri alınmış — yani karar bilinçli.

**O halde çözücü tarafı yanlış** ve iki sonucu var:

1. `_net_saat` mola politikasının TAMAMINI düşmeli.
2. **Zor veri setinin şablon aritmetiği de yanlış kuruldu.** 45 net saat için
   6 günlük desende brüt = 7,5 + yemek + dinlenme olmalıydı (SATIŞ için
   7,5 + 1,00 + 0,75 = **9,25** saat, 07:00-16:15). Şu an 8,5 yazılı.

**Neden bugüne kadar görülmedi.** İki şey aynı anda değişti:
`SAAT_DENGESI`'nin doğrulayıcı gövdesi bugün yazıldı (K-39) ve eski veri seti
kimseyi sözleşme saatine yaklaştırmıyordu. İkisi olmadan bu ayrışma
görünmezdi — **§7.6'nın tam olarak yakalamak için var olduğu şey.**

⚠ Kapsamı geniş: `GUNLUK_AZAMI`, `HAFTALIK_AZAMI`, `FAZLA_MESAI_TAVANI`,
`PART_TIME_LIMIT`, `SAAT_DENGESI` — hepsi net saate bakıyor. Düzeltme
kırmızı kanıtla ve mutasyonla yapılmalı, aceleye gelmez.

</details>

→ K-32 · K-38 · K-39 · `09-motor/cozucu/model.py` (`_net_saat`,
  `_mola_toplam_dk`) · `09-motor/dogrulayici/kurallar.py` (`haftalik_azami`) ·
  `09-motor/testler/test_net_saat_uyumu.py`

---

## ✅ T-58 · ~~Kesirli vardiya bitişi doğrulayıcıyı çökertıyordu~~ — **KAPANDI (29 Eylül)**

**Bulundu:** zor veri seti ilk kez çözüldüğünde, daha kapıya bağlanmadan.

```
ONAYLI_IZIN -> range(a["gun"], (bit - 1) // 24 + 1)
TypeError: 'float' object cannot be interpreted as an integer
```

K-34 çeyrek saat ızgarasını getirdiğinden beri vardiya bitişi **kesirli**
olabiliyordu (07:00-15:30 gibi); bu kural bitişin tam sayı olduğunu
**varsayıyordu**. Hiçbir test kesirli bitiş kullanmadığı için aylarca
görünmedi. `int(...)` ile düzeltildi, kırmızı kanıtlı test eklendi
(`test_ceyrek_saat.py`).

---

## 🔴 T-59 · Verilen süre bütçesi **aşılıyor** — 900 saniye istendi, 1078 sürdü

**Ölçüldü:** 29 Eylül, Mustafa'nın makinesinde, 500 kişilik tam ölçek.

```
2/3  Cozuluyor... (en fazla 900 sn)
     1078 sn  |  durum: cozuldu  |  2493 atama
     durma: butce_doldu    iki asama: False
```

**Sebep.** `ilk_asama_saniye` (varsayılan **120 sn**) verilen bütçenin
**ÜSTÜNE** ekleniyor, içinden gelmiyor:

```
_ipucu_ver   -> max_time_in_seconds = ilk_asama_saniye   (120)
ana çözüm    -> max_time_in_seconds = azami_saniye       (900)
```

900 + 120 = 1020, artı model kurma 51 sn ≈ **1071** — ölçülen 1078 ile
tutuyor.

**Neden önemli.** K-35 kullanıcıya **süre seçtiriyor** (10/15/30 dakika).
*"15 dakika"* diyen yönetici 18 dakika bekliyor. Bir süre vaadi, vaat
edilen süreden uzun sürüyorsa vaat değildir.

**Önerilen.** Birinci aşama bütçenin **içinden** pay alsın
(ör. `min(ilk_asama_saniye, azami_saniye * 0.2)`), toplam asla
`azami_saniye`yi geçmesin. Model kurma süresi ayrı bir kalem — o da
kullanıcıya ayrıca gösterilmeli.

→ K-35 · `09-motor/cozucu/coz.py` (`_ipucu_ver`, `coz`)

---

## 🔴 T-60 · Tam ölçekte plan **üretiliyor ama optimize edilemiyor** — optimuma %98,3 uzak

**Ölçüldü:** 29 Eylül, 500 kişi, 900 saniye bütçe, Mustafa'nın makinesi
(6 çekirdek).

| | |
|---|---|
| model | 638.572 değişken · 754.633 kısıt · kurma **51 sn** |
| çözüm | 1078 sn, **2493 atama** |
| **optimuma uzaklık** | **%98,3** |
| sert ihlal | **0** · yayınlanabilir **True** |
| yumuşak ihlal | ADALET_DENGESI 157 · HEDEF_KAPSAMA 95 · MOLA_KAPSAMASI 63 |

**⚠ İki yüzü var ve karıştırılmamalı.**

* **Yasal/sözleşmesel taraf tamam:** 0 sert ihlal, plan yayınlanabilir.
  Çözücü ile doğrulayıcı aynı plan hakkinda **anlaşıyor** (T-57 sonrası).
* **Kalite tarafı yok denecek kadar az:** %98,3, *"neredeyse hiçbir şey
  optimize edilmedi"* demektir. Kıyas: eski 350 kişilik set aynı 900
  saniyede **%10** veriyordu.

**Ne değişti.** Set 1,9 kat büyüdü **ve** iki yeni sert kısıt geldi
(`SAAT_DENGESI` her tam zamanlıyı 45 saate çiviliyor, `GECE_UYGUNLUGU`).
Arama alanı hem büyüdü hem daraldı.

**⚠ İki aşama DEVREYE GİRMEDİ** (`iki_asama: False`) — oysa 638 bin
değişken eşiğin (50.000) 12 katı üstünde. Demek ki **birinci aşama
başarısız oldu**: 120 saniyede uygun bir plan bile bulamadı ve `_ipucu_ver`
`False` döndü. Yani bütçenin 120 saniyesi **hiçbir şeye yaramadan** gitti
(T-59 ile aynı kök).

**Sıradaki ölçümler — tahminle değil deneyle:**

1. `ilk_asama_saniye`'yi 300'e çıkar: iki aşama devreye giriyor mu, girerse
   uzaklık düşüyor mu?
2. T-50'nin sorusu bu ölçekte yeniden geçerli: iki aşama açık mı kapalı mı
   daha iyi? (350 kişide **kapalı** daha iyiydi.)
3. `SAAT_DENGESI`'yi geçici olarak yumuşatıp ölç: uzaklığın ne kadarı
   ondan geliyor? (Ürün kararı değil, **teşhis** için.)
4. %85 seti aynı bütçeyle ne veriyor?

⚠ **Karar vermek için henüz yeterli veri yok.** %98,3'ün kabul edilemez
olduğu açık; sebebi açık değil.

→ T-50 · T-54 · T-59 · K-35 · K-39

---

## ✅ T-61 · ~~Nitelik kapsamasında çözücü *"atanmış"*, doğrulayıcı *"sahada"* sayıyor~~ — **KAPANDI (30 Eylül, K-41)**

**Bulundu:** 30 Eylül, `ROL_KAPSAMASI` ve `YETKINLIK_KAPSAMASI` için doğrulayıcı
gövdeleri yazılırken — yani bağımsız denetim ilk kez var olduğu anda.

**Ne.** Şartname §6.4 iki kuralı da **sahada** diye tanımlıyor:

| kural | şartnamenin cümlesi |
|---|---|
| `ROL_KAPSAMASI` | *"Belirli operasyonel rolün her açık saatte **sahada** bulunması"* |
| `YETKINLIK_KAPSAMASI` | *"Belirli saatlerde belirli yetkinliğin **sahada** olması"* |

Çözücü (`09-motor/cozucu/model.py`, `_yetkinlik`) **atama** değişkenini sayıyor —
molayı düşmüyor. Doğrulayıcı gövdesi şartnameden yazıldı, yani **sahadaki** kişiyi
sayıyor. Fark tam olarak mola.

**Ölçülen (3 kişi, 1 gün, tek takım lideri, 8–16 vardiyası):**

Çözücü planı üretti ve **üçünün yemeği de aynı saate düştü** (11:00–12:00) —
`MOLA_YERLESIMI` yumuşak, `SAHADA_ASGARI` bu sahnede yok, yani molaları
kaydıracak bir şey yoktu. O saatte sahada takım lideri kalmadı. Bağımsız denetçi
o saatin **dört çeyreğinde** ihlal yazdı; çözücü kendi ölçüsüne göre kuralı
sağlıyor.

**Hangisi doğru — doğrulayıcı.** Şartname *"sahada"* diyor ve aynı ayrımı
`SAHADA_ASGARI` (K-33) zaten yapıyor. Mustafa'nın o günkü cümlesi: *"Firma molada
en az 5 demeyecek, firma sahada en az 5 diyecek."* Aynı mantık tek bir takım
liderine de uyar: molada olan takım lideri, o an sahada olan takım lideri
değildir.

**T-57'nin aynı ailesi.** Orada da çözücü ile doğrulayıcı aynı kelimeye farklı
anlam veriyordu, doğrulayıcı haklı çıktı ve düzeltilen taraf çözücü oldu.

**Karar Mustafa'da, çünkü bedeli plana yansıyor:**

| seçenek | sonucu |
|---|---|
| çözücü de *"sahada"* sayar | şartnameye uyar; plan **zorlaşır** — nitelikli kişilerin molaları kaydırılmak zorunda |
| kural *"atanmış"* okunur | plan kolaylaşır; şartnamenin iki satırı ve K-33'ün mantığıyla çelişir |

Ayrışma test paketinde **ölçülüyor ve sabitlenmiyor**:
`09-motor/testler/test_nitelik_kapsamasi.py::test_AYRISMA_OLCUMU_cozucu_molayi_dusmuyor`.
Karar verildiğinde o test ya silinir ya tersine çevrilir — K-33'te aynısı yapıldı.

### ✅ Kapanış — 30 Eylül, K-41

Mustafa'nın kararı: **molada olan sayılır.** Değişen taraf **doğrulayıcı** oldu;
çözücü haklıydı.

> *"Sahada bir müdürün işi 15 dk mola süresini bekleyebilir… Zaten mola öneri
>  gibi bir kurgu olacağından bu kadar derine inmemize gerek yok."*

İki test **tersine çevrildi**, silinmedi — gerekçeleri testlerin başında.
`SAHADA_ASGARI` molayı düşmeye devam ediyor; ikisi farklı soru soruyor.

⚠ **Şartname borcu:** §6.4'ün iki satırı hâlâ *"sahada"* diyor, güncellenmeli.
⚠ **Açık kalan:** yasal bayraklı bir satırda molanın sayılması hukuken
tartışılabilir; gerekirse satır bazlı seçenek eklenir.

→ T-57 · T-62 · T-63 · K-33 · K-41 · `09-motor/cozucu/model.py`

---

## ✅ T-62 · ~~Çözücüde nitelik kuralı `saatler` yazılmazsa hiçbir şey kısıtlamıyor; `ekip` yazılmazsa plan çözümsüz~~ — **KAPANDI (30 Eylül)**

**Bulundu:** 30 Eylül, aynı gövdeler yazılırken şartname çözücüyle karşılaştırılınca.

**Birinci yarısı — sessiz hiçlik.** `model.py::_yetkinlik` saat listesini
`p.get("saatler", [])` ile okuyor. Liste **yoksa** iç döngü hiç çalışmıyor: aktif
bir **SERT** kural modele tek bir kısıt koymuyor ve kimse bunu bilmiyor.
Şartname rol kuralını *"her **açık** saatte"* diye tanımlıyor — yani saat listesi
yoksa **bütün açık saatler** geçerli olmalı, hiçbiri değil.

**İkinci yarısı — ters yönde ve daha sinsi.** Aynı fonksiyon uygun kişileri
`p.get("ekip") in (c.get("ekipler") or [])` ile süzüyor. `ekip` yazılmazsa
karşılaştırma `None` ile yapılıyor, hiç kimse uygun sayılmıyor ve modele
*"boş toplam en az 1 olsun"* kısıtı giriyor → **plan çözümsüz**. Yöneticinin
göreceği cümle *"bu talebi bu kadroyla karşılamak imkânsız"* olur; sebebi bir
eksik parametredir.

**Ölçülen (49 kişi, %95 seti, 180 saniye):** her ekibe *"en az 1 takım lideri
sahada"* gerekliliği kondu, `saatler` bilerek verilmedi.

| | gereklilik yok (bugünkü set) | gereklilik var, `saatler` yok |
|---|---|---|
| durum | çözüldü | çözüldü |
| atama | 221 | 221 — **aynı plan** |
| sert ihlal | 0 | **1.238** |
| `yayınlanabilir` | True | **False** |

Çözücü kuralı hiç kısıtlamadan aynı planı üretti; ihlalleri yalnız bağımsız
denetçi gördü.

⚠ **Bu sayının bir kısmı kodun değil ölçeğin sonucu — açıkça yazıyorum.**
0.1 ölçekte ekip başına yalnız **2** takım lideri var, haftalık talep ise
7/24. İki kişi 168 saati kapatamaz. Tam ölçekte 42 takım lideri var; oradaki
gerçek sayı ölçülmedi. Yani 1.238 *"çözücü kuralı görmüyor"*un kanıtıdır,
*"gereklilik imkânsız"*ın ölçüsü değildir.

### ✅ Kapanış — 30 Eylül

Üç şey düzeltildi:

1. `saatler` yoksa **açık saatlerin hepsi** denetlenir (talep hücresi olan her saat).
2. `ekip` yoksa kural **saha çapında** okunur — doğrulayıcı gövdesiyle aynı.
3. Kontrol artık **çeyrek** bazında: 15:30'da biten vardiya saatin son yarısını
   kapatmıyorsa görünür (K-34).

Ve dördüncü, yeni bir davranış: **niteliği taşıyan kimse yoksa kısıt yazılmaz,
not yazılır.** Kısıt yazmak planı sessizce çözümsüz yapardı ve sebebi
görünmezdi; karşılığını doğrulayıcı söyler. *"Yüksek sesle yanlış, sessizce
çözümsüzden iyidir"* (§7.6).

**Üç test.** ⚠ Kırmızı kanıtları **mutasyonla** üretildi, çünkü gövde testlerden
önce yazıldı — kırmızı önce kuralı burada uygulanmadı ve bu kayda geçiyor.

⚠ **Bir test ilk turda mutasyondan sağ kurtuldu ve dersi ağır:** *"kural iki
lider istiyor, ikisi de atanmış mı"* diye soruyordu. Kısıt tamamen
kaldırıldığında test **yine yeşil** kaldı — çünkü fazladan atamanın bir
maliyeti yok (T-54), çözücü iki lideri zaten kendiliğinden atıyordu.
*"Atandı mı"* sorusu bu motorda hiçbir şey kanıtlamıyor. Yerine **imkânsız**
bir gereklilik konuldu: iki lider varken üç lider isteniyor; kısıt yazılıysa
plan çözümsüz kalmak zorunda.

→ T-61 · T-63 · T-54 · `09-motor/cozucu/model.py`

---

## 🟡 T-63 · Veri setinde üç kural aktif ama hiçbir şey istemiyor — **ROL TARAFI KAPANDI (30 Eylül)**

**Bulundu:** 30 Eylül, yeni gövdeler bağlanınca zor veri seti bekçileri
**yeşil kaldı** — ve sebebi araştırılınca.

**Ne.** 500 kişilik sahnede:

| kural | sahnedeki hâli | sonucu |
|---|---|---|
| `ROL_KAPSAMASI` | `parametreler` alanı **yok** | hiçbir rol istenmiyor |
| `YETKINLIK_KAPSAMASI` | `parametreler` alanı **yok** | hiçbir yetkinlik istenmiyor |
| `SAHADA_ASGARI` | `asgari_sahada: 0` | saha tabanı yok |

Üçü de **aktif**. Yani *"40 kuralın hepsi tanımlı"* cümlesi doğru ama
**tanımlı olmak, istemek değildir.** Bekçiler bu yüzden yeşil kaldı: yeni
gövdeler doğru çalışıyor, denetlenecek bir gereklilik yok.

**Veri duruyor, gereklilik yazılmamış.** Sahnedeki 500 kişide
42 takım lideri, 302 agent, 118 kıdemli agent, 38 uzman var; yetkinlikler
`teknik`, `almanca`, `ingilizce`, `iade`.

**Yeni görünürlük — bu bulgunun bir kısmı aynı gün kapandı.**
`eksik_boyutlar` kanalı artık parametresiz gereklilik satırını bildiriyor:
*"gereklilik satırında `rol` yazılı değil; hangi niteliğin arandığı bilinmiyor
— denetlenemedi."* Yani bundan sonra sessiz kalmıyor. Kanal hâlâ yalnız
**rapor**; yayın kapısının ona ne yapacağı T-18.

⚠ **29 Eylül'ün dersi burada tekrar ediyor, bu kez veri tarafında.** Dün kod
tarafında *"39 kuralın hepsi uygulanıyor"* yazmıştım, 15'inin gövdesi yoktu.
Bugün *"40 kuralın hepsi tanımlı"* yazıyor, üçü hiçbir şey istemiyor.
**Sayı saymak yetmiyor; sayılan şeyin ne işe yaradığına bakmak gerekiyor.**

### ✅ Rol tarafı kapandı — 30 Eylül, Mustafa'nın seçimi

> *"Yalnız gündüz saatlerinde 1 lider."*

Sahneye **her ekip için ayrı bir gereklilik satırı** kondu (K-24: bu kuralda
gereklilik satır bazlıdır): `takim_lideri`, asgari 1, saatler **08:00–20:00**.
Ticari tercih olduğu için `yasal` değil, **kabul edilebilir** işaretli.

⚠ **Saat aralığı benim seçimim, Mustafa saat vermedi.** Gündüz 08:00–20:00
alındı; gece postasında takım lideri zorunlu değil.

### ⚠ Gereklilik konunca sahne ÇÖZÜMSÜZ kaldı — ve sebebi ölçek çıktı

İlk deneme: 0.1 ölçekte plan **kanıtlanarak** çözümsüz (`teshis_kesin` True,
zaman aşımı değil). Sayarak:

| | |
|---|---|
| gündüz penceresi | 12 saat; en uzun vardiya ~10,5 saat → günü kapatmak için **2 lider** |
| hafta | 2 × 7 = **14 lider-günü** gerekiyor |
| eldeki | 2 lider × 6 gün (`HAFTA_TATILI`) = **12 lider-günü** |

Yani gereklilik değil **ölçek** imkânsızdı: rol dağılımı %8 lider veriyor,
500 kişide 21/15/6 ediyor ama 0.1 ölçekte 2/2/**0**.

⚠ **Yalnız sayıyı 4'e çıkarmak YETMEDİ** — 323 saniye sonra yine çözümsüz.
Promosyon yarı zamanlıya ya da izinliye denk gelince plan tutmuyor. Taban
*"4 kişi"* değil, **"gündüz vardiyası yazılabilecek 4 kişi"**: tam zamanlı,
aktif, izinsiz. O hâliyle sahne **79 saniyede** çözüldü.

**Konulan:** üreticide ekip başına **4 lider tabanı** (tam zamanlı, aktif,
izinsiz adaylardan). Tam ölçekte hiçbir şey değişmiyor (21/15/6 tabanı zaten
aşıyor); 0.1 ölçekte 5/5/4 oluyor.

⚠ **Küçük ölçekte bu oranı bozuyor:** 7 kişilik ekipte 4 lider, kişilerin
yarısından fazlası demek. Gerçekçi değil — ama 7 kişiyle 7/24 kapsama da
gerçekçi değil; o sahne zaten bir küçültme yapısıdır. Alternatifi, firmanın
kendi kuralını tutamayan bir veri seti olurdu.

**Bekçiler yeşil:** 12 test. İhlal vakası artık gerekliliği kendisi yazmıyor,
yalnız **planı** bozuyor — bir günün liderlerini plandan çıkarıyor.

### 🟡 Açık kalan

* **Yetkinlik tarafı.** `YETKINLIK_KAPSAMASI` hâlâ parametresiz. Veri duruyor
  (`teknik`, `almanca`, `ingilizce`, `iade`); gereklilik karara bağlanmadı.
  Sessiz değil: `eksik_boyutlar` kanalı *"hangi niteliğin arandığı bilinmiyor
  — denetlenemedi"* diye bildiriyor.
* **`SAHADA_ASGARI` hâlâ 0.** Saha tabanı yok.
* **Tam ölçekte gereklilik ölçülmedi.** 0.1'de çözülüyor; 500 kişide
  (21/15/6 lider) sayı elverişli görünüyor ama **koşulmadı**.

→ T-61 · T-62 · T-18 · K-24 · K-41 ·
  `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py`

---

## ✅ T-64 · İhlal vakası aracı kendi listesini sayıyordu — **KAPANDI (30 Eylül, aynı gün)**

**Ne.** Araç özeti `basarili / len(VAKALAR)` yazıyordu: *"yazdığım vakaların kaçı
ateşledi."* Gövdesi yazılı ama **vakası olmayan** bir kural bu paydada hiç
görünmüyordu. Yani araç *"EKSIK: 0"* diyebiliyordu ve bu *"her kural sınandı"*
demek değildi.

⚠ **29 Eylül'de yazdığım cümlenin dayanağı buydu:** *"gövdesi yazılı 26 kuralın
tamamı kendi vakasında kırmızı yanıyor, eksik sıfır."* Cümle doğruydu ama
sorduğu soru yanlıştı — araç kendi kapsamasını ölçemiyordu.

**Bugün görüldü:** iki yeni gövde yazıldı, vakaları yoktu, araç *"EKSIK: 0"*
demeye devam etti.

**Düzeltildi.** Evren artık doğrulayıcının `KAYIT` sözlüğü: gövdesi yazılı her
kural. Vakası olmayan gövde ayrı bir satır olarak *"VAKASI YOK — hiç sınanmadı"*
diye yazılıyor ve `eksik` sayısına giriyor. Özet üç sayıyı ayrı gösteriyor:
gövde sayısı, vakası olan, kırmızı yanan.

Bekçisi `test_HER_KURAL_kirmizi_yanabiliyor`; eşik 26'dan **28**'e çıkarıldı ve
`eksik == 0` iddiası artık gerçekten kapsama ölçüyor.

**Ölçülen:** 28 gövde · 28 vaka · 28 kırmızı · eksik sıfır.

⚠ **Ölçen aracın da bekçisi olmalı — bu oturumda ikinci kez.** İlki çekirdek
ölçüm aracıydı (tek koşuyu genel kural saymak, `--tekrar` eklendi), bu ikincisi.
İkisinin ortak dersi: **aracın kendi payını kim denetliyor?**

→ T-61 · `08-motor-testleri/gercekci-veri-seti/ihlal-vakalari.py`

---

## ✅ T-65 · ~~Motorun kendi kapsama metriği kesirli vardiya bitişini kırpıyordu~~ — **KAPANDI (30 Eylül, aynı gün)**

**Bulundu:** 30 Eylül, **CI kırmızı yandı.** Mustafa'nın koşumu:

```
sert_ihlal: 0   ·   asgari_kapsama_yuzde: 99.76
```

İlk bakışta çelişki gibi duruyor — `ASGARI_KAPSAMA` SERT bir kural, ihlal yoksa
kapsama %100 olmalı. **Çelişki değil:** iki sayının ikisi de motorun **kendi**
raporundan geliyor ve ikisi de yanıltıcı.

### Sebep

`09-motor/cozucu/coz.py::_metrikler` kapsamayı şöyle sayıyordu:

```python
range(a["gun"] * 24 + int(a["bas"]), a["gun"] * 24 + int(a["bit"]))
```

Vardiya 07:00–16:15 ise `int(16.25)` = 16 ve `range(7, 16)` **saat 16'yı
dışarıda bırakıyor**. Oysa vardiya 16:00–16:15 arası sahada ve kısıt tarafı
(`_atanmis` → `_dilimler` → `_q`) o çeyreği sayıyor. Yani **kısıt sağlanmış,
metrik "kapanmadı" diyor.**

K-34 çeyrek ızgarasından beri şablonların çoğu kesirli bitiyor (16.25, 16.75,
18.25, 18.75, 20.25…) — yani bu kırpma istisna değil **kural**. 415 talep
hücreli sahnede **bir** hücre bu yüzden eksik sayıldı: 414/415 = %99,76.

### ⚠ T-58 ile aynı aile — ve aynı hata iki yerde duruyordu

29 Eylül'de kesirli vardiya bitişi **doğrulayıcıyı çökertiyordu** (`range()`e
float gidiyordu) ve orada düzeltildi. Çözücüdeki bu **kopyasına kimse bakmadı.**
Şartname §7.6 iki tarafı bilerek ayırıyor; bedeli de bu: bir hatayı bulmak, onu
**iki yerde** aramak demek.

### Neden benim makinemde geçti, CI'da yandı

Hangi hücrenin eksik sayılacağı **plana** bağlı. Benim koşumda her hücreyi
`int(bit)`'i o saati hâlâ kapsayan biri örtüyordu; CI'nın 2 çekirdekli
makinesinde çözücü başka bir plan buldu ve bir hücre açıkta kaldı.
⚠ Yani test **rastgele** yeşil yanıyordu. Bulunması Mustafa'nın koşumuna kaldı.

### Düzeltildi

Karşılaştırma artık mutlak zamanda ve **kesirli** yapılıyor — doğrulayıcının
`zaman.atanmis_mi`si de böyle çalışıyor. Üç test
(`09-motor/testler/test_motor_metrigi.py`), ikisi kırmızı başladı; mutasyon
(`int()` geri kondu) ikisini birden öldürdü.

**Bekçi de değişti:** `test_KUCULTULMUS_olcekte_kapsama_TAM` artık motorun
kendi sayısına değil **doğrulayıcının** sayısına bakıyor, ve ayrıca ikisinin
**anlaştığını** sınıyor. Komşu test (`test_TAM_ZAMANLI_sozlesme_saatini_DOLDURUYOR`)
bu dersi zaten öğrenmişti; burada atlanmıştı.

→ T-58 · T-66 · `09-motor/cozucu/coz.py` · `09-motor/testler/test_motor_metrigi.py`

---

## 🟡 T-66 · `sert_ihlal` ölçülmüyor, **sabit yazılıyor**

**Bulundu:** 30 Eylül, T-65 araştırılırken — yanındaki satırda.

`coz.py::_metrikler` şunu döndürüyor:

```python
"sert_ihlal": 0,   # kisitlar sert; cozum varsa hepsi saglanmistir
```

**Cümle mantık olarak doğru** ama alan adı bir **ölçüm** vaat ediyor. Ekranda
*"0 sert ihlal"* yazdığında yönetici bunu sayılmış sanır. Sayılmadı.

**İki ayrı sınırı var:**

1. Yalnız **motorun kendi kurduğu** kısıtları kapsar. Gövdesi yalnız
   doğrulayıcıda olan bir kural — ya da gövdesi hiç yazılmamış **12** kural —
   bu sıfıra girmez.
2. Sıfır, *"ihlal yok"* değil *"kendi kısıtlarımı çiğnemedim"* demek. T-65'in
   yanıltıcı çifti (*"sert ihlal 0, kapsama %99,76"*) tam olarak bu yüzden
   mümkün oldu.

Gerçek sayı `dogrulayici.degerlendir`den gelir ve bekçiler 30 Eylül'den beri
oraya bakıyor. Ama **çıktı sözleşmesi (§11.3) hâlâ bu alanı barındırıyor** ve
ekranı yazan taraf onu okuyacak.

**Karar Mustafa'da** (§11.3 değişir): alan kaldırılsın mı, adı değişsin mi
(*"kendi_kisitlarim"* gibi), yoksa yanında *"ölçülmedi"* diyen bir kardeş alan
mı dursun. Motorun kendi metriğinin var olma sebebi doğrulayıcıyla
**karşılaştırılmak**; karşılaştırılamayan bir sayı o işi yapmıyor.

→ T-65 · T-18 · `09-motor/cozucu/coz.py` · `02-spec/v1.4-master-spec.md` §11.3

---

## 🟡 T-67 · `GECE_YARISI_ASAN` "gövdesiz" sayılıyor ama şartnameye göre ihlal üretmez

**Bulundu:** 30 Eylül, kalan gövdesiz kurallar tek tek okunurken.

Şartname §6.3 satırı açık: *"Bitişi başlangıcından küçük olan vardiya ertesi
güne taşar. **Hesaplama kuralı, ihlal üretmez.**"* Zaman modeli (Z-1…Z-7) bu
hesabı zaten yapıyor — `zaman.aralik` Z-1'i uyguluyor.

Yani bu kural *"yazılmamış"* değil *"bilerek gövdesiz"*. Ama sayımlarımızda,
veri setinde ve `uygulanmayan_kurallar` kanalında **eksik** diye görünüyor.
Gerçek eksik sayısı 11 değil **10**.

⚠ **Düzeltmesi basit değil:** ona boş bir gövde yazmak doğruyu söyler ama ihlal
vakası aracı artık her gövdeden bir kırmızı bekliyor (T-64) — bu kural için
kırmızı **tanım gereği imkânsız**. Araca *"bilerek sessiz"* diye bir sınıf
eklemek gerekiyor. Küçük ama ayrı bir iş.

→ T-64 · `02-spec/v1.4-master-spec.md` §6.3

---

## 🟡 T-68 · Çözücü gece sınırını **brüt** ölçüyor — doğrulayıcıdan bilerek daha katı

**Bulundu değil, bilerek seçildi:** 30 Eylül, `GECE_VARDIYASI_AZAMI` yazılırken.
Kayda geçiyor çünkü iki taraf aynı kuralı **farklı ölçüyor** ve bu T-57 / T-61
ailesinden — bu kez bilinçli.

| taraf | ölçü |
|---|---|
| doğrulayıcı | gece penceresine düşen **net** çalışma (penceredeki mola düşülür) |
| çözücü | şablonun penceresine düşen **brüt** saat |

**Neden:** net ölçü molanın **nereye** düştüğüne bağlı ve mola yeri bir karar
değişkeni. Onu kısıtlamak kişi × gece × çeyrek kadar terim demek — 500 kişide
on binlerce. T-60'a göre model zaten optimuma %98,3 uzak; ona yük eklemek bugün
yanlış yön.

**Bedeli:** brütü 8, penceresindeki molayla neti 7 saat olan bir şablon
çözücüde **yasaklanır** — oysa yasaldır. Yani çözücü yasal bir planı
**reddedebilir**, ama hiçbir zaman yasadışı plan **üretmez**. Ayrışma güvenli
yönde, ve olduğunda sessiz değil: çözücü not yazıyor.

**Bugün etkisi yok:** veri setinde brüt örtüşmesi 7,5'i aşan şablon yok.

**İkinci boşluk — iki vardiya aynı pencereyi paylaşırsa.** Çözücü **şablon
başına** bakıyor, doğrulayıcı **pencere başına toplar.** Pazartesi 16:00–24:00
+ Salı 00:00–06:00 aynı geceye 10 saat yazar. `VARDIYA_ARASI_DINLENME` aktifken
imkânsız (11 saat ara gerekir); kapatılırsa iki taraf ayrışır ve **doğrulayıcı
görür**.

**Ne zaman ele alınmalı:** gerçek müşteri şablonları geldiğinde. Seyahat
acentesi verisinde 182 atama gece yarısını aşıyor; o şablonların brüt/net farkı
ölçülmeden karar verilemez.

→ K-26 · T-60 · T-61 · `09-motor/cozucu/model.py`

---

## 🟡 T-69 · İşaretsiz erken saatli vardiya iki tarafta da **gece sayılmıyor**

**Bulundu:** 30 Eylül, geçmiş veri yazılırken — iki motor yarısının gece
tespiti yan yana denenince.

| vardiya (işaretsiz) | çözücü | doğrulayıcı | doğrusu |
|---|---|---|---|
| 00:00–08:45 | gece değil | gece değil | 00:00–06:00 gece penceresinde |
| 04:00–12:00 | gece değil | gece değil | 04:00–06:00 gece penceresinde |
| 23:00–08:15 | gece | gece | gece |

İki taraf da tahmini yalnız **aynı günün** 20:00–06:00 penceresine bakarak
yapıyor; bir önceki gecenin 00:00–06:00 kısmını görmüyor. **İkisi tutarlı,
ikisi de yanlış** — T-19'un ailesi; bağımsız denetim tam bu yüzden yakalayamaz.

**Bugün etkisi yok:** veri setinde gece şablonlarının hepsi **işaretli** (K-40
— işaret tahmini ezer), B-GECE (00:00–08:45) işaretli olduğu için doğru.

**Neden artık önemli:** PDKS kaydının şablonu ve işareti yok. Geçmişte
pazar 00:00–08:00 çalışmış biri ardışık gece sayımında **görünmez**.
Düzeltme iki tarafta da ayrı yazılmalı ve altın senaryolarla sınanmalı —
işaretsiz şablonu olan fikstürlerin sonucu değişebilir.

→ K-40 · T-28 · `09-motor/cozucu/model.py` · `09-motor/dogrulayici/kurallar.py`

---

## ✅ T-70 · Mutasyon denemeleri **eski bytecode** ile koşabiliyordu — **KAPANDI (30 Eylül, aynı gün)**

**Bulundu:** 30 Eylül, doğru bir test kırmızı yandığında.

**Ne.** Python derlenmiş kodu (`__pycache__`) geçerli sayarken kaynağın
**değişiklik zamanına (saniye)** ve **boyutuna** bakar. Mutasyonların çoğu
**aynı uzunlukta** bir değişiklik (`plan_geceler` → `plan_gunleri`, ikisi de
12 harf) ve dosya **aynı saniyede** geri yazılıyor. Sonuç: mutasyonlu bytecode
özgün kaynak için de geçerli sayıldı. Diskteki kod doğruydu, Python on ikinci
mutasyonun kodunu çalıştırıyordu, doğru bir test kırmızı yandı.

⚠ **Ters yön de mümkündü:** bir mutasyon bir öncekinin bytecode'uyla koşup
sahte *"öldü"* ya da sahte *"yaşadı"* verebilirdi. Yani bu oturumdaki **bütün
mutasyon sonuçları** şüpheliydi.

**Düzeltildi:** `09-motor/mutasyon_kostur.py` — her koşudan önce önbellek
silinir, bytecode hiç yazılmaz, özgün kod **başta ve sonda** yeşil olmak
zorunda, her mutasyondan sonra dosya md5 ile doğrulanır, çapası bulunmayan
mutasyon *"ATLANDI"* yazar.

**Yeniden doğrulandı:** bu oturumun bütün mutasyonları (nitelik kapsaması,
motor metriği, gece sınırı, firma sınırları, geçmiş veri) — **42 mutasyon,
42'si de öldü, atlanan yok.** Önceki sonuçlar geçerliydi; tuzak yalnız son
geri yazmada ısırmıştı.

**Yan kazanç:** A-6 (*"otomatik mutasyon hâlâ yok"*) için ilk adım — elle
seçilmiş ama **tekrarlanabilir** bozmalar. CI'a konmadı (süre bütçesi).

→ A-6 · `09-motor/mutasyon_kostur.py`

---

## Öncelik sırası — önerilen

**Sıralama ölçütü: yanlış karar riski.** Önce yanlış yayın izni, yanlış
*"çözümsüz"* açıklaması ve yanlış personel sayımı; sonra hız ve kolaylık.

### Önce bunlar — yanlış karar ürettirenler

| Sıra | Madde | Gerekçe |
|---|---|---|
| ~~1~~ | ~~**T-28 · geçmiş vardiyalar okunmuyor**~~ | ✅ **KAPANDI 30 Eylül, K-42** — ölçüldü: geçmişsiz 27 yasal ihlal, geçmişle 0 |
| **2** | **T-38 · şartnamenin 12 alanı karşılıksız** 🔴⚠ | ⚠ **Seviyesi şüpheli.** İki ağır satırı da 25 Eylül'de kapsam kararına bağlandı (K-21 geri alındı, K-31 verildi). Kalanlar yazılmamış özellik ve ad uyuşmazlığı — **ölçüme göre 🟡**, onay bekliyor |
| **3** | **T-29 · `DONMUS_GUN` ölü** 🔴 | *"Geçmiş yeniden planlanamaz"* sözünün tek bekçisi hiç ateşlenemiyor |
| **4** | **T-21 · çok ekipli çalışan** 🔴 | Modelin kendi inancı yanlış: bir kişi iki ekibi birden dolduruyor |
| **5** | **T-18 · yayın kapısı** 🔴 | *"Kontrol edemedim"* ile *"yayınlanabilir"* aynı cevapta — artık **üç** kanal bu kapıda bekliyor |
| **6** | **T-59 · süre bütçesi aşılıyor** 🔴 | K-35 kullanıcıya bir süre **söz veriyor**; 900 saniye istenen koşu 1.078 sürdü. **Karar gerektirmiyor**, mekanik |
| **7** | **T-60 · tam ölçekte kalite yok** 🔴 | Plan yasal çıkıyor, optimuma **%98,3** uzak. Yönetici *"motor kötü plan yapıyor"* der. ⚠ Sebebi henüz ayrılmadı — önce dört ölçüm |
| **8** | **T-54 · saatin maliyeti yok** 🔴 | Çözücü fazladan saat yazmaktan çekinmiyor: %85 dolulukta 49 kişiye 124 saat fazla mesai. ✅ **Mustafa'nın kararı** — `HEDEF_ASIMI` gibi yumuşak bir kural mı, ücret terimi mi |
| ~~9~~ | ~~**T-62 · nitelik kuralı çözücüde sessiz**~~ | ✅ **KAPANDI 30 Eylül** — saat listesi yoksa açık saatlerin hepsi; ekip yoksa saha çapı; nitelik taşıyan yoksa not |
| ~~10~~ | ~~**T-61 · atanmış mı, sahada mı**~~ | ✅ **KAPANDI 30 Eylül, K-41** — molada olan sayılır; değişen taraf doğrulayıcı oldu |
| **9** | **T-63 · yetkinlik gerekliliği yok** 🟡 | Rol tarafı kapandı (gündüz 1 lider). Yetkinlik kapsaması hâlâ parametresiz, `SAHADA_ASGARI` hâlâ 0. ✅ **Mustafa'nın kararı** |
| **9b** | **T-66 · `sert_ihlal` ölçülmüyor** 🟡 | Sabit sıfır yazılıyor; ekranda ölçüm gibi görünüyor. ✅ **Mustafa'nın kararı** — §11.3 çıktı sözleşmesi değişir |

### Sonra — doğruluğu değil, güveni bozanlar

| Sıra | Madde | Gerekçe |
|---|---|---|
| ~~10~~ | ~~**T-23 · "süre yetmedi" ≠ "imkânsız"**~~ | ✅ **KAPANDI 29 Eylül, K-37** — `UNKNOWN` artık `sure_yetmedi` diyor, o yolda teşhis koşmuyor |
| 11 | **T-24 · K-28 durgunluk + süre bütçesi** | Karar yazılmamış; bütçe isteğin tamamını kapsamıyor (0,05 sn → 57 sn) |
| 12 | **T-39 · aynı hücre iki talep satırı** 🟡 | Sözleşme sessiz: yinelenen hücre iki kez sayılır, hangi `asgari` geçerli tanımsız. **Talep ekranından önce** karara bağlanmalı |
| 13 | **T-40 · `tercih_karsilama_yuzde` yetim** 🟡 | Şartname çıktıda yazıyor, motor üretmiyor; A7 onsuz yeşil |
| 14 | **T-42 · §11.2 örneği §5.2 ile çelişiyor** 🟡 | `kural_degerleri` örneği şartnamenin kendi yasakladığı iki `S` kapsamlı kuralla yazılmış. Taşıyıcı biçim sorunu T-43 ile çözüldü |
| 15 | **T-41 · DENETIM uyarılarının 13'ü kalıcı** 🟡 | Düzeltilemeyen ile iş düşen aynı listede; uyarı bloğu okunmaz hale gelir (O-7) |
| 16 | **T-30 · T-31 · T-32 · T-33** 🟡 | Hafta tatili · adalet penceresi · tavan uyuşmazlığı · yarım saatler. **T-32'yi bugün ben açtım** (K-30) |
| 17 | **T-36** 🟡 | Eşzamanlı oturum yenilemesi yarışı *(`04-kod`)* |
| 18 | **T-26 · kayıt ≠ yürürlük** | K-28'i kimse yakalamadı. Bekçisi olmayan kararlar için kontrol yok |
| 19 | **T-20 · M0 kapsamı** | A-1'i kapatan test. Doğrulanmalı |
| 20 | **T-25 · tek iş parçacıklı servis** | Tek satırlık düzeltme; pilot öncesi. **Karar gerektirmiyor** |
| 21 | **T-13 · `ADALET_DENGESI`'nin `saat` boyutu** | K-27 sayı eşiğini verdi; süre boyutu açık |

### Ondan sonra — yeni iş

| Sıra | Madde | Gerekçe |
|---|---|---|
| 22 | **`/suggest`** (§11.5) | Motorun yazılmamış tek ucu. ⚠ Kabul ölçütü yok, fikstürü yok — önce cümleler yazılıp onaylanmalı |
| 23 | **A-5** zaman modeli testleri | 182 gerçek gece-yarısı ataması var; A4 yeşil ama gerçek veriyle koşulmadı |
| 24 | **A-6** mutasyon raporu | 16 Eylül kırmızı kanıt turu 12/12 yakaladı ama yalnız **elle seçilen** kırılmalarda. Otomatik mutasyon hâlâ yok |
| 25 | **A-2**, **A-3** eksik bekçiler | Küçük, tanımlı |
| 26 | **A-13 · kapsam envanteri** | Ocak hedefi hâlâ ölçülmedi. Ayrı pencere işi |
| 27 | Eksik 14 senaryo sınıfı (G02–G04, G07–G14, G16, G20) | `04-TEST-HARITASI.md` kapsama tablosu |
| 28 | **A-16** hukuk teyidi | Sahaya çıkmadan önce; işi bloke etmiyor |
| 29 | **A-7** eşzamanlılık | Plan editörünün önkoşulu |
| 30 | **A-9** KVKK | Gerçek veriden önce |
| 31 | **A-8** PgBouncer | Barındırma kararıyla birlikte |

> **Yeni özellikten önce bu liste.** Dış incelemenin sözü: *"önce yanlış yayın
> izni ve sessiz veri atlama sorunları değerlendirilsin, ardından tamamlanma
> tablosu gerçek test kapsamıyla eşleştirilsin."* Katılıyoruz.


> **16 Eylül'de kapanan beş iş:** fikstürler · test iskeleti · **şartname v1.4**
> (A-15) · **bağımsız doğrulayıcı** · **çözücü + onarım döngüsü** (`09-motor/`).
>
> **Yedi altın senaryo koşuyor ve yeşil** (A1, A3, A4, A6, A7, A8, A9).
> Dört tanesi (A2, A10, A11, A12) backend tarafında ve **bu pakette
> koşmuyor** — `.cs.taslak`, çalıştırılabilir test değil. A5 ertelendi
> (K-12). `12 passed` sayısı bu yedi senaryo + paketin kendi beş sağlık
> testidir.
>
> ⚠ **Düzeltme (16 Eylül, dış inceleme):** daha önce burada *"on iki altın
> senaryonun tamamı yeşil"* yazıyordu. **Yanlıştı.** `12 passed` ile
> "12 senaryo yeşil" karıştırılmıştı. Çift tıklama (A10), geçmiş veri (A11)
> ve plan kopyalama (A12) **hiç sınanmadı**.

### Kapanan maddeler

| Madde | Kapanış | Neyle |
|---|---|---|
| A-1 K-9'un bekçisi yok | 12 Eylül 2026 | `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` |
| A-14 gerçek veri yok | 13–14 Eylül 2026 | 3,5 aylık PDKS + plan analiz edildi, 529 ihlal bulundu |
| **A-4 CI yok** | **14 Eylül 2026** | **GitHub Actions koştu ve yeşil yandı** |
| **A-15 şartname v1.4** | **16 Eylül 2026** | **`02-spec/v1.4-master-spec.md` — 35 kural sınıflandırıldı, 11 tutarsızlık düzeltildi** |
| **A-17 adalet eşiği** | **16 Eylül 2026** | **K-27: eşik 2, ortalamadan sapma. Doğrulayıcıda yazıldı, 8 testle sabitlendi** |
| **T-12 adalet kuralı yazılmadı** | **16 Eylül 2026** | K-27 geldi, doğrulayıcıda yazıldı |
| **T-14 şablonun günü yok** | **16 Eylül 2026** | `shift_templates.gunler` — A9'u kırmızı tutan şeydi, deneyle kanıtlandı |
| **A-18 çözücü yok** | **16 Eylül 2026** | `09-motor/cozucu/` + `09-motor/orkestra.py`. Yedi altın senaryo koşuyor ve yeşil; dördü backend tarafında |
| **T-15 fazla mesai ayarı** | **16 Eylül 2026** | K-30: hedef için asla, asgari zorlarsa minimum. Kod değişmedi — mevcut davranış zaten buymuş, üç testle çivilendi |
| **Motor CI'ya bağlı değil** | **16 Eylül 2026** | `motor` işi eklendi, **ilk koşu yeşil** (`47c7050`). Kapının kendi kırmızı kanıtı da yapıldı |
| **T-35 kurulum çapında kilitlenme** | **23 Eylül 2026** | Gerçek istemci IP'si + güvenilen **tek adres**. 3 test + iki turlu uçtan uca elle ölçüm. İlk yapılandırma yanlıştı, elle deneme yakaladı (O-11) |
| **T-34 sırlar varsayılana düşüyordu** | **23 Eylül 2026** | Beş katmanda 16 yer temizlendi; `Sirlar.Zorunlu()`. Kırmızı kanıt CI dalında kalıcı. 3 test |
| **T-19 şartname talep biçimi** | **23 Eylül 2026** | Şartname kazandı; talep beş yerde hücre başına okunuyor. Okunmayan girdi alanları için `okunmayan_alanlar` kanalı açıldı. 5 test, beşi de kırmızı yandı. Aynı turda T-38, T-39 ve T-26'nın ikinci kanıtı bulundu |
| **T-22 denetlenmeyen taslak** | **23 Eylül 2026** | Çözümsüzlükte sunulan plan artık özgün girdiyle denetleniyor; boş plan `var: False`. 4 test. A03'te T-18'i görünür kıldı |
| **T-27 olmayan mola** | **16 Eylül 2026** | Mola vardiyaya kırpılıyor + üst üste binenler birleşiyor. 8 test. Dış incelemenin 1 numaralı bulgusu |
| **T-17 Actions eylemleri** | **16 Eylül 2026** | checkout v7, setup-python v7, setup-dotnet v6. Önce `ci/node24` dalında denendi, yeşil görülünce `main`'e alındı |
