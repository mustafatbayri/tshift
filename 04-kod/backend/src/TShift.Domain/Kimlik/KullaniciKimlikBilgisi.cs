using TShift.Domain.Common;

namespace TShift.Domain.Kimlik;

/// <summary>
/// Parola özeti. Spec §8.1 `user_credentials`.
///
/// Neden ayrı tablo: parola `users` tablosunda dursaydı, kullanıcı listesi
/// çeken her sorgu parola özetini de belleğe alırdı. Ayrı tabloda olması,
/// "yanlışlıkla dışarı sızdırma" ihtimalini yapısal olarak azaltır.
/// </summary>
public class KullaniciKimlikBilgisi : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid KullaniciId { get; set; }

    /// <summary>Argon2id çıktısı. Ham parola hiçbir yerde saklanmaz, kayda yazılmaz.</summary>
    public required string SifreHash { get; set; }

    /// <summary>İleride algoritma değişirse eski kayıtları tanıyabilmek için.</summary>
    public string Algoritma { get; set; } = "argon2id";

    public DateTimeOffset DegisimZamani { get; set; } = DateTimeOffset.UtcNow;

    /// <summary>İlk girişte parola değiştirme zorunluluğu.</summary>
    public bool ZorunluDegisim { get; set; }
}
