# Altın senaryo test iskeleti — OKU-BENİ

**Klasör:** `08-motor-testleri/v5/testler/`
**Ne zaman yazıldı:** 16 Eylül 2026
**Durum:** İskelet hazır, **bilerek kırmızı**. Motor yazılmadı.

---

## 1. Bu klasör ne?

`KABUL-OLCUTLERI.md` içinde onayladığın on iki altın senaryonun **çalıştırılabilir** hâli.

Zincir şöyle:

```
KABUL-OLCUTLERI.md   ← senin onayladığın cümleler (İŞ DİLİ)
        ↓
fikstur/A0X.json     ← aynı cümlelerin veri hâli (SAYILAR)
        ↓
testler/             ← burası: fikstürü okur, motoru çağırır, sonucu sınar
        ↓
motor                ← henüz yok
```

Her katman bir öncekine dosya yoluyla bağlı. Fikstürdeki `kabul_olcutu` alanı
kabul ölçütündeki başlığı gösterir; test fikstürü adıyla bulur. Yani bir
senaryoyu değiştirmek istersen tek yerden değiştirip zincirin tamamını
denetleyebilirsin (`fikstur-denetleyici.py` bu bağı kontrol eder).

---

## 2. Şu an ne oluyor? (Kırmızı normal)

```
py -m pytest -q
→ 7 failed, 3 passed, 4 skipped
```

| Sonuç | Kaç | Ne demek |
|---|---|---|
| 🔴 failed | 7 | A1, A3, A4, A6, A7, A8, A9 — **motor yok**, çağrı yapılamıyor |
| 🟢 passed | 3 | Paketin kendi sağlık kontrolü — motorsuz da geçmeli |
| ⏭ skipped | 4 | A2, A10, A11, A12 — backend senaryosu, burada koşmaz |

**Kırmızı olması istenen durumdur.** Master Spec §16.4 "kırmızı kanıt" kuralı:
bir test önce kırmızı yanmadan yeşile dönemez. Önce kırmızı yanmayan test,
aslında hiçbir şeyi sınamıyor olabilir — ve bunu asla anlayamayız.

Hata mesajı da bunu açıkça söylüyor:

```
MOTOR YAZILMADI.
  Bu test, motor var oldugunda yesile donecek sekilde yazildi.
  Kirmizi olmasi BEKLENEN durumdur (spec #16.4 kirmizi kanit).
  Motor hazir oldugunda: set TSHIFT_MOTOR_URL=http://localhost:8000
```

### ⚠ Bu paket CI'da koşmuyor — bilerek

CI şu an yalnız `dotnet test` çalıştırıyor (A-4 kapısı, 14 Eylül).
Kırmızı bir paketi şimdi CI kapısına bağlamak **"main her zaman yeşil"**
kuralını bozardı ve kapı sürekli kırmızı yanardı. Motor var olduğunda
CI'a eklenecek — bu, A-15 listesindeki işlerden biri.

---

## 3. Nasıl koşturulur?

```powershell
# Bir kereliğine:
py -m pip install pytest

# Her seferinde:
cd C:\Users\PC\Desktop\Tshift\08-motor-testleri\v5\testler
py -m pytest -v
```

Tek bir senaryoyu koşturmak:

```powershell
py -m pytest -v -k A04
```

Yalnız sağlıklı olanları (motor gerekmeyenleri) koşturmak:

```powershell
py -m pytest -v -k "yukleniyor or govdesi or acikca"
```

---

## 4. Dosyalar

| Dosya | Ne yapar | Motor gelince değişir mi? |
|---|---|---|
| `test_altin_senaryolar.py` | Testlerin kendisi. Fikstürü okur, motoru çağırır, `beklenen` bloğunu sınar. | Hayır |
| `motor_istemci.py` | Motorla **tek temas noktası**. `/solve`, `/evaluate`, `/health`. | **Evet — yalnız bu** |
| `kontroller.py` | Fikstürdeki `degismezler` listesinde geçen kontrol adlarının gövdesi. | Hayır |
| `conftest.py` | pytest ortak ayarları, fikstür klasörü, karşılaştırma sözdizimi. | Hayır |
| `backend-taslak/` | A2, A10, A11, A12 için C# taslakları. Derlenmiyor. | Ayrı yol — bkz. o klasörün OKU-BENİ'si |

`fikstur_yukleyici.py` bir üst klasörde (`../`) duruyor; hem testler hem
`fikstur-denetleyici.py` aynı birleştirme mantığını kullansın diye oraya
konuldu. İki yerde iki farklı `fark` yorumu olsaydı, denetleyici "tamam" derken
test başka bir şey sınıyor olurdu.

---

## 5. Motor yazıldığında ne değişecek?

**Tek dosya:** `motor_istemci.py` içindeki `_cagir` metodu.

Şu an her çağrı `MotorYok` fırlatıyor. Orası gerçek bir HTTP isteğine
dönüştüğünde:

