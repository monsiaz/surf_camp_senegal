#!/usr/bin/env python3
"""
Sitewide fix: correct wave-bottom divider colors.
Each wave needs:
  background = color of the section ABOVE (what the wave sits inside)
  fill       = color of the section BELOW (what the wave points into)

Logic: scan every HTML file, find every wave-bottom div, then look backwards in 
the HTML for the nearest section/div background color, and forwards for the next one.
"""
import re
import os
from pathlib import Path

ROOT  = Path(__file__).parent.parent
DEMO  = ROOT / "cloudflare-demo"

# Known background color patterns (ordered by priority)
BG_PATTERNS = [
    (r'background:\s*var\(--navy\)', '#0a2540'),
    (r'background:\s*#0a2540',       '#0a2540'),
    (r'background:\s*#07192e',       '#07192e'),
    (r'background:\s*#070f1c',       '#070f1c'),
    (r'background:\s*#0c2e4e',       '#0c2e4e'),
    (r'background:\s*#f7fafd',       '#f7fafd'),
    (r'background:\s*#f8fafd',       '#f8fafd'),
    (r'background:\s*#f8f9fa',       '#f8f9fa'),
    (r'background:\s*#fff\b',        '#ffffff'),
    (r'background:\s*#ffffff',       '#ffffff'),
    (r'background:\s*white',         '#ffffff'),
    (r'background:\s*linear-gradient\([^;)]*07192e[^;)]*\)', '#07192e'),
    (r'background:\s*linear-gradient\([^;)]*070f1c[^;)]*\)', '#070f1c'),
    (r'background:\s*linear-gradient\([^;)]*0a2540[^;)]*\)', '#0a2540'),
    (r'background:\s*linear-gradient\([^;)]*dark[^;)]*\)',   '#070f1c'),
]

WAVE_RE = re.compile(
    r'<div class="wave-bottom"[^>]*style="background:([^"]+)">'
    r'<svg[^>]*><path[^>]*fill="([^"]+)"'
)

def extract_bg_color(text: str):
    """Extract the most prominent background color from a chunk of HTML."""
    for pattern, color in BG_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return color
    return None

def fix_wave_colors_in_file(path: Path) -> int:
    html = path.read_text(encoding='utf-8')
    
    # Find all wave positions
    positions = [(m.start(), m.end(), m.group(1), m.group(2)) 
                 for m in WAVE_RE.finditer(html)]
    
    if not positions:
        return 0
    
    changes = 0
    new_html = html
    offset = 0  # Track string offset as we make replacements
    
    for start, end, current_bg, current_fill in positions:
        # Look backwards (500 chars) for the containing section's background
        look_back = html[max(0, start-1500):start]
        # Look forwards (500 chars) for the next section's background  
        look_forward = html[end:min(len(html), end+1500)]
        
        # Find last bg color in look_back (= color of section above)
        correct_bg = None
        for pattern, color in BG_PATTERNS:
            matches = list(re.finditer(pattern, look_back, re.IGNORECASE))
            if matches:
                # Take the LAST match (most recent = containing section)
                correct_bg = color
                break
        
        # Find first bg color in look_forward (= color of section below)
        correct_fill = None
        for pattern, color in BG_PATTERNS:
            if re.search(pattern, look_forward, re.IGNORECASE):
                correct_fill = color
                break
        
        # Normalize current colors
        norm_bg = current_bg.strip().lower()
        norm_fill = current_fill.strip().lower()
        if norm_bg == '#fff': norm_bg = '#ffffff'
        if norm_fill == '#fff': norm_fill = '#ffffff'
        
        # Determine what the wave should have
        target_bg   = correct_bg   or norm_bg
        target_fill = correct_fill or norm_fill
        
        # Skip if already correct
        if target_bg == norm_bg and target_fill == norm_fill:
            continue
        
        # Only fix if there's a clear mismatch worth fixing
        # Key bug: wave background is white/light but section above is dark
        DARK_COLORS = {'#07192e', '#070f1c', '#0a2540', '#0c2e4e'}
        LIGHT_COLORS = {'#ffffff', '#f7fafd', '#f8fafd', '#f8f9fa'}
        
        should_fix = False
        # Bug: wave bg is light but section above is dark
        if norm_bg in LIGHT_COLORS and target_bg in DARK_COLORS:
            should_fix = True
        # Bug: wave bg is dark but section above is light
        elif norm_bg in DARK_COLORS and target_bg in LIGHT_COLORS:
            should_fix = True
        # Bug: wave fill is wrong for section below
        elif correct_fill and target_fill != norm_fill:
            if (norm_fill in DARK_COLORS and target_fill in LIGHT_COLORS) or \
               (norm_fill in LIGHT_COLORS and target_fill in DARK_COLORS):
                should_fix = True
        
        if not should_fix:
            continue
        
        old_wave = f'background:{current_bg}"'
        new_wave = f'background:{target_bg}"'
        old_fill = f'fill="{current_fill}"'
        new_fill = f'fill="{target_fill}"'
        
        adj_start = start + offset
        adj_end   = end + offset
        chunk = new_html[adj_start:adj_end]
        
        chunk = chunk.replace(f'background:{current_bg}"', f'background:{target_bg}"', 1)
        chunk = chunk.replace(f'fill="{current_fill}"', f'fill="{target_fill}"', 1)
        
        if chunk != new_html[adj_start:adj_end]:
            new_html = new_html[:adj_start] + chunk + new_html[adj_end:]
            offset += len(chunk) - (adj_end - adj_start)
            changes += 1
            rel = path.relative_to(DEMO)
            print(f"  {rel}: bg {current_bg}→{target_bg}, fill {current_fill}→{target_fill}")
    
    if changes:
        path.write_text(new_html, encoding='utf-8')
    return changes


def main():
    total = 0
    files_fixed = 0
    # Only fix main pages, not blog articles
    for p in sorted(DEMO.rglob("index.html")):
        rel = str(p.relative_to(DEMO))
        # Skip blog article pages (too many, handled differently)
        parts = p.parts
        if "blog" in parts:
            continue
        n = fix_wave_colors_in_file(p)
        if n:
            total += n
            files_fixed += 1
    
    print(f"\n✅ Fixed {total} wave dividers across {files_fixed} pages")


if __name__ == "__main__":
    main()
