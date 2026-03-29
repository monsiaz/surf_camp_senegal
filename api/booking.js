/**
 * POST /api/booking
 *
 * Receives the surf camp booking form, saves to Neon Postgres,
 * and optionally sends an email notification via Resend.
 *
 * Required env vars (set in Vercel Dashboard → Settings → Environment Variables):
 *   POSTGRES_URL         — auto-set by Vercel Postgres (Neon) integration
 *   RESEND_API_KEY       — optional, from resend.com (free tier: 3 000 emails/month)
 *   NOTIFY_EMAIL         — email address to receive booking alerts (e.g. info@surfcampsenegal.com)
 */

import { sql } from '@vercel/postgres';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default async function handler(req, res) {
  // CORS pre-flight
  if (req.method === 'OPTIONS') {
    return res.status(204).set(CORS_HEADERS).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;

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

    // Basic validation
    if (!first_name.trim() || !email.trim()) {
      return res.status(400).json({ error: 'first_name and email are required' });
    }
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRe.test(email)) {
      return res.status(400).json({ error: 'Invalid email address' });
    }

    // Save to Postgres
    const { rows } = await sql`
      INSERT INTO bookings
        (first_name, email, phone, country, arrival, departure, guests, level, message, lang, page_url)
      VALUES
        (${first_name.trim()}, ${email.trim().toLowerCase()}, ${phone}, ${country},
         ${arrival || null}, ${departure || null}, ${parseInt(guests) || 1},
         ${level}, ${message}, ${lang}, ${page_url})
      RETURNING id, created_at
    `;

    const booking = rows[0];

    // Optional email notification via Resend
    if (process.env.RESEND_API_KEY && process.env.NOTIFY_EMAIL) {
      try {
        await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: 'Ngor Surfcamp <noreply@surfcampsenegal.com>',
            to: process.env.NOTIFY_EMAIL,
            subject: `📋 New booking request from ${first_name} (${email})`,
            html: `
              <h2>New booking request #${booking.id}</h2>
              <table style="border-collapse:collapse;font-family:sans-serif;font-size:14px">
                <tr><td style="padding:6px 12px;font-weight:bold">Name</td><td style="padding:6px 12px">${first_name}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Email</td><td style="padding:6px 12px"><a href="mailto:${email}">${email}</a></td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Phone</td><td style="padding:6px 12px">${phone || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Country</td><td style="padding:6px 12px">${country || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Arrival</td><td style="padding:6px 12px">${arrival || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Departure</td><td style="padding:6px 12px">${departure || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Guests</td><td style="padding:6px 12px">${guests}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Level</td><td style="padding:6px 12px">${level || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Message</td><td style="padding:6px 12px">${message || '—'}</td></tr>
                <tr><td style="padding:6px 12px;font-weight:bold">Language</td><td style="padding:6px 12px">${lang}</td></tr>
              </table>
              <p style="margin-top:16px;font-size:12px;color:#666">
                Received ${new Date(booking.created_at).toLocaleString('fr-FR')} · Booking ID #${booking.id}
              </p>
            `,
          }),
        });
      } catch (emailErr) {
        // Non-fatal — booking is already saved
        console.error('Email notification failed:', emailErr);
      }
    }

    return res.status(200).json({
      ok: true,
      bookingId: booking.id,
      message: 'Booking saved successfully',
    });

  } catch (err) {
    console.error('Booking error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
