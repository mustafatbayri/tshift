# AÇIK RİSKLER

**Bilinen ama henüz kapatılmamış** maddeler. Kanıtı olmayan her şey buraya
yazılır — `00`–`05` arası dosyalar yalnız **kanıtlanmış** bilgiyi taşır.

**Son güncelleme:** 2026-09-12

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
`0 - Baglanan rol super kullanici degil` adlı bir test olduğunu yazıyor.

**Bulgu (12 Eylül):** **Böyle bir test yok.** Ne `MimariTestleri` içinde, ne
`CokKiracilikTestleri` içinde, ne `YALITIM-KANITI.ps1` betiğinde. Test
dosyaları bağlantı dizesinde `tshift_app` **kullanıyor** — ama o rolün
gerçekten `NOSUPERUSER`/`NOBYPASSRLS` olduğunu **kimse doğrulamıyor**.

**Neden kritik:** Bu, projedeki **en ciddi hatanın** (O-1) tekrar etme
yoludur. Biri `db/rls/02-uygulama-rolu.sql` betiğini değiştirse, ya da yeni
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

**Ne:** 38 test yeşil. Ama bu testlerin kodu **kasten bozsak** fark edip
etmeyeceğini bilmiyoruz.

**Neden kritik:** "38 test var" ile "38 test bir şeyi koruyor" aynı şey değil.
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

## 🔴 A-5 · Zaman modeli hiç sınanmıyor (G-6)

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

## 🟡 A-10 · Motor sözleşmesi yazılmadı

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

## 📌 Araç kararı (12 Eylül) — ne kullanılacak, ne kullanılmayacak

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

**İlke:** Her araç bir bakım yüküdür. Yanlış alarm veren araç, bir süre sonra
bakılmayan araca dönüşür (bkz. O-7). Kullanılan araç sayısı değil, kapatılan
açık sayısı ölçülür.

---

## 🔴 A-13 · Kapsam envanteri yapılmadı — Ocak hedefi ölçülmedi

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

## Öncelik sırası — önerilen

| Sıra | Madde | Gerekçe |
|---|---|---|
| **1** | **A-10 motor sözleşmesi** | Gerçek veri geldi; motorun neye göre yazılacağı artık biliniyor. V01–V12 + mola modeli + UNSAT biçimi. |
| 2 | **A-5** zaman modeli testleri | 182 gerçek gece-yarısı ataması var; motor yazılmadan kapatmak ucuz |
| 3 | **A-6** mutasyon raporu | 39 testin gerçek gücünü söyler |
| 4 | **A-2**, **A-3** eksik bekçiler | Küçük, tanımlı |
| 5 | Eksik 14 senaryo sınıfı (G02–G04, G07–G14, G16, G20) | `04-TEST-HARITASI.md` kapsama tablosu |
| 6 | **A-13** kapsam envanteri | Ocak hedefi hâlâ ölçülmedi |
| 7 | **A-7** eşzamanlılık | Plan editörünün önkoşulu |
| 8 | **A-9** KVKK | Gerçek veriden önce |
| 9 | **A-8** PgBouncer | Barındırma kararıyla birlikte |

### Kapanan maddeler

| Madde | Kapanış | Neyle |
|---|---|---|
| A-1 K-9'un bekçisi yok | 12 Eylül 2026 | `M0 - Baglanan rol super kullanici degil` testi |
| A-14 gerçek veri yok | 13–14 Eylül 2026 | 3,5 aylık PDKS + plan analiz edildi, 529 ihlal bulundu |
| **A-4 CI yok** | **14 Eylül 2026** | **GitHub Actions koştu ve yeşil yandı** |
