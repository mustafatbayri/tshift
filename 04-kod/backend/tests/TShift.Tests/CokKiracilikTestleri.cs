using Microsoft.EntityFrameworkCore;
using TShift.Domain.Calisanlar;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Infrastructure.Persistence;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// ÇOK KİRACILIK YALITIM TESTLERİ — projenin en kritik testi.
///
/// Sorduğu soru: "A firmasının kullanıcısı B firmasının verisini görebilir mi?"
/// Cevabın her koşulda HAYIR olması gerekiyor.
///
/// İki savunma katmanını ayrı ayrı sınıyoruz:
///   1. EF küresel sorgu filtresi — uygulama katmanı (kolaylık)
///   2. Satır seviyesi güvenlik   — veritabanı katmanı (asıl garanti)
///
/// 2, 3 ve 4 numaralı testler EF'i kasten devre dışı bırakıp ham SQL yazar.
/// Uygulama katmanı hata yapsa bile veritabanının tutması gerekir.
///
/// Not: yerel geliştirme veritabanına bağlanır (docker compose).
/// Her test kendi verisini oluşturur ve sonunda temizler.
/// </summary>
public class CokKiracilikTestleri
{
    // DİKKAT: `tshift` DEĞİL, `tshift_app`.
    // `tshift` süper kullanıcıdır ve PostgreSQL'de süper kullanıcı RLS'i tamamen aşar.
    // Onunla test etmek, alarmı kapatıp "bak hırsız girmedi" demek olur.
    // Uygulama da testler de RLS'e tabi olan kısıtlı rolle bağlanır. Bkz. db/rls/02-uygulama-rolu.sql
    private const string Baglanti =
        "Host=localhost;Port=5433;Database=tshift;Username=tshift_app;Password=tshift_app_dev_2026";

