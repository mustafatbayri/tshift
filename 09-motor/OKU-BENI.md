# 09-motor — Planlama motoru servisi

**Ne var:** Bağımsız doğrulayıcı (`/evaluate`) ve onu sunan küçük bir HTTP servisi.
**Ne yok:** Çözücü. Plan **üretilmiyor** — `/solve` ve `/suggest` bilerek 501 dönüyor.
**Yazıldı:** 16 Eylül 2026 · **Şartname:** `02-spec/v1.4-master-spec.md` §7.6, §11.4, §16.1

---

## 1. Neden önce doğrulayıcı, sonra çözücü

Altın senaryo testlerinin yedisi kırmızıydı. **İkisi** (A4, A8) plan üretmiyor,
var olan bir planı **denetliyor** — yani çözücü olmadan yeşile dönebilirler.
En küçük adım buydu ve döndüler.

Kalan beşi (A1, A3, A6, A7, A9) hâlâ kırmızı ve **doğru sebeple**: servis
ayakta, ama `/solve` ucu yok. Hata mesajı bunu ayırt ediyor — "motor çökmüş"
ile "çözücü henüz yazılmadı" aynı şey değil.

```
py -m pytest -q          (motor adresliyken)
→ 5 failed, 7 passed, 4 skipped
```

## 2. Bu doğrulayıcı çözücüyle mantık paylaşmaz

Şartname §7.6 ve §16.1 bunu şart koşuyor. Sebebi **D-6 sınıfı hata**: kodu
yazan testi de yazarsa aynı yanlış varsayım iki yere birden geçer ve hiçbir
test yakalamaz.

Bu yüzden `dogrulayici/kurallar.py` içindeki her kural **şartnameden okunarak
yeniden yazıldı**. Çözücü yazıldığında onun kısıt kodunu çağırmayacak, onunla
tek bir yardımcı fonksiyon bile paylaşmayacak. Kod bilerek "aptal" ve
doğrudan: her kural kendi sayımını kendi yapar, optimizasyon yok.

> ⚠ Çözücü yazılırken en kolay hata, "aynı hesabı iki kez yazmayalım" diyip
> ortak bir yardımcı modül çıkarmaktır. **Yapılmamalı.** Tekrar burada
> maliyet değil, güvencedir.

## 3. Çalıştırma

```powershell
cd C:\Users\PC\Desktop\Tshift\09-motor
py servis.py
```

Dışarıdan **hiçbir paket gerekmiyor** — yalnız Python standart kütüphanesi.
Kurulum adımı olmayan bir servis, "bende çalışmadı" ile geçen saatleri de
ortadan kaldırır. Yük altında koşacak sürüm için ASGI'ye taşınabilir;
sözleşme değişmez.

Testleri yeşile çevirmek için, **ayrı bir pencerede** servis açıkken:

```powershell
set TSHIFT_MOTOR_URL=http://localhost:8000
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\v5\testler
py -m pytest -v
```

Doğrulayıcının kendi testleri servis gerektirmez:

```powershell
cd C:\Users\PC\Desktop\Tshift\09-motor
py -m pytest testler -v
```

## 4. Dosyalar

| Dosya | Ne yapar |
|---|---|
| `servis.py` | HTTP ucları. `/health`, `/evaluate`; `/solve` ve `/suggest` → 501 |
| `dogrulayici/zaman.py` | Zaman modeli (Z-1…Z-6). Gece yarısını aşan vardiya aritmetiğinin **tek** kaynağı |
| `dogrulayici/kurallar.py` | Kural gövdeleri. Her biri ihlal listesi döndürür |
| `dogrulayici/denetle.py` | Orkestrasyon + metrikler + yayın kapısı |
| `testler/test_kurallar.py` | 26 birim testi. Her biri bir K-kararını sabitler |

## 5. Şu an hangi kurallar yazıldı

**14 kural.** Katalogdaki 35'in hepsi değil — şu an gereken alt küme.

| Bölüm | Yazılanlar |
|---|---|
| §6.1 Uygunluk | `AKTIF_CALISAN` · `SOZLESME_GECERLI` · `ONAYLI_IZIN` · `UYGUNLUK_TAKVIMI` |
| §6.2 Süre ve dinlenme | `GUNLUK_AZAMI` · `HAFTALIK_AZAMI` · `PART_TIME_LIMIT` · `CAKISMA_YOK` · `VARDIYA_ARASI_DINLENME` · `HAFTA_TATILI` · `ARDISIK_CALISMA_GUNU` · `MOLA_HAKKI` |
| §6.4 Kapsama | `ASGARI_KAPSAMA` · `HEDEF_KAPSAMA` · `MOLA_KAPSAMASI` |
| §6.6 Düzenleme | `KILIT_UYUMU` · `DONMUS_GUN` |
| §6.7 Fazla mesai | `FAZLA_MESAI_TAVANI` |

