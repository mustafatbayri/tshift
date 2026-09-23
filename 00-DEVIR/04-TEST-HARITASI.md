# TEST HARİTASI

**Bu dosya Mustafa içindir.** Her testin ne koruduğu, kod okumadan
anlaşılacak şekilde Türkçe tek cümleyle yazılmıştır.

## Nasıl kullanılır

Her satırdaki **"Ne garanti ediyor"** sütununu oku ve tek bir soru sor:

> **"Bu cümle doğru mu? Sahada gerçekten böyle mi işliyor?"**

Cevap "hayır" ya da "emin değilim" ise **test yanlıştır, kod değil.**
Bunu söylediğinde test düzeltilir.

### Kaynak sütunu — hangi cümleye daha çok dikkat etmelisin

| İşaret | Anlamı | Senin için |
|---|---|---|
| `[spec]` | Cümle şartnameden geldi, onaylı bir karara dayanıyor | Rutin kontrol |
| `[karar]` | Sohbette açıkça verilmiş ve günlüğe yazılmış bir karar | Rutin kontrol |
| `[çıkarım]` | **Cümleyi yapay zekâ türetti.** Şartnamede yazmıyor, sen onaylamadın | **Buraya dikkat et** |

`[çıkarım]` satırları, D6 sınıfı hatanın (kodu yazan testi de yazınca aynı
yanlış varsayımın iki yere birden geçmesi) yaşanabileceği yerlerdir.

**Durum: 39 test · 31 `[spec]`/`[karar]` · 8 `[çıkarım]`**

---

## Çok kiracılık — 4 test
*Dosya: `CokKiracilikTestleri.cs` · "başka FİRMANIN verisi gelmesin"*

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `1 - Iki ayri baglam ayni anda birbirinin verisini gormez` | A firması ile B firması aynı anda sisteme bağlıyken, hiçbiri diğerinin çalışanlarını göremez. | `[spec]` |
| `2 - Ham SQL ile bile baska kiracinin satiri gelmez (RLS)` | Birisi uygulamayı atlayıp doğrudan veritabanına sorgu yazsa bile, yalnız kendi firmasının satırlarını görür. | `[spec]` |
| `3 - Kiraci baglami yoksa hicbir satir gorunmez` | Sistem hangi firma adına çalıştığını bilmiyorsa **hiçbir şey** göstermez. Varsayılan "hepsi" değil, "hiçbiri". | `[karar]` |
| `4 - Baska kiracinin kimligiyle kayit yazilamaz` | A firmasındaki bir kullanıcı, B firmasına ait bir kayıt oluşturamaz. | `[spec]` |

---

## Yetki ve kapsam — 9 test
*Dosya: `YetkiTestleri.cs` · "aynı firma içinde, yetkisi olmayan görmesin"*

