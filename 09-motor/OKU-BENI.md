# 09-motor — Planlama motoru servisi

**Ne var:** Bağımsız doğrulayıcı (`/evaluate`), çözücü (`/solve`) ve §11.7
onarım döngüsü. **Çekirdek çalışıyor — "tamamlandı" değil:** kataloğun 35
kuralının 19'u yazılı, `/suggest` yok, ve **iki 🔴 açık bulgu var**
(T-18 yayın kapısı · T-19 talep biçimi — `00-DEVIR/06-ACIK-RISKLER.md`).
**Ne yok:** Öneri üretimi — `/suggest` bilerek 501 dönüyor.
**Yazıldı:** 16 Eylül 2026 · **Şartname:** `02-spec/v1.4-master-spec.md`
§7.6, §11.2, §11.3, §11.4, §11.7, §16.1

```
py -m pytest testler -q                        →  72 passed
py -m pytest -q   (08-motor-testleri/v5, motor ayakta)  →  12 passed, 4 skipped
```

---

## 1. Üç parça, üçü ayrı durur

| Parça | Ne yapar | Ne yapmaz |
|---|---|---|
| `09-motor/dogrulayici/` | Var olan planı kurallara karşı denetler | Plan **üretmez** |
| `09-motor/cozucu/` | CP-SAT ile plan üretir | Kendi ürettiğini **denetlemez** |
| `09-motor/orkestra.py` | İkisini üstten çağırır, onarım döngüsünü koşar | Kural **bilmez** |

Bu ayrım şartnamenin §7.6 ve §16.1 maddeleridir ve projedeki **en kolay
bozulacak** kuraldır. Somut hâli:

> `cozucu/` ile `dogrulayici/` birbirini **import etmez.**
> `orkestra.py` ikisini de import eder — ve bu doğrudur.

`orkestra.py` bir istisna değil; §11.7'nin tarif ettiği mimarinin ta kendisi:
*"Motor plan üretir, doğrulayıcı denetler."* Yasak olan, **ikisinin birbirini
çağırmasıdır**.

Bunu artık yorum değil bir test koruyor:
`09-motor/testler/test_bagimsizlik.py` — dosyaların import ağacına bakar ve
üçüncü bir ortak yerel modül çıkarılmasını da yakalar.

### Neden bu kadar üstünde duruluyor — D-6

Kodu yazan testi de yazarsa, aynı yanlış varsayım iki yere birden geçer ve
hiçbir test yakalamaz. Doğrulayıcı ancak çözücüden **bağımsızsa** onu
denetleyebilir.

Bu yüzden zaman aritmetiği iki kez, **bilerek farklı** yazıldı: doğrulayıcı
mutlak saat aralıklarıyla, çözücü saat dilimi (slot) tabanlı. Aynı sonuca iki
ayrı yoldan varmaları, ikisinin birden yanlış olma ihtimalini düşürür.

> ⚠ En kolay hata: *"aynı hesabı iki kez yazmayalım"* deyip ortak bir yardımcı
> modül çıkarmak. **Yapılmamalı.** Tekrar burada maliyet değil, güvencedir.

## 2. Çalıştırma

```powershell
cd C:\Users\PC\Desktop\Tshift\09-motor
py servis.py
```

Doğrulayıcı ve servis **hiçbir dış paket gerektirmiyor** — yalnız Python
standart kütüphanesi. Çözücü OR-Tools, testler pytest istiyor:

```powershell
py -m pip install -r requirements.txt
```

`09-motor/requirements.txt` sürümleri **sabitliyor** (O-8 gerekçesi: serbest
bırakılan sürümler CI ile yerel makineyi sessizce ayırıyor). Doğrulayıcının
dış bağımlılığı yok ve bu bilerek korunuyor — o dosyaya eklenen her paket
yalnız çözücüyü ya da testleri ilgilendirmeli.

Testleri koşturmak için, **ayrı bir pencerede** servis açıkken:

```powershell
$env:TSHIFT_MOTOR_URL = "http://localhost:8000"
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\v5
py -m pytest -v
```

Motorun kendi testleri servis gerektirmez:

```powershell
cd C:\Users\PC\Desktop\Tshift\09-motor
py -m pytest testler -v
```

