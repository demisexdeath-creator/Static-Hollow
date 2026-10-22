#!/usr/bin/env python3
"""Builds the official Static Hollow website.

Wraps each page fragment in src/ with the shared template (top bar, sidebar, title card,
contents rail), then writes the search index (assets/js/search-index.js) and the embedded
fonts (assets/css/fonts.css).

Usage, from the site's folder:   python3 _build/build.py            (the public site)
                                 python3 _build/build.py --drafts   (with the TODO notes showing)
It writes the pages into the folder above _build/ (the site itself). CSS, JS and images
live in the site's assets/ folder and are edited there directly; this script never
touches them. Needs Python 3.8+, nothing else.

The public site hides every TODO note (the amber boxes) and lists them in _build/TODO.md
instead, so you can see what's left to confirm. --drafts shows them on the pages and adds a
todo.html page that lists them all.
"""
import html
import json
import os
import re
import shutil
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
STATIC = os.path.join(HERE, "static")
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
DRAFTS = "--drafts" in sys.argv[1:]
OUT = os.path.abspath(ARGS[0]) if ARGS else os.path.dirname(HERE)

SITE = "Static Hollow"
# Where the site lives on its host. GitHub Pages serves it at demisexdeath-creator.github.io/Static-Hollow/,
# and 404.html needs that to find its styles from any depth. With a custom domain, set this to "/".
BASE_PATH = "/Static-Hollow/"
HOME_TITLE = "Static Hollow | Official Website"
VERSION = "1.63.3"

CHAPTERS = {
    1: ("story/chapter-1.html", "The Nine"),
    2: ("story/chapter-2.html", "The Breach"),
    3: ("story/chapter-3.html", "The Glasshouse"),
    4: ("story/chapter-4.html", "The Flesh"),
    5: ("story/chapter-5.html", "The Static"),
    6: ("story/chapter-6.html", "The Door at the End of the World"),
    7: ("story/chapter-7.html", "The First Signal"),
    8: ("story/chapter-8.html", "The Dead Water"),
}

# (path, label, chapter-number-or-None)
NAV = [
    ("Archive", [
        ("index.html", "Home", None),
        ("install.html", "Installation guide", None),
        ("faq.html", "FAQ", None),
    ]),
    ("Story", [("story/index.html", "Story overview", None)]
     + [(p, name, n) for n, (p, name) in CHAPTERS.items()]),
    ("Entities & bosses", [
        ("entities/index.html", "Bestiary (everything)", None),
        ("entities/the-watcher.html", "The Watcher", 1),
        ("entities/hollow-saint.html", "The Hollow Saint", 1),
        ("entities/the-mended.html", "The Mended", 2),
        ("entities/the-gardener.html", "The Gardener", 3),
        ("entities/the-bloom.html", "The Bloom", 3),
        ("entities/giant-tentacles.html", "The giant tentacles", 3),
        ("entities/gardener-reborn.html", "The Gardener, Reborn (Again)", 4),
        ("entities/warden-of-shelter-no-4.html", "The Warden of Shelter No. 4", 4),
        ("entities/the-parasite.html", "The Parasite", 4),
        ("entities/the-omni.html", "The Omni", 4),
        ("entities/the-amalgam.html", "The Amalgam", 5),
        ("entities/the-carrier.html", "The Carrier", 5),
        ("entities/the-turned.html", "The turned (the outbreak)", 5),
        ("entities/the-chorus.html", "The Chorus", 5),
        ("entities/the-deaf-king.html", "The Deaf King", 5),
        ("entities/the-crowd.html", "The Crowd", 6),
        ("entities/the-projectionist.html", "The Projectionist", 6),
        ("entities/the-viewer.html", "The Viewer", 6),
        ("entities/the-first-signal.html", "The First Signal", 7),
        ("entities/the-undertow.html", "The Undertow", 8),
    ]),
    ("Locations & structures", [
        ("places/index.html", "Every location", None),
        ("places/cathedral.html", "The church that isn't on any map", 1),
        ("places/the-bloom-realm.html", "The teeth pit and floating islands", 3),
        ("places/the-flesh.html", "The red fog", 4),
        ("places/relay-6.html", "The relay and the live banks", 5),
        ("places/starlite-drive-in.html", "The Starlite Drive-In", 5),
        ("places/null-static-zone.html", "The Null Static Zone", 5),
        ("places/the-hive.html", "The Hive", 5),
        ("places/the-deep.html", "The Sinkhole and the Deep", 5),
        ("places/the-stalls.html", "The Door and the Stalls", 6),
        ("places/the-watchers-vault.html", "The Watcher's Vault", 6),
        ("places/the-other-side.html", "The Other Side", 6),
        ("places/the-hub.html", "The Hub", 7),
        ("places/the-dead-water.html", "The Dead Water", 8),
        ("places/the-hollows-country.html", "The Hollow's own country", None),
    ]),
    ("Items & blocks", [
        ("items/index.html", "Every item and block", None),
        ("items/chapter-gear.html", "Gear for every chapter", None),
        ("items/index.html#relay-core", "Relay Core", None),
        ("items/index.html#compasses", "Compasses and needles", None),
        ("items/index.html#power-source", "Power source parts", None),
        ("items/index.html#parasite-egg", "Parasite egg (pod)", None),
    ]),
    ("Lore", [
        ("lore/index.html", "Notes and books", None),
        ("lore/tapes-and-broadcasts.html", "Tapes and broadcasts", None),
        ("lore/the-watcher-speaks.html", "The Watcher speaks", None),
    ]),
    ("Records", [
        ("advancements.html", "Advancements", None),
        ("music.html", "The soundtrack", None),
        ("survival.html", "Cold, thirst and the world", None),
        ("credits.html", "Credits", None),
        ("todo.html", "Unverified entries (TODO)", None),
    ]),
]

