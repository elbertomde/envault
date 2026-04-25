"""Main CLI entry point for envault."""
import click

from envault.cli_profiles import profile_group
from envault.cli_export import export_group
from envault.cli_audit import audit_group
from envault.cli_rotate import rotate_group
from envault.cli_diff import diff_group
from envault.cli_share import share_group


@click.group()
@click.version_option()
def cli():
    """envault — manage and encrypt environment variable files."""


cli.add_command(profile_group)
cli.add_command(export_group)
cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(diff_group)
cli.add_command(share_group)
