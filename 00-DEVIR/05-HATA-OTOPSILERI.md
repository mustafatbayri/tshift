# HATA OTOPSİLERİ

Bu projede **gerçekten olmuş** hatalar. Her biri için: ne oldu, nasıl
görünüyordu, ne yakaladı, **ve bir daha sessizce geri gelmesini ne engelliyor.**

> **Bu projenin işleyiş kuralı:** Bir hata bulunduğunda düzeltmek işin
> yarısıdır. Diğer yarısı, o hatanın bir daha **sessizce** geri gelmesini
> engelleyen kalıcı bir kontrol eklemektir. Kontrolü eklenmemiş bir düzeltme
> tamamlanmamış sayılır.

Genel hata sınıfları ve savunma hatları için: `RISKLER-VE-ONLEMLER.md` §2–§3.
Burası **yaşanmış** olanların kaydı — genel doğrulardan daha öğretici.

---

## O-1 · Süper kullanıcı RLS'i aşıyordu ⚠ **en ciddi**

**Tarih:** 10 Eylül 2026

**Ne oldu:** Satır seviyesi güvenlik (RLS) doğru yazılmıştı, açılmıştı ve
veritabanında `t/t` diye doğrulanmıştı. Ama uygulama veritabanına Docker'ın
**süper kullanıcısıyla** (`tshift`) bağlanıyordu. PostgreSQL'de süper
kullanıcı RLS'i **tamamen** aşar — `FORCE` bile durduramaz.

**Nasıl görünüyordu:** Hiçbir hata yok. Kod derleniyor, uygulama çalışıyor,
"RLS açık mı" sorgusu `t` dönüyor. **Güvenlik kâğıt üstünde vardı, çalışmada
yoktu.**

**Ne yakaladı:** İnceleme değil, **testin kendisi** — iki firma kurup
"birbirini görüyor mu" diye sorunca görüldü.

**Düzeltme:** İki rol. `tshift` migration çalıştırır, `tshift_app` uygulamayı
taşır (`NOSUPERUSER`, `NOBYPASSRLS`).
→ `04-kod/db/rls/02-uygulama-rolu.sql`

**Kalıcı bekçi:** `M0 - Baglanan rol super kullanici degil (RLS gercekten
yururlukte)` — **12 Eylül 2026'da eklendi.**

> **Bu bekçinin kendi hikâyesi var.** 10 Eylül'de eklendiği kaydedilmişti ve
> `RISKLER-VE-ONLEMLER.md` onu bekçi olarak gösteriyordu — **ama test hiç var
> olmamıştı.** Bu, 12 Eylül'de devir paketi hazırlanırken, dokümandaki her
> iddia bir test adına bağlanmaya çalışılınca ortaya çıktı: bağlanacak test
> yoktu.
>
> Yani projedeki en ciddi hatanın bekçisi iki gün boyunca **yalnızca kâğıt
> üstünde** vardı — tam da hatanın kendisi gibi. Bu, `RISKLER-VE-ONLEMLER.md`
> §2'deki 9 numaralı hata sınıfının ("gerekçenin kaybolması") doküman
> üzerinde gerçekleşmiş hâlidir.

**Testin tasarımı:** Rol **adına** bakmaz, `current_user`'ın **yetkisine**
bakar (`pg_roles.rolsuper`, `rolbypassrls`). Böylece bağlantı dizesi sahibi
role çevrilirse de, `tshift_app` rolüne sonradan yetki verilirse de yakalar.

**Kırmızı kanıt (12 Eylül):**

```
  rolname   | rolsuper | rolbypassrls
------------+----------+--------------
 tshift     | t        | t
 tshift_app | f        | f
```

Uygulama `tshift` ile bağlansaydı M0 **iki ayrı iddiadan birden** kırılırdı.

### Çıkarılan genel ders

> **"Koruma tanımlı mı" yanlış sorudur. Doğru soru: "koruma şu anda beni
> durduruyor mu?"**
>
> Her koruma için, korumanın **yürürlükte olduğunu** kanıtlayan ayrı bir
> kontrol gerekir.

Bu ders sahanın standart kalite listelerinde **yok**. Oradaki risk
taksonomilerinde "güvenliği örtük varsayma" maddesi var ama **"koruma tanımlı
ama etkisiz"** diye bir satır yok. Bu bize ait bir bulgu.

---

## O-2 · JWT `sub` talebi sessizce yeniden adlandırılıyordu ⚠

**Tarih:** 10 Eylül 2026
**Yılmaz'ın tarif ettiği "bağlam kopması" sınıfının tam örneği.**

**Ne oldu:** `JwtBearer`, gelen jetonun `sub` talebini eski WS-Federation
şemasına çeviriyor. Kod `sub` diye aradığı için kullanıcı kimliği `null`
geliyor ve uç "yetkisiz" diyordu.

**Nasıl görünüyordu:** **21 test yeşilken bütün korumalı uçlar 401
dönüyordu.** Yetki mantığı doğruydu, kimlik mantığı doğruydu — kırılan yer
**ikisinin buluştuğu sınırdı.**

**Ne yakaladı:** Testler **kaçırdı**. Yakalayan şey uçtan uca kanıt betiği
oldu — çünkü testlerin hepsi servisleri doğrudan çağırıyor, HTTP katmanından
geçmiyordu.

**Düzeltme:** `MapInboundClaims = false`

**Kalıcı bekçi:** `HttpSinirTestleri` sınıfı — uygulamayı bellek içinde ayağa
kaldırıp **gerçek HTTP isteği** atar. Özellikle `H1 - Jetonla /me calisir ve
dogru kullaniciyi doner`.

