# Değişim günlüğü

En yeni en üstte. Her satır: tarih · ne oldu · nerede.

---

**2026-10-07 (05:00) · Kredi kesintisi (03:05): O-18 düzeltmesi oturum kaydından yeniden uygulandı ve yeniden doğrulandı; eşdeğer mutant düzeltildi; iki bağımsız inceleme yeniden koştu — mola adımına giden ipucu testi, ipucu koruması, "~700 sn" düzeltmesi (31 test / 290 mutasyon / 587); bulgu 24 (mola adımı yetişmezse elde plan varken "süre yetmedi")**
03:05'te kredi bitti; 02:35–03:05 düzeltmesi yalnız bulut alanındaydı ve
silindi. Oturum kaydındaki 20 düzenleme adımı Mustafa'nın makinesindeki 00:45
sürümüne yeniden uygulandı (20'nin 20'si ilk denemede), çıktılar 03:00'teki hâlle
birebir (14 dosyanın fark satır sayıları aynı). Yeniden doğrulama: 583 test,
39 gerçekçi set testi, karşı örnekler aynı puanlar; mutasyon grupları `demir`
40'ın 40'ı, `ilk_asama` 6/6, `kalite` 6/6; `fm_sifir` 43'ün 1'i yaşadı — ipucu
yazılmadan siliniyordu (eşdeğer mutant; 03:30'da "hepsi öldü" koşu bitmeden
yazılmıştı, üstü çizildi) → mutasyon düzeltildi, ikincisi eklendi, ipucuyu
doğrudan okuyan test eklendi; `fm_sifir` yeniden **44'ün 44'ü öldü, atlanan 0** (04:14, bulut). 49 kişi 30 sn ikişer:
düzeltilmiş yol 2.722 / 2.689, sert kesim 2.717 / 2.719, 6 Ekim öncesi
15.478 / 15.469. Bulgu 24: 20 sn'de mola adımına 2,3 sn kalınca plan yokken
"süre yetmedi" (karar Mustafa'da; önerim 2. aşamanın planı notla dönsün).
İlk incelemenin raporları kurtarıldı; son iki inceleme yeniden koşturuldu
(04:10–04:45): A — 640 rastgele sahnede ürün yolu 640'ın 640'ı kanıtlı optimuma
eşit; mola adımına giden ipucu denetlenmiyordu → test + 2 mutasyon; çöken
mutant `.clear()`; ölçüm aracı `KeyError` → düzeltildi; eşitlikte fazla
mesaili plan seçilebiliyor (tasarım notu). B — *"~700 sn"* yanlış (170 sn),
iki güncellenmemiş satır, *"birebir"* zayıflatıldı, *"ipucundan kötü plan
dönemez"* garanti değildi → **ipucu koruması** (`ipucu_korundu`; test + 2
mutasyon), K-30 ↔ K-61 çelişkisi yeni değil (kodda hiç sert kural olmadı).
Son: 31 test / 587 / 290 mutasyon (`fm_sifir` 48'in 48'i bulut). Kanıt klasörü:
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/` (betikler, loglar, inceleme raporları, yeniden uygulama adımları).
→ `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-07-o18-duzeltme/OKU-BENI.md` · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §16 · `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 23 kesinti paragrafı, bulgu 24) · `00-DEVIR/08-URUN-KARARLARI.md` (K-61 durum) · `00-DEVIR/05-HATA-OTOPSILERI.md` (O-18 tarih) · `00-DEVIR/00-BURADAN-BASLA.md` (04:30 eki) · `09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/mutasyon_kostur.py`

**2026-10-07 (03:30) · O-18 / T-60 bulgu 23: K-61'in 00:45 sürümü ilkeyi çiğniyordu — bağımsız inceleme buldu, düzeltildi; fazla mesaisiz plan yalnız başlangıç noktası, kararı ağırlıklar verir; 500 kişilik ölçüm bekliyor**
İşi görmemiş iki inceleme ajanı: 00:45 sürümü fazla mesaisiz plan bulunca
fazla mesaiyi bütün aşamalarda 0'da tutuyordu ve "ağırlık koşulu" bunu
korumuyordu — **ürün ağırlıklarında** kanıtlı optimum fazla mesaili olan
sahneler var (15 dakikalık adım haftanın düzenini açıyor: 750'ye karşı 2.256;
12 kişide 9.000'e karşı 12.000 — tam 3 saat, Mustafa'nın örneği; iki ekibe
üye kişide 750'ye karşı 900 / 2.000). *"Bu kurda oluşmaz"* ve *"hesapla
gösterildi"* cümleleri yanlıştı; üstü çizilerek düzeltildi. Motor: bulunan
fazla mesaisiz plan ipucu, alanlar geri açılır, iyileştirme tam ağırlıklı
amaçla o plandan (`_ipucu_ver`); ağırlık koşulu ve `_fazla_mesai_kisayolu_gecerli`
kaldırıldı; sert kesim ölçüm seçeneği `fazla_mesai_sifirda_tut` (bulgu 21 o
hâl); çıktıda `uygulandi` → `sifirda_tutuldu`; iyileştirme eğrisi; amaç
değeri yuvarlanır. Testler 27 (dört karşı örnek; Mustafa'nın örneğinde plan
bulunsa da 3 saatlik seçiliyor); mutasyon `fm_sifir` 43 / toplam 285; bulutta
583 test. `kalite-olc.py`: `fm_once*` (ürün yolu), `fm_sert*` (6 Ekim'in
hâli), bulgu 21 adları sert kesime sabit, kayıtta `sert_kesim`. Şartname §6.7
yeniden, §11.3, değişiklik 61. Küçük ölçek (49 kişi, bulut): düzeltilmiş yol
2.713 (0 fazla mesai), sert kesim 2.758, 6 Ekim öncesi 11.918. Mustafa'da:
koşular, bulgu 23 ölçümü (`fm_once,fm_once_kapsama`, 900 sn, üçer), K-30 ilk
satırı ↔ K-61 ilkesi sorusu.
→ `00-DEVIR/05-HATA-OTOPSILERI.md` (O-18) · `00-DEVIR/08-URUN-KARARLARI.md` (K-61 düzeltme bölümü, K-30 notu) · `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 23) · `00-DEVIR/00-BURADAN-BASLA.md` (⚠ 7 Ekim 03:30) · `02-spec/v1.4-master-spec.md` §6.7, §11.3 · `09-motor/cozucu/coz.py` · `09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` · `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/OKU-BENI.md` · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §15

**2026-10-07 (00:45) · K-61: motor önce fazla mesaisiz plan arar (ürünün varsayılanı), hakem ağırlıklardır — koda indi; K-62: veri seti merdiveni ve kadro kararları** *(⚠ bu girişin motor kısmı 03:30'da düzeltildi — üstteki giriş; Mustafa 00:45 sürümünü hiç koşmadı)*
Mustafa (6 Ekim 23:44): *"Evet, ama sadece basit bir evet değil … 3 saat fazla
mesai içeren en optimum plan … fazla mesaisiz plandan oldukça daha optimum
bir plan ise en optimum olanı seçmeliyiz."* Motor: `fazla_mesai_once_sifir`
varsayılan açık; kısayol yalnız fazla mesainin dakika başı ağırlığı öteki
ağırlıkların en büyüğünden küçük değilken uygulanır
(`_fazla_mesai_kisayolu_gecerli`), değilse çıktı sebebini söyler ve kararı
ağırlıklı arama verir. Mustafa'nın örneği test: ürün ağırlıklarında fazla
mesaisiz plan (72) seçilir; hedef ağırlığı 2.000 olunca 3 saat fazla mesaili
plan (9.000 < 16.000) seçilir. Bulutta 41 dosya 582 test geçti; mutasyon
harnesi 286 (`fm_sifir` 44), grup koşularında hepsi öldü — toplam Mustafa'nın
tam koşusundan sonra. `kalite-olc.py`: ürün hali yapılandırmaları seçeneği
motorun varsayılanından alır, eski kayıt yapılandırmaları kapalı sabit,
`fm_once_kapali` eklendi, koşu kaydına `once_fazla_mesaisiz`. Şartname §6.7
(yeni alt bölüm), §11.3, değişiklik 60. **K-62:** altı set, 500 kişi, sabit
kriter seti, her seviyenin bilinen cevabı; ekipler 285 / 145 / 70; iki işi
yapabilen kişiler bütün seviyelerde; gece back office asgari 2; iki işi
yapabilen satışçı sayısı 30 (varsayım, teyit bekliyor).
→ `00-DEVIR/08-URUN-KARARLARI.md` (K-61, K-62; K-30 ve K-50 notları) · `02-spec/v1.4-master-spec.md` §6.7, §11.3 · `09-motor/cozucu/coz.py` · `09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` · `00-DEVIR/06-ACIK-RISKLER.md` (T-60) · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §14

**2026-10-06 (23:15) · Mustafa merdiven yapısını ve sabit kriter setini onayladı; O-17: iki işi yapabilen eleman ve "%95"in kıtlığı 500 kişilik sette yok; dört karar bekliyor**
Mustafa (23:02): yapı *"evet"*, kriter seti *"önerdiğin gibi"*; 151 kişiyi ve
*"herkes tek ekipte"* cümlesini sordu; gece iki işi yapabilen tek elemanla iki
ekibin talebini karşılama durumunun süreçte olması gerektiğini söyledi.
Bakıldı: o durum motorda var ve test edilmiş (`test_cok_ekipli.py` 13 test,
bulutta yeniden koşuldu, geçti) ama 500 kişilik sette iki ekibe üye kimse yok
ve gece back office talebi hafta içi asgari 13 — K-50 verilirken sete
eklenmemiş; 29 Eylül'ün *"%95: eleman yetmiyor, fazla mesaiye gidiliyor"*
tarifi de sette yok (**O-17**). Merdivende iki işi yapabilen kişiler bütün
seviyelerin kadrosuna alındı. Açıklandı: merdiven ve sayılacak ölçümler 500
kişi (151 yalnız bulut ön denemesiydi); sette üç ekip var (285, 145, 70).
Bekleyen kararlar: *önce fazla mesaisiz* varsayılan olsun mu (öneri: evet),
ekip sayıları, iki işi yapabilen kişi sayısı, gece back office talebi. Kod ve
fikstür değişmedi.
→ `00-DEVIR/05-HATA-OTOPSILERI.md` (O-17) · `00-DEVIR/08-URUN-KARARLARI.md` (K-50, 6 Ekim notu) · `00-DEVIR/06-ACIK-RISKLER.md` (T-60, 23:02 bölümü ve "Sıradaki adım") · `00-DEVIR/00-BURADAN-BASLA.md` (⚠ 6 Ekim 23:15) · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §13

**2026-10-06 (22:45) · Mustafa amacı hatırlattı ve veri seti merdiveni önerdi; okuma + küçük ölçekli ön deneme (bulgu 22, keşif); tasarım kararı Mustafa'da**
Mustafa (21:34, 21:36): zorunlu fazla mesaili, en azı (x) bilinen bir set;
asıl soru *"tüm kriterlere bağlı olarak optimum planı çıkarabiliyor muyuz"*;
beş seviyeli veri setleri. Okunan: katalog 41 kural (yumuşak dokuzun dördü
yazılı değil); %95 setinde kıtlık yok (en iyi planda hedefin üstünde 3.141,
altında 350 kişi-saat), geçen haftanın vardiyaları boş *("geçmiş boş" yazılmıştı; devreden adalet yükü 124 kişide var — 7 Ekim düzeltmesi)*, yayınlanmış plan yok, herkes tek ekipte.
Ön deneme (bulut, 49–151 kişi, tek koşu; 500 için tahmin değil): cevabı
bilinen set kurulabiliyor (151 kişi: referans 4.089 · ürünün hali 8.864 ·
*önce fazla mesaisiz* 4.146); x bilinen zorunlu fazla mesai seti
kurulabiliyor (151 kişi: en az 3,5 saat kanıtlı · ürünün hali 11,25 ·
seçenek 9,75 saat). Görüş verildi: çok set doğru; her seviyenin bilinen
cevabı, seviyeler arasında sabit kriter seti, beşinci seviye iki set. Kod ve
ürün varsayılanı değişmedi.
→ `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/OKU-BENI.md` · `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 22, "Sıradaki adım") · `00-DEVIR/00-BURADAN-BASLA.md` (⚠ 6 Ekim 22:45) · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §12

**2026-10-06 (21:15) · *Önce fazla mesaisiz* ölçüldü (bulgu 21): altı koşuda fazla mesai 0, amaç 4–5,6 kat düştü, karar kuralı tuttu — ürün varsayılanı kararı Mustafa'da**
Sabahın işi `85131ee` ile commit'lendi, CI yeşil. Ölçüm (Mustafa'nın makinesi,
900 sn, üçer koşu, `kalite-olcumu-95-fmsifir-900.json`; kıyas sabahın
`profiller-900` koşuları): fazla mesaisiz plan altı koşunun altısında 9–13
sn'de bulundu, fazla mesai 0; amaç DENGELI 106–148 bin → 26,4–26,5 bin,
KAPSAMA 46–58 bin → 13,8–13,9 bin; fazla mesai dışı kalemler de iyileşti
(DENGELI %1,6–2,2, KAPSAMA %7–12); hedefi tam tutan hücre DENGELI %82–85 →
%86, KAPSAMA %90 → %93–94; koşudan koşuya fark amaçta %40 → %0,3; süre aynı;
0 sert. Koşudan önce yazılan karar kuralının dört maddesi iki profilde de
tuttu. ⚠ Ölçülmeyen: fazla mesainin zorunlu olduğu veri (orada bugünkü yol
işler); %85 seti; 600 ve 1.800 sn. Kod değişmedi; seçenek hâlâ varsayılan
kapalı.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 21, "Sıradaki adım") · `00-DEVIR/08-URUN-KARARLARI.md` (K-30 notu) · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-fmsifir-900.json` · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §11

**2026-10-06 (11:45) · Üç profil 900 sn (bulgu 20): fazla mesai aramanın artığı; O-16: çıktıdaki "optimum · %0" yanlıştı, düzeltildi; ölçüm seçeneği `fazla_mesai_once_sifir` (varsayılan kapalı)**
Mustafa'nın makinesi, 900 sn, üçer koşu (`kalite-olcumu-95-profiller-900.json`):
dokuz koşu 0 sert; fazla mesai DENGELI 26–40,5 · KAPSAMA 10–14 · CALISAN **0**
saat. CALISAN'ın planları DENGELI ağırlıklarıyla 26,6–26,7 bin, DENGELI'nin
kendi bulduğu 106–148 bin (4–5,6 kat); DENGELI'de fazla mesai dışı amaç %0,2
oynuyor — koşudan koşuya farkın tamamı fazla mesai, o da bu girdide
gerekmiyor (K-30'a not). *"Alt sınır zayıf"* okuması düzeltildi (en iyi kanıt
21.098, bilinen en iyi plan 26.589). **O-16:** K-60'tan beri çıktı mola
adımının optimumunu planın optimumu gibi yazıyordu; artık mola adımı koşan
çıktıda `alt_sinir` ve `optimuma_uzaklik_yuzde` null, adımın sınırı
`mola_adimi_alt_sinir`, sebep `mola_adimi_optimum` (büyük modelde küresel
sınır yok — sonuç kartı için sınır adımı açık); kural genel: çözülen model
tam model değilse sınır küresel alana yazılmaz (`_sinir_kapsami`). Ölçüm seçeneği: önce fazla
mesaisiz plan; bulunursa fazla mesai 0'da kalır, bulunamazsa bugünkü yol +
not; başarısız denemenin süresi iyileştirmenin süresinden düşer (mola adımına
kalan süre korunur); CALISAN'da işlemsiz. **Bağımsız inceleme** (işi görmemiş
ayrı oturum) altı bulgu verdi, altısı düzeltildi — en önemlisi O-16'nın aynı
sınıfının seçeneğin içinde de olması. Testler: `test_fazla_mesai_once_sifir.py`
16 (yeni), `test_demir_secenekleri.py` 24 (+5), `test_ilk_asama.py`,
`test_kalite_olc.py` 16 (+6); bulutta 572 motor testi geçti. Mutasyon: `demir`
40 (+14), yeni grup `fm_sifir` 29 — grup koşularında öldü; toplam 271.
**19:21, Mustafa'nın makinesi:** 572 test (80 sn), gerçekçi set 37 (428 sn),
**tam mutasyon koşusu 271 · yaşayan 0 · atlanan 0** (damga), DENETIM hata yok.
`kalite-olc.py`: `fm_once_sifir`,
`fm_once_sifir_kapsama`, fazla mesai dışı amaç sütunu, sınır yazısı, seçenek
uygulanmadıysa *"UYGULANMADI"* satırı. 5 Ekim
21:41: demo sayfasının bağlantısı yenilendi (eski bağlantı silindi; depoda
atıf yoktu).
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 20, "Sıradaki adım") · `00-DEVIR/05-HATA-OTOPSILERI.md` (O-16) · `00-DEVIR/08-URUN-KARARLARI.md` (K-30, K-35, K-60 notları) · `02-spec/v1.4-master-spec.md` (değişiklik 59, §9.4, §11.3) · `09-motor/cozucu/coz.py` · `09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/testler/test_ilk_asama.py` · `09-motor/mutasyon_kostur.py` · `09-motor/mutasyon-tam-kosu.txt` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` · `00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md`

**2026-10-05 (21:45) · K-60 Mustafa'nın makinesinde yeşil; kalibrasyon ölçümü (bulgu 19): %80 kaldı; ölçüm bütçesi kararı; üç profil yapılandırmaları**
Mustafa'nın makinesi: 551 test, **tam mutasyon koşusu 228 · yaşayan 0 ·
atlanan 0** (damga), gerçekçi set 31 (434 sn), DENETIM 0 hata. Kalibrasyon
(`kalite-olcumu-95-kalibrasyon-600.json`, 600 sn, üçer koşu): %80 ↔ %90 fark
yok; %90'da mola adımına 44–47 sn kaldı, optimum 40,5–42,9 sn — **%80
kaldı**. Koşudan koşuya fark iyileştirme aramasından (aynı başlangıçtan
126–161 bin). Karar (Mustafa): ürün hali ölçümleri bundan sonra **900 sn**,
600 sn A/B için. `kalite-olc.py`: `profil_kapsama`, `profil_calisan`; `oran_90`
kayıt notu.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 19, bütçe notu) · `00-DEVIR/08-URUN-KARARLARI.md` (K-60) · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `09-motor/mutasyon-tam-kosu.txt` · `00-DEVIR/oturumlar/2026-10-04-k60-mola-adimi-koda.md` §6–7

**2026-10-04 (14:30) · K-60 koda indi: motor üç aşama, mola adımı varsayılan (atamalar sabit, kanıtlı optimum), iyileştirme payı %80; 228 mutasyon**
`coz.py`: `VARSAYILAN` `mola_adimi: True`, `mola_adimi_hedef_bosluk: 0.0`,
`ilk_asama_iyilestirme_orani: 0.8`; ana aşama atamaları kilitler, bekçiye 0
eşiği verir; `_ErkenDur` alt sınır değere eşitse "optimum"; küçük modelde not
düşülmez; eski `ana_asama_atamalar_sabit` kaldırıldı. Testler
`test_demir_secenekleri.py` 19 (+2, iki yeniden yazıldı), `test_sure_butcesi.py`
pay %80; `demir` 26 mutasyon (+7), **toplam 228**, bulutta grup koşuları hepsi
öldü; bulutta 40 dosya **551 test** geçti; 0,1 ölçek duman: mola adımı 1,3
sn'de optimum, 199 → 28. `kalite-olc.py`: `varsayilan` üç aşama, eski ortak
aramalı yapılandırmalara `mola_adimi: False`, yeni `oran_90` ve `k59_hali`.
Şartname §11.3 (`ilk_asama_sn`, `ana_asama_butce_sn`) ve değişiklik 58 "koda
indi". ⚠ Mustafa'nın makinesinde test, tam mutasyon koşusu, commit, kalibrasyon
ölçümü bekliyor. 14:04: Mustafa bugün dinleniyor — **testsiz commit** (CI
karar verir), tam mutasyon koşusu ve damga yarın.
→ `09-motor/cozucu/coz.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/testler/test_sure_butcesi.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `02-spec/v1.4-master-spec.md` · `00-DEVIR/08-URUN-KARARLARI.md` (K-60 Durum) · `00-DEVIR/06-ACIK-RISKLER.md` (T-60) · `00-DEVIR/oturumlar/2026-10-04-k60-mola-adimi-koda.md`

**2026-10-04 (02:45) · K-60: mola yerleşimi motor içinde ayrı adım — karar verildi, kod sırada; gün kapanışı**
Mustafa (02:07): *"evet"* → **K-60** (`08-URUN-KARARLARI.md`): atamalar
sabitken mola adımı, kanıtlı optimuma kadar; molalar plan çıktısında kalır,
şartname §6.4 cümlesi değişmez; molaların isteğe bağlı ürün adımı olması (C)
ertelendi. Şartname değişiklik 58 ve §11.3 notu (kod henüz değişmedi). Sırada
(aynı pencere, T-60'ın devamı): `coz.py` üç aşama + testler/mutasyonlar +
kalibrasyon ölçümü.
→ `00-DEVIR/08-URUN-KARARLARI.md` (K-60) · `00-DEVIR/06-ACIK-RISKLER.md` (T-60 sıradaki adım) · `02-spec/v1.4-master-spec.md` (58, §11.3) · `00-DEVIR/00-BURADAN-BASLA.md` · `00-DEVIR/oturumlar/2026-10-03-mola-olcumu-ve-mutasyon.md` §10

**2026-10-04 (02:30) · Kontrollü mola ölçümü bitti (T-60 bulgu 18): mola adımı 45 sn'de kanıtlı optimum; öneri "molalar motor içinde ayrı adım", karar Mustafa'da**
Mustafa'nın makinesi, 600 sn, üçer koşu, `kalite-olcumu-95-kontrollu-600.json`.
Atamalar sabitken mola adımı 44–46 sn'de kanıtlı optimum (mola açığı 177–188),
ortak arama 347 sn'de 193–202; ortak aramanın kazancının %94'ü mola, %6'sı
atama takası (aşım −670, eksik +115 kişi-saat; fazla mesai 0). Fazla mesai
ilk aşamada belirleniyor; 480 sn'lik dokuz koşu ort. 34,7 saat, 240 sn'lik beş
koşu 45,1 — üçer koşuda aralıklar çakışıyor. ⚠ Bulgu 15'in eksik/aşım
okuması düzeltildi (ortak aramanın takasıymış). Karar kuralı bu sonucu tam
kapsamadı (aşım kuralda yoktu) — dürüst okuma T-60'ta. Öneri: B'nin
mekanizması; süre paylaşımı kalibrasyon; (C) ürün/ekran kararı.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 18, bulgu 15 düzeltmesi, öneri) · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-kontrollu-600.json` · `00-DEVIR/oturumlar/2026-10-03-mola-olcumu-ve-mutasyon.md` §9

**2026-10-03 (19:40) · Mola kararı için kontrollü ölçüm tasarımı ve karar kuralı; `mola_adimi_tam` yapılandırması**
Mustafa (19:09): *"Kontrollü ölçümle gidelim, bu mola kararı çok kritik
duruyor; yeterli done veya anlaşılır bir öneri vermedin."* Bulgu 17 `e07311e`
ile depoda. T-60'a ölçülenin okunur tablosu (mola açığı hücre başına kişi),
A↔B kontrollü ölçüm tasarımı (üçer koşu) ve **önceden yazılmış karar kuralı**
eklendi. `kalite-olc.py`: `mola_adimi_tam` (480 sn sabit molalı + atamalar
sabit mola adımı, `hedef_bosluk 0`), mola açığı artık hücre başına kişi ve
asgarinin yüzdesi olarak da yazılıyor; bayat "varsayılan hiçbirini açmaz"
yorumu K-59'a göre düzeltildi. Bulutta 0,1 ölçekte duman testi: mola adımı
1,6 sn'de optimum, 199 → 29.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 "Kontrollü ölçüm", "Karar kuralı") · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `00-DEVIR/oturumlar/2026-10-03-mola-olcumu-ve-mutasyon.md` §8

**2026-10-03 (19:15) · K-59 depoda (`74a7a36`), 221 mutasyon hepsi öldü · mola ayrı adım ölçüldü (T-60 bulgu 17)**
Mustafa'nın makinesi: 549 + 31 test, `demir` 19/19, DENETIM 0 hata, commit
`74a7a36` push; tam mutasyon koşusu **221, hepsi öldü, atlanan 0** (damga
18:54). Ölçüm `sabit_mola_480` ↔ `mola_ayri_adim` (tek fark: ana aşamada
atamalar sabit), 600 sn, ikişer: mola adımı **29 sn'de %78–82** geri aldı
(445–535), serbest 107 sn %70–75 (597–723) ve atamalara dokunmadı; fazla mesai
27,5–36 saat (ilk aşamadan, %31 açıklık). ⚠ %2 boşluk toplam amacın; mola
teriminin kendi boşluğu geniş. **Mola kararı Mustafa'da (A/B/C).**
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 17) · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-molaadim-600.json` · `09-motor/mutasyon-tam-kosu.txt` · `00-DEVIR/oturumlar/2026-10-03-mola-olcumu-ve-mutasyon.md` §7

**2026-10-03 (16:55) · K-59: birinci aşamada amaçlı iyileştirme ürünün varsayılanı (%40) · mola ayrı adım ölçüm seçeneği**
Mustafa: *"olsun."* Varsayılan `ilk_asama_iyilestirme_saniye: None` (orandan),
oran 0.4; `0` eski davranış (ölçüm). Mola kararı için ölçüm seçeneği
`ana_asama_atamalar_sabit` ve `kalite-olc.py` `mola_ayri_adim`,
`eski_urun_hali`. 17 test, `demir` 19 mutasyon (bulut, hepsi öldü), toplam
**221**; `test_sure_butcesi.py` bütçe testi üç aramaya göre düzeltildi (K-59'un
kırdığı tek test). Bulutta 40 motor test dosyası **549 test geçti**, kalite
ölçüm testleri 18 geçti; `test_gercekci_olcek.py` bulutta koşmadı (180 sn
sınırı). Mustafa'nın tam koşusu (215) hepsi öldü, `280c4ef`. ⚠ Yeni kod
Mustafa'nın makinesinde ve CI'da henüz koşmadı.
→ `00-DEVIR/08-URUN-KARARLARI.md` (K-59) · `09-motor/cozucu/coz.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/testler/test_sure_butcesi.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `02-spec/v1.4-master-spec.md` (§11.3, değişiklik 57)

**2026-10-03 (16:00) · T-60 blok 4: molalar sabitken uzun arama fazla mesaiyi 34–38 saate indirdi · O-15: tam mutasyon koşusu 1 yaşayan 3 atlanan buldu, düzeltildi**
600 sn, ikişer koşu: 240 sn iyileştirme 45–53 saat / 512–533 kişi-saat eksik;
molalar sabit 480 sn 34–38 saat / 360–366 — bedeli mola sırasında kapsama
üç kat (bulgu 15–16). Tam mutasyon koşusu: çözücünün gün-0 "geçmiş" kaydı
mutasyonu K-56'dan sonra yaşıyordu (boş plan "çözüldü"), üç çapa K-56 ile
bozulmuştu; test güçlendirildi, +1 test, +1 mutasyon (**215**), tam koşu
damgası eklendi (O-15). Ürün varsayılanı değişmedi; iki karar Mustafa'da.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 15–16) · `00-DEVIR/05-HATA-OTOPSILERI.md` (O-15) · `09-motor/testler/test_gecmis_veri.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-mola-600.json` · `00-DEVIR/oturumlar/2026-10-03-mola-olcumu-ve-mutasyon.md`

**2026-10-02 (23:45) · K-58: sözleşme tipi yalnız tam zamanlı ve yarı zamanlı — çalışana saat tanımlanmaz · gün kapanışı**
Mustafa: *"Tam zamanlı ve yarı zamanlı kalacak sadece"*; değerler kanundan
(tam 45; yarı baz 30 / tavan 45, arası ek mesai). Karar kayda geçti; kod,
veri seti ve şartname §8.3 henüz çekilmedi (**T-80** 🟡). `gun_sayisi`
alanı açık. Commit `4bd41ab` push edildi (23:20); mola kararı ölçümden
sonra; blok 4 yarın.
→ `00-DEVIR/08-URUN-KARARLARI.md` (K-58) · `00-DEVIR/06-ACIK-RISKLER.md` (T-80) · `02-spec/v1.4-master-spec.md` (§8.3, değişiklik 56) · `00-DEVIR/oturumlar/2026-10-02-kalite-olcumu-tam-olcek.md` §11

**2026-10-02 (23:25) · T-60: birinci aşamada iyileştirme tam ölçekte fazla mesaiyi 475–511 → 60–100 saate indirdi · yan yana arama ve ipuçsuz uzun arama elendi**
Mustafa'nın makinesi, 600 sn, ikişer koşu: (a) hedef eksiğini de yarıya
indirdi, ilk plan gecikmedi, 0 sert; kazancın çoğu molalar sabitken geldi.
(b) ve (c) elendi. Çözücünün ceza değişkenleri eşitsizlikle tanımlı olduğu
için amaç değeri plandan büyük çıkabiliyor (bulgu 14); `kalite-olc.py`
uyarısı ikiye ayrıldı, iki yeni ölçüm yapılandırması (`a_ipuclu_240`,
`sabit_mola_480`). Yarı zamanlı tanımı düzeltildi (şartname §5.2, §6.2;
K-39): çalışana saat tanımlanmaz, baz 30, tavan 45. **Ürün varsayılanı
değişmedi.** Kalite testleri 10.
→ `00-DEVIR/06-ACIK-RISKLER.md` (T-60 bulgu 13–14) · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-ab-600.json` · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-95-c-900.json` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `02-spec/v1.4-master-spec.md` · `00-DEVIR/08-URUN-KARARLARI.md` (K-39)

