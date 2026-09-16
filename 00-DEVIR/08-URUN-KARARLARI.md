# ÜRÜN KARARLARI

`03-MIMARI-KARARLAR.md`'nin kardeşi. Orada **M-serisi** var: mimari kararlar,
"bu satır neden böyle" sorusunun cevabı. Burada **K-serisi** var: ürün ve
kapsam kararları, "bu davranış neden böyle" sorusunun cevabı.

> **Neden ayrı dosya (karar: 14 Eylül 2026):** R7 kuralı yeni dosya açmadan
> önce *"bu, var olan bir dosyanın bölümü olabilir mi?"* diye sormayı emreder.
> Sorduk. Cevap hayır: ürün kararları mimari karar değil, ve `03-MIMARI-KARARLAR`
> adlı bir dosyaya ürün kararı koymak dosyanın adını yanlış yapardı. Bu projede
> **adı içeriğine uymayan dosya** zaten bir kez pahalıya mal oldu (`07-motor/`).
>
> ⚠ Bu dosyayla birlikte `00-DEVIR/` **dokuz dosyaya** ulaştı — R7 eşiği.
> Onuncu dosya açılmadan önce sadeleştirme yapılmalı. `DENETIM.py` bunu
> otomatik uyarıyor.

## Numaralandırma kuralı

