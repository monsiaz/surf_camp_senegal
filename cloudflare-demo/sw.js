/* ─────────────────────────────────────────────────────────────────────────
   Ngor Surfcamp Teranga — Service Worker  v2
   Stamped by build.py on every deploy (CACHE_VERSION = CSS+JS MD5 hash).

   Strategy (by request type):
     /assets/**   → Cache-first   (hashed filenames = immutable)
     HTML pages   → Network-first → cache only as offline fallback
     Everything else → Network-first → cache fallback

   This guarantees HTML is ALWAYS fresh after a deployment.
   The offline fallback still works when there's no network at all.
   ───────────────────────────────────────────────────────────────────────── */

const CACHE_VERSION = 'af75f89a'; // replaced by build.py on each build
const CACHE_ASSETS  = `ngor-assets-${CACHE_VERSION}`;
const CACHE_PAGES   = `ngor-pages-${CACHE_VERSION}`;

// ── Install: pre-cache the offline fallback only ───────────────────────────
self.addEventListener('install', event => {
  self.skipWaiting(); // activate immediately, don't wait for old tabs to close
  event.waitUntil(
    caches.open(CACHE_PAGES)
      .then(c => c.add(new Request('/offline.html', { cache: 'reload' })))
      .catch(() => {/* offline during install — ignore */})
  );
});

// ── Activate: purge ALL stale caches, take control immediately ─────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(k => k !== CACHE_ASSETS && k !== CACHE_PAGES)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── Version check message from page JS ─────────────────────────────────────
// Pages embed <meta name="x-build" content="HASH">.
// On load, JS asks the SW: "is your version the same as mine?"
// If not → SW tells the page to reload → guarantees version sync.
self.addEventListener('message', event => {
  if (!event.data) return;

  if (event.data.type === 'CHECK_VERSION') {
    if (event.data.version !== CACHE_VERSION) {
      // Our version is different → tell the page to reload so it gets fresh HTML
      if (event.source) {
        event.source.postMessage({ type: 'VERSION_MISMATCH' });
      }
    }
  }

  // Manual skip-waiting trigger (optional, for future use)
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// ── Fetch ───────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;

  // Only handle GET
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Skip cross-origin (CDN, GA, Maps…) — browser handles its own caching
  if (url.origin !== self.location.origin) return;

  // Skip admin routes
  if (url.pathname.startsWith('/admin')) return;

  // ── /assets/** → Cache-first (immutable hashed filenames) ──────────────
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(cacheFirst(request, CACHE_ASSETS));
    return;
  }

  // ── HTML navigation → Network-first, offline fallback ──────────────────
  // HTML is NEVER served stale from cache — always goes to network.
  // The Vercel edge CDN (s-maxage=3600) handles performance; the SW just
  // ensures the browser always sees the freshest deployment.
  if (request.mode === 'navigate' ||
      (request.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(networkFirstHtml(request));
    return;
  }

  // ── Everything else (fonts.css, favicons…) → Network-first ─────────────
  event.respondWith(networkFirst(request, CACHE_PAGES));
});

// ── Strategy helpers ────────────────────────────────────────────────────────

/** Cache-first: instant for hashed assets. Fetches + caches on first miss. */
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
    return new Response('Asset unavailable offline', { status: 503 });
  }
}

/** Network-first for HTML: always try network; cache only as offline backup. */
async function networkFirstHtml(request) {
  const cache = await caches.open(CACHE_PAGES);
  try {
    const response = await fetch(request);
    if (response.ok) {
      // Save a copy for offline use (overwrite old stale version)
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // No network → serve cached version (offline)
    const cached = await cache.match(request);
    if (cached) return cached;
    const offline = await caches.match('/offline.html');
    return offline || new Response(
      '<!DOCTYPE html><html><body><h1>You are offline</h1><p><a href="/">Retry</a></p></body></html>',
      { status: 503, headers: { 'Content-Type': 'text/html' } }
    );
  }
}

/** Network-first for misc resources. */
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
    return cached || new Response('Unavailable offline', { status: 503 });
  }
}
