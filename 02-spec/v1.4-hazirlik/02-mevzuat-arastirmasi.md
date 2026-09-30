# Mevzuat araştırması — belirsiz kuralların çözümü

**Ne bu:** `01-kural-yasal-siniflandirma.md`'de ⚠️ belirsiz bırakılan satırların
birincil mevzuat kaynaklarından çözülmesi.
**Tarih:** 16 Eylül 2026 · **Durum:** ⏳ ONAY BEKLİYOR
**İstek:** Mustafa — *"Hukuki konuları benden daha iyi araştırabilirsin diye düşünüyorum."*

---

## ⚠️ Bu ne değildir

**Ben avukat değilim ve bu hukuki tavsiye değildir.** Aşağıdakiler kanun ve
yönetmelik metinlerinden okunmuş **bilgilerdir**. Madde numaraları ve alıntılar
birincil kaynaklardan; yorumlar bana ait.

**Açık madde A-16 kapanmadı.** Sahaya çıkmadan önce bir iş hukuku uzmanı
bakmalı. Bu araştırma o görüşmeyi **kısaltır**, yerine geçmez: uzmana "hangi
kurallar yasal" diye boş sayfayla gitmek yerine, madde numaralı bir tabloyla
*"bunlar doğru mu"* diye gidilecek.

**Yöntem:** Yalnız kanun ve yönetmelik metinleri, akademik makale ve Yargıtay
kararı. Hukuk forumu kullanılmadı — orada yazanlar kaynak değil, yorumdur.

---

## 1. Özet — ne değişiyor

| Kural | Önce | Sonra | Sebep |
|---|---|---|---|
| `PART_TIME_LIMIT` | ⚠️ belirsiz | ✅ **YASAL** | Yönetmelik açıkça yasaklıyor |
| `ARDISIK_CALISMA_GUNU` | ⚠️ belirsiz | ❌ **FİRMA** (şartlı) | Kanunda 6 gün diye bir sayı yok |
| `VARDIYA_ARASI_DINLENME` | ✅ yasal (tahmin) | ✅ **YASAL** (doğrulandı) | Madde metni birebir bulundu |
| `ARDISIK_GECE_LIMIT` | ❌ firma | ❌ **FİRMA** (değişmedi) | Ama yanında eksik bir yasal kural çıktı |

**Ve iki yeni bulgu** — ikisi de senin ilk müşterini doğrudan ilgilendiriyor:
katalogda **olmayan bir yasal kural** ve gece sınırının **sektör istisnası**.

---

## 2. Çözülen belirsizlikler

### `PART_TIME_LIMIT` → ✅ YASAL

**Soru:** Part-time çalışanın sözleşme saatini aşmak yasaya aykırı mı, yoksa
sadece sözleşme meselesi mi?

**Cevap: yasaya aykırı.** Fazla Çalışma Yönetmeliği md. 8, fazla çalışma
yaptırılamayacakları sayıyor ve listede açıkça yer alıyor:

> *"Kısmî süreli iş sözleşmesi ile çalıştırılan işçiler"*
>
> *"Kısmî süreli iş sözleşmesi ile çalışan işçilere fazla sürelerle çalışma da
> yaptırılamaz."*

İkinci cümle kritik: yalnız **fazla çalışma** (45 saat üstü) değil, **fazla
sürelerle çalışma** (sözleşme saati ile 45 saat arası) da yasak. Yani part-time
birinin sözleşmesi 20 saatse, 25 saat çalıştırmak — 45'in çok altında olsa
bile — yönetmelik ihlali.

**Sonuç:** `yasal = true`, `kabul_edilebilir = false`. Şartnamedeki
`tolerans_saat: 0` varsayılanı **tam doğru** — tolerans olamaz, çünkü kanun
tolerans tanımıyor. Fikstürlerdeki C08/C09/C10 sınırları bu yüzden sert.

### `ARDISIK_CALISMA_GUNU` → ❌ FİRMA KURALI (bir şartla)

**Soru:** "En çok 6 gün üst üste" ayrı bir yasal kural mı, hafta tatilinin
türevi mi?

