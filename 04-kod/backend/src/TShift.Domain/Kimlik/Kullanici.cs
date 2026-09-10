using TShift.Domain.Common;

namespace TShift.Domain.Kimlik;

public enum KullaniciDurumu { Aktif = 1, Pasif = 2 }

/// <summary>
/// Uygulamaya giriş yapan kişi. Spec §8.1 `users`.
/// Parola bu tabloda DEĞİL — `user_credentials` tablosunda tutulacak (kimlik adımında).
/// </summary>
public class Kullanici : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }

    public required string Ad { get; set; }
    public required string Soyad { get; set; }

    /// <summary>Giriş kimliği. (kiraci_id, eposta) benzersiz.</summary>
    public required string Eposta { get; set; }
    public bool EpostaDogrulandi { get; set; }
    public string? Telefon { get; set; }

    /// <summary>Bu kullanıcı aynı zamanda bir çalışansa.</summary>
    public Guid? CalisanId { get; set; }

    public bool MfaAktif { get; set; }
    public short BasarisizGiris { get; set; }
    public DateTimeOffset? KilitBitis { get; set; }

    // Faz 2 SSO için baştan hazır — faz 1'de boş durur. Spec §7.4.
    public string? DisKimlikSaglayici { get; set; }
    public string? DisKimlikId { get; set; }

    public KullaniciDurumu Durum { get; set; } = KullaniciDurumu.Aktif;
    public DateTimeOffset? SonGiris { get; set; }
}
