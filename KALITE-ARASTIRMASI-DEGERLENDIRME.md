# GPT Kalite Araştırması — Değerlendirme

**Belge:** `ai_yazilim_kalite_arastirmasi.docx` (754 paragraf, ~39.000 karakter, 20 kaynak)
**Değerlendiren:** Claude · **Tarih:** 12 Eylül 2026
**Soru:** Bu belgenin T-Shift'in geliştirme ve test süreçlerine katkısı olur mu?

---

## 0. Kısa cevap

**Evet, ama dengeli okumak gerekiyor.** Belgenin kabaca:

- **%55–60'ı** zaten yaptığımız şeyleri anlatıyor. Bu kötü bir şey değil — bağımsız bir doğrulama. Yılmaz'a göstereceğin dosyaya değer katar: "bu kontroller aklımıza böyle geldi" değil, "bu kontroller sahanın standardı."
- **%20–25'i** bize şu an uymuyor. Belge 10–50 kişilik, canlıda çalışan, kullanıcısı olan bir ekip için yazılmış. Bizde bir kişi (sen) + bir yapay zeka var, canlı yok, kullanıcı yok.
- **%15–20'si gerçekten yeni ve değerli.** Ve şanslıyız: bu kısım neredeyse tamamen **henüz yazmadığımız parçaya**, yani **vardiya optimizasyon motoruna** bakıyor (§8) ve **testlerin gerçekten koruyup korumadığı** sorusuna (§6). İkisi de bizde açık.

En kıymetli tek cümlesi şu, ve bu cümle bizi doğrudan vuruyor:

> "Model hem kodu hem testi aynı oturumda yazarsa, yanlış yorumu iki tarafta da tutarlı biçimde tekrar edebilir."

Bunu biz zaten yaşadık. Aşağıda anlatıyorum.

---

## 1. Önce belgenin kendisi güvenilir mi?

GPT'nin ürettiği bu tür belgelerde en sık görülen hata **uydurma kaynak**tır. Bu yüzden önce kaynakları denetledim. Sonuç iyi:

| Kaynak | Durum |
|---|---|
| [2] METR 2025, %19 yavaşlama | **Doğru.** Gerçek çalışma, rakam doğru aktarılmış. |
| [3] METR 2026 güncellemesi | **Doğru.** 24 Şubat 2026 tarihli güncelleme gerçekten "artık hızlanma muhtemel görünüyor ama yeni sonuçlarımız güvenilmez" diyor. Belge bunu dürüstçe aktarmış — abartmamış. |
| [6] USENIX Security 2025, paket halüsinasyonu | **Doğru.** %5,2 / %21,7 oranları gerçek çalışmaya uyuyor. |
| [16] "Misu ve diğerleri, Agent Generated Tests and Over Mocking" | **Bulgu doğru, künye yanlış.** Çalışma gerçek (MSR 2026, 1,2 milyon commit incelemesi) ama yazarı Misu değil, **Andre Hora**. |
| [1] [4] [5] [7] [8] [19] [20] | Hepsi gerçek ve tanınmış kaynaklar; aktarımları doğru. |

**Yorum:** Bu, GPT çıktısı için iyi bir karne. Ama [16]'daki künye hatası tam da belgenin kendi uyardığı şeyin örneği: *ikna edici görünen, çoğu doğru, bir yeri sessizce yanlış.* Belgeyi Yılmaz'a ya da başkasına bir otorite gibi sunmayacağız — "sahanın özeti" olarak sunacağız.

İkinci bir sınır: belge **hiçbir yeni bilgi üretmiyor.** Kamuya açık en iyi pratiklerin derli toplu bir sentezi. Bizim `RISKLER-VE-ONLEMLER.md` dosyamızda olan ama bu belgede olmayan şey şu: **bizde gerçekten olmuş dört hatanın otopsisi.** Genel doğru, yaşanmış hatadan daha ucuzdur ama daha az öğreticidir.

---

## 2. Belgenin bizi doğruladığı yerler

