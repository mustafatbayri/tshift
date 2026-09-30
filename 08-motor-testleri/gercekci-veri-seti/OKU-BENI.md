# Gerçekçi veri seti — S-20

> ⚠ **Bu sayfa 28 Eylül'deki 350 kişilik S-20 setini anlatıyor.** 29 Eylül'den
> beri bekçilerin kullandığı set **500 kişilik iki settir**
> (`fikstur/_sahne-S30-85.json`, `fikstur/_sahne-S30-95.json`); tanımı ve
> gerekçesi `uret_veri_seti.py`'nin başında. Aşağıdaki sayılar S-20'nindir.

**Ne bu.** 350 kişilik, üç ekipli, on dört vardiya şablonlu bir organizasyon.
Motorun oyuncak sahnelerde değil, **gerçek ölçekte** ne yaptığını ölçmek için.

**Neden ayrı klasör, `v6` değil.** `v1`…`v5` aynı altın senaryo setinin
(A1–A12) sürümleri. Bu ondan farklı bir şey — onların yerine geçmiyor,
yanlarında duruyor. `v6` diye açsaydım `DENETIM.py` onu güncel sürüm sanar ve
bütün v5 atıflarını "bayat" sayardı (28 Eylül'de tam olarak bu oldu, 37 hata).

---

## İçindekiler

| dosya | ne yapar |
|---|---|
| `uret_veri_seti.py` | sahneyi üretir. Tohum sabit (`20260928`) — aynı girdi hep aynı dosyayı verir |
| `fikstur/_sahne-S20.json` | üretilmiş sahne |
| `kural-kapsamasi.py` | *"kullanmadığımız kural kalmasın"*ı **ölçer** |
| `ihlal-vakalari.py` | her kural için birer kırmızı kanıt |
| `sahte_pdks.py` 🆕 | **sahte PDKS** (Mustafa'nın ikinci yolu): hafta 1'in planından *"plana %80-85 uyumlu"* gerçekleşme ve **eksik kayıt** üretir, hafta 2'yi o eksik geçmişle çözer, sonra planı **gerçek** geçmişe göre denetler: K-42 raporu gerçek ihlalleri haber verdi mi. Oranların hangisinin ölçüm, hangisinin varsayım olduğu dosyanın başında. Üreticinin kendi testleri `testler/test_sahte_pdks.py` (CI'da) |
| `iki-hafta-olc.py` 🆕 | **geçmiş veri ölçümü** (T-28): hafta 1'in planı hafta 2'nin geçmişi olur; hafta 2 geçmişsiz ve geçmişle çözülür, ikisi de geçmişi bilen denetçiye sorulur. `--uc-hafta` üçüncü haftayı iki haftalık geçmişle çözer. Uzun (10–20 dk), CI'da değil |

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti
py uret_veri_seti.py          # sahneyi yeniden üret
py kural-kapsamasi.py         # temiz koşuda hangi kural gerçekten sınandı
py ihlal-vakalari.py          # her kural kırmızı yanıyor mu
py ihlal-vakalari.py -v       # + ihlal mesajları ve yan etkiler
```

---

## Sahne neyi içeriyor

| | |
|---|---|
| çalışan | **350** — Satış 200, Back Office 100, Müşteri Hizmetleri 50 |
| sözleşme | `tam_zamanli` 240 · `yari_zamanli` 83 · `sezonluk` 19 · `stajyer` 8 |
| vardiya şablonu | **14** — Satış 5, Back Office 5, MH 4 |
| talep | **422 hücre**, hafta içi / hafta sonu **ayrı eşiklerle** |
| kural | **39** — kataloğun tamamı |

**Vardiyalar bilerek örtüşüyor.** Gün üçe bölünmedi; Satış'ta 07–15, 11–19,
15–23, 23–07 ve 10–16 var. Örtüşme `CAKISMA_YOK`'u gerçekten sınar, gece
vardiyası gün sınırını aşar (Z-1).

**Her ekibin ayrı mola politikası ve ayrı yemek penceresi var** — aynı kodun
üç ayrı politikayı doğru çevirdiğini görmek için.

---

## İki ölçüm, iki ayrı soru

Bu ikisi farklı şey ölçer ve ikisi de gerekli.

### `kural-kapsamasi.py` — *"temiz bir koşu neyi kanıtlar?"*

Her kural için üç durumu ayırır:

| durum | anlamı |
|---|---|
| **SINANDI** | kural gerçekten zorlandı |
| **TEMİZ** | çalıştı ama veri onu zorlamadı — ⚠ **bu yeşil bir şey kanıtlamaz** |
| **GÖVDE YOK** | yazılmamış kural; `uygulanmayan_kurallar` kanalının işi |

Ortadaki satır bu aracın varlık sebebi. *"Plan temiz"* ile *"bu kural hiç
sınanmadı"* aynı renkte görünüyordu.

### `ihlal-vakalari.py` — *"bu kural hiç ateşleyebiliyor mu?"*

Her kural için, **yalnız onu** çiğnemesi gereken küçük bir plan bozması
tanımlar; sonra üç şeyi sınar:

1. Bozma sonrası o kural ihlal yazıyor mu
2. Bozma **öncesi** temiz miydi (ihlal bozmadan mı geliyor)
3. Bozma başka kuralları da patlattı mı (vaka dar mı)

Üçüncüsü bilgilendirici, hata değil: yedi gün çalışan biri hem
`HAFTA_TATILI` hem `ARDISIK_CALISMA_GUNU` çiğner. Rapor yan etkiyi yazar.

**28 Eylül itibarıyla: 24/24 kırmızı yanıyor.**

---

## Bu veri setinin şimdiye kadar bulduğu şeyler

| bulgu | ne |
|---|---|
| **T-45** 🔴 | Tanınmayan **değer** sessizce geçiyor. `part_time` yazdım, motor tanımadı, `PART_TIME_LIMIT` 90 kişiyi atladı, **hiçbir kanal bildirmedi** |
| **T-46** 🔴 | 350 kişide model kurma **117 saniye**, 968 bin değişken; bunun **%64'ü** kişinin çalışamayacağı ekiplerin şablonları için |
| — | `okunmayan_alanlar` kanalı **çalışıyor**: `aktif` alanını (doğrusu `durum`) yakaladı |

⚠ **Tam ölçekli çözüm süresi henüz ölçülmedi.** Ölçmek için:

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\gercekci-veri-seti
py coz-olc.py
```

---

## Bu veri setini yazarken yapılan hatalar

Kayda geçiyor, çünkü ikisi de aynı sınıftan ve ikisini de **ölçüm** buldu:

1. **`part_time`** yazdım, şartname `yari_zamanli` diyor (§8.3). Motor sessiz
   kaldı → bu **T-45** oldu.
2. **`aktif: false`** yazdım, şartname `durum: pasif` diyor. Motor bunu
   `okunmayan_alanlar` ile **bildirdi** → mekanizmanın çalıştığının kanıtı.

İkisi de "veri setim yanlıştı" diye kapatılabilirdi. Aradaki fark — birinin
bildirilmesi, ötekinin bildirilmemesi — asıl bulgu.
