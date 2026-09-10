using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Organizasyon;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class DepartmanYapilandirmasi : IEntityTypeConfiguration<Departman>
{
    public void Configure(EntityTypeBuilder<Departman> b)
    {
        b.ToTable("departments");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(200).IsRequired();
        b.Property(x => x.Kod).HasColumnName("kod").HasMaxLength(40).IsRequired();
        b.Property(x => x.UstDepartmanId).HasColumnName("ust_department_id");
        b.Property(x => x.CalismaTipi).HasColumnName("calisma_tipi").HasConversion<short>();
        b.Property(x => x.AcilisSaat).HasColumnName("acilis_saat").HasPrecision(5, 2);
        b.Property(x => x.KapanisSaat).HasColumnName("kapanis_saat").HasPrecision(5, 2);
        b.Property(x => x.Aktif).HasColumnName("aktif");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.KiraciId, x.Kod }).IsUnique().HasDatabaseName("ux_departments_tenant_kod");
        b.HasOne<TShift.Domain.Kiracilar.Kiraci>().WithMany()
            .HasForeignKey(x => x.KiraciId).OnDelete(DeleteBehavior.Cascade);
    }
}
