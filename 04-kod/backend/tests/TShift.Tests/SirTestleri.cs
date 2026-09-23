using Xunit;

namespace TShift.Tests;

/// <summary>
/// SIR TESTLERİ — bir sır verilmediğinde uygulama AÇILMAMALI.
///
/// NEDEN AYRI BİR SINIF VE AYRI BİR KOLEKSİYON:
/// Bu testler ortam değişkenlerini geçici olarak SİLER. Ortam değişkeni
/// süreç geneli bir şeydir; aynı anda koşan başka bir test sınıfı uygulamayı
/// ayağa kaldırmaya çalışırsa onu da etkiler. Koleksiyon paralelliği
/// kapatılarak bu engellendi.
///
/// NE KORUYORLAR (T-34):
/// 16 Eylül dış incelemesi, sırların ortam değişkeni yoksa KODDAKİ SABİTE
/// düştüğünü buldu. Uygulama hata vermiyor, bilinen bir anahtarla açılıyordu:
///
///     APP_DB_PASSWORD ?? "tshift_app_dev_2026"
///     JWT_SECRET      ?? "yerel-gelistirme-imza-anahtari-..."
///
/// Program.cs'in kendi yorumu "canlıda JWT_SECRET mutlaka verilir" diyordu.
/// Bunu ZORLAYAN hiçbir şey yoktu — yazılıydı, yürürlükte değildi. K-28 ve
/// T-18 ile aynı sınıf.
///
/// M5 ("appsettings icinde gercek parola yok") bu ailenin TEK bir üyesini
/// koruyordu ve yeşil yanıyordu. Kapı vardı; başka bir kapıydı.
/// </summary>
[Collection(SirKoleksiyonu.Ad)]
public class SirTestleri
{
    [Fact(DisplayName = "S1 - APP_DB_PASSWORD verilmezse uygulama acilmaz")]
    public void S1_AppDbPassword_yoksa_acilmaz()
    {
        SirsizCalistir("APP_DB_PASSWORD");
    }

    [Fact(DisplayName = "S2 - JWT_SECRET verilmezse uygulama acilmaz")]
    public void S2_JwtSecret_yoksa_acilmaz()
    {
        SirsizCalistir("JWT_SECRET");
    }

    [Fact(DisplayName = "S3 - Sirlar verildiginde uygulama normal acilir")]
    public void S3_Sirlar_verildiginde_acilir()
    {
        // Gerileme koruması: düzeltme "her koşulda patla" diyerek yapılamaz.
        // S1 ve S2 tek başlarına, hiç açılmayan bir uygulamayla da yeşil yanar.
        using var uygulama = new TestUygulamasi();
        var istemci = uygulama.CreateClient();
        Assert.NotNull(istemci);
    }

    /// <summary>
    /// Verilen değişkeni geçici olarak siler, uygulamayı ayağa kaldırmayı dener
    /// ve hatanın o değişkenin ADINI söylemesini bekler.
    ///
    /// Adın geçmesi şart: "bir yerde bir şey patladı" kullanıcıyı çözüme
    /// götürmez. Hangi değişkenin eksik olduğu yazmalı.
    /// </summary>
    private static void SirsizCalistir(string degisken)
    {
        var onceki = Environment.GetEnvironmentVariable(degisken);
        Environment.SetEnvironmentVariable(degisken, null);
        try
        {
            using var uygulama = new TestUygulamasi();
            var hata = Assert.ThrowsAny<Exception>(() => uygulama.CreateClient());
            Assert.Contains(degisken, TumMesajlar(hata));
        }
        finally
        {
            Environment.SetEnvironmentVariable(degisken, onceki);
        }
    }

    /// <summary>Dış hatanın mesajı yetmez; asıl sebep iç hatada olur.</summary>
    private static string TumMesajlar(Exception? hata)
    {
        var metin = "";
        while (hata is not null)
        {
            metin += hata.Message + "\n";
            hata = hata.InnerException;
        }
        return metin;
    }
}

/// <summary>
/// Ortam değişkeni silen testler tek başlarına koşar — süreç geneli bir
/// değeri değiştirdikleri için paralel koşan başka bir sınıfı bozarlar.
/// </summary>
[CollectionDefinition(Ad, DisableParallelization = true)]
public class SirKoleksiyonu
{
    public const string Ad = "Sirlar";
}
