using Microsoft.EntityFrameworkCore;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Persistence;

namespace TShift.Infrastructure.Yetki;

public interface IKiraciKurulumServisi
{
    /// <summary>Yeni kiracıya sistem rollerini kurar. Zaten kuruluysa dokunmaz.</summary>
    Task<int> SistemRolleriniKurAsync(Guid kiraciId, CancellationToken ct = default);

    /// <summary>Kullanıcıya rol atar. Rol kodu o kiracıda bulunmalı.</summary>
    Task RolAtaAsync(Guid kullaniciId, string rolKodu,
        DateOnly? bas = null, DateOnly? bitis = null, Guid? verenKullaniciId = null,
        CancellationToken ct = default);

    /// <summary>Kullanıcıya departman veya ekip kapsamı ekler.</summary>
    Task KapsamEkleAsync(Guid kullaniciId, KapsamTipi tip, Guid hedefId, CancellationToken ct = default);
}

/// <summary>
/// Kiracı kurulumu. Şimdilik yalnız roller; ilerde vardiya şablonları ve
/// varsayılan kural parametreleri de buradan kurulacak (spec §4.1).
///
/// ÖNEMLİ: bu servis kiracı bağlamı KURULU haldeyken çağrılmalı. Aksi halde
/// RLS yazmayı reddeder — ki bu iyi bir şeydir: yanlışlıkla başka firmaya rol
/// kurmak mümkün olmasın.
/// </summary>
public sealed class KiraciKurulumServisi(TShiftDbContext db) : IKiraciKurulumServisi
{
    public async Task<int> SistemRolleriniKurAsync(Guid kiraciId, CancellationToken ct = default)
    {
        var mevcut = await db.Roller.Select(r => r.Kod).ToListAsync(ct);
        var eklenen = 0;

        foreach (var tanim in YetkiKatalogu.Roller)
        {
            if (mevcut.Contains(tanim.Kod)) continue;

            var rol = new Rol
            {
                KiraciId = kiraciId,
                Kod = tanim.Kod,
                Ad = tanim.Ad,
                Kapsam = tanim.Kapsam,
                SistemMi = true
            };
            db.Roller.Add(rol);

            foreach (var izin in tanim.Izinler)
                db.RolIzinleri.Add(new RolIzni { KiraciId = kiraciId, RolId = rol.Id, IzinKodu = izin });

            eklenen++;
        }

        if (eklenen > 0) await db.SaveChangesAsync(ct);
        return eklenen;
    }

    public async Task RolAtaAsync(Guid kullaniciId, string rolKodu,
        DateOnly? bas = null, DateOnly? bitis = null, Guid? verenKullaniciId = null,
        CancellationToken ct = default)
    {
        var rol = await db.Roller.FirstOrDefaultAsync(r => r.Kod == rolKodu, ct)
            ?? throw new InvalidOperationException($"Rol bulunamadi: {rolKodu}. Kiraci baglami kurulu mu?");

        db.KullaniciRolleri.Add(new KullaniciRolu
        {
            KullaniciId = kullaniciId,
            RolId = rol.Id,
            GecerlilikBas = bas,
            GecerlilikBitis = bitis,
            VerenKullaniciId = verenKullaniciId
        });
        await db.SaveChangesAsync(ct);
    }

    public async Task KapsamEkleAsync(Guid kullaniciId, KapsamTipi tip, Guid hedefId,
        CancellationToken ct = default)
    {
        db.KullaniciKapsamlari.Add(new KullaniciKapsami
        {
            KullaniciId = kullaniciId,
            Tip = tip,
            HedefId = hedefId
        });
        await db.SaveChangesAsync(ct);
    }
}
