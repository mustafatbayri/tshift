# Değişim günlüğü

En yeni en üstte. Her satır: tarih · ne oldu · nerede.

---

**2026-09-16 · DIŞ İNCELEME, 3. tur — on bulgu daha, beşi 🔴**

Üçüncü tur şartnameyi kural kural kodla karşılaştırdı. **On bulgunun onu da**
ölçülerek doğrulandı; hiçbiri tahmin değil, her biri koşturularak görüldü.

**T-27 🔴 — olmayan mola yasal sınırı deviriyor.** `zaman.mola_saat()` mola
süresini vardiyanın **içinde olup olmadığına bakmadan** topluyor. Ölçüm:
`vardiya 08:00–20:00, mola 22:00–23:00 → brüt 12, mola 1, net 11,
GUNLUK_AZAMI (11 saat) ihlali: 0`. Devrilen kural `yasal: true,
kabul_edilebilir: false` sınıfında — K-20'ye göre asla göz yumulamaz olan.

**T-28 🔴 — geçmiş vardiyalar hiç okunmuyor.** `gecmis_vardiyalar` ifadesi
`09-motor/` içinde **hiçbir dosyada geçmiyor**. Haftalar arası dinlenme
kuralı önceki haftaya kör: pazar gecesini çalışmış biri pazartesi sabahına
yazılabilir.

**T-29 🔴 — `DONMUS_GUN` hiç ateşlenemez.** Kural yalnız `_yeni` işaretli
atamalarda çalışıyor, o işareti **hiçbir yer üretmiyor**. Ölçüm: işaretsiz
girdide 0 ihlal, elle işaretlenince 1. *"Geçmiş yeniden planlanamaz"*
sözünün tek bekçisi bu.

**T-34 🔴 — sırlar kodda varsayılana düşüyor.** `Program.cs`:
`APP_DB_PASSWORD ?? "tshift_app_dev_2026"` ve
`JWT_SECRET ?? "yerel-gelistirme-imza-anahtari-..."`. Ortam değişkeni
unutulursa uygulama **hata vermiyor**, bilinen anahtarla açılıyor.

**T-35 🔴 — bir kullanıcının hatalı girişi bütün kiracıyı kilitliyor.**
`giris/route.ts` `X-Forwarded-For` iletmiyor, backend
`ctx.Connection.RemoteIpAddress` okuyor, `ForwardedHeaders` ara katmanı
hiçbir yerde yok. Sonuç: bütün istekler tek IP'den geliyor gibi görünüyor —
beş yanlış parola **herkesi** kilitliyor, denetim kaydındaki her IP kurgusal.

**Dört 🟡 daha.** T-30 `HAFTA_TATILI` kesintisiz 24 saati ölçmüyor (kodun
kendi yorumu bunu söylüyor) · T-31 adalet penceresi takvim ayında
sıfırlanmıyor · T-33 `_dilimler(0, 8.5, 12.5) -> [8, 9, 10, 11]`, yarım
saatler kayboluyor · T-36 `YenileAsync` oku-kontrol-işaretle-kaydet yapıyor,
`RowVersion` / işlem / seviye yok.

**T-32 🟡 — bunu bugün ben açtım.** K-30'u yazarken fazla mesai tavanını
çözücüde **profil tablosundan**, doğrulayıcıda **kural parametresinden**
okur hâle getirdim. Bugün aynı sayıyı veriyorlar; kiracı parametreyi
değiştirdiği gün sessizce ayrışırlar. §7.6'nın bağımsızlığı kural mantığını
ayırıyor, **ortak gerçeğin tek kaynağını** garanti etmiyor.

**Öncelik tablosu yeniden sıralandı** — ölçüt *yanlış karar riski*:
T-27 · T-35 · T-34 · T-28 · T-29 · T-19 · T-21 · T-18 · T-22.

**Düzeltme yine yapılmadı, bilerek.** Beş bulgu ürün kararı içeriyor.
Kaydedildi, uydurulmadı.

→ `00-DEVIR/06-ACIK-RISKLER.md` T-27 … T-36

**2026-09-16 · DIŞ İNCELEME, 1. ve 2. tur — dokuz bulgu, iki yanlış iddia**

Motor bittikten sonra proje **başka bir modele** (GPT) şartnameyle birlikte
incelettirildi. **Dokuz bulgunun tamamı** bizim tarafımızda doğrulandı.
*(Üçüncü tur ayrı girdide, yukarıda.)*

**T-18 🔴 — yayın kapısı.** Gövdesi yazılmamış ama aktif ve SERT bir kural
varken doğrulayıcı aynı cevapta *"bu kuralı kontrol edemedim"* ve
*"yayınlanabilir"* diyor. `denetle.py` içinde kendi yazdığımız cümle
*"'ihlal bulamadım' ile 'bakmadım' aynı şey değildir"* — ilkeyi yazmışız,
kapıya bağlamamışız. O-1'in tam şekli.

**T-19 🔴 — talep biçimi.** Şartname §11.2 `{ekip, gun, saat}` diyor, motor
`{gunler:[], saatler:[]}` okuyor. Şartname biçimi verildiğinde **sıfır
atamalı plan** üretiliyor ve %100 kapsama ile yayına açılıyor.

> **Bağımsızlık tek başına yetmiyor.** §7.6 çözücü ile doğrulayıcıyı kural
> mantığında ayırıyor, ama ikisi de girdiyi aynı fikstür geleneğiyle okuyor.
> Birbirleriyle tutarlılar, ikisi de şartnameyle tutarsız. D-6'ya karşı
> kurulan savunma, ortak yanlış bir **girdi yorumuna** karşı boş.

**Yanlış iddia düzeltildi.** *"On iki altın senaryonun tamamı yeşil"*
cümlesi **yanlıştı**. `12 passed` = 7 altın senaryo + paketin kendi 5 sağlık
testi. A2, A10, A11, A12 backend tarafında ve **hiç sınanmadı** — çift
tıklama, geçmiş veri ve plan kopyalama tamamlanmış güvence değil. Cümle
dokümanlara ve commit mesajlarına girmişti; hepsi düzeltildi.

