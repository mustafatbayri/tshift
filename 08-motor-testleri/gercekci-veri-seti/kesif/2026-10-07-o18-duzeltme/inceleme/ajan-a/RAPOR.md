# Bağımsız inceleme (ajan-a) — "önce fazla mesaisiz" düzeltmesi (7 Ekim, O-18)

Koşu ortamı: Python 3.13, OR-Tools 9.15, 2 çekirdek, başka test koşusu açıkken; süreler değil sonuç/puanlar ölçüldü. Bütün betikler ve çıktılar `ajan-a/` altında; `calisir/` kopyası `ajan-a/calisir/`. Başlangıç 01:16, bitiş 01:36 UTC.

## ÖZET

Düzeltme ilkeyi ("hakem ağırlıklardır") **sağlıyor**: kod okumasında bulununca fazla mesai alanları gerçekten geri açılıyor, fazla mesaisiz plan TAM ipucu olarak iyileştirmeye gidiyor, mola adımı tam modelde koşuyor; beş karşı örnekte URUN = kanıtlı optimum (750/750/9000/750/750), SERT eski yanlışı veriyor (2256/880/12000/900/2000). Kendi avımda 640 rastgele küçük sahnede (kanıtlı optimumla kıyas) URUN puanı 640/640 TAM'a eşit; bunların 50'si tam hedef sınıfta (fazla mesaisiz plan VAR ama optimum fazla mesaili) ve 50/50 eşit — (a) sınıfı "fazla mesai kaynaklı kayıp" sıfır. En ciddi bulgu: resmî mutasyon listesindeki **"ipucu fm değerleri silinsin" (#64) mutantı bu ortamda `AttributeError: __delitem__` ile ÇÖKÜYOR** — "OLDU" kaydı testin iddiasının kanıtı değil, çökmenin kaydı (düzeltilmiş hâliyle de ölüyor, o kısım iyi). Ayrıca iki anlamlı mutant yaşıyor: mola adımına giden ipucunun fm değerleri yanlış/eksik yazılsa hiçbir test görmüyor.

## Bulgular (ciddiyet sırasıyla)

### 1. Resmî mutasyon #64 ("O-18: ipucu fm degerleri silinsin") çalışmayan koddan ibaret — sahte "OLDU"
- **Ne:** `mutasyon_kostur.py` fm_sifir grubundaki mutant `del _p.solution_hint.vars[:]; del _p.solution_hint.values[:]` kullanıyor. Bu ortamın protobuf'unda repeated alan `__delitem__` desteklemiyor; mutant uygulanınca `_ipucu_ver` her koşuda çöküyor, dosyanın İLK testi (`test_varsayilan_ACIK...`) hata ile kırmızı yanıyor. `loglar/fm_sifir2.log`'daki "44 mutasyon · yaşayan 0" bu mutant için çökme sayımıdır.
- **Kanıt:** `ajan-a/mut.py` → `R-64 RESMI #64 oldugu gibi`: `1 failed` — hata metni `cozucu/coz.py:431: AttributeError: __delitem__` (mut.log ve tek-test koşusu). Düzeltilmiş hâli (`.clear()` ile; `R-64b`) gerçekten TAM_IPUCU testince ölüyor: `FAILED ...TAM_IPUCU_olarak_gider_fm_SIFIR`.
- **Öneri:** mutantta `del x[:]` yerine `x.clear()` (kodun kendisi `_tam_ipucu_yaz`'da zaten `.clear()` kullanıyor). Genel kural: mutasyon koşturucu "OLDU"yu hata/çökme ile assertion'ı ayırsın (pytest çıktısında `Error` vs `assert`), aksi hâlde sözdizimi/çalışma hatası veren her mutant "yakalandı" sayılır.

### 2. Mola adımına giden ipucu denetlenmiyor — iki mutant yaşıyor
- **Ne:** İyileştirme bittikten sonra `_tam_ipucu_yaz(kuruldu, c2)` mola adımının ipucusunu yazar; `_atamalari_sabitle` yalnız x'leri okur. İpucunun fm değerleri bozulursa (hep 0 yazılsa ya da silinse) hiçbir test görmüyor. Küçük modelde sonuç değişmiyor (x sabitken mola adımı zaten çözüyor); tam ölçekte yarım/yanlış ipucu T-60'ın ölçtüğü "ipucu onarımı → ilk plan 57-101 sn" riskini mola adımına taşır.
- **Kanıt:** `mut.py` → `G-3 _tam_ipucu_yaz fm ipucularini hep 0 yazsin`: **YAŞADI** (28 passed). `G-4b iyilestirme SONRASI fm ipuclari silinsin (.clear())`: **YAŞADI** (28 passed).
- **Öneri:** `_durgunluk_bekcisiyle_coz` girişinde ipucuyu okuyan bir test (TAM_IPUCU testinin ikizi): Mustafa'nın örneğinde (HEDEF 2000) ipucu tam (`len == degisken`) ve fm_ ipucu değerleri = 180 dk olsun. Bu iki mutant listeye eklenebilir.

### 3. 20 sn bütçede 49 kişide `sure_yetmedi` — elde plan varken boş dönüş; düzeltmeden bağımsız, önceden var
- **Ne:** `loglar/duman-49.jsonl` (20 sn): sert ve yeni yollarda `durum=sure_yetmedi, sebep=butce_doldu, ilk_asama=17.75, ana=2.25-2.3 sn`; kapalı yolda `ilk=17.2-17.3, ana=2.7-2.8` ve çözüldü. Hesap: ilk aşama payı min(120, 20×0,2)=4 sn; fazla mesaisiz arama 1,35 sn; iyileştirme tavanı 20×0,8=16 sn ve bulununca `dusulecek=0` → iyileştirme 16,02 sn → mola adımına `max(1, 20-17,75)=2,25 sn` kalıyor; 49 kişilik modelde bu sürede ilk çözüm gelmiyor, `coz()` plan yokken ipucuya düşmeden `sure_yetmedi` döndürüyor (`coz.py` 1006-1016: UNKNOWN → sure_yetmedi; ipucudaki planı döndüren bir yol yok). `_ipucu_ver` docstring'indeki "bütçe dolsa bile çıktı boş kalmaz" cümlesi mola adımı (K-60) için geçerli değil; `_ilk_asamada_iyilestir` docstring'i bunu zaten kabul ediyor ("elde plan varken 'sure yetmedi' doner").
- **Düzeltmeden bağımsız mı:** Evet. Yeni ve sert yolların ilk aşama süreleri aynı (17,74 / 17,75); kapalı yol da aynı yapıyla (20% payı - amaçsız arama süresi) çalışıyor, yalnız amaçsız araması 1 sn daha kısa sürdüğü için 2,8 sn'ye sığdı. Kaynak: K-60 (4 Ekim) %80 iyileştirme payı + bulununca deneme süresinin düşülmemesi (bu düzeltmede değişmedi; 00:45 sürümünde de `dusulecek` yalnız başarısızlıkta).
- **Öneri:** mola adımı plan bulamazsa (durum UNKNOWN) elde TAM ipucu varken ipucudaki planı `cozuldu` + not ("mola adımı süreye sığmadı; iyileştirmenin planı döndü, molalar şablonun ideal yerinde") olarak döndürmek; ya da mola adımına asgari pay (ör. bütçenin %10'u) ayırıp iyileştirmeyi ona göre kırpmak.

### 4. Ölçüm aracı: eski kayıtta `uygulandi: False` sözlüğü `fm_once_yazisi`'nı KeyError ile düşürüyor
- **Ne:** 00:45 sürümü ağırlık koşulu tutmayınca `{"uygulandi": False, "sebep": "agirlik", ...}` yazıyordu (`bulundu` anahtarı yok). Yeni `fm_once_yazisi` o dalı sildi ve doğrudan `f["bulundu"]` okuyor.
- **Kanıt:** `fm_once_yazisi({"fazla_mesai_once_sifir": {"uygulandi": False, "sebep": "agirlik", ...}}, {"fazla_mesai_once_sifir": True})` → `KeyError: 'bulundu'` (ajan-a koşusu). Diğer iki hâl doğru: eski `uygulandi: True` kaydı → "SERT KESIM ... (olcum)"; yeni ürün kaydı → "ipucu oldu, alanlar geri acildi".
- **Etki:** 6 Ekim 22:45 – 7 Ekim 00:55 arasında ağırlıkları değiştirilmiş ve seçeneği açık bir kayıt varsa rapor çöker (`fm_agirlik_*` yapılandırmaları KAPALI'yı açıkça taşıdığı için bulgu 21 kaydı etkilenmez). Öneri: `f.get("bulundu")` ve `uygulandi is False` için "UYGULANMADI (00:45 sürümü, ağırlık koşulu)" satırı.

### 5. Eşitlikte fazla mesaili plan seçilebiliyor (tasarım notu, düşük)
- **Ne:** Ağırlıklara göre puanı EŞİT iki plan varsa (biri fazla mesaisiz) motor fazla mesaili olanı döndürebiliyor; "belirgin daha iyiyse" ilkesi eşitlikte fazla mesaisizi tercih etmiyor.
- **Kanıt:** `av-kilit2-66.jsonl` i=6 (2 kişi, DENGELİ, SAAT_DENGESİ yumuşak): TAM 3252 (fm 0; saat dengesi 600 dk) — URUN 3252 (fm 0,5 sa = 1500 + saat dengesi 300 dk = 1500). 640 sahnede tek örnek; puan eşit olduğu için kayıp değil.
- **Öneri:** ürün kararı: eşitlikte fazla mesaisiz tercih istenirse amaç fonksiyonuna çok küçük ikincil terim (ör. fm dakikası +1) ya da sonuç kartında not.

### 6. Küçük kalıntılar (yorum/dokümantasyon)
- `coz.py` 883-890 (`coz()` içindeki O-16 bloğu): "fazla_mesaisiz: ... fazla mesai degiskenleri 0'da kaldi (K-61)" — artık yalnız ölçüm seçeneğinde (`fazla_mesai_sifirda_tut`) oluşuyor, blok bunu söylemiyor (`_sinir_kapsami` docstring'i doğru).
- `kalite-olc.py` 180-183 (`fm_once_kapali` üstündeki OLCUM yorumu): "bulursa fazla mesai butun asamalarda 0'da kalir" ürün yolu gibi yazılmış; sert kesime özgü olduğu belirtilmeli. Diğer yapılandırmalar tutarlı: `fm_once` = {True, False} = ürün yolu (= varsayılan), `fm_sert` = {True, True}, bulgu 21 adları (`fm_once_sifir*`) `dict(SERT)`'e sabit; kayda `sert_kesim` alanı eklenmiş.
- Kodda `uygulandi` / `kisayol` / `_fazla_mesai_kisayolu_gecerli` kalıntısı yok (grep: yalnız ilgisiz "gruplu talep kısayolu").
- `loglar/fm_sifir2.log` ve `zincir.log` mutasyon bölümlerinde yalnız YASADI satırları var, OLDU satırları yok; hangi mutantı hangi testin öldürdüğü logdan doğrulanamıyor (bulgu 1'i de bu yüzden log değil, yeniden koşu gösterdi).
- `zincir.log`: V5 ALTIN 7 failed ("motor_istemci...") — bu düzeltmeyle ilgisi yok, servis gerektiriyor; not olarak.

## Görev 1 — coz.py farkı (satır satır)
- Bulunursa yol: `sifirda = bulundu and ayar["fazla_mesai_sifirda_tut"]` → ürün yolunda False → `_fazla_mesaiyi_serbest_birak` (393-401) → `_tam_ipucu_yaz(c)` (427; çözüm vektörü tüm değişkenler, fm_=0) → `_ilk_asamada_iyilestir` tam ağırlıklı amaçla, molalar sabit, fm alanı [0,600] (test TAM_IPUCU bunu okuyor) → bulursa `_tam_ipucu_yaz(c2)` → `finally` molaları açar, amacı geri koyar → `coz()` `_atamalari_sabitle` x'i iyileşmiş plana sabitler, mola adımı fm serbest. Doğru.
- Bulunamadı yolu: `sifirda=False` → alanlar açılır → not + `dusulecek=deneme` → `_gecerli_plan_yeniden_ara` (fm serbest). Doğru; sert seçeneği açıkken de aynı (test `SERT_KESIM_bulunamazsa`).
- Sert kesim (`sifirda=True`): alanlar [0,0] kalır; `_sinir_kapsami` "fazla_mesaisiz" yalnız `sifirda_tutuldu` ile; ürün yolunda atamalar sabitken "mola_adimi". Doğru.
- İpucu geçerliliği: fm_ değişkeni `fazla >= dakika - tavan` ile yalnız alttan bağlı; fm'siz çözümde dakika ≤ tavan olduğundan fm=0 açık alanda da uygulanabilir → ipucu tam ve geçerli. `_tam_ipucu_yaz` `ResponseProto().solution`'ı okuduğu için alan açılışından bağımsız.
- Kaçırılmış yol yok. `finally` fm'yi açmaz ama fm açma `if fm_eski:` bloğunda her hâlde (sert dışında) çalışıyor; `c.Solve` istisna atarsa fm kapalı kalır — o hâlde çağrı zaten çöker, ürün etkisi yok.
- `_CozumSayaci.egri`, `_iyilesme_ozeti(nokta=24)`, `int(round())` üç yerde: farkla uyumlu.
- Yorumlar: başlık AKIS ve VARSAYILAN notları güncel; kalıntı yalnız bulgu 6'dakiler.

## Görev 2 — dogrula.py
`MOTOR=ajan-a/calisir/09-motor PYTHONDONTWRITEBYTECODE=1 python3 dogrula.py` → `ajan-a/dogrula.log` (iki bağımsız koşu, aynı sayılar):

| sahne | TAM (kanıtlı) | URUN | SERT |
|---|---|---|---|
| S1 tek kişi DENGELİ yumuşak | 750 (fm 0,25) | 750 (fm 0,25) | 2256 (fm 0) |
| F2 tek kişi KAPSAMA sert | 750 | 750 | 880 |
| S3b 12 kişi KAPSAMA | 9000 (fm 3,0) | 9000 (fm 3,0) | 12000 |
| S3c iki ekip DENGELİ | 750 | 750 | 900 |
| S3d iki ekip KAPSAMA | 750 | 750 | 2000 |

Hepsinde URUN `bulundu: True, sifirda_tutuldu: False`, yayın kapısı True; SERT `sifirda_tutuldu: True`.

## Görev 3 — karşı örnek avı (ajan-a/av.py)
- Üretici: 1-6 kişi, çeyrek saat ızgaralı şablonlar (net 6-9,5 sa + 60 dk ücretsiz yemek), gün kısıtları, SAAT_DENGESİ yok/YUMUŞAK/SERT (tolerans 0), iki ekip + çift üyelik (%40), sözleşme 40/45, hedef/asgari çeşitleri, DENGELİ/KAPSAMA. Üç kip: genel (tohum 11, 22), `kilit` (fm'ye meyilli; tohum 33, 44), `kilit2` (S1 yapısının genellemesi: ana şablon 5 gün + tek şablon 6. gün, 5x+y sözleşmeyi 15-45 dk aşar; tohum 55, 66). Fizibilite ön kontrolü amaçsız çözümle; TAM = {azami 40, 2 işçi, hedef_bosluk 0, fm_once_sifir False}, URUN = varsayılan iki aşamalı yol; `durma_sebebi != "optimum"` veya `alt_sinir != amac` olan TAM kıyasa girmedi.
- Sayılar: 647 kayıt, **640 kıyas** (7 kanıtsız atıldı, 229 uygunsuz sahne atlandı). **URUN amaç = TAM amaç: 640/640**; URUN fm = TAM fm: 639/640 (tek fark bulgu 5'teki eşit puanlı alternatif optimum). Optimumda fm>0 olan 127 sahne: 77'sinde fm'siz plan yok (`bulundu: False`, zorunlu fazla mesai), **50'sinde fm'siz plan var ama optimum fazla mesaili (hedef sınıf) → 50/50 eşit**, fm 0,25-3,0 sa, n 1-6, DENGELİ 34 / KAPSAMA 16. Sınıf (a) 0, (b) 0, (c) 0 — iyileştirme 50/50'de sabit molalı optimuma ulaştı, mola adımı optimumda durdu. Yayın kapısı 640/640 True. Sahneler: `av-*.jsonl` (her kayıtta tam istatistik), hedef sınıf özeti `hedef-sinif/ozet.json`; `gap-*/` boş (URUN>TAM sahne yok).
- Gözlem: hedef sınıfta iyileştirme eğrisinin ilk noktası 44/50'de amaçsız planın puanından düşük — CP-SAT'in raporladığı ilk çözüm ipucunun kendisi değil; sonuç etkilenmiyor (TAM_IPUCU testi ipucunun gittiğini doğruluyor). İlk incelemenin 200 sahne hedefi aşıldı; ancak ilk 240 genel sahnede hedef sınıf HİÇ çıkmadı (fm>0 olan 44 sahnenin hepsi zorunlu) — rastgele genel üretici bu düzeltmeyi sınamaz, hedefli `kilit2` kipi gerekti.

## Görev 4 — testler ve mutasyonlar
- Testler iddialarını sınıyor: bölüm 1 alan/ipucu okumaları beyaz kutu (monkeypatch ile `_durgunluk_bekcisiyle_coz` / `_iyilestirme_coz` girişinde alan ve ipucu); TAM_IPUCU testi `len(ipucu) == degisken`, fm ipucu 0, fm alanı [0,600] — tautolojik değil (M-C, R-64b, G-2 onunla ölüyor). 3b `mola_adimi=False` ile sınır alanlarını ayırıyor. Bölüm 5 O-18 sahneleri incelemeden alınmış (regresyon için beklenen); genelleme kanıtı bu rapordaki av. `test_K61_...AYNI_puanda` ve `test_O18_...` kanıtlı optimumu `_kanitli_optimum` ile doğrulayıp kıyaslıyor — doğru kurgu. Zayıf nokta: `iy["iyilesmis_amac"] <= iy["amacsiz_amac"]` çoğu sahnede büyük farkla doğru, az şey söylüyor.
- `test_demir_secenekleri::test_O16_sinir_kapsami` saf birim testi; G-5 (sıra değişimi) onu kırıyor (`1 failed`), fm_sifir dosyası tek başına yakalamıyor (28 passed) — fm_sifir grubunun `_sinir_kapsami` mutantları o dosyaya değil demir dosyasına bağlı olmalı ya da iki dosya birden koşulmalı.
- Eklenen fm_sifir mutasyonları (44): değişen satırlar koşulan yolda (sifirda satırı, serbest bırakma `if`, `_sinir_kapsami`, eğri, round). Eşdeğer/geçersiz: #64 çöküyor (bulgu 1). Diğerlerinde eşdeğer mutant bulmadım; ancak logda OLDU satırları olmadığından 44'ün tamamını yeniden koşmadım (süre).
- Elle uygulanan ve kırmızıya dönen (hepsi `ajan-a/mut.log`): M-A `sifirda = False` → `test_SERT_KESIM_olcum_secenegi...` kırmızı; M-B serbest bırakma `if not bulundu` → `test_varsayilan_ACIK...`; M-C ipucu yazıldıktan sonra silinsin → TAM_IPUCU; M-D `sifirda = bulundu` → `test_varsayilan_ACIK`; G-1 iyileştirme sonucu ipucuya yazılmasın → `test_MUSTAFANIN_ORNEGI`; G-2 iyileştirme fm'siz modelde → TAM_IPUCU; G-6 yalnız bulununca aç → SERT testi; G-7 bulununca iyileştirme atlansın → `test_fazla_mesaisiz_plan_VARSA`; R-64b (düzeltilmiş #64) → TAM_IPUCU.

## Görev 5 — 49 kişi
- 30 sn (`duman-49-30sn.jsonl`): yeni yolda iyileştirme fm'siz ipucudan başlıyor ve **fazla mesaiye dönmüyor** (`fm_izi` [[0.8, 0]] — tek nokta, 0 dk); amaç yeni 2722/2689, sert 2717/2719, kapalı 15478/15469 (fm 4,25 sa = 12750 puan arama artığı). Yeni ≈ sert (fark %0,2-1,1, koşudan koşuya gürültü içinde), ikisi de kapalıdan 5,7 kat iyi. Bu ölçekte "alanlar açık" fazla mesai eklemedi: ağırlıklar fm'yi kazandırmıyor, bulgu 21'in kazancı korunuyor.
- 20 sn (`duman-49.jsonl`): sert/yeni `sure_yetmedi` — sebebi ve bağımsızlığı bulgu 3'te. olc3.py'yi makine yükü (iki av + mutasyon koşusu) yüzünden ayrıca koşturmadım.

## Görev 6 — kalite-olc.py
Yapılandırmalar tutarlı (bulgu 6'daki yorum ve bulgu 4'teki KeyError dışında): `fm_once`/`fm_once_kapsama` = ürün yolu, `fm_sert*` = sert kesim, bulgu 21 adları sert kesime sabit, `varsayilan` motorun varsayılanından geliyor, `sert_kesim` alanı kayda yazılıyor; `fm_once_yazisi` eski `uygulandi: True` kaydı için "SERT KESIM (olcum)" (doğru: 6 Ekim koşuları sert kesimdi), yeni ürün kaydı için "ipucu oldu, alanlar geri acildi".

## Koşu sayıları
- dogrula.py: 5 sahne × 3 yol × 2 koşu = 30 çözüm.
- Av: 647 üretilen kayıt, 640 TAM+URUN kıyası (~1.300 çözüm), 229 uygunsuz sahne, 7 kanıtsız; hedef sınıf 50.
- Mutasyon: 14 elle mutant (M-A..D, G-1..7, R-64, R-64b, G-4b), her biri 28 testlik dosya (G-5 ayrıca demir dosyası).
- Küçük ölçek: loglar okundu; ek koşu yok.

## Yaşayan mutantlar
1. **G-3** `_tam_ipucu_yaz` fm ipucularını hep 0 yazsın (mola adımına yanlış ipucu) — 28 passed.
2. **G-4b** iyileştirme sonrası ipucudan fm değerleri silinsin (mola adımına yarım ipucu) — 28 passed.
3. **G-5** `_sinir_kapsami` sırası (sert kesim mola adımından önce) — fm_sifir dosyasında 28 passed, YALNIZ `test_demir_secenekleri::test_O16_sinir_kapsami` yakalıyor.
4. (Geçersiz) resmî **#64** `del [:]` ile çöküyor — mutant değil, hata; düzeltilince ölüyor.
