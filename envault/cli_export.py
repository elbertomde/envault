"""CLI commands for exporting and importing vault files."""

import click

from envault.export import ExportError, export_env, import_env


@click.group(name="export")
def export_group() -> None:
    """Export and import vault contents."""


@export_group.command("env")
@click.argument("vault_path")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option("--output", "-o", default=None, help="Output .env file path (default: .env).")
def export_env_cmd(vault_path: str, password: str, output: str) -> None:
    """Decrypt VAULT_PATH and write a plain .env file."""
    try:
        dest = export_env(vault_path, password, output)
        click.echo(f"Exported to {dest}")
    except ExportError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@export_group.command("import")
@click.argument("env_path")
@click.option("--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True, help="Vault password.")
@click.option("--output", "-o", default=None, help="Output vault file path (default: <env_path>.vault).")
def import_env_cmd(env_path: str, password: str, output: str) -> None:
    """Encrypt ENV_PATH and write a vault file."""
    try:
        dest = import_env(env_path, password, output)
        click.echo(f"Vault created at {dest}")
    except ExportError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
