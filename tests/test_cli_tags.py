"""Tests for envault.cli_tags CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_tags import tag_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tag_file(tmp_path):
    return str(tmp_path / "tags.json")


def test_add_tag_success(runner, tag_file):
    result = runner.invoke(tag_group, ["add", "prod", "critical", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_duplicate_tag_fails(runner, tag_file):
    runner.invoke(tag_group, ["add", "prod", "critical", "--tag-file", tag_file])
    result = runner.invoke(tag_group, ["add", "prod", "critical", "--tag-file", tag_file])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_remove_tag_success(runner, tag_file):
    runner.invoke(tag_group, ["add", "prod", "critical", "--tag-file", tag_file])
    result = runner.invoke(tag_group, ["remove", "prod", "critical", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_nonexistent_tag_fails(runner, tag_file):
    result = runner.invoke(tag_group, ["remove", "prod", "ghost", "--tag-file", tag_file])
    assert result.exit_code == 1


def test_list_tags_empty(runner, tag_file):
    result = runner.invoke(tag_group, ["list", "prod", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_list_tags_shows_tags(runner, tag_file):
    runner.invoke(tag_group, ["add", "prod", "live", "--tag-file", tag_file])
    result = runner.invoke(tag_group, ["list", "prod", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "live" in result.output


def test_find_by_tag_success(runner, tag_file):
    runner.invoke(tag_group, ["add", "prod", "live", "--tag-file", tag_file])
    runner.invoke(tag_group, ["add", "staging", "live", "--tag-file", tag_file])
    result = runner.invoke(tag_group, ["find", "live", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output


def test_find_by_tag_no_matches(runner, tag_file):
    result = runner.invoke(tag_group, ["find", "unknown", "--tag-file", tag_file])
    assert result.exit_code == 0
    assert "No vaults found" in result.output
