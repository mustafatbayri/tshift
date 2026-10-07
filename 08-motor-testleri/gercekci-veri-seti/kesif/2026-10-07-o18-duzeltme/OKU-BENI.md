# 7 Ekim 2026 — O-18 düzeltmesinin kanıt klasörü (keşif, bulut; ürün ölçümü DEĞİL)

**Ne bu.** 6 Ekim gecesi yazılan *"önce fazla mesaisiz"* kodu (K-61'in 00:45
sürümü) bağımsız incelemede Mustafa'nın ilkesini çiğniyordu (O-18). Düzeltme
02:35–03:05'te bulutta yazıldı, 03:05'te kredi kesintisiyle silindi, 03:25'ten
sonra oturum kaydındaki adımlardan yeniden uygulandı ve yeniden doğrulandı.
Bu klasör o gecenin **kanıtlarını** saklar — kayıtlardaki sayıların kaynağı.
Hepsi bulut makinesinde (2 çekirdek) üretildi; **Mustafa'nın makinesi ve 500
kişi için tahmin değildir** (bkz. `../OKU-BENI.md` kuralı).

## İçindekiler

1. [Dosyalar](#1-dosyalar)
2. [Nasıl koşturulur](#2-nasıl-koşturulur)
3. [Sayıların kaynağı](#3-sayıların-kaynağı)
4. [Kaybolanlar](#4-kaybolanlar)

## 1. Dosyalar

| Dosya | Ne |
|---|---|
| `dogrula.py` | Beş karşı örnek sahnesi (tek kişi DENGELI / KAPSAMA, 12 kişi 3 saat, iki ekibe üye kişi ×2), üç yol: TAM (kanıtlı optimum) / URUN (ürün yolu) / SERT (sert kesim ölçüm seçeneği). Motor yolu `MOTOR` ortam değişkeniyle |
| `olc3.py` | 49 kişilik gerçekçi sahnede üç yol kıyası (`kapali` 6 Ekim öncesi / `sert` / `yeni`); iyileştirme boyunca fazla mesai izi |
| `loglar/zincir.log` | 04:00: 583 motor testi, 39 gerçekçi set testi, v5 (servis yok), mutasyon grupları — `fm_sifir` 43'ün 1'i yaşadı (eşdeğer mutant) |
| `loglar/fm_sifir2.log` | 04:14: düzeltilmiş `fm_sifir` 44/44 |
| `loglar/son.log` | 04:52: 587 motor testi, 26 ölçüm aracı testi, `fm_sifir` 48/48, `ilk_asama` 6/6 |
| `loglar/duman-49.jsonl` | 49 kişi, 20 sn, ikişer koşu — sert ve yeni yol `sure_yetmedi` (bulgu 24) |
| `loglar/duman-49-30sn.jsonl` | 49 kişi, 30 sn, ikişer koşu — kapalı 15.478 / 15.469, sert 2.717 / 2.719, yeni 2.722 / 2.689 |
| `inceleme/ilk-inceleme-ajan-*-{istem,rapor}.md` | 00:57'de başlatılıp 02:09'da dönen iki incelemenin istemleri ve raporları (00:45 sürümünü bulan). Betik ve logları kesintide silindi; raporlar oturum kaydından kurtarıldı |
| `inceleme/ajan-a/` | 04:10–04:45 motor incelemesi: `RAPOR.md`, `av.py` (640 sahnelik karşı örnek avı; `av-*.log` özetleri, `hedef-sinif-ozet.json`), `mut.py` + `mut.log` (14 mutant elle), `dogrula.log` |
| `inceleme/ajan-b/` | 04:10–04:45 kayıt incelemesi: `RAPOR.md`, `dogrula-cikti.log`, `ipucu_deneyi.py` (CP-SAT ipucu mikro deneyi) |
| `yeniden-uygulama/*.sh` | Oturum kaydından çıkarılan 20 düzenleme adımı (sırayla 1642 → 1738); her biri tek ve belirli metin değişimi (`assert count == 1`). Yollar bulut çalışma alanına göre; belge niteliğinde |

## 2. Nasıl koşturulur

```
cd 08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme
set MOTOR=..\..\..\..\09-motor
py dogrula.py                       # ~1 dk, 15 çözüm
py olc3.py ..\..\..\.. 0.1 0.95 30 2 duman.jsonl   # 49 kişi, 30 sn, ikişer
```

## 3. Sayıların kaynağı

Kayıtlardaki (K-61, O-18, T-60 bulgu 23–24, oturum günlüğü §15–16) her sayı
yukarıdaki dosyalardan okunur. İstisnalar — logu olmayanlar: 02:50'deki 20 sn
tek koşu (2.713 / 2.758 / 11.918) yalnız oturum kaydındaki koşu çıktısında;
ilk incelemenin avı (8/400, 0/1.200) ve ×400 sahnesi (300.000 / 902.400)
yalnız ilk inceleme raporunda.

## 4. Kaybolanlar

03:05 kesintisinde bulut alanı silindi: düzeltme dosyaları (yeniden
uygulandı), ilk incelemenin betikleri ve logları (`repro_min.py`,
`b3_s3_cesitleri.py`, `log_*.txt` — `dogrula.py` aynı sahneleri taşır),
02:50 koşusunun logu. Sayı eşitliği var, dosya eşitliği (md5) kanıtlanamaz.
