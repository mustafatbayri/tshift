# 2026-09-28 · Mola modeli bitti, gerçek ölçek ilk kez denendi (K-32…K-35)

**İş parçası:** 25 Eylül'de bilerek yarım bırakılan tek iş. Eşit dağıtım
aritmetiği yazılı ve beş testle sınanmıştı ama çağrısızdı; motor hâlâ tek
mola üretiyordu.

**Neden yarım bırakılmıştı:** `_sahada`'nın yeniden kurgusu gerekiyordu ve
25 Eylül'ün dersi *"ölçmeden ilerleme"* idi. Çözücünün kapsama matematiğinde
yapılan bir hata, **testler yeşilken** yanlış plan üretir.

---

## 1. Zorluk göründüğü yerde değildi

*"Sahada olmak"* = atanmış **ve** hiçbir mola bu dilimi kapsamıyor. Bu bir VE
bağlacı; CP-SAT'ta çarpım demek, çarpım da yardımcı değişken ve reification
demek. Kişi × gün × şablon × dilim başına yardımcı değişken, modeli ciddi
büyütürdü.

**Gerekmedi.** Molalar birbirini kesmiyorsa *"molada olmak"* bir **toplamdır**:

```
sahada = (kapsamayan yemek seçenekleri) − (kapsayan dinlenmeler)
```

İlk terim atanmışsa 1, atanmamışsa 0. İkinci terim dinlenme o dilimi
kapsıyorsa 1. İkisi de doğrusal.

> **Çakışmama kısıtı bu yüzden iki işe birden yarıyor:** adil plan için ve
> **bu aritmetiğin geçerliliği** için. İki mola aynı dilimi kapsarsa sonuç
> eksiye düşer ve kapsama hesabı sessizce bozulur. Bekçisi
> `test_molalar_BIRBIRINI_kesmez` — ve o testin varlık sebebi bu satırdır.

## 2. Model neden büyümedi

Aday pencereleri **eşit dağıtımdan** geliyor ve birbirini kesmiyor
(`_dinlenme_baslangiclari`). Bu yüzden dinlenmeler arası çakışma kısıtı
**hiç yazılmıyor** — yalnız yemekle çakışma yazılıyor. Her molaya iki aday
verildi; tek aday bırakmak yemekle çakışınca çözümsüzlük üretirdi.

## 3. Üretilen plan

*"60 dk yemek + 3×15 dk ücretli kısa mola"* politikasıyla, üç kişi, 09:00–18:00:

```
C3  11:00 dinlenme · 12:00 yemek · 13:00 dinlenme · 16:00 dinlenme
C2  12:00 dinlenme · 13:00 yemek · 14:00 dinlenme · 15:00 dinlenme
C1  12:00 dinlenme · 13:00 dinlenme · 14:00 yemek · 15:00 dinlenme
```

Üç yemek de 3–5 saat penceresinde ama **farklı saatlerde** — çözücü kişileri
kaydırmış. Sabit yerleştirilseydi üçü de aynı saatte molada olurdu ve kapsama
çökerdi; karar değişkeni olmalarının tek sebebi bu.

Dört süre gerçek planda doğrulandı: vardiya **9 saat** · çalışma **7 saat
15 dk** · ücret **8 saat**.

## 4. Yol üstünde bulunan tutarsızlık

`_mola_baslangiclari` yemek süresini politikadan alıyordu ama
`_mola_dilimleri` hâlâ `sablon["mola_dk"]`'ya bakıyordu. Politika farklı bir
süre verdiğinde **kapsama dilimleri yanlış hesaplanacaktı** — mola 30 dakika
planlanıp 60 dakikalık dilim kaplayacaktı ya da tersi.

25 Eylül'de `mola_dk` → politika geçişini yaparken bu çağrı yerini
atlamışım. Sessiz bir hataydı: politika tanımlanmamış kiracıda iki değer
eşit olduğu için hiçbir test kırmızı yanmazdı.

## 5. Ölçümler

