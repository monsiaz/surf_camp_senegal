"""
Step 1 – Pull GA4 traffic & Search Console data
Google service account: leafy-brace-242115-821d33bd2707.json
"""
import json, os, sys
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, DateRange, OrderBy, FilterExpression, Filter
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SA_FILE = "/Users/simonazoulay/SurfCampSenegal/leafy-brace-242115-821d33bd2707.json"
SCOPES_GA = ["https://www.googleapis.com/auth/analytics.readonly"]
SCOPES_SC = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL  = "https://www.surfcampsenegal.com/"
OUTPUT    = "/Users/simonazoulay/SurfCampSenegal/output/analytics_data.json"

creds_ga = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES_GA)
creds_sc = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES_SC)

# ── 1. List GA4 properties accessible to this service account ──────────────────
from google.analytics.admin import AnalyticsAdminServiceClient
admin_client = AnalyticsAdminServiceClient(credentials=creds_ga)

properties = []
try:
    # list account summaries
    for summary in admin_client.list_account_summaries():
        for prop in summary.property_summaries:
            properties.append({"account": summary.display_name, "property": prop.display_name, "id": prop.property})
    print(f"Found {len(properties)} GA4 properties:")
    for p in properties:
        print(f"  {p['property']}  →  {p['id']}")
except Exception as e:
    print(f"[GA Admin] {e}")

# ── 2. If we found a property, pull data ──────────────────────────────────────
ga_data = {"properties": properties, "top_pages": [], "top_queries": [], "countries": [], "search_console": {}}

if properties:
    # Pick the Ngor Surfcamp Teranga property specifically
    surf_props = [p for p in properties if "surfcamp" in p["property"].lower() or "ngor" in p["property"].lower() or "teranga" in p["property"].lower()]
    prop_id = surf_props[0]["id"] if surf_props else properties[0]["id"]
    # Numeric only
    numeric_id = prop_id.replace("properties/", "")
    print(f"\nUsing property: {prop_id}  (numeric: {numeric_id})")

    ga_client = BetaAnalyticsDataClient(credentials=creds_ga)

    # Top pages
    try:
        req = RunReportRequest(
            property=prop_id,
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[Metric(name="sessions"), Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date="2025-01-01", end_date="2026-03-27")],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
            limit=30,
        )
        resp = ga_client.run_report(req)
        for row in resp.rows:
            ga_data["top_pages"].append({
                "path": row.dimension_values[0].value,
                "title": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
                "views": int(row.metric_values[1].value),
            })
        print(f"  Top pages: {len(ga_data['top_pages'])} rows")
    except Exception as e:
        print(f"  [Top pages] {e}")

    # Top countries
    try:
        req = RunReportRequest(
            property=prop_id,
            dimensions=[Dimension(name="country"), Dimension(name="language")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="2025-01-01", end_date="2026-03-27")],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
            limit=20,
        )
        resp = ga_client.run_report(req)
        for row in resp.rows:
            ga_data["countries"].append({
                "country": row.dimension_values[0].value,
                "language": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
            })
        print(f"  Countries: {len(ga_data['countries'])} rows")
    except Exception as e:
        print(f"  [Countries] {e}")

    # Organic search queries (GA4 search console link)
    try:
        req = RunReportRequest(
            property=prop_id,
            dimensions=[Dimension(name="sessionGoogleAdsAdGroupName"),
                        Dimension(name="sessionManualAdContent")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="2025-01-01", end_date="2026-03-27")],
            limit=20,
        )
    except Exception as e:
        pass

# ── 3. Search Console ─────────────────────────────────────────────────────────
try:
    sc_service = build("searchconsole", "v1", credentials=creds_sc)
    # List sites to verify access
    sites_list = sc_service.sites().list().execute()
    sc_sites = [s["siteUrl"] for s in sites_list.get("siteEntry", [])]
    print(f"\nSearch Console sites: {sc_sites}")
    ga_data["search_console"]["accessible_sites"] = sc_sites

    # Queries report
    sc_target = SITE_URL if SITE_URL in sc_sites else (sc_sites[0] if sc_sites else None)
    if sc_target:
        body = {
            "startDate": "2025-10-01",
            "endDate":   "2026-03-27",
            "dimensions": ["query"],
            "rowLimit": 50,
            "startRow": 0,
        }
        resp = sc_service.searchanalytics().query(siteUrl=sc_target, body=body).execute()
        ga_data["search_console"]["top_queries"] = resp.get("rows", [])
        print(f"  SC queries: {len(ga_data['search_console']['top_queries'])} rows")

        # Top pages
        body2 = {
            "startDate": "2025-10-01",
            "endDate":   "2026-03-27",
            "dimensions": ["page"],
            "rowLimit": 30,
        }
        resp2 = sc_service.searchanalytics().query(siteUrl=sc_target, body=body2).execute()
        ga_data["search_console"]["top_pages"] = resp2.get("rows", [])
        print(f"  SC pages: {len(ga_data['search_console']['top_pages'])} rows")

        # Top countries
        body3 = {
            "startDate": "2025-10-01",
            "endDate":   "2026-03-27",
            "dimensions": ["country"],
            "rowLimit": 20,
        }
        resp3 = sc_service.searchanalytics().query(siteUrl=sc_target, body=body3).execute()
        ga_data["search_console"]["countries"] = resp3.get("rows", [])
        print(f"  SC countries: {len(ga_data['search_console']['countries'])} rows")

except Exception as e:
    print(f"[Search Console] {e}")

# Save
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w") as f:
    json.dump(ga_data, f, indent=2, default=str)
print(f"\nData saved → {OUTPUT}")
