# TShift Fizibilite Testi — Sonuç Raporu

**Sorulan soru:** 200 çalışan, 3 ekip ve geçmiş haftaların gerçekleşen verisiyle,
tanımlanan kısıtlara uyan **3 ayrı optimum senaryo planı** üretebilir miyiz — ve bu
çıktılar gerçekten kısıtlara uyuyor mu?

**Cevap: Evet.** Ölçülen sonuçlar aşağıda. Bu bir demo değil; her sayı bu klasördeki
kodun çalıştırılmasıyla üretildi ve tekrar üretilebilir.

---

## 1. Test verisi

Sentetik ama gerçekçi bir çağrı merkezi operasyonu (`uret.py` üretir, tohum sabit →
her çalıştırmada aynı veri):

| | |
|---|---|
| Çalışan | 200 (194 aktif, 6 pasif) |
| Sözleşme türü | 165 tam zamanlı, 35 yarı zamanlı |
| Takım lideri | 18 (T1: 8, T2: 6, T3: 4) |
| Ekip | 3 — T1 07:00–24:00, T2 08:00–21:00, T3 09:00–20:00 |
| Vardiya şablonu | 12 |
| Uygunluk kaydı olan çalışan | 58 (üni öğrencilerinin ders programı dahil) |
| Onaylı izin | 11 çalışan |
| Talep hücresi | 301 (ekip × gün × saat) |
| Talep — hedef | 5.431 kişi-saat |
| Talep — asgari | 3.930 kişi-saat |
| Geçmiş veri | 1.597 **gerçekleşen** vardiya kaydı, planın öncesindeki 14 gün |
| Kural | 17 (15 sert, 2 yumuşak) |

Geçmiş verinin işlevi dekoratif değil: haftalık saat limiti, hafta tatili ve
11 saatlik vardiya arası dinlenme, plan haftasının **ilk gününde** geçmiş
kayıtlara karşı ölçülüyor. Yani pazar gecesi 23:00'te biten bir vardiya,
pazartesi 07:00 vardiyasını fiilen bloke ediyor.

---

## 2. Mimari kararı: üreten kod ile doğrulayan kod ayrıdır

Bu spike'ın en önemli tasarım kararı budur.

- `planla.py` planı **üretir**. Kısıtları atama anında uygular.
- `degerlendirici.py` planı **denetler**. Planlayıcıyı hiç tanımaz; sadece
  girdi + plan JSON'ını alır ve 17 kuralı sıfırdan yeniden hesaplar.

Planlayıcı kendi çıktısını "temiz" ilan edemez. Bir kuralı yanlış anlarsa,
denetleyici bunu yakalar. Bu ayrım olmadan "0 ihlal" cümlesinin hiçbir
kanıt değeri olmaz.

---

## 3. Ölçülen sonuç — 3 senaryo

Aynı veri, aynı kurallar, sadece **hedef ağırlıkları** farklı:

| | **DENGELİ** | **KAPSAMA ODAKLI** | **ÇALIŞAN DOSTU** |
|---|---|---|---|
| **Sert ihlal (bağımsız denetim)** | **0** | **0** | **0** |
| Asgari kapsama | %100,0 | %100,0 | %100,0 |
| Hedef kapsama | %95,7 | %95,6 | %93,6 |
| Kapatılamayan hedef açığı | 235 kişi-saat | 240 kişi-saat | 345 kişi-saat |
| Fazla mesai | 92 sa | 114 sa | **0 sa** |
| Adalet (saat dağılımı σ) | 3,06 sa | 3,65 sa | **2,72 sa** |
| Atama sayısı | 975 | 978 | 936 |
| Çalıştırma süresi | 1,1 sn | 1,1 sn | 1,0 sn |
| Yumuşak uyarı | 4 | 5 | 4 |

**Senaryolar birbirinin kopyası değil:**

| | atama farkı |
|---|---|
| Dengeli ↔ Kapsama | %15,8 |
| Dengeli ↔ Çalışan dostu | %26,4 |
| Kapsama ↔ Çalışan dostu | %24,9 |

