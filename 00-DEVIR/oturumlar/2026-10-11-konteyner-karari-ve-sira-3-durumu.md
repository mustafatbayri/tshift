# 11 Ekim 2026 — Yılmaz görüşmesinin sonucu: konteyner mimarisi kararı (M-16); sıra 3'ün durumu

**Pencere:** 11 Ekim 18:25 – 22:30 · **Önceki:** `2026-10-07-gece-kosusu-ve-fm-siz-arama-kuyrugu.md`
§9 (K-61 kapanışı, sıra 3'ün ilk sorusu, literatür okuması). Kod 18:30'dan
sonra değişti (§4–5).

## İçindekiler

1. [Mustafa'nın haberi ve M-16](#1--mustafanın-haberi-ve-m-16)
2. [Nerede kaldık](#2--nerede-kaldık)
3. [Sıradaki adım](#3--sıradaki-adım)
4. [İki karar ve K-66: çizelge her koşuda (18:30–19:30)](#4--iki-karar-ve-k-66-çizelge-her-koşuda-18301930)
5. [K-65 koda indi; bağımsız inceleme 4 (19:30–22:00)](#5--k-65-koda-indi-bağımsız-inceleme-4-19302200)
6. ["Önce" ölçümü (bulgu 28) ve Mustafa'ya blok](#6--önce-ölçümü-bulgu-28-ve-mustafaya-blok)

## 1 · Mustafa'nın haberi ve M-16

Mustafa (18:25): *"Yılmaz ile görüşmemiz sonucunda, tek database multitenant
id yerine, her müşteri için konteyner mimarisine geçme kararı aldık. Bunu
bir söyleyeyim, diğer konularla ilgili yorumlarını bana iletecek. Biz şimdilik
motoru yazmaya ve test etmeye devam edeceğiz."*

Kayıt: `03-MIMARI-KARARLAR.md` **M-16** — M-01'in (tek DB + `tenant_id` +
RLS) yerine her müşteri için ayrı konteyner; karar verildi, **tanımı açık,
uygulanmadı**; neye dokunduğu sayıldı (şartname §7.3/§8.1, değişmezler
K-1…K-9'un kanıt yöntemi, 45 kimlik testinin RLS'e dayananları,
`04-kod/db/rls/`, M-02/M-13/M-14; motor M-09 **değişmez** — motor kiracıyı
zaten bilmiyor) ve koda inmeden cevaplanacak yedi soru yazıldı (konteynerin
sınırı, kimlik/yönlendirme, sürüm dağıtımı, motor havuzu mu konteyner başına
mı, RLS'in kaderi, maliyet/ölçek, yedek/silme). Bugün neden ucuz: henüz
müşteri verisi yok — M-01'in *"tüm veri taşınır"* bedeli bugün kod + test +
belge. M-01 satırına uyarı, özet tablosuna M-16 satırı. Depo, testler ve
DENETIM bilerek M-01'i kanıtlamaya devam ediyor; tanım gelmeden sökülmez.

## 2 · Nerede kaldık

Depo temiz: `bc51d6a` push edildi (`main` = `origin/main`); 610 + 41 test,
DENETIM 0 HATA, tam mutasyon **327 hepsi öldü** (damga 8 Ekim 05:39). K-61
kapalı (varsayılan 3 deneme). Sıra 3 (dört yumuşak kural) 8 Ekim'de başladı:
`VARDIYA_ROTASYON_YONU` için literatür okuması ve tanım taslağı hazır
(`02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md`, keşif
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-08-rotasyon-yonu/`).
Mustafa 1 ve 2'yi kabul etti; **bekleyen iki karar onda:** başlangıç farkı
dairesel okunsun mu (sabah→gece atlaması geri sayılsın — literatür öyle),
ceza birimi saat mı adet mi (öneri saat). 9 Ekim 00:55'te istediği *"okunur
çizelge"* (kişi × gün tablosu) yarım kaldı — görüşme geçti, hâlâ gerekli mi
soruldu.

## 3 · Sıradaki adım

(1) İki rotasyon kararı → şartname (K-65) + motor terimi + bağımsız
doğrulayıcı + testler + mutasyonlar + bağımsız inceleme + 500 kişide
önce/sonra ölçüm; (2) `TERCIH_KARSILAMA` tanım sorusu (hazır); (3)
`PLAN_KARARLILIGI`, (4) `EKIP_SUREKLILIGI` (son ikisi ancak veri seti v2'de
ölçülür); sonra veri seti v2 (K-62), merdiven, K-64; bulgu 26 (karar
Mustafa'da), bulgu 27 (sırada). Mimari (M-16) Yılmaz'ın yorumları gelince.

## 4 · İki karar ve K-66: çizelge her koşuda (18:30–19:30)

**18:30 — Mustafa:** *"1 — evet, 2 — önerin"* → dairesel okuma + ceza =
ağırlık × geri saat (**K-65**). **18:31–18:35:** *"Bundan sonra testlerimizin
çıktıları çizelge de üretmeli … Sadece Yılmaz'ın bakması için değil,
sonrasında UI tarafında bunu aktarabilmek için de çizelge lazım … üründe
kullanılacak çizelge çıktısı üret … Tüm koşumlarda bu çizelge de hazır
olsun artık."* (**K-66**). 18:32: evden çıkmadan koşturacak bir şey istedi;
18:37 *"seni bekliyorum"*.

Önce K-66 (küçük, koşuyu hemen başlatabilsin diye): `cizelge.py` yazıldı
(`plan_kaydet`: `<ad>.json` = `{"kayit", "girdi_ozeti", "cikti", "dogrulama"}`
— `cikti` motorun /solve cevabı aynen + `bagimsiz_denetim` orkestra ile aynı
özet; `dogrulama` doğrulayıcı raporu aynen; `<ad>.html` kişi × gün tablosu,
kapsama ızgarası, doğrulayıcı özeti, künye), `kalite-olc.py` kancası
(`kosu(..., tekrar)`, `planlar/<ölçüm>/<yapılandırma>-<tekrar>`, `--plansiz`,
`--plan-klasoru`). 0.05 ölçekte duman, HTML ekran görüntüsüyle bakıldı,
makineye yazıldı (md5), 18:40 blok: `py kalite-olc.py --saniye 900 --tekrar
3 --yapilandirma varsayilan --etiket rotasyon-once-900` (11 Ekim öncesi
motor = "önce" tabanı + ilk üç gerçek çizelge). Sonra 9 test
(`test_cizelge.py`; ürün biçimi parite testi: `cikti` alanları aynen,
`bagimsiz_denetim` ≡ `orkestra._denetim_ozeti`), eski ölçüm testleri depoya
plan bırakmasın diye `KO.PLANSIZ = True`; 08 testleri 50.

## 5 · K-65 koda indi; bağımsız inceleme 4 (19:30–22:00)

**Kod.** `09-motor/cozucu/model.py`: `rotasyon_geri_saat` (dairesel, (−12, 12]; `yon`),
`rotasyon_yonu`, `Model._rotasyon` — kişi × gün çifti başına `ro_<kişi>_<gün>`
tam sayısı (0..12), yalnız geri şablon çiftleri için `g ≥ saat × (x_s + x_t −
1)` (saat tam sayıya yuvarlı, 0,5 yukarı), çarpım değişkeni yok; K-54: iki
donmuş günün çifti yazılmaz; Pazar→Pazartesi geçmiş gün −1 ile; amaca
`_amac` içinden. `coz.py`: `_CEZA_ONEKI["ro"]`, `_rotasyon_metrigi` →
`metrikler.rotasyon_geri_gecis / _saat` (plandan, kesin saat; kural pasifse
None). `09-motor/dogrulayici/kurallar.py`: `VARDIYA_ROTASYON_YONU` gövdesi (aynı tanım
ayrı yazılı; satırın günü çiftin ikinci günü — K-54 işareti). Testler 18 →
inceleme sonrası **26**; mutasyon `rotasyon` 21 → **35** (toplam 362), hepsi
öldü; takım 636 (bulut). Ölçüm aracı: `rotasyon_0` (ağırlık 0, kural susar,
metrik sayar), rotasyon satırı; `plandan_say.py` (kaydedilen planlardan
doğrulayıcıyla sayım — "önce" için). Şartname §6.3 satır + tanım alt bölümü
(8 madde; madde 8 bilinen sınırlar), §11.3 rotasyon metrikleri, §16.2
çizelge notu, değişiklik 65–66; K-65, K-66 kayıtları; `uret_veri_seti.py`
yorumu (üç gövdesiz kural kaldı).

**İnceleme 4 (ayrı ajan, ~35 dk; `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-11-inceleme4-rotasyon/`).**
*Koda inmeye hazır, bloklayıcı yok.* 1.100 rastgele + 40 hedefli sahne:
metrik ≡ doğrulayıcı ≡ üçüncü sayım (0 fark); amaç terimi ≡ yuvarlanmış satır
toplamı (4 fark — hepsi şablona oturmayan donmuş satır, B1). İşlenen: **B3**
metrik pasif çalışanın aktarılan satırının geçmişini okumuyordu →
`kuruldu.girdi["calisanlar"]` (planda satırı olan); **B5** 19 ek mutantın 13'ü
testlerden kaçıyordu → 8 test (tam ,5 yukarı — `round()` bankacı
yuvarlaması 2,5→2 verirdi; 2,25→2; 0,25 satırı; 1 saatlik çift; 12 saatlik
alan; aynı günde / gün −1'de iki kayıt → ilk başlangıç; gün 0 donmuş +
geçmiş; pasif kişi; `aktif: false`) + 14 mutant (ilk koşuda 2 yaşadı + 1
çapa eskimiş → testler güçlendirildi, çapa düzeltildi; 35'in 35'i öldü; *B1 dersi bir kez daha:* takımı grup koşusuyla aynı anda koşturdum, bir test mutant kodu yükleyip kızardı — temiz ve sakin ağaçta yeniden: 636'nın 636'sı);
**B6** "~54 bin kısıt" ölçülmemişti → 6 şablonlu kişide 14 geri çift,
0.1'de +3.570 (+%4,7), 0.2'de +7.476 (+%4,9) kısıt, değişken +%0,45, kurma
süresi gürültü içinde; **B9** ağırlık 0 iken amaç kırılımı `deger: null`.
Not düzeyi: B2 (donmuş günde iki satır → en büyük geri; K-54'ün kusurlu
saydığı geçmiş), B7 (tam ±12: `yon=geri`'de 12 saat ceza — asimetri),
B8 ("çalışma günü = başlangıç günü": gece → boş → akşam çifti görülmez;
`bas ≥ 24` şablon uyarısı) → şartname madde 8; B8 karar Mustafa'da.

## 6 · "Önce" ölçümü (bulgu 28) ve Mustafa'ya blok

**19:25 — Mustafa koşu çıktısını attı** (*"hâlâ çıkamadım … dönüşte
bakarım … ben çıktım"*): 500 kişi, 900 sn × 3, `varsayilan` (11 Ekim öncesi
kod): kurma 52–61 sn, 778–783 sn, mola adımı optimum; amaç **27.040 / 26.646 /
27.119**; fazla mesai 0; hedef kapsama %84,34 / 85,06 / 84,34 (eksik 368 /
364 / 375 kişi-saat); 0 sert, yayınlanabilir; üç çizelge
`08-motor-testleri/gercekci-veri-seti/planlar/kalite-olcumu-95-rotasyon-once-900/` (varsayilan-1..3 json + html)
(1,6 MB + 430 KB her biri). Planlar buluta çekilip `plandan_say.py` ile
sayıldı: **279 / 301 / 278 geri geçiş** (art arda 1.619 / 1.637 / 1.627
çiftin %17,2 / 18,4 / 17,1'i), **1.364 / 1.489 / 1.346 saat**, ort. 4,9;
büyüklükler: 2,75 (63–72), 3,25 (43–48), 4 (49–54), 9 (47–61: 09:00–13:00 →
ertesi 00:00 gecesi), 11 (12–17), sabah→gece atlaması 30–35. Ağırlık 3 ile
≈ 4.000–4.500 puan = amacın ~%15'i → **ince ayar değil** (küçük ölçekteki
%1 yanıltıcıydı). T-60 bulgu 28; karar kuralı K-65'e koşudan önce yazıldı.

**Blok (Mustafa dönünce):** testler (636 + 50) → DENETIM → commit/push →
tam mutasyon (362) → `py kalite-olc.py --saniye 900 --tekrar 3 --yapilandirma
varsayilan,rotasyon_0 --etiket rotasyon-sonra-900` (~1 sa 45 dk, çizelgeli)
→ `py plandan_say.py` iki klasöre. Sonra `TERCIH_KARSILAMA` sorusu.
