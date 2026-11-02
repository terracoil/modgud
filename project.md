## Directory layout:

```bash
-modgud/                          # Top-level package (docstring + __version__ only; no re-exports)
  -app/                            # Decorators (re-exports guarded_expression, implicit_return)
    -wiring.py                     # Wiring.ensure(): the single Idunn composition root (not re-exported)
    -guarded_expression.py         # class guarded_expression, @Invert() __init__
    -implicit_return.py            # class implicit_return, @Invert() __init__ (applied as @implicit_return())
  -domain/                         # Container package — no re-exports
   -guarded_expr/                  # Guarded-expression parent
     -ports/                       # @Port protocols (GuardRuntimePort) injected to hide infrastructure
     -enums/guard_failure_enum.py  # GuardFailureEnum
     -errors/guard_clause_error.py # GuardClauseError
     -types.py                     # GuardFunction (shared with app and infrastructure)
    -implicit_ret/                 # Implicit Return parent
     -ports/                       # @Port protocols (ImplicitReturnTransformerPort)
     -errors/                      # ImplicitReturnError + 3 children, one per module
  -infrastructure/                 # Container package — no re-exports. Implementations that don't concern the user.
    -adapters/                     # @Adapter implementations of the ports, discovered and injected by Idunn
    -common/                       # CommonGuards and GuardRegistry
    -ast/                          # Internal AST helpers for the transformer adapter (underscore modules, re-exported by __init__ only)
```

Re-export rule: only leaf packages (those containing `.py` files beyond `__init__.py`) re-export, via single-dot relative imports + `__all__`. Container packages (`modgud`, `modgud.domain`, `modgud.infrastructure`) carry a docstring only. Consumers import from the owning leaf package, e.g. `from modgud.domain.guarded_expr import GuardFunction`.

IoC: the app layer depends on ports only. [Idunn](https://pypi.org/project/idunn) discovers `modgud.domain.*.ports` and `modgud.infrastructure.adapters` when `Wiring.ensure()` calls `Idunn().bootstrap('modgud')` on the first decoration, and `@Invert()` injects the adapters into the decorator constructors. `Idunn(` appears only in `modgud/app/wiring.py`.

Import exception (ports): ports are imported from the 4-level path `modgud.domain.<feature>.ports`. They are deliberately **not** re-exported by the feature package: each port module imports `GuardFunction`/`GuardFailureEnum` from its feature package, so re-exporting the port there creates a circular import. This is the one sanctioned exception to the 3-level import cap.

---

## Dependencies
Enforced by `tests/test_architecture.py`.

| Name                                  | May import from `modgud`                                                         | Third-party                                                        |
|:--------------------------------------|:---------------------------------------------------------------------------------|:-------------------------------------------------------------------|
| `modgud.app`                          | `modgud.domain.<feature>`, `modgud.domain.<feature>.ports`                       | `idunn` (`Invert` anywhere; `Idunn`/`ReportMap` only in `wiring.py`) |
| `modgud.infrastructure.adapters`      | `modgud.domain.<feature>`, `modgud.domain.<feature>.ports`, `modgud.infrastructure.common`, `modgud.infrastructure.ast` | `idunn` (`Adapter`, `LifecycleEnum`) |
| `modgud.infrastructure.common`        | `modgud.domain.<feature>`                                                        | none                                                               |
| `modgud.infrastructure.ast`           | `modgud.domain.<feature>`, itself (package only; imported solely by `adapters`)   | none                                                               |
| `modgud.domain.<feature>.ports`       | `modgud.domain.<feature>` (own feature only)                                     | `idunn.Port` only                                                  |
| `modgud.domain.<feature>` (non-ports) | own feature only (never its own `ports`)                                         | none                                                               |

Nothing in `modgud/` outside `modgud.infrastructure.adapters` imports it; only tests do. `modgud.infrastructure.ast` is imported only by the adapters, as the package, never by module filename.

---
