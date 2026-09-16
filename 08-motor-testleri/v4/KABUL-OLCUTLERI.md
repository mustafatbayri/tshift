# Altın Senaryolar A1–A12 — Kabul Ölçütleri (v4)

**Durum:** Mustafa'nın 15 Eylül geri bildirimi işlendi · **yeniden onay bekliyor**
**Tarih:** 15 Eylül 2026
**Önceki sürümler:** `../v1/` `../v2/` `../v3/` — dondurulmuş, değiştirilmedi.

**v3 → v4 farkı özeti.** Bu sefer içerik değişti, anlatım değil.

| Ne değişti | Nerede |
|---|---|
| **Sahne gerçekçi hâle getirildi:** çoklu vardiya tipi, part-time, cumartesi nöbeti | §3 (T-10 → **S-10**) |
| Hedef kapsama sözü %100 → **%95** | A1, K-8 |
| **İzin planlamayı ezer** — çakışma oluşturulamaz, sonradan gelen izin kişiyi plandan düşürür | A2, K-9 |
| **Yönetici çözümsüz planı kabul edebilir** — en iyi plan + kabul edilmiş ihlal kaydı | A3, A6, K-10 |
| **K-1 GERİ ALINDI** — sınır değer ihlal değil. Yanlış sorulmuş bir soruydu | A4, K-11 |
| **DST ertelendi** — altyapı kalıyor, test v1 kapsamı dışı | A5, K-12 |
| **Çalışan tercihi diye bir şey yok** — uygunluk sözleşmeden gelir, part-time için sert | A7, K-13 |
| Mola: **yerleşim penceresi** vardiya parametresi, tek blok, çıktı **öneri** niteliğinde | A8, K-14 |
| Plan kopyalama motoru **doğrulama için** çalıştırır, editör ekranına taşır | A12, K-15 |

---

## İçindekiler