**2026-10-02 (21:05) · Şartname 41 kurala ve verilmiş kararlara çekildi · T-60 ölçüm seçenekleri (a) ve (b) yazıldı · açığın yeri döküldü**
Yeni pencere şartnameyi baştan sona okudu; altı çelişki düzeltildi (v1.4
değişiklik listesi 49–55): katalog 41, `GECE_UYGUNLUGU` satırı, `SAAT_DENGESI`
sert ve toleranssız, yarı zamanlı tavanı 45, *"aynı girdiyle aynı plan"*
cümlesi kaldırıldı, A11 *"çalışır, atlar ve raporlar"*, kapsamsız kullanıcı
notu. T-60: 1 Ekim planının hücre dökümü (900 kişi-saat eksik, 3.903 fazla);
keşif modeli aynı kurallarla 80 kişi-saat açık + 0 fazla mesai buldu (keşif,
testi yok); çözücüye iki **ölçüm** seçeneği — birinci aşamada amaçlı
iyileştirme ve ipuçlu + ipuçsuz yan yana arama — ürün varsayılanı değişmedi.
İpuçsuz 900 sn tam ölçekte ölçüldü: beş koşunun dördünde plan yok (bulgu 12).
`kalite-olc.py` her koşunun hedef dökümünü saklıyor. 14 + 2 test, 13 mutasyon
(toplam **214**), motor **545 test** (bulut makinesinde;
Mustafa'nın makinesinde ve CI'da henüz koşmadı). O-14: `git status` kilit
bıraktı, kural yazıldı.
→ `02-spec/v1.4-master-spec.md` · `09-motor/cozucu/coz.py` · `09-motor/testler/test_demir_secenekleri.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `08-motor-testleri/gercekci-veri-seti/kesif/2026-10-02-hedef-tabani/OKU-BENI.md` · `00-DEVIR/06-ACIK-RISKLER.md` (T-60) · `00-DEVIR/05-HATA-OTOPSILERI.md` (O-14) · `00-DEVIR/oturumlar/2026-10-02-kalite-olcumu-tam-olcek.md`

**2026-10-02 (14:40) · K-57 "fazla mesai" tek tanım (yasal) · T-60 kalite ölçüm araçları ve 0.1 ölçek ölçümleri · ağırlık deneyi**
Üç ayrı "fazla mesai" sayısı vardı (çözücü cezası 5–11 saat, doğrulayıcı
metriği 116–125, motor metriği 117–127 — aynı 0.1 ölçekli sahne). Mustafa:
yasal tanım; yarı zamanlıya fazla mesai yazılmaz. İki metrik çalışma
süresine çekildi, ücret farkı `sozlesme_ustu_ucret_saat` adıyla ayrı alan;
fazla mesai ağırlığı tabloya alındı (kiracı ezebilir, davranış aynı). Çözücü
çıktısına `amac_dagilimi` ve `iyilesme`; `kalite-olc.py` (yapılandırmalar,
bağımsız tabanlar, `--tekrar`). 0.1 ölçekte: amacın %90'ı fazla mesai,
koşudan koşuya oynama iki kat, "ipucu kapalı üç kat iyi" gürültü çıktı;
ağırlık 50→1 deneyi hedef açığının sebebinin ağırlık olmadığını gösterdi
(50 kalır). 9 + 6 + 7 test, 11 mutasyon (toplam **201**), motor **531 test**.
→ `09-motor/cozucu/coz.py` · `09-motor/cozucu/model.py` · `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_kalite_olcumu.py` · `09-motor/testler/test_fazla_mesai_tanimi.py` · `09-motor/mutasyon_kostur.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py` · `08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py` · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-0.1-95.json` · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-0.1-95-tekrar3.json` · `08-motor-testleri/gercekci-veri-seti/kalite-olcumu-0.1-95-agirlik.json` · `08-motor-testleri/gercekci-veri-seti/OKU-BENI.md` · `02-spec/v1.4-master-spec.md` §11.3 · `00-DEVIR/08-URUN-KARARLARI.md` K-57 · `00-DEVIR/06-ACIK-RISKLER.md` T-60 · `00-DEVIR/oturumlar/2026-09-30-nitelik-kapsamasi.md` §55

**2026-10-02 (00:50) · K-56 devreden kapsama iki yarıda yazıldı · T-38 kapandı**
Önceki haftanın bu haftaya taşan vardiyaları (pazar 23 → pazartesi 07)
bu haftanın ilk saatlerini kapatır: sayı `gecmis_vardiyalar`dan türetilir,
`devir_kapsama` yalnız geçmiş yokken elle (Mustafa: "sana katılıyorum").
Çözücü: atanmış/sahada/yetkinlik toplamlarına sabit, ön kontrol ve kendi
metriği; doğrulayıcı: sahte atama satırları yalnız kapsama kurallarına.
8 test, 6 mutasyon (toplam **190**), motor **516 test**. Şartnamenin on iki
karşılıksız alanının hepsi kapandı.
→ `09-motor/cozucu/model.py` · `09-motor/cozucu/teshis.py` · `09-motor/cozucu/coz.py` · `09-motor/dogrulayici/kurallar.py` · `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_devir_kapsama.py` · `02-spec/v1.4-master-spec.md` §6.4, §11.2 · `00-DEVIR/08-URUN-KARARLARI.md` K-56 · `00-DEVIR/06-ACIK-RISKLER.md` T-38

**2026-10-02 (00:10) · T-38: sabit atama = sabitleme kilidi, saat+ekip ile eşlenir ve doğrulanır · şartname örneği temizlendi**
Motor sabit atamayı ve sabitleme kilidini `sablon` ya da `ekip`+`bas`+`bit`
ile kişinin kendi şablonları içinde eşliyor (eski kilit ekibe bakmıyordu);
doğrulayıcı `KILIT_UYUMU` sabit atamaları da denetliyor (eskiden hiç
bakmıyordu). 9 test, 4 mutasyon (toplam **184**); motor **508 test**.
Şartname §11.2 örneğinden `kural_degerleri` ve `tercihler` çıktı,
`mola_tek_blok` ve sabit atama notları; değişiklik 46. T-38'de tek açık
satır: `devir_kapsama` tanımı (Mustafa'ya soruldu).
→ `09-motor/cozucu/model.py` (`_sablon_esle`, `_sabitle_satir`) · `09-motor/dogrulayici/kurallar.py` (`kilit_uyumu`) · `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_sabit_atama.py` · `02-spec/v1.4-master-spec.md` §11.2

**2026-10-01 (23:15) · K-55: PDKS'ten yalnız ham giriş-çıkış; bilinen boş gün = TShift plan geçmişi + izin satırları; yıl içi fazla mesai PDKS hamından TShift hesabıyla**
Mustafa'nın üç maddelik kararı (üçüncüde bordro önerim reddedildi: kaynak
PDKS, hesap TShift — PDKS'in hazır fazla mesai kolonu okunmaz). Motor kodu
değişmedi; içe aktarma kuralları şartname §11.2 notuna ve §6.2 yıllık tavan
satırına yazıldı (değişiklik 45). K-47'nin açık ucu ve T-77'nin veri tarafı
kapandı.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-55 · `02-spec/v1.4-master-spec.md` §6.2, §11.2 · `07-GERCEK-VERI-BULGULARI.md` §7

**2026-10-01 (23:00) · Donmuş gün tam ölçekte kanıtlandı · günsüz ihlalde "geçmiş" ölçüsü tavan kurallarıyla sınırlandı**
Mustafa'nın koşusu: taze hafta 0 sert; gün 0 dondurulup yeniden: 92.899
kısıt düştü, gün 0 aynı, 0 sert, yayınlanabilir (305 sn, ipucu kullanıldı).
Koşu bir yanlışı gösterdi: adalet dengesi (günsüz, karşılaştırma) ihlalleri
"olan oldu" sayılıyordu. Artık günsüz ihlalde yalnız tavan kuralları geçmiş
sayılabilir (`GUNSUZ_TAVAN_KURALLARI`); eksiklik/karşılaştırma kuralları
asla. 1 test, 1 mutasyon; motor **499 test**, mutasyon **180**.
→ `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_donmus_gun.py` · `00-DEVIR/08-URUN-KARARLARI.md` K-54

**2026-10-01 (21:23) · K-54 dondurulmuş gün canlandı: `mevcut_plan` girdisi, geçmiş aynen geçer ve gerçek sayılır, geçmişin kusuru çözümsüz etmez · T-29 kapandı**
Mustafa'nın onayı (ekiyle: yönetici geçmiş günleri düzenler, gelecek
günleri kilitler, çoklu seçim). Çözücü: donmuş gün satırları çıktıya aynen
(`donmus: true`), modelde sabit; yalnız geçmişe ait kısıtlar düşer, aşılmış
sınır kırpılır (`_kisit` süzgeci); yayınlanmış plan ipucu. Doğrulayıcı:
`DONMUS_GUN` plana göre bayraksız; `gecmis` işaretli ihlaller kapıdan
sayılmaz (`gecmis_ihlaller`, `metrikler.gecmis_sert_ihlal`); plansız donmuş
gün "denetlenemedi". Veri seti taze hafta; `coz-olc.py --donmus`; bekçide
yeniden planlama testi. Motor **497 test**, mutasyon **179** (yeni `donmus`
8), bekçi 21, vaka aracı 36 vaka · 36 kırmızı, altın 12. Arayüz tarafı yazılmadı.
→ `09-motor/cozucu/model.py` · `09-motor/cozucu/coz.py` · `09-motor/cozucu/teshis.py` · `09-motor/dogrulayici/kurallar.py` · `09-motor/dogrulayici/denetle.py` · `09-motor/orkestra.py` · `09-motor/testler/test_donmus_gun.py` · `08-motor-testleri/gercekci-veri-seti/` (üretici, fikstürler, vaka aracı, `coz-olc.py`, bekçi) · şartname §6.6, §11.2–11.4 · `00-DEVIR/08-URUN-KARARLARI.md` K-54 · `00-DEVIR/06-ACIK-RISKLER.md` T-29

**2026-10-01 (19:17) · CI kırmızı → "süre yetmedi" testleri yarıştan kurtarıldı (T-79, O-12)**
Push'tan sonra GitHub'da `test_sure_yetmedi.py`'nin dört testi kırmızı:
makine 60 kişilik sahneyi 1 saniyede çözdü, test çözememesini bekliyordu
(0,1 sn bütçe aslında 1 sn — T-59 tabanı; konteynerde ilk plan 1,9 sn).
Motor değişmedi. Testler artık dolan bütçeyi `sure_dolmus` fikstürüyle
enjekte ediyor (CP-SAT aramadan `UNKNOWN` der); 5 yeni mutasyon öldü,
toplam **171**; motor 481 test yeşil.
→ `09-motor/testler/test_sure_yetmedi.py` · `09-motor/mutasyon_kostur.py` · `00-DEVIR/06-ACIK-RISKLER.md` T-79 · `05-HATA-OTOPSILERI.md` O-12

**2026-10-01 (18:15) · PDKS ham verisi: `MS 00:00` bilinen boş gün değil · gece yarısı başladığı günde · saat kovaları güvenilmez**
Mustafa ham PDKS'i açtı; betik makinesinde koştu, yalnız sayı döndü.
Bulgular `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` §7 (P-2…P-5); 13 Eylül'deki
`MS` okuması düzeltildi. K-47'nin açık sorusu cevaplandı: PDKS'in `00:00`'ı
plan değil, kart okutulunca sonradan değişen takvim (1.084/1.084). Gece
yarısını aşan vardiya PDKS'te de başladığı günde — motorla aynı. Öneri karar
bekliyor (bilinen boş gün = TShift'in kendi plan geçmişi + izin satırları;
yıl içi fazla mesai bordrodan, PDKS `FM`'den değil). Motor kodu değişmedi.
→ `07-motor/pdks-ms-gece-yarisi.py` · `00-DEVIR/07-GERCEK-VERI-BULGULARI.md` · `08-URUN-KARARLARI.md` K-47 · `06-ACIK-RISKLER.md` T-77 · şartname §11.2

**2026-10-01 (17:27) · K-51 sahte sert ihlal sayısı kaldırıldı · K-52 departman çalışma saatleri + her birim için yetkinlik · K-53 hedefi aşan saate ceza · T-38 sıralandı**
Mustafa'nın dört kararı. **K-51:** çözücü çıktısındaki `metrikler.sert_ihlal`
(hep sıfır, ölçülmüyordu) kaldırıldı; altın senaryo testi beklentiyi bağımsız
denetimden okuyor. **K-52:** girdiye `departmanlar[]` (ekipler + `acik`:
"7/24" ya da gün gün pencereler); `CALISMA_SAATLERI` gövdesi iki yarıda —
çözücü kapalı saate taşan şablon-gün çiftlerini kapatıp not düşüyor, ön
kontrol kapalı şablonu ulaşıyor saymıyor, doğrulayıcı ihlal yazıyor, tanımsız
departman "denetlenemedi"; veri setinde müşteri hizmetleri hafta içi 07–23,
hafta sonu 08–19. Her birim için yetkinlik gerekliliği (4 satır) ve üreticide
taşıyıcı tabanı; iki kabul kaydı kalktı (T-63 kapandı). **K-53:** `HEDEF_ASIMI`
yumuşak kural, ağırlık profilden (3/1/4), hedefin altı her profilde daha
pahalı; T-54 kapandı. **T-38:** seviye 🟡, sıra verildi; `sure_butcesi_sn`
arama bütçesi, `istek_id` çıktıya geri — servis testi gerçek HTTP ile.
Motor **481 test**, mutasyon **166** (yeni gruplar: çalışma saatleri 8, hedef
aşımı 4 — hepsi öldü), vaka aracı 37 gövde · 36 vaka · 36 kırmızı, bekçi 20
(7 dk 41 sn), altın senaryolar 12. ⚠ Tam ölçek bu değişikliklerden sonra
yeniden koşulmalı.
→ `09-motor/cozucu/model.py` · `09-motor/dogrulayici/kurallar.py` · `denetle.py` · `09-motor/servis.py` · `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py` · `00-DEVIR/08-URUN-KARARLARI.md` K-51…K-53 · `02-spec/v1.4-master-spec.md` değişiklik 39–42

**2026-10-01 (16:45) · K-49 yayın kapısı "bakamadım"ı görüyor · K-50 çok yetenekli çalışan bütün ekiplerine sayılır · yıllık fazla mesai tavanının gövdesi yazıldı · T-18, T-21, T-67 kapandı**
Mustafa iki kararı verdi. **K-49 (T-18):** motorun kontrol edemediği aktif
kural kapıdan geçemez — yasal+sert **engeller**, firma+sert yetkili gerekçe
yazarak kabul edene kadar **bekler** (`girdi.denetim_disi_kabul`), yumuşak
yalnız **raporlanır**; iki kanal kapıya bağlı (`uygulanmayan_kurallar`,
`eksik_boyutlar[denetlenemedi]`), kırpma raporları hariç. Kapı kapanınca
veri seti üç yerden ısırdı: parametresiz yetkinlik kuralı ve gövdesiz
çalışma saatleri kuralı için gerekçeli kabul kaydı; **yıllık fazla mesai
tavanı yasal ve gövdesizdi → gövdesi yazıldı** (iki yarıda: yıl içi toplam
`yil_ici_fazla_mesai_saat`, biliniyorsa bu haftanın fazla mesaisi kalan payı
aşamaz, bilinmiyorsa K-42 ile atlanır ve bildirilir; veri setinde her 50
kişiden biri tavanın kıyısında). Gece yarısını aşan vardiya kuralı *"ihlal
üretmez"* diye kayıtlı, vaka aracına *"bilerek vakasız"* sınıfı (T-67).
**K-50 (T-21):** sabah önerdiğimin tersi — Mustafa'nın sahasında hem satış
hem backoffice yapabilen kişi o saatte iki birim için de yer doldurur; atama
üye olduğu **bütün ekiplere** sayılır (kişi sayısı ve nitelik), çıktıdaki
`ekip` vardiyanın ekibi, görünürlük `metrikler.baska_ekipten_kapsama`,
kiracı seçeneği `cok_ekipli_sayim: "tek"`. Değişen taraf doğrulayıcı.
Motor **459 test**, mutasyon **154** (yeni gruplar kapı 6, çok ekipli 11,
yıllık 9 — hepsi öldü), 35 gövde · 34 vaka · 34 kırmızı. Şartname: §4.5,
§6.2, §8.2, §11.2, §11.4; değişiklik listesi 36–38.
→ `09-motor/dogrulayici/denetle.py` · `kurallar.py` · `09-motor/cozucu/model.py` · `coz.py` · `teshis.py` · `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py` · `00-DEVIR/08-URUN-KARARLARI.md` K-49, K-50

**2026-10-01 (15:45) · Tam ölçek sınavı geçti · şartname yazı borcu ödendi · mutasyon 128/128**
Mustafa'nın 900 sn koşusu: birinci aşama **10,3 sn** (üç koşudur 120 sn'de
başarısızdı), ana aşamada ilk plan **48,9 sn**, 2.476 atama, 0 sert,
yayınlanabilir; kaydedilen planda 9.171 mola, üst üste binen sıfır; bir yarı
zamanlı tam 45,00'de, temiz. T-78 sahada kapandı, T-60'ın plan bulma yarısı
kapandı (kalite %99 uzaklıkta duruyor). K-48 kesinleşti. Mutasyon tam koşusu
**128 · hepsi öldü**. Şartname v1.4 yerinde güncellendi: §6.3 (K-44, K-45),
§6.4 (K-41, T-62/T-63), §6.5 (K-46), §8.4 (`gece_vardiyasi`, K-40/K-43),
§11.2 (K-42 lookback), §11.3 (süre kalemleri, `ilk_cozum_sn`, `belirsiz_
kurallar`, K-48), §11.4 (çıktı kanalları); değişiklik listesi 29–35.
Mustafa'ya iki karar soruldu: T-18 (üç kademeli yayın kapısı; kodu hazır,
13 test) ve T-21 (şablon tek ekibe ait).
→ `02-spec/v1.4-master-spec.md` · `00-DEVIR/06-ACIK-RISKLER.md` T-60, T-78 · `08-motor-testleri/gercekci-veri-seti/olcum-sonucu-95.json`

**2026-10-01 (14:00) · T-78'in bedeli: tam ölçekte plan yok · birinci aşama molaları sabitleyerek arıyor, ipucu tam · K-48**
Mustafa düzeltmeyi push edip tam ölçeği koşturdu: **plan bulunamadı**
(`sure_yetmedi`, 0 atama; dün 654 çözüm). Model çözümsüz değil (her şablonda
geçerli yerleşim var), arama ağırlaştı: +12 bin kısıt, 20 dk'lık mola iki
çeyrek kapatıyor, kurma 55 → 78 sn; çözücü zaten sınırdaydı. Eski/yeni kod
0.2 ölçekte yan yana ölçüldü: ikisi de 18 sn'de birinci aşamayı geçiyor,
ilk plan 57–101 sn — yani sorun ölçekle büyüyen *plan bulma*. **Değişen
(`cozucu/coz.py::_ipucu_ver`):** (1) birinci aşamada her şablonun molaları
ideale en yakın tek noktaya sabitleniyor — seçilmeyen adayların alanı [0,0],
kısıt eklenmiyor, sonra geri [0,1] (`Model.sabit_mola_secimi`); (2) ipucu
**bütün** değişkenlere yazılıyor — eskiden ceza değişkenleri boştu, CP-SAT
yarım ipucuyu 10 çelişkide bırakıyordu. 0.2 ölçekte birinci aşama 18 →
**1,7 sn**, ana aşamanın ilk planı → **21 sn**. 0.3 ölçekte (151 kişi, 300
sn) tam ölçeğin hastalığı yeniden üretildi: eski kod ipucu eldeyken ana
aşamada **hiç plan bulamadı** (265 sn, 0 atama); yeni kod 2,5 sn + ilk plan
25 sn, 306 çözüm. ⚠ Tam ölçekte ölçülmedi.
Ana aşama molaları serbest arıyor (K-32 korunur); sabit molalı başlangıca
demir atma riski T-60'ın kalite ölçümlerine not edildi. `coz()` artık
önceden kurulmuş model alıyor (`kuruldu=`); `coz-olc.py` modeli bir kez
kuruyor. **K-48:** bütçe = arama süresi, model kurma ayrı gösterilir
(Mustafa'nın önerisi, sabah onayı). 5 test (`test_ilk_asama.py`), 6
mutasyon. Motor **421 test**, mutasyon **128**.
→ `09-motor/cozucu/coz.py` · `09-motor/cozucu/model.py` · `09-motor/testler/test_ilk_asama.py` · `00-DEVIR/06-ACIK-RISKLER.md` T-60, T-78 · `00-DEVIR/08-URUN-KARARLARI.md` K-48

**2026-10-01 (gece) · T-78 kapandı: 20 dakikalık mola çeyreğe sığmıyordu · `ilk_cozum_sn` · K-48 sorusu**
Mustafa tam ölçeği üç kez koşturdu: 900 sn temiz, 1.200 sn **1 sert ihlal**
(PART_TIME_LIMIT), gece commit'inden sonra 900 sn yine temiz. Plan
beklenmeden sebep koddan bulundu: müşteri hizmetleri şablonlarındaki **3×20 dk**
dinlenme molası çeyrek ızgarada `round(1,33) = 1` çeyrek sayılıyordu — pencere
aralığı, yemek–dinlenme çakışma kısıtı ve molanın kapattığı dilimler üçü de
bu hesapla. Gerçekte iki mola **5 dk üst üste** binebiliyor (13:30–13:50 ile
13:45–14:05; 10:45–11:05 ile 11:00 yemeği); doğrulayıcı üst üste bineni tek
aralık sayıp (T-27) net çalışmayı 5 dk fazla görüyor; tam 45,00 saatteki yarı
zamanlıda bu tek başına sert ihlal. Sahne şablonlarında sayıldı: M-SABAH'ta
2.880 yerleşimin **822'sinde** ayrışma; 15 dk'lık molalı şablonlarda sıfır.
⚠ İlk hipotez (sığmayan mola üretilmiyor) **yanlıştı**. Düzeltme
(`09-motor/cozucu/model.py`): çeyrek sayısı **yukarı** yuvarlanır
(`_ceyrek_yukari`); çakışma **gerçek zamanda** ölçülür (`_gercek_kesisiyor`,
uç uca değen serbest); ardışık dinlenmeler arasına **emniyet kemeri**;
politika vardiyaya sığmıyorsa **nota** yazılır (eskiden üst üste bindirerek
"sığıyordu" — geçersiz plan). ⚠ Açık etki: yalnız fiziksel olarak üst üste
binen yerleşimler gitti; 20 dk mola saha modelinde artık iki çeyrek anı
kapatıyor (doğrulayıcıyla aynı), MOLA_KAPSAMASI cezası o şablonlarda biraz
artabilir. 9 test (yerleşim çiftleri, dilim örneklemesi, 3–12 saat tarama,
uçtan uca 45,00 saat, kemer, sığmayan not), **6 mutasyon hepsi öldü**
(toplam 122). `ilk_cozum_sn` çıktıya eklendi (T-60: ana aşama ilk planı kaçıncı
saniyede buldu; `coz-olc.py` yazıyor). **T-59'a soru:** "en fazla 900 sn"
deyip 958 sn — model kurma bütçenin dışında; duvar saati olsun mu (K-48 adayı).
**T-66'ya not:** motorun `toplam_saat`/`fazla_mesai_saat` metriği politikayı
düşmüyor. Motor **416 test**, bekçi 20, 33 gövde · 33 vaka, sahte PDKS 0 habersiz.
→ `09-motor/cozucu/model.py` · `09-motor/testler/test_net_saat_uyumu.py` · `00-DEVIR/06-ACIK-RISKLER.md` T-78, T-59, T-60, T-66

**2026-09-30 (gece) · Beş karar uygulandı (K-43…K-47) · T-72, T-73, T-74, T-75, T-76, T-59 kapandı · T-78 açıldı**
Mustafa döndü; hukukçu olmadığı için iki yasal soruyu çevrimiçi kaynaklarla
bana bıraktı, kalanını kararlaştırdı. **K-44:** Yargıtay 9. HD 2020/17967 —
gece postasının (yarısından çoğu 20:00–06:00'da) **bütün** net süresi 7,5
saati geçemez; 22:00–08:00 artık yasa dışı. **K-45:** gece haftası =
haftanın saatlerinin yarısından çoğu gece postasında; üst sınır 2 = iki
hafta gece, iki hafta gündüz; sıkı okuma ayar olarak kaldı. **K-43:** gece
işareti yönetmelikten otomatik, firma yalnız ekler — K-40'ın üç bekçi testi
tersine döndü. **K-46:** hafta sonu = iki gün de; gün = saatlerin yarısından
çoğu. **K-47:** geçmiş eksik raporuna yönetici bakar, kişi başına özet.
**Ölçüldü:** üçüncü hafta iki haftalık geçmişle artık **çözülüyor, 0 ihlal**
(eski tanımla iki koşuda çözümsüzdü); tam ölçek 1.200 sn koşusu süre sözünü
tuttu (121,8 + 1.078,2 = 1.200,0) ama **1 sert ihlalle** döndü (**T-78** 🔴,
yarı zamanlı tavanı; plan kaydedilmediği için sebep açık, araç artık planı
yazıyor). Teşhis üç cevap veriyor (T-76). ⚠ 116 mutasyonun ilk turunda 10
yaşadı — hepsi test boşluğu, hepsi kapatıldı; ⚠ T-54'ün tuzağı çözücü
testinde bir kez daha ısırdı (bedava altıncı vardiya). Motor **406 test**.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-43…K-47 · `00-DEVIR/06-ACIK-RISKLER.md` T-78 · `02-spec/v1.4-hazirlik/02-mevzuat-arastirmasi.md` bölüm 3b · `09-motor/testler/test_hafta_kurallari.py` · `test_rapor_ozeti_ve_teshis.py`


**2026-09-30 (akşam, 2) · Üç hafta: ardışık hafta sonu limiti üçüncü haftayı kilitliyor (T-75) · sahte PDKS · T-59 düzeltildi**
Mustafa'nın iki aşamalı yolu **üç haftaya** uzatıldı. Üçüncü hafta, iki haftalık
geçmişle **iki bağımsız koşuda da çözümsüz**; ardışık hafta sonu limiti
kaldırılınca çözülüyor (**T-75** 🔴). Sebep yapısal: 6 günlük desende cumartesi
ya da pazardan biri mutlaka çalışılıyor, bugünkü tanımla herkes her hafta sonu
*"çalışmış"*; hafta hafta çözen motor gelecek haftayı görmüyor — 45 kişinin 29'u
iki hafta sonu da çalıştı. Çözücünün kendi teşhisi *"engelleyen: yok"* dedi
(**T-76**: 10 saniyelik deneme bu ölçekte yetmiyor). **Sahte PDKS** (Mustafa'nın
ikinci yolu) kuruldu: PDKS gerçekleşenin %57'sini yakaladı; eksik geçmişle
yapılan planda gerçek geçmişe göre **7 ihlal** kaçtı (beşi yasal) — **hepsi**
raporda haber verilmişti, ama **141 satırla** (**T-77**). **T-59 düzeltildi**:
birinci aşama süre bütçesinin içinden pay alıyor; tam ölçekte yeniden
ölçülmedi. ⚠ `06-veri/anonim/` boş — sahte PDKS'in oranlarının çoğu varsayım,
dosyada tek tek işaretli. Motor **359 test**, bekçiler **20**, mutasyon **88 ·
hepsi öldü**, açık 🔴 **dokuz**.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-59 · T-75 · T-76 · T-77 · `08-motor-testleri/gercekci-veri-seti/sahte_pdks.py` · `08-motor-testleri/gercekci-veri-seti/uc-hafta-sonucu.json` · `09-motor/testler/test_sure_butcesi.py`


**2026-09-30 (akşam) · Gece postası devri (yasal) ve ardışık hafta sonu limiti yazıldı · T-69, T-71 kapandı · T-72, T-74 🔴 açıldı**
Mustafa dışarıdayken, soru sormadan. İki kural iki motor yarısında da yazıldı;
geçmiş okunduğu için (T-28) artık yazılabilirdi. **Yönetmeliğin tam metni
okundu** ve şartnamede olmayan iki fıkra çıktı: md. 8/3 iki haftalık nöbetleşmeye
izin veriyor (**T-73**); md. 7/2 geceyi tanımlıyor — *"çalışma süresinin
yarısından çoğu gece dönemine rastlayan"* posta. Yasal kural bu tanımı kullanıyor,
firma işaretini (K-40) **bilerek kullanmıyor**. *"Bir iş haftası gece
çalıştırılan"* tanımlı değil — **en sıkı okuma** uygulandı: haftada tek gece
yeter (**T-72** 🔴, karar bekliyor). **Ölçüldü:** 49 kişide ikinci hafta geçmişsiz
çözülünce 11 kişi iki hafta üst üste gecede, toplam 30 sert ihlal; geçmişle
**çözüldü, 0**. **T-74** 🔴: yasal gece sınırı yalnız pencereye düşen kısmı
ölçüyor; yönetmeliğe göre gece postasının bütün süresi 7,5 saati geçemez —
gerçek müşteride 16:00–01:00 deseni 82 kez; bilerek değiştirilmedi.
**T-69 + T-71 kapandı:** işaretsiz vardiyanın tahmini artık md. 7/2 (00:00–08:45
gece, 13:00–21:00 değil); doğrulayıcının adalet boyutu işareti okuyor. ⚠ Beş eski
testin sahnesi eski tahmine yaslanıyordu: biri kırmızı yandı, üçü **yeşil kaldı
ama sahneleri sessizce değişmişti** — dördüne eski sonuç açıkça işaret olarak
yazıldı, biri aynı sınırı sınayan vakaya taşındı. ⚠ Mutasyon iki boşluk daha
yakaladı. Motor **353 test**, **33 gövde · 33 vaka · 33 kırmızı**, mutasyon
**79 · hepsi öldü**.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-69 · T-71 · T-72 · T-73 · T-74 · `00-DEVIR/08-URUN-KARARLARI.md` K-25 · K-40 · `09-motor/testler/test_hafta_kurallari.py` · `09-motor/testler/test_gece_tespiti.py`


**2026-09-30 (öğleden sonra) · T-28 kapandı — geçmiş veri iki tarafta da okunuyor**
Risk listesinde birinci sıradaki madde. **Ölçüldü, Mustafa'nın önerdiği iki
aşamalı yolla:** hafta 1'in planı hafta 2'nin geçmişi oldu; hafta 2 geçmişsiz
çözülünce geçmişi bilen denetçi **27 sert ihlal** gördü (10 hafta tatili, 7
vardiya arası dinlenme, 10 ardışık gün) — 49 kişilik tek haftada, hepsi
bugüne kadar **görünmez**. Geçmişle: **0**. Beş kural pazartesi 00:00'da artık
kör değil; geçmişin kendi ihlali plana yazılmıyor; K-42'nin rapor kanalı
(`gecmis_eksik`) yalnız sonucu değiştirebilecek bilinmeyen günü yazıyor.
⚠ İki aşamalı testin ilk hâli çözücü geçmişi hiç okumasa da yeşildi —
sabit atamalı, deterministik bir sahneyle yeniden yazıldı. ⚠ Gerçek ölçekli
sürüm CI'da zamanlamadan kırmızı yandı; elle koşulan araçta kaldı.
**T-70 (aynı gün kapandı):** mutasyon denemeleri eski bytecode ile
koşabiliyordu (aynı uzunlukta değişiklik, aynı saniye). `mutasyon_kostur.py`
yazıldı; bu oturumun **42 mutasyonu yeniden koşuldu, hepsi öldü.**
**T-69:** işaretsiz erken saatli vardiya (00:00–08:45) iki tarafta da gece
sayılmıyor — PDKS kaydında işaret olmayacağı için artık önemli.
Motor **274 test** yeşil.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-28 · T-69 · T-70 · `08-motor-testleri/gercekci-veri-seti/iki-hafta-olc.py`


**2026-09-30 (gece, 3) · İki firma sınırı: asgari vardiya süresi, ardışık gece limiti**
Önce kendi sınıflandırmamı düzelttim: *"karar gerektirmeyen beş firma kuralı"*
dediklerimin yalnız **ikisi** öyleydi. Üçü karar istiyor: çalışma saatleri
(departman açılış/kapanış saatleri §11.2 girdisinde yok), ekip sürekliliği
(anlamı belirsiz — 500 kişinin hepsi tek ekipte, *"aynı ekip"* okuması boş
kalır), vardiya rotasyon yönü (çözücüde yüz binlerce kısıt; T-60 açıkken ağır).
**Asgari vardiya süresi:** ölçü **brüt** — bilerek; net ölçülseydi firmanın kendi
4 saatlik şablonları (09–13, 17–21) kendi 4 saat kuralını her kullanımda
çiğneyecekti. **Ardışık gece limiti:** gece = K-40'ın işareti; arada gündüz
vardiyası seriyi kırar; yalnız plan haftası (T-28). Bu kez testler gövdeden
**önce** yazıldı: 17 test, 10 gerçek kırmızı; 8 mutasyon, sekizi de öldü.
Veri setinde ardışık gece limiti **ısırabilir** (B-AKSAM gece işaretli) —
küçük ölçekte plan yine temiz çıktı. Motor **242 test**, **31 gövde · 31 vaka ·
31 kırmızı**.
**T-28'e ek:** Mustafa geçmiş verinin gerçekte **PDKS'ten** geleceğini söyledi
ve iki test yolu önerdi. ⚠ Gerçek veri P-1: kayıtların yalnız %18'i dolu — baskın
sorun sapma değil **eksik kayıt**; ve şartname *"lookback eksikse motor
çalışmaz"* diyor.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-28 · `09-motor/testler/test_firma_sinirlari.py`


**2026-09-30 (gece, 2) · `GECE_VARDIYASI_AZAMI` — yasal gece sınırı yazıldı (K-26)**
Mustafa kalan kurallar arasından bunu seçti: hukuki risk taşıyan tek yazılabilir
kural. Önce kendi sözümü düzelttim — dün *"mantıklı grup üç yasal kural"*
demiştim; üçün ikisi geçmiş hafta verisine (T-28) bağlı çıktı. Gövdesiz 12
kural tek tek okundu: beşi bugün yazılabilir, dördü T-28'e, biri `tercihler`
alanına bağlı, biri (`GECE_YARISI_ASAN`) şartnameye göre **zaten ihlal
üretmez** — sayımımızda sınıflandırma hatası (T-67).
**Kural:** gece penceresine (20:00–06:00) düşen **net** çalışma 7,5 saati
geçemez; pencere gün sınırını aşarak hesaplanır (Z-5). **Sektör istisnası kişi
bazlı:** turizm/özel güvenlik/sağlık/petrol **ve** çalışanın yazılı onayı varsa
sınır o çalışan için kalkar. İki yeni girdi alanı: `sektor`,
`gece_calisma_onayi`. 20 test, 11 mutasyon, hepsi öldü.
**T-68:** çözücü sınırı **brüt** ölçüyor — bilerek, çünkü net ölçü mola
yerine bağlı ve modeli ağırlaştırır (T-60). Yasal planı reddedebilir, yasadışı
plan üretmez; ayrışma güvenli yönde ve not yazılıyor.
⚠ **Veri seti kuralı zorlamıyor** (en uzun gece örtüşmesi 7,00 saat); zorlayan
testler ve ihlal vakası. Sahnenin sektörü bilerek istisna dışı.
Motor **225 test**, **29 gövde · 29 vaka · 29 kırmızı**.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-26 · `00-DEVIR/06-ACIK-RISKLER.md` T-67 · T-68


**2026-09-30 (gece) · CI kırmızı yandı — motorun kendi metriği yanlış sayıyordu**
Mustafa'nın koşumu: *"sert ihlal 0, asgari kapsama %99,76."* Çelişki gibi
duruyordu, değildi — iki sayı da motorun **kendi** raporundan geliyor.
**T-65:** `coz.py::_metrikler` kapsamayı `int(a["bit"])` ile sayıyordu; vardiya
07:00–16:15 ise `int(16.25)` = 16 ve saat 16 **dışarıda** kalıyordu. K-34'ten
beri şablonların çoğu kesirli bittiği için bu istisna değil kural: 415 hücrenin
biri eksik sayıldı. ⚠ **T-58 ile aynı aile** — aynı `int()` varsayımı 29
Eylül'de doğrulayıcıyı çökertmişti, orada düzeltildi, **çözücüdeki kopyasına
bakılmadı.** ⚠ Test rastgele yeşil yanıyordu: hangi hücrenin açıkta kalacağı
plana bağlı, benim makinemde geçti CI'da yandı. Düzeltildi; üç test, ikisi
kırmızı başladı, mutasyon ikisini birden öldürdü. **Bekçi de değişti:**
kapsama artık **doğrulayıcının** sayısıyla ölçülüyor ve iki tarafın anlaştığı
ayrıca sınanıyor. **T-66 açıldı:** `sert_ihlal` ölçülmüyor, **sabit sıfır**
yazılıyor — yalnız motorun kendi kısıtlarını kapsar, gövdesi olmayan 12 kural
o sıfıra girmez. §11.3 çıktı sözleşmesi Mustafa'nın kararını bekliyor.
Motor **205 test** yeşil.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-65 · T-66


**2026-09-30 (akşam) · K-41 · Molada olan sayılır · T-61, T-62, T-63'ün rol tarafı kapandı**
**K-41:** nitelik kapsamasında mola **sahadan çıkarmaz** — Mustafa: *"Sahada bir
müdürün işi 15 dk mola süresini bekleyebilir."* ⚠ Değişen taraf **doğrulayıcı**
oldu; ben şartnamenin harfine bakıp çözücünün düzeltileceğini varsaymıştım
(T-57 refleksi), yanlıştı. İki test **tersine çevrildi**, silinmedi.
`SAHADA_ASGARI` molayı düşmeye devam ediyor — ayrım bilerek.
**T-62 kapandı:** saat listesi yoksa açık saatlerin hepsi, `ekip` yoksa saha
çapı, kontrol çeyrek bazında; niteliği taşıyan kimse yoksa kısıt değil **not**.
⚠ Bir testim mutasyondan sağ kurtuldu: *"atandı mı"* sorusu bu motorda hiçbir
şey kanıtlamıyor (fazladan atamanın maliyeti yok, T-54). İmkânsız gereklilikle
yeniden yazıldı.
**T-63'ün rol tarafı kapandı:** Mustafa *"yalnız gündüz saatlerinde 1 lider"*
dedi; her ekibe ayrı gereklilik satırı kondu (08:00–20:00). ⚠ Gereklilik konunca
0.1 ölçekte plan **kanıtlanarak çözümsüz** kaldı — 2 lider × 6 gün = 12
lider-günü, gereken 14. Sayıyı 4'e çıkarmak da yetmedi; taban *"4 kişi"* değil
**"gündüz vardiyası yazılabilecek 4 kişi"**. Üreticiye ekip başına 4 lider
tabanı kondu; tam ölçekte hiçbir şey değişmiyor. Motor **202 test** yeşil.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-41 · `00-DEVIR/06-ACIK-RISKLER.md` T-61…T-63


**2026-09-30 · Rol ve yetkinlik kapsaması doğrulayıcıya bağlandı**
Gövdesiz 14 kuralın ikisi **çözücüde vardı, doğrulayıcıda yoktu**: motor o iki
kural için kendi işini kendi onaylıyordu (#7.6'nın tam tersi). Gövdeler
şartnameden okunarak yazıldı — çözücü kodu bilerek okunmadı (T-19'un dersi).
14 test, 9'u kırmızı yandı; beş mutasyon denendi, biri ilk turda **yaşadı**
(ekip süzgeci) ve yeni bir testle öldürüldü. Parametresiz gereklilik satırı
artık `eksik_boyutlar` kanalından bildiriliyor: *"hangi niteliğin arandığı
bilinmiyor — denetlenemedi."*
**Bağımsız denetim ilk gününde iki bulgu buldu.** **T-61:** şartname *"sahada"*
diyor, çözücü **atanmış** kişiyi sayıyor — üç kişinin yemeği aynı saate düştü,
o saatte sahada takım lideri kalmadı, çözücü kendi ölçüsüne göre kuralı
sağlıyor (T-57'nin aynı ailesi). **T-62:** `saatler` yazılmazsa çözücünün iç
döngüsü hiç çalışmıyor — aktif bir SERT kural modele **tek kısıt koymuyor**;
`ekip` yazılmazsa tersine plan **çözümsüz** kalıyor. Ölçüldü: 49 kişide aynı
plan, gereklilik konunca **1.238 sert ihlal** ve `yayınlanabilir` False.
**T-63:** veri setinde rol/yetkinlik kapsaması `parametreler` **olmadan**
tanımlı, `SAHADA_ASGARI` ise 0 — üç kural aktif ama hiçbir şey istemiyor.
**T-64 kapandı (aynı gün):** ihlal vakası aracı `basarili / len(VAKALAR)`
yazıyordu, yani kendi listesini sayıyordu; vakası olmayan gövde paydada hiç
görünmüyordu. Evren artık doğrulayıcının kural kayıt sözlüğü —
**28 gövde · 28 vaka · 28 kırmızı · eksik sıfır**. Motor **198 test** yeşil.
→ `00-DEVIR/06-ACIK-RISKLER.md` T-61…T-64 ·
  `00-DEVIR/oturumlar/2026-09-30-nitelik-kapsamasi.md`


**2026-09-29 (akşam) · Veri seti baştan kuruldu · K-37 · K-38 · K-39 · K-40**
Mustafa 350 kişilik seti *"en zor senaryo"* diye anlattığım için uyardı:
*"Beni yanılttın. Konuyu çözmek için problemi daraltma bir daha!"* Ölçülünce
haklı çıktı — 15 kuralın gövdesi yok, 13'ü hiç zorlanmıyor, kapasite talebin
2,3 katı, 45 saatlik sözleşme ulaşılamaz. Yerine **500 kişilik iki set**
kuruldu (%85 ve %95 doluluk, tek fark talep tablosu; 17 şablon, 40 kural,
19.630 kişi-saat kapasite). Dört ürün kararı verildi:
**K-37** *"imkânsız"* ile *"yetiştiremedim"* ayrı cevaplar — süre dolduğunda
teşhis **koşmuyor**, kullanıcı *"neden olduğunu araştır"* derse koşuyor ama
cevabın kanıtlanmadığı çıktıda yazılı (**T-23 ve T-48 kapandı**).
**K-38** haftalık 45 saat **normal** çalışma sınırı, toplam tavan değil —
fazla mesai yolu vardı, hiç açılamıyordu.
**K-39** tam zamanlının sözleşme saati **doldurulur** (izin oranında düşer,
yeni alan `gun_sayisi`); yarı zamanlıya kişi başı saat **girilmez**, tavan
mevzuattan gelir.
**K-40** *"gece vardiyası yapamaz"* ve *"bu vardiya gece vardiyasıdır"*
işaretleri — tahmin işareti **ezmez**.
Set kurulurken üç hata buldu: çözücü ile doğrulayıcı *"net saat"*i farklı
hesaplıyordu (geçerli planda 28 sert ihlal), kesirli vardiya bitişi
doğrulayıcıyı **çökertiyordu**, ve K-38 doğrulayıcı tarafına uygulanmamıştı.
⚠ Mutasyon iki kez boşluk yakaladı; ikisi de benim yazdığım `assert True`
ile biten testlerdi. Motor **184 test** yeşil, zor set bekçileri **12** test.
**Tam ölçek ilk kez çözüldü** (638.572 değişken, 2.493 atama, **0 sert
ihlal**, `yayınlanabilir` True) **ama optimuma %98,3 uzak** ve 900 saniye
istenen koşu 1.078 sürdü → **T-59** (bütçe aşımı, mekanik) ve **T-60**
(kalite yok, önce dört ölçüm).
→ `00-DEVIR/08-URUN-KARARLARI.md` K-37…K-40 · `00-DEVIR/06-ACIK-RISKLER.md`
  T-56 · T-59 · T-60 · `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py`


**2026-09-29 · 350 kişilik set otomatik koşuya bağlandı · K-36**
Set 28 Eylül'de bir saatte altı hata bulmuştu ama **elle** çalıştırılıyordu;
artık her `git push`'ta koşuyor. Tam ölçekli çözüm CI'a konmadı (~16 dk):
**çözmeden** ölçülenler 350 kişide, çözüm gerektirenler 0.1 ölçekte.
**K-36:** arama işçisi sayısı artık makinenin çekirdek sayısından okunuyor.
2 çekirdekte fark büyük (eski sabit 8 işçi optimuma **%23,6**, 2 işçi **%7,0**);
küçük sahnede ise hiçbir fark ayırt edilemedi. **350 kişide kapandı:** 6
çekirdekli makinede hem 120 hem 360 saniyede en iyi satır **çekirdek kadar
işçi** (2 işçiye göre amaç üçte bir düşüyor), 12 işçi 6'yı geçemedi.
`cekirdek-olc.py` artık `--tekrar` ile koşuyor, zar payını satırlar arası
farkla karşılaştırıyor ve ayırt edemediğinde karar verdirmiyor.
**Yeni ölçüm sorusu (T-50):** aynı sahne 900 sn'de optimuma %10, 360 sn'de
%42 uzaktı — süre mi **iki aşama** mı, ayrılmadı.
**T-48 hipotez olmaktan çıktı:** bütçe dolduğunda motor teşhise giriyor ve
45 saniyelik bütçe **470 saniye** sürüyor — hem yanlış olabilecek bir cümle,
hem on kat bekleme. Motor **146 test** yeşil.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-36 · `00-DEVIR/06-ACIK-RISKLER.md` T-48


**2026-09-28 · Gerçekçi veri seti (350 kişi) ve K-35**
Üç ekipli, 14 vardiya şablonlu, 39 kurallı bir sahne kuruldu ve tam ölçekte
çalıştı: **1.757 atama, 0 sert ihlal**, %100 asgari kapsama, optimuma %10 uzak.
Bir saatte altı bulgu çıktı (T-45…T-49), beşi aynı gün kapandı.
**K-35:** süre seçimi (10/15/30 dk), sonuç kartında **kanıtlanmış** optimuma
yakınlık, ve plan başına bir kez *İyileştir* — plan asla kötüleşmez.
Motor **137 test** yeşil.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-35 · `08-motor-testleri/gercekci-veri-seti/`

**2026-09-28 · K-34 · Motorun zaman birimi çeyrek saat oldu (Z-7)**
Mustafa: *"Molalar zaten 15 dk lık dilimlere dağıtılıyor, doğrusu bu."* Saat izgarası
kolaylık değil **hataydı**: 15 dk'lık dinlenme bir tam saat kaplıyordu (yemekte hata
yoktu, **1.00×**; dinlenmede **4.00×** — önceki "2.29×" ikisini harmanlıyordu).
T-44 **kapandı**: eşik `4F → 12F/7`, taban 3 için 12 kişi yerine 6. Çözüm süresi
40 kişide 0.78 sn. Yol üstünde bir sessiz geçiş bulundu ve kapatıldı: 14:15'te
sahada sıfır kişi varken doğrulayıcı hiçbir ihlal yazmıyordu. Motor **120 test** yeşil.
→ `00-DEVIR/08-URUN-KARARLARI.md` K-34 · `02-spec/v1.4-master-spec.md` Z-7

**2026-09-28 · K-33 · `SAHADA_ASGARI` — firma *"sahada en az N kişi"* diyebiliyor**
Molada olan sahada sayılmaz; `ASGARI_KAPSAMA` *atanmış*ı sayar, bu *sahadaki*ni.
⚠ Kural bir kez **yanlış mantıkla** yazıldı (taban talep tablosuyla sınırlanıyordu,
bir test de bunu sabitliyordu); Mustafa yakaladı, aynı gün düzeltildi ve test
tersine çevrildi. Katalog **39**, motor **109 test** yeşil. Yeni 🔴 T-44:
bugünkü mola geometrisi kuralı boğuyor (`N ≥ 4F`).
→ `00-DEVIR/08-URUN-KARARLARI.md` K-33 · `00-DEVIR/06-ACIK-RISKLER.md` T-44

**2026-09-28 · Dinlenme molaları çözücüye bağlandı — K-32 tamamlandı**

Motor artık firmanın mola politikasını **plana çeviriyor**. *"60 dk yemek +
3×15 dk ücretli kısa mola"* politikasıyla üretilen gerçek plan:

```
C3  11:00 dinlenme · 12:00 yemek · 13:00 dinlenme · 16:00 dinlenme
C2  12:00 dinlenme · 13:00 yemek · 14:00 dinlenme · 15:00 dinlenme
C1  12:00 dinlenme · 13:00 dinlenme · 14:00 yemek · 15:00 dinlenme
```

**Yemekler kişiler arasında kaydırılmış** — üçü de 3–5 saat penceresinde ama
farklı saatlerde. "Adil ve yönetilebilir mola operasyonu" istenen buydu.

**Asıl zorluk `_sahada`'daydı ve reification'sız çözüldü.** *"Sahada olmak"*
= atanmış **ve** hiçbir mola bu dilimi kapsamıyor — bir VE bağlacı, çarpım
gerektiriyor gibi görünüyor. Gerektirmiyor: molalar birbirini kesmiyorsa
*"molada olmak"* bir **toplamdır**.

```
sahada = (kapsamayan yemek seçenekleri) − (kapsayan dinlenmeler)
```

İkisi de doğrusal, yardımcı değişken yok. Çakışmama kısıtı bu yüzden yalnız
adil plan için değil, **bu aritmetiğin geçerliliği** için de şart — iki mola
aynı dilimi kapsarsa sonuç eksiye düşer. Bekçisi
`test_molalar_BIRBIRINI_kesmez`.

**Model neden büyümedi:** aday pencereleri eşit dağıtımdan geliyor ve ayrık,
bu yüzden dinlenmeler arası çakışma kısıtı **hiç yazılmıyor** — yalnız
yemekle çakışma yazılıyor.

**Yol üstünde bir tutarsızlık bulundu:** `_mola_baslangiclari` yemek süresini
politikadan alıyordu ama `_mola_dilimleri` hâlâ `mola_dk`'ya bakıyordu.
Politika farklı bir süre verdiğinde kapsama dilimleri yanlış hesaplanacaktı.
Düzeltildi.

**Ölçümler:** motor **103/103** · altın senaryolar **12 geçti, 4 atlandı** ·
fikstür denetleyicisi **11/11**.

---

**2026-09-25 · K-32 uygulandı: mola tipleri, dört süre, göreli pencere**

**Motor.** `dinlenme` / `yemek` tipleri · üç süre ayrı ayrı hesaplanıyor ve
raporlanıyor (`brut_saat`, `toplam_saat` = çalışma, `ucret_saat`) · sözleşme
karşılaştırması artık **ücret** saatine bakıyor · dört yeni kural:
`MOLA_YERLESIMI` (yumuşak), `MOLA_TIPI_ZORUNLU`, `MOLA_ASGARI_BLOK`,
`YEMEK_TEK_BLOK` · mola politikası firmadan ve şablondan okunuyor (şablon
ezer) · mutlak mola penceresi kaldırıldı, yerine vardiyaya **göreli** pencere.

**Şartname.** §6.2 kataloğuna dört kural (**34 → 38**, sayılarak doğrulandı) ·
§8.4'te `mola_en_erken`/`mola_en_gec_bitis`/`mola_tek_blok` kaldırıldı,
`mola_politikasi` eklendi · §11.2 şablon örneği ve §11.3 metrikleri
güncellendi · *"Üç süre, tek toplam değil"* notu eklendi.

**Fikstürler.** Sahnedeki üç şablondan mutlak pencere kaldırıldı; A04 ve
A08'deki **19 mola bloğu** tiplendi.

⚠ **Bu kararın ilk hâli yanlıştı ve aynı gün düzeltildi.** *"Ücretli olmak"*
ile *"çalışma süresine dahil olmak"* karıştırılmıştı; `net_saat` ters yönde
değiştirilip geri alındı. Yakalayan haftalık dış inceleme oldu — kendi
ölçümüm bulamazdı, çünkü **yanlış modeli doğru ölçüyordum**. Ayrıntısı
K-32'nin "Düzeltmenin kaydı" bölümünde.

**Bitmeyen:** dinlenme molalarının çözücüye bağlanması. Eşit dağıtım
aritmetiği yazıldı ve **5 testle sınandı**, ama çağrısız duruyor — motor hâlâ
tek mola (yemek) üretiyor. Bağlanması `_sahada`'nın yeniden kurgulanmasını
gerektiriyor: *"yemek kapsamıyor **ve** hiçbir dinlenme kapsamıyor"* bir VE
bağlacı ve bugünkü boolean toplamıyla ifade edilemiyor.

**Ölçümler:** motor **98/98** · altın senaryolar **12 geçti, 4 atlandı** ·
fikstür denetleyicisi **11/11**.

---

**2026-09-25 · K-31: yarım günlük izin motora gönderilmez, elle yönetilir**

**Karar (Mustafa):** yarım günlük izin/rapor sistemde kaydedilir ama plan
üretimine girmez. Yönetici planı editörle günceller.

**Gerekçe:** yarım günlük izin plan yapılırken **bilinemez**. Ya bir gün
önceden (*"sabah hastanede işim var"*) ya da aynı gün doğar — her iki durumda
da plan çoktan yayınlanmıştır. Çözücüye verilecek bilgi değil, yayınlanmış
plana yapılacak düzeltmedir.

**Yazılanlar:** §11.2'ye *"`izinler` yalnız TAM GÜN taşır"* notu · §8.3'e ikinci
not · **K-31** · `09-motor/dogrulayici/denetle.py` içindeki bildirim metni
(*"kusur"* değil *"sınır"* diyecek şekilde).

**Kararın tek otomatik bekçisi 23 Eylül'de kurulmuş.** Arka uç yarım günlük
izni yanlışlıkla gönderirse motor bütün günü kapatır — ama sessiz kalmaz:
`okunmayan_alanlar` `izinler[].tum_gun` satırını bildirir. T-19 ile açılan
kanal burada ilk kez **bekçi** olarak kullanıldı, bulgu raporu olarak değil.

⚠ **Bırakılan sınır açıkça yazıldı:** yönetici planı düzeltmeyi unutursa
sistem yakalamaz — kişi çalışamayacağı vardiyada görünür ve hiçbir kural
itiraz etmez. Bilinçli kabul edilen risk.

**Yan sonuç:** T-38'in iki ağır satırı da (`kural_degerleri`, `tum_gun`) aynı
gün kapsam kararına bağlandı. Kalanlar yazılmamış özellik ve ad uyuşmazlığı;
**ölçüme göre T-38 artık 🟡** — seviye onayı Mustafa'da, tek taraflı
düşürülmedi.

**Motor:** 77/77 yeşil (metin değişikliği, davranış değişmedi).

---

**2026-09-25 · `SAGLIK_KISITI` kaldırıldı — K-21 geri alındı, katalog 34**

**Karar (Mustafa):** *"Günde 4 veya max 5 saat çalışabilir diye bir sağlık
raporu belki milyonda bir vaka olarak karşımıza çıkabilir. Ürüne eklememiz
gereksiz."*

Ürünün gördüğü sağlık durumu **dönemseldir** — iki günlük rapor, yarım günlük
rapor — ve o zaten bir **izin** satırıdır (`leaves.tip = rapor`, §8.3), motoru
`ONAYLI_IZIN` üzerinden bağlar ve **yazılı**. Yeni kural gerekmiyordu.

**Nasıl ortaya çıktı.** İş `SAGLIK_KISITI`'nı yazmak diye başladı. Kod yazmadan
önce üç ürün kararı soruldu; ikincisine verilen cevap kuralın kendisini
gereksiz kıldı. **Yazmadan sormak, yazdıktan sonra çıkarmaktan ucuza geldi.**

**Dokunulan yerler:** şartnamede sekiz (§1 değişiklik tablosu · §5.2 · §6 kural
sayısı · §6.1 katalog satırı ve bölümü · §6.2 · §6.6 yasal dayanak · §8.3 · §17
sürüm notları), artı `08-URUN-KARARLARI.md` (K-21 geri alındı, K-1 biçiminde),
`06-ACIK-RISKLER.md` ve `00-BURADAN-BASLA.md`. **Katalog 35 → 34**, sayılarak
doğrulandı (benzersiz kural kodu 34).

⚠ **Bırakılan sınır açıkça yazıldı:** kalıcı bir *süre* kısıtı olan çalışan
gerçekten çıkarsa sistem onu koruyamaz; plan onu normal yasal tavana kadar
planlar. §5.2'deki *"Ayşe'nin raporu var, günde en fazla 4 saat nereye
yazılacak?"* sorusunun cevabı artık **"hiçbir yere"** ve orada öyle yazıyor.

**Yan sonuçlar:** **T-43** aynı gün açıldı ve geri çekildi. **T-42** (§11.2
örneği §5.2 ile çelişiyor) yarı yarıya çözüldü — taşıyıcı biçim sorunu
kalmadı, örnek sorunu duruyor. **T-38**'in gerekçesi düzeltildi: `kural_degerleri`
değil, **`izinler[].tum_gun`** en ağır satır — yarım günlük izin motora hiç
gelmiyor, ve Mustafa'nın *"yarım gün de rapor alabilir"* cümlesi onu asıl iş
yaptı.

---

**2026-09-23 · Devir dosyası tazelendi; içinde bir haftalık yanlış sayı vardı**

`00-DEVIR/00-BURADAN-BASLA.md` güncellendi: dört kapanan 🔴, yeni dört bulgu,
77 birim test, `okunmayan_alanlar` kanalı.

Güncellerken iki yanlış sayı çıktı. Kural gövdesi **17** yazıyordu, sayılınca
**19**. Daha önemlisi: *"Altın senaryo 12, hepsi yeşil"* — `12 passed` sayısı
**7 senaryo + paketin 5 sağlık testidir**; A2/A10/A11/A12 hiç koşmadı. Bu
düzeltme **16 Eylül'de** `06-ACIK-RISKLER.md`'ye yazılmış ama giriş
dokümanına taşınmamış: hata bulunmuş, adı konmuş, belgelenmiş ve deponun ilk
okunan sayfasında **bir hafta** aynen durmuş.

**T-37 ile T-26'nın kesişme noktası.** Giriş dokümanı tazelik kontrolünün
kapsamında değil, ve bir yerde yapılan düzeltme kendiliğinden yürürlüğe
girmiyor.

---

**2026-09-23 · T-41 açıldı — DENETIM uyarılarının 13'ü kalıcı**

Commit öncesi denetim: **0 HATA, 14 UYARI**. Ölçüldü: 14'ün 13'ü
`oturumlar/` ve `DEGISIM-GUNLUGU.md` içinde, yani append-only dosyalarda —
düzeltilemez. İş düşen tek uyarı *"commit bekleyen 19 dosya"*.

`DENETIM.py` okundu: tasarım **zaten doğru**
(`bildir = uyari if tarihsel_mi(yol) else hata`). Eksik olan kural değil
etiket — düzeltilemez uyarı, iş düşenle aynı listede basılıyor. Her koşuda
akan 13 satır, uyarı bloğunu okunmaz hale getirir; **O-7**, bu kez projenin
kendi bekçisinde.

Kod değişmedi: `DENETIM.py` her şeyin bekçisi, dokunmak onay ister.

---

**2026-09-23 · Koşturma yönergeleri sekiz yerde cmd sözdizimi veriyordu**

Mustafa altın senaryoları koşturdu, 7 kırmızı geldi: *"MOTOR ADRESI TANIMLI
DEGIL"*. Sebep kodda değildi — `set AD=deger` **cmd** sözdizimi. PowerShell'de
`set`, `Set-Variable`'ın takma adıdır ve ortam değişkeni kurmaz.

Yönerge deponun **kendi** dosyalarında sekiz yerde böyle yazılıydı; ikisi
`​```powershell` etiketli blokların içinde. Yani etiket bir şey iddia ediyor,
içeriği başka şey yapıyordu.

