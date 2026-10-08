# 7 Ekim 2026 — fazla mesaisiz ilk aramanın kuyruğu (keşif; ölçüm sırasında motor değişmedi — yeniden başlatma 7 Ekim 18:35'te koda indi, 8 Ekim'de varsayılan oldu)

**Soru.** Ürün yolu (K-61) birinci aşamada geçerli planı fazla mesai
değişkenleri 0'a sabitken arar; payı en çok 120 sn. 7 Ekim gece koşusunda
bu arama 18 koşunun 17'sinde 8,6–21 sn sürdü, **1'inde 120 sn'de bulunamadı**
→ motor fazla mesai serbest yola düştü, plan 30 saat fazla mesaiyle döndü
(116.976; aynı gecenin öteki iki koşusu 26.602 / 26.823) — T-60 bulgu 25.
Kuyruk ne kadar kalın; 120 sn'yi birkaç yeniden başlatma hâlinde harcamak
kuyruğu keser mi?

**Araç.** `kuyruk.py` — 500 kişilik fikstürü bir kez kurar, birinci aşamayı
motorun kendi yardımcılarıyla (`_molalari_sabitle`, `_fazla_mesaiyi_sifirla`,
amaç silinmiş) aynen hazırlar ve aynı modeli N farklı `random_seed` ile
çözer; her denemenin süresi ve durumu `jsonl`e yazılır; sonda kantiller,
P(T > eşik) ve yeniden başlatma politikalarının **offline tahmini** (3 × 40
sn gibi) basılır.

**Koşturma (Mustafa'nın makinesi; bulutta koşturulmaz):**

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti\kesif\2026-10-07-fm-siz-arama-kuyrugu
py kuyruk.py --deneme 30 --tavan 120 --sifir-tekrar 5 --cikti kuyruk-30.jsonl
```

**Karar kuralı (koşudan önce yazıldı, 7 Ekim 17:45).** Sonuç T-60 bulgu
25'e yazılır. P(T > 120 sn) ≈ 0 ve %90 kantil < 40 sn ise kuyruk gece
koşusunun bir tesadüfüdür — yine de motora yeniden başlatma yazılır (ucuz
sigorta), ama ölçüm önceliği hibrite döner. P(T > 120 sn) > 0 ya da %90
kantil > 60 sn ise kuyruk gerçektir: yeniden başlatma politikası (offline
tahminde başarısızlığı en düşük olan) motorda ölçüm seçeneği olarak yazılır,
500 kişide 900 sn × 3 ile doğrulanır, sonra varsayılan yapılır. Her hâlde
*"bulunamadı"* yolunun planı (30 saat fazla mesai) bir ürün sorunu olarak
kalır: K-61 ancak bu kuyruk kapanınca *"kapandı"* denir.

**Sonuç (7 Ekim 18:00, Mustafa'nın makinesi; `kuyruk-30.jsonl`).** 35 denemenin
hepsi 120 sn'de buldu; medyan 7,5 sn, %90 13,0 sn, en uzun 61,9 sn; P(T > 40)
= 2/35, P(T > 60) = 1/35, P(T > 120) = 0/35. Tohum 0'ın beş tekrarı 7,8–55,9
sn: rastgelelik tohumdan değil paralel işçilerin zamanlamasından. Kuralın
ilk dalı: kuyruk ince ama gerçek (53 gözlemde 1 × > 120 sn); yeniden
başlatma (3 × 40 sn, farklı tohum; offline tahmin %0,02 başarısızlık) motorda
ölçüm seçeneği olarak yazılacak, 900 sn × 3 ile doğrulanacak, sonra
varsayılan. Okuması T-60 bulgu 25'te.

> ⚠ **Düzeltme (7 Ekim 18:40, O-19).** Yukarıda ve 18:00 kaydında *"tohum 0 =
> motorun kullandığı değer (CP-SAT varsayılanı)"* deniyordu — **yanlış**.
> CP-SAT'in varsayılan tohumu **1**'dir (ortools 9.15'te ölçüldü:
> `CpSolver().parameters.random_seed` → 1); motor tohum yazmadığı için 1 ile
> arıyordu. 18:00 koşusundaki 5 tekrar tohum 0'ındı — motorun tohumunun değil.
> Vardığı sonuç değişmez: aynı tohumda bile 7× fark, rastgelelik paralel
> işçilerin zamanlamasından; motorun tohumu (1) 30'un içinde bir kez ölçüldü.
> Araçta tekrarlanan tohum artık `--tekrar-tohum` (varsayılan 1);
> `--sifir-tekrar` adı 18:00 komut satırı geçerli kalsın diye duruyor (anlamı
> tekrar sayısı). Varsayım kütüphaneden okunmadan yazılmıştı; ders O-19'da.

**Politika kipi (18:50'den sonra).** Motora yeniden başlatma yazıldıktan sonra
araç motorun kendi `_fazla_mesaisiz_ara` fonksiyonunu tekrar tekrar koşturur:

```
py kuyruk.py --politika 3 --deneme 20 --tavan 120 --cikti politika-3x40.jsonl
```

Her koşuda: bulundu mu, toplam süre, hangi denemede (tohum 1 → 2 → 3). Asıl
doğrulama kalite-olc.py `fm_once_deneme3` (900 sn × 3); bu kip aramanın
kendisini 20 kez görmek için (karar kuralı: hiçbir koşu 3 × 40'ta bulunamadı
yoluna düşmemeli; 2+ deneme gereken koşu sayısı kuyruğun ölçüsüdür).

**Politika kipinin sonucu (7–8 Ekim gecesi, Mustafa'nın makinesi;
`politika-3x40.jsonl`).** 20 koşunun **20'si de ilk denemede** (tohum 1,
OPTIMAL) buldu; süreler 6,48–8,37 sn (medyan 6,6 sn, en uzun 8,4 sn), 2+
deneme gereken 0, bulunamayan 0. Aynı gece `fm_once_deneme3` 900 sn × 3'te de
üç koşu ilk denemede (6,73 / 7,12 / 7,34 sn) buldu → karar kuralı tuttu,
**`fazla_mesaisiz_deneme` varsayılanı 3 oldu, K-61 kapandı** (8 Ekim sabahı;
T-60 bulgu 25, K-61). Dürüst okuma: politika kipinin her koşusu ürün yolu
gibi tohum 1 ile başlar; yani bu 20 koşu ürünün **ilk denemesinin 20
tekrarıdır** ve yayılımı 1,3× (6,5–8,4 sn) çıktı — 18:00 ölçümünde aynı
tohumun (0) beş tekrarı 7× yayılmıştı (7,8–55,9 sn). Yeniden başlatma
(tohum 2, 3) 23 koşunun hiçbirinde **devreye girmedi**: zararsızlığı ölçüldü
(puan, süre, fazla mesai tek denemeli yolla aynı), koruma değeri 18:00
ölçümüne (53 gözlemde 1 × > 120 sn, 2 × 56–62 sn) ve çevrimdışı tahmine
dayanıyor. Ürün koşularının `fazla_mesai_once_sifir.denemeler` alanı okunmaya
devam eder; ilk denemede bulunamayan ilk koşu T-60'a yazılır.
