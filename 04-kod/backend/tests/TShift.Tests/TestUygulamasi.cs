using System.Net;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace TShift.Tests;

/// <summary>
/// Testler için uygulama örneği.
///
/// Tek işi kayıt gürültüsünü kısmak. Geliştirme ortamında EF her SQL cümlesini
/// yazıyor; test çıktısında bu, asıl hata mesajını yüzlerce satırın arasında
/// kaybediyor. Gürültülü bir çıktı, okunmayan bir çıktıdır — ve okunmayan
/// çıktı, olmayan çıktıyla aynı şeydir.
///
/// Uyarı ve üstü görünmeye devam eder; bir şey gerçekten ters giderse kaybolmaz.
/// </summary>
public class TestUygulamasi : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureLogging(k =>
        {
            k.ClearProviders();
            k.SetMinimumLevel(LogLevel.Warning);
        });

        // T-35: test sunucusunda GERCEK SOKET YOK, bu yuzden
        // `Connection.RemoteIpAddress` null geliyor. Gercekte her istegin bir
        // karsi adresi vardir; `UseForwardedHeaders` guvenilen vekil listesini
        // tam o adresle karsilastirir ve null ile hicbir seye guvenmez.
        //
        // Burada YAPILAN: testin ORTAMINI gercege benzetmek (sokete bir adres
        // vermek). YAPILMAYAN: bir iddiayi gevsetmek. IP1/IP2/IP3'un
        // iddialari aynen duruyor -- yalnizca gercekligin her zaman
        // sagladigi bir onkosul burada elle saglaniyor.
        builder.ConfigureServices(h =>
            h.AddSingleton<IStartupFilter, SoketAdresiFiltresi>());
    }
}

/// <summary>
/// Boru hattinin EN BASINA girer ve bos olan uzak adresi doldurur.
/// ForwardedHeaders'tan once kosmasi sart: o ara katman listeye bakarken
/// adresin dolu olmasi gerekiyor.
/// </summary>
internal sealed class SoketAdresiFiltresi : IStartupFilter
{
    public Action<IApplicationBuilder> Configure(Action<IApplicationBuilder> sonraki)
        => uygulama =>
        {
            uygulama.Use(async (ctx, ileri) =>
            {
                ctx.Connection.RemoteIpAddress ??= IPAddress.Loopback;
                await ileri();
            });
            sonraki(uygulama);
        };
}
