# 2026-10-02 · T-60 tam ölçek kalite: açığın yeri, ölçüm seçenekleri, şartname düzeltmeleri

**Kim.** Mustafa + Claude (yeni pencere; önceki pencere 18:50'de devretti)
**Nereden devam.** `00-BURADAN-BASLA.md` 2 Ekim 18:50 paragrafı: tam ölçek
kalite sonucu geldi (T-60 bulgu 7–9), sırada üç seçeneğin ölçümü ve hedef
eksiğinin dökümü.

## İçindekiler

1. [Açılış beyanı ve bir hata](#1--açılış-beyanı-ve-bir-hata)
2. [Açığın yeri ve keşif modeli](#2--açığın-yeri-ve-keşif-modeli)
3. [Mustafa'nın süreç kuralları](#3--mustafanın-süreç-kuralları)
4. [Şartname baştan sona okundu, düzeltildi](#4--şartname-baştan-sona-okundu-düzeltildi)
5. [Ölçüm seçenekleri (a) ve (b)](#5--ölçüm-seçenekleri-a-ve-b)
6. [(c) koşusu](#6--c-koşusu)
7. [Verilen kararlar, bekleyen kararlar, reddedilenler](#7--verilen-kararlar-bekleyen-kararlar-reddedilenler)
8. [Değişen dosyalar](#8--değişen-dosyalar)
9. [Doğrulama durumu — ne koştu, ne koşmadı](#9--doğrulama-durumu--ne-koştu-ne-koşmadı)
10. [Gece: (a) ve (b) sonuçları, Mustafa'nın düzeltmesi ve notları](#10--gece-a-ve-b-sonuçları-mustafanın-düzeltmesi-ve-notları)
11. [Kapanış: commit, K-58, yarına kalanlar](#11--kapanış-commit-k-58-yarına-kalanlar)

---

## 1 · Açılış beyanı ve bir hata

18:56'da açılış beyanı verildi (okunanlar: `00-BURADAN-BASLA.md` §1–§3, §5,
§5b, §6–§8 ve baştaki durum paragrafları; `06-ACIK-RISKLER.md` T-60;
`08-URUN-KARARLARI.md` K-57; `05-HATA-OTOPSILERI.md` O-13;
`KALITE-ARASTIRMASI-DEGERLENDIRME.md` §8; proje durum notu). Mustafa 19:03'te
onayladı; `02-DEGISMEZLER.md` ilk iş olarak okundu.

**Hata:** depo durumuna bakmak için koştuğum `git status`, silme izni
olmayan kabukta `.git/index.lock` bıraktı. Mustafa elle sildi. Otopsi ve
kural: `05-HATA-OTOPSILERI.md` O-14.

Beyanda iki tutarsızlık bildirildi: `00-BURADAN-BASLA.md` §3'teki T-60 satırı
ve `06-ACIK-RISKLER.md` öncelik tablosu 18:50 sonucundan eskiydi (bu oturumda
düzeltildi); hedef kapsaması sözü %95 iken tam ölçek planı hücre sayısıyla
%57–61, kişi-saatle yaklaşık %93–94 (sözün hangi ölçüyle tutulacağı
Mustafa'nın kararı — **henüz sorulmadı, açık**).

## 2 · Açığın yeri ve keşif modeli

Ayrıntı ve sayılar: `06-ACIK-RISKLER.md` T-60 bulgu 10 ve 11. Özet:

- Bugünkü kalite dosyası (`kalite-olcumu-95-tam.json`) hücre dökümünü
  saklamıyor; döküm 1 Ekim'in kayıtlı planından (`olcum-plan-95.json`) yapıldı:
  900 kişi-saat hedefin altında, 3.903 kişi-saat hedefin üstünde.
- Motordan bağımsız keşif modeli aynı kadro ve taleple, bir kısım kural
  altında 80 kişi-saat açıklı ve sıfır fazla mesaili plan buldu. Devirdeki
  *"hedef eksiği yapısal"* cümlesi bu kurallar için desteklenmiyor.
- ⚠ Keşif betiği önce depo dışında yazıldı ve koşuldu; Mustafa'ya sınırlarıyla
  bildirildi; sonra arşivlendi:
  `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-02-hedef-tabani/`.
  Testi yok; araç değil.

Mustafa (19:22): *"devirde yazılı olanlar a b c, sonra senin önerinle devam
edelim."*

## 3 · Mustafa'nın süreç kuralları

19:09'da, geçmiş hatalara dayanarak:

> *"Hızlı cevap vermek için tahmin yürütme, her zaman elimizdeki dokümanlar
> veya ölçümlere dayanarak veya araştırarak cevaplar üret. Uygulamanın ana
> spec dokümanını okuman gereken durumlarda oku! kendin yorumlamaya çalışma.
> En önemlilerinden biri de çözüm üretebilmek için problemi basitleştirme
> veya değiştirme, farklı yerden bakarak yeni çözümler üretmenden
> bahsetmiyorum, yani cevapların kanıtlara veya çalışmamıza bağlı olarak
> değerlendirilsin lütfen. Bağlamdan koptuğunu fark ettiğin veya
> şüphelendiğin an bana sor doğru ilerleyip ilerlemediğimizi."*

`00-BURADAN-BASLA.md` §6'nın 7. ve 8. kurallarıyla aynı yönde; yeni olan iki
şey: şartnameyi okuma yükümlülüğü ve *"bağlamdan şüphelenince sor"*.

## 4 · Şartname baştan sona okundu, düzeltildi

Mustafa'nın isteğiyle `02-spec/v1.4-master-spec.md` baştan sona okundu
(4.090 satır). Altı çelişki bulundu; Mustafa 19:39'da tek tek cevapladı:

| Çelişki | Mustafa'nın cevabı | Yapılan |
|---|---|---|
| Katalog başlığı 38, sayım 35, Faz 1 listesi 38; gerçek 41; "gece çalışamayana gece yazılmaz" kuralı tabloda yok | *"41'e göre düzenleyelim, güncel değil burası resmen."* | Başlık, sayım tablosu (katalogdan yeniden sayıldı), §14.1 düzeltildi; `GECE_UYGUNLUGU` satırı eklendi |
| Sözleşme saatini doldurma: şartname yumuşak ±2, veri seti sert ve toleranssız | *"Sert ve toleranssız doğrusu."* | §6.5 satırı, §5.3 örneği, §5.4 notu |
| §12.1 *"aynı girdiyle aynı plan çıkar"* ↔ §11.7 *"garanti edilmez"* | Müşteriye *"%1–2 sapma söz konusudur"* demeyi düşünüyor; çıktı saklamak ya da arka planda arama pahalı | Cümle kaldırıldı; ⚠ **yüzde yazılmadı** — ölçülen fark %1–2 değil (aşağıda §7) |
| A11 *"motor çalışmaz"* ↔ 30 Eylül kararı | *"Çalışır, atlar ve raporlar."* + raporun ekranı çok önemli | §16.3 A11 satırı; §11.2'ye ekran gerekliliği notu |
| §8.1 notu *"kapsamı olmayan tüm kiracıyı görür"* ↔ §3.2 | *"Hiçbir şey görmez doğrusu."* | Not §3.2'ye çekildi |
| Plan sonuç kartı *"en iyinin %90'ı kadar iyi"* tam ölçekte %1 çıkar | *"Neye karar vermeliyim?"* | **Dokunulmadı** — karar bekliyor (§7) |

Okurken bulunan ve aynı kararlara (K-39) dayanarak düzeltilen bir satır daha:
`PART_TIME_LIMIT` şartnamede *"sözleşmenin saati aşılamaz"* diyordu; kod
29 Eylül'den beri tavanı emsal tam sürelinin saati (45) alıyor
(`09-motor/dogrulayici/kurallar.py` `part_time_limit`). Doküman sonu satırı
*"v1.1"* diyordu, düzeltildi.

**Sürümleme notu:** düzeltmeler yeni bir sürüm dosyası açılmadan v1.4'e
işlendi ve değişiklik listesine 49–55 olarak yazıldı — 30 Eylül–2 Ekim
eklerinin (29–48) izlediği yol. Mustafa yeni sürüm dosyası isterse v1.5
açılır.

⚠ **Düzeltilmeyen, Mustafa'ya bildirilecek:** `08-URUN-KARARLARI.md` K-39'un
gövdesinde yarı zamanlı tavanı hâlâ *"45'in 2/3'ü = 30 saat"* yazıyor; kod
ve K-57 *"45 saate kadar"* diyor. `08-motor-testleri/v5/KABUL-OLCUTLERI.md`
A11 başlığı duruyor; içeriği bu oturumda okunmadı.

## 5 · Ölçüm seçenekleri (a) ve (b)

Mustafa 19:39'da 1–1,5 saatliğine ayrıldı: *"kararım gerekmeyen işleri
tamamla."* Devirdeki (a) ve (b) seçenekleri **ölçüm ayarı** olarak yazıldı;
ürünün varsayılanı değişmedi. Tanım, testler ve mutasyonlar:
`06-ACIK-RISKLER.md` T-60 (*"Ölçüm seçenekleri yazıldı"* paragrafı),
`09-motor/testler/test_demir_secenekleri.py`.

Geliştirme, Mustafa'nın makinesindeki koşu sürerken depoya dokunmamak için
deponun bir kopyasında yapıldı; bitince dört dosya depoya yazıldı ve
Windows tarafından geri okunarak md5 ile doğrulandı (O-13 kuralı).

**Yazarken çıkan üç hata (ilk ikisini test, üçüncüsünü uçtan uca deneme yakaladı):**

1. (b)'de bir arama optimumu kanıtlayınca ötekini durduruyor; öteki henüz
   aramaya başlamamışsa tek durdurma çağrısı boşa gidiyordu. Durdurma artık
   iki arama da bitene kadar tekrarlanıyor.
3. (a)'da iyileştirme bütçenin neredeyse tamamını alabiliyordu: 0.1 ölçekte
   45 sn bütçeyle ana aşamaya 1 sn kaldı ve plan dönmedi. Tavan kondu
   (bütçenin en çok %40'ı), testi ve mutasyonu yazıldı. Tavanla da 45 sn'de
   plan dönmedi (ana aşamaya 25 sn kaldı, ipucunun plana dönmesi o makinede
   7–26 sn) — (a)'nın gerçek bedeli; T-60'a yazıldı.
2. İlk testim *"ipuçlu aramanın her zaman planı vardır"* diyordu; küçük
   sahnede ipuçsuz arama optimumu önce kanıtlayıp ipuçluyu plansız
   durdurabiliyor. Söz düzeltildi: *"seçilenin planı vardır"*. Test 18 kez
   üst üste koşuldu, 18'i yeşil.

## 6 · (c) koşusu

Mustafa 19:37'de başlattı:
`py kalite-olc.py --saniye 900 --tekrar 5 --yapilandirma ipucu_kapali --etiket c-900`.
20:59'da bitti. Beş koşunun **dördü 900 saniyede plan bulamadı**; üçüncü koşu
ilk planı 644. saniyede buldu (amaç 665.587, yasal fazla mesai 199 saat, hedef
eksiği 1.061 kişi-saat, 0 sert, yayınlanabilir). Tablo ve okuma:
`06-ACIK-RISKLER.md` T-60 bulgu 12. Sonuç: süreyi uzatmak ipuçsuz aramayı
güvenilir yapmıyor.

## 7 · Verilen kararlar, bekleyen kararlar, reddedilenler

**Verilen (hepsi var olan kararların teyidi, yeni K kaydı açılmadı):**
katalog 41 · sözleşme saatini doldurma sert ve toleranssız (K-39) · eksik
geçmişte motor çalışır, atlar ve raporlar (K-42) · kapsamsız kapsam-rolü
hiçbir şey görmez (Y-8) · sıra: (a)(b)(c), sonra bağımsız model.

**Yeni gereklilik (kayıt: şartname §11.2):** geçmiş-eksik raporunun ekranı
yöneticinin bir bakışta anlayacağı biçimde olmalı; tasarım ve kabul cümleleri
onaylanmadan kod yazılmaz.

**Bekleyen:**

1. **Plan sonuç kartı** (§9.4): *"bu plan en iyinin %X'i kadar iyi"* cümlesi
   çözücünün alt sınırına dayanıyor; tam ölçekte alt sınır zayıf, sayı %1
   çıkar. Seçenekler Mustafa'ya sohbette sunuldu.
2. **Müşteriye söylenecek sapma cümlesi:** Mustafa'nın niyeti sapmayı açıkça
   söylemek. ⚠ *"%1–2"* ölçümle uyuşmuyor: 2 Ekim tam ölçekte aynı ayarın iki
   koşusu arasında amaç %7, fazla mesai 475 ↔ 511 saat, hedef kapsaması
   %56,9 ↔ %61,5. Sayı T-60 kapanınca ölçülür.
3. %95 hedef kapsaması sözü hücre sayısıyla mı kişi-saatle mi tutulacak.

**Reddedilen:** aynı girdinin çıktısını saklayıp geri vermek ve arka planda
arama yapmak — Mustafa: *"çok pahalı geliyor."* (Çift tıklamaya karşı
§11.7'deki istek anahtarı bundan ayrıdır ve duruyor.) *"Projenin neresindeyiz"*
dökümünün dosyaya yazılması — Mustafa: *"yazmana gerek yok şimdilik."*

## 8 · Değişen dosyalar

| Dosya | Ne |
|---|---|
| `02-spec/v1.4-master-spec.md` | Değişiklik listesi 49–55 |
| `09-motor/cozucu/coz.py` | Üç ölçüm ayarı (kapalı), `_ilk_asamada_iyilestir`, `_paralel_coz`, `_paralel_sec`; çıktıya `ilk_asama_iyilestirme`, `paralel` |
| `09-motor/testler/test_demir_secenekleri.py` | **Yeni**, 14 test |
| `09-motor/mutasyon_kostur.py` | `demir` grubu, 13 mutasyon |
| `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` | Beş yapılandırma; (a)/(b) satırlarının yazdırılması; `hedef_dokumu` (açık ve aşım nerede) |
| `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` | +2 test (hedef dökümü) |
| `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-02-hedef-tabani/` | **Yeni**, keşif arşivi |
| `00-DEVIR/00-BURADAN-BASLA.md` · `05-HATA-OTOPSILERI.md` (O-14) · `06-ACIK-RISKLER.md` (T-60) · `DEGISIM-GUNLUGU.md` | Durum |

## 9 · Doğrulama durumu — ne koştu, ne koşmadı

| Ne | Nerede | Sonuç |
|---|---|---|
| `09-motor/testler/` (40 dosya) | bulut makinesi, Python 3.10, 2 çekirdek, dosya dosya | **545 geçti** (531 + 14), kodun son hâliyle |
| `mutasyon_kostur.py demir` | aynı | 13 mutasyon, **hepsi öldü** |
| `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` | aynı | 9 geçti (7 + 2) |
| `kalite-olc.py` uçtan uca | aynı, 0.1 ölçek, 90 sn | (a) iki koşu, ürün hali bir koşu — çıktı ve döküm yazıldı |
| Diğer 201 mutasyon | — | ⚠ **koşmadı** (çözücü dosyası değişti; Mustafa'nın makinesinde koşulmalı) |
| Altın senaryolar, bekçiler, taban testleri | — | ⚠ **koşmadı** |
| `DENETIM.py` | bulut makinesi | 0 hata; uyarılar önceki oturumlardan + commit bekleyen dosyalar |
| Mustafa'nın makinesi (Python 3.14), CI | — | ⚠ **koşmadı**; commit ve push yapılmadı |

## 10 · Gece: (a) ve (b) sonuçları, Mustafa'nın düzeltmesi ve notları

**21:41 — (c) çıktısındaki uyarı.** Mustafa ekran çıktısını gönderdi; sonda
*"ÜÇ SAYI AYNI DEĞİL (K-57 bozuldu)"* satırı vardı. Dosyadan okurken
görmemiştim (ekrana yazılan satır, dosyaya değil). İnceleme ve sonuç:
`06-ACIK-RISKLER.md` T-60 bulgu 14.

**21:45–23:00 — Mustafa blok 1 ve blok 2'yi koştu.** Blok 1: `545 passed`,
`OZET: 13 mutasyon · yasayan 0 · atlanan 0`, `9 passed`. Blok 2: (a) ve (b)
tam ölçek — tablo ve okuma bulgu 13. Yukarıdaki §9 tablosunun *"Mustafa'nın
makinesi — koşmadı"* satırı böylece kapandı; **CI ve 214 mutasyonun tamamı
hâlâ koşmadı**, commit yapılmadı.

**23:05 — Mustafa'nın düzeltmesi (yarı zamanlı).** Şartnamede yaptığım
*"yarı zamanlı tavanı 45"* düzeltmesinde *"20 saatlik sözleşmeli"* örneği
vardı. Mustafa: çalışana sözleşme saati **tanımlanmaz**; kişi yalnız tam
zamanlı / yarı zamanlı diye işaretlenir; yarı zamanlı için baz 30 saat, 45'e
kadar *ek mesai* (fazla mesai değil); değerler kanundan gelir. Şartname §5.2,
§6.2 ve K-39'un bayat satırı (*"tavan 30 saat"*) düzeltildi. **Açık kalan
soru (Mustafa'ya soruldu):** veri setinde ve K-57'de sezonluk (40) ve stajyer
(30) sözleşmelerin kendi saati, tam zamanlıda `haftalik_saat` ve `gun_sayisi`
alanları var — *"çalışana saat tanımlamıyoruz"* ile nasıl bağdaşacak.
**Cevap 23:22:** *"tam zamanlı ve yarı zamanlı kalacak sadece"* → K-58, §11.
**Açık iş:** yarı zamanlının 30–45 arası *ek mesai* saati ayrı bir sayı
olarak raporlanmıyor.

**23:05 — Mustafa'nın dört notu** (ayrıntı T-60, *"Mustafa'nın 2 Ekim 23:05
notları"*): koşudan koşuya fark küçültülecek · sonuç kartının yüzde cümlesi
ertelendi, unutulmayacak · molalar ayrı ve isteğe bağlı adım olabilir mi —
yorum istendi, verildi, ölçüm yapılandırması yazıldı · süre önerisi probleme
göre değişebilir mi — yorum verildi, T-60 sonrası ölçülecek.

**Bu bölümde değişen dosyalar:** `02-spec/v1.4-master-spec.md` ·
`00-DEVIR/08-URUN-KARARLARI.md` (K-39) ·
`08-motor-testleri/gercekci-veri-seti/kalite-olc.py` (`fazla_mesai_uyumu`,
iki yapılandırma) · `…/testler/test_kalite_olc.py` (+1 test; bulut
makinesinde 10 geçti, Mustafa'nın makinesinde **henüz koşmadı**) · devir
dosyaları.

## 11 · Kapanış: commit, K-58, yarına kalanlar

**23:20 — commit ve push.** Mustafa blok 3'ü koştu: kalite testleri
`10 passed`, `DENETIM.py` 0 hata (15 bilinen uyarı; commit bekleyen 15
dosya o anda). Ardından commit **`4bd41ab`** — 16 dosya, 34.016 satır ekleme
(iki ölçüm dosyası 32.490 satır) — ve push; `origin/main = 4bd41ab`.
**CI sonucu bu pencerede görülmedi.**

**23:22 — K-58.** Sezonluk/stajyer sorusuna: *"tam zamanlı ve yarı zamanlı
kalacak sadece."* Karar `08-URUN-KARARLARI.md` K-58'e, uygulama borcu
`06-ACIK-RISKLER.md` T-80'e (🟡), şartname §8.3'e işaret (değişiklik 56)
yazıldı. **Kod, veri seti ve şartname metni çekilmedi** — veri seti
değişeceği için tam ölçek ölçümleri yeni setle yinelenecek. `gun_sayisi`
alanı: soruldu, cevap yalnız tipleri kapsadı; **yarın ilk soru.**

**Mustafa'nın kararları:** molalar — *"ölçümden sonra karar verelim"*; blok 4
bugün koşulmayacak; *"bugünlük çalışmamız yeterli, yarın devam edelim."*

**Kapanış durumu.** Bu bölümden sonra değişen devir dosyaları (bu günlük,
`00-BURADAN-BASLA.md`, `06`, `08`, şartname, `DEGISIM-GUNLUGU.md`) **commit
edilmedi**; kapanış commit bloğu sohbette verildi. Yarının girişi:
`00-BURADAN-BASLA.md` 23:45 paragrafı — *"Yarın sıradaki tek adım"*.

**Bu pencerenin kendi dersleri (O-14 dışında, otopsi açılmadı):**
- (c) çıktısındaki *"K-57 bozuldu"* uyarısını dosyadan okurken görmedim;
  ekran çıktısında vardı. Ölçüm betiği önemli bulguyu **yalnız ekrana**
  yazıyordu; `fazla_mesai_uyumu` artık dosyaya da gidiyor.
- Şartnameyi düzeltirken *"20 saatlik sözleşmeli"* örneği uydurdum; karar
  *"çalışana saat tanımlanmaz"* idi. Örnek, karar metninden değil koddaki
  eski test adından geldi. Kural: şartnameye yazılan her örnek bir karar
  metnine ya da ölçüme bağlanır.

