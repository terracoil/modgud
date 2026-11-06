**Parent**: [📋 ADR Index](README.md) | [📖 ADR-003](ADR-003-registry-system-architecture.md) | [📖 ADR-005](ADR-005-idunn-ports-and-adapters.md)

# ADR-004: Public Facade and API Tiers

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2026-11-02), amended 2026-11-06

> **Update 2026-11-06.** The `guarded_expr` and `implicit_ret` feature packages are gone: `modgud.domain` now holds `enums/`, `errors/`, `ports/` and `types.py` directly. Read "feature package" below as one of those four, and `modgud.domain.<feature>.ports` as `modgud.domain.ports`. The facades and their names did not change.

## Context
The package layout was tried as the API: no top-level re-exports, and every symbol imported from the leaf package that owns it. It kept the containers honest and it made a quick start four import lines long. Three of those lines named a layer (`app`, `domain`, `infrastructure`) that a user has no reason to know about. Every reorganisation of the tree was also a change to the public API, which is the wrong coupling in the wrong direction.

## Decision
`modgud/__init__.py` re-exports exactly 13 names, with absolute imports and an explicit `__all__`. `modgud.domain` (the 7 passive names and the 2 ports) and `modgud.app` (the decorators, `CommonGuards`, `GuardRegistry`) are secondary paths to the same objects; `modgud.infrastructure` exports nothing. The API has three tiers:

- **Public**: the 13 names, imported from `modgud`.
- **Integration seam**: the two ports (also reachable at `modgud.domain` and `modgud.domain.<feature>.ports`), the `runtime=` / `transformer=` parameters, `IDUNN_ENV` and `Idunn().reset()`.
- **Internal**: the adapters and the `ast` helpers. Importable, not promised.

Two rules keep this from collapsing back into a cycle: nothing inside `modgud/` imports a facade, and a port module never imports its own feature package, which re-exports it. The docs teach one import path. The leaf paths keep working, but their layout may change between releases.

## Consequences

### Positive
- One import line for users; the tree can move without a deprecation cycle.
- The tiers say which breakages count as breaking changes.
- Fitness functions exist: `tests/test_public_api.py` pins `__all__` and object identity; the facade probes in `tests/test_architecture.py` flag any inner module that imports a facade.

### Negative
- Two import paths exist for every public name. The docs pick one; a grep in `tests/test_docs.py` keeps user-facing docs on it.
- The root facade names every export twice (import line and `__all__`), and the identity test exists because that is the kind of list that drifts.
- `import modgud` now also imports `idunn`.

## Alternatives Considered
1. **Keep "the structure is the API".** Rejected: the four-line quick start and the tree-equals-API coupling above.
2. **Export the ports only from the 4-level path.** Rejected: the decorators' `runtime=` / `transformer=` parameters are already typed by the ports, so the commitment exists either way; exporting them costs nothing new.
3. **Route the root through the `modgud.domain` facade with a star import.** Tried first; it needed a ruff per-file ignore and put a facade between the root and the owning packages for no gain. The root now imports from the feature packages directly.
