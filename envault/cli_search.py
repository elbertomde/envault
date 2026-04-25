"""CLI commands for searching vault contents."""

from __future__ import annotations

from pathlib import Path

import click

from envault.search import SearchError, search_vault


@click.group("search")
def search_group() -> None:
    """Search for keys or values inside a vault."""


@search_group.command("run")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.argument("query")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--keys-only",
    is_flag=True,
    default=False,
    help="Search only key names, not values.",
)
@click.option(
    "--case-sensitive",
    is_flag=True,
    default=False,
    help="Perform a case-sensitive search.",
)
def search_cmd(
    vault_file: Path,
    query: str,
    password: str,
    keys_only: bool,
    case_sensitive: bool,
) -> None:
    """Search QUERY inside VAULT_FILE."""
    try:
        matches = search_vault(
            vault_file,
            password,
            query,
            keys_only=keys_only,
            case_sensitive=case_sensitive,
        )
    except SearchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not matches:
        click.echo("No matches found.")
        return

    click.echo(f"Found {len(matches)} match(es) in {vault_file}:\n")
    for match in matches:
        if keys_only:
            click.echo(f"  {match.key}")
        else:
            click.echo(f"  {match.key}={match.value}")
