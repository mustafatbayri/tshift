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