**Yanlış sayı düzeltildi.** Doğrulayıcıda **19** kural var, doküman 17
diyordu — üstelik aynı dosyanın tablosu 19 satır listeliyordu. `DENETIM.py`
yakalayamaz: tutarlılığa bakar, doğruluğa değil.

**İkinci turda beş bulgu daha.** **T-21** 🔴 çok ekipli çalışan iki ekibin
ihtiyacına birden sayılıyor — modelin `x` değişkeninde ekip boyutu yok; tek
kişiyle yapılan deneyde motor *"çözüldü"* derken asgari kapsama %50 çıktı.
**T-22** 🔴 çözümsüzlükte sunulan `en_iyi_plan` bağımsız denetimden geçmeden
dönüyor, üstelik sıfır atamalı plan `var: True` diyor. **T-23** zaman aşımı
ile gerçek çözümsüzlük aynı cevabı alıyor. **T-24** K-28'in *"2 dakika
durgunluk"* koşulu **hiç yazılmamış**, ayrıca süre bütçesi isteğin tamamını
kapsamıyor — 0,05 saniyelik bütçeyle yapılan çağrı **57,4 saniye** sürdü.
**T-25** servis tek iş parçacıklı.

**T-26 açıldı: kayıt ile yürürlük arasında kontrol yok.** K-28 kayda geçti,
şartnameye işlendi, kodun başında anlatıldı, "kapandı" sayıldı — ve ikinci
koşulu hiç yazılmadı. Ne kırmızı kanıt, ne `DENETIM.py`, ne CI yakaladı;
hiçbiri *"her K-kararının onu çiviyen bir testi var mı"* diye sormuyor.
O-1'in genel hali: O-1'de RLS tanımlıydı ama etkisizdi, burada karar kayıtlı
ama yürürlükte değil.

**Yöntem kayda geçti:** iç kırmızı kanıt *"varsayımlarımız korunuyor mu"*
sorar; dış inceleme *"varsayımlarımız doğru mu"* sorar. İkincisi olmadan
birincisi kendi dünyasında kusursuz kalır. Bir iş parçası bittiğinde,
şartnameden türetilmiş girdilerle **başka bir modelle** inceleme yapılır.

Düzeltme yapılmadı — T-18 ve T-19'un ikisi de ürün kararı içeriyor.

→ `00-DEVIR/06-ACIK-RISKLER.md` T-18 … T-26

**2026-09-16 · T-17 kapandı · Actions eylemleri Node 24'e çıkarıldı**

CI kapısının ilk koşusunda iki uyarı çıkmıştı: eylemler Node 20 hedefliyordu,
GitHub onları Node 24'te zorla koşturuyordu. Kapı çalışıyordu ama zorlama
kalkınca çalışmayacaktı — kendi kendine kırmızıya dönecek bir madde.

checkout v4→**v7**, setup-python v5→**v7**, setup-dotnet v4→**v6**. En güncel
ana sürümlere çıkıldı ki aynı iş birkaç ay sonra tekrarlanmasın. `checkout`
v7'nin kırıcı değişikliği fork PR'larıyla ilgili (`pull_request_target` /
`workflow_run`); bu depoda o tetikleyiciler yok.

**Önce dalda denendi.** Workflow zaten `branches: ["**"]` ile her dalda
koştuğu için `ci/node24` dalına push edildi, orada yeşil yandığı görüldü,
sonra `main`'e alındı. Gerekçe bir değişmez: *"`main` her zaman yeşildir"* —
bir CI değişikliği için bedava riske atılmaz.

→ `.github/workflows/testler.yml`

**2026-09-16 · Güncelleme ritüelinin tetikleyicisi değişti**

Devir dosyalarının **ne zaman** güncelleneceği tek cümleye bağlıydı:
*"Mustafa 'güncelle' dediğinde."* Yani birinin hatırlamasına bağlıydı —
hatırlamaya bağlı bir bekçi bekçi değildir (O-1). Üç somut ana bağlandı:
aynı commit'te (karar/kural/kapanan madde), iş parçası bitince (oturum
günlüğü), oturum kapanırken (neredeyiz + sıradaki adım + DENETIM).

En önemlisi ilki: oturum her an bitebilir, doküman koddan geriden geliyorsa
bir sonraki pencere yanlış haritayla başlar.

`DENETIM.py`'ye *"kod değişti ama devir dosyası değişmedi"* kontrolü
**eklenmedi** — küçük düzeltmelerde sürekli öterdi, O-7'nin dersi tam bu.
Bilinçli bir boşluk olarak kayda geçti.

→ `00-DEVIR/00-BURADAN-BASLA.md` §5

**2026-09-16 · MOTOR CI KAPISINA BAĞLANDI — ilk koşu YEŞİL**

`.github/workflows/testler.yml` içine **`motor`** adlı ikinci bir iş eklendi:
60 birim testi + 12 altın senaryo + fikstür denetleyicisi. Docker
gerektirmiyor. Python **3.14**'e sabitlendi — Mustafa'nın makinesindeki
sürümün aynısı; gerekçe workflow'da docker için zaten yazılıydı: *"CI ile
yerel arasında fark olmasın"*.

**Neden ayrı iş, aynı işe ek adım değil:** aynı işte olsalardı .NET tarafının
kırmızısı motorun sonucunu **gizlerdi** — bir adım patlayınca sonrakiler hiç
koşmaz.

**Kapının kendi kırmızı kanıtı yapıldı.** Bir kapının en tehlikeli hâli,
koruduğu şey yokken de yeşil yanmasıdır. Ölçüldü: `TSHIFT_MOTOR_URL`
verilmezse `exit=1`, servis kapalıysa `exit=1`, sağlık beklemesi 20 sn'de
cevap alamazsa adım `::error::` ile duruyor.

`09-motor/requirements.txt` eklendi, sürümler sabitlendi (O-8 gerekçesi).
Doğrulayıcının dış bağımlılığı yok ve bu bilerek korunuyor.

