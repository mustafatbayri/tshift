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
