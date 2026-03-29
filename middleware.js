/**
 * Vercel Edge Middleware — Basic Auth (free, no $150 "Advanced Deployment Protection").
 *
 * Set in Vercel → Project → Settings → Environment Variables:
 *   BASIC_AUTH_PASSWORD  (required to enable protection — any strong secret)
 *   BASIC_AUTH_USER      (optional, default: simon)
 *
 * Unauthenticated paths (no login prompt):
 *   /api/*     — booking API + admin API (admin still needs x-api-key)
 *   /assets/*  — CSS, JS, images
 *   /robots.txt, /sitemap*
 */

import { next } from '@vercel/edge';

export default function middleware(request) {
  const url = new URL(request.url);
  const p = url.pathname;

  if (p.startsWith('/assets/')) return next();
  if (p.startsWith('/api/')) return next();
  if (p === '/robots.txt') return next();
  if (p.startsWith('/sitemap')) return next();

  const requiredPass = process.env.BASIC_AUTH_PASSWORD;
  if (!requiredPass) return next();

  const expectedUser = process.env.BASIC_AUTH_USER || 'simon';
  const auth = request.headers.get('authorization');

  if (auth && auth.startsWith('Basic ')) {
    try {
      const decoded = atob(auth.slice(6));
      const i = decoded.indexOf(':');
      const user = i >= 0 ? decoded.slice(0, i) : '';
      const pass = i >= 0 ? decoded.slice(i + 1) : '';
      if (user === expectedUser && pass === requiredPass) return next();
    } catch (_) {
      /* invalid base64 */
    }
  }

  return new Response(
    `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Accès protégé — Ngor Surfcamp</title>
<style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0a2540;color:#fff}
.box{text-align:center;padding:2.5rem;background:rgba(255,255,255,.08);border-radius:12px;max-width:22rem}
p{opacity:.75;font-size:.95rem;margin-top:.5rem}</style></head>
<body><div class="box"><h1 style="margin:0 0 .5rem;font-size:1.35rem">Ngor Surfcamp</h1><p>Démo privée — identifiez-vous via la fenêtre du navigateur.</p></div></body></html>`,
    {
      status: 401,
      headers: {
        'WWW-Authenticate': 'Basic realm="Ngor Surfcamp Demo"',
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store',
      },
    }
  );
}

export const config = {
  matcher: '/:path*',
};
