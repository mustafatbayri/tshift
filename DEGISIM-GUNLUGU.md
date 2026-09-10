# Değişim günlüğü

En yeni en üstte. Her satır: tarih · ne oldu · nerede.

---

**2026-09-11 · İlk ekran (Next.js) — dikey dilim tamamlandı**
Giriş ekranı ve çalışan listesi. Veritabanından ekrana kadar bütün katmanlar
bağlı: PostgreSQL + RLS → EF → kimlik → yetki → denetim → API → arayüz.
Aynı ekran dört farklı kullanıcıda farklı davranıyor — müdür tüm listeyi ve
"Yeni çalışan" butonunu görüyor, şef yalnız kendi ekibini, çalışan yalnız
kendini, izleyici hepsini ama hiçbir eylem düğmesi olmadan.

**Karar: jetonlar `httpOnly` çerezde, tarayıcı koduna hiç girmiyor.**
Yaygın yöntem `localStorage`'dır; kolaydır ama sayfadaki HERHANGİ bir betik
jetonu okuyabilir (sızmış bağımlılık, XSS, tarayıcı eklentisi). Çerez
yönteminde tarayıcı jetonu isteğe ekler ama sayfa kodu göremez.
Yan fayda: API çağrıları Next.js sunucusundan gittiği için CORS ayarı
gerekmiyor — tarayıcı hiçbir zaman doğrudan API'ye gitmiyor.

**Yeni çalışan kaydı.** `POST /api/v1/employees` (`calisan.duzenle` izni) ve
form için `GET /api/v1/departments` · `GET /api/v1/teams` — ikisi de kapsama
göre filtreli, çünkü kullanıcı göremeyeceği bir departmanı seçenek olarak da
görmemeli.

**İlke: göremeyeceğin kaydı oluşturamazsın.** Listeyi filtreleyen ifade ile
"bu kaydı oluşturabilir misin" kontrolü tek bir `KapsamKurali` fonksiyonundan
geliyor; biri `IQueryable`'a uygulanıyor, diğeri derlenip tek kayda. İki ayrı
yerde yazılsaydı zamanla ayrışır ve bir gün "listede göremediğim ama
oluşturabildiğim kayıt" ortaya çıkardı — risk dokümanındaki 4 numaralı hata
sınıfı.

**Benzersizlik kontrolü kodda değil, kısıtta.** Önce "bu personel no var mı"
diye sorup sonra yazmak yetmez: iki istek aynı anda gelirse ikisi de "yok"
görür. Veritabanı kısıtı yapısal olarak engelliyor; kod yalnızca hatayı
anlaşılır mesaja çeviriyor (`PERSONEL_NO_TEKRAR`).

**Not:** `middleware.ts` içindeki kontrol bir güvenlik sınırı DEĞİL, kullanıcı
deneyimi düzenlemesi. Yalnız çerezin varlığına bakar, içeriğini doğrulamaz
(imza anahtarı orada yok). Asıl kontrol API'de. Aynı şey gizlenen düğmeler
için de geçerli: yetkisi olmayan butonu görmez, ama zorla çağırsa sunucu
403 döner.
→ `04-kod/frontend/`

**2026-09-11 · Denetim kaydı (audit_log) — risk listesindeki kırmızı madde kapandı**
Her oluşturma, güncelleme ve silme otomatik olarak kaydediliyor: kim, ne zaman,
hangi kayıt, hangi alanlar, önceki ve yeni değer, IP.
Üç kasıtlı özellik:
1. **Otomatik** — uçlarda tek tek çağrılmıyor, EF'in kaydetme akışına bağlı.
   Yeni tablo ya da yeni uç kendiliğinden kapsanıyor.
2. **Aynı işlemde** — değişiklikle denetim satırı tek `SaveChanges`'te gidiyor;
   biri yazılıp diğeri yazılamıyor. (İstemci tarafında üretilen UUIDv7
   kimlikler sayesinde mümkün.)
