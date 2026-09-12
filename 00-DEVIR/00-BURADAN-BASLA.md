# BURADAN BAŞLA

> **Yeni bir sohbet penceresi ya da başka bir yapay zekâ isen: önce bu sayfayı
> baştan sona oku, sonra aşağıdaki okuma sırasını takip et. Kod yazmaya
> başlamadan önce `02-DEGISMEZLER.md` dosyasını mutlaka okumuş olmalısın.**

**Son güncelleme:** 2026-09-12
**Son sürüm etiketi:** `v0.8-devir`
**Depo:** `github.com/mustafatbayri/tshift` (özel) · yerel kök: `C:\Users\PC\Desktop\Tshift`

---

## 1. Bu proje nedir, tek paragrafta

**T-Shift**, çok kiracılı (multi-tenant) bir yapay zekâ destekli vardiya
planlama ve optimizasyon SaaS ürünüdür. Teknovisor markası altında
geliştiriliyor. Ürün sahibi ve tek karar verici **Mustafa**: 11 yıllık BT ürün
müdürü, **yazılımcı değil** — kod yazmıyor, kod okumuyor. Bütün kod yapay zekâ
tarafından yazılıyor, Mustafa niyeti ve iş kurallarını doğruluyor.

Bunun iki pratik sonucu var ve ikisi de bu projedeki her kararı şekillendiriyor:

1. **Mustafa'ya kod gösterilerek onay alınamaz.** Doğrulama, testlerin ve
   dokümanların Türkçe iş cümlelerine çevrilmesiyle olur.
2. **Yapay zekâ kendi hatasını göremez.** Bu yüzden bu projede kurallar
   yazıya değil, **otomatik kontrollere** bağlanır. Detay: `05-HATA-OTOPSILERI.md`.

---

## 2. Şu anda neredeyiz

**Dikey dilim tamamlandı.** Veritabanından ekrana kadar bütün katmanlar bağlı
ve çalışıyor:

```
PostgreSQL + RLS → EF Core → Kimlik → Yetki/Kapsam → Denetim kaydı → API → Next.js arayüz
```

- **39/39 test yeşil.** Hepsi gerçek PostgreSQL'e karşı koşuyor, hiç mock yok.
- **Tek komutla ayağa kalkıyor:** `docker compose --profile tam up --build`
- **Çalışan ekranlar:** giriş, çalışan listesi (rol bazlı farklı davranıyor),
  yeni çalışan kaydı.
- **Yılmaz'a inceleme paketi gönderildi** (`05-inceleme/v1-2026-09-11/`).

**Henüz yazılmadı:** vardiya optimizasyon motoru, plan editörü, kural yönetimi,
kullanıcı/rol yönetim ekranları, CI.

## 3. Sıradaki tek adım

> **CI'ı yeşile almak.** `.github/workflows/testler.yml` yazıldı ama **henüz
> bir kez bile koşmadı.** İlk `git push` ile koşacak. İlk denemede kırmızı
> yanabilir (CI ortamı burada denenemedi) — logu okuyup düzeltmek işin
> parçası, kötü işaret değil.
>
> **CI yeşile döner dönmez sıradaki:** CsCheck ile property-based testler —
> 14 boş senaryo sınıfının çoğunu kapatır ve motorun metamorfik testleri de
> aynı araçla yazılır. Araç kararının tamamı: `06-ACIK-RISKLER.md` içindeki
> "Araç kararı" bölümü.
>
> Sonra sırasıyla: Bruno koleksiyonu (Mustafa'nın kendi koşacağı API
> senaryoları) → Stryker mutasyon raporu (A-6) → zaman modeli testleri (A-5)
> → motor sözleşmesi (A-10, doğrulayıcı önce).
>
> Tam öncelik listesi: `06-ACIK-RISKLER.md` sonundaki tablo.

---

## 4. Okuma sırası

Aşağıdaki sıra, bir işe başlamadan önce ne kadar okuman gerektiğini söyler.
**Hepsini okumak zorunda değilsin** — yapacağın işe göre seç.

| Sıra | Dosya | Ne zaman okumalısın |
|---|---|---|
| 1 | Bu sayfa | Her zaman |
| 2 | `02-DEGISMEZLER.md` | **Her zaman.** Kod yazmadan önce mutlaka. |
| 3 | `01-PROJE-KIMLIGI.md` | Ürün kararı, kapsam ya da öncelik konuşulacaksa |
| 4 | `03-MIMARI-KARARLAR.md` | Mevcut bir yapıyı değiştirecek ya da yeni katman ekleyeceksen |
| 5 | `04-TEST-HARITASI.md` | Test yazacak ya da mevcut bir testi değiştireceksen |
| 6 | `05-HATA-OTOPSILERI.md` | Yeni bir savunma/kontrol tasarlayacaksan |
| 7 | `06-ACIK-RISKLER.md` | Yayına çıkma, ölçek ya da güvenlik konuşulacaksa |
| 8 | `oturumlar/` | Belirli bir değişikliğin ne zaman ve neden yapıldığını arıyorsan |

Depodaki diğer önemli dosyalar:

| Dosya | İçerik |
|---|---|
| `02-spec/v1.2-master-spec.md` | **Ürünün şartnamesi.** Kabul ölçütlerinin birincil kaynağı. |
| `DEGISIM-GUNLUGU.md` | Kilometre taşları, en yeni en üstte |
| `RISKLER-VE-ONLEMLER.md` | 15 hata sınıfı, savunma hatları, kırmızı çizgiler |
| `SURUMLEME.md` | Hata yapılırsa nasıl geri dönülür |
| `KALITE-ARASTIRMASI-DEGERLENDIRME.md` | Sahanın kalite pratiklerinin bizim projeye göre değerlendirmesi |
| `05-inceleme/` | Dış inceleme paketleri |

