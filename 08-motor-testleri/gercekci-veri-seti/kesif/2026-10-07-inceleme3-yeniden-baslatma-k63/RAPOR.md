# Bağımsız inceleme 3 — (A) `fazla_mesaisiz_deneme` yeniden başlatma, (B) K-63 ipucu planı

Tarih: 7 Ekim 2026 (akşam). İncelenen: `coz.py.diff` (committed sürüme göre), yeni bölüm 7 testleri, `test_mola_adimi_yetismedi.py`, mutasyon listesi, `kuyruk.py`, `kalite-olc.py.diff`.
Makine: 2 çekirdek (bulut); ortools 9.15.6755 (requirements'ta sabit).

## 0. Yöntem ve bir süreç uyarısı

**Depo kopyası inceleme sırasında kararlı değildi.** `duzeltme/depo/09-motor/cozucu/coz.py` incelemem başladığında başka bir süreç tarafından (ana oturumun 16:14'te başlattığı `mutasyon_kostur.py butce/demir/ilk_asama/kalite/sure_yetmedi` grup koşusu) yerinde değiştiriliyordu (`ps` ile görüldü; dosya mtime saniyeler önceydi; içinde "butce" mutasyonu açıktı). Bu yüzden:

* İlk tam koşumda `test_fazla_mesai_once_sifir.py` 1 kırmızı verdi (`test_SERT_KESIMDE_ortak_arama_KISITLIDIR...`: `durma_sebebi == "mola_adimi_optimum"`, `mola_adimi=False` iken) — kodun hiçbir yolundan üretilemeyecek bir değer; o anda `coz.py`'de başka bir mutasyon açıktı. Sonraki 8 tam koşuda tekrarlanmadı. **Sahte kırmızı; koda ait bulgu değil.**
* Mutasyon koşusu bitince depodan **dondurulmuş bir kopya** aldım (`inceleme3/deneme/depo/`) ve doğruladım: `coz.py` == committed (`/mnt/user-data/uploads/Tshift/...`) + `coz.py.diff` **birebir**; `model.py`, `teshis.py` committed ile aynı. Bütün ölçümler bu kopyada yapıldı; depo dosyaları değiştirilmedi.
* Dondurulmuş kopyada tam takım: **604 passed, 137 sn** (`pytest testler -q`).

Deney betikleri ve çıktıları: `inceleme3/deneme/d1_tohum.py … d7_donmus.py` ve `*.out`.

---

## 1. Bulgular

### B1 — İnceleme paketindeki `coz.py` kopyası mutant bir anlık görüntü  — **düzeltilmeli (süreç)**
**Ne:** `inceleme3/coz.py` (16:14:32'de kopyalanmış; `mut3/` klasörüyle aynı saniye) depodaki gerçek `coz.py`'den iki satırda farklı: satır 407 `pay = float(ayar.get("ilk_asama_saniye", 120))` (mutasyon listesindeki "birinci asama eski butcesini alsin") ve satır 1203 `"teshis_istenebilir": False` (listedeki "neden oldugunu arastir secenegi sunulmasin"; committed sürümde ve depoda `True`). Yani paket, dosyada mutasyon(lar) açıkken alınmış — iki mutasyonun aynı anda açık olması, iki koşunun üst üste bindiğine işaret ediyor (koşturucu her mutasyonda "orijinal"i diskten okuyup ona geri yazıyor; üst üste binen iki koşu birbirinin mutasyonunu orijinal sanır).
**Nasıl:** `diff duzeltme/depo/09-motor/cozucu/coz.py inceleme3/coz.py` → 2 fark; `coz.py.diff` ise doğru satırı (`pay = _ilk_asama_payi(ayar)`) içeriyor; depo şu an temiz (committed + diff ile birebir).
**Öneri:** Paketi mutasyon koşusu bitmişken yeniden üretmek; `mutasyon_kostur.py`'nin çalışma kopyasını değil geçici bir kopyayı değiştirmesi ya da bir kilit dosyasıyla eşzamanlı koşuyu reddetmesi; koşu sürerken aynı checkout'ta başka test/inceleme koşturulmaması. Aksi halde CI dışı her ölçüm (bu akşamki grup koşuları dahil) şüpheli kalır — yukarıdaki sahte kırmızı bunun örneği.

### B2 — (A, soru 1) `random_seed` yazılmamış ≡ `random_seed = 1`: **birebir, ölçüldü** — not
**Nasıl:** `d2_tohum_01.py`, 0.1 ölçek (49 kişi, 59.812 değişken), birinci aşamanın hazırlığı motorun kendi yardımcılarıyla (amaç silinmiş, molalar sabit, fm [0,0]):
* 1 işçi: yazılmamış → OPTIMAL, dal 12.625, çatışma 31, det. süre 0,0888; `seed=1` → **aynı çözüm vektörü, aynı dal/çatışma/det. süre**. Tekrar koşu da aynı.
* 2 işçi: 3'er tekrar, yazılmamış ve seed 1 → hepsi dal 14.143 / çatışma 96 (aynı).
* seed 2 ve 3 **farklı** arama ve farklı çözüm (seed 2: 1.841 x'in 294'ü farklı; dal 12.810/çatışma 81; seed 3: dal 8.370) — yani tohum değişimi gerçekten aramanın yolunu değiştiriyor; yeniden başlatma fikrinin önkoşulu sağlanıyor.
* 9.15'te parametre nesnesi pybind sarmalayıcısı; `has_` sorgusu dışa açık değil, CP-SAT yalnız değeri okur — ölçüm bunu doğruluyor.
**Sonuç:** Varsayılan 1 ile Solve sayısı, süre ve tohum eskiyle aynı. Tek sapma B4'te.

### B3 — (A, soru 2) Aynı `kuruldu.m` üzerinde ardışık Solve güvenli — not
**Nasıl:** `d1`/`d2`: `str(k.m.Proto())` Solve öncesi ve 4–9 Solve sonrası **aynı** (ipucu, alan, amaç değişmiyor). Her denemede yeni `CpSolver` kuruluyor, parametre mirası yok. Süre yalnız `max_time_in_seconds` ile sınırlı (callback/bekçi yok); amaçsız arama ilk çözümde kendiliğinden durur. Paralel yol için `Clone()` bağımsızlığı da ölçüldü: kopyada `ClearHints()` ve alan değişikliği asıl modeli etkilemiyor.

### B4 — (A, soru 3) Bütçe aritmetiği uçtan uca tutuyor; "birebir" iddiasının küçük bir sınırı var — not
**Nasıl:** `d3_butce.py`: `coz()` ile `_sahne(5)`, ilk N Solve `max_time` kadar uyuyup UNKNOWN dönecek şekilde zorlandı (gerçek zaman), sonrası gerçek arama. `ilk_asama_sn + ana_asama_butce_sn`:

| azami | deneme | fm-siz denemeler | ilk_asama | ana_butce | toplam |
|---|---|---|---|---|---|
| 10 | 3 | 3 × 1,0 sn (pay 2 → taban 1) | 3,01 | 6,99 | 10,00 |
| 10 | 1 | 1 × 2,0 | 2,01 | 7,99 | 10,00 |
| 5 | 3 | 3 × 1,0 | 3,01 | 1,99 | 5,00 |
| 4 | 3 | 3 × 1,0 (pay 0,8) | 3,01 | 1,00 | **4,01** |
| 4 | 1 | 1 × 1,0 (pay 0,8; eski kod 0,8 verirdi) | 1,01 | 2,99 | 4,00 |
| 30 | 3 | 3 × 2,0 | 6,01 | 23,99 | 30,00 |

* `dusulecek` doğru işliyor: azami 10/deneme 3'te iyileştirmeye `min(8−3, 10−3−1)=5` sn, azami 30'da `min(24−6, 23)=18` sn verildi (çağrı süreleri çıktıda).
* Taşma yalnız `pay < deneme` (azami < 5·N) hâlinde ve 1 sn tabanından; belgelenmiş. Gerçekçi bütçelerde yok.
* **Sapma:** `parca = max(1.0, pay/adet)` tabanı **deneme=1 iken de** uygulanıyor: pay < 1 sn (azami < 5 sn) ise eski kod 0,8 sn, yeni kod 1,0 sn arıyor. Pratikte anlamsız bütçe, ama "varsayılan 1 = birebir" iddiası tam değil; isteniyorsa `parca = pay if adet == 1 else max(1.0, pay/adet)` ya da docstring'e "azami ≥ 5 sn" notu.

### B5 — (B, soru 4) İpucu her yolda TAM ve GEÇERLİ — ölçüldü, sorun yok — not
**Nasıl:** `d4_ipucu.py`, `d5_olcek.py`: `_ipucu_ver` → `_atamalari_sabitle` → `_ipucu_planini_al` akışında ipucu uzunluğu = değişken sayısı (466/466, 474/474, 59.812/59.812, 123.935/123.935); sabitlenmiş çözüm ipucuyla **0 değişkende farklı** (bütün değişkenler, yalnız x değil). Akış doğrulaması: `_tam_ipucu_yaz` `ResponseProto().solution`'ı (tam uzunluk) yazar; `yedek` tam ipucunun kopyası; `_molalari_serbest_birak` [0,1]'e açar, ipucu değerleri 0/1; fm alanları eski alana döner, ipucu değeri alanın içinde; `_atamalari_sabitle` x'leri ipucudan okuyup sabitler → çelişki kurulumca imkânsız. İyileştirme kapalı (`ilk_asama_iyilestirme_saniye: 0`) ve `ipucu_korundu`/plansız yollarında da ipucu tam (d4 c'). Paralel yolda K-63 asıl modelin ipucusunu kullanıyor (d4 son blok: `paralel` iki kol plansız, `ipucu_plani.bulundu True`, amaç 9.000, JSON serileştirilebilir).

### B6 — (B, soru 5) Sabitleme ipucuyu **aynen** alır; ceza değişkenlerini **sıkılaştırmaz** → K-63 planının `amac_degeri`/`amac_dagilimi` ipucunun gevşek değerleridir — **düzeltilmeli (bloklayıcı değil)**
**Nasıl:**
* Gevşek ipucu kabul ediliyor (d4 d): `_sahne(5)` ipucusunda bir `fm_` değeri 0 → 600 yazıldı (alan üst sınırı); `_ipucu_planini_al` → `bulundu True, OPTIMAL`, `amac = 30.360` (planın gerçek amacı 360). Yani "geçersiz ipucu" korunması yalnız kısıt ihlalini yakalar, amaç gevşekliğini değil.
* İkinci aşamanın (c2) ipucusu pratikte neredeyse sıkı ama tam değil — aynı x/mola/dinlenme için en küçük amaç (`ortak.tam_amac`: karar değişkenleri sabit, amaç en küçüklenir) ile kıyas:
  * 0.1 ölçek, 24 sn iyileştirme: ipucu 3.938, sıkı 3.935 (+3, `ha`).
  * 0.2 ölçek, 24 sn: 8.915 / 8.912 (+3).
  * 0.2 ölçek uçtan uca (azami 20, ana aşama UNKNOWN): dönen planın `amac_degeri` **9.172**, sıkı **9.062** (+110 = %1,2; `he` 72, `ag` 20, `ha` 18).
  * 0.2 doğal koşu: 9.639 / 9.630 (+9).
* **Amaçsız (birinci aşama) planın** ceza değişkenleri **çok gevşek**: 0.1'de ipucu amacı 11.792, sıkı 6.227 (+5.565, %89; tamamı `me_` MOLA_KAPSAMASI); 0.2'de 26.392 / 14.268 (+12.124, %85). Küçük sahnelerde (presolve'da çözülen) sıkı çıkıyor; ölçekte değil.
**Neden önemli:** K-35/#9.5 kartı planları `amac_degeri` ile kıyaslıyor; K-63 planı ile olağan plan (mola adımı ceza değişkenlerini yeniden en küçükler) aynı ölçekte değil. `amac_dagilimi` da aynı gevşek değerlerden.
**Öneri:** `_ipucu_planini_al`'da bütün değişkenleri değil **yalnız karar değişkenlerini** (x, mola, dinlenme) ipucu değerine (alan daraltarak) sabitleyip amaçla çözmek: yayılım ceza değişkenlerini en küçüğe indirir, durum yine OPTIMAL. Prototip `d8_siki_oneri.py` / `d8b_sure.py` (0.2 ölçek, 1 işçi, 3 tekrar): fix-all 0,77–0,86 sn, amaç 8.757; öneri — Clone 0,06 + 120.841 alan düzenleme 0,43 + çözüm 0,11–0,15 sn = **0,63 sn**, amaç **8.754 = alt sınır**, karar değişkenlerinde **0 fark** (atamalar ve molalar aynen; plan "ikinci aşamanın planı" olmaya devam eder). Model `coz` içinde zaten tek kullanımlık olduğundan Clone bile gerekmeyebilir (`_atamalari_sabitle` gibi yerinde). Alternatif: fix-all'ı bırakıp `amac_degeri`/`amac_dagilimi`'nı ayrı bir sıkılaştırma çözümünden yazmak.

### B7 — (B) İyileştirme plan bulamadıysa / ipucu korunduysa dönen plan **birinci aşamanın amaçsız planıdır**, not yine "ikinci asamanin plani dondu" der — **düzeltilmeli (metin + amaç)**
**Nasıl:** `d4` (c'): `_iyilestirme_coz` UNKNOWN + ana aşama UNKNOWN zorlandı (küçük sahneler): `durum cozuldu`, `sebep mola_adimi_yetismedi`, `ilk_asama_iyilestirme.plan_bulundu False`, notta "ikinci asamanin plani dondu". Bu durumda plan `_tam_ipucu_yaz(kuruldu, c)`'nin (amaçsız) planıdır; ölçekte `amac_degeri` %85–89 şişkin olur (B6). Aynı şey `ipucu_korundu: True` yolunda (yedek = amaçsız ipucu). Olasılığı düşük (ipucu tamken iyileştirme genelde ilk çözüm olarak ipucuyu alır) ama tam ölçekte bütçe darsa (presolve birkaç sn) mümkün; çıktı o zaman yanıltır.
**Öneri:** Not metnini `kuruldu.ilk_asama_iyilestirme` durumuna göre seçmek ("birinci asamanin amacsiz plani dondu (iyilestirme plan bulamadi)" / "...ipucu korundu"), B6'daki sıkılaştırmayla amacı doğru yazmak; `test_mola_adimi_yetismedi.py`'ye bu iki yol için test.

### B8 — (B, soru 7) Çevirme süresi ve 0.2 ölçek uçtan uca — not (tam ölçek Mustafa'nın makinesinde)
**Nasıl:** `d5_olcek.py` (2 çekirdek, 1 işçi, fix-all):
* 0.1 ölçek (59.812 değişken): `_ipucu_planini_al` **0,33 sn** (3 tekrar: 0,33/0,33/0,35).
* 0.2 ölçek (123.935 değişken): **0,72–0,81 sn**. 2 işçi ile 0,75 (fark yok).
* Doğrusal dışdeğerleme: değişken sayısı kişiyle ~doğrusal (0.1→0.2: ×2,07), süre ×2,3 → 500 kişide (~600 bin değişken) **≈ 4 sn** (bu makinede). `ipucu_plani_saniye` 30 tavanı yeterli görünüyor; ama `VARSAYILAN` yorumundaki **"tipik olarak 1 sn'nin altinda"** 0.2 ölçekte zaten 0,75 sn — tam ölçekte tutmayacak gibi; ölçüm sonrası yorum güncellenmeli. Tavan aşılırsa cevap eski cevap ("sure yetmedi") — zarif.
* **Uçtan uca 0.2, azami 20, ana aşama UNKNOWN zorlanmış:** `cozuldu`, `mola_adimi_yetismedi`, `ipucu_plani {True, 0.81, OPTIMAL}`, `alt_sinir`/`mola_adimi_alt_sinir`/`optimuma_uzaklik_yuzde` None, `cozum_sayisi 0`, `ilk_cozum_sn None`, `iyilesme None`; **doğrulayıcı yayınlanabilir = True, sert ihlal 0**; duvar saati 19,1 sn.
* **Uçtan uca 0.2, azami 20, DOĞAL koşu:** bulgu 24 kendiliğinden oluştu — mola adımına 1,68 sn kaldı, UNKNOWN; K-63 planı döndü (0,74 sn), doğrulayıcı yayınlanabilir; toplam duvar **20,7 sn** (bütçe + çevirme; belgelendiği gibi bütçe dışı tek kalem).

### B9 — (B, soru 6) Alanların tutarlılığı — not
`kapsam` "mola_adimi" kalıyor, `sinir=None` → üç sınır alanı None; `sebep` `_durma_sebebi`'nin "optimum"una (sabit modelin OPTIMAL'i) rağmen `mola_adimi_yetismedi`'ye eziliyor (sıra doğru: `_paralel_kisitli_isaretle`'den sonra). `iyilesme None`, `cozum_sayisi 0`, `ilk_cozum_sn None` ana aşamanındır — tutarlı ama **`durum: cozuldu` + `cozum_sayisi: 0` + `cozum_suresi_sn` = başarısız ana aşamanın süresi (doğal koşuda 1,49 sn)** yeni bir kombinasyon; `kalite-olc.py` None'ları kaldırıyor (`or {}`), servis/orkestra bu alanlara bakmıyor (grep). Ürün kartı "çözüm süresi 1,5 sn" gösterirse yanıltır; `ilk_asama_sn` yanında olduğu için kabul edilebilir, spec'te açıkça yazılmalı. `_paralel_kisitli_isaretle` K-63'te zararsız (kollar plansız: `alt_sinir None`, `durma_sebebi None` kalıyor; ölçüldü).

### B10 — (8) Testler ve mutasyonlar
Verilen gruplar (`k63.txt`: 16 mutasyon, 0 yaşayan; `fm_sifir.txt`: 59 mutasyon, 0 yaşayan, 1 atlanan çapa — sonradan düzeltildiği belirtildi) 16:14 zincirinden önce bitmiş (dosya saatleri 15:51 ve 16:01); üst üste binme kanıtı 16:14:32'ye ait, o koşuları doğrudan suçlamıyor. Yine de temiz checkout'ta bir kez daha koşmak ucuz (k63 ~20 sn, fm_sifir ~10 dk) ve B1'den sonra gerekli. Dondurulmuş kopyada iki test dosyası 48/48 yeşil. Ellle 20 ek mutasyon (`d6_mutasyon.py`, ayrı kopyada):

| Mutasyon | Sonuç | Yorum |
|---|---|---|
| `durum_kodu` hep OPTIMAL | yaşıyor | **eşdeğer** (bulundu False'ta kullanılmıyor; True'da sebep zaten eziliyor) |
| `durum` adı hep "OPTIMAL" | öldü | gecersiz-ipucu testi |
| tohum hep 1 / i+2 / `pay/(adet+1)` | öldü | bölüm 7 |
| `tohum = len(denemeler)+1` | yaşıyor | eşdeğer |
| not "mola adimi"/"ana asama" ters | öldü | |
| K-63 başlangıç planında da / yalnız atamalar sabitken | öldü | |
| `ipucu_plani` yalnız bulununca yazılsın | öldü | |
| tavan `or 30` | öldü | |
| **not sınırı `> 1` → `>= 1`** ("(1 denemede)") | **yaşıyor** | boşluk: tek denemede "(1 denemede)" ürün notuna sızar, hiçbir test görmez (kozmetik) |
| `deneme_siniri = len(denemeler)` | öldü | |
| `dusulecek = sum(denemeler)` | yaşıyor | ~eşdeğer (0,05 sn tolerans) |
| `fm_once.saniye` = son denemenin süresi | öldü | |
| **K-63: `sure += ipucu_plani.saniye`** | **yaşıyor** | boşluk: "çevirme süresi `cozum_suresi_sn`'ye girmez, bütçe dışı" iddiası test edilmiyor |
| sebep `mola_adimi` ayarına göre | yaşıyor | pratikte eşdeğer (iki aşama varken ipucu tam → `atamalar_sabit == mola_adimi`) |
| ipucu eksik `<=` | öldü | |
| ilk deneme payın tamamı | öldü | |
| `denemeler = []` | yaşıyor | eşdeğer |

**Test edilmeyen iddialar:** (1) `coz()` uçtan uca deneme=3 bütçe (`ilk_asama_sn + ana_asama_butce_sn ≤ azami`) — yalnız mock'lu; D3 ölçtü, tutuyor. (2) K-63'te dönen planın `amac_degeri`'nin plana ait sıkı amaçla eşitliği — yok; B6'da ölçülen fark var. (3) İyileştirme plansız / `ipucu_korundu` iken K-63 çıktısı — yok (B7). (4) `cozum_suresi_sn` çevirmeyi kapsamaz — yok. (5) not sınırı — yok. (6) 0.2 ölçek K-63 + doğrulayıcı — yalnız bu inceleme (B8). (7) "varsayılan 1 birebir" yalnız parametre kaydıyla sınanıyor; tohum eşdeğerliği B2 ile ölçüldü (teste 1 işçi/deterministik kıyas eklenebilir ama ortools sürümüne bağlı, zorunlu değil).

### B11 — (9) Dokümantasyon / isimlendirme — not
* "1 = kütüphanenin varsayılanı = bugünkü arama" doğru (ölçüldü). `(2/35)^3 ≈ %0,019 ≈ "~%0,02"` doğru. "INFEASIBLE kanıt, tohum değiştirmez" doğru.
* K-63 notu: "optimuma yakınlık kanıtı yok" doğru; "molalar şablonun ideal yerinde" `ilk_asama_sabit_mola` (belgesiz seçenek, varsayılan True) kapalıysa yanlış olur; "ikinci aşamanın planı" B7'deki yollarda yanlış.
* `VARSAYILAN["ipucu_plani_saniye"]` yorumu "tipik olarak 1 sn'nin altında": B8'e göre tam ölçekte ~4 sn beklenir; ölçüm sonrası güncellenmeli.
* Kod içi isim karmaşası: `_ipucu_ver`'de `deneme` bir **süre** (saniye), `denemeler` bir **liste**, `fazla_mesaisiz_deneme` bir **sayı**; geliştirici için yanıltıcı (`deneme_sn` daha açık).
* Ürün ekibi için `ipucu_plani` jargon ("ipucu" = çözücünün başlangıç çözümü); spec v1.4 #3723 açıklıyor, kabul edilebilir; `durma_sebebi: mola_adimi_yetismedi` açık.
* `fazla_mesai_once_sifir.saniye` ("bütün denemelerin toplamı, bulunan dahil") doğru; testte 0,05 toleransla doğrulanıyor.

### B12 — Kapsam dışı ama bitişik gözlemler (ölçüldü)
* **K-61 `ipucu_korundu` kıyası gevşek amaca dayanıyor:** `iyilesmis_amac > amacsiz_amac` kıyasında `amacsiz_amac` amaçsız çözümün gevşek ceza değerleriyle hesaplanıyor (0.1'de 11.792; gerçek 6.227). Dolayısıyla "ipucudan kötü plan ezilmez" güvenlik ağı, gerçek amaçtan %85–89 yukarıda bir eşikle çalışıyor. B6'daki sıkılaştırma (karar değişkenleri sabit, amaç en küçük; 0,3–0,6 sn) burada da kullanılırsa kıyas anlamlı olur. (7 Ekim sabahının kodu; bugünkü diff'in dışında.)
* **Donmuş gün × iki aşama:** `d7_donmus.py` — `mevcut_plan` oturmayan bir satır içerdiğinde (`_plandan_ipucu` False) iki aşama yolu koşuyor ve `_molalari_sabitle`/`_molalari_serbest_birak` donmuş gün 0'ın `[0,0]`/`[1,1]` mola alanlarını `[0,1]`'e açıyor (48 alan değişti). Donmuş satırlar çıktıya aynen aktarıldığı ve yalnız-donmuş kısıtlar düştüğü için görünür etkisi ölçülmedi; yine de K-54 değişmezi bozuluyor. Bugünkü değişiklikle ilgisiz; ayrı bir kayıt olarak öneririm.

---

## 2. Özet ve karar

**Koda inmeye hazır — bloklayıcı bulgu yok.** (A) varsayılan 1 ile Solve sayısı, süre, tohum ve model durumu eskiyle birebir (ölçüldü; tek sapma azami < 5 sn'deki 1 sn tabanı), bütçe aritmetiği uçtan uca tutuyor. (B) ipucu her yolda tam ve geçerli, sabitleme ipucuyu birebir plana çeviriyor, 0.2 ölçekte K-63 doğal koşuda devreye girip doğrulayıcıdan geçen plan döndürüyor (0,74–0,81 sn).

Girmeden/girerken yapılacaklar (öncelik sırasıyla):
1. **(süreç)** İnceleme paketindeki `coz.py`'yi yeniden üretmek (mutant kopya); mutasyon koşturucuyu çalışma kopyası dışında koşturmak — B1.
2. **(düzeltilmeli)** K-63 planının `amac_degeri`/`amac_dagilimi`'nı sıkı hesaplamak: yalnız karar değişkenleri ipucuya sabit + amaç (ya da ayrı sıkılaştırma adımı) — B6; aynı yardımcı K-61 `ipucu_korundu` kıyasını da düzeltir — B12.
3. **(düzeltilmeli)** İyileştirme plansız / ipucu korundu yollarında not metni ("birinci aşamanın amaçsız planı") ve bu iki yol için test — B7.
4. **(not)** Testler: `cozum_suresi_sn` çevirmeyi kapsamaz; not sınırı `> 1`; uçtan uca deneme=3 bütçe — B10.
5. **(not)** Yorumlar: "1 sn'nin altında" iddiasını tam ölçek ölçümüne bağlamak; `deneme` değişken adı — B8, B11.

## 3. Tekrar üretme

```
S=/tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/inceleme3/deneme
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d1_tohum.py          # tohum (küçük sahne, presolve'da çözülür)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d2_tohum_01.py       # tohum 0.1 ölçek (B2, B3)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d3_butce.py          # bütçe uçtan uca (B4)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d4_ipucu.py          # ipucu birebir / gevşeklik / c' (B5–B7)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d5_olcek.py 0.1 30 ipucu
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d5_olcek.py 0.2 30 ipucu
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d5_olcek.py 0.2 20 uctan
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d5_olcek.py 0.2 20 dogal   # B8
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d6_mutasyon.py       # ek mutasyonlar (B10; mut/ kopyasında)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d7_donmus.py         # kapsam dışı (B12)
cd $S && PYTHONDONTWRITEBYTECODE=1 python3 d8_siki_oneri.py && python3 d8b_sure.py   # B6 öneri prototipi
cd $S/depo/09-motor && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest testler -q -p no:cacheprovider   # 604 passed
```