3. **Sadece eklenir** — `tshift_app` rolünün `audit_log` üzerinde UPDATE ve
   DELETE yetkisi YOK. Kısıt uygulamada değil veritabanında, çünkü uygulama
   katmanı açığın bulunacağı katmandır.
Parola ve jeton özetleri kayda girmez: alanın **değiştiği** kaydedilir,
**değeri** kaydedilmez. Yeni izin: `denetim.gor` (kiracı yöneticisi + izleyici).
Yeni uç: `GET /api/v1/audit`. 7 denetim testi + M6 mimari testi; toplam 38/38.
→ `04-kod/backend/src/TShift.Infrastructure/Denetim/`, `04-kod/db/rls/05-denetim-kaydi.sql`

**2026-09-11 · Test temizliği tek yere alındı**
Dört test dosyasında dört ayrı tablo listesi vardı — yeni tablo eklendiğinde
üçünü güncelleyip birini unutmak an meselesiydi. `TestTemizlik` sınıfına
taşındı. Temizlik artık **sahibi rolle** yapılıyor; uygulama rolü denetim
kaydını silemediği için (kasıtlı) başka türlü mümkün de değil.

**2026-09-11 · D6 testi düzeltildi — iddia yanlış kurulmuştu**
"B kiracısı hiçbir denetim kaydı görmemeli" diye yazmıştım; yanlış bir iddia,
çünkü B kendi işlemlerinin kaydını görmeli. Sınanmak istenen şey "B, **A'nın**
kayıtlarını göremez" idi. İddia zayıflatılmadı, gerçekte sınanan şeye çevrildi
ve kimlik karşılaştırmasıyla daha keskin hale geldi. Kod değişmedi.

**2026-09-10 · Mimari testleri ve risk dokümanı**
Özellik değil **yasa** sınayan bir test katmanı eklendi: kiracıya ait her
tabloda RLS açık mı, RLS dışı tablolar bilinen istisnalar mı, korumasız uç
var mı, kültüre bağımlı `ToLower()` kullanılmış mı, ayar dosyasında sır var mı.
Bunlar gelecekteki hatalara önceden konmuş bekçiler — bugün bir şey yakalamak
için değil, altı ay sonra unutulacak bir kuralı hatırlatmak için varlar.
`RISKLER-VE-ONLEMLER.md`: yapay zekâyla geliştirmede 15 hata sınıfı, hangisinin
sessiz hangisinin gürültülü olduğu, gerçekten geri dönülmez dört şey, ve
kırmızı çizgiler. **Açık madde: denetim kaydı (audit log) pilot öncesi
yazılmalı — tutulmayan geçmiş sonradan üretilemez.**
→ `RISKLER-VE-ONLEMLER.md`, `04-kod/backend/tests/TShift.Tests/MimariTestleri.cs`

**2026-09-10 · Roller ve izinler — kapsam devrede**
Spec §3.2 yetki matrisi koda geçti. 5 sistem rolü, 18 izin kodu, departman/ekip
kapsamı, süreli yetki devri. Uçlar izin politikalarıyla korunuyor; çalışan
listesi kapsama göre filtreleniyor. Aynı firmada müdür 3, şef 2, çalışan 1,
izleyici 3 kayıt görüyor — izleyicide hiçbir yazma izni yok.
9 yetki testi + 5 HTTP sınırı testi; toplam 26/26 yeşil.
→ `04-kod/backend/src/TShift.Infrastructure/Yetki/`, `04-kod/db/rls/04-yetki-tablolari.sql`

**2026-09-10 · SPEC'TEN BİLİNÇLİ SAPMA: kapsamsız kullanıcı hiçbir şey görmez** ⚑
Spec §3.2: *"Kapsamı olmayan kullanıcı tüm kiracıyı görür."*
Uygulama: kapsam seviyesi `Kapsam` olup hiç kapsam satırı olmayan kullanıcı
**hiçbir şey görmez.**
Gerekçe: kapsamı atanmayı unutulan bir departman müdürü, spec'teki davranışla
sessizce tüm firmayı görürdü — yapılandırma eksikliğinin yetki genişlemesine
dönüşmesi. Kiracı yöneticisi zaten `Kiraci` seviyesinde olduğu için spec'in
asıl kastettiği durum bozulmuyor. Eksik yapılandırma artık "göremiyorum"
şikâyeti üretir, sızıntı değil. Y8 testi bunu sabitliyor.

