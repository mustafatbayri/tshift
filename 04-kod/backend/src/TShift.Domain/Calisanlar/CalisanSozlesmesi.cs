using TShift.Domain.Common;

namespace TShift.Domain.Calisanlar;

public enum SozlesmeTipi { TamZamanli = 1, YariZamanli = 2, Sezonluk = 3, Stajyer = 4 }

/// <summary>
/// Spec §8.3 `employee_contracts`.
/// Bir çalışanın birden çok sözleşmesi olabilir; motor plan haftasında geçerli olanı kullanır.
/// GunlukAzamiSaat doluysa kiracının GUNLUK_AZAMI kural parametresini ezer (Spec §5.2, 4 kademeli çözünürlük).
/// </summary>
public class CalisanSozlesmesi : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid CalisanId { get; set; }

    public SozlesmeTipi Tip { get; set; } = SozlesmeTipi.TamZamanli;
    public decimal HaftalikSaat { get; set; } = 45m;
    public decimal? GunlukAzamiSaat { get; set; }

    public DateOnly Baslangic { get; set; }
    public DateOnly? Bitis { get; set; }
    public bool Aktif { get; set; } = true;
}
