using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Organizasyon;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class EkipYapilandirmasi : IEntityTypeConfiguration<Ekip>
{
    public void Configure(EntityTypeBuilder<Ekip> b)
    {
        b.ToTable("teams");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.DepartmanId).HasColumnName("department_id").IsRequired();
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(200).IsRequired();
        b.Property(x => x.Kod).HasColumnName("kod").HasMaxLength(40).IsRequired();
        b.Property(x => x.Aciklama).HasColumnName("aciklama").HasMaxLength(500);
        b.Property(x => x.Aktif).HasColumnName("aktif");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        b.HasIndex(x => new { x.KiraciId, x.Kod }).IsUnique().HasDatabaseName("ux_teams_tenant_kod");
        b.HasOne<Departman>().WithMany().HasForeignKey(x => x.DepartmanId).OnDelete(DeleteBehavior.Cascade);
    }
}
