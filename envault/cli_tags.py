"""CLI commands for managing vault tags."""

from __future__ import annotations

from pathlib import Path

import click

from envault.tags import TagError, TagManager

DEFAULT_TAG_FILE = Path(".envault_tags.json")


@click.group("tags")
def tag_group() -> None:
    """Manage tags for vault files."""


@tag_group.command("add")
@click.argument("vault_name")
@click.argument("tag")
@click.option("--tag-file", default=str(DEFAULT_TAG_FILE), show_default=True)
def add_tag_cmd(vault_name: str, tag: str, tag_file: str) -> None:
    """Add TAG to VAULT_NAME."""
    manager = TagManager(Path(tag_file))
    try:
        manager.add_tag(vault_name, tag)
        click.echo(f"Tag '{tag}' added to '{vault_name}'.")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_group.command("remove")
@click.argument("vault_name")
@click.argument("tag")
@click.option("--tag-file", default=str(DEFAULT_TAG_FILE), show_default=True)
def remove_tag_cmd(vault_name: str, tag: str, tag_file: str) -> None:
    """Remove TAG from VAULT_NAME."""
    manager = TagManager(Path(tag_file))
    try:
        manager.remove_tag(vault_name, tag)
        click.echo(f"Tag '{tag}' removed from '{vault_name}'.")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_group.command("list")
@click.argument("vault_name")
@click.option("--tag-file", default=str(DEFAULT_TAG_FILE), show_default=True)
def list_tags_cmd(vault_name: str, tag_file: str) -> None:
    """List all tags for VAULT_NAME."""
    manager = TagManager(Path(tag_file))
    tags = manager.list_tags(vault_name)
    if not tags:
        click.echo(f"No tags for '{vault_name}'.")
    else:
        for tag in tags:
            click.echo(f"  {tag}")


@tag_group.command("find")
@click.argument("tag")
@click.option("--tag-file", default=str(DEFAULT_TAG_FILE), show_default=True)
def find_by_tag_cmd(tag: str, tag_file: str) -> None:
    """Find all vaults with TAG."""
    manager = TagManager(Path(tag_file))
    vaults = manager.find_by_tag(tag)
    if not vaults:
        click.echo(f"No vaults found with tag '{tag}'.")
    else:
        for name in vaults:
            click.echo(f"  {name}")
