using TShift.Domain.Common;

namespace TShift.Domain.Yetki;

/// <summary>Rol ile izin arasındaki bağ. Spec §8.1 `role_permissions`.</summary>
public class RolIzni : VarlikTemel, IKiraciVarligi
{
    public Guid KiraciId { get; set; }
    public Guid RolId { get; set; }
    public required string IzinKodu { get; set; }
}
