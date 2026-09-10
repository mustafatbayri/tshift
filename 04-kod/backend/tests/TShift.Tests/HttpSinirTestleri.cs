using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using TShift.Domain.Calisanlar;
using TShift.Domain.Kimlik;
using TShift.Domain.Kiracilar;
using TShift.Domain.Organizasyon;
using TShift.Domain.Yetki;
using TShift.Infrastructure.Kimlik;
using TShift.Infrastructure.Persistence;
using TShift.Infrastructure.Yetki;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// HTTP SINIRI TESTLERİ — uygulamayı gerçekten ayağa kaldırıp gerçek istek atar.
///
/// NEDEN AYRI BİR TEST SINIFI:
/// Diğer testler servisleri doğrudan çağırır ve iç mantığın doğruluğunu sınar.
/// Ama bir hata **katmanların arasında** olabilir: mantık kusursuz çalışırken
/// jetondaki bir talebin adı beklenenden farklı olduğu için her istek reddedilir.
///
/// Bu tam olarak 10 Eylül'de başımıza geldi: 21 test yeşilken korumalı bütün
/// uçlar 401 dönüyordu. JwtBearer, gelen jetonun `sub` talebini eski Microsoft
/// şemasına çeviriyordu; kod ise `sub` diye arıyordu. Yetki mantığı doğruydu,
/// kırılan şey iki katmanın buluştuğu yerdi — ve oraya hiçbir test bakmıyordu.
///
/// Birim testi katmanın İÇİNİ, bu testler katmanların ARASINI doğrular.
/// İkisi birbirinin yerine geçmez.
/// </summary>
public class HttpSinirTestleri : IClassFixture<TestUygulamasi>
{
    private readonly TestUygulamasi _uygulama;

    public HttpSinirTestleri(TestUygulamasi uygulama) => _uygulama = uygulama;

    private const string Baglanti =
        "Host=localhost;Port=5433;Database=tshift;Username=tshift_app;Password=tshift_app_dev_2026";
    private const string Parola = "Http-Sinir-Testi-2026!";

    private static TShiftDbContext Baglam(IKiraciBaglami b)
    {
        var opt = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(Baglanti)
            .AddInterceptors(new KiraciBaglantiKesici(b))
            .Options;
        return new TShiftDbContext(opt, b);
    }

    private sealed record Sahne(Guid KiraciId, string Slug, string MudurEposta, string SefEposta,
        string RolsuzEposta, Guid GunduzCalisanId, Guid GeceCalisanId);

