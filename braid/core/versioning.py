"""Versioning of concretes and polymorphic config migrators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from braid.core.registry import registry


@dataclass(frozen=True)
class versioninfo:
    """Semantic version info for a concrete or config schema."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, raw: str) -> "versioninfo":
        parts = raw.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "versioninfo") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: "versioninfo") -> bool:
        return self < other or self == other


@runtime_checkable
class configmigrator(Protocol):
    """Polymorphic config migrator: transforms an old-version config to new-version."""

    fromversion: str
    toversion: str

    def migrate(self, raw: dict[str, Any]) -> dict[str, Any]: ...


@registry.register(category="migrator", name="noopmigrator")
class noopmigrator:
    """A migrator that returns the config unchanged.

    Useful as a base case for testing migration chains.
    """

    fromversion = "0.0.0"
    toversion = "0.0.0"

    def migrate(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Return the config dict unchanged.

        Args:
            raw: the config dict.

        Returns:
            The same dict (no migration applied).
        """
        return raw


def applymigrations(
    raw: dict[str, Any],
    category: str,
    targetname: str,
    *,
    fromversion: str = "0.0.0",
) -> dict[str, Any]:
    """Apply registered migrators in version order to reach ``targetname``'s version.

    Args:
        raw: source config dict.
        category: the registry category.
        targetname: registry name of the target concrete.
        fromversion: starting version.

    Returns:
        Migrated config dict.
    """
    klass = registry.resolve(category, targetname)
    target = str(getattr(klass, "_registry_version", "1.0.0"))
    available = registry.available("migrator")
    for name in available:
        if (category, name) not in registry._items.get("migrator", {}):
            continue
        mig: configmigrator = registry.create("migrator", name)
        if not (versioninfo.parse(mig.fromversion) >= versioninfo.parse(fromversion)
                and versioninfo.parse(mig.toversion) <= versioninfo.parse(target)):
            continue
        raw = mig.migrate(raw)
    return raw
