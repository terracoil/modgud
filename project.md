# modgud project layout

## 🗂️ Directory layout

```bash
modgud/                            # Facade: the 13 public names, absolute imports + __all__, __version__
  app/                             # Decorators and guard toolkit (re-exports all four)
    guarded_expression.py          # class guarded_expression, @Invert(bootstrap='modgud') __init__
    implicit_return.py             # class implicit_return, same @Invert (applied as @implicit_return())
    common_guards.py               # CommonGuards
    guard_registry.py              # GuardRegistry
  domain/                          # Facade: 9 names (enum, errors, GuardFunction, the two ports)
    enums/guard_failure_enum.py    # GuardFailureEnum
    errors/                        # GuardClauseError, ImplicitReturnError + 3 children, one per module
    ports/                         # @Port protocols (GuardPort, ImplicitReturnPort)
    types.py                       # GuardFunction, and the T / F type variables the ports use
  infrastructure/                  # Exports nothing; all three subpackages are internal
    adapters/                      # @Adapter implementations of the ports, discovered and injected by Idunn
    ast/                           # Internal AST helpers for the transformer (underscore modules, re-exported by __init__ only)
    internal/                      # MethodDescriptors: unwrap/rewrap staticmethod & classmethod around the adapters
examples/
  free_range/                      # Module-level decorated functions; exempt from single-class-per-file / no-loose-functions
  classy/                          # One class per file, no module-level def, a demo() classmethod with the asserts
tests/                             # pytest; test_architecture.py enforces the table below
```

## 📜 API tiers

| Tier | Names | Import from |
|---|---|---|
| Public | `guarded_expression`, `implicit_return`, `GuardFailureEnum`, `GuardClauseError`, `GuardFunction`, `ImplicitReturnError` and its 3 children, `CommonGuards`, `GuardRegistry` (11 names; plus the two ports below, 13 in `__all__`) | `modgud` |
| Integration seam | `GuardPort`, `ImplicitReturnPort`; the `guard_port=` / `imp_return_port=` parameters; `IDUNN_ENV`; `Idunn().reset()` | `modgud`, `modgud.domain`, or `modgud.domain.ports` |
| Internal | `GuardAdapter`, `ImplicitReturnAdapter`, `NoExplicitReturnChecker`, `TailRewriter`, `TopLevelTransformer`, `MethodDescriptors` | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast`, `modgud.infrastructure.internal` |

The structure used to be the API. It turned out people wanted one import line; see ADR-004.

## 🔗 Re-export rules

- Leaf packages (those with `.py` files beyond `__init__.py`) re-export via single-dot relative imports + `__all__`.
- The root facade re-exports via absolute imports + `__all__`, and imports every name directly from the package that owns it (four from `modgud.app`, one from `modgud.domain.enums`, five from `modgud.domain.errors`, two from `modgud.domain.ports`, one from `modgud.domain.types`). `modgud.domain` is a convenience facade, not a layer the root goes through. `modgud.infrastructure` exports nothing: re-exporting the guards from it would point infrastructure at `app`.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the `modgud.domain.<owner>` that holds the symbol (`enums`, `errors`, `ports` or `types`). That is what keeps import cycles impossible, and the architecture test flags any breach.
- Ports are re-exported by `modgud.domain`, so a port module must never import `modgud.domain`; it imports `modgud.domain.enums`, `.errors` or `.types` directly. Going through the facade only works while `.types` loads before `.ports` in its `__init__`, and ruff's import sort puts `.ports` first. Everything else under `modgud/` takes a port from `modgud.domain.ports`.
- `GuardFunction` lives in a module directly under `domain`, and the only package above it is the facade. So `from modgud.domain.types import GuardFunction` is the one sanctioned exception to never importing from filenames.
- Nothing runnable lives under `modgud/`: Idunn's discovery imports every module there. Examples live in `examples/`.

IoC: the app layer depends on ports only. [Idunn](https://pypi.org/project/idunn) discovers `modgud.domain.ports` and `modgud.infrastructure.adapters` the first time a decoration leaves a port to injection: each decorator's `__init__` wears `@Invert(bootstrap='modgud')`, which bootstraps the package and then injects the adapters. A decoration that supplies every port discovers nothing. `Idunn(` appears nowhere under `modgud/`.

## 🔗 Dependencies

Enforced by `tests/test_architecture.py`. No row may import a third-party package other than what its last column names. `<owner>` is one of the four names directly under `modgud.domain`: `enums`, `errors`, `ports` or `types`.

| Name | May import from `modgud` | Third-party |
|:--|:--|:--|
| `modgud` (facade) | `modgud.app`, `modgud.domain`, `modgud.domain.<owner>` | none |
| `modgud.domain` (facade) | `modgud.domain.<owner>` | none |
| `modgud.infrastructure` (facade) | nothing | none |
| `modgud.app` | `modgud.app.*`, `modgud.domain.<owner>` | `idunn` (`Invert` only) |
| `modgud.infrastructure.adapters` | `modgud.domain.<owner>`, `modgud.infrastructure.ast`, `modgud.infrastructure.internal` | `idunn` (`Adapter`, `LifecycleEnum`) |
| `modgud.infrastructure.ast` | `modgud.domain.<owner>`, itself (package only; imported solely by `adapters`) | none |
| `modgud.infrastructure.internal` | `modgud.domain.<owner>`, itself (package only; imported solely by `adapters`) | none |
| `modgud.domain.ports` | itself, `modgud.domain.enums`, `.errors` and `.types`; never `modgud.domain` | `idunn.Port` only |
| `modgud.domain.enums`, `.errors`, `.types` | itself only | none |

Nothing in `modgud/` outside `modgud.infrastructure.adapters` imports the adapters; only tests do. `modgud.infrastructure.ast` and `modgud.infrastructure.internal` are imported only by the adapters, as the package, never by module filename.

## 🗂️ Example tree rules

- `free_range/`: module-level decorated functions, then `if __name__ == '__main__':`. Exempt from single-class-per-file and no-loose-functions; every other rule applies.
- `classy/`: exactly one class, no module-level `def`, a `demo()` classmethod holding the asserts, ending with `if __name__ == '__main__': XxxExample.demo()`.
- Same numbering in both trees; every classy file has a free-range twin. Imports are `from modgud import ...` and the stdlib only. No `__init__.py`. `tests/test_examples.py` runs every file, checks the README index and the twins, and checks the classy one-class / no-module-level-def rule; the other conventions are reviewed by hand.