    private static async Task<Sahne> SahneKur(string ek)
    {
        var b = new KiraciBaglami();
        b.Ayarla(null);
        await using var db = Baglam(b);

        var slug = $"http-{ek}";
        var kiraci = new Kiraci { Ad = $"Http {ek}", Slug = slug, Durum = KiraciDurumu.Aktif };
        db.Kiracilar.Add(kiraci);
        await db.SaveChangesAsync();

        b.Ayarla(kiraci.Id);
        var kurulum = new KiraciKurulumServisi(db);
        await kurulum.SistemRolleriniKurAsync(kiraci.Id);

        var dep = new Departman { Ad = "Ops", Kod = $"OPS-{ek}", CalismaTipi = CalismaTipi.Saatli };
        db.Departmanlar.Add(dep);
        await db.SaveChangesAsync();

        var gunduz = new Ekip { DepartmanId = dep.Id, Ad = "Gunduz", Kod = $"G-{ek}" };
        var gece = new Ekip { DepartmanId = dep.Id, Ad = "Gece", Kod = $"C-{ek}" };
        db.Ekipler.AddRange(gunduz, gece);
        await db.SaveChangesAsync();

        var c1 = new Calisan { PersonelNo = $"H1-{ek}", Ad = "Gunduzcu", Soyad = "Test",
            DepartmanId = dep.Id, BirincilEkipId = gunduz.Id, IseGiris = new DateOnly(2025, 1, 1) };
        var c2 = new Calisan { PersonelNo = $"H2-{ek}", Ad = "Gececi", Soyad = "Test",
            DepartmanId = dep.Id, BirincilEkipId = gece.Id, IseGiris = new DateOnly(2025, 1, 1) };
        db.Calisanlar.AddRange(c1, c2);
        await db.SaveChangesAsync();

        var parolalar = new ParolaServisi();
        async Task<Guid> Kul(string onek, string? rol)
        {
            var u = new Kullanici
            {
                Ad = onek, Soyad = "Test", Eposta = $"{onek}@{slug}.test",
                EpostaDogrulandi = true, Durum = KullaniciDurumu.Aktif
            };
            db.Kullanicilar.Add(u);
            await db.SaveChangesAsync();

            db.KullaniciKimlikBilgileri.Add(new KullaniciKimlikBilgisi
            {
                KullaniciId = u.Id, SifreHash = parolalar.Ozetle(Parola)
            });
            await db.SaveChangesAsync();

            if (rol is not null) await kurulum.RolAtaAsync(u.Id, rol);
            return u.Id;
        }

        await Kul("mudur", YetkiKatalogu.KiraciYonetici);
        var sefId = await Kul("sef", YetkiKatalogu.Sef);
        await kurulum.KapsamEkleAsync(sefId, KapsamTipi.Ekip, gunduz.Id);
        await Kul("rolsuz", null);   // giris yapabilir ama hicbir izni yok

        return new Sahne(kiraci.Id, slug, $"mudur@{slug}.test", $"sef@{slug}.test",
            $"rolsuz@{slug}.test", c1.Id, c2.Id);
    }

    // Bu sinifta yalnizca BASARILI girisler var; kaba kuvvet sayaci
    // yalnizca basarisiz denemeleri sayar, o yuzden login_attempts temizligi
    // gerekmiyor.
    private static Task Temizle(Guid kiraciId)
        => TestTemizlik.KiraciSilAsync(kiraciId);

    private async Task<(HttpStatusCode Kod, JsonElement Govde)> Cagir(
        HttpClient istemci, string yol, string? jeton = null, string? sahteKiraci = null)
    {
        var istek = new HttpRequestMessage(HttpMethod.Get, yol);
        if (jeton is not null)
            istek.Headers.Authorization = new AuthenticationHeaderValue("Bearer", jeton);
        if (sahteKiraci is not null)
            istek.Headers.Add("X-Tenant-Id", sahteKiraci);

        var cevap = await istemci.SendAsync(istek);
        var metin = await cevap.Content.ReadAsStringAsync();
        var govde = string.IsNullOrWhiteSpace(metin)
            ? default
            : JsonDocument.Parse(metin).RootElement.Clone();
        return (cevap.StatusCode, govde);
    }

    private async Task<string?> GirisAsync(HttpClient istemci, string firma, string eposta)
    {
        var cevap = await istemci.PostAsJsonAsync("/api/v1/auth/login",
            new { firma, eposta, parola = Parola });
        if (!cevap.IsSuccessStatusCode) return null;

        var govde = JsonDocument.Parse(await cevap.Content.ReadAsStringAsync()).RootElement;
        return govde.GetProperty("erisimJetonu").GetString();
    }

