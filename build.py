"""Builds the Sixth String public pages (privacy, terms, support, security) from Markdown.
Legal text comes from the monorepo's reviewed drafts in 03-guitar/Compliance; their internal
'Draft prepared' banner and 'To complete before publishing' checklist are stripped here."""
import html, re, pathlib, sys
ROOT = pathlib.Path(__file__).parent
COMP = pathlib.Path.home() / "Developer/01.-All-Apps/03-guitar/Compliance"
EFFECTIVE = "9 October 2026"

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(?<![\w/\">])(ico\.org\.uk|findahelpline\.com)", r'<a href="https://\1">\1</a>', t)
    return t

def md_to_html(md):
    out, para, lst, table = [], [], [], []
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
        if lst: out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>"); lst.clear()
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table if not re.match(r"^\|?\s*-", r.strip().strip("|"))]
            h, body = rows[0], rows[1:]
            out.append('<div class="table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in h) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
            table.clear()
    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("|"): para and flush(); lst and flush(); table.append(s); continue
        if table: flush()
        if not s: flush(); continue
        m = re.match(r"^(#{1,3}) (.*)", s)
        if m: flush(); n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
        if s.startswith("- "): para and flush(); lst.append(s[2:]); continue
        if lst: flush()
        para.append(s)
    flush()
    return "\n".join(out)

def clean_draft(md):
    md = re.sub(r"^\*Draft prepared.*\n", "", md, flags=re.M)
    md = re.sub(r"## To complete before publishing\n(?:- .*\n)+", "", md)
    md = md.replace("[EFFECTIVE DATE]", EFFECTIVE)
    left = re.findall(r"\[[A-Z][A-Z /:,-]{3,}[^\]]*\]", md)
    if left: sys.exit(f"Unresolved placeholders: {left}")
    return md

def security_page(md):
    md = re.sub(r"\n## [^\n]*security\.txt.*", "", md, flags=re.S | re.I)
    md = re.sub(r"^- \[(CANONICAL|POLICY|PGP)[^\n]*\n", "", md, flags=re.M)
    return clean_draft(md).strip()

STYLE = """
:root{--bg:#fbfaf8;--fg:#1b1a19;--muted:#5c5852;--line:#e4e0da;--accent:#b4231a;--code:#f0ede8}
@media (prefers-color-scheme:dark){:root{--bg:#121212;--fg:#ecebe8;--muted:#a8a39b;--line:#2c2b29;--accent:#ff6b5e;--code:#232220}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:46rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
header.site{display:flex;flex-wrap:wrap;gap:.5rem 1.25rem;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:1rem;margin-bottom:2rem}
header.site .brand{font-weight:700;letter-spacing:-.01em;color:var(--fg);text-decoration:none;margin-right:auto}
header.site nav a{color:var(--muted);text-decoration:none;font-size:.95rem}
header.site nav a[aria-current=page]{color:var(--accent);font-weight:600}
nav{display:flex;flex-wrap:wrap;gap:1rem}
h1{font-size:2rem;line-height:1.15;letter-spacing:-.02em;margin:.2rem 0 1rem;text-wrap:balance}
h2{font-size:1.25rem;margin:2.2rem 0 .6rem;text-wrap:balance}h3{font-size:1.05rem;margin:1.6rem 0 .4rem}
p,li{color:var(--fg)}ul{padding-left:1.2rem}li{margin:.35rem 0}
a{color:var(--accent)}a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
code{font:.9em ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--code);padding:.1em .3em;border-radius:3px}
.table{overflow-x:auto;margin:1rem 0}table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{border-bottom:1px solid var(--line);padding:.55rem .6rem;text-align:left;vertical-align:top}th{color:var(--muted);font-weight:600}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
"""
PAGES = [("", "Sixth String", None), ("privacy", "Privacy policy", "PRIVACY-POLICY-PUBLIC-APP.md"), ("terms", "Terms of use", "TERMS-OF-USE-PUBLIC-APP.md"),
         ("support", "Support", "support.md"), ("security", "Security", "SECURITY.md")]

def shell(slug, title, body):
    up = "../" if slug else ""
    nav = "".join(f'<a href="{up}{s}/"{" aria-current=page" if s == slug else ""}>{t}</a>' for s, t, _ in PAGES[1:])
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Sixth String</title><meta name="description" content="Sixth String guitar-practice app: {html.escape(title.lower())}.">
<style>{STYLE}</style></head>
<body><div class="wrap"><header class="site"><a class="brand" href="{up or './'}">Sixth String</a><nav aria-label="Pages">{nav}</nav></header>
<main>
{body}
</main>
<footer>Sixth String is published by Alasdair Maciver, Scotland, United Kingdom. Contact: maciverguitar@gmail.com</footer></div></body></html>
"""

def main():
    index_md = ("# Sixth String\n\nA guitar-practice trainer for Windows, macOS and iPhone that listens to your playing and grades drills in real time.\n\n"
                "- [Support](support/)\n- [Privacy policy](privacy/)\n- [Terms of service](terms/)\n- [Security](security/)\n")
    for slug, title, src in PAGES:
        if src is None: md = index_md
        elif src == "support.md": md = (ROOT / src).read_text()
        elif src == "SECURITY.md": md = security_page((COMP / src).read_text())
        else: md = clean_draft((COMP / src).read_text())
        d = ROOT / slug; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(shell(slug, title, md_to_html(md)))
    (ROOT / ".nojekyll").write_text("")
    print("built", [p[0] or "index" for p in PAGES])
main()
