# 16 Eylül 2026 · Fikstürler ve test iskeleti

**Pencere:** Claude (Cowork) · yazma hakkı bu pencerede
**Girdi:** `08-motor-testleri/v5/KABUL-OLCUTLERI.md` (15 Eylül'de onaylandı, dondurulmuş)
**Çıktı:** 11 fikstür + ortak sahne, koşan bir pytest paketi, 20 xUnit taslağı
**Ürün kodu değişmedi. CI'ya dokunulmadı. 39/39 hâlâ yeşil.**

---

## Ne yapıldı

Onaylı kabul cümleleri önce **veriye**, sonra **koşan teste** çevrildi.
Zincir kapandı:

```
KABUL-OLCUTLERI.md  →  fikstur/*.json  →  testler/  →  (motor: yok)
```

Son halka boş olduğu için yedi senaryo kırmızı. **İstenen budur** —
Master Spec §16.4 "kırmızı kanıt" kuralı, bir testin yeşile dönmeden önce
kırmızı yanmasını şart koşar.

```
py -m pytest -q   →   7 failed, 3 passed, 4 skipped
```

| | Kaç | Hangileri | Neden |
|---|---|---|---|
| 🔴 | 7 | A1, A3, A4, A6, A7, A8, A9 | Motor yok |
| 🟢 | 3 | Paketin kendi sağlığı | Motorsuz da geçmeli |
| ⏭ | 4 | A2, A10, A11, A12 | Backend senaryosu, xUnit tarafında |

---

## Alınan kararlar

### 1. Fikstür veri, test kod

Fikstür `"C08 hicbir Sali calismaz"` cümlesini taşır ama **nasıl** kontrol
edileceğini bilmez. Gövde `kontroller.py` içinde. Sebebi: fikstürler motor
hangi dille yazılırsa yazılsın aynı kalmalı; kontrol gövdeleri test çatısına
ait.

### 2. Sahne ortaklaştırıldı

On bir fikstürün on biri aynı gerçekçi sahneye (S-10) dayanıyor; her biri
yalnız kendi `fark`ını taşıyor. Sahne 11 yere kopyalansaydı, bir düzeltme
on bir yerde yapılırdı ve biri unutulurdu.

### 3. `fikstur_yukleyici.py` ortak modüle çıkarıldı

`fikstur-denetleyici.py` ile testler aynı `fark` birleştirme mantığını
kullanmalı. İki ayrı uygulama olsaydı denetleyici *"tutarlı"* derken test
başka bir şey sınıyor olabilirdi — ve bunu kimse fark etmezdi.

### 4. Motorla tek temas noktası

`motor_istemci.py`. Motor yazıldığında **yalnız bu dosya** değişecek;
fikstürlerin, kabul ölçütünün ve kontrollerin tek satırı değişmeyecek.

### 5. İki şey bilerek bozuk bırakıldı — ikisi de CI'ı korumak için

| Ne | Neden |
|---|---|
| C# taslakları `.cs` değil, `.cs.taslak` | Dayandıkları tablolar (plan tabloları, `leaves.durum`, `rules.yasal`) yok. `.cs` olsalardı **derleme hatası** verir, CI'ı kırardı |
| pytest paketi CI'a bağlanmadı | Kırmızı bir paketi kapıya bağlamak "main her zaman yeşil" kuralını bozardı |

İkisi de eksikliği **gizlemiyor**: taslakta 20 test adı ve ne bekledikleri
yazılı, pytest paketi koşuyor ve neden kırmızı olduğunu mesajında söylüyor.

---

## Kırmızı kanıt — iki kez yapıldı

Denetleyicilerin gerçekten bir şey yakaladığını görmek için fikstürler
kasten bozuldu:

**Birinci tur (4 bozma):** bir vardiya saati kaydırıldı · kabul ölçütü
çapası kırıldı · olmayan bir çalışan kimliği yazıldı · bilinmeyen bir `tip`
verildi. Dördü de yakalandı, çıkış kodu 1.

**İkinci tur (2 bozma):** sert ihlal sayısı yanlış yazıldı · yumuşak ihlal
listesi boşaltıldı. İkisi de yakalandı.

Test iskeleti tarafında da bir eksik **kendiliğinden** yakalandı:
`test_her_kontrol_adinin_govdesi_var` kırmızı yandı — A07 fikstüründe geçen
`adalet_ihlali_sert_sayilmaz` kontrolünün gövdesi yazılmamıştı.

---

## Yakalanan kendi hatam

`DENETIM.py`'nin 3. kontrolü (dosya yolları) belgelerdeki her ters tırnaklı
yolu depo kökünden, belgenin kendi klasöründen ve `00-DEVIR/`'den arıyor.
Ben belgelerde kısa yol yazmıştım:

```
v5/fikstur/OKU-BENI.md      testler/kontroller.py      backend-taslak/
```

Bunların hiçbiri üç tabandan da çözülmüyor — **hepsi "bulunamayan yol"
hatası üretecekti.**

Mustafa `DENETIM.py`'yi henüz koşturamadığı için (8 Eylül Windows
güncellemesi, bkz. §7) bu hata üç oturumdur görünmemişti. Bütün yollar depo
kökünden yazıldı.

