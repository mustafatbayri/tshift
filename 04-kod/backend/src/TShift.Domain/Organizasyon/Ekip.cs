using TShift.Domain.Common;

namespace TShift.Domain.Organizasyon;

/// <summary>Departman içinde birlikte çalışan grup. Kapsama ekip bazında tanımlanır. Spec §8.2 `teams`.</summary>
public class Ekip : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid DepartmanId { get; set; }

    public required string Ad { get; set; }
    public required string Kod { get; set; }
    public string? Aciklama { get; set; }
    public bool Aktif { get; set; } = true;
}
