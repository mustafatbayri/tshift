# Oturum · 13–14 Eylül 2026 · veri analizi

**Başlangıç:** `v0.8-devir` · 39/39 test yeşil · A-14 açık (🔴)
**Bitiş:** kod değişmedi · **A-14 ve A-4 kapandı** · gerçek veri analiz edildi ·
analiz araçları yazıldı · **pencere protokolü kuruldu**

> Bu dosya **append-only**. Yeniden yazılmaz, yalnız eklenir.

---

## 1. Gerçek veri geldi — A-14 kapandı

Bir seyahat acentesinin **PDKS** (48 CSV, ~100 MB) ve **vardiya planı**
(71 Excel) dosyaları, Haziran–Eylül 2026.

**Veri git'e girmiyor:** `.gitignore`'a `06-veri/` eklendi. Gerekçe: git
geçmişi silinmez; bir kez commit edilen gerçek operasyon verisi geri alınamaz.

Bulguların tamamı: **`07-GERCEK-VERI-BULGULARI.md`** (anonim — isim, sicil,
firma adı yok).

### En önemli üç bulgu

| # | Bulgu | Sayı |
|---|---|---|
| B-1 | **Kapsama hesabı bozuk** — HC sayfası `#REF!` veriyor | 43 dosyanın 28'inde |
| B-2 | **Gece yarısını aşan vardiya** — varsayım değil, gerçek | 182 atama |
| B-8 | **Plan mola bilgisi taşımıyor** → net çalışma süresi hesaplanamıyor | tüm dosyalar |

B-1'in anlamı: ekip, *"saat 14:00'te kaç kişi sahada olacak"* sorusunu
**cevaplayamadan** plan yayınlıyor.

### ÇM2 sayfası — okunmuyor, ve sebebi kayda değer

- **SicilNo kolonu yok** — kişiler **adlarıyla** anahtarlanmış
- Başlangıç ve bitiş **ayrı kolonlarda**, 28 günlük (56 kolon)
- 43 dosyanın 24'ünde başlıklar dahil tamamen `#REF!`
- **`23:59` 137 kez geçiyor** — gece yarısını aşan vardiyayı Excel'de
  yazabilmek için `00:00` yerine yazılmış bir hack

Aynı çalışma kitabında **iki uyumsuz plan gösterimi** var ve biri isimle
anahtarlanıyor. Dönüştürücü bunu sessizce atlamıyor, **sayıp raporluyor**.

---

## 2. Mustafa'nın kapsam kararları

Tam liste `07-GERCEK-VERI-BULGULARI.md` §4c'de. Özet:

| Konu | Karar |
|---|---|
| Erlang-C ekranı | ❌ Kapsam dışı |
| Geçmiş veriden yoğunluk tahmini | ✅ Kapsam içi, önemli |
| Otel verisi analizi | ❌ Yapılmayacak — asıl veri çağrı merkezi + plan |
| Çok tüzel kişilik | ❌ Takılma — tek şirket mantığı |
| Anonimleştirme | ❌ Yapılmayacak |
| Tutarsız kod normalleştirme | ❌ Ağır katman yok — **editör ekranında kullanıcı düzeltir** |
| **Değişken planlama ufku** | ❌ **REDDEDİLDİ** — ufuk takvim ayını aşamaz, adalet penceresi ayın 1'inde başlar |
| **Mola planlama ve adil dağıtım** | ✅ **Yeni kapsam maddesi — ürünün 2. satış noktası** |
| Kadro devir hızı yönetimi | ✅ **Ürünün kritik özelliği — 1. satış noktası** |

---

## 3. ⚠ SÜREÇ KURALI: veri kapsam kararı vermez

**Mustafa'nın uyarısı (14 Eylül):**

> *"Sana bu dataları analiz amaçlı attım, bu datalardan bir varsayım çıkarıp
> kapsamı değiştirmen için değil. Tabii ki varsayımlarımız olacak ve kapsama
> ekleyeceğiz, ki yaptık — ama bu data üzerinden bir iş modeli kurmaya kalkma."*

