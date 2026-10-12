# 12 Ekim 2026 gecesi — iki ölçüm: hedef aşımı kimden geliyor; rotasyonda gün tanımı

Bağlam: T-60 bulgu 28 eki ve bulgu 29; K-53 "yeniden açıldı"; K-65 B8 (D önerisi).
Oturum kaydı: `00-DEVIR/oturumlar/2026-10-11-konteyner-karari-ve-sira-3-durumu.md` §7.

| dosya | ne |
|---|---|
| `olc.py` | Kaydedilmiş planlardan (K-66) iki sayım: (1) `HEDEF_ASIMI` hücrelerindeki kişi-saat sözleşme tipine göre (tam zamanlı batık / saat ücretli), (2) rotasyon gün tanımı — bugünkü (başlangıç günü) / C (K-46 çoğunluk) / D (dokunulan günler) ile sayılan geri çiftler. Kullanım: `py olc.py ..\..\planlar\kalite-olcumu-95-rotasyon-once-900\varsayilan-1.json …` |
| `sonuc-once-planlari.txt` | `olc.py`'nin üç "önce" planındaki çıktısı (12 Ekim 04:45, bulut) |
| `sonuc-sonra-planlari.txt` | `olc.py`'nin altı "sonra" planındaki çıktısı (12 Ekim 05:55, bulut): D ile kalan geri geçişlerin yarısı B8; aşım dağılımı öncekiyle aynı |
| `asim_profili.py` | Aşım **nerede**: hücre başına (atanan − hedef) dağılımı, en büyük hücreler ve oradaki şablonlar, ekip × saat ortalama aşım. `py asim_profili.py <plan.json> …` |
| `sonuc-asim-profili.txt` | Sonra ve önce planlarında profil (12 Ekim 14:50): SATIS 14:00–16:00 hedef 122 / atanan 186 (+64); gündüz şablonlarının beşi de 13:45–16:15'i kapsıyor → K-67 ve K-62 seviye 1 |
| `sert_deneme.py` | Sert mutlak `HEDEF_ASIMI` sondası: `ha_*` değişkenleri 0'a sabitlenince model çözülebilir mi (amaçsız olabilirlik). `py sert_deneme.py 0.1 120` |
| `sonuc-sert-mutlak-0.1.txt` | 0,1 ölçek: bugünkü OPTIMAL 11 sn; `ha_* = 0` **INFEASIBLE 1,8 sn** |
| `sert_deneme2.py` | Çatışma hangi kuralda: `ha_* = 0` + sırayla `SAAT_DENGESI`, `+ROL/YETKINLIK`, `+ASGARI_KAPSAMA` kaldırılınca |
| `sonuc-sert-hangi-kural-0.1.txt` | Yalnız `ASGARI_KAPSAMA` da kaldırılınca çözülüyor → geometri (örtüşen bloklu şablonlar + asgari) |

⚠ Bulut makinesi (2 çekirdek, ortools 9.15), 0,1 ölçek: olabilirlik sonucu
(INFEASIBLE) ölçekten bağımsız bir kanıt; süreler Mustafa'nın makinesi için
tahmin değildir. Sayımlar tam ölçekli (500 kişi) planlardan.
