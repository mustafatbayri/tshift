cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo && python3 - <<'PYEOF'
import io
p="DEGISIM-GUNLUGU.md"
s=io.open(p,encoding="utf-8").read()
marker='''**2026-10-07 (00:45) · K-61: motor önce fazla mesaisiz plan arar (ürünün varsayılanı), hakem ağırlıklardır — koda indi; K-62: veri seti merdiveni ve kadro kararları**
'''
assert s.count(marker)==1
yeni='''**2026-10-07 (03:30) · O-18 / T-60 bulgu 23: K-61'in 00:45 sürümü ilkeyi çiğniyordu — bağımsız inceleme buldu, düzeltildi; fazla mesaisiz plan yalnız başlangıç noktası, kararı ağırlıklar verir; 500 kişilik ölçüm bekliyor**
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
'''
s=s.replace(marker,yeni)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
cd /mnt/user-data/uploads/Tshift && grep -n "devir_yuk\|devreden adalet\|geçmiş boş\|gecmis bos\|dışındaki kalemler\|%40 → %0,3\|yumuşak cezayla\|Tam ölçekte ölçüldü\|olmayacak\|olamaz\|oluşmaz" 08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/OKU-BENI.md | cut -c1-200