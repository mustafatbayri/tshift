# BURADAN BAŞLA

> **Yeni bir sohbet penceresi ya da başka bir yapay zekâ isen: önce bu sayfayı
> baştan sona oku, sonra aşağıdaki okuma sırasını takip et. Kod yazmaya
> başlamadan önce `02-DEGISMEZLER.md` dosyasını mutlaka okumuş olmalısın.**

**Son güncelleme:** 2026-09-16 (fikstürler + test iskeleti yazıldı; 7 test bilerek kırmızı)
**Son sürüm etiketi:** `v0.8-devir`
**Depo:** `github.com/mustafatbayri/tshift` (özel) · yerel kök: `C:\Users\PC\Desktop\Tshift`

---

## 1. Bu proje nedir, tek paragrafta

**T-Shift**, çok kiracılı (multi-tenant) bir yapay zekâ destekli vardiya
planlama ve optimizasyon SaaS ürünüdür. Teknovisor markası altında
geliştiriliyor. Ürün sahibi ve tek karar verici **Mustafa**: 11 yıllık BT ürün
müdürü, **yazılımcı değil** — kod yazmıyor, kod okumuyor. Bütün kod yapay zekâ
tarafından yazılıyor, Mustafa niyeti ve iş kurallarını doğruluyor.

Bunun iki pratik sonucu var ve ikisi de bu projedeki her kararı şekillendiriyor:

1. **Mustafa'ya kod gösterilerek onay alınamaz.** Doğrulama, testlerin ve
   dokümanların Türkçe iş cümlelerine çevrilmesiyle olur.
2. **Yapay zekâ kendi hatasını göremez.** Bu yüzden bu projede kurallar
   yazıya değil, **otomatik kontrollere** bağlanır. Detay: `05-HATA-OTOPSILERI.md`.

---

## 2. Şu anda neredeyiz

**Dikey dilim tamamlandı.** Veritabanından ekrana kadar bütün katmanlar bağlı
ve çalışıyor:

```
PostgreSQL + RLS → EF Core → Kimlik → Yetki/Kapsam → Denetim kaydı → API → Next.js arayüz
```

- **39/39 test yeşil.** Hepsi gerçek PostgreSQL'e karşı koşuyor, hiç mock yok.
- **CI çalışıyor (14 Eylül).** Her `git push` sonrası testler GitHub Actions'ta
  kendiliğinden koşuyor — kurallar artık öneri değil **kapı**.
- **Tek komutla ayağa kalkıyor:** `docker compose --profile tam up --build`
- **Çalışan ekranlar:** giriş, çalışan listesi (rol bazlı farklı davranıyor),
  yeni çalışan kaydı.
- **Yılmaz'a inceleme paketi gönderildi** (`05-inceleme/v1-2026-09-11/`).

**Henüz yazılmadı:** vardiya optimizasyon motoru, plan editörü, kural yönetimi,
kullanıcı/rol yönetim ekranları.

**Gerçek müşteri verisi elimizde (13–14 Eylül).** Bir seyahat acentesinin 3,5
aylık PDKS ve vardiya planı. Analiz edildi, **529 kural ihlali** bulundu.
Bulgular ve Mustafa'nın kapsam kararları: **`07-GERCEK-VERI-BULGULARI.md`**
— motor yazılmadan önce okunmalı.

⚠ `07-motor/` klasöründe **motor yok**, analiz araçları var. Bkz.
`07-motor/OKU-BENI.md`.

**Fikstürler yazıldı (16 Eylül).** `08-motor-testleri/v5/fikstur/` — 11 JSON
dosyası + ortak sahne. Kod değil veri; motor hangi dille yazılırsa yazılsın
aynı dosyalar koşar. Biçim: `08-motor-testleri/v5/fikstur/OKU-BENI.md`.

**Test iskeleti yazıldı (16 Eylül).** `08-motor-testleri/v5/testler/` —
pytest çatısı (A1, A3, A4, A6, A7, A8, A9) ve xUnit taslakları (A2, A10, A11,
A12). Koşuyor ve **bilerek kırmızı**:

