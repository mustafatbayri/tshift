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
| **opencode** — paralel ikinci ajan *(15 Eylül)* | İkinci **yazıcı** ajan R5'i (*iki pencere yazar, sürüklenme*) yeniden açar; R5 kapalı ve açacak ölçülmüş gerekçe yok. **Salt-okunur inceleyici** olarak değerli — ama bugün inceletilecek bitmiş iş yok: motor yazılmadı, A1–A12 onaylanmadı, fikstürler yazılmadı. Motorun bağımsız doğrulayıcısı (M-09) yazıldığında yeniden bakılacak, **iki haftalık ölçüm şartıyla**: on incelemede kayda değer bulgu yoksa bırakılır. Tam gerekçe: `oturumlar/2026-09-15-calisma-bicimi-opencode.md` |

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

## Öncelik sırası — önerilen

| Sıra | Madde | Gerekçe |
|---|---|---|
| **1** | **CI kapısının ilk koşusunu görmek** | `motor` işi eklendi ama **henüz koşmadı**. Yeşil yanana kadar kanıt yok |
| 2 | **T-13 · `ADALET_DENGESI`'nin `saat` boyutu** | K-27 sayı eşiğini verdi; süre boyutu açık. `SAAT_DENGESI` ile örtüşme de bakılmalı |
| 3 | **`/suggest`** (§11.5) | Motorun yazılmamış tek ucu; bilerek 501 dönüyor |
| 4 | **A-5** zaman modeli testleri | 182 gerçek gece-yarısı ataması var; A4 yeşil ama gerçek veriyle koşulmadı |
| 5 | **A-6** mutasyon raporu | 16 Eylül kırmızı kanıt turu 12/12 yakaladı ama yalnız **elle seçilen** kırılmalarda. Otomatik mutasyon hâlâ yok |
| 6 | **A-2**, **A-3** eksik bekçiler | Küçük, tanımlı |
| 7 | **A-16** hukuk teyidi | Sahaya çıkmadan önce; işi bloke etmiyor |
| 8 | Eksik 14 senaryo sınıfı (G02–G04, G07–G14, G16, G20) | `04-TEST-HARITASI.md` kapsama tablosu |
| 9 | **A-13** kapsam envanteri | Ocak hedefi hâlâ ölçülmedi |
| 10 | **A-7** eşzamanlılık | Plan editörünün önkoşulu |
| 11 | **A-9** KVKK | Gerçek veriden önce |
| 12 | **A-8** PgBouncer | Barındırma kararıyla birlikte |

> **16 Eylül'de kapanan beş iş:** fikstürler · test iskeleti · **şartname v1.4**
> (A-15) · **bağımsız doğrulayıcı** · **çözücü + onarım döngüsü** (`09-motor/`).
>
> **On iki altın senaryonun tamamı yeşil** (A5 ertelendi, dört backend
> senaryosu xUnit tarafında). Birim testi 60. Kırmızı kanıt turunda 12
> kırılmanın 12'si yakalandı — ilk turda 8'de 4'ü kaçmıştı, eksik testler
> o yüzden yazıldı (`09-motor/testler/test_profiller.py`).

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
| **A-18 çözücü yok** | **16 Eylül 2026** | `09-motor/cozucu/` + `09-motor/orkestra.py`. On iki altın senaryonun tamamı yeşil |
| **T-15 fazla mesai ayarı** | **16 Eylül 2026** | K-30: hedef için asla, asgari zorlarsa minimum. Kod değişmedi — mevcut davranış zaten buymuş, üç testle çivilendi |
