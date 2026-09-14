# Oturum · 14 Eylül 2026 · altın senaryolar ve devir denetiminin otomatikleşmesi

**Başlangıç:** `v0.8-devir` · 39/39 test yeşil · CI yeşil · motor yok
**Bitiş:** ürün kodu değişmedi · A1–A12 kabul ölçütleri yazıldı (v1 → v2) ·
7 ürün kararı alındı ve sicile geçti · **devir denetimi betiğe çevrildi**

> Bu dosya **append-only**. Yeniden yazılmaz, yalnız eklenir.
> Aynı gün ikinci oturum: birincisi `2026-09-14-veri-analizi.md`.

---

## 1. İş parçası

`00-BURADAN-BASLA.md` §3'teki sıradaki adımın üçüncü maddesi:
*"§16'daki 12 altın senaryoyu (A1–A12) çalıştırılabilir teste çevir."*

Proje kuralı 3 gereği sıra şöyle kuruldu: **önce Türkçe kabul cümleleri ve
somut veri setleri, Mustafa onaylar, sonra fikstür ve test.** Bu oturumda
ilk adım yapıldı; onay bekliyor.

## 2. Okunanlar

`00-BURADAN-BASLA.md`, `02-DEGISMEZLER.md`, `04-TEST-HARITASI.md`,
`06-ACIK-RISKLER.md`, `07-GERCEK-VERI-BULGULARI.md`,
`oturumlar/2026-09-14-veri-analizi.md`, `07-motor/OKU-BENI.md`,
`07-motor/kurallar.json`, spec v1.3 §5, §6, §9.7, §11, §16.

Okunmayanlar: `01-PROJE-KIMLIGI.md`, `03-MIMARI-KARARLAR.md`,
`05-HATA-OTOPSILERI.md` (bu iş parçası için gerekmedi; okuma sırası tablosu
böyle söylüyordu ve doğru söylemiş).

## 3. Üretilenler

| Dosya | Ne |
|---|---|
| `08-motor-testleri/v1/KABUL-OLCUTLERI.md` | İlk taslak: 12 senaryo + 7 açık soru. **Dondurulmuş.** |
| `08-motor-testleri/v2/KABUL-OLCUTLERI.md` | Kararlar işlenmiş hâli. Onay bekliyor. |
| `08-motor-testleri/v2/fikstur/A04.json` | Örnek fikstür — biçim göstermek için |
| `08-motor-testleri/v2/fikstur-denetleyici.py` | Fikstürün girdisi ile beklenen bloğunun kaymadığını kontrol eder |
| `08-motor-testleri/OKU-BENI.md` | Klasör notu: burada ne var, ne yok |
| `00-DEVIR/08-URUN-KARARLARI.md` | **Yeni** — K-serisi ürün kararları sicili |
| `DENETIM.py` | **Yeni** — devir paketi denetimi, depo kökünde |

**Ürün kodu değişmedi.** 39/39 durumu aynı.

## 4. Alınan kararlar — K-1…K-7

Tamamı `08-URUN-KARARLARI.md`'de gerekçeleriyle. Özet:

| # | Karar |
|---|---|
| K-1 | Sınır değerler **ihlal** (tam 11 saat dinlenme, tam 9 saat günlük); ama `sinir_dahil` parametresiyle firma ayarı |
| K-2 | Saat dilimi sabit ofsetle gelirse girdi **reddedilir** |
| K-3 | Çözücü istatistikleri çıktıya girer, müşteriye gösterilir |
| K-4 | Mola hakkı İş Kanunu'na göre, **brüt** süreden (uzman teyidi bekliyor) |
| K-5 | Geçmişi olmayan kiracıda motor çalışır |
| K-6 | Sonbahar DST kontrolü ileri tura |
| K-7 | Çözümsüzlük teşhisine **hafta seviyesi** eklenir |

K-1'in bedeli bilerek kabul edildi: `GUNLUK_AZAMI: 9` fiilen "en çok 8:59"
demek oluyor. Karşılığı kural ekranında cümlenin açık yazılması.

K-7 doğrudan yeni bir test doğurdu: A9(c). 10 kişilik kadroda her gün 9 kişi
isteyen talep — hiçbir hücre tek başına imkânsız değil, ama hafta toplamı
63 > 60. Motor bunu görmezse birine yedi gün çalıştıran plan üretir.