```
py -m pytest -q   →   7 failed, 3 passed, 4 skipped
```

7 kırmızı = motor yok (§16.4 kırmızı kanıt). 3 yeşil = paketin **kendi**
sağlık kontrolü, motorsuz da geçmeli: fikstürler yükleniyor mu, fikstürde
geçen her `kontrol` adının gövdesi var mı, motor yokluğu sessizce değil
açıkça söyleniyor mu. 4 atlanan = backend senaryoları, xUnit tarafında
koşacak. Motor gelince **tek dosya** değişecek: `motor_istemci.py`.

⚠ **Bu paket CI'da koşmuyor — bilerek.** CI şu an yalnız `dotnet test`
çalıştırıyor (A-4). Kırmızı bir paketi kapıya bağlamak "main her zaman yeşil"
kuralını bozardı. C# taslakları da bu yüzden `.cs.taslak` uzantılı —
derleyici görmez, CI kırılmaz. Ayrıntı: `08-motor-testleri/v5/testler/OKU-BENI.md`.

**Altın senaryolar ONAYLANDI (15 Eylül).** Spec §16.3'teki A1–A12'nin beklenen
sonuçları Türkçe kabul cümlelerine çevrildi ve Mustafa tarafından **tek tek
onaylandı**: `08-motor-testleri/v5/KABUL-OLCUTLERI.md` (dondurulmuş).
Onay turunda **on ürün kararı** doğdu (K-8…K-17), **bir karar geri alındı**
(K-1), dört senaryo ve ortak sahne **baştan yazıldı**.

⚠ **Motorun hiçbir davranışı hâlâ korunmuyor.** Zincir (kabul ölçütü →
fikstür → test) tamam ama ucu boşta: motor yok, bu yüzden 7 senaryo kırmızı.
Kabul ölçütü bir taahhüttür, bekçi değil; bekçi ancak test **yeşile
döndüğünde** doğar.

**Devir denetimi artık betik (14 Eylül) ve 16 Eylül'de İLK KEZ gerçekten
koştu.** `DENETIM.py` — bu paketteki test adlarını, sayıları, dosya yollarını,
sürüm atıflarını ve commit durumunu makineye kontrol ettirir.

İlk gerçek koşusunda **17 hata** buldu: iki dokümandaki 17 atıf hâlâ
dondurulmuş **v2** ve **v4** sürümlerini gösteriyordu. O düzeltmeler aslında
yapılmıştı ama makineye hiç gönderilmemişti — ve **dosya boyutu değişmediği
için** (`v2` ile `v5` aynı uzunlukta) hiçbir boyut kontrolü bunu yakalayamazdı.
Hepsi düzeltildi. Kalan 14 uyarı tarihsel dosyalarda, aksiyon gerektirmiyor.

⚠ **Her oturumun sonunda koşturulmalı.** Göz bu 17 satırı üç oturumdur
görmedi; betik ilk koşuşunda gördü.

**Çalışma biçimi kararı (15 Eylül).** Yazan pencerenin yanına **yazmayan** bir
gösterge penceresi açılıyor: günlükler sürekli, testler talep üzerine — §5b.
Paralel ikinci **yazıcı** ajan (opencode vb.) **reddedildi**; R5'i yeniden
açıyor. Salt-okunur inceleyici Aşama 2'ye ertelendi, ölçüm şartıyla.
**Ürün kodu değişmedi, test eklenmedi.** Gerekçe:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

## 3. Sıradaki tek adım

