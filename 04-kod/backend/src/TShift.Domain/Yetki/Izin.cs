using TShift.Domain.Common;

namespace TShift.Domain.Yetki;

/// <summary>
/// İzin kataloğu. Spec §8.1 `permissions`.
///
/// Bu tablo KİRACIYA AİT DEĞİLDİR ve satır seviyesi güvenliğe girmez.
/// Sebep: içinde müşteri verisi yok — yalnızca sistemin tanıdığı işlem
/// kodlarının listesi ("plan.uret" diye bir şey var mı?). Herkes aynı
/// katalogu görür; kim neyi yapabilir bilgisi role_permissions'ta durur ve
/// O tablo kiracıya aittir.
///
/// Katalog kodda tanımlıdır (YetkiKatalogu); bu tablo onun veritabanındaki
/// yansımasıdır, böylece role_permissions yabancı anahtarla bağlanabilir.
/// </summary>
public class Izin
{
    /// <summary>Birincil anahtar. Örn. `plan.uret`, `calisan.duzenle`.</summary>
    public required string Kod { get; set; }
    public required string Aciklama { get; set; }
    /// <summary>Ekranda gruplama için: `Çalışan`, `Plan`, `Kural`...</summary>
    public required string Kategori { get; set; }
}
