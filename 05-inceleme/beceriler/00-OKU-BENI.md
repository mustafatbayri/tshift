# İnceleme becerileri — dizin

**Ne bu klasör.** TShift'in **nasıl inceleneceğini** anlatan dosyalar. Projenin
ne olduğunu değil, incelemenin nasıl yapılacağını yazar.

> **Bağlam ile beceri ayrımı.** `00-DEVIR/` bağlamdır — ajanın *neyi bilmesi*
> gerektiğini söyler. Bu klasör beceridir — *işin nasıl yapılacağını* söyler.
> Beceriler modelden bağımsızdır: sağlayıcı değişse de geçerli kalırlar.

## İçindekiler

| Dosya | Ne zaman koşar | Kim koşar | Girdi |
|---|---|---|---|
| `01-dal-farki-incelemesi.md` | Haftalık taramanın **1. geçişi** | Farklı sağlayıcının modeli | O haftanın `git diff`'i + kabul cümleleri |
| `02-sartname-kod-taramasi.md` | Haftalık taramanın **2. geçişi** | Aynı | Şartname + deponun tamamı |
| `03-haftalik-dongu.md` | **Döngünün kendisi** — kim ne yapar, paket nasıl hazırlanır | — | — |

## Üç kural, ikisi için de geçerli

**1. İnceleyici yazmaz.** Dosya değiştirmez, commit etmez, komut çalıştırmaz
(okuma ve ölçüm dışında). R5 — *tek aktif yazıcı pencere* — bu sayede açılmaz.

**2. İnceleyici işi yapan olamaz.** Kodu yazan kendi işini denetlerse aynı
yanlış varsayım ikisine birden geçer (D-6). 16 Eylül'de bunun insan tarafındaki
hâli yaşandı: O-10.

**3. Bulgu ölçülebilir olmalı.** *"Şu yanlış olabilir"* bulgu değildir.
Bulgu, **nasıl üretileceği yazılmış** bir farktır. 16 Eylül'de gelen 19
bulgunun 19'u da koşturularak doğrulandı; hiçbiri tahmin değildi.

> **Erişim kuralı (O-10).** *"Bakamıyorum, o dosya bende yok"* demeden **önce
> erişim denenir.** Denenmemiş bir erişimin raporu bulgu değil tahmindir — ve
> tahmin, kaydedilirken bulgu gibi görünür.

## Ölçüm şartı — araç bırakılır mı

Her incelemenin ne bulduğu `00-DEVIR/06-ACIK-RISKLER.md`'ye yazılır.

> **Arka arkaya üç incelemede kayda değer bulgu çıkmazsa, o incelemenin
> sıklığı düşürülür** — bırakılmaz, seyrekleşir.

Gerekçe O-7: *yanlış alarm veren araç, bir süre sonra bakılmayan araca
dönüşür.* Getirisi düşen bir incelemenin ritüele dönüşmesi de aynı kapıya
çıkar. İki inceleme **ayrı ayrı** ölçülür; biri seyrekleşirken diğeri
sıklığını koruyabilir.
