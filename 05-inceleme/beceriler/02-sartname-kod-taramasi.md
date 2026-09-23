# Beceri · Şartname–kod taraması

**Ne zaman:** bir iş parçası bittiğinde (motorun bitmesi gibi).
**Süre:** birkaç saat, birden fazla tur.
**Kim:** **farklı bir sağlayıcının** modeli. Salt-okunur, oturum geçmişi yok.

> **Neden farklı sağlayıcı.** Aynı model aynı kör noktayı iki kez taşır. Ve
> asıl mekanizma zekâ değil **soğukluk**: işi yapan model *"bunu zaten yazdım"*
> diye hatırladığı için bir daha bakmaz. Hatırlamayan bakar.
>
> Bu yüzden bu tarama **kalıcı bir araca bağlanmaz**. Depoda duran, bağlam
> biriktiren bir inceleyici soğukluğunu kaybeder — yani değerin kaynağını.

**Ölçülmüş getirisi:** 16 Eylül 2026, üç tur, **19 bulgu**, dokuzu 🔴,
yanlış alarm sıfır. Ayrıca dokümandaki iki yanlış iddia düzeltildi.

---

## Girdi

1. `02-spec/v1.4-master-spec.md` — **referans budur**
2. Deponun tamamı: `09-motor/`, `04-kod/`, `08-motor-testleri/`
3. `00-DEVIR/02-DEGISMEZLER.md` ve `00-DEVIR/03-MIMARI-KARARLAR.md`

> **Referans yönü kritik.** Şartname gerçek, kod **iddiadır**. Ters çevirme:
> kodu gerçek sayıp şartnameyi hatırladığın hâliyle karşılaştırmak, işi yapan
> modelin zaten yaptığı şeydir ve hiçbir şey bulmaz.

---

## Yöntem — beş tarama

### Tarama 1 · Kural kataloğu: gövdesi var mı

Şartname §6'daki her kural için:

1. Kod içinde bir gövdesi **var mı**?
2. Varsa, şartnamedeki cümleyle **aynı şeyi mi** söylüyor?
3. Yoksa, motor bunu **sessizce mi geçiyor**, yoksa bildiriyor mu?
   (`uygulanmayan_kurallar` / `eksik_boyutlar` alanları)

*Bu taramadan çıkanlar: T-18, T-30.*

### Tarama 2 · Okunmayan girdi alanları

Şartnamenin bahsettiği her girdi alanı için: **kod bu alanı hiç okuyor mu?**

```
grep -rn "<alan_adi>" 09-motor/
```

Sıfır sonuç = bulgu. Alan şartnamede var, kodda yok.

*Bu taramadan çıkanlar: **T-28** (`gecmis_vardiyalar` hiçbir dosyada geçmiyor —
yasal dinlenme kuralı önceki haftaya kör).*

> Bu tarama **dal farkı incelemesinin asla yakalayamayacağı** sınıfı bulur:
> bir **yokluk** hiçbir diff'te görünmez.

### Tarama 3 · Ateşlenemeyen kod yolları

Her kural gövdesi için: bu kod **hangi koşulda** çalışır, o koşulu **kim
üretir**? Üreten yoksa kural ölüdür.

*Bu taramadan çıkanlar: **T-29** (`DONMUS_GUN` yalnız `_yeni` işaretli
atamalarda ateşleniyor, o işareti hiçbir yer üretmiyor. Ölçüm: işaretsiz
girdide 0 ihlal, elle işaretlenince 1).*

### Tarama 4 · Girdi biçimi sözleşmesi

Şartnamedeki girdi biçimini **birebir** alıp motora ver. Ne oluyor?

*Bu taramadan çıkan: **T-19** — şartname §11.2 `{ekip, gun, saat}` diyor, motor
`{gunler:[], saatler:[]}` okuyor. Şartname biçimi verilince **sıfır atamalı
plan** üretiliyor ve `%100 kapsama, yayınlanabilir` diyor.*

⚠ **Dikkat:** *"sert ihlal 0, kapsama %100"* kontrolü bunu **yakalamaz** —
boş plan zaten ihlalsizdir. Kontrol *"atama sayısı > 0"* diye de sormalı.

### Tarama 5 · Sınır ve güvenlik

Bu tarama **`04-kod/` tarafında** ve motor incelemesinde unutulmaya müsait.

- Sırlar: ortam değişkeni yoksa kod **varsayılana mı düşüyor**, hata mı veriyor?
- İstemci IP'si: proxy başlıkları iletiliyor mu, ara katman var mı?
- Kiracı yalıtımı: bir kiracının işlemi diğerini etkileyebilir mi?
- Eşzamanlılık: oku-kontrol-yaz dizileri satır sürümü / işlem ile korunuyor mu?

*Bu taramadan çıkanlar: **T-34** (parola ve JWT anahtarı kodda varsayılan),
**T-35** (bir kişinin beş yanlış parolası bütün kiracıyı kilitliyor, denetim
kaydındaki her IP kurgusal), **T-36**.*

> ⚠ **Bu üçü ilk turda *"doğrulayamıyorum, o dosyalar bende yok"* diye
> geçiştirildi. Erişim vardı, denenmemişti.** Otopsisi O-10. Bu yüzden 5.
> tarama listeye ayrı madde olarak kondu: unutulduğunda fark edilmiyor.

---

## Bulgu nedir, ne değildir

| Bulgu | Bulgu değil |
|---|---|
| Koşturulup gösterilen fark | *"Şu yanlış olabilir"* |
| *"Şu girdiyle şu çıkıyor, şartname şunu diyor"* | *"Burası kırılgan görünüyor"* |
| Sıfır `grep` sonucu | Üslup, isimlendirme, tercih |
| Ateşlenemediği ölçülen kural | Bakılmadan verilen *"doğrulayamadım"* |

---

## Çıktı biçimi

```
KOD      : SK-1 (sartname-kod 1)
AGIRLIK  : KIRMIZI (yanlis karar urettirir) | SARI (guveni bozar)
IDDIA    : <tek cumle>
URETIMI  : <girdi + komut + beklenen/gercek cikti>
ONEMI    : <hangi sartname maddesini, hangi K/M kararini deviriyor>
KAPSAM   : <uretilen planlarda mi cikiyor, yoksa yalniz ice aktarmada mi>
```

**`KAPSAM` alanı bilerek var.** T-27'de bulgu gerçekti ama çözücü molayı zaten
vardiya içine zorluyordu — yani hata üretilen planlarda çıkmıyordu, riski
taşıyan yol içe aktarılan veri ve plan editörüydü. Bu ayrım yazılmazsa bulgu
olduğundan büyük görünür.

---

## Sonrasında

1. Her bulgu `00-DEVIR/06-ACIK-RISKLER.md`'ye T-numarasıyla girer
2. **Bu tarafta ölçülerek doğrulanır** — dış incelemenin iddiası kanıt değildir
3. Ürün kararı içerenler **uydurulmaz**, kaydedilip beklenir
4. Öncelik sırası ölçütü: **yanlış karar riski** (hız ve kolaylık sonra)