## 3. Dosyalar

| Dosya | Ne yapar |
|---|---|
| `09-motor/servis.py` | HTTP ucları. `/health`, `/evaluate`, `/solve`; `/suggest` → 501 |
| `09-motor/orkestra.py` | §11.7 onarım döngüsü: üret → bağımsız denetle → en fazla 2 onarım |
| `09-motor/dogrulayici/zaman.py` | Zaman modeli (Z-1…Z-6), doğrulayıcı tarafı |
| `09-motor/dogrulayici/kurallar.py` | **19** kural gövdesi. Her biri ihlal listesi döndürür |
| `09-motor/dogrulayici/denetle.py` | Denetim + metrikler + yayın kapısı |
| `09-motor/cozucu/model.py` | CP-SAT modeli, ağırlık tablosu (§5.4), zaman aritmetiğinin **ikinci** yazımı |
| `09-motor/cozucu/coz.py` | `/solve` gövdesi, K-28 erken durma |
| `09-motor/cozucu/teshis.py` | Çözümsüzlük teşhisi (§11.3) + K-10 en iyi plan |
| `09-motor/testler/test_kurallar.py` | **48** birim testi. Her biri bir K-kararını sabitler. Sekizi T-27'nin bekçisi: mola vardiyaya kırpılır, gece yarısını aşanda kaydırılır, üst üste binenler birleşir |
| `09-motor/testler/test_profiller.py` | **20** birim testi. Plan profilleri, adalet gradyanı, onarım döngüsü, fazla mesai (K-30). Dördü T-22'nin bekçisi: çözümsüzlükte sunulan taslak da denetlenir |
| `09-motor/testler/test_bagimsizlik.py` | 4 birim testi. §7.6 bağımsızlığını korur |
| `09-motor/requirements.txt` | Sabitlenmiş bağımlılıklar. Doğrulayıcı hiçbirini kullanmaz |

### CI 🆕 *(16 Eylül)*

`.github/workflows/testler.yml` içinde **`motor`** adlı ayrı bir iş var:
birim testleri → servisi başlat → altın senaryolar → fikstür denetleyicisi.
Docker gerektirmiyor, Python 3.14'e sabitli.

Kapının kendi kırmızı kanıtı yapıldı: adres verilmezse `exit=1`, servis
kapalıysa `exit=1`, sağlık beklemesi 20 sn'de cevap alamazsa adım durur.

**İlk koşu yeşil** (16 Eylül, `47c7050`). Çıkan Node 20 uyarısı aynı gün
kapatıldı (T-17): checkout v7, setup-python v7, setup-dotnet v6.

## 4. Şu an hangi kurallar yazıldı

**19 kural.** Katalogdaki 35'in hepsi değil — şu an gereken alt küme.

> ⚠ 16 Eylül'e kadar burada **17** yazıyordu; aşağıdaki tablo ise 19 satır
> listeliyordu. Başlık kendi tablosuyla çelişiyordu ve `DENETIM.py` bunu
> yakalayamaz — betik *tutarlılığa* bakar, *doğruluğa* değil. Dış inceleme
> buldu.

| Bölüm | Yazılanlar |
|---|---|
| §6.1 Uygunluk | `AKTIF_CALISAN` · `SOZLESME_GECERLI` · `ONAYLI_IZIN` · `UYGUNLUK_TAKVIMI` |
| §6.2 Süre ve dinlenme | `GUNLUK_AZAMI` · `HAFTALIK_AZAMI` · `PART_TIME_LIMIT` · `CAKISMA_YOK` · `VARDIYA_ARASI_DINLENME` · `HAFTA_TATILI` · `ARDISIK_CALISMA_GUNU` · `MOLA_HAKKI` |
| §6.4 Kapsama | `ASGARI_KAPSAMA` · `HEDEF_KAPSAMA` · `MOLA_KAPSAMASI` |
| §6.5 Adalet | `ADALET_DENGESI` (K-27 eşiği geldi) |
| §6.6 Düzenleme | `KILIT_UYUMU` · `DONMUS_GUN` |
| §6.7 Fazla mesai | `FAZLA_MESAI_TAVANI` |

### Sessiz geçmeme ilkesi