**Cevap: kanunda 6 gün diye bir sayı yok.** İş K. md. 46 şunu diyor:

> *"…yedi günlük bir zaman dilimi içinde kesintisiz en az yirmidört saat
> dinlenme (hafta tatili) verilir."*

Kanun gün saymıyor, **pencere** tanımlıyor. 6 sayısı bu pencerenin kayan
(rolling) okunuşundan **türetiliyor**: her 7 günlük dilimde bir dinlenme günü
olacaksa, 7. gün çalışılamaz.

Yargıtay bu okumayı destekliyor — hafta tatili **toplu kullandırılamaz** ve
**bölünemez**:

> *"Hafta tatilinin toplu halde kullandırılması yasa hükmünün konuluş amacına
> aykırı olduğundan, bu şekilde hafta tatili kullandırıldığının kabulü mümkün
> değildir."* — Y. 22. HD, 23.01.2019, E. 2017/19485, K. 2019/1727

Bu önemli, çünkü toplu kullandırma yasağı **12 gün üst üste çalıştırma
numarasını** kapatıyor (izinleri iki haftanın uçlarına yığıp aradaki 12 günü
çalıştırmak).

**Sonuç:**

| Kural | Sınıf | Gerekçe |
|---|---|---|
| `HAFTA_TATILI` | ✅ yasal | Kanunun kendisi (md. 46) |
| `ARDISIK_CALISMA_GUNU` | ❌ firma, kabul edilebilir | Türev. Firma 5 demek isterse diyebilir |

> ### ⚠ Ama bir şartla — ve bu şart şartnamede yazmıyor
>
> `ARDISIK_CALISMA_GUNU`'nun firma kuralı olabilmesi, `HAFTA_TATILI`'nin
> **gerçekten kayan 7 günlük pencere** olarak uygulanmasına bağlı. Takvim
> haftası olarak uygulanırsa 12 gün üst üste çalışma yasal görünür ve o zaman
> tek koruma `ARDISIK_CALISMA_GUNU` olur — ki o da kabul edilebilir bir firma
> kuralı, yani kapatılabilir.
>
> v1.3 §6.2'de `HAFTA_TATILI` parametresi `pencere_gun: 7` yazıyor ama
> **kayan mı sabit mi söylemiyor.** v1.4'te açıkça "kayan" yazılmalı.
> **T-11** olarak kaydettim.

### `VARDIYA_ARASI_DINLENME` → ✅ YASAL (doğrulandı)

Tahmin değil artık, madde metni elimde. Postalar Halinde İşçi Çalıştırılarak
Yürütülen İşlerde Çalışmalara İlişkin Özel Usul ve Esaslar Hakkında Yönetmelik,
**md. 9**:

> *"Posta değişiminde işçiler sürekli olarak en az onbir saat dinlendirilmeden
> çalıştırılamaz. Bu hüküm, postası değiştirilen işçilere de uygulanır."*

11 saat doğru, `yasal = true` doğru. **A4 senaryosundaki Cem vakası bu maddeye
dayanıyor** — 8 saat dinlenme açık ihlal.

---

## 3. Yeni bulgu 1 — katalogda olmayan bir yasal kural

Aynı yönetmeliğin **md. 8**'i, katalogda hiç karşılığı olmayan bir zorunluluk
getiriyor:

> *"…en fazla bir iş haftası gece çalıştırılan işçilerin, ondan sonra gelen
> ikinci iş haftasında gündüz çalıştırılmaları suretiyle…"*

Yani: **bir işçi en fazla bir iş haftası üst üste gece postasında
çalıştırılabilir, sonra gündüze geçmesi gerekir.**

Katalogda buna karşılık gelen hiçbir kural yok:

