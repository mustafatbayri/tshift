# Bağımsız inceleme 4 — `VARDIYA_ROTASYON_YONU` (K-65, 11 Ekim 2026)

Tarih: 11 Ekim 2026 (akşam, bulut). İnceleyen: kodu yazan oturum değil; görev
karşı örnek avı. İncelenen: `09-motor/cozucu/model.py` (`rotasyon_geri_saat`,
`rotasyon_yonu`, `Model._rotasyon`), `cozucu/coz.py` (`_rotasyon_metrigi`,
`_CEZA_ONEKI`, `_amac_dagilimi`), `dogrulayici/kurallar.py`
(`_rotasyon_geri_saat`, `vardiya_rotasyon_yonu`), `dogrulayici/denetle.py`
(`_gecmis_ihlalleri_isaretle`), `testler/test_rotasyon_yonu.py`,
`mutasyon_kostur.py` `rotasyon` grubu (yalnız okundu), şartname §6.3 tanım
alt bölümü / §11.3 / değişiklik 65, karar K-65.
Makine: 2 çekirdek Xeon 2,10 GHz, 8 GB; Python 3.13.16; ortools 9.15.6755.

**Ürün koduna dokunulmadı.** Başta alınan md5'ler (sonda tekrar):

```
29296ff6f61d691e6c11b945ab699792  09-motor/cozucu/model.py
b42935f24ed9ce6c0965f1ad273e611b  09-motor/cozucu/coz.py
2333bb8128ceed2936005812310e3fc5  09-motor/dogrulayici/kurallar.py
1927019602037006da6d16f56f6e8059  09-motor/dogrulayici/denetle.py
852ffd5217b2fa95709a6fa31d8d20a2  09-motor/testler/test_rotasyon_yonu.py
0b11c381da0a8e75aa199a8e10d72028  09-motor/mutasyon_kostur.py
```

`mutasyon_kostur.py` **çalıştırılmadı**. Tek yan etki: ara deneylerde
`09-motor/cozucu` ve `dogrulayici` altında oluşan `__pycache__` klasörleri
(başlangıçta yoktu) sonda silindi; `.py` dosyalarına yazılmadı. Ek mutant denemeleri (B5) `09-motor`'un
`deneme/mut_kopya/` altına alınan **geçici bir kopyasında** yapıldı ve kopya
silindi. Test takımı inceleme başında `test_rotasyon_yonu.py` 18/18, tam takım
**628 passed, 138 sn**.

## İçindekiler

