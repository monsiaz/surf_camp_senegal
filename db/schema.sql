-- Neon Postgres schema for Ngor Surfcamp
-- Run once: Vercel Dashboard → Storage → your DB → Query tab → paste & run

CREATE TABLE IF NOT EXISTS bookings (
  id          SERIAL PRIMARY KEY,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Guest info
  first_name  TEXT NOT NULL,
  email       TEXT NOT NULL,
  phone       TEXT,
  country     TEXT,

  -- Stay details
  arrival     DATE,
  departure   DATE,
  guests      INTEGER DEFAULT 1,
  level       TEXT,   -- beginner / intermediate / advanced
  message     TEXT,

  -- Meta
  lang        TEXT DEFAULT 'en',
  page_url    TEXT,
  status      TEXT NOT NULL DEFAULT 'new',   -- new / replied / confirmed / cancelled
  notes       TEXT   -- internal staff notes
);

CREATE INDEX IF NOT EXISTS bookings_created_at_idx ON bookings (created_at DESC);
CREATE INDEX IF NOT EXISTS bookings_status_idx     ON bookings (status);
CREATE INDEX IF NOT EXISTS bookings_email_idx      ON bookings (email);
