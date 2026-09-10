using Microsoft.EntityFrameworkCore;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Persistence;

namespace TShift.Infrastructure.Yetki;

/// <summary>
/// Bir kullanıcının o an sahip olduğu izinler ve görebildiği alan.
/// "Neyi yapabilir" (Izinler) ile "nerede yapabilir" (Seviye + kapsam) ayrı.
/// </summary>
public sealed record KullaniciYetkisi(
    Guid KullaniciId,
    IReadOnlySet<string> Izinler,
    KapsamSeviyesi Seviye,
    IReadOnlyList<Guid> DepartmanIds,
    IReadOnlyList<Guid> EkipIds,
    Guid? CalisanId)
{
    public bool Var(string izin) => Izinler.Contains(izin);

    /// <summary>Hiçbir rolü olmayan kullanıcı. Hiçbir şey yapamaz, hiçbir şey göremez.</summary>
    public static KullaniciYetkisi Bos(Guid kullaniciId) =>
        new(kullaniciId, new HashSet<string>(), KapsamSeviyesi.Kendi, [], [], null);
}

public interface IYetkiCozucu
{
    Task<KullaniciYetkisi> CozAsync(Guid kullaniciId, CancellationToken ct = default);
}

/// <summary>
/// Kullanıcının etkin yetkisini hesaplar.
///
/// Birden fazla rolü olabilir; izinler BİRLEŞTİRİLİR, kapsam seviyesi ise
/// EN GENİŞİ alınır. Örnek: hem "şef" hem geçici "departman müdürü" olan biri,
/// devir süresince departman genelinde iş yapar; süre dolunca kendiliğinden
/// şefliğe döner çünkü müdür satırı artık geçerli değildir.
///
/// Süreli devir tarihe göre çözülür (spec §3.2). Bugünün tarihi kiracının saat
/// diliminde değil, UTC'de değerlendirilir — sistem geneli UTC saklar; bu
/// karar bir günün sınırında en fazla saatlik bir kayma yaratır ve yetki
/// devrinde bu kabul edilebilir.
/// </summary>
public sealed class YetkiCozucu(TShiftDbContext db, TimeProvider saat) : IYetkiCozucu
{
    public async Task<KullaniciYetkisi> CozAsync(Guid kullaniciId, CancellationToken ct = default)
    {
        var bugun = DateOnly.FromDateTime(saat.GetUtcNow().UtcDateTime);

        // Geçerli rol atamaları. Süresi geçmiş devir buraya hiç gelmez.
        var rolIdleri = await db.KullaniciRolleri
            .Where(r => r.KullaniciId == kullaniciId)
            .Where(r => (r.GecerlilikBas == null || r.GecerlilikBas <= bugun)
                     && (r.GecerlilikBitis == null || r.GecerlilikBitis >= bugun))
            .Select(r => r.RolId)
            .ToListAsync(ct);

        if (rolIdleri.Count == 0)
            return KullaniciYetkisi.Bos(kullaniciId);

        var roller = await db.Roller
            .Where(r => rolIdleri.Contains(r.Id))
            .Select(r => new { r.Id, r.Kapsam })
            .ToListAsync(ct);

        if (roller.Count == 0)
            return KullaniciYetkisi.Bos(kullaniciId);

        var izinler = await db.RolIzinleri
            .Where(ri => rolIdleri.Contains(ri.RolId))
            .Select(ri => ri.IzinKodu)
            .Distinct()
            .ToListAsync(ct);

        // En geniş kapsam kazanır.
        var seviye = roller.Max(r => r.Kapsam);

        var calisanId = await db.Kullanicilar
            .Where(k => k.Id == kullaniciId)
            .Select(k => k.CalisanId)
            .FirstOrDefaultAsync(ct);

        // Kapsam satırlarını yalnız gerektiğinde okuyoruz.
        List<Guid> departmanlar = [];
        List<Guid> ekipler = [];

        if (seviye == KapsamSeviyesi.Kapsam)
        {
            var kapsamlar = await db.KullaniciKapsamlari
                .Where(k => k.KullaniciId == kullaniciId)
                .Select(k => new { k.Tip, k.HedefId })
                .ToListAsync(ct);

            departmanlar = kapsamlar.Where(k => k.Tip == KapsamTipi.Departman).Select(k => k.HedefId).ToList();
            ekipler      = kapsamlar.Where(k => k.Tip == KapsamTipi.Ekip).Select(k => k.HedefId).ToList();
        }

        return new KullaniciYetkisi(
            kullaniciId,
            izinler.ToHashSet(),
            seviye,
            departmanlar,
            ekipler,
            calisanId);
    }
}