Ödünleşim tablodan okunuyor ve mantıklı: kapsama odaklı senaryo 5 kişi-saat
daha fazla hedef kapsıyor, karşılığında 22 saat fazla mesai ve daha bozuk bir
saat dağılımı üretiyor. Çalışan dostu senaryo fazla mesaiyi sıfıra indiriyor ve
en adil dağılımı veriyor, karşılığında hedef kapsamadan %2 feda ediyor.
**Üçünde de asgari kapsama %100 ve sert ihlal 0** — yani üçü de yayınlanabilir
planlar; müşteri bunlar arasında tercih yapıyor, "geçerli plan" arasında değil.

---

## 4. Denetleyici gerçekten çalışıyor mu? (sabotaj testi)

"0 ihlal" sonucu, ancak denetleyicinin ihlali yakalayabildiği kanıtlanırsa
bir anlam taşır. `sinav.py` geçerli planı 9 farklı şekilde bilerek bozar ve
her birinin doğru kural koduyla yakalanmasını bekler.

| Sabotaj | Beklenen kural | Sonuç |
|---|---|---|
| 9 saatlik sınırı aşan vardiya | GUNLUK_AZAMI | ✅ |
| 22:00 bitiş → ertesi 07:00 başlangıç | VARDIYA_ARASI_DINLENME | ✅ |
| Aynı kişiye çakışan iki vardiya | CAKISMA_YOK | ✅ |
| İzinli çalışanı izin gününe atama | ONAYLI_IZIN | ✅ |
| Uygunluk penceresi dışına atama | UYGUNLUK_TAKVIMI | ✅ |
| En yoğun saatten 4 kişi silme | ASGARI_KAPSAMA | ✅ |
| Tüm takım liderlerini çıkarma | ROL_KAPSAMASI | ✅ (301 hücre) |
| 8 saatlik vardiyaya 15 dk mola | MOLA_HAKKI | ✅ |
| Tek kişiye 7 günün tamamı | herhangi bir sert ihlal | ✅ |

**9 / 9 yakalandı.** Temiz plandaki sert ihlal sayısı: 0.

---

## 5. Plan yapılamadığında sebebini söyleyebiliyor mu?

Bu, kabul kriterlerinin en önemlisiydi. Bir planlama ürünü "yapamadım" derken
**hangi kuralın** bağladığını söyleyemiyorsa kullanıcı için kullanılamaz.

Test senaryosu: günlük azami 9 → 5 saat, haftalık azami 45 → 25 saat; talep sabit.

```
Sonuç : asgari karşılama %35,8 — kapatılamayan 2.523 kişi-saat
→ PLAN YAPILAMAZ.
```

Teşhis yöntemi: her sert kural tek tek gevşetilip yeniden planlanır; açığı
kapatan kural, bağlayan kuraldır.

| gevşetilen kural | kalan açık | kapanan |
|---|---|---|
| **GUNLUK_AZAMI** | 626 | **1.897** ← bağlayan |
| VARDIYA_ARASI_DINLENME | 2.523 | 0 |
| UYGUNLUK_TAKVIMI | 2.523 | 0 |
| ROL_KAPSAMASI | 2.523 | 0 |
| PART_TIME_LIMIT | 2.523 | 0 |
| ONAYLI_IZIN | 2.523 | 0 |
| HAFTA_TATILI | 2.523 | 0 |
| HAFTALIK_AZAMI | 2.523 | 0 |

Sistem, sıkılaştırdığım kuralı doğru buldu. Üründe bu şöyle görünür:

> **Bu hafta planlanamıyor.** Sebep: günlük azami çalışma süresi.
> Bu kuralı gevşetirseniz 1.897 kişi-saatlik açık kapanır.
> Tek başına gevşetmek yetmiyorsa: "tek bir kural sebep değil, kadro yetersiz."

