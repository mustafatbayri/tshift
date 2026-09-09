# Spec dokümanları

Yazılım ekibinin okuyacağı asıl kaynak. Bir yazılımcı bu klasörü okuyup soru
sormadan geliştirmeye başlayabilmeli.

## Versiyonlar

| Versiyon | Tarih | Durum | Not |
|---|---|---|---|
| `v1.1-master-spec.md` | 9 Eylül 2026 | **Yürürlükte** | 16 bölüm, 44 tablo, 25 ekran, 27 kural |
| `v1.0-master-spec.md` | 9 Eylül 2026 | Geçersiz | İlk tam spec |

PDF sürümü aynı klasörde: `TShift-Master-Spec-v1.1.pdf` (63 sayfa, paylaşmak için).

## v1.1'de ne değişti

1. Kimlik katmanı kendi kodumuzda — Keycloak çıktı, 6 yeni tablo, 13 yeni uç
2. Metrik açıklama bileşeni + `metric_definitions` tablosu
3. Uygulanan önerilerde geri alma
4. İçe aktarmadan yapay zekâ kaldırıldı — mevcut araç kullanılacak
5. **İzin etki analizi** — yeni özellik
6. Seçilmeyen plan adayları için saklama politikası (30 gün)
7. Departman / Şube isimlendirmesi
8. Arayüz yaklaşımı: Tailwind + shadcn/ui + TanStack Table
9. Plan revizyon karşılaştırması kapsamdan çıktı

Tam liste dokümanın 16. bölümünde.

## Versiyonlama kuralı

Bu dosyalar **değiştirilmez.** Bir şey değişecekse yeni sürüm açılır:
`v1.2-master-spec.md`. Değişiklik dokümanın "Sürüm notları" bölümüne ve kökteki
`DEGISIM-GUNLUGU.md` dosyasına yazılır.

## Bir sonraki sürümü tetikleyecek şeyler

- Demo v2'de alınan UI kararları
- Mevcut içe aktarma aracının sözleşmesi
- Gölge pilot verisi geldiğinde çıkacak gerçeklik düzeltmeleri