### Sessiz geçmeme ilkesi

Girdide **aktif ama gövdesi yazılmamış** bir kural varsa, cevap
`uygulanmayan_kurallar` listesinde bunu **açıkça** bildirir.

> *"İhlal bulamadım"* ile *"bakmadım"* aynı şey değildir. İkisini karıştıran
> bir doğrulayıcı, yeşil yanan ama hiçbir şey sınamayan testten daha
> tehlikelidir — çünkü planı temiz gösterir.

Şu an bilerek yazılmayan: **`ADALET_DENGESI`**. Şartname §6.5 kuralı
tanımlıyor ama **ihlal eşiğini tanımlamıyor** — dağılım ne kadar sapınca
ihlal sayılır? `SAAT_DENGESI`'nde eşik var (`tolerans_saat`, ±2),
`ADALET_DENGESI`'nde yok. Eşiği koda gömmek, ürün kararını gizlemek olurdu.
**T-12** olarak kaydedildi. Yumuşak bir kural olduğu için hiçbir planı yanlış
yere geçerli göstermiyor; yalnız puan hesabı eksik kalıyor.

## 6. İki kural bilerek ayrı — karıştırılırsa sessiz hata olur

| Kural | Molayı ne yapar | Türü |
|---|---|---|
| `ASGARI_KAPSAMA` | **Saymaya dahil eder** — "yeterli kişi planlandı mı" | SERT |
| `MOLA_KAPSAMASI` | **Düşer** — "o an sahada kaç kişi var" | YUMUŞAK (K-14) |

Üç kişinin üçü de 12:00'de moladaysa: `ASGARI_KAPSAMA` tamam (üçü de atanmış),
`MOLA_KAPSAMASI` ihlal (sahada kimse yok). İkisini karıştıran bir uygulama o
planı **geçersiz** yapardı; doğrusu puanını düşürmektir.

Bu ayrım `test_asgari_kapsama_molayi_SAYMAZ_yani_dusurmez` ile sabitlendi.

## 7. Kırmızı kanıt — testler gerçekten bir şey koruyor mu

Doğrulayıcı **yedi ayrı şekilde kasten bozuldu**, yedisi de yakalandı:

| # | Bozma | Sonuç |
|---|---|---|
| 1 | `GUNLUK_AZAMI` 11 → 9 (K-18 geri alınır) | ✅ yakalandı |
| 2 | `MOLA_HAKKI` brüt yerine net süreye bakar (K-4) | ✅ yakalandı |
| 3 | Tam 11 saat dinlenme de ihlal sayılır (K-11) | ✅ yakalandı |
| 4 | Örtüşmede ayrıca dinlenme ihlali yazılır (V-1) | ✅ yakalandı |
| 5 | Yayın kapısı `yasal`a bakar, `kabul_edilebilir`e değil (K-24) | ✅ yakalandı |
| 6 | Gövdesi olmayan kural sessizce geçilir | ✅ yakalandı |
| 7 | `ASGARI_KAPSAMA` molayı düşer | ✅ yakalandı |

Bunlar rastgele seçilmedi: her biri **sessizce bozulabilecek bir ürün
kararıdır** ve hiçbiri derleme hatası vermez.

## 8. Klasör adı hakkında — açık bir sorun

`07-motor/` klasöründe **motor yok**, müşteri Excel'ini okuyan analiz
betikleri var. Oradaki OKU-BENİ `08-analiz/` olarak yeniden adlandırılmasını
öneriyor, karar bekliyor.

⚠ **O ada geçilirse çakışma olur:** `08-analiz/` ile `08-motor-testleri/`
aynı numarayı paylaşır. Yeniden adlandırma kararı verilirken bu göz önüne
alınmalı — örneğin `10-analiz/`.

## 9. Sıradaki

**Çözücü (M-09).** Python + OR-Tools CP-SAT, ayrı servis. Kalan beş altın
senaryoyu (A1, A3, A6, A7, A9) yeşile çevirecek.

Çözücü yazılırken uyulacak tek zorunlu kural yukarıda, §2'de: **doğrulayıcıyla
hiçbir mantık paylaşmayacak.**

Paralelde: `ADALET_DENGESI` eşiği (T-12) ve A-16 hukuk teyidi.