> Çok kiracılık "başka firma" sorunuydu — veritabanının garantisi.
> Bu grup "aynı firma içinde kim neyi görür" sorunu — uygulamanın kararı.
> İkisi farklı sınıf sorun, bu yüzden ayrı ayrı sınanıyor.

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `Y1 - Kiraci yoneticisi tum calisanlari gorur` | Firma yöneticisi kendi firmasındaki **bütün** çalışanları görür ve kullanıcı/kural yönetimi yapabilir. | `[spec]` §3.2 |
| `Y2 - Sef YALNIZ kendi ekibini gorur` | Gündüz ekibinin şefi, gece ekibindeki çalışanı **göremez**. | `[spec]` §3.2 |
| `Y3 - Sef plan uretemez, duzenleyebilir` | Şef mevcut planı düzenleyebilir ama yeni plan **üretemez**, **onaylayamaz**, çalışan kaydı **düzenleyemez**, kural parametresi **değiştiremez**. | `[spec]` §3.2 |
| `Y4 - Calisan yalniz kendi kaydini gorur` | Normal çalışan yalnız kendi kaydını görür; kendi izin **talebini** oluşturabilir ama başkası adına izin **giremez**. | `[spec]` §3.2 |
| `Y5 - Izleyici her seyi gorur, hicbir sey yazamaz` | İzleyici rolü firmadaki her şeyi görür ama katalogdaki **hiçbir** yazma iznine sahip değildir. *(Yeni bir yazma izni eklenirse bu test onu da otomatik kapsar.)* | `[spec]` §3.2 |
| `Y6 - Suresi gecmis yetki devri islemez` | Dün bitmiş bir yetki devri bugün hiçbir şey yapmaz; kişi kendi rolüne döner. | `[spec]` |
| `Y7 - Suren yetki devri calisir ve kapsami genisletmez` | Yetki devri "daha fazlasını **yapabilirsin**" demektir, "daha fazlasını **görebilirsin**" demek değil. Şefe departman müdürlüğü devredilse bile gördüğü ekip değişmez. | `[çıkarım]` ⚠️ |
| `Y8 - Kapsami olmayan kapsamli rol HICBIR SEY gormez` ⚑ | Kapsamı atanmayı unutulan bir departman müdürü **hiçbir şey görmez** — tüm firmayı değil. Eksik yapılandırma sızıntıya değil, "göremiyorum" şikâyetine dönüşür. | `[karar]` — spec'ten **bilinçli sapma**, Mustafa onayladı |
| `Y9 - Rolsuz kullanici hicbir izne sahip degil` | Rolü atanmamış bir kullanıcının hiçbir izni ve hiçbir görüşü yoktur. | `[karar]` |

**⚠️ Y7 neden dikkat gerektiriyor:** "Yetki devri kapsamı genişletmez" kuralı
şartnamede açıkça yazmıyor; tasarım gereği böyle kuruldu. Sahada beklenti
farklı olabilir — *"müdür yerine bakan şef, o gün müdürün tüm departmanını
görmeli mi?"* Bu senin cevaplayacağın bir soru.

---

## Kimlik ve oturum — 7 test
*Dosya: `KimlikTestleri.cs`*

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `K1 - Dogru parola ile giris yapilir ve jeton verilir` | Doğru firma + doğru e-posta + doğru parola ile giriş çalışır. | `[spec]` |
| `K2 - Yanlis parola reddedilir` | Yanlış parola reddedilir ve **kullanıcının var olup olmadığı sızdırılmaz** (aynı hata mesajı döner). | `[çıkarım]` |
| `K3 - Baska firmanin adiyla giris yapilamaz` | A firmasının kullanıcısı, parolası doğru olsa bile B firmasının adıyla giriş yapamaz. | `[spec]` |
| `K4 - Bes basarisiz denemeden sonra hesap kilitlenir` | 5 yanlış denemeden sonra hesap kilitlenir; altıncı deneme **doğru parolayla** bile girilemez. | `[karar]` (5 deneme / 15 dakika) |
| `K5 - Yenileme jetonu doner; eski jeton olur` | Oturum yenilendiğinde yeni bir jeton verilir ve eskisi geçersizleşir. | `[karar]` |
| `K6 - Calinmis jeton tekrar kullanilirsa TUM oturumlar duser` | Biri jetonu çalıp kullanırsa, hangisinin hırsız olduğu bilinemeyeceği için o kullanıcının **bütün** oturumları düşürülür. | `[çıkarım]` ⚠️ |
| `K7 - Parola veritabaninda duz metin olarak durmaz` | Parola veritabanında okunamaz halde durur; **aynı parolayı kullanan iki kullanıcı bile veritabanında farklı görünür**. | `[spec]` |

**⚠️ K6 neden dikkat gerektiriyor:** "Tüm oturumlar düşer" güvenli ama sert
bir davranış. Kullanıcı deneyimi açısından: bir kişinin telefonundaki oturum
bir sorun yaşadığında bilgisayarındaki oturum da kapanır. Bu kabul edilebilir
mi, senin kararın.

---

## HTTP sınırı — 5 test
*Dosya: `HttpSinirTestleri.cs` · katmanların **arasını** sınar*

> Bu grup bir hatanın sonucu doğdu: 21 test yeşilken bütün korumalı uçlar 401
> dönüyordu. Testler kaçırmıştı çünkü hepsi servisleri doğrudan çağırıyor,
> HTTP katmanından geçmiyordu. Bkz. `05-HATA-OTOPSILERI.md` O-2.

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `H1 - Jetonla /me calisir ve dogru kullaniciyi doner` | Giriş yapmış kullanıcı gerçek bir HTTP isteğiyle kendi bilgisini alabilir. *(Bu test JWT `sub` hatasının kalıcı bekçisidir.)* | `[karar]` |
| `H2 - Jetonsuz istek 401` | Giriş yapmamış istek reddedilir. | `[spec]` |
| `H3 - Izni olmayan kullanici 403 alir, 401 degil` | Giriş yapmış ama yetkisi olmayan kullanıcı "yetkin yok" (403) alır, "kim olduğunu bilmiyorum" (401) değil. | `[çıkarım]` |
| `H4 - Sef HTTP uzerinden de yalniz kendi ekibini gorur` | Kapsam filtresi yalnız iç katmanda değil, **gerçek API çağrısında da** çalışır. | `[spec]` |
| `H5 - Sahte X-Tenant-Id basligi hicbir sey degistirmez` | Kullanıcı isteğe elle "ben şu firmadanım" yazsa bile hiçbir şey değişmez; firma kimliği **sunucunun imzaladığı jetondan** okunur. | `[karar]` |

---

## Denetim kaydı — 7 test
*Dosya: `DenetimTestleri.cs`*

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `D1 - Kayit olusturmak otomatik iz birakir` | Yeni bir kayıt oluşturulduğunda, kimsenin ayrıca bir şey yapmasına gerek kalmadan iz düşer. | `[spec]` |
| `D2 - Guncellemede SADECE degisen alanlar kaydedilir` | Bir kaydın tek alanı değiştiyse kayda yalnız o alan yazılır, tüm kayıt değil. | `[çıkarım]` |
| `D3 - Parola ozeti denetim kaydina SIZMAZ` | Parola değiştiğinde "parola alanı değişti" yazar, **parolanın kendisi yazmaz**. | `[karar]` |
| `D4 - Yazilmis denetim kaydi DEGISTIRILEMEZ` | Yazılmış bir iz sonradan değiştirilemez — uygulama izin vermediği için değil, **veritabanı yetki vermediği için**. | `[karar]` |
| `D5 - Yazilmis denetim kaydi SILINEMEZ` | Yazılmış bir iz silinemez. Aynı gerekçe. | `[karar]` |
| `D6 - Bir kiraci digerinin denetim kaydini goremez` | B firması **A'nın** izlerini göremez (ama kendi izlerini görür). | `[spec]` |
| `D7 - Islemi yapan kullanici ve IP kaydedilir` | Her izde kimin, ne zaman, hangi adresten yaptığı yazar. | `[spec]` |

---

## Mimari (yasa) testleri — 7 test
*Dosya: `MimariTestleri.cs` · özellik değil **kural** sınar*

> Bunlar bugün bir şey yakalamak için değil, **altı ay sonra unutulacak bir
> kuralı hatırlatmak** için varlar.

