/**
 * /api/admin-availability
 *
 * GET  — list availability (same as public but with notes)
 * POST — upsert availability for date ranges
 *
 * Protected by x-api-key header (ADMIN_API_KEY env var).
 */
import crypto from 'crypto';
import { sql, hasDb } from './_db.js';

function timingSafeKeyEqual(a, b) {
  if (!a || !b || typeof a !== 'string' || typeof b !== 'string') return false;
  try {
    const ba = Buffer.from(a, 'utf8'), bb = Buffer.from(b, 'utf8');
    if (ba.length !== bb.length) return false;
    return crypto.timingSafeEqual(ba, bb);
  } catch { return false; }
}

function auth(req) {
  const secret = process.env.ADMIN_API_KEY;
  return secret && timingSafeKeyEqual(req.headers['x-api-key'], secret);
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-api-key');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (!auth(req)) return res.status(401).json({ error: 'Unauthorized' });
  if (!hasDb || !sql) return res.status(503).json({ error: 'Database not available' });

  try {
    if (req.method === 'GET') {
      const from = req.query.from || new Date().toISOString().slice(0, 10);
      const months = Math.min(parseInt(req.query.months) || 3, 12);
      const toDate = new Date(from);
      toDate.setMonth(toDate.getMonth() + months);
      const to = req.query.to || toDate.toISOString().slice(0, 10);

      const rows = await sql`SELECT date, room_type, total, booked, price_eur, notes, updated_at
                             FROM availability
                             WHERE date >= ${from}::date AND date <= ${to}::date
                             ORDER BY date, room_type`;
      return res.status(200).json({ total: rows.length, rows });
    }

    if (req.method === 'POST') {
      let body = req.body;
      if (typeof body === 'string') try { body = JSON.parse(body); } catch { body = {}; }

      const { dates, room_type, total, booked, price_eur, notes } = body || {};

      if (!dates || !Array.isArray(dates) || dates.length === 0) {
        return res.status(400).json({ error: 'dates[] required (array of YYYY-MM-DD)' });
      }
      if (!room_type) {
        return res.status(400).json({ error: 'room_type required (shared/private)' });
      }

      let updated = 0;
      for (const date of dates) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) continue;
        await sql`INSERT INTO availability (date, room_type, total, booked, price_eur, notes)
                  VALUES (${date}, ${room_type},
                          ${total ?? 4}, ${booked ?? 0}, ${price_eur ?? 55}, ${notes ?? null})
                  ON CONFLICT (date, room_type)
                  DO UPDATE SET
                    total = COALESCE(${total}, availability.total),
                    booked = COALESCE(${booked}, availability.booked),
                    price_eur = COALESCE(${price_eur}, availability.price_eur),
                    notes = COALESCE(${notes}, availability.notes),
                    updated_at = NOW()`;
        updated++;
      }

      return res.status(200).json({ ok: true, updated });
    }

    return res.status(405).json({ error: 'GET or POST only' });
  } catch (err) {
    console.error('[admin-availability] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