**Bu haklı bir uyarıydı ve Claude bunu ihlal etmişti:** "plan ufku 7–35 gün
arası değişiyor, modelimiz bunu desteklemeli" önerisi (B-9) tam olarak veriden
iş modeli çıkarmaya kalkmaktı. Mustafa reddetti ve gerekçesi daha güçlüydü.

**Bundan sonraki kural:**

> Veriden **bulgu** çıkarılır, **kapsam kararı** çıkarılmaz.
> İkisi ayrı ayrı işaretlenir: *bulgu* = "veride şu var", *öneri* = "buna göre
> şunu yapabiliriz, karar senin".

---

## 4. Analiz araçları yazıldı — ve bir kez daha yanlış isimlendirildi

`07-motor/` altına üç dosya: `donusturucu.py`, `dogrulayici.py`,
`kurallar.json`.

**Ne yapıyorlar:** 69 Excel planını tek kanonik CSV'ye çeviriyor
(**4.625 vardiya, 98 kişi, 105 gün**), sonra kurallara karşı denetliyor.

### Sonuç: 529 ihlal

| Kural | Vaka | Kişi |
|---|---|---|
| Haftalık 45 saat aşımı (net, mola düşülmüş) | 274 | 50 |
| 6 günden fazla ardışık çalışma | 167 | 37 |
| Ardışık vardiyalar arası < 11 saat dinlenme | 88 | 27 |

**Doğrulandı (D6 disiplini):** V_ARDISIK bulgusu ham veriden tek tek teyit
edildi — sicil 1089, 10–17 Haziran sekiz gün arka arkaya. Gerçek.

### Doğrulayıcı kendi girdisini denetliyor