Bu çıktı, ürünün **yapay zekâ katmanının** üstüne oturacağı yer: teşhis
sayısaldır, anlatı LLM'in işidir.

---

## 6. Bu spike'ın kanıtladığı ve kanıtlamadığı şeyler

**Kanıtladıkları**
- 200 çalışan / 301 talep hücresi / 17 kurallık bir problem 1 saniyede planlanıyor.
- Üretilen planlar, bağımsız bir denetleyiciye göre **sıfır sert ihlal** içeriyor.
- Ağırlık değiştirmek gerçekten farklı planlar üretiyor (%16–26 atama farkı) ve
  ödünleşimler beklenen yönde.
- Geçmiş gerçekleşen veri, plan haftasının ilk gününü doğru şekilde kısıtlıyor.
- Sistem çözümsüzlüğü tespit edip **sebebini kural adıyla** söyleyebiliyor.

**Kanıtlamadıkları (bilerek)**
- **Optimumluk garantisi yok.** Bu bir açgözlü (greedy) planlayıcı; iyi bir plan
  buluyor ama "daha iyisi yok" diyemiyor. Optimuma uzaklığı ölçmek için OR-Tools
  CP-SAT sürümü gerekiyor — bu sandbox'ta `pip` kapalı olduğu için burada
  çalıştırılamadı, sizin makinenizde çalıştırılacak. Beklenti: aynı veri setinde
  CP-SAT'in bulduğu hedef kapsama ile bu planlayıcının %95,7'si arasındaki fark
  = optimuma uzaklık.
- Gerçek müşteri verisiyle test edilmedi. Sentetik veri, kural mantığını test eder;
  veri kalitesi sorunlarını (eksik saat, çakışan kayıt, yanlış ekip) test etmez.
- Çok haftalık devir (rolling) senaryoları hâlâ kapsam dışında.
- Gece vardiyası gün aşırılığı ve otel senaryosu (7/24) **artık kapsamda** —
  bkz. §9.

---

## 7. Nasıl çalıştırılır

Python 3.11+ dışında hiçbir bağımlılık yok — kurulum gerekmiyor.

```bash
python3 uret.py      # girdi.json üretir (tohum sabit, tekrar üretilebilir)
python3 planla.py    # 3 senaryo planı + sonuc.json üretir, her birini denetler
python3 sinav.py     # sabotaj testi + çözümsüzlük teşhisi
```

| Dosya | İşlevi |
|---|---|
| `uret.py` | Sentetik veri üreteci → `girdi.json` |
| `degerlendirici.py` | **Bağımsız** kural denetleyicisi (17 kural) |
| `planla.py` | Açgözlü planlayıcı, 3 ağırlık profili → `plan_*.json`, `sonuc.json` |
| `sinav.py` | Sabotaj testi (9–11 mutasyon) + çözümsüzlük teşhisi |
| `uret_otel.py` | Otel veri üreteci (7/24, gece vardiyalı) → `girdi_otel.json` (bkz. §9) |
| `olcek.py` | Ölçek testi: 200–2.000 çalışan süre eğrisi |
| `karsilastir.py` | Kaydedilmiş planları yeniden çözmeden karşılaştırır |
| `cpsat.py` | OR-Tools CP-SAT kesin çözüm + greedy karşılaştırması (bkz. §8) |
| `cpsat_kontrol.py` | CP-SAT model kodlama testi — **kurulum gerektirmez** |
| `rapor.md` | Bu rapor |

---

## 8. Sonraki adım: optimuma uzaklık ölçümü (CP-SAT)

Geriye tek teknik soru kaldı: **bu planlar optimuma ne kadar yakın?**
`cpsat.py` aynı `girdi.json`'ı OR-Tools CP-SAT ile kesin olarak çözer. CP-SAT
yalnız bir çözüm değil, bir de **üst sınır** verir — aradaki fark, greedy
motorun kalite açığıdır.

```
py -m pip install ortools
py cpsat.py            # 120 sn süre sınırı, DENGELI profili
py cpsat.py 300        # daha uzun süre → daha dar bound
py cpsat.py 300 KAPSAMA
```

