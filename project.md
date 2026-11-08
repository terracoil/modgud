# modgud project layout

## 🗂️ Directory layout

```bash
modgud/                            # Facade: the 24 public names, absolute imports + __all__, __version__
  app/                             # Decorators, markers and guard toolkit (re-exports all ten)
    guarded_expression.py          # class guarded_expression, @Invert(bootstrap='modgud', keys=...) __init__
    implicit_return.py             # class implicit_return, same @Invert (applied as @implicit_return())
    eop_cond.py, eop_case.py, eop_match.py   # EopCond / EopCase / EopMatch markers and their eop_* constants
    eop_when.py, eop_var.py        # EopWhen / EopVar pattern vocabulary
    guards.py                      # Guards (CommonGuards alias)
    guard_registry.py              # GuardRegistry
  domain/                          # Facade: 14 names (enum, errors, GuardFunction, eop_clause, the three ports)
    enums/                         # GuardFailureEnum; EopFormEnum (leaf export only)
    errors/                        # GuardClauseError, ImplicitReturnError + 5 children, MarkerNotRewrittenError, one per module
    ports/                         # @Port protocols (GuardPort, ImplicitReturnPort, EopPort)
    types.py                       # GuardFunction, eop_clause, and the T / T_co / F type variables
  infrastructure/                  # Exports nothing; all three subpackages are internal
    adapters/                      # @Adapter implementations of the ports, discovered and injected by Idunn; the three EopPort adapters are keyed
    ast/                           # Internal AST helpers for the transformer and the form adapters (underscore modules, re-exported by __init__ only)
    internal/                      # MethodDescriptors: unwrap/rewrap staticmethod & classmethod around the adapters; shared code that is not AST work
examples/
  free_range/                      # Module-level decorated functions; exempt from single-class-per-file / no-loose-functions
  classy/                          # One class per file, no module-level def, a demo() classmethod with the asserts
tests/                             # pytest; test_architecture.py enforces the table below
```

## 📜 API tiers

| Tier | Names | Import from |
|---|---|---|
| Public | `guarded_expression`, `implicit_return`, `GuardFailureEnum`, `GuardClauseError`, `GuardFunction`, `ImplicitReturnError` and its 5 children, `MarkerNotRewrittenError`, `Guards` and its alias `CommonGuards`, `GuardRegistry`, `eop_cond`, `eop_case`, `eop_match`, `eop_clause`, `eop_when`, `eop_var` (21 names; plus the three ports below, 24 in `__all__`) | `modgud` |
| Integration seam | `GuardPort`, `ImplicitReturnPort`, `EopPort`; the `guard_port=` / `imp_return_port=` / `eop_*_port=` parameters; `IDUNN_ENV`; `Idunn().reset()` | `modgud`, `modgud.domain`, or `modgud.domain.ports` |
| Internal | the five adapters, the `ast` helpers, `MethodDescriptors`, `EopFormEnum` | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast`, `modgud.infrastructure.internal`, `modgud.domain.enums` |

The structure used to be the API. It turned out people wanted one import line; see ADR-004.

## 🔗 Re-export rules

- Leaf packages (those with `.py` files beyond `__init__.py`) re-export via single-dot relative imports + `__all__`.
- The root facade re-exports via absolute imports + `__all__`, and imports every name directly from the package that owns it (four from `modgud.app`, one from `modgud.domain.enums`, five from `modgud.domain.errors`, two from `modgud.domain.ports`, one from `modgud.domain.types`). `modgud.domain` is a convenience facade, not a layer the root goes through. `modgud.infrastructure` exports nothing: re-exporting the guards from it would point infrastructure at `app`.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the `modgud.domain.<owner>` that holds the symbol (`enums`, `errors`, `ports` or `types`). That is what keeps import cycles impossible, and the architecture test flags any breach.
- Ports are re-exported by `modgud.domain`, so a port module must never import `modgud.domain`; it imports `modgud.domain.enums`, `.errors` or `.types` directly. Going through the facade only works while `.types` loads before `.ports` in its `__init__`, and ruff's import sort puts `.ports` first. Everything else under `modgud/` takes a port from `modgud.domain.ports`.
- `GuardFunction` lives in a module directly under `domain`, and the only package above it is the facade. So `from modgud.domain.types import GuardFunction` is the one sanctioned exception to never importing from filenames.
- Nothing runnable lives under `modgud/`: Idunn's discovery imports every module there. Examples live in `examples/`.

IoC: the app layer depends on ports only. [Idunn](https://pypi.org/project/idunn) discovers `modgud.domain.ports` and `modgud.infrastructure.adapters` the first time a decoration leaves a port to injection: each decorator's `__init__` wears `@Invert(bootstrap='modgud', keys=...)`, which bootstraps the package and then injects the adapters, the three `EopPort` adapters by their `EopFormEnum` key. The decorators pass the form ports to the transformer as `forms`; the markers reach their port through a private `@Invert` helper only to refuse a plain call. A decoration that supplies every port discovers nothing. `Idunn(` appears nowhere under `modgud/`, and `Invert` is imported only in `app`.

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
