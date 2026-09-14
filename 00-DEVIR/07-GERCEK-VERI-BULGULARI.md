# GERÇEK VERİ BULGULARI

**Kaynak:** Bir seyahat acentesinin PDKS ve vardiya planlama dosyaları,
Haziran–Eylül 2026 · **İnceleme:** 13 Eylül 2026
**Ham veri konumu:** `06-veri/ham` — **git'e girmez** (`.gitignore`)

> Bu doküman anonimdir: kişi adı, sicil numarası ve firma adı içermez.
> Ham dosyalar yalnız yerel makinede durur.

Bu, `06-ACIK-RISKLER.md` **A-14**'ün kapanışıdır. A-14'ün gerekçesi şuydu:
*"Bu pazarda ret sebebinin bir numarası eksik özellik değil, ürünün gerçek
operasyona oturmamasıdır."* Aşağıdaki bulgular tam olarak o riski ölçüyor.

---

## 1. Ne geldi

| | PDKS (gerçekleşen) | Plan |
|---|---|---|
| Dosya | 48 CSV, ~100 MB | ~70 Excel (xlsx/xlsm) |
| Dönem | Haziran–Eylül 2026 | 2026-06-01 → 2026-09-13 (105 gün, ~15 hafta) |
| Biçim | UTF-8 BOM, `;` ayraçlı, 29 kolon | 4 sayfalı çalışma kitabı |
| İncelenen | 4 dosya | **69 dosya (tamamı)** |

**Kritik bağlam:** Bu bir çağrı merkezi *firması* değil, **bir seyahat
acentesinin tamamı**. İçinde hem çağrı merkezi hem otel operasyonu var:

| Operasyon | Kişi (tek aylık dosyada) |
|---|---|
| Çağrı merkezi satış | 97 |
| Çağrı merkezi müdürlüğü | 62 |
| Otel CC çağrı merkezi | 12 |
| Yiyecek-içecek müdürlüğü | 46 |
| Kat hizmetleri | 39 |
| Mutfak | 37 |
| Otel (Bodrum) | 23 |

**Bu beklenmedik bir hediye.** "Tek üründe çok sektör" iddiamızı **tek bir
veri kümesi üzerinde** sınayabiliriz: aynı firmanın çağrı merkezi ve otel
ekipleri, aynı kural havuzundan çözülebiliyor mu?

---

## 2. PDKS (gerçekleşen) — yapı

Kolonlar: `Simge, SID, sicilno, Ad, Soyad, Firma, Bölüm, Pozisyon, Görev,
Yaka, AltFirma, Direktörlük, mesaitarih, Giriş, Çıkış, MS, NM, AS, FM, GV,
GZ, FAS, OFM, IZS, RM, EM, Mesai Açıklama, İzin Açıklama, RM Açıklama`

**Örnek dosya:** 26.201 satır, 781 çalışan, 30 gün — yani **çalışan × gün tam
takvim ızgarası** (boş günler dahil).

**`MS` = planlanan günlük süre**, yalnız üç değer alıyor:

| MS | Satır | Anlamı |
|---|---|---|
| `10:00` | 18.461 | Vardiyalı çalışma (mola dahil) |
| `00:00` | 6.277 | Çalışma günü değil |
| `07:30` | 1.463 | Standart ofis mesaisi |

`NM, AS, FM, FAS, OFM, IZS, EM` süre kovaları (HH:MM); `GV, GZ, RM` her
satırda `00:00` — **kullanılmıyor.**

### ⚠ Bulgu P-1: Gerçekleşen veri büyük ölçüde eksik

**Giriş/Çıkış kaydı satırların yalnız %18'inde var** (4.714 / 26.201).
781 çalışanın **411'inde** hiç kayıt yok. Çağrı merkezinde bile oran %46.

Kart okutma tutarlı kullanılmıyor. **Sonucu bizim için şu:** "gerçekleşen
veriyi girdi alacağız" kararı (spec) tek başına yetmez — *gerçekleşen verinin
seyrek olabileceği* tasarıma girmeli. Plan × gerçekleşen karşılaştırması
yapacaksak, kayıt yokluğunu "çalışmadı" ile karıştırmamalıyız.