| Belgenin önerisi | Bizdeki karşılığı | Durum |
|---|---|---|
| §3.3 "Talimat yönlendiricidir, CI/izin/hook zorlayıcıdır" | `MimariTestleri` M1–M6 — kuralı yazıya değil teste bağladık | ✅ Belgenin ana tezi, bizim ana tezimiz |
| §6.1 "Gerçek DB, mock değil" | 38 testin tamamı gerçek PostgreSQL'e gidiyor, hiç mock yok | ✅ Belgenin istediğinden ileride |
| §6.2 "Test diff denetimi" | Kırmızı çizgi kuralımız: *"bu değişiklikten sonra test, eskiden yakalayacağı bir hatayı kaçırır mı?"* | ✅ Aynı kural, daha keskin ifade |
| §7 G05 Yetki / G06 Tenant ayrımı | `CokKiracilikTestleri`, `YetkiTestleri`, `YALITIM-KANITI.ps1` | ✅ Kapsanıyor |
| §7 G15 Secret loglama | `DenetimToplayici` — `SifreHash`, `JetonOzeti` → `<gizlendi>`; istek gövdesi loglanmıyor | ✅ Kapsanıyor |
| §5 "Mimari sınırlar korunur" | M1/M2/M3 — RLS zorunluluğu, korumasız uç yasağı | ✅ Kapsanıyor |
| §5.1 Diff bütçesi | Yazılı kural değil ama fiilen küçük adımlarla gidiyoruz | 🟡 Yazıya dökülmemiş |
| §4.1 Kısa depo talimatı | `README.md` + `SURUMLEME.md` + `RISKLER-VE-ONLEMLER.md` | ✅ Var |
| §12 Asgari protokol maddelerinin çoğu | Adım adım onayınla ilerleme, her sürümde etiket + günlük | ✅ Var |

**Bunun anlamı:** Yılmaz'a "AI blokları birleştiremez" itirazına karşı elimizdeki kanıt, artık sadece kendi deneyimimiz değil. Belgedeki çerçeve şunu söylüyor: sorun AI'ın birleştirememesi değil, **birleşmenin sessizce bozulabilmesi**. Çözüm de AI'ı daha çok zorlamak değil, **bozulmayı gürültülü hale getiren kapılar koymak.** Biz tam olarak bunu yaptık ve işe yaradığını dört kere gördük.

---

## 3. Belgenin bizde gerçekten açık yakaladığı yerler

Bunlar önem sırasına göre.

### 3.1 Testleri kodu yazan yazdı — en ciddi açık

Belge §6'da diyor ki: *kritik kabul ölçütleri uygulamayı görmeyen bir kişi ya da ayrı bir oturum tarafından tanımlanmalı.*

Bizde 38 testin tamamını ben yazdım, kodu da ben yazdım, çoğunu aynı oturumda. Bu, belgenin tarif ettiği tam da o risk.

**Ve bu risk bizde bir kere gerçekleşti:** denetim kaydı testi D6. Test kırmızı yandı, ben "kod bozuk" diye baktım — kod doğruydu, **test yanlıştı.** "B kiracısı sıfır kayıt görür" diye yazmışım; oysa B'nin kendi kayıtları var. Yani kendi yanlış varsayımımı hem koda hem teste yazmadım, ama **teste yazdım ve kod doğru olduğu için yakalandı.** Tersi de olabilirdi: yanlış varsayımı ikisine birden yazsaydım, test yeşil yanardı ve hiçbir şey fark etmezdik.

**Bizim ölçeğimizde çözümü "ikinci bir kişi" olamaz.** Uygulanabilir hali şu:

> **Kabul ölçütünü sen yaz, Türkçe, kod yazılmadan önce.**
> Ben "şunu yapacağım" demeden, sen "bu doğru çalışıyorsa ne görmeliyim" cümlesini kuracaksın. Test o cümlenin çevirisi olacak, benim varsayımımın değil.

Bu hiçbir şeye mal olmuyor ve D6 sınıfı hatayı kökten kapatıyor. **Belgeden aldığımız en değerli tek şey bu.**

### 3.2 Kapıların hiçbiri zorlayıcı değil — sadece biz çalıştırıyoruz

