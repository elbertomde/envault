"""Tests for envault profile management."""

import json
import pytest
from pathlib import Path

from envault.profiles import ProfileManager, ProfileError, DEFAULT_PROFILE


@pytest.fixture
def manager(tmp_path):
    return ProfileManager(vault_dir=str(tmp_path))


def test_list_profiles_empty(manager):
    assert manager.list_profiles() == []


def test_add_profile(manager):
    manager.add_profile("staging")
    assert "staging" in manager.list_profiles()


def test_add_duplicate_profile_raises(manager):
    manager.add_profile("staging")
    with pytest.raises(ProfileError, match="already exists"):
        manager.add_profile("staging")


def test_remove_profile(manager):
    manager.add_profile("staging")
    manager.remove_profile("staging")
    assert "staging" not in manager.list_profiles()


def test_remove_nonexistent_profile_raises(manager):
    with pytest.raises(ProfileError, match="does not exist"):
        manager.remove_profile("ghost")


def test_remove_active_profile_raises(manager):
    manager.add_profile("prod")
    manager.set_active("prod")
    with pytest.raises(ProfileError, match="Cannot remove active"):
        manager.remove_profile("prod")


def test_default_active_profile(manager):
    assert manager.get_active() == DEFAULT_PROFILE


def test_set_active_profile(manager):
    manager.add_profile("dev")
    manager.set_active("dev")
    assert manager.get_active() == "dev"


def test_set_active_nonexistent_raises(manager):
    with pytest.raises(ProfileError, match="does not exist"):
        manager.set_active("unknown")


def test_vault_file_for_default_profile(manager):
    assert manager.vault_file_for_profile(DEFAULT_PROFILE) == ".envault"


def test_vault_file_for_named_profile(manager):
    manager.add_profile("production")
    assert manager.vault_file_for_profile("production") == ".envault.production"


def test_vault_file_uses_active_profile(manager):
    manager.add_profile("staging")
    manager.set_active("staging")
    assert manager.vault_file_for_profile() == ".envault.staging"


def test_profiles_persisted_to_disk(manager, tmp_path):
    manager.add_profile("ci")
    profiles_file = tmp_path / ".envault_profiles.json"
    assert profiles_file.exists()
    data = json.loads(profiles_file.read_text())
    assert "ci" in data["profiles"]


def test_active_profile_persisted_to_disk(manager, tmp_path):
    """Verify that the active profile is saved to disk after set_active."""
    manager.add_profile("staging")
    manager.set_active("staging")
    profiles_file = tmp_path / ".envault_profiles.json"
    data = json.loads(profiles_file.read_text())
    assert data["active"] == "staging"


def test_manager_reloads_state_from_disk(tmp_path):
    """Verify that a new ProfileManager instance reads persisted state correctly."""
    manager1 = ProfileManager(vault_dir=str(tmp_path))
    manager1.add_profile("dev")
    manager1.set_active("dev")

    manager2 = ProfileManager(vault_dir=str(tmp_path))
    assert "dev" in manager2.list_profiles()
    assert manager2.get_active() == "dev"
