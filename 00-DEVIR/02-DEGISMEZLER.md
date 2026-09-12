# DEĞİŞMEZLER

**Kod yazmadan önce bu dosya okunur.**

Buradaki her satır, bozulduğunda ürünün yanlış çalışacağı bir kuraldır.
Bunlar "iyi olur" değil, "bozulursa durulur" maddeleridir.

## Bu tablo nasıl okunur

Her değişmezin yanında **onu koruyan test** yazar. Bu kasıtlı: bir kuralın
yazılı olması onu korumaz, **test korur.** Sütunlar:

| İşaret | Anlamı |
|---|---|
| ✅ | Otomatik bir test bu kuralı koruyor. Test adı yazılı. |
| ⚠️ | Kural geçerli ama **bekçisi yok.** Bozulursa kimse fark etmez. |
| 🔒 | Veritabanı ya da altyapı seviyesinde zorlanıyor (koddan bağımsız). |

> **Kural:** ⚠️ işaretli bir satır, kapatılması gereken bir açıktır.
> Yeni test yazma sırası belirlerken önce bu listeye bakılır.

---

## 1. Çok kiracılık — en kritik grup

Bir müşterinin başka bir müşterinin verisini görmesi, bu üründe **geri
dönülmez** hatadır: KVKK sorumluluğu doğurur ve güven bir daha geri gelmez.

| # | Değişmez | Durum | Bekçi |
|---|---|---|---|
| K-1 | Bir kiracı başka kiracının verisini **hiçbir yoldan** göremez | ✅🔒 | `1 - Iki ayri baglam ayni anda birbirinin verisini gormez` |
| K-2 | **Ham SQL ile bile** başka kiracının satırı gelmez | ✅🔒 | `2 - Ham SQL ile bile baska kiracinin satiri gelmez (RLS)` |
| K-3 | Kiracı bağlamı ayarlanmamışsa **hiçbir satır** görünmez (varsayılan "hepsi" değil, "hiçbiri") | ✅🔒 | `3 - Kiraci baglami yoksa hicbir satir gorunmez` |
| K-4 | Başka kiracının kimliğiyle kayıt yazılamaz | ✅🔒 | `4 - Baska kiracinin kimligiyle kayit yazilamaz` |
| K-5 | Kiracıya ait **her** tabloda RLS açık **ve** `FORCE` | ✅ | `M1 - Kiraciya ait her tabloda RLS acik ve zorunlu` |
| K-6 | RLS dışında kalan tablolar yalnız 3 bilinen istisna; dördüncüsü sessizce eklenemez | ✅ | `M2 - RLS disindaki tablolar sadece bilinen istisnalar` |
| K-7 | Kiracı kimliği **sunucunun imzaladığı JWT'den** okunur; istemcinin yazdığı başlıktan değil | ✅ | `H5 - Sahte X-Tenant-Id basligi hicbir sey degistirmez` |
| K-8 | Denetim kayıtları da kiracıya göre yalıtılmıştır | ✅ | `D6 - Bir kiraci digerinin denetim kaydini goremez` |
| **K-9** | **Uygulama veritabanına `tshift_app` ile bağlanır — `tshift` (süper kullanıcı) ile ASLA** | ✅ | `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` |

### K-9 neden bu kadar önemli

Bu projedeki **en ciddi hata** buydu. RLS doğru yazılmıştı, açılmıştı,
veritabanında `t/t` diye doğrulanmıştı — ve hiçbir şey yapmıyordu, çünkü
uygulama Docker'ın süper kullanıcısıyla bağlanıyordu. PostgreSQL'de süper
kullanıcı RLS'i **tamamen** aşar; `FORCE` bile durduramaz.

> **Genel ders — belgede yok, bize ait:**
> *"Koruma tanımlı mı" yanlış sorudur. Doğru soru: "koruma şu anda beni
> durduruyor mu?"* Her koruma için, korumanın **yürürlükte olduğunu**
> kanıtlayan ayrı bir kontrol gerekir.

Bu dersin kendisi K-1…K-8'in tamamının üzerinde durur: onların hepsi, K-9
bozulursa **hiçbir şey ifade etmez.**

**M0 bu yüzden M1'in önünde durur.** M1 *"RLS tanımlı mı?"* diye sorar;
M0 *"RLS beni gerçekten durduruyor mu?"* diye. M0 rol **adına** değil,
`current_user`'ın **yetkisine** bakar (`pg_roles.rolsuper` ve
`rolbypassrls`) — böylece bağlantı dizesi bir gün sahibi role çevrilirse de,
`tshift_app` rolüne sonradan yetki verilirse de yakalar.

