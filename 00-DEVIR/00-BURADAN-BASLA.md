# BURADAN BAŞLA

> **Yeni bir sohbet penceresi ya da başka bir yapay zekâ isen: önce bu sayfayı
> baştan sona oku, sonra aşağıdaki okuma sırasını takip et. Kod yazmaya
> başlamadan önce `02-DEGISMEZLER.md` dosyasını mutlaka okumuş olmalısın.**

**Son güncelleme:** 2026-09-23 akşam (**dört 🔴 kapandı:** T-22, T-34, T-35, T-19. Motor **77 birim test** + **7 altın senaryo** yeşil; `.NET` 45/45; CI yeşil; `DENETIM.py` **0 hata**. Yeni kanal: `okunmayan_alanlar` — gönderilen ama okunmayan girdi alanı artık bildiriliyor. ⚠ Kapatma turları **dört yeni bulgu** açtı: T-38…T-41. **25 Eylül:** `SAGLIK_KISITI` kaldırıldı (K-21 geri alındı), katalog **34**; T-42 açıldı, T-43 aynı gün geri çekildi)
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

- **45/45 test yeşil.** Hepsi gerçek PostgreSQL'e karşı koşuyor, hiç mock yok.
  *(23 Eylül: T-34 ile üç sır testi eklendi — `S1`, `S2`, `S3`.)*
- **CI çalışıyor (14 Eylül), 16 Eylül'de motor da bağlandı.** Her `git push`
  sonrası **iki iş** koşuyor: `test` (.NET) ve `motor` (Python). Kurallar
  artık öneri değil **kapı**.
- **Tek komutla ayağa kalkıyor:** `docker compose --profile tam up --build`
- **Çalışan ekranlar:** giriş, çalışan listesi (rol bazlı farklı davranıyor),
  yeni çalışan kaydı.
- **Yılmaz'a inceleme paketi gönderildi** (`05-inceleme/v1-2026-09-11/`).

**Motor çekirdeği çalışıyor (16 Eylül).** Doğrulayıcı, çözücü ve onarım
döngüsü yazıldı; **yedi altın senaryo** (A1, A3, A4, A6, A7, A8, A9) ve o gün
60 birim testi yeşildi. **23 Eylül itibarıyla 77 birim testi**, CI'da da
yeşil.

⚠ **"Motor tamamlandı" demiyoruz, bilerek.** Kataloğun **34** kuralının 19'u
yazılı; A2/A10/A11/A12 backend tarafında ve hiç sınanmadı; aynı gün yapılan
**dış inceleme üç turda 19 bulgu** buldu, dokuzu 🔴 (T-18…T-36). Doğru
ifade: *belirli senaryoları çalışan bir motor çekirdeği var.*

**Dokuz 🔴'nın hepsi sessizdi:** hiçbiri kırmızı yanmıyordu, hepsi planı
temiz gösteriyordu.

**Beşi kapandı:** T-27 (16 Eylül) · T-22, T-34, T-35, T-19 (23 Eylül).

**Dördü açık:** geçmiş hafta hiç okunmuyor (**T-28**), *"geçmiş yeniden
planlanamaz"* sözünün tek bekçisi ateşlenemiyor (**T-29**), çok ekipli çalışan
iki ekibi aynı anda dolduruyor (**T-21**), denetlenmemiş kural yayını
engellemiyor (**T-18**).

⚠ **Kapatma turları dört yeni bulgu açtı — ve bu bir kural haline geldi.**
T-19'u kapatırken şartnamenin **on iki alanı daha** motorda karşılıksız çıktı
(**T-38** 🔴). ⚠ Bu kaydın ilk gerekçesi **yanlış yazılmıştı** ve 25 Eylül'de
düzeltildi; en ağır satır `izinler[].tum_gun`: **yarım günlük izin motora
gelmiyor**, motor bütün günü kapatıyor, yarım gün rapor alan kişi o gün hiç
planlanamıyor. Yanında
**T-39** 🟡 (aynı hücreye iki talep satırı tanımsız), **T-40** 🟡
(`tercih_karsilama_yuzde` şartnamede var, motorda yok — onu gerektirdiği
söylenen A7 onsuz yeşil) ve **T-41** 🟡 (`DENETIM.py` uyarılarının 13'ü
kalıcı). Açık 🔴 sayısı dörtten **beşe** çıktı.

> **Kaydedilen bulgu, bulgunun kendisi değildir.** T-34 iki satır sanılmıştı,
> 16 yer çıktı. T-35 kiracı çapı sanılmıştı, kurulum çapı çıktı. T-19'un üç
> ölçüsünün üçü de dardı. Bir bulguyu kapatmak, onu **ilk kez gerçekten
> ölçmek** demek.

**Henüz yazılmadı:** `/suggest` ucu (öneri üretimi, §11.5), plan editörü,
kural yönetimi, kullanıcı/rol yönetim ekranları.

**Gerçek müşteri verisi elimizde (13–14 Eylül).** Bir seyahat acentesinin 3,5
aylık PDKS ve vardiya planı. Analiz edildi, **529 kural ihlali** bulundu.
Bulgular ve Mustafa'nın kapsam kararları: **`07-GERCEK-VERI-BULGULARI.md`**
— motor yazılmadan önce okunmalı.

⚠ `07-motor/` klasöründe **motor yok**, analiz araçları var. Bkz.
`07-motor/OKU-BENI.md`.

**Fikstürler yazıldı (16 Eylül).** `08-motor-testleri/v5/fikstur/` — 11 JSON
dosyası + ortak sahne. Kod değil veri; motor hangi dille yazılırsa yazılsın
aynı dosyalar koşar. Biçim: `08-motor-testleri/v5/fikstur/OKU-BENI.md`.

