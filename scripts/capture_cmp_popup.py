#!/usr/bin/env python3
"""Serve cloudflare-demo briefly and screenshot the CMP banner (requires playwright)."""
import http.server
import os
import socketserver
import threading
import time

from playwright.sync_api import sync_playwright

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUT = os.path.join(_BASE, "output", "cmp-popup.png")
_DEMO = os.path.join(_BASE, "cloudflare-demo")
_PORT = 8765


def main():
    os.makedirs(os.path.dirname(_OUT), exist_ok=True)
    os.chdir(_DEMO)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", _PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.2)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{_PORT}/", wait_until="networkidle", timeout=60000)
            # #cc-main may be aria-hidden while the inner .cm banner is visible
            page.wait_for_selector(".cm", state="visible", timeout=20000)
            time.sleep(0.5)
            page.screenshot(path=_OUT, full_page=False)
            browser.close()
    finally:
        httpd.shutdown()
    print(_OUT)


if __name__ == "__main__":
    main()
