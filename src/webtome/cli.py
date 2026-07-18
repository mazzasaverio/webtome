"""webtome command line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import ingest, scaffold
from .build import BuildError, build_volume
from .library import Library, LibraryError

app = typer.Typer(
    help="Turn web feeds and articles into print-ready books, volume after volume.",
    no_args_is_help=True,
)
source_app = typer.Typer(help="Manage feed sources.", no_args_is_help=True)
volume_app = typer.Typer(help="Create and organize volumes.", no_args_is_help=True)
app.add_typer(source_app, name="source")
app.add_typer(volume_app, name="volume")


def _library() -> Library:
    try:
        return Library.find()
    except LibraryError as exc:
        typer.secho(str(exc), fg="red", err=True)
        raise typer.Exit(1)


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Directory for the new library."),
    name: Optional[str] = typer.Option(None, help="Library name (shown on title pages)."),
) -> None:
    """Create a new webtome library in DIRECTORY."""
    created = scaffold.init_library(directory, name=name)
    typer.secho(f"Library created in {created}", fg="green")
    typer.echo("Next steps:")
    typer.echo("  webtome source add <feed-url>   # follow a blog or feed")
    typer.echo("  webtome sync                    # fetch new articles")
    typer.echo("  webtome add <article-url>       # or grab a single article")


@source_app.command("add")
def source_add(
    url: str = typer.Argument(..., help="Feed URL, or a site URL (feed is auto-discovered)."),
    tag: list[str] = typer.Option([], "--tag", help="Tag new articles from this source."),
) -> None:
    """Follow a blog or feed."""
    library = _library()
    feed_url = url
    if not ingest.is_feed(url):
        discovered = ingest.discover_feed(url)
        if discovered and ingest.is_feed(discovered):
            typer.echo(f"Discovered feed: {discovered}")
            feed_url = discovered
        else:
            typer.secho(
                f"{url} does not look like a feed and none was discovered on the page.\n"
                "For a single article use: webtome add <url>",
                fg="red",
                err=True,
            )
            raise typer.Exit(1)
    try:
        library.add_source(feed_url, tags=list(tag) or None)
    except LibraryError as exc:
        typer.secho(str(exc), fg="red", err=True)
        raise typer.Exit(1)
    typer.secho(f"Following {feed_url}", fg="green")


@source_app.command("list")
def source_list() -> None:
    """List followed feeds."""
    library = _library()
    if not library.sources:
        typer.echo("No sources yet. Add one with: webtome source add <url>")
        return
    for source in library.sources:
        tags = f"  [{', '.join(source['tags'])}]" if source.get("tags") else ""
        typer.echo(f"{source['url']}{tags}")


@app.command()
def sync(
    limit: Optional[int] = typer.Option(
        None, help="Max entries to consider per feed (default: all)."
    ),
) -> None:
    """Fetch new articles from all followed feeds."""
    library = _library()
    new = ingest.sync_feeds(library, limit=limit, on_event=typer.echo)
    typer.secho(f"{len(new)} new article(s).", fg="green")


@app.command()
def add(url: str = typer.Argument(..., help="URL of a single article to grab.")) -> None:
    """Fetch one article by URL and add it to the library."""
    library = _library()
    if url in library.known_urls():
        typer.secho("Already in the library.", fg="yellow")
        raise typer.Exit(0)
    fetched = ingest.fetch_article(url)
    if fetched is None:
        typer.secho(f"Could not extract an article from {url}", fg="red", err=True)
        raise typer.Exit(1)
    meta, body = fetched
    article = library.save_article(meta, body)
    typer.secho(f"+ {article.slug}", fg="green")


@app.command()
def status() -> None:
    """Show library overview: sources, inbox, volumes."""
    library = _library()
    articles = library.articles()
    unassigned = [a for a in articles if not a.volume]
    typer.echo(f"Library: {library.config.get('name', library.root.name)} ({library.root})")
    typer.echo(f"Sources: {len(library.sources)} feed(s)")
    typer.echo(f"Articles: {len(articles)} total, {len(unassigned)} not yet in a volume")
    for volume in library.volumes():
        marker = "printed" if volume.printed else "draft"
        typer.echo(f"  {volume.name}: {volume.title} [{marker}, {len(volume.article_slugs())} articles]")


@app.command("list")
def list_articles(
    unassigned: bool = typer.Option(False, "--unassigned", help="Only articles not in a volume."),
) -> None:
    """List articles (slug, title, volume)."""
    library = _library()
    for article in library.articles():
        if unassigned and article.volume:
            continue
        volume = article.volume or "-"
        typer.echo(f"{article.slug}\t{volume}\t{article.title}")


@volume_app.command("new")
def volume_new(
    title: Optional[str] = typer.Option(None, help="Volume title (default: library name).")
) -> None:
    """Start a new volume (numbered automatically)."""
    library = _library()
    volume = library.new_volume(title=title)
    typer.secho(f"Created {volume.name}: {volume.title}", fg="green")
    typer.echo(f"Edit {volume.path / 'volume.yaml'} to organize it, or run:")
    typer.echo(f"  webtome volume fill {volume.name}")


@volume_app.command("add")
def volume_add(
    name: str = typer.Argument(..., help="Volume name, e.g. volume-01."),
    slugs: list[str] = typer.Argument(..., help="Article slugs to append."),
) -> None:
    """Append articles to a volume."""
    library = _library()
    _assign(library, name, slugs)


@volume_app.command("fill")
def volume_fill(name: str = typer.Argument(..., help="Volume name, e.g. volume-01.")) -> None:
    """Add every article not yet assigned to any volume."""
    library = _library()
    slugs = [a.slug for a in library.articles() if not a.volume]
    if not slugs:
        typer.echo("No unassigned articles.")
        return
    _assign(library, name, slugs)


def _assign(library: Library, name: str, slugs: list[str]) -> None:
    try:
        volume = library.volume(name)
    except LibraryError as exc:
        typer.secho(str(exc), fg="red", err=True)
        raise typer.Exit(1)
    if "sections" in volume.data:
        typer.secho(
            f"{name} is organized in sections; edit volume.yaml directly.", fg="red", err=True
        )
        raise typer.Exit(1)
    existing = volume.data.setdefault("articles", [])
    added = 0
    for slug in slugs:
        try:
            article = library.article(slug)
        except LibraryError as exc:
            typer.secho(str(exc), fg="red", err=True)
            raise typer.Exit(1)
        if slug in existing:
            continue
        existing.append(slug)
        article.meta["volume"] = name
        library.update_article(article)
        added += 1
    library.save_volume(volume)
    typer.secho(f"{added} article(s) added to {name}.", fg="green")


@volume_app.command("mark-printed")
def volume_mark_printed(name: str = typer.Argument(...)) -> None:
    """Mark a volume as printed (frozen); new articles go to the next volume."""
    library = _library()
    try:
        volume = library.volume(name)
    except LibraryError as exc:
        typer.secho(str(exc), fg="red", err=True)
        raise typer.Exit(1)
    volume.data["status"] = "printed"
    library.save_volume(volume)
    typer.secho(f"{name} marked as printed.", fg="green")


@app.command()
def build(name: str = typer.Argument(..., help="Volume name, e.g. volume-01.")) -> None:
    """Build a volume into a print-ready PDF in dist/."""
    library = _library()
    try:
        output = build_volume(library, name, on_event=typer.echo)
    except (BuildError, LibraryError) as exc:
        typer.secho(str(exc), fg="red", err=True)
        raise typer.Exit(1)
    typer.secho(f"Built {output}", fg="green")


def main() -> None:
    app()
