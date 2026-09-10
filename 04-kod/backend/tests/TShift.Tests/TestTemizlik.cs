using Npgsql;

namespace TShift.Tests;

/// <summary>
/// Test verisini siler.
///
/// SAHİBİ ROLLE (`tshift`) çalışır, uygulama rolüyle değil. İki sebeple:
///
/// 1. Uygulama rolü denetim kaydını SİLEMEZ — bu kasıtlı bir kısıt ve
///    D4/D5 testlerinin konusu. Temizliği uygulama rolüyle yapmaya çalışmak,
///    korumanın kendisine takılmak olur.
/// 2. Gerçek hayatta da saklama süresi dolduğunda temizliği sahibi rol yapar,
///    bilinçli bir bakım işi olarak. Test bunu taklit ediyor.
///
/// Bu, testleri zayıflatmaz: bütün İDDİALAR uygulama rolüyle çalışıyor.
/// Sahibi rol yalnızca ortalığı toplarken kullanılıyor.
///
/// Tablo listesi TEK BİR YERDE. Dört ayrı test dosyasında dört kopya
/// olsaydı, yeni bir tablo eklendiğinde üçünü güncelleyip birini unutmak
/// an meselesiydi — ve unutulan yer sessizce çöp veri biriktirirdi.
/// </summary>
public static class TestTemizlik
{
    private const string SahipBaglanti =
        "Host=localhost;Port=5433;Database=tshift;Username=tshift;Password=tshift_dev_2026";

    /// <summary>
    /// Silme sırası: en derindeki çocuktan yukarı doğru.
    /// Kademeli silmeye güvenmiyoruz — employees → departments ilişkisi
    /// bilerek `Restrict` ile tanımlı.
    /// </summary>
    private static readonly string[] Sira =
    [
        "audit_log",
        "user_scopes", "user_roles", "role_permissions", "roles",
        "refresh_tokens", "user_credentials",
        "employee_contracts", "employees", "teams", "departments", "users"
    ];

    public static async Task KiraciSilAsync(params Guid[] kiracilar)
    {
        if (kiracilar.Length == 0) return;

        await using var baglanti = new NpgsqlConnection(SahipBaglanti);
        await baglanti.OpenAsync();

        foreach (var kiraciId in kiracilar)
        {
            foreach (var tablo in Sira)
            {
                // Tablo adlari yukaridaki SABIT diziden geliyor; disaridan
                // hicbir girdi buraya ulasmiyor. Kiraci kimligi parametre.
                await using var komut = baglanti.CreateCommand();
                komut.CommandText = $"DELETE FROM {tablo} WHERE tenant_id = @k";
                komut.Parameters.AddWithValue("k", kiraciId);
                await komut.ExecuteNonQueryAsync();
            }

            await using var son = baglanti.CreateCommand();
            son.CommandText = "DELETE FROM tenants WHERE id = @k";
            son.Parameters.AddWithValue("k", kiraciId);
            await son.ExecuteNonQueryAsync();
        }
    }

    /// <summary>Giriş denemelerini temizler — kaba kuvvet sayacı testler arasında taşmasın.</summary>
    public static async Task GirisDenemeleriniSilAsync(params string[] epostalar)
    {
        if (epostalar.Length == 0) return;

        await using var baglanti = new NpgsqlConnection(SahipBaglanti);
        await baglanti.OpenAsync();

        foreach (var eposta in epostalar)
        {
            await using var komut = baglanti.CreateCommand();
            komut.CommandText = "DELETE FROM login_attempts WHERE eposta = @e";
            komut.Parameters.AddWithValue("e", eposta);
            await komut.ExecuteNonQueryAsync();
        }
    }
}
