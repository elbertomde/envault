"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.cli_audit import audit_group
from envault.cli_export import export_group
from envault.cli_profiles import profile_group


@click.group()
@click.version_option(prog_name="envault")
def cli() -> None:
    """envault — Manage and encrypt environment variable files."""


cli.add_command(profile_group)
cli.add_command(export_group)
cli.add_command(audit_group)


if __name__ == "__main__":
    cli()
