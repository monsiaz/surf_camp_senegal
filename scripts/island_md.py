"""Markdown to HTML for island guide articles (same block model as blog v2)."""
import os
import re


def md2html_island(md, lang="en", icons_dir="", ico_base="/assets/images/icons"):
    if not md:
        return ""
    md = re.sub(r",\s*,", ",", str(md).replace(" — ", ", ").replace("—", ",").replace("\u2014", ",").replace(" – ", ", ").replace("–", ","))

    def icon_img(name, size=24, alt=""):
        local = f"{icons_dir}/{name}.png"
        if icons_dir and os.path.exists(local):
            return (
                f'<img src="{ico_base}/{name}.png" alt="{alt}" width="{size}" height="{size}" '
                f'style="display:inline-block;vertical-align:middle;object-fit:contain">'
            )
        FALLBACKS = {
            "icon-tip": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><circle cx="12" cy="12" r="10" stroke="#ff6b35" stroke-width="2"/><path d="M12 7v5M12 16v.5" stroke="#ff6b35" stroke-width="2.5" stroke-linecap="round"/></svg>',
            "icon-summary": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#0a2540" stroke-width="2"/><path d="M7 8h10M7 12h10M7 16h6" stroke="#0a2540" stroke-width="2" stroke-linecap="round"/></svg>',
            "icon-checklist": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><path d="M9 12l2 2 4-4" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round"/><rect x="3" y="3" width="18" height="18" rx="3" stroke="#22c55e" stroke-width="2"/></svg>',
            "icon-quote": '<svg viewBox="0 0 24 24" fill="#f0d6a4" style="width:{s}px;height:{s}px"><path d="M3 12C3 7.5 6 4 9 3l1 2C7 6.5 5.5 9 6 11h3v6H3v-5zm11 0c0-4.5 3-7.5 6-8.5l1 2C18 7 16.5 9.5 17 12h3v6h-6v-6z"/></svg>',
            "icon-federation": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><path d="M12 2l7 4v6c0 4-3 7.5-7 9-4-1.5-7-5-7-9V6l7-4z" stroke="#ff6b35" stroke-width="2"/><path d="M9 12l2 2 4-4" stroke="#ff6b35" stroke-width="2" stroke-linecap="round"/></svg>',
            "icon-coaching": '<svg viewBox="0 0 24 24" fill="none" style="width:{s}px;height:{s}px"><circle cx="12" cy="12" r="9" stroke="#b45309" stroke-width="2"/><path d="M12 8v4l3 2" stroke="#b45309" stroke-width="2" stroke-linecap="round"/></svg>',
        }
        fb = FALLBACKS.get(name, FALLBACKS.get("icon-tip", "")).replace("{s}", str(size))
        return fb if fb else ""

    lines = md.split("\n")
    out = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def to_id(text):
        return re.sub(r"[^a-z0-9-]", "-", text.lower().strip())[:50].rstrip("-")

    def inline(t):
        t = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<![*])\*(?![*])(.*?)(?<![*])\*(?![*])", r"<em>\1</em>", t)

        def mk_ilink(m):
            parts = m.group(0)[6:-1].split("->")
            a2 = parts[0].strip()
            tgt = parts[1].strip() if len(parts) > 1 else "#"
            return (
                f'<a href="{tgt}/" class="ilink" style="color:var(--fire);font-weight:600;'
                f'display:inline-flex;align-items:center;gap:4px">→ {a2}</a>'
            )

        t = re.sub(r"\[LINK:[^\]]+\]", mk_ilink, t)
        return t

    TIP_KW = ("**TIP:", "**CONSEIL:", "**TIPP:", "**CONSEJO:", "**CONSIGLIO:")
    NOTE_KW = ("**NOTE:", "**REMARQUE:", "**HINWEIS:", "**NOTA:")
    FACT_KW = ("**FACT:", "**FAIT:", "**HECHO:", "**FATTO:", "**FAKT:")
    EXP_KW = ("**EXPERT:", "**EXPERT ", "**QUOTE:", "**CITATION:")
    CHKL_KW = ("**CHECKLIST:", "**CHECK:")
    SUM_KW = ("**SUMMARY:", "**SYNTHÈSE:", "**RESUMEN:", "**SINTESI:", "**FAZIT:", "**ZUSAMMENFASSUNG:")

    BLOCK_LABELS = {
        "tip": {"en": "Pro Tip", "fr": "Conseil Pro", "es": "Consejo Pro", "it": "Consiglio Pro", "de": "Profi-Tipp"},
        "fact": {"en": "Did You Know", "fr": "Le Saviez-Vous", "es": "Sabías Que", "it": "Lo Sapevi", "de": "Wusstest Du"},
        "expert": {"en": "From the Coaches", "fr": "Depuis les Coachs", "es": "De los Coaches", "it": "Dai Coach", "de": "Von den Coaches"},
        "checklist": {"en": "Action Checklist", "fr": "Checklist d'Action", "es": "Lista de Acciones", "it": "Checklist", "de": "Aktionsliste"},
        "summary": {"en": "Key Takeaways", "fr": "Points Clés", "es": "Puntos Clave", "it": "Punti Chiave", "de": "Wichtige Punkte"},
    }

    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            close_lists()
            i += 1
            continue

        if s in ("## Contents", "## Sommaire", "## Tabla de Contenidos", "## Indice", "## Inhaltsverzeichnis"):
            close_lists()
            toc_title = (
                "Contents"
                if lang == "en"
                else "Sommaire"
                if lang == "fr"
                else "Contenido"
                if lang == "es"
                else "Indice"
                if lang == "it"
                else "Inhalt"
            )
            out.append(
                f'<nav class="toc-block" aria-label="Table of contents"><div class="toc-title">{toc_title}</div>'
                f'<ol class="toc-list">'
            )
            i += 1
            while i < len(lines) and lines[i].strip().startswith("- "):
                item = lines[i].strip()[2:].strip()
                anchor = to_id(item)
                out.append(f'<li><a href="#{anchor}">{inline(item)}</a></li>')
                i += 1
            out.append("</ol></nav>")
            continue

        if s.startswith("#### "):
            close_lists()
            out.append(f"<h4>{inline(s[5:])}</h4>")
        elif s.startswith("### "):
            close_lists()
            out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            close_lists()
            txt = inline(s[3:])
            anchor = to_id(s[3:])
            out.append(f'<h2 id="{anchor}">{txt}</h2>')
        elif s.startswith("# "):
            close_lists()
            out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("> "):
            close_lists()
            out.append(
                f'<div class="pull-quote">{icon_img("icon-quote", 36, "Quote")}'
                f'<blockquote class="pq-txt">{inline(s[2:])}</blockquote></div>'
            )
        elif any(s.upper().startswith(k) for k in TIP_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]+:\*?\*?\s*", "", s)
            lbl = BLOCK_LABELS["tip"].get(lang, "Tip")
            out.append(
                f'<div class="vblock vb-tip"><div class="vb-ico">{icon_img("icon-tip", 28, lbl)}</div>'
                f'<div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>'
            )
        elif any(s.upper().startswith(k) for k in FACT_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]+:\*?\*?\s*", "", s)
            lbl = BLOCK_LABELS["fact"].get(lang, "Did You Know")
            out.append(
                f'<div class="vblock vb-fact"><div class="vb-ico">{icon_img("icon-federation", 28, lbl)}</div>'
                f'<div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>'
            )
        elif any(s.upper().startswith(k) for k in EXP_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]*:\*?\*?\s*", "", s)
            lbl = BLOCK_LABELS["expert"].get(lang, "From the Coaches")
            out.append(
                f'<div class="vblock vb-expert"><div class="vb-ico">{icon_img("icon-coaching", 28, lbl)}</div>'
                f'<div><span class="vb-label">{lbl}</span>'
                f'<blockquote style="margin:0;font-style:italic">{inline(ct)}</blockquote></div></div>'
            )
        elif any(s.upper().startswith(k) for k in NOTE_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]+:\*?\*?\s*", "", s)
            out.append(
                f'<div class="vblock vb-note"><div class="vb-ico">{icon_img("icon-tip", 28, "Note")}</div>'
                f'<div><span class="vb-label">Note</span><p>{inline(ct)}</p></div></div>'
            )
        elif any(s.upper().startswith(k) for k in SUM_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]+:\*?\*?\s*", "", s)
            lbl = BLOCK_LABELS["summary"].get(lang, "Key Takeaways")
            out.append(
                f'<div class="vblock vb-summary"><div class="vb-ico">{icon_img("icon-summary", 28, lbl)}</div>'
                f'<div><span class="vb-label">{lbl}</span><p>{inline(ct)}</p></div></div>'
            )
        elif any(s.upper().startswith(k) for k in CHKL_KW):
            close_lists()
            ct = re.sub(r"^\*\*[^:]+:\*?\*?\s*", "", s)
            lbl = BLOCK_LABELS["checklist"].get(lang, "Action Checklist")
            items = [x.strip().lstrip("-").strip() for x in ct.split(",") if x.strip()]
            if len(items) <= 1:
                items_html_parts = f"<p>{inline(ct)}</p>"
            else:
                items_html_parts = (
                    '<ul class="checklist-items">'
                    + "".join(
                        f'<li>{icon_img("icon-checklist", 16, "check")} {inline(it)}</li>' for it in items
                    )
                    + "</ul>"
                )
            out.append(
                f'<div class="vblock vb-checklist"><div class="vb-ico">{icon_img("icon-checklist", 28, lbl)}</div>'
                f'<div><span class="vb-label">{lbl}</span>{items_html_parts}</div></div>'
            )
        elif re.match(r"^[-*]\s", s):
            if not in_ul:
                out.append('<ul class="prose-ul">')
                in_ul = True
            if in_ol:
                out.append("</ol>")
                in_ol = False
            out.append(f"<li>{inline(s[2:])}</li>")
        elif re.match(r"^\d+\.\s", s):
            if not in_ol:
                out.append('<ol class="prose-ol">')
                in_ol = True
            if in_ul:
                out.append("</ul>")
                in_ul = False
            item = re.sub(r"^\d+\.\s", "", s)
            out.append(f"<li>{inline(item)}</li>")
        elif s.startswith("**") and s.endswith("**") and s.count("**") == 2:
            close_lists()
            t2 = s.strip("*")
            if "?" in t2:
                out.append(f'<h4 class="faq-inline-q">{t2}</h4>')
            else:
                out.append(f"<h4>{t2}</h4>")
        else:
            close_lists()
            p = inline(s)
            if p:
                if s.startswith('"') and s.endswith('"') and len(s) > 60:
                    out.append(f'<div class="pull-quote mini"><blockquote class="pq-txt">{p}</blockquote></div>')
                else:
                    out.append(f"<p>{p}</p>")
        i += 1

    close_lists()
    return "\n".join(out)
