using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using TShift.Domain.Common;
using TShift.Infrastructure.Persistence;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// MİMARİ TESTLERİ — özellik değil, YASA sınar.
///
/// Diğer testler "bu özellik doğru çalışıyor mu" diye sorar. Bunlar
/// "sistemin her zaman doğru olması gereken kuralları hâlâ geçerli mi"
/// diye sorar. Yeni bir özellik eklenirken bir kuralı sessizce çiğnemek
/// çok kolaydır; bu testlerin varlık sebebi tam olarak budur.
///
/// Örnek: altı ay sonra yeni bir tablo eklenir, RLS açmak unutulur.
/// Hiçbir özellik testi bunu fark etmez — tablo çalışır, veri gelir.
/// Yalnız M1 kırılır.
///
/// Bu testler yavaş yavaş büyümeli. Bir hata bulunduğunda sorulacak soru:
/// "bunu bir yasa hâline getirebilir miyim?"
/// </summary>
public class MimariTestleri : IClassFixture<TestUygulamasi>
{
    private readonly TestUygulamasi _uygulama;
    public MimariTestleri(TestUygulamasi uygulama) => _uygulama = uygulama;

    private const string Baglanti =
        "Host=localhost;Port=5433;Database=tshift;Username=tshift_app;Password=tshift_app_dev_2026";

    private static TShiftDbContext Baglam()
    {
        var b = new KiraciBaglami();
        b.Ayarla(null);
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(b))
            .Options;
        return new TShiftDbContext(opt, b);
    }

    private sealed record RlsSatiri(string Tablo, bool Acik, bool Zorunlu);

    private static async Task<List<RlsSatiri>> RlsDurumu(TShiftDbContext db)
        => await db.Database.SqlQuery<RlsSatiri>($"""
            SELECT c.relname             AS "Tablo",
                   c.relrowsecurity      AS "Acik",
                   c.relforcerowsecurity AS "Zorunlu"
            FROM   pg_class c
            JOIN   pg_namespace n ON n.oid = c.relnamespace
            WHERE  n.nspname = 'public' AND c.relkind = 'r'
            """).ToListAsync();

    // ------------------------------------------------------------------ M1
    /// <summary>
    /// Kiracıya ait HER varlığın tablosunda satır seviyesi güvenlik açık olmalı.
    ///
    /// Bu, "yeni tablo ekledim, RLS betiğini güncellemeyi unuttum" hatasının
    /// tek gerçek savunmasıdır. Böyle bir tablo mükemmel çalışır, veri döner,
    /// hiçbir test kırılmaz — ve bir gün bir firma diğerinin verisini görür.
    /// </summary>
    [Fact(DisplayName = "M1 - Kiraciya ait her tabloda RLS acik ve zorunlu")]
    public async Task Her_kiraci_tablosunda_rls_var()
    {
        await using var db = Baglam();

        // Modeldeki kiracıya ait varlıkların tablo adlarını EF'ten okuyoruz.
        // Elle yazılmış bir liste değil — yeni varlık eklendiğinde kendiliğinden kapsanır.
        var kiraciTablolari = db.Model.GetEntityTypes()
            .Where(e => typeof(IKiraciVarligi).IsAssignableFrom(e.ClrType))
            .Select(e => e.GetTableName())
            .Where(t => t is not null)
            .Distinct()
            .ToList();

        Assert.NotEmpty(kiraciTablolari);

        var durum = await RlsDurumu(db);
        var eksik = new List<string>();

        foreach (var tablo in kiraciTablolari)
        {
            var s = durum.FirstOrDefault(d => d.Tablo == tablo);
            if (s is null) { eksik.Add($"{tablo}: tablo bulunamadi"); continue; }
            if (!s.Acik)    eksik.Add($"{tablo}: RLS KAPALI");
            if (!s.Zorunlu) eksik.Add($"{tablo}: FORCE yok (tablo sahibi RLS'i asar)");
        }

        Assert.True(eksik.Count == 0,
            "Kiraciya ait tablolarda RLS eksik:\n  " + string.Join("\n  ", eksik) +
            "\n\nYeni tablo eklendiyse db/rls/ altina bir betik yazip calistirmak gerekiyor.");
    }

    // ------------------------------------------------------------------ M2
    /// <summary>
    /// RLS dışında kalan tabloların listesi KAPALI olmalı.
    ///
    /// Üç tablo bilerek dışarıda; her birinin gerekçesi kodda yazılı.
    /// Dördüncüsü çıkarsa bu test kırılır ve birinin karar vermesi gerekir —
    /// sessizce eklenemez.
    /// </summary>
    [Fact(DisplayName = "M2 - RLS disindaki tablolar sadece bilinen istisnalar")]
    public async Task Rls_disi_tablolar_bilinen_istisnalar()
    {
        // Gerekçeler:
        //   tenants        — kiracının kendisi kiracıya ait değildir
        //   login_attempts — kiracı bilinmeden yazılır (kaba kuvvet sayacı)
        //   permissions    — sistem sözlüğü, müşteri verisi değil
        var izinliler = new HashSet<string> { "tenants", "login_attempts", "permissions" };

        await using var db = Baglam();
        var durum = await RlsDurumu(db);

        var beklenmedik = durum
            .Where(d => !d.Acik)
            .Select(d => d.Tablo)
            .Where(t => !t.StartsWith("__"))          // EF migration gecmisi
            .Where(t => !izinliler.Contains(t))
            .ToList();

        Assert.True(beklenmedik.Count == 0,
            "RLS'siz beklenmedik tablo(lar): " + string.Join(", ", beklenmedik) +
            "\nYa RLS acilmali, ya da istisna listesine GEREKCESIYLE eklenmeli.");
    }

    // ------------------------------------------------------------------ M3
    /// <summary>
    /// Her HTTP ucu ya kimlik doğrulaması ister, ya da açık bir listede yer alır.
    ///
    /// "Yeni uç yazdım, RequireAuthorization koymayı unuttum" hatası tamamen
    /// sessizdir: uç çalışır, veri döner, kimse fark etmez. Bu test onu
    /// derleme sonrası ilk saniyede yakalar.
    /// </summary>
    [Fact(DisplayName = "M3 - Her uc korumali ya da acikca istisna")]
    public void Korumasiz_uc_yok()
    {
        // Bilerek herkese açık uçlar:
        var acikUclar = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "/health",                    // ayakta mi
            "/health/db",                 // veritabani baglantisi
            "/api/v1/auth/login",         // giris - dogal olarak jetonsuz
            "/api/v1/auth/refresh",       // yenileme - jetonun kendisi kimlik
            "/api/v1/auth/logout",        // cikis
            "/dev/seed",                  // GECICI - surum oncesi silinecek
            "/dev/tenants"                // GECICI - surum oncesi silinecek
        };

        var kaynak = _uygulama.Services.GetRequiredService<EndpointDataSource>();

        var korumasiz = kaynak.Endpoints
            .OfType<RouteEndpoint>()
            .Where(e => e.Metadata.GetMetadata<IAuthorizeData>() is null)
            .Select(e => "/" + e.RoutePattern.RawText!.TrimStart('/'))
            .Where(y => !acikUclar.Contains(y))
            .Distinct()
            .ToList();

        Assert.True(korumasiz.Count == 0,
            "Korumasiz uc(lar): " + string.Join(", ", korumasiz) +
            "\nYa .RequireAuthorization(...) eklenmeli, ya da yukaridaki listeye " +
            "GEREKCESIYLE yazilmali.");
    }

    // ------------------------------------------------------------------ M4
    /// <summary>
    /// Türkçe 'I' tuzağı.
    ///
    /// Türkçe kültüründe "I".ToLower() sonucu "ı"dır, "i" değil. Sunucu Türkçe
    /// yerel ayarla çalışırsa `"IZLEYICI".ToLower() == "izleyici"` YANLIŞ olur.
    /// Bu, e-posta karşılaştırmasından rol kodu eşleştirmesine kadar her yerde
    /// sessizce yanlış sonuç üretir ve hata ayıklaması kâbustur.
    ///
    /// Kural: kültürden bağımsız karşılaştırmalarda daima `ToLowerInvariant`.
    /// </summary>
    [Fact(DisplayName = "M4 - Kulture bagimli ToLower/ToUpper kullanilmiyor")]
    public void Turkce_i_tuzagi_yok()
    {
        var kok = KaynakKoku();
        var desen = new Regex(@"\.To(Lower|Upper)\s*\(\s*\)", RegexOptions.Compiled);
        var bulgular = new List<string>();

        foreach (var dosya in Directory.EnumerateFiles(kok, "*.cs", SearchOption.AllDirectories))
        {
            if (dosya.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}") ||
                dosya.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") ||
                dosya.Contains("Migrations")) continue;

            var satirlar = File.ReadAllLines(dosya);
            for (var i = 0; i < satirlar.Length; i++)
            {
                var satir = satirlar[i].TrimStart();

                // Yorum satirlarini atla. Bu testin kendi aciklamasi da ornek
                // olarak ToLower() yaziyor; onu hata sanmak yanlis alarm olur.
                // Yanlis alarm veren bir kontrol, bir sure sonra ciddiye
                // alinmayan bir kontrole donusur.
                if (satir.StartsWith("//") || satir.StartsWith("*")) continue;

                if (desen.IsMatch(satirlar[i]))
                    bulgular.Add($"{Path.GetFileName(dosya)}:{i + 1}");
            }
        }

        Assert.True(bulgular.Count == 0,
            "Kulture bagimli ToLower()/ToUpper() bulundu:\n  " + string.Join("\n  ", bulgular) +
            "\nToLowerInvariant() / ToUpperInvariant() kullan. Turkce 'I' harfi farkli davranir.");
    }

    // ------------------------------------------------------------------ M5
    /// <summary>
    /// Ayar dosyalarında gerçek sır bulunmamalı — yalnız yer tutucu.
    /// Sırlar ortam değişkeninden gelir; depoya girmez.
    /// </summary>
    [Fact(DisplayName = "M5 - appsettings icinde gercek parola yok")]
    public void Ayar_dosyalarinda_sir_yok()
    {
        var kok = KaynakKoku();
        var desen = new Regex(@"(Password|Secret|ApiKey)\s*=\s*(?!\{)([^\s"";,}]+)",
            RegexOptions.IgnoreCase | RegexOptions.Compiled);
        var bulgular = new List<string>();

        foreach (var dosya in Directory.EnumerateFiles(kok, "appsettings*.json", SearchOption.AllDirectories))
        {
            if (dosya.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}")) continue;

            foreach (Match m in desen.Matches(File.ReadAllText(dosya)))
                bulgular.Add($"{Path.GetFileName(dosya)}: {m.Value}");
        }

        Assert.True(bulgular.Count == 0,
            "Ayar dosyasinda sir gorunuyor:\n  " + string.Join("\n  ", bulgular) +
            "\nYer tutucu kullan ({DB_PASSWORD} gibi) ve degeri ortam degiskeninden oku.");
    }

    // ------------------------------------------------------------------ M6
    /// <summary>
    /// Denetim kaydı SADECE EKLENİR olmalı.
    ///
    /// Uygulama rolünün `audit_log` üzerinde UPDATE ve DELETE yetkisi olmamalı.
    /// Biri ileride "temizlik lazım" diye bu yetkiyi verirse, denetim kaydı
    /// sessizce anlamını kaybeder — ve kimse fark etmez, çünkü her şey
    /// çalışmaya devam eder. Bu test o anı yakalar.
    /// </summary>
    [Fact(DisplayName = "M6 - Denetim kaydi sadece eklenir (UPDATE/DELETE yok)")]
    public async Task Denetim_kaydi_sadece_eklenir()
    {
        await using var db = Baglam();

        var yetkiler = await db.Database.SqlQuery<string>($"""
            SELECT privilege_type AS "Value"
            FROM   information_schema.table_privileges
            WHERE  grantee = 'tshift_app' AND table_name = 'audit_log'
            """).ToListAsync();

        Assert.Contains("SELECT", yetkiler);
        Assert.Contains("INSERT", yetkiler);
        Assert.DoesNotContain("UPDATE", yetkiler);
        Assert.DoesNotContain("DELETE", yetkiler);
    }

    // ------------------------------------------------------------------
    /// <summary>Depo kökünü bulur: TShift.slnx dosyasını yukarı doğru arar.</summary>
    private static string KaynakKoku()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d is not null && !d.EnumerateFiles("TShift.slnx").Any())
            d = d.Parent;

        Assert.NotNull(d);
        return d!.FullName;
    }
}
