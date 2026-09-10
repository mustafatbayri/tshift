using TShift.Domain.Common;

namespace TShift.Domain.Yetki;

public enum KapsamTipi { Departman = 1, Ekip = 2 }

/// <summary>
/// Kullanıcının hangi departman/ekipleri görebildiği. Spec §8.1 `user_scopes`.
/// Kapsam seviyesi <see cref="KapsamSeviyesi.Kapsam"/> olan roller bu satırlarla
/// sınırlanır.
/// </summary>
public class KullaniciKapsami : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid KullaniciId { get; set; }
    public KapsamTipi Tip { get; set; }
    public Guid HedefId { get; set; }
}
