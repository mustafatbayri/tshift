cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo && python3 - <<'PYEOF'
import io
p="02-spec/v1.4-master-spec.md"
s=io.open(p,encoding="utf-8").read()
R=[]
# --- degisiklik listesi: satir 60 duzeltme notu + satir 61
old='''| 60 | **Motor önce fazla mesaisiz plan arar** — ürünün varsayılanı. Bulursa fazla mesai bütün aşamalarda 0'da kalır; bulamazsa önceki yol işler ve not düşer. **Hakem ağırlıklardır:** arama bir kısayoldur, yalnız fazla mesainin dakika başı ağırlığı öteki ağırlıkların en büyüğünden küçük değilken uygulanır; ağırlıklar fazla mesaili planı daha iyi kılıyorsa o seçilir. Tam ölçekte ölçüldü: altı koşunun altısında fazla mesai 0, plan puanı 3–5 kat iyi. Fazla mesainin zorunlu olduğu veri tam ölçekte ölçülmedi *(6 Ekim)* | §6.7, §11.3 | K-61, K-30, T-60 bulgu 20–22 |
'''
new='''| 60 | **Motor önce fazla mesaisiz plan arar** — ürünün varsayılanı. ~~Bulursa fazla mesai bütün aşamalarda 0'da kalır~~; bulamazsa önceki yol işler ve not düşer. **Hakem ağırlıklardır.** ~~Arama bir kısayoldur, yalnız fazla mesainin dakika başı ağırlığı öteki ağırlıkların en büyüğünden küçük değilken uygulanır~~ Tam ölçekte ölçüldü (sert kesimle): altı koşunun altısında fazla mesai 0, plan puanı 3–5 kat iyi. Fazla mesainin zorunlu olduğu veri tam ölçekte ölçülmedi *(6 Ekim)*. **Üstü çizili kısımlar 7 Ekim'de düzeltildi → 61** | §6.7, §11.3 | K-61, K-30, T-60 bulgu 20–22 |
| 61 | **Önce fazla mesaisiz aramanın uygulanışı düzeltildi (O-18)** — 6 Ekim gecesinin hâli, fazla mesaisiz plan bulununca fazla mesaiyi bütün aşamalarda 0'da tutuyor ve bunu bir "ağırlık koşulu"yla koruyordu; bağımsız inceleme ürün ağırlıklarında bunun ilkeyi çiğnediğini gösterdi (15 dakikalık fazla mesai adımı bir haftalık düzenin kilidini açıyor: kanıtlı optimum 750 iken 2.256; 12 kişide 9.000'e karşı 12.000). Şimdi: bulunan fazla mesaisiz plan yalnız **başlangıç noktasıdır**; fazla mesai alanları geri açılır, iyileştirme tam ağırlıklı amaçla o plandan başlar, kararı ağırlıklar verir. Sert kesim ölçüm seçeneği olarak kaldı (`fazla_mesai_sifirda_tut`). Düzeltilmiş yolun 500 kişilik ölçümü **bekleniyor** *(7 Ekim)* | §6.7, §11.3 | K-61, O-18, T-60 bulgu 23 |
'''
R.append((old,new))
# --- 6.7 alt bolum
a=s.index("### Motor önce fazla mesaisiz plan arar 🆕 *(K-61, 6 Ekim)*")
b=s.index("## 6.8 Tercihler")
yeni='''### Motor önce fazla mesaisiz plan arar 🆕 *(K-61, 6 Ekim; uygulanışı 7 Ekim'de düzeltildi — O-18)*

K-30'un ilk satırı (*"yalnız hedef kapsama iyileşecekse fazla mesai
yapılmaz"*) ağırlıkla söyleniyordu; tam ölçekte ağırlık tek başına yetmedi.
Ölçüldü (500 kişi, 900 sn, üçer koşu): veride fazla mesaiye **gerek olmadığı
hâlde** plan 26–40 saat fazla mesai içeriyordu ve plan puanının %74–82'si bu
cezaydı (T-60 bulgu 20). Sebep veri değil, aramanın artığıydı: yumuşak ceza
süre içinde fazla mesaiyi sıfıra itemiyor, sert sınır 13–33 saniyede
sıfırlıyor.

**Davranış (7 Ekim).** Motor geçerli planı önce **fazla mesaisiz** arar
(fazla mesai değişkenleri 0'a sabitken). Bulduğu plan **başlangıç noktasıdır**,
sınır değil.

| Durum | Ne olur |
|---|---|
| Fazla mesaisiz plan **bulundu** | O plan iyileştirmenin ipucu olur; fazla mesai alanları **geri açılır**, iyileştirme ve mola adımı **tam modelde**, tam ağırlıklı amaçla o plandan başlar. Fazla mesai ancak ağırlıklara göre **kazanıyorsa** plana girer |
| Fazla mesaisiz plan **yok** (kanıtlandı) | Fazla mesai serbest bırakılır, önceki yol işler; `uygulanmayan_notlar`a *"fazla mesaisiz plan yok"* düşer. Not *"en aza indirilir"* **demez**: ağırlıklı arama azaltmaya çalışır, en azı olduğu kanıtlı değildir |
| Bu sürede **bulunamadı** | Aynı; not *"bu sürede bulunamadı"* der — dönen plan fazla mesaili olabilir ve fazla mesaisizi var olabilir |

**Hakem ağırlıklardır.** Mustafa (6 Ekim): *"…elimizdeki tüm kriterleri
karşılayan en iyi plan fazla mesaisiz olmalı. Ama matematiksel olarak
kurduğumuz modelde ağırlıklar baz alındığında örneğin 3 saat fazla mesai
içeren en optimum plan var ve fazla mesaisiz plandan oldukça daha optimum bir
plan ise en optimum olanı seçmeliyiz."* Bunu sağlayan, aramanın hiçbir planı
baştan dışarıda bırakmamasıdır: fazla mesaisiz plan yalnız iyi bir başlangıç
noktasıdır; sonrası tam ağırlıklı aramadır ve ipucundan kötü plan dönemez.
K-30'un ilk satırını ağırlıklar sağlar: bir saat fazla mesai 3.000 puan;
hedefin bir kişi-saat altında kalmak 9 / 20 / 5 puan (DENGELI / KAPSAMA /
CALISAN). Bir saatlik fazla mesai **tek başına** en çok bir-iki kişi-saat
kapsama kazandırdığından olağan veride hedef için fazla mesai yapılmaz.

> ⚠ **6 Ekim gecesinin hâli yanlıştı (O-18).** O hâlde fazla mesaisiz plan
> bulununca fazla mesai **bütün aşamalarda 0'da tutuluyordu** (sert kesim) ve
> bunu bir "ağırlık koşulu" (*fazla mesainin dakika başı ağırlığı ≥ en büyük
> öteki ağırlık*) koruyordu; *"ürün ağırlıklarında fazla mesaili bir planın
> daha iyi olamayacağı hesapla gösterildi"* deniyordu. Bağımsız inceleme (7
> Ekim, iki ajan) ürün ağırlıklarında karşı örnekler buldu: **15 dakikalık
> bir fazla mesai adımı bir haftalık düzenin kilidini açabiliyor** — şablon
> net saatleri sözleşme saatini tam döşemiyorsa (7,5 × 5 + 7,75 = 45 sa 15 dk)
> fazla mesaisiz tek seçenek bir günü düşürmektir (7,25 saat sözleşme altı,
> SAAT_DENGESI yumuşakken 2.175 puan) ya da talebin dışındaki bir şablondur.
> Kanıtlı optimum 750 iken sert kesim 2.256 (DENGELI, tek kişi), 880
> (KAPSAMA, SAAT_DENGESI sert); 12 kişide 9.000'e karşı 12.000 — tam 3 saat,
> Mustafa'nın örneği; iki ekibe üye kişide (K-50) 750'ye karşı 900 / 2.000.
> 500 kişilik veri setinde bu durumun oluştuğu **gösterilmedi** (en küçük
> şablon taşmaları 15–75 dk), oluşmayacağı da kanıtlı değil. Sert kesim ölçüm
> seçeneği olarak kaldı: `fazla_mesai_sifirda_tut` (varsayılan kapalı).
> Testler: `09-motor/testler/test_fazla_mesai_once_sifir.py` bölüm 5.

**Ölçülen.** Sert kesimle (6 Ekim, T-60 bulgu 21; aynı veri, aynı süre, üçer
koşu): altı koşunun altısında fazla mesai **0**; plan puanı DENGELI'de
106–148 bin → 26,4–26,5 bin, KAPSAMA'da 46–58 bin → 13,8–13,9 bin (toplam
iyileşti; adalet ve hedef aşımı çok az kötüleşti); koşudan koşuya fark DENGELI
%40 → %0,3, KAPSAMA %26 → %0,6. **Düzeltilmiş yol (alanlar açık) tam ölçekte
henüz ölçülmedi**; küçük ölçekte (49 kişi, bulut, tek koşu) iyileştirme fazla
mesaisiz plandan başlayıp fazla mesaiye dönmedi ve puan sert kesimle aynı
düzeyde kaldı. Ölçüm yapılandırmaları: `fm_once` / `fm_once_kapsama` (ürün
yolu), `fm_sert` / `fm_sert_kapsama` (6 Ekim'in hâli), `fm_once_kapali` (6
Ekim öncesi).

> ⚠ **Bilinen sınırlar.** (1) Fazla mesainin **zorunlu** olduğu veride
> (K-30'un ikinci satırı) bu arama bir şey kazandırmaz; orada önceki yolun
> artığı durur ve tam ölçekte **ölçülmedi** (keşif, 151 kişi, tek koşu: en az
> 3,5 saat zorunluyken 9,75–11,25 saat yazıldı — T-60 bulgu 22). Veri seti
> merdiveninin 4. seviyesi bunu ölçecek (K-62). (2) Yalnız iki aşamalı akışta
> (büyük model) devreye girer; eşiğin altındaki modelde çözücü tam modeli tek
> aramayla çözer ve aynı kararı ağırlıklarla verir. Başlangıç planı verilen
> koşu (*"İyileştir"*, K-54) fazla mesaili bir plandan başlıyorsa fazla
> mesaiyi azaltmak aramaya kalır — ölçülmedi. (3) Aşamalı yol tam modelin
> kanıtlı optimumuna fazla mesaiden bağımsız sebeplerle de uzak kalabilir:
> iyileştirme molalar sabitken koşar (K-60), mola adımı atamaları
> değiştirmez. (4) Başarısız denemede birinci aşama en kötü hâlde iki pay
> sürer (deneme + yeniden arama, her biri ≤ %20); denemenin süresi
> iyileştirmeden düşer, mola adımına kalan süre korunur.

Çıktı: `cozum_istatistikleri.fazla_mesai_once_sifir` (§11.3). Ayarlar:
`fazla_mesai_once_sifir` (varsayılan **açık**; `false` = 6 Ekim öncesinin
yolu, ölçüm ve kıyas için), `fazla_mesai_sifirda_tut` (varsayılan **kapalı**;
`true` = sert kesim, yalnız ölçüm). Testler:
`09-motor/testler/test_fazla_mesai_once_sifir.py`.

'''
s=s[:a]+yeni+s[b:]
# --- 11.3 satirlari
R.append(('''*önce fazla mesaisiz* arama (K-61) plan bulduysa ve ana aşama ortak aramaysa (ölçüm birleşimi: `mola_adimi: false`) `fazla_mesaisiz_optimum` / `fazla_mesaisiz_hedef_bosluk`. Kanıt iddia etmeyen sebepler (`durgunluk`, `butce_doldu`) aynen kalır |''',
'''*önce fazla mesaisiz* arama **sert kesimle** (ölçüm: `fazla_mesai_sifirda_tut: true`) plan bulduysa ve ana aşama ortak aramaysa (`mola_adimi: false`) `fazla_mesaisiz_optimum` / `fazla_mesaisiz_hedef_bosluk` — ürün yolunda bulunan plan ipucudur, alanlar geri açılır, model tamdır *(7 Ekim, O-18)*. Kanıt iddia etmeyen sebepler (`durgunluk`, `butce_doldu`) aynen kalır |'''))
R.append(('''İki kısıtlı hâl: mola adımı koştu (`atamalar_sabit: true`); *önce fazla mesaisiz* plan buldu ve fazla mesai değişkenleri 0'da kaldı. Plan yoksa da null |''',
'''İki kısıtlı hâl: mola adımı koştu (`atamalar_sabit: true`); *önce fazla mesaisiz* plan buldu ve fazla mesai değişkenleri 0'da **tutuldu** (yalnız ölçüm seçeneği `fazla_mesai_sifirda_tut`; `fazla_mesai_once_sifir.sifirda_tutuldu: true`). Plan yoksa da null |'''))
R.append(('''> | `fazla_mesaisiz_alt_sinir` | Yalnız ölçüm birleşiminde dolu (*önce fazla mesaisiz* plan buldu **ve** ana aşama ortak arama, `mola_adimi: false`; ürünün yolunda ana aşama mola adımıdır ve sınır `mola_adimi_alt_sinir`e gider): *fazla mesaisiz planların* hiçbiri bundan iyi olamaz. Tam modelin sınırı değildir |''',
'''> | `fazla_mesaisiz_alt_sinir` | Yalnız ölçüm birleşiminde dolu (sert kesim `fazla_mesai_sifirda_tut: true` ile *önce fazla mesaisiz* plan buldu **ve** ana aşama ortak arama, `mola_adimi: false`; ürünün yolunda alanlar geri açılır ve ana aşama mola adımıdır, sınır `mola_adimi_alt_sinir`e gider): *fazla mesaisiz planların* hiçbiri bundan iyi olamaz. Tam modelin sınırı değildir |'''))
old=s[s.index("> | `fazla_mesai_once_sifir` | *Önce fazla mesaisiz* aramanın sonucu"):]
old=old[:old.index("\n")+1]
new='''> | `fazla_mesai_once_sifir` | *Önce fazla mesaisiz* aramanın sonucu (**K-61, 6 Ekim: ürünün varsayılanı; uygulanışı 7 Ekim'de düzeltildi, O-18**; ayar `fazla_mesai_once_sifir`, varsayılan **açık**, `false` = 6 Ekim öncesinin yolu; §6.7). **null** = deneme yapılmadı: ayar kapalı, iki aşama devreye girmedi (küçük model, başlangıç planı) ya da daraltılacak fazla mesai değişkeni yok (CALISAN profili, yarı zamanlı kadro). **`{bulundu, degisken, saniye, kanitlandi_yok, molalar_sabit, sifirda_tutuldu}`** = denendi: birinci aşama geçerli planı fazla mesai değişkenleri 0'a sabitken aradı. **`bulundu: true`** → o plan iyileştirmenin ipucudur, alanlar geri açılır, kararı ağırlıklar verir (`sifirda_tutuldu: false`); yalnız ölçüm seçeneği `fazla_mesai_sifirda_tut: true` ile fazla mesai bütün aşamalarda 0'da tutulur (`sifirda_tutuldu: true`, çözülen model tam model değildir, küresel sınır yazılmaz). **`bulundu: false`** → alanlar geri açılır, fazla mesai serbestken yeniden aranır ve not düşer (`kanitlandi_yok: true` = fazla mesaisiz plan olmadığı kanıtlandı — kanıt aranan modelindir: `molalar_sabit: true` ise molalar şablonun ideal yerindeyken; `false` = süre yetmedi); başarısız denemenin süresi iyileştirmenin süresinden düşer, mola adımına kalan süre korunur. 6 Ekim 22:45 – 7 Ekim 00:45 arasındaki sürüm `uygulandi` alanı taşıyordu; kaldırıldı |
'''
R.append((old,new))
R.append(('''| Tarih | 16 Eylül 2026 · son ek 6 Ekim 2026 |''','''| Tarih | 16 Eylül 2026 · son ek 7 Ekim 2026 |'''))
R.append(('''**Doküman sonu · TShift Master Spec v1.4 · 16 Eylül 2026 · son ek 2 Ekim 2026**''','''**Doküman sonu · TShift Master Spec v1.4 · 16 Eylül 2026 · son ek 7 Ekim 2026**'''))
for old,new in R:
    assert s.count(old)==1, old[:90]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
grep -n "ilk_asama_iyilestirme" 02-spec/v1.4-master-spec.md | head -3