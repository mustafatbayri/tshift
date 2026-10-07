cd /tmp/claude-0/-home-claude/5238fc68-a9b3-5ff2-b41f-ed509faf594a/scratchpad/duzeltme/depo/00-DEVIR && python3 - <<'PYEOF'
import io
p="05-HATA-OTOPSILERI.md"
s=io.open(p,encoding="utf-8").read()
yeni='''## O-18 · Kararın ilkesi *"hakem ağırlıklardır"* idi; yazdığım kod fazla mesaisiz planı bulunca fazla mesaili planlara hiç bakmıyordu — ve *"bu kurda oluşmaz"* dedim, karşı örnek aramadan ⚠

**Tarih:** 7 Ekim 2026, 01:00–03:30 (hata 6 Ekim 22:45–7 Ekim 00:45 arasında
yazıldı; bağımsız inceleme buldu)

**Ne oldu.** 6 Ekim 23:44'te Mustafa *"önce fazla mesaisiz"* aramayı ürünün
varsayılanı yaptı ve ilkesini söyledi: *"…ağırlıklar baz alındığında örneğin
3 saat fazla mesai içeren en optimum plan var ve fazla mesaisiz plandan oldukça
daha optimum bir plan ise en optimum olanı seçmeliyiz."* Ben bunu koda şöyle
yazdım: birinci aşama fazla mesaisiz plan bulunca fazla mesai değişkenleri
**bütün aşamalarda 0'da kalır** (6 Ekim akşamının ölçüm seçeneği aynen), ve
ilkeyi bir *"ağırlık koşulu"* ile *"sağladım"*: fazla mesainin dakika başı
ağırlığı öteki ağırlıkların en büyüğünden küçük değilse kısayol uygulanır.
Gerekçem bir hesaptı: bir saat fazla mesai 3.000 puan, hedefin bir kişi-saat
altında kalmak 9 puan; *"bir saatlik fazla mesai en çok birkaç birim
kazandırır, 3.000'i geçemez"*. Mustafa'ya *"bu kurda 3 saat fazla mesaili
plan oldukça daha optimum durumu oluşmaz"* dedim, şartnameye *"hesapla
gösterildi"* yazdım, teste *"kısayolun planı kanıtlı optimumla aynı puanda"*
yazdım — tek bir sahneyle.

İşi görmemiş iki ayrı inceleme ajanı aynı gece karşı örnekleri buldu, ben de
koştum: **ürün ağırlıklarında** kanıtlı optimum fazla mesaili, kısayol daha
kötüsünü döndürüyor.

| Sahne (ürün ağırlıkları) | Kanıtlı optimum | Sert kesimin döndürdüğü |
|---|---|---|
| Tek kişi, DENGELI, SAAT_DENGESI yumuşak; şablonlar 7,5 sa × 5 + 7,75 sa | **750** (15 dk fazla mesai) | 2.256 (bir gün düşer: 7,25 sa sözleşme altı) |
| Tek kişi, KAPSAMA, SAAT_DENGESI sert | **750** | 880 (talebin dışındaki 9 saatlik şablon) |
| 12 kişi, KAPSAMA — Mustafa'nın örneği, tam **3 saat** | **9.000** | 12.000 |
| İki ekibe üye tek kişi (K-50), DENGELI / KAPSAMA | **750** | 900 / 2.000 |

Hesabın yanlışı: fazla mesai **adım adım** gelir (çeyrek saat = 750 puan) ve
küçük bir adım bütün haftanın düzenini açar — bir saatin kazancı *"bir
kişi-saat"* değil, *"bir gün daha çalışabilmek"* ya da *"sözleşme saatini
doldurabilmek"* olabiliyor (SAAT_DENGESI dakika başına cezalı, sert hâli
düzeni kilitliyor; iki ekibe üyelik kazancı ikiye katlıyor). Ağırlık koşulu
bunların hiçbirini görmüyordu. 500 kişilik sette bu durumun oluştuğu
gösterilmedi (en küçük şablon taşmaları 15–75 dk); oluşmayacağı da kanıtlı
değil.

**Neden.** (1) *"Kısayol"* diye adlandırdığım şey bir **kuraldı**: planların
bir kümesini aramadan çıkarıyordu. Mustafa'nın ilkesi *"hiçbir planı baştan
eleme"* demekti; ben *"elemenin zararsız olduğu koşulu bul"* diye okudum ve
koşulu da bir hesapla değil, hesabın **bir** biçimiyle kurdum. (2) *"Oluşmaz"*
cümlesini karşı örnek aramadan söyledim. Sınıf O-11 ve O-17 ile aynı (yorumda
yazılmış, ölçülmemiş iddia) ve O-16 ile aynı (kısıtlı bir modelin sonucunu
genel bir sonuç gibi sunmak). (3) Testi tezi doğrulayacak sahneyle yazdım
(8 saatlik tek şablon: en küçük fazla mesai adımı 3 saat); 15 dakikalık
adımın olduğu şablonlar, SAAT_DENGESI, iki ekibe üyelik testte yoktu. (4)
Mustafa 23:44'te mid-turn *"devam et"* dedi; hız baskısıyla 00:45'te *"koda
indi"* yazdım ve incelemeyi **sonraya** bıraktım — inceleme gelene kadar
kayıtlar yanlış cümleleri taşıdı.

**Nasıl fark edildi.** Bağımsız inceleme (iki ajan, kodu görmeden; bu
projenin alışkanlığı). İkisi de 01:00 civarı aynı bulguyla döndü; biri
rastgele sahne avıyla 8/400 karşı örnek buldu (çeyrek saat ızgaralı karışık
şablonlar + yumuşak SAAT_DENGESI), gerçekçi şablon netleriyle 0/1.200.
Mustafa'ya 02:35'te söylendi, blok koşmaması istendi.

**Düzeltme (7 Ekim).**

- **Motor:** fazla mesaisiz plan bulununca o plan yalnız **başlangıç
  noktasıdır** — fazla mesai alanları geri açılır, iyileştirme tam ağırlıklı
  amaçla o plandan başlar (ipucundan kötü plan dönemez), kararı ağırlıklar
  verir. Ağırlık koşulu kaldırıldı. Sert kesim **ölçüm** seçeneği olarak
  kaldı (`fazla_mesai_sifirda_tut`, varsayılan kapalı) — 6 Ekim'in ölçümü
  (bulgu 21) o hâldir ve yeniden üretilebilir.
- **Testler:** dört karşı örnek sahnesi test oldu (tam model kanıtlı optimumu
  = ürün yolunun puanı; sert kesimin daha kötü döndürdüğü de test). Mustafa'nın
  örneği: fazla mesaisiz plan **bulunsa da** 3 saatlik plan seçiliyor.
  `09-motor/testler/test_fazla_mesai_once_sifir.py` 27; mutasyon `fm_sifir`
  43 (toplam 285).
- **Kayıtlar:** şartname §6.7 / §11.3 / değişiklik 61, K-61, K-30 notu,
  T-60, BURADAN-BASLA, oturum kaydı — yanlış cümleler üstü çizilerek
  düzeltildi (sürümleme kuralı: tarih silinmez).
- **Açık:** düzeltilmiş yolun 500 kişilik ölçümü (Mustafa'nın makinesi);
  küçük ölçekte (49 kişi) iyileştirme fazla mesaiye dönmedi.

### Kalıcı bekçi

- **"Oluşmaz" / "olamaz" cümlesi karşı örnek avı olmadan yazılmaz.** Bir
  mekanizmanın bir plan kümesini aramadan çıkardığı her yerde (alan daraltma,
  sabitleme, kısayol) ilk soru: *dışarıda kalan kümede daha iyi plan var mı?*
  Cevap *"hayır"* ise bu bir ölçümdür (av betiği, sayı), bir hesap değil.
  DENETIM'e eklenecek: `00-DEVIR/*.md` içinde *"oluşmaz"*, *"olamaz"*,
  *"hesapla gösterildi"* geçen satırda `ölçüldü`/`test` referansı yoksa
  uyarı. *(yazılacak)*
- **İlkeyi koşula çevirme.** Karar *"hakem X'tir"* diyorsa kod X'i
  **uygular**, X'in ne zaman yanılacağını tahmin eden bir kapı yazmaz.
- **Test sahnesi tezi doğrulamak için seçilmez.** Bir davranışın *"her
  ağırlıkta doğru"* iddiası en az üç ayrı yapıdaki sahneyle sınanır (en
  küçük adımın büyüklüğü, yumuşak/sert kural çeşitleri, çok ekipli üyelik).
- **Bağımsız inceleme, kod "indi" denmeden önce gelir;** *"koda indi, koşuları
  bekleniyor"* cümlesi inceleme bitmeden yazılmaz.

---

'''
marker="## Özet: hata → bekçi tablosu"
assert s.count(marker)==1
s=s.replace(marker, yeni+marker)
old='''| O-17 | Karar veri setine bağlanmadı: iki işi yapabilen eleman 500 kişilik sette hiç yok (K-50); *"%95"* seti istenen kıtlığı (fazla mesai zorunlu) taşımıyor | Karar kapanışında üçüncü soru: *tam ölçekli veri setinde sınanıyor mu*; saha durumu oranla değil ölçümle doğrulanır; merdiven seviyelerinin *"neyi sınıyor"* tablosu | 🟡 *(kural yazıldı; bekçi merdiven aracıyla gelecek)* |
'''
new=old+'''| O-18 | *"Hakem ağırlıklardır"* kararını, fazla mesaili planları aramadan çıkaran bir kısayol + tahmini bir ağırlık koşuluyla yazdım; *"bu kurda oluşmaz"* dedim — ürün ağırlıklarında karşı örnek vardı (750'ye karşı 2.256; 12 kişide 9.000'e karşı 12.000) | Bulunan fazla mesaisiz plan yalnız başlangıç noktası (alanlar geri açılır, karar ağırlıklarda); karşı örnekler test; *"oluşmaz"* cümlesi av betiği olmadan yazılmaz; inceleme *"indi"* denmeden önce | 🟡 *(kod + test; DENETIM uyarısı yazılacak; 500 kişilik ölçüm bekleniyor)* |
'''
assert s.count(old)==1
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
PYEOF
grep -n "^## O-18\|^| O-18" 05-HATA-OTOPSILERI.md | head; sed -n 1,30p 05-HATA-OTOPSILERI.md | grep -n "O-17\|İçindekiler\|Icindekiler" | head