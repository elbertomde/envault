"""Integration tests for the profile CLI commands."""

import pytest
from click.testing import CliRunner
from envault.cli_profiles import profile_group


@pytest.fixture
def runner():
    return CliRunner()


def test_list_profiles_empty(runner, tmp_path):
    result = runner.invoke(profile_group, ["list", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_add_profile(runner, tmp_path):
    result = runner.invoke(profile_group, ["add", "staging", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_duplicate_profile_fails(runner, tmp_path):
    runner.invoke(profile_group, ["add", "staging", "--vault-dir", str(tmp_path)])
    result = runner.invoke(profile_group, ["add", "staging", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_list_shows_added_profile(runner, tmp_path):
    runner.invoke(profile_group, ["add", "dev", "--vault-dir", str(tmp_path)])
    result = runner.invoke(profile_group, ["list", "--vault-dir", str(tmp_path)])
    assert "dev" in result.output


def test_use_profile(runner, tmp_path):
    runner.invoke(profile_group, ["add", "prod", "--vault-dir", str(tmp_path)])
    result = runner.invoke(profile_group, ["use", "prod", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert ".envault.prod" in result.output


def test_use_nonexistent_profile_fails(runner, tmp_path):
    result = runner.invoke(profile_group, ["use", "ghost", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_remove_profile(runner, tmp_path):
    runner.invoke(profile_group, ["add", "staging", "--vault-dir", str(tmp_path)])
    result = runner.invoke(profile_group, ["remove", "staging", "--vault-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_active_profile_marked_in_list(runner, tmp_path):
    runner.invoke(profile_group, ["add", "dev", "--vault-dir", str(tmp_path)])
    runner.invoke(profile_group, ["use", "dev", "--vault-dir", str(tmp_path)])
    result = runner.invoke(profile_group, ["list", "--vault-dir", str(tmp_path)])
    assert "(active)" in result.output
