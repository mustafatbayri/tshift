using TShift.Domain.Common;

namespace TShift.Domain.Yetki;

/// <summary>
/// Rolün ne kadarını görebildiği. İzin "neyi yapabilir", kapsam "nerede yapabilir"
/// sorusunu cevaplar. İkisi ayrı kavram: bir şef de bir departman müdürü de
/// plan düzenleyebilir, ama farklı yerlerde.
/// </summary>
public enum KapsamSeviyesi
{
    /// <summary>Yalnızca kendi çalışan kaydı. Spec matrisinde "kendi".</summary>
    Kendi = 1,
    /// <summary>user_scopes tablosundaki departman/ekipler. Spec matrisinde "K".</summary>
    Kapsam = 2,
    /// <summary>Kiracının tamamı. Spec matrisinde "✓".</summary>
    Kiraci = 3
}

/// <summary>
/// Rol. Spec §3.1 ve §8.1 `roles`.
///
/// Roller KİRACIYA AİTTİR — her firma kendi rol satırlarını taşır. Sebep:
/// ileride bir müşteri kendi rolünü tanımlamak isteyecek ("bölge sorumlusu"),
/// ve genel + kiracıya özel rolleri tek tabloda karıştırmak RLS kuralını
/// zayıflatır (politika "tenant_id NULL ya da benim" demek zorunda kalırdı).
/// Bedeli: yeni kiracı açılırken 5 sistem rolü kopyalanır. Ucuz.
/// </summary>
public class Rol : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }

    /// <summary>`kiraci_yonetici` | `departman_muduru` | `sef` | `calisan` | `izleyici`</summary>
    public required string Kod { get; set; }
    public required string Ad { get; set; }

    public KapsamSeviyesi Kapsam { get; set; } = KapsamSeviyesi.Kapsam;

    /// <summary>Sistem rolleri kullanıcı tarafından düzenlenemez veya silinemez.</summary>
    public bool SistemMi { get; set; }
}
