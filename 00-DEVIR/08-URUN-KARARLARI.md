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
(`v2/KABUL-OLCUTLERI.md` K-1…K-7'ye atıf yapıyor); geriye dönük ekleme yüzünden
numaralar kayarsa o atıflar sessizce yanlış olur.

Yani geçmişteki bir karar sonradan kayda alınırsa **sıradaki boş numarayı**
alır, araya sıkıştırılmaz.

---

## İçindekiler

| # | Karar | Tarih | Durum |
|---|---|---|---|
| [K-1](#k-1--sınır-değerler-ihlal-sayılır-ve-firma-ayarıdır) | Sınır değerler ihlal sayılır (ve firma ayarıdır) | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-2](#k-2--kiracı-saat-dilimi-iana-adı-olmak-zorunda) | Kiracı saat dilimi IANA adı olmak zorunda | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-3](#k-3--çözücü-istatistikleri-çıktıya-girer-ve-müşteriye-gösterilir) | Çözücü istatistikleri çıktıya girer ve müşteriye gösterilir | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-4](#k-4--mola-hakkı-iş-kanununa-göre-brüt-süreden-hesaplanır) | Mola hakkı İş Kanunu'na göre, brüt süreden | 14 Eyl 2026 | ⏳ uzman teyidi bekliyor |
| [K-5](#k-5--geçmişi-olmayan-kiracıda-motor-çalışır) | Geçmişi olmayan kiracıda motor çalışır | 14 Eyl 2026 | ⏳ uygulanmadı |
| [K-6](#k-6--sonbahar-dst-kontrolü-ileri-tura) | Sonbahar DST kontrolü ileri tura | 14 Eyl 2026 | ✅ kayıtta |
| [K-7](#k-7--çözümsüzlük-teşhisine-hafta-seviyesi-eklenir) | Çözümsüzlük teşhisine hafta seviyesi eklenir | 14 Eyl 2026 | ⏳ uygulanmadı |

**Durum işaretleri:** ✅ uygulandı ve bir bekçisi var · ⏳ karar verildi,
uygulanmadı · ⚠ uygulandı ama bekçisi yok.

---

## K-1 · Sınır değerler ihlal sayılır (ve firma ayarıdır)

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

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A4 (iki ayarla da koşulur) ·
spec v1.4 §5–§6'ya girecek (T-6)

---

## K-2 · Kiracı saat dilimi IANA adı olmak zorunda

**Karar (14 Eylül 2026, Mustafa).** Saat dilimi sabit ofsetle (`+03:00`)
verilirse girdi **reddedilir** — şema hatası döner. Uyarı verip devam edilmez.

**Neden:** Spec §6.3 zaten IANA adını (`Europe/Istanbul`) şart koşuyordu ama
ihlalinde ne olacağını yazmıyordu. Uyarı sessizce geçilir; zaman modelini
sonradan değiştirmenin bedeli *"her plan yeniden yorumlanır"* seviyesindedir.

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A5 madde 5 · spec v1.4 (T-7)

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

> ⚠ **Bu bir hukuki yorumdur.** Yapay zekâ türetti, avukat değil. İş Kanunu
> md. 68 için uzman teyidi alınmalı. Teyit gelene kadar bu satır
> `[çıkarım]` sayılır.

**Yan sonuç:** Spec §11.2'deki örnekte 08–16 vardiyası için `mola_dk 30`
yazıyor; §6.2 tablosuna göre 60 olmalı. v1.4'te düzeltilecek (T-3).

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A8 · §7 V-4

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

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A11 madde 5 · spec v1.4 (T-8)

---

## K-6 · Sonbahar DST kontrolü ileri tura

**Karar (14 Eylül 2026, Mustafa).** 25 saatlik gün kontrolü (31 Ekim 2027)
v1 fikstürlerine girmez.

**Neden:** İlkbahar geçişi asıl riski yakalıyor — duvar saatiyle 11 saat görünen
dinlenmenin gerçekte 10 saat olması. Sonbaharda gün uzar, kural gevşer; sessiz
ihlal üretmez.

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A5 sonu

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

→ `08-motor-testleri/v2/KABUL-OLCUTLERI.md` A9(c) · spec v1.4 §11.3 (T-5)

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
