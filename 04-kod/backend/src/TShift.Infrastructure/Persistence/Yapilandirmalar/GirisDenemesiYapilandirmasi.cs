using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using TShift.Domain.Kimlik;

namespace TShift.Infrastructure.Persistence.Yapilandirmalar;

public class GirisDenemesiYapilandirmasi : IEntityTypeConfiguration<GirisDenemesi>
{
    public void Configure(EntityTypeBuilder<GirisDenemesi> b)
    {
        b.ToTable("login_attempts");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id");
        b.Property(x => x.FirmaSlug).HasColumnName("firma_slug").HasMaxLength(80);
        b.Property(x => x.Eposta).HasColumnName("eposta").HasColumnType("citext").IsRequired();
        b.Property(x => x.Ip).HasColumnName("ip").HasMaxLength(60);
        b.Property(x => x.Tarayici).HasColumnName("user_agent").HasMaxLength(400);
        b.Property(x => x.Basarili).HasColumnName("basarili");
        b.Property(x => x.Zaman).HasColumnName("zaman");
        b.Property(x => x.OlusturmaZamani).HasColumnName("created_at");
        b.Property(x => x.GuncellemeZamani).HasColumnName("updated_at");

        // Kilit kontrolü bu iki sorguyla yapılır (spec §8.1).
        b.HasIndex(x => new { x.Eposta, x.Zaman }).HasDatabaseName("ix_login_attempts_eposta");
        b.HasIndex(x => new { x.Ip, x.Zaman }).HasDatabaseName("ix_login_attempts_ip");
    }
}
