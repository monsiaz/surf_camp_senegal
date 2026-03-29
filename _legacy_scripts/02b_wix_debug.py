"""
Debug Wix API – find the right site ID and working endpoints
"""
import json, requests, base64

WIX_KEY = open("/Users/simonazoulay/SurfCampSenegal/clesapi.txt").read().strip()

# ── Decode the JWT payload to find tenant/site id ────────────────────────────
parts = WIX_KEY.split(".")
if len(parts) >= 2:
    payload = parts[1]
    # pad base64
    payload += "=" * (4 - len(payload) % 4)
    try:
        decoded = json.loads(base64.urlsafe_b64decode(payload).decode())
        print("JWT payload:", json.dumps(decoded, indent=2))
        tenant = decoded.get("data", "{}")
        if isinstance(tenant, str):
            tenant_data = json.loads(tenant)
            print("Tenant data:", json.dumps(tenant_data, indent=2))
            account_id = tenant_data.get("tenant", {}).get("id", "")
            app_id     = tenant_data.get("identity", {}).get("id", "")
            print(f"\nAccount ID: {account_id}")
            print(f"App ID:     {app_id}")
    except Exception as e:
        print("Decode error:", e)

BASE    = "https://www.wixapis.com"
HEADERS = {"Authorization": WIX_KEY, "Content-Type": "application/json"}

endpoints_to_test = [
    ("GET", "/site-list/v2/sites", None),
    ("POST", "/site-list/v2/sites/query", {"query": {}}),
    ("GET", "/site-properties/v4/properties", None),
    ("GET", "/pages/v2/pages", None),
    ("GET", "/blog/v3/posts?paging.limit=3", None),
    ("GET", "/premium/v2/user-packages", None),
    ("GET", "/identity/v1/accounts/current", None),
]

print("\n=== Testing endpoints ===")
for method, path, body in endpoints_to_test:
    try:
        url = BASE + path
        r = requests.request(method, url, headers=HEADERS, json=body, timeout=15)
        try:
            resp = r.json()
            snippet = json.dumps(resp)[:300]
        except Exception:
            snippet = r.text[:300]
        print(f"\n{method} {path}")
        print(f"  Status: {r.status_code}")
        print(f"  Body:   {snippet}")
    except Exception as e:
        print(f"\n{method} {path} → ERROR: {e}")
