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

## 7. T-22 kapatıldı — ve kapatırken T-18'i görünür kıldı

Karar gerektirmeyen ilk 🔴. Teknik kısmı kısa: `orkestra.py`'nin erken dönüşü
artık `_taslagi_denetle()`'den geçiyor, denetim **özgün** girdiyle yapılıyor,
sıfır atamalı plan `var: False` diyor.

### Kabul cümlesi yine üç şartlıydı, yine ikincisi tuzaktı

`en_iyi_plan` üretilirken `ASGARI_KAPSAMA` **bilerek gevşetilir**. Denetim o
gevşetilmiş girdiyle yapılsaydı doğrulayıcı gevşetilen kuralı hiç görmez,
taslak tertemiz görünürdü — **denetim eklenmiş ama işe yaramaz olurdu** ve
diğer üç test yeşil yanardı.

Bunun için ayrı bir bekçi yazıldı: `test_taslak_denetimi_OZGUN_girdiyle_yapilir`.
T-27'de öğrenilen şey burada tekrar işe yaradı — **kabul cümlesi madde madde
işaretlenir.**

### Ölçtüm, kaydetmedim — bir bulgu adayı elendi

İlk sahnemde `en_iyi_plan` **boş** dönüyordu, oysa atanabilecek üç kişi vardı.
Yeni bir bulgu gibi göründü. `HEDEF_KAPSAMA` kuralını ekleyip tekrar ölçtüm:
üç atama geldi. Yani boşluk **benim minimal fikstürümün eseriymiş**, motorun
değil. Kaydedilmedi.

> Bu da kuralın diğer yönü: bulgu ölçülebilir olmalı — ölçüm tutmuyorsa
> bulgu da yoktur. Kaydedilmeyen bir bulgu, kaydedilen yanlış bir bulgudan
> iyidir.

### ⚠ A03 — T-18'in kanıtı güçlendi

A03 (*"İmkânsız durum ve yöneticinin kararı"*) tam bu yoldan geçiyor. Denetim
artık koşuyor ve şunu söylüyor:

```
uygulanmayan_kurallar : ['YETKINLIK_KAPSAMASI']
sert_ihlal            : 0
yayinlanabilir        : true
```

`YETKINLIK_KAPSAMASI` A03'ün girdisinde **aktif ve SERT**, gövdesi
doğrulayıcıda **yok**. Aynı cevapta *"bu SERT kuralı kontrol edemedim"* ve
*"yayınlanabilir"* — üstelik A03'ün tamamı o kural sağlanamadığı için
çözümsüz.

**T-18 daha önce kurulmuş bir girdiyle gösteriliyordu; artık Mustafa'nın
onayladığı bir altın senaryoda görünüyor.**

> Dikkat: T-22 düzeltmesi bu hatayı **üretmedi**. Denetim hiç koşmadığı için
> çelişki görünmüyordu. Düzeltme, görünmez bir boşluğu **görünür bir
> çelişkiye** çevirdi — bir denetim eklemenin asıl getirisi budur.

T-18 açık kalıyor: kapının bilinmeyen kuralda ne yapacağı **ürün kararı**,
uydurulmadı.

## 8. T-34 kapatıldı — CI dalında kırmızı kanıt

İlk kez `04-kod` tarafında bir düzeltme yapıldı ve ilk kez **kırmızı kanıt
kalıcı bir yere** yazıldı: Claude'un konteynerinde .NET yok, testi
koşturamıyor. Yol T-17'nin yolu oldu — önce yalnız test, dalda kırmızı,
sonra düzeltme, dalda yeşil.

| Commit | Ne | Sonuç |
|---|---|---|
| `48583e4` | Yalnız `SirTestleri.cs` | **42 test, 40 geçti** — S1, S2 kırmızı: *"No exception was thrown"* |
| `3ec5d42` | Düzeltme, 19 dosya | **42/42 yeşil** |

Hata mesajının kendisi bulgunun ifadesi: *sır yoktu, uygulama yine de açıldı.*

