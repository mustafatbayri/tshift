# 8 Ekim 2026 — `VARDIYA_ROTASYON_YONU` keşfi: bugünkü motor kaç geri geçiş üretiyor?

**Soru.** Kural yazılmadan önce ürün yolunun planında art arda çalışma
günlerinde başlangıç saati **geriye kayan** geçiş ne sıklıkta, ne büyüklükte?
Literatür okuması ve tanım önerisi: `02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md`.

**Araç.** `geri_say.py [olcek] [saniye]` — `uret_veri_seti.sahne_uret(olcek, 0.95)`
sahnesini ürün yolu varsayılanlarıyla (2 işçi) çözer, kişi→gün→başlangıç
çıkarır, art arda çalışma günü çiftlerinde **dairesel fark** hesaplar (24
saatlik çemberde (−12, 12]; eksi = geri — sabah→gece atlaması böylece geri
sayılır, IARC 2020 madde 8). Sonuç `geri-<olcek>.json`.

**Sonuç (bulut, 2 çekirdek; küçük ölçek — sayılar yapıyı gösterir, kaliteyi değil).**

| Ölçek | Kişi | Art arda çift | İleri | Aynı | **Geri** | Geri büyüklükleri (saat: adet) |
|---|---|---|---|---|---|---|
| 0.1 (40 sn) | 49 | 132 | 33 | 81 | 18 (%14) | 1:1 · 2:1 · 2,75:7 · 3,25:4 · 4:2 · 8:1 · 9:2 — ort. 3,85 |
| 0.2 (60 sn) | 100 | 301 | 73 | 180 | 48 (%16) | 1:3 · 2,25:1 · 2,75:12 · 3:2 · 3,25:7 · 3,75:2 · 4:8 · 7:1 · 8:2 · 9:7 · 11:3 — ort. 4,7 |

En sık geri geçişler (0.2): 13:45→11:00 (12), 11:15→08:00 (7), 15:15→11:15 (6),
09:00→00:00 (6; dört saatlik sabahtan gece yarısı başlayan geceye — tam 11
saat dinlenme), 10:00→23:00 (3), 07:00→23:00 (2). Geri geçişlerin ~dörtte
biri sabah→gece atlaması; düz (dairesel olmayan) okumada bunlar "ileri"
görünürdü. 500 kişide ölçüm kural yazıldıktan sonra (önce/sonra, 900 sn × 3).
