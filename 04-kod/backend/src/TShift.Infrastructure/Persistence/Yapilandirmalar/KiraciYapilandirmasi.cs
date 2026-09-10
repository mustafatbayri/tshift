using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Kiracilar;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class KiraciYapilandirmasi : IEntityTypeConfiguration<Kiraci>
{
    public void Configure(EntityTypeBuilder<Kiraci> b)
    {
        b.ToTable("tenants");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.Ad).HasColumnName("ad").HasMaxLength(200).IsRequired();
        b.Property(x => x.Slug).HasColumnName("slug").HasMaxLength(80).IsRequired();
        b.Property(x => x.SektorPaketi).HasColumnName("sektor_paketi").HasMaxLength(40);
        b.Property(x => x.BirimAdi).HasColumnName("birim_adi").HasMaxLength(40);
        b.Property(x => x.ZamanDilimi).HasColumnName("zaman_dilimi").HasMaxLength(60);
        b.Property(x => x.HaftaBaslangic).HasColumnName("hafta_baslangic");
        b.Property(x => x.Durum).HasColumnName("durum").HasConversion<short>();
        b.Property(x => x.DenemeBitis).HasColumnName("deneme_bitis");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");
        b.HasIndex(x => x.Slug).IsUnique().HasDatabaseName("ux_tenants_slug");
    }
}
