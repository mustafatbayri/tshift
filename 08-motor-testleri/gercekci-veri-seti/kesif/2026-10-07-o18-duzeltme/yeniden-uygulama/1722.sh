cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/00-DEVIR && python3 - <<'PYEOF'
import io
p="00-BURADAN-BASLA.md"
s=io.open(p,encoding="utf-8").read()
R=[]
old=s[s.index("**Son güncelleme:** 2026-10-07 00:45 ("):]
old=old[:old.index("\n")+1]
new='''**Son güncelleme:** 2026-10-07 03:30 (**⚠ 7 Ekim 03:30** paragrafı: **O-18 / T-60 bulgu 23** — K-61'in 00:45 sürümü bağımsız incelemede ilkeyi çiğnedi (fazla mesaisiz plan bulunca fazla mesaili planlara bakmıyordu; *"bu kurda oluşmaz"* demiştim, ürün ağırlıklarında karşı örnek var); **düzeltildi:** fazla mesaisiz plan yalnız başlangıç noktası, kararı ağırlıklar verir; bulutta 583 test; **Mustafa'nın koşuları ve 500 kişilik ölçüm bekliyor**; K-30 ilk satırı ↔ K-61 ilkesi sorusu Mustafa'da) · önceki 00:45 (**⚠ 7 Ekim 00:45** paragrafı — *"koda indi"* dediği sürüm yanlıştı, Mustafa onu hiç koşmadı: **K-61** — *önce fazla mesaisiz* ürünün varsayılanı, hakem ağırlıklardır; **K-62** — veri seti merdiveni ve kadro kararları) · önceki 2026-10-06 23:15 (**⚠ 6 Ekim 23:15** paragrafı: Mustafa merdiven yapısını ve sabit kriter setini onayladı; **O-17** — iki işi yapabilen eleman ve *"%95"*in kıtlığı 500 kişilik sette yok; **dört karar Mustafa'da**) · önceki 22:50 (**⚠ 6 Ekim 22:45** paragrafı: Mustafa amacı hatırlattı — *tüm kriterlere bağlı optimum plan, fazla mesai tek kriter* — ve veri seti merdiveni önerdi; küçük ölçekli ön deneme, **bulgu 22**; **tasarım kararı Mustafa'da**) · önceki 21:20 (**⚠ 6 Ekim 21:15** paragrafı: *önce fazla mesaisiz* ölçüldü — altı koşuda fazla mesai 0, amaç 4–5,6 kat düştü, karar kuralı tuttu; **ürün varsayılanı kararı Mustafa'da**) · önceki 19:25 (19:21: Mustafa'nın makinesinde 572 test, 271 mutasyon hepsi öldü; **⚠ 6 Ekim** başlıklı paragraf, `⚠ 4 Ekim 14:30` paragrafının hemen altında: üç profil 900 sn ölçüldü — **bulgu 20:** fazla mesai aramanın artığı, CALISAN'ın fazla mesaisiz planı DENGELI ağırlıklarıyla 4–5,6 kat iyi; **O-16:** çıktıdaki *"optimum · %0"* yanlıştı, düzeltildi; ölçüm seçeneği `fazla_mesai_once_sifir`; sırada onun 900 sn ölçümü) · önceki 5 Ekim 21:45 (`⚠ 4 Ekim 14:30` paragrafının sonu: K-60 Mustafa'nın makinesinde yeşil — 551 test, 228 mutasyon; **bulgu 19:** pay %80 ↔ %90 fark yok, %80 kaldı; sırada üç profil 900 sn) · önceki 4 Ekim 14:30 · önceki 2 Ekim 23:45 · önceki 23:25 (en alttaki iki paragraf; (a) tam ölçekte ölçüldü: fazla mesai 475–511 → 60–100 saat, (b) ve (c) elendi) · önceki 21:05 (yeni pencere — en alttaki paragraf: şartname düzeltmeleri, T-60 açığın yeri, ölçüm seçenekleri (a)/(b) yazıldı, (c) ölçüldü: ipuçsuz 900 sn beş koşunun dördünde plan yok) · önceki 18:50 (pencere devrediliyor: commit `8b53fe2` push edildi ve CI yeşil; tam ölçek kalite koşusu bitti ve yorumlandı — T-60 bulgu 7–9; sırada üç seçeneğin ölçümü, YENİ pencerede) · 2 Ekim: **K-57** "fazla mesai" tek tanım (yasal), T-60 kalite ölçüm araçları yazıldı ve 0.1 ölçekte ölçüldü (amacın %90'ı fazla mesai, oynama iki kat, ağırlık deneyi: sebep ağırlık değil). 1 Ekim'de **on 🔴 kapandı:** T-18, T-21, T-29, T-38, T-54, T-63, T-66, T-67, T-78, T-79; kararlar **K-48…K-57** (`08-URUN-KARARLARI.md`, hepsi açıklamalı). Motor **531 birim test** + 12 altın senaryo + bekçi 21 + taban 7 + **201 mutasyon hepsi öldü** (Mustafa'nın makinesinde de yeşil); `DENETIM.py` **0 hata**. Tam ölçek (500 kişi, %95): 0 sert, yayınlanabilir. **Açık 🔴 tek: T-60** (tam ölçekte tekrarlı kalite ölçümü koşuyor). Aşağıdaki *"⚠ … en güncel durum budur"* paragrafları kronolojik; **en alttaki en yeni**.
'''
R.append((old,new))
R.append(('''**⚠ 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* ürünün varsayılanı; hakem
ağırlıklardır) koda indi, Mustafa'nın koşuları bekliyor; K-62 (veri seti
merdiveni ve kadro) karara bağlandı; en güncel durum budur.** Mustafa (6 Ekim
''','''**⚠ 7 Ekim 00:45 — K-61 (*önce fazla mesaisiz* ürünün varsayılanı; hakem
ağırlıklardır) koda indi, Mustafa'nın koşuları bekliyor; K-62 (veri seti
merdiveni ve kadro) karara bağlandı; ~~en güncel durum budur~~ (03:30'da
aşağıdaki paragrafla değişti: bu paragrafın *"koda indi"* dediği sürüm
ilkeyi çiğniyordu, O-18).** Mustafa (6 Ekim
'''))
R.append(('''oku: bu paragraf, `08-URUN-KARARLARI.md` K-61 ve K-62, `06-ACIK-RISKLER.md`
T-60'ın son iki bölümü, şartname §6.7 (*Motor önce fazla mesaisiz plan arar*),
oturum günlüğü `oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md`
§12–14.

**4 Ekim 02:45 — K-60 verildi, gün kapandı.**''','''oku: bu paragraf, `08-URUN-KARARLARI.md` K-61 ve K-62, `06-ACIK-RISKLER.md`
T-60'ın son iki bölümü, şartname §6.7 (*Motor önce fazla mesaisiz plan arar*),
oturum günlüğü `oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md`
§12–14.

**⚠ 7 Ekim 03:30 — K-61'in 00:45 sürümü yanlıştı (O-18, T-60 bulgu 23);
düzeltildi, bulutta doğrulandı; Mustafa'nın koşuları ve 500 kişilik ölçüm
bekliyor; en güncel durum budur.** İşi görmemiş iki inceleme ajanı aynı
bulguyla döndü, kendi koşumla doğruladım: 00:45 sürümü fazla mesaisiz plan
bulunca fazla mesai alanlarını bütün aşamalarda kapalı tutuyordu ve
*"ağırlık koşulu"* bunu korumuyordu — **ürün ağırlıklarında** kanıtlı optimum
fazla mesaili olan sahneler var (15 dakikalık fazla mesai adımı bir haftalık
düzeni açıyor: 750'ye karşı 2.256; 12 kişide 9.000'e karşı 12.000 — tam 3
saat, Mustafa'nın örneği; iki ekibe üye kişide 750'ye karşı 900 / 2.000).
Mustafa'ya söylediğim *"bu kurda oluşmaz"* ve şartnameye yazdığım *"hesapla
gösterildi"* yanlıştı. **Düzeltme:** bulunan fazla mesaisiz plan yalnız
başlangıç noktası — alanlar geri açılır, iyileştirme tam ağırlıklı amaçla o
plandan başlar, kararı ağırlıklar verir (hiçbir plan dışarıda kalmaz); ağırlık
koşulu kalktı; sert kesim ölçüm seçeneği (`fazla_mesai_sifirda_tut`, bulgu 21
o hâl). Dört karşı örnek test; Mustafa'nın örneğinde fazla mesaisiz plan
bulunsa da 3 saatlik plan seçiliyor. Bulutta 41 dosya **583 test**, mutasyon
harnesi 285 (`fm_sifir` 43) grup koşularında öldü — **toplam ve yeşil
Mustafa'nın tam koşusundan sonra** (O-15). Küçük ölçekli ön ölçüm (49 kişi,
bulut, 20 sn, tek koşu): düzeltilmiş yol 2.713 (fazla mesai 0), sert kesim
2.758, 6 Ekim öncesi 11.918 (3 saat). **500 kişi ölçülmedi** — bulgu 21 sert
kesimin ölçümüdür. **Mustafa'da:** (1) koşular — testler, DENETIM, commit,
tam mutasyon; (2) bulgu 23 ölçümü `fm_once,fm_once_kapsama` 900 sn üçer koşu
(karar kuralı K-61'de koşudan önce yazılı); (3) ürün sorusu: K-30'un ilk
satırı (*hedef için fazla mesai asla*) ile K-61 ilkesi (*ağırlıklara göre
oldukça daha iyi plan seçilir*) birbirini tam örtmüyor — motor K-61'e göre
yazıldı. Açılışta oku: bu paragraf, `05-HATA-OTOPSILERI.md` O-18,
`06-ACIK-RISKLER.md` T-60 bulgu 23, `08-URUN-KARARLARI.md` K-61 (düzeltme
bölümü) ve K-30 (7 Ekim notu), şartname §6.7, oturum günlüğü
`oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md` §15.

**4 Ekim 02:45 — K-60 verildi, gün kapandı.**'''))
R.append(('''**Bulgu 21 (6 Ekim akşamı):** `fazla_mesai_once_sifir` ölçüldü — altı koşuda fazla mesai 0, amaç DENGELI 26,4–26,5 bin · KAPSAMA 13,8–13,9 bin, karar kuralı tuttu. Açık: ürün varsayılanı kararı; fazla mesainin zorunlu olduğu veri ölçülmedi; sonuç kartı için küresel sınır | Mustafa: *önce fazla mesaisiz* ürün varsayılanı olsun mu |''',
'''**Bulgu 21 (6 Ekim akşamı):** `fazla_mesai_once_sifir` ölçüldü (sert kesimle) — altı koşuda fazla mesai 0, amaç DENGELI 26,4–26,5 bin · KAPSAMA 13,8–13,9 bin, karar kuralı tuttu. **K-61 (6 Ekim 23:44):** ürün varsayılanı, hakem ağırlıklardır. **Bulgu 23 / O-18 (7 Ekim):** 00:45 sürümü ilkeyi çiğniyordu (fazla mesaisiz planı bulunca fazla mesaili planlara bakmıyordu; ürün ağırlıklarında karşı örnekler), düzeltildi — fazla mesaisiz plan yalnız başlangıç noktası. Açık: düzeltilmiş yolun 500 kişilik ölçümü; fazla mesainin zorunlu olduğu veri ölçülmedi; sonuç kartı için küresel sınır | Mustafa: koşular + bulgu 23 ölçümü; K-30 ilk satırı mutlak mı, ağırlıkların sonucu mu |'''))
for old,new in R:
    assert s.count(old)==1, old[:90]
    s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF