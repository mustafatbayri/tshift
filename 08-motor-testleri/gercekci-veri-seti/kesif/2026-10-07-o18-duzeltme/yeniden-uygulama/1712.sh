cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/00-DEVIR && python3 - <<'PYEOF'
import io
p="06-ACIK-RISKLER.md"
s=io.open(p,encoding="utf-8").read()
R=[]
R.append(('''**6 Ekim 23:44 – 7 Ekim 00:45 — Mustafa'nın kararları: K-61 (*önce fazla
mesaisiz* ürünün varsayılanı; hakem ağırlıklardır) ve K-62 (veri seti
merdiveni, kadro); K-61 koda indi (bulut).**
''','''**6 Ekim 23:44 – 7 Ekim 00:45 — Mustafa'nın kararları: K-61 (*önce fazla
mesaisiz* ürünün varsayılanı; hakem ağırlıklardır) ve K-62 (veri seti
merdiveni, kadro); K-61 koda indi (bulut).** ⚠ *Bu bölümün "koddaki
karşılığı" ve "Mustafa'ya söylenen kur" paragrafları 7 Ekim'de yanlış çıktı
(O-18); geçerli hâl aşağıdaki **bulgu 23** bölümündedir.*
'''))
R.append(('''*Mustafa'ya söylenen kur.* Bugünkü ağırlıklarda 1 saat fazla mesai = 333
kişi-saat hedef eksiği (DENGELI), 150 (KAPSAMA); 500 kişilik en iyi planın
haftalık hedef eksiği 350 kişi-saat. Bu kurda fazla mesaili plan kazanamaz —
K-30'un ağırlığa yazılmış hâli. Fazla mesainin pazarlık edilebilir olması
istenirse bu bir ağırlık kararıdır; o ağırlıklarda kısayol kendiliğinden
devreden çıkar ve aramanın artığı yeniden ölçülmelidir.

**Sıradaki adım (7 Ekim 00:45; 23:15 adımının yerine):** Mustafa'nın
koşuları — motor testleri, gerçekçi set, tam mutasyon koşusu (damga 286
olmalı), DENETIM, commit + push → **doğrulama ölçümü** (`varsayilan`, 900 sn,
üç koşu: ürünün yolu bulgu 21'in ölçtüğüyle aynı mı — beklenen fazla mesai 0,
amaç 26,4–26,5 bin). Sonra K-62: merdiven kadrosu (iki işi yapabilen 30
satışçı — teyit bekliyor; gece back office asgari 2), seviye 1 ve 4 araç
olarak, referans planlar Mustafa'nın makinesinde, 500 kişide 900 sn ölçüm.
Sonra eski sıra: sonuç kartı için sınır adımı → atama cilası → T-80 → bulgu
11'in modeli araç olarak.
''','''*Mustafa'ya söylenen kur.* Bugünkü ağırlıklarda 1 saat fazla mesai = 333
kişi-saat hedef eksiği (DENGELI), 150 (KAPSAMA); 500 kişilik en iyi planın
haftalık hedef eksiği 350 kişi-saat. ~~Bu kurda fazla mesaili plan kazanamaz~~
*(yanlış — bulgu 23)* — K-30'un ağırlığa yazılmış hâli. Fazla mesainin
pazarlık edilebilir olması istenirse bu bir ağırlık kararıdır ~~; o
ağırlıklarda kısayol kendiliğinden devreden çıkar~~ ve aramanın artığı
yeniden ölçülmelidir.

**Sıradaki adım (7 Ekim 00:45; 23:15 adımının yerine — 03:30'da aşağıdaki
bulgu 23'ün adımıyla değişti):** Mustafa'nın koşuları — motor testleri,
gerçekçi set, tam mutasyon koşusu (damga 286 olmalı), DENETIM, commit + push →
**doğrulama ölçümü** (`varsayilan`, 900 sn, üç koşu: ürünün yolu bulgu 21'in
ölçtüğüyle aynı mı — beklenen fazla mesai 0, amaç 26,4–26,5 bin). Sonra K-62:
merdiven kadrosu (iki işi yapabilen 30 satışçı — teyit bekliyor; gece back
office asgari 2), seviye 1 ve 4 araç olarak, referans planlar Mustafa'nın
makinesinde, 500 kişide 900 sn ölçüm. Sonra eski sıra: sonuç kartı için sınır
adımı → atama cilası → T-80 → bulgu 11'in modeli araç olarak.

**7 Ekim 01:00–03:30 — bulgu 23: K-61'in 00:45 sürümü ilkeyi çiğniyordu;
düzeltildi (O-18). Mustafa 00:45 sürümünü hiç koşmadı.**

*Ne bulundu.* İşi görmemiş iki inceleme ajanı (kod kopyası, bulut) aynı
bulguyla döndü, ben de koştum: 00:45 sürümü fazla mesaisiz plan bulunca
fazla mesaiyi bütün aşamalarda 0'da tutuyordu ve "ağırlık koşulu" bunu
görmüyordu — **ürün ağırlıklarında** kanıtlı optimum fazla mesaili, dönen plan
daha kötü:

| Sahne (ürün ağırlıkları; tam model kanıtlı optimum ↔ 00:45 sürümü) | Optimum | 00:45 sürümü |
|---|---|---|
| Tek kişi, DENGELI, SAAT_DENGESI yumuşak; şablon netleri 7,5 sa × 5 + 7,75 sa = 45 sa 15 dk | **750** (15 dk fazla mesai) | 2.256 (0 fazla mesai; bir gün düşer, 7,25 sa sözleşme altı) |
| Aynı kişi, KAPSAMA, SAAT_DENGESI sert (fazla mesaisiz tek dolum talebin dışındaki 9 saatlik şablon) | **750** | 880 |
| 12 kişi, KAPSAMA; 12 × 15 dk = tam **3 saat** — Mustafa'nın örneğindeki miktar | **9.000** | 12.000 |
| İki ekibe üye tek kişi (K-50), DENGELI / KAPSAMA | **750** | 900 / 2.000 |
| Tek kişi ×400 (56.854 değişken, iki aşamalı yol) | **300.000** | 902.400 |

Sebep: fazla mesai çeyrek saatlik adımlarla gelir (15 dk = 750 puan) ve bir
adım bütün haftanın düzenini açabiliyor — bir gün daha çalışabilmek (9 hücre
+ 7,25 saat sözleşme altı = 2.256), talebin içindeki şablona geçebilmek, iki
ekibi birden kapatabilmek. Benim hesabım *"bir saat fazla mesai = en çok
bir-iki kişi-saat kazanç"* diyordu; bu yalnız tek şablonlu düz sahnelerde
doğru. Ajan A'nın rastgele avı: çeyrek saat ızgaralı karışık şablonlar +
yumuşak SAAT_DENGESI ile 8/400 karşı örnek; gerçekçi şablon netleriyle (7,5 /
9 / 4,25 sa; en küçük adım 90 dk) 0/1.200. 500 kişilik sette (en küçük
şablon taşmaları: satış ve back office 75 dk, müşteri hizmetleri 30 dk, 40
saatlik sezonluk kadro 15 dk) bu durumun oluştuğu **gösterilmedi**;
oluşmayacağı kanıtlı değil.

İncelemenin öteki bulguları: küçük model (tek arama) ile büyük model (sert
kesim) aynı girdide farklı karar veriyordu (yol bağımlı politika);
*"İyileştir"* yolu (başlangıç planı) kısayolu hiç görmüyor; koşul "daraltılacak
alan var mı" kontrolünden önce çalışıyordu (CALISAN + düşürülmüş ağırlıkta
yanlış atlama notu); `FAZLA_MESAI_TAVANI` yokken "bulundu" sayılan deneme
`mola_adimi: False` ile küresel kanıtı düşürüyordu; `int(ObjectiveValue())`
kırpıyordu (65154 ↔ alt sınır 65155); birinci aşama başarısız denemede iki
pay sürebiliyor (başlık "≤ %20" diyordu); testler yalnız 8 saatlik tek
şablonla yazılmıştı (en küçük adım 3 saat), SAAT_DENGESI / ADALET / MOLA /
çok ekipli üyelik yoktu; keşif OKU-BENI'de *"devreden adalet yükü hepsinde
0"* yanlıştı (üretici 500 kişinin 124'üne `devir_yuk` yazıyor; boş olan
geçen haftanın vardiyaları); K-61 metninde *"fazla mesai dışındaki kalemler de
iyileşti"* abartılıydı (toplam iyileşti, adalet ve hedef aşımı az kötüleşti),
*"%40 → %0,3"* yalnız DENGELI (KAPSAMA %26 → %0,6), *"10 yeni test"* 11'di,
O-15'e aykırı biçimde *"286 mutasyon hepsi öldü"* grupları saymadan
yazılmıştı.

*Düzeltme (03:30, bulut; Mustafa'nın koşuları bekleniyor).* Motor: fazla
mesaisiz plan bulununca alanlar **geri açılır**, o plan iyileştirmenin
ipucudur, iyileştirme ve mola adımı tam modelde tam ağırlıklı amaçla koşar —
ipucundan kötü plan dönemez, fazla mesai ancak ağırlıklara göre kazanıyorsa
girer. Ağırlık koşulu kaldırıldı. Sert kesim ölçüm seçeneği
(`fazla_mesai_sifirda_tut`, varsayılan kapalı); bulgu 21 o hâldir. Çıktı:
`uygulandi` kalktı, `sifirda_tutuldu` geldi; `_sinir_kapsami` yalnız sert
kesimde kısıtlı der; iyileştirme eğrisi çıktıya girdi
(`ilk_asama_iyilestirme.iyilesme`); amaç değeri yuvarlanıyor. Yukarıdaki dört
sahne test oldu: tam modelin kanıtlı optimumu = ürün yolunun puanı; sert
kesimin daha kötü döndürdüğü de test; Mustafa'nın örneğinde fazla mesaisiz
plan **bulunsa da** 3 saatlik plan seçiliyor. Bulutta 41 dosya **583 test**
geçti (`test_fazla_mesai_once_sifir.py` 27); mutasyon harnesi 285
(`fm_sifir` 43) — grup koşuları aşağıda; toplam iddiası tam koşudan sonra
(O-15). `kalite-olc.py`: `fm_once` / `fm_once_kapsama` (ürün yolu), `fm_sert`
/ `fm_sert_kapsama` (6 Ekim gecesinin hâli; bulgu 21'in kayıt adları buna
sabitlendi), kayıtta `sert_kesim`; `ipucu_kapali` ve `mola_adimi_tam`
açıklamaları düzeltildi. Şartname §6.7 yeniden yazıldı, §11.3, değişiklik 61;
K-61 ve K-30 kayıtlarında yanlış cümleler üstü çizili; O-18.

*Küçük ölçekli ön ölçüm (bulut, 2 çekirdek; ürün ölçümü DEĞİL).* 49 kişi,
20 sn, tek koşu: 6 Ekim öncesi 11.918 (3 sa fazla mesai) · sert kesim 2.758
(0) · **düzeltilmiş yol 2.713 (0)** — iyileştirme fazla mesaisiz plandan
başlayıp fazla mesaiye dönmedi (iyileştirme boyunca fazla mesai toplamı 0'da
kaldı). Üçer tekrar ve 151 kişi: aşağıda / oturum kaydında.

*Açık ürün sorusu (Mustafa'ya soruldu).* K-30'un ilk satırı (*"hedef için
fazla mesai yapılmaz"*, 16 Eylül) ile K-61'in ilkesi (*"ağırlıklara göre
oldukça daha optimum plan seçilir"*, 6 Ekim) birbirini tam örtmüyor: motor
K-61'e göre yazıldı, K-30'un ilk satırını olağan veride ağırlıklar sağlıyor,
15 dakikalık adımın haftayı açtığı yapılarda ağırlıklar fazla mesaili planı
seçiyor. K-30'un ilk satırı mutlak istenirse bu sert kesimdir.

**Sıradaki adım (7 Ekim 03:30; 00:45 adımının yerine):** Mustafa'nın
koşuları — motor testleri (583), gerçekçi set testleri, DENETIM, commit + push
→ **tam mutasyon koşusu** (damga 285 olmalı) → **bulgu 23'ün ölçümü**:
`fm_once,fm_once_kapsama`, 900 sn, üçer koşu (≈1,6 saat); karar kuralı K-61'de
yazılı (sert kesimin ±%2'si ve fazla mesai 0 → kapanır; fazla mesai > 0 →
ağırlıkların kararı, sebebi okunur; puan %5'ten kötü → arama artığı geri
geldi, yol yeniden). Sonra K-62 (merdiven kadrosu, seviye 1 ve 4 araç olarak,
referans planlar, 500 kişide 900 sn). Sonra eski sıra.
'''))
R.append(('''**6 Ekim 23:44 – 7 Ekim 00:45:** **K-61** — *önce fazla mesaisiz* ürünün varsayılanı, hakem ağırlıklardır (kısayol yalnız ağırlık koşulu tutarken uygulanır); koda indi, bulutta 582 test geçti ve 286 mutasyon grup koşularında öldü; **K-62** — merdiven ve kadro kararları. Kalan: Mustafa'nın koşuları (testler, tam mutasyon, commit) ve doğrulama ölçümü; merdivenin 1. ve 4. seviyesi (iki işi yapabilen satışçı sayısı teyit bekliyor); zorunlu fazla mesai tam ölçekte ölçülmedi; sonuç kartı için küresel sınır (sınır adımı ölçümü) |''',
'''**6 Ekim 23:44 – 7 Ekim 00:45:** **K-61** — *önce fazla mesaisiz* ürünün varsayılanı, hakem ağırlıklardır; **K-62** — merdiven ve kadro kararları. **7 Ekim 01:00–03:30, bulgu 23 / O-18:** 00:45 sürümü (bulunca fazla mesai 0'da tutuluyor + "ağırlık koşulu") bağımsız incelemede ürün ağırlıklarında ilkeyi çiğnedi (kanıtlı optimum 750 ↔ 2.256; 12 kişide 9.000 ↔ 12.000 — Mustafa'nın 3 saatlik örneği); düzeltildi: fazla mesaisiz plan yalnız başlangıç noktası, alanlar geri açılır, kararı ağırlıklar verir; sert kesim ölçüm seçeneği; dört karşı örnek test; bulutta 583 test, 285 mutasyon grup koşularında öldü. Kalan: Mustafa'nın koşuları (testler, DENETIM, commit, tam mutasyon) ve **düzeltilmiş yolun 500 kişilik ölçümü** (`fm_once`, 900 sn, üçer koşu); K-30 ilk satırı ↔ K-61 ilkesi sorusu Mustafa'da; merdivenin 1. ve 4. seviyesi (iki işi yapabilen satışçı sayısı teyit bekliyor); zorunlu fazla mesai tam ölçekte ölçülmedi; sonuç kartı için küresel sınır (sınır adımı ölçümü) |'''))
for old,new in R:
    assert s.count(old)==1, old[:90]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF