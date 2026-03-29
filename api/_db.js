/**
 * Neon / Vercel Postgres connection.
 * Vercel+Neon may set POSTGRES_URL, DATABASE_URL, or POSTGRES_PRISMA_URL.
 */
import { neon } from '@neondatabase/serverless';

const url =
  process.env.POSTGRES_URL ||
  process.env.DATABASE_URL ||
  process.env.POSTGRES_PRISMA_URL;

export const sql = url ? neon(url) : null;
export const hasDb = Boolean(url);
