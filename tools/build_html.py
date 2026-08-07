#!/usr/bin/env python3
"""
build_html.py — Render a Markdown guide into a responsive, mobile-friendly HTML page.

Usage:
    python3 tools/build_html.py <input.md> <output.html> [more_outputs.html ...]

Mobile features:
  - Sticky top app bar with hamburger menu
  - Slide-in nav drawer + backdrop, tap-to-close, body scroll lock
  - Horizontally scrollable tables and code blocks (no layout break)
  - Fluid typography, 44px min tap targets
  - Back-to-top button, reading progress bar, scroll-spy active nav
"""

import re
import sys
import subprocess
from datetime import datetime, timezone
import markdown

try:
    from zoneinfo import ZoneInfo
    CENTRAL = ZoneInfo('America/Chicago')   # auto-handles CST (winter) / CDT (summer)
except Exception:                            # pragma: no cover
    CENTRAL = None

STAMP_FMT = '%d %b %Y, %I:%M %p %Z'


def _to_central(dt):
    """Convert an aware datetime to US Central, falling back to UTC if tz data is missing."""
    if CENTRAL is None:
        return dt.astimezone(timezone.utc)
    return dt.astimezone(CENTRAL)


def build_stamp(src):
    """
    Build the 'last updated' / 'page built' stamps in US Central time.

    'last updated' prefers the source file's last git commit timestamp (when the
    CONTENT actually changed); falls back to build time if git data is missing.
    Timezone label is CST or CDT automatically, per the date.
    """
    built = _to_central(datetime.now(timezone.utc)).strftime(STAMP_FMT)

    content_date = None
    try:
        out = subprocess.run(
            ['git', 'log', '-1', '--format=%cI', '--', src],   # strict ISO-8601
            capture_output=True, text=True, timeout=10,
        )
        iso = out.stdout.strip()
        if out.returncode == 0 and iso:
            content_date = _to_central(datetime.fromisoformat(iso)).strftime(STAMP_FMT)
    except Exception:
        pass

    return content_date or built, built

