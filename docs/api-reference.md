**Parent**: [📚 Documentation Hub](README.md) | [🌉 Main README](../README.md) | [⚙️ How It Works](how-it-works.md)

# API Reference

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>
---

## 📋 Table of Contents

- [📦 Module Overview](#module-overview)
- [🎖️ Primary Decorators](#primary-decorators)
  - [guarded_expression](#guarded_expression)
  - [implicit_return](#implicit_return)
- [📖 Usage Patterns: Choosing Your Approach](#usage-patterns-choosing-your-approach)
- [🧩 Pre-built Guard Functions](#pre-built-guard-functions)
- [🚨 Error Classes](#error-classes)
- [📝 Guard Registry Functions](#guard-registry-functions)
- [📐 Type Definitions](#type-definitions)

---

## 📦 Module Overview

```python
# Primary decorators
from modgud.app import guarded_expression, implicit_return

# Errors and type alias
from modgud.domain.guarded_expr import GuardClauseError
from modgud.domain.implicit_ret import (
    ExplicitReturnDisallowedError,
    ImplicitReturnError,
    MissingImplicitReturnError,
    UnsupportedConstructError,
)

# Guard validators (static methods on CommonGuards) + registry
from modgud.infrastructure.guarded_expr import CommonGuards, GuardRegistry
```

**Version**: 0.2.0
**Python**: 3.11+
**Zero Runtime Dependencies**: Uses only Python standard library

---

## 🎖️ Primary Decorators

### guarded_expression

Unified decorator combining guard clauses with optional implicit return transformation.

#### Signature

```python
guarded_expression(
    *guards: GuardFunction,
    implicit_return: bool = True,
    strategy: GuardFailureStrategy = GuardFailureStrategy.ERROR_RAISE,
    on_failure: Any = GuardClauseError,
    continuance: int = 0,
) -> Callable[[Callable], Callable]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | - | Variable number of guard functions that validate input |
| `implicit_return` | `bool` | `True` | Enable implicit return AST rewrite |
| `strategy` | `GuardFailureStrategy` | `ERROR_RAISE` | How collected failures are dispatched (see below) |
| `on_failure` | `Any` | `GuardClauseError` | Payload paired with `strategy` |
| `continuance` | `int` | `0` | Extra guards to evaluate past the first failure |

#### GuardFailureStrategy + on_failure pairings

| `strategy` | `on_failure` means | Body executed on failure? |
|-----|-----|-----|
| `ERROR_RAISE` (default) | Exception class to raise | No |
| `ERROR_RETURN` | Exception class to instantiate and return | No |
| `RETURN_VALUE` | Value to return as-is | No |
| `CALL_HANDLER` | Callable invoked as `on_failure(errors, *args, **kwargs)` | No |

When `continuance > 0` and more than one failure is collected, `ERROR_RAISE` / `ERROR_RETURN` wrap the instances in `ExceptionGroup('Guards failed', [...])`.

#### Returns

Decorated function with guard validation and optional implicit returns.

#### Raises

Failure mode is strict: if `implicit_return=True` and the AST rewrite refuses (source unavailable, unsupported construct), the underlying exception (`ValueError`, `OSError`, `UnsupportedConstructError`, etc.) propagates from the decoration site.

#### Examples

##### Basic Guard Validation

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.not_none("x"),
    CommonGuards.positive("x")
)
def calculate(x):
    return x * 2

calculate(5)   # Returns: 10
calculate(-1)  # Raises: GuardClauseError: x must be positive
calculate(None)  # Raises: GuardClauseError: x must not be None
```

##### Implicit Returns

```python
@guarded_expression()
def get_status(user):
    if user.is_active:
        "active"
    else:
        "inactive"

# No explicit return needed!
```

##### Custom Error Handling

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

# Return None on failure
@guarded_expression(
    CommonGuards.positive("amount"),
    on_error=None
)
def process_payment(amount):
    amount * 1.1  # Add tax

process_payment(-10)  # Returns: None

# Custom handler function
def log_and_default(msg, *args, **kwargs):
    print(f"Guard failed: {msg}")
    return 0

@guarded_expression(
    CommonGuards.positive("x"),
    on_error=log_and_default
)
def safe_divide(x):
    100 / x

safe_divide(-5)  # Prints error, returns 0
```

##### With Logging

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.not_empty("items"),
    log=True  # Enables logging
)
def process_items(items):
    len(items) * 10

process_items([])  # Logs: "INFO: Guard failed: items must not be empty"
```

##### Usage Patterns (Both Fully Supported)

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards

# Pattern 1: Unified parameter (simple, all-in-one)
@guarded_expression(
    CommonGuards.positive("x"),
    implicit_return=True  # Fully supported!
)
def calculate(x):
    result = x * 2
    result

# Pattern 2: Separate decorators (flexible, composable)
@guarded_expression(CommonGuards.positive("x"))
@implicit_return
def calculate_v2(x):
    result = x * 2
    result

# Both patterns are first-class citizens - choose based on your needs!
```

---

### implicit_return

**New in v0.3.0:** Standalone decorator for expression-oriented programming that transforms the last expression in each code path into an implicit return value.

#### Signature

```python
implicit_return(func: Callable) -> Callable
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `func` | `Callable` | Function to transform with implicit returns |

#### Returns

Decorated function with AST-transformed implicit return behavior.

#### Raises

- `ExplicitReturnDisallowedError`: If function contains explicit `return` statements
- `MissingImplicitReturnError`: If not all code paths yield a value
- `UnsupportedConstructError`: If source code contains unsupported constructs

#### Examples

##### Basic Implicit Returns

```python
from modgud.app import implicit_return

@implicit_return
def classify_status(is_active, is_premium):
    if is_active:
        "premium" if is_premium else "standard"
    else:
        "inactive"

classify_status(True, True)   # Returns: "premium"
classify_status(True, False)  # Returns: "standard" 
classify_status(False, True)  # Returns: "inactive"
```

##### Composition with Guards

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(CommonGuards.not_none("user"))
@implicit_return
def get_user_role(user):
    if user.is_admin:
        "admin"
    elif user.is_moderator:
        "moderator"
    else:
        "user"
```

##### Complex Control Flow

```python
@implicit_return
def process_data(data, fallback_mode=False):
    try:
        if fallback_mode:
            data.get("simple_result", "default")
        else:
            complex_processing(data)
    except ProcessingError:
        "error_occurred"
    except Exception:
        "unknown_error"
```

#### Notes

- **Two Valid Patterns**: Use `implicit_return=True` parameter OR separate `@implicit_return` decorator
- **Order Matters**: When using separate decorators, `@implicit_return` should typically be the innermost (closest to the function)
- **⚠️ Composition Warning**: Avoid placing `@implicit_return` before `@guarded_expression` as it may bypass guards
- **Source Required**: Function source code must be available via `inspect.getsource()`
- **No Explicit Returns**: Functions cannot contain `return` statements when using implicit returns
- **All Paths Must Yield**: Every execution path must end with an expression that produces a value

---

## 📖 Usage Patterns: Choosing Your Approach

modgud offers two equally valid patterns for combining guards with implicit returns. Both are fully supported and the choice depends on your specific needs.

### Pattern 1: Unified Parameter Approach

**When to use:**
- Simple functions with guards and implicit returns
- When you want all configuration in one place
- Teaching/learning scenarios
- Functions where the transformation is core to the function's identity

**Example:**
```python
@guarded_expression(
    CommonGuards.positive("amount"),
    CommonGuards.not_none("user"),
    implicit_return=True,  # All-in-one configuration
    on_error=None
)
def calculate_discount(amount, user):
    discount = user.discount_rate if user.is_premium else 0.05
    amount * (1 - discount)
```

**Benefits:**
- Single decorator for complete function transformation
- Explicit configuration in one place
- Easier to understand for newcomers
- Reduces decorator stack complexity

### Pattern 2: Separate Decorators Approach

**When to use:**
- Complex decorator compositions
- When implicit return is optional/conditional
- Building reusable decorator stacks
- Need maximum flexibility

**Example:**
```python
@cache  # Other decorators can be added
@guarded_expression(CommonGuards.positive("amount"), CommonGuards.not_none("user"))
@implicit_return  # Separate concern
def calculate_discount(amount, user):
    discount = user.discount_rate if user.is_premium else 0.05
    amount * (1 - discount)
```

**Benefits:**
- More composable and flexible
- Clearer separation of concerns
- Better for complex decorator stacks
- Allows fine-grained control

### ⚠️ Important: Decorator Order Matters

When using separate decorators, the order is critical:

```python
# ✅ CORRECT: Guards before implicit return
@guarded_expression(CommonGuards.positive("x"))
@implicit_return
def correct(x):
    x * 2

# ❌ WRONG: This can bypass guards!
@implicit_return
@guarded_expression(CommonGuards.positive("x"))  # Guards may not execute properly
def problematic(x):
    x * 2
```

The incorrect order can cause guards to be bypassed due to how Python's `inspect.getsource()` works with decorated functions.

### Choosing Between Patterns

| Use Case | Recommended Pattern | Example |
|----------|-------------------|---------|
| Simple validation + implicit return | Unified parameter | `@guarded_expression(..., implicit_return=True)` |
| Complex decorator stacks | Separate decorators | `@cache @guarded_expression(...) @implicit_return` |
| Guards without implicit returns | Unified with `implicit_return=False` | `@guarded_expression(..., implicit_return=False)` |
| Conditional implicit returns | Separate decorators | Apply `@implicit_return` conditionally |
| Teaching/documentation | Unified parameter | Shows all features in one place |

### Migration from Deprecated Pattern

If you previously avoided the `implicit_return` parameter due to deprecation warnings:
1. **No action required** - your separate decorator code continues to work
2. **Optional**: Consider if the unified parameter would be cleaner for your use case
3. **Review**: Check decorator order if using separate decorators

---

## 🧩 Pre-built Guard Functions

Pre-defined guard validators for common validation scenarios. These are static methods on `CommonGuards`, imported from `modgud.infrastructure.guarded_expr`.

All methods are static and return `GuardFunction` instances that can be used with `guarded_expression`.

#### Methods

##### CommonGuards.not_empty

Ensures collection parameter is not empty.

```python
CommonGuards.not_empty(param_name: str = 'parameter', position: Optional[int] = None) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (None = first arg)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

# Using unified parameter approach
@guarded_expression(
    CommonGuards.not_empty("items"),
    implicit_return=True
)
def process(items):
    len(items)
```

---

##### CommonGuards.not_none

Ensures parameter is not None.

```python
CommonGuards.not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

# Using unified parameter approach
@guarded_expression(
    CommonGuards.not_none("user"),
    implicit_return=True
)
def greet(user):
  f"Hello, {user.item_name}"
```

---

##### CommonGuards.positive

Ensures numeric parameter is positive (> 0).

```python
CommonGuards.positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.positive("amount"),
    implicit_return=True
)
def calculate_tax(amount):
    amount * 0.1
```

---

##### CommonGuards.in_range

Ensures parameter is within specified range (inclusive).

```python
CommonGuards.in_range(
    min_val: Union[int, float],
    max_val: Union[int, float],
    param_name: str = 'parameter',
    position: int = 0
) -> GuardFunction
```

**Parameters:**
- `min_val`: Minimum allowed value (inclusive)
- `max_val`: Maximum allowed value (inclusive)
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.in_range(1, 10, "rating"),
    implicit_return=True
)
def save_rating(rating):
    {"rating": rating}

save_rating(5)   # OK
save_rating(11)  # Raises: GuardClauseError
```

---

##### CommonGuards.type_check

Ensures parameter is of expected type.

```python
CommonGuards.type_check(
    expected_type: type,
    param_name: str = 'parameter',
    position: int = 0
) -> GuardFunction
```

**Parameters:**
- `expected_type`: Expected type or tuple of types
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(CommonGuards.type_check(str, "name"))
def create_user(name):
    return {"name": name.upper()}

create_user("alice")  # OK
create_user(123)      # Raises: GuardClauseError
```

---

##### CommonGuards.matches_pattern

Ensures string parameter matches regex pattern.

```python
CommonGuards.matches_pattern(
    pattern: str,
    param_name: str = 'parameter',
    position: int = 0
) -> GuardFunction
```

**Parameters:**
- `pattern`: Regular expression pattern
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.matches_pattern(r'^\d{3}-\d{3}-\d{4}$', "phone")
)
def save_phone(phone):
    return {"phone": phone}

save_phone("555-123-4567")  # OK
save_phone("invalid")        # Raises: GuardClauseError
```

---

##### CommonGuards.valid_file_path

Validates file path with optional existence and type checks.

```python
CommonGuards.valid_file_path(
    param_name: str = 'path',
    position: int = 0,
    exists_required: bool = False,
    is_file: Optional[bool] = None
) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)
- `exists_required`: Whether path must exist
- `is_file`: `True` = must be file, `False` = must be directory, `None` = either

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.valid_file_path("config_path", exists_required=True, is_file=True)
)
def load_config(config_path):
    with open(config_path) as f:
        return f.read()
```

---

##### CommonGuards.valid_url

Validates URL format with optional scheme restrictions.

```python
CommonGuards.valid_url(
    param_name: str = 'url',
    position: int = 0,
    schemes: Optional[list[str]] = None
) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)
- `schemes`: Allowed URL schemes (default: ['http', 'https'])

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

@guarded_expression(
    CommonGuards.valid_url("endpoint", schemes=['https'])
)
def fetch_data(endpoint):
    # Fetch from HTTPS endpoint
    return f"Fetching from {endpoint}"
```

---

##### CommonGuards.valid_enum

Ensures parameter is valid enum member.

```python
CommonGuards.valid_enum(
    enum_class: type[Enum],
    param_name: str = 'parameter',
    position: int = 0
) -> GuardFunction
```

**Parameters:**
- `enum_class`: The Enum class to validate against
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from enum import Enum

from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@guarded_expression(
    CommonGuards.valid_enum(Status, "status")
)
def update_status(status):
    return {"status": status.value}

update_status(Status.ACTIVE)  # OK
update_status("active")       # Raises: GuardClauseError
```

---

## 🚨 Error Classes

### GuardClauseError

Base exception raised when a guard clause fails.

```python
class GuardClauseError(Exception):
    pass
```

**Usage:**
```python
@guarded_expression(
    lambda x: x > 0 or "Must be positive",
    on_error=GuardClauseError  # Default
)
```

---

### ImplicitReturnError

Base class for implicit return transformation errors. Inherits from `SyntaxError`.

```python
class ImplicitReturnError(SyntaxError):
    def __init__(self, message: str, lineno: Optional[int] = None, col_offset: Optional[int] = None)
```

---

### ExplicitReturnDisallowedError

Raised when explicit `return` statement found in function with implicit returns.

```python
class ExplicitReturnDisallowedError(ImplicitReturnError):
    pass
```

**Example:**
```python
@guarded_expression()
def invalid():
    if True:
        return 5  # Error! No explicit returns allowed
```

---

### MissingImplicitReturnError

Raised when not all code paths yield a value.

```python
class MissingImplicitReturnError(ImplicitReturnError):
    pass
```

**Example:**
```python
@guarded_expression()
def invalid(x):
    if x > 0:
        x * 2
    # Error! Missing else branch
```

---

### UnsupportedConstructError

Raised when transformation encounters unsupported Python construct.

```python
class UnsupportedConstructError(ImplicitReturnError):
    pass
```

---

## 📝 Guard Registry Functions

Methods on `GuardRegistry` (imported from `modgud.infrastructure.guarded_expr`) for managing custom guard registration and retrieval.

### GuardRegistry.register

Register a custom guard function.

```python
GuardRegistry.register(
    name: str,
    guard_factory: Callable[..., GuardFunction],
    namespace: str | None = None
) -> None
```

**Example:**
```python
from modgud.infrastructure.guarded_expr import GuardRegistry

def positive_int(param_name="vector", position=0):
    def check(*args, **kwargs):
        value = kwargs.get(param_name, args[position] if position < len(args) else None)
        return (isinstance(value, int) and value > 0) or "Must be a positive integer"
    return check

GuardRegistry.register("positive_int", positive_int, namespace="validators")
```

---

### GuardRegistry.get

Retrieve a registered guard function.

```python
GuardRegistry.get(name: str, namespace: str | None = None) -> Callable[..., GuardFunction] | None
```

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import GuardRegistry

positive_int_guard = GuardRegistry.get("positive_int", namespace="validators")

@guarded_expression(positive_int_guard("count"))
def process(count):
    return count * 2
```

---

### GuardRegistry.has_guard

Check if a guard is registered.

```python
GuardRegistry.has_guard(name: str, namespace: str | None = None) -> bool
```

---

### GuardRegistry.list_guards

List all guards in a namespace.

```python
GuardRegistry.list_guards(namespace: str | None = None) -> list[str]
```

---

### GuardRegistry.list_namespaces

List all available namespaces.

```python
GuardRegistry.list_namespaces() -> list[str]
```

---

### GuardRegistry.unregister

Remove a registered guard.

```python
GuardRegistry.unregister(name: str, namespace: str | None = None) -> bool
```

---

### GuardRegistry.instance

Get the singleton guard registry instance.

```python
GuardRegistry.instance() -> GuardRegistry
```

**Returns:** The global `GuardRegistry` singleton.

---

## 📐 Type Definitions

### GuardFunction

Type alias for guard validation functions.

```python
GuardFunction = Callable[..., Union[bool, str]]
```

A guard function:
- Receives `(*args, **kwargs)` from the decorated function
- Returns `True` if validation passes
- Returns error message string if validation fails

---

### GuardFailureStrategy

Enum selecting how collected failures are dispatched. See the `guarded_expression` section above for the strategy × `on_failure` pairing table.

```python
class GuardFailureStrategy(IntEnum):
  ERROR_RAISE  = auto()
  ERROR_RETURN = auto()
  RETURN_VALUE = auto()
  CALL_HANDLER = auto()
```

---

### ErrorHandler

Type alias for error handling callables.

```python
ErrorHandler = Callable[[str, tuple, dict], Any]
```

Receives:
- Error message (str)
- Original args (tuple)
- Original kwargs (dict)

Returns: Value to return from decorated function

---

[← Back to Documentation Hub](README.md) | [← How It Works](how-it-works.md)
