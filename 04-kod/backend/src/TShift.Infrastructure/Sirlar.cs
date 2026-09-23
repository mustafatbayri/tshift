namespace TShift.Infrastructure;

/// <summary>
/// SIRLAR — ortam değişkeninden okunur, varsayılanı YOKTUR.
///
/// NEDEN (T-34, 16 Eylül dış incelemesi):
/// Sırlar `?? "varsayilan"` ile okunuyordu. Ortam değişkeni unutulduğunda
/// uygulama hata vermiyor, <b>bilinen bir anahtarla</b> açılıyordu. Depo
/// herkese açık; o anahtarlar da öyle.
///
/// Program.cs'in kendi yorumu şunu diyordu: <i>"Parola koda ve appsettings'e
/// YAZILMAZ."</i> Bir satır altında koda yazılmıştı. K-28 ve T-18 ile aynı
/// sınıf: yazılı, yürürlükte değil.
///
/// KURAL: sır yoksa uygulama AÇILMAZ. Sessizce zayıf bir sırla açılmaktansa
/// gürültülü biçimde hiç açılmamak doğrudur — ilki fark edilmez, ikincisi
/// hemen fark edilir.
///
/// Hata mesajı değişkenin ADINI söyler; "bir şey eksik" kullanıcıyı çözüme
/// götürmez. Değerin KENDİSİ asla yazılmaz, yalnız uzunluğu.
/// </summary>
public static class Sirlar
{
    public static string Zorunlu(string ad, int enAzUzunluk = 1)
    {
        var deger = Environment.GetEnvironmentVariable(ad);

        if (string.IsNullOrWhiteSpace(deger))
        {
            throw new InvalidOperationException(
                ad + " ortam degiskeni verilmedi. Sirlar koda yazilmaz. "
                + "04-kod/.env.example dosyasini kopyalayip .env yapin ve "
                + "degeri girin. (T-34)");
        }

        if (deger.Length < enAzUzunluk)
        {
            throw new InvalidOperationException(
                ad + " en az " + enAzUzunluk + " karakter olmali; "
                + deger.Length + " karakter verildi. (T-34)");
        }

        return deger;
    }
}
