using TShift.Domain.Common;

namespace TShift.Domain.Calisanlar;

public enum CalisanDurumu { Aktif = 1, Pasif = 2, Ayrildi = 3 }

/// <summary>Spec §8.3 `employees`.</summary>
public class Calisan : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }

    /// <summary>Firma sicil no — İK entegrasyonunun eşleştirme anahtarı. (kiraci_id, personel_no) benzersiz.</summary>
    public required string PersonelNo { get; set; }

    public required string Ad { get; set; }
    public required string Soyad { get; set; }
    public string? Eposta { get; set; }
    public string? Telefon { get; set; }

    public Guid DepartmanId { get; set; }
    public Guid? BirincilEkipId { get; set; }

    public DateOnly IseGiris { get; set; }
    public DateOnly? IstenCikis { get; set; }

    public CalisanDurumu Durum { get; set; } = CalisanDurumu.Aktif;

    /// <summary>Uygulamaya girişi varsa ilgili kullanıcı.</summary>
    public Guid? KullaniciId { get; set; }

    /// <summary>İK sistemindeki kimlik.</summary>
    public string? DisSistemId { get; set; }

    public string TamAd => $"{Ad} {Soyad}";
}
