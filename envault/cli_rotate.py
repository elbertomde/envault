"""CLI commands for vault password rotation."""

import click
from pathlib import Path

from .rotate import rotate_password, RotateError
from .audit import AuditLog


@click.group("rotate")
def rotate_group() -> None:
    """Rotate the master password for a vault."""


@rotate_group.command("run")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current vault password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
@click.option(
    "--audit-log",
    "audit_log_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional path to an audit log file.",
)
def rotate_cmd(
    vault_file: Path,
    old_password: str,
    new_password: str,
    audit_log_path: Path | None,
) -> None:
    """Rotate the master password of VAULT_FILE."""
    audit_log = AuditLog(audit_log_path) if audit_log_path else None

    try:
        rotate_password(vault_file, old_password, new_password, audit_log)
        click.echo(f"Password rotated successfully for {vault_file}.")
    except RotateError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
