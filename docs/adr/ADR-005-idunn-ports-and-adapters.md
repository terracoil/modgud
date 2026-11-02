**Parent**: [📋 ADR Index](README.md) | [📖 ADR-004](ADR-004-public-facade-and-api-tiers.md) | [📚 Documentation Hub](../README.md)

# ADR-005: Idunn Ports and Adapters

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2026-11-02)

## Context
The decorators used to import `GuardRuntime` and `ImplicitReturnTransformer` directly. Tests that wanted a fake runtime had to monkeypatch a module attribute, and the "app never imports infrastructure" rule was a comment rather than a fact. A library whose whole pitch is discipline at function boundaries was wiring its own internals by hand.

## Decision
Ports and adapters, wired by [Idunn](https://pypi.org/project/idunn):

- `GuardRuntimePort` and `ImplicitReturnTransformerPort` are `@Port` Protocols in `modgud.domain.<feature>.ports`. The decorators depend on them only.
- `GuardRuntime` and `ImplicitReturnTransformer` subclass their port as `@Adapter(..., lifecycle=SINGLETON)` in `modgud.infrastructure.adapters`.
- `Wiring.ensure()` calls `Idunn().bootstrap('modgud')` on the first decoration, not at import. `@Invert()` on each decorator's `__init__` injects `runtime` / `transformer`; a caller-supplied value wins.
- Idunn imports are fenced: `Invert` in `app`, `Adapter` / `LifecycleEnum` in `adapters`, `Port` in `ports` modules, and `Idunn` / `ReportMap` only in `modgud/app/wiring.py`. `tests/test_architecture.py` enforces the fence.

## Consequences

### Positive
- The test seam is a parameter: pass `runtime=` or `transformer=` and no monkeypatching is needed.
- The layering rule is a test, not a comment.
- Idunn environments (`IDUNN_ENV`) exist, but modgud ships one adapter per port and does not test process-wide replacement; the supported seam is the per-decoration parameter.

### Negative
- One runtime dependency, after a long stretch of none. `import modgud` imports `idunn`.
- Discovery imports every module under `modgud/`, so nothing runnable may live there; examples sit in `examples/`.
- The Idunn container is a process-wide singleton shared with the host application; `Idunn().reset()` clears the host's registrations too and costs a re-discovery.
- `@Invert()` hides the decorators' real signatures from type checkers and `inspect.signature`; fixing that belongs upstream in Idunn.
- Supplying both `runtime=` and `transformer=` does not skip the bootstrap; `__new__` still discovers the adapters.

## Alternatives Considered
1. **Hand-written wiring** (a module-level registry of port → adapter). Rejected: it reinvents the half of a container that is easy and skips the half that is tested.
2. **Constructor injection only, no discovery.** Rejected: the decorators are constructed by users at import time, who should not have to pass a runtime.
3. **Keep direct imports and document the layering.** Rejected: that was the status quo, and the status quo was a comment.
