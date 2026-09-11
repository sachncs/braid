"""Polymorphic registry for braid concretes.

Every concrete in every category registers itself with the registry and is
resolvable by ``registry.create(category, name, **kwargs)``. Built-in
concretes are registered as a side-effect of importing the package; plugins
register via Python entry points (see ``pyproject.toml``).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Iterator


class registry:
    """Static registry. Categories dispatch by name to concrete classes.

    Example:
        >>> @registry.register(category="catalogstore", name="matmulinmem")
        ... class matmulinmem:
        ...     pass
        >>> registry.available("catalogstore")
        ['matmulinmem']
        >>> store = registry.create("catalogstore", "matmulinmem", embeddings=...)
    """

    _items: dict[str, dict[str, type]] = defaultdict(dict)
    _aliases: dict[tuple[str, str], str] = {}
    _factories: dict[tuple[str, str], Callable[..., Any]] = {}

    @classmethod
    def register(
        cls,
        *,
        category: str,
        name: str,
        version: str = "1.0.0",
        aliases: tuple[str, ...] | None = None,
    ) -> Callable[[type], type]:
        """Class decorator registering a concrete under ``(category, name)``.

        Args:
            category: the polymorphic category (e.g., ``"catalogstore"``).
            name: the registry-friendly name (e.g., ``"matmulinmem"``).
            version: semantic version of this concrete.
            aliases: alternative names that resolve to the same concrete.

        Returns:
            The class unchanged, with side effects in the registry.

        Example:
            >>> @registry.register(category="loss", name="rankingce")
            ... class rankingce:
            ...     pass
        """

        def deco(klass: type) -> type:
            cls._items[category][name] = klass
            klass._registry_category = category  # type: ignore[attr-defined]
            klass._registry_name = name  # type: ignore[attr-defined]
            klass._registry_version = version  # type: ignore[attr-defined]
            if aliases:
                for alias in aliases:
                    cls._aliases[(category, alias)] = name
            return klass

        return deco

    @classmethod
    def registerfactory(
        cls,
        *,
        category: str,
        name: str,
        factory: Callable[..., Any],
    ) -> Callable[..., Any]:
        """Register a factory function rather than a class.

        Useful when construction requires non-trivial setup.
        """
        cls._factories[(category, name)] = factory
        return factory

    @classmethod
    def loadentrypoints(cls, groupprefix: str = "braid.") -> int:
        """Discover and register every concrete declared as a ``braid.*`` entry point.

        Third-party packages may declare additional concretes under
        ``[project.entry-points."braid.<category>"]`` in their ``pyproject.toml``.
        Eager imports run first, so this method either augments the existing
        registration or overrides it with the entry-point class.

        Args:
            groupprefix: only groups starting with this prefix are loaded.

        Returns:
            The number of entry points that were registered.
        """
        from importlib.metadata import entry_points

        loaded = 0
        for ep in entry_points():
            if not ep.group.startswith(groupprefix):
                continue
            category = ep.group[len(groupprefix):]
            try:
                klass = ep.load()
            except Exception:
                continue
            cls._items[category][ep.name] = klass
            klass._registry_category = category  # type: ignore[attr-defined]
            klass._registry_name = ep.name  # type: ignore[attr-defined]
            loaded += 1
        return loaded

    @classmethod
    def create(cls, category: str, name: str, /, **kwargs: Any) -> Any:
        """Resolve a concrete by category+name and instantiate it.

        Args:
            category: the polymorphic category.
            name: the registry name (or alias).
            **kwargs: forwarded to the concrete.

        Returns:
            A new instance of the resolved concrete.

        Raises:
            registryerror: if the name is not registered.

        Example:
            >>> obj = registry.create("loss", "rankingce")
        """
        from braid.core.error import registryerror

        actual = cls._aliases.get((category, name), name)
        if (category, actual) in cls._factories:
            return cls._factories[(category, actual)](**kwargs)
        klass = cls._items.get(category, {}).get(actual)
        if klass is None:
            raise registryerror(
                f"no concrete registered for category={category!r} name={actual!r}",
                available=list(cls._items.get(category, {}).keys()),
            )
        return klass(**kwargs)

    @classmethod
    def resolve(cls, category: str, name: str) -> type:
        """Return the concrete class without instantiating."""
        from braid.core.error import registryerror

        actual = cls._aliases.get((category, name), name)
        klass = cls._items.get(category, {}).get(actual)
        if klass is None:
            raise registryerror(
                f"no concrete registered for category={category!r} name={actual!r}",
                available=list(cls._items.get(category, {}).keys()),
            )
        return klass

    @classmethod
    def available(cls, category: str) -> list[str]:
        """Return all registered names in a category, sorted."""
        return sorted(cls._items.get(category, {}).keys())

    @classmethod
    def categories(cls) -> list[str]:
        """Return all categories with at least one registered concrete."""
        return sorted(cls._items.keys())

    @classmethod
    def capabilities(cls, category: str, name: str) -> frozenset[str]:
        """Return the declared capabilities for a concrete."""
        klass = cls.resolve(category, name)
        caps = getattr(klass, "capabilities", frozenset())
        return frozenset(caps)

    @classmethod
    def findwithcap(cls, capabilityname: str) -> list[tuple[str, str]]:
        """Find all concretes across all categories that declare a capability."""
        results: list[tuple[str, str]] = []
        for category, items in cls._items.items():
            for name, klass in items.items():
                caps = getattr(klass, "capabilities", frozenset())
                if capabilityname in caps:
                    results.append((category, name))
        return sorted(results)

    @classmethod
    def items(cls) -> Iterator[tuple[str, str, type]]:
        """Yield all registered (category, name, klass) triples."""
        for category, items in cls._items.items():
            for name, klass in items.items():
                yield category, name, klass

    @classmethod
    def clear(cls) -> None:
        """Reset the registry (used by tests)."""
        cls._items.clear()
        cls._aliases.clear()
        cls._factories.clear()
