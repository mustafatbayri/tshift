using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using TShift.Domain.Calisanlar;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Infrastructure.Kimlik;
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

// ---- Kimlik ayarları -------------------------------------------------------
// JWT imza anahtarı da bir sırdır ve aynı kurala tabidir.
// Canlıda JWT_SECRET mutlaka verilir; aşağıdaki değer yalnız yerel geliştirme içindir.
var imzaAnahtari = Environment.GetEnvironmentVariable("JWT_SECRET")
    ?? "yerel-gelistirme-imza-anahtari-en-az-32-bayt-olmali!";

var kimlikAyarlari = new KimlikAyarlari { ImzaAnahtari = imzaAnahtari };

builder.Services.AddSingleton(kimlikAyarlari);
builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<IParolaServisi, ParolaServisi>();
builder.Services.AddSingleton<IJetonServisi, JetonServisi>();
builder.Services.AddScoped<IKimlikServisi, KimlikServisi>();

builder.Services.AddScoped<IKiraciBaglami, KiraciBaglami>();
builder.Services.AddScoped<KiraciBaglantiKesici>();

builder.Services.AddDbContext<TShiftDbContext>((sp, opt) =>
{
    opt.UseNpgsql(baglantiDizesi);
    opt.AddInterceptors(sp.GetRequiredService<KiraciBaglantiKesici>());
    if (builder.Environment.IsDevelopment()) opt.EnableSensitiveDataLogging();
});

// ---- JWT doğrulama ---------------------------------------------------------
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = kimlikAyarlari.Yayinci,
            ValidateAudience = true,
            ValidAudience = kimlikAyarlari.Hedef,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(imzaAnahtari)),
            ValidateLifetime = true,
            // Varsayılan 5 dakikalık tolerans, 15 dakikalık jetonu 20 dakika
            // yaşatır. Süre gerçekten süre olsun.
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();
builder.Services.AddProblemDetails();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

