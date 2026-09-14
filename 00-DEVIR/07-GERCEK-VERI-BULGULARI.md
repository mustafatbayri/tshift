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
| İncelenen | 4 dosya | 43 dosya |

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

### 🔴 B-1 · Kapsama hesabı 43 dosyanın 28'inde BOZUK

HC sayfası — *"şu saatte kaç kişi var"* sorusunun cevabı — çoğu dosyada
Excel formül hatası veriyor:

| HC sayfasının durumu | Dosya |
|---|---|
| **`#REF!` — kırık formül** | **28** |
| Sayfa hiç yok | 9 |
| Gerçek sayı var | **6** |

**İncelenen 43 planın yalnız 6'sında kapsama hesabı çalışıyor.**

Yani ekip, vardiya planlarını *"bu planla saat 14:00'te kaç kişi sahada
olacak"* sorusunu **cevaplayamadan** yayınlıyor. Çalışan 6 dosyada kapsama
dilim başına 1–9 kişi, ortalama 4.

**Bu, bu veri kümesindeki en güçlü satış argümanı** — ve iddia değil, kanıt.
Ürünümüzün *doğrulayıcısı* tam olarak bu boşluğu kapatıyor.

### 🔴 B-2 · Gece yarısını aşan 175 vardiya — varsayım değil, gerçek

| Desen | Sayı |
|---|---|
| `16:00-01:00` | 84 |
| `15:00-00:00` | 66 |
| `18:00-00:00` | 11 |
| `18:00-01:00` | 7 |
| `17:00-01:00` | 6 |
| `17:00-00:00` | 1 |
| **Toplam** | **175** |

`02-DEGISMEZLER.md` **G-6** (zaman modeli) ve `04-TEST-HARITASI.md` **G12**
(saat dilimi) bekçisiz açıklardı ve *"vardiya ürünü için kritik"* diye
işaretlenmişti. **Artık varsayım değil:** operasyonun kendisi gece yarısını
aşan vardiya kullanıyor. Çakışma, günlük saat toplamı ve minimum dinlenme
hesapları bu 175 atamada yanlış çıkarsa plan yanlış olur.

**A-5'in önceliği yükseldi.**

### 🟡 B-3 · 17 farklı vardiya deseni — beklediğimizden çok daha fazla

4.795 atama, **17 farklı** başlangıç-bitiş deseni:

| Desen | Sayı | | Desen | Sayı |
|---|---|---|---|---|
| `09:00-18:00` | 3.170 | | `12:00-18:00` | 31 |
| `14:00-23:00` | 601 | | `18:00-00:00` | 11 |
| `09:00-15:00` | 404 | | `15:00-21:00` | 8 |
| `11:00-20:00` | 291 | | `18:00-01:00` | 7 |
| `16:00-01:00` | 84 | | `17:00-01:00` | 6 |
| `15:00-00:00` | 66 | | `14:00-20:00` | 6 |
| `12:00-21:00` | 53 | | `10:00-19:00` | 3 |
| `17:00-23:00` | 51 | | `13:30-21:00` | 2 |
| | | | `17:00-00:00` | 1 |

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

43 dosya tek bir kanonik tabloya indirildi (aynı gün için birden çok revizyon
varsa **en son dosya** esas alındı): **3.955 vardiya ataması, 86 kişi,
2026-06-01 → 2026-09-13.**

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

### Bulgu B-7 · Ardışık vardiyalar arası dinlenme 8 saate kadar düşüyor

| Kontrol | Sonuç |
|---|---|
| Ardışık vardiyalar arası **< 11 saat** | **62 vaka / 25 kişi** |
| Ardışık vardiyalar arası < 12 saat | 65 vaka / 27 kişi |
| **En kısa dinlenme aralığı** | **8 saat** |

Örüntü açık: gece vardiyası `16:00-01:00` biten kişi, ertesi gün `09:00-18:00`
ile başlıyor → **8 saat** ara. 11 saat, yaygın olarak kullanılan asgari
günlük dinlenme eşiğidir; bunun sözleşmeye/sektöre göre yasal bir ihlal olup
olmadığı ayrıca teyit edilmeli — ama **operasyonel olarak** 8 saatlik ara
(yol ve uyku dahil) sürdürülebilir değil.

