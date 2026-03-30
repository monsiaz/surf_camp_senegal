/**
 * POST /api/booking
 *
 * Saves booking form data to Neon Postgres and sends an email notification.
 *
 * Env (Vercel auto-injects one of these when Neon is connected):
 *   POSTGRES_URL | DATABASE_URL | POSTGRES_PRISMA_URL
 * Optional:
 *   RESEND_API_KEY, NOTIFY_EMAIL
 *   ALLOWED_ORIGINS — comma-separated exact origins (e.g. https://www.example.com)
 *     If unset, allows production hostnames + *.vercel.app + http://localhost:* for dev.
 */

import { sql, hasDb } from './_db.js';

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function clip(s, max) {
  const t = String(s ?? '');
  return t.length > max ? t.slice(0, max) : t;
}

const MAX_LEN = {
  first_name: 120,
  email: 254,
  phone: 60,
  country: 80,
  message: 8000,
  level: 80,
  page_url: 2048,
  lang: 12,
};

function isAllowedOrigin(origin) {
  if (!origin) return true;
  const list = (process.env.ALLOWED_ORIGINS || '')
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean);
  if (list.length) return list.includes(origin);
  try {
    const u = new URL(origin);
    const host = u.hostname;
    if (host === 'localhost' || host === '127.0.0.1') return true;
    if (u.protocol === 'https:' && host.endsWith('.vercel.app')) return true;
    const allow = new Set([
      'surfcampsenegal.com',
      'www.surfcampsenegal.com',
      'surf-camp-senegal.vercel.app',
    ]);
    return allow.has(host);
  } catch {
    return false;
  }
}

export default async function handler(req, res) {
  const origin = req.headers.origin;
  if (origin && !isAllowedOrigin(origin)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  } else {
    res.setHeader('Access-Control-Allow-Origin', '*');
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const cl = req.headers['content-length'];
  if (cl && Number(cl) > 65536) {
    return res.status(413).json({ error: 'Payload too large' });
  }

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    let {
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

    first_name = clip(first_name, MAX_LEN.first_name).trim();
    email = clip(email, MAX_LEN.email).trim();
    phone = clip(phone, MAX_LEN.phone).trim();
    country = clip(country, MAX_LEN.country).trim();
    level = clip(level, MAX_LEN.level).trim();
    message = clip(message, MAX_LEN.message).trim();
    lang = clip(lang, MAX_LEN.lang).replace(/[^a-z-]/gi, '').toLowerCase() || 'en';
    page_url = clip(page_url, MAX_LEN.page_url).trim();

    if (!first_name || !email) {
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
        (${first_name}, ${email.toLowerCase()}, ${phone || null}, ${country || null},
         ${arrival || null}, ${departure || null}, ${parseInt(guests, 10) || 1},
         ${level || null}, ${message || null}, ${lang}, ${page_url || null})
      RETURNING id, created_at
    `;

    const booking = rows[0];

    if (process.env.RESEND_API_KEY && process.env.NOTIFY_EMAIL) {
      const safe = {
        first_name: escapeHtml(first_name),
        email: escapeHtml(email),
        phone: escapeHtml(phone),
        country: escapeHtml(country),
        arrival: escapeHtml(String(arrival ?? '—')),
        departure: escapeHtml(String(departure ?? '—')),
        guests: escapeHtml(String(guests)),
        level: escapeHtml(level),
        message: escapeHtml(message).replace(/\n/g, '<br>'),
        lang: escapeHtml(lang),
      };
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
  <tr><td style="padding:4px 10px;font-weight:bold">Name</td><td style="padding:4px 10px">${safe.first_name}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Email</td><td style="padding:4px 10px"><a href="mailto:${safe.email}">${safe.email}</a></td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Phone</td><td style="padding:4px 10px">${safe.phone || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Arrival</td><td style="padding:4px 10px">${safe.arrival}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Departure</td><td style="padding:4px 10px">${safe.departure}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Guests</td><td style="padding:4px 10px">${safe.guests}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Level</td><td style="padding:4px 10px">${safe.level || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Message</td><td style="padding:4px 10px">${safe.message || '—'}</td></tr>
  <tr><td style="padding:4px 10px;font-weight:bold">Language</td><td style="padding:4px 10px">${safe.lang}</td></tr>
</table>`,
        }),
      }).catch((e) => console.error('[booking] email error:', e));
    }

    return res.status(200).json({ ok: true, bookingId: booking.id });
  } catch (err) {
    console.error('[booking] error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
