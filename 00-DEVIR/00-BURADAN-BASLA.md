# BURADAN BAŞLA

> **Yeni bir sohbet penceresi ya da başka bir yapay zekâ isen: önce bu sayfayı
> baştan sona oku, sonra aşağıdaki okuma sırasını takip et. Kod yazmaya
> başlamadan önce `02-DEGISMEZLER.md` dosyasını mutlaka okumuş olmalısın.**

**Son güncelleme:** 2026-10-01 · *(23 Eylül)* **dört 🔴 kapandı:** T-22, T-34, T-35, T-19. Motor **77 birim test** + **7 altın senaryo** yeşil; `.NET` 45/45; CI yeşil; `DENETIM.py` **0 hata**. Yeni kanal: `okunmayan_alanlar` — gönderilen ama okunmayan girdi alanı artık bildiriliyor. ⚠ Kapatma turları **dört yeni bulgu** açtı: T-38…T-41. **25 Eylül:** `SAGLIK_KISITI` kaldırıldı (K-21 geri alındı) · **K-31** yarım günlük izin elle yönetilir · **K-32 mola modeli** — dört yeni kural, katalog **38**. *(**28 Eylül:** dinlenme molaları çözücüye bağlandı · **K-33** `SAHADA_ASGARI` — firmanın *"sahada en az N kişi"* kuralı, katalog **39**; · **K-34** zaman birimi **çeyrek saate** indi (Z-7) · **K-35** süre seçimi, kanıtlanmış optimuma yakınlık ve *İyileştir* — motor **137 test** yeşil, katalog **39**. **350 kişilik gerçekçi veri seti kuruldu** ve tam ölçekte çalıştı: 1.757 atama, **0 sert ihlal**, %100 asgari kapsama. Altı bulgu açıldı, beşi aynı gün kapandı.)* T-42 açıldı, T-43 aynı gün geri çekildi) *(**29 Eylül:** 350 kişilik set **otomatik koşuya bağlandı** — çözmeden ölçülenler tam ölçekte, çözüm gerektirenler 0.1'de · **K-36** arama işçisi sayısı makinenin çekirdeğine uyuyor: 2 çekirdekte optimuma **%23,6 yerine %7,0** uzaklık — ⚠ 6 çekirdekli makinede aynı sahne ayırt etmedi, sunucu sorusu için gerçekçi ölçek + `--tekrar` gerekiyor · motor **146 test** yeşil · **T-48 hipotez olmaktan çıktı:** 45 saniyelik bütçe çözümsüzlükte **470 saniye** sürüyor.)*

**⚠ 29 Eylül akşamı — en güncel durum budur.** Mustafa 350 kişilik seti *"en zor senaryo"* diye anlattığım için uyardı; ölçülünce haklı çıktı (15 kuralın gövdesi yok, 13'ü hiç zorlanmıyor, kapasite talebin 2,3 katı). Yerine **500 kişilik iki set** kuruldu (%85 ve %95 doluluk). Dört karar: **K-37** *"imkânsız"* ile *"yetiştiremedim"* ayrı cevaplar (T-23 ve T-48 kapandı) · **K-38** haftalık 45 saat **normal** çalışma sınırı, toplam tavan değil · **K-39** sözleşme saati **doldurulur**, yarı zamanlıya saat girilmez · **K-40** gece vardiyası **işaretlenir**, tahmin edilmez. Katalog **40**, gövdesi yazılı **26**, motor **184 test** yeşil, zor set bekçileri **12** test. **Tam ölçek ilk kez çözüldü** — 2.493 atama, **0 sert ihlal**, `yayınlanabilir` True, **ama optimuma %98,3 uzak** ve 900 saniye istenen koşu 1.078 sürdü → iki yeni 🔴: **T-59** (bütçe aşımı, mekanik) ve **T-60** (kalite yok, önce dört ölçüm). Açık 🔴 sayısı **sekiz**.

**⚠ 30 Eylül — en güncel durum budur.** 29 Eylül'ün işi commit edildi, push edildi, CI'ın iki işi de yeşil yandı. Bugün **rol kapsaması** ve **yetkinlik kapsaması** doğrulayıcıya bağlandı: o iki kural çözücüde vardı, doğrulayıcıda yoktu — yani motor onlar için kendi işini kendi onaylıyordu. Gövdeler şartnameden okunarak yazıldı; 14 test, 9'u kırmızı yandı, beş mutasyondan biri ilk turda yaşadı ve yeni testle öldürüldü. Katalog **40**, gövdesi yazılı **28**, gövdesiz **12**, motor **198 test** yeşil. **Bağımsız denetim ilk gününde üç bulgu açtı:** **T-61** çözücü *"atanmış"* sayıyor, şartname *"sahada"* diyor · **T-62** saat listesi yazılmazsa çözücü o SERT kuralı hiç kısıtlamıyor, ekip yazılmazsa plan çözümsüz kalıyor · **T-63** veri setinde üç kural aktif ama hiçbir şey istemiyor. **T-64 aynı gün kapandı:** ihlal vakası aracı kendi listesini sayıyordu; evren artık doğrulayıcının kural kaydı — **28 gövde, 28 vaka, 28 kırmızı, eksik sıfır**. Açık 🔴 sayısı **on**.

**⚠ 30 Eylül akşamı — kararlar alındı, iki bulgu kapandı.** **K-41:** nitelik kapsamasında mola **sahadan çıkarmaz** (Mustafa: *"sahada bir müdürün işi 15 dk mola süresini bekleyebilir"*) — ⚠ değişen taraf **doğrulayıcı** oldu, çözücü haklıydı; iki test tersine çevrildi. `SAHADA_ASGARI` molayı düşmeye devam ediyor, ayrım bilerek. **T-62 kapandı:** saat listesi yoksa açık saatlerin hepsi, ekip yoksa saha çapı, kontrol çeyrek bazında. **T-63'ün rol tarafı kapandı:** *"yalnız gündüz saatlerinde 1 lider"* — her ekibe ayrı gereklilik satırı (08:00–20:00). ⚠ Gereklilik konunca 0.1 ölçekte plan **kanıtlanarak çözümsüz** kaldı; sebebi kural değil **ölçek** çıktı (2 lider × 6 gün = 12 lider-günü, gereken 14) ve üreticiye ekip başına 4 lider tabanı kondu. Motor **202 test** yeşil, gövde **28**, açık 🔴 **sekiz**. ⚠ **Yazı borcu:** şartname §6.4'ün iki satırı hâlâ *"sahada"* diyor.

**⚠ 30 Eylül gecesi — CI kırmızı yandı ve sebebi ölçümdü.** *"Sert ihlal 0, asgari kapsama %99,76"* çifti çelişki gibi duruyordu; ikisi de motorun **kendi** raporundan geliyordu. **T-65:** motorun kapsama metriği kesirli vardiya bitişini `int()` ile kırpıyordu (07:00–16:15 → saat 16 sayılmıyor) — ⚠ **T-58 ile aynı aile**, aynı varsayım 29 Eylül'de doğrulayıcıda düzeltilmişti, çözücüdeki kopyasına bakılmamıştı. Test **rastgele** yeşil yanıyordu. Düzeltildi; bekçi artık **doğrulayıcının** sayısına bakıyor ve iki tarafın anlaştığını ayrıca sınıyor. **T-66 açıldı:** `sert_ihlal` ölçülmüyor, **sabit sıfır** yazılıyor — §11.3 Mustafa'nın kararını bekliyor. Motor **205 test** yeşil.

**⚠ 30 Eylül gecesi (2) — yasal gece sınırı yazıldı.** `GECE_VARDIYASI_AZAMI`
(K-26): gece penceresine düşen **net** çalışma 7,5 saati geçemez; turizm,
özel güvenlik, sağlık ve petrolde **yazılı onaylı** çalışan için kalkar — istisna
**kişi bazlı**. İki yeni girdi alanı: `sektor`, `gece_calisma_onayi`. ⚠ Çözücü
sınırı **brüt** ölçüyor (T-68) — bilerek; yasal planı reddedebilir, yasadışı
üretmez. ⚠ Veri seti kuralı zorlamıyor (en uzun gece 7,00 saat). Kalan
gövdesizler yeniden sayıldı: **11**, ama biri (`GECE_YARISI_ASAN`) şartnameye göre
zaten ihlal üretmez (T-67) — gerçek eksik **10**. Motor **225 test** yeşil,
**29 gövde · 29 vaka · 29 kırmızı**.

**⚠ 30 Eylül gecesi (3) — iki firma sınırı.** Asgari vardiya süresi (**brüt**,
bilerek) ve ardışık gece limiti (K-40'ın gece işareti) iki tarafta da yazıldı.
⚠ *"Karar gerektirmeyen beş kural"* dediğimin yalnız ikisi öyleydi; çalışma
saatleri, ekip sürekliliği ve rotasyon yönü karar istiyor. Motor **242 test**,
**31 gövde · 31 vaka · 31 kırmızı**; gövdesiz **9** (biri bilerek, T-67).
**T-28:** Mustafa geçmişin PDKS'ten geleceğini söyledi; gerçek veride kayıtların
yalnız %18'i dolu — şartnamenin *"lookback eksikse motor çalışmaz"* kuralıyla
çarpışıyor.

**⚠ 30 Eylül öğleden sonra — T-28 KAPANDI, en güncel durum budur.** Mustafa iki
karar verdi (**K-42**): geçmiş veri yoksa motor durmaz, geçmişe dayanan ölçütler
— **yasal olanlar dahil** — atlanır ve **raporlanır**. İki motor yarısı artık
`gecmis_vardiyalar`'ı okuyor; beş kural pazartesi 00:00'da kör değil.
**Mustafa'nın iki aşamalı yoluyla ölçüldü:** hafta 2 geçmişsiz çözülünce
geçmişi bilen denetçiye göre **27 sert ihlal** (49 kişi, tek hafta, hepsi
bugüne kadar görünmez); geçmişle **0**. **T-70:** mutasyon denemeleri eski
bytecode ile koşabiliyordu — `mutasyon_kostur.py` yazıldı, bütün mutasyonlar
yeniden koşuldu: **42'si de öldü**. **T-69:** işaretsiz erken saatli vardiya
iki tarafta da gece sayılmıyor. Motor **274 test** yeşil.

**⚠ 30 Eylül akşamı — en güncel durum budur.** Mustafa dışarıdayken, soru
sormadan: **gece postası devri** (yasal) ve **ardışık hafta sonu limiti** iki
motor yarısında yazıldı. Yönetmeliğin **tam metni** okundu; şartnamede olmayan
iki fıkra çıktı — md. 7/2 geceyi tanımlıyor (*"çalışma süresinin yarısından
çoğu gece dönemine rastlayan"* posta), md. 8/3 iki haftalık nöbetleşmeye izin
veriyor (T-73). Yasal kural firma işaretini **bilerek kullanmıyor**.
*"Bir iş haftası gece çalıştırılan"* tanımsız — **en sıkı okuma** uygulandı
(**T-72** 🔴, karar bekliyor). **Ölçüldü:** 49 kişide ikinci hafta geçmişsiz
çözülünce 11 kişi iki hafta üst üste gecede; geçmişle çözüldü, 0 ihlal.
**T-74** 🔴: yasal gece sınırı (K-26) yalnız pencereye düşen kısmı ölçüyor —
yönetmeliğe göre gece postasının **bütün** süresi 7,5 saati geçemez; gerçek
müşteride 16:00–01:00 deseni 82 kez; **bilerek değiştirilmedi**. **T-69 ve T-71
kapandı:** işaretsiz vardiyanın tahmini artık md. 7/2; doğrulayıcının adalet
boyutu işareti okuyor. **33 gövde · 33 vaka · 33 kırmızı**. **T-59 düzeltildi**
(karar gerektirmiyordu):
birinci aşama artık süre bütçesinin **içinden** pay alıyor — tam ölçekte
yeniden ölçülene kadar 🟡. **Üç haftalık ölçüm:** üçüncü hafta, iki haftalık
geçmişle **iki bağımsız koşuda da çözümsüz** — ardışık hafta sonu limiti
kaldırılınca çözülüyor (**T-75** 🔴; 6 günlük desende herkes her hafta sonu
*"çalışmış"* sayılıyor, motor gelecek haftayı görmüyor). Çözücünün teşhisi
*"engelleyen: yok"* dedi (**T-76**). **Sahte PDKS** kuruldu: eksik geçmişle
yapılan planda gerçek geçmişe göre 7 ihlal kaçtı, **hepsi** raporda haber
verilmişti — ama 141 satırla (**T-77**). Motor **359 test**, bekçiler **20**,
**88 mutasyon, hepsi öldü**. Açık 🔴 **dokuz**. **Mustafa'yı bekleyen sorular:**
oturum kaydı `oturumlar/2026-09-30-nitelik-kapsamasi.md` bölüm 29 ve eki.

**⚠ 30 Eylül gecesi — en güncel durum budur.** Mustafa döndü; hukukçu olmadığı
için iki yasal soruyu çevrimiçi kaynaklarla bana bıraktı, kalanını
kararlaştırdı — **beş karar, iki motor yarısında:** **K-43** gece işareti
yönetmelikten otomatik gelir ve tabandır, firma yalnız ekler (K-40'ın üç
bekçisi tersine döndü) · **K-44** yasal gece sınırı gece postasının **bütün**
süresine (Yargıtay 9. HD 2020/17967) · **K-45** gece haftası = saatlerin
yarısından çoğu; üst sınır 2 = iki hafta gece, iki hafta gündüz · **K-46**
hafta sonu = iki gün de, gün = saatlerin yarısından çoğu · **K-47** geçmiş
eksik raporuna yönetici bakar. **Ölçüldü:** üçüncü hafta artık **çözülüyor,
0 ihlal** (T-75 kapandı); tam ölçek 1.200 sn koşusu süre sözünü tuttu (T-59
kapandı) ama **1 sert ihlalle** döndü — **T-78** 🔴, koşu tekrarı gerekiyor.
Teşhis *"belirsiz"* diyebiliyor (T-76 kapandı). Motor **406 test**, **116
mutasyon hepsi öldü**, 33 gövde · 33 vaka. Açık 🔴 **yedi**. **Şartname yazı
borcu** birikti (§6.3, §6.5, §8.3, §11.4 — oturum kaydı bölüm 37).
**⚠ 1 Ekim gecesi — en güncel durum budur.** Mustafa gece commit'ini push edip
tam ölçeği üç kez koşturdu: 900 sn temiz, 1.200 sn **1 sert ihlal**, gece
commit'inden sonra 900 sn yine temiz. **T-78 planı beklemeden koddan bulundu
ve kanıtlandı:** müşteri hizmetleri şablonlarındaki **20 dakikalık** dinlenme
molası çeyrek ızgarada 1 çeyrek (15 dk) sayılıyordu; pencereler o hesapla
ayrılıyor, mola gerçek süresiyle uzuyor — iki mola **5 dk üst üste** binebiliyor,
doğrulayıcı onu tek aralık sayıp 5 dk fazla çalışma görüyordu. Tam 45,00
saatteki yarı zamanlıda bu tek başına sert ihlal. Sahne şablonlarında sayıldı:
eski kod M-SABAH'ta 2.880 yerleşimin **822'sinde** ayrışıyordu. ⚠ İlk hipotezim
(sığmayan mola) **yanlıştı**. Üç yerde düzeltildi (yukarı yuvarlama, gerçek
zamanlı çakışma, emniyet kemeri) + sığmayan politika artık **nota** yazılıyor.
Motor **416 test**, **122 mutasyon hepsi öldü**, bekçi 20, 33 gövde · 33 vaka, sahte
PDKS 0 habersiz. Yeni 🟡 soru: süre bütçesi duvar saati mi (model kurma ~55 sn
dışarıda; K-48 adayı). `ilk_cozum_sn` çıktıya eklendi (T-60 için). Açık 🔴
**altı**.

**⚠ 1 Ekim 13:05 — düzeltmenin bedeli ve cevabı (en güncel durum budur).**
Mustafa T-78 düzeltmesini push edip (CI yeşil) tam ölçeği koşturdu: **plan
bulunamadı** — `sure_yetmedi`, 0 atama, 778 saniyede ilk plan yok (dün 654
çözüm vardı). Model çözümsüz değil, arama ağırlaştı; çözücü zaten sınırdaydı
(birinci aşama üç koşuda da 120 sn'de plan bulamıyordu). **Yapılan (T-60'ın
plan bulma tarafı):** birinci aşama molaları ideale en yakın tek noktaya
**sabitleyerek** arıyor (alan [0,0], kısıt yok, sonra geri) ve ipucu artık
**bütün** değişkenlere yazılıyor (yarım ipucuyu CP-SAT 10 çelişkide
bırakıyordu). 0.2 ölçekte: birinci aşama 18 → **1,7 sn**, ana aşamanın ilk
planı 57–101 → **21 sn**; 0.3 ölçekte (151 kişi) tam ölçeğin hastalığı yeniden
üretildi — eski kod ipucu eldeyken ana aşamada **hiç plan bulamadı** (265 sn),
yeni kod 2,5 sn + ilk plan 25 sn. ⚠ **Tam ölçekte ölçülmedi** — 15:20 koşusu
bunun sınavı. Ana aşama molaları serbest arıyor (K-32 değişmedi). **K-48** (sabah
onayı bekliyor): bütçe = arama, model kurma ayrı gösterilir. Ölçüm betiği
modeli artık bir kez kuruyor (55–80 sn tasarruf). Motor **421 test**,
**128 mutasyon hepsi öldü** (1 Ekim 15:35, tam koşu). **Sabah:** commit + `py coz-olc.py --saniye 900`; beklenen
`iki asama: True`, ilk plan erken, 0 sert. **→ 1 Ekim 15:20, ölçüldü ve geçti:**
birinci aşama 10,3 sn, ilk plan 48,9 sn, 0 sert, yayınlanabilir; planda üst
üste binen mola yok. T-78 sahada kapandı; T-60'ın plan bulma yarısı kapandı,
kalite yarısı (%99 uzaklık) duruyor. K-48 kesinleşti. **Şartname yazı borcu ödendi** (16:30): §6.3, §6.4, §6.5, §8.4, §11.2–11.4 ve değişiklik listesi 29–35.

**⚠ 1 Ekim 16:45 — iki karar daha, en güncel durum budur.** Mustafa iki 🔴'yı
kararlaştırdı. **K-49 (onayladı):** motorun kontrol edemediği aktif kural kapıdan
geçemez — yasal+sert engeller, firma+sert yetkili gerekçeyle kabul edene kadar
bekler, yumuşak yalnız raporlanır. Kapı kapanınca veri seti üç yerden ısırdı:
parametresiz yetkinlik kuralı ve gövdesiz çalışma saatleri kuralı için gerekçeli
kabul kaydı; **yıllık fazla mesai tavanı (yasal) gövdesizdi → gövdesi yazıldı**
(iki yarıda; yıl içi toplam bilinmiyorsa K-42 ile atlanır). Gece yarısını aşan
vardiya kuralı "ihlal üretmez" diye kayıtlı (T-67 kapandı). **K-50 (Mustafa'nın
sahası):** çok yetenekli çalışan üye olduğu **bütün ekiplere** sayılır — sabah
önerdiğimin tersi; değişen taraf doğrulayıcı, görünürlük `baska_ekipten_kapsama`,
"yalnız vardiyanın ekibine say" kiracı seçeneği. T-18 ve T-21 kapandı. Motor
**459 test**, **154 mutasyon hepsi öldü**, 35 gövde · 34 vaka · 34 kırmızı (+1
bilerek vakasız). Açık 🔴 **dört** (T-29, T-38, T-54, T-60).

**⚠ 1 Ekim 17:27 — dört karar daha uygulandı, en güncel durum budur.**
**K-51:** çözücünün sabit "0 sert ihlal" sayısı çıktıdan kaldırıldı.
**K-52:** departman tanımı ve çalışma saatleri geldi (`departmanlar[].acik`),
`CALISMA_SAATLERI` iki yarıda yazıldı; her birim için yetkinlik gerekliliği
(satış 2 İngilizce, back office 1 İngilizce, müşteri hizmetleri 1 İngilizce +
1 Almanca), üretici taşıyıcı tabanı koyuyor; veri setindeki kabul kayıtları
kalktı. **K-53:** hedefi aşan kişi-saate yumuşak ceza (`HEDEF_ASIMI`, katalog
**41**). **T-38** 🟡'ya indi ve sıralandı; `sure_butcesi_sn` ve `istek_id`
servise bağlandı. Kapananlar: T-54, T-63, T-66 (+ bugün daha önce T-18, T-21, T-67,
T-78). Motor **481 test**, mutasyon **166 hepsi öldü** (18:45: 171), 37 gövde · 36 vaka ·
36 kırmızı (+1 bilerek vakasız), bekçi 20, altın senaryolar 12 geçti. Açık 🔴
**iki**: T-29 (dondurulmuş gün — Mustafa onayladı, yazılacak), T-60 (kalite).
⚠ Bugünkü değişikliklerden sonra tam ölçek **yeniden** koşulmalı.

**⚠ 1 Ekim 18:15 — PDKS ham verisi ölçüldü, en güncel durum budur.** Mustafa
ham PDKS'i açtı; betik makinesinde koştu, yalnız sayı döndü
(`07-motor/pdks-ms-gece-yarisi.py`). **K-47'nin açık sorusu cevaplandı:**
PDKS'in `00:00`'ı plan değil, kart okutulunca sonradan değişen takvim —
*"bilinen boş gün"* kaynağı **olamaz**; gece yarısını aşan vardiya PDKS'te de
başladığı günde (motorla aynı, düzeltme yok); PDKS'in normal/eksik/fazla
mesai kovaları vardiyalı çalışan için yanlış, yıl içi fazla mesai bordrodan
gelmeli. Bulgular `07-GERCEK-VERI-BULGULARI.md` §7; öneri karar bekliyor.
İkinci tam ölçek koşusu (16:45 kodu) **0 sert, yayınlanabilir**; beş kararın
commit bloğu verildi, 17:27 kodunun tam ölçek koşusu bekleniyor, push sonra.
⚠ Bugünün saat etiketleri 18:15'te sohbet kaydına göre düzeltildi ("akşam/gece,
19:15, 22:40, 22:50" yanlıştı; öğleden sonra ve akşam işiydi).

**⚠ 1 Ekim 18:45 — CI kırmızı yandı ve sebebi testti, en güncel durum budur.**
Push'tan sonra GitHub'da `test_sure_yetmedi.py`'nin dört testi kırmızı:
GitHub'ın makinesi 60 kişilik sahneyi 1 saniyede çözdü, test çözememesini
bekliyordu (0,1 sn bütçe aslında 1 sn; konteynerde ilk plan 1,9 sn).
**Motor değişmedi;** testler artık dolan bütçeyi enjekte ediyor
(`sure_dolmus`), 5 yeni mutasyon öldü, toplam **171**; 481 test yeşil.
T-79 kapandı, otopsi O-12. Üçüncü tam ölçek koşusu (17:27 kodu, 46 kural)
**0 sert, yayınlanabilir** (birinci aşama 22,9 sn, ilk plan 88,8 sn).
Push tekrar bekleniyor.

**⚠ 1 Ekim 20:40 — dondurulmuş gün canlandı (K-54), en güncel durum budur.**
CI yeşil yandı; T-29 kapatıldı. Yayınlanmış plan (`mevcut_plan`) motora
girdi: donmuş günün satırları çıktıya **aynen** geçer (molalarıyla), o güne
yeni atama yazılmaz, geçmiş **gerçek** sayılır (dinlenme, haftalık saat,
adalet), geçmişin kusuru planı çözümsüz **etmez** (yalnız geçmişe ait
kısıtlar düşer, aşılmış sınır kırpılır). Doğrulayıcı `DONMUS_GUN`'u plana
göre yazar (eklenen/silinen/değişen), geçmişe ait ihlalleri `gecmis`
işaretler ve kapı saymaz; plansız donmuş gün *"denetlenemedi"* (kabul
bekler). Gerçekçi sahne artık taze hafta (`donmus_gunler: []`; eski `[0]`
ölü kuralla hiç etkili olmamıştı — zorluk aynı). Donmuş gün yolu: bekçide
0,1 ölçekte yeniden planlama (gün 0 aynı, 0 sert) ve `coz-olc.py --donmus`
(tam ölçek). Motor **497 test**, mutasyon **179 hepsi
öldü**, bekçi **21**, vaka aracı 36 vaka · 36 kırmızı, altın 12. Açık 🔴 **bir**: T-60
(kalite). Arayüz tarafı (çoklu seçimle kilit/silme) yazılmadı.

**⚠ 1 Ekim 21:15 — donmuş gün tam ölçekte kanıtlandı, en güncel durum budur.**
Mustafa `coz-olc.py --saniye 900 --donmus` koştu: taze hafta 0 sert; gün 0
dondurulup motorun kendi planıyla yeniden çözüldü — 92.899 kısıt geçmişe
düştü, 0 kırpıldı, 305 sn, **gün 0 aynı, 0 sert, yayınlanabilir**. Koşu bir
yanlış etiketi gösterdi (adalet dengesi "olan oldu" sayılıyordu); günsüz
ihlalde artık yalnız tavan kuralları geçmiş sayılabilir. Motor **499 test**,
mutasyon **180 hepsi öldü**. Push bekleniyor.
**Son sürüm etiketi:** `v0.8-devir`
**Depo:** `github.com/mustafatbayri/tshift` (özel) · yerel kök: `C:\Users\PC\Desktop\Tshift`

---

## 1. Bu proje nedir, tek paragrafta

**T-Shift**, çok kiracılı (multi-tenant) bir yapay zekâ destekli vardiya
planlama ve optimizasyon SaaS ürünüdür. Teknovisor markası altında
geliştiriliyor. Ürün sahibi ve tek karar verici **Mustafa**: 11 yıllık BT ürün
müdürü, **yazılımcı değil** — kod yazmıyor, kod okumuyor. Bütün kod yapay zekâ
tarafından yazılıyor, Mustafa niyeti ve iş kurallarını doğruluyor.

Bunun iki pratik sonucu var ve ikisi de bu projedeki her kararı şekillendiriyor:

1. **Mustafa'ya kod gösterilerek onay alınamaz.** Doğrulama, testlerin ve
   dokümanların Türkçe iş cümlelerine çevrilmesiyle olur.
2. **Yapay zekâ kendi hatasını göremez.** Bu yüzden bu projede kurallar
   yazıya değil, **otomatik kontrollere** bağlanır. Detay: `05-HATA-OTOPSILERI.md`.

---

## 2. Şu anda neredeyiz

**Dikey dilim tamamlandı.** Veritabanından ekrana kadar bütün katmanlar bağlı
ve çalışıyor:

```
PostgreSQL + RLS → EF Core → Kimlik → Yetki/Kapsam → Denetim kaydı → API → Next.js arayüz
```

- **45/45 test yeşil.** Hepsi gerçek PostgreSQL'e karşı koşuyor, hiç mock yok.
  *(23 Eylül: T-34 ile üç sır testi eklendi — `S1`, `S2`, `S3`.)*
- **CI çalışıyor (14 Eylül), 16 Eylül'de motor da bağlandı.** Her `git push`
  sonrası **iki iş** koşuyor: `test` (.NET) ve `motor` (Python). Kurallar
  artık öneri değil **kapı**.
- **Tek komutla ayağa kalkıyor:** `docker compose --profile tam up --build`
- **Çalışan ekranlar:** giriş, çalışan listesi (rol bazlı farklı davranıyor),
  yeni çalışan kaydı.
- **Yılmaz'a inceleme paketi gönderildi** (`05-inceleme/v1-2026-09-11/`).

**Motor çekirdeği çalışıyor (16 Eylül).** Doğrulayıcı, çözücü ve onarım
döngüsü yazıldı; **yedi altın senaryo** (A1, A3, A4, A6, A7, A8, A9) ve o gün
60 birim testi yeşildi. **23 Eylül itibarıyla 77 birim testi**, CI'da da
yeşil.

⚠ **"Motor tamamlandı" demiyoruz, bilerek.** Kataloğun **38** kuralının **23**'ü
yazılı; A2/A10/A11/A12 backend tarafında ve hiç sınanmadı; aynı gün yapılan
**dış inceleme üç turda 19 bulgu** buldu, dokuzu 🔴 (T-18…T-36). Doğru
ifade: *belirli senaryoları çalışan bir motor çekirdeği var.*

**Dokuz 🔴'nın hepsi sessizdi:** hiçbiri kırmızı yanmıyordu, hepsi planı
temiz gösteriyordu.

**Beşi kapandı:** T-27 (16 Eylül) · T-22, T-34, T-35, T-19 (23 Eylül).

**Dördü açık:** geçmiş hafta hiç okunmuyor (**T-28**), *"geçmiş yeniden
planlanamaz"* sözünün tek bekçisi ateşlenemiyor (**T-29**), çok ekipli çalışan
iki ekibi aynı anda dolduruyor (**T-21**), denetlenmemiş kural yayını
engellemiyor (**T-18**).

⚠ **Kapatma turları dört yeni bulgu açtı — ve bu bir kural haline geldi.**
T-19'u kapatırken şartnamenin **on iki alanı daha** motorda karşılıksız çıktı
(**T-38** 🔴). ⚠ Bu kaydın ilk gerekçesi **yanlış yazılmıştı** ve 25 Eylül'de
düzeltildi; en ağır satır `izinler[].tum_gun`: **yarım günlük izin motora
gelmiyor**, motor bütün günü kapatıyor, yarım gün rapor alan kişi o gün hiç
planlanamıyor. Yanında
**T-39** 🟡 (aynı hücreye iki talep satırı tanımsız), **T-40** 🟡
(`tercih_karsilama_yuzde` şartnamede var, motorda yok — onu gerektirdiği
söylenen A7 onsuz yeşil) ve **T-41** 🟡 (`DENETIM.py` uyarılarının 13'ü
kalıcı). Açık 🔴 sayısı dörtten **beşe** çıktı.

### 25 Eylül — mola modeli baştan kuruldu (K-32)

Gün `SAGLIK_KISITI`'nı yazmakla başladı, kuralın **kaldırılmasıyla** bitti
(K-21 geri alındı): ürünün gördüğü sağlık durumu kalıcı bir süre kısıtı değil,
**dönemsel bir rapor** — ve o zaten bir izin satırı. Yarım günlük izin de
kapsam dışına alındı (**K-31**): plan yapılırken bilinemez, elle yönetilir.

Sonra iş molaya kaydı ve **K-32** çıktı:

| | |
|---|---|
| Mola tipleri | `dinlenme` (ücretli) · `yemek` (ücretsiz, tek blok) |
| **Üç süre ayrı** | `brut_saat` · `toplam_saat` (çalışma) · `ucret_saat` |
| Yemeğin yeri | Mutlak saat değil, **vardiyaya göreli** (3.–5. saat), firma parametresi |
| Yeni kural | `MOLA_YERLESIMI` (yumuşak) · `MOLA_TIPI_ZORUNLU` · `MOLA_ASGARI_BLOK` · `YEMEK_TEK_BLOK` |
| Mola politikası | Firmada varsayılan, **şablonda ezilir** (§5.2 merdiveni) |

⚠ **K-32'nin ilk hâli yanlıştı ve aynı gün düzeltildi.** *"Ücretli olmak"* ile
*"çalışma süresine dahil olmak"* karıştırılmıştı. Bu varsayımla `net_saat`
ters yönde değiştirildi, *"motor günde bir saat eksik hesaplıyor"* diye bir
**bulgu uyduruldu**, ve A08'in kırılması *"altın senaryo yeniden onaylanmalı"*
diye okundu. Gerçek: `net_saat` doğruydu, A08 doğruydu, kıran şey modeldi.

**Yakalayan haftalık dış inceleme oldu.** İç ölçüm bulamazdı — **yanlış model
doğru ölçülüyordu** ve her test yeşil yanıyordu. Ayrıntısı K-32'nin
*"Düzeltmenin kaydı"* bölümünde.

✅ **28 Eylül'de tamamlandı.** Dinlenme molaları çözücüye bağlandı; motor
firmanın mola politikasını plana çeviriyor ve molaları kişiler arasında
kaydırıyor. `_sahada` yeniden kuruldu: *"sahada olmak"* artık
`(kapsamayan yemek seçenekleri) − (kapsayan dinlenmeler)` — **doğrusal**,
yardımcı değişken yok. Şartı molaların birbirini kesmemesi; bekçisi
`test_molalar_BIRBIRINI_kesmez`.

Aynı gün **K-33** geldi: firma *"sahada en az N kişi"* diyebiliyor (`SAHADA_ASGARI`, SERT). Önce bir plan ölçüldü: saat 12 ve 13'te **sahada sıfır kişi**, sert ihlal 0, `yayınlanabilir` **True**. ⚠ Kuralın ilk hali **yanlıştı** — tabanı `min(parametre, hücrenin asgarisi)` ile sınırlıyordu ve bir test bu hatayı **sabitliyordu**. Mustafa: *"Firma molada en az 5 demeyecek, firma sahada en az 5 diyecek."* Sınır kaldırıldı, test **tersine çevrildi**. Ölçüm yeni bir 🔴 açtı (**T-44**): bugünkü mola pencereleriyle plan ancak **`N ≥ 4F`** iken çözülüyor — taban 3 için 12 kişi gerekiyor. Motor **109 test** yeşil.

> **Kaydedilen bulgu, bulgunun kendisi değildir.** T-34 iki satır sanılmıştı,
> 16 yer çıktı. T-35 kiracı çapı sanılmıştı, kurulum çapı çıktı. T-19'un üç
> ölçüsünün üçü de dardı. Bir bulguyu kapatmak, onu **ilk kez gerçekten
> ölçmek** demek.

**Henüz yazılmadı:** `/suggest` ucu (öneri üretimi, §11.5), plan editörü,
kural yönetimi, kullanıcı/rol yönetim ekranları.

**Gerçek müşteri verisi elimizde (13–14 Eylül).** Bir seyahat acentesinin 3,5
aylık PDKS ve vardiya planı. Analiz edildi, **529 kural ihlali** bulundu.
Bulgular ve Mustafa'nın kapsam kararları: **`07-GERCEK-VERI-BULGULARI.md`**
— motor yazılmadan önce okunmalı.

⚠ `07-motor/` klasöründe **motor yok**, analiz araçları var. Bkz.
`07-motor/OKU-BENI.md`.

**Fikstürler yazıldı (16 Eylül).** `08-motor-testleri/v5/fikstur/` — 11 JSON
dosyası + ortak sahne. Kod değil veri; motor hangi dille yazılırsa yazılsın
aynı dosyalar koşar. Biçim: `08-motor-testleri/v5/fikstur/OKU-BENI.md`.

**Test iskeleti yazıldı (16 Eylül).** `08-motor-testleri/v5/testler/` —
pytest çatısı (A1, A3, A4, A6, A7, A8, A9) ve xUnit taslakları (A2, A10, A11,
A12). Koşuyor ve **bilerek kırmızı**:

```
py -m pytest -q   →   7 failed, 4 passed, 5 skipped      (motor ADRESSIZ)
```

Motorsuz koşu **hâlâ kırmızı ve bu doğru** (§16.4 kırmızı kanıt): motor
adressizken testler yeşil yanıyorsa hiçbir şeyi sınamıyorlar demektir.
Yeşiller paketin **kendi** sağlık kontrolü: fikstürler yükleniyor mu, her
`kontrol` adının gövdesi var mı, motorun yokluğu açıkça söyleniyor mu.

✅ **"Motor gelince tek dosya değişecek" sözü tutuldu.** Doğrulayıcı yazıldı ve
yalnız `motor_istemci.py` değişti — testlerin, fikstürlerin ve kontrollerin
tek satırı değişmedi.

⚠ **Bu paket CI'da koşmuyor — bilerek.** CI şu an yalnız `dotnet test`
çalıştırıyor (A-4). Kırmızı bir paketi kapıya bağlamak "main her zaman yeşil"
kuralını bozardı. C# taslakları da bu yüzden `.cs.taslak` uzantılı —
derleyici görmez, CI kırılmaz. Ayrıntı: `08-motor-testleri/v5/testler/OKU-BENI.md`.

**MOTOR ÇEKİRDEĞİ ÇALIŞIYOR (16 Eylül) — yedi altın senaryo yeşil.**
`09-motor/` üç parçadan oluşuyor ve **üçü ayrı ayrı durur**:

| Parça | Ne yapar | Ne yapmaz |
|---|---|---|
| `09-motor/dogrulayici/` | Var olan planı kurallara karşı denetler | Plan üretmez |
| `09-motor/cozucu/` | CP-SAT ile plan üretir | Kendi ürettiğini denetlemez |
| `09-motor/orkestra.py` | İkisini üstten çağırır, §11.7 onarım döngüsünü koşar | Kural bilmez |

```
py servis.py   (ayri pencerede)
$env:TSHIFT_MOTOR_URL = "http://localhost:8000"
py -m pytest -q   →   12 passed, 4 skipped
```

Atlanan dört senaryo backend tarafında koşuyor (A2, A10, A11, A12);
A5 ertelendi (K-12).

| | Sayı | Ne zaman ölçüldü |
|---|---|---|
| Yazılan kural gövdesi | **37** (katalogdaki **41**'in alt kümesi; biri ihlal üretmez) | 1 Ekim akşamı, ikisi de sayılarak |
| Motor birim testi | **481**, hepsi yeşil | 1 Ekim akşamı, koşularak |
| Zor veri seti bekçisi | **20**, hepsi yeşil (12 + sahte PDKS üreticisi 8; 6 dk 10 sn) | 30 Eylül gecesi |
| **Koşan** altın senaryo | **7** — A1, A3, A4, A6, A7, A8, A9 | 23 Eylül |
| Kırmızı kanıt | **12 kasten bozma, 12'si de yakalandı** | 16 Eylül |

⚠ **Bu tabloda 23 Eylül akşamına kadar iki yanlış sayı vardı.**
*"Altın senaryo 12, hepsi yeşil"* yazıyordu: `12 passed` sayısı **7 senaryo +
paketin kendi 5 sağlık testidir**; A2, A10, A11, A12 backend tarafında ve hiç
koşmadı. Bu düzeltme 16 Eylül'de `06-ACIK-RISKLER.md`'ye yazılmış ama **buraya
taşınmamış** — bir hafta burada yanlış durdu. Kural gövdesi de 17 yazıyordu,
sayılınca 19 çıktı.

> **T-37 ile T-26 aynı anda.** Giriş dokümanı hiçbir tazelik kontrolünün
> kapsamında değil (T-37), ve bir yerde yapılan düzeltme kendiliğinden
> yürürlüğe girmiyor (T-26). Bu tablo ikisinin kesişme noktasıydı.

⚠ **Kırmızı kanıtın ilk turu 8'de 4'ünü KAÇIRDI.** Kaçanlar: ağırlık tablosu
yok sayılsa, adalet gradyanı kaldırılsa, orkestra doğrulayıcıyı çağırmasa ya
da fazla mesai tavanı sabitlense **hiçbir test kırmızı yanmıyordu**. Eksik
testler o yüzden yazıldı (`09-motor/testler/test_profiller.py`). Kırmızı
kanıt turu olmasaydı bu dört boşluk sessizce kalırdı — turun varlık sebebi
tam olarak budur.

⚠ **Doğrulayıcı çözücüyle mantık paylaşmaz** (§7.6, §16.1). Çözücü yazılırken
*"aynı hesabı iki kez yazmayalım"* deyip ortak modül çıkarmak **yasaktır** —
tekrar burada maliyet değil, güvencedir.

**Sessiz geçmeme:** girdide aktif ama gövdesi yazılmamış bir kural varsa cevap
`uygulanmayan_kurallar` listesinde bunu açıkça söyler. *"İhlal bulamadım"* ile
*"bakmadım"* aynı şey değildir.

Ayrıntı: `09-motor/OKU-BENI.md`

**Şartname v1.4 yazıldı (16 Eylül).** `02-spec/v1.4-master-spec.md` —
**v1.3'e dokunulmadı**, yanına yazıldı. Ana değişiklik: kural kataloğu
`yasal` ve `kabul_edilebilir` sütunlarını kazandı. Bu olmadan iki onaylı karar
(K-10 kabul edilmiş ihlal, K-16 yayın kapısı) **uygulanamıyordu** — sistem
hangi ihlali kabul etmeye izin vereceğini bilemiyordu.

| Ne | Sayı |
|---|---|
| Sınıflandırılan kural | 16 Eylül'de **35** · `SAGLIK_KISITI` kaldırılınca **34** · K-32'nin dört mola kuralıyla **38** (25 Eylül) |
| Yeni kural | 1 — `GECE_POSTASI_DEVRI`. (`SAGLIK_KISITI` de eklenmişti, **25 Eylül'de geri alındı** — K-21) |
| Türü/değeri/anlamı değişen | 3 — `MOLA_KAPSAMASI` yumuşadı · `GUNLUK_AZAMI` 9→11 · `TERCIH_KARSILAMA` |
| Yeni veri alanı | 13 |
| Düzeltilen tutarsızlık | 11 (T-1…T-11) |
| Yeni ürün kararı | 9 (K-18…K-26) |

**Mevzuat araştırması yapıldı** (`02-spec/v1.4-hazirlik/`): iki belirsizlik
birincil kaynaklardan çözüldü, katalogda **olmayan bir yasal kural** bulundu
(`GECE_POSTASI_DEVRI`), ve gece 7,5 saat sınırının **turizm istisnası** ortaya
çıktı — ilk müşteri verisi bir seyahat acentesine ait olduğu için bu teorik
değil, ilk gün karşımıza çıkacak bir konu.

⚠ **Yasal sınıflandırma hukuk uzmanı tarafından teyit edilmedi** (A-16).
Madde numaraları birincil mevzuattan okundu, yorumlar yapay zekâya ait.

**Altın senaryolar ONAYLANDI (15 Eylül).** Spec §16.3'teki A1–A12'nin beklenen
sonuçları Türkçe kabul cümlelerine çevrildi ve Mustafa tarafından **tek tek
onaylandı**: `08-motor-testleri/v5/KABUL-OLCUTLERI.md` (dondurulmuş).
Onay turunda **on ürün kararı** doğdu (K-8…K-17), **bir karar geri alındı**
(K-1), dört senaryo ve ortak sahne **baştan yazıldı**.

✅ **Motorun ilk iki davranışı artık korunuyor (16 Eylül).** A4 (gece yarısını
aşan vardiya) ve A8 (öğle arası) yeşile döndü — kabul ölçütü bu iki senaryoda
taahhüt olmaktan çıkıp **bekçiye** dönüştü. Kalan on senaryo hâlâ taahhüt:
beşi çözücü bekliyor, dördü backend, biri (A5) ertelendi.

**Devir denetimi artık betik (14 Eylül) ve 16 Eylül'de İLK KEZ gerçekten
koştu.** `DENETIM.py` — bu paketteki test adlarını, sayıları, dosya yollarını,
sürüm atıflarını ve commit durumunu makineye kontrol ettirir.

İlk gerçek koşusunda **17 hata** buldu: iki dokümandaki 17 atıf hâlâ
dondurulmuş **v2** ve **v4** sürümlerini gösteriyordu. O düzeltmeler aslında
yapılmıştı ama makineye hiç gönderilmemişti — ve **dosya boyutu değişmediği
için** (`v2` ile `v5` aynı uzunlukta) hiçbir boyut kontrolü bunu yakalayamazdı.
Hepsi düzeltildi. Kalan 14 uyarı tarihsel dosyalarda.

⚠ **23 Eylül'de bu cümlenin kendisi bir bulguya dönüştü.** *"Aksiyon
gerektirmiyor"* doğru ama eksik: o 14 uyarı, iş düşen uyarılarla **aynı
listede** ve *"bakılmalı"* başlığı altında basılıyor. Her koşuda akan aynı 13
satır, uyarı bloğunu okunmaz hale getirir — ve o blokta bir gün gerçek bir şey
belirdiğinde görünmez. Kayıt: **T-41**.

⚠ **Her oturumun sonunda koşturulmalı.** Göz bu 17 satırı üç oturumdur
görmedi; betik ilk koşuşunda gördü.

**Çalışma biçimi kararı (15 Eylül).** Yazan pencerenin yanına **yazmayan** bir
gösterge penceresi açılıyor: günlükler sürekli, testler talep üzerine — §5b.
Paralel ikinci **yazıcı** ajan (opencode vb.) **reddedildi**; R5'i yeniden
açıyor. Salt-okunur inceleyici Aşama 2'ye ertelendi, ölçüm şartıyla.
**Ürün kodu değişmedi, test eklenmedi.** Gerekçe:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

### 28 Eylül — gerçek ölçek ilk kez denendi

Gün mola modelini bitirmekle başladı, **350 kişilik bir organizasyonun
planlanmasıyla** bitti. Mustafa'nın isteği açıktı:

> *"Test senaryolarını 15-20 kişilik bir ekip düşünerek yapıyorsun hep…
>  Kullanmadığımız hiçbir kural veya kriter olmamalı."*

Haklı çıktı. Bugüne kadarki en büyük sahne **10 kişi, 1 ekip, 3 şablon**
idi. Üç ekipli gerçekçi sahne kurulunca **altı ayrı bulgu** bir saat içinde
ortaya çıktı — hepsi kodda aylardır duruyordu.

| önce | sonra |
|---|---|
| en büyük sahne 10 kişi | **350 kişi**, 3 ekip, 14 şablon, 39 kural |
| 24 kuraldan **7'si** gerçekten sınanıyordu | **hepsi** (24 kuralın 24ü) kırmızı yanabiliyor |
| çözümsüzlük **292 saniyede** bildiriliyordu | **10 saniyede**, hücre adıyla |
| çözücü iyileşme durduğunda **bütçeyi bitiriyordu** | durgunlukta kendi durur |
| 350 kişide **bellek yetmiyordu** | 435 MB, çözülüyor |

**Kapanış ölçümü (350 kişi):** 1.757 atama · **0 sert ihlal** · %100 asgari
kapsama · %98,8 hedef kapsama · 0 saat fazla mesai · optimuma **%10** uzak.

#### Günün dersi — altı kez aynı şey

Ölçmeden kurulan mantık **altı kez** yanlış çıktı ve altısında da ölçüm
düzeltti. İkisi ürün tarafındaydı (Mustafa yakaladı), dördü mühendislik.

Daha önemlisi: **üç test, yazıldığı anda yeşildi ve ölçmek istediğini hiç
ölçmedi** — sahne küçük olduğu için. Biri de eski davranışı kural sanıp
**yanlış mantığı sabitliyordu**. Test yeşil olması bir şey kanıtlamaz;
neyi kırmızı yaktığı kanıtlar.

#### Motorun iyi tarafı da ölçüldü

Veri setini kurarken **dört ayrı veri hatası** yapıldı. Motor üçünü yakaladı
ve doğru yeri gösterdi; yalnız biri sessizce geçti (tanınmayan bir **değer**,
T-45). Yani motor sanılandan iyi durumda; zayıf olan test verisiydi.

### 29 Eylül — set baştan kuruldu, dört karar, iki yeni bulgu

Gün 350 kişilik seti otomatik koşuya bağlamakla başladı, **500 kişilik iki
yeni set** ve dört ürün kararıyla bitti.

**Kırılma noktası Mustafa'nın uyarısıydı.** 28 Eylül'de seti *"en zor
senaryo"* diye anlatmıştım. Ölçülünce öyle olmadığı çıktı:

| ne yazmıştım | ölçülen |
|---|---|
| 39 kuralın hepsi uygulanıyor | **15'inin gövdesi hiç yazılmamış** |
| kurallar sınanıyor | **13'ü hiç zorlanmıyor** |
| gerçekçi kadro | kapasite talebin **2,3 katı** — kimse sıkışmıyor |
| 45 saatlik sözleşme | hiçbir şablon kombinasyonu 45 etmiyor |

> *"Beni yanılttın. Patlasa da çatlasa da en zor senaryo ile test etmeliyiz…
>  Konuyu çözmek için problemi daraltma bir daha!!! Beni memnun etmeye
>  çalışma, problemlere odaklan. Beni yanıltmanın bedeli en ağır!"*

Bu, §6'ya **7. ve 8. çalışma kuralı** olarak yazıldı.

**Dört karar** (ayrıntısı `00-DEVIR/08-URUN-KARARLARI.md`):

| | ne değişti |
|---|---|
| **K-37** | Süre dolduğunda motor *"çözümsüz"* **demiyor** — `sure_yetmedi` diyor ve teşhis **koşmuyor**. Kullanıcı isterse *"neden olduğunu araştır"* der; o cevapta *kanıtlanmadığı* yazılı. **T-23 ve T-48 kapandı** |
| **K-38** | Haftalık 45 saat **normal** çalışma sınırı, toplam tavan değil. Fazla mesai yolu tanımlıydı ama **hiç açılamıyordu** |
| **K-39** | Tam zamanlının sözleşme saati **doldurulur** (izin oranında düşer; yeni alan `gun_sayisi`). Yarı zamanlıya kişi başı saat **girilmez**, tavan mevzuattan gelir |
| **K-40** | *"Bu kişi gece vardiyası yapamaz"* ve *"bu vardiya gece vardiyasıdır"* artık **işaret**. Tahmin işareti **ezmez** |

**Yeni veri seti:** 500 kişi · 17 şablon · 40 kural · 19.630 kişi-saat
kapasite · iki doluluk (%85 ve %95, tek fark talep tablosu). Mustafa'nın
gerekçesi: *"%85 demek 'fazladan %15 elemana sahibim' gibi bir ifadeyi
doğurabilir. Türkiye'de genelde eleman yetmiyor, fazla mesaiye gidiliyor."*

**Set kurulurken üç hata buldu:** çözücü ile doğrulayıcı *"net saat"*i farklı
hesaplıyordu (geçerli planda **28 sert ihlal**), kesirli vardiya bitişi
doğrulayıcıyı **çökertiyordu**, ve K-38 doğrulayıcı tarafına uygulanmamıştı.
Üçünü de **veri seti** buldu, test paketi bulmadı.

**Tam ölçek ilk kez çözüldü** — ve asıl soruyu açtı:

| | |
|---|---|
| model | 638.572 değişken · 754.633 kısıt |
| süre | kurma 51 sn · çözüm **1.078 sn** (900 istenmişti) |
| sonuç | 2.493 atama · **0 sert ihlal** · `yayınlanabilir` **True** |
| kalite | optimuma **%98,3** uzak (eski 350 kişilik set aynı bütçede %10) |

Yani **yasal ve sözleşmesel taraf temiz, kalite neredeyse yok.** İki yeni 🔴:
**T-59** (verilen süre bütçesi aşılıyor — mekanik, karar gerektirmiyor) ve
**T-60** (kalite yok — ⚠ sebebi henüz ayrılmadı, önce dört ölçüm).

#### Günün dersi — dört kez aynı şey

Bugün dört kez **ölçmeden yazdım**: 117 saniyeyi *"beklenen ~2 dakika"* diye,
iki çekirdekli tek ölçümü genel kural diye, ölçüm aracında ürünün hiç
kullanmadığı bir ayarı ölçerek, ve veri setini *"hepsini kapsıyor"* diye.
Dördünü de ölçüm ya da Mustafa düzeltti.

Ve **mutasyon iki boşluk yakaladı**; ikisi de benim yazdığım, sonunda
`assert True` bulunan testlerdi — yani yeşil yanıyor, hiçbir şey ölçmüyordu.

---

## 3. Sıradaki tek adım

> **Dış incelemenin 🔴 bulguları — yeni özellikten önce.**
>
> 16 Eylül'de proje başka bir modele (GPT) şartnameyle birlikte **üç turda**
> incelettirildi. **19 bulgu** çıktı, hepsi bizim tarafımızda **ölçülerek**
> doğrulandı; ayrıca iki yanlış iddiamız düzeltildi. Dokuzu 🔴 ve **yeni iş
> bunların önüne geçmemeli.**
>
> **Sıralama ölçütü: yanlış karar riski.**
>
> | Sıra | Ne oluyor | Karar gerekiyor mu |
> |---|---|---|
> | ~~T-27~~ | ✅ **KAPANDI 16 Eylül** — mola artık vardiyaya kırpılıyor ve üst üste binenler birleştiriliyor. 8 test | — |
> | ~~T-35~~ | ✅ **KAPANDI 23 Eylül** — gerçek istemci IP'si + güvenilen vekil listesi. Etkisi kayıtta *kiracı* yazıyordu, **kurulum çapında** çıktı | — |
> | ~~T-34~~ | ✅ **KAPANDI 23 Eylül** — beş katmanda 16 yer; sır yoksa uygulama açılmıyor. Kırmızı kanıt `fix/t34-sirlar` dalında | — |
> | ~~T-22~~ | ✅ **KAPANDI 23 Eylül** — çözümsüzlükteki taslak artık **özgün** girdiyle denetleniyor; boş plan `var: False`. 4 test | — |
> | ~~T-19~~ | ✅ **KAPANDI 23 Eylül** — şartname biçimi kazandı; talep beş yerde hücre başına okunuyor. Yeni kanal `okunmayan_alanlar`. 5 test, **beşi de kırmızı yandı** | — |
> | ~~T-28~~ | ✅ **KAPANDI 30 Eylül, K-42** — iki taraf da geçmişi okuyor; ölçüldü: geçmişsiz 27 yasal ihlal, geçmişle 0 | — |
> | ~~T-75~~ | ✅ **KAPANDI 30 Eylül gecesi, K-46** — hafta sonu = iki gün de; üçüncü hafta çözüldü, 0 ihlal | — |
> | ~~T-72~~ | ✅ **KAPANDI 30 Eylül gecesi, K-45** — gece haftası = saatlerin yarısından çoğu | — |
> | ~~T-74~~ | ✅ **KAPANDI 30 Eylül gecesi, K-44** — gece postasının bütün süresi; Yargıtay 9. HD 2020/17967 | — |
> | ~~T-78~~ | ✅ **KAPANDI 1 Ekim gecesi** — 20 dk mola çeyreğe sığmıyordu, molalar 5 dk üst üste biniyordu; üç yerde düzeltildi, 9 test + 6 mutasyon. Sabah koşu tekrarı: 0 sert beklenir | — |
> | **T-59 sorusu** 🆕 | *"En fazla 900 sn"* deyip 958 sn: model kurma (~55 sn) bütçenin dışında | ✅ bütçe duvar saati mi olsun (K-48 adayı; öneri: evet) |
> | **T-38** 🆕 | Şartnamenin **on iki alanı daha** karşılıksız. En ağırı `kural_degerleri`: kişiye özel sözleşme sınırı yok sayılıyor, günde 9 saatlik sözleşme 11 saate planlanabiliyor | ✅ hangisi önce yazılacak |
> | ~~**T-29**~~ | ~~`DONMUS_GUN` yalnız `_yeni` işaretli atamada ateşleniyor, o işareti **kimse üretmiyor**~~ ✅ **KAPANDI 1 Ekim, K-54** — işaret yok, `mevcut_plan` ile karşılaştırma | — |
> | **T-21** | Çok ekipli çalışan iki ekibi aynı anda dolduruyor — modelde ekip boyutu yok | ✅ bir vardiyada tek ekibe mi sayılır |
> | **T-18** | Gövdesi yazılmamış aktif SERT kural yayını engellemiyor. ⚠ Artık **üç** kanal bu kapıda bekliyor: `uygulanmayan_kurallar`, `eksik_boyutlar`, `okunmayan_alanlar` | ✅ kapı ne yapmalı |
> | ~~T-59~~ | 🟡 **DÜZELTİLDİ 30 Eylül akşamı** — birinci aşama bütçenin içinden pay alıyor, ana çözüme kalan veriliyor; tam ölçekte (900 sn) yeniden ölçülmedi | — |
> | **T-60** 🆕 | Tam ölçekte plan üretiliyor ama optimuma **%98,3** uzak. Yasal taraf temiz, kalite yok | ⚠ önce **dört ölçüm**, sonra karar |
> | **T-54** 🆕 | Saatin **maliyeti yok**: çözücü fazladan saat yazmaktan çekinmiyor (%85 dolulukta 49 kişiye 124 saat fazla mesai) | ✅ `HEDEF_ASIMI` gibi yumuşak bir kural mı, ücret terimi mi |
> | ~~T-44~~ | ✅ **KAPANDI 28 Eylül** — K-34 ile zaman birimi çeyrek saate indi; eşik `4F → 12F/7` (taban 3 için 12 kişi yerine **6**). Çözüm süresi 40 kişide 0.78 sn | — |
> | ~~T-23~~, ~~T-48~~ | ✅ **KAPANDI 29 Eylül, K-37** — *"süre yetmedi"* ile *"imkânsız"* ayrıldı; teşhis artık yalnız istenirse koşuyor | — |
>
> **Sekiz 🔴 açık.** Altısı Mustafa'nın cevabını bekliyor (T-28, T-38, T-29,
> T-21, T-18, T-54); **T-59 mekanik** ve karar gerektirmiyor; **T-60** karar
> değil önce **ölçüm** istiyor.
>
> ⚠ **Sıra Mustafa'nın verdiği sıradır:** *"Gece işareti → iki veri seti →
> eksik kurallar → testleri tekrarlarız."* İlk ikisi 29 Eylül'de bitti;
> şimdi **eksik kuralların gövdeleri** (14 kural) geliyor. İçlerinde
> **rol kapsaması** ve **yetkinlik kapsaması** çözücüde var, doğrulayıcıda
> yok — yani motor kendi işini kendi onaylıyor (§7.6'nın tam tersi).
>
> **İki küçük onay da bekliyor:** §11.3 çıktısına eklenen `okunmayan_alanlar`
> (commit'e girdi; itiraz gelirse tek blok çıkar) ve **T-41**'in `DENETIM.py`
> yaması (kod değişmedi, `DENETIM.py` her şeyin bekçisi olduğu için onay
> istiyor).
>
> ### Neden bunlar önce
>
> Dış incelemenin sözü: *"önce yanlış yayın izni ve sessiz veri atlama
> sorunları, sonra tamamlanma tablosu."* Katılıyoruz. Dokuzu da **sessiz**
> hatalar: hiçbiri kırmızı yanmıyor, hepsi planı temiz gösteriyor.
>
> ### ⛔ Bozulmaması gereken kural
>
> Şartname §7.6 ve §16.1: **doğrulayıcı çözücüyle mantık paylaşmaz.**
> `09-motor/cozucu/` ve `09-motor/dogrulayici/` birbirini **import etmez**;
> `09-motor/orkestra.py` ikisini de import eder ve bu doğrudur.
> `09-motor/testler/test_bagimsizlik.py` bunu koruyor.
>
> ⚠ **T-19 bu kuralın sınırını gösterdi ve ders kapandıktan sonra da
> geçerli:** bağımsızlık kural *mantığını* ayırıyor, **girdi yorumunu**
> ayırmıyor. İki taraf da aynı fikstür geleneğiyle okuyordu ve o gelenek
> şartnameyle uyuşmuyordu — ikisi birbiriyle tutarlı, ikisi de yanlıştı.
>
> Çözüm ortak modül **değildi**: talep artık üç yerde ayrı ayrı okunuyor ve
> `okunmayan_alanlar` *"neye bakmadım"* sorusunu cevaplıyor.
> `09-motor/testler/test_bagimsizlik.py` ortak yardımcı modülü hâlâ yasaklıyor.
>
> ⚠ **T-32 aynı sınırın ikinci örneği ve onu bugün ben açtım:** K-30'u
> yazarken fazla mesai tavanını çözücüde **profil tablosundan**, doğrulayıcıda
> **kural parametresinden** okur hâle getirdim. İkisi bugün aynı sayıyı
> veriyor; kiracı parametreyi değiştirdiği gün sessizce ayrışırlar.
>
> ### ⛔ Commit öncesi içerik karşılaştırması (O-9)
>
> Dosyalar karşı taraftan çekilip **içerikçe** karşılaştırılır. Hafızaya
> değil `cmp`'ye güvenilir. Boyut eşitliği de yetmez.
>
> ✅ **Tamamlananlar:** fikstürler · test iskeleti · şartname v1.4 · kural
> sınıflandırması · mevzuat araştırması · bağımsız doğrulayıcı · çözücü ·
> onarım döngüsü · plan profilleri · **CI kapısı (yeşil)**.
> A-15, A-17, A-18, T-12, T-14, T-15, T-17 kapandı.
> Dış incelemeden: **T-27** (16 Eylül) · **T-22, T-34, T-35, T-19** (23 Eylül).
> K-27, K-28, K-29, K-30 karara bağlandı — **ama K-28 kodda eksik (T-24a).**
>
> **Paralelde açık kalanlar:**
>
> - **T-24, T-25, T-26** — ikinci turun kalan bulguları (**T-23** 29 Eylül'de K-37 ile kapandı)
> - **T-30, T-31, T-32, T-33, T-36** 🟡 — üçüncü turun kalan bulguları
> - **T-39, T-40, T-41** 🟡 — 23 Eylül kapatma turunun açtıkları.
>   **T-39** talep ekranı yazılmadan önce karara bağlanmalı (kapı şartı);
>   **T-40** `tercih_karsilama_yuzde` üretilmiyor — T-38'in `tercihler`
>   satırına bağlı; **T-41** `DENETIM.py` uyarı çıktısının ayrıştırılması
> - **T-20** — M0 testinin kapsamı; A-1'i kapatan test, doğrulanmalı
> - **T-13** — `ADALET_DENGESI`'nin `saat` boyutu
> - **`/suggest` (§11.5)** — ⚠ **kabul ölçütü yok, fikstürü yok.** Kod
>   yazmadan önce *"doğru çalışıyorsa ne görmeliyiz"* cümleleri yazılıp
>   onaylanmalı — A7'de bu adımın atlanmasının bedeli görüldü.
> - **A-16 hukuk teyidi** — madde numaralı tablo hazır, uzman bakacak.
> - **A-13 kapsam envanteri** — Ocak hedefi ölçülmedi. Ayrı pencere işi.
> - **`07-motor/` yeniden adlandırma** — `08-analiz/` adı `08-motor-testleri/`
>   ile çakışır; örneğin `10-analiz/`.
> - ✅ **`DENETIM.py` her oturum sonunda koşturulmalı:**
>   `cd C:\Users\PC\Desktop\Tshift` sonra `py DENETIM.py`.
> - **A-6 mutasyon raporu** — kırmızı kanıt turu elle seçilen kırılmalarda
>   12/12 yakaladı ama **dış inceleme 19 bulgu buldu**; otomatik mutasyon
>   hâlâ yok ve iç kanıtın sınırı görüldü.
> - A-2 ve A-3 eksik bekçiler.
>
> Tam öncelik listesi: `06-ACIK-RISKLER.md` sonundaki tablo.

---

## 4. Okuma sırası

Aşağıdaki sıra, bir işe başlamadan önce ne kadar okuman gerektiğini söyler.
**Hepsini okumak zorunda değilsin** — yapacağın işe göre seç.

| Sıra | Dosya | Ne zaman okumalısın |
|---|---|---|
| 1 | Bu sayfa | Her zaman |
| 2 | `02-DEGISMEZLER.md` | **Her zaman.** Kod yazmadan önce mutlaka. |
| 3 | `01-PROJE-KIMLIGI.md` | Ürün kararı, kapsam ya da öncelik konuşulacaksa |
| 4 | `03-MIMARI-KARARLAR.md` | Mevcut bir yapıyı değiştirecek ya da yeni katman ekleyeceksen |
| 5 | `04-TEST-HARITASI.md` | Test yazacak ya da mevcut bir testi değiştireceksen |
| 6 | `05-HATA-OTOPSILERI.md` | Yeni bir savunma/kontrol tasarlayacaksan |
| 7 | `06-ACIK-RISKLER.md` | Yayına çıkma, ölçek ya da güvenlik konuşulacaksa |
| 8 | `08-URUN-KARARLARI.md` | **Bir ürün davranışının neden böyle olduğunu soruyorsan.** K-serisi: verilmiş kararlar, gerekçeleriyle |
| 9 | `oturumlar/` | Belirli bir değişikliğin ne zaman ve neden yapıldığını arıyorsan |

### Deponun tamamı — nerede ne var

> **Bu klasör (`00-DEVIR/`) şartnameyi, demoyu ya da kodu İÇERMEZ; onlara
> İŞARET EDER.** Devir paketi bir harita, arşiv değil. Aşağıdaki tablo o
> haritanın tamamıdır.

| Yol | İçerik | Ne zaman aç |
|---|---|---|
| **`02-spec/v1.4-master-spec.md`** | **YÜRÜRLÜKTEKİ ŞARTNAME — 17 bölüm, son karar.** §3 roller ve yetki matrisi · **§5.3 `yasal` / `kabul_edilebilir` ayrımı** · §6 kural kataloğu (**38 kural**, yasal ve kabul sütunlarıyla, madde dayanaklarıyla) · §6.3 gece yarısını aşan vardiya + **sektör istisnası** + DST modeli · §8 veri modeli · §9 ekranlar · **§11 motor sözleşmesi** (`/solve`, `/evaluate`, çözümsüzlük teşhisi, **`en_iyi_plan`**, §11.2 lookback, §11.7 idempotency + onarım) · **§16 test stratejisi ve 12 altın senaryo** · §17 sürüm notları. | **Motor, kural ya da ekran işine başlamadan ÖNCE.** v1.0–v1.3 aynı klasörde, **dondurulmuş** (geçmiş korunuyor). Hazırlık notları `02-spec/v1.4-hazirlik/`. |
| **`02-spec/v0-koken-...Analiz_v2.docx`** | **KÖKEN DOKÜMANI — 27 bölüm.** Projenin doğduğu analiz. Master Spec'in kapsamadığı yerde **hâlâ kaynak**: §8 sektörel kural paketleri (çağrı merkezi/perakende/üretim) · §23 Faz 0–10 geliştirme planı · §25 12 haftalık yol haritası · §20 riskler. | Gerekçe, fazlama ya da sektör paketi sorusu varsa. **Çeliştiğinde Master Spec kazanır** (§17). |
| `03-demo/v2-html/tshift-demo-v2.html` | **Çalışan demo** — 15 ekran, iki operasyon (çağrı merkezi + otel), sürükle-bırak takvim. Tek HTML dosyası, tarayıcıda açılır. | Ekran tasarımı ya da akış konuşulacaksa. Ürünün görsel dili burada. |
| `01-spike/` | **Motor fizibilite testleri** (7–8 Eylül) — CP-SAT vs greedy karşılaştırması, ölçek testleri (200→2000 kişi), otel senaryosu. Kronoloji ve ölçülen sayılar `01-spike/README.md`'de. | Motor yazılmadan **önce mutlaka.** Teknoloji kararının dayanağı burada. |
| `04-kod/` | **Çalışan uygulama** — backend (.NET 10), frontend (Next.js 16), veritabanı betikleri, testler, Docker | Kod yazılacaksa |
| `05-inceleme/v1-2026-09-11/` | **Yılmaz'a gönderilen inceleme paketi** — 8 soru, 4 hata otopsisi, bilinen açıklar | Dış inceleme konuşulacaksa |
| `06-veri/` | **Gerçek müşteri verisi** (PDKS + plan) ve türetilen çıktılar. ⚠ **`.gitignore` içinde — git'e girmez.** | Veri analizi yapılacaksa |
| `07-motor/` | ⚠ **Motor YOK.** Geçmiş planları ölçen analiz betikleri. Bkz. `07-motor/OKU-BENI.md` | — |
| **`08-motor-testleri/`** | ✅ **Motor var; 7 altın senaryo koşuyor ve yeşil, 4'ü (A2/A10/A11/A12) backend tarafında koşmuyor.** Şartnameden türetilmiş **kabul senaryoları** (A1–A12): motorun ne yapması gerektiğinin, motor yazılmadan önce ve motora bakmadan yazılmış hâli. **`08-motor-testleri/v5/` onaylanmış ve güncel**; v1–v4 dondurulmuş. İçinde: `KABUL-OLCUTLERI.md` (onaylı cümleler) → `08-motor-testleri/v5/fikstur/` (11 JSON + ortak sahne) → `08-motor-testleri/v5/testler/` (pytest çatısı + `08-motor-testleri/v5/testler/backend-taslak/` C# taslakları). Onay turunun özeti `ONAY-DURUMU.md`'de. Bkz. `08-motor-testleri/OKU-BENI.md` ve `08-motor-testleri/v5/testler/OKU-BENI.md` | Motor ya da doğrulayıcı işine başlamadan **ÖNCE** |
| **`05-inceleme/beceriler/`** 🆕 | **İncelemenin nasıl yapılacağı** — dört dosya. Haftalık dış tarama döngüsü: kim ne yapar, paket nasıl hazırlanır, ne bulgu sayılır. `00-DEVIR/` **bağlamdır** (neyi bilmen gerek), burası **beceridir** (işin nasıl yapılacağı) | Haftalık tarama öncesi; yeni bir inceleme yapılacaksa |
| **`09-motor/`** | ✅ **MOTOR — çalışıyor.** Üç parça: `09-motor/dogrulayici/` (denetler, **37** kural gövdesi), `09-motor/cozucu/` (CP-SAT ile üretir), `09-motor/orkestra.py` (§11.7 onarım döngüsü). **481** birim testi (1 Ekim akşamı). **`/suggest` hâlâ yok** — bilerek 501 dönüyor. ⛔ Çözücü ile doğrulayıcı birbirini import ETMEZ (§7.6); `09-motor/testler/test_bagimsizlik.py` bunu koruyor. Bkz. `09-motor/OKU-BENI.md` | Motor ya da doğrulayıcı işine başlamadan önce |
| **`DENETIM.py`** | **Devir paketi denetimi.** §5'teki ritüelin 5. maddesini makineye yaptırır. `py DENETIM.py` | Devire "tamam" demeden önce, her seferinde |
| `00-arsiv/` | Dondurulmuş eski sürümler | Geçmiş aranıyorsa |
| `DEGISIM-GUNLUGU.md` | Kilometre taşları, en yeni en üstte | "Ne zaman ne değişti" |
| `RISKLER-VE-ONLEMLER.md` | 15 hata sınıfı, savunma hatları, **kırmızı çizgiler §6** | Veri/sır/migration'a dokunmadan önce |
| `SURUMLEME.md` | Hata yapılırsa nasıl geri dönülür | Bir şey bozulduğunda |
| `KALITE-ARASTIRMASI-DEGERLENDIRME.md` | Sahanın kalite pratiklerinin bu projeye göre değerlendirmesi | Test/süreç tasarımı yapılacaksa |

**Git etiketleri** `v0.1-kiracilik` … `v0.8-devir` — her kilometre taşı
işaretli, geri dönülebilir.

---

## 5. Bu dokümanların çalışma kuralı

Bu klasör bir **özet** değil, bir **devir paketidir**. İki farklı şey:

- Özet, benim yazdığım düz yazıdır. İçinde bir yanlış varsayım varsa sonraki
  pencereye sessizce taşınır ve orada doğru sanılır.
- Devir paketi **doğrulanabilir** olmak zorundadır. Bu yüzden buradaki her
  iddia ya bir **test adına**, ya bir **dosya yoluna**, ya da bir
  **çalıştırılabilir komuta** bağlıdır.

**Kural:** Bu klasöre, karşılığında çalıştırılabilir bir kanıt gösteremediğin
hiçbir cümle yazılmaz. Kanıtı olmayan bilgi `06-ACIK-RISKLER.md` altına,
"kanıtlanmamış" etiketiyle gider.

### Güncelleme ritüeli

> **Tetikleyici değişti (16 Eylül).** Önceki kural şuydu: *"Mustafa 'aktarım
> dosyasını güncelle' dediğinde."* Yani güncelleme **birinin hatırlamasına**
> bağlıydı — ve hatırlamaya bağlı bir bekçi, bekçi değildir (O-1'in tam
> tarifi). Yerine üç somut an kondu.

| Ne zaman | Ne güncellenir |
|---|---|
| **Aynı commit'te** | Bir karar verildi, bir kural yazıldı, bir madde kapandı → `08-URUN-KARARLARI.md`, `06-ACIK-RISKLER.md` ve ilgili `02`–`07` dosyası. **Kod ile doküman aynı commit'te gider** |
| **İş parçası bitince** | `oturumlar/YYYY-AA-GG-<is-parcasi>.md` |
| **Oturum ya da pencere kapanırken** | Bu sayfadaki iki bölüm + `DEGISIM-GUNLUGU.md` + `DENETIM.py` |

**Neden en önemlisi ilki.** Oturum **her an** bitebilir: bağlam dolar, makine
uyur, insan yorulur. Doküman koddan geriden geliyorsa bir sonraki pencere
**yanlış haritayla** başlar. §5'in kuralı *"kanıtı olmayan cümle yazılmaz"*
diyor; aynanın öteki yüzü de geçerli: **kanıt değişti ama cümle değişmediyse
doküman yalan söylüyor.**

16 Eylül bunun küçük bir örneğini verdi: A7'nin onaylı kabul cümlesi
(*"Ç01–Ç03 en müsait olanlar"*) fikstüre hiç çevrilmemişti. Cümle onaylıydı,
fikstür ona uymuyordu ve boşluk **ancak motor yazılınca** göründü.

Adım adım:

1. `oturumlar/YYYY-AA-GG-<is-parcasi>.md` dosyası yazılır — o oturumda
   **hangi dosya neden değişti, hangi test eklendi, hangi karar verildi,
   hangi öneri REDDEDİLDİ.** Bu dosyalar **asla yeniden yazılmaz.**
2. Değişen şeye göre `02`–`07` arası ilgili dosyalar güncellenir.
3. Bu sayfadaki **"Şu anda neredeyiz"** ve **"Sıradaki tek adım"** bölümleri
   yenilenir. Bu iki bölüm her zaman güncel olmak zorundadır — devir
   paketinin geri kalanı bu ikisi yanlışsa işe yaramaz.
4. `DEGISIM-GUNLUGU.md`'ye kilometre taşıysa satır eklenir, etiket atılır.
5. **DENETİM — atlanmaz, ve artık elle yapılmıyor:**

   ```
   cd C:\Users\PC\Desktop\Tshift
   py DENETIM.py
   ```

   Yedi kontrolü makine yapar: test adlarının `DisplayName` ile birebir
   eşleşmesi, sayı tutarlılığı, dosya yollarının varlığı, değişmez özet
   tablosu, günlük adlandırması, değişim günlüğünün tazeliği ve **commit
   edilmemiş devir dosyası** olup olmadığı. Çıkış kodu 0 değilse devir
   "tamam" değildir.

   Betiğin yapamadığı iki şey elde kalır:
   - **Ölçüm değiştiyse tahmin edilmez, yeniden koşulur.**
   - Betik *tutarlılığa* bakar, *doğruluğa* değil. Tutarlı bir yanlış yine
     yakalanmaz; onu ancak iddiayı kaynağıyla karşılaştırmak yakalar.

> ⚠ **Yazdım ≠ gönderdim ≠ commit ettim ≠ karşı tarafta değişti ≠ göndermem
> gerektiğini fark ettim.** Beşi ayrı adımdır ve beşi de doğrulanır.
>
> 14 Eylül'de Mustafa'nın kapsam kararlarının tamamı yerel kopyada
> güncellenmiş ama makineye hiç gitmemişti (`oturumlar/2026-09-14-veri-analizi.md`
> §10). 16 Eylül'de son halka eklendi: bir düzeltme **hiç gönderilmemişti** ve
> iki tarafta da hiçbir şey kırmızı yanmıyordu — git temiz, `DENETIM.py`
> *"commit bekleyen 0"*, testler yeşil; çünkü her iki taraf **kendi içinde**
> tutarlıydı ve tutarsızlık **aralarındaydı** (`05-HATA-OTOPSILERI.md` O-9).
>
> **Bekçi:** commit öncesi dosyalar karşı taraftan çekilip **içerikçe**
> karşılaştırılır. Hafızaya değil `cmp`'ye güvenilir. Boyut eşitliği de
> yetmez — 15 Eylül'de `v2`→`v5` 17 bayat atıf, dosya boyutları **birebir
> aynıydı**.

---

## 5b. PENCERE PROTOKOLÜ

**Karar: 14 Eylül 2026.** Uzun sohbetlerde bağlam kaybını önlemek için iş,
pencereler arasında devredilir. Kurallar:

### Ritim: iş parçası başına bir pencere, SIRALI

Motor sözleşmesi bir pencere, CI+testler bir pencere, ekranlar bir pencere —
ama **hepsi sırayla.** Aynı anda **tek aktif pencere** olur.

| Durum | Ne yapılır |
|---|---|
| Yeni ve ilgisiz iş parçası | **Yeni pencere.** Bu sayfayı oku, devam et. |
| Aynı işin küçük devamı | Aynı pencerede kal |
| Sohbet uzadı / yavaşladı | Günlüğü yaz, yeni pencere |
| **Aynı hata iki kez düzeltildi** | **Dur.** Bağlamın kirlendiğinin en net işareti. |
| Doküman ile kod çelişiyor | Kod yazma; hangisinin doğru olduğunu Mustafa'ya sor |

### Açılış beyanı — yeni pencere işe başlamadan önce

> **Yeni pencere, dosya yazmadan önce şunu söyler:** hangi dosyaları okudum,
> sıradaki adımı nasıl anladım, hangi varsayımla başlıyorum.

**Neden (karar: 14 Eylül 2026):** Aşağıdaki tablo *"doküman yanlış başlarsa
yakalamaz"* diyor ve bu açık kapalı değildi. Testler başlangıcı yönlendirmez,
doküman da yanlış anlaşılmayı göremez. Açılış beyanı **Mustafa'nın**
görebileceği tek an: iş yapılmadan önce.

Bedeli bir mesaj, getirisi yanlış yöne gidilmiş bir oturum. 14 Eylül'de
kendiliğinden yapıldı ve işe yaradı — şartnamedeki bir çelişki daha ilk
mesajda görüldü.

### Yazma hakkı

> **Aynı anda yalnız bir pencere dosya yazar ve commit eder.**
> Devredilen pencere **salt-okunur** olur: soru cevaplayabilir, dosya yazamaz.

Devredilen pencere hemen kapatılmaz — **geri dönüş yoludur.** Yeni pencere
devir paketini okuyup işe başladığını gösterene kadar açık kalır. Devir eksik
çıkarsa oraya dönülüp tamamlanır.

### Geri bildirim yüzeyleri — iki pencere, biri yazmaz

**Karar: 15 Eylül 2026.** Gerekçe, elenen alternatif ve kanıt durumu:
`oturumlar/2026-09-15-calisma-bicimi-opencode.md`.

Aktif pencerenin yanında **ikinci bir pencere** açılır. Bu pencere ajan
değildir: dosya yazmaz, komut almaz, soru cevaplamaz. Yalnız **göstergedir.**
Amacı tek: kırmızıyı saatler sonra değil dakikalar içinde fark etmek.

| Yüzey | Komut (`04-kod` içinde) | Sürekli mi |
|---|---|---|
| **Sunucu günlükleri** | `docker compose logs -f` | ✅ Sürekli açık |
| **Testler** | `.\TEST.ps1` | ❌ **Talep üzerine** |

⚠ **Testler neden sürekli koşmaz:** §7'ye göre `TEST.ps1` API'yi **önce
durdurur.** Sürekli koşan bir test izleyicisi geliştirme kipindeki API'yi
sürekli düşürür. Başka depolarda gördüğünüz "sürekli koşan test penceresi"
kurgusu bu depoda **olduğu gibi kurulamaz.**

**Bunun doğurduğu kural — asıl madde budur:**

> **Ajan "bitti" demeden önce `.\TEST.ps1`'i kendisi koşar ve çıktısını
> rapor eder.** Test çıktısını pencereler arasında elle taşıyan insan,
> zincirin en zayıf halkasıdır.

**Ne DEĞİLDİR:** ikinci bir *yazıcı* ajan değildir. Paralel ajan modeli
(kod bir ajanda, hata ayıklama başka bir ajanda) 15 Eylül'de değerlendirildi
ve **reddedildi** — aşağıdaki tabloda R5 kapalıdır ve onu yeniden açacak
ölçülmüş bir gerekçe yoktur. Araç tarafı: `06-ACIK-RISKLER.md` ·
📌 Araç kararı.

**Kapı değil, hız.** CI (A-4) zaten kapıdır ve 14 Eylül'de yeşil yandı. Bu
karar yeni bir kapı eklemez; **kırmızının fark edilme süresini** kısaltır.
İkisi farklı şeylerdir, biri diğerinin yerine geçmez.

### Günlük dosyası adlandırma

Aynı gün birden çok oturum olabilir. **İki pencere asla aynı dosyaya
yazmaz:**

```
oturumlar/2026-09-14-veri-analizi.md
oturumlar/2026-09-15-motor-sozlesmesi.md
oturumlar/2026-09-15-ci-ve-testler.md     ← aynı gün, ayrı iş, ayrı dosya
```

İndeks dosyası **bilerek yok** — olsaydı çakışan dosya o olurdu. Kronolojik
sıra dosya adından çıkar.

**Paylaşımlı tek dosya bu sayfadır** (`00-BURADAN-BASLA.md`), çünkü "şu an
neredeyiz" tek yerde olmak zorunda. Onu yalnız **aktif** pencere günceller.

### Pencereler arası kopukluk — asıl güvence ne

Yılmaz'ın *"bloklar arası ilişki kopar"* itirazının pencere seviyesindeki
hâli. Cevap da aynı yerden gelir: **kopmayı engelleyemezsin, gürültülü
yaparsın.**

| Ne | Ne işe yarar | Neyi yaramaz |
|---|---|---|
| **Doküman** (`00-DEVIR/`) | Yeni pencerenin **doğru başlamasını** sağlar | Yanlış başlarsa yakalamaz |
| **Açılış beyanı** | Yanlış başlangıcı **iş yapılmadan** yakalar | Sessiz kalan varsayımı göremez |
| **`DENETIM.py`** | Dokümanın **kendi içinde tutarsızlığını** yakalar | Tutarlı bir yanlışı göremez |
| **Testler** (39 + M0–M6) | Bir ilişki bozulursa **kırmızı yanar** | Başlangıcı yönlendirmez |

**Asıl güvence testlerdir, doküman değil.** Doküman iyi niyeti taşır; test
yanlışı yakalar. Bu yüzden **CI (A-4) pencere protokolünün önkoşuludur:**
pencere değişince "testleri çalıştırmayı hatırlayan bağlam" ortadan kalkar,
ve tam o anda otomatik kapıya en çok ihtiyaç duyulur.

### Devirde bilinen riskler

| # | Risk | Önlem | Kapalı mı |
|---|---|---|---|
| R1 | Yazıya dökülmemiş sezgi kaybolur | Oturum günlüğü | 🟡 Tanım gereği tam kapanamaz |
| R2 | Verilmiş karar yeniden verilir | 02/03/06 + **reddedilenler kaydı** | ✅ |
| R3 | Bozuk bir şey sağlam sanılır | 06'da açık durum işaretleri | ✅ |
| R4 | Mevcut kod bozulur | Testler | ⚠️ **CI koşana kadar zayıf** |
| R5 | İki pencere yazar, sürüklenme | Tek aktif pencere kuralı | ✅ *(15 Eylül: paralel ajan modeli değerlendirildi, reddedildi — teyit)* |
| R6 | Devir dokümanının kendisi yanlış olur | Her iddia bir teste/dosyaya/komuta bağlı **+ `DENETIM.py`** | ✅ *(M0'da, sonra 14 Eylül'de betikle)* |
| R7 | **Dokümanlar büyür, okumak kendisi bağlam sorunu olur** | Giriş 1 sayfa; derin dosyalar talep üzerine; **düzenli sadeleştirme** | 🔴 **Eşikte** — 9 dosya |

**R7 için kural:** Yeni bir devir dosyası açmadan önce sor — *bu, var olan bir
dosyanın bölümü olabilir mi?* `00-DEVIR/` dokuz dosyayı geçerse sadeleştirme
zamanı gelmiştir.

⚠ **14 Eylül: dokuzuncu dosya açıldı** (`08-URUN-KARARLARI.md`). Soru soruldu
ve cevabı "hayır" çıktı — ürün kararı mimari karar değil, ve adı içeriğine
uymayan dosya bu projede zaten bir kez pahalıya mal oldu. **Onuncu dosyadan
önce sadeleştirme yapılmalı.** `DENETIM.py` bunu otomatik uyarıyor.

---

## 6. Yeni pencere için çalışma kuralları

Bu kurallar Mustafa ile üzerinde anlaşılmıştır; tartışmaya açık değil.

1. **Mustafa yazılımcı değildir.** Komutlar tam olarak, kopyalanıp
   yapıştırılacak şekilde verilir. "Şunu yapmalısın" değil, "şu komutu şu
   klasörde çalıştır" denir.
2. **Versiyonla, üzerine yazma.** Dosyalar güncellenerek değil,
   versiyonlanarak ilerler. Her kilometre taşı: git etiketi + değişim günlüğü
   satırı. Şartname değişikliği yeni bir sürüm dosyası olur.
3. **Kabul ölçütü önce.** Kod yazmadan önce "bu doğru çalışıyorsa ne
   görmeliyiz" cümlesi Türkçe yazılır ve Mustafa onaylar. Test o cümlenin
   çevirisidir.
4. **Bir hata bulunduğunda düzeltmek yetmez.** O hatanın bir daha sessizce
   geri gelmesini engelleyen kalıcı bir kontrol eklenir. Bu projenin işleyiş
   biçimi budur; örnekleri `05-HATA-OTOPSILERI.md`'de.
5. **Kırmızı çizgiler** `RISKLER-VE-ONLEMLER.md` §6'da. Okumadan veri, sır
   ya da migration konusuna dokunma.
6. **Anlaşılmayan komut çalıştırılmaz** — özellikle `rm`, `del`, `format`,
   `Remove-Item`, `--force` içerenler. Bu projede `git reset --hard` ve
   `git push --force` yasaktır.
7. **ÇÖZÜMLEMEK İÇİN PROBLEMİ DARALTMA.** *(Mustafa, 29 Eylül — iki kez
   ihlal edildiği için yazıldı.)* Test verisi, senaryo ya da ölçüm ayarı,
   geçmesi kolay olsun diye küçültülmez, gevşetilmez, ürünün gerçek
   ayarından uzaklaştırılmaz. **En zor senaryoyla test edilir**; o
   aşılırsa konu zaten çözülmüş olur.

   İki ihlal aynı gün yaşandı:
   * *"Tüm kuralların uygulandığı 350 kişilik set"* denildi; gerçekte 39
     kuralın **15'inin gövdesi yoktu**, 13'ü hiç zorlanmıyordu, kadro
     talebin **iki katıydı** ve 45 saatlik sözleşme şablonlarla
     **tutturulamıyordu** (T-51).
   * Ölçüm aracı *"temiz olsun"* diye iki aşamayı kapatıyordu — yani
     ürünün hiç kullanmadığı bir ayarı ölçüyordu.

   **Bir ölçümü ya da testi kolaylaştıran her ayar, raporda AÇIKÇA
   yazılır.** Yazılamayacak kadar utandırıcıysa, yapılmamalıdır.
8. **Beni memnun etme, problemlere odaklan.** *(Mustafa, 29 Eylül:
   "Beni yanıltmanın bedeli en ağır.")* İyi haber özetlenmez, kötü haber
   yumuşatılmaz. Ölçülmemiş bir şey **ölçülmedi** diye yazılır.

---

## 7. Ortam gerçekleri — kaybedilen zamanın çoğu buradan geldi

Bunlar "bilinmezse tekrar tekrar saat kaybettiren" şeyler:

| Gerçek | Sonucu |
|---|---|
| Windows 11, **Windows PowerShell 5.1** (PowerShell 7 **değil**) | `.ps1` dosyaları **saf ASCII** olmalı (5.1 dosyayı ANSI okur, Türkçe karakter ayrıştırıcıyı bozar). `-SkipHttpErrorCheck` gibi PS7'ye özgü parametreler kullanılamaz. |
| `dotnet test` sırasında API çalışıyorsa DLL kilidi | Testler **`TEST.ps1`** ile koşulur — API'yi önce durdurur. Doğrudan `dotnet test` çağırma. |
| Docker bağlamına Windows `bin/`/`obj/` girerse restore bozulur | `04-kod/.dockerignore` var, silinmeyecek |
| PostgreSQL yerelde 5432'de olabilir | Kutu **5433**'te dinliyor |
| Mustafa'nın `.env.local` dosyasını uzak araçlar yazamıyor | O dosyayı Mustafa'nın kendisi oluşturur |

Kurulu sürümler: git 2.55 · .NET SDK 10.0.401 · Node 24.20 · npm 11.19 ·
Docker 29.7.2 · Python 3.14.7

---

## 8. Uygulamayı çalıştırma

**İnceleme kipi — her şey kutuda, tek komut:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose --profile tam up --build
```
→ `http://localhost:3000` · firma: `anadolu-cm` · parola: `TShift2026!Deneme`

**Geliştirme kipi — yalnız veritabanı kutuda:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
docker compose up -d
```

**Testler:**

```
cd C:\Users\PC\Desktop\Tshift\04-kod
.\TEST.ps1
```

**Yalıtım kanıtı (iki firma birbirini görüyor mu):**

```
.\YALITIM-KANITI.ps1
```
