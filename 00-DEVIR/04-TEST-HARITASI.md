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

---

## Şartnamedeki kabul senaryoları — tanımlandı, hiçbiri koşmuyor

**Master Spec v1.3 §16** on iki altın senaryo tanımlıyor (A1–A12): basit
uygulanabilir, çelişkili sert kural → `cozumsuz`, yetkinlik açığı, **gece
yarısı → 8 saat dinlenme ihlali**, DST geçişi, kilitli revizyon, yumuşak hedef
çatışması, mola kapsaması, kısmi kapasite, idempotency, lookback eksikliği,
plan kopyalama.

**Durum (14 Eylül, ikinci oturum):** On ikisinin de *"doğru çalışıyorsa ne
görmeliyiz"* cümleleri ve somut veri setleri yazıldı —
`08-motor-testleri/v2/KABUL-OLCUTLERI.md`. Beklenen sonuçlar **şartnameden
türetildi**, motora bakılmadı; motor zaten yok.

| Adım | Durum |
|---|---|
| Kabul cümleleri yazıldı | ✅ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` §3 |
| Mustafa onayladı | ❌ **bekliyor** |
| Fikstürler yazıldı | 🟡 yalnız örnek (`08-motor-testleri/v2/fikstur/A04.json`) |
| Testler koşuyor | ❌ motor yok |

**Hiçbir test koşmuyor.** Bu tablonun ilk satırı yeşil diye kapsama
büyümedi — kabul ölçütü bir taahhüttür, bekçi değil. Bekçi, fikstür pytest'e
bağlandığında doğar.

A1–A9 motor testi olacak (Python + pytest), A10–A12 backend testi (bu
projedeki xUnit). Bu, projedeki en önemli test ilkesinin (uygulama ile
doğrulayıcı aynı varsayımdan beslenmez) şartname seviyesindeki karşılığı.

---

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
`08-motor-testleri/v2/KABUL-OLCUTLERI.md` A4 ve A5. Kabul ölçütü var, test yok.
