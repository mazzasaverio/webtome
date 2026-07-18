"""Library workspace: articles, sources, volumes, config.

A library is any directory containing a ``webtome.yaml``. Articles live in
``articles/`` as Markdown files with YAML frontmatter; volumes live in
``volumes/<name>/volume.yaml``; built PDFs land in ``dist/``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from slugify import slugify

CONFIG_FILE = "webtome.yaml"
SOURCES_FILE = "sources.yaml"

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


@dataclass
class Article:
    slug: str
    path: Path
    meta: dict
    body: str

    @property
    def title(self) -> str:
        return self.meta.get("title") or self.slug

    @property
    def volume(self) -> str | None:
        return self.meta.get("volume")


@dataclass
class Volume:
    name: str  # directory name, e.g. "volume-01"
    path: Path
    data: dict = field(default_factory=dict)

    @property
    def title(self) -> str:
        return self.data.get("title") or self.name

    @property
    def printed(self) -> bool:
        return self.data.get("status") == "printed"

    def article_slugs(self) -> list[str]:
        """All slugs in reading order, whether flat or grouped in sections."""
        if "sections" in self.data:
            slugs: list[str] = []
            for section in self.data["sections"] or []:
                slugs.extend(section.get("articles") or [])
            return slugs
        return list(self.data.get("articles") or [])


class LibraryError(Exception):
    pass


class Library:
    def __init__(self, root: Path):
        self.root = root.resolve()

    # -- discovery ---------------------------------------------------------

    @classmethod
    def find(cls, start: Path | None = None) -> "Library":
        current = (start or Path.cwd()).resolve()
        for candidate in [current, *current.parents]:
            if (candidate / CONFIG_FILE).is_file():
                return cls(candidate)
        raise LibraryError(
            f"No {CONFIG_FILE} found here or in any parent directory. "
            "Run 'webtome init' to create a library."
        )

    # -- paths -------------------------------------------------------------

    @property
    def articles_dir(self) -> Path:
        return self.root / "articles"

    @property
    def volumes_dir(self) -> Path:
        return self.root / "volumes"

    @property
    def dist_dir(self) -> Path:
        return self.root / "dist"

    # -- config and sources ------------------------------------------------

    @property
    def config(self) -> dict:
        return _read_yaml(self.root / CONFIG_FILE) or {}

    @property
    def sources(self) -> list[dict]:
        data = _read_yaml(self.root / SOURCES_FILE) or {}
        return data.get("feeds") or []

    def add_source(self, url: str, title: str | None = None, tags: list[str] | None = None) -> None:
        path = self.root / SOURCES_FILE
        data = _read_yaml(path) or {}
        feeds = data.setdefault("feeds", [])
        if any(f.get("url") == url for f in feeds):
            raise LibraryError(f"Source already present: {url}")
        entry: dict = {"url": url}
        if title:
            entry["title"] = title
        if tags:
            entry["tags"] = tags
        feeds.append(entry)
        _write_yaml(path, data)

    # -- articles ----------------------------------------------------------

    def articles(self) -> list[Article]:
        if not self.articles_dir.is_dir():
            return []
        items = [self._load_article(p) for p in sorted(self.articles_dir.glob("*.md"))]
        return [a for a in items if a is not None]

    def article(self, slug: str) -> Article:
        path = self.articles_dir / f"{slug}.md"
        if not path.is_file():
            raise LibraryError(f"No such article: {slug}")
        loaded = self._load_article(path)
        assert loaded is not None
        return loaded

    def known_urls(self) -> set[str]:
        return {a.meta["source_url"] for a in self.articles() if a.meta.get("source_url")}

    def save_article(self, meta: dict, body: str) -> Article:
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        base = slugify(meta.get("title") or "untitled")[:70] or "untitled"
        slug, n = base, 2
        while (self.articles_dir / f"{slug}.md").exists():
            slug, n = f"{base}-{n}", n + 1
        path = self.articles_dir / f"{slug}.md"
        self._write_article(path, meta, body)
        return Article(slug=slug, path=path, meta=meta, body=body)

    def update_article(self, article: Article) -> None:
        self._write_article(article.path, article.meta, article.body)

    def _write_article(self, path: Path, meta: dict, body: str) -> None:
        frontmatter = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
        path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")

    def _load_article(self, path: Path) -> Article | None:
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(text)
        if not match:
            return Article(slug=path.stem, path=path, meta={}, body=text)
        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        return Article(slug=path.stem, path=path, meta=meta, body=text[match.end():])

    # -- volumes -----------------------------------------------------------

    def volumes(self) -> list[Volume]:
        if not self.volumes_dir.is_dir():
            return []
        result = []
        for d in sorted(self.volumes_dir.iterdir()):
            if (d / "volume.yaml").is_file():
                result.append(Volume(name=d.name, path=d, data=_read_yaml(d / "volume.yaml") or {}))
        return result

    def volume(self, name: str) -> Volume:
        path = self.volumes_dir / name / "volume.yaml"
        if not path.is_file():
            raise LibraryError(f"No such volume: {name}")
        return Volume(name=name, path=path.parent, data=_read_yaml(path) or {})

    def save_volume(self, volume: Volume) -> None:
        volume.path.mkdir(parents=True, exist_ok=True)
        _write_yaml(volume.path / "volume.yaml", volume.data)

    def new_volume(self, title: str | None = None) -> Volume:
        number = len(self.volumes()) + 1
        name = f"volume-{number:02d}"
        volume = Volume(
            name=name,
            path=self.volumes_dir / name,
            data={
                "number": number,
                "title": title or self.config.get("name") or "Collected Articles",
                "subtitle": f"Volume {number}",
                "status": "draft",
                "articles": [],
            },
        )
        self.save_volume(volume)
        return volume


def _read_yaml(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
