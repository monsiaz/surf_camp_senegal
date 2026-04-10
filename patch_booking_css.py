import re

css_path = "/Users/simonazoulay/SurfCampSenegal/cloudflare-demo/assets/css/ngor-surfcamp.css"
with open(css_path, "r") as f:
    css = f.read()

# Add new CSS for booking header
new_css = """
/* ── Booking Header (No Hero Image) ─────────────────────── */
.booking-header {
  padding: max(140px, env(safe-area-inset-top, 0px) + 120px) 0 60px;
  background: var(--navy);
  color: #fff;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.booking-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 50% 0%, rgba(255, 90, 31, 0.15) 0%, transparent 70%);
  pointer-events: none;
}
.booking-header-inner {
  position: relative;
  z-index: 2;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.booking-header-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sand);
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.08);
  padding: 6px 16px;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.booking-header-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--fire);
}
.booking-header-h1 {
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -0.03em;
  margin: 0 0 20px;
  font-family: var(--fh);
}
.booking-header-tagline {
  font-size: clamp(16px, 2vw, 20px);
  color: rgba(255, 255, 255, 0.75);
  margin: 0 0 32px;
  line-height: 1.6;
}
.booking-header-trust {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.booking-header-trust span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 50px;
  padding: 8px 16px;
  transition: transform 0.2s var(--spring), background 0.2s;
}
.booking-header-trust span:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}
"""

if ".booking-header {" not in css:
    css += new_css

with open(css_path, "w") as f:
    f.write(css)

print("Booking CSS patched.")
