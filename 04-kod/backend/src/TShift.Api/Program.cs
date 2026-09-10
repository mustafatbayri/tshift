using Microsoft.EntityFrameworkCore;
using TShift.Domain.Calisanlar;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Infrastructure.Persistence;

var builder = WebApplication.CreateBuilder(args);

// ---- Bağlantı dizesi -------------------------------------------------------
// Parola koda ve appsettings'e YAZILMAZ. Ortam değişkeninden gelir.
// Yerel geliştirmede 04-kod/.env dosyasındaki değerle aynı olmalı.
//
// API, veritabanına `tshift_app` rolüyle bağlanır — `tshift` ile DEĞİL.
// `tshift` süper kullanıcıdır ve PostgreSQL'de süper kullanıcı satır seviyesi
// güvenliği tamamen aşar. Migration'lar sahibi rolle (tshift) çalışır,
// çalışan uygulama kısıtlı rolle. Bkz. db/rls/02-uygulama-rolu.sql
var parola = Environment.GetEnvironmentVariable("APP_DB_PASSWORD") ?? "tshift_app_dev_2026";
var baglantiDizesi = builder.Configuration.GetConnectionString("TShift")!.Replace("{APP_DB_PASSWORD}", parola);

builder.Services.AddScoped<IKiraciBaglami, KiraciBaglami>();
builder.Services.AddScoped<KiraciBaglantiKesici>();

builder.Services.AddDbContext<TShiftDbContext>((sp, opt) =>
{
    opt.UseNpgsql(baglantiDizesi);
    opt.AddInterceptors(sp.GetRequiredService<KiraciBaglantiKesici>());
    if (builder.Environment.IsDevelopment()) opt.EnableSensitiveDataLogging();
});

builder.Services.AddProblemDetails();
var app = builder.Build();

// ---- Kiracı bağlamı --------------------------------------------------------
// GEÇİCİ: kiracı şimdilik X-Tenant-Id başlığından okunuyor.
// Kimlik katmanı devreye girince JWT'den okunacak ve bu ara katman silinecek.
// Spec §10: "tenant_id token'dan okunur, istekten değil."
app.Use(async (ctx, next) =>
{
    if (ctx.Request.Headers.TryGetValue("X-Tenant-Id", out var ham)
        && Guid.TryParse(ham.ToString(), out var kid))
    {
        ctx.RequestServices.GetRequiredService<IKiraciBaglami>().Ayarla(kid);
    }
    await next();
});

// ---- Sağlık ---------------------------------------------------------------
app.MapGet("/health", () => Results.Ok(new { durum = "ayakta", zaman = DateTimeOffset.UtcNow }));

app.MapGet("/health/db", async (TShiftDbContext db) =>
{
    var acilabilir = await db.Database.CanConnectAsync();
    var kiraciSayisi = await db.Kiracilar.CountAsync();
    return Results.Ok(new { veritabani = acilabilir ? "bagli" : "baglanamadi", kiraciSayisi });
});

// ---- Geliştirme: örnek veri ------------------------------------------------
// İKİ kiracı oluşturur. Amaç: çok kiracılık yalıtımını gözle görebilmek.
app.MapPost("/dev/seed", async (TShiftDbContext db, IKiraciBaglami baglam) =>
{
    if (await db.Kiracilar.AnyAsync())
        return Results.Conflict(new { mesaj = "Örnek veri zaten var. Sıfırlamak için: docker compose down -v" });

    var sonuc = new List<object>();

    foreach (var (ad, slug, sektor, birim, kisiler) in new[]
    {
        ("Anadolu Çağrı Merkezi", "anadolu-cm", "cagri_merkezi", "Departman",
            new[] { ("A4101", "Mert", "Kaya"), ("A4102", "Selin", "Arslan"), ("A4103", "Burak", "Demir") }),
        ("Marmara Perakende", "marmara-perakende", "perakende", "Şube",
            new[] { ("P7001", "Ayşe", "Yıldız"), ("P7002", "Emre", "Doğan") }),
    })
    {
        // Kiracı kaydının kendisi kiracıya ait değildir; bağlamı boşaltarak yazıyoruz.
        baglam.Ayarla(null);
        var kiraci = new Kiraci { Ad = ad, Slug = slug, SektorPaketi = sektor, BirimAdi = birim, Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(kiraci);
        await db.SaveChangesAsync();

        // Bundan sonrası o kiracının bağlamında.
        baglam.Ayarla(kiraci.Id);

        var dep = new Departman { Ad = birim == "Şube" ? "Kadıköy Şubesi" : "Çağrı Merkezi Operasyon", Kod = "OPS", CalismaTipi = CalismaTipi.Saatli, AcilisSaat = 8m, KapanisSaat = 24m };
        db.Departmanlar.Add(dep);
        await db.SaveChangesAsync();

        var ekip = new Ekip { DepartmanId = dep.Id, Ad = "Müşteri Hizmetleri", Kod = "MH" };
        db.Ekipler.Add(ekip);

        db.Kullanicilar.Add(new Kullanici
        {
            Ad = "Murat", Soyad = "Kaya", Eposta = $"mudur@{slug}.test",
            EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
        });
        await db.SaveChangesAsync();

        foreach (var (no, cad, csoyad) in kisiler)
        {
            var c = new Calisan
            {
                PersonelNo = no, Ad = cad, Soyad = csoyad,
                DepartmanId = dep.Id, BirincilEkipId = ekip.Id,
                IseGiris = new DateOnly(2024, 1, 15), Durum = CalisanDurumu.Aktif
            };
            db.Calisanlar.Add(c);
            await db.SaveChangesAsync();

            db.CalisanSozlesmeleri.Add(new CalisanSozlesmesi
            {
                CalisanId = c.Id, Tip = SozlesmeTipi.TamZamanli,
                HaftalikSaat = 45m, Baslangic = new DateOnly(2024, 1, 15), Aktif = true
            });
        }
        await db.SaveChangesAsync();

        sonuc.Add(new { kiraci = ad, id = kiraci.Id, calisan = kisiler.Length });
    }

    baglam.Ayarla(null);
    return Results.Ok(new { mesaj = "Örnek veri oluşturuldu", kiracilar = sonuc });
});

// Kiracı listesi — kiracı tablosu filtreye tabi değil (kimlik katmanına kadar açık).
app.MapGet("/dev/tenants", async (TShiftDbContext db) =>
    await db.Kiracilar.OrderBy(k => k.Ad)
        .Select(k => new { k.Id, k.Ad, k.Slug, k.SektorPaketi, k.BirimAdi })
        .ToListAsync());

// ---- Çalışanlar ------------------------------------------------------------
app.MapGet("/api/v1/employees", async (TShiftDbContext db, IKiraciBaglami baglam) =>
{
    if (baglam.KiraciId is null)
        return Results.BadRequest(new { mesaj = "X-Tenant-Id başlığı gerekli." });

    var liste = await db.Calisanlar
        .OrderBy(c => c.Ad).ThenBy(c => c.Soyad)
        .Select(c => new
        {
            c.Id, c.PersonelNo, c.Ad, c.Soyad,
            TamAd = c.Ad + " " + c.Soyad,
            c.Eposta, c.DepartmanId, c.BirincilEkipId, c.Durum, c.KiraciId
        })
        .ToListAsync();

    return Results.Ok(new { kiraciId = baglam.KiraciId, adet = liste.Count, kayitlar = liste });
});

app.Run();
