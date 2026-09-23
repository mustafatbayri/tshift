using TShift.Infrastructure;

namespace TShift.Tests;

/// <summary>
/// TEST BAĞLANTILARI — parola testlerin içine de YAZILMAZ (T-34).
///
/// Yedi test dosyası bağlantı dizesini sabit tutuyordu; aynı parola yedi kez
/// depoda duruyordu. Uygulama kodunu düzeltip test kodunu bırakmak, sırrı
/// depodan çıkarmamak demekti.
///
/// Değerler ortam değişkeninden gelir ve yoksa test <b>açılışta</b> patlar —
/// sessizce yanlış bir veritabanına bağlanıp anlaşılmaz hata vermektense.
/// Yerelde `.\TEST.ps1` bunları 04-kod/.env dosyasından okur; CI her koşuda
/// rastgele üretir.
/// </summary>
public static class TestAyarlari
{
    /// <summary>Uygulamanın bağlandığı kısıtlı rol — RLS'e TABİ.</summary>
    public static string UygulamaBaglantisi =>
        "Host=localhost;Port=5433;Database=tshift;Username=tshift_app;Password="
        + Sirlar.Zorunlu("APP_DB_PASSWORD");

    /// <summary>Sahibi rol — migration ve temizlik için. RLS'i AŞAR.</summary>
    public static string SahipBaglantisi =>
        "Host=localhost;Port=5433;Database=tshift;Username=tshift;Password="
        + Sirlar.Zorunlu("DB_PASSWORD");
}
