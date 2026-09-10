using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace TShift.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Kimlik : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "login_attempts",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    firma_slug = table.Column<string>(type: "character varying(80)", maxLength: 80, nullable: true),
                    eposta = table.Column<string>(type: "citext", nullable: false),
                    ip = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: true),
                    user_agent = table.Column<string>(type: "character varying(400)", maxLength: 400, nullable: true),
                    basarili = table.Column<bool>(type: "boolean", nullable: false),
                    zaman = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_login_attempts", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "refresh_tokens",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    token_hash = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    onceki_token_hash = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    cihaz = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: true),
                    ip = table.Column<string>(type: "character varying(60)", maxLength: 60, nullable: true),
                    son_kullanim = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    bitis = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    iptal_zamani = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true),
                    iptal_sebebi = table.Column<short>(type: "smallint", nullable: true),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_refresh_tokens", x => x.id);
                    table.ForeignKey(
                        name: "FK_refresh_tokens_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_refresh_tokens_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "public",
                        principalTable: "users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_credentials",
                schema: "public",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    tenant_id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<Guid>(type: "uuid", nullable: false),
                    sifre_hash = table.Column<string>(type: "character varying(400)", maxLength: 400, nullable: false),
                    algoritma = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    degisim_zamani = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    zorunlu_degisim = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTimeOffset>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_credentials", x => x.id);
                    table.ForeignKey(
                        name: "FK_user_credentials_tenants_tenant_id",
                        column: x => x.tenant_id,
                        principalSchema: "public",
                        principalTable: "tenants",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_credentials_users_user_id",
                        column: x => x.user_id,
                        principalSchema: "public",
                        principalTable: "users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_login_attempts_eposta",
                schema: "public",
                table: "login_attempts",
                columns: new[] { "eposta", "zaman" });

            migrationBuilder.CreateIndex(
                name: "ix_login_attempts_ip",
                schema: "public",
                table: "login_attempts",
                columns: new[] { "ip", "zaman" });

            migrationBuilder.CreateIndex(
                name: "IX_refresh_tokens_tenant_id",
                schema: "public",
                table: "refresh_tokens",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ix_refresh_tokens_user",
                schema: "public",
                table: "refresh_tokens",
                columns: new[] { "user_id", "iptal_zamani" });

            migrationBuilder.CreateIndex(
                name: "ux_refresh_tokens_hash",
                schema: "public",
                table: "refresh_tokens",
                column: "token_hash",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_user_credentials_tenant_id",
                schema: "public",
                table: "user_credentials",
                column: "tenant_id");

            migrationBuilder.CreateIndex(
                name: "ux_user_credentials_user",
                schema: "public",
                table: "user_credentials",
                column: "user_id",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "login_attempts",
                schema: "public");

            migrationBuilder.DropTable(
                name: "refresh_tokens",
                schema: "public");

            migrationBuilder.DropTable(
                name: "user_credentials",
                schema: "public");
        }
    }
}
