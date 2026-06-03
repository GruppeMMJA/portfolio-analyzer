-- ============================================================
-- Portfolio Analyzer — Supabase Setup SQL
-- Run this ONCE in the Supabase SQL Editor:
-- Dashboard → SQL Editor → New Query → paste → Run
-- ============================================================


-- ── 1. Portfolios ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS portfolios (
    id            UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id       UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker        TEXT        NOT NULL,
    name          TEXT        DEFAULT '',
    market_value  FLOAT       DEFAULT 0,
    currency      TEXT        DEFAULT 'EUR',
    isin          TEXT        DEFAULT '',
    country       TEXT        DEFAULT '',
    gics_sector   INTEGER     DEFAULT 0,
    asset_type    TEXT        DEFAULT '',
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user lookups
CREATE INDEX IF NOT EXISTS portfolios_user_id_idx ON portfolios (user_id);

-- Row Level Security
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- Each user can only read/write their own rows
CREATE POLICY "users_own_portfolios" ON portfolios
    FOR ALL
    USING      (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- ── 2. Profiles ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    user_id     UUID  PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    theme       TEXT  DEFAULT 'midnight',
    avatar      TEXT  DEFAULT '',       -- base64 encoded image
    avatar_mime TEXT  DEFAULT 'image/jpeg',
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_profiles" ON profiles
    FOR ALL
    USING      (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);


-- ── 3. Auto-update updated_at ────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ── Done ─────────────────────────────────────────────────────
-- Tables created:
--   portfolios  (ticker, name, market_value, currency, isin, country, gics_sector, asset_type)
--   profiles    (theme, avatar, avatar_mime)
-- RLS enabled on both tables.
