#!/usr/bin/env python3

import click
import requests
from urllib.parse import urljoin


@click.command()
@click.argument('word')
def dict_lookup(word) -> None:
    """Query dictionary API with positional word argument; return definition and other information about word"""
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

    api = urljoin(url, word)
    r = requests.get(api)

    status = r.status_code
    response = r.json()

    attrib = meanings = definitions = {}

    if status == 200:
        try:
            attrib: dict = response[0]
            meanings: dict = attrib.get('meanings')[0]
            definitions: dict = meanings.get('definitions')[0]
        except TypeError:
            click.echo("No definition returned")
            exit(1)
        click.echo(f"Word: {attrib.get('word')}")
        click.echo(f"Type: {meanings.get('partOfSpeech')}")
        click.echo(f"Definition: {definitions.get('definition')}")
        click.echo(f"Example: {definitions.get('example')}")
    elif status == 404:
        click.echo(f"Word not found: {word}")


if __name__ == "__main__":
    dict_lookup()
