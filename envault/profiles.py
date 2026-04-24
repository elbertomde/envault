"""Profile management for envault — supports multiple named environments (dev, staging, prod)."""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_PROFILE = "default"
PROFILES_FILE = ".envault_profiles.json"


class ProfileError(Exception):
    """Raised when a profile operation fails."""


class ProfileManager:
    """Manages named profiles for a vault directory."""

    def __init__(self, vault_dir: str = "."):
        self.vault_dir = Path(vault_dir)
        self.profiles_path = self.vault_dir / PROFILES_FILE

    def _load(self) -> dict:
        if not self.profiles_path.exists():
            return {"active": DEFAULT_PROFILE, "profiles": []}
        with open(self.profiles_path, "r") as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        with open(self.profiles_path, "w") as f:
            json.dump(data, f, indent=2)

    def list_profiles(self) -> list[str]:
        """Return all registered profile names."""
        return self._load().get("profiles", [])

    def add_profile(self, name: str) -> None:
        """Register a new profile name."""
        data = self._load()
        if name in data["profiles"]:
            raise ProfileError(f"Profile '{name}' already exists.")
        data["profiles"].append(name)
        self._save(data)

    def remove_profile(self, name: str) -> None:
        """Remove a profile by name."""
        data = self._load()
        if name not in data["profiles"]:
            raise ProfileError(f"Profile '{name}' does not exist.")
        if data["active"] == name:
            raise ProfileError(f"Cannot remove active profile '{name}'.")
        data["profiles"].remove(name)
        self._save(data)

    def get_active(self) -> str:
        """Return the currently active profile name."""
        return self._load().get("active", DEFAULT_PROFILE)

    def set_active(self, name: str) -> None:
        """Switch the active profile."""
        data = self._load()
        if name not in data["profiles"]:
            raise ProfileError(f"Profile '{name}' does not exist. Add it first.")
        data["active"] = name
        self._save(data)

    def vault_file_for_profile(self, profile: Optional[str] = None) -> str:
        """Return the vault filename associated with a profile."""
        profile = profile or self.get_active()
        if profile == DEFAULT_PROFILE:
            return ".envault"
        return f".envault.{profile}"
