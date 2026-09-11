#!/usr/bin/env python3
"""Générateur du portfolio — Python 3, bibliothèque standard uniquement.

    python build.py

Lit locales/fr.json et locales/en.json, écrit :
    index.html      version française (racine du site)
    en/index.html   version anglaise
    sitemap.xml, robots.txt, .nojekyll

Les deux langues sont de vraies pages distinctes : chacune est indexable,
lisible sans JavaScript, et liée à l'autre par <link rel="alternate" hreflang>.
"""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape as _escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Données qui ne se traduisent pas : liens, identités, chemins.
# ---------------------------------------------------------------------------
SITE = {
    "baseUrl": "https://lenu-san.github.io",
    "author": "Lénusan Gunarajah",
    "fullName": "Lénusan Josap Gunarajah",
    "email": "lenuss@live.fr",
    "linkedin": "https://www.linkedin.com/in/l%C3%A9nusan-g-0470b6336",
    "github": "https://github.com/Lenu-san",
    "credly": "https://www.credly.com/users/lenusan-josap-gunarajah/badges",
    "sourceRepo": "https://github.com/Lenu-san/Lenu-san.github.io",
    "locality": "Aulnay-sous-Bois",
    "country": "FR",
    "themeColorLight": "#f5f7fa",
    "themeColorDark": "#0b1220",
    # Déposez le fichier à cet emplacement pour faire apparaître le bouton « CV ».
    "cvPath": "assets/cv.pdf",
}

PAGES = [
    {"locale": "fr", "out": "index.html", "url": "/", "prefix": "", "ogImage": "assets/og.png"},
    {"locale": "en", "out": "en/index.html", "url": "/en/", "prefix": "../", "ogImage": "assets/og-en.png"},
]

HAS_CV = (ROOT / SITE["cvPath"]).exists()


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
def esc(value) -> str:
    return _escape(str(value), quote=True)


