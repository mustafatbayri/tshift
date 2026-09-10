namespace TShift.Infrastructure.Persistence;

/// <summary>
/// O anki isteğin hangi kiracıya ait olduğunu taşır.
/// Faz 1'de geçici olarak X-Tenant-Id başlığından geliyor; kimlik katmanı
/// devreye girince JWT'den okunacak ve başlık tamamen kaldırılacak (Spec §10).
/// </summary>
public interface IKiraciBaglami
{
    Guid? KiraciId { get; }
    void Ayarla(Guid? kiraciId);
}

public sealed class KiraciBaglami : IKiraciBaglami
{
    public Guid? KiraciId { get; private set; }
    public void Ayarla(Guid? kiraciId) => KiraciId = kiraciId;
}
