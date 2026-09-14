# Altın Senaryolar A1–A12 — Kabul Ölçütleri (v1)

**Durum:** TASLAK — Mustafa'nın onayını bekliyor
**Tarih:** 14 Eylül 2026
**Kaynak:** Master Spec v1.3 §5, §6, §9.7, §11, §16.3
**Kural:** Bu dokümandaki hiçbir beklenen sonuç motorun ürettiğine bakılarak
yazılmadı; motor yok. Hepsi şartnameden türetildi. Onaylandıktan sonra
JSON fikstürler ve testler bu cümlelerin **çevirisi** olacak.

> **Bu dosya ne DEĞİL:** test kodu değil, fikstür değil. Onay dokümanıdır.
> Onaylanan cümleler değişmez; değişmesi gerekirse v2 açılır.

---

## İçindekiler

1. [Nasıl okunur](#1-nasıl-okunur)
2. [Ortak temel veri seti "T-10"](#2-ortak-temel-veri-seti-t-10)
3. [Senaryolar](#3-senaryolar)
   - [A1 · Basit uygulanabilir](#a1--basit-uygulanabilir)
   - [A2 · Çelişkili sert kural](#a2--çelişkili-sert-kural)
   - [A3 · Kritik yetkinlik açığı](#a3--kritik-yetkinlik-açığı)
   - [A4 · Gece yarısını aşan vardiya](#a4--gece-yarısını-aşan-vardiya)
   - [A5 · DST geçiş haftası](#a5--dst-geçiş-haftası)
   - [A6 · Kilitli revizyon](#a6--kilitli-revizyon)
   - [A7 · Yumuşak hedef çatışması](#a7--yumuşak-hedef-çatışması)
   - [A8 · Mola kapsaması](#a8--mola-kapsaması)
   - [A9 · Kısmi kapasite](#a9--kısmi-kapasite)
   - [A10 · Aynı istek iki kez](#a10--aynı-istek-iki-kez)
   - [A11 · Lookback eksik](#a11--lookback-eksik)
   - [A12 · Plan kopyalama](#a12--plan-kopyalama)
4. [Şartnamede bulunan tutarsızlıklar](#4-şartnamede-bulunan-tutarsızlıklar)
5. [Mustafa'nın karar vermesi gereken açık sorular](#5-mustafanın-karar-vermesi-gereken-açık-sorular)
6. [Onay sonrası ne olacak](#6-onay-sonrası-ne-olacak)

---

## 1. Nasıl okunur

Her senaryoda dört blok var:

| Blok | Ne |
|---|---|
| **Girdi** | Motorun/backend'in alacağı somut veri. T-10 temel setinden farkı yazılır. |
| **Doğru çalışıyorsa ne görmeliyiz** | Türkçe cümle. **Onaylayacağın şey bu.** Test bu cümlenin çevirisidir. |
| **Kaynak** | `[spec §x]` şartnameden · `[karar]` günlüğe yazılmış karar · `[çıkarım]` yapay zekâ türetti, **dikkat** |
| **Hangi katman** | `motor /solve` · `motor /evaluate` · `backend` |

Soru sadece şu: *"Bu cümle doğru mu? Sahada gerçekten böyle mi olmalı?"*
Hayır ya da emin değilim diyorsan cümle yanlıştır, düzeltilir.

Senaryoların 9'u (A1–A9) motor testi, 3'ü (A10–A12) backend testi. Motor
Python + OR-Tools (spec §7.1), o yüzden A1–A9 pytest ile; A10–A12 mevcut
xUnit projesinde (`04-kod/backend/tests/`) koşacak.

**Saat gösterimi:** spec §11.2 ile aynı — sayısal ve genişletilmiş.
`25` = ertesi gün 01:00. Gün 0 = Pazartesi. `gun: -1` = önceki Pazar.

---

## 2. Ortak temel veri seti "T-10"

Senaryoların çoğu bu setten başlar, yalnız farkı belirtir.

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
| Kurallar | §6 varsayılanları: `GUNLUK_AZAMI 9`, `HAFTALIK_AZAMI 45`, `VARDIYA_ARASI_DINLENME 11`, `HAFTA_TATILI 24/7`, `ARDISIK_CALISMA_GUNU 6`, `CAKISMA_YOK`, `MOLA_HAKKI`, `MOLA_KAPSAMASI`, `ASGARI_KAPSAMA`, `HEDEF_KAPSAMA (9)`, `FAZLA_MESAI_TAVANI 10` |
| Sabit atama, kilit, devir kapsama | yok |

**Neden bu set uygulanabilir (elle hesap):** hedef 5 kişi × 7 gün = 35
kişi-gün. 10 kişi × en çok 6 gün (hafta tatili) = 60 kişi-gün kapasite.
Kişi başı 5 gün × 7 saat net (8 brüt − 1 mola) = 35 saat < 45. Fazla mesai
gerekmiyor. `[çıkarım]` — hesap yapay zekânın, onaylanmalı.

> **Mola notu:** V-G 8 saat brüt. §6.2 `MOLA_HAKKI` tablosu ">7,5 saat → 60
> dk" der; bu yüzden `mola_dk 60`. Spec §11.2 örneğinde aynı vardiya için
> `mola_dk 30` yazıyor — bkz. §4 tutarsızlık T-2.

---

## 3. Senaryolar

### A1 · Basit uygulanabilir

**Katman:** `motor /solve`
**Girdi:** T-10, değişiklik yok.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozuldu"`.
2. `metrikler.sert_ihlal = 0`.
3. `metrikler.asgari_kapsama_yuzde = 100`.
4. `metrikler.hedef_kapsama_yuzde = 100` (kapasite yettiği için).
5. `metrikler.fazla_mesai_saat = 0`.
6. Bağımsız doğrulayıcı (`/evaluate`) aynı planı denetlediğinde **0 sert ihlal**
   bulur. (Motorun "0 ihlal" demesi yetmez; §16.1.)
7. Hiçbir çalışan 7 gün üst üste çalışmaz; hiç kimseye haftada 45 saatten
   fazla verilmez; hiç kimseye aynı günde iki vardiya verilmez.

**Kaynak:** 1–3, 5 `[spec §11.3, §16.3]` · 4 `[çıkarım]` (kapasite hesabından)
· 6 `[spec §16.1]` · 7 `[spec §6.2]`

---

### A2 · Çelişkili sert kural

**Katman:** `motor /solve`
**Girdi:** T-10 +
- Ç01'in **onaylı izni** var: gün 2 (Çarşamba), tüm gün.
- **Sabit atama** (`sabit_atamalar`): Ç01, E1, gün 2, 08–16.

İkisi aynı anda sağlanamaz: zorunlu atama ile onaylı izin aynı gün.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozumsuz"`. Motor **plan üretmez** — izne rağmen atayıp "1 ihlal
   var" diyen bir plan **kabul edilmez**.
2. `teshis.engelleyen_kurallar` listesinde `kod = "ONAYLI_IZIN"` var ve
   `etkilenen_kisi ≥ 1`.
3. `teshis.hucre` gün 2'yi işaret eder.
4. Onarım döngüsü (§11.7) en fazla 2 deneme yapar; sonuç yine `cozumsuz`.
   *(Bu madde motorun deneme sayısını dışarı vermesini gerektirir — açık soru S-3.)*

**Kaynak:** 1–2 `[spec §11.3, §16.3]` · 3 `[çıkarım]` · 4 `[spec §11.7]`

---

### A3 · Kritik yetkinlik açığı

**Katman:** `motor /solve`
**Girdi:** T-10 +
- Yetkinlik `ilkyardim` yalnız **Ç07**'de var.
- Kural `YETKINLIK_KAPSAMASI`: E1, gün 4 (Cuma), saat 08–15 → `ilkyardim ≥ 1`.
- Ç07'nin gün 4 **onaylı izni** var (tüm gün).

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozumsuz"`.
2. `teshis.engelleyen_kurallar` içinde `YETKINLIK_KAPSAMASI` var.
3. `teshis.hucre.gun = 4`, `teshis.gereken = 1`, `teshis.mumkun = 0`.
4. **Kontrol çifti:** Ç07'nin izni kaldırılırsa aynı girdi `cozuldu` döner ve
   gün 4'te Ç07 atanmıştır. (Testin senaryoyu gerçekten sınadığının kanıtı;
   §16.4 "kırmızı kanıt".)

**Kaynak:** 1–2 `[spec §6.4, §16.3]` · 3 `[spec §11.3 örnek biçimi]` · 4 `[çıkarım]`

---

### A4 · Gece yarısını aşan vardiya

**Katman:** `motor /evaluate` (doğrulayıcı testi; plan elle verilir)
**Girdi:** T-10 tabanı + ek şablon **V-Akşam**: 16:00–01:00 (`bas 16, bit 25`,
`mola_dk 60`). Denetlenecek atamalar:

| # | Çalışan | Gün | Saat | Ne sınıyor |
|---|---|---|---|---|
| a | Ç01 | 1 (Salı) | 16–25 | ertesi güne taşan vardiya |
| a | Ç01 | 2 (Çarşamba) | 9–17 | 01:00 bitiş → 09:00 başlangıç = **8 saat** dinlenme |
| b | Ç02 | 1 | 16–25 | sınır durumu |
| b | Ç02 | 2 | 12–20 | 01:00 → 12:00 = **tam 11 saat**, ihlal değil |
| c | Ç03 | 1 | 16–25 | mutlak zamanda çakışma |
| c | Ç03 | 2 | 0–8 | Salı 16–01 ile Çarşamba 00–08, 00:00–01:00 arası **çakışıyor** |
| d | Ç04 | 6 (Pazar) | 16–25 | hafta sonu → Pazartesi'ye taşma, gün sayımı |

**Doğru çalışıyorsa ne görmeliyiz:**

1. Ç01 için **tam bir** `VARDIYA_ARASI_DINLENME` ihlali; ihlal kaydında ölçülen
   dinlenme **8 saat**, gereken **11**. (Z-4: dinlenme gerçek bitişten ölçülür.)
2. Ç02 için **hiç** dinlenme ihlali yok (11 ≥ 11; sınır dâhil).
3. Ç03 için **tam bir** `CAKISMA_YOK` ihlali (Z-3: mutlak zamanda).
4. Ç01'in Salı vardiyasının süresi **9 saat brüt** sayılır (Z-1), Salı gününe
   yazılır (Z-2): Ç01 Salı günlük toplam 9, Çarşamba 8 → `GUNLUK_AZAMI` ihlali
   **yok** (9 ≤ 9 sınır).
5. Ç04'ün Pazar vardiyası **Pazar'a** sayılır; Pazartesi'ye (gün 7) hiçbir
   şey yazılmaz; ihlal yok.
6. Toplam ihlal listesi: **tam olarak 2** sert ihlal (Ç01 dinlenme, Ç03
   çakışma). Fazlası ya da eksiği hata.

**Kırmızı kanıt:** vardiyayı `bit 25` yerine "aynı gün 01:00" diye yorumlayan
(yani `bit < bas` ise günü aşırmayan) bir doğrulayıcı Ç01'de 32 saat dinlenme
görür, ihlali **kaçırır** ve bu test kırmızı yanar. Test bunu yakalamak için var.

**Kaynak:** hepsi `[spec §6.3 Z-1…Z-4, §6.2, §16.3]` · madde 4'teki "sınır dâhil"
yorumu `[çıkarım]` — açık soru S-1.

---

### A5 · DST geçiş haftası

**Katman:** `motor /evaluate`
**Girdi:** T-10 tabanı ama kiracı saat dilimi **`Europe/Berlin`** ve
`DST_GECISI` kuralı **aktif**. Hafta: **2027-03-22 Pazartesi – 2027-03-28
Pazar**. 28 Mart 2027 Pazar 02:00'de saat 03:00'e alınır (ileri); o gün
**23 saat** sürer. *(Doğrulandı: 28 Mart 2027 Pazar'dır; IANA verisiyle
hesaplandı.)*

Denetlenecek atamalar:

| # | Çalışan | Gün | Yerel saat | Ne sınıyor |
|---|---|---|---|---|
| a | Ç01 | 5 (Cmt 27 Mart) | 22:00 → 07:00 (`bas 22, bit 31`) | geçiş gecesi vardiya süresi |
| b | Ç02 | 5 (Cmt) | 15:00–23:00 | — |
| b | Ç02 | 6 (Paz 28 Mart) | 10:00–18:00 | duvar saatiyle 11 saat, gerçekte **10** |
| c | Ç03 | 6 (Paz) | 08:00–16:00 | geçiş günü sıradan vardiya |

**Doğru çalışıyorsa ne görmeliyiz:**

1. Ç01'in Cumartesi gece vardiyası **8 saat brüt** sayılır, 9 değil
   (02:00–03:00 arası hiç yaşanmadı). Süre **mutlak zamanda** ölçülür (Z-6).
2. Ç02 için `VARDIYA_ARASI_DINLENME` ihlali **var**: ölçülen dinlenme **10
   saat**. Duvar saatine bakan bir doğrulayıcı 11 görür ve kaçırır — bu testin
   asıl amacı.
3. Ç03'ün Pazar vardiyası **8 saat**; ihlal yok.
4. Aynı fikstür `Europe/Istanbul` ile koşulursa Ç02'de ihlal **yoktur**
   (Türkiye'de DST yok; gün 24 saat). Bu kontrol çifti, farkın gerçekten saat
   diliminden geldiğini kanıtlar.
5. Kiracı saat dilimi sabit ofset (`+01:00`) olarak verilirse girdi
   **reddedilir** (şema hatası); IANA adı zorunlu.

**Ek (sonbahar, isteğe bağlı):** 31 Ekim 2027 Pazar gün **25 saat**; Cmt 22:00 →
Paz 07:00 gece vardiyası **10 saat** sayılır. v1'de zorunlu değil, v2'ye
bırakılabilir.

**Kaynak:** 1–3 `[spec §6.3 DST, Z-6; 02-DEGISMEZLER G-6]` · 4 `[çıkarım]` ·
5 `[spec §6.3 "IANA bölge adıyla saklanır"]` — reddetme davranışı `[çıkarım]`, açık soru S-2.

---

### A6 · Kilitli revizyon

**Katman:** `motor /solve`
**Girdi:** T-10 +
- `sabit_atamalar`: Ç01 gün 0 08–16 · Ç02 gün 3 08–16 · Ç03 gün 6 08–16.
- `kilitler`: Ç04 gün 2 `tip: yasak`.

**Doğru çalışıyorsa ne görmeliyiz:**

1. `durum = "cozuldu"`, `sert_ihlal = 0`.
2. Çıktıdaki atamalar arasında **üç sabit atama birebir** (aynı çalışan, ekip,
   gün, saat) vardır.
3. Ç04'e gün 2'de **hiçbir** atama yoktur.
4. Sabit atamalar yüzünden başka bir kural bozulmaz: Ç01, Ç02, Ç03'ün haftası
   yine 45 saat altında ve hafta tatilli.
5. Kırmızı kanıt: sabit atamalar `kurallar` listesinden `KILIT_UYUMU`
   çıkarılarak verilirse motor bunları **yok saymalı değil, yine de reddetmemeli**
   — `KILIT_UYUMU` kapsamı `S` (sistem), kiracı kapatamaz; girdi bu kuralı
   içermese bile davranış aynıdır.

**Kaynak:** 1–3 `[spec §6.6 KILIT_UYUMU, §11.2, §16.3]` · 4 `[çıkarım]` ·
5 `[spec §6 kapsam sütunu S]` yorumu `[çıkarım]`

---

### A7 · Yumuşak hedef çatışması

**Katman:** `motor /solve` (iki çağrı, aynı girdi, farklı profil)
**Girdi:** T-10 +
- İkinci şablon **V-Akşam2**: 14:00–22:00 (`bas 14, bit 22`, `mola_dk 60`).
- Talep (T-10'unkinin **yerine**), hafta içi (gün 0–4): 08–13 arası
  `asgari 2, hedef 3`; 14–21 arası `asgari 2, hedef 5`. Hafta sonu talep yok.
- Tercih: Ç01–Ç08 her hafta içi gün **08–16 tercih ediyor** (`agirlik 3`).
  Ç09, Ç10'un tercihi yok.
- Çağrı 1: `profil = "KAPSAMA"`. Çağrı 2: `profil = "CALISAN"`.

Çatışma: akşam hedefi 5 kişi; tercihsiz yalnız 2 kişi var. Hedefi doldurmak
için 3 tercihli kişi akşama alınmalı. `KAPSAMA` (hedef ağırlığı 20, tercih 1)
bunu yapar; `CALISAN` (hedef 5, tercih 9) yapmaz, akşamı asgaride bırakır.

**Doğru çalışıyorsa ne görmeliyiz:**

1. İki çağrı da `cozuldu`, `sert_ihlal = 0`, asgari kapsama %100.
2. `hedef_kapsama_yuzde(KAPSAMA) ≥ hedef_kapsama_yuzde(CALISAN)`.
3. `tercih_karsilama_yuzde(CALISAN) ≥ tercih_karsilama_yuzde(KAPSAMA)`.
4. 2 ve 3'ten **en az biri kesin büyük** (eşitlik ikisinde de olursa
   ağırlıklar hiçbir şey değiştirmiyor demektir → test kırmızı).
5. Tercih hiçbir çağrıda sert kısıt gibi davranmaz: `KAPSAMA` çağrısında
   tercihli birinin akşama atanması **ihlal sayılmaz**.

**Kaynak:** ağırlık tablosu `[spec §5.4]` · beklenen yön `[spec §16.3 "beklenen
yönde değişir"]` · ölçüm biçimi (madde 2–4) `[çıkarım]`. **Not:** §11.3 metrik
listesinde `tercih_karsilama_yuzde` **yok**; eklenmesi gerekir — bkz. T-3.

---

### A8 · Mola kapsaması

**Katman:** `/evaluate` (a, b) + `/solve` (c)
**Girdi:** T-10 tabanı, talep tek gün (gün 0) 08–15 her saat `asgari 3, hedef 4`.
Vardiya V-G (08–16, mola 60 dk).

**a) Kötü plan (elle):** Ç01–Ç04 gün 0 08–16, dördünün molası da **12:00–13:00**.
**b) İyi plan (elle):** aynı dört kişi, molalar 11–12, 12–13, 13–14, 14–15
(kaydırılmış).
**c) `/solve`:** aynı talep, motor molaları kendisi yerleştirsin.

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) `MOLA_KAPSAMASI` ihlali **var**: 12:00–13:00 hücresinde sahada 0 kişi,
   asgari 3. Tam bir ihlal, o saate işaret eder.
2. (b) Sert ihlal **0**: her saatte sahada ≥ 3 kişi kalıyor.
3. (b) Her atamanın **60 dk** molası var (`MOLA_HAKKI`, >7,5 saat). Mola
   eksik ya da 30 dk verilirse `MOLA_HAKKI` ihlali.
4. (c) `cozuldu`, sert ihlal 0; çıktıda her atamada `molalar` dolu; hiçbir
   saatte (mola düşülmüş) sahadaki kişi sayısı 3'ün altına inmiyor. Bunu
   doğrulayıcı ayrıca sayar, motorun metriklerine güvenilmez.
5. Mola çalışma süresinden düşülür: 4 kişi × 7 saat net = günlük toplam 28
   saat, 32 değil.

**Kaynak:** 1–4 `[spec §6.2 MOLA_HAKKI, §6.4 MOLA_KAPSAMASI, §16.3]` · 5
`[spec §6.2 "net süre"]` — brüt/net ayrımı açık soru S-4.

---

### A9 · Kısmi kapasite

**Karar (14 Eylül, Mustafa):** ayrıştırıldı. **Asgari** karşılanamıyorsa
`cozumsuz` + teşhis (§11.3). **Yalnız hedef** karşılanamıyorsa `cozuldu` +
eksik raporu. §16.3'teki A9 satırı ikinci hâli kasteder; v1.4'te bu şekilde
netleştirilecek (T-1).

**Katman:** `motor /solve`, iki fikstür.

**a) Hedef yetmiyor:** T-10, talep her gün `asgari 3, hedef 9`. Hedef 63
kişi-gün, kapasite 60 (10 kişi × 6 gün) → hedef **ulaşılamaz**, asgari (21)
rahat.

**b) Asgari yetmiyor:** T-10, talep her gün `asgari 11, hedef 11`. Kadro 10
kişi; hiçbir gün 11 kişi sahaya çıkamaz → **çözümsüz**, ve bu eksik **tek
hücrede** görülebilir (§11.3 teşhis biçimi hücre bazlı).

> Neden 9 değil 11: `asgari 9` de çözümsüzdür (63 > 60 kişi-gün) ama eksik
> **haftanın toplamında** doğar, tek hücrede değil; §11.3'ün hücre bazlı
> teşhisi bunu ifade edemez. Bu ayrı bir açık soru (S-7).

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) `durum = "cozuldu"`, `sert_ihlal = 0`, `asgari_kapsama_yuzde = 100`,
   `hedef_kapsama_yuzde < 100`.
2. (a) Eksik, **dakika cinsinden** raporlanır: metrik `eksik_hedef_dakika > 0`
   ve ayrıca hangi hücrelerde kaç kişi eksik olduğu listelenir. (Alan adı
   öneri; §11.3'te yok — T-3.)
3. (a) Motor asgariyi aşmak için fazla mesai tavanını (10 saat) **aşmaz**;
   `fazla_mesai_saat ≤ 10 × 10 kişi`. Kimseye 7 gün üst üste vermez.
4. (b) `durum = "cozumsuz"`. **Asgariyi karşılamayan bir plan asla
   "cozuldu" diye dönmez.**
5. (b) `teshis.hucre` vardır; `teshis.gereken = 11` ve `teshis.mumkun ≤ 10`;
   `gevsetme_denemeleri` içinde `ASGARI_KAPSAMA` için en az bir deneme var.
   (`engelleyen_kurallar` burada boş olabilir — engelleyen bir kural değil,
   kadro sayısıdır. Test bunu **zorunlu tutmaz**.)
6. Kırmızı kanıt: motor (b)'de asgariyi sessizce yumuşatıp plan dönerse test
   kırmızı yanar.

**Kaynak:** ayrım `[karar 14 Eylül]` · 1, 4 `[spec §5.3, §11.3]` · 2 `[spec
§16.3 "eksik dakikalar raporlanır"]`, alan adı `[çıkarım]` · 3, 5 `[çıkarım]`
(elle hesap)

---

### A10 · Aynı istek iki kez

**Katman:** `backend` (xUnit; motor sahte — çağrı sayan bir taklit)
**Girdi:** Plan üretme ucuna aynı `istek_anahtari = "K1"` ile ardışık iki
istek. Üç alt durum (§11.7 tablosu):

| Alt durum | Kurgu |
|---|---|
| (a) Bitmiş | İlk istek tamamlandı; ikinci istek geliyor |
| (b) Sürüyor | İlk istek kuyrukta/çalışıyor; ikinci istek geliyor |
| (c) Farklı anahtar | Aynı girdi, `istek_anahtari = "K2"` |

**Doğru çalışıyorsa ne görmeliyiz:**

1. (a) İkinci istek **aynı `plan_runs` kimliğini** döner; motor taklidi
   **tam 1 kez** çağrılmıştır; `plan_runs` tablosunda o kiracı için **tek**
   satır vardır.
2. (b) İkinci istek mevcut çalışmanın kimliğini döner, ikinci çalışma
   **başlatılmaz**; motor taklidi 1 kez çağrılmış.
3. (c) Farklı anahtar → **yeni** çalıştırma, ikinci `plan_runs` satırı,
   motor 2 kez çağrılmış. (Anahtarın gerçekten anahtar olduğunun kanıtı.)
4. Anahtar **kiracıya özeldir**: B kiracısı aynı `"K1"` ile isteyince A'nın
   sonucunu **almaz**, kendi çalıştırmasını başlatır.
5. Denetim kaydında ikinci (yinelenen) istek için ayrı bir "plan üretildi"
   izi **yoktur**.

**Kaynak:** 1–3 `[spec §11.7 idempotency tablosu, §16.3]` · 4 `[çıkarım]`
(02-DEGISMEZLER K-1'in sonucu) · 5 `[çıkarım]`

---

### A11 · Lookback eksik

**Katman:** `backend` hazırlık kontrolü (motor çağrılmadan önce)
**Girdi:** Kiracı 6 aydır sistemde, planlanan hafta 2026-10-12. Önceki 14
günün (28 Eylül – 11 Ekim) atamaları **kısmen yok**: 28 Eylül – 4 Ekim haftası
için yayınlanmış plan var, 5–11 Ekim için **hiç plan yok**.

**Doğru çalışıyorsa ne görmeliyiz:**

1. Plan üretme isteği motora **gitmez**; motor taklidi 0 kez çağrılmış.
2. Hazırlık cevabı `eksik_veri` listesinde `tip = "lookback_atamalar"`,
   eksik aralık **5–11 Ekim** olarak yazılı.
3. Kullanıcıya gösterilen mesaj eksik aralığı **günlerle** söyler; "veri
   eksik" demekle yetinmez.
4. Aynı kurguda 5–11 Ekim planı yayınlanınca hazırlık geçer ve motor 1 kez
   çağrılır. (Kontrol çifti.)
5. **Açık soru S-5:** yeni kurulan kiracıda hiç geçmiş yoktur; bu "eksik" mi
   "boş" mu? Karar verilmeden bu alt durum teste çevrilmez.

**Kaynak:** 1–2 `[spec §11.2 "lookback eksikse motor çalışmaz; hazırlık
kontrolü raporlar"]` · 3–4 `[çıkarım]`

---

### A12 · Plan kopyalama

**Katman:** `backend`
**Girdi:** 2026-10-12 haftası için **yayınlanmış** plan; T-10'un 10 çalışanı,
her birinin en az bir ataması var. Sonra Ç03 **pasife** alınır. Kullanıcı bu
planı **2026-10-26 haftasına** kopyalar.

**Doğru çalışıyorsa ne görmeliyiz:**

1. Yeni plan `taslak` durumundadır, yayınlanmamıştır.
2. Yeni planda Ç03'e ait **hiç** atama yoktur; diğer 9 kişinin atamaları
   **gün ve saat olarak aynı** (tarih 14 gün kaymış).
3. Kopyalama cevabı `dusen_atamalar` listesinde Ç03'ün düşen atamalarını
   **tek tek** (gün + saat) sayar; boş liste dönmez, "1 atama düştü" gibi
   özet de yetmez.
4. Kopya **doğrulayıcıdan geçer** ve sonucu taslağa yazılır: Ç03 düşünce bir
   hücrede asgari kapsama bozulduysa bu **ihlal olarak listelenir**, motor
   çağrılıp sessizce doldurulmaz.
5. Kaynak plan **hiç değişmez** (yayınlanmış plan dokunulmaz).
6. Denetim kaydında "plan kopyalandı" izi: kaynak plan, hedef aralık, düşen
   atama sayısı.

**Kaynak:** 1–4 `[spec §9.7 tablo, §16.3]` · 5–6 `[çıkarım]`

---

## 4. Şartnamede bulunan tutarsızlıklar

Bu doküman yazılırken bulundu. Hepsi v1.4'e taşınmalı; **v1.3 dosyasına
dokunulmaz** (versiyonlama kuralı).

| # | Nerede | Ne | Öneri |
|---|---|---|---|
| T-1 | §16.2 katman tablosu ↔ §16.3 | "on senaryo" yazıyor, tablo 12 senaryo | "on iki (A1–A12)" |
| T-1b | §16.3 A9 ↔ §6.4 + §11.3 | A9 "sert ihlal üretmez" der; ASGARI_KAPSAMA sert | **Karar verildi:** asgari → cozumsuz, hedef → raporla. A9 satırı buna göre yazılsın |
| T-2 | §11.2 örnek ↔ §6.2 MOLA_HAKKI | 08–16 vardiya için örnekte `mola_dk 30`, tabloya göre 60 | Örnek 60'a çekilsin; ya da tablodaki "süre" net mi brüt mü netleşsin (S-4) |
| T-3 | §11.3 metrikler | `tercih_karsilama_yuzde` ve `eksik_hedef_dakika` yok; A7 ve A9 bunlarsız ölçülemez | İki metrik eklensin |
| T-4 | §16.3 A11 | "Lookback eksik" ile "geçmiş hiç yok" (yeni kiracı) ayrılmamış | S-5 kararına göre yazılsın |

## 5. Mustafa'nın karar vermesi gereken açık sorular

| # | Soru | Öneri (karar senin) |
|---|---|---|
| S-1 | Sınır değerler **dâhil** mi? Dinlenme tam 11 saat, günlük tam 9 saat → ihlal değil? | Dâhil: "≥ 11" ve "≤ 9" ihlal değil. Yaygın yorum bu. A4 (Ç02) ve A4 madde 4 buna göre yazıldı. |
| S-2 | Kiracı saat dilimi sabit ofsetle gelirse **reddet** mi, **uyar** mı? | Reddet (şema hatası). Uyarı sessizce geçilir, sonra düzeltmek pahalı (§6.3 gerekçesi). |
| S-3 | Onarım döngüsü deneme sayısı çıktıda görünsün mü? (`onarim_denemesi: 2`) | Evet — A2 madde 4 ancak böyle test edilir; ayrıca izlenebilirlik (§11.7) için ucuz. |
| S-4 | `MOLA_HAKKI` tablosundaki "vardiya süresi" **brüt** mü (08–16 = 8 saat → 60 dk) **net** mi (7,5 → 30 dk)? | Brüt. Mola hakkı sahada olunan süreye göre doğar; İş Kanunu md. 68 de öyle okunur. **Bu bir hukuki yorum, uzman teyidi gerekir.** |
| S-5 | Yeni kiracı, hiç geçmiş yok: motor çalışsın mı? | Çalışsın ama kullanıcı **açıkça** "geçmiş yok, başlangıç" onayı versin; hazırlık ekranında işaretli kutu, denetim kaydına yazılır. Sessizce geçilmez. |
| S-6 | A5 sonbahar (25 saat) kontrolü v1'e girsin mi? | v2'ye; ilkbahar kontrolü asıl riski (kısa dinlenme) yakalıyor. |
| S-7 | Eksik **haftanın toplamında** doğduğunda (her gün 9 kişi gerekir, kadro 10 ama kimse 7 gün çalışamaz) §11.3'ün hücre bazlı teşhisi yetmiyor. Teşhis biçimine `kapsam: "hafta"` gibi bir toplam seviyesi eklensin mi? | Eklensin; küçük müşterinin en sık göreceği ekran UNSAT ekranı (`06-ACIK-RISKLER.md` ölçek matrisi). v1.4 §11.3. Bu doküman v1'de yalnız hücre bazlı hâli sınar. |

## 6. Onay sonrası ne olacak

1. Onaylanan her cümle **değişmez**; bu dosya `v1` olarak kalır.
2. `08-motor-testleri/v1/fikstur/A01.json … A12.json` yazılır: §11.2
   şemasında girdi + `beklenen` bloğu. **Uygulamadan bağımsız** — motor hangi
   dille yazılırsa yazılsın aynı dosyalar koşar.
3. A1–A9 için pytest iskeleti: fikstürü okur, `/solve` ya da `/evaluate`
   çağırır, `beklenen`i sınar. Motor olmadığı için **hepsi kırmızı** başlar —
   bu istenen durum (§16.4 kırmızı kanıt). Motor yazıldıkça yeşile döner.
4. A10–A12 için xUnit testleri `04-kod/backend/tests/` altına, plan ve
   `plan_runs` tabloları geldiğinde.
5. `04-TEST-HARITASI.md`'ye "Altın senaryolar" bölümü, her satırı bu
   dosyadaki cümleye bağlı.
6. Tutarsızlıklar (§4) ve kararlar (§5) → `02-spec/v1.4-master-spec.md`.