CSS = r"""
:root{
  --primary:#1B2A4A; --accent:#2E86AB; --bg:#f8f9fa; --text:#333;
  --code-bg:#1e1e1e; --code-text:#d4d4d4; --border:#e0e0e0;
  --sidebar-w:290px; --topbar-h:56px;
}
*{box-sizing:border-box;margin:0;padding:0;}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  line-height:1.7;color:var(--text);background:var(--bg);
  overflow-wrap:break-word;word-wrap:break-word;
}
body.nav-open{overflow:hidden;}

/* ---------- Top app bar (mobile only) ---------- */
.topbar{
  display:none;position:fixed;top:0;left:0;right:0;height:var(--topbar-h);
  background:var(--primary);color:#fff;z-index:120;
  align-items:center;gap:12px;padding:0 12px;
  box-shadow:0 2px 8px rgba(0,0,0,.2);
}
.topbar__btn{
  background:transparent;border:0;color:#fff;cursor:pointer;
  min-width:44px;min-height:44px;font-size:24px;line-height:1;
  display:flex;align-items:center;justify-content:center;border-radius:8px;
}
.topbar__btn:active{background:rgba(255,255,255,.15);}
.topbar__title{font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

/* ---------- Sidebar / drawer ---------- */
.sidebar{
  width:var(--sidebar-w);position:fixed;top:0;left:0;height:100vh;
  background:var(--primary);color:#fff;overflow-y:auto;padding:20px 0;
  z-index:130;transition:transform .28s ease;
  -webkit-overflow-scrolling:touch;
}
.sidebar h2{
  padding:0 20px 12px;font-size:14px;text-transform:uppercase;letter-spacing:1px;
  opacity:.75;border-bottom:1px solid rgba(255,255,255,.12);margin-bottom:8px;
}
.sidebar a{
  display:block;padding:9px 20px;color:rgba(255,255,255,.85);text-decoration:none;
  font-size:13px;border-left:3px solid transparent;transition:background .2s;
}
.sidebar a:hover,.sidebar a.active{background:rgba(255,255,255,.12);color:#fff;border-left-color:var(--accent);}
.sidebar .nav-section{
  font-weight:700;font-size:10.5px;margin-top:14px;padding:5px 20px;
  opacity:.6;text-transform:uppercase;letter-spacing:.5px;color:#7fb8d9;
}
.sidebar__close{display:none;}

/* ---------- Backdrop ---------- */
.backdrop{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);
  z-index:125;opacity:0;transition:opacity .28s ease;
}
.backdrop.show{opacity:1;}

/* ---------- Content ---------- */
.content{margin-left:var(--sidebar-w);max-width:900px;padding:40px 60px;min-height:100vh;}
h1{color:var(--primary);font-size:clamp(1.6rem,4.5vw,2.1rem);margin:36px 0 18px;padding-bottom:10px;border-bottom:3px solid var(--accent);line-height:1.25;}
h2{color:var(--primary);font-size:clamp(1.25rem,3.6vw,1.55rem);margin:32px 0 14px;padding-top:18px;border-top:1px solid var(--border);line-height:1.3;scroll-margin-top:70px;}
h3{color:var(--accent);font-size:clamp(1.08rem,3vw,1.22rem);margin:24px 0 10px;line-height:1.35;scroll-margin-top:70px;}
h4{color:#555;font-size:1.03rem;margin:18px 0 8px;}
p{margin:12px 0;}
ul,ol{margin:10px 0 10px 22px;}
li{margin:6px 0;}
strong{color:var(--primary);}
a{color:var(--accent);}
hr{border:none;border-top:2px solid var(--border);margin:28px 0;}

/* ---------- Code blocks: scroll, never break layout ---------- */
pre,pre.codehilite{
  background:var(--code-bg);color:var(--code-text);padding:16px;border-radius:8px;
  overflow-x:auto;-webkit-overflow-scrolling:touch;margin:15px 0;
  font-size:12.5px;line-height:1.5;border:1px solid #333;
  max-width:100%;
}
pre code{background:none;padding:0;color:inherit;white-space:pre;}
code{background:#e9ecef;padding:2px 6px;border-radius:3px;font-size:.9em;color:#c7254e;}

/* ---------- Tables: wrapped in a scroll container ---------- */
.table-wrap{
  overflow-x:auto;-webkit-overflow-scrolling:touch;margin:15px 0;
  border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.1);
}
table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:480px;}
th{background:var(--primary);color:#fff;padding:11px 14px;text-align:left;font-weight:600;white-space:nowrap;}
td{padding:9px 14px;border-bottom:1px solid var(--border);vertical-align:top;}
tr:nth-child(even){background:#f8f9fa;}
tr:hover{background:#e8f4f8;}

blockquote{
  background:linear-gradient(135deg,#e8f4f8,#f0f8ff);border-left:4px solid var(--accent);
  padding:14px 18px;margin:15px 0;border-radius:0 8px 8px 0;font-style:italic;
}
blockquote p{margin:5px 0;}
img{max-width:100%;height:auto;}

/* ---------- Last-updated stamp ---------- */
.updated{
  display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;
  background:#eef6fa;border:1px solid #cfe5ef;border-left:4px solid var(--accent);
  border-radius:0 8px 8px 0;padding:10px 14px;margin:0 0 24px;
  font-size:13px;color:#31576b;
}
.updated__label{font-weight:700;color:var(--primary);}
.updated__sep{opacity:.4;}
.updated a{color:var(--accent);}

/* ---------- Progress bar ---------- */
.progress-bar{position:fixed;top:0;left:var(--sidebar-w);right:0;height:3px;background:var(--border);z-index:110;}
.progress-bar .fill{height:100%;background:var(--accent);width:0%;}

/* ---------- Back to top ---------- */
.to-top{
  position:fixed;bottom:20px;right:20px;width:48px;height:48px;border-radius:50%;
  background:var(--accent);color:#fff;border:0;font-size:22px;cursor:pointer;
  display:none;align-items:center;justify-content:center;z-index:115;
  box-shadow:0 3px 10px rgba(0,0,0,.3);
}
.to-top.show{display:flex;}

/* ================= MOBILE / TABLET ================= */
@media (max-width:900px){
  .topbar{display:flex;}
  .sidebar{transform:translateX(-100%);width:min(86vw,320px);box-shadow:2px 0 16px rgba(0,0,0,.3);}
  .sidebar.open{transform:translateX(0);}
  .sidebar__close{
    display:flex;position:absolute;top:10px;right:10px;
    min-width:44px;min-height:44px;align-items:center;justify-content:center;
    background:transparent;border:0;color:#fff;font-size:26px;cursor:pointer;border-radius:8px;
  }
  .sidebar h2{padding-right:60px;}
  .sidebar a{padding:12px 20px;font-size:14px;}   /* bigger tap targets */
  .sidebar .nav-section{font-size:11px;}
  .backdrop{display:block;pointer-events:none;}
  .backdrop.show{pointer-events:auto;}
  .content{margin-left:0;padding:calc(var(--topbar-h) + 16px) 16px 60px;}
  .progress-bar{left:0;top:var(--topbar-h);}
  h2{scroll-margin-top:calc(var(--topbar-h) + 10px);}
  h3{scroll-margin-top:calc(var(--topbar-h) + 10px);}
  pre,pre.codehilite{font-size:11.5px;padding:12px;}
  table{font-size:12.5px;min-width:420px;}
  th,td{padding:8px 10px;}
  blockquote{padding:12px 14px;}
}
@media (max-width:420px){
  .content{padding:calc(var(--topbar-h) + 12px) 12px 60px;}
  pre,pre.codehilite{font-size:10.5px;}
  .to-top{bottom:14px;right:14px;width:44px;height:44px;}
}
@media print{
  .sidebar,.topbar,.backdrop,.progress-bar,.to-top{display:none!important;}
  .content{margin:0;padding:0;max-width:100%;}
}
"""

