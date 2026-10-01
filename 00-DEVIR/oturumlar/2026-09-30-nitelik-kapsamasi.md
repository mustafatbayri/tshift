# 2026-09-30 · Rol ve yetkinlik kapsaması doğrulayıcıya bağlandı · dört yeni bulgu

**Kim.** Mustafa + Claude
**Nereden devam.** 29 Eylül gecesi commit edildi, push edildi, CI'ın iki işi de
yeşil yandı. Mustafa: *"iki iş te yeşil :) nerede kaldık devam ediyoruz"*

**Sıra.** Mustafa'nın 29 Eylül'de kurduğu sıra: gece işareti → iki veri seti →
**eksik kurallar** → testleri tekrarla. İlk ikisi bitmişti; bugün eksik kurallar.

---

## 0 · Gövdesiz 14 kural üçe ayrıldı, hepsi aynı anlamda "yok" değildi

Listeyi alfabetik okumak yanlış sonuç veriyor. Ölçülünce üç ayrı durum çıktı:

| durum | kaç | hangi kurallar |
|---|---|---|
| **çözücüde var, doğrulayıcıda yok** | 2 | rol kapsaması, yetkinlik kapsaması |
| ağırlığı tanımlı, gövdesi hiçbir yerde yok | 4 | ekip sürekliliği, tercih karşılama, vardiya rotasyon yönü, plan kararlılığı |
| hiçbir yerde yok | 8 | üçü **yasal**: gece vardiyası azami, gece postası devri, yıllık fazla mesai tavanı |

Mustafa ilk grubu seçti. Gerekçe en ağır olanıydı: o iki kural için **bağımsız
denetim hiç yoktu**. Çözücü kısıtı kendi kuruyor, plan zorunlu olarak uyuyor,
doğrulayıcı da *"ihlal yok"* diyor — **hiç bakmadan**. Şartname #7.6 iki yarıyı
tam olarak bunu engellemek için ayırıyor.

⚠ **Dünün cümlesinin sınırı burada görüldü.** 29 Eylül tam ölçekli koşumda
*"0 sert ihlal, yayınlanabilir True"* yazıyordu ve ben bunu iyi haber diye
aktardım. Doğru ama eksik: denetçi o iki kurala bakmadı. Motor bunu kendisi
bildiriyordu (`uygulanmayan_kurallar`), yayın kapısı o kanalı görmüyor (T-18).

---

## 1 · İki gövde yazıldı — şartnameden, çözücü kodundan değil

Çözücünün kısıt kodu **bilerek okunmadı**. T-19'un dersi: iki taraf aynı yanlış
geleneği paylaşırsa ikisi birbiriyle tutarlı ve ikisi de yanlış olur; bağımsız
denetim de o yanlışı göremez.

Şartname §6.4'ten üç kelime belirleyici çıktı:

| kelime | ne demek |
|---|---|
| **sahada** | molada olan sayılmaz — `SAHADA_ASGARI` ile aynı ölçü (K-33) |
| **açık saat** | talep hücresi olan saat; kapalı dönemde saha yoktur |
| **saatlerde** | yetkinlikte liste parametreden gelir; rolde liste yoksa açık saatlerin hepsi |

Ayrıca K-24: bu iki kuralda `yasal` bayrağı **satırın** özelliği. *"Her vardiyada
1 ilk yardım sertifikalı kişi"* muhtemelen yasaldır, *"kahvaltıda 1 barista"*
ticari tercihtir. Ek bir iş gerekmedi — her gereklilik satırı girdide ayrı bir
kural tanımı olduğu için her ihlal kendi bayrağını taşıyor.

**Kırmızı kanıt:** 14 test yazıldı, **9'u** kırmızı yandı.

⚠ **Üçü kırmızı YANMADI ve bunu kayda geçiriyorum.** *"Sahadaysa ihlal yok"*
diyen testler, kural **hiç yokken** de yeşil yanar — yani gövde yazılmadan önce
hiçbir şey ölçmüyorlardı. Bu oturumda aynı tuzağa iki kez düşülmüştü
(`assert True` ile biten testler). Üçü de gövde yazıldıktan **sonra** anlam
kazanıyor (fazla ihlal yazılmasını engelliyorlar), ama kırmızı kanıt sayısı
14 değil **9**.

**Mutasyon: beş bozma denendi, beşi de öldü** — ama biri ilk turda **yaşadı**:

| mutasyon | sonuç |
|---|---|
| molayı düşme (çözücü gibi atanmışı say) | iki test kırmızı |
| yalnız tam saate bak, çeyreği atla | beş test kırmızı |
| saat listesini yok say | üç test kırmızı |
| satırın yasal bayrağını yok say | bir test kırmızı |
| ekip süzgecini yok say | ⚠ **hepsi yeşil kaldı** |

Son satır bir boşluktu: ekip süzgeci iki yerde uygulanıyor ve her sahnede
ikincisi zaten yetiyordu. Fark ancak şu veride ortaya çıkıyor: kişi ekip
kadrosunda **değil** ama o ekibe atanmış. Yeni test yazıldı, mutasyon öldü.

---

## 2 · Parametresiz gereklilik satırı artık sessiz geçmiyor

Hangi rolün arandığı yazılmamışsa kural **denetlenemez**. Gövde boş liste
dönüyor, yani *"ihlal yok"* gibi görünüyor. `denetle.py`'nin ilkesi bunu
yasaklıyor: *"ihlal yok"* ile *"bakamadım"* aynı şey değil.

`eksik_boyutlar` kanalı genişletildi — kanal zaten *"kural yazılı, bir parçası
eksik"* için vardı (T-13'ün adalet boyutu). Artık şunu da yazıyor:

> *"gereklilik satırında `rol` yazılı değil; hangi niteliğin arandığı bilinmiyor
> — denetlenemedi"*

Bu bir ihlal **değil**: veri eksikliği plan hatası değildir.

---

## 3 · Ölçüm aracının kendi boşluğu — T-64

İhlal vakası aracı özetinde `basarili / len(VAKALAR)` yazıyordu: *"yazdığım
vakaların kaçı ateşledi."* Gövdesi yazılı ama **vakası olmayan** bir kural bu
paydada hiç görünmüyordu.

İki yeni gövde yazıldı, vakaları yoktu, araç **"EKSIK: 0"** demeye devam etti.

⚠ **29 Eylül'de yazdığım cümlenin dayanağı buydu:** *"gövdesi yazılı 26 kuralın
tamamı kendi vakasında kırmızı yanıyor, eksik sıfır."* Cümle doğruydu ama
aracın sorduğu soru yanlıştı.

Evren artık doğrulayıcının kural kayıt sözlüğü. Vakası olmayan gövde
*"VAKASI YOK — hiç sınanmadı"* diye ayrı satır alıyor ve eksik sayısına giriyor.
İki vaka yazıldı; şimdi **28 gövde · 28 vaka · 28 kırmızı · eksik sıfır**.

⚠ **Bu oturumda ölçüm aracının kendi payı ikinci kez boşluk çıktı.** İlki
çekirdek ölçüm aracıydı (tek koşuyu genel kural saymak). Ortak ders:
**ölçen aracın da bekçisi olmalı.**

---

## 4 · Bağımsız denetim ilk gününde iki bulgu buldu

Gövdeler yazılınca ortaya çıkan şey, gövdelerin kendisinden daha önemli.

### T-61 · Çözücü *"atanmış"*, doğrulayıcı *"sahada"* sayıyor

Şartname iki kuralı da *"sahada"* diye tanımlıyor; çözücü atama değişkenini
sayıyor, molayı düşmüyor.

**Ölçülen (3 kişi, tek takım lideri, 8–16 vardiyası):** çözücü planı üretti ve
**üçünün yemeği de aynı saate düştü** (11:00–12:00). O saatte sahada takım
lideri kalmadı. Denetçi o saatin **dört çeyreğinde** ihlal yazdı; çözücü kendi
ölçüsüne göre kuralı sağlıyor.

**T-57'nin aynı ailesi** — orada da doğrulayıcı haklı çıktı ve çözücü
düzeltildi. Karar Mustafa'da, çünkü bedeli plana yansıyor: çözücü de *"sahada"*
sayarsa nitelikli kişilerin molaları kaydırılmak zorunda kalır.

Ayrışma test paketinde **ölçülüyor, sabitlenmiyor** — ayrı bir test olarak
duruyor ve karar verilince silinecek ya da tersine çevrilecek.

### T-62 · Saat listesi yoksa çözücü hiçbir şey kısıtlamıyor

`saatler` verilmezse çözücünün iç döngüsü hiç çalışmıyor: aktif bir **SERT**
kural modele tek kısıt koymuyor. Şartname rol kuralını *"her açık saatte"* diye
tanımlıyor — yani liste yoksa **hepsi** geçerli olmalı, hiçbiri değil.

Aynı fonksiyonun ikinci yarısı ters yönde bozuk: `ekip` yazılmazsa hiç kimse
uygun sayılmıyor ve modele *"boş toplam en az 1 olsun"* kısıtı giriyor →
**plan çözümsüz**. Yöneticinin göreceği cümle *"bu kadroyla imkânsız"* olur;
sebebi bir eksik parametredir.

**Ölçülen (49 kişi, %95 seti, 180 saniye):** her ekibe *"en az 1 takım lideri
sahada"* gerekliliği kondu, `saatler` bilerek verilmedi.

| | gereklilik yok | gereklilik var, saat listesi yok |
|---|---|---|
| durum | çözüldü | çözüldü |
| atama | 221 | 221 — **aynı plan** |
| sert ihlal | 0 | **1.238** |
| yayınlanabilir | True | **False** |

⚠ **Bu sayının bir kısmı kodun değil ölçeğin sonucu.** 0.1 ölçekte ekip başına
yalnız **2** takım lideri var, talep 7/24. İki kişi 168 saati kapatamaz. Tam
ölçekte 42 takım lideri var; oradaki gerçek sayı **ölçülmedi**. Yani 1.238
*"çözücü kuralı görmüyor"*un kanıtıdır, *"gereklilik imkânsız"*ın ölçüsü
değildir.

---

## 5 · Veri seti tarafında dünün dersi tekrar etti — T-63

Yeni gövdeler bağlanınca zor veri seti bekçileri **yeşil kaldı**. Sebebi
araştırıldı:

| kural | sahnedeki hâli |
|---|---|
| rol kapsaması | `parametreler` alanı **yok** — hiçbir rol istenmiyor |
| yetkinlik kapsaması | `parametreler` alanı **yok** — hiçbir yetkinlik istenmiyor |
| sahada asgari | `asgari_sahada: 0` — saha tabanı yok |

Üçü de aktif. *"40 kuralın hepsi tanımlı"* cümlesi doğru ama **tanımlı olmak,
istemek değildir.**

Veri duruyor: sahnede 42 takım lideri, 302 agent, 118 kıdemli agent, 38 uzman;
yetkinlikler teknik, almanca, ingilizce, iade. Gereklilik yazılabilir,
yazılmamış.

⚠ **Dün kod tarafında aynı hatayı yapmıştım** (*"39 kuralın hepsi uygulanıyor"*,
15'inin gövdesi yoktu). Bugün aynısı veri tarafında çıktı. **Sayı saymak
yetmiyor; sayılan şeyin ne işe yaradığına bakmak gerekiyor.**

---

## Gün sonu durumu

| ne | sayı | nasıl |
|---|---|---|
| Motor birim testi | **198** yeşil | koşuldu (2 dk 13 sn) |
| Altın senaryolar | **12 geçti, 4 atlandı** | koşuldu |
| Fikstür tutarlılığı | 11 fikstürün hepsi tutarlı | koşuldu |
| Zor veri seti bekçisi | **12** yeşil (~4,5 dk) | koşuldu |
| İhlal vakaları | **28 gövde · 28 vaka · 28 kırmızı · eksik sıfır** | koşuldu |
| Kural kataloğu | **40** | sayıldı |
| Yazılı kural gövdesi | **28** (dün 26) | sayıldı |
| Gövdesi yazılmamış | **12** (dün 14) | sayıldı |

**Bugün kapanan:** T-64 (aynı gün)
**Bugün açılan:** T-61 · T-62 · T-63
**Açık 🔴:** on

**Gövdesi yazılmamış 12 kural:** ardışık gece limiti · ardışık hafta sonu
limiti · asgari vardiya süresi · çalışma saatleri · ekip sürekliliği · gece
postası devri · gece vardiyası azami · gece yarısını aşan · plan kararlılığı ·
tercih karşılama · vardiya rotasyon yönü · yıllık fazla mesai tavanı.

---

## Sırada

1. **T-62** — mekanik, karar gerektirmiyor. Saat listesi yoksa açık saatlerin
   hepsi; `ekip` yoksa sessizce çözümsüz kalmak yerine açık davranış.
2. **T-61** — Mustafa'nın kararı: çözücü de *"sahada"* mı sayacak?
3. **T-63** — Mustafa'nın kararı: gereklilik satırları ne olacak? Bu bir veri
   modeli sorusu değil, **işin nasıl yürüdüğü** sorusu.
4. Kalan 12 gövde. Sıradaki mantıklı grup **üç yasal kural** (gece vardiyası
   azami, gece postası devri, yıllık fazla mesai tavanı); ilk ikisi K-40'ın
   gece işareti sayesinde artık yazılabilir, üçüncüsü geçmiş veri istiyor.
5. T-59 (süre bütçesi aşımı) ve T-60'ın dört ölçümü hâlâ açık.

---

# AKŞAM · Kararlar alındı, üç bulgunun ikisi kapandı

Mustafa iki soruyu da cevapladı ve biri beklediğimin tersi çıktı.

## 6 · K-41 · Mola sahadan çıkarmaz — **değişen taraf doğrulayıcı oldu**

> *"Sahada bir müdürün işi 15 dk mola süresini bekleyebilir. Bu 'sahada olmalı'
>  kuralını bozmaz. Molalar sahada sayılır olarak geçebilir. Zaten mola öneri
>  gibi bir kurgu olacağından bu kadar derine inmemize gerek yok."*

Ben şartnamenin harfine bakıp doğrulayıcıyı *"sahada"* diye yazmıştım ve
T-57'nin refleksiyle çözücünün düzeltileceğini varsaymıştım. **Yanlış varsayım:**
hangi tarafın değişeceği şartnamenin kelimesine değil işin nasıl yürüdüğüne
bakılarak belirleniyor. Çözücü haklıydı.

İki test **tersine çevrildi**, silinmedi — gerekçeleri testlerin başına yazıldı.
K-33'te aynısı yapılmıştı: kararla çelişen test silinirse altı ay sonra
*"acaba neden böyle?"* diye sorulur ve kimse bilemez.

⚠ **Ayrım bilerek bırakıldı:** `SAHADA_ASGARI` molayı düşmeye devam ediyor.
Saha tabanı *"tezgâhta kaç kişi var"*dır, nitelik kapsaması *"o nitelik
ulaşılabilir mi"*dir.

⚠ **Şartname borcu:** §6.4'ün iki satırı hâlâ *"sahada"* diyor.
⚠ **Açık kalan:** yasal bayraklı bir satırda (*"her vardiyada 1 ilk yardım
sertifikalı kişi"*) molanın sayılması hukuken tartışılabilir. Mustafa daha
derine inilmemesini istedi.

## 7 · T-62 kapandı — ve bir testim mutasyondan sağ kurtuldu

Çözücüde üç şey düzeltildi: saat listesi yoksa **açık saatlerin hepsi**; `ekip`
yoksa **saha çapı**; kontrol artık **çeyrek** bazında. Dördüncüsü yeni bir
davranış: niteliği taşıyan kimse yoksa **kısıt yazılmaz, not yazılır** — kısıt
yazmak planı sessizce çözümsüz yapardı.

⚠ **Kırmızı kanıtlar mutasyonla üretildi**, çünkü gövdeyi testlerden önce
yazdım. Kırmızı önce kuralı burada uygulanmadı; kayda geçiyor.

⚠ **Bir test ilk turda mutasyondan sağ kurtuldu ve dersi ağır.** Test *"kural
iki lider istiyor, ikisi de atanmış mı"* diye soruyordu. Kısıt tamamen
kaldırıldığında test **yine yeşil** kaldı: fazladan atamanın maliyeti yok
(T-54), çözücü iki lideri zaten kendiliğinden atıyordu. **Bu motorda "atandı
mı" sorusu hiçbir şey kanıtlamıyor.** Yerine imkânsız bir gereklilik konuldu —
iki lider varken üç lider isteniyor; kısıt yazılıysa plan çözümsüz kalmak
zorunda. Cevap tek, tesadüfe kapalı.

Bugün mutasyon **iki kez** boşluk yakaladı (ekip süzgeci ve bu).

## 8 · T-63'ün rol tarafı kapandı — gereklilik konunca sahne çözümsüz kaldı

Mustafa'nın seçimi: *"Yalnız gündüz saatlerinde 1 lider."* Her ekip için ayrı
gereklilik satırı kondu (K-24), saatler **08:00–20:00**.
⚠ Saat aralığı benim seçimim, Mustafa saat vermedi.

**İlk deneme çözümsüz — ve `teshis_kesin` True, yani kanıtlandı, zaman aşımı
değil.** Sayarak:

| | |
|---|---|
| gündüz penceresi | 12 saat; en uzun vardiya ~10,5 saat → günü kapatmak için **2 lider** |
| hafta | 2 × 7 = **14 lider-günü** gerekiyor |
| eldeki | 2 lider × 6 gün (`HAFTA_TATILI`) = **12 lider-günü** |

Gereklilik değil **ölçek** imkânsızdı: %8 lider oranı 500 kişide 21/15/6 ediyor,
0.1 ölçekte 2/2/**0**.

⚠ **Yalnız sayıyı 4'e çıkarmak yetmedi** — 323 saniye sonra yine çözümsüz.
Promosyon yarı zamanlıya ya da izinliye denk gelince tutmuyor. Taban *"4 kişi"*
değil, **"gündüz vardiyası yazılabilecek 4 kişi"**: tam zamanlı, aktif, izinsiz.
O hâliyle **79 saniyede** çözüldü.

**Konulan:** üreticide ekip başına 4 lider tabanı. Tam ölçekte hiçbir şey
değişmiyor; 0.1 ölçekte 5/5/4.

⚠ **Küçük ölçekte oranı bozuyor:** 7 kişilik ekipte 4 lider. Gerçekçi değil —
ama 7 kişiyle 7/24 kapsama da gerçekçi değil. Alternatifi, firmanın kendi
kuralını tutamayan bir veri seti olurdu. Problemi daraltmak yerine ölçeğin
kendi sınırını yazıya geçirdim.

⚠ **Tam ölçekte gereklilik ÖLÇÜLMEDİ.** 0.1'de çözülüyor; 500 kişide sayı
elverişli görünüyor ama koşulmadı.

## Gün sonu — akşam

| ne | sayı |
|---|---|
| Motor birim testi | **202** yeşil (2 dk 22 sn) |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 fikstür tutarlı |
| Zor veri seti bekçisi | **12** yeşil (~6 dk) |
| İhlal vakaları | 28 gövde · 28 vaka · 28 kırmızı · eksik sıfır |
| Yazılı kural gövdesi | **28** / katalog 40 |

**Bugün kapanan:** T-64 · T-61 (K-41) · T-62 · T-63'ün rol tarafı
**Bugün karara bağlanan:** K-41
**Açık 🔴:** sekiz

## Sırada

1. **Şartname §6.4'ün iki satırı** — K-41 ile güncellenmeli (yazı borcu).
2. **T-63'ün yetkinlik tarafı** ve `SAHADA_ASGARI`'nin tabanı — Mustafa'nın kararı.
3. **Tam ölçekte gündüz lider gerekliliği** ölçülmeli.
4. Kalan **12 gövde**. Mantıklı grup: üç yasal kural (gece vardiyası azami,
   gece postası devri, yıllık fazla mesai tavanı).
5. T-59 (süre bütçesi aşımı) ve T-60'ın dört ölçümü.

---

# GECE · CI kırmızı yandı — ve sebebi planda değil ölçümde

Mustafa'nın koşumu:

```
sert_ihlal: 0   ·   asgari_kapsama_yuzde: 99.76
```

Çelişki gibi duruyor: `ASGARI_KAPSAMA` SERT, ihlal yoksa kapsama %100 olmalı.
Çelişki değil — **iki sayının ikisi de motorun kendi raporundan geliyor.**

## 9 · T-65 · Kesirli vardiya bitişi metrikte kırpılıyordu

`coz.py::_metrikler` kapsamayı `range(... int(a["bas"]), ... int(a["bit"]))`
ile sayıyordu. Vardiya 07:00–16:15 ise `int(16.25)` = 16 ve saat 16 **dışarıda**
kalıyor — oysa vardiya 16:00–16:15 arası sahada ve kısıt tarafı o çeyreği
sayıyor. **Kısıt sağlanmış, metrik "kapanmadı" diyor.**

K-34 çeyrek ızgarasından beri şablonların çoğu kesirli bitiyor (16.25, 18.75,
20.25…), yani bu kırpma istisna değil kural. 415 hücrenin **biri** eksik
sayıldı: 414/415 = %99,76.

⚠ **T-58 ile aynı aile, ve aynı hata iki yerde duruyordu.** 29 Eylül'de aynı
`int()` varsayımı doğrulayıcıyı çökertmişti ve orada düzeltildi. Çözücüdeki
**kopyasına kimse bakmadı.** Şartname §7.6 iki tarafı bilerek ayırıyor; bedeli
de bu: bir hatayı bulmak, onu **iki yerde** aramak demek. Bunu dün de yaşadık
(K-38 çözücüde düzeltildi, doğrulayıcıda değil).

⚠ **Test rastgele yeşil yanıyordu.** Hangi hücrenin açıkta kalacağı **plana**
bağlı: benim koşumda her hücreyi `int(bit)`'i o saati hâlâ kapsayan biri
örtüyordu, CI'nın 2 çekirdekli makinesinde çözücü başka bir plan buldu.
Bulunması Mustafa'nın koşumuna kaldı — bir test yeşil yandığında bunun
tesadüf olup olmadığını sormak gerekiyor.

**Düzeltildi.** Üç test, ikisi kırmızı başladı; mutasyon (`int()` geri kondu)
ikisini birden öldürdü.

**Bekçi de değişti:** `test_KUCULTULMUS_olcekte_kapsama_TAM` artık motorun
kendi sayısına değil **doğrulayıcının** sayısına bakıyor ve ayrıca ikisinin
**anlaştığını** sınıyor. Komşu test bu dersi zaten öğrenmişti
(*"çözücünün kendi ölçüsüyle bakmak kendi işini kendi onaylamak olurdu"*);
burada atlanmıştı.

## 10 · T-66 · `sert_ihlal` ölçülmüyor, sabit yazılıyor

Aynı fonksiyonun yanındaki satır:

```python
"sert_ihlal": 0,   # kisitlar sert; cozum varsa hepsi saglanmistir
```

Cümle mantık olarak doğru, ama alan adı bir **ölçüm** vaat ediyor. İki sınırı
var: yalnız motorun **kendi kurduğu** kısıtları kapsar (gövdesi yazılmamış 12
kural o sıfıra girmez), ve *"ihlal yok"* değil *"kendi kısıtlarımı çiğnemedim"*
demek. T-65'in yanıltıcı çifti tam bu yüzden mümkün oldu.

§11.3 çıktı sözleşmesi Mustafa'nın kararını bekliyor: alan kaldırılsın mı, adı
değişsin mi, yanına *"ölçülmedi"* diyen bir kardeş alan mı gelsin.

## Gece sonu

| ne | sayı |
|---|---|
| Motor birim testi | **205** yeşil (2 dk 06 sn) |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 fikstür tutarlı |
| Zor veri seti bekçisi | **12** yeşil (6 dk 25 sn) |
| İhlal vakaları | 28 gövde · 28 vaka · 28 kırmızı · eksik sıfır |
| `DENETIM.py` | 0 hata |

**Bugün kapanan:** T-64 · T-61 (K-41) · T-62 · T-65 · T-63'ün rol tarafı
**Bugün açılan:** T-61 · T-62 · T-63 · T-64 · T-65 · T-66
**Karara bağlanan:** K-41
**Açık 🔴:** sekiz

⚠ **Günün toplamı:** bağımsız denetim iki kural için ilk kez var oldu ve
**altı bulgu** açtı; beşi aynı gün kapandı. Beşinin üçü *ölçüm aracının kendi
boşluğuydu* — ihlal vakası aracı kendi listesini sayıyordu, motorun metriği
kesirli sınırı kırpıyordu, `sert_ihlal` hiç sayılmıyordu. **Ölçen aracın da
bekçisi olmalı.**

---

# GECE (2) · Yasal gece sınırı — `GECE_VARDIYASI_AZAMI`

## 11 · Önce kendi sözümü düzelttim

Dün *"mantıklı grup üç yasal kural"* demiştim. Kalan 12 gövdesiz kural tek tek
okununca yanlış çıktı:

| durum | kaç | hangileri |
|---|---|---|
| bugün yazılabilir | 5 | asgari vardiya süresi · ardışık gece limiti · çalışma saatleri · ekip sürekliliği · vardiya rotasyon yönü |
| yeni girdi alanı istiyor | 1 | **gece vardiyası azami** (yasal) |
| geçmiş hafta/yıl verisine bağlı (T-28) | 4 | ardışık hafta sonu · **gece postası devri** (yasal) · **yıllık fazla mesai** (yasal) · plan kararlılığı |
| `tercihler` alanına bağlı (T-40) | 1 | tercih karşılama |
| **zaten ihlal üretmez** | 1 | gece yarısını aşan — şartname *"hesaplama kuralı"* diyor (T-67) |

Üç yasal kuralın ikisi T-28'in arkasındaymış. Mustafa yazılabilir olan yasal
kuralı seçti.

## 12 · Kural ve istisnası

İş K. md. 69: gece çalışması 7,5 saati geçemez. 6645 sayılı Kanun istisna
getirdi — turizm, özel güvenlik, sağlık, petrolde **yazılı onayla** aşılabilir.

| karar | neden |
|---|---|
| ölçü **net** | `GUNLUK_AZAMI` ile aynı gelenek; penceredeki mola düşülür, dışındaki düşülmez |
| tam 7,5 ihlal değil | kanun *"geçemez"* diyor |
| pencere gün sınırını aşar (Z-5) | 19:00–05:00'in gecesi 9 saat — takvim gününe bakan govde 4 görür ve kaçırır |
| istisna **kişi bazlı** | aynı firmada aynı vardiyada onaylı muaf, onaysız değil — K-24'ün üçüncü biçimi |
| tarihli onay + hafta tarihi yok → geçersiz | yasal bir sınırı doğrulanamayan istisna açmamalı; tarihsiz onay süresizdir |

İki yeni girdi alanı: kökte `sektor`, çalışan kartında `gece_calisma_onayi`.

**Kırmızı kanıt:** 15 doğrulayıcı testi yazıldı, **9'u** kırmızı yandı. ⚠ Altısı
kural yokken de yeşildi (*"ihlal yok"* diyenler) — bu oturumdaki aynı tuzak,
kayda geçiyor.

**Mutasyon:** doğrulayıcıda sekiz bozma (brüt ölç · bütün molaları düş · Z-5'i
kaldır · istisnayı kaldır · yalnız sektöre bak · yalnız onaya bak · sınırda
eşitlik · süresi geçmiş onay) — **sekizi de öldü.** Çözücüde üç — **üçü de
öldü.**

## 13 · Çözücü bilerek daha katı — T-68

Doğrulayıcı **net** ölçüyor; çözücü şablonun penceresine düşen **brüt** saate
bakıyor. Net ölçü molanın yerine bağlı ve mola yeri bir karar değişkeni —
onu kısıtlamak 500 kişide on binlerce terim demek, T-60'a göre model zaten
zorlanıyor. Bedeli: çözücü yasal bir planı **reddedebilir** ama yasadışı plan
**üretmez**. Olduğunda not yazıyor. Bugün etkisi yok.

Çözücü testleri T-62'nin dersiyle kuruldu: talep öyle konuyor ki onu **yalnız**
yasak şablon karşılayabiliyor — kısıt yazılıysa plan çözümsüz kalmak zorunda.
*"Doğru şablonu seçti mi"* sorusu bu motorda tesadüfe açık.

## 14 · Veri seti kuralı zorlamıyor — açıkça

En uzun gece örtüşmesi S-GECE'de **7,00 saat**, sınır 7,5. Kural tanımlı ve
aktif ama şablonlar onu zorlamıyor; zorlayan testler ve ihlal vakası.
Şablonları sınırın üstüne çıkarmak **yasadışı bir firma kurmak** olurdu.
Sahnenin sektörü bilerek **istisna dışı** (çağrı merkezi) — sınır herkese.

## Gece (2) sonu

| ne | sayı |
|---|---|
| Motor birim testi | **225** yeşil (2 dk 06 sn) |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 tutarlı |
| Zor veri seti bekçisi | **12** yeşil (**6 dk 57 sn**) |
| İhlal vakaları | **29 gövde · 29 vaka · 29 kırmızı** · eksik sıfır |
| Gövdesiz | 11 — biri bilerek (T-67), gerçek eksik **10** |

⚠ **İzlenecek: bekçilerin süresi büyüyor.** Bugün sabah 4 dk 31 sn, şimdi
6 dk 57 sn. Her kural modele yük ekliyor. CI'da `motor` işinin sınırı 20 dakika
ve CI 2 çekirdekli. Kırmızı yanarsa önce **hangi adımda** ve **süre sınırından
mı** diye bakılmalı — bütçe aşımı kırmızısı gerçek hataya benziyor.

**Sırada:** beş firma kuralı (karar gerektirmiyor) · T-28 (geçmiş veri —
Mustafa'nın kararı, iki yasal kuralın önkoşulu) · T-66 (`sert_ihlal` — §11.3)
· T-63'ün yetkinlik tarafı · T-67 (`GECE_YARISI_ASAN` sınıflandırması) ·
T-59/T-60.

---

# GECE (3) · İki firma sınırı · ve geçmiş veri için Mustafa'nın önerisi

## 15 · Sınıflandırmamı bir kez daha düzelttim

*"Karar gerektirmeyen beş firma kuralı"* demiştim. Şartnameye bakınca yalnız
**ikisi** öyle çıktı:

| kural | neden karar istiyor |
|---|---|
| çalışma saatleri | departmanın açılış/kapanış saati veritabanı şemasında var (`departments.acilis_saat`), **motorun girdisinde yok** (§11.2) |
| ekip sürekliliği | *"aynı kişiler aynı ekiple"* iki türlü okunuyor; 500 kişinin hepsi tek ekipte, *"aynı ekip"* okuması boş kalır |
| vardiya rotasyon yönü | anlamı net ama çözücüde yüz binlerce kısıt demek; T-60 açıkken model ağırlaşır |

Bugün üçüncü kez aynı hata: sınıflandırmayı **okumadan** yaptım.

## 16 · Asgari vardiya süresi · ardışık gece limiti

**Asgari süre — ölçü brüt, bilerek.** Kaygı çalışanın kısa bir iş için yola
çıkması. Ölçüldü: net ölçülseydi firmanın kendi 4 saatlik şablonları (09–13,
17–21) kendi 4 saat kuralını her kullanımda çiğneyecekti — ekip mola politikası
4 saatlik vardiyaya 1,25–1,5 saat mola yazıyor.

⚠ **Yan gözlem:** 4 saatlik vardiyaya 1,5 saat mola veri setinin bir
yapaylığı — mola politikası ekip bazında, vardiya uzunluğuna bakmıyor.

**Ardışık gece — gece = K-40'ın işareti**, arada gündüz vardiyası seriyi kırar,
yalnız plan haftası (T-28).

**Bu kez testler gövdeden önce yazıldı:** 17 test, **10 gerçek kırmızı** (üç
çözücü testi dahil); yedisi kural yokken de yeşildi. **Sekiz mutasyon, sekizi de
öldü.**

**Veri setinde:** asgari süre ısırmıyor (en kısa şablon tam 4 saat); ardışık
gece **ısırabilir** (B-AKSAM gece işaretli) — küçük ölçekte plan yine temiz.

## 17 · Mustafa'nın önerisi — geçmiş veri nasıl test edilir

> *"Geçmiş datayı test etmek amaçlı test planını iki aşamalı yaparsak… önce 1
>  hafta sonrasını ve ondan sonra diğer haftayı… Veya bir PDKS verisi üretiriz,
>  plana %80-85 uyumlu olarak gerçekleşmiş, ve bunun üzerine yeni bir plan
>  yaparız."*

Ve bir ürün cümlesi: *"Realitede geçmiş datayı PDKS v.b. sistemlerden alacağız,
plan datası olmayacak."*

⚠ **Gerçek veri önerinin ikinci yolunu değiştiriyor** (P-1): kayıtların yalnız
**%18'i** dolu, 781 kişinin **411'inde** hiç kayıt yok. Baskın sorun sapma değil
**eksik kayıt**. Ve şartname *"lookback eksikse motor çalışmaz"* diyor — gerçek
PDKS'le bu kural motoru çoğu koşumda durdurur.

Değerlendirme ve öneri Mustafa'ya yazıldı; karar bekleniyor.

| ne | sayı |
|---|---|
| Motor birim testi | **242** yeşil |
| Zor veri seti bekçisi | 12 yeşil (5 dk 54 sn) |
| İhlal vakaları | **31 gövde · 31 vaka · 31 kırmızı** |
| Gövdesiz | **9** — biri bilerek (T-67) |

---

# ÖĞLEDEN SONRA · T-28 kapandı — geçmiş veri

## 18 · İki karar (K-42)

1. Geçmiş veri yoksa motor **durmaz**; geçmişe dayanan ölçütler atlanır.
   Mustafa: *"Geçmiş veri yoksa adalet kavramı gibi geçmiş veriye dayanan
   kriterleri dikkate almadan ilerlemek."*
2. **Yasal kurallar dahil** — ayrıca soruldu; seçilen *"atlansın,
   raporlansın"*. Motor o kişi için hafta sınırında yasal garanti vermez,
   çıktı bunu kişi ve kural adıyla söyler.

Şartnamenin *"lookback eksikse motor çalışmaz"* kuralının yerine geçiyor:
gerçek veride kayıtların yalnız %18'i dolu (P-1), o kural motoru çoğu koşumda
durdururdu.

## 19 · Temel ilke ve rapor

**Kayıtlı aralık çalışıldığını kanıtlar; kaydın yokluğu hiçbir şey
kanıtlamaz.** Bilinmeyen gün kısıt yaratmaz. `gecmis_eksik` kanalı yalnız
**sonucu değiştirebilecek** bilinmeyen günü yazar — pazartesi boşsa, bilinen
boş gün seriyi kırıyorsa ya da ihlal zaten kanıtlıysa satır yok. Gerçek veride
her pazartesi çalışanı için dört satır yazan bir kanal okunmaz olurdu.

## 20 · Ölçüm — Mustafa'nın iki aşamalı yolu

| hafta 2 | atama | geçmişi bilen denetçiye göre sert ihlal |
|---|---|---|
| geçmişsiz | 217 | **27** (10 hafta tatili · 7 dinlenme · 10 ardışık gün) |
| geçmişle | 217 | **0** |

49 kişilik tek bir hafta. 27 yasal ihlal ve **hiçbiri görünmüyordu** — eski
denetçi de geçmişe bakmıyordu.

## 21 · Üç tuzak, üçü de yakalandı

**1 · İki aşamalı testin ilk hâli hiçbir şey ölçmüyordu.** *"Hafta 2 geçmişle
temiz mi"* diye soruyordu; çözücü geçmişi **hiç okumayacak** şekilde
bozuldu, test yine yeşil kaldı — sahnede boşluk çoktu. Bu kez mutasyonu
koşmadan önce **sordum**. Sabit atamalı deterministik sahneyle yeniden
yazıldı: geçmiş okunuyorsa plan çözümsüz kalmak zorunda.

**2 · Gerçek ölçekli iki hafta testi CI'da zamanlamadan kırmızı yandı.** Aynı
hafta 144 ve 178 sn sürdü, bekçide 240 sn'ye sığmadı; bekçileri 9,5 dakikaya
çıkardı. Elle koşulan araca taşındı.

**3 · T-70 — mutasyonlar eski bytecode ile koşabiliyordu.** Diskteki kod
doğruydu, Python on ikinci mutasyonun derlenmiş hâlini çalıştırıyordu (aynı
uzunlukta değişiklik, aynı saniyede geri yazma). Bu oturumdaki **bütün**
mutasyon sonuçlarını şüpheli yapıyordu. `mutasyon_kostur.py` yazıldı ve
**42 mutasyon yeniden koşuldu: hepsi öldü.** Önceki sonuçlar geçerliydi.

## 22 · T-69 — iki taraf aynı hatayı yapıyor

İşaretsiz 00:00–08:45 vardiyası iki motor yarısında da **gece sayılmıyor**;
ikisi tutarlı, ikisi yanlış. Bugün veri setinde etkisi yok (şablonlar
işaretli), ama PDKS kaydının işareti olmayacak.

## Öğleden sonra sonu

| ne | sayı |
|---|---|
| Motor birim testi | **274** yeşil |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 tutarlı |
| Zor veri seti bekçisi | 12 yeşil (7 dk 11 sn) |
| İhlal vakaları | 31 gövde · 31 vaka · 31 kırmızı |
| Mutasyonlar | **42 · hepsi öldü · atlanan yok** |
| Açık 🔴 | **yedi** |

**Sırada:** gece postası devri (yasal) ve ardışık hafta sonu limiti — geçmiş
okunduğu için artık yazılabilir · T-69 (erken saatli gece tespiti) · sahte
PDKS (Mustafa'nın ikinci yolu; oranlar anonim gerçek veriden ölçülerek) ·
T-66 · T-59/T-60.


---

# Akşam · Mustafa dışarıda — soru sormadan ilerleme

Mustafa T-28'in CI koşusunu yeşil görüp *"yeşil devam"* dedi; biraz sonra:
*"Ben şimdi 2 saatliğine dışarı çıkıyorum, ben yokken benden cevap beklemeden
yapabileceklerini ilerletip, geldiğimde test v.s neyse devam edelim."*
Karar gerektiren her şey bölüm 29'da biriktirildi.

## 23 · Gece postası devri ve ardışık hafta sonu limiti — iki tarafta

Geçmiş okunduğu için (T-28) ikisi de yazılabilir olmuştu. **Testler gövdeden
önce:** 56 test, **27'si gerçekten kırmızı** başladı (yedisi çözücüde). Kalan
29 test *"ihlal yok / çözülür"* diyen testlerdi — gövdesiz de yeşildiler;
değerleri mutasyonda ortaya çıkar (bozulan bir gövde fazladan yasak koyarsa
onlar yakalar).

Üç tanım, üçü de açıkça yazıldı:

| | uygulanan |
|---|---|
| hafta | plan haftası; gün −1…−7 geçen hafta. Taban bölme — `int(gün / 7)` geçen pazarı bu haftaya koyar (mutasyonla sınandı, öldü) |
| hafta sonu çalıştı | cumartesi **ya da** pazar **başlayan** vardiya. Cuma gecesi cumartesiye taşsa da sayılmaz — **seçim**, adaletin hafta sonu boyutuyla aynı |
| bilinmeyen hafta | kısıt yaratmaz (K-42); rapor yalnız sonucu değiştirebilecekse |

`ARDISIK_HAFTA_SONU_LIMIT` veri setinde *"kabul edilemez"* tanımlıydı; şartname
§6.5 **kabul edilebilir** diyor — düzeltildi.

## 24 · Yönetmeliğin tam metni — iki fıkra şartnamede yoktu

Şartnamede md. 8'in yalnız 1. fıkrasının bir parçası alıntılanmıştı. Tam
metin okundu (Lexpera konsolide metni; RG 07.04.2004/25426, son değişiklik
29.06.2024):

> *md. 8/3: "...gece ve gündüz postalarında iki haftalık nöbetleşme esası da
> uygulanabilir."* → parametrenin 2 değeri yasal; ama anlamı ve üst sınırı
> açık (**T-73**).
>
> *md. 7/2: "Çalışma süresinin yarısından çoğu gece dönemine rastlayan bir
> postanın çalışması, gece çalışması sayılır."*

**İlk yazımda gece = K-40 işaretiydi** (ardışık gece limitindeki gibi). md. 7/2
okununca değişti: yasal kuralda firma işareti iki yönde de bozar —
22:00–06:00'yı *"gece değil"* işaretleyen firma yasadan kaçar (K-18);
15:15–24:00'ü *"gece"* işaretleyen firmanın yasal olarak serbest planı kabul
edilemez bir ihlalle kilitlenir (K-20). Veri setinde B-AKSAM tam bu ikinci
durum: işaretli ama 8,75 saatin 4'ü gece döneminde — yasal kural onu **saymıyor**.
Firma kuralları (ardışık gece, gece uygunluğu, adalet) işareti kullanmaya
devam ediyor.

Aynı okumada **T-74** 🔴 çıktı (bölüm 27).

## 25 · Ölçüm — iki aşamalı yol, yeni kurallarla

49 kişi, %95 doluluk. Hafta 1'in planı hafta 2'nin geçmişi:

| hafta 2 | durum | atama | geçmişi bilen denetçiye göre sert ihlal |
|---|---|---|---|
| geçmişsiz | çözüldü | 215 | **30** — gece postası devri **11** · hafta tatili 7 · ardışık gün 7 · dinlenme 5 |
| geçmişle | **çözüldü** | 214 | **0** |

En sıkı okuma bu ölçekte **çözülebiliyor**. Geçmiş okunmasaydı 11 kişi iki
hafta üst üste gece çalışıyordu.

⚠ Öğleden sonraki ölçümde bu satır **27** idi; fark yeni kuralın kendisi
(gece postası devri 11) ve çözücünün her koşuda farklı plan üretmesi.

`gecmis_eksik` her iki koşuda **30** satır — iki haftalık ölçümde hafta −2
bilinmiyor; ardışık hafta sonu limiti iki önceki hafta sonunu istiyor.
**Üç haftalık ölçüm** bunun için eklendi (`--uc-hafta`, bölüm 30).

## 26 · T-69 ve T-71 kapandı — işaretsiz tahmin yönetmeliğe bağlandı

**T-69:** işaret yoksa iki taraf da yalnız **aynı günün** 20:00–06:00
penceresine *"en ufak değme"* arıyordu. İki yönde yanlıştı: 00:00–08:45 gece
**değil**, 13:00–21:00 **gece** sayılıyordu. Gece çalışamayan birine 13:00–21:00
verilemiyordu; PDKS'ten gelen işaretsiz 00:00–08:00 kaydı ardışık geceye
girmiyordu. **Yeni tahmin md. 7/2** — yasal kuralla aynı ölçü.

**T-71:** doğrulayıcıda adaletin *"gece"* boyutu işareti **hiç okumuyordu**;
K-40'ın *"iki yerde iki gece tanımı kalmadı"* cümlesi yalnız çözücü için
doğruydu. Artık iki tarafta aynı.

14 test, 8'i gerçek kırmızı. ⚠ **Mutasyon bir boşluk daha yakaladı:** adaletin
işareti okuduğunu sınayan ilk testim 13:45–23:00 ile kurulmuştu; yeni tahmin onu
zaten gece saymadığı için işareti **hiç okumayan** gövde de geçiyordu. İşaretle
tahminin **ayrıştığı** iki vardiya eklendi (22:00–06:00 *"gece değil"*,
15:15–24:00 *"gece"*); mutasyon öldü.

**Yan etki, açıkça:** beş eski testin sahnesi işaretsiz şablonlarla kuruluydu.

| test | ne oldu | ne yapıldı |
|---|---|---|
| durgunluk | sahnenin zorluğu adaletin gece teriminden geliyordu; yeni tahminle kolaylaştı, çözücü optimumu **kanıtladı** ve test *"durgunluk"* yerine *"hedef boşluk"* gördü — **kırmızı yandı** | eski tahminin sonucu şablona **açıkça işaret** olarak yazıldı; model eskisiyle aynı |
| iki aşama · iyileştir · süre yetmedi | yeşil kaldılar — ama sahneleri sessizce değişmişti | aynı işaret; model eskisiyle aynı |
| gece penceresinin sınırı (16 Eylül) | 18:00–21:00'ün gece sayılmasını çiviliyordu; yeni tanımla 1/3 gece, sayılmaz | vaka 19:00–23:00 oldu — testin amacı (pencere 20'de mi başlıyor) aynı kaldı |

⚠ Üç testin yeşil kalması **bir şey kanıtlamıyordu**: sahneleri değişmişti ve
ben bunu yalnız kırmızı yanan dördüncüsü yüzünden aradım.

## 27 · T-74 🔴 — yasal gece sınırının ölçüsü yönetmelikle aynı değil

Bizim kural *"gece penceresine düşen net çalışma 7,5 saati geçemez"* diye ölçüyor.
md. 7/1–7/2'nin okuması: vardiyanın yarısından çoğu gecedeyse **bütün**
çalışma süresi gece çalışmasıdır ve 7,5 saati geçemez. 22:00–08:00 (1 saat
mola): bizde 7 saat, yasal; yönetmelikte 9 saat, **yasa dışı**. Tek gerçek
müşterinin verisinde 16:00–01:00 deseni **82 kez** var.

**Bilerek değiştirmedim:** şartnamenin kural tanımı değişir, hukuk teyidi (A-16)
gerekir. Uygulaması küçük — *"gece postası mı"* tespiti bugün iki tarafta da
yazıldı.

## 28 · Veri notu — anonim veri klasörü boş

Sahte PDKS için oranları *"anonim gerçek veriden ölçerek"* kuracağımı
yazmıştım. `06-veri/anonim/` **boş**; `06-veri/ham/`'a bakılmadı ve
bakılmayacak. Elde yalnız belgelenmiş türetilmiş istatistikler var
(`07-GERCEK-VERI-BULGULARI.md`: kayıtların %18'i dolu, çağrı merkezinde %46;
gece yarısını aşan 182 vardiyanın desen tablosu). Sahte PDKS bunlarla ve
Mustafa'nın *"plana %80-85 uyumlu"* cümlesiyle kurulacak; geri kalan her
oran **varsayım** olarak yazılacak.

## 29 · Mustafa'yı bekleyen kararlar

| # | soru | neden önemli |
|---|---|---|
| 1 | **T-74** · Yasal gece sınırı: pencereye düşen kısım mı (bugünkü), gece postasının bütün süresi mi (md. 7/2)? | Yanlış yönde hata — yasa dışı planı yasal gösterebilir. Gerçek müşteride 82 vardiya |
| 1b | **T-75** · *"Hafta sonu çalıştı"* = bir günü yeter mi (bugünkü) yoksa **iki günü de** mi? Ya da motor gelecek haftayı mı gözetsin? | Bugünkü tanımla üçüncü hafta **iki koşuda da çözümsüz** (bölüm 30) |
| 2 | **T-72** · Haftada tek gece o haftayı gece haftası yapar mı (bugünkü) yoksa bir eşik mi? | Yasal kural; 49 kişide çözülebilir ölçüldü, gerçek müşteride ölçülemedi |
| 3 | **T-72** · Yasal kuralda gece: yönetmeliğin tanımı (bugünkü) mı, firma işareti mi? | İşaret yasal kuralı iki yönde bozabiliyor |
| 4 | **T-73** · İki haftalık nöbetleşmede 2 değeri gece-gece-gündüz-gündüz mü; üst sınır 2 mi? | Bugün varsayılan 1, etkisi yok |
| 5 | Cuma gecesi cumartesiye taşan vardiya hafta sonu sayılsın mı? (bugün: sayılmıyor) | Firma kuralı; seçim açıkça yazıldı |
| 6 | İşaretsiz vardiyanın tahmini artık md. 7/2 (T-69) — onay | Veri setinde etkisi yok |

Önceden bekleyenler: T-66 (§11.3 `sert_ihlal`) · T-63 (yetkinlik gerekliliği,
`SAHADA_ASGARI` tabanı) · T-54 · T-18 · T-38 · T-29 · T-21.

## 30 · Üç hafta — ardışık hafta sonu limiti tam veriyle, ve üçüncü hafta kilitlendi (T-75)

İki haftalık ölçümde hafta −2 bilinmiyordu; ardışık hafta sonu limiti (azami
2) iki önceki hafta sonunu istediği için K-42 gereği atlanıyordu (`gecmis_eksik`
satırlarının **hepsi** bu kuraldı). Araca `--uc-hafta` eklendi: üçüncü hafta iki
haftalık geçmişle çözülüyor. **İki bağımsız koşu:**

| | koşu 1 | koşu 2 |
|---|---|---|
| hafta 2 geçmişle | çözüldü · 0 ihlal | çözüldü · 0 ihlal |
| hafta 3 geçmişsiz | çözüldü · **61** sert ihlal (26'sı üçüncü ardışık hafta sonu, 6'sı gece postası devri) | — |
| hafta 3 geçmişle | **çözümsüz** | **çözümsüz** |
| … hafta sonu limiti kaldırılınca | | **çözüldü** (172 sn) |
| … gece postası devri kaldırılınca | | yine **çözümsüz** |
| … ikisi de kaldırılınca | | çözüldü (259 sn) |

**Sebep:** 6 günlük desende tek izin günü var; cumartesi ya da pazardan biri
**mutlaka** çalışılıyor. Bugünkü tanımla (*bir gün yeter*) herkes her hafta
sonu *"çalışmış"*. Hafta 1 ve 2'yi çözen motor gelecek haftayı görmüyor: 45
aktif kişinin **29'u** iki hafta sonu da çalıştı, satışta 25'in 18'i. Hafta 3'te
satışın 7/24 hafta sonunu kalan 7 kişi karşılayamıyor.

⚠ **Çözücünün kendi teşhisi boş döndü (T-76):** *"engelleyen kural: yok"*.
Her kuralı 10 saniyeyle deniyor; bu ölçekte yetmiyor. Kullanıcı sebepsiz bir
*"çözümsüz"* görürdü. Sebebi ancak kuralları **tam bütçeyle** tek tek kaldıran
deney buldu.

⚠ Araç adaletin devir yükünü haftadan haftaya taşımıyor — açıkça yazıldı (T-75).

## 31 · T-59 düzeltildi — süre bütçesi artık aşılmıyor (karar gerektirmiyordu)

Birinci aşama bütçenin **içinden** pay alıyor: `min(ilk_asama_saniye,
azami_saniye × %20)`; ana çözüme **kalan** veriliyor. Model kurma ayrı kalem
olarak çıktıda. Durma sebebi kıyası da ana aşamanın payına bağlandı. 6 test,
altısı kırmızı başladı; 4 mutasyon öldü. **Testler saat ölçmüyor** — CI yükünde
rastgele kırmızı yanmasınlar diye bütçenin **bölünüşü** sınanıyor.

⚠ **Tam ölçekte yeniden ölçülmedi** — 900 saniyelik koşu Mustafa'nın
makinesinde yapılmalı (`py coz-olc.py --saniye 900`); araç artık üç kalemi de
yazıyor. Ölçülene kadar 🟡.

## 32 · Sahte PDKS — Mustafa'nın ikinci yolu (T-77)

`sahte_pdks.py`: hafta 1'in planından *"plana %80-85 uyumlu"* gerçekleşme
(%82,5 aynen · %5 gelmedi · kalanı 15–60 dk geç giriş/çıkış · %3 çağrılma) ve
**eksik kayıt** üretir (%30 kişinin hiç kaydı yok, kalanlarda günlerin %66'sı
okutulmuş). Bilinen gün = kaydı olan gün (K-42). Hafta 2 bu eksik geçmişle
planlanır, sonra plan **gerçek** geçmişe göre denetlenir.

| | sayı |
|---|---|
| PDKS'in yakaladığı | gerçekleşen 209 vardiyanın **119'u (%57)**; çalışan 8 kişinin hiç kaydı yok |
| eksik geçmişle bakan denetçi | **0** sınır ihlali |
| gerçek geçmişle bakan denetçi | **7** — hafta tatili 2 · dinlenme 1 · gece postası devri 2 · ardışık gün 2 |
| `gecmis_eksik` | **141 satır** |
| raporda haberi olmadan kaçan | **0** |

**K-42'nin sözü tutuyor** — her gerçek ihlal raporda o kişi ve kural için
haber verilmiş. **Ama 141 satır**: yaklaşık 20 satırdan biri gerçek; yedinin
beşi yasal ve plan yayınlanabilir görünüyor.

Üreticinin kendi 8 testi CI'da koşuyor
(`08-motor-testleri/gercekci-veri-seti/testler/test_sahte_pdks.py`); 5
mutasyon, beşi de öldü. Oranların hangisinin ölçüm, hangisinin varsayım olduğu
dosyanın başında (bölüm 28).

## 29'a ek — iki soru daha

| # | soru | neden önemli |
|---|---|---|
| 7 | **T-77** · Geçmiş eksik raporu nasıl sunulsun (kişi başına mı, yasal olanlar önce mi)? Yayın kapısı ona bakacak mı (T-18)? | 7 gerçek ihlal için 141 satır |
| 8 | **T-59** · 900 saniyelik tam ölçek koşusu senin makinende: `py coz-olc.py --saniye 900` | Düzeltme kodda ve testte kanıtlı, tam ölçekte ölçülmedi |

## Akşam sonu

| ne | sayı |
|---|---|
| Motor birim testi | **359** yeşil (274'ten) |
| Zor veri seti bekçisi | **20** yeşil (12 + sahte PDKS üreticisi 8) · 6 dk 02 sn |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 tutarlı |
| İhlal vakaları | **33 gövde · 33 vaka · 33 kırmızı** |
| Mutasyonlar | **88 · hepsi öldü · atlanan yok** (42'den) |
| Açık 🔴 | **dokuz** — yeni: T-72, T-74, T-75 · 🟡'ye inen: T-59 |
| Kapanan | T-69, T-71 |

**Mustafa'yı bekleyen sorular:** bölüm 29 ve eki.

---

# Gece · Mustafa döndü, kararlar alındı ve uygulandı

Mustafa dokuz soruyu okudu; 1, 2, 5, 6'yı anlamadığını söyledi, açıldı.
Cevapları: hukukçu yok, yasal iki soru (1 ve 3) çevrimiçi kaynaklarla bana
bırakıldı; 2, 4, 5, 6, 7 kabul; 8'in cevabı 4'te; 9 için kod dizini verildi,
push yapıldı ve tam ölçek koşusu makinesinde başlatıldı.

## 33 · Araştırma — iki yasal soru, çevrimiçi kaynaklarla

**Yasal gece sınırı (T-74).** Yargıtay 9. HD 2016/36126 E., 2020/17967 K.
tam bizim soruyu çözüyor: 20:00–08:00 vardiyasında bilirkişi gece hesabını
06:00'da kesmiş, Yargıtay bozmuş — hesap fiili bitiş 08:00'e kadar,
*"yarısından fazlası gece dönemine denk gelince tüm çalışma gece kurallarına
tabi."* Doktrin ekliyor: bu okuma vardiyalı (postalar hâlinde) işyerleri
için; vardiyasızda yalnız 20:00 sonrası sayılır. Biz vardiya ürünüyüz.
**Karar K-44.**

**Gece haftası (T-72).** Hiçbir kaynak karma haftayı ele almıyor. Hepsi
kuralın amacını aynı cümleyle veriyor: sürekli gece çalıştırma yasağı
(Yargıtay 22. HD 2019/18396: bir ay aralıksız gece = ihlal, haklı fesih).
**Karar K-45:** yönetmeliğin tek vardiya ölçüsü haftaya uygulandı —
haftanın çalışma saatlerinin yarısından çoğu gece postasındaysa gece
haftası. Sıkı okuma ayar olarak kaldı, yalnız ekler.

Kaynaklar ve madde metinleri mevzuat araştırması bölüm 3b'ye yazıldı.

## 34 · Beş karar, iki motor yarısında (K-43…K-47)

| karar | ne değişti |
|---|---|
| **K-43** işaret tabandır | otomatik işaret yönetmelikten; firma ekler, altına inemez. ⚠ K-40'ın üç bekçi testi **tersine döndü**, gerekçesi testlerin içinde |
| **K-44** yasal gece sınırı | gece postasının bütün net süresi ≤ 7,5; pencere ölçüsü yanında (aynı geceyi paylaşan iki vardiya için) |
| **K-45** gece haftası | çoğunluk; pencere 2×azami haftada ≤ azami gece haftası; üst sınır 2, fazlası kırpılır ve bildirilir; geçmiş hafta tam bilinmeden hesaplanmaz |
| **K-46** hafta sonu | iki gün de; gün = saatlerin yarısından çoğu |
| **K-47** rapor | kişi başına özet, yasal önde; kapı engellemez |
| T-76 | teşhis üç cevap: engelliyor · engellemiyor · **belirsiz** (süre doldu) |

**Testler:** motor **406** (274 → 359 → 406). Tanımlar değiştiği için hafta
kurallarının test dosyası baştan yazıldı (80 test). **Mutasyon: 116, hepsi
öldü** — ilk turda **10 yaşadı**, hepsi test boşluğuydu:

| yaşayan | boşluk | eklenen |
|---|---|---|
| pencere ölçüsünde istisna (2) | posta ölçüsü önce ateşlediği için pencere ölçüsü hiç çalışmıyordu | aynı geceyi paylaşan iki vardiya sahnesi — pencere ölçüsünün hâlâ gerekli olduğu tek durum |
| çözücü K-44 brüt ölçsün | brüt ile net aynı sonucu veriyordu | 16:00–01:00 + 1,5 sa mola = 7,5 net → **yasal**, çözülmeli |
| geçmiş hafta vardiya sayısıyla / yarısı yeter (2) | sahnelerde saat ve sayı aynı yöndeydi | 2 uzun gece + 3 kısa gündüz; 3 gece + 3 gündüz (tam yarı) |
| en ufak taşma ertesi gün | cuma akşamı çözücü tarafında sınanmıyordu | cuma 16:00–01:00 + pazar → çözülür |
| adalet hafta sonu boyutu (2 taraf) | boyut testi yoktu | cuma gecesini cumartesi sayan adalet testi; iki tarafın sınıflaması yan yana |
| rapor: bilinmeyen yetmese de | kenar durum | azami 2, tek bilinmeyen hafta → rapor yok |

⚠ Bir tuzak daha (T-54'ün ailesi): çoğunluk-gece çözücü testinde motor
talepte olmayan bir gündüz vardiyası daha ekleyip dengeyi 24–24'e getirdi
ve *"gece haftası değil"* diye çözdü. Haftalık tavan (40 saat = beş vardiya)
altıncı vardiyayı kapatınca sahne doğru ölçtü. Karşı kanıt her sahneye
eklendi: geçmişsiz çözülür.

⚠ Karma haftalı sahnelerde gündüz ile gece arasına boş gün gerekti:
çözücü 11 saatlik dinlenmeyi kural yokken de varsayılan uyguluyor; ilk
sahne bu yüzden kendiliğinden çözümsüzdü ve hiçbir şey ölçmüyordu.

## 35 · Ölçümler — yeni tanımlarla, aynı üç haftalık yol

| | eski tanımlar (akşam) | yeni tanımlar (gece) |
|---|---|---|
| hafta 1'de gece haftası yaşayan | 11 (tek gece yeter) | **1** (çoğunluk; çözücü geceleri adaletle dağıtıyor) |
| hafta 2 geçmişsiz → kaçan sert ihlal | 30 | 24 (gece postası devri 0) |
| hafta 2 geçmişle | çözüldü, 0 | çözüldü, 0; rapor 3 satır (30'du) |
| hafta 3 geçmişsiz → kaçan sert ihlal | 61 | 36 (2 gece postası devri, 2 ardışık hafta sonu) |
| **hafta 3 geçmişle** | **çözümsüz** (iki koşu) | **çözüldü, 213 atama, 0 ihlal** — T-75 kapandı |

Rapor satırlarının 30'dan 3'e inmesi tanımdan: hafta sonu iki gün de
çalışılmadıkça geçmişin ne olduğu sonucu değiştiremez, satır yazılmaz.

**Tam ölçek (Mustafa'nın makinesi, 1.200 sn, 500 kişi):** birinci aşama 121,8
+ ana aşamaya verilen 1.078,2 = **1.200,0 sn** — T-59 kapandı. Model kurma
54,9 sn ayrı. İki yan bulgu: birinci aşama 120 saniyede geçerli plan
**bulamadı** (`iki_asama: false`, süre boşa gitti — T-60'ın konusu) ve plan
**1 sert ihlalle** döndü: yarı zamanlı tavanı, `yayınlanabilir: false`
(**T-78** 🔴). Plan kaydedilmediği için sebebi araştırılamadı; araç artık
sert ihlal cümlelerini ve planı yazıyor. Hipotez: şablona sığmayan dinlenme
molası çözücünün net saatini doğrulayıcınınkinden düşük gösteriyor (T-57
ailesi). Koşu tekrarı gerekiyor.

## 36 · Sahte PDKS — yeni tanımlarla

| | akşam | gece |
|---|---|---|
| PDKS'in yakaladığı | %57 | %46 (başka plan, aynı oranlar) |
| gerçek geçmişe göre kaçan ihlal | 7 | 9 (3 dinlenme, 2 hafta tatili, 2 ardışık gün, 2 gece postası devri) |
| rapor satırı | 141 | **106** |
| haberi olmadan kaçan | 0 | **0** |

K-42'nin sözü yeni tanımlarla da tutuyor. Rapor artık kişi başına özetle
geliyor (K-47); satırın kendisi hâlâ uzun — asıl çözüm PDKS'teki *"çalışma
günü değil"* satırlarının bilinen boş gün sayılması (açık).

## 37 · Gece sonu

| ne | sayı |
|---|---|
| Motor birim testi | **406** yeşil (akşam 359) |
| Zor veri seti bekçisi | 20 yeşil · 6 dk 10 sn |
| Altın senaryolar | 12 geçti, 4 atlandı |
| Fikstür tutarlılığı | 11 tutarlı |
| İhlal vakaları | 33 gövde · 33 vaka · 33 kırmızı |
| Mutasyonlar | **116 · hepsi öldü** (ilk turda 10 yaşadı, hepsi test boşluğu — bölüm 34) |
| Açık 🔴 | **yedi** — kapanan: T-72, T-73, T-74, T-75, T-76, T-59 · açılan: **T-78** |
| Kararlar | K-43 · K-44 · K-45 · K-46 · K-47 |

**Yazı borcu (şartname):** §6.3 gece sınırının ölçüsü (K-44), gece haftası
tanımı ve parametre üst sınırı (K-45); §6.5 hafta sonu tanımı (K-46); §8.3
gece işaretinin anlamı (K-43); §11.4 çıktıya `gecmis_eksik_ozet` ve teşhise
`belirsiz_kurallar`.

**Sırada:** T-78 (tam ölçek koşusunu tekrarla, planı oku) · T-60 (birinci
aşama 120 saniyede plan bulamıyor) · T-66 · T-63 · T-54 · T-18.

## 38 · Kapanış (1 Ekim 01:20)

DENETIM ilk koşuda 1 hata verdi: T-78 metni henüz var olmayan
*olcum-plan-95* dosyasını yol gibi anıyordu; cümle düzeltildi. Son durum:
DENETIM **0 hata / 15 uyarı**, YOL-KONTROL 8 kırık yol (hepsi eski, v1–v5
sürüm klasörleri). Gece çalışması commit edilmedi; blok sohbette, Mustafa
sabah çalıştıracak. Oturum açık — Mustafa kapatır.

## 39 · T-78 — plan beklenmeden bulundu (1 Ekim 01:30–03:15)

Mustafa üç tam ölçekli koşunun çıktısını gönderdi (900 temiz · 1.200 → 1
sert · gece commit'i sonrası 900 temiz). Sebep kuralda olsaydı her koşuda
çıkardı; çıkmadı → çözücünün **bazen** seçtiği bir yerleşim.

**Yöntem.** Planı beklemek yerine iki tarafın hesabı doğrudan karşılaştırıldı:
sahnenin 17 şablonu için çözücünün **izin verdiği her mola yerleşimi**
(yemek adayı × dinlenme adayları, çözücünün kendi çakışma kısıtıyla)
sayıldı ve her biri doğrulayıcının `zaman.net_saat`ine verildi.

| şablon | izinli yerleşim | net saat ayrışan |
|---|---|---|
| S-* (15 dk mola) | 495–4.302 | **0** |
| B-* (15 dk mola) | 35–567 | **0** |
| M-SABAH · M-AKSAM (3×20 dk) | 2.880 | **822** (810'u +5 dk, 12'si +10 dk) |
| M-UZUN | 4.860 | 567 |
| M-HSONU | 1.974 | 378 |
| M-AKSAMK | 27 | 27 |

**Sebep:** 20 dakika çeyrek ızgarada `round(1,33) = 1` çeyrek. Pencereler
o hesapla ayrılıyor, mola gerçek süresiyle uzuyor; yemek–dinlenme kısıtı
çeyrek kümesiyle bakıyor. ⚠ Gece yazdığım hipotez (sığmayan mola
üretilmiyor) **yanlıştı** — her mola sığıyordu. ⚠ Üçüncü yüz: `_mola_dilimleri`
20 dk'yı tek çeyrek kapalı sayıyordu; `SAHADA_ASGARI` sert ve sahayı çeyrek
anlarında örnekliyor — sahnede kapalı olduğu için görünmedi.

**Düzeltme** bölüm 38'in altındaki changelog kaydında; dört parça. Kanıt: 9
test, mutasyon grubu `mola_t78` (6, hepsi öldü). ⚠ İlk mutasyon turunda 4
yaşadı: ikisi test boşluğu (pencere ayrıklığı ve uç uca değen mola doğrudan
sınanmıyordu — testler yazıldı), biri **eşdeğer** mutasyon (çeyrek kümesi
yukarı yuvarlanınca çeyrek kesişimi gerçek kesişimle aynı cevabı veriyor —
listeden çıkarıldı, yerine "kısıt hiç yazılmasın" kondu), biri emniyet
kemeri (pencereler ayrıkken hiç çalışmıyor — adaylar elle bozularak sınandı).

**Taramanın açığa çıkardığı:** 3.700 şablon biçiminden 64'ünde politika
üst üste binmeden sığmıyor (≤4,75 sa vardiyaya 45–60 dk yemek + 3–4
dinlenme). 41'i eskiden de sığmıyordu; 23'ü eskiden yalnız üst üste
bindirerek "sığıyordu". Sessiz kalmasın diye nota yazılıyor.

**Doğrulama:** motor 416, bekçi 20 (7 dk 45 sn), 33 gövde · 33 vaka, sahte PDKS
14 gerçek ihlal / 109 satır / **0 habersiz** (üretici rastgele; sayılar
koşudan koşuya değişir, sıfır değişmez).

**Yan bulgular:** (1) "en fazla 900 sn" deyip 958 sn — model kurma ~55 sn
bütçenin dışında; Mustafa'ya soru (T-59, K-48 adayı). (2) Motorun
`toplam_saat`/`fazla_mesai_saat` metriği politikayı düşmüyor (T-66'ya not).
(3) Üç koşuda da `iki_asama: False`; `ilk_cozum_sn` çıktıya eklendi, sabahki
koşu T-60'ın ilk ölçümünü verir.

Mustafa yatıyor; devir dosyaları güncellendi, commit bloğu sohbette.

## 40 · Düzeltmenin bedeli ve birinci aşama (1 Ekim 13:05–14:00)

Mustafa düzeltmeyi push etti (CI yeşil), tam ölçek 900 sn: **plan yok** —
`sure_yetmedi`, 0 atama, `ilk_cozum_sn: None`. Dün aynı sahnede 654 çözüm.
Kabul: benim düzeltmemin bedeli. Model çözümsüz değil; arama ağırlaştı.

**Ölçüm (0.2 ölçek = 100 kişi, 2 çekirdek, 240 sn; eski kod dört geri
alma ile yeniden üretildi, T-78 testleri onda 8 kırmızı):**

| | eski | T-78 sonrası | + sabit mola + tam ipucu |
|---|---|---|---|
| birinci aşama | 18,3 sn ✓ | 18,2 sn ✓ | **1,7 sn** ✓ |
| ana aşamada ilk plan | 100,9 sn | 57,2 sn | **21,0 sn** |
| çözüm sayısı | 181 | 220 | 293 |

İlk iki sütun aynı: bu ölçekte T-78 düzeltmesi zarar vermiyor; sorun
ölçekle büyüyen plan bulma. Asıl bulgu üçüncü satır: ipucu **eldeyken**
ilk plan 57–101 saniyede geliyordu — ipucu yarımdı (ceza değişkenleri
yoktu). ⚠ Mutasyon koşusu ile A/B aynı anda koştu, ilk ölçümler kirlendi;
ikisini de durdurup A/B tek başına tekrarlandı; mutasyon tam koşusu
yarım kaldı (sabah).

**Değişen:** `_ipucu_ver` molaları sabitleyerek arıyor (alan [0,0]; proto
`domain.clear()/extend()` ile — `del constraints[n:]` bu OR-Tools
sürümünde desteklenmiyor, ölçüldü) ve ipucuyu `solution_hint`e tam
yazıyor. `coz(kuruldu=)` ile ölçüm betiğinin çifte model kurması bitti.
Motor 421 test, bekçi 20. Mutasyon grubu `ilk_asama` (6).

**0.3 ölçek (151 kişi, 300 sn), 05:10:** eski kod birinci aşamayı 35
sn'de geçti ama ana aşama **265 saniyede tek plan bulamadı** (0 atama) —
tam ölçeğin hastalığı burada yeniden üretildi. Yeni kod: birinci aşama
2,5 sn, ilk plan 25 sn, 306 çözüm. Yarım ipucu CP-SAT'e hiçbir şey
vermiyormuş; asıl kaldıraç ipucunun tam yazılması + sabit molalı aramaydı.

**K-48** yazıldı (sabah onayı). Devir dosyaları güncellendi; commit bloğu
sohbette. ⚠ Saat etiketi 18:15'te düzeltildi: bu bölüm 13:05–14:00 arasında
yazıldı, gece değil — koşu gece bitmiş, Mustafa sonucunu öğlen göndermişti.

## 41 · Öğleden sonra: tam ölçek sınavı geçti (1 Ekim 15:20)

Mustafa commit'i push etti (CI yeşil) ve 900 sn koşturdu: birinci aşama
**10,3 sn**, ana aşamada ilk plan **48,9 sn**, 2.476 atama, 0 sert,
yayınlanabilir, toplam 958 sn (54 kurma + 900 arama + 2 doğrulama + 2).
Plan dosyası okundu: 9.171 mola, üst üste binen sıfır; bir yarı zamanlı
tam 45,00'de, temiz. T-78 sahada kapandı; T-60'ın plan bulma yarısı
kapandı, kalite yarısı duruyor (%98,99). K-48 kesinleşmiş sayıldı
(itiraz gelmedi). Mustafa'ya iki karar soruldu: T-18 (üç kademeli kapı) ve
T-21 (şablon tek ekibe ait). Mutasyon tam koşusu bitti: **128 · hepsi öldü · atlanan 0** (15:35).

## 42 · Şartname yazı borcu ödendi (1 Ekim 15:45)

Mustafa'nın cevabı beklenirken `02-spec/v1.4-master-spec.md` güncellendi
(yerinde, tarihli eklerle — v1.4 canlı sürüm): §6.3 K-44 ve K-45 alt
bölümleri + tablo satırları; §6.4 K-41 (atanmış ölçüsü) ve T-62/T-63
notları; §6.5 K-46 alt bölümü; §8.4 `gece_vardiyasi` satırı (K-40/K-43);
§11.2 lookback kuralı K-42 ile değişti (eski cümle üstü çizili);
§11.3 süre kalemleri tablosu (K-48, `ilk_cozum_sn`, `iki_asama`,
`belirsiz_kurallar`); §11.4 çıktı kanalları tablosu; değişiklik listesine
29–35. satırlar. T-18 ve T-21 karar gelince yazılacak. DENETIM 0 hata.

## 43 · İki karar için kod hazırlandı, makineye yazılmadı (1 Ekim 15:45)

Mustafa 15:20'den beri yazmadı. T-18 (üç kademeli kapı, K-49 adayı) ve
T-21 (atama tek ekibe sayılır, K-50 adayı) için kod **oturum aynasında**
hazır, makineye **yazılmadı** — karar gelmeden davranış değiştirmemek için.
İçerik: `denetle.py` kapısı `uygulanmayan_kurallar` ve `eksik_boyutlar
[denetlenemedi]` kanallarını görüyor, kabul kaydı `girdi.denetim_disi_kabul`
(gerekçesiz kabul kabul değil; yasal kural kabulle açılamaz); `model.py`
`_atama_ekibi` (şablonun ekibi, yoksa ilk ekip) `_atanmis`/`_sahada`/
nitelik toplamında, `coz.py` çıktı ekibi, `teshis.py` ulaşılabilirlik;
22 test, 13 mutasyon hepsi öldü; motor 443, altın senaryolar 12 geçti 4
atlandı, fikstür tutarlı. ⚠ T-18 veri setindeki parametresiz
YETKINLIK_KAPSAMASI yüzünden 0.1 bekçisini ve tam ölçek planını *"kabul
bekliyor"*a düşürür; Mustafa'ya söylendi, çözüm onun seçimi (kabul kaydı
ya da T-63 parametresi). Devir dosyaları ve proje notu güncel.

## 44 · İki karar uygulandı (1 Ekim 16:00–16:45)

Mustafa: T-18 *"onaylıyorum"*; T-21 için saha örneği — çift yetenekli
eleman o saatte iki birim için yer doldurur. ⚠ Önerim tersti; geri alındı,
`"tek"` modu seçenek olarak kaldı. ⚠ Mustafa kısaltmalardan yakındı
(*"k-48 diyip bırakma"*): bundan sonra her kod cümlesiyle yazılır.

**Kapı kapanınca ne oldu:** 0.1 bekçisi kırmızı — veri setinde
YILLIK_FAZLA_MESAI_TAVANI (yasal, gövdesiz) yayını engelledi,
CALISMA_SAATLERI (sert firma, gövdesiz) kabul bekledi, GECE_YARISI_ASAN
(hesaplama kuralı) *"kontrol edilemedi"* göründü, dört yumuşak kural rapor.
Yapılan: yıllık tavanın gövdesi iki yarıda yazıldı (`yil_ici_fazla_mesai_
saat`; K-42 ile bilinmeyen atlanır), gece yarısı kuralı *"ihlal üretmez"*
diye kayıtlı + vaka aracında `IHLAL_URETMEZ`, çalışma saatleri ve yetkinlik
için veri setine gerekçeli kabul kaydı. Veri setine yıl içi toplam ayrı
tohumlu üreteçle kondu — ana üretecin sırası bozulmadı (ilk denemede
bozuldu, fark edildi, düzeltildi; NameError'lu bir koşu da sessizce
atlanmıştı — çıkış kodu okunmadan sonuç okunmaz).

**Çok ekipli:** `_sayilir` (çözücü) ve `ekibe_sayilir` (doğrulayıcı) aynı
alanı aynı varsayılanla okur; ön kontrol çift üyeli kişiyi görür; çıktı
`ekip` = vardiyanın ekibi; `baska_ekipten_kapsama` metriği.

Sayılar: motor 459, mutasyon gruplarında kapı 6/6, çok ekipli 11/11,
yıllık 9/9; vaka aracı 35 gövde · 34 vaka · 34 kırmızı · 1 bilerek vakasız.

## 45 · Dört karar daha (1 Ekim 16:56–17:27)

Mustafa'nın cevapları: 1 departman tanımı + çalışma saatleri (katılıyor);
2 her birim için İngilizce, veri seti karmaşık olsun; 3 ceza ile ilerle,
ücret hiç gelmeyebilir; 4 dondurulmuş gün — onayladı, ekiyle (geçmiş gün
yönetici bilgisiyle düzenlenebilir, gelecek günler kilitlenir, toplu seçim);
5 şartname alanlarının sırası bana bırakıldı; 6 sahte sayı kaldırılsın;
7 PDKS 00:00 — ham veriye bakmadan makinesinde çalışacak sayım betiği
yazıldı (`06-veri/pdks-gece-yarisi-kontrolu.py`), sonuç bekleniyor.
Mustafa ayrıca: 0,1 ölçek testini kabul ölçütü sayma, tam ölçek koşusuna
göre kabul edelim → sıra: koşu → sonuç → commit/push.

Yapılan: K-51 (çıktıdan `sert_ihlal` kalktı; altın senaryo testi bağımsız
denetimden okuyor), K-52 (`departmanlar[]`, `CALISMA_SAATLERI` iki yarıda,
ön kontrol, `eksik_boyutlar`; yetkinlik gereklilikleri 4 satır + taban),
K-53 (`HEDEF_ASIMI`), T-38 sırası + `sure_butcesi_sn`/`istek_id`.
⚠ İlk bekçi koşusu kırmızı: gövdesi yazılan `HEDEF_ASIMI` sahnede tanımlı
değildi — üreticiye eklendi. ⚠ Altın senaryolar 4 kırmızı: fikstürler
`metrikler.sert_ihlal` bekliyordu; test bağımsız denetimden okuyacak
şekilde değişti (fikstürlere dokunulmadı). Mutasyon gruplarında
`calisma`da 2 eşdeğer mutant çıktı: biri test boşluğuydu (kapatıldı:
tek seçenekli kapalı şablon → çözümsüz testi), biri çift koruma —
koruma tekleştirildi, mutant yeniden hedeflendi. Sayılar: motor 481,
mutasyon 166, vaka 36/36+1, bekçi 20, altın 12.

## 46 · İkinci tam ölçek koşusu (1 Ekim 17:37) — 16:45'teki kodla

Mustafa'nın koşusu (sahne 42 kurallı, yani yıllık fazla mesai toplamı ve
kabul kayıtlı 16:45 sürümü; departman saatleri ve yetkinlik gereklilikleri
henüz yok): model kurma 98,5 sn, birinci aşama 100,6 sn (öğlen 10,3),
ana aşamada ilk plan 87,8 sn (öğlen 48,9), 2.513 atama, **0 sert ihlal,
yayınlanabilir**, optimuma uzaklık %99,14, yumuşak: adalet 154 · hedef
128 · mola 62. Toplam 1.008 sn. Model kurma da iki katına çıktığı (54 →
98 sn) için makine o sırada yavaştı; birinci aşamanın 10 → 100 sn
sıçraması buna yorulabilir ama **ölçülmedi** — sonraki koşuda tekrar
bakılacak. Yayın kapısı yeni kademeleriyle (K-49) bu planı geçirdi:
yıllık tavan gövdeli, iki kabul kaydı yerinde.

Karar: 16:45 sürümü tam ölçekte kabul. 17:27 sürümü (K-51…K-53, T-38)
için koşu tekrarı gerekiyor; commit önce, push koşu sonrası.

## 47 · PDKS ham verisi incelendi — `MS 00:00` bilinen boş gün değil (1 Ekim 17:50–18:15)

Mustafa üç PDKS klasörünü (Temmuz, Ağustos, Eylül ihracatları) bağladı ve
*"ham veriye bakabilirsin"* dedi. Bakış: dosyalar makinesinde kaldı, betik
orada koştu, bana yalnız sayılar geldi; isim, sicil, firma ve bölüm adı
hiçbir çıktıya yazılmadı, hiçbir dosya buluta kopyalanmadı. Betik repoya
girdi: `07-motor/pdks-ms-gece-yarisi.py` (yalnız sayı yazar; raporu
`06-veri/` altına, git dışına bırakır).

Bulgular `07-GERCEK-VERI-BULGULARI.md` §7'de (P-2…P-5): `MS` plan değil
takvim — hafta sonu satırı kart okutulunca sonradan `00:00`→`07:30` oluyor
(1.084/1.084 kartlı; `00:00` kalan 6.014'te kart yok); gece yarısını aşan
vardiya başladığı güne tek satırda yazılıyor (1.392 satır; bölünmüş satır 0)
— motorla aynı, düzeltme yok; PDKS'in NM/EM/FM kovaları vardiyalı çalışan
için yanlış (17:46–00:01'e "eksik 9:16, fazla 5:31"), 22–23 saatlik sahte
satırlar var; izinler ve resmi tatil işareti güvenilir. 13 Eylül'deki `MS`
tablosu düzeltme notuyla işaretlendi.

Öneri Mustafa'ya yazıldı, karar bekliyor: bilinen boş gün = TShift'in kendi
plan geçmişi + PDKS izin satırları; giriş/çıkış ham saat; yıl içi fazla
mesai bordrodan. Motor kodu değişmedi.

Aynı saatlerde beş kararın commit bloğu verildi (öğleden sonraki iki kararlık
blok geçersiz sayıldı); tam ölçek koşusu 17:27 koduyla bekleniyor, push
ondan sonra.

⚠ **Saat etiketleri düzeltildi (18:15):** 40–46. bölümlerin başlıkları
yanlış saatler taşıyordu (03:40–05:00, 17:15, 17:30–19:15, 19:30–22:30,
22:50; sürümler "19:15" ve "22:40" diye anılıyordu). Gerçek saatler sohbet
kaydından alındı: 13:05–14:00, 15:45, 16:00–16:45, 16:56–17:27, 17:37;
sürümler 16:45 ve 17:27. Diğer devir dosyalarındaki aynı etiketler de
düzeltildi; gece (01:20–02:17) etiketleri doğruydu, kaldı.