SECTION_NAMES = {
    "story": ("story/index.html", "Story"),
    "entities": ("entities/index.html", "Entities"),
    "places": ("places/index.html", "Locations"),
    "items": ("items/index.html", "Items"),
    "lore": ("lore/index.html", "Lore"),
}


def slug(text):
    t = html.unescape(re.sub(r"<[^>]+>", "", text)).lower()
    t = t.replace("'", "").replace("’", "")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "section"


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def read_page(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--(.*?)-->\s*", raw, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    return meta, raw


class TodoFinder(HTMLParser):
    """Collects the text of every .todo / .todo-inline element and the heading it sits under."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.depth = 0
        self.buf = []
        self.heading = ("", "")
        self.in_h = None
        self.hbuf = []
        self.hid = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if self.depth:
            self.depth += 1
            return
        if "todo" in cls or "todo-inline" in cls:
            self.depth = 1
            self.buf = []
            return
        if tag in ("h2", "h3") and not self.depth:
            self.in_h = tag
            self.hbuf = []
            self.hid = a.get("id", "")

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if self.depth == 0:
                text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
                text = re.sub(r"^TODO:?\s*", "", text)
                self.items.append((self.heading, text))
            return
        if self.in_h and tag == self.in_h:
            self.heading = (self.hid, re.sub(r"\s+", " ", "".join(self.hbuf)).strip())
            self.in_h = None

    def handle_data(self, data):
        if self.depth:
            self.buf.append(data)
        elif self.in_h:
            self.hbuf.append(data)


def add_heading_ids(body):
    used = set(re.findall(r'id="([^"]+)"', body))

    def fix(m):
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "id=" in attrs:
            return m.group(0)
        base = slug(inner)
        i, sid = 2, base
        while sid in used:
            sid = f"{base}-{i}"
            i += 1
        used.add(sid)
        return f'<{tag}{attrs} id="{sid}">{inner}</{tag}>'

    return re.sub(r"<(h[23])([^>]*)>(.*?)</\1>", fix, body, flags=re.S)


def sections_for_search(body, page_path, page_title):
    """Split the article at h2/h3 so search results can jump straight to a section."""
    parts = re.split(r'(<h[23][^>]*id="[^"]+"[^>]*>.*?</h[23]>)', body, flags=re.S)
    out = []
    cur_h, cur_id, cur_txt = "", "", []
    for part in parts:
        hm = re.match(r'<h[23][^>]*id="([^"]+)"[^>]*>(.*?)</h[23]>', part, re.S)
        if hm:
            if cur_txt or cur_h:
                out.append((cur_h, cur_id, " ".join(cur_txt)))
            cur_id, cur_h, cur_txt = hm.group(1), strip_tags(hm.group(2)), []
        else:
            t = strip_tags(part)
            if t:
                cur_txt.append(t)
    if cur_txt or cur_h:
        out.append((cur_h, cur_id, " ".join(cur_txt)))
    entries = []
    for h, sid, txt in out:
        entries.append({
            "p": page_title,
            "h": h,
            "u": page_path + (f"#{sid}" if sid else ""),
            "t": txt[:2400],
        })
    return entries


def strip_todos(body):
    """The public site doesn't show the TODO notes."""
    body = re.sub(r'\s*<div class="todo">.*?</div>', "", body, flags=re.S)
    body = re.sub(r'\s*<figcaption class="todo-inline">.*?</figcaption>', "", body, flags=re.S)
    body = re.sub(r'\s*<span class="todo-inline[^"]*">.*?</span>', "", body, flags=re.S)
    return body


def rel_root(path):
    depth = path.count("/")
    return "../" * depth


def chapter_class(meta):
    ch = meta.get("chapter", "")
    return f"ch{ch}" if ch.isdigit() else ""


def render_nav(current):
    out = ['<nav id="sidebar" class="sidebar" aria-label="Wiki sections"><div class="sidebar__inner">']
    for group, links in NAV:
        links = [l for l in links if DRAFTS or l[0] != "todo.html"]
        out.append(f'<div class="nav-group"><p class="nav-group__title">{html.escape(group)}</p><ul>')
        for path, label, ch in links:
            cur = ' aria-current="page"' if path == current else ""
            mark = f'<span class="chip-num">{ch}</span>' if (group == "Story" and ch) else ""
            dot = f'<span class="nav-dot" aria-hidden="true"></span>' if (ch and group != "Story") else ""
            cls = f' class="ch{ch}"' if ch else ""
            out.append(f'<li{cls}><a href="{{root}}{path}"{cur}>{mark}{dot}<span>{html.escape(label)}</span></a></li>')
        out.append("</ul></div>")
    out.append('<p class="sidebar__ver">Written for Static Hollow ' + VERSION + '</p>')
    out.append("</div></nav>")
    return "\n".join(out)


def render_crumbs(path, meta):
    if path == "index.html":
        return ""
    items = ['<a href="{root}index.html">Home</a>']
    sec = meta.get("section", "")
    if sec in SECTION_NAMES and SECTION_NAMES[sec][0] != path:
        p, n = SECTION_NAMES[sec]
        items.append(f'<a href="{{root}}{p}">{n}</a>')
    items.append(f'<span aria-current="page">{html.escape(meta.get("nav", meta.get("title", "")))}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span class="crumbs__sep" aria-hidden="true">/</span>'.join(items) + "</nav>"


def render_titlecard(meta):
    file_line = meta.get("file", "")
    sub = meta.get("sub", "")
    t = meta.get("title", "")
    parts = ['<header class="titlecard">']
    if file_line:
        parts.append(f'<p class="titlecard__file">{file_line}</p>')
    parts.append(f'<h1 data-text="{html.escape(t)}">{t}</h1>')
    if sub:
        parts.append(f'<p class="titlecard__sub">{sub}</p>')
    parts.append("</header>")
    return "\n".join(parts)


def render_toc(body):
    hs = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', body, re.S)
    if len(hs) < 3:
        return "", ""
    lis = "".join(f'<li><a href="#{i}">{html.escape(strip_tags(t))}</a></li>' for i, t in hs)
    rail = f'<aside class="toc" aria-label="On this page"><p class="toc__title">On this page</p><ol>{lis}</ol></aside>'
    mobile = f'<details class="toc-m"><summary>On this page</summary><ol>{lis}</ol></details>'
    return rail, mobile


def render_prevnext(meta):
    ch = meta.get("chapter", "")
    if meta.get("section") != "story" or not ch.isdigit():
        return ""
    n = int(ch)
    cells = []
    if n - 1 in CHAPTERS:
        p, name = CHAPTERS[n - 1]
        cells.append(f'<a class="pn pn--prev ch{n-1}" href="{{root}}{p}"><span class="pn__dir">Previous chapter</span><span class="pn__name">{name}</span></a>')
    else:
        cells.append('<a class="pn pn--prev" href="{root}story/index.html"><span class="pn__dir">Back to</span><span class="pn__name">Story overview</span></a>')
    if n + 1 in CHAPTERS:
        p, name = CHAPTERS[n + 1]
        cells.append(f'<a class="pn pn--next ch{n+1}" href="{{root}}{p}"><span class="pn__dir">Next chapter</span><span class="pn__name">{name}</span></a>')
    else:
        cells.append('<a class="pn pn--next" href="{root}entities/index.html"><span class="pn__dir">Then read</span><span class="pn__name">The bestiary</span></a>')
    return '<nav class="prevnext" aria-label="Chapters">' + "".join(cells) + "</nav>"


TEMPLATE = """<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doc_title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0e0a12">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Static Hollow">
<meta property="og:title" content="{doc_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{root}assets/img/scene.jpg">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/css/fonts.css">
<link rel="stylesheet" href="{root}assets/css/style.css">
<script src="{root}assets/js/search-index.js" defer></script>
<script src="{root}assets/js/site.js" defer></script>
</head>
<body class="{body_class}">
<a class="skip" href="#content">Skip to the article</a>
<div class="grain" aria-hidden="true"></div>
<header class="topbar">
  <button class="navtoggle" type="button" aria-controls="sidebar" aria-expanded="false">
    <span class="navtoggle__bars" aria-hidden="true"></span><span class="vh">Menu</span>
  </button>
  <a class="brand" href="{root}index.html">
    <span class="brand__eyes" aria-hidden="true"><i></i><i></i></span>
    <span class="brand__name">Static Hollow</span>
    <span class="brand__sub">official wiki</span>
  </a>
  <div class="search" role="search">
    <label class="vh" for="q">Search the wiki</label>
    <input id="q" class="search__input" type="search" placeholder="Search creatures, places, items" autocomplete="off" spellcheck="false"
      role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="results">
    <kbd class="search__key" aria-hidden="true">/</kbd>
    <ul id="results" class="results" role="listbox" aria-label="Search results" hidden></ul>
  </div>
</header>
<div class="layout">
{nav}
<div class="scrim" hidden></div>
<main id="content" class="main" tabindex="-1">
{crumbs}
{titlecard}
{toc_mobile}
<div class="article-wrap{wrap_class}">
<article class="article">
{body}
</article>
{toc}
</div>
{prevnext}
<footer class="sitefoot">
  <p>The official website of <strong>Static Hollow</strong>, a creepypasta horror mod for Minecraft by Death. Written for version {version}, Minecraft 26.3.</p>
  <p>Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.</p>{drafts_note}
</footer>
</main>
</div>
</body>
</html>
"""


FONTS = [
    ("Big Shoulders Display", "big-shoulders-display-latin-700-normal.woff2", 700, "normal"),
    ("Big Shoulders Display", "big-shoulders-display-latin-900-normal.woff2", 900, "normal"),
    ("Spectral", "spectral-latin-400-normal.woff2", 400, "normal"),
    ("Spectral", "spectral-latin-400-italic.woff2", 400, "italic"),
    ("Spectral", "spectral-latin-600-normal.woff2", 600, "normal"),
    ("Courier Prime", "courier-prime-latin-400-normal.woff2", 400, "normal"),
    ("Courier Prime", "courier-prime-latin-700-normal.woff2", 700, "normal"),
]


def write_fonts_css():
    """Fonts are embedded in fonts.css so the site also looks right when opened straight
    from a folder (browsers block font files loaded over file://). The .woff2 files are
    kept beside it with their licences."""
    import base64
    rules = ["/* Self-hosted fonts, all under the SIL Open Font License (see ../fonts/LICENSE-*.txt). */"]
    for fam, f, w, st in FONTS:
        data = base64.b64encode(open(os.path.join(OUT, "assets/fonts", f), "rb").read()).decode()
        rules.append(f'@font-face{{font-family:"{fam}";src:url(data:font/woff2;base64,{data}) format("woff2");font-weight:{w};font-style:{st};font-display:swap}}')
    open(os.path.join(OUT, "assets/css/fonts.css"), "w").write("\n".join(rules) + "\n")


def build():
    if os.path.isdir(STATIC):  # (only in the original workspace; the site's own assets/ is the source after that)
        shutil.copytree(STATIC, OUT, dirs_exist_ok=True)
    write_fonts_css()

    pages = []
    for dirpath, _, files in os.walk(SRC):
        for f in sorted(files):
            if f.endswith(".html"):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, SRC).replace(os.sep, "/")
                pages.append(rel)
    pages.sort()

    rendered = {}
    index = []
    todos = []

    def render(path, meta, body):
        body = add_heading_ids(body)
        full = body
        if not DRAFTS:
            body = strip_todos(body)
        toc, toc_m = ("", "") if meta.get("toc") == "no" else render_toc(body)
        title_txt = strip_tags(meta.get("nav") or meta.get("title", ""))
        doc_title = HOME_TITLE if path == "index.html" else f"{title_txt} | {SITE}"
        layout = meta.get("layout", "")
        body_class = " ".join(c for c in [f"sec-{meta.get('section','misc')}", chapter_class(meta), f"layout-{layout}" if layout else ""] if c)
        out = TEMPLATE.format(
            root="{root}",
            doc_title=html.escape(doc_title),
            desc=html.escape(meta.get("desc", "")),
            body_class=body_class,
            nav=render_nav(path),
            crumbs=render_crumbs(path, meta),
            titlecard="" if layout == "home" else render_titlecard(meta),
            toc_mobile=toc_m,
            wrap_class=" has-toc" if toc else "",
            body=body,
            toc=toc,
            prevnext=render_prevnext(meta),
            version=VERSION,
            drafts_note=('\n  <p>Draft build: anything marked <span class="todo-inline todo-inline--key">TODO</span> hasn\'t been confirmed yet. '
                         '<a href="{root}todo.html">See the full list</a>.</p>') if DRAFTS else "",
        )
        out = out.replace("{root}", rel_root(path))
        return full, body, out

    for path in pages:
        meta, body = read_page(os.path.join(SRC, path))
        full, body, out = render(path, meta, body)
        rendered[path] = out
        title_txt = strip_tags(meta.get("nav") or meta.get("title", ""))
        if not meta.get("noindex"):
            index.extend(sections_for_search(body, path, title_txt))
        tf = TodoFinder()
        tf.feed(full)
        for (hid, htext), text in tf.items:
            todos.append((path, title_txt, hid, htext, text))

    # The TODO page, generated from every page's markers.
    by_page = {}
    for path, title, hid, htext, text in todos:
        by_page.setdefault((path, title), []).append((hid, htext, text))
    order = [p for p in pages if any(k[0] == p for k in by_page)]
    rows = [
        "<p>Everything on this list is marked on its page with an amber <span class=\"todo-inline todo-inline--key\">TODO</span> box. "
        "Each one is something the mod files and the README didn't settle, so it was left for you to fill in rather than guessed. "
        "To fix one, open the page's HTML file, search for <code>TODO</code>, replace the box with the real text, and the entry drops off this list the next time the site is built "
        "(or delete the line here by hand if you edit the HTML directly).</p>",
        f"<p><strong>{len(todos)}</strong> open items across <strong>{len(order)}</strong> pages.</p>",
    ]
    for p in order:
        title = next(k[1] for k in by_page if k[0] == p)
        rows.append(f'<h2>{html.escape(title)}</h2><ul class="todolist">')
        for hid, htext, text in by_page[(p, title)]:
            href = "{root}" + p + (f"#{hid}" if hid else "")
            where = html.escape(htext) if htext else "Top of page"
            rows.append(f'<li><a href="{href}">{where}</a><span>{html.escape(text)}</span></li>')
        rows.append("</ul>")
    if DRAFTS:
        todo_meta = {"title": "UNVERIFIED", "nav": "Unverified entries", "sub": "what the files didn't say", "section": "misc",
                     "desc": "Every open TODO on the Static Hollow wiki, in one list.", "toc": "no", "noindex": "1"}
        _, _, out = render("todo.html", todo_meta, "\n".join(rows))
        rendered["todo.html"] = out
    else:
        stale = os.path.join(OUT, "todo.html")
        if os.path.exists(stale):
            os.remove(stale)
    # The author's private list, kept beside the build script (folders starting with _ aren't published on GitHub Pages).
    md = ["# Static Hollow website: open TODOs", "",
          f"{len(todos)} notes across {len(order)} pages. They're hidden on the public site. Build with `--drafts` to see them on the pages.",
          "To close one, open the page's source in `src/`, search for `TODO`, replace the box with the real text, and build again.", ""]
    for p in order:
        title = next(k[1] for k in by_page if k[0] == p)
        md.append(f"## {title} (`src/{p}`)")
        for hid, htext, text in by_page[(p, title)]:
            md.append(f"- **{htext or 'Top of page'}**: {text}")
        md.append("")
    open(os.path.join(HERE, "TODO.md"), "w", encoding="utf-8").write("\n".join(md))

    if BASE_PATH and "404.html" in rendered:
        rendered["404.html"] = rendered["404.html"].replace("<head>", f'<head>\n<base href="{BASE_PATH}">', 1)
    for path, out in rendered.items():
        dest = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(out)

    js = "window.SH_INDEX=" + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(OUT, "assets/js/search-index.js"), "w", encoding="utf-8").write(js)
    mode = "drafts, TODOs showing" if DRAFTS else "public, TODOs hidden and listed in TODO.md"
    print(f"built {len(rendered)} pages ({mode}), {len(index)} search sections, {len(todos)} TODOs -> {OUT}")


if __name__ == "__main__":
    build()