- 7 kırmızı test motorun verdiği cevaba göre yeşile veya **anlamlı** kırmızıya döner
- Fikstürlerin, kabul ölçütünün, kontrollerin tek satırı değişmez

Temas noktasını tek tutmanın sebebi bu. Motor Python + OR-Tools olarak ayrı bir
servis (M-09); testler onun içini bilmez, yalnız sözleşmesini (§11.1) bilir.

Adres ortam değişkeninden okunur:

```powershell
set TSHIFT_MOTOR_URL=http://localhost:8000
```

---

## 6. Üç test tipi

Fikstürlerdeki `tip` alanı testin nereye gideceğini belirler.

**`solve`** — motor sıfırdan plan üretir (A1, A3, A6, A7, A9).
Test, çıkan planın `beklenen` bloğundaki koşulları sağlayıp sağlamadığına bakar:
durum (`COZULDU` / `COZULEMEDI`), metrikler, ve `degismezler` listesi.

**`evaluate`** — plan elle verilir, motor denetler (A4, A8).
Test, motorun **doğru ihlalleri bulup bulmadığına** bakar. Buradaki beklenen
ihlal sayıları `fikstur-denetleyici.py` tarafından fikstürdeki atamalardan
bağımsız olarak yeniden hesaplanıyor — yani "2 sert ihlal" iddiası elle
yazılmış bir sayı değil, denetlenmiş bir sayı.

**`backend`** — motor değil, .NET tarafı sınanır (A2, A10, A11, A12).
Burada `skip` edilir, taslakları `backend-taslak/` altında.

---

## 7. `degismezler` nedir, `kontroller.py` neden var?

Fikstür bir **veridir**. Şu cümleyi taşıyabilir:

```json
{ "ad": "C08 hicbir Sali calismaz",
  "kontrol": "calisan_gun_atamasi_yok",
  "calisan": "C08", "gun": 1 }
```

Ama bu kontrolün **nasıl** yapılacağını bilmez. Gövdesi `kontroller.py`
içinde duruyor. Yeni bir değişmez eklemek = fikstüre bir satır + `kontroller.py`'ye
bir fonksiyon.

`test_her_kontrol_adinin_govdesi_var` testi, fikstürde geçen her kontrol adının
gövdesinin gerçekten var olduğunu sınıyor — bu test motorsuz da koşuyor ve
yeşil. Yani fikstüre yazım hatasıyla olmayan bir kontrol adı yazarsan, motoru
beklemeden anında yakalanır.

### Bu ne DEĞİLDİR

`kontroller.py` **ürünün doğrulayıcısı değildir**. Master Spec §16.1 bağımsız
doğrulayıcının çözücüyle hiçbir mantık paylaşmamasını şart koşuyor. Buradaki
kontroller kaba, dar ve testin yardımcısı; ürünün ihlal listesini yeniden
üretmezler.

---

## 8. Karşılaştırma sözdizimi

Fikstürdeki `beklenen` bloğunda sayılar üç şekilde yazılabiliyor:

```json
"kapsama_yuzde":      { "en_az": 95 }
"sert_ihlal_sayisi":  { "esit": 0 }
"fazla_mesai_saat":   { "en_fazla": 10 }
```

`_` ile başlayan anahtarlar yorumdur, sınanmaz. Bu, fikstürün içine "neden bu
sayı" açıklaması yazabilmek için var.

---

## 9. Bilinen boşluklar (dürüstlük notu)

| Boşluk | Ne zaman kapanır |
|---|---|
| A7'nin iki profil karşılaştırması sınanmıyor — `_karsilastirmalar` şimdilik "motor yok" diyor | Motor yazılınca |
| `olmamasi_gerekenler` blokları sınanmıyor, yalnız listeleniyor | Motor yazılınca |
| `evaluate_ile_dogrula` gibi ikinci çağrı gerektiren kontroller `None` dönüyor | Motor yazılınca |
| A5 hiç yok | K-12: yaz saati ertelendi, Türkiye'de müşteri yok |

Bunlar **gizlenmiş eksik değil**; testler koştuğunda mesajlarında açıkça
söylüyorlar. Yeşile dönmüş ama aslında hiçbir şey sınamayan bir test,
kırmızı bir testten daha tehlikelidir.

---

## 10. İlgili dosyalar

- `../KABUL-OLCUTLERI.md` — senin onayladığın senaryolar
- `../fikstur/OKU-BENI.md` — fikstür formatı
- `../fikstur-denetleyici.py` — fikstürleri denetler (6 kontrol)
- `../../../DENETIM.py` — belge/kod tutarlılığını denetler (8 kontrol)
- `00-DEVIR/04-TEST-HARITASI.md` — testlerin tam haritası
- `00-DEVIR/08-URUN-KARARLARI.md` — K-1…K-17 kararları