def inline_code(value) -> str:
    """Rend `code` en <code> dans un texte, après échappement du reste."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(value))


ICONS = {
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "route": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H15a3 3 0 0 1 0 6H9a3 3 0 0 0 0 6h6.5"/>',
    "car": '<path d="M4 16v-3.2L6 7h12l2 5.8V16"/><path d="M4 16h16v2.5h-3V16H7v2.5H4Z"/><circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3.5v3M16 3.5v3"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "github": '<path d="M12 2.6a9.4 9.4 0 0 0-3 18.3c.5.1.6-.2.6-.5v-1.7c-2.6.6-3.2-1.2-3.2-1.2-.4-1.1-1-1.4-1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .8 1.5 2.2 1 2.8.8.1-.6.4-1 .6-1.3-2.1-.2-4.3-1-4.3-4.6 0-1 .4-1.9 1-2.5-.1-.3-.4-1.3.1-2.6 0 0 .8-.3 2.6 1a9 9 0 0 1 4.7 0c1.8-1.3 2.6-1 2.6-1 .5 1.3.2 2.3.1 2.6.6.6 1 1.5 1 2.5 0 3.6-2.2 4.4-4.3 4.6.4.3.7.9.7 1.8v2.6c0 .3.1.6.6.5A9.4 9.4 0 0 0 12 2.6Z"/>',
    "linkedin": '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 10.5V17M8 7.6v.1M12 17v-3.6a2 2 0 0 1 4 0V17"/>',
    "badge": '<circle cx="12" cy="9.5" r="5.5"/><path d="m8.5 14.5-1 6 4.5-2.3 4.5 2.3-1-6"/>',
    "external": '<path d="M14 4h6v6M20 4l-8.5 8.5"/><path d="M18 14v4.5A1.5 1.5 0 0 1 16.5 20h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10"/>',
    "repo": '<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5Z"/><path d="M5 19.5V4.5M8.5 21H19v-3"/>',
    "download": '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5"/><path d="M4.5 17.5v1A1.5 1.5 0 0 0 6 20h12a1.5 1.5 0 0 0 1.5-1.5v-1"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>',
    "shield": '<path d="M12 3.5 19 6.5v5.2c0 4.4-2.9 7.7-7 9.3-4.1-1.6-7-4.9-7-9.3V6.5Z"/><path d="m9 12 2 2 4-4"/>',
    "layers": '<path d="m12 4 8 4-8 4-8-4Z"/><path d="m4 12 8 4 8-4M4 16l8 4 8-4"/>',
    "key": '<circle cx="8" cy="14" r="4"/><path d="m11 11 8.5-8.5M16 6l2.5 2.5M13.5 8.5 16 11"/>',
    "pulse": '<path d="M3 12h4l2.5-6 4 12 2.5-6h5"/>',
    "users": '<circle cx="9" cy="8.5" r="3.5"/><path d="M3 19c0-3 2.7-5 6-5s6 2 6 5"/><circle cx="17" cy="9.5" r="2.5"/><path d="M16 14.5c2.8 0 5 1.8 5 4.5"/>',
    "book": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4Z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H13a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h7Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/>',
}


def svg(name: str, cls: str = "icon") -> str:
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{ICONS.get(name, "")}</svg>'
    )


def other_page(page):
    return next(p for p in PAGES if p["locale"] != page["locale"])


# ---------------------------------------------------------------------------
# Fragments de page
# ---------------------------------------------------------------------------
def head(t, page) -> str:
    other = other_page(page)
    canonical = SITE["baseUrl"] + page["url"]
    og_image = SITE["baseUrl"] + "/" + page["ogImage"]

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": SITE["author"],
        "alternateName": SITE["fullName"],
        "jobTitle": t["hero"]["role"],
        "description": t["hero"]["intro"],
        "email": "mailto:" + SITE["email"],
        "url": canonical,
        "image": og_image,
        "sameAs": [SITE["github"], SITE["linkedin"], SITE["credly"]],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": SITE["locality"],
            "addressCountry": SITE["country"],
        },
        "worksFor": {"@type": "Organization", "name": t["experience"]["company"]},
        "alumniOf": [
            {"@type": "EducationalOrganization", "name": e["school"]}
            for e in t["education"]["items"]
        ],
        "knowsAbout": [i for g in t["skills"]["groups"] for i in g["items"]][:24],
        "knowsLanguage": [l["name"] for l in t["languages"]["items"]],
    }

    # Applique le thème mémorisé avant le premier rendu (pas de flash).
    theme_init = (
        "(function(){try{var t=localStorage.getItem('theme');"
        "if(t==='dark'||t==='light'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();"
    )

    return f"""<meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(t["meta"]["title"])}</title>
    <meta name="description" content="{esc(t["meta"]["description"])}">
    <meta name="keywords" content="{esc(t["meta"]["keywords"])}">
    <meta name="author" content="{esc(SITE["author"])}">
    <meta name="robots" content="index, follow">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="{SITE["themeColorLight"]}">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="{SITE["themeColorDark"]}">
    <link rel="canonical" href="{canonical}">
    <link rel="alternate" hreflang="{page["locale"]}" href="{SITE["baseUrl"] + page["url"]}">
    <link rel="alternate" hreflang="{other["locale"]}" href="{SITE["baseUrl"] + other["url"]}">
    <link rel="alternate" hreflang="x-default" href="{SITE["baseUrl"]}/">
    <meta property="og:type" content="profile">
    <meta property="og:site_name" content="{esc(SITE["author"])}">
    <meta property="og:locale" content="{t["localeTag"]}">
    <meta property="og:title" content="{esc(t["meta"]["title"])}">
    <meta property="og:description" content="{esc(t["meta"]["description"])}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{esc(t["meta"]["ogAlt"])}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(t["meta"]["title"])}">
    <meta name="twitter:description" content="{esc(t["meta"]["description"])}">
    <meta name="twitter:image" content="{og_image}">
    <link rel="icon" href="{page["prefix"]}assets/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="{page["prefix"]}assets/apple-touch-icon.png">
    <link rel="stylesheet" href="{page["prefix"]}assets/style.css">
    <script>{theme_init}</script>
    <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>"""


def header(t, page) -> str:
    other = other_page(page)
    other_href = "en/" if page["locale"] == "fr" else "../"
    m = t["meta"]

    links = "\n            ".join(
        f'<li><a href="#{item["id"]}" data-nav="{item["id"]}">{esc(item["label"])}</a></li>'
        for item in t["nav"]["items"]
    )

    return f"""<header class="site-header">
      <div class="shell header-inner">
        <a class="brand" href="#top">
          <span class="brand-mark" aria-hidden="true">LG</span>
          <span class="brand-text">
            <strong>{esc(SITE["author"])}</strong>
            <span>{esc(t["hero"]["role"])}</span>
          </span>
        </a>
        <nav id="site-nav" class="nav" aria-label="{esc(t["nav"]["label"])}">
          <ul>
            {links}
          </ul>
        </nav>
        <div class="header-actions">
          <button class="theme-toggle" type="button" data-theme-toggle
                  aria-label="{esc(m["themeLabel"])}" title="{esc(m["themeLabel"])}"
                  data-label-light="{esc(m["themeLight"])}" data-label-dark="{esc(m["themeDark"])}">
            {svg("sun", "icon icon-sun")}{svg("moon", "icon icon-moon")}
          </button>
          <a class="lang-switch" href="{other_href}" hreflang="{other["locale"]}"
             lang="{other["locale"]}" title="{esc(m["switchLabel"])}">
            <span aria-hidden="true">{esc(m["switchShort"])}</span>
            <span class="visually-hidden">{esc(m["switchLabel"])}</span>
          </a>
          <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav"
                  data-open="{esc(t["nav"]["menuOpen"])}" data-close="{esc(t["nav"]["menuClose"])}">
            <span class="nav-toggle-bars" aria-hidden="true"><span></span><span></span><span></span></span>
            <span class="visually-hidden">{esc(t["nav"]["menuOpen"])}</span>
          </button>
        </div>
      </div>
    </header>"""


def cv_button(t_label: str, page, cls: str = "btn btn-primary") -> str:
    if not HAS_CV:
        return ""
    return (
        f'<a class="{cls}" href="{page["prefix"]}{SITE["cvPath"]}" download>'
        f'{svg("download", "icon icon-sm")}{esc(t_label)}</a>'
    )


def hero(t, page) -> str:
    h = t["hero"]
    facts = "\n            ".join(
        f'<li>{svg(f["icon"], "icon icon-sm")}<span>{esc(f["text"])}</span></li>' for f in h["facts"]
    )
    domains = "\n            ".join(f"<li>{esc(d)}</li>" for d in h["domains"])
    stats = "\n            ".join(
        f"""<div class="stat">
              <span class="stat-value" data-count>{esc(s["value"])}</span>
              <span class="stat-label">{esc(s["label"])}</span>
            </div>"""
        for s in h["stats"]
    )
    cv = cv_button(h["ctaCv"], page)
    contact_cls = "btn" if cv else "btn btn-primary"
    sep = " :" if page["locale"] == "fr" else ":"

    return f"""<section class="hero" id="top">
        <div class="shell hero-grid">
          <div class="hero-inner">
            <p class="eyebrow">{esc(h["eyebrow"])}</p>
            <h1>{esc(h["name"])}</h1>
            <p class="hero-role">{esc(h["role"])}</p>
            <p class="hero-subtitle">{esc(h["subtitle"])}</p>
            <p class="hero-intro">{esc(h["intro"])}</p>
            <p class="hero-search">
              {svg("search", "icon icon-sm")}
              <span><strong>{esc(h["searchLabel"])}{sep}</strong> {esc(h["search"])}</span>
            </p>
            <p class="hero-domains-label">{esc(h["domainsLabel"])}</p>
            <ul class="hero-domains">
              {domains}
            </ul>
            <ul class="hero-facts">
              {facts}
            </ul>
            <div class="cta">
              {cv}
              <a class="{contact_cls}" href="#contact">{svg("mail", "icon icon-sm")}{esc(h["ctaContact"])}</a>
              <a class="btn" href="{SITE["linkedin"]}" rel="me noopener" target="_blank">{svg("linkedin", "icon icon-sm")}{esc(h["ctaLinkedin"])}</a>
              <a class="btn" href="{SITE["github"]}" rel="me noopener" target="_blank">{svg("github", "icon icon-sm")}{esc(h["ctaGithub"])}</a>
            </div>
          </div>
          {terminal(h["terminal"])}
          <div class="stats" role="group" aria-label="{esc(h["statsLabel"])}">
            {stats}
          </div>
        </div>
      </section>"""


def terminal(t) -> str:
    """Panneau « terminal d'audit » : toutes les scènes sont dans le HTML
    (lisibles sans JavaScript) ; script.js les fait défiler une par une."""
    scenes = []
    for scene in t["scenes"]:
        lines = "\n                ".join(
            f'<p class="term-line{(" sev-" + l["sev"]) if l["sev"] else ""}">{esc(l["text"])}</p>'
            for l in scene["lines"]
        )
        scenes.append(
            f"""<div class="term-scene">
                <p class="term-cmd"><span class="term-prompt" aria-hidden="true">$</span> <span class="term-cmd-text">{esc(scene["cmd"])}</span></p>
                {lines}
              </div>"""
        )
    scenes_html = "\n              ".join(scenes)
    return f"""<aside class="hero-panel" aria-label="{esc(t["title"])}">
            <div class="term">
              <div class="term-bar" aria-hidden="true"><span></span><span></span><span></span><p>{esc(t["title"])}</p></div>
              <div class="term-body" data-term>
              {scenes_html}
              </div>
            </div>
            <p class="hero-panel-note">{esc(t["note"])}</p>
          </aside>"""


def about(t) -> str:
    a = t["about"]
    blocks = "\n            ".join(
        f"""<article class="about-block">
              <h3>{esc(b["title"])}</h3>
              <p>{esc(b["text"])}</p>
            </article>"""
        for b in a["blocks"]
    )
    return f"""<section id="profil" class="section reveal">
        <div class="shell">
          <h2>{esc(a["title"])}</h2>
          <p class="lead">{esc(a["lead"])}</p>
          <div class="about-grid">
            {blocks}
          </div>
        </div>
      </section>"""


def domains(t) -> str:
    d = t["domains"]
    cards = "\n            ".join(
        f"""<article class="domain">
              <span class="domain-icon" aria-hidden="true">{svg(i["icon"])}</span>
              <h3>{esc(i["title"])}</h3>
              <p>{esc(i["text"])}</p>
            </article>"""
        for i in d["items"]
    )
    return f"""<section id="domaines" class="section section-alt reveal">
        <div class="shell">
          <h2>{esc(d["title"])}</h2>
          <p class="section-intro">{esc(d["intro"])}</p>
          <div class="domain-grid">
            {cards}
          </div>
        </div>
      </section>"""


def skills(t) -> str:
    s = t["skills"]
    groups = "\n            ".join(
        f"""<article class="skill-group">
              <h3>{esc(g["title"])}</h3>
              <ul class="tags">
                {"".join(f"<li>{esc(i)}</li>" for i in g["items"])}
              </ul>
            </article>"""
        for g in s["groups"]
    )
    return f"""<section id="competences" class="section reveal">
        <div class="shell">
          <h2>{esc(s["title"])}</h2>
          <p class="section-intro">{esc(s["intro"])}</p>
          <div class="skill-grid">
            {groups}
          </div>
          <p class="note">{esc(s["note"])}</p>
        </div>
      </section>"""


def experience(t) -> str:
    e = t["experience"]
    missions = "\n            ".join(
        f"""<article class="mission">
              <p class="mission-tag">{esc(m["tag"])}</p>
              <h4>{esc(m["title"])}</h4>
              <ul>
                {"".join(f"<li>{esc(i)}</li>" for i in m["items"])}
              </ul>
            </article>"""
        for m in e["missions"]
    )
    return f"""<section id="experience" class="section section-alt reveal">
        <div class="shell">
          <h2>{esc(e["title"])}</h2>
          <p class="section-intro">{esc(e["intro"])}</p>
          <div class="job">
            <div class="job-head">
              <div>
                <h3>{esc(e["role"])}</h3>
                <p class="job-company">{esc(e["company"])}</p>
                <p class="job-context">{esc(e["context"])}</p>
              </div>
              <p class="job-period">{esc(e["period"])}</p>
            </div>
            <h4 class="visually-hidden">{esc(e["missionsLabel"])}</h4>
            <div class="missions">
            {missions}
            </div>
          </div>
        </div>
      </section>"""


def methods(t) -> str:
    m = t["methods"]
    steps = "\n              ".join(
        f"""<li>
                <span class="step-index" aria-hidden="true">{i}</span>
                <div><strong>{esc(s["step"])}</strong><p>{esc(s["text"])}</p></div>
              </li>"""
        for i, s in enumerate(m["process"], start=1)
    )
    tools = "\n              ".join(
        f"""<div class="tool-row">
                <dt>{esc(g["label"])}</dt>
                <dd><ul class="tags tags-sm">{"".join(f"<li>{esc(i)}</li>" for i in g["items"])}</ul></dd>
              </div>"""
        for g in m["tools"]
    )
    return f"""<section id="methodes" class="section reveal">
        <div class="shell">
          <h2>{esc(m["title"])}</h2>
          <p class="section-intro">{esc(m["intro"])}</p>
          <div class="methods-grid">
            <article class="panel">
              <h3>{esc(m["processTitle"])}</h3>
              <ol class="steps">
              {steps}
              </ol>
            </article>
            <article class="panel">
              <h3>{esc(m["toolsTitle"])}</h3>
              <dl class="tool-list">
              {tools}
              </dl>
            </article>
          </div>
        </div>
      </section>"""


def projects(t) -> str:
    p = t["projects"]
    lb = p["labels"]
    cards = []
    for it in p["items"]:
        links = []
        if it.get("repo"):
            links.append(
                f'<a class="project-link" href="{it["repo"]}" rel="noopener" target="_blank">'
                f'{svg("repo", "icon icon-sm")}{esc(p["codeLabel"])}</a>'
            )
        if it.get("demo"):
            links.append(
                f'<a class="project-link" href="{it["demo"]}" rel="noopener" target="_blank">'
                f'{svg("external", "icon icon-sm")}{esc(p["demoLabel"])}</a>'
            )
        links_html = f'<p class="project-links">{"".join(links)}</p>' if links else ""
        env = "".join(f"<li>{esc(i)}</li>" for i in it["environment"])
        cards.append(
            f"""<article class="project">
              <p class="project-kind">{esc(it["kind"])}</p>
              <h3>{esc(it["name"])}</h3>
              <dl class="project-fields">
                <dt>{esc(lb["objective"])}</dt>
                <dd>{esc(it["objective"])}</dd>
                <dt>{esc(lb["problem"])}</dt>
                <dd>{inline_code(it["problem"])}</dd>
                <dt>{esc(lb["environment"])}</dt>
                <dd><ul class="tags tags-sm">{env}</ul></dd>
                <dt>{esc(lb["results"])}</dt>
                <dd>{esc(it["results"])}</dd>
                <dt>{esc(lb["skills"])}</dt>
                <dd>{esc(it["skills"])}</dd>
              </dl>
              {links_html}
            </article>"""
        )
    cards_html = "\n            ".join(cards)
    aside = ""
    if p.get("aside"):
        aside = f"""<p class="note">{esc(p["aside"])} <a href="{p["asideLink"]}" rel="noopener" target="_blank">{esc(p["codeLabel"])}</a></p>"""
    return f"""<section id="projets" class="section section-alt reveal">
        <div class="shell">
          <h2>{esc(p["title"])}</h2>
          <p class="section-intro">{esc(p["intro"])}</p>
          <div class="project-grid">
            {cards_html}
          </div>
          {aside}
          <p class="section-more">
            <a href="{SITE["github"]}" rel="noopener" target="_blank">{esc(p["allProjects"])}{svg("external", "icon icon-sm")}</a>
          </p>
        </div>
      </section>"""


def certifications(t) -> str:
    c = t["certifications"]
    items = "\n            ".join(
        f"""<li>
              <strong>{esc(i["name"])}</strong>
              <span class="cert-issuer">{esc(i["issuer"])}</span>
              {f'<span class="cert-date">{esc(i["date"])}</span>' if i.get("date") else ""}
              {f'<span class="cert-note">{esc(i["note"])}</span>' if i.get("note") else ""}
            </li>"""
        for i in c["items"]
    )
    return f"""<section id="certifications" class="section reveal">
        <div class="shell">
          <h2>{esc(c["title"])}</h2>
          <p class="section-intro">{esc(c["intro"])}</p>
          <ul class="certs">
            {items}
          </ul>
          <p class="section-more">
            <a href="{SITE["credly"]}" rel="noopener" target="_blank">{svg("badge", "icon icon-sm")}{esc(c["verifyLabel"])}</a>
          </p>
        </div>
      </section>"""


def education(t) -> str:
    e = t["education"]
    items = "\n            ".join(
        f"""<li>
              <p class="edu-period">{esc(i["period"])}</p>
              <div>
                <strong>{esc(i["degree"])}</strong>
                <span>{esc(i["school"])}</span>
                {f'<span class="edu-note">{esc(i["note"])}</span>' if i.get("note") else ""}
              </div>
            </li>"""
        for i in e["items"]
    )
    return f"""<section id="formation" class="section section-alt reveal">
        <div class="shell">
          <h2>{esc(e["title"])}</h2>
          <ol class="timeline">
            {items}
          </ol>
        </div>
      </section>"""


def languages(t) -> str:
    l = t["languages"]
    langs = "\n              ".join(
        f'<li><strong>{esc(i["name"])}</strong><span>{esc(i["level"])}</span></li>' for i in l["items"]
    )
    mobility = "\n              ".join(f"<li>{esc(m)}</li>" for m in l["mobility"])
    return f"""<section id="langues" class="section reveal">
        <div class="shell">
          <h2>{esc(l["title"])}</h2>
          <div class="split">
            <article class="panel">
              <h3>{esc(l["languagesLabel"])}</h3>
              <ul class="lang-list">
              {langs}
              </ul>
            </article>
            <article class="panel">
              <h3>{esc(l["mobilityLabel"])}</h3>
              <ul class="mobility-list">
              {mobility}
              </ul>
            </article>
          </div>
        </div>
      </section>"""


def contact(t, page) -> str:
    c = t["contact"]
    cv = cv_button(c["cvLabel"], page, cls="btn")
    cv_note = "" if HAS_CV else f'<p class="contact-note">{esc(c["cvMissing"])}</p>'
    return f"""<section id="contact" class="section section-contact reveal">
        <div class="shell">
          <h2>{esc(c["title"])}</h2>
          <p class="lead">{esc(c["lead"])}</p>
          <div class="cta">
            <a class="btn btn-primary" href="mailto:{SITE["email"]}">{svg("mail", "icon icon-sm")}{esc(c["emailLabel"])}</a>
            <a class="btn" href="{SITE["linkedin"]}" rel="me noopener" target="_blank">{svg("linkedin", "icon icon-sm")}{esc(c["linkedinLabel"])}</a>
            <a class="btn" href="{SITE["github"]}" rel="me noopener" target="_blank">{svg("github", "icon icon-sm")}{esc(c["githubLabel"])}</a>
            {cv}
          </div>
          <p class="contact-mail"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
          {cv_note}
        </div>
      </section>"""


def footer(t) -> str:
    f = t["footer"]
    return f"""<footer class="site-footer">
      <div class="shell footer-inner">
        <p>&copy; <span data-year>{date.today().year}</span> {esc(SITE["author"])} — {esc(f["rights"])}</p>
        <p class="footer-note">{esc(f["builtWith"])}</p>
        <p><a href="{SITE["sourceRepo"]}" rel="noopener" target="_blank">{esc(f["sourceLabel"])}</a></p>
      </div>
    </footer>"""


# ---------------------------------------------------------------------------
# Page complète
# ---------------------------------------------------------------------------
def render_page(t, page) -> str:
    return f"""<!doctype html>