---

## 3. Plan dosyaları — yapı

Her çalışma kitabı 4 sayfa:

| Sayfa | İçerik |
|---|---|
| **Vardiya** | Ana matris: satır = çalışan, kolon = gün. Hücre = `09:00-18:00` ya da durum kodu |
| **HC** | **Kapsama eğrisi**: 41 yarım saatlik dilim (00:00–23:30) × gün. "Şu saatte kaç kişi var" |
| **ÇM2** | İkinci ekibin aynı yapıdaki matrisi (2 haftalık) |
| **IK** | **Kod sözlüğü** — 20 izin/devamsızlık tipi |

Vardiya sayfası başlıkları: `Takım | SicilNo | İsim & Soy İsim | Görevi | HC |
<7 gün> | OFF`

`IK` sözlüğündeki 20 kod: T.İZNİ, C.İZNİ, DEVAMSIZ, D.İZNİ, EĞİTİM, E.İZNİ,
FESİH, R.TATİL, OFF, D.GÖREV, İSTİFA, RAPORLU, TŞ.İZNİ, Ü.Lİ.İZİN,
Ü.SİZ.İZİN, Y.İZİN, S.İZNİ, G-OFF, MAZERET.

---

## 4. Bulgular — bunlar spec'i ve testleri değiştiriyor

### 🔴 B-1 · Kapsama hesabı 69 dosyanın 42'sinde BOZUK

HC sayfası — *"şu saatte kaç kişi var"* sorusunun cevabı — çoğu dosyada
Excel formül hatası veriyor:

| HC sayfasının durumu | Dosya |
|---|---|
| **`#REF!` — kırık formül** | **42** |
| Sayfa hiç yok | 18 |
| Gerçek sayı var | **9** |

**69 planın yalnız 9'unda kapsama hesabı çalışıyor.** (%13)

Yani ekip, vardiya planlarını *"bu planla saat 14:00'te kaç kişi sahada
olacak"* sorusunu **cevaplayamadan** yayınlıyor. Çalışan 6 dosyada kapsama
dilim başına 1–9 kişi, ortalama 4.

**Bu, bu veri kümesindeki en güçlü satış argümanı** — ve iddia değil, kanıt.
Ürünümüzün *doğrulayıcısı* tam olarak bu boşluğu kapatıyor.

### 🔴 B-2 · Gece yarısını aşan 182 vardiya — varsayım değil, gerçek

| Desen | Sayı |
|---|---|
| `16:00-01:00` | 82 |
| `15:00-00:00` | 73 |
| `18:00-00:00` | 11 |
| `18:00-01:00` | 8 |
| `17:00-01:00` | 7 |
| `17:00-00:00` | 1 |
| **Toplam** | **182** |

`02-DEGISMEZLER.md` **G-6** (zaman modeli) ve `04-TEST-HARITASI.md` **G12**
(saat dilimi) bekçisiz açıklardı ve *"vardiya ürünü için kritik"* diye
işaretlenmişti. **Artık varsayım değil:** operasyonun kendisi gece yarısını
aşan vardiya kullanıyor. Çakışma, günlük saat toplamı ve minimum dinlenme
hesapları bu 182 atamada yanlış çıkarsa plan yanlış olur.

**A-5'in önceliği yükseldi.**

### 🟡 B-3 · 18 farklı vardiya deseni — beklediğimizden çok daha fazla

4.625 atama, **18 farklı** başlangıç-bitiş deseni:

| Desen | Sayı | | Desen | Sayı |
|---|---|---|---|---|
| `09:00-18:00` | 2.993 | | `18:00-00:00` | 11 |
| `14:00-23:00` | 635 | | `15:00-21:00` | 8 |
| `11:00-20:00` | 368 | | `18:00-01:00` | 8 |
| `09:00-15:00` | 333 | | `17:00-01:00` | 7 |
| `16:00-01:00` | 82 | | `14:00-20:00` | 3 |
| `15:00-00:00` | 73 | | `10:00-19:00` | 3 |
| `12:00-21:00` | 37 | | `13:30-21:00` | 2 |
| `17:00-23:00` | 32 | | `13:00-22:00` | 1 |
| `12:00-18:00` | 28 | | `17:00-00:00` | 1 |

Uzunluklar 6 ile 9 saat arasında değişiyor; `13:30-21:00` gibi yarım saatlik
başlangıçlar var. **Vardiya kataloğu sabit bir liste değil** — ürün, müşterinin
kendi desenlerini tanımlamasına izin vermeli. Uzun kuyruk (tek seferlik
desenler) da normal.

### 🟡 B-4 · İzin kodları tutarsız yazılıyor — içe aktarmanın birinci işi

17 farklı durum kodu geçiyor, ve **aynı şey farklı yazılmış**:

| Aynı anlam | Bulunan yazımlar |
|---|---|
| Raporlu | `RAPORLU` (85) · `Raporlu` (73) |
| Yıllık izin | `Y.İZİN` (66) · `YILLIK İZİN` (7) · `Y.İzin` (4) |
| Resmî tatil | `R.TATİL` (4) · `R.Tatil` (1) |

Takım adlarında da aynı sorun: `Satış Destek` / `Satış Destek Birimi`,
`FİYATLANDIRMA` / `Fiyatlandırma`.

**Doğrudan sonucu:** İçe aktarma katmanı ham metni olduğu gibi kabul edemez;
eşleme ve normalleştirme adımı şart — ve eşlenemeyen değeri **sessizce
atmak yerine kullanıcıya sormalı.** Ayrıca `M4` testimizin (kültüre bağımlı
`ToLower`) neden var olduğunu hatırla: `Y.İZİN`.ToLower() Türkçe ayarda
`y.izin` değil `y.ızın` verir.

### 🟡 B-5 · Sözlükte olmayan kodlar — "Uzaktan Çalışma"

`IK` sayfasındaki 20 kodun dışında, planlarda şunlar da kullanılmış:

| Kod | Sayı | Durum |
|---|---|---|
| **`Uzaktan Çalışma`** | **48** | Sözlükte **yok**, bizim spec'imizde de yok |
| `Telafi İzni` | 2 | Sözlükte yok |
| `TÇİ` | 1 | Muhtemelen "Telafi Çalışma İzni" kısaltması |
| `-` | 10 | Anlamsız girdi |

**"Uzaktan çalışma" bir izin değil** — kişi çalışıyor ama sahada değil.
Kapsama hesabında sayılmalı mı? Muhtemelen hayır (telefon açmıyor). Bu,
spec'te olmayan **yeni bir durum türü** ve kapsama mantığını etkiliyor.

*Mustafa'nın cevaplaması gereken ürün sorusu:* uzaktan çalışan bir kişi
kapsama sayısına dahil mi?

### 🟢 B-6 · Talep hesabı Erlang-C ile yapılıyor, verisi yok

Mustafa'nın notu: *"Yük hesaplamasını vardiyaları ayarlarken Erlang-C
yöntemiyle yapıyorlar."* Erlang-C, çağrı hacmi + ortalama görüşme süresi +
hedef servis seviyesinden **kaç kişi gerektiğini** hesaplar.

**Elimizde çağrı hacmi verisi yok** — yalnız sonucu (plan) ve gerçekleşen var.

Bunun spec'e etkisi var: bizim modelimizde talep bir **girdi**
(*"o saat o ekipte kaç kişi"*). Müşterinin gerçek akışında ise talep, çağrı
tahmininden **türetiliyor**. Yani müşteri bu hesabı hâlâ Excel'de yapıp
sonucu bize girecek. Bu bir engel değil ama **sürtünme** — ve rakip ürünlerin
çoğunda Erlang-C dahili.

*Karar gerektiren:* Erlang-C hesabını ürünün içine almak kapsamda mı?
(Formül karmaşık değil; girdi verisi ise müşterinin santralinden gelir.)

---

## 4b. Gerçek planlarda bulunan kural ihlalleri

