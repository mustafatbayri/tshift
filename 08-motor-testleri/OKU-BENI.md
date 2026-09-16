# 08-motor-testleri — Altın senaryolar (Master Spec §16.3, A1–A12)

**Ne var:** Şartnameden türetilmiş kabul senaryoları. Motorun ne yapması
gerektiğini, motor yazılmadan **önce** ve motora bakmadan tanımlar.

**Ne YOK:** Motor yok. Ürünün doğrulayıcısı da yok. **Hiçbir test koşmuyor.**
Analiz betikleri de burada değil (onlar `07-motor/`'da ve onlar da motor
değil — bkz. `07-motor/OKU-BENI.md`).

**Neden ayrı klasör (karar: 14 Eylül 2026):** `07-motor/` adı yanıltıcı ve
yeniden adlandırma kararı bekliyor; senaryolar oraya karışmasın. Motor gelince
fikstürleri koşacak test iskeleti de buraya gelir.

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
| `v5/KABUL-OLCUTLERI.md` | **Ana doküman.** §1 onayın ne olduğu · §3 sahne (S-10) · §4 on iki senaryo · §5 veto edilebilir varsayımlar · §6 kararlar K-1…K-15 · §7 onay nasıl verilir |

⚠ **v4'te fikstür yok.** `v3/fikstur/A04.json` **geçersiz** oldu: eski sahneye
(T-10) dayanıyor ve geri alınan K-1'e göre yazılmıştı. Biçim örneği olarak
duruyor, beklenen sonuçları kullanılmayacak. Yeni fikstürler onaydan sonra
yazılacak.

`v3/fikstur-denetleyici.py` kullanılabilir durumda: fikstürün girdisi ile
beklenen bloğunun birbirinden kaymadığını kontrol eder. **Ürünün doğrulayıcısı
değildir** — dosya başındaki uyarıya bak.

## Sıradaki adım

> **Fikstürler.** `v5/fikstur/A01.json … A12.json` (A5 hariç, 11 dosya),
> sonra pytest iskeleti (A1–A9) ve xUnit testleri (A10–A12). Motor olmadığı
> için hepsi **kırmızı** başlar; istenen durum bu (§16.4 kırmızı kanıt).
>
> Paralelde: şartname **v1.4** (liste `v5/KABUL-OLCUTLERI.md` §8'de) ve
> iki maddenin **hukuk teyidi**.
>
> Onaydan sonra kalan 11 fikstür ve pytest iskeleti yazılır. Motor yazılana
> kadar testler **kırmızı** kalır; istenen durum bu (§16.4 kırmızı kanıt).
