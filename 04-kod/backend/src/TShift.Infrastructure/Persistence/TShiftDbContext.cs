using Microsoft.EntityFrameworkCore;
using TShift.Domain.Calisanlar;
using TShift.Domain.Common;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;

namespace TShift.Infrastructure.Persistence;

public class TShiftDbContext(DbContextOptions<TShiftDbContext> options, IKiraciBaglami baglam)
    : DbContext(options)
{
    public DbSet<Kiraci> Kiracilar => Set<Kiraci>();
    public DbSet<Kullanici> Kullanicilar => Set<Kullanici>();
    public DbSet<Departman> Departmanlar => Set<Departman>();
    public DbSet<Ekip> Ekipler => Set<Ekip>();
    public DbSet<Calisan> Calisanlar => Set<Calisan>();
    public DbSet<CalisanSozlesmesi> CalisanSozlesmeleri => Set<CalisanSozlesmesi>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.HasDefaultSchema("public");
        b.ApplyConfigurationsFromAssembly(typeof(TShiftDbContext).Assembly);

        // SAVUNMANIN BİRİNCİ KATMANI: küresel sorgu filtresi.
        // IKiraciVarligi uygulayan her varlık otomatik olarak kiracıyla filtrelenir.
        // Yeni tablo eklendiğinde arayüzü uygulamak yeterli; filtre yazmayı unutmak diye bir şey olmaz.
        foreach (var et in b.Model.GetEntityTypes())
        {
            if (!typeof(IKiraciVarligi).IsAssignableFrom(et.ClrType)) continue;

            var p = System.Linq.Expressions.Expression.Parameter(et.ClrType, "e");
            var sol = System.Linq.Expressions.Expression.Property(p, nameof(IKiraciVarligi.KiraciId));
            var sag = System.Linq.Expressions.Expression.Property(
                System.Linq.Expressions.Expression.Constant(this), nameof(AktifKiraciId));
            var esit = System.Linq.Expressions.Expression.Equal(sol, sag);
            b.Entity(et.ClrType).HasQueryFilter(
                System.Linq.Expressions.Expression.Lambda(esit, p));
        }
    }

    /// <summary>Sorgu filtresinin okuduğu değer. Kiracı yoksa hiçbir satır eşleşmez.</summary>
    public Guid AktifKiraciId => baglam.KiraciId ?? Guid.Empty;

    public override int SaveChanges()
    {
        KiraciIdDoldur(); ZamanDamgala();
        return base.SaveChanges();
    }

    public override Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        KiraciIdDoldur(); ZamanDamgala();
        return base.SaveChangesAsync(ct);
    }

    /// <summary>Yeni kayıtlarda KiraciId'yi elle yazmayı unutmak mümkün olmasın.</summary>
    private void KiraciIdDoldur()
    {
        var kid = baglam.KiraciId;
        if (kid is null) return;

        foreach (var e in ChangeTracker.Entries<IKiraciVarligi>())
            if (e.State == EntityState.Added && e.Entity.KiraciId == Guid.Empty)
                e.Entity.KiraciId = kid.Value;
    }

    private void ZamanDamgala()
    {
        foreach (var e in ChangeTracker.Entries<VarlikTemel>())
            if (e.State == EntityState.Modified)
                e.Entity.GuncellemeZamani = DateTimeOffset.UtcNow;
    }
}