| Katalogdaki kural | Ne yapıyor | Bu maddeyi karşılıyor mu |
|---|---|---|
| `ARDISIK_GECE_LIMIT` (3) | Üst üste gece sayısını sınırlar | ❌ Hayır — firma kuralı, kapatılabilir |
| `VARDIYA_ROTASYON_YONU` | Vardiya ileri kaysın | ❌ Hayır — yumuşak, yön kuralı |
| `GECE_VARDIYASI_AZAMI` | Gecede 7,5 saat | ❌ Hayır — süre kuralı |

**Önerim — yeni kural:**

| Kod | Tür | Kapsam | Parametre | Varsayılan | Yasal | Kabul |
|---|---|---|---|---|---|---|
| `GECE_POSTASI_DEVRI` 🆕 | SERT | S | `azami_ardisik_gece_haftasi` | 1 | ✅ | 🔒 Hayır |

`ARDISIK_GECE_LIMIT` (3) yerine geçmez, **yanında durur**: biri kanunun tavanı
(kapatılamaz), diğeri firmanın daha sıkı uyku sağlığı politikası (kapatılabilir).
Bu, senin K-18 kuralına birebir uyuyor — firma kanunu esnetemez, ama kendi
daha sıkı kuralını koyabilir.

> **Not:** Bu kural haftalık planın **dışına** taşıyor — "geçen hafta da gece
> çalıştı mı" bilgisi gerekiyor. Şartnamedeki lookback penceresi (§11.2) bunu
> zaten taşıyor, yeni altyapı gerekmiyor.

**Katalog 34 → 35 kural oldu.**

---

---

## 3b. 30 Eylül gecesi — md. 7 ve md. 8'in **tam metni** ve iki karar *(hukukçu yok; çevrimiçi kaynaklarla)*

16 Eylül'de md. 8'in yalnız birinci fıkrasının bir parçası alıntılanmıştı.
30 Eylül'de yönetmeliğin tamamı okundu (Lexpera konsolide metni; RG
07.04.2004/25426, son değişiklik 29.06.2024). Üç fıkra kuralları değiştirdi.

### md. 7/2 — "gece çalışması" neyin sayıldığı

> *"Çalışma süresinin yarısından çoğu gece dönemine rastlayan bir postanın
> çalışması, gece çalışması sayılır."*

**Sonuç 1 — `GECE_VARDIYASI_AZAMI`'nin ölçüsü değişti (K-44, T-74).**
Şartname *"gece penceresine düşen çalışma 7,5'i geçemez"* diyordu. Yargıtay
9. HD, 2016/36126 E., 2020/17967 K.: 20:00–08:00 vardiyasında bilirkişi gece
hesabını 06:00'da kesmişti; Yargıtay bozdu — hesap fiili bitiş 08:00'e kadar
yapılır, *"çalışmanın yarısından fazlası gece dönemine denk gelince tüm
çalışma gece kurallarına tabi."* Doktrin (Baysal): bu okuma **postalar
hâlinde** çalışılan işyerleri içindir; vardiyasız işyerinde yalnız 20:00
sonrası sayılır; örnek: *"17:00–01:00 çalışan işçinin çalışmasının tamamı gece
sayılır."* Biz vardiya ürünüyüz → gece postasının **bütün** net süresi 7,5'i
geçemez. 22:00–08:00 (1 sa mola) artık yasa dışı; 16:00–01:00 (1 sa mola,
ilk müşteride 82 kez) yazılı onaysız yasa dışı.

**Sonuç 2 — işaretsiz vardiyanın gece tahmini bu tanıma bağlandı (T-69).**
Eski tahmin *"pencereye en ufak değme"* idi: 13:00–21:00'ü gece sayıyor,
00:00–08:45'i saymıyordu.

**Sonuç 3 — işaret tabandır (K-43).** Firma işareti yasal kuralları iki
yönde de bozabiliyordu; artık yasal kurallar yönetmelik tanımını kullanır,
firma işareti firma kurallarında yalnız **ekler**.

### md. 8 — postaların değişme süresi, tam metin