Ayrıca **henüz yazılmamış** `02-spec/v1.4-master-spec.md`, gerekçesiyle
birlikte `YOK_AMA_KASITLI` listesine eklendi — ve listeye *"v1.4 yazılınca
bu satır silinir"* notu düşüldü, yoksa gerçekten kaybolan bir dosyayı gizler.

*Öğrenilen: bir denetleyici yazmak, denetlediği şeyi yazmaktan daha çok
düzeltme doğuruyor. Kısa yol okurken rahattı, makine için yanlıştı —
"okunabilir" ile "doğrulanabilir" aynı şey değil.*

---

## Değişmeyen şeyler

- Ürün kodu: **hiç dokunulmadı**
- CI yapılandırması: **hiç dokunulmadı**
- `02-spec/v1.3-master-spec.md`: **hiç dokunulmadı** (v1.4 ayrı dosya olacak)
- Dondurulmuş sürümler v1–v5 `KABUL-OLCUTLERI.md`: **hiç dokunulmadı**
- Kapsama: **büyümedi.** Bekçi, test yeşile döndüğünde doğar

---

## Hâlâ koşulmamış olan

**`py DENETIM.py` bu pencerede de koşturulamadı.** Dört oturumdur aynı sebep:
8 Eylül Windows güncellemesi, uzaktan kabuk Mustafa'nın diskine bağlanamıyor.
Dosyalar yazılabiliyor (stage/commit), komut çalıştırılamıyor.

Sonuç: **commit kontrolü hiç koşmadı.** Diğer yedi kontrolün mantığı burada
elle taklit edildi (yol listesi çıkarıldı, cihazdaki dosyalarla karşılaştırıldı)
ama bu bir taklit — asıl koşu Mustafa'nın makinesinde yapılmalı:

```
cd C:\Users\PC\Desktop\Tshift
py DENETIM.py
```

---

## Sıradaki

**Şartname v1.4 (A-15).** Motor bundan önce yazılamaz: `yasal` sütunu
olmadan K-10 ve K-16 uygulanamaz, `leaves` durum alanı olmadan K-9
uygulanamaz. On maddelik liste `08-motor-testleri/v5/KABUL-OLCUTLERI.md` §8'de.

Karara bağlanacak açık tasarım sorusu: `yasal` bayrağı **kuralın mı eşiğin
mi** özelliği? `GUNLUK_AZAMI` için kanunî tavan 11, bizim varsayılanımız 9 —
9'u aşmak firma kuralı ihlali, 11'i aşmak yasal ihlal. Tek bayrak bu ikisini
ayıramıyor.
