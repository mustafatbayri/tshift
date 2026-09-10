using TShift.Domain.Common;

namespace TShift.Domain.Kimlik;

public enum IptalSebebi
{
    /// <summary>Normal akış: jeton kullanıldı, yerine yenisi verildi.</summary>
    Kullanildi = 1,
    /// <summary>Kullanıcı çıkış yaptı.</summary>
    Cikis = 2,
    /// <summary>Güvenlik olayı: yeniden kullanım tespit edildi ya da parola değişti.</summary>
    Guvenlik = 3
}

/// <summary>
/// Yenileme jetonu. Spec §8.1 `refresh_tokens`, §7.4.
///
/// İki kural bu sınıfın varlık sebebi:
///
/// 1. **Ham jeton hiçbir yerde saklanmaz.** Veritabanında yalnız SHA-256 özeti
///    durur. Veritabanı sızsa bile jetonlar kullanılamaz.
///
/// 2. **Döner jeton.** Her kullanımda mevcut jeton iptal edilir, yenisi verilir.
///    İptal edilmiş bir jeton tekrar gelirse bu, birinin jetonu çaldığı anlamına
///    gelir — o kullanıcının TÜM oturumları düşürülür.
/// </summary>
public class YenilemeJetonu : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid KullaniciId { get; set; }

    /// <summary>Jetonun SHA-256 özeti. Ham hali sadece kullanıcının elinde.</summary>
    public required string JetonOzeti { get; set; }

    /// <summary>Zincirin bir önceki halkası — hırsızlık takibi için.</summary>
    public string? OncekiJetonOzeti { get; set; }

    public string? Cihaz { get; set; }
    public string? Ip { get; set; }

    public DateTimeOffset SonKullanim { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset Bitis { get; set; }

    public DateTimeOffset? IptalZamani { get; set; }
    public IptalSebebi? IptalSebebi { get; set; }

    public bool Gecerli(DateTimeOffset simdi) => IptalZamani is null && Bitis > simdi;
}
