/* ─────────────────────────────────────────────────────────────────────────
   Ngor Surfcamp Teranga — Service Worker
   Strategy:
     /assets/**   → Cache-first  (hashed filenames, immutable)
     navigation   → Stale-while-revalidate  (instant load, bg refresh)
     everything else → Network-first with cache fallback
   ───────────────────────────────────────────────────────────────────────── */

const CACHE_VERSION = 'a8f099ab'; // replaced by build.py on each build
const CACHE_ASSETS  = `ngor-assets-${CACHE_VERSION}`;
const CACHE_PAGES   = `ngor-pages-${CACHE_VERSION}`;
const CACHE_MAX_AGE = 7 * 24 * 60 * 60 * 1000; // 7 days for pages

// Warm-up: pre-cache only the absolute critical assets so install is fast
const PRECACHE = [
  '/',
  '/offline.html',
];

// ── Install: pre-cache critical shell ──────────────────────────────────────
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_PAGES).then(cache =>
      cache.addAll(PRECACHE.map(url => new Request(url, { cache: 'reload' })))
        .catch(() => {/* offline during install — ignore */})
    )
  );
});

// ── Activate: purge stale caches ───────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_ASSETS && k !== CACHE_PAGES)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch ───────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;

  // Only handle GET
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Skip cross-origin (CDN, GA, …) — let the browser & its own cache handle
  if (url.origin !== self.location.origin) return;

  // Skip admin / API routes
  if (url.pathname.startsWith('/admin')) return;

  // ── /assets/** → Cache-first (immutable, hashed names) ─────────────────
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(cacheFirst(request, CACHE_ASSETS));
    return;
  }

  // ── HTML navigation → Stale-while-revalidate ────────────────────────────
  if (request.mode === 'navigate' ||
      request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(staleWhileRevalidate(request, CACHE_PAGES));
    return;
  }

  // ── Everything else (fonts.css, sw.js, favicons…) → Network-first ───────
  event.respondWith(networkFirst(request, CACHE_PAGES));
});

// ── Strategy helpers ────────────────────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache   = await caches.open(cacheName);
  const cached  = await cache.match(request);

  // Kick off a background network fetch regardless
  const networkFetch = fetch(request).then(response => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  }).catch(() => null);

  // Return cached immediately if fresh enough; else await network
  if (cached) {
    const cachedDate = cached.headers.get('sw-cached-at');
    const age = cachedDate ? Date.now() - Number(cachedDate) : 0;
    if (age < CACHE_MAX_AGE) return cached;
  }

  // No fresh cache — wait for network
  const net = await networkFetch;
  if (net) return net;
  if (cached) return cached;
  return caches.match('/offline.html') ||
    new Response('<h1>Offline</h1>', {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || new Response('Offline', { status: 503 });
  }
}