**Test iskeleti yazıldı (16 Eylül).** `08-motor-testleri/v5/testler/` —
pytest çatısı (A1, A3, A4, A6, A7, A8, A9) ve xUnit taslakları (A2, A10, A11,
A12). Koşuyor ve **bilerek kırmızı**:

```
py -m pytest -q   →   7 failed, 4 passed, 5 skipped      (motor ADRESSIZ)
```

Motorsuz koşu **hâlâ kırmızı ve bu doğru** (§16.4 kırmızı kanıt): motor
adressizken testler yeşil yanıyorsa hiçbir şeyi sınamıyorlar demektir.
Yeşiller paketin **kendi** sağlık kontrolü: fikstürler yükleniyor mu, her
`kontrol` adının gövdesi var mı, motorun yokluğu açıkça söyleniyor mu.

✅ **"Motor gelince tek dosya değişecek" sözü tutuldu.** Doğrulayıcı yazıldı ve
yalnız `motor_istemci.py` değişti — testlerin, fikstürlerin ve kontrollerin
tek satırı değişmedi.

⚠ **Bu paket CI'da koşmuyor — bilerek.** CI şu an yalnız `dotnet test`
çalıştırıyor (A-4). Kırmızı bir paketi kapıya bağlamak "main her zaman yeşil"
kuralını bozardı. C# taslakları da bu yüzden `.cs.taslak` uzantılı —
derleyici görmez, CI kırılmaz. Ayrıntı: `08-motor-testleri/v5/testler/OKU-BENI.md`.

**MOTOR ÇEKİRDEĞİ ÇALIŞIYOR (16 Eylül) — yedi altın senaryo yeşil.**
`09-motor/` üç parçadan oluşuyor ve **üçü ayrı ayrı durur**:

| Parça | Ne yapar | Ne yapmaz |
|---|---|---|
| `09-motor/dogrulayici/` | Var olan planı kurallara karşı denetler | Plan üretmez |
| `09-motor/cozucu/` | CP-SAT ile plan üretir | Kendi ürettiğini denetlemez |
| `09-motor/orkestra.py` | İkisini üstten çağırır, §11.7 onarım döngüsünü koşar | Kural bilmez |

```
py servis.py   (ayri pencerede)
$env:TSHIFT_MOTOR_URL = "http://localhost:8000"
py -m pytest -q   →   12 passed, 4 skipped
```

Atlanan dört senaryo backend tarafında koşuyor (A2, A10, A11, A12);
A5 ertelendi (K-12).

