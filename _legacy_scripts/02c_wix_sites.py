"""
Decode Wix IST token and find the correct site IDs
"""
import json, requests, base64

WIX_KEY = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()
BASE    = "https://www.wixapis.com"

# ── Decode IST JWT (format: IST.header.payload.sig) ──────────────────────────
token_body = WIX_KEY[4:]  # strip "IST."
parts = token_body.split(".")
payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
decoded = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
tenant_str = decoded.get("data", "{}")
tenant_data = json.loads(tenant_str) if isinstance(tenant_str, str) else tenant_str

ACCOUNT_ID = tenant_data.get("tenant", {}).get("id", "")
APP_ID     = tenant_data.get("identity", {}).get("id", "")
print(f"Account ID : {ACCOUNT_ID}")
print(f"App ID     : {APP_ID}")

# ── Headers variants to try ───────────────────────────────────────────────────
H_BASE    = {"Authorization": WIX_KEY, "Content-Type": "application/json"}
H_ACCOUNT = {**H_BASE, "wix-account-id": ACCOUNT_ID}

tests = [
    ("GET",  "/site-list/v2/sites",            H_ACCOUNT, None),
    ("POST", "/site-list/v2/sites/query",      H_ACCOUNT, {"query": {}}),
    ("GET",  "/site-properties/v4/properties", H_ACCOUNT, None),
    ("GET",  "/accounts/v2/accounts/current",  H_ACCOUNT, None),
    ("GET",  "/premium/v2/user-packages",      H_ACCOUNT, None),
]

site_id = None
for method, path, hdrs, body in tests:
    r = requests.request(method, BASE+path, headers=hdrs, json=body, timeout=15)
    try:
        rj = r.json()
        snippet = json.dumps(rj)[:400]
    except Exception:
        snippet = r.text[:400]
    print(f"\n{method} {path} → {r.status_code}")
    print(f"  {snippet}")
    if r.status_code == 200 and "sites" in rj:
        for s in rj.get("sites", []):
            print(f"    SITE: {s.get('displayName')} id={s.get('id')} url={s.get('viewUrl')}")
            if not site_id:
                site_id = s.get("id")

# ── Try with known surfcampsenegal metaSiteId if we can discover it ───────────
# Try a known approach: use the Wix headless domain lookup
print("\n=== Trying domain lookup ===")
r_domain = requests.get(
    "https://www.wixapis.com/premium-store/v1/domains/is-connected-to-wix",
    headers=H_ACCOUNT, params={"domain": "surfcampsenegal.com"}, timeout=15
)
print(f"Domain check → {r_domain.status_code}: {r_domain.text[:300]}")

# ── Save whatever we found ────────────────────────────────────────────────────
print(f"\nDiscovered site_id: {site_id}")
with open("/Users/simonazoulay/SurfCampSenegal/output/wix_account.json","w") as f:
    json.dump({"account_id": ACCOUNT_ID, "app_id": APP_ID, "site_id": site_id}, f, indent=2)
