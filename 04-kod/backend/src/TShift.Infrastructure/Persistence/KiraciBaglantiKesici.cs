using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace TShift.Infrastructure.Persistence;

/// <summary>
/// SAVUNMANIN İKİNCİ KATMANI.
///
/// Her veritabanı bağlantısı açıldığında PostgreSQL oturumuna `app.tenant_id`
/// değişkenini yazar. Satır seviyesi güvenlik (RLS) politikaları bu değişkeni
/// okur. Yani uygulama katmanında bir sorgu `KiraciId` filtresini unutsa bile
/// veritabanı başka kiracının satırını döndürmez.
///
/// Bağlantı havuzu notu: `set_config(..., false)` oturum düzeyindedir ve havuza
/// dönen bağlantıda kalır. Bu yüzden değeri HER açılışta yazıyoruz — kiracı yoksa
/// boş yazıyoruz ki eski bir değer sızmasın.
/// </summary>
public sealed class KiraciBaglantiKesici(IKiraciBaglami baglam) : DbConnectionInterceptor
{
    public override async Task ConnectionOpenedAsync(
        DbConnection connection,
        ConnectionEndEventData eventData,
        CancellationToken cancellationToken = default)
    {
        await UygulaAsync(connection, cancellationToken);
        await base.ConnectionOpenedAsync(connection, eventData, cancellationToken);
    }

    public override void ConnectionOpened(DbConnection connection, ConnectionEndEventData eventData)
    {
        UygulaAsync(connection, CancellationToken.None).GetAwaiter().GetResult();
        base.ConnectionOpened(connection, eventData);
    }

    private async Task UygulaAsync(DbConnection connection, CancellationToken ct)
    {
        var deger = baglam.KiraciId?.ToString() ?? string.Empty;

        await using var cmd = connection.CreateCommand();
        cmd.CommandText = "SELECT set_config('app.tenant_id', @kiraci, false)";
        var p = cmd.CreateParameter();
        p.ParameterName = "kiraci";
        p.Value = deger;
        cmd.Parameters.Add(p);
        await cmd.ExecuteNonQueryAsync(ct);
    }
}