Düzeltildi: `$env:TSHIFT_MOTOR_URL = "http://localhost:8000"`.
`00-DEVIR/00-BURADAN-BASLA.md`, `00-DEVIR/04-TEST-HARITASI.md`,
`08-motor-testleri/v5/testler/motor_istemci.py` (yardım metni **ve** hata
metni), `08-motor-testleri/v5/testler/OKU-BENI.md`, `09-motor/OKU-BENI.md`,
`09-motor/servis.py`. Ayrıca `cd 09-motor && py servis.py` → `ve`;
`&&` PowerShell 5.1'de geçerli bir ayraç değil.

**Testin kendisi doğru davrandı:** motora ulaşamayınca sessizce atlamadı,
*"adres tanımlı değil"* diye durdu (§16.4). Yanlış olan tek şey yönergeydi.

Sonuç: **12 geçti, 4 atlandı** — makinede doğrulandı.

---

**2026-09-23 · T-19 KAPANDI — şartnamedeki talep biçimi sessizce atlanıyordu**

**Karar (Mustafa): şartname kazanır; okunmayan alan bildirilir, iş
durdurulmaz.** Reddetmek, motorun tanımadığı tek bir alan yüzünden çalışan
bir planı yok ederdi.

**Kırmızı kanıt — bulgu iki satırda:**

