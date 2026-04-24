"""CLI commands for the envault audit log."""

from __future__ import annotations

from pathlib import Path

import click

from envault.audit import AUDIT_LOG_FILENAME, AuditError, AuditLog


@click.group(name="audit")
def audit_group() -> None:
    """Manage the vault audit log."""


@audit_group.command(name="list")
@click.option("--log", default=AUDIT_LOG_FILENAME, show_default=True, help="Path to audit log file.")
def list_audit(log: str) -> None:
    """List all recorded audit log entries."""
    try:
        audit = AuditLog(Path(log))
        entries = audit.entries()
    except AuditError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not entries:
        click.echo("No audit entries found.")
        return

    for entry in entries:
        details = f" — {entry['details']}" if entry["details"] else ""
        click.echo(f"[{entry['timestamp']}] {entry['user']}: {entry['action']}{details}")


@audit_group.command(name="clear")
@click.option("--log", default=AUDIT_LOG_FILENAME, show_default=True, help="Path to audit log file.")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_audit(log: str) -> None:
    """Clear all audit log entries."""
    try:
        audit = AuditLog(Path(log))
        audit.clear()
        click.echo("Audit log cleared.")
    except AuditError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
