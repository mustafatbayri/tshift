# Onay durumu — A1–A12 (15 Eylül 2026 turu) · **KAPANDI**

**Bu tur bitti.** On iki senaryonun tamamı ve altı varsayımın tamamı onaylandı.
Buradaki ekler `v5/KABUL-OLCUTLERI.md`'ye işlendi ve v4 donduruldu.

Dosya, kendi kuralına göre (*"tur bitince sıfırlanır"*) sıfırlandı; aşağıda
turun **özeti** kaldı. Bir sonraki onay turu bu dosyayı baştan doldurur.

---

## Turun sonucu

| Ne | Sonuç |
|---|---|
| Senaryolar | **12/12 onaylandı.** A5 ertelendi (K-12), altyapısı korunuyor |
| Varsayımlar | **6/6 karara bağlandı** (V-1…V-6) |
| Turda doğan karar | **On tane:** K-8 … K-17 |
| Geri alınan karar | **K-1** — yanlış sorulmuş bir soruya verilmiş doğru cevaptı |
| Baştan yazılan senaryo | **A2, A3, A7, A8** ve §3'teki sahne |

## Turda ortaya çıkan iki şartname eksiği

1. **`leaves` tablosunda durum alanı yok** (K-9) — izin iptali modellenemiyordu.
2. **§6 kataloğunda `yasal` sütunu yok** (K-16, K-17) — ihlal kabulü ve yayın
   kapısı bu bayrağa dayanıyor; olmadan ikisi de uygulanamaz.

İkisi de senaryolar yazılırken çıktı, şartname okunurken değil. Kabul ölçütü
yazmanın şartnameyi denetlemek gibi bir yan faydası olduğu bu turda görüldü.

## Uzman gözü bekleyen iki madde — fikstürleri bloke etmiyor

| # | Ne | Neden |
|---|---|---|
| 1 | Mola hakkı eşiğinin **brüt** süreye uygulanması (K-4) | Hukuki yorum. Hata yönü tek taraflı (kanunun istediğinden az mola vermez) ama yine de hukukçu bakmalı |
| 2 | Hangi kuralların `yasal = true` olduğu (K-17) | Claude'un sınıflandırması. Belirsizler güvenli tarafta (kabul edilemez) duruyor |

Sahaya çıkmadan önce ikisi de teyit edilmeli. Şu an `[çıkarım]` etiketini
koruyorlar.

## Sıradaki adım

> **Fikstürler:** `v5/fikstur/A01.json … A12.json` (A5 hariç, 11 dosya).
> Sonra pytest iskeleti (A1–A9) ve xUnit testleri (A10–A12). Motor olmadığı
> için hepsi **kırmızı** başlar — istenen durum bu.
