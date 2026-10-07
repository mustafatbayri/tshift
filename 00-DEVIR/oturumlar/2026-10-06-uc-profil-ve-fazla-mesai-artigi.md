# 6 Ekim 2026 — üç profil ölçümü: fazla mesai aramanın artığı (bulgu 20); motorun "optimum"u yanlıştı (O-16)

**Pencere:** 3 Ekim'den devam eden pencere (T-60'ın devamı; §5b "aynı işin
devamı → aynı pencere"). Önceki günlük: `2026-10-04-k60-mola-adimi-koda.md`
(§6–7: K-60 yeşil, bulgu 19, ölçüm bütçesi kararı).

## İçindekiler

1. [5 Ekim 21:36–21:45 — commit, demo bağlantısı](#1--5-ekim-21362145--commit-demo-bağlantısı)
2. [6 Ekim 09:48 — koşunun sonucu](#2--6-ekim-0948--koşunun-sonucu)
3. [Okuma: aynı planlar, üç ağırlık tablosu](#3--okuma-aynı-planlar-üç-ağırlık-tablosu)
4. [O-16: "optimum · %0" neydi, nasıl düzeltildi](#4--o-16-optimum--0-neydi-nasıl-düzeltildi)
5. ["Önce fazla mesaisiz" ölçüm seçeneği](#5--önce-fazla-mesaisiz-ölçüm-seçeneği)
6. [Doğrulama (bulut)](#6--doğrulama-bulut)
7. [Kararlar, reddedilenler, açık kalanlar](#7--kararlar-reddedilenler-açık-kalanlar)
8. [Sıradaki adım](#8--sıradaki-adım)
9. [Bağımsız inceleme ve düzeltmeleri](#9--bağımsız-inceleme-ve-düzeltmeleri)
10. [19:21 — Mustafa'nın koşuları](#10--1921--mustafanın-koşuları)
11. [21:08 — ölçüm sonucu (bulgu 21) ve karar sorusu](#11--2108--ölçüm-sonucu-bulgu-21-ve-karar-sorusu)
12. [21:34–22:45 — amaç hatırlatması ve veri seti merdiveni; okuma, ön deneme (bulgu 22)](#12--21342245--amaç-hatırlatması-ve-veri-seti-merdiveni-okuma-ön-deneme-bulgu-22)
13. [23:02–23:15 — Mustafa'nın cevabı: yapı ve sabit kriter onaylandı; üç soru; iki veri seti eksiği (O-17)](#13--23022315--mustafanın-cevabı-yapı-ve-sabit-kriter-onaylandı-üç-soru-iki-veri-seti-eksiği-o-17)
14. [6 Ekim 23:44 – 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* varsayılan; hakem ağırlıklardır) koda indi; K-62 (merdiven ve kadro)](#14--6-ekim-2344--7-ekim-0045--k-61-önce-fazla-mesaisiz-varsayılan-hakem-ağırlıklardır-koda-indi-k-62-merdiven-ve-kadro)
15. [7 Ekim 01:00–03:30 — bağımsız inceleme: 00:45 sürümü ilkeyi çiğniyordu (O-18, bulgu 23); düzeltme](#15--7-ekim-01000330--bağımsız-inceleme-0045-sürümü-ilkeyi-çiğniyordu-o-18-bulgu-23-düzeltme)
16. [7 Ekim 03:05–04:30 — kredi kesintisi, yeniden uygulama, yeniden doğrulama; eşdeğer mutant; bulgu 24](#16--7-ekim-03050430--kredi-kesintisi-yeniden-uygulama-yeniden-doğrulama-eşdeğer-mutant-bulgu-24)

## 1 · 5 Ekim 21:36–21:45 — commit, demo bağlantısı

Kalibrasyon sonucu (bulgu 19) ve damga `e4f6115` ile commit'lendi (21:36).
**21:41 — Mustafa:** demo sayfasının bağlantısı istemediği kişilere geçmiş
olabilir; eski bağlantı çalışmasın, yenisi olsun. Eski sayfa silindi, aynı
içerik yeni ve özel bir bağlantıyla yayınlandı (içerik bayt bayt aynı). Depoda
eski bağlantıya atıf yoktu (arandı); bağlantının kendisi depoya yazılmadı.

## 2 · 6 Ekim 09:48 — koşunun sonucu

Mustafa: *"koşunun sonucu"* (ek: üç profil, 900 sn, üçer koşu; 07:34–09:42,
`kalite-olcumu-95-profiller-900.json`). Dokuz koşunun hepsi 0 sert,
yayınlanabilir, K-57'nin üç fazla mesai sayısı aynı. Tablo `06-ACIK-RISKLER.md`
T-60 bulgu 20'de. Kısaca:

| | DENGELI | KAPSAMA | CALISAN |
|---|---|---|---|
| fazla mesai (saat) | 26,25–40,5 | 10–14,25 | **0** |
| hedef eksiği (kişi-saat) | 356–367 | 170–197 | 565–615 |
| amaç (kendi ağırlıklarıyla) | 105.742–148.431 | 45.702–57.781 | 33.870–34.259 |
| toplam arama | 779–781 sn | 781–795 sn | 779–798 sn |

5 Ekim'de *"CALISAN çözümsüz çıkabilir"* diye uyarmıştım (tavan 0, veri
setinde 28–45 saat fazla mesai). **Çıkmadı**; üç koşuda da 0 saatle çözdü.

## 3 · Okuma: aynı planlar, üç ağırlık tablosu

CALISAN'ın amacı (34 bin) DENGELI'ninkinden (106–148 bin) çok küçük görününce
şu soruldu: profil modelde neyi değiştiriyor? Koddan okundu (`model.py`):
yalnız ağırlık sütununu (`_agirlik`) ve fazla mesai tavanını
(`FAZLA_MESAI_PROFIL`). Sert kurallar aynı → CALISAN'ın planı DENGELI ve
KAPSAMA için de geçerli. Her kuralın ağırlığı kural içinde tek (çıktıdaki
ceza ÷ ham değer dokuz koşuda tam sayı) → bir planın başka profildeki amacı
Σ ağırlık × ham değer; her koşunun kendi amacı bu toplamla birebir tuttu.

- CALISAN planları **DENGELI ağırlıklarıyla** 26.703 · 26.589 · 26.671;
  DENGELI'nin kendi planları 105.742–148.431 → **4–5,6 kat**.
- CALISAN planları **KAPSAMA ağırlıklarıyla** 20.696 · 21.360 · 21.549;
  KAPSAMA'nın kendi planları 45.702–57.781 → 2,2–2,8 kat.
- DENGELI'nin üç koşusunda fazla mesai **dışı** toplam 26.972 · 26.931 ·
  26.992 (%0,2). Oynayan tek kalem fazla mesai: 24 · 33 · 21 kişi, hepsi
  46,25 saatlik altı vardiyalı karışımda (1,25 saat fazla).

Sonuç: fazla mesai bu girdide **gerekmiyor**; motorun yumuşak cezayla süre
içinde sıfırlayamadığı bir artık. K-30'un tablosuna göre (*"yalnız hedef
kapsama iyileşecekse fazla mesai yapılmaz"*) plan karara uymuyor.

⚠ Aşırı okumamak için: CALISAN planı DENGELI müşterisi için "daha iyi plan"
değil — hedefi tam tutan hücre %69–72 (DENGELI %82–85). Kesin olan yalnız
*"DENGELI için 26.589'luk fazla mesaisiz plan var"*.

**"Alt sınır zayıf" okumasının düzeltmesi.** 1–2 Ekim'de optimuma uzaklığın
%93–99 çıkmasını *"sınır zayıf"* diye okumuştum. Eldeki dosyalardan: tam
modelin kanıtladığı sınır 19.769–20.934, en iyisi 21.098; model 2 Ekim
17:58'den beri değişmedi. Bilinen en iyi plan 26.589 → sınıra en çok %20,7.
Sınır yerindeydi; planlar kötüydü.

## 4 · O-16: "optimum · %0" neydi, nasıl düzeltildi

Dokuz koşunun hepsi `durma_sebebi: optimum`, `alt_sinir == amac_degeri`,
`optimuma_uzaklik_yuzde: 0.0` ile bitmişti. §3'teki sayılarla bu imkânsız:
*"optimum"* denen planın 4–5,6 kat iyisi var. Sebep: K-60'tan beri ana aşama
mola adımı; çözücü atamalar **sabitken** çalışıyor ve sınırı yalnız *"bu
atamalarla en iyi mola yerleşimi"*ni kanıtlıyor. Ben 4 Ekim'de bu sınırı genel
alanlara yazdırdım, teste ve şartnameye de öyle yazdım. K-35'in kartı bu
alandan beslenir.

Düzeltme (`09-motor/cozucu/coz.py`, `coz()`):
- mola adımı koştuysa (`atamalar_sabit`): `alt_sinir` → **null**,
  `metrikler.optimuma_uzaklik_yuzde` → **null**, yeni alan
  `mola_adimi_alt_sinir`; `durma_sebebi` `optimum` / `hedef_bosluk` ise
  `mola_adimi_` ön eki alır (`durgunluk`, `butce_doldu` aynen);
- tam modeli çözen yollarda (küçük model, başlangıç planı, `mola_adimi:
  False`) alanlar eskisi gibi.

Testler (`test_demir_secenekleri.py` 21, `test_ilk_asama.py`): yanlış iddiayı
taşıyan üç test düzeltildi; yeni `test_O16_mola_adimi_optimumu_PLANIN_
optimumu_DEGILDIR_kuresel_sinir_YAZILMAZ` (birinci aşamaya bilerek kötü plan
verilir — mola adımı *"mola_adimi_optimum"* der, plan tam modelin kanıtlı
optimumundan kötüdür, çıktı küresel sınır yazmaz) ve `test_O16_on_ek_...`
(ön ek yalnız kanıt iddia eden sebeplere, yalnız mola adımında). İncelemeden
sonra kural genelleştirildi (§9): toplam 5 O-16 testi, 14 mutasyon (`demir` →
40). `kalite-olc.py` ekrana *"küresel alt sınır YOK (mola adımı
sınırı …)"* yazar, tabloda `-` basar, fazla mesai dışı amacı ayrı sütunda verir.

## 5 · "Önce fazla mesaisiz" ölçüm seçeneği

`VARSAYILAN["fazla_mesai_once_sifir"] = False` — **ürün davranışı değişmedi.**
Açıkken `_ipucu_ver`:

1. fazla mesai ceza değişkenlerinin (`fm_*`) alanı [0,0] yapılır (kısıt
   eklenmez; molaları sabitleyen yöntemle aynı), geçerli plan aranır;
2. **bulunursa** alanlar kapalı kalır: iyileştirme ve mola adımı da fazla
   mesaisiz bölgede arar (K-30 tablosunun ilk satırı);
3. **bulunamazsa** — `INFEASIBLE` (molalar sabitken kanıt) ya da süre —
   alanlar aynen geri açılır, fazla mesai serbestken bir kez daha geçerli plan
   aranır (`_gecerli_plan_yeniden_ara`: birinci aşamanın payı kadar, kalan
   bütçeyi aşmadan, en az 1 sn), bugünkü yol işler; `uygulanmayan_notlar`a
   *"fazla mesaisiz plan yok (molalar sabitken kanıtlandı)…"* ya da *"…bu
   sürede bulunamadı…"* düşer. Zorunlu fazla mesai yolu (K-38) kapanmaz.
   Başarısız denemenin süresi **iyileştirmenin payından düşer**
   (`_ilk_asamada_iyilestir(…, dusulecek)`): ilk yazışta düşülmüyordu ve
   kendi gözden geçirmemde en kötü hâl çıktı — deneme ve yeniden arama
   paylarını doldurursa 900 sn'de 120 + 120 + 659, mola adımına 1 sn, elde
   plan varken *"süre yetmedi"*. Düşülünce mola adımına kalan süre bugünkü
   yolun en kötü hâliyle aynı (120 + 720 → 60 sn). Bulunan denemede düşülmez:
   o arama birinci aşamanın aramasının kendisidir.

Çıktı: `cozum_istatistikleri.fazla_mesai_once_sifir = {bulundu, degisken,
saniye, kanitlandi_yok}` (kapalıyken, iki aşama yokken ya da fazla mesai
değişkeni yokken null). Kapsam: yalnız iki aşamalı yol; eşiğin altındaki model
ve başlangıç planı (*"İyileştir"*) etkilenmez.

Neden işe yaraması beklenir (ölçüm değil, gerekçe): fazla mesai değişkenleri
0'a sabitken DENGELI'nin birinci aşaması **bu veri setinde** CALISAN'ın
birinci aşamasıyla aynı problemdir (profil yalnız ağırlık ve tavanı
değiştirir; birinci aşama amaçsızdır; kadroda sözleşme saati olmayan tam
zamanlı yok — olsaydı onların haftalık tavanı iki profilde farklı kalırdı) —
ve o problem bu sabah üç koşuda 13–33 sn'de çözüldü.

Testler: `test_fazla_mesai_once_sifir.py` 16 (§9'dakilerle; varsayılan kapalı ve ürün aynı;
plan varsa bulunur ve fazla mesai mola adımında da [0,0]; zorunluysa kanıt,
alanlar aynen geri, plan döner, not; süreye takılırsa kanıt denmez; yeniden
arama süresi pay ve kalan bütçeyle sınırlı; başarısız denemenin süresi
iyileştirmeden düşer, başarılınınki düşmez, seçenek kapalıyken pay aynen;
sıfırlama yalnız `fm_` değişkenlerine dokunur, geri alma tam; fazla mesai
değişkeni yoksa sessiz; iki aşama yoksa uygulanmaz). 29 mutasyon (yeni grup
`fm_sifir`).

`kalite-olc.py`: `fm_once_sifir` (DENGELI), `fm_once_sifir_kapsama`;
`test_kalite_olc.py` +6 (16).

## 6 · Doğrulama (bulut)

Bulut makinesi (2 çekirdek) — Mustafa'nın makinesi için **tahmin değildir**.

- `09-motor/testler`: 41 dosya, **572 test** geçti (5 Ekim'de 551; +5 `demir`,
  +16 yeni dosya).
- gerçekçi set: `test_kalite_olc.py` 16 + `test_sahte_pdks.py` 8 geçti;
  `test_gercekci_olcek.py` bulutta koşulmadı (180 sn sınırı) — Mustafa'da.
- mutasyon grup koşuları, hepsi öldü: `demir` 40, `fm_sifir` 29, `ilk_asama`
  6, `butce` 4, `kalite` 6. Bütün çapalar tam bir kez geçiyor (271 mutasyon
  sayıldı). ⚠ **Toplam iddiası yalnız tam koşudan** (O-15): tam koşu
  Mustafa'nın makinesinde bekliyor.
- duman, 0,1 ölçek, 45 sn, tek koşu: `varsayilan` 6.458 (1,25 saat fazla
  mesai, fazla mesai dışı 2.708) ↔ `fm_once_sifir` 2.673 (0 saat; fazla
  mesaisiz plan 0,5 sn'de bulundu), ikisi de 0 sert, yayınlanabilir.

Tam ölçek bulutta koşulmadı: 2 çekirdek, Mustafa'nın 6 çekirdeğiyle
kıyaslanamaz.

## 7 · Kararlar, reddedilenler, açık kalanlar

**Karar yok** — bugün ölçüm okundu, hata düzeltildi, ölçüm seçeneği yazıldı.
Ürün varsayılanına dokunulmadı.

Değerlendirilip **yazılmayanlar:**
- *"Yalnız başlangıç fazla mesaisiz olsun, sonra alanlar açılsın"* (fazla
  mesaisiz plandan başla, iyileştirme ağırlıklara göre fazla mesaiyi geri
  getirebilsin). K-30'un ilk satırı fazla mesaiyi hedef için yasaklıyor; bu
  hâl ona izin verirdi. Mutasyon olarak duruyor (*"bulununca alanlar geri
  açılsın"*), test öldürüyor.
- Sonuç kartı için **sınır adımı** (tam modeli kalan sürede sınır için
  koşturmak). Kart cümlesi 2 Ekim'den beri ertelenmiş; fazla mesai kararından
  önce ikinci bir mekanizma eklenmedi. Eldeki eğrilerden bedeli T-60'ta yazılı.

Benim düzeltmelerim (bu oturumda yanlış çıkan kendi cümlelerim):
- *"CALISAN çözümsüz çıkabilir"* — çıkmadı.
- *"Alt sınır zayıf"* (1–2 Ekim) — sınır yerindeydi.
- K-60'ın *"kanıtlı optimum"*unu çıktının genel alanına yazdırmak (O-16).
- Seçeneği yazarken önce *"problemi değiştirmiyor"* diye düşündüm; kesin
  ifade şu: dayanağı K-30'un tablosudur (sıfır mümkünse sıfır). Ağırlıkların
  söylediğinden farklı bir şey yaptığı tek durum — fazla mesaisiz plan varken
  birkaç dakika fazla mesaiyle toplam puanın daha iyi çıkması — K-30'un
  yasakladığı durumdur. Yani ağırlıklı toplamı değil, kararı uygular.

**Açık (Mustafa'ya):**
1. `fazla_mesai_once_sifir` ürün varsayılanı olsun mu — **ölçümden sonra**.
2. Mola adımı süresinde plan bulamazsa birinci aşamanın planı notla dönsün mü
   (4 Ekim'den beri açık; bugün *"süre yetmedi"* döner).
3. Sonuç kartı: büyük modelde yüzde nereden gelecek (sınır adımı ölçümü) ve
   null iken kart ne gösterecek.
4. `gun_sayisi` alanı (T-80).

## 8 · Sıradaki adım

Mustafa'nın makinesinde: `09-motor` testleri, gerçekçi set testleri, **tam
mutasyon koşusu** (271 beklenir), `DENETIM.py`, commit + push
(`kalite-olcumu-95-profiller-900.json` ve damga dahil). Sonra ölçüm:

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti
py kalite-olc.py --saniye 900 --tekrar 3 --yapilandirma fm_once_sifir,fm_once_sifir_kapsama --etiket fmsifir-900
```

≈85 dk (ilk üç koşu ≈43 dk). Karar kuralı koşudan önce yazıldı:
`06-ACIK-RISKLER.md` T-60, son "Sıradaki adım".

## 9 · Bağımsız inceleme ve düzeltmeleri

Kod ve testler yazıldıktan sonra, işi **görmemiş** ayrı bir oturuma yalnız
dosyalar okutuldu (motoru koşturamadı; okuma ve ölçüm dosyası üzerinde
hesap). Gerekçe O-10'un kuralı ve bugünkü O-16: hatayı koruyan testi ben
yazmıştım, düzeltmeyi de ben onaylamamalıydım.

**Bulduğu ve düzeltilenler:**

1. **O-16'nın aynı sınıfı seçeneğin içinde.** Deneme plan bulduysa fazla mesai
   değişkenleri ana aşamada da 0'da; ana aşama ortak aramaysa (`mola_adimi:
   False`, ölçüm) çözülen model tam model değil ama sınır küresel alanlara
   gidiyordu. → `_sinir_kapsami`: soru *"atamalar sabit mi"* değil *"çözülen
   model tam model mi"*; kısıtın adı (`mola_adimi` / `fazla_mesaisiz`) sınırın
   ve sebebin adına girer; yeni alan `fazla_mesaisiz_alt_sinir`.
2. Ölçüm seçeneği (b)'nin kolları kopyayı atamalar sabitlendikten sonra
   alıyor; sınırları kısıtlı koşuda küresel diye yazılıyordu. →
   `_paralel_kisitli_isaretle`.
3. Başarısız denemenin süresi yalnız paydan (%80) düşüyordu; iyileştirme
   süresi açıkça verilmiş yapılandırmada hiç düşmüyor, mola adımının süresi
   kısalıyordu. → `min(min(istenen, pay) − deneme, kalan)`.
4. CALISAN'da fazla mesai alanları zaten [0,0]: deneme *"sabitledi"*,
   başarısızsa *"serbest bıraktı"* diyor ve aynı modeli ikinci kez arıyordu.
   → zaten 0 olan alan sayılmaz; seçenek orada işlemsiz, çıktı null.
5. Not, `ilk_asama_sabit_mola: False` iken de *"molalar sabitken kanıtlandı"*
   diyordu. → ayardan okunur; çıktıda `molalar_sabit`.
6. `kalite-olc.py`: seçenek istendiği hâlde uygulanmadıysa (küçük ölçekte iki
   aşama yok) koşu sessizce varsayılan yolu ölçüyordu; plansız koşuda deneme
   satırı basılmıyordu. → `fm_once_yazisi`: *"UYGULANMADI"* yazar; iki yolda
   da basılır.

Küçük düzeltmeler: KAPSAMA için kat aralığı 2,1–2,8 değil **2,2–2,8** (en iyi
plana bölünce); bir test yolu gerçekten koşturduğunu artık iddia ediyor
(`iki_asama`); özetin plansız ve istisna kayıtlarıyla çökmediği testte.

**Doğruladıkları (bağımsız hesap/okuma):** dokuz koşunun amacı kendi
ağırlıklarıyla birebir; yeniden fiyatlama sayıları; DENGELI'nin fazla mesai
dışı üç sayısı; profilin modelde yalnız `_agirlik` ve `FAZLA_MESAI_PROFIL`
üzerinden etki ettiği; `cezalar`a giren altı değişken ailesinin hepsinin adlı
olduğu, `fm_` ön ekinin yalnız fazla mesai değişkeninde kullanıldığı; seçenek
kapalıyken akışın aynı kaldığı; zaman testlerinin saat çözünürlüğüne bağlı
olmadığı.

**Bilinen, düzeltilmeden bırakılan** (T-60'ta yazılı): başarılı ama yavaş
denemenin mola adımının süresini yemesi (yeni değil — birinci aşamanın payını
dolduran her aramada var; Mustafa'ya açık soru 2); `iyilesme` eğrisindeki sınır
sütununun adı; `kalite-olc.py` *"bağımsız alt sınır"* satırının karışık
profilli dosyada ilk koşunun ağırlığını kullanması (taban 0, etkisiz).

Düzeltmelerden sonra: bulutta `09-motor` **572 test**, gerçekçi setin iki
dosyası 24 test; `demir` 40 ve `fm_sifir` 29 mutasyon grup koşularında öldü;
toplam sayılan **271**. 0,1 ölçek dumanı iki yapılandırmada yeniden koşuldu
(`fm_once_sifir` 2.673; `fm_once_sifir_kapsama` 1.699; ikisi de 0 saat fazla
mesai, 0 sert).

## 10 · 19:21 — Mustafa'nın koşuları

Mustafa: *"her şey ok mi geçeyim mi blok 3 e"* (ek: blok 1–2 çıktısı).
`09-motor` **572 geçti** (80 sn), gerçekçi set **37 geçti** (428 sn), tam
mutasyon koşusu **271 · yaşayan 0 · atlanan 0** (damga 19:16), DENETIM hata
yok (15 uyarı: eski günlüklerdeki ad ve yol atıfları, commit bekleyen 16
dosya, R7). Köprüden bakıldı: depoda yalnız beklenen 16 dosya değişik; 14
dosyanın md5'i sabah yazılıp doğrulananla aynı — testler tam o dosyalarda
koştu, mutasyon koşusu her dosyayı geri yazmış. Bu dört satır (koşu sonucu)
commit'ten önce belgelere işlendi; kod dosyalarına dokunulmadı. Sırada blok 3
(commit + push) ve blok 4 (ölçüm).

## 11 · 21:08 — ölçüm sonucu (bulgu 21) ve karar sorusu

Mustafa: *"cı da yeşil"* (ek: ölçüm çıktısı). Commit `85131ee`, iki atıf
satırı tek blokta. Ölçüm 19:37–21:00, `kalite-olcumu-95-fmsifir-900.json`
(sayılar dosyadan okunarak doğrulandı; tablo `06-ACIK-RISKLER.md` T-60 bulgu
21'de).

| | DENGELI sabah → akşam | KAPSAMA sabah → akşam |
|---|---|---|
| fazla mesai (saat) | 26,25–40,5 → **0** | 10–14,25 → **0** |
| amaç | 105.742–148.431 → 26.407–26.494 | 45.702–57.781 → 13.834–13.914 |
| hedef eksiği (kişi-saat) | 356–367 → 344–350 | 170–197 → 98–106 |
| hedefi tam tutan hücre | %82,4–84,8 → %85,8–86,5 | %89,6–90,6 → %92,8–94,2 |
| koşudan koşuya fark (amaç) | %40 → %0,3 | %26 → %0,6 |
| toplam arama | 779–781 → 773–776 sn | 781–795 → 775–779 sn |

Karar kuralının dört maddesi (sabah yazıldı) iki profilde, altı koşuda tuttu.
Fazla mesaisiz plan 8,8–12,7 sn'de bulundu. Kötüleşen kalemler de yazıldı
(DENGELI adalet ≈+%0,6; KAPSAMA aşım ≈+%3, adalet ≈+%2).

**Önerim:** ürün varsayılanı olsun. **Öneriyle birlikte söylenen sınır:**
seçenek *"sıfır mümkünse sıfır"*ı çözüyor; fazla mesainin gerçekten zorunlu
olduğu veride bugünkü yol işliyor ve orası tam ölçekte hiç ölçülmedi (öyle
bir set yok). Yalnız %95 seti ve 900 sn ölçüldü.

**Karar Mustafa'da.** Kod bu adımda değişmedi; belgeler ve ölçüm dosyası için
commit bloğu verildi.

## 12 · 21:34–22:45 — amaç hatırlatması ve veri seti merdiveni; okuma, ön deneme (bulgu 22)

Mustafa (21:34): *"Sonraki iş: zorunlu fazla mesaili bir veri seti kurup o
yarıyı ölçmek. bunu yapmalıyız. Yani öyle bir data seti verelim ki örneğin
minimum x kadar fazla mesai yapmak zorunda kalalım, x ten ne kadar
uzaklaştığımıza göre kaliteyi ölçeriz. Tabi bu x değerini tutturmak
olabildiğince zor olmalı. Ürünümüzün amacı fazla mesai yani firmaya ek ücret
çıkarmadan eldeki kaynağı en iyi kullanmasını sağlaması bu hiç bir zaman
değişmeyecek bir konu. Şu an yapmaya çalıştığımız plan fazla mesai kısmına
olabildiğince az giderek diğer kriterleri de hesaba katarak optimum plan
yapabiliyor mu? Bu arada sadece sen sorduğun için fazla mesaiye cevap verdim,
ürünün asıl çıktısı bu değil. Ürünün çıktısı elimizdeki tüm kriterlere bağlı
olarak optimum planı çıkarabiliyor muyuz? Amacımız fazla mesai konusunu
çözmek değil sadece. Fazla mesai 43 kriterden sadece biri bunu unutma.
Amaçtan dağılma sakın."*

Mustafa (21:36, ben çalışırken): *"Bence bundan sonrası için, birden fazla
data seti ile ilerlemeliyiz. Data setleri 5 kısım olabilir aklıma gelen
sadece, sen de yorumla bu kısmı: 1- en basit data seti ve kriter seti (500
çalışan için tabi) , 2- planın optimum oluşturulması biraz daha zor, 3 4 5
olarak zorlaşarak ilerlemeli hatta 5 seviyesinde plan çözümsüz olabilecek
kadar zor data seti olmalı? fikrime ne diyorsun ?"*

**Okuma (yalnız okuma; depo `ae57023`, temiz).** Şartname §5.3–5.4 ve §6
baştan okundu: katalog **41** kural (32 sert, 9 yumuşak) — Mustafa'nın *"43"*ü
katalogla uyuşmuyor, kendisine söylendi. Motorda dört yumuşak kuralın
(`EKIP_SUREKLILIGI`, `PLAN_KARARLILIGI`, `TERCIH_KARSILAMA`,
`VARDIYA_ROTASYON_YONU`) yalnız ağırlık satırı var; terimi ve doğrulayıcı
gövdesi yok. %95 fikstürü: asgari 12.723, hedef 18.660 kişi-saat, kapasite
sayısı 19.630; geçmiş vardiyalar 500 kişide boş, donmuş gün ve yayınlanmış
plan yok, kilit 6, herkes tek ekipte, yıl içi fazla mesai 497 kişide dolu (en
büyük 269). Akşamın en iyi DENGELI planı (26.407): adalet 12.490 · hedef
aşımı 9.423 (3.141 kişi-saat) · hedef eksiği 3.150 (350) · mola 1.344 ·
fazla mesai 0. `kural-kapsamasi.py`: 22 satır SINANDI (17 ayrı kural), 20
TEMİZ, 4 GÖVDE YOK.

**Ön deneme (bulut, 2 çekirdek; betikler ve tablolar
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/`).**

| Deneme | Kişi | Bilinen | Ürünün hali | *Önce fazla mesaisiz* |
|---|---|---|---|---|
| Gömülü plan (puan) | 49 | referans 1.429 | 1.424 | — |
| Gömülü plan (puan) | 151 | referans 4.089 | 8.864 | 4.146 |
| Zorunlu fazla mesai (saat) | 151 | en az 3,5 (kanıtlı) | 11,25 | 9,75 |

Tek koşu, 90–125 sn bütçe; 500 kişi için tahmin değil. Gömülü planın tuzağı
(referans varsayılan aramayla üretilirse motor aynı planı yeniden buluyor)
ve *"asgariyi topluca artırınca zorunlu aralık dar"* gözlemi keşif
klasöründe.

**Mustafa'ya verilen görüş (22:45).** Çok set doğru. Ekler: her seviyenin
bilinen bir cevabı olsun; kriter seti seviyeler arasında aynı kalsın (kriter
kapatma yalnız teşhis için); beşinci seviye iki set olsun (dar kapı / kanıtlı
imkânsız). Basamak önerisi: 1 tam oturan talep · 2 sıkı kadro · 3 geçmişli
hafta · 4 zorunlu fazla mesai (x) · 5a dar kapı · 5b imkânsız; bugünkü %85 ve
%95 setleri karşılaştırma olarak durur. Sıra bir varsayım, ölçülünce
değişebilir. Dört yazılmamış yumuşak kural ayrıca söylendi: *"tüm kriterler"*
bugün ölçülebilen 37 kuraldır.

**Değişmeyen.** Kod; ürün varsayılanı (`fazla_mesai_once_sifir` kapalı —
Mustafa *"evet"* demedi, *"bunu yapmalıyız"* zorunlu yarının ölçülmesi diye
okundu ve kendisine söylendi). **Yanlış çıkan bir not:** `uret_veri_seti.py`
*"%95: … fazla mesai ZORUNLU hale gelir"* diyor; bulgu 20–21 tersini ölçtü.
Not, merdiven aracı yazılırken düzeltilecek (dosyaya bu adımda dokunulmadı).

**Açık.** Mustafa'nın merdiven tasarımına cevabı; ürün varsayılanı (zorunlu
yarı ölçülünce); önceki açık sorular (mola adımı yetişmezse plan notla dönsün
mü; sonuç kartındaki yüzde; `gun_sayisi`).

## 13 · 23:02–23:15 — Mustafa'nın cevabı: yapı ve sabit kriter onaylandı; üç soru; iki veri seti eksiği (O-17)

Önceki adımın kayıtları `82f0135` ile commit'lendi.

Mustafa (23:02): *"“Önce fazla mesaisiz” hâlâ kapalı. “Bunu yapmalıyız”ı
“önce zorunlu yarıyı ölç” diye okudum; “evet” demek istediysen söyle. Bunu
anlamadım. 1- merdiven yapısını beğendim evet. 2- önerdiğin gibi. 151 kişiyi
anlamadım kafam karıştı, biz merdiven testlerini 500 kişi için yapacağız
değil mi ? Bir de 1 ekip 500 kişi demişsin, ben 250 satış 150 backoffice 100
müşteri ilişkileri ekibi örneğini vermiştim diye hatırlıyorum. Gerçi senin 1
ekip 500 kişi daha zor lakin şu case patlıyorsa diye endişem var, örneğin
gece 3 de satış ve backoffice den sahada olması gereken sayıyı, örneğin satış
ekibinde bulunan hem satış hem backoffice yetkinliği olan elemanla
çözecektik, yani örneğin her birimden bir kişi olması gerekiyor ya, biz 2
yetkjinliği olan 1 kişi ile bu talebi karşılayabiliyoruz. Bu case'in de
sürecimizde olması gerekiyordu. Bunlara cevap verir misin önce, sonra ne
yapacağımızı tam onaylamış olayım devam edelim"*

**Onaylanan (Mustafa).** Merdiven yapısı (altı set, 500 kişi, her seviyenin
bilinen cevabı, beşinci seviye iki set) — *"evet"*. Kriter seti seviyeler
arasında sabit — *"önerdiğin gibi"*.

**Bakılan (yalnız okuma + bir test koşusu).**

- *Ekip sayıları.* Depodaki kayıtlarda 250 / 150 / 100 yok. Kayıtta olan: 28
  Eylül seti 350 kişi, 200 satış / 100 back office / 50 müşteri hizmetleri
  (`uret_veri_seti.py`: *"Mustafa'nın verdiği dağılım"*); 29 Eylül'de *"350-500"*
  üzerine aynı oranla 500 kişi: 285 / 145 / 70. Mustafa'nın o günkü tam
  cümlesi kayıtta yok.
- *İki işi yapabilen eleman.* K-50 (1 Ekim) motor ve doğrulayıcıda;
  `09-motor/testler/test_cok_ekipli.py` 13 test, ilki Mustafa'nın örneği
  (gece, satış 1 + back office 1, iki ekibe üye tek kişi → tek atama, iki
  talep de karşılanır, doğrulayıcı 0 ihlal, başka ekipten kapsama 1 hücre).
  Bulutta koşuldu: **13 geçti**. 500 kişilik fikstürde iki ekibe üye **kimse
  yok**; gece back office talebi hafta içi asgari 13 (hedef 19), hafta sonu
  asgari 6 (hedef 13). K-50 kaydının kendi satırı: *"500 kişilik sette herkes
  tek ekipte; davranış değişmedi"*.
- *"%95".* 29 Eylül günlüğü §5: Mustafa seti *"eleman yetmiyor, fazla mesaiye
  gidiliyor"* durumu için istemişti; set o durumu vermiyor (bulgu 20–22).
- *Seçeneğin kapsamı.* `fazla_mesai_once_sifir` yalnız iki aşamalı akışta
  (50.000 değişken ve üstü) uygulanır; küçük modelde dokunmaz
  (`test_iki_asama_YOKSA_secenek_uygulanmaz_alanlara_dokunulmaz`).

**Verilen cevap (23:10).** (1) Anlaşılmayan cümle açıklandı: 21:08'de sorulan
evet/hayır sorusu (*önce fazla mesaisiz ürünün standart davranışı olsun mu*)
cevapsız kalmıştı, ürün değişmedi; öneri **evet** (ölçülen durumda açık ara
iyi; zorunlu durumda küçük denemede zararsız; 500 kişide zorunlu durumun
süresi ölçülmedi, en kötü 2 dakika). (2) 151 kişi yalnız buluttaki ön
denemeydi; merdiven ve sayılacak bütün ölçümler 500 kişi, Mustafa'nın
makinesinde. (3) Sette bir değil üç ekip var; *"herkes tek ekipte"* = kimse
iki ekibe üye değil; 250 / 150 / 100 istenirse merdiven öyle kurulur.
(4) İki işi yapabilen eleman: motor yapıyor ve test edilmiş, ama 500 kişilik
sette yok — eksik benim (**O-17**); *"%95"* de aynı sınıf. Düzeltme: iki işi
yapabilen kişiler merdivenin **bütün** seviyelerinde (seviye 2'ye
bırakılmıyor), gece back office talebi tarif edildiği gibi, her ölçümde
başka ekipten kapsama raporlanır.

**Mustafa'nın kararını bekleyen dört şey.** (a) *Önce fazla mesaisiz* açılsın
mı (öneri: evet). (b) Ekip sayıları 285 / 145 / 70 mi, 250 / 150 / 100 mü.
(c) Kaç satışçı back office de yapabilsin (varsayım: 30, yaklaşık %10 —
sahadan sayı değil, düzeltilecek). (d) Gece 00:00–08:00 back office talebi
en az 1 kişi olsun mu.

**Sıra (onay sonrası).** (a) evet ise önce o: varsayılan, testler,
mutasyonlar, karar kaydı, şartname; Mustafa'nın koşuları ve tek doğrulama
koşusu. Sonra kadro (iki işi yapabilen kişiler, gece talebi), seviye 1 ve 4
araç olarak, referans planlar Mustafa'nın makinesinde, 500 kişide 900 sn
ölçüm.

## 14 · 6 Ekim 23:44 – 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* varsayılan; hakem ağırlıklardır) koda indi; K-62 (merdiven ve kadro)

`82f0135` commit'lenmişti; §13'ün kayıtları commit edilmedi (Mustafa: *"son
attığın git bloğunu koşmadım. Sen koş dersen koşacağım"* — bu adımın bloğuyla
birlikte gidecek).

Mustafa (23:44): *"mesaisiz bir plan arasın, bulursa onunla devam etsin; bu,
ürünün standart davranışı olsun mu? Evet, ama sadece basit bir evet değil,
ürünün en önemli davranışının bu olmadığını anlatmaya çalıştım. Yani
elimizdeki tüm kriterleri karşılayan en iyi plan fazla mesaisiz olmalı. Ama
matematiksel olarak kurduğumuz modelde ağırlıklar baz alındığında örneğin 3
saat fazla mesai içeren en optimum plan var var ve fazla mesaisiz plandan
oldukça daha optimum bir plan ise en optimum olanı seçmeliyiz. Ne demek
istediğimi anlattığıma inanıyorum, kafanı karıştıran bir durum varsa söyle
netleştirelim. Sonuçta elimizde ser kısıtlar, yasal kısıtlar var yani
bunların tamamı bir küme davranışı. Örneğim basit olabilir ama ne yapmak
istediğimi anlattığına inanıyorum. İki işi yapabilen kişiler merdivenin
bütün seviyelerinde kadroda olacak; seviye 2'ye bırakmıyorum. Bu çok doğru
bir davranış tebrik ederim. Çünkü gün içinde de örneğin satış çağrıları
şiştiğinde veya backoffice çağrıları şiştiğinde satış ekibine çağrı
gidebiliyor, burada bacvkoffice kabiliyetli bazı kişilerin olması gerçek
planlamada da bulunuyor. 1- Evet 2- 285 145 70 kalsın. 4- en az 2 olsun
mesela."* · (aynı dakika) *"Cevaplarımdan sonra ne yapacağız devam et, son
attığın git bloğunu koşmadım. Sen koş dersen koşacağım"*

**Okuma.** *"Evet"* koşulsuz bir evet değil: hakem ağırlıklar. Seçeneğin o
günkü hâli ise fazla mesaisiz plan varken fazla mesaili planlara hiç
bakmıyordu — ilkeyle arasında bir fark vardı. Karıştıran bir durum yoktu,
ama farkın kendisi Mustafa'ya sayıyla söylenmeli: bugünkü ağırlıklarda 1 saat
fazla mesai = 333 kişi-saat hedef eksiği (DENGELI), ~~yani örneği (*"3 saat
fazla mesaili plan oldukça daha optimum"*) bu kurda oluşmaz~~ *(yanlış —
§15)*; kur K-30'un ağırlığa yazılmış hâli.

> ⚠ **Bu bölümün "Yapılan" ve "Doğrulama" kısımları 7 Ekim 03:30'da
> geçersiz oldu (§15, O-18).** Buradaki sürüm (ağırlık koşulu, `uygulandi`,
> 26 test, 44 mutasyon) Mustafa tarafından hiç koşulmadı ve commit edilmedi.

**Yapılan.**

1. *Kod* (`09-motor/cozucu/coz.py`): varsayılan True; koşul
   `_fazla_mesai_kisayolu_gecerli` (fazla mesai dakika ağırlığı ≥ öteki
   ağırlıkların en büyüğü); koşul tutmazsa deneme yapılmaz, çıktı
   `{uygulandi: false, sebep: "agirlik", …}`, not düşer; denenen hâllerde
   `uygulandi: true`.
2. *Testler* (`test_fazla_mesai_once_sifir.py` 16 → 26): varsayılan açık;
   `False` ile önceki yol; koşul üç profilde tutuyor; eşitlik sınırı; en
   büyük ağırlığa bakıyor; fazla mesai değişkeni ya da öteki ceza yokken;
   ağırlık düşürülünce atlanıyor (varsayılandan da, açıkça istenince de);
   kapalıyken koşula bakılmıyor; **Mustafa'nın örneği** (hedef ağırlığı
   2.000: motor 3 saat fazla mesaili 9.000'lik planı seçiyor; kısayol zorla
   uygulanınca 16.000'lik plan dönüyor); aynı örnekte ürün ağırlıklarıyla
   fazla mesai yapılmıyor (72); ürün ağırlıklarında kısayolun planı tam
   modelin kanıtlı optimumuyla aynı puanda (iki sahne).
   `test_demir_secenekleri.py`: varsayılan satırı ve `_sinir_kapsami`ne bir
   satır.
3. *Mutasyon* (`mutasyon_kostur.py` 271 → 286; `fm_sifir` 29 → 44): üç eski
   çapa yeni koda taşındı (varsayılan mutasyonu tersine döndü), 15 yeni.
   Bütün çapalar tam bir kez eşleşiyor.
4. *Ölçüm aracı* (`kalite-olc.py`, `test_kalite_olc.py` 16 → 18): ürün hali
   yapılandırmaları seçeneği motorun varsayılanından alıyor; 16 kayıt
   yapılandırması açıkça kapalı; `fm_once_kapali`, `fm_once_kapali_kapsama`;
   koşu kaydında `once_fazla_mesaisiz`; satır, ağırlık koşulu tutmadığında da
   *"UYGULANMADI"* diyor; yeni yapılandırma eklenince sınıfını yazmaya
   zorlayan test.
5. *Şartname*: §6.7'ye *"Motor önce fazla mesaisiz plan arar"* alt bölümü
   (davranış tablosu, kur tablosu, koşul, bilinen sınırlar); §11.3
   `fazla_mesai_once_sifir` satırı; değişiklik 60.
6. *Kararlar*: K-61, K-62; K-30 ve K-50'ye yönlendirme notları; O-17'ye
   karar notu.

**Doğrulama (bulut, 2 çekirdek).**

| Ne | Sonuç |
|---|---|
| `09-motor` testleri, 41 dosya | **582 geçti** (≈95 sn) |
| `test_kalite_olc.py` | 18 geçti |
| Mutasyon, grup grup (286) | hepsi öldü, atlanan 0 — **toplam iddiası değil** (O-15) |
| Gerçekçi set bekçilerinin taklidi (0,1 ölçek, 110 sn) | fazla mesaisiz plan 0,5 sn'de; 0 sert; yayınlanabilir; asgari %100; donmuş günle yeniden planlama geçti |
| Koşul, gerçekçi sahnenin kurallarıyla | DENGELI (50 ≥ 9), KAPSAMA (50 ≥ 20), CALISAN (50 ≥ 8) — tutuyor |

Bulutta koşulamayan: gerçekçi set bekçilerinin kendisi (240 sn'lik çözüm,
komut sınırı 180 sn) ve tam ölçek.

**Kararlar (K-62).** Ekipler 285 / 145 / 70; iki işi yapabilen kişiler bütün
seviyelerde; gece 00:00–08:00 back office asgari 2. **Cevaplanmayan:** kaç
satışçı back office de yapabilsin — 30 varsayımıyla ilerleniyor, Mustafa'ya
söylendi.

**Sıradaki.** Mustafa: testler, gerçekçi set, tam mutasyon, DENETIM, commit
→ doğrulama ölçümü (`varsayilan`, 900 sn, üç koşu). Sonra merdivenin 1. ve 4.
seviyesi.

## 15 · 7 Ekim 01:00–03:30 — bağımsız inceleme: 00:45 sürümü ilkeyi çiğniyordu (O-18, bulgu 23); düzeltme

Bu pencerenin alışkanlığı: kod *"indi"* denmeden işi görmemiş ayrı ajanlara
inceletmek. 00:45'te önce *"indi"* yazıp sonra inceletmiştim — sıra yanlıştı
(O-18'in bekçilerinden biri). İki ajan (A ve B; kopya üzerinde, kodu
koşarak; 00:57'de başlatıldı) 02:09'da döndü. Ortak bulgu, kendi koşumla doğrulandı
(ajanların repro_min.py ve b3_s3_cesitleri.py betikleri — 03:05 kesintisinde
silindi, aynı sahneler `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/dogrula.py`'de; bulutta
0,6 sn ve birkaç saniye):

| Sahne (ürün ağırlıkları) | Tam model, kanıtlı optimum | 00:45 sürümü (ürün yolu) |
|---|---|---|
| S1: tek kişi, DENGELI, SAAT_DENGESI yumuşak; A = 7,5 sa net (Pzt–Cum), B = 7,75 sa (Cmt); 5A + B = 45 sa 15 dk | **750**, 15 dk fazla mesai | 2.256, 0 fazla mesai (bir A günü düşer: 435 dk × 5 + 9 hücre × 9) |
| F2: aynı kişi, KAPSAMA, SAAT_DENGESI sert; fazla mesaisiz tek dolum 15:00–01:00 (9 sa net), talebin dışında | **750** | 880 (44 hücre × 20) |
| S3b: 12 kişi, KAPSAMA, SAAT_DENGESI sert; ERKEN 04:00–12:30 talebin dışında; P9 × 4 + PL = 45 sa 15 dk | **9.000**, tam **3 saat** | 12.000 |
| S3c / S3d: iki ekibe üye tek kişi (K-50), DENGELI / KAPSAMA | **750** | 900 / 2.000 |
| S1 × 400 kişi (56.854 değişken; gerçekten iki aşamalı yol) | **300.000** | 902.400 |

Ajan A'nın rastgele avı: çeyrek saat ızgaralı karışık şablonlar + yumuşak
SAAT_DENGESI ile 8/400 karşı örnek; gerçekçi netlerle (7,5 / 9 / 4,25 sa; en
küçük adım 90 dk) 0/1.200. 500 kişilik sette en küçük şablon taşmaları 75 dk
(satış, back office), 30 dk (müşteri hizmetleri), 15 dk (40 saatlik sezonluk
kadro): orada oluştuğu gösterilmedi, oluşmayacağı kanıtlı değil.

**Neden yanlıştı.** Hesabım *"bir saat fazla mesai en çok bir-iki kişi-saat
kazandırır"* idi; fazla mesai çeyrek saatlik adımlarla gelir ve küçük bir adım
bütün haftanın düzenini açar (bir gün daha çalışmak, sözleşme saatini
doldurmak, talebin içindeki şablona geçmek, iki ekibi birden kapatmak).
Ağırlık koşulu bunu göremezdi; testim de tek şablonlu düz sahneyle yazılmıştı
(en küçük adım 3 saat). Tam metin: `05-HATA-OTOPSILERI.md` O-18.

**İncelemenin öteki bulguları** (hepsi ele alındı): küçük model ↔ büyük model
aynı girdide farklı karar (yol bağımlı politika — düzeltmeyle ikisi de
ağırlıklara göre); *"İyileştir"* yolu kısayolu hiç görmüyor (bilinen sınır
olarak yazıldı); koşul "daraltılacak alan var mı"dan önce (koşul kalktı);
`FAZLA_MESAI_TAVANI` yokken "bulundu" sayılan deneme `mola_adimi: False` ile
küresel kanıtı düşürüyor (alanlar açıldığı için model tam, kanıt küresel);
`int(ObjectiveValue())` kırpıyor (65154 ↔ 65155; `int(round())`, test);
başlık "≤ %20" (en kötü hâlde iki pay — düzeltildi); iyileştirme eğrisi
yazılmıyordu (eklendi, `ilk_asama_iyilestirme.iyilesme`); keşif OKU-BENI
*"devreden adalet yükü hepsinde 0"* yanlış (üretici 124 kişiye `devir_yuk`
yazıyor; boş olan geçen haftanın vardiyaları — düzeltildi); K-61 metnindeki
abartılar (*"öteki kalemler de iyileşti"*, *"%40 → %0,3"* yalnız DENGELI,
*"10 yeni"* 11, *"286 hepsi öldü"* grup sayılmadan — düzeltildi); `kalite-olc`
metinleri (`mola_adimi_tam` "= varsayılan", `ipucu_kapali` iki şey farklı,
"(alan yoksa … kapalı)" — düzeltildi).

**Mustafa'ya 02:35'te söylendi** (blok koşma; ne bulundu, neden yanlıştı,
ne yapılıyor).

**Düzeltme (02:35–03:05; 03:05'te kredi kesildi — §16).**

1. *Motor* (`coz.py`): bulununca `_fazla_mesaiyi_serbest_birak` — plan ipucu,
   alanlar açık, iyileştirme tam ağırlıklı amaçla o plandan; ağırlık koşulu ve
   `_fazla_mesai_kisayolu_gecerli` kaldırıldı; `fazla_mesai_sifirda_tut`
   (varsayılan False) 6 Ekim'in sert kesimini ölçüm için saklıyor; çıktıda
   `uygulandi` yerine `sifirda_tutuldu`; `_sinir_kapsami` yalnız sert kesimde
   *"fazla_mesaisiz"*; `_CozumSayaci` eğri tutuyor; amaç değeri
   `int(round())`. Not metni *"en aza indirilir"* demiyor (*"azaltmaya
   çalışır; en azı olduğu kanıtlı değildir"*).
2. *Testler* (`test_fazla_mesai_once_sifir.py` 26 → 27; 04:00'te 28, §16): bölüm 1 ürün yolu
   (alanlar geri açılır, ipucu fazla mesaisiz plan) + sert kesim ölçüm; 3b
   ürün yolunda küresel sınır yazılır, sert kesimde yazılmaz; bölüm 5 yeniden:
   Mustafa'nın örneği — fazla mesaisiz plan **bulunsa da** 3 saatlik plan
   seçiliyor, sert kesim 16.000 döndürüyor; dört karşı örnek sahnesi (beşincisi,
   iki ekibe üye kişi KAPSAMA, yalnız `dogrula.py`'de; tam
   model kanıtlı optimum = ürün yolu; sert kesim daha kötü); kanıtlı optimumla
   aynı puan (iki sahne); eğri; yuvarlama. `test_demir_secenekleri.py`
   `_sinir_kapsami`.
3. *Mutasyon* (`fm_sifir` 44 → 43; toplam 285; 04:00'te 44 / 286, §16): 15 koşul mutasyonu kalktı,
   sert kesim / geri açma / `sifirda_tutuldu` / eğri / yuvarlama mutasyonları
   geldi; çapaların hepsi tam bir kez eşleşiyor.
4. *Ölçüm aracı*: `fm_once`, `fm_once_kapsama` (ürün yolu), `fm_sert`,
   `fm_sert_kapsama` (6 Ekim gecesinin hâli); bulgu 21'in kayıt adları
   (`fm_once_sifir*`) sert kesime sabitlendi; kayıtta `sert_kesim`; satır
   iki hâli ayırıyor; `test_kalite_olc.py` 18 güncellendi.
5. *Kayıtlar*: şartname §6.7 yeniden yazıldı, §11.3 dört satır, değişiklik
   61 (60 üstü çizili notla); K-61 düzeltme bölümü ve üstü çizili cümleler;
   K-30 7 Ekim notu; O-18; T-60 bulgu 23 ve yeni "Sıradaki adım";
   BURADAN-BASLA 03:30 paragrafı ve T-60 satırı; değişim günlüğü; keşif
   OKU-BENI.

**Doğrulama (bulut, 2 çekirdek; asıl kapı Mustafa'nın koşuları).**

| Ne | Sonuç |
|---|---|
| Karşı örnekler, düzeltilmiş motor (`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/dogrula.py`) | beş sahnede ürün yolu = kanıtlı optimum (750 / 750 / 9.000 / 750 / 750); sert kesim 2.256 / 880 / 12.000 / 900 / 2.000 |
| `09-motor` testleri, 41 dosya | **583 geçti** (≈126 sn) |
| `test_kalite_olc.py` | 18 geçti |
| Mutasyon, grup grup | §16 (03:30'da koşu bitmeden *"aşağıda"* denmişti; koşu 03:05'te kredi uyarısıyla düştü); toplam iddiası tam koşudan sonra (O-15) |
| Küçük ölçekli ön ölçüm, 49 kişi, 20 sn, tek koşu | 6 Ekim öncesi 11.918 (3 sa) · sert kesim 2.758 (0) · **düzeltilmiş yol 2.713 (0)**; iyileştirme boyunca fazla mesai 0'da kaldı |

**Açık ürün sorusu.** K-30'un ilk satırı ile K-61'in ilkesi birbirini tam
örtmüyor; motor K-61'e göre yazıldı; Mustafa'ya soruldu (K-61'in düzeltme
bölümünde yazılı).

**Sıradaki.** Mustafa: testler, DENETIM, commit + push → tam mutasyon (damga
~~285~~ 286, §16) → bulgu 23 ölçümü (`fm_once,fm_once_kapsama`, 900 sn, üçer koşu; karar
kuralı K-61'de). Sonra K-62.

---

## 16 · 7 Ekim 03:05–04:30 — kredi kesintisi, yeniden uygulama, yeniden doğrulama; eşdeğer mutant; bulgu 24

**Ne oldu.** 03:05'te, §15'in son adımı olan iki bağımsız inceleme (düzeltilmiş
motor; kayıtlar) başlatılır başlatılmaz hesabın kredisi bitti (*"Fable
limit"*); ajanlar hiç koşmadı. 03:18'de Mustafa yeni oturumda devam etti:
*"son attığın git bloğunu koşmadım"*, 03:19: *"kredim bittiği için az önce
yaptığın 3 saati aşan çalışma boşa mı gitti?"* Durum sayıldı ve söylendi:

| Parça | Nerede | Durum |
|---|---|---|
| 23:44–00:45 K-61 kodu, testler, şartname, kararlar (13 dosya) | Mustafa'nın makinesi, commit edilmemiş | **kayıp yok** (`git status` 13 M; `coz.py` md5 `a90fe3da…` = 00:57'de incelemeye verilen hâl) |
| 00:57–02:35 iki bağımsız inceleme | raporlar oturum kaydında | **kayıp yok**; raporlar `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/inceleme/` altına kurtarıldı (betikleri ve logları silindi) |
| 02:35–03:05 düzeltme (motor, 27 test, 285 mutasyon, ölçüm aracı, şartname, O-18, K-61/K-30) | yalnız bulut çalışma alanı | **silindi** — oturumla birlikte sıfırlandı; Mustafa'nın makinesine kopyalanmamıştı |
| 03:05 son iki inceleme + mutasyon grup koşusu | — | hiç koşmadı |

**Yeniden uygulama (03:25–03:35).** Her düzenleme adımı oturum kaydında tam
metin duruyordu — 20 betik, hepsi *"şu metni şununla değiştir"* biçiminde
(`assert count == 1`). Mustafa'nın makinesinden 126 dosya buluta alındı
(00:45 sürümü), adımlar sırayla koşturuldu: 20'nin 20'si ilk denemede geçti. Çıkan
dosyalar 03:00'teki hâlle **birebir**: 14 dosyanın fark satır sayıları
(00:45 sürümüne göre) 03:00'teki ölçümle aynı — `coz.py` 311, test 567,
`mutasyon_kostur.py` 212, `kalite-olc.py` 140, `test_kalite_olc.py` 108,
şartname 188, K-61/K-30 241, O-18 114, T-60 146, BURADAN-BASLA 77, oturum
129, değişim 42, keşif OKU-BENI 24, `test_demir_secenekleri.py` 31.

**Yeniden doğrulama (bulut, 2 çekirdek).**

| Ne | Sonuç |
|---|---|
| Karşı örnekler (`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/dogrula.py`; log `loglar/` altında) | beş sahnede ürün yolu = kanıtlı optimum 750 / 750 / 9.000 / 750 / 750; sert kesim 2.256 / 880 / 12.000 / 900 / 2.000 (03:00 ile aynı) |
| `09-motor` testleri | **583 geçti** (151 sn) |
| gerçekçi set testleri | **39 geçti** (619 sn) |
| v5 altın senaryolar | 7 kırmızı — hepsi *"MOTOR ADRESI TANIMLI DEGIL"* (servis yok; bu değişiklikle ilgisiz) |
| mutasyon grupları | `demir` 40'ın 40'ı · `ilk_asama` 6/6 · `kalite` 6/6 öldü; **`fm_sifir` 43'ün 1'i yaşadı** (aşağıda) |
| 49 kişi, 20 sn, ikişer koşu | 6 Ekim öncesi 19.423 / 15.606 (5,5 / 4,25 sa); sert kesim ve düzeltilmiş yol **plan döndürmedi** (`sure_yetmedi`) — bulgu 24 |
| 49 kişi, 30 sn, ikişer koşu | 6 Ekim öncesi 15.478 / 15.469 (4,25 sa); sert kesim 2.717 / 2.719 (0); **düzeltilmiş yol 2.722 / 2.689 (0)**; iyileştirme ipucudan (11.792) başladı, fazla mesaiye dönmedi; fark ±%1,1 |

**Eşdeğer mutant (04:00).** Yaşayan: *"O-18: geri açma yerine ipucu silinsin"*
— `ClearHints`i `_fazla_mesaiyi_serbest_birak`in ardına koyuyordu; ipucu o
noktada **henüz yazılmamış** (`_tam_ipucu_yaz` 26 satır sonra), yani mutasyon
davranışı değiştirmiyordu. 03:30'da kayıtlara *"grup koşularında hepsi öldü"*
yazılmıştı — koşu bitmeden (O-15'in aynısı; üstü çizildi, bu bölüm yazıldı).
Düzeltme: (1) mutasyon ipucu **yazıldıktan sonra** siliyor; (2) ikinci
mutasyon ipucunun `fm_*` değerlerini siliyor (yarım ipucu — T-60 1 Ekim'in
tuzağı); (3) yeni test
`test_bulunan_fazla_mesaisiz_plan_iyilestirmeye_TAM_IPUCU_olarak_gider_fm_SIFIR`
iyileştirme aramasına giren modelin ipucusunu doğrudan okuyor: bütün
değişkenler yazılı, `fm_*` değerleri 0, alanlar `[0, 600]` (açık). İki
mutasyon elle uygulandı, test kırmızı; özgün kodda yeşil. Çapa kontrolü: 286
mutasyonun hepsi tam bir kez eşleşiyor. `fm_sifir` yeniden koşu: **44'ün 44'ü öldü, atlanan 0** (04:14, bulut).
Ders (O-15 + O-18 bekçisi): *"hepsi öldü"* ve *"aşağıda"* koşu bitmeden
yazılmaz — bu kez yazıldı ve yanlış çıktı.

**Bulgu 24 (yan bulgu).** 20 sn / 49 kişi: birinci aşama 17,7 sn (fazla
mesaisiz arama 1,3 + iyileştirme 16,0), mola adımına 2,3 sn kaldı, adım ilk
çözümünü bulamadı → `sure_yetmedi`, **plan yok** — elde iyileştirmenin planı
(3.936 / 4.032; fazla mesai 0; molalar şablonun ideal yerinde = tam modelin
geçerli çözümü) varken. 6 Ekim öncesinin yolu aynı bütçede döndürdü (birinci
aşaması 0,5 sn kısa). `_ipucu_ver`in *"bütçe dolsa bile çıktı boş kalmaz"*
cümlesi mola adımı için tutmuyor. 500 kişi / 900 sn'de görülmedi (adıma ~700
sn kalıyor, ~45 sn sürüyor). Karar Mustafa'da (açık listedeki *"mola adımı
yetişmezse plan notla dönsün mü"*); önerim: dönsün. Kod değişmedi. Kozmetik:
doğrulayıcının `fazla_mesai_saat`i 0 yerine `5,7e-14` yazabiliyor (kayan
nokta); motorun metriği 0 — `== 0` kıyaslayan testler için tuzak, not edildi.

**Bağımsız inceleme (04:10–04:45).** 03:05'te düşen iki inceleme aynı
istemlerle yeniden başlatıldı (A: düzeltilmiş motor — fark, karşı örnek avı,
mutasyon elle; B: kayıtlar — her sayısal iddia kanıtına). Raporlar ve betikler
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/inceleme/ajan-a/RAPOR.md`, `ajan-b/RAPOR.md` (kalıcı özet burada).

*A — motor.* **Düzeltme ilkeyi sağlıyor.** Kod okuması: bulununca
`sifirda=False` → alanlar geri açılır → `_tam_ipucu_yaz` (bütün değişkenler,
fm = 0; `fazla ≥ dakika − tavan` yalnız alt sınır olduğundan açık alanda
geçerli) → iyileştirme tam amaç → `finally` mola + amaç → `_atamalari_sabitle`
yalnız x → mola adımı fm serbest; kaçırılmış yol yok. Karşı örnekler iki
bağımsız koşuda aynı. **Av: 647 kayıt, 640 kıyas (7 kanıtsız atlandı), ürün
yolu = kanıtlı optimum 640'ın 640'ı**; optimumda fazla mesai olan 127 sahnenin
50'si tam hedef sınıfta (fazla mesaisiz plan var, optimum fazla mesaili) —
50'nin 50'si eşit; dikkat: rastgele üretici ilk 240 sahnede hedef sınıfı hiç
üretmedi, S1 yapısının genellemesi (`kilit2`) gerekti. Bulgular: (1) eklediğim
*"yarım ipucu"* mutasyonu `del vars[:]` ile protobuf'ta çöküyordu —
*"öldü"* sanılan şey çökmeydi → `.clear()`; (2) **mola adımına giden ipucu
denetlenmiyordu** — fm ipuçları hep 0 yazılsa ya da iyileştirmeden sonra
silinse (yarım ipucu: T-60 1 Ekim'in *"onarım → ilk plan 57–101 sn"* riski
mola adımına taşınır) 28 test görmüyordu → yeni test
`test_mola_adimina_giden_ipucu_TAM_ve_fazla_mesai_degerleri_iyilestirmenin_planindan`
(Mustafa'nın örneğinde ana aramaya giren ipucu tam, fm toplamı 180 dk) + iki
mutasyon; (3) 20 sn `sure_yetmedi` düzeltmeden bağımsız ve önceden var
(00:45 sürümünde de; kaynak %80 payı) — bulgu 24 doğrulandı; (4) ölçüm aracı
00:45 sürümünün `uygulandi: False` kaydında `KeyError` → `.get` + test;
(5) eşitlikte fazla mesaili plan seçilebiliyor (640'ta 1: 3.252 = 3.252, ürün
yolu 0,5 sa fazla mesaili) — *"belirgin daha iyiyse"* ilkesi eşitlikte
fazla mesaisizi tercih etmiyor, **tasarım notu Mustafa'ya**; (6) `_ipucu_ver`
O-16 yorumu ve `kalite-olc.py` yorumu eski hâli anlatıyordu → düzeltildi;
(7) `_sinir_kapsami` sırası mutantı fm dosyasında yaşıyor, demir dosyası
öldürüyor (yeterli). Elle uygulanan 14 mutant: 11 kırmızı, 3 yaşayan → ikisi
test + mutasyonla kapatıldı, üçüncüsü başka dosyada ölüyor.

*B — kayıtlar.* **Büyük ölçüde güvenilir**: beş karşı örnek puanı yeniden
üretildi; test/mutasyon sayıları loglarla tutuyor; 49 kişilik tekrarlar ve
bulgu 24'ün sayıları `duman-49*.jsonl` ile birebir; düzeltilmiş yol için 500
kişilik iddia yok; §6.7 ↔ `_ipucu_ver`, §11.3 anahtarları birebir; kesinti
anlatımı dürüst. Düzeltilenler: (1) *"500 kişi/900 sn'de mola adımına ~700
sn kalıyor"* **yanlış** — iyileştirme payı 720 sn, bulgu 21'in tablosu toplam
773–795 sn, mola adımına ~170 sn kalır (sonuç tutar, sayı yanlıştı; ölçmeden
yazılmış bir sayı — O-18/O-15 bekçisine aykırı); (2) T-60 öncelik tablosu
satırı ve BURADAN-BASLA T-60 satırı 04:30'a işlenmemişti; (3) *"birebir"*
kanıtından güçlü (03:00 dosyaları silindi, md5 yok; dayanak adımların
belirli olması ve 14 fark satır sayısı) → zayıflatıldı; 2.713 / 2.758 /
11.918'in logu yok, kaynağı oturum kaydı → yazıldı; ×400 ve 8/400, 0/1.200
yalnız ilk inceleme raporunda; *"dört sahne test"* derken tablo beş satır
(S3d yalnız betikte) → yazıldı; 75/30/15 dk yöntemi kayıtlı değil, B yeniden
üretemedi → işaretlendi; (4) *"CP-SAT ipucuyu ilk çözüm olarak alır"*: sekiz
koşuda iyileştirmenin **ilk** çözümü ipucudan iyiydi (9.398 < 11.792; ipucunun
ceza değişkenleri gevşek) — mikro deney (OR-Tools 9.15): sıkı tam ipucu → ilk
çözüm = ipucu, gevşek → daha iyi; belgelenmiş garanti değil ve kötü dönerse
koruma yoktu → **ipucu koruması** eklendi (`_ilk_asamada_iyilestir`:
`iyilesmis_amac > amacsiz_amac` ise ipucu ezilmez, `ipucu_korundu: True`;
test + iki mutasyon); (5) zaman çizelgesi (01:00 ↔ 02:09; 02:40 ↔ 02:35)
düzeltildi; alıntıdaki *"var var"* O-18 ve şartnamede sessizce düzeltilmişti
→ birebir yapıldı; (6) **K-30 ↔ K-61 çelişkisi yeni değil** — K-30 kodda
hiçbir zaman sert kural olmadı (*"kod değişmedi"*), 6 Ekim öncesinin yolu da
12 kişilik örnekte fazla mesaili optimumu seçiyordu; onu sert kurala çeviren
6 Ekim gecesinin sert kesimiydi; *"artık sert kural değil"* yanıltıcıydı →
düzeltildi; S1 sahnesi K-30 ilk satırının örneği değil (sözleşme doldurma);
(7) BURADAN-BASLA'da açıklanmamış kodlar (O-15, eşdeğer mutant, harnes, md5)
→ açıklandı; O-18 bekçileri (2) ve (4) *"otomatik bekçisi yok"* diye
işaretlendi; (8) arşivdeki ilk inceleme raporlarının dosya adları çaprazdı →
düzeltildi. Doğrulanamayanlar (B): 2.713/2.758/11.918 (log yok), ×400,
8/400, 0/1.200, 75/30/15 dk yöntemi, *"birebir"* içerik eşitliği.

**Son durum (05:00).** `test_fazla_mesai_once_sifir.py` **31**; `09-motor`
**587 test** (bulut); mutasyon **290** (`fm_sifir` 48; bulut grup koşuları
`fm_sifir` 48'in 48'i, `ilk_asama` 6/6 — 04:52; `demir` 40'ın 40'ı, `kalite` 6/6 —
04:00); `test_kalite_olc.py` 18. Toplam iddiası tam koşudan sonra (O-15).
Mustafa'ya: koşular, bulgu 23 ölçümü, iki karar (K-30 ilk satırı; bulgu 24),
bir tasarım notu (eşitlikte fazla mesaisiz tercih edilsin mi).