**İlk koşu yeşil** (`47c7050`). Uyarı yazısı yazıldığı gün konulmuş, ancak
yeşil koşu görüldükten sonra kaldırılmıştı — 12 Eylül'de tersi yaşandığı için
(dokümanda *"bekçi eklendi"* yazıyordu, bekçi yoktu; O-1).

Tek çıktı iki uyarı, ikisi de bugünden değil: eylemler (`actions/checkout@v4`,
`actions/setup-python@v5`, `actions/setup-dotnet@v4`) Node 20 hedefliyor,
GitHub Node 24'e zorluyor. Kapıyı kırmıyor ama zamanla kıracak — **T-17**.

→ `.github/workflows/testler.yml` · `09-motor/requirements.txt`

**2026-09-16 · ÇÖZÜCÜ YAZILDI · ON İKİ ALTIN SENARYONUN TAMAMI YEŞİL**
**.NET ürün kodu değişmedi, 39/39 hâlâ yeşil.**

**Motor tamamlandı.** `09-motor/cozucu/` (CP-SAT) ve `09-motor/orkestra.py`
(§11.7 onarım döngüsü) yazıldı. Kalan beş kırmızı senaryo — A1, A3, A6, A7,
A9 — yeşile döndü. Birim testi 44 → **60**, altın senaryo **12/12**.

**Üç senaryo kolay yeşile dönmedi ve üçü de gerçek bir boşluk buldu:**

- **A9** — `shift_templates`'te *"bu şablon hangi günlerde kullanılır"* alanı
  **yoktu**. "Cumartesi nöbeti" adlı 4 saatlik şablonu motor hafta içi de
  kullanıyor, kapasiteyi 42 yerine 49 gösteriyordu. Tahminle değil **deneyle**
  bulundu: şablon çıkarılınca kapasite tam olarak fikstürün belgelediği 42'ye
  düştü. **Ders:** bir alanın *adı* motoru bağlamaz; bağlayan tek şey kısıttır.
  → `gunler` alanı eklendi (T-14 kapandı)
- **A1** — `/solve` §11.7 onarım döngüsünü hiç koşmuyordu. `orkestra.py`
  yazıldı: üret → **bağımsız** doğrulayıcıyla denetle → en fazla 2 onarım.
  Denetim her zaman **kullanıcının** girdisiyle yapılıyor, onarımın eklediği
  kilitlerle değil — yoksa motor kendi koltuk değneğini kural sanardı.
- **A7** — üç ayrı boşluk birden. (1) Motor `profil` alanını **hiç
  okumuyordu**; §5.4 ağırlık tablosu kodda yoktu. (2) `ADALET_DENGESI`'nin
  eşik altında gradyanı yoktu, yani ağırlığı değiştirmek planı
  değiştiremiyordu — iki profil **birebir aynı planı** üretiyordu. (3)
  **Fikstürün kendisi de eksikti:** kabul ölçütü *"Ç01–Ç03 en müsait
  olanlar"* diyordu ama fikstürde on çalışan birbirinin aynısıydı, yani
  cumartesiyi kime verdiğin kapsamaya **hiçbir şey mal olmuyordu**.

> **A7'nin dersi.** Onaylı bir cümle fikstüre çevrilmemişse, senaryo
> anlattığı şeyi sınamaz. Cümle onaylıydı, fikstür ona uymuyordu — ve bu
> ancak motor yazılınca görüldü.

**K-29 doğdu: eşik ihlali sayar, planı gradyan seçer.** Adalet eşiği
(K-27) yalnız doğrulayıcıda; motorda yerine **artan marjinal maliyet** var.
İki yanlış biçim denendi ve **ölçümle** elendi: *"ortalamanın üstündeki
sapma"* denendiğinde motor cumartesiye gerekenden fazla kişi koymaya başladı
(3 yerine 5) — ortalamayı yükseltmek herkesin sapmasını düşürüyordu, yani
ceza cezalandırdığı şeyi ödüllendiriyordu. Aynı açık eşik teriminde de vardı;
çıkarıldı ve o anki 57 birim + 12 altın testin **hiçbiri değişmedi** — terim zaten
atıl duruyordu.

**Kırmızı kanıt ilk turda 8'de 4'ünü KAÇIRDI.** Ağırlık tablosu yok sayılsa,
adalet gradyanı kaldırılsa, orkestra doğrulayıcıyı çağırmasa ya da fazla mesai
tavanı sabitlense **hiçbir test kırmızı yanmıyordu**. Üçüncüsü özellikle
öğretici: import'a bakan test yakalamıyor, çünkü import durur, **çağrı**
kaybolur. Eksik testler yazıldı (`09-motor/testler/test_profiller.py`, 13
test); ikinci turda **12/12 yakalandı**.

**Ölçüm yöntemi de bir tuzak çıkardı.** *"Motor şu kişiyi seçti"* testleri
kırılgan: kısıt gevşekse çözücü eşit değerdeki seçenekler arasında arama
sırasına göre seçiyor ve **bozulmuş kod aynı cevabı verebiliyor**. Bu
varsayılmadı, denendi ve doğrulandı. Çözüm: `amac_degeri` çıktıya eklendi;
aynı girdi, iki seçim sabitlenmiş hâlde çözülüp amaç değerleri
karşılaştırılıyor.

**K-29 ve K-30 karara bağlandı.** K-29 onaylandı: adalet eşiğin altında da
bir **tercihtir**; üç plan kartını birbirinden farklı yapan mekanizma bu.

K-30'da soruyu kötü sormuşum — *"bir saat fazla mesai kaç saatlik açığa
değer"* diye, yani ceza katsayısı dilinde. Mustafa haklı olarak *"ben tam
neyi cevaplayayım onu da anlamadım"* dedi ve kararı ürün dilinde verdi:
**"Zaten hedef hiç gitmemek. Gidilecekse de minimum gitmek."** Ölçüldü — kod
bunu **zaten yapıyormuş**: hedef kapsama için 0 saat, asgari kapsama zorlarsa
tam gereken kadar. Sayı değişmedi, üç test kararı çiviledi.

