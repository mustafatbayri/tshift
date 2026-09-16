# Kural sınıflandırması — hangi kural yasal, hangi ihlal kabul edilebilir

**Ne bu:** Şartname v1.4'ün en büyük maddesi. Yazılmadan önce senin onayın gerekiyor.
**Tarih:** 16 Eylül 2026 · **Durum:** ⏳ ONAY BEKLİYOR
**Kaynak:** v1.3 §6 kural kataloğu · kararlar K-10, K-16, K-17, K-18…K-22

---

## 1. Neyi onaylıyorsun

Sistem, bir planı yayınlamadan önce şu soruyu soruyor: *"Bu ihlali yönetici
kabul edip geçebilir mi, yoksa düzeltmek zorunda mı?"*

Bu soruyu cevaplayabilmek için **her kuralın hangi gruba girdiği** yazılı olmalı.
Şu an hiçbir yerde yazmıyor — kararların (K-10, K-16) bu yüzden uygulanamıyor.

Aşağıdaki tablo o eksiği kapatıyor. Onayladığında v1.4 §6'ya girecek.

**Bu tablo `[çıkarım]`** — hukukçu değilim, İş Kanunu'ndan okuyarak türettim.
Sahaya çıkmadan önce bir iş hukuku uzmanı bakmalı (açık madde A-16).

---

## 2. Bugün aldığın altı karar

| # | Karar | Sonucu |
|---|---|---|
| **K-18** | Yasal kuralın değeri **kanunun değeridir**, firma değiştiremez | `GUNLUK_AZAMI` **9 → 11** oldu |
| **K-19** | "Firma günlük azami" diye ayrı bir kural **olmayacak** | Firma daha sıkı günlük tavan koyamaz |
| **K-20** | Yasal kural ihlali **hiçbir koşulda** kabul edilemez (K-16 aynen geçerli) | Yayın kapısı mutlak |
| **K-21** | Sağlık raporu için **ayrı kural**: `SAGLIK_KISITI` | Katalog bir kural büyüyor |
| **K-22** | `TERCIH_KARSILAMA` anlamı değişti, **adı aynı kalıyor** | Part-time esnekliğini ölçecek |
| **K-23** | Kabul yetkisi = **yayın yetkisi** | Yetki matrisine yeni satır yok |

---

## 3. Sınıflandırma yaparken çıkan iki sorun

Bunları tabloyu doldurmaya çalışırken buldum. İkisi de senin kararını
gerektiriyor ama ikisi de **teknik**, ürün kararı değil — o yüzden çözümünü
ben öneriyorum, sen sadece "olur" dersen yeter.

### Sorun 1 — İki grup yetmiyor, üçüncü bir grup var

Kararın şu: *yasal ihlal kabul edilemez, firma kuralı ihlali kabul edilebilir.*
Tablo iki gruplu olunca şu absürtlük çıkıyor:

> `AKTIF_CALISAN` yasal bir kural değil — hiçbir kanun *"işten ayrılmış kişiye
> vardiya yazma"* demiyor, çünkü buna gerek yok. Ama "yasal değil" dersek,
> sistem yöneticiye **"ayrılmış çalışanı planda tutmayı kabul ediyorum"**
> seçeneğini sunar. Bu saçma.

Aynı durum `CAKISMA_YOK` (aynı kişi iki yerde), `DONMUS_GUN` (geçmişi
değiştirme), `KILIT_UYUMU` (kullanıcının kararını geri alma) için de geçerli.
Bunlar kural değil, **imkânsızlık**. K-16'da `CAKISMA_YOK` için *"yasal
kuraldır"* demiştik — pratikte doğru sonucu veriyor ama etiket yanlış:
çakışmayı yasaklayan bir kanun maddesi yok, mantık yasaklıyor.

**Önerim — bayrağı ikiye ayır:**

| Alan | Ne söyler | Kime lazım |
|---|---|---|
| `yasal` | Bu kural kanundan mı geliyor, hangi maddeden | Kullanıcıya, denetime, hukukçuya |
| `kabul_edilebilir` | Yönetici bu ihlali kabul edip yayınlayabilir mi | **Yayın kapısına** |

Kural: `yasal = true` ise `kabul_edilebilir` **her zaman** `false`. İmkânsızlık
kuralları da `false`, ama `yasal = false` — dürüst etiket. Firma kuralları
`true`.

Böylece hem kararın bozulmuyor, hem katalog yalan söylemiyor. Bir de faydası
var: hukukçu geldiğinde `yasal` sütununu düzeltmesi yayın kapısını bozmuyor.

### Sorun 2 — Bazı kurallarda bayrak kuralın değil, **kural örneğinin** özelliği

`YETKINLIK_KAPSAMASI` tek bir kural ama her firmada farklı satırlar taşıyor:

| Firmanın yazdığı satır | Bu yasal mı |
|---|---|
| "Her vardiyada en az 1 ilk yardım sertifikalı kişi" | Muhtemelen **evet** (İlk Yardım Yönetmeliği) |
| "Kahvaltı saatinde en az 1 barista" | Kesinlikle **hayır** — ticari tercih |

Aynı kural tipi, iki farklı cevap. Bayrağı yalnız kural **tipine** koyarsak ya
baristayı kabul edilemez yaparız ya ilk yardımcıyı kabul edilebilir.

**Önerim:** `ROL_KAPSAMASI` ve `YETKINLIK_KAPSAMASI` için bayrak, firmanın
yazdığı **her satırda ayrı ayrı** tutulur. Diğer 32 kuralda tip seviyesinde
kalır. Kural yönetimi ekranında bu satırların yanında bir onay kutusu olur:
*"Bu gereklilik yasal zorunluluktan geliyor"*.

---

## 4. Kural sayısı doğru değil

Şartname §6 *"27 kural"* diyor. **Saydım: 33.** Yeni `SAGLIK_KISITI` ile **34**.

Sayı üç ayrı yerde geçiyor (§6 başlığı, §14.1 Faz 1 kapsamı, kural yönetimi
ekranı) ve üçü de 27 diyor. v1.4'te düzeltilecek — **T-10** olarak kaydettim.

---

## 5. Tablo — 34 kural

**Okuma:** `kabul` sütunu tek soruyu cevaplar — *"yönetici bu ihlali kabul edip
planı yayınlayabilir mi?"*

### Uygunluk — kim çalışabilir

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `AKTIF_CALISAN` | Ayrılmış kişiye atama yok | ❌ | 🔒 **Hayır** | İmkânsızlık — kişi orada değil |
| `SOZLESME_GECERLI` | Sözleşme bittikten sonra atama yok | ❌ | 🔒 **Hayır** | İmkânsızlık — çalıştırma hakkı yok |
| `ONAYLI_IZIN` | Onaylı izin gününe atama yok | ✅ | 🔒 Hayır | İş K. md. 53 vd. — izinli işçi çalıştırılamaz |
| `UYGUNLUK_TAKVIMI` | "Uygun değilim" dediği saate atama yok | ❌ | ✅ Evet | Firma–çalışan anlaşması |
| `CALISMA_SAATLERI` | Operasyon kapalıyken atama yok | ❌ | ✅ Evet | Firma operasyon kararı |
| `SAGLIK_KISITI` 🆕 | Raporlu kişinin günlük/haftalık sınırı | ✅ | 🔒 Hayır | İSG K. 6331 — rapor bağlayıcı. Yalnız çalışan kademesi, **belge referansı zorunlu** |