| Ne | Sonuç |
|---|---|
| Motor birim testleri | **103 geçti** (25 Eylül: 98) |
| Altın senaryolar | **12 geçti, 4 atlandı** |
| Fikstür denetleyicisi | **11/11 tutarlı** |
| `YOL-KONTROL.py` | 8 kırık yol — hepsi eski |

## 6. K-33 · *"Firma sahada en az 5 diyecek"* — ve yanlış yazdığım mantık

Molalar çözücüye bağlanınca Mustafa şunu söyledi:

> *"Biz saat başı kafamıza göre kişileri yollayamayız. Gerçekte mesaide
> kalması gereken bir kişi sayısı tanımı gerekecek."*

Haklı olduğu ölçüldü: üç kişilik bir planda saat **12 ve 13'te sahada
sıfır kişi** vardı — sert ihlal 0, `yayınlanabilir` **True**. Üçü de aynı
anda molada ve plan temiz görünüyordu. Sebep kod değil **K-14**:
`MOLA_KAPSAMASI` bilerek yumuşak, ve o karar kişi başına *tek* öğle arası
varken verilmişti.

### ⚠ Kuralı yanlış kurdum, Mustafa yakaladı

Kuralı `MOLA_ASGARI_SAHADA` diye adlandırdım ve tabanı
`min(parametre, hücrenin asgarisi)` ile sınırladım. Gerekçesini de üç yere
yazdım: *"firma **molada** en az 5 dese de hücre 2 kişi istiyorsa taban
2'dir."*

> **Mustafa:** *"Firma molada en az 5 demeyecek, firma sahada en az 5
> diyecek, yanlış mantık kurma lütfen."*

İki ayrı hata vardı:

1. **Yanlış cümle.** Parametre bir mola kotası değil **saha tabanı**. Kuralın
   adı bile yanlıştı — `MOLA_` ile başlamamalıydı.
2. **Yanlış mantık.** `min(...)` firmanın sayısını **sessizce** talep
   tablosunun sayısıyla değiştiriyordu. Firma 5 der, hücre 2 isterse motor 2
   uygular — firmanın cümlesi buharlaşır.

**En kötüsü buydu:** `test_taban_hucre_ASGARISINI_asamaz` adlı bir test
**hatayı sabitliyordu**. Yani hatayı kalıcı hâle getiren şey testin
kendisiydi — yeşil bir test, yanlış bir mantığı koruyor.

Düzeltme: ad `SAHADA_ASGARI`, parametre `asgari_sahada`, sınır kaldırıldı.
Test silinmedi, **tersine çevrildi** (`test_taban_TALEBE_boyun_egmez`).
Mutasyonla sınandı: eski `min(...)` mantığı geri konduğunda test kırmızı
oluyor — yani artık gerçekten bekçilik yapıyor.

**Üç mutasyonun üçü de yakalandı:**

| mutasyon | kırmızı yanan test |
|---|---|
| çözücü kısıtı kaldırıldı | 3 |
| doğrulayıcı kural gövdesi susturuldu | 1 |
| **eski `min(...)` mantığı geri kondu** | 1 |