**69 dosyanın tamamı** tek bir kanonik tabloya indirildi (aynı gün için birden
çok revizyon varsa **en son dosya** esas alındı): **4.625 vardiya ataması,
96 kişi, 2026-06-01 → 2026-09-13.**

Bu iş `07-motor/donusturucu.py` ile yapıldı; denetim
`07-motor/dogrulayici.py` ile. ⚠ O klasörde **motor yok** — bkz.
`07-motor/OKU-BENI.md`.

### ⚠ Önce dürüst uyarı: bunlar BRÜT aralık

Plan hücresi `09:00-18:00` yazıyor — bu 9 saatlik **aralık**. Molanın ücretli
mi ücretsiz mi olduğu **plan dosyasında hiç yok**. Ücretsiz 1 saat mola varsa
net süre 8 saat olur ve aşağıdaki saat rakamları düşer. Dinlenme aralığı
bulguları molalardan etkilenmez, saat toplamı bulguları etkilenir.

*Bu uyarının kendisi bir bulgu: **plan dosyası mola bilgisi taşımıyor.***

### Vardiya süresi dağılımı (brüt)

| Süre | Atama |
|---|---|
| 9 saat | 3.551 |
| 6 saat | 388 |
| 8 saat | 6 |
| 7 saat | 8 |
| 7,5 saat | 2 |

Fiilen iki vardiya uzunluğu var: tam gün (9 sa) ve yarım gün (6 sa).

### Doğrulama özeti: **529 kural ihlali**

`07-motor/dogrulayici.py` çıktısı (69 dosya, kurallar `kurallar.json` v1.0):

| Kural | Vaka | Kişi |
|---|---|---|
| `V04_HAFTALIK` — haftalık net 45 saat aşımı | 274 | 50 |
| `V_ARDISIK` — 6 günden fazla ardışık çalışma | 167 | 37 |
| `V03_DINLENME` — ardışık vardiya arası < 11 saat | 88 | 27 |
| **TOPLAM** | **529** | |

⚠ **Bu bir ALT SINIR.** Veri kısmi: kişi başına dönemin ~%58'i kayıtlı,
çünkü plan dosyaları ekip ekip ve her gün herkesi kapsamıyor. Eksik gün
ihlalleri **gizler, uydurmaz** — dolayısıyla gerçek sayı bundan yüksektir.
Doğrulayıcı bu tamlık oranını kendisi raporlar.

⚠ **`V04_HAFTALIK` varsayıma duyarlı:** mola `kurallar.json` içinde
vardiya başına −1 saat kabul edildi (plan dosyalarında mola bilgisi yok).
Mola 1,5 saat olsaydı bu ihlallerin çoğu kaybolurdu. Eşiği değiştirip tekrar
koşmak, kararın varsayıma ne kadar bağlı olduğunu görmenin en hızlı yolu.

### Bulgu B-7 · Ardışık vardiyalar arası dinlenme 8 saate kadar düşüyor

| Kontrol | Sonuç |
|---|---|
| Ardışık vardiyalar arası **< 11 saat** | **88 vaka / 27 kişi** |
| **En kısa dinlenme aralığı** | **8 saat** |

Örüntü açık: gece vardiyası `16:00-01:00` biten kişi, ertesi gün `09:00-18:00`
ile başlıyor → **8 saat** ara. 11 saat, yaygın olarak kullanılan asgari
günlük dinlenme eşiğidir; bunun sözleşmeye/sektöre göre yasal bir ihlal olup
olmadığı ayrıca teyit edilmeli — ama **operasyonel olarak** 8 saatlik ara
(yol ve uyku dahil) sürdürülebilir değil.

**Bu, ürünümüzün V03 değişmezinin (minimum dinlenme) gerçek karşılığıdır ve
mevcut süreç onu yakalamıyor.**

### Bulgu B-8 · Haftalık süre ve ardışık gün

| Kontrol | Sonuç |
|---|---|
| Haftalık **net** 45 saat aşımı (mola −1 sa varsayımıyla) | **274 kişi-hafta / 50 kişi** |
| **6 günden fazla** ardışık çalışma | **167 vaka / 37 kişi** |
| Haftada 6 çalışma günü (ihlal değil, ölçüm) | 651 kişi-hafta / 91 kişi |
| Haftada 7 çalışma günü (hiç OFF yok) | **0** — haftalık tatil hep verilmiş |