---

## 5. Bu dokümanların çalışma kuralı

Bu klasör bir **özet** değil, bir **devir paketidir**. İki farklı şey:

- Özet, benim yazdığım düz yazıdır. İçinde bir yanlış varsayım varsa sonraki
  pencereye sessizce taşınır ve orada doğru sanılır.
- Devir paketi **doğrulanabilir** olmak zorundadır. Bu yüzden buradaki her
  iddia ya bir **test adına**, ya bir **dosya yoluna**, ya da bir
  **çalıştırılabilir komuta** bağlıdır.

**Kural:** Bu klasöre, karşılığında çalıştırılabilir bir kanıt gösteremediğin
hiçbir cümle yazılmaz. Kanıtı olmayan bilgi `06-ACIK-RISKLER.md` altına,
"kanıtlanmamış" etiketiyle gider.

### Güncelleme ritüeli

Mustafa **"aktarım dosyasını güncelle"** dediğinde şunlar yapılır:

1. `oturumlar/YYYY-AA-GG.md` dosyası oluşturulur ya da eklenir — o oturumda
   **hangi dosya neden değişti, hangi test eklendi, hangi karar verildi.**
   Bu dosyalar **asla yeniden yazılmaz**, yalnız eklenir.
2. Değişen şeye göre `02`–`06` arası ilgili dosyalar güncellenir.
3. Bu sayfadaki **"Şu anda neredeyiz"** ve **"Sıradaki tek adım"** bölümleri
   yenilenir. Bu iki bölüm her zaman güncel olmak zorundadır — devir
   paketinin geri kalanı bu ikisi yanlışsa işe yaramaz.
4. `DEGISIM-GUNLUGU.md`'ye kilometre taşıysa satır eklenir, etiket atılır.

---

## 6. Yeni pencere için çalışma kuralları

Bu kurallar Mustafa ile üzerinde anlaşılmıştır; tartışmaya açık değil.

1. **Mustafa yazılımcı değildir.** Komutlar tam olarak, kopyalanıp
   yapıştırılacak şekilde verilir. "Şunu yapmalısın" değil, "şu komutu şu
   klasörde çalıştır" denir.
2. **Versiyonla, üzerine yazma.** Dosyalar güncellenerek değil,
   versiyonlanarak ilerler. Her kilometre taşı: git etiketi + değişim günlüğü
   satırı. Şartname değişikliği yeni bir sürüm dosyası olur.
3. **Kabul ölçütü önce.** Kod yazmadan önce "bu doğru çalışıyorsa ne
   görmeliyiz" cümlesi Türkçe yazılır ve Mustafa onaylar. Test o cümlenin
   çevirisidir.
4. **Bir hata bulunduğunda düzeltmek yetmez.** O hatanın bir daha sessizce
   geri gelmesini engelleyen kalıcı bir kontrol eklenir. Bu projenin işleyiş
   biçimi budur; örnekleri `05-HATA-OTOPSILERI.md`'de.
5. **Kırmızı çizgiler** `RISKLER-VE-ONLEMLER.md` §6'da. Okumadan veri, sır
   ya da migration konusuna dokunma.
6. **Anlaşılmayan komut çalıştırılmaz** — özellikle `rm`, `del`, `format`,
   `Remove-Item`, `--force` içerenler. Bu projede `git reset --hard` ve
   `git push --force` yasaktır.

---

## 7. Ortam gerçekleri — kaybedilen zamanın çoğu buradan geldi

Bunlar "bilinmezse tekrar tekrar saat kaybettiren" şeyler:

| Gerçek | Sonucu |
|---|---|
| Windows 11, **Windows PowerShell 5.1** (PowerShell 7 **değil**) | `.ps1` dosyaları **saf ASCII** olmalı (5.1 dosyayı ANSI okur, Türkçe karakter ayrıştırıcıyı bozar). `-SkipHttpErrorCheck` gibi PS7'ye özgü parametreler kullanılamaz. |
| `dotnet test` sırasında API çalışıyorsa DLL kilidi | Testler **`TEST.ps1`** ile koşulur — API'yi önce durdurur. Doğrudan `dotnet test` çağırma. |
| Docker bağlamına Windows `bin/`/`obj/` girerse restore bozulur | `04-kod/.dockerignore` var, silinmeyecek |
| PostgreSQL yerelde 5432'de olabilir | Kutu **5433**'te dinliyor |
| Mustafa'nın `.env.local` dosyasını uzak araçlar yazamıyor | O dosyayı Mustafa'nın kendisi oluşturur |

Kurulu sürümler: git 2.55 · .NET SDK 10.0.401 · Node 24.20 · npm 11.19 ·
Docker 29.7.2 · Python 3.14.7

---

## 8. Uygulamayı çalıştırma

**İnceleme kipi — her şey kutuda, tek komut:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose --profile tam up --build
```
→ `http://localhost:3000` · firma: `anadolu-cm` · parola: `TShift2026!Deneme`

**Geliştirme kipi — yalnız veritabanı kutuda:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose up -d
```

**Testler:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
.\TEST.ps1
```

**Yalıtım kanıtı (iki firma birbirini görüyor mu):**

```
.\YALITIM-KANITI.ps1
```
