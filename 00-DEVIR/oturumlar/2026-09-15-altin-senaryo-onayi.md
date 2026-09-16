# Oturum · 15–16 Eylül 2026 · altın senaryoların onayı

**Başlangıç:** `v0.8-devir` · 39/39 test yeşil · A1–A12 kabul cümleleri
v2 hâliyle onay bekliyor
**Bitiş:** **ürün kodu değişmedi · test eklenmedi.** Üretilen: A1–A12'nin
**onaylanmış** hâli (`08-motor-testleri/v5/`), on yeni ürün kararı (K-8…K-17),
bir geri alma (K-1), iki şartname eksiğinin tespiti

> Bu dosya **append-only**. Yeniden yazılmaz, yalnız eklenir.
> Oturum 15 Eylül akşamı başladı, 16 Eylül'ün ilk saatlerinde bitti.
> Aynı gün ikinci oturum: birincisi `2026-09-15-calisma-bicimi-opencode.md`.

---

## 1. İş parçası

`00-BURADAN-BASLA.md` §3'teki sıradaki adım: A1–A12 kabul cümlelerinin onayı.

Mustafa önce şunu sordu: *"Ben tam olarak neyi yorumluyorum, neye onay
veriyorum?"* — ve bu soru haklıydı. v2 dokümanı yazılım tarafına göre
yazılmıştı; onaylanacak cümleler teknik ayrıntının altında kalıyordu.

## 2. Okunanlar

Önceki pencerenin yazdıkları önce **makineden geri okundu** (yerel kopyaya
güvenilmedi): `00-BURADAN-BASLA.md`, `06-ACIK-RISKLER.md`,
`DEGISIM-GUNLUGU.md` ve yeni `oturumlar/2026-09-15-calisma-bicimi-opencode.md`.
Değişen dört dosya mtime karşılaştırmasıyla bulundu; kalan on bir dosya
okunmadı.

## 3. Sürüm zinciri — dört sürümde ne oldu

| Sürüm | Ne değişti | Neden |
|---|---|---|
| v2 → **v3** | İçerik aynı, **anlatım iş diline çevrildi** | Mustafa onaylayacağı cümleyi göremiyordu |
| v3 → **v4** | **İçerik değişti:** sahne, A2, A3, A7, A8 baştan | Mustafa'nın geri bildirimi |
| v4 → **v5** | Onay turunun ekleri işlendi, donduruldu | Onay tamamlandı |

v1–v4 dondurulmuş, hiçbirine dokunulmadı.

## 4. Claude'un üç hatası — ayrı ayrı

### 4.1 Sahne gerçekçi değildi

"T-10" sahnesi tek vardiya tipi, herkes tam zamanlı, cumartesi yok diye
kurulmuştu. Mustafa: *"Mantık olarak kurduğun problem ve çözüm doğru, sadece
realistik değil. Bizim problemini çözeceğimiz yerler muhtemelen birden fazla
mesai tipi olan ve part-time eleman çalıştıran kurumlar olacak."*

