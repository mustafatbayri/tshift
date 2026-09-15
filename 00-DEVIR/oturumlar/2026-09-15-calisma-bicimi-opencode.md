# Oturum · 15 Eylül 2026 · çalışma biçimi — paralel ajan modeli değerlendirmesi

**Başlangıç:** `v0.8-devir` · 39/39 test yeşil · CI yeşil · motor yok ·
A1–A12 kabul cümleleri onay bekliyor
**Bitiş:** **ürün kodu değişmedi · test eklenmedi · ölçüm yapılmadı.**
Üretilen tek şey karar: geri bildirim yüzeyleri (2 pencere) kuruluyor,
**opencode şimdilik kullanılmıyor**, ikinci ajan Aşama 2'ye ertelendi.

> Bu dosya **append-only**. Yeniden yazılmaz, yalnız eklenir.

---

## 1. İş parçası

**Sıradaki adım değildi.** `00-BURADAN-BASLA.md` §3 hâlâ A1–A12 onayını
bekliyor ve bu oturumda ona dokunulmadı.

Mustafa bir videoda gördüğü çalışma modelini sordu:

> 1. pencere: kodu Claude yazıyor · 2. pencere: hata ayıklamayı **opencode**
> paralel yapıyor · 3. pencere: testler · 4. pencere: sunucu günlükleri.

Soru: *"Bu modeli veya benzerini kurmalı mıyız?"*

## 2. Okunanlar

`00-BURADAN-BASLA.md` (§2, §3, §5, §5b, §6, §7), `03-MIMARI-KARARLAR.md`,
`06-ACIK-RISKLER.md` (📌 Araç kararı bölümü ve öncelik tablosu),
`08-URUN-KARARLARI.md`, `oturumlar/2026-09-14-altin-senaryolar.md`,
`DENETIM.py`, `DEGISIM-GUNLUGU.md`.

**Depo dışı kaynak:** opencode ve paralel ajan araçları üzerine üç genel
yayın. Bunlar **ölçüm değil sektör yazısıdır**; §3'e bakınız.

## 3. Kanıt durumu — bu bölüm önce okunmalı

`00-BURADAN-BASLA.md` §5: *"Bu klasöre, karşılığında çalıştırılabilir bir
kanıt gösteremediğin hiçbir cümle yazılmaz."*

Bu oturumda **çalıştırılabilir kanıt üretilmedi.** Dolayısıyla 14 Eylül'ün
süreç kuralı (`06-ACIK-RISKLER.md` · *Veri kapsam kararı vermez*) burada da
geçerlidir ve ayrım şöyle işaretlenir:

