using TShift.Domain.Common;

namespace TShift.Domain.Yetki;

/// <summary>
/// Kullanıcıya atanmış rol. Spec §8.1 `user_roles`.
///
/// Geçerlilik tarihleri süreli yetki devri içindir (spec §3.2): kiracı
/// yöneticisi bir şefe, müdür izindeyken iki haftalığına departman müdürü
/// yetkisi verir. Devir kendiliğinden biter — kimsenin geri almayı
/// hatırlaması gerekmez. Unutulan yetki, verilmemiş yetkiden tehlikelidir.
/// </summary>
public class KullaniciRolu : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid KullaniciId { get; set; }
    public Guid RolId { get; set; }

    /// <summary>Boşsa "her zaman geçerli".</summary>
    public DateOnly? GecerlilikBas { get; set; }
    /// <summary>Boşsa "süresiz". Doluysa o günün SONUNA kadar geçerli.</summary>
    public DateOnly? GecerlilikBitis { get; set; }

    /// <summary>Devri kim yaptı — denetim izi.</summary>
    public Guid? VerenKullaniciId { get; set; }

    public bool Gecerli(DateOnly bugun)
        => (GecerlilikBas is null || GecerlilikBas <= bugun)
        && (GecerlilikBitis is null || GecerlilikBitis >= bugun);
}
