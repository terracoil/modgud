# modgud project layout

## 🗂️ Directory layout

```bash
modgud/                            # Facade: the 13 public names, absolute imports + __all__, __version__
  app/                             # Decorators (re-exports guarded_expression, implicit_return, Wiring)
    wiring.py                      # Wiring.ensure(): the single Idunn composition root
    method_descriptors.py          # MethodDescriptors: unwrap/rewrap staticmethod & classmethod around the decorators
    guarded_expression.py          # class guarded_expression, @Invert() __init__
    implicit_return.py             # class implicit_return, @Invert() __init__ (applied as @implicit_return())
  domain/                          # Facade: the 7 passive names (enum, errors, GuardFunction); never the ports
    guarded_expr/                  # Guarded-expression feature
      ports/                       # @Port protocols (GuardRuntimePort)
      enums/guard_failure_enum.py  # GuardFailureEnum
      errors/guard_clause_error.py # GuardClauseError
      types.py                     # GuardFunction (shared with app and infrastructure)
    implicit_ret/                  # Implicit-return feature
      ports/                       # @Port protocols (ImplicitReturnTransformerPort)
      errors/                      # ImplicitReturnError + 3 children, one per module
  infrastructure/                  # Facade: CommonGuards and GuardRegistry only
    adapters/                      # @Adapter implementations of the ports, discovered and injected by Idunn
    common/                        # CommonGuards and GuardRegistry
    ast/                           # Internal AST helpers for the transformer (underscore modules, re-exported by __init__ only)
examples/
  free_range/                      # Module-level decorated functions; exempt from single-class-per-file / no-loose-functions
  classy/                          # One class per file, no module-level def, a demo() classmethod with the asserts
tests/                             # pytest; test_architecture.py enforces the table below
```

## 📜 API tiers

| Tier | Names | Import from |
|---|---|---|
| Public | `guarded_expression`, `implicit_return`, `GuardFailureEnum`, `GuardClauseError`, `GuardFunction`, `ImplicitReturnError` and its 3 children, `CommonGuards`, `GuardRegistry` (11 names; plus the two ports below, 13 in `__all__`) | `modgud` |
| Integration seam | `GuardRuntimePort`, `ImplicitReturnTransformerPort`; the `runtime=` / `transformer=` parameters; `IDUNN_ENV`; `Idunn().reset()` | `modgud`, or `modgud.domain.<feature>.ports` |
| Internal | `GuardRuntime`, `ImplicitReturnTransformer`, `NoExplicitReturnChecker`, `TailRewriter`, `TopLevelTransformer`, `Wiring` | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast`, `modgud.app` |

The structure used to be the API. It turned out people wanted one import line; see ADR-004.

## 🔗 Re-export rules

- Leaf packages (those with `.py` files beyond `__init__.py`) re-export via single-dot relative imports + `__all__`.
- Facades (`modgud`, `modgud.domain`, `modgud.infrastructure`) re-export via absolute imports + `__all__`. The root facade imports every name directly from the package that owns it (three from `modgud.domain.guarded_expr`, four from `modgud.domain.implicit_ret`); `modgud.domain` and `modgud.infrastructure` are convenience facades, not a layer the root goes through.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the owning feature package. That is what keeps import cycles impossible, and the architecture test flags any breach.
- Ports are imported from the 4-level path `modgud.domain.<feature>.ports`, never re-exported by their feature package: each port module imports from its feature package, so the re-export would be a cycle. This is the one sanctioned exception to the 3-level cap.
- Nothing runnable lives under `modgud/`: Idunn's discovery imports every module there. Examples live in `examples/`.

IoC: the app layer depends on ports only. [Idunn](https://pypi.org/project/idunn) discovers `modgud.domain.*.ports` and `modgud.infrastructure.adapters` when `Wiring.ensure()` calls `Idunn().bootstrap('modgud')` on the first decoration, and `@Invert()` injects the adapters into the decorator constructors. `Idunn(` appears only in `modgud/app/wiring.py`.

## 🔗 Dependencies

Enforced by `tests/test_architecture.py`. No row may import a third-party package other than what its last column names.

| Name | May import from `modgud` | Third-party |
|:--|:--|:--|
| `modgud` (facade) | `modgud.app`, `modgud.domain`, `modgud.infrastructure`, `modgud.domain.<feature>.ports` | none |
| `modgud.domain` (facade) | `modgud.domain.<feature>` | none |
| `modgud.infrastructure` (facade) | `modgud.infrastructure.common` | none |
| `modgud.app` | `modgud.app.*`, `modgud.domain.<feature>`, `modgud.domain.<feature>.ports` | `idunn` (`Invert` anywhere; `Idunn` / `ReportMap` only in `wiring.py`) |
| `modgud.infrastructure.adapters` | `modgud.domain.<feature>`, `modgud.domain.<feature>.ports`, `modgud.infrastructure.common`, `modgud.infrastructure.ast` | `idunn` (`Adapter`, `LifecycleEnum`) |
| `modgud.infrastructure.common` | `modgud.domain.<feature>` | none |
| `modgud.infrastructure.ast` | `modgud.domain.<feature>`, itself (package only; imported solely by `adapters`) | none |
| `modgud.domain.<feature>.ports` | `modgud.domain.<feature>` (own feature only) | `idunn.Port` only |
| `modgud.domain.<feature>` (non-ports) | own feature only (never its own `ports`) | none |

Nothing in `modgud/` outside `modgud.infrastructure.adapters` imports the adapters; only tests do. `modgud.infrastructure.ast` is imported only by the adapters, as the package, never by module filename.

## 🗂️ Example tree rules

- `free_range/`: module-level decorated functions, then `if __name__ == '__main__':`. Exempt from single-class-per-file and no-loose-functions; every other rule applies.
- `classy/`: exactly one class, no module-level `def`, a `demo()` classmethod holding the asserts, ending with `if __name__ == '__main__': XxxExample.demo()`.
- Same numbering in both trees; every classy file has a free-range twin. Imports are `from modgud import ...` and the stdlib only. No `__init__.py`. `tests/test_examples.py` runs every file, checks the README index and the twins, and checks the classy one-class / no-module-level-def rule; the other conventions are reviewed by hand.
