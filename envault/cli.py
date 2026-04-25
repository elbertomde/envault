"""Entry point for the envault CLI."""

import click

from .cli_profiles import profile_group
from .cli_export import export_group
from .cli_audit import audit_group
from .cli_rotate import rotate_group


@click.group()
@click.version_option()
def cli() -> None:
    """envault — encrypted environment variable manager."""


cli.add_command(profile_group)
cli.add_command(export_group)
cli.add_command(audit_group)
cli.add_command(rotate_group)


if __name__ == "__main__":
    cli()
