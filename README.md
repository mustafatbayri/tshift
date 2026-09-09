# TShift — çalışma kökü

Teknovisor'un çok kiracılı yapay zekâ destekli vardiya planlama ve optimizasyon ürünü.
Bu klasör projenin **tek doğru kaynağı**: analiz, testler, spec, demo ve kod hepsi burada.

---

## Klasörler

| Klasör | İçinde ne var |
|---|---|
| `00-arsiv/` | Artık kullanılmayan ama saklanan işler. Eski demolar, eski dokümanlar. Silinmez, buraya taşınır. |
| `01-spike/` | Motorun ar-ge testleri. Her test turu kendi versiyon klasöründe. |
| `02-spec/` | Ürün ve teknik spec dokümanları. Yazılım ekibinin okuyacağı asıl kaynak. |
| `03-demo/` | Tıklanabilir prototipler. Kodlamadan önce akışı doğrulamak için. |
| `04-kod/` | Gerçek yazılım. Henüz boş. |
| `DEGISIM-GUNLUGU.md` | Ne zaman ne değişti — tek satırlık kayıtlar. Bir şey aradığında önce buraya bak. |

---

## Çalışma kuralı: dosya güncellenmez, versiyon açılır

Bir şeyi değiştirdiğimizde **eski dosyanın üzerine yazmıyoruz.** Yeni bir versiyon
klasörü açıp değişikliği orada yapıyoruz. Sebebi basit: üç hafta sonra "biz bunu neden
böyle yapmıştık" sorusunun cevabı ancak eski hâli duruyorsa verilebilir.

Versiyon adı şu biçimde: `v<numara>-<tarih>-<kısa ad>`

```
01-spike/v1-2026-09-09-fizibilite/
01-spike/v2-2026-09-20-esneklik/
02-spec/v1.0-master-spec.md
03-demo/v2-html/
```

Her yeni versiyon açıldığında `DEGISIM-GUNLUGU.md` dosyasına bir satır eklenir.
Bir versiyonun içindeki `README.md` o versiyonda **ne denendiğini ve ne çıktığını** anlatır.

---

## Ürün bir cümleyle

Bir işletmenin çalışanlarını, iş kanununu, şirket kurallarını ve beklenen iş yükünü
girdi alarak; kimin ne zaman çalışacağını belirleyen haftalık vardiya planını üreten,
üç farklı önceliğe göre üç alternatif sunan, yönetici plana müdahale ettiğinde
sonuçlarını hesaplayıp öneri getiren bir SaaS.

Ayrıntı için: `02-spec/`

---

## Şu an neredeyiz

| Konu | Durum |
|---|---|
| Planlama motoru | Test edildi, çalışıyor (`01-spike/`) |
| Kural seti | 21 kural aktif, 6 kural havuzdan seçildi, karar föyüyle onaylandı |
| Teknoloji kararları | Verildi (PostgreSQL · .NET 10 · Python motor · Next.js · RabbitMQ · Keycloak) |
| Master spec | Yazılıyor |
| Demo v2 | Spec bittikten sonra |
| Kod | Başlamadı |
