## Directory layout:

```bash
-modgud/                          # Top-level modgud package
  -app/                            # Decorators
  -domain/
   -guarded_expr/             # Guarded-expression parent
     -ports/                      # Interfaces, or protocols injected to hide irrelevant infrastructure    
     -enums/                      # Enumerations, can be in enums.py if dir not needed 
     -errors/                     # Errors/exceptions, can be in errors.py if dir not needed
    -implicit_ret/                # Implicit Return parent
     -ports/                      # Interfaces, or protocols injected to hide irrelevant infrastructure    
     -enums/                      # Enumerations, can be in enums.py if dir not needed 
     -errors/                     # Errors/exceptions, can be in errors.py if dir not needed
  -infrastructure/                    # Implementations that don't concern the user.  For optimal hiding, we will use a domain/port (protocol) and an infrastructure/adapter (implementation) and use iOC (../gleipnyr soon to be published).
    -guarded_expr/                    # Guarded-expression functionality; encapsulated in adapters
    -implicit_ret/                    # Implicit Return functionality; encapsulated in adapters      
 -shared/                             # Domain-specific Items shared between guarded_expr & implicit_ret, and even app(if any)
 -util/                               # Generic utilities shared to between all layers, StrUtil, FileUtil, etc.  
```
---

## Dependencies
| Name                                 | Dependencies                   |
|:-------------------------------------|:-------------------------------|
| `modgud.app`                         | `modgud.domain`                |
| `modgud.infrastructure.guarded_expr` | `modgud.domain.guarded_expr`   |
| `modgud.infrastructure.implicit_ret` | `modgud.domain.implicit_ret`   |
| `modgud.domain.guarded_expr`         | `modgud.shared`, `modgud.util` |
| `modgud.domain.implicit_ret`         | `modgud.shared`, `modgud.util` |
| `modgud.shared`                      | `modgud.util`                  |
| `modgud.util`                        |                                |
--- 