> **Şartname v1.4 (A-15).** Test iskeleti hazır ve kırmızı; sıradaki iş,
> motorun yazılabilmesi için şartnamedeki eksik alanları kapatmak.
>
> 1. **Oku:** `08-motor-testleri/v5/KABUL-OLCUTLERI.md` §8 (on maddelik liste,
>    dondurulmuş) ve `06-ACIK-RISKLER.md` A-15.
> 2. **Yaz:** `02-spec/v1.4-master-spec.md`. **v1.3'e dokunulmaz** — sürümleme
>    kuralı: üzerine yazma, yanına yaz (`SURUMLEME.md`).
> 3. **Kapatılacak eksikler:** `leaves` durum alanı (K-9), kabul edilmiş ihlal
>    (K-10/K-16), `en_iyi_plan`, mola penceresi, `MOLA_KAPSAMASI` sert→yumuşak
>    (K-14), **§6 kural kataloğuna `yasal` sütunu** (K-17), yayın kapısı,
>    `TERCIH_KARSILAMA` yeniden değerlendirmesi (K-13), %95 eşiği (K-8),
>    artı T-1…T-8 iç tutarsızlıkları.
> 4. **Karara bağlanacak açık tasarım sorusu:** `yasal` bayrağı **kuralın mı
>    eşiğin mi** özelliği? `GUNLUK_AZAMI` için kanunî tavan 11, bizim
>    varsayılanımız 9 — 9'u aşmak firma kuralı ihlali, 11'i aşmak yasal ihlal.
>    Tek bayrak bu ikisini ayıramıyor.
> 5. Sonra ürünün doğrulayıcısı, sonra çözücü (M-09).
>
> ✅ **Tamamlananlar:** fikstürler (11 dosya + ortak sahne, 16 Eylül) ve test
> iskeleti (pytest + xUnit taslakları, 16 Eylül). Her ikisi de kendi
> denetleyicisinden geçiyor.
>
> **Paralelde açık kalanlar:**
>
> - **İki hukuki yorum uzman gözü bekliyor** (K-4 mola eşiği, K-17 yasal
>   sınıflandırma). v1.4'ü bloke etmiyor; sahaya çıkmadan önce şart.
> - ✅ **`DENETIM.py` 16 Eylül'de ilk kez gerçekten koştu** ve 17 hata buldu
>   (hepsi düzeltildi). Her oturumun sonunda koşturulmalı:
>   `cd C:\Users\PC\Desktop\Tshift` sonra `py DENETIM.py`. Kalan 14 uyarı
>   tarihsel dosyalarda, aksiyon gerektirmiyor.
> - **2 pencere kurulumu yapılmadı** — karar 15 Eylül'de verildi, komutlar §5b'de.
> - **pytest paketi CI'a bağlanmadı** — motor yeşile çevirene kadar bağlanmayacak.
> - A-6 mutasyon raporu, A-2 ve A-3 eksik bekçiler.
>
> Tam öncelik listesi: `06-ACIK-RISKLER.md` sonundaki tablo.

---

## 4. Okuma sırası

Aşağıdaki sıra, bir işe başlamadan önce ne kadar okuman gerektiğini söyler.
**Hepsini okumak zorunda değilsin** — yapacağın işe göre seç.

| Sıra | Dosya | Ne zaman okumalısın |
|---|---|---|
| 1 | Bu sayfa | Her zaman |
| 2 | `02-DEGISMEZLER.md` | **Her zaman.** Kod yazmadan önce mutlaka. |
| 3 | `01-PROJE-KIMLIGI.md` | Ürün kararı, kapsam ya da öncelik konuşulacaksa |
| 4 | `03-MIMARI-KARARLAR.md` | Mevcut bir yapıyı değiştirecek ya da yeni katman ekleyeceksen |
| 5 | `04-TEST-HARITASI.md` | Test yazacak ya da mevcut bir testi değiştireceksen |
| 6 | `05-HATA-OTOPSILERI.md` | Yeni bir savunma/kontrol tasarlayacaksan |
| 7 | `06-ACIK-RISKLER.md` | Yayına çıkma, ölçek ya da güvenlik konuşulacaksa |
| 8 | `08-URUN-KARARLARI.md` | **Bir ürün davranışının neden böyle olduğunu soruyorsan.** K-serisi: verilmiş kararlar, gerekçeleriyle |
| 9 | `oturumlar/` | Belirli bir değişikliğin ne zaman ve neden yapıldığını arıyorsan |

### Deponun tamamı — nerede ne var

> **Bu klasör (`00-DEVIR/`) şartnameyi, demoyu ya da kodu İÇERMEZ; onlara
> İŞARET EDER.** Devir paketi bir harita, arşiv değil. Aşağıdaki tablo o
> haritanın tamamıdır.

