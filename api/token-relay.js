/**
 * GET /api/token-relay?token=TOKEN
 *
 * Legacy token relay endpoint disabled for security reasons.
 */
export default function handler(req, res) {
  return res.status(410).json({
    error: 'Legacy token relay disabled. Use /api/auth GitHub OAuth flow.',
  });
}
