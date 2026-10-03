# 2026-10-03 · T-60 blok 4 (mola ölçümü) · tam mutasyon koşusu (O-15)

**Kim.** Mustafa + Claude (2 Ekim 18:56'da açılan pencere devam ediyor; iş
parçası aynı: T-60 kalite)
**Nereden devam.** `00-BURADAN-BASLA.md` 2 Ekim 23:45 paragrafı: CI → blok 4 →
iki karar → T-80.

## İçindekiler

1. [CI, kaynak sorusu, gün deseni sorusu](#1--ci-kaynak-sorusu-gün-deseni-sorusu)
2. [Blok 4 sonucu](#2--blok-4-sonucu)
3. [Tam mutasyon koşusu: 1 yaşadı, 3 atlandı](#3--tam-mutasyon-koşusu-1-yaşadı-3-atlandı)
4. [Değişen dosyalar ve doğrulama durumu](#4--değişen-dosyalar-ve-doğrulama-durumu)
5. [Bekleyen kararlar](#5--bekleyen-kararlar)
6. [16:31 — K-59 ve mola ölçüm seçeneği](#6--1631--k-59-ve-mola-ölçüm-seçeneği)

---

## 1 · CI, kaynak sorusu, gün deseni sorusu

**13:44.** Mustafa: CI yeşil. Depo: `1138a5d` (gece kapanışı) push edilmiş,
çalışma ağacı temiz. **Kaynak sorusu:** Mustafa bulut makinesine kendi
makinesindeki gibi kaynak alınabilir mi diye sordu. Ölçülen: bulut makinesi 2
çekirdek / 3 GB; köprüdeki Linux sanal makinesi de 2 çekirdek / 3 GB (6
çekirdeği yalnız PowerShell görüyor). Dokümanlarda bulut makinesini büyüten
paket yok; kurum sunucusunda koşturma Team/Enterprise'a özel. Önerilen yol:
Claude Code'u Mustafa'nın makinesinde yerel çalıştırmak (ayrı oturum; devir
paketiyle geçiş). Karar verilmedi.

**`gun_sayisi` sorusu** (K-58'in açık maddesi) Mustafa'ya soruldu: *"haftada 5
mi 6 gün"* alanı kalkarsa izin düşümü tek varsayılanla (6) yapılır; 5 günlük
desende bir gün izinli kişiden motor 36 değil 37,5 saat ister. **Cevap
bekliyor.**

Pencere protokolü notu: T-80 (sözleşme tipi) ayrı iş parçası → yeni pencere;
blok 4 ve iki karar bu pencerede. Mustafa'ya söylendi.

## 2 · Blok 4 sonucu

15:22'de geldi. Tablo ve okuma: `06-ACIK-RISKLER.md` T-60 **bulgu 15–16**.
Kısaca: sabit molalı aşama 120 → 240 → 480 sn uzadıkça fazla mesai 60–83 →
45–53 → 34–38 saat, hedef eksiği 575–610 → 512–533 → 360–366 kişi-saat; bedeli
mola sırasında kapsama ihlali üç kat ve hedef aşımı yüksek; serbest mola arayan
ana aşama her yapılandırmada %6–9 ekliyor; ilk plan 53–57 sn (sebebi
ölçülmedi). Altı koşu 0 sert, yayınlanabilir; üç fazla mesai sayısı aynı.

## 3 · Tam mutasyon koşusu: 1 yaşadı, 3 atlandı

Mustafa 214 mutasyonun tamamını koşturdu: **1 yaşadı, 3 atlandı**. Otopsi:
`05-HATA-OTOPSILERI.md` **O-15**. Özet: *"hepsi öldü"* toplamları grup
koşularından toplanmıştı; son tam koşu 1 Ekim 15:35'ti. K-56 (devreden
kapsama) bir mutasyonu yaşatır hale getirdi (gün-0 kaydı hem vardiyayı
yasaklıyor hem talebi kapatıyor → boş plan "çözüldü", test yalnız duruma
bakıyordu) ve üç çapayı bozdu.

**Yapılan (bulut makinesinde doğrulandı):** `test_COZUCU_gun_degeri_NEGATIF_
olmayan_kaydi_yok_sayar` planın dolu olduğunu ve kaydın devreden kapsamaya
sayılmadığını da sınıyor; yeni test `test_gun_degeri_NEGATIF_olmayan_kayit_
DEVREDEN_kapsama_SAYILMAZ` (doğrulayıcı, K-56 okuyucusu); üç çapa yeni metne;
K-56 okuyucusuna ayrı mutasyon (**215**); `gecmis` 17/17, `cok_ekipli` 11/11
öldü; `test_gecmis_veri.py` 35 geçti. Grup koşusu artık *"toplam iddiası için
tam koşu"* notu yazıyor; tam koşu `09-motor/mutasyon-tam-kosu.txt` damgası
bırakıyor. DENETIM kontrolü önerildi, onay bekliyor.

**Ders (O-15'te):** toplam bir ölçümdür, toplama değil; çözücü/doğrulayıcı
değişince commit öncesi tam koşu.

## 4 · Değişen dosyalar ve doğrulama durumu

| Dosya | Ne |
|---|---|
| `09-motor/testler/test_gecmis_veri.py` | güçlendirilen test + 1 yeni test (35) |
| `09-motor/mutasyon_kostur.py` | üç çapa düzeltildi, +1 mutasyon (215), tam koşu damgası, grup koşusu notu |
| `00-DEVIR/06-ACIK-RISKLER.md` | T-60 bulgu 15–16, sıradaki adım |
| `00-DEVIR/05-HATA-OTOPSILERI.md` | O-15 |
| `00-DEVIR/00-BURADAN-BASLA.md` · `DEGISIM-GUNLUGU.md` | durum |

| Ne | Nerede | Sonuç |
|---|---|---|
| `test_gecmis_veri.py` | bulut (Python 3.10) | 35 geçti |
| `mutasyon_kostur.py gecmis` / `cok_ekipli` / `fmtanim` | bulut | 17/17 · 11/11 · 5/5 öldü |
| Tam koşu (215) | — | ⚠ **koşmadı** — Mustafa'nın makinesinde, commit öncesi |
| Motor testlerinin tamamı | — | ⚠ değişen yalnız bir test dosyası; tam koşu CI'da |
| Commit | — | ⚠ yapılmadı (blok sohbette) |

## 5 · Bekleyen kararlar

1. Birinci aşamada iyileştirme ürünün varsayılanı olsun mu; bütçenin ne kadarı
   sabit molalı aşamaya (ölçülen: uzadıkça iyi).
2. Molalar motorun hesabından çıkıp ayrı, isteğe bağlı adım olsun mu (ayrı
   adımın mola kapsamasını geri alma payı ölçülmedi; istenirse ölçüm
   yapılandırması yazılır: atamalar sabit, molalar serbest, 60 sn).
3. `gun_sayisi` (K-58 açık maddesi).
4. `DENETIM.py`'ye tam koşu damgası kontrolü (O-15) — onay.

## 6 · 16:31 — K-59 ve mola ölçüm seçeneği

**Mustafa'nın koşusu:** `test_gecmis_veri.py` 35 geçti, **tam mutasyon
koşusu 215 mutasyon, hepsi öldü**, `mutasyon-tam-kosu.txt` damgası yazıldı, DENETIM 0
hata, commit **`280c4ef`** push. O-15'in doğrulaması tamamlandı.

**Kararlar:** (1) *"olsun"* → **K-59** (`08-URUN-KARARLARI.md`): iyileştirme
varsayılan, süre bütçenin %40'ı — kalibrasyon, mola kararından sonra yeniden.
(2) *"Ölçümlerimizi tamamlayıp karar vermek isterim."*

**Yapılan (bulut):**
- `coz.py`: `ilk_asama_iyilestirme_saniye` varsayılanı `None` (süre orandan;
  `0` = kapalı), oran 0.4; iyileşmiş planın `amac_dagilimi` çıktıya;
  `ana_asama_atamalar_sabit` ölçüm seçeneği (`_atamalari_sabitle`: x
  değişkenleri ipucu değerine sabitlenir, molalar serbest); çıktıda
  `atamalar_sabit`.
- Testler: `test_demir_secenekleri.py` 17 (K-59 varsayılanı, sıfır kapatır,
  atamalar sabit → x değişmez molalar serbest → dönen plan sabitlenen
  atamalar, ipucu yoksa not); `demir` 19 mutasyon hepsi öldü; **toplam 221**.
- `kalite-olc.py`: `varsayilan` K-59'lu, `eski_urun_hali`, `mola_ayri_adim`
  (`sabit_mola_480` ile aynı ilk aşama — 480 sn sabit molalı iyileştirme,
  ana aşamaya ≈107 sn — tek fark atamalar sabit); çıktıda sabit molalı
  planın mola kapsaması ↔ ana aşama sonu. Ölçüm tasarımı: iki yapılandırma
  yan yana, aralarında **tek fark**; 107 sn'lik ana aşamanın plan verdiği
  sabahki 480 koşularından biliniyor (ilk plan 56–57 sn).
- Devir: K-59, T-60 (bulgu 15'e ürün halinin mola değeri 426–474 eklendi —
  *"üç kat"* 240 sn'ye göredir, ürün haline göre 1,3–1,5 kat; sıradaki adım),
  şartname §11.3 ve değişiklik 57.

**Doğrulama (bulut, 16:45–16:55):** `demir` 19/19 öldü. Tüm motor test
dosyaları teker teker koşuldu (bulutun 180 sn komut sınırı yüzünden
parçalı): **40 dosya, 549 test geçti**. Tek kırılan
`test_sure_butcesi.py::test_ipucu_aramasi_KENDI_payiyla_sinirli` idi — iki
CP-SAT araması bekliyordu, K-59 ile üç oldu (ipucu 2,0 sn = %20 ·
iyileştirme 4,0 sn = %40 · ana aşama kalan 9,98 sn); test üç aramaya göre
düzeltildi, bütçe sözü aynen duruyor (*birinci aşamada geçen + ana aşamaya
verilen ≤ azami*). Kalite ölçüm testleri (`test_kalite_olc.py`,
`test_sahte_pdks.py`) 18 geçti. Mutasyon: 221 çapanın hepsi dosyalarda
tam bir kez bulunuyor (atlanan çıkmayacak); `demir` 19/19, `butce` 4/4
(`test_sure_butcesi.py` düzeltmesinden sonra), `ilk_asama` 6/6 öldü — grup
koşuları, toplam iddiası değil (O-15). ⚠ `test_gercekci_olcek.py` **bulutta
koşmadı** (tam ölçek model kurma + 0,1 ölçek çözüm > 180 sn): 0,1 ölçekte
240 sn bütçeyle K-59 artık ilk aşamada 96 sn'ye kadar iyileştirme yapar,
ana aşamaya ≥ 96 sn kalır — plan döner, süre uzayabilir; **CI ve Mustafa'nın
makinesi ölçer.** ⚠ Mustafa'nın makinesinde test, tam mutasyon koşusu,
commit ve ölçüm **bekliyor**.

