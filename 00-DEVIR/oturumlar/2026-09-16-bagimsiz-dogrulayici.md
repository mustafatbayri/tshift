# 16 Eylül 2026 · Bağımsız doğrulayıcı — ilk iki senaryo yeşil

**Pencere:** Claude (Cowork) · yazma hakkı bu pencerede
**Girdi:** `02-spec/v1.4-master-spec.md` §6, §7.6, §11.4, §16.1 · A4 ve A8 fikstürleri
**Çıktı:** `09-motor/` — doğrulayıcı, servis, 26 birim testi
**Ürün kodu (.NET) değişmedi. CI'ya dokunulmadı. 39/39 hâlâ yeşil.**

---

## Sonuç önce

```
py -m pytest -q          (motor adresliyken)
→ 5 failed, 7 passed, 4 skipped
```

**A4 ve A8 yeşile döndü.** Bu, projede motorun **ilk korunan davranışı**.
Kabul ölçütü bu iki senaryoda taahhüt olmaktan çıkıp bekçiye dönüştü.

| | Önce | Sonra |
|---|---|---|
| Kırmızı | 7 | **5** |
| Yeşil | 4 | **7** |

Kalan beş kırmızı **doğru sebeple** kırmızı: servis ayakta, `/solve` yok.

---

## Neden önce doğrulayıcı, sonra çözücü

Yedi kırmızı testin **ikisi** plan üretmiyor — var olan bir planı denetliyor.
Yani çözücü olmadan yeşile dönebilecek tek iki senaryo onlardı. En küçük
adım seçildi.

Çözücü çok daha büyük bir iş ve doğrulayıcı olmadan zaten sınanamaz: onun
ürettiği planın doğru olup olmadığını söyleyecek bağımsız bir gözü olmalı.

---

## Alınan kararlar

### 1. Dışarıdan hiçbir paket yok

Servis Python standart kütüphanesiyle yazıldı (`http.server`). FastAPI ya da
Flask eklenmedi.

Gerekçe: kurulum adımı olmayan bir servis, *"bende çalışmadı"* ile geçen
saatleri de ortadan kaldırır. Mustafa yazılımcı değil; `py servis.py` ile
`pip install` arasındaki fark onun için büyük. Yük altında koşacak sürüm
ASGI'ye taşınabilir — **sözleşme değişmez**, yalnız taşıyıcı değişir.

### 2. Çözücüyle tek satır mantık paylaşılmayacak

Şartname §7.6 ve §16.1 bunu şart koşuyor ve bu projedeki **en kolay
bozulacak** kural. Çözücü yazılırken *"aynı hesabı iki kez yazmayalım"* deyip
ortak bir modül çıkarmak yasak.

Sebebi D-6: kodu yazan testi de yazarsa aynı yanlış varsayım iki yere birden
geçer ve hiçbir test yakalamaz. Doğrulayıcı ancak çözücüden bağımsızsa onu
denetleyebilir. **Tekrar burada maliyet değil, güvence.**

Bu kural `00-BURADAN-BASLA.md` §3'e ⛔ işaretiyle yazıldı.

### 3. Sessiz geçmeme

Girdide **aktif ama gövdesi yazılmamış** bir kural varsa, cevap
`uygulanmayan_kurallar` listesinde bunu açıkça bildiriyor.

> *"İhlal bulamadım"* ile *"bakmadım"* aynı şey değildir. İkisini karıştıran
> bir doğrulayıcı, yeşil yanan ama hiçbir şey sınamayan testten daha
> tehlikelidir — çünkü planı **temiz gösterir**.

### 4. `ADALET_DENGESI` bilerek yazılmadı

Şartname §6.5 kuralı tanımlıyor ama **ihlal eşiğini tanımlamıyor**: dağılım ne
kadar sapınca ihlal sayılır? `SAAT_DENGESI`'nde eşik var (±2 saat),
`ADALET_DENGESI`'nde yok.

Eşiği koda gömüp uydurmak, bir **ürün kararını kodun içine gizlemek** olurdu.
Kural uygulanmayanlar listesinde görünüyor ve bir test
(`test_adalet_dengesi_bilerek_yazilmadi`) birinin ileride sessizce eşik
uydurmasını engelliyor — yazarsa o test kırmızı yanar.

**T-12** olarak kaydedildi, açık madde **A-17** açıldı.

---

## İki kural bilerek ayrı tutuldu

| Kural | Molayı ne yapar | Türü |
|---|---|---|
| `ASGARI_KAPSAMA` | **Sayar** — "yeterli kişi planlandı mı" | SERT |
| `MOLA_KAPSAMASI` | **Düşer** — "o an sahada kaç kişi var" | YUMUŞAK (K-14) |

Üç kişinin üçü de 12:00'de moladaysa `ASGARI_KAPSAMA` tamamdır (üçü de
atanmış), `MOLA_KAPSAMASI` ihlaldir (sahada kimse yok). İkisini karıştıran bir
uygulama o planı **geçersiz** yapardı; doğrusu puanını düşürmektir.

