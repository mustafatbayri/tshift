# Fikstür biçimi

Bu klasördeki JSON dosyaları, `../KABUL-OLCUTLERI.md`'de onaylanmış Türkçe
cümlelerin **makine tarafından okunabilir** karşılığıdır.

**Kod değil veri.** Motor hangi dille yazılırsa yazılsın aynı dosyalar koşar.
Bir fikstür hiçbir test çatısına bağlı değildir; pytest de xUnit de aynı
dosyayı okur.

---

## İçindekiler

1. [Dosya listesi](#1-dosya-listesi)
2. [Ortak sahne ve fark](#2-ortak-sahne-ve-fark)
3. [Fikstür zarfı](#3-fikstür-zarfı)
4. [Üç tip](#4-üç-tip)
5. [Karşılaştırma sözdizimi](#5-karşılaştırma-sözdizimi)
6. [Denetleyici](#6-denetleyici)
7. [Bilerek yapılmayanlar](#7-bilerek-yapılmayanlar)

---

## 1. Dosya listesi

| Dosya | Senaryo | Tip |
|---|---|---|
| `_sahne-S10.json` | **Ortak sahne** — hepsinin başladığı yer | — |
| `A01.json` | Normal hafta | `solve` |
| `A02.json` | İzin planlamayı ezer | `backend` |
| `A03.json` | İmkânsız durum ve yöneticinin kararı | `solve` |
| `A04.json` | Gece yarısını aşan vardiya | `evaluate` |
| `A06.json` | Elle sabitlenmiş atamalar | `solve` |
| `A07.json` | Cumartesi adaleti mi, kapsama mı | `solve` |
| `A08.json` | Öğle arası planlaması | `evaluate` |
| `A09.json` | Kadro yetmiyor | `solve` |
| `A10.json` | Çift tıklama | `backend` |
| `A11.json` | Geçmiş veri eksik | `backend` |
| `A12.json` | Geçen haftanın planını kopyala | `backend` |

**A5 yok.** Yaz saati senaryosu ertelendi (K-12); numara bilerek boş bırakıldı,
çünkü başka dosyalar A6–A12'ye atıf yapıyor ve yeniden numaralandırma o
atıfları sessizce yanlış yapardı.

## 2. Ortak sahne ve fark

Her fikstür `_sahne-S10.json`'ı okur ve **yalnız farkını** yazar.

> **Neden:** Aynı sahneyi 11 dosyaya kopyalamak, birini değiştirip diğerlerini
> unutmaya davetiye. Bu depoda aynı kalıp üç kez sorun çıkardı.

`fark` bloğunda tanınan alanlar:

| Alan | Davranış |
|---|---|
| `calisanlar` | Kimliğe göre **birleştirme**: `{"C01": {"izinler": [...]}}` |
| `talep`, `sabit_atamalar`, `kilitler`, `profil`, `donmus_gunler`, `kiraci_saat_dilimi`, `hafta_baslangic` | Tamamen **değiştirir** |
| `vardiya_sablonlari_ekle`, `kurallar_ekle` | Listeye **ekler** |
| `kurallar_cikar` | Kural kodlarını **çıkarır** (yalıtım için) |

Fark bilinmeyen bir çalışanı değiştirmeye çalışırsa denetleyici hata verir.

## 3. Fikstür zarfı

```
{
  "senaryo":      "A4",
  "ad":           "Gece yarisini asan vardiya",
  "tip":          "solve" | "evaluate" | "backend",
  "sahne":        "_sahne-S10.json",
  "kabul_olcutu": "../KABUL-OLCUTLERI.md#a4--gece-yarısını-aşan-vardiya",
  "fark":         { ... },
  "beklenen":     { ... }
}
```

Beş alan zorunlu: `senaryo`, `ad`, `tip`, `sahne`, `kabul_olcutu`.

`kabul_olcutu` **gerçekten var olan bir başlığa** işaret etmek zorunda —
denetleyici kontrol ediyor. Bir senaryo yeniden adlandırılırsa bağ kopar ve
sessiz kalmaz.

`_` ile başlayan her anahtar **yorumdur**, denetleyici onları yok sayar.
Açıklama yazmak için kullanılır; JSON yorum desteklemediği için.

## 4. Üç tip

### `evaluate` — plan elle verilir, denetlenir

`atamalar` dizisi zorunlu. `beklenen` içinde `sert_ihlal_sayisi`, `ihlaller`,
`yumusak_ihlaller` bulunur. **Denetleyici bu listeyi girdiden yeniden türetip
karşılaştırır** — yani beklenen blok ile girdi birbirinden kayarsa yakalanır.

A8'de olduğu gibi birden çok alt durum varsa `alt_durumlar` dizisi kullanılır;
her alt durum kendi `fark`ını ve `atamalar`ını taşıyabilir.

### `solve` — motor plan üretir

Beklenen sonuç bir **özelliktir**, girdiden türetilemez: "çözüldü", "sert ihlal
0", "hedef kapsama ≥ %95". `beklenen` içinde `durum`, `metrikler`,
`cozum_istatistikleri` ve bir `degismezler` listesi bulunur.

`degismezler`, testin motorun çıktısında **ayrıca** kontrol edeceği
iddialardır — her biri bir `kontrol` adı taşır (`calisan_gun_atamasi_yok`,
`ardisik_gun_en_fazla`, `evaluate_ile_sifir_sert_ihlal` gibi). Bu kontrollerin
gövdesi test iskeletinde yazılacak.

### `backend` — davranış testi

Motor girdi/çıktısı değil, sistemin davranışı sınanır. `adimlar` ya da
`alt_durumlar` dizisi; her biri `kurgu`, `eylem`, `beklenen` taşır.
xUnit tarafında koşacak.

## 5. Karşılaştırma sözdizimi

Sayısal beklentiler tek bir değer yerine karşılaştırma nesnesi olabilir:

```
"sert_ihlal":          { "esit": 0 }
"hedef_kapsama_yuzde": { "en_az": 95 }
"mumkun":              { "en_fazla": 10 }
```

Böylece "%95 ve üstü kabul" (K-8) gibi kararlar fikstürde **doğrudan** durur,
test kodunda gizlenmez.

## 6. Denetleyici

```
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\v5
py fikstur-denetleyici.py
```

Altı kontrol: yapı, sahne çözümü, referans bütünlüğü, kabul ölçütü çapası,
`turetilmis_degerler`, ve `evaluate` tipinde beklenen ihlal listesi.

**Denemesi yapıldı (15 Eylül):** dört fikstür kasten bozuldu — bir vardiyanın
saati kaydırıldı, bir çapa bozuldu, olmayan bir çalışan yazıldı, tanınmayan bir
tip verildi. Dördü de ayrı kontrol tarafından yakalandı, çıkış kodu 1 döndü.
Beklenen ihlal listeleri de ayrıca sınandı: sert ve yumuşak listeler
bozulduğunda ikisi de yakalandı.

⚠ **Denetleyici `solve` ve `backend` fikstürlerinde beklenen sonucu
doğrulayamaz** — orada beklenen bir özelliktir, girdiden türetilemez. Onlarda
yalnız yapı, referans ve çapa bakılır. Asıl doğrulama motor ve backend
yazıldığında testlerin kendisiyle olur.

## 7. Bilerek yapılmayanlar

| Ne | Neden |
|---|---|
| Fikstürlerde UUID yok, `C01`/`E1` gibi okunur kimlikler var | İnsan okuyacak; gerçek UUID'ler test kurulumunda üretilir |
| `solve` fikstürlerinde beklenen **plan** yok | Motor birden çok geçerli plan üretebilir; test **özellikleri** sınar, belirli bir planı değil (§11.7: tekrarlanabilirlik garanti edilmiyor) |
| A5 fikstürü yok | K-12, ertelendi |
| Beklenen metrik değerleri kesin sayı değil, aralık | K-8: %100 sözü verilmiyor |
