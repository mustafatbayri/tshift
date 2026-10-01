# 07-motor — DİKKAT: burada henüz MOTOR YOK

> **Bu klasördeki dosyalar ürünün motoru değildir.**
> Yanlış anlaşılmaya yol açtığı için bu not yazıldı (14 Eylül 2026).

## Burada ne var

Müşterinin **geçmiş Excel planlarını ölçen iki analiz betiği.** Plan
üretmezler, atama yapmazlar. Sadece okur ve denetlerler.

| Dosya | Ne yapar |
|---|---|
| `donusturucu.py` | 69 Excel dosyasını tek bir kanonik CSV'ye çevirir. Aynı güne birden çok revizyon varsa **en sonuncuyu** esas alır. |
| `dogrulayici.py` | O CSV'yi kurallara karşı denetler, ihlal listesi üretir. Ayrıca **kendi girdisinin ne kadar tam olduğunu** raporlar. |
| `kurallar.json` | Eşik değerleri (dinlenme, haftalık saat, ardışık gün). **Kod değil veri** — M-10. |
| `pdks-ms-gece-yarisi.py` | 🆕 1 Ekim. PDKS ihracatlarını okur, **yalnız sayı** yazar: `MS` alanı plan mı takvim mi, gece yarısını aşan vardiya hangi güne yazılıyor, saat kovaları güvenilir mi. İsim/sicil/firma/bölüm adı yazmaz. Bulgular: `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` §7 |

**Amaçları:** `06-ACIK-RISKLER.md` A-14'ün sorusunu ölçmek —
*"ürünümüz gerçek operasyonda bir işe yarar mı?"* Cevap kanıtla verildi:
mevcut süreç 529 kural ihlali üretmiş ve kimse fark etmemiş.

Yani bunlar **kanıt üretme aracı**, ürün kodu değil.

## Burada ne YOK

**Motorun kendisi.** Motor, plan **üreten** şeydir: çalışanları, kuralları ve
talebi alıp *"kim ne zaman çalışacak"* çıktısını verir. Yazılmadı, çünkü:

- **Motor sözleşmesi (A-10) yazılmadı** — girdi şeması, çıktı şeması,
  UNSAT biçimi, zaman aşımı davranışı, tekrarlanabilirlik garantisi
- **V01–V12 değişmez listesi** Mustafa ile kesinleştirilmedi
- Çözücü (OR-Tools CP-SAT) kurulmadı

## Bu betikler ürün doğrulayıcısı mı olacak?

**Hayır.** M-09'daki *"doğrulayıcı önce, çözücü sonra"* kararı **ürünün**
doğrulayıcısını kastediyor: bizim kanonik veri modelimizle çalışan, testleri
ve sözleşmesi olan bir bileşen.

Bu betikler ise **müşterinin Excel şablonunu** okur. Ürün doğrulayıcısı
yazılırken bunların **büyük kısmı atılır.** Kalıcı olan:

- `kurallar.json`'daki eşikler ve kural adlandırması
- Doğrulayıcının kendi girdi tamlığını raporlaması fikri
- `07-GERCEK-VERI-BULGULARI.md`'deki öğrenilenler

## Açık karar

Klasör adı yanıltıcı. **`08-analiz/` olarak yeniden adlandırılması önerildi,
Mustafa henüz karar vermedi.** Karar verilene kadar bu not burada durur.

## Çalıştırma

```
py -m pip install openpyxl pandas       (bir kereliğine)
cd C:\Users\PC\Desktop\Tshift\07-motor
py donusturucu.py
py dogrulayici.py
```

Girdi: `../06-veri/ham/plan` · Çıktı: `../06-veri/kanonik` ve `../06-veri/rapor`

PDKS betiği (klasörleri komut satırında ver; vermezsen `../06-veri/ham` altında arar):

```
cd C:\Users\PC\Desktop\Tshift\07-motor
py pdks-ms-gece-yarisi.py "C:\...\pdks\2026-07" "C:\...\pdks\2026-08" "C:\...\pdks\2026-09"
```

Çıktı: ekran + `../06-veri/pdks-ms-gece-yarisi-raporu.txt` (git dışı).
(ikisi de `.gitignore` içinde — veri git'e girmez).