```
assert c["metrikler"]["asgari_kapsama_yuzde"] == 100.0   -> GEÇTİ
assert len(c["atamalar"]) > 0                            -> KALDI
```

Sıfır atamalı plan, %100 kapsama, yayınlanabilir. Beş testin **beşi de**
kırmızı yandı.

**Yazılanlar:** talep hücre başına okunuyor —
`09-motor/cozucu/model.py`, `09-motor/dogrulayici/kurallar.py`,
`09-motor/dogrulayici/denetle.py`, **üçü ayrı ayrı** (§7.6; ortak yardımcı
modül `test_ortak_yardimci_modul_yok` ile yasak). Yeni kanal:
`okunmayan_alanlar` — *"gönderildi ama okunmadı"*.
Fikstür kısayolu `08-motor-testleri/v5/fikstur_yukleyici.py` içinde açılıyor.

**Kayıtta yazan ile ölçülen — üçüncü kez.** Kayıt *"2 yer okuyor, 11 fikstür
dönüşecek, 5 alan sessiz"* diyordu. Ölçülen: **5 yer**, **0 fikstür dosyası**
(kısayol yükleyicide açıldı), **12 alan** — artı `gecmis_vardiyalar` (T-28).
T-34 ve T-35'ten sonra aynı ders üçüncü kez: *bir bulgunun kaydı, bulgunun
kendisi değildir.*

⚠ **Kendi testimde birim hatası.** İlk yazımda *"4 saat × 3 kişi = 12 atama"*
diyordum. Yanlış: bir atama kişi × **vardiya**, kişi × saat değil. Motor
doğruydu, test yanlıştı. Sayı yerine **kapsama** sınanacak şekilde
değiştirildi — birimden bağımsız.

⚠ **Mekanizma ilk sürümünde iki yanlış alarm üretti.** `yetkinlikler` ve
`operasyonel_rol` *"okunmuyor"* diye bildirildi; oysa
`09-motor/cozucu/model.py` `_yetkinlik()` ikisini de okuyor. Kendi koyduğum
kurala (*"önce okuyan satırı bul"*) iki adda uymamışım. **O-7:** sessizliğe
karşı kurulan mekanizmanın ilk hatası gürültü olmak oldu.

**Yan bulgu — T-26'nın ikinci canlı örneği.**
`08-motor-testleri/v5/fikstur-denetleyici.py`, ortak olduğu **yazılı** olan
`fikstur_yukleyici.py`'yi hiç import etmiyor, kendi kopyasını taşıyormuş.
Kopya bugün ayrıştı ve A08'i tutarsız gösterdi. Silindi; ortak modül
çağrılıyor.

**Şartname değişti:** §11.3 çıktısına `okunmayan_alanlar` eklendi
(`02-spec/v1.4-master-spec.md`). Kanal kodda var, sözleşmede yoktu — bu da
T-19'un ta kendisi olurdu.

**Açılan kayıtlar:** **T-38** (şartnamenin 12 alanı daha karşılıksız —
`kural_degerleri` yok sayılıyor, 9 saatlik sözleşme 11 saate planlanabilir) ·
**T-39** (aynı hücreye iki talep satırı tanımsız) · **T-40**
(`tercih_karsilama_yuzde` §11.3'te yazılı ama motorda yok; onu gerektirdiği
söylenen A7 onsuz yeşil).

**Ölçümler:** motor **77/77** · altın senaryolar **12 geçti, 4 atlandı** ·
fikstür denetleyicisi **11/11**.

---

**2026-09-23 · T-35 KAPANDI — kurulum çapında kilitlenme**

Kayıt iki yerde küçük yazmıştı. **Etki:** *"bütün kiracıyı kilitliyor"*
deniyordu; `KilitliMi` sorgusunda kiracı filtresi yok (M-13, bilerek), yani
gerçek etki **kurulum çapında** — herhangi bir kiracıda 5 yanlış parola,
herkesi 15 dakika kilitliyordu. **Kapsam:** yalnız `04-kod/frontend/src/app/api/giris/route.ts`
anılıyordu; `grep` API'ye giden **beş** çağrı yeri buldu.

**Kural doğruydu, gördüğü IP yanlıştı.** Şartname *"aynı e-posta veya IP için
5 başarısız denemede 15 dakika kilit"* diyor ve kod bunu doğru uygulamış.
Tarayıcı API'ye doğrudan gitmediği için `RemoteIpAddress` her zaman ön yüzün
adresiydi.

⚠ **"Mekanik" etiketi yanlıştı.** `X-Forwarded-For` istemcinin yazdığı bir
başlık; körlemesine güvenmek saldırganın kendini istediği IP gibi
göstermesine izin verir. Güvenilen vekil listesi şart, o da barındırmaya
bağlı — yani içinde bir ürün kararı vardı ve soruldu.

**Yazılanlar:** API tarafında `UseForwardedHeaders` +
`TSHIFT_GUVENILEN_VEKILLER` (liste boşsa başlık **hiç** okunmaz — güvenli
varsayılan); ön yüzde `istemciBasliklari()` ve beş çağrı yerinin hepsi;
compose ve `.env.example`.

**Ölçümler:** kırmızı kanıt `IP1` (`Expected: "203.0.113.9", Actual: null`) →
düzeltme → **45/45 yeşil**. Uçtan uca elle: Next'e `198.51.100.7` verildi,
`login_attempts.ip` **aynısını** yazdı.

⚠ **Sonra sahte başlık denendi ve GEÇTİ — ilk yapılandırma yanlıştı.**
Güvenilen aralık `172.16.0.0/12` konmuş, yanına *"host'tan gelen istek bu
aralığa girmez"* diye yazılmıştı. Ölçüldü: host'tan gelen istek API'ye
**docker ağ geçidinden** (`::ffff:172.18.0.1`) ulaşıyor ve o adres aralığın
**içinde**. Yani aralık host'taki her şeyi güvenilir sayıyordu.

**Düzeltildi:** compose'a sabit alt ağ (`172.28.9.0/24`), web kutusuna sabit
adres, güvenilen liste **tek adres**. İkinci tur: Next'ten `198.51.100.8`
geçti ✅, host'tan `203.0.113.55` **yok sayıldı** ✅.

`IP2` testi bunu yakalayamazdı — kod doğru, test doğru, yanlış olan
**yapılandırma**. Otopsisi **O-11**: *birim testi mantığı doğrular,
topolojiyi doğrulayamaz.*

⚠ **Ön yüzün otomatik testi yok** — `IP1`–`IP3` API'ye doğrudan gidiyor.
Elle doğrulandı, gerileme bekçisi yok; Next test altyapısı bilerek ertelendi.

→ `04-kod/backend/src/TShift.Api/Program.cs` ·
`04-kod/frontend/src/lib/api.ts` ·
`04-kod/backend/tests/TShift.Tests/IstemciIpTestleri.cs`

**2026-09-23 · T-34 KAPANDI — sırlar depodan çıktı**

Ortam değişkeni verilmediğinde uygulama hata vermiyor, **bilinen bir
anahtarla** açılıyordu. `Program.cs`'in kendi yorumu *"Parola koda ve
appsettings'e YAZILMAZ"* diyordu; bir satır altında koda yazılmıştı.

**Kayıttaki tarif eksikti.** `grep` ile tarandı: aynı sabit **beş katmanda 16
yerde**. Uygulama kodu (4), test kodu (7 dosya), `docker-compose.yml` (4) ve
**`04-kod/db/rls/02-uygulama-rolu.sql`** — veritabanı rolü o parolayla
*yaratılıyordu*. Yalnız C# tarafını düzeltmek tiyatro olurdu.

**`Sirlar.Zorunlu()` yazıldı:** varsayılan yok, sır yoksa uygulama açılmaz,
hata **değişkenin adını** söyler, değerini asla yazmaz. SQL betiği yer
tutucuya geçti (`{APP_DB_PASSWORD}`) ve `ALTER ROLE ... PASSWORD` eklendi —
rol zaten varsa yaratma bloğu atlanıyor, eski parolayla kalıyordu. CI her
koşuda `openssl rand` ile üretiyor: depoda sır yok, GitHub secret'ı gerekmiyor.

**`.env.example`'da `JWT_SECRET` hiç yoktu** — örneği takip eden biri imza
anahtarsız kalır ve koddaki sabiti kullanırdı. Eklendi. `TEST.ps1` artık
`.env`'i okuyor.

**Kırmızı kanıt CI dalında, kalıcı.** `48583e4` yalnız testi taşıyordu:
*42 test, 40 geçti, S1 ve S2 kırmızı — "No exception was thrown"*.
`3ec5d42` düzeltmeyi getirdi: **42/42 yeşil.**

⚠ **`M5 - appsettings icinde gercek parola yok` bu ailenin tek üyesini
koruyordu ve yeşil yanıyordu.** Parola `appsettings`'te değildi, başka beş
yerdeydi. Kapı vardı; başka bir kapıydı — O-1 ve O-9 ile aynı sınıf.

**Yan düzeltme:** `04-TEST-HARITASI.md` başlığında hâlâ *"on ikisi de yeşil"*
yazıyordu — 16 Eylül'de beş dosyada düzeltilen yanlış iddia, burası
atlanmıştı. T-37'nin aynı sınıfı.

→ `04-kod/backend/src/TShift.Infrastructure/Sirlar.cs` ·
`04-kod/db/rls/02-uygulama-rolu.sql` · `.github/workflows/testler.yml`

**2026-09-23 · T-22 KAPANDI — çözümsüzlükteki taslak artık denetleniyor**

`orkestra.py` çözücü *"cozumsuz"* dediğinde erken dönüyor, bağımsız
doğrulayıcıyı hiç çağırmıyordu. **En çok açıklama gereken plan, en az
denetlenen plandı** — yönetici K-10 uyarınca bu taslağı gerekçeyle onaylıyor
ve neyi onayladığını göremiyordu.

Üç şart yazıldı: taslak `degerlendir()`'den geçer · denetim **özgün** girdiyle
yapılır · sıfır atamalı plan `var: False` der.

**İkincisi sessiz tuzaktı.** `en_iyi_plan` üretilirken `ASGARI_KAPSAMA`
bilerek gevşetilir; denetim gevşetilmiş girdiyle yapılsaydı doğrulayıcı o
kuralı hiç görmez, taslak tertemiz görünürdü — denetim eklenmiş ama işe
yaramaz olurdu. Bekçisi ayrı bir test.

**Kırmızı kanıt:** 3 kırmızı / 1 yeşil (yeşil olan gerileme koruması:
düzeltme *"hep False de"* diye yapılamaz) → 4/4. **72 birim testi** ·
7 altın senaryo · fikstür denetleyicisi 0.

⚠ **Düzeltme A03'te T-18'i görünür kıldı.** Artık gelen denetim raporu şunu
diyor: `uygulanmayan_kurallar: ['YETKINLIK_KAPSAMASI']`, `sert_ihlal: 0`,
`yayinlanabilir: true`. O kural A03'ün girdisinde **aktif ve SERT**, gövdesi
doğrulayıcıda yok — ve A03'ün tamamı zaten o kural sağlanamadığı için
çözümsüz. Aynı cevapta *"kontrol edemedim"* ve *"yayınlanabilir"*.
**T-18 artık onaylanmış bir altın senaryoda görünüyor.** Hata üretilmedi,
görünmez olmaktan çıktı.

→ `09-motor/orkestra.py` · `09-motor/cozucu/teshis.py` ·
`09-motor/testler/test_profiller.py`

**2026-09-23 · İNCELEME DÖNGÜSÜ KURULDU — tadımcı kararı kapandı**

15 Eylül'de ertelenen salt-okunur inceleyici kararı kapandı. **Tetikleyici
16 Eylül'de ateşlenmişti ve kimse fark etmemişti** — T-26'nın üçüncü örneği,
ilk kez bir ürün kararında değil **sürecin kendisinde**.

**Ölçüm şartı fazlasıyla karşılandı.** Şart *"on incelemede bulgu yoksa
bırak"* idi; 16 Eylül'de üç incelemede **19 bulgu**, yanlış alarm sıfır.

**Ama tasarım değişti ve gerekçesi ölçüldü.** Kurgu *"dal farkını incele"*
idi. `git log` ile bakıldı: `09-motor/` klasörünün tamamı 16 Eylül'de doğmuş,
yani o günün dal farkı motorun kendisiymiş — tasarım **tesadüfen** çalışırdı.
Bir daha çalışmaz: T-19 (kod eski, yanlış olan gelenek), T-28 (bir **yokluk**),
T-29 (ölü kod yolu) ve T-34/T-35 (motor dalının dışında) hiçbir diff'te
görünmez.

**Kalıcı araç reddedildi.** Değeri üreten şey ikinci ajan değil **soğukluk**:
hatırlamayan bakar. Depoda bağlam biriktiren inceleyici onu kaybeder.

**Kurulan:** haftalık elle tarama, iki geçiş (haftanın farkı · şartname-kod
taraması), farklı sağlayıcının modeliyle. Yöntem `05-inceleme/beceriler/`
altında dört dosyada — `00-DEVIR/` dışında, çünkü **R7 eşikte** (9 dosya).
Yeni ölçüm şartı: üç haftada bulgu yoksa **sıklık düşer**, bırakılmaz.

⚠ **Kapatılamayan boşluk:** mimar ulaşılamıyor. Geri alma bedeli 🔴 olan beş
karar (M-01, M-06, M-09, M-10, M-11) için ikinci teknik insan görüşü yok. Dış
tarama kodun şartnameye uygunluğuna bakar, **kararın doğruluğuna** değil.

**T-37 açıldı.** `README.md` aylardır bayat: *"kod başlamadı"*, *"master spec
yazılıyor"*, elenen Keycloak, eksik altı klasör. `DENETIM.py` yakalayamaz —
6. kontrolü yalnız oturum günlüğü ile değişim günlüğü arasına bakıyor, giriş
dokümanı **hiçbir kontrolün kapsamında değil**. Olgular düzeltildi, kontrol
eklenmedi.

→ `05-inceleme/beceriler/` · `00-DEVIR/06-ACIK-RISKLER.md` · `README.md`

**2026-09-16 · T-27 KAPANDI — olmayan mola artık yasal sınırı devirmiyor**

Dış incelemenin **1 numaralı** bulgusu. `mola_araliklari()` molayı, vardiyanın
içinde olup olmadığına bakmadan döndürüyordu.

```
vardiya 08:00-20:00, mola 22:00-23:00
ESKI : net 11 saat, GUNLUK_AZAMI (11) ihlali 0
YENI : net 12 saat, GUNLUK_AZAMI ihlali 1
```

Devrilen kural `yasal: true, kabul_edilebilir: false` sınıfında. Hata yönü
tek taraflıydı ve **yanlış tarafa**: bozuk girdi motoru daha gevşek yapıyordu.

