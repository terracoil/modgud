# API Reference

[← Back to Documentation Hub](README.md)

Complete API reference for the modgud library, covering all decorators, classes, functions, and types.

---

## Table of Contents

- [Module Overview](#module-overview)
- [Primary Decorator](#primary-decorator)
  - [guarded_expression](#guarded_expression)
- [Classes](#classes)
  - [CommonGuards](#commonguards)
- [Error Classes](#error-classes)
- [Guard Registry Functions](#guard-registry-functions)
- [Type Definitions](#type-definitions)

---

## Module Overview

```python
from modgud import (
    # Primary decorator
    guarded_expression,

    # Guard validators
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
**Python**: 3.7+

---

## Primary Decorator

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
| `implicit_return` | `bool` | `True` | Enable implicit return transformation |
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
from modgud import guarded_expression, CommonGuards

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
@guarded_expression(
    CommonGuards.not_empty("items"),
    log=True  # Enables logging
)
def process_items(items):
    len(items) * 10

process_items([])  # Logs: "INFO: Guard failed: items must not be empty"
```

---

## Classes

### CommonGuards

Pre-defined guard validators for common validation scenarios.

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
@guarded_expression(CommonGuards.not_empty("items"))
def process(items):
    return len(items)
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
@guarded_expression(CommonGuards.not_none("user"))
def greet(user):
    return f"Hello, {user.name}"
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
@guarded_expression(CommonGuards.positive("amount"))
def calculate_tax(amount):
    return amount * 0.1
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
@guarded_expression(CommonGuards.in_range(1, 10, "rating"))
def save_rating(rating):
    return {"rating": rating}

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
@guarded_expression(CommonGuards.type_check(str, "name"))
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
@guarded_expression(
    CommonGuards.matches_pattern(r'^\d{3}-\d{3}-\d{4}$', "phone")
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
    CommonGuards.valid_file_path("config_path", exists_required=True, is_file=True)
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
    CommonGuards.valid_url("endpoint", schemes=['https'])
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
    CommonGuards.valid_enum(Status, "status")
)
def update_status(status):
    return {"status": status.value}

update_status(Status.ACTIVE)  # OK
update_status("active")       # Raises: GuardClauseError
```

---

## Error Classes

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

## Guard Registry Functions

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
def positive_int(param_name="value", position=0):
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

## Type Definitions

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