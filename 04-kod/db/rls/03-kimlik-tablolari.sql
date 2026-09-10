-- =============================================================================
-- 03 — KİMLİK TABLOLARI: satır seviyesi güvenlik
--
-- Migration çalıştıktan SONRA, `tshift` kullanıcısıyla çalıştır.
--
-- İki yeni tablo kiracıya aittir ve RLS'e girer:
--   user_credentials  — parola özetleri
--   refresh_tokens    — oturum jetonları
--
-- Bir yeni tablo BİLEREK RLS DIŞINDA bırakılır:
--   login_attempts    — gerekçe aşağıda
-- =============================================================================

-- ---- 1) Kiracıya ait tablolar ----------------------------------------------
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['user_credentials', 'refresh_tokens']
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

-- ---- 2) login_attempts — neden RLS yok --------------------------------------
--
-- Giriş denemesi, kiracının kim olduğu HENÜZ BİLİNMEDEN kaydedilmek zorunda:
-- var olmayan bir firma adıyla ya da var olmayan bir e-postayla yapılan
-- denemeler de sayılmalı. Aksi halde saldırgan, kayıtlı olmayan bir firma adı
-- yazarak kaba kuvvet kilidini tamamen atlar.
--
-- Bedeli: bu tabloda tüm kiracıların denenen e-posta adresleri bir arada durur.
-- Bu yüzden hiçbir API ucu bu tabloyu dışarı açmaz; yalnızca giriş akışı
-- içinden sayım amacıyla okunur. Parola ya da jeton İÇERMEZ.
--
-- Karar bilinçlidir; RLS'i "unutmuş" değiliz. Aşağıdaki yorum satırını açıp
-- RLS eklerseniz kaba kuvvet koruması sessizce çalışmaz hale gelir.
COMMENT ON TABLE login_attempts IS
    'Kaba kuvvet sayaci. BILEREK RLS disidir: kiraci bilinmeden yazilir. Disari acilmaz.';

-- ---- 3) Yeni tablolarda uygulama rolünün yetkisi ---------------------------
-- 02-uygulama-rolu.sql'deki ALTER DEFAULT PRIVILEGES bunu zaten yapmış olmalı;
-- burada garantiye alıyoruz (betik sırası değişirse diye).
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO tshift_app;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO tshift_app;

-- ---- 4) Kontrol -------------------------------------------------------------
-- Beklenen:
--   user_credentials · refresh_tokens → t / t
--   login_attempts                    → f / f   (bilerek)
SELECT c.relname                AS tablo,
       c.relrowsecurity         AS rls_acik,
       c.relforcerowsecurity    AS sahibe_de_uygula
FROM   pg_class c
JOIN   pg_namespace n ON n.oid = c.relnamespace
WHERE  n.nspname = 'public'
  AND  c.relname IN ('users', 'departments', 'teams', 'employees',
                     'employee_contracts', 'user_credentials',
                     'refresh_tokens', 'login_attempts')
ORDER  BY c.relrowsecurity DESC, c.relname;
