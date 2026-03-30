/**
 * GET /api/token-relay?token=TOKEN
 *
 * Used by the password-login flow to complete the Decap CMS GitHub handshake.
 *
 * Decap CMS uses a 2-step handshake with the OAuth popup:
 *  1. Popup  → main  : "authorizing:github"
 *  2. Main   → popup : "authorizing:github"   (main acks, sets up next listener)
 *  3. Popup  → main  : "authorization:github:success:{token,...}"
 *
 * This page handles steps 1-3 using a pre-supplied token (no real OAuth needed).
 */
export default function handler(req, res) {
  const { token } = req.query;
  if (!token) {
    return res.status(400).send('Missing token');
  }

  const safeToken = String(token).trim();
  const authMsg = JSON.stringify(
    `authorization:github:success:${JSON.stringify({ token: safeToken, provider: 'github' })}`
  );

  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Authentification…</title>
  <style>
    body { font-family: system-ui, sans-serif; display: flex; align-items: center;
           justify-content: center; min-height: 100vh; margin: 0;
           background: #0a2540; color: #fff; }
    p { opacity: .7; font-size: 14px; text-align: center; }
  </style>
</head>
<body>
  <p>✅ Connexion en cours…</p>
  <script>
  (function() {
    var authMsg = ${authMsg};

    if (!window.opener) {
      document.querySelector('p').textContent =
        '⚠️ Pas de fenêtre parente — ferme cet onglet.';
      return;
    }

    // Step 1 — send handshake to main window
    window.opener.postMessage('authorizing:github', '*');

    // Step 2 — wait for main window to ack (sends "authorizing:github" back)
    var sent = false;
    window.addEventListener('message', function onAck(e) {
      if (e.data === 'authorizing:github' && !sent) {
        sent = true;
        window.removeEventListener('message', onAck);
        // Step 3 — send the real authorization message
        window.opener.postMessage(authMsg, e.origin || '*');
        setTimeout(function() { window.close(); }, 400);
      }
    }, false);

    // Safety fallback: if no ack in 1.5 s, send directly and close
    setTimeout(function() {
      if (!sent) {
        sent = true;
        window.opener.postMessage(authMsg, '*');
        setTimeout(function() { window.close(); }, 400);
      }
    }, 1500);
  })();
  </script>
</body>
</html>`;

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.send(html);
}