    // ------------------------------------------------------------------ H1
    /// <summary>
    /// 10 Eylül hatasının bekçisi. Jetonla /me çağrılabilmeli ve dönen kimlik
    /// giriş yapan kullanıcının kimliği olmalı. `sub` talebi yeniden
    /// adlandırılırsa burası anında kırmızı yanar.
    /// </summary>
    [Fact(DisplayName = "H1 - Jetonla /me calisir ve dogru kullaniciyi doner")]
    public async Task Me_calisir()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        var istemci = _uygulama.CreateClient();
        try
        {
            var jeton = await GirisAsync(istemci, s.Slug, s.MudurEposta);
            Assert.NotNull(jeton);

            var (kod, govde) = await Cagir(istemci, "/api/v1/me", jeton);

            Assert.Equal(HttpStatusCode.OK, kod);
            Assert.Equal(s.MudurEposta, govde.GetProperty("eposta").GetString());
            Assert.Equal("Kiraci", govde.GetProperty("kapsam").GetString());
            // Sayiyi elle yazmiyoruz: katalog degisince test de kendiliginden guncellenir.
            var beklenen = YetkiKatalogu.Roller.First(r => r.Kod == YetkiKatalogu.KiraciYonetici).Izinler.Length;
            Assert.Equal(beklenen, govde.GetProperty("izinler").GetArrayLength());
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ H2
    [Fact(DisplayName = "H2 - Jetonsuz istek 401")]
    public async Task Jetonsuz_401()
    {
        var istemci = _uygulama.CreateClient();
        var (kod, _) = await Cagir(istemci, "/api/v1/employees");
        Assert.Equal(HttpStatusCode.Unauthorized, kod);
    }

    // ------------------------------------------------------------------ H3
    /// <summary>
    /// 401 ile 403 farkı önemli: 401 "kim olduğunu bilmiyorum", 403 "kim
    /// olduğunu biliyorum ama bunu yapamazsın". Rolsüz kullanıcı 403 almalı.
    /// Eğer 401 alıyorsak jeton doğrulanamıyor demektir — bambaşka bir sorun.
    /// </summary>
    [Fact(DisplayName = "H3 - Izni olmayan kullanici 403 alir, 401 degil")]
    public async Task Izinsiz_403()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        var istemci = _uygulama.CreateClient();
        try
        {
            var jeton = await GirisAsync(istemci, s.Slug, s.RolsuzEposta);
            Assert.NotNull(jeton);

            var (kod, _) = await Cagir(istemci, "/api/v1/employees", jeton);
            Assert.Equal(HttpStatusCode.Forbidden, kod);
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ H4
    [Fact(DisplayName = "H4 - Sef HTTP uzerinden de yalniz kendi ekibini gorur")]
    public async Task Sef_kapsami_http_uzerinden()
    {
        var s = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        var istemci = _uygulama.CreateClient();
        try
        {
            var jeton = await GirisAsync(istemci, s.Slug, s.SefEposta);
            var (kod, govde) = await Cagir(istemci, "/api/v1/employees", jeton);

            Assert.Equal(HttpStatusCode.OK, kod);
            Assert.Equal("Kapsam", govde.GetProperty("kapsam").GetString());
            Assert.Equal(1, govde.GetProperty("adet").GetInt32());
            Assert.Equal(s.GunduzCalisanId,
                govde.GetProperty("kayitlar")[0].GetProperty("id").GetGuid());
        }
        finally { await Temizle(s.KiraciId); }
    }

    // ------------------------------------------------------------------ H5
    /// <summary>
    /// Eski açığın bekçisi: kiracı kimliği başlıktan okunuyordu.
    /// Başlık hâlâ gönderilebilir; artık hiçbir etkisi olmamalı.
    /// </summary>
    [Fact(DisplayName = "H5 - Sahte X-Tenant-Id basligi hicbir sey degistirmez")]
    public async Task Sahte_baslik_etkisiz()
    {
        var a = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        var b = await SahneKur(Guid.NewGuid().ToString("N")[..6]);
        var istemci = _uygulama.CreateClient();
        try
        {
            var jeton = await GirisAsync(istemci, a.Slug, a.MudurEposta);

            var (kod, govde) = await Cagir(istemci, "/api/v1/employees", jeton,
                sahteKiraci: b.KiraciId.ToString());

            Assert.Equal(HttpStatusCode.OK, kod);
            Assert.Equal(a.KiraciId, govde.GetProperty("kiraciId").GetGuid());
            Assert.Equal(2, govde.GetProperty("adet").GetInt32());
        }
        finally { await Temizle(a.KiraciId); await Temizle(b.KiraciId); }
    }
}