**2026-09-10 · Karar: izin kodları jetonda, kapsam veritabanında**
İzinler JWT'ye yazılıyor (spec §7.4) — bedeli: geri alınan bir yetki, jeton
süresi dolana kadar (≤15 dk) taşınmaya devam eder; acil iptalde yenileme
jetonları da düşürülmeli. Kapsam jetona konmadı, her istekte okunuyor:
liste uzayabilir ve kapsam değişikliğinin anında etkili olması iyidir.

**2026-09-10 · Bulunan hata: JWT `sub` talebi yeniden adlandırılıyordu** ⚠
21 test yeşilken korumalı bütün uçlar 401 dönüyordu. JwtBearer, gelen jetonun
`sub` talebini eski Microsoft şemasına çeviriyor; kod `sub` diye aradığı için
kullanıcı kimliği null geliyor ve uç "yetkisiz" diyordu. Yetki mantığı
doğruydu; kırılan yer iki katmanın buluştuğu sınırdı.
Çözüm: `MapInboundClaims = false`.
**Testler bunu yakalamadı** — hepsi servisleri doğrudan çağırıyordu, HTTP
katmanından geçmiyordu. Yakalayan şey kanıt betiği oldu.
Bu yüzden `HttpSinirTestleri` eklendi: uygulamayı bellek içinde ayağa kaldırıp
gerçek istek atar. Ders: birim testi katmanın İÇİNİ, uçtan uca test
katmanların ARASINI doğrular; biri diğerinin yerine geçmez.

