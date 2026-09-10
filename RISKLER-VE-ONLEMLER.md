# Riskler ve önlemler

Yapay zekâ ile yazılım geliştirirken hangi hatalar oluyor, hangileri gerçekten
tehlikeli, ve bu projede ne yapıyoruz.

## İçindekiler

1. [Gerçekten geri dönülmez olan dört şey](#1-gerçekten-geri-dönülmez-olan-dört-şey)
2. [Hata sınıfları ve neyin yakaladığı](#2-hata-sınıfları-ve-neyin-yakaladığı)
3. [Savunma hatlarımız](#3-savunma-hatlarımız)
4. [Şimdi ucuz, sonra pahalı kararlar](#4-şimdi-ucuz-sonra-pahalı-kararlar)
5. [Dışarıdan destek: ne zaman, ne için](#5-dışarıdan-destek-ne-zaman-ne-için)
6. [Kırmızı çizgiler](#6-kırmızı-çizgiler)

---

## 1. Gerçekten geri dönülmez olan dört şey

Kod hatası geri dönülmez değildir. Depoda her sürüm duruyor, her değişiklik
geri alınabiliyor. "Baştan yazmak zorunda kalmak" korkusunun kaynağı kodun
kendisi değil, aşağıdaki dört şeyden biridir.

### 1.1 Veri

Silinen veri geri gelmez. Bozulan veri, bozulduğu fark edilene kadar geçen
sürede türetilen her şeyi de bozar. Sızan veri geri alınamaz — KVKK
sorumluluğu da cabası.

En sık kaynağı: **migration.** Bir kolonu düşüren, tipini değiştiren ya da
veriyi dönüştüren bir migration, gerçek veri üzerinde çalıştığında geri
alınamaz. Üretilen migration kodu rutin görünür; tehlikeli olan tam da budur.

### 1.2 Kaydedilmemiş geçmiş

Tutmadığın geçmişi sonradan üretemezsin. Denetim kaydı (audit log) olmadan
canlıya çıkıp altı ay sonra "bu planı kim değiştirdi, hangi kural sürümüyle
üretildi" diye sorarsan, cevap yoktur ve hiçbir zaman olmayacaktır.

Bu, spec'te tanımlı ama **henüz yazılmadı.** Pilot öncesi yazılması gerekir;
pilot sonrası yazılırsa aradaki dönem kalıcı olarak karanlıkta kalır.

### 1.3 Güven

Pilot müşteri yanlış bir vardiya planı görüp buna göre iş yaparsa, ürüne olan
güven bir daha aynı olmaz. Bir çalışan izinli olduğu gün vardiyaya yazılırsa,
düzeltmen teknik olarak kolaydır; itibarı düzeltmen kolay değildir.

### 1.4 Anlaşılmazlık

**Yazılımların baştan yazılma sebebi kötü kod değil, anlaşılmaz koddur.**

Bir ekip devraldığında şu soruyu sorar: "bu satır neden böyle?" Cevap yoksa,
dokunmaya korkar. Dokunamadığı kodu zamanla kuşatır, sonra yeniden yazmayı
teklif eder. Yeniden yazma kararı teknik değil, **psikolojiktir**: kimse
anlamadığı bir sistemin sorumluluğunu almak istemez.

Yapay zekâyla yazılan kodda bu risk daha yüksektir, çünkü kod hızlı üretilir
ve gerekçesi üretenin kafasında kalır — kafası da her oturumda sıfırlanır.

Bu yüzden bu depoda kural şudur: **her sıra dışı karar, yanındaki yorumda
gerekçesiyle birlikte durur.** `login_attempts` neden RLS dışında, `sub`
talebi neden yeniden adlandırılmıyor, kapsamsız kullanıcı neden hiçbir şey
görmüyor — hepsi kodda yazılı. Yorumlar süs değil, yeniden yazılmaya karşı
sigortadır.

---

## 2. Hata sınıfları ve neyin yakaladığı

Yılmaz'ın tarif ettiği "bağlam kopması" bunlardan yalnız biri.

| # | Hata sınıfı | Nasıl görünür | Ne yakalar |
|---|---|---|---|
| 1 | **Uydurma** — var olmayan bir metot ya da davranış varsayma | Derlenmez | Derleyici |
| 2 | **Bağlam kopması** — iki bloğun ilişkisini yanlış kurma | Tek tek doğru, birlikte bozuk | Uçtan uca test |
| 3 | **Anlamsal kayma** — aynı kavramın iki yerde farklı uygulanması | Hiçbir şey; bir gün rakamlar tutmaz | Tip sistemi, değişmez testler |
| 4 | **Kopyalanmış mantık** — mevcut yardımcıyı görmeyip yenisini yazma | İkisi zamanla ayrışır | İnceleme, küçük kod tabanı |
| 5 | **Testin aynı yanlışı paylaşması** | Test yeşil, davranış yanlış | Spec'ten türetilen test, bağımsız denetleyici |
| 6 | **Testi düzeltip kodu bırakma** | Yeşil ama yanlış | Kural: iddia değişmez, önce spec değişir |
| 7 | **Fazla mühendislik** | Gereksiz soyutlama, kayan takvim | Kapsam sözleşmesi (spec) |
| 8 | **Onaylayıcılık** — kötü fikre itiraz etmemek | Fark edilmez | Karşıt inceleme, açık talep |
| 9 | **Gerekçenin kaybolması** | Biri "sadeleştirir", açık açılır | Yorum + bekçi test |
| 10 | **Yıkıcı migration** | Veri gider | İnceleme ritüeli, yedek |
| 11 | **Sır ve kişisel veri sızıntısı** | Kayıtlarda parola, depoda anahtar | Kayıt kuralı, `.gitignore` |
| 12 | **Bağımlılık riski** | Terk edilmiş paket, lisans sorunu | Sürüm sabitleme, düzenli tarama |
| 13 | **Yerel ayar ve zaman** | Türkçe `ı`, ondalık virgül, saat dilimi | Değişmez testler, UTC kuralı |
| 14 | **Eşzamanlılık** | İki kişi aynı anda onaylar | Veritabanı kısıtları, idempotency |
| 15 | **Ölçek uçurumu** | 5 kayıtta çalışır, 5.000'de ölür | Gerçekçi hacimle test |

Bu projede şimdiye kadar **3, 10, 11, 14, 15 dışında** hepsinden en az bir
örnek yaşandı ve hepsi otomatik bir kontrol tarafından yakalandı.

### Neden 3, 5 ve 9 en tehlikelileri

Diğerleri **gürültülüdür**: derleyici bağırır, test kırılır, istek patlar.
Gürültülü hata ucuzdur.

3, 5 ve 9 **sessizdir**. Kod derlenir, testler geçer, uygulama çalışır, ve
üretilen sonuç yanlıştır. Bir vardiya planlama ürününde bu şu demektir: plan
üretilir, kimse itiraz etmez, üç hafta sonra birinin fazla mesaisi patlar.

Sessiz hataya karşı geri alma işe yaramaz — geri alacak bir şey olduğunu
bilmiyorsundur. Savunma başka yerdedir:

- **Bağımsız denetleyici** (spec §11): planı üreten kodla denetleyen kod
  hiçbir mantık paylaşmaz. Planlayıcı kuralı yanlış anladıysa denetleyici
  aynı yanlışı tekrarlamaz, çünkü aynı kodu okumaz.
- **Kurallar veride, kodda değil**: yanlış bir kural kod değişikliği
  gerektirmez, parametre değişir ve sürümü kayıtta kalır.
- **Testler spec'ten türetilir, koddan değil.** Kodu yazan kişi testi de
  kendi anladığı şekilde yazarsa, sistem kapalı devre olur ve test hiçbir
  şey ispatlamaz.
- **Değişmez (invariant) testler**: özellikten bağımsız, her zaman doğru
  olması gereken yasalar. Bkz. `MimariTestleri`.

---

## 3. Savunma hatlarımız

Sıra önemli: yukarıdakiler ucuz ve hızlıdır, aşağıdakiler pahalı ve yavaş.
İyi bir sistem hatayı mümkün olan en üst basamakta yakalar.

| Hat | Ne yakalar | Ne zaman çalışır |
|---|---|---|
| **Tip sistemi ve derleyici** | Uydurma, imza uyuşmazlığı, sürüm çakışması | Yazarken |
| **Veritabanı kısıtları** | Tutarsız veri, yetim kayıt, çift kayıt | Yazma anında |
| **Satır seviyesi güvenlik (RLS)** | Kiracı sızıntısı | Her sorguda |
| **Birim testleri** | Katmanın içindeki mantık hataları | `dotnet test` |
| **HTTP sınırı testleri** | Katmanlar arası kopmalar | `dotnet test` |
| **Mimari testleri** | Unutulan RLS, korumasız uç, yerel ayar tuzağı | `dotnet test` |
| **Kanıt betiği** | Uçtan uca davranış, gözle görülür kanıt | Elle |
| **İnsan incelemesi** | Niyet hatası, ürün yanlışı | Kilometre taşlarında |

### Neyi kim doğrular

Mustafa'nın işi **sözdizimi değil, niyet**. Derleyici zaten sözdizimine
bakıyor. Bakılacak sorular şunlar:

- Bu kural sahada gerçekten böyle mi işliyor?
- Bu çıktı bir operasyon müdürüne mantıklı gelir mi?
- Bu ekranda kullanıcı ne yapmaya çalışır?
- Bu kararı müşteriye nasıl anlatırım?

11 yıllık operasyon bilgisi bunları cevaplar; hiçbir test cevaplayamaz.

### Yapay zekânın kendi kendini denetleyememesi

Bir metni yazan, o metindeki hatayı en zor gören kişidir. Aynı sınırlama
burada da geçerli. Bu yüzden:

- Kodu yazan oturumun kendi kodunu "gözden geçirmesi" düşük değerlidir.
- **Sıfırdan bağlamla yapılan inceleme** yüksek değerlidir: kodu hiç
  yazmamış, yalnız spec'i ve diff'i okuyan bir inceleme.
- Kilometre taşlarında bunu yapacağız.

---

## 4. Şimdi ucuz, sonra pahalı kararlar

Aşağıdakiler değiştirilemez değil, ama sonradan değiştirmek katlanarak
pahalılaşır. Bugün karar vermek bir saat, canlıdayken bir ay sürer.

| Karar | Durum | Sonradan değiştirmenin bedeli |
|---|---|---|
| Kiracılık modeli (tek db + RLS) | ✅ Karar verildi, çalışıyor | Tüm veri taşınır |
| Kimlik şeması (UUIDv7) | ✅ Karar verildi | Tüm yabancı anahtarlar |
| Zaman modeli (UTC + genişletilmiş saat) | ✅ Karar verildi | Her plan yeniden yorumlanır |
| Kural motoru (kurallar veride) | ✅ Karar verildi | Motorun tamamı |
| **Denetim kaydı (audit log)** | ⚠️ **Yazılmadı** | **Geçmiş kalıcı olarak kaybolur** |
| Eşzamanlılık (satır sürümü, idempotency) | ⚠️ Yazılmadı | Bozulan veriyi tespit etmek zor |
| Para ve yuvarlama kuralları | Henüz gündemde değil | Geçmiş hesaplamalar yeniden yapılır |
| Motor sınırı (ayrı servis, sözleşme) | ✅ Karar verildi | Yeniden yazım |

**Denetim kaydı pilot öncesi yazılmalı.** Diğerlerinin hepsi sonradan
eklenebilir; bu eklenemez, çünkü geçmişi geriye dönük üretemezsin.

---

## 5. Dışarıdan destek: ne zaman, ne için

Sürekli bir yazılımcıya ihtiyaç yok. Belirli üç anda dış göz yüksek değerli:

**1. Mimari kontrol noktası — şimdi.**
Kiracılık, kimlik ve yetki katmanları oturdu, henüz gerçek veri yok.
Değiştirmenin en ucuz olduğu an. Yılmaz'a gösterilecek paket tam olarak bu.
Sorulacak soru: "bu temel üzerine bir yıl inşa edilir mi?"

**2. Güvenlik ve KVKK incelemesi — gerçek veri girmeden önce.**
Çalışan verisi kişisel veridir. Anonimleştirme, saklama süresi, erişim
kaydı, silme talebi — bunlar ürün özelliği değil, yasal yükümlülük.
Bir kere yanlış kurulursa geri dönüşü zor.

**3. Motorun çıktısı operasyonel olarak güvenilir sayılmadan önce.**
Planın matematiksel doğruluğu ile operasyonel doğruluğu farklı şeylerdir.
Bunu bir çağrı merkezi operasyon müdürüne doğrulatmak gerekir — yazılımcıya
değil.

Bunların dışında sürekli destek gereksiz; hız kaybettirir.

---

## 6. Kırmızı çizgiler

Bu maddeler tartışmaya kapalıdır. Her biri geri dönülmez bir hataya karşı
duruyor.

**Veri**

- Gerçek veri üzerinde çalışacak hiçbir migration, üretilen SQL okunmadan
  çalıştırılmaz. `DROP`, `ALTER COLUMN ... TYPE`, `DELETE` görürsen dur.
- Gerçek veri üzerinde migration öncesi **yedek alınır.** İstisnasız.
- Kolon silme ve ekleme aynı sürümde yapılmaz: önce ekle, doldur, geç,
  **sonraki sürümde** sil. Böylece her adım geri alınabilir kalır.
- `docker compose down -v` yalnız geliştirme makinesinde.

**Sır ve kişisel veri**

- `.env` git'e gitmez. Sırlar `appsettings.json`'a yazılmaz.
- İstek gövdeleri kayda yazılmaz — içinde parola olabilir.
- Pilot verisi anonimleştirilmiş gelir; gerçek isim ve kimlik numarası
  geliştirme ortamına girmez.

**Kod**

- `main` her zaman yeşil. Test kırmızıyken birleştirilmez.
- Kırılan bir test, iddia değiştirilerek düzeltilmez. Önce spec değişir,
  değişiklik günlüğe yazılır, sonra test güncellenir.
- Sıra dışı her karar yanındaki yorumda gerekçesiyle durur.
- Anlaşılmayan komut çalıştırılmaz — özellikle `rm`, `del`, `format`,
  `Remove-Item`, `--force` içerenler.

**Süreç**

- Kilometre taşlarında etiket atılır ve değişiklik günlüğüne yazılır.
- Spec'ten sapılıyorsa sapma **açıkça** kaydedilir ve bir testle sabitlenir.
- Bir hata bulunduğunda düzeltmek yetmez: o hatanın **bir daha sessizce
  geri gelmesini engelleyen** bir kontrol eklenir.

Son madde bu projenin işleyiş biçimi. Şimdiye kadar üç ciddi hata çıktı ve
üçü de artık kalıcı bir bekçiye bağlı:

| Hata | Bekçi |
|---|---|
| Süper kullanıcı RLS'i aşıyordu | `0 - Baglanan rol super kullanici degil` |
| EF sürümleri uyuşmuyordu | Sabitlenmiş paket sürümleri |
| JWT `sub` talebi yeniden adlandırılıyordu | `H1 - Jetonla /me calisir` |
