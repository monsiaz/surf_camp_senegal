/**
 * GET /api/availability?from=2026-04-01&to=2026-06-30&room=shared
 *
 * Returns availability + pricing for the given date range.
 * Public endpoint (no auth needed).
 */
import { sql, hasDb } from './_db.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET only' });
  if (!hasDb || !sql) return res.status(503).json({ error: 'Database not available' });

  const from = req.query.from || new Date().toISOString().slice(0, 10);
  const months = Math.min(parseInt(req.query.months) || 3, 12);
  const toDate = new Date(from);
  toDate.setMonth(toDate.getMonth() + months);
  const to = req.query.to || toDate.toISOString().slice(0, 10);
  const room = req.query.room || null;

  try {
    const rows = room
      ? await sql`SELECT date, room_type, total, booked, price_eur
                  FROM availability
                  WHERE date >= ${from}::date AND date <= ${to}::date AND room_type = ${room}
                  ORDER BY date`
      : await sql`SELECT date, room_type, total, booked, price_eur
                  FROM availability
                  WHERE date >= ${from}::date AND date <= ${to}::date
                  ORDER BY date, room_type`;

    const days = {};
    for (const r of rows) {
      const d = r.date instanceof Date ? r.date.toISOString().slice(0, 10) : String(r.date).slice(0, 10);
      if (!days[d]) days[d] = {};
      days[d][r.room_type] = {
        total: r.total,
        booked: r.booked,
        available: r.total - r.booked,
        price: r.price_eur,
      };
    }

    return res.status(200).json({ from, to, days });
  } catch (err) {
    console.error('[availability] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
