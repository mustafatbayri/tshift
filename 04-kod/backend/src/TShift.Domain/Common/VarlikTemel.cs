namespace TShift.Domain.Common;

/// <summary>
/// Her tablonun ortak alanları. Spec §8: id UUID, created_at, updated_at.
/// </summary>
public abstract class VarlikTemel
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public DateTimeOffset OlusturmaZamani { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? GuncellemeZamani { get; set; }
}

/// <summary>
/// Kiracıya ait olan varlıklar bunu uygular. Sorgu filtresi ve satır seviyesi
/// güvenlik bu arayüze bakarak çalışır — yeni bir tablo eklendiğinde bunu
/// uygulamayı unutmak, çok kiracılık sızıntısının bir numaralı sebebidir.
/// </summary>
public interface IKiraciVarligi
{
    Guid KiraciId { get; set; }
}
