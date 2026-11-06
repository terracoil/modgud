# modgud project layout

## 🗂️ Directory layout

```bash
modgud/                            # Facade: the 13 public names, absolute imports + __all__, __version__
  app/                             # Decorators and guard toolkit (re-exports all four)
    method_descriptors.py          # MethodDescriptors: unwrap/rewrap staticmethod & classmethod around the decorators
    guarded_expression.py          # class guarded_expression, @Invert(bootstrap='modgud') __init__
    implicit_return.py             # class implicit_return, same @Invert (applied as @implicit_return())
    common_guards.py               # CommonGuards
    guard_registry.py              # GuardRegistry
  domain/                          # Facade: 9 names (enum, errors, GuardFunction, the two ports)
    guarded_expr/                  # Guarded-expression feature
      ports/                       # @Port protocols (GuardPort)
      enums/guard_failure_enum.py  # GuardFailureEnum
      errors/guard_clause_error.py # GuardClauseError
      types.py                     # GuardFunction (shared with app and infrastructure)
    implicit_ret/                  # Implicit-return feature
      ports/                       # @Port protocols (ImplicitReturnPort)
      errors/                      # ImplicitReturnError + 3 children, one per module
  infrastructure/                  # Exports nothing; both subpackages are internal
    adapters/                      # @Adapter implementations of the ports, discovered and injected by Idunn
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
| Integration seam | `GuardPort`, `ImplicitReturnPort`; the `runtime=` / `transformer=` parameters; `IDUNN_ENV`; `Idunn().reset()` | `modgud`, `modgud.domain`, or `modgud.domain.<feature>.ports` |
| Internal | `GuardAdapter`, `ImplicitReturnAdapter`, `NoExplicitReturnChecker`, `TailRewriter`, `TopLevelTransformer` | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast` |

The structure used to be the API. It turned out people wanted one import line; see ADR-004.

## 🔗 Re-export rules

- Leaf packages (those with `.py` files beyond `__init__.py`) re-export via single-dot relative imports + `__all__`.
- The root facade re-exports via absolute imports + `__all__`, and imports every name directly from the package that owns it (four from `modgud.app`, four from `modgud.domain.guarded_expr`, five from `modgud.domain.implicit_ret`). `modgud.domain` is a convenience facade, not a layer the root goes through. `modgud.infrastructure` exports nothing: re-exporting the guards from it would point infrastructure at `app`.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the owning feature package. That is what keeps import cycles impossible, and the architecture test flags any breach.
- Ports are re-exported by their feature package and by `modgud.domain`, so a port module must never import its own feature package; it imports the feature's `enums`, `errors` or `types` directly. Going through the feature package only works while `.types` loads before `.ports` in its `__init__`, and ruff's import sort puts `.ports` first. This is the one sanctioned exception to never importing from filenames. Only the feature's `__init__` imports the `ports` subpackage; everything else under `modgud/` takes a port from `modgud.domain.<feature>`, which keeps it inside the 3-level cap.
- Nothing runnable lives under `modgud/`: Idunn's discovery imports every module there. Examples live in `examples/`.

IoC: the app layer depends on ports only. [Idunn](https://pypi.org/project/idunn) discovers `modgud.domain.*.ports` and `modgud.infrastructure.adapters` the first time a decoration leaves a port to injection: each decorator's `__init__` wears `@Invert(bootstrap='modgud')`, which bootstraps the package and then injects the adapters. A decoration that supplies every port discovers nothing. `Idunn(` appears nowhere under `modgud/`.

## 🔗 Dependencies

Enforced by `tests/test_architecture.py`. No row may import a third-party package other than what its last column names.

| Name | May import from `modgud` | Third-party |
|:--|:--|:--|
| `modgud` (facade) | `modgud.app`, `modgud.domain`, `modgud.domain.<feature>` | none |
| `modgud.domain` (facade) | `modgud.domain.<feature>` | none |
| `modgud.infrastructure` (facade) | nothing | none |
| `modgud.app` | `modgud.app.*`, `modgud.domain.<feature>` | `idunn` (`Invert` only) |
| `modgud.infrastructure.adapters` | `modgud.domain.<feature>`, `modgud.infrastructure.ast` | `idunn` (`Adapter`, `LifecycleEnum`) |
| `modgud.infrastructure.ast` | `modgud.domain.<feature>`, itself (package only; imported solely by `adapters`) | none |
| `modgud.domain.<feature>.ports` | own feature's subpackages and modules, never the feature package itself | `idunn.Port` only |
| `modgud.domain.<feature>` (non-ports) | own feature only; only the feature's `__init__` may import its `ports` package | none |

Nothing in `modgud/` outside `modgud.infrastructure.adapters` imports the adapters; only tests do. `modgud.infrastructure.ast` is imported only by the adapters, as the package, never by module filename.

## 🗂️ Example tree rules

- `free_range/`: module-level decorated functions, then `if __name__ == '__main__':`. Exempt from single-class-per-file and no-loose-functions; every other rule applies.
- `classy/`: exactly one class, no module-level `def`, a `demo()` classmethod holding the asserts, ending with `if __name__ == '__main__': XxxExample.demo()`.
- Same numbering in both trees; every classy file has a free-range twin. Imports are `from modgud import ...` and the stdlib only. No `__init__.py`. `tests/test_examples.py` runs every file, checks the README index and the twins, and checks the classy one-class / no-module-level-def rule; the other conventions are reviewed by hand.