A8'in `a-kotu` alt durumu tam olarak bunu sınıyor: **0 sert, 1 yumuşak.**

---

## Kırmızı kanıt — yedi kasten bozma

Testlerin gerçekten bir şey koruduğunu görmek için doğrulayıcı yedi ayrı
şekilde kasten bozuldu. **Yedisi de yakalandı.**

| # | Bozma | Hangi karar geri alınırdı |
|---|---|---|
| 1 | `GUNLUK_AZAMI` 11 → 9 | K-18 |
| 2 | `MOLA_HAKKI` brüt yerine net süreye bakar | K-4 |
| 3 | Tam 11 saat dinlenme de ihlal sayılır | K-11 |
| 4 | Örtüşmede ayrıca dinlenme ihlali yazılır | V-1 |
| 5 | Yayın kapısı `yasal`a bakar, `kabul_edilebilir`e değil | K-24 |
| 6 | Gövdesi olmayan kural sessizce geçilir | sessiz geçmeme ilkesi |
| 7 | `ASGARI_KAPSAMA` molayı düşer | K-14 ayrımı |

Rastgele seçilmediler: her biri **sessizce bozulabilecek bir ürün kararıdır**
ve hiçbiri derleme hatası vermez.

---

## Testlerin yakaladığı iki kendi hatam

### 1. "Motor yok" ile "çözücü yok" karışıyordu

İlk yazımda `/solve` 501 döndüğünde istemci *"Motora ulaşılamadı"* diyordu.
Oysa servis ayaktaydı — yalnız o uç yazılmamıştı. İkisi bambaşka sorunlar:
biri *"daha yazılmadı"*, diğeri *"servis çöktü"*. Aynı mesajı verirlerse
saatler yanlış yerde aranır.

Ayrıldı ve `test_cozucu_yokken_sebep_acikca_ayirt_edilir` ile sabitlendi.

### 2. İstemcide `adres=""` ile `adres=None` aynı şey sayılıyordu

`MotorIstemci(adres="")` "adressiz" demek istiyordu ama kod `adres or
ortam_degiskeni` yazdığı için yine ortam değişkenine düşüyordu. Sonuç:
**adressiz davranış hiç sınanamıyordu** — test motor ayakta koşunca sessizce
başka bir yolu deniyordu.

Bunu bir sağlık testi yakaladı. `adres=None` → ortama bak, `adres=""` →
açıkça adressiz olarak ayrıldı.

*Öğrenilen: "boş değer" ile "belirtilmemiş" aynı şey değil. Python'da
`x or y` kalıbı bu ikisini sessizce birleştirir.*

---

## "Tek dosya değişecek" sözü tutuldu

15 Eylül'de test iskeleti yazılırken şu söz verilmişti:

> *"Motor yazıldığında tek dosya değişecek: `motor_istemci.py`. Fikstürlerin,
> kabul ölçütünün ve kontrollerin tek satırı değişmeyecek."*

Doğrulayıcı yazıldı ve gerçekten öyle oldu — `motor_istemci.py` HTTP'ye
çevrildi, başka hiçbir test dosyası dokunulmadı. Sağlık testleri değişti ama
o ayrı: mesaj metni değiştiği için iddiaları güncellendi.

---

## Klasör adı — açık bir çakışma

Doğrulayıcı `09-motor/` altına yazıldı. `07-motor/` klasöründe **motor yok**
(müşteri Excel'ini okuyan analiz betikleri var) ve oranın OKU-BENİ'si
`08-analiz/` adını öneriyor.

⚠ **O ada geçilirse çakışma olur:** `08-analiz/` ile `08-motor-testleri/` aynı
numarayı paylaşır. Yeniden adlandırma kararı verilirken göz önüne alınmalı —
örneğin **10-analiz**.

---

## Değişmeyen şeyler

- .NET ürün kodu: **hiç dokunulmadı**, 39/39 yeşil
- CI yapılandırması: **hiç dokunulmadı**
- Fikstürler: **tek satır değişmedi**
- `02-spec/v1.4-master-spec.md`: **hiç dokunulmadı**
- pytest paketi CI'a **hâlâ bağlanmadı** — beş test kırmızı olduğu sürece
  bağlanmayacak

---

## Sıradaki

**Çözücü (M-09).** Python + OR-Tools CP-SAT, ayrı servis. `servis.py`'deki
`/solve` ucu şu an 501 dönüyor; oraya bağlanacak. Kalan beş senaryoyu
(A1, A3, A6, A7, A9) yeşile çevirecek.

⛔ **Tek zorunlu kural:** `09-motor/dogrulayici/` altındaki hiçbir modülü
import etmeyecek. Aynı aritmetik ikinci kez, bağımsız olarak yazılacak.
