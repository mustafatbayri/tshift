using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace TShift.Infrastructure.Persistence;

// EF Core komut satiri araclari (dotnet ef) bu fabrikayi kullanir:
// uygulamayi ayaga kaldirmadan DbContext olusturabilmek icin.
public class TasarimZamaniFabrika : IDesignTimeDbContextFactory<TShiftDbContext>
{
    public TShiftDbContext CreateDbContext(string[] args)
    {
        // T-34: "dotnet ef" komutlari da DB_PASSWORD ister. Varsayilan yok.
        var parola = Sirlar.Zorunlu("DB_PASSWORD");
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql($"Host=localhost;Port=5433;Database=tshift;Username=tshift;Password={parola}")
            .Options;
        return new TShiftDbContext(opt, new KiraciBaglami());
    }
}