Belgenin ana tezi "talimat yönlendirir, CI zorlar." `MimariTestleri` mükemmel bir kapı — **ama kapıyı kimse zorla açtırmıyor.** Testler sadece sen `TEST.ps1` çalıştırdığında koşuyor. Unuttuğumuz bir gün, kırık kod GitHub'a girer ve kimse görmez.

**Yapılacak:** GitHub Actions ile her `git push`'ta testlerin otomatik koşması. Repo zaten GitHub'da, ek maliyet yok, tek bir dosya. Bu, belgenin 30 günlük planındaki "Gün 11–15" işi ve bizim için gerçekten eksik olan şey.

### 3.3 Testlerin gerçekten koruyup korumadığını bilmiyoruz

38 test yeşil. Ama "38 test var" ile "38 test bir şeyi koruyor" aynı şey değil — belge buna §6.2'de **mutasyon testi** diyor: kodu kasten boz, testler bunu yakalıyor mu?

C# için hazır araç var: **Stryker.NET**. Bir kereliğine kritik modüllere (`Yetki`, `CokKiracilik`, `Denetim`) koşturursak, elimize "testlerinizin gerçek gücü şu" diye bir rapor gelir. Yeşil ekrana güvenmek yerine ölçmüş oluruz.

Bu, Yılmaz'a göstereceğin dosyaya da çok yakışır: *"testler yeşil"* demek yerine *"testlerin %X'i kasten bozulmuş kodu yakalıyor"* demek bambaşka bir iddia.

### 3.4 Vardiya motoru için §8 — belgenin en iyi bölümü

Bu bölüm bize özel yazılmış gibi ve tam da **henüz yazmadığımız** parçaya bakıyor. Ayrı başlık açıyorum (bkz. §5).

---

## 4. Bize uymayan, şimdilik atlanacak kısımlar

Dürüst olalım — belgenin bir kısmı bizim ölçeğimizde israf:

| Bölüm | Neden şimdilik gereksiz |
|---|---|
| §11.3 "AI'lı ve AI'sız akışı dönüşümlü kullan, karşılaştır" | **Bizde kontrol grubu yok.** Sen hiç AI'sız kod yazmıyorsun. Bu deney tasarımı bizde uygulanamaz. |
| §11.1 Change failure rate, çevrim süresi, DORA metrikleri | Canlı yok, kullanıcı yok, yayın yok. Ölçecek bir şey yok. |
| §11.2 30 günlük plan (ekip odaklı) | Ekip yok. Maddelerin 4'ü bize uyar, 8'i uymaz. Plan olarak değil, kontrol listesi olarak okunmalı. |
| §3.2 Aşama 9 Canary / SLO / hata bütçesi | Pilot müşteriden sonra konuşulur, şimdi değil. |
| SBOM, bağımlılık allowlist, lisans onayı | Bir avuç NuGet paketimiz var, hepsi Microsoft. Şimdi kurmak ağır olur. |
| CODEOWNERS, korunan test dizini | Tek yazar var. Kendinden koruma anlamsız. |

Ayrıca belge **yaklaşık %30 tekrar** içeriyor: §2 risk tablosu, §5.2 inceleme soruları, §10 CI kapıları ve §12 asgari protokol büyük ölçüde aynı listenin dört farklı görünümü. Yanlış değil, sadece şişkin.

---

## 5. Vardiya motoru: belgenin bize en somut hediyesi

Kural ve optimizasyon problemlerinde "doğru çıktı" tek bir beklenen listeyle sınanamaz — aynı girdiye birden çok geçerli plan vardır. Belge §8'de bunun mimarisini veriyor ve doğru veriyor:

```
girdi şema doğrulaması  →  çözücü (solver)  →  BAĞIMSIZ doğrulayıcı  →  puan hesaplayıcı
                                                  ↑
                              solver'ın koduyla HİÇBİR ŞEY paylaşmaz
```

**Kritik nokta:** doğrulayıcı, çözücünün "ben geçerli bir plan ürettim" bayrağına bakmaz. Planı sıfırdan kurallara karşı denetler. Çözücü hangi teknolojiyle yazılırsa yazılsın, hiçbir plan doğrulayıcıdan geçmeden kullanıcıya gösterilmez.

