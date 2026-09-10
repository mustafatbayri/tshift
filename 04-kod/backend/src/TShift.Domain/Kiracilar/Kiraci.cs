using TShift.Domain.Common;

namespace TShift.Domain.Kiracilar;

public enum KiraciDurumu { Aktif = 1, Askida = 2, Deneme = 3 }

/// <summary>Sistemi kullanan müşteri firma. Spec §8.1 `tenants`.</summary>
public class Kiraci : VarlikTemel
{
    public required string Ad { get; set; }
    public required string Slug { get; set; }
    public string SektorPaketi { get; set; } = "bos";

    /// <summary>Arayüzde "departman" yerine kullanılacak kelime: Departman / Şube / Birim. Spec §9.11.</summary>
    public string BirimAdi { get; set; } = "Departman";

    public string ZamanDilimi { get; set; } = "Europe/Istanbul";
    public short HaftaBaslangic { get; set; } = 1; // 1 = Pazartesi
    public KiraciDurumu Durum { get; set; } = KiraciDurumu.Deneme;
    public DateOnly? DenemeBitis { get; set; }
}
