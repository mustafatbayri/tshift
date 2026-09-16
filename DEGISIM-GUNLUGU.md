# Değişim günlüğü

En yeni en üstte. Her satır: tarih · ne oldu · nerede.

---

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
