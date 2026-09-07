"""Polymorphic schema registry with versioning and migration.

Schemas are registered as ``schemaregistryentry`` instances. Built-in
schemas cover items, events, contexts, prompts, requests, responses, and
metrics. External packages can register their own via ``registry.register``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class schemaregistryentry(Protocol):
    """A single schema entry: name, version, validator, migrator."""

    name: str
    version: str

    def validate(self, value: Any) -> Any: ...

    def migrate(self, raw: dict[str, Any], targetversion: str) -> dict[str, Any]: ...


@dataclass
class schemaregistry:
    """In-memory registry of ``schemaregistryentry`` instances."""

    entries: dict[tuple[str, str], schemaregistryentry] = field(default_factory=dict)

    def register(self, entry: schemaregistryentry) -> None:
        """Register a schema entry under ``(name, version)``.

        Args:
            entry: the schema entry.
        """
        self.entries[(entry.name, entry.version)] = entry

    def resolve(self, name: str, version: str) -> schemaregistryentry:
        """Return the entry for ``(name, version)`` or raise ``configurationerror``."""
        from braid.core.error import configurationerror

        entry = self.entries.get((name, version))
        if entry is None:
            available = sorted({v for n, v in self.entries if n == name})
            raise configurationerror(
                f"no schema registered for {name!r} v{version!r}",
                available=available,
                hint="check schema versions",
            )
        return entry

    def validate(self, name: str, value: Any, *, version: str = "1.0.0") -> Any:
        """Validate ``value`` against the registered schema.

        Args:
            name: schema name.
            value: candidate value.
            version: schema version. Defaults to ``"1.0.0"``.

        Returns:
            The validated (possibly normalized) value.
        """
        return self.resolve(name, version).validate(value)

    def migrate(self, name: str, raw: dict[str, Any], target: str) -> dict[str, Any]:
        """Walk versions forward to ``target``.

        Args:
            name: schema name.
            raw: dict-form value.
            target: target version.

        Returns:
            Migrated dict.
        """
        fromversion = raw.get("__schema_version__", "1.0.0")
        versions = sorted(
            {v for n, v in self.entries if n == name},
            key=lambda v: tuple(int(p) for p in v.split(".")),
        )
        for v in versions:
            if v < fromversion:
                continue
            if v > target:
                break
            entry = self.resolve(name, v)
            raw = entry.migrate(raw, target)
        raw["__schema_version__"] = target
        return raw


GLOBAL_SCHEMAS: schemaregistry = schemaregistry()


@dataclass
class simplemapschema:
    """Minimal schema entry backed by ``dict`` with optional version string."""

    name: str
    version: str

    def validate(self, value: Any) -> Any:
        """Identity validator; concrete schemas override.

        Args:
            value: candidate.

        Returns:
            The value unchanged.
        """
        if not isinstance(value, dict):
            from braid.core.error import validationerror

            raise validationerror(f"{self.name} expects dict, got {type(value).__name__}")
        value["__schema_version__"] = self.version
        return value

    def migrate(self, raw: dict[str, Any], targetversion: str) -> dict[str, Any]:
        """Identity migrator.

        Args:
            raw: dict-form value.
            targetversion: target version string.

        Returns:
            The dict unchanged.
        """
        raw["__schema_version__"] = targetversion
        return raw


GLOBAL_SCHEMAS.register(simplemapschema("item", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("item", "2.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("event", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("event", "2.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("context", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("prompt", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("rankrequest", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("rankresponse", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("metric", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("report", "1.0.0"))
GLOBAL_SCHEMAS.register(simplemapschema("artifact", "1.0.0"))