| | Sayı | Ne zaman ölçüldü |
|---|---|---|
| Yazılan kural gövdesi | **19** (katalogdaki **34**'ün alt kümesi) | 25 Eylül, ikisi de sayılarak |
| Motor birim testi | **77**, hepsi yeşil | 23 Eylül |
| **Koşan** altın senaryo | **7** — A1, A3, A4, A6, A7, A8, A9 | 23 Eylül |
| Kırmızı kanıt | **12 kasten bozma, 12'si de yakalandı** | 16 Eylül |

⚠ **Bu tabloda 23 Eylül akşamına kadar iki yanlış sayı vardı.**
*"Altın senaryo 12, hepsi yeşil"* yazıyordu: `12 passed` sayısı **7 senaryo +
paketin kendi 5 sağlık testidir**; A2, A10, A11, A12 backend tarafında ve hiç
koşmadı. Bu düzeltme 16 Eylül'de `06-ACIK-RISKLER.md`'ye yazılmış ama **buraya
taşınmamış** — bir hafta burada yanlış durdu. Kural gövdesi de 17 yazıyordu,
sayılınca 19 çıktı.

> **T-37 ile T-26 aynı anda.** Giriş dokümanı hiçbir tazelik kontrolünün
> kapsamında değil (T-37), ve bir yerde yapılan düzeltme kendiliğinden
> yürürlüğe girmiyor (T-26). Bu tablo ikisinin kesişme noktasıydı.

⚠ **Kırmızı kanıtın ilk turu 8'de 4'ünü KAÇIRDI.** Kaçanlar: ağırlık tablosu
yok sayılsa, adalet gradyanı kaldırılsa, orkestra doğrulayıcıyı çağırmasa ya
da fazla mesai tavanı sabitlense **hiçbir test kırmızı yanmıyordu**. Eksik
testler o yüzden yazıldı (`09-motor/testler/test_profiller.py`). Kırmızı
kanıt turu olmasaydı bu dört boşluk sessizce kalırdı — turun varlık sebebi
tam olarak budur.

⚠ **Doğrulayıcı çözücüyle mantık paylaşmaz** (§7.6, §16.1). Çözücü yazılırken
*"aynı hesabı iki kez yazmayalım"* deyip ortak modül çıkarmak **yasaktır** —
tekrar burada maliyet değil, güvencedir.

**Sessiz geçmeme:** girdide aktif ama gövdesi yazılmamış bir kural varsa cevap
`uygulanmayan_kurallar` listesinde bunu açıkça söyler. *"İhlal bulamadım"* ile
*"bakmadım"* aynı şey değildir.

Ayrıntı: `09-motor/OKU-BENI.md`

**Şartname v1.4 yazıldı (16 Eylül).** `02-spec/v1.4-master-spec.md` —
**v1.3'e dokunulmadı**, yanına yazıldı. Ana değişiklik: kural kataloğu
`yasal` ve `kabul_edilebilir` sütunlarını kazandı. Bu olmadan iki onaylı karar
(K-10 kabul edilmiş ihlal, K-16 yayın kapısı) **uygulanamıyordu** — sistem
hangi ihlali kabul etmeye izin vereceğini bilemiyordu.

| Ne | Sayı |
|---|---|
| Sınıflandırılan kural | 16 Eylül'de **35** (v1.3 "27" diyordu, gerçek 33'tü) · **25 Eylül'den beri 34** — `SAGLIK_KISITI` kaldırıldı |
| Yeni kural | 1 — `GECE_POSTASI_DEVRI`. (`SAGLIK_KISITI` de eklenmişti, **25 Eylül'de geri alındı** — K-21) |
| Türü/değeri/anlamı değişen | 3 — `MOLA_KAPSAMASI` yumuşadı · `GUNLUK_AZAMI` 9→11 · `TERCIH_KARSILAMA` |
| Yeni veri alanı | 13 |
| Düzeltilen tutarsızlık | 11 (T-1…T-11) |
| Yeni ürün kararı | 9 (K-18…K-26) |

**Mevzuat araştırması yapıldı** (`02-spec/v1.4-hazirlik/`): iki belirsizlik
birincil kaynaklardan çözüldü, katalogda **olmayan bir yasal kural** bulundu
(`GECE_POSTASI_DEVRI`), ve gece 7,5 saat sınırının **turizm istisnası** ortaya
çıktı — ilk müşteri verisi bir seyahat acentesine ait olduğu için bu teorik
değil, ilk gün karşımıza çıkacak bir konu.

⚠ **Yasal sınıflandırma hukuk uzmanı tarafından teyit edilmedi** (A-16).
Madde numaraları birincil mevzuattan okundu, yorumlar yapay zekâya ait.

**Altın senaryolar ONAYLANDI (15 Eylül).** Spec §16.3'teki A1–A12'nin beklenen
sonuçları Türkçe kabul cümlelerine çevrildi ve Mustafa tarafından **tek tek
onaylandı**: `08-motor-testleri/v5/KABUL-OLCUTLERI.md` (dondurulmuş).
Onay turunda **on ürün kararı** doğdu (K-8…K-17), **bir karar geri alındı**
(K-1), dört senaryo ve ortak sahne **baştan yazıldı**.

✅ **Motorun ilk iki davranışı artık korunuyor (16 Eylül).** A4 (gece yarısını
aşan vardiya) ve A8 (öğle arası) yeşile döndü — kabul ölçütü bu iki senaryoda
taahhüt olmaktan çıkıp **bekçiye** dönüştü. Kalan on senaryo hâlâ taahhüt:
beşi çözücü bekliyor, dördü backend, biri (A5) ertelendi.

**Devir denetimi artık betik (14 Eylül) ve 16 Eylül'de İLK KEZ gerçekten
koştu.** `DENETIM.py` — bu paketteki test adlarını, sayıları, dosya yollarını,
sürüm atıflarını ve commit durumunu makineye kontrol ettirir.

İlk gerçek koşusunda **17 hata** buldu: iki dokümandaki 17 atıf hâlâ
dondurulmuş **v2** ve **v4** sürümlerini gösteriyordu. O düzeltmeler aslında
yapılmıştı ama makineye hiç gönderilmemişti — ve **dosya boyutu değişmediği
için** (`v2` ile `v5` aynı uzunlukta) hiçbir boyut kontrolü bunu yakalayamazdı.
Hepsi düzeltildi. Kalan 14 uyarı tarihsel dosyalarda.

⚠ **23 Eylül'de bu cümlenin kendisi bir bulguya dönüştü.** *"Aksiyon
gerektirmiyor"* doğru ama eksik: o 14 uyarı, iş düşen uyarılarla **aynı
listede** ve *"bakılmalı"* başlığı altında basılıyor. Her koşuda akan aynı 13
satır, uyarı bloğunu okunmaz hale getirir — ve o blokta bir gün gerçek bir şey
belirdiğinde görünmez. Kayıt: **T-41**.

⚠ **Her oturumun sonunda koşturulmalı.** Göz bu 17 satırı üç oturumdur
görmedi; betik ilk koşuşunda gördü.

**Çalışma biçimi kararı (15 Eylül).** Yazan pencerenin yanına **yazmayan** bir
gösterge penceresi açılıyor: günlükler sürekli, testler talep üzerine — §5b.
Paralel ikinci **yazıcı** ajan (opencode vb.) **reddedildi**; R5'i yeniden
açıyor. Salt-okunur inceleyici Aşama 2'ye ertelendi, ölçüm şartıyla.
**Ürün kodu değişmedi, test eklenmedi.** Gerekçe:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

## 3. Sıradaki tek adım

> **Dış incelemenin 🔴 bulguları — yeni özellikten önce.**
>
> 16 Eylül'de proje başka bir modele (GPT) şartnameyle birlikte **üç turda**
> incelettirildi. **19 bulgu** çıktı, hepsi bizim tarafımızda **ölçülerek**
> doğrulandı; ayrıca iki yanlış iddiamız düzeltildi. Dokuzu 🔴 ve **yeni iş
> bunların önüne geçmemeli.**
>
> **Sıralama ölçütü: yanlış karar riski.**
>
> | Sıra | Ne oluyor | Karar gerekiyor mu |
> |---|---|---|
> | ~~T-27~~ | ✅ **KAPANDI 16 Eylül** — mola artık vardiyaya kırpılıyor ve üst üste binenler birleştiriliyor. 8 test | — |
> | ~~T-35~~ | ✅ **KAPANDI 23 Eylül** — gerçek istemci IP'si + güvenilen vekil listesi. Etkisi kayıtta *kiracı* yazıyordu, **kurulum çapında** çıktı | — |
> | ~~T-34~~ | ✅ **KAPANDI 23 Eylül** — beş katmanda 16 yer; sır yoksa uygulama açılmıyor. Kırmızı kanıt `fix/t34-sirlar` dalında | — |
> | ~~T-22~~ | ✅ **KAPANDI 23 Eylül** — çözümsüzlükteki taslak artık **özgün** girdiyle denetleniyor; boş plan `var: False`. 4 test | — |
> | ~~T-19~~ | ✅ **KAPANDI 23 Eylül** — şartname biçimi kazandı; talep beş yerde hücre başına okunuyor. Yeni kanal `okunmayan_alanlar`. 5 test, **beşi de kırmızı yandı** | — |
> | **T-28** | `gecmis_vardiyalar` `09-motor/` içinde **hiç geçmiyor** — yasal dinlenme kuralı önceki haftaya kör | ✅ veri nereden gelecek |
> | **T-38** 🆕 | Şartnamenin **on iki alanı daha** karşılıksız. En ağırı `kural_degerleri`: kişiye özel sözleşme sınırı yok sayılıyor, günde 9 saatlik sözleşme 11 saate planlanabiliyor | ✅ hangisi önce yazılacak |
> | **T-29** | `DONMUS_GUN` yalnız `_yeni` işaretli atamada ateşleniyor, o işareti **kimse üretmiyor** | ✅ işareti kim koyacak |
> | **T-21** | Çok ekipli çalışan iki ekibi aynı anda dolduruyor — modelde ekip boyutu yok | ✅ bir vardiyada tek ekibe mi sayılır |
> | **T-18** | Gövdesi yazılmamış aktif SERT kural yayını engellemiyor. ⚠ Artık **üç** kanal bu kapıda bekliyor: `uygulanmayan_kurallar`, `eksik_boyutlar`, `okunmayan_alanlar` | ✅ kapı ne yapmalı |
>
> **Beş 🔴 açık ve beşi de Mustafa'nın cevabını bekliyor.** Mekanik olanların
> hepsi kapandı.
>
> **İki küçük onay da bekliyor:** §11.3 çıktısına eklenen `okunmayan_alanlar`
> (commit'e girdi; itiraz gelirse tek blok çıkar) ve **T-41**'in `DENETIM.py`
> yaması (kod değişmedi, `DENETIM.py` her şeyin bekçisi olduğu için onay
> istiyor).
>
> ### Neden bunlar önce
>
> Dış incelemenin sözü: *"önce yanlış yayın izni ve sessiz veri atlama
> sorunları, sonra tamamlanma tablosu."* Katılıyoruz. Dokuzu da **sessiz**
> hatalar: hiçbiri kırmızı yanmıyor, hepsi planı temiz gösteriyor.
>
> ### ⛔ Bozulmaması gereken kural
>
> Şartname §7.6 ve §16.1: **doğrulayıcı çözücüyle mantık paylaşmaz.**
> `09-motor/cozucu/` ve `09-motor/dogrulayici/` birbirini **import etmez**;
> `09-motor/orkestra.py` ikisini de import eder ve bu doğrudur.
> `09-motor/testler/test_bagimsizlik.py` bunu koruyor.
>
> ⚠ **T-19 bu kuralın sınırını gösterdi ve ders kapandıktan sonra da
> geçerli:** bağımsızlık kural *mantığını* ayırıyor, **girdi yorumunu**
> ayırmıyor. İki taraf da aynı fikstür geleneğiyle okuyordu ve o gelenek
> şartnameyle uyuşmuyordu — ikisi birbiriyle tutarlı, ikisi de yanlıştı.
>
> Çözüm ortak modül **değildi**: talep artık üç yerde ayrı ayrı okunuyor ve
> `okunmayan_alanlar` *"neye bakmadım"* sorusunu cevaplıyor.
> `09-motor/testler/test_bagimsizlik.py` ortak yardımcı modülü hâlâ yasaklıyor.
>
> ⚠ **T-32 aynı sınırın ikinci örneği ve onu bugün ben açtım:** K-30'u
> yazarken fazla mesai tavanını çözücüde **profil tablosundan**, doğrulayıcıda
> **kural parametresinden** okur hâle getirdim. İkisi bugün aynı sayıyı
> veriyor; kiracı parametreyi değiştirdiği gün sessizce ayrışırlar.
>
> ### ⛔ Commit öncesi içerik karşılaştırması (O-9)
>
> Dosyalar karşı taraftan çekilip **içerikçe** karşılaştırılır. Hafızaya
> değil `cmp`'ye güvenilir. Boyut eşitliği de yetmez.
>
> ✅ **Tamamlananlar:** fikstürler · test iskeleti · şartname v1.4 · kural
> sınıflandırması · mevzuat araştırması · bağımsız doğrulayıcı · çözücü ·
> onarım döngüsü · plan profilleri · **CI kapısı (yeşil)**.
> A-15, A-17, A-18, T-12, T-14, T-15, T-17 kapandı.
> Dış incelemeden: **T-27** (16 Eylül) · **T-22, T-34, T-35, T-19** (23 Eylül).
> K-27, K-28, K-29, K-30 karara bağlandı — **ama K-28 kodda eksik (T-24a).**
>
> **Paralelde açık kalanlar:**
>
> - **T-23, T-24, T-25, T-26** — ikinci turun kalan bulguları
> - **T-30, T-31, T-32, T-33, T-36** 🟡 — üçüncü turun kalan bulguları
> - **T-39, T-40, T-41** 🟡 — 23 Eylül kapatma turunun açtıkları.
>   **T-39** talep ekranı yazılmadan önce karara bağlanmalı (kapı şartı);
>   **T-40** `tercih_karsilama_yuzde` üretilmiyor — T-38'in `tercihler`
>   satırına bağlı; **T-41** `DENETIM.py` uyarı çıktısının ayrıştırılması
> - **T-20** — M0 testinin kapsamı; A-1'i kapatan test, doğrulanmalı
> - **T-13** — `ADALET_DENGESI`'nin `saat` boyutu
> - **`/suggest` (§11.5)** — ⚠ **kabul ölçütü yok, fikstürü yok.** Kod
>   yazmadan önce *"doğru çalışıyorsa ne görmeliyiz"* cümleleri yazılıp
>   onaylanmalı — A7'de bu adımın atlanmasının bedeli görüldü.
> - **A-16 hukuk teyidi** — madde numaralı tablo hazır, uzman bakacak.
> - **A-13 kapsam envanteri** — Ocak hedefi ölçülmedi. Ayrı pencere işi.
> - **`07-motor/` yeniden adlandırma** — `08-analiz/` adı `08-motor-testleri/`
>   ile çakışır; örneğin `10-analiz/`.
> - ✅ **`DENETIM.py` her oturum sonunda koşturulmalı:**
>   `cd C:\Users\PC\Desktop\Tshift` sonra `py DENETIM.py`.
> - **A-6 mutasyon raporu** — kırmızı kanıt turu elle seçilen kırılmalarda
>   12/12 yakaladı ama **dış inceleme 19 bulgu buldu**; otomatik mutasyon
>   hâlâ yok ve iç kanıtın sınırı görüldü.
> - A-2 ve A-3 eksik bekçiler.
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
| 8 | `08-URUN-KARARLARI.md` | **Bir ürün davranışının neden böyle olduğunu soruyorsan.** K-serisi: verilmiş kararlar, gerekçeleriyle |
| 9 | `oturumlar/` | Belirli bir değişikliğin ne zaman ve neden yapıldığını arıyorsan |

### Deponun tamamı — nerede ne var

> **Bu klasör (`00-DEVIR/`) şartnameyi, demoyu ya da kodu İÇERMEZ; onlara
> İŞARET EDER.** Devir paketi bir harita, arşiv değil. Aşağıdaki tablo o
> haritanın tamamıdır.

| Yol | İçerik | Ne zaman aç |
|---|---|---|
| **`02-spec/v1.4-master-spec.md`** | **YÜRÜRLÜKTEKİ ŞARTNAME — 17 bölüm, son karar.** §3 roller ve yetki matrisi · **§5.3 `yasal` / `kabul_edilebilir` ayrımı** · §6 kural kataloğu (**34 kural**, yasal ve kabul sütunlarıyla, madde dayanaklarıyla) · §6.3 gece yarısını aşan vardiya + **sektör istisnası** + DST modeli · §8 veri modeli · §9 ekranlar · **§11 motor sözleşmesi** (`/solve`, `/evaluate`, çözümsüzlük teşhisi, **`en_iyi_plan`**, §11.2 lookback, §11.7 idempotency + onarım) · **§16 test stratejisi ve 12 altın senaryo** · §17 sürüm notları. | **Motor, kural ya da ekran işine başlamadan ÖNCE.** v1.0–v1.3 aynı klasörde, **dondurulmuş** (geçmiş korunuyor). Hazırlık notları `02-spec/v1.4-hazirlik/`. |
| **`02-spec/v0-koken-...Analiz_v2.docx`** | **KÖKEN DOKÜMANI — 27 bölüm.** Projenin doğduğu analiz. Master Spec'in kapsamadığı yerde **hâlâ kaynak**: §8 sektörel kural paketleri (çağrı merkezi/perakende/üretim) · §23 Faz 0–10 geliştirme planı · §25 12 haftalık yol haritası · §20 riskler. | Gerekçe, fazlama ya da sektör paketi sorusu varsa. **Çeliştiğinde Master Spec kazanır** (§17). |
| `03-demo/v2-html/tshift-demo-v2.html` | **Çalışan demo** — 15 ekran, iki operasyon (çağrı merkezi + otel), sürükle-bırak takvim. Tek HTML dosyası, tarayıcıda açılır. | Ekran tasarımı ya da akış konuşulacaksa. Ürünün görsel dili burada. |
| `01-spike/` | **Motor fizibilite testleri** (7–8 Eylül) — CP-SAT vs greedy karşılaştırması, ölçek testleri (200→2000 kişi), otel senaryosu. Kronoloji ve ölçülen sayılar `01-spike/README.md`'de. | Motor yazılmadan **önce mutlaka.** Teknoloji kararının dayanağı burada. |
| `04-kod/` | **Çalışan uygulama** — backend (.NET 10), frontend (Next.js 16), veritabanı betikleri, testler, Docker | Kod yazılacaksa |
| `05-inceleme/v1-2026-09-11/` | **Yılmaz'a gönderilen inceleme paketi** — 8 soru, 4 hata otopsisi, bilinen açıklar | Dış inceleme konuşulacaksa |
| `06-veri/` | **Gerçek müşteri verisi** (PDKS + plan) ve türetilen çıktılar. ⚠ **`.gitignore` içinde — git'e girmez.** | Veri analizi yapılacaksa |
| `07-motor/` | ⚠ **Motor YOK.** Geçmiş planları ölçen analiz betikleri. Bkz. `07-motor/OKU-BENI.md` | — |
| **`08-motor-testleri/`** | ✅ **Motor var; 7 altın senaryo koşuyor ve yeşil, 4'ü (A2/A10/A11/A12) backend tarafında koşmuyor.** Şartnameden türetilmiş **kabul senaryoları** (A1–A12): motorun ne yapması gerektiğinin, motor yazılmadan önce ve motora bakmadan yazılmış hâli. **`08-motor-testleri/v5/` onaylanmış ve güncel**; v1–v4 dondurulmuş. İçinde: `KABUL-OLCUTLERI.md` (onaylı cümleler) → `08-motor-testleri/v5/fikstur/` (11 JSON + ortak sahne) → `08-motor-testleri/v5/testler/` (pytest çatısı + `08-motor-testleri/v5/testler/backend-taslak/` C# taslakları). Onay turunun özeti `ONAY-DURUMU.md`'de. Bkz. `08-motor-testleri/OKU-BENI.md` ve `08-motor-testleri/v5/testler/OKU-BENI.md` | Motor ya da doğrulayıcı işine başlamadan **ÖNCE** |
| **`05-inceleme/beceriler/`** 🆕 | **İncelemenin nasıl yapılacağı** — dört dosya. Haftalık dış tarama döngüsü: kim ne yapar, paket nasıl hazırlanır, ne bulgu sayılır. `00-DEVIR/` **bağlamdır** (neyi bilmen gerek), burası **beceridir** (işin nasıl yapılacağı) | Haftalık tarama öncesi; yeni bir inceleme yapılacaksa |
| **`09-motor/`** | ✅ **MOTOR — çalışıyor.** Üç parça: `09-motor/dogrulayici/` (denetler, **19** kural gövdesi), `09-motor/cozucu/` (CP-SAT ile üretir), `09-motor/orkestra.py` (§11.7 onarım döngüsü). **77** birim testi (23 Eylül). **`/suggest` hâlâ yok** — bilerek 501 dönüyor. ⛔ Çözücü ile doğrulayıcı birbirini import ETMEZ (§7.6); `09-motor/testler/test_bagimsizlik.py` bunu koruyor. Bkz. `09-motor/OKU-BENI.md` | Motor ya da doğrulayıcı işine başlamadan önce |
| **`DENETIM.py`** | **Devir paketi denetimi.** §5'teki ritüelin 5. maddesini makineye yaptırır. `py DENETIM.py` | Devire "tamam" demeden önce, her seferinde |
| `00-arsiv/` | Dondurulmuş eski sürümler | Geçmiş aranıyorsa |
| `DEGISIM-GUNLUGU.md` | Kilometre taşları, en yeni en üstte | "Ne zaman ne değişti" |
| `RISKLER-VE-ONLEMLER.md` | 15 hata sınıfı, savunma hatları, **kırmızı çizgiler §6** | Veri/sır/migration'a dokunmadan önce |
| `SURUMLEME.md` | Hata yapılırsa nasıl geri dönülür | Bir şey bozulduğunda |
| `KALITE-ARASTIRMASI-DEGERLENDIRME.md` | Sahanın kalite pratiklerinin bu projeye göre değerlendirmesi | Test/süreç tasarımı yapılacaksa |

**Git etiketleri** `v0.1-kiracilik` … `v0.8-devir` — her kilometre taşı
işaretli, geri dönülebilir.

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

> **Tetikleyici değişti (16 Eylül).** Önceki kural şuydu: *"Mustafa 'aktarım
> dosyasını güncelle' dediğinde."* Yani güncelleme **birinin hatırlamasına**
> bağlıydı — ve hatırlamaya bağlı bir bekçi, bekçi değildir (O-1'in tam
> tarifi). Yerine üç somut an kondu.

| Ne zaman | Ne güncellenir |
|---|---|
| **Aynı commit'te** | Bir karar verildi, bir kural yazıldı, bir madde kapandı → `08-URUN-KARARLARI.md`, `06-ACIK-RISKLER.md` ve ilgili `02`–`07` dosyası. **Kod ile doküman aynı commit'te gider** |
| **İş parçası bitince** | `oturumlar/YYYY-AA-GG-<is-parcasi>.md` |
| **Oturum ya da pencere kapanırken** | Bu sayfadaki iki bölüm + `DEGISIM-GUNLUGU.md` + `DENETIM.py` |

**Neden en önemlisi ilki.** Oturum **her an** bitebilir: bağlam dolar, makine
uyur, insan yorulur. Doküman koddan geriden geliyorsa bir sonraki pencere
**yanlış haritayla** başlar. §5'in kuralı *"kanıtı olmayan cümle yazılmaz"*
diyor; aynanın öteki yüzü de geçerli: **kanıt değişti ama cümle değişmediyse
doküman yalan söylüyor.**

16 Eylül bunun küçük bir örneğini verdi: A7'nin onaylı kabul cümlesi
(*"Ç01–Ç03 en müsait olanlar"*) fikstüre hiç çevrilmemişti. Cümle onaylıydı,
fikstür ona uymuyordu ve boşluk **ancak motor yazılınca** göründü.

Adım adım:

1. `oturumlar/YYYY-AA-GG-<is-parcasi>.md` dosyası yazılır — o oturumda
   **hangi dosya neden değişti, hangi test eklendi, hangi karar verildi,
   hangi öneri REDDEDİLDİ.** Bu dosyalar **asla yeniden yazılmaz.**
2. Değişen şeye göre `02`–`07` arası ilgili dosyalar güncellenir.
3. Bu sayfadaki **"Şu anda neredeyiz"** ve **"Sıradaki tek adım"** bölümleri
   yenilenir. Bu iki bölüm her zaman güncel olmak zorundadır — devir
   paketinin geri kalanı bu ikisi yanlışsa işe yaramaz.
4. `DEGISIM-GUNLUGU.md`'ye kilometre taşıysa satır eklenir, etiket atılır.
5. **DENETİM — atlanmaz, ve artık elle yapılmıyor:**

   ```
   cd C:\Users\PC\Desktop\Tshift
   py DENETIM.py
   ```

   Yedi kontrolü makine yapar: test adlarının `DisplayName` ile birebir
   eşleşmesi, sayı tutarlılığı, dosya yollarının varlığı, değişmez özet
   tablosu, günlük adlandırması, değişim günlüğünün tazeliği ve **commit
   edilmemiş devir dosyası** olup olmadığı. Çıkış kodu 0 değilse devir
   "tamam" değildir.

   Betiğin yapamadığı iki şey elde kalır:
   - **Ölçüm değiştiyse tahmin edilmez, yeniden koşulur.**
   - Betik *tutarlılığa* bakar, *doğruluğa* değil. Tutarlı bir yanlış yine
     yakalanmaz; onu ancak iddiayı kaynağıyla karşılaştırmak yakalar.

> ⚠ **Yazdım ≠ gönderdim ≠ commit ettim ≠ karşı tarafta değişti ≠ göndermem
> gerektiğini fark ettim.** Beşi ayrı adımdır ve beşi de doğrulanır.
>
> 14 Eylül'de Mustafa'nın kapsam kararlarının tamamı yerel kopyada
> güncellenmiş ama makineye hiç gitmemişti (`oturumlar/2026-09-14-veri-analizi.md`
> §10). 16 Eylül'de son halka eklendi: bir düzeltme **hiç gönderilmemişti** ve
> iki tarafta da hiçbir şey kırmızı yanmıyordu — git temiz, `DENETIM.py`
> *"commit bekleyen 0"*, testler yeşil; çünkü her iki taraf **kendi içinde**
> tutarlıydı ve tutarsızlık **aralarındaydı** (`05-HATA-OTOPSILERI.md` O-9).
>
> **Bekçi:** commit öncesi dosyalar karşı taraftan çekilip **içerikçe**
> karşılaştırılır. Hafızaya değil `cmp`'ye güvenilir. Boyut eşitliği de
> yetmez — 15 Eylül'de `v2`→`v5` 17 bayat atıf, dosya boyutları **birebir
> aynıydı**.

---

## 5b. PENCERE PROTOKOLÜ

**Karar: 14 Eylül 2026.** Uzun sohbetlerde bağlam kaybını önlemek için iş,
pencereler arasında devredilir. Kurallar:

### Ritim: iş parçası başına bir pencere, SIRALI

Motor sözleşmesi bir pencere, CI+testler bir pencere, ekranlar bir pencere —
ama **hepsi sırayla.** Aynı anda **tek aktif pencere** olur.

| Durum | Ne yapılır |
|---|---|
| Yeni ve ilgisiz iş parçası | **Yeni pencere.** Bu sayfayı oku, devam et. |
| Aynı işin küçük devamı | Aynı pencerede kal |
| Sohbet uzadı / yavaşladı | Günlüğü yaz, yeni pencere |
| **Aynı hata iki kez düzeltildi** | **Dur.** Bağlamın kirlendiğinin en net işareti. |
| Doküman ile kod çelişiyor | Kod yazma; hangisinin doğru olduğunu Mustafa'ya sor |

### Açılış beyanı — yeni pencere işe başlamadan önce

> **Yeni pencere, dosya yazmadan önce şunu söyler:** hangi dosyaları okudum,
> sıradaki adımı nasıl anladım, hangi varsayımla başlıyorum.

**Neden (karar: 14 Eylül 2026):** Aşağıdaki tablo *"doküman yanlış başlarsa
yakalamaz"* diyor ve bu açık kapalı değildi. Testler başlangıcı yönlendirmez,
doküman da yanlış anlaşılmayı göremez. Açılış beyanı **Mustafa'nın**
görebileceği tek an: iş yapılmadan önce.

Bedeli bir mesaj, getirisi yanlış yöne gidilmiş bir oturum. 14 Eylül'de
kendiliğinden yapıldı ve işe yaradı — şartnamedeki bir çelişki daha ilk
mesajda görüldü.

### Yazma hakkı

> **Aynı anda yalnız bir pencere dosya yazar ve commit eder.**
> Devredilen pencere **salt-okunur** olur: soru cevaplayabilir, dosya yazamaz.

Devredilen pencere hemen kapatılmaz — **geri dönüş yoludur.** Yeni pencere
devir paketini okuyup işe başladığını gösterene kadar açık kalır. Devir eksik
çıkarsa oraya dönülüp tamamlanır.

### Geri bildirim yüzeyleri — iki pencere, biri yazmaz

**Karar: 15 Eylül 2026.** Gerekçe, elenen alternatif ve kanıt durumu:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

Aktif pencerenin yanında **ikinci bir pencere** açılır. Bu pencere ajan
değildir: dosya yazmaz, komut almaz, soru cevaplamaz. Yalnız **göstergedir.**
Amacı tek: kırmızıyı saatler sonra değil dakikalar içinde fark etmek.

| Yüzey | Komut (`04-kod` içinde) | Sürekli mi |
|---|---|---|
| **Sunucu günlükleri** | `docker compose logs -f` | ✅ Sürekli açık |
| **Testler** | `.\TEST.ps1` | ❌ **Talep üzerine** |

⚠ **Testler neden sürekli koşmaz:** §7'ye göre `TEST.ps1` API'yi **önce
durdurur.** Sürekli koşan bir test izleyicisi geliştirme kipindeki API'yi
sürekli düşürür. Başka depolarda gördüğünüz "sürekli koşan test penceresi"
kurgusu bu depoda **olduğu gibi kurulamaz.**

**Bunun doğurduğu kural — asıl madde budur:**

> **Ajan "bitti" demeden önce `.\TEST.ps1`'i kendisi koşar ve çıktısını
> rapor eder.** Test çıktısını pencereler arasında elle taşıyan insan,
> zincirin en zayıf halkasıdır.

**Ne DEĞİLDİR:** ikinci bir *yazıcı* ajan değildir. Paralel ajan modeli
(kod bir ajanda, hata ayıklama başka bir ajanda) 15 Eylül'de değerlendirildi
ve **reddedildi** — aşağıdaki tabloda R5 kapalıdır ve onu yeniden açacak
ölçülmüş bir gerekçe yoktur. Araç tarafı: `06-ACIK-RISKLER.md` ·
📌 Araç kararı.

**Kapı değil, hız.** CI (A-4) zaten kapıdır ve 14 Eylül'de yeşil yandı. Bu
karar yeni bir kapı eklemez; **kırmızının fark edilme süresini** kısaltır.
İkisi farklı şeylerdir, biri diğerinin yerine geçmez.

### Günlük dosyası adlandırma

Aynı gün birden çok oturum olabilir. **İki pencere asla aynı dosyaya
yazmaz:**

```
oturumlar/2026-09-14-veri-analizi.md
oturumlar/2026-09-15-motor-sozlesmesi.md
oturumlar/2026-09-15-ci-ve-testler.md     ← aynı gün, ayrı iş, ayrı dosya
```

İndeks dosyası **bilerek yok** — olsaydı çakışan dosya o olurdu. Kronolojik
sıra dosya adından çıkar.

**Paylaşımlı tek dosya bu sayfadır** (`00-BURADAN-BASLA.md`), çünkü "şu an
neredeyiz" tek yerde olmak zorunda. Onu yalnız **aktif** pencere günceller.

### Pencereler arası kopukluk — asıl güvence ne

Yılmaz'ın *"bloklar arası ilişki kopar"* itirazının pencere seviyesindeki
hâli. Cevap da aynı yerden gelir: **kopmayı engelleyemezsin, gürültülü
yaparsın.**

| Ne | Ne işe yarar | Neyi yaramaz |
|---|---|---|
| **Doküman** (`00-DEVIR/`) | Yeni pencerenin **doğru başlamasını** sağlar | Yanlış başlarsa yakalamaz |
| **Açılış beyanı** | Yanlış başlangıcı **iş yapılmadan** yakalar | Sessiz kalan varsayımı göremez |
| **`DENETIM.py`** | Dokümanın **kendi içinde tutarsızlığını** yakalar | Tutarlı bir yanlışı göremez |
| **Testler** (39 + M0–M6) | Bir ilişki bozulursa **kırmızı yanar** | Başlangıcı yönlendirmez |

**Asıl güvence testlerdir, doküman değil.** Doküman iyi niyeti taşır; test
yanlışı yakalar. Bu yüzden **CI (A-4) pencere protokolünün önkoşuludur:**
pencere değişince "testleri çalıştırmayı hatırlayan bağlam" ortadan kalkar,
ve tam o anda otomatik kapıya en çok ihtiyaç duyulur.

### Devirde bilinen riskler

| # | Risk | Önlem | Kapalı mı |
|---|---|---|---|
| R1 | Yazıya dökülmemiş sezgi kaybolur | Oturum günlüğü | 🟡 Tanım gereği tam kapanamaz |
| R2 | Verilmiş karar yeniden verilir | 02/03/06 + **reddedilenler kaydı** | ✅ |
| R3 | Bozuk bir şey sağlam sanılır | 06'da açık durum işaretleri | ✅ |
| R4 | Mevcut kod bozulur | Testler | ⚠️ **CI koşana kadar zayıf** |
| R5 | İki pencere yazar, sürüklenme | Tek aktif pencere kuralı | ✅ *(15 Eylül: paralel ajan modeli değerlendirildi, reddedildi — teyit)* |
| R6 | Devir dokümanının kendisi yanlış olur | Her iddia bir teste/dosyaya/komuta bağlı **+ `DENETIM.py`** | ✅ *(M0'da, sonra 14 Eylül'de betikle)* |
| R7 | **Dokümanlar büyür, okumak kendisi bağlam sorunu olur** | Giriş 1 sayfa; derin dosyalar talep üzerine; **düzenli sadeleştirme** | 🔴 **Eşikte** — 9 dosya |

**R7 için kural:** Yeni bir devir dosyası açmadan önce sor — *bu, var olan bir
dosyanın bölümü olabilir mi?* `00-DEVIR/` dokuz dosyayı geçerse sadeleştirme
zamanı gelmiştir.

⚠ **14 Eylül: dokuzuncu dosya açıldı** (`08-URUN-KARARLARI.md`). Soru soruldu
ve cevabı "hayır" çıktı — ürün kararı mimari karar değil, ve adı içeriğine
uymayan dosya bu projede zaten bir kez pahalıya mal oldu. **Onuncu dosyadan
önce sadeleştirme yapılmalı.** `DENETIM.py` bunu otomatik uyarıyor.

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
