using System.Security.Cryptography;
using System.Text;
using Konscious.Security.Cryptography;

namespace TShift.Infrastructure.Kimlik;

public interface IParolaServisi
{
    string Ozetle(string parola);
    bool Dogrula(string parola, string ozet);
    /// <summary>Kullanıcı bulunamadığında bile aynı süreyi harcamak için.</summary>
    void BosaCalis();
}

/// <summary>
/// Argon2id parola özeti. Spec §7.4: bellek 64 MB · yineleme 3 · paralellik 4.
///
/// Neden Argon2id ve neden bu kadar pahalı: parola düşük entropili bir sırdır.
/// Hızlı bir özet algoritması (SHA-256 gibi) kullanılırsa, veritabanı sızdığında
/// saldırgan saniyede milyarlarca deneme yapabilir. Argon2id her denemeyi
/// 64 MB bellek ve ölçülebilir bir süre harcamaya zorlar; bu, saldırıyı
/// pratik olmaktan çıkarır.
///
/// Saklama biçimi (kendi kendini tanımlayan, PHC benzeri):
///   argon2id$v=19$m=65536,t=3,p=4$&lt;tuz-base64&gt;$&lt;ozet-base64&gt;
/// Parametreler özetin içinde durur; ileride maliyeti artırırsak eski kayıtlar
/// kendi parametreleriyle doğrulanmaya devam eder.
/// </summary>
public sealed class ParolaServisi : IParolaServisi
{
    private const int BellekKb = 65536;   // 64 MB
    private const int Yineleme = 3;
    private const int Paralellik = 4;
    private const int TuzUzunluk = 16;
    private const int OzetUzunluk = 32;

    public string Ozetle(string parola)
    {
        var tuz = RandomNumberGenerator.GetBytes(TuzUzunluk);
        var ozet = Hesapla(parola, tuz, BellekKb, Yineleme, Paralellik, OzetUzunluk);
        return $"argon2id$v=19$m={BellekKb},t={Yineleme},p={Paralellik}$" +
               $"{Convert.ToBase64String(tuz)}${Convert.ToBase64String(ozet)}";
    }

    public bool Dogrula(string parola, string ozet)
    {
        try
        {
            var parcalar = ozet.Split('$');
            if (parcalar.Length != 5 || parcalar[0] != "argon2id") return false;

            var p = parcalar[2].Split(',');
            var bellek = int.Parse(p[0][2..]);
            var yineleme = int.Parse(p[1][2..]);
            var paralellik = int.Parse(p[2][2..]);

            var tuz = Convert.FromBase64String(parcalar[3]);
            var beklenen = Convert.FromBase64String(parcalar[4]);

            var hesaplanan = Hesapla(parola, tuz, bellek, yineleme, paralellik, beklenen.Length);

            // Sabit süreli karşılaştırma: "kaçıncı karakterde farklı" bilgisi
            // sızmasın diye. Zamanlama saldırısına karşı.
            return CryptographicOperations.FixedTimeEquals(hesaplanan, beklenen);
        }
        catch
        {
            // Bozuk kayıt = doğrulanmamış. Sessizce false; ayrıntı dışarı verilmez.
            return false;
        }
    }

    /// <summary>
    /// Kullanıcı bulunamadığında da bir Argon2 hesabı yapılır.
    ///
    /// Sebep: aksi halde "var olmayan kullanıcı" isteği 1 ms, "yanlış parola"
    /// isteği 300 ms sürer. Saldırgan bu farkı ölçerek hangi e-postaların
    /// kayıtlı olduğunu çıkarabilir. Buna kullanıcı sayımı (user enumeration)
    /// denir ve tek savunması iki yolun aynı süreyi harcamasıdır.
    /// </summary>
    public void BosaCalis()
    {
        var tuz = RandomNumberGenerator.GetBytes(TuzUzunluk);
        Hesapla("bosa-calisan-parola", tuz, BellekKb, Yineleme, Paralellik, OzetUzunluk);
    }

    private static byte[] Hesapla(string parola, byte[] tuz, int bellekKb, int yineleme, int paralellik, int uzunluk)
    {
        using var argon = new Argon2id(Encoding.UTF8.GetBytes(parola))
        {
            Salt = tuz,
            MemorySize = bellekKb,
            Iterations = yineleme,
            DegreeOfParallelism = paralellik
        };
        return argon.GetBytes(uzunluk);
    }
}
