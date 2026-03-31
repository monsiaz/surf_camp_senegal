/**
 * GET /api/callback?code=...
 * GitHub OAuth callback for Decap CMS.
 * Exchanges the authorization code for an access token, then sends it
 * back to the CMS opener window via postMessage.
 */
function getCookie(req, key) {
  const raw = req.headers.cookie || '';
  const parts = raw.split(';');
  for (const part of parts) {
    const idx = part.indexOf('=');
    if (idx < 0) continue;
    const k = part.slice(0, idx).trim();
    if (k !== key) continue;
    return decodeURIComponent(part.slice(idx + 1).trim());
  }
  return '';
}

export default async function handler(req, res) {
  const { code, error, error_description, state } = req.query;
  res.setHeader('Set-Cookie', 'oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/api/callback; Max-Age=0');

  if (error) {
    const html = renderPage('error', { error, message: error_description || error });
    return res.status(400).setHeader('Content-Type', 'text/html').send(html);
  }

  if (!code) {
    return res.status(400).setHeader('Content-Type', 'text/html')
      .send(renderPage('error', { error: 'missing_code', message: 'No authorization code received.' }));
  }

  const expectedState = getCookie(req, 'oauth_state');
  if (!state || !expectedState || state !== expectedState) {
    return res.status(400).setHeader('Content-Type', 'text/html').send(
      renderPage('error', {
        error: 'invalid_state',
        message: 'OAuth state mismatch. Restart the login flow.',
      })
    );
  }

  try {
    const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        client_id: process.env.OAUTH_CLIENT_ID,
        client_secret: process.env.OAUTH_CLIENT_SECRET,
        code,
      }),
    });

    const data = await tokenRes.json();

    if (data.error) {
      const html = renderPage('error', { error: data.error, message: data.error_description });
      return res.status(401).setHeader('Content-Type', 'text/html').send(html);
    }

    const token = (data.access_token || '').trim();
    const html = renderPage('success', { token, provider: 'github' });
    res.setHeader('Content-Type', 'text/html').send(html);

  } catch (err) {
    const html = renderPage('error', { error: 'fetch_failed', message: err.message });
    res.status(500).setHeader('Content-Type', 'text/html').send(html);
  }
}

function renderPage(status, payload) {
  if (status === 'success') {
    const { token, provider } = payload;
    // Decap CMS listens for this postMessage format:
    // "authorization:<provider>:success:<json>"
    const message = `authorization:${provider}:success:${JSON.stringify({ token, provider })}`;
    return `<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Authenticating…</title>
<style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0a2540;color:#fff}
p{opacity:.7;font-size:14px}</style>
</head><body>
<div style="text-align:center">
  <p>✅ Authentification réussie — fermeture en cours…</p>
</div>
<script>
(function() {
  function send(e) {
    window.opener.postMessage(${JSON.stringify(message)}, e.origin);
  }
  window.addEventListener("message", send, false);
  // Trigger the handshake
  if (window.opener) {
    window.opener.postMessage("authorizing:github", "*");
  } else {
    document.querySelector('p').textContent = 'Pas de fenêtre parente détectée. Ferme cet onglet.';
  }
})();
</script>
</body></html>`;
  }

  // Error page
  const { error, message } = payload;
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Erreur OAuth</title>
<style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#0a2540;color:#fff}
.box{background:rgba(255,90,31,.15);border:1px solid rgba(255,90,31,.4);border-radius:12px;padding:28px 32px;max-width:420px}
h2{color:#ff5a1f;margin:0 0 10px}code{background:rgba(255,255,255,.1);padding:2px 6px;border-radius:4px;font-size:13px}
</style></head><body>
<div class="box">
  <h2>Erreur OAuth</h2>
  <p><code>${error}</code></p>
  <p style="opacity:.75;font-size:14px;margin-top:8px">${message || ''}</p>
  <button onclick="window.close()" style="margin-top:16px;padding:8px 18px;background:#ff5a1f;color:#fff;border:none;border-radius:8px;cursor:pointer">Fermer</button>
</div>
</body></html>`;
}