Yeni sahne **S-10**: 7 tam zamanlı + 3 part-time (biri salı günleri derste,
biri 16:00'dan sonra çalışamıyor), üç vardiya tipi, cumartesi 09:00–13:00 üç
kişilik nöbet. Kapasitesi programatik doğrulandı, Mustafa onayladı.

### 4.2 A7'de tercih modeli tamamen yanlıştı

Çalışanların tek tek vardiya tercihi bildirdiği varsayılmıştı. Mustafa:
*"Çalışan bir çalışma saati veya vardiyası belirtemez. Sözleşmeden gelir bu
kural. Sadece part-time çalışanlar için bu kural geçerlidir."*

Senaryo baştan yazıldı: yumuşak gerilim artık **cumartesi adaleti ile kapsama**
arasında. Karar K-13.

### 4.3 K-1: yanlış soru soruldu

14 Eylül'de Mustafa'ya *"tam 11 saat dinlenme ihlal mi?"* diye sorulmuştu.
15 Eylül'de sordu: *"Ben neye yanlış karar verdim anlamadım."*

**Haklıydı — yanlış bir karar vermemişti, yanlış bir soru sorulmuştu.** İki ayrı
şey tek soruya sıkıştırılmıştı:

| Soru | Tipi |
|---|---|
| "11,0 saat, 'asgari 11 saat' kuralına uyuyor mu?" | **Aritmetik.** Ürün kararı değil, sorulmamalıydı |
| "Yönetici elle 8 saate düşürürse ne olur?" | **Ürün kararı.** Mustafa'nın cevabı zaten doğruydu |

K-1 geri alındı, yerine K-11. **Ders:** teknik kenar durumlarını ürün
kararıymış gibi Mustafa'ya yollamak hem dikkatini israf ediyor hem yanlış
varsayılan üretme riski taşıyor. Sorulmadan önce "bu ürün kararı mı" diye
ayrılmalı.

## 5. Alınan kararlar — K-8…K-17

Tamamı `08-URUN-KARARLARI.md`'de gerekçeleriyle.

| # | Karar |
|---|---|
| K-8 | Hedef kapsama sözü **%95**, %100 değil (asgari %100 ve sert kalır) |
| K-9 | **İzin planlamayı ezer** — izinliye atama yapılamaz, sonradan onaylanan izin kişiyi plandan düşürür, yönetici plana girdiğinde sebebiyle görür, asistan öneri sunar |
| K-10 | **Yönetici çözümsüz planı kabul edebilir** — en iyi plan sunulur, ihlal kim/ne zaman/neden ile kaydedilir. Yasal kural edilemez, firma kuralı edilebilir |
| K-11 | Sınır değer ihlal değil (K-1'in yerine) |
| K-12 | **DST ertelendi**, altyapı kalıyor |
| K-13 | **Çalışan tercihi yok**, uygunluk sözleşmeden gelir, part-time için sert |
| K-14 | Öğle arası vardiya şablonu parametresi; tek blok; **`MOLA_KAPSAMASI` YUMUŞAK**, `MOLA_HAKKI` sert |
| K-15 | Plan kopyalama **doğrulayıcıyı** çalıştırır, editöre taşır |
| K-16 | **Yayın kapısı:** taslak ihlal taşıyabilir, yayınlanmış plan taşıyamaz |
| K-17 | **`yasal` bayrağı üç durumlu**; belirsiz = kabul edilemez |

### K-16 ve K-17 nasıl doğdu

Mustafa A4'ü onaylarken ekledi: *"Cem'in çakışan mesaisi mantıksız, bu
çözülmeden plan yayınlanamaz. Zaten yasal ihlal de var."*

Bu iki şey doğurdu. Birincisi **yayın kapısı** ayrımı: taslak plan ihlal
taşıyabilir (A2'de izin birini düşürünce, A3'te imkânsızlıkta, A12'de kopyada),
ama yayınlanmış plan taşıyamaz. İkincisi, kapının **hangi kuralın yasal
olduğunu bilmeye** dayandığının fark edilmesi — ve şartnamede o bilginin
olmadığının görülmesi.

## 6. Bulunan iki şartname eksiği

**İkisi de senaryolar yazılırken çıktı, şartname okunurken değil.**

| # | Eksik | Sonucu |
|---|---|---|
| 1 | `leaves` tablosunda **izin durumu alanı yok** | İzin iptali modellenemiyordu (K-9) |
| 2 | §6 kataloğunda **`yasal` sütunu yok** | K-10 ve K-16 **uygulanamaz**; sistem hangi ihlalin kabul edilebileceğini bilemez |

İkincisi ayrıca çözülmemiş bir tasarım sorusu ortaya çıkardı: **bayrak kurala mı
ait, eşiğe mi?** `GUNLUK_AZAMI` örneği — kanunun tavanı 11 saat, bizim
varsayılanımız 9. 9–11 arası aşım firma politikasının ihlali, 11 üstü kanunun.
Yasal kuralların ayrıca bir "yasal sınır" değeri olması gerekiyor.

**Yeni açık madde:** A-15 (şartname v1.4, on maddelik fark) ve A-16 (iki hukuki
yorum uzman bekliyor) `06-ACIK-RISKLER.md`'ye eklendi.

## 7. `yasal` bayrağının varsayılanı — küçük ama önemli bir ekleme

Mustafa: *"Sen kurallara şimdilik bir yasal kural mı true ekle yeter. Gerisini
ileride de çözebiliriz, teknik olarak bir problemimiz de yok."*

Tespiti doğru ama **davranışsal bir sonucu vardı**: sınıflandırılmamış bir kural
için sistem ne yapacak? Bayrak üç durumlu yapıldı ve **belirsiz = yasal gibi
davranılır** (kabul edilemez) seçildi. Gerekçe `02-DEGISMEZLER.md` Y-8'in
aynısı:

| Yön | Sonucu |
|---|---|
| Belirsiz → firma kuralı sayılsaydı | Sınıflandırılmamış bir **yasal** kuralın ihlali sessizce kabul edilebilirdi |
| Belirsiz → yasal sayılınca | Yönetici kabul edemez, şikâyet eder, biz sınıflandırırız |

**Şikâyet, sızıntıdan iyidir.**

## 8. Kod değişikliği

**Yok.** 39/39 durumu aynı, `v0.8-devir` etiketi aynı. Hiçbir test eklenmedi,
hiçbir fikstür yazılmadı.

## 9. Üretilen ve değişen dosyalar

| Dosya | Ne |
|---|---|
| `08-motor-testleri/v3/`, `v4/`, `v5/` | Üç yeni sürüm; v5 onaylanmış hâl |
| `08-motor-testleri/ONAY-DURUMU.md` | **Yeni** — onay turunun kaydı, tur kapanınca özete indirildi |
| `00-DEVIR/08-URUN-KARARLARI.md` | K-8…K-17 eklendi, K-1 geri alındı olarak işaretlendi |
| `00-DEVIR/02-DEGISMEZLER.md` | Özet tablosu ikinci kez düzeltildi (sütunlar toplamıyordu) |
| `00-DEVIR/04-TEST-HARITASI.md` | Altın senaryo bölümü onay durumuna göre |
| `00-DEVIR/06-ACIK-RISKLER.md` | **A-15** ve **A-16** eklendi, öncelik tablosu yenilendi |
| `DENETIM.py` | Üç iyileştirme: kod bloklarını atlama, değişmez tablosu jenerik sayımı, "bilerek yok" listesi |
| `01-PROJE-KIMLIGI.md`, `RISKLER-VE-ONLEMLER.md` | Kırık test adları düzeltildi |

## 10. DENETIM.py bu turda üç kez işe yaradı

1. **Kendi hatamı yakaladı.** 14 Eylül'de değişmez özet tablosunu düzeltmiştim;
   düzeltme eksikti — sütunlar toplamıyordu (39+4+2=45, toplam 47). İki satır
   aradan düşüyordu: `G-4` yalnız 🔒 işaretli, `G-8` insan incelemesine
   bırakılmış. Betik ikinci düzeltmede de yanımdaydı.
2. **Yanlış alarmını da gösterdi.** `KALITE-ARASTIRMASI-DEGERLENDIRME.md`'deki
   `38/38` bir **kod bloğu içindeki örnek şablondaydı** — iddia değil. Sayıyı
   değiştirmek yanlış olurdu; betik düzeltildi, artık kod bloklarını atlıyor.
3. **Bayat sürüm atıflarını buldurdu.** Devir dosyalarında 25 yerde
   `08-motor-testleri/v2/` yazıyordu; v5'e güncellendi.

⚠ **Commit kontrolü üçüncü oturumdur koşmadı** — bu pencerelerde Mustafa'nın
makinesinde kabuk çalıştırılamıyor (Windows tarafında bir mount sorunu).
İlk koşuyu Mustafa yapacak.

## 11. Sıradaki adım

> **Fikstürler.** `08-motor-testleri/v5/fikstur/A01.json … A12.json` —
> **A5 hariç, 11 dosya.** Her biri `fikstur-denetleyici.py`'den geçirilir.
> Sonra pytest iskeleti (A1–A9) ve xUnit testleri (A10–A12). Motor olmadığı
> için hepsi **kırmızı** başlar.
>
> ⚠ `v2/fikstur/A04.json` ve `v3/fikstur/A04.json` **geçersiz**: eski T-10
> sahnesine dayanıyor ve geri alınan K-1'e göre yazılmışlar. Yalnız biçim
> örneği.
>
> **Paralelde:** A-15 (şartname v1.4) ve A-16 (hukuk teyidi).

## 12. Bu oturumun dersi

14 Eylül'ün dersi *"kaynağın kendisi tutarsız olabilir"*, 15 Eylül'ün
*"başka birinin çalışan kurulumu senin kurulumun hakkında kanıt değildir"*ti.
Bunun devamı:

**Kabul ölçütü yazmak, şartnameyi denetlemenin en ucuz yolu.** İki şartname
eksiği de senaryolar yazılırken çıktı — şartname baştan sona okunurken değil.
Sebebi basit: okurken "yazılmış mı" diye bakarsın, senaryo yazarken "bu
davranışı ifade edebiliyor muyum" diye. İkinci soru eksiği bulur.

İkinci ders Claude'a ait ve K-1'den geliyor: **bir soruyu sormadan önce onun
ürün kararı olup olmadığı ayrılmalı.** Aritmetik bir kenar durumu ürün
kararıymış gibi sunmak, cevap doğru gelse bile yanlış bir varsayılan üretir.