## 5. Şartnamede bulunan sekiz tutarsızlık

v1.3'e **dokunulmadı**; hepsi v1.4'e taşınacak. Liste
`08-motor-testleri/v2/KABUL-OLCUTLERI.md` §4'te (T-1…T-8). En belirginleri:
§16.2 "on senaryo" diyor ama tablo 12 satır; A9 ile §11.3 çelişiyor;
§11.2 örneğinde mola 30 dk, §6.2 tablosuna göre 60 olmalı.

**Not:** Bugünkü tutarsızlıkların hiçbiri devir paketinde değildi,
**şartnamenin kendi içindeydi.** Devir paketi kendini denetliyor; şartnameyi
denetleyen bir mekanizma yok. §16 altın senaryoları tam olarak o boşluğu
kapatan şey.

## 6. Claude'un kendi hatası — v1'de brüt/net karışması

v1'de A4'ün 4. maddesi günlük azamiyi **brüt** süre üzerinden yazmıştı.
§6.2 `GUNLUK_AZAMI` için *"azami **net** süre"* diyor. v2'de düzeltildi ve
sınırı gerçekten sınamak için yeni bir vaka eklendi: 10 saat brüt, 60 dk mola,
**tam 9 saat net**.

Yakalanma biçimi kayda değer: hata, hesapları elle değil **programatik**
doğrulayınca çıktı. Elle okunsa "9 ≤ 9, sınır, tamam" diye geçilirdi.

## 7. Devir paketinin değerlendirmesi — Mustafa'nın sorusu

Mustafa sordu: *"Verdiğim devir dokümanı projeyi devam ettirebilmek için
yeterli mi?"*

**Cevap: evet, ve bugünün kendisi kanıtı** — tek bir "bu proje ne, nerede
kalmıştık" sorusu sorulmadan işe başlandı.

**En çok işe yarayan şey şartname içeriği değildi, hata otopsileri ve
reddedilen öneriler kaydıydı.** `07-motor/` yanlış isimlendirme hikâyesi yeni
klasörün dikkatle adlandırılmasını ve denetleyicinin başına "bu ne değildir"
uyarısı konmasını sağladı. "Yazdım ≠ gönderdim" kuralı dosyaların boyutunun
geri okunmasını sağladı. "Kırmızı kanıt" kuralı fikstürün bilerek bozulup
denetleyicinin yakaladığının gösterilmesini sağladı. Bunların hiçbiri
söylenmedi; doküman söyledi.

**Bulunan yapısal zayıflık:** Paket kendi ilkesini kendine uygulamıyordu.
§5b *"asıl güvence testlerdir, doküman değil"* diyor, ama `00-DEVIR/`'in
tamamı düz yazıydı ve tek denetim yöntemi elle okumaktı. 14 Eylül
denetiminde bulunan dört sorunun (D-1…D-4) **dördü de** betikle
yakalanabilirdi.

## 8. DENETIM.py — ve ilk koşuda bulduğu gerçek hatalar

Yedi kontrol: test adları, test sayısı, dosya yolları, değişmez özet tablosu,
günlük adlandırması, değişim günlüğü tazeliği, commit durumu. Artı R7 uyarısı.

**Tasarım kararı:** `oturumlar/` ve `DEGISIM-GUNLUGU.md` **tarihsel** dosya
sayılır. İçlerindeki sayılar o günün doğrusudur, bugünküyle karşılaştırılmaz;
oradaki test adı sorunları HATA değil UYARI üretir — çünkü bu dosyalar tanım
gereği yeniden yazılmaz.

**İlk koşuda bulunanlar (hepsi gerçek, hiçbiri elle fark edilmemişti):**

| Bulgu | Nerede | Durum |
|---|---|---|
| `0 - Baglanan rol super kullanici degil` — başındaki **M eksik** | `01-PROJE-KIMLIGI.md`, `06-ACIK-RISKLER.md`, `RISKLER-VE-ONLEMLER.md` | ✅ düzeltildi |
| `H1 - Jetonla /me calisir` — kısaltılmış | `RISKLER-VE-ONLEMLER.md` | ✅ düzeltildi |
| `M0 - ...` — kısaltılmış (parantezli son ek düşmüş) | `RISKLER-VE-ONLEMLER.md` | ✅ düzeltildi |
| Özet tablosu **45/41** diyor, satırlar **47/39** veriyor | `02-DEGISMEZLER.md` | ✅ düzeltildi |
| `DEGISIM-GUNLUGU.md` 13–14 Eylül'ü hiç yazmamış | depo kökü | ✅ geriye dönük eklendi |
| `oturumlar/2026-09-12.md` — silinmiş dosyaya atıf | 14 Eylül günlüğü | ⏳ dokunulmadı |

