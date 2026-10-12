# 11 Ekim 2026 — Bağımsız inceleme 4: `VARDIYA_ROTASYON_YONU` (K-65)

**Ne incelendi.** K-65 ile yazılan rotasyon yönü kuralı: motor amaç terimi
(`model.py _rotasyon`), metrik (`coz.py _rotasyon_metrigi`), doğrulayıcı
(`kurallar.py vardiya_rotasyon_yonu`), K-54 işareti, testler, mutasyon
listesi (yalnız okundu), şartname §6.3 / §11.3 / değişiklik 65. İnceleyen,
kodu yazan oturum değil; görev karşı örnek avıydı. Ürün koduna dokunulmadı
(md5'ler raporun başında ve sonunda).

**Dosyalar.** `RAPOR.md` (bulgular B1–B9; karar: *koda inmeye hazır,
bloklayıcı yok*; düzeltilmeli: B1 K-54 not metni/şartname cümlesi, B5 test
boşlukları + mutasyon listesi ekleri; not: B2 donmuş iki satır, B3 pasif kişi,
B4 plansız donmuş gün işareti, B6 "~54 bin" metni, B7 tam 12 asimetrisi, B8
başlangıç günü / `bas ≥ 24` görüşü), `deneme/` (betikler `ortak.py`,
`d1…d5` ve çıktıları `*.out` / `*.json`; depo köküne göre çalışır).

**Sayılar.** 1.100 rastgele sahne (1.078 çözüldü, hepsi optimum) + 40
hedefli sahne: metrik ≡ doğrulayıcı ≡ bağımsız sayım (0 fark); amaç terimi ≡
yuvarlanmış satır toplamı (4 fark, hepsi K-54 "şablona oturmayan satır"
sınıfı). Kurulum: 0.1 ölçekte +3.570 kısıt (+%4,7), 0.2'de +7.476 (+%4,9);
süre farkı gürültü içinde. 19 ek mutantın 13'ü test dosyasını geçiyor
(başta tam ,5 yuvarlama).

**Tekrar üretme.** `cd deneme && python3 d1_tanim.py && python3
d2_rastgele.py 400 11 0.4 d2_rastgele.json && python3 d2_rastgele.py 400 23
0.9 d2_rastgele_b.json && python3 d2b_sabit.py 300 5 && python3 d3_sinir.py
&& python3 d4_kurulum.py 40 && python3 d5_mutasyon.py` (toplam ~3 dk; d5
geçici kopya kurar ve siler). 1.0 ölçek bulutta kurulmadı.
