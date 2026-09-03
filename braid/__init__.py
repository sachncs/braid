"""braid: a polymorphic LLM-backed recommendation ranker.

Braiding signals into ranks.

This top-level package exposes the registry, the polymorphic primitives,
and the CLI entry points used by the `braid` command.
"""

from braid.core.registry import registry
from braid.core.capability import capability
from braid.core.trait import asyncable, cachable, distributable, idempotent, observable, persistable, streamable, teachable
from braid.core.lifecycle import healthstatus, lifecycle
from braid.core.context import requestcontext
from braid.core.error import braiderror, configurationerror, registryerror
from braid.core.transform import pipeline, transform

__version__ = "0.1.0"
__all__ = [
    "registry",
    "capability",
    "streamable",
    "cachable",
    "persistable",
    "observable",
    "idempotent",
    "asyncable",
    "distributable",
    "teachable",
    "lifecycle",
    "healthstatus",
    "requestcontext",
    "braiderror",
    "configurationerror",
    "registryerror",
    "transform",
    "pipeline",
    "__version__",
]
