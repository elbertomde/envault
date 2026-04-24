"""CLI commands for profile management in envault."""

import click
from envault.profiles import ProfileManager, ProfileError


@click.group("profile")
def profile_group():
    """Manage named environment profiles (e.g. dev, staging, prod)."""


@profile_group.command("list")
@click.option("--vault-dir", default=".", help="Path to the vault directory.")
def list_profiles(vault_dir):
    """List all available profiles."""
    manager = ProfileManager(vault_dir)
    profiles = manager.list_profiles()
    active = manager.get_active()
    if not profiles:
        click.echo("No profiles found. Use 'profile add <name>' to create one.")
        return
    for name in profiles:
        marker = " (active)" if name == active else ""
        click.echo(f"  {name}{marker}")


@profile_group.command("add")
@click.argument("name")
@click.option("--vault-dir", default=".", help="Path to the vault directory.")
def add_profile(name, vault_dir):
    """Add a new profile."""
    manager = ProfileManager(vault_dir)
    try:
        manager.add_profile(name)
        click.echo(f"Profile '{name}' added.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile_group.command("remove")
@click.argument("name")
@click.option("--vault-dir", default=".", help="Path to the vault directory.")
def remove_profile(name, vault_dir):
    """Remove an existing profile."""
    manager = ProfileManager(vault_dir)
    try:
        manager.remove_profile(name)
        click.echo(f"Profile '{name}' removed.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile_group.command("use")
@click.argument("name")
@click.option("--vault-dir", default=".", help="Path to the vault directory.")
def use_profile(name, vault_dir):
    """Switch to a different profile."""
    manager = ProfileManager(vault_dir)
    try:
        manager.set_active(name)
        vault_file = manager.vault_file_for_profile(name)
        click.echo(f"Switched to profile '{name}' (vault: {vault_file}).")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