*Doğrulandı (12 Eylül): `tshift` → `rolsuper=t`, `rolbypassrls=t`;
`tshift_app` → `f`, `f`. Uygulama `tshift` ile bağlansa M0 iki ayrı iddiadan
birden kırılır.*

---

## 2. Yetki ve kapsam

Temel ayrım: **izin = ne yapabilir** (`plan.uret`), **kapsam = nerede
yapabilir** (hangi departman/ekip). İkisi ayrı kavramdır ve karıştırılmaz.

Kapsam seviyeleri: `Kiraci` (tüm firma) · `Kapsam` (atanan departman/ekip) ·
`Kendi` (yalnız kendi kaydı).

| # | Değişmez | Durum | Bekçi |
|---|---|---|---|
| Y-1 | Kiracı yöneticisi tüm firmayı görür | ✅ | `Y1 - Kiraci yoneticisi tum calisanlari gorur` |
| Y-2 | Şef **yalnız** kendi kapsamındaki ekibi görür | ✅ | `Y2 - Sef YALNIZ kendi ekibini gorur` |
| Y-3 | Yetki matrisi (spec §3.2) birebir uygulanır: şef plan düzenler, üretemez/onaylayamaz | ✅ | `Y3 - Sef plan uretemez, duzenleyebilir` |
| Y-4 | Çalışan yalnız kendi kaydını görür; başkası adına izin giremez | ✅ | `Y4 - Calisan yalniz kendi kaydini gorur` |
| Y-5 | İzleyicide **hiçbir** yazma izni yoktur (yeni yazma izni eklense de) | ✅ | `Y5 - Izleyici her seyi gorur, hicbir sey yazamaz` |
| Y-6 | Süresi geçmiş yetki devri işlemez | ✅ | `Y6 - Suresi gecmis yetki devri islemez` |
| Y-7 | Yetki devri **izin** genişletir, **kapsam** genişletmez | ✅ | `Y7 - Suren yetki devri calisir ve kapsami genisletmez` |
| Y-8 | Kapsam seviyesinde olup hiç kapsam satırı olmayan kullanıcı **hiçbir şey görmez** ⚑ | ✅ | `Y8 - Kapsami olmayan kapsamli rol HICBIR SEY gormez` |
| Y-9 | Rolsüz kullanıcının hiçbir izni yoktur | ✅ | `Y9 - Rolsuz kullanici hicbir izne sahip degil` |
| Y-10 | Yetkisiz kullanıcı **403** alır, **401** değil (kimlik ile yetki karıştırılmaz) | ✅ | `H3 - Izni olmayan kullanici 403 alir, 401 degil` |
| Y-11 | Kapsam filtresi HTTP katmanında da geçerlidir (servis katmanında kalmaz) | ✅ | `H4 - Sef HTTP uzerinden de yalniz kendi ekibini gorur` |
| **Y-12** | **Göremeyeceğin kaydı oluşturamazsın** (liste filtresi ile yazma kontrolü tek `KapsamKurali`'ndan gelir) | ⚠️ | **BEKÇİSİ YOK — bkz. A-2** |
| **Y-13** | **Kapsam seviyesindeki bir kullanıcı, kapsam atanmadan tek tek oluşturulamaz** (içe aktarmada izinli, ama işaretli) | ⏳ | **Karar verildi 12 Eylül, henüz uygulanmadı — bkz. A-12** |
| **Y-14** | **Kapsamsız kalmış kullanıcılar her zaman görünür olur** (liste rozeti + uyarı şeridi) | ⏳ | **Karar verildi 12 Eylül, henüz uygulanmadı — bkz. A-12** |

> ⏳ = karar verildi ve kayda geçti, ilgili ekran/uç henüz yazılmadı.

### Y-13/Y-14 ile Y-8 arasındaki ilişki — karıştırılmamalı

Bunlar **aynı sorunun iki farklı katmanı**, biri diğerinin yerine geçmez:

| | Ne yapar | Sınırı |
|---|---|---|
| **Y-13/Y-14** | Kötü yapılandırmanın **oluşmasını zorlaştırır** | Deliklidir — aşağıdaki 6 senaryo |
| **Y-8** | Kötü yapılandırma **oluştuğunda güvenli davranır** | Deliksiz — son savunma |

**Y-13 varken bile Y-8 kalkamaz, çünkü kapsamsız durum kullanıcı
oluşturmadan da doğabilir:**

1. **Arayüz güvenlik sınırı değildir.** Formu atlayıp API'ye doğrudan istek
   atılabilir. (Aynı ilke: `middleware.ts` ve gizlenen düğmeler de sınır
   değil.)
2. **İçe aktarma bilerek izin veriyor** — kararın gereği.
3. **Rol yükseltmesi.** `Kendi` seviyesindeki bir kullanıcı `Kapsam`
   seviyesine çıkarıldığı anda kapsamı boştur.
4. **Kural öncesi veri.** Bu kural yazılmadan önce oluşturulmuş kullanıcılar.
5. **İki adımlı yazma.** Kullanıcı satırı ve kapsam satırları aynı işlemde
   gitmezse arada bir pencere oluşur.
6. **Departman ya da ekip silinmesi.** Kapsam satırları onunla birlikte
   gider. **Kimse kapsamsız kullanıcı oluşturmaz — durum kendiliğinden
   doğar.**

Altıncısı belirleyici olanı: engelleme mekanizmasının hiç devreye girmediği,
ama sonucun yine de kapsamsız bir kullanıcı olduğu senaryo.

> **Genel ilke:** *Engelleme* ile *güvenli varsayılan* farklı şeylerdir.
> Engellemenin delikleri vardır; güvenli varsayılanın yoktur. İkisi de
> istenir — ama ikisinden biri seçilecekse güvenli varsayılan seçilir.
>
> Bu, `05-HATA-OTOPSILERI.md` O-1'deki dersin kardeşi: orada *"koruma tanımlı
> mı"* değil *"koruma yürürlükte mi"* diye sormayı öğrendik. Burada da
> *"kötü durum engellendi mi"* değil, **"kötü durum oluşursa ne olur"** diye
> soruyoruz.

### Y-8: spec'ten bilinçli sapma ⚑

Spec §3.2 der ki: *"Kapsamı olmayan kullanıcı tüm kiracıyı görür."*
**Biz bilerek tersini yapıyoruz.**

Gerekçe: kapsamı atanmayı unutulan bir departman müdürü, spec'teki davranışla
**sessizce tüm firmayı görürdü** — yapılandırma eksikliği yetki genişlemesine
dönüşürdü. Bizim davranışımızda eksik yapılandırma "göremiyorum" şikâyeti
üretir, sızıntı değil. Kiracı yöneticisi zaten `Kiraci` seviyesinde olduğu
için spec'in asıl kastettiği durum bozulmuyor.

*Bu sapma Mustafa tarafından onaylandı ve Y8 testiyle sabitlendi.*

### Y-12 neden kritik

Listeyi filtreleyen ifade ile "bu kaydı oluşturabilir misin" kontrolü tek bir
`KapsamKurali` fonksiyonundan geliyor — biri `IQueryable`'a uygulanıyor,
diğeri derlenip tek kayda. İki ayrı yerde yazılsaydı zamanla ayrışır ve bir
gün *"listede göremediğim ama oluşturabildiğim kayıt"* ortaya çıkardı.

Şu an bu birlik **tasarım gereği** sağlanıyor ama **hiçbir test onu
sabitlemiyor.** Biri iki kontrolü ayırırsa hiçbir şey kırılmaz.

---

## 3. Kimlik ve oturum

| # | Değişmez | Durum | Bekçi |
|---|---|---|---|
| I-1 | Parola veritabanında düz metin durmaz; Argon2id, her kayıtta **ayrı tuz** | ✅ | `K7 - Parola veritabaninda duz metin olarak durmaz` |
| I-2 | Doğru parola bile olsa, kullanıcı o firmada yoksa giriş olmaz | ✅ | `K3 - Baska firmanin adiyla giris yapilamaz` |
| I-3 | Yanlış parola `KimlikGecersiz` döner; kullanıcının var olup olmadığını sızdırmaz | ✅ | `K2 - Yanlis parola reddedilir` |
| I-4 | 5 başarısız denemeden sonra hesap kilitlenir (doğru parola da girmez) | ✅ | `K4 - Bes basarisiz denemeden sonra hesap kilitlenir` |
| I-5 | Yenileme jetonu **döner**: her kullanımda yenisi verilir, eskisi ölür | ✅ | `K5 - Yenileme jetonu doner; eski jeton olur` |
| I-6 | Çalınmış jeton tekrar kullanılırsa o kullanıcının **tüm** oturumları düşer | ✅ | `K6 - Calinmis jeton tekrar kullanilirsa TUM oturumlar duser` |
| I-7 | Kimliksiz istek 401 alır | ✅ | `H2 - Jetonsuz istek 401` |
| **I-8** | **Jetonlar `httpOnly` çerezde tutulur; tarayıcı koduna hiç girmez (`localStorage` yasak)** | ⚠️ | **BEKÇİSİ YOK — arayüz tarafında test yok** |

### I-8 gerekçesi

Yaygın yöntem `localStorage`'dır; kolaydır ama sayfadaki **herhangi bir
betik** jetonu okuyabilir (sızmış bağımlılık, XSS, tarayıcı eklentisi).
Çerez yönteminde tarayıcı jetonu isteğe ekler ama sayfa kodu göremez.
Yan fayda: API çağrıları Next.js sunucusundan gittiği için CORS ayarı
gerekmiyor — tarayıcı hiçbir zaman doğrudan API'ye gitmiyor.

### Güvenlik sınırı NEREDE değil

- `middleware.ts` / `proxy.ts` içindeki kontrol **güvenlik sınırı DEĞİLDİR.**
  Yalnız çerezin varlığına bakar, içeriğini doğrulamaz (imza anahtarı orada
  yok). Kullanıcı deneyimi düzenlemesidir.
- **Gizlenen düğmeler güvenlik değildir.** Yetkisi olmayan butonu görmez, ama
  zorla çağırsa sunucu 403 döner. Asıl kontrol her zaman API'dedir.

---

## 4. Denetim kaydı (audit log)

**Tutulmayan geçmiş sonradan üretilemez.** Bu yüzden denetim kaydı ilk
müşteri verisi girmeden önce yazıldı.

| # | Değişmez | Durum | Bekçi |
|---|---|---|---|
| D-1 | Her oluşturma/güncelleme/silme **otomatik** iz bırakır (uçlarda tek tek çağrılmaz) | ✅ | `D1 - Kayit olusturmak otomatik iz birakir` |
| D-2 | Güncellemede yalnız **değişen** alanlar kaydedilir | ✅ | `D2 - Guncellemede SADECE degisen alanlar kaydedilir` |
| D-3 | Parola ve jeton özetleri kayda **sızmaz** — alanın *değiştiği* kaydedilir, *değeri* kaydedilmez | ✅ | `D3 - Parola ozeti denetim kaydina SIZMAZ` |
| D-4 | Yazılmış denetim kaydı **değiştirilemez** | ✅🔒 | `D4 - Yazilmis denetim kaydi DEGISTIRILEMEZ` |
| D-5 | Yazılmış denetim kaydı **silinemez** | ✅🔒 | `D5 - Yazilmis denetim kaydi SILINEMEZ` |
| D-6 | Kısıt uygulamada değil **veritabanında**: `tshift_app` rolünün `audit_log` üzerinde UPDATE/DELETE yetkisi yok | ✅🔒 | `M6 - Denetim kaydi sadece eklenir (UPDATE/DELETE yok)` |
| D-7 | İşlemi yapan kullanıcı ve IP kaydedilir | ✅ | `D7 - Islemi yapan kullanici ve IP kaydedilir` |
| D-8 | Değişiklik ve denetim satırı **aynı işlemde** gider; biri yazılıp diğeri yazılamaz | ✅ | (D1 dolaylı olarak; istemci üretimi UUIDv7 sayesinde mümkün) |

Kısıtın veritabanında olmasının sebebi: **uygulama katmanı, açığın bulunacağı
katmandır.** Uygulamada "silmeyin" demek yeterli değil.

---

## 5. Genel kod ve veri kuralları

| # | Değişmez | Durum | Bekçi |
|---|---|---|---|
| G-1 | Her API ucu ya korumalı ya da **açıkça** istisna | ✅ | `M3 - Her uc korumali ya da acikca istisna` |
| G-2 | Kültüre bağımlı `ToLower()`/`ToUpper()` kullanılmaz (Türkçe `I` tuzağı) | ✅ | `M4 - Kulture bagimli ToLower/ToUpper kullanilmiyor` |
| G-3 | `appsettings.json` içinde gerçek parola/sır yok | ✅ | `M5 - appsettings icinde gercek parola yok` |
| G-4 | Kimlikler **UUIDv7**, istemci tarafında üretilir | 🔒 | (şema; değiştirilmesi tüm yabancı anahtarları etkiler) |
| **G-5** | **Benzersizlik kontrolü kodda değil, veritabanı kısıtında** (önce sor sonra yaz = iki eşzamanlı istekte ikisi de "yok" görür) | ⚠️ | **BEKÇİSİ YOK — bkz. A-3** |
| **G-6** | **Zaman UTC + genişletilmiş saat modeli; naive datetime kullanılmaz** | ⚠️ | **BEKÇİSİ YOK — vardiya ürünü için kritik** |
| G-7 | `login_attempts` bilerek RLS dışında (kiracı bilinmeden yazılmak zorunda; aksi halde saldırgan olmayan firma adı yazarak kilidi atlar) | ✅ | `M2` bu istisnayı tanır |
| G-8 | Sıra dışı her karar, yanındaki yorumda gerekçesiyle durur | — | İnsan incelemesi |

### G-6 neden acil

Bu bir **vardiya planlama ürünü.** Yaz saati geçişinde "minimum dinlenme 11
saat" kuralı gerçekte 10 veya 12 saat olur. Gece yarısını aşan vardiyalar iki
güne yayılır. Şu anda zaman modelini sınayan **tek bir test bile yok** ve
motor henüz yazılmadı — yani şimdi kapatmak ucuz.

---

## 6. Süreç değişmezleri

Bunların bekçisi kod değil, alışkanlık. Yine de bozulmaz:

- **`main` her zaman yeşil.** Test kırmızıyken birleştirilmez.
- **Kırılan bir test, kodu doğru sanıp iddiayı zayıflatarak düzeltilmez.**
  Ayrım şu soruyla yapılır: *"bu değişiklikten sonra test, eskiden
  yakalayacağı bir hatayı kaçırır mı?"* Cevap evetse yapılan şey düzeltme
  değil **örtbastır.**
  Tek istisna: iddianın, sınanmak istenen şeyi yanlış ifade ettiği durum. O
  zaman iddia **düzeltilir** — ve düzeltilmiş hali eskisinden **daha keskin**
  olmalıdır, daha gevşek değil. (Örnek: D6, 11 Eylül.)
- **Spec'ten sapılıyorsa sapma açıkça kaydedilir ve bir testle sabitlenir.**
  (Örnek: Y-8.)
- **Bir hata bulunduğunda düzeltmek yetmez**; o hatanın bir daha sessizce geri
  gelmesini engelleyen kontrol eklenir.
- **Kilometre taşlarında** etiket atılır ve değişim günlüğüne yazılır.
- `.ps1` dosyaları **saf ASCII** ve **PowerShell 5.1 uyumlu**.

### Kırmızı çizgiler

Tam liste `RISKLER-VE-ONLEMLER.md` §6'da. Özeti:

- Gerçek veri üzerinde hiçbir migration, üretilen SQL okunmadan
  çalıştırılmaz. `DROP`, `ALTER COLUMN ... TYPE`, `DELETE` görürsen **dur**.
- Gerçek veri üzerinde migration öncesi **yedek alınır.** İstisnasız.
- Kolon silme ve ekleme aynı sürümde yapılmaz: önce ekle, doldur, geç,
  **sonraki sürümde** sil.
- `.env` git'e gitmez. Sırlar `appsettings.json`'a yazılmaz.
- İstek gövdeleri kayda yazılmaz — içinde parola olabilir.
- Pilot verisi anonimleştirilmiş gelir; gerçek isim ve kimlik numarası
  geliştirme ortamına girmez.
- `TSHIFT_KURULUM=true` canlıda **asla** olmaz.
- `docker compose down -v` yalnız geliştirme makinesinde.
- Bu projede `git reset --hard` ve `git push --force` **yasaktır**.

---

## Özet: kaç değişmez korunuyor?

| Grup | Toplam | ✅ Bekçili | ⚠️ Açık |
|---|---|---|---|
| Çok kiracılık | 9 | **9** | 0 |
| Yetki ve kapsam | 12 | 11 | **1** (Y-12) |
| Kimlik ve oturum | 8 | 7 | **1** (I-8) |
| Denetim kaydı | 8 | 8 | 0 |
| Genel | 8 | 5 | **2** (G-5, G-6) |
| **TOPLAM** | **45** | **41** | **4** |

Dört açığın hepsi `06-ACIK-RISKLER.md` altında izleniyor: A-2 (Y-12),
A-3 (G-5), A-5 (G-6), ve I-8.

**Değişim günlüğü — bu tablo:**

| Tarih | Olay |
|---|---|
| 12 Eylül 2026 | Paket kuruldu: 39/45 bekçili, 5 açık |
| 12 Eylül 2026 | **K-9 kapandı** (M0 eklendi) → 41/45, 4 açık. En kritik açıktı: bozulduğunda diğer 8 kiracılık değişmezi de anlamsızlaşıyordu. |
