# 10-veri-seti — TShift örnek veri seti

Çalışan verisi ve planın bütün girdisi, **şartname §8 tablolarında**
(kiracısız, M-16), gerçekçi bir çağrı merkezi örneğiyle. Sürümlü klasörler:
bir sürüm değişmez; yeni sürüm yeni klasördür.

| sürüm | tarih | ne |
|---|---|---|
| [`v1/`](v1/) | 14 Ekim 2026 | 500 + 49 kişi; JSON, JSON Schema, Excel import örneği, veri sözlüğü, dönüştürücü. **Dondu** — 14 Ekim gündüz ölçümlerinin (-VS1) girdisi; CI'da koşmaz |
| [`v2/`](v2/) | 14 Ekim 2026 (akşam) | v1 + iki alan: `employee_contracts.haftalik_saat` yarı zamanlıda zorunlu (**K-71** sözleşme süresi, 16/20/24/30 sa), `employee_teams.oncelik` eşit olabilir (**K-72** gezici; motor `birincil_ekip` türetir). İsimler ve öteki tablolar aynı. **Güncel**: merdiven/kalite ölçümü (-VS2) ve CI bunu kullanır |

Başlangıç noktası: **`v2/VERI-SOZLUGU.md`** (içindekiler, dosyalar, kararlar,
şartnameden farklar, açık sorular, kolon kolon tablolar).

Kural: bir sürüm değişmez. Alan ekleyen / anlam değiştiren her karar yeni
klasördür (v3…); eski sürümün referans ve ölçüm dosyaları (`08-motor-testleri/
gercekci-veri-seti/fikstur/_*-VS<n>-*`) o sürümün kaydı olarak durur.