| Yol | İçerik | Ne zaman aç |
|---|---|---|
| **`02-spec/v1.3-master-spec.md`** | **YÜRÜRLÜKTEKİ ŞARTNAME — 17 bölüm, son karar.** §3 roller ve yetki matrisi · §6 kural kataloğu (36 kural kodu, parametreleriyle) · **§6.3 gece yarısını aşan vardiya + DST modeli** · §8 veri modeli (50 tablo) · §9 ekranlar · **§11 motor sözleşmesi** (`/solve`, çözümsüzlük teşhisi, **§11.2 lookback**, **§11.7 idempotency + onarım**) · **§16 test stratejisi ve 12 altın senaryo** · §17 sürüm notları. | **Motor, kural ya da ekran işine başlamadan ÖNCE.** v1.0–v1.2 aynı klasörde (geçmiş korunuyor). |
| **`02-spec/v0-koken-...Analiz_v2.docx`** | **KÖKEN DOKÜMANI — 27 bölüm.** Projenin doğduğu analiz. Master Spec'in kapsamadığı yerde **hâlâ kaynak**: §8 sektörel kural paketleri (çağrı merkezi/perakende/üretim) · §23 Faz 0–10 geliştirme planı · §25 12 haftalık yol haritası · §20 riskler. | Gerekçe, fazlama ya da sektör paketi sorusu varsa. **Çeliştiğinde Master Spec kazanır** (§17). |
| `03-demo/v2-html/tshift-demo-v2.html` | **Çalışan demo** — 15 ekran, iki operasyon (çağrı merkezi + otel), sürükle-bırak takvim. Tek HTML dosyası, tarayıcıda açılır. | Ekran tasarımı ya da akış konuşulacaksa. Ürünün görsel dili burada. |
| `01-spike/` | **Motor fizibilite testleri** (7–8 Eylül) — CP-SAT vs greedy karşılaştırması, ölçek testleri (200→2000 kişi), otel senaryosu. Kronoloji ve ölçülen sayılar `01-spike/README.md`'de. | Motor yazılmadan **önce mutlaka.** Teknoloji kararının dayanağı burada. |
| `04-kod/` | **Çalışan uygulama** — backend (.NET 10), frontend (Next.js 16), veritabanı betikleri, testler, Docker | Kod yazılacaksa |
| `05-inceleme/v1-2026-09-11/` | **Yılmaz'a gönderilen inceleme paketi** — 8 soru, 4 hata otopsisi, bilinen açıklar | Dış inceleme konuşulacaksa |
| `06-veri/` | **Gerçek müşteri verisi** (PDKS + plan) ve türetilen çıktılar. ⚠ **`.gitignore` içinde — git'e girmez.** | Veri analizi yapılacaksa |
| `07-motor/` | ⚠ **Motor YOK.** Geçmiş planları ölçen analiz betikleri. Bkz. `07-motor/OKU-BENI.md` | — |
| **`08-motor-testleri/`** | ⚠ **Motor YOK; testler koşuyor ama bilerek kırmızı.** Şartnameden türetilmiş **kabul senaryoları** (A1–A12): motorun ne yapması gerektiğinin, motor yazılmadan önce ve motora bakmadan yazılmış hâli. **`08-motor-testleri/v5/` onaylanmış ve güncel**; v1–v4 dondurulmuş. İçinde: `KABUL-OLCUTLERI.md` (onaylı cümleler) → `08-motor-testleri/v5/fikstur/` (11 JSON + ortak sahne) → `08-motor-testleri/v5/testler/` (pytest çatısı + `08-motor-testleri/v5/testler/backend-taslak/` C# taslakları). Onay turunun özeti `ONAY-DURUMU.md`'de. Bkz. `08-motor-testleri/OKU-BENI.md` ve `08-motor-testleri/v5/testler/OKU-BENI.md` | Motor ya da doğrulayıcı işine başlamadan **ÖNCE** |
| **`DENETIM.py`** | **Devir paketi denetimi.** §5'teki ritüelin 5. maddesini makineye yaptırır. `py DENETIM.py` | Devire "tamam" demeden önce, her seferinde |
| `00-arsiv/` | Dondurulmuş eski sürümler | Geçmiş aranıyorsa |
| `DEGISIM-GUNLUGU.md` | Kilometre taşları, en yeni en üstte | "Ne zaman ne değişti" |
| `RISKLER-VE-ONLEMLER.md` | 15 hata sınıfı, savunma hatları, **kırmızı çizgiler §6** | Veri/sır/migration'a dokunmadan önce |
| `SURUMLEME.md` | Hata yapılırsa nasıl geri dönülür | Bir şey bozulduğunda |
| `KALITE-ARASTIRMASI-DEGERLENDIRME.md` | Sahanın kalite pratiklerinin bu projeye göre değerlendirmesi | Test/süreç tasarımı yapılacaksa |

**Git etiketleri** `v0.1-kiracilik` … `v0.8-devir` — her kilometre taşı
işaretli, geri dönülebilir.

---

## 5. Bu dokümanların çalışma kuralı

Bu klasör bir **özet** değil, bir **devir paketidir**. İki farklı şey:

- Özet, benim yazdığım düz yazıdır. İçinde bir yanlış varsayım varsa sonraki
  pencereye sessizce taşınır ve orada doğru sanılır.
- Devir paketi **doğrulanabilir** olmak zorundadır. Bu yüzden buradaki her
  iddia ya bir **test adına**, ya bir **dosya yoluna**, ya da bir
  **çalıştırılabilir komuta** bağlıdır.

**Kural:** Bu klasöre, karşılığında çalıştırılabilir bir kanıt gösteremediğin
hiçbir cümle yazılmaz. Kanıtı olmayan bilgi `06-ACIK-RISKLER.md` altına,
"kanıtlanmamış" etiketiyle gider.

### Güncelleme ritüeli

Mustafa **"aktarım dosyasını güncelle"** dediğinde şunlar yapılır:

1. `oturumlar/YYYY-AA-GG-<is-parcasi>.md` dosyası yazılır — o oturumda
   **hangi dosya neden değişti, hangi test eklendi, hangi karar verildi,
   hangi öneri REDDEDİLDİ.** Bu dosyalar **asla yeniden yazılmaz.**
2. Değişen şeye göre `02`–`07` arası ilgili dosyalar güncellenir.
3. Bu sayfadaki **"Şu anda neredeyiz"** ve **"Sıradaki tek adım"** bölümleri
   yenilenir. Bu iki bölüm her zaman güncel olmak zorundadır — devir
   paketinin geri kalanı bu ikisi yanlışsa işe yaramaz.
4. `DEGISIM-GUNLUGU.md`'ye kilometre taşıysa satır eklenir, etiket atılır.
5. **DENETİM — atlanmaz, ve artık elle yapılmıyor:**

   ```
   cd C:\Users\PC\Desktop\Tshift
   py DENETIM.py
   ```

   Yedi kontrolü makine yapar: test adlarının `DisplayName` ile birebir
   eşleşmesi, sayı tutarlılığı, dosya yollarının varlığı, değişmez özet
   tablosu, günlük adlandırması, değişim günlüğünün tazeliği ve **commit
   edilmemiş devir dosyası** olup olmadığı. Çıkış kodu 0 değilse devir
   "tamam" değildir.

   Betiğin yapamadığı iki şey elde kalır:
   - **Ölçüm değiştiyse tahmin edilmez, yeniden koşulur.**
   - Betik *tutarlılığa* bakar, *doğruluğa* değil. Tutarlı bir yanlış yine
     yakalanmaz; onu ancak iddiayı kaynağıyla karşılaştırmak yakalar.

> ⚠ **Yazdım ≠ gönderdim ≠ commit ettim.** Üçü ayrı adımdır ve üçü de
> doğrulanır. 14 Eylül'de Mustafa'nın kapsam kararlarının tamamı yerel kopyada
> güncellenmiş ama makineye hiç gitmemişti; denetim olmasa sessizce
> kaybolacaktı. Bkz. `oturumlar/2026-09-14-veri-analizi.md` §10.

---

## 5b. PENCERE PROTOKOLÜ

**Karar: 14 Eylül 2026.** Uzun sohbetlerde bağlam kaybını önlemek için iş,
pencereler arasında devredilir. Kurallar:

### Ritim: iş parçası başına bir pencere, SIRALI

Motor sözleşmesi bir pencere, CI+testler bir pencere, ekranlar bir pencere —
ama **hepsi sırayla.** Aynı anda **tek aktif pencere** olur.

| Durum | Ne yapılır |
|---|---|
| Yeni ve ilgisiz iş parçası | **Yeni pencere.** Bu sayfayı oku, devam et. |
| Aynı işin küçük devamı | Aynı pencerede kal |
| Sohbet uzadı / yavaşladı | Günlüğü yaz, yeni pencere |
| **Aynı hata iki kez düzeltildi** | **Dur.** Bağlamın kirlendiğinin en net işareti. |
| Doküman ile kod çelişiyor | Kod yazma; hangisinin doğru olduğunu Mustafa'ya sor |

### Açılış beyanı — yeni pencere işe başlamadan önce

> **Yeni pencere, dosya yazmadan önce şunu söyler:** hangi dosyaları okudum,
> sıradaki adımı nasıl anladım, hangi varsayımla başlıyorum.

**Neden (karar: 14 Eylül 2026):** Aşağıdaki tablo *"doküman yanlış başlarsa
yakalamaz"* diyor ve bu açık kapalı değildi. Testler başlangıcı yönlendirmez,
doküman da yanlış anlaşılmayı göremez. Açılış beyanı **Mustafa'nın**
görebileceği tek an: iş yapılmadan önce.

Bedeli bir mesaj, getirisi yanlış yöne gidilmiş bir oturum. 14 Eylül'de
kendiliğinden yapıldı ve işe yaradı — şartnamedeki bir çelişki daha ilk
mesajda görüldü.

### Yazma hakkı

> **Aynı anda yalnız bir pencere dosya yazar ve commit eder.**
> Devredilen pencere **salt-okunur** olur: soru cevaplayabilir, dosya yazamaz.

Devredilen pencere hemen kapatılmaz — **geri dönüş yoludur.** Yeni pencere
devir paketini okuyup işe başladığını gösterene kadar açık kalır. Devir eksik
çıkarsa oraya dönülüp tamamlanır.

### Geri bildirim yüzeyleri — iki pencere, biri yazmaz

**Karar: 15 Eylül 2026.** Gerekçe, elenen alternatif ve kanıt durumu:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

Aktif pencerenin yanında **ikinci bir pencere** açılır. Bu pencere ajan
değildir: dosya yazmaz, komut almaz, soru cevaplamaz. Yalnız **göstergedir.**
Amacı tek: kırmızıyı saatler sonra değil dakikalar içinde fark etmek.

| Yüzey | Komut (`04-kod` içinde) | Sürekli mi |
|---|---|---|
| **Sunucu günlükleri** | `docker compose logs -f` | ✅ Sürekli açık |
| **Testler** | `.\TEST.ps1` | ❌ **Talep üzerine** |

⚠ **Testler neden sürekli koşmaz:** §7'ye göre `TEST.ps1` API'yi **önce
durdurur.** Sürekli koşan bir test izleyicisi geliştirme kipindeki API'yi
sürekli düşürür. Başka depolarda gördüğünüz "sürekli koşan test penceresi"
kurgusu bu depoda **olduğu gibi kurulamaz.**

**Bunun doğurduğu kural — asıl madde budur:**

> **Ajan "bitti" demeden önce `.\TEST.ps1`'i kendisi koşar ve çıktısını
> rapor eder.** Test çıktısını pencereler arasında elle taşıyan insan,
> zincirin en zayıf halkasıdır.

**Ne DEĞİLDİR:** ikinci bir *yazıcı* ajan değildir. Paralel ajan modeli
(kod bir ajanda, hata ayıklama başka bir ajanda) 15 Eylül'de değerlendirildi
ve **reddedildi** — aşağıdaki tabloda R5 kapalıdır ve onu yeniden açacak
ölçülmüş bir gerekçe yoktur. Araç tarafı: `06-ACIK-RISKLER.md` ·
📌 Araç kararı.

**Kapı değil, hız.** CI (A-4) zaten kapıdır ve 14 Eylül'de yeşil yandı. Bu
karar yeni bir kapı eklemez; **kırmızının fark edilme süresini** kısaltır.
İkisi farklı şeylerdir, biri diğerinin yerine geçmez.

### Günlük dosyası adlandırma

Aynı gün birden çok oturum olabilir. **İki pencere asla aynı dosyaya
yazmaz:**

```
oturumlar/2026-09-14-veri-analizi.md
oturumlar/2026-09-15-motor-sozlesmesi.md
oturumlar/2026-09-15-ci-ve-testler.md     ← aynı gün, ayrı iş, ayrı dosya
```

İndeks dosyası **bilerek yok** — olsaydı çakışan dosya o olurdu. Kronolojik
sıra dosya adından çıkar.

**Paylaşımlı tek dosya bu sayfadır** (`00-BURADAN-BASLA.md`), çünkü "şu an
neredeyiz" tek yerde olmak zorunda. Onu yalnız **aktif** pencere günceller.

### Pencereler arası kopukluk — asıl güvence ne

Yılmaz'ın *"bloklar arası ilişki kopar"* itirazının pencere seviyesindeki
hâli. Cevap da aynı yerden gelir: **kopmayı engelleyemezsin, gürültülü
yaparsın.**

| Ne | Ne işe yarar | Neyi yaramaz |
|---|---|---|
| **Doküman** (`00-DEVIR/`) | Yeni pencerenin **doğru başlamasını** sağlar | Yanlış başlarsa yakalamaz |
| **Açılış beyanı** | Yanlış başlangıcı **iş yapılmadan** yakalar | Sessiz kalan varsayımı göremez |
| **`DENETIM.py`** | Dokümanın **kendi içinde tutarsızlığını** yakalar | Tutarlı bir yanlışı göremez |
| **Testler** (39 + M0–M6) | Bir ilişki bozulursa **kırmızı yanar** | Başlangıcı yönlendirmez |

**Asıl güvence testlerdir, doküman değil.** Doküman iyi niyeti taşır; test
yanlışı yakalar. Bu yüzden **CI (A-4) pencere protokolünün önkoşuludur:**
pencere değişince "testleri çalıştırmayı hatırlayan bağlam" ortadan kalkar,
ve tam o anda otomatik kapıya en çok ihtiyaç duyulur.

### Devirde bilinen riskler

| # | Risk | Önlem | Kapalı mı |
|---|---|---|---|
| R1 | Yazıya dökülmemiş sezgi kaybolur | Oturum günlüğü | 🟡 Tanım gereği tam kapanamaz |
| R2 | Verilmiş karar yeniden verilir | 02/03/06 + **reddedilenler kaydı** | ✅ |
| R3 | Bozuk bir şey sağlam sanılır | 06'da açık durum işaretleri | ✅ |
| R4 | Mevcut kod bozulur | Testler | ⚠️ **CI koşana kadar zayıf** |
| R5 | İki pencere yazar, sürüklenme | Tek aktif pencere kuralı | ✅ *(15 Eylül: paralel ajan modeli değerlendirildi, reddedildi — teyit)* |
| R6 | Devir dokümanının kendisi yanlış olur | Her iddia bir teste/dosyaya/komuta bağlı **+ `DENETIM.py`** | ✅ *(M0'da, sonra 14 Eylül'de betikle)* |
| R7 | **Dokümanlar büyür, okumak kendisi bağlam sorunu olur** | Giriş 1 sayfa; derin dosyalar talep üzerine; **düzenli sadeleştirme** | 🔴 **Eşikte** — 9 dosya |

**R7 için kural:** Yeni bir devir dosyası açmadan önce sor — *bu, var olan bir
dosyanın bölümü olabilir mi?* `00-DEVIR/` dokuz dosyayı geçerse sadeleştirme
zamanı gelmiştir.

⚠ **14 Eylül: dokuzuncu dosya açıldı** (`08-URUN-KARARLARI.md`). Soru soruldu
ve cevabı "hayır" çıktı — ürün kararı mimari karar değil, ve adı içeriğine
uymayan dosya bu projede zaten bir kez pahalıya mal oldu. **Onuncu dosyadan
önce sadeleştirme yapılmalı.** `DENETIM.py` bunu otomatik uyarıyor.

---

## 6. Yeni pencere için çalışma kuralları

Bu kurallar Mustafa ile üzerinde anlaşılmıştır; tartışmaya açık değil.

1. **Mustafa yazılımcı değildir.** Komutlar tam olarak, kopyalanıp
   yapıştırılacak şekilde verilir. "Şunu yapmalısın" değil, "şu komutu şu
   klasörde çalıştır" denir.
2. **Versiyonla, üzerine yazma.** Dosyalar güncellenerek değil,
   versiyonlanarak ilerler. Her kilometre taşı: git etiketi + değişim günlüğü
   satırı. Şartname değişikliği yeni bir sürüm dosyası olur.
3. **Kabul ölçütü önce.** Kod yazmadan önce "bu doğru çalışıyorsa ne
   görmeliyiz" cümlesi Türkçe yazılır ve Mustafa onaylar. Test o cümlenin
   çevirisidir.
4. **Bir hata bulunduğunda düzeltmek yetmez.** O hatanın bir daha sessizce
   geri gelmesini engelleyen kalıcı bir kontrol eklenir. Bu projenin işleyiş
   biçimi budur; örnekleri `05-HATA-OTOPSILERI.md`'de.
5. **Kırmızı çizgiler** `RISKLER-VE-ONLEMLER.md` §6'da. Okumadan veri, sır
   ya da migration konusuna dokunma.
6. **Anlaşılmayan komut çalıştırılmaz** — özellikle `rm`, `del`, `format`,
   `Remove-Item`, `--force` içerenler. Bu projede `git reset --hard` ve
   `git push --force` yasaktır.

---

## 7. Ortam gerçekleri — kaybedilen zamanın çoğu buradan geldi

Bunlar "bilinmezse tekrar tekrar saat kaybettiren" şeyler:

| Gerçek | Sonucu |
|---|---|
| Windows 11, **Windows PowerShell 5.1** (PowerShell 7 **değil**) | `.ps1` dosyaları **saf ASCII** olmalı (5.1 dosyayı ANSI okur, Türkçe karakter ayrıştırıcıyı bozar). `-SkipHttpErrorCheck` gibi PS7'ye özgü parametreler kullanılamaz. |
| `dotnet test` sırasında API çalışıyorsa DLL kilidi | Testler **`TEST.ps1`** ile koşulur — API'yi önce durdurur. Doğrudan `dotnet test` çağırma. |
| Docker bağlamına Windows `bin/`/`obj/` girerse restore bozulur | `04-kod/.dockerignore` var, silinmeyecek |
| PostgreSQL yerelde 5432'de olabilir | Kutu **5433**'te dinliyor |
| Mustafa'nın `.env.local` dosyasını uzak araçlar yazamıyor | O dosyayı Mustafa'nın kendisi oluşturur |

Kurulu sürümler: git 2.55 · .NET SDK 10.0.401 · Node 24.20 · npm 11.19 ·
Docker 29.7.2 · Python 3.14.7

---

## 8. Uygulamayı çalıştırma

**İnceleme kipi — her şey kutuda, tek komut:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose --profile tam up --build
```
→ `http://localhost:3000` · firma: `anadolu-cm` · parola: `TShift2026!Deneme`

**Geliştirme kipi — yalnız veritabanı kutuda:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose up -d
```

**Testler:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
.\TEST.ps1
```

**Yalıtım kanıtı (iki firma birbirini görüyor mu):**

```
.\YALITIM-KANITI.ps1
```
