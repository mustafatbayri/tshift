# Değişim günlüğü

En yeni en üstte. Her satır: tarih · ne oldu · nerede.

---

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
