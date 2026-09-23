# Haftalık inceleme döngüsü

**Karar: 23 Eylül 2026.** Mimar (Yılmaz) şu an ulaşılamıyor; teknik ikinci göz
rolünü **haftalık dış tarama** üstleniyor.

## Kim ne yapar

| | Kim | Ne |
|---|---|---|
| **Yazma** | Claude penceresi | Kod, test, doküman. **Tek aktif yazıcı** (R5 korunuyor) |
| **Kapanış kontrolü** | Aynı pencere | Her iş parçası kapanırken kabul cümlesi madde madde işaretlenir. *İnceleme değil, kontrol listesi* |
| **Haftalık tarama** | **Mustafa + farklı sağlayıcının modeli** | İki geçiş: haftanın farkı + şartname-kod taraması |
| **Bulguların doğrulanması** | Claude penceresi | Her bulgu **ölçülerek** sınanır. Dış tarama iddia üretir, kanıt değil |
| **Ürün kararları** | **Mustafa** | Karar gerektiren bulgu uydurulmaz, kaydedilir ve beklenir |

> ⚠ **Bu düzenlemenin açık tarafı.** Geri alma bedeli 🔴 olan kararlar
> (M-01 kiracılık, M-06 denetim kaydı, M-09 motor mimarisi, M-10 kurallar
> veride, M-11 zaman modeli) için şu an **ikinci bir teknik insan görüşü yok.**
> Dış tarama bunun bir kısmını karşılar; *"bu sistemle yaşayacak birinin"*
> görüşünün yerine geçmez. Yılmaz'a ulaşılınca ilk gösterilecek şey bu liste.

## Haftalık paket — Mustafa'nın GPT'ye vereceği

Claude penceresi her hafta sonunda bunu hazırlar:

```
cd C:\Users\PC\Desktop\Tshift
git log --oneline --since="7 days ago"
git diff --stat HEAD@{7.days.ago} HEAD
```

**Pakete girenler:**

1. `05-inceleme/beceriler/01-dal-farki-incelemesi.md` — 1. geçişin yöntemi
2. `05-inceleme/beceriler/02-sartname-kod-taramasi.md` — 2. geçişin yöntemi
3. O haftanın `git diff` çıktısı
4. Kapanan iş parçalarının **kabul cümleleri**
5. `02-spec/v1.4-master-spec.md`
6. Hangi taramanın sırası olduğu (aşağıya bak)

## Dönüşümlü tarama — her hafta beşini birden yapma

`02-sartname-kod-taramasi.md` beş tarama tanımlıyor. Hepsini her hafta
koşturmak hem pahalı hem getirisi düşük: kural kataloğu haftadan haftaya
değişmiyor.

| Hafta | 2. geçişte koşan tarama |
|---|---|
| 1 | Tarama 1 — kural kataloğu: gövdesi var mı |
| 2 | Tarama 2 + 3 — okunmayan alanlar, ateşlenemeyen yollar |
| 3 | Tarama 4 — girdi biçimi sözleşmesi |
| 4 | Tarama 5 — sınır ve güvenlik |

**1. geçiş (haftanın farkı) her hafta koşar.** Değişen tek şey odur.

> Büyük bir iş parçası bittiğinde (motorun bitmesi gibi) sıra bozulur ve
> **beşi birden** koşturulur. 16 Eylül böyle yapıldı: 19 bulgu.

## Dönen bulgularla ne yapılır

1. Claude penceresi her bulguyu **koşturarak** doğrular — *"doğrulayamadım"*
   demeden önce erişim denenir (O-10)
2. Doğrulananlar `00-DEVIR/06-ACIK-RISKLER.md`'ye T-numarasıyla girer
3. Doğrulanamayanlar da yazılır — **neden doğrulanamadığıyla birlikte**
4. Öncelik ölçütü: **yanlış karar riski**
5. Ürün kararı içerenler Mustafa'ya sorulur, uydurulmaz

## Ölçüm şartı

Her haftanın bulgu sayısı `06-ACIK-RISKLER.md`'ye yazılır.

> **Arka arkaya üç haftada kayda değer bulgu çıkmazsa** taramanın sıklığı
> düşürülür (haftalık → iki haftalık). Bırakılmaz.

İki geçiş **ayrı ayrı** ölçülür. 1. geçişin kuruması beklenir — kod
olgunlaştıkça haftalık fark küçülür. 2. geçişin kuruması ise *"şartname ile
kod artık örtüşüyor"* demektir ve o ayrı bir haber.

## Neden kalıcı araç değil

Değeri üreten şey ikinci bir ajan değil, **soğukluk**: hatırlamayan bakar.
Depoda duran, bağlam biriktiren bir inceleyici zamanla işi yapan modele
benzer ve aynı kör noktayı edinir. Makalenin kendi uyarısı da bu:
*"grafik ya da depo talimatları bayatsa, iyi yapılandırılmış ama kötü bağlama
dayanan bir karar çıkar."*

Haftalık, elle, sıfırdan başlayan bir tarama bu riski taşımıyor.
