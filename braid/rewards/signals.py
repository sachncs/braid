"""Shared reward signal definitions and registry."""

from __future__ import annotations


from braid.core.registry import registry


REWARD_REGISTRY: dict[str, type] = {}


def register(name: str):
    """Decorator that registers a reward class under ``name``."""

    def deco(klass):
        REWARD_REGISTRY[name] = klass
        registry.register(category="reward", name=name)(klass)
        return klass

    return deco