Çıktı, greedy ile CP-SAT'i yan yana koyar ve CP-SAT planını **aynı bağımsız
denetleyiciden** geçirir. Yorum:

| fark | karar |
|---|---|
| < %2 puan | greedy motor üretim için yeterli; ürün hızlı kalır |
| > %2 puan | motoru CP-SAT'e taşımak gerekçeli |

### Modelin kendisi nasıl test edildi

Bir optimizasyon projesinde en sinsi hata "çözücü çalışmadı" değil, **"çözücü
çalıştı ama yanlış problemi çözdü"**dür. Model kuralları hatalı kodlarsa CP-SAT
kusursuz bir çözüm üretir — yanlış bir problemin çözümünü.

`cpsat_kontrol.py` bunu OR-Tools kurmadan test eder: sahte bir CP-SAT modülüyle
modeli kurar, greedy'nin 0 ihlalli planını modelin değişken uzayına çevirir ve
**6.071 kısıtın her birini** tek tek sınar. Geçerli bir plan bir kısıtı ihlal
ediyorsa model yanlış kodlanmıştır.

```
py cpsat_kontrol.py    # kurulum gerektirmez
```

Bu test yazıldığı anda gerçek bir hata yakaladı: model, molayı vardiyanın ilk
ve son saatine koymayı yasaklıyordu — oysa MOLA_HAKKI kuralı molanın *süresini*
şart koşar, *yerini* değil. Model kural setinden katıydı ve CP-SAT'i gereksiz
yere kısıtlayacaktı. Düzeltildi; şu an 6.071 kısıtın tamamı geçiyor. İkinci
aşama, toplu mola sayaçlarının kişi bazına doğru dağıtıldığını doğrular
(975 atama, 0 ihlal).

### Modelde bilinçli farklar

- Greedy'de "sözleşme + profil toleransı" sert bir kapı gibi çalışıyordu.
  CP-SAT'te gerçek kural setine sadık kalındı: tam zamanlıda sert tavan yalnızca
  HAFTALIK_AZAMI (45 sa), sözleşme aşımı hedef fonksiyonunda cezadır. Bu,
  CP-SAT'e greedy'de olmayan bir serbestlik verir — farkın bir kısmı buradan
  gelebilir.
- "Kararlılık" (vardiya saatinin günden güne oynamaması) 17 kuralın parçası
  değil, yalnız greedy'de bir puanlama ağırlığıydı; modele konmadı. Bu yüzden
  ana karşılaştırma metriği **hedef kapsama yüzdesi**dir.

Hangi motor seçilirse seçilsin, bu klasördeki **denetleyici ve sınav altyapısı
aynen kullanılmaya devam eder** — asıl kalıcı varlık orasıdır.


---

## 9. Otel senaryosu — aynı motor, ikinci sektör

Ürünün asıl iddiası "tek üründe çok sektör". Buraya kadarki her sayı tek bir
çağrı merkezi veri setinden geliyordu ve o operasyonda **hiçbir vardiya gün
aşmıyordu** (07:00–24:00). Otel bunu kırar.

### Teknik mesele: gece vardiyası

23:00'te başlayıp 07:00'de biten bir vardiya iki takvim gününe yayılır.
`range(23, 7)` boş kümedir — yani sistemin ilk zaman modeli bu vardiyayı
göremiyordu bile. Çözüm, bitişi **genişletilmiş saatle** yazmak: `"31:00"`.
Süre, çakışma, dinlenme aritmetiği olduğu gibi çalışır; yalnız kapsama
sayarken 24'ü aşan saatler ertesi günün hücresine eşlenir.

Buna bağlı ikinci mesele: **devir vardiyaları.** Plan haftasının pazartesi
00:00–07:00 saatleri, pazar gecesi başlayan vardiyayla kapanır — o kişiler
zaten sahadadır ve plan onları değiştiremez. Değerlendirici bunu saymazsa
0. günün sabahında var olmayan bir açık görünür ve motor boşuna kişi eklemeye
çalışır. Geçmiş veriden gelen kapsama artık hesaba katılıyor.