### Çıkarılan genel ders

> **Birim testi katmanın İÇİNİ, uçtan uca test katmanların ARASINI doğrular.
> Biri diğerinin yerine geçmez.**

Yılmaz'ın itirazına verilecek cevap "daha iyi bir yapay zekâ" değil,
**katman aralarını sınayan bir test katmanıdır.**

---

## O-3 · D6 testinin iddiası yanlış kurulmuştu

**Tarih:** 11 Eylül 2026
**Bu, "kodu yazan testi de yazıyor" riskinin gerçekleşmiş hali.**

**Ne oldu:** *"B kiracısı hiçbir denetim kaydı görmemeli"* diye yazılmıştı.
Yanlış bir iddia — B kendi işlemlerinin kaydını **görmeli**. Sınanmak istenen
şey *"B, **A'nın** kayıtlarını göremez"* idi.

**Nasıl görünüyordu:** Test kırmızı yandı. İlk tepki "kod bozuk" oldu.
**Kod doğruydu, test yanlıştı.**

**Düzeltme:** İddia **zayıflatılmadı**, gerçekte sınanan şeye çevrildi ve
kimlik karşılaştırmasıyla **daha keskin** hale getirildi. Kod değişmedi.

**Kalıcı bekçi:** Kod değil, bir **kural**:

> Kırılan bir test, kodu doğru sanıp iddiayı zayıflatarak düzeltilmez.
> Tek istisna: iddianın, sınanmak istenen şeyi yanlış ifade ettiği durum.
> O zaman iddia **düzeltilir** — ve düzeltilmiş hali eskisinden **daha
> keskin** olmalıdır.
>
> **Ayrım şu soruyla yapılır:** *"Bu değişiklikten sonra test, eskiden
> yakalayacağı bir hatayı kaçırır mı?"* Cevap evetse, yapılan şey düzeltme
> değil **örtbastır.**

### Neden bu en öğretici hata

Bu sefer şanslıydık: yanlış varsayım yalnız **teste** yazılmıştı, koda
yazılmamıştı. Bu yüzden test kırmızı yandı ve yakalandı.

**Eğer aynı yanlış varsayım hem koda hem teste yazılsaydı, test yeşil yanardı
ve hiçbir şey fark edilmezdi.**

Bu yüzden 12 Eylül'de şu kural konuldu: **kabul ölçütü, kod yazılmadan önce,
Türkçe, Mustafa tarafından onaylanır.** Test o cümlenin çevirisi olur —
yapay zekânın varsayımının değil.

---

## O-4 · Docker bağlamına Windows `bin/`/`obj/` giriyordu

**Tarih:** 11 Eylül 2026

**Ne oldu:** Windows'ta derlenmiş `bin/` ve `obj/` klasörleri (75 MB) Docker
imajına kopyalanıp kutu içindeki restore'u eziyordu. Hata: `NETSDK1064`.

**Nasıl görünüyordu:** Yerelde her şey çalışıyor, kutuda derleme patlıyor.
Hata mesajı sebebi göstermiyordu.

**Düzeltme:** `04-kod/.dockerignore`

**Kalıcı bekçi:** `.dockerignore` dosyasının kendisi.

---

## O-5 · PowerShell 5.1 / UTF-8 tuzağı

**Tarih:** 10 Eylül 2026

**Ne oldu:** İki ayrı sorun aynı anda. (a) `-SkipHttpErrorCheck` parametresi
yalnız PowerShell 7'de var, makinede **Windows PowerShell 5.1** kurulu.
(b) 5.1 `.ps1` dosyalarını **ANSI** okuyor; UTF-8 Türkçe karakterler
ayrıştırıcıyı bozuyordu.

**Kalıcı kural:** Bütün `.ps1` dosyaları **saf ASCII** ve **PowerShell 5.1
uyumlu** yazılır. → `00-BURADAN-BASLA.md` §7

---

## O-6 · `dotnet test` sırasında DLL kilidi

**Tarih:** 11 Eylül 2026 (üç kez tekrarladı)

**Ne oldu:** API çalışırken `dotnet test` çağrılınca DLL kilitli kalıyor,
derleme `MSB3026`/`MSB3027` ile patlıyordu.

**Düzeltme ve kalıcı bekçi:** `04-kod/TEST.ps1` — testten önce API'yi
durduruyor. **Doğrudan `dotnet test` çağrılmaz.**

---

## O-7 · M4 testi kendi doküman satırını hata sanıyordu

**Tarih:** 10 Eylül 2026

**Ne oldu:** "Kültüre bağımlı `ToLower()` kullanma" testi, kendi açıklama
yorumundaki örnek metni gerçek kullanım sanıp kırmızı yandı.

**Düzeltme:** Yorum satırları atlanıyor.

### Çıkarılan genel ders

> **Yanlış alarm veren bir kontrol, bir süre sonra ciddiye alınmayan bir
> kontrole dönüşür.** Gereksiz uyaran bir kapı, olmayan kapıdan daha kötüdür
> — çünkü var sanırsın.

Bu ders de sahanın standart kalite listelerinde **yok**. Kapı kurmayı uzun
uzun anlatan kaynaklar **kapı bakımını** hiç konuşmuyor.

---

## O-8 · EF Core sürüm uyuşmazlığı ve analizör uyarıları

**Tarih:** 10 Eylül 2026

**Ne oldu:** EF paket sürümleri birbiriyle uyuşmuyordu; ayrıca EF1002/EF1003
analizör uyarıları çıktı.

