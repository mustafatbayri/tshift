using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Calisanlar;
using TShift.Domain.Organizasyon;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class CalisanYapilandirmasi : IEntityTypeConfiguration<Calisan>
{
    public void Configure(EntityTypeBuilder<Calisan> b)
    {
        b.ToTable("employees");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.KiraciId).HasColumnName("tenant_id").IsRequired();
        b.Property(x => x.PersonelNo).HasColumnName("personel_no").HasMaxLength(40).IsRequired();
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(100).IsRequired();
        b.Property(x => x.Soyad).HasColumnName("soyad").HasMaxLength(100).IsRequired();
        b.Property(x => x.Eposta).HasColumnName("eposta").HasColumnType("citext");
        b.Property(x => x.Telefon).HasColumnName("telefon").HasMaxLength(30);
        b.Property(x => x.DepartmanId).HasColumnName("department_id").IsRequired();
        b.Property(x => x.BirincilEkipId).HasColumnName("birincil_team_id");
        b.Property(x => x.IseGiris).HasColumnName("ise_giris");
        b.Property(x => x.IstenCikis).HasColumnName("isten_cikis");
        b.Property(x => x.Durum).HasColumnName("durum").HasConversion<short>();
        b.Property(x => x.KullaniciId).HasColumnName("user_id");
        b.Property(x => x.DisSistemId).HasColumnName("dis_sistem_id").HasMaxLength(200);
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");
        b.Ignore(x => x.TamAd);

        b.HasIndex(x => new { x.KiraciId, x.PersonelNo }).IsUnique().HasDatabaseName("ux_employees_tenant_personel_no");
        b.HasIndex(x => new { x.KiraciId, x.DepartmanId, x.Durum }).HasDatabaseName("ix_employees_tenant_dept_durum");
        b.HasOne<Departman>().WithMany().HasForeignKey(x => x.DepartmanId).OnDelete(DeleteBehavior.Restrict);
        b.HasOne<Ekip>().WithMany().HasForeignKey(x => x.BirincilEkipId).OnDelete(DeleteBehavior.SetNull);
    }
}