> *(1) "Gece ve gündüz işletilen ve nöbetleşe işçi postaları çalıştırılarak
> yürütülen işlerde postalar; en fazla bir iş haftası gece çalıştırılan
> işçilerin, ondan sonra gelen ikinci iş haftasında gündüz çalıştırılmaları
> suretiyle ve postalar birbirlerinin yerini alacak şekilde düzenlenir."*
>
> *(3) "İşin niteliği ve yürütümü, iş sağlığı ve güvenliği gözönünde
> tutularak, gece ve gündüz postalarında iki haftalık nöbetleşme esası da
> uygulanabilir."*

Aynı hüküm İş K. md. 69'da da var (*"…postalar sıraya konur. Gece ve gündüz
postalarında iki haftalık nöbetleşme esası da uygulanabilir."*).

**Ne tanımlı değil:** *"bir iş haftası gece çalıştırılan"* — haftanın bir
kısmı gece bir kısmı gündüz çalışan kişi için hiçbir kaynak bir şey
söylemiyor. Kaynakların ortak cümlesi kuralın amacı: **sürekli gece
çalıştırma yasağı.** Yargıtay 22. HD, 2017/24339 E., 2019/18396 K.: işçi son
bir ay aralıksız gece vardiyasında çalıştırılmış — yönetmeliğe aykırı, haklı
fesih.

**Karar (K-45):** yönetmeliğin tek vardiya için kullandığı ölçü haftaya
uygulanır — haftanın çalışma saatlerinin yarısından çoğu gece postasındaysa
gece haftasıdır. Daha sıkısı ayarla mümkün, gevşeği değil. Parametre 2'ye
kadar (md. 8/3); 2 = iki hafta gece, iki hafta gündüz.

**⚠ Sektör istisnası (6645 s. K.) bu maddeyi kapsamıyor** — yalnız 7,5 saat
sınırı için. İlk müşterinin 16:00–01:00 ekibi (yönetmeliğe göre gece
postası) yazılı onayla 7,5 saati aşabilir ama **haftalık nöbetleşmeden
kurtulamaz.**

### Kaynaklar (30 Eylül)

