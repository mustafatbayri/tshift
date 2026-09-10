using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace TShift.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class DenetimKaydi : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "audit_log",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: true),
                    varlik = table.Column<string>(type: "character varying(80)", maxLength: 80, nullable: false),
                    varlik_id = table.Column<Guid>(type: "uuid", nullable: false),
                    islem = table.Column<short>(type: "smallint", nullable: false),
                    oncesi = table.Column<string>(type: "jsonb", nullable: true),
                    sonrasi = table.Column<string>(type: "jsonb", nullable: true),
                    ip = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: true),
                    user_agent = table.Column<string>(type: "character varying(400)", maxLength: 400, nullable: true),
                    zaman = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_audit_log", x => x.id);
                    table.ForeignKey(
                        name: "FK_audit_log_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.InsertData(
                schema: "public",
                table: "permissions",
                columns: new[] { "kod", "aciklama", "kategori" },
                values: new object[] { "denetim.gor", "Denetim kaydını görüntüler", "Yönetim" });

            migrationBuilder.CreateIndex(
                name: "IX_audit_log_tenant_id",
                schema: "public",
                table: "audit_log",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ix_audit_kullanici",
                schema: "public",
                table: "audit_log",
                columns: new[] { "user_id", "zaman" });

            migrationBuilder.CreateIndex(
                name: "ix_audit_varlik",
                schema: "public",
                table: "audit_log",
                columns: new[] { "varlik", "varlik_id", "zaman" });

            migrationBuilder.CreateIndex(
                name: "ix_audit_zaman",
                schema: "public",
                table: "audit_log",
                column: "zaman");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "audit_log",
                schema: "public");

            migrationBuilder.DeleteData(
                schema: "public",
                table: "permissions",
                keyColumn: "kod",
                keyValue: "denetim.gor");
        }
    }
}
