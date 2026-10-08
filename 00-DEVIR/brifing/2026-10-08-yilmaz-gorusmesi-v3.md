# Yılmaz görüşmesi — brifing v3 (8 Ekim 2026)

**Hazırlayan:** Claude (8 Ekim gecesi), Mustafa'nın isteğiyle · **Kim için:**
Mustafa (görüşmeye hazırlık) ve Yılmaz (doğrudan okuyabilir) · **v3'ün
farkı:** her kararın, her bulgunun ve her otopsinin **kendisi** bu belgede
anlatılıyor — *K-61*, *K-63*, *O-19* gibi numaralar yalnız kayıt
adresidir, okumak için başka dosyaya gitmek gerekmez. v1 ve v2 kayıt için
duruyor. · **Önceki paket:** `05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md`
(11 Eylül; sekiz soru — cevap alınamadı).

> Her sayı bu depodaki bir ölçüme ya da kayda dayanır. Tahmin olan yerler
> *tahmin* diye işaretli. Numaralar: **K** ürün kararı · **M** mimari karar ·
> **O** hata otopsisi · **T** bulgu/açık risk · **A** eski risk serisi ·
> *"bulgu N"* T-60 kalite programının numaralı ölçüm sonucu. Hepsi
> `00-DEVIR/` altındaki dosyalarda tarih ve gerekçesiyle kayıtlı; burada
> içerikleri yazılı.

## İçindekiler

