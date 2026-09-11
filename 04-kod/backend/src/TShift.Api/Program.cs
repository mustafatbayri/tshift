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
using TShift.Api;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Yetki;
using TShift.Infrastructure.Denetim;
using TShift.Domain.Denetim;

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
builder.Services.AddScoped<IYetkiCozucu, YetkiCozucu>();
builder.Services.AddScoped<IKiraciKurulumServisi, KiraciKurulumServisi>();

builder.Services.AddScoped<IKiraciBaglami, KiraciBaglami>();
builder.Services.AddScoped<IDenetimBaglami, DenetimBaglami>();
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
        // Jetondaki talep adlarına DOKUNMA.
        //
        // Varsayılan davranış, gelen jetonun standart taleplerini eski
        // Microsoft/WS-Federation şemalarına çevirir: `sub` talebi
        // `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier`
        // adını alır. Sonuç: jeton geçerlidir, kullanıcı doğrulanmıştır, ama
        // kodda `FindFirstValue("sub")` diye arayınca null gelir ve uç sessizce
        // "yetkisiz" der. Hata mesajı da yanıltıcıdır — sorun kimlikte değil,
        // isimlendirmede.
        //
        // Kapatıyoruz: jetona ne yazdıysak onu okuyoruz.
        o.MapInboundClaims = false;

        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = kimlikAyarlari.Yayinci,
            ValidateAudience = true,
            ValidAudience = kimlikAyarlari.Hedef,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(imzaAnahtari)),
            ValidateLifetime = true,
            NameClaimType = System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub,
            // Varsayılan 5 dakikalık tolerans, 15 dakikalık jetonu 20 dakika
            // yaşatır. Süre gerçekten süre olsun.
            ClockSkew = TimeSpan.Zero
        };
    });

// Her izin kodu için bir politika. Uçlar `.RequireAuthorization("plan.uret")`
// diyerek korunur; yetki kontrolü tek yerde, uç kodunun içinde dağınık
// `if (yetkisi var mi)` kontrolleri olmadan yapılır.
builder.Services.AddAuthorization(o =>
{
    foreach (var izin in YetkiKatalogu.Izinler)
        o.AddPolicy(izin.Kod, p => p.RequireClaim(JetonServisi.IzinTalebi, izin.Kod));
});
builder.Services.AddProblemDetails();

var app = builder.Build();

