/**
 * GET /api/admin-bookings
 *
 * Returns all bookings as JSON, protected by an API key header.
 *
 * Required env vars:
 *   POSTGRES_URL    — auto-set by Vercel Postgres (Neon)
 *   ADMIN_API_KEY   — any strong secret you choose (set in Vercel env vars)
 *
 * Usage:
 *   curl https://your-site.vercel.app/api/admin-bookings \
 *        -H "x-api-key: YOUR_ADMIN_API_KEY"
 *
 * Query params:
 *   ?status=new|replied|confirmed|cancelled  (filter by status)
 *   ?limit=50                                (default 100)
 *   ?offset=0
 */

import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  // Auth check
  const apiKey = req.headers['x-api-key'];
  if (!process.env.ADMIN_API_KEY || apiKey !== process.env.ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const status = req.query.status || null;
    const limit  = Math.min(parseInt(req.query.limit)  || 100, 500);
    const offset = parseInt(req.query.offset) || 0;

    let rows;
    if (status) {
      ({ rows } = await sql`
        SELECT * FROM bookings
        WHERE  status = ${status}
        ORDER  BY created_at DESC
        LIMIT  ${limit} OFFSET ${offset}
      `);
    } else {
      ({ rows } = await sql`
        SELECT * FROM bookings
        ORDER  BY created_at DESC
        LIMIT  ${limit} OFFSET ${offset}
      `);
    }

    // Summary counts
    const { rows: counts } = await sql`
      SELECT status, COUNT(*) AS n FROM bookings GROUP BY status
    `;
    const summary = Object.fromEntries(counts.map(r => [r.status, parseInt(r.n)]));

    return res.status(200).json({ summary, bookings: rows, limit, offset });

  } catch (err) {
    console.error('Admin bookings error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
