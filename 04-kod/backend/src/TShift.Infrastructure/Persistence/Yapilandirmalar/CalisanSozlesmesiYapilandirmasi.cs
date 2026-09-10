using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Calisanlar;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class CalisanSozlesmesiYapilandirmasi : IEntityTypeConfiguration<CalisanSozlesmesi>
{
    public void Configure(EntityTypeBuilder<CalisanSozlesmesi> b)
    {
        b.ToTable("employee_contracts");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.CalisanId).HasColumnName("employee_id").IsRequired();
        b.Property(x => x.Tip).HasColumnName("tip").HasConversion<short>();
        b.Property(x => x.HaftalikSaat).HasColumnName("haftalik_saat").HasPrecision(5, 2);
        b.Property(x => x.GunlukAzamiSaat).HasColumnName("gunluk_azami_saat").HasPrecision(5, 2);
        b.Property(x => x.Baslangic).HasColumnName("baslangic");
        b.Property(x => x.Bitis).HasColumnName("bitis");
        b.Property(x => x.Aktif).HasColumnName("aktif");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.CalisanId, x.Aktif }).HasDatabaseName("ix_contracts_employee_aktif");
        b.HasOne<Calisan>().WithMany().HasForeignKey(x => x.CalisanId).OnDelete(DeleteBehavior.Cascade);
    }
}