6 gün × 9 saat = 54 saat brüt. Ücretsiz 1 saat mola varsa net 48 saat — yine
45'in üstünde. **Molasız hesapla emin konuşulamaz; bu yüzden mola modellemesi
ürün için zorunlu.**

İyi haber: haftalık tatil hiç atlanmamış (0 vaka).

### Bulgu B-9 · Planlama ufku sabit değil: 7–35 gün

Vardiya sayfasındaki tarih kolonu sayısı dosyadan dosyaya değişiyor:
**7, 9, 15, 16, 21, 28, 30, 35 gün.** Bazı planlar 1 haftalık, bazıları 5
haftalık. Bizim modelimiz tek bir ufuk varsayıyor — **değişken ufku
desteklemeli.**

### Bulgu B-10 · Kadro dönem içinde değişiyor

89 kişinin yalnız **46'sı** dört ayın hepsinde planda var. **27 kişi**
Haziran-Temmuz'da görünüp sonra kayboluyor. Planlarda `İSTİFA` (26) ve
`FESİH` kodları da geçiyor.

**Çağrı merkezinde devir hızı yüksek — kadro sabit değil.** Ürün, dönem
ortasında işe giren/ayrılan kişiyi birinci sınıf durum olarak ele almalı.

### Bulgu B-11 · Üç ayrı tüzel kişilik, yedi farklı yazım

PDKS'te `Firma` kolonu 7 farklı değer taşıyor ama gerçekte 3 şirket:

| Kişi | Firma |
|---|---|
| 559 | Ana acente A.Ş. |
| 170 | Bağlı acente A.Ş. |
| 45 + 2 + 1 + 1 | Kurumsal hizmetler A.Ş. — **aynı şirket, dört farklı yazım** |
| 7 | `- - - - - - -` (boş) |

**Bu çok kiracılık modelimizi ilgilendiriyordu** — bir müşteri = bir tüzel
kişilik mi, yoksa bir grup içinde birden çok şirket mi?

✅ **Karar verildi (14 Eylül):** *"Buraya takılma. Şu an tek şirket
mantığıyla ilerleyeceğiz."* Grup yapısı ürün kapsamına girmiyor.

---

## 4c. Alınan kararlar (13–14 Eylül, Mustafa)

> **Bu bölüm bulgulardan daha bağlayıcıdır.** Aşağıdaki her satır, bir
> bulgunun ürüne nasıl (ya da hiç) yansıyacağını belirler. Yeni bir pencere
> bu tabloyu okumadan bulgulara göre iş yapmamalı.

### Kapsam kararları

| Konu | Karar |
|---|---|
| **Erlang-C hesabı** | **Kapsam DIŞI.** Erlang ekranı planlanmıyor; müşteri bunu 3. parti ortamda veya kendi trafik verisiyle yapar. |
| **Geçmiş veriden yoğunluk tahmini** | **Kapsam İÇİ ve önemli.** Talep tahmini geçmiş veriden türetilecek. |
| **Analiz kapsamı** | **Otel tarafı analiz edilmeyecek.** Bizim için asıl veri **çağrı merkezi + plan**. PDKS'in grup geneli gelmesi ihracat hatası. |
| **Çok tüzel kişilik (B-11)** | **Takılma.** Şu an **tek şirket mantığıyla** ilerlenecek. |
| **Evden çalışma (B-5)** | **Önemli bulgu değil.** Takılma. |
| **Anonimleştirme** | **Yapılmayacak.** Veri bu hâliyle kullanılacak; git'e girmemesi yeterli koruma. |

### Veri kalitesi kararları — "düzeltmeyi ürün değil kullanıcı yapar"