Veri kısmi (kişi başına dönemin %58'i kayıtlı). Doğrulayıcıya bunu **kendisinin
raporlaması** eklendi, ve yönü ayırt ediyor:

- **Yerel kontroller** (dinlenme, ardışık gün): eksik gün bunları *gizler,
  uydurmaz* → bulunanlar gerçek, **alt sınır**
- **Toplam kontrolleri** (haftalık saat, adalet): eksik gün toplamları düşürür
  → yine alt sınır, ama **adalet ölçümleri güvenilir değil** (0 saat = veri yok)

*Gerekçe: girdisinin ne kadar tam olduğunu bilmeyen bir doğrulayıcı, sessizce
yanlış güven verir.*

### ⚠ Yapılan hata: "motoru yazdım" denmesi

Claude bu betikleri *"motorun ilk parçası"* diye sundu ve `07-motor/` klasörüne
koydu. **Yanlıştı.** Motor plan **üreten** şeydir; bu betikler sadece **ölçer**.

Karıştırılan iki ayrı şey:
1. Bu betikler — müşterinin Excel şablonunu okuyan, testi ve sözleşmesi olmayan
   analiz araçları
2. **Ürünün doğrulayıcısı** (M-09) — bizim kanonik modelimizle çalışan,
   testleri ve sözleşmesi olan motor bileşeni

Ortak olan tek şey fikir; kod ortak değil. Ürün doğrulayıcısı yazılırken bu
betiklerin büyük kısmı atılır.

**Bu, M0 olayının aynası:** orada doküman koddan sapmıştı, burada Claude
saptırdı. Düzeltme: `07-motor/OKU-BENI.md` yazıldı, klasörde motor olmadığını
açıkça söylüyor.

**Açık karar:** `07-motor/` → `08-analiz/` yeniden adlandırma önerildi,
Mustafa henüz karar vermedi.

---

## 5. Kod değişikliği

**Yok.** Ürün kodunda hiçbir dosya değişmedi. 39/39 test durumu aynı.

## 6. Eklenen dosyalar

| Dosya | Ne |
|---|---|
| `.gitignore` | `06-veri/` eklendi (gerçek veri git'e girmez) |
| `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` | **Yeni** — anonim veri değerlendirmesi |
| `07-motor/donusturucu.py` · `dogrulayici.py` · `kurallar.json` | **Yeni** — analiz araçları |
| `07-motor/OKU-BENI.md` | **Yeni** — "burada motor yok" uyarısı |

## 7. Sıradaki adım

> **Motor sözleşmesi (A-10).** V01–V12 değişmez listesi Mustafa ile
> kesinleştirilecek, sonra girdi/çıktı şeması ve UNSAT biçimi yazılacak.
> Doğrulayıcı önce, çözücü sonra (M-09).
>
> Ayrıca hâlâ açık: **A-4 CI yeşile alınmadı** (dosya yazıldı, koşup koşmadığı
> doğrulanmadı).

## 8. Bu oturumun dersi

İki kez aynı hata yapıldı ve ikisi de aynı sınıftan:

| Ne | Nasıl düzeltildi |
|---|---|
| Veriden kapsam kararı çıkarmaya kalkmak (B-9) | Mustafa reddetti → §3'teki süreç kuralı yazıldı |
| Analiz aracına "motor" demek | `OKU-BENI.md` yazıldı |

**Ortak kök neden:** yapılan işi olduğundan daha ileri bir şeymiş gibi
adlandırmak. Bu, projede en çok korktuğumuz hata sınıfının (sessiz hata)
doküman tarafındaki hâli — kod yanlış değil, **kodun ne olduğuna dair iddia**
yanlış.

**Alınan önlem:** Bundan sonra her çıktı için iki soru ayrı ayrı cevaplanacak:
*"Bu ne yapıyor?"* ve *"Bu ne DEĞİL?"*

---

## 9. Gün sonu: A-4 kapandı, pencere protokolü kuruldu

**CI yeşil yandı (14 Eylül).** GitHub Actions koştu, 39 test + 7 mimari kuralı
geçti. **A-4 kapandı.** Kurallar artık öneri değil kapı.

### Pencere protokolü kararlaştırıldı

Mustafa'nın sorusu uzerine devir prosedürü netleştirildi ve
`00-BURADAN-BASLA.md` §5b'ye yazıldı. Özet:

| Konu | Karar |
|---|---|
| Ritim | **İş parçası başına bir pencere, SIRALI.** Aynı anda tek aktif pencere. |
| Yazma hakkı | Yalnız aktif pencere yazar/commit eder. Devredilen **salt-okunur**. |
| Devredilen pencere | Hemen kapanmaz — **geri dönüş yolu.** Yeni pencere işe başladığını gösterene kadar açık kalır. |
| Günlük adlandırma | `YYYY-AA-GG-<is-parcasi>.md`. İki pencere asla aynı dosyaya yazmaz. İndeks dosyası **bilerek yok** (çakışan o olurdu). |
| Paylaşımlı tek dosya | `00-BURADAN-BASLA.md` — yalnız aktif pencere günceller. |

### Claude'un geri aldığı tavsiye

Claude önce "hemen yeni pencereye geçelim" demişti. **Geri aldı:** pencereler
arası asıl güvence testlerdir, ve testleri zorla koşturan mekanizma (CI) o an
hiç çalışmamıştı. Pencere değişince "testleri çalıştırmayı hatırlayan bağlam"
ortadan kalkar — tam o anda otomatik kapıya en çok ihtiyaç duyulur.
Sıra ters kurulmuştu; önce CI, sonra devir.

*Mustafa'nın uyarısı: "Çok hızlı karar aldın." Haklıydı.*

### Devir riskleri yazıya döküldü

R1–R7 tablosu `00-BURADAN-BASLA.md` §5b'de. İkisi açık kaldı:
- **R1** yazıya dökülmemiş sezgi kaybı — tanım gereği tam kapanamaz
- **R7** dokümanların büyümesi — `00-DEVIR/` dokuz dosyayı geçerse
  sadeleştirme zamanı. *Bu oturumda R7 disiplini uygulandı: pencere protokolü
  için yeni dosya açılmadı, giriş sayfasının bölümü yapıldı.*

### Devir paketinin haritası tamamlandı

Mustafa sordu: *"Bu devir dosyasında projenin analiz dokümanı, demo
dokümanları falan da var değil mi?"*

**Cevap: devir paketi onları içermez, onlara işaret eder** — ve işaret listesi
eksikti. `03-demo/` (15 ekranlık çalışan demo) ve `01-spike/` (motor fizibilite
testleri) haritada hiç yoktu. `00-BURADAN-BASLA.md` §4'teki tablo deponun
tamamını kapsayacak şekilde yeniden yazıldı.

*Bu, R6'nın (devir dokümanının kendisi yanlış olur) ikinci yakalanışı — ilki
M0 olayıydı. İkisi de aynı yöntemle bulundu: dokümandaki iddiayı gerçekle
karşılaştırmak.*



---

## 10. DEVİR DENETİMİ — ve bulunan ciddi hata

Mustafa: *"Önce şu devir için oluşturduğun dosyalarda her şey tamam mı onu
bir netleştirir misin? Çok hızlı karar aldın."*

Haklıydı. Devir paketi "tamam" diye ilan edilmeden önce **denetlendi** ve
dört sorun çıktı.

### 🔴 D-1 · Kararların yazıldığı bölüm makineye HİÇ GİTMEMİŞ

`07-GERCEK-VERI-BULGULARI.md` dosyasının §4c bölümü — **Mustafa'nın 14 Eylül
kapsam kararlarının tamamının yazılı olduğu yer** — yerel kopyada güncellenmiş
ama makineye gönderilmemişti. Makinedeki sürüm 1.006 bayt, olması gereken
4.389 bayt.

**Kaybolacak olanlar:** analiz kapsamı kararı, çok tüzel kişilik kararı,
anonimleştirme kararı, yükleme formatı kararı, **REDDEDİLEN değişken ufuk
önerisi**, **SATIŞ NOKTALARI tablosu**, **MOLA MODELİ kapsam maddesi**.

**Kök neden:** Claude dosyayı yerelde düzenledi, sonra tekrar düzenledi, ama
yalnız bazı sürümleri gönderip commit etti. *Yerel kopya = makine kopyası*
varsayımı yanlıştı ve bunu hiç kontrol etmedi.

**Bu, R6'nın (devir dokümanının kendisi yanlış olur) üçüncü yakalanışı.**
Öncekiler: M0 (doküman olmayan bir testi gösteriyordu), depo haritası
(demo ve spike hiç yazılmamıştı).

### 🟡 D-2 · Bayat rakamlar

`07-GERCEK-VERI-BULGULARI.md` ilk analizin (43 dosya) rakamlarıyla kalmıştı;
oysa sonradan 69 dosyanın tamamı işlendi. Düzeltilenler:

| Ne | Eski (43 dosya) | Doğru (69 dosya) |
|---|---|---|
| İncelenen dosya | 43 | **69** |
| Kanonik vardiya ataması | 3.955 | **4.625** |
| Kişi | 86 | **96** |
| Kırık HC sayfası | 28 | **42** |
| HC hiç yok | 9 | **18** |
| Çalışan HC | 6 | **9** |
| Gece yarısını aşan | 175 | **182** |
| Farklı vardiya deseni | 17 | **18** |
| Kısa dinlenme vakası | 62 / 25 kişi | **88 / 27 kişi** |
| **Toplam ihlal** | — *(dosyada hiç yoktu)* | **529** |

**529 rakamı `00-BURADAN-BASLA.md` ve `06-ACIK-RISKLER.md`'de geçiyordu ama
kaynak dokümanda hiç yoktu.** Yani dokümanlar birbiriyle çelişiyordu.

### 🟡 D-3 · Test adı kısaltılmış

İki yerde `M0 - Baglanan rol super kullanici degil` yazıyordu; koddaki tam ad
`M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)`.
Tam metin araması bulamaz — **M0 olayının aynı tuzağı.** Düzeltildi.

**Kural:** Dokümanda geçen test adı, koddaki `DisplayName` ile **birebir**
aynı olmalı.

### 🟡 D-4 · Eski günlük adlandırması

`oturumlar/2026-09-12.md` yeni adlandırma kuralına uymuyordu
(`YYYY-AA-GG-<is-parcasi>.md`). `2026-09-12-devir-paketi.md` olarak
kopyalandı; eskisi silinecek.

### Denetim nasıl yapıldı — tekrarlanabilir olsun diye

1. Makinedeki dosyalar **geri alındı** (yerel kopyaya güvenilmedi)
2. Dokümanlardaki her test adı, koddaki `DisplayName` listesiyle karşılaştırıldı
3. Sayılar dosyalar arası tarandı (39/38, 529/343, 43/69 …)
4. Yerel ve makine kopyaları **bayt bayt karşılaştırıldı** → D-1 böyle bulundu
5. Değişen ölçümler **tahmin edilmedi, yeniden koşuldu** (HC durumu 69 dosyada)

### 📌 YENİ SÜREÇ KURALI

> **Devir "tamam" denmeden önce, dosyalar makineden GERİ OKUNUR ve
> karşılaştırılır.** Yerel kopyanın makineye gittiği varsayılmaz.
>
> Yazdım ≠ gönderdim ≠ commit ettim. Üçü ayrı adımdır ve üçü de doğrulanır.

Bu kural `00-BURADAN-BASLA.md` §5 güncelleme ritüeline eklenecek.


---

## 11. KÖKEN DOKÜMANI ORTAYA ÇIKTI — ve beş yanlış iddia düzeltildi

Mustafa: *"Analiz dokümanından kastım projenin en başında başladığımız
doküman."* — `Vardiya_Otomasyonu_Urun_Teknik_Analiz_v2.docx`, 27 bölüm,
~61.000 karakter.

**Bu doküman depoda hiç yoktu.** Ne `02-spec/`, ne `00-arsiv/` (boş, ama
README'si *"önceki dokümanlar buraya taşınacak"* diyor — hiç taşınmamış).

### Son iki günde "keşfedilen" şeylerin çoğu orada zaten yazılıydı

| Claude ne dedi | Köken dokümanında ne var |
|---|---|
| *"Spec'te UNSAT hiç geçmiyor, gerçek boşluk bu"* | §18.1: *"Çelişkili hard kural → INFEASIBLE beklenir"* — **üstelik Master Spec §11.3'te de vardı**, teşhisiyle birlikte |
| *"Mola modeli yeni kapsam maddesi"* | §18.1: *"Mola kapsaması: mola hakkı sağlanırken min role coverage altına düşülmez"* |
| *"Property-based test ekleyelim"* | §18 test katmanları tablosunda ayrı satır |
| *"G12 saat dilimi testimiz yok"* | §18.1: *"Gece yarısı ve DST"* golden senaryosu |
| *"A-13: kapsam envanteri hiç hesaplanmadı"* | §3 MVP/P1/P2 + §25 12 haftalık yol haritası — **ve Master Spec §14** |

**Beş madde. Hepsi yeniden icat edildi ve bir kısmı "yeni bulgu" diye sunuldu.**

### En utandırıcı olanı: arama hatası

*"Spec'te çözümsüzlük hiç geçmiyor"* iddiası, `grep "çözümsüz"` sonucu 0
döndüğü için kuruldu. Spec'te `Çözümsüzse` (büyük Ç) ve `cozumsuz` (Türkçe
karaktersiz) yazıyordu. **M4 testinin koruduğu Türkçe karakter tuzağına
Claude'un kendisi düştü.**

Doğru arama (büyük/küçük harf + Türkçe karakter normalize) yapılınca gerçek
boşluk listesi yediden beşe indi.

### Alınan kararlar (Mustafa)

| Konu | Karar |
|---|---|
| **Doküman otoritesi** | **Master Spec son karardır.** Köken dokümanı yürürlükte kalır, Master Spec'in sessiz kaldığı yerde kaynak. Çeliştiğinde Master Spec kazanır. |
| **MVP 3 alternatif** | **Net: 3 alternatif.** Köken §24'teki *"MVP tek öneri"* geçersiz. |
| Gece yarısı / DST | Gece yarısı tam yazılsın; DST **taşınabilir ama pasif** (IANA bölge adı, sabit ofset değil) |
| Lookback | Eklensin |
| Outbox | Kabul — bildirim katmanının teknik gereksinimi |
| **Tekrarlanabilirlik** | **Garanti verilmeyecek.** *"Bir kullanıcının pasife düşmüş olması bile her şeyi değiştirir; bunu açıklamakla vakit kaybedemez uygulama."* Yerine **plan kopyalama.** |
| Bildirim kanalları | uygulama içi + e-posta (v1) → SMS (gerçek müşteri) → WhatsApp (en son, belki hiç) |
| AI sağlayıcı bağımsızlığı | **Kapsam dışı** — model değiştirme düşünülmüyor |

### Mustafa'nın tekrarlanabilirlik kararı neden iyi

Motoru deterministik yapmaya çalışmak yanlış hedefti. Kullanıcının istediği
*"aynı planı tekrar uygula"* — bunun cevabı determinizm değil **kopyalama.**
Karar hem ürünü sadeleştirdi hem motordan gerçekçi olmayan bir söz kaldırdı.
Spec §11.7 bunu gerekçesiyle yazıyor.

---

## 12. Master Spec v1.3 yazıldı

`02-spec/v1.3-master-spec.md` — v1.2'ye dokunulmadı, yeni sürüm açıldı.
Bölüm numarası ve içindekiler tutarlılığı doğrulandı (1–17, birebir).

| # | Eklenen | Nereye |
|---|---|---|
| 1 | `GECE_YARISI_ASAN` + zaman modeli Z-1…Z-6 | §6.3 |
| 2 | DST taşınabilir-pasif, IANA bölge adı | §6.3 |
| 3 | Lookback 14 gün; eksikse motor çalışmaz | §11.2 |
| 4 | Onarım döngüsü: +2 deneme, sonra `cozumsuz` | §11.7 |
| 5 | İdempotency: `istek_anahtari` | §11.7 |
| 6 | **Tekrarlanabilirlik garanti EDİLMEZ** + gerekçe | §11.7 |
| 7 | **Plan kopyalama** | §9.7 |
| 8 | Bildirim kanal önceliği + outbox | §8.8 |
| 9 | **§16 Test stratejisi — 9 katman + 12 altın senaryo (A1–A12)** | §16 (yeni) |
| 10 | Doküman otoritesi kararı | §17 |

Veriden gelen bir uyarı da spec'e girdi: müşteri Excel'inde gece yarısını
yazabilmek için **`23:59` kullanmış (137 kez)**; içe aktarma bunu `00:00`'a
çevirmezse 1 dakikalık sistematik hata girer.

**Köken dokümanı depoya alındı:**
`02-spec/v0-koken-Vardiya_Otomasyonu_Urun_Teknik_Analiz_v2.docx`

### Devir paketinde düzeltilenler

| Yanlış iddia | Düzeltme |
|---|---|
| Birincil kaynak `v1.2` | → `v1.3`, ve köken dokümanı haritaya eklendi |
| *"UNSAT spec'te tanımsız"* | → §11.3'te teşhisiyle tanımlı |
| *"Mola yeni kapsam maddesi"* | → §6.2/§6.4'te zaten vardı |
| A-13 *"kapsam envanteri yok"* | → §14 + köken §3/§25 var; eksik olan **güncellenmesi** |
| A-10 *"motor sözleşmesi yazılmadı"* | → §11'de vardı, v1.3'te tamamlandı |
| A-5 *"zaman modeli tanımsız"* | → §6.3'te tanımlandı; **test hâlâ yok** |

## 13. Bu bölümün dersi

Beşinci "tamam" hatası ve kök neden her seferinde aynı: **kaynağı okumadan
konuşmak.** Bu sefer kaynağın var olduğu bile bilinmiyordu, çünkü depoda
değildi.

**Alınan önlem:** Devir paketindeki depo haritası artık köken dokümanını da
içeriyor, ve `00-BURADAN-BASLA.md` şartname satırında *"motor, kural ya da
ekran işine başlamadan ÖNCE"* uyarısı var.

**Genelleştirilebilir hâli:** *"Depoda yok"* ile *"yok"* aynı şey değil.
Bir şeyin var olmadığını iddia etmeden önce, nerede olabileceği de sorulmalı.
