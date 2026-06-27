#!/usr/bin/env python3

import json
from typing import Any, Dict, List, Optional

import click
import requests
from urllib.parse import quote


BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
REQUEST_TIMEOUT_SECONDS = 5


def fetch_entries(word: str) -> List[Dict[str, Any]]:
    api = f"{BASE_URL}{quote(word.strip())}"

    try:
        response = requests.get(api, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as exc:
        raise click.ClickException(f"Request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise click.ClickException("Dictionary API returned invalid JSON") from exc

    if response.status_code == 200:
        if not isinstance(payload, list) or not payload:
            raise click.ClickException("No definition returned")
        return payload

    if response.status_code == 404:
        message = f"Word not found: {word}"
        if isinstance(payload, dict) and payload.get("resolution"):
            message = f"{message}\n{payload['resolution']}"
        raise click.ClickException(message)

    raise click.ClickException(
        f"Dictionary API returned HTTP {response.status_code} for {word}"
    )


def first_audio(entry: Dict[str, Any]) -> Optional[str]:
    for phonetic in entry.get("phonetics", []):
        audio = phonetic.get("audio")
        if audio:
            return audio
    return None


def first_phonetic(entry: Dict[str, Any]) -> Optional[str]:
    if entry.get("phonetic"):
        return entry["phonetic"]
    for phonetic in entry.get("phonetics", []):
        text = phonetic.get("text")
        if text:
            return text
    return None


def unique_values(values: List[str]) -> List[str]:
    seen = set()
    unique = []
    for value in values:
        if value and value not in seen:
            unique.append(value)
            seen.add(value)
    return unique


def normalize_lookup(entries: List[Dict[str, Any]], show_all: bool) -> Dict[str, Any]:
    entry = entries[0]
    definitions = []

    for meaning in entry.get("meanings", []):
        part_of_speech = meaning.get("partOfSpeech", "unknown")
        meaning_synonyms = meaning.get("synonyms", [])
        meaning_antonyms = meaning.get("antonyms", [])

        for definition in meaning.get("definitions", []):
            definitions.append(
                {
                    "part_of_speech": part_of_speech,
                    "definition": definition.get("definition", ""),
                    "example": definition.get("example"),
                    "synonyms": unique_values(
                        meaning_synonyms + definition.get("synonyms", [])
                    ),
                    "antonyms": unique_values(
                        meaning_antonyms + definition.get("antonyms", [])
                    ),
                }
            )
            if not show_all:
                break
        if definitions and not show_all:
            break

    if not definitions:
        raise click.ClickException("No definition returned")

    return {
        "word": entry.get("word"),
        "phonetic": first_phonetic(entry),
        "audio": first_audio(entry),
        "definitions": definitions,
    }


def render_plain(lookup: Dict[str, Any]) -> str:
    lines = [f"Word: {lookup['word']}"]
    if lookup.get("phonetic"):
        lines.append(f"Phonetic: {lookup['phonetic']}")
    if lookup.get("audio"):
        lines.append(f"Audio: {lookup['audio']}")

    for index, definition in enumerate(lookup["definitions"], start=1):
        lines.append("")
        lines.append(f"[{index}] {definition['part_of_speech']}")
        lines.append(f"Definition: {definition['definition']}")
        if definition.get("example"):
            lines.append(f"Example: {definition['example']}")
        if definition.get("synonyms"):
            lines.append(f"Synonyms: {', '.join(definition['synonyms'])}")
        if definition.get("antonyms"):
            lines.append(f"Antonyms: {', '.join(definition['antonyms'])}")

    return "\n".join(lines)


def render_rich(lookup: Dict[str, Any]) -> None:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
    except ImportError:
        click.echo(render_plain(lookup))
        return

    console = Console()
    title = Text(lookup["word"], style="bold cyan")
    if lookup.get("phonetic"):
        title.append(f"  {lookup['phonetic']}", style="dim italic")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Part", style="yellow", no_wrap=True)
    table.add_column("Definition")
    table.add_column("Example", style="italic green")

    for index, definition in enumerate(lookup["definitions"], start=1):
        detail = definition["definition"]
        extras = []
        if definition.get("synonyms"):
            extras.append(f"synonyms: {', '.join(definition['synonyms'])}")
        if definition.get("antonyms"):
            extras.append(f"antonyms: {', '.join(definition['antonyms'])}")
        if extras:
            detail = f"{detail}\n[dim]{' | '.join(extras)}[/dim]"
        table.add_row(
            str(index),
            definition["part_of_speech"],
            detail,
            definition.get("example") or "",
        )

    if lookup.get("audio"):
        table.caption = f"Audio: {lookup['audio']}"

    console.print(Panel(table, title=title, border_style="cyan"))


@click.command()
@click.argument('word')
@click.option("--all", "show_all", is_flag=True, help="Show all definitions.")
@click.option("--json", "as_json", is_flag=True, help="Print normalized JSON.")
@click.option("--plain", is_flag=True, help="Print plain text without rich formatting.")
@click.option("--no-color", is_flag=True, help="Alias for --plain.")
def dict_lookup(word: str, show_all: bool, as_json: bool, plain: bool, no_color: bool) -> None:
    """Query dictionary API with positional word argument; return definition and other information about word"""
    entries = fetch_entries(word)
    lookup = normalize_lookup(entries, show_all=show_all)

    if as_json:
        click.echo(json.dumps(lookup, indent=2))
    elif plain or no_color:
        click.echo(render_plain(lookup))
    else:
        render_rich(lookup)


if __name__ == "__main__":
    dict_lookup()