| Konu | Karar |
|---|---|
| **Yükleme formatı** | Gerçekleşen veri ve izinlerin **doğru formatta yüklenmesi müşterinin sorumluluğu.** |
| **Tutarsız kodlar (B-4)** | **Takılma.** Ağır normalleştirme katmanı yazılmayacak; **editör ekranında kullanıcı kolayca düzeltir.** Bu, mevcut analizden çıkarım yapılacak bir konu değil. |
| **Gerçekleşen kaynağı (P-1)** | **Santral veya PDKS — ikisiyle de devam.** Tek kaynağa bağlanılmayacak. |

**Mimari sonucu:** Veri temizliği yükü **içe aktarma katmanından editör
ekranına** kaydı. Editör, hatalı/eksik veriyi görünür kılıp hızlı düzeltmeye
izin vermek zorunda — yani editör bir "rahatlık" değil, **veri kalitesi
mekanizması**.

### ⛔ REDDEDİLEN öneri: değişken planlama ufku (B-9)

Claude "plan ufku 7–35 gün arası değişiyor, modelimiz bunu desteklemeli"
demişti. **Mustafa reddetti ve gerekçesi daha güçlü:**

> *"Biz ayın 1'inden itibaren ilgili ay içerisinde adalet kurallarını
> uygulayacağız. Kullanıcı '35 günlük plan yapıyorum' diyemez. İsterse 35 günü
> 5'e böler veya 30 ve 5 olarak planlar. Planlar genelde 1 veya 2 haftalık
> yapılır, en zoru aylık. 2 aylık plan izin vb. durumlar zaten realist değil."*

**Kural:** Planlama ufku **takvim ayını aşamaz.** Adalet penceresi = takvim
ayı, ayın 1'inde başlar. Veride görülen 35 günlük plan, ürünümüzde iki plana
bölünür.

*Neden bu daha iyi:* Adalet ölçümü (OFF dağılımı, gece nöbeti dağılımı, fazla
mesai) sabit bir pencereye ihtiyaç duyar. Kayan/değişken ufuk, adaleti
ölçülemez hâle getirir. Veriden gelen "esneklik" aslında bir düzensizlikti.

### ⭐ SATIŞ NOKTALARI — bulgular ürün argümanına dönüştü

| # | Satış noktası | Kanıt |
|---|---|---|
| **1** | **Devir hızından dolayı yönetilemeyen operasyon.** Çağrı merkezinde kadro sürekli değişiyor; mevcut süreç bunu yönetemiyor. **Ürünün kritik özelliği.** | **B-10**: 89 kişinin yalnız 46'sı dört ayda da var; 27 kişi iki ay sonra kayboluyor |
| **2** | **Mola planlama ve adil dağıtım.** *"Bununla uğraşanı görmedim planlamada. Bu hep gün içinde yönetilir."* | **B-8**: plan dosyası mola bilgisi taşımıyor, dolayısıyla net çalışma süresi hesaplanamıyor |
| **3** | **Kapsama hesabı çalışmıyor.** Ekip planı, *"saat 14:00'te kaç kişi olacak"* sorusunu cevaplayamadan yayınlıyor. | **B-1**: 43 planın 28'inde HC sayfası `#REF!` |
| 4 | Kural ihlalleri sessiz kalıyor (satış argümanı, mühendislik sorunu değil) | **B-7**: 62 vakada ardışık vardiya arası 8 saate düşüyor |

**B-7 hakkında Mustafa'nın notu:** *"Bu zaten bizim satarken ortaya
koyabileceğimiz bir müşteri hatası. Doğrusu bu değil, mevzuat da insanlık da
bunu desteklemez."* — Yani bu bulgu **düzeltilecek bir teknik sorun değil**,
gösterilecek bir kanıt.

### 🔴 Yeni kapsam maddesi: MOLA MODELİ

Satış noktası 2'nin doğrudan sonucu. Mola artık bir "detay" değil, **ürünün
ayırt edici özelliği.** Gerektirdikleri:

1. Mola, vardiya içinde **planlanan bir blok** olarak modellenmeli
2. **Adil dağıtılmalı** — kimse sürekli kötü saatte mola almamalı
3. **Kapsamadan düşülmeli** — molada olan kişi çağrı açmıyor
4. Ücretli/ücretsiz ayrımı, net çalışma süresi hesabı için gerekli

