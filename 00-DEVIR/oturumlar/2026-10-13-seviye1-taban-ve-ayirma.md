# 13 Ekim 2026 — Seviye 1 taban ölçümü, bulgu 31, ayırma ölçümü

Aynı pencerenin devamı (12 Ekim kaydı: `oturumlar/2026-10-12-rotasyon-d-kodu.md`
§6–7). Yeni gün, yeni kayıt (§5b adlandırma kuralı).

## İçindekiler

1. Gece bloğu ve taban ölçümü
2. Ayırma ölçümü — karar kuralı (koşudan önce)
3. Mustafa'nın bloğu
4. Sonra: yapıcı başlangıç (b)

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
