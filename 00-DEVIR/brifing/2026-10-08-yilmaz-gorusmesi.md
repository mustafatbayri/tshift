# Yılmaz görüşmesi — brifing (8 Ekim 2026)

**Hazırlayan:** Claude (7 Ekim akşamı), Mustafa'nın isteğiyle · **Kim için:**
Mustafa (görüşmeye hazırlık) ve Yılmaz (okumak isterse) · **Önceki paket:**
`05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md` (11 Eylül; sekiz soru — cevap
alınamadı, Yılmaz o dönem ulaşılamıyordu). Bu belge o paketin devamıdır:
*o günden bu yana ne oldu, bugün neredeyiz, ne eksik, nerede destek
istiyoruz, hangi konularda görüşünü istiyoruz.*

> Her sayı bu depodaki bir ölçüme ya da kayda dayanır; kaynağı yanında.
> Tahmin olan yerler *tahmin* diye işaretli.

## İçindekiler

1. [Bir sayfada proje](#1--bir-sayfada-proje)
2. [11 Eylül'den bu yana ne oldu](#2--11-eylülden-bu-yana-ne-oldu)
3. [Bugünkü durum — katman katman](#3--bugünkü-durum--katman-katman)
4. [Ocak'a kadar eksikler](#4--ocaka-kadar-eksikler)
5. [Nerede destek almalıyız](#5--nerede-destek-almalıyız)
6. [Yılmaz'ın görüşünü istediğimiz konular](#6--yılmazın-görüşünü-istediğimiz-konular)
7. [Önerilen gündem (90 dakika)](#7--önerilen-gündem-90-dakika)
8. [Ek — sayılar ve okuma listesi](#8--ek--sayılar-ve-okuma-listesi)

---

## 1 · Bir sayfada proje

**T-Shift** (Teknovisor): çok kiracılı, yapay zekâ destekli **vardiya
planlama ve optimizasyon SaaS'ı**. Girdi: çalışanlar, sözleşmeler, iş kanunu
ve firma kuralları, beklenen iş yükü. Çıktı: haftalık vardiya planı — üç
önceliğe göre üç alternatif (DENGELI / KAPSAMA / CALISAN), yönetici plana
dokununca sonuçlarını hesaplayıp öneri getiren bir editör.

**Ürünün amacı (Mustafa, 6 Ekim):** *"Ürünün çıktısı elimizdeki tüm kriterlere
bağlı olarak optimum planı çıkarabiliyor mu?"* — firmaya ek ücret (fazla
mesai) çıkarmadan eldeki kaynağı en iyi kullanmak; fazla mesai kriterlerden
yalnız biri.

**Temel iddia:** tek üründe çok sektör (çağrı merkezi, otel, perakende…);
sektöre özel kural **koda değil veriye** yazılır. Spike'ta kanıtlandı (otel
gece kuralları tek satır kod değişmeden veriyle devreye girdi).

**Kim:** Mustafa — ürün sahibi, tek karar verici, 11 yıl BT ürün müdürlüğü,
yazılımcı değil. Claude — bütün kodu yazıyor. Yılmaz — dış göz, kilometre
taşlarında. **Yılmaz'ın başlangıçtaki itirazı projenin asıl sorusu olarak
kayıtlı:** *"Yapay zekâ blokların birbiriyle ilişkisini kuramaz."* Cevap
tartışmayla değil ölçümle aranıyor: *katmanlar arası kopmalar sessiz mi
kalıyor, yakalanıyor mu?*

**Hedef ve strateji:** MVP yok (K: 12 Eylül, tartışmaya kapalı) — satılabilir
sürüm şartnamenin fonksiyonel bütünü; **Ocak sonunda sahaya çıkmak**; pilot
yöntemi *gölge pilot* (gerçek çağrı merkezi verisiyle, gerçek kullanıcı
olmadan uçtan uca). Satış sonrası bütçeyle mimar/yazılım ekibi kurulacak —
yani ilk satış geliştirmenin sonu değil finansmanı.

**Yığın:** PostgreSQL 17 (tek veritabanı + `tenant_id` + RLS) · .NET 10 ·
Python + OR-Tools CP-SAT (motor, ayrı servis) · Next.js 16 · kimlik kendi
kodumuzda · RabbitMQ ve barındırma kararı ertelendi.

---

## 2 · 11 Eylül'den bu yana ne oldu

11 Eylül'de Yılmaz'a giden paket **dikey dilimi** anlatıyordu: veritabanından
ekrana çalışan yönetimi, 38 test (bugün 45), 4 hata otopsisi, 8 soru. O günden beri ağırlık
**motora** kaydı. Kısa zaman çizgisi:

| Tarih | Ne oldu | Kaynak |
|---|---|---|
| 12–16 Eyl | Ölçek kararı (20 kişilik bar ekibinden 2000 kişiye; küçük ekip ayrı problem sınıfı) · şartname **v1.4** (17 bölüm, **41 kural**: 32 sert, 9 yumuşak; her kuralda `yasal` / `kabul edilebilir` sütunu) · gerçek çağrı merkezi verisi geldi (PDKS + plan, `06-veri/`, git dışı) | `02-spec/v1.4-master-spec.md`, `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` |
| 16 Eyl | **Motor yazıldı:** bağımsız doğrulayıcı (`/evaluate`) + CP-SAT çözücü (`/solve`) + onarım döngüsü; çözücü ile doğrulayıcı birbirini import etmez — bir test bunu koruyor | `09-motor/OKU-BENI.md` |
| 23 Eyl | Dış inceleme döngüsü kuruldu (haftalık tarama; farklı sağlayıcının modeli); 19 bulgu (T-18…T-36): 🔴 olanların hepsi kapandı, 🟡'ların bir kısmı açık (T-20, T-24, T-30…T-33, T-36); CI (GitHub Actions, backend + motor) yeşil | `05-inceleme/beceriler/`, `06-ACIK-RISKLER.md` öncelik tablosu |
| 28–30 Eyl | 350 → **500 kişilik gerçekçi veri setleri**; altı gizli hata bir saatte çıktı; *"imkânsız"* ile *"yetiştiremedim"* ayrıldı (K-37); tam ölçek ilk kez çözüldü — 2.493 atama, **0 sert ihlal** | `06-ACIK-RISKLER.md` T-59/T-60 |
| 1–2 Eki | On 🔴 bulgu kapandı (K-48…K-57); fazla mesai tek tanıma indi (yasal); kalite ölçüm araçları yazıldı | `08-URUN-KARARLARI.md` |
| 3–7 Eki | **T-60 kalite programı:** üç aşamalı arama (geçerli plan → iyileştirme → mola adımı), *önce fazla mesaisiz* arama (K-61), fazla mesai tam ölçekte 475–511 saatten **0**'a; O-16/O-18 otopsileri; yeniden başlatma + K-63 (7 Ekim akşamı) | `06-ACIK-RISKLER.md` T-60 bulgu 1–27 |

**Süreç tarafında kurulanlar** (Yılmaz'ın itirazına verilen asıl cevap bunlar):

- **Devir paketi** `00-DEVIR/` (10 dosya + oturum günlükleri): her karar
  gerekçesiyle (K-1…K-64), her hata otopsisiyle (O-1…O-19), her açık risk
  numarasıyla (T-…). `DENETIM.py` her oturum sonunda paketi denetler (kırık
  yol, bayat iddia, tazelik).
- **Ölçmeden yazmama kuralı:** her kalite iddiası tam ölçekte, üçer koşuyla
  ölçülür; karar kuralı koşudan **önce** yazılır.
- **Mutasyon koşturucu:** elle seçilmiş 325 bozma (kod kasten bozulur, test
  kırmızı yanmazsa test eksiktir); son tam koşu 7 Ekim 05:42, 290'ın hepsi
  öldü (bugünkü 325 Mustafa'nın koşusunu bekliyor).
- **Bağımsız inceleme:** kod *"indi"* denmeden önce, işi görmemiş ayrı bir
  ajan karşı örnek arar (7 Ekim'de iki kez ilkeyi çiğneyen kod yakalandı —
  O-18).
- **Bir hatayı düzeltmek işin yarısı:** öteki yarısı bir daha sessizce geri
  gelmesini engelleyen bekçi (test, betik, kural) — 19 otopsinin tablosu
  `05-HATA-OTOPSILERI.md` sonunda.

---

## 3 · Bugünkü durum — katman katman

| Katman | Durum | Ölçü / kaynak |
|---|---|---|
| **Şartname** | ✅ v1.4 yürürlükte; 63 değişiklik kaydı (son: 7 Ekim) | `02-spec/v1.4-master-spec.md` |
| **Veritabanı + çok kiracılık** | ✅ Çalışıyor: RLS + `FORCE`, iki rol (`tshift` / `tshift_app`), denetim kaydı sadece-eklenir; mimari testleri (özellik değil *yasa* sınayan 7 test) | `03-MIMARI-KARARLAR.md` M-01…M-13 |
| **Backend (.NET)** | ✅ Dikey dilim: kimlik (Argon2id, döner yenileme jetonu), yetki (5 rol, 19 izin, kapsam), ~12 uç, **45 test** gerçek PostgreSQL'e karşı (DENETIM sayımı, 7 Ekim); CI GitHub Actions (backend + motor; son bakılan 2 Ekim: yeşil) | `04-kod/`, `06-ACIK-RISKLER.md` A-4 |
| **Frontend (Next.js)** | 🟡 Yalnız giriş + çalışan listesi + yeni kayıt; BFF deseni (`httpOnly` çerez) | `04-kod/frontend/` |
| **Motor — doğrulayıcı** | ✅ 41 kuralın gövdeleri (4 yumuşak hariç); plan üretmez, yalnız denetler; yayın kapısı üç kademe (yasal+sert engeller, firma+sert kabul bekler, yumuşak rapor — K-49) | `09-motor/dogrulayici/` |
| **Motor — çözücü** | ✅ Tam ölçekte (500 kişi, %95 doluluk) **0 sert ihlal, yayınlanabilir**; 900 sn bütçede üç aşama; fazla mesai bütün ölçülen koşularda **0** (6–7 Ekim) | `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-*.json` |
| **Motor — kalite (T-60)** 🔴 | Planın **optimuma yakınlığı kanıtlı değil** (büyük modelde küresel alt sınır yok — O-16); koşudan koşuya yayılım KAPSAMA'da %4,7; 4 yumuşak kural yazılmadığı için kalibrasyonlar donduruldu | `06-ACIK-RISKLER.md` T-60 |
| **Motor — testler** | **609 birim testi** (bulut, 7 Ekim), 12 altın senaryo (7'si motoru sınar), 325 mutasyon | `09-motor/testler/`, `08-motor-testleri/v5/` |
| **`/suggest`** (öneri ucu) | ❌ Yazılmadı (bilerek 501) — kabul ölçütü yok | `09-motor/servis.py` |
| **Plan editörü, 24 yönetim ekranı, içe aktarma, bildirim** | ❌ Yazılmadı | §4 |
| **Backend ↔ motor entegrasyonu** | ❌ Yok: motor ayrı HTTP servisi, backend henüz çağırmıyor; kuyruk (RabbitMQ) ertelendi | `03-MIMARI-KARARLAR.md` M-09 |
| **Demo** | ✅ 15 ekranlı tıklanabilir prototip (çağrı merkezi + otel) | `03-demo/v2-html/` |

**Motorun bugünkü "kalite" cümlesi, abartısız:** 500 kişilik sette plan
yasal ve yayınlanabilir; fazla mesai sıfır; ama planın *en iyi* plan olduğunu
söyleyemiyoruz — mola adımının optimumu kanıtlı, atamaların değil. Önümüzdeki
iş (sıra Mustafa'nın 7 Ekim onayıyla): yeniden başlatmanın 900 sn ölçümü →
dört yumuşak kural → veri seti v2 (cevabı bilinen beş seviyeli merdiven, K-62)
→ merdiven ölçümleri.

---

## 4 · Ocak'a kadar eksikler

Şartnamenin kapsamı sabit (MVP yok). Dürüst envanter — Ocak'ı tehdit eden
motor değil, **ekran ve CRUD kuyruğu** (`01-PROJE-KIMLIGI.md` §4):

| Alan | Eksik | Büyüklük (tahmin) |
|---|---|---|
| **Ekranlar** | 24 ekranın ~22'si: plan oluştur sihirbazı, plan karşılaştırma (üç kart), **plan editörü takvimi** (sıfırdan yazılacak tek karmaşık bileşen), çalışanlar/ekipler/yetkinlikler/şablonlar/kurallar/talep/profiller yönetimi, izinler, gerçekleşen veri içe aktarma, raporlar, kullanıcı & yetki, firma ayarları, kurulum sihirbazı | En büyük kalem; haftalar |
| **Backend uçları** | Plan tabloları (`plans`, `plan_runs`, `plan_versions`, `assignments`…) ve CRUD uçlarının çoğu; şartname §8'deki 44 tablonun 15'i var (11 Eylül; backend o günden beri değişmedi) | Büyük |
| **Entegrasyon** | Backend → motor çağrısı (uzun iş: 15 dk'ya kadar; kuyruk, zaman aşımı, geri basınç, sonuç saklama, idempotency §11.7) | Orta, **mimari karar ister** |
| **Motor** | 4 yumuşak kural (`EKIP_SUREKLILIGI`, `PLAN_KARARLILIGI`, `TERCIH_KARSILAMA`, `VARDIYA_ROTASYON_YONU`); `/suggest`; sonuç kartı için küresel sınır (optimuma yakınlık); küçük ölçek (20 kişi) hiç sınanmadı — orada çözümsüzlük ve çatışma açıklaması birincil özellik | Orta |
| **Veri** | Veri seti v2 (K-62); gerçek veriyle gölge pilot | Orta |
| **Bildirim** | 4 kanal (e-posta/SMS/WhatsApp/uygulama içi); WhatsApp Business onayı haftalar alır — *müşteri verisi çizgisi*, satış çizgisi değil | Dış bağımlılık |
| **Altyapı** | Eşzamanlılık (satır sürümü, idempotency — A-7), PgBouncer / `app.tenant_id` (A-8), KVKK (A-9), yedekleme, denetim kaydı hacmi, barındırma | Pilot öncesi |

**İki "bitti" çizgisi** hatırlatması: *satış çizgisi* (ilk demo: ekranlar,
kurallar, motor, içe aktarma çalışır) ile *müşteri verisi çizgisi* (KVKK,
eşzamanlılık, PgBouncer, performans, yedek) ayrı; ikincisi gölge pilot
penceresinde.

---

## 5 · Nerede destek almalıyız

**Yılmaz'dan (mimari, bir yıl taşır mı):**

1. **Geri alma bedeli 🔴 olan beş karar için ikinci teknik görüş** — bugüne
   kadar hiç alınmadı: M-01 tek veritabanı + RLS · M-06 denetim kaydı
   (sadece-eklenir, aynı işlemde) · M-09 motor ayrı Python servisi ·
   M-10 kurallar veride · M-11 UTC + genişletilmiş saat. Dış tarama bunu
   karşılamıyor (kodun şartnameye uyduğuna bakıyor, kararın doğruluğuna değil).
2. **Backend ↔ motor sözleşmesi:** 15 dakikaya varan işler, kuyruk mu
   (RabbitMQ ertelendi), çağrı mı; zaman aşımı, yeniden deneme, geri basınç,
   sonuç saklama; aynı anda kaç kiracının planı koşar; motorun yatay ölçeği
   (CP-SAT çok işçili — bir makinede bir koşu mu?).
3. **PgBouncer / oturum değişkeni:** `set_config('app.tenant_id', …, false)`
   oturum düzeyinde; transaction kipi havuz araya girerse kiracılar
   karışabilir. 11 Eylül'den beri açık, çözüm kararı yok.
4. **Plan editörü mimarisi:** sıfırdan yazılacak tek karmaşık bileşen
   (sürükle-bırak takvim, yerel onarım, her düzenleme aynı doğrulayıcıdan
   geçer); frontend durumu-yönetimi, eşzamanlı düzenleme (A-7).
5. **Ekip kurma ve devir:** satış sonrası ilk hangi profil (mimar? full-stack?
   frontend?); yapay zekâyla yazılmış kodu bir ekip devralırken `00-DEVIR/`
   yeter mi; neyi şimdiden değiştirmeliyiz.

**Dışarıdan (Yılmaz'ın alanı değil, ama görüşü yararlı):**

- **Frontend kapasitesi:** 24 ekran + editör Ocak'a tek başına sığıyor mu?
  Bir frontend geliştirici/yüklenici şimdiden mi, satıştan sonra mı?
- **Hukuk teyidi (A-16):** iki yasal yorum (gece sınırı, hafta tatili
  penceresi) uzman gözü bekliyor — araştırıldı, karar verildi, teyit yok.
- **KVKK (A-9):** gerçek veri girmeden önce saklama/silme/anonimleştirme.
- **Barındırma:** yerli sağlayıcı kararı ertelenmiş; gölge pilot için
  gerekecek.

---

## 6 · Yılmaz'ın görüşünü istediğimiz konular

**11 Eylül'ün sekiz sorusu hâlâ açık** (`05-inceleme/v1-2026-09-11/` §7):
temel bir yıl taşır mı · tek DB + RLS ne zaman duvara toslar (50 kiracı ×
5.000 çalışan) · PgBouncer/`app.tenant_id` · kendi kimlik katmanımız hata mı ·
izin kodları jetonda (15 dk gecikme) · dört hatayı görünce ilk itiraz hakkında
ne düşünüyor · **bu yaklaşımın sessizce kaybedeceği yer neresi — hangi hata
sınıfı buradaki kontrollerin hiçbirine takılmaz** · ilk üç ayda neyi farklı
yapardı.

**Yeni sorular (o günden beri öğrendiklerimizle):**

9. **Ölçüm disiplini yeterli mi?** Her iddia tam ölçekte üçer koşu, karar
   kuralı önce yazılıyor, mutasyon, bağımsız inceleme. Yine de bir hafta
   içinde iki kez *"bu kurda oluşmaz"* dedik ve karşı örnek çıktı (O-18),
   bir kütüphane varsayılanını hafızadan yazdık (O-19). Bir mimar olarak
   bu süreçte neyi eksik görüyor?
10. **Motor servisi tasarımı:** planı üreten servis, kiracı başına uzun iş,
    sonuç büyük JSON (2.493 atama), üç alternatif aynı anda → üç koşu mu, tek
    koşu mu; "süre aralığı ver, üst sınırda elindeki en iyi planla dön"
    (K-63) ürün sözü olarak doğru mu?
11. **Kalite kanıtı ürün karşısında nasıl söylenmeli?** *"Optimuma %x yakın"*
    kartı büyük modelde dürüst yazılamıyor (küresel alt sınır yok); müşteriye
    *"yasal, yayınlanabilir, fazla mesai 0, kalite ölçümü şu"* demek yeterli
    mi? Rakipler ne diyor, Yılmaz benzer ürünlerde ne gördü?
12. **Küçük ekip problemi:** 20 kişilik barda üç izin planı çözümsüz yapar;
    *"hangi kural çakışıyor, neyi gevşetirsem çözülür"* (teşhis, K-37) orada
    birincil özellik. Mimari olarak teşhisi motorun içinde mi, ayrı bir
    serviste mi tutmalı?
13. **Devir:** `00-DEVIR/` paketi (karar + otopsi + risk + oturum günlükleri)
    bir ekibin kodu korkmadan devralmasına yeter mi? Neyi eklemeliyiz —
    ADR biçimi, C4 diyagramı, çalışır ortam tarifi?
14. **Takvim:** MVP'siz Ocak hedefi için Yılmaz'ın okuması; neyi önce,
    neyi *müşteri verisi çizgisine* bırakırdı (kapsam kesmeden sıralama).

---

## 7 · Önerilen gündem (90 dakika)

| Süre | Konu | Çıktı |
|---|---|---|
| 10 dk | Bir sayfada durum (§1, §3) — motor artık var, tam ölçekte çözüyor; ekranlar yok | Ortak resim |
| 20 dk | **Beş 🔴 karar** (M-01, M-06, M-09, M-10, M-11) — her biri için *"dönmeli miyiz?"* | Evet/hayır + gerekçe; `03-MIMARI-KARARLAR.md`'ye not |
| 20 dk | **Backend ↔ motor sözleşmesi** ve PgBouncer — tasarım tahtası | Taslak karar; şartname §11 ve A-8'e yazılacak |
| 15 dk | 11 Eylül'ün 7. sorusu: *sessizce kaybedeceğimiz yer* + süreç eleştirisi (soru 9) | Yeni bekçi listesi |
| 15 dk | Ocak takvimi: ekran kuyruğu, frontend desteği, ekip kurma sırası | Karar: dış destek şimdi mi |
| 10 dk | Sonraki kilometre taşı ve Yılmaz'ın tekrar bakacağı an (ör. motor-backend entegrasyonu bitince) | Tarih |

**Görüşmeden sonra:** cevaplar `00-DEVIR/08-URUN-KARARLARI.md` (K-65+) ve
`03-MIMARI-KARARLAR.md`'ye kaynağıyla yazılır; açık kalanlar
`06-ACIK-RISKLER.md`'ye.

---

## 8 · Ek — sayılar ve okuma listesi

| Sayı | Değer | Tarih / kaynak |
|---|---|---|
| Şartname | v1.4, 17 bölüm, 41 kural (32 sert, 9 yumuşak), 44 tablo, 24 ekran, 63 değişiklik kaydı | `02-spec/v1.4-master-spec.md` |
| Backend testleri | 45 (gerçek PostgreSQL; DENETIM sayımı) | `04-kod/backend/tests/`, CI |
| Motor birim testleri | 609 | 7 Ekim, bulut (`09-motor/testler/`) |
| Altın senaryolar | 12 (7'si motoru sınar; 4'ü backend tarafında bekliyor) | `08-motor-testleri/v5/` |
| Mutasyonlar | 325 (son tam koşu 290, hepsi öldü — 7 Ekim 05:42) | `09-motor/mutasyon_kostur.py`, `mutasyon-tam-kosu.txt` |
| Tam ölçek | 500 kişi, %95 doluluk, 2.493 atama, 0 sert ihlal, yayınlanabilir; model kurma ~55 sn + arama 900 sn | `08-motor-testleri/gercekci-veri-seti/` |
| Fazla mesai (tam ölçek) | 2 Ekim 475–511 saat/hafta → 7 Ekim **0** (altı koşunun altısı) | T-60 bulgu 7, 23 |
| Kararlar / otopsiler / açık riskler | K-1…K-64 · O-1…O-19 · T-… (açık 🔴: T-60) | `00-DEVIR/` |
| Gerçek veri | Çağrı merkezi PDKS + plan (git dışı) | `06-veri/`, `07-GERCEK-VERI-BULGULARI.md` |

**Okuma listesi (öncelik sırasıyla, hepsi depoda):**
`00-DEVIR/01-PROJE-KIMLIGI.md` (Yılmaz'ın itirazı §3) ·
`00-DEVIR/03-MIMARI-KARARLAR.md` · `00-DEVIR/05-HATA-OTOPSILERI.md` (özet
tablo) · `00-DEVIR/06-ACIK-RISKLER.md` (öncelik tablosu, T-60) ·
`09-motor/OKU-BENI.md` · `05-inceleme/v1-2026-09-11/YILMAZ-INCELEME.md`
(önceki paket). 10 dakikada çalıştırmak: `04-kod/` → `docker compose --profile
tam up --build` → `http://localhost:3000` (firma `anadolu-cm`).
