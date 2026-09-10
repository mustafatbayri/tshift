using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using TShift.Domain.Kimlik;

namespace TShift.Infrastructure.Kimlik;

public interface IJetonServisi
{
    string ErisimJetonuUret(Kullanici kullanici);
    (string HamJeton, string Ozet) YenilemeJetonuUret(Guid kiraciId);
    string Ozetle(string hamJeton);
    bool KiraciCoz(string hamJeton, out Guid kiraciId);
}

/// <summary>
/// Jeton üretimi. İki farklı jeton, iki farklı mantık:
///
/// **Erişim jetonu (JWT)** — 15 dakika. İçinde kullanıcı ve kiracı kimliği var,
/// imzalı. Veritabanına bakmadan doğrulanır, bu yüzden hızlı; bu yüzden de
/// kısa ömürlü, çünkü iptal edilemez. Süresi dolana kadar geçerlidir.
///
/// **Yenileme jetonu** — 30 gün. Anlamsız rastgele bir dizi; tüm bilgi
/// veritabanında. Bu yüzden iptal edilebilir, bu yüzden uzun ömürlü olabilir.
///
/// Bu ikilinin sebebi şu dengeye çözüm: jeton ne kadar uzun ömürlüyse çalınması
/// o kadar tehlikeli; ne kadar kısa ömürlüyse kullanıcı o kadar sık giriş yapar.
/// Kısa ömürlü + iptal edilebilir uzun ömürlü ikilisi ikisini de çözer.
/// </summary>
public sealed class JetonServisi(KimlikAyarlari ayarlar, TimeProvider saat) : IJetonServisi
{
    public const string KiraciTalebi = "kiraci";

    private readonly SymmetricSecurityKey _anahtar =
        new(Encoding.UTF8.GetBytes(ayarlar.ImzaAnahtari));

    public string ErisimJetonuUret(Kullanici kullanici)
    {
        var simdi = saat.GetUtcNow().UtcDateTime;

        var talepler = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, kullanici.Id.ToString()),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(JwtRegisteredClaimNames.Email, kullanici.Eposta),
            new("ad", $"{kullanici.Ad} {kullanici.Soyad}"),
            // KRİTİK: kiracı kimliği burada. İstekten değil, imzalı jetondan okunur.
            new(KiraciTalebi, kullanici.KiraciId.ToString())
        };

        var jeton = new JwtSecurityToken(
            issuer: ayarlar.Yayinci,
            audience: ayarlar.Hedef,
            claims: talepler,
            notBefore: simdi,
            expires: simdi.Add(ayarlar.ErisimOmru),
            signingCredentials: new SigningCredentials(_anahtar, SecurityAlgorithms.HmacSha256));

        return new JwtSecurityTokenHandler().WriteToken(jeton);
    }

    /// <summary>
    /// Yenileme jetonu: "&lt;kiraciId&gt;.&lt;256 bit rastgele&gt;".
    ///
    /// Kiracı kimliğinin jetonun içinde açık durmasının sebebi pratik:
    /// yenileme isteği geldiğinde henüz kimlik doğrulanmamıştır, ama jetonu
    /// veritabanında aramak için kiracı bağlamını kurmak gerekir (RLS açık).
    /// Bu kısım sır değil — sır, noktadan sonraki rastgele kısım.
    /// </summary>
    public (string HamJeton, string Ozet) YenilemeJetonuUret(Guid kiraciId)
    {
        var rastgele = RandomNumberGenerator.GetBytes(32);
        var ham = $"{kiraciId:N}.{Base64UrlEncoder.Encode(rastgele)}";
        return (ham, Ozetle(ham));
    }

    /// <summary>
    /// Yenileme jetonunun özeti. Burada Argon2 DEĞİL, SHA-256 kullanılır.
    ///
    /// Fark şu: parola düşük entropilidir, tahmin edilebilir, bu yüzden pahalı
    /// bir algoritma ile korunur. Yenileme jetonu 256 bit rastgeledir — tahmin
    /// edilemez. Onu Argon2 ile özetlemek her istekte 64 MB bellek harcamaktan
    /// başka bir işe yaramaz.
    /// </summary>
    public string Ozetle(string hamJeton)
        => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(hamJeton)));

    public bool KiraciCoz(string hamJeton, out Guid kiraciId)
    {
        kiraciId = Guid.Empty;
        var nokta = hamJeton.IndexOf('.');
        return nokta > 0 && Guid.TryParseExact(hamJeton[..nokta], "N", out kiraciId);
    }
}
