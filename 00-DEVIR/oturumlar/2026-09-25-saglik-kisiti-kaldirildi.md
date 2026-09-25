# 2026-09-25 · `SAGLIK_KISITI` kaldırıldı — yazılmadan önce sorulduğu için

**İş parçası:** T-38'in `kural_degerleri` satırı olarak başladı, `SAGLIK_KISITI`
kuralının yazılmasına döndü, kuralın kaldırılmasıyla bitti. **Ürün kodu
değişmedi.**

**Tetikleyen:** Mustafa açık 🔴'lar arasından T-38'i seçti.

---

## 1. Seçilen iş yanlış bir gerekçenin üstündeydi — ve gerekçeyi dün ben yazdım

23 Eylül'de T-38'e şunu yazmıştım:

> *"`calisanlar[].kural_degerleri` — Kişiye özel kural değeri yok sayılır.
> Sözleşmesi günde 9 saat diyen kişi genel kuralın 11 saatine planlanabilir —
> yasal tarafta yanlış plan."*

Kod yazmadan önce şartname okununca **yanlış olduğu** görüldü:

| İddia | Şartname ne diyor |
|---|---|
| Kişiye özel günlük sınır `kural_degerleri` ile verilir | `GUNLUK_AZAMI` kapsamı **`S`** — hiçbir kademede ezilemez (§5.2, K-18) |
| Yasal tarafta yanlış plan | Üretmiyor; o senaryonun yolu `SAGLIK_KISITI` idi (K-21) |

Üstelik §11.2'nin girdi örneği tam da bu iki `S` kapsamlı kuralı kişiye özel
değer olarak gösteriyor — şartname kendi yasakladığı şeyi örnek yapmış.
Kayıt: **T-42**.

> **Dördüncü kez bir kayıt ölçülünce değişti — ama ilk kez ters yönde.**
> T-34, T-35 ve T-19 gerçeği **eksik** söylüyordu; bu **fazla** söyledi.
> Ders *"hafife alıyorum"* değil: **ölçmeden yazıyorum**, ve bu iki yöne de
> sapıyor. Kaydı yazan da düzelten de aynı taraftı; dış inceleme değil.

---

## 2. Üç soru, ve ikincisinin cevabı kuralı gereksiz kıldı

`SAGLIK_KISITI` yazılamazdı: kabul ölçütü yok, fikstürü yok, girdi
sözleşmesinde taşıyıcı alanı yok. Üç ürün kararı soruldu — taşıyıcı biçim,
geçerlilik penceresi, belge referansı eksikse ne olacağı.

Mustafa ikinci soruya şöyle cevap verdi:

> *"Benim rapordan kastım dönemsel bir hastalık v.b. durumlar için. Örneğin
> çalışan hastalandı ve 2 günlük rapor aldı... Bir çalışan için günlük 4 saat
> çalışabilir diye bir alan v.b. bilgi tutmak istemiyorum."*

Ve ardından:

> *"Günde 4 veya max 5 saat çalışabilir diye bir sağlık raporu belki milyonda
> bir vaka olarak karşımıza çıkabilir. Ürüne eklememiz gereksiz."*

**Kural gereksizdi.** Ürünün gördüğü sağlık durumu dönemsel, ve dönemsel rapor
zaten bir izindir:

| Durum | Nerede ifade edilir |
|---|---|
| İki günlük rapor | `leaves` satırı, `tip = rapor`, `tum_gun = true` (§8.3) |
| Yarım günlük rapor | Aynı satır, `tum_gun = false` + saat aralığı |
| Motoru bağlaması | `ONAYLI_IZIN` — **yazılı ve testli** |

Plan yayınlandıktan sonra gelen rapor (*"yerine kim geçecek"*) bir kural değil;
plan editörü + `/suggest` işi.

> **Asıl ders:** *"bu kural hangi gerçek vakayı çözüyor"* sorusu **kod
> yazılmadan önce** soruldu ve kuralın kendisini eledi. Yazılsaydı katalogda
> bir SERT yasal kural, bir fikstür, bir kabul ölçütü ve bir taşıyıcı alan
> birikecekti — hepsi hiçbir vakayı çözmeden. Maliyet üç soruya indi.

---

## 3. Kaldırmanın kapsamı — ölçüldü

İlk tahmin "bir katalog satırı"ydı. `grep` **26 yer / 8 dosya** buldu.

| Dosya | Dokunulan |
|---|---|
| `02-spec/v1.4-master-spec.md` | 8 yer: §1 değişiklik tablosu · §5.2 · §6 kural sayısı · §6.1 katalog satırı **ve** bölümü · §6.2 · §6.6 yasal dayanak tablosu · §8.3 · §17 sürüm notları |
| `00-DEVIR/08-URUN-KARARLARI.md` | K-21 geri alındı, **K-1 biçiminde** (üstü çizili başlık + gerekçe + özgün metin korundu) |
| `00-DEVIR/06-ACIK-RISKLER.md` | T-43 geri çekildi · T-42 sadeleşti · T-38 düzeltildi · öncelik tabloları |
| `00-DEVIR/00-BURADAN-BASLA.md` | 6 yer, çoğu kural sayısı |
| `02-spec/v1.4-hazirlik/` · `oturumlar/2026-09-16-*` | **Dokunulmadı** — dondurulmuş, o gün doğruydu |

**Katalog 35 → 34.** Tahmin edilmedi: benzersiz kural kodu programla sayıldı,
34 çıktı.

---

## 4. Bırakılan sınır — boş bırakılmadı

§5.2 şu soruyu soruyor: *"Peki 'Ayşe'nin raporu var, günde en fazla 4 saat'
nereye yazılacak?"* Cevabı `SAGLIK_KISITI` idi. Kural gidince cevap
**"hiçbir yere"** oldu ve şartnamede **öyle yazıyor**:

> *"Sistem bunu ifade edemez — bilinçli bir kapsam sınırıdır... Böyle bir
> çalışan gerçekten çıkarsa sistem onu koruyamaz; plan onu normal yasal tavana
> kadar planlar. O durum sistem dışında yönetilir."*

Bir kuralı çıkarıp yerine boşluk bırakmak, T-26'nın tersi bir hata olurdu:
kayıt siliniyor ama sonucu kayıtsız kalıyor.

---

## 5. Geriye kalan gerçek iş

**Yarım günlük izin motora hiç gelmiyor.** `tum_gun = false` ve saat aralığı
`leaves` tablosunda var; §11.2 yalnız `tum_gun` gönderiyor ve motor her
koşulda **bütün günü** kapatıyor. Yarım gün rapor alan kişi o gün hiç
planlanamıyor.

Bu, T-38'in bir satırıydı ve 23 Eylül'de ikincil görünüyordu. Mustafa'nın
*"veya yarım gün de rapor alabilir"* cümlesi onu **asıl iş** yaptı. T-38
öncelik listesinde 2. sıraya bu gerekçeyle yazıldı.

---

## 6. Bu oturumda üretilmeyenler — dürüstlük notu

- **Kod yazılmadı.** Ne motor ne test. Bu oturum tamamen şartname ve kayıt.
- **Yarım gün işi başlamadı** — yalnız tarif edildi ve önceliklendirildi.
- **T-42'nin kalan yarısı açık:** §11.2'nin `kural_degerleri` örneği hâlâ iki
  `S` kapsamlı kuralla yazılı. Hangi kuralla değiştirileceği — ya da alanın
  tümüyle çıkarılıp çıkarılmayacağı — karar bekliyor.
- **`PART_TIME_LIMIT`'in `C` kademesi** hâlâ okunmuyor; kayıt T-38'de.

---

## 7. Ek — yarım gün de kapsam dışına alındı (K-31)

Bölüm 5'te *"geriye kalan gerçek iş: yarım günlük izni motora taşımak"*
yazıyordu. Mustafa aynı oturumda onu da kapsam dışına aldı:

> *"Yarım günlük bir rapor önceden verilmez veya tahmin etmesi zordur. Bunu
> sistemin tutmasına gerek yok yani. Kullanıcı iznini girer, sistemde kayıt
> tutulur. Planı ilgili yönetici edit yardımıyla günceller."*

**Gerekçe sağlam ve zamanlamayla ilgili:** plan hafta öncesinden üretilir,
yarım günlük izin aynı gün ya da bir gün önce doğar. Çözücüye verilecek bir
bilgi değil.

### Ama karar "hiçbir şey yapma" değildi

Bugün motor yarım günlük izni alırsa **bütün günü kapatıyor**. Arka uç
izinleri ayıklamadan gönderirse, sabahı izinli olan kişi bütün gün müsait
değil görünür. Karar sözleşmeye **yazılmadıkça** bu yazısız bir varsayım
olarak kalırdı — T-19'un tam şekli.

Yazılanlar: §11.2'ye *"`izinler` yalnız TAM GÜN taşır, arka uç ayıklamakla
yükümlüdür"* notu, §8.3'e ikinci not, **K-31**, ve motordaki bildirim metni.

### Kanal ilk kez bekçi oldu

`okunmayan_alanlar` 23 Eylül'de bir **bulgu raporu** olarak açılmıştı. Burada
ilk kez bir **kararın bekçisi** olarak kullanıldı: yarım günlük izin motora
sızarsa rapor `izinler[].tum_gun` satırını bildirir. K-31'in tek otomatik
bekçisi bu.

> T-26'nın sorduğu soru buydu: *"bu kararın gerçekten uygulandığını kim
> soruyor?"* K-31 için cevabı var. K-21 için yok — ama K-21 bir şeyi
> **kaldırdığı** için bekçiye de ihtiyacı yok.

### Bırakılan sınır

Yönetici planı düzeltmeyi unutursa sistem yakalamaz. Bilinçli kabul edildi,
K-31'e yazıldı.

### Ölçümler