### Süre ve dinlenme

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `GUNLUK_AZAMI` | Günde en çok **11 saat** net | ✅ | 🔒 Hayır | İş K. md. 63. **K-18: değer 11, firma değiştiremez** |
| `HAFTALIK_AZAMI` | Haftada en çok 45 saat | ✅ | 🔒 Hayır | İş K. md. 63 |
| `PART_TIME_LIMIT` | Kısmi süreli sözleşme saati aşılamaz | ⚠️ belirsiz | 🔒 Hayır | Sözleşme hukuku. Aşım fazla çalışma sayılır mı — **hukukçuya** |
| `VARDIYA_ARASI_DINLENME` | İki vardiya arası en az 11 saat | ✅ | 🔒 Hayır | Postalar Halinde Çalışma Yönetmeliği md. 7 |
| `HAFTA_TATILI` | 7 günde kesintisiz 24 saat | ✅ | 🔒 Hayır | İş K. md. 46 |
| `CAKISMA_YOK` | Aynı kişiye çakışan iki vardiya yok | ❌ | 🔒 **Hayır** | İmkânsızlık. **A4'teki Cem vakası budur** |
| `MOLA_HAKKI` | Süreye göre zorunlu ara dinlenme | ✅ | 🔒 Hayır | İş K. md. 68 (K-4: brüt süreye uygulanır) |
| `ASGARI_VARDIYA_SURESI` | En kısa vardiya 4 saat | ❌ | ✅ Evet | Firma politikası |
| `ARDISIK_CALISMA_GUNU` | En çok 6 gün üst üste | ⚠️ belirsiz | 🔒 Hayır | Hafta tatiliyle örtüşüyor; ayrı mı türev mi — **hukukçuya** |
| `YILLIK_FAZLA_MESAI_TAVANI` | Yılda 270 saat | ✅ | 🔒 Hayır | İş K. md. 41 |

### Gece

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `GECE_VARDIYASI_AZAMI` | Gecede en çok 7,5 saat | ✅ | 🔒 Hayır | İş K. md. 69 |
| `ARDISIK_GECE_LIMIT` | En çok 3 gece üst üste | ❌ | ✅ Evet | Firma / sağlık politikası, kanunda yok |
| `VARDIYA_ROTASYON_YONU` | Vardiya ileri kaysın | ❌ | — | Yumuşak kural, kapı konusu değil |
| `GECE_YARISI_ASAN` | Bitiş < başlangıç ise ertesi güne taşar | ❌ | — | Hesaplama kuralı, ihlal üretmez |
| `DST_GECISI` | Yaz saati geçişi | ❌ | — | **Pasif** (K-12) |

### Kapsama

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `ASGARI_KAPSAMA` | Her hücrede zorunlu asgari kişi | ❌ | ✅ Evet | Firma talebi. **A3'teki Zeynep vakası budur** |
| `HEDEF_KAPSAMA` | İdeal kişi sayısı | ❌ | — | Yumuşak |
| `MOLA_KAPSAMASI` | Mola sırasında asgari altına düşülmesin | ❌ | — | **K-14: SERT → YUMUŞAK** |
| `ROL_KAPSAMASI` | Belirli rol sahada olsun | ⚠️ **satır bazlı** | ⚠️ satır bazlı | Bkz. Sorun 2 |
| `YETKINLIK_KAPSAMASI` | Belirli yetkinlik sahada olsun | ⚠️ **satır bazlı** | ⚠️ satır bazlı | Bkz. Sorun 2 — ilk yardımcı vs. barista |

### Adalet ve denge

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `SAAT_DENGESI` | Saatler sözleşmeye yakın olsun | ❌ | — | Yumuşak |
| `ADALET_DENGESI` | Yük dengeli dağılsın | ❌ | — | Yumuşak |
| `ARDISIK_HAFTA_SONU_LIMIT` | En çok 2 hafta sonu üst üste | ❌ | ✅ Evet | Firma politikası |
| `EKIP_SUREKLILIGI` | Aynı kişiler aynı ekiple | ❌ | — | Yumuşak |
| `PLAN_KARARLILIGI` | Mevcut atamalar korunsun | ❌ | — | Yumuşak |

### Düzenleme ve fazla mesai

