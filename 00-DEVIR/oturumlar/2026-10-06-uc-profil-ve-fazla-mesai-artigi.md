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
