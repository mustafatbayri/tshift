# Backend taslakları — OKU-BENİ

**Klasör:** `08-motor-testleri/v5/testler/backend-taslak/`
**İçerik:** `AltinSenaryolarTestleri.cs.taslak` — 20 xUnit testi, hepsi taslak
**Durum:** ⛔ Derlenmiyor ve **derlenmemeli**

---

## 1. Neden `.cs` değil de `.cs.taslak`?

Bu testlerin dayandığı veritabanı tabloları henüz **yok**:

| Gereken | Var mı | Hangi testler bekliyor |
|---|---|---|
| `plans`, `plan_runs` | ❌ | A10, A11, A12 |
| `plan_violations` (+ `kabul_edildi` durumu) | ❌ | A12, K-16 |
| `leaves.durum` alanı | ❌ | A2 |
| `rules.yasal` alanı | ❌ | K-16, K-17 |
| Lookback hazırlık kontrolü | ❌ | A11 |

Dosya `.cs` uzantısıyla `04-kod/backend/tests/` altına konsaydı derleyici onu
görür, `TestUygulamasi` gibi olmayan tiplere takılır ve **derleme hatası**
verirdi. Derleme hatası = CI kırmızı = A-4 kapısı kapalı = "main her zaman
yeşil" kuralı bozuldu.

Uzantı bilerek bozuk. Proje ağacına girse bile derleyici görmez, CI'ı
kırmaz, ama içerik kaybolmaz.

**Bu, eksikliği gizlemek değil** — tam tersi. Testler yazılı, ne bekledikleri
yazılı, hangi tablonun eksik olduğu yazılı. Yalnız henüz koşamıyorlar.

---

## 2. İçindeki 20 test

### `AltinSenaryoA10Testleri` — Aynı isteği iki kez gönderme (§11.7)

| # | DisplayName |
|---|---|
| 1 | `A10 - Ayni istek anahtariyla tekrar cagirinca yeni plan uretilmez` |
| 2 | `A10 - Calisma surerken gelen ayni anahtar ikinci calismayi baslatmaz` |
| 3 | `A10 - Farkli istek anahtari yeni calistirma baslatir` |
| 4 | `A10 - Istek anahtari kiraciya ozeldir, baska firmanin sonucu donmez` |

4. test kritik: istek anahtarı **kiracıya özel** olmalı. Değilse iki firma aynı
anahtarı kullandığında biri diğerinin planını görür — kiracı sızıntısı.

### `AltinSenaryoA11Testleri` — Geçmiş hafta eksikse (§11.2)

| # | DisplayName |
|---|---|
| 5 | `A11 - Lookback penceresinde eksik hafta varsa motor cagrilmaz` |
| 6 | `A11 - Eksik hafta kullaniciya tarihleriyle soylenir ve kopyalama onerilir` |
| 7 | `A11 - Eksik hafta girilince hazirlik gecer ve motor cagrilir` |
| 8 | `A11 - Hic yayinlanmis plani olmayan firmada motor calisir` |

8. test senin kararın: "geçmiş yok" ölçütü = firmanın **ilk yayınlanmış planı**.
Yeni müşteri ilk planını hiçbir uyarı görmeden üretebilmeli.

### `AltinSenaryoA12Testleri` — Plan kopyalama (§9.7)

| # | DisplayName |
|---|---|
| 9 | `A12 - Plan kopyalanirken dogrulayici kosar, cozucu kosmaz` |
| 10 | `A12 - Dusen atamalar sebebiyle birlikte tek tek listelenir` |
| 11 | `A12 - Kopyada kapsama bozulursa ihlal gosterilir, sessizce doldurulmaz` |
| 12 | `A12 - Kopya taslak olur ve kaynak plan degismez` |

11. test senin "sessizce doldurma" endişenin karşılığı: kopyada boşluk oluşursa
sistem kendi kafasına göre birini atamaz, boşluğu **gösterir**.

### `AltinSenaryoA02Testleri` — İzin her şeyi ezer (K-9)

| # | DisplayName |
|---|---|
| 13 | `A2 - Onayli izni olan calisan plana sabitlenemez` |
| 14 | `A2 - Sonradan onaylanan izin calisani plandan dusurur ve bildirim gider` |
| 15 | `A2 - Iptal edilen izin calisani yeniden atanabilir yapar` |
| 16 | `A2 - Izinli kisiye sabit atama iceren girdi motorda da plan uretmez` |

14. test senin cümlen: *"yönetici plana girdiğinde, Ayşe'nin silindiğini izin
sebebiyle görmeli ve asistan ona öneri vermelidir."*
16. test **savunma hattı**: backend izinliyi engellemeyi unutsa bile motor da
reddetmeli. İki kapı, tek kilit değil.

### `YayinKapisiTestleri` — Yayın kapısı (K-16, K-17)

| # | DisplayName |
|---|---|
| 17 | `K16 - Yasal kural ihlali olan plan yayinlanamaz ve kabul secenegi sunulmaz` |
| 18 | `K16 - Firma kurali ihlali kabul edilirse plan yayinlanabilir` |
| 19 | `K16 - Yasal bayragi belirsiz olan kural yasal gibi davranir` |

Senin kuralın: *"Yasal kuralların ihlali kabul edilemez ama firma kuralı ihlali
kabul edilebilir."*
19. test güvenli varsayılan: emin olmadığımız kural yasal sayılır (K-17).
Yanlış tarafta hata yapmak isterse, **kısıtlayıcı** tarafta yapsın.

---

## 3. Bunları gerçek teste çevirmek

Tabloları yazdıktan sonra:

1. Dosyayı `04-kod/backend/tests/TShift.Tests/` altına taşı
2. Adını `AltinSenaryolarTestleri.cs` yap
3. `TestUygulamasi` sınıfını mevcut test altyapısına bağla
4. `NotImplementedException` gövdelerini doldur
5. `.\TEST.ps1` çalıştır → **testler kırmızı yanmalı** (spec §16.4)
6. Backend'i yaz → yeşile dönsün
7. `00-DEVIR/04-TEST-HARITASI.md` ve `02-DEGISMEZLER.md` sayılarını güncelle
8. `py DENETIM.py` çalıştır → test adları belgeyle eşleşiyor mu

> ⚠ 5. adım atlanmamalı. Doğrudan yeşil yanan bir test, aslında hiçbir şeyi
> sınamıyor olabilir ve bunu asla anlayamayız.

---

## 4. Test adı kuralı

`DisplayName` **saf ASCII** ve belgede geçen adla **birebir aynı** olmalı.

`DENETIM.py` (kontrol 1) belgelerde geçen test adlarını koddaki
`DisplayName` değerleriyle karşılaştırıyor. Kısaltılmış, Türkçe karakterli
veya yeniden yazılmış bir ad orada **hata** olarak çıkar. Bu, "belgede
yazan test aslında yok" durumunu engelleyen tek mekanizma.

---

## 5. Kaynaklar

- `../../KABUL-OLCUTLERI.md` — §4 A2, A10, A11, A12
- `../../fikstur/A02.json`, `A10.json`, `A11.json`, `A12.json` — beklenen davranış
- `00-DEVIR/08-URUN-KARARLARI.md` — K-5, K-9, K-15, K-16, K-17
- `00-DEVIR/06-ACIK-RISKLER.md` — A-15 (spec v1.4: eksik alanlar burada)
