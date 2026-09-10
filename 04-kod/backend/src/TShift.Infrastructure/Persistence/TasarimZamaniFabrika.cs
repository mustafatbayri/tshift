using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace TShift.Infrastructure.Persistence;

// EF Core komut satiri araclari (dotnet ef) bu fabrikayi kullanir:
// uygulamayi ayaga kaldirmadan DbContext olusturabilmek icin.
public class TasarimZamaniFabrika : IDesignTimeDbContextFactory<TShiftDbContext>
{
    public TShiftDbContext CreateDbContext(string[] args)
    {
        var parola = Environment.GetEnvironmentVariable("DB_PASSWORD") ?? "tshift_dev_2026";
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql($"Host=localhost;Port=5433;Database=tshift;Username=tshift;Password={parola}")
            .Options;
        return new TShiftDbContext(opt, new KiraciBaglami());
    }
}
