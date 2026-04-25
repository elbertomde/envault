"""CLI commands for team sharing of vault files."""
import click
from pathlib import Path

from envault.share import ShareError, export_shared, import_shared


@click.group(name="share")
def share_group():
    """Share encrypted vaults with teammates."""


@share_group.command(name="export")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option("--password", prompt=True, hide_input=True, help="Your vault password.")
@click.option(
    "--recipient-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password for the recipient.",
)
def export_shared_cmd(vault_file: Path, output_file: Path, password: str, recipient_password: str):
    """Export vault re-encrypted with a recipient password."""
    try:
        export_shared(vault_file, password, recipient_password, output_file)
        click.echo(f"Shared vault exported to {output_file}")
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@share_group.command(name="import")
@click.argument("shared_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--recipient-password",
    prompt=True,
    hide_input=True,
    help="Password you received from the sender.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Your new local vault password.",
)
def import_shared_cmd(shared_file: Path, output_file: Path, recipient_password: str, new_password: str):
    """Import a shared vault and re-encrypt it with your own password."""
    try:
        meta = import_shared(shared_file, recipient_password, output_file, new_password)
        source = meta.get("source", "unknown")
        click.echo(f"Vault imported from '{source}' → {output_file}")
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