**Üç işlem eklendi, sırası önemli.** *Kaydırma* — gece yarısını aşan
vardiyada mola ham saatle yazılmış olabilir (`00:30`), 24 saat ileri alınır.
*Kırpma* — kalan aralık vardiyayla kesiştirilir. *Birleştirme* — üst üste
binen molalar tek aralığa iner.

⚠ **Birleştirme ilk turda atlandı.** Kırpma yazıldı, sekiz testin altısı
yeşil yandı, "kapandı" denecekti. Kabul cümlesi tekrar okununca üçüncü
şartın yazılmadığı görüldü: `10:00–12:00` + `11:00–13:00` = **dört saat**
sayılıyordu, üç değil. **T-26'nın tam örneği** — kayıt ile yürürlük ayrı
şeyler; bu kez kaydın kendisi yakaladı.

**Kapsam.** Çözücü molayı zaten vardiya içine zorluyordu (`model.py`), yani
hata **üretilen planlarda** çıkmıyordu. Riski taşıyan yol içe aktarılan
gerçek veri ve **plan editörü** — yani henüz yazılmamış olan yol.

**Kırmızı kanıt:** düzeltmeden önce 6 kırmızı / 2 yeşil (ikisi gerileme
koruması: gece yarısı molası ve ayrık molalar). Sonrasında 8/8.
**68 birim testi** · **7 altın senaryo** · fikstür denetleyicisi 0.

→ `09-motor/dogrulayici/zaman.py` · `09-motor/testler/test_kurallar.py`

**2026-09-16 · DIŞ İNCELEME, 3. tur — on bulgu daha, beşi 🔴**

Üçüncü tur şartnameyi kural kural kodla karşılaştırdı. **On bulgunun onu da**
ölçülerek doğrulandı; hiçbiri tahmin değil, her biri koşturularak görüldü.

**T-27 🔴 — olmayan mola yasal sınırı deviriyor.** `zaman.mola_saat()` mola
süresini vardiyanın **içinde olup olmadığına bakmadan** topluyor. Ölçüm:
`vardiya 08:00–20:00, mola 22:00–23:00 → brüt 12, mola 1, net 11,
GUNLUK_AZAMI (11 saat) ihlali: 0`. Devrilen kural `yasal: true,
kabul_edilebilir: false` sınıfında — K-20'ye göre asla göz yumulamaz olan.

**T-28 🔴 — geçmiş vardiyalar hiç okunmuyor.** `gecmis_vardiyalar` ifadesi
`09-motor/` içinde **hiçbir dosyada geçmiyor**. Haftalar arası dinlenme
kuralı önceki haftaya kör: pazar gecesini çalışmış biri pazartesi sabahına
yazılabilir.

**T-29 🔴 — `DONMUS_GUN` hiç ateşlenemez.** Kural yalnız `_yeni` işaretli
atamalarda çalışıyor, o işareti **hiçbir yer üretmiyor**. Ölçüm: işaretsiz
girdide 0 ihlal, elle işaretlenince 1. *"Geçmiş yeniden planlanamaz"*
sözünün tek bekçisi bu.

**T-34 🔴 — sırlar kodda varsayılana düşüyor.** `Program.cs`:
`APP_DB_PASSWORD ?? "tshift_app_dev_2026"` ve
`JWT_SECRET ?? "yerel-gelistirme-imza-anahtari-..."`. Ortam değişkeni
unutulursa uygulama **hata vermiyor**, bilinen anahtarla açılıyor.

**T-35 🔴 — bir kullanıcının hatalı girişi bütün kiracıyı kilitliyor.**
`04-kod/frontend/src/app/api/giris/route.ts` `X-Forwarded-For` iletmiyor, backend
`ctx.Connection.RemoteIpAddress` okuyor, `ForwardedHeaders` ara katmanı
hiçbir yerde yok. Sonuç: bütün istekler tek IP'den geliyor gibi görünüyor —
beş yanlış parola **herkesi** kilitliyor, denetim kaydındaki her IP kurgusal.

**Dört 🟡 daha.** T-30 `HAFTA_TATILI` kesintisiz 24 saati ölçmüyor (kodun
kendi yorumu bunu söylüyor) · T-31 adalet penceresi takvim ayında
sıfırlanmıyor · T-33 `_dilimler(0, 8.5, 12.5) -> [8, 9, 10, 11]`, yarım
saatler kayboluyor · T-36 `YenileAsync` oku-kontrol-işaretle-kaydet yapıyor,
`RowVersion` / işlem / seviye yok.

**T-32 🟡 — bunu bugün ben açtım.** K-30'u yazarken fazla mesai tavanını
çözücüde **profil tablosundan**, doğrulayıcıda **kural parametresinden**
okur hâle getirdim. Bugün aynı sayıyı veriyorlar; kiracı parametreyi
değiştirdiği gün sessizce ayrışırlar. §7.6'nın bağımsızlığı kural mantığını
ayırıyor, **ortak gerçeğin tek kaynağını** garanti etmiyor.

**Öncelik tablosu yeniden sıralandı** — ölçüt *yanlış karar riski*:
T-27 · T-35 · T-34 · T-28 · T-29 · T-19 · T-21 · T-18 · T-22.

**Düzeltme yine yapılmadı, bilerek.** Beş bulgu ürün kararı içeriyor.
Kaydedildi, uydurulmadı.

→ `00-DEVIR/06-ACIK-RISKLER.md` T-27 … T-36

**2026-09-16 · DIŞ İNCELEME, 1. ve 2. tur — dokuz bulgu, iki yanlış iddia**

Motor bittikten sonra proje **başka bir modele** (GPT) şartnameyle birlikte
incelettirildi. **Dokuz bulgunun tamamı** bizim tarafımızda doğrulandı.
*(Üçüncü tur ayrı girdide, yukarıda.)*

**T-18 🔴 — yayın kapısı.** Gövdesi yazılmamış ama aktif ve SERT bir kural
varken doğrulayıcı aynı cevapta *"bu kuralı kontrol edemedim"* ve
*"yayınlanabilir"* diyor. `denetle.py` içinde kendi yazdığımız cümle
*"'ihlal bulamadım' ile 'bakmadım' aynı şey değildir"* — ilkeyi yazmışız,
kapıya bağlamamışız. O-1'in tam şekli.

**T-19 🔴 — talep biçimi.** Şartname §11.2 `{ekip, gun, saat}` diyor, motor
`{gunler:[], saatler:[]}` okuyor. Şartname biçimi verildiğinde **sıfır
atamalı plan** üretiliyor ve %100 kapsama ile yayına açılıyor.

> **Bağımsızlık tek başına yetmiyor.** §7.6 çözücü ile doğrulayıcıyı kural
> mantığında ayırıyor, ama ikisi de girdiyi aynı fikstür geleneğiyle okuyor.
> Birbirleriyle tutarlılar, ikisi de şartnameyle tutarsız. D-6'ya karşı
> kurulan savunma, ortak yanlış bir **girdi yorumuna** karşı boş.

**Yanlış iddia düzeltildi.** *"On iki altın senaryonun tamamı yeşil"*
cümlesi **yanlıştı**. `12 passed` = 7 altın senaryo + paketin kendi 5 sağlık
testi. A2, A10, A11, A12 backend tarafında ve **hiç sınanmadı** — çift
tıklama, geçmiş veri ve plan kopyalama tamamlanmış güvence değil. Cümle
dokümanlara ve commit mesajlarına girmişti; hepsi düzeltildi.

**Yanlış sayı düzeltildi.** Doğrulayıcıda **19** kural var, doküman 17
diyordu — üstelik aynı dosyanın tablosu 19 satır listeliyordu. `DENETIM.py`
yakalayamaz: tutarlılığa bakar, doğruluğa değil.

**İkinci turda beş bulgu daha.** **T-21** 🔴 çok ekipli çalışan iki ekibin
ihtiyacına birden sayılıyor — modelin `x` değişkeninde ekip boyutu yok; tek
kişiyle yapılan deneyde motor *"çözüldü"* derken asgari kapsama %50 çıktı.
**T-22** 🔴 çözümsüzlükte sunulan `en_iyi_plan` bağımsız denetimden geçmeden
dönüyor, üstelik sıfır atamalı plan `var: True` diyor. **T-23** zaman aşımı
ile gerçek çözümsüzlük aynı cevabı alıyor. **T-24** K-28'in *"2 dakika
durgunluk"* koşulu **hiç yazılmamış**, ayrıca süre bütçesi isteğin tamamını
kapsamıyor — 0,05 saniyelik bütçeyle yapılan çağrı **57,4 saniye** sürdü.
**T-25** servis tek iş parçacıklı.

**T-26 açıldı: kayıt ile yürürlük arasında kontrol yok.** K-28 kayda geçti,
şartnameye işlendi, kodun başında anlatıldı, "kapandı" sayıldı — ve ikinci
koşulu hiç yazılmadı. Ne kırmızı kanıt, ne `DENETIM.py`, ne CI yakaladı;
hiçbiri *"her K-kararının onu çiviyen bir testi var mı"* diye sormuyor.
O-1'in genel hali: O-1'de RLS tanımlıydı ama etkisizdi, burada karar kayıtlı
ama yürürlükte değil.

**Yöntem kayda geçti:** iç kırmızı kanıt *"varsayımlarımız korunuyor mu"*
sorar; dış inceleme *"varsayımlarımız doğru mu"* sorar. İkincisi olmadan
birincisi kendi dünyasında kusursuz kalır. Bir iş parçası bittiğinde,
şartnameden türetilmiş girdilerle **başka bir modelle** inceleme yapılır.

Düzeltme yapılmadı — T-18 ve T-19'un ikisi de ürün kararı içeriyor.

→ `00-DEVIR/06-ACIK-RISKLER.md` T-18 … T-26

**2026-09-16 · T-17 kapandı · Actions eylemleri Node 24'e çıkarıldı**

CI kapısının ilk koşusunda iki uyarı çıkmıştı: eylemler Node 20 hedefliyordu,
GitHub onları Node 24'te zorla koşturuyordu. Kapı çalışıyordu ama zorlama
kalkınca çalışmayacaktı — kendi kendine kırmızıya dönecek bir madde.

checkout v4→**v7**, setup-python v5→**v7**, setup-dotnet v4→**v6**. En güncel
ana sürümlere çıkıldı ki aynı iş birkaç ay sonra tekrarlanmasın. `checkout`
v7'nin kırıcı değişikliği fork PR'larıyla ilgili (`pull_request_target` /
`workflow_run`); bu depoda o tetikleyiciler yok.

**Önce dalda denendi.** Workflow zaten `branches: ["**"]` ile her dalda
koştuğu için `ci/node24` dalına push edildi, orada yeşil yandığı görüldü,
sonra `main`'e alındı. Gerekçe bir değişmez: *"`main` her zaman yeşildir"* —
bir CI değişikliği için bedava riske atılmaz.

→ `.github/workflows/testler.yml`

**2026-09-16 · Güncelleme ritüelinin tetikleyicisi değişti**

Devir dosyalarının **ne zaman** güncelleneceği tek cümleye bağlıydı:
*"Mustafa 'güncelle' dediğinde."* Yani birinin hatırlamasına bağlıydı —
hatırlamaya bağlı bir bekçi bekçi değildir (O-1). Üç somut ana bağlandı:
aynı commit'te (karar/kural/kapanan madde), iş parçası bitince (oturum
günlüğü), oturum kapanırken (neredeyiz + sıradaki adım + DENETIM).

En önemlisi ilki: oturum her an bitebilir, doküman koddan geriden geliyorsa
bir sonraki pencere yanlış haritayla başlar.

`DENETIM.py`'ye *"kod değişti ama devir dosyası değişmedi"* kontrolü
**eklenmedi** — küçük düzeltmelerde sürekli öterdi, O-7'nin dersi tam bu.
Bilinçli bir boşluk olarak kayda geçti.

→ `00-DEVIR/00-BURADAN-BASLA.md` §5

**2026-09-16 · MOTOR CI KAPISINA BAĞLANDI — ilk koşu YEŞİL**

`.github/workflows/testler.yml` içine **`motor`** adlı ikinci bir iş eklendi:
60 birim testi + 12 altın senaryo + fikstür denetleyicisi. Docker
gerektirmiyor. Python **3.14**'e sabitlendi — Mustafa'nın makinesindeki
sürümün aynısı; gerekçe workflow'da docker için zaten yazılıydı: *"CI ile
yerel arasında fark olmasın"*.

**Neden ayrı iş, aynı işe ek adım değil:** aynı işte olsalardı .NET tarafının
kırmızısı motorun sonucunu **gizlerdi** — bir adım patlayınca sonrakiler hiç
koşmaz.

**Kapının kendi kırmızı kanıtı yapıldı.** Bir kapının en tehlikeli hâli,
koruduğu şey yokken de yeşil yanmasıdır. Ölçüldü: `TSHIFT_MOTOR_URL`
verilmezse `exit=1`, servis kapalıysa `exit=1`, sağlık beklemesi 20 sn'de
cevap alamazsa adım `::error::` ile duruyor.

`09-motor/requirements.txt` eklendi, sürümler sabitlendi (O-8 gerekçesi).
Doğrulayıcının dış bağımlılığı yok ve bu bilerek korunuyor.

**İlk koşu yeşil** (`47c7050`). Uyarı yazısı yazıldığı gün konulmuş, ancak
yeşil koşu görüldükten sonra kaldırılmıştı — 12 Eylül'de tersi yaşandığı için
(dokümanda *"bekçi eklendi"* yazıyordu, bekçi yoktu; O-1).

Tek çıktı iki uyarı, ikisi de bugünden değil: eylemler (`actions/checkout@v4`,
`actions/setup-python@v5`, `actions/setup-dotnet@v4`) Node 20 hedefliyor,
GitHub Node 24'e zorluyor. Kapıyı kırmıyor ama zamanla kıracak — **T-17**.

→ `.github/workflows/testler.yml` · `09-motor/requirements.txt`

**2026-09-16 · ÇÖZÜCÜ YAZILDI · ON İKİ ALTIN SENARYONUN TAMAMI YEŞİL**
**.NET ürün kodu değişmedi, 39/39 hâlâ yeşil.**

**Motor tamamlandı.** `09-motor/cozucu/` (CP-SAT) ve `09-motor/orkestra.py`
(§11.7 onarım döngüsü) yazıldı. Kalan beş kırmızı senaryo — A1, A3, A6, A7,
A9 — yeşile döndü. Birim testi 44 → **60**, altın senaryo **12/12**.

**Üç senaryo kolay yeşile dönmedi ve üçü de gerçek bir boşluk buldu:**

- **A9** — `shift_templates`'te *"bu şablon hangi günlerde kullanılır"* alanı
  **yoktu**. "Cumartesi nöbeti" adlı 4 saatlik şablonu motor hafta içi de
  kullanıyor, kapasiteyi 42 yerine 49 gösteriyordu. Tahminle değil **deneyle**
  bulundu: şablon çıkarılınca kapasite tam olarak fikstürün belgelediği 42'ye
  düştü. **Ders:** bir alanın *adı* motoru bağlamaz; bağlayan tek şey kısıttır.
  → `gunler` alanı eklendi (T-14 kapandı)
- **A1** — `/solve` §11.7 onarım döngüsünü hiç koşmuyordu. `orkestra.py`
  yazıldı: üret → **bağımsız** doğrulayıcıyla denetle → en fazla 2 onarım.
  Denetim her zaman **kullanıcının** girdisiyle yapılıyor, onarımın eklediği
  kilitlerle değil — yoksa motor kendi koltuk değneğini kural sanardı.
- **A7** — üç ayrı boşluk birden. (1) Motor `profil` alanını **hiç
  okumuyordu**; §5.4 ağırlık tablosu kodda yoktu. (2) `ADALET_DENGESI`'nin
  eşik altında gradyanı yoktu, yani ağırlığı değiştirmek planı
  değiştiremiyordu — iki profil **birebir aynı planı** üretiyordu. (3)
  **Fikstürün kendisi de eksikti:** kabul ölçütü *"Ç01–Ç03 en müsait
  olanlar"* diyordu ama fikstürde on çalışan birbirinin aynısıydı, yani
  cumartesiyi kime verdiğin kapsamaya **hiçbir şey mal olmuyordu**.

> **A7'nin dersi.** Onaylı bir cümle fikstüre çevrilmemişse, senaryo
> anlattığı şeyi sınamaz. Cümle onaylıydı, fikstür ona uymuyordu — ve bu
> ancak motor yazılınca görüldü.

**K-29 doğdu: eşik ihlali sayar, planı gradyan seçer.** Adalet eşiği
(K-27) yalnız doğrulayıcıda; motorda yerine **artan marjinal maliyet** var.
İki yanlış biçim denendi ve **ölçümle** elendi: *"ortalamanın üstündeki
sapma"* denendiğinde motor cumartesiye gerekenden fazla kişi koymaya başladı
(3 yerine 5) — ortalamayı yükseltmek herkesin sapmasını düşürüyordu, yani
ceza cezalandırdığı şeyi ödüllendiriyordu. Aynı açık eşik teriminde de vardı;
çıkarıldı ve o anki 57 birim + 12 altın testin **hiçbiri değişmedi** — terim zaten
atıl duruyordu.

**Kırmızı kanıt ilk turda 8'de 4'ünü KAÇIRDI.** Ağırlık tablosu yok sayılsa,
adalet gradyanı kaldırılsa, orkestra doğrulayıcıyı çağırmasa ya da fazla mesai
tavanı sabitlense **hiçbir test kırmızı yanmıyordu**. Üçüncüsü özellikle
öğretici: import'a bakan test yakalamıyor, çünkü import durur, **çağrı**
kaybolur. Eksik testler yazıldı (`09-motor/testler/test_profiller.py`, 13
test); ikinci turda **12/12 yakalandı**.

**Ölçüm yöntemi de bir tuzak çıkardı.** *"Motor şu kişiyi seçti"* testleri
kırılgan: kısıt gevşekse çözücü eşit değerdeki seçenekler arasında arama
sırasına göre seçiyor ve **bozulmuş kod aynı cevabı verebiliyor**. Bu
varsayılmadı, denendi ve doğrulandı. Çözüm: `amac_degeri` çıktıya eklendi;
aynı girdi, iki seçim sabitlenmiş hâlde çözülüp amaç değerleri
karşılaştırılıyor.

**K-29 ve K-30 karara bağlandı.** K-29 onaylandı: adalet eşiğin altında da
bir **tercihtir**; üç plan kartını birbirinden farklı yapan mekanizma bu.

K-30'da soruyu kötü sormuşum — *"bir saat fazla mesai kaç saatlik açığa
değer"* diye, yani ceza katsayısı dilinde. Mustafa haklı olarak *"ben tam
neyi cevaplayayım onu da anlamadım"* dedi ve kararı ürün dilinde verdi:
**"Zaten hedef hiç gitmemek. Gidilecekse de minimum gitmek."** Ölçüldü — kod
bunu **zaten yapıyormuş**: hedef kapsama için 0 saat, asgari kapsama zorlarsa
tam gereken kadar. Sayı değişmedi, üç test kararı çiviledi.

