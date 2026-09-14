# Altın Senaryolar A1–A12 — Kabul Ölçütleri (v2)

**Durum:** Kararlar işlendi · **cümle onayı bekliyor**
**Tarih:** 14 Eylül 2026
**Önceki sürüm:** `../v1/KABUL-OLCUTLERI.md` — dondurulmuş, değiştirilmedi.
v1 açık sorular (S-1…S-7) sordu; bu sürüm onların cevaplarını içeriyor.
**Kaynak:** Master Spec v1.3 §5, §6, §9.7, §11, §16.3 + 14 Eylül kararları

**v1 → v2 farkı özeti:**

| Ne değişti | Nerede |
|---|---|
| Sınır değerler artık **ihlal** (K-1) ve kural parametresi oldu | A4, A9, §2, §7 |
| A4'te **hatalı bir hesabım düzeltildi** (brüt/net karışmıştı) | A4 |
| A4'e yeni vaka: tam 9 saat **net** günlük sınır | A4 (e) |
| A9'a üçüncü alt durum: **hafta toplamında** yetersizlik | A9 (c) |
| Çözücü istatistikleri sözleşmeye girdi (K-3) | §6, A1, A2, A9 |
| Açık soruların 7'si de kapandı | §5 |

---

## İçindekiler

1. [Nasıl okunur](#1-nasıl-okunur)
2. [Ortak temel veri seti "T-10"](#2-ortak-temel-veri-seti-t-10)
3. [Senaryolar A1–A12](#3-senaryolar)
4. [v1.4'e taşınacak şartname maddeleri](#4-v14e-taşınacak-şartname-maddeleri)
5. [Kapanan kararlar (K-1…K-7)](#5-kapanan-kararlar-k-1k-7)
6. [Yeni sözleşme alanları](#6-yeni-sözleşme-alanları)
7. [Veto edilebilir varsayımlar](#7-veto-edilebilir-varsayımlar)
8. [Onay sonrası ne olacak](#8-onay-sonrası-ne-olacak)

---

## 1. Nasıl okunur

Her senaryoda dört blok var:

| Blok | Ne |
|---|---|
| **Girdi** | Motorun/backend'in alacağı somut veri. T-10 temel setinden farkı yazılır. |
| **Doğru çalışıyorsa ne görmeliyiz** | Türkçe cümle. **Onaylayacağın şey bu.** Test bu cümlenin çevirisidir. |
| **Kaynak** | `[spec §x]` şartnameden · `[karar]` günlüğe yazılmış karar · `[çıkarım]` yapay zekâ türetti, **dikkat** |
| **Katman** | `motor /solve` · `motor /evaluate` · `backend` |

Soru sadece şu: *"Bu cümle doğru mu? Sahada gerçekten böyle mi olmalı?"*
Hayır ya da emin değilim diyorsan cümle yanlıştır, düzeltilir.

A1–A9 motor testi (Python + pytest; motor §7.1 gereği Python + OR-Tools),
A10–A12 backend testi (mevcut xUnit projesi, `04-kod/backend/tests/`).

**Saat gösterimi:** spec §11.2 ile aynı — sayısal ve genişletilmiş.
`25` = ertesi gün 01:00. Gün 0 = Pazartesi. `gun: -1` = önceki Pazar.

---

## 2. Ortak temel veri seti "T-10"

| Alan | Değer |
|---|---|
| Hafta | 2026-10-12 Pazartesi – 2026-10-18 Pazar (gün 0–6) |
| Kiracı saat dilimi | `Europe/Istanbul` (DST yok) |
| Profil | `DENGELI` |
| Çalışanlar | Ç01 … Ç10, hepsi ekip **E1**, operasyonel rol `agent`, yetkinlik yok |
| Sözleşme | tam zamanlı, 45 saat/hafta |
| İzin, uygunluk kısıtı, tercih | yok |
| Geçmiş 14 gün (lookback) | var, **boş** (kimse çalışmamış); yıllık fazla mesai 0; adalet sayaçları 0 |
| Vardiya şablonu | **V-G**: 08:00–16:00 (`bas 8, bit 16`), `mola_dk 60` |
| Talep | E1, her gün (0–6), her saat 08–15: `asgari 3, hedef 5` |
| Sınır davranışı | `sinir_dahil = false` (K-1 varsayılanı) |
| Kurallar | §6 varsayılanları: `GUNLUK_AZAMI 9`, `HAFTALIK_AZAMI 45`, `VARDIYA_ARASI_DINLENME 11`, `HAFTA_TATILI 24/7`, `ARDISIK_CALISMA_GUNU 6`, `CAKISMA_YOK`, `MOLA_HAKKI`, `MOLA_KAPSAMASI`, `ASGARI_KAPSAMA`, `HEDEF_KAPSAMA (9)`, `FAZLA_MESAI_TAVANI 10` |
| Sabit atama, kilit, devir kapsama | yok |

**Kapasite hesabı (programatik doğrulandı):**

| Büyüklük | Değer | Nasıl |
|---|---|---|
| Haftalık kapasite | **60 kişi-gün** | 10 kişi × en çok 6 gün (`HAFTA_TATILI` haftada bir tam gün istiyor) |
| Hedef talep | 35 kişi-gün | 5 kişi × 7 gün |
| Asgari talep | 21 kişi-gün | 3 kişi × 7 gün |
| Kişi başı haftalık | 42 saat net | 6 gün × 7 saat (8 brüt − 60 dk mola) ≤ 45 |
| Günler arası dinlenme | 16 saat | 16:00 bitiş → ertesi 08:00 başlangıç; 16 > 11 |

Yani T-10 rahatça uygulanabilir; fazla mesai gerekmiyor. `[çıkarım]` — hesap
yapay zekânın, onay senin.

**Mola:** V-G 8 saat brüt → `MOLA_HAKKI` >7,5 saat bandı → **60 dk** (K-4).

---

## 3. Senaryolar

### A1 · Basit uygulanabilir

**Katman:** `motor /solve` · **Girdi:** T-10, değişiklik yok.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozuldu"`.
2. `metrikler.sert_ihlal = 0`.
3. `metrikler.asgari_kapsama_yuzde = 100`.
4. `metrikler.hedef_kapsama_yuzde = 100` (kapasite yetiyor).
5. `metrikler.fazla_mesai_saat = 0`.
6. Bağımsız doğrulayıcı (`/evaluate`) aynı planı denetlediğinde **0 sert ihlal**
   bulur. Motorun "0 ihlal" demesi yetmez (§16.1).
7. Hiç kimse 7 gün üst üste çalışmaz; kimseye haftada 45 saatten fazla
   verilmez; kimseye aynı günde iki vardiya verilmez.
8. `cozum_istatistikleri` bloğu dolu gelir: `degisken_sayisi`,
   `kisit_sayisi`, `onarim_denemesi = 0`, `cozum_suresi_sn`. (K-3)

**Kaynak:** 1–3, 5 `[spec §11.3, §16.3]` · 4 `[çıkarım]` · 6 `[spec §16.1]`
· 7 `[spec §6.2]` · 8 `[karar K-3]`

---

### A2 · Çelişkili sert kural

**Katman:** `motor /solve`
**Girdi:** T-10 + Ç01'in gün 2 (Çarşamba) **onaylı izni** (tüm gün) +
`sabit_atamalar`: Ç01, E1, gün 2, 08–16.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozumsuz"`. Motor **plan üretmez** — izne rağmen atayıp "1 ihlal
   var" diyen bir plan kabul edilmez.
2. `teshis.engelleyen_kurallar` içinde `kod = "ONAYLI_IZIN"`, `etkilenen_kisi ≥ 1`.
3. `teshis.hucre` gün 2'yi işaret eder.
4. `cozum_istatistikleri.onarim_denemesi = 2` — motor pes etmeden önce
   §11.7'nin izin verdiği kadar denedi, fazlasını değil. (K-3 bunu ölçülebilir
   yaptı.)

**Kaynak:** 1–2 `[spec §11.3, §16.3]` · 3 `[çıkarım]` · 4 `[spec §11.7 + karar K-3]`

---

### A3 · Kritik yetkinlik açığı

**Katman:** `motor /solve`
**Girdi:** T-10 + yetkinlik `ilkyardim` yalnız **Ç07**'de; kural
`YETKINLIK_KAPSAMASI`: E1, gün 4 (Cuma), 08–15 → `ilkyardim ≥ 1`; Ç07'nin
gün 4 onaylı izni var.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozumsuz"`.
2. `teshis.engelleyen_kurallar` içinde `YETKINLIK_KAPSAMASI`.
3. `teshis.hucre.gun = 4`, `teshis.gereken = 1`, `teshis.mumkun = 0`.
4. **Kontrol çifti:** Ç07'nin izni kaldırılırsa aynı girdi `cozuldu` döner ve
   gün 4'te Ç07 atanmıştır. (§16.4 kırmızı kanıt.)

**Kaynak:** 1–2 `[spec §6.4, §16.3]` · 3 `[spec §11.3]` · 4 `[çıkarım]`

---

### A4 · Gece yarısını aşan vardiya

**Katman:** `motor /evaluate` (plan elle verilir, motor çözmez)

> **Yalıtım:** A4'te talep **yok** ve kapsama kuralları (`ASGARI_KAPSAMA`,
> `HEDEF_KAPSAMA`, `MOLA_KAPSAMASI`) kural listesine konmaz. Amaç yalnız zaman
> modelini sınamak; kapsama gürültüsü ihlal sayımını bozmasın.

**Girdi:** T-10 tabanı + ek şablonlar **V-Akşam** 16:00–01:00 (`bas 16, bit 25`,
mola 60) ve **V-Uzun** 08:00–18:00 (`bas 8, bit 18`, mola 60).

| # | Çalışan | Gün | Saat | Brüt | Net | Ne sınıyor |
|---|---|---|---|---|---|---|
| a | Ç01 | 1 Salı | 16–25 | 9 | 8 | ertesi güne taşan vardiya |
| a | Ç01 | 2 Çar | 9–17 | 8 | 7 | 01:00 → 09:00 = **8 saat** dinlenme |
| b | Ç02 | 1 Salı | 16–25 | 9 | 8 | sınır durumu |
| b | Ç02 | 2 Çar | 12–20 | 8 | 7 | 01:00 → 12:00 = **tam 11 saat** |
| c | Ç03 | 1 Salı | 16–25 | 9 | 8 | mutlak zamanda çakışma |
| c | Ç03 | 2 Çar | 0–8 | 8 | 7 | 00:00–01:00 **örtüşüyor** |
| d | Ç04 | 6 Paz | 16–25 | 9 | 8 | Pazartesi'ye taşma, gün sayımı |
| e | Ç05 | 3 Perş | 8–18 | 10 | **9** | günlük azami **tam sınır** |

*(Tüm süreler ve dinlenmeler programatik doğrulandı.)*

**Doğru çalışıyorsa ne görmeliyiz:**

1. Ç01 için **tam bir** `VARDIYA_ARASI_DINLENME` ihlali; ihlal kaydında
   ölçülen dinlenme **8 saat**, gereken **11**. (Z-4: dinlenme gerçek
   bitişten ölçülür.)
2. Ç02 için dinlenme **tam 11 saat** hesaplanır ve varsayılan ayarda
   (`sinir_dahil = false`) bu **ihlaldir**. Ayar `true` yapılırsa ihlal
   **değildir**. Aynı fikstür iki ayarla koşulur. (K-1)
3. Ç03 için **tam bir** `CAKISMA_YOK` ihlali (Z-3: mutlak zamanda). Örtüşen
   vardiyalar için ayrıca dinlenme ihlali **üretilmez** (bkz. §7 V-1).
4. Ç01'in Salı vardiyası **9 saat brüt / 8 saat net**tir. `GUNLUK_AZAMI` net
   süreye bakar (§6.2) → 8 < 9, ihlal yok. Vardiya **Salı'ya** yazılır (Z-2).
   *(v1'de bu maddeyi brüt üzerinden yazmıştım — yanlıştı, düzeltildi.)*
5. Ç05'in Perşembe vardiyası **tam 9 saat net**tir; varsayılan ayarda
   `GUNLUK_AZAMI` **ihlalidir**, `sinir_dahil = true` ayarında değildir. (K-1)
6. Ç04'ün Pazar vardiyası **Pazar'a** sayılır; gün 7'ye hiçbir şey yazılmaz;
   ihlal yok.
7. Hiçbir atamada `MOLA_HAKKI` ihlali yok — hepsi 60 dk mola taşıyor ve
   hepsinin brütü >7,5 saat.
8. **Toplam sert ihlal sayısı:**

| Ayar | Beklenen | Hangi ihlaller |
|---|---|---|
| `sinir_dahil = false` (varsayılan) | **4** | Ç01 dinlenme · Ç02 dinlenme · Ç03 çakışma · Ç05 günlük |
| `sinir_dahil = true` | **2** | Ç01 dinlenme · Ç03 çakışma |

   Fazlası da eksiği de hata.

**Kırmızı kanıt:** `bit 25`'i "aynı gün 01:00" diye yorumlayan bir doğrulayıcı
Ç01'de 8 saat yerine 32 saat dinlenme görür ve ihlali **kaçırır**. Bu test
tam olarak onu yakalamak için var.

**Kaynak:** 1, 3, 4, 6 `[spec §6.3 Z-1…Z-4, §6.2]` · 2, 5 `[karar K-1]` ·
7 `[spec §6.2]` · 8 `[çıkarım]` (sayım)

---

### A5 · DST geçiş haftası

**Katman:** `motor /evaluate`
**Girdi:** T-10 tabanı, kiracı saat dilimi **`Europe/Berlin`**, `DST_GECISI`
kuralı **aktif**. Hafta **2027-03-22 Pzt – 2027-03-28 Paz**. 28 Mart 2027
Pazar 02:00'de saat 03:00'e alınır; o gün **23 saat** sürer.
*(28 Mart 2027'nin Pazar olduğu ve gün uzunlukları IANA verisiyle doğrulandı.)*

| # | Çalışan | Gün | Yerel saat | Gerçek süre | Ne sınıyor |
|---|---|---|---|---|---|
| a | Ç01 | 5 Cmt 27 Mart | 22:00 → 07:00 | **8 saat** | geçiş gecesi vardiya süresi |
| b | Ç02 | 5 Cmt | 15:00 – 23:00 | 8 saat | — |
| b | Ç02 | 6 Paz 28 Mart | 10:00 – 18:00 | 8 saat | 23:00 → 10:00 duvar saatiyle 11, gerçekte **10** |
| c | Ç03 | 6 Paz | 08:00 – 16:00 | 8 saat | geçiş günü sıradan vardiya |

**Doğru çalışıyorsa ne görmeliyiz:**

1. Ç01'in gece vardiyası **8 saat brüt** sayılır, 9 değil — 02:00–03:00 arası
   hiç yaşanmadı. Süre **mutlak zamanda** ölçülür (Z-6).
2. Ç02 için `VARDIYA_ARASI_DINLENME` ihlali **var**: ölçülen dinlenme
   **10 saat**. Duvar saatine bakan bir doğrulayıcı 11 görür ve kaçırır — bu
   testin asıl amacı. *(Not: 11 görse bile varsayılan ayarda yine ihlal
   olurdu; bu yüzden test hem ihlalin varlığını hem **ölçülen değerin 10
   olduğunu** ayrıca sınar. Yoksa yanlış sebeple yeşil yanar.)*
3. Ç03'ün Pazar vardiyası **8 saat**; ihlal yok.
4. **Kontrol çifti:** aynı fikstür `Europe/Istanbul` ile koşulursa Ç02'nin
   dinlenmesi **11 saat** ölçülür (Türkiye'de DST yok, gün 24 saat). Farkın
   gerçekten saat diliminden geldiğinin kanıtı.
5. Kiracı saat dilimi sabit ofsetle (`+01:00`) verilirse girdi **reddedilir**,
   şema hatası döner. Uyarıyla geçilmez. (K-2)

**Ertelendi (K-6):** sonbahar geçişi (31 Ekim 2027, gün 25 saat; Cmt 22:00 →
Paz 07:00 = 10 saat) ileri bir tura bırakıldı.

**Kaynak:** 1–3 `[spec §6.3 DST, Z-6; 02-DEGISMEZLER G-6]` · 4 `[çıkarım]` ·
5 `[karar K-2]`

---

### A6 · Kilitli revizyon

**Katman:** `motor /solve`
**Girdi:** T-10 + `sabit_atamalar`: Ç01 gün 0 08–16 · Ç02 gün 3 08–16 ·
Ç03 gün 6 08–16. `kilitler`: Ç04 gün 2 `tip: yasak`.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozuldu"`, `sert_ihlal = 0`.
2. Çıktıdaki atamalar arasında **üç sabit atama birebir** vardır (aynı
   çalışan, ekip, gün, saat).
3. Ç04'e gün 2'de **hiçbir** atama yoktur.
4. Sabit atamalar yüzünden başka kural bozulmaz: Ç01–Ç03'ün haftası 45 saat
   altında ve hafta tatili var.
5. `KILIT_UYUMU` kapsamı `S` (sistem) olduğu için kiracı bunu kapatamaz:
   kural listesinde gönderilmese bile davranış aynıdır.

**Kaynak:** 1–3 `[spec §6.6, §11.2, §16.3]` · 4 `[çıkarım]` · 5 `[spec §6
kapsam sütunu]`, yorum `[çıkarım]`

---

### A7 · Yumuşak hedef çatışması

**Katman:** `motor /solve` — iki çağrı, aynı girdi, farklı profil
**Girdi:** T-10 +
- İkinci şablon **V-Akşam2**: 14:00–22:00 (`bas 14, bit 22`, mola 60).
- Talep (T-10'unkinin **yerine**), hafta içi (gün 0–4): 08–13 `asgari 2,
  hedef 3`; 14–21 `asgari 2, hedef 5`. Hafta sonu talep yok.
- Tercih: Ç01–Ç08 her hafta içi günü **08–16 tercih ediyor** (`agirlik 3`).
  Ç09, Ç10'un tercihi yok.
- Çağrı 1: `profil = "KAPSAMA"` · Çağrı 2: `profil = "CALISAN"`.

Çatışma: akşam hedefi 5 kişi; tercihsiz yalnız 2 kişi var. Hedefi doldurmak
için tercihli kişiler akşama alınmalı. `KAPSAMA` (hedef 20, tercih 1) bunu
yapar; `CALISAN` (hedef 5, tercih 9) yapmaz, akşamı asgaride bırakır.

**Doğru çalışıyorsa ne görmeliyiz:**

1. İki çağrı da `cozuldu`, `sert_ihlal = 0`, asgari kapsama %100.
2. `hedef_kapsama_yuzde(KAPSAMA) ≥ hedef_kapsama_yuzde(CALISAN)`.
3. `tercih_karsilama_yuzde(CALISAN) ≥ tercih_karsilama_yuzde(KAPSAMA)`.
4. 2 ve 3'ten **en az biri kesin büyük**. İkisi de eşitse ağırlıklar hiçbir
   şey değiştirmiyor demektir → test kırmızı yanar.
5. Tercih hiçbir çağrıda sert kısıt gibi davranmaz: `KAPSAMA` çağrısında
   tercihli birinin akşama atanması **ihlal sayılmaz**.

**Kaynak:** ağırlıklar `[spec §5.4]` · yön `[spec §16.3]` · ölçüm biçimi
`[çıkarım]`. `tercih_karsilama_yuzde` metriği §11.3'te **yok**, eklenmeli (T-3).

---

### A8 · Mola kapsaması

**Katman:** `/evaluate` (a, b) + `/solve` (c)
**Girdi:** T-10 tabanı; talep tek gün (gün 0), 08–15 her saat `asgari 3,
hedef 4`. Vardiya V-G (08–16, mola 60).

- **(a) Kötü plan:** Ç01–Ç04 gün 0 08–16, **dördünün molası da 12:00–13:00**.
- **(b) İyi plan:** aynı dört kişi; molalar 11–12, 12–13, 13–14, 14–15.
- **(c) `/solve`:** aynı talep, molaları motor yerleştirsin.

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) `MOLA_KAPSAMASI` ihlali **var**: 12:00–13:00 hücresinde sahada 0 kişi,
   asgari 3. Tam bir ihlal, o saate işaret eder.
2. (b) Sert ihlal **0**: her saatte sahada ≥ 3 kişi kalıyor.
3. (b) Her atamada **60 dk** mola var (`MOLA_HAKKI`, brüt 8 saat > 7,5 → 60).
   30 dk verilseydi `MOLA_HAKKI` ihlali olurdu. (K-4)
4. (c) `cozuldu`, sert ihlal 0; çıktıda her atamanın `molalar` alanı dolu;
   mola düşüldükten sonra hiçbir saatte sahadaki kişi 3'ün altına inmiyor.
   Bunu **doğrulayıcı ayrıca sayar**; motorun metriğine güvenilmez.
5. Mola çalışma süresinden düşülür: 4 kişi × 7 saat net = günlük 28 saat,
   32 değil.
6. Her kişinin molası **tek blok**tur, parçalanmaz. (Molaların kişiler arası
   kaydırılması serbest; bir kişinin molasının bölünmesi ayrı bir konu —
   bkz. §7 V-2.)

**Kaynak:** 1–5 `[spec §6.2, §6.4, §16.3; karar K-4]` · 6 `[çıkarım]`

---

### A9 · Kısmi kapasite

**Karar K-5 (14 Eylül):** Ayrıştırıldı. **Asgari** karşılanamıyorsa
`cozumsuz` + teşhis (§11.3). **Yalnız hedef** karşılanamıyorsa `cozuldu` +
eksik raporu. K-7 sayesinde teşhisin artık **hafta toplamı** seviyesi de var,
bu yüzden üçüncü alt durum eklendi.

**Katman:** `motor /solve`, üç fikstür.

| Alt durum | Talep | Neden böyle | Beklenen |
|---|---|---|---|
| **(a)** hedef yetmiyor | `asgari 3, hedef 9` | hedef 63 kişi-gün > 60 kapasite; asgari 21 rahat | `cozuldu` |
| **(b)** hücre imkânsız | `asgari 11, hedef 11` | kadro 10; hiçbir gün 11 kişi çıkamaz — **tek hücrede** görülür | `cozumsuz`, teşhis `kapsam: "hucre"` |
| **(c)** hafta toplamı yetmiyor | `asgari 9, hedef 9` | 9 ≤ 10 olduğu için **her hücre tek başına mümkün**; ama 63 > 60 → hafta tutmaz | `cozumsuz`, teşhis `kapsam: "hafta"` |

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) `durum = "cozuldu"`, `sert_ihlal = 0`, `asgari_kapsama_yuzde = 100`,
   `hedef_kapsama_yuzde < 100`.
2. (a) Eksik **dakika cinsinden** raporlanır: `metrikler.eksik_hedef_dakika > 0`,
   ve hangi hücrede kaç kişi eksik olduğu listelenir.
3. (a) Motor hedefi kovalamak için `FAZLA_MESAI_TAVANI`'nı (10 saat/kişi)
   **aşmaz** ve kimseye 7 gün üst üste vermez.
4. (b) `durum = "cozumsuz"`. **Asgariyi karşılamayan plan asla `cozuldu`
   dönmez.**
5. (b) `teshis.kapsam = "hucre"`, `teshis.gereken = 11`, `teshis.mumkun ≤ 10`;
   `gevsetme_denemeleri` içinde `ASGARI_KAPSAMA` için en az bir deneme var.
   *(`engelleyen_kurallar` burada boş olabilir — engelleyen bir kural değil,
   kadro sayısıdır. Test bunu zorunlu tutmaz.)*
6. (c) `durum = "cozumsuz"`, `teshis.kapsam = "hafta"`, `gereken = 63`
   kişi-gün, `mumkun = 60`; `engelleyen_kurallar` içinde `HAFTA_TATILI`
   ve/veya `ARDISIK_CALISMA_GUNU` var.
7. (c) **Kırmızı kanıt — bu senaryonun asıl sebebi:** motor hafta toplamını
   görmezse, tek tek hücreler mümkün göründüğü için birine 7 gün üst üste
   çalıştıran bir plan üretir. O plan doğrulayıcıdan `HAFTA_TATILI` ihlaliyle
   döner. Test bunun **plan olarak dönmediğini**, `cozumsuz` döndüğünü sınar.

**Kaynak:** ayrım `[karar K-5]` · hafta seviyesi `[karar K-7]` · 1, 4
`[spec §5.3, §11.3]` · 2 `[spec §16.3]`, alan adı `[çıkarım]` · 3, 5, 6, 7
`[çıkarım]` (kapasite hesabı programatik doğrulandı)

---

### A10 · Aynı istek iki kez

**Katman:** `backend` (xUnit; motor yerine çağrı sayan bir taklit)
**Girdi:** Plan üretme ucuna aynı `istek_anahtari = "K1"` ile ardışık iki istek.

| Alt durum | Kurgu |
|---|---|
| (a) Bitmiş | İlk istek tamamlandı, ikinci istek geliyor |
| (b) Sürüyor | İlk istek kuyrukta/çalışıyor, ikinci istek geliyor |
| (c) Farklı anahtar | Aynı girdi, `istek_anahtari = "K2"` |

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) İkinci istek **aynı `plan_runs` kimliğini** döner; motor taklidi **tam
   1 kez** çağrılmıştır; `plan_runs`'ta o kiracı için **tek** satır vardır.
2. (b) İkinci istek mevcut çalışmanın kimliğini döner, ikinci çalışma
   başlatılmaz; motor taklidi 1 kez çağrılmış.
3. (c) Farklı anahtar → yeni çalıştırma, ikinci `plan_runs` satırı, motor
   2 kez çağrılmış. (Anahtarın gerçekten anahtar olduğunun kanıtı.)
4. Anahtar **kiracıya özeldir**: B kiracısı aynı `"K1"` ile isteyince A'nın
   sonucunu almaz, kendi çalıştırmasını başlatır.
5. Denetim kaydında yinelenen istek için ayrı bir "plan üretildi" izi yoktur.

**Kaynak:** 1–3 `[spec §11.7, §16.3]` · 4 `[çıkarım]` (02-DEGISMEZLER K-1'in
sonucu) · 5 `[çıkarım]`

---

### A11 · Lookback eksik

**Katman:** `backend` hazırlık kontrolü (motor çağrılmadan önce)
**Girdi:** Kiracı 6 aydır sistemde, planlanan hafta 2026-10-12. Önceki 14
günün atamaları **kısmen yok**: 28 Eylül – 4 Ekim planı var, **5–11 Ekim
için hiç plan yok**.

**Doğru çalışıyorsa ne görmeliyiz:**

1. Plan üretme isteği motora **gitmez**; motor taklidi 0 kez çağrılmış.
2. Hazırlık cevabında `eksik_veri` listesinde `tip = "lookback_atamalar"` ve
   eksik aralık **5–11 Ekim** olarak yazılı.
3. Kullanıcıya gösterilen mesaj eksik aralığı **günleriyle** söyler; "veri
   eksik" demekle yetinmez.
4. 5–11 Ekim planı yayınlanınca hazırlık geçer ve motor 1 kez çağrılır.
   (Kontrol çifti.)
5. **Yeni kiracı farkı (K-5):** kiracının hiç geçmişi yoksa hazırlık
   **engellemez**, motor çalışır. Ayrım ölçütü: lookback penceresi kiracının
   ilk yayınlanmış planından öncesine düşüyorsa bu **"boş"**tur, "eksik"
   değil. O çalıştırmanın `plan_runs` kaydına "geçmişsiz başlangıç" notu
   düşülür.

**Kaynak:** 1–2 `[spec §11.2]` · 3–4 `[çıkarım]` · 5 `[karar K-5]`, ayrım
ölçütü `[çıkarım]` (bkz. §7 V-3)

---

### A12 · Plan kopyalama

**Katman:** `backend`
**Girdi:** 2026-10-12 haftası için **yayınlanmış** plan; T-10'un 10 çalışanının
her birinin en az bir ataması var. Sonra **Ç03 pasife alınır**. Kullanıcı planı
**2026-10-26 haftasına** kopyalar.

**Doğru çalışıyorsa ne görmeliyiz:**

1. Yeni plan `taslak` durumundadır, yayınlanmamıştır.
2. Yeni planda Ç03'e ait **hiç** atama yoktur; diğer 9 kişinin atamaları gün
   ve saat olarak **aynı**dır (tarih 14 gün kaymış).
3. Cevaptaki `dusen_atamalar` listesi Ç03'ün düşen atamalarını **tek tek**
   (gün + saat) sayar. Boş liste dönmez; "1 atama düştü" gibi özet yetmez.
4. Kopya **doğrulayıcıdan geçer** ve sonucu taslağa yazılır: Ç03 düşünce bir
   hücrede asgari kapsama bozulduysa bu **ihlal olarak listelenir**; motor
   çağrılıp sessizce doldurulmaz.
5. Kaynak plan **hiç değişmez**.
6. Denetim kaydında "plan kopyalandı" izi: kaynak plan, hedef aralık, düşen
   atama sayısı.

**Kaynak:** 1–4 `[spec §9.7, §16.3]` · 5–6 `[çıkarım]`

---

## 4. v1.4'e taşınacak şartname maddeleri

**v1.3 dosyasına dokunulmaz** (versiyonlama kuralı). Aşağıdakiler yeni sürümde.

| # | Nerede | Ne | Ne yazılacak |
|---|---|---|---|
| T-1 | §16.2 ↔ §16.3 | "on senaryo" yazıyor, tablo 12 satır | "on iki (A1–A12)" |
| T-2 | §16.3 A9 ↔ §6.4 + §11.3 | A9 "sert ihlal üretmez" der, `ASGARI_KAPSAMA` sert | K-5: asgari → `cozumsuz`, hedef → raporla |
| T-3 | §11.2 örnek ↔ §6.2 | 08–16 vardiya için örnekte `mola_dk 30`, tabloya göre 60 | Örnek 60'a çekilsin (K-4) |
| T-4 | §11.3 metrikler | `tercih_karsilama_yuzde`, `eksik_hedef_dakika`, `cozum_istatistikleri` yok | §6'daki alanlar eklensin |
| T-5 | §11.3 teşhis | Yalnız hücre bazlı | K-7: `kapsam: "hucre" \| "hafta"` eklensin |
| T-6 | §5, §6 | Sınır davranışı tanımsız | K-1: `sinir_dahil` parametresi, kural metni ekranda açık yazılsın |
| T-7 | §6.3, §8.1 | IANA zorunluluğu yazıyor ama ihlalinde ne olacağı yazmıyor | K-2: sabit ofset **reddedilir** |
| T-8 | §11.2 | Yeni kiracıda lookback | K-5: geçmişsiz başlangıç tanımı |

## 5. Kapanan kararlar (K-1…K-7)

Hepsi **14 Eylül 2026, Mustafa**. v1 §5'teki S-1…S-7 sorularının cevapları.

| # | Karar | Sonucu |
|---|---|---|
| **K-1** | **Sınır değer ihlaldir.** Tam 11 saat dinlenme, tam 9 saat günlük → ihlal. Ama bu **firma kararıdır**, kural tanımında esnek bırakılır. | Her eşikli kurala `sinir_dahil` parametresi (varsayılan `false` = sınır ihlal). Bu, §5.1'in "kural tipi kodda, kural değeri veride" ilkesiyle uyumlu: sınır davranışı bir **değer**dir. A4 iki ayarla da koşulur. |
| **K-2** | **Sabit ofset reddedilir.** | Kiracı saat dilimi IANA adı değilse girdi şema hatası verir; uyarıyla geçilmez. A5 madde 5. |
| **K-3** | **Çözücü istatistikleri çıktıya girer** — ve müşteriye gösterilebilir ("17.000 değişken üzerinden çözüldü"). | `cozum_istatistikleri` bloğu: `degisken_sayisi`, `kisit_sayisi`, `onarim_denemesi`, `cozum_suresi_sn`, `incelenen_dugum`. A2 madde 4 bunu ölçülebilir yaptı. |
| **K-4** | **İş Kanunu'na uyulur** (mola hakkı). | Mola hakkı **brüt vardiya süresine** göre hesaplanır. Gerekçe §7 V-4'te. |
| **K-5** | **Geçmişi olmayan kiracıda motor çalışır.** | A11 madde 5. "Eksik" ile "hiç yok" ayrılır. |
| **K-6** | Sonbahar DST kontrolü **ileri tura**. | A5'ten çıkarıldı, kayıtta duruyor. |
| **K-7** | **Hafta seviyesi teşhis eklensin.** | `teshis.kapsam` alanı; A9(c) bu sayede yazılabildi. |

### K-1 hakkında bilmen gereken tek şey

Varsayılan "sınır ihlal" olduğunda, ekranda `GUNLUK_AZAMI: 9` yazan parametre
fiilen **"en çok 8 saat 59 dakika"** anlamına gelir — 9 saatlik bir vardiya
kurulamaz. Aynısı dinlenmede tersine işler: `11` yazar, fiilen 11 saat 1 dakika
ister.

Bu **yasal olarak güvenlidir** (kanun bir taban/tavan koyar, firma daha sıkı
davranabilir; gevşek davranamaz). Bedeli iki yerde çıkar: planlar daha zor
çözülür, `cozumsuz` sayısı artar; ve kullanıcı "9 yazdım ama 9 saat vardiya
kuramıyorum" der.

**Önerim:** kararın kalsın, ama kural ekranında parametrenin yanında cümle
**açıkça** yazılsın — *"11 saat ve altı dinlenme ihlaldir"* / *"11 saatten az
dinlenme ihlaldir"*. Böylece sayı hiçbir zaman sessizce başka bir şey demez.
Fikrini değiştirirsen tek satırlık bir varsayılan değişikliği.

## 6. Yeni sözleşme alanları

K-3, K-5, K-7 ve A7/A9 için §11.3 çıktısına eklenmesi gerekenler:

```json
{
  "metrikler": {
    "tercih_karsilama_yuzde": 82.4,
    "eksik_hedef_dakika": 10800
  },
  "cozum_istatistikleri": {
    "degisken_sayisi": 17412,
    "kisit_sayisi": 38905,
    "onarim_denemesi": 0,
    "incelenen_dugum": 214880,
    "cozum_suresi_sn": 47
  },
  "teshis": {
    "kapsam": "hafta",
    "gereken": 63,
    "mumkun": 60
  }
}
```

**K-3 için bir uyarı:** bu sayılar modelin kuruluşuna bağlıdır — motor
iyileştirildiğinde değişken sayısı **düşebilir**. Müşteriye gösterilmesi güzel,
ama satış materyaline sabit bir rakam ("17.000 değişken") yazılırsa bir sonraki
sürümde yanlış olur. Ekranda **o çalıştırmanın gerçek sayısı** gösterilmeli,
broşürde sabit sayı değil.

## 7. Veto edilebilir varsayımlar

Bunları ben türettim. İtiraz etmezsen fikstürlere böyle girerler.

| # | Varsayım | Gerekçe |
|---|---|---|
| **V-1** | Örtüşen iki vardiyada **yalnız** `CAKISMA_YOK` ihlali üretilir; ayrıca dinlenme ihlali yazılmaz. | Tek hata iki satır üretirse ihlal sayısı anlamını yitirir ve kullanıcı aynı sorunu iki kez düzeltmeye çalışır. |
| **V-2** | Bir kişinin molası **tek blok**tur. Kişiler arası kaydırma serbest. | İş Kanunu md. 68 ara dinlenmenin aralıksız verilmesini esas alır; bölünmesi sözleşmeye bağlıdır. Ürün varsayılanı tek blok olsun, bölme sonra parametre olur. |
| **V-3** | "Geçmiş yok" ölçütü: lookback penceresi kiracının **ilk yayınlanmış planından** öncesine düşüyorsa boştur. | Nesnel ve test edilebilir. Alternatifi (kiracı oluşturma tarihi) yanıltıcı: kiracı 3 ay önce açılıp yeni plan yapmaya başlamış olabilir. |
| **V-4** | `MOLA_HAKKI` eşiği **brüt** vardiya süresine uygulanır (08–16 = 8 saat → 60 dk). | K-4 "İş Kanunu'na uyalım" dedi. Net süreye uygulamak **döngüsel**dir: net süre molaya, mola net süreye bağlı olur. Brüt her zaman net'ten büyük ya da eşit ve eşik tablosu artan olduğu için, brüt hesap kanunun istediğinden **asla az** mola vermez. Yani hem belirli hem güvenli taraf. **Bu bir hukuki yorumdur; ben avukat değilim, uzman teyidi alınmalı.** |

## 8. Onay sonrası ne olacak

1. Onaylanan cümleler **değişmez**; bu dosya `v2` olarak dondurulur.
2. `v2/fikstur/A01.json … A12.json` yazılır: §11.2 şemasında girdi +
   `beklenen` bloğu. **Uygulamadan bağımsız** — motor hangi dille yazılırsa
   yazılsın aynı dosyalar koşar. Örnek olarak `A04.json` şimdiden yazıldı,
   biçimi görmek için.
3. A1–A9 için pytest iskeleti: fikstürü okur, `/solve` ya da `/evaluate`
   çağırır, `beklenen`i sınar. Motor olmadığı için **hepsi kırmızı** başlar —
   istenen durum bu (§16.4 kırmızı kanıt). Motor yazıldıkça yeşile döner.
4. A10–A12 için xUnit testleri, plan ve `plan_runs` tabloları geldiğinde.
5. `04-TEST-HARITASI.md`'ye "Altın senaryolar" bölümü; her satır bu dosyadaki
   cümleye bağlı.
6. §4 ve §5 → `02-spec/v1.4-master-spec.md`.
