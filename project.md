## Directory layout:

```bash
-modgud/                          # Top-level package (docstring + __version__ only; no re-exports)
  -app/                            # Decorators (re-exports guarded_expression, implicit_return)
  -domain/                         # Container package — no re-exports
   -guarded_expr/             # Guarded-expression parent
     -ports/                      # Interfaces, or protocols injected to hide irrelevant infrastructure
     -enums/guard_failure_enum.py # GuardFailureEnum
     -errors/guard_clause_error.py # GuardClauseError
     -types.py                    # GuardFunction (shared by guarded_expr & app)
    -implicit_ret/                # Implicit Return parent
     -ports/                      # Interfaces, or protocols injected to hide irrelevant infrastructure
     -errors/                     # ImplicitReturnError + 3 children, one per module
  -infrastructure/                    # Container package — no re-exports. Implementations that don't concern the user.  For optimal hiding, we will use a domain/port (protocol) and an infrastructure/adapter (implementation) and use iOC (../gleipnyr soon to be published).
    -guarded_expr/                    # Guarded-expression functionality; encapsulated in adapters
    -implicit_ret/                    # Implicit Return functionality; encapsulated in adapters
```

Re-export rule: only leaf packages (those containing `.py` files beyond `__init__.py`) re-export, via single-dot relative imports + `__all__`. Container packages (`modgud`, `modgud.domain`, `modgud.infrastructure`) carry a docstring only. Consumers import from the owning leaf package, e.g. `from modgud.domain.guarded_expr import GuardFunction`.

---

## Dependencies
| Name                                 | Dependencies                                                   |
|:-------------------------------------|:---------------------------------------------------------------|
| `modgud.app`                         | `modgud.domain.<feature>`, `modgud.infrastructure.<feature>`   |
| `modgud.infrastructure.guarded_expr` | `modgud.domain.guarded_expr`                                   |
| `modgud.infrastructure.implicit_ret` | `modgud.domain.implicit_ret`                                   |
| `modgud.domain.guarded_expr`         | (self-contained)                                               |
| `modgud.domain.implicit_ret`         | (self-contained)                                               |
--- 
