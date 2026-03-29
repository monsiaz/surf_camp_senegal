/**
 * GET /api/admin-bookings
 *
 * Returns all bookings as JSON. Protected by x-api-key header.
 *
 * Required env vars:
 *   POSTGRES_URL    — auto-set by Vercel Neon integration
 *   ADMIN_API_KEY   — any strong secret set in Vercel env vars
 *
 * Usage:
 *   curl https://your-site.vercel.app/api/admin-bookings \
 *        -H "x-api-key: YOUR_ADMIN_API_KEY"
 *
 * Query params:
 *   ?status=new|replied|confirmed|cancelled
 *   ?limit=100   (max 500)
 *   ?offset=0
 */

import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  if (!process.env.ADMIN_API_KEY || req.headers['x-api-key'] !== process.env.ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  if (!process.env.POSTGRES_URL) {
    return res.status(503).json({ error: 'Database not connected yet' });
  }

  try {
    const status = req.query.status || null;
    const limit  = Math.min(parseInt(req.query.limit) || 100, 500);
    const offset = parseInt(req.query.offset) || 0;

    const { rows } = status
      ? await sql`SELECT * FROM bookings WHERE status = ${status} ORDER BY created_at DESC LIMIT ${limit} OFFSET ${offset}`
      : await sql`SELECT * FROM bookings ORDER BY created_at DESC LIMIT ${limit} OFFSET ${offset}`;

    const { rows: counts } = await sql`SELECT status, COUNT(*) AS n FROM bookings GROUP BY status`;
    const summary = Object.fromEntries(counts.map(r => [r.status, parseInt(r.n)]));

    return res.status(200).json({ summary, total: rows.length, bookings: rows });

  } catch (err) {
    console.error('[admin-bookings] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