- [Postalar Hâlinde İşçi Çalıştırılarak Yürütülen İşlerde Çalışmalara İlişkin Özel Usul ve Esaslar Hakkında Yönetmelik — Lexpera konsolide metin](https://www.lexpera.com.tr/mevzuat/yonetmelikler/postalar-halinde-isci-calistirilarak-yurutulen-islerde-calismalara-iliskin-ozel-usul-ve-esaslar)
- [Yargıtay 9. HD 2016/36126 E., 2020/17967 K. — "çalışmaların tamamı gece çalışması olarak değerlendirilmelidir" (Musa Çakmakçı, muhasebetr.com)](https://www.muhasebetr.com/yazarlarimiz/musacakmakci/0160/)
- [Yargıtay 7. HD 2013/3898 E., 2013/12354 K. — haftalık 45 saat aşılmasa da gece 7,5 saati aşan çalışma fazla çalışmadır (muhasebetr.com)](https://www.muhasebetr.com/yazarlarimiz/musacakmakci/0106/)
- [Mustafa Baysal — "yarısından çoğu" kuralı postalar hâlinde işyerleri içindir; 17:00–01:00 örneği](https://mustafabaysal.com/gece-calismasi-nedir/)
- [Harbiye Hukuk — işçi sürekli gece vardiyasında çalıştırılabilir mi (22. HD 2019/18396)](https://www.harbiyehukuk.com/isci-surekli-gece-vardiyasinda/)
- [Mimoza Hukuk — sürekli gece vardiyası, nöbetleşme zorunluluğu](https://www.mimozahukuk.com/isci-surekli-gece-vardiyasinda-calistirilabilir-mi/)
- [SMS Hukuk — gece kavramı ve gece çalışmasına ilişkin düzenlemeler](https://www.smshukuk.com/post/i%CC%87%C5%9F-hukukunda-gece-kavram%C4%B1-ve-gece-%C3%A7al%C4%B1%C5%9Fmas%C4%B1na-i%CC%87li%C5%9Fkin-d%C3%BCzenlemeler)
- [Nevzat Erdağ — postalar hâlinde (vardiyalı) çalışma; iki haftalık nöbetleşme](https://www.nevzaterdag.com/is-kanununa-gore-postalar-halinde-vardiyali-calisma/)

## 4. Yeni bulgu 2 — gece sınırının sektör istisnası · **ilk müşterini ilgilendiriyor**

`GECE_VARDIYASI_AZAMI` = 7,5 saat doğru, ama **mutlak değil.**

6645 sayılı Kanun (23 Nisan 2015) İş K. md. 69'a istisna getirdi. Aynı istisna
Postalar Yönetmeliği md. 7'de de var:

| Sektör | 7,5 saat aşılabilir mi | Şart |
|---|---|---|
| Turizm | ✅ Evet | İşçinin **yazılı onayı** |
| Özel güvenlik | ✅ Evet | İşçinin **yazılı onayı** |
| Sağlık hizmeti | ✅ Evet | İşçinin **yazılı onayı** |
| Petrol arama / sondaj | ✅ Evet | İşçinin **yazılı onayı** |
| Diğer bütün sektörler | ❌ Hayır | — |

### Bu neden önemli

Elindeki tek gerçek müşteri verisi bir **seyahat acentesine** ait — turizm.
Ve o veride **182 atama gece yarısını aşıyor.** Yani bu istisna teorik bir
kenar durum değil, ilk müşterinde ilk gün karşına çıkacak.

Bugünkü tasarımla sistem o firmada gece 8 saatlik vardiyayı **yasal ihlal**
sayar ve — K-20 gereği — yöneticiye kabul seçeneği bile sunmaz. Plan
yayınlanamaz. Oysa yazılı onay varsa tamamen yasaldır.

### Ne gerekiyor

İki yeni veri alanı, ikisi de küçük:

| Nerede | Alan | Ne için |
|---|---|---|
| `tenants` | `sektor` | Firma istisna kapsamında mı |
| `employees` (ya da `employee_contracts`) | `gece_calisma_yazili_onay` + tarih | O çalışan onay vermiş mi |

Kural şöyle işler: firma istisna sektöründe **ve** o çalışanın yazılı onayı
varsa, `GECE_VARDIYASI_AZAMI` o çalışan için uygulanmaz. İkisinden biri eksikse
7,5 saat sınırı yürürlüktedir.

> Bu, onayladığın **"bayrak satır bazlı olabilir"** kararının (Sorun 2) üçüncü
> örneği. Orada kural örneğine bağlıydı; burada **çalışana** bağlı. Aynı ilke:
> bir kuralın yasal olup olmaması bağlama göre değişebiliyor.

---

## 5. Doğrulanan diğer maddeler

| Kural | Dayanak | Durum |
|---|---|---|
| `GUNLUK_AZAMI` = 11 | İş K. md. 63/2 — *"günde onbir saati aşmamak koşulu ile"* | ✅ Doğrulandı. K-18 doğru |
| `HAFTALIK_AZAMI` = 45 | İş K. md. 63/1 | ✅ Doğrulandı |
| `YILLIK_FAZLA_MESAI_TAVANI` = 270 | Fazla Çalışma Yönetmeliği md. 5 — *"bir yılda ikiyüzyetmiş saatten fazla olamaz"* | ✅ Doğrulandı |
| `HAFTA_TATILI` = 24 saat / 7 gün | İş K. md. 46 | ✅ Doğrulandı (pencere tipi hariç — T-11) |
| `GECE_VARDIYASI_AZAMI` = 7,5 | İş K. md. 69 · Postalar Yön. md. 7 | ✅ Doğrulandı, **istisnalı** |

---

## 6. Hâlâ uzman gözü bekleyen iki şey

Araştırma bu ikisini **kapatamadı** — A-16 bu kadarıyla açık kalıyor.

### K-4 · Mola eşiği brüt süreye mi uygulanır

İş K. md. 68 ara dinlenmesini *"günlük çalışma süresi"*ne bağlıyor, ama aynı
madde *"ara dinlenmeleri çalışma süresinden sayılmaz"* diyor. Tanım kendine
dönüyor: mola süresini belirlemek için kullanılan "çalışma süresi", molayı
içeriyor mu?

**Kararımız brüt** (K-4) ve hata yönü tek taraflı: brüt hesap kanunun
istediğinden asla **az** mola vermez. Riski düşük, ama teyit gerekiyor.

### Yazılı onayın fazla çalışma ücretine etkisi

Turizmde gece 7,5 saati aşan kısım için yazılı onay alınmış olması, o sürenin
**fazla çalışma ücreti** doğurup doğurmadığını değiştirmiyor olabilir.
İncelediğim akademik kaynak bunu *"çözülmesi gereken uygulama sorunu"* olarak
işaretliyor, net cevap vermiyor.

**Bizi bugün bağlamıyor** — biz plan yapıyoruz, bordro hesaplamıyoruz. Ama
ileride ücret modülü gelirse burası ilk bakılacak yer.

---

## 7. Güncel sayım

| Grup | Önce | Sonra |
|---|---|---|
| ✅ Yasal | 10 | **12** (+`PART_TIME_LIMIT`, +`GECE_POSTASI_DEVRI`) |
| ⚠️ Belirsiz | 4 | **2** (yalnız rol/yetkinlik — satır bazlı, çözümü var) |
| 🔒 İmkânsızlık | 5 | 5 |
| ✅ Firma kuralı | 6 | **7** (+`ARDISIK_CALISMA_GUNU`) |
| Yumuşak | 9 | 9 |
| **TOPLAM** | 34 | **35** |

---

## 8. Onayın gereken üç şey

| # | Ne | Onayın |
|---|---|---|
| 1 | `GECE_POSTASI_DEVRI` yeni yasal kural olarak eklensin (35. kural) | ☐ |
| 2 | Gece istisnası için `tenants.sektor` + çalışan yazılı onay alanı eklensin | ☐ |
| 3 | `HAFTA_TATILI` penceresi **kayan** olarak yazılsın (T-11) | ☐ |

Üçü de onaylanırsa v1.4'ün kural bölümü tamamdır ve yazmaya başlarım.

---

## Kaynaklar

- [İş Kanununa İlişkin Fazla Çalışma ve Fazla Sürelerle Çalışma Yönetmeliği (md. 5, md. 8)](https://pdb.itu.edu.tr/docs/librariesprovider175/default-document-library/i%C5%9F-kanununa-ili%C5%9Fkin-fazla-%C3%A7al%C4%B1%C5%9Fma-ve-fazla-s%C3%BCrelerle-%C3%A7al%C4%B1%C5%9Fma-y%C3%B6netmeli%C4%9Fi.pdf?sfvrsn=0)
- [Postalar Halinde İşçi Çalıştırılarak Yürütülen İşlerde Çalışmalara İlişkin Özel Usul ve Esaslar Hakkında Yönetmelik (md. 7, 8, 9)](https://rayp.adalet.gov.tr/resimler/275/dosya/postalar-halinde-isci-calistirilarak-yurutulen-islerde-calismalara-iliskin-ozel-usul-ve-esaslar-hakkinda-yonetmelik04-12-202511-02-am.pdf)
- [Yargıtay kararları doğrultusunda 4857 sayılı İş Kanunu'nda hafta tatili ücreti — Dicle Üniv. Hukuk Fak. Dergisi](https://dergipark.org.tr/tr/download/article-file/4495733)
- [Hafta tatili ile ilgili İş Kanunu'nun 46'ıncı maddesinde yapılan değişikliğin değerlendirilmesi — Legal Blog](https://legal.com.tr/blog/is-hukuku/hafta-tatili-ile-ilgili-is-kanununun-46inci-maddesinde-yapilan-degisikligin-degerlendirilmesi/)
- [Turizm, özel güvenlik ve sağlık hizmeti yürütülen işlerde gece çalışması — Çalışma ve Toplum](https://www.calismatoplum.org/makale/turizm-ozel-guvenlik-ve-saglik-hizmeti-yurutulen-islerde-gece-calismasi)
