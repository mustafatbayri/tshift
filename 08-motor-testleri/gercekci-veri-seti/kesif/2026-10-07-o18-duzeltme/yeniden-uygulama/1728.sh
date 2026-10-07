cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/00-DEVIR && python3 - <<'PYEOF'
import io
p="oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md"
s=io.open(p,encoding="utf-8").read()
R=[]
R.append(('''14. [6 Ekim 23:44 – 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* varsayılan; hakem ağırlıklardır) koda indi; K-62 (merdiven ve kadro)](#14--6-ekim-2344--7-ekim-0045--k-61-önce-fazla-mesaisiz-varsayılan-hakem-ağırlıklardır-koda-indi-k-62-merdiven-ve-kadro)
''','''14. [6 Ekim 23:44 – 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* varsayılan; hakem ağırlıklardır) koda indi; K-62 (merdiven ve kadro)](#14--6-ekim-2344--7-ekim-0045--k-61-önce-fazla-mesaisiz-varsayılan-hakem-ağırlıklardır-koda-indi-k-62-merdiven-ve-kadro)
15. [7 Ekim 01:00–03:30 — bağımsız inceleme: 00:45 sürümü ilkeyi çiğniyordu (O-18, bulgu 23); düzeltme](#15--7-ekim-01000330--bağımsız-inceleme-0045-sürümü-ilkeyi-çiğniyordu-o-18-bulgu-23-düzeltme)
'''))
R.append(('''**Okuma.** *"Evet"* koşulsuz bir evet değil: hakem ağırlıklar. Seçeneğin o
günkü hâli ise fazla mesaisiz plan varken fazla mesaili planlara hiç
bakmıyordu — ilkeyle arasında bir fark vardı. Karıştıran bir durum yoktu,
ama farkın kendisi Mustafa'ya sayıyla söylenmeli: bugünkü ağırlıklarda 1 saat
fazla mesai = 333 kişi-saat hedef eksiği (DENGELI), yani örneği (*"3 saat
fazla mesaili plan oldukça daha optimum"*) bu kurda oluşmaz; kur K-30'un
ağırlığa yazılmış hâli.
''','''**Okuma.** *"Evet"* koşulsuz bir evet değil: hakem ağırlıklar. Seçeneğin o
günkü hâli ise fazla mesaisiz plan varken fazla mesaili planlara hiç
bakmıyordu — ilkeyle arasında bir fark vardı. Karıştıran bir durum yoktu,
ama farkın kendisi Mustafa'ya sayıyla söylenmeli: bugünkü ağırlıklarda 1 saat
fazla mesai = 333 kişi-saat hedef eksiği (DENGELI), ~~yani örneği (*"3 saat
fazla mesaili plan oldukça daha optimum"*) bu kurda oluşmaz~~ *(yanlış —
§15)*; kur K-30'un ağırlığa yazılmış hâli.

> ⚠ **Bu bölümün "Yapılan" ve "Doğrulama" kısımları 7 Ekim 03:30'da
> geçersiz oldu (§15, O-18).** Buradaki sürüm (ağırlık koşulu, `uygulandi`,
> 26 test, 44 mutasyon) Mustafa tarafından hiç koşulmadı ve commit edilmedi.
'''))
s2=s+'''
## 15 · 7 Ekim 01:00–03:30 — bağımsız inceleme: 00:45 sürümü ilkeyi çiğniyordu (O-18, bulgu 23); düzeltme

Bu pencerenin alışkanlığı: kod *"indi"* denmeden işi görmemiş ayrı ajanlara
inceletmek. 00:45'te önce *"indi"* yazıp sonra inceletmiştim — sıra yanlıştı
(O-18'in bekçilerinden biri). İki ajan (A ve B; kopya üzerinde, kodu
koşarak) 01:00 civarı döndü. Ortak bulgu, kendi koşumla doğrulandı
(`inceleme/ajan-a/repro_min.py`, `ajan-b/b3_s3_cesitleri.py`; bulutta
0,6 sn ve birkaç saniye):

| Sahne (ürün ağırlıkları) | Tam model, kanıtlı optimum | 00:45 sürümü (ürün yolu) |
|---|---|---|
| S1: tek kişi, DENGELI, SAAT_DENGESI yumuşak; A = 7,5 sa net (Pzt–Cum), B = 7,75 sa (Cmt); 5A + B = 45 sa 15 dk | **750**, 15 dk fazla mesai | 2.256, 0 fazla mesai (bir A günü düşer: 435 dk × 5 + 9 hücre × 9) |
| F2: aynı kişi, KAPSAMA, SAAT_DENGESI sert; fazla mesaisiz tek dolum 15:00–01:00 (9 sa net), talebin dışında | **750** | 880 (44 hücre × 20) |
| S3b: 12 kişi, KAPSAMA, SAAT_DENGESI sert; ERKEN 04:00–12:30 talebin dışında; P9 × 4 + PL = 45 sa 15 dk | **9.000**, tam **3 saat** | 12.000 |
| S3c / S3d: iki ekibe üye tek kişi (K-50), DENGELI / KAPSAMA | **750** | 900 / 2.000 |
| S1 × 400 kişi (56.854 değişken; gerçekten iki aşamalı yol) | **300.000** | 902.400 |

Ajan A'nın rastgele avı: çeyrek saat ızgaralı karışık şablonlar + yumuşak
SAAT_DENGESI ile 8/400 karşı örnek; gerçekçi netlerle (7,5 / 9 / 4,25 sa; en
küçük adım 90 dk) 0/1.200. 500 kişilik sette en küçük şablon taşmaları 75 dk
(satış, back office), 30 dk (müşteri hizmetleri), 15 dk (40 saatlik sezonluk
kadro): orada oluştuğu gösterilmedi, oluşmayacağı kanıtlı değil.

**Neden yanlıştı.** Hesabım *"bir saat fazla mesai en çok bir-iki kişi-saat
kazandırır"* idi; fazla mesai çeyrek saatlik adımlarla gelir ve küçük bir adım
bütün haftanın düzenini açar (bir gün daha çalışmak, sözleşme saatini
doldurmak, talebin içindeki şablona geçmek, iki ekibi birden kapatmak).
Ağırlık koşulu bunu göremezdi; testim de tek şablonlu düz sahneyle yazılmıştı
(en küçük adım 3 saat). Tam metin: `05-HATA-OTOPSILERI.md` O-18.

**İncelemenin öteki bulguları** (hepsi ele alındı): küçük model ↔ büyük model
aynı girdide farklı karar (yol bağımlı politika — düzeltmeyle ikisi de
ağırlıklara göre); *"İyileştir"* yolu kısayolu hiç görmüyor (bilinen sınır
olarak yazıldı); koşul "daraltılacak alan var mı"dan önce (koşul kalktı);
`FAZLA_MESAI_TAVANI` yokken "bulundu" sayılan deneme `mola_adimi: False` ile
küresel kanıtı düşürüyor (alanlar açıldığı için model tam, kanıt küresel);
`int(ObjectiveValue())` kırpıyor (65154 ↔ 65155; `int(round())`, test);
başlık "≤ %20" (en kötü hâlde iki pay — düzeltildi); iyileştirme eğrisi
yazılmıyordu (eklendi, `ilk_asama_iyilestirme.iyilesme`); keşif OKU-BENI
*"devreden adalet yükü hepsinde 0"* yanlış (üretici 124 kişiye `devir_yuk`
yazıyor; boş olan geçen haftanın vardiyaları — düzeltildi); K-61 metnindeki
abartılar (*"öteki kalemler de iyileşti"*, *"%40 → %0,3"* yalnız DENGELI,
*"10 yeni"* 11, *"286 hepsi öldü"* grup sayılmadan — düzeltildi); `kalite-olc`
metinleri (`mola_adimi_tam` "= varsayılan", `ipucu_kapali` iki şey farklı,
"(alan yoksa … kapalı)" — düzeltildi).

**Mustafa'ya 02:35'te söylendi** (blok koşma; ne bulundu, neden yanlıştı,
ne yapılıyor).

**Düzeltme (02:40–03:30).**

1. *Motor* (`coz.py`): bulununca `_fazla_mesaiyi_serbest_birak` — plan ipucu,
   alanlar açık, iyileştirme tam ağırlıklı amaçla o plandan; ağırlık koşulu ve
   `_fazla_mesai_kisayolu_gecerli` kaldırıldı; `fazla_mesai_sifirda_tut`
   (varsayılan False) 6 Ekim'in sert kesimini ölçüm için saklıyor; çıktıda
   `uygulandi` yerine `sifirda_tutuldu`; `_sinir_kapsami` yalnız sert kesimde
   *"fazla_mesaisiz"*; `_CozumSayaci` eğri tutuyor; amaç değeri
   `int(round())`. Not metni *"en aza indirilir"* demiyor (*"azaltmaya
   çalışır; en azı olduğu kanıtlı değildir"*).
2. *Testler* (`test_fazla_mesai_once_sifir.py` 26 → 27): bölüm 1 ürün yolu
   (alanlar geri açılır, ipucu fazla mesaisiz plan) + sert kesim ölçüm; 3b
   ürün yolunda küresel sınır yazılır, sert kesimde yazılmaz; bölüm 5 yeniden:
   Mustafa'nın örneği — fazla mesaisiz plan **bulunsa da** 3 saatlik plan
   seçiliyor, sert kesim 16.000 döndürüyor; dört karşı örnek sahnesi (tam
   model kanıtlı optimum = ürün yolu; sert kesim daha kötü); kanıtlı optimumla
   aynı puan (iki sahne); eğri; yuvarlama. `test_demir_secenekleri.py`
   `_sinir_kapsami`.
3. *Mutasyon* (`fm_sifir` 44 → 43; toplam 285): 15 koşul mutasyonu kalktı,
   sert kesim / geri açma / `sifirda_tutuldu` / eğri / yuvarlama mutasyonları
   geldi; çapaların hepsi tam bir kez eşleşiyor.
4. *Ölçüm aracı*: `fm_once`, `fm_once_kapsama` (ürün yolu), `fm_sert`,
   `fm_sert_kapsama` (6 Ekim gecesinin hâli); bulgu 21'in kayıt adları
   (`fm_once_sifir*`) sert kesime sabitlendi; kayıtta `sert_kesim`; satır
   iki hâli ayırıyor; `test_kalite_olc.py` 18 güncellendi.
5. *Kayıtlar*: şartname §6.7 yeniden yazıldı, §11.3 dört satır, değişiklik
   61 (60 üstü çizili notla); K-61 düzeltme bölümü ve üstü çizili cümleler;
   K-30 7 Ekim notu; O-18; T-60 bulgu 23 ve yeni "Sıradaki adım";
   BURADAN-BASLA 03:30 paragrafı ve T-60 satırı; değişim günlüğü; keşif
   OKU-BENI.

**Doğrulama (bulut, 2 çekirdek; asıl kapı Mustafa'nın koşuları).**

| Ne | Sonuç |
|---|---|
| Karşı örnekler, düzeltilmiş motor (`duzeltme/karsi/dogrula.py`) | beş sahnede ürün yolu = kanıtlı optimum (750 / 750 / 9.000 / 750 / 750); sert kesim 2.256 / 880 / 12.000 / 900 / 2.000 |
| `09-motor` testleri, 41 dosya | **583 geçti** (≈126 sn) |
| `test_kalite_olc.py` | 18 geçti |
| Mutasyon, grup grup | aşağıda (§15 sonu); toplam iddiası tam koşudan sonra (O-15) |
| Küçük ölçekli ön ölçüm, 49 kişi, 20 sn, tek koşu | 6 Ekim öncesi 11.918 (3 sa) · sert kesim 2.758 (0) · **düzeltilmiş yol 2.713 (0)**; iyileştirme boyunca fazla mesai 0'da kaldı |

**Açık ürün sorusu.** K-30'un ilk satırı ile K-61'in ilkesi birbirini tam
örtmüyor; motor K-61'e göre yazıldı; Mustafa'ya soruldu (K-61'in düzeltme
bölümünde yazılı).

**Sıradaki.** Mustafa: testler, DENETIM, commit + push → tam mutasyon (damga
285) → bulgu 23 ölçümü (`fm_once,fm_once_kapsama`, 900 sn, üçer koşu; karar
kuralı K-61'de). Sonra K-62.
'''
for old,new in R:
    assert s2.count(old)==1, old[:90]
    s2=s2.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s2)
print("ok")
PYEOF