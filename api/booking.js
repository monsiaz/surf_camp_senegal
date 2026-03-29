/**
 * POST /api/booking
 *
 * Saves booking form data to Neon Postgres and sends an email notification.
 *
 * Env (Vercel auto-injects one of these when Neon is connected):
 *   POSTGRES_URL | DATABASE_URL | POSTGRES_PRISMA_URL
 * Optional:
 *   RESEND_API_KEY, NOTIFY_EMAIL
 */

import { sql, hasDb } from './_db.js';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default async function handler(req, res) {
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v));

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const {
      firstName: first_name = '',
      email = '',
      phone = '',
      country = '',
      arrival = null,
      departure = null,
      guests = 1,
      level = '',
      message = '',
      lang = 'en',
      pageUrl: page_url = '',
    } = body;

    if (!first_name.trim() || !email.trim()) {
      return res.status(400).json({ error: 'first_name and email are required' });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ error: 'Invalid email address' });
    }

    if (!hasDb || !sql) {
      console.log('[booking] No DATABASE_URL / POSTGRES_URL — logging only:', { first_name, email });
      return res.status(200).json({ ok: true, bookingId: null, message: 'Received (DB not yet connected)' });
    }

    const rows = await sql`
      INSERT INTO bookings
        (first_name, email, phone, country, arrival, departure, guests, level, message, lang, page_url)
      VALUES
        (${first_name.trim()}, ${email.trim().toLowerCase()}, ${phone || null}, ${country || null},
         ${arrival || null}, ${departure || null}, ${parseInt(guests) || 1},
         ${level || null}, ${message || null}, ${lang}, ${page_url || null})
      RETURNING id, created_at
    `;

    const booking = rows[0];

    if (process.env.RESEND_API_KEY && process.env.NOTIFY_EMAIL) {
      fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: 'Ngor Surfcamp <noreply@surfcampsenegal.com>',
          to: process.env.NOTIFY_EMAIL,
          subject: `📋 New booking #${booking.id} — ${first_name} (${email})`,
          html: `<h2>Booking request #${booking.id}</h2>
<table style="border-collapse:collapse;font-size:14px">
  <tr><td style="padding:4px 10px;font-weight:bold">Name</td><td style="padding:4px 10px">${first_name}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Email</td><td style="padding:4px 10px"><a href="mailto:${email}">${email}</a></td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Phone</td><td style="padding:4px 10px">${phone || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Arrival</td><td style="padding:4px 10px">${arrival || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Departure</td><td style="padding:4px 10px">${departure || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Guests</td><td style="padding:4px 10px">${guests}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Level</td><td style="padding:4px 10px">${level || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Message</td><td style="padding:4px 10px">${message || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Language</td><td style="padding:4px 10px">${lang}</td></tr>
</table>`,
        }),
      }).catch(e => console.error('[booking] email error:', e));
    }

    return res.status(200).json({ ok: true, bookingId: booking.id });

  } catch (err) {
    console.error('[booking] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
