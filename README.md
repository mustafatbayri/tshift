# TShift — çalışma kökü

Teknovisor'un çok kiracılı yapay zekâ destekli vardiya planlama ve optimizasyon ürünü.
Bu klasör projenin **tek doğru kaynağı**: analiz, testler, spec, demo ve kod hepsi burada.

---

## Klasörler

| Klasör | İçinde ne var |
|---|---|
| **`00-DEVIR/`** | **Buradan başla.** Devir paketi: proje kimliği, değişmezler, mimari ve ürün kararları, test haritası, hata otopsileri, açık riskler, oturum günlükleri. |
| `00-arsiv/` | Artık kullanılmayan ama saklanan işler. Eski demolar, eski dokümanlar. Silinmez, buraya taşınır. |
| `01-spike/` | Motorun ar-ge testleri. Her test turu kendi versiyon klasöründe. |
| `02-spec/` | Ürün ve teknik spec dokümanları. **Güncel: `v1.4-master-spec.md`** — yazılım ekibinin okuyacağı asıl kaynak. |
| `03-demo/` | Tıklanabilir prototipler. Kodlamadan önce akışı doğrulamak için. |
| `04-kod/` | Gerçek yazılım: .NET API + Next.js arayüz + PostgreSQL. Çalışıyor. |
| `05-inceleme/` | Dış inceleme işleri. `05-inceleme/beceriler/` altında **incelemenin nasıl yapılacağı** yazılı. |
| `06-veri/` | Gerçek müşteri verisi. **Git'e gitmez** (gitignore). |
| `07-motor/` | Gerçek veri analiz araçları. ⚠ Motor burada **değil**. |
| `08-motor-testleri/` | Altın senaryolar ve fikstürler. Güncel sürüm `08-motor-testleri/v5/`. |
| **`09-motor/`** | **Planlama motoru.** `09-motor/dogrulayici/` · `09-motor/cozucu/` (CP-SAT) · `09-motor/orkestra.py`. |
| `DENETIM.py` | Devir paketi denetim betiği. Her oturum sonunda koşar: `py DENETIM.py` |
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

> ⚠ **Bu bölüm 23 Eylül'de düzeltildi.** Aylardır bayattı: *"kod başlamadı"*
> yazıyordu, `04-kod/` çalışıyor. Otopsisi `00-DEVIR/06-ACIK-RISKLER.md` · T-37.
> Ayrıntılı ve güncel durum her zaman **`00-DEVIR/00-BURADAN-BASLA.md`**'dedir;
> bu tablo yalnız kabaca yön verir.

| Konu | Durum *(23 Eylül 2026)* |
|---|---|
| Master spec | ✅ **v1.4 bitti** — 17 bölüm, 35 kural sınıflandırıldı |
| Backend (`04-kod/`) | ✅ Çalışıyor — 39 test, çok kiracılık (RLS), yetki, denetim kaydı |
| Planlama motoru (`09-motor/`) | 🟡 **Çekirdek çalışıyor** — 68 birim testi, 7 altın senaryo. Kataloğun 35 kuralının 19'u yazılı |
| CI kapısı | ✅ GitHub Actions — iki iş (backend + motor), yeşil |
| Dış inceleme | 🔴 **19 bulgu kayıtlı, 8'i açık** (T-18…T-36) |
| `/suggest` ucu, plan editörü, yönetim ekranları | ❌ Yazılmadı |
| Demo v2 | ✅ `03-demo/v2-html/` — 15 ekran |

**Teknoloji:** PostgreSQL · .NET 10 · Python (OR-Tools CP-SAT) · Next.js.
*(Keycloak **elendi** — kimlik katmanı kendi kodumuzda, bkz. M-03. RabbitMQ
ertelendi.)*
