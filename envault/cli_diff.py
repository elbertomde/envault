"""CLI commands for diffing vault files."""

import click

from envault.diff import DiffError, diff_vaults


@click.group(name="diff")
def diff_group() -> None:
    """Compare vault files."""


@diff_group.command(name="vaults")
@click.argument("vault_a", type=click.Path(exists=True))
@click.argument("vault_b", type=click.Path(exists=True))
@click.option(
    "--password-a",
    prompt="Password for vault A",
    hide_input=True,
    help="Password to unlock vault A.",
)
@click.option(
    "--password-b",
    prompt="Password for vault B",
    hide_input=True,
    help="Password to unlock vault B.",
)
@click.option("--show-unchanged", is_flag=True, default=False, help="Include unchanged keys.")
def diff_vaults_cmd(
    vault_a: str,
    vault_b: str,
    password_a: str,
    password_b: str,
    show_unchanged: bool,
) -> None:
    """Diff two vault files and display changes."""
    try:
        entries = diff_vaults(vault_a, password_a, vault_b, password_b)
    except DiffError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    _print_diff(entries, show_unchanged)


def _print_diff(entries, show_unchanged: bool) -> None:
    status_symbols = {
        "added": (click.style("+", fg="green"), "green"),
        "removed": (click.style("-", fg="red"), "red"),
        "changed": (click.style("~", fg="yellow"), "yellow"),
        "unchanged": (" ", None),
    }

    shown = 0
    for entry in entries:
        if entry.status == "unchanged" and not show_unchanged:
            continue
        symbol, color = status_symbols[entry.status]
        if entry.status == "changed":
            line = f"{symbol} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}"
        elif entry.status == "added":
            line = f"{symbol} {entry.key}={entry.new_value!r}"
        elif entry.status == "removed":
            line = f"{symbol} {entry.key}={entry.old_value!r}"
        else:
            line = f"{symbol} {entry.key}={entry.old_value!r}"
        click.echo(click.style(line, fg=color) if color else line)
        shown += 1

    if shown == 0:
        click.echo("No differences found.")