### Kural havuzu genişledi, kod genişlemedi

Otele iki kural eklendi ve **ikisi de veriden geliyor, koda gömülü değil**:

| kural | dayanak |
|---|---|
| `GECE_VARDIYASI_AZAMI` | İş Kanunu md.69 — gece çalışması 7,5 saati geçemez |
| `ARDISIK_GECE_LIMIT` | ardışık gece nöbeti sınırı (parametre: 3) |

Çağrı merkezi veri setinde bu iki kural **yoktur** ve motor onları hiç
çalıştırmaz. Aynı ikili (değerlendirici + CP-SAT modeli) iki veri setini de
işler. Ürün tezi olan "yeni sektöre girerken kural yazılmaz, havuzdan seçilir"
burada mekanik olarak kanıtlanmış oluyor.

### Otel veri seti

| | |
|---|---|
| Çalışan | 300 (295 aktif) |
| Departman | 5 — Ön Büro ve Güvenlik **7/24**, Kat Hizmetleri / F&B / Mutfak uzun mesai |
| Şablon | 19 (2'si gün aşan gece vardiyası) |
| Talep hücresi | 679 (çağrı merkezinde 301) |
| Kural | 19 (17 sert) |
| Plana devreden gece vardiyası | 21 |

### Ölçülen sonuç

| | çağrı merkezi | otel |
|---|---|---|
| Sabotaj testi | **9 / 9** | **11 / 11** (2 gece kuralı dahil) |
| Çözümsüzlük teşhisi | doğru kuralı buldu | doğru kuralı buldu |
| Model–denetleyici tutarlılığı | birebir | birebir |
| Greedy asgari kapsama | %100 | %99,9 |
| Greedy sert ihlal | **0** | **5** (679 hücrede, MOLA_KAPSAMASI) |

Gece kuralları sabotajla ayrıca sınandı: 21:00–06:00'lık bir vardiya
(gece penceresinde 8 saat) ve aynı kişiye 4 ardışık gece — ikisi de doğru
kural koduyla yakalandı.

### Greedy oteli tam çıkaramıyor — ve bu bir bulgu

Açgözlü planlayıcı otelde 5 sert ihlal bırakıyor (679 hücrenin %0,7'si).
Hepsi aynı desende: **7/24 bir departmanda tek lider vardiyada ve molaya
çıkınca rol kapsaması düşüyor.** Greedy verdiği kararı geri alamaz; molayı
taşımak, lider eklemek ve gereksiz bir lider vardiyasını takas etmek için
üç ayrı onarım geçişi eklendi, 16'dan 5'e indi, sıfıra inmedi.

Bu, 2.000 çalışan ölçek testindeki bulgunun aynısıdır: **greedy zorlaşan
problemde bozuluyor.** Motor kararının (CP-SAT) gerekçesini zayıflatmıyor,
güçlendiriyor. Greedy düzeltilmedi — emekli ediliyor.

### Test bunun için zayıflatılmadı, GÜÇLENDİRİLDİ

Model kodlama testi "referans plan temiz olmalı" varsayımına dayanıyordu.
Otelde referans plan temiz değil. Kolay yol, o kısıtları testten çıkarmaktı.
Bunun yerine test iki yönlü hale getirildi:

> Modelin ihlal ettiği kısıtlar ile bağımsız denetleyicinin bulduğu ihlaller
> **birebir örtüşmeli.** Fazlası model gereksiz katı demektir; eksiği model
> gevşek demektir — asıl tehlikeli yön budur, çünkü CP-SAT o boşluğu
> kullanır ve kurala aykırı bir planı "optimum" diye sunar.

Otelde her ikisi de 5 çıktı, birebir. Bu, "0 ihlal" görmekten daha güçlü bir
kanıttır: model ile denetleyici bağımsız yazılmış iki kod olduğu hâlde aynı
şeyi görüyorlar.

### CP-SAT otelde — ölçülen sonuç

300 sn süre sınırı, DENGELI profili, 7.458 karar değişkeni, 10.974 kısıt:

| | GREEDY | **CP-SAT** |
|---|---|---|
| Sert ihlal | 5 | **0** |
| Asgari kapsama | %99,9 | **%100,0** |
| Hedef kapsama | %95,2 | **%99,6** |
| Fazla mesai | 104 sa | **72 sa** |
| Adalet σ | 3,52 sa | **1,15 sa** |
| Atama | 1.364 | 1.655 |

Optimuma uzaklık **%0,03** — pratikte kanıtlanmış en iyi.

**Greedy'nin çözemediği 5 ihlali CP-SAT native olarak çözdü** ve sebebi
yapısaldır: greedy molayı plan kurulduktan SONRA yerleştirir, sonra üç ayrı
onarım geçişiyle kurtarmaya çalışır. CP-SAT'te mola yerleşimi karar
değişkeninin kendisidir — kapsama kısıtı molayı zaten içerir, dolayısıyla
"molaya çıkınca lider kalmadı" durumu hiç oluşmaz. Sonradan onarılan bir şey
değil, baştan kurulmuyor.

Adalet σ'sındaki 3,52 → 1,15 düşüşü ayrıca dikkat çekicidir. CP-SAT 291 fazla
atama yapmış ama fazla mesaiyi 104'ten 72'ye indirmiş: greedy işi az kişiye
yığıp bir kısmını fazla mesaiye sokarken diğerlerini boş bırakıyormuş.

### Çalıştırma

```
py uret_otel.py                           # otel veri setini üret
py planla.py girdi_otel.json              # 3 senaryo (greedy)
py sinav.py girdi_otel.json               # 11 sabotaj + çözümsüzlük teşhisi
py cpsat_kontrol.py girdi_otel.json       # model–denetleyici tutarlılığı
py cpsat.py 300 DENGELI girdi_otel.json   # kesin çözüm
```

### Otelde üç senaryo — ölçüldü

| CP-SAT | DENGELİ | KAPSAMA | ÇALIŞAN |
|---|---|---|---|
| Sert ihlal | 0 | 0 | 0 |
| Hedef kapsama | %99,6 | **%99,8** | %99,2 |
| Eksik kişi-saat | 36 | **17** | 69 |
| Fazla mesai | 72 sa | 116 sa | **48 sa** |
| Adalet σ | 1,15 | 1,14 | **1,08** |
| Optimuma uzaklık | %0,03 | %0,03 | %0,07 |

Senaryolar ayrışıyor ve ödünleşim doğru yönde: kapsama odaklı senaryo 19
kişi-saatlik ek kapsama için 44 saat fazla mesai ödüyor; çalışan dostu senaryo
fazla mesaiyi 48 saate indirmek için 33 kişi-saat kapsamadan feragat ediyor.

**Ama dikkat edilmesi gereken bir bulgu var.** Greedy'de "çalışan dostu"
profilinin fazla mesaisi **0 saatti**; CP-SAT'te **48 saat**. Sebep şu:
greedy'de sözleşme aşımı SERT bir kapıydı (o profilde tolerans sıfır),
CP-SAT'te ise hedef fonksiyonunda bir CEZA. Ceza olduğu için çözücü,
6,4 puanlık kapsama kazancı karşılığında 48 saatlik fazla mesaiyi kabul
etmeyi tercih etti — matematiksel olarak doğru davrandı.

Ürün kararı: **"çalışan dostu" fazla mesai SÖZÜ veriyorsa, bu ağırlık değil
SERT KISIT olmalıdır.** Ağırlık bırakılırsa optimizasyon onu er geç takas
eder. Bu, kural tasarımında "neyi söz veriyoruz, neyi tercih ediyoruz"
ayrımının somut örneğidir.
