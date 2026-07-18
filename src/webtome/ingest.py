"""Fetch articles from feeds or single URLs and store them as Markdown."""

from __future__ import annotations

import re
from datetime import date

import feedparser
import trafilatura

from .library import Article, Library

_FEED_LINK_RE = re.compile(
    r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*>', re.IGNORECASE
)
_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def fetch_article(url: str) -> tuple[dict, str] | None:
    """Download one page and return (metadata, markdown body), or None."""
    html = trafilatura.fetch_url(url)
    if not html:
        return None
    body = trafilatura.extract(
        html,
        output_format="markdown",
        include_formatting=True,
        include_links=False,
        include_images=False,
        include_comments=False,
    )
    if not body:
        return None
    meta_obj = trafilatura.extract_metadata(html)
    meta: dict = {
        "title": (meta_obj.title if meta_obj else None) or url,
        "author": meta_obj.author if meta_obj else None,
        "date": meta_obj.date if meta_obj else None,
        "source": meta_obj.sitename if meta_obj else None,
        "source_url": url,
        "fetched": date.today().isoformat(),
        "volume": None,
    }
    meta = {k: v for k, v in meta.items() if v is not None or k == "volume"}
    return meta, body


def discover_feed(url: str) -> str | None:
    """If ``url`` is an HTML page advertising a feed, return the feed URL."""
    html = trafilatura.fetch_url(url)
    if not html:
        return None
    match = _FEED_LINK_RE.search(html)
    if not match:
        return None
    href = _HREF_RE.search(match.group(0))
    if not href:
        return None
    feed_url = href.group(1)
    if feed_url.startswith("/"):
        base = re.match(r"https?://[^/]+", url)
        if base:
            feed_url = base.group(0) + feed_url
    return feed_url


def is_feed(url: str) -> bool:
    parsed = feedparser.parse(url)
    return bool(parsed.entries)


def sync_feeds(
    library: Library, limit: int | None = None, on_event=None
) -> list[Article]:
    """Fetch new entries from every feed in sources.yaml. Returns new articles."""
    notify = on_event or (lambda _msg: None)
    known = library.known_urls()
    new_articles: list[Article] = []
    for source in library.sources:
        feed_url = source["url"]
        parsed = feedparser.parse(feed_url)
        entries = parsed.entries[:limit] if limit else parsed.entries
        notify(f"{feed_url}: {len(entries)} entries")
        for entry in entries:
            link = entry.get("link")
            if not link or link in known:
                continue
            fetched = fetch_article(link)
            if fetched is None:
                fetched = _from_feed_entry(entry)
            if fetched is None:
                notify(f"  skipped (no content): {link}")
                continue
            meta, body = fetched
            if source.get("tags"):
                meta["tags"] = source["tags"]
            article = library.save_article(meta, body)
            known.add(link)
            new_articles.append(article)
            notify(f"  + {article.slug}")
    return new_articles


def _from_feed_entry(entry) -> tuple[dict, str] | None:
    """Fallback: build the article from the feed entry's own HTML content."""
    html = None
    if entry.get("content"):
        html = entry.content[0].get("value")
    html = html or entry.get("summary")
    if not html:
        return None
    body = trafilatura.extract(
        f"<html><body>{html}</body></html>",
        output_format="markdown",
        include_formatting=True,
        include_links=False,
        include_images=False,
    )
    if not body:
        return None
    published = entry.get("published") or entry.get("updated")
    meta = {
        "title": entry.get("title") or entry.get("link"),
        "author": entry.get("author"),
        "date": published[:10] if published else None,
        "source_url": entry.get("link"),
        "fetched": date.today().isoformat(),
        "volume": None,
    }
    meta = {k: v for k, v in meta.items() if v is not None or k == "volume"}
    return meta, body