| Tür | Bu oturumda ne var |
|---|---|
| **Bulgu** (ölçüm, tartışmasız) | Yalnız deponun kendi durumu: R5 kapalı, CI yeşil, `TEST.ps1` API'yi durduruyor (`00-BURADAN-BASLA.md` §7), `00-DEVIR/` dokuz dosyada |
| **Öneri** (karar Mustafa'nın) | 4 pencere modelinin değerlendirmesi, 2 pencere kararı, opencode'un ertelenmesi — **hepsi muhakeme, hiçbiri ölçüm** |

**Sonuç:** Aşağıdaki kararların hiçbiri bugün kanıtlanmadı. Aşama 2'nin
(§8) ölçüm şartı tam olarak bu boşluğu kapatmak için kondu.

## 4. Modelin ayrıştırılması — dört pencere aynı şey değil

Videodaki model tek bir fikir değil, birbirinden bağımsız iki fikrin
üst üste binmiş hâli:

| Pencere | Gerçekte nedir | Karar |
|---|---|---|
| 3 — testler | Ajan değil, **süreç**. Geri bildirim yüzeyi. | ✅ Alınıyor (kayıtla, bkz. §5) |
| 4 — sunucu günlükleri | Ajan değil, **süreç**. Geri bildirim yüzeyi. | ✅ Alınıyor |
| 1 — kodu yazan ajan | Zaten var | — |
| 2 — paralel hata ayıklayan **ikinci yazıcı ajan** | Asıl tartışmalı kısım | ❌ **Reddedildi** (§7) |

Yani modelin işe yarayan yarısı ajanla ilgili değil; **kırmızının ne kadar
geç fark edildiğiyle** ilgili.

## 5. KARAR — geri bildirim yüzeyleri, iki pencere

**Karar: 15 Eylül 2026.** Yazan pencere bir tane kalır; yanına **yazmayan**
bir gösterge penceresi açılır. Detay ve komutlar
`00-BURADAN-BASLA.md` §5b'ye işlendi.

⚠ **Ortam gerçeği kararı değiştirdi.** `00-BURADAN-BASLA.md` §7:
*"`dotnet test` sırasında API çalışıyorsa DLL kilidi. Testler `TEST.ps1` ile
koşulur — API'yi önce durdurur."*

Bu yüzden videodaki "testler sürekli açık pencerede koşar" kurgusu bu depoda
**olduğu gibi kurulamaz**: sürekli koşan bir test izleyicisi, geliştirme
kipindeki API'yi sürekli düşürür. Uyarlanmış hâli:

| Yüzey | Nasıl | Sürekli mi |
|---|---|---|
| Günlükler | `docker compose logs -f` (04-kod) | ✅ Evet, sürekli açık |
| Testler | `.\TEST.ps1` (04-kod) | ❌ Hayır — **talep üzerine**, API'yi durdurduğu için |

**Bunun doğurduğu sonuç, penceresinden daha önemli:** testler sürekli
koşamıyorsa, onları koşmayı hatırlaması gereken taraf insan olmamalı.
**Ajan, "bitti" demeden önce `TEST.ps1`'i kendisi koşar ve çıktısını rapor
eder.** Bu, §5'teki güncelleme ritüelinin geliştirme tarafındaki karşılığıdır.

**Not — yeniden karar verilmiyor:** CI zaten kapı (A-4, 14 Eylül'de kapandı).
Bu karar kapı eklemiyor; **kırmızıyı fark etme süresini** kısaltıyor. İkisi
farklı şeylerdir ve biri diğerinin yerine geçmez.

## 6. KARAR — opencode şimdilik kullanılmayacak

`06-ACIK-RISKLER.md` · 📌 Araç kararı bölümündeki *"Şimdilik kullanılmayacak"*
tablosuna satır olarak eklendi. Aynı bölümün ilkesi burada da geçerli:

> *"Her araç bir bakım yüküdür. Kullanılan araç sayısı değil, kapatılan açık
> sayısı ölçülür."*

**Aracın kendisi ciddi** — MIT lisanslı, çok sağlayıcılı, salt-okunur bir
inceleme kipi ve derleyici tanılamalarını modele geri besleyen bir
entegrasyonu var. Sorun araçta değil, **bugün kapattığı açık olmamasında**.

Bugün elde inceletilecek bitmiş bir iş parçası yok: motor yazılmadı, A1–A12
onaylanmadı, fikstürler yazılmadı. İnceleyiciyi inceleyecek şey olmadan
kurmak, ilkeye göre saf bakım yüküdür.

## 7. Neden ikinci **yazıcı** ajan bu projede özellikle riskli

Genel gerekçelerden önce deponun kendi kaydı:

`00-BURADAN-BASLA.md` §5b risk tablosu:

| # | Risk | Önlem | Durum |
|---|---|---|---|
| R5 | İki pencere yazar, sürüklenme | **Tek aktif pencere kuralı** | ✅ kapalı |

**Dört pencereli model R5'i yeniden açar.** Kapalı bir riski yeniden açmak
için bugün hiçbir ölçülmüş gerekçe yok — ve R2 (*"verilmiş karar yeniden
verilir"*) tam olarak bunun için kondu.

§5b'nin *"Aynı anda yalnız bir pencere dosya yazar ve commit eder"* kuralı
zaten aynı şeyi söylüyor. Bugünkü karar o kuralın **ihlali değil, teyididir**.

Üç ek gerekçe (öneri seviyesinde):

1. **Bağlam ikiye bölünür.** Bu projenin bilinen en pahalı sorunu bu —
   Yılmaz'ın itirazı, pencere protokolü ve `00-DEVIR/`'in tamamı bu yüzden
   var. İkinci yazıcı ajan, senkron tutulması gereken ikinci bir bağlam
   demektir.
2. **Darboğaz modelden operatöre kayar.** Mustafa yazılımcı değil (§1);
   inceleme kapasitesi bu projenin en kıt kaynağı. Pencere eklemek onu
   çoğaltmaz, tüketir.
3. **Paralellik N bağımsız iş ister.** Şu an tek bir iş var: motor. Tek işi
   ikiye bölmek hız vermez.

## 8. Aşama 2 — "tadımcı": salt-okunur inceleyici, ölçüm şartıyla

**Ertelenen karar, iptal edilen değil.** Motor işinin ilk parçası (doğrulayıcı,
M-09) yazıldığında yeniden bakılacak. O zamanki kurgu:

- Farklı bir sağlayıcının modeli, **salt-okunur** kipte
- Tek görev: birleştirme öncesi dal farkını incele, **bulgu listesi** çıkar
- **Dosya yazmaz, commit etmez** → R5 açılmaz, §5b'nin yazma hakkı kuralı korunur

**Gerekçesi doğrudan M-09'dan geliyor:**

> *"Çözücüyü ve testini aynı oturum yazarsa, yanlış kural yorumu ikisinde de
> tutarlı biçimde tekrar eder ve test yeşil yanar."*

M-09 bu sorunu **motor için** bağımsız doğrulayıcıyla çözüyor. Tadımcı aynı
ilkenin **doküman ve kod için** karşılığıdır. `DENETIM.py`'nin kendi sınırı da
aynı cümleyle yazılmıştı: *"Betik tutarlılığa bakar, doğruluğa değil. Tutarlı
bir yanlış yine yakalanmaz."* Tadımcının hedeflediği boşluk tam olarak burası.

**Ölçüm şartı — araç kalıcılaşmadan önce:** iki hafta boyunca tadımcının her
incelemede ne bulduğu yazılır. On incelemede kayda değer bulgu yoksa araç
**bırakılır**. Bu şart, §3'teki kanıtsızlığın kapanma yoludur ve
`06-ACIK-RISKLER.md`'deki O-7 kalıbını (*"yanlış alarm veren araç bakılmayan
araca dönüşür"*) engellemek için kondu.

**Yan fayda:** Yılmaz'ın *"AI bloklar arası bağlamı koruyamıyor"* itirazı
bugün tartışma hâlinde. Tadımcı, bulduğu bağlam kopukluklarını sayıya
çevirirse itiraz ölçülebilir hâle gelir.

## 9. Bu oturumda üretilmeyenler — dürüstlük notu

- **Kod değişmedi.** 39/39 durumu aynı, `v0.8-devir` etiketi aynı.
- **Test eklenmedi, koşulmadı.**
- **Yeni devir dosyası açılmadı.** R7 sorusu soruldu (*"bu, var olan bir
  dosyanın bölümü olabilir mi?"*) ve cevabı **evet** çıktı: çalışma biçimi
  kararı §5b'ye, araç kararı `06-ACIK-RISKLER.md`'nin mevcut 📌 Araç kararı
  bölümüne gitti. `00-DEVIR/` kökü **dokuz dosyada kaldı.**
- **2 pencere modeli henüz kurulmadı** — karar verildi, uygulanmadı.

## 10. Sıradaki adım

> **Değişmedi: A1–A12 kabul cümlelerinin onayı.**
> `08-motor-testleri/v2/KABUL-OLCUTLERI.md` §3 (12 senaryo) ve §7 (V-1…V-4).
> Onaya kadar fikstür yazılmaz.
>
> **Bugün eklenen, paralelde açık:**
> - **2 pencere kurulumu** — §5b'deki komutlar, Mustafa'nın makinesinde
>   bir kez yapılacak. Bugün yapılmadı.
> - **`DENETIM.py`'nin commit kontrolü hâlâ hiç koşmadı** (14 Eylül'den
>   devreden madde): `cd C:\Users\PC\Desktop\Tshift` sonra `py DENETIM.py`.
>   **Bu oturum da Mustafa'nın makinesinde kabuk çalıştıramadı** — dosyalar
>   düzenlendi, betik koşulmadı.

## 11. Bu oturumun dersi

14 Eylül'ün dersi *"kaynağın kendisi tutarsız olabilir"* idi. Bunun devamı:
**başka birinin çalışan kurulumu senin kurulumun hakkında kanıt değildir.**

Videodaki model bu depoda olduğu gibi kurulamazdı ve bunu söyleyen şey
muhakeme değil, `00-BURADAN-BASLA.md` §7'deki tek satırdı: *`TEST.ps1` API'yi
durdurur.* Ortam gerçekleri dosyası olmasa, sürekli koşan bir test penceresi
kurulur ve neden API'nin sürekli düştüğü saatlerce aranırdı.

Aynı cümlenin üçüncü kez çıkması: **bir kuralın yazılı olması onu korumaz,
kontrol korur** — ve bu oturumda korunan şey ürün kodu değil, çalışma
biçiminin kendisiydi. R5 kapalıydı; kapalı kalması yazılı olduğu için değil,
tabloya bakıldığı için oldu.
