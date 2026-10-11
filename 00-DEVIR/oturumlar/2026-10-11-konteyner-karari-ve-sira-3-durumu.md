# 11 Ekim 2026 — Yılmaz görüşmesinin sonucu: konteyner mimarisi kararı (M-16); sıra 3'ün durumu

**Pencere:** 11 Ekim 18:25 – · **Önceki:** `2026-10-07-gece-kosusu-ve-fm-siz-arama-kuyrugu.md`
§9 (K-61 kapanışı, sıra 3'ün ilk sorusu, literatür okuması). **Bu pencerede
kod değişmedi.**

## İçindekiler

1. [Mustafa'nın haberi ve M-16](#1--mustafanın-haberi-ve-m-16)
2. [Nerede kaldık](#2--nerede-kaldık)
3. [Sıradaki adım](#3--sıradaki-adım)

## 1 · Mustafa'nın haberi ve M-16

Mustafa (18:25): *"Yılmaz ile görüşmemiz sonucunda, tek database multitenant
id yerine, her müşteri için konteyner mimarisine geçme kararı aldık. Bunu
bir söyleyeyim, diğer konularla ilgili yorumlarını bana iletecek. Biz şimdilik
motoru yazmaya ve test etmeye devam edeceğiz."*

Kayıt: `03-MIMARI-KARARLAR.md` **M-16** — M-01'in (tek DB + `tenant_id` +
RLS) yerine her müşteri için ayrı konteyner; karar verildi, **tanımı açık,
uygulanmadı**; neye dokunduğu sayıldı (şartname §7.3/§8.1, değişmezler
K-1…K-9'un kanıt yöntemi, 45 kimlik testinin RLS'e dayananları,
`04-kod/db/rls/`, M-02/M-13/M-14; motor M-09 **değişmez** — motor kiracıyı
zaten bilmiyor) ve koda inmeden cevaplanacak yedi soru yazıldı (konteynerin
sınırı, kimlik/yönlendirme, sürüm dağıtımı, motor havuzu mu konteyner başına
mı, RLS'in kaderi, maliyet/ölçek, yedek/silme). Bugün neden ucuz: henüz
müşteri verisi yok — M-01'in *"tüm veri taşınır"* bedeli bugün kod + test +
belge. M-01 satırına uyarı, özet tablosuna M-16 satırı. Depo, testler ve
DENETIM bilerek M-01'i kanıtlamaya devam ediyor; tanım gelmeden sökülmez.

## 2 · Nerede kaldık

Depo temiz: `bc51d6a` push edildi (`main` = `origin/main`); 610 + 41 test,
DENETIM 0 HATA, tam mutasyon **327 hepsi öldü** (damga 8 Ekim 05:39). K-61
kapalı (varsayılan 3 deneme). Sıra 3 (dört yumuşak kural) 8 Ekim'de başladı:
`VARDIYA_ROTASYON_YONU` için literatür okuması ve tanım taslağı hazır
(`02-spec/v1.4-hazirlik/03-vardiya-rotasyon-yonu-literatur.md`, keşif
`08-motor-testleri/gercekci-veri-seti/kesif/2026-10-08-rotasyon-yonu/`).
Mustafa 1 ve 2'yi kabul etti; **bekleyen iki karar onda:** başlangıç farkı
dairesel okunsun mu (sabah→gece atlaması geri sayılsın — literatür öyle),
ceza birimi saat mı adet mi (öneri saat). 9 Ekim 00:55'te istediği *"okunur
çizelge"* (kişi × gün tablosu) yarım kaldı — görüşme geçti, hâlâ gerekli mi
soruldu.

## 3 · Sıradaki adım

(1) İki rotasyon kararı → şartname (K-65) + motor terimi + bağımsız
doğrulayıcı + testler + mutasyonlar + bağımsız inceleme + 500 kişide
önce/sonra ölçüm; (2) `TERCIH_KARSILAMA` tanım sorusu (hazır); (3)
`PLAN_KARARLILIGI`, (4) `EKIP_SUREKLILIGI` (son ikisi ancak veri seti v2'de
ölçülür); sonra veri seti v2 (K-62), merdiven, K-64; bulgu 26 (karar
Mustafa'da), bulgu 27 (sırada). Mimari (M-16) Yılmaz'ın yorumları gelince.
