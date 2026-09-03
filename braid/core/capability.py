"""Capability declarations and capability-based selection.

A concrete declares its capabilities as a class attribute::

    @registry.register(category="catalogstore", name="matmulinmem")
    class matmulinmem:
        capabilities: frozenset[str] = frozenset({"gpu", "async", "fusedkernel"})

The registry then supports capability queries.
"""

from __future__ import annotations

from dataclasses import dataclass


class capability:
    """Marker for a capability declaration on a concrete class."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"capability({self.name!r})"


@dataclass(frozen=True)
class capable:
    """Concrete+capabilities tuple returned by capability-based lookup.

    Attributes:
        category: registry category.
        name: registry name.
        capabilities: full set of declared capabilities for this concrete.
    """

    category: str
    name: str
    capabilities: frozenset[str]

    def has(self, *caps: str) -> bool:
        return all(c in self.capabilities for c in caps)


BUILTIN_CAPABILITIES: dict[str, str] = {
    "gpu": "Executes on CUDA devices.",
    "async": "Has async public-method variants.",
    "fusedkernel": "Uses fused custom kernels (e.g., FlashAttention).",
    "int4quantize": "Supports INT4 quantized weights.",
    "int8quantize": "Supports INT8 quantized weights.",
    "streamable": "Produces a stream of values.",
    "cachable": "Has an integrated cache layer.",
    "persistable": "Persists state across restarts.",
    "observable": "Declares observability metadata.",
    "idempotent": "Produces identical output for the same idempotency key.",
    "distributable": "Supports distributed execution across shards.",
    "teachable": "Accepts in-context examples.",
    "shardedcatalog": "Can score catalogs larger than device memory.",
    "prefixcache": "Reuses prefix KV-cache across requests.",
    "speculative": "Supports speculative decoding.",
    "quantizedcatalog": "Loads quantized catalog embeddings.",
    "rotatingemb": "Hot-swappable embedding store.",
    "shadowmode": "Ranks without affecting responses.",
    "banditarmed": "Has built-in exploration arms.",
    "circuitbreaker": "Supports circuit-breaker semantics.",
    "replayable": "Supports exact deterministic replay.",
    "lowlatency": "Optimized for sub-10ms latency.",
}
