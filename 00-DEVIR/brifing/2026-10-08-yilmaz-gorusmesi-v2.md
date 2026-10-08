# Yılmaz görüşmesi — brifing v2 (8 Ekim 2026)

**Hazırlayan:** Claude (7 Ekim gecesi), Mustafa'nın isteğiyle · **Kim için:**
Mustafa (görüşmeye hazırlık) ve Yılmaz (doğrudan okuyabilir) · **v1'den
farkı:** kendi başına okunur — her karar numarasının, her kısaltmanın ve
motorun ne yaptığının açıklaması bu belgenin içinde; şartnameye ya da başka
dosyaya gidip gelmek gerekmez. v1 (`2026-10-08-yilmaz-gorusmesi.md`) kayıt
için duruyor. · **Önceki paket:** `05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md`
(11 Eylül; sekiz soru — cevap alınamadı, Yılmaz o dönem ulaşılamıyordu).

> Her sayı bu depodaki bir ölçüme ya da kayda dayanır; kaynağı yanında.
> Tahmin olan yerler *tahmin* diye işaretli.

## İçindekiler

0. [Bu belge nasıl okunur — numaralar ve kısaltmalar](#0--bu-belge-nasıl-okunur--numaralar-ve-kısaltmalar)
1. [Bir sayfada proje](#1--bir-sayfada-proje)
2. [11 Eylül'den bu yana ne oldu](#2--11-eylülden-bu-yana-ne-oldu)
3. [Mimari — iki sayfada](#3--mimari--iki-sayfada)
4. [Motor nasıl çalışıyor — ve bu hafta ne değişti](#4--motor-nasıl-çalışıyor--ve-bu-hafta-ne-değişti)
5. [Kaliteyi nasıl ölçüyoruz; ne biliyoruz, ne bilmiyoruz](#5--kaliteyi-nasıl-ölçüyoruz-ne-biliyoruz-ne-bilmiyoruz)
6. [Süreç ve bekçiler — hatalar nasıl yakalanıyor](#6--süreç-ve-bekçiler--hatalar-nasıl-yakalanıyor)
7. [Bugünkü durum — katman katman](#7--bugünkü-durum--katman-katman)
8. [Ocak'a kadar eksikler](#8--ocaka-kadar-eksikler)
9. [Nerede destek almalıyız](#9--nerede-destek-almalıyız)
10. [Yılmaz'ın görüşünü istediğimiz konular](#10--yılmazın-görüşünü-istediğimiz-konular)
11. [Önerilen gündem (90 dakika)](#11--önerilen-gündem-90-dakika)
12. [Ek A — Sözlük: bu belgede geçen bütün numaralar](#12--ek-a--sözlük-bu-belgede-geçen-bütün-numaralar)
13. [Ek B — Sayılar ve okuma listesi](#13--ek-b--sayılar-ve-okuma-listesi)

---

## 0 · Bu belge nasıl okunur — numaralar ve kısaltmalar

Depoda her şey numaralı; bu belgede geçen her numara **ilk geçtiği yerde bir
cümleyle açıklanır** ve hepsi Ek A'da toplu durur. Seriler:

| Ön ek | Ne | Nerede tutulur | Örnek |
|---|---|---|---|
| **K-nn** | **Ürün kararı** — Mustafa'nın verdiği, tarihli, gerekçeli karar | `00-DEVIR/08-URUN-KARARLARI.md` | K-61 *"motor önce fazla mesaisiz plan arar"* |
| **M-nn** | **Mimari karar** — ne, neden, hangi alternatif elendi, geri almanın bedeli | `00-DEVIR/03-MIMARI-KARARLAR.md` | M-01 *tek veritabanı + RLS* |
| **O-nn** | **Hata otopsisi** — gerçekten yapılmış bir hata, nasıl göründü, ne yakaladı, bir daha gelmesini ne engelliyor | `00-DEVIR/05-HATA-OTOPSILERI.md` | O-19 *tohum etiketi yanlıştı* |
| **T-nn** | **Bulgu / açık risk** — dış inceleme ya da ölçümle açılmış madde; kapanınca kapanış tarihi ve kararı yazılır | `00-DEVIR/06-ACIK-RISKLER.md` | T-60 *tam ölçekte kalite* |
| **A-nn** | Açık risk listesinin ilk serisi (Eylül) — altyapı borçları | aynı dosya | A-8 *PgBouncer* |
| **"bulgu N"** | T-60 programının içindeki numaralı ölçüm sonuçları (bulgu 1–27) | aynı dosya, T-60 bölümü | bulgu 25 *aramanın kuyruğu* |

Sık geçen kısaltmalar: **CP-SAT** — Google OR-Tools'un kısıt çözücüsü, motorun
çekirdeği. **Profil** — ağırlık sütunu: DENGELI / KAPSAMA / CALISAN, aynı
girdiye üç farklı öncelikle üç plan. **Tam ölçek** — 500 kişilik, %95
dolulukta gerçekçi veri seti (ürünün üst ucu değil, sahada beklenen büyük
operasyon). **Mutasyon** — kodun kasten bozulup testin kırmızı yanıp
yanmadığına bakılması (testin gücünü ölçer). **RLS** — PostgreSQL Row Level
Security, satır seviyesinde kiracı yalıtımı.

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
sektöre özel kural **koda değil veriye** yazılır (M-10). Spike'ta kanıtlandı:
otelin gece kuralları tek satır kod değişmeden, yalnız veriyle devreye girdi.

**Kim:** Mustafa — ürün sahibi, tek karar verici, 11 yıl BT ürün müdürlüğü,
yazılımcı değil (fonksiyonel ve API testi yapar, kod okumaz). Claude — bütün
kodu yazıyor. Yılmaz — dış göz, kilometre taşlarında. **Yılmaz'ın
başlangıçtaki itirazı projenin asıl sorusu olarak kayıtlı:** *"Yapay zekâ
blokların birbiriyle ilişkisini kuramaz."* Cevap tartışmayla değil ölçümle
aranıyor: *katmanlar arası kopmalar sessiz mi kalıyor, yakalanıyor mu?*

**Hedef ve strateji:** MVP yok (12 Eylül kararı, tartışmaya kapalı) —
satılabilir sürüm şartnamenin fonksiyonel bütünü, çünkü kuralların %80'ine
uyan plan müdürün elle düzelteceği plandır (müşterinin zaten yaptığı iş).
**Ocak sonunda sahaya çıkmak**; pilot yöntemi *gölge pilot* (gerçek çağrı
merkezi verisiyle, gerçek kullanıcı olmadan uçtan uca). Satış sonrası
bütçeyle mimar/yazılım ekibi kurulacak — ilk satış geliştirmenin sonu değil
finansmanı.

**Yığın:** PostgreSQL 17 (tek veritabanı + `tenant_id` + RLS) · .NET 10 ·
Python + OR-Tools CP-SAT (motor, ayrı servis) · Next.js 16 · kimlik kendi
kodumuzda · RabbitMQ ve barındırma kararı ertelendi.

---

## 2 · 11 Eylül'den bu yana ne oldu

11 Eylül'de Yılmaz'a giden paket **dikey dilimi** anlatıyordu: veritabanından
ekrana çalışan yönetimi, 38 test (bugün 45), 4 hata otopsisi, 8 soru. O
günden beri ağırlık **motora** kaydı:

| Tarih | Ne oldu |
|---|---|
| 12–16 Eyl | Ölçek kararı: ürün hem 20 kişilik bar ekibini hem 2.000 kişilik operasyonu çözmeli — küçük ekip ayrı bir problem sınıfı (üç kişinin izni planı çözümsüz yapar; *"hangi kural çakışıyor"* açıklaması orada birincil özellik). Şartname **v1.4**: 17 bölüm, **41 kural** (32 sert, 9 yumuşak), her kuralda *yasal mı* / *ihlali kabul edilebilir mi* sütunları. Gerçek çağrı merkezi verisi geldi (giriş-çıkış kayıtları + plan; `06-veri/`, git dışı). |
| 16 Eyl | **Motor yazıldı** (§4): bağımsız doğrulayıcı + CP-SAT çözücü + onarım döngüsü. |
| 23 Eyl | Haftalık dış inceleme döngüsü (farklı sağlayıcının modeli kodu şartnameye karşı tarar); 19 bulgu (T-18…T-36) — 🔴 olanların hepsi kapandı, 🟡'ların bir kısmı açık. CI (GitHub Actions, backend + motor) yeşil. |
| 28–30 Eyl | 350 → **500 kişilik gerçekçi veri setleri**; 10 kişilik test sahnelerinde görünmeyen altı hata bir saatte çıktı. **K-37:** *"imkânsız"* ile *"süre yetmedi"* ayrı cevaplar oldu. Tam ölçek ilk kez çözüldü — 2.493 atama, **0 sert ihlal**. |
| 1–2 Eki | On 🔴 bulgu kapandı (K-48…K-57); *"fazla mesai"* tek tanıma indi (yasal: çalışma süresi − sözleşme saati); kalite ölçüm araçları yazıldı. |
| 3–7 Eki | **T-60 kalite programı** (§5): üç aşamalı arama (K-59, K-60), *önce fazla mesaisiz* arama (K-61), tam ölçekte fazla mesai 475–511 saat/haftadan **0**'a; iki otopsi (O-16, O-18); 7 Ekim akşamı yeniden başlatma + K-63 (§4.3). |

---

## 3 · Mimari — iki sayfada

### 3.1 Backend ve veri katmanı (11 Eylül'den beri değişmedi)

- **Çok kiracılık, iki katman (M-01).** Tek PostgreSQL veritabanı, her tabloda
  `tenant_id`. Yalıtım iki bağımsız yerde: (1) EF Core küresel sorgu filtresi
  — uygulama her sorguya kiracı şartını kendiliğinden ekler; (2) PostgreSQL
  **RLS + `FORCE`** — veritabanı, ham SQL yazılsa bile başka kiracının
  satırını vermez. Kiracı kimliği her bağlantı açılışında `app.tenant_id`
  oturum değişkenine yazılır. İkinci katman asıl garanti; birincisi
  unutulabilir.
- **İki veritabanı rolü (M-02).** `tshift` migration koşar (süper
  kullanıcı); `tshift_app` uygulamayı taşır (`NOSUPERUSER`, `NOBYPASSRLS`).
  Neden: PostgreSQL'de süper kullanıcı RLS'i tamamen aşar — bu bir kez
  başımıza geldi (O-1: güvenlik kâğıt üstünde vardı, çalışmada yoktu); bir
  bekçi test bağlanan rolün süper kullanıcı olmadığını her koşuda doğrular.
- **Kimlik kendi kodumuzda (M-03).** Keycloak elendi. Argon2id parola özeti,
  15 dakikalık JWT erişim jetonu, 30 günlük **döner** yenileme jetonu
  (her kullanımda yenisi verilir; kullanılmış jeton tekrar gelirse hırsızlık
  sayılıp kullanıcının bütün oturumları düşer), 5 deneme / 15 dk kaba kuvvet
  kilidi.
- **İzin jetonda, kapsam veritabanında (M-04).** *Ne yapabilir* (izin kodu)
  JWT'de; *nerede yapabilir* (departman/ekip kapsamı) her istekte
  veritabanından. Bedeli: geri alınan izin en çok 15 dk daha taşınır.
- **Denetim kaydı (M-06).** Otomatik (EF `SaveChanges` kancası), değişiklikle
  **aynı işlemde**, **sadece eklenir** (`tshift_app`'in `audit_log` üzerinde
  UPDATE/DELETE yetkisi yok — kısıt veritabanında).
- **Arayüz BFF deseni (M-07).** Tarayıcı API'ye doğrudan gitmez; istekleri
  Next.js sunucusu taşır, jetonlar `httpOnly` çerezde (sayfa JavaScript'i
  göremez).
- **Mimari testleri (M-08).** Özellik değil **yasa** sınayan testler: kiracıya
  ait her tabloda RLS açık ve `FORCE`'lu mu; RLS dışı tablolar yalnız bilinen
  istisnalar mı; korumasız uç var mı; ayar dosyasında sır var mı; denetim
  kaydı hâlâ sadece-eklenir mi. Yeni tablo eklenince EF modelinden
  kendiliğinden kapsanır.

### 3.2 Motor katmanı

- **Ayrı Python servisi (M-09).** HTTP uçları: `/evaluate` (bir planı
  denetle), `/solve` (plan üret), `/suggest` (öneri — henüz yok, 501 döner).
  .NET backend henüz çağırmıyor; entegrasyon ve kuyruk tasarımı açık (§9).
- **Dört bağımsız parça, biri diğerine bakmaz:** girdi şema doğrulaması →
  **çözücü** → **bağımsız doğrulayıcı** → puan. Çözücü ile doğrulayıcı
  birbirini **import etmez**; bir test (`test_bagimsizlik.py`) import ağacını
  denetler. Neden: optimizasyonda *"doğru çıktı"* tek bir beklenen listeyle
  sınanamaz (aynı girdiye çok sayıda geçerli plan var). Çözücüyü ve testini
  aynı el yazarsa yanlış kural yorumu ikisinde de tutarlı tekrar eder ve
  test yeşil yanar. Bu yüzden zaman aritmetiği bile iki yerde **bilerek
  farklı** yazıldı (doğrulayıcı mutlak saat aralıklarıyla, çözücü çeyrek saat
  dilimleriyle).
- **Kurallar veride (M-10).** 41 kuralın her birinin *türü* kodda (ne
  ölçtüğü), *değeri* veride (firma parametresi: günlük azami 11 saat, haftalık
  fazla mesai tavanı 10 saat…). Yanlış kural kod değişikliği değil parametre
  değişikliği; sürümü denetim kaydında kalır.
- **Yayın kapısı (K-16, K-49).** Hiçbir plan doğrulayıcıdan geçmeden
  kullanıcıya gösterilmez. Üç kademe: yasal + sert kural ihlali **engeller**;
  firma kuralı + sert ihlal gerekçeli **kabul bekler**; yumuşak kural ihlali
  **rapor** edilir. Doğrulayıcının *denetleyemediği* kural da kapıdan geçemez
  (*"bakamadım"* ≠ *"temiz"*).

---

## 4 · Motor nasıl çalışıyor — ve bu hafta ne değişti

Bu bölüm şartnameye bakmadan anlaşılsın diye yazıldı. Mimar gözüyle önemli
olan, aramanın **neden** böyle bölündüğü ve her bölümün hangi ölçümden
çıktığı.

### 4.1 Model — ne arıyoruz

- **Karar değişkenleri:** her (çalışan, gün, vardiya şablonu) üçlüsü için bir
  0/1 değişken (*x*: bu kişi o gün o şablonda çalışıyor mu); her vardiya için
  yemek molasının ve kısa dinlenmelerin hangi çeyrek saatte başlayacağını
  söyleyen 0/1 adaylar. 500 kişide model **633.591 değişken**; kurulması ~55
  sn (bütçenin dışında sayılır, ekranda ayrı gösterilecek — K-48).
- **Sert kurallar** kısıttır: haftalık 45 saat normal çalışma, günlük azami
  11, hafta tatili, gece sınırları, asgari kapsama (her saat en az N kişi),
  mola hakkı… Bunlar çiğnenemez.
- **Yumuşak kurallar** cezadır: hedef kapsamanın altında kalan her kişi-saat,
  hedefin üstüne çıkan, fazla mesai (dakika başına 50 puan — bir saat 3.000),
  adalet dengesi, saat dengesi, mola kapsaması. Amaç fonksiyonu = ağırlık ×
  ceza toplamı; profil (DENGELI / KAPSAMA / CALISAN) ağırlık sütununu seçer.
  **Hakem ağırlıklardır:** motor hiçbir yumuşak kuralı mutlak saymaz; hangi
  planın *"daha iyi"* olduğuna puan karar verir.
- **Bütçe:** kullanıcı süre seçer (varsayılan 15 dk = 900 sn, K-35). Motor
  bu süre içinde elindeki en iyi planı döndürür; *"optimuma %2 yakın"* ya da
  *"2 dakikadır iyileşmiyor"* olunca erken durur (K-28).

### 4.2 Üç aşamalı arama (K-59, K-60) — neden tek aramayla olmadı

Tam ölçekte CP-SAT'e modeli olduğu gibi verince **45 saniyede hiç plan
bulamıyordu** (amaç varken); amaç kaldırılınca 32 saniyede plan vardı. Yani
*geçerli* plan bulmak kolay, *iyileştirmek* zor. Çözüm, aramayı üçe bölmek:

| Aşama | Ne yapar | Süre payı (900 sn'de) | Neden |
|---|---|---|---|
| **1 · Geçerli plan** | Amaç kapalı, molalar şablonun ideal yerine **sabit** (değişkenlerin üçte ikisi mola yerleşimi; geçerli plan için hepsini aramaya gerek yok) | en çok 120 sn (%20) | Elde mutlaka bir plan olsun; *"süre yetmedi"* ile *"imkânsız"* karışmasın |
| **2 · İyileştirme** | Amaç geri konur, molalar hâlâ sabit, atamalar iyileştirilir; 1. aşamanın planı **başlangıç çözümü (ipucu)** olarak verilir | %80 (720 sn) | Küçük modelde arama derine iner; ölçüldü: fazla mesai 475–511 → 34–38 saat (K-59), hedef eksiği yarıya |
| **3 · Mola adımı** | Atamalar 2'nin planına **sabit**, yalnız molaların yeri aranır; bu kısıtlı problemin **kanıtlı optimumunda** durur | kalan (~170 sn; adım ~45 sn sürüyor) | Aynı şablondaki herkes aynı dakikada molaya çıkmasın (K-32); ortak arama bunu 347 sn'de daha kötü yapıyordu (bulgu 17–18) |

**İpucu (hint)** CP-SAT'in bir mekanizması: çözücüye *"şu değerler geçerli bir
çözüm, buradan başla"* denir. Biz ipucuyu **tam** yazıyoruz (bütün
değişkenler); yarım ipucuyu CP-SAT *"onarmaya"* çalışıp vazgeçiyordu
(ölçüldü: ilk plan 57–101 sn gecikiyordu).

**O-16 — bir dürüstlük düzeltmesi.** 3. aşama *"optimum"* deyince çıktı dört
gün boyunca *"plan optimuma %0 uzak"* yazdı. Yanlıştı: kanıtlanan şey *"bu
atamalarla en iyi mola yerleşimi"*ydi, planın tamamı değil (aynı girdide
4–5,6 kat iyi plan ölçüldü). Kural: **çözülen model tam model değilse sınır
küresel alana yazılmaz** — büyük modelde `optimuma_uzaklik_yuzde` artık
`null`. Sonuç kartının yüzdesi için ayrı bir *"sınır adımı"* gerekiyor; açık.

### 4.3 Bu hafta değişen üç şey

**(a) Önce fazla mesaisiz ara — K-61 (6 Ekim), uygulanışı O-18 ile düzeltildi
(7 Ekim).**
*Gözlem (bulgu 20):* veride fazla mesaiye gerek olmadığı hâlde DENGELI
profili 26–40 saat fazla mesaili planlar üretiyordu; CALISAN profili (fazla
mesai tavanı 0, yani **sert** sınır) aynı veride 13–33 saniyede fazla mesaisiz
plan buluyordu ve o planlar DENGELI'nin kendi ağırlıklarıyla 4–5,6 kat daha
iyiydi. Teşhis: fazla mesai verinin zorladığı bir şey değil, **aramanın
artığı** — yumuşak ceza süre içinde fazla mesaiyi sıfıra itemiyor, sert sınır
saniyeler içinde sıfırlıyor.
*Karar (Mustafa):* 1. aşama geçerli planı **fazla mesai değişkenleri 0'a
sabitken** arasın. Bulursa o plan **yalnız başlangıç noktasıdır**: alanlar
geri açılır, 2. ve 3. aşama tam modelde, tam ağırlıklarla koşar — fazla mesai
ancak puana göre kazanıyorsa plana girer (*"3 saat fazla mesaili plan
oldukça daha optimumsa onu seçmeliyiz"*). Bulamazsa (kanıtla ya da sürede)
alanlar yine açılır, eski yol işler, çıktıya not düşer.
*O-18 — hata:* ilk yazdığım sürüm bulunan fazla mesaisiz planı **bütün
aşamalarda** 0'da tutuyordu (*"sert kesim"*) ve bunu bir hesapla savunuyordu
(*"bir saat fazla mesai 3.000 puan, hedef açığı 9 puan; fazla mesaili plan
daha iyi olamaz"*). İki bağımsız inceleme ajanı ürün ağırlıklarında karşı
örnek buldu: şablon saatleri sözleşme saatini tam döşemiyorsa (7,5 × 5 +
7,75 = 45 sa 15 dk) **15 dakikalık bir fazla mesai adımı bütün haftanın
kilidini açıyor** — kanıtlı optimum 750 puan iken sert kesim 2.256; 12 kişide
9.000'e karşı 12.000 (Mustafa'nın *"3 saat"* örneği). Düzeltildi; dört karşı
örnek sahnesi artık test. Ders (kalıcı): *"oluşmaz"* cümlesi karşı örnek avı
olmadan yazılmaz.
*Ölçüm (bulgu 23, 500 kişi, 900 sn, üçer koşu):* fazla mesai altı koşunun
altısında **0**; DENGELI 26.634–26.705 puan (önceki hâl 106–148 bin).

**(b) Yeniden başlatma — bulgu 25 (7 Ekim).**
*Gözlem:* 18 koşunun 17'sinde fazla mesaisiz ilk arama 8,6–21 sn sürdü;
**1'inde 120 sn'de bulamadı** → motor eski yola düştü, plan 30 saat fazla
mesaiyle döndü (116.976 puan; ötekiler 26,6–26,8 bin). Ürün için kabul
edilemez. Kuyruk ölçüldü (aynı model, 35 deneme, farklı rastgelelik
tohumları): hepsi buldu, medyan 7,5 sn, en uzun 62 sn — kuyruk ince ama
gerçek (53 gözlemde 1 × > 120 sn). CP-SAT paralel işçilerle koşar;
zamanlama koşudan koşuya değişir, aynı tohumda bile 7× fark ölçüldü.
*Çare (koda indi, ölçümü sürüyor):* 120 saniyelik payı **3 × 40 saniyelik
denemeye bölmek**, her deneme farklı tohumla; ilk bulunan alınır. Varsayılan
hâlâ 1 (bugünkü arama, birebir); 3, tam ölçekte 900 sn × 3 ile ölçülmeden
varsayılan yapılmaz — karar kuralı koşudan **önce** yazıldı.
*O-19 — küçük ama kayda değer hata:* kuyruk ölçümünde *"tohum 0 = CP-SAT'in
varsayılanı = motorun kullandığı"* yazmıştım; kütüphanenin varsayılanı
**1**. Sonuç değişmedi, etiket yanlıştı. Ders: kütüphane varsayılanı
hafızadan yazılmaz, koddan okunur ve test çiviler.

**(c) Mola adımı yetişmezse ikinci aşamanın planı döner — K-63 (7 Ekim).**
*Gözlem (bulgu 24):* kısa bütçede 3. aşamaya 1–2 sn kalıyor ve plansız
dönüyordu; oysa 2. aşama geçerli bir plan bulmuştu — motor elde plan varken
*"süre yetmedi"* diyordu.
*Karar (Mustafa):* 2. aşamanın planı notla dönsün (*"molalar şablonun ideal
yerinde; mola adımı yetişmedi"*); ürün müşteriye tek süre değil **aralık**
söylesin (*"15–20 dk"* — üst uç kafadan tavan, motor üst uçta elindeki en
iyi planla döner). Aralığın sayıları ölçülmeden şartnameye yazılmıyor.
*Uygulama:* karar değişkenleri (atamalar ve molalar) ipucu değerine
sabitlenir, cezaları amaç sıkar (böylece raporlanan puan planın gerçek
puanıdır — ilk sürüm ipucunun gevşek ceza değerlerini aynen alıyordu,
bağımsız inceleme ölçtü: %85'e kadar şişkin olabiliyordu; düzeltildi).
Çevirme 0.2 ölçekte 0,6–0,8 sn; tam ölçekte ölçülmedi (tahmin ~4 sn).

### 4.4 Ne bilmiyoruz (motor)

- Planın **en iyi** plan olduğunu söyleyemiyoruz (küresel alt sınır yok, O-16).
- Dört yumuşak kural yazılmadı: ekip sürekliliği, plan kararlılığı (bir
  önceki plana sadakat), tercih karşılama, vardiya rotasyon yönü. Bunlar
  olmadan yapılan kalibrasyonlar (süre payları, hibrit arama) tekrar
  gerekeceği için **donduruldu**; sıra: önce dört kural, sonra veri seti v2.
- 500 kişilik set **kıtlık** taşımıyor (asgari talep sözleşme saatlerinin
  %65'i; fazla mesai hiç zorunlu değil). Cevabı bilinen, beş seviyeli veri
  seti merdiveni kararlaştırıldı (K-62) — en kolaydan çözümsüze.
- Küçük ölçek (20 kişi) hiç sınanmadı; çözümsüzlük teşhisi orada birincil.

---

## 5 · Kaliteyi nasıl ölçüyoruz; ne biliyoruz, ne bilmiyoruz

**T-60** projenin tek açık 🔴 maddesi: *"plan yasal çıkıyor ama kalitesi
kanıtlı değil."* Program (3–7 Ekim) şöyle işliyor:

- **Ölçüm aracı** `kalite-olc.py`: aynı 500 kişilik sahne, aynı makine, bir
  seferde yalnız bir şey değişir (yapılandırma); her yapılandırma **üçer
  koşu** (28 Eylül'de aynı girdi iki koşuda 21.905 ve 22.715 vermişti — tek
  koşudan sonuç çıkmaz). Kayıt JSON; amaç değerinin kural başına kırılımı,
  iyileşme eğrisi (hangi saniyede ne kadar düzeldi), süre kalemleri.
- **Karar kuralı koşudan önce yazılır** (*"X ise ürün yolu değişir, değilse
  değişmez"*); sonuç kuralla okunur, yorumla değil.
- **Bilinenler:** tam ölçekte 0 sert ihlal; fazla mesai 0 (altı koşu);
  DENGELI'de koşudan koşuya fark %0,3; KAPSAMA'da yayılım %4,7 (yakınsama —
  720 sn'lik iyileştirme 359 serbest değişkenle bitmiyor). Model kurma ~55
  sn, 3. aşama ~45 sn.
- **Bilinmeyenler:** §4.4. Ayrıca kalite cümlesinin müşteriye nasıl
  söyleneceği (*"optimuma %x"* dürüst yazılamıyorsa ne yazılacak) ürün
  sorusu olarak açık (§10, soru 11).

---

## 6 · Süreç ve bekçiler — hatalar nasıl yakalanıyor

Yılmaz'ın itirazına verilen asıl cevap bu bölüm. Katmanlar:

| Katman | Ne | Büyüklük |
|---|---|---|
| Birim testleri | Motor 609, backend 45 (gerçek PostgreSQL'e karşı, taklit yok — RLS taklitle sınanamaz) | her commit |
| Altın senaryolar | Şartnameden türetilmiş, motor yazılmadan **önce** ve motora bakmadan yazılmış kabul senaryoları (12; 7'si motoru sınar) | `08-motor-testleri/v5/` |
| **Mutasyon koşturucu** | 325 elle seçilmiş bozma: *"bu satırı tersine çevirirsem hangi test kırmızı yanar?"* Yanmıyorsa test eksik. Son tam koşu 290'ın hepsi öldü; 325 bu gece koşuyor | `09-motor/mutasyon_kostur.py` |
| **Bağımsız inceleme** | Kod *"indi"* denmeden önce işi görmemiş ayrı bir ajan **karşı örnek** arar. 7 Ekim'de iki kez işe yaradı: O-18 (ilkeyi çiğneyen kod) ve K-63'ün gevşek puan hatası | `kesif/…inceleme*/` klasörleri, raporla |
| Dış tarama | Haftalık, farklı sağlayıcının modeli: kod şartnameye uyuyor mu; *"yanlış yayın izni"* ve *"sessiz veri atlama"* öncelikli | `05-inceleme/beceriler/` |
| `DENETIM.py` | Devir paketini denetler: kırık dosya yolu, bayat test adı, test sayısı iddiası, değişim günlüğü tazeliği, commit durumu | her oturum sonu, 0 hata şartı |
| Hata otopsileri | O-1…O-19: her gerçek hata için *ne oldu, nasıl göründü, ne yakaladı, **bir daha gelmesini ne engelliyor*** — kalıcı bekçisi olmayan düzeltme tamamlanmış sayılmaz | `05-HATA-OTOPSILERI.md` |

**Dürüst eleştiri (kendimize):** bekçiler kodun ve deponun durumunu yakalıyor;
**cevapların** durumunu değil. Bir hafta içinde iki kez *"bu kurda oluşmaz"*
dedim ve karşı örnek çıktı (O-18); bir kütüphane varsayılanını hafızadan
yazdım (O-19). Her ikisini de bağımsız inceleme ya da kodun kendisi yakaladı,
insan gözü değil. **11 Eylül'ün 7. sorusu hâlâ en önemli soru:** hangi hata
sınıfı bu kontrollerin hiçbirine takılmaz?

---

## 7 · Bugünkü durum — katman katman

| Katman | Durum | Ölçü / kaynak |
|---|---|---|
| **Şartname** | ✅ v1.4 yürürlükte; 63 değişiklik kaydı (son: 7 Ekim) | `02-spec/v1.4-master-spec.md` |
| **Veritabanı + çok kiracılık** | ✅ RLS + `FORCE`, iki rol, denetim kaydı sadece-eklenir; 7 mimari "yasa" testi | §3.1 |
| **Backend (.NET)** | ✅ Dikey dilim: kimlik, yetki (5 rol, 19 izin, kapsam), ~12 uç, **45 test**; CI (son bakılan 2 Ekim: yeşil) | `04-kod/` |
| **Frontend (Next.js)** | 🟡 Yalnız giriş + çalışan listesi + yeni kayıt; BFF | `04-kod/frontend/` |
| **Motor — doğrulayıcı** | ✅ 41 kuralın gövdeleri (4 yumuşak hariç); yayın kapısı üç kademe | `09-motor/dogrulayici/` |
| **Motor — çözücü** | ✅ Tam ölçekte 0 sert ihlal, yayınlanabilir; üç aşama; fazla mesai 0 | `09-motor/cozucu/` |
| **Motor — kalite (T-60)** 🔴 | Optimuma yakınlık kanıtlı değil; 4 yumuşak kural eksik; kalibrasyonlar dondu | §4.4, §5 |
| **Motor — testler** | 609 birim · 12 altın senaryo · 325 mutasyon | §6 |
| **`/suggest`** | ❌ Yazılmadı (bilerek 501) — kabul ölçütü yok | — |
| **Plan editörü, 24 yönetim ekranı, içe aktarma, bildirim** | ❌ Yazılmadı | §8 |
| **Backend ↔ motor entegrasyonu** | ❌ Yok; kuyruk ertelendi | §9 |
| **Demo** | ✅ 15 ekranlı tıklanabilir prototip | `03-demo/v2-html/` |

---

## 8 · Ocak'a kadar eksikler

Kapsam sabit (MVP yok). Ocak'ı tehdit eden motor değil, **ekran ve CRUD
kuyruğu**:

| Alan | Eksik | Büyüklük (tahmin) |
|---|---|---|
| **Ekranlar** | 24 ekranın ~22'si: plan oluştur sihirbazı, üç plan kartı, **plan editörü takvimi** (sıfırdan yazılacak tek karmaşık bileşen: sürükle-bırak, yerel onarım, her düzenleme doğrulayıcıdan geçer), çalışan/ekip/yetkinlik/şablon/kural/talep/profil yönetimi, izinler, gerçekleşen veri içe aktarma, raporlar, kullanıcı & yetki, firma ayarları, kurulum sihirbazı | En büyük kalem; haftalar |
| **Backend uçları** | Plan tabloları ve CRUD uçlarının çoğu; 44 tablonun 15'i var (11 Eylül; backend o günden beri değişmedi) | Büyük |
| **Entegrasyon** | Backend → motor: 15 dk'ya varan iş, kuyruk, zaman aşımı, geri basınç, sonuç saklama, idempotency | Orta, **mimari karar ister** |
| **Motor** | 4 yumuşak kural; `/suggest`; sonuç kartı için küresel sınır; küçük ölçek | Orta |
| **Veri** | Veri seti v2 (K-62); gerçek veriyle gölge pilot | Orta |
| **Bildirim** | 4 kanal (e-posta/SMS/WhatsApp/uygulama içi); WhatsApp Business onayı haftalar alır — *müşteri verisi çizgisi* | Dış bağımlılık |
| **Altyapı** | Eşzamanlılık (satır sürümü, idempotency — A-7), PgBouncer / `app.tenant_id` (A-8), KVKK (A-9), yedek, denetim kaydı hacmi, barındırma | Pilot öncesi |

**İki "bitti" çizgisi:** *satış çizgisi* (ilk demo: ekranlar, kurallar, motor,
içe aktarma çalışır) ve *müşteri verisi çizgisi* (KVKK, eşzamanlılık,
PgBouncer, performans, yedek — gölge pilot penceresinde).

---

## 9 · Nerede destek almalıyız

**Yılmaz'dan (mimari: temel bir yıl taşır mı):**

1. **Geri alma bedeli 🔴 olan beş karar için ikinci teknik görüş** — bugüne
   kadar hiç alınmadı: M-01 tek veritabanı + RLS (geri almak = bütün veriyi
   taşımak) · M-06 denetim kaydı tasarımı (geri alınamaz, geçmiş kaybolur) ·
   M-09 motor ayrı Python servisi (yeniden yazım) · M-10 kurallar veride
   (motorun tamamı) · M-11 UTC + genişletilmiş saat modeli (gece yarısını
   aşan vardiya için; her plan yeniden yorumlanır). Dış tarama bunu
   karşılamıyor: kodun şartnameye uyduğuna bakıyor, kararın doğruluğuna değil.
2. **Backend ↔ motor sözleşmesi:** 15 dakikaya varan işler — kuyruk mu
   (RabbitMQ ertelendi), eşzamansız çağrı mı; zaman aşımı, yeniden deneme,
   geri basınç, sonuç saklama; aynı anda kaç kiracının planı koşar; CP-SAT
   çok çekirdek kullanır — bir makinede bir koşu mu, yatay ölçek nasıl.
3. **PgBouncer / oturum değişkeni:** kiracı kimliği `set_config('app.tenant_id',
   …, false)` ile **oturum** düzeyinde yazılıyor; araya transaction kipinde
   bir bağlantı havuzu girerse değişken istekler arasında karışabilir — çok
   kiracılıkta en kötü hata sınıfı: sessiz ve çapraz. 11 Eylül'den beri açık.
4. **Plan editörü mimarisi:** tek karmaşık bileşen; frontend durum yönetimi,
   eşzamanlı düzenleme (iki müdür aynı planı açarsa), yerel onarım döngüsü.
5. **Ekip kurma ve devir:** satış sonrası ilk hangi profil; yapay zekâyla
   yazılmış kodu bir ekip devralırken `00-DEVIR/` yeter mi; neyi şimdiden
   değiştirmeliyiz.

**Dışarıdan (görüşü yararlı):**

- **Frontend kapasitesi:** 24 ekran + editör Ocak'a tek başına sığıyor mu?
  Bir frontend geliştirici/yüklenici şimdiden mi, satıştan sonra mı?
- **Hukuk teyidi (A-16):** iki yasal yorum uzman gözü bekliyor — mola
  eşiğinin brüt vardiya süresine uygulanması (İş K. md. 68) ve yazılı onayın
  gece 7,5 saati aşan çalışmada fazla mesai ücretine etkisi; birincil
  mevzuattan araştırıldı, güvenli varsayılanla karar verildi, uzman teyidi
  yok.
- **KVKK (A-9):** gerçek veri girmeden önce saklama/silme/anonimleştirme.
- **Barındırma:** yerli sağlayıcı kararı ertelenmiş; gölge pilot için
  gerekecek.

---

## 10 · Yılmaz'ın görüşünü istediğimiz konular

**11 Eylül'ün sekiz sorusu hâlâ açık:**

1. Bu temel üzerine bir yıl inşa edilir mi; şimdi dönmemiz gereken bir şey
   görüyor musun?
2. Tek veritabanı + RLS ne zaman duvara toslar (50 kiracı × 5.000 çalışan)?
3. PgBouncer / `app.tenant_id` riskini nasıl çözerdin — oturum kipi, işlem
   düzeyi, başka bir şey?
4. Kendi kimlik katmanımızı yazmak hata mı; kurumsal müşteri (SSO) kapıya
   dayanınca bedelini nasıl öderiz?
5. İzin kodlarını jetona koymanın 15 dakikalık gecikmesi kabul edilebilir mi?
6. Yakaladığımız hataları görünce ilk itirazın hakkında ne düşünüyorsun?
7. **En çok merak ettiğimiz:** bu yaklaşımın sessizce kaybedeceği yer neresi
   — hangi hata sınıfı buradaki kontrollerin hiçbirine takılmaz?
8. İlk üç ayda sen olsan neyi farklı yapardın?

**Yeni sorular:**

9. **Ölçüm disiplini yeterli mi?** (§5–6) Her iddia tam ölçekte üçer koşu,
   karar kuralı önce, mutasyon, bağımsız inceleme — yine de O-18 ve O-19
   oldu. Bir mimar olarak süreçte neyi eksik görüyorsun?
10. **Motor servisi tasarımı:** kiracı başına uzun iş, sonuç büyük JSON
    (2.493 atama), üç alternatif → üç koşu mu tek koşu mu; *"süre aralığı
    ver, üst sınırda elindeki en iyi planla dön"* (K-63) ürün sözü olarak
    doğru mu?
11. **Kalite kanıtı müşteriye nasıl söylenmeli?** *"Optimuma %x yakın"* büyük
    modelde dürüst yazılamıyor (O-16); *"yasal, yayınlanabilir, fazla mesai
    0, kalite ölçümü şu"* yeterli mi? Benzer ürünlerde ne gördün?
12. **Küçük ekip problemi:** 20 kişilik barda üç izin planı çözümsüz yapar;
    *"hangi kural çakışıyor, neyi gevşetirsem çözülür"* teşhisi (K-37) orada
    birincil. Teşhis motorun içinde mi, ayrı serviste mi?
13. **Devir:** `00-DEVIR/` paketi (karar + otopsi + risk + oturum
    günlükleri) bir ekibin kodu korkmadan devralmasına yeter mi? Ne eksik —
    ADR biçimi, C4 diyagramı, çalışır ortam tarifi?
14. **Takvim:** MVP'siz Ocak hedefi için okuman; neyi önce, neyi *müşteri
    verisi çizgisine* bırakırdın (kapsam kesmeden sıralama)?

---

## 11 · Önerilen gündem (90 dakika)

| Süre | Konu | Çıktı |
|---|---|---|
| 10 dk | Bir sayfada durum (§1, §7) — motor artık var, tam ölçekte çözüyor; ekranlar yok | Ortak resim |
| 20 dk | **Beş 🔴 karar** (M-01, M-06, M-09, M-10, M-11) — her biri için *"dönmeli miyiz?"* | Evet/hayır + gerekçe; `03-MIMARI-KARARLAR.md`'ye not |
| 20 dk | **Backend ↔ motor sözleşmesi** ve PgBouncer — tasarım tahtası | Taslak karar; şartname §11 ve A-8'e yazılacak |
| 15 dk | 7. soru: *sessizce kaybedeceğimiz yer* + süreç eleştirisi (soru 9) | Yeni bekçi listesi |
| 15 dk | Ocak takvimi: ekran kuyruğu, frontend desteği, ekip kurma sırası | Karar: dış destek şimdi mi |
| 10 dk | Sonraki kilometre taşı ve Yılmaz'ın tekrar bakacağı an (ör. motor-backend entegrasyonu bitince) | Tarih |

**Görüşmeden sonra:** cevaplar `08-URUN-KARARLARI.md` (K-65+) ve
`03-MIMARI-KARARLAR.md`'ye kaynağıyla yazılır; açık kalanlar
`06-ACIK-RISKLER.md`'ye.

---

## 12 · Ek A — Sözlük: bu belgede geçen bütün numaralar

**Ürün kararları (K)**

| No | Tarih | Karar — bir cümleyle |
|---|---|---|
| K-16 | Eyl | Yayın kapısı: hiçbir plan doğrulayıcıdan geçmeden kullanıcıya gösterilmez |
| K-28 | 16 Eyl | Erken dur, bekletme: optimuma %2 yakınsa ya da 2 dakikadır iyileşmiyorsa arama biter |
| K-30 | 16 Eyl | Fazla mesai *"hedef hiç gitmemek, gidilecekse minimum"*: yalnız hedef kapsama iyileşecekse yapılmaz; asgari (sert) tutmuyorsa gereken kadar yapılır. 7 Ekim: ilk satır ağırlıkların sonucudur, sert kesim değil |
| K-32 | 25 Eyl | Mola modeli: ücretsiz yemek + ücretli kısa dinlenme; aynı şablondaki herkes aynı dakikada molaya çıkmasın |
| K-35 | Eyl | Çözüm süresini kullanıcı seçer (varsayılan 15 dk); kart *"kanıtlanmış yakınlık"* gösterir |
| K-37 | 29 Eyl | *"İmkânsız"* (kanıtlı çözümsüz) ile *"süre yetmedi"* ayrı cevaplardır; teşhis yalnız kanıt varsa koşar |
| K-48 | 1 Eki | Süre bütçesi = arama süresi; model kurma ayrı kalem olarak gösterilir |
| K-49 | 1 Eki | Yayın kapısı üç kademe: yasal+sert engeller, firma+sert kabul bekler, yumuşak rapor; denetlenemeyen kural geçemez |
| K-54 | 1 Eki | Donmuş gün: yayınlanmış planın geçmiş günleri aynen geçer, *gerçek* sayılır; *"İyileştir"* mevcut plandan devam eder |
| K-57 | 2 Eki | *"Fazla mesai"* tek tanım: çalışma süresi (bütün molalar düşülmüş) − sözleşme saati; yarı zamanlıya yazılmaz |
| K-59 | 3 Eki | İkinci aşama (molalar sabitken iyileştirme) ürünün varsayılanı |
| K-60 | 4 Eki | Üçüncü aşama: molalar motor içinde ayrı adım, atamalar sabit, kanıtlı optimum |
| K-61 | 6 Eki | Motor **önce fazla mesaisiz** plan arar; bulunan plan başlangıç noktasıdır, **hakem ağırlıklardır** (uygulanışı O-18 ile düzeltildi) |
| K-62 | 6–7 Eki | Kalite, cevabı bilinen **beş seviyeli veri seti merdiveniyle** ölçülür (500 kişi, kriter seti sabit, iki işi yapabilen kişiler her seviyede) |
| K-63 | 7 Eki | Mola adımı yetişmezse 2. aşamanın planı notla döner; müşteriye süre **aralığı** (sayıları ölçüm sonrası) |
| K-64 | 7 Eki | Puan eşitse fazla mesaisiz plan tercih edilir (⏳ koda inmedi) |

**Mimari kararlar (M)**

| No | Karar | Geri alma bedeli |
|---|---|---|
| M-01 | Tek veritabanı + `tenant_id` + iki katmanlı yalıtım (EF filtresi + RLS `FORCE`) | 🔴 bütün veri taşınır |
| M-02 | İki veritabanı rolü: `tshift` (migration) / `tshift_app` (uygulama, RLS'e tabi) | 🟢 |
| M-03 | Kimlik katmanı kendi kodumuzda (Keycloak elendi) | 🟡 |
| M-04 | İzin kodları jetonda, kapsam veritabanında | 🟢 |
| M-06 | Denetim kaydı otomatik, aynı işlemde, sadece-eklenir | 🔴 geçmiş kaybolur |
| M-07 | Jetonlar `httpOnly` çerezde; arayüz API'ye doğrudan gitmez (BFF) | 🟡 |
| M-08 | Mimari testleri: özellik değil yasa sınayan katman | 🟢 |
| M-09 | Motor ayrı Python + OR-Tools CP-SAT servisi; dört bağımsız parça | 🔴 yeniden yazım |
| M-10 | Kurallar veride, kodda değil | 🔴 motorun tamamı |
| M-11 | Zaman: UTC + genişletilmiş saat modeli (gece yarısını aşan vardiya) | 🔴 her plan yeniden yorumlanır |

**Hata otopsileri (O) — bu belgede geçenler**

| No | Hata | Kalıcı bekçi |
|---|---|---|
| O-1 | Uygulama süper kullanıcıyla bağlanıyordu; RLS kâğıt üstündeydi | İki rol + *"bağlanan rol süper kullanıcı değil"* testi |
| O-16 | Mola adımının optimumu planın optimumu gibi yazıldı (*"optimum · %0"*) | Kısıtlı model çözüldüyse sınır küresel alana yazılmaz; test + mutasyon |
| O-18 | Fazla mesaisiz plan bulununca fazla mesaili planlara hiç bakılmıyordu; *"bu kurda oluşmaz"* dendi, karşı örnek vardı | Bulunan plan yalnız başlangıç; karşı örnekler test; *"oluşmaz"* av betiği olmadan yazılmaz; inceleme *"indi"* denmeden önce |
| O-19 | *"Tohum 0 = CP-SAT varsayılanı"* hafızadan yazıldı; varsayılan 1 | Kütüphane varsayılanı koddan okunur, betik basar, test çiviler |

**Bulgular / riskler (T, A, "bulgu")**

| No | Ne |
|---|---|
| T-60 🔴 | Tam ölçekte kalite programı (3 Ekim'den beri; bulgu 1–27 bunun altında) |
| T-18…T-36 | 23 Eylül dış incelemesinin 19 bulgusu; 🔴'lar kapandı |
| A-7 / A-8 / A-9 / A-16 | Eşzamanlılık (satır sürümü, idempotency) · PgBouncer-oturum değişkeni · KVKK · iki hukuki yorumun uzman teyidi (mola eşiği brüt süreye mi; yazılı onay ve fazla mesai ücreti) |
| bulgu 17–18 | Mola adımı 45 sn'de kanıtlı optimum; ortak arama 347 sn'de daha kötü |
| bulgu 20 | Fazla mesai verinin değil aramanın artığı (CALISAN planı DENGELI ağırlıklarıyla 4–5,6 kat iyi) |
| bulgu 23 | Düzeltilmiş K-61 yolu tam ölçekte: fazla mesai 0, DENGELI 26,6–26,7 bin |
| bulgu 24 | Kısa bütçede elde plan varken *"süre yetmedi"* → K-63 |
| bulgu 25 | Fazla mesaisiz ilk aramanın ağır kuyruğu (1/18 koşu > 120 sn) → yeniden başlatma |
| bulgu 26–27 | İnceleme 3'ün bitişik bulguları: ipucu koruma kıyası gevşek puanla (karar Mustafa'da); donmuş gün × iki aşama mola alanları (sırada) |

---

## 13 · Ek B — Sayılar ve okuma listesi

| Sayı | Değer | Tarih / kaynak |
|---|---|---|
| Şartname | v1.4, 17 bölüm, 41 kural (32 sert, 9 yumuşak), 44 tablo, 24 ekran, 63 değişiklik kaydı | `02-spec/v1.4-master-spec.md` |
| Backend testleri | 45 (gerçek PostgreSQL; DENETIM sayımı) | `04-kod/backend/tests/` |
| Motor birim testleri | 609 | 7 Ekim, bulut |
| Altın senaryolar | 12 (7'si motoru sınar) | `08-motor-testleri/v5/` |
| Mutasyonlar | 325 (son tam koşu 290, hepsi öldü — 7 Ekim 05:42; 325 bu gece) | `09-motor/mutasyon-tam-kosu.txt` |
| Tam ölçek | 500 kişi, %95 doluluk, 633.591 değişken, 2.493 atama, 0 sert ihlal; model kurma ~55 sn + arama 900 sn | `08-motor-testleri/gercekci-veri-seti/` |
| Fazla mesai (tam ölçek) | 2 Ekim 475–511 saat/hafta → 7 Ekim **0** (altı koşunun altısı) | T-60 bulgu 7, 23 |
| Kararlar / otopsiler | K-1…K-64 · O-1…O-19 · açık 🔴: T-60 | `00-DEVIR/` |
| Gerçek veri | Çağrı merkezi giriş-çıkış + plan (git dışı) | `06-veri/`, `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` |

**Okuma listesi (öncelik sırasıyla):** `00-DEVIR/01-PROJE-KIMLIGI.md`
(Yılmaz'ın itirazı §3) · `00-DEVIR/03-MIMARI-KARARLAR.md` ·
`00-DEVIR/05-HATA-OTOPSILERI.md` (sondaki özet tablo) ·
`00-DEVIR/06-ACIK-RISKLER.md` (öncelik tablosu, T-60) · `09-motor/OKU-BENI.md`
· `05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md` (önceki paket).
10 dakikada çalıştırmak: `04-kod/` → `docker compose --profile tam up --build`
→ `http://localhost:3000` (firma `anadolu-cm`, dört rol, ikinci firma
`marmara-perakende`).