**Bu, ürünümüzün V03 değişmezinin (minimum dinlenme) gerçek karşılığıdır ve
mevcut süreç onu yakalamıyor.**

### Bulgu B-8 · Haftalık süre: 553 kişi-hafta 45 saatin üstünde (brüt)

| Kontrol | Sonuç |
|---|---|
| Haftalık brüt 45 saat aşımı | 553 kişi-hafta / 84 kişi (en yüksek 54 sa) |
| Haftada 6 çalışma günü | 553 kişi-hafta / 84 kişi |
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

**Bu doğrudan çok kiracılık modelimizi ilgilendiriyor:** bir müşteri = bir
tüzel kişilik mi, yoksa bir grup içinde birden çok şirket mi? Veride
`AltFirma` kolonu da var. **Mustafa'nın kararı gereken bir spec sorusu.**

---

## 4c. Alınan kararlar (13 Eylül, Mustafa)

| Konu | Karar |
|---|---|
| **Erlang-C hesabı** | **Kapsam DIŞI.** Erlang hesabı yapan bir ekran planlanmıyor; müşteriler bunu 3. parti ortamlarda veya kendi trafik verileriyle yapar. |
| **Geçmiş veriden yoğunluk tahmini** | **Kapsam İÇİ ve önemli.** Talep tahmini geçmiş veriden türetilecek. |
| **"Uzaktan Çalışma" (B-5)** | **Evden çalışma demek** — kişi PC ile bağlanıp çalışıyor. İzin değil, **çalışma biçimi**. Kapsama sayısına dahil edilmeli. |
| **Gerçekleşen verinin kaynağı** | PDKS değil, büyük ihtimalle **çağrı merkezi santral sistemi**. Çağrının ilk açılış ve son kapanış saati alınabiliyor; mola bilgisi olmasa da realizasyon için yeterli. |

**Santral kararının sonucu:** P-1'deki "%18 dolu Giriş/Çıkış" sorunu
büyük ölçüde çözülüyor — santral verisi PDKS'ten çok daha eksiksiz olacak.
Ama santral verisi de **mola taşımıyor**, yani B-7/B-8'deki brüt/net sorunu
devam ediyor. Mola ya planda tanımlanmalı ya da parametre olarak girilmeli.

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
| **B-11 üç tüzel kişilik** | Bir müşteri = bir şirket mi, grup mu? | **Mustafa'nın kararı** |

### Artık gerçek veriye dayandırılabilecek testler

Bu veri, `04-TEST-HARITASI.md`'deki boş senaryo sınıflarından üçünü
**gerçek örneklerle** doldurmamızı sağlıyor:

- **G12 saat dilimi** → 175 gerçek gece-yarısı ataması
- **G02 sınır değerler** → kapsama 1–9 kişi arasında; 1 kişilik dilimler var
- **G03/G04 boş ve bozuk girdi** → `#REF!`, `-`, tutarsız kodlar, %18 dolu
  Giriş/Çıkış

Ayrıca **alt uç ölçek** (A-10 matrisi) gerçek veriyle sınanabilir: 12 kişilik
otel CC ekibi ile 97 kişilik çağrı merkezi aynı veri kümesinde.

---

## 6. Sonraki adım

1. **Anonimleştirme betiği** — `06-veri/anonim` altına sicil→takma kimlik
   eşlemesiyle türetilmiş veri. Testlerde bu kullanılacak, ham veri hiç
   kullanılmayacak.
2. **Plan → kanonik model dönüştürücü** — 43 dosyanın tamamını tek bir
   normalleştirilmiş yapıya çevir; tutarsız kodları eşle, eşlenemeyeni raporla.
3. **Doğrulayıcı prototipi** — gerçek planları V01–V12'ye karşı denetle.
   **Beklenti: gerçek planlarda ihlal bulacağız.** Bulursak bu kötü haber
   değil, ürünün varlık sebebinin kanıtı olur.
4. Mustafa'nın iki kararı: B-5 (uzaktan çalışma kapsama sayılır mı) ve
   B-6 (Erlang-C kapsamda mı).