**Riski açarken yazdığım teşhis yanlıştı ve düzeltildi.** *"Profil tavanı
pratikte hiç kullanılmıyor"* demiştim; tavan **ölü değil** — zorunlu aşımın
sınırını o çiziyor (CALISAN'da tavan 0 → plan çözümsüz). Ölçüm doğruydu,
yorumu yanlıştı: ölçtüğüm sayıyı ürün kararının yerine koymuşum. T-15 kapandı.

**O-9 · Gönderilmeyen dosya iki tarafta da "temiz" görünüyordu.** Mustafa'nın
makinesinde ilk koşuda A06 kırmızı yandı ve birim testi 53 çıktı (57 değil):
doğrulayıcıdaki `KILIT_UYUMU` düzeltmesi ve 4 testi **hiç gönderilmemişti.**
Hiçbir yerde kırmızı yanmıyordu — git temiz, `DENETIM.py` *"commit bekleyen
0"*, testler yeşil; çünkü her iki taraf **kendi içinde** tutarlıydı ve
tutarsızlık **aralarındaydı**.

Yakalayan şey `orkestra.py` oldu: `/solve` ilk kez doğrulayıcıyı çağırınca
eski `KILIT_UYUMU`, A06'nın `tip: "yasak"` kilidinde patladı. Onarım
döngüsünün yazıldığı ilk gün amacı dışında bir şeyi de yakaladı.

Kalıcı bekçi: **commit öncesi dosyalar karşı taraftan çekilip içerikçe
karşılaştırılır** — hafızaya değil `cmp`'ye güvenilir. D-1 zincirine yeni
halka: *yazdım ≠ gönderdim ≠ commit ettim ≠ karşı tarafta değişti ≠
göndermem gerektiğini fark ettim.*

→ `09-motor/` · `02-spec/v1.4-master-spec.md` §5.4, §6.5, §6.7, §8.4, §11.3
→ `00-DEVIR/08-URUN-KARARLARI.md` K-28, K-29, K-30
→ `00-DEVIR/05-HATA-OTOPSILERI.md` O-9
→ `00-DEVIR/oturumlar/2026-09-16-cozucu.md`

**2026-09-16 · ADALET KURALI YAZILDI (K-27) · kırmızı kanıt ÜÇ ZAYIF TEST buldu**
**.NET ürün kodu değişmedi, 39/39 hâlâ yeşil. A4 ve A8 yeşil kalmaya devam.**

**T-12 ve A-17 kapandı.** Mustafa eşiği verdi: *"ortalamadan 2 gece fazla
çalışıyorsa bu adaletsizliktir; 1 gün fazla olabilir."* Kural yazıldı — ölçü
ortalamadan sapma, eşik 2, karşılaştırma `>=`, tek yönlü, devir yükü dâhil.

**K-11 ile ters yönde ve bu tuzak kayda değer:** *"asgari 11 saat"* 11'i
kapsar (ihlal değil), *"eşik 2"* 2'yi kapsar (ihlaldir). Biri bir **taban**,
diğeri bir **sapma tavanı**. K-11 alışkanlığıyla okunsaydı kural tam sınırda
sessizce kaçırırdı.

**Asıl olay: kırmızı kanıt bu sefer BENİ yakaladı.** Yeni kuralı altı şekilde
kasten bozdum, **üçü kaçtı** — ve kabahat doğrulayıcıda değil testlerimdeydi:

- Varsayılan eşik 2→3 **kaçtı**: bütün testler eşiği açıkça geçiriyordu,
  varsayılan hiç koşmuyordu
- `>=` → `>` **kaçtı**: hiçbir vaka tam sınıra oturmuyordu (sapma hep 2,25)
- Tek yönlü → `abs()` **kaçtı**: kimse ortalamanın 2 altında değildi

Üç test yeniden yazıldı, sonra dördüncü bir boşluk çıktı: gece penceresi
20→22'ye kaydırılınca hiçbir test kırılmadı, çünkü bütün gece vakalarım
20:00–01:00 kullanıyordu. Sınırı çiviyen iki test daha eklendi.

**Son durum: 8 kasten bozma, 8'i de yakalandı. 36 test yeşil.**

**T-13 açıldı:** `saat` boyutu yazılmadı — K-27 eşiği **sayı** olarak verdi,
`saat` süredir ve `SAAT_DENGESI` ile örtüşüyor olabilir. Sessizce atlanmıyor:
kuralın kendisi yazılı olduğu için `uygulanmayan_kurallar` göremezdi, ayrı bir
`eksik_boyutlar` alanı eklendi ve bir test onu koruyor.

*Öğrenilen: bir eşiği sınayan test, o eşiği açıkça geçiriyorsa varsayılanı hiç
sınamaz. Bir sınır değerini sınayan test, vakası tam sınırda değilse `>` ile
`>=` farkını göremez. İkisi de yeşil yanar ve hiçbir şey korumaz.*
→ `09-motor/dogrulayici/kurallar.py`, `02-spec/v1.4-master-spec.md` §6.5,
`00-DEVIR/08-URUN-KARARLARI.md` K-27

**2026-09-16 · BAĞIMSIZ DOĞRULAYICI YAZILDI · A4 ve A8 YEŞİL**
**.NET ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.**
Fikstürlerin tek satırı değişmedi.

**Projede motorun İLK KORUNAN DAVRANIŞI.** `09-motor/` — `/evaluate` ucu,
17 kural gövdesi, 26 birim testi. Kabul ölçütü bu iki senaryoda taahhüt
olmaktan çıkıp **bekçiye** dönüştü.

```
py -m pytest -q   ->  5 failed, 7 passed, 4 skipped   (onceki: 7/4/5)
```

**Neden önce doğrulayıcı:** yedi kırmızının ikisi plan üretmiyor, var olan
planı denetliyor — çözücü olmadan yeşile dönebilecek tek iki senaryo onlardı.
Kalan beş kırmızı **doğru sebeple** kırmızı: servis ayakta, `/solve` 501
dönüyor, istemci bunu *"COZUCU YAZILMADI"* diye ayırt ediyor.

**Dışarıdan hiçbir paket yok.** Python standart kütüphanesi. Kurulum adımı
olmayan bir servis, "bende çalışmadı" ile geçen saatleri de ortadan kaldırır.

**Kırmızı kanıt: 7 kasten bozma, 7'si de yakalandı.** Her biri sessizce
bozulabilecek bir ürün kararı — `GUNLUK_AZAMI` 11→9 (K-18), mola hakkı brüt
yerine net (K-4), tam 11 saat ihlal sayılır (K-11), örtüşmede çift ihlal
(V-1), yayın kapısı `yasal`a bakar (K-24), gövdesi olmayan kural sessizce
geçilir, `ASGARI_KAPSAMA` molayı düşer.

**`ADALET_DENGESI` bilerek yazılmadı.** Şartname kuralı tanımlıyor ama ihlal
eşiğini tanımlamıyor. Eşiği koda gömmek, ürün kararını kodun içine gizlemek
olurdu. Uygulanmayanlar listesinde görünüyor ve bir test birinin ileride
sessizce eşik uydurmasını engelliyor. **T-12 / A-17.**

**Testler iki kendi hatamı yakaladı:** (1) "motor çöktü" ile "çözücü yok"
aynı mesajı veriyordu — ayrıldı; (2) istemcide `adres=""` ile `adres=None`
aynı sayılıyordu, bu yüzden *adressiz davranış hiç sınanamıyordu*.

**"Motor gelince tek dosya değişecek" sözü tutuldu** — yalnız
`motor_istemci.py` değişti.

⛔ **Çözücü için tek zorunlu kural:** doğrulayıcıyla mantık paylaşmayacak
(§7.6, §16.1). *"Aynı hesabı iki kez yazmayalım"* deyip ortak modül çıkarmak
yasak — tekrar burada maliyet değil, güvence.

*Öğrenilen: "boş değer" ile "belirtilmemiş" aynı şey değil. `x or y` kalıbı
bu ikisini sessizce birleştirir ve bir testi yanlışlıkla başka bir yolu
denemeye gönderir.*
→ `09-motor/`, `00-DEVIR/oturumlar/2026-09-16-bagimsiz-dogrulayici.md`

**2026-09-16 · ŞARTNAME v1.4 YAZILDI · A-15 kapandı · dokuz yeni karar**
**Ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.** v1.3'e
dokunulmadı — v1.4 tam dosya olarak yanına yazıldı.

**Ana değişiklik:** kural kataloğu **`yasal` ve `kabul_edilebilir` sütunlarını**
kazandı, 35 kuralın tamamı sınıflandırıldı. Bu olmadan iki onaylı karar
(K-10 kabul edilmiş ihlal, K-16 yayın kapısı) **uygulanamıyordu** — sistem hangi
ihlali kabul etmeye izin vereceğini bilemiyordu.

**Dokuz yeni karar (K-18…K-26).** Öne çıkanlar: yasal kuralın değeri kanunun
değeridir, firma değiştiremez (`GUNLUK_AZAMI` **9 → 11**) · firma için ayrı
günlük azami kuralı açılmayacak · yasal ihlal hiçbir koşulda kabul edilemez ·
sağlık raporu için ayrı kural · kabul yetkisi = yayın yetkisi.

**Bir çelişki çıktı ve sessizce çözülmedi.** Mustafa K-18'i verirken *"firma
esnetemez ama ihlali onaylayabilir"* dedi; bu K-16 ile çelişiyordu. Çelişki
açıkça soruldu, üç seçenek sunuldu, **en katısı** seçildi. Yanlış dal seçilseydi
A4 kabul ölçütü, fikstürü ve yayın kapısı testleri yeniden yazılacaktı.

**Tablo doldurulurken iki tasarım sorunu çıktı.** `AKTIF_CALISAN` yasal bir
kural değil ama ihlali de kabul edilemez — iki gruplu tabloda sistem
*"ayrılmış çalışanı planda tutmayı kabul ediyorum"* seçeneği sunardı. Bayrak
ikiye ayrıldı: `yasal` dürüst etiket, `kabul_edilebilir` yayın kapısının baktığı
alan. İkincisi: `YETKINLIK_KAPSAMASI`'nda bayrak kuralın değil **satırın**
özelliği — ilk yardımcı yasal, barista değil.

**Mevzuat araştırması yapıldı** (Mustafa'nın isteğiyle, birincil kaynaklardan —
forum kullanılmadı). İki belirsizlik çözüldü, **katalogda olmayan bir yasal
kural** bulundu (`GECE_POSTASI_DEVRI`, Postalar Yön. md. 8) ve gece 7,5 saat
sınırının **turizm istisnası** ortaya çıktı (6645 s. K.) — ilk müşteri verisi
seyahat acentesine ait olduğu için bu teorik değil.

**Şartnamede dört yanlış bulundu:** §5.2'de 9 saat *"İş Kanunu üst sınırı"*
diye etiketlenmiş (kanun 11 diyor) · "27 kural" yazıyor, gerçek 33 · künye
tablosunda sürüm hâlâ 1.1 · `employee_contracts.gunluk_azami_saat` olmayan bir
yetkiyi gösteriyor.

**Okuma bir maddeyi de gereksiz çıkardı:** *"`leaves` durum alanı eklenecek"*
— v1.3 §8.3'te **zaten vardı.** K-9'un gerçek eksiği alan değil, yayınlanmış
planı düşüren akıştı.

**Fikstürler güncellendi, sonuç değişmedi:** 11/11 tutarlı, pytest yine
7 kırmızı / 3 yeşil / 4 atlanan. Kontrol edildi, tahmin edilmedi.

*Öğrenilen: "eksik" diye kaydedilen bir madde, kapatılmadan önce gerçekten
eksik mi diye bakılmalı. On maddenin biri zaten yapılmıştı; iki madde de liste
yazılırken hiç görülmemişti.*
→ `02-spec/v1.4-master-spec.md`, `02-spec/v1.4-hazirlik/`,
`00-DEVIR/08-URUN-KARARLARI.md`, `00-DEVIR/oturumlar/2026-09-16-sartname-v14.md`

**2026-09-16 · `DENETIM.py` İLK KEZ koştu · 17 hata buldu, hepsi düzeltildi**
**Ürün kodu değişmedi.** Betik 14 Eylül'de yazılmıştı ama üç oturumdur
koşturulamıyordu (uzaktan kabuk çalışmıyor). Mustafa bugün ilk kez kendi
makinesinde koşturdu.

**17 HATA, 14 uyarı.** Hepsi tek sebepten: `02-DEGISMEZLER.md` ve
`08-URUN-KARARLARI.md` içindeki 17 atıf hâlâ dondurulmuş **v2** ve **v4**
sürümlerini gösteriyordu, güncel **v5**'i değil. 14 uyarının tamamı tarihsel
dosyalarda — aksiyon gerekmiyor.

**Asıl bulgu, ve D-1 kuralını genişletiyor:** O iki dosya aslında
düzeltilmişti, ama düzeltme makineye hiç gönderilmemişti. Yakalanmama sebebi:
`v2` → `v5` değişimi **dosya boyutunu değiştirmiyor.** İki dosya da her iki
tarafta birebir aynı byte sayısındaydı (19 023 ve 29 883).
*"Yerel kopya = makine kopyası" varsayımının yanlış olduğunu biliyorduk;
yeni olan, **boyut karşılaştırmasının bu varsayımı doğrulamadığı.** Aynı
uzunluktaki bir düzeltme sessizce kaybolur.*

**Betiğin kendi hatası da çıktı:** `govde()` kod bloklarını silerek
çıkarıyor, bu yüzden sonraki satır numaraları kayıyordu. Bugün doğru satırı
göstermesi şanstı (o iki dosyada kod bloğu yok). Düzeltildi — blok yerine
aynı sayıda boş satır konuyor.

*Öğrenilen: bir denetim aracının kendi çıktısı da denetlenmeli. Yanlış satır
numarası veren hata mesajı insanı yanlış yere bakmaya gönderir.*
→ `DENETIM.py`, `00-DEVIR/02-DEGISMEZLER.md`, `00-DEVIR/08-URUN-KARARLARI.md`,
`00-DEVIR/oturumlar/2026-09-16-fikstur-ve-test-iskeleti.md` (EK bölümü)

**2026-09-16 · Fikstürler + test iskeleti yazıldı · yedi test BİLEREK kırmızı**
**Ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.** Yeni paket CI'ya
**bağlanmadı** — kırmızı bir paketi kapıya bağlamak "main her zaman yeşil"
kuralını bozardı.

Onaylı kabul cümleleri (15 Eylül) önce **veriye**, sonra **koşan teste**
çevrildi. Zincir kapandı: kabul ölçütü → fikstür → test → (motor).

**Fikstürler:** 11 JSON + ortak sahne `_sahne-S10.json`. A5 yok — yaz saati
ertelendi (K-12). Fikstür kod değil veri; motor hangi dille yazılırsa yazılsın
aynı dosyalar koşar. Sahne 11 dosyadan ortaklaştırıldı; her senaryo yalnız
kendi `fark`ını taşıyor.

**Test iskeleti:** pytest çatısı (A1, A3, A4, A6, A7, A8, A9) ve `.cs.taslak`
uzantılı xUnit taslakları (A2, A10, A11, A12 + yayın kapısı, 20 test adı).
Sonuç: **7 kırmızı / 3 yeşil / 4 atlanan.** Kırmızı istenen durumdur —
spec §16.4 "kırmızı kanıt" kuralı, bir testin yeşile dönmeden önce kırmızı
yanmasını şart koşar.

**İki şey bilerek bozuk bırakıldı, ikisi de CI'ı korumak için:** C# taslakları
`.cs` değil (derlenirse CI kırılır, dayandıkları tablolar yok) ve pytest paketi
`dotnet test` kapısına bağlanmadı.

**Üç test motorsuz da yeşil** ve asıl işi onlar yapıyor: fikstürler
yükleniyor mu, fikstürde geçen her `kontrol` adının kodda gövdesi var mı,
motor yokluğu sessizce mi geçiliyor. Üçüncüsü yazılırken bir eksik yakalandı —
A07 fikstüründe kullanılan bir kontrolün gövdesi yoktu.

**Anti-kopya kararı:** `fikstur_yukleyici.py` ortak modüle çıkarıldı.
Denetleyici ile test aynı `fark` birleştirme mantığını kullanmasaydı,
denetleyici "tutarlı" derken test başka bir şey sınıyor olurdu.

**`DENETIM.py` yol kontrolü için düzeltme:** belgelerdeki `v5/...` biçimindeki
kısa yollar depo kökünden yazıldı (`08-motor-testleri/v5/...`), yoksa 3.
kontrol hepsini "bulunamayan yol" sayacaktı. Yazılmamış `02-spec/v1.4-master-spec.md`
bilerek-yok listesine gerekçesiyle eklendi.

*Öğrenilen: bir denetleyici yazmak, denetlediği şeyi yazmaktan daha çok
düzeltme doğuruyor. Yolları kısaltmak okurken rahattı, makine için yanlıştı.*
→ `08-motor-testleri/v5/fikstur/`, `08-motor-testleri/v5/testler/`,
`00-DEVIR/oturumlar/2026-09-16-fikstur-ve-test-iskeleti.md`

**2026-09-15 · Altın senaryolar A1–A12 ONAYLANDI · on yeni ürün kararı**
**Ürün kodu değişmedi, test eklenmedi, hiçbir test koşmuyor.** Bu bir karar
satırıdır, kilometre taşı değil — etiket atılmadı.

Spec §16.3'teki on iki senaryonun *"doğru çalışıyorsa ne görmeliyiz"* cümleleri
Mustafa tarafından **tek tek onaylandı**. Altı varsayımın (V-1…V-6) hepsi karara
bağlandı. A5 (yaz saati) ertelendi, altyapısı korunuyor.

**Üç sürüm gerekti.** v2 yazılım tarafına göre yazılmıştı; Mustafa *"ben tam
olarak neye onay veriyorum"* diye sorunca v3'te anlatım iş diline çevrildi.
Geri bildirimi v4'te içeriği değiştirdi — **sahne gerçekçi olmadığı için baştan
kuruldu** (çoklu vardiya tipi, part-time, cumartesi nöbeti), A2/A3/A7/A8
yeniden yazıldı. v5 onayın dondurulmuş hâli.

**On karar (K-8…K-17)** ve **bir geri alma (K-1)**. Öne çıkanlar: izin
planlamayı ezer · yönetici çözümsüz planı kabul edebilir (yasal kural hariç) ·
yayın kapısı — taslak ihlal taşıyabilir, yayınlanmış plan taşıyamaz ·
`MOLA_KAPSAMASI` yumuşadı · çalışan tercihi diye bir şey yok, uygunluk
sözleşmeden gelir.

**K-1 geri alındı ve sebebi kayda değer:** Claude 14 Eylül'de *"tam 11 saat
dinlenme ihlal mi?"* diye sormuştu. Mustafa *"ben neye yanlış karar verdim
anlamadım"* dedi ve haklıydı — yanlış karar vermemişti, **yanlış soru
sorulmuştu.** Aritmetik bir kenar durumu ürün kararıymış gibi sunulmuştu.

**İki şartname eksiği bulundu ve ikisi de senaryolar yazılırken çıktı, şartname
okunurken değil:** `leaves` tablosunda izin durumu alanı yok, ve §6 kataloğunda
**`yasal` sütunu yok** — ikincisi olmadan "hangi ihlal kabul edilebilir" sorusu
cevaplanamıyor, yani iki yeni karar uygulanamaz durumda. Yeni açık maddeler:
**A-15** (şartname v1.4, on maddelik fark) ve **A-16** (iki hukuki yorum uzman
bekliyor).

*Öğrenilen: kabul ölçütü yazmak, şartnameyi denetlemenin en ucuz yolu. Okurken
"yazılmış mı" diye bakarsın; senaryo yazarken "bu davranışı ifade edebiliyor
muyum" diye. İkinci soru eksiği bulur.*
→ `08-motor-testleri/v5/`, `00-DEVIR/08-URUN-KARARLARI.md`,
`00-DEVIR/oturumlar/2026-09-15-altin-senaryo-onayi.md`

**2026-09-15 · Çalışma biçimi: geri bildirim yüzeyleri · paralel ajan reddedildi**
**Ürün kodu değişmedi, test eklenmedi, ölçüm yapılmadı** — bu satır bir karar
satırıdır, kilometre taşı değil. Etiket atılmadı.

Mustafa bir videoda gördüğü dört pencereli modeli sordu (kod Claude'da, hata
ayıklama opencode'da paralel, ayrı pencerelerde testler ve sunucu günlükleri).
Model ayrıştırıldı: **işe yarayan yarısı ajanla ilgili değil**, kırmızının ne
kadar geç fark edildiğiyle ilgili.

**Alınan:** Aktif pencerenin yanına **yazmayan** bir gösterge penceresi —
günlükler sürekli (`docker compose logs -f`), testler **talep üzerine**
(`.\TEST.ps1`). Testler sürekli koşamıyor çünkü `TEST.ps1` API'yi önce
durduruyor (`00-BURADAN-BASLA.md` §7). *Bu ortam gerçeği olmasa, sürekli
koşan bir test penceresi kurulur ve API'nin neden sürekli düştüğü saatlerce
aranırdı.* Doğurduğu asıl kural: **ajan "bitti" demeden önce testleri kendisi
koşar.**

**Reddedilen:** Paralel ikinci **yazıcı** ajan. Gerekçe depodan geldi — R5
(*iki pencere yazar, sürüklenme*) 14 Eylül'de kapatılmıştı; yeniden açacak
ölçülmüş bir gerekçe yok. opencode `06-ACIK-RISKLER.md`'deki *"şimdilik
kullanılmayacak"* tablosuna girdi; **salt-okunur inceleyici** olarak M-09
doğrulayıcısından sonra yeniden bakılacak, iki haftalık ölçüm şartıyla.

**Yeni devir dosyası açılmadı** — R7 sorusu soruldu, cevabı "evet, var olan
bir dosyanın bölümü olabilir" çıktı. `00-DEVIR/` kökü **dokuz dosyada kaldı.**
→ `00-DEVIR/00-BURADAN-BASLA.md` §5b, `00-DEVIR/06-ACIK-RISKLER.md`,
`00-DEVIR/oturumlar/2026-09-15-calisma-bicimi-opencode.md`

**2026-09-14 · Altın senaryolar tanımlandı, devir denetimi betiğe çevrildi**
Spec §16.3'teki A1–A12'nin beklenen sonuçları Türkçe kabul cümlelerine
çevrildi — motor yazılmadan, motora bakmadan, şartnameden türetilerek.
`08-motor-testleri/` açıldı: `v1/` taslak (donduruldu), `v2/` kararlar
işlenmiş hâli, bir örnek fikstür ve fikstürün kendi içinde tutarlılığını
kontrol eden bir betik. **Cümleler onay bekliyor; hiçbir test koşmuyor.**

**Yedi ürün kararı** alındı ve yeni bir sicile geçti (`00-DEVIR/08-URUN-KARARLARI.md`,
K-1…K-7). En çok şeyi değiştiren K-1: **sınır değerler ihlal sayılır** — tam
11 saat dinlenme, tam 9 saat günlük çalışma. Firma ayarı olarak esnek
bırakılıyor (`sinir_dahil` parametresi). K-7 doğrudan yeni bir test doğurdu:
hafta toplamında yetersiz kapasite, hücre bazlı teşhisin göremediği durum.

**`DENETIM.py` yazıldı** — `00-BURADAN-BASLA.md` §5'teki denetim ritüeli artık
elle değil makineyle yapılıyor: test adları `DisplayName` ile birebir eşleşiyor
mu, sayılar tutuyor mu, dosya yolları var mı, commit edilmemiş devir dosyası
kaldı mı. *Gerekçe: §5b "asıl güvence testlerdir, doküman değil" diyor ama
`00-DEVIR/` bu ilkenin dışında kalan tek parçaydı.*

**İlk koşusunda elle bulunmamış altı tutarsızlık çıktı, dördü düzeltildi:**
üç dokümanda `M0` test adı eksik ya da kısaltılmış yazılmıştı (biri
`0 - Baglanan...` diye, baştaki M düşmüş), `H1` kısaltılmıştı, ve
`02-DEGISMEZLER.md` özet tablosu **45/41** diyordu — doğrusu **47/39**.
Y-13 ve Y-14 satır olarak eklenmiş ama özet güncellenmemişti. D-3 hatası
14 Eylül'de iki yerde düzeltilmişti; **üçüncü yer gözden kaçmıştı.**

Pencere protokolüne **açılış beyanı** eklendi: yeni pencere iş yapmadan önce
ne okuduğunu ve sıradaki adımı nasıl anladığını söyler. Risk tablosundaki
*"doküman yanlış başlarsa yakalamaz"* açığını kapatıyor.
⚠ `00-DEVIR/` dokuz dosyaya ulaştı — **R7 eşiği.**
→ `08-motor-testleri/`, `00-DEVIR/08-URUN-KARARLARI.md`, `DENETIM.py`

**2026-09-14 · Gerçek müşteri verisi analiz edildi · CI yeşil yandı** ⚠
*(Bu satır 14 Eylül'de yazılmamıştı; `DENETIM.py`'nin "değişim günlüğü geride"
kontrolü ortaya çıkardı ve geriye dönük eklendi.)*

Bir seyahat acentesinin 3,5 aylık PDKS (48 CSV) ve vardiya planı (71 Excel)
dosyaları analiz edildi — **4.625 vardiya, 98 kişi, 105 gün**. Sonuç:
**529 kural ihlali** ve kimse fark etmemiş. 274 haftalık saat aşımı, 167
altı günden uzun ardışık çalışma, 88 kısa dinlenme. **A-14 kapandı:** ürünün
gerçek operasyonda işe yarayıp yaramayacağı artık tahmin değil, ölçüm.

**182 atama gece yarısını aşıyor** — kenar durum değil, olağan işleyiş. Müşteri
Excel'inde gece yarısını yazabilmek için `00:00` yerine **`23:59` kullanmış
(137 kez)**; içe aktarma bunu çevirmezse 1 dakikalık sistematik hata girer.

**CI yeşil yandı — A-4 kapandı.** GitHub Actions koştu, 39 test + 7 mimari
kuralı geçti. Kurallar artık öneri değil **kapı**. Pencere protokolü
kararlaştırıldı ve `00-BURADAN-BASLA.md` §5b'ye yazıldı.

**Master Spec v1.3** yazıldı (v1.2'ye dokunulmadı): gece yarısı zaman modeli
Z-1…Z-6, DST taşınabilir-pasif, lookback 14 gün, onarım döngüsü, idempotency,
**tekrarlanabilirlik garanti edilmiyor** (yerine plan kopyalama), ve **§16 test
stratejisi + 12 altın senaryo**. Köken dokümanı depoya alındı — beş "yeni
bulgu" orada zaten yazılıydı.
→ `02-spec/v1.3-master-spec.md`, `00-DEVIR/07-GERCEK-VERI-BULGULARI.md`, `07-motor/`

**2026-09-12 · Devir paketi kuruldu — ve kurulurken bir açık buldu** ⚠
Uzun sohbetlerde bağlam kaybını önlemek için projenin hafızası sohbetten
depoya taşındı: `00-DEVIR/` altında 8 dosya. Sohbet özeti değil **devir
paketi** — fark şu ki buradaki her iddia bir test adına, dosya yoluna ya da
çalıştırılabilir komuta bağlı. *Sohbet özeti yanlış bir varsayımı sessizce
taşıyabilir; test yeşil yanar ya da yanmaz.*

**Kurulurken bir açık çıktı.** `RISKLER-VE-ONLEMLER.md`, projedeki en ciddi
hatanın (süper kullanıcı RLS'i aşıyordu) bekçisi olarak bir test gösteriyordu
— **o test hiç var olmamıştı.** Doküman iki gün boyunca, en çok güvenilen
satırında yanlıştı. Bulan şey, her iddiayı bir teste bağlama kuralı oldu:
bağlanacak test yoktu.

**`M0` eklendi** — `M1`'in önünde duruyor, çünkü M1 *"RLS tanımlı mı"*, M0
*"RLS beni gerçekten durduruyor mu"* diye sorar. Rol **adına** değil,
`current_user`'ın **yetkisine** bakıyor (`rolsuper`, `rolbypassrls`); böylece
bağlantı dizesi sahibi role çevrilse de, role sonradan yetki verilse de
yakalıyor. Kanıt: `tshift` → `t/t`, `tshift_app` → `f/f`.
**39/39 yeşil.** Değişmez tablosu 39/45 → 41/45 bekçili.

**Karar: kabul ölçütü kod yazılmadan önce yazılır** ve Mustafa onaylar; test
o cümlenin çevirisi olur. Her cümle kaynağına göre `[spec]` / `[karar]` /
`[çıkarım]` diye işaretleniyor — `[çıkarım]` olanlar yapay zekânın türettiği,
onaylanmamış varsayımlar. Sebebi D6 (11 Eylül): kodu yazan testi de yazarsa
aynı yanlış varsayım iki yere birden geçebilir.

Ayrıca GPT'nin ürettiği kalite araştırması değerlendirildi (kaynakları
denetlendi: gerçek, bir künye hatası hariç). Test kapsamımız sahanın 20
senaryo sınıfına oturtuldu: **4'ünde derin, 2'sinde kısmi, 14'ünde hiç yok.**
Derinlik iyi, sorun genişlik.
→ `00-DEVIR/`, `KALITE-ARASTIRMASI-DEGERLENDIRME.md`

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