**Riski açarken yazdığım teşhis yanlıştı ve düzeltildi.** *"Profil tavanı
pratikte hiç kullanılmıyor"* demiştim; tavan **ölü değil** — zorunlu aşımın
sınırını o çiziyor (CALISAN'da tavan 0 → plan çözümsüz). Ölçüm doğruydu,
yorumu yanlıştı: ölçtüğüm sayıyı ürün kararının yerine koymuşum. T-15 kapandı.

**O-9 · Gönderilmeyen dosya iki tarafta da "temiz" görünüyordu.** Mustafa'nın
makinesinde ilk koşuda A06 kırmızı yandı ve birim testi 53 çıktı (57 değil):
doğrulayıcıdaki `KILIT_UYUMU` düzeltmesi ve 4 testi **hiç gönderilmemişti.**
Hiçbir yerde kırmızı yanmıyordu — git temiz, `DENETIM.py` *"commit bekleyen
0"*, testler yeşil; çünkü her iki taraf **kendi içinde** tutarlıydı ve
tutarsızlık **aralarındaydı**.

Yakalayan şey `orkestra.py` oldu: `/solve` ilk kez doğrulayıcıyı çağırınca
eski `KILIT_UYUMU`, A06'nın `tip: "yasak"` kilidinde patladı. Onarım
döngüsünün yazıldığı ilk gün amacı dışında bir şeyi de yakaladı.

Kalıcı bekçi: **commit öncesi dosyalar karşı taraftan çekilip içerikçe
karşılaştırılır** — hafızaya değil `cmp`'ye güvenilir. D-1 zincirine yeni
halka: *yazdım ≠ gönderdim ≠ commit ettim ≠ karşı tarafta değişti ≠
göndermem gerektiğini fark ettim.*

→ `09-motor/` · `02-spec/v1.4-master-spec.md` §5.4, §6.5, §6.7, §8.4, §11.3
→ `00-DEVIR/08-URUN-KARARLARI.md` K-28, K-29, K-30
→ `00-DEVIR/05-HATA-OTOPSILERI.md` O-9
→ `00-DEVIR/oturumlar/2026-09-16-cozucu.md`

**2026-09-16 · ADALET KURALI YAZILDI (K-27) · kırmızı kanıt ÜÇ ZAYIF TEST buldu**
**.NET ürün kodu değişmedi, 39/39 hâlâ yeşil. A4 ve A8 yeşil kalmaya devam.**

**T-12 ve A-17 kapandı.** Mustafa eşiği verdi: *"ortalamadan 2 gece fazla
çalışıyorsa bu adaletsizliktir; 1 gün fazla olabilir."* Kural yazıldı — ölçü
ortalamadan sapma, eşik 2, karşılaştırma `>=`, tek yönlü, devir yükü dâhil.

**K-11 ile ters yönde ve bu tuzak kayda değer:** *"asgari 11 saat"* 11'i
kapsar (ihlal değil), *"eşik 2"* 2'yi kapsar (ihlaldir). Biri bir **taban**,
diğeri bir **sapma tavanı**. K-11 alışkanlığıyla okunsaydı kural tam sınırda
sessizce kaçırırdı.

**Asıl olay: kırmızı kanıt bu sefer BENİ yakaladı.** Yeni kuralı altı şekilde
kasten bozdum, **üçü kaçtı** — ve kabahat doğrulayıcıda değil testlerimdeydi:

- Varsayılan eşik 2→3 **kaçtı**: bütün testler eşiği açıkça geçiriyordu,
  varsayılan hiç koşmuyordu
- `>=` → `>` **kaçtı**: hiçbir vaka tam sınıra oturmuyordu (sapma hep 2,25)
- Tek yönlü → `abs()` **kaçtı**: kimse ortalamanın 2 altında değildi

Üç test yeniden yazıldı, sonra dördüncü bir boşluk çıktı: gece penceresi
20→22'ye kaydırılınca hiçbir test kırılmadı, çünkü bütün gece vakalarım
20:00–01:00 kullanıyordu. Sınırı çiviyen iki test daha eklendi.

**Son durum: 8 kasten bozma, 8'i de yakalandı. 36 test yeşil.**

**T-13 açıldı:** `saat` boyutu yazılmadı — K-27 eşiği **sayı** olarak verdi,
`saat` süredir ve `SAAT_DENGESI` ile örtüşüyor olabilir. Sessizce atlanmıyor:
kuralın kendisi yazılı olduğu için `uygulanmayan_kurallar` göremezdi, ayrı bir
`eksik_boyutlar` alanı eklendi ve bir test onu koruyor.

*Öğrenilen: bir eşiği sınayan test, o eşiği açıkça geçiriyorsa varsayılanı hiç
sınamaz. Bir sınır değerini sınayan test, vakası tam sınırda değilse `>` ile
`>=` farkını göremez. İkisi de yeşil yanar ve hiçbir şey korumaz.*
→ `09-motor/dogrulayici/kurallar.py`, `02-spec/v1.4-master-spec.md` §6.5,
`00-DEVIR/08-URUN-KARARLARI.md` K-27

**2026-09-16 · BAĞIMSIZ DOĞRULAYICI YAZILDI · A4 ve A8 YEŞİL**
**.NET ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.**
Fikstürlerin tek satırı değişmedi.

**Projede motorun İLK KORUNAN DAVRANIŞI.** `09-motor/` — `/evaluate` ucu,
17 kural gövdesi, 26 birim testi. Kabul ölçütü bu iki senaryoda taahhüt
olmaktan çıkıp **bekçiye** dönüştü.

```
py -m pytest -q   ->  5 failed, 7 passed, 4 skipped   (onceki: 7/4/5)
```

**Neden önce doğrulayıcı:** yedi kırmızının ikisi plan üretmiyor, var olan
planı denetliyor — çözücü olmadan yeşile dönebilecek tek iki senaryo onlardı.
Kalan beş kırmızı **doğru sebeple** kırmızı: servis ayakta, `/solve` 501
dönüyor, istemci bunu *"COZUCU YAZILMADI"* diye ayırt ediyor.

**Dışarıdan hiçbir paket yok.** Python standart kütüphanesi. Kurulum adımı
olmayan bir servis, "bende çalışmadı" ile geçen saatleri de ortadan kaldırır.

**Kırmızı kanıt: 7 kasten bozma, 7'si de yakalandı.** Her biri sessizce
bozulabilecek bir ürün kararı — `GUNLUK_AZAMI` 11→9 (K-18), mola hakkı brüt
yerine net (K-4), tam 11 saat ihlal sayılır (K-11), örtüşmede çift ihlal
(V-1), yayın kapısı `yasal`a bakar (K-24), gövdesi olmayan kural sessizce
geçilir, `ASGARI_KAPSAMA` molayı düşer.

**`ADALET_DENGESI` bilerek yazılmadı.** Şartname kuralı tanımlıyor ama ihlal
eşiğini tanımlamıyor. Eşiği koda gömmek, ürün kararını kodun içine gizlemek
olurdu. Uygulanmayanlar listesinde görünüyor ve bir test birinin ileride
sessizce eşik uydurmasını engelliyor. **T-12 / A-17.**

**Testler iki kendi hatamı yakaladı:** (1) "motor çöktü" ile "çözücü yok"
aynı mesajı veriyordu — ayrıldı; (2) istemcide `adres=""` ile `adres=None`
aynı sayılıyordu, bu yüzden *adressiz davranış hiç sınanamıyordu*.

**"Motor gelince tek dosya değişecek" sözü tutuldu** — yalnız
`motor_istemci.py` değişti.

⛔ **Çözücü için tek zorunlu kural:** doğrulayıcıyla mantık paylaşmayacak
(§7.6, §16.1). *"Aynı hesabı iki kez yazmayalım"* deyip ortak modül çıkarmak
yasak — tekrar burada maliyet değil, güvence.

*Öğrenilen: "boş değer" ile "belirtilmemiş" aynı şey değil. `x or y` kalıbı
bu ikisini sessizce birleştirir ve bir testi yanlışlıkla başka bir yolu
denemeye gönderir.*
→ `09-motor/`, `00-DEVIR/oturumlar/2026-09-16-bagimsiz-dogrulayici.md`

**2026-09-16 · ŞARTNAME v1.4 YAZILDI · A-15 kapandı · dokuz yeni karar**
**Ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.** v1.3'e
dokunulmadı — v1.4 tam dosya olarak yanına yazıldı.

**Ana değişiklik:** kural kataloğu **`yasal` ve `kabul_edilebilir` sütunlarını**
kazandı, 35 kuralın tamamı sınıflandırıldı. Bu olmadan iki onaylı karar
(K-10 kabul edilmiş ihlal, K-16 yayın kapısı) **uygulanamıyordu** — sistem hangi
ihlali kabul etmeye izin vereceğini bilemiyordu.

**Dokuz yeni karar (K-18…K-26).** Öne çıkanlar: yasal kuralın değeri kanunun
değeridir, firma değiştiremez (`GUNLUK_AZAMI` **9 → 11**) · firma için ayrı
günlük azami kuralı açılmayacak · yasal ihlal hiçbir koşulda kabul edilemez ·
sağlık raporu için ayrı kural · kabul yetkisi = yayın yetkisi.

**Bir çelişki çıktı ve sessizce çözülmedi.** Mustafa K-18'i verirken *"firma
esnetemez ama ihlali onaylayabilir"* dedi; bu K-16 ile çelişiyordu. Çelişki
açıkça soruldu, üç seçenek sunuldu, **en katısı** seçildi. Yanlış dal seçilseydi
A4 kabul ölçütü, fikstürü ve yayın kapısı testleri yeniden yazılacaktı.

**Tablo doldurulurken iki tasarım sorunu çıktı.** `AKTIF_CALISAN` yasal bir
kural değil ama ihlali de kabul edilemez — iki gruplu tabloda sistem
*"ayrılmış çalışanı planda tutmayı kabul ediyorum"* seçeneği sunardı. Bayrak
ikiye ayrıldı: `yasal` dürüst etiket, `kabul_edilebilir` yayın kapısının baktığı
alan. İkincisi: `YETKINLIK_KAPSAMASI`'nda bayrak kuralın değil **satırın**
özelliği — ilk yardımcı yasal, barista değil.

**Mevzuat araştırması yapıldı** (Mustafa'nın isteğiyle, birincil kaynaklardan —
forum kullanılmadı). İki belirsizlik çözüldü, **katalogda olmayan bir yasal
kural** bulundu (`GECE_POSTASI_DEVRI`, Postalar Yön. md. 8) ve gece 7,5 saat
sınırının **turizm istisnası** ortaya çıktı (6645 s. K.) — ilk müşteri verisi
seyahat acentesine ait olduğu için bu teorik değil.

**Şartnamede dört yanlış bulundu:** §5.2'de 9 saat *"İş Kanunu üst sınırı"*
diye etiketlenmiş (kanun 11 diyor) · "27 kural" yazıyor, gerçek 33 · künye
tablosunda sürüm hâlâ 1.1 · `employee_contracts.gunluk_azami_saat` olmayan bir
yetkiyi gösteriyor.

**Okuma bir maddeyi de gereksiz çıkardı:** *"`leaves` durum alanı eklenecek"*
— v1.3 §8.3'te **zaten vardı.** K-9'un gerçek eksiği alan değil, yayınlanmış
planı düşüren akıştı.

**Fikstürler güncellendi, sonuç değişmedi:** 11/11 tutarlı, pytest yine
7 kırmızı / 3 yeşil / 4 atlanan. Kontrol edildi, tahmin edilmedi.

*Öğrenilen: "eksik" diye kaydedilen bir madde, kapatılmadan önce gerçekten
eksik mi diye bakılmalı. On maddenin biri zaten yapılmıştı; iki madde de liste
yazılırken hiç görülmemişti.*
→ `02-spec/v1.4-master-spec.md`, `02-spec/v1.4-hazirlik/`,
`00-DEVIR/08-URUN-KARARLARI.md`, `00-DEVIR/oturumlar/2026-09-16-sartname-v14.md`

**2026-09-16 · `DENETIM.py` İLK KEZ koştu · 17 hata buldu, hepsi düzeltildi**
**Ürün kodu değişmedi.** Betik 14 Eylül'de yazılmıştı ama üç oturumdur
koşturulamıyordu (uzaktan kabuk çalışmıyor). Mustafa bugün ilk kez kendi
makinesinde koşturdu.

**17 HATA, 14 uyarı.** Hepsi tek sebepten: `02-DEGISMEZLER.md` ve
`08-URUN-KARARLARI.md` içindeki 17 atıf hâlâ dondurulmuş **v2** ve **v4**
sürümlerini gösteriyordu, güncel **v5**'i değil. 14 uyarının tamamı tarihsel
dosyalarda — aksiyon gerekmiyor.

**Asıl bulgu, ve D-1 kuralını genişletiyor:** O iki dosya aslında
düzeltilmişti, ama düzeltme makineye hiç gönderilmemişti. Yakalanmama sebebi:
`v2` → `v5` değişimi **dosya boyutunu değiştirmiyor.** İki dosya da her iki
tarafta birebir aynı byte sayısındaydı (19 023 ve 29 883).
*"Yerel kopya = makine kopyası" varsayımının yanlış olduğunu biliyorduk;
yeni olan, **boyut karşılaştırmasının bu varsayımı doğrulamadığı.** Aynı
uzunluktaki bir düzeltme sessizce kaybolur.*

**Betiğin kendi hatası da çıktı:** `govde()` kod bloklarını silerek
çıkarıyor, bu yüzden sonraki satır numaraları kayıyordu. Bugün doğru satırı
göstermesi şanstı (o iki dosyada kod bloğu yok). Düzeltildi — blok yerine
aynı sayıda boş satır konuyor.

*Öğrenilen: bir denetim aracının kendi çıktısı da denetlenmeli. Yanlış satır
numarası veren hata mesajı insanı yanlış yere bakmaya gönderir.*
→ `DENETIM.py`, `00-DEVIR/02-DEGISMEZLER.md`, `00-DEVIR/08-URUN-KARARLARI.md`,
`00-DEVIR/oturumlar/2026-09-16-fikstur-ve-test-iskeleti.md` (EK bölümü)

**2026-09-16 · Fikstürler + test iskeleti yazıldı · yedi test BİLEREK kırmızı**
**Ürün kodu değişmedi, CI'ya dokunulmadı, 39/39 hâlâ yeşil.** Yeni paket CI'ya
**bağlanmadı** — kırmızı bir paketi kapıya bağlamak "main her zaman yeşil"
kuralını bozardı.

Onaylı kabul cümleleri (15 Eylül) önce **veriye**, sonra **koşan teste**
çevrildi. Zincir kapandı: kabul ölçütü → fikstür → test → (motor).

**Fikstürler:** 11 JSON + ortak sahne `_sahne-S10.json`. A5 yok — yaz saati
ertelendi (K-12). Fikstür kod değil veri; motor hangi dille yazılırsa yazılsın
aynı dosyalar koşar. Sahne 11 dosyadan ortaklaştırıldı; her senaryo yalnız
kendi `fark`ını taşıyor.

**Test iskeleti:** pytest çatısı (A1, A3, A4, A6, A7, A8, A9) ve `.cs.taslak`
uzantılı xUnit taslakları (A2, A10, A11, A12 + yayın kapısı, 20 test adı).
Sonuç: **7 kırmızı / 3 yeşil / 4 atlanan.** Kırmızı istenen durumdur —
spec §16.4 "kırmızı kanıt" kuralı, bir testin yeşile dönmeden önce kırmızı
yanmasını şart koşar.

**İki şey bilerek bozuk bırakıldı, ikisi de CI'ı korumak için:** C# taslakları
`.cs` değil (derlenirse CI kırılır, dayandıkları tablolar yok) ve pytest paketi
`dotnet test` kapısına bağlanmadı.

**Üç test motorsuz da yeşil** ve asıl işi onlar yapıyor: fikstürler
yükleniyor mu, fikstürde geçen her `kontrol` adının kodda gövdesi var mı,
motor yokluğu sessizce mi geçiliyor. Üçüncüsü yazılırken bir eksik yakalandı —
A07 fikstüründe kullanılan bir kontrolün gövdesi yoktu.

**Anti-kopya kararı:** `fikstur_yukleyici.py` ortak modüle çıkarıldı.
Denetleyici ile test aynı `fark` birleştirme mantığını kullanmasaydı,
denetleyici "tutarlı" derken test başka bir şey sınıyor olurdu.

**`DENETIM.py` yol kontrolü için düzeltme:** belgelerdeki `v5/...` biçimindeki
kısa yollar depo kökünden yazıldı (`08-motor-testleri/v5/...`), yoksa 3.
kontrol hepsini "bulunamayan yol" sayacaktı. Yazılmamış `02-spec/v1.4-master-spec.md`
bilerek-yok listesine gerekçesiyle eklendi.

*Öğrenilen: bir denetleyici yazmak, denetlediği şeyi yazmaktan daha çok
düzeltme doğuruyor. Yolları kısaltmak okurken rahattı, makine için yanlıştı.*
→ `08-motor-testleri/v5/fikstur/`, `08-motor-testleri/v5/testler/`,
`00-DEVIR/oturumlar/2026-09-16-fikstur-ve-test-iskeleti.md`

**2026-09-15 · Altın senaryolar A1–A12 ONAYLANDI · on yeni ürün kararı**
**Ürün kodu değişmedi, test eklenmedi, hiçbir test koşmuyor.** Bu bir karar
satırıdır, kilometre taşı değil — etiket atılmadı.

Spec §16.3'teki on iki senaryonun *"doğru çalışıyorsa ne görmeliyiz"* cümleleri
Mustafa tarafından **tek tek onaylandı**. Altı varsayımın (V-1…V-6) hepsi karara
bağlandı. A5 (yaz saati) ertelendi, altyapısı korunuyor.

**Üç sürüm gerekti.** v2 yazılım tarafına göre yazılmıştı; Mustafa *"ben tam
olarak neye onay veriyorum"* diye sorunca v3'te anlatım iş diline çevrildi.
Geri bildirimi v4'te içeriği değiştirdi — **sahne gerçekçi olmadığı için baştan
kuruldu** (çoklu vardiya tipi, part-time, cumartesi nöbeti), A2/A3/A7/A8
yeniden yazıldı. v5 onayın dondurulmuş hâli.

**On karar (K-8…K-17)** ve **bir geri alma (K-1)**. Öne çıkanlar: izin
planlamayı ezer · yönetici çözümsüz planı kabul edebilir (yasal kural hariç) ·
yayın kapısı — taslak ihlal taşıyabilir, yayınlanmış plan taşıyamaz ·
`MOLA_KAPSAMASI` yumuşadı · çalışan tercihi diye bir şey yok, uygunluk
sözleşmeden gelir.

**K-1 geri alındı ve sebebi kayda değer:** Claude 14 Eylül'de *"tam 11 saat
dinlenme ihlal mi?"* diye sormuştu. Mustafa *"ben neye yanlış karar verdim
anlamadım"* dedi ve haklıydı — yanlış karar vermemişti, **yanlış soru
sorulmuştu.** Aritmetik bir kenar durumu ürün kararıymış gibi sunulmuştu.

**İki şartname eksiği bulundu ve ikisi de senaryolar yazılırken çıktı, şartname
okunurken değil:** `leaves` tablosunda izin durumu alanı yok, ve §6 kataloğunda
**`yasal` sütunu yok** — ikincisi olmadan "hangi ihlal kabul edilebilir" sorusu
cevaplanamıyor, yani iki yeni karar uygulanamaz durumda. Yeni açık maddeler:
**A-15** (şartname v1.4, on maddelik fark) ve **A-16** (iki hukuki yorum uzman
bekliyor).

*Öğrenilen: kabul ölçütü yazmak, şartnameyi denetlemenin en ucuz yolu. Okurken
"yazılmış mı" diye bakarsın; senaryo yazarken "bu davranışı ifade edebiliyor
muyum" diye. İkinci soru eksiği bulur.*
→ `08-motor-testleri/v5/`, `00-DEVIR/08-URUN-KARARLARI.md`,
`00-DEVIR/oturumlar/2026-09-15-altin-senaryo-onayi.md`

**2026-09-15 · Çalışma biçimi: geri bildirim yüzeyleri · paralel ajan reddedildi**
**Ürün kodu değişmedi, test eklenmedi, ölçüm yapılmadı** — bu satır bir karar
satırıdır, kilometre taşı değil. Etiket atılmadı.

Mustafa bir videoda gördüğü dört pencereli modeli sordu (kod Claude'da, hata
ayıklama opencode'da paralel, ayrı pencerelerde testler ve sunucu günlükleri).
Model ayrıştırıldı: **işe yarayan yarısı ajanla ilgili değil**, kırmızının ne
kadar geç fark edildiğiyle ilgili.

**Alınan:** Aktif pencerenin yanına **yazmayan** bir gösterge penceresi —
günlükler sürekli (`docker compose logs -f`), testler **talep üzerine**
(`.\TEST.ps1`). Testler sürekli koşamıyor çünkü `TEST.ps1` API'yi önce
durduruyor (`00-BURADAN-BASLA.md` §7). *Bu ortam gerçeği olmasa, sürekli
koşan bir test penceresi kurulur ve API'nin neden sürekli düştüğü saatlerce
aranırdı.* Doğurduğu asıl kural: **ajan "bitti" demeden önce testleri kendisi
koşar.**

**Reddedilen:** Paralel ikinci **yazıcı** ajan. Gerekçe depodan geldi — R5
(*iki pencere yazar, sürüklenme*) 14 Eylül'de kapatılmıştı; yeniden açacak
ölçülmüş bir gerekçe yok. opencode `06-ACIK-RISKLER.md`'deki *"şimdilik
kullanılmayacak"* tablosuna girdi; **salt-okunur inceleyici** olarak M-09
doğrulayıcısından sonra yeniden bakılacak, iki haftalık ölçüm şartıyla.

**Yeni devir dosyası açılmadı** — R7 sorusu soruldu, cevabı "evet, var olan
bir dosyanın bölümü olabilir" çıktı. `00-DEVIR/` kökü **dokuz dosyada kaldı.**
→ `00-DEVIR/00-BURADAN-BASLA.md` §5b, `00-DEVIR/06-ACIK-RISKLER.md`,
`00-DEVIR/oturumlar/2026-09-15-calisma-bicimi-opencode.md`

**2026-09-14 · Altın senaryolar tanımlandı, devir denetimi betiğe çevrildi**
Spec §16.3'teki A1–A12'nin beklenen sonuçları Türkçe kabul cümlelerine
çevrildi — motor yazılmadan, motora bakmadan, şartnameden türetilerek.
`08-motor-testleri/` açıldı: `v1/` taslak (donduruldu), `v2/` kararlar
işlenmiş hâli, bir örnek fikstür ve fikstürün kendi içinde tutarlılığını
kontrol eden bir betik. **Cümleler onay bekliyor; hiçbir test koşmuyor.**

**Yedi ürün kararı** alındı ve yeni bir sicile geçti (`00-DEVIR/08-URUN-KARARLARI.md`,
K-1…K-7). En çok şeyi değiştiren K-1: **sınır değerler ihlal sayılır** — tam
11 saat dinlenme, tam 9 saat günlük çalışma. Firma ayarı olarak esnek
bırakılıyor (`sinir_dahil` parametresi). K-7 doğrudan yeni bir test doğurdu:
hafta toplamında yetersiz kapasite, hücre bazlı teşhisin göremediği durum.

**`DENETIM.py` yazıldı** — `00-BURADAN-BASLA.md` §5'teki denetim ritüeli artık
elle değil makineyle yapılıyor: test adları `DisplayName` ile birebir eşleşiyor
mu, sayılar tutuyor mu, dosya yolları var mı, commit edilmemiş devir dosyası
kaldı mı. *Gerekçe: §5b "asıl güvence testlerdir, doküman değil" diyor ama
`00-DEVIR/` bu ilkenin dışında kalan tek parçaydı.*

**İlk koşusunda elle bulunmamış altı tutarsızlık çıktı, dördü düzeltildi:**
üç dokümanda `M0` test adı eksik ya da kısaltılmış yazılmıştı (biri
`0 - Baglanan...` diye, baştaki M düşmüş), `H1` kısaltılmıştı, ve
`02-DEGISMEZLER.md` özet tablosu **45/41** diyordu — doğrusu **47/39**.
Y-13 ve Y-14 satır olarak eklenmiş ama özet güncellenmemişti. D-3 hatası
14 Eylül'de iki yerde düzeltilmişti; **üçüncü yer gözden kaçmıştı.**

Pencere protokolüne **açılış beyanı** eklendi: yeni pencere iş yapmadan önce
ne okuduğunu ve sıradaki adımı nasıl anladığını söyler. Risk tablosundaki
*"doküman yanlış başlarsa yakalamaz"* açığını kapatıyor.
⚠ `00-DEVIR/` dokuz dosyaya ulaştı — **R7 eşiği.**
→ `08-motor-testleri/`, `00-DEVIR/08-URUN-KARARLARI.md`, `DENETIM.py`

**2026-09-14 · Gerçek müşteri verisi analiz edildi · CI yeşil yandı** ⚠
*(Bu satır 14 Eylül'de yazılmamıştı; `DENETIM.py`'nin "değişim günlüğü geride"
kontrolü ortaya çıkardı ve geriye dönük eklendi.)*

Bir seyahat acentesinin 3,5 aylık PDKS (48 CSV) ve vardiya planı (71 Excel)
dosyaları analiz edildi — **4.625 vardiya, 98 kişi, 105 gün**. Sonuç:
**529 kural ihlali** ve kimse fark etmemiş. 274 haftalık saat aşımı, 167
altı günden uzun ardışık çalışma, 88 kısa dinlenme. **A-14 kapandı:** ürünün
gerçek operasyonda işe yarayıp yaramayacağı artık tahmin değil, ölçüm.

**182 atama gece yarısını aşıyor** — kenar durum değil, olağan işleyiş. Müşteri
Excel'inde gece yarısını yazabilmek için `00:00` yerine **`23:59` kullanmış
(137 kez)**; içe aktarma bunu çevirmezse 1 dakikalık sistematik hata girer.

**CI yeşil yandı — A-4 kapandı.** GitHub Actions koştu, 39 test + 7 mimari
kuralı geçti. Kurallar artık öneri değil **kapı**. Pencere protokolü
kararlaştırıldı ve `00-BURADAN-BASLA.md` §5b'ye yazıldı.

**Master Spec v1.3** yazıldı (v1.2'ye dokunulmadı): gece yarısı zaman modeli
Z-1…Z-6, DST taşınabilir-pasif, lookback 14 gün, onarım döngüsü, idempotency,
**tekrarlanabilirlik garanti edilmiyor** (yerine plan kopyalama), ve **§16 test
stratejisi + 12 altın senaryo**. Köken dokümanı depoya alındı — beş "yeni
bulgu" orada zaten yazılıydı.
→ `02-spec/v1.3-master-spec.md`, `00-DEVIR/07-GERCEK-VERI-BULGULARI.md`, `07-motor/`

**2026-09-12 · Devir paketi kuruldu — ve kurulurken bir açık buldu** ⚠
Uzun sohbetlerde bağlam kaybını önlemek için projenin hafızası sohbetten
depoya taşındı: `00-DEVIR/` altında 8 dosya. Sohbet özeti değil **devir
paketi** — fark şu ki buradaki her iddia bir test adına, dosya yoluna ya da
çalıştırılabilir komuta bağlı. *Sohbet özeti yanlış bir varsayımı sessizce
taşıyabilir; test yeşil yanar ya da yanmaz.*

**Kurulurken bir açık çıktı.** `RISKLER-VE-ONLEMLER.md`, projedeki en ciddi
hatanın (süper kullanıcı RLS'i aşıyordu) bekçisi olarak bir test gösteriyordu
— **o test hiç var olmamıştı.** Doküman iki gün boyunca, en çok güvenilen
satırında yanlıştı. Bulan şey, her iddiayı bir teste bağlama kuralı oldu:
bağlanacak test yoktu.

**`M0` eklendi** — `M1`'in önünde duruyor, çünkü M1 *"RLS tanımlı mı"*, M0
*"RLS beni gerçekten durduruyor mu"* diye sorar. Rol **adına** değil,
`current_user`'ın **yetkisine** bakıyor (`rolsuper`, `rolbypassrls`); böylece
bağlantı dizesi sahibi role çevrilse de, role sonradan yetki verilse de
yakalıyor. Kanıt: `tshift` → `t/t`, `tshift_app` → `f/f`.
**39/39 yeşil.** Değişmez tablosu 39/45 → 41/45 bekçili.

**Karar: kabul ölçütü kod yazılmadan önce yazılır** ve Mustafa onaylar; test
o cümlenin çevirisi olur. Her cümle kaynağına göre `[spec]` / `[karar]` /
`[çıkarım]` diye işaretleniyor — `[çıkarım]` olanlar yapay zekânın türettiği,
onaylanmamış varsayımlar. Sebebi D6 (11 Eylül): kodu yazan testi de yazarsa
aynı yanlış varsayım iki yere birden geçebilir.

Ayrıca GPT'nin ürettiği kalite araştırması değerlendirildi (kaynakları
denetlendi: gerçek, bir künye hatası hariç). Test kapsamımız sahanın 20
senaryo sınıfına oturtuldu: **4'ünde derin, 2'sinde kısmi, 14'ünde hiç yok.**
Derinlik iyi, sorun genişlik.
→ `00-DEVIR/`, `KALITE-ARASTIRMASI-DEGERLENDIRME.md`

**2026-09-11 · İlk ekran (Next.js) — dikey dilim tamamlandı**
Giriş ekranı ve çalışan listesi. Veritabanından ekrana kadar bütün katmanlar
bağlı: PostgreSQL + RLS → EF → kimlik → yetki → denetim → API → arayüz.
Aynı ekran dört farklı kullanıcıda farklı davranıyor — müdür tüm listeyi ve
"Yeni çalışan" butonunu görüyor, şef yalnız kendi ekibini, çalışan yalnız
kendini, izleyici hepsini ama hiçbir eylem düğmesi olmadan.

**Karar: jetonlar `httpOnly` çerezde, tarayıcı koduna hiç girmiyor.**
Yaygın yöntem `localStorage`'dır; kolaydır ama sayfadaki HERHANGİ bir betik
jetonu okuyabilir (sızmış bağımlılık, XSS, tarayıcı eklentisi). Çerez
yönteminde tarayıcı jetonu isteğe ekler ama sayfa kodu göremez.
Yan fayda: API çağrıları Next.js sunucusundan gittiği için CORS ayarı
gerekmiyor — tarayıcı hiçbir zaman doğrudan API'ye gitmiyor.

**Yeni çalışan kaydı.** `POST /api/v1/employees` (`calisan.duzenle` izni) ve
form için `GET /api/v1/departments` · `GET /api/v1/teams` — ikisi de kapsama
göre filtreli, çünkü kullanıcı göremeyeceği bir departmanı seçenek olarak da
görmemeli.

**İlke: göremeyeceğin kaydı oluşturamazsın.** Listeyi filtreleyen ifade ile
"bu kaydı oluşturabilir misin" kontrolü tek bir `KapsamKurali` fonksiyonundan
geliyor; biri `IQueryable`'a uygulanıyor, diğeri derlenip tek kayda. İki ayrı
yerde yazılsaydı zamanla ayrışır ve bir gün "listede göremediğim ama
oluşturabildiğim kayıt" ortaya çıkardı — risk dokümanındaki 4 numaralı hata
sınıfı.

**Benzersizlik kontrolü kodda değil, kısıtta.** Önce "bu personel no var mı"
diye sorup sonra yazmak yetmez: iki istek aynı anda gelirse ikisi de "yok"
görür. Veritabanı kısıtı yapısal olarak engelliyor; kod yalnızca hatayı
anlaşılır mesaja çeviriyor (`PERSONEL_NO_TEKRAR`).

**Not:** `middleware.ts` içindeki kontrol bir güvenlik sınırı DEĞİL, kullanıcı
deneyimi düzenlemesi. Yalnız çerezin varlığına bakar, içeriğini doğrulamaz
(imza anahtarı orada yok). Asıl kontrol API'de. Aynı şey gizlenen düğmeler
için de geçerli: yetkisi olmayan butonu görmez, ama zorla çağırsa sunucu
403 döner.
→ `04-kod/frontend/`

**2026-09-11 · Denetim kaydı (audit_log) — risk listesindeki kırmızı madde kapandı**
Her oluşturma, güncelleme ve silme otomatik olarak kaydediliyor: kim, ne zaman,
hangi kayıt, hangi alanlar, önceki ve yeni değer, IP.
Üç kasıtlı özellik:
1. **Otomatik** — uçlarda tek tek çağrılmıyor, EF'in kaydetme akışına bağlı.
   Yeni tablo ya da yeni uç kendiliğinden kapsanıyor.
2. **Aynı işlemde** — değişiklikle denetim satırı tek `SaveChanges`'te gidiyor;
   biri yazılıp diğeri yazılamıyor. (İstemci tarafında üretilen UUIDv7
   kimlikler sayesinde mümkün.)
3. **Sadece eklenir** — `tshift_app` rolünün `audit_log` üzerinde UPDATE ve
   DELETE yetkisi YOK. Kısıt uygulamada değil veritabanında, çünkü uygulama
   katmanı açığın bulunacağı katmandır.
Parola ve jeton özetleri kayda girmez: alanın **değiştiği** kaydedilir,
**değeri** kaydedilmez. Yeni izin: `denetim.gor` (kiracı yöneticisi + izleyici).
Yeni uç: `GET /api/v1/audit`. 7 denetim testi + M6 mimari testi; toplam 38/38.
→ `04-kod/backend/src/TShift.Infrastructure/Denetim/`, `04-kod/db/rls/05-denetim-kaydi.sql`

**2026-09-11 · Test temizliği tek yere alındı**
Dört test dosyasında dört ayrı tablo listesi vardı — yeni tablo eklendiğinde
üçünü güncelleyip birini unutmak an meselesiydi. `TestTemizlik` sınıfına
taşındı. Temizlik artık **sahibi rolle** yapılıyor; uygulama rolü denetim
kaydını silemediği için (kasıtlı) başka türlü mümkün de değil.

**2026-09-11 · D6 testi düzeltildi — iddia yanlış kurulmuştu**
"B kiracısı hiçbir denetim kaydı görmemeli" diye yazmıştım; yanlış bir iddia,
çünkü B kendi işlemlerinin kaydını görmeli. Sınanmak istenen şey "B, **A'nın**
kayıtlarını göremez" idi. İddia zayıflatılmadı, gerçekte sınanan şeye çevrildi
ve kimlik karşılaştırmasıyla daha keskin hale geldi. Kod değişmedi.

**2026-09-10 · Mimari testleri ve risk dokümanı**
Özellik değil **yasa** sınayan bir test katmanı eklendi: kiracıya ait her
tabloda RLS açık mı, RLS dışı tablolar bilinen istisnalar mı, korumasız uç
var mı, kültüre bağımlı `ToLower()` kullanılmış mı, ayar dosyasında sır var mı.
Bunlar gelecekteki hatalara önceden konmuş bekçiler — bugün bir şey yakalamak
için değil, altı ay sonra unutulacak bir kuralı hatırlatmak için varlar.
`RISKLER-VE-ONLEMLER.md`: yapay zekâyla geliştirmede 15 hata sınıfı, hangisinin
sessiz hangisinin gürültülü olduğu, gerçekten geri dönülmez dört şey, ve
kırmızı çizgiler. **Açık madde: denetim kaydı (audit log) pilot öncesi
yazılmalı — tutulmayan geçmiş sonradan üretilemez.**
→ `RISKLER-VE-ONLEMLER.md`, `04-kod/backend/tests/TShift.Tests/MimariTestleri.cs`

**2026-09-10 · Roller ve izinler — kapsam devrede**
Spec §3.2 yetki matrisi koda geçti. 5 sistem rolü, 18 izin kodu, departman/ekip
kapsamı, süreli yetki devri. Uçlar izin politikalarıyla korunuyor; çalışan
listesi kapsama göre filtreleniyor. Aynı firmada müdür 3, şef 2, çalışan 1,
izleyici 3 kayıt görüyor — izleyicide hiçbir yazma izni yok.
9 yetki testi + 5 HTTP sınırı testi; toplam 26/26 yeşil.
→ `04-kod/backend/src/TShift.Infrastructure/Yetki/`, `04-kod/db/rls/04-yetki-tablolari.sql`

**2026-09-10 · SPEC'TEN BİLİNÇLİ SAPMA: kapsamsız kullanıcı hiçbir şey görmez** ⚑
Spec §3.2: *"Kapsamı olmayan kullanıcı tüm kiracıyı görür."*
Uygulama: kapsam seviyesi `Kapsam` olup hiç kapsam satırı olmayan kullanıcı
**hiçbir şey görmez.**
Gerekçe: kapsamı atanmayı unutulan bir departman müdürü, spec'teki davranışla
sessizce tüm firmayı görürdü — yapılandırma eksikliğinin yetki genişlemesine
dönüşmesi. Kiracı yöneticisi zaten `Kiraci` seviyesinde olduğu için spec'in
asıl kastettiği durum bozulmuyor. Eksik yapılandırma artık "göremiyorum"
şikâyeti üretir, sızıntı değil. Y8 testi bunu sabitliyor.

**2026-09-10 · Karar: izin kodları jetonda, kapsam veritabanında**
İzinler JWT'ye yazılıyor (spec §7.4) — bedeli: geri alınan bir yetki, jeton
süresi dolana kadar (≤15 dk) taşınmaya devam eder; acil iptalde yenileme
jetonları da düşürülmeli. Kapsam jetona konmadı, her istekte okunuyor:
liste uzayabilir ve kapsam değişikliğinin anında etkili olması iyidir.

**2026-09-10 · Bulunan hata: JWT `sub` talebi yeniden adlandırılıyordu** ⚠
21 test yeşilken korumalı bütün uçlar 401 dönüyordu. JwtBearer, gelen jetonun
`sub` talebini eski Microsoft şemasına çeviriyor; kod `sub` diye aradığı için
kullanıcı kimliği null geliyor ve uç "yetkisiz" diyordu. Yetki mantığı
doğruydu; kırılan yer iki katmanın buluştuğu sınırdı.
Çözüm: `MapInboundClaims = false`.
**Testler bunu yakalamadı** — hepsi servisleri doğrudan çağırıyordu, HTTP
katmanından geçmiyordu. Yakalayan şey kanıt betiği oldu.
Bu yüzden `HttpSinirTestleri` eklendi: uygulamayı bellek içinde ayağa kaldırıp
gerçek istek atar. Ders: birim testi katmanın İÇİNİ, uçtan uca test
katmanların ARASINI doğrular; biri diğerinin yerine geçmez.

**2026-09-10 · Kimlik katmanı — `X-Tenant-Id` başlığı kaldırıldı**
Kiracı kimliği artık sunucunun imzaladığı JWT'den okunuyor; istemcinin
yazdığı başlıktan değil (spec §10). Önceki hali bilerek kabul edilmiş geçici
bir açıktı — isteyen istediği firmanın kimliğini yazabiliyordu.
Eklenenler: Argon2id parola saklama (64 MB/3/4), 15 dakikalık erişim jetonu,
30 günlük **döner** yenileme jetonu, jeton yeniden kullanım tespiti
(çalınırsa o kullanıcının tüm oturumları düşer), 5 deneme / 15 dakika kaba
kuvvet kilidi. Uçlar: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/me`.
7 yeni test; toplam 12/12 yeşil.
→ `04-kod/backend/src/TShift.Infrastructure/Kimlik/`, `04-kod/db/rls/03-kimlik-tablolari.sql`

**2026-09-10 · Karar: `login_attempts` bilerek RLS dışında**
Kaba kuvvet sayacı, kiracının kim olduğu bilinmeden yazılmak zorunda — aksi
halde saldırgan var olmayan bir firma adı yazarak kilidi tamamen atlar.
Tablo hiçbir API ucundan dışarı açılmaz; parola ya da jeton içermez.
Gerekçe hem koda hem SQL betiğine yazıldı ki ileride "RLS unutulmuş" diye
düzeltilmesin.

**2026-09-10 · Karar: giriş isteği firma kısa adını taşır**
`users` benzersizliği `(tenant_id, eposta)` olduğu için e-posta tek başına
kimlik değil; aynı kişi iki firmada kullanıcı olabilir. Canlıda firma alt
alan adından gelecek (`anadolu-cm.tshift.com`), kullanıcı yazmayacak.

**2026-09-10 · Not: makinede Windows PowerShell 5.1 var, 7 değil**
Betikler 5.1 uyumlu yazılacak (`-SkipHttpErrorCheck` gibi 7'ye özgü
parametreler kullanılmayacak) ve `.ps1` dosyaları saf ASCII olacak — 5.1
betikleri ANSI okuyor, UTF-8 türkçe karakterler ayrıştırıcıyı bozuyor.

**2026-09-10 · Dikey dilim 1: çok kiracılık yalıtımı ayakta**
Veritabanı, alan modeli, EF katmanı, RLS, API ve testler uçtan uca bağlandı.
7 tablo, ilk migration (`20260910002040_Ilk`), 5 test yeşil.
İki firma aynı API adresinden birbirinin verisini göremiyor — betikle kanıtlandı.
→ `04-kod/`, `04-kod/YALITIM-KANITI.ps1`

**2026-09-10 · Bulunan açık: süper kullanıcı RLS'i aşıyordu** ⚠
Satır seviyesi güvenlik doğru yazılmış, açılmış ve `t/t` diye doğrulanmıştı;
ama uygulama veritabanına Docker'ın süper kullanıcısıyla (`tshift`) bağlanıyordu.
PostgreSQL'de süper kullanıcı RLS'i tamamen aşar — `FORCE` bile durdurmaz.
Güvenlik kâğıt üstünde vardı, çalışmada yoktu.
Çözüm: iki rol. `tshift` migration çalıştırır, `tshift_app` uygulamayı taşır
(süper değil, `NOBYPASSRLS`). Ayrıca 0 numaralı **bekçi test** eklendi:
bağlanan rol süper kullanıcıysa test paketi kırmızı yanıyor.
Açığı bulan şey inceleme değil, testin kendisi oldu.
→ `04-kod/db/rls/02-uygulama-rolu.sql`

**2026-09-09 · Master Spec v1.1**
Spec'in gözden geçirilmesinden 9 değişiklik: kimlik katmanı kendi kodumuza alındı
(Keycloak çıktı), izin etki analizi yeni özellik olarak eklendi, uygulanan
önerilerde geri alma, metrik açıklama bileşeni, içe aktarmadan yapay zekâ
kaldırıldı, seçilmeyen plan adayları için 30 günlük saklama politikası,
departman/şube isimlendirmesi, arayüz bileşen kütüphanesi kararı, plan revizyon
karşılaştırması kapsam dışı. Tablo sayısı 37 → 44.
→ `02-spec/v1.1-master-spec.md`

**2026-09-09 · Pilot kararı: gölge pilot**
Pilot müşteri beklenmeyecek. Çağrı merkezi operasyonundan gerçek veri alınıp
gerçek kullanıcı olmadan uçtan uca çalışılacak. Sektör paketi önceliği:
çağrı merkezi.

**2026-09-09 · Master Spec v1.0 yazıldı**
Ürün tanımından veri modeline kadar tüm spec: 15 bölüm, 37 tablo, 24 ekran,
27 kural, backend servis listesi, motor sözleşmesi, Ocak sonu teslim planı.
→ `02-spec/v1.0-master-spec.md`

**2026-09-09 · Föy notları görüşüldü**
Motor dili Python'da kaldı (Go elendi — resmî OR-Tools bağlayıcısı yok).
Yapay zekâ maliyeti ölçüldü: kiracı başına aylık $0,80–1,60. Ocak sonu hedefi
kapsam kesintileriyle gerçekçi bulundu.

**2026-09-09 · Çalışma kökü kuruldu**
Proje dosyaları `Desktop\Tshift` altında toplandı. Versiyonlama kuralı belirlendi.
→ `README.md`

**2026-09-09 · Spike testleri v1 olarak donduruldu**
7–8 Eylül'de yapılan tüm motor testleri arşivlendi; kronoloji ve ölçülen sayılar
`01-spike/README.md` içinde.

**2026-09-09 · Karar föyü dolduruldu**
Teknoloji, ürün ve eksik bilgi başlıklarının tamamı cevaplandı. 6 yeni kural seçildi.

**2026-09-08 · Karar föyü yayınlandı**

**2026-09-07/08 · Motor fizibilite testleri koşuldu**
CP-SAT motoru iki sektörde 0 sert ihlalle plan üretti. 12 kritik hata bulundu
ve düzeltildi. → `01-spike/README.md`
