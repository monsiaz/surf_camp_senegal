/**
 * POST /api/password-login
 * Legacy password login has been disabled for security reasons.
 * Use GitHub OAuth via /api/auth instead.
 */
export default async function handler(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed. Use GitHub OAuth login.' });
  }

  return res.status(410).json({
    error: 'Password login disabled. Use "Login with GitHub".',
    oauth_url: '/api/auth?provider=github&scope=repo',
  });
}