JS = r"""
(function(){
  var sidebar  = document.querySelector('.sidebar');
  var backdrop = document.querySelector('.backdrop');
  var toTop    = document.querySelector('.to-top');
  var fill     = document.querySelector('.progress-bar .fill');

  function openNav(){
    sidebar.classList.add('open');
    backdrop.classList.add('show');
    document.body.classList.add('nav-open');
    sidebar.setAttribute('aria-hidden','false');
  }
  function closeNav(){
    sidebar.classList.remove('open');
    backdrop.classList.remove('show');
    document.body.classList.remove('nav-open');
    sidebar.setAttribute('aria-hidden','true');
  }
  function toggleNav(){
    sidebar.classList.contains('open') ? closeNav() : openNav();
  }

  var t1=document.querySelector('.topbar__btn');
  var t2=document.querySelector('.sidebar__close');
  if(t1) t1.addEventListener('click', toggleNav);
  if(t2) t2.addEventListener('click', closeNav);
  if(backdrop) backdrop.addEventListener('click', closeNav);
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeNav(); });

  /* Auto-assign heading IDs from text so nav anchors always resolve */
  function slug(s){
    return s.toLowerCase().replace(/[^a-z0-9\s-]/g,'').trim().replace(/\s+/g,'-').slice(0,60);
  }
  document.querySelectorAll('.content h1,.content h2,.content h3').forEach(function(h){
    if(!h.id) h.id = slug(h.textContent);
  });

  /* Nav links: smooth scroll + close drawer on mobile */
  document.querySelectorAll('.sidebar a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(e){
      var target=document.querySelector(a.getAttribute('href'));
      if(target){ e.preventDefault(); target.scrollIntoView({behavior:'smooth',block:'start'}); }
      if(window.innerWidth<=900) closeNav();
    });
  });

  /* Reading progress + back-to-top */
  window.addEventListener('scroll', function(){
    var st=document.documentElement.scrollTop;
    var h=document.documentElement.scrollHeight-document.documentElement.clientHeight;
    if(fill) fill.style.width=(h>0? (st/h*100):0)+'%';
    if(toTop) toTop.classList.toggle('show', st>400);
  }, {passive:true});
  if(toTop) toTop.addEventListener('click', function(){
    window.scrollTo({top:0,behavior:'smooth'});
  });

  /* Scroll-spy: highlight the current section in the nav */
  var obs=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){
        document.querySelectorAll('.sidebar a').forEach(function(a){a.classList.remove('active');});
        var l=document.querySelector('.sidebar a[href="#'+en.target.id+'"]');
        if(l) l.classList.add('active');
      }
    });
  },{threshold:0.25,rootMargin:'-70px 0px -60% 0px'});
  document.querySelectorAll('.content h1[id],.content h2[id],.content h3[id]').forEach(function(el){obs.observe(el);});
})();
"""


