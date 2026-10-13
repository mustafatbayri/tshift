# 12 Ekim 2026 — Rotasyon gün tanımı D koda indi (K-65 madde 1)

Pencere: 16:23'te açıldı (⚠ 12 Ekim 16:00 paragrafından; *"ilk iş D kodu"*).
Kod bulutta yazıldı ve test edildi (`2f16729` klonu), dosyalar Mustafa'nın
makinesine kopyalandı; commit Mustafa'da.

## İçindekiler

1. Açılış beyanı ve kabul ölçütleri
2. Ne yazıldı
3. Ölçüm (ölçüt 8)
4. Mustafa'nın bloğu
5. Açık kalanlar

## 1 · Açılış beyanı ve kabul ölçütleri (16:46–17:06)

Okunan: BURADAN ⚠ 16:00, §5b/§6/§7; K-65 tamamı; oturum
`2026-10-11-konteyner-karari-ve-sira-3-durumu.md` §7–8; şartname v1.4 §6.3;
kod (`model.py _rotasyon`, `kurallar.py vardiya_rotasyon_yonu`,
`coz.py _rotasyon_metrigi`, `mutasyon_kostur.py` rotasyon grubu). K-67,
K-62 seviye 1, bulgu 29 bu adımda okunmadı (sıra 2'nin işi).

Ölçütler (Mustafa 17:06): 1 ok · 2 ok · 3 ok · 4 *"Bir günde de
sıfırlanıyorsa 2 günde de sıfırlanır herhalde"* → karar değil koruma testi
(d → d+3'e kayan bir kod hatasını yakalar), test olarak kaldı · 5 ok · 6
*"tam anlamadım"* → düz anlatıldı: önceki haftanın son vardiyası geçmiş
kayıtta; D aynen uygulanır · 7 *"tam anlamadım, sen yorumla ve karar ver"* →
karar: motor, doğrulayıcı, metrik aynı çifti sayar, testle zorlanır · 8
*"bulutta ok, lokalde gerekirse koşu yapalım. ölçmeden ilerlemiyoruz."*

Varsayımlar (beyanda yazıldı, itiraz gelmedi): `bas < 24` (şartname madde
8d); aynı günde birden çok kayıt → ilk başlangıç, son gün en geç bitişten;
K-54: d ve d+2 ikisi de donmuşsa amaç terimi yok, doğrulayıcı satırının günü
ikinci vardiyanın günü.

## 2 · Ne yazıldı (17:06–17:30)

- `09-motor/cozucu/model.py`: `gece_yarisini_asar` (yeni yardımcı),
  `_rotasyon` D döngüsü (gece yarısını aşan şablon × d+2 geri şablon;
  `ro_<kişi>_<d+1>` yeniden, `− _calisiyor(d+1)`), geçmiş için gün −2
  gecesi → Pazartesi ve gün −1 gecesi → (Pazartesi boş) → Salı;
  `_ro_degiskeni` (varsa al, yoksa kur ve amaca ekle); docstring madde 1 ve 4.
- **Yan bulgu:** `if not geri: continue` kaldırıldı — tek şablonlu kişinin
  geçmiş→Pazartesi terimi atlanıyordu (doğrulayıcı/metrik sayıyordu).
  Ürün sahnesinde (5–6 şablonlu kişiler) etkisizdi; tek şablonlu kiracıda
  motor kuralı görmeyecekti. Test + mutant ile bağlandı. Otopsi açılmadı:
  ürünü etkileyen bir hata yaşanmadı, kalıcı kontrol (test + mutant) kondu.
- `09-motor/dogrulayici/kurallar.py`: `_rotasyon_son_gun` (ayrı yazım, #7.6),
  `vardiya_rotasyon_yonu` birleşik okuma (plan + geçmiş, `d1 ≤ son(d0) + 1`,
  satır yalnız `d1 ≥ 0`).
- `09-motor/cozucu/coz.py`: `_rotasyon_metrigi` aynı tanım.
- `09-motor/testler/test_rotasyon_yonu.py`: bölüm 5, 13 test (26 → 39).
  Not: `test_D_ara_gunde_calisilirsa_D_kisiti_SUSAR` ilk yazımda çözümsüz
  sahne kurmuştu (gece → ertesi akşam 11 saat dinlenmeyi bozar); şablonlar
  `gunler` alanıyla günlere bağlanarak tek plan zorlandı.
- `09-motor/mutasyon_kostur.py`: 15 eski rotasyon mutantı yeni metne
  bağlandı (aynı anlam; biri D mutantına çevrildi), 12 yeni D mutantı →
  `rotasyon` 47, toplam 374. Bulutta `py mutasyon_kostur.py rotasyon`:
  **47 mutasyon · yaşayan 0 · atlanan 0** (1 dk 53 sn).
- `02-spec/v1.4-master-spec.md`: §6.3 madde 1 (D), madde 8 (d kapandı, e
  model biçimi, f yan bulgu), değişiklik satırı 67, künye tarihi.

Bulutta: 09-motor **649 passed** (2 dk); v5 altın 12 passed + 4 skipped
(servis ayakta); fikstür denetleyici temiz; gerçekçi veri seti **50 passed**
(8 dk 42 sn). DENETIM: 4 HATA yalnız `06-veri/` (git dışı, bulut klonunda
yok) — Mustafa'nın makinesinde teyit edilecek.

## 3 · Ölçüm (17:30–18:00, ölçüt 8)

Bulut, **2 çekirdek** (süreler Mustafa'nın 6 çekirdeğiyle kıyaslanamaz),
0,2 ölçek (100 kişi, %95), 300 sn × 2. Eski kod `git worktree` ile ayrı
kopyada koşuldu (`kalite-olcumu-0.2-95-d-once-bulut`, çıktısı depoya
girmiyor — sayımları `sonuc-0.2-bulut.txt`'te); D kodu
`kalite-olcumu-0.2-95-d-sonra-bulut.json` + planlar (depoya girer). Sayım:
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-12-rotasyon-D/say_D.py`. Tablo K-65 *"D koda indi"*.

- Eski kod planlarında D'nin gördüğü gece→akşam çifti **2 / 3** (18,5 /
  27,75 sa); D koduyla **0 / 0**; ağırlık 0'da +3 / +3.
- Metrik ≡ doğrulayıcı dört planda birebir; amaç terimi ≡ yuvarlı satır
  toplamı (9 = 9, 7 = 7). Eski tanımla yeniden sayım, eski motorun kendi
  metriğiyle birebir (2 = 2, 5 = 5) — sayım aracının kendisi de doğrulandı.
- Fazla mesai 0, 0 sert, yayınlanabilir, fazla mesaisiz ilk arama ilk
  denemede (hepsi).
- Bedel: rotasyon dışı amaç ort. 5.420 → 5.442 (+%0,4; tekrarlar arası
  %1,6) — **bu örneklem ayırt etmez**; tam ölçek K-62 seviye 1 tabanında.
- Kurulum: 0,2'de 161.256 → 161.521 kısıt (+265, +%0,16); 500 kişide
  809.888 → 811.258 (+1.370, +%0,17), değişken 636.495 aynı, kurma 72,6 →
  74,4 sn (tek ölçüm). `kisit_say.py`.

Kolaylaştıran ayar (§6 madde 7): ölçek 0,2 ve 300 sn — Mustafa 15:57'de
onaylanan yol (tam ölçek seviye 1 tabanında). Başka kolaylaştırma yok.

## 4 · Mustafa'nın bloğu

Dosyalar makineye kopyalandı. Blok sohbette verildi; özeti:
korkuluk → `09-motor` testleri (649) → zor veri seti (50) → `DENETIM.py`
(0 hata beklenir) → commit + push → `py mutasyon_kostur.py` (374, yaşayan 0
beklenir) → damga commit'i. CI beklentisi: 09 işi 649, 08 işi 50.

**21:28 — blok koştu (Mustafa'nın makinesi):** 649 passed (1 dk 34 sn), 50
passed (7 dk 7 sn), DENETIM HATA 0 / 17 uyarı, `573ee6e` push
(`2f16729..573ee6e`), tam mutasyon **374 · yaşayan 0 · atlanan 0** (damga
19:57). Bulut kopyası `573ee6e` ile birebir (stash karşılaştırması). Damga
dosyası + bu ek ayrı commit.

## 5 · Açık kalanlar

1. ~~Mustafa'nın bloğu~~ ✅ (21:28).
2. Sıra 2: K-62 seviye 1 aracı + K-67 `HEDEF_ASIMI` sert + teşhis + testler,
   mutasyonlar, şartname §6.4 (BURADAN ⚠ 16:00).
3. Sıra 3: seviye 1 taban ölçümü (Mustafa'nın makinesi, 900 sn × 3) — D'nin
   tam ölçek okuması da orada.

## 6 · Sıra 2 — K-67 + K-62 seviye 1: açılış ve kabul ölçütleri (21:30)

Okunan: K-67 tamamı, K-62 tamamı (seviye 1 satırı, kadro tablosu),
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/` (OKU-BENI §3, `b_gomulu.py`),
`model.py _kapsama`, `teshis.py`, `kurallar.py hedef_asimi`,
`test_hedef_asimi.py`, `uret_veri_seti.py` (TALEP_PROFILI, kadro).
Kabul ölçütleri 1–10 ve iki soru sohbette Mustafa'ya soruldu; cevap
gelmeden kod yok.

**22:03–22:11 — cevaplar.** *"1- ok 2- ok 3- ok 4- neden böyle anlamadım 5- ok
6 20 satışçı fazla bence bunu 10 yapalım. 7- ok 8- ok 9 - bunu tam anlamadım.
10 ok"*; Back Office gece hedefi 3 ✅. 4 ve 9 açıldı (puan dökümü / bekçiler
ve maliyetleri) → 22:09 *"Gerekçeli kabul istemesine gerek yok sadece
yöneticiyi bilgilendirsin ve bu aksiyonun yönetici tarafından alındığını
görelim yeter"* (K-67 eki), 22:11 *"ok önerine katılıyorum"* (500 çözüm
bekçisi haftalık CI). Ayrıca 21:31 sorusu: *"koşu sonuçlarında hâlâ hedef
aşımını yumuşak görüyorum"* → cevap: sert hâli o an kodda değildi (sıra 2);
eski S30 seti sertle çözümsüz (bulgu 29), K-67 madde 4 ile tarihsel.

## 7 · K-67 + merdiven seviye 1 koda indi (22:05–23:15, bulut)

- **Motor:** `_kapsama` SERT → `atanan ≤ hedef` (K-54 süzgecinden geçer);
  `teshis.py` `celisen_talep` (asgari / `SAHADA_ASGARI` / devir > hedef →
  çözücüsüz `cozumsuz`), `_asim_gevsek_plan` (önce yalnız aşım — OPTIMAL ise
  kanıtlı en az; sonra o tavanda normal amaç; ilk taslakta tek ağırlıkla
  "kanıtlı" diyecektim, kanıt olmadığını görüp iki adıma çevirdim),
  `_en_iyi_plan` HEDEF_ASIMI'yi siler yerine yumuşatır (silinince taslak 48
  aşım, yumuşatınca 32 — 5/5 ölçüldü, test tam sayıya sıkılaştırıldı);
  `denetle.py` `BILGI_VEREN_KURALLAR` → `yayin_kapisi.bilgi_ihlaller`.
- **Tuzak bulundu:** fazla mesaisiz ilk arama tohumları 1-2-3 sabit, dışarıdan
  `random_seed` görmüyordu → referans ürünle aynı başlangıçtan üretilecekti
  (K-62 ilke 1). `tohum_kaydirma` ölçüm seçeneği (ürün 0); test + mutant.
- **Merdiven:** `merdiven.py` — taban (S30-95 + 10 çift yetkinlikli satışçı
  `random.Random(TOHUM+62)` ile + BO gece 00–08 asgari 2 / hedef 3),
  referans (tohum 7, `fazla_mesai_sifirda_tut`; şartlar: 0 sert, fazla mesai
  0), seviye 1 (hedef = doğrulayıcının kendi sayımı — HEDEF_KAPSAMA /
  HEDEF_ASIMI satırlarından; asgari = hedef − 1, en az 1; HEDEF_ASIMI SERT),
  `plan_puani` (planı modele eşitlikle sabitleyip motorun ölçüsüyle puan).
  Küçük kopya (0,1; 49 kişi): referans tabanda 156 aşım + 13 eksik → seviye
  1'de 0/0/0; referansın seviye 1 puanı **3.404** (mola 2.170, adalet 1.210,
  rotasyon 24); motor 120 sn'de (ilk sürümde) **2.863**, aşım 0, sert 0,
  fazla mesai 0, ilk plan 1,4 sn.
- **Bulut denemesi 500 (bulgu 30):** ürün yoluyla tohum 7 referansı 16 saat
  fazla mesaiyle döndü; ilk arama ölçüldü — yeni ve eski sette 1-2-3 ve
  7-8-9 hepsi UNKNOWN (2 çekirdek). Referans yolu sert kesime alındı; haftalık
  bekçi fazla mesaiyi zorlamıyor. Sıkı setin 500'de çözülme süresi bulutta
  ÖLÇÜLEMEDİ (500 referansı yok) — ilk ölçüm Mustafa'nın taban koşusu.
- **Testler/mutasyon (bulut):** 09-motor 657; `k67` 14 + `hedef_asimi` 4
  (hepsi öldü; toplam 388); `test_merdiven.py` küçük kopyada 7 geçti, 500
  dosyaları yokken 2 kırmızı (bilerek — referans Mustafa'nın koşusunda
  üretilir), haftalık test atlandı.
- **Şartname:** §6.4 satırı (SERT, kabul ✅ bilgi verir), §4.5 alt başlık,
  §11.3 `asim_hucreleri` + ön kontrol, `bilgi_ihlaller`, değişiklik 68.

**Blok (Mustafa, sohbette verildi):** korkuluk → 09 testleri (657) →
`py merdiven.py referans --olcek 1.0 --saniye 900 --tohum 7` → 08 testleri
(59 + 1 atlanan) → DENETIM → commit/push → `py kalite-olc.py --seviye 1
--saniye 900 --tekrar 3 --yapilandirma varsayilan --etiket taban-900` → tam
mutasyon (388). Karar kuralı K-67 *"Ölçü"* ve kabul ölçütü 10.
