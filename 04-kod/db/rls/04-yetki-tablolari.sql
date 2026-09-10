-- =============================================================================
-- 04 — YETKİ TABLOLARI: satır seviyesi güvenlik
--
-- Migration çalıştıktan SONRA, `tshift` kullanıcısıyla çalıştır.
--
-- Kiracıya ait olanlar RLS'e girer:
--   roles · role_permissions · user_roles · user_scopes
--
-- Bilerek RLS dışında:
--   permissions — sistem sözlüğü, müşteri verisi değil
-- =============================================================================

DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['roles', 'role_permissions', 'user_roles', 'user_scopes']
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS kiraci_yalitimi ON %I', t);
        EXECUTE format(
            'CREATE POLICY kiraci_yalitimi ON %I
                 USING (tenant_id = app_tenant_id())
                 WITH CHECK (tenant_id = app_tenant_id())', t);
        RAISE NOTICE 'RLS acildi: %', t;
    END LOOP;
END $$;

-- permissions: izin KODLARININ listesi. "plan.uret diye bir izin var mı"
-- sorusunun cevabı; hangi firmanın hangi rolünde olduğu bilgisi DEĞİL.
-- O bilgi role_permissions'ta durur ve orası RLS'e tabidir.
-- Uygulama bu tabloyu yalnız okur; yazma yetkisi verilmez.
REVOKE INSERT, UPDATE, DELETE ON permissions FROM tshift_app;
GRANT  SELECT                  ON permissions TO   tshift_app;
COMMENT ON TABLE permissions IS
    'Izin katalogu. BILEREK RLS disidir: musteri verisi degil, sistem sozlugu. Uygulama icin salt okunur.';

-- Yeni tablolarda uygulama rolünün yetkisi (betik sırası değişirse diye).
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO tshift_app;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO tshift_app;
-- Yukarıdaki toplu GRANT permissions'a da yazma verdi; geri alıyoruz.
REVOKE INSERT, UPDATE, DELETE ON permissions FROM tshift_app;

-- ---- Kontrol ----------------------------------------------------------------
-- Beklenen: permissions ve login_attempts dışında hepsi t / t
SELECT c.relname             AS tablo,
       c.relrowsecurity      AS rls_acik,
       c.relforcerowsecurity AS sahibe_de_uygula
FROM   pg_class c
JOIN   pg_namespace n ON n.oid = c.relnamespace
WHERE  n.nspname = 'public'
  AND  c.relkind = 'r'
  AND  c.relname NOT LIKE '\_\_%'
ORDER  BY c.relrowsecurity DESC, c.relname;
