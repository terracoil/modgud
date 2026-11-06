**Parent**: [📋 ADR Index](README.md) | [📖 ADR-004](ADR-004-public-facade-and-api-tiers.md) | [📚 Documentation Hub](../ADVANCED.md)

# ADR-005: Idunn Ports and Adapters

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2026-11-02)

> **Update 2026-11-05.** Idunn 2.0 added `@Invert(bootstrap=...)`. The `Wiring` composition root and the decorators' `__new__` hooks are gone; the decision below describes the wiring as it now stands.

> **Update 2026-11-06.** The ports now live in `modgud.domain.ports`. The `modgud.domain.<feature>.ports` path below predates the flattening of `modgud.domain` (see ADR-004).

> **Update 2026-11-06 (later).** The seam parameters are now `guard_port=` / `imp_return_port=` (formerly `runtime=` / `transformer=`), and each port exposes a single `transform` entry point that the decorator delegates to wholesale: descriptor handling, the markers and the stacking check moved from `modgud.app` into the adapters, and `MethodDescriptors` moved to `modgud.infrastructure.internal`. `GuardAdapter.wrap_function` survives as the adapter's guard-only step, no longer on the port.

## Context
The decorators used to import `GuardAdapter` and `ImplicitReturnAdapter` directly. Tests that wanted a fake runtime had to monkeypatch a module attribute, and the "app never imports infrastructure" rule was a comment rather than a fact. A library whose whole pitch is discipline at function boundaries was wiring its own internals by hand.

## Decision
Ports and adapters, wired by [Idunn](https://pypi.org/project/idunn):

- `GuardPort` and `ImplicitReturnPort` are `@Port` Protocols in `modgud.domain.<feature>.ports`. The decorators depend on them only.
- `GuardAdapter` and `ImplicitReturnAdapter` subclass their port as `@Adapter(..., lifecycle=SINGLETON)` in `modgud.infrastructure.adapters`.
- `@Invert(bootstrap='modgud')` on each decorator's `__init__` runs `Idunn().bootstrap('modgud')` on the first decoration that leaves a port to injection, not at import, then injects `runtime` / `transformer`. A caller-supplied value wins, and a decoration that supplies every port discovers nothing.
- Idunn imports are fenced: `Invert` in `app`, `Adapter` / `LifecycleEnum` in `adapters`, `Port` in `ports` modules. `Idunn` is constructed nowhere under `modgud/`. `tests/test_architecture.py` enforces the fence.

## Consequences

### Positive
- The test seam is a parameter: pass `runtime=` or `transformer=` and no monkeypatching is needed.
- The layering rule is a test, not a comment.
- Idunn environments (`IDUNN_ENV`) exist, but modgud ships one adapter per port and does not test process-wide replacement; the supported seam is the per-decoration parameter.

### Negative
- One runtime dependency, after a long stretch of none. `import modgud` imports `idunn`.
- Discovery imports every module under `modgud/`, so nothing runnable may live there; examples sit in `examples/`.
- The Idunn container is a process-wide singleton shared with the host application; `Idunn().reset()` clears the host's registrations too and costs a re-discovery.
- `@Invert()` hides the decorators' real signatures from type checkers (`inspect.signature` follows `__wrapped__` since Idunn 2.0); fixing the static side belongs upstream in Idunn.
- The root name `'modgud'` is spelled once per decorator instead of once in a wiring module.

## Alternatives Considered
1. **Hand-written wiring** (a module-level registry of port → adapter). Rejected: it reinvents the half of a container that is easy and skips the half that is tested.
2. **Constructor injection only, no discovery.** Rejected: the decorators are constructed by users at import time, who should not have to pass a runtime.
3. **Keep direct imports and document the layering.** Rejected: that was the status quo, and the status quo was a comment.
