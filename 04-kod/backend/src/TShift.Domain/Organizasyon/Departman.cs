using TShift.Domain.Common;

namespace TShift.Domain.Organizasyon;

public enum CalismaTipi { YediYirmiDort = 1, Saatli = 2 }

/// <summary>
/// Departman / Şube. Plan bu birim bazında üretilir. Spec §8.2 `departments`.
/// Perakendede şube = departman; ayrı kavram yok, arayüzdeki kelime Kiraci.BirimAdi'ndan gelir.
/// </summary>
public class Departman : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }

    public required string Ad { get; set; }
    public required string Kod { get; set; }

    /// <summary>Bölge → Şube hiyerarşisi için.</summary>
    public Guid? UstDepartmanId { get; set; }

    public CalismaTipi CalismaTipi { get; set; } = CalismaTipi.Saatli;

    /// <summary>Genişletilmiş saat: kapanış 24'ü aşabilir (ör. 08:00–26:00).</summary>
    public decimal? AcilisSaat { get; set; }
    public decimal? KapanisSaat { get; set; }

    public bool Aktif { get; set; } = true;
}