Girdide **aktif ama gövdesi yazılmamış** bir kural varsa, cevap
`uygulanmayan_kurallar` listesinde bunu **açıkça** bildirir. Bir kuralın
gövdesi var ama bir **boyutu** yazılmamışsa, o da `eksik_boyutlar`'da görünür
(`ADALET_DENGESI`'nin `saat` boyutu — T-13).

> *"İhlal bulamadım"* ile *"bakmadım"* aynı şey değildir. İkisini karıştıran
> bir doğrulayıcı, yeşil yanan ama hiçbir şey sınamayan testten daha
> tehlikelidir — çünkü planı temiz gösterir.

## 5. Plan profilleri — §5.4 artık gerçekten çalışıyor

Aynı kural seti, farklı ağırlıklarla üç farklı plan üretir: `DENGELI`,
`KAPSAMA`, `CALISAN`. Ağırlık okuma sırası:

1. İsteğin `agirliklar` alanı — kiracının düzenlediği `plan_profiles`
2. §5.4 tablosu, istekteki `profil` sütunundan
3. Kural kataloğundaki `agirlik`

Tanınmayan profil adı `DENGELI`'ye düşer **ama sessizce değil** — çıktıdaki
`uygulanmayan_notlar` bildirir. Sessizce düşmek, kullanıcının *"çalışan odaklı
plan istedim"* deyip dengeli plan alması ve bunu hiç öğrenmemesi demektir.

### Adalet: eşik **ihlali sayar**, gradyan **planı seçer** (K-29)

K-27 eşiği (ortalamadan 2 fazla) yalnız **doğrulayıcıda** duruyor. Motorda
onun yerine **artan marjinal maliyet** var: üçüncü cumartesi ikinciden, ikinci
birinciden pahalıdır.

Sebebi ölçüldü: eşik tek başınayken eşiğin altındaki bütün dağılımlar sıfır
ceza alıyordu, yani ağırlığı 2'den 8'e çıkarmak planı değiştiremiyordu. İki
profil **birebir aynı planı** üretiyordu.

> İki yanlış biçim denendi ve ölçümle elendi. *"Ortalamanın üstündeki sapma"*
> denendiğinde motor cumartesiye gerekenden fazla kişi koymaya başladı (3
> yerine 5): ortalamayı yükseltmek herkesin sapmasını düşürüyordu. Aynı açık
> eşik teriminde de var — ihlali kaldırmanın ucuz yolu *başkalarına gereksiz
> cumartesi vermek*. Artan marjinal maliyette bu açık yok.

**Onaylandı (K-29, Mustafa, 16 Eylül):** adalet eşiğin altında da bir
tercihtir. Üç plan kartının birbirinden farklı çıkmasını sağlayan mekanizma
budur.

## 5b. Fazla mesai — hedef için asla, asgari zorlarsa minimum (K-30)

| Durum | Davranış |
|---|---|
| Yalnız **hedef** kapsama iyileşecek | Fazla mesai **yapılmaz** |
| **Asgari** kapsama (SERT) tutmuyor | Fazla mesai **yapılır**, gereken kadar |
| Profil tavanı zorunlu aşıma yetmiyor | Plan **çözümsüz** |

Profil tavanı (CALISAN 0 · DENGELI 10 · KAPSAMA 15) **zorunlu** fazla
mesainin sınırıdır; isteğe bağlı fazla mesai için zaten kullanılmıyor.

Ceza katsayısı (dakika başına 50) bir **kalibrasyondur**, karar değil.
Testler *"ceza sıfır olmasın"* diyor, *"tam olarak 50 olsun"* demiyor —
ölçüldü: ceza 0 yapılınca test kırmızı yanıyor, 1 yapılınca yanmıyor.

## 6. Onarım döngüsü — §11.7

`/solve` üç adım koşar:

1. Çözücü plan üretir
2. **Bağımsız doğrulayıcı** denetler
3. Sert ihlal varsa, ihlal edilen çalışan-gün çiftleri kapatılıp **en fazla
   2 kez** yeniden denenir; hâlâ varsa `durum: cozumsuz` + K-10 en iyi plan

Denetim **her zaman kullanıcının girdisiyle** yapılır, onarım için eklenen
kilitlerle değil. Yoksa ikinci turda doğrulayıcı, motorun kendi koyduğu koltuk
değneklerini "kural" sanıp onaylardı.

Çıktıdaki `bagimsiz_denetim` bloğu doğrulayıcının sayılarını taşır ve
`metrikler.sert_ihlal` (motorun **kendi** ölçümü) ile yan yana durur. İkisi
ayrışıyorsa taraflardan biri kuralı yanlış yorumluyor demektir.

## 7. İki kural bilerek ayrı — karıştırılırsa sessiz hata olur

| Kural | Molayı ne yapar | Türü |
|---|---|---|
| `ASGARI_KAPSAMA` | **Saymaya dahil eder** — "yeterli kişi planlandı mı" | SERT |
| `MOLA_KAPSAMASI` | **Düşer** — "o an sahada kaç kişi var" | YUMUŞAK (K-14) |

Üç kişinin üçü de 12:00'de moladaysa: `ASGARI_KAPSAMA` tamam (üçü de atanmış),
`MOLA_KAPSAMASI` ihlal (sahada kimse yok). İkisini karıştıran bir uygulama o
planı **geçersiz** yapardı; doğrusu puanını düşürmektir.

Bu ayrım `test_asgari_kapsama_molayi_SAYMAZ_yani_dusurmez` ile sabitlendi.

## 8. Kırmızı kanıt — ilk turda 8'de 4'ü **kaçtı**

§16.4 kuralı: bir test yeşil sayılmadan önce kırmızı yanabildiği
gösterilmeli. Motor koduna tek tek kasıtlı bozmalar uygulandı.

**İlk tur: 8 bozmanın 4'ü hiçbir teste yakalanmadı.**

| Kaçan bozma | Neden kaçtı |
|---|---|
| Ağırlık tablosu yok sayılır | A7 yeşil kalıyordu; profil farkı **başka bir sebepten** oluşuyordu |
| Adalet gradyanı kaldırılır | Aynı |
| Orkestra doğrulayıcıyı çağırmaz | Import'a bakan test yakalamıyor — import durur, **çağrı** kaybolur |
| Fazla mesai tavanı sabitlenir | Hiçbir senaryo o tavana dokunmuyordu |

Eksik testler bunun üzerine yazıldı (`09-motor/testler/test_profiller.py`).
İkinci turda **12 bozmanın 12'si yakalandı.**

### Ölçüm yöntemi hakkında bir not

*"Motor şu kişiyi seçti"* biçimindeki testler **kırılgandır**: kısıt gevşekse
çözücü eşit değerdeki seçenekler arasında arama sırasına göre seçer ve bozulmuş
kod aynı cevabı verebilir. Bu varsayılmadı, **ölçüldü** — gradyan kaldırıldığı
hâlde küçük bir sahnede aynı kişiler seçildi.

Bu yüzden `cozum_istatistikleri.amac_degeri` çıktıya eklendi: aynı girdi, iki
farklı seçim **sabitlenmiş** hâlde çözülüp amaç değerleri karşılaştırılıyor.
Arama sırasından bağımsız, kesin ölçüm.

## 9. Klasör adı hakkında — açık bir sorun

`07-motor/` klasöründe **motor yok**, müşteri Excel'ini okuyan analiz
betikleri var. Oradaki OKU-BENİ `08-analiz/` olarak yeniden adlandırılmasını
öneriyor, karar bekliyor.

⚠ **O ada geçilirse çakışma olur:** `08-analiz/` ile `08-motor-testleri/`
aynı numarayı paylaşır. Yeniden adlandırma kararı verilirken bu göz önüne
alınmalı — örneğin `10-analiz/`.

## 10. Sıradaki

| | Ne |
|---|---|
| **1** | **T-13** — `ADALET_DENGESI`'nin `saat` boyutu (ürün kararı gerekiyor) |
| 2 | **`/suggest`** (§11.5) — ⚠ kabul ölçütü yok, önce cümleler yazılıp onaylanmalı |

**Kapanan ürün kararları:** K-27 (adalet eşiği) · K-28 (erken durma) ·
K-29 (adalet gradyanı) · K-30 (fazla mesai: hedef için asla, asgari zorlarsa
minimum).
