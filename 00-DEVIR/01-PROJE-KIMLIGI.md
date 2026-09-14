# PROJE KİMLİĞİ

Ne yapıyoruz, kimin için, neyi kanıtlamaya çalışıyoruz.
Bu dosya **kod değiştiğinde değişmez.** Ürün kararı değiştiğinde değişir.

---

## 1. Ürün

**T-Shift** — çok kiracılı, yapay zekâ destekli vardiya planlama ve
optimizasyon SaaS'ı. Teknovisor markası altında.

**Temel iddia:** Tek bir üründe çok sektöre birden hizmet vermek. Çağrı
merkezi, otel, hastane — hepsi **aynı kural havuzundan seçim yaparak**
çalışır. Sektöre özel kural **koda değil veriye** yazılır.

Bu iddia spike aşamasında kanıtlandı: otel senaryosunda gece vardiyası
kuralları koda tek satır eklenmeden, yalnız veri ile devreye girdi
(0 sert ihlal, %99,6 hedef kapsama).

### Ölçek aralığı — iki uç da ürünün içinde

**Karar (12 Eylül).** Ürün hem çok küçük hem çok büyük ekipleri çözmeli:

| Örnek | Kişi | Nereden |
|---|---|---|
| Otelde bar ekibi, havuz/deniz ekibi | ~20 | Otel müşterisi, haftalık plan |
| Otel departmanı | 80–120 | Otel müşterisi |
| Çağrı merkezi operasyonu | 350 | Farklı bir müşteri |
| Büyük operasyon | 500–2000 | Ölçek sınırı (spike'ta test edildi) |

**Bu sadece "büyük/küçük" farkı değil, farklı bir problem sınıfı:**

Küçük ekipte kısıtlar çok daha sıkı bağlar. 350 kişide bir kişinin izni
gürültüdür; 20 kişide üç kişinin izni planı **çözümsüz** yapar. Sonuçları:

- **UNSAT küçük ölçekte kenar durum değil, sık karşılaşılan durumdur.**
  "Çözüm yok" demek yetmez — *"hangi kural çakışıyor, neyi gevşetirsem
  çözülür"* demek gerekir. Yani V09 (yapılandırılmış UNSAT + çatışma
  açıklaması) küçük müşteride **birincil özellik**.
- **Adalet küçük ekipte görünürdür.** 350 kişide "Ayşe 2 saat fazla çalıştı"
  kimse fark etmez; 20 kişilik barda herkes birbirinin vardiyasını bilir ve
  bu tartışma konusu olur.
- **Manuel düzenleme oranı yüksektir.** Küçük ekipte müdür planı elle oynar
  → V11 (manuel düzenleme de aynı doğrulayıcıdan geçer) kritik.
- **Kişi bazlı istisnalar sert kısıt gibi davranır.** *"Mehmet çarşamba
  akşamları okulda"* — 20 kişide bu bir hard constraint, 350 kişide tercih.
- **Geçmiş veri azdır** → istatistiksel/öğrenen bileşenler zayıf kalır.

**Test etkisi:** Ölçek testleri şu ana kadar yalnız **üst uçta** yapıldı
(350/500/1000/2000). **Alt uç hiç test edilmedi** ve orada farklı hatalar
çıkar: tek kişilik ekip, bir kişinin tüm haftayı kapsaması, talep = kapasite,
talep > kapasite, 0 uygun çalışan. Bu tam olarak boş bıraktığımız **G02
(sınır değerler: 0, 1, max, max+1)** senaryo sınıfının vardiya karşılığıdır.

Ayrıntılı ölçek matrisi: `06-ACIK-RISKLER.md` A-10.

### Ürünün sınırları

