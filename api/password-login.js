/**
 * POST /api/password-login
 * Body: { username, password }
 *
 * Verifies credentials against ADMIN_USERS env var (JSON array).
 * On success, returns an HTML page that sends the GitHub PAT
 * back to the CMS opener via postMessage — same format as /api/callback.
 */
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  const { username, password } = body || {};

  if (!username || !password) {
    return res.status(400).json({ error: 'username and password required' });
  }

  const users = JSON.parse(process.env.ADMIN_USERS || '[]');
  const user = users.find(
    u => u.username === username && u.password === password
  );

  if (!user) {
    return res.status(401).json({ error: 'Identifiants incorrects' });
  }

  const token = (process.env.GITHUB_TOKEN || '').trim();
  if (!token) {
    return res.status(500).json({ error: 'GitHub token not configured' });
  }

  // Fetch GitHub profile so the client can populate decap-cms-user directly
  let ghName = username, ghLogin = username;
  try {
    const ghRes = await fetch('https://api.github.com/user', {
      headers: { Authorization: `token ${token}`, 'User-Agent': 'ngor-surfcamp-admin' }
    });
    if (ghRes.ok) {
      const ghData = await ghRes.json();
      ghName  = ghData.name  || ghData.login || username;
      ghLogin = ghData.login || username;
    }
  } catch (_) {}

  return res.status(200).json({ token, provider: 'github', username, ghName, ghLogin });
}