// ---- Kiracı bağlamı --------------------------------------------------------
// Kiracı kimliği İMZALI JETONDAN okunur. Spec §10: "tenant_id token'dan okunur,
// istekten değil."
//
// Eskiden burada X-Tenant-Id başlığı okunuyordu ve bu, kimlik katmanı gelene
// kadar bilerek kabul edilmiş geçici bir açıktı: başlığı isteyen istediği gibi
// yazabilir. Artık kiracı, sunucunun imzaladığı ve kullanıcının değiştiremediği
// bir jetondan geliyor.
app.Use(async (ctx, next) =>
{
    var ham = ctx.User.FindFirstValue(JetonServisi.KiraciTalebi);
    if (ctx.User.Identity?.IsAuthenticated == true && Guid.TryParse(ham, out var kid))
        ctx.RequestServices.GetRequiredService<IKiraciBaglami>().Ayarla(kid);

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

// ---- Kimlik ---------------------------------------------------------------
// Not: giriş isteği firma kısa adını da taşır. Sebebi veri modeli: e-posta
// (kiraci_id, eposta) çifti içinde benzersiz, tek başına değil. Aynı kişi iki
// ayrı firmada kullanıcı olabilir. Canlıda bu değer alt alan adından
// (anadolu-cm.tshift.com) gelecek ve kullanıcı hiç yazmayacak.
app.MapPost("/api/v1/auth/login", async (GirisIstegi istek, IKimlikServisi kimlik, HttpContext ctx) =>
{
    var sonuc = await kimlik.GirisAsync(
        istek.Firma, istek.Eposta, istek.Parola,
        ctx.Connection.RemoteIpAddress?.ToString(),
        ctx.Request.Headers.UserAgent.ToString());

    return sonuc.Basarili ? Results.Ok(Cevap(sonuc)) : Hata(sonuc.Hata);
});

app.MapPost("/api/v1/auth/refresh", async (YenilemeIstegi istek, IKimlikServisi kimlik, HttpContext ctx) =>
{
    var sonuc = await kimlik.YenileAsync(
        istek.YenilemeJetonu,
        ctx.Connection.RemoteIpAddress?.ToString(),
        ctx.Request.Headers.UserAgent.ToString());

    return sonuc.Basarili ? Results.Ok(Cevap(sonuc)) : Hata(sonuc.Hata);
});

app.MapPost("/api/v1/auth/logout", async (YenilemeIstegi istek, IKimlikServisi kimlik) =>
{
    await kimlik.CikisAsync(istek.YenilemeJetonu);
    // Çıkış her zaman başarılı görünür: "bu jeton geçerli miydi" bilgisi
    // dışarıya verilmez.
    return Results.Ok(new { mesaj = "Cikis yapildi." });
});

app.MapGet("/api/v1/me", async (TShiftDbContext db, HttpContext ctx) =>
{
    var kid = ctx.User.FindFirstValue(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub);
    if (!Guid.TryParse(kid, out var kullaniciId)) return Results.Unauthorized();

    var k = await db.Kullanicilar
        .Where(x => x.Id == kullaniciId)
        .Select(x => new { x.Id, x.Ad, x.Soyad, x.Eposta, x.KiraciId, x.SonGiris, x.Durum })
        .FirstOrDefaultAsync();

    return k is null ? Results.Unauthorized() : Results.Ok(k);
}).RequireAuthorization();

// ---- Geliştirme: örnek veri ------------------------------------------------
// İKİ kiracı oluşturur. Amaç: çok kiracılık yalıtımını gözle görebilmek.
app.MapPost("/dev/seed", async (TShiftDbContext db, IKiraciBaglami baglam, IParolaServisi parolalar) =>
{
    if (await db.Kiracilar.AnyAsync())
        return Results.Conflict(new { mesaj = "Örnek veri zaten var. Sıfırlamak için: docker compose down -v" });

    const string ornekParola = "TShift2026!Deneme";
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

        var yonetici = new Kullanici
        {
            Ad = "Murat", Soyad = "Kaya", Eposta = $"mudur@{slug}.test",
            EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
        };
        db.Kullanicilar.Add(yonetici);
        await db.SaveChangesAsync();

        // Parola ayrı tabloda ve özetlenmiş olarak durur.
        db.KullaniciKimlikBilgileri.Add(new KullaniciKimlikBilgisi
        {
            KullaniciId = yonetici.Id,
            SifreHash = parolalar.Ozetle(ornekParola)
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

        sonuc.Add(new { kiraci = ad, firma = slug, id = kiraci.Id, eposta = yonetici.Eposta, calisan = kisiler.Length });
    }

    baglam.Ayarla(null);
    return Results.Ok(new { mesaj = "Örnek veri oluşturuldu", parola = ornekParola, kiracilar = sonuc });
});

// Kiracı listesi — kiracı tablosu filtreye tabi değil (yönetim ucu, sürüm öncesi silinecek).
app.MapGet("/dev/tenants", async (TShiftDbContext db) =>
    await db.Kiracilar.OrderBy(k => k.Ad)
        .Select(k => new { k.Id, k.Ad, k.Slug, k.SektorPaketi, k.BirimAdi })
        .ToListAsync());

// ---- Çalışanlar ------------------------------------------------------------
app.MapGet("/api/v1/employees", async (TShiftDbContext db, IKiraciBaglami baglam) =>
{
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
}).RequireAuthorization();

app.Run();

// ---- Yardımcılar -----------------------------------------------------------
static object Cevap(OturumSonucu s) => new
{
    erisimJetonu = s.ErisimJetonu,
    yenilemeJetonu = s.YenilemeJetonu,
    bitis = s.ErisimBitis,
    kullaniciId = s.KullaniciId,
    kiraciId = s.KiraciId,
    zorunluParolaDegisimi = s.ZorunluParolaDegisimi
};

// Hata kodları kasten kaba: "e-posta yok" ile "parola yanlış" ayrımı dışarı
// verilmez, yoksa saldırgan hangi e-postaların kayıtlı olduğunu öğrenir.
static IResult Hata(KimlikHatasi h) => h switch
{
    KimlikHatasi.Kilitli => Results.Json(
        new { kod = "COK_FAZLA_DENEME", mesaj = "Cok fazla basarisiz deneme. Bir sure sonra tekrar deneyin." },
        statusCode: StatusCodes.Status429TooManyRequests),

    KimlikHatasi.JetonYenidenKullanildi => Results.Json(
        new { kod = "OTURUM_GUVENLIGI", mesaj = "Oturum guvenligi nedeniyle tum oturumlar kapatildi. Tekrar giris yapin." },
        statusCode: StatusCodes.Status401Unauthorized),

    KimlikHatasi.HesapPasif => Results.Json(
        new { kod = "HESAP_PASIF", mesaj = "Hesap aktif degil." },
        statusCode: StatusCodes.Status403Forbidden),

    _ => Results.Json(
        new { kod = "KIMLIK_GECERSIZ", mesaj = "Firma, e-posta veya parola hatali." },
        statusCode: StatusCodes.Status401Unauthorized)
};

public sealed record GirisIstegi(string Firma, string Eposta, string Parola);
public sealed record YenilemeIstegi(string YenilemeJetonu);
