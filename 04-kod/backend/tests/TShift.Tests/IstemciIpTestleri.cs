using Microsoft.EntityFrameworkCore;
using System.Net.Http.Json;
using TShift.Infrastructure.Persistence;
using Xunit;

namespace TShift.Tests;

/// <summary>
/// İSTEMCİ IP TESTLERİ — API, kullanıcının gerçek IP'sini görüyor mu (T-35).
///
/// NEDEN HTTP SEVİYESİNDE:
/// Kusur mantıkta değil, KATMANLARIN ARASINDA. `KimlikServisi.GirisAsync`
/// kendisine verilen IP'yi doğru kullanıyor; sorun `Program.cs`'in ona
/// `ctx.Connection.RemoteIpAddress` vermesi. Tarayıcı API'ye doğrudan
/// gitmiyor, Next.js üzerinden geçiyor — dolayısıyla o adres HER ZAMAN
/// ön yüzün adresi. Servisi doğrudan çağıran bir test bunu göremez.
///
/// NE KADAR CİDDİ (ölçüldü, 23 Eylül):
/// `KilitliMi` sorgusunda kiracı filtresi YOK ve olmaması bilinçli (M-13:
/// sayaç kiracı bilinmeden yazılmalı, yoksa saldırgan uydurma firma adıyla
/// kilidi atlar). Bütün istekler tek IP'den geliyor gibi görününce:
///
///     Herhangi bir kiracıda, herhangi biri, 15 dakikada 5 kez yanlış
///     parola girerse -> KURULUMDAKİ HERKES 15 dakika giremez.
///
/// Şartname (§ satır 1403) *"aynı e-posta veya IP için 5 başarısız denemede
/// 15 dakika kilit"* diyor. Kural doğru yazılmış; yanlış olan gördüğü IP.
///
/// NEDEN FİKSTÜR YOK:
/// Firma bulunamadığında da deneme kaydediliyor (`GirisAsync` 2. adım) —
/// M-13'ün gereği. Uydurma bir firma+e-posta yeterli, hiçbir kiracı
/// kurulmuyor, hiçbir şeye dokunulmuyor.
/// </summary>
[Collection(SirKoleksiyonu.Ad)]
public class IstemciIpTestleri
{
    private const string VekilAyari = "TSHIFT_GUVENILEN_VEKILLER";
    private const string IstemciIp = "203.0.113.9";     // RFC 5737 — belgeleme icin ayrilmis

    [Fact(DisplayName = "IP1 - Guvenilen vekilden gelen gercek istemci IP'si kaydedilir")]
    public async Task IP1_Guvenilen_vekil()
    {
        var kaydedilen = await DenemeYapVeKaydiOku(vekilListesi: "127.0.0.1,::1");
        Assert.Equal(IstemciIp, kaydedilen);
    }

    [Fact(DisplayName = "IP2 - Guvenilmeyen kaynaktan gelen X-Forwarded-For yok sayilir")]
    public async Task IP2_Sahte_baslik()
    {
        // T-35'in sessiz tuzagi. Basliga KORLEMESINE guvenen bir duzeltme
        // IP1'i yesil yakar ama saldirganin kendi IP'sini istedigi gibi
        // gostermesine izin verir: hem kilitten kacar hem denetim kaydini
        // kirletir. Guvenilen vekil listesi bos oldugunda baslik SAYILMAZ.
        var kaydedilen = await DenemeYapVeKaydiOku(vekilListesi: "");
        Assert.NotEqual(IstemciIp, kaydedilen);
    }

    [Fact(DisplayName = "IP3 - Baslik hic yoksa istek yine de kayda gecer")]
    public async Task IP3_Basliksiz()
    {
        // Gerileme korumasi: duzeltme "baslik yoksa patla" diye yapilamaz.
        var kaydedilen = await DenemeYapVeKaydiOku(vekilListesi: "127.0.0.1,::1", baslikGonder: false);
        Assert.NotEqual(IstemciIp, kaydedilen);
    }

    // ------------------------------------------------------------------

    /// <summary>
    /// Uydurma bir firma/e-posta ile giris dener, `login_attempts` satirindaki
    /// IP'yi dondurur. Vekil listesi uygulama AYAGA KALKARKEN okundugu icin
    /// her cagri kendi uygulamasini kuruyor.
    /// </summary>
    private static async Task<string?> DenemeYapVeKaydiOku(string vekilListesi, bool baslikGonder = true)
    {
        var eposta = $"t35-{Guid.NewGuid():N}@ornek.gecersiz";
        var onceki = Environment.GetEnvironmentVariable(VekilAyari);
        Environment.SetEnvironmentVariable(VekilAyari, vekilListesi);
        try
        {
            using (var uygulama = new TestUygulamasi())
            {
                var istemci = uygulama.CreateClient();
                var istek = new HttpRequestMessage(HttpMethod.Post, "/api/v1/auth/login")
                {
                    Content = JsonContent.Create(new
                    {
                        firma = "yok-boyle-bir-firma",
                        eposta,
                        parola = "yanlis-parola-1234"
                    })
                };
                if (baslikGonder)
                    istek.Headers.TryAddWithoutValidation("X-Forwarded-For", IstemciIp);

                await istemci.SendAsync(istek);   // 401 bekleniyor; onemli olan KAYIT
            }

            return await KaydiOku(eposta);
        }
        finally
        {
            Environment.SetEnvironmentVariable(VekilAyari, onceki);
            await KaydiSil(eposta);
        }
    }

    private static TShiftDbContext SahipBaglami()
    {
        var secenekler = new DbContextOptionsBuilder<TShiftDbContext>()
            .UseNpgsql(TestAyarlari.SahipBaglantisi)
            .Options;
        return new TShiftDbContext(secenekler, new KiraciBaglami());
    }

    private static async Task<string?> KaydiOku(string eposta)
    {
        await using var db = SahipBaglami();
        var satir = await db.GirisDenemeleri
            .AsNoTracking()
            .Where(d => d.Eposta == eposta)
            .OrderByDescending(d => d.Zaman)
            .FirstOrDefaultAsync();

        Assert.True(satir is not null, "giris denemesi hic kaydedilmemis -- test kurulumu bozuk");
        return satir!.Ip;
    }

    private static async Task KaydiSil(string eposta)
    {
        await using var db = SahipBaglami();
        await db.GirisDenemeleri.Where(d => d.Eposta == eposta).ExecuteDeleteAsync();
    }
}