Bu, "bağımsız oracle" fikrinin **kod düzeyinde** hali — ve §3.1'deki insan düzeyindeki çözümün tamamlayıcısı. İkisi birlikte, D6 sınıfı hatanın motorda tekrarlanmasını engeller.

Belgenin V01–V12 değişmez listesi de neredeyse olduğu gibi alınabilir. Bizim için en keskin olanlar:

- **V02** — gece yarısını aşan vardiya (00:00'da biten/başlayan çakışma hesabı)
- **V03 + V04** — **yaz saati geçişi.** Türkiye kalıcı UTC+3'te ama çok uluslu müşteride bu gerçek bir hata kaynağı. "Minimum dinlenme 11 saat" kuralı DST gününde 10 veya 12 saat olur. Belgenin G12'si haklı.
- **V09** — imkansız girdi **asla** kaçak bir plan üretmez; `UNSAT` döner ve **hangi kuralın çakıştığını söyler.** Kullanıcı için en kritik özelliklerden biri bu ve mühendislik olarak da en kolay atlanan.
- **V10** — aynı girdi + aynı seed → aynı sonuç. Yoksa hata ayıklayamayız.
- **V11** — **manuel düzenleme de aynı doğrulayıcıdan geçer.** Sürükle-bırak ile kural ihlali yapılamaz.
- **V12** — audit kaydı. Bunu zaten yaptık; motora da bağlanacak.

§8.3'teki **metamorfik testler** ise bizde hiç olmayan bir teknik ve tam yerinde:

- Çalışan listesinin sırası değişirse sonuç değişmemeli
- Bir katı kural **gevşetilirse**, çözülebilen bir örnek çözülemez hale gelemez
- Bir katı kural **sıkılaştırılırsa**, dönen plan yeni kuralı ihlal edemez

Bunlar "doğru cevabı bilmeden doğruluğu sınama" yöntemi ve optimizasyon için biçilmiş kaftan.

**Öneri:** Motoru yazmaya başlamadan önce **doğrulayıcıyı ve V01–V12 listesini** yazalım. Sıralama önemli: önce "neyin yanlış olduğunu bilen" parça, sonra "çözmeye çalışan" parça. Bu, spec'e girmesi gereken bir mimari karar.

---

## 6. Belgenin bilmediği, bizim yaşadığımız üç hata sınıfı

Bu kısım önemli, çünkü belgeyi mutlak doğru sanmayalım. Bizim `RISKLER-VE-ONLEMLER.md`'de olan ama belgenin risk taksonomisinde **hiç geçmeyen** üç şey var:

### 6.1 Koruma var ama yürürlükte değil

En ciddi hatamız buydu: RLS yazılmıştı, tanımlıydı, veritabanında görünüyordu — **ve hiçbir şey yapmıyordu**, çünkü uygulama süper kullanıcıyla bağlanıyordu. Süper kullanıcı RLS'i tamamen atlar; `FORCE` bile durduramaz.

Belgenin §2 tablosunda "güvenlik açığı: güvenliği örtük varsayma" var, ama **"koruma tanımlı ama etkisiz"** diye bir satır yok. Bizim çıkardığımız kural belgede yok ve belgeden daha keskin:

> **"Koruma tanımlı mı" yanlış sorudur. Doğru soru: "koruma şu anda beni durduruyor mu?"**
> Her koruma için, korumanın *yürürlükte olduğunu* kanıtlayan ayrı bir test.

Bizdeki karşılığı: `"0 - Baglanan rol super kullanici degil"` testi. Bu bizim icadımız, belgede yok.

### 6.2 Yanlış alarm veren kontrol, ölü kontroldür

M4 testi bir ara kendi doküman satırını hata diye işaretledi. Kuralımız:

> *"Yanlış alarm veren bir kontrol, bir süre sonra ciddiye alınmayan bir kontrole dönüşür."*

Belge kapı kurmayı uzun uzun anlatıyor ama **kapı bakımını** hiç konuşmuyor. Gereksiz uyaran bir kapı, olmayan kapıdan daha kötüdür — çünkü var sanırsın.

### 6.3 Zaman kaybımızın çoğu AI'dan değil, alet çantasından geldi

Dürüst bir muhasebe: bu projede kaybettiğimiz saatlerin büyük kısmı şunlardan geldi —

- PowerShell 5.1 `.ps1` dosyasını ANSI okuyor, Türkçe karakter parser'ı kırıyor
- `-SkipHttpErrorCheck` sadece PowerShell 7'de var
- Windows'un `bin/`/`obj/` klasörleri Docker imajına girip restore'u eziyor (`.dockerignore` yoktu)
- `dotnet test` sırasında DLL kilidi (üç kere)
- Next.js 16 + Turbopack görsel işleme hattı logoyu kırıyor

**Hiçbiri "AI gereksinimi yanlış anladı" değil.** Hepsi ortam, sürüm ve platform farkı. Belge idealize edilmiş bir Linux/CI dünyası için yazılmış ve bu sınıfı hiç görmüyor. Gerçek projede bu sınıf, belgenin saydığı risklerin çoğundan daha pahalıya patlıyor.

---

## 7. Ne yapalım — sıralı öneri

Maliyet/fayda sırasına göre:

| # | İş | Maliyet | Kazanç |
|---|---|---|---|
| 1 | **Kabul ölçütünü sen yaz, Türkçe, kod yazılmadan önce** | Sıfır | D6 sınıfı hatayı kapatır. Belgenin en değerli maddesi. |
| 2 | **GitHub Actions: her push'ta testler koşsun** | ~1 saat, tek dosya | Kapıları öneri olmaktan çıkarıp zorunlu yapar |
| 3 | **Stryker.NET mutasyon raporu** (bir kereliğine, kritik modüller) | ~2 saat | "38 test var" yerine "testler şu kadar koruyor" |
| 4 | **Motor sözleşmesi: bağımsız doğrulayıcı + V01–V12** | Motor işinin parçası | Motorun doğruluğunu baştan kanıtlanabilir yapar |
| 5 | **`DEVIR.md`** — oturumlar arası devir özeti | 15 dakika | Aşağıdaki §8'in cevabı |
| 6 | **Diff bütçesi kuralını yazıya dök** | 10 dakika | Kapsam kaymasını senin görebileceğin hale getirir |
| — | Metrik programı, SBOM, canary, A/B deney | — | **Ertelendi.** Pilot müşteriden sonra. |

---

## 8. "Uzun sohbet bağlam kaybettirir, yeni pencerede devam edelim mi?"

Kısa cevap: **evet, ama sohbeti özetleyerek değil — deponun kendisini devir paketi yaparak.**

Sorunun kendisi haklı ve belge de §4.2'de aynı şeyi söylüyor. Hatta **bu konuşma tam olarak bunu yaşadı**: sohbet bağlam sınırına dayandı ve özetlendi. İyi haber: **maliyeti neredeyse sıfır oldu.** Çünkü projenin hafızası sohbette değil, depoda duruyordu.

### Neden sohbet özeti kötü bir devir yöntemi

Bir sohbet özeti, benim yazdığım düzyazıdır. İçinde bir yanlış varsayım varsa, sonraki pencereye **sessizce** taşınır ve orada doğru sanılır. Belge buna "yamalı bağlam" diyor. Depo öyle değil: kod derlenir ya da derlenmez, test yeşil yanar ya da yanmaz. **Depo yalan söyleyemez, özet söyleyebilir.**

### Bizim hafızamız zaten doğru yerde

Farkında olmadan doğru şeyi yapmışız. Şu anda projenin hafızası şurada:

- **Kod + 38 test** → "sistem ne yapıyor" sorusunun sorgulanabilir cevabı. Testler aynı zamanda şartname.
- **`DEGISIM-GUNLUGU.md` + git etiketleri (v0.1 … v0.7)** → "ne zaman ne değişti"
- **`RISKLER-VE-ONLEMLER.md`** → "hangi hatalar oldu, ne öğrendik"
- **`SURUMLEME.md`** → "hata yaparsak nasıl geri döneriz"
- **Kod içi Türkçe yorumlar** → "neden böyle yapıldı" (bunlar alışılmadık derecede ayrıntılı ve bilinçliydi)
- **`02-spec/v1.2-master-spec.md`** → "ne yapmak istiyoruz"

Yeni bir pencere bu altı kaynağı okuyarak projeyi **doğrulanabilir** şekilde yeniden kurabilir. Sohbet geçmişini okuyarak kuramaz.

### Eksik olan tek parça

Bir şey eksik: **"şu anda tam olarak neredeyiz ve sıradaki tek adım ne?"** Bu bilgi şu an sadece sohbette duruyor ve devredilen tek kırılgan şey o.

Çözüm, depoda tek bir dosya — `DEVIR.md` — ve her oturum sonunda güncelleniyor. Belgenin §4.3'teki biçimini bizim projeye uyarladım:

```markdown
# DEVIR — son güncelleme: <tarih>

## NEREDEYIZ
Son etiket: v0.7-inceleme
Çalışan: PostgreSQL+RLS, kimlik, yetki, denetim kaydı, API, Next.js ekranı
Test: 38/38 yeşil (gerçek veritabanına karşı)

## SIRADAKI TEK ADIM
<tek cümle>

## AÇIK KARARLAR (henüz verilmedi)
- PgBouncer / oturum GUC riski — çözülmedi, belgelendi
- Motor teknolojisi seçilmedi

## DEĞİŞMEZLER — asla bozulmayacak
- Uygulama tshift_app ile bağlanır, asla tshift ile
- audit_log append-only; UPDATE/DELETE yok
- Parola ve JWT_SECRET yalnızca ortam değişkeni
- Her kiracı tablosunda RLS + FORCE
- .ps1 dosyaları saf ASCII, PowerShell 5.1 uyumlu

## SON DOĞRULAMA
<komut ve sonuç, tarihiyle>

## KANITLANMAMIŞ RİSKLER
<test edilmemiş varsayımlar>
```

### Pratik kural

| Durum | Ne yapmalı |
|---|---|
| Yeni ve ilgisiz iş (örn. motor) | **Yeni pencere.** `DEVIR.md` + ilgili dosyaları ver. |
| Aynı iş, küçük devam | Aynı pencerede kal. Karar bağlamı hâlâ geçerli. |
| Sohbet uzadı, yavaşladı | `DEVIR.md`'yi güncelle, yeni pencere aç. |
| **Aynı hata iki kez düzeltildi** | **Dur.** Yeni pencere ve kök neden. Bu, bağlamın bozulduğunun en net işareti. |
| Doküman ile kod çelişiyor | Kod yazma, önce bana sor hangisi doğru. |

Son satır belgenin en iyi maddelerinden biri: aynı hatanın iki kez düzeltilmesi, bağlamın kirlendiğinin sinyalidir. Tazelemek, ısrar etmekten ucuzdur.

---

## 9. Sonuç

Belge, **kendi başına** bir katkı değil — söylediklerinin çoğunu zaten yapıyoruz ve bir kısmı bizim ölçeğimize uymuyor. Ama **iki yerde gerçekten değerli:**

1. **§6 — bağımsız oracle.** Testleri kodu yazanın yazması bizde gerçek bir açık ve bir kere gerçekleşti (D6). Çözümü de bedava: kabul ölçütünü sen yaz.
2. **§8 — motor mimarisi.** Henüz yazmadığımız parçaya, doğru zamanda, doğru şekli veriyor. Bağımsız doğrulayıcı + V01–V12 + metamorfik testler.

Ve belgenin kendi sonuç cümlesi, bizim bu projede fiilen yaptığımız şeyin iyi bir tarifi:

> "En değerli ekip alışkanlığı, her ajan hatasını yalnızca düzeltmek değil, onu tekrar edilemez hale getiren test, kural veya araç eklemektir."

Dört hatamızın dördünde de tam olarak bunu yaptık: süper kullanıcı hatası → rol testi; `sub` claim hatası → `HttpSinirTestleri`; DLL kilidi → `TEST.ps1`; Docker bağlamı → `.dockerignore`. Bu alışkanlık zaten yerleşmiş durumda. Belge onu bize öğretmiyor, **doğruluyor** — ki Yılmaz'ın sorusu açısından bu da bir kazanç.
