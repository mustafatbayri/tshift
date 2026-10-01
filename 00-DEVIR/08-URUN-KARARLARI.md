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
   > ⚠ **Düzeltme (25 Eylül, K-32):** pencere artık **mutlak saat değil**.
   > Mutlak pencere şablona bağlıydı ve şablon paylaşılıyor: 12:00'de başlayıp
   > 20:00'de biten bir vardiya için *"12:00–14:00 arası"* anlamsız — kural
   > kendi kendini patlatıyordu. Pencere **kişinin kendi vardiyasına göre
   > göreli** oldu: en erken 3., en geç 5. saatinden sonra.
2. **Tek blok:** *"Öğle arasını bölemeyiz. Mevzuatta böyle diyor."* 60 dakika
   30+30 verilemez. (v3'teki V-2 varsayımı bu kararla kapandı.)
   > ⚠ **Düzeltme (25 Eylül, K-32):** kural **ayakta**, gerekçesi **değişti**.
   > K-14 yazılırken öğle arası, İş K. md. 68'in yasal ara dinlenmesi
   > sayılıyordu — *"mevzuatta böyle diyor"* buradan geliyordu. K-32 yasal
   > hakkı **`dinlenme`** tipine bağladı ve onu bölünebilir yaptı (60 dk, en az
   > 15'er dakikalık bloklar). **Yemek tek blok kalır**, ama sebebi mevzuat
   > değil **operasyon**: bölünmüş bir öğle arası ne çalışana dinlenme sağlar
   > ne operasyona öngörülebilirlik.
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

## K-18 · Yasal kuralın değeri kanunun değeridir

**Karar (16 Eylül 2026, Mustafa).** *"Kural yasal işaretlenir ve değer 11'dir.
Firma bunu esnetemez… Firmalar kafasına göre kural bende 9 veya 10 diyemez."*

`GUNLUK_AZAMI` **9 → 11** oldu, kapsamı `K,D,Z,C` → **`S`**.

**Neden 9 yanlıştı:** v1.3 §5.2 tablosunda 9 saat için *"İş Kanunu üst sınırı"*
yazıyordu. Kanunun tavanı **11** (İş K. md. 63/2: *"günde onbir saati aşmamak
koşulu ile"*); 9 bizim koyduğumuz firma varsayılanıydı ve kanun diye
etiketlenmişti. Şartnamedeki düpedüz yanlış bir cümleydi.

**Kabul edilen sonuç:** firma artık *"bizde kimse 9 saatten fazla çalışmaz"*
diyemez; 10 saatlik vardiya kurulabilir ve sistem itiraz etmez.

**Fikstürlere etkisi ölçüldü: yok.** Hiçbir fikstürde 9 saatten uzun net çalışma
yok, hiçbiri `GUNLUK_AZAMI` ihlali beklemiyor (A04 açıkça `false` diyor).
Sınırı yükseltmek hiçbir beklenen sonucu değiştirmedi.

→ `02-spec/v1.4-master-spec.md` §5.2, §6.2

---

## K-19 · Firma için ayrı günlük azami kuralı açılmayacak

**Karar (16 Eylül 2026, Mustafa).** *"Firma günlük azami diye bir kuralımız
olmayacak. Yasal mevzuat 11 diyorsa 11."*

Teklif edilen `FIRMA_GUNLUK_AZAMI` (yasal kuralın yanında, daha sıkı firma
tavanı) **reddedildi.** Günlük tavan tek ve yasaldır.

**Sonucu:** `employee_contracts.gunluk_azami_saat` alanı kaldırıldı — olmayan
bir yetkiyi varmış gibi gösteriyordu. Alan üretimde kullanılmamıştı, veri
taşıma gerekmedi.

→ `02-spec/v1.4-master-spec.md` §6.2, §8.3

---

## K-20 · Yasal kural ihlali hiçbir koşulda kabul edilemez

**Karar (16 Eylül 2026, Mustafa).** K-16 **aynen geçerli.**

Bu karar bir çelişkinin çözümüdür. Mustafa K-18'i verirken *"firma bunu
esnetemez ama kural ihlalini onaylayabilir, kendi inisiyatifindedir"* demişti;
bu, K-16'nın *"yasal ihlal kabul edilemez"* kuralıyla çelişiyordu. Çelişki
açıkça soruldu, üç seçenek sunuldu ve **en katı olan** seçildi.

| | Kabul edilebilir mi |
|---|---|
| Yasal kural ihlali | ❌ Hayır, hiçbir koşulda |
| İmkânsızlık kuralı ihlali | ❌ Hayır (K-24) |
| Firma kuralı ihlali | ✅ Evet, gerekçeyle |

**Bedeli bilerek kabul edildi:** sahada gerçek bir imkânsızlıkta (personel yok,
kapatılamıyor) yönetici planı hiç yayınlayamaz. Alternatifi — yasal ihlali
kabul ettirmek — daha pahalı bulundu.

→ `02-spec/v1.4-master-spec.md` §4.5, §6

---

## K-21 · ~~Sağlık raporu için ayrı kural: `SAGLIK_KISITI`~~ — **GERİ ALINDI (25 Eylül)**

> ⛔ **Bu karar yürürlükte değil. Kural kataloğdan kaldırıldı; yerine bir kural
> gelmedi — bilinçli bir kapsam sınırı bırakıldı.**
>
> **Neden geri alındı (Mustafa, 25 Eylül):** *"Real ortamlarda çalışanların
> ayakta çalışamaz gibi sağlık kısıtları olabilir, bunlar da bizi
> etkilemiyor. Günde 4 veya max 5 saat çalışabilir diye bir sağlık raporu
> belki milyonda bir vaka olarak karşımıza çıkabilir. Ürüne eklememiz
> gereksiz."*
>
> **Ürünün gördüğü sağlık durumu dönemseldir ve bir kural değil, bir
> izindir:** iki günlük rapor da yarım günlük rapor da `leaves` satırıdır
> (`tip = rapor`, §8.3) ve motoru `ONAYLI_IZIN` üzerinden bağlar. Bunun için
> yeni bir kural gerekmiyor — zaten yazılı.
>
> ⚠ **Bırakılan sınır, açıkça:** kalıcı bir **süre** kısıtı olan çalışan
> gerçekten çıkarsa sistem onu koruyamaz; plan onu normal yasal tavana kadar
> planlar. O durum sistem dışında yönetilir. Şartname §5.2'deki *"Ayşe'nin
> raporu var, günde en fazla 4 saat nereye yazılacak?"* sorusunun cevabı
> artık **"hiçbir yere"**dir ve orada öyle yazıyor — boşluk bırakılmadı.
>
> **Nasıl ortaya çıktı:** 25 Eylül'de T-43 (*"`SAGLIK_KISITI` yazılmadı"*)
> üzerinde çalışılırken Mustafa'ya üç ürün kararı soruldu. İkinci soruya
> verdiği cevap, kuralın kendisinin gereksiz olduğunu gösterdi. Kuralı
> yazmadan önce sorulması, yazıldıktan sonra çıkarılmasından ucuza geldi.
>
> **Dokunulan yerler (25 Eylül):** `02-spec/v1.4-master-spec.md` §1 değişiklik
> tablosu · §5.2 · §6 kural sayısı (35 → **34**, sayılarak doğrulandı) · §6.1
> katalog satırı ve bölümü · §6.2 · §6.6 yasal dayanak tablosu · §8.3 · §17
> sürüm notları.

*Özgün metin, kayıt için:*

**Karar (16 Eylül 2026, Mustafa).** K-18 `GUNLUK_AZAMI`'yi sabitleyince,
*"Ayşe'nin raporu var, günde en fazla 4 saat"* durumu yersiz kaldı. Ayrı bir
kural açıldı.

| Özellik | Değer |
|---|---|
| Kapsam | Yalnız `C` — çalışan |
| Zorunlu | `belge_referansi`, `gecerlilik_bas`, `gecerlilik_bitis` |
| Dayanak | 6331 sayılı İSG Kanunu — hekim raporu işvereni bağlar |
| Yasal | ✅ · ihlali kabul edilemez |

**Neden firma esnetmesi sayılmıyor:** bu, firmanın kanunu gevşetmesi değil;
kanunun kendisinin koruduğu, tek kişiye ait, belgeli bir kısıt. Belge
referansının zorunlu olması kötüye kullanımı engelliyor.

→ `02-spec/v1.4-master-spec.md` §6.1, §8.3

---

## K-22 · `TERCIH_KARSILAMA` anlamı değişti, kod adı korundu

**Karar (16 Eylül 2026, Mustafa).** İki ayrı soru soruldu, ikisi de cevaplandı:

1. **Kural ne olacak?** → *"Anlamını değiştir."* Artık part-time çalışanların
   sözleşmeden gelen uygunluk esnekliğinin kullanım oranını ölçüyor.
2. **Adı değişsin mi?** → *"`TERCIH_KARSILAMA` kalsın."*

**Neden gerekti:** K-13 ile çalışan tercihi diye bir şey kalmadı; kuralın
besleneceği veri yoktu.

**Bilinen risk, kayda geçirildi:** ad ile anlam artık birebir örtüşmüyor.
`TERCIH_KARSILAMA` görüp *"çalışan tercihi özelliği var"* sanılabilir. Yeniden
adlandırma teklif edildi (ağırlık tablosu ve profil kayıtları o anda henüz
kullanılmadığı için bedava olurdu); Mustafa adın korunmasını seçti.

→ `02-spec/v1.4-master-spec.md` §5.4, §6.8

---

## K-23 · Kabul yetkisi = yayın yetkisi

**Karar (16 Eylül 2026, Mustafa).** *"Yayın yetkisi kimdeyse o."*

Yetki matrisine (§3.2) ayrı bir satır **eklenmedi**. İhlali kabul etmek, planı
yayınlama yetkisinin parçasıdır. Şef ihlali görür, gerekçe yazabilir, ama kabul
edemez — onaya gönderir.

**Bilinen sonuç:** ileride yayın yetkisi genişletilirse kabul yetkisi de
sessizce genişler. Ayrı satır olmadığı için bu bir karar noktası olarak karşımıza
çıkmaz.

→ `02-spec/v1.4-master-spec.md` §4.5, §8.6

---

## K-24 · `yasal` ve `kabul_edilebilir` iki ayrı alan; bayrak bazen satır bazlı

**Karar (16 Eylül 2026, Mustafa).** Sınıflandırma tablosu doldurulurken çıkan
iki sorunun çözümü onaylandı.

### Sorun 1 — iki grup yetmiyordu

`AKTIF_CALISAN` yasal bir kural değil; hiçbir kanun *"ayrılmış kişiye vardiya
yazma"* demiyor, çünkü gerek yok. İki gruplu tabloda bu "firma kuralı" olurdu
ve sistem yöneticiye *"ayrılmış çalışanı planda tutmayı kabul ediyorum"*
seçeneğini sunardı.

| Alan | Ne söyler |
|---|---|
| `yasal` | Kural kanundan mı geliyor, hangi maddeden |
| `kabul_edilebilir` | Yönetici bu ihlali kabul edip yayınlayabilir mi |

Üç grup oldu: **kanundan gelen** (yasal ✅, kabul ❌) · **imkânsızlık**
(yasal ❌, kabul ❌) · **firma kuralı** (yasal ❌, kabul ✅).

**Yan faydası:** hukuk uzmanı `yasal` sütununu düzelttiğinde yayın kapısı
bozulmaz.

### Sorun 2 — bayrak bazen kuralın değil, satırın özelliği

`YETKINLIK_KAPSAMASI` tek kural ama *"her vardiyada 1 ilk yardımcı"* ile
*"kahvaltıda 1 barista"* farklı cevap verir. Bu iki kuralda
(`ROL_KAPSAMASI`, `YETKINLIK_KAPSAMASI`) bayraklar **her gereklilik satırında**
tutulur; diğer 33 kuralda tip seviyesinde kalır.

→ `02-spec/v1.4-master-spec.md` §5.3, §6.4, §8.4

---

## K-25 · `GECE_POSTASI_DEVRI` — katalogda olmayan bir yasal kural

**Karar (16 Eylül 2026, Mustafa).** Mevzuat araştırmasında bulundu, eklendi.

Postalar Halinde İşçi Çalıştırılarak Yürütülen İşlerde Çalışmalara İlişkin Özel
Usul ve Esaslar Hakkında Yönetmelik **md. 8**:

> *"…en fazla bir iş haftası gece çalıştırılan işçilerin, ondan sonra gelen
> ikinci iş haftasında gündüz çalıştırılmaları suretiyle…"*

Katalogdaki üç gece kuralının hiçbiri bunu karşılamıyordu: `ARDISIK_GECE_LIMIT`
firma kuralıdır ve kapatılabilir, `VARDIYA_ROTASYON_YONU` yumuşaktır,
`GECE_VARDIYASI_AZAMI` süre kuralıdır.

`ARDISIK_GECE_LIMIT`'in **yerine geçmez, yanında durur**: biri kanunun tavanı,
diğeri firmanın daha sıkı uyku sağlığı politikası.

**Aynı araştırmada çözülen iki belirsizlik:**

| Kural | Sonuç | Dayanak |
|---|---|---|
| `PART_TIME_LIMIT` | ⚠️ → ✅ **yasal** | Fazla Çalışma Yön. md. 8 — *"kısmî süreli… işçilere fazla sürelerle çalışma da yaptırılamaz"* |
| `ARDISIK_CALISMA_GUNU` | ⚠️ → ❌ **firma** | Kanunda "6 gün" yok; `HAFTA_TATILI` kayan penceresinin türevi |

→ `02-spec/v1.4-master-spec.md` §6.2, §6.3 · `02-spec/v1.4-hazirlik/02-mevzuat-arastirmasi.md`

### ✅ Uygulandı — 30 Eylül 2026 akşamı

İki motor yarısında da yazıldı; geçmiş okunduğu için (T-28, K-42) artık
yazılabilirdi. Yanında `ARDISIK_HAFTA_SONU_LIMIT` de yazıldı.

**Yönetmeliğin tam metni okundu** — şartnamede yalnız 1. fıkranın bir parçası
vardı. İki fıkra daha kuralı ilgilendiriyor:

> *md. 8/3: "İşin niteliği ve yürütümü, iş sağlığı ve güvenliği gözönünde
> tutularak, gece ve gündüz postalarında iki haftalık nöbetleşme esası da
> uygulanabilir."* → `azami_ardisik_gece_haftasi` 2 yasal; parametrenin anlamı
> ve üst sınırı açık (**T-73**).
>
> *md. 7/2: "Çalışma süresinin yarısından çoğu gece dönemine rastlayan bir
> postanın çalışması, gece çalışması sayılır."*

**Uygulanan üç okuma:**

| soru | uygulanan | durum |
|---|---|---|
| hangi vardiya gece | **md. 7/2** — süresinin yarısından çoğu 20:00–06:00'da (brüt). Firma işareti (K-40) **bilerek kullanılmıyor**: yasal kuralı iki yönde de bozardı | Mustafa'nın onayı bekliyor (**T-72**) |
| hangi hafta gece haftası | **en sıkı:** haftada tek bir gece çalışması yeter | ürün kararı bekliyor (**T-72**) |
| hafta | plan haftası; vardiya başladığı günün haftasına yazılır | — |

**Ölçüldü** (iki aşamalı yol, 49 kişi): geçmişsiz çözülen ikinci haftada
**11 kişi** iki hafta üst üste gece çalışıyordu; geçmişle çözülen plan temiz ve
çözülebilir.

**Aynı okumada bulunan:** yasal gece sınırı (K-26) yalnız pencereye düşen
kısmı ölçüyor; md. 7'ye göre gece postasının **bütün** çalışma süresi 7,5 saati
geçemez (**T-74** 🔴). Kural bilerek değiştirilmedi — şartnamenin tanımı değişir.

→ `09-motor/dogrulayici/kurallar.py` (`gece_postasi_devri`,
`_yasal_gece_postasi_mi`) · `09-motor/cozucu/model.py` (`_gece_postasi_devri`) ·
`09-motor/testler/test_hafta_kurallari.py`

---

## K-26 · Gece sınırının sektör istisnası

**Karar (16 Eylül 2026, Mustafa).** Araştırmada bulundu, eklendi.

6645 sayılı Kanun (23 Nisan 2015) İş K. md. 69'a istisna getirdi: **turizm,
özel güvenlik, sağlık hizmeti ve petrol arama/sondaj** işlerinde, çalışanın
**yazılı onayıyla** gece 7,5 saat sınırı aşılabilir.

**Neden acil:** elimizdeki tek gerçek müşteri verisi bir **seyahat acentesine**
ait — turizm — ve o veride **182 atama gece yarısını aşıyor**. İstisna olmadan
sistem o firmada gece 8 saatlik vardiyayı yasal ihlal sayar, K-20 gereği kabul
seçeneği sunmaz ve plan yayınlanamaz. Oysa yazılı onay varsa tamamen yasaldır.

**İki yeni alan:** `tenants.sektor` (yasal sektör — kurulum sihirbazında ayrı ve
açık soru) ve `employees.gece_calisma_onayi` + tarih + belge.

**Kural:** ikisinden biri eksikse 7,5 saat sınırı yürürlüktedir.

**Bu, K-24'ün üçüncü biçimidir:** orada bayrak kural satırına bağlıydı, burada
**çalışana** bağlı. Aynı ilke — bir kuralın yasal olup olmaması bağlama göre
değişebiliyor.

→ `02-spec/v1.4-master-spec.md` §6.3, §8.1, §8.3

### ✅ Uygulandı — 30 Eylül 2026

`GECE_VARDIYASI_AZAMI` iki tarafta da yazıldı. Mustafa bu kuralı kalan 11
gövdesiz kural arasından seçti: *hukuki risk taşıyan tek yazılabilir kural.*

**Motorun okuduğu iki yeni alan:**

| alan | nerede | biçim |
|---|---|---|
| `sektor` | girdinin kökünde | `turizm` · `ozel_guvenlik` · `saglik` · `petrol` istisna; gerisi değil |
| `gece_calisma_onayi` | çalışan kartında | `true`, ya da `{"onay": true, "gecerli_bitis": "YYYY-AA-GG"}` |

**Ölçü net çalışma** — `GUNLUK_AZAMI` ile aynı gelenek: penceresine düşen mola
gece çalışmasından düşülür, pencere dışındaki düşülmez. **Kanun "geçemez"
diyor:** tam 7,5 saat ihlal değildir. **Z-5:** pencere gün sınırını aşarak
hesaplanır — 19:00–05:00'in gecesi 9 saattir, 4 değil.

**⚠ Tarihli onay + hafta tarihi yok → geçersiz sayılır.** `SOZLESME_GECERLI`
tarih yoksa hoşgörülüdür; burada değil, **bilerek**: bu yasal bir sınırın
kaldırılması, doğrulanamayan bir istisna o sınırı açmamalı. Tarihsiz onay
*"süresiz"* demektir ve geçerlidir.

**⚠ Çözücü doğrulayıcıdan bilerek daha katı** — T-68. Brüt ölçüyor; yasal bir
planı reddedebilir ama yasadışı plan üretmez.

**⚠ Veri seti kuralı zorlamıyor:** en uzun gece örtüşmesi 7,00 saat. Zorlayan
testler ve ihlal vakası. Sahnenin sektörü bilerek **istisna dışı**.

20 test (9 kırmızı kanıt + 6'sı kural yokken de yeşildi), 11 mutasyon, hepsi
öldü.

→ T-68 · `09-motor/dogrulayici/kurallar.py` · `09-motor/cozucu/model.py` ·
  `09-motor/testler/test_gece_vardiyasi_azami.py`

---

## K-27 · Adalet eşiği: ortalamadan 2 fazla

**Karar (16 Eylül 2026, Mustafa).**

> *"Eşik 2 diyebiliriz. Sayıdan ve geceden bazı kişilerin zaman zaman
> diğerlerinden 1 gün fazla çalışması gerekebilir ama ortalamadan 2 gece
> fazla çalışıyorsa bu adaletsizliktir."*

**Neden soruldu:** `ADALET_DENGESI` şartnamede tanımlıydı ama **ihlal eşiği
yoktu**. Doğrulayıcı yazılırken eşiği uydurmak, bir ürün kararını kodun içine
gizlemek olurdu; kural bilerek yazılmadı ve T-12 / A-17 olarak kaydedildi.
Bu karar ikisini de kapatıyor.

| Özellik | Değer |
|---|---|
| Ölçü | Kişinin yükü ile **grup ortalaması** arasındaki fark |
| Eşik | **2** (`adaletsizlik_esigi`, kiracı değiştirebilir) |
| Karşılaştırma | `sapma >= esik` — **2 dâhildir** |
| Yön | **Tek yönlü** — yalnız ortalamanın üstü |
| Pencere | Takvim ayı; devir yükü hesaba katılır |
| Boyutlar | `gece`, `hafta_sonu`, `cumartesi` — sayılabilir olanlar |

### ⚠ K-11 ile ters yönde

| Kural | Cümle | Sınır değeri |
|---|---|---|
| `VARDIYA_ARASI_DINLENME` | *"asgari 11 saat"* | 11 **ihlal değil** (K-11) |
| `ADALET_DENGESI` | *"2 gece fazla ise adaletsizlik"* | 2 **ihlaldir** (K-27) |

Biri bir **taban**, diğeri bir **sapma tavanı**. İkisi aynı yönde okunursa
biri yanlış uygulanır. Doğrulayıcıda bu ayrım iki ayrı testle sabitlendi.

**Tek yönlü olmasının gerekçesi:** ortalama sabittir — biri çok altındaysa bir
başkası mutlaka üstündedir ve o zaten yakalanır. İki yönlü saymak aynı olayı
iki kez yazar ve **az çalışan kişiyi adaletsizlikle suçlar**.

**Açık kalan:** `saat` boyutu. K-27 eşiği **sayı** olarak verdi; *"ortalamadan
2 saat fazla"* bambaşka bir büyüklük ve `SAAT_DENGESI` ile örtüşüyor olabilir.
**T-13** olarak kaydedildi, sessizce atlanmıyor (`eksik_boyutlar`).

→ `02-spec/v1.4-master-spec.md` §6.5 · `09-motor/dogrulayici/kurallar.py`

---

## K-28 · Çözücü ne zaman durur: erken dur, bekletme

**Tarih:** 16 Eylül 2026 · **Soran:** Claude · **Karar:** Mustafa

**Soru.** CP-SAT bütçesi 15 dakika. Optimuma çok yaklaşmışken kalan süreyi
sonuna kadar kullanmalı mı, yoksa *"yeterince iyi"* deyip dönmeli mi?

**Karar:** *"Erken dur, bekletme."*

| Durma koşulu | Değer |
|---|---|
| Optimuma yakınlık (nispi boşluk) | **%2** |
| İyileşme olmayan süre (durgunluk) | **2 dakika** |
| Mutlak bütçe (üstte) | 15 dakika |

**Gerekçe.** 3. dakikada bulunan planla 15. dakikadakinin farkı sahada
1–2 saatlik kapsamadır. Planı bekleyen yönetici için kalan 12 dakika daha
değerlidir. Çıktıdaki `durma_sebebi` hangi koşulun durdurduğunu söyler —
`optimum` / `hedef_bosluk` / `durgunluk` / `butce_doldu`.

→ `02-spec/v1.4-master-spec.md` §11.2 · `09-motor/cozucu/coz.py`

---

## K-29 · Adalet: eşik ihlali sayar, planı **gradyan** seçer

**Tarih:** 16 Eylül 2026 · **Kaynak:** motor yazılırken çıkan ölçüm ·
**Karar:** Mustafa — *"Onaylıyorum."* (16 Eylül) · **Durum:** ✅ kapandı

**Soru.** K-27 *"ne zaman ihlaldir"* sorusunu cevapladı (ortalamadan 2 fazla).
Peki **eşiğin altındaki** iki dağılım arasında motor neye göre seçer?

**Bulgu (tahmin değil, ölçüm).** Eşik tek başına amaç fonksiyonuna konduğunda
eşiğin altındaki bütün dağılımlar sıfır ceza aldı. *"Ç01 üçüncü kez
cumartesi"* ile *"Ç04 ilk kez cumartesi"* motor için **eşit değerdeydi**.
Ağırlığı 2'den 8'e çıkarmak hiçbir şeyi değiştirmedi — sıfırın sekiz katı
yine sıfır. **KAPSAMA ve CALISAN profilleri birebir aynı planı üretti.**
Yani şartnamenin *"üç bakışlı plan"* iddiası çalışmıyordu.

**Karar (uygulanan).**

| | Nerede | Ne yapar |
|---|---|---|
| Eşik (K-27) | Yalnız **doğrulayıcıda** | İhlali sayar, yayın kapısına bildirir |
| Gradyan (K-29) | Yalnız **motorda** | Eşiği aşmayan planlar arasında dengeli olanı seçtirir |

Gradyanın biçimi **artan marjinal maliyet**: üçüncü cumartesi ikinciden,
ikinci birinciden pahalıdır.

**İki yanlış biçim denendi ve ölçümle elendi:**

1. *"Ortalamanın üstündeki sapma"* → motor cumartesiye gerekenden fazla kişi
   koymaya başladı (3 yerine 5). Ortalamayı yükseltmek herkesin sapmasını
   düşürüyordu; ceza, cezalandırdığı şeyi ödüllendiriyordu.
2. *Eşik terimi amaç fonksiyonunda* → aynı açık: ihlali kaldırmanın ucuz yolu
   **başkalarına gereksiz cumartesi vermek**. Çıkarıldığında o anki 57 birim testinin
   ve 12 altın senaryonun hiçbiri değişmedi; terim zaten atıl duruyordu.

**Onaylandı.** *"Adalet"* eşiğin altında da bir **tercihtir**: motor eşiği
aşmasa bile daha dengeli dağılımı seçer. Üç plan kartının birbirinden farklı
çıkmasını sağlayan mekanizma budur.

→ `02-spec/v1.4-master-spec.md` §6.5 · `09-motor/cozucu/model.py`

---

## K-30 · Fazla mesai: hedef için asla, asgari zorlarsa minimum

**Tarih:** 16 Eylül 2026 · **Karar:** Mustafa · **Durum:** ✅ kapandı,
**kod değişmedi**

**Karar:**

> *"Zaten hedef hiç gitmemek. Gidilecekse de minimum gitmek. Mantığımız
> değişmedi."*

| Durum | Davranış |
|---|---|
| Yalnız **hedef** kapsama iyileşecek | Fazla mesai **yapılmaz** — hedef eksik bırakılır |
| **Asgari** kapsama (SERT) fazla mesaisiz tutmuyor | Fazla mesai **yapılır**, gereken kadar |
| Profil tavanı zorunlu aşıma yetmiyor | Plan **çözümsüz** olur |

**Soru kötü sorulmuştu ve Mustafa bunu söyledi:** *"ben tam neyi
cevaplayayım onu da anlamadım."* Soruyu *"bir saat fazla mesai kaç saatlik
açığa değer"* diye sormuştum — ürün dilinde değil, ceza katsayısı dilinde.
Doğru soru *"açığı fazla mesaiyle mi kapatalım, eksik mi bırakalım"*
olmalıydı ve cevabı zaten verilmişti.

**Ölçüldü: mevcut kod bu kararı zaten uyguluyor.** Küçük bir sahnede:

| Sahne | Fazla mesai | Sonuç |
|---|---|---|
| Asgari 2, hedef 3 (fazla mesai **opsiyonel**) | **0 saat** | Hedef %0'a düştü |
| Asgari 3 (fazla mesai **zorunlu**) | **12 saat** — tam gereken kadar | Plan üretildi |

Sayı değiştirilmedi. Üç test kararı çiviledi
(`09-motor/testler/test_profiller.py`).

### ⚠ Önceki ifadem yanlıştı — düzeltiliyor

*"§5.2'nin profil tavanı pratikte hiç kullanılmıyor"* demiştim. **Yanlış.**
Tavan ölü bir sayı değil: **zorunlu** aşımın ne kadarına izin verildiğini o
söylüyor. Aynı sahnede CALISAN profilinde (tavan 0) plan **çözümsüz**,
DENGELI (10) ve KAPSAMA'da (15) **çözülüyor**.

Doğrusu: tavan **isteğe bağlı** fazla mesai için hiç kullanılmıyor (ceza
karşılıyor), **zorunlu** fazla mesai için belirleyici.

→ `06-ACIK-RISKLER.md` T-15 (kapandı) · `09-motor/cozucu/model.py`

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

---

## K-31 · Yarım günlük izin motora gönderilmez — elle yönetilir

**Karar (25 Eylül 2026, Mustafa).** Yarım günlük izin/rapor sistemde
**kaydedilir** ama plan üretimine **girmez**. Yönetici planı editörle günceller,
asistan yerine kimin geçebileceğini önerir.

**Gerekçe, Mustafa'nın kendi cümleleriyle:**

> *"Yarım günlük bir rapor anca şu şekilde çalışır: ya çalışan bir gün önceden
> der ki hastanede işlerim var, öğlene kadar halledeceğim... yahut çalışan
> sabahtan rahatsızlanır ve öğlen hastaneye gider. Yarım günlük bir rapor
> önceden verilmez veya tahmin etmesi zordur. Bunu sistemin tutmasına gerek yok
> yani. Kullanıcı iznini girer, sistemde kayıt tutulur. Planı ilgili yönetici
> edit yardımıyla günceller."*

**Altında yatan ilke:** plan **hafta öncesinden** üretilir; yarım günlük izin
**aynı gün ya da bir gün önce** doğar. Çözücüye verilecek bir bilgi değil,
yayınlanmış plana yapılacak bir düzeltmedir.

| | |
|---|---|
| Nerede tutulur | `leaves`, `tum_gun = false` + `baslangic_saat`/`bitis_saat` (§8.3) |
| Motora gider mi | **Hayır.** `izinler` dizisi yalnız `tum_gun = true` taşır (§11.2) |
| Kim çözer | Yönetici, plan editörü + `/suggest` ile |

### ⚠ Bırakılan sınır — açıkça

Yönetici planı düzeltmeyi **unutursa** sistem bunu yakalamaz: kişi
çalışamayacağı bir vardiyaya atanmış görünür ve hiçbir kural itiraz etmez.
Bu bilinçli kabul edilen bir risktir; otomatik bekçisi yoktur.

### Bekçisi ne

Arka uç yarım günlük izni yanlışlıkla gönderirse motor **bütün günü** kapatır
— yanlış ama sessiz değil: `okunmayan_alanlar` raporu `izinler[].tum_gun`
satırını bildirir (23 Eylül'de T-19 ile açılan kanal). Bu, kararın tek
otomatik bekçisidir.

→ `02-spec/v1.4-master-spec.md` §11.2, §8.3

---

## K-32 · Mola ikiye ayrılır ve **dört ayrı süre** hesaplanır

**Karar (25 Eylül 2026, Mustafa).**

> ⚠ **Bu karar aynı gün bir kez yanlış yazıldı ve düzeltildi.** İlk hâli
> *"yasal hakkı `dinlenme` karşılar"* ve *"dinlenme ücretli olduğu için
> çalışma süresine dahildir"* diyordu. İkisi de yanlıştı; gerekçesi aşağıda,
> **Düzeltmenin kaydı** bölümünde.

### 1. Molanın iki tipi var — ayrım **ücret** eksenindedir

| Tip | Ücretli mi | Ücret hesabından | Çalışma süresinden | Bölünebilir mi |
|---|---|---|---|---|
| `yemek` | ❌ hayır | **düşülür** | **düşülür** | ❌ tek blok (K-14) |
| `dinlenme` | ✅ evet | düşülmez | **düşülür** | ✅ en az 15'er dk |

**Kritik ayrım:** bir molanın **ücretli** olması, o sırada **iş yapılıyor**
olması demek değildir. Ara dinlenme ücretli de olsa **çalışma süresinden
düşülür**; ücret tarafı ayrı bir büyüklüktür.

Kısa molanın ücretli sayılıp sayılmayacağı **sözleşmeye ve işyeri
uygulamasına** bağlıdır — yasal varsayılan değildir. Motor bunu girdiden
okur, kendisi varsaymaz.

### 2. Dört ayrı süre — tek bir "mesai süresi" toplamı YOK

| Büyüklük | Ne ölçer | Kim kullanır |
|---|---|---|
| **Vardiya aralığı** (`brut_saat`) | Baştan sona | `MOLA_HAKKI` eşiği (K-4) |
| **Çalışma süresi** (`net_saat`) | Bütün molalar düşük | `GUNLUK_AZAMI`, `HAFTALIK_AZAMI` |
| **Ücret hesabı** (`ucret_saat`) 🆕 | Yalnız ücretsiz mola düşük | Sözleşme saati, fazla mesai |
| **Görev kapasitesi** | Molada kimse sahada sayılmaz | Kapsama kuralları |

Aynı çalışanın bu dört değeri **farklı** olabilir ve ekranda **ayrı ayrı**
gösterilir. Örnek — 09:00–18:00, 60 dk yemek, 3×15 dk ücretli kısa mola:

```
vardiya araligi : 9 saat
mola toplami    : 1 saat 45 dk
calisma suresi  : 7 saat 15 dk      <- yasal sayac
ucret hesabi    : 8 saat            <- firma politikasinin sonucu
```

Bu sayede firmanın kabul ettiği ücretli molalar yüzünden sistem yanlışlıkla
*"45 dakika eksik çalıştı"* uyarısı üretmez.

### 3. Yasal ara dinlenme — yemek de sayılır, üstüne EKLENMEZ

`MOLA_HAKKI` (İş K. md. 68 · ≤4sa 15 dk · 4–7,5sa 30 dk · >7,5sa 60 dk)
**bütün ara dinlenmelerin toplamına** bakar. **Yemek arası bu ihtiyacı
karşılayabilir.**

> ⛔ **Sistem yemek arasının üzerine otomatik olarak bir saat daha
> eklememelidir.** 9 saatlik vardiyada 1 saatlik öğle arası md. 68'i
> karşılar; ayrıca 60 dk ücretli mola *zorunlu değildir*. Firma isterse
> verir — o zaman ücret hesabı büyür, yasal zorunluluk değişmez.

### 4. Yemek molasının yeri — göreli, mutlak değil

Yemek molası kişinin **kendi vardiyasının** en erken **3.**, en geç **5.**
saatinden sonra başlar. İkisi de **firma parametresidir** (2/4, 3/5, …).

Mutlak saatli pencere (`mola_en_erken: 12`) **kaldırılır**: şablona bağlıydı,
şablon paylaşılıyor ve 12:00'de başlayan vardiyada kural kendi kendini
patlatıyordu.

### 5. Yeni kural: `MOLA_YERLESIMI` — kapsam `K`, **YUMUŞAK**

Firma parametresi `MOLA_HAKKI`'nın üstüne binemez: onun kapsamı `S`, yasal ve
değiştirilemez (K-18'in aynı gerekçesi).

**Yumuşaktır, ve bu K-14'ün kendi mantığıdır:**

> *"Mola çıktısı öneri niteliğindeyse, mola sırasındaki kapsamayı sert kısıt
> yapmak kendi kendisiyle çelişirdi."* (K-14)

**Sert olan, hakkın verilmiş olmasıdır** (`MOLA_HAKKI`). **Nereye konduğu
yumuşaktır** (`MOLA_YERLESIMI`) — puan düşürür, yayını engellemez.

### 6. Mola politikası tanımlanır — firmada **ve** şablonda

Bugün şablonda tek bir sayı var (`mola_dk: 60`) ve bu sayı iki tipi, adedi ve
ücretliliği taşıyamaz. Politika bir **liste** olur:

```json
"mola_politikasi": [
  { "tip": "yemek",    "dakika": 60, "adet": 1, "ucretli": false },
  { "tip": "dinlenme", "dakika": 15, "adet": 3, "ucretli": true  }
]
```

**Nerede durur — ikisinde de (Mustafa, 25 Eylül).** Firma varsayılanı verir,
**şablon gerekirse ezer.** Gerekçe: *"biz 3×15 veriyoruz"* şirket kararıdır,
ama 4 saatlik cumartesi nöbetine 1 saatlik yemek konamaz — şablonun kendi
gerçeği vardır.

Yeni bir mekanizma değil: §5.2'nin çözünürlük merdiveni zaten bunu tarif
ediyor (kapsam `K` firma, `D` departman). Politika o merdivenin bir yolcusu.

**Adet, sıklık değil (Mustafa, 25 Eylül).** *"3×15 dk"* ile *"2 saatte bir
15 dk"* aynı şey değildir: 9 saatlik vardiyada ikisi de üç mola verir,
**12 saatlik** vardiyada biri üç öteki beş der. **Adet** seçildi — daha
öngörülebilir ve zaten şablon başına tanımlanıyor.

*"İki saatte bir 15 dk"* bütün çalışanlar için genel bir kanuni kural
**değildir**; işyeri politikası olarak tanımlanır.

⚠ **Politika yasal tavanı ezemez.** `MOLA_HAKKI` kapsamı `S`: politika
md. 68'in altına inen bir toplam üretirse **sert ihlal** yazılır. Politika
fazlasını verebilir, eksiğini veremez.
Bekçisi: `test_politika_yasal_tabanin_ALTINA_inemez`.

✅ **Uygulandı (28 Eylül).** Çözücü politikayı plana çeviriyor: yemek göreli
pencerede, dinlenmeler vardiyaya eşit dağıtılmış, hepsi kişiler arasında
kaydırılabilir. `_sahada` yeniden kuruldu — *"sahada olmak"* artık
`(kapsamayan yemek seçenekleri) − (kapsayan dinlenmeler)` olarak **doğrusal**
yazılıyor; yardımcı değişken ve reification gerekmedi, çünkü molalar
birbirini kesmiyor. 5 test.

### 7. Molalar çalışan ekranında görünmez — şimdilik

> *"Bu molalar çalışanların ekranlarında gözükmeyecek şimdilik. Yöneticilere
> adil plan ve yönetilebilir bir mola operasyonu sunmak amaçlı duracak."*

### ⏳ A-16'ya bağlı — doğrulanmadı

Buradaki yasal rakamlar (md. 68 eşikleri, ara dinlenmenin çalışma süresinden
sayılmaması, kısa molaların sözleşmeyle çalışma süresine dahil
edilebilmesi) **hukuk uzmanına doğrulatılmadı**. Şartname bu noktayı zaten
*"⚠️ Brüt/net yorumu açık (K-4, A-16)"* diye işaretlemişti. Model bu
rakamlardan **bağımsız** çalışır: eşikler parametredir, dört büyüklük
ayrımı yorumdan etkilenmez.

### Kabul cümleleri

1. Her molanın tipi vardır: `dinlenme` ya da `yemek`. Tipsiz mola bildirilir.
2. 09:00–18:00 vardiyada 60 dk `yemek` + 3×15 dk `dinlenme` verilirse:
   vardiya **9 saat**, çalışma süresi **7 saat 15 dk**, ücret hesabı
   **8 saat**. Üçü ayrı ayrı raporlanır.
3. 09:00'da başlayan vardiyada yemek **en erken 12:00**, **en geç 14:00**.
4. 12:00'de başlayan vardiyada yemek **en erken 15:00**, **en geç 17:00**.
   *(Bugün bu vardiyada kural hiç çalışmıyor.)*
5. Firma 3/5 yerine 2/4 derse plan buna uyar.
6. Yemek penceresi dışına konmuş plan **yumuşak** ihlal üretir — yayın
   engellenmez.
7. 9 saatlik vardiyada **yalnız 1 saat yemek** verilmişse `MOLA_HAKKI`
   **sağlanmıştır**; sistem üstüne mola eklemez ve ihlal yazmaz.
8. 15 dakikadan kısa bir `dinlenme` bloğu **sert** ihlal.
9. İki bloğa bölünmüş `yemek` **sert** ihlal (K-14).
10. Ücretli mola, sözleşme saati karşılaştırmasında **düşülmez**; çalışma
    süresi sayacında **düşülür**. İkisi aynı anda doğrudur.

### Düzeltmenin kaydı — 25 Eylül, aynı gün

**İlk hâli neyi yanlış söylüyordu:**

| İlk yazılan | Doğrusu |
|---|---|
| *"Yasal hakkı `dinlenme` karşılar"* | Bütün ara dinlenmeler sayılır; **yemek de karşılar** |
| *"Dinlenme ücretli, o halde çalışma süresine dahil"* | **Ücretli olmak ≠ iş yapıyor olmak.** İki ayrı eksen |
| *"Motor günde 1 saat eksik hesaplıyor"* | **Hesap doğruydu.** Eksik olan yanlış bir büyüklük değil, **hiç olmayan** bir büyüklüktü (ücret hesabı) |
| *"A08 fikstürü kırılıyor, yeniden onaylanmalı"* | **A08 doğruymuş.** Kıran şey K-32 değil, yanlış modeldi |

**Nasıl yakalandı:** Mustafa taslağı haftalık dış incelemeye (GPT) verdi.
Kendi ölçümüm bunu bulamazdı — **yanlış modeli doğru ölçüyordum**, ve her
test yeşil yanıyordu.

> **16 Eylül'de dış inceleme döngüsünü kurarken yazdığımız gerekçe buydu:**
> *"aynı model aynı kör noktayı iki kez taşır."* İlk sefer kör nokta kodda
> çıkmıştı; bu sefer **tasarımda** ve **bendeydi**. Kod gönderilmeden önce
> yakalandı.

**Dört büyüklük ayrımı ve *"yemeğin üstüne otomatik saat eklenmez"* kuralı
dış incelemeden geldi**, bu kayda aynen alındı.

→ `02-spec/v1.4-master-spec.md` §6.2, §11.2 · K-14 (düzeltildi), K-18, K-4, A-16

---

## K-33 · Firma **sahada** kaç kişi ister — `SAHADA_ASGARI`

**Karar (28 Eylül 2026, Mustafa).**

> ⚠ **Bu karar da bir kez yanlış yazıldı ve aynı gün düzeltildi.** İlk hâli
> kuralı `MOLA_ASGARI_SAHADA` diye adlandırıyor ve tabanı talep tablosunun
> `asgari`si ile sınırlıyordu. Gerekçesi aşağıda, **Düzeltmenin kaydı**
> bölümünde.

### Neden gerekti

Mustafa: *"Mola için şöyle bir kural gerekebilir: ilgili saatte çalışması
gereken minimum çalışan sayısını firmanın tanımlaması gerekebilir. Biz saat
başı kafamıza göre kişileri yollayamayız."*

Ölçülen durum (28 Eylül, üç kişilik plan, hücre `asgari` 2):

| saat | 11 | 12 | 13 | 14 |
|---|---|---|---|---|
| sahada | 3 | **0** | **0** | 3 |

Sert ihlal **0**, `yayınlanabilir` **True**. Üçü de aynı anda molada ve plan
temiz görünüyordu.

Sebep kod değil **K-14**: `MOLA_KAPSAMASI` bilerek YUMUŞAK. O karar kişi
başına *tek* öğle arası varken verildi; motor artık kişi başına **dört** mola
üretiyor ve aynı dişsiz kural tabanı tamamen boşaltıyor.

### Karar

`MOLA_KAPSAMASI` **yumuşak kalır** (K-14 ayakta; planı `asgari`ye doğru iter).
Yanına **SERT** bir saha tabanı gelir: `SAHADA_ASGARI`, parametre
`asgari_sahada`. İkisi ayrı iş yapar, biri ötekinin yerine geçmez.

| | sayar | mola |
|---|---|---|
| `ASGARI_KAPSAMA` | o saate **atanmış** kişi | sayılır |
| `SAHADA_ASGARI` | o saatte **sahada** olan kişi | düşülür |

Fark tam da molalardır. Müşterinin gördüğü ikincisidir.

### ⚠ Düzeltmenin kaydı

İlk yazımda kural `min(parametre, hücrenin asgarisi)` ile sınırlanıyordu ve
hem doğrulayıcıda hem çözücüde *"firma **molada** en az 5 dese de..."* diye
açıklanmıştı. Bundan daha kötüsü: `test_taban_hucre_ASGARISINI_asamaz` adlı
bir test **bu hatayı sabitliyordu** — yani hatayı kalıcı hâle getiren şey
testin kendisiydi.

> **Mustafa:** *"Firma molada en az 5 demeyecek, firma sahada en az 5
> diyecek, yanlış mantık kurma lütfen."*

İki ayrı hata vardı:

1. **Yanlış cümle.** Firma *"molada en az 5"* demez, *"**sahada** en az 5"*
   der. Parametre bir mola kotası değil, **saha tabanıdır**. Kuralın adı da
   bu yüzden `MOLA_` ile başlamamalı — `SAHADA_ASGARI` oldu.
2. **Yanlış mantık.** `min(...)` firmanın sayısını sessizce talep tablosunun
   sayısıyla değiştiriyordu: firma 5 der, hücre 2 isterse motor 2 uygular ve
   firmanın cümlesi buharlaşırdı.

Sınır kaldırıldı; parametre olduğu gibi uygulanır. O test silinmedi,
**tersine çevrildi**: `test_taban_TALEBE_boyun_egmez` artık tabanın talep
tablosuna boyun eğmediğini korur. (Mutasyonla sınandı: eski `min(...)`
mantığı geri konduğunda test kırmızı oluyor.)

### Taban talebi yukarı çekebilir — bu kasıtlıdır

Firma 5 derken hücre 2 kişi istiyorsa iki SERT kural aynı anda geçerlidir ve
**katı olan bağlar**: o saatte en az 5 kişi sahada olmak zorundadır,
dolayısıyla en az 5 kişi atanır. Talep tablosu işin gerektirdiğini söyler,
firma tezgâhta görmek istediğini; ikisi çelişirse motor birini ötekine tercih
etmez.

Çelişki planı çözümsüz bırakabilir. Çözümsüzlük **sessiz değildir** — teşhis
katmanı sebebi yazar. Sessizce gevşetmek yerine yüksek sesle durmak bu
projenin tercihi (§7.6).

**Nereye uygulanır:** talep hücresi **olan** her saate; hücrenin kendi
`asgari`sine bakılmaz. Firmanın talep yazmadığı saatte (kapalı dönem) taban
da yoktur — o saatte saha diye bir şey yoktur.

### 🔴 Açık bulgu: bugünkü mola geometrisi bu kuralı boğuyor

Kural yazıldı ve çalışıyor, ama **bugünkü mola yerleşimiyle plan ancak
`N ≥ 4F` iken çözülüyor** (N = ekipteki kişi, F = taban). 15 senaryo
ölçüldü, formül 15/15 tuttu.

09:00–18:00 vardiya, 1 yemek + 3×15 dk dinlenme için aday pencereler:

| mola | aday saatler |
|---|---|
| yemek | 12, 13, 14 |
| dinlenme #0 | 11, 12 |
| dinlenme #1 | 13, 14 |
| dinlenme #2 | 15, 16 |

Kişi başına dört molanın **üçü** `{11,12,13,14}` dört saatine sıkışıyor:
`4(N−F) ≥ 3N` → `N ≥ 4F`. Saat **9, 10 ve 17'ye hiçbir mola düşemiyor**.

Yani taban 3 isteyen bir firmanın o vardiyada **12 kişisi** olmak zorunda.
Gerçekçi değil.

İki ayrı maliyet, ayrı ayrı ölçüldü:

| kaynak | etkisi | ne gerektirir |
|---|---|---|
| **pencere darlığı** | eşik `4F` → `~1.8F` | aday penceresini ±2 saate açmak — yerel değişiklik |
| **saat yuvarlaması** | `~1.8F` → `~1.24F` | ⚠ Şişme **yemekte 1.00×, dinlenmede 4.00×**; önceki "2.29×" ikisini harmanlıyordu (bkz. K-34). → K-34 ile kaldırıldı |

Baskın maliyet **pencere darlığı** — bu beklenmiyordu, ölçüm gösterdi.
Pencereyi ±2'ye açmanın "eşit dağıtım" kararına (K-32, 25 Eylül) maliyeti de
ölçüldü: dinlenmeler arası ortalama boşluk 2.12 sa → 2.83 sa (ideal 2.25),
en küçük boşluk iki durumda da 1.00 sa. Adalet çökmüyor.

~~**Karar bekliyor** → T-44.~~ ✅ **Çözüldü 28 Eylül, K-34** — zaman birimi çeyrek saate indi, eşik `4F → 12F/7`.

→ `02-spec/v1.4-master-spec.md` §6.2 · K-14, K-32, T-44

---

## K-34 · Motorun zaman birimi **çeyrek saat**

**Karar (28 Eylül 2026, Mustafa).**

> *"Molalar zaten normalde planlanırken, gün içinde 15 dk lık dilimlere
> dağıtılıyor. Yani 15:15'e de mola koyabiliyorlar, 15:30'a da 15:45'e de.
> Doğrusu bu."*

Bu bir hız/maliyet kararı değil **doğruluk** kararı. Saat izgarası bir
modelleme kolaylığı sanılıyordu; gerçekte mola operasyonu çeyrek saatle
yapıldığı için izgara **gerçeğe aykırıydı**.

### ⚠ Yemek ile dinlenme ayrı şeylerdir

> **Mustafa:** *"Yemek ile molayı birbirine karıştırma."*

Bu uyarı, T-44'e yazdığım **"2.29× şişme"** rakamının neyi gizlediğini
ortaya çıkardı. Ayrıştırınca:

| | gerçek | modelde | şişme | |
|---|---|---|---|---|
| **yemek** | 60 dk | 60 dk | **1.00×** | hata yok |
| **dinlenme** | 45 dk (3×15) | 180 dk | **4.00×** | hata burada |
| toplam | 105 dk | 240 dk | 2.29× | ← benim yazdığım |

**2.29× harmanlanmış bir rakamdır** ve yemeğin doğruluğunu dinlenmenin
hatasıyla ortalar. Düzeltme dinlenmeyi düzeltir, yemeği **olduğu gibi
bırakır**. T-44 kaydındaki tablo bu yüzden düzeltildi.

### Ne değişti

| | eski | yeni |
|---|---|---|
| iç zaman birimi | 1 saat | **15 dk** |
| 15 dk mola kaç dilim kaplar | 4 (bir tam saat) | **1** |
| 60 dk yemek kaç dilim kaplar | 4 | **4** (değişmedi) |
| dinlenme aday sayısı (9 sa vardiya) | molaya 2 | molaya **9** |
| eşit dağıtım noktaları | 11, 13, 15 (yuvarlanmış) | **11:15, 13:30, 15:45** (tam isabet) |
| kapsama kontrolü | saat başı | **her çeyrekte** |

**Girdi sözleşmesi DEĞİŞMEDİ** (§11.2). Talep yine saatlik okunur; bir
saatlik hücrenin değeri o saatin dört çeyreğinin her birine uygulanır.
Hücre bölünmez, yalnızca daha sık **örneklenir**. Fikstürler ve altın
senaryo girdileri aynen geçerli.

### Ölçülen sonuç

**T-44 kapandı.** Eşik `N ≥ 4F` → **`N ≥ 12F/7`** (~1.71×F), 15 senaryoda
15/15:

| taban | eskiden gereken ekip | şimdi |
|---|---|---|
| 2 | 8 kişi | **4** |
| 3 | 12 kişi | **6** |
| 5 | 20 kişi | **9** |

**Çözüm süresi** — T-44'te *"bilmiyorum"* dediğim sayı, artık ölçüldü:

| senaryo | süre |
|---|---|
| 8 kişi, taban 2 | 0.14 sn |
| 20 kişi, taban 4 | 0.37 sn |
| 40 kişi, taban 5 | 0.78 sn |

Model dört kat büyüdü, maliyeti pratikte yok. Kaygı yersizmiş — ama
ölçmeden bilinemezdi.

### Kalan sınır (~1.71×F) bir modelleme hatası **değil**

5 kişi / taban 3 senaryosunda kısıtlar **tek tek gevşetilerek** bulundu:

| gevşetilen | sonuç |
|---|---|
| hiçbiri | çözümsüz |
| `MOLA_HAKKI` kapalı | çözümsüz |
| yemek yok, yalnız 3×15 dinlenme | çözümsüz |
| **dinlenme yok, yalnız yemek** | **çözüldü** |
| **yemek 60 → 30 dk** | **çözüldü** |

Bağlayan şey **yemek ile ortadaki dinlenme molasının aynı dilimler için
yarışması**. Yemek 4 çeyrek kaplar ve penceresi vardiyanın ortasındadır;
ortadaki dinlenme de oradadır. `{12:00..15:00}` arasındaki 12 çeyrekte:

```
4N (yemek) + N (dinlenme#1)  ≤  12(N − F)   →   N ≥ 12F/7
```

Bu gerçek bir planlama gerilimi: insanlar öğle yemeğini günün ortasında
ister, ortadaki dinlenme molası da oradadır. Yemek penceresini genişletmek
eşiği **değiştirmedi** (ölçüldü: 3–5, 3–6 ve 2–7 saat pencerelerinin üçü de
taban 3 için 6 kişi verdi).

### 🔴 Yol üstünde bulunan sessiz geçiş — kapatıldı

K-34 uygulanırken K-33'ü doğuran sessiz geçişin **aynısı** bulundu, bu kez
bir çeyreğin içine saklanmış:

> İki kişilik planda ikisi de **14:15–14:30** arası molada. 14:00'de ve
> 15:00'te sahadalar. **14:15'te sahada sıfır kişi.**
> Doğrulayıcı: **hiçbir ihlal yok.**

Sebep: `_talep_hucreleri` tam saat üretiyordu, kural yalnız o anlara
bakıyordu. Molayı çeyreğe taşıyıp kontrolü saatte bırakmak sessiz geçişi
**düzeltmek değil gizlemek** olurdu — ihlal artık daha kolay saklanırdı.

`SAHADA_ASGARI` ve `MOLA_KAPSAMASI` çeyrek bazına indirildi. İkincisinde
hücre başına **tek** ihlal yazılır (saatin en kötü çeyreği); dört ayrı satır
yazmak aynı boşluğu dört kez sayar ve puanı sessizce dört katına çıkarırdı.

### Bekçiler (mutasyonla sınandı)

| mutasyon | kırmızı yanan |
|---|---|
| saat yuvarlaması geri kondu | 2 test |
| pencere yarıçapından mola süresi çıkarıldı | `test_adaylar_AYRIK` |
| taban yine yalnız tam saatte bakıyor | `test_GEOMETRI_SINIRI` |

Üçüncüsü yalnız sınır kaydı tarafından yakalandı — zayıftı; doğrudan
bekçisi `test_taban_CEYREKTE_delinirse_de_gorulur` olarak eklendi.

→ `02-spec/v1.4-master-spec.md` §6.3 · K-32, K-33, T-44 (kapandı)

---

## K-35 · Süre seçimi, **kanıtlanmış** optimuma yakınlık ve "İyileştir"

**Karar (28 Eylül 2026, Mustafa).**

### Çözülen sorun: aynı girdi, farklı plan

Motor aynı girdiye her seferinde aynı planı vermiyor. Ölçüldü (35 kişilik
sahne, 25 saniye, iki koşu): **21.905** ve **22.715**.

Sebep paralel çalışma — sekiz arama işçisi aynı anda arıyor ve hangisinin
önce iyi bir plan bulduğu her koşuda değişiyor. Birbirine çok yakın binlerce
plan var; hangisinin geldiği yarışa bağlı.

Tekrarlanabilirlik mümkün ama bedeli ağır. Ölçüldü:

| ayar | koşu 1 | koşu 2 | aynı mı |
|---|---|---|---|
| 25 sn, 8 işçi | 21.905 | 22.715 | ❌ |
| 25 sn, **1 işçi** | 1.010.039 | 1.010.039 | ✅ |

Tek işçiyle aynı sürede üretilen plan **46 kat kötü**. Yani *"her seferinde
aynı"* istemek, *"her seferinde çok daha kötü"* demek.

> **Mustafa:** *"Yönetici tekrar çalıştırdığında daha iyi bir plan gelip
> gelmeyeceğini nasıl bilecek? Bunu bilmezse nasıl güvenecek?"*

### Karar: tekrarlanabilirlik değil, **görünürlük + birikim**

**1. Süre seçimi — üç seçenek: 10 / 15 / 30 dakika.**

⚠ Seçeneklerin yanına *"%85 optimum"* gibi yüzde **yazılmaz**. Optimuma
yakınlık senaryoya göre değişir; 50 kişilik bir dükkânla 500 kişilik bir
operasyonun eğrisi aynı değildir. Önden yüzde söz vermek çoğu kiracıda
yalan olur.

**2. Sonuç kartında kanıtlanmış yakınlık gösterilir.**

Çözücü optimumun alt sınırını (`BestObjectiveBound`) matematiksel olarak
kanıtlar. *"Bu plan teorik en iyisinin %90'ı kadar iyi"* bir tahmin değil,
garantidir. Yönetici böylece *"tekrar denesem daha iyisi gelir mi"*
sorusunu **kendi planı için** cevaplar: boşluk %2 ise denemeye değmez,
%25 ise değer.

Bu, önden ortalama yüzde göstermekten güçlüdür — çünkü onun planı hakkında.

**3. "İyileştir" düğmesi — plan başına bir kez.**

Sıfırdan üretmez; mevcut planı çözücüye başlangıç noktası (hint) olarak
verir. Çözücü amacı küçülttüğü için **plan asla kötüleşmez**. Yönetici zar
atmıyor, biriktiriyor.

Ölçüldü (35 kişilik sahne, üç adım):

| adım | süre | optimuma yakınlık |
|---|---|---|
| 1 | 15 sn | %24,5 |
| 2 | +20 sn | %44,3 |
| 3 | +25 sn | %71,2 |

Geçersiz bir başlangıç planı (girdi değişmişse) sessizce yok sayılmaz,
**bildirilir**. *"İyileştirdim"* deyip aslında zar atmak, çözmeye
çalıştığımız güveni daha da bozardı.

### ⚠ Neden "İyileştir" asıl yol değil

Ölçüldü — aynı 60 saniye, iki farklı şekilde:

| | optimuma yakınlık |
|---|---|
| **tek seferde 60 sn** | **%93,0** |
| 15+20+25 sn (üç adım) | %71,2 |

Her yeniden başlayışta çözücü kendi iç birikimini kaybediyor; ipucu
**planı** koruyor ama **aramayı** korumuyor. Bu yüzden kullanıcı önden
makul bir süre seçmeli; "İyileştir" sonucu görüp *"biraz daha"* demek
isteyene ikinci şanstır, birincil yol değil.

Plan başına bir kezle sınırlı olmasının sebebi de bu (ve maliyet).

**4. Problem büyüklüğü ekranda gösterilir.**

Mustafa (14 Eylül): *"müşteri de bu verileri istatistiki olarak görebilir,
örnek 17.000 değişken… etkileyici olabilir."* 28 Eylül'de 350 kişilik
gerçekçi sahnede ölçülen: **335.072 değişken · 423.489 kısıt · 39 kural**.
`cozum_istatistikleri` bunları zaten üretiyor (§11.3).

### Maliyet

**Yapay zeka maliyeti yok.** Planlama motoru bir kısıt çözücüsüdür (CP-SAT),
dil modeli değil. Token harcamaz.

İşlem maliyeti plan başına birkaç sent mertebesinde. Asıl risk çarpan:
3 öncelik × 3 süre seçeneği. "İyileştir"in plan başına bir kezle
sınırlanması bu yüzden.

→ `02-spec/v1.4-master-spec.md` §9.4, §11.3 · K-28 · `09-motor/cozucu/coz.py`

---

## K-36 · Arama işçisi sayısı **makinenin çekirdeğine** uyar

**Karar (29 Eylül).** Çözücünün arama işçisi sayısı koda sabit yazılmaz;
çalıştığı makinenin kullanılabilir çekirdek sayısından okunur.

**Nereden çıktı.** Mustafa'nın sorusu şuydu:

> *"Bu 15 dk süren koşuyu daha hızlı bir makinede koşsak kısa sürer mi?
>  Cloud ortamdan ciddi kapasitesi olan bir sunucu alsam işe yarar mı?"*

Sunucu almadan önce **ücretsiz olan** düzeltme buydu.

**Ölçüldü — ama iki makine iki ayrı şey söyledi.**

35 kişilik sahne, her satıra aynı süre, erken durma kapalı:

| işçi | **2 çekirdek** (45 sn) | **6 çekirdek** (60 sn) |
|---|---|---|
| 1 | **plan bulunamadı** | — |
| 2 | %7,0 | %3,1 |
| 4 | %24,2 | %2,9 |
| 8 *(eski sabit)* | %23,6 | %2,3 |
| 16 | — | %1,4 |

**⚠ İlk yazımda bu madde *"makinede olmayan çekirdeği istemek planı
kötüleştirir"* diyordu.** Yalnız **dar** makinede doğru. 6 çekirdekli
makinede bütün satırlar optimuma %1,4–%3,1 arasında — aradaki fark, aynı
ayarın **kendi zar payından** küçük (28 Eylül'de ölçüldü: aynı girdi, aynı
25 saniye → 21.905 ve 22.715). Yani geniş makinede **bu sahne soruya cevap
vermiyor**; birer koşudan genelleme çıkarmak 28 Eylül'deki *"117 saniye =
beklenen ~2 dakika"* hatasının aynısı olurdu.

**İki ölçümün ORTAK dediği şey — kararın dayanağı bu:**

* Sabit sayı **dar makinede açıkça zararlı** (%7,0 → %23,6). CI'ın
  makineleri 2 çekirdekli, yani bu bizim kendi koşumuz.
* Sabit sayı **geniş makinede çekirdekleri israf eder**: 32 çekirdekli bir
  sunucuda da 8 işçi koşacaktı.

**Gerçekçi ölçekte ölçüldü (29 Eylül akşamı) — soru kapandı.**

Mustafa 350 kişilik sahnede, 6 çekirdekli makinesinde, her satırı iki kez
koşturdu. Amaç değerinin **ortancası** (küçük iyi):

| işçi | 350 kişi · 120 sn | 350 kişi · 360 sn |
|---|---|---|
| 2 | 321.270 | 151.388 |
| **6** *(= çekirdek)* | **224.007** | **119.966** |
| 12 | 236.846 | 125.114 |

**Her iki bütçede de çekirdek sayısı kadar işçi kazandı.** 2 işçi ile 6
işçi arasındaki fark, aynı ayarın zar payından **üç kat büyük** — yani
bu sefer ölçüm gerçekten ayırt ediyor. 12 işçi 6'yı geçemedi.

**Küçük ölçek soruyu cevaplayamıyor:** aynı makinede 0.1 ve 0.3 ölçekte
bütün satırlar zar payının içinde kaldı. Bu yüzden araç artık satır içi
yayılmayı satırlar arası farkla karşılaştırıyor ve ayırt edemediğinde
**karar verdirmiyor**.

**Sunucu sorusunun cevabı da bu düzeltmeden önce verilemezdi:** 32 çekirdekli
bir makinede de 8 işçi koşacaktı, yani ödenen çekirdeklerin çoğu boş dururdu.

**Ölçüm aracı.** `08-motor-testleri/gercekci-veri-seti/cekirdek-olc.py` aynı
sahneyi farklı işçi sayılarıyla, aynı süre bütçesiyle koşar ve tabloyu
çıkarır. Sunucu kararı tahmine değil bu tabloya dayanır — 28 Eylül'de bir
makinede ölçülen 117 saniyeyi *"beklenen ~2 dakika"* diye yazıp yanılmıştık.

**Elle verilen sayı korunur.** Ölçüm aracı tam olarak buna dayanıyor; ayrıca
bir müşteri makinesinde bilinçli olarak sınırlamak gerekebilir.

→ K-28 · K-35 · `09-motor/cozucu/model.py` (`cekirdek_sayisi`, `isci_sayisi`) ·
  `09-motor/testler/test_isci_sayisi.py`

---

## K-37 · *"İmkânsız"* ile *"yetiştiremedim"* ayrı cevaplardır

**Karar (29 Eylül, Mustafa).** Çözücü plansız döndüğünde iki ayrı durum
var ve artık iki ayrı cevap veriliyor:

| çözücü ne dedi | motorun `durum`u | teşhis | `teshis_kesin` |
|---|---|---|---|
| `INFEASIBLE` — kanıtladım | `cozumsuz` | koşar | `true` |
| ön kontrol — hücreye ulaşan vardiya yok | `cozumsuz` | (ucuz yol) | `true` |
| `UNKNOWN` — süre doldu | **`sure_yetmedi`** | **koşmaz** | — |
| süre doldu **+ kullanıcı istedi** | `sure_yetmedi` | koşar | **`false`** |

**Neden.** Bir yöneticiye *"çözümsüz"* demek, *"bu talebi bu kadroyla
karşılamak imkânsız"* demektir — personel alımına ya da talep düşürmeye
kadar giden bir karar. Oysa gerçek *"biz yetiştiremedik"* olabilir.

Teşhisin kendisi de ucuz değil: her sert kuralı tek tek gevşetip yeniden
çözüyor. **Ölçüldü: 45 saniyelik bütçe, toplam 470 saniye.** Kullanıcı
bütçesini bekledikten sonra 7 dakika daha bekliyor ve sonunda muhtemelen
yanlış bir cümle alıyordu.

**"Neden olduğunu araştır" düğmesi (Mustafa'nın onayladığı çözüm).**
Teşhis kullanıcı isterse koşar. Böylece 7 dakikalık bekleme onun bilinçli
seçimi olur, bizim sessizce ödetttiğimiz bir bedel değil.

⚠ **İstenerek koşan teşhis de KANIT DEĞİLDİR** ve çıktıda öyle işaretlenir
(`teshis_kesin: false`). Gevşetilmiş modeli çözmek de 10 saniyeyle sınırlı;
bulunan şey *"bu kuralı kaldırınca 10 saniyede çözülüyor"*, bulunamayan şey
*"kaldırmasam da 20 saniyede çözülecekti"*. Düğme arkasına saklı yanlış bir
cümle, ekranda duran yanlış cümleden iyi değildir.

**Ekranda.**

* `cozumsuz` → *"Bu plan üretilemez. Engelleyen: …"*
* `sure_yetmedi` → *"Verilen sürede plan bulunamadı."* + **süreyi uzat** +
  **neden olduğunu araştır**

**Şartname §11.3 çıktı sözleşmesi değişti**: `durum` artık üç değer alabilir.
Yan etkisi ölçüldü: altın senaryolar (A03, A09) kanıtlanabilir çözümsüzlük
kullandıkları için `cozumsuz` dönmeye devam ediyor — 12'si de yeşil.

→ K-10 · K-35 · `09-motor/cozucu/coz.py` · `09-motor/cozucu/teshis.py`
  (`teshis_koy(..., kesin=)`) · `09-motor/testler/test_sure_yetmedi.py`

---

## K-38 · `HAFTALIK_AZAMI` **normal çalışma sınırıdır**, toplam tavan değil

**Karar (29 Eylül, Mustafa).** *"Normal çalışma sınırı. Toplam tavan değil.
Yani minimum 45 saat çalışmalı."*

Toplam saat 45'i **aşabilir**; aşan kısım fazla mesaidir ve kendi tavanına
tabidir (profile bağlı: CALISAN 0 · DENGELI 10 · KAPSAMA 15), üstüne günlük
11 saat sınırı ayrıca geçerlidir.

**Ne bozuktu.** Çözücü iki kisit koyuyordu ve **bağlayıcı olan yanlışıydı**:

```python
dakika <= HAFTALIK_AZAMI                  # 45  <- toplamı burada kesiyordu
dakika <= sozlesme + fazla_mesai_tavani   # 55
```

45 saat sözleşmeli bir çalışan zaten 45'te duruyordu: **fazla mesai
matematiksel olarak imkânsızdı**. K-30'un *"asgari zorlarsa minimum fazla
mesai"* dalı, ceza değişkeni ve profile bağlı tavan bu çalışanlar için **ölü
koddu** — yani Mustafa'nın *"çözümsüzse başvururuz"* dediği kaçış yolu kapalıydı
ve motor onun yerine *"bu talebi bu kadroyla karşılayamazsınız"* diyordu.

**Ölçüldü** — aynı sahne, tek değişen parametre:

| `HAFTALIK_AZAMI` | sonuç | en çok çalışan | fazla mesai |
|---|---|---|---|
| 45 | **çözümsüz** | — | — |
| 55 | çözüldü | 48 saat | 48 saat *(6 kişi × 8)* |

**Tavan kalkmadı, yeri değişti**: toplam hâlâ sınırlı, sınır artık
*normal çalışma + fazla mesai tavanı*.

⚠ **Mutasyon testi bir boşluk yakaladı.** Düzeltme yazıldıktan sonra haftalık
kisit **tamamen silindiğinde bütün testler yeşil kaldı**: sözleşmesi olan bir
çalışanda `sözleşme + tavan` kisiti zaten daha dar olduğu için haftalık tavan
hiç bağlamıyordu. Altıncı bir test eklendi (sözleşme saati verilmemiş çalışan,
10 net saatlik vardiya × 6 gün = 60 saat) ve mutasyon artık ölüyor.

**Açık kalan (ürün kararı).** *"Minimum 45 saat çalışmalı"* kısmı
`SAAT_DENGESI` kuralıdır ve bugün **yumuşak, tek taraflı, 2 saat toleranslı,
doğrulayıcıda gövdesiz** (T-51). Sert yapılması %85 talepli veri setini
tanım geregi çözümsüz kılar — çünkü orada sözleşmeleri dolduracak kadar
talep yoktur. Bu yüzden önce **doğrulayıcı gövdesi** yazılmalı: eksik
planlanan saat ölçülebilir ve **parası görünür** hale gelmeli.

→ K-30 · T-51 · T-52 · `09-motor/cozucu/model.py` (`_sure_sinirlari`) ·
  `09-motor/testler/test_fazla_mesai_yolu.py`

---

## K-39 · Sözleşme saati **doldurulur**; yarı zamanlı tavanı **mevzuattan** gelir

**Karar (29 Eylül, Mustafa).** *"Haftalık 45 saati için ödeme yaptığı bir
çalışanı 43 saat çalıştırmaz. Böyle plan yapmaz. Bunu esnetemeyiz."*

Gerekçe **ticari**, yasal değil: Türkiye'de tam zamanlıya saat başına değil
net maaş ödenir; eksik planlanan saat, ödenmiş ama kullanılmamış saattir.

### Tam zamanlı — taban var, sert

```
günlük norm = haftalik_saat / gun_sayisi        (yeni alan; yoksa 6)
gereken     = haftalik_saat - (onaylı izin günü × günlük norm)
planlanan  >= gereken
```

⚠ **İzin borç düşürür, müsaitsizlik düşürmez.** Yıllık izin ücretlidir — o
saatin parası zaten ödeniyor. Uygunluk takvimi (*"o gün çalışamam"*) bir
ödeme değil bir kısıttır; borç aynen durur. İkisini aynı saymak, çalışanı
eksik çalıştırıp *"olsun, zaten müsait değildi"* demek olurdu.

⚠ **`gun_sayisi` olmadan izin saate çevrilemez**: aynı 45 saat, 6 günlük
desende bir izin günü 7,5 saat; 5 günlük desende 9,0 saat eder. Bu, **girdi
sözleşmesine yeni bir alan** demektir (§8.3 / §11.2).

### Yarı zamanlı — kişiye özel taban yok, tavan mevzuattan

Mustafa: *"Bizim çalışan için şu kadar saat max veya min çalışabilir diye
kisıt girmemize gerek yok. Yapmamız gereken sadece çalışanın çalışabileceği
kısıtlı günler veya saat aralıkları varsa bunu tutmak."*

* taban: **yok**
* tavan: emsal tam sürelinin **2/3'ü** = 45'in 2/3'ü = **30 saat**
* haftayı şekillendiren: `UYGUNLUK_TAKVIMI` — zaten SERT ve **iki tarafta da
  yazılı** (çözücü + doğrulayıcı), doğrulandı

### Doğrulayıcı gövdesi yazıldı

`SAAT_DENGESI`'nin çözücüde gövdesi vardı, **doğrulayıcıda yoktu** — yani
§7.6'nın koruması bu kuralda hiç çalışmıyordu. Bedeli ölçülmüştü: 45 saat
sözleşmeli 17 kişiden 45'i tutturan **sıfır**, ortalama 38,2 saat, plan yine de
*"0 sert ihlal, yayınlanabilir: True"*. Borç hesabı iki tarafta **ayrı ayrı**
yazıldı (§7.6: ortak modül yasak) — biri dakika, diğeri saat cinsinden.

### Ölçüm

7 yeni test; üçü kırmızı başladı. Üç mutasyon denendi (izin düşümü çözücüde,
izin düşümü doğrulayıcıda, yarı zamanlı tavanı) — üçü de öldü.

⚠ **Bir eski test tersine çevrildi:** `test_part_time_sozlesme_saati_toleranssiz`
20 saatlik bir yarı zamanlıya 24 saat verilmesini ihlal sayarak **eski
davranışı çiviliyordu**. Silinmedi, terse çevrildi ve neden değiştiği içine
yazıldı. Yanına, tavanın hâlâ bağladığını gösteren ikinci bir test kondu.

⚠ **İki altın senaryo kırmızıya düştü (T-53)** — A1 ve A9. Fikstürlere
dokunulmadı: onaylanmış cümleyi değiştirmek Mustafa'nın kararı.

→ K-30 · K-38 · T-51 · T-53 · `09-motor/cozucu/model.py` (`_saat_dengesi`,
  `_borc_dakika`) · `09-motor/dogrulayici/kurallar.py` (`saat_dengesi`,
  `part_time_limit`) · `09-motor/testler/test_sozlesme_saati.py`

---

## K-40 · *"Bu kişi gece vardiyası yapamaz"* — tahmin değil **işaret**

**Karar (29 Eylül, Mustafa).**

> *"Kullanıcı kartında gece vardiyası yapamaz gibi bir ifadeye ihtiyacımız var.
> Vardiya planı yapılırken de vardiya gece vardiyasıdır diye bir işaret koymamız
> gerekiyor. Bunu kullanıcı işaretleyecek."*

**İki yeni alan** (girdi sözleşmesi §8.3 / §11.2):

| nerede | alan | anlamı |
|---|---|---|
| vardiya şablonu | `gece_vardiyasi` | bu şablon gece vardiyasıdır — **kullanıcı işaretler** |
| çalışan | `gece_calisamaz` | bu kişi gece vardiyasına atanamaz |

**Yeni kural `GECE_UYGUNLUGU`, SERT.** Katalog **39 → 40**.

**Ne vardı.** Motor geceyi **saat aralığından tahmin ediyordu** ve bunu yalnız
`ADALET_DENGESI`'nin "gece" boyutunda, yani **adil dağıtım** için kullanıyordu.
*"Gece çalışamaz"* diye bir kayıt hiçbir yerde yoktu; ancak her gece için ayrı
bir `uygunluk` aralığı yazılarak taklit edilebilirdi — zahmetli ve
unutulduğunda **sessiz**.

**⚠ İşaret tahmini ezer.** 23:00-07:00 çoğu zaman doğru çalışır ama 22:00-06:00
ya da 00:00-08:00 gibi sınır durumlarında firmanın kendi tanımıyla çelişebilir.
Mustafa'nın istediği işaret: kullanıcı söyler, motor tahmin etmez.

**⚠ İşaret yoksa tahmine düşülür — ama sessiz değil.** Geçişi olmayan depolar
kırılmasın diye `gece_vardiyasi` yazılmamış bir şablon saat aralığına göre
değerlendirilir ve **not yazılır**. İşaretlenmemiş bir gece vardiyası,
korunması gereken birini sessizce geceye koyabilirdi.

`ADALET_DENGESI`'nin "gece" boyutu da artık aynı tespiti kullanıyor — iki yerde
iki farklı gece tanımı kalmadı.

### Ölçüm

8 test; dördü kırmızı başladı. Üç mutasyon denendi.

⚠ **Mutasyon bir boşluk yakaladı — ikinci kez.** *"İşaret tahmini ezer"*
testi sonunda `assert True` ile bitiyordu; işaret tamamen yok sayılıp hep
tahmine düşüldüğünde bütün testler yeşil kaldı. Test yeniden yazıldı: sahne
artık öyle kuruldu ki cevap tek — gece penceresindeki şablon *"gece değil"*
işaretli ve o saati kapatabilecek tek kişi gece çalışamayan. Doğrulayıcı için
de aynısı eklendi. Mutasyon artık ölüyor.

→ T-55 · `09-motor/cozucu/model.py` (`_gece_sablonu`, `_gece_uygunlugu`) ·
  `09-motor/dogrulayici/kurallar.py` (`gece_uygunlugu`) ·
  `09-motor/testler/test_gece_uygunlugu.py`

### ⚠ Tahmin değişti — 30 Eylül akşamı (T-69, T-71)

**İşaret hâlâ tahmini ezer; değişen yalnız işaret yokken yapılan tahmin.**

Eski tahmin: *aynı günün 20:00–06:00 penceresine en ufak değme.* İki yönde
yanlıştı — 00:00–08:45 **gece değil**, 13:00–21:00 **gece** sayılıyordu. Gece
çalışamayan birine 13:00–21:00 verilemiyordu; PDKS'ten gelen (işaretsiz)
00:00–08:00 kaydı ardışık geceye sayılmıyordu.

Yeni tahmin **yönetmeliğin kendi tanımı** (Postalar Yön. md. 7/2): süresinin
**yarısından çoğu** 20:00–06:00'da olan vardiya gece. Tam yarısı gece değil
(16:00–24:00).

**Yarım kalan cümle de tamamlandı (T-71):** yukarıdaki *"`ADALET_DENGESI`'nin
'gece' boyutu da artık aynı tespiti kullanıyor"* cümlesi yalnız çözücü için
doğruydu; doğrulayıcı işareti hiç okumuyordu. Artık iki tarafta da aynı.

**Veri setinde etkisi yok** — bütün şablonlar işaretli. Dört eski test sahnesi
işaretsiz şablonlarla kurulmuştu ve zorluğu adaletin gece teriminden geliyordu;
o sahnelere eski tahminin sonucu **açıkça işaret olarak** yazıldı, model aynı
kaldı. Bir eski test (gece penceresinin sınırı) yeni tanıma göre aynı sınırı
sınayan bir vakaya taşındı.

→ `09-motor/testler/test_gece_tespiti.py`

---

## K-41 · Nitelik kapsamasında mola **sahadan çıkarmaz**

**Karar:** 30 Eylül 2026, Mustafa.

`ROL_KAPSAMASI` ve `YETKINLIK_KAPSAMASI` *"o saatte o nitelik **vardiyada** mı"*
diye sorar. Molada olan kişi de sayılır.

> *"Sahada bir müdürün işi 15 dk mola süresini bekleyebilir. Bu 'sahada olmalı'
>  kuralını bozmaz. Molalar sahada sayılır olarak geçebilir. Zaten mola öneri
>  gibi bir kurgu olacağından bu kadar derine inmemize gerek yok."*

### Nasıl çıktı

Doğrulayıcı gövdeleri şartnameden okunarak yazıldı ve şartname §6.4 iki kuralda
da *"sahada"* diyor — gövde molayı düştü. Ölçülünce çözücünün **atanmış** kişiyi
saydığı görüldü: iki taraf aynı kelimeye farklı anlam veriyordu (T-61).

**Ölçülen:** 3 kişilik sahnede çözücü planı üretti, üçünün yemeği de aynı saate
düştü (11:00–12:00), o saatte sahada takım lideri kalmadı. Denetçi dört çeyrekte
ihlal yazdı. Çözücü kendi ölçüsüne göre kuralı sağlıyordu.

**Karar sorulduğunda değişen taraf doğrulayıcı oldu — çözücü haklıydı.** T-57'de
tersi olmuştu (doğrulayıcı haklıydı, çözücü düzeltildi); hangisinin değişeceği
şartnamenin harfine değil **işin nasıl yürüdüğüne** bakılarak belirleniyor.

### Ayrım bilerek bırakıldı

| kural | molada olan |
|---|---|
| `SAHADA_ASGARI` (K-33) | **sayılmaz** — *"firma sahada en az 5 diyecek"* |
| `ROL_KAPSAMASI` · `YETKINLIK_KAPSAMASI` (K-41) | **sayılır** |

Bu çelişki değil, iki farklı soru: saha tabanı *"tezgâhta kaç kişi var"*dır
(müşteri görür), nitelik kapsaması *"o nitelik o saat içinde ulaşılabilir mi"*dir.

### ⚠ Açık kalan

Yasal bayraklı bir gereklilik satırında (*"her vardiyada 1 ilk yardım
sertifikalı kişi"*) molanın sayılması hukuken tartışılabilir. Mustafa bugün daha
derine inilmemesini istedi. Gerekirse gereklilik satırına kendi seçeneği
eklenir — karar föyünde konuşulan üçüncü seçenek buydu.

### Ölçüm

İki test **tersine çevrildi** (silinmedi): mola testi ve uçtan uca ayrışma
ölçümü. Gerekçeleri testlerin başına yazıldı — K-33'te aynısı yapılmıştı.
Şartname §6.4'ün iki satırı bu kararla güncellenmeli.

→ T-61 · T-57 · K-33 · `09-motor/dogrulayici/kurallar.py` ·
  `09-motor/testler/test_nitelik_kapsamasi.py`

---

## K-42 · Geçmiş veri yoksa motor **durmaz**; geçmişe dayanan ölçütler atlanır

**Karar:** 30 Eylül 2026, Mustafa.

> *"Geçmiş veri yoksa adalet kavramı gibi geçmiş veriye dayanan kriterleri
>  dikkate almadan ilerlemek."*

Aynı gün verilen ürün cümlesi: *"Realitede geçmiş datayı PDKS v.b.
sistemlerden alacağız, plan datası olmayacak."*

### Neden soruldu

Şartname §11.2 *"Lookback verisi eksikse motor çalışmaz"* diyordu. Gerçek veri
(`07-GERCEK-VERI-BULGULARI.md` P-1) bunun uygulanamayacağını gösteriyor:
giriş/çıkış kaydı satırların yalnız **%18'inde** var, 781 çalışanın **411'inde**
hiç kayıt yok. Kural uygulansaydı motor gerçek koşumların çoğunda dururdu.

### Ne değişiyor

| önce (şartname) | şimdi (K-42) |
|---|---|
| geçmiş eksikse motor çalışmaz | motor çalışır |
| — | geçmişe dayanan ölçüt, geçmişi olmayan kişi için **atlanır** |

**⚠ Atlanan ölçüt sessiz geçmez** — projenin her atlamasındaki ilke
(`uygulanmayan_kurallar`, `eksik_boyutlar`, `okunmayan_alanlar`). Hangi ölçütün
kimin için atlandığı çıktıda yazılır. Bu, kararın uygulanış biçimidir; kararın
kendisini değiştirmez.

### ⚠ Açık kalan — yasal kurallar

Geçmişe dayanan ölçütlerin üçü **yasal**:

| kural | geçmiş neden gerekiyor |
|---|---|
| vardiya arası dinlenme (11 saat) | pazartesi sabahı, pazar gecesinin bitişini bilmeden denetlenemez |
| hafta tatili (kayan 7 gün) | pencere geçen haftaya uzanıyor |
| gece postası devri | *"geçen hafta gece çalıştı mı"* |

Mustafa'nın örneği (*adalet*) yumuşak bir kural. Yasal kurallar da aynı
şekilde atlanırsa, kaydı olmayan bir kişi pazar 23:00'e kadar çalışmış olabilir
ve pazartesi 07:00'ye yazılabilir.

**✅ Karar (aynı gün, Mustafa): yasal kurallar da atlanır ve raporlanır.**

Üç seçenek soruldu: yayındaki planı varsayım olarak kullanmak, atlayıp
raporlamak, geçmişi bilinmeyen kişinin pazartesi sabahını kapatmak. Seçilen
ikincisi. Sonucu açıkça:

* Motor bu durumda o kişi için hafta sınırında **yasal garanti vermez**.
* Çıktı bunu **kişi ve kural adıyla** söyler (*"C0123 için pazartesi dinlenme
  kontrolü yapılamadı — geçmiş kayıt yok"*); yönetici görür.
* Sorumluluk gerçekleşen verinin yüklenmesinde — `07-GERCEK-VERI-BULGULARI.md`
  kapsam kararı: *"Gerçekleşen veri ve izinlerin doğru formatta yüklenmesi
  müşterinin sorumluluğu."*

⚠ **Yayın kapısıyla ilişkisi açık (T-18):** bu rapor da bugünkü üç sessizlik
kanalı gibi yalnız rapor olacak; kapının ona ne yapacağı T-18'in kararı.

→ T-28 · §11.2 · `07-GERCEK-VERI-BULGULARI.md` P-1

### ✅ Uygulandı — 30 Eylül

**Rapor kanalı:** `gecmis_eksik` — doğrulayıcı çıktısında, diğer üç sessizlik
kanalının yanında. Her satır: kural, çalışan, eksik gün, cümle
(*"C0123 için pazartesi dinlenme kontrolü yapılamadı — gün -1 için geçmiş
kayıt yok (K-42: atlandı)"*). Yalnız rapor; ihlal değil, yayın kapısına girmez.

**⚠ Gürültü değil, kesin satır.** Gerçek veride kişilerin çoğunun pazarı
bilinmiyor; her pazartesi çalışanı için dört satır yazan bir kanal okunmaz
olurdu. Satır yalnız **sonucu değiştirebilecek** bilinmeyen gün için yazılır:

| durum | satır |
|---|---|
| pazartesi boş | yok — sınır kuralları etkilenemez |
| geriye yürürken **bilinen boş** gün | yok — seri orada kırılır |
| geçmişle birlikte ihlal **kanıtlı** | yok — ihlal kanalı söyler, iki kez yazılmaz |
| ilk **bilinmeyen** gün, seri hâlâ eşiğe yetişebilecekken | **var** |

**Yeni isteğe bağlı alan:** `gecmis_bilinen_gunler` — kaydı tam olan günler.
Bilinen ama kaydı olmayan gün **çalışılmamış** sayılır. Alan gelmezse yalnız
kaydı olan gün bilinir.

**Geçmiş tam verildiğinde kanal boş** — iki aşamalı ölçümde de öyle çıktı.

→ T-28 · `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_gecmis_veri.py`

---

## K-43 · Gece işareti **yönetmelikten otomatik gelir ve tabandır**; firma yalnız ekler

**Karar (30 Eylül 2026 gecesi, Mustafa).**

> *"Vardiya için seçilen saat sonrası sistem otomatik işaretlesin. Bunu bir
> işaretle tutarsak, çalışan sözleşmesinde gece çalışamaz işaretini de
> eklersek sanki daha rahat arka planda yakalarız."*

K-40 *"kullanıcı işaretler, motor tahmin etmez"* demişti. Yeni karar onu
değiştiriyor:

| | K-40 (29 Eylül) | K-43 (30 Eylül) |
|---|---|---|
| işaret nereden gelir | kullanıcı koyar | **yönetmelik tanımından otomatik** (Postalar Yön. md. 7/2: süresinin yarısından çoğu 20:00–06:00'da) |
| işaret yoksa | saat aralığından **tahmin**, not yazılır | otomatik belirlenir, not yazılır |
| firma "gece" derse | gece | gece (**ekler**) |
| firma "gece değil" derse | gece değil (işaret tahmini ezer) | yasal olarak geceyse **yine gece** (altına inemez), not yazılır |

**Neden altına inemez:** *"22:00–06:00 gece değil"* diyen bir firma, gece
çalışamayan birini o vardiyaya yazabilirdi — koruma tek işaretle delinirdi.
**Neden üstüne ekleyebilir:** daha sıkı olmak her zaman serbest (K-18'in
diğer yüzü); *"15:15–24:00 bizde gece sayılır"* meşru bir firma tercihi.

**Yasal kurallar işareti hiç kullanmaz** (K-44, K-45): işaret yasal kuralı
iki yönde de bozardı — kaçırır ya da yasal planı kilitler.

**Uygulandı:** iki motor yarısında da. Üç eski test tersine döndü (K-40'ın
*"işaret tahmini ezer"* bekçileri) ve gerekçesi testin içinde yazılı.
Veri setinde etkisi yok — hiçbir şablon yasal geceyi inkâr etmiyor.

→ K-40 · `09-motor/testler/test_gece_uygunlugu.py` · `test_gece_tespiti.py`

---

## K-44 · Yasal gece sınırı **gece postasının bütün süresine** uygulanır

**Karar (30 Eylül 2026 gecesi).** Mustafa: *"Hukuk teyidini alabileceğimiz bir
hukukçu yok, online kaynaklardan elde ederek karar vermeliyiz. Sana
bırakıyorum."* Araştırıldı, karar verildi.

**Yönetmelik (Postalar Yön. md. 7):** *"...işçilerin gece postalarında 7,5
saatten çok çalıştırılmaları yasaktır."* ve md. 7/2: *"Çalışma süresinin
yarısından çoğu gece dönemine rastlayan bir postanın çalışması, gece
çalışması sayılır."*

**Yargıtay (9. HD, 2016/36126 E., 2020/17967 K.):** 20:00–08:00 vardiyasında
gece hesabı 06:00'da kesilmez, fiili bitiş 08:00'e kadar yapılır —
*"çalışmanın yarısından fazlası gece dönemine denk gelince tüm çalışma gece
kurallarına tabi"*. Doktrin aynı: bu okuma **postalar hâlinde** (vardiyalı)
işyerleri içindir; vardiyasız işyerinde yalnız 20:00 sonrası sayılır. Biz
vardiya ürünüyüz.

**Kural artık iki ölçü birden:**

| ölçü | ne |
|---|---|
| **gece postası** (yeni) | vardiyanın yarısından çoğu 20:00–06:00'daysa **bütün net çalışma** ≤ 7,5 |
| pencere (eski) | 20:00–06:00'a düşen net çalışma ≤ 7,5 — tek başına asla ateş almaz ama ayrıca aynı geceyi paylaşan **iki** vardiyayı toplar |

Aynı vardiya iki kez yazılmaz. Sektör istisnası (K-26) ikisinde de geçerli.

| vardiya | eski | yeni |
|---|---|---|
| 22:00–08:00, 1 sa mola | 7 sa → yasal | 9 sa → **yasa dışı** |
| 16:00–01:00, 1 sa mola (gerçek müşteri, 82 kez) | 5 sa → yasal | 8 sa → **yasa dışı** (yazılı onay yoksa) |
| 16:00–01:00, 1,5 sa mola | yasal | 7,5 → yasal |

Eski ölçü hiçbir durumda yönetmelikten sıkı değildi; fark hep *"yasa dışıya
yasal deme"* yönündeydi (T-74).

**Uygulandı:** iki yarıda; çözücü net süreyi şablondan kesin hesaplar, bu
ölçüde doğrulayıcıyla aynı (brüt pencere ölçüsü T-68 olarak kalıyor).
Veri setinde etkisi yok — bütün gece şablonları tam 7,5 saat net.

→ T-74 · K-26 · şartname §6.3 (yazı borcu) ·
`02-spec/v1.4-hazirlik/02-mevzuat-arastirmasi.md` bölüm 3b

---

## K-45 · "Gece haftası" = haftanın çalışma saatlerinin **yarısından çoğu** gece postasında; üst sınır 2, anlamı "iki hafta gece, iki hafta gündüz"

**Karar (30 Eylül 2026 gecesi).** Mustafa: *"Online araştırıp karar
vereceğiz. Sana bırakıyorum."* Parametrenin üst sınırı ve anlamı için:
*"Sana katılıyorum."*

**Kanun ve yönetmelik:** İş K. md. 69 ve Postalar Yön. md. 8 — *"bir
çalışma haftası gece çalıştırılan işçilerin, ondan sonra gelen ikinci
çalışma haftası gündüz çalıştırılmaları suretiyle postalar sıraya konur.
Gece ve gündüz postalarında iki haftalık nöbetleşme esası da
uygulanabilir."*

**Araştırma:** hiçbir kaynak *"haftanın bir kısmı gece"* durumunu
tanımlamıyor. Kaynakların hepsi kuralın amacını aynı cümleyle veriyor —
**sürekli gece çalıştırma yasağı** (Yargıtay 22. HD 2017/24339 E.,
2019/18396 K.: bir ay aralıksız gece vardiyası ihlal; işçi haklı fesih
hakkı kazandı). Kural posta düzenini varsayıyor: kişi o hafta gece
postasındadır ya da gündüz.

**Karar:** kişi bazlı karma haftaya en tutarlı çeviri, yönetmeliğin **tek
vardiya** için kullandığı ölçüyü **haftaya** uygulamak — haftanın çalışma
saatlerinin yarısından çoğu gece postasındaysa o hafta gece haftasıdır.
Tam yarısı değildir. Ölçü brüt saat (PDKS kaydında mola yok).

**Sıkı okuma seçenek olarak kaldı:** `gece_haftasi_asgari_gece` (yasal
işaretli): *"haftada N gece de haftayı gece haftası yapar"* — yalnız
**ekler**, gevşetemez (K-18).

**Parametre:** `azami_ardisik_gece_haftasi` — art arda 2×azami haftalık
her pencerede en fazla azami gece haftası. 1: gece-gündüz-gece-gündüz.
2: gece-gece-gündüz-gündüz; **gece-gece-gündüz-gece yasak** (dörtte üç).
**Üst sınır 2** — 3 verilirse 2 uygulanır ve `eksik_boyutlar`da bildirilir
(çözücü not yazar).

**Geçmişte yalnız tam bilinen hafta değerlendirilir** (K-42): çoğunluk
yarım bilgiyle hesaplanamaz; bir günü bilinmeyen hafta kısıt yaratmaz,
raporlanır. Gerçek PDKS'te (kayıtların %57'si) bu, kuralın çoğunlukla
*"raporladı"* demesi anlamına gelir — dürüst durum; PDKS'teki *"çalışma günü
değil"* satırlarının bilinen boş gün sayılması (entegrasyon kararı, açık)
bunu büyük ölçüde çözer.

**Ölçüldü** (49 kişi, %95 doluluk, üç hafta): çözücü geceleri adaletle
dağıttığı için birinci haftada gece haftası yaşayan **1 kişi** çıktı (sıkı
okumada 11'di); ikinci ve üçüncü hafta geçmişle çözüldü, gece postası devri
ihlali 0. Geçmişsiz çözülen üçüncü haftada 2 kişi üst üste gece haftası
yaşardı — okunan geçmiş bunu engelledi. Yani bu ölçekte kural, sürekli
gece çalıştırma **niyetini** yakalar, adil dağıtılmış planı zorlamaz.

**Gerçek müşteri notu:** 16:00–01:00 deseni yönetmeliğe göre gece
postasıdır (9 saatin 5'i gecede). O vardiyada çoğunlukla çalışan ekip her
hafta gündüz ekibiyle yer değiştirmek zorunda; **sektör istisnası bu kuralı
kapsamıyor** (istisna yalnız 7,5 saat sınırı için).

→ T-72 · T-73 · K-25 · `09-motor/testler/test_hafta_kurallari.py`

---

## K-46 · "Hafta sonu çalıştı" = **hem cumartesi hem pazar**; gün, saatlerinin **yarısından çoğu**nun düştüğü gündür

**Karar (30 Eylül 2026 gecesi, Mustafa).** İki parça:

**Tanım — "Katılıyorum":** *"hafta sonu çalıştı" = hem cumartesi hem pazar
çalıştı. 6 gün çalışan biri izin gününü cumartesi-pazar arasında dönüşümlü
alırsa hiç birikmez; kural yalnız iki günü de üst üste çalışanları yakalar.
Yöneticinin kastettiği: "üç hafta üst üste tam hafta sonu çalışmasın."*

Önceki tanım (bir gün yeter) hafta hafta planlamada **üçüncü haftayı
çözümsüz** bırakıyordu (T-75): 6 günlük desende herkes her hafta sonu
*"çalışmış"* sayılıyor, motor gelecek haftayı görmüyor, 45 kişinin 29'u
üçüncü haftada yasaklı kalıyordu.

**Gün — "Katılıyorum, ben de bunu dedim":** Mustafa'nın sorusu *"ne kadar
sarktığına bağlı olmaz mı, eşik mi vermeliyiz?"* — eşik yüzde elli, yani
yönetmeliğin gece için kullandığı ölçünün aynısı:

| vardiya | hangi gün |
|---|---|
| cuma 23:00–06:00 | 7 saatin 6'sı cumartesi → **cumartesi** |
| cuma 16:00–01:00 | 9 saatin 1'i cumartesi → cuma |
| pazar 23:00–06:00 | pazartesi |
| tam yarısı | başladığı gün |

**Yalnız hafta sonu kurallarında:** ardışık hafta sonu limiti ve adalet
dengesinin hafta sonu boyutu (iki tarafta). Motorun genel kuralı — vardiya
başladığı güne yazılır (Z-2) — ardışık gün, hafta tatili ve diğerlerinde
olduğu gibi kalır.

**Geçmişte yalnız kanıtlı (iki günü de kayıtlı) hafta sonu sayılır** (K-42).

→ T-75 · şartname §6.5 (yazı borcu) · `09-motor/testler/test_hafta_kurallari.py`

---

## K-47 · Geçmiş eksik raporuna **yönetici bakar**; kapı engellemez

**Karar (30 Eylül 2026 gecesi, Mustafa):** *"Yönetici baksın."*

Sahte PDKS ölçümünde (T-77) 49 kişilik plan için `gecmis_eksik` 141 satır
yazdı; 7 gerçek ihlalin hepsi haberliydi ama satır satır okunmaz.

**Uygulanan:** doğrulayıcı çıktısına `gecmis_eksik_ozet` eklendi — kişi
başına gruplanmış, **yasal** kontrolü yapılamayanlar önde, tepede sayılar
(satır · kişi · yasal kontrolü yapılamayan kişi). Yayın kapısı bunu
**engellemez** (K-42: atlanır, raporlanır).

**Arayüz/backend işi (yazılmadı):** yayından önce özet gösterilir, yönetici
*"gördüm"* der. **Veri işi (açık):** PDKS dosyasında her çalışan×gün satırı
var ve planlanan süre `00:00` ise o gün çalışma günü değil — bu satır
*"bilinen boş gün"* sayılırsa bilinmeyen gün sayısı ciddi düşer. PDKS'in o
alanı gerçekten böyle kullanıp kullanmadığı doğrulanmalı.

🆕 **1 Ekim 18:00 — doğrulandı, cevap HAYIR** (`07-GERCEK-VERI-BULGULARI.md`
§7): PDKS'in `00:00`'ı plan değil, takvim — hafta sonu satırı kişi kart
okutunca **sonradan** `07:30`'a dönüyor (günden önce `00:00` olup sonra
`07:30` olan 1.084 satırın hepsinde kart var; `00:00` kalan 6.014'ün hiçbirinde
yok). Gelecek günler için hiçbir şey söylemiyor, geçmiş için *"kart yok"*un
tekrarı. **Karar → K-55 (aynı akşam):** bilinen boş günün kaynağı TShift'in
kendi yayınladığı önceki planlar + PDKS izin satırları; PDKS'ten yalnız ham
giriş-çıkış (gece vardiyası başladığı günde tek satır — motorla aynı,
düzeltme yok); yıl içi fazla mesai toplamı PDKS ham verisinden TShift'in
kendi hesabıyla (PDKS'in `FM` kolonu okunmaz; bordro değil — Mustafa).

→ T-77 · T-18 · K-42 · `09-motor/testler/test_rapor_ozeti_ve_teshis.py`


## K-48 · Süre bütçesi **arama süresidir**; model kurma **ayrı kalem** olarak gösterilir — 1 Ekim 16:00: itiraz gelmedi, kesinleşti

**Soru (1 Ekim gecesi):** üç tam ölçekli koşu *"en fazla 900 sn"* deyip
958 sn sürdü — birinci aşama + ana aşama = tam 900, model kurma (~55–78 sn)
bütçenin dışında.

**Mustafa (1 Ekim 13:05):** *"Zaman en önemli kaynağımız… 'Ekranda modelleme
58, plan 900 sn' gibi belirtsek zamandan da kazanmış olmaz mıyız? Yahut
900'e sığdıralım, kayıp var mı yok mu testlerde anlar öyle ilerleyebiliriz."*

**Seçilen (benim seçimim, Mustafa'nın ilk önerisi):** `azami_saniye` =
**arama** bütçesi (birinci aşama + ana aşama); model kurma bütçeden
düşülmez, ekranda **ayrı satır** olarak gösterilir (*"modelleme 58 sn ·
arama 900 sn"*). Gerekçe: zamanı yetmeyen taraf arama; tam ölçekte birinci
aşama 120 saniyede plan bulamıyor, 1 Ekim'de ana aşama 778 saniyede de
bulamadı. 55 saniyeyi aramadan kesmek plan bulma şansını düşürür. İkinci
seçenek (kurma da içeride) T-60 kapandıktan sonra yeniden açılabilir.

**Uygulama:** kod zaten böyle (T-59); `coz-olc.py` ve çıktı (`model_kurma_sn`)
iki kalemi ayrı yazıyor. Arayüz işi: iki sayı ayrı gösterilir, *"toplam
bekleme"* ikisinin toplamıdır. ⚠ `coz-olc.py` ölçüm betiği modeli bir kez
daha kuruyor (sayım için) — betiğin fazlası, ürünün değil.

→ T-59 · T-60 · K-35


## K-49 · Denetlenemeyen kural yayın kapısından geçemez — üç kademe

**Soru (T-18, 16 Eylül dış incelemesi):** doğrulayıcıda gövdesi yazılmamış
ama aktif bir kural varken cevap aynı anda *"bu kuralı kontrol edemedim"* ve
*"yayınlayabilirsin"* diyordu. Kapı yalnız bulunan ihlallere bakıyordu;
*"bakamadım"* kapıyı geçiyordu.

**Karar (1 Ekim 2026, Mustafa: "onaylıyorum"):** kontrol edilemeyen bir
kuralın kapıdaki etkisi kuralın türüne göre üç kademedir:

1. Kural **sert ve yasal** ise (örneğin gece sınırı): plan **yayınlanamaz**.
   Firma, kanunun kontrolünü "kabul ediyorum" diyerek geçemez — K-18 ve K-20
   ile aynı ilke.
2. Kural **sert ama firmanın kendi kuralı** ise (örneğin "her saat bir takım
   lideri"): plan **kabul bekler**. Yetkili bir gerekçe yazarak kabul eder;
   kabul edilene kadar yayınlanamaz. Gerekçesiz kabul, kabul sayılmaz.
3. Kural **yumuşak** ise: yalnız **raporlanır**, yayın etkilenmez.

**Hangi durumlar "bakamadım" sayılır:** (a) gövdesi hiç yazılmamış aktif
kural (`uygulanmayan_kurallar`); (b) yazılmış bir kuralın bakılamayan parçası
(`eksik_boyutlar` içinde `denetlenemedi: true` olanlar — örneğin gereklilik
satırı olmayan yetkinlik kapsaması, adalet dengesinin yazılmamış `saat`
boyutu). Bir kuralın yasal sınıra **kırpılması** (örneğin nöbetleşme 3
verildi, 2 uygulandı — K-45) kural **denetlendiği** için kapıyı etkilemez.

**Kabul kaydı nasıl gelir:** girdide `denetim_disi_kabul` listesi —
`{"kod": ..., "gerekce": ..., "onaylayan": ...}`. Bu plan başına bir kabuldür
(kural tanımına yazılmaz). Yasal kural için kabul kaydı gelse de kapı açılmaz.

**Görünen sonuç:** çıktıdaki `yayin_kapisi.denetlenemeyen_kurallar` her
satırda kuralı, türünü, etkisini (*engelliyor · kabul bekliyor · kabul
edildi · rapor*) ve okunur bir cümleyi taşır. Arayüz kabul düğmesini bu
satırlara göre gösterir.

**Veri setine etkisi:** 500 kişilik ölçüm setinde `YETKINLIK_KAPSAMASI`
aktif, sert ama parametresiz (T-63'ün açık yarısı). Bu kararla tam ölçek
planı *"kabul bekliyor"*a düşer. Ölçüm setine **gerekçeli kabul kaydı**
kondu ("yetkinlik gerekliliği henüz tanımlanmadı, T-63"); gereklilik
tanımlanınca kayıt kalkar.

→ T-18 · T-63 · K-18 · K-20 · `09-motor/dogrulayici/denetle.py` · `09-motor/testler/test_yayin_kapisi_denetlenemeyen.py`

## K-50 · Çok ekipli çalışan, üye olduğu **bütün ekiplere** sayılır — talep "adanmış beden" değil "hazır bulunan kişi"dir

**Soru (T-21, 16 Eylül dış incelemesi):** iki ekibe üye bir çalışan tek
vardiyayla iki ekibin kapsamasına birden giriyordu; kayıt bunu *"modelin
inancı yanlış — bir kişi aynı anda iki yerde olamaz"* diye açmıştı.
Doğrulayıcı ise atamayı yalnız bir ekibe sayıyordu: aynı plan için çözücü
*"%100"*, doğrulayıcı *"%50"* diyordu.

**Mustafa (1 Ekim 2026):** *"Sahada hem satış hem backoffice yapabilen
elemanlar var. Bu elemanlar iki yetkinlik grubuna da ait sayılır: o saatte
o eleman iki birim elemanı için yer doldurmuş sayılır. Gece 12'den sonra
backoffice talepleri yok denecek kadar azalıyor; buraya bir eleman koymak
yerine asıl işi satış ama backoffice yeteneği olan bir eleman konuyor ve
sorun sahada çözülmüş oluyor. Zaten firmalar da eleman açığını böyle
yapıyor."*

**Karar:** modelin inancı doğruymuş; **değişen taraf doğrulayıcı** oldu.
Talep tablosundaki sayı *"o saatte o yetenekte hazır bulunan kişi"*
demektir, *"o işe adanmış beden"* değil. Bir atama, çalışanın üye olduğu
bütün ekiplerin kapsamasına sayılır: hem kişi sayısı (asgari ve hedef
kapsama, mola sırasındaki kapsama, saha tabanı) hem nitelik (rol ve
yetkinlik kapsaması) için. Çıktıdaki atamanın `ekip` alanı **vardiyanın
ekibidir** (şablonun ekibi; şablon ekipsizse kişinin ilk ekibi) — hangi
vardiyada olduğunu söyler, sayımı sınırlamaz.

**Görünürlük:** başka ekibin vardiyasındaki kişiyle kapatılan hücreler
sessiz kalmaz: `metrikler.baska_ekipten_kapsama` kaç hücrenin ve kaç
kişi-saatin böyle kapandığını söyler. Yönetici gündüz yoğunluğunda bu sayı
büyüyorsa görür.

**Kiracı seçimi:** girdide `cok_ekipli_sayim: "tek"` denirse atama yalnız
vardiyanın ekibine sayılır (ekipsiz şablonda kişinin ilk ekibine; bu durum
nota yazılır). Varsayılan `"hepsi"`. İki motor yarısı aynı alanı aynı
varsayılanla okur.

**Veri setine etkisi:** 500 kişilik sette herkes tek ekipte; davranış
değişmedi, alan açıkça `"hepsi"` yazıldı.

→ T-21 · K-41 · `09-motor/cozucu/model.py` (`_sayilir`) · `09-motor/dogrulayici/kurallar.py` (`ekibe_sayilir`) · `09-motor/testler/test_cok_ekipli.py`


## K-51 · Çözücünün kendi "sert ihlal" sayısı çıktıdan kaldırıldı

**Soru (T-66):** çözücü çıktısındaki `metrikler.sert_ihlal` hep sıfır
yazıyordu; ölçülmüyordu. Ekranda "0 sert ihlal" görünce insan sayılmış
sanıyordu.

**Karar (1 Ekim 2026, Mustafa):** *"Kaldıralım; ihlaller değişken değil
sonuçta, birinin saptaması bizim için yeterlidir."* Alan çözücü çıktısından
kaldırıldı. Tek doğru sayı bağımsız doğrulayıcınınki (`/evaluate` →
`metrikler.sert_ihlal` ve `yayin_kapisi`). Çözücünün kendi işini kendi
onaylaması zaten yasaktı (§7.6). Şartname §11.3 çıktı örneğinden de alan
çıkarıldı.

→ T-66 · `09-motor/cozucu/coz.py` · `09-motor/testler/test_motor_metrigi.py`

## K-52 · Departman tanımı ve çalışma saatleri; her birim için yetkinlik gerekliliği

**Mustafa (1 Ekim 2026):** *"Sistemde departman tanımı lazım ve ilgili
departmana çalışma günleri ile saatlerini tanımlamalıyız."* ve *"her birim
için tanımlamalıyız bu İngilizce kuralını — veri setinde olabildiğince
kompleks kurgu istediğimi unutma."*

**Çalışma saatleri (CALISMA_SAATLERI, gövdesi yazıldı):** girdiye
`departmanlar` listesi geldi: her departmanın ekipleri ve açık saatleri —
ya `"7/24"` ya da gün gün pencereler (`{"gunler": [0..4], "bas": 7,
"bit": 23}`; `bit` 24'ü aşabilir, gece yarısını aşan pencere için). Bir
vardiya **başladığı günün bir penceresine tamamen sığıyorsa** açıktır.
Çözücü kapalı saate taşan şablon-gün çiftlerine atama yazmaz ve her
çift için not düşer; ön kontrol kapalı şablonu "ulaşıyor" saymaz;
doğrulayıcı kapalı saate taşan atamaya ihlal yazar (sert, firma kuralı,
kabul edilebilir). Ekibin departman saatleri **tanımsızsa** kural o ekip
için kontrol edilemez: çözücü kısıt yazmaz ve not düşer, doğrulayıcı
"denetlenemedi" der, yayın kapısı kabul bekler (K-49).

**Veri setinde:** satış ve back office 7/24; müşteri hizmetleri hafta içi
07:00–23:00, hafta sonu 08:00–19:00 — hafta sonu akşam şablonları kapalı
saate taştığı için kural gerçekten kısıyor.

**Yetkinlik gereklilikleri (T-63 kapandı):** her satır ayrı kural (K-24,
satır bazlı bayrak): satışta 08–20 arası en az 2 İngilizce bilen; back
office'te 08–18 en az 1 İngilizce; müşteri hizmetlerinde 08–22 en az 1
İngilizce **ve** 10–16 en az 1 Almanca. Üretici, lider tabanıyla aynı
hesapla her ekipte yeterli sayıda tam zamanlı, izinsiz taşıyıcı olmasını
sağlıyor (8 / 3 / 4 / 3). Veri setindeki iki kabul kaydı (yetkinlik ve
çalışma saatleri) kalktı.

→ T-63 · T-38 · `09-motor/cozucu/model.py` (`_kapali_saatleri_kapat`) · `09-motor/dogrulayici/kurallar.py` (`calisma_saatleri`) · `09-motor/testler/test_calisma_saatleri.py` · `08-motor-testleri/gercekci-veri-seti/uret_veri_seti.py`

## K-53 · Hedefi aşan saate yumuşak ceza (`HEDEF_ASIMI`) — ücret terimi yok

**Soru (T-54):** modelde bir saatin bedeli yoktu; 1 kişilik talep için 4
yarı zamanlı 45'er saate dolduruluyor, 350 kişilik sahnede hedefin 2 katı
kişi sahaya konuyordu.

**Karar (1 Ekim 2026, Mustafa):** *"Ceza ile ilerleyelim. Ücret tarafı hiç
gelmeyebilir."* Katalogda yeni yumuşak kural **`HEDEF_ASIMI`** (katalog
41): bir talep hücresine hedeften fazla kişi atanmışsa fazla kişi başına
ceza. Ağırlık profilden: dengeli 3, kapsama 1, çalışan 4 — hedefin
**altında** kalmak (`HEDEF_KAPSAMA`: 9 / 20 / 5) her profilde aşmaktan
pahalı; eksik kişi müşteri kaybıdır, fazla kişi paradır. Sert tabanları
ezmez: 45 saatlik tam zamanlı yine 45'e dolar, ceza fazlalığı en az
hücreye yayar. Doğrulayıcı aynı hücreleri yumuşak ihlal olarak sayar.

→ T-54 · `09-motor/cozucu/model.py` (`AGIRLIK_TABLOSU`, `_kapsama`) · `09-motor/dogrulayici/kurallar.py` (`hedef_asimi`) · `09-motor/testler/test_hedef_asimi.py`


## K-54 · Dondurulmuş gün **olan oldu**dur: yayınlanmış plan motora gelir, geçmiş günler aynen kalır, gelecek ona uyar

**Soru (T-29, 16 Eylül dış incelemesi):** *"Geçmiş yeniden planlanamaz"*
sözünün tek bekçisi `DONMUS_GUN`, yalnız *"bu atama yeni"* işaretli
atamalarda çalışıyordu ve o işareti hiçbir şey üretmiyordu — kural ölüydü.
Çözücü donmuş günleri ayrıca korumuyordu. Önerim (1 Ekim öğleden sonra):
mevcut yayınlanmış plan motora girdi olarak gelsin, motor kendi ürettiğini
onunla karşılaştırsın.

**Karar (1 Ekim 2026, Mustafa):** *"Onaylıyorum ama bir ek ile: kilitleme
özelliğini hafta için aynı planı güncellerken kullanacaktık hatırlarsan.
Kapanan günlerdeki plan uyumu yöneticinin bilgisi dahilinde değişebileceği
için — yani başka bir elemanı o gün kendi inisiyatifiyle işe çağırabilir
misal — yönetici ilgili bir planı güncellerken geçmiş günler için düzenleme
yapabilir. Gelecek günler için istediği çalışanları kilitleyebilir. Hatta bu
kilitleme-silme konuları için ekranda çoklu aksiyon alabileceği seçenekler
olmalı; birden fazla kullanıcı seçerek silebilir veya kilitleyebilir. Sana
katıldığım kısım şu: yönetici edit işlemlerini bitirdikten sonra motora
ilgili verilerin gitmesi gerekiyor."*

**Uygulanan (1 Ekim akşamı, iki yarıda):**

*Girdi.* `mevcut_plan` — yayınlanmış planın satırları, çıktı biçimiyle
aynı, yöneticinin düzenlediği hâliyle (geçmiş günler için *"gerçekte ne
oldu"*). `donmus_gunler` zaten vardı.

*Çözücü.* Donmuş günün satırları çıktıya **aynen** aktarılır (molalarıyla,
`donmus: true` işaretiyle; çözücü üretmez, aktarır). O günlere **yeni atama
yazılmaz**. Donmuş atamalar modelde **sabittir** ve günler arası kurallar
onları gerçek sayar: pazartesi gece çalışmış kişi salı 11:00'den önce
başlayamaz; beş günde 35 saat dolduranın iki günü 10 saati geçemez; adalet
sayaçları geçmişi de sayar. Geçmişin **kendisi yargılanmaz**: bütün
değişkenleri donmuş güne ait kısıt düşer (o gün eksik kapsanmışsa, iki
vardiya yazılmışsa, izinli günde çalışılmışsa plan çözümsüz olmaz — 0,1
ölçekte gün 0 için 8.945 kısıt düştü). Geçmişle geleceği birlikte tutan
kısıt kalır; geçmiş sınırı zaten aşmışsa sınır ulaşılabilir en yakın noktaya
**kırpılır** (40 saatlik tavan 42 saatle dolmuşsa kalan günlere pay kalmaz,
plan yine çözülür). Yayınlanmış plan ayrıca başlangıç ipucudur (*"iyileştir,
zar atma"*, 28 Eylül). Donmuş günde kilit ve sabit atama uygulanmaz (not
düşülür). Hiçbir şablona oturmayan satır (yönetici 10:00–14:00 yazmış) aynen
geçer ama modele girmez — not düşülür, doğrulayıcı yine görür.

*Doğrulayıcı.* `DONMUS_GUN` donmuş günleri `mevcut_plan` ile karşılaştırır:
eklenen, silinen, değişen satır sert ve kabul edilemez ihlal — bayrak yok.
Yalnız donmuş günlere dayanan diğer ihlaller **`gecmis: true`** işaretlenir
(*"olan oldu"*): `ihlaller` listesinde kalır, `gecmis_ihlaller`de ayrıca
listelenir, **yayın kapısı ve `sert_ihlal` saymaz** — yönetici geçmişi
değiştiremez, geleceği yayınlayamaz çıkmazına girmesin diye. Ölçü: aynı
kural yalnız donmuş günlerin atamalarıyla da aynı ihlali üretiyor mu;
donmuş günle serbest gün arasındaki dinlenme ihlali bu yüzden geçmiş
sayılmaz (gelecek değişir). Donmuş gün var ama plan yoksa kural
*"denetlenemedi"* olur, kapı kabul bekler (K-49). Onarım döngüsü geçmiş
ihlali onarmaya kalkmaz.

*Veri seti.* Gerçekçi sahne artık **taze hafta** (`donmus_gunler: []`):
eskiden `[0]` yazıyordu ama kural ölü olduğu için sahneyi hiç etkilememişti;
canlanınca yayınlanmış plan isterdi. Çözücü için zorluk değişmedi, önceki
ölçümlerle karşılaştırılabilir. Donmuş gün yolu ayrıca ölçülür: bekçide
0,1 ölçekte yeniden planlama testi (gün 0 aynı, 0 sert, yayınlanabilir,
ipucu kullanıldı) ve `coz-olc.py --donmus` (tam ölçek, Mustafa koşturur).

*Arayüz / backend (yazılmadı):* yönetici geçmiş günleri düzenler, gelecek
günleri kilitler, **çoklu seçimle** kilitler ve siler; düzenleme bitince
motor `mevcut_plan` + `donmus_gunler` ile çağrılır.

**Günsüz ihlalde ölçü (tam ölçek koşusunun düzelttiği nokta, 1 Ekim 23:00):**
günsüz (haftalık) ihlallerden yalnız **tavan** türü kurallar geçmiş
sayılabilir — haftalık azami, fazla mesai tavanı, yarı zamanlı tavanı, yıllık
tavan: saat arttıkça kötüleşen kural, donmuş günler tek başına tavanı
aşmışsa gelecek düzeltemez. Eksiklik ve karşılaştırma kuralları (saat
dengesi "eksik", adalet dengesi) yalnız donmuş günlerle değerlendirilince
her zaman daha kötü görünür ve gelecek onları düzeltebilir; günsüzken asla
geçmiş sayılmaz. Mustafa'nın tam ölçek koşusunda 162 "geçmiş" ihlalin bir
kısmı adalet dengesiydi — yanlış etiket; aynı akşam düzeltildi, test ve
mutasyonla çivilendi. Donmuş gündeki sahada sayım, molalar motorun aday
noktalarına oturmadıysa yaklaşıktır (not düşer).

**Tam ölçekte ölçüldü (Mustafa, 1 Ekim 22:50, `coz-olc.py --saniye 900
--donmus`):** taze hafta 902 sn → 2.352 atama, 0 sert, yayınlanabilir; sonra
gün 0 dondurulup motorun kendi planıyla yeniden: model kurma 71 sn (54'e
karşı, süzgeç bedeli %31), **92.899 kısıt geçmişe düştü, 0 kırpıldı**,
305 sn'de çözüldü, ipucu kullanıldı, ilk plan 48,5 sn, **gün 0 aynı, 0 sert
ihlal (DONMUS_GUN 0), yayınlanabilir**, optimuma uzaklık %97,1 (ilk çözüm
%97,6). Not sıfır: motorun kendi planının molaları aday noktalarına oturdu.

Sayılar: 18 test (`test_donmus_gun.py`), 9 mutasyon hepsi öldü (toplam 180),
bekçi 21, vaka aracı 36 vaka · 36 kırmızı, altın senaryolar 12, motor 499 test.

→ T-29 · K-49 · şartname §6.6, §11.2, §11.3, §11.4 · `09-motor/cozucu/model.py` (`_donmus_plani_esle`, `_donmus_sabitle`, `_kisit`, `_donmus_suz`) · `09-motor/cozucu/coz.py` · `09-motor/dogrulayici/kurallar.py` (`donmus_gun`) · `09-motor/dogrulayici/denetle.py` (`_gecmis_ihlalleri_isaretle`) · `09-motor/testler/test_donmus_gun.py` · `08-motor-testleri/gercekci-veri-seti/coz-olc.py --donmus`


## K-55 · PDKS'ten yalnız **ham giriş-çıkış** gelir; bilinen boş gün TShift'in kendi plan geçmişi + izin satırlarıdır; yıl içi fazla mesai PDKS ham verisinden **TShift'in hesabıyla** gelir

**Soru (K-47'nin açık ucu, 1 Ekim):** PDKS'teki planlanan süresi `00:00`
olan satır *"bilinen boş gün"* sayılabilir mi? Ham veri ölçüldü
(`07-GERCEK-VERI-BULGULARI.md` §7): sayılamaz — o alan plan değil, kart
okutulunca sonradan değişen takvim. Yan bulgular: PDKS'in normal/eksik/fazla
mesai kolonları sabit gündüz şablonuna göre hesaplanıyor, vardiyalı
çalışan için yanlış (17:46–00:01'e *"eksik 9:16, fazla 5:31"*); gece
yarısını aşan vardiya PDKS'te de başladığı günde; izin kayıtları güvenilir.

**Karar (1 Ekim 2026 akşamı, Mustafa), üç madde:**

1. *"Onaylıyorum."* — **Bilinen boş günün kaynağı PDKS'in `00:00`'ı
   değildir.** Kaynak: TShift'in kendi yayınladığı önceki planlar (ilk
   haftalardan sonra geçmiş zaten elimizde, geçmiş-eksik raporunun gürültüsü
   kendiliğinden düşer) ve PDKS'teki izin satırları (yıllık izin, ücretsiz
   izin, evlenme, taşınma… — o gün çalışmadığı kesindir).
2. *"PDKS'ten tam giriş-çıkış alacağız, mola uyumunu falan kontrol
   etmeyeceğiz. Bizim PDKS'ten alacağımız tek bilgi çalışanın hangi günler
   çalıştığı ve saat aralıkları."* — **PDKS'ten yalnız ham giriş-çıkış
   aralıkları alınır**; süre, dinlenme ve fazla mesai hesabını ürün yapar.
   PDKS'ten mola bilgisi gelmez ve PDKS verisiyle mola kuralları denetlenmez.
   Çıkışı girişten küçük satır gece vardiyasıdır (başladığı güne); 16 saati
   aşan satır ve gece 00:00–02:00 arası *"giriş"*li satır (çift kart okutma
   artığı) **bilinmeyen gün** sayılır.
3. *"Bordrodan bu bilgiyi aktartamayız. Bunu PDKS'ten almalıyız, ki
   alabiliriz. Gerekirse PDKS firmasının çıktısını bizim istediğimiz formatta
   alırız, müşteriye düzelttiririz ya da araya bir RPA koyarız. Ürünü almayı
   kabul eden firma bu yolu öyle ya da böyle açacak; bu uygulamayla denetime
   de girecekler."* — **Yıl içi fazla mesai toplamı PDKS'ten gelir, ama
   PDKS'in hazır fazla mesai kolonundan değil: ham giriş-çıkıştan TShift'in
   kendi hesabıyla.** Benim *"bordrodan"* önerim bordroya güvenden değil,
   PDKS'in hazır kolonuna güvensizliktendi; Mustafa'nın yolu ikisini de
   çözüyor — kaynak PDKS, hesap TShift. PDKS firmasından istenecek tek şey:
   kişi · gün · giriş saati · çıkış saati. Başka hiçbir hesaplanmış alan
   okunmaz.

**Hesap kuralı (`yil_ici_fazla_mesai_saat`, içe aktarma tarafı):** haftanın
net çalışması = giriş-çıkış aralıklarının toplamı − firmanın mola
politikasındaki ücretsiz yemek molası (PDKS'ten mola gelmediği için
politikadan düşülür); 45 saati (haftalık normal sınır) aşan kısım o haftanın
fazla mesaisi; yıl içi toplam = takvim yılı başından planlanan haftaya kadar
haftalık fazlaların toplamı. Bilinmeyen gün varsa toplam **"en az şu kadar"**
gelir ve bilinmeyen gün sayısı raporlanır; motor eksik geçmişte durmaz,
bildirir (K-42). Devreye alma: takvim yılı başından itibaren PDKS ham verisi
bir kez içe aktarılır (açılış bakiyesi), sonra haftalık.

**Motor tarafında değişiklik yok;** bunlar içe aktarma (entegrasyon) ve
backend kurallarıdır. Şartname §11.2 notu ve §6.2 yıllık tavan satırı
güncellendi. K-47'nin açık ucu kapandı; T-77'nin veri tarafı kapandı
(arayüzdeki *"gördüm"* onayı açık).

→ K-42 · K-47 · T-77 · `07-GERCEK-VERI-BULGULARI.md` §7 · `07-motor/pdks-ms-gece-yarisi.py` · şartname §6.2, §11.2