| Kural | Ne der | Yasal mı | Kabul | Dayanak / gerekçe |
|---|---|---|---|---|
| `KILIT_UYUMU` | Motor kullanıcının kararını bozamaz | ❌ | 🔒 **Hayır** | İmkânsızlık — ürünün temel sözü |
| `DONMUS_GUN` | Geçmiş yeniden planlanamaz | ❌ | 🔒 **Hayır** | İmkânsızlık — olan oldu |
| `FAZLA_MESAI_TAVANI` | Haftalık fazla mesai tavanı | ❌ | ✅ Evet | Firma profili (0/10/15). Yıllık 270 ayrı ve yasal |
| `TERCIH_KARSILAMA` | Part-time sözleşme esnekliği kullanımı | ❌ | — | Yumuşak. **K-22: anlamı değişti, adı kaldı** |

### Sayım

| Grup | Adet |
|---|---|
| ✅ Yasal (kanundan) | **10** |
| ⚠️ Belirsiz — hukukçu bakacak | **4** (2'si satır bazlı) |
| 🔒 İmkânsızlık (yasal değil ama kabul de edilemez) | **5** |
| ✅ Firma kuralı — kabul edilebilir | **6** |
| Yumuşak — kapı konusu değil | **9** |
| **TOPLAM** | **34** |

> **Güvenli varsayılan (K-17 devam ediyor):** ⚠️ belirsiz olanlar yasal gibi
> davranır — kabul edilemez. Hata yönü *"kabul edemedim"* şikâyeti olur,
> *"sessizce geçti"* sızıntısı değil.

---

## 6. `GUNLUK_AZAMI` 9 → 11: ne değişiyor

| Nerede | Eski | Yeni |
|---|---|---|
| Kural değeri | 9 (firma/departman/sözleşme/çalışan değiştirebilir) | **11, kimse değiştiremez** |
| Şartname §5.2 örneği | GUNLUK_AZAMI üzerinden 4 kademe anlatılıyordu | **Başka kurala taşınacak** — GUNLUK_AZAMI artık örnek olamaz |
| §5.2'deki "Ayşe 4 saat" durumu | `rule_overrides` | **`SAGLIK_KISITI`** (K-21) |
| §5.2'deki *"9 saat — İş Kanunu üst sınırı"* | **Yanlış cümle** | Kanunun tavanı 11; düzeltilecek |
| Fikstürler | `azami_saat: 9`, `yasal: "belirsiz"` | `azami_saat: 11`, `yasal: true` |

**Fikstürlere etkisi — kontrol ettim:** Hiçbir fikstürde 9 saatten uzun net
çalışma yok, ve hiçbir fikstür `GUNLUK_AZAMI` ihlali beklemiyor (A04 açıkça
*"GUNLUK_AZAMI_ihlali: false"* diyor). **Sınırı 9'dan 11'e çıkarmak hiçbir
beklenen sonucu değiştirmiyor.** Sahnede yalnız iki değer güncellenecek.

**Pratikte ne demek:** Firma artık *"bizde kimse 9 saatten fazla çalışmaz"*
diyemiyor. 10 saatlik vardiya kurulabiliyor ve sistem itiraz etmiyor. Bunu
istiyorsan tablo hazır; istemiyorsan K-19'u tekrar konuşmamız gerekir.

---

## 7. Onay

Üç şeye ayrı ayrı bak:

| # | Ne | Onayın |
|---|---|---|
| 1 | **Sorun 1 çözümü** — `yasal` ve `kabul_edilebilir` iki ayrı alan olsun | ☐ |
| 2 | **Sorun 2 çözümü** — rol/yetkinlik gerekliliklerinde bayrak satır bazlı | ☐ |
| 3 | **34 kuralın tablosu** — özellikle 🔒 imkânsızlık grubu ve ⚠️ belirsizler | ☐ |

Onayladıktan sonra v1.4 yazılır. Onaylamazsan hangi satırın yanlış olduğunu
söyle, tablo düzeltilir — v1.4 bu tablo kesinleşmeden yazılmaz.
