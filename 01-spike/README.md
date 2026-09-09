# Spike testleri

Motorun gerçekten çalışıp çalışmadığını anlamak için yapılan ar-ge testleri.
Ürün kodu değil; ürüne yatırım yapmadan önce riski ölçmek için yazıldı.

---

## İçindekiler

1. [Versiyonlar](#versiyonlar)
2. [Neden test ettik](#neden-test-ettik)
3. [Test kronolojisi ve sonuçlar](#test-kronolojisi-ve-sonuçlar)
4. [Testlerin bulduğu hatalar](#testlerin-bulduğu-hatalar)
5. [Kanıtlanan ve kanıtlanmayanlar](#kanıtlanan-ve-kanıtlanmayanlar)

---

## Versiyonlar

| Versiyon | Tarih | İçerik |
|---|---|---|
| `v1-2026-09-09-fizibilite` | 9 Eylül 2026 | 7–8 Eylül'de yapılan tüm testlerin son hâli |

**Not:** v1'e kadar dosyalar yerinde güncellendi, bu yüzden ara adımların ayrı kodu
elimizde yok. Aşağıdaki kronoloji o adımların kaydıdır. Bu tarihten sonra her
değişiklik yeni versiyon klasörüne gidiyor.

---

## Neden test ettik

Ürünün tek satışı var: **"plan kurallara uyar ve iyidir."** Bu cümle yanlışsa ürün yok.
Yazılıma para ve zaman harcamadan önce şunları ölçmek istedik:

1. Motor gerçekten kurallara uyan bir plan üretiyor mu?
2. Ürettiği plan "iyi" mi, yoksa sadece geçerli mi?
3. Kaç çalışana kadar dayanıyor?
4. Farklı sektörlerde çalışıyor mu, yoksa çağrı merkezine mi özel?
5. Yönetici plana müdahale ettiğinde ne oluyor?

### Test yönteminin en önemli kuralı: bağımsız denetleyici

Planı üreten kod (`planla.py`, `cpsat.py`) ile planı denetleyen kod
(`degerlendirici.py`) **hiçbir mantığı paylaşmaz.**

Sebebi şu: motorun kendi kendini kontrol etmesi, öğrencinin kendi sınavını okuması
gibidir. Motor "11 saat dinlenme"yi yanlış hesaplıyorsa, aynı yanlış hesapla kontrol
edince her şey yolunda görünür. Denetleyici kuralları sıfırdan, bağımsız olarak
yeniden hesaplar. Motor bir kuralı yanlış anlamışsa denetleyici bunu yakalar.

Bu ayrım sayesinde aşağıdaki 12 hatanın hepsi bulundu. Tek kodla çalışsaydık
hiçbirini göremezdik.

---

## Test kronolojisi ve sonuçlar

### 1 · Çağrı merkezi — temel senaryo
**Ne:** 200 çalışan, 3 ekip, haftalık plan, 21 kural, geçmiş hafta verisi.
**Neden:** En basit gerçekçi vaka. Burada çalışmıyorsa hiçbir yerde çalışmaz.

| | Greedy (basit yöntem) | CP-SAT (asıl motor) |
|---|---|---|
| Sert kural ihlali | 0 | **0** |
| Hedef kapsama | %95,7 | **%99,5** |
| Fazla mesai | 92 saat | **0 saat** |
| Optimuma uzaklık | ölçülemez | **%0,01** |

"Optimuma uzaklık %0,01" şu demek: matematiksel olarak mümkün olan en iyi plan ile
motorun bulduğu plan arasında binde bir fark var. Pratikte en iyi plan.

**Dosyalar:** `girdi.json`, `planla.py`, `cpsat.py`, `sonuc.json`

---

### 2 · Sabotaj sınavı — denetleyici gerçekten görüyor mu?
**Ne:** Geçerli plana kasten hata sokup denetleyicinin yakalayıp yakalamadığına bakmak.
Çağrı merkezinde 9, otelde 12 farklı bozma denendi (izinli günde vardiya, çakışan
vardiya, dinlenmesiz peş peşe vardiya, kapsama düşürme, mola silme...).

**Sonuç: 9/9 ve 12/12 yakalandı.**

Buna ek olarak çözümsüzlük teşhisi test edildi: plan imkânsız hâle getirildiğinde
motor "olmadı" demekle kalmıyor, **hangi kuralın imkânsızlığa yol açtığını** söylüyor.
Her sert kuralı tek tek gevşetip hangisinin çözümü açtığına bakarak buluyor.
Yöneticiye "plan üretilemedi" yerine "cuma gecesi için yetkin personel yetmiyor"
diyebilmemizin sebebi bu.

**Dosyalar:** `sinav.py`

---

### 3 · Ölçek — kaç çalışana kadar dayanıyor?
**Ne:** 200 / 500 / 1000 / 2000 çalışanla aynı test.

| Çalışan | Model kurulumu | 60 sn'de kapsama | Optimuma uzaklık |
|---|---|---|---|
| 200 | anlık | %99,5 | %0,01 |
| 500 | ~0,3 sn | %99,4 | %0,1 |
| 1000 | ~0,7 sn | %99,2 | %2,4 |
| 2000 | 1,5 sn | %98,9 | %8,9 |

2000 çalışanda bile kullanılabilir plan çıkıyor; sadece "en iyi"ye uzaklık artıyor.
Süreyi 5 dakikaya çıkarınca bu fark kapanıyor. **Ölçek ürün riski değil.**

Ayrıca: 300 çalışanla 300 saniye verildiğinde optimuma uzaklık %0,03'e iniyor.

**Dosyalar:** `olcek.py`, `uret.py`

---

### 4 · Otel — çok sektörlülük iddiası
**Ne:** 300 çalışan, 5 departman (ön büro, kat hizmetleri, F&B, mutfak, güvenlik),
7/24 çalışma, gece vardiyaları, 19 kural, yetkinlik gereksinimleri (yabancı dil,
barista).
**Neden:** Ürünün satış vaadi "tek üründe çok sektör". Bu test o vaadin kanıtı.

| | Greedy | CP-SAT |
|---|---|---|
| Sert kural ihlali | 5 | **0** |
| Hedef kapsama | — | **%99,6** |
| Optimuma uzaklık | — | **%0,03** |
| Adalet (gece dağılımı σ) | — | **1,15** |

**En önemli bulgu:** gece vardiyası kuralları (İş Kanunu md. 69 gece azami 7,5 saat,
ardışık gece limiti) **koda yazılmadı, veriye eklendi.** Yani yeni bir sektör için
kod değiştirmek gerekmiyor, kural seti değiştirmek yetiyor. Ürünün konfigürasyonla
çok sektöre açılması bu yüzden mümkün.

Teknik olarak çözülmesi gereken şey gece vardiyasının iki güne birden dokunmasıydı.
Saat modeli genişletildi: `"31:00"` = ertesi gün 07:00. Ayrıca "devir" eklendi —
geçen haftanın pazar gecesi 23:00–07:00 vardiyası bu haftanın pazartesi sabahını
kapsıyor ve plan bunu sayıyor.

**Dosyalar:** `uret_otel.py`, `girdi_otel.json`, `otel_sonuc.json`

---

### 5 · Öneri motoru — yönetici müdahale ettiğinde
**Ne:** Yönetici plandan iki kişi çıkarıyor, birini başka güne kaydırıyor. Motor
oluşan boşluklara aday öneriyor, her adayın sonucunu açıklıyor, kararı yönetici veriyor.
**Neden:** Ürün kararı olarak "yerel onarım" seçildi — yöneticinin elle yaptığı işi
motor bozmaz, sadece boşluğu doldurmak için öneri getirir.

**Sonuç: 0 hatalı öneri, 0 kaçırılan boşluk.**

Bu testte ürünün en tehlikeli hatası bulundu, aşağıda #10'da anlatılıyor.

**Dosyalar:** `oneri.py`

---

### 6 · Plan kararlılığı — yeniden planlarken her şey değişmesin
**Ne:** Bir kişi hastalanınca planı yeniden üretiyoruz. Naif yöntemde plan baştan
kuruluyor ve 200 kişinin vardiyası değişebiliyor — sahada kabul edilemez.

**Sonuç: değişimin %91'i önlendi.** Motor mevcut atamaları koruma ödülüyle çalışıyor;
sadece gerçekten değişmesi gereken yerler değişiyor.

Ayrıca hafta ortası yeniden planlama test edildi: geçmiş günler donduruldu, motor
artık olmuş bitmiş günleri yeniden yazmıyor.

**Dosyalar:** `yeniden_planla.py`, `hafta_ortasi.py`

---

### 7 · Talep modeli — kaç kişi gerekiyor
**Ne:** Çağrı merkezi için Erlang C formülüyle gereken personel hesabı, ardından
bunun bağımsız bir kuyruk simülasyonuyla doğrulanması.
**Neden:** "Bu saatte kaç kişi lazım" sorusunun cevabı yanlışsa, plan ne kadar
mükemmel olursa olsun yanlış plandır.

Formülün verdiği sayı simülasyonla doğrulandı. Kapanma payı (shrinkage — mola, izin,
eğitim, devamsızlık) ayrı bir parametre: %30 alındığında gereken kadro %45 artıyor.
Bu yüzden müşteri başına ayarlanabilir olması gerekiyor.

**Dosyalar:** `talep.py`

---

### 8 · Çok haftalı adalet
**Ne:** 4 hafta üst üste plan üretip gece vardiyalarının, hafta sonlarının ve
saatlerin kişiler arasında nasıl dağıldığına bakmak.

| | Hafızasız | Devir yüküyle |
|---|---|---|
| Gece dağılımı σ | 8,21 | **3,18** |

Motor haftalar arası hafıza olmadan çalıştığında, her hafta bağımsız olarak "en iyi"
planı buluyor ama aynı kişiler sürekli gece alıyor. Devir yükü eklenince yük dengeleniyor.

Adalet penceresi **aylık** olarak kararlaştırıldı: birikim ay sonunda sıfırlanır.

**Dosyalar:** `cok_hafta.py`

---

## Testlerin bulduğu hatalar

Bu liste testlerin niye yapıldığının cevabı. Hepsi ürüne girseydi sahada patlardı.

| # | Hata | Sonucu ne olurdu |
|---|---|---|
| 1 | Saat biçimlendirmede 24.00 → "00:00" yazılıyordu, akşam vardiyaları sıfır uzunluk oluyordu | 638 sert ihlal, %49 kapsama. Plan tümüyle çöp. |
| 2 | 8 saatlik vardiyaya 45 dk mola konmuştu, kural 60 dk istiyor | Yasal ihlal |
| 3 | Mola yerleştirme, kapsama zaten yetersizken bile mola koyuyordu | 22 ihlal |
| 4 | CP-SAT modeli kuraldan katıydı (molayı ilk/son saatte yasaklıyordu) | Motor bazı geçerli planları hiç aramıyordu |
| 5 | Adalet sapması iki farklı yöntemle ölçülüyordu | Yanlış rakamla karar verecektik |
| 6 | Model kurulumu kare karmaşıklıktaydı | 2000 çalışanda 37,3 sn; indeksleme sonrası 1,5 sn |
| 7 | Değişken gölgelemesi (`x` döngü değişkeni kararları eziyordu) | Motor çalışmıyordu |
| 8 | Takım lideri ataması gece 00:00–06:00'yı kapsayamıyordu | Otelde gece rol açığı |
| 9 | Onarım adımı yöneticinin kilitlediği atamaları siliyordu | **Kullanıcının kararı sessizce geri alınıyordu** |
| 10 | **Öneri doğrulaması ihlal *sayısını* karşılaştırıyordu, kimliğini değil** | Bir rol açığını kapatıp yerine dinlenme ihlali yaratan aday "sorunsuz" görünüyordu. **Yöneticiye kural ihlal eden öneri sunuyorduk.** |
| 11 | Devir vardiyaları kapsamada sayılmıyordu | Olmayan boşluklar için öneri üretiliyordu |
| 12 | Adalet yanlış popülasyonda ölçülüyordu ("141 kişi hiç gece almamış" — 108'i zaten gece çalışamayan kişilerdi) | Gerçek rakam 187 uygun kişiden 33'ü |

10 numara en kritik olanı. Ürünün tüm güvenilirliği "önerilerimiz kural ihlal etmez"
vaadine dayanıyor; o hata sahaya çıksa vaat yalan olurdu.

---

## Kanıtlanan ve kanıtlanmayanlar

### Kanıtlandı
- Motor kurallara uyan plan üretiyor (0 sert ihlal, iki ayrı sektörde)
- Ürettiği plan sadece geçerli değil, optimuma çok yakın
- 2000 çalışana kadar ölçekleniyor
- Yeni sektör için kod değil kural seti değişiyor
- Çözümsüzlükte sebebi söyleyebiliyor
- Yönetici müdahalesinde plan bozulmuyor, öneriler kural ihlal etmiyor
- Haftalar arası adalet dengeleniyor
- "Kaç kişi lazım" hesabı bağımsız simülasyonla doğrulandı

### Kanıtlanmadı / kapsam dışı bırakıldı
- **Bozuk veri dayanıklılığı** — testlerde veri hep tam kabul edildi. Bilinçli karar:
  veri girişi operasyonel olarak çözülecek, basit giriş/çıkış verisiyle ilerlenecek.
- **Gerçek müşteri verisi** — tüm girdiler sentetik. Gerçek bir işletmenin verisiyle
  hiç çalışılmadı.
- **Otelde KAPSAMA ve CALISAN profilleri** — otel senaryosunda sadece DENGELI profili
  koşuldu. Diğer iki profil çağrı merkezinde koşuldu.
- **Eşzamanlılık** — aynı planı iki yönetici aynı anda düzenlerse ne olur, test edilmedi.
  Bu yazılım tarafının işi, motorun değil.
