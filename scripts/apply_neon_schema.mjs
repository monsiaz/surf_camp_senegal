#!/usr/bin/env node
/**
 * Apply db/schema.sql to Neon using DATABASE_URL from .env.neon.local
 * (create with: vercel env pull .env.neon.local --environment production -y)
 */
import { readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { neon } from '@neondatabase/serverless';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const envPath = join(root, '.env.neon.local');

function parseEnvLine(line) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (!m) return null;
  let v = m[2].trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1).replace(/\\n/g, '').replace(/\\"/g, '"');
  }
  return [m[1], v];
}

function loadDatabaseUrl() {
  for (const key of ['DATABASE_URL', 'POSTGRES_URL']) {
    if (process.env[key]?.trim()) return process.env[key].trim();
  }
  if (!existsSync(envPath)) {
    console.error('Missing DATABASE_URL / POSTGRES_URL and .env.neon.local');
    console.error('Run: vercel env pull .env.neon.local --environment production -y');
    process.exit(1);
  }
  const text = readFileSync(envPath, 'utf8');
  const vars = {};
  for (const line of text.split('\n')) {
    const p = parseEnvLine(line);
    if (p) vars[p[0]] = p[1];
  }
  const url = vars.DATABASE_URL || vars.POSTGRES_URL;
  if (!url) throw new Error('DATABASE_URL / POSTGRES_URL not found in .env.neon.local');
  return url;
}

const url = loadDatabaseUrl();
const sql = neon(url);
const schemaPath = join(root, 'db', 'schema.sql');
let raw = readFileSync(schemaPath, 'utf8');
raw = raw.replace(/--[^\n]*/g, '\n');
const parts = raw
  .split(';')
  .map((s) => s.trim())
  .filter(Boolean);

for (const stmt of parts) {
  await sql.query(stmt);
  console.log('OK:', stmt.split(/\s+/).slice(0, 4).join(' ') + '…');
}
console.log('Schema applied successfully.');
