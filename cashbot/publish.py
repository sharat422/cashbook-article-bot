"""Build the public static site (publication/bolcash-guides-site/dist) from an approved article.
Host-agnostic: upload the dist folder to any static host (Cloudflare Pages, Netlify, GitHub Pages)."""
import html
import os
import re
from datetime import date

from .settings import ROOT, product_facts, read_json, write_json

CSS = ("body{max-width:850px;margin:16px auto;padding:16px;font:18px/1.6 system-ui}"
       "table{display:block;overflow-x:auto;border-collapse:collapse}td,th{border:1px solid #ccc;padding:8px}"
       "h1{font-size:clamp(1.8rem,5vw,2.4rem)}a{overflow-wrap:anywhere}nav{margin-bottom:24px}"
       ".cta{margin:32px 0;padding:16px;border:1px solid #ccc;border-radius:8px}"
       ".cta a{display:inline-block;min-height:44px;font-weight:600}")


def site():
    return ROOT / "publication/bolcash-guides-site"


def page(title, description, body, url="", extra_head=""):
    meta = f'<meta name="description" content="{html.escape(description, quote=True)}">'
    if url:
        meta += (f'<link rel="canonical" href="{url}"><meta property="og:title" content="{html.escape(title, quote=True)}">'
                 f'<meta property="og:description" content="{html.escape(description, quote=True)}">'
                 f'<meta property="og:url" content="{url}"><meta property="og:type" content="article">')
    return ('<!doctype html><html lang="en-IN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{html.escape(title)} | Bolcash</title>{meta}<style>{CSS}</style>{extra_head}</head>"
            f'<body><nav><a href="/guides/">Bolcash practical guides</a></nav><main>{body}</main></body></html>')


def build_indexes(articles):
    items = "".join(f'<a href="/guides/{a["slug"]}/">{html.escape(a["title"])}</a><p>{html.escape(a["description"])}</p>'
                    for a in reversed(articles))
    body = ('<h1>Bolcash practical guides</h1><p>Practical guides for FMCG distributors, '
            f"agencies and their teams.</p>{items}")
    for name in ("index.html", "guides/index.html"):
        path = site() / "dist" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page("Practical guides", "Practical guides for FMCG distributors and agencies.", body),
                        encoding="utf-8")


def publish(job, slug=None, description=None):
    approval = read_json(ROOT / f"approved/{job}.approval.json")
    if approval["demo"]:
        raise ValueError("Demo articles cannot be published.")
    raw = (ROOT / f"approved/{job}.html").read_text(encoding="utf-8")
    body = raw.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    h1 = re.search(r"<h1>(.*?)</h1>", body, re.S)
    if not h1:
        raise ValueError("Approved article has no title.")
    title = html.unescape(re.sub(r"<[^>]+>", "", h1[1])).strip()
    slug = slug or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:70]
    first = re.search(r"</h1>\s*<p>(.*?)</p>", body, re.S)
    description = description or html.unescape(re.sub(r"<[^>]+>", "", first[1] if first else title))[:155].strip()
    today = date.today()
    base = os.getenv("SITE_URL", "").rstrip("/")
    url = f"{base}/guides/{slug}/" if base else ""
    cta = product_facts().get("marketing_url", "")
    if cta.startswith("https://"):  # the one approved call to action; omitted until a real URL exists
        body += f'<div class="cta"><a href="{html.escape(cta, quote=True)}">Join the Bolcash waitlist</a></div>'
    body = f'<p>Published: <time datetime="{today}">{today.strftime("%d %B %Y")}</time></p>' + body
    target = site() / "dist/guides" / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(page(title, description, body, url), encoding="utf-8")

    registry = site() / "articles.json"
    articles = [a for a in (read_json(registry) if registry.exists() else []) if a["slug"] != slug]
    articles.append({"slug": slug, "title": title, "description": description, "date": str(today)})
    write_json(registry, articles)
    build_indexes(articles)
    if base:
        dist = site() / "dist"
        urls = [f"{base}/", f"{base}/guides/"] + [f"{base}/guides/{a['slug']}/" for a in articles]
        (dist / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>", encoding="utf-8")
        (dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    approval.update({"publicly_published": True, "published_slug": slug, "published_on": str(today)})
    write_json(ROOT / f"approved/{job}.approval.json", approval)
    return slug, target / "index.html"
