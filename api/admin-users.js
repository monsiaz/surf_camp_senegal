/**
 * /api/admin-users — User management CRUD
 *
 * Auth: requires Authorization: Bearer <ADMIN_USERS_API_TOKEN>
 * Users are stored in ADMIN_USERS Vercel env var (JSON array).
 * Updates go through the Vercel API using VERCEL_TOKEN.
 *
 * GET    → list users (without passwords)
 * POST   → { username, password, role? } — add user
 * PUT    → { username, password } — change password
 * DELETE → { username } — remove user
 */
import crypto from 'crypto';

const PROJECT_NAME = 'surf-camp-senegal';
const ADMIN_USERS_API_TOKEN = (process.env.ADMIN_USERS_API_TOKEN || process.env.GITHUB_TOKEN || '').trim();

function parseUsers(raw) {
  try {
    const parsed = JSON.parse(raw || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function hashPassword(plain) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(String(plain), salt, 64).toString('hex');
  return `scrypt:${salt}:${hash}`;
}

function looksHashed(stored) {
  return typeof stored === 'string' && stored.startsWith('scrypt:');
}

async function getEnvVarId(token) {
  const r = await fetch(
    `https://api.vercel.com/v9/projects/${PROJECT_NAME}/env`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  const data = await r.json();
  const envs = data.envs || [];
  const found = envs.find(e => e.key === 'ADMIN_USERS' && e.target?.includes('production'));
  return found ? found.id : null;
}

async function persistUsers(users, vercelToken) {
  const envId = await getEnvVarId(vercelToken);
  const value = JSON.stringify(users);

  if (envId) {
    await fetch(
      `https://api.vercel.com/v9/projects/${PROJECT_NAME}/env/${envId}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${vercelToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ value }),
      }
    );
  } else {
    // Create if not exists
    await fetch(
      `https://api.vercel.com/v9/projects/${PROJECT_NAME}/env`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${vercelToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          key: 'ADMIN_USERS',
          value,
          type: 'encrypted',
          target: ['production'],
        }),
      }
    );
  }
}

export default async function handler(req, res) {
  // CORS for admin panel
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  // Auth check
  const authHeader = req.headers.authorization || '';
  const bearerToken = authHeader.replace('Bearer ', '').trim();
  if (!bearerToken || !ADMIN_USERS_API_TOKEN || bearerToken !== ADMIN_USERS_API_TOKEN) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const vercelToken = process.env.VERCEL_TOKEN;
  if (!vercelToken) {
    return res.status(500).json({ error: 'VERCEL_TOKEN not configured' });
  }

  let users = parseUsers(process.env.ADMIN_USERS);

  // One-time in-memory normalization: keep legacy plaintext records readable.
  users = users.map((u) => {
    if (!u || !u.username) return null;
    return {
      username: String(u.username),
      password: String(u.password || ''),
      role: String(u.role || 'editor'),
      password_hashed: Boolean(u.password_hashed || looksHashed(u.password)),
    };
  }).filter(Boolean);

  if (req.method === 'GET') {
    return res.json({
      users: users.map(u => ({ username: u.username, role: u.role || 'editor' })),
    });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }

  if (req.method === 'POST') {
    const { username, password, role = 'editor' } = body || {};
    if (!username || !password) {
      return res.status(400).json({ error: 'username and password required' });
    }
    if (users.find(u => u.username === username)) {
      return res.status(409).json({ error: 'User already exists' });
    }
    users.push({
      username: String(username),
      password: hashPassword(password),
      role: String(role || 'editor'),
      password_hashed: true,
    });
    await persistUsers(users, vercelToken);
    return res.json({ success: true });
  }

  if (req.method === 'PUT') {
    const { username, password } = body || {};
    const user = users.find(u => u.username === username);
    if (!user) return res.status(404).json({ error: 'User not found' });
    if (!password) return res.status(400).json({ error: 'password required' });
    user.password = hashPassword(password);
    user.password_hashed = true;
    await persistUsers(users, vercelToken);
    return res.json({ success: true });
  }

  if (req.method === 'DELETE') {
    const { username } = body || {};
    const idx = users.findIndex(u => u.username === username);
    if (idx === -1) return res.status(404).json({ error: 'User not found' });
    if (users.length === 1) {
      return res.status(400).json({ error: 'Cannot delete the last admin user' });
    }
    users.splice(idx, 1);
    await persistUsers(users, vercelToken);
    return res.json({ success: true });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