| Ne | Sonuç |
|---|---|
| Motor birim testleri | **77 geçti** (metin değişikliği, davranış aynı) |
| `YOL-KONTROL.py` | 8 kırık yol — hepsi eski |
| `00-DEVIR/` kökü | 9 dosya, R7 eşiği değişmedi |

---

## 8. K-32 — mola modeli baştan kuruldu

`SAGLIK_KISITI` kaldırıldıktan sonra iş mola tarafına kaydı ve günün en uzun
parçası oldu. Karar zinciri: mola ikiye ayrılsın (`dinlenme`/`yemek`) → yemeğin
yeri mutlak saat değil vardiyaya göre olsun → firma politikası tanımlansın →
dinlenme molaları eşit dağıtılsın.

### Gün içinde bir kez ters yöne gittim

K-32'nin ilk hâli *"yasal hakkı `dinlenme` karşılar"* ve *"dinlenme ücretli
olduğu için çalışma süresine dahildir"* diyordu. **İkisi de yanlıştı.**

Bunun üstüne `net_saat`'i değiştirdim, sonuç olarak *"motor günde bir saat
eksik hesaplıyor"* diye bir **bulgu uydurdum** ve Mustafa'ya sundum. Ardından
A08'in kırıldığını görüp *"altın senaryo yeniden onaylanmalı"* dedim.

Gerçek: `net_saat` **doğruydu**, A08 **doğruydu**, kıran şey benim modelimdi.

**Yakalayan dış inceleme oldu.** GPT'nin cümlesi: *"Bir molanın ücretli
olması, o sırada çalışanın iş yapıyor olmasıyla aynı şey değil."*

> Kendi ölçümüm bunu bulamazdı — **yanlış modeli doğru ölçüyordum** ve her
> test yeşil yanıyordu. 16 Eylül'de dış inceleme döngüsünü kurarken yazdığımız
> gerekçe buydu: *"aynı model aynı kör noktayı iki kez taşır."* İlk sefer kör
> nokta koddaydı; bu sefer **tasarımda** ve **bendeydi**.

Dört büyüklük ayrımı (`brut` / `çalışma` / `ücret` / `görev kapasitesi`) ve
*"sistem yemeğin üstüne otomatik bir saat eklemez"* kuralı dış incelemeden
geldi ve K-32'ye aynen alındı.

### Ölçmenin iki kez daha kazandırdığı

**Bir:** 9 saatlik vardiyaya *"30 dk yemek"* politikası verdim, plan
çözülemedi. Önce testimi yanlış yazdım sandım; motor haklıydı — politika
yasal tabanın altına inemez. Davranış teste bağlandı
(`test_politika_yasal_tabanin_ALTINA_inemez`).

**İki:** mutlak pencereyi kaldırmak A08'i hiç kırmadı. Çünkü A08'deki mola
09:00 vardiyasında 12:00'de, yani tam **3. saat** — Mustafa'nın verdiği 3–5
penceresinin içinde. 15 Eylül'de onaylanan fikstür, 25 Eylül'de konan kuralla
kendiliğinden uyumlu çıktı.

### Yazılanlar

| Katman | Ne |
|---|---|
| `09-motor/dogrulayici/zaman.py` | Mola tipi, tip süzgeci, `yemek_saat`/`dinlenme_saat`/`ucret_saat` |
| `09-motor/dogrulayici/kurallar.py` | Dört yeni kural; `MOLA_HAKKI`'ya hatanın kaydı ve bekçisinin adı |
| `09-motor/dogrulayici/denetle.py` | Üç süre ayrı metrik; sözleşme karşılaştırması ücrete bakıyor |
| `09-motor/cozucu/model.py` | Göreli pencere, mola politikası, eşit dağıtım aritmetiği |
| `09-motor/cozucu/coz.py` | Üretilen molaya `tip` |
| `02-spec/v1.4-master-spec.md` | §6.2 dört kural (34 → **38**), §8.4, §11.2, §11.3 |
| `08-motor-testleri/v5/fikstur/` | Mutlak pencere kaldırıldı, **19 mola bloğu** tiplendi |

### Bitmeyen — açıkça

**Dinlenme molaları çözücüye bağlanmadı.** Eşit dağıtım aritmetiği yazıldı ve
beş testle sınandı ama **çağrısız**; motor hâlâ tek mola üretiyor. Bağlamak
`_sahada`'yı yeniden kurgulamayı gerektiriyor: bugün *"seçilen mola bu dilimi
kapsamıyor"* diye tek bir boolean toplanıyor, dinlenme eklenince bu bir **VE**
bağlacına dönüşüyor ve yardımcı değişken + reification istiyor.

Bilerek bırakıldı: günün dersi ölçmeden ilerlememekti, ve çözücünün kapsama
matematiği yanlış olursa **testler yeşilken** yanlış plan üretir.

### Ölçümler

| Ne | Sonuç |
|---|---|
| Motor birim testleri | **98 geçti** |
| Altın senaryolar | **12 geçti, 4 atlandı** |
| Fikstür denetleyicisi | **11/11 tutarlı** |
| Katalogdaki kural | **38**, programla sayıldı |