def build_nav(html_body):
    """
    Auto-generate the nav from the document's h2 headings.
    Reads the `id` attribute that the markdown 'toc' extension already assigned —
    this is the source of truth, so anchors can never drift out of sync.
    """
    import html as _html

    def label_of(raw):
        # Drop noisy parentheticals like "(→ Amazon Connect + Bedrock Agents)"
        lbl = re.sub(r'\s*\((?:→|->).*?\)\s*', '', raw)
        lbl = re.sub(r'\s*[—–-]\s*Hiring Manager.*$', ' — HM Interview', lbl)
        lbl = lbl.replace('Cheat Sheet: Key Terms to Use Fluently', 'Cheat Sheet')
        lbl = lbl.replace('Quick Reference: End-to-End Architecture', 'Reference Architecture')
        lbl = re.sub(r'\s+Preparation$', '', lbl)
        lbl = re.sub(r'\s+', ' ', lbl).strip()
        if lbl.isupper():
            lbl = lbl.title()
        return lbl if len(lbl) <= 38 else lbl[:36].rstrip() + '…'

    items = []
    # Only match headings that already carry an id (toc extension adds them)
    for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', html_body, re.DOTALL):
        hid = m.group(1)
        raw = _html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
        if raw:
            items.append((hid, label_of(raw)))

    links = ['<a href="#top">&#127968; Top</a>']
    for hid, label in items:
        links.append(f'<a href="#{hid}">{label}</a>')
    return "\n    ".join(links)


def wrap_tables(html):
    """Wrap every table in a horizontally scrollable container."""
    return re.sub(r'(<table>.*?</table>)', r'<div class="table-wrap">\1</div>',
                  html, flags=re.DOTALL)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, outs = sys.argv[1], sys.argv[2:]

    md_text = open(src).read()
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br'])
    body = md.convert(md_text)
    body = wrap_tables(body)

    content_date, built = build_stamp(src)
    title_m = re.search(r'^#\s+(.+)$', md_text, re.M)
    title = re.sub(r'[#*`]', '', title_m.group(1)).strip() if title_m else "Guide"
    nav_links = build_nav(body)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#1B2A4A">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>

<header class="topbar">
  <button class="topbar__btn" aria-label="Open navigation menu" aria-controls="sidebar">&#9776;</button>
  <span class="topbar__title">{title}</span>
</header>

<div class="backdrop" aria-hidden="true"></div>

<nav class="sidebar" id="sidebar" aria-label="Table of contents" aria-hidden="true">
  <button class="sidebar__close" aria-label="Close navigation menu">&times;</button>
  <h2>Contents</h2>
    {nav_links}
</nav>

<div class="progress-bar"><div class="fill"></div></div>

<main class="content" id="top">
<div class="updated">
  <span><span class="updated__label">Last updated:</span> {content_date}</span>
  <span class="updated__sep">·</span>
  <span>Page built: {built}</span>
  <span class="updated__sep">·</span>
  <span><a href="https://github.com/naramsettisiva/genAIPrepration/commits/main">View change history</a></span>
</div>
{body}
</main>

<button class="to-top" aria-label="Back to top">&#8679;</button>

<script>{JS}</script>
</body>
</html>"""

    for out in outs:
        with open(out, 'w') as f:
            f.write(html)
        print(f"  wrote {out}  ({len(html)/1024:.1f} KB)")
    print(f"Nav sections: {nav_links.count('<a href')}")


if __name__ == "__main__":
    main()