<html lang="{t["lang"]}">
  <head>
    {head(t, page)}
  </head>
  <body>
    <a class="skip-link" href="#main">{esc(t["skipLink"])}</a>
    {header(t, page)}
    <main id="main">
      {hero(t, page)}
      {about(t)}
      {domains(t)}
      {skills(t)}
      {experience(t)}
      {methods(t)}
      {projects(t)}
      {certifications(t)}
      {education(t)}
      {languages(t)}
      {contact(t, page)}
    </main>
    {footer(t)}
    <script src="{page["prefix"]}assets/script.js" defer></script>
  </body>
</html>
"""


def sitemap() -> str:
    today = date.today().isoformat()
    entries = []
    for page in PAGES:
        alternates = "\n".join(
            f'    <xhtml:link rel="alternate" hreflang="{p["locale"]}" href="{SITE["baseUrl"]}{p["url"]}"/>'
            for p in PAGES
        )
        entries.append(
            f"""  <url>
    <loc>{SITE["baseUrl"]}{page["url"]}</loc>
{alternates}
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{"1.0" if page["locale"] == "fr" else "0.9"}</priority>
  </url>"""
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE['baseUrl']}/sitemap.xml\n"


# ---------------------------------------------------------------------------
# Écriture
# ---------------------------------------------------------------------------
def write(relative: str, content: str) -> None:
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    size = len(content.encode("utf-8")) / 1024
    print(f"  {relative:<20} {size:.1f} Ko")


def main() -> None:
    print("Génération du portfolio :")
    for page in PAGES:
        locale = json.loads((ROOT / "locales" / f"{page['locale']}.json").read_text(encoding="utf-8"))
        write(page["out"], render_page(locale, page))
    write("sitemap.xml", sitemap())
    write("robots.txt", robots())
    write(".nojekyll", "")
    print(
        "  CV détecté : le bouton de téléchargement est activé."
        if HAS_CV
        else f"  Pas de {SITE['cvPath']} : le bouton « CV » reste masqué."
    )


if __name__ == "__main__":
    main()
