/**
 * GET /api/auth?provider=github&scope=repo
 * Initiates the GitHub OAuth flow for Decap CMS.
 * Redirects the user to GitHub authorization page.
 */
export default function handler(req, res) {
  const { provider = 'github', scope = 'repo' } = req.query;

  if (provider !== 'github') {
    return res.status(400).json({ error: 'Only "github" provider is supported.' });
  }

  const clientId = process.env.OAUTH_CLIENT_ID;
  if (!clientId) {
    return res.status(500).json({ error: 'OAUTH_CLIENT_ID env var not set.' });
  }

  const redirectUri = `https://${req.headers.host}/api/callback`;

  const params = new URLSearchParams({
    client_id: clientId,
    scope,
    redirect_uri: redirectUri,
  });

  res.redirect(302, `https://github.com/login/oauth/authorize?${params.toString()}`);
}
