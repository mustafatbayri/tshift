# 4 Ekim 2026 — K-60 koda indi: motor üç aşama, mola adımı varsayılan

**Pencere:** 3 Ekim'den devam eden pencere (T-60'ın devamı; §5b "aynı işin
devamı → aynı pencere"). Önceki günlük: `2026-10-03-mola-olcumu-ve-mutasyon.md`
(§6–10: K-59, bulgu 17–18, K-60 kararı).

## İçindekiler

1. [13:32 — açılış ve durum](#1--1332--açılış-ve-durum)
2. [K-60 uygulaması: ne değişti](#2--k-60-uygulaması-ne-değişti)
3. [Doğrulama (bulut)](#3--doğrulama-bulut)
4. [Kararlar, reddedilenler, açık kalanlar](#4--kararlar-reddedilenler-açık-kalanlar)
5. [Mustafa'nın koşuları ve sıradaki adım](#5--mustafanın-koşuları-ve-sıradaki-adım)
6. [5 Ekim — koşular yeşil, kalibrasyon ölçümü, 600/900 sn kararı](#6--5-ekim--koşular-yeşil-kalibrasyon-ölçümü-600900-sn-kararı)
7. [5 Ekim 21:28 — kalibrasyon sonucu (bulgu 19) ve sıradaki ölçüm](#7--5-ekim-2128--kalibrasyon-sonucu-bulgu-19-ve-sıradaki-ölçüm)

## 1 · 13:32 — açılış ve durum

Mustafa: *"koşu yeşil, nerede kalmıştık."* Depo `dee255c` (K-60 kapanış
commit'i), CI yeşil. Gece "yeni pencere" düzeltmeleri (5 doküman, 10 satır)
commit'ten sonra yazılmıştı — bugünkü commit'le gidiyor. İş: K-60'ı koda
indirmek (`00-BURADAN-BASLA.md` 02:55 paragrafı).

## 2 · K-60 uygulaması: ne değişti

`09-motor/cozucu/coz.py`:
- `VARSAYILAN`: `mola_adimi: True` (yeni; eski ölçüm anahtarı
  `ana_asama_atamalar_sabit` kaldırıldı — `False` eski ortak aramayı ölçüm
  için geri getirir), `mola_adimi_hedef_bosluk: 0.0`,
  `ilk_asama_iyilestirme_orani: 0.4 → 0.8` (ölçülen `mola_adimi_tam` hâli;
  %90 kalibrasyonu sırada). Modül docstring'ine üç aşamanın akışı yazıldı.
- `coz()`: iki aşama devreye girdiyse atamalar `_atamalari_sabitle` ile
  ipucudaki değerlere kilitlenir ve bekçiye (`_ErkenDur.ayar`) mola adımının
  eşiği (0) verilir; ana aşama yalnız molaları arar. Devreye girmediyse
  (küçük model, başlangıç planı) atamalar ve molalar birlikte aranır ve
  **not düşülmez** — ilk yazımda not düşülüyordu, `test_devir_kapsama`
  (küçük model, "notlar boş") kırmızı yandı; not kaldırıldı, bu doğru:
  küçük modelin olağan yolu "uygulanmayan" değil.
- `_ErkenDur`: `deger == sinir` → `"optimum"` (eski: yalnız 0 == 0). Bulgu
  18'de üç koşunun ikisi 0 boşlukla *"hedef_bosluk"* yazılmıştı; yanıltıcıydı.
- Çıktı: `cozum_istatistikleri.mola_adimi` (ayar) ve `atamalar_sabit`
  (uygulandı mı).

Testler: `test_demir_secenekleri.py` 17 → **19** — varsayılanlar testi K-60'a
göre (oran 0,8, mola adımı açık, `durma_sebebi == "optimum"`, amaç == alt
sınır); atamalar sabit/molalar serbest testi varsayılanla ve eşik 0
denetimiyle; "ipucu yoksa uygulanmaz ve not DÜŞMEZ"; yeni: `mola_adimi: False`
eski yol (atamalar serbest, genel %2 eşik, not yok), eşik ayardan okunur
(0,5); oran testi "%40" → "oran kadarı" (%80 ve ayardan %25).
`test_sure_butcesi.py`: iyileştirme payı 10 × %80 = 8 sn. `mutasyon_kostur.py`
`demir` 19 → **26** (toplam **228**): oran %40 / oran sabit / mola adımı
varsayılan kapalı / eşik %2 / eşik ayardan okunmasın / eşik uygulanmasın /
`False` da sabitlesin / `_ErkenDur` eşitlikte optimum demesin; iki eski çapa
yeni satırlara taşındı.

`08-motor-testleri/gercekci-veri-seti/kalite-olc.py`: `varsayilan` açıklaması
üç aşama; **eski ortak aramalı yapılandırmalar** (`eski_urun_hali`,
`a_ipuclu_*`, `a_ipucusuz_120`, `sabit_mola_480`, `b_paralel_*`) anlamlarını
korusun diye `mola_adimi: False` aldı; `mola_ayri_adim` (bulgu 17 kaydı:
eşik %2) ve `mola_adimi_tam` (bulgu 18 kaydı; 600 sn'de = `varsayilan`) yeni
anahtarlarla; yeni `k59_hali` (%40 + ortak arama, 3 Ekim ürün hali) ve
`oran_90` (kalibrasyon). Çıktıda `mola_adimi` alanı.

Şartname: değişiklik 58 "koda indi", §11.3 `ilk_asama_sn` (%80) ve
`ana_asama_butce_sn` (mola adımı) satırları.

## 3 · Doğrulama (bulut)

- `demir` 26/26 öldü; `butce` 4/4; `ilk_asama` 6/6; 228 çapanın hepsi tam bir
  kez bulunuyor. Grup koşuları — toplam iddiası değil (O-15).
- 40 motor test dosyası, **551 test geçti** (parçalı: 180 sn sınırı). Tek
  kırılan `test_devir_kapsama` idi (not meselesi, §2); düzeltildi, yeniden
  yeşil.
- Kalite ölçüm testleri 18 geçti.
- 0,1 ölçek duman (`--saniye 90 --yapilandirma varsayilan`): iyileştirme
  72 sn (%80), **mola adımı 1,3 sn'de optimum** (`durma_sebebi: optimum`),
  mola açığı 199 → 28 (hücre başına 0,5 → 0,1 kişi), 0 sert, yayınlanabilir,
  toplam 74 sn / 90 (16 sn geri döndü).
- `test_gercekci_olcek.py` bulutta koşmadı (180 sn sınırı); CI ve Mustafa'nın
  makinesi. K-60 ile 0,1 ölçekli fikstürün süresi değişebilir (iyileştirme
  payı %80 = 192 sn; mola adımı saniyeler) — ölçülecek.
- Beş kod dosyası depoya kopyalandı, md5 bire bir (O-13).

## 4 · Kararlar, reddedilenler, açık kalanlar

- **Küçük modelde "mola adımı uygulanmadı" notu:** yazıldı, test kırdı,
  kaldırıldı — gerekçe §2. `atamalar_sabit: False` yeter.
- **Yedek plan (mola adımı plan bulamazsa birinci aşamanın planı dönsün):**
  yazılmadı. Bugün de "elde plan varken süre yetmedi" dönebilir (T-60'ta
  bilinen açık); K-60 bunu kötüleştirmiyor, tersine mola adımında ilk plan
  23 sn'de geliyor (ortak aramada 50–57). Ürüne görünür bir davranış
  değişikliği olduğu için **Mustafa'nın kararına** sunuluyor (§5).
- **Oran %80:** ölçülen hâl; %90 kalibrasyon ölçümü sırada (karar kuralı
  T-60 "Sıradaki adım").
- **(C) molaların isteğe bağlı ürün adımı:** K-60'ın dışında, ertelendi.

## 5 · Mustafa'nın koşuları ve sıradaki adım

**14:04 — Mustafa:** *"Bugün çalışmaktan vazgeçtim. Sadece git push ver
lütfen, dünü update edelim. Yarın devam edeceğiz."* → Kod + dokümanlar
**Mustafa'nın makinesinde test koşulmadan** commit'lendi; CI testleri koşar
(09-motor 551 + gerçekçi set), tam mutasyon koşusu CI'da yok. ⚠ Damga
`mutasyon-tam-kosu.txt` hâlâ 221'de (3 Ekim 18:54) — 228 için tam koşu YARIN
ilk iş (O-15). Yarının sırası: `py -m pytest testler -q` (iki dizin) →
`py mutasyon_kostur.py` → damga commit'i → kalibrasyon ölçümü
`py kalite-olc.py --saniye 600 --tekrar 3 --yapilandirma varsayilan,oran_90
--etiket kalibrasyon-600` (≈70 dk) → karar kuralı → üç profil.

## 6 · 5 Ekim — koşular yeşil, kalibrasyon ölçümü, 600/900 sn kararı

**18:49 — Mustafa:** *"devam ediyoruz, nerede kaldık."* Depo `97791b5`, temiz;
damga 221'de. Blok 1 verildi (testler + tam mutasyon + DENETIM), Blok 2
(kalibrasyon) "yalnız Blok 1 yeşilse".

**19:28 — Blok 1 sonucu (Mustafa'nın makinesi):** `09-motor` **551 geçti**
(74 sn); **tam mutasyon koşusu 228 · yaşayan 0 · atlanan 0** (`demir` 26'sının
hepsi dahil; damga dosyası değişti, commit bekliyor); gerçekçi set **31 geçti,
434 sn** (dün 361, önceki gün ~170: K-60 ile 0,1 ölçekli fikstür iyileştirmeye
bütçenin %80'ini veriyor — 192 sn; bütçe 240 sn tavanlı, CI süresi uzar,
sorun değil); DENETIM 0 hata. → Blok 2 başladı (19:30, ≈70 dk).

**19:31 — Mustafa:** *"neden 900 değil 600 sn? Müşteride 15 dk sınırımız
olacaktı."* Dokümanlardan cevap: 600 sn 2 Ekim'de ölçüm ekonomisi için
seçildi ve kıyaslar için sabit tutuldu; ürün seçenekleri 10/15/30 dk (K-35),
600 = en kısası; paylaşım orantılı olduğundan 900'de mola adımına ≈170 sn
kalır, 600'deki kalibrasyon dar durum. **Öneri:** ürün hali ölçümleri 900
sn'de, 600 A/B için. **19:34 — Mustafa: "katılıyorum."** T-60'a not yazıldı.

## 7 · 5 Ekim 21:28 — kalibrasyon sonucu (bulgu 19) ve sıradaki ölçüm

Çıktı 21:28'de geldi (`kalite-olcumu-95-kalibrasyon-600.json`, 6 koşu; tam
tablo T-60 bulgu 19). Karar kuralı uygulandı: %90 fazla mesai/eksikte belirgin
iyi değil (aralıklar çakışıyor: 29–45,5 ↔ 28–44,75 saat; 354–402 ↔ 366–397
kişi-saat); mola adımı altı koşuda da optimuma ulaştı ama %90'da bütçe 44–47
sn, optimum 40,5–42,9 sn — pay 1–5 sn. **%80 kaldı, kod değişmedi.** Yan
bulgu: aynı amaçsız başlangıç planı (2.433.123) üç koşuda 160.935 / 126.535 /
144.770'e varıyor — koşudan koşuya fark iyileştirme aramasının kendisinden;
not 1'in ölçüm tasarımı buradan.

`kalite-olc.py`: `oran_90` kayıt notu; **`profil_kapsama`** ve
**`profil_calisan`** (yalnız `profil` alanını değiştirir; sahne DENGELI).
Kalite ölçüm testleri 18 geçti (bulut).

**Sıradaki ölçüm — ürün hali, üç profil, 900 sn, üçer koşu** (≈2,5 saat):
`py kalite-olc.py --saniye 900 --tekrar 3 --yapilandirma varsayilan,profil_kapsama,profil_calisan --etiket profiller-900`.
⚠ CALISAN profilinde zorunlu fazla mesai tavanı 0; %95 setinde fazla mesai
şablon karışımından geliyor (45'i tam tutturamayan desen) → çözümsüz
çıkabilir; çıkarsa ürün bulgusu (profil × veri seti).

**Commit bekleyen:** damga `09-motor/mutasyon-tam-kosu.txt` (228),
`kalite-olcumu-95-kalibrasyon-600.json`, `kalite-olc.py`, `06`, `08`, `00`,
`DEGISIM-GUNLUGU.md`, bu günlük §6–7.

