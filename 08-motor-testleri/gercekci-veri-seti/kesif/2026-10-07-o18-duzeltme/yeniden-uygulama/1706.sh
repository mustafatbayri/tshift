cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/00-DEVIR && python3 - <<'PYEOF'
import io
p="08-URUN-KARARLARI.md"
s=io.open(p,encoding="utf-8").read()
R=[]
# ---- K-61 basligi
R.append(('''## K-61 · Motor **önce fazla mesaisiz plan arar** (ürünün varsayılanı); **hakem ağırlıklardır** — arama bir kısayoldur, kural değil
''','''## K-61 · Motor **önce fazla mesaisiz plan arar** (ürünün varsayılanı); **hakem ağırlıklardır** — bulunan plan yalnız başlangıç noktasıdır *(uygulanışı 7 Ekim'de düzeltildi, O-18)*
'''))
# ---- "Ne demek -- iki parca" bolumu
R.append(('''1. **Varsayılan açıldı.** Motor geçerli planı önce fazla mesaisiz arar;
   bulursa fazla mesai bütün aşamalarda 0'da kalır, bulamazsa (kanıt ya da
   süre) önceki yol işler ve plana not düşer (K-30'un iki satırı; K-38'in
   zorunlu fazla mesai yolu kapanmaz). Yalnız iki aşamalı akışta (büyük
   model) devreye girer.
2. **Hakem ağırlıklardır.** Bu arama fazla mesaisiz plan varken fazla mesaili
   planlara **bakmaz** — yani bir kısayoldur. Mustafa'nın ilkesi, kısayolun
   yalnız *fazla mesainin ağırlıklara göre kazanamayacağı yerde* kullanılmasını
   gerektirir. Koda **koşul** olarak yazıldı: kısayol, fazla mesainin
   **dakika** başı ağırlığı öteki ağırlıkların en büyüğünden küçük olmadığı
   sürece uygulanır. Koşul tutmuyorsa kısayol uygulanmaz, çıktı sebebini
   söyler (`uygulandi: false, sebep: "agirlik"`), not düşer ve kararı ağırlıklı
   arama verir.
''','''1. **Varsayılan açıldı.** Motor geçerli planı önce fazla mesaisiz arar;
   ~~bulursa fazla mesai bütün aşamalarda 0'da kalır~~ **bulursa o plan
   iyileştirmenin başlangıç noktasıdır, fazla mesai alanları geri açılır
   (7 Ekim)**; bulamazsa (kanıt ya da süre) önceki yol işler ve plana not
   düşer (K-30'un iki satırı; K-38'in zorunlu fazla mesai yolu kapanmaz).
   Yalnız iki aşamalı akışta (büyük model) devreye girer.
2. **Hakem ağırlıklardır.** ~~Bu arama fazla mesaisiz plan varken fazla mesaili
   planlara **bakmaz** — yani bir kısayoldur. Mustafa'nın ilkesi, kısayolun
   yalnız *fazla mesainin ağırlıklara göre kazanamayacağı yerde* kullanılmasını
   gerektirir. Koda **koşul** olarak yazıldı: kısayol, fazla mesainin
   **dakika** başı ağırlığı öteki ağırlıkların en büyüğünden küçük olmadığı
   sürece uygulanır. Koşul tutmuyorsa kısayol uygulanmaz, çıktı sebebini
   söyler (`uygulandi: false, sebep: "agirlik"`), not düşer ve kararı ağırlıklı
   arama verir.~~ **7 Ekim (O-18):** bu paragraf yanlıştı — aşağıdaki
   düzeltme bölümüne bakın. Şimdi: hiçbir plan aramadan çıkarılmaz; fazla
   mesaisiz plan ipucudur, iyileştirme tam ağırlıklı amaçla o plandan başlar
   ve ipucundan kötü plan dönemez; fazla mesai ancak ağırlıklara göre
   kazanıyorsa plana girer. Ağırlık koşulu diye bir şey yok.
'''))
# ---- kur paragrafi: "Bu kurda ... olusmaz" (yanlis)
R.append(('''500 kişilik en iyi planın bütün hafta boyunca hedef eksiği 350 kişi-saat
(3.150 puan) — bir saat fazla mesainin cezası kadar. Bu kurda *"3 saat fazla
mesaili plan oldukça daha optimum"* durumu oluşmaz: 3 saat 9.000 puandır, o
planın fazla mesai dışındaki **bütün** puanı 26.400. Kur, K-30'un (*"hedef
hiç gitmemek"*) ağırlığa yazılmış hâlidir. **Mustafa fazla mesainin gerçekten
pazarlık edilebilir olmasını isterse** (örneğin 1 saat = 20 kişi-saat) bu bir
ağırlık kararıdır; koşul sayesinde kısayol o ağırlıklarda kendiliğinden
devreden çıkar — ama büyük modelde aramanın fazla mesai artığı (bulgu 20) o
ağırlıklarda yeniden ölçülmelidir.

**Koşulun sayısı bir kalibrasyondur.** *"Dakika ağırlığı ≥ en büyük öteki
ağırlık"*, bir saat fazla mesainin en pahalı öteki birimin en az 60 katı
olması demektir. Ölçülen yer ürün ağırlıklarıdır (oran 150 ve 333). Bir
saatlik fazla mesainin doğrudan kazandırabileceği birkaç birimdir (bir
kişi-saat varlık: hedef eksiği + mola kapsaması; iki ekibe üye kişide iki
ekip). 60 kat bir **kanıt değildir**; T-60 teşhis yapılandırmalarını
(fazla mesai 5 ve 1) dışarıda, makul kiracı düzenlemelerini (ağırlık 50'ye
kadar) içeride bırakır.
''','''500 kişilik en iyi planın bütün hafta boyunca hedef eksiği 350 kişi-saat
(3.150 puan) — bir saat fazla mesainin cezası kadar. ~~Bu kurda *"3 saat fazla
mesaili plan oldukça daha optimum"* durumu oluşmaz: 3 saat 9.000 puandır, o
planın fazla mesai dışındaki **bütün** puanı 26.400.~~ **Yanlış (7 Ekim,
O-18):** kur yalnız *"bir saat fazla mesai = bir kişi-saat kazanç"* için
geçerli; fazla mesai çeyrek saatlik adımlarla gelir ve küçük bir adım bütün
haftanın düzenini açabilir (bkz. düzeltme bölümü: 15 dakika = 750 puan, bir
gün daha çalışabilmek ya da sözleşme saatini doldurabilmek 2.000'in üstünde
kazandırıyor). 500 kişilik sette bu durumun oluştuğu **gösterilmedi**,
oluşmayacağı kanıtlı değil. Kur, K-30'un (*"hedef hiç gitmemek"*) ağırlığa
yazılmış hâlidir ve olağan veride K-30'un ilk satırını sağlar. **Mustafa fazla
mesainin gerçekten pazarlık edilebilir olmasını isterse** (örneğin 1 saat = 20
kişi-saat) bu bir ağırlık kararıdır — düzeltilmiş motor o ağırlıklarda da
aynı şekilde çalışır (arama hiçbir planı dışarıda bırakmaz); büyük modelde
aramanın fazla mesai artığı (bulgu 20) o ağırlıklarda yeniden ölçülmelidir.

~~**Koşulun sayısı bir kalibrasyondur.** *"Dakika ağırlığı ≥ en büyük öteki
ağırlık"*, bir saat fazla mesainin en pahalı öteki birimin en az 60 katı
olması demektir. Ölçülen yer ürün ağırlıklarıdır (oran 150 ve 333). Bir
saatlik fazla mesainin doğrudan kazandırabileceği birkaç birimdir (bir
kişi-saat varlık: hedef eksiği + mola kapsaması; iki ekibe üye kişide iki
ekip). 60 kat bir **kanıt değildir**; T-60 teşhis yapılandırmalarını
(fazla mesai 5 ve 1) dışarıda, makul kiracı düzenlemelerini (ağırlık 50'ye
kadar) içeride bırakır.~~ *(7 Ekim: koşul kaldırıldı; "60 kat" açıklaması da
yanlıştı — birimler farklı: fazla mesai dakika, ötekiler kişi-saat/birim.)*
'''))
# ---- ornek tablosu
R.append(('''| Ağırlıklar | Fazla mesaisiz plan | 3 saat fazla mesaili plan | Motorun seçtiği |
|---|---|---|---|
| Ürünün ağırlıkları (hedef 9) | **72** | 9.000 | fazla mesaisiz (kısayol uygulandı) |
| Hedef ağırlığı 2.000 | 16.000 | **9.000** | **3 saat fazla mesaili** (kısayol koşulu tutmadı, uygulanmadı) |

Aynı testte kısayol koşulsuz uygulanmaya zorlanınca motor 16.000'lik planı
döndürür — koşul olmasaydı ilke çiğnenirdi.
''','''| Ağırlıklar | Fazla mesaisiz plan | 3 saat fazla mesaili plan | Motorun seçtiği |
|---|---|---|---|
| Ürünün ağırlıkları (hedef 9) | **72** | 9.000 | fazla mesaisiz (ağırlıklar öyle diyor) |
| Hedef ağırlığı 2.000 | 16.000 | **9.000** | **3 saat fazla mesaili** — fazla mesaisiz plan **bulunduğu hâlde** (ipucu), ağırlıklar onu seçti *(7 Ekim)* |

~~Aynı testte kısayol koşulsuz uygulanmaya zorlanınca motor 16.000'lik planı
döndürür — koşul olmasaydı ilke çiğnenirdi.~~ *(7 Ekim: aynı testte sert
kesim — 6 Ekim gecesinin hâli — 16.000'lik planı döndürür; bu artık yalnız
ölçüm seçeneğidir.)*
'''))
# ---- bilinen sinirlar 1
R.append(('''1. Ürün ağırlıklarında fazla mesaili bir planın daha iyi **olamayacağı**
   hesapla gösterildi, her veri için kanıtlanmadı. Küçük sahnelerde kısayolun
   planı tam modelin kanıtlı optimumuyla aynı puanda (test). 500 kişide
   küresel optimumu 15 dakikada hiçbir yol kanıtlayamıyor; merdivenin
   referans planları (K-62) bunu izleyecek.
''','''1. ~~Ürün ağırlıklarında fazla mesaili bir planın daha iyi **olamayacağı**
   hesapla gösterildi, her veri için kanıtlanmadı. Küçük sahnelerde kısayolun
   planı tam modelin kanıtlı optimumuyla aynı puanda (test).~~ **Yanlıştı
   (O-18):** ürün ağırlıklarında fazla mesaili planın daha iyi olduğu sahneler
   var ve 6 Ekim gecesinin kodu orada daha kötü planı döndürüyordu. Düzeltilmiş
   yol o sahnelerde kanıtlı optimumu veriyor (test). 500 kişide küresel
   optimumu 15 dakikada hiçbir yol kanıtlayamıyor; merdivenin referans planları
   (K-62) bunu izleyecek.
'''))
# ---- durum paragrafi
old=s[s.index("**Durum (7 Ekim 00:45): koda indi (bulut); Mustafa'nın koşuları bekleniyor.**"):s.index("→ K-30 · K-38 · K-62 · T-60 bulgu 20–22 · şartname §6.7, §11.3 ·")]
new='''~~**Durum (7 Ekim 00:45): koda indi (bulut); Mustafa'nın koşuları bekleniyor.**~~
*(7 Ekim 00:45 sürümü: `_fazla_mesai_kisayolu_gecerli` koşulu, çıktıda
`uygulandi`, 26 test, 44 mutasyon — hepsi aşağıdaki düzeltmeyle değişti;
Mustafa o sürümü hiç koşmadı.)*

### ⚠ 7 Ekim 01:00–03:30 — uygulanış yanlıştı, düzeltildi (O-18)

Bağımsız inceleme (iki ajan, kodu görmeden) 00:45 sürümünün Mustafa'nın
ilkesini **ürün ağırlıklarında** çiğnediğini gösterdi; kendi koşumla
doğruladım. Sert kesim (bulunca 0'da tut) fazla mesaili planları aramadan
çıkarıyordu; *"ağırlık koşulu"* bunu görmüyordu, çünkü hesabı *"bir saat fazla
mesai = en çok bir-iki kişi-saat kazanç"* varsayıyordu. Oysa fazla mesai
çeyrek saatlik adımlarla gelir ve bir adım bütün haftayı açabilir:

| Sahne (ürün ağırlıkları) | Kanıtlı optimum | Sert kesim |
|---|---|---|
| Tek kişi, DENGELI, SAAT_DENGESI yumuşak; 7,5 sa × 5 + 7,75 sa = 45 sa 15 dk | **750** (15 dk fazla mesai) | 2.256 |
| Tek kişi, KAPSAMA, SAAT_DENGESI sert | **750** | 880 |
| 12 kişi, KAPSAMA — tam **3 saat** (Mustafa'nın örneği) | **9.000** | 12.000 |
| İki ekibe üye tek kişi (K-50), DENGELI / KAPSAMA | **750** | 900 / 2.000 |

**Düzeltilmiş davranış:** fazla mesaisiz plan bulununca fazla mesai alanları
**geri açılır**; o plan iyileştirmenin ipucudur; iyileştirme ve mola adımı tam
modelde, tam ağırlıklı amaçla koşar. Fazla mesai ancak ağırlıklara göre
kazanıyorsa plana girer; ipucundan kötü plan dönemez. Bulunamazsa yol aynen
(alanlar açılır, yeniden arama, not). Sert kesim **ölçüm** seçeneği olarak
kaldı: `fazla_mesai_sifirda_tut` (varsayılan kapalı) — bulgu 21 o hâldir.

**Mustafa'ya söylenen ve düzeltilen cümleler:** *"bu kurda 3 saat fazla mesaili
plan oldukça daha optimum durumu oluşmaz"* (yanlış), *"hesapla gösterildi"*
(yanlış), *"en az 60 katı"* (birimler farklı, anlamsız), *"küçük sahnelerde
aynı puanda (test)"* (tek sahneyle).

**Ölçüm durumu.** Sert kesimin tam ölçekli ölçümü var (bulgu 21). Düzeltilmiş
yol tam ölçekte **henüz ölçülmedi**: küçük ölçekte (49 kişi, bulut, 20 sn)
iyileştirme fazla mesaisiz plandan başlayıp fazla mesaiye dönmedi (puan 2.713;
sert kesim 2.758; 6 Ekim öncesi 11.918). 500 kişi, 900 sn, DENGELI + KAPSAMA,
üçer koşu Mustafa'nın makinesinde — T-60 bulgu 23'e yazılacak. **Karar
kuralı (koşudan önce):** düzeltilmiş yolun puanı sert kesimin ±%2'si içinde ve
fazla mesai 0 ise iş kapanır; fazla mesai sıfırdan ayrılıyorsa bu ağırlıkların
kararıdır (ilke gereği doğru) ama sebebi okunur ve Mustafa'ya gösterilir;
puan sert kesimden %5'ten fazla kötüyse arama artığı geri gelmiş demektir ve
yol yeniden ele alınır.

**Açık ürün sorusu (Mustafa'ya soruldu, 7 Ekim).** K-30'un ilk satırı
(*"yalnız hedef için fazla mesai yapılmaz"*, 16 Eylül) artık **sert bir kural
değil, ağırlıkların sonucudur**: olağan veride (bir saatlik fazla mesai en çok
bir-iki kişi-saat kazandırırken) ağırlıklar bunu sağlar; 15 dakikalık bir
adımın bütün haftayı açtığı yapılarda ağırlıklar fazla mesaili planı seçer —
bu da 6 Ekim ilkesinin söylediğidir. İki karar birbirini tam örtmüyor; motor
6 Ekim ilkesine göre yazıldı. Mustafa K-30'un ilk satırını mutlak isterse bu
sert kesimdir ve 6 Ekim ilkesiyle çelişir; o zaman karar yeniden yazılır.

**Durum (7 Ekim 03:30): koda indi (bulut), Mustafa'nın koşuları bekleniyor.**
`09-motor/cozucu/coz.py`: `VARSAYILAN["fazla_mesai_once_sifir"]` True,
`VARSAYILAN["fazla_mesai_sifirda_tut"]` False (ölçüm); `_ipucu_ver` bulunca
alanları geri açar; `_fazla_mesai_kisayolu_gecerli` **kaldırıldı**; çıktıda
`uygulandi` kalktı, `sifirda_tutuldu` geldi; `_sinir_kapsami` yalnız sert
kesimde *"fazla_mesaisiz"*; iyileştirme eğrisi (`ilk_asama_iyilestirme.
iyilesme`); amaç değeri yuvarlanır (kırpılmıyor). Testler:
`09-motor/testler/test_fazla_mesai_once_sifir.py` 27 (dört karşı örnek sahnesi,
Mustafa'nın örneği bulunsa-da-seçilir, sert kesim ölçüm, eğri, yuvarlama);
`test_demir_secenekleri.py` sınır kapsamı. Mutasyon `fm_sifir` 43, harnes
toplamı 285 — bulutta grup koşularında hepsi öldü (`fm_sifir`, `demir`,
`ilk_asama`, `kalite`); **toplam iddiası Mustafa'nın tam koşusundan sonra**
(O-15). Bulutta 41 dosya 583 test geçti. `kalite-olc.py`: `fm_once` /
`fm_once_kapsama` (ürün yolu), `fm_sert` / `fm_sert_kapsama` (6 Ekim'in hâli);
bulgu 21'in kayıt adları sert kesime sabitlendi; kayıtta `sert_kesim` alanı.
Şartname §6.7 (yeniden yazıldı), §11.3, değişiklik 61.

'''
R.append((old,new))
R.append(('''→ K-30 · K-38 · K-62 · T-60 bulgu 20–22 · şartname §6.7, §11.3 ·
`09-motor/cozucu/coz.py` (`_ipucu_ver`, `_fazla_mesai_kisayolu_gecerli`) ·
`09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/mutasyon_kostur.py`
(`fm_sifir`) · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py`
''','''→ K-30 · K-38 · K-62 · O-18 · T-60 bulgu 20–23 · şartname §6.7, §11.3 ·
`09-motor/cozucu/coz.py` (`_ipucu_ver`, `_fazla_mesaiyi_sifirla`, `_sinir_kapsami`) ·
`09-motor/testler/test_fazla_mesai_once_sifir.py` · `09-motor/mutasyon_kostur.py`
(`fm_sifir`) · `08-motor-testleri/gercekci-veri-seti/kalite-olc.py`
'''))
# ---- K-30 notu
R.append(('''**6 Ekim 23:44 — karar verildi: K-61.** Mustafa: *"Evet, ama sadece basit
bir evet değil…"* — seçenek ürünün varsayılanı oldu ve bir **koşula** bağlandı:
hakem ağırlıklardır, arama yalnız fazla mesainin kazanamayacağı ağırlıklarda
uygulanır. Bu kararın tablosu (yukarıda) ve 50 kalibrasyonu değişmedi; kur
(1 saat fazla mesai = 333 kişi-saat hedef eksiği, DENGELI) K-61'de yazılı ve
Mustafa'ya söylendi.
''','''**6 Ekim 23:44 — karar verildi: K-61.** Mustafa: *"Evet, ama sadece basit
bir evet değil…"* — seçenek ürünün varsayılanı oldu ~~ve bir **koşula** bağlandı:
hakem ağırlıklardır, arama yalnız fazla mesainin kazanamayacağı ağırlıklarda
uygulanır~~. Bu kararın tablosu (yukarıda) ve 50 kalibrasyonu değişmedi; kur
(1 saat fazla mesai = 333 kişi-saat hedef eksiği, DENGELI) K-61'de yazılı ve
Mustafa'ya söylendi.

**7 Ekim — düzeltme (O-18).** *"Koşul"* yanlıştı ve kaldırıldı: fazla
mesaisiz plan bulununca fazla mesai 0'da **tutulmuyor**, o plan yalnız
başlangıç noktası; kararı ağırlıklar veriyor. Bunun bu karara etkisi: **ilk
satır (*"hedef için fazla mesai yapılmaz"*) artık sert bir kural değil,
ağırlıkların sonucudur.** Olağan veride (bir saatlik fazla mesai en çok
bir-iki kişi-saat kazandırırken) ağırlıklar satırı sağlar; 15 dakikalık bir
fazla mesai adımının bir haftalık düzeni açtığı yapılarda (şablon netleri
sözleşmeyi tam döşemiyor, SAAT_DENGESI, iki ekibe üyelik) ağırlıklar fazla
mesaili planı seçer — K-61'in ilkesi bunu söylüyor. **Bu karar ile K-61
birbirini tam örtmüyor; motor K-61'e göre yazıldı, soru Mustafa'ya soruldu**
(K-61'deki "açık ürün sorusu").
'''))
for old,new in R:
    assert s.count(old)==1, old[:90]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF