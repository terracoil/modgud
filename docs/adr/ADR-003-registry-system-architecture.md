# ADR-003: Registry System Architecture

## Status
Accepted (2025-10-26)

## Context
Guard functions need a discovery mechanism for runtime configuration and plugin systems. Users should be able to register custom guards and access them by name, while avoiding naming conflicts between different guard sources (built-in, third-party, user-defined).

## Decision
Implement a global singleton registry with namespace support:
- **Global singleton**: Single `GuardRegistry` instance accessible throughout application
- **Namespaces**: Optional grouping to prevent naming collisions
- **Factory registration**: Register guard factories, not instances, for parameterization
- **Thread-safe**: Registry operations protected for concurrent access

Architecture:
```python
# Global singleton
_GLOBAL_REGISTRY = GuardRegistry()

# Registration with namespaces
from modgud import positive
register_guard("positive", positive)  # Default namespace
register_guard("email", validators.email, namespace="validators")

# Usage
registry.get("positive")()  # Returns guard factory
registry.get("email", namespace="validators")()
```

## Consequences

### Positive
- **Global accessibility**: Guards available anywhere without passing registry
- **Namespace isolation**: Prevents conflicts between packages
- **Plugin friendly**: Third-party packages can register guards
- **Lazy instantiation**: Factories called only when guards are used
- **Discovery**: Can list available guards for documentation/tooling

### Negative
- **Global state**: Singleton pattern introduces global mutable state
- **Import order**: Registration depends on module import order
- **Testing complexity**: Must reset registry between tests
- **No dependency injection**: Hard to substitute registry for testing
- **Memory overhead**: All registered guards stay in memory

## Alternatives Considered

### 1. Dependency Injection Container
Pass registry instance through constructors/parameters.
```python
def __init__(self, guard_registry: GuardRegistry):
  self.registry = guard_registry
```
- **Rejected**: Verbose, requires plumbing registry through entire codebase

### 2. Module-Level Registries
Each module maintains its own registry.
```python
# modgud.guards.common.registry
COMMON_REGISTRY = {}
```
- **Rejected**: No central discovery, import complexity

### 3. Class-Based Namespaces
Use classes as namespaces instead of strings.
```python
class CommonNamespace:
  positive = positive_guard
```
- **Rejected**: Less flexible, can't dynamically add guards

### 4. Decorator Registration
Register guards via decorator at definition.
```python
@register_guard("positive")
def positive_guard(...): ...
```
- **Rejected**: Couples definition with registration, less flexible

## Implementation Details

### Thread Safety
Registry uses locks for concurrent access:
```python
class GuardRegistry:
  def __init__(self):
    self._guards = {}
    self._namespaces = {}
    self._lock = threading.RLock()

  def register(self, name, factory, namespace=None):
    with self._lock:
      # Thread-safe registration
```

### Auto-Registration
CommonGuards auto-registers at import:
```python
# At module level in common_guards.py
def _register_common_guards():
  for name in dir(CommonGuards):
    if not name.startswith('_'):
      register_guard(name, getattr(CommonGuards, name), namespace='common')

_register_common_guards()
```

### Testing Support
Test utilities for registry isolation:
```python
@contextmanager
def isolated_registry():
  original = _GLOBAL_REGISTRY._guards.copy()
  try:
    yield _GLOBAL_REGISTRY
  finally:
    _GLOBAL_REGISTRY._guards = original
```

## References
- Service Locator pattern
- Python's `logging` module registry design
- pytest plugin registration system