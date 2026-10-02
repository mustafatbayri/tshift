# Keşif — hedef eksiği kaçınılmaz mı? (2 Ekim 2026)

> ⚠ **Bu klasör bir KEŞİF arşividir, ölçüm aracı değildir.** `taban.py` tek
> oturumda yazıldı, **testi yok**, kural tanımları şartnameden değil motorun
> kodundan ve veri setinden okunarak yazıldı. Sonuçları karar dayanağı
> yapılmadan önce araç olarak baştan (şartnameden okunarak, testleriyle)
> yazılmalıdır. Arşivlenme sebebi: bulgu tekrar üretilebilsin.

## İçindekiler

1. [Soru](#1-soru)
2. [Ne yapıldı](#2-ne-yapıldı)
3. [Sonuç](#3-sonuç)
4. [Bu sonucun sınırı](#4-bu-sonucun-sınırı)
5. [Nasıl çalıştırılır](#5-nasıl-çalıştırılır)

## 1. Soru

`00-DEVIR/06-ACIK-RISKLER.md` T-60 bulgu 7: tam ölçekte (500 kişi, %95
doluluk) hedef eksiği üç koşuda da 1.180–1.248 kişi-saat ve *"yapısal,
çözücüden ve ağırlıktan bağımsız"*. Soru: bu açık gerçekten kaçınılmaz mı,
yani kurallar mı üretiyor?

## 2. Ne yapıldı

Motordan bağımsız küçük bir model (`taban.py`, CP-SAT): aynı 500 kişi, aynı
17 şablon, aynı talep tablosu (`fikstur/_sahne-S30-95.json`). Fazla mesai
**sıfıra** çivilenip hedef eksiği en aza indirildi. Kurallar basamak basamak
eklendi:

| Basamak | Modeldeki kurallar |
|---|---|
| 0 | günde tek vardiya · haftada en çok 6 gün · onaylı izin · departman çalışma saatleri · şablonun günleri · asgari kapsama (sert) · tam zamanlının sözleşme saatini doldurması (izin düşülerek) · yarı zamanlıya 45 saat tavanı · haftalık fazla mesai ≤ 10 saat |
| 1 | + uygunluk takvimi (tam gün "uygun değil") · "gece çalışamaz" işareti |
| 2 | + vardiyalar arası 11 saat dinlenme (ardışık günler) |
| 3 | + dört günlük pencerede en çok 3 gece (ardışık gece limiti) |

## 3. Sonuç

Bulut tarafındaki 2 çekirdekli makinede, 2 Ekim 2026:

| Basamak | Süre sınırı | En iyi bulunan açık (kişi-saat) | Kanıtlanan alt sınır | Fazla mesai |
|---|---|---|---|---|
| 0 | 60 sn (23 sn'de bitti) | 23 | 23 (kesin) | 0 |
| 1 | 50 sn | 106 | 74 | 0 |
| 2 | 50 sn | 115 | 73 | 0 |
| 3 | 160 sn | 80 | 74 | 0 |

Basamak 1 ve 2'nin 106 ve 115'i sürenin kısalığındandır (basamak 3, daha çok
kuralla ve daha uzun sürede 80 buldu).

**Okuma:** bu kurallar altında **80 kişi-saat açıklı ve sıfır fazla mesaili**
bir plan vardır. Motorun aynı gün ölçülen planları 1.180–1.248 kişi-saat açık
ve 228–511 saat fazla mesai taşıyor. Yani açığın büyük kısmı **bu kurallardan
gelmiyor**; bulgu 7'nin *"yapısal"* cümlesi bu kurallar için desteklenmiyor.

Aynı gün 1 Ekim'in kayıtlı planı (`olcum-plan-95.json`) hücre hücre döküldü:
900 kişi-saat hedefin altında, **3.903 kişi-saat hedefin üstünde** — açık saat
yetmediğinden değil, saatlerin yanlış yere yazılmasından.

## 4. Bu sonucun sınırı

- **Modelde olmayanlar:** ardışık hafta sonu limiti, gece postası devri, lider
  ve yetkinlik kapsaması, bütün mola kuralları ve saha tabanı, kilitler,
  yıllık fazla mesai tavanı, adalet dengesi, hedef aşımı cezası, saatlik
  uygunluk. Aradaki fark bunlardan birinden geliyor olabilir — **ölçülmedi**.
- Bu bir **alt sınır modeli**dir, ürünün testi değil: kural çıkarmak problemi
  kolaylaştırır. *"Şu kurallar sebep değil"* demeye yarar; *"motor 80'e
  inebilir"* demeye yaramaz.
- Tek kişinin yazdığı, sınanmamış kod; şartnameyle karşılaştırılmadı.

## 5. Nasıl çalıştırılır

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti\kesif\2026-10-02-hedef-tabani
py taban.py 3 eksik_fm0 160
```

İlk sayı basamak (0–3), ikinci amaç (`eksik_fm0`: fazla mesai sıfırken en az
açık · `eksik` · `fm` · `urun`: 9 × açık + 50 × fazla mesai dakikası), üçüncü
süre sınırı (saniye). Çekirdek sayısı betikte 2'ye sabit.
