"""Tests for envault.tags module."""

from __future__ import annotations

import pytest

from envault.tags import TagError, TagManager


@pytest.fixture
def manager(tmp_path):
    return TagManager(tmp_path / "tags.json")


def test_new_manager_has_no_tags(manager):
    assert manager.all_tags() == {}


def test_add_tag(manager):
    manager.add_tag("production", "critical")
    assert "critical" in manager.list_tags("production")


def test_add_duplicate_tag_raises(manager):
    manager.add_tag("production", "critical")
    with pytest.raises(TagError, match="already exists"):
        manager.add_tag("production", "critical")


def test_remove_tag(manager):
    manager.add_tag("staging", "infra")
    manager.remove_tag("staging", "infra")
    assert manager.list_tags("staging") == []


def test_remove_nonexistent_tag_raises(manager):
    with pytest.raises(TagError, match="not found"):
        manager.remove_tag("staging", "ghost")


def test_list_tags_empty_for_unknown_vault(manager):
    assert manager.list_tags("unknown") == []


def test_find_by_tag_returns_matching_vaults(manager):
    manager.add_tag("prod", "live")
    manager.add_tag("staging", "live")
    manager.add_tag("dev", "local")
    result = manager.find_by_tag("live")
    assert set(result) == {"prod", "staging"}


def test_find_by_tag_no_matches(manager):
    assert manager.find_by_tag("nonexistent") == []


def test_tags_persist_to_disk(tmp_path):
    path = tmp_path / "tags.json"
    m1 = TagManager(path)
    m1.add_tag("vault_a", "team-alpha")
    m2 = TagManager(path)
    assert "team-alpha" in m2.list_tags("vault_a")


def test_remove_last_tag_cleans_up_vault_entry(manager):
    manager.add_tag("solo", "only")
    manager.remove_tag("solo", "only")
    assert "solo" not in manager.all_tags()


def test_multiple_tags_per_vault(manager):
    for tag in ("web", "backend", "prod"):
        manager.add_tag("api", tag)
    assert set(manager.list_tags("api")) == {"web", "backend", "prod"}