1. [Bir sayfada proje](#1--bir-sayfada-proje)
2. [11 Eylül'den bu yana ne oldu](#2--11-eylülden-bu-yana-ne-oldu)
3. [Mimari kararlar — ne, neden, geri almanın bedeli](#3--mimari-kararlar--ne-neden-geri-almanın-bedeli)
4. [Motor nasıl çalışıyor ve neden böyle](#4--motor-nasıl-çalışıyor-ve-neden-böyle)
5. [Fazla mesai: kararlar, hata, düzeltme, ölçüm](#5--fazla-mesai-kararlar-hata-düzeltme-ölçüm)
6. [Bu hafta koda inen iki şey: yeniden başlatma ve K-63](#6--bu-hafta-koda-inen-iki-şey-yeniden-başlatma-ve-k-63)
7. [Kaliteyi nasıl ölçüyoruz; ne biliyoruz, ne bilmiyoruz](#7--kaliteyi-nasıl-ölçüyoruz-ne-biliyoruz-ne-bilmiyoruz)
8. [Süreç ve bekçiler — hatalar nasıl yakalanıyor](#8--süreç-ve-bekçiler--hatalar-nasıl-yakalanıyor)
9. [Bugünkü durum — katman katman](#9--bugünkü-durum--katman-katman)
10. [Ocak'a kadar eksikler](#10--ocaka-kadar-eksikler)
11. [Nerede destek almalıyız](#11--nerede-destek-almalıyız)
12. [Yılmaz'ın görüşünü istediğimiz konular](#12--yılmazın-görüşünü-istediğimiz-konular)
13. [Önerilen gündem (90 dakika)](#13--önerilen-gündem-90-dakika)
14. [Ek — sayılar ve okuma listesi](#14--ek--sayılar-ve-okuma-listesi)

---

## 1 · Bir sayfada proje

**T-Shift** (Teknovisor): çok kiracılı, yapay zekâ destekli **vardiya
planlama ve optimizasyon SaaS'ı**. Girdi: çalışanlar ve sözleşmeleri, iş
kanunu ve firma kuralları, beklenen iş yükü (saat saat kaç kişi gerek).
Çıktı: haftalık vardiya planı — üç önceliğe göre üç alternatif (DENGELI /
KAPSAMA / CALISAN) ve yönetici plana dokununca sonuçlarını hesaplayıp öneri
getiren bir editör.

**Ürünün amacı (Mustafa, 6 Ekim):** *"Ürünün çıktısı elimizdeki tüm
kriterlere bağlı olarak optimum planı çıkarabiliyor mu?"* — firmaya ek ücret
(fazla mesai) çıkarmadan eldeki kaynağı en iyi kullanmak; fazla mesai
kriterlerden yalnız biri.

**Temel iddia:** tek üründe çok sektör (çağrı merkezi, otel, perakende…);
sektöre özel kural **koda değil veriye** yazılır (§3, M-10). Spike'ta
kanıtlandı: otelin gece kuralları tek satır kod değişmeden, yalnız veriyle
devreye girdi.

**Kim:** Mustafa — ürün sahibi, tek karar verici, 11 yıl BT ürün müdürlüğü,
yazılımcı değil (fonksiyonel ve API testi yapar, kod okumaz). Claude — bütün
kodu yazıyor. Yılmaz — dış göz, kilometre taşlarında. **Yılmaz'ın
başlangıçtaki itirazı projenin asıl sorusu olarak kayıtlı:** *"Yapay zekâ
blokların birbiriyle ilişkisini kuramaz."* Cevap tartışmayla değil ölçümle
aranıyor: *katmanlar arası kopmalar sessiz mi kalıyor, yakalanıyor mu?*

**Hedef ve strateji:** MVP yok (12 Eylül kararı, tartışmaya kapalı) —
satılabilir sürüm şartnamenin fonksiyonel bütünü, çünkü kuralların %80'ine
uyan plan müdürün elle düzelteceği plandır (müşterinin zaten yaptığı iş);
referans müşteri yokken bir ret kapıyı kapatır. **Ocak sonunda sahaya
çıkmak**; pilot yöntemi *gölge pilot* (gerçek çağrı merkezi verisiyle,
gerçek kullanıcı olmadan uçtan uca). Satış sonrası bütçeyle mimar/yazılım
ekibi kurulacak — ilk satış geliştirmenin sonu değil finansmanı.

**Yığın:** PostgreSQL 17 (tek veritabanı + `tenant_id` + satır seviyesi
güvenlik) · .NET 10 · Python + OR-Tools CP-SAT (motor, ayrı servis) · Next.js
16 · kimlik kendi kodumuzda · RabbitMQ ve barındırma kararı ertelendi.

---

## 2 · 11 Eylül'den bu yana ne oldu

11 Eylül'de Yılmaz'a giden paket **dikey dilimi** anlatıyordu: veritabanından
ekrana çalışan yönetimi, 38 test (bugün 45), 4 hata otopsisi, 8 soru. O
günden beri ağırlık **motora** kaydı:

| Tarih | Ne oldu |
|---|---|
| 12–16 Eyl | **Ölçek kararı:** ürün hem 20 kişilik bar ekibini hem 2.000 kişilik operasyonu çözmeli; küçük ekip ayrı bir problem sınıfı — üç kişinin izni planı çözümsüz yapar, *"hangi kural çakışıyor, neyi gevşetirsem çözülür"* açıklaması orada birincil özellik. **Şartname v1.4:** 17 bölüm, **41 kural** (32 sert, 9 yumuşak), her kuralda *yasal mı* / *ihlali kabul edilebilir mi* sütunları. Gerçek çağrı merkezi verisi geldi (giriş-çıkış kayıtları + plan; `06-veri/`, git dışı). |
| 16 Eyl | **Motor yazıldı** (§4): bağımsız doğrulayıcı + CP-SAT çözücü + onarım döngüsü. |
| 23 Eyl | Haftalık dış inceleme döngüsü (farklı sağlayıcının modeli kodu şartnameye karşı tarar): 19 bulgu (T-18…T-36); 🔴 olanların hepsi kapandı, 🟡'ların bir kısmı açık. CI (GitHub Actions, backend + motor) yeşil. |
| 28–30 Eyl | 350 → **500 kişilik gerçekçi veri setleri**; 10 kişilik test sahnelerinde görünmeyen altı hata bir saatte çıktı. *"İmkânsız"* ile *"süre yetmedi"* ayrı cevaplar oldu (§4.4). Tam ölçek ilk kez çözüldü — 2.493 atama, **0 sert ihlal**. |
| 1–2 Eki | On 🔴 bulgu kapandı; *"fazla mesai"* tek tanıma indi (§5.2); kalite ölçüm araçları yazıldı. |
| 3–7 Eki | **Kalite programı (T-60, §7):** üç aşamalı arama (§4.5), *önce fazla mesaisiz* arama (§5.3), tam ölçekte fazla mesai 475–511 saat/haftadan **0**'a; iki otopsi (§4.6, §5.4); 7 Ekim akşamı yeniden başlatma + K-63 koda indi (§6), gece ölçüldü. |

---

## 3 · Mimari kararlar — ne, neden, geri almanın bedeli

Her karar `00-DEVIR/03-MIMARI-KARARLAR.md`'de *ne / neden / hangi alternatif
elendi / sonradan değiştirmenin bedeli* biçiminde duruyor; burada hepsinin
özü. Yılmaz'dan asıl istenen, 🔴 işaretli beşine ikinci göz (§11).

### 3.1 Backend ve veri katmanı

**M-01 · Çok kiracılık: tek veritabanı + `tenant_id` + iki katmanlı yalıtım
(9 Eylül) — geri alma 🔴 bütün veri taşınır.** Bütün kiracılar tek PostgreSQL
veritabanında, her tabloda `tenant_id`. Yalıtım iki bağımsız yerde: (1) EF
Core küresel sorgu filtresi — `IKiraciVarligi` arayüzünü uygulayan her varlık
için her sorguya kiracı şartı kendiliğinden eklenir; (2) PostgreSQL **Row
Level Security + `FORCE`** — ham SQL yazılsa bile veritabanı başka kiracının
satırını vermez. Kiracı kimliği her bağlantı açılışında `app.tenant_id`
oturum değişkenine `DbConnectionInterceptor` ile yazılır. *Neden iki katman:*
birincisi unutulabilir (yeni sorgu, ham SQL, yeni geliştirici), ikincisi
unutulamaz; uygulama katmanı açığın bulunacağı katmandır, garanti
veritabanında olmalı. *Elenen:* kiracı başına ayrı veritabanı ya da şema (100
müşteride 100 migration). *Açık risk (A-8):* oturum değişkeni transaction
kipinde bir bağlantı havuzunun (PgBouncer) arkasında istekler arasında
karışabilir — §11.

**M-02 · İki veritabanı rolü (10 Eylül) — 🟢.** `tshift` migration ve şema
(sahip/süper); `tshift_app` uygulamayı taşır (`NOSUPERUSER`, `NOBYPASSRLS`,
yalnız CRUD). *Neden — bir hatanın sonucu (O-1):* uygulama Docker'ın süper
kullanıcısıyla bağlanıyordu; RLS doğru yazılmış, açılmış, *"açık mı"* sorgusu
`t/t` dönüyordu — ama PostgreSQL'de süper kullanıcı RLS'i tamamen aşar,
`FORCE` bile durduramaz. Güvenlik kâğıt üstünde vardı, çalışmada yoktu;
yakalayan inceleme değil testin kendisi oldu (iki firma kurup *"birbirini
görüyor mu"*). Bekçi: *"Bağlanan rol süper kullanıcı değil"* testi — bağlantı
dizesi `tshift`e çevrilirse paket anında kırmızı yanar. Bağlantı dizeleri
kasıtlı olarak iki ayrı değişkende.

**M-03 · Kimlik katmanı kendi kodumuzda; Keycloak elendi (9 Eylül) — 🟡.**
Argon2id (64 MB / 3 tur / 4 paralellik), 15 dakikalık JWT erişim jetonu, 30
günlük **döner** yenileme jetonu (her kullanımda yenisi verilir, yalnız
SHA-256 özeti saklanır; kullanılmış jeton tekrar gelirse hırsızlık sayılıp o
kullanıcının bütün oturumları düşürülür), e-posta veya IP başına 5 başarısız
denemede 15 dk kilit, kullanıcı yoksa bile Argon2 çalıştırılır (zamanlama
saldırısı). *Neden:* kiracı-kullanıcı eşleşmesi ve kapsam modeli zaten
bizde; Keycloak ek dağıtım birimi, ek hata kaynağı, modeli tam karşılamayan
soyutlama. Bedel kabul edildi: güvenlik kodunu kendimiz taşıyoruz; kimlik
testleri diğerlerinden ayrıntılı. SSO/OIDC faz 2.

**M-04 · İzin kodları jetonda, kapsam veritabanında (10 Eylül) — 🟢.**
*Ne yapabilir* (izin listesi, kısa, seyrek değişir) JWT'de; *nerede
yapabilir* (departman/ekip kapsamı, uzayabilir, anında etkili olmalı) her
istekte veritabanından. Kabul edilen bedel: geri alınan izin jeton süresi
dolana kadar (≤15 dk) taşınır; acil iptalde yenileme jetonları da düşürülür.

**M-05 · Tek `KapsamKurali`: hem listeleme hem yazma kontrolü (11 Eylül) —
🟢.** Kapsam kuralı tek bir ifade; biri `IQueryable`'a uygulanır (liste), biri
derlenip tek kayda (yazma). İlke: *göremeyeceğin kaydı oluşturamazsın.*
İki ayrı yerde yazılsaydı zamanla ayrışır, bir gün *"listede göremediğim ama
oluşturabildiğim kayıt"* çıkardı. ⚠ Bu birliği sabitleyen test yok (A-2).

**M-06 · Denetim kaydı: otomatik, aynı işlemde, sadece-eklenir (11 Eylül) —
🔴 geri alınamaz, geçmiş kaybolur.** Uçlarda tek tek çağrılmaz, EF'in
`SaveChanges` akışına bağlı — yeni tablo kendiliğinden kapsanır; değişiklik
ve denetim satırı tek işlemde gider (istemcide üretilen UUIDv7 kimlikler
sayesinde); `tshift_app`'in `audit_log` üzerinde UPDATE/DELETE yetkisi yok —
kısıt uygulamada değil veritabanında. Parola ve jeton özetleri kayda girmez
(alanın *değiştiği* yazılır, değeri değil). *Neden şimdi:* tutulmayan geçmiş
sonradan üretilemez. Açık: hacim yönetimi (bölümleme, saklama) yazılmadı.

**M-07 · Jetonlar `httpOnly` çerezde; arayüz API'ye doğrudan gitmez (BFF)
(11 Eylül) — 🟡.** Tarayıcı istekleri Next.js sunucusu taşır; `localStorage`
kolaydır ama sayfadaki herhangi bir betik jetonu okuyabilir. Yan fayda: CORS
gerekmez. Arayüzdeki kontrol güvenlik sınırı değildir; asıl sınır API.

**M-08 · Mimari testleri: özellik değil *yasa* sınayan katman (10 Eylül) —
🟢.** Kiracıya ait her tabloda RLS açık ve `FORCE`'lu mu (tablo listesi elle
değil EF modelinden); RLS dışı tablolar yalnız bilinen istisnalar mı (M-13:
`login_attempts` kaba kuvvet sayacı bilerek dışarıda — kiracı bilinmeden
yazılmalı, yoksa saldırgan var olmayan firma adıyla kilidi atlar); korumasız
uç var mı; kültüre bağımlı `ToLower()` (Türkçe `I` tuzağı); ayar dosyasında
sır var mı; denetim kaydı hâlâ sadece-eklenir mi. Bugün bir şey yakalamak
için değil, altı ay sonra unutulacak kuralı hatırlatmak için.

**M-12 · Benzersizlik kodda değil veritabanı kısıtında (11 Eylül) — 🟢.**
*"Bu personel no var mı"* diye sorup yazmak yetmez (iki eşzamanlı istek
ikisi de *yok* görür); kısıt yapısal engeller, kod `23505` → `PERSONEL_NO_TEKRAR`
(HTTP 409) çevirir. Bekçisi yok (A-3).

**M-14 · Giriş isteği firma kısa adını taşır.** `users` benzersizliği
`(tenant_id, eposta)`: aynı kişi iki firmada kullanıcı olabilir. Canlıda
firma alt alan adından gelecek (`anadolu-cm.tshift.com`).

**M-15 · Kapsam zorunluluğu: engelle *ve* güvenli davran (12 Eylül) — ⏳
kullanıcı yönetimi ekranıyla.** Kapsamı atanmayı unutulan bir departman
müdürü şartname v1.1'e göre bütün firmayı görecekti (sessiz yetki
genişlemesi); kod bilerek tersi yazıldı — kapsam satırı yoksa **hiçbir şey**
görmez (Y-8 testi) ve şartname v1.2 koda uyduruldu. Departman silinince kapsam
satırları onunla gider; bu yüzden hem arayüz/API engeller hem veritabanı
görünür kılar (yasaklamaz — içe aktarma politikasıyla çelişirdi).

**Henüz yazılmayan altyapı kararları:** eşzamanlılık — satır sürümü ve
idempotency (A-7; plan editörünün önkoşulu, bozulan veriyi sonradan tespit
etmek zor); PgBouncer / oturum değişkeni (A-8); KVKK — saklama, silme talebi,
anonimleştirme (A-9); barındırma (satış sonrası).

### 3.2 Motor katmanı

**M-09 · Planlama motoru ayrı Python + OR-Tools CP-SAT servisi — 🔴 yeniden
yazım.** *Ölçülmüş dayanak (spike, Eylül):* CP-SAT %99,5 hedef kapsama + 0
fazla mesai; açgözlü (greedy) algoritma %95,7 + 92 saat, 2.000 kişide
**geçersiz plan** üretti; CP-SAT 2.000 çalışanda 60 saniyede %98,9 kapsama.
*Elenen:* Go (resmî OR-Tools bağlayıcısı yok), .NET içinde motor. HTTP
uçları: `/evaluate` (bir planı denetle), `/solve` (plan üret), `/suggest`
(öneri — henüz yok, bilerek 501). .NET backend henüz çağırmıyor; kuyruk ve
sözleşme tasarımı açık (§11).

**Dört bağımsız parça, biri diğerinin işini onaylamaz (şartname §7.6):**
girdi şema doğrulaması → **çözücü** (plan üretir, denetlemez) → **bağımsız
doğrulayıcı** (planı sıfırdan kurallara karşı denetler, çözücünün *"geçerli"*
bayrağına bakmaz) → puan. Çözücü ile doğrulayıcı birbirini **import etmez**;
bir test import ağacını denetler ve üçüncü bir ortak yerel modül çıkarılmasını
da yakalar. *Neden:* optimizasyonda *"doğru çıktı"* tek bir beklenen listeyle
sınanamaz — aynı girdiye çok sayıda geçerli plan var. Çözücüyü ve testini aynı
el yazarsa yanlış kural yorumu ikisinde de tutarlı tekrar eder ve test yeşil
yanar. Bu yüzden zaman aritmetiği bile iki yerde **bilerek farklı** yazıldı
(doğrulayıcı mutlak saat aralıklarıyla, çözücü çeyrek saat dilimleriyle);
*"aynı hesabı iki kez yazmayalım"* deyip ortak yardımcı çıkarmak burada
maliyet değil güvence kaybıdır.

**M-10 · Kurallar veride, kodda değil — 🔴 motorun tamamı.** 41 kuralın
*türü* kodda (ne ölçtüğü), *değeri* veride (firma parametresi: günlük azami
11 saat, haftalık fazla mesai tavanı profile göre 0/10/15, adalet eşiği…).
Yanlış kural kod değişikliği değil parametre değişikliği; denetim kaydı
sayesinde *"bu plan hangi kural sürümüyle üretildi"* cevaplanabilir.

**M-11 · Zaman: UTC + genişletilmiş saat modeli — 🔴 her plan yeniden
yorumlanır.** Saklama UTC; vardiya gece yarısını aşabildiği için saat 24'ü
geçen gösterim (23:00–07:00 = 23–31). Yaz saati geçişi ertelendi (altyapı
duruyor). Gerçek veride 182 gece-yarısı-aşan atama var; bu model gerçek
veriyle uçtan uca sınanmadı (A-5).

---

## 4 · Motor nasıl çalışıyor ve neden böyle

### 4.1 Model — ne arıyoruz

- **Karar değişkenleri:** her (çalışan, gün, vardiya şablonu) üçlüsü için bir
  0/1 değişken — *bu kişi o gün o şablonda çalışıyor mu*; her vardiya için
  yemek molasının ve kısa dinlenmelerin hangi çeyrek saatte başlayacağını
  söyleyen 0/1 adaylar (K-34: motorun zaman birimi çeyrek saat). 500 kişilik
  sette model **633.591 değişken, 771.332 kısıt**; kurulması ~50 sn.
- **Sert kurallar** kısıttır, çiğnenemez: haftalık 45 saat normal çalışma
  sınırı, günlük azami 11 saat, hafta tatili, 11 saat vardiya arası dinlenme,
  gece sınırları, asgari kapsama (her saat en az N kişi), mola hakkı, izin…
- **Yumuşak kurallar** cezadır: hedef kapsamanın altında kalan her kişi-saat
  (ağırlık DENGELI 9 / KAPSAMA 20 / CALISAN 5), hedefin üstüne çıkan,
  **fazla mesai (dakika başına 50 puan — bir saat 3.000)**, adalet dengesi,
  saat dengesi, mola kapsaması. Amaç fonksiyonu = ağırlık × ceza toplamı;
  profil ağırlık sütununu seçer. **Hakem ağırlıklardır:** motor hiçbir
  yumuşak kuralı mutlak saymaz; hangi planın *"daha iyi"* olduğuna puan karar
  verir (bu cümle §5'te sınanacak).
- **Adalet nasıl puanlanır (K-27, K-29, 16 Eylül):** ihlal eşiği *"ortalamadan
  2 fazla"* yalnız doğrulayıcıda sayılır; motorda ise eşiğin altındaki
  dağılımlar arasında **artan marjinal maliyetli** bir gradyan seçim yapar
  (üçüncü cumartesi ikinciden pahalı). Ölçülmüştü: eşik tek başına amaç
  fonksiyonuna konunca eşiğin altındaki bütün dağılımlar sıfır ceza aldı ve
  KAPSAMA ile CALISAN profilleri birebir aynı planı üretti — *"üç bakışlı
  plan"* iddiası çalışmıyordu. Üç kartın birbirinden farklı çıkmasını sağlayan
  mekanizma bu gradyan.

### 4.2 Süre: ne kadar arar, ne zaman durur, ne söz verir

**K-28 · Erken dur, bekletme (16 Eylül, Mustafa).** Soru: optimuma çok
yaklaşmışken kalan süre sonuna kadar kullanılmalı mı? Karar: durma koşulları
**optimuma %2 yakınlık** ya da **2 dakikadır iyileşme yok**; üstte mutlak
bütçe. Gerekçe: 3. dakikada bulunan planla 15. dakikadakinin farkı sahada 1–2
saatlik kapsama; planı bekleyen yönetici için 12 dakika daha değerli.
Çıktıdaki `durma_sebebi` hangisinin durdurduğunu söyler.

**K-48 · Bütçe arama süresidir; model kurma ayrı kalem (1 Ekim).** Üç tam
ölçekli koşu *"en fazla 900 sn"* deyip 958 sn sürdü: model kurma (~50–78 sn)
bütçenin dışındaydı. Mustafa: *"Ekranda 'modelleme 58, plan 900 sn' gibi
belirtsek…"* Seçilen bu: `azami_saniye` = arama; ekranda iki satır, toplam
bekleme ikisinin toplamı. Gerekçe: zamanı yetmeyen taraf arama.

**K-35 · Süre seçimi, kanıtlanmış yakınlık, "İyileştir" (28 Eylül,
Mustafa).** *Çözülen sorun:* motor aynı girdiye her seferinde aynı planı
vermiyor (35 kişi, 25 sn: 21.905 ve 22.715) — sekiz arama işçisi paralel
arıyor, hangisinin önce iyi plan bulduğu yarışa bağlı. Tek işçiyle
tekrarlanabilir olur ama aynı sürede plan **46 kat kötü** (1.010.039).
Mustafa: *"Yönetici tekrar çalıştırdığında daha iyi bir plan gelip
gelmeyeceğini nasıl bilecek? Bunu bilmezse nasıl güvenecek?"* Karar —
tekrarlanabilirlik değil **görünürlük + birikim**: (1) süre seçimi 10 / 15 /
30 dk, yanına *"%85 optimum"* gibi yüzde **yazılmaz** (eğri sahneye göre
değişir; önden söz çoğu kiracıda yalan olur); (2) sonuç kartında çözücünün
**kanıtladığı** alt sınırdan gelen yakınlık gösterilir (*"bu plan teorik en
iyisinin %90'ı kadar iyi"* — tahmin değil garanti; yönetici *"tekrar denesem
değer mi"* sorusunu kendi planı için cevaplar); (3) **"İyileştir"** düğmesi:
sıfırdan üretmez, mevcut planı çözücüye başlangıç noktası verir, amacı
küçülttüğü için plan kötüleşmez — zar atmıyor, biriktiriyor (ölçüldü: 15 →
+20 → +25 sn ile yakınlık %24,5 → %44,3 → %71,2). ⚠ (2)'nin bugünkü durumu
§4.6'da: büyük modelde kanıtlanmış yakınlık **gösterilemiyor**.

### 4.3 Yayın kapısı: hiçbir plan denetlenmeden kullanıcıya gösterilmez

**K-16 · Çözülmemiş ihlalle plan yayınlanamaz.** Bağımsız doğrulayıcının
bulduğu sert ihlal varken plan yayınlanmaz; yönetici *"kabul ediyorum"*
diyebildiği kurallar ayrı (K-10, K-23: kabul yetkisi = yayın yetkisi).

**K-49 · Denetlenemeyen kural da kapıdan geçemez — üç kademe (1 Ekim,
Mustafa: "onaylıyorum").** Dış inceleme bulgusu (T-18): doğrulayıcıda gövdesi
yazılmamış ama aktif bir kural varken cevap aynı anda *"bu kuralı kontrol
edemedim"* ve *"yayınlayabilirsin"* diyordu — kapı yalnız bulunan ihlallere
bakıyordu, *"bakamadım"* geçiyordu. Karar: kontrol edilemeyen kuralın etkisi
türüne göre — (1) **sert ve yasal** (gece sınırı gibi): plan yayınlanamaz,
firma kanunun kontrolünü kabul ederek geçemez; (2) **sert ama firma kuralı**
(*"her saat bir takım lideri"*): plan gerekçeli **kabul bekler**, gerekçesiz
kabul kabul sayılmaz; (3) **yumuşak**: yalnız raporlanır. *"Bakamadım"* sayılan
hâller: gövdesi yazılmamış aktif kural; yazılmış kuralın bakılamayan parçası
(örneğin gereklilik satırı olmayan yetkinlik kapsaması). Kabul kaydı plan
başına girdiyle gelir (`{kod, gerekce, onaylayan}`).

### 4.4 "İmkânsız" ile "yetiştiremedim" ayrı cevaplardır — K-37 (29 Eylül)

Çözücü plansız döndüğünde iki ayrı durum var: `INFEASIBLE` — *kanıtladım,
böyle plan yok* → `cozumsuz`, teşhis koşar; `UNKNOWN` — *süre doldu* →
`sure_yetmedi`, teşhis **koşmaz**. *Neden:* bir yöneticiye *"çözümsüz"* demek
*"bu talebi bu kadroyla karşılamak imkânsız"* demektir — personel alımına
kadar giden bir karar; oysa gerçek *"biz yetiştiremedik"* olabilir. Teşhis de
ucuz değil: her sert kuralı tek tek gevşetip yeniden çözer (ölçüldü: 45
saniyelik bütçe, toplam 470 saniye). *"Neden olduğunu araştır"* düğmesi:
teşhis kullanıcı isterse koşar ve o zaman da **kanıt değildir** diye
işaretlenir. Ayrıca ucuz bir ön kontrol var: hiçbir şablonun ulaşamadığı bir
talep hücresi varsa çözücü hiç çalıştırılmaz (105 kişilik gerçek sahnede 292
saniye tasarruf).

### 4.5 Üç aşamalı arama — K-59, K-60: neden tek aramayla olmadı

Tam ölçekte (28 Eylül, 350 kişi) CP-SAT'e modeli olduğu gibi verince **45
saniyede hiç plan bulamıyordu** (amaç varken); amaç kaldırılınca 32 saniyede
plan vardı. Yani *geçerli* plan bulmak kolay, *iyileştirmek* zor. Çözücü
bütün bütçeyi iyileştirmeye harcayıp eli boş dönüyor, kullanıcı bunu
*"çözümsüz"* görüyordu. Çözüm aramayı üçe bölmek oldu:

| Aşama | Ne yapar | Süre payı (900 sn) | Dayanak |
|---|---|---|---|
| **1 · Geçerli plan** | Amaç kapalı; molalar şablonun ideal yerine **sabit** (değişkenlerin üçte ikisi mola yerleşimi, geçerli plan için seçilmesi gerekmez — 500 kişide 529.480 aday kapatılır) | en çok 120 sn (%20) | Tam ölçekte 120 sn'de üç koşuda da plan bulamayan arama, molalar sabitlenince ~10 sn'de buluyor (1 Ekim) |
| **2 · İyileştirme** (K-59, 3 Ekim, Mustafa: *"olsun"*) | Amaç geri konur, molalar hâlâ sabit, atamalar iyileştirilir; 1'in planı **başlangıç çözümü (ipucu)** | %80 (720 sn) | 500 kişi, 600 sn: fazla mesai 475–511 saat → 120 sn iyileştirmeyle 60–83, 240 sn ile 45–53, 480 sn ile 34–38; hedef eksiği 1.199–1.248 → 360–366 kişi-saat |
| **3 · Mola adımı** (K-60, 4 Ekim, Mustafa: *"evet"*) | Atamalar 2'nin planına **sabit**, yalnız molaların yeri aranır; bu kısıtlı problemin **kanıtlı optimumunda** durur | kalan (~170 sn; adım 42–47 sn) | Ortak arama (atama + mola birlikte) 347 sn'de mola açığını 193–202'ye indirip bütçe dolunca hâlâ iyileşiyordu; mola adımı ≈45 sn'de 177–188 ve kanıtlı optimum; ortak aramanın atamalara dokunan payı kazancın %6'sı |

**İpucu (hint)** CP-SAT'in mekanizması: çözücüye *"şu değerler geçerli bir
çözüm, buradan başla"* denir. İpucu **tam** yazılır (bütün değişkenler):
yarım ipucuyu CP-SAT *"onarmaya"* çalışıp 10 çelişkiden sonra vazgeçiyordu,
ilk plan 57–101 sn gecikiyordu. **İpucu korunur:** iyileştirmenin döndürdüğü
plan başlangıç planından kötüyse ipucu ezilmez (7 Ekim, bağımsız inceleme).
Süre paylaşımı (%80) bir **kalibrasyon**dur, karar değil: %90 da ölçüldü
(bulgu 19, üçer koşu), fark yok, %80 kaldı. Mola adımı aynı şablondaki herkesin
aynı dakikada molaya çıkmasını önler (K-32'nin kararı); hücre başına en kötü
çeyrekte asgarinin altındaki kişi sayısını 5,9'dan 0,4–0,5'e indiriyor.

### 4.6 O-16 — motor *"optimum, uzaklık %0"* dedi; kanıtladığı yalnız mola yerleşimiydi

**Ne oldu (4–6 Ekim).** 3. aşama kısıtlı problemin optimumunu kanıtlayınca
çıktı bunu genel alanlara yazdı: `durma_sebebi: optimum`, `alt_sinir ==
amac_degeri`, `optimuma_uzaklik_yuzde: 0`. 5–6 Ekim'in 15 tam ölçekli
koşusunun hepsi böyle bitti. K-35'in sonuç kartı yazılmış olsaydı her planda
*"%100"* gösterecekti. **Ölçüm (bulgu 20):** *"optimum · %0"* denen DENGELI
planları 105.742–148.431 puan; aynı girdide **26.589**'luk plan var. *"Optimum"*
denen bir planın dört kat iyisi olamaz.

**Neden.** Çözücünün alt sınırı **çözdüğü modelin** sınırıdır; model
daraltılınca (atamalar sabit) sınırın anlamı daraldı, alanın adı aynı kaldı.
Daha kötüsü: bunu 4 Ekim'de doğru davranış sanıp teste ve şartnameye yazdım —
bekçi hatayı koruyordu. Fark eden test değil, üç profilin yan yana gelmesi:
CALISAN planı DENGELI ağırlıklarıyla yeniden fiyatlanınca 26,6 bin çıktı.

**Düzeltme (6 Ekim) ve kural.** *Çözülen model tam model değilse sınır
küresel alana yazılmaz:* `alt_sinir` ve `optimuma_uzaklik_yuzde` **null**
(sıfır ya da kısıtlı sınır yazmak yalan garanti olurdu), adımın kendi sınırı
`mola_adimi_alt_sinir`, sebep `mola_adimi_optimum`. Aynı sınıf aynı gün ikinci
kez çıktı (ölçüm seçeneğinde) ve onu bağımsız inceleme buldu; kural
genelleştirildi (*"ana aşamanın çözdüğü model tam model mi"*). Bilerek kötü
planla uçtan uca test + 18 mutasyon. **Kapatmadığı:** büyük modelde artık hiç
küresel sınır yok — K-35'in kartı için tam modelde ayrı bir *"sınır adımı"*
gerekiyor; açık.

### 4.7 Donmuş gün — K-54 (1 Ekim): yayınlanmış plan motora gelir, geçmiş aynen kalır

Dış inceleme (T-29): *"geçmiş yeniden planlanamaz"* sözünün tek bekçisi
`DONMUS_GUN` kuralı, hiçbir şeyin üretmediği bir işarete bakıyordu — ölüydü.
Karar: yayınlanmış plan (`mevcut_plan`) motora girdi olarak gelir; donmuş
günün satırları çıktıya **aynen** aktarılır, o günlere yeni atama yazılmaz,
donmuş atamalar modelde sabittir ve günler arası kurallar onları gerçek
sayar (pazartesi gece çalışan salı 11:00'den önce başlayamaz). Geçmişin
**kendisi yargılanmaz**: yalnız donmuş güne ait kısıtlar düşer (0,1 ölçekte
8.945 kısıt); geçmiş bir sınırı zaten aşmışsa sınır ulaşılabilir en yakın
noktaya kırpılır (plan yine çözülür). Doğrulayıcıda yalnız donmuş günlere
dayanan ihlaller `gecmis: true` işaretlenir — listede kalır ama yayın kapısı
saymaz (*"olan oldu"*; yönetici geçmişi değiştiremez, geleceği yayınlayamaz
çıkmazına girmesin). Mustafa'nın eki: yönetici geçmiş günleri bilgisi
dahilinde düzenleyebilir, gelecek günlerde kişileri kilitleyebilir; motora
düzenleme bittikten sonra gider.

---

## 5 · Fazla mesai: kararlar, hata, düzeltme, ölçüm

Ürünün amacı fazla mesai çıkarmadan kaynağı en iyi kullanmak olduğu için bu
bölüm ayrıntılı. Sıra kronolojik: karar (K-30) → tanım (K-57) → tam ölçekte
tutmadığı görüldü → yeni karar (K-61) → hatalı uygulama ve düzeltme (O-18) →
ölçüm (bulgu 23).

### 5.1 K-30 · Hedef için asla, asgari zorlarsa minimum (16 Eylül, Mustafa)

> *"Zaten hedef hiç gitmemek. Gidilecekse de minimum gitmek."*

| Durum | Davranış |
|---|---|
| Yalnız **hedef** kapsama iyileşecek | Fazla mesai **yapılmaz** — hedef eksik bırakılır |
| **Asgari** kapsama (sert) fazla mesaisiz tutmuyor | Fazla mesai **yapılır**, gereken kadar |
| Profil tavanı (CALISAN 0 / DENGELI 10 / KAPSAMA 15 saat) zorunlu aşıma yetmiyor | Plan **çözümsüz** olur |

Motorda bunu sağlayan şey fazla mesai cezasının kapsama kazancından çok ağır
olmasıdır (bir saat 3.000 puan, kaçırılan bir hedef kişi-saati 9–20). Tavan
*isteğe bağlı* fazla mesai için hiç kullanılmaz (ceza karşılar), *zorunlu*
fazla mesainin sınırını o çizer. **7 Ekim (Mustafa):** tablonun ilk satırı
*ağırlıkların sonucudur*, kodda sert bir kural değil — 15 dakikalık bir fazla
mesai bütün haftayı düzeltiyorsa ağırlıklar onu seçer (§5.4).

### 5.2 K-57 · "Fazla mesai" tek tanımdır: yasal (2 Ekim, Mustafa)

Kalite ölçümü aynı plan için **üç ayrı "fazla mesai" sayısı** olduğunu
gösterdi (49 kişi): çözücünün cezaladığı 5–10 saat (çalışma süresi − sözleşme),
doğrulayıcının metriği 116–125 saat (ücret saati − sözleşme), motorun kendi
metriği 117–127 (brüt − yemek). Ekranda 120 saat görünecek, motor 5 saati
optimize ediyor olacaktı.

> *"Fazla mesai bizim için çok önemli bir kriter. Firmanın zaten baş edemediği
> konulardan… Fazla mesai üç ayrı sayı tarafında yasal tanımı kabul edeceğiz.
> Yarı zamanlılar… 45 saate kadar fazla mesai saymadan, çarpanı normal mesai
> ile aynıdır."* — Mustafa

**Tanım (her yerde):** fazla mesai = çalışma süresi (vardiya − **bütün**
molalar, ücretli dinlenme dahil; İş K. md. 68) − sözleşme saati, sıfırdan
küçükse sıfır. Yarı zamanlıya **yazılmaz** (45 saate kadar *"yarı zamanlının
ek mesaisi"*, çarpan aynı; K-58: yarı zamanlıya sözleşme saati tanımlanmaz,
baz 30 / tavan 45 kanundan). Ücret farkı ayrı alanda: *sözleşme üstü ücretli
saat* — fazla mesai değildir, raporlanır.

### 5.3 K-61 · Motor önce fazla mesaisiz plan arar; hakem ağırlıklardır (6 Ekim)

**Gözlem (6 Ekim, bulgu 20; 500 kişi, 900 sn, üç profil, üçer koşu).**
DENGELI 26–40,5 saat, KAPSAMA 10–14 saat fazla mesai yazdı; aynı girdide
CALISAN (tavan 0, yani **sert** sınır) üç koşuda da **0 saatle**
yayınlanabilir plan buldu. CALISAN'ın planı DENGELI'nin kendi ağırlıklarıyla
26,6–26,7 bin puan; DENGELI'nin kendi bulduğu 106–148 bin. Fazla mesai dışı
kalemler %0,2 oynuyor — koşudan koşuya farkın tamamı fazla mesai. **Teşhis:**
fazla mesai verinin zorladığı bir şey değil, **aramanın artığı** — yumuşak
ceza (dakika başı 50) süre içinde fazla mesaiyi sıfıra itemiyor; süreyi
900'e çıkarmak da kapatmadı; sert sınır 13–33 saniyede sıfırlıyor.

**Karar (Mustafa, 6 Ekim 23:44: "Evet") ve ilkesi:**

> *"…elimizdeki tüm kriterleri karşılayan en iyi plan fazla mesaisiz olmalı.
> Ama matematiksel olarak kurduğumuz modelde ağırlıklar baz alındığında
> örneğin 3 saat fazla mesai içeren en optimum plan var ve fazla mesaisiz
> plandan oldukça daha optimum bir plan ise en optimum olanı seçmeliyiz."*

**Ne demek (uygulanan hâli, 7 Ekim):** 1. aşama geçerli planı **fazla mesai
değişkenleri 0'a sabitken** arar (kısıt eklenmez, değişkenlerin alanı
daraltılır; *"kimse sözleşme saatini aşamaz"* demektir).

| Durum | Ne olur |
|---|---|
| Fazla mesaisiz plan **bulundu** | O plan yalnız **başlangıç noktasıdır**: fazla mesai alanları geri açılır, 2. ve 3. aşama tam modelde, tam ağırlıklarla koşar — fazla mesai ancak puana göre **kazanıyorsa** plana girer |
| **Yok** (çözücü kanıtladı) | Alanlar açılır, eski yol işler; nota *"fazla mesaisiz plan yok (molalar sabitken kanıtlandı)"* düşer — zorunlu fazla mesai yolu kapanmaz (K-38: haftalık 45 saat *normal çalışma* sınırıdır, toplam tavan değil; asgari ancak fazla mesaiyle tutuyorsa fazla mesai yapılır) |
| Bu sürede **bulunamadı** | Aynı; not *"bu sürede bulunamadı"* der — dönen plan fazla mesaili olabilir ve fazla mesaisizi var olabilir (§6.1'in konusu) |

Başarısız denemenin süresi iyileştirmenin payından düşer (mola adımına kalan
süre korunur). Kapsam yalnız iki aşamalı akış; küçük model tek aramada aynı
kararı ağırlıklarla verir.

### 5.4 O-18 · İlk uygulama ilkeyi çiğniyordu; bağımsız inceleme yakaladı (7 Ekim)

**Ne oldu.** 6 Ekim gecesi yazdığım sürüm fazla mesaisiz planı bulunca fazla
mesaiyi **bütün aşamalarda 0'da tutuyordu** (*"sert kesim"*) ve bunu bir
*"ağırlık koşulu"* ile savunuyordum: *"bir saat fazla mesai 3.000 puan,
hedefin bir kişi-saat altında kalmak 9 puan; fazla mesaili plan daha iyi
olamaz."* Mustafa'ya *"bu kurda oluşmaz"* dedim, şartnameye *"hesapla
gösterildi"* yazdım, tek sahneyle test yazdım.

**Karşı örnek (iki bağımsız inceleme ajanı, ürün ağırlıklarında).** Şablon
saatleri sözleşme saatini tam döşemiyorsa — 7,5 × 5 + 7,75 = **45 saat 15
dakika** — fazla mesaisiz tek seçenek bir günü düşürmektir (7,25 saat sözleşme
altı: saat dengesi cezası 2.175) ya da talebin dışındaki bir şablondur. **15
dakikalık bir fazla mesai adımı bütün haftanın kilidini açıyor:** kanıtlı
optimum 750 puan iken sert kesim 2.256 (DENGELI, tek kişi), 880 (KAPSAMA);
12 kişide 9.000'e karşı 12.000 — tam 3 saat, Mustafa'nın örneği. *"Oluşmaz"*
dediğim şey ürün ağırlıklarında oluşuyordu.

**Düzeltme.** Bulunan fazla mesaisiz plan yalnız başlangıç noktası (§5.3
tablosu); ağırlık koşulu kalktı; sert kesim ölçüm seçeneği olarak duruyor;
dört karşı örnek sahnesi test oldu; Mustafa'nın örneğinde fazla mesaisiz plan
bulunsa da 3 saatlik plan seçiliyor. **Kalıcı ders:** *"oluşmaz / olamaz"*
cümlesi karşı örnek avı (betik, sayı) olmadan yazılmaz; ilke koşula
çevrilmez — karar *"hakem ağırlıklardır"* diyorsa kod ağırlıkları uygular,
ne zaman yanılacaklarını tahmin eden kapı yazmaz; bağımsız inceleme kod
*"indi"* denmeden önce gelir.

### 5.5 Ölçüm — bulgu 23 (7 Ekim, 500 kişi, 900 sn, üçer koşu)

Fazla mesai altı koşunun altısında **0**. DENGELI 26.634–26.705 puan (sert
kesim 26.407–26.494; +%0,8 — karar kuralı: kapandı). KAPSAMA 14.132–15.028
(sert 13.834–13.914; +%5,2, yayılım %6,3) — fark fazla mesai değil
**yakınsama**: 359 serbest fazla mesai değişkeniyle 720 sn'lik iyileştirme
bitmiyor; 1200 sn'de fark +%1,5'e indi (büyük kısmı bütçe). Hibrit arama
(iyileştirme fazla mesai kapalı + serbest son tur) aday; dört yumuşak kural
yazılmadan kalibrasyon ölçümleri **dondu** (§7).

### 5.6 K-64 · Puan eşitse fazla mesaisiz plan (7 Ekim, Mustafa: "evet") — ⏳

Ağırlıklı amaç iki planı eşit puanlıyorsa (ör. 3.252 = 3.252: biri 0,5 saat
fazla mesaili, öteki saat dengesinde 300 dk uzak) motor fazla mesaisizi
seçer; K-61 ilkesini bozmaz, yalnız eşitlik fazla mesaisizden yana kırılır.
İnceleme A'nın 640 sahnelik avında 1 eşitlik çıktı — nadir ama ilkeye
dokunuyor. İki uygulama yolu var (amaçta ε ya da çözümden sonra eşitlik
kontrolü), ölçülmeden seçilmez; dört yumuşak kuraldan sonra.

---

## 6 · Bu hafta koda inen iki şey: yeniden başlatma ve K-63

### 6.1 Bulgu 25 · Fazla mesaisiz ilk aramanın ağır kuyruğu → yeniden başlatma

**Gözlem (7 Ekim gece koşusu, 1200 sn × 3, DENGELI).** İki koşu 26.602 /
26.823; üçüncüsü **116.976** — fazla mesaisiz ilk arama 120 saniyelik payında
plan bulamadı, motor eski yola düştü, plan **30 saat fazla mesaiyle** döndü
(bulgu 20'nin artığı aynen). 6 Ekim'den beri bu arama 18 koşunun 17'sinde
8,6–21 sn sürmüştü; 1'inde > 120 sn. **K-61 bu kuyruk kapanmadan "kapandı"
denemezdi**, çünkü ürün yolunun kalitesi bu aramaya bağlı.

**Kuyruk ölçümü (7 Ekim 18:00, `kuyruk.py`).** Aynı 500 kişilik model, aynı
hazırlık, 35 deneme (30 farklı rastgelelik tohumu + 5 tekrar), 120 sn tavan:
hepsi buldu; medyan 7,5 sn, %90 13 sn, en uzun 61,9 sn; P(T > 40 sn) = 2/35.
CP-SAT paralel işçilerle koşar, zamanlama koşudan koşuya değişir — aynı
tohumda bile 7× fark ölçüldü. Toplam 53 gözlemde 1 × > 120 sn: kuyruk ince
ama gerçek.

**O-19 (18:40).** Araçta ve kayıtta *"tohum 0 = CP-SAT'in varsayılanı =
motorun kullandığı"* yazmıştım — hafızadan. Kütüphanenin varsayılanı **1**;
motor tohum yazmadığı için 1 ile arıyordu. Sonuç değişmedi (aynı tohumda 7×
fark gözlemi herhangi bir tohum için aynı okunur), etiket yanlıştı.
Düzeltildi; ders: kütüphane varsayılanı hafızadan yazılmaz, koddan okunur ve
test çiviler.

**Çare — koda indi (7 Ekim).** 120 saniyelik payı **3 × 40 saniyelik
denemeye bölmek**, her deneme farklı tohumla (1 → 2 → 3), ilk bulunan alınır;
çözücü *"fazla mesaisiz plan yok"* diye kanıt verirse kalan denemeler
yapılmaz (tohum kanıtı değiştirmez). Tipik koşu (7 sn) etkilenmez; kuyruğun
üç kez üst üste gelme olasılığı (denemeler bağımsız sayılarak) ≈ %0,02 —
çevrimdışı tahmin. Ayar `fazla_mesaisiz_deneme`; **karar kuralı koşudan önce
yazıldı:** 900 sn × 3'te fazla mesai 0 ve puan önceki düzeyde, hiçbir koşu
*"bulunamadı"* yoluna düşmemiş, politika kipinde 20 koşunun hiçbiri
bulunamamış değilse → varsayılan 3 olur, K-61 kapanır.

**Ölçüm sonucu (8 Ekim 00:10, Mustafa'nın makinesi).** `fm_once_deneme3`
900 sn × 3: puan **26.498 / 26.700 / 26.736**, fazla mesai üçünde de **0**,
0 sert ihlal, hepsi yayınlanabilir; fazla mesaisiz arama üçünde de ilk
denemede buldu (7,3 / 6,7 / 7,1 sn). Politika kipi 20 koşu: hepsi ilk
denemede, medyan 6,6 sn, en uzun 8,4 sn. **Karar kuralı tuttu → varsayılan 3
olacak, K-61 kapanıyor** (kod değişikliği 8 Ekim'de). Dürüst not: bu 23
koşunun hiçbirinde yeniden başlatma **devreye girmedi** (hepsi ilk denemede
bulundu); seçeneğin koruma değeri gözlemlenmedi, 18:00 kuyruk ölçümüne ve
çevrimdışı tahmine dayanıyor. Zararsız olduğu ölçüldü (puan ve süre aynı).

### 6.2 K-63 · Mola adımı yetişmezse 2. aşamanın planı notla döner; müşteriye süre aralığı (7 Ekim)

**Gözlem (bulgu 24).** 20 saniyelik kısa bütçede 1. aşama (fazla mesaisiz
arama 1,3 sn + iyileştirme 16 sn) 17,7 sn aldı, mola adımına 2,3 sn kaldı,
adım ilk çözümünü bulamadı → *"süre yetmedi"*, plan yok. Oysa iyileştirmenin
geçerli planı eldeydi (molalar şablonun ideal yerinde — tam modelin geçerli
bir çözümü). 0.2 ölçekte 20 sn'lik **doğal** koşuda da aynısı oldu (mola
adımına 1,68 sn kaldı). 500 kişi / 900 sn'de görülmedi (adıma ~170 sn kalıyor,
adım 42–47 sn).

**Karar (Mustafa, 7 Ekim 07:18).** *"Burada belki de müşteriye bir aralık
vermeliyiz. Planın 15-20 dk arasında tamamlanacağı gibi. Yani kafadan üst
sınır veriyoruz bu tür durumlar için. Bence bu çalışır. Ayrıca 2. aşamanın
planı notla dönsün önerine notumla birlikte katılıyorum."* İki parça: (1)
**motor** — mola adımı plansız dönerse 2. aşamanın planı döner, nota
*"molalar şablonun ideal yerinde; mola adımı yetişmedi"* düşer; (2) **ürün** —
kullanıcıya tek süre değil aralık (*"15–20 dk"*): alt uç olağan tamamlanma,
üst uç kafadan tavan, motor üst uçta elindeki en iyi planla döner. Aralığın
sayıları tam ölçekte ölçülmeden şartnameye yazılmaz.

**Uygulama (7 Ekim akşamı).** Ana aşama plansız dönerse (yalnız *"süre
yetmedi"* hâlinde; *"imkânsız"* kanıtı K-37 yolunda kalır) ve elde 2. aşamanın
**tam** ipucusu varsa: karar değişkenleri (atamalar ve molalar) ipucu
değerine sabitlenir, ceza değişkenlerini amaç en küçüğe indirir — böylece
raporlanan puan planın **gerçek** puanıdır. İlk sürüm bütün değişkenleri
ipucuya sabitliyordu; bağımsız inceleme ipucunun ceza değerlerinin gevşek
olabildiğini ölçtü (2. aşamanın planında +%1,2, 1. aşamanın amaçsız planında
**+%85–89**) — K-35'in kartı planları puanla kıyasladığı için düzeltildi.
Çıktıda `durma_sebebi: mola_adimi_yetismedi`, sınır ve yakınlık alanları
null (kanıt yok), `ipucu_plani {bulundu, saniye, durum, kaynak}` — `kaynak`
dönen planın hangi aşamadan geldiğini söyler (iyileştirme plan bulamadıysa
1. aşamanın amaçsız planı döner ve not bunu açıkça der). İki aşama yoksa
(küçük model; başlangıç planı verilen *"İyileştir"* koşusu — ipucu yarımdır)
eski cevap. Çevirme süresi bütçenin dışındaki tek kalem: 0.1 ölçekte 0,33 sn,
0.2'de 0,6–0,8 sn, tam ölçekte ölçülmedi (dışdeğerleme ~4 sn; tavan 30 sn).

---

## 7 · Kaliteyi nasıl ölçüyoruz; ne biliyoruz, ne bilmiyoruz

**T-60** projenin tek açık 🔴 maddesi (29 Eylül'den beri): *"plan yasal
çıkıyor ama kalitesi kanıtlı değil."* 29 Eylül'de ilk tam ölçek planı optimuma
%98,3 uzaktı; bugün planın en iyi plan olup olmadığını **söyleyemiyoruz**
(§4.6), ama fazla mesai sıfıra indi ve koşudan koşuya fark DENGELI'de %0,3'e.

**Yöntem.**
- `kalite-olc.py`: aynı 500 kişilik sahne, aynı makine, bir seferde yalnız
  bir şey değişir (*yapılandırma*); **üçer koşu** — 28 Eylül'de aynı girdi
  iki koşuda 21.905 ve 22.715 vermişti, tek koşudan sonuç çıkmaz. Kayıt JSON:
  amaç değerinin kural başına kırılımı, iyileşme eğrisi, süre kalemleri,
  doğrulayıcının bağımsız ölçümü (hedef eksiği, aşım, fazla mesai).
- **Karar kuralı koşudan önce yazılır** (*"X ise ürün yolu değişir, değilse
  değişmez"*); sonuç kuralla okunur. Bu gece de öyle oldu (§6.1).
- Çözücüden bağımsız bir **kapasite tabanı**: herkes azami çalışsa bile hedefin
  ne kadarı açıkta kalır; plan bu tabana yakınsa *"motor kötü"* değil *"kadro
  yetmiyor"*dur. Bugünkü sette taban 0 — set kıtlık taşımıyor.

**Bilinenler (500 kişi, %95, 900 sn).** 0 sert ihlal, yayınlanabilir; fazla
mesai 0 (dokuz koşu üst üste); hedef kapsama %85–86 (eksik 343–376 kişi-saat,
hedefin üstünde 3.191–3.210 kişi-saat — puanın %36'sı hedef aşımı, %47'si
adalet); mola adımı sonrası en kötü çeyrekte asgarinin altındaki kişi 0,4–0,5;
model kurma ~50 sn; mola adımı ilk planını ~21 sn'de buluyor, kanıtlı
optimumu ~40 sn'de; iyileştirme 720 sn'nin tamamını kullanıyor (bu gece 648–677
çözüm; bulgu 23'te son iyileşme 684–717. sn — bütçe arttıkça hâlâ iyileşiyor,
yakınsama bitmiyor).

**Bilinmeyenler.**
1. Küresel alt sınır yok → optimuma yakınlık kanıtı yok (sınır adımı açık).
2. **Dört yumuşak kural yazılmadı:** ekip sürekliliği, plan kararlılığı (bir
   önceki plana sadakat), tercih karşılama (yarı zamanlı sözleşme
   esnekliğinin kullanımı), vardiya rotasyon yönü. Bunlar olmadan kalibrasyon
   ölçümleri (süre payları, hibrit, K-64) tekrar gerekir — **donduruldu**.
   Sıra (Mustafa, 7 Ekim 18:31): dört kural → veri seti v2 → merdiven
   ölçümleri.
3. **Veri seti** (K-62, 6–7 Ekim): bugünkü %95 seti kıtlık taşımıyor
   (asgari talep sözleşme saatlerinin %65'i, fazla mesai hiç zorunlu değil,
   geçen haftanın vardiyaları boş, herkes tek ekipte) — geçmişe bağlı
   kuralları ve zorunlu fazla mesaiyi sınamıyor; en iyi plan bilinmiyor
   (O-17: iki işi yapabilen kişi sette hiç yoktu). Karar: **cevabı bilinen beş
   seviyeli merdiven** — (1) tam oturan talep, referans plan bilinir; (2) sıkı
   kadro; (3) geçmişli hafta (geçen haftanın vardiyaları, donmuş günler,
   kilitler, yıllık tavana yakın kişiler); (4) zorunlu fazla mesai — en az
   fazla mesai x ve x'i tutturan plan önceden bilinir; (5a) dar kapı, (5b)
   imkânsız (*"bu plan üretilemez"* ve sebebi). Kriter seti seviyeler arasında
   aynı; kadro Satış 285 · Back Office 145 · Müşteri Hizmetleri 70, iki işi
   yapabilen 20 satışçı her seviyede (Mustafa: *"gün içinde satış çağrıları
   şiştiğinde backoffice'e çağrı gidebiliyor, gerçek planlamada da var"*),
   gece back office asgari 2. Araç yazılmadı.
4. Küçük ölçek (20 kişi) hiç sınanmadı; çözümsüzlük teşhisi orada birincil.
5. İki bitişik bulgu (bağımsız inceleme 3): K-61'in *ipucu koruma* kıyası
   gevşek puanla yapılıyor (karar Mustafa'da); donmuş gün × iki aşama mola
   alanlarını geçici açıyor, görünür etki ölçülmedi (sırada).

---

## 8 · Süreç ve bekçiler — hatalar nasıl yakalanıyor

Yılmaz'ın itirazına verilen asıl cevap bu bölüm.

| Katman | Ne | Büyüklük |
|---|---|---|
| Birim testleri | Motor **609**, backend **45** (gerçek PostgreSQL'e karşı, taklit yok — RLS taklitle sınanamaz) | her commit |
| Altın senaryolar | Şartnameden türetilmiş, motor yazılmadan **önce** ve motora bakmadan yazılmış kabul senaryoları (12; 7'si motoru sınar, 4'ü backend tarafında bekliyor) | `08-motor-testleri/v5/` |
| **Mutasyon koşturucu** | Elle seçilmiş **325** bozma: *"bu satırı tersine çevirirsem hangi test kırmızı yanar?"* Yanmıyorsa test eksik. Her bozma için dosya geri yazılır ve md5 ile doğrulanır; önbellek kapalı (bytecode tuzağı bir kez yaşandı). **Tam koşu 7 Ekim 22:15: 325'in hepsi öldü.** | `09-motor/mutasyon_kostur.py` |
| **Bağımsız inceleme** | Kod *"indi"* denmeden önce işi görmemiş ayrı bir ajan **karşı örnek** arar; raporu ve deney betikleri depoda arşivlenir. 7 Ekim'de iki kez işe yaradı (§5.4 O-18; §6.2 gevşek puan). | `08-motor-testleri/gercekci-veri-seti/kesif/…` |
| Dış tarama | Haftalık, farklı sağlayıcının modeli: kod şartnameye uyuyor mu; *"yanlış yayın izni"* ve *"sessiz veri atlama"* öncelikli | `05-inceleme/beceriler/` |
| `DENETIM.py` | Devir paketini denetler: kırık dosya yolu, bayat test adı, test sayısı iddiası, değişim günlüğü tazeliği, commit durumu; her oturum sonunda 0 hata şartı | depo kökü |
| Hata otopsileri | O-1…O-19: *ne oldu, nasıl göründü, ne yakaladı, **bir daha gelmesini ne engelliyor***. Kalıcı bekçisi olmayan düzeltme tamamlanmış sayılmaz. | `00-DEVIR/05-HATA-OTOPSILERI.md` |
| Devir paketi | Her karar gerekçesi ve tarihiyle (K-1…K-64), mimari kararlar geri alma bedeliyle, açık riskler numarasıyla, oturum günlükleri — bir ekibin kodu korkmadan devralması için | `00-DEVIR/` |

**Ölçüm disiplini:** her kalite iddiası tam ölçekte üçer koşuyla; karar kuralı
koşudan önce; *"hepsi öldü"* yalnız tam koşudan sonra yazılır (O-15: bir kez
grup koşularından toplanıp yanlış çıktı); yazılan her dosya makineden geri
okunup md5 ile doğrulanır (O-13: bir kez boş dosya gitti).

**Dürüst eleştiri (kendimize).** Bekçiler kodun ve deponun durumunu
yakalıyor; **cevapların** durumunu değil. Bir haftada iki kez *"bu kurda
oluşmaz"* dedim ve karşı örnek çıktı (O-18); bir kütüphane varsayılanını
hafızadan yazdım (O-19); 4 Ekim'de yanlış bir iddiayı teste yazıp bekçiye
korutturdum (O-16). Üçünü de bağımsız inceleme, ölçümün kendisi ya da kodu
okumak yakaladı — insan gözü değil. **11 Eylül'ün 7. sorusu hâlâ en önemli
soru:** hangi hata sınıfı bu kontrollerin hiçbirine takılmaz?

---

## 9 · Bugünkü durum — katman katman

| Katman | Durum | Ölçü / kaynak |
|---|---|---|
| **Şartname** | ✅ v1.4 yürürlükte; 63 değişiklik kaydı (son: 7 Ekim) | `02-spec/v1.4-master-spec.md` |
| **Veritabanı + çok kiracılık** | ✅ RLS + `FORCE`, iki rol, denetim kaydı sadece-eklenir; 7 mimari "yasa" testi | §3.1 |
| **Backend (.NET)** | ✅ Dikey dilim: kimlik, yetki (5 rol, 19 izin, kapsam), ~12 uç, **45 test**; CI (son bakılan 2 Ekim: yeşil) | `04-kod/` |
| **Frontend (Next.js)** | 🟡 Yalnız giriş + çalışan listesi + yeni kayıt; BFF | `04-kod/frontend/` |
| **Motor — doğrulayıcı** | ✅ 41 kuralın gövdeleri (4 yumuşak hariç); yayın kapısı üç kademe | `09-motor/dogrulayici/` |
| **Motor — çözücü** | ✅ Tam ölçekte 0 sert ihlal, yayınlanabilir; üç aşama; fazla mesai 0 (dokuz koşu) | `09-motor/cozucu/` |
| **Motor — kalite (T-60)** 🔴 | Optimuma yakınlık kanıtlı değil; 4 yumuşak kural eksik; kalibrasyonlar dondu | §7 |
| **Motor — testler** | 609 birim · 12 altın senaryo · 325 mutasyon (hepsi öldü, 7 Ekim) | §8 |
| **`/suggest`** | ❌ Yazılmadı (bilerek 501) — kabul ölçütü yok | — |
| **Plan editörü, 24 yönetim ekranı, içe aktarma, bildirim** | ❌ Yazılmadı | §10 |
| **Backend ↔ motor entegrasyonu** | ❌ Yok; kuyruk ertelendi | §11 |
| **Demo** | ✅ 15 ekranlı tıklanabilir prototip (çağrı merkezi + otel) | `03-demo/v2-html/` |

---

## 10 · Ocak'a kadar eksikler

Kapsam sabit (MVP yok). Ocak'ı tehdit eden motor değil, **ekran ve CRUD
kuyruğu**:

| Alan | Eksik | Büyüklük (tahmin) |
|---|---|---|
| **Ekranlar** | 24 ekranın ~22'si: plan oluştur sihirbazı, üç plan kartı, **plan editörü takvimi** (sıfırdan yazılacak tek karmaşık bileşen: sürükle-bırak, yerel onarım, her düzenleme doğrulayıcıdan geçer), çalışan/ekip/yetkinlik/şablon/kural/talep/profil yönetimi, izinler, gerçekleşen veri içe aktarma, raporlar, kullanıcı & yetki, firma ayarları, kurulum sihirbazı | En büyük kalem; haftalar |
| **Backend uçları** | Plan tabloları ve CRUD uçlarının çoğu; 44 tablonun 15'i var (11 Eylül; backend o günden beri değişmedi) | Büyük |
| **Entegrasyon** | Backend → motor: 15 dk'ya varan iş, kuyruk, zaman aşımı, geri basınç, sonuç saklama, idempotency (§11.7) | Orta, **mimari karar ister** |
| **Motor** | 4 yumuşak kural; `/suggest`; sonuç kartı için küresel sınır; K-64; küçük ölçek | Orta |
| **Veri** | Veri seti merdiveni (K-62, araç + referans planlar); gerçek veriyle gölge pilot | Orta |
| **Bildirim** | 4 kanal (e-posta / SMS / WhatsApp / uygulama içi); WhatsApp Business onayı haftalar alır — *müşteri verisi çizgisi* | Dış bağımlılık |
| **Altyapı** | Eşzamanlılık (A-7), PgBouncer / `app.tenant_id` (A-8), KVKK (A-9), yedek, denetim kaydı hacmi, barındırma | Pilot öncesi |

**İki "bitti" çizgisi:** *satış çizgisi* (ilk demo: ekranlar, kurallar, motor,
içe aktarma çalışır) ve *müşteri verisi çizgisi* (KVKK, eşzamanlılık,
PgBouncer, performans, yedek — gölge pilot penceresinde). İkincisini birinciden
ayırmak şartnameden feragat değil, sıralama.

---

## 11 · Nerede destek almalıyız

**Yılmaz'dan (mimari: temel bir yıl taşır mı):**

1. **Geri alma bedeli 🔴 olan beş karar için ikinci teknik görüş** — bugüne
   kadar hiç alınmadı: M-01 tek veritabanı + RLS · M-06 denetim kaydı tasarımı
   · M-09 motor ayrı Python servisi · M-10 kurallar veride · M-11 UTC +
   genişletilmiş saat (hepsi §3'te). Dış tarama bunu karşılamıyor: kodun
   şartnameye uyduğuna bakıyor, kararın doğruluğuna değil.
2. **Backend ↔ motor sözleşmesi:** 15 dakikaya varan işler — kuyruk mu
   (RabbitMQ ertelendi), eşzamansız çağrı mı; zaman aşımı, yeniden deneme,
   geri basınç, sonuç saklama (2.493 atamalık JSON); aynı anda kaç kiracının
   planı koşar; CP-SAT çok çekirdek kullanır (6 işçi) — bir makinede bir koşu
   mu, yatay ölçek nasıl; üç alternatif plan → üç koşu mu.
3. **PgBouncer / oturum değişkeni (A-8):** kiracı kimliği
   `set_config('app.tenant_id', …, false)` ile **oturum** düzeyinde; araya
   transaction kipinde havuz girerse istekler arasında karışabilir — çok
   kiracılıkta en kötü hata sınıfı, sessiz ve çapraz. Seçenekler: havuz
   session kipinde; `set_config(..., true)` + her sorgu açık işlemde; başka.
   11 Eylül'den beri açık.
4. **Plan editörü mimarisi:** tek karmaşık bileşen; frontend durum yönetimi,
   iki müdür aynı planı açarsa (A-7), yerel onarım döngüsü (§11.7'nin
   idempotency ve onarım sözleşmesi).
5. **Ekip kurma ve devir:** satış sonrası ilk hangi profil; yapay zekâyla
   yazılmış kodu bir ekip devralırken `00-DEVIR/` yeter mi; neyi şimdiden
   değiştirmeliyiz.

**Dışarıdan (görüşü yararlı):**

- **Frontend kapasitesi:** 24 ekran + editör Ocak'a tek başına sığıyor mu?
  Bir frontend geliştirici/yüklenici şimdiden mi, satıştan sonra mı?
- **Hukuk teyidi (A-16):** iki yorum uzman gözü bekliyor — mola eşiğinin
  brüt vardiya süresine uygulanması (İş K. md. 68 kendine dönüyor; hata yönü
  tek taraflı, kanundan az mola vermez) ve yazılı onayın gece 7,5 saati aşan
  çalışmada fazla mesai ücretine etkisi (bugün bağlamıyor, ücret modülü
  gelirse ilk bakılacak). Belirsiz kural **yasal gibi** davranır (K-17 güvenli
  varsayılanı).
- **KVKK (A-9):** gerçek veri girmeden önce saklama / silme talebi /
  anonimleştirme.
- **Barındırma:** yerli sağlayıcı kararı ertelenmiş; gölge pilot için
  gerekecek.

---

## 12 · Yılmaz'ın görüşünü istediğimiz konular

**11 Eylül'ün sekiz sorusu hâlâ açık:**

1. Bu temel üzerine bir yıl inşa edilir mi; şimdi dönmemiz gereken bir şey
   görüyor musun?
2. Tek veritabanı + RLS ne zaman duvara toslar (50 kiracı × 5.000 çalışan)?
3. PgBouncer / `app.tenant_id` riskini nasıl çözerdin — oturum kipi, işlem
   düzeyi, başka bir şey?
4. Kendi kimlik katmanımızı yazmak hata mı; kurumsal müşteri (SSO) kapıya
   dayanınca bedelini nasıl öderiz?
5. İzin kodlarını jetona koymanın 15 dakikalık gecikmesi kabul edilebilir mi?
6. Yakaladığımız hataları (§8) görünce ilk itirazın hakkında ne
   düşünüyorsun?
7. **En çok merak ettiğimiz:** bu yaklaşımın sessizce kaybedeceği yer neresi
   — hangi hata sınıfı buradaki kontrollerin hiçbirine takılmaz?
8. İlk üç ayda sen olsan neyi farklı yapardın?

**Yeni sorular:**

9. **Ölçüm disiplini yeterli mi?** (§7–8) Her iddia tam ölçekte üçer koşu,
   karar kuralı önce, mutasyon, bağımsız inceleme — yine de O-16, O-18, O-19
   oldu. Bir mimar olarak süreçte neyi eksik görüyorsun?
10. **Motor servisi tasarımı** (§11 madde 2) ve K-63'ün ürün sözü: *"süre
    aralığı ver, üst sınırda elindeki en iyi planla dön"* doğru mu?
11. **Kalite kanıtı müşteriye nasıl söylenmeli?** *"Optimuma %x yakın"* büyük
    modelde dürüst yazılamıyor (§4.6); *"yasal, yayınlanabilir, fazla mesai 0,
    kalite ölçümü şu"* yeterli mi? Benzer ürünlerde ne gördün?
12. **Küçük ekip problemi:** 20 kişilik barda üç izin planı çözümsüz yapar;
    *"hangi kural çakışıyor, neyi gevşetirsem çözülür"* teşhisi (§4.4) orada
    birincil. Teşhis motorun içinde mi, ayrı serviste mi?
13. **Devir:** `00-DEVIR/` paketi bir ekibin kodu korkmadan devralmasına
    yeter mi? Ne eksik — ADR biçimi, C4 diyagramı, çalışır ortam tarifi?
14. **Takvim:** MVP'siz Ocak hedefi için okuman; neyi önce, neyi *müşteri
    verisi çizgisine* bırakırdın (kapsam kesmeden sıralama)?

---

## 13 · Önerilen gündem (90 dakika)

| Süre | Konu | Çıktı |
|---|---|---|
| 10 dk | Bir sayfada durum (§1, §9) — motor artık var, tam ölçekte çözüyor; ekranlar yok | Ortak resim |
| 20 dk | **Beş 🔴 karar** (M-01, M-06, M-09, M-10, M-11; §3) — her biri için *"dönmeli miyiz?"* | Evet/hayır + gerekçe; `03-MIMARI-KARARLAR.md`'ye not |
| 20 dk | **Backend ↔ motor sözleşmesi** ve PgBouncer — tasarım tahtası | Taslak karar; şartname §11 ve A-8'e yazılacak |
| 15 dk | 7. soru: *sessizce kaybedeceğimiz yer* + süreç eleştirisi (soru 9) | Yeni bekçi listesi |
| 15 dk | Ocak takvimi: ekran kuyruğu, frontend desteği, ekip kurma sırası | Karar: dış destek şimdi mi |
| 10 dk | Sonraki kilometre taşı ve Yılmaz'ın tekrar bakacağı an (ör. motor-backend entegrasyonu bitince) | Tarih |

**Görüşmeden sonra:** cevaplar `08-URUN-KARARLARI.md` (K-65+) ve
`03-MIMARI-KARARLAR.md`'ye kaynağıyla yazılır; açık kalanlar
`06-ACIK-RISKLER.md`'ye.

---

## 14 · Ek — sayılar ve okuma listesi

| Sayı | Değer | Tarih / kaynak |
|---|---|---|
| Şartname | v1.4, 17 bölüm, 41 kural (32 sert, 9 yumuşak), 44 tablo, 24 ekran, 63 değişiklik kaydı | `02-spec/v1.4-master-spec.md` |
| Backend testleri | 45 (gerçek PostgreSQL; DENETIM sayımı) | `04-kod/backend/tests/` |
| Motor birim testleri | 609 | 7 Ekim, Mustafa'nın makinesi (85 sn) |
| Altın senaryolar | 12 (7'si motoru sınar) | `08-motor-testleri/v5/` |
| Mutasyonlar | 325, hepsi öldü (tam koşu 7 Ekim 22:15) | `09-motor/mutasyon-tam-kosu.txt` |
| Tam ölçek | 500 kişi, %95 doluluk, 633.591 değişken / 771.332 kısıt, 2.493 atama, 0 sert ihlal; model kurma ~50 sn + arama 900 sn | `08-motor-testleri/gercekci-veri-seti/` |
| Fazla mesai (tam ölçek) | 2 Ekim 475–511 saat/hafta → 7–8 Ekim **0** (dokuz koşu) | T-60 bulgu 7, 23, 25 |
| Son ölçüm (8 Ekim 00:10) | `fm_once_deneme3` 900 × 3: 26.498 / 26.700 / 26.736, fazla mesai 0, hedef kapsama %85–86 | `kalite-olcumu-95-fmonce-deneme3-900.json` |
| Kararlar / otopsiler | K-1…K-64 · O-1…O-19 · açık 🔴: T-60 | `00-DEVIR/` |
| Gerçek veri | Çağrı merkezi giriş-çıkış + plan (git dışı) | `06-veri/`, `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` |

**Okuma listesi (öncelik sırasıyla):** `00-DEVIR/01-PROJE-KIMLIGI.md`
(Yılmaz'ın itirazı §3) · `00-DEVIR/03-MIMARI-KARARLAR.md` ·
`00-DEVIR/05-HATA-OTOPSILERI.md` (sondaki özet tablo) ·
`00-DEVIR/06-ACIK-RISKLER.md` (öncelik tablosu, T-60) · `09-motor/OKU-BENI.md`
· `05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md` (önceki paket).
10 dakikada çalıştırmak: `04-kod/` → `docker compose --profile tam up --build`
→ `http://localhost:3000` (firma `anadolu-cm`, dört rol — müdür / şef /
çalışan / izleyici aynı ekranda dört farklı davranış; ikinci firma
`marmara-perakende`, tamamen ayrı veri).