### Kayıttaki tarif kapsamı küçük gösteriyordu

T-34 iki satır olarak yazılmıştı (`Program.cs`'teki iki `??`). `grep` beş
katmanda **16 yer** buldu — ve en kritiği kayıtta hiç geçmiyordu:
`04-kod/db/rls/02-uygulama-rolu.sql` veritabanı rolünü o parolayla
**yaratıyordu**.

> **Ders:** bir bulgunun kaydı, bulgunun kapsamı değildir. Kapatmadan önce
> aynı desen depoda aranır. Bu, kabul cümlesini madde madde işaretleme
> kuralının kardeşi: *"nerede daha var?"*

### M5 — kapı vardı, başka bir kapıydı

`M5 - appsettings icinde gercek parola yok` yıllardır yeşil yanıyor ve
doğru söylüyordu: parola `appsettings`'te değildi. **Başka beş yerdeydi.**

O-1'de RLS tanımlıydı ama etkisizdi. O-9'da git temizdi ama karşılaştırdığı
iki şey de aynı taraftaydı. Burada test doğruydu ama **baktığı dosya
yanlıştı.** Aynı ailenin üçüncü örneği.

### Kendi kuralımı iki kez uyguladım

**Yer tutucu deseni uydurulmadı, koddan alındı.** `KurulumHizmeti` zaten
`{DB_PASSWORD}` için aynı şeyi yapıyordu; SQL betiği o desene bağlandı.

**`.env` yazılmadı.** Proje kuralı: *"Mustafa'nın `.env` dosyasını uzak
araçlar yazamaz."* Eksik olan `JWT_SECRET` satırı ona bildirildi, kendisi
ekledi.

### ⚠ Açık kalan

`.env`'deki üç değer herkese açık bir depoda aylardır duruyordu — artık sır
değiller. Değiştirilmeleri ve `TSHIFT_KURULUM=true` ile bir kurulum koşusuyla
veritabanı rolünün senkronlanması gerekiyor. **Mustafa'nın işi**, kayda geçti.

## 9. T-35 kapatıldı — ve "mekanik" etiketi yanlış çıktı

Üçüncü 🔴. Bu madde *"karar gerektirmiyor"* diye kaydedilmişti; **değildi**.

`X-Forwarded-For` istemcinin yazdığı bir başlıktır. Körlemesine güvenmek
saldırganın kendini istediği IP gibi göstermesine izin verir — hem kilitten
kaçar hem denetim kaydını kirletir. Güvenilen vekil listesi şart, o liste de
barındırmaya bağlı, barındırma ertelenmiş. Yani içinde gerçek bir ürün kararı
vardı ve kayıtta görünmüyordu.

> **Bugünün ikinci dersi:** *"mekanik"* etiketi de bir iddiadır ve
> doğrulanmadan taşınır. T-34'te kapsam küçük yazılmıştı; burada **zorluk**
> küçük yazılmıştı.

### Kayıt yine iki yerde küçük yazmış

| | Kayıtta | Ölçülen |
|---|---|---|
| Etki | *"bütün kiracıyı kilitliyor"* | **Kurulum çapında** — `KilitliMi`'de kiracı filtresi yok (M-13, bilerek) |
| Kapsam | Yalnız `04-kod/frontend/src/app/api/giris/route.ts` | API'ye giden **beş** çağrı yeri |

Üçüncü kez aynı şey: *bir bulgunun kaydı, bulgunun kendisi değildir.*

### Kural doğruydu

Şartname *"aynı e-posta veya IP için 5 başarısız denemede 15 dakika kilit"*
diyor; kod bunu doğru uygulamış. Kusur kuralda değil, kuralın **gördüğü
veride**. Bu ayrımı yapmasaydım IP kilidini kaldırmayı önerecektim — yani
şartnameden sapmayı, hiç gerekmezken.

### Test sunucusu sınırı — ince ve kayda değer

Gerçek soket olmadığı için `RemoteIpAddress` null geliyordu ve
`UseForwardedHeaders` tam o adresi karşılaştırıyor. `TestUygulamasi`'na boş
adresi loopback'e dolduran bir filtre eklendi.

> **Yapılan:** testin ortamını gerçeğe benzetmek. **Yapılmayan:** iddiayı
> gevşetmek. `02-DEGISMEZLER.md` §6 *"kırılan test iddiayı zayıflatarak
> düzeltilmez"* diyor; bu onun sınırında durduğu için kayda geçti.

### ⚠ Elle doğrulama bir kusur yakaladı — ve yakalaması şanstı

Uçtan uca ölçüm ilk turda **geçti**: Next'e verilen `198.51.100.7` kayda aynen
yazıldı. T-35 orada kapatılabilirdi. Kapatılmadı, çünkü bir ölçüm daha
yapıldı: **sahte başlık host'tan doğrudan API'ye**.

**Geçti.** Yani koruma çalışmıyordu.

```
host -> yayinlanmis port -> api   =>  ::ffff:172.18.0.1   (docker AG GECIDI)
web kutusu                        =>  172.18.0.4
```

Güvenilen aralık `172.16.0.0/12` yazılmıştı ve ağ geçidi de o aralıkta.
Yanına da *"host'tan gelen istek bu aralığa girmez"* diye **ölçülmemiş bir
gerekçe** yazılmıştı. Otopsisi **O-11**.

Düzeltme: sabit alt ağ, web kutusuna sabit adres, güvenilen liste tek adres.
İkinci tur iki yönde de geçti.

> **İki ders.** Birincisi: bir yorum *"şu saldırı geçmez"* diyorsa bu bir
> iddiadır ve ölçülür — ölçülmemiş güvenlik yorumu hiç yorum olmamasından
> kötüdür, çünkü sonraki okuyan kontrol etmez.
>
> İkincisi: `IP2` doğru şeyi sınıyor ve çalışıyordu. Yanlış olan **kod değil
> yapılandırma**, ve test sunucusu üretimdeki yapılandırmayla hiç
> karşılaşmıyor. **Birim testi mantığı doğrular, topolojiyi doğrulayamaz.**

Bu yüzden iki elle ölçüm, T-35'in kapanış kaydına *koşturulacak adım* olarak
yazıldı: topoloji değişirse ikisi de yeniden koşar.

### Ön yüzün testi yok — bilerek

`IP1`–`IP3` API'ye doğrudan gidiyor. Beş çağrı yerinin başlığı ilettiği
**elle doğrulandı**: Next'e `X-Forwarded-For: 198.51.100.7` verildi,
`login_attempts.ip` aynısını yazdı. Gerileme bekçisi yok; Next.js route
handler test altyapısı kurmak T-35'ten büyük bir iş, ertelendi.

Bu seçim Mustafa'ya soruldu, sessizce yapılmadı.

## 10. Bu oturumda üretilmeyenler — dürüstlük notu

- **Kapanan üç 🔴:** T-22 (motor), T-34 ve T-35 (`04-kod`). Motor tarafı burada
  koşturuldu (72 birim, 7 altın senaryo, fikstür 0); `04-kod` tarafı CI'da
  (42/42).
- **Kapsam dışı bulgu kuralı `02-DEGISMEZLER.md`'ye yazılmadı** — kabul edildi
  ama bu oturumda uygulanmadı. Sıradaki iş.
- **M kayıtlarına zorunlu alanlar eklenmedi** (reddedilen alternatifler, geri
  dönüş planı). Karar verildi, uygulanmadı.
- **İlk haftalık tarama koşmadı.** Döngü yazıldı, çalıştırılmadı.

> Son üç madde T-26'nın kendisidir: *kayıt ≠ yürürlük.* Bu oturum tam da onun
> üçüncü örneğini bulmakla başladı; dördüncüsünü üretmemek için buraya yazıldı.