**Düzeltme:** Sürümler sabitlendi. EF1003 için **dar kapsamlı** bir
`#pragma warning disable` ve yanına **yazılı gerekçe**.

**Kalıcı bekçi:** Sabitlenmiş paket sürümleri. *(Merkezî paket yönetimi —
`Directory.Packages.props` — henüz yapılmadı, açık madde.)*

---

## O-9 · Gönderilmeyen dosya, iki tarafta da "temiz" görünüyordu ⚠

**Tarih:** 16 Eylül 2026

**Ne oldu.** Doğrulayıcıdaki `KILIT_UYUMU` düzeltmesi ve onun 4 testi
Claude'un çalışma alanında vardı, **Mustafa'nın makinesine hiç
gönderilmemişti**. Commit listesi *"hangi dosyaları değiştirdiğimi
hatırlıyorum"* yöntemiyle çıkarılmıştı; `kurallar.py` "zaten commit
edilmişti" diye atlanmıştı.

**Neden hiçbir yerde kırmızı yanmadı:**

| Nerede | Ne görünüyordu | Neden yanıltıcı |
|---|---|---|
| Mustafa'nın makinesi | `git status` **temiz**, `DENETIM.py` *"commit bekleyen dosya: 0"* | Eski dosya zaten commit'liydi. Git, **var olmayan** bir değişikliği bildiremez |
| Claude'un tarafı | Testler **yeşil** | Onun kopyasında dosya doğruydu |

İki taraf da kendi içinde tutarlıydı. Tutarsızlık **aralarındaydı** ve
aradaki farka bakan hiçbir kontrol yoktu.

**Nasıl ortaya çıktı.** `orkestra.py` yazılınca `/solve` ilk kez bağımsız
doğrulayıcıyı çağırmaya başladı. Eski `KILIT_UYUMU`, A06'nın
`{calisan, gun, tip: "yasak"}` biçimindeki kilidinde `KeyError: 'bas'`
veriyordu — bu yüzden A06 Mustafa'da kırmızı, Claude'da yeşildi. İkinci
ipucu test sayısıydı: **53 yerine 57**; eksik dördü tam olarak o kilit
biçimini sınayan testlerdi.

**Düzeltme:** İki dosya gönderildi, boyutları **birebir doğrulandı**.

### Kalıcı bekçi

> **Commit öncesi dosyalar karşı taraftan çekilip içerikçe karşılaştırılır.**
> Hafızaya değil, `cmp`'ye güvenilir. Bu seferki fark da öyle bulundu.

### D-1 zincirine eklenen halka

Zincir şuydu: **yazdım ≠ gönderdim ≠ commit ettim ≠ karşı tarafta değişti.**
Şimdi bir halka daha var:

> **≠ göndermem gerektiğini fark ettim.**

Önceki halkalar *"gönderdim ama gitmedi"* hatalarıydı — ölçülebilir, çünkü
bir gönderme denemesi var. Bu ise *"göndermeyi hiç denemedim"*: ortada
başarısız bir işlem bile yok, dolayısıyla loglanacak bir şey de yok.

Aynı aile: boyut eşitliği içerik eşitliği demek değil (15 Eylül, `v2`→`v5`
17 bayat atıf, dosya boyutları **birebir aynıydı**). Her ikisinde de hata,
*doğru sinyale bakıp yanlış sonuç çıkarmaktı*.

### Çıkarılan genel ders

> **İki sistem ayrı ayrı "temiz" olabilir ve yine de birbirinden farklı
> olabilir.** Her iki tarafın kendi içindeki tutarlılığını ölçen kontroller,
> aradaki farkı **tanım gereği** göremez. Fark ancak karşılaştırılırsa
> görülür.

Bu, O-1 ile aynı sınıftan: *hiçbir şey kırmızı yanmadı.* Gürültülü hata
ucuzdur; sessiz olan pahalıdır.

---

## O-10 · "Doğrulayamam" dedim; denememiştim ⚠

**Tarih:** 16 Eylül 2026

**Ne oldu.** Dış incelemenin üçüncü turunda üç bulgu `04-kod/` tarafındaydı
(T-34, T-35, T-36). Cevabımda *"bu üçünü doğrulayamıyorum"* dedim ve
gerekçesini de yazdım: o dosyalar bende yok.

**Doğru değildi.** Mustafa'nın makinesine açılan köprü **bütün gün
elimdeydi** ve o gün onunla defalarca dosya okumuştum. `04-kod/` dosyalarını
**hiç istememiştim.** Mustafa itiraz etti — *"neden doğrulayamıyorsun, GPT
nasıl doğruluyor"* — dosyaları çektim ve **üçü de doğru çıktı.**

**Neden hiçbir yerde kırmızı yanmadı.** Çünkü kendi cümlem, kendi
davranışımın denetimiydi. Denemediğim bir şeyin başarısızlık kaydı yoktur;
ortada log da, hata da, eksik dosya uyarısı da yok. Tek kanıt, olmayan bir
tool çağrısı.

| | O-9 | O-10 |
|---|---|---|
| Ne atlandı | Gönderme | **Bakma** |
| Görünen kanıt | `git status` temiz | *"erişimim yok"* cümlesi |
| Gerçek | Dosya gitmemişti | **Erişim vardı, denenmemişti** |

**Bu T-18'in bende çalışan hâli.** T-18'de motor *"bu kuralı kontrol
edemedim"* ile *"yayınlanabilir"* diyor. Burada ben *"doğrulayamadım"* ile
*"bulgu kaydedildi"* dedim. İkisinde de **bilinmeyen, olumsuz cevapla
karıştırıldı** — kontrol edilmemiş bir şey, kontrol edilmiş gibi raporlandı.

