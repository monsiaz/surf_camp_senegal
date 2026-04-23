/* ─────────────────────────────────────────────────────────────────────────
   Ngor Surfcamp Teranga — Service Worker  v3
   Stamped by build.py on every deploy (CACHE_VERSION = CSS+JS MD5 hash).

   Strategy (SIMPLE & SAFE):
     /assets/**   → Cache-first  (hashed filenames = immutable, safe forever)
     Everything else → DO NOT intercept (browser + Vercel CDN handle it)

   HTML pages are intentionally NOT cached by the SW.
   Vercel edge CDN (s-maxage=3600) handles HTML performance.
   This prevents any stale-HTML or reload-loop issues.
   ───────────────────────────────────────────────────────────────────────── */

const CACHE_VERSION = 'a58b25f8'; // replaced by build.py on each build
const CACHE_ASSETS  = `ngor-assets-${CACHE_VERSION}`;

// ── Install: activate immediately ──────────────────────────────────────────
self.addEventListener('install', event => {
  self.skipWaiting();
});

// ── Activate: purge ALL stale asset caches, claim clients ──────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(k => k !== CACHE_ASSETS)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── Fetch: only intercept /assets/** ───────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Only handle same-origin asset requests
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.startsWith('/assets/')) return;

  // Cache-first for hashed assets (immutable)
  event.respondWith(cacheFirst(request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_ASSETS);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Asset unavailable', { status: 503 });
  }
}
