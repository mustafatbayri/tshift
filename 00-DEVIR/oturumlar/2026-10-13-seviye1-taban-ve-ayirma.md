# 13 Ekim 2026 — Seviye 1 taban ölçümü, bulgu 31, ayırma ölçümü

Aynı pencerenin devamı (12 Ekim kaydı: `oturumlar/2026-10-12-rotasyon-d-kodu.md`
§6–7). Yeni gün, yeni kayıt (§5b adlandırma kuralı).

## İçindekiler

1. Gece bloğu ve taban ölçümü
2. Ayırma ölçümü — karar kuralı (koşudan önce)
3. Mustafa'nın bloğu
4. Sonra: yapıcı başlangıç (b)
5. Ayırma sonucu (Mustafa'nın makinesi) ve K-68 kararı
6. K-68 koda indi (bulut)
7. Ölçüm bloğu — karar kuralı (koşudan önce)

## 1 · Gece bloğu ve taban ölçümü (04:31–06:11; okuma 08:30–09:40)

Blok uçtan uca koştu (çıktı Mustafa 13:56'da tam attı; dosyalardan sabah
okunanla birebir): damga `3cfe3a3`; 657 passed; 500 referansı (tohum 7,
`fazla_mesai_sifirda_tut`; fazla mesaisiz ilk arama 8,8 sn OPTIMAL; tabanda 0
sert, 186 aşım, 35 eksik, 0 fazla mesai; 841 sn); seviye 1 puanı **55.248**
(mola 43.715, adalet 11.515, rotasyon 18); 59 passed + 1 skipped; DENETIM
HATA yok (17 uyarı); **`68cd4cc` push** (`573ee6e..68cd4cc`; bulutta
hazırlanan 19 dosyayla birebir); taban ölçümü; **tam mutasyon 388 · yaşayan
0 · atlanan 0** (06:11).

Taban ölçümü (`kalite-olcumu-L1-95-taban-900.json`, 6 çekirdek): ayrıntı
`06-ACIK-RISKLER.md` bulgu 31. Özet: 1 / 3 plan (aşım 0, sert 0, fazla mesai
7,5 sa, amaç 62.953 / fazla mesai hariç 40.453 ↔ referans 55.248); 2 / 3
plansız. D tam ölçek: 5 / 30 sa, D-fazlası 0 (`kesif/2026-10-12-rotasyon-D`
yöntemi, L1 sahnesiyle). Bulut ayırması 2 çekirdekte (600 sn, birer koşu):
olduğu gibi / aşım yumuşak / eski asgari — üçü de plansız; S30 kontrolü
plan (26 sn). Sabah mesajında Mustafa'ya üç seçenek: (a) pay'lı set, (b)
yapıcı başlangıç, (c) ikisi. **14:00: *"C seçmek istiyorum ama ölçerek gitmek
istiyorum tabiki"*.**

## 2 · Ayırma ölçümü — karar kuralı (koşudan önce, 14:20)

Çeşitler (`merdiven.CESITLER`, seviye 1'den türer; referans her çeşitte
geçerli, 0 sert):

| çeşit | ne değişir | soru |
|---|---|---|
| `asim_yumusak` | HEDEF_ASIMI YUMUŞAK; asgari hedef − 1 aynen | Üstten kilit (sert aşım + birebir hedef) mi tıkıyor? |
| `eski_asgari` | asgari = min(hedef, taban asgarisi); aşım SERT | Alttan kilit (dar asgari) mi tıkıyor? |
| `pay1` | hedef = referans + 1, asgari = referans − 1; aşım SERT | (a) adayı — **kolaylaştırılmış** (§6 madde 7) |

Her biri 900 sn × 2, `varsayilan`, çizelgeli. **Okuma kuralı:**
- `asim_yumusak` 2/2 plan, `eski_asgari` değil → üstten kilit tıkıyor.
- `eski_asgari` 2/2 plan, `asim_yumusak` değil → alttan kilit tıkıyor.
- İkisi de 2/2 → kilitlerden **birini** açmak yetiyor.
- İkisi de plansız ya da yarım → tek kilit değil, setin genel sıkılığı
  (bulut gözlemi doğrulanır).
- `pay1` 2/2 plan + aşım 0 + sert 0 → (a) merdiven ölçümünün tabanı olur
  (kolaylaştırılmış diye etiketli); değilse (a) da yetmez, (b) tek yol.
- Her koşuda: ilk plan süresi, fazla mesaisiz ilk arama, fazla mesai,
  referans kıyası kalem kalem.

Yapıcı başlangıcın (b) kabul ölçütleri bu okumadan sonra yazılır ve
onaylanır; hangi kilidi açacağı tasarımı belirler.

## 3 · Mustafa'nın bloğu

Sohbette verildi: korkuluk → commit (gece çıktıları + damga + çeşitler +
dokümanlar) + push → `kalite-olc.py --seviye 1 --cesit <ad> --saniye 900
--tekrar 2 --yapilandirma varsayilan --etiket ayirma-900` × 3 (~1 sa 40 dk).

## 4 · Sonra: yapıcı başlangıç (b)

Ayırma okunduktan sonra kabul ölçütleri; bulutta küçük/orta ölçekte (0,2–0,5)
seviye 1'in bulutta da plansız kaldığı bir ölçek aranır — orada denenebilir
bir test yatağı kurulur.

## 5 · Ayırma sonucu (Mustafa'nın makinesi) ve K-68 kararı

Ayırma koştu (900 sn × 2, 6 çekirdek; çıktılar Mustafa'nın makinesinde,
bir sonraki commit'te depoya girer): `asim_yumusak` 1 / 2 (amaç 38.737 ↔
referans 55.248; ama **1.690 kişi-saat aşım**, 157 hücre; fazla mesai 0,5
sa), `eski_asgari` 0 / 2, `pay1` 0 / 2. Altı koşunun altısında fazla mesaisiz
ilk arama 3 × 40 sn UNKNOWN. §2'nin okuma kuralına göre: **tek kilit değil,
setin genel darlığı**; `pay1` de yetmedi → (a) bu hâliyle işe yaramıyor, (b)
tek yol. Mustafa'ya "plan bulamamak" ne demek, samanlıkta iğne benzetmesiyle
anlatıldı; öneri "önce gevşek bul, sonra sık".

17:15 Mustafa: gevşekten serte ✅ + *"+1 −1 kısmını parametrik yapalım"*.
17:20 önerim: yalnız **üst** tolerans; kabul ölçütleri 1–7; iki soru. 17:31:
*"(i) vardiya bazında … ekip bazında olmaz … zaman değişkeni önemli. (ii)
uygundur"* + *"15 dk yı 20 dk yapalım"*. Kayıt: `08-URUN-KARARLARI.md`
**K-68**; genel ilke **T-81** (`06-ACIK-RISKLER.md`).

## 6 · K-68 koda indi (bulut)

- **Üst tolerans:** `09-motor/cozucu/model.py` — SERT'te aşım değişkeni
  `ha_*` alanı [0, tolerans], kısıt `asim ≥ atanan − hedef` (K-67 kısıtı
  böylece bir değişkenin alanına taşındı: alan açılıp kapanabilir);
  `Model.asim_sinirli`; tolerans > 0 ise bant içi ceza.
  `09-motor/dogrulayici/kurallar.py` — bant içi YUMUŞAK, üstü SERT (bilgi).
  `09-motor/cozucu/teshis.py` — ön kontrol ve aşım hücreleri üst sınıra göre.
- **Gevşekten serte:** `09-motor/cozucu/coz.py` `_gevsekten_serte` — birinci
  aşamanın aramaları UNKNOWN dönerse (INFEASIBLE değil) açık → +3 → +1 → +0;
  bütçe `gevsek_orani` %50, açık adım bunun `gevsek_acik_orani` %50'si
  (darboğaz ilk planı bulmak); tam serte inemezse yalnız tolerans üstü ×1000
  (`gk_*`, yeni değişken + kısıt yalnız bu yolda), ipucu `_EkliCozum` ile
  tam; taslak kararı **son plandan** (cevap adımında). `_ilk_arama`
  ayrıldı (testler "bulunamadı" yolunu buradan zorlar).
- **Testler:** `09-motor/testler/test_hedef_asimi.py` 13 → 21;
  `09-motor/testler/test_gevsekten_serte.py` 15 (yeni). 09 paketi 657 →
  **680** (bulutta yeşil); 08 `test_merdiven.py` + `test_kalite_olc.py` 34 +
  1 atlanan. Bir yan gözlem:
  `test_ceyrek_saat.py::test_molalar_gunun_HER_yerine_dagilabilir` arka
  planda başka çözücü koşarken (2 çekirdek dolu) bir kez kırmızı, tek başına
  3/3 yeşil — yük altında kırılgan; not edildi, değiştirilmedi.
- **Mutasyon:** `k68` 32 · yaşayan 0 (bulut grup koşusu; ilk koşuda
  yaşayan "taslakta optimuma uzaklık yazılsın" — mola adımı açıkken alan
  zaten null; ortak arama testiyle kapandı; bütçe mutantları 4 sonradan
  eklendi). `hedef_asimi` 4 · yaşayan 0. Toplam 420 (tam koşu blokta). `k67`
  6 mutantın hedefi yeni koda bağlandı (K-67 kısıtı, ön kontrol `ust`, teşhis
  `h = {`), `hedef_asimi` 2, `rotasyon` 1 (`_CEZA_ONEKI` satırı).
- **Merdiven:** çeşit `tol1`, `tol2` (`merdiven.CESITLER`);
  `kalite-olc.py` gevşek yolu (`gevsekten_serte`, `taslak`, `taslak_asim`)
  dosyaya ve ekrana yazar. Bulut dumanı (0,1 ölçek, `tol1`, 60 sn, dört
  yapılandırma): üçü plan — motor referanstan −%29…−%33 (bant içi 63–65
  kişi-saat aşımı mola kapsamasına harcıyor); `ipucu_kapali` süre yetmedi
  (iki aşama kapalı, gevşek yol yok — beklenen).
- **Şartname:** §5.2 not (T-81), §6.4 `HEDEF_ASIMI` satırı, §8.6
  `plans.kural_degerleri`, §11.3 `gevsekten_serte`, `taslak`, `taslak_asim`,
  teşhis üst sınır; değişiklik **69**.
- **Bulut test yatağı (seviye 1, 0,3 ölçek, 2 çekirdek, 300 sn, birer
  koşu; sahne `/tmp`'de, referans 286 sn'de tohum 7 ile üretildi):**
  gevşek yol **kapalıyken** `sure_yetmedi` — fazla mesaisiz ilk arama 3 ×
  UNKNOWN, yeniden arama da yok, ana aşama da yok (bulgu 31'in bulutta
  tekrarı; 0,3 ölçek bulutta "plansız kalan" yatak). **Açıkken:** aynı yol
  tıkandıktan sonra açık adım **5,25 sn'de OPTIMAL, toplam aşım 0** — yani
  sert kurala uyan plan; erken durdu, tam sert; sonuç `cozuldu`, doğrulayıcı
  0 sert, 0 aşım, 12 eksik, fazla mesai 5 sa, amaç 33.730 (referans 7.989;
  300 sn'nin 120'si boşa giden iki aramada, iyileştirmeye ~175 sn kaldı).
  Okuma: aşım açıkken "toplam aşımı en aza indir" amacı aramayı sert plana
  götürüyor; sert modelde sıfırdan aramak bulamıyor. **n = 1, 2 çekirdek —
  yön gösterir; 500'ün cevabı Mustafa'nın makinesinde.**
- **Bilinen sınırlar:** (1) gevşek yol yalnız iki aşamalı aramada (50 000+
  değişken); küçük model tam modeli doğrudan çözer. (2) Gevşek yoldan önce
  `_gecerli_plan_yeniden_ara` (aşım sert, fazla mesai serbest, 120 sn) yine
  koşar — ölçüt 4 (normal yol değişmez) gereği; seviye 1'de hep boşa
  gidiyorsa atlanması ayrı karar. (3) Tolerans > 0'da açık adımın amacı
  bant içi aşımı da sayar. (4) Bütçe oranları kalibrasyon; 500'de ölçülmedi.

## 7 · Ölçüm bloğu — karar kuralı (koşudan önce)

Mustafa'nın makinesi, `--seviye 1 --yapilandirma varsayilan`:

| koşu | ne | soru |
|---|---|---|
| `--saniye 900 --tekrar 3 --etiket gevsek-900` | ölçüt 3 | 3/3 plan? kaçında aşım 0? |
| `--saniye 1200 --tekrar 3 --etiket gevsek-1200` | Mustafa 17:31 | 20 dk bir şey değiştiriyor mu? |
| `--cesit tol1 --saniye 900 --tekrar 2 --etiket gevsek-900` | ölçüt 7 | tolerans 1'de plan bulma oranı |
| `--cesit tol2 --saniye 900 --tekrar 2 --etiket gevsek-900` | ölçüt 7 | tolerans 2'de |

**Okuma kuralı (yazıldı, koşudan önce):**
- Ölçüt 3 **tuttu**: 900 sn'de 3/3 `cozuldu` (taslak dahil) ve aşımı 0 olan
  (taslak değil) sayısı raporlanır; hedef 3/3. 3/3 plan ama < 3/3 aşım 0 →
  ölçüt kısmen; taslaklarda kaç hücre / kişi-saat, gevşek adımlarından
  hangisinde takıldığı (`gevsekten_serte.adimlar`) okunur.
- Herhangi bir koşu **plansız** → açık adım da bulamadı (`adimlar[0]`
  UNKNOWN): darboğaz aşım değil, öteki sert kurallar + fazla mesai; sıradaki
  aday "geçen haftanın planından başla" (ürün yolu) ya da açık adıma daha
  çok bütçe (`gevsek_acik_orani`) — ölçülerek.
- 1200 ↔ 900: plan sayısı, aşım-0 sayısı, amaç; fark yoksa 900 kalır.
- `tol1` / `tol2`: plan bulma oranı ve gevşek yolun tetiklenip
  tetiklenmediği; referans kıyası (bant içi aşımın neye harcandığı).
- Gerileme: tam paket (09 + 08) yeşil, tam mutasyon yaşayan 0.

