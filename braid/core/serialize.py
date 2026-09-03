"""Polymorphic serialization across json, yaml, msgpack, arrow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class polyserialize(Protocol):
    """Polymorphic serializer.

    Implementations: ``jsonserialize``, ``yamlserialize``, ``msgpackserialize``, ``arrowserialize``.
    """

    name: str

    def tobytes(self, value: Any) -> bytes: ...
    def frombytes(self, raw: bytes) -> Any: ...


@dataclass
class jsonserialize:
    """JSON serializer with byte-array preservation."""

    name: str = "json"

    def tobytes(self, value: Any) -> bytes:
        """Encode ``value`` as JSON bytes.

        Args:
            value: any JSON-serializable structure.

        Returns:
            UTF-8 encoded JSON bytes.
        """
        return json.dumps(value, default=str).encode("utf-8")

    def frombytes(self, raw: bytes) -> Any:
        """Decode JSON bytes.

        Args:
            raw: UTF-8 encoded JSON.

        Returns:
            The decoded Python value.
        """
        return json.loads(raw.decode("utf-8"))


@dataclass
class yamlserialize:
    """YAML serializer."""

    name: str = "yaml"

    def tobytes(self, value: Any) -> bytes:
        try:
            import yaml
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("PyYAML required for yamlserialize") from exc
        return yaml.safe_dump(value, default_flow_style=False).encode("utf-8")

    def frombytes(self, raw: bytes) -> Any:
        try:
            import yaml
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("PyYAML required for yamlserialize") from exc
        return yaml.safe_load(raw.decode("utf-8"))
