/**
 * Cloudflare Pages Worker — Basic Auth Protection
 * Login: simon / simon
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname;

    // Cloudflare Pages serves /path/index.html as /path/ — bare /path often 404s
    if (
      request.method === 'GET' &&
      p.length > 1 &&
      !p.endsWith('/') &&
      !p.split('/').pop().includes('.') &&
      !p.startsWith('/assets/')
    ) {
      url.pathname = p + '/';
      return Response.redirect(url.toString(), 308);
    }

    // Crawlers can read robots + sitemaps (HTML pages still require auth on demo)
    if (
      p === '/robots.txt' ||
      p === '/sitemap-index.xml' ||
      /^\/sitemap-(en|fr|es|it|de)\.xml$/.test(p)
    ) {
      return env.ASSETS.fetch(request);
    }

    // Skip auth for assets (images, css, js) for performance
    if (p.startsWith('/assets/')) {
      return env.ASSETS.fetch(request);
    }

    const authHeader = request.headers.get('Authorization');

    if (!authHeader || !isValidAuth(authHeader)) {
      return new Response(
        `<!DOCTYPE html><html><head><title>Login Required</title>
        <style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0a2540;color:white}
        .box{text-align:center;padding:40px;background:rgba(255,255,255,0.1);border-radius:12px}
        h1{font-size:24px;margin-bottom:8px}p{opacity:0.7}</style></head>
        <body><div class="box"><h1>🏄 Ngor Surfcamp Teranga</h1><p>Demo Preview — Login Required</p></div></body></html>`,
        {
          status: 401,
          headers: {
            'WWW-Authenticate': 'Basic realm="Ngor Surfcamp Demo — Login: simon / simon"',
            'Content-Type': 'text/html',
          },
        }
      );
    }

    return env.ASSETS.fetch(request);
  },
};

function isValidAuth(authHeader) {
  if (!authHeader.startsWith('Basic ')) return false;
  try {
    const encoded = authHeader.slice(6);
    const decoded = atob(encoded);
    return decoded === 'simon:simon';
  } catch {
    return false;
  }
}
