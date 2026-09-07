# Extension guide: adding new concretes

This guide shows how to add a new concrete to any existing category in
`braid`. The convention is **one concrete = one file = one class** with a
class docstring, a `name`, `version`, `capabilities`, and a registry
registration.

## Pattern

```python
# braid/<area>/<category>/<concrete>.py

"""One-line summary.

Extended description.

Attributes:
    someattr: what it is.

Invariants:
    someinvariant: a stability property.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="<category>", name="<concrete>")
class <concrete>:
    """Class docstring (numpy-style)."""

    name: str = "<concrete>"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "<other caps>"})

    def __init__(self, ...) -> None:
        """Constructor docstring."""
        ...

    def <method>(self, ...) -> ...:
        """Method docstring."""
        ...

    def observability(self) -> dict[str, Any]:
        """Return declared observability."""
        return {"metrics": [...]}

    def metrics(self) -> list[Any]:
        """Return runtime metric sinks (optional)."""
        return []
```

## Where concretes live

| Category | Path |
|---|---|
| datasource | `braid/datasource/<concrete>.py` |
| loss | `braid/loss/<concrete>.py` |
| backbone | `braid/backbone/<concrete>.py` |
| catalogstore | `braid/catalogstore/<concrete>.py` |
| (etc.) | |

## Adding a new category

```python
# braid/newcat/protocol.py
class newcat(Protocol):
    def domything(self) -> Any: ...

# braid/newcat/myimpl.py
@registry.register(category="newcat", name="myimpl")
class myimpl:
    ...
    def domything(self): ...

# braid/newcat/__init__.py
from braid.newcat.protocol import newcat
from braid.newcat.myimpl import myimpl
```

Then add `newcat` to `braid/__init__.py`'s eager imports list.

## Adding a new composite

A composite consumes a list of registered concretes of the same category
via the `braid.core.registry.create()` API.

```python
@registry.register(category="loss", name="mybraid")
class mybraid:
    def __init__(self, terms: list[tuple[str, float]] = ...): ...
    def compute(self, outputs, batch):
        loss = 0
        for n, w in self.terms:
            term = registry.create("loss", n)
            loss = loss + w * term.compute(outputs, batch)
        return loss
```

## Registration outside the package (entry points)

External packages can register concretes via Python entry points:

```toml
[project.entry-points."braid.loss"]
mynewloss = "mypkg.loss:mynewloss"
```

The registry picks these up automatically.

## Versioning

Concrete `version` is a semantic version. Configs declare a minimum
required version via `minconfigversion`. Migrators registered under
`migrator` perform in-place config upgrades between versions.

## Conventions

- One word per identifier. Don't write `matmul_inmem`; write `matmulinmem`.
- Numpy-style docstrings. No `_` prefixes; internals use full names.
- Mandatory: `name`, `version`, `capabilities`, `__init__`, `observability`, `metrics()`.
- Add `idempotencykey()` if you declare `idempotent` capability.
- Add `cacheget`/`cacheput`/`cacheinvalidate` if you declare `cachable` capability.
- Add `persist`/`restore` if you declare `persistable` capability.
- Add `shardrank`/`numshards` if you declare `distributable` capability.
