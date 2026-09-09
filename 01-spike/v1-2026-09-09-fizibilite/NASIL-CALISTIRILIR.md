# v1 — fizibilite testleri · nasıl çalıştırılır

7–8 Eylül 2026'da yapılan motor testlerinin son hâli.
Ne test edildiği ve ne çıktığı için bir üst klasördeki `README.md` dosyasına bakın.

---

## Gereksinimler

- Python 3.10+ (bu makinede 3.14.7 kurulu, komut `py`)
- OR-Tools: `py -m pip install ortools`

`cpsat.py` dışındaki her şey OR-Tools olmadan da çalışır.

---

## Komutlar

PowerShell'i bu klasörde açın.

```powershell
# 1) Test verisi üret (çağrı merkezi, 200 çalışan)
py uret.py

# 2) Basit yöntemle plan üret — 3 profil
py planla.py

# 3) Asıl motorla plan üret ve karşılaştır
py cpsat.py

# 4) Denetleyici gerçekten görüyor mu — sabotaj sınavı
py sinav.py

# 5) Ölçek testi (60 saniye bütçe, 2000 çalışan, deterministik)
py olcek.py 60 2000 --det

# 6) Otel senaryosu
py uret_otel.py
py cpsat.py --otel

# 7) Yönetici düzenlemesi sonrası öneri motoru
py oneri.py

# 8) Plan kararlılığı — bir kişi hastalanınca ne kadarı değişiyor
py yeniden_planla.py

# 9) Hafta ortası yeniden planlama (geçmiş günler dondurulmuş)
py hafta_ortasi.py

# 10) Talep modeli — Erlang C + simülasyon doğrulaması
py talep.py

# 11) 4 haftalık adalet / rotasyon testi
py cok_hafta.py

# 12) Kayıtlı planları yeniden çözmeden ölçüp karşılaştır
py karsilastir.py

# 13) Model kodlamasını OR-Tools olmadan doğrula
py cpsat_kontrol.py
```

---

## Dosyalar ne işe yarıyor

| Dosya | Görevi |
|---|---|
| `degerlendirici.py` | **Bağımsız denetleyici.** Planı kurallara göre denetler. Plan üreten hiçbir kodla mantık paylaşmaz — testlerin güvenilirliği buna dayanır. |
| `cpsat.py` | Asıl motor. Kısıt programlama (OR-Tools CP-SAT) ile plan üretir. |
| `planla.py` | Basit sezgisel planlayıcı. Karşılaştırma tabanı olarak duruyor. |
| `uret.py` / `uret_otel.py` | Sentetik test verisi üretir (çağrı merkezi / otel). |
| `sinav.py` | Sabotaj testleri + çözümsüzlük teşhisi. |
| `olcek.py` | Ölçek ölçümü. |
| `oneri.py` | Yönetici düzenlemesi sonrası aday öneri motoru. |
| `yeniden_planla.py` | Plan kararlılığı / değişim ölçümü. |
| `hafta_ortasi.py` | Hafta ortası yeniden planlama, donmuş günler. |
| `talep.py` | Erlang C talep modeli + kuyruk simülasyonu doğrulaması. |
| `cok_hafta.py` | Çok haftalı adalet ve rotasyon. |
| `karsilastir.py` | Kayıtlı planları yeniden çözmeden ölçer. |
| `cpsat_kontrol.py` | Sahte OR-Tools ile model kodlamasını doğrular. |
| `rapor.md` | 8 Eylül tarihli teknik rapor. |
| `girdi.json` / `girdi_otel.json` | Üretilmiş test verileri. |
| `uretilen-planlar/` | Testlerde üretilmiş plan çıktıları. |

**Not:** `girdi_500/1000/2000.json` gibi büyük ölçek dosyaları buraya kopyalanmadı;
`py olcek.py` komutu bunları kendisi üretiyor.
