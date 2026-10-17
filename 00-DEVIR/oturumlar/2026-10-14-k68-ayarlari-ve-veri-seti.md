# 14 Ekim 2026 — K-68 ayarları, K-69 (süre kısıt değil), 7 saatlik ölçüm bloğu, veri seti işi

Önceki kayıt: `oturumlar/2026-10-13-seviye1-taban-ve-ayirma.md` §8 (900 ve
1200 ölçümü, üç ayar önerisi). Gece yarısını geçtiği için yeni kayıt (§5b).

## İçindekiler

1. Mustafa'nın kararları (13 Ekim 23:08–23:5x)
2. K-68 ayarları koda indi (bulut)
3. 7 saatlik ölçüm bloğu — karar kuralı (koşudan önce)
4. Veri seti işi (Yılmaz için) — kapsam ve kararlar
5. 01:30–01:45 — eski blok hiç durmamıştı; `tol1` sonucu; `07-motor/` adı; R7 sorusu
6. 01:40–02:00 — Yılmaz'ın küçük ölçek endişesi → T-82 (ölçek merdiveni 10 kademe, iki aşama eşiği), ikinci makine
7. Blok sonucu (04:34–11:27) — eski sette 5/5 plan, VS1'de 2/4; fazla mesai onarımı 0/7; tavan
8. 14:30–15:30 — öneriler onaylandı ve koda indi; kabul ölçütleri; üç kuralın tanım konuşması
9. 15:26 — `PLAN_KARARLILIGI` kararı (K-70); yarı zamanlı saat için mevzuat taraması (T-83); bu gecenin bloğu
10. 17:05 — K-71 (yarı zamanlı sözleşme süresi) ve K-72 (ekip sürekliliği) kararları; çağrı üzerine çalışma sorusu
11. 19:20 — gece bloğu ikiye bölündü (kısa blok koşuyor); ölçüm için bulut makinesi araştırması
12. 19:40–21:10 — K-70 / K-71 / K-72 koda indi (bulut); veri seti v2; VS2 0,1 ilk ölçüm ve veri düzeltmesi (sözleşme süresi müsaitlikle tutarlı); kısa blok sonucu
13. 22:09 — optimum hesabı çıktıda (kalem kalem, aşama aşama); ipucu fikri hayır; blok 03:00–04:00; `--veri-seti` anahtarı ve bloğun VS2 düzeltmesi
14. 23:56–04:20 — ölçek merdiveni (T-82) başladı: 1000'e kadar; bulut zinciri ve üç bulgu (eşik altı tek yol, 25'te fm kanıtlı kaçınılmaz, 100'de PART_TIME_LIMIT sert ihlal); zincir boşta öldü; gece bloğu
15. 15 Ekim 04:24–08:48 — gece bloğu: `6a2ab5d` push; VS2 500 referansı tutmadı (fm'siz arama bütçesi → düzeltme); VS1 1.800 × 3 → 2/3, lin0 1/3; bilgisayar 08:48'de yeniden başladı, 3.600 kesildi; `--devam`; devam bloğu
16. 15 Ekim 14:30–17:15 — fazla mesai onarımı komşuluk aramasıyla (K-68 ayar 3 ekleme); PART_TIME_LIMIT yeniden üretilemedi (HATA planı kaydı); yama `-e`
17. 15 Ekim 17:07–20:00 — merdiven zinciri 2. tur (bulut); iki doğrulayıcı hatası kapandı (kayan nokta; K-71 alanı FAZLA_MESAI_TAVANI'nda); 25 VS2, 151 üretildi
18. 16 Ekim 01:54–06:40 — test denetimi (A–H planı); Mustafa'nın "başla" talimatı (motor / edit / suggest); **ekili sahne** (A1: motordan bağımsız tanık plan, 49'da motor tanıktan −%3,9, 25'te kurulamaz), **çapraz denetim** (D: 11 fikstür + 30 plan kaydı temiz), **metamorfik testler** (E: 7 ilişki), bulut makinesi rehberi + betikler
19. 16 Ekim 14:38–18:30 — devam bloğu okundu (VS2 500 ref tuttu; VS1 3.600 × 3 → **0/3**, VS2 1.800 × 3 → 1/3 −%17,4; 751 ref 12 sn'de ilk plan): **L1 sahnesi plan bulmayı yapay zorlaştırıyor** (taban sahnede 500'de 31 sn); ekili 500 kuruldu (tanık 26.248), motor 900 sn'de fm 27,75 sa — arama zaafı; `gevsek_fm0` ölçüm seçeneği; cetvel kararı ölçümle (karar kuralı); **A3 insan planı sahnesi** (`insan-plani.py`: gerçek müşterinin elle planı, anonim; 22 Haziran 83 kişi, 20 Temmuz 70 kişi); gece bloğu

## 1 · Mustafa'nın kararları (13 Ekim 23:08–23:5x)

- **Üç ayarın maliyeti soruldu** (23:08); cevap: üçü de küçük iş, kaliteye
  zararı yok (ayrıntı sohbette; özeti §2).
- **K-69 (23:08):** süre ürünün kısıtı değil, hedef en zor şartta en iyi
  plan; müşteriye söylenecek süreyi ölçüm belirler, Mustafa'nın kararı.
  Kayıt `08-URUN-KARARLARI.md` K-69.
- **23:20:** *"2- olur 3- bu bloğu daha uzun tutalım. 7 saat sürecek bir koşu
  olabilir çok rahat … Yeter ki en iyi ölçümleri yapalım. Doğru değerlere
  ulaşalım."* → üç ayar onaylandı; ölçüm bloğu ~7 saat.
- **Veri seti (23:20):** Yılmaz toplantısında çalışan verisi soruldu,
  bulunamadı (*"Her defasında kuruyoruz galiba"* — doğru: `uret_veri_seti.py`
  seti bellekte kuruyor; depoda yalnız motor girdisi biçiminde fikstür var).
  İstek: çalışan verisinin şeması ve gerçekçi bir veri seti JSON olarak,
  isimler dışında gerçekçi, DB yapısına uygun; bundan sonraki testler bu
  setten (ya da merdiven setlerinden) koşsun. Yılmaz LDAP / API / Excel
  import'una ve kuyruk yapısına başlıyor.
- **Sorular ve cevaplar (23:3x, hepsi önerilen):** şema kaynağı şartname
  §8; kapsam planın bütün girdisi; kiracı alanı yok (M-16); teslim: JSON
  veri seti + JSON Schema + Excel örneği + veri sözlüğü.
- **K-58'in açık sorusu kapandı (00:0x):** tam zamanlının haftalık gün sayısı
  (5 | 6) **sözleşmede tutulur**. Eski tipler: **sezonluk → tam zamanlı**
  (sözleşmenin bitiş tarihi dolu), **stajyer → yarı zamanlı**.

## 2 · K-68 ayarları koda indi (bulut)

`09-motor/cozucu/coz.py`:

1. **`gevsek_yeniden_arama_atla`** (açık): fazla mesaisiz arama **süre
   doldurduysa** ve aşım sertse `_gecerli_plan_yeniden_ara` koşmaz,
   doğrudan gevşek yol. INFEASIBLE döndürdüyse koşar (girdi sertte çözümsüz
   olabilir; kanıt teşhis yoluna gider — K-37). Çıktı:
   `gevsekten_serte.yeniden_arama_atlandi`.
2. **`gevsek_yedek_orani`** (%25) iyileştirme + mola adımına ayrılır; gevşek
   yol kalanın tamamını kullanabilir. Her adım plan bulduktan sonra
   **`gevsek_durgunluk_saniye`** (60) iyileşmesizlikte durur (mevcut
   `_durgunluk_bekcisiyle_coz` ile). Ölçüm seçeneği
   **`gevsek_acik_parca_saniye`**: açık adım parça parça, her parçada başka
   tohumla (1, 2, 3… + `tohum_kaydirma`). Eski `gevsek_orani` /
   `gevsek_acik_orani` kalktı.
3. **`fazla_mesai_onarimi`** (açık, en çok `fazla_mesai_onarim_saniye` 300):
   gevşek plan fazla mesailiyse ve fazla mesaisiz arama başta bulamadıysa —
   fazla mesai alanları 0, plan ipucu, amaçsız arama; bulunursa iyileştirme
   oradan başlar; alanlar her yolda geri açılır (K-61/O-18). Çıktı:
   `cozum_istatistikleri.fazla_mesai_onarimi`.

Testler `09-motor/testler/test_gevsekten_serte.py` 15 → **26** (ayar başına
3–4 + bütçe testi yeni anlamıyla). Bir test ilk yazılışında yanlış sahnedeydi
(K-37 kanıt yolu: ayar 1 INFEASIBLE'da da atlıyordu → kanıtlı çözümsüz sahne
taslağa dönüyordu); kod düzeltildi (yalnız UNKNOWN'da atla). Mutasyon `k68`
32 → **49** (eski 4 bütçe mutantı yeni ayarlara çevrildi, 21 yeni); bulut
grup koşusunda 1 yaşayan ("fazla mesai yokken de denensin" — test ayarı
varsayılanla birleştirmeden çağırıyordu, süre 0 → erken dönüş); test
düzeltildi, mutant elle öldürüldü. Şartname §11.3 `gevsekten_serte` /
`fazla_mesai_onarimi`, değişiklik **70** (K-69 ile). `kalite-olc.py`:
yapılandırma `gevsek_parca` (150 sn parçalar), gevşek satırı onarımı ve
parçaları yazar. 09 paketi **691** yeşil; ölçüm testleri 34 + 1.

**Bulut yatağı (seviye 1, 0,3 ölçek, 300 sn, 2 çekirdek, n = 1; 13 Ekim'in
aynı sahnesi):** fazla mesaisiz arama 3 × UNKNOWN → yeniden arama
**atlandı** → açık adım **6,3 sn'de aşım 0** → gevşek planda **6.345 dk
(105 sa) fazla mesai** → onarım **101 sn'de 0'a indirdi** → sonuç çözüldü, 0
sert, 0 aşım, **0 fazla mesai**, amaç 10.704 (referans 7.989; 13 Ekim'de
aynı sahnede onarımsız 33.730, 5 sa fazla mesai). Gevşek yolun açık adımı
fazla mesaiye hiç bakmadığı için plan çok fazla mesaili çıkıyor; onarım 101
sn sürdü → varsayılan süre **120 → 300 sn** (500 kişi ~3 kat büyük; K-69).

## 3 · 7 saatlik ölçüm bloğu — karar kuralı (koşudan önce)

**İki set (01:10'da güncellendi).** Mustafa 23:20: *"Bundan sonraki
yapacağımız testler bu json veri seti veya merdiven tarafını yapınca setleri
kullanarak koşsun."* Bu yüzden blok iki sette: **eski L1** (13 Ekim'in altı
koşusuyla aynı fikstür — ayarların etkisi ancak aynı sette okunur) ve **VS1
L1** (veri setinden, K-58 sözleşmeleri + geçmiş; bundan sonraki set). VS1'in
500 referansı bloğun başında üretilir; üretilemezse VS1 satırları atlanır,
gerisi koşar. Mustafa'nın makinesi, 6 çekirdek; toplam ~7 sa 45 dk.

| sıra | koşu | set | süre | ne ölçer |
|---|---|---|---|---|
| 1 | testler (09 / 08 / 10) + commit + push | — | ~10 dk | yeşilse commit; kırmızıysa commit yok, ölçüm sürer |
| 2 | VS1 500 referansı (tohum 7, sert kesim) | VS1 | 900 sn | yeni setin seviye 1 talebi |
| 3 | `varsayilan` × 3 (`k68-1800`) | eski L1 | 1.800 sn | yeni ayarlarla plan bulma (13 Ekim: 5/6), aşım / sert 0, onarım, referansa göre puan |
| 4 | `varsayilan` × 3 (`k68-1800`) | VS1 L1 | 1.800 sn | aynısı yeni sette |
| 5 | `varsayilan` × 1 (`tavan-7200`) | VS1 L1 | 7.200 sn | **tavan**: iyileşme eğrisi nerede düzleşiyor; 30 dk ile 2 sa farkı |
| 6 | `gevsek_parca` × 2 (`k68-parca-1800`) | eski L1 | 1.800 sn | parçalı yeniden başlatma (açık adımın kuyruğu eski sette görüldü) |
| 7 | tam mutasyon (437) | — | ~50 dk | gerileme |

Tavan notu: iyileştirme aşaması (`_ilk_asamada_iyilestir`, bütçenin %80'i)
durgunluk bekçisi kullanmaz, bütçesinin tamamını harcar; 120 sn'lik durgunluk
yalnız mola adımında ve tek aşamalı yolda. Yani 7.200 sn'lik `varsayilan`
ayrıca ayar istemeden tavanı ölçer (bulutta 49 kişide denendi: iki yapılandırma
da 192 sn'nin tamamını kullandı). Eğri en çok 24 noktaya inceltilir; %50 /
%90 / %99 eşikleri tam eğriden.

Koşu günlüğü: blok her adımın başını / sonunu ve testlerin çıkış kodunu
`08-motor-testleri/gercekci-veri-seti/kosu-gunlugu-2026-10-14.txt`'ye yazar
(bulut köprüden okuyup ilerlemeyi izler).

**Okuma kuralı:**
- **Plan bulma:** `varsayilan` 5/5 → ayar 2 kuyruğu kapattı. < 5/5 →
  plansız koşunun açık adımı ne kadar aradı (`gevsekten_serte.adimlar[0]`),
  `gevsek_parca` daha iyi mi (parça sayısı, toplam süre).
- **Fazla mesai:** onarım kaç koşuda denendi / buldu; son planda fazla mesai
  (hedef 0). Onarım bulup son planda yine fazla mesai varsa: ağırlıklar
  fazla mesaiyi seçti (K-61; doğru davranış, raporlanır).
- **Kalite:** referans 55.248'e göre %; 13 Ekim'in 900 / 1200 koşularıyla
  (fazla mesai hariç −%24…−%27).
- **Tavan:** iyileştirme eğrisinin %90 / %99 saniyesi; 1.800 sn'de tavanın
  yüzde kaçında olunduğu → K-69'un "müşteriye söylenecek süre" girdisi.
- **Gerileme:** 09 paketi + merdiven / ölçüm testleri yeşil, tam mutasyon
  yaşayan 0.

## 4 · Veri seti işi (Yılmaz için) — kapsam ve kararlar

Teslim: `10-veri-seti/` (sürümlü klasör). Şartname §8 tabloları, kiracısız
(M-16), K-58 güncel; planın bütün girdisi (organizasyon, çalışan, vardiya,
kural, talep, plan + geçen haftanın planı). Dört parça: JSON veri seti
(500 kişi, uydurma Türkçe isimler), JSON Schema, Excel import örneği, veri
sözlüğü; ek olarak dönüştürücü (DB JSON → motor girdisi) ve testleri.
**Set değişir** (29 kişinin sözleşmesi K-58'e göre) → yeni referans ve yeni
seviye 1 seti Mustafa'nın makinesinde üretilir; o noktadan sonra testler bu
setten koşar (T-80'in 3–5. adımları).

**Yapıldı (14 Ekim 00:20–01:00, bulut):**

- `10-veri-seti/v1/` — `tablolar.py` (23 tablo, tek kaynak), `uret.py`
  (bugünkü tabandan tablolara; tohumlu, kimlikler uuid5), `donustur.py`
  (tablolar → motor girdisi; backend'in referansı), `belgeler.py` (JSON
  Schema, `VERI-SOZLUGU.md`, Excel), `10-veri-seti/v1/veri/tshift-500.json` (8,6 MB) ve
  `10-veri-seti/v1/veri/tshift-49.json`, `10-veri-seti/v1/testler/test_veri_seti.py` (19 test).
- **Dönüştürücü eski sahneden yalnız bilinen yerlerde ayrılıyor** (test):
  29 sözleşme, geçmiş (yeni; gün −14…−1), devir (geçmişten), 6 kuralın
  bayrağı (katalogdan), `HEDEF_ASIMI` türü, `sektor`, departman adları,
  `agirliklar`. Şablonlar, talep, kilitler, öteki kurallar birebir.
- **Bulgu 1 — üreticinin kural bayrakları katalogdan sapmış:** `ASGARI_KAPSAMA`
  ve `FAZLA_MESAI_TAVANI` kabul edilebilir (katalog ✅, üretici ❌);
  `ONAYLI_IZIN` ve `PART_TIME_LIMIT` yasal (katalog ✅, üretici ❌);
  `GECE_YARISI_ASAN` (katalog "—"); `HEDEF_ASIMI` (üreticide yok). Planı
  değiştirmez; yayın kapısının "kabul edilebilir / yasal" cümlesini
  değiştirir. Veri setinde katalog geçerli.
- **Bulgu 2 — geçmiş + sert hedef aşımı:** geçen haftanın Pazar gecesi
  vardiyası Pazartesi sabahını kapatıyor (K-56); üreticinin talep eğrisi
  geçmişi bilmeden kurulduğu için `HEDEF_ASIMI` sertken ön kontrolde
  çözümsüz (Satış Pzt 07:00: sahada 7, hedef 5). Merdiven tabanı (aşım
  yumuşak) çözülüyor (49 kişi, 60 sn, 0 sert); seviye 1 talebi yeni
  referanstan türeyince tutarlı.
- **Merdiven ve ölçüm aracı:** `merdiven.py --kaynak veri-seti` (taban
  depodaki veri setinden; dosyalar `_sahne-L1-VS1-95*`,
  `_referans-L1-VS1-95*`; eski adlar aynen), `kalite-olc.py --kaynak
  veri-seti` (dosya adında `-VS1`). Testler `test_merdiven.py` +3.
- Şartname §8 girişine not (farklar sözlükte; işlenmesi onayda).
- **VS1 küçük kopya (0,1; 49 kişi) bulutta üretildi:** referans tohum 7,
  300 sn bütçe, 252 sn; fazla mesaisiz ilk arama 0,9 sn'de OPTIMAL; tabanda
  sert 0, fazla mesai 0, yayınlanabilir; amaç 3.763. Seviye 1 sahnesi 415
  hücre, hedef 1.886 kişi-saat, asgari 1.552; referansın seviye 1 puanı
  4.720. Bulutta motor aynı sahnede 240 sn'de 3.478 (referanstan −%26,3;
  aşım 0, sert 0, fazla mesai 0).
- **Testler (bulut, 01:00):** 09 → 691 ✅; 08 merdiven + ölçüm aracı → 36 ✅ +
  2 atlanan (500'lük çözüm bekçisi haftalık; VS1 500 referansı henüz yok);
  10 → 19 ✅.
- **CI:** `testler.yml`'nin motor işine "Veri seti v1" adımı eklendi
  (`10-veri-seti/v1`, `pytest testler`). `jsonschema` ve `openpyxl`
  requirements'ta yok → o 3 test CI'da atlanır (bulutta paketler
  gizlenerek denendi: 16 ✅ + 3 atlanan); bağımlılıksız şema denetimi koşar.
  İkisini requirements'a sabit sürümle eklemek Mustafa'nın kararı (O-8).

## 5 · 01:30–01:45 — eski blok hiç durmamıştı; `tol1` sonucu; `07-motor/` adı; R7 sorusu

**Eski blok durmamıştı.** 13 Ekim 22:58'deki "Ctrl-C" koşuyu durdurmamış:
pencerede metin SEÇİLİYKEN Ctrl-C Windows konsolunda "kopyala"dır. Blok
sürdü; `tol1` 22:59'da başladı, 1. koşu 23:16'da yazıldı. Sonra pencere
**seçim moduna** girdi (pencereye tıklanınca konsol program çıktısını
bekletir, program da ekrana yazamadığı için durur): 23:3x'ten 01:35'e kadar
hiçbir şey ilerlemedi. Mustafa 01:35'te çıktıyı kopyalayınca donma çözüldü:
`tol1` dosyasını yazdı (2/2), **`tol2` başladı** (01:36), arkasından eski
kodla tam mutasyon gelecekti. 01:37 öneri: pencereyi X ile kapat (tol2 ve
mutasyon eski kodla; yeni blok ikisini de yeni kodla yapacak). 01:39 Mustafa:
*"Durdurdum."* Köprüden denetlendi: `.mutasyon-suruyor` yok, motor kodu
makinede `17779f3` ile birebir (mutasyon izi yok). `tol2` yalnız boş bir
iskelet dosyası bıraktı (`kalite-olcumu-L1-tol2-95-gevsek-900.json`, 0 koşu)
— commit'e girmez.

Ders (O- kaydı değil, işletim notu): uzun blokta pencereye tıklanmaz;
ilerleme koşu günlüğünden ya da köprüden okunur. Başlıkta "Seç" / "Select"
görünürse Esc.

**`tol1` sonucu (eski kod — K-68 ayarlarından önce; 900 sn × 2):**

| koşu | fazla mesaisiz ilk arama | gevşek açık adım | sonuç | aşım (bant içi) | eksik | fazla mesai | amaç (fm hariç) |
|---|---|---|---|---|---|---|---|
| tol1-1 | yok | OPTIMAL 203 sn | plan | 102 kişi-saat (102 hücre, hepsi +1 bandında) | 6 | 8,75 sa | 67.294 (41.044; referanstan −%25,7) |
| tol1-2 | yok | **UNKNOWN 225 sn** | **plansız** | — | — | — | — |

Okuma: tolerans 1 eski ayarlarla plan bulmayı kolaylaştırmadı (1/2; 13
Ekim'in sıfır toleransında 5/6). 2. koşuda açık adıma yalnız 225 sn kaldı
(fazla mesaisiz arama 123 sn + yeniden arama 120 sn önce yedi) — K-68 ayar
1 ve 2'nin kapattığı kuyruk tam bu. Eksik hedef belirgin düştü (6 kişi-saat;
sıfır toleransta 15–28): bant, eksik hücreleri komşu fazlayla takas
ettiriyor. Yeni blokta `tol` ölçülmüyor (öncelik K-68 ayarlarının kendisi);
gerekirse sonraki blokta yeni kodla.

**`07-motor/` → `07-gercek-veri-analizi/`** (Mustafa 01:36: *"Evet 07
ismini öyle değiştir"*). Klasör 14 Eylül'den beri adı içeriğine uymayan
analiz klasörüydü (motor `09-motor/`); `08-analiz/` önerisi
`08-motor-testleri/` ile çakışmıştı, `10-analiz/` önerisine karar
verilmemişti. Yapılan: yaşayan işaretler yeni adda (`README.md` klasör
tablosu, BURADAN klasör tablosu ve iki işaret, klasörün kendi
`OKU-BENI.md`'si, üç betiğin çalıştırma satırı, `08-motor-testleri/OKU-BENI.md`,
`09-motor/OKU-BENI.md` §9 KAPANDI); karar / risk / bulgu / oturum kayıtları
eski adla kalır (o günün doğrusu), `DENETIM.py` eski altı yolu "bilerek yok"
listesine gerekçesiyle aldı. Taşıma Mustafa'nın makinesinde `git mv` ile
(blokta, testlerden önce). Bulutta denetim: yeni HATA yok (bulutta çıkan 6
HATA `06-veri/` ve makinedeki ölçüm dosyaları — makinede var).

**R7 sorusu.** Mustafa: *"10. klasörle ilgili bir problem … 9 klasör sınırı
vs bir şey vardı."* İki ayrı şey karışmış: (1) **R7** — `00-DEVIR/` kökünde
en çok **9 dosya** (devir paketi büyüyünce okumak kendisi bağlam sorunu
olur); bugün 10 dosya, `DENETIM.py` 1 Ekim'den beri uyarı veriyor,
sadeleştirme sırada. Klasör sayısıyla ilgisi yok; veri seti işi
`00-DEVIR/`'e dosya eklemedi (oturum kaydı `oturumlar/` altında, sayılmaz).
(2) **`10-analiz/`** — 16 Eylül'de `07-motor/` için önerilen ad; "10.
klasör" hatırası buradan. Kök klasör sayısına bir sınır yok;
`10-veri-seti/` hiçbir kurala takılmıyor (sıralamada `09-motor/`'dan sonra
gelir, denetim temiz).

## 6 · 01:40–02:00 — Yılmaz'ın küçük ölçek endişesi → T-82; ikinci makine

Mustafa 01:40: Yılmaz'ın endişesi — 500 kişiye göre kurgulanan çözücü 50 /
100 kişilik basit senaryoda aynı kalitede olmayabilir ya da bozulabilir;
Mustafa'nın cevabı: merdiven verileriyle testlere başlayınca anlaşılacak.

Cevap (01:50): iki soru ayrı. **Bozulma** kapıda (altın senaryolar, küçük
sahneli birim testleri, 49 kişilik merdiven kopyası her push, bağımsız
doğrulayıcı). **Kalite** ölçülmedi ve Yılmaz haklı: iki aşama eşiği 50.000
değişken ≈ 40 kişi (ölçüldü: 49 kişi 61.220, 500 kişi 647.205 değişken) —
25 ile 50 kişilik müşteri farklı yoldan geçiyor; 49'daki ölçü referansa göre,
optimuma göre değil; ara boyutlar hiç ölçülmedi. Öneri: ölçek merdiveni.

Mustafa 01:53: *"Somut noktayı 50k değil de 100k mı yapsak … not al,
merdiven verisini oluşturduğumuzda bu iki aşama olayını da test edelim.
Merdiven testlerinde 5 kademe değil 10 kademe yapalım."* İkinci bilgisayar:
eski oyun laptopu, merdiven testlerinde aynı anda ikinci koşu için. Bu gece
başka iş yok; blok ~04:00'te başlar (bitiş ~11:45).

Kayıt: **T-82** (`06-ACIK-RISKLER.md`) — 10 kademe önerisi (25 … 500),
her kademede ürün yolu / tek aşamalı yol, ≤ 100 kişide 1 saatlik uzun koşu
(gerçek mesafe), eşik adayları 50.000 / 100.000 ölçümle; karar kuralı
koşudan önce (X Mustafa'da); ikinci makinenin kuralları (aynı makinede
kıyas, makine adı çıktıda, tek yazar). 100.000'e geçiş ölçümden önce
yapılmadı: hangi yönün iyi olduğu bilinmiyor.

## 7 · Blok sonucu (14 Ekim 04:34–11:27, Mustafa'nın makinesi, 6 çekirdek)

Blok 04:34'te başladı (Mustafa ~04:30), 11:27'de bitti; Mustafa 13:49'da
konsol çıktısını attı. Koşu günlüğü:
`08-motor-testleri/gercekci-veri-seti/kosu-gunlugu-2026-10-14.txt`.

**Akış.** `07-motor/` taşındı, CI yaması uygulandı (ikisi çıkış 0); 09 →
691 ✅; 08 → 66 ✅ + 2 atlanan; 10 → 16 ✅ + 3 atlanan (makinede `jsonschema`
ve `openpyxl` kurulu değil); DENETIM HATA 0; **`7dfd610` push**. VS1 500
referansı 835 sn'de (sert 0, fazla mesai 0, yayınlanabilir; seviye 1 puanı
**62.606** — ADALET 20.890, MOLA 41.608, ROTASYON 108; eski setin referansı
55.248). Tam mutasyon **437 · yaşayan 0**.

**Eski L1** (13 Ekim'in setiyle aynı; referans 55.248, fazla mesai 0):

| koşu | açık adım | fm onarımı | sonuç | fm (sa) | eksik (k-s) | amaç (fm hariç) | fm hariç, referansa göre |
|---|---|---|---|---|---|---|---|
| `varsayilan` 1800-1 | OPTIMAL 146 sn | bulamadı (300 sn) | plan | 7,5 | 34 | 63.072 (40.572) | −%26,6 |
| `varsayilan` 1800-2 | OPTIMAL 462 sn | bulamadı (300 sn) | plan | 7,5 | 13 | 62.792 (40.292) | −%27,1 |
| `varsayilan` 1800-3 | OPTIMAL 130 sn | bulamadı (300 sn) | plan | 6,25 | 20 | 59.109 (40.359) | −%26,9 |
| `gevsek_parca` 1800-1 | 1. parça OPTIMAL 66 sn | bulamadı (300 sn) | plan | 5,0 | 27 | 55.537 (40.537) | −%26,6 |
| `gevsek_parca` 1800-2 | 7 parça × 150 sn boş, 8.'si 62 sn → **1.114 sn** | bulamadı (112 sn) | plan | **28,75** | 64 | 128.301 (42.051) | −%23,9 |

Aşım 0, sert 0 hepsinde.

**VS1 L1** (veri setinden; referans 62.606, fazla mesai 0):

| koşu | açık adım | fm onarımı | sonuç | fm (sa) | eksik (k-s) | amaç (fm hariç) | fm hariç, referansa göre |
|---|---|---|---|---|---|---|---|
| `varsayilan` 1800-1 | **UNKNOWN 1.227 sn** | — | **plansız** | — | — | — | — |
| `varsayilan` 1800-2 | **UNKNOWN 1.226 sn** | — | **plansız** | — | — | — | — |
| `varsayilan` 1800-3 | OPTIMAL 287 sn | bulamadı (300 sn) | plan | 8,75 | 31 | 75.992 (49.742) | −%20,5 |
| `varsayilan` 7200 (tavan) | OPTIMAL 793 sn | bulamadı (300 sn) | plan; 6.145 sn'de durgunlukla bitti | 5,0 | 15 | 64.215 (49.215) | −%21,4 |

**§3'ün kuralıyla okuma.**

- **Plan bulma.** Eski sette **5/5** (13 Ekim'de 5/6) — ayar 1 + 2 eski
  sette kuyruğu kapattı görünüyor (n küçük). **VS1'de 2/4** (1.800 sn'de
  1/3). Açık adımın süresi VS1'de belirgin uzun: 287 / 793 / > 1.226 /
  > 1.226 sn (eski sette 66–462, bir kez 1.114). Yeni set (geçmiş hafta,
  K-58 sözleşmeleri, gerçek kural bayrakları) ilk geçerli planı bulmayı
  zorlaştırdı. **Plansızlık bugün ürünün en büyük açığı.**
- **Fazla mesai.** Onarım (ayar 3) 500'de **0/7**. Sebep: onarım açık
  adımın planından başlıyor; açık adım yalnız aşıma bakar, fazla mesaiye
  bakmaz → başlangıç planında **326–465 saat** fazla mesai (çıktıdaki
  19.575–27.900 dk). İpucu fazla mesaisiz plana çok uzak; her koşuda 300 sn
  boşa. Son planlarda fazla mesai 5–8,75 sa (iyileştirme indiriyor,
  sıfırlayamıyor); referansta 0 → fazla mesaisiz plan VAR. Fazla mesaisiz
  ilk arama (3 × 40 sn) da 500'de bu blokta **0/10** (13 Ekim 1/9; 49
  kişide 0,9 sn'de buluyor). 500'de bu iki adım koşu başına ~420 sn harcadı,
  hiç tutmadı.
- **Kalite (fazla mesai hariç).** Eski sette referanstan −%26,6…−%27,1
  (13 Ekim 900 sn: −%23,6…−%25,3; 1.200 sn: −%26,5…−%26,7): 30 dk 15 dk'ya
  göre ~%2–3 iyileştirdi. Toplam amaçtaki fark neredeyse tamamen fazla mesai
  (1 saat = 3.000 puan; 7,5 sa = 22.500).
- **Tavan.** 2 saatlik koşu fazla mesai hariç 49.215, 30 dk'lık 49.742
  (−%1,1 — eski setteki üç koşunun kendi arasındaki farkı ~%0,7; yani
  ölçüm gürültüsüne yakın). Toplam fark (64.215 / 75.992) neredeyse tamamen
  fazla mesai (5 / 8,75 sa). İyileştirme aşamasının eğrisi düzleşmedi: son
  iyileşme 4.466. sn'de; 1.785 → 4.466 sn arası sabit molalı amaç 112.707 →
  93.888 — sıçramalar fazla mesai kaldırılması. Yani: fazla mesai dışı
  kalite 30 dk'da tavana yakın; fazla mesaiyi sıfırlamak çözücü için yavaş
  iş — uzun süre bunu kısmen yapıyor.
- **Parçalı arama.** Plan bulmayı iyileştirmedi: 2. koşuda 7 tohum 150'şer
  sn boş, 8.'si 62 sn'de buldu (1.114 sn), iyileştirmeye 91 sn kaldı, plan
  kötü (fazla mesai 28,75 sa). Ürün yolu tek uzun arama kalır; parça ölçüm
  seçeneği olarak durur.

**Öneriler (karar Mustafa'da; 14:00 mesajı):**

1. **Fazla mesai onarımını iyileştirmenin sonuna taşı.** Onarım açık
   adımın planından değil, iyileştirmenin bulduğu plandan (5–9 sa, 4–8
   kişi) başlasın: ipucu fazla mesaisiz plana çok yakın; 300 sn'lik boşa
   harcama da kalkar. Küçük kod işi + test + ölçüm (eski L1 ve VS1).
2. **VS1'de plan bulma.** (a) 500'de hiç tutmayan fazla mesaisiz ilk
   aramanın süresi açık adıma verilsin (K-61'in ilkesi — önce fazla
   mesaisiz — 1. öneriyle sona taşınır; karar Mustafa'nın); (b) CP-SAT'in
   ilk çözüm bulmaya yönelik arama ayarları açık adımda ölçüm seçeneği
   olarak denensin; (c) bütçe: K-69 gereği 30 dk sabit değil — 45 / 60
   dk'da açık adım ~1.700–2.400 sn alır. Ölçüm VS1'de 5 tekrar, karar kuralı
   koşudan önce.
3. **T-82 ölçek merdiveni** bundan sonra (ikinci makine hazırsa paralel).

## 8 · 14:30–15:30 — öneriler onaylandı ve koda indi; kabul ölçütleri; üç kuralın tanım konuşması

**14:33, Mustafa:** *"sorularına ok diyorum. Henüz laptop'ın gelmesine var.
Onu ben sana söylerim. Şu an kriterler tarafında eksik var mı?"* → öneri 1
(onarım sona), 2a (fazla mesaisiz ilk arama kısa), 2b (açık adım ayarları,
ölçüm), 2c (bütçe 30 / 45 / 60 dk) onaylandı. f9994e2 (blok sonucu) Mustafa'nın
makinesinde push edildi (merdiven testleri 17 ✅ + 1 atlanan).

**Koda indi (bulut):** `coz.py` — onarım iyileştirmenin sonunda
(`_fazla_mesai_onar` amaçla, kabul kuralı, süre iyileştirmeden en çok yarısı;
`_ilk_asamada_iyilestir` `ayrilan` alır, ipucuyu yazan çözücüyü döndürür),
ayar 4 (`gevsek_fazla_mesaisiz_saniye` 20), öneri 2b
(`gevsek_acik_cozucu_parametreleri`); `kalite-olc.py` — `acik_lin0`,
`acik_ls`, onarım ve kısa deneme satırları. 2a'nın uygulanışı: fazla
mesaisiz ilk arama **tamamen atlanmadı**, gevşek yol mümkünken tek 20 sn'lik
denemeye indi (önce 3 × 40). Sebep: küçük modelde saniyenin altında plan
buluyor ya da fazla mesaisiz planın yokluğunu kanıtlıyor; tamamen atlansa
kanıtlı çözümsüzlükte çıktı "çözümsüz + teşhis"ten "taslak"a dönerdi (13
Ekim'de ayar 1 için bilerek korunan yol, K-37). 500'de 120 sn'nin 100'ü
açık adıma kalır. **Ekleme (15:15):** onarımın kullanmadığı süre
iyileştirmeye geri döner (`_iyilestirmeye_devam`) — bulut uçtan uca denemesi
(VS1 0,1, 180 sn, fazla mesaisiz arama atlanmış yol) devam yokken 87. sn'de
bitiyordu (ayrılan 71 sn boşa); devamla 157 sn, amaç 3.526 → 3.469. Ürün
yolunda (kısa deneme açık) 49 kişide fazla mesaisiz plan 2,2 sn'de bulundu,
gevşek yola gerek olmadı (amaç 3.478). Testler 09 → **705**
(`test_gevsekten_serte.py` 26 → 40), 08 merdiven + ölçüm 37 ✅ + 1 atlanan,
10 → 19 ✅; mutasyon bulut grup koşuları `k68` **78 · yaşayan 0**,
`fm_sifir` **63 · 0**, `demir` **40 · 0** (çapaları yeni koda bağlandı);
toplam mutant 466.

**Kriterler — Mustafa'nın sorusuna cevap (14:40):** (A) üç kuralın gövdesi
yok (`TERCIH_KARSILAMA`, `PLAN_KARARLILIGI`, `EKIP_SUREKLILIGI`; tanım
soruları 11 Ekim'den beri sorulmamıştı); yazılı her kuralın CI'da kendi ihlal
vakası var (`ihlal-vakalari.py`). (B) Ölçüm kabul ölçütü önerisi.

**14:56, Mustafa — B:** *"1- ok 2 ok 3 … hedef mantığı ok. yasak değil,
hedef 0 yapmak, ama yapamıyorsak bu çözümsüzlük yaratmamalı. 4 ok 6- ok.
Ölçek merdiveni için karar eşiğini ölçerek belirleyemiyor muyuz?"* →
**Kabul ölçütü (VS1 L1, 5 tekrar):** (1) plan 5/5; (2) aşım 0, sert 0; (3)
son planda fazla mesai 0 en az 4/5'te — **hedef**, yasak değil: onarım
bulamazsa plan olduğu gibi döner, çözümsüzlük yaratmaz (bugünkü davranış,
K-38); (4) fazla mesai hariç referanstan iyi; (5) eski setler ve bütün
testler değişmez; (6) süre: 1–3'ü tutturan en kısa bütçe (30 / 45 / 60 dk;
K-69 — müşteriye söylenecek süre adayı). **Ölçek merdiveninin eşiği
ölçümden:** her kademede iki yol 3'er koşu; aralıklar örtüşmüyorsa fark
gerçek (iyi olan seçilir), örtüşüyorsa gürültü (bugünkü ayar kalır) —
T-82'deki "%X" sorusu böylece kalktı.

**14:56, Mustafa — A (üç kural):**
- `TERCIH_KARSILAMA`: *"Yarı zamanlığının esnekliği söz konusu … öğrenci
  ptesi salı ve perşembe çalışamıyor … çarş cuma cumartesi ve pazar günleri
  mesai yazabiliyoruz. Tercih karşılama dediğin sende başka bir şey mi?"* →
  Cevap: anlattığı **uygunluk takvimi** (sert, K-13; motorda var). Açık
  soru: üstüne yumuşak bir şey var mı — yarı zamanlıyı uygun günlerinde boş
  bırakmamak / saatini makul düzeye getirmek (küçük keşifte 33 yarı
  zamanlının 2'si hiç planlanmadı)? Yoksa kural katalogdan kalkar.
- `PLAN_KARARLILIGI`: *"Geçtiğimiz haftanın planı ile aynı planı tutturmaya
  çalışmak çok zor … belki de bu konuyu plan klonlama ile çözmek daha mı
  mantıklı olur?"* → Cevap: kural **aynı haftanın yeniden planlanması**
  (K-54 akışı: yayınlanmış plan, biri hastalandı, yönetici düzenler / kilitler,
  motor yeniden koşar); bugün motor yayınlanmış plandan uzaklaşmanın bedelini
  bilmiyor. Öneri: yalnız aynı hafta, birim kişi-gün. Klonlama ayrı ürün
  özelliği (yeni haftayı geçen haftadan başlatmak; motor girdisi K-54'te
  hazır) — ayrıca VS1'de ilk planı bulmak için güçlü başlangıç olabilir
  (ölçülecek).
- `EKIP_SUREKLILIGI`: *"sadece tam zamanlı çalışanlar için mi çalıştırmalıyız
  … uzun zamandır aynı iş yerinde çalışanlar için değerli olabilir. Çok
  yumuşak bir kriter olacağına neredeyse eminim"* → Cevap: tanım (a) birincil
  ekipte kal; ayrımı sözleşme tipine değil **veriye** bırak — `employee_teams`
  önceliği eşitse (gezici) ceza yok, birincil ekip varsa var (sezonluk tipi
  zaten yok, K-58). Ağırlık 2 / 1 / 4.
- Karar Mustafa'da (üç soru, 15:00 mesajı).

## 9 · 15:26 — `PLAN_KARARLILIGI` kararı (K-70); yarı zamanlı saat için mevzuat taraması (T-83); bu gecenin bloğu

**Mustafa 15:26:** `TERCIH_KARSILAMA` için *"Bunun yasal zeminini araştırır
mısın? karar veremiyorum … Part time aldığımız adamı da bir hafta 4 saat
VEYA HİÇ, diğer hafta 30 saat kafamıza göre planlayamayız gibime geliyor."*
`PLAN_KARARLILIGI` için *"edit ekranında tamamını kitle, çoklu seçim yapıp
kitleme gibi fonksiyonlar olacak. Önerine katılıyorum, aynı haftanın
yeniden planlanmasında çalışsın."* → **K-70** yazıldı. `EKIP_SUREKLILIGI`
cevabı gelmedi (öneri: birincil ekip önceliğine göre).

**Mevzuat taraması → T-83:** kısmi süreli sözleşmede normal haftalık süre
sözleşmede belirlenir (İş K. m. 13; yönetmelik: emsalin 2/3'üne kadar),
kısaltılması ortak iradeyle; değişken sürenin yasal biçimi çağrı üzerine
çalışma (m. 14: yazılı, belirlenmemişse haftada 20 saat, çağrılsın
çağrılmasın ücret, çağrı başına en az 4 saat, en az 4 gün önceden). Motorda
yarı zamanlının alt sınırı yok; K-58 kişi başına saat tutmuyor. Üç karar
sorusu T-83'te; hukukçu teyidi gerekir (A-16).

**Bu gecenin bloğu (Mustafa'da, ~8 sa 15 dk):** testler (09: 705, 08, 10)
+ DENETIM + commit/push → VS1 L1 `varsayilan` 1.800 sn × 5 (kabul ölçütü)
→ VS1 L1 `varsayilan` 3.600 sn × 3 (süre) → VS1 L1 `acik_lin0` 1.800 sn × 3
(öneri 2b) → tam mutasyon (466). Koşu günlüğü
`08-motor-testleri/gercekci-veri-seti/kosu-gunlugu-2026-10-14-b.txt`.

## 10 · 17:05 — K-71 ve K-72 kararları; çağrı üzerine çalışma sorusu

**Mustafa 17:05:** *"Ekip sürekliliği ok. Bizdeki boşluk için çalışan
sözleşmesine süre girelim. uygundur. 2- motor yarı zamanlıya bu süreyi
getirmeye çalışsın. Sonuçta sözleşmenin altında çağırırsak yine para
ödüyoruz yani şirket boşa para yakıyor. 3- çağrı üzerine çalışma konusunu
anlamadım."* → **K-71** (yarı zamanlı sözleşme süresi kişi başına; motor
o süreye getirmeye çalışır — yumuşak; ağırlık önerisi 2.000 puan / boşa
ödenen saat, onay bekliyor) ve **K-72** (`EKIP_SUREKLILIGI` birincil ekip
önceliğine göre). Sıra 3'ün üç kuralının üçü de tanımlandı (K-70, K-71,
K-72); **uygulama bu gecenin bloğundan sonra, tek pakette** — veri seti
v2 (yarı zamanlı süreleri), şartname §8.3 / §11.2, motor + doğrulayıcı,
merdiven referansı yeniden. Çağrı üzerine çalışma 17:10 mesajında anlatıldı;
öneri: şimdilik kapsam dışı.

Bu kayıtlar bu gecenin commit'ine girer (blok başlamadan makineye yazıldı).

**18:40, Mustafa:** *"Ağırlık ok, mantıklı. Bu çağrı üzerineyi şimdilik
kapsam dışı bırakalım."* → K-71'de ağırlık 2.000 puan / boşa ödenen saat
(üç profilde aynı) onaylandı; çağrı üzerine çalışma kapsam dışı (T-83).

## 11 · 19:20 — gece bloğu ikiye bölündü; ölçüm için bulut makinesi araştırması

**19:21, Mustafa:** *"8 saat 15 dklık koşuyu koşmak istemiyorum hemen.
Yatarken koşmak istediğim bir blok o. Laptop yerine cloud ortamda
kurabileceğim bir makine olabilir mi? Hatta ölçek olarak daha güçlü
olabilir."* → Blok ikiye bölündü: **kısa blok** (testler + commit/push +
VS1 `varsayilan` 1.800 × 3; ~1 sa 50 dk) 19:23'te başladı
(`kosu-gunlugu-2026-10-14-b.txt`); kalan (1.800 × 2, 3.600 × 3,
`acik_lin0` 1.800 × 3, tam mutasyon; ~6,5 sa) yatarken. Kabul ölçütünün 5
koşusu = kısa bloğun 3'ü + gecenin 2'si (aynı makine, aynı kod — birleşik
okunur).

**Bulut makinesi araştırması (14 Ekim 19:30–20:00, bulut; fiyatlar üçüncü
taraf sayfalardan, Ekim 2026):**

| Seçenek | Çekirdek | Bellek | Saatlik | 8 sa blok | Not |
|---|---|---|---|---|---|
| Hetzner CCX43 (ayrılmış vCPU, AMD EPYC) | 16 vCPU = **8 fiziksel** çekirdek | 64 GB | ≈ €0,40 (aylık €276,49; saatlik faturalama, aylık tavan) | ≈ €3,3 | Haziran 2026'da fiyatlar iki kattan fazla arttı; Nürnberg / Falkenstein / Helsinki |
| Hetzner CCX53 | 32 vCPU = **16 fiziksel** | 128 GB | ≈ €0,80 (aylık €533,99) | ≈ €6,4 | |
| AWS c7a.4xlarge (Frankfurt) | **16 fiziksel** (SMT yok, EPYC 9R14) | 32 GB | $0,94 talep üzerine; spot ≈ $0,37 | ≈ $7,5 / $3 | spot kesilebilir — uzun ölçüm için talep üzerine |
| GitHub Actions büyük koşucu 16 çekirdek | 16 vCPU | — | $0,042/dk = **$2,52/sa** | ≈ $20 | yalnız **Team / Enterprise** planındaki **organizasyon** depolarında (bizimki kişisel); iş en çok **6 saat** |
| GitHub Actions **kendi koşucumuz** (self-hosted; Hetzner VM üstünde) | VM'in | VM'in | VM ücreti; dakika ücreti yok | VM | iş sınırı **5 gün**; `workflow_dispatch` ile tetiklenir, sonuçlar artifact |
| Mustafa'nın masaüstü (bugün) | 6 | — | 0 | 0 | tek makine; kıyas tabanı burada |

CP-SAT tarafı (OR-Tools belgeleri): 8 işçi paralel aramanın tabanı; 16'da
sürekli araştırma + ek ilk-çözüm alt çözücüleri (rastgele arama,
feasibility jump) + alt sınır işçileri; 24 ve 32'de daha fazla LNS ve
ilk-çözüm işçisi. **Yeni setteki plansızlık ilk-çözüm sorunu** → 16 fiziksel
çekirdek doğrudan buna çalışır. Bulutta (2 çekirdek) fazla mesaisiz ilk plan
500'de hiç bulunamadı (bulgu 30); 6 çekirdekte 13 Ekim'de 1/9, 14 Ekim'de
0/10.

**Öneri (istişare 21:30):**
1. **Hetzner CCX43 ya da CCX53**, yalnız ölçüm sırasında açık (saatlik
   faturalama; silinip yeniden kurulur — kurulum betiği depoda). Aylık
   bırakmak ~€276 / €534; blok başına €3–7. CCX53'ün 16 fiziksel çekirdeği
   ilk-çözüm sorununa daha çok işçi verir; önce CCX43 ile taban, gerekirse
   CCX53 denenir (ikisi aynı CPU ailesi, aynı tabanla okunur).
2. **Koşuyu kim başlatır:** (a) Mustafa SSH ile — bugünkü blok mantığı, bir
   `.sh` dosyası; (b) GitHub Actions kendi koşucusu VM'de — `workflow_dispatch`
   ile tetikleme, sonuçlar artifact olarak iner; koşucu dakika ücreti yok.
   (b) laptop için de aynı yol.
3. **Sonuçlar depoya nasıl gelir:** commit **yalnız Mustafa'nın
   makinesinden** (tek yazar kuralı) — VM'den ölçüm dosyaları `scp` / artifact
   ile iner, Mustafa commit'ler. VM'den commit yok.
4. **Kıyas kuralı:** her makinenin kendi tabanı; kıyaslanan iki yapılandırma
   aynı makinede (T-82 kuralları). `kalite-olc.py` çıktısına makine adı
   (`COMPUTERNAME` / `hostname`) eklenecek.
5. **Ürün için yan kazanç:** müşteri konteynerinin çekirdek sayısı sorusu
   (bulgu 30, açık) aynı ölçümle cevaplanır — 6 / 8 / 16 çekirdekte aynı
   sahne.

Kaynaklar: [agentdeals — Hetzner fiyatları (API, 7 Ekim 2026)](https://agentdeals.dev/hetzner-pricing-2026) ·
[privatedevops — Hetzner Haziran 2026 zammı](https://privatedevops.com/news/hetzner-june-2026-cloud-price-increase-what-to-do) ·
[sparecores — CCX43](https://sparecores.com/server/hcloud/ccx43) ·
[aws-pricing — c7a.4xlarge](https://aws-pricing.com/c7a.4xlarge.html) ·
[GitHub Docs — koşucu fiyatları](https://docs.github.com/en/enterprise-cloud@latest/billing/reference/actions-runner-pricing) ·
[GitHub Docs — Actions sınırları](https://docs.github.com/en/actions/reference/limits) ·
[OR-Tools CP-SAT — sorun giderme (işçi sayısı)](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md).


## 12 · 19:40–21:10 — üç kural koda indi; veri seti v2; VS2 0,1 ilk ölçüm

Mustafa koşuda (kısa blok makinesinde); bulutta iş: §9–§10 kararlarının
(K-70, K-71, K-72) kodu, veri seti v2 ve ilk ölçüm. Commit yok (tek yazar
kuralı); dosyalar bulutta, Mustafa gelince makinesine kopyalanacak.

**Kod (09-motor).** `model.py`: `_tercih_karsilama` (yarı zamanlı +
`sozlesme.haftalik_saat` → eksik dakika, 33 / dk), `_ekip_surekliligi`
(`birincil_ekip` dışı atama sayısı, 2/1/4), `_plan_kararliligi` (`mevcut_plan`
varken donmuş olmayan kişi-günde değişim, 6/6/6); hepsi `_amac`a `cezalar`
ile girer, ön ekleri `coz._CEZA_ONEKI` (tk / es / pk) amaç dağılımına eşler.
`coz.py`: `metrikler.plan_degisikligi` (korunan / değişen / kaldırılan /
eklenen; `mevcut_plan` yoksa `null`). Doğrulayıcı: üç kural bağımsız
(`kurallar.tercih_karsilama`, `ekip_surekliligi`, `plan_kararliligi`; #7.6).
Testler: `test_tercih_karsilama.py` 13, `test_ekip_surekliligi.py` 9,
`test_plan_kararliligi.py` 12 → **09 toplam 739** (geçti). Mutasyon grupları
`k71` 13, `k72` 10, `k70` 17 — **yaşayan 0** (bulut grup koşusu; tam koşu
Mustafa'nın makinesinde, toplam 506). `ihlal-vakalari.py`'de üç yeni vaka,
üçü kırmızı yanıyor. 08 testleri 66 geçti + 2 atlandı (500 VS2 referansı
yok). DENETIM: yalnız bulutta olmayan `06-veri/` (git dışı) hataları.

**Eski sahneler değişmedi — ölçümle doğrulandı:** üreteç L1, kayıtlı
`_sahne-L1-95.json` ve `_sahne-L1-VS1-95.json`'da `haftalik_saat`li yarı
zamanlı 0, `birincil_ekip` 0, `mevcut_plan` yok → üç kural o sahnelerde
değişken üretmez, amaç aynı. **Gece bloğu (VS1) yeni kodla da
karşılaştırılabilir**; paket makineye bu gece kopyalanabilir.

**Veri seti v2** (`10-veri-seti/v2/`, v1'den kopya; isimler aynı):
`employee_contracts.haftalik_saat` yarı zamanlıda zorunlu (16 / 20 / 24 / 30;
kişi başına ayrı tohum, v1'in rastgele dizisi bozulmadı); `employee_teams.
oncelik` çok ekiplilerin ~%30'unda eşit (gezici: 500'de 10'un 2'si, 49'da
1'in 1'i); `donustur.py` `sozlesme.haftalik_saat` ve türetilmiş
`birincil_ekip` yazar; sözlük / şema / Excel yeniden üretildi; testler 20
(yeni: K-71/K-72 dönüşümü, tutarlılık). `merdiven.VERI_SETI_SURUM = "v2"`
→ dosya eki **-VS2**; `kalite-olc.py` eki merdivenden alır; CI adımı v2;
`10-veri-seti/OKU-BENI.md` sürüm tablosu; şartname değişiklik satırı 72.
v1 dondu (-VS1 dosyaları 14 Ekim gündüz ölçümlerinin kaydı).

**İlk VS2 0,1 referansı (bulut, 300 sn) bir VERİ HATASI gösterdi.** Amaç
61.812, bunun **57.420'si `TERCIH_KARSILAMA`** (16 yarı zamanlının 6'sı
toplam 29 sa eksik). Neden: v2 taslağı sözleşme süresini **müsaitlikten
bağımsız** çekmişti — haftada yalnız 2 gün müsait öğrenciye (C0011: pazartesi,
çarşamba, cuma, cumartesi, pazar kapalı) 30 saatlik sözleşme yazılmıştı;
9 saatlik şablonlarla 18 saatin üstü imkânsız. Motorun aynı sahnedeki 240
sn'si de 57.915 verdi (referanstan −%1,6; TERCIH oynamadı) — **seviye 1
sahnesinde TERCIH zaten oynamaz:** hedef = referansın sayımı ve HEDEF_ASIMI
SERT → toplam saat sabit, tam zamanlılar 45'e SERT dolu, yarı zamanlıya kalan
tam referansın verdiği kadar. **Düzeltme (`uret.py`, 20:45):** süre, kişinin
uygun gün sayısı × 9 saati aşmayan değerlerden çekilir (2 gün → 16; 3 gün →
16 / 20 / 24; 4+ gün → hepsi). Yeni dağılım 500: 16 × 42, 20 × 20, 24 × 61,
30 × 23; 49: 4 / 2 / 8 / 2. Testte tutarlılık bekçisi. Referans yeniden
(300 sn, 250 sn): amaç **16.132**, seviye 1 puanı **17.135**, TERCIH 11.880
(= 6 sa: C0002, sözleşme 24, müsait 3 gün, referans 2 gün yazmış — referans
yolu bu kuralı aramıyor, "en az bu kadar iyisi var"). **Motor aynı sahnede
(bulut, 2 çekirdek, 240 sn):** fazla mesaisiz ilk plan 2,4 sn'de OPTIMAL
(gevşek yola girmedi), 22 çözüm, mola adımı optimumda durdu (203 sn), amaç
**15.637 → referanstan −%8,7**; aşım 0, sert 0, fazla mesai 0; TERCIH
**11.880 = referansla aynı** (beklendiği gibi oynamadı), kazanç mola
kapsaması (2.877 → 1.386) ve rotasyon. Dosya
`kalite-olcumu-L1-VS2-0.1-95-bulut.json` (+ `planlar/…/varsayilan-1.json`).
Kıyas için VS1 0,1 (sabah): −%26,3 — iki sahne farklı (v2'de TERCIH sabit
terimi payı büyütüyor, yüzde küçülüyor; mutlak kazanç benzer).

**Ders (K-71 ölçümü için):** seviye 1 sahnesi K-71'i ölçmez; kuralın etkisi
**taban sahnede** (HEDEF_ASIMI YUMUŞAK, referans üretim yolu) ya da referansı
bu kuralla aranmış yeni bir referansla görülür. 500 VS2 referansı Mustafa'nın
makinesinde (gece bloğu) — orada da aynı sınır geçerli. 49'da **K-72'nin
etkisi yok** (tek çok ekipli gezici); 500'de 8 kişi birincil ekipli.

**Kısa blok sonucu (Mustafa'nın makinesi, 6 çekirdek, 19:23–21:08;
`kosu-gunlugu-2026-10-14-b.txt`, `kalite-olcumu-L1-VS1-95-k68b-1800.json`):**
testler yeşil (09 / 08 / 10), DENETIM 0, `fe6909d` push 19:35. **VS1 L1
`varsayilan` 1.800 sn × 3 → 1/3 plan.** Üçünde de fazla mesaisiz tek deneme
20 sn'de UNKNOWN (K-68 ayar 4 çalıştı: 22 sn, önceki 3 × 40 yerine). Açık
adım: tekrar 1 ve 2'de **1.327 sn'de plan yok** (bütçenin %75'i; yeniden
arama atlandı), tekrar 3'te **773 sn'de** plan (durgunlukta durdu, aşım 0,
doğrudan tam sert) → iyileştirme 345 sn (1.229.574 → 145.888; alt sınır
78.445; hâlâ iyileşiyordu) → **fazla mesai onarımı 298 sn, fazla mesaisiz
plan bulunamadı (UNKNOWN), kabul yok** → devam + mola → amaç **116.313 =
referanstan +%85,8**, fazla mesai **22,0 sa** (20 kişi × 1,25 sa: 6 günlük
tam zamanlılar 46,25 sa'da — şablon net süreleri 45'i tam tutturamıyor;
referans planında fazla mesai 0, yani tutturan bileşim var). Gece bloğuyla
birlikte **VS1 1.800 sn: 2/6 plan** (açık adım bulduğunda 287 / 773 / 793
sn; bulamadığında 1.226–1.327 sn yetmedi). **Kabul ölçütü (5/5 plan) bu
bütçede sağlanamıyor** — 1.800 × 2 tamamlama koşusu anlamını yitirdi, gece
bloğundan çıkarıldı; yerine `acik_ls` 1.800 × 3 girdi. Bu gecenin sorusu:
açık adım planı **ne zaman** buluyor (yeni `ilk_cozum_saniye` kaydı, 3.600 ×
3), CP-SAT ayarları (lin0 / ls) bulma süresini değiştiriyor mu.

~~**Not (ürün fikri, karar Mustafa'nın):** üründe her hafta bir önceki haftanın
yayınlanmış planı vardır … geçen haftanın planını ipucu vermek ilk planı
saniyeler içine çekebilir.~~ **Mustafa 22:09: hayır** — *"geçtiğimiz haftaya
ait değer aslında PDKS gibi gerçekleşen veriden alınacak, plandan değil. Bu
senaryo çalışmaz."* Kapandı; ilk plan sorunu motorun kendi işi (CP-SAT
ayarları, bütçe, çekirdek).

## 13 · 22:09 — Mustafa'nın üç isteği: optimum hesabı çıktıda; ipucu fikri hayır; blok 03:00–04:00; "testler v2 ile mi?"

**(1) "Koşu sonuçlarına optimum hesaplamasının detaylarını ekle — puan puan,
% bilgileriyle; ne ne kadar etkiledi."** `kalite-olc.py`'ye **OPTIMUM
HESABI** bölümü (her koşunun sonunda; kayıtta `optimum_hesabi`): (a) **kalem
kalem** — her yumuşak kuralın ham değeri, birimi, ağırlığı (puan/birim),
cezası, amaçtaki payı, ilk aşama sonundaki cezası (mola adımı neyi
değiştirdi), referansın aynı kalemi, fark (puan ve %), farkın toplam farktaki
payı; (b) **aşama aşama** — ilk plan (kaynağı: fazla mesaisiz arama / açık
adım, ilk plan saniyesi) → ilk aşama iyileştirmesi → fazla mesai onarımı
(kabul / red / bulunamadı) → devam → mola adımı; her adımda amaç, fark
(puan, %), süre. Yalnız kayıttaki sayılar düzenlenir, yeniden hesap yok;
yazım hatası ölçümü durdurmaz (`optimum_hesabi_hatasi`). Kayıtlı dosya
için: `py kalite-olc.py --optimum-raporu <dosya.json>` (14 Ekim'in bütün
sonuçlarına geriye dönük uygulanır). Kısa bloğun 3. tekrarı bu gözle:
fark +53.707'nin **%122,9'u fazla mesai** (+66.000; referansta 0), mola
kapsaması referanstan **13.069 daha iyi** (−%31,4; farkın −%24,3'ü), adalet
+380, hedef eksiği +297, rotasyon +99. Aşamalar: açık adım 1.330.895 →
iyileştirme 145.888 (−%89, 345 sn) → onarım bulunamadı (298 sn boşa) →
mola adımı 116.313 (−%20,3; tamamı mola kapsamasından 58.114 → 28.539).
Testler 5 (`test_kalite_olc.py` 25).

**(2) Geçen haftanın planı ipucu — hayır** (§12 sonu).

**(3) Blok 03:00–04:00'te başlar** (uzun blok). **(4) "Testleri en son
oluşturduğumuz veri şemasıyla yapıyorsun değil mi?"** — Evet: veri seti
testleri v2 (20), CI v2, merdiven/kalite ölçümü -VS2. Ama soru bir hatayı
yakaladı: merdiven v2'ye dönünce **ilk verilen gece bloğu kırılacaktı** —
`--kaynak veri-seti` artık `_sahne-L1-VS2-95.json` arıyor, 500'lük VS2
sahnesi makinede yok (referans bloğun sonundaydı) → üç ölçüm "sahne yok"
ile düşerdi. Düzeltme: (a) `merdiven.py` `--veri-seti v1|v2` (argv; ortam
`TSHIFT_VERI_SETI`; varsayılan v2) — -VS1 kayıtlarıyla kıyas için eski sürüm
hâlâ koşulabilir; (b) blok sırası: **VS2 500 referansı önce (1.800 sn)** →
sahne yoksa (referans plan bulamazsa) ölçümler **VS1'e düşer** (günlüğe
yazar) → `varsayilan` 1.800 × 3 (VS2 tabanı) → `acik_lin0` 1.800 × 3 →
`varsayilan` 3.600 × 3 → tam mutasyon (~7,7 sa). `acik_ls` bu geceden
çıktı (süre); bulut makinesine ya da yarına. Motor birim testleri (739)
kendi küçük sahneleriyle koşar — veri setinden bağımsız; VS'yi 08 ve 10
testleri kullanır.


## 14 · 23:56–04:20 — ölçek merdiveni (T-82) başladı: liste 1000'e kadar; bulut zinciri ve üç bulgu; gece bloğu 04:20'de

**Mustafa 23:56:** *"Merdiven setlerini oluşturdun mu yoksa?"* — hayır, henüz
yoktu; zincir (üreteç referansı → veri seti v2 → VS2 referansı) bulutta
başlatıldı. **00:03:** *"Ölçekleri böyle düşünmüyorum, daha stratejik ve zora
doğru götürmek istiyorum. 1000'e kadar gitmeli. 2 hepsi gitsin."* → kademe
listesi **25 · 49 · 100 · 151 · 200 · 300 · 400 · 500 · 751 · 1000**
(onayında; üreteç 2,0'da temiz), ham tablolar dahil her şey git'e.

**Bulgular (bulut zinciri, 00:02–00:15):**
1. **25 kişi, eşiğin altı → tek aşamalı yol → fazla mesaili referans (4,5 sa).**
   Fazla mesaisiz ilk arama ve sert kesim yalnız iki aşamalı yolda. Referans
   üretimi artık her boyutta iki aşamaya zorlanır (`iki_asama_esigi: 0`).
2. **25 kişide fazla mesaisiz plan KANITLI yok** (ilk arama 0,35 sn
   INFEASIBLE; 16 tam zamanlı × 45 sa sert, 9 saatlik şablonlar). Kural:
   kanıtlı imkânsızsa referans fazla mesaili kabul (`fazla_mesaisiz_kanitli_yok`,
   `fazla_mesai_saat` kayıtta), seviye 1 sahnesi o kadar fazla mesaiye izin
   verir; kabul ölçütü o kademede "referansın fazla mesaisi". 25'in üreteç
   referansı 2,0 sa ile üretildi (seviye 1 puanı 7.361; `_sahne-L1-95-0.05`),
   veri seti `tshift-25.json` yazıldı; VS2 25 referansı henüz yok.
3. **100 kişi (üreteç sahnesi): motorun planı doğrulayıcıda `PART_TIME_LIMIT`
   SERT ihlal** (eksik 22, fm 0; fazla mesaisiz ilk arama 2,35 sn'de bulmuş).
   Motor ile doğrulayıcı aynı kuralı farklı okuyor olabilir (eski tipler
   `stajyer` / `sezonluk` yalnız üreteç sahnesinde; v1/v2 K-58 ile çevirdi) —
   **açık, incelenecek** (#7.6'nın yakalaması gereken tür). 100 kademesi bu
   yüzden üretilemedi.

**Zincir öldü (ders):** bulutta arka plana atılan iş (nohup) oturum
boşta kalınca durdu — 0,3 kademesi 00:15'te başladı, dört saat sonra hiç
çıktı yok, süreç yok. **Bulutta uzun koşu yalnız oturum çalışırken**
(araç çağrısı içinde beklenerek) yürür; gece boyu bırakılamaz. Ölçüm
makinesi sorusu (oturum §11) bir kez daha.

**Kod:** `merdiven.py` — `veri_seti_dosyasi(olcek)` (kişi sayısından ad),
`_veri_seti_tabani` dosya yoksa açık hata, `referans_uret` iki aşama + kanıtlı
fm kabulü, `turet` izinli fm; `uret.py` — `--olcek`, `MERDIVEN_OLCEKLERI`,
`dosya_yolu(olcek, kisi)`; testler 2 (merdiven). T-82 metni güncel.

**Gece bloğu (Mustafa 04:10: *"8–9 saat kadar vaktimiz var"*):** yama
`paket-k70-71-72-c.patch` → testler → commit/push → VS2 500 referansı
(1.800) → `varsayilan` 1.800 × 3 → `acik_lin0` 1.800 × 3 → `varsayilan`
3.600 × 3 → tam mutasyon → **751 üreteç referansı (3.600 sn)** (merdivenin
büyük ucu; sığmazsa sabah kapatılır). Günlük `kosu-gunlugu-2026-10-14-c.txt`.


## 15 · 15 Ekim 04:24–08:48 gece bloğu: `6a2ab5d` push; VS2 500 referansı tutmadı; VS1 1.800 × 3 → 2/3, lin0 1/3; **bilgisayar 08:48'de kendi kendine yeniden başladı**, 3.600 × 3 kesildi

**Zaman çizelgesi (`kosu-gunlugu-2026-10-14-c.txt`):** 04:24 yama `-c` →
09/08/10-v2 testleri yeşil, DENETIM 0 → **04:35 commit + push `6a2ab5d`**
(bulut 13:45'te çekti, stash düştü) → 04:35–05:01 **VS2 500 referansı çıkış 1
(1.576 sn'de; süre dolmadan)** → ölçümler planlanan yedeğe, **VS1**'e düştü
→ 05:01–06:35 `varsayilan` 1.800 × 3 → 06:35–08:09 `acik_lin0` 1.800 × 3 →
08:09 `varsayilan` 3.600 × 3 başladı → **08:48:43 bilgisayar yeniden başladı**
(Mustafa, `LastBootUpTime`): PowerShell penceresi ve Claude uygulaması
birlikte kapandı; 3.600'ün 1. tekrarı 39. dakikadaydı, dosyada 0 koşu.
Tam mutasyon ve 751 referansı koşmadı. Bulut oturumu kapanmadı (bağlam
yerinde); kapanan makinedeki uygulama penceresiydi.

**VS2 500 referansı neden tutmadı (çıktı pencereyle gitti; çıkarım):**
1.576 sn < 1.800 → süre değil, "REFERANS ŞARTI TUTMADI". Referans yolu fazla
mesaisiz ilk aramayı ürün payıyla (3 × 40 sn) yapıyor; VS1 500'de bu arama
saniyeler içinde bulmuştu, VS2'de (aynı sert kurallar, amaçta K-71 terimi)
bulamamış olmalı → gevşek yol → fazla mesaili plan → red. Düzeltme
(`referans_uret`): fazla mesaisiz aramaya **bütçenin yarısı** (3 deneme ×
saniye/6; 1.800 → 3 × 300 sn); eski referansları değiştirmez (ilk deneme
bulunca kalan süre kullanılmaz). Bir de ders: referans adımının çıktısı
dosyaya yazılmıyordu — devam bloğunda `Tee-Object` ile dosyaya.

**Sonuçlar (VS1 L1, 6 çekirdek; optimum hesabı çıktıda):**

| koşu | plan | açık adım ilk plan | amaç (ref 62.606) | fm | fm hariç | mola kaps. ref'e göre |
|---|---|---|---|---|---|---|
| `varsayilan` 1 | var | **346. sn** | 80.354 (+%28,3) | 10,25 sa | **−%20,8** | −13.097 |
| `varsayilan` 2 | var | **979. sn** | 144.546 (+%130,9) | 31,25 sa | −%18,9 | −12.971 |
| `varsayilan` 3 | yok | 1.327 sn yetmedi | — | — | — | — |
| `acik_lin0` 1, 2 | yok | 1.327 sn yetmedi | — | — | — | — |
| `acik_lin0` 3 | var | 654. sn | 90.851 (+%45,1) | 13,75 sa | −%20,8 | −13.146 |

Birleşik VS1 1.800 sn, `varsayilan`: **4/9 plan** (ilk plan 287 / 346 / 773 /
979. sn; bulamayanlar 1.327 sn bütçeyi tüketti); `acik_lin0` 1/3 (654. sn) —
yardım ettiğine dair işaret yok, örnek az. Bulunan her planda **fazla mesai
hariç referanstan %19–21 iyi, mola kapsaması ~13.000 puan iyi**; farkın
tamamı fazla mesai (10–31 sa; 50 puan/dk × 615–1.875 dk = farkın %114–173'ü),
**onarım 0/3 kabul** (300 sn'de fazla mesaisiz plan bulamıyor). İki ayrı
sorun: **planı bulma** (ilk plan 5–16 dk, kuyruklu; 3.600 ölçümü kuyruğu
görecekti) ve **fazla mesaiyi sıfırlama** (onarım tutmuyor).

**Yapılanlar (bulut, 13:45–14:10):** `kalite-olc.py --devam` — kayıtlı sonuç
dosyasındaki bitmiş (yapılandırma, tekrar) çiftleri atlanır, eksikler
koşulur; kesilen blok aynı komutla kaldığı yerden sürer (test + 49'da uçtan
uca denendi). `referans_uret` fazla mesaisiz arama bütçesi (üstte).
**Devam bloğu** (`kosu-gunlugu-2026-10-15-d.txt`): yama `-d` → 08 testleri
→ gece sonuçlarının commit'i → VS2 500 referansı (1.800 sn, çıktı dosyaya;
sahne varsa atlanır) → VS1 `varsayilan` 3.600 × 3 (`--devam`; kuyruk
sorusu VS1'in 9 koşusuyla okunur) → VS2 `varsayilan` 1.800 × 3 (referans
olduysa) → tam mutasyon → 751 üreteç referansı (3.600 sn). ~7 sa.
**Makine için:** Windows Update'i bir hafta duraklat, uyku kapalı — blok
gece koşacaksa.


## 16 · 15 Ekim 14:30–17:15 — gündüz PC'ye dokunmadan: fazla mesai onarımı komşuluk aramasıyla; PART_TIME_LIMIT incelemesi; gece bloğu yaması `-e`

**Mustafa 14:32:** *"Şu an 7 saatlik bir koşu açamam … iş yaparsam PC
yavaşlıyor. Artık geceye kaldı. Şimdi ne yapmamızı öneriyorsun?"* → üç
bulut işi önerildi; 15:19 *"Çalış bakalım, bulut olayını Yılmaz'la
görüştükten sonra karar vericem."*

**1. Fazla mesai onarımı → komşuluk araması (K-68 ayar 3 ekleme; kod).**
Gece planlarının fazla mesaisi 6 günlük tam zamanlılarda +0,5 / +1,25 sa
(şablon bölünebilirliği), onarım bütün modeli yeniden çözüyordu (7/7
UNKNOWN). Yeni yöntem: fm'li kişiler + ortak hücre / boş kapasite komşuları
serbest, geri kalan ipucuya sabit (alan daraltma), fm [0,0], amaç açık;
tur tur büyür. Ayarlar `fazla_mesai_onarim_yontemi` (komsuluk | tam),
`_tur` (4), `_komsu` (2). Testler 6, mutasyon `onarim` 16 (0 yaşayan),
`kalite-olc.py onarim_tam` kıyas yapılandırması, çıktıda yöntem ve turlar.
Ayrıntı K-68 maddesinde.

**2. PART_TIME_LIMIT (100 kişi) — yeniden üretilemedi.** Aynı sahne, aynı
tohum, bulutta 266 sn: sert 0, fm 0. Kod okuması iki tarafın tavanı ve net
süreyi aynı okuduğunu gösterdi; 500 planında 2.362 atamada model/doğrulayıcı
net farkı 0. Açık (T-82 üçüncü bulgu); şartı tutmayan referans planı artık
`_referans-HATA-…json`a yazılıyor ki bir dahaki görülüşte incelenebilsin.

**3. Merdiven küçük kademeleri bulutta** — bu gece Mustafa'nın makinesi
boşken bulut saatleri boşa gitmesin diye ertelendi; VS2 25 referansı ve
151 / 200 / 300 / 400 kademeleri bir sonraki gündüz oturumunda (oturum açık
tutularak).

**Ders (bulut):** mutasyon koşusuyla eş zamanlı test koşulmaz (O-20/O-21)
— bulutta bir kez çakıştı, 1 yanlış kırmızı; tekrar tek başına yeşil.

**Gece için:** yama `paket-15ekim-e.patch` (`-d`'nin yerine; `-d`
uygulanmadı, bayat): komşuluk onarımı + `--devam` + referans düzeltmeleri +
belgeler. Blok sırası aynı (§15); her ölçümde onarım artık komşulukla —
**bu gecenin ikinci sorusu:** onarım kaç koşuda fazla mesaiyi sıfırlıyor,
kaç saniyede, kaç turda.


## 17 · 15 Ekim 17:07–20:00 — merdiven zinciri 2. tur (bulut, oturum açık); iki doğrulayıcı hatası bulundu ve kapandı

**Mustafa 17:07:** *"Gece bloğu dursun, biz şu an gündüz ne yapabiliriz
oralardan devam edelim."* → merdiven zinciri 2. tur (25 VS2 → 100 → 151 →
200 → 300 → 400) bulutta, oturum açık tutularak (`kosu-gunlugu-2026-10-15-
bulut-merdiven.txt`). Referans üretimi artık şartı tutmayan planı kaydediyor
— ve bu iki hatayı aynı saat içinde çözdürdü:

1. **100 kişi, `PART_TIME_LIMIT` SERT — doğrulayıcıda kayan nokta hatası.**
   C0088 (yarı zamanlı) 5 × M-UZUN = tam 45,00 sa; doğrulayıcının toplamı
   45,00000000000002 (20 dk mola = 1/3 saat, ikili kesirde tam değil) →
   "aştı". Motor dakikayla çalışır, doğruydu. Düzeltme: doğrulayıcıda süre
   kıyasları tam dakikayla (`kurallar._dk`: GUNLUK_AZAMI, HAFTALIK_AZAMI,
   PART_TIME_LIMIT, FAZLA_MESAI_TAVANI); 2 test (`test_net_saat_uyumu.py`).
2. **151 kişi VS2, `FAZLA_MESAI_TAVANI` SERT ×2 (fm 0 iken) — K-71'in yan
   etkisi.** Yarı zamanlıya gelen `haftalik_saat` (16–30) doğrulayıcının
   FAZLA_MESAI_TAVANI gövdesinde fazla mesai tabanı sayıldı; 20 saatlik
   sözleşmeyle 32 saat çalışan "12 sa fazla mesai > 10" oldu. K-39: yarı
   zamanlıda 45'e kadar çalışma fazla mesai değil, tavan PART_TIME_LIMIT;
   motor da yarı zamanlıya fm değişkeni kurmaz; `denetle` metriği zaten
   atlıyordu. Düzeltme: gövde yarı zamanlıyı atlar; test
   (`test_tercih_karsilama.py`). **Ders:** K-71 paketi 14 Ekim'de 739
   testle yeşildi ama bu gövdeye dokunulmamıştı — yeni bir alan eski bir
   kuralın anlamını değiştirdi, bunu veri seti v2'nin 151 kişilik referansı
   yakaladı (49'da kimse 45'e yaklaşmıyordu). Her iki kaydedilen plan yeni
   doğrulayıcıyla temiz.

**Üretilenler (bulut, 2 çekirdek):** 25 VS2 (referans 152 sn, fm 2,0
kanıtlı; seviye 1 puanı 20.669 — TERCIH 11.880), 151 üreteç (526 sn, fm 0;
puan 13.837), `tshift-25.json`, `tshift-151.json`; zincir 200 / 300 / 400
ile sürüyor; 100 ve 151-VS2 düzeltilmiş doğrulayıcıyla yeniden üretilir.

## 18 · 16 Ekim 01:54–06:40 — test denetimi (A–H planı), Mustafa'nın "başla" talimatı; gece işi: ekili sahne (A1), çapraz denetim (D), metamorfik testler (E), bulut rehberi

**01:54 (Mustafa):** *"Şu ana kadar yaptığımız testleri … tamamını düşündüğünde
hangi konularda testlerimiz olabilir? … Ben hala bu optimum ve son eklediğimiz
kriterlerden sonra şüphelere sahibim."* → denetim ve öncelikli plan (bu
sohbette): **A1** ekilmiş çözüm (bilinen tanık planla sahne), **D** çapraz
denetim (her referans / plan bugünkü doğrulayıcıdan), **A3** insan planı
referansı, **B** karar/ağırlık testleri, **C** K-70/71/72 sahneleri, **E**
metamorfik testler, **F** veri fizibilitesi, **G** ölçüm disiplini / CI kalite
kapısı, **H** sistem testi. Teşhis: bugüne kadarki *"referanstan %x iyi"*
cümlelerinin hepsi **döngüsel** — referans aynı motorun başka tohumla planı
(K-62 ilke 1); K-71 L1 sahnesinde ölçülemiyor (toplam saat sabit), K-72 49'da
etkisiz, K-70'in sahnesi yok.

**05:46 (Mustafa):** *"artık motorun ana gövdesini yazdık … kurgu ve kod
yapısının gerçekten düzgün çalıştığını, doğru sonuçlar verdiğini görmek
istiyorum … bana göre 3 konu var: 1 motor 2 edit 3 suggest … ekstra para
harcamaya hazırım. Cloud ortamda ne gerekirse yapacağım … Başla lütfen, ben
yatıyorum … kullanım limitimin %30'u gibi bir eforun üzerine geçme."*
Cevap (05:55 mesajı): üç konu zor çekirdek — katılıyorum; **durum dürüstçe:**
motor yazıldı ve doğrulanıyor; **edit kısmen** (mevcut_plan + kilitler ile
yeniden çözüm, K-70, `/evaluate`, `orkestra.coz_ve_onar`); **`/suggest` hiç
yazılmadı** (`servis.py` 501). Motor dışı kalan riskler: veri kalitesi / içe
aktarma, çözümsüzlükte kullanıcıya ne gösterilir, makine / işletim, hukukçu
teyidi (T-83). Gece kuralı: ölçüm koşusu yok, yalnız kod + test + belge;
yama `paket-16ekim-g.patch`.

**05:57 — Mustafa'nın devam bloğu `f4f16c4` push'ladı** (yama `-f`, 09 / 08 /
10-v2 yeşil, DENETIM 0). Bulut eşitlendi (stash içeriği commit'le aynı, iki
stash düşürüldü). Blok VS2 500 referansıyla sürüyor (sabah okunacak).

### 18.1 · A1 — ekili sahne: motordan bağımsız TANIK plan (`ekili.py`)

Fikir: önce **desen çözücü** geçerli bir plan bulur (tabanın `Model`'i, sert
kuralların tamamı; üstüne iki desen: her kişi haftada **en çok 2 şablon**, fazla
mesai alanları [0,0]; asgari 0, HEDEF_ASIMI YUMUŞAK; amaç modelin ceza toplamı;
tek CP-SAT çağrısı). Sonra **talep taniktan türetilir**: hedef = doğrulayıcının
o saate saydığı kişi (`hucre_sayimi`), asgari = o saatin **en kötü çeyreğinde
sahadaki** kişi (doğrulayıcının MOLA_KAPSAMASI ölçüsüyle aynı fonksiyonlar),
yarı zamanlının sözleşme saati = tanıkta çalıştığı saat, HEDEF_ASIMI SERT.
Böylece tanığın **beş kalemi kuruluş gereği sıfır** (HEDEF_KAPSAMA, HEDEF_ASIMI,
MOLA_KAPSAMASI, FAZLA_MESAI, TERCIH_KARSILAMA); kalanı ölçülür → **tanık puanı**
= bu sahnede optimumun **üst sınırı**, ve **fazla mesaisiz / aşımsız / eksiksiz
planın KESİN var olduğu** bir sahne. Doğrulama motorun değil doğrulayıcının:
`referans_denetle` sert 0 / aşım 0 / eksik 0 / fm 0 ve beş kalem sıfır değilse
üretim **durur** (sessiz kabul yok). Dosya düzeni L1 ile aynı
(`_sahne-L1-EK[-VS2]-95[-ölçek].json`, `_referans-L1-EK…`; merdiven kaynağı
`ekili` / `ekili-veri-seti`), `kalite-olc.py --seviye 1 --kaynak ekili`
değişmeden çalışır (REFERANS KIYASI ve OPTIMUM HESABI tanıkla).

**Ölçüm (bulut, 2 çekirdek):**
- Tek şablon/kişi **25 ve 49'da ÇÖZÜMSÜZ** (saniyede kanıt): ROL/YETKINLIK_
  KAPSAMASI her gün 08–19 lider / İngilizce ister, tek şablonlu kişi günü
  kapatamaz → `DESEN_UST = 2` (`--desen`). **25 kişide fm'siz plan desen
  çözücüde de yok** (INFEASIBLE 0,7 sn) — T-82'nin 25 kişi bulgusuyla aynı;
  ekili sahne 25'te kurulamaz (test bunu kayda alır).
- **49 kişi:** tanık 120 sn'de (FEASIBLE; arama amacı 2.058, alt sınır 1.775),
  185 atama; türetilen talep 1.695 kişi-saat (taban 1.514 — tanık hedefi
  kovalarken 45 saatlik tam zamanlılar ve sözleşmesiz yarı zamanlılar hedefin
  üstünü doldurdu), asgari 979; **tanık puanı 1.275** — yalnız ADALET_DENGESI
  (1.275), diğer her kalem 0. Yarı zamanlılardan 7'si tanıkta çalışmıyor
  (sözleşme alanı yok), 8'inin saati 2,5–30.
- **Motor bu sahnede (`varsayilan`, 300 sn × 1):** plan **243 sn'de**, amaç
  **1.225 = tanıktan −%3,9**; ilk plan **1,34 sn'de** (8 çözüm); fm 0, hedef
  %100, aşım 0, mola 0, sert 0 — beş kalem tanıkla aynı sıfırda, fark yalnız
  ADALET 1.225 ↔ 1.275. **İlk döngüsel olmayan doğrulama:** 49'da motor,
  dışarıdan kurulmuş planın altına iniyor. Dikkat çeken: L1 sahnesinde 500'de
  ilk plan 287–979 sn iken burada 49'da 1,3 sn — ekili sahnenin asgarisi
  (çeyrek sahada) L1'in `hedef − 1`inden gevşek ve sözleşmeler tanıkla tutarlı;
  **500'deki asıl soru** (fm 10–31 sa) bu sahnede ölçülünce cevabı ikili olur:
  motor fm'siz planı bulur → L1'deki fm veri sıkılığından; bulamaz → arama zaafı
  kanıtlı. Bu ölçüm bulut makinesi bloğunun ilk adımı (`00-DEVIR/bulut/blok.sh`).
- Ekili sahne K-70 / K-72 sahnesi için de taban: `mevcut_plan` = tanık + bozulma
  (izin, hastalık) → yeniden planlama ölçümü (C planı; yazılmadı).

Testler `testler/test_ekili.py` **10**: türetim alanları ve determinizm
(fikstürdeki sahne taniktan yeniden türetilenle **aynı**), fikstür tutarlılığı
(sert / aşım / eksik / fm 0, beş kalem 0, puan = toplam, kayıt), desen kısıtı
değişken sayısı, 25'te çözümsüzlük, bozuk türetim ve sıfır olmayan kalem
**reddedilir**, bilinmeyen taban, merdiven ekleri.

### 18.2 · D — çapraz denetim (`capraz-denetim.py`)

Her `_sahne-L1*` + `_referans-L1*` çifti (EK dahil) ve `planlar/` altındaki her
plan kaydı **bugünkü** doğrulayıcıdan geçer: fikstürde sert 0 / aşım 0 / eksik 0,
fm ≤ kayıttaki izinli fm, `referans_puani` = kalemlerin toplamı (`--puan` ile
`plan_puani` yeniden); plan kaydında **taze `degerlendir` ↔ kayıtlı `dogrulama`**
(sert sayısı, yayınlanabilir, fm) ve motorun fm metriği ↔ doğrulayıcının fm'i
(#7.6). Sahne dosya adından çözülür (L1[-EK][-VS<n>][-çeşit][-ölçek]; S30);
sahnesi dosyada olmayan kayıt (0,2 ölçek bellekten üretilmişti) **atlanır**.
Çıkış kodu 0 / 1; `--json`. **Bulut sonucu: 11 fikstür TEMİZ** (iki 25 kişi
referansı fm 2,0 = izinli), **30 plan kaydı TEMİZ** (eski 500 kişilik planlar
— 14 Ekim öncesi — 15 Ekim doğrulayıcı düzeltmeleriyle de aynı sert 0 / aynı fm;
yani düzeltmeler eski kararları değiştirmedi), 4 kayıt atlandı (0,2). Testler
`testler/test_capraz_denetim.py` **13**: küçük fikstürlerin tamamı (parametreli),
çift eksiksizliği, ad çözümlemesi, EK plan kaydı taze = kayıtlı, **bozulmuş plan
(bir satıra +6 sa) SERT FARKI verir**, bilinmeyen biçim atlanır. 500 kişilik
fikstürler testte değil (4 sn/plan) — blokta `py capraz-denetim.py --puan`.

### 18.3 · E — metamorfik testler (`09-motor/testler/test_metamorfik.py`, 7)

Küçük sahne (3 yarı zamanlı, 2 şablon, 19 vardiya talep ↔ 18 kapasite → en az
bir eksik, amaç 0 olamaz), tek işçi, **yalnız OPTIMAL** (`durma_sebebi
"optimum"`, alt sınır = amaç — ilişkiler yaklaşık çözümde kesin değil):
**M1** kimlik değişimi (kişi / ekip / şablon adları) amacı, dağılımı ve plan
iskeletini değiştirmez · **M2** boş kalabilen kişi eklemek amacı kötüleştirmez ·
**M3** HEDEF_KAPSAMA'yı kapatmak amacı kötüleştirmez · **M4** çözümün kendisi
`mevcut_plan` olunca PLAN_KARARLILIGI 0 ve amaç aynı (K-70 sağlaması) · **M5**
aynı girdi aynı plan (determinizm) · **M6** çözümün satırları kilit olunca plan
ve amaç aynı (KILIT_UYUMU çözümle çelişmez). İlk yazımda sahne çok kolaydı
(amaç 0, hepsi boş geçerdi) — M0 testi *"amaç > 0"* bunu kapıda tutar.

### 18.4 · Bulut ölçüm makinesi rehberi

`00-DEVIR/BULUT-OLCUM-MAKINESI.md` + `00-DEVIR/bulut/kur.sh` (Ubuntu 24.04,
Python venv, depo salt okunur belirteçle, requirements, üç test paketi) +
`bulut/blok.sh` (ekili 500 tanık 900 sn → ekili sahnede `varsayilan` 1.800 × 3
→ VS2 500 referansı → VS2 1.800 × 3 → çapraz denetim `--puan` → tam mutasyon
→ 751; her adım günlüğe, sonuçlar `/opt/sonuc/`). Kurallar: makine yalnız
ölçümde açık, bitince **silinir**; **commit yok**; kıyas kendi tabanıyla.
Karar Yılmaz görüşmesinden sonra (Mustafa 15 Ekim 15:19).

### 18.5 · Bu gece yapılmayanlar (plan açık)

A3 insan planı referansı (Mustafa / Yılmaz'dan gerçek bir haftalık plan),
B karar/ağırlık testleri (ağırlık değişince plan hangi yöne kayar), C K-70 /
K-72 sahneleri (ekili tanık + bozulma), F veri fizibilitesi (sözleşme toplamı
↔ talep toplamı, lider-günü ↔ gereken), G CI kalite kapısı (49 kişi ekili
sahnede motor ≤ tanık + %x, haftalık), H sistem testi (`servis.py` uçtan uca).
Edit ve `/suggest` yazımı bunlardan sonra.

## 19 · 16 Ekim 14:38–17:00 — devam bloğu okundu: L1 sahnesi plan bulmayı yapay olarak zorlaştırıyor; ekili sahne 500'de kuruldu, motor fm'li kaldı; `gevsek_fm0` ölçüm seçeneği

**Blok (05:46–12:33, Mustafa'nın makinesi, 6 çekirdek; `kosu-gunlugu-2026-10-15-d.txt`):**

| Adım | Sonuç |
|---|---|
| Yama `-f`, testler, DENETIM, **`f4f16c4` push** (05:57) | yeşil |
| VS2 500 referansı (1.800 sn) | **tuttu**: 1.575 sn, 2.468 atama, fm 0, sert 0; fm'siz ilk plan **30,7 sn** (yarım bütçe düzeltmesi işe yaradı); seviye 1 puanı 81.672 (MOLA 43.953, ADALET 21.755, **TERCIH 15.840**, ROT 66, EKIP 58) |
| VS1 L1 `varsayilan` 3.600 × 3 | **0/3 plan.** Üç koşuda da fm'siz deneme 20 sn UNKNOWN, açık adım **2.677 sn UNKNOWN, 0 çözüm**; durma "bütçe doldu" |
| VS2 L1 `varsayilan` 1.800 × 3 | **1/3 plan.** 1. koşu: açık adım 117. sn'de ilk plan (123 sn'de OPTIMAL), iyileştirme 955 sn (3.367.687 → 115.371), devam → 97.451, mola adımı → **67.449 = referanstan −%17,4**, fm 0, sert 0, aşım 0, hedef eksiği 20 kişi-saat (180 puan); 2.–3. koşu açık adım 1.330 sn UNKNOWN |
| Tam mutasyon | 522, yaşayan 0 |
| 751 üreteç referansı (3.600 sn) | tuttu: 3.095 sn, 3.525 atama, fm 0; fm'siz ilk plan **12,4 sn**; seviye 1 puanı 81.360 (MOLA 64.414) |

**Okuma — sorun L1 sahnesinin kendisi.** Aynı motor, aynı makine: **taban** sahnede
(üreteçin asgarisi, HEDEF_ASIMI yumuşak) 500 kişide 31 sn'de, 751 kişide 12 sn'de
geçerli plan buluyor; **L1** sahnesinde (her hücre `[hedef−1, hedef]`, aşım sert)
500'de 2.677 sn'de bile bulamıyor, bulduğunda da piyango: ≥ 1.800 sn'de **VS1 4/12,
VS2 1/3**. Süre vermek işe yaramıyor (1.800'de 2/3, 3.600'de 0/3 — aynı sahne, aynı
ayar; fark yalnız iş parçacığı zamanlaması) → ilk çözüm ya ilk ~1.000 sn'de geliyor ya
hiç. K-62'nin seviye 1 kurgusu (referansın sayımı hedef, asgari = hedef − 1; 12 Ekim)
415 hücrenin hepsini aynı anda 1 kişilik banda sıkıştırıyor; gerçek müşteri talebi böyle
olmaz. **Motorun "500'de plan bulamıyor" görüntüsü büyük ölçüde bu kurgunun eseri.**
Karar Mustafa'da: kalite ölçüsü ekili sahneye taşınsın, L1 stres testi olarak kalsın
(öneri; K-62'ye ek).

**Ekili sahne 500 (bulut, 2 çekirdek; VS2 tabanı):** desen çözücü 900 sn'de tanık
buldu (FEASIBLE; arama amacı 242.305, alt sınır 51.010): 2.399 atama, fm 0, aşım 0,
eksik 0; türetilen hedef 21.987 kişi-saat (taban 17.860 — tam zamanlıların 45 saati ve
sözleşmeli yarı zamanlılar hedefin üstünü dolduruyor), asgari 12.993; **tanık puanı
26.248** (ADALET 25.000, ROT 1.236, EKIP 12). Fikstürler
`_sahne-L1-EK-VS2-95.json` / `_referans-L1-EK-VS2-95.json` (yama `-h`).

**Motor bu sahnede (`varsayilan`, 900 sn × 1, bulut 2 çekirdek):** plan buldu — açık
adım ilk planı **160. sn** (L1'de 1.330 sn'de yok; sahne tezi burada da tutuyor) — ama
**amaç 366.124 = tanığın 14 katı; fazla mesai 27,75 sa (27 kişi)**, hedef eksiği 91
kişi-saat, adalet ham 4.983 (tanık 5.000). Komşuluk onarımı 4 turda da bulamadı
(50 / 70 / 91 kişi serbestken **ÇÖZÜMSÜZ**, 109'da süre bitti). Bütçe darlığı gerçek
(iyileştirmeye 268 sn kaldı) ama bulgu ayırıcı: **fm'siz planın kesin var olduğu sahnede
motor fm'li planda kalıyor — arama zaafı, veri sıkılığı değil.** Teyit: Mustafa'nın
makinesinde 1.800 × 3 (gece bloğu).

**L1'de desenli arama (bulut):** aynı desen çözücü (≤ 3 şablon/kişi), fm 0 ve fm
serbest, L1 VS2 500 sahnesinde 420 sn'de **UNKNOWN** — L1 desenli aramaya da kapalı;
"desenli ilk plan" fikri L1'i kurtarmaz, ekili/ürün sahnelerinde ise açık adım zaten
buluyor → bu fikir şimdilik rafta (ölçülmeden yazılmaz).

**`gevsek_fazla_mesai_sifir` (ÖLÇÜM seçeneği; `kalite-olc.py gevsek_fm0`):** fm'siz
ilk arama bulamayınca açık adım fm alanları [0,0] ile koşar; plan bulursa fm sonraki
aşamalarda da 0'da tutulur (sert kesim gibi), bulamazsa alanlar açılır ve ana aşama
tam modelle sürer. Ürün varsayılanı **False** (K-38 zorunlu fm yolu kapanmaz). Gerekçe:
ekili 500'de açık adım fm serbestken 27 kişiye fm yazıyor ve onarım geri alamıyor; fm
0 iken açık adım plan bulabiliyorsa sorun kökünden çözülür. 2 test
(`test_gevsekten_serte.py` 48), `onarim` mutasyon grubu +3 (19; toplam 525),
çıktıda "acik adim fazla mesai 0 ile: …" notu.

**Fazla mesainin anatomisi (bulut EK-VS2 planı, 27 kişi / 27,75 sa):** hepsi 6 gün
çalışan tam zamanlı; 19'u +1,25 sa, 8'i +0,5 sa; hepsinde karışık şablon (örn. 3 × S-UZUN
+ S-KISA + S-GECE + S-SABAH = 46,25). Tanık aynı kişilere **tam 45,0** veriyor (5 × S-GECE
+ 1 × S-ARA; 5 × S-UZUN …) — yani 45'i tam tutturan dizilişler var, açık adım fm
serbestken kapsama uğruna 45'in üstünü seçiyor, iyileştirme ve komşuluk onarımı bunu
geri çeviremiyor (6 günlük tam zamanlıların 219'unda motor 149 kişiye karışık şablon
yazdı, tanık 116). `gevsek_fm0` tam bu mekanizmaya karşı.

**16:26 (Mustafa):** *"Bu kararı ölçüm yaparak vermeliyiz diye düşünüyorum. A veya C
arasında kaldım."* → **karar kuralı koşudan önce yazıldı (16:30; K-62 durum notu):**
sıkılık ölçüldü — asgari/hedef **taban 0,68 · L1 0,98 · tanıklı 0,59**; oynama payı
L1'de 415 hücrenin hepsinde tam 1, tabanda 359 hücrede ≥ 2, tanıklıda 301 hücrede ≥ 2.
Dört ölçüt: güvenilirlik (≥ 5/6 plan), gerçekçilik (tabana yakınlık), ayırt edicilik
(yapılandırma farkı > tekrar oynaması), tutarlılık (iki cetvel aynı sıra mı). A: tanıklı
1–2–3'ü geçer ve L1 1'i geçemez ya da 4'te aynı sıra; C: ikisi 1'i geçer, 4'te farklı
sıra. Gece bloğuna L1 VS2 `gevsek_fm0` × 3 eklendi (aynı yapılandırma iki cetvelde).

**17:26 (Mustafa):** *"Sana daha önce attığım tatilbudur'un plan verileri işine
yaramıyor mu?"* — yarar, **A3'ün cetveli tam bu** ve plan yazılırken unutulmuştu. Gerçek
müşterinin elle yaptığı planlar (`06-veri/ham/plan`, 69 Excel, 15 hafta; haftada 58–83
kişi, 311–485 atama, 18 vardiya deseni; `07-GERCEK-VERI-BULGULARI.md`). Yapılan
(`insan-plani.py`, A3): 07 dönüştürücüsünün kanonik tablosu Mustafa'nın makinesinde
yeniden üretildi (4.625 atama, 98 kişi — **isim ve sicil PC'den çıkmadı**, çıkmayacak);
seçilen hafta anonim motor girdisine çevrilir (kişi → `I001…`, eşleme yalnız
`06-veri/anonim/insan` altında git dışı; takım → ekip kodu, "Takım Lideri" → rol; o haftanın
izin kodları → onaylı izin; sözleşme saati = insan planının **net** saati ≤ 45; o haftada
kullanılan her (takım, desen) → şablon, mola politikası vardiya uzunluğundan), **talep insan
planından** (tanıklı sahnenin yöntemi: hedef = sayılan kişi, asgari = en kötü çeyrekte
sahadaki; HEDEF_ASIMI SERT), insan planına **varsayılan molalar** yerleştirilir (müşteri
planı mola yazmaz: yemek baş+4 sa 60 dk / 7,5 sa altı 30 dk; 15 dk dinlenmeler) ve plan
bugünkü doğrulayıcıdan geçer. Katalog üreteç sahnesinden; ROL/YETKINLIK_KAPSAMASI ve
CALISMA_SAATLERI atıldı (veri yok). İki hafta kuruldu:

| Hafta | Kişi (lider) | Atama | Şablon | Ekip | Hedef / asgari kişi-saat | İnsan planı: sert | yumuşak | fm |
|---|---|---|---|---|---|---|---|---|
| 22 Haziran | 83 (6) | 485 | 31 | 8 | 4.223 / 2.822 | **5** (DINLENME 4, ARDISIK_GECE 1) | 15 (ROTASYON 14, ADALET 1) | 0 |
| 20 Temmuz | 70 (4) | 404 | 25 | 5 | 3.533 / 2.360 | **2** (DINLENME 1, ARDISIK_GECE 1) | 8 (ROTASYON 7, ADALET 1) | 0 |

Net saat dağılımı (22 Haziran): 43 kişi ≈ 43 sa, 28 kişi 45 sa (6 gün × 09–18), 12 kişi
30–38 sa; 45 üstü yok. Sert ihlal sayısı 07 bulgusundaki 529'dan çok düşük: o sayı 15
haftanın ve **brüt** aralığın toplamıydı; burada tek hafta, molalar düşülmüş.
`kalite-olc.py --sahne <dosya>` (yeni): hazır sahne dosyasıyla ölçüm; insan planının
puanı `insan-plani.py --puan` ile (ortools; Windows'ta) — sert ihlalli plan modele oturmazsa
puan yerine durum yazılır ve REFERANS KIYASI atlanır, kıyas doğrulayıcı raporuyla kalem kalem
(sert, fm, kapsama = aynı, adalet, rotasyon, mola). Testler `test_insan_plani.py` 5 (uydurma
kanonik tablo; isim/sicil çıktıda yok), `test_kalite_olc.py` +3 (30).

**Gece bloğu (ekili 500 + insan planı + edit; Mustafa'nın makinesi; `gece-16f`):** yama k (i2 + j akşam uygulandı) →
testler → commit → tanıklı `varsayilan` 1.800 × 3 → tanıklı `gevsek_fm0` 1.800 × 3 →
L1 VS2 `gevsek_fm0` 1.800 × 3 → **insan planı puanı (iki hafta) → INSAN 22 Haziran
`varsayilan` 1.800 × 2 → INSAN 20 Temmuz 1.800 × 2** → tanıklı `onarim_tam` 1.800 × 2 →
üreteç tabanından ekili 500 → **yeniden planlama INSAN 22 Haziran (3 × 5, 1 × 5 örnek)** → çapraz denetim → tam mutasyon. İnsan sahnesinde okunacak:
motor sert 0 mı (insan 5 / 2), fm (insan 0), adalet / rotasyon / mola kalemleri, ilk plan
saniyesi (83 kişi, 31 şablon).

~~**Gece bloğu (ekili 500, Mustafa'nın makinesi; `gece-16c`):**~~ (d ile birleşti; sırası aşağıda)

### 19.1 · 19:47–20:03 — akşam bloğu: `e815ebe` push; **insan planı ↔ motor, ilk gerçek kıyas**

Yama i2 + j uygulandı (757 + 109 test, DENETIM 0, **`e815ebe`** push). İnsan planının motor
ölçüsüyle puanı iki haftada da hesaplanamadı (beklenen: sert ihlalli plan modele oturmaz) →
kıyas doğrulayıcıyla kalem kalem. **22 Haziran, `varsayilan` 300 sn × 1 (6 çekirdek):**

| Kalem (doğrulayıcı) | Planlamacının planı | Motor (300 sn) |
|---|---|---|
| Sert ihlal | **5** (DINLENME 4, ARDISIK_GECE 1) | **0** |
| Yayınlanabilir | hayır | evet |
| Hedef kapsama / aşım | %100 / 0 (tanım) | %100 / 0 |
| Fazla mesai | 0 | 0 |
| Rotasyon (geri geçiş satırı) | 14 | **3** (8 sa) |
| Adalet (eşik aşan kişi) | 1 (gece) | **0** |
| Mola kapsaması (en kötü çeyrekte asgari altı hücre) | 0 (asgari onun sayısından) | 65 (1.344'te; hepsi 1 kişi eksik) |
| Net saat / gün dağılımı | — | insan planıyla aynı (71 kişi 6 gün, 11 kişi 5 gün) |

**⚠ Bu kıyasın sınırı (Mustafa 22:40: *"TatilBudur'un yaptığı plana dair elimizde bilgi yok ki —
çıktı var, çalışan sözleşmeleri yok, vardiya kuralları yok"*).** Doğru. Elimizde planlamacının
**girdisi değil çıktısı** var; sahne o çıktıdan **geri kuruldu** ve dört varsayım taşır:
(1) sözleşme saati = planda çalışılan net saat (gerçek sözleşmeler bilinmiyor); (2) talep =
planın saat başına kişi sayısı (planlamacının Erlang-C ihtiyacı bilinmiyor; plan fazla ya da
eksik kadroluysa onu miras alıyoruz); (3) kurallar = **bizim** katalog (yasal eşikler + ürün
kuralları), planlamacının kendi iç kuralları, çalışan istekleri, yetkinlik zorunlulukları
bilinmiyor; (4) molalar bizim varsayılan yerleşimimiz. Bu yüzden tablo **"motor planlamacıdan
iyi"** demez. Sağlam söylenebilenler: (a) planlamacının çıktısı Türk iş hukukunun eşiklerine
göre 5 sert ihlal taşıyor (11 saat dinlenme brüt aralıkla ölçülür, mola varsayımından
etkilenmez; ardışık gece de öyle) — bu çıktının gerçek bir özelliği; (b) aynı kadro, aynı
desenler ve aynı saat başı kişi sayısıyla **yasal** bir plan var ve motor onu saniyeler içinde
buluyor; (c) rotasyon / adalet / mola sayıları iki ÇIKTININ aynı ölçüyle sayımı — planlamacının
görmediğimiz bir kısıtı (istek, yetkinlik) bu farkı açıklayabilir. **Kıyası tam yapmak için
müşteriden istenecekler:** çalışan sözleşmeleri (tip, haftalık saat), kendi kural/eşik listesi,
talep (Erlang-C çıktısı / HC hedefi), çalışan istek ve kısıtları. Gelene kadar A3 cetveli
**"çıktıdan kurulmuş, varsayımlı"** etiketiyle okunur; kabul ölçütünde yalnız (a) ve (b)
kullanılır. "Doğrulayıcı kıyası" = iki planın da **bağımsız kural denetçisinden** (09-motor/
dogrulayici) geçirilip kural kural ihlal satırlarının yan yana yazılması; puan değil sayımdır
ve puan kıyası (plan_puani) sert ihlalli planda mümkün olmadığı için tek adil kıyastır.

Motor: fm'siz ilk plan **0,46 sn** (OPTIMAL), ilk plan 1,55 sn, kazancın %90'ı **2,5 sn**;
amaç 1.348 (ADALET 680 = ham 136 × 5; MOLA 644 = 92 × 7; ROT 24); aşamalar 35.333 →
3.707 (240 sn) → 1.348 (mola adımı 59 sn; adımın sınırı 1.264). **Okuma (yukarıdaki
sınırla):** gerçek müşterinin kadrosu, desenleri ve saat başı kişi sayısıyla motor saniyeler
içinde **yasal** plan buluyor; planlamacının çıktısındaki 5 yasal ihlal bu planda yok; rotasyon
14 → 3 ve adalet 1 → 0 aynı ölçüyle sayım (planlamacının görünmeyen kısıtları olabilir); zayıf
kalem mola kapsaması (65 hücrede 1 kişi eksik) — hem cetvelin insan lehine kuruluşu (asgari bizim
varsayılan molalarımızdan türedi) hem mola adımının bu atamalarla sınırına dayanması
(atamalar değişmeden daha iyisi yok). Tablo ve optimum hesabı `Claude outputs\insan-motor-
kiyasi-2026-06-22.xlsx` (4 sayfa, formüllü).

**Eklenen (yama k):** `kalite-olc.py --sahne` için **DOĞRULAYICI KIYASI** bölümü — sahnenin
yanındaki `_referans-…` planı (insan planı / tanık) ve her koşu aynı doğrulayıcıyla kural kural
ihlal satırı, sert toplam, fm, yayınlanabilirlik (puan kıyası olmadığında tek kıyas bu;
`dogrulayici_kiyasi`, test). **"Edit" ölçümü `yeniden-planlama.py`:** "yayınlanmış plan" = ölçümde **mevcut plan yerine
konan** geçerli bir plan (insan planının çıktısı ya da tanık; kimin yaptığı değil, motorun bir
mevcut plana karşı davranışı ölçülür) + bozulma (`--hastalik k`: k kişi planda çalıştığı bir günde onaylı rapor) →
A ürün yolu (`mevcut_plan` + K-70) ve B sıfırdan; ölçülen: dokunulan kişi-gün (değişen +
kaldırılan + eklenen), **fazladan dokunulan** = dokunulan − 2k, sert, fm, eksik, raporlu
günde çalışan (0 olmalı), süre. Bulut 49 (tanıklı sahne, 2 kişi raporlu, 60 sn, 2 örnek):
**A 10 / 27 kişi-gün dokundu (fazladan 6 / 23), B 119 / 122** — K-70 değişikliği ~6 kat
azaltıyor ama en aza (2k = 4) inmiyor: ADALET vb. kalemler planı yayınlanandan uzaklaştırıyor
→ K-70 ağırlığı (6) ölçülecek bir ayar (B planı: karar/ağırlık testleri). 4 test.
Gece bloğuna eklendi: INSAN 22 Haziran, 3 kişi raporlu × 5 örnek ve 1 kişi × 5 örnek, 120 sn. yama i → tanıklı
`varsayilan` 1.800 × 3 → tanıklı `gevsek_fm0` 1.800 × 3 → **L1 VS2 `gevsek_fm0` 1.800 × 3**
→ tanıklı `onarim_tam` 1.800 × 2 → üreteç tabanından ekili 500 tanık (900 sn) +
`varsayilan` 1.800 × 2 → çapraz denetim `--puan` → tam mutasyon. Okunacak: (1) ilk plan
saniyesi ve plan sayısı (sahne tezi; ölçüt 1), (2) fm — `varsayilan` ↔ `gevsek_fm0`,
(3) tanığa uzaklık kalem kalem (OPTIMUM HESABI), (4) iki cetvelde sıra (ölçüt 4),
(5) 6 çekirdek ↔ bulut 2 çekirdek farkı.

### 19.2 · 17 Ekim 13:23–14:00 — gece bloğu okundu: tanıklı 6/6, L1 `gevsek_fm0` 3/3 fm 0; cetvel kuralı uygulandı → **A**

Gece bloğu (`gece-16g.ps1`, 04:16–13:50, 6 çekirdek): yama k2 uygulandı, 09/08 testleri ve
DENETIM yeşil, 04:27 commit + push `2a4bd77`; bütün ölçümler 13:12'de bitti; tam mutasyon
13:11–13:50, **525 mutant, yaşayan 0**; çapraz denetim 15 fikstür + 53 plan kaydı, şart
tutmayan 0 (motor fm = doğrulayıcı fm hepsinde). Günlük: `kosu-gunlugu-2026-10-16-gece.txt`.

**Sonuçlar (500 kişi, 1.800 sn).** Tanıklı EK-VS2 (tanık 26.248; fm 0, açık 0):
`varsayilan` × 3 → 3/3, amaç 27.382 / 61.807 / 48.782 (+4 / +136 / +86 %), fm 1,25 / 6,25 /
4,75 sa, hedef açığı 30 / 27 / 23 kişi-saat; `gevsek_fm0` × 3 → 3/3, 23.566 / 34.230 /
38.368 (**−10** / +30 / +46 %), fm 0 / 0 / 0, açık 28 / 50 / 25; `onarim_tam` × 2 → 59.956
(fm 3,0) / 39.461 (fm 0). **L1 VS2 `gevsek_fm0` × 3 → 3/3 plan** (dün `varsayilan` 1/3):
68.205 / 68.039 / 72.544 (−16,5 / −16,7 / −11,2 %), fm 0, sert 0, açık 35 / 63 / 66; açık
adım fm 0 ile 749 / 194 / 762 sn'de plan buldu. Tanıklı EK (üreteç tabanı; tanık 905 sn'de
kuruldu, puan 12.033, asgari/hedef 0,58): `varsayilan` × 2 → 11.479 / 11.347 (−4,6 / −5,7 %),
fm 0, açık 26 / 18. İnsan planı 1.800 × 2: 22 Haziran 1.348 / 1.348 (300 sn ile aynı), 20
Temmuz 1.200 / 1.186; doğrulayıcı kıyası değişmedi. Yeniden planlama (INSAN 22 Haz, 120 sn):
1 kişi raporlu × 5 → A 5/5, ort 18 kişi-gün dokunuldu (fazladan 16), B 255; 3 kişi raporlu
× 5 → ikisi de 2/5, üç örnek "cozumsuz" (260–277 sn) — **ölçüm betiği motorun teşhisini ve
taslağını kaydetmemişti** (§19.3'te düzeltildi).

**Dürüst okuma.** (1) L1'de fm alanlarını kapatmak plan bulduruyor (1/3 → 3/3); "−16,5 %"in
tamamı mola kapsamasından (ref 43.953 → 29.736), hedef kapsamasında motor referanstan **geri**
(35–66 kişi-saat açık, referansta 0). (2) Tanıklı sahnede `gevsek_fm0` **dalı hiç çalışmadı**
(üç koşuda fm'siz ilk arama 10 sn'de tuttu) → 23.566 ↔ 27.382 farkı yapılandırma değil şans;
aynı yolun üç koşusu 23.566–38.368 (+63 %), kaynağı tek kalem: TERCİH_KARŞILAMA 0 / 10.395 /
14.850 (tanık 0'ın mümkün olduğunu kanıtlıyor). 500'de sonuç ilk 20 sn'de dönen piyango.
(3) **Her kıyasta aynı desen: motor 18–66 kişi-saat hedef açığı bırakıp adaletle ödüyor**
(EK üreteç koşu 1: adalet 11.165 ↔ tanık 11.835, açık 234 = 26 × 9; net −554). Ağırlıklar
böyle diyor: 1 kişi-saat açık 9, 1 adalet birimi 5, 1 saat fm 3.000, 1 dk sözleşme altı 33 —
motor için 1 saat fm = 333 kişi-saat açık. Karar Mustafa'nın (K-61). (4) İnsan planında
1.800 sn = 300 sn: sınır süre değil arama şekli. (5) Edit: K-70 dokunuşu 14 kat azaltıyor ama
1 raporlu gün için 10–22 kişi-gün fazladan dokunuş; kararlılık ağırlığı (6) adaletin (5/birim)
ve tercihin (33/dk) yanında zayıf.

**Cetvel kuralı (K-62 durum notu, koşudan önce yazıldı) uygulandı:** (1) güvenilirlik —
tanıklı 6/6 ✔, L1 4/6 ✘; (2) gerçekçilik — tanıklı 0,59 ✔, L1 0,98 ✘; (3) ayırt edicilik —
tanıklıda ortanca farkı 14.500 < 3 tekrarın oynaması 34.000 ✘ (dal çalışmadı), L1'de plan
var/yok düzeyinde ✔; (4) tutarlılık — ikisi de `gevsek_fm0`'ı öne koyuyor ✔. Kural ne A'yı ne
C'yi tam veriyor (A: tanıklı 1-2-3 — 3 tutmadı; C: ikisi de 1 — L1 geçemedi). Okuma: **A'ya en
yakın** — tanıklı asıl cetvel, L1 gerilim testi; 3'ün tutmaması cetvelin değil motorun
oynaklığının kusuru. "Hangi yapılandırma iyi" sorusu oynaklık düşürülmeden (ilk aramaya
tekrar/bütçe, daha çok tekrar) cevaplanamaz. Mustafa'ya sunuldu, onayı bekleniyor.

### 19.3 · 17 Ekim 14:00–17:30 — **"çözümsüz diye bir şey yok"**; K-73 vardiya kayması; vardiya tasarımı analizi (K-74 aday); teşhis/taslak kaydı; ölçülen beraberlik

**Mustafa (13:53):** *"Çözümsüz diye bir şey yok, olmamalı. … sert kuralı ihlal etmeyerek plan
oluşturmamak mı yoksa fazla mesaili plan üretmek mi?"* Cevap: motor zaten böyle tasarlandı
(K-10 taslak + K-37 teşhis): "çözümsüz" ancak fazla mesai serbestken de kanıtla imkânsızsa
denir; teşhis hangi hücre / gereken / mümkün / hangi kural (yasal mı) der; yasal kuralları hiç
gevşetmeden asgariyi gevşetip **taslak** döndürür. Kusur ölçüm betiğindeydi (`yeniden-planlama.py`
yalnız "cozumsuz" kelimesini kaydetti; 260 sn'nin çoğu teşhisin kendisi: her sert kural tek
tek gevşetilip yeniden çözülüyor). Beden eksiği inceliği: raporlunun saatlerinde takımın
kalanı zaten sahada; komşu vardiya 11 saat sınırını aşmadan uzayamazsa hiçbir motor bedeni
yaratamaz → doğru cevap "Çarşamba 09–18 Satış Destek 1 kişi eksik, seçenekler şunlar".
**İlke: yasal kurallar sert kalır, firma kuralları (asgari, hedef aşımı) sırayla gevşer,
cevap hiçbir zaman boş olmaz.**

**Soruları (13:53):** molalar mı kötülüyor → hayır (L1'de mola kazanç, insan sahnesinde
insanın 0'ı kuruluş gereği); 26 kişi-saat açık fm'den kaçmak için mi → hayır, adalet için
(yukarıdaki rakamlar; fm 0'dı, tanık açık 0'ı kanıtlıyor); "1 raporlu gün" = 5 ayrı deney,
her birinde tek kişi; tavan fikri (1→3, 2→5, 3→7 kişi) → sert tavan yine "çözümsüz"e düşürür,
doğrusu "en az kişiye dokun" sıralı amacı + tavan müşteriye söz olarak kontrol.

**K-73 — VARDİYA KAYMASI (Mustafa 14:46, 14:52, 14:58).** *"İnsanlar planı düzenlerken
vardiya dahi kaydırabilir … 2 kişinin mesaisini 2 saat uzatır, bir sonraki mesaiye gelecek
kişinin vardiyasını 2 saat erken başlatır."* Kararlar: kayma değişkeni eklenir; **sınır
yasal, miktara puanlama karar verir** (*"En fazla kaymayı kafamıza göre belirlememeliyiz,
ölçümler karar vermeli"*); herkes uzatmaya açık; sıfırdan planda kapalı; **firma ayarı,
edit'te onay sorusu**; sözleşme penceresi zaten `uygunluk` ile (*"Sözleşmesinin dışına
çıkmayız"*); 45 saate kadar: İş K. md. 41 **fazla sürelerle çalışma** (%25) — *"bu sorunun
cevabı burada"*. Kuruluş: `09-motor/cozucu/kayma.py` — **türetilmiş şablon**: tabanın erken
başlayan / geç biten kopyaları, yalnız etkilenen (ekip, gün)de mevcut planda çalışan kişiye
(`kisiler`) ve o güne (`gunler`); yasal sınır net ≤ GUNLUK_AZAMI (11); kopya gün öncesine
taşamaz; gece işareti yeniden hesaplanır (K-43 tabanı korur). Model: `_sablonlari` `kisiler`
süzgeci + kişi başına önbellek; çıktı satırı `kayma` {taban, erken, geç, saat}; metrikler
`kayma_atama`, `kayma_saat`; `kayma_ozeti`. **FAZLA_SURELER** ölçüm kalemi: yarı zamanlının
sözleşme üstü dakikası (tam zamanlıda sözleşme üstü zaten FAZLA_MESAI'de, K-57 tanımı), ürün
ağırlığı 0 (değişken yazılmaz, model aynı), ölçüm 42/dk (= 2.500/saat, 1,25×). Testler 6
(`test_kayma.py`): kapalı → cozumsuz kanıtlı, açık → P1 08–16 → 08–20 (geç 4, net 11),
P2 14–22 → 12–22 (erken 2), sert 0, K-70 iki kişi-gün DEĞİŞEN; yasal sınır 10 → +4 üretilmez →
cozumsuz. Mutasyon grubu `kayma` 15, yaşayan 0 (**toplam 540**).

**Vardiya tasarımı analizi (Mustafa 14:49: "Biz hep vardiyayı sabit, kişileri değişken
tuttuk. Neden vardiyada da değişiklik yapmıyoruz? … literatürde de araştır").** Literatür:
Ernst ve ark. 2004 derlemesi süreci modüllere ayırır (talep → izin günleri → **vardiya
çizelgeleme** → çalışma hattı → atama); bizim motor son halkalar. Musliu–Schaerf–Slany
**shift design**: dilim başına gereken kişi + vardiya tipi aralıkları → hangi vardiyalar kaç
kişi; amaç eksik + fazla + **çeşit sayısı**; çağrı merkezi verisi, Ximes OPA. Örtük modeller
(Bechtold–Jacobs 1990, Thompson 1995) = kaymanın akademik hali. Gramerle tanımlı vardiya
(Côté–Gendron–Rousseau) = tam esnek. Rerostering (Wickert–Smet–Vanden Berghe): **değişiklik
sayısı en ağır kalem (100)**, ufuk daraltma ucuz — Mustafa'nın tavan içgüdüsünün karşılığı;
bizim kararlılık 6 ters uçta. Sektör: perakende/çağrı merkezi WFM "talebe dayalı çizelgeleme".
Bizde: kapasite tabanı satırı ("şablonlar sabitken en az X açık") tasarımın düşüreceği sınır.
Engel: bağımsız talep (üreteçte var — Mustafa: hedef kişi verisinin sürümlerini üretelim;
insan planında yok, döngüsel → müşteriden saatlik talep). Üç seviye: (1) kayma — K-73;
(2) **vardiya tasarımı modülü**, motordan önce ayrı küçük çözücü, firmaya öneri ekranı
("09–18 / 14–23 düzeniniz %93 kapatıyor; 10–19 ve 13–22 aynı kadroyla %98") — **K-74 aday**;
(3) tam esnek — mimariyle uyumsuz, kapalı. Riskler: hukuk (md. 22 esaslı değişiklik yazılı
kabul, md. 63 denkleştirme — hukukçuya), çalışan öngörülebilirliği (pencere içinde oynama),
hesap yükü (Mustafa: korkmuyorum), ölçüm döngüselliği. Kaynak bağlantıları K-74'te.

**Ölçüm betiği (`yeniden-planlama.py`, 17 Ekim):** yapılandırma tablosu (`--yapilandirma`):
`A_urun`, `B_sifirdan`, `A_kayma`, `A_kayma_tavan1/2`, `A_yumusak` (asgari kaldırıldı +
HEDEF_KAPSAMA 3.000), `A_kayma_yumusak` (3.000), `A_kayma_yumusak6` (6.000); çözümsüzde
**teşhis + taslak** kaydı (kapsam, hücre, gereken/mümkün, engelleyen kurallar, kanıtlı mı;
taslağın açığı/sert/fm/kayma); her planda kayma özeti ve açık kişi-saat (doğrulayıcıdan);
özet satırlarında kayma ortalaması ve taslak satırı. `kalite-olc.py`: `kapsama_once`
(3.000), `kapsama_once6` (6.000), `fazla_sureler` (42) ölçüm yapılandırmaları.

**Ölçülen gerçek (küçük sahne, testte sabit):** asgari gevşek + **1 kişi-saat açık = 1 saat
fm (3.000) → berabere**, kararlılık cezası (6) teraziyi açık bırakmaya iter: motor
**uzatmaz** (açık 8, kayma 0). 6.000'de uzatır (açık 2, kayma 6 sa, fm 6). Yani kapsamanın
ağırlığı fm bedelinin **üstünde** olmalı ki motor insan planlamacı gibi davransın; sayı
Mustafa'nın (K-61). Gece bloğu (17 Ekim) bu tabloyu insan planı sahnesinde ölçer.