| Test | Ne garanti ediyor | Kaynak |
|---|---|---|
| `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` | Uygulamanın veritabanına bağlandığı rol **süper kullanıcı değildir** ve güvenliği atlama yetkisi yoktur. *(Diğerleri "güvenlik kurulmuş mu" diye sorar; bu "güvenlik gerçekten çalışıyor mu" diye sorar.)* | `[karar]` — O-1'in bekçisi |
| `M1 - Kiraciya ait her tabloda RLS acik ve zorunlu` | Yeni bir tablo eklenip güvenlik ayarı unutulursa test kırılır. *(Tablo listesi elle yazılmıyor, koddan okunuyor — yeni tablo kendiliğinden kapsanıyor.)* | `[karar]` |
| `M2 - RLS disindaki tablolar sadece bilinen istisnalar` | Güvenlik dışında kalan tablolar yalnız 3 bilinen istisna. Dördüncüsü **sessizce eklenemez**. | `[karar]` |
| `M3 - Her uc korumali ya da acikca istisna` | Yeni bir API ucu eklenip korumasız bırakılırsa test kırılır. | `[karar]` |
| `M4 - Kulture bagimli ToLower/ToUpper kullanilmiyor` | Türkçe `I` harfi tuzağı: `"IZMIR".ToLower()` Türkçe ayarda `ızmır` verir. Bu tür kullanım yasak. | `[karar]` |
| `M5 - appsettings icinde gercek parola yok` | Ayar dosyalarına yanlışlıkla gerçek bir parola yazılırsa test kırılır. | `[karar]` |
| `M6 - Denetim kaydi sadece eklenir (UPDATE/DELETE yok)` | Veritabanı yetkilerinin gerçekten "sadece ekle" olduğunu **veritabanına sorarak** doğrular. | `[karar]` |
| `S1 - APP_DB_PASSWORD verilmezse uygulama acilmaz` | Sır verilmezse uygulama **sessizce koddaki sabite düşemez**; açılmaz ve eksik değişkenin adını söyler. | `[karar]` — T-34 |
| `S2 - JWT_SECRET verilmezse uygulama acilmaz` | Aynısı imza anahtarı için; ayrıca en az 32 karakter şartı. `Program.cs` *"canlıda mutlaka verilir"* diyordu, **zorlayan yoktu**. | `[karar]` — T-34 |
| `IP1 - Guvenilen vekilden gelen gercek istemci IP'si kaydedilir` | Kullanıcının IP'si API'ye ulaşır. Ulaşmazsa kaba kuvvet kilidi herkesi birden kilitler ve denetim kaydındaki IP kurgusal olur. | `[karar]` — T-35 |
| `IP2 - Guvenilmeyen kaynaktan gelen X-Forwarded-For yok sayilir` | **Sahte başlık koruması.** Başlığa körlemesine güvenen bir düzeltme IP1'i yeşil yakar ama saldırganın kendini istediği IP gibi göstermesine izin verir. | `[karar]` — T-35 |
| `IP3 - Baslik hic yoksa istek yine de kayda gecer` | Gerileme koruması: düzeltme *"başlık yoksa patla"* diye yapılamaz. | `[karar]` — T-35 |
| `S3 - Sirlar verildiginde uygulama normal acilir` | Gerileme koruması: düzeltme *"her koşulda patla"* diye yapılamaz. S1/S2 tek başlarına hiç açılmayan bir uygulamayla da yeşil yanar. | `[karar]` — T-34 |

> **M5 bu ailenin tek üyesini koruyordu ve yeşil yanıyordu.** *"appsettings
> icinde gercek parola yok"* doğruydu — parola `Program.cs`'teydi, üstelik
> yedi test dosyasında, `docker-compose.yml`'de ve bir SQL betiğinde de.
> Kapı vardı; başka bir kapıydı. O-1 ve O-9 ile aynı sınıf.

---

## Şartnamedeki kabul senaryoları — **yedisi koşuyor ve yeşil**

**Master Spec §16** on iki altın senaryo tanımlıyor (A1–A12): basit
uygulanabilir, çelişkili sert kural → `cozumsuz`, yetkinlik açığı, **gece
yarısı → 8 saat dinlenme ihlali**, DST geçişi, kilitli revizyon, yumuşak hedef
çatışması, mola kapsaması, kısmi kapasite, idempotency, lookback eksikliği,
plan kopyalama.

