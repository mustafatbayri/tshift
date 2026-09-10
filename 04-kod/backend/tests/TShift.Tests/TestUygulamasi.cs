using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
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
    }
}
