**Parent**: [📚 Documentation Hub](README.md) | [🌉 Main README](../README.md) | [⚙️ How It Works](how-it-works.md)

# API Reference

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>
---

## 📋 Table of Contents

- [📦 Module Overview](#module-overview)
- [🎖️ Primary Decorators](#primary-decorators)
  - [guarded_expression](#guarded_expression)
  - [implicit_return](#implicit_return)
- [🧩 Pre-built Guard Functions](#pre-built-guard-functions)
- [🚨 Error Classes](#error-classes)
- [📝 Guard Registry Functions](#guard-registry-functions)
- [📐 Type Definitions](#type-definitions)

---

## 📦 Module Overview

```python
from modgud import (
    # Primary decorators
    guarded_expression,
    implicit_return,

    # Guard validators (all available guards)
    not_none,
    not_empty,
    positive,
    in_range,
    type_check,
    matches_pattern,
    valid_file_path,
    valid_url,
    valid_enum,

    # Or import from CommonGuards class
    CommonGuards,

    # Errors
    GuardClauseError,
    ImplicitReturnError,
    ExplicitReturnDisallowedError,
    MissingImplicitReturnError,
    UnsupportedConstructError,

    # Guard registry
    register_guard,
    get_guard,
    has_custom_guard,
    list_custom_guards,
    list_guard_namespaces,
    unregister_guard,
    get_registry,
)
```

**Version**: 0.2.0
**Python**: 3.13+
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
    on_error: FailureBehavior = GuardClauseError,
    log: bool = False
) -> Callable[[Callable], Callable]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | - | Variable number of guard functions that validate input |
| `implicit_return` | `bool` | `True` | **⚠️ Deprecated:** Use separate `@implicit_return` decorator instead |
| `on_error` | `FailureBehavior` | `GuardClauseError` | Behavior when guard fails (see below) |
| `log` | `bool` | `False` | Log guard failures at INFO level |

#### on_error Options

The `on_error` parameter accepts:
- **Exception class**: Instantiated with error message and raised
- **Callable**: Called with `(error_msg, *args, **kwargs)`, return value used
- **Any value**: Returned directly on guard failure (e.g., `None`, `"error"`, `0`)

#### Returns

Decorated function with guard validation and optional implicit returns.

#### Raises

- `GuardClauseError`: Default exception when guards fail
- Custom exception if specified via `on_error`
- `UnsupportedConstructError`: If source unavailable with implicit returns

#### Examples

##### Basic Guard Validation

```python
from modgud import guarded_expression, not_none, positive

@guarded_expression(
    not_none("x"),
    positive("x")
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
from modgud import guarded_expression, positive

# Return None on failure
@guarded_expression(
    positive("amount"),
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
    positive("x"),
    on_error=log_and_default
)
def safe_divide(x):
    100 / x

safe_divide(-5)  # Prints error, returns 0
```

##### With Logging

```python
from modgud import guarded_expression, not_empty

@guarded_expression(
    not_empty("items"),
    log=True  # Enables logging
)
def process_items(items):
    len(items) * 10

process_items([])  # Logs: "INFO: Guard failed: items must not be empty"
```

##### Recommended Composition Pattern (New in v0.3.0)

```python
from modgud import guarded_expression, implicit_return, positive

# Recommended: Use separate decorators
@guarded_expression(positive("x"))
@implicit_return
def calculate(x):
    result = x * 2
    result

# Legacy (deprecated but functional)
@guarded_expression(positive("x"), implicit_return=True)  # ⚠️ Shows warning
def legacy_calculate(x):
    result = x * 2
    result
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
from modgud import implicit_return

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
from modgud import guarded_expression, implicit_return, not_none

@guarded_expression(not_none("user"))
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

- **Order Matters**: When composing with other decorators, `@implicit_return` should typically be the innermost (closest to the function)
- **Source Required**: Function source code must be available via `inspect.getsource()`
- **No Explicit Returns**: Functions cannot contain `return` statements when using `@implicit_return`
- **All Paths Must Yield**: Every execution path must end with an expression that produces a value

---

## 🧩 Pre-built Guard Functions

Pre-defined guard validators for common validation scenarios. These functions are imported directly from modgud.

All methods are static and return `GuardFunction` instances that can be used with `guarded_expression`.

#### Methods

##### not_empty

Ensures collection parameter is not empty.

```python
not_empty(param_name: str = 'parameter', position: Optional[int] = None) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (None = first arg)

**Example:**
```python
from modgud import guarded_expression, implicit_return, not_empty

@guarded_expression(not_empty("items"))
@implicit_return
def process(items):
    len(items)
```

---

##### not_none

Ensures parameter is not None.

```python
not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud import guarded_expression, implicit_return, not_none

@guarded_expression(not_none("user"))
@implicit_return
def greet(user):
    f"Hello, {user.name}"
```

---

##### positive

Ensures numeric parameter is positive (> 0).

```python
positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud import guarded_expression, implicit_return, positive

@guarded_expression(positive("amount"))
@implicit_return
def calculate_tax(amount):
    amount * 0.1
```

---

##### in_range

Ensures parameter is within specified range (inclusive).

```python
in_range(
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
from modgud import guarded_expression, implicit_return, in_range

@guarded_expression(in_range(1, 10, "rating"))
@implicit_return
def save_rating(rating):
    {"rating": rating}

save_rating(5)   # OK
save_rating(11)  # Raises: GuardClauseError
```

---

##### type_check

Ensures parameter is of expected type.

```python
type_check(
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
from modgud import guarded_expression, type_check

@guarded_expression(type_check(str, "name"))
def create_user(name):
    return {"name": name.upper()}

create_user("alice")  # OK
create_user(123)      # Raises: GuardClauseError
```

---

##### matches_pattern

Ensures string parameter matches regex pattern.

```python
matches_pattern(
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
from modgud import guarded_expression, matches_pattern

@guarded_expression(
    matches_pattern(r'^\d{3}-\d{3}-\d{4}$', "phone")
)
def save_phone(phone):
    return {"phone": phone}

save_phone("555-123-4567")  # OK
save_phone("invalid")        # Raises: GuardClauseError
```

---

##### valid_file_path

Validates file path with optional existence and type checks.

```python
valid_file_path(
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
@guarded_expression(
    valid_file_path("config_path", exists_required=True, is_file=True)
)
def load_config(config_path):
    with open(config_path) as f:
        return f.read()
```

---

##### valid_url

Validates URL format with optional scheme restrictions.

```python
valid_url(
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
@guarded_expression(
    valid_url("endpoint", schemes=['https'])
)
def fetch_data(endpoint):
    # Fetch from HTTPS endpoint
    return f"Fetching from {endpoint}"
```

---

##### valid_enum

Ensures parameter is valid enum member.

```python
valid_enum(
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

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@guarded_expression(
    valid_enum(Status, "status")
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

Functions for managing custom guard registration and retrieval.

### register_guard

Register a custom guard function.

```python
register_guard(
    name: str,
    guard_func: Callable[..., GuardFunction],
    namespace: str = 'default'
) -> None
```

**Example:**
```python
def positive_int(param_name="vector", position=0):
    def check(*args, **kwargs):
        value = kwargs.get(param_name, args[position] if position < len(args) else None)
        return (isinstance(value, int) and value > 0) or "Must be a positive integer"
    return check

register_guard("positive_int", positive_int, namespace="validators")
```

---

### get_guard

Retrieve a registered guard function.

```python
get_guard(name: str, namespace: str = 'default') -> Callable[..., GuardFunction]
```

**Example:**
```python
positive_int_guard = get_guard("positive_int", namespace="validators")

@guarded_expression(positive_int_guard("count"))
def process(count):
    return count * 2
```

---

### has_custom_guard

Check if a guard is registered.

```python
has_custom_guard(name: str, namespace: str = 'default') -> bool
```

---

### list_custom_guards

List all guards in a namespace.

```python
list_custom_guards(namespace: str = 'default') -> list[str]
```

---

### list_guard_namespaces

List all available namespaces.

```python
list_guard_namespaces() -> list[str]
```

---

### unregister_guard

Remove a registered guard.

```python
unregister_guard(name: str, namespace: str = 'default') -> None
```

---

### get_registry

Get the complete guard registry dictionary.

```python
get_registry() -> dict[str, dict[str, Callable]]
```

**Returns:** Dictionary mapping namespaces to guard names to guard functions.

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

### FailureBehavior

Type alias for `on_error` parameter options.

```python
FailureBehavior = Union[type[Exception], Callable[..., Any], Any]
```

Can be:
- Exception class to instantiate and raise
- Callable to invoke with error details
- Any other value to return directly

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
