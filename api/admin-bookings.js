/**
 * GET /api/admin-bookings
 *
 * Protected by x-api-key header.
 *
 * Env: POSTGRES_URL | DATABASE_URL | POSTGRES_PRISMA_URL, ADMIN_API_KEY
 */

import { sql, hasDb } from './_db.js';

export default async function handler(req, res) {
  if (!process.env.ADMIN_API_KEY || req.headers['x-api-key'] !== process.env.ADMIN_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  if (!hasDb || !sql) {
    return res.status(503).json({ error: 'Database not connected yet' });
  }

  try {
    const status = req.query.status || null;
    const limit  = Math.min(parseInt(req.query.limit) || 100, 500);
    const offset = parseInt(req.query.offset) || 0;

    const rows = status
      ? await sql`SELECT * FROM bookings WHERE status = ${status} ORDER BY created_at DESC LIMIT ${limit} OFFSET ${offset}`
      : await sql`SELECT * FROM bookings ORDER BY created_at DESC LIMIT ${limit} OFFSET ${offset}`;

    const counts = await sql`SELECT status, COUNT(*)::int AS n FROM bookings GROUP BY status`;
    const summary = Object.fromEntries(counts.map(r => [r.status, Number(r.n)]));

    return res.status(200).json({ summary, total: rows.length, bookings: rows });

  } catch (err) {
    console.error('[admin-bookings] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
