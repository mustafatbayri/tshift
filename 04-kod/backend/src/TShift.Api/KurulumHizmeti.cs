using Microsoft.EntityFrameworkCore;
using Npgsql;
using TShift.Infrastructure.Persistence;

namespace TShift.Api;

/// <summary>
/// Kutu içinde ilk açılış kurulumu: migration, satır seviyesi güvenlik ve
/// örnek veri.
///
/// ⚠ CANLIDA ASLA ÇALIŞMAZ. Yalnızca `TSHIFT_KURULUM=true` ortam değişkeni
/// açıkça verildiğinde devreye girer.
///
/// NEDEN TEHLİKELİ VE NEDEN YİNE DE VAR:
/// Uygulamanın açılışta kendi kendine şema değiştirmesi kötü bir alışkanlıktır.
/// Şema değişikliği bilinçli bir adım olmalı: birinin üretilen SQL'i okuması,
/// yedek alması, ne zaman çalıştığını bilmesi gerekir. Açılışta otomatik
/// çalışan bir migration, bir gün beklenmedik bir anda beklenmedik bir
/// veritabanına dokunur.
///
/// Buna rağmen var, çünkü inceleme ortamında `docker compose up` tek komut
/// olmalı. Bir mimardan .NET SDK kurup migration çalıştırmasını istemek,
/// incelemenin hiç yapılmaması demektir.
///
/// Sınır net: bu bayrak yalnız `docker-compose.yml` içindeki inceleme
/// profilinde açık. Canlı ortamda migration ayrı ve bilinçli bir adımdır.
/// Bkz. RISKLER-VE-ONLEMLER.md §6 kırmızı çizgiler.
/// </summary>
public static class KurulumHizmeti
{
    public static async Task CalistirAsync(WebApplication app)
    {
        var kayit = app.Services.GetRequiredService<ILoggerFactory>().CreateLogger("Kurulum");

        kayit.LogWarning(
            "TSHIFT_KURULUM acik. Migration ve RLS betikleri otomatik calistirilacak. " +
            "Bu ayar CANLI ORTAMDA KAPALI olmalidir.");

        var sahipBaglanti = SahipBaglantisi();

        // ---- 1) Şema -----------------------------------------------------
        // Migration'lar SAHİBİ rolle çalışır; uygulama rolünün tablo yaratma
        // yetkisi yok ve olmamalı.
        await using (var kurulumBaglami = SahipBaglami(sahipBaglanti))
        {
            await BeklVeritabani(kurulumBaglami, kayit);
            kayit.LogInformation("Migration uygulaniyor...");
            await kurulumBaglami.Database.MigrateAsync();
        }

        // ---- 2) Satır seviyesi güvenlik ----------------------------------
        // Betikler dosya adı sırasıyla çalışır: 01, 02, 03... Sıra önemli —
        // 02 uygulama rolünü yaratır, sonrakiler ona yetki verir.
        var klasor = Path.Combine(AppContext.BaseDirectory, "db", "rls");
        if (Directory.Exists(klasor))
        {
            await using var ham = new NpgsqlConnection(sahipBaglanti);
            await ham.OpenAsync();

            foreach (var dosya in Directory.GetFiles(klasor, "*.sql").OrderBy(d => d))
            {
                kayit.LogInformation("Betik: {Dosya}", Path.GetFileName(dosya));
                await using var komut = ham.CreateCommand();
                komut.CommandText = await File.ReadAllTextAsync(dosya);
                await komut.ExecuteNonQueryAsync();
            }
        }
        else
        {
            kayit.LogWarning("db/rls klasoru bulunamadi: {Klasor}", klasor);
        }

        // ---- 3) Örnek veri -----------------------------------------------
        // Uygulama rolüyle, yani RLS devredeyken. Kurulumun kendisi de
        // güvenlik kurallarına tabi olsun.
        using var kapsam = app.Services.CreateScope();
        var db = kapsam.ServiceProvider.GetRequiredService<TShiftDbContext>();

        if (await db.Kiracilar.AnyAsync())
        {
            kayit.LogInformation("Ornek veri zaten var, atlandi.");
            return;
        }

        kayit.LogInformation("Ornek veri olusturuluyor...");
        await OrnekVeri.KurAsync(kapsam.ServiceProvider);
        kayit.LogInformation("Kurulum tamam. Giris: anadolu-cm / mudur@anadolu-cm.test / {Parola}",
            OrnekVeri.Parola);
    }

    /// <summary>
    /// Sahibi rolün bağlantı dizesi. Uygulamanınkinden AYRI bir ortam
    /// değişkeninden gelir — ikisi karışırsa uygulama süper kullanıcıyla
    /// bağlanır ve RLS sessizce devre dışı kalır. (Bu hata bir kez yapıldı;
    /// bkz. DEGISIM-GUNLUGU 10 Eylül.)
    /// </summary>
    private static string SahipBaglantisi()
    {
        var sablon = Environment.GetEnvironmentVariable("TSHIFT_SAHIP_BAGLANTI")
            ?? "Host=localhost;Port=5433;Database=tshift;Username=tshift;Password={DB_PASSWORD}";
        var parola = Environment.GetEnvironmentVariable("DB_PASSWORD") ?? "tshift_dev_2026";
        return sablon.Replace("{DB_PASSWORD}", parola);
    }

    private static TShiftDbContext SahipBaglami(string baglanti)
    {
        var secenekler = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(baglanti)
            .Options;

        // Kiracı bağlamı boş: migration kiracıya ait bir iş değil.
        var kiraci = new KiraciBaglami();
        kiraci.Ayarla(null);
        return new TShiftDbContext(secenekler, kiraci);
    }

    /// <summary>
    /// Veritabanı kabı sağlıklı raporlansa da bazen ilk saniyelerde bağlantı
    /// kabul etmiyor. Birkaç kez deniyoruz — yoksa kurulum "veritabanı yok"
    /// diye patlar ve sebebi anlaşılmaz görünür.
    /// </summary>
    private static async Task BeklVeritabani(TShiftDbContext db, ILogger kayit)
    {
        for (var deneme = 1; deneme <= 10; deneme++)
        {
            try
            {
                await db.Database.OpenConnectionAsync();
                await db.Database.CloseConnectionAsync();
                return;
            }
            catch (Exception e) when (deneme < 10)
            {
                kayit.LogInformation("Veritabani hazir degil ({Deneme}/10): {Mesaj}", deneme, e.Message);
                await Task.Delay(TimeSpan.FromSeconds(2));
            }
        }
    }
}
