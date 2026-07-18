"""Build a volume into a print-ready PDF: Markdown -> Typst (pandoc) -> PDF."""

from __future__ import annotations

import shutil
import subprocess
from importlib import resources
from pathlib import Path

import typst

from .library import Library, Volume


class BuildError(Exception):
    pass


def build_volume(library: Library, name: str, on_event=None) -> Path:
    notify = on_event or (lambda _msg: None)
    _require_pandoc()
    volume = library.volume(name)
    slugs = volume.article_slugs()
    if not slugs:
        raise BuildError(f"{name} has no articles. Add some with 'webtome volume add'.")

    build_dir = library.dist_dir / ".build" / name
    build_dir.mkdir(parents=True, exist_ok=True)
    template = resources.files("webtome.templates").joinpath("book.typ").read_text()
    (build_dir / "book.typ").write_text(template, encoding="utf-8")

    main = _render_main(library, volume, notify)
    main_path = build_dir / "main.typ"
    main_path.write_text(main, encoding="utf-8")

    output = library.dist_dir / f"{name}.pdf"
    notify(f"compiling {output.name} ...")
    typst.compile(main_path, output=output, root=build_dir)
    return output


def _render_main(library: Library, volume: Volume, notify) -> str:
    config = library.config
    lines = [
        '#import "book.typ": book, chapter, part, sources-page',
        "#show: book.with(",
        f"  title: {_s(volume.data.get('title') or volume.name)},",
    ]
    if volume.data.get("subtitle"):
        lines.append(f"  subtitle: {_s(volume.data['subtitle'])},")
    if config.get("author"):
        lines.append(f"  curator: {_s(config['author'])},")
    if volume.data.get("date"):
        lines.append(f"  date: {_s(str(volume.data['date']))},")
    lines.append(")")
    lines.append("")

    sources: list[tuple[str, str]] = []

    def render_article(slug: str) -> None:
        article = library.article(slug)
        notify(f"  {slug}")
        body_typ = _markdown_to_typst(article.body, slug)
        meta = article.meta
        args = [f"title: {_s(article.title)}"]
        if meta.get("author"):
            args.append(f"author: {_s(str(meta['author']))}")
        if meta.get("source_url"):
            args.append(f"source: {_s(meta['source_url'])}")
            sources.append((article.title, meta["source_url"]))
        if meta.get("date"):
            args.append(f"date: {_s(str(meta['date']))}")
        lines.append(f"#chapter({', '.join(args)})[")
        lines.append(body_typ)
        lines.append("]")
        lines.append("")

    if "sections" in volume.data:
        for section in volume.data["sections"] or []:
            if section.get("title"):
                lines.append(f"#part({_s(section['title'])})")
                lines.append("")
            for slug in section.get("articles") or []:
                render_article(slug)
    else:
        for slug in volume.data.get("articles") or []:
            render_article(slug)

    if sources:
        entries = ", ".join(f"({_s(t)}, {_s(u)})" for t, u in sources)
        lines.append(f"#sources-page(({entries},))")
        lines.append("")

    return "\n".join(lines)


def _markdown_to_typst(markdown: str, slug: str) -> str:
    result = subprocess.run(
        ["pandoc", "--from", "gfm", "--to", "typst", "--wrap", "none"],
        input=markdown,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BuildError(f"pandoc failed on article '{slug}':\n{result.stderr}")
    return result.stdout


def _s(value: str) -> str:
    """Quote a Python string as a Typst string literal."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _require_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise BuildError(
            "pandoc is required to build volumes but was not found on PATH. "
            "Install it from https://pandoc.org/installing.html "
            "(e.g. 'sudo apt install pandoc' or 'brew install pandoc')."
        )
