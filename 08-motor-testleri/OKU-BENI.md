# 08-motor-testleri — Altın senaryolar (Master Spec §16.3, A1–A12)

**Ne var:** Şartnameden türetilmiş kabul senaryoları. Motorun ne yapması
gerektiğini, motor yazılmadan **önce** ve motora bakmadan tanımlar.

**Ne YOK:** Motor yok. Ürünün doğrulayıcısı da yok. Analiz betikleri de burada
değil (onlar `07-motor/`'da ve onlar da motor değil — bkz.
`07-motor/OKU-BENI.md`).

**Neden ayrı klasör (karar: 14 Eylül 2026):** `07-motor/` adı yanıltıcı ve
yeniden adlandırma kararı bekliyor; senaryolar oraya karışmasın. Motor gelince
fikstürleri koşacak test iskeleti de buraya gelir.

## Sürümler

| Klasör | Durum | İçerik |
|---|---|---|
| `v1/` | **DONDURULDU** | İlk taslak. 12 senaryonun kabul ölçütleri + 7 açık soru (S-1…S-7). Tarihsel kayıt; değiştirilmez. |
| `v2/` | **Güncel — cümle onayı bekliyor** | v1'in soruları Mustafa tarafından cevaplandı (K-1…K-7) ve işlendi. Ayrıca v1'deki bir hesap hatam düzeltildi (A4'te brüt/net karışmıştı). Örnek fikstür + fikstür denetleyicisi eklendi. |

Versiyonlama kuralı: onaylanmış ya da devredilmiş bir sürüm **değiştirilmez**;
değişiklik yeni klasör açar.

## v2 içeriği

| Dosya | Ne |
|---|---|
| `v2/KABUL-OLCUTLERI.md` | **Ana doküman.** 12 senaryo, her biri için somut veri + "doğru çalışıyorsa ne görmeliyiz" cümleleri + kaynak etiketi. Ayrıca kapanan kararlar, v1.4'e taşınacak şartname maddeleri, veto edilebilir varsayımlar. |
| `v2/fikstur/A04.json` | **Örnek fikstür** — biçimi göstermek için. Kod değil veri; motor hangi dille yazılırsa yazılsın aynı dosya koşar. Diğer 11'i onaydan sonra yazılır. |
| `v2/fikstur-denetleyici.py` | Fikstürün **kendi içinde** tutarlı olduğunu kontrol eder: yazılı beklenen ihlal listesi girdiden gerçekten çıkıyor mu. **Ürünün doğrulayıcısı değildir** — dosya başındaki uyarıya bak. |

## Çalıştırma

```
py -3 --version
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\v2
py fikstur-denetleyici.py
```

Beklenen çıktı:

```
[TAMAM]    A04.json  (8 atama, 2 varyant)

1/1 fikstur tutarli.
```

Fikstürün girdisi ile beklenen bloğu birbirinden kayarsa `[TUTARSIZ]` yazar ve
çıkış kodu 1 döner. *(Denendi: A4'te bir vardiyanın saati bir saat kaydırıldı,
denetleyici üç ayrı tutarsızlığı da yakaladı.)*

## Nasıl kullanılır

1. `v2/KABUL-OLCUTLERI.md` §5'teki kararların doğru anlaşıldığını kontrol et —
   özellikle **K-1** (sınır değerler) hakkındaki not.
2. Her senaryonun "Doğru çalışıyorsa ne görmeliyiz" cümlelerini onayla ya da
   düzelt. `[çıkarım]` etiketli maddeler yapay zekânın yorumu — oralara dikkat.
3. §7'deki dört varsayımı (V-1…V-4) veto etme fırsatın var.
4. Onaydan sonra kalan 11 fikstür ve pytest iskeleti yazılır. Motor yazılana
   kadar testler **kırmızı** kalır; istenen durum bu (§16.4 kırmızı kanıt).
