# Beceri · Dal farkı incelemesi

**Ne zaman:** haftalık taramanın **1. geçişi** — o haftanın birikmiş farkı.
**Süre:** 20–40 dakika.
**Kim:** o değişikliği **yazmayan** bir model. Salt-okunur.

> ⚠ **Haftalık ritmin bedeli.** Pazartesi yapılan bir hata Cuma'ya kadar
> yakalanmaz ve o arada üstüne inşa edilir. Bu yüzden **1. maddenin**
> (kabul cümlesini madde madde işaretle) hafifletilmiş hâli, iş parçasını
> kapatan tarafça **kapanış anında** yapılır — inceleme olarak değil,
> kontrol listesi olarak. T-27'nin üçüncü şartını yakalayan şey buydu.

## Neyi yakalar, neyi yakalamaz

| Yakalar | Yakalamaz |
|---|---|
| Yeni işteki gerileme | Eski koddaki birikmiş sapma |
| Kabul cümlesinin yazılmamış şartı | Hiç yazılmamış alanlar (**yokluk diff'te görünmez**) |
| İkinci doğruluk kaynağı açılması | Hiç ateşlenmeyen ölü kod yolları |
| Dokümandaki doğrulanmamış sayı | Dalın dışındaki dosyalar |

Yakalayamadıkları `02-sartname-kod-taramasi.md`'nin işi. İkisi ayrı alet.

---

## Girdi — incelemeye başlamadan istenecekler

1. `git diff` çıktısının tamamı (kısaltılmamış)
2. Bu iş parçasının **kabul cümlesi** — `08-URUN-KARARLARI.md` (K-serisi) ya da
   `06-ACIK-RISKLER.md` (T-serisi) içinden
3. Testlerin koşum çıktısı: **kaç geçti, kaç kırmızıydı, kırmızı kanıt var mı**

Üçü de yoksa inceleme yapılmaz — eksik olan istenir.

---

## Kontrol listesi

### 1. Kabul cümlesi — **madde madde işaretle**

> Kabul cümlesini bileşenlerine ayır. Her bileşen için diff'te karşılığını
> göster. Karşılığı olmayan bileşen **bulgudur.**

⚠ **Bu maddenin kendi kanıtı var (23 Eylül · T-27).** Kabul cümlesi üç şart
içeriyordu: vardiya dışındaki, **üst üste binen** ve vardiyadan uzun molalar.
İlk turda kırpma yazıldı, altı test yeşil yandı, *"kapandı"* denecekti.
**İkinci şart yazılmamıştı** — `10:00–12:00` ile `11:00–13:00` dört saat
sayılıyordu, üç değil. Yakalayan şey test değil, **cümlenin kendisiydi.**

*"Testler yeşil" kapanış kanıtı değildir: testler yalnız yazılanı sınar,
söz verileni değil.*

### 2. Kırmızı kanıt gerçekten alınmış mı

- Yeni test, düzeltmeden **önce** koşturulup **kırmızı** görülmüş mü?
- Kırmızı yanmayan bir test hiçbir şey kanıtlamaz — yazılmamış olsa da aynı
  sonucu verirdi.
- Düzeltmeden önce **yeşil** yanan testler varsa: bunlar gerileme koruması
  olarak **bilerek mi** yazılmış? Yazılmışsa doğru. Yazılmamışsa, test
  sınadığını sandığı şeyi sınamıyor olabilir.

### 3. İkinci doğruluk kaynağı açıldı mı

> Bu değişiklikten sonra **aynı gerçek iki yerden** okunuyor mu?

⚠ **Kanıtı (16 Eylül · T-32).** K-30 yazılırken fazla mesai tavanı çözücüde
**profil tablosundan**, doğrulayıcıda **kural parametresinden** okunur hâle
geldi. İkisi bugün aynı sayıyı veriyor; kiracı parametreyi değiştirdiği gün
sessizce ayrışırlar. Şartname §7.6 kural *mantığını* ayırıyor, **ortak
gerçeğin tek kaynağını** garanti etmiyor.

Sor: bu değeri başka nereden okuyan var? İkisi ne zaman ayrışır?

### 4. Bağımsızlık bozuldu mu (§7.6)

- `09-motor/cozucu/` ile `09-motor/dogrulayici/` birbirini **import etmez**
- `09-motor/orkestra.py` ikisini de import eder — **bu doğrudur**
- Bekçisi: `09-motor/testler/test_bagimsizlik.py`

### 5. Dokümandaki her sayı doğrulandı mı

> Diff bir dokümanda sayı değiştiriyorsa, o sayı **koşturularak** mı
> bulundu, hatırlanarak mı?

⚠ **Kanıtı (16 Eylül).** *"On iki altın senaryo yeşil"* yazılmıştı; `12 passed`
= 7 senaryo + paketin 5 sağlık testiydi. Ayrıca *"17 kural"* yazıyordu, 19'du —
üstelik aynı dosyanın tablosu 19 satır listeliyordu. `DENETIM.py` bunu
yakalayamaz: **tutarlılığa bakar, doğruluğa değil.**

### 6. Yollar depo köküne göre mi yazılmış

`cozucu/model.py` ❌ · `09-motor/cozucu/model.py` ✅
`DENETIM.py` 3. kontrolü bunu hata sayar.

### 7. Karar kaydı gerektiren bir şey yapıldı mı

Diff, kayıtlı bir K- ya da M- kararını değiştiriyor ya da yeni bir karar
içeriyorsa: kayıt güncellendi mi? Yeni kararın **bekçisi** (onu çiviyen test)
var mı? Yoksa bu T-26'dır.

---

## Çıktı biçimi

Her bulgu için, bu dört başlık:

```
KOD      : DF-1 (dal farki 1)
IDDIA    : <tek cumle -- ne yanlis>
URETIMI  : <hangi komut / hangi girdi -- baskasi tekrar edebilsin>
ONEMI    : <hangi kurali, hangi kabul cumlesini, hangi K/M kararini deviriyor>
```

Bulgu yoksa **"bulgu yok"** yazılır ve bu da kayda geçer — ölçüm şartı
(üç incelemede üç bulgu yok → seyrekleş) ancak böyle işler.
