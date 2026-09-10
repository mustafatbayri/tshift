using TShift.Domain.Calisanlar;
using TShift.Domain.Yetki;

namespace TShift.Infrastructure.Yetki;

/// <summary>
/// Sorgulara kapsam sınırı uygular.
///
/// Bu, satır seviyesi güvenliğin ÜSTÜNE gelen ÜÇÜNCÜ bir daraltmadır ve onun
/// yerine geçmez. Sıralama şöyle:
///   1. RLS          → başka FİRMANIN satırı hiç gelmez (veritabanı garantisi)
///   2. Sorgu filtresi → aynı şeyin uygulama katmanındaki kopyası
///   3. Kapsam        → aynı firma içinde, kullanıcının göremeyeceği satırlar
///
/// Üçüncüsü bir GÜVENLİK sınırı değil, bir YETKİ sınırıdır: şef ile müdür aynı
/// firmadadır, veritabanı ikisini de meşru görür. Ayrımı uygulama yapar.
/// Bu yüzden burada yapılan hata, RLS hatası kadar felaket değil ama yine de
/// müşterinin "şefim herkesin maaşını gördü" diye arayacağı türden.
/// </summary>
public static class KapsamFiltresi
{
    public static IQueryable<Calisan> KapsamUygula(this IQueryable<Calisan> q, KullaniciYetkisi y)
        => y.Seviye switch
        {
            KapsamSeviyesi.Kiraci => q,

            // DİKKAT — SPEC'TEN BİLİNÇLİ SAPMA (spec §3.2 son notu).
            //
            // Spec: "Kapsamı olmayan kullanıcı tüm kiracıyı görür."
            // Burada: kapsam seviyesi Kapsam olup HİÇ kapsam satırı olmayan
            // kullanıcı HİÇBİR ŞEY görmez.
            //
            // Gerekçe: kapsamı unutulmuş bir departman müdürü, spec'in yazdığı
            // gibi davranırsak sessizce tüm firmayı görür. Bu, bir yapılandırma
            // eksikliğinin yetki genişlemesine dönüşmesidir — güvenlikte en
            // istenmeyen davranış. "Kapsamı yoksa her şeyi görür" kuralı yalnız
            // kiracı yöneticisi için doğrudur, ve o zaten Kiraci seviyesinde
            // olduğu için yukarıdaki dalda karşılanıyor.
            //
            // Sonuç: eksik yapılandırma "göremiyorum" diye şikâyete yol açar,
            // "her şeyi gördüm" diye sızıntıya değil.
            KapsamSeviyesi.Kapsam => q.Where(c =>
                y.DepartmanIds.Contains(c.DepartmanId) ||
                (c.BirincilEkipId != null && y.EkipIds.Contains(c.BirincilEkipId.Value))),

            // Kendi kaydı. Kullanıcı bir çalışana bağlı değilse hiçbir şey görmez.
            KapsamSeviyesi.Kendi => q.Where(c => y.CalisanId != null && c.Id == y.CalisanId),

            _ => q.Where(c => false)
        };
}