Sonuncusu bilerek bırakıldı: o atıf **tarihsel bir günlükte** ve dosyanın adının
o gün değiştirildiğini anlatıyor. Append-only dosya yeniden yazılmaz. Betik
buna göre düzeltildi — tarihsel dosyalardaki yol ve ad sorunları **UYARI**
üretiyor, HATA değil.

**Değişmez tablosu hatası kayda değer:** Y-13 ve Y-14, 12 Eylül'de satır olarak
eklenmiş ama özet güncellenmemişti. Tablo üç elle denetimden geçti ve
hiçbirinde yakalanmadı. Düzeltilirken bir kural da netleşti: **⏳ satırları
toplama girer, bekçiliye girmez** — karar verilmiş ama uygulanmamış bir
değişmez korunuyor sayılmaz.

**D-3, 14 Eylül'ün ilk oturumunda iki yerde düzeltilmişti — üçüncü yer gözden
kaçmıştı.** Elle denetimin sınırı tam olarak bu: aynı hatayı ikinci kez
ararken yorulursun.

**Kırmızı kanıt:** Betik, yazıldıktan sonra kasten bozulmuş bir fikstürle ve
gerçek devir paketiyle koşuldu; ikisinde de beklenen hataları buldu ve
çıkış kodu 1 döndürdü.

⚠ **Bu oturumda koşulamayan tek kontrol: commit durumu.** Bu pencerede
Mustafa'nın makinesinde kabuk çalıştırılamadı (Windows tarafında bir mount
sorunu). `git status` kontrolü **ilk kez Mustafa koşacak.**

## 9. Pencere protokolüne eklenen madde — açılış beyanı

Devir risk tablosu R-satırında *"Doküman yanlış başlarsa yakalamaz"* diye bir
açık vardı ve kapalı değildi. Kapatma yolu ucuz çıktı: yeni pencere **iş
yapmadan önce** hangi dosyaları okuduğunu ve sıradaki adımı kendi cümleleriyle
söyler.

Bu oturumda kendiliğinden yapıldı ve işe yaradı — Mustafa, spec §16'daki
çelişki uyarısını daha ilk mesajda gördü. Protokol adımı hâline getirildi
(`00-BURADAN-BASLA.md` §5b).

## 10. Sıradaki adım

> **A1–A12 kabul cümlelerinin onayı.** `08-motor-testleri/v2/KABUL-OLCUTLERI.md`
> §3'teki 12 senaryo ve §7'deki dört varsayım (V-1…V-4) Mustafa tarafından
> okunacak. Onaydan sonra kalan 11 fikstür ve pytest iskeleti yazılır.
>
> **Paralelde açık:**
> - **`git status` kontrolü hiç koşmadı** — ilk kez Mustafa koşacak.
> - **K-4 uzman teyidi bekliyor** (İş Kanunu md. 68 mola yorumu).
> - **Spec v1.4 yazılmadı:** sekiz tutarsızlık (T-1…T-8) ve yedi karar
>   (K-1…K-7) v1.3'e işlenmedi.
> - **R7 eşiği:** `00-DEVIR/` dokuz dosyada. Onuncudan önce sadeleştirme.

## 11. Bu oturumun dersi

Önceki iki oturumun dersi *"kaynağı okumadan konuşma"* idi. Bunun devamı
çıktı: **kaynağı okumak da yetmiyor, kaynağın kendisi tutarsız olabilir.**

Devir paketi kendini denetliyordu, şartname denetlenmiyordu. Aynı sınıftan
bir boşluk daha vardı: paketin denetimi elle yapılıyordu. İkisi de aynı
cümleyle kapanıyor — *bir kuralın yazılı olması onu korumaz, kontrol korur* —
ve bu cümle bugüne kadar yalnız ürün koduna uygulanmıştı.