- [0. Yöntem ve deney betikleri](#0-yöntem-ve-deney-betikleri)
- [1. Bulgular](#1-bulgular)
  - [B1 — Şablona oturmayan donmuş satır amaç terimine girmez (metrik/doğrulayıcı görür)](#b1)
  - [B2 — Donmuş günde iki satır: motor "ilk başlangıç" değil "en büyük geri" alır](#b2)
  - [B3 — Pasif çalışanın aktarılan satırı: metrik geçmişini okumaz, doğrulayıcı okur](#b3)
  - [B4 — `donmus_gunler` var, `mevcut_plan` yok: motor terimi yazar, doğrulayıcı "geçmiş" işaretler](#b4)
  - [B5 — Test boşlukları: 13 ek mutant yaşıyor (tam ,5 yuvarlama, "ilk başlangıç", alan 12 …)](#b5)
  - [B6 — Şartnamedeki "~54 bin kısıt (ölçüm: K-65)" ölçülmemiş; ölçüm ~40 bin'e işaret ediyor](#b6)
  - [B7 — Tam ±12 saatlik fark: `ileri`'de cezasız, `yon=geri`'de 12 saat ceza (asimetri)](#b7)
  - [B8 — "Çalışma günü = başlangıç günü" ve `bas ≥ 24` şablonlar: görüş](#b8)
  - [B9 — Küçük notlar (`yon` büyük/küçük harf, ağırlık 0'da `deger`, K-54 not metni)](#b9)
- [2. A–F özetleri](#2-af-özetleri)
  - [A. Tanım ↔ kod, madde madde](#a-tanım--kod-madde-madde)
  - [B. Rastgele sahne avı — sayılar](#b-rastgele-sahne-avı--sayılar)
  - [C. Dairesel tanımın sınırları](#c-dairesel-tanımın-sınırları)
  - [D. Kurulum bedeli](#d-kurulum-bedeli)
  - [E. Testler ve mutasyon listesi](#e-testler-ve-mutasyon-listesi)
  - [F. Şartname metni](#f-şartname-metni)
- [3. Ölçülmeyenler](#3-ölçülmeyenler)
- [4. Karar](#4-karar)
- [5. md5 (sonda)](#5-md5-sonda)

---

## 0. Yöntem ve deney betikleri

Betikler `deneme/` altında; hepsi depo kökünü dosya konumundan türetir
(`ortak.py`: `kesif/<klasör>/deneme` → beş üst), mutlak yol yok, dışarıdan
kopya gerekmez. Çıktılar yanlarında (`*.out`, `*.json`).

| Betik | Ne yapar | Çıktı |
|---|---|---|
| `ortak.py` | yollar, tanımın **üçüncü** (incelemeye ait) yazımı `dairesel_geri` / `benim_say`, `Model.kur` ve proto sayımı | — |
| `d1_tanim.py` | A: 12 hedefli karşı örnek (sınır değerler, yuvarlama uçtan uca, donmuş günde iki satır, plansız donmuş gün, pasif çalışan, oturmayan satır, serbest→donmuş, gün −1'de iki kayıt, `yon` değerleri, gün 0 donmuş, `aktif:false`, alan 12) | `d1_tanim.out/.json` |
| `d2_rastgele.py` | B: rastgele sahneler (2–4 kişi, 2–7 gün, 3–5 şablon; çeyrek saat; `bas` 0 ve ≥ 24; gece yarısını aşan; `gecmis_vardiyalar` −1/−2, gün −1'de iki kayıt; `donmus_gunler` + `mevcut_plan`, bazen iki satır / oturmayan satır; `yon=geri`; ağırlık 0 / rastgele; kural yok / `aktif:false`; dinlenme 0/4/8/11) — (i)–(iv) kontrolleri | `d2_rastgele.out/.json` (tohum 11, 400 sahne), `d2_rastgele_b.*` (tohum 23, 400 sahne, asgari %90) |
| `d2b_sabit.py` | B ek: hedef plan `sabit_atamalar` ile zorlanır → motorun planı rastgele plan olur; amaç terimi çok sayıda geri çiftle sınanır | `d2b_sabit.out/.json` (tohum 5, 300 sahne) |
| `d3_sinir.py` | C: 16 sınır vakası uçtan uca (motor + doğrulayıcı + metrik) | `d3_sinir.out` |
| `d4_kurulum.py` | D: 0.1 / 0.2 ölçekte kurma süresi, değişken/kısıt, `ro_` sayımı, kural açık/kapalı; 0.1'de bir ürün yolu çözümü | `d4_kurulum.out` |
| `d5_mutasyon.py` | E: 19 **ek** mutant, geçici kopyada (`mut_kopya/`, sonda silinir) | `d5_mutasyon.out` |

Rastgele sahnelerin girdisi yalnız **farklı / çözümsüz** çıkanlarda saklandı;
ötekiler `tohum + sıra no` ile aynen yeniden üretilir (üretici deterministik;
çözücü 2 işçiyle eşit amaçlı planlar arasında tie-break değiştirebilir — satır
sayıları koşular arasında ±2 oynadı, fark sınıfı değişmedi).

---

## 1. Bulgular

<a id="b1"></a>
### B1 — Şablona oturmayan donmuş satır amaç terimine girmez; metrik ve doğrulayıcı görür — **düzeltilmeli (not metni + bilinen sınır)**

**Ne:** K-54'te hiçbir şablona oturmayan donmuş satır (yönetici 10:00–14:00
yazmış) çıktıya aynen geçer ama modele girmez. Rotasyon terimi `x`
değişkenleri üzerinden kurulduğu için o satırla yapılan çift **amaç terimine
hiç girmez**; `metrikler.rotasyon_geri_*` ve doğrulayıcı satırı plandan sayar.
Sonuç: şartname §6.3/§11.3'ün *"amaç kırılımındaki `deger` = yuvarlanmış saat
toplamı"* iddiası bu sahnede tutmaz; motor o çifti **görmeden** planlar.
**Karşı örnek (d1 A6):** gün 0 donmuş, mevcut plan `P1 10:00–14:00` (şablonsuz);
gün 1 talep SABAH (07:00) → plan `[(0, None, 10), (1, SABAH, 7)]`; amaç kırılımı
`deger 0`; metrik `(1, 3.0)`; doğrulayıcı `(gün 1, 3.00, geri)`.
**Kanıt:** rastgele avda 1.078 çözülen sahnenin **4'ü** (i)'de farklı çıktı ve
**dördü de** bu sınıf (`donmus_oturmayan: True`): `d2_rastgele` sahne 221
(`deger 5`, beklenen 11), `d2_rastgele_b` 147 (`0` / 7) ve 255 (`0` / 9),
`d2b_sabit` 61 (`0` / 9). Bu sınıf dışında (i) farkı **sıfır**.
**Not metni:** motorun K-54 notu *"saat ve dinlenme kurallarinda modele
girmedi"* der; rotasyon terimini saymaz. Okuyan, rotasyon cezasının o satırı
gördüğünü sanır.
**Öneri:** (a) nota "rotasyon" eklensin (ucuz); (b) istenirse oturmayan satırın
`bas`'ı sabit sayı olarak ikinci güne kısıt yazabilir (`g ≥ geri(bas_sabit, t) · x_t`),
gün −1 terimiyle aynı kalıp — küçük değişiklik, ama K-54'ün "modele girmez"
ilkesini kısmen deler; karar Mustafa'nın. Şartname §6.3 madde 5'e bir cümle:
"şablona oturmayan donmuş satırla yapılan çift amaç terimine girmez, metrik ve
doğrulayıcı sayar".

<a id="b2"></a>
### B2 — Donmuş günde aynı kişiye iki satır: motor "ilk başlangıç" değil **en büyük geri**yi alır — **not (tanımdan sapma, dar kenar)**

**Ne:** §6.3 madde 1: *"aynı günde birden çok atama varsa ilk başlangıç alınır"*.
Doğrulayıcı ve metrik `min(bas)` alır (`kurallar.py:2090`, `coz.py:1426`).
Motor ise her şablon çiftine ayrı kısıt yazar (`model.py:2554–2560`): donmuş
günde iki `x` birden 1'e sabitlenince `g ≥ hy(s1,t)` **ve** `g ≥ hy(s2,t)` →
`g = max`. Motor planında bu durum oluşamaz (`_gunde_tek_vardiya`), yalnız
yöneticinin iki vardiya yazdığı donmuş günde (K-54 bunu açıkça öngörüyor) ve
`gecmis_vardiyalar` ile değil (orada `min(onceki)` doğru, `model.py:2568`).
**Karşı örnek (d1 A3):** gün 0 donmuş, mevcut plan `SABAH 07:00` + `AKSAM 13:45`;
gün 1 talep yalnız ORTA (10:00) ile kapanıyor → amaç kırılımı `deger 4`
(13:45→10:00 = 3,75 → 4); doğrulayıcı `[]`, metrik `(0, 0.0)` (07:00→10:00
ileri). Motor olmayan bir cezayı öder; seçenek olsaydı gün 1'de planı
saptırabilirdi.
**Öneri:** `_rotasyon`'da donmuş gün için yalnız **en erken** sabitlenmiş
şablonun çiftlerini yazmak (`self._donmus_plan[(kisi, d)]`'den `min(bas)`);
ya da şartnameye "motor donmuş günde iki satırı iki ayrı çift gibi görür"
notu. Test yok (B5, M4–M8).

<a id="b3"></a>
### B3 — Pasif çalışanın aktarılan donmuş satırı: metrik geçmişini okumaz, doğrulayıcı okur — **not**

**Ne:** `_rotasyon_metrigi` plan satırlarını herkes için, `gecmis_vardiyalar`'ı
yalnız `kuruldu.calisanlar` (aktif) için okur (`coz.py:1423–1430`);
doğrulayıcı `_gecmis_kayitlari(girdi, kimlik)` ile pasif kişinin geçmişini de
okur. Donmuş satırı aktarılan pasif kişi (K-54: "satır çıktıya aynen geçti")
için Pazar→Pazartesi çifti iki tarafta farklı.
**Karşı örnek (d1 A5):** P2 `durum: pasif`, geçmiş gün −1 13:45, donmuş gün 0
satırı SABAH → metrik `(0, 0.0)`; doğrulayıcı `(P2, gün 0, 6.75, gecmis: True)`.
**Kanıt:** 1 hedefli sahne; rastgele avda pasif kişi üretilmedi (ölçülmedi).
**Öneri:** metrikte geçmişi `girdi["calisanlar"]`'dan (aktiflik süzgeçsiz)
okumak ya da §11.3'e "pasif kişinin geçmişi metriğe girmez" notu.

<a id="b4"></a>
### B4 — `donmus_gunler` var ama `mevcut_plan` yok: motor serbest planlar ve (−1,0) terimini yazar (doğru), doğrulayıcı satırı yine `gecmis: true` işaretler — **not (K-54 geneli, rotasyona özgü değil)**

**Karşı örnek (d1 A4):** `donmus_gunler: [0]`, `mevcut_plan` yok, geçmiş gün −1
13:45, gün 0 talep SABAH → model `self.donmus = ∅`, `(P1, −1)` terimi var,
`deger 7`; doğrulayıcı satırı `(gün 0, 6.75, gecmis: True)`,
`gecmis_ihlaller`'a girer. Motor o günü **kendisi** planladı; "olan oldu"
işareti yanıltır (kapı yumuşak kuralda zaten kapanmaz, ama rapor yanlış sınıfa
yazar). `_gecmis_ihlalleri_isaretle` yalnız `donmus_gunler`'e bakıyor;
`mevcut_plan is None` iken işaretlememesi bir satırlık değişiklik. Bütün
kurallar için geçerli; ayrı kayıt öneririm.

<a id="b5"></a>
### B5 — Test boşlukları: 19 ek mutantın 13'ü `test_rotasyon_yonu.py`'yi geçiyor — **düzeltilmeli (testler + mutasyon listesi)**

**Nasıl:** `d5_mutasyon.py`, geçici kopyada, her mutant tek başına, 18 test.

| Ek mutant | Sonuç | Boşluk |
|---|---|---|
| M1 motor `int(h+0.5)` → `int(round(h))` (tam ,5 aşağı — Python bankacı yuvarlaması: 2,5→2, 3,5→4) | **yaşıyor** | testlerde ,5'lik geri saat yok (3,75 · 6,75 · 8 · 3 · 9,25 · 11); "0,5 yukarı" iddiası test edilmiyor. Görevde örnek verilen mutant tam bu. |
| M1b aynı şey Pazartesi teriminde | **yaşıyor** | aynı |
| M2 motor yuvarlama hep yukarı (0,25→1; 9,25→10) | **yaşıyor** | motor testlerinde kesri < 0,5 olan zorunlu çift yok (9,25 yalnız kısıt sayımında) |
| M3 motor: gün 0 donmuşken de (−1,0) terimi yazılsın | **yaşıyor** | gün 0 donmuş + geçmiş −1 testi yok |
| M4 motor: gün −1'de iki kayıt → `max` | **yaşıyor** | iki kayıtlı geçmiş testi yok |
| M5 doğrulayıcı: gün −1'de iki kayıt → `max` | **yaşıyor** | aynı |
| M6 doğrulayıcı: aynı günde iki atama → `max` | **yaşıyor** | doğrulayıcıya iki satırlı gün verilmiyor |
| M7 metrik: aynı günde iki atama → `max` | **yaşıyor** | aynı (donmuş iki satır) |
| M8 metrik: gün −1'de iki kayıt → `max` | **yaşıyor** | aynı |
| M9 motor: `g` alanı 0..11 | **yaşıyor** | 12'ye yuvarlanan çift (11,75; `yon=geri` ile tam 12) testte yok |
| M10 motor: donmuş→serbest çifti de atlansın | öldü | `test_motor_K54…` |
| M11 metrik: donmuş satırlar sayılmasın (görevdeki örnek) | öldü | `test_motor_K54…` (gecis == 1) — listede yok ama testler yakalıyor |
| M13/M14 motor: sınır `<= -12` / `> 12` kaydırılsın | öldü | tanım testi (8,20)/(20,8) |
| M18 doğrulayıcı: 0,5 saatten küçük geri satır yazılmasın | **yaşıyor** | 0,25'lik satır testi yok |
| M19 motor: 1 saatlik geri çift kısıt yazmasın | **yaşıyor** | motor testlerinde 1–2 saatlik geri çift yok |
| M20 metrik: pasif kişinin aktarılan satırı sayılmasın | **yaşıyor** | B3 |
| M21 motor: `yon` notu düşülmesin | öldü | `…bilinmeyen_yon_not_duser` |
| M22 doğrulayıcı `olculen` 1 ondalık | öldü | 3,75 |

**Öneri — testler:** (1) 13:30→11:00 = 2,5 → `deger 3`, metrik 2,5; (2)
10:15→10:00 = 0,25 → motor `deger 0`, doğrulayıcı satırı `olculen 0.25`,
metrik 0,25 (d3 C14 bunu zaten gösteriyor); (3) 10:00→22:15 = 11,75 → 12
(alan sınırı); (4) gün −1'de iki kayıt (05:00 ve 13:45) → ilk başlangıç
(d1 A8: satır yok); (5) donmuş günde iki satır (B2 — beklenen davranış
kararlaştırıldıktan sonra); (6) gün 0 donmuş + geçmiş (d1 A10: model
`(P1,-1)` yazmaz, doğrulayıcı `gecmis`); (7) `aktif: false` (yalnız "kural
yok" sınanıyor; d1 A11 ile doğrulandı: terim/metrik/satır/anahtar yok); (8)
1 saatlik zorunlu geri çift. **Mutasyon listesine:** M1 (tam ,5 aşağı), M2
(hep yukarı), M3, M9, M18, M19 ve görevde anılan M11 ("metrik donmuş satırı
atlasın" — bugün test yakalıyor, listede dursun). Listedeki 21 mutant yalnız
okunarak değerlendirildi: hepsinin 18 testten en az biriyle öldüğü kodla
izlenebiliyor (örn. "yuvarlama aşağı `int(h)`" 3,75→3 ile, "boş gün
sıfırlamasın" `test_motor_bos_gun…` ile, "ikinci gün yerine ilk gün"
`test_dogrulayici_geri_gecis…` ile); **eşdeğer mutant görmedim**. Koşturulmadı.

<a id="b6"></a>
### B6 — Şartname §6.3 madde 7 "~54 bin kısıt (ölçüm: K-65 kaydı)": ölçüm yok, dışdeğerleme ~37–40 bin — **not (metin)**

**Ne:** §6.3 madde 7 ve `model.py` docstring (*"cift basina ~18 kisit, 500 kisi
x 6 gun ~54 bin"*) 6 şablonlu ekipte 18 geri çift varsayıyor. Ölçüm
(`d4_kurulum.py`, veri setinin şablonları): **6 şablonlu kişide 14, 5 şablonlu
kişide 9 geri çift**.

| Ölçek | Kişi (şablonlu) | `ro_` değişken | `ro_` kısıt | Toplam kısıt açık / kapalı | Toplam değişken açık / kapalı | Kurma sn açık / kapalı (3 tekrar) |
|---|---|---|---|---|---|---|
| 0.1 | 49 (45) | 270 (= 45 × 6) | 3.570 (= 7·9·6 + 38·14·6) | 79.578 / 76.008 (+%4,7) | 60.082 / 59.812 (+%0,45) | 6,43 · 6,35 · 7,11 / 7,24 · 6,12 · 6,74 |
| 0.2 | 100 (94) | 564 | 7.476 | 161.256 / 153.780 (+%4,9) | 124.499 / 123.935 (+%0,45) | 12,82 · 13,52 · 13,12 / 13,81 · 13,38 · 12,40 |

Kurma süresi farkı **gürültünün içinde** (ölçülemedi; ±0,5 sn tekrar
oynaması). 500 kişiye doğrusal dışdeğerleme: ≈ 5 × 7.476 ≈ **37 bin** (ekip
karışımı aynıysa; 1.0 ölçek bulutta kurulmadı). K-65 kaydında 500 kişilik
ölçüm henüz yok ("rotasyon-once-900" koşusu bekleniyor); "(ölçüm: K-65
kaydı)" ileriye dönük bir referans. **Öneri:** metni "~40 bin (0.2'den
dışdeğerleme; 500 ölçümü K-65)" yapmak, docstring'deki 18'i 14'e çekmek.
Geçmiş gün −1 kaydı olan kişi başına +1 değişken ve ≤ şablon sayısı kadar
kısıt gelir (veri setinde geçmiş yok).

<a id="b7"></a>
### B7 — Tam ±12 saatlik fark: `yon=ileri`'de cezasız, `yon=geri`'de **12 saat ceza** — **not (karar)**

**Ne:** `fark > 12 → −24; fark ≤ −12 → +24` → tam +12 ve tam −12 ikisi de
**+12 = ileri**. `yon=ileri`: 08:00→20:00 ve 20:00→08:00 cezasız (d3 C1, C2).
`yon=geri` işareti çevirince ikisi de **12 saat "geri"** olur: C11 (08→20)
ve C12 (20→08) `deger 12`, metrik 12,0. Şartnameye uygun (madde 2 formülü
böyle); ama tie-break'in sonucu asimetrik: bir kiracı için en pahalı geçiş,
öteki için bedava. 12 saatlik fark gerçek sahnede 11 saat dinlenmeyle ancak
≤ 1 saatlik vardiyada kurulur (20→08) ya da sabah→akşam (08→20, 8 saat +
12 dinlenme: **kurulur**). **Seçenek:** tam 12'yi "yön yok" sayıp iki yönde
de 0 vermek (`fark == ±12 → 0`), ya da şartnameye asimetriyi yazmak.
Kararı Mustafa verir; kodda sapma yok.

<a id="b8"></a>
### B8 — "Çalışma günü = başlangıç günü" ve `bas ≥ 24` şablonlar — **not (görüş; karar Mustafa'nın)**

**Ölçülen (d3):** gece 23:00–07:00 (gün d) → gün d+1 boş → gün d+2 07:00
(C8) ya da 13:45 (C9): **çift yok**, satır yok (sayılsaydı C9 9,25 geri).
`bas 0` (00:00–08:00) → ertesi gün 07:00: **+7 ileri**, cezasız (C7).
09:00–13:00 → ertesi gün 00:00 gecesi: 9 geri, tam 11 saat (C10, şartname
örneği). 0.1 ölçekli ürün planında "gece → boş → iki gün sonra" deseni 7 kez
oluştu, hiçbiri dairesel okumada geri değildi (d4).

**Görüş.** Başlangıç günü tanımı Z-2 ile, çizelge görünümüyle (gece vardiyası
d'nin hücresinde, d+1 boş) ve literatürün M→E→N çemberiyle tutarlı; 23→07
"ileri" literatürün N→M = ileri okumasıdır. Kullanıcı gözüyle iki pürüz var:
(1) gece çıkışı (07:00) ile iki gün sonraki başlangıç arasında 24–40 saat
var; "boş gün" sezgisel; ama 23:00 gecesi → d+2 13:45 (30,75 saat ara)
literatürde "gece→akşam = geri" sayılan geçiştir ve tanım bunu hiç görmez.
Yumuşak kuralda kabul edilebilir; isteniyorsa "boş gün"ü *takvim günü içinde
hiç çalışılmamış gün* diye tanımlamak gerekir (gece d+1'in ilk 7 saatini
kaplar → d+1 boş değil → (d, d+2) çifti kıyaslanır). Bu, tanımı değiştirir,
kararı Mustafa verir. (2) `bas 0` gece (00:00–08:45, veri setinde **B-GECE
gerçek**) → ertesi gün 08:00 (23,25 saat ara): dairesel okumada +8 ileri,
cezasız; uyku açısından "gece sonrası ertesi sabah" sert bir geçiştir ama
bu *rotasyon yönü* değil *gece sonrası dinlenme* konusudur (ayrı kural;
11 saat tutuyor).

**`bas ≥ 24`:** girdi sözleşmesi "saatler genişletilmiş" der (§11.2), veri
setinde böyle şablon yok. Olursa `gun` alanı takvim gününden ayrışır: C5 —
gün 0'a yazılı `bas 24.5` (saatte gün 1 00:30–08:30) → gün 1 10:00 **aynı
takvim gününde** iki vardiya, tanım "art arda gün, 9,5 ileri" der; C5b — gün 0
`bas 24.5` → gün 2 07:00 takvimde art arda, tanımda değil, **çift yok**. Kod
`% 24` ile farkı doğru okur, çift kurma `gun`'a bağlı. **Öneri:** şablonda
`0 ≤ bas < 24` şartını sözleşmeye yazmak (ya da içe aktarmada `gun+1,
bas−24`'e normalleştirmek); motor/doğrulayıcı/metrik üçü de `gun`'a baktığı
için **tutarlı**, yalnız anlam kayar.

<a id="b9"></a>
### B9 — Küçük notlar — **not**

- `yon` büyük/küçük harfe duyarlı: `"GERI"`, `"Geri"`, `"geri "`, `None`, `1`
  → "ileri" + `uygulanmayan_notlar` ("yon 'GERI' taninmadi"); doğrulayıcı da
  ileri (d1 A9). Kabul edilebilir; arayüz sözleşmesi küçük harf göndermeli.
- Ağırlık 0 iken `amac_dagilimi.VARDIYA_ROTASYON_YONU.deger` çöp: 58
  sahnede toplam **10.393** (değişken başına ~12, üst sınır); `ceza 0`,
  `pay_yuzde 0`. Şartname "anlamsızdır" diyor, `kalite-olc.py` metriği basıyor
  (satır 825). İsteğe bağlı: ağırlık 0'da `deger: null` yazmak.
- `_amac_dagilimi` adı `ro_` ile eşliyor; `_CEZA_ONEKI["ro"]` var (A: ✓).
- Doğrulayıcı mesajı şartnamedeki örnekle birebir (`"P1: gun 0 13:45 -> gun 1
  10, 3.75 saat geri"`); `yon=geri`'de "ileri (yon=geri)" yazıyor (C11).

---

## 2. A–F özetleri

### A. Tanım ↔ kod, madde madde

| Madde | Kod | Durum | Kanıt |
|---|---|---|---|
| 1 art arda iki çalışma günü (d, d+1); boş gün sıfırlar | `model.py:2550` (`gunler[:-1]`, yalnız d/d+1), `kurallar.py:2094–2096`, `coz.py:1433–1434` | ✓ | d1, d3 C8/C9, 1.078 sahne |
| 1 Pazar→Pazartesi: gün −1 varsa, yoksa sessiz | `model.py:2565–2580` (`min(onceki)`, not yok, `gecmis_eksik` yok), `kurallar.py:2091–2093`, `coz.py:1427–1430` | ✓ (B3: pasif kişi) | test, d1 A8/A10, 605 geçmişli sahne |
| 1 aynı günde birden çok atama → ilk başlangıç | doğrulayıcı/metrik `min` ✓; **motor `max`** (`model.py:2554–2560`) | **sapma (B2)** | d1 A3 |
| 2 dairesel (−12, 12]; negatif geri; `yon=geri` çevirir; tanınmayan → ileri + not | `rotasyon_geri_saat` 681–688, `_rotasyon_geri_saat` 2066–2073, `rotasyon_yonu` 691–699, `kurallar.py:2082–2084` | ✓ (B7 asimetri notu) | d1 A1: 34 sınır çifti × 2 yön, üç yazım aynı; A9 |
| 3 ceza = ağırlık × geri saat; amaçta `int(h+0,5)`; doğrulayıcı/metrik kesin | `model.py:2545, 2571`; `kurallar.py:2100` `round(h,2)`; `coz.py:1439` `round(saat,2)` | ✓ | d1 A2: 0,25→0 · 0,5→1 · 0,75→1 · 2,5→3 · 2,75→3 · 9,25→9 · 11,75→12 · 12→12 uçtan uca; ağırlık profil/kiracı test |
| 4 K-54: iki donmuş gün terime girmez; donmuş→serbest girer; doğrulayıcı iki donmuşu `gecmis` işaretler (ikinci gün) | `model.py:2551–2552, 2565`; `denetle.py:83–138` (yalnız donmuş satırlarla yeniden koşarak) | ✓ (B1, B4 kenarları) | d1 A7 (serbest→donmuş da girer, işaret yok), A10; 236 donmuşlu sahne, `k54_isaret_farkli` 0 |
| 5 metrikler (plandan, donmuş dahil, pasifse `None`); kırılım `ro` | `coz.py:1412–1439, 1520, 1537–1538, 1543–1545` | ✓ (B1, B3) | 243 kapalı/yok sahne (iii) 0 fark; 835 açık sahne (ii) 0 fark |

### B. Rastgele sahne avı — sayılar

| | `d2_rastgele` (tohum 11) | `d2_rastgele_b` (tohum 23, asgari %90) | `d2b_sabit` (tohum 5, plan zorlanmış) | Toplam |
|---|---|---|---|---|
| Sahne / çözülen / çözümsüz | 400 / 394 / 6 | 400 / 391 / 9 | 300 / 293 / 7 (921 üretildi, sert kural tutanlar) | 1.100 / 1.078 / 22 |
| Durma sebebi | 394 optimum | 391 optimum | 293 optimum | **hepsi optimum** |
| Kural açık / yok / `aktif:false` | 272 / 62 / 60 | 270 / 66 / 55 | 293 / — / — | 835 / 128 / 115 |
| Açık: ağırlık 0 · `yon=geri` · geçmişli · donmuşlu (iki satır / oturmayan) | 58 · 55 · 211 · 80 (12 / 6) | 51 · 57 · 195 · 75 (13 / 2) | 70 · 53 · 199 · 81 (6 / 3) | 179 · 165 · 605 · 236 (31 / 11) |
| Şablon: `bas` 0 · `bas` ≥ 24 · gece yarısını aşan | 138 · 166 · 285 | 149 · 163 · 327 | (aynı üretici) | — |
| Doğrulayıcı geri satırı (gecmis işaretli) | 114 (23) | 111 (31) | 314 (25) | 539 (79) |
| Ağırlık > 0 ve `deger` > 0 sahne · `deger` toplamı | 24 · 175 | 23 · 210 | 128 · 1.287 | 175 · 1.672 |
| (i) `deger` ≠ yuvarlanmış toplam | 1 (sahne 221) | 2 (147, 255) | 1 (61) | **4 — hepsi B1 sınıfı** |
| (ii) metrik ≠ doğrulayıcı (sayı / kesin saat / satır satır / inceleme sayımı) | 0 | 0 | 0 | **0** |
| (iii) kapalı/yok: metrik `None`, satır yok, anahtar yok | 0 fark | 0 fark | — | **0** |
| (iv) ağırlık 0: metrik doğru mu | 0 fark (53 satır) | 0 fark (38 satır) | 0 fark (75 satır) | **0** |
| `ceza == ağırlık × deger` | ✓ | ✓ | ✓ | ✓ |

Her farkın sahnesi JSON'da (`girdi` alanı). Rastgele av **B2'yi**
yakalamadı (31 iki-satırlı donmuş sahnede `min` ile `max` aynı çıktı; A3
hedefli sahne gösterdi).

### C. Dairesel tanımın sınırları

`d3_sinir.out` (16 vaka, hepsi sabit atamayla zorlanmış, ağırlık 1):

| Vaka | deger | metrik | doğrulayıcı |
|---|---|---|---|
| C1 08→20 (+12) | 0 | (0, 0) | — |
| C2 20→08 (−12 → +12) | 0 | (0, 0) | — |
| C3 20→08:15 (−11,75) | 12 | (1, 11,75) | 11,75 geri |
| C4 08→20:15 (+12,25 → −11,75) | 12 | (1, 11,75) | 11,75 geri |
| C5 gün 0 `bas 24.5` → gün 1 10:00 (aynı takvim günü) | 0 | (0, 0) | — (9,5 ileri) |
| C5b gün 0 `bas 24.5` → gün 2 07:00 (takvimde art arda) | 0 | (0, 0) | — (çift yok) |
| C6 23:00 → ertesi gün `bas 24.5` (1,5 ileri) | 0 | (0, 0) | — |
| C7 `bas 0` 00–08 → ertesi 07:00 (+7 ileri) | 0 | (0, 0) | — |
| C8 23–07 → boş → d+2 07:00 | 0 | (0, 0) | — (çift yok) |
| C9 23–07 → boş → d+2 13:45 | 0 | (0, 0) | — (çift yok; sayılsaydı 9,25) |
| C10 09–13 → ertesi 00:00 (`bas 0`; tam 11 saat) | 9 | (1, 9,0) | 9,00 geri |
| C10b 09–13 (gün 0) → gün 1'e yazılı `bas 24` (saatte gün 2 00:00, 35 saat ara) | 9 | (1, 9,0) | 9,00 geri |
| C11 `yon=geri` 08→20 | 12 | (1, 12,0) | "12.00 saat ileri (yon=geri)" |
| C12 `yon=geri` 20→08 | 12 | (1, 12,0) | aynı |
| C13 13:45→13:45 | 0 | (0, 0) | — |
| C14 10:15→10:00 (0,25) | 0 | (1, 0,25) | 0,25 geri |

Görüş B8'de; asimetri B7'de.

### D. Kurulum bedeli

B6'daki tablo. Özet: kural **+%4,7–4,9 kısıt, +%0,45 değişken**; kurma
süresi farkı 2 çekirdekte ölçülemedi (gürültü). Değişken: kişi × gün çifti
(6) — yalnız en az bir geri şablon çifti olan kişide (`if not geri: continue`);
kısıt: kişi başına geri çift × 6 (ölçümle birebir: 3.570 / 7.476).
`cozum_istatistikleri.degisken_sayisi` `ro_`'yu saymaz (x + mola; önceden de
dinlenmeyi saymıyordu — mevcut gelenek). 0.1 ölçekte ürün yolu çözümü (40 sn,
`mola_adimi_optimum`): 0 geri geçiş, `deger 0`, doğrulayıcı 0 satır — tutarlı.

### E. Testler ve mutasyon listesi

Test dosyası tanımın şu parçalarını kapsıyor: dairesel fark (12 çift + iki
yön, iki yazım), doğrulayıcı satırı/mesajı/kapı, ileri ve aynı saat, boş gün,
sabah→gece, Pazar→Pazartesi (var / yok / −2), `yon` (geri, tanınmayan), K-54
(iki taraf), zorunlu bedel = yuvarlanmış × ağırlık, seçim varken geri olmayan,
ağırlık profil/kiracı/0, kural yokken terim/metrik/anahtar yok, kısıt sayısı.
**Kapsamadığı:** tam ,5 yuvarlama; kesri < 0,5 olan çift (0,25 → 0 motorda;
doğrulayıcıda 0,25 satırı); ilk başlangıç (üç tarafta); gün 0 donmuş +
geçmiş; `aktif: false`; `g` üst sınırı 12 (11,75 / `yon=geri` 12); pasif
kişi; oturmayan donmuş satır; 1 saatlik geri çift; serbest→donmuş çift
(d1 A7 ile doğrulandı). Ayrıntı ve mutant kanıtı B5. Listedeki 21 mutant
(okuma): eşdeğer yok, hepsi öldürülebilir; eksikler B5'te.

### F. Şartname metni

| İddia | Durum |
|---|---|
| §6.3 madde 1–6 tanım cümleleri | kodla uyumlu; madde 1 "ilk başlangıç" motorda donmuş iki satırda tutmuyor (B2); madde 5/6 "donmuş satırlar dahil" metrikte pasif kişinin geçmişi hariç (B3) |
| §6.3 madde 2 örnekleri (08→23 = 9; 13:45→11 = 2,75; 23→07 ileri "zaten imkânsız") | ✓ (A1; C8) |
| §6.3 madde 3 "2,75→3; 0,25→0"; "DENGELI'de bir saat = hedef eksiğinin üçte biri (9/3)" | ✓ (A2; `AGIRLIK_TABLOSU` 3/1/6 ve HEDEF_KAPSAMA 9; §5.4 tablosu satır 876 aynı) |
| §6.3 madde 4 "09:00–13:00 → 00:00: tam 11 saat, 9 geri" | ✓ (C10) |
| §6.3 madde 6 mesaj örneği, `metrikler` alanları, kırılım | ✓ |
| §6.3 madde 7 "`ro_<kişi>_<gün>` 0..12, yalnız geri çiftler, çarpım yok" | ✓; "~54 bin (ölçüm: K-65)" **ölçülmemiş, ~37–40 bin görünüyor** (B6) |
| §6.3 "%14–16 … 3,9–4,7 saat … dörtte biri sabah→gece" | 8 Ekim keşif JSON'larıyla uyumlu (18/132 = %13,6; 48/301 = %15,9; ort. 3,85 / 4,7; 0.2'de 11/48 sabah→gece) |
| §11.3 rotasyon metrikleri notu; değişiklik 65 "18 test + 21 mutasyon", K-65 "toplam 348" | ✓ (18 test; `MUTASYONLAR` 348, `rotasyon` 21 — `ast` ile sayıldı) |
| K-65 "koda indi" paragrafı | ✓ |
| Literatür atıfları (IARC 124 madde 8 vb.) | doğrulanmadı (kapsam dışı) |

---

## 3. Ölçülmeyenler

- **Optimum olmayan duruşta `deger`'in sıkılığı:** `g` yalnız alttan sınırlı;
  1.078 sahnenin hepsi `optimum` bitti, FEASIBLE/`durgunluk` duruşunda `g`'nin
  gevşek kalıp kalmadığı **ölçülmedi** (inceleme 3 B6 ailesi; K-63 yolunda
  karar değişkenleri sabitlenip ceza en küçüklendiği için orada sıkı).
- 500 kişilik kurulum ve önce/sonra ölçümü (K-65, Mustafa'nın makinesi).
- Pasif çalışan rastgele avda üretilmedi (yalnız A5).
- Kurma süresi farkı (gürültü içinde; B6).

## 4. Karar

**Koda inmeye hazır — bloklayıcı yok.** Tanımın beş maddesi motor, doğrulayıcı
ve metrikte uyumlu; 1.078 rastgele + 40 hedefli sahnede metrik ≡ doğrulayıcı
≡ bağımsız sayım (0 fark), amaç terimi ≡ yuvarlanmış satır toplamı (tek
istisna K-54'ün bilinen "şablona oturmayan satır" sınıfı, B1). Düzeltilmesi
gerekenler kod değil **kenar ve kanıt**: B1 not metni/şartname cümlesi, B2
motorun donmuş-iki-satır okuması (karar), B5 test boşlukları (tam ,5
yuvarlama başta) ve mutasyon listesi ekleri, B6 "~54 bin" metni. B7/B8
Mustafa'nın tanım kararları (tam 12 asimetrisi; başlangıç günü / `bas ≥ 24`).

## 5. md5 (sonda)

İnceleme bitiminde yeniden alındı — başlangıçla **aynı**:

```
29296ff6f61d691e6c11b945ab699792  09-motor/cozucu/model.py
b42935f24ed9ce6c0965f1ad273e611b  09-motor/cozucu/coz.py
2333bb8128ceed2936005812310e3fc5  09-motor/dogrulayici/kurallar.py
1927019602037006da6d16f56f6e8059  09-motor/dogrulayici/denetle.py
852ffd5217b2fa95709a6fa31d8d20a2  09-motor/testler/test_rotasyon_yonu.py
0b11c381da0a8e75aa199a8e10d72028  09-motor/mutasyon_kostur.py
```
