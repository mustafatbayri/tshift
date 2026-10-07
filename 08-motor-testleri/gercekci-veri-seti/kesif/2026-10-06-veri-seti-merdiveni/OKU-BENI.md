# Keşif — veri seti merdiveni: cevabı bilinen set kurulabiliyor mu? (6 Ekim 2026)

> ⚠ **Bu klasör bir KEŞİF arşividir, ölçüm aracı değildir.** Betikler tek
> oturumda yazıldı, **testleri yok**. Sayılar bulut tarafındaki 2 çekirdekli
> makinede, **49 ve 151 kişilik** küçültülmüş setlerde, 40–150 saniyelik
> bütçelerle, **tek koşu** olarak alındı. 500 kişi ve 900 sn için **tahmin
> değildir**; koşudan koşuya oynama ölçülmedi. Arşivlenme sebebi: yöntem
> tekrar denenebilsin. Merdiven kurulacaksa araç baştan, şartnameden
> okunarak ve testleriyle yazılır.

## İçindekiler

1. [Soru](#1-soru)
2. [Okunan olgular — 500 kişilik %95 seti](#2-okunan-olgular--500-kişilik-95-seti)
3. [Deneme 1 — gömülü plan: cevabı bilinen set](#3-deneme-1--gömülü-plan-cevabı-bilinen-set)
4. [Deneme 2 — zorunlu fazla mesai: x](#4-deneme-2--zorunlu-fazla-mesai-x)
5. [Bu sonuçların sınırı](#5-bu-sonuçların-sınırı)
6. [Nasıl çalıştırılır](#6-nasıl-çalıştırılır)

## 1. Soru

Mustafa, 6 Ekim 21:34: *"… öyle bir data seti verelim ki örneğin minimum x
kadar fazla mesai yapmak zorunda kalalım, x ten ne kadar uzaklaştığımıza göre
kaliteyi ölçeriz. Tabi bu x değerini tutturmak olabildiğince zor olmalı. …
Ürünün çıktısı elimizdeki tüm kriterlere bağlı olarak optimum planı
çıkarabiliyor muyuz? Amacımız fazla mesai konusunu çözmek değil sadece. Fazla
mesai 43 kriterden sadece biri bunu unutma. Amaçtan dağılma sakın."*

Mustafa, 21:36: *"Bence bundan sonrası için, birden fazla data seti ile
ilerlemeliyiz. Data setleri 5 kısım olabilir … 1- en basit data seti ve
kriter seti (500 çalışan için tabi), 2- planın optimum oluşturulması biraz
daha zor, 3 4 5 olarak zorlaşarak ilerlemeli hatta 5 seviyesinde plan
çözümsüz olabilecek kadar zor data seti olmalı? fikrime ne diyorsun ?"*

Görüş yazmadan önce iki şey denendi:

- **(a)** Bir veri setinde iyi bir planın puanı **önceden** bilinebilir mi —
  yani motorun planını "sınıra şu kadar uzak" yerine "bilinen plana şu kadar
  uzak" diye okuyabilir miyiz?
- **(b)** Fazla mesainin **zorunlu** olduğu ve en az miktarı (x) **bilinen**
  bir set kurulabilir mi; motor x'e ne kadar yaklaşıyor?

## 2. Okunan olgular — 500 kişilik %95 seti

Kaynak: `02-spec/v1.4-master-spec.md` §5.4 ve §6, `fikstur/_sahne-S30-95.json`,
`uret_veri_seti.py`, `kural-kapsamasi.py`, `kalite-olcumu-95-fmsifir-900.json`,
`09-motor/cozucu/model.py`.

| Olgu | Değer |
|---|---|
| Katalogdaki kural | **41** — 32 sert, 9 yumuşak (şartname §6 "Sayım"; fikstürde 46 satır, 41 ayrı kod) |
| Motorda ve doğrulayıcıda hiç yazılı olmayan | 4 yumuşak kural: `EKIP_SUREKLILIGI`, `PLAN_KARARLILIGI`, `TERCIH_KARSILAMA`, `VARDIYA_ROTASYON_YONU` (motorda yalnız ağırlık tablosunda adları var) |
| Plan puanını oluşturan kalemler | hedef eksiği, hedef aşımı, mola sırasında kapsama, adalet, fazla mesai cezası |
| Asgari talep | 12.723 kişi-saat — üreticinin kapasite sayısının (19.630 sözleşme saati) **%65**'i |
| Hedef talep | 18.660 kişi-saat — aynı sayının %95'i (setin adı buradan) |
| Bilinen en iyi DENGELI planı (26.407 puan) | hedefin **altında 350**, **üstünde 3.141** kişi-saat; fazla mesai 0 |
| O planın puanı nereden geliyor | adalet %47 · hedef aşımı %36 · hedef eksiği %12 · mola kapsaması %5 |
| Kanıtlı alt sınır (tam model) | 21.098 → plan sınıra en çok %20 uzak; ne kadarı motorun eksiği **bilinmiyor** |
| Geçen haftanın vardiyaları | 500 kişinin hepsinde **boş** (`gecmis_vardiyalar`). ~~Devreden adalet yükü hepsinde 0~~ — *düzeltme 7 Ekim (inceleme): üretici 500 kişinin 124'üne sıfırdan farklı `devir_yuk` yazıyor (adalet bilerek dengesiz); 6 Ekim'de tek bir kişinin satırına bakıp genellemiştim* |
| Donmuş gün · yayınlanmış plan · sabit atama | yok · yok · yok (kilit 6) |
| Ekip üyeliği | 500 kişinin hepsi **tek** ekipte (model çok ekipli kişiyi destekliyor) |
| `kural-kapsamasi.py` | 22 satır SINANDI (17 ayrı kural) · 20 TEMİZ · 4 GÖVDE YOK |

**Okuma.** Bu sette kadro yetmiyor değil; plan hedefin üstüne 3.141 kişi-saat
yazıyor. Sebebin bir kısmı birim farkı: talep *o saatte atanmış kişi* sayar
(molada olan da sayılır), sözleşme saati net çalışmadır. En iyi planda 17.592
net saat, talep hücrelerinde 21.451 kişi-saat ediyor (18.660 − 350 + 3.141)
— net saat başına ≈1,22. Tam zamanlı da sözleşme saatini doldurmak zorunda
(sert kural). Yani bu setin zorluğu **yerleştirme ve adalet**; kıtlık değil.
Üreticideki *"%95: fazla mesai ZORUNLU hale gelir"* notu ölçümle uyuşmuyor
(bulgu 20–21: fazla mesaisiz plan 9–13 sn'de bulunuyor).

⚠ `kural-kapsamasi.py` *"kaba bir plan bu kuralı çiğniyor mu"*yu ölçer;
*"kural en iyi planı kısıtlıyor mu"*yu ölçmez. TEMİZ satırlarının bir kısmı
veride karşılığı olmadığı için temiz (geçen haftanın vardiyaları boş →
ardışık gün, ardışık gece, ardışık hafta sonu, gece postası devri geçmişten
zorlanamıyor; yayınlanmış plan yok → donmuş gün zorlanamıyor).

## 3. Deneme 1 — gömülü plan: cevabı bilinen set

**Yapılan.** (1) Taban sahne üretilir (`uret_veri_seti.sahne_uret`, %95).
(2) Motor *önce fazla mesaisiz* seçeneğiyle bir plan bulur (A planı; bağımsız
doğrulayıcıda 0 sert ihlal). (3) Yeni sahne: talep tablosunun **yalnız
`hedef` sütunu** değişir — her hücrenin hedefi, A planında o hücreye atanmış
kişi sayısı olur (sayım bağımsız doğrulayıcıdan). Asgari, kişiler, şablonlar,
kurallar aynen kalır. A planı yeni sahnede hedefi **tam** tutan, fazla
mesaisiz, geçerli bir plandır; puanı bilinir (**referans**). (4) Yeni sahne
motora **sıfırdan** verilir, sonuç referansla karşılaştırılır.

Referans bir **üst sınırdır**: en iyi plan referanstan kötü olamaz, daha iyi
olabilir. Hedef eksiği, hedef aşımı ve fazla mesai için en iyi değer bilinir
(üçü de 0); adalet ve mola için referansın değeri bilinir.

| Kişi | Bütçe | A planının kaynağı | Referans | Motor · ürünün hali | Motor · *önce fazla mesaisiz* |
|---|---|---|---|---|---|
| 49 | 90 sn | varsayılan arama | 1.427 | 1.439 (+%0,8) | — |
| 49 | 90 sn | başka tohum (7) | 1.429 | **1.424** (−%0,3) | — |
| 49 | 40 sn | başka tohum (7) | 1.453 | — | 1.509 (+%3,9) |
| 151 | 125 sn | başka tohum (7) | 4.089 | **8.864** (2,17 kat) | **4.146** (+%1,4) |

151 kişide kalem kalem (ceza puanı; parantezde ham değer):

| Kalem | Referans | Ürünün hali | *Önce fazla mesaisiz* |
|---|---|---|---|
| Fazla mesai | 0 | 4.500 (1,5 saat) | 0 |
| Adalet | 3.550 | 3.535 | 3.540 |
| Mola sırasında kapsama | 539 | 574 | 546 |
| Hedef eksiği | 0 | 171 (19 kişi-saat) | 36 (4) |
| Hedef aşımı | 0 | 84 (28 kişi-saat) | 24 (8) |
| **Toplam** | **4.089** | **8.864** | **4.146** |

Hepsi 0 sert ihlal. Referansın hedefi taban sahneninkinden yüksek çıkar
(151 kişide 5.426 → 6.223 kişi-saat): A planı hedefin üstüne yazıyordu,
yeni hedef o fazlayı içerir.

**Tuzak — aynı başlangıç (ilk satır).** A planı ürünün varsayılan aramasıyla
üretilince motor yeni sahnede neredeyse aynı planı yeniden buldu (adalet ve
mola değerleri A planınınkiyle birebir aynı). Sebep: birinci aşama amaçsız
geçerli plan arar ve sert kurallar iki sahnede aynıdır; arama aynı yerden
başlar. Bu ölçü motoru kayırır. Başka tohumla üretilen A planı varsayılan
aramanın planıyla atamaların yalnız %33'ünü paylaşıyor (49 kişi: 208 atamadan
68'i). Sonraki satırlar o yüzden başka tohumla.

**Alt sınır (49 kişi, tohum 7 sahnesi).** Tek modelde ortak arama 150 sn:
küresel alt sınır **1.315**. Yani o sahnede en iyi plan 1.315 ile 1.424
arasında; motorun planı sınıra en çok %7,7 uzak (ürünün ölçüsüyle:
(plan − sınır) / plan). (Ortak aramanın kendi planı
kötüdür — 32.385, 10,25 saat fazla mesai — buradan yalnız sınır okunur.)

## 4. Deneme 2 — zorunlu fazla mesai: x

**Yapılan.** Taban sahnenin asgari talebi bütün ekiplerde aynı oranla (f)
çarpılır; hedef asgarinin altında kalmaz. Motorun **kendi modeli** (bütün
sert kurallar) kurulur, amaç yalnız fazla mesai dakikalarının toplamı yapılır,
çözücüden en az toplam (x) istenir. Molalar şablon idealinde sabittir (saha
tabanı 0 olduğu için mola yeri hiçbir sert kuralı etkilemez).

| Kişi | f | Sonuç |
|---|---|---|
| 49 | 1,00 · 1,05 · 1,10 · 1,15 · 1,16 | x = 0 — kanıtlı (her biri <1 sn) |
| 49 | 1,17 ve üstü (1,50'ye kadar denendi) | plan **imkânsız** — kanıtlı |
| 49 | yalnız SATIS 1,2 · 1,3 · 1,4 | x = 0 — kanıtlı |
| 151 | 1,00 | x = 0 — kanıtlı |
| 151 | 1,12 · 1,16 · 1,20 | 60 dk bulundu, alt sınır 0 — 15 sn'de **kanıt yok** |
| 151 | 1,22 | 210 dk bulundu, alt sınır 0 — 15 sn'de kanıt yok |
| 151 | **1,24** | **x = 210 dk (3,5 saat) — kanıtlı**, 126 sn; yedi kişi × 30 dk |
| 151 | 1,26 · 1,30 | plan **imkânsız** — kanıtlı |

x'in tanığı (151 kişi, f = 1,24): 684 atamalı plan bağımsız doğrulayıcıda
**0 sert ihlal**, doğrulayıcının saydığı fazla mesai **3,50 saat**,
yayınlanabilir.

Aynı sahnede motor (120 sn bütçe, tek koşu, ikisi de 0 sert):

| | Fazla mesai | x'in katı | Toplam puan |
|---|---|---|---|
| En az (kanıtlı) | **3,5 saat** | 1 | — |
| Ürünün hali | 11,25 saat | 3,2 | 43.064 (33.750'si fazla mesai) |
| *Önce fazla mesaisiz* | 9,75 saat | 2,8 | 38.465 (29.250'si fazla mesai) |

Seçenek 1,5 sn'de *"fazla mesaisiz plan yok (molalar sabitken kanıtlandı)"*
dedi ve bugünkü yola döndü — tasarlandığı gibi; zorunlu durumda bir şey
kazandırmıyor (iki koşu arasındaki 1,5 saat tek koşu farkıdır, okunmaz).

**Okuma.** (1) x bilinen bir set bu ölçekte kurulabiliyor ve motorun x'ten
uzaklığı ölçülebiliyor. (2) Talebi topluca artırmak zorunlu fazla mesaiyi
kolay vermiyor: *fazla mesai gerekmiyor* ile *plan imkânsız* arasındaki
aralık dar (151 kişide f = 1,24 zorunlu, 1,26 imkânsız; 49 kişide aralık hiç
yakalanmadı), x küçük (151 kişide 3,5 saat). Büyük ve zor tutturulan bir x
için hedefli kurulum gerekir. (3) x'i çözücüye kanıtlatmak 151 kişide 126 sn
sürdü; 500 kişide kanıtlanıp kanıtlanamayacağı bilinmiyor.

## 5. Bu sonuçların sınırı

- **Tek koşu.** Fazla mesai serbestken koşudan koşuya fark büyüktü (bulgu 20:
  amaçta %40). Buradaki tek koşular yön gösterir, oran vermez.
- **Küçük set, kısa bütçe, 2 çekirdek.** Ürünün hali 500 kişi, 900 sn, 6
  çekirdektir. 151 kişide 125 sn onun karşılığı değildir.
- **Referans planı motorun kendisi üretti** (başka tohumla). Doğrulayıcı planı
  bağımsız denetler, ama planın *biçimi* motorun aramasından gelir; motorun
  kolay bulduğu türden olabilir. Motordan bağımsız bir kurucu denenmedi.
- **Referans en iyi plan değildir**, üst sınırdır. 49 kişide motor referansı
  geçti (1.424 < 1.429).
- **x'in alt sınırı motorun modelinden.** Tanık bağımsız doğrulayıcıdan geçti;
  alt sınırın bağımsız bir sayım kanıtı yok. Model bir kuralı olduğundan sıkı
  kuruyorsa gerçek x daha küçük olabilir.
- **Asgari topluca çarpıldı.** Gerçek sahada asgari her saatte aynı oranda
  artmaz; bu bir kurulum kolaylığıdır, saha modeli değil.
- **500 kişide hiçbiri ölçülmedi.**

## 6. Nasıl çalıştırılır

Çıktılar depoya yazılmaz; işletim sisteminin geçici klasöründe
`tshift-merdiven` altına gider.

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti\kesif\2026-10-06-veri-seti-merdiveni
py a_plan.py 0.3 125 k03t7 7            # A planı: 151 kişi, 125 sn, tohum 7
py b_gomulu.py k03t7 125 varsayilan     # hedefi türet, ürünün haliyle sıfırdan çöz
py b_gomulu.py k03t7 125 fm0            # aynısı, önce fazla mesaisiz açık
py d_sinir.py k03t7 150                 # ortak arama: küresel alt sınır (bu oturumda 49 kişilik sahnede koşuldu)
py x_kanit.py 0.3 140 1.24              # en az fazla mesai (x), kanıtıyla
py x_tanik.py 0.3 1.24 25               # x'in planı bağımsız doğrulayıcıda
py c_zorunlu.py 0.3 1.24 120 varsayilan # motor aynı sahnede
py c_zorunlu.py 0.3 1.24 120 fm0
```

| Betik | İşi |
|---|---|
| `ortak.py` | depo yolları, çöz-ölç, doğrulayıcı sayımı, asgariyi çarpma |
| `a_plan.py` | taban sahne + fazla mesaisiz plan (gömülecek plan) |
| `b_gomulu.py` | hedefi plandan türetir, referansı yazar, sıfırdan çözer, karşılaştırır |
| `d_sinir.py` | gömülü sahnede tek modelle küresel alt sınır |
| `x_kanit.py` | asgari × f için en az toplam fazla mesai |
| `x_tanik.py` | o planı bağımsız doğrulayıcıya sorar |
| `c_zorunlu.py` | zorunlu fazla mesaili sahnede motorun sonucu |
