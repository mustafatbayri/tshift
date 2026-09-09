-- TShift - veritabani ilk kurulum
-- Bu dosya YALNIZCA veritabani ilk kez olusturulurken calisir.
-- Tablolari burada olusturmuyoruz; onlar .NET tarafindaki migration'lardan gelecek.

-- gen_random_uuid() icin (birincil anahtarlarimiz UUID)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Buyuk/kucuk harf duyarsiz metin - e-posta alanlari icin
CREATE EXTENSION IF NOT EXISTS citext;

DO $$
BEGIN
  RAISE NOTICE 'TShift veritabani hazir. Eklentiler: pgcrypto, citext';
END $$;