    private static TShiftDbContext Baglam(IKiraciBaglami baglam)
    {
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(baglam))
            .Options;
        return new TShiftDbContext(opt, baglam);
    }

    /// <summary>Bir kiracı ve altında bir departman + bir çalışan oluşturur.</summary>
    private static async Task<Guid> KiraciKur(string etiket, string ek, string cad)
    {
        var b = new KiraciBaglami();
        b.Ayarla(null);
        await using var db = Baglam(b);

        var k = new Kiraci { Ad = $"Test {etiket} {ek}", Slug = $"test-{etiket}-{ek}".ToLowerInvariant(), Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(k);
        await db.SaveChangesAsync();

        b.Ayarla(k.Id);
        var d = new Departman { Ad = "Ops", Kod = $"OPS-{etiket}-{ek}", CalismaTipi = CalismaTipi.Saatli };
        db.Departmanlar.Add(d);
        await db.SaveChangesAsync();

        db.Calisanlar.Add(new Calisan
        {
            PersonelNo = $"{etiket}-{ek}", Ad = cad, Soyad = "Test",
            DepartmanId = d.Id, IseGiris = new DateOnly(2025, 1, 1)
        });
        await db.SaveChangesAsync();
        return k.Id;
    }

    /// <summary>
    /// Test verisini siler. İki incelik var, ikisi de RLS'in doğrudan sonucu:
    ///
    /// 1) Kiracı bağlamı KURULU olmadan silme yapılamaz. Bağlam boşken RLS
    ///    satırları gizler, DELETE hiçbir şeyi bulamaz ve sessizce 0 satır siler.
    ///    Bu yüzden her kiracı kendi bağlamıyla temizlenir.
    ///
    /// 2) Çocuk tablolar bağımlılık sırasına göre elle silinir. `tenants` üzerinden
    ///    kademeli silmeye güvenemeyiz: employees → departments ilişkisi
    ///    OnDelete(Restrict) ile tanımlı, yani kademeli silmeyi bilerek engelliyor.
    ///    (Yanlışlıkla departman silinince çalışanların uçmasını istemiyoruz.)
    /// </summary>
    private static async Task Temizle(params Guid[] kiraciler)
    {
        foreach (var k in kiraciler)
        {
            var bk = new KiraciBaglami();
            bk.Ayarla(k);
            await using var dbk = Baglam(bk);

            // Sıra önemli: önce en derindeki çocuk, sonra yukarı doğru.
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM user_scopes WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM user_roles WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM role_permissions WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM roles WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM refresh_tokens WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM user_credentials WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM employee_contracts WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM employees WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM teams WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM departments WHERE tenant_id = {k}");
            await dbk.Database.ExecuteSqlAsync($"DELETE FROM users WHERE tenant_id = {k}");
        }

        // tenants tablosunda RLS yok (kiracıların kendisi kiracıya ait değil),
        // bu yüzden bağlamsız silinir.
        var b = new KiraciBaglami();
        b.Ayarla(null);
        await using var db = Baglam(b);
        foreach (var k in kiraciler)
            await db.Database.ExecuteSqlAsync($"DELETE FROM tenants WHERE id = {k}");
    }

    // ------------------------------------------------------------------ 0
    /// <summary>
    /// Bekçi testi. Diğer üç testin anlamlı olmasının ön koşulu:
    /// bağlandığımız rol süper kullanıcı OLMAMALI. Süperse RLS hiç çalışmaz ve
    /// "yalıtım testleri geçti" demek hiçbir şey ifade etmez.
    /// Biri ileride bağlantı dizesini `tshift`e çevirirse burası anında yakalar.
    /// </summary>
    [Fact(DisplayName = "0 - Baglanan rol super kullanici degil (RLS gecerli olsun)")]
    public async Task Rol_super_kullanici_degil()
    {
        var b = new KiraciBaglami();
        b.Ayarla(null);
        await using var db = Baglam(b);

        var super = await db.Database
            .SqlQuery<bool>($"SELECT rolsuper AS \"Value\" FROM pg_roles WHERE rolname = current_user")
            .SingleAsync();
        var muaf = await db.Database
            .SqlQuery<bool>($"SELECT rolbypassrls AS \"Value\" FROM pg_roles WHERE rolname = current_user")
            .SingleAsync();

        Assert.False(super, "Baglanti super kullanici ile kurulmus. Super kullanici RLS'i asar; yalitim testleri anlamsiz hale gelir.");
        Assert.False(muaf, "Rolde BYPASSRLS var. RLS devre disi kalir.");
    }

    // ------------------------------------------------------------------ 1
    [Fact(DisplayName = "1 - Iki ayri baglam ayni anda birbirinin verisini gormez")]
    public async Task Iki_baglam_birbirini_gormez()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await KiraciKur("A", ek, "Ali");
        var b = await KiraciKur("B", ek, "Berk");
        try
        {
            // Bilerek İKİ AYRI bağlam nesnesi ve İKİ AYRI DbContext kuruyoruz.
            // Amaç: EF'in filtreyi ilk örneğe sabitleyip sabitlemediğini yakalamak.
            var bagA = new KiraciBaglami(); bagA.Ayarla(a);
            var bagB = new KiraciBaglami(); bagB.Ayarla(b);

            await using var dbA = Baglam(bagA);
            await using var dbB = Baglam(bagB);

            var aListe = await dbA.Calisanlar.ToListAsync();
            var bListe = await dbB.Calisanlar.ToListAsync();

            Assert.NotEmpty(aListe);
            Assert.NotEmpty(bListe);
            Assert.All(aListe, c => Assert.Equal(a, c.KiraciId));
            Assert.All(bListe, c => Assert.Equal(b, c.KiraciId));
        }
        finally { await Temizle(a, b); }
    }

    // ------------------------------------------------------------------ 2
    [Fact(DisplayName = "2 - Ham SQL ile bile baska kiracinin satiri gelmez (RLS)")]
    public async Task Ham_sql_ile_sizmaz()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await KiraciKur("A", ek, "Ali");
        var b = await KiraciKur("B", ek, "Berk");
        try
        {
            var bag = new KiraciBaglami(); bag.Ayarla(a);
            await using var db = Baglam(bag);

            // EF'in sorgu filtresini tamamen atlıyoruz — kasten "uygulama hatası" taklidi.
            // Geriye yalnızca veritabanının savunması kalıyor.
            var digerKiraci = await db.Database
                .SqlQuery<long>($"SELECT count(*)::bigint AS \"Value\" FROM employees WHERE tenant_id = {b}")
                .SingleAsync();
            Assert.Equal(0, digerKiraci);

            var toplam = await db.Database
                .SqlQuery<long>($"SELECT count(*)::bigint AS \"Value\" FROM employees")
                .SingleAsync();
            var kendi = await db.Database
                .SqlQuery<long>($"SELECT count(*)::bigint AS \"Value\" FROM employees WHERE tenant_id = {a}")
                .SingleAsync();

            Assert.True(kendi > 0, "A kiracisinin calisani gorunmeli");
            Assert.Equal(kendi, toplam);
        }
        finally { await Temizle(a, b); }
    }

    // ------------------------------------------------------------------ 3
    [Fact(DisplayName = "3 - Kiraci baglami yoksa hicbir satir gorunmez")]
    public async Task Baglam_yoksa_bos()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await KiraciKur("A", ek, "Ali");
        try
        {
            var bag = new KiraciBaglami(); bag.Ayarla(null);
            await using var db = Baglam(bag);

            var sayi = await db.Database
                .SqlQuery<long>($"SELECT count(*)::bigint AS \"Value\" FROM employees")
                .SingleAsync();

            Assert.Equal(0, sayi);
        }
        finally { await Temizle(a); }
    }

    // ------------------------------------------------------------------ 4
    [Fact(DisplayName = "4 - Baska kiracinin kimligiyle kayit yazilamaz")]
    public async Task Baska_kiraciya_yazilamaz()
    {
        var ek = Guid.NewGuid().ToString("N")[..6];
        var a = await KiraciKur("A", ek, "Ali");
        var b = await KiraciKur("B", ek, "Berk");
        try
        {
            var bag = new KiraciBaglami(); bag.Ayarla(a);
            await using var db = Baglam(bag);

            var dep = await db.Departmanlar.FirstAsync();

            db.Calisanlar.Add(new Calisan
            {
                KiraciId = b,                    // kasten yanlış kiracı
                PersonelNo = $"SIZMA-{ek}",
                Ad = "Sizma", Soyad = "Denemesi",
                DepartmanId = dep.Id,
                IseGiris = new DateOnly(2025, 1, 1)
            });

            // RLS'in WITH CHECK kısmı bunu reddetmeli.
            await Assert.ThrowsAnyAsync<DbUpdateException>(() => db.SaveChangesAsync());
        }
        finally { await Temizle(a, b); }
    }
}
