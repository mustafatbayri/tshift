# Altın Senaryolar A1–A12 — Kabul Ölçütleri (v3)

**Durum:** Onay bekliyor · **Tarih:** 15 Eylül 2026
**Önceki sürümler:** `../v1/` (ilk taslak, açık sorular) · `../v2/` (kararlar
işlendi) — ikisi de dondurulmuş, değiştirilmedi.
**Kaynak:** Master Spec v1.3 §5, §6, §9.7, §11, §16.3 + `00-DEVIR/08-URUN-KARARLARI.md` K-1…K-7

**v2 → v3 farkı:** İçerik aynı, **anlatım değişti.** v2 yazılım tarafına göre
yazılmıştı; Mustafa'nın onaylayacağı şey teknik ayrıntının altında kalıyordu.
v3'te her senaryo önce **iş diliyle** anlatılıyor, teknik karşılığı arkasına
konuyor. Hiçbir beklenen sonuç değişmedi — v2 ile satır satır aynı.

---

## İçindekiler

1. [Neyi onaylıyorsun](#1-neyi-onaylıyorsun)
2. [Nasıl okunur, neye dikkat edilir](#2-nasıl-okunur-neye-dikkat-edilir)
3. [Ortak sahne: "T-10 ekibi"](#3-ortak-sahne-t-10-ekibi)
4. [Senaryolar A1–A12](#4-senaryolar)
   - [A1 Kolay hafta](#a1--kolay-hafta) · [A2 İzinli kişiye zorunlu vardiya](#a2--izinli-kişiye-zorunlu-vardiya) · [A3 Tek yetkin kişi izinli](#a3--tek-yetkin-kişi-izinli)
   - [A4 Gece yarısını aşan vardiya](#a4--gece-yarısını-aşan-vardiya) · [A5 Yaz saati geçişi](#a5--yaz-saati-geçişi) · [A6 Elle sabitlenmiş atamalar](#a6--elle-sabitlenmiş-atamalar)
   - [A7 Kapsama mı, çalışan tercihi mi](#a7--kapsama-mı-çalışan-tercihi-mi) · [A8 Herkes aynı anda molada](#a8--herkes-aynı-anda-molada) · [A9 Kadro yetmiyor](#a9--kadro-yetmiyor)
   - [A10 Çift tıklama](#a10--çift-tıklama) · [A11 Geçmiş veri eksik](#a11--geçmiş-veri-eksik) · [A12 Geçen haftanın planını kopyala](#a12--geçen-haftanın-planını-kopyala)
5. [Veto edilebilir dört varsayım](#5-veto-edilebilir-dört-varsayım)
6. [Daha önce verdiğin kararlar (K-1…K-7)](#6-daha-önce-verdiğin-kararlar-k-1k-7)
7. [Onay nasıl verilir](#7-onay-nasıl-verilir)
8. [Onay sonrası ne olacak](#8-onay-sonrası-ne-olacak)

---

## 1. Neyi onaylıyorsun

Bu dosyadaki 12 senaryo, motorun **ne yapması gerektiğini** anlatan Türkçe
cümlelerdir. Motor daha yazılmadı. Cümleler şartnameden türetildi, motora
bakılarak değil — çünkü motora bakarak yazılan test, motorun hatasını
onaylamış olur (Master Spec §16.1).

Onayladığın şey **tek bir şey:**

> *"Bir vardiya planlama ürünü, bu durumda gerçekten böyle mi davranmalı?"*

Onayladıktan sonra bu cümleler çalıştırılabilir teste çevrilir. Motor yazılınca
testler ya yeşil yanar ya kırmızı. **Cümle yanlışsa motor yanlış davranışı
doğru sanarak yazılır ve test yeşil yanar** — hatayı sahada müşteri bulur.
Onayın gecikmeli bedeli budur.

**Onaylamadığın şeyler** — bunlara bakmana gerek yok:

| Bakma | Neden |
|---|---|
| JSON biçimi, alan adları | Mekanik; motor hangi dille yazılırsa yazılsın değişmez |
| Saat gösterimi (`25` = ertesi gün 01:00) | Şartnamenin §11.2'deki gösterimi, zaten karara bağlı |
| pytest, dosya düzeni, klasör adı | Yazılım tarafı |
| Hesapların doğruluğu (saat, dinlenme, kapasite) | Programatik doğrulandı; elle sayman gerekmiyor |

## 2. Nasıl okunur, neye dikkat edilir

Her senaryoda beş blok var:

| Blok | Ne işe yarar |
|---|---|
| **Durum** | Sahada olan şey, iş diliyle. Jargon yok. |
| **Doğru çalışıyorsa ne olmalı** | **Onaylayacağın cümleler.** Numaralı, her biri ayrı bir iddia. |
| **Dikkat** | Nerede itiraz etmen gerekebilir. Benim tereddütlerim burada. |
| **Kaynak** | Cümle nereden geldi (aşağıdaki tablo) |
| **Teknik karşılık** | Yazılım ekibi için. Sen atlayabilirsin. |

**Kaynak etiketleri — hangi cümleye daha çok dikkat etmelisin:**

| Etiket | Anlamı | Senin için |
|---|---|---|
| `[spec]` | Şartnamede yazılı, onaylı bir karara dayanıyor | Rutin kontrol |
| `[karar]` | Sen karar verdin, günlüğe yazıldı | Rutin kontrol |
| `[çıkarım]` | **Ben türettim.** Şartnamede yazmıyor, sen onaylamadın | **Buraya dikkat et** |

`[çıkarım]` satırları, bu projenin en korktuğu hata sınıfının (kodu yazan
testi de yazınca aynı yanlış varsayımın iki yere birden geçmesi) yaşanabileceği
yerlerdir.

## 3. Ortak sahne: "T-10 ekibi"

Senaryoların çoğu aynı sahnede geçiyor. Sadece farkı yazıyorum, gerisi bu:

> **Tek bir ekip, 10 kişi.** Hepsi aynı işi yapabiliyor, özel yetkinlik yok.
> Hepsi tam zamanlı, haftalık 45 saat sözleşmeli.
>
> **Bir haftalık plan:** 12–18 Ekim 2026, Pazartesi'den Pazar'a.
>
> **Tek vardiya tipi:** 08:00–16:00, içinde 1 saat mola. Yani kişi 8 saat
> sahada, 7 saat çalışıyor.
>
> **Talep:** Her gün, 08:00–16:00 arasında **en az 3**, **ideal 5** kişi sahada
> olsun.
>
> **Kimsenin izni yok**, kimsenin "şu saatte müsait değilim" kaydı yok, kimse
> tercih bildirmemiş. Firma İş Kanunu varsayılanlarıyla çalışıyor: günde en çok
> 9 saat, haftada 45, iki vardiya arası en az 11 saat dinlenme, haftada bir
> tam tatil günü, üst üste en çok 6 gün.

**Bu ekip rahat bir hafta geçirir mi?** Evet, ve hesabı şöyle: haftada en fazla
10 kişi × 6 gün = **60 kişi-gün** kapasite var. İdeal talep 5 kişi × 7 gün =
35 kişi-gün. Yani bolca yer var, kimsenin fazla mesai yapmasına gerek yok.
Kişi başı haftalık 42 saat çıkıyor, 45'in altında.

*Bu hesap `[çıkarım]` — benim. Doğruluğunu programatik kontrol ettim ama
mantığını sen onaylamalısın.*

---

## 4. Senaryolar

### A1 · Kolay hafta

**Durum.** T-10 ekibi, hiçbir komplikasyon yok. Müdür "plan üret" diyor.

**Doğru çalışıyorsa ne olmalı:**

1. Motor bir plan **üretir** — "çözemedim" demez.
2. **Hiçbir sert kural ihlali olmaz.** Sıfır. Bir tane bile olsa plan geçersizdir.
3. Her gün, her saatte **en az 3 kişi** sahadadır (asgari kapsama %100).
4. Her gün **5 kişi** sahadadır — ideal de tutar, çünkü kapasite yetiyor.
5. **Hiç fazla mesai yoktur.**
6. Bağımsız denetleyici aynı planı baştan kontrol ettiğinde **o da 0 ihlal
   bulur.** Motorun "ben temiz ürettim" demesi yetmez.
7. Kimse 7 gün üst üste çalışmaz, kimseye haftada 45 saatten fazla verilmez,
   kimseye aynı gün iki vardiya verilmez.
8. Çıktıda "bu plan kaç değişken ve kaç kısıt üzerinden çözüldü" bilgisi gelir.

**Dikkat.** 4. madde `[çıkarım]`: ideal kapsamanın **%100 tutmasını** bekliyorum,
çünkü kapasite fazlasıyla yetiyor. Sahada "ideal her zaman tutmayabilir, %95 de
kabul" diyorsan bu cümle gevşetilmeli. Gevşetirsek testin yakalama gücü düşer —
ama yanlış bir beklenti koymaktan iyidir.

**Kaynak:** 1–3, 5 `[spec §11.3, §16.3]` · 4 `[çıkarım]` · 6 `[spec §16.1]` ·
7 `[spec §6.2]` · 8 `[karar K-3]`

<details><summary>Teknik karşılık</summary>

`/solve`, T-10 girdisi. `durum = "cozuldu"`, `metrikler.sert_ihlal = 0`,
`asgari_kapsama_yuzde = 100`, `hedef_kapsama_yuzde = 100`,
`fazla_mesai_saat = 0`, `cozum_istatistikleri.onarim_denemesi = 0`.
Ardından aynı plan `/evaluate`'ten geçirilir, ihlal listesi boş olmalı.
</details>

---

### A2 · İzinli kişiye zorunlu vardiya

**Durum.** Ayşe'nin Çarşamba günü **onaylı yıllık izni** var. Ama sistemde
Çarşamba 08:00–16:00 için Ayşe'ye **sabitlenmiş bir atama** duruyor (müdür elle
koymuş ya da eski plandan gelmiş). İkisi aynı anda mümkün değil.

**Doğru çalışıyorsa ne olmalı:**

1. Motor **plan üretmez.** "Çözümsüz" der.
2. Çözümsüzlük ekranında **hangi kuralın engellediği** yazar: `ONAYLI_IZIN`,
   ve kaç kişiyi etkilediği.
3. Hangi gün ve hangi hücrede takıldığı gösterilir (Çarşamba).
4. Motor pes etmeden önce **en fazla 2 kez** yeniden dener; sonra çözümsüz der.
   Sonsuza kadar denemez.

**Dikkat — burası önemli.** Motorun "izne rağmen atadım ama 1 ihlalim var"
diyen bir plan üretmesi **kabul edilmiyor.** Çünkü o plan yayınlanabilir görünür
ve birisi onaylayabilir. Sert kural ihlali olan plan, plan değildir.

Buna itirazın olabilir: *"Ben yine de planı göreyim, ihlali de göreyim, kararı
ben vereyim"* diyebilirsin. O zaman bu cümle değişir ve ürün farklı davranır.
**Bu senin kararın, ve önemli bir karar.**

**Kaynak:** 1–2 `[spec §11.3, §16.3]` · 3 `[çıkarım]` · 4 `[spec §11.7 + K-3]`

<details><summary>Teknik karşılık</summary>

T-10 + Ç01'e gün 2 tüm gün `izinler`, + `sabit_atamalar`: Ç01 gün 2 08–16.
`durum = "cozumsuz"`; `teshis.engelleyen_kurallar` içinde
`{kod: "ONAYLI_IZIN", etkilenen_kisi >= 1}`; `teshis.hucre.gun = 2`;
`cozum_istatistikleri.onarim_denemesi = 2`.
</details>

---

### A3 · Tek yetkin kişi izinli

**Durum.** Firma kuralı: **Cuma günü sahada en az bir ilk yardım sertifikalı
kişi bulunmalı.** Ekipte bu sertifika sadece Zeynep'te var. Zeynep'in Cuma
izni onaylanmış.

**Doğru çalışıyorsa ne olmalı:**

1. Motor **plan üretmez**, çözümsüz der.
2. Engelleyen kural olarak **yetkinlik kapsaması** gösterilir.
3. Teşhis net konuşur: Cuma günü **1 kişi gerekiyor, 0 kişi mümkün.**
4. **Kontrol:** Zeynep'in izni kaldırılırsa aynı girdi çözülür ve Cuma günü
   Zeynep atanmış olur.

**Dikkat.** 4. madde testin kendisini sınıyor: senaryo gerçekten yetkinlikten
mi takıldı, yoksa başka bir sebepten mi? İzni kaldırınca çözülüyorsa sebep
gerçekten oydu. Buna projede "kırmızı kanıt" diyoruz.

Sahada asıl soru şu olabilir: *"Zeynep izinliyken Cuma hiç plan yapılamıyor mu?"*
Evet — çünkü kural firmanın kendi koyduğu sert kural. Ürün burada doğru
davranıyor ama **kullanıcıya ne söylediği** kritik: "çözemedim" değil, "Cuma
ilk yardımcı yok, izni kaldır ya da kuralı gevşet" demeli.

**Kaynak:** 1–2 `[spec §6.4, §16.3]` · 3 `[spec §11.3]` · 4 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

T-10 + `YETKINLIK_KAPSAMASI` (E1, gün 4, 08–15, `ilkyardim >= 1`), yetkinlik
yalnız Ç07'de, Ç07'ye gün 4 izni. `teshis.hucre.gun = 4`, `gereken = 1`,
`mumkun = 0`.
</details>

---

### A4 · Gece yarısını aşan vardiya

**Durum.** Bu senaryo **gerçek müşteri verisinden** geliyor: analiz ettiğimiz
3,5 aylık planda **182 atama** gece yarısını aşıyordu (`16:00–01:00`,
`15:00–00:00` gibi). Kenar durum değil, olağan işleyiş.

Burada motor plan üretmiyor; **elle hazırlanmış bir planı denetliyor.** Beş
farklı kişi, beş farklı tuzak:

| Kişi | Ne yapıyor | Sınanan şey |
|---|---|---|
| Ali | Salı 16:00–01:00, ertesi gün 09:00–17:00 | 01:00'de biten kişi 09:00'da başlarsa **8 saat** dinlenmiş olur |
| Burak | Salı 16:00–01:00, ertesi gün 12:00–20:00 | **Tam 11 saat** dinlenme — sınır durumu |
| Cem | Salı 16:00–01:00, ertesi gün 00:00–08:00 | İki vardiya **00:00–01:00 arası çakışıyor** |
| Deniz | Pazar 16:00–01:00 | Vardiya Pazartesi'ye taşıyor — hangi güne sayılır? |
| Elif | Perşembe 08:00–18:00, 1 saat mola | Net **tam 9 saat** — günlük sınır |

**Doğru çalışıyorsa ne olmalı:**

1. Ali için **bir** dinlenme ihlali yazılır; ölçülen dinlenme **8 saat**,
   gereken 11. Dinlenme, vardiyanın **gerçek bitişinden** ölçülür.
2. Burak tam 11 saat dinlenmiştir. **Varsayılan ayarda bu da ihlaldir** (K-1
   kararın). Firma ayarı gevşetilirse ihlal değildir. Test iki ayarla da koşar.
3. Cem için **bir** çakışma ihlali yazılır. Çakışma mutlak zamanda ölçülür.
4. Ali'nin Salı vardiyası **9 saat sahada / 8 saat çalışma**dır ve **Salı'ya**
   sayılır. Günlük sınır net süreye bakar → 8 < 9, ihlal yok.
5. Elif'in Perşembe vardiyası net **tam 9 saat**tir; varsayılan ayarda
   **ihlaldir** (yine K-1).
6. Deniz'in Pazar vardiyası **Pazar'a** sayılır. Pazartesi'ye hiçbir şey
   yazılmaz, ihlal de yok.
7. Kimsede mola ihlali yok — hepsinin molası kuralın istediği kadar.
8. **Toplam ihlal sayısı:** varsayılan ayarda **4** (Ali, Burak, Cem, Elif),
   gevşek ayarda **2** (Ali, Cem). Fazlası da eksiği de hata.

**Dikkat.** Bu senaryo, ürünün en kolay sessiz hata yapacağı yer. `16:00–01:00`
vardiyasını "aynı gün 01:00'de bitiyor" diye yorumlayan bir hesap, Ali'nin 8
saatlik dinlenmesini **32 saat** görür ve ihlali kaçırır. Gerçek müşteri
verisinde bunun 88 vakası vardı ve kimse fark etmemişti.

2. ve 5. maddeler senin K-1 kararının doğrudan sonucu. Kararını değiştirmek
istersen tek değişiklik: varsayılan `sinir_dahil` değeri.

**Kaynak:** 1, 3, 4, 6 `[spec §6.3 Z-1…Z-4]` · 2, 5 `[karar K-1]` ·
7 `[spec §6.2]` · 8 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

`/evaluate`. Talep yok, kapsama kuralları kural listesinde değil (yalıtım).
Şablonlar: V-AKSAM `bas 16 bit 25 mola 60`, V-UZUN `bas 8 bit 18 mola 60`.
Fikstür `fikstur/A04.json`, iki varyant (`sinir_dahil` false/true),
beklenen 4 / 2 ihlal. Tüm süreler `fikstur-denetleyici.py` ile doğrulandı.
</details>

---

### A5 · Yaz saati geçişi

**Durum.** Türkiye'de yaz saati yok, ama ürün yurt dışına satılacaksa gerekli.
Almanya'da bir kiracı düşün: **28 Mart 2027 Pazar** gecesi saat 02:00'de 03:00'e
alınıyor. O gün **23 saat** sürüyor.

Ayşe Cumartesi 23:00'te işten çıkıyor, Pazar 10:00'da başlıyor. Duvar saatine
bakarsan 11 saat dinlenmiş görünüyor. **Gerçekte 10 saat dinlenmiş** — bir saat
buharlaştı.

**Doğru çalışıyorsa ne olmalı:**

1. Geçiş gecesi 22:00–07:00 çalışan kişi **8 saat** çalışmış sayılır, 9 değil.
2. Ayşe için dinlenme ihlali **yazılır** ve ölçülen değer **10 saat** olarak
   kaydedilir. Test yalnız "ihlal var mı" diye bakmaz, **10 yazdığını da**
   kontrol eder.
3. Geçiş günü normal 08:00–16:00 çalışan kişi 8 saat çalışmıştır, ihlal yok.
4. **Kontrol:** aynı senaryo Türkiye kiracısında koşulursa Ayşe'nin dinlenmesi
   **11 saat** ölçülür. Fark gerçekten saat diliminden geliyor.
5. Kiracının saat dilimi `+01:00` gibi sabit bir sayıyla girilirse sistem
   **kabul etmez**, hata verir. `Europe/Berlin` gibi bölge adı zorunlu (K-2).

**Dikkat.** 2. maddedeki ayrıntı önemli: varsayılan ayarda 11 saat de ihlal
olduğu için, test yanlış sebeple yeşil yanabilirdi. O yüzden ölçülen değerin
**10** olduğunu ayrıca sınıyoruz.

Bu senaryo bugün hiçbir müşteriyi ilgilendirmiyor. Şimdi yazılmasının sebebi,
zaman modelini sonradan değiştirmenin bedelinin "her plan yeniden yorumlanır"
seviyesinde olması.

**Kaynak:** 1–3 `[spec §6.3, Z-6; 02-DEGISMEZLER G-6]` · 4 `[çıkarım]` ·
5 `[karar K-2]`

<details><summary>Teknik karşılık</summary>

`/evaluate`, kiracı `Europe/Berlin`, hafta 2027-03-22…28, `DST_GECISI` aktif.
Süreler mutlak zamanda (UTC) ölçülür. 28 Mart 2027'nin Pazar olduğu ve gün
uzunlukları IANA verisiyle doğrulandı. Sonbahar geçişi (25 saatlik gün)
K-6 ile ileri tura bırakıldı.
</details>

---

### A6 · Elle sabitlenmiş atamalar

**Durum.** Müdür plan üzerinde üç atamayı elle yapmış ve kilitlemiş: "bu üç
kişi bu günlerde kesin burada olacak". Ayrıca bir kişiye "Çarşamba günü **bu
kişiye vardiya verme**" demiş. Şimdi motordan kalan boşlukları doldurmasını
istiyor.

**Doğru çalışıyorsa ne olmalı:**

1. Motor planı üretir, sert ihlal yok.
2. **Üç sabit atama çıktıda birebir durur** — aynı kişi, aynı gün, aynı saat.
   Motor bunları "daha iyisini buldum" diye değiştiremez.
3. Yasaklı kişiye Çarşamba **hiçbir atama yapılmaz.**
4. Sabit atamalar yüzünden başka bir kural bozulmaz: o üç kişinin haftalık
   saati yine sınır altında, hafta tatilleri yerinde.
5. Bu davranış firma tarafından **kapatılamaz.** Kilit uyumu sistem kuralıdır.

**Dikkat.** Buradaki ilke şu: **motor kullanıcının kararını geri alamaz.**
Yöneticinin elle yaptığı düzenleme, motorun optimizasyonundan üstündür. Bu
ürünün güven kazanma biçimi — bir kere "elle koyduğumu sildi" denirse editöre
kimse güvenmez.

Ama tersi bir risk de var: sabit atamalar yüzünden plan çözümsüzleşebilir.
O durumda ne olmalı? Şu an **A2'deki gibi davranıyor** (çözümsüz + teşhis).
Kabul ediyorsan bir şey yapmana gerek yok.

**Kaynak:** 1–3 `[spec §6.6, §11.2, §16.3]` · 4 `[çıkarım]` · 5 `[spec §6]`

<details><summary>Teknik karşılık</summary>

T-10 + `sabit_atamalar` (Ç01 gün 0, Ç02 gün 3, Ç03 gün 6, 08–16) +
`kilitler` (Ç04 gün 2 `tip: yasak`). `KILIT_UYUMU` kapsamı `S` (sistem),
kural listesinde gönderilmese bile geçerli.
</details>

---

### A7 · Kapsama mı, çalışan tercihi mi

**Durum.** Ürünün satış noktalarından biri: aynı hafta için **üç farklı plan
önerisi** üretmek. Dengeli, kapsama odaklı, çalışan odaklı.

Sahne: hafta içi iki vardiya var — sabah (08:00–16:00) ve akşam (14:00–22:00).
Akşam için ideal 5 kişi isteniyor. Ama **8 kişi sabah çalışmayı tercih
ettiğini bildirmiş**, sadece 2 kişinin tercihi yok.

Yani akşamı doldurmak için tercihli birilerini akşama almak gerekiyor.

**Doğru çalışıyorsa ne olmalı:**

1. Her iki profil de plan üretir, sert ihlal yok, asgari kapsama %100.
2. **Kapsama odaklı** plan, çalışan odaklı plandan **daha iyi kapsama** verir
   (ya da eşit).
3. **Çalışan odaklı** plan, kapsama odaklı plandan **daha çok tercih karşılar**
   (ya da eşit).
4. İkisi **birden eşit olamaz.** Eşitse ağırlıklar hiçbir şey değiştirmiyor
   demektir ve test kırmızı yanar.
5. Tercih hiçbir profilde sert kural gibi davranmaz — kapsama profilinde
   tercihli birini akşama almak **ihlal sayılmaz**, sadece puanı düşürür.

**Dikkat.** Bu senaryonun asıl işi, "üç bakışlı plan önerisi" iddiasının
**gerçekten çalıştığını** kanıtlamak. Demoda üç kart göstermek kolay; üç kartın
gerçekten farklı olması zor. 4. madde tam olarak o farkı zorunlu kılıyor.

Ölçüm biçimi `[çıkarım]`: "daha iyi kapsama" ve "daha çok tercih" derken hangi
metriğe baktığımı ben seçtim. Sahada başka bir ölçü daha anlamlıysa söyle.

**Kaynak:** ağırlıklar `[spec §5.4]` · yön `[spec §16.3]` · ölçüm `[çıkarım]`

<details><summary>Teknik karşılık</summary>

Aynı girdi, iki `/solve` çağrısı: `profil = "KAPSAMA"` ve `"CALISAN"`.
`hedef_kapsama_yuzde(KAPSAMA) >= hedef_kapsama_yuzde(CALISAN)` ve
`tercih_karsilama_yuzde(CALISAN) >= tercih_karsilama_yuzde(KAPSAMA)`,
en az biri kesin büyük. `tercih_karsilama_yuzde` metriği §11.3'te **yok**,
v1.4'te eklenmeli (T-4).
</details>

---

### A8 · Herkes aynı anda molada

**Durum.** Dört kişi 08:00–16:00 çalışıyor, her birinin 1 saat molası var.
Dördü de molayı **12:00–13:00**'te kullanıyor. O saatte sahada **kimse yok** —
ama kâğıt üzerinde dört kişi "çalışıyor" görünüyor.

Talep: her saat en az 3 kişi sahada.

**Doğru çalışıyorsa ne olmalı:**

1. **Kötü plan denetlendiğinde:** 12:00–13:00 için mola kapsaması ihlali
   yazılır — o saatte sahada 0 kişi var, 3 olmalıydı.
2. **İyi planda** (molalar 11–12, 12–13, 13–14, 14–15 diye kaydırılmış) hiç
   ihlal yok: her saatte en az 3 kişi kalıyor.
3. Her atamada **60 dakika** mola var. 8 saatlik vardiya için kural bu (K-4).
   30 dakika verilse mola hakkı ihlali olurdu.
4. **Motor kendisi plan ürettiğinde** molaları da kendisi yerleştirir ve hiçbir
   saatte sahadaki kişi 3'ün altına inmez. Bunu bağımsız denetleyici ayrıca
   sayar — motorun kendi raporuna güvenilmez.
5. Mola çalışma süresinden düşülür: 4 kişi × 7 saat = günlük 28 saat, 32 değil.
6. Bir kişinin molası **tek parça**dır, bölünmez. (Kişiler arasında kaydırmak
   serbest.)

**Dikkat.** Mola planlaması senin **ürünün 2. satış noktası** dediğin şey. Bu
senaryo onun temel testi. Gerçek müşteri verisinde mola bilgisi hiç yoktu —
yani mevcut süreç bu hesabı **hiç yapmıyor.**

6. madde `[çıkarım]` ve hukuki tarafı var: İş Kanunu ara dinlenmenin aralıksız
verilmesini esas alıyor, bölünmesi sözleşmeye bağlı. Uzman teyidi konusu.

**Kaynak:** 1–5 `[spec §6.2, §6.4, §16.3; karar K-4]` · 6 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

(a) ve (b) `/evaluate`, (c) `/solve`. Tek gün, talep 08–15 `asgari 3 hedef 4`.
`MOLA_KAPSAMASI` ihlali 12:00–13:00 hücresine işaret eder.
</details>

---

### A9 · Kadro yetmiyor

**Durum.** Üç ayrı durum, üçü de "kadro az" ama sonuçları farklı olmalı.

| | Talep | Sahada ne demek |
|---|---|---|
| **(a)** | en az 3, ideal 9 | Asgari rahat tutuyor, ideal tutmuyor — 9×7=63 kişi-gün gerekir, kapasite 60 |
| **(b)** | en az 11 | Kadro 10 kişi. **Hiçbir gün** 11 kişi sahaya çıkamaz |
| **(c)** | en az 9 | Her gün 9 kişi **mümkün** (9 ≤ 10), ama hafta boyu 63 kişi-gün gerekir, kapasite 60 |

**Doğru çalışıyorsa ne olmalı:**

1. **(a)** Motor plan **üretir.** Asgari %100 tutar, ideal tutmaz.
2. **(a)** Eksik **dakika cinsinden** raporlanır, ve hangi hücrede kaç kişi
   eksik olduğu listelenir. "İdeal tutmadı" demekle yetinmez.
3. **(a)** Motor ideali kovalamak için **fazla mesai tavanını aşmaz** ve
   kimseye 7 gün üst üste çalışma yazmaz. Eksik kapsama, kural ihlalinden
   iyidir.
4. **(b)** Motor plan **üretmez.** Asgariyi karşılamayan bir plan asla
   "çözüldü" diye dönmez.
5. **(b)** Teşhis **hücre** seviyesinde: "bu hücrede 11 gerekiyor, en fazla 10
   mümkün", ve gevşetme önerisi sunulur.
6. **(c)** Motor plan **üretmez.** Teşhis **hafta** seviyesinde: "haftada 63
   kişi-gün gerekiyor, kapasite 60", engelleyen kural hafta tatili ve/veya
   ardışık çalışma sınırı.
7. **(c) bu senaryonun asıl sebebi:** motor hafta toplamını görmezse, her hücre
   tek başına mümkün göründüğü için **birine yedi gün üst üste çalıştıran** bir
   plan üretir. Test o planın üretilmediğini sınıyor.

**Dikkat.** Buradaki ayrım senin 14 Eylül kararın (K-5'in kardeşi): **asgari**
tutmuyorsa çözümsüz, sadece **ideal** tutmuyorsa plan üretilir ve eksik
raporlanır. Şartnamedeki A9 maddesi bunu karıştırıyordu, v1.4'te düzeltilecek.

Sahada asıl soru: küçük müşteri bu ekranı **en sık görecek** olan. 20 kişilik
otel bar ekibi sürekli sınırda çalışır. O yüzden "çözemedim" demek yetmez;
**ne yapılırsa çözülür** demek zorunda.

**Kaynak:** ayrım `[karar]` · 1, 4 `[spec §5.3, §11.3]` · 2 `[spec §16.3]` ·
6 `[karar K-7]` · 3, 5, 7 `[çıkarım]` (kapasite hesabı programatik doğrulandı)

<details><summary>Teknik karşılık</summary>

Üç fikstür. (a) `cozuldu` + `eksik_hedef_dakika > 0`. (b) `cozumsuz`,
`teshis.kapsam = "hucre"`, `gereken 11`, `mumkun <= 10`. (c) `cozumsuz`,
`teshis.kapsam = "hafta"`, `gereken 63`, `mumkun 60`. `eksik_hedef_dakika`
ve `teshis.kapsam` §11.3'te yok, v1.4'te eklenecek (T-4, T-5).
</details>

---

### A10 · Çift tıklama

**Durum.** Müdür "Plan üret" düğmesine bastı, sayfa yavaş yüklendi, tekrar
bastı. Ya da internet koptu, tarayıcı isteği yeniden gönderdi.

**Doğru çalışıyorsa ne olmalı:**

1. **Tek plan üretilir.** İkinci istek aynı planın kimliğini döner, motor
   ikinci kez hiç çalışmaz.
2. İlk çalışma **hâlâ sürüyorsa** ikinci istek mevcut çalışmanın kimliğini
   döner; ikinci bir çalışma başlatılmaz.
3. Kullanıcı **gerçekten yeni bir plan** isterse (yeni istek anahtarıyla) yeni
   plan üretilir. Yani koruma, meşru ikinci planı engellemez.
4. Bu koruma **firmaya özeldir.** B firması aynı anahtarla istek atarsa A
   firmasının sonucunu **almaz**, kendi planını üretir.
5. Denetim kaydında yinelenen istek için ayrı bir "plan üretildi" izi yoktur.

**Dikkat.** 4. madde `[çıkarım]` ama kritik: firmalar arası sızıntı bu üründe
geri dönülmez hata. Diğer 9 kiracılık koruması gibi bunun da testi olmalı.

Plan üretimi 15 dakika sürebiliyor ve maliyetli (AI çağrısı + çözücü). Çift
tıklamanın iki plan üretmesi hem para hem karışıklık demek.

**Kaynak:** 1–3 `[spec §11.7, §16.3]` · 4–5 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

Backend testi (xUnit), motor yerine çağrı sayan bir taklit. Aynı
`istek_anahtari` ile üç alt durum: bitmiş / sürüyor / farklı anahtar.
`plan_runs` tablosunda satır sayısı kontrol edilir.
</details>

---

### A11 · Geçmiş veri eksik

**Durum.** Müdür 12 Ekim haftası için plan istiyor. Ama sistemde **5–11 Ekim
haftasının planı yok** — o hafta girilmemiş.

Neden önemli: "iki vardiya arası 11 saat dinlenme" kuralı hafta sınırını aşar.
Pazartesi sabah 08:00'de başlayan birinin, önceki Pazar gecesi 02:00'ye kadar
çalışıp çalışmadığını bilmeden o plan doğrulanamaz.

**Doğru çalışıyorsa ne olmalı:**

1. İstek motora **hiç gitmez.** Sistem önce hazırlık kontrolü yapar.
2. Kullanıcıya **hangi tarihlerin eksik olduğu** söylenir: "5–11 Ekim arası
   plan yok". "Veri eksik" demekle yetinmez.
3. Eksik hafta girilince hazırlık geçer ve motor çalışır.
4. **Yeni kiracı farkı (senin K-5 kararın):** firma yeni kurulmuşsa ve hiç
   geçmişi yoksa, motor **çalışır** — engellenmez. Ayrım ölçütü: geçmiş
   penceresi firmanın **ilk yayınlanmış planından** öncesine düşüyorsa durum
   "boş"tur, "eksik" değil. O çalıştırmaya "geçmişsiz başlangıç" notu düşülür.

**Dikkat.** 4. maddedeki **ölçüt** `[çıkarım]`: "ilk yayınlanmış plan" ölçüsünü
ben seçtim. Alternatifi firma oluşturma tarihiydi ama yanıltıcı — firma üç ay
önce açılıp yeni plan yapmaya başlamış olabilir.

Bu senaryo sahada can sıkıcı görünür ("niye plan üretmiyor?") ama alternatifi
daha kötü: eksik geçmişle üretilen plan, dinlenme ihlalini **sessizce** kaçırır.

**Kaynak:** 1–2 `[spec §11.2]` · 3 `[çıkarım]` · 4 `[karar K-5]`, ölçüt `[çıkarım]`

<details><summary>Teknik karşılık</summary>

Backend hazırlık kontrolü. `eksik_veri` listesinde
`{tip: "lookback_atamalar", aralik: "2026-10-05…2026-10-11"}`. Motor taklidi
0 kez çağrılmalı. Yeni kiracı durumunda `plan_runs`'a not.
</details>

---

### A12 · Geçen haftanın planını kopyala

**Durum.** Müdür 12 Ekim haftasının planını beğenmiş, 26 Ekim haftasına aynısını
uygulamak istiyor. Ama arada **bir çalışan işten ayrılmış** (pasife alınmış).

Not: bu özellik, motorun "aynı girdiyle aynı planı üretirim" sözü vermemesinin
karşılığı. Kullanıcının gerçek isteği "aynı planı tekrar uygula"ydı; cevabı
determinizm değil, kopyalama.

**Doğru çalışıyorsa ne olmalı:**

1. Yeni plan **taslak** olarak oluşur, doğrudan yayınlanmaz.
2. Ayrılan kişinin atamaları yeni planda **yok**; diğer 9 kişinin atamaları gün
   ve saat olarak **aynı**.
3. Düşen atamalar kullanıcıya **tek tek listelenir** — hangi gün, hangi saat.
   "1 atama düştü" gibi bir özet yetmez, **sessizce silinmez.**
4. Kopya **doğrulayıcıdan geçer.** Kişi düştüğü için bir hücrede asgari kapsama
   bozulduysa bu **ihlal olarak gösterilir**; motor çağrılıp boşluk sessizce
   doldurulmaz.
5. **Kaynak plan hiç değişmez.**
6. Denetim kaydına iz düşer: hangi plandan, hangi aralığa, kaç atama düştü.

**Dikkat.** 3. ve 4. maddeler aynı ilkenin iki yüzü: **ürün kullanıcı adına
sessiz karar vermez.** Kopyalarken eksik oluştuysa kullanıcı görsün ve kendisi
doldursun. Alternatifi "sistem hallediyor" hissi, ki o his bir kere yanlış
çıkınca güven gider.

5. ve 6. maddeler `[çıkarım]` — bana doğru göründü ama senin onayın gerek.

**Kaynak:** 1–4 `[spec §9.7, §16.3]` · 5–6 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

Backend testi. Kaynak plan yayınlanmış, Ç03 pasife alınmış, hedef aralık
+14 gün. Cevapta `dusen_atamalar` listesi dolu; yeni plan `taslak`;
doğrulayıcı sonucu taslağa yazılır.
</details>

---

## 5. Veto edilebilir dört varsayım

Bunları ben türettim. İtiraz etmezsen fikstürlere böyle girecekler.

| # | Varsayım | Neden böyle seçtim |
|---|---|---|
| **V-1** | İki vardiya çakışıyorsa **yalnız çakışma ihlali** yazılır; ayrıca dinlenme ihlali yazılmaz | Tek hata iki satır üretirse ihlal sayısı anlamını yitirir ve kullanıcı aynı sorunu iki kez düzeltmeye çalışır |
| **V-2** | Bir kişinin molası **tek parça**dır; kişiler arası kaydırma serbest | İş Kanunu md. 68 ara dinlenmenin aralıksız verilmesini esas alır; bölünmesi sözleşmeye bağlı. Bölme sonradan parametre olabilir |
| **V-3** | "Geçmiş yok" ölçütü: geçmiş penceresi firmanın **ilk yayınlanmış planından** öncesine düşüyorsa | Nesnel ve test edilebilir. Firma oluşturma tarihi yanıltıcı olurdu |
| **V-4** | Mola hakkı eşiği **brüt** vardiya süresine uygulanır (08–16 = 8 saat → 60 dk) | Net süreye uygulamak döngüsel: net mola'ya, mola net'e bağlı olur. Brüt hesap kanunun istediğinden **asla az** mola vermez — hem belirli hem güvenli taraf. **Hukuki yorum; avukat değilim, uzman teyidi gerekli** |

## 6. Daha önce verdiğin kararlar (K-1…K-7)

Bunlar 14 Eylül'de karara bağlandı, tekrar onay istemiyorum — bağlam için
duruyor. Tam gerekçeler `00-DEVIR/08-URUN-KARARLARI.md`'de.

| # | Karar | Hangi senaryoyu etkiliyor |
|---|---|---|
| K-1 | Sınır değerler **ihlal** (tam 11 saat dinlenme, tam 9 saat günlük); firma ayarıyla gevşetilebilir | A4 (2, 5, 8) |
| K-2 | Saat dilimi sabit ofsetle gelirse **reddedilir** | A5 (5) |
| K-3 | Çözücü istatistikleri çıktıya girer, müşteriye gösterilir | A1 (8), A2 (4) |
| K-4 | Mola hakkı İş Kanunu'na göre, brüt süreden | A8 (3) |
| K-5 | Geçmişi olmayan kiracıda motor çalışır | A11 (4) |
| K-6 | Sonbahar DST kontrolü ileri tura | A5 sonu |
| K-7 | Çözümsüzlük teşhisine hafta seviyesi eklenir | A9 (6, 7) |

## 7. Onay nasıl verilir

Senaryo senaryo gidebilirsin, hepsini tek seferde bitirmen gerekmiyor.
Her senaryo için üç cevaptan biri:

| Cevap | Ne olur |
|---|---|
| **"A3 tamam"** | Cümleler dondurulur, fikstürü yazılır |
| **"A3'te 4. madde şöyle olmalı: …"** | Cümle düzeltilir, sonra dondurulur |
| **"A3'ten emin değilim, sahayı sorayım"** | O senaryo beklemeye alınır; diğerleri ilerler |

Ayrıca V-1…V-4 için ayrı bir "tamam" ya da itiraz gerekiyor.

**Öneri sıra:** En çok düşünmeyi hak edenler **A2** (çözümsüz mü, ihlalli plan
mı), **A4** (gerçek veriden geliyor, 182 vaka) ve **A9** (küçük müşterinin en
sık göreceği ekran). Diğerleri daha rutin.

## 8. Onay sonrası ne olacak

1. Onaylanan cümleler **değişmez**; bu dosya `v3` olarak dondurulur.
2. `v3/fikstur/A01.json … A12.json` yazılır — uygulamadan bağımsız veri
   dosyaları. Örnek olarak `A04.json` şimdiden burada.
3. A1–A9 için pytest iskeleti, A10–A12 için xUnit testleri. Motor olmadığı
   için **hepsi kırmızı** başlar; istenen budur (§16.4 kırmızı kanıt).
4. `00-DEVIR/04-TEST-HARITASI.md`'ye "Altın senaryolar" bölümü.
5. Şartnamedeki sekiz tutarsızlık (T-1…T-8) ve yedi karar (K-1…K-7) →
   `02-spec/v1.4-master-spec.md`. v1.3'e dokunulmaz.
