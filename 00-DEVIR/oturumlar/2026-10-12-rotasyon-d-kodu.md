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

## 5 · Açık kalanlar

1. Mustafa'nın bloğu (yukarıda).
2. Sıra 2: K-62 seviye 1 aracı + K-67 `HEDEF_ASIMI` sert + teşhis + testler,
   mutasyonlar, şartname §6.4 (BURADAN ⚠ 16:00).
3. Sıra 3: seviye 1 taban ölçümü (Mustafa'nın makinesi, 900 sn × 3) — D'nin
   tam ölçek okuması da orada.
