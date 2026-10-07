# 7 Ekim 2026 (gündüz) — gece koşusunun okunması; bulgu 25: fazla mesaisiz ilk aramanın kuyruğu

**Pencere:** 7 Ekim 17:28 – · **Önceki:** `2026-10-06-uc-profil-ve-fazla-mesai-artigi.md`
§15–17 (O-18 düzeltmesi, kredi kesintisi, bulgu 23–24, K-63/K-64). **Bu
pencerede kod değişmedi.**

## İçindekiler

1. [Gece koşusunun sonucu](#1--gece-koşusunun-sonucu)
2. [Bulgu 25 — fazla mesaisiz ilk aramanın kuyruğu](#2--bulgu-25--fazla-mesaisiz-ilk-aramanın-kuyruğu)
3. [Kuyruk ölçümü aracı ve karar kuralı](#3--kuyruk-ölçümü-aracı-ve-karar-kuralı)
4. [Sıradaki](#4--sıradaki)
5. [Kuyruk ölçümünün sonucu (18:00)](#5--kuyruk-ölçümünün-sonucu-1800)

## 1 · Gece koşusunun sonucu

Mustafa 07:40'ta kapanış commit'ini ve gece koşusunu başlattı; 17:28'de
çıktıyı attı (`kalite-olcumu-95-fmsert-kapsama-900.json`,
`kalite-olcumu-95-fmonce-1200.json`). Karar kuralları koşudan önce T-60'a
yazılmıştı; okuma oraya göre:

| Koşu | Sonuç | Okuma |
|---|---|---|
| `fm_sert_kapsama` 900 × 3 | 13.638 · 13.983 · 13.623; fazla mesai 0 | bulgu 21 (13.834–13.914) ±%2'de → taban aynı, sert kesim seçeneği bugünkü kodda bulgu 21'i yeniden üretiyor |
| `fm_once_kapsama` 1200 × 3 | 14.041 · 13.773 · 14.418; fazla mesai 0 | bulgu 21 ort.'a göre +1,3 · −0,7 · +4,0 (**+%1,5**); 900 sn'de +%5,2 idi → farkın büyük kısmı **bütçe**; yayılım %4,7 kalıyor |
| `fm_once` (DENGELI) 1200 × 3 | 26.602 · 26.823 · **116.976** | ilk ikisi 900 sn ile aynı düzey (fazla süre kazandırmıyor); üçüncüsü **bulgu 25** |

Hibrit hâlâ aday (dar yayılım için) ama önceliği düştü; K-63'ün 20 dk üst
ucu KAPSAMA'yı tek başına sert düzeyine getiriyor.

## 2 · Bulgu 25 — fazla mesaisiz ilk aramanın kuyruğu

Üçüncü DENGELI koşusunda birinci aşamanın fazla mesaisiz uygunluk araması
120 sn'lik payını doldurdu, plan bulamadı (süre yetmedi; imkânsızlık kanıtı
değil). Motor tasarlandığı gibi davrandı: alanları açtı, serbest arama hemen
plan buldu (amaçsız 2.688.191), iyileştirme 845 sn'de 132.551'e indi (sabit
molalı sınırı 41.662'nin 3,2 katı), mola adımı 116.976 — **30 saat fazla
mesai, 24 kişi**; fazla mesai dışı kalemler ötekilerle aynı. Çıktı notu düştü,
ölçüm satırı gösterdi. Bu, bulgu 20'nin artığının ta kendisi.

Dağılım (6 Ekim'den beri bu aramanın süresi, 18 koşu): 8,6 · 8,8 · 8,8 · 8,8 ·
8,9 · 9,0 · 9,0 · 9,1 · 9,3 · 9,5 · 9,5 · 9,5 · 9,8 · 10,0 · 12,2 · 12,7 · 21,1
sn ve **1 × > 120 sn**. Tek olay, ama ürün yolunun kalitesi bu aramaya bağlı:
**K-61 kuyruk kapanmadan "kapandı" denmez.** 1200 sn bütçe payı
büyütmüyor (`_ilk_asama_payi` = min(120, %20)).

## 3 · Kuyruk ölçümü aracı ve karar kuralı

`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-fm-siz-arama-kuyrugu/kuyruk.py` (+ OKU-BENI): 500 kişilik modeli bir kez kurar,
birinci aşamayı motorun kendi yardımcılarıyla aynen hazırlar (amaç silinir,
`_molalari_sabitle`, `_fazla_mesaiyi_sifirla`), aynı modeli 30 tohum + 5 ×
tohum 0 ile 120 sn tavanla çözer; süre dağılımı, P(T > 20/40/60/120) ve
yeniden başlatma politikalarının (2 × 60, 3 × 40, 4 × 30) offline tahmini.
Bulutta 49 kişiyle uçtan uca denendi (hazırlık ve döngü çalışıyor; sayılar
anlamsız). Karar kuralı koşudan önce OKU-BENI'ye yazıldı: kuyruk gerçekse
yeniden başlatma motorda ölçüm seçeneği → 900 sn × 3 → varsayılan; değilse
yine yazılır (ucuz sigorta), öncelik hibrite döner.

## 4 · Sıradaki

(1) `kuyruk.py` koşusu (Mustafa, ~15–25 dk) → politika; (2) K-63 (süre
aralığı; mola adımı yetişmezse plan) ve K-64 kod; (3) hibrit KAPSAMA; (4)
K-62 merdiven kadrosu (20 satışçı BO, gece BO ≥ 2).

## 5 · Kuyruk ölçümünün sonucu (18:00)

Mustafa `kuyruk.py --deneme 30 --tavan 120 --sifir-tekrar 5` koşturdu (kurma
53 sn; 633.591 değişken; 529.480 mola adayı kapalı; 359 fazla mesai değişkeni
[0,0]; 6 işçi). **35 denemenin hepsi buldu**; medyan 7,5 sn, %90 13,0 sn, en
uzun 61,9 sn; P(T > 10/20/40/60/120) = 9/35 · 2/35 · 2/35 · 1/35 · 0/35. Tohum
0'ın beş tekrarı 13,0 · 55,9 · 12,2 · 7,9 · 7,8 sn — rastgelelik tohumdan
değil, paralel işçilerin zamanlamasından (aynı tohumda 7× fark).

Karar kuralı (OKU-BENI, koşudan önce): P(T > 120) ≈ 0 ve %90 < 40 sn → ilk
dal. Toplamda (6 Ekim'den beri 18 ürün/sert koşusu + 35 deneme = 53 gözlem)
1 × > 120 sn, 2 × 56–62 sn, 1 × 21 sn. Kuyruk ince ama gerçek; tek denemeyle
120 sn'de kalma ~%2 ve bedeli 30 saat fazla mesaili plan. Çare ucuz: **120
sn'lik payı 3 × 40 sn'lik denemeye bölmek**, her deneme farklı tohumla
(offline tahmin: başarısızlık 0,057³ ≈ %0,02; bağımsızlık varsayımı, motorda
doğrulanacak). Tipik koşu (7,5 sn) etkilenmez. Çıktıya denemelerin
süresi/durumu eklenir.

**Plan:** motorda ölçüm seçeneği `fazla_mesaisiz_deneme` (varsayılan 1 =
bugünkü davranış; ölçümde 3) + testler + mutasyonlar → `fm_once` 900 sn × 3 →
varsayılan 3 → K-61 kapanır. Sırası Mustafa'nın sıralama cevabına göre
(18:03'te sorulan: kalibrasyonları dondurma; dört kural + veri seti).
