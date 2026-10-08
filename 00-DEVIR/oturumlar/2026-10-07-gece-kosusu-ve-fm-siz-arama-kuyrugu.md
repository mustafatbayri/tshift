# 7 Ekim 2026 (gündüz) — gece koşusunun okunması; bulgu 25: fazla mesaisiz ilk aramanın kuyruğu; yeniden başlatma + K-63 koda; K-61 kapanışı (8 Ekim sabahı)

**Pencere:** 7 Ekim 17:28 – 8 Ekim 06:30+ (sürüyor) · **Önceki:** `2026-10-06-uc-profil-ve-fazla-mesai-artigi.md`
§15–17 (O-18 düzeltmesi, kredi kesintisi, bulgu 23–24, K-63/K-64). ~~**Bu
pencerede kod değişmedi.**~~ *(18:31'den sonra değişti — §6; 8 Ekim sabahı
varsayılan 3 — §9.)*

## İçindekiler

1. [Gece koşusunun sonucu](#1--gece-koşusunun-sonucu)
2. [Bulgu 25 — fazla mesaisiz ilk aramanın kuyruğu](#2--bulgu-25--fazla-mesaisiz-ilk-aramanın-kuyruğu)
3. [Kuyruk ölçümü aracı ve karar kuralı](#3--kuyruk-ölçümü-aracı-ve-karar-kuralı)
4. [Sıradaki](#4--sıradaki)
5. [Kuyruk ölçümünün sonucu (18:00)](#5--kuyruk-ölçümünün-sonucu-1800)
6. [Sıra onaylandı; yeniden başlatma + K-63 koda indi (18:31–20:30)](#6--sıra-onaylandı-yeniden-başlatma--k-63-koda-indi-18312030)
7. [Bağımsız inceleme 3 ve düzeltmeler; O-19](#7--bağımsız-inceleme-3-ve-düzeltmeler-o-19)
8. [Mustafa'ya blok ve sıradaki](#8--mustafaya-blok-ve-sıradaki)
9. [Gece koşusunun sonucu: karar kuralı tuttu — varsayılan 3, K-61 kapandı; brifing v3 (8 Ekim 00:10–05:45)](#9--gece-koşusunun-sonucu-karar-kuralı-tuttu--varsayılan-3-k-61-kapandı-brifing-v3-8-ekim-00100545)

## 1 · Gece koşusunun sonucu

Mustafa 07:40'ta kapanış commit'ini ve gece koşusunu başlattı; 17:28'de
çıktıyı attı (`kalite-olcumu-95-fmsert-kapsama-900.json`,
`kalite-olcumu-95-fmonce-1200.json`). Karar kuralları koşudan önce T-60'a
yazılmıştı; okuma oraya göre:

| Koşu | Sonuç | Okuma |
|---|---|---|
| `fm_sert_kapsama` 900 × 3 | 13.638 · 13.983 · 13.623; fazla mesai 0 | bulgu 21 (13.834–13.914) ±%2'de → taban aynı, sert kesim seçeneği bugünkü kodda bulgu 21'i yeniden üretiyor |
| `fm_once_kapsama` 1200 × 3 | 14.041 · 13.773 · 14.418; fazla mesai 0 | bulgu 21 ort.'a göre +1,3 · −0,7 · +4,0 (**+%1,5**); 900 sn'de +%5,2 idi → farkın büyük kısmı **bütçe**; yayılım %4,7 kalıyor |
| `fm_once` (DENGELI) 1200 × 3 | 26.602 · 26.823 · **116.976** | ilk ikisi 900 sn ile aynı düzey (fazla süre kazandırmıyor); üçüncüsü **bulgu 25** |

Hibrit hâlâ aday (dar yayılım için) ama önceliği düştü; K-63'ün 20 dk üst
ucu KAPSAMA'yı tek başına sert düzeyine getiriyor.

## 2 · Bulgu 25 — fazla mesaisiz ilk aramanın kuyruğu

Üçüncü DENGELI koşusunda birinci aşamanın fazla mesaisiz uygunluk araması
120 sn'lik payını doldurdu, plan bulamadı (süre yetmedi; imkânsızlık kanıtı
değil). Motor tasarlandığı gibi davrandı: alanları açtı, serbest arama hemen
plan buldu (amaçsız 2.688.191), iyileştirme 845 sn'de 132.551'e indi (sabit
molalı sınırı 41.662'nin 3,2 katı), mola adımı 116.976 — **30 saat fazla
mesai, 24 kişi**; fazla mesai dışı kalemler ötekilerle aynı. Çıktı notu düştü,
ölçüm satırı gösterdi. Bu, bulgu 20'nin artığının ta kendisi.

Dağılım (6 Ekim'den beri bu aramanın süresi, 18 koşu): 8,6 · 8,8 · 8,8 · 8,8 ·
8,9 · 9,0 · 9,0 · 9,1 · 9,3 · 9,5 · 9,5 · 9,5 · 9,8 · 10,0 · 12,2 · 12,7 · 21,1
sn ve **1 × > 120 sn**. Tek olay, ama ürün yolunun kalitesi bu aramaya bağlı:
**K-61 kuyruk kapanmadan "kapandı" denmez.** 1200 sn bütçe payı
büyütmüyor (`_ilk_asama_payi` = min(120, %20)).

## 3 · Kuyruk ölçümü aracı ve karar kuralı

`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-fm-siz-arama-kuyrugu/kuyruk.py` (+ OKU-BENI): 500 kişilik modeli bir kez kurar,
birinci aşamayı motorun kendi yardımcılarıyla aynen hazırlar (amaç silinir,
`_molalari_sabitle`, `_fazla_mesaiyi_sifirla`), aynı modeli 30 tohum + 5 ×
tohum 0 ile 120 sn tavanla çözer; süre dağılımı, P(T > 20/40/60/120) ve
yeniden başlatma politikalarının (2 × 60, 3 × 40, 4 × 30) offline tahmini.
Bulutta 49 kişiyle uçtan uca denendi (hazırlık ve döngü çalışıyor; sayılar
anlamsız). Karar kuralı koşudan önce OKU-BENI'ye yazıldı: kuyruk gerçekse
yeniden başlatma motorda ölçüm seçeneği → 900 sn × 3 → varsayılan; değilse
yine yazılır (ucuz sigorta), öncelik hibrite döner.

## 4 · Sıradaki

(1) `kuyruk.py` koşusu (Mustafa, ~15–25 dk) → politika; (2) K-63 (süre
aralığı; mola adımı yetişmezse plan) ve K-64 kod; (3) hibrit KAPSAMA; (4)
K-62 merdiven kadrosu (20 satışçı BO, gece BO ≥ 2).

## 5 · Kuyruk ölçümünün sonucu (18:00)

Mustafa `kuyruk.py --deneme 30 --tavan 120 --sifir-tekrar 5` koşturdu (kurma
53 sn; 633.591 değişken; 529.480 mola adayı kapalı; 359 fazla mesai değişkeni
[0,0]; 6 işçi). **35 denemenin hepsi buldu**; medyan 7,5 sn, %90 13,0 sn, en
uzun 61,9 sn; P(T > 10/20/40/60/120) = 9/35 · 2/35 · 2/35 · 1/35 · 0/35. Tohum
0'ın beş tekrarı 13,0 · 55,9 · 12,2 · 7,9 · 7,8 sn — rastgelelik tohumdan
değil, paralel işçilerin zamanlamasından (aynı tohumda 7× fark). *(O-19,
18:40: tohum 0'a "motorun tohumu" denmişti; motorun tohumu CP-SAT'in
varsayılanı **1**'dir — sonuç değişmez, etiket düzeltildi; §7.)*

Karar kuralı (OKU-BENI, koşudan önce): P(T > 120) ≈ 0 ve %90 < 40 sn → ilk
dal. Toplamda (6 Ekim'den beri 18 ürün/sert koşusu + 35 deneme = 53 gözlem)
1 × > 120 sn, 2 × 56–62 sn, 1 × 21 sn. Kuyruk ince ama gerçek; tek denemeyle
120 sn'de kalma ~%2 ve bedeli 30 saat fazla mesaili plan. Çare ucuz: **120
sn'lik payı 3 × 40 sn'lik denemeye bölmek**, her deneme farklı tohumla
(offline tahmin: başarısızlık 0,057³ ≈ %0,02; bağımsızlık varsayımı, motorda
doğrulanacak). Tipik koşu (7,5 sn) etkilenmez. Çıktıya denemelerin
süresi/durumu eklenir.

**Plan:** motorda ölçüm seçeneği `fazla_mesaisiz_deneme` (varsayılan 1 =
bugünkü davranış; ölçümde 3) + testler + mutasyonlar → `fm_once` 900 sn × 3 →
varsayılan 3 → K-61 kapanır. Sırası Mustafa'nın sıralama cevabına göre
(18:03'te sorulan: kalibrasyonları dondurma; dört kural + veri seti).

## 6 · Sıra onaylandı; yeniden başlatma + K-63 koda indi (18:31–20:30)

**18:03–18:31.** Mustafa: *"eksik kalan kriterleri ne zaman ekleyeceğiz,
sanki onları eklemeden yaptığımız testler zaman kaybı gibi…"* — cevap: dört
yumuşak kural (EKIP_SUREKLILIGI, PLAN_KARARLILIGI, TERCIH_KARSILAMA,
VARDIYA_ROTASYON_YONU) ve veri seti v2 (K-62) olmadan kalibrasyon ölçümleri
(hibrit, %80→%90, K-64) tekrar gerekir; o yüzden kalibrasyonlar **dondu**,
bulgu 25 ise ölçümden bağımsız bir ürün sorunu (30 saat fazla mesaili plan).
Önerilen sıra onaylandı (*"önerdiğin sıraya katılıyorum"*, 18:31 *"başla"*):
(1) yeniden başlatma + K-63; (2) kalibrasyonlar dondu; (3) dört yumuşak kural
(motor + doğrulayıcı + test + mutasyon; tanım soruları tek tek); (4) veri seti
v2; (5) merdiven ölçümleri; K-64 (3)'ten sonra.

**Kod (bulut, 18:35–19:45).** `09-motor/cozucu/coz.py`:
- `VARSAYILAN["fazla_mesaisiz_deneme"] = 1`; `_deneme_siniri`,
  `_fazla_mesaisiz_ara(kuruldu, ayar, pay)` — pay N parçaya, tohum `i + 1`
  (1 = CP-SAT varsayılanı; **buradayken O-19 görüldü**, §7), ilk bulunan
  alınır, INFEASIBLE kanıt sayılır; `_ipucu_ver` fazla mesaisiz aramayı bu
  fonksiyona verir, `fazla_mesai_once_sifir`'a `deneme_siniri` + `denemeler`
  yazar, not *"(N denemede)"* der; `saniye` bütün denemelerin toplamı
  (`deneme_sn`), başarısızsa iyileştirmeden düşer.
- K-63: `coz()` ana aşama UNKNOWN + `iki_asama` → `_ipucu_planini_al`
  (ilk sürüm: `fix_variables_to_their_hinted_value`, 1 işçi, tavan
  `ipucu_plani_saniye` 30) → plan + not + `durma_sebebi:
  mola_adimi_yetismedi` / `ana_asama_yetismedi`, `sinir None`, çıktıda
  `ipucu_plani`; `optimuma_uzaklik_yuzde` None.
- Testler: bölüm 7 (7 test: varsayılan tek deneme/tohum 1, üç deneme
  pay/3 + tohumlar, hepsi UNKNOWN → not + süre düşer, INFEASIBLE kalanları
  durdurur, parçalar/taban, geçersiz sayı → 1, ürün çıktısı);
  `test_mola_adimi_yetismedi.py` (10: yol, ortak arama, paralel, eşik altı,
  başlangıç planı, yarım ipucu, INFEASIBLE K-37, geçersiz ipucu, parametreler,
  olağan yol). Mutasyon: `fm_sifir` +11, yeni grup `k63` 16. Bulutta
  `k63` 16'nın 16'sı, `fm_sifir` 59'un 58'i öldü + 1 **ATLANDI** (çapa eskimişti —
  düzeltildi, tek başına koşuldu: öldü); tam takım 604; `butce` 4/4, `demir`
  40'ın 40'ı, `ilk_asama` 6'nın 6'sı, `kalite` 6'nın 6'sı, `sure_yetmedi` 5'in 5'i (üç eskimiş çapa
  düzeltildi).
- Ölçüm araçları: kalite-olc `fm_once_deneme3` / `_kapsama` (+ `ipucu_plani`
  satırı, test listesi); `kuyruk.py --politika N` (motorun kendi
  `_fazla_mesaisiz_ara`sı N kez), `--tekrar-tohum`; 0.1 ölçekte duman.
- Şartname §6.7 (bulgu 25 + yeni alt bölüm K-63), §11.3 (`durma_sebebi`,
  `denemeler`, `ipucu_plani`), değişiklik 63.

**18:52 — Mustafa:** yarın akşam mimar arkadaşı Yılmaz'la görüşecek; proje
özeti + gelinen nokta + eksikler + destek alınacak yerler + yorumunu
istediğimiz konular için bir çıktı istedi. **19:48:** spora gitti (1,5 saat);
onay gerektirmeyen işler sürsün, makinede koşacak bir şey varsa atılsın.

## 7 · Bağımsız inceleme 3 ve düzeltmeler; O-19

**O-19 (18:40).** `_fazla_mesaisiz_ara`'yı yazarken varsayılanı okudum:
`CpSolver().parameters.random_seed` → **1**. Kuyruk aracında, OKU-BENI'de,
bulgu 25 tablosunda ve bu kaydın §5'inde *"tohum 0 = motorun kullandığı değer
(CP-SAT varsayılanı)"* yazmıştım — hafızadan. Ölçümün sonucu değişmedi (aynı
tohumda 7× fark; motorun tohumu 30'un içinde bir kez), etiketi yanlıştı.
Düzeltildi (araç, OKU-BENI, bulgu 25 üstü çizili, §5'e not), test + mutasyon
tohumu çiviliyor. `05-HATA-OTOPSILERI.md` O-19.

**İnceleme 3 (19:05–19:45; ayrı ajan, kodu görmemiş; rapor + deney
betikleri `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-inceleme3-yeniden-baslatma-k63/`).**
Karar: *koda inmeye hazır, bloklayıcı yok.* Ölçtükleri: tohum yazılmamış ≡
tohum 1 (aynı çözüm vektörü, dal/çatışma), ardışık Solve model durumunu
değiştirmiyor, bütçe uçtan uca tutuyor (azami 10/5/30 × deneme 1/3), ipucu
her yolda tam ve geçerli, sabitleme ipucuyla birebir (123.935 değişkende 0
fark), çevirme 0.1'de 0,33 sn / 0.2'de 0,7–0,8 sn, 0.2 ölçekte 20 sn doğal
koşuda bulgu 24 kendiliğinden oluştu ve K-63 plan döndürdü (doğrulayıcı
yayınlanabilir). Bulduğu ve **aynı akşam işlenen** düzeltmeler:
- **B6 (düzeltilmeli):** `fix_variables_to_their_hinted_value` ipucunun
  **gevşek ceza değerlerini** aynen alıyordu — ikinci aşamanın planında
  +%1,2, birinci aşamanın amaçsız planında **+%85–89** (0.1–0.2 ölçek,
  tamamı `me_`). K-35 kartı planları `amac_degeri` ile kıyaslıyor. Düzeltme:
  `_ipucu_planini_al` yalnız **karar değişkenlerini** (x, mola, dinlenme)
  ipucuya sabitler, cezaları amaç sıkar (inceleme prototipi 0,63 sn, amaç =
  alt sınır, karar değişkenlerinde 0 fark). Test: *"ceza değerleri gevşekse
  amaç yine sıkı"* (fm ipucusu 0 → 600: eski 30.360, yeni 360).
- **B7:** iyileştirme plan bulamadıysa / ipucu korunduysa dönen plan birinci
  aşamanın amaçsız planıdır; not *"ikinci aşamanın planı"* diyordu →
  `_ipucu_kaynagi`, `ipucu_plani.kaynak`, not üç hâli ayırır; `ilk_asama_sabit_mola`
  kapalıysa *"şablonun ideal yerinde"* de denmez; iki test.
- **B4:** 1 sn tabanı tek denemede de uygulanıyordu (azami < 5 sn'de 0,8 →
  1,0): `parca = pay if adet == 1 else max(1, pay/adet)`; test + mutasyon.
- **B10:** test edilmeyen iddialar → üç test: not sınırı (*"(1 denemede)"*
  sızmasın), çevirme süresi `cozum_suresi_sn`'ye girmez, uçtan uca 3 deneme
  bütçe (gerçek uyku). Mutasyonlar: `fm_sifir` 61, `k63` 22 (toplam 325).
- **B1 (süreç):** inceleme paketine kopyaladığım `coz.py` **mutant anlık
  görüntüydü** — grup koşusu sürerken ağaçtan kopya almıştım (koşturucu
  dosyayı yerinde değiştirip geri yazıyor); inceleyici bunu fark edip
  dondurulmuş kopya aldı ve diff ile doğruladı. **Ders:** mutasyon koşusu
  sürerken aynı ağaçtan kopya alınmaz, test koşturulmaz; son doğrulama
  (takım + gruplar) koşu bittikten sonra, temiz ağaçta. Bu akşam öyle
  yapıldı (§8).
- **B11:** `deneme` (süre) → `deneme_sn`; `VARSAYILAN` yorumundaki *"tipik
  olarak 1 sn'nin altında"* ölçüme bağlandı (0.2'de 0,6–0,8 sn; tam ölçek
  ölçülmedi, dışdeğerleme ~4 sn).
- **B9:** K-63 çıktısında `durum: cozuldu` + `cozum_sayisi: 0` +
  `cozum_suresi_sn` = plansız ana aşamanın süresi — spec §11.3'e yazıldı.
- **B12 (bitişik, kapsam dışı):** T-60 **bulgu 26** (`ipucu_korundu` kıyası
  gevşek `amacsiz_amac` ile — aynı sıkılaştırma çaresi; ürün yoluna ~0,5–4
  sn ekler, **karar Mustafa'da**), **bulgu 27** (donmuş gün × iki aşama:
  `_molalari_serbest_birak` donmuş günün mola alanlarını `[0,1]`e açıyor,
  48 alan; görünür etki ölçülmedi; **sırada**).

## 8 · Mustafa'ya blok ve sıradaki

Düzeltmelerden sonra temiz ağaçta (hiçbir koşu sürmezken): tam takım **609**
(587 + bölüm 7'nin 8'i + K-63'ün 14'ü); mutasyon grupları `k63` 22'nin 22'si,
`fm_sifir` 61, `butce` 4, `demir` 40 (sonuçlar aşağıda, koşu bittikçe);
`08-motor-testleri/gercekci-veri-seti/testler` 41. Dosyalar Mustafa'nın
makinesine taze adlarla yazıldı, md5 geri okundu (O-13), DENETIM 0 HATA.
Blok (Mustafa döndüğünde): testler → DENETIM → commit → tam mutasyon (damga)
→ `fm_once_deneme3` 900 sn × 3 → `kuyruk.py --politika 3 --deneme 20`.
**Karar kuralı koşudan önce** (T-60 bulgu 25 *"Koda indi"* paragrafı):
üç koşuda fazla mesai 0 ve amaç `fm_once` düzeyinde (26,6–26,8 bin), hiçbiri
*"bulunamadı"* yoluna düşmemiş; politika kipinde 20'de 0 bulunamayan →
**varsayılan 3, K-61 kapanır**; bir koşu bile düşerse 4 × 30 ölçülür.
Sonra sıranın 3. maddesi: dört yumuşak kural — şartnameden okunarak, tanım
soruları tek tek. Yılmaz brifingi ayrı dosya (`00-DEVIR/brifing/`).
## 9 · Gece koşusunun sonucu: karar kuralı tuttu — varsayılan 3, K-61 kapandı; brifing v3 (8 Ekim 00:10–05:45)

**Mustafa'nın koşusu (7 Ekim akşamı → gece; çıktı 00:10 dolayında okundu).**
Blok sırayla geçti: 609 + 41 test, DENETIM 0 HATA, commit `34a386b` push;
**tam mutasyon 325'in hepsi öldü, atlanan 0** (damga 22:15,
`09-motor/mutasyon-tam-kosu.txt`); `fm_once_deneme3` 900 sn × 3
(`08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-fmonce-deneme3-900.json`);
politika kipi (`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-fm-siz-arama-kuyrugu/politika-3x40.jsonl`).
Sayılar T-60 bulgu 25'teki *"Ölçüldü"* tablosunda; özeti: amaç **26.498 /
26.700 / 26.736** (tek denemeli yolun 7 Ekim ölçümü 26.634–26.705 — aynı
düzey), fazla mesai üçünde **0**, 0 sert, hepsi yayınlanabilir, hedef kapsama
%85,3–86,0, fazla mesaisiz arama üçünde de **ilk denemede** (6,73–7,34 sn),
mola adımı optimum (772–775 sn); politika kipi **20 koşunun 20'si ilk
denemede**, 6,48–8,37 sn, medyan 6,6 sn, 2+ deneme gereken 0. Koşudan önce
yazılı kuralın (§8) her şartı sağlandı → **varsayılan 3, K-61 kapandı**
(00:10; 08-URUN-KARARLARI K-61 başlığı, T-60 bulgu 25, şartname değişiklik 64).

**Dürüst okuma.** Yeniden başlatma bu 23 koşunun **hiçbirinde devreye
girmedi**. Politika kipinin her koşusu ürün yolu gibi tohum 1'le başlar; yani
o 20 koşu ürünün *ilk denemesinin* 20 tekrarıdır ve yayılımı 1,3× çıktı
(6,5–8,4 sn) — 18:00 ölçümünde aynı tohumun (0) beş tekrarı 7× yayılmıştı
(7,8–55,9 sn). Seçeneğin **zararsız** olduğu ölçüldü (puan, süre, fazla mesai
tek denemeli yolla aynı); **koruma değeri gözlemlenmedi**, 18:00 kuyruk
ölçümüne (53 gözlemde 1 × > 120 sn, 2 × 56–62 sn) ve çevrimdışı tahmine
dayanıyor. Ürün koşularının `fazla_mesai_once_sifir.denemeler` alanı okunmaya
devam eder; ilk denemede bulunamayan ilk koşu T-60'a yazılır — politika o
zaman gerçekten sınanmış olur.

**Kod (bulut, 04:10–05:30).**
- `09-motor/cozucu/coz.py`: `VARSAYILAN["fazla_mesaisiz_deneme"] = 3`
  (yorumu ölçümle; 1 = tek deneme, payın tamamı — 7 Ekim sabahının yolu,
  ölçüm/kıyas). Başka kod değişmedi.
- `09-motor/testler/test_fazla_mesai_once_sifir.py` bölüm 7 yeniden yazıldı:
  *varsayılan 3 — pay üçe bölünür, tohum 1'le başlar*; *tek deneme seçeneği —
  payın tamamı, tohum 1*; parçalar (varsayılan → 3 × 2,0; seçenek 1 → (6,0, 1)
  ve (0,8, 1); 2 → [1,0, 1,0]); ürün yolu çıktısında `deneme_siniri` 3, ilk
  denemede bulunur; `UZUN` ve *"süreye takılırsa"* testi tek denemeli (notta
  *"denemede"* geçmez). Dosya 40 test.
- `09-motor/mutasyon_kostur.py`: `fm_sifir` +2 — *"varsayılan tek deneme
  olsun"*, *"varsayılan 2 deneme olsun"* (ikisi de öldü: 3 test düşüyor) →
  `fm_sifir` 63, toplam **327**.
- `kalite-olc.py`: `fm_once` / `fm_once_kapsama` **tek denemeye sabit**
  (`fazla_mesaisiz_deneme: 1` — bulgu 23'ün kaydı, 7 Ekim sabahının yolu);
  `fm_once_deneme3` / `_kapsama` açıkça 3 (= bugünkü varsayılan);
  `varsayilan` / `profil_*` motoru izler. `test_kalite_olc.py` 20 (yapılandırma
  kümesi, `COZ_VARSAYILAN` 3, `etkin_ayar` 3 / 1).
- Bulutta, koşu bittikten sonra temiz ağaçta okundu: tam takım **610**;
  `fm_sifir` 63'ün 63'ü, `k63` 22'nin 22'si, `butce` 4'ün 4'ü öldü, atlanan 0;
  ölçüm aracı testleri 41. Toplam iddiası Mustafa'nın tam koşusundan sonra
  (beklenen 327, yaşayan 0).
- Dokümanlar: K-61 başlığı ✅ KAPANDI + ölçüm paragrafı (08); bulgu 25
  *"Ölçüldü — karar kuralı tuttu"* tablosu, T-60 satırı (06); şartname §6.7
  (varsayılan 3), §11.3 (`deneme_siniri` varsayılan 3), değişiklik 64; kuyruk
  OKU-BENI politika sonucu; BURADAN ⚠ 8 Ekim 05:00; DEGISIM 05:00.

**Brifing (22:26 → 00:12).** Mustafa 22:26: brifingde O-19, K-63 gibi
kısayolların açıklaması olsun, *"bir bu doküman bir spec gidip gelmek
istemiyorum"*. v2 bir kısaltma sözlüğü (fihrist) ekledi — **yanlış anlama**;
00:12: *"K-61 ne ise onu dokümana eklemen"* — istenen, her kararın
*kendisinin* belgede olmasıydı. v3 yazıldı
(`00-DEVIR/brifing/2026-10-08-yilmaz-gorusmesi-v3.md`, 855 satır): her karar,
bulgu ve otopsi içeriğiyle yerinde — M-01…M-15; K-28, K-48, K-35, K-16, K-49,
K-37, K-59, K-60, O-16, K-54; K-30, K-57, K-61, O-18, bulgu 23, K-64; bulgu
25, O-19, ölçüm sonucu, K-63; T-60 + K-62 merdiveni; bekçiler. Taslakta
*"iyileştirmede kazancın %99'u ilk 36 sn'de"* yazmıştım — o eğri mola
adımınındı, düzeltildi. v1 ve v2 yan yana duruyor (sürümleme). Ders: geri
bildirim iki türlü okunabiliyorsa tek örnekle sormak bir sürüm kazandırır.

**04:07 — Mustafa:** *"şimdi ne yapacağım"* → koşturulacak bir şey yok;
varsayılan 3 + dokümanlar bitince tek blok. **Sıradaki blok:** testler (610 +
41) → DENETIM → commit (K-61 kapanışı; untracked: brifing v2/v3, ölçüm json,
politika jsonl, damga) → push → tam mutasyon (327). Sonra sıranın 3. maddesi:
dört yumuşak kural (şartnameden okunarak; tanım soruları tek tek); bulgu 26
karar Mustafa'da; bulgu 27 sırada; hibrit/%90 dondu (K-64 sonrası).

**05:05 — sıra 3 başladı: ilk tanım sorusu soruldu.** Okunan: şartname §5.4,
§6.3/6.5/6.8 satırları, §8.2–8.3, §11.2; K-13, K-22, K-49, K-50, K-54;
`09-motor/cozucu/model.py` (dört kuralın yalnız ağırlık satırı var),
`09-motor/dogrulayici/kurallar.py` (gövde yok), %95 fikstürü (herkes tek ekipte, `mevcut_plan` yok, 130 yarı
zamanlı / 85 uygunluk kaydı, şablon başlangıçları 07:00 · 08:00 · 10:00 ·
11:00 · 13:45 · 15:15 · 23:00; sabah/akşam/gece etiketi yok, yalnız yasal
`gece_mi`). Mustafa'ya **soru 1 — `VARDIYA_ROTASYON_YONU`**, üç karar:
(1) "geri" = art arda iki çalışma gününde sonraki başlangıç öncekinden erken
(önerim) / sınıf gerilemesi; (2) boş gün karşılaştırmayı sıfırlar (önerim) /
sıfırlamaz; (3) ceza birimi geri geçiş başına 1 × ağırlık (önerim) / erken
kaydırılan saat. Sıradaki sorular: `TERCIH_KARSILAMA` (esnekliğin "kullanım
oranı" ne), `PLAN_KARARLILIGI` ("değişim" sayımı), `EKIP_SUREKLILIGI` (hangi
süreklilik). Cevaplar gelmeden kod yazılmaz.

**05:05 — Mustafa'nın cevabı; 05:10–06:30 literatür.** *"1 için cevabı
literatürden alabilirsin … geri tanımına katılıyorum … 2 boş gün sıfırlar …
3'ü anlayamadım, istişare ederek ilerleyelim; ben yatıyorum, makine açık,
bloğu koşmaya bıraktım."* Blok: `c4ddca1` commit + push (origin'le eşit);
**tam mutasyon 327'nin hepsi öldü, atlanan 0** (damga 05:39, okundu 05:52);
pytest özetleri Mustafa'nın ekranında. Literatür okuması
`02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md`: IARC 124
(2020) §1.1 madde 8 — *geri* = öğleden sonra→sabah **ve sabah→gece**; hızlı
dönüş < 11 sa (madde 9); FIOH vardiya sınıfları (Härmä 2018 SJWEH); kanıt
Czeisler 1982, Bambra 2008 (26 çalışma), Di Muzio 2021 (JAMA Netw Open), HSE,
NIOSH. Üç karara yansıması: (1) kabul edilen tanıma ek — başlangıç farkı
**dairesel** ((−12, 12]) okunsun ki 08:00→23:00 geri sayılsın; (2) kabul,
Pazar→Pazartesi çifti geçmişle; (3) açıklandı — öneri **ağırlık × geri
kaydırılan saat**, alternatif geçiş başına 1 birim. Keşif
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-08-rotasyon-yonu/` (`geri_say.py`): 0.1 ölçekte 132
art arda çiftin 18'i geri (ort. 3,85 sa), 0.2'de 301'in 48'i (ort. 4,7 sa);
geri geçişlerin ~dörtte biri sabah→gece atlaması. Okunamayanlar belgede
(sjweh.fi izin istedi, PMC doğrulama, Europe PMC 429; Czeisler ikincil
kaynaktan). 05:40'ta Mustafa'ya özet + iki soru (1-ek dairesel; 3: saat/adet)
gönderildi; kod yazılmadı. Sıradaki: `TERCIH_KARSILAMA` sorusu hazır
bekliyor (0.2 ölçek keşfi: 33 yarı zamanlı ort. 20,1 sa / 3,1 gün, uygun
günlerin %67–75'i kullanılıyor, 2'si 0 saat).
