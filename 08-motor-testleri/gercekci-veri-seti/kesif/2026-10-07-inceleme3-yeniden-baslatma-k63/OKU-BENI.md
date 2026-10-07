# 7 Ekim 2026 — Bağımsız inceleme 3: yeniden başlatma (bulgu 25) + K-63

**Ne incelendi.** `fazla_mesaisiz_deneme` (fazla mesaisiz ilk aramanın
3 × 40 sn yeniden başlatılması; varsayılan 1) ve K-63 (mola adımı
yetişmezse ikinci aşamanın planı döner) — kod, testler, mutasyonlar, ölçüm
araçları. İnceleyen, kodu yazan oturum değil; görev karşı örnek avıydı.

**Dosyalar.** `RAPOR.md` (bulgular B1–B12, karar: *koda inmeye hazır,
bloklayıcı yok*; düzeltilmeli: B6 gevşek amaç, B7 not metni; süreç: B1),
`deneme/` (deney betikleri `d1…d8` ve çıktıları `*.out`; `ortak.py` depo
köküne göre çalışır — inceleme sırasında dondurulmuş bir kopyaya bakıyordu),
`*.diff` (incelenen değişiklik, committed `01e5e29`'a göre),
`mutasyon-*-ilk-kosu.txt` (B6/B7 düzeltmesinden ÖNCEKİ grup koşuları: k63
16/16, fm_sifir 59'un 58'i öldü + 1 çapa atlandı — sonradan düzeltildi).

**Ne değişti (inceleme sonrası, aynı akşam).** B6: `_ipucu_planini_al`
artık bütün değişkenleri değil **karar değişkenlerini** (x, mola, dinlenme)
ipucuya sabitler, cezaları amaç sıkar → `amac_degeri` sıkı. B7: not plan
kaynağını söyler (`ipucu_plani.kaynak`). B4: tek denemede 1 sn tabanı yok.
B10: üç yeni test (not sınırı, çevirme süresi bütçe dışı, uçtan uca 3 deneme
bütçe) + mutasyonlar. B12'nin iki bitişik bulgusu T-60 bulgu 26–27 olarak
kayda geçti (karar Mustafa'da / sırada). B1 süreç dersi oturum kaydında.

**Tekrar üretme.** `RAPOR.md` §3'teki komutlar; `deneme/ortak.py` depo
köküne göre yol kurar, dışarıdan kopya gerekmez. 500 kişilik koşu yok; 0.1–0.2
ölçek (`uret_veri_seti.sahne_uret`).