**2026-09-10 · Kimlik katmanı — `X-Tenant-Id` başlığı kaldırıldı**
Kiracı kimliği artık sunucunun imzaladığı JWT'den okunuyor; istemcinin
yazdığı başlıktan değil (spec §10). Önceki hali bilerek kabul edilmiş geçici
bir açıktı — isteyen istediği firmanın kimliğini yazabiliyordu.
Eklenenler: Argon2id parola saklama (64 MB/3/4), 15 dakikalık erişim jetonu,
30 günlük **döner** yenileme jetonu, jeton yeniden kullanım tespiti
(çalınırsa o kullanıcının tüm oturumları düşer), 5 deneme / 15 dakika kaba
kuvvet kilidi. Uçlar: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/me`.
7 yeni test; toplam 12/12 yeşil.
→ `04-kod/backend/src/TShift.Infrastructure/Kimlik/`, `04-kod/db/rls/03-kimlik-tablolari.sql`

**2026-09-10 · Karar: `login_attempts` bilerek RLS dışında**
Kaba kuvvet sayacı, kiracının kim olduğu bilinmeden yazılmak zorunda — aksi
halde saldırgan var olmayan bir firma adı yazarak kilidi tamamen atlar.
Tablo hiçbir API ucundan dışarı açılmaz; parola ya da jeton içermez.
Gerekçe hem koda hem SQL betiğine yazıldı ki ileride "RLS unutulmuş" diye
düzeltilmesin.

**2026-09-10 · Karar: giriş isteği firma kısa adını taşır**
`users` benzersizliği `(tenant_id, eposta)` olduğu için e-posta tek başına
kimlik değil; aynı kişi iki firmada kullanıcı olabilir. Canlıda firma alt
alan adından gelecek (`anadolu-cm.tshift.com`), kullanıcı yazmayacak.

**2026-09-10 · Not: makinede Windows PowerShell 5.1 var, 7 değil**
Betikler 5.1 uyumlu yazılacak (`-SkipHttpErrorCheck` gibi 7'ye özgü
parametreler kullanılmayacak) ve `.ps1` dosyaları saf ASCII olacak — 5.1
betikleri ANSI okuyor, UTF-8 türkçe karakterler ayrıştırıcıyı bozuyor.

**2026-09-10 · Dikey dilim 1: çok kiracılık yalıtımı ayakta**
Veritabanı, alan modeli, EF katmanı, RLS, API ve testler uçtan uca bağlandı.
7 tablo, ilk migration (`20260910002040_Ilk`), 5 test yeşil.
İki firma aynı API adresinden birbirinin verisini göremiyor — betikle kanıtlandı.
→ `04-kod/`, `04-kod/YALITIM-KANITI.ps1`

**2026-09-10 · Bulunan açık: süper kullanıcı RLS'i aşıyordu** ⚠
Satır seviyesi güvenlik doğru yazılmış, açılmış ve `t/t` diye doğrulanmıştı;
ama uygulama veritabanına Docker'ın süper kullanıcısıyla (`tshift`) bağlanıyordu.
PostgreSQL'de süper kullanıcı RLS'i tamamen aşar — `FORCE` bile durdurmaz.
Güvenlik kâğıt üstünde vardı, çalışmada yoktu.
Çözüm: iki rol. `tshift` migration çalıştırır, `tshift_app` uygulamayı taşır
(süper değil, `NOBYPASSRLS`). Ayrıca 0 numaralı **bekçi test** eklendi:
bağlanan rol süper kullanıcıysa test paketi kırmızı yanıyor.
Açığı bulan şey inceleme değil, testin kendisi oldu.
→ `04-kod/db/rls/02-uygulama-rolu.sql`

**2026-09-09 · Master Spec v1.1**
Spec'in gözden geçirilmesinden 9 değişiklik: kimlik katmanı kendi kodumuza alındı
(Keycloak çıktı), izin etki analizi yeni özellik olarak eklendi, uygulanan
önerilerde geri alma, metrik açıklama bileşeni, içe aktarmadan yapay zekâ
kaldırıldı, seçilmeyen plan adayları için 30 günlük saklama politikası,
departman/şube isimlendirmesi, arayüz bileşen kütüphanesi kararı, plan revizyon
karşılaştırması kapsam dışı. Tablo sayısı 37 → 44.
→ `02-spec/v1.1-master-spec.md`

**2026-09-09 · Pilot kararı: gölge pilot**
Pilot müşteri beklenmeyecek. Çağrı merkezi operasyonundan gerçek veri alınıp
gerçek kullanıcı olmadan uçtan uca çalışılacak. Sektör paketi önceliği:
çağrı merkezi.

**2026-09-09 · Master Spec v1.0 yazıldı**
Ürün tanımından veri modeline kadar tüm spec: 15 bölüm, 37 tablo, 24 ekran,
27 kural, backend servis listesi, motor sözleşmesi, Ocak sonu teslim planı.
→ `02-spec/v1.0-master-spec.md`

**2026-09-09 · Föy notları görüşüldü**
Motor dili Python'da kaldı (Go elendi — resmî OR-Tools bağlayıcısı yok).
Yapay zekâ maliyeti ölçüldü: kiracı başına aylık $0,80–1,60. Ocak sonu hedefi
kapsam kesintileriyle gerçekçi bulundu.

**2026-09-09 · Çalışma kökü kuruldu**
Proje dosyaları `Desktop\Tshift` altında toplandı. Versiyonlama kuralı belirlendi.
→ `README.md`

**2026-09-09 · Spike testleri v1 olarak donduruldu**
7–8 Eylül'de yapılan tüm motor testleri arşivlendi; kronoloji ve ölçülen sayılar
`01-spike/README.md` içinde.

**2026-09-09 · Karar föyü dolduruldu**
Teknoloji, ürün ve eksik bilgi başlıklarının tamamı cevaplandı. 6 yeni kural seçildi.

**2026-09-08 · Karar föyü yayınlandı**

**2026-09-07/08 · Motor fizibilite testleri koşuldu**
CP-SAT motoru iki sektörde 0 sert ihlalle plan üretti. 12 kritik hata bulundu
ve düzeltildi. → `01-spike/README.md`
