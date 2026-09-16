# 08-motor-testleri — Altın senaryolar (Master Spec §16.3, A1–A12)

**Ne var:** Şartnameden türetilmiş kabul senaryoları. Motorun ne yapması
gerektiğini, motor yazılmadan **önce** ve motora bakmadan tanımlar.

**Ne YOK:** Motor yok. Ürünün doğrulayıcısı da yok. **Testler koşuyor ama
yedisi bilerek kırmızı** — motor olmadığı için (§16.4 kırmızı kanıt).
Analiz betikleri de burada değil (onlar `07-motor/`'da ve onlar da motor
değil — bkz. `07-motor/OKU-BENI.md`).

**Neden ayrı klasör (karar: 14 Eylül 2026):** `07-motor/` adı yanıltıcı ve
yeniden adlandırma kararı bekliyor; senaryolar oraya karışmasın. Fikstürleri
koşan test iskeleti de 16 Eylül'de buraya geldi: `v5/testler/`.

## Buradan başla

| Kimsen | Neyi oku |
|---|---|
| **Mustafa** | `v5/KABUL-OLCUTLERI.md` — onaylanmış hâli. Turun özeti `ONAY-DURUMU.md`'de — §1 neyi onayladığını anlatır, §4'te 12 senaryo iş diliyle. Teknik bloklar katlanmış, atlayabilirsin. |
| **Yazılım tarafı** | Aynı dosya; "Teknik karşılık" blokları + `00-DEVIR/08-URUN-KARARLARI.md` K-serisi |

## Sürümler

| Klasör | Durum | İçerik |
|---|---|---|
| `v1/` | **DONDURULDU** | İlk taslak + 7 açık soru (S-1…S-7). Tarihsel kayıt. |
| `v2/` | **DONDURULDU** | Soruların cevapları işlendi (K-1…K-7). Ayrıca v1'deki bir hesap hatam düzeltildi (A4'te brüt/net karışmıştı). Örnek fikstür ve fikstür denetleyicisi burada doğdu. |
| `v3/` | **DONDURULDU** | İçerik v2 ile aynı, anlatım iş diline çevrildi. Mustafa'nın geri bildirimi bu sürüm üzerine geldi. |
| `v4/` | **DONDURULDU** | Mustafa'nın 15 Eylül geri bildirimi işlendi: sahne gerçekçi hâle getirildi, A2/A3/A7/A8 baştan yazıldı, K-1 geri alındı, A5 ertelendi. Onay turu bu sürüm üzerine yapıldı. |
| `v5/` | ✅ **ONAYLANDI — güncel** | Onay turunun ekleri işlendi: yayın kapısı (K-16), `yasal` bayrağı (K-17), mola kapsaması yumuşak, altı varsayımın tamamı karara bağlandı. **Fikstür yazımı bu sürümden ilerler.** |

Versiyonlama kuralı: dondurulmuş bir sürüm **değiştirilmez**; değişiklik yeni
klasör açar. Her sürüm klasörü kendi kendine yeter.

## İçerik

| Dosya | Ne |
|---|---|
| `ONAY-DURUMU.md` | 15 Eylül onay turunun **özeti.** Tur kapandı, ekler v5'e işlendi. Bir sonraki tur bu dosyayı baştan doldurur |
| `v5/KABUL-OLCUTLERI.md` | **Ana doküman.** §1 onayın ne olduğu · §3 sahne (S-10) · §4 on iki senaryo · §5 veto edilebilir varsayımlar · §6 kararlar K-1…K-17 · §7 onay nasıl verilir |
| `v5/fikstur/` | ✅ **11 fikstür + ortak sahne.** Biçim ve gerekçeler `v5/fikstur/OKU-BENI.md`'de |
| `v5/testler/` | ✅ **Test iskeleti.** pytest çatısı + `v5/testler/backend-taslak/` C# taslakları. Kırmızı; sebebi `v5/testler/OKU-BENI.md`'de |
| `v5/fikstur-denetleyici.py` | Fikstürlerin kendi içinde tutarlı olduğunu kontrol eder (6 kontrol). **Ürünün doğrulayıcısı değildir** |
| `v5/fikstur_yukleyici.py` | Sahne + `fark` birleştirme. Denetleyici ile testler **aynı** mantığı kullansın diye ortak modül |

⚠ **v2/v3'teki `A04.json` geçersiz** — eski T-10 sahnesine dayanıyor ve geri
alınan K-1'e göre yazılmıştı. Yalnız tarihsel kayıt; kullanılmaz. Geçerli
fikstürler `v5/fikstur/` altında.

## Sıradaki adım

> ✅ **Fikstürler yazıldı** (16 Eylül) — 11 dosya + ortak sahne, hepsi
> denetleyiciden geçiyor.
>
> **Sıradaki: test iskeleti.** pytest (A1–A9) ve xUnit (A10–A12). Motor
> olmadığı için hepsi **kırmızı** başlar; istenen durum bu (§16.4 kırmızı
> kanıt). `degismezler` bloklarındaki `kontrol` adlarının gövdesi orada yazılır.
>
> Paralelde: şartname **v1.4** (A-15) ve iki maddenin **hukuk teyidi** (A-16).
>
> Onaydan sonra kalan 11 fikstür ve pytest iskeleti yazılır. Motor yazılana
> kadar testler **kırmızı** kalır; istenen durum bu (§16.4 kırmızı kanıt).
