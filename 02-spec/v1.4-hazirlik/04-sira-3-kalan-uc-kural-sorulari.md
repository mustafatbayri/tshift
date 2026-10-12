# Sıra 3'ün kalan üç yumuşak kuralı — tanım soruları (taslak, Mustafa'ya henüz sorulmadı)

**Durum:** ⏳ taslak · **Yazıldı:** 11 Ekim 2026 (K-65 öncesi, bulut taslağı); 12 Ekim 16:00'da depoya alındı, pencere kapanırken.
**Bağlam:** 7 Ekim 18:31'de onaylanan sıra — (3) dört yumuşak kural: `EKIP_SUREKLILIGI`, `PLAN_KARARLILIGI`, `TERCIH_KARSILAMA`, `VARDIYA_ROTASYON_YONU` (K-65 ile kapandı) — tanım soruları **tek tek** sorulur, cevap literatür/ölçümle temellendirilir. 12 Ekim'den sonra sıra: D kodu → K-62 seviye 1 + K-67 → taban ölçümü → bu üç soru (`PLAN_KARARLILIGI` ve `EKIP_SUREKLILIGI` ancak seviye 1 setinde ölçülebilir: `mevcut_plan` ve çok ekipli kişiler orada).
**Sayılar:** S30-95 setinden (11 Ekim); seviye 1 seti kurulunca yeniden sayılır.

## İçindekiler

1. [Soru 2 · `TERCIH_KARSILAMA`](#soru-2--tercih_karsilama)
2. [Soru 3 · `PLAN_KARARLILIGI`](#soru-3--plan_kararliligi)
3. [Soru 4 · `EKIP_SUREKLILIGI`](#soru-4--ekip_surekliligi)

---

## Soru 2 · `TERCIH_KARSILAMA`

şartname §6.8: *"Part-time çalışanların sözleşmeden gelen uygunluk esnekliğinin kullanım oranı"*, altında *"yüksek ağırlıkta motor part-time çalışanı kendi uygun olduğu saatlerin merkezine yerleştirmeye çalışır"*; ağırlık 3/1/9. K-13 (15 Eylül): çalışan tercih belirtemez, part-time'ın uygunluğu sözleşmeden gelir ve **serttir** (`UYGUNLUK_TAKVIMI`); K-22 (16 Eylül): anlam değişti, ad kaldı. Ölçülebilir bir tanım hiç yazılmadı.

Elde ne var: 500 kişilik sette 130 yarı zamanlı; 85'inin uygunluk kaydı var ve hepsi **tam gün** kapalı günler (2 uygun gün: 18 kişi · 3 gün: 47 · 4 gün: 20 · kısıtsız: 45). K-58: yarı zamanlı baz 30 saat, 45'e kadar ek mesai. Küçük ölçek keşfi (100 kişi): yarı zamanlılar ort. 20 saat / 3,1 gün alıyor; uygun günlerinin %67–75'i kullanılıyor; 33'ün 2'si hiç planlanmamış.

Kuralın neyi ölçeceğini seçmen lazım:

- **(A) Uygun günlerin kullanım oranı:** kullanılan uygun gün / uygun gün sayısı (3 uygun gününden 2'si kullanıldı = %67). Ceza: kullanılmayan uygun gün × ağırlık. *Anlamı:* part-time'ı işe aldığımız günlerde onu kullan — boş bırakıp tam zamanlıya yüklenme.
- **(B) Sözleşme bazının doldurulması:** planlanan saat / 30 saat (tam zamanlının `SAAT_DENGESI`'nin yumuşak, yarı zamanlı karşılığı). Ceza: 30'un altındaki saat × ağırlık.
- **(C) Pencerenin ortası:** vardiya, kişinin uygun saat penceresinin kenarına değil ortasına (şartnamedeki cümle). Bugünkü veride pencereler tam gün olduğu için **hiç etkisi olmaz**; saatli pencere (öğrenci 16:00'dan sonra) gelirse anlam kazanır.
- **(D) Başka:** senin tarif edeceğin bir şey.

Önerim yok — bu bir ürün anlamı sorusu; (A) ile (B) farklı davranır: (A) günleri yayar, (B) saati doldurur. Hangisi "sözleşmeden gelen esnekliğin kullanımı"dır?

---
## Soru 3 · `PLAN_KARARLILIGI`

şartname §6.5: *"Yeniden planlamada mevcut atamalar korunsun. Ölçüm: değişimin %91'i önlendi"*, ağırlık 6/6/6 (üç profilde aynı — en yüksek dört kural içinde), kapsam K. Girdi: `mevcut_plan` (K-54: yayınlanmış plan; donmuş günler gerçek, öteki günler başlangıç ipucu — *"iyileştir, zar atma"*). Bugün ipucu var ama **bedeli yok**: motor ipucudan uzaklaşınca puan düşmüyor. Fikstürde `mevcut_plan` yok → ancak veri seti v2'de ölçülür.

Kararlar: (1) "değişim" birimi — **kişi-gün** (aynı günde şablon/saat/ekip farklıysa, vardiya kaldırıldıysa ya da boş güne vardiya eklendiyse 1) mi, **saat** (değişen saat kadar) mı? Önerim kişi-gün: çalışan için "planım değişti" ikili bir olaydır. (2) Yalnız mola yeri değişmişse değişim **sayılmaz** (mola adımı planı değil — öneri). (3) Eklenen vardiya (boş günü dolduran) sayılır mı? Önerim evet (çalışanın serbest günü gitti). (4) Donmuş günler zaten sabit — kıyas dışı. (5) Çıktı: `metrikler.plan_degisikligi {korunan, degisen, kaldirilan, eklenen}` + doğrulayıcı satırları.

---
## Soru 4 · `EKIP_SUREKLILIGI`

şartname §6.5: *"Aynı kişiler mümkün olduğunca aynı ekiple çalışsın"*, ağırlık 2/1/4, kapsam K,D. K-50: çok ekipli çalışan bütün ekiplerine sayılır; atamanın `ekip`i şablonun ekibidir; `calisanlar[].ekipler` sıralı (ilki birincil; `employee_teams.oncelik`). Fikstürde herkes tek ekipte → **bugün etkisiz**; K-62 setinde çok ekipli kişiler gelecek (satış + backoffice örneği).

Hangi süreklilik? (a) **Kişi kendi (birincil) ekibinde kalsın:** başka ekibin şablonuna her atama 1 × ağırlık — "ödünç" kişiyi ancak gerekince kullan. (b) **Hafta içinde ekip değiştirmesin:** art arda çalışma günlerinde ekip farklıysa 1 × ağırlık (geçiş sayısı). (c) **Aynı insanlar birlikte çalışsın** (ekip = beraber vardiya tutan grup): kişi çiftleri üzerinden, 500 kişide pahalı ve tanımı belirsiz. (d) Başka. Önerim (a): K-50'nin diliyle uyumlu, doğrusal ve ucuz; (b) ek olarak düşünülebilir.
