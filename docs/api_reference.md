# API reference

This is a hand-curated reference for the most-used entry points. The
full reference is the union of the per-concrete docstrings under
`braid/<area>/<category>/<concrete>.py` — read those directly for the
authoritative interface contracts.

Run `python -c "import braid; help(braid.<module>)"` for any module's
docstring. Run `make list` (or `python -m braid list`) for the live
registry of every concrete.

## Top-level

- `braid.registry` — polymorphic registry (44 categories, 147 concretes as of this writing).
- `braid.testing.scaledown` — config down-scaling for tests.
- `braid.testing.tinytokenizer` — hermetic tokenizer for conformance tests.

## core/

- `braid.core.registry.registry` — `register`, `create`, `resolve`, `available`, `findwithcap`.
- `braid.core.error.braiderror` — typed error model.
- `braid.core.trait.{streamable,cachable,persistable,observable,idempotent,distributable,asyncable,teachable,circuitbreaker}`.
- `braid.core.lifecycle.{lifecycle,lifecycledelegate,healthstatus}`.
- `braid.core.capability.{capability,capable,BUILTIN_CAPABILITIES}`.
- `braid.core.versioning.{versioninfo,configmigrator,noopmigrator,applymigrations}`.
- `braid.core.schema.{schemaregistry,schemaregistryentry,GLOBAL_SCHEMAS,simplemapschema}`.
- `braid.core.observability.{metricdecl,tracedecl,logdecl,observabilityspec,normalize}`.
- `braid.core.context.requestcontext`.
- `braid.core.transform.{transform,pipeline,identity}`.
- `braid.core.serialize.{polyserialize,jsonserialize,yamlserialize}`.
- `braid.core.visitor.{metricvisitor,htmlreporter,jsonreporter,csvreporter,mdreporter}`.
- `braid.core.conformance.{conformancecheck,verifyone,verifyall,assertconformant}`.
- `braid.core.logging.{configure,getlogger}`.
- `braid.core.seed.seedall`.
- `braid.core.io.{atomicwrite,checksum,ensurechecksum,readlazy}`.
- `braid.core.cli.main`.

## Per-category

See the per-module docstrings in `braid/<area>/<category>/<concrete>.py`.