**Durum (16 Eylül).** Zincir uçtan uca tamam: onaylı cümle → fikstür → test
→ motor.

> ⚠ **Düzeltme (23 Eylül).** Bu başlıkta *"on ikisi de yeşil"* yazıyordu.
> **Yanlıştı** ve 16 Eylül'de beş dosyada düzeltilen iddianın aynısıydı —
> burası atlanmış. Gerçek: **yedi senaryo koşuyor ve yeşil** (A1, A3, A4, A6,
> A7, A8, A9). A2, A10, A11, A12 backend tarafında `.cs.taslak` hâlinde,
> **hiç koşmadı**. A5 ertelendi (K-12). Aynı sınıf: T-37.

| Adım | Durum |
|---|---|
| Kabul cümleleri yazıldı | ✅ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` §4 |
| Mustafa onayladı | ✅ **12/12 senaryo, 6/6 varsayım** (A5 ertelendi) |
| Fikstürler yazıldı | ✅ **11 dosya** (A5 hariç) + ortak sahne, hepsi denetleyiciden geçiyor |
| Test iskeleti | ✅ `08-motor-testleri/v5/testler/` — pytest çatısı + `08-motor-testleri/v5/testler/backend-taslak/` |
| Bağımsız doğrulayıcı | ✅ `09-motor/dogrulayici/` — `/evaluate`, **19** kural gövdesi |
| Çözücü | ✅ `09-motor/cozucu/` — CP-SAT, `/solve` |
| Onarım döngüsü | ✅ `09-motor/orkestra.py` — §11.7, en fazla 2 deneme |
| **Altın senaryolar** | ⚠ **7 tanesi koşuyor ve yeşil** — A1, A3, A4, A6, A7, A8, A9 |
| Koşmayanlar | A2, A10, A11, A12 **backend tarafında**, `.cs.taslak` — hiç sınanmadı · A5 ertelendi (K-12) |
| Birim testi | ✅ **60 passed** |

> ⚠ **`12 passed` sayısı yanıltıcıdır ve 16 Eylül'e kadar yanlış
> aktarıldı.** O sayı **7 altın senaryo + paketin kendi 5 sağlık testi**
> demek; *"12 altın senaryo yeşil"* demek **değil**. Dış inceleme yakaladı.
>
> Sınanmayan üç senaryonun konusu önemsiz de değil: **çift tıklama iki plan
> üretmesin** (A10), **geçmiş veri eksikliği** (A11), **plan kopyalama**
> (A12). Bunlar tamamlanmış güvence olarak sunulmamalı.

```
py servis.py   (ayri pencerede)
set TSHIFT_MOTOR_URL=http://localhost:8000
py -m pytest -q   →   12 passed, 4 skipped
```

### Kapsamanın büyüme çizgisi

| | Motorsuz | Doğrulayıcıyla | Çözücüyle |
|---|---|---|---|
| Kırmızı | 7 | 5 | **0** |
| Yeşil (senaryo + paket sağlığı) | 4 | 7 | **12** |
| Atlanan | 5 | 4 | 4 |

Son sütundaki 12'nin **7'si altın senaryo**, 5'i paketin kendi sağlık testi.
Atlanan dördü backend senaryosu (A2, A10, A11, A12); xUnit tarafında koşacak
ama o taraf henüz **taslak**.

### Son üç senaryo neyi ortaya çıkardı

Yeşile dönmeleri kolay olmadı ve üçü de **motorda ya da fikstürde gerçek bir
boşluk** olduğu için kırmızıydı:

| Senaryo | Kırmızı tutan şey | Nasıl bulundu |
|---|---|---|
| **A9** kadro yetmiyor | `shift_templates`'te *"bu şablon hangi günlerde kullanılır"* alanı **yoktu**. "Cumartesi nöbeti" adlı şablonu motor hafta içi de kullanıyordu — adı bir yorumdur, kısıt değildir | Tahminle değil **deneyle**: şablon çıkarılınca kapasite tam olarak fikstürün belgelediği 42'ye düştü (şablon dururken 49) → T-14 |
| **A1** normal hafta | `/solve` §11.7 onarım döngüsünü hiç koşmuyordu; `onarim_denemesi` diye bir sayı yoktu | Fikstür istiyordu, çıktı vermiyordu → `09-motor/orkestra.py` yazıldı |
| **A7** adalet mi kapsama mı | **İki ayrı boşluk birden.** (1) Motor `profil` alanını hiç okumuyordu — ağırlık tablosu (§5.4) kodda yoktu. (2) `ADALET_DENGESI`'nin eşik altında gradyanı yoktu, yani ağırlığı değiştirmek planı değiştiremiyordu. (3) **Fikstürün kendisi de eksikti**: kabul ölçütü *"Ç01–Ç03 en müsait olanlar"* diyordu ama fikstürde on çalışan da birbirinin aynısıydı — cumartesiyi kime verdiğin kapsamaya hiçbir şey mal olmuyordu | Test kırmızıydı ve **haklıydı**; sebebi ararken üçü de çıktı → K-29, T-14 |

> **A7'nin dersi.** Kabul ölçütündeki bir cümle (*"en müsait olanlar"*)
> fikstüre çevrilmemişse, senaryo anlattığı şeyi sınamaz. Cümle onaylıydı,
> fikstür ona uymuyordu ve bu ancak motor yazılınca görüldü.

### Kırmızı kanıt turu — 12/12, ama ilk turda 8'de 4'ü kaçtı

§16.4 kuralı: bir test yeşil sayılmadan önce **kırmızı yanabildiği**
gösterilmeli. 16 Eylül'de motor koduna tek tek kasıtlı bozmalar uygulandı.

**İlk tur: 8 bozmanın 4'ü hiçbir teste yakalanmadı.**

| Kaçan bozma | Ne demek |
|---|---|
| Ağırlık tablosu yok sayılır | Profil farkı **başka bir sebepten** oluşuyordu; A7 yeşildi ama §5.4'ü kanıtlamıyordu |
| Adalet gradyanı kaldırılır | Aynı |
| Orkestra doğrulayıcıyı çağırmaz | Import'a bakan test yakalamıyor — import durur, çağrı kaybolur |
| Fazla mesai tavanı sabitlenir | Hiçbir senaryo bu tavana dokunmuyordu |

Eksik testler bunun üzerine yazıldı (`09-motor/testler/test_profiller.py`, 16
test). İkinci turda **12 bozmanın 12'si yakalandı.**

> **Bu turun varlık sebebi tam olarak budur.** Dört boşluk, testler yeşil
> yanarken duruyordu. "Testler geçiyor" ile "testler bir şeyi koruyor" aynı
> şey değildir.

### Paket CI'ya bağlandı 🆕 *(16 Eylül)* — **ilk koşu yeşil**

Bugüne kadarki gerekçe basitti: motor yokken paket bilerek kırmızıydı, kırmızı
bir paketi kapıya bağlamak *"main her zaman yeşil"* kuralını bozardı. Motor
bitti, kırmızı kalmadı, gerekçe de ortadan kalktı.

`.github/workflows/testler.yml` içine **ikinci bir iş** eklendi:

| İş | Ne koşar | Docker |
|---|---|---|
| `test` | .NET backend — 39 test + mimari kuralları | gerekli |
| `motor` 🆕 | **72** birim + 7 altın senaryo + fikstür denetleyicisi | **gerekmez** |

> ⚠ **Ön yüzün testi yok.** `IP1`–`IP3` API'ye doğrudan gidiyor. Next.js
> route handler'larının istemci IP'sini ilettiği **elle doğrulandı**
> (23 Eylül: `X-Forwarded-For: 198.51.100.7` → `login_attempts.ip` aynısı)
> ama gerileme bekçisi yok. Next test altyapısı kurulmadı.

**Neden ayrı iş, aynı işe ek adım değil:** aynı işte olsalardı ilkinin
kırmızısı ikincinin sonucunu **gizlerdi** — bir adım patlayınca sonrakiler hiç
koşmaz. Ayrı işler paralel koşar ve depo sayfasında hangisinin kırıldığı tek
bakışta görünür.

Python sürümü **3.14**'e sabitlendi: Mustafa'nın makinesindeki sürümün
aynısı. Gerekçe workflow'da docker için zaten yazılıydı — *"CI ile yerel
arasında fark olmasın"*.

#### Kapının kendi kırmızı kanıtı

Bir kapının en tehlikeli hâli, koruduğu şey yokken de yeşil yanmasıdır.
Ölçüldü:

| Durum | Sonuç |
|---|---|
| `TSHIFT_MOTOR_URL` verilmemiş | `exit=1` — 7 failed |
| Adres var, servis kapalı | `exit=1` — 8 failed |
| Sağlık beklemesi 20 sn'de cevap alamazsa | adım `::error::` ile durur |

Yani motor ayağa kalkmazsa kapı **sessizce geçmiyor**.

#### İlk koşu ✅ *(16 Eylül, `47c7050`)*

Her iki iş de **yeşil** yandı. Artık bu satırların kanıtı var: kapı gerçekten
koştu, gerçekten geçti.

İlk koşuda iki **uyarı** çıktı: eylemler Node 20 hedefliyordu, GitHub onları
Node 24'e zorluyordu. Aynı gün kapatıldı (**T-17**) — checkout v7,
setup-python v7, setup-dotnet v6. Değişiklik önce `ci/node24` dalında
denendi, yeşil görülünce `main`'e alındı: *"`main` her zaman yeşildir"*
bir değişmez, bir CI değişikliği için bedava riske atılmaz.

C# taslakları `.cs.taslak` uzantılı kalmaya devam ediyor — derleyici görmez,
CI kırılmaz.

## ⚠ Dış inceleme — 16 Eylül, iki 🔴 bulgu

Motor bittikten sonra proje **başka bir modele** (GPT) şartnameyle birlikte
incelettirildi. İki sessiz hata çıktı ve **ikisini de kendi kırmızı kanıt
turumuz bulamamıştı.**

| Bulgu | Ne oluyor |
|---|---|
| **T-18** 🔴 | Gövdesi yazılmamış aktif SERT kural varken plan **"yayınlanabilir"** çıkıyor. *"Kontrol edemedim"* ile *"yayınla"* aynı cevapta |
| **T-19** 🔴 | Şartname §11.2 biçimindeki talep sessizce atlanıyor: **sıfır kişilik plan**, %100 kapsama, yayınlanabilir |

### Neden iç kırmızı kanıt bunları bulamadı

| | İç kırmızı kanıt | Dış inceleme |
|---|---|---|
| Yöntem | Kodu bozar, test yakalıyor mu bakar | Şartnameden girdi verir, motor doğru mu bakar |
| Bulduğu | Varsayımlarımız korunuyor mu | **Varsayımlarımız doğru mu** |
| Sonuç | 12/12 yakalandı | 2 sessiz hata |

Kırmızı kanıt **kendi kurduğumuz dünyanın içinde** kusursuzdu. T-19 özellikle
öğretici: §7.6 bağımsızlığı çözücü ile doğrulayıcıyı kural mantığında
ayırıyor ama ikisi de girdiyi aynı **fikstür geleneğiyle** okuyor — ve o
gelenek şartnameyle uyuşmuyor.

> **Yöntem olarak kayda geçti:** bir iş parçası bittiğinde, şartnameden
> türetilmiş girdilerle dışarıdan inceleme yapılır. Tercihen **başka bir
> modelle** — aynı model aynı kör noktayı iki kez taşır.

Ayrıntı: `00-DEVIR/06-ACIK-RISKLER.md` T-18, T-19, T-20.

## Kapsama özeti — dürüst tablo

Sahanın standart senaryo matrisi 20 sınıf tanımlıyor
(`KALITE-ARASTIRMASI-DEGERLENDIRME.md`). Bizim durumumuz:

| Senaryo sınıfı | Durum |
|---|---|
| G01 Mutlu yol | ✅ Derin |
| G05 Yetki | ✅ Derin (9 test) |
| G06 Kiracı ayrımı | ✅ Derin (6 test) |
| G19 Bağlam gerilemesi | ✅ Derin (M1–M5) |
| G15 Secret sızıntısı | 🟡 Yalnız denetim kaydında (D3); **log ve hata çıktısı sınanmıyor** |
| G18 Sahte yeşil test | 🟡 Yalnız M6; **mutasyon testi yok** |
| G02 Sınır değerler (0, 1, max, max+1) | ❌ Yok |
| G03 Boş ve null | ❌ Yok |
| G04 Geçersiz biçim (tarih, UUID, encoding) | ❌ Yok |
| G07 Tekrar ve idempotency | ❌ Yok |
| G08 Eşzamanlılık | ❌ Yok |
| G09 Timeout | ❌ Yok (motor gelince gerekli) |
| G10 Kısmi bağımlılık arızası | ❌ Yok (motor gelince gerekli) |
| G11 Sözleşme değişimi | ❌ Yok |
| **G12 Saat dilimi / yaz saati** | ❌ **Yok — vardiya ürünü için kritik** |
| G13 Migration (yarıda kesilme, tekrar) | ❌ Yok |
| G14 Injection ve kötü girdi | ❌ Yok |
| G16 Performans | ❌ Yok (spike'ta ölçüldü, testte yok) |
| G17 Bağımlılık gerçekliği | ❌ Yok (CI işi) |
| G20 Geri dönüş / rollback | ❌ Yok |

**Okunuşu: 20 sınıfın 4'ünde derin, 2'sinde kısmi, 14'ünde hiç yok.**

Testlerin **derinliği** iyi; sorun **genişlik**. 39 testin tamamı elle
yazılmış beklenen değere dayanıyor — hiçbiri üretilmiş girdi kullanmıyor,
hiçbiri testlerin gücünü ölçmüyor.

### Korunmayan değişmezler

`02-DEGISMEZLER.md`'deki değişmezlerin **4'ünün bekçisi yok**:

| Değişmez | Neden önemli |
|---|---|
| Y-12 Göremeyeceğin kaydı oluşturamazsın | Kontroller ayrışırsa sessiz yetki açığı |
| I-8 Jetonlar `httpOnly` çerezde | `localStorage`'a dönülürse sessizce güvenlik kaybı |
| G-5 Benzersizlik DB kısıtında | Eşzamanlı istekte çift kayıt |
| G-6 Zaman UTC + genişletilmiş saat | Yaz saatinde dinlenme kuralı yanlış hesaplanır |

*~~K-9 Uygulama süper kullanıcıyla bağlanmaz~~ — **12 Eylül'de kapandı**,
bekçisi `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)`.*

⚠ **14 Eylül: `DENETIM.py` bu sayıda bir tutarsızlık buldu.**
`02-DEGISMEZLER.md` özet tablosu **45** diyor, satırları sayınca **47** çıkıyor
(Yetki grubunda 14 satır var, tablo 12 diyor — Y-13 ve Y-14 sonradan eklendi
ama özet güncellenmedi). Bekçili sayısı da 41 yazıyor, 39 sayılıyor.
**Düzeltilmedi**; ayrı bir iş parçası olarak bırakıldı. Betiği koşarak
güncel hâlini gör.

G-6'nın bekçisi hâlâ yok, ama artık **ne olması gerektiği yazılı**:
`08-motor-testleri/v5/KABUL-OLCUTLERI.md` A4 ve A5. Kabul ölçütü var, test yok.
