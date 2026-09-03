"""Core polymorphic infrastructure for braid.

Modules:
    registry:     registry and category dispatch.
    types:        shared type aliases and vars.
    error:        typed error model with retry classification.
    capability:   capability declaration on concretes.
    trait:        composable mixin Protocols.
    lifecycle:    setup/warmup/shutdown/health contract.
    versioning:   configmigrator and version resolution.
    schema:       schemaregistry for versioned value objects.
    observability:declared metrics, traces, and logs.
    context:      requestcontext propagation.
    transform:    composable pipeline of typed transforms.
    serialize:    polymorphic serialization.
    visitor:      metricvisitor for report emissions.
    conformance:  runtime conformance verification.
    logging:      structlog bootstrap.
    seed:         deterministic seeding.
    io:           atomic filesystem helpers.
    cli:          `braid` command entry points.
"""

from braid.core.registry import registry
from braid.core.error import braiderror, configurationerror, registryerror
from braid.core.capability import capability, capable
from braid.core.trait import (
    asyncable,
    cachable,
    distributable,
    idempotent,
    observable,
    persistable,
    streamable,
    teachable,
)
from braid.core.lifecycle import healthstatus, lifecycle
from braid.core.versioning import configmigrator, versioninfo
from braid.core.schema import schemaregistry, schemaregistryentry
from braid.core.observability import logdecl, metricdecl, tracedecl
from braid.core.context import requestcontext
from braid.core.transform import pipeline, transform
from braid.core.serialize import polyserialize
from braid.core.visitor import metricvisitor
from braid.core.conformance import conformancecheck, contractfail

__all__ = [
    "registry",
    "braiderror",
    "configurationerror",
    "registryerror",
    "capability",
    "capable",
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
    "configmigrator",
    "versioninfo",
    "schemaregistry",
    "schemaregistryentry",
    "metricdecl",
    "tracedecl",
    "logdecl",
    "requestcontext",
    "transform",
    "pipeline",
    "polyserialize",
    "metricvisitor",
    "conformancecheck",
    "contractfail",
]
