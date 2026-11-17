"""Bounded feed collection and opt-in HTML extraction; no unrestricted crawling."""
import calendar
import hashlib
import html
import ipaddress
import re
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import feedparser
import httpx
import trafilatura
from langchain_core.tools import tool

from .settings import ROOT, read_json, write_json

USER_AGENT = "CashbookResearchBot/0.1"
MAX_BYTES = 2_000_000


def checked_url(url, hosts):
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in hosts
            or parts.username or parts.password or parts.port not in (None, 443)):
        raise ValueError("Only HTTPS URLs on exact, approved hostnames are allowed.")
    addresses = socket.getaddrinfo(parts.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
        raise ValueError("Private, loopback and non-public addresses are not allowed.")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def get_text(url, hosts):
    # Revalidate each redirect; do not forward authentication to source websites.
    with httpx.Client(timeout=25, headers={"User-Agent": USER_AGENT}, follow_redirects=False) as client:
        for _ in range(4):
            url = checked_url(url, hosts)
            with client.stream("GET", url) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers["location"])
                    continue
                response.raise_for_status()
                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > MAX_BYTES:
                        raise ValueError("Source exceeds the 2 MB tutorial limit.")
                return content.decode(response.encoding or "utf-8", errors="replace"), url
    raise ValueError("Too many redirects; review this source manually.")


def allowed_by_robots(url, hosts):
    parts = urlsplit(url)
    robots_url = f"https://{parts.netloc}/robots.txt"
    try:
        text, _ = get_text(robots_url, hosts)
    except httpx.HTTPStatusError as exc:
        # A missing robots file is different from a forbidden/unavailable one.
        return exc.response.status_code == 404
    except (httpx.HTTPError, ValueError, OSError):
        return False
    parser = RobotFileParser()
    parser.parse(text.splitlines())
    return parser.can_fetch(USER_AGENT, url)


def fetch_page(url, registry=None):
    registry = registry if registry is not None else read_json(ROOT / "sources.json")
    host = urlsplit(url).hostname
    rule = next((s for s in registry if host in s["hosts"]
                 and s.get("full_text_allowed") and s.get("enabled")), None)
    if rule is None:
        raise ValueError("Full-page extraction is not enabled for this source in sources.json.")
    if not allowed_by_robots(url, rule["hosts"]):
        raise ValueError("Robots rules deny access or could not be checked.")
    raw, final_url = get_text(url, rule["hosts"])
    if not allowed_by_robots(final_url, rule["hosts"]):
        raise ValueError("The destination page does not allow this bot.")
    text = trafilatura.extract(raw, include_comments=False, include_tables=True)
    if not text or len(text) < 150:
        raise ValueError("No useful article text found; this may require JavaScript or manual research.")
    return text[:8000]


@tool
def fetch_approved_page(url: str) -> str:
    """Extract text from an explicitly enabled, approved public HTML source."""
    return fetch_page(url)


def collect():
    result, warnings = [], []
    now = datetime.now(timezone.utc)
    for rule in read_json(ROOT / "sources.json"):
        if not rule.get("enabled"):
            continue
        try:
            if not allowed_by_robots(rule["feed_url"], rule["hosts"]):
                raise ValueError("Feed access denied or robots rules unavailable.")
            raw, _ = get_text(rule["feed_url"], rule["hosts"])
            parsed = feedparser.parse(raw)
            if not parsed.entries:
                raise ValueError("No RSS/Atom entries found.")
            extracted_pages = 0
            for entry in parsed.entries[:15]:
                url = entry.get("link", "")
                try:
                    url = checked_url(url, rule["hosts"])
                except (ValueError, OSError):
                    continue
                date_parts = entry.get("published_parsed") or entry.get("updated_parsed")
                published = None
                if date_parts:
                    published = datetime.fromtimestamp(calendar.timegm(date_parts), timezone.utc)
                    age = (now - published).total_seconds() / 86400
                    if age > 30 or age < -1:
                        continue
                title = html.unescape(entry.get("title", "Untitled"))
                summary = html.unescape(re.sub(r"<[^>]+>", " ", entry.get("summary", "")))
                text = f"{title}\n{summary}".strip()
                kind = "feed summary; verify the linked original before publication"
                if rule.get("full_text_allowed") and extracted_pages < 2:
                    extracted_pages += 1
                    time.sleep(2)
                    try:
                        text = fetch_page(url)
                        kind = "extracted page; event date still needs review"
                    except (ValueError, httpx.HTTPError, OSError):
                        warnings.append(f"Could not extract {url}; kept its feed summary.")
                result.append({
                    "id": hashlib.sha256(url.encode()).hexdigest()[:12],
                    "title": title, "url": url, "publisher": rule["name"],
                    "published_at": published.isoformat() if published else None,
                    "retrieved_at": now.isoformat(), "kind": kind, "text": text[:8000],
                })
        except (ValueError, httpx.HTTPError, OSError) as exc:
            warnings.append(f"{rule['name']}: {type(exc).__name__}: {exc}")
    unique = {s["id"]: s for s in result}
    packet = {"collected_at": now.isoformat(), "sources": list(unique.values()), "warnings": warnings}
    write_json(ROOT / "data/inbox.json", packet)
    return packet