| Kapsamda | Kapsam dışı |
|---|---|
| Vardiya planı üretimi ve optimizasyonu | Maliyet/ücret hesabı (v1'de ekran yok) |
| Yapılandırılmış ekran ve içe aktarma girdisi | Son kullanıcının doğal dil promptu yazması |
| Ekip (kim kiminle) ve yetkinlik (kim neyi yapabilir) ayrı kurgu | Plan revizyon karşılaştırması |
| Global kural havuzu + şirkete özel kural | — |

### Kritik ürün kararları

- **Vardiya planını yapay zekâ optimizasyon motoru üretir.** Deterministik
  katman yalnız şema, kural ve yetki doğrular. Bu ayrım mimarinin temelidir.
- **Kurallar veride tutulur, kodda değil.** Yanlış bir kural kod değişikliği
  değil parametre değişikliği gerektirir ve sürümü kayıtta kalır.
- **Geçmiş veri olarak "gerçekleşen" vardiya kullanılır**, plan değil.
- **Adalet penceresi aylık**, ay sonunda sıfırlanır. Fazla mesai tavan modeli.
- **Günlük azami çalışma 9 saat.**
- **Plan üretim süresi kısıt değil** (gerekirse 15 dk+), ama editör ekranında
  bekletme olmaz.

---

## 2. Kim, ne yapıyor

**Mustafa** — ürün sahibi, tek karar verici. 11 yıl BT ürün müdürlüğü.
**Yazılımcı değil**: kod yazmıyor, kod okumuyor. Fonksiyonel ve API seviyesi
test yapabiliyor; backend bilgisi yok.

**Yapay zekâ (Claude)** — bütün kodu yazıyor.

**Yılmaz** — Mustafa'nın deneyimli yazılım mimarı arkadaşı. Sürekli değil,
kilometre taşlarında devrede. Dış göz.

### Doğrulamanın iş bölümü

Bu, projenin en önemli tasarım kararıdır ve sık sık unutuluyor:

| Kim | Neyi doğrular |
|---|---|
| Derleyici, veritabanı kısıtları, RLS | Sözdizimi, tutarlılık, yalıtım |
| Otomatik testler | Davranışın yazılana uyduğu |
| **Mustafa** | **Yazılanın doğru olduğu.** "Bu kural sahada gerçekten böyle mi işliyor? Bu çıktı bir operasyon müdürüne mantıklı gelir mi?" |
| Yılmaz | Temelin bir yıl taşıyıp taşımayacağı |

**Hiçbir test, Mustafa'nın cevapladığı soruları cevaplayamaz.** 11 yıllık
operasyon bilgisi orada devreye girer. Bu yüzden ona kod gösterilmez, Türkçe
iş cümlesi gösterilir.

---

## 3. YILMAZ'IN İTİRAZI — bu projenin asıl sorusu

> **Bu bölüm silinmez ve değiştirilmez. Projenin varlık sebebi budur.**

Yılmaz, projeye başlarken şu itirazı yaptı:

> **"Yapay zekâ blokların birbiri ile ilişkisini kuramaz."**

Yani: tek tek dosyalar doğru olabilir, ama katmanlar birleştiğinde ilişki
kopar ve bu kopukluk fark edilmez. Deneyimli bir mimarın, deneyimden gelen,
ciddiye alınması gereken bir itirazı.

### Üzerinde anlaşılan test

İtiraz tartışmayla değil **ampirik olarak** çözülecek: iki haftalık bir
**dikey dilim** yazılacak — çalışan yönetimi, veritabanından ekrana kadar tüm
katmanlar — ve bakılacak soru şu olacak:

> **Katmanlar arası kopmalar SESSİZ mi kalıyor, yoksa YAKALANIYOR mu?**

Soru "hata olur mu" değil. Hata olacak. Soru, hatanın fark edilip
edilmediği.

### Şu ana kadarki bulgu

Dikey dilim tamamlandı. **Dört ciddi hata çıktı ve dördü de yakalandı** —
üstelik hiçbiri insan incelemesiyle değil, otomatik bir kontrolle:

| # | Hata | Yılmaz'ın tarif ettiği sınıf mı? | Ne yakaladı |
|---|---|---|---|
| 1 | Süper kullanıcı RLS'i aşıyordu — güvenlik kâğıt üstünde vardı, çalışmada yoktu | Hayır, daha kötüsü: **koruma vardı ama etkisizdi** | Testin kendisi |
| 2 | JWT `sub` talebi yeniden adlandırılıyordu — 21 test yeşilken tüm korumalı uçlar 401 | **Evet, tam olarak bu.** İki katmanın buluştuğu sınır koptu | Kanıt betiği (testler kaçırmıştı) |
| 3 | D6 testinin iddiası yanlış kurulmuştu | Hayır: kod doğruydu, **testi yazan yanılmıştı** | Testin kırmızı yanması |
| 4 | Docker bağlamına Windows `bin/`/`obj/` girip restore'u eziyordu | Hayır, ortam farkı | Derleme hatası |

**Yılmaz'ın itirazı 2 numarada gerçekleşti ve haklı çıktı.** Ama asıl ders
şu: o hatayı **mevcut testler kaçırmıştı**, çünkü hepsi servisleri doğrudan
çağırıyor, HTTP katmanından geçmiyordu. Yakalayan şey uçtan uca kanıt betiği
oldu. Bunun üzerine `HttpSinirTestleri` kalıcı olarak eklendi.

> **Ders:** Birim testi katmanın **içini**, uçtan uca test katmanların
> **arasını** doğrular. Biri diğerinin yerine geçmez. Yılmaz'ın itirazına
> cevap, daha iyi bir yapay zekâ değil — **katman aralarını sınayan bir test
> katmanıdır.**

### Cevabın şu anki hali

İtiraza verilecek dürüst cevap şu: **haklı, ama sonuç değiştirilebilir.**
Bağlam kopmaları oluyor. Fark şu ki bu projede her kopma, bir daha sessizce
geri gelemeyeceği bir kontrola bağlandı:

| Hata | Kalıcı bekçi |
|---|---|
| Süper kullanıcı RLS'i aşıyordu | `0 - Baglanan rol super kullanici degil` |
| JWT `sub` yeniden adlandırılıyordu | `H1 - Jetonla /me calisir ve dogru kullaniciyi doner` |
| EF sürümleri uyuşmuyordu | Sabitlenmiş paket sürümleri |
| `dotnet test` DLL kilidi | `TEST.ps1` |
| Docker bağlamı | `04-kod/.dockerignore` |

**Yeni pencere için kural:** Bu projede bir hata bulduğunda, düzeltmek işin
yarısıdır. Diğer yarısı, o hatanın bir daha sessizce geri gelmesini engelleyen
kontrolü eklemek ve `05-HATA-OTOPSILERI.md`'ye yazmaktır.

---

## 4. Plan ve zamanlama

### KARAR: MVP yapılmayacak — satılabilir sürüm spec'in fonksiyonel bütünüdür

**Karar tarihi:** 12 Eylül 2026 (Mustafa) · **Tartışmaya kapalı**

> *"Sahada ret yiyip arkada yazılım geliştirme döngüsüne girebilecek bir
> lüksüm yok, spec'im net. Bu spec tamamlandığında satış yapabileceğim."*

**Bu, kapsam disiplinsizliği değil, ürünün yapısından gelen bir zorunluluk.
Gerekçeler kayda geçiriliyor ki altı ay sonra "neden MVP yapmadık" sorusu
yeniden açılmasın:**

1. **Vardiya planlaması kısmi değer üretmez.** Kuralların %80'ine uyan bir
   plan, müdürün elle düzelteceği bir plandır — yani müşterinin zaten yaptığı
   iş. Eksik *özellik* ertelenebilir; eksik *kural* planı kullanılamaz yapar.
2. **Referans müşteri yok.** Bu pazarda bir ret kalıcı olarak kapı kapatır.
   "Önce küçük sat, sonra büyüt" stratejisi referansı olanların lüksüdür.
3. **Satış sonrası plan ekip kurmak.** Bütçeyle mimar/yazılım ekibi kurulup
   devam edilecek (yapay zekâ desteği sürerek). Yani ilk satış, geliştirmenin
   sonu değil finansmanı.

**Bunun bu depo için sonucu:** kapsam kesme önerileri, Mustafa açıkça
istemedikçe gündeme getirilmez. Kapsam sabit; oynayabilen değişkenler takvim
ve sıralamadır.

### İki ayrı "bitti" çizgisi

MVP yapılmaması, her şeyin aynı anda bitmesi gerektiği anlamına gelmez.
İki farklı eşik var:

| | **Satış çizgisi** | **Müşteri verisi çizgisi** |
|---|---|---|
| Ne zaman | İlk demo yapılırken | İlk gerçek veri girmeden önce |
| İçerik | Tüm ekranlar, tüm kurallar, motor, içe aktarma — **çalışır hâlde** | KVKK (A-9), eşzamanlılık (A-7), PgBouncer (A-8), 2000 kişide performans, yedekleme, denetim kaydı hacim yönetimi, WhatsApp/SMS altyapısı |
| Müşteri görür mü | Evet | Hayır — ama eksikliği projeyi bitirir |

İkinci listedeki maddeler **gölge pilot penceresinde** tamamlanır. Bunları
satış çizgisinden ayırmak spec'ten feragat değil, sıralama.

*Örnek: WhatsApp Business API'nin onay süreci ve maliyeti haftalar alabilir.
Satışta "WhatsApp'tan da bildirim gider" demek ile Ocak'ta çalışır teslim
etmek farklı işlerdir.*

### Ocak'ı tehdit eden şey

**Motor değil.** Motor spike'ta kanıtlandı, backend kalıpları oturdu.
Tehdit **24 ekran ve CRUD/yönetim kuyruğu** — yavaş, sıkıcı, çok sayıda ve
takvimlerin öldüğü yer. Bkz. `06-ACIK-RISKLER.md` A-13 (kapsam envanteri).

- **Hedef:** Ocak sonunda ürünü sahaya çıkarmak.
- **Pilot yöntemi: gölge pilot.** Pilot müşteri beklenmeyecek; bir çağrı
  merkezi operasyonundan gerçek veri alınıp, gerçek kullanıcı olmadan uçtan
  uca çalışılacak.
- **Sektör önceliği:** çağrı merkezi. Ama sektöre özel konfigle çok sektöre
  birden hazır çıkılacak.
- **Bekleyen girdi:** Mustafa'nın eski işvereninden çağrı merkezi veri örneği.

### Teknoloji kararları

| Katman | Karar |
|---|---|
| Veritabanı | PostgreSQL · tek veritabanı + `tenant_id` + RLS |
| Backend | .NET 10 |
| **Planlama motoru** | **Python + OR-Tools CP-SAT, ayrı servis** (Go elendi: resmî bağlayıcı yok) |
| Kuyruk | RabbitMQ |
| Kimlik | **Kendi kodumuzda** (Keycloak v1.1'de elendi) |
| Frontend | Next.js 16 + TypeScript |
| Yapay zekâ katmanı | Claude API |
| Barındırma | **Karar satış sonrasına ertelendi** |

Motor kararının dayanağı ölçülmüş: CP-SAT %99,5 hedef kapsama + 0 fazla mesai
(greedy %95,7 + 92 saat); optimuma uzaklık %0,01. 2000 çalışanda bile 60
saniyede %98,9 kapsama. Ölçek ürün riski değil.

---

## 5. Elde olan varlıklar

| Ne | Nerede | Durum |
|---|---|---|
| Master Spec v1.2 | `02-spec/` | Güncel referans |
| Motor fizibilite spike'ları | `01-spike/` | Donduruldu, kronoloji README'de |
| Demo (15 ekran, 2 operasyon) | `03-demo/v2-html/` | Yayınlandı, telefonda açılabiliyor |
| Çalışan dikey dilim | `04-kod/` | 39 test yeşil, CI'da koşuyor |
| Yılmaz inceleme paketi | `05-inceleme/v1-2026-09-11/` | Gönderildi |
| Excel okuyup UI'da doğrulayan mevcut araç | Mustafa'da | Sıfırdan yazılmayacak, entegre edilecek |