**Motor üzerindeki etkisi dürüstçe:** Bu, çözücüyü zorlaştırır. Vardiya
atama + vardiya içi mola yerleştirme iki ayrı optimizasyon katmanıdır ve
sektörde genelde iki fazda çözülür (önce vardiya, sonra mola). Motor
sözleşmesi (A-10) bunu baştan hesaba katmalı.

---

## 5. Spec ve test etkisi

| Bulgu | Etki | Nereye |
|---|---|---|
| B-1 kapsama kırık | Doğrulayıcının en kritik çıktısı kapsama raporu | A-10 motor sözleşmesi |
| B-2 gece yarısı | **A-5 önceliği yükseldi**, artık kanıtlı | A-5, G-6, V02/V03 |
| B-3 17 desen | Vardiya kataloğu müşteri tanımlı olmalı | Spec §kural |
| B-4 tutarsız kod | İçe aktarmada normalleştirme + kullanıcıya sorma | Spec §içe aktarma |
| B-5 evden çalışma | ✅ Karar verildi: çalışma biçimi, kapsamaya dahil | Spec §kural |
| B-6 Erlang-C | ✅ Karar verildi: kapsam dışı. Yoğunluk tahmini kapsam içi | Spec §talep |
| P-1 gerçekleşen seyrek | Santral verisine geçilecek — büyük ölçüde çözülüyor | Spec §gerçekleşen |
| **B-7 dinlenme 8 saate düşüyor** | **V03'ün gerçek karşılığı; mevcut süreç yakalamıyor** | A-5, V03 |
| **B-8 haftalık 45+ saat** | Mola modellenmeden net süre hesaplanamaz | **Spec: mola modeli** |
| **B-9 ufuk 7–35 gün** | Sabit ufuk varsayımı yanlış | Spec §plan |
| **B-10 kadro değişiyor** | Dönem ortası giriş/çıkış birinci sınıf durum | Spec §çalışan |
| B-11 üç tüzel kişilik | ✅ Karar verildi: tek şirket mantığı, grup yapısı kapsam dışı | — |

### Artık gerçek veriye dayandırılabilecek testler

Bu veri, `04-TEST-HARITASI.md`'deki boş senaryo sınıflarından üçünü
**gerçek örneklerle** doldurmamızı sağlıyor:

- **G12 saat dilimi** → 182 gerçek gece-yarısı ataması
- **G02 sınır değerler** → kapsama 1–9 kişi arasında; 1 kişilik dilimler var
- **G03/G04 boş ve bozuk girdi** → `#REF!`, `-`, tutarsız kodlar, %18 dolu
  Giriş/Çıkış

Ayrıca **alt uç ölçek** (A-10 matrisi) gerçek veriyle sınanabilir: 12 kişilik
otel CC ekibi ile 97 kişilik çağrı merkezi aynı veri kümesinde.

---

## 6. Sonraki adım

| # | İş | Durum |
|---|---|---|
| 1 | ~~Anonimleştirme betiği~~ | ⛔ **İptal** — veri bu hâliyle kullanılacak |
| 2 | Plan → kanonik model dönüştürücü | ✅ **Yapıldı** → `07-motor/donusturucu.py` |
| 3 | Doğrulayıcı prototipi | ✅ **Yapıldı** → `07-motor/dogrulayici.py`, **529 ihlal** bulundu |
| 4 | Bekleyen kararlar | ✅ Hepsi §4c'de cevaplandı |
| 5 | **Motor sözleşmesi (A-10)** | ⏭ **SIRADAKİ İŞ** — V01–V12 + mola modeli + UNSAT biçimi |

**2 ve 3 neden şimdi ve neden bu sırayla:** M-09'da karar verilmişti —
*doğrulayıcı önce, çözücü sonra.* Elimizde artık gerçek plan var, yani
doğrulayıcı daha yazıldığı gün gerçek veriyle sınanabilir. Bu, motorun ilk
gerçek parçasıdır; bu yüzden `06-veri` altında değil **`07-motor/`** altında
duruyor: kod git'e girer, veri girmez.
