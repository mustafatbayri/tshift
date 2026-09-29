# TESTLER NEYİ GARANTİ EDER, NEYİ ETMEZ

**Kim için:** Mustafa ve ürün tarafı. Kod okumayı gerektirmez.
**Son güncelleme:** 29 Eylül 2026

---

## İçindekiler

1. [Bu belge niye var](#1-bu-belge-niye-var)
2. [Testin değeri yeşil olmasında değil](#2-testin-değeri-yeşil-olmasında-değil)
3. [Üç ayrı koruma katmanı](#3-üç-ayrı-koruma-katmanı)
4. [Altın senaryolar — tek tek](#4-altın-senaryolar--tek-tek)
5. [Motor testleri — gruplar hâlinde](#5-motor-testleri--gruplar-hâlinde)
6. [Ölçülen kapsama — dürüst tablo](#6-ölçülen-kapsama--dürüst-tablo)
7. [Neyin testi yok](#7-neyin-testi-yok)
8. [Bir testin iyi olduğu nasıl anlaşılır](#8-bir-testin-iyi-olduğu-nasıl-anlaşılır)
9. [Bu belge ne zaman güncellenir](#9-bu-belge-ne-zaman-güncellenir)

---

## 1. Bu belge niye var

Mustafa, 28 Eylül:

> *"Şu altın test senaryoları ve diğer test senaryolarını bana açıklayan,
> aptala anlatır gibi anlatacağın bir içerik istiyorum. İçimde bir his var,
> test senaryolarımızın eksik veya yetersiz olduğuna dair."*

O his **ölçüldü ve haklı çıktı**. Aynı gün, 350 kişilik gerçekçi bir veri
seti kurulunca altı ayrı hata bir saat içinde ortaya çıktı — hepsi kodda
aylardır duruyordu ve hiçbiri 10 kişilik test sahnelerinde görünmüyordu.

Bu belge iki soruyu cevaplar:

- **Bir test yeşilse ne öğrenmiş olurum?**
- **Neyi hâlâ bilmiyorum?**

İkincisi daha önemli.

---

## 2. Testin değeri yeşil olmasında değil

Bir testin tek işi vardır: **bozulduğunda kırmızı yanmak.**

Yeşil olması iki ayrı şey demek olabilir ve ikisi ekranda **aynı görünür**:

| yeşil | anlamı |
|---|---|
| ✅ gerçek | kural sınandı, plan doğru çıktı |
| ⚠ sahte | kural hiç zorlanmadı, o yüzden şikâyet etmedi |

İkincisi tehlikelidir çünkü güven verir ve hiçbir şey kanıtlamaz.

### Bunun üç canlı örneği (28 Eylül, hepsi aynı gün)

**a) Yeşil bir test yanlış mantığı sabitliyordu.**
Saha tabanı kuralı yazılırken bir sınır konmuştu: firma *"sahada en az 5"*
dese de talep tablosu 2 istiyorsa 2 uygulanıyordu. Bu yanlıştı — ve
`test_taban_hucre_ASGARISINI_asamaz` adlı bir test **tam olarak bu yanlışı
koruyordu**. Yani hatayı kalıcı hâle getiren şey testin kendisiydi.

Mustafa yakaladı: *"Firma molada en az 5 demeyecek, firma sahada en az 5
diyecek."* Test silinmedi, **tersine çevrildi**.

**b) Üç test yazıldığı anda yeşildi ve ölçmek istediğini hiç ölçmedi.**
Üçü de küçük sahnelere dayanıyordu; çözücü zaten milisaniyede bitiyordu,
dolayısıyla test ölçmek istediği mekanizmaya hiç dokunmuyordu.

**c) Bir kural tanımlıydı, açıklaması yazılıydı, hiç çalışmıyordu.**
Ayarlarda `"durgunluk_saniye": 120  # 2 dk iyileşme yoksa bitir` satırı
duruyordu. Parametre vardı, belgesi vardı, **hiçbir yerde okunmuyordu**.
Bunun bedeli ölçüldü: çözücü 900 saniye boşuna arıyordu.

> **Ders:** bir kuralın yazılı olması, yürürlükte olduğu anlamına gelmez.
> Bunu ancak onu çiğneyen bir testin kırmızı yanması kanıtlar.

---

## 3. Üç ayrı koruma katmanı

Sistemi koruyan üç ayrı şey var ve farklı sorulara cevap verirler.

### Katman 1 — Birim testleri (139 test)

**Soru:** *Tek bir kural doğru çalışıyor mu?*

Küçük, hızlı, tek bir şeyi sınar. Örnek: *"9 saatlik vardiyadan bütün
molalar silinirse mola hakkı ihlali yazılır mı?"*

**Garanti eder:** kuralın gövdesi yazıldığı gibi çalışıyor.
**ETMEZ:** kuralın kendisinin doğru olduğunu. Yanlış bir kuralı da aynı
titizlikle korur.

### Katman 2 — Altın senaryolar (11 senaryo, 7'si motoru sınar)

**Soru:** *Gerçek bir haftada uçtan uca doğru davranıyor mu?*

Baştan sona bir hikâye: girdi verilir, plan üretilir, sonuç denetlenir.

**Garanti eder:** parçalar birlikte çalışıyor.
**ETMEZ:** ölçekte çalıştığını. En büyük senaryo **10 kişiydi**.

### Katman 3 — Denetim betikleri

**Soru:** *Belgeler ile kod birbirini tutuyor mu?*

`DENETIM.py` ve `YOL-KONTROL.py`. Dokümanda yazan test sayısı kodla
uyuşuyor mu, kırık dosya yolu var mı, commit edilmemiş değişiklik var mı.

**Garanti eder:** belge yalan söylemiyor.
**ETMEZ:** kodun doğru olduğunu.

### ⚠ Üçünün de kaçırdığı şey

Hiçbiri *"bu kural gerçekten sınandı mı"* diye sormuyordu. 28 Eylül'de bunu
soran bir araç yazıldı (`kural-kapsamasi.py`) ve cevap şaşırtıcıydı — bkz.
[bölüm 6](#6-ölçülen-kapsama--dürüst-tablo).

---

## 4. Altın senaryolar — tek tek

On bir senaryo var. **Yedisi motoru**, dördü backend'i sınar. A5 ertelendi.

### Motoru sınayanlar

| | senaryo | ne garanti eder | ⚠ neyi ETMEZ |
|---|---|---|---|
| **A1** | Normal hafta | Sıradan bir haftada plan üretilir, sert ihlal çıkmaz | Zor hafta. Her şey bol, hiçbir kural zorlanmıyor |
| **A3** | İmkânsız durum ve yöneticinin kararı | Plan üretilemiyorsa motor **sebebini** söyler, sessizce boş dönmez | Sebebin hızlı geldiğini. 28 Eylül'e kadar 292 saniye sürüyordu |
| **A4** | Gece yarısını aşan vardiya | 16:00–01:00 vardiyası 9 saat sayılır, ertesi güne taşar | Haftanın ilk gününün gece saatlerini. Onu önceki hafta karşılar ve o veri okunmuyor |
| **A6** | Elle sabitlenmiş atamalar | Yöneticinin kilitlediği atama plana aynen yansır | Kilidin çelişkili olduğu durumu. 28 Eylül'de çelişkili kilit yazıldı, plan çözümsüz kaldı |
| **A7** | Cumartesi adaleti mi, kapsama mı | İki yumuşak kural çakışınca profil ağırlığı karar verir | Ölçekte adaletin ne olduğunu. 350 kişide sapma 79 çıktı |
| **A8** | Öğle arası planlaması | Mola planı üretilir, süreler doğru hesaplanır | Molanın gerçekten saha bırakıp bırakmadığını — **bu 28 Eylül'de ayrı kural oldu** |
| **A9** | Kadro yetmiyor | Kapasite yetmezse motor bunu söyler | Kapasitenin yettiği ama **geometrinin** yetmediği durumu |

### Backend'i sınayanlar (motor koşusunda atlanır)

| | senaryo | konu |
|---|---|---|
| **A2** | İzin planlamayı ezer | Onaylı izin atamayı iptal eder |
| **A10** | Çift tıklama | Aynı istek iki kez gelirse iki plan üretilmez |
| **A11** | Geçmiş veri eksik | Eksik veriyle ne olur |
| **A12** | Geçen haftanın planını kopyala | Kopyalama davranışı |

### ⚠ Altın senaryoların ortak kör noktası

**Hepsi küçük.** En büyüğü 10 kişi, 1 ekip, 3 vardiya şablonu. Bu yüzden
şunların hiçbirini yakalayamazlardı ve yakalamadılar:

- Bir çalışanın **başka ekibin** vardiyasına atanabilmesi (tek ekip vardı)
- Model kurma süresinin kabul edilemez olması (küçük modelde görünmez)
- Çözücünün bütçeyi boşuna tüketmesi (küçük sahnede zaten erken bitiyordu)
- Bellek yetmemesi

Bunların hepsi **350 kişilik veri seti** kurulunca bir saat içinde çıktı.

---

## 5. Motor testleri — gruplar hâlinde

139 test, 11 dosya.

| dosya | test | ne korur |
|---|---|---|
| `test_kurallar.py` | 48 | Kuralların tek tek doğru çalışması. En kalabalık grup |
| `test_mola_modeli.py` | 32 | Mola tipleri, dört ayrı süre hesabı, saha tabanı |
| `test_profiller.py` | 18 | Ağırlık profilleri (dengeli / kapsama / çalışan) gerçekten farklı plan üretiyor mu |
| `test_ceyrek_saat.py` | 11 | Zaman biriminin çeyrek saat olması; yemek ile molanın karışmaması |
| `test_on_kontrol.py` | 5 | Ulaşılamayan talep hücresi **çözmeden** bildiriliyor mu |
| `test_girdi_sozlesmesi.py` | 5 | Şartnamedeki girdi biçimi okunuyor mu, okunmayan alan bildiriliyor mu |
| `test_bagimsizlik.py` | 4 | ⛔ Çözücü ile doğrulayıcı birbirini **import etmiyor** |
| `test_durgunluk.py` | 4 | İyileşme durunca çözücü kendi duruyor mu |
| `test_ekip_kapsami.py` | 4 | Kişi yalnız kendi ekibinin vardiyasına atanabiliyor mu |
| `test_iki_asama.py` | 4 | Büyük modelde önce geçerli plan bulunuyor mu |
| `test_iyilestir.py` | 4 | Mevcut plandan devam edince plan **kötüleşmiyor** mu |

### Bunlardan biri neden özel: `test_bagimsizlik.py`

Dört test, ama mimarinin belkemiği. Şunu yasaklar: **plan üreten kod ile
planı denetleyen kod birbirini tanımasın.**

Sebebi basit — aynı kodu kullanırlarsa, üretendeki hata denetleyende de
olur ve hata **iki tarafta birden** görünmez olur. İkisi ayrı yazıldığında
biri yanılırsa öteki yakalar.

Bu dün canlı olarak işe yaradı: kilit biçimi yanlış yazıldığında çözücü ve
doğrulayıcı **birbirinden habersiz aynı şeyi** söyledi.

---

## 6. Ölçülen kapsama — dürüst tablo

Bu bölüm 28–29 Eylül'de yazılan `kural-kapsamasi.py` aracının çıktısıdır.
Araç şunu sorar: *350 kişilik gerçek bir planda her kural ne yaptı?*

Katalogda **39 kural** var. Bunların **24'ünün gövdesi yazılı**.

### Temiz bir koşuda

| durum | sayı | anlamı |
|---|---|---|
| **SINANDI** | 11 | Kural gerçekten zorlandı, ihlal buldu |
| **TEMİZ** | 13 | Kural çalıştı ama veri onu hiç zorlamadı — ⚠ **yeşili bir şey kanıtlamaz** |
| **GÖVDE YOK** | 15 | Henüz yazılmamış; `uygulanmayan_kurallar` kanalı bildiriyor |

### Kasıtlı olarak zorlandığında

`ihlal-vakalari.py` her kural için, **yalnız onu** çiğneyen küçük bir plan
bozması tanımlar ve kırmızı yanıp yanmadığına bakar.

```
KIRMIZI YANAN : 24 / 24
```

**Yani yazılmış her kuralın çalıştığı kanıtlı.** Ama temiz bir koşuda
13'ü hiç zorlanmıyor — o yüzden *"350 kişide yeşil"* cümlesi tek başına
o 13 kural hakkında hiçbir şey söylemez.

### Bu ikisi neden çelişmiyor

İki farklı soru:

- **Kapsama aracı:** *"Normal bir planda bu kural devreye girdi mi?"*
- **İhlal vakaları:** *"Bu kural hiç ateşleyebiliyor mu?"*

Birincisi *"yeşilim neyi kanıtlıyor"* sorusunun cevabı. İkincisi
*"kural sahiden var mı"* sorusunun.

---

## 7. Neyin testi yok

Dürüst liste. Bunlar bilinen boşluklar, sürpriz değil.

### a) Yazılmamış 15 kural

Katalogda var, gövdesi yok. Motor bunları `uygulanmayan_kurallar` diye
bildiriyor — yani sessiz geçmiyorlar. Ama **yayın kapısının** bu bildirimle
ne yapacağı henüz karara bağlanmadı.

Aralarında gece çalışmasıyla ilgili yasal kurallar da var.

### b) Geçmiş hafta okunmuyor

Pazartesi sabahın ilk saatlerini önceki haftanın gece vardiyası karşılar.
O veri motora hiç gitmiyor. 7/24 çalışan bir müşteride bu **ilk çarpılan
duvar** oldu.

### c) Ölçek testleri henüz otomatik değil

350 kişilik veri seti var ve çalışıyor, ama otomatik koşuda değil — elle
çalıştırılıyor. Yani ölçekte bir şey bozulursa **kimse görmez**.

Bu, 28 Eylül'de bulunan hataların tam olarak nasıl aylarca gizlendiğinin
cevabı.

### d) Aynı girdi farklı plan verebilir

Ölçüldü: 25 saniyede 21.905 ve 22.715. Sebebi paralel arama. Bu bir hata
değil, bilinçli takas — ama **testi yok**, yani farkın ne kadar büyüyebileceği
bilinmiyor.

### e) Tek bir cümlenin iki anlama gelmesi

Motor *"çözümsüz"* derken hem *"kanıtlandı, imkânsız"* hem *"süre doldu,
bulamadım"* demiş olabilir. İkisi çok farklı şeyler: biri personel alımına
kadar giden bir karar, öteki sadece beklemek. Ayrım çıktının derinlerinde
var, başlıkta yok.

⚠ **Bu madde ölçülmedi, kod okunarak çıkarıldı.** Kanıtı üretilmeden
kapatılmayacak.

---

## 8. Bir testin iyi olduğu nasıl anlaşılır

Tek yol var: **kodu bilerek boz, test kırmızı yanıyor mu bak.**

Buna mutasyon denir ve bu projede 28 Eylül'de ilk kez sistemli olarak
yapıldı. Sonuçlar:

| bozulan şey | kırmızı yanan test |
|---|---|
| Saha tabanı kısıtı kaldırıldı | 3 |
| Doğrulayıcı kural gövdesi susturuldu | 1 |
| **Eski yanlış mantık geri kondu** | 1 |
| Saat yuvarlaması geri getirildi | 2 |
| Pencere hesabından mola süresi çıkarıldı | 1 |
| Ön kontrol kapatıldı | 2 |

Üçüncü satır en değerlisi: Mustafa'nın yakaladığı hatayı geri koyduğumuzda
test kırmızı yanıyor. Yani o hata bir daha sessizce geri gelemez.

> **Kural:** yeni bir test yazıldığında, korumak istediği şeyi bozup
> kırmızı yandığını görmeden o test bitmiş sayılmaz.

---

## 9. Bu belge ne zaman güncellenir

- Yeni bir altın senaryo eklendiğinde → [bölüm 4](#4-altın-senaryolar--tek-tek)
- Yeni bir kural gövdesi yazıldığında → [bölüm 6](#6-ölçülen-kapsama--dürüst-tablo) sayıları
- [Bölüm 7](#7-neyin-testi-yok)'deki boşluklardan biri kapandığında → o madde silinir
- Ölçek testleri otomatik koşuya bağlandığında → (c) maddesi düşer

Sayılar **elle yazılmaz, sayılarak** güncellenir:

```
cd C:\Users\PC\Desktop\Tshift\09-motor
py -m pytest testler --collect-only -q

cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti
py kural-kapsamasi.py
py ihlal-vakalari.py
```