Bu, projede **ilk kez** ölçülen bekçi kapsaması (A-6'nın küçük bir örneği).

### 🔴 T-44 · Kural çalışıyor ama geometri onu boğuyor

Kural doğru kurulduğunda plan **çözülmedi**. Önce kaba bir kapasite hesabı
yaptım (`N ≥ 3F`) — 15 senaryonun **10'unda** tuttu, yani yanlıştı. Doğru
kısıt pencerelerin **örtüşmesiydi**: kişi başına dört molanın **üçü**
`{11,12,13,14}` dört saatine sıkışıyor → **`N ≥ 4F`**, 15/15.

İki maliyet ayrı ölçüldü: **pencere darlığı** (`4F → ~1.8F`) ve **saat
yuvarlaması** (`~1.8F → ~1.24F`). Baskın olan pencere darlığı — **sezgi saat
yuvarlamasını suçluyordu**. Ayrıntı T-44'te; karar Mustafa'da.

> ⚠ Buraya "105 dk gerçek mola modelde 240 dk, **2.29×**" diye yazmıştım.
> Aynı gün Mustafa *"yemek ile molayı birbirine karıştırma"* deyince ayırdım:
> yemekte şişme **1.00×** (hata yok), dinlenmede **4.00×**. Harmanlanmış rakam
> hatanın hangi tarafta olduğunu gizliyordu. Bkz. 7. bölüm ve K-34.

### Bugünün dersi

İki kez aynı şey oldu: **ölçmeden kurduğum mantık yanlıştı, ölçtüğümde
düzeldi.** Bir kere ürün tarafında (Mustafa yakaladı), bir kere mühendislik
tarafında (kapasite formülü 10/15 tuttu). Yeşil test, doğru mantık demek
değil — bugün testin kendisi yanlıştı.

---

## 7. K-34 · Zaman birimi çeyrek saat — ve *"yemek ile molayı karıśtırma"*

T-44'ü üç seçenekle sundum. Mustafa ikinciyi seçti ve gerekçesi benim
elimde olmayan bir gerçekti:

> *"Molalar zaten normalde planlanırken, gün içinde 15 dk lık dilimlere
> dağıtılıyor. Yani 15:15'e de mola koyabiliyorlar, 15:30'a da 15:45'e de.
> Doğrusu bu."*

Yani saat izgarası bir **modelleme kolaylığı değil, gerçeğe aykırı bir
varsayımdı**. Ben onu "pahalı ama doğru" diye sunmuştum; değilmiş.

### ⚠ İkinci uyarı: *"Yemek ile molayı birbirine karıştırma"*

Bu uyarı benim kendi ölçümümdeki bir gizlemeyi açığa çıkardı. T-44'e
*"2.29× şişme"* yazmıştım. Ayrıştırınca:

| | gerçek | modelde | şişme |
|---|---|---|---|
| yemek | 60 dk | 60 dk | **1.00×** hata yok |
| dinlenme | 45 dk | 180 dk | **4.00×** hata burada |
| toplam | 105 dk | 240 dk | 2.29× ← benim rakamım |

Harmanlanmış rakam yemeğin **doğruluğunu** dinlenmenin **hatasıyla**
ortalıyordu. İki tipin aynı koda girip farklı sonuç alması, hatanın bu kadar
uzun süre görünmez kalmasının sebebiydi. K-32'de ikisini ayırmıştık; ben
ölçerken yeniden birleştirmişim.

### Kapsam sandığımdan dardı

Kırmızı kanıt yazınca sekiz testin **dördü yeşil geldi** — doğrulayıcı zaten
kesirli saatle doğru çalışıyormuş. Hata yalnız çözücünün dilim sayımındaydı.
Şartname §11.2 (girdi sözleşmesi) hiç değişmedi: talep yine saatlik okunuyor,
yalnızca daha sık **örnekleniyor**. Fikstürler ve altın senaryo girdileri
aynen geçerli kaldı.

### Altı test kırmızı yandı — ikisi gerçek hata, dördü eski davranışın kaydı

| test | ne çıktı |
|---|---|
| `test_adaylar_AYRIK` | **gerçek hata.** Pencere yarıçapına mola süresini katmamıştım; 4 saatlik vardiyada pencereler uç noktada değiyordu. Bu `_sahada` aritmetiğini bozar |
| `test_sigmayan_mola_UYDURULMAZ` | **testin kendisi yanlıştı.** *"4 saatlik vardiyaya 3×15 dk sığmaz"* diyordu — 45 dakika 4 saate elbette sığar. Sığmıyor görünmesinin sebebi saat izgarasının kendi kusuruydu; test o kusuru **kural sanmış** |
| `ESIT_dagilir`, `VARDIYAYA_gore_kayar` | yuvarlanmış değerleri (`11, 13, 15`) *"doğru cevap"* sayıyorlardı. Gerçek idealler `11:15, 13:30, 15:45` ve çeyrek izgarada **tam isabet** ediyor |
| `IKI_aday` | *"tam iki aday"* diyordu; iki aday saat izgarasının **zorladığı** bir saydı. Artık sayıyı değil, sayının **varlık sebebini** koruyor |
| `GEOMETRI_SINIRI` | tasarlanmış kırmızı: *"sınır değişti, kaydı güncelle"* |

Üç test **eski davranışı kural sanmıştı** — bu, sabahın dersinin (yanlış
mantığı sabitleyen yeşil test) aynı gün içinde ikinci kez tekrarı.

### 🔴 Yol üstünde: sessiz geçiş, çeyreğe saklanmış

İki kişilik planda ikisi de **14:15–14:30** arası molada. 14:00'de ve
15:00'te sahadalar. **14:15'te sahada sıfır kişi.** Doğrulayıcı: hiçbir ihlal.

K-33'ü doğuran sessiz geçişin **aynısı**. Molayı çeyreğe taşıyıp kontrolü
saatte bırakmak, sessiz geçişi düzeltmek değil **gizlemek** olurdu. İki kural
da çeyrek bazına indirildi.

### Sayılar

| | |
|---|---|
| eşik | `N ≥ 4F` → **`N ≥ 12F/7`** (15/15 senaryo) |
| taban 3 için gereken ekip | 12 kişi → **6** |
| çözüm süresi (40 kişi, taban 5) | **0.78 sn** — T-44'te *"bilmiyorum"* dediğim sayı |
| motor testi | 109 → **120** yeşil |

Kalan `~1.71×F` bir modelleme hatası **değil**: kısıtlar tek tek gevşetilerek
bulundu ki bağlayan şey **yemek ile ortadaki dinlenme molasının aynı dilimler
için yarışması**. Gerçek bir planlama gerilimi.

### Günün dersi — üç kez aynı şey

Ölçmeden kurduğum mantık **üç kez** yanlış çıktı ve üçünde de ölçüm düzeltti:

1. **`min(...)` sınırı** — Mustafa yakaladı (ürün tarafı)
2. **kapasite formülü** `N ≥ 3F` — 10/15 tuttu, doğrusu `4F` (mühendislik)
3. **yemek penceresi kalan darlığın sebebidir** tahmini — tutmadı; kısıtları
   tek tek gevşetince bağlayanın başka şey olduğu çıktı

Üçüncüsünden sonra tahmin etmeyi bırakıp **doğrudan ölçmeye** geçtim
(kısıtı tek tek kapatma). Doğru cevap ilk denemede geldi.

---

## 8. Gerçek ölçek — 350 kişi, ve çıkan altı bulgu

Mustafa:

> *"Test senaryolarını 15-20 kişilik bir ekip düşünerek yapıyorsun hep…
>  Kullanmadığımız hiçbir kural veya kriter olmamalı. Ancak bu şekilde
>  doğru test sonuçları elde edebiliriz."*

Üç ekipli (200 satış / 100 back office / 50 müşteri hizmetleri), 14 vardiya
şablonlu, hafta içi–hafta sonu ayrı eşikli, 39 kurallı bir sahne kuruldu.

**Bir saat içinde altı ayrı bulgu çıktı** — hepsi kodda aylardır duruyordu ve
hiçbiri 10 kişilik sahnelerde görünmüyordu:

| bulgu | ne çıktı |
|---|---|
| **T-45** 🔴 | Tanınmayan bir **değer** sessizce geçiyor. `part_time` yazıldı, motor tanımadı, yarı zamanlı tavanı 90 kişiye hiç uygulanmadı, hiçbir kanal bildirmedi |
| **T-46** ✅ | Motor SATIŞ çalışanını BACKOFFICE vardiyasına atayabiliyordu. Performans sorunu sanıldı, **doğruluk hatası** çıktı. Düzeltildi: 968→335 bin değişken |
| **T-47** ✅ | Çözümsüzlük 292 saniye sonra bildiriliyordu. Ön kontrol yazıldı: **10 saniye**, hücre adıyla |
| **T-48** 🟡 | *"Çözümsüz"* hem *kanıtlandı imkânsız* hem *süre doldu* demek. **Ölçülmedi, hipotez** |
| **T-49** ✅ | `durgunluk_saniye` tanımlıydı, açıklaması yazılıydı, **hiç okunmuyordu**. 903 sn → 111 sn |
| **K-35** | Aynı girdi farklı plan veriyor. Çözüm: tekrarlanabilirlik değil, **görünürlük + birikim** |

### Kapanış ölçümü

350 kişi · 1.757 atama · **0 sert ihlal** · %100 asgari kapsama · %98,8 hedef
kapsama · 0 saat fazla mesai · optimuma **%10** uzak · model 435 MB.

### ⚠ Üç test yazıldığı anda yeşildi ve hiçbir şey ölçmedı

Günün en önemli dersi bu. Üç ayrı testi **süreye** ya da **küçük sahneye**
dayandırdım; üçü de yeşil geldi ve ölçmek istediği şeyi hiç ölçmedi:

- ön kontrol testi **süreye** bakıyordu — dört kişilik sahnede çözücü zaten
  milisaniyede bitiyordu
- durgunluk testi 24 kişilik sahnede 3 saniyede `hedef_bosluk` ile bitiyordu
- iki aşama testi 350 kişiyi bekleyemezdi

Üçü de **mekanizmayı** sınayacak şekilde yeniden yazıldı (`durma_sebebi`,
`iki_asama`, `cozum_suresi_sn == 0`) ve mutasyonla doğrulandı.

Ayrıca `test_sigmayan_mola_UYDURULMAZ` eski davranışı **kural sanıp** yanlış
mantığı sabitliyordu.

### Motorun iyi tarafı

Veri setini kurarken **dört veri hatası** yapıldı. Motor **üçünü yakaladı** ve
doğru yeri gösterdi; yalnız biri sessizce geçti (T-45). Kilit biçimi hatasında
çözücü ve doğrulayıcı **birbirinden bağımsız olarak aynı şeyi** söyledi —
§7.6 tam bunun için var.

### Günün dersi — altı kez aynı şey

Ölçmeden kurulan mantık altı kez yanlış çıktı; altısında da ölçüm düzeltti.
İkisini Mustafa yakaladı (ürün), dördünü ölçüm (mühendislik). Tahmin
etmeyi bırakıp **kısıtları tek tek gevşetmeye** geçildiğinde doğru cevap ilk
denemede geldi — iki ayrı vakada.

---

## 9. Sıradaki iş — Mustafa'nın isteği

> *"Şu altın test senaryoları ve diğer test senaryolarını bana açıklayan,
> aptala anlatır gibi anlatacağın bir içerik istiyorum. İçimde bir his var,
> test senaryolarımızın eksik veya yetersiz olduğuna dair."*

Hissin dayanağı kayıtlarda zaten var: **A-6** açık ve 🔴 (*"testlerin gerçek
gücü ölçülmedi"*) · dış inceleme 19 bulgu buldu, iç tur hiçbirini bulamadı ·
12 altın senaryonun 4'ü hiç koşmuyor, biri ertelendi — yani pratikte **7** ·
14 senaryo sınıfı hiç yazılmadı · **T-40** (A7'nin gerekçesindeki metrik
motorda yok).

**Teşhis:** testler model içinde güçlü, **modelin kendisine kör**. Üç olay da
aynı şekil — T-19, 25 Eylül'ün yanlış mola modeli, T-40. Üçünde de testler
sorularını doğru cevapladı; **soru yanlıştı**. Bu yüzden aynı türden test
eklemek bu deliği kapatmaz.

**Eksik olan üç tür:**
1. **Sözleşme testleri** — fikstürden değil şartnameden türetilmiş.
   `test_girdi_sozlesmesi` tek örnek.
2. **Mutasyon ölçümü** — A-6. *"12/12 yakaladık"* turu elle seçilmiş
   kırılmalardı.
3. **Bekçi kapsaması** — 38 kuralın 23'ünün gövdesi var; kaçının bozulduğunda
   kırmızı yanan bir testi var **ölçülmedi**.

**Anlaşılan sıra:** önce ölç (bekçi kapsaması + senaryo haritası), sonra
ölçümün gösterdiği yere test yaz. Önce genişletip sonra ölçersek ne
kazandığımızı bilemeyiz.