Numaralar **kayda giriş sırasıdır, kronoloji değil.** Tarih sütunu kronolojiyi
verir. Sebebi: bir numara verildikten sonra başka dosyalardan ona atıf yapılır
(`08-motor-testleri/v5/KABUL-OLCUTLERI.md` K-1…K-7'ye atıf yapıyor); geriye dönük ekleme yüzünden
numaralar kayarsa o atıflar sessizce yanlış olur.

Yani geçmişteki bir karar sonradan kayda alınırsa **sıradaki boş numarayı**
alır, araya sıkıştırılmaz.

---

## İçindekiler

| # | Karar | Tarih | Durum |
|---|---|---|---|
| ~~K-1~~ | ~~Sınır değerler ihlal sayılır~~ | 14 Eyl 2026 | ⛔ **geri alındı → K-11** |
| [K-2](#k-2--kiracı-saat-dilimi-iana-adı-olmak-zorunda) | Kiracı saat dilimi IANA adı olmak zorunda | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-3](#k-3--çözücü-istatistikleri-çıktıya-girer-ve-müşteriye-gösterilir) | Çözücü istatistikleri çıktıya girer ve müşteriye gösterilir | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-4](#k-4--mola-hakkı-iş-kanununa-göre-brüt-süreden-hesaplanır) | Mola hakkı İş Kanunu'na göre, brüt süreden | 14 Eyl 2026 | ⏳ uzman teyidi bekliyor |
| [K-5](#k-5--geçmişi-olmayan-kiracıda-motor-çalışır) | Geçmişi olmayan kiracıda motor çalışır | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-6](#k-6--sonbahar-dst-kontrolü-ileri-tura) | Sonbahar DST kontrolü ileri tura | 14 Eyl 2026 | ✅ kayıtta |
| [K-7](#k-7--çözümsüzlük-teşhisine-hafta-seviyesi-eklenir) | Çözümsüzlük teşhisine hafta seviyesi eklenir | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-8](#k-8--hedef-kapsama-sözü-95-100-değil) | Hedef kapsama sözü %95, %100 değil | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-9](#k-9--izin-planlamayı-ezer) | İzin planlamayı ezer | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-10](#k-10--yönetici-çözümsüz-planı-kabul-edebilir) | Yönetici çözümsüz planı kabul edebilir | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-11](#k-11--sınır-değer-ihlal-değil-yanlış-sorulmuş-bir-soruydu) | Sınır değer ihlal değil (K-1'in yerine) | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-12](#k-12--dst-ertelendi-altyapı-kalıyor) | DST ertelendi, altyapı kalıyor | 15 Eyl 2026 | ✅ kayıtta |
| [K-13](#k-13--çalışan-tercihi-yok-uygunluk-sözleşmeden-gelir) | Çalışan tercihi yok, uygunluk sözleşmeden gelir | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-14](#k-14--öğle-arası-vardiya-şablonunun-parametresidir) | Öğle arası vardiya şablonunun parametresidir | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-15](#k-15--plan-kopyalama-doğrulayıcıyı-çalıştırır-ve-editöre-taşır) | Plan kopyalama doğrulayıcıyı çalıştırır ve editöre taşır | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-16](#k-16--yayın-kapısı-çözülmemiş-ihlalle-plan-yayınlanamaz) | Yayın kapısı: çözülmemiş ihlalle plan yayınlanamaz | 15 Eyl 2026 | ⏳ uygulanmadı |
| [K-17](#k-17--yasal-bayrağı-üç-durumlu-belirsiz-güvenli-tarafta) | `yasal` bayrağı üç durumlu; belirsiz = güvenli tarafta | 15 Eyl 2026 | ⏳ uygulanmadı |

**Durum işaretleri:** ✅ uygulandı ve bir bekçisi var · ⏳ karar verildi,
uygulanmadı · ⚠ uygulandı ama bekçisi yok.

---

## K-1 · ~~Sınır değerler ihlal sayılır~~ — **GERİ ALINDI (15 Eylül)**

> ⛔ **Bu karar yürürlükte değil. Yerine [K-11](#k-11--sınır-değer-ihlal-değil-yanlış-sorulmuş-bir-soruydu).**
>
> **Neden geri alındı:** Karar, yanlış sorulmuş bir soruya verilmiş doğru
> cevaptı. Claude iki ayrı şeyi tek soruya sıkıştırmıştı: *"11,0 saat 'asgari
> 11 saat' kuralına uyuyor mu?"* (aritmetik, ürün kararı değil) ve *"yönetici
> elle 8 saate düşürürse ne olur?"* (asıl ürün kararı). Mustafa 15 Eylül'de
> sordu: *"Ben neye yanlış karar verdim anlamadım."* Haklıydı — yanlış bir
> karar vermemişti, yanlış bir soru sorulmuştu.
>
> **Ders:** Teknik kenar durumları ürün kararıymış gibi Mustafa'ya yollamak,
> hem dikkatini israf ediyor hem yanlış varsayılan üretme riski taşıyor.
> Kararın ürün kararı olup olmadığı **sormadan önce** ayrılmalı.

*Özgün metin, kayıt için:*

**Karar (14 Eylül 2026, Mustafa).** Tam 11 saat dinlenme **ihlaldir**. Tam 9
saat günlük çalışma **ihlaldir**. Ama bu davranış kural tanımında esnek
bırakılır — firma kararıdır.

**Nasıl uygulanır:** Eşikli her kurala `sinir_dahil` parametresi eklenir.
Varsayılan `false` (sınır ihlal). Bu, §5.1'in *"kural tipi kodda, kural değeri
veride"* ilkesine uyuyor: sınır davranışı bir **değerdir**, kural tipi değil.

**Sonucu — bilerek kabul edildi:** Ekranda `GUNLUK_AZAMI: 9` yazan parametre
fiilen *"en çok 8 saat 59 dakika"* demektir; 9 saatlik vardiya kurulamaz.
Dinlenmede tersi işler: `11` yazar, fiilen 11 saat 1 dakika ister.

Yasal tarafta sorun yok — kanun taban/tavan koyar, firma daha **sıkı**
davranabilir, gevşek davranamaz. Bedeli iki yerde çıkar: planlar zorlaşır,
`cozumsuz` sayısı artar; ve kullanıcı *"9 yazdım ama 9 saat vardiya
kuramıyorum"* der.

**Bu yüzden zorunlu:** Kural ekranında parametrenin yanında cümle **açıkça**
yazılır — *"11 saat ve altı dinlenme ihlaldir"*. Sayı hiçbir zaman sessizce
başka bir şey dememeli.

**Elenen alternatif:** Sınırı dâhil saymak (yasal okuma). Reddedildi; çalışan
lehine daha temkinli olan seçildi.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A4 (iki ayarla da koşulur) ·
spec v1.4 §5–§6'ya girecek (T-6)

---

## K-2 · Kiracı saat dilimi IANA adı olmak zorunda

**Karar (14 Eylül 2026, Mustafa).** Saat dilimi sabit ofsetle (`+03:00`)
verilirse girdi **reddedilir** — şema hatası döner. Uyarı verip devam edilmez.

**Neden:** Spec §6.3 zaten IANA adını (`Europe/Istanbul`) şart koşuyordu ama
ihlalinde ne olacağını yazmıyordu. Uyarı sessizce geçilir; zaman modelini
sonradan değiştirmenin bedeli *"her plan yeniden yorumlanır"* seviyesindedir.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A5 madde 5 · spec v1.4 (T-7)

---

## K-3 · Çözücü istatistikleri çıktıya girer ve müşteriye gösterilir

**Karar (14 Eylül 2026, Mustafa).** Motor çıktısına `cozum_istatistikleri`
bloğu eklenir: `degisken_sayisi`, `kisit_sayisi`, `onarim_denemesi`,
`incelenen_dugum`, `cozum_suresi_sn`.

**İki amacı var.** Birincisi test edilebilirlik: onarım döngüsünün (§11.7)
gerçekten iki denemeyle sınırlı kaldığı ancak böyle sınanabiliyor. İkincisi
**satış** — *"bu plan 17.412 değişken ve 38.905 kısıt üzerinden çözüldü"*
cümlesi ürünün yaptığı işi müşteriye somutlaştırıyor.

**Sınırı:** Bu sayılar modelin kuruluşuna bağlıdır; motor iyileştirildiğinde
değişken sayısı **düşebilir**. Ekranda **o çalıştırmanın gerçek sayısı**
gösterilir. Satış materyaline sabit bir rakam yazılırsa bir sonraki sürümde
yanlış olur.

→ §9.5 metrik açıklama bileşeni · spec v1.4 §11.3 (T-4)

---

## K-4 · Mola hakkı İş Kanunu'na göre, brüt süreden hesaplanır

**Karar (14 Eylül 2026, Mustafa):** *"İş kanununa uyalım."*

**Uygulaması:** `MOLA_HAKKI` eşiği vardiyanın **brüt** süresine uygulanır.
08:00–16:00 vardiyası 8 saat brüttür → 60 dk mola.

**Neden brüt, net değil:** Net süreye uygulamak **döngüseldir** — net süre
molaya, mola net süreye bağlı olur. Brüt her zaman netten büyük ya da eşit ve
eşik tablosu artan olduğu için, brüt hesap kanunun istediğinden **asla az**
mola vermez. Hem belirli hem güvenli taraf.

**Onaylandı (15 Eylül, V-4 kapandı):** *"Mola hakkı eşiği brüt süreye uygulanır
— doğru."*

**Bu kararı şimdi vermek neden güvenli:** Hata yönü tek taraflı. Brüt süre
netten büyük ya da eşit, eşik tablosu da artan olduğu için brüt hesap kanunun
istediğinden **asla az** mola vermez. En kötü ihtimalle gerekenden fazla mola
verilir — bu bir ihlal değil.

> ⚠ Yine de bu bir **hukuki yorumdur**; Claude avukat değil. Sahaya çıkmadan
> önce İş Kanunu md. 68 için uzman gözü geçmeli. Karar bloke değil, teyit
> beklemede.

**Yan sonuç:** Spec §11.2'deki örnekte 08–16 vardiyası için `mola_dk 30`
yazıyor; §6.2 tablosuna göre 60 olmalı. v1.4'te düzeltilecek (T-3).

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A8 · §7 V-4

---

## K-5 · Geçmişi olmayan kiracıda motor çalışır

**Karar (14 Eylül 2026, Mustafa).** Yeni kurulmuş, hiç yayınlanmış planı
olmayan kiracıda lookback eksikliği motoru **engellemez**.

**Ayrım ölçütü:** Lookback penceresi kiracının **ilk yayınlanmış planından**
öncesine düşüyorsa durum *"boş"*tur, *"eksik"* değil. Var olan bir kiracıda
pencere içindeki bir hafta eksikse bu **eksiktir** ve motor çalışmaz (§11.2).

O çalıştırmanın `plan_runs` kaydına *"geçmişsiz başlangıç"* notu düşülür.

**Neden ölçüt kiracı oluşturma tarihi değil:** Kiracı üç ay önce açılıp yeni
plan yapmaya başlamış olabilir; o durumda geçmiş gerçekten yoktur ama kiracı
yeni değildir. Ölçüt yayınlanmış plan olmalı. *(Bu ölçüt `[çıkarım]`.)*

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A11 madde 5 · spec v1.4 (T-8)

---

## K-6 · Sonbahar DST kontrolü ileri tura

**Karar (14 Eylül 2026, Mustafa).** 25 saatlik gün kontrolü (31 Ekim 2027)
v1 fikstürlerine girmez.

**Neden:** İlkbahar geçişi asıl riski yakalıyor — duvar saatiyle 11 saat görünen
dinlenmenin gerçekte 10 saat olması. Sonbaharda gün uzar, kural gevşer; sessiz
ihlal üretmez.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A5 sonu

---

## K-7 · Çözümsüzlük teşhisine hafta seviyesi eklenir

**Karar (14 Eylül 2026, Mustafa).** §11.3 teşhisi yalnız hücre bazlıydı.
`teshis.kapsam` alanı eklenir: `"hucre"` | `"hafta"`.

**Neden gerekli — somut vaka:** 10 kişilik kadroda her gün 9 kişi isteyen bir
talep. Hiçbir hücre tek başına imkânsız değil (9 ≤ 10), ama hafta toplamı
63 kişi-gün ve kapasite 60 (kimse 7 gün üst üste çalışamaz). Hücre bazlı
teşhis bu durumu **ifade edemez**; motor hafta toplamını görmezse birine yedi
gün çalıştıran bir plan üretir.

*"Küçük müşterinin en sık göreceği ekran UNSAT ekranıdır"*
(`06-ACIK-RISKLER.md` ölçek matrisi) — bu yüzden teşhisin eksiksiz olması
ürün özelliğidir, hata mesajı değil.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A9(c) · spec v1.4 §11.3 (T-5)

---

---

## K-8 · Hedef kapsama sözü %95, %100 değil

**Karar (15 Eylül 2026, Mustafa).** Ürün, ideal (hedef) kapsamanın %100
tutacağı sözünü **vermez.** Kabul eşiği **%95**.

**Gerekçesi (Mustafa):** *"Kesinlikle %100 kapsama sözü doğru olmayabilir. %95
de kabul görür kanaatindeyim. Özellikle daha kompleks problemler çözdüğümüzde
%95 kabul oranı çok daha yüksek oranda değer gösterebilir. Birçok problemde
%100 kapsayabiliriz de."*

**Ayrım korunur:** **Asgari** kapsama hâlâ %100'dür ve serttir — o tutmazsa plan
geçersizdir (K-5 ayrımı). Gevşeyen yalnız **hedef** kapsamadır.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A1 madde 4

---

## K-9 · İzin planlamayı ezer

**Karar (15 Eylül 2026, Mustafa).** *"İzin tüm planlamayı ezer. Mevzuatta izni
olan çalışanı çalıştıramıyoruz."*

Üç davranış:

1. **Önleme.** Onaylı ve iptal edilmemiş izni olan çalışana o gün için atama
   yapılamaz — yönetici sabitleme de yapamaz. Uyarı verip devam ettirilmez.
2. **Sonradan gelen izin.** Plan varken izin onaylanırsa çalışan plandan
   **otomatik çıkarılır**, yöneticinin kontrolü beklenmez. Yöneticiye bildirim
   gider. Oluşan kapsama eksiği plana ihlal olarak yazılır, sessizce
   doldurulmaz.

   **Ek (15 Eylül, onay turunda):** Bildirim yetmez — yönetici **plana
   girdiğinde** düşen atamayı ve **sebebini (izin)** plan ekranında görmeli, ve
   **yapay zekâ asistanı ona öneri sunmalı** (boşluğu kim kapatabilir).
   Mustafa'nın ifadesi: *"Yönetici plana girdiğinde, Ayşe'nin silindiğini izin
   sebebiyle görmeli ve asistan ona öneri vermelidir."* Bu, A6'daki asistan
   işleviyle aynı mekanizma (§12.2: yapay zekâ plan üretmez, açıklar ve önerir).
3. **İzin iptali.** İzin kaydı silinmez; **durumu** değişir. İptal edilen izin
   çalışanı yeniden atanabilir yapar.

**Veri modeli sonucu:** `leaves` tablosuna durum alanı gerekiyor
(`talep` / `onayli` / `iptal` / `reddedildi`). Şartname §8.3'te yok, v1.4'e
girecek.

**Savunma katmanı:** Arayüz engellemesi güvenlik sınırı değildir. Motora izinli
kişiye sabit atama içeren girdi gelirse motor da plan üretmez.
(`02-DEGISMEZLER.md`: *"Engellemenin delikleri vardır; güvenli varsayılanın
yoktur."*)

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A2

---

## K-10 · Yönetici çözümsüz planı kabul edebilir

**Karar (15 Eylül 2026, Mustafa).** *"Sahada bazı durumlarda imkansızlıklar
maalesef oluşuyor. Bu tür durumlarda yöneticilere onay ile çözümsüz dahi olsa
en iyi planı sunmalıyız."*

| Adım | Davranış |
|---|---|
| Motor çözemezse | `cozumsuz` **ve** elindeki **en iyi planı** birlikte döner |
| Kullanıcıya | Hangi gün, hangi kural, kaç kişi — açıkça yazılır, "devam edilsin mi" sorulur |
| "Devam et" | Plan taslak olur; ihlaller **kabul edilmiş ihlal** olarak kaydedilir: kural, hücre, **kabul eden kullanıcı**, zaman, gerekçe |
| Sonrasında | Kabul edilmiş ihlal plan ekranında **görünür kalır**; plan "temiz" görünmez |

**Kapsamı dar:** Kabul yalnız **o hücre** için geçerlidir. Kural haftanın geri
kalanında yürürlüktedir.

**Kuralı gevşetmekten farkı — ikisi ayrı özellik:**

| | Kuralı plan için gevşetmek | İhlali kabul etmek |
|---|---|---|
| Kural nerede kapanır | Tüm plan | Yalnız o hücre |
| Fark edilmemiş ikinci ihlal | Sessizce geçer | Ayrıca çıkar |
| Planda iz | Yok | Kim kabul etti, ne zaman, neden |

Gevşetme = *"bu plan gerçekten farklı koşullarda çalışıyor"*. Kabul = *"kural
doğru, ama gerçek onu bozdu"*.

**Veri modeli sonucu:** `plan_violations`'a `kabul_edildi` durumu +
`kabul_eden_kullanici`, `kabul_zamani`, `gerekce` alanları. `/solve` çözümsüz
çıktısına `en_iyi_plan`. v1.4 §8.6 ve §11.3.

**Kapsam sınırı — onaylandı (15 Eylül, V-5 kapandı):**

> *"Yasal kuralların ihlali kabul edilemez ama firma kuralı ihlali kabul
> edilebilir."* — Mustafa

| Kural tipi | Kabul edilebilir mi |
|---|---|
| `yasal = true` (onaylı izinde çalıştırma, 11 saat dinlenme, gece azami) | ❌ **Hayır.** Sistem kabul seçeneği sunmaz |
| Firma kuralı (ilk yardımcı bulundurma, ekip sürekliliği, rol kapsaması) | ✅ **Evet**, kaydıyla birlikte |

Gerekçe: denetimde *"sistem izin verdi"* savunması yoktur. Firma kendi koyduğu
kuralı kendi gevşetebilir; kanunu gevşetemez.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A3, A6, A9

---

## K-11 · Sınır değer ihlal değil (yanlış sorulmuş bir soruydu)

**Karar (15 Eylül 2026, Mustafa).** K-1 geri alındı. *"Asgari 11 saat"* kuralı
**11 saati kapsar**; tam 11 saat dinlenme ihlal değildir. `sinir_dahil`
parametresine gerek yok.

**Asıl ürün kararı bu:** Motor planı kurallara uyarak yapar. Yönetici **elle**
kuralı bozacak bir değişiklik yaparsa (dinlenmeyi 8 saate düşürmek gibi):

1. Sistem **uyarır** ve ne olacağını söyler: *"Bu değişiklik dinlenme süresini
   8 saate düşürür."*
2. **Karar kullanıcınındır.**
3. Devam edilirse K-10'daki gibi **kabul edilmiş ihlal** olarak kayda geçer.

Mustafa'nın ifadesi: *"Sen çalışanın en son hangi saat diliminde ve saat kaça
mesai konduğunu biliyorsun, buna bakarak 11 saat farkla planlama yapabilirsin;
kullanıcı bu farkı manuel olarak 8 saate indirirse de uyarı verirsin ve karar
kullanıcının olur."*

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A4 madde 2 ve 7

---

## K-12 · DST ertelendi, altyapı kalıyor

**Karar (15 Eylül 2026, Mustafa).** *"Şu an Türkiye'de bir müşterim dahi yok ve
önce bu pazarda iş yapmalıyım. Bunu ileride çözülebilecek bir alt yapı ile
erteleyelim. Şu an gerçekten kritik olduğunu düşünmüyorum."*

**Ertelenen:** A5 senaryosu, DST geçiş testleri. v1 kapsamı dışı.

**Ertelenmeyen — altyapı, çünkü sonradan eklemenin bedeli yüksek:**
saat dilimi IANA adıyla saklanır (K-2), süre hesapları mutlak zamanda yapılır,
`DST_GECISI` kuralı katalogda pasif durur. Bu üçü A1 ve A4 testleriyle dolaylı
korunuyor.

K-6 (sonbahar geçişi) bu kararın içinde eriyor.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A5

---

## K-13 · Çalışan tercihi yok, uygunluk sözleşmeden gelir

**Karar (15 Eylül 2026, Mustafa).** *"Çalışan bir çalışma saati veya vardiyası
belirtemez. Sözleşmeden gelir bu kural. Sadece part-time çalışanlar için bu
kural geçerlidir."*

**Ne var:** Part-time çalışanın **uygunluk kısıtı** — sözleşmeden doğar ve
**serttir**. Örnekler: öğrenci Salı günleri tüm gün derste; ikinci öğretim
öğrencisi 16:00'dan sonra çalışamıyor.

**Ne yok:** Çalışanlardan tek tek toplanan vardiya tercihi.

**Sonucu:** Şartname §6.8'deki `TERCIH_KARSILAMA` yumuşak kuralı yeniden
değerlendirilmeli — bugünkü tanımıyla karşılığı yok. Yumuşak kural tarafındaki
asıl gerilim **adalet ile kapsama** arasında (§6.5 `ADALET_DENGESI`).

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` §3 sahne, A1 madde 6–7, A7

---

## K-14 · Öğle arası vardiya şablonunun parametresidir

**Karar (15 Eylül 2026, Mustafa).**

1. **Parametre:** Vardiya şablonu oluşturulurken öğle arası **süresi** ve
   **penceresi** (en erken başlangıç – en geç bitiş, ör. 12:00–14:00) girilir.
2. **Tek blok:** *"Öğle arasını bölemeyiz. Mevzuatta böyle diyor."* 60 dakika
   30+30 verilemez. (v3'teki V-2 varsayımı bu kararla kapandı.)
3. **Motor kaydırır:** Molalar pencere içinde kişiler arasında kaydırılarak
   yerleştirilir, kapsama korunur.
4. **Çıktı öneridir:** *"Mola öneri gibi düşünmeliyiz. Kişiler molalarını
   kaydırabilir, bizim sistemde tutulmayacak aksiyonlar olabilir ama bu bizi
   bozmaz. Biz en azından bir rehber gibi öneri mantığında mola verisi de
   hesaplayıp sunuyor olacağız. Katma değerimiz olacak."*

**Sert mi yumuşak mı — karar verildi (15 Eylül, V-6 kapandı):**
**`MOLA_KAPSAMASI` YUMUŞAK kuraldır.**

Claude sert kalmasını önermişti; Mustafa yumuşak dedi. **Kararı tutarlı
buluyorum:** mola çıktısı öneri niteliğindeyse (4. madde), mola sırasındaki
kapsamayı sert kısıt yapmak kendi kendisiyle çelişirdi. Sahada kimse molasını
plana göre kullanmıyorsa, plana göre hesaplanan bir eksiği "plan geçersiz"
saymak gerçeği yansıtmaz.

⚠ **Karıştırılmaması gereken iki kural:**

| Kural | Tür | Neden |
|---|---|---|
| `MOLA_HAKKI` — kişiye mola verilmesi | **SERT** kalır | Yasal. 9 saat sahadaki kişiye 60 dk ara dinlenme verilmek zorunda |
| `MOLA_KAPSAMASI` — mola sırasında sahada kimse kalması | **YUMUŞAK** oldu | Plan önerisidir; sahada kaydırılabilir |

**Sonucu:** Herkesin aynı anda molaya çıktığı bir plan artık **geçersiz
değildir** — puanı düşüktür. Motor yine de molaları kaydırmaya çalışır, çünkü
ağırlık onu oraya iter.

**Ağırlık — onaylandı (15 Eylül):** DENGELI **7** · KAPSAMA **9** ·
CALISAN **6** (§5.4 tablosuna eklenecek). Hedef kapsamanın (9) biraz altında:
önemli ama kapsamanın önüne geçmemeli. Ağırlık çok düşük olursa motor
molaları üst üste yığar ve plan müşteriye saçma görünür.

**Şartname sonucu:** §6.4'te `MOLA_KAPSAMASI` **SERT → YUMUŞAK**, ve §5.4
ağırlık tablosuna yeni satır. v1.4.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A8

---

## K-15 · Plan kopyalama doğrulayıcıyı çalıştırır ve editöre taşır

**Karar (15 Eylül 2026, Mustafa).** *"Kopyala seçeneği işaretlendiğinde motor
tekrar çalışıp, sözleşmeleri örneğin kontrol etmeli, biten varsa veya işten
çıkarılmış biri varsa kullanıcıyı uyarmalı. Plan kopyalama özelliği kullanıcıyı
ilk orjinal planın motordan çıkıp kullanıcıya sunulduğu, kullanıcının edit
yapabildiği ekranına taşımalı."*

1. Kopyalamada **doğrulayıcı** yeniden koşar: pasife düşen çalışan, **süresi
   biten sözleşme**, yeni izinler, değişmiş kural sürümü.
2. Düşen atamalar **sebebiyle birlikte** tek tek listelenir.
3. Kullanıcı **plan editörü ekranına** düşer — motordan yeni çıkmış planla aynı
   ekran. Kopyalama ayrı bir ekran değildir.

**Onaylandı (15 Eylül):** *"motor tekrar çalışıp"* ifadesi **doğrulayıcının**
çalışmasıdır (kontrol), çözücünün yeniden plan üretmesi değil. Boşluklar
sessizce doldurulmaz; kullanıcı editörde görür ve kendisi doldurur.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A12

---

## K-16 · Yayın kapısı: çözülmemiş ihlalle plan yayınlanamaz

**Karar (15 Eylül 2026, Mustafa).** A4'teki Cem vakası üzerine: *"Cem'in çakışan
mesaisi mantıksız, bu çözülmeden plan yayınlanamaz. Zaten yasal ihlal de var."*

**Taslak ile yayın arasındaki ayrım netleşti:**

| Durum | Sert ihlal taşıyabilir mi |
|---|---|
| **Taslak plan** | ✅ Evet. A2 (izin düşürdü), A3 (imkânsız durum), A12 (kopyada kişi düştü) hepsi ihlalli taslak üretebilir — kullanıcı görsün diye |
| **Yayınlanmış plan** | ❌ Hayır. Yayın için: **sıfır yasal ihlal** + kalan her sert ihlal **açıkça kabul edilmiş** (K-10: kim, ne zaman, neden) |

**Yani yayın düğmesi bir kapıdır.** Planı çözmek zorunda değilsin — ama
yayınlamadan önce her sert ihlal ya düzeltilmiş ya da adıyla kabul edilmiş
olmalı. Sessiz geçiş yok.

**`CAKISMA_YOK` yasal kuraldır** → K-10 gereği **kabul edilemez.** Cem'in
çakışması düzeltilmeden o plan yayınlanamaz; "kabul ediyorum" seçeneği bile
sunulmaz. Zeynep vakasından (A3) farkı tam burada: ilk yardımcı bulundurma
firma kuralıdır, kabul edilebilir; çakışma değildir.

### ⚠ Bu karar bir şartname eksiğini ortaya çıkardı

K-10 ve K-16'nın ikisi de kuralın `yasal` olup olmamasına dayanıyor. **Ama
şartname §6 kural kataloğunda hangi kuralın `yasal = true` olduğu yazmıyor.**
Alan §5.3'te tanımlı (*"Yasal dayanağı olan kurallar sertlikten çıkarılamaz"*)
ama katalog tablosunda sütunu yok.

Bu bayrak olmadan K-10 ve K-16 **uygulanamaz** — sistem hangi ihlali kabul
etmeye izin vereceğini bilemez. v1.4'te §6'ya `yasal` sütunu eklenmeli
(T-9 olarak kaydedildi).

**Başlangıç ayrımı — `[çıkarım]`, hukuk uzmanı teyidi gerekli:**

| Muhtemelen yasal | Muhtemelen firma kuralı | Bakılması gereken |
|---|---|---|
| `ONAYLI_IZIN` · `CAKISMA_YOK` · `VARDIYA_ARASI_DINLENME` · `GUNLUK_AZAMI` · `HAFTALIK_AZAMI` · `HAFTA_TATILI` · `GECE_VARDIYASI_AZAMI` · `MOLA_HAKKI` · `YILLIK_FAZLA_MESAI_TAVANI` | `ROL_KAPSAMASI` · `YETKINLIK_KAPSAMASI` · `ASGARI_KAPSAMA` · `ASGARI_VARDIYA_SURESI` · `ARDISIK_HAFTA_SONU_LIMIT` · `EKIP_SUREKLILIGI` | `ARDISIK_CALISMA_GUNU` (hafta tatilinin vekili mi?) · `PART_TIME_LIMIT` (sözleşme) · `SOZLESME_GECERLI` · `AKTIF_CALISAN` · `ARDISIK_GECE_LIMIT` |

Bu tablo **V-4 ile aynı sepette**: Claude avukat değil, teyit gelene kadar
`[çıkarım]`.

→ `08-motor-testleri/v5/KABUL-OLCUTLERI.md` A4 (Cem), A3 (Zeynep karşıtlığı)

---

## K-17 · `yasal` bayrağı üç durumlu, belirsiz güvenli tarafta

**Karar (15 Eylül 2026, Mustafa).** *"Sen kurallara şimdilik bir yasal kural mı
true ekle yeter. Gerisini ileride de çözebiliriz. Elimizde hangilerini şimdilik
emin olarak işaretleyebiliriz bu bilgide var, bunlara göre aksiyon al."*

### Bayrak üç durumludur

| Değer | Anlamı | İhlali kabul edilebilir mi (K-10) |
|---|---|---|
| `true` | Yasal dayanağı var | ❌ Hayır, kabul seçeneği sunulmaz |
| `false` | Firma kuralı | ✅ Evet, kaydıyla |
| `belirsiz` | Henüz sınıflandırılmadı | ❌ **Hayır — `true` gibi davranılır** |

**Belirsiz neden yasal sayılır:** Bu, `02-DEGISMEZLER.md` Y-8'deki ilkenin
aynısı — *eksik yapılandırma sızıntıya değil, "yapamıyorum" şikâyetine
dönüşmeli.* Yanlış yön seçilirse sonuçlar simetrik değil:

- Belirsiz → firma kuralı sayılsaydı: sınıflandırılmamış bir **yasal** kuralın
  ihlali sessizce kabul edilebilirdi. Denetimde savunması yok.
- Belirsiz → yasal sayılınca: yönetici kabul edemediği bir ihlalle karşılaşır,
  şikâyet eder, biz de o kuralı sınıflandırırız. **Şikâyet, sızıntıdan iyidir.**

Mustafa'nın *"teknik olarak bir problemimiz yok"* tespiti doğru — ama davranışsal
bir sonucu var ve varsayılanın yönü bu yüzden yazıya geçti.

### Şimdilik emin olduklarımız

⚠ **Claude avukat değil.** Aşağıdaki "emin" sütunu, İş Kanunu'nda açık karşılığı
olduğunu düşündüğüm maddeler. **Sahaya çıkmadan önce hepsi uzman gözünden
geçmeli.** Bayrak yalnız **SERT** kurallar için anlamlıdır; yumuşak kural zaten
"ihlal" üretmez.

| Kural | `yasal` | Dayanak / gerekçe |
|---|---|---|
| `ONAYLI_IZIN` | **true** | Onaylı izindeki çalışan çalıştırılamaz |
| `CAKISMA_YOK` | **true** | Mustafa: *"zaten yasal ihlal de var"*; ayrıca fiziksel imkânsızlık |
| `HAFTA_TATILI` | **true** | İş Kanunu md. 46 — haftada kesintisiz 24 saat |
| `GECE_VARDIYASI_AZAMI` | **true** | İş Kanunu md. 69 — gece en çok 7,5 saat |
| `MOLA_HAKKI` | **true** | İş Kanunu md. 68 — ara dinlenme |
| `HAFTALIK_AZAMI` | **true** | İş Kanunu md. 63 — haftada 45 saat |
| `YILLIK_FAZLA_MESAI_TAVANI` | **true** | İş Kanunu md. 41 — yılda 270 saat |
| `SOZLESME_GECERLI` · `AKTIF_CALISAN` | **true** | İş sözleşmesi olmayan kişi çalıştırılamaz |
| `ASGARI_KAPSAMA` · `ROL_KAPSAMASI` · `YETKINLIK_KAPSAMASI` | **false** | Firmanın operasyon kararı |
| `ASGARI_VARDIYA_SURESI` · `ARDISIK_HAFTA_SONU_LIMIT` | **false** | Firma politikası |
| `CALISMA_SAATLERI` · `UYGUNLUK_TAKVIMI` | **false** | Departman/sözleşme yapılandırması |
| `KILIT_UYUMU` · `DONMUS_GUN` · `GECE_YARISI_ASAN` | **false** | Sistem/mekanik kurallar, yasal dayanak değil |
| `FAZLA_MESAI_TAVANI` (haftalık) | **false** | Yıllık tavan ayrı ve yasal; haftalık tavan firma politikası |

### Belirsiz bırakılanlar — kabul edilemez gibi davranılır

| Kural | Neden belirsiz |
|---|---|
| `VARDIYA_ARASI_DINLENME` | 11 saatlik vardiya arası dinlenmenin Türkiye mevzuatındaki dayanağı sektöre göre değişiyor; AB direktifinde açık, İş Kanunu'nda doğrudan madde göremedim |
| `ARDISIK_CALISMA_GUNU` | Hafta tatilinin (md. 46) vekili mi, ayrı bir firma kuralı mı belirsiz |
| `ARDISIK_GECE_LIMIT` | md. 69 gece süresini sınırlıyor ama ardışık gece sayısını göremedim |
| `PART_TIME_LIMIT` | Sözleşmeden doğuyor; sözleşme ihlali ile kanun ihlali ayrımı netleşmeli |

### ⚠ Çözülmemiş tasarım sorusu: bayrak kurala mı, değere mi ait?

`GUNLUK_AZAMI` bunu ortaya çıkarıyor. İş Kanunu md. 63'e göre günlük tavan
**11 saat**; bizim varsayılanımız **9**. Yani:

- 9 ile 11 arasındaki bir aşım **firma politikasının** ihlali — kabul edilebilir
- 11'i aşan bir atama **kanunun** ihlali — kabul edilemez

Bu durumda bayrak kuralın değil, **eşiğin** özelliği oluyor: her yasal kuralın
bir de "yasal sınır" değeri olmalı ve firma bunu ancak **daha sıkı** yapabilmeli.
`GUNLUK_AZAMI` şimdilik **belirsiz** bırakıldı; bu tasarım v1.4'te çözülecek.

**Şartname sonucu:** §6 katalog tablosuna `yasal` sütunu, `rule_types` tablosuna
alan; yasal kurallara ayrıca "yasal sınır" değeri (T-9).

---

## Geriye dönük kayda alınacaklar

Bu sicil 14 Eylül'de kuruldu. Daha önce verilmiş ürün kararları hâlâ
dağınık duruyor. **Restatement yapılmadı** — yanlış aktarma riski var; bunun
yerine nerede oldukları yazıldı. Kayda alınırken sıradaki boş numarayı
alacaklar.

| Nerede | Ne var |
|---|---|
| `07-GERCEK-VERI-BULGULARI.md` §4c | 14 Eylül kapsam kararları: Erlang-C kapsam dışı, yoğunluk tahmini kapsam içi, anonimleştirme yok, **reddedilen değişken ufuk önerisi**, satış noktaları, mola modeli |
| `oturumlar/2026-09-14-veri-analizi.md` §11 | Doküman otoritesi (Master Spec son karar), MVP 3 alternatif, lookback, outbox, **tekrarlanabilirlik garanti edilmeyecek**, bildirim kanal sırası, AI sağlayıcı bağımsızlığı kapsam dışı |
| `oturumlar/2026-09-12-devir-paketi.md` | Kabul ölçütü önce kuralı, kaynak etiketleri |
| `02-DEGISMEZLER.md` Y-8 | Spec'ten bilinçli sapma (kapsamsız kullanıcı hiçbir şey görmez) |

**Kural:** Bundan sonra verilen her ürün/kapsam kararı **önce buraya**
yazılır, sonra spec'e taşınır. Oturum günlüğü kararın *hikâyesini* tutar;
sicil kararın *kendisini*.