1. [Neyi onaylıyorsun](#1-neyi-onaylıyorsun)
2. [Nasıl okunur](#2-nasıl-okunur)
3. [Ortak sahne: S-10](#3-ortak-sahne-s-10)
4. [Senaryolar](#4-senaryolar) — [A1](#a1--normal-hafta) [A2](#a2--izin-planlamayı-ezer) [A3](#a3--imkânsız-durum-ve-yöneticinin-kararı) [A4](#a4--gece-yarısını-aşan-vardiya) [A5](#a5--yaz-saati-geçişi--ertelendi) [A6](#a6--elle-sabitlenmiş-atamalar) [A7](#a7--cumartesi-adaleti-mi-kapsama-mı) [A8](#a8--öğle-arası-planlaması) [A9](#a9--kadro-yetmiyor) [A10](#a10--çift-tıklama) [A11](#a11--geçmiş-veri-eksik) [A12](#a12--geçen-haftanın-planını-kopyala)
5. [Veto edilebilir varsayımlar](#5-veto-edilebilir-varsayımlar)
6. [Kararlar K-1…K-15](#6-kararlar-k-1k-15)
7. [Onay nasıl verilir](#7-onay-nasıl-verilir)
8. [Onay sonrası](#8-onay-sonrası)

---

## 1. Neyi onaylıyorsun

Bu 12 senaryo, motorun **ne yapması gerektiğini** anlatan Türkçe cümlelerdir.
Motor daha yazılmadı. Cümleler şartnameden ve senin kararlarından türetildi,
motora bakılarak değil (Master Spec §16.1).

Onayladığın tek şey: *"Bir vardiya planlama ürünü bu durumda gerçekten böyle mi
davranmalı?"*

Onaydan sonra bu cümleler teste çevrilir. **Cümle yanlışsa motor yanlış
davranışı doğru sanarak yazılır ve test yeşil yanar** — hatayı sahada müşteri
bulur.

Bakmana gerek olmayanlar: JSON biçimi, alan adları, saat gösterimi, pytest,
dosya düzeni. Hesapların doğruluğunu programatik kontrol ettim.

## 2. Nasıl okunur

Her senaryoda: **Durum** (sahada olan şey) · **Doğru çalışıyorsa ne olmalı**
(onaylayacağın numaralı cümleler) · **Dikkat** (tereddütlerim) · **Kaynak** ·
katlanmış **Teknik karşılık**.

| Etiket | Anlamı | Senin için |
|---|---|---|
| `[spec]` | Şartnamede yazılı | Rutin |
| `[karar]` | Sen karar verdin, kayıtlı | Rutin |
| `[çıkarım]` | **Ben türettim**, sen onaylamadın | **Dikkat** |

## 3. Ortak sahne: S-10

> **v3'teki "T-10" sahnesi kaldırıldı.** Mantığı doğruydu ama gerçekçi değildi:
> tek vardiya tipi, herkes tam zamanlı, cumartesi yok. Mustafa'nın notu:
> *"Bizim problemini çözeceğimiz yerler muhtemelen birden fazla mesai tipi olan
> ve part-time eleman çalıştıran kurumlar olacak."* Yeni sahne ona göre kuruldu.

**Ekip E1 — 10 kişi, bir ofis/şube operasyonu.**

| Kim | Sözleşme | Kısıt |
|---|---|---|
| Ç01–Ç07 | Tam zamanlı, 45 saat/hafta | — |
| **Ç08** | Yarı zamanlı, 20 saat/hafta | Öğrenci: **Salı günleri tüm gün ders**, çalışamaz |
| **Ç09** | Yarı zamanlı, 24 saat/hafta | İkinci öğretim: **16:00'dan sonra çalışamaz** |
| Ç10 | Yarı zamanlı, 20 saat/hafta | — |

**Vardiya tipleri:**

| Şablon | Saat | Öğle arası | Net |
|---|---|---|---|
| `V-TAM` | 09:00–18:00 | 60 dk, **12:00–14:00 penceresinde** | 8 saat |
| `V-ERKEN` | 08:00–16:00 | 60 dk, 12:00–14:00 penceresinde | 7 saat |
| `V-CMT` | 09:00–13:00 | 15 dk | 3,75 saat |

**Talep:**

| Ne zaman | Asgari | Hedef |
|---|---|---|
| Pazartesi–Cuma, 09:00–18:00 | **3 kişi** | 5 kişi |
| **Cumartesi, 09:00–13:00** | **3 kişi** | 3 kişi (nöbet) |
| Pazar | kapalı | — |

**Hafta:** 12–18 Ekim 2026. **Kurallar:** §6 varsayılanları (günde 9 saat,
haftada 45, 11 saat dinlenme, haftada bir tam tatil, üst üste 6 gün) +
cumartesi yükü için adalet dengesi.

**Bu sahne uygulanabilir mi? Evet — hesabı şöyle:**

| Büyüklük | Değer | Nasıl |
|---|---|---|
| Öğle arası matematiği | günde **en az 6 kişi** | Mola 12–14 penceresinde iki bloğa bölünür; N kişiden yarısı molada olur, sahada 3 kalması için N ≥ 6 |
| Gereken atama | **33 kişi-gün** | 5 gün × 6 kişi + cumartesi 3 |
| Tam zamanlı kapasite | 35 vardiya | 7 kişi × 5 gün |
| Part-time kapasite | 7 vardiya | Saat sınırlarından: Ç08 2, Ç09 3, Ç10 2 |
| **Toplam** | **42 ≥ 33** | Yer var, fazla mesai gerekmiyor |

Tam zamanlı biri 5 gün × 8 saat = **40 saat**, 45'in altında.
Ç09'a `V-TAM` verilemez (18:00'de biter), `V-ERKEN` uygundur.

*Bu hesap programatik doğrulandı. Mantığını sen onaylamalısın — `[çıkarım]`.*

---

## 4. Senaryolar

### A1 · Normal hafta

**Durum.** S-10 ekibi, komplikasyon yok. Müdür "plan üret" diyor.

**Doğru çalışıyorsa ne olmalı:**

1. Motor plan **üretir**.
2. **Sert kural ihlali sıfır.**
3. Asgari kapsama **%100** — hafta içi her saat en az 3 kişi, cumartesi 3 kişi.
4. Hedef kapsama **en az %95** (K-8). %100 olabilir ama söz verilmiyor.
5. **Fazla mesai yok.**
6. Part-time kısıtlarına uyulur: Ç08'e **hiçbir Salı** atanmaz; Ç09'a
   16:00'dan sonra biten vardiya (`V-TAM`) **verilmez**.
7. Kimsenin haftalık saati sözleşmesini aşmaz — Ç08 20, Ç09 24, Ç10 20 saati
   geçmez; tam zamanlılar 45'i geçmez.
8. Kimse 7 gün üst üste çalışmaz, kimseye aynı gün iki vardiya verilmez.
9. Bağımsız doğrulayıcı aynı planda **0 sert ihlal** bulur.
10. Çıktıda "kaç değişken, kaç kısıt üzerinden çözüldü" bilgisi gelir.

**Dikkat.** 4. madde senin kararın (K-8): *"%95 de kabul görür, özellikle daha
kompleks problemler çözdüğümüzde %95 kabul oranı çok daha yüksek değer
gösterebilir."* Test artık `>= 95` diyor, `= 100` demiyor.

6. ve 7. maddeler yeni — part-time kısıtları sahnenin kalbinde olduğu için
artık A1'in bir parçası. Bunlar **sert** kısıt: Ç08 Salı çalışamaz, "tercih
etmiyor" değil.

**Kaynak:** 1–3, 5 `[spec §11.3, §16.3]` · 4 `[karar K-8]` · 6–7 `[karar K-13]`
· 8 `[spec §6.2]` · 9 `[spec §16.1]` · 10 `[karar K-3]`

---

### A2 · İzin planlamayı ezer

> **v3'te bu senaryo yanlıştı.** Motorun "çözümsüz" demesini bekliyordum.
> Mustafa'nın düzeltmesi: *"İzin tüm planlamayı ezer. Mevzuatta izni olan
> çalışanı çalıştıramıyoruz."* Yani çakışma **oluşamamalı**; oluştuğunda da
> motora hiç gitmemeli.

**Durum — üç ayrı an:**

**(a) İzin önce var, atama sonra deneniyor.** Ayşe'nin Çarşamba onaylı izni
var. Yönetici Çarşamba için Ayşe'yi plana sabitlemeye çalışıyor.

**(b) Atama önce var, izin sonra onaylanıyor.** Plan yayınlanmış, Ayşe Çarşamba
çalışıyor. Ayşe Çarşamba için izin alıyor ve izin onaylanıyor.

**(c) İzin iptal ediliyor.** Ayşe iznini iptal ettiriyor.

**Doğru çalışıyorsa ne olmalı:**

1. **(a)** Yönetici bu sabitlemeyi **yapamaz.** Sistem kabul etmez ve sebebini
   söyler: "Ayşe'nin bu güne onaylı izni var." Uyarı verip devam ettirmez.
2. **(b)** Ayşe **plandan otomatik olarak çıkarılır** — yöneticinin kontrolü
   beklenmez.
3. **(b)** Yöneticiye **bildirim** gider: hangi çalışan, hangi gün, hangi
   plandan düştü.
4. **(b)** Kişi düşünce o hücrede asgari kapsama bozulduysa bu plana **ihlal
   olarak** yazılır ve yönetici görür. Motor çağrılıp boşluk sessizce
   doldurulmaz.
5. **(c)** İzin iptal edilince kişi o güne **yeniden atanabilir** hale gelir.
   İzin kaydı silinmez; **durumu** değişir (`iptal`).
6. **Savunma katmanı:** Motora bir şekilde "izinli kişiye sabit atama" içeren
   bir girdi gelirse, motor **plan üretmez** — girdiyi geçersiz sayar. Arayüz
   engellemesi güvenlik sınırı değildir.

**Dikkat.** 5. madde bir **veri modeli değişikliği** gerektiriyor: `leaves`
tablosuna durum alanı (`talep` / `onayli` / `iptal` / `reddedildi`). Şartname
§8.3'te bu alan yok, v1.4'e girmeli.

6. madde `02-DEGISMEZLER.md`'deki ilkeden geliyor: *"Engelleme ile güvenli
varsayılan farklı şeylerdir. Engellemenin delikleri vardır."* Arayüz
engelliyor, motor da güvenli davranıyor — ikisi birden.

**Kaynak:** 1–5 `[karar K-9]` · 6 `[02-DEGISMEZLER ilkesi]` · kapsama ihlali
yazma biçimi `[çıkarım]`

---

### A3 · İmkânsız durum ve yöneticinin kararı

> **v3'te bu senaryo eksikti.** Motorun "çözümsüz" deyip durmasını
> bekliyordum. Mustafa'nın düzeltmesi: *"Sahada bazı durumlarda imkansızlıklar
> maalesef oluşuyor. Bu tür durumlarda yöneticilere onay ile çözümsüz dahi olsa
> en iyi planı sunmalıyız."*

**Durum.** Firma kuralı: Cuma sahada en az bir ilk yardım sertifikalı kişi
olmalı. Sertifika sadece Zeynep'te. Zeynep gerçekten hasta, Cuma izinli.
Operasyon yine de dönmek zorunda.

**Doğru çalışıyorsa ne olmalı:**

1. Motor **çözümsüz** der ama **elleri boş dönmez**: elindeki **en iyi planı**
   da verir.
2. Yöneticiye net konuşulur: *"Cuma günü ilk yardım kuralı sağlanamıyor. Plan
   bu kural dışında geçerli. Devam etmek istiyor musunuz?"* Hangi gün, hangi
   kural, kaç kişi — hepsi yazılı.
3. Yönetici **"devam et"** derse plan taslak olarak oluşur ve ihlal
   **kabul edilmiş ihlal** olarak kayda geçer: hangi kural, hangi hücre,
   **kimin kabul ettiği**, ne zaman, gerekçesi.
4. Kabul edilmiş ihlal plan ekranında **görünür kalır** — sessizce kaybolmaz.
   Plan "temiz" görünmez.
5. Yönetici **"devam etme"** derse plan oluşmaz.
6. Kabul edilmiş ihlal, **yalnız o hücre için** geçerlidir. Kural haftanın
   geri kalanında yürürlüktedir; Salı'da aynı kural bozulursa o ayrıca ihlal
   olarak çıkar.
7. Yasal dayanaklı kurallar (`yasal=true`) bu yolla kabul **edilemez.**
   İlk yardım kuralı firma kuralıdır, kabul edilebilir; "izinli çalıştırma"
   ya da "11 saat dinlenme" edilemez.

**Dikkat — sorduğun soruya cevap.** *"Kullanıcı plan adımına dönerek ilgili
kriteri bu vardiya planı için esnetse çözülmüyor mu?"*

Çözülür — ama farklı bir şey yapmış olur, ve fark kayıt tarafında:

| | Kuralı plan için gevşetmek | İhlali kabul etmek |
|---|---|---|
| Kural nerede kapanır | **Tüm hafta**, her gün | **Yalnız o hücre** |
| Salı'da fark edilmemiş ikinci bir ihlal | **Sessizce geçer** | Ayrıca çıkar |
| Planda iz | Yok — plan temiz görünür | Kabul edilmiş ihlal, kim onayladı yazılı |
| Altı ay sonra "o hafta neden ilk yardımcı yoktu" | Cevap yok | Cevap var |

İkisi de gerekli, farklı durumlar için. **Gevşetme** = "bu plan gerçekten farklı
koşullarda çalışıyor" (bayram haftası, sezon dışı). **Kabul** = "kural doğru,
ama bugün gerçek onu bozdu" — Zeynep'in durumu bu.

7. madde benim eklemem `[çıkarım]`: yasal kuralların kabul edilememesi. İtiraz
edebilirsin ama tavsiyem tutulması — KVKK/İş Kanunu denetiminde "sistem izin
verdi" savunması yoktur.

**Kaynak:** 1–5 `[karar K-10]` · 6 `[çıkarım]` · 7 `[çıkarım]`

<details><summary>Teknik karşılık</summary>

`/solve` çıktısı `durum: "cozumsuz"` iken de `en_iyi_plan` (atamalar) döner.
`plan_violations` tablosuna yeni durum: `kabul_edildi`, alanları
`kabul_eden_kullanici`, `kabul_zamani`, `gerekce`. §11.3 ve §8.6 v1.4'te
güncellenmeli.
</details>

---

### A4 · Gece yarısını aşan vardiya

**Durum.** Gerçek müşteri verisinden: 3,5 aylık planda **182 atama** gece
yarısını aşıyordu. S-10'a gece vardiyası eklendiğini düşün —
`V-GECE` 16:00–01:00.

| Kişi | Ne yapıyor | Sınanan |
|---|---|---|
| Ali | Salı 16:00–01:00, Çarşamba 09:00–18:00 | 01:00 → 09:00 = **8 saat** dinlenme |
| Burak | Salı 16:00–01:00, Çarşamba 12:00–21:00 | 01:00 → 12:00 = **tam 11 saat** |
| Cem | Salı 16:00–01:00, Çarşamba 00:00–08:00 | **00:00–01:00 çakışıyor** |
| Deniz | Cumartesi 16:00–01:00 | Vardiya Pazar'a taşıyor — hangi güne sayılır |

**Doğru çalışıyorsa ne olmalı:**

1. Ali için **bir** dinlenme ihlali; ölçülen **8 saat**, gereken 11. Dinlenme
   vardiyanın **gerçek bitişinden** ölçülür.
2. Burak **tam 11 saat** dinlenmiştir ve bu **ihlal değildir.** "Asgari 11
   saat" kuralı 11'i kapsar.
3. Cem için **bir** çakışma ihlali. Çakışma mutlak zamanda ölçülür.
4. Ali'nin Salı vardiyası 9 saat sahada / 8 saat çalışmadır ve **Salı'ya**
   sayılır.
5. Deniz'in Cumartesi vardiyası **Cumartesi'ye** sayılır; Pazar'a bir şey
   yazılmaz.
6. **Toplam sert ihlal: 2** (Ali, Cem). Fazlası da eksiği de hata.
7. **Elle müdahale:** Yönetici Ali'nin Çarşamba vardiyasını 09:00'a çekerse
   sistem **uyarır** ("bu değişiklik dinlenme süresini 8 saate düşürür") ve
   karar kullanıcınındır. Kullanıcı devam ederse A3'teki gibi **kabul edilmiş
   ihlal** olarak kayda geçer.

**Dikkat — K-1 geri alındı, ve bu benim hatamdı.**

14 Eylül'de sana şunu sormuştum: *"Tam 11 saat dinlenme ihlal mi?"* Sen "evet
ihlal" dedin ve ben `sinir_dahil` diye bir parametre kurdum. **Soru yanlıştı.**
İki ayrı şeyi tek soruya sıkıştırmıştım:

- *"11,0 saat, 'asgari 11 saat' kuralına uyuyor mu?"* — Bu ürün kararı değil,
  aritmetik. Cevabı evet. Sana sormamalıydım.
- *"Yönetici elle 8 saate düşürürse ne olur?"* — **Bu** ürün kararı, ve senin
  cevabın net: uyar, karar kullanıcının, kayda geç.

Senin bu turdaki sözlerin doğruyu söylüyor: *"Sen çalışanın en son hangi saat
diliminde mesai konduğunu biliyorsun, buna bakarak 11 saat farkla planlama
yapabilirsin; kullanıcı bu farkı manuel 8 saate indirirse uyarı verirsin ve
karar kullanıcının olur."* Tam olarak böyle. Bir şeyi yanlış karar vermedin;
ben teknik bir kenar durumu ürün kararıymış gibi sana yolladım.

**Kaynak:** 1, 3, 4, 5 `[spec §6.3 Z-1…Z-4]` · 2 `[karar K-11]` ·
6 `[çıkarım]` · 7 `[karar K-10, K-11]`

---

### A5 · Yaz saati geçişi — **ERTELENDİ**

**Karar (15 Eylül, K-12).** *"Şu an Türkiye'de bir müşterim dahi yok ve önce bu
pazarda iş yapmalıyım. Bunu ileride çözülebilecek bir alt yapı ile erteleyelim."*

**Bu turda test yazılmıyor.** Numara boş bırakıldı — A6'yı A5 yapmıyorum,
çünkü başka dosyalar bu numaralara atıf yapıyor.

**Ama altyapı kalıyor**, çünkü sonradan eklemenin bedeli yüksek:

1. Kiracı saat dilimi **IANA bölge adıyla** saklanır (`Europe/Istanbul`), sabit
   ofsetle (`+03:00`) değil. Sabit ofset gelirse girdi **reddedilir** (K-2).
2. Bütün süre hesapları **mutlak zamanda** yapılır; yerel saat yalnız gösterim
   ve kural penceresi için.
3. `DST_GECISI` kuralı katalogda **pasif** durur.

Bu üçü A1 ve A4 testleriyle dolaylı olarak korunuyor. DST'li bir ülkede
müşteri açıldığında senaryo buradan devam eder.

**Kaynak:** `[karar K-12]` · altyapı `[spec §6.3, karar K-2]`

---

### A6 · Elle sabitlenmiş atamalar

**Durum.** Müdür üç atamayı elle sabitlemiş, bir kişiye de "Çarşamba vardiya
verme" demiş. Kalan boşlukları motor dolduracak.

**Doğru çalışıyorsa ne olmalı:**

1. Motor planı üretir, sert ihlal yok.
2. **Üç sabit atama çıktıda birebir durur.** Motor "daha iyisini buldum" diye
   değiştiremez.
3. Yasaklı kişiye Çarşamba hiçbir atama yapılmaz.
4. Sabit atamalar yüzünden başka kural bozulmaz.
5. Bu davranış firma tarafından kapatılamaz — sistem kuralıdır.
6. **Sabit atamalar yüzünden plan çözümsüzleşirse** A3 işler: neden çözümsüz
   olduğu anlatılır, en iyi plan sunulur, yönetici kabul edebilir.
7. Yapay zekâ asistanı bu noktada **çözüm önerir**: hangi sabitlemeyi
   kaldırmak, hangi kuralı gevşetmek planı çözer. Öneri sunar, kendisi
   uygulamaz.

**Dikkat.** 6. ve 7. maddeler bu turda eklendi. 7. madde senin sözün:
*"Asistanın fonksiyonlarından biri bu amaca hizmet etmeli — kullanıcıyı
çözümsüz bir planda veya mevcut planda daha iyi sonuç almasını sağlatmak."*
Bu, §12.2'deki "yapay zekâ plan üretmez, açıklar ve önerir" ilkesiyle uyumlu.

**Kaynak:** 1–5 `[spec §6.6, §11.2]` · 6 `[karar K-10]` · 7 `[karar, spec §12.2]`

---

### A7 · Cumartesi adaleti mi, kapsama mı

> **v3'te bu senaryo tamamen yanlış kurulmuştu.** Çalışanların tek tek tercih
> bildirdiğini varsaymıştım. Mustafa'nın düzeltmesi: *"Çalışan bir çalışma
> saati veya vardiyası belirtemez. Sözleşmeden gelir bu kural. Sadece part-time
> çalışanlar için bu kural geçerlidir."* Senaryo baştan yazıldı.

**Durum.** Ekim ayının üçüncü haftası planlanıyor (17 Ekim Cumartesi). Ayın ilk
iki cumartesisinde kimin çalıştığı sistemde kayıtlı:

| Kişi | Bu ay çalıştığı cumartesi |
|---|---|
| Ç01, Ç02, Ç03 | 2 |
| Ç07, Ç10 | 1 |
| Ç04, Ç05, Ç06, Ç08, Ç09 | 0 |

Cumartesi nöbetine 3 kişi gerekiyor. Ç01–Ç03 en deneyimli ve en müsait olanlar;
kapsama açısından en kolay seçim onlar. Ama bu ay zaten iki cumartesi
çalıştılar.

**Doğru çalışıyorsa ne olmalı:**

1. Her iki profil de plan üretir, sert ihlal yok, asgari kapsama %100.
2. **Çalışan odaklı** profil cumartesi yükünü daha dengeli dağıtır: seçilen 3
   kişinin adalet sapması, kapsama odaklı profilin seçiminden **düşüktür**.
3. **Kapsama odaklı** profilin hedef kapsaması, çalışan odaklı profilinkinden
   **düşük değildir**.
4. 2 ve 3'ten **en az biri kesin fark** gösterir. İkisi de eşitse ağırlıklar
   çalışmıyor demektir ve test kırmızı yanar.
5. Adalet **yumuşak** kuraldır: kapsama profilinde Ç01'i üçüncü kez cumartesiye
   koymak **ihlal değildir**, sadece puanı düşürür.
6. Adalet penceresi **takvim ayıdır** ve ayın 1'inde sıfırlanır.

**Dikkat.** Bu senaryonun işi, "üç bakışlı plan önerisi" iddiasının gerçekten
çalıştığını kanıtlamak. Demoda üç kart göstermek kolay; üç kartın **gerçekten
farklı** olması zor. 4. madde tam olarak o farkı zorunlu kılıyor.

Ölçüm biçimi `[çıkarım]`: adalet sapmasını standart sapmayla ölçüyorum
(`07-motor/kurallar.json`'daki yaklaşım). Sahada başka bir ölçü daha anlamlıysa
söyle.

**Ağırlıklar konusundaki önerin zaten kararlı:** Spec §5.4 *"Bu tablo
`plan_profiles` tablosunda tutulur ve **kiracı düzenleyebilir.** Varsayılanlar
spike testlerinde ölçülen değerlerdir"* diyor. Yani istediğin şey — bizim
tablomuz öneri, firma değiştirebilir — zaten tasarımda. Değişiklik gerekmiyor.

**Kaynak:** ağırlıklar `[spec §5.4]` · yön `[spec §16.3]` · adalet penceresi
`[spec §6.5]` · ölçüm `[çıkarım]`

---

### A8 · Öğle arası planlaması

> **v3'te mola "sert kural" gibi anlatılıyordu.** Mustafa'nın düzeltmesi:
> *"Mola öneri gibi düşünmeliyiz. Kişiler molalarını kaydırabilir, bizim
> sistemde tutulmayacak aksiyonlar olabilir ama bu bizi bozmaz. Biz en azından
> bir rehber gibi öneri mantığında mola verisi de hesaplayıp sunuyor olacağız."*

**Durum.** `V-TAM` vardiyası 09:00–18:00, içinde 60 dakika öğle arası. Arası
**12:00–14:00 penceresinde** kullanılabiliyor — mevzuat ve işyeri pratiği böyle.
Gün içinde sahada en az 3 kişi kalmalı.

**Doğru çalışıyorsa ne olmalı:**

1. Öğle arası **vardiya şablonunun parametresidir**: süre (60 dk) + pencere
   (en erken 12:00, en geç bitiş 14:00). Her vardiya tipi kendi arasını
   tanımlar.
2. Mola **tek bloktur, bölünmez.** 60 dakika 30+30 olarak verilemez —
   mevzuat aralıksız veriyor.
3. Motor molaları **pencere içinde kaydırarak** yerleştirir: 6 kişi varsa
   üçü 12:00–13:00, üçü 13:00–14:00 gibi. Sahada hep en az 3 kişi kalır.
4. **Kötü plan denetlenirse** (altı kişinin altısı da 12:00–13:00'te molada)
   ihlal yazılır: o saatte sahada 0 kişi var, 3 olmalıydı.
5. Vardiya süresine göre hak edilen mola verilir: 9 saat sahada → 60 dk;
   4 saatlik `V-CMT` → 15 dk.
6. Mola çalışma süresinden düşülür: `V-TAM` net 8 saat sayılır, 9 değil.
7. **Çıktı öneri niteliğindedir.** Plan ekranında "önerilen mola saati" olarak
   gösterilir; sahada kaydırılması sistemi bozmaz, gerçekleşen veri ayrı
   tutulur.

**Dikkat.** 7. madde ile 4. madde arasında bir gerilim var ve kararı sen
vermelisin: **mola kapsaması sert kural mı, yumuşak mı?**

Benim okumam: **ürettiğimiz plan** kendi içinde tutarlı olmalı — yani motor,
sahada kimsenin kalmayacağı bir mola yerleşimi üretmemeli (4. madde, sert).
Ama sahada kişi molasını kaydırırsa bu bir ihlal sayılmaz, çünkü gerçekleşen
veri ayrı ölçülüyor. Böyle yazdım; farklı düşünüyorsan söyle.

2. madde senin teyidin: *"Öğle arasını bölemeyiz, mevzuatta böyle diyor."*
Bu, v3'teki V-2 varsayımını **karara** dönüştürdü.

**Kaynak:** 1–3, 7 `[karar K-14]` · 2 `[karar, mevzuat]` · 4–6 `[spec §6.2, §6.4]`
· sert/yumuşak yorumu `[çıkarım]`

---

### A9 · Kadro yetmiyor

**Durum.** Üç ayrı durum, üçü de "kadro az" ama sonuçları farklı.

| | Talep (hafta içi) | Sahada ne demek |
|---|---|---|
| **(a)** | asgari 3, **hedef 9** | Asgari rahat tutuyor, hedef tutmuyor |
| **(b)** | **asgari 11** | Kadro 10 kişi; hiçbir gün 11 kişi çıkamaz |
| **(c)** | **asgari 9** | Her gün 9 mümkün, ama hafta toplamı kapasiteyi aşıyor |

**Doğru çalışıyorsa ne olmalı:**

1. **(a)** Motor plan **üretir.** Asgari %100, hedef tutmaz.
2. **(a)** Eksik **dakika cinsinden** raporlanır; hangi hücrede kaç kişi eksik
   olduğu listelenir.
3. **(a)** Motor hedefi kovalamak için fazla mesai tavanını **aşmaz** ve
   kimseye 7 gün üst üste çalışma yazmaz. Eksik kapsama, kural ihlalinden
   iyidir.
4. **(b)** Motor plan **üretmez** — asgariyi karşılamayan plan "çözüldü"
   dönmez. A3 devreye girer: en iyi plan + yönetici kararı.
5. **(b)** Teşhis **hücre** seviyesinde: "11 gerekiyor, en fazla 10 mümkün",
   gevşetme önerisiyle.
6. **(c)** Motor plan üretmez. Teşhis **hafta** seviyesinde: haftalık kişi-gün
   ihtiyacı kapasiteyi aşıyor; engelleyen kural hafta tatili / ardışık çalışma
   sınırı.
7. **(c) bu senaryonun asıl sebebi:** motor hafta toplamını görmezse, her hücre
   tek başına mümkün göründüğü için **birine yedi gün üst üste çalıştıran** bir
   plan üretir. Test o planın üretilmediğini sınıyor.

**Dikkat.** Bu senaryoyu 15 Eylül'de onayladın, kararın geçerli. Tek değişiklik:
4. maddede artık A3'e bağlanıyor — "çözümsüz" demek "hiçbir şey gösterme"
demek değil.

**Kaynak:** ayrım `[karar]` · 1, 4 `[spec §5.3, §11.3]` · 2 `[spec §16.3]` ·
6 `[karar K-7]` · 3, 5, 7 `[çıkarım]`

---

### A10 · Çift tıklama

**Durum.** Müdür "Plan üret"e bastı, sayfa yavaş yüklendi, tekrar bastı.

**Doğru çalışıyorsa ne olmalı:**

1. **Tek plan üretilir.** İkinci istek aynı planın kimliğini döner, motor
   ikinci kez çalışmaz.
2. İlk çalışma sürüyorsa ikinci istek mevcut çalışmanın kimliğini döner.
3. Gerçekten yeni bir plan istenirse (yeni istek anahtarı) yeni plan üretilir.
4. Bu koruma **firmaya özeldir.** B firması aynı anahtarla istek atarsa A'nın
   sonucunu almaz.
5. Denetim kaydında yinelenen istek için ayrı "plan üretildi" izi yoktur.

**Dikkat.** 4. madde artık `[karar]`: *"Kiracılık koruması testi de olmalı."*
Firmalar arası sızıntı bu üründe geri dönülmez hata; diğer 9 kiracılık
koruması gibi bunun da bekçisi olacak.

**Kaynak:** 1–3 `[spec §11.7]` · 4 `[karar]` · 5 `[çıkarım]`

---

### A11 · Geçmiş veri eksik

**Durum.** Firma iki aydır sistemi kullanıyor. Müdür 12 Ekim haftası için plan
istiyor ama **5–11 Ekim haftasının planı sistemde yok.**

**Doğru çalışıyorsa ne olmalı:**

1. İstek motora **gitmez.** Hazırlık kontrolü önce çalışır.
2. Kullanıcıya **hangi tarihlerin eksik olduğu** söylenir: "5–11 Ekim arası
   plan yok."
3. Sistem **çözümü de önerir:** *"Muhtemelen geçen haftanın planı aynen
   uygulandı ama girilmedi — o haftayı kopyalayarak tamamlayabilirsiniz."*
4. Eksik hafta girilince hazırlık geçer, motor çalışır.
5. **Yeni firma farkı:** Sisteme ilk kez giren firmada geçmiş **yoktur**,
   eksik değildir. Motor çalışır, kurallar sıfırdan başlar. İlk planda adalet
   ölçümleri **yapılamaz** — devir yük sıfırdır ve bu normaldir.
6. Ayrım ölçütü: geçmiş penceresi firmanın **ilk yayınlanmış planından**
   öncesine düşüyorsa durum "boş"tur, "eksik" değil.

**Dikkat.** 3. madde senin gözleminden çıktı: *"Muhtemelen bu tür durumlar
geçtiğimiz haftanın planı aynen uygulanmış ama sisteme girilmemiştir. Kullanıcı
bunu kolayca çözebilir."* Hata mesajının çözümü de göstermesi, A12'yi (plan
kopyalama) buraya bağlıyor.

5. maddedeki "ilk planda adalet ölçümü olmaz" ayrıntısı da senin. Bu önemli:
adalet sayacı boşken motorun adalet ağırlığını uygulaması anlamsız, hatta
yanıltıcı olur.

**Kaynak:** 1–2 `[spec §11.2]` · 3, 5 `[karar]` · 4 `[çıkarım]` ·
6 `[karar K-5]`, ölçüt `[çıkarım]`

---

### A12 · Geçen haftanın planını kopyala

**Durum.** Müdür 12 Ekim haftasının planını 26 Ekim haftasına uygulamak
istiyor. Arada bir çalışan işten ayrılmış, bir çalışanın da sözleşmesi bitmiş.

**Doğru çalışıyorsa ne olmalı:**

1. Kopyala seçildiğinde **doğrulayıcı yeniden çalışır** ve yeni tarih
   aralığına göre kontrol eder: pasife düşen çalışan, **süresi biten
   sözleşme**, yeni onaylanmış izinler, değişmiş kural sürümü.
2. Ayrılan kişinin ve sözleşmesi biten kişinin atamaları yeni planda **yok**.
   Diğerlerinin atamaları gün ve saat olarak **aynı**.
3. Düşen atamalar **tek tek listelenir** — hangi kişi, hangi gün, hangi saat,
   **hangi sebeple** (ayrıldı / sözleşme bitti / izin aldı). "1 atama düştü"
   gibi özet yetmez.
4. Kişi düştüğü için bir hücrede asgari kapsama bozulduysa **ihlal olarak
   gösterilir**; motor çağrılıp boşluk sessizce doldurulmaz.
5. Yeni plan **taslak**tır, yayınlanmaz.
6. Kullanıcı doğrudan **plan editörü ekranına** düşer — motordan yeni çıkmış
   bir planla aynı ekran, aynı düzenleme yetkileri. Kopyalama ayrı bir ekran
   değildir.
7. Kaynak plan **hiç değişmez**.
8. Denetim kaydına iz: kaynak plan, hedef aralık, düşen atama sayısı.

**Dikkat.** 1. ve 6. maddeler bu turda senden geldi. 1. maddede bir yorum
yaptım: *"motor tekrar çalışıp"* dedin; ben bunu **doğrulayıcının** çalışması
olarak anladım (kontrol), **çözücünün** yeniden plan üretmesi olarak değil —
çünkü 4. madde "sessizce doldurulmasın" diyor. Yanlış anladıysam söyle.

**Kaynak:** 1, 6 `[karar K-15]` · 2–5 `[spec §9.7]` · 7–8 `[çıkarım]`

---

## 5. Veto edilebilir varsayımlar

v3'teki dördünün ikisi karara dönüştü, ikisi duruyor.

| # | Varsayım | Durum |
|---|---|---|
| ~~V-1~~ | Çakışmada yalnız çakışma ihlali yazılır, ayrıca dinlenme ihlali yazılmaz | Duruyor — veto edebilirsin |
| ~~V-2~~ | Mola tek bloktur | ✅ **Karar oldu** (K-14): *"Öğle arasını bölemeyiz, mevzuatta böyle diyor"* |
| ~~V-3~~ | "Geçmiş yok" ölçütü = ilk yayınlanmış plan | Duruyor — A11 madde 6 |
| **V-4** | Mola hakkı eşiği **brüt** süreye uygulanır | Duruyor, **uzman teyidi gerekli.** Net süreye uygulamak döngüsel; brüt hesap kanunun istediğinden asla az mola vermez |
| **V-5** 🆕 | Yasal dayanaklı kurallar "kabul edilmiş ihlal" yoluyla geçilemez | A3 madde 7 — yeni, senin onayın gerek |
| **V-6** 🆕 | Mola kapsaması plan üretiminde **sert**, sahada gerçekleşen için ölçülmez | A8 madde 7 — yeni |

## 6. Kararlar K-1…K-15

`00-DEVIR/08-URUN-KARARLARI.md`'de gerekçeleriyle. Bu turda eklenenler **kalın**.

| # | Karar | Tarih |
|---|---|---|
| ~~K-1~~ | ~~Sınır değerler ihlal sayılır~~ | **GERİ ALINDI → K-11** |
| K-2 | Saat dilimi IANA adı olmak zorunda, sabit ofset reddedilir | 14 Eyl |
| K-3 | Çözücü istatistikleri çıktıya girer, müşteriye gösterilir | 14 Eyl |
| K-4 | Mola hakkı İş Kanunu'na göre, brüt süreden | 14 Eyl |
| K-5 | Geçmişi olmayan firmada motor çalışır | 14 Eyl |
| K-6 | Sonbahar DST kontrolü ileri tura | 14 Eyl |
| K-7 | Çözümsüzlük teşhisine hafta seviyesi eklenir | 14 Eyl |
| **K-8** | **Hedef kapsama sözü %95, %100 değil** | 15 Eyl |
| **K-9** | **İzin planlamayı ezer;** izinliye atama yapılamaz, sonradan onaylanan izin kişiyi plandan düşürür + bildirim; izin iptali durumu eklenir | 15 Eyl |
| **K-10** | **Yönetici çözümsüz planı kabul edebilir;** en iyi plan sunulur, ihlaller "kabul edilmiş ihlal" olarak kim/ne zaman/neden ile kaydedilir | 15 Eyl |
| **K-11** | **Sınır değer ihlal değil.** "Asgari 11 saat" 11'i kapsar. Elle müdahalede uyarı + kullanıcının kararı + kayıt | 15 Eyl |
| **K-12** | **DST ertelendi;** altyapı (IANA, mutlak zaman, pasif kural) kalır | 15 Eyl |
| **K-13** | **Çalışan tercihi yok.** Uygunluk sözleşmeden gelir; part-time için **sert** kısıt | 15 Eyl |
| **K-14** | **Öğle arası vardiya şablonu parametresi** (süre + pencere), tek blok, çıktı öneri niteliğinde | 15 Eyl |
| **K-15** | **Plan kopyalama** doğrulayıcıyı çalıştırır, sözleşme/izin kontrolü yapar, kullanıcıyı plan editörüne taşır | 15 Eyl |

## 7. Onay nasıl verilir

Senaryo senaryo, üç cevaptan biriyle: **"A3 tamam"** · **"A3'te 4. madde şöyle
olmalı: …"** · **"A3'ten emin değilim, sahayı sorayım"**.

Ayrıca V-1, V-3, V-4, V-5, V-6 için ayrı onay ya da veto.

**Bu turda değişenler öncelikli:** A2, A3, A4 (K-1 geri alındı), A7 (baştan
yazıldı), A8, §3 sahne. A9, A10, A11, A12 zaten onayladın — yalnız bu turda
eklenen maddelere bakman yeterli.

## 8. Onay sonrası

1. Onaylanan cümleler dondurulur; bu dosya `v4` olur.
2. `v4/fikstur/A01.json … A12.json` yazılır. ⚠ v3'teki `A04.json` **geçersiz**
   oldu: T-10 sahnesine dayanıyor ve K-1'e göre yazılmıştı. Biçim örneği olarak
   kalıyor, beklenen sonuçları kullanılmayacak.
3. A1–A9 için pytest, A10–A12 için xUnit. Motor olmadığı için hepsi **kırmızı**
   başlar.
4. `00-DEVIR/04-TEST-HARITASI.md`'ye "Altın senaryolar" bölümü.
5. **Şartname v1.4** — bu turda biriken değişiklikler öncekilerden fazla:
   `leaves` tablosuna durum alanı (K-9), `plan_violations`'a kabul edilmiş ihlal
   (K-10), vardiya şablonuna mola penceresi (K-14), `/solve` çözümsüz çıktısına
   `en_iyi_plan` (K-10), §6.8 `TERCIH_KARSILAMA`'nın yeniden değerlendirilmesi
   (K-13), artı önceki sekiz madde (T-1…T-8).