### Kalıcı bekçi

> **"Erişimim yok" demeden önce erişim denenir.** Denenmemiş bir erişimin
> raporu, bulgu değil tahmindir; ve tahmin kaydedilirken bulgu gibi görünür.

Bu, D-1 zincirinin beşinci halkasıyla aynı aileden: *"göndermem gerektiğini
fark ettim."* İkisinde de eksik olan **işlem** değil, **işlemi yapma
fikri**.

---

## O-11 · Yorumda yazılmış, ölçülmemiş güvenlik iddiası ⚠

**Tarih:** 23 Eylül 2026

**Ne oldu.** T-35'in düzeltmesinde `X-Forwarded-For` başlığına güvenilecek
adresler `172.16.0.0/12` olarak verildi ve yanına şu yorum yazıldı:

> *"Host'tan (127.0.0.1) doğrudan atılan bir istek bu aralığa GİRMEZ, yani
> yayınlanmış porttan sahte başlık geçmez."*

**Yanlıştı.** Elle yapılan uçtan uca denemede ölçüldü:

```
host -> yayinlanmis port -> api kutusu  =>  ::ffff:172.18.0.1  (docker AG GECIDI)
web kutusu                              =>  172.18.0.4
```

Docker yayınlanmış portu **ağ geçidi üzerinden** geçiriyor. Ağ geçidi de
`/12`'nin içinde. Yani aralık, host'taki her şeyi güvenilir sayıyordu:
`curl` ile atılan sahte `X-Forwarded-For` **kabul edildi ve kaydedildi.**

Düzeltilen şey, korumanın kendisi olduğu için ciddiydi — hem kaba kuvvet
kilidinden kaçmaya hem denetim kaydını kirletmeye izin veriyordu.

**Neden hiçbir test yakalayamadı.**

| | |
|---|---|
| `IP2` ne sınıyor | *"Güvenilmeyen kaynaktan gelen başlık yok sayılır"* |
| `IP2` doğru mu | **Evet.** Kod doğru, test doğru, ikisi de çalışıyor |
| Yanlış olan ne | **Yapılandırma** — hangi kaynağın "güvenilen" sayıldığı |
| Test bunu neden göremez | Test sunucusunda liste boş; üretimdeki listeyle hiç karşılaşmıyor |

> **Birim testi mantığı doğrular, topolojiyi doğrulayamaz.**

**Neyin yakaladığı.** Elle yapılan uçtan uca deneme — ve o adım plana
*"nice-to-have"* diye kondu, sonra zorunlu yapıldı. Yapılmasaydı T-35
"kapandı" diye kaydedilecek, sahte IP koruması çalışmıyor olacaktı.

### Neden bu, koddaki bir hatadan tehlikeli

Yanlış olan yalnız değer değildi; yanına **onu doğru gösteren bir gerekçe**
yazılmıştı. Sonraki okuyan o yorumu görür ve kontrol etmez — yorumun işi
zaten kontrolü gereksiz kılmaktır.

> **Kalıcı bekçi:** bir yorum *"şu saldırı geçmez"* diyorsa, o cümle bir
> **iddiadır** ve kaydedilmeden önce **ölçülür**. Ölçülmemiş bir güvenlik
> yorumu, hiç yorum olmamasından kötüdür.

Bu, O-10'un ikizi. O-10'da *"erişimim yok"* denip denenmemişti; burada
*"bu saldırı geçmez"* denip denenmedi. İkisinde de eksik olan **işlem**
değil, **işlemi yapma fikri**.

### Sınıfa eklediği yeni şey

O-1'den O-9'a kadar hatalar **kodun** ya da **deponun** durumuydu; bekçi
yazılabildi. O-10 bir **cevabın** durumuydu. O-11 bir **yapılandırmanın**
durumu — ve yapılandırma, kodla birlikte test edilmediği sürece görünmez.

Bu yüzden T-35'in kapanış kaydına iki elle ölçüm **koşturulacak adım**
olarak yazıldı: topoloji değişirse ikisi de yeniden koşar.

---

## O-12 · Yeşil test, şans eseri yeşildi: "süre yetmedi" bir yarıştı ⚠

**Tarih:** 1 Ekim 2026, 19:05

**Ne oldu.** Beş kararın push'undan sonra GitHub'daki motor işi kırmızı
yandı: `test_sure_yetmedi.py`'nin dört testi *"'sure_yetmedi' beklenirdi:
'cozuldu'"* dedi. Aynı dosya konteynerde ve Mustafa'nın makinesinde
yeşildi; 29 Eylül'den beri CI'da da yeşildi.

**Neden.** Testler *"60 kişilik sahne + 0,1 saniyelik bütçe"* kurup
çözücünün yetişememesini **bekliyordu**. Ama `coz` ana aramaya en az
1 saniye verir (T-59 tabanı) ve bu sahnede ilk plan konteynerde 1,9
saniyede bulunuyor. GitHub'ın makinesi o gün 1 saniyenin altında buldu.
Test, makinenin yavaş olmasına güveniyordu — dosyanın kendi başındaki
uyarının (*"süre ölçerek değil yapıyı sınayarak"*) tam tersi. Yazan
bendim; uyarıyı yazıp uymamışım.

**Sınıfı.** O-1 ve O-9'un ailesi değil (kontrol yanlış şeye bakmıyordu);
yeni bir sınıf: **kontrol doğru şeye bakıyor ama sonucu bir yarış
belirliyor.** Böyle bir test kırmızı yandığında "motor bozuldu" sanılır,
yeşil yandığında güven verir — ikisi de yanlıştır.

**Düzeltme.** Dolan bütçe artık enjekte ediliyor: `sure_dolmus` fikstürü
CP-SAT'e aramadan `UNKNOWN` dedirtiyor (gerçek çözücünün bütçe dolunca
döndürdüğü şeyin aynısı). Sınanan şey mekanizma; makine hızı testin
dışında. Testlerin hâlâ ısırdığı 5 mutasyonla kanıtlandı. Motor kodu
değişmedi.

### Kalıcı bekçi

Mutasyon grubu `sure_yetmedi` (5 bozma); ve bir kural: **testte "zaman
yetmedi" durumu hiçbir zaman gerçek saatle kurulmaz** — sonuç enjekte
edilir ya da sahne kanıtlanabilir biçimde çözümsüz yapılır. Aynı aile
tarandı: `test_sure_butcesi.py` süreyi ölçmüyor, yapıyı sınıyor.

---

## O-13 · Aktarılan dosya makinede boşaldı; doğrulamam önbelleğe bakıyordu ⚠

**Tarih:** 2 Ekim 2026, 17:49 (bulgu 17:5x, Mustafa'nın koşusuyla)

**Ne oldu.** Konteynerden Mustafa'nın makinesine 11 dosya aktarıldı (15:03);
aktarımdan hemen sonra md5 doğrulaması yaptım, on biri de doğruydu.
17:49:36'da `09-motor/cozucu/coz.py` Windows tarafında **0 bayt** oldu —
aktarım listesinin ilk dosyası, ötekiler sağlam. Mustafa blok 1'i koşunca
28 test dosyası *"cannot import name 'coz'"* ile daha toplanırken çöktü.

**Neden.** Kesin sebep bilinmiyor. Aradaki saatlerde makineyle bağlantı
(köprü) iki kez kopup yeniden kuruldu; en güçlü şüphe, yeniden bağlanırken
köprünün bekleyen bir yazımı boş tamponla kapatması. Benim doğrulamam ise
köprünün Linux tarafındaki **görünümünü** okuyordu — o görünüm aktarımın
önbelleğini gösterir, Windows'taki gerçek dosyayı değil. O-9 ile aynı
sınıf: **kontrol vardı ama yanlış şeye bakıyordu** (iki taraf da aynı
önbellekti).

**Düzeltme.** Dosya yeniden yazıldı (35.193 bayt). Doğrulama bu kez
Windows tarafından **geri okunarak** yapıldı: sekiz kod dosyası
`device_stage_files` ile makineden çekilip konteynerdeki kopyayla md5
karşılaştırıldı — sekizi de aynı. Blok 1 ikinci denemede yeşil (531 test,
11 mutasyon öldü, taban testleri 7).

### Kalıcı bekçi

Kural (otomatik bekçisi yok, O-10 gibi): **aktarımdan sonra doğrulama
Windows tarafından geri okuyarak yapılır, Linux görünümünden değil; köprü
koptuysa son aktarılan dosyalar yeniden doğrulanır.** Ve Mustafa'nın
makinesindeki test koşusu, aktarımın gerçek kapısıdır — nitekim yakalayan o
oldu.

---

## O-14 · "Yalnız bakıyorum" dediğim git komutu depoda kilit bıraktı ⚠

**Tarih:** 2 Ekim 2026, 18:57 (yeni pencerenin ilk dakikaları)

**Ne oldu.** Açılış beyanı için depo durumuna `git status` ile baktım —
okuma komutu saydığım için. Git, `status` sırasında indeksi tazeler ve bunun
için `.git/index.lock` oluşturur; Mustafa'nın makinesine bağlı kabukta dosya
**silme izni yok**, kilit silinemedi ve 0 baytlık dosya orada kaldı. Depo
sağlamdı ama bir sonraki `git add` / `git commit` *"index.lock: File exists"*
ile duracaktı. Mustafa elle sildi.

**Neden.** *"Okuma komutu"* ile *"hiçbir şey yazmayan komut"* aynı şey
değil; `git status`, `git diff` ve benzerleri indeksi yazabilir. Silme izni
olmayan bir kabukta, arkasını toplayamayacağım geçici dosya üreten her komut
iz bırakır.

### Kalıcı bekçi

Kural (otomatik bekçisi yok): **bu kabuktan git yalnız `GIT_OPTIONAL_LOCKS=0`
ile çağrılır** (`export GIT_OPTIONAL_LOCKS=0`); o ayarla `status`, `diff`,
`log` kilit açmaz — 2 Ekim'de `status` ve `diff` bu ayarla koşulup ardından
`.git/index.lock` arandı, oluşmadı. `git add`,
`commit`, `push` bu kabuktan **yapılmaz**; commit bloğu Mustafa'ya verilir.
`DENETIM.py` de git çağırdığı için aynı ayarla koşulur.

---

## O-15 · "214 mutasyon hepsi öldü" denmişti; tam koşu iki gün yapılmamıştı, 1 yaşadı 3 atlandı ⚠

**Tarih:** 3 Ekim 2026, 15:22 (Mustafa'nın tam koşusuyla)

**Ne oldu.** Mustafa `py mutasyon_kostur.py`'yi **tam** koşturdu: 214 mutasyon,
**1 yaşadı, 3 atlandı**. Devir dokümanları 1–2 Ekim boyunca *"201 mutasyon
hepsi öldü"*, *"214 mutasyon"* yazıyordu; o sayılar **grup koşularından**
toplanmıştı (`py mutasyon_kostur.py demir` gibi). Son tam koşu 1 Ekim 15:35'ti
(128 mutasyon); sonraki dokuz karar (K-49…K-57) grup koşusuyla doğrulandı.

| Ne | Sebep | Neden görünmedi |
|---|---|---|
| **Yaşadı:** çözücü, günü 0 ve üstü olan "geçmiş" kaydını da geçmiş saysın | K-56 (2 Ekim 00:50, devreden kapsama) geçmiş kayıtları **kapsamaya da** sayar oldu. Mutasyonlu kodda gün-0 kaydı hem o günkü vardiyayı yasaklıyor hem talebi "devreden kişi" olarak kapatıyor → **boş plan "çözüldü"** çıkıyor. Test yalnız `durum == "cozuldu"` diyordu, planın dolu olduğuna bakmıyordu | Mutasyon 30 Eylül'de yazıldı ve o gün öldü; K-56 davranışı değiştirdi, `gecmis` grubu K-56'dan sonra koşulmadı |
| **Atlandı:** doğrulayıcı, gün-0 kaydı geçmiş sayılsın | K-56 doğrulayıcıya aynı satırı taşıyan ikinci bir okuyucu ekledi (`devir_atamalari`); çapa iki yerde geçti | aynı |
| **Atlandı (2):** K-50 doğrulayıcı sayımı (tek mod / hepsi modu) | K-56 `ekibe_sayilir`'a `_devir_elle` koşulu ekledi; çapa metni değişti | `cok_ekipli` grubu K-56'dan sonra koşulmadı |

**Neden.** İki şey birden: (1) *"hepsi öldü"* toplamı tam koşudan değil grup
koşularından **toplanarak** yazıldı — toplam sayı bir ölçüm değil bir **toplama
işlemiydi**; (2) bir özellik (K-56) komşu grupların çapalarını ve bir testin
varsayımını değiştirdi; grup koşusu kendi grubunu görür, komşuyu görmez. Sınıf
O-9/O-12 ile aynı: *"kontrol vardı ama yanlış şeye bakıyordu"* — grup
koşusu bakıyordu, tam koşu bakmıyordu.

**Düzeltme (3 Ekim, bulut makinesinde doğrulandı; Mustafa'nın makinesinde
koşulacak).** Test güçlendirildi: gün-0 kaydıyla çözülen plan **dolu** olmalı
(`[("C1", 0)]`) ve kayıt devreden kapsamaya **sayılmamalı**; doğrulayıcı için
yeni test: gün-0 kaydı asgari kapsamayı kapatmaz, gün −1'in 23–07 kaydı
yalnız taşan saatleri kapatır. Üç çapa yeni metne çekildi; K-56 okuyucusuna
ayrı mutasyon kondu (**toplam 215**). `gecmis` 17/17 ve `cok_ekipli` 11/11
öldü (bulut).

### Kalıcı bekçi

- **Toplam iddiası yalnız tam koşudan yazılır.** Grup koşusu yalnız grubun
  sayısını söyler; betik grup koşusunda bunu çıktıya yazar. Tam koşu
  `09-motor/mutasyon-tam-kosu.txt` damgasını yazar (tarih, özet) — *"en son ne
  zaman tam koşuldu"* sohbete değil depoya bağlı.
- **Çözücü ya da doğrulayıcı değiştiyse commit öncesi tam koşu** (Mustafa'nın
  makinesinde ≈12 dk). Grup koşusu geliştirme sırasında, tam koşu commit
  kapısında.
- ⚠ Otomatik bekçisi henüz yok: `DENETIM.py`'ye *"damga, çözücü/doğrulayıcı
  dosyalarının son değişikliğinden eskiyse uyar"* kontrolü eklenebilir —
  `DENETIM.py` her şeyin bekçisi olduğu için **Mustafa'nın onayıyla** (T-41
  emsali).

---

## O-16 · Motor *"optimum, uzaklık %0"* dedi; kanıtladığı yalnız mola yerleşimiydi — aynı girdide 4–5,6 kat iyi plan vardı ⚠

**Tarih:** 6 Ekim 2026 (üç profil ölçümü okunurken; hata 4 Ekim'de K-60 ile girdi)

**Ne oldu.** K-60 ile ana aşama *mola adımı* oldu: atamalar birinci aşamanın
planına sabitlenir, yalnız molaların yeri aranır, çözücü o **kısıtlı**
problemin optimumunu kanıtlayınca durur. Çıktı bunu genel alanlara yazıyordu:
`durma_sebebi: "optimum"`, `alt_sinir == amac_degeri`,
`metrikler.optimuma_uzaklik_yuzde: 0.0`. 5–6 Ekim'in 15 tam ölçek koşusunun
hepsi böyle bitti. K-35'in sonuç kartı tam bu alanlardan beslenir (*"Bu plan
teorik en iyisinin %X'i kadar iyi — tahmin değil, garantidir"*): kart yazılmış
olsaydı her planda *"%100"* gösterecekti.

Ölçüm (T-60 bulgu 20): *"optimum · %0"* denen DENGELI planları 105.742–148.431
puan; aynı girdide **26.589**'luk plan var (CALISAN profilinin fazla mesaisiz
planı, DENGELI ağırlıklarıyla). Tam modelin 2 Ekim'de kanıtladığı gerçek sınır
21.098.

**Neden.** (1) Çözücünün alt sınırı **çözdüğü modelin** sınırıdır; modeli
daralttığımda (alan sabitleme) sınırın anlamı da daraldı, alanın adı aynı
kaldı. (2) Bunu 4 Ekim'de doğru davranış sandım ve **teste yazdım**
(*"amaç = alt sınır: kanıtlı optimum"*), şartnameye de (`durma_sebebi:
optimum`). Yani bekçi hatayı koruyordu. (3) Bulgu 18'de *"kanıtlı optimum"*
derken kastedilen mola yerleşimiydi ve orada doğruydu; aynı kelime ürünün
genel alanına taşınınca başka bir iddia oldu. Sınıf O-9 · O-12 · O-15 ile
aynı — kontrol vardı, yanlış şeye bakıyordu; burada kontrolü yanlış şeye
**ben baktırdım**.

**Nasıl fark edildi.** Testle değil; üç profil yan yana gelince. CALISAN'ın
amacı (34 bin) DENGELI'ninkinden (106–148 bin) çok küçüktü. Profil yalnız
ağırlıkları ve fazla mesai tavanını değiştirdiği için CALISAN planı DENGELI
için de geçerliydi; DENGELI ağırlıklarıyla yeniden fiyatlanınca 26,6 bin
çıktı. *"Optimum"* denen bir planın dört kat iyisi olamaz.

**Düzeltme (6 Ekim).** Mola adımı koştuysa (`atamalar_sabit: true`):
`alt_sinir` ve `optimuma_uzaklik_yuzde` **null** (küresel kanıt yok — sıfır ya
da kısıtlı sınır yazmak yalan garanti olurdu), adımın sınırı
`mola_adimi_alt_sinir`, sebep `mola_adimi_optimum` / `mola_adimi_hedef_bosluk`.
Tam modeli çözen yollarda (küçük model, başlangıç planı, `mola_adimi: False`)
alanlar eskisi gibi — kanıt varken susmak da yanlış olurdu. Testler: yanlış
iddiayı taşıyan üç test düzeltildi; iki yeni test — biri birinci aşamaya
**bilerek kötü** plan verir (*mola adımı "optimum" der, plan tam modelin
kanıtlı optimumundan kötüdür, çıktı küresel sınır yazmaz*), öteki ön ekin
yalnız kanıt iddia eden sebeplere ve yalnız mola adımında yazıldığını sınar.
`kalite-olc.py` aynı ayrımı ekrana ve dosyaya yazar.

⚠ **Aynı sınıf aynı gün ikinci kez çıktı — ve onu ben değil bağımsız inceleme
buldu.** Düzeltmeyi yazarken yalnız *"atamalar sabit mi"* diye baktım. Aynı
gün yazdığım ölçüm seçeneğinde (*önce fazla mesaisiz*) fazla mesai
değişkenleri 0'a sabit kalıyor: ana aşama ortak arama olsa bile çözdüğü model
tam model değil, ama sınırı yine küresel alana gidiyordu; ölçüm seçeneği
(b)'nin kollarında da öyle. İşi görmemiş ayrı bir oturuma dosyalar okutuldu;
ilk bulgusu buydu. Kural genelleştirildi: soru *"atamalar sabit mi"* değil
*"ana aşamanın çözdüğü model **tam model mi**"* (`_sinir_kapsami`: değilse
kısıtın adı — `mola_adimi` ya da `fazla_mesaisiz` — sınırın ve sebebin
adına girer). Toplam 5 yeni test, 14 mutasyon (`demir`), 4 mutasyon
(`fm_sifir`).

⚠ **Düzeltmenin kapatmadığı.** Büyük modelde artık **hiç** küresel sınır yok;
K-35'in kartı için tam modelde ayrı bir sınır adımı gerekir (T-60'ta ölçüm
olarak yazılı). 4–6 Ekim arasında yazılmış ölçüm dosyalarındaki
(`kalite-olcumu-95-kalibrasyon-600.json`, `kalite-olcumu-95-profiller-900.json`)
`alt_sinir` ve `optimuma_uzaklik_yuzde` eski anlamdadır: mola adımının sınırı.

### Kalıcı bekçi

- **Bir sınır ya da kanıt alanı, hangi modelin sınırı olduğunu adında taşır.**
  Model daraltılıyorsa (alan sabitleme, ipucu kilidi) sonucu genel alana
  yazılmaz. Sorulacak soru tek tek kısıtlar değil: *"çözülen model tam model
  mi?"* Modele yeni bir daraltma eklenince `_sinir_kapsami`ne de eklenir.
- **Kendi düzeltmemi kendim onaylamam.** Bir hata sınıfını düzelttikten sonra
  aynı sınıfın başka örneğini aramak için dosyalar işi görmemiş bir oturuma
  okutulur (O-10'un kuralı; burada işe yaradı).
- **Ucuz çapraz kontrol:** aynı girdinin daha kısıtlı bir çözümü (burada:
  tavanı sert olan profil) aynı ağırlıklarla yeniden fiyatlanır; daha iyi
  çıkıyorsa *"optimum"* yanlıştır. `kalite-olc.py` fazla mesai dışı amacı ayrı
  yazar; üç profil ölçümü bu kontrolün kendisidir.
- Testler: adında `O16` geçen beş test (`09-motor/testler/test_demir_secenekleri.py`)
  ve `test_fazla_mesaisiz_ORTAK_arama_da_KISITLIDIR_kuresel_sinir_YAZILMAZ`
  (`09-motor/testler/test_fazla_mesai_once_sifir.py`); mutasyon grupları `demir`,
  `fm_sifir`.

---

## Özet: hata → bekçi tablosu

| # | Hata | Kalıcı bekçi | Durum |
|---|---|---|---|
| O-1 | Süper kullanıcı RLS'i aşıyordu | `M0 - Baglanan rol super kullanici degil (RLS gercekten yururlukte)` | ✅ *(12 Eylül'de eklendi; iki gün boyunca yalnız kâğıt üstündeydi)* |
| O-2 | JWT `sub` yeniden adlandırılıyordu | `HttpSinirTestleri` (özellikle H1) | ✅ |
| O-3 | D6 iddiası yanlış kurulmuştu | Kırmızı çizgi kuralı + kabul ölçütü önce | ✅ |
| O-4 | Docker bağlamı şişiyordu | `04-kod/.dockerignore` | ✅ |
| O-5 | PowerShell 5.1 / UTF-8 | Saf ASCII + PS5.1 kuralı | ✅ |
| O-6 | `dotnet test` DLL kilidi | `TEST.ps1` | ✅ |
| O-7 | M4 yanlış alarm veriyordu | Yorum satırları atlanıyor | ✅ |
| O-8 | EF sürüm uyuşmazlığı | Sabitlenmiş paket sürümleri | 🟡 Kısmi |
| O-9 | Gönderilmeyen dosya iki tarafta da temiz görünüyordu | Commit öncesi içerik karşılaştırması (`cmp`), hafıza değil | ✅ |
| O-10 | *"Doğrulayamam"* denildi, denenmemişti | "Erişimim yok" demeden önce erişimi dene | ✅ *(kural; otomatik bekçisi yok)* |
| O-11 | Yorumda ölçülmemiş güvenlik iddiası; yapılandırma yanlıştı | Uçtan uca elle ölçüm, kapanış kaydına adım olarak yazılı | ✅ *(kural; birim testi göremez)* |
| O-12 | "Süre yetmedi" testi makine hızına güveniyordu; CI'da kırmızı yandı | Dolan bütçe enjekte edilir (`sure_dolmus`); mutasyon grubu `sure_yetmedi` | ✅ |
| O-13 | Aktarılan dosya makinede boşaldı; doğrulama önbelleğe bakıyordu | Windows tarafından geri okuyarak md5; köprü koptuysa yeniden doğrula; Mustafa'nın makinesindeki test koşusu asıl kapı | ✅ *(kural; otomatik bekçisi yok)* |
| O-14 | `git status` silme izni olmayan kabukta `.git/index.lock` bıraktı | Git yalnız `GIT_OPTIONAL_LOCKS=0` ile; `add`/`commit` bu kabuktan yapılmaz | ✅ *(kural; otomatik bekçisi yok)* |
| O-15 | "Hepsi öldü" toplamı grup koşularından toplanmıştı; tam koşuda 1 yaşadı 3 atlandı | Toplam yalnız tam koşudan; tam koşu damgası `mutasyon-tam-kosu.txt`; çözücü/doğrulayıcı değişince commit öncesi tam koşu | ✅ *(kural + damga; DENETIM kontrolü onay bekliyor)* |
| O-16 | Mola adımının optimumu planın optimumu diye yazıldı (*"optimum · %0"*); aynı girdide 4–5,6 kat iyi plan vardı; aynı sınıf aynı gün ölçüm seçeneğinde de çıktı | Çözülen model tam model değilse sınır genel alana yazılmaz (`_sinir_kapsami`; `mola_adimi_alt_sinir`, `fazla_mesaisiz_alt_sinir`); bilerek kötü planla uçtan uca test + 18 mutasyon; yeniden fiyatlama çapraz kontrolü; bağımsız inceleme | ✅ *(test + mutasyon; sonuç kartı için küresel sınır açık)* |

---

## Bu tablodan çıkan üç şey

**1. Yılmaz haklı çıktı — ama sonuç değiştirilebilir.**
O-2 tam olarak onun tarif ettiği hata. Fark şu ki artık kalıcı bir bekçisi
var ve aynı şekilde geri gelemez.

**2. Zaman kaybımızın çoğu yapay zekâdan değil, alet çantasından geldi.**
O-4, O-5, O-6 — üçü de ortam, sürüm ve platform farkı. Hiçbiri "yapay zekâ
gereksinimi yanlış anladı" değil. Sahanın kalite literatürü bu sınıfı hiç
görmüyor çünkü idealize edilmiş bir Linux/CI dünyası için yazılmış.

**3. En tehlikeli hata, hata gibi görünmeyendi.**
O-1'de hiçbir şey kırmızı yanmadı, hiçbir şey uyarı vermedi, doğrulama
sorgusu bile "her şey yolunda" dedi. Diğerlerinin hepsi gürültülüydü —
gürültülü hata ucuzdur.

**O-9 aynı sınıfa dördüncü bir örnek ekledi ve bir şeyi netleştirdi:** bu
sınıfın ortak özelliği *kontrolün yokluğu* değil, **kontrolün yanlış şeye
bakması**. O-1'de RLS tanımlıydı ama etkisizdi; O-9'da git temizdi ama
karşılaştırdığı iki şey de aynı taraftaydı. Her ikisinde de kapı vardı,
sadece başka bir kapıydı.

**O-10 sınıfa beşincisini ekledi ve sınırı gösterdi:** O-1'den O-9'a kadar
her hatanın bir bekçisi yazılabildi, çünkü hepsi **kodun** ya da **deponun**
durumuydu. O-10 ise bir **cevabın** durumu: *"doğrulayamadım"* cümlesini
sınayacak otomatik bir kapı yok. Bu yüzden 16 Eylül'de kayda geçen kural —
*bir iş parçası bitince şartnameden türetilmiş girdilerle başka bir modelle
inceleme* — bir öneri değil, bu sınıfın tek bekçisi.