// Kutu içi inceleme kurulumu. Ortam değişkeni AÇIKÇA verilmediği sürece
// hiçbir şey yapmaz. Canlıda kapalı kalmalı — bkz. KurulumHizmeti.
if (Environment.GetEnvironmentVariable("TSHIFT_KURULUM") == "true")
    await KurulumHizmeti.CalistirAsync(app);

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
    if (ctx.User.Identity?.IsAuthenticated == true)
    {
        var hamKiraci = ctx.User.FindFirstValue(JetonServisi.KiraciTalebi);
        if (Guid.TryParse(hamKiraci, out var kid))
            ctx.RequestServices.GetRequiredService<IKiraciBaglami>().Ayarla(kid);

        // "Bu işi kim yaptı" bilgisi de aynı jetondan gelir. Denetim kaydına
        // yazılacak; istemcinin söylediğine değil, imzalı jetona güveniyoruz.
        var hamKullanici = ctx.User.FindFirstValue(
            System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub);
        if (Guid.TryParse(hamKullanici, out var uid))
            ctx.RequestServices.GetRequiredService<IDenetimBaglami>().Ayarla(
                uid,
                ctx.Connection.RemoteIpAddress?.ToString(),
                ctx.Request.Headers.UserAgent.ToString());
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

app.MapGet("/api/v1/me", async (TShiftDbContext db, IYetkiCozucu yetkiler, HttpContext ctx) =>
{
    var kid = ctx.User.FindFirstValue(System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub);
    if (!Guid.TryParse(kid, out var kullaniciId)) return Results.Unauthorized();

    var k = await db.Kullanicilar
        .Where(x => x.Id == kullaniciId)
        .Select(x => new { x.Id, x.Ad, x.Soyad, x.Eposta, x.KiraciId, x.SonGiris, x.Durum })
        .FirstOrDefaultAsync();

    if (k is null) return Results.Unauthorized();

    // Arayüz hangi menüyü göstereceğini buradan öğrenir. Gizleme bir güvenlik
    // önlemi değildir — asıl kontrol sunucuda; bu yalnız kullanıcıya
    // yapamayacağı düğmeleri göstermemek için.
    var y = await yetkiler.CozAsync(kullaniciId);

    return Results.Ok(new
    {
        k.Id, k.Ad, k.Soyad, k.Eposta, k.KiraciId, k.SonGiris, k.Durum,
        kapsam = y.Seviye.ToString(),
        izinler = y.Izinler.OrderBy(i => i).ToArray(),
        departmanSayisi = y.DepartmanIds.Count,
        ekipSayisi = y.EkipIds.Count
    });
}).RequireAuthorization();

// ---- Geliştirme: örnek veri ------------------------------------------------
// İKİ kiracı oluşturur. Amaç: çok kiracılık yalıtımını gözle görebilmek.
// ---- Geliştirme uçları -----------------------------------------------------
// KOŞULLU. Bu uçlar kimlik doğrulaması istemez: /dev/tenants sistemdeki tüm
// firmaları listeler, /dev/seed veri yazar. Yanlışlıkla canlıya çıkarlarsa
// müşteri listesi dışarı açılmış olur.
//
// Yalnızca geliştirme ortamında ya da TSHIFT_KURULUM açıkken haritalanıyorlar;
// ikisi de "bu ortam tek kullanımlık" demek. Sürüm öncesi tamamen silinecekler.
var gelistirmeUclari = app.Environment.IsDevelopment()
    || Environment.GetEnvironmentVariable("TSHIFT_KURULUM") == "true";

if (gelistirmeUclari)
{
    app.MapPost("/dev/seed", async (TShiftDbContext db, IServiceProvider saglayici) =>
    {
        if (await db.Kiracilar.AnyAsync())
            return Results.Conflict(new { mesaj = "Örnek veri zaten var. Sıfırlamak için: docker compose down -v" });

        var sonuc = await OrnekVeri.KurAsync(saglayici);
        return Results.Ok(new { mesaj = "Örnek veri oluşturuldu", parola = OrnekVeri.Parola, kiracilar = sonuc });
    });

    // Kiracı listesi — kiracı tablosu filtreye tabi değil (yönetim ucu, sürüm öncesi silinecek).
    app.MapGet("/dev/tenants", async (TShiftDbContext db) =>
        await db.Kiracilar.OrderBy(k => k.Ad)
            .Select(k => new { k.Id, k.Ad, k.Slug, k.SektorPaketi, k.BirimAdi })
            .ToListAsync());
}

// ---- Organizasyon ----------------------------------------------------------
// Yeni çalışan formunun ihtiyaç duyduğu seçenekler. Kapsama göre filtreli:
// kullanıcı, göremeyeceği bir departmanı seçenek olarak da görmemeli.
app.MapGet("/api/v1/departments", async (TShiftDbContext db, IYetkiCozucu yetkiler, HttpContext ctx) =>
{
    var yetki = await ctx.YetkiAl(yetkiler);
    if (yetki is null) return Results.Unauthorized();

    var sorgu = db.Departmanlar.AsNoTracking().AsQueryable();

    if (yetki.Seviye == KapsamSeviyesi.Kapsam)
    {
        // Doğrudan kapsamdaki departmanlar + kapsamdaki ekiplerin departmanları.
        var ekipDepartmanlari = db.Ekipler
            .Where(e => yetki.EkipIds.Contains(e.Id))
            .Select(e => e.DepartmanId);

        sorgu = sorgu.Where(d => yetki.DepartmanIds.Contains(d.Id)
                              || ekipDepartmanlari.Contains(d.Id));
    }
    else if (yetki.Seviye == KapsamSeviyesi.Kendi)
    {
        var kendiDepartman = db.Calisanlar
            .Where(c => c.Id == yetki.CalisanId)
            .Select(c => c.DepartmanId);
        sorgu = sorgu.Where(d => kendiDepartman.Contains(d.Id));
    }

    var liste = await sorgu.OrderBy(d => d.Ad)
        .Select(d => new { d.Id, d.Ad, d.Kod })
        .ToListAsync();

    return Results.Ok(liste);
}).RequireAuthorization(YetkiKatalogu.CalisanGor);

app.MapGet("/api/v1/teams", async (TShiftDbContext db, IYetkiCozucu yetkiler, HttpContext ctx,
    Guid? departmanId) =>
{
    var yetki = await ctx.YetkiAl(yetkiler);
    if (yetki is null) return Results.Unauthorized();

    var sorgu = db.Ekipler.AsNoTracking().AsQueryable();
    if (departmanId is { } d) sorgu = sorgu.Where(e => e.DepartmanId == d);

    if (yetki.Seviye == KapsamSeviyesi.Kapsam)
        sorgu = sorgu.Where(e => yetki.EkipIds.Contains(e.Id)
                              || yetki.DepartmanIds.Contains(e.DepartmanId));
    else if (yetki.Seviye == KapsamSeviyesi.Kendi)
        sorgu = sorgu.Where(e => false);

    var liste = await sorgu.OrderBy(e => e.Ad)
        .Select(e => new { e.Id, e.Ad, e.Kod, e.DepartmanId })
        .ToListAsync();

    return Results.Ok(liste);
}).RequireAuthorization(YetkiKatalogu.CalisanGor);

// ---- Denetim kaydı ---------------------------------------------------------
// Salt okunur. Bu uçtan hiçbir şey silinemez ya da değiştirilemez — zaten
// veritabanı seviyesinde de uygulama rolünün böyle bir yetkisi yok.
app.MapGet("/api/v1/audit", async (TShiftDbContext db,
    string? varlik, Guid? varlikId, Guid? kullaniciId, int sayfa = 1, int boyut = 50) =>
{
    boyut = Math.Clamp(boyut, 1, 200);
    sayfa = Math.Max(sayfa, 1);

    var sorgu = db.DenetimKayitlari.AsNoTracking().AsQueryable();

    if (!string.IsNullOrWhiteSpace(varlik)) sorgu = sorgu.Where(k => k.Varlik == varlik);
    if (varlikId is { } vid)                sorgu = sorgu.Where(k => k.VarlikId == vid);
    if (kullaniciId is { } uid)             sorgu = sorgu.Where(k => k.KullaniciId == uid);

    var toplam = await sorgu.CountAsync();
    var kayitlar = await sorgu
        .OrderByDescending(k => k.Zaman)
        .Skip((sayfa - 1) * boyut).Take(boyut)
        .Select(k => new
        {
            k.Id, k.Zaman, k.KullaniciId, k.Varlik, k.VarlikId,
            islem = k.Islem.ToString(), k.Oncesi, k.Sonrasi, k.Ip
        })
        .ToListAsync();

    return Results.Ok(new { toplam, sayfa, boyut, kayitlar });
}).RequireAuthorization(YetkiKatalogu.DenetimGor);

// ---- Çalışanlar ------------------------------------------------------------
app.MapGet("/api/v1/employees", async (TShiftDbContext db, IKiraciBaglami baglam,
    IYetkiCozucu yetkiler, HttpContext ctx) =>
{
    // İzin kontrolünü politika yaptı ("bu kişi çalışan görebilir mi").
    // Burada kapsam uygulanıyor ("hangi çalışanları görebilir").
    var yetki = await ctx.YetkiAl(yetkiler);
    if (yetki is null) return Results.Unauthorized();

    var liste = await db.Calisanlar
        .KapsamUygula(yetki)
        .OrderBy(c => c.Ad).ThenBy(c => c.Soyad)
        .Select(c => new
        {
            c.Id, c.PersonelNo, c.Ad, c.Soyad,
            TamAd = c.Ad + " " + c.Soyad,
            c.Eposta, c.DepartmanId, c.BirincilEkipId, c.Durum, c.KiraciId
        })
        .ToListAsync();

    return Results.Ok(new
    {
        kiraciId = baglam.KiraciId,
        kapsam = yetki.Seviye.ToString(),
        adet = liste.Count,
        kayitlar = liste
    });
}).RequireAuthorization(YetkiKatalogu.CalisanGor);

app.MapPost("/api/v1/employees", async (YeniCalisan istek, TShiftDbContext db,
    IYetkiCozucu yetkiler, HttpContext ctx) =>
{
    var yetki = await ctx.YetkiAl(yetkiler);
    if (yetki is null) return Results.Unauthorized();

    var personelNo = istek.PersonelNo?.Trim() ?? "";
    var ad = istek.Ad?.Trim() ?? "";
    var soyad = istek.Soyad?.Trim() ?? "";

    if (personelNo.Length == 0 || ad.Length == 0 || soyad.Length == 0)
        return Hata422("EKSIK_ALAN", "Personel no, ad ve soyad zorunlu.");

    // Departman gerçekten bu kiracıya ait mi? Sorgu filtresi + RLS zaten
    // başka kiracının departmanını getirmez; burada VARLIĞINI doğruluyoruz.
    var departmanVar = await db.Departmanlar.AnyAsync(d => d.Id == istek.DepartmanId);
    if (!departmanVar)
        return Hata422("DEPARTMAN_YOK", "Secilen departman bulunamadi.");

    if (istek.BirincilEkipId is { } ekipId)
    {
        var ekipUygun = await db.Ekipler.AnyAsync(e => e.Id == ekipId && e.DepartmanId == istek.DepartmanId);
        if (!ekipUygun)
            return Hata422("EKIP_UYUMSUZ", "Secilen ekip bu departmana ait degil.");
    }

    var calisan = new Calisan
    {
        PersonelNo = personelNo,
        Ad = ad,
        Soyad = soyad,
        Eposta = string.IsNullOrWhiteSpace(istek.Eposta) ? null : istek.Eposta.Trim(),
        Telefon = string.IsNullOrWhiteSpace(istek.Telefon) ? null : istek.Telefon.Trim(),
        DepartmanId = istek.DepartmanId,
        BirincilEkipId = istek.BirincilEkipId,
        IseGiris = istek.IseGiris ?? DateOnly.FromDateTime(DateTime.UtcNow),
        Durum = CalisanDurumu.Aktif
    };

    // "Goremeyecegin kaydi olusturamazsin." Listeyi filtreleyen kuralin AYNISI
    // burada tek kayda uygulaniyor — ikisi tek ifadeden turuyor, ayrisamazlar.
    if (!calisan.Kapsamda(yetki))
        return Results.Json(
            new { kod = "KAPSAM_DISI", mesaj = "Bu departman/ekip senin kapsaminin disinda." },
            statusCode: StatusCodes.Status403Forbidden);

    db.Calisanlar.Add(calisan);

    try
    {
        await db.SaveChangesAsync();
    }
    catch (DbUpdateException e) when (e.InnerException is Npgsql.PostgresException { SqlState: "23505" })
    {
        // Benzersizlik kisiti veritabaninda. Once sorgulayip sonra yazmak
        // yeterli degil: iki istek ayni anda gelirse ikisi de "yok" gorur.
        // Asil koruma burada, kontrol degil kisit.
        return Results.Json(
            new { kod = "PERSONEL_NO_TEKRAR", mesaj = $"'{personelNo}' zaten kayitli." },
            statusCode: StatusCodes.Status409Conflict);
    }

    return Results.Created($"/api/v1/employees/{calisan.Id}", new
    {
        calisan.Id, calisan.PersonelNo, calisan.Ad, calisan.Soyad,
        TamAd = calisan.TamAd, calisan.Eposta,
        calisan.DepartmanId, calisan.BirincilEkipId, calisan.Durum
    });
}).RequireAuthorization(YetkiKatalogu.CalisanDuzenle);

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

static IResult Hata422(string kod, string mesaj) =>
    Results.Json(new { kod, mesaj }, statusCode: StatusCodes.Status422UnprocessableEntity);

/// <summary>
/// Jetondaki kullanıcı kimliğinden yetkiyi çözer. Dört uçta aynı üç satırı
/// tekrarlamak yerine tek yerde.
/// </summary>
internal static class YetkiUzantisi
{
    public static async Task<KullaniciYetkisi?> YetkiAl(this HttpContext ctx, IYetkiCozucu yetkiler)
    {
        var ham = ctx.User.FindFirstValue(
            System.IdentityModel.Tokens.Jwt.JwtRegisteredClaimNames.Sub);
        return Guid.TryParse(ham, out var id) ? await yetkiler.CozAsync(id) : null;
    }
}

public sealed record GirisIstegi(string Firma, string Eposta, string Parola);
public sealed record YeniCalisan(
    string? PersonelNo, string? Ad, string? Soyad,
    string? Eposta, string? Telefon,
    Guid DepartmanId, Guid? BirincilEkipId, DateOnly? IseGiris);
public sealed record YenilemeIstegi(string YenilemeJetonu);

/// <summary>
/// Testlerin uygulamayı bellek içinde ayağa kaldırabilmesi için.
///
/// Üst düzey deyimlerle yazılan bir Program sınıfı varsayılan olarak
/// `internal`dir; WebApplicationFactory ona ulaşamaz. Bu boş kısmi sınıf
/// yalnızca görünürlüğü açar, başka hiçbir şey yapmaz.
/// </summary>
public partial class Program { }
