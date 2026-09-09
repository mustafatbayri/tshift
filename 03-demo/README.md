# Demolar

Kodlamadan önce akışı ve ekranları doğrulamak için yapılan tıklanabilir prototipler.
Demo kodu ürün kodu değildir; akış onaylandıktan sonra atılır.

## Versiyonlar

| Versiyon | Tarih | Teknoloji | Durum |
|---|---|---|---|
| `v2-html/tshift-demo-v2.html` | 9 Eylül 2026 | Tek dosya HTML | **Güncel** — 25 ekran, spec v1.1'e göre |
| v1-nextjs | Eylül 2026 | Next.js + Tailwind | Geçersiz. Plan editörü ve karşılaştırma ekranı yetersiz bulundu |

## v2 nasıl açılır

`v2-html/tshift-demo-v2.html` dosyasına **çift tıklayın.** Kurulum yok, npm yok,
sunucu yok. Telefona da atabilirsiniz, orada da açılır.

## v2'de ne var

**Veri:** Anadolu Çağrı Merkezi kurgusu — 214 çalışan, 3 ekip, 5 vardiya şablonu,
4 yetkinlik, gerçekçi saatlik çağrı talebi, 32 izin kaydı, geçen haftanın
gerçekleşen verisi. Üç plan adayı gerçekten üretiliyor (basit bir yerleştirici ile),
metrikleri hesaplanıyor.

**25 ekran.** Kullanıcı notlarından gelen her madde karşılandı:

- Plan karşılaştırma: 3 kart + gün gün / çalışan bazlı / saatlik ısı haritası / **farklar** sekmeleri
- Plan editörü: **hafta / gün / liste** görünümleri, katlanabilir üst şerit ve iki yan panel
- Asistan: açık nokta önerileri, her birinde **Uygula**, uygulananlar **geri alınabilir**
- Düzenleme geçmişi: oturumdaki her işlem, tek tek geri alma
- **İzin etki analizi**: her izin satırında rozet, "Etkileri gör" ile saat saat kapsama düşüşü ve aday listesi
- Metrik açıklama bileşeni: her sayının yanında `?`, tek kaynaktan açıklama
- Geçmiş planlar takvimi, çalışan takvimi (salt-okunur), plan realizasyon raporu, haftalık takip
- Her "yeni kayıt" butonu gerçek modalini gerçek alanlarla açıyor

**Rol değiştirme:** sol altta ⇄ düğmesi — müdür / takım lideri / çalışan arasında geçiş.

## v2'de kasten yapılmayanlar

- Sürükle-bırak yok (gerçek üründe olacak; prototipte tıklama yeterli)
- Veri kalıcı değil — sayfayı yenileyince başa döner
- Arama ve filtreler yalnız çalışan listesinde gerçekten çalışıyor
- Grafikler gerçek veriden üretiliyor ama etkileşimli değil
