-- Neon Postgres schema for Ngor Surfcamp
-- Run once in Neon: console.neon.tech → your branch → SQL Editor → paste & run
-- (or Vercel → Storage → your Postgres → Query)

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

-- Room availability & pricing per day
CREATE TABLE IF NOT EXISTS availability (
  date        DATE NOT NULL,
  room_type   TEXT NOT NULL DEFAULT 'shared',  -- shared / private / suite
  total       INTEGER NOT NULL DEFAULT 4,
  booked      INTEGER NOT NULL DEFAULT 0,
  price_eur   INTEGER NOT NULL DEFAULT 55,     -- price per night in EUR
  notes       TEXT,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, room_type)
);

CREATE INDEX IF NOT EXISTS avail_date_idx ON availability (date);
CREATE INDEX IF NOT EXISTS avail_room_idx ON availability (room_type, date);
