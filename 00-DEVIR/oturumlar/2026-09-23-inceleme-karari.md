# 2026-09-23 · İnceleme döngüsü kararı — tadımcı kapandı

**İş parçası:** 15 Eylül'de ertelenen salt-okunur inceleyici ("tadımcı")
kararının kapatılması. Kod yazılmadı.

**Tetikleyen:** Mustafa bir mühendislik makalesi getirdi (*"One AI Agent Wasn't
Enough: Engineering Council and a Code Graph"*) ve başka bir pencerede yapılan
analizi buraya taşıyıp yeniden değerlendirilmesini istedi.

---

## 1. Kaçırılmış tetikleyici

`06-ACIK-RISKLER.md` satır 409, 15 Eylül'den:

> *"Motorun bağımsız doğrulayıcısı (M-09) yazıldığında yeniden bakılacak."*

**M-09'un doğrulayıcısı 16 Eylül'de yazıldı.** Koşul gerçekleşti, kimse
fark etmedi ve karar bir hafta öylece durdu.

**T-26'nın üçüncü örneği** — ve ilk kez bir ürün kararında değil, **sürecin
kendisinde**. K-28'de karar kayıtlıydı, yürürlükte değildi. Burada bir
tetikleyici kayıtlıydı, ateşlendi, kimse bakmadı.

> Kayıt ile yürürlük arasındaki boşluk süreç kurallarını da kapsıyor. Karar
> kaydına *"ne zaman yeniden bakılacak"* yazmak yetmiyor; o tarihi kimin
> kontrol edeceği de yazılmalı.

---

## 2. Dış analiz değerlendirildi — üç düzeltme

Başka penceredeki analiz büyük ölçüde doğruydu. Depoya karşı kontrol edildi,
**üç yerde zaten var olanı atlıyordu:**

| İddia | Gerçek |
|---|---|
| *"Karar kaydına geri dönüş planı eklenmeli"* | `03-MIMARI-KARARLAR.md` sonunda **geri alma maliyeti tablosu var** — 15 karar, her biri 🔴/🟡/🟢. Eksik olan *bedel* değil, **plan** |
| *"Reddedilen alternatifler eklenmeli"* | M kayıtlarının **yedisinde var** (M-03: *"Keycloak elendi"*). Eksik olan alan değil, **zorunluluk** |
| *"Risk sınıflandırması yapılmalı"* | Sınıflandırma **zaten yazılı**: geri alma bedeli 🔴 olan beş karar = 3. sınıf |

**Haklı olduğu yer:** kapsam dışı bulgu kuralı (*"dur, yaz, onay bekle"*)
gerçekten `02-DEGISMEZLER.md`'de yazılı değil. Fiilen uyguluyoruz — 16 Eylül'de
T-18, T-19, T-21, T-24b uydurulmadı, kaydedildi — ama yazılı değil.

---

## 3. Tasarım değişti, gerekçesi ölçüldü

15 Eylül'ün kurgusu *"birleştirme öncesi **dal farkını** incele"* idi.

`git log --diff-filter=A` ile bakıldı: **`09-motor/` klasörünün tamamı
16 Eylül'de doğdu.** Yani o günün dal farkı motorun kendisiydi ve tasarım
tesadüfen çalışırdı — 19 bulgunun ~15'i o farkın içindeydi.

**Bir daha çalışmaz.** Şu sınıflar hiçbir dal farkında görünmez:

| Bulgu | Neden görünmez |
|---|---|
| T-19 talep biçimi | Kod eski; yanlış olan **gelenek** |
| T-28 `gecmis_vardiyalar` | Bir **yokluk** |
| T-29 `DONMUS_GUN` | Ölü kod yolu |
| T-34, T-35 🔴 | `04-kod`'da, motor dalının dışında |

> İki ayrı alet: **dal farkı** yeni işteki gerilemeyi, **şartname-kod taraması**
> birikmiş sapmayı ve eksikliği yakalar.

---

## 4. Mekanizma "ikinci ajan" değil, soğukluk

GPT'nin bulmasının sebebi daha akıllı olması değil, **hatırlamıyor olması.**
İşi yapan model *"bunu zaten yazdım"* diye bir daha bakmaz.

Bu, kalıcı aracı doğrudan sorunlu yapıyor. Makalenin kendi uyarısı:

> *"Grafik ya da depo talimatları bayatsa, konsey iyi yapılandırılmış ama kötü
> bağlama dayanan bir karar verebilir."*

Depoda duran, bağlam biriktiren bir inceleyici soğukluğunu — yani değerin
kaynağını — kaybeder.

---

## 5. Karar

**Kalıcı araç reddedildi. Haftalık elle tarama kuruldu.**

| | |
|---|---|
| Kim | Mustafa + **farklı sağlayıcının** modeli (şu an GPT) |
| Ritim | Haftalık, iki geçiş |
| 1. geçiş | Haftanın birikmiş `git diff`'i + kabul cümleleri |
| 2. geçiş | Şartname-kod taraması — beş taramadan **sırası gelen** |
| Yöntem | `05-inceleme/beceriler/` — dört dosya |
| Ölçüm şartı | Üç haftada üst üste bulgu yoksa **sıklık düşer**, bırakılmaz. İki geçiş ayrı ölçülür |

`00-DEVIR/` dışına yazıldı çünkü **R7 eşikte** (9 dosya; onuncusu uyarı üretir).
Makalenin *bağlam ↔ beceri* ayrımı da aynı yere çıkıyor: `00-DEVIR/` neyi
bilmen gerektiğini, `05-inceleme/beceriler/` işin nasıl yapılacağını söyler.

### Haftalık ritmin bedeli — ve hafifletmesi

Pazartesi yapılan hata Cuma'ya kadar yakalanmaz, o arada üstüne inşa edilir
(16 Eylül'ün O-9'u tam buydu). Tamamen çözülemez; en pahalı kısmı çözülür:

> **İş parçası kapanırken kabul cümlesi madde madde işaretlenir.** İnceleme
> değil, kontrol listesi — yazan taraf yapar. T-27'nin üçüncü şartını
> yakalayan şey buydu.

### ⚠ Kapatılamayan boşluk

Mimar (Yılmaz) ulaşılamıyor. Geri alma bedeli 🔴 olan beş karar — M-01, M-06,
M-09, M-10, M-11 — için **ikinci bir teknik insan görüşü yok.** Dış tarama
kodun şartnameye uyup uymadığına bakar, **kararın kendisinin doğruluğuna**
değil. Yılmaz'a ulaşılınca ilk gösterilecek şey bu liste.

---

## 6. T-37 — bu oturumda çıkan yan bulgu

`README.md`'ye `05-inceleme/` satırı eklenirken görüldü: dosya **aylardır
bayat.** *"`04-kod/` henüz boş"*, *"Kod: başlamadı"*, *"Master spec: yazılıyor"*,
teknoloji listesinde **elenen Keycloak**, ve altı klasör hiç yok.

**Neden kimse yakalamadı:** `DENETIM.py`'nin 6. kontrolü tazeliğe bakıyor ama
yalnız oturum günlüğü ile değişim günlüğü arasında. `README.md` **hiçbir
kontrolün kapsamında değil.**

Deponun **ilk okunan** dosyası bu. Okuyup *"kod başlamamış"* sanan biri projeye
yanlış yerden girer — dış incelemenin *bayat bağlam* uyarısının tam hedefi.

**Bugün yapılan:** yalnız ölçülebilir olgular düzeltildi.
**Yapılmayan:** tazelik kontrolü eklenmedi — betiğin neyi doğru sayacağı karar
gerektiriyor. T-37 açık.

---

## 7. Bu oturumda üretilmeyenler — dürüstlük notu

- **Kod değişmedi.** 68 birim testi, 7 altın senaryo; hiçbiri koşturulmadı
  çünkü değişen bir şey yok.
- **Kapsam dışı bulgu kuralı `02-DEGISMEZLER.md`'ye yazılmadı** — kabul edildi
  ama bu oturumda uygulanmadı. Sıradaki iş.
- **M kayıtlarına zorunlu alanlar eklenmedi** (reddedilen alternatifler, geri
  dönüş planı). Karar verildi, uygulanmadı.
- **İlk haftalık tarama koşmadı.** Döngü yazıldı, çalıştırılmadı.

> Son üç madde T-26'nın kendisidir: *kayıt ≠ yürürlük.* Bu oturum tam da onun
> üçüncü örneğini bulmakla başladı; dördüncüsünü üretmemek için buraya yazıldı.
