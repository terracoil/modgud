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

# Errors, enum, and type alias
from modgud.domain.guarded_expr import GuardClauseError, GuardFailureEnum, GuardFunction
from modgud.domain.implicit_ret import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

# Guard validators (static methods on CommonGuards) + registry
from modgud.infrastructure.guarded_expr import CommonGuards, GuardRegistry
```

**Version**: 2.0.0
**Python**: 3.11+
**Zero Runtime Dependencies**: Uses only Python standard library

---

## 🎖️ Primary Decorators

### guarded_expression

Unified decorator combining guard clauses with optional implicit return transformation.

#### Signature

```python
# illustrative — signature only
guarded_expression(
  *guards: GuardFunction,
  implicit_return: bool = True,
  strategy: GuardFailureEnum = GuardFailureEnum.ERROR_RAISE,
  on_failure: Any = GuardClauseError,
  continuance: int = 0,
) -> Callable[[Callable], Callable]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | - | Variable number of guard functions that validate input |
| `implicit_return` | `bool` | `True` | Enable implicit return AST rewrite |
| `strategy` | `GuardFailureEnum` | `ERROR_RAISE` | How collected failures are dispatched (see below) |
| `on_failure` | `Any` | `GuardClauseError` | Payload paired with `strategy` |
| `continuance` | `int` | `0` | Extra guards to evaluate past the first failure |

#### GuardFailureEnum + on_failure pairings

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
  CommonGuards.not_none('x'),
  CommonGuards.positive('x'),
)
def calculate(x):
  x * 2


calculate(5)  # Returns: 10
# calculate(-1) raises GuardClauseError: x must be positive
# calculate(None) raises GuardClauseError: x cannot be None
```

##### Implicit Returns

```python
from modgud.app import guarded_expression


@guarded_expression()
def get_status(user):
  if user.is_active:
    'active'
  else:
    'inactive'


# No explicit return needed!
```

##### Custom Failure Handling

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.guarded_expr import CommonGuards


# Return None on failure
@guarded_expression(
  CommonGuards.positive('amount'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure=None,
)
def process_payment(amount):
  amount * 1.1  # Add tax


process_payment(-10)  # Returns: None


# Custom handler — receives errors as a list[str]
def log_and_default(errors, *args, **kwargs):
  print(f'Guards failed: {errors}')
  return 0


@guarded_expression(
  CommonGuards.positive('x'),
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=log_and_default,
)
def safe_divide(x):
  100 / x


safe_divide(-5)  # Prints errors, returns 0
```

##### Collecting Multiple Failures

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(
  CommonGuards.not_empty('name'),
  CommonGuards.positive('age', position=1),
  continuance=1,  # collect up to 1 + 1 = 2 failures
)
def register(name, age):
  {'name': name, 'age': age}


try:
  register('', -1)
except* Exception as eg:
  for err in eg.exceptions:
    print(err)
# Prints: name cannot be empty
# Prints: age must be positive
```

##### Usage Patterns (Both Fully Supported)

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards


# Pattern 1: Unified parameter (simple, all-in-one)
@guarded_expression(
  CommonGuards.positive('x'),
  implicit_return=True,  # Fully supported!
)
def calculate(x):
  result = x * 2
  result


# Pattern 2: Separate decorators (flexible, composable)
@guarded_expression(CommonGuards.positive('x'), implicit_return=False)
@implicit_return
def calculate_v2(x):
  result = x * 2
  result


# Both patterns are first-class citizens - choose based on your needs!
```

---

### implicit_return

Standalone decorator for expression-oriented programming that transforms the last expression in each code path into an implicit return value.

#### Signature

```python
# illustrative — signature only
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
    'premium' if is_premium else 'standard'
  else:
    'inactive'


classify_status(True, True)   # Returns: "premium"
classify_status(True, False)  # Returns: "standard"
classify_status(False, True)  # Returns: "inactive"
```

##### Composition with Guards

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.not_none('user'), implicit_return=False)
@implicit_return
def get_user_role(user):
  if user.is_admin:
    'admin'
  elif user.is_moderator:
    'moderator'
  else:
    'user'
```

##### Complex Control Flow

```python
from modgud.app import implicit_return


@implicit_return
def process_data(data, fallback_mode=False):
  try:
    if fallback_mode:
      data.get('simple_result', 'default')
    else:
      complex_processing(data)
  except ProcessingError:
    'error_occurred'
  except Exception:
    'unknown_error'
```

#### Notes

- **Two Valid Patterns**: Use the `implicit_return=True` parameter OR the separate `@implicit_return` decorator
- **Order Matters**: When stacking, put `@implicit_return` closest to the `def` and set `implicit_return=False` on the outer `@guarded_expression`
- **⚠️ Composition Warning**: Placing `@implicit_return` *outside* `@guarded_expression` may bypass guards
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
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(
  CommonGuards.positive('amount'),
  CommonGuards.not_none('user', position=1),
  implicit_return=True,  # All-in-one configuration
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
from functools import cache

from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards


@cache  # Other decorators can be stacked freely
@guarded_expression(
  CommonGuards.positive('amount'),
  CommonGuards.not_none('user', position=1),
  implicit_return=False,
)
@implicit_return  # Separate concern, closest to the def
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
# illustrative — the second stacking order can bypass guards
# ✅ CORRECT: Guards wrap the implicit-return transform
@guarded_expression(CommonGuards.positive('x'), implicit_return=False)
@implicit_return
def correct(x):
  x * 2


# ❌ WRONG: implicit_return outermost may bypass guards
@implicit_return
@guarded_expression(CommonGuards.positive('x'))
def problematic(x):
  x * 2
```

The incorrect order can cause guards to be bypassed due to how Python's `inspect.getsource()` works with decorated functions.

### Choosing Between Patterns

| Use Case | Recommended Pattern | Example |
|----------|-------------------|---------|
| Simple validation + implicit return | Unified parameter | `@guarded_expression(..., implicit_return=True)` |
| Complex decorator stacks | Separate decorators | `@cache @guarded_expression(..., implicit_return=False) @implicit_return` |
| Guards without implicit returns | Unified with `implicit_return=False` | `@guarded_expression(..., implicit_return=False)` |
| Conditional implicit returns | Separate decorators | Apply `@implicit_return` conditionally |
| Teaching/documentation | Unified parameter | Shows all features in one place |

---

## 🧩 Pre-built Guard Functions

Pre-defined guard validators for common validation scenarios. These are static methods on `CommonGuards`, imported from `modgud.infrastructure.guarded_expr`.

All methods are static and return `GuardFunction` instances that can be used with `guarded_expression`. Guard param resolution: value taken from `kwargs[param_name]` if present, else `args[position]`.

#### Methods

##### CommonGuards.not_empty

Ensures collection parameter is not empty.

```python
# illustrative — signature only
CommonGuards.not_empty(param_name: str = 'parameter', position: int | None = None) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (None = first arg)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.not_empty('items'))
def process(items):
  len(items)
```

---

##### CommonGuards.not_none

Ensures parameter is not None.

```python
# illustrative — signature only
CommonGuards.not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.not_none('user'))
def greet(user):
  f'Hello, {user.name}'
```

---

##### CommonGuards.positive

Ensures numeric parameter is positive (> 0).

```python
# illustrative — signature only
CommonGuards.positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.positive('amount'))
def calculate_tax(amount):
  amount * 0.1
```

---

##### CommonGuards.in_range

Ensures parameter is within specified range (inclusive).

```python
# illustrative — signature only
CommonGuards.in_range(
  min_val: int | float,
  max_val: int | float,
  param_name: str = 'parameter',
  position: int = 0,
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


@guarded_expression(CommonGuards.in_range(1, 10, 'rating'))
def save_rating(rating):
  {'rating': rating}


save_rating(5)  # OK
# save_rating(11) raises GuardClauseError: rating must be between 1 and 10
```

---

##### CommonGuards.type_check

Ensures parameter is of expected type.

```python
# illustrative — signature only
CommonGuards.type_check(
  expected_type: type,
  param_name: str = 'parameter',
  position: int = 0,
) -> GuardFunction
```

**Parameters:**
- `expected_type`: Expected type for the isinstance check
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.type_check(str, 'name'))
def create_user(name):
  {'name': name.upper()}


create_user('alice')  # OK
# create_user(123) raises GuardClauseError: name must be of type str
```

---

##### CommonGuards.matches_pattern

Ensures string parameter matches regex pattern.

```python
# illustrative — signature only
CommonGuards.matches_pattern(
  pattern: str,
  param_name: str = 'parameter',
  position: int = 0,
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


@guarded_expression(CommonGuards.matches_pattern(r'^\d{3}-\d{3}-\d{4}$', 'phone'))
def save_phone(phone):
  {'phone': phone}


save_phone('555-123-4567')  # OK
# save_phone('invalid') raises GuardClauseError
```

---

##### CommonGuards.valid_file_path

Validates a file path with optional existence and type checks.

```python
# illustrative — signature only
CommonGuards.valid_file_path(
  param_name: str = 'path',
  position: int = 0,
  must_exist: bool = True,
  must_be_file: bool = False,
  must_be_dir: bool = False,
) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)
- `must_exist`: Whether the path must exist (default: True)
- `must_be_file`: Whether the path must be a file (default: False)
- `must_be_dir`: Whether the path must be a directory (default: False)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(
  CommonGuards.valid_file_path('config_path', must_exist=True, must_be_file=True),
  implicit_return=False,
)
def load_config(config_path):
  with open(config_path) as f:
    return f.read()
```

---

##### CommonGuards.valid_url

Validates URL format, optionally requiring a scheme.

```python
# illustrative — signature only
CommonGuards.valid_url(
  param_name: str = 'url',
  position: int = 0,
  require_scheme: bool = True,
) -> GuardFunction
```

**Parameters:**
- `param_name`: Name of parameter in kwargs
- `position`: Position in args (default: 0)
- `require_scheme`: If True, the URL must include an http/https scheme (default: True)

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.valid_url('endpoint', require_scheme=True))
def fetch_data(endpoint):
  f'Fetching from {endpoint}'
```

---

##### CommonGuards.valid_enum

Ensures parameter is a valid enum member (or a string matching one of its values).

```python
# illustrative — signature only
CommonGuards.valid_enum(
  enum_class: type[Enum],
  param_name: str = 'parameter',
  position: int = 0,
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
  ACTIVE = 'active'
  INACTIVE = 'inactive'


@guarded_expression(CommonGuards.valid_enum(Status, 'status'))
def update_status(status):
  {'status': Status(status).value}


update_status(Status.ACTIVE)  # OK
update_status('active')       # OK — string matching a member value
# update_status('deleted') raises GuardClauseError
```

---

## 🚨 Error Classes

### GuardClauseError

Default exception raised when a guard clause fails under `ERROR_RAISE`.

```python
# illustrative — class definition
class GuardClauseError(Exception):
  pass
```

**Usage:** `on_failure=GuardClauseError` is the default, so `@guarded_expression(...)` raises it automatically:
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


@guarded_expression(CommonGuards.positive('x'))  # on_failure defaults to GuardClauseError
def needs_positive(x):
  x * 2
```

---

### ImplicitReturnError

Base class for implicit return transformation errors. Inherits from `SyntaxError`.

```python
# illustrative — class definition
class ImplicitReturnError(SyntaxError):
  def __init__(self, message: str, lineno: int | None = None, col_offset: int | None = None): ...
```

---

### ExplicitReturnDisallowedError

Raised when an explicit `return` statement is found in a function with implicit returns.

```python
# illustrative — class definition
class ExplicitReturnDisallowedError(ImplicitReturnError):
  pass
```

**Example:**
```python
# illustrative — raises ExplicitReturnDisallowedError at decoration time
@guarded_expression()
def invalid():
  if True:
    return 5  # Error! No explicit returns allowed
  else:
    0
```

---

### MissingImplicitReturnError

Raised when not all code paths yield a value.

```python
# illustrative — class definition
class MissingImplicitReturnError(ImplicitReturnError):
  pass
```

**Example:**
```python
# illustrative — raises MissingImplicitReturnError at decoration time
@guarded_expression()
def invalid(x):
  if x > 0:
    x * 2
  # Error! Missing else branch
```

---

### UnsupportedConstructError

Raised when transformation encounters an unsupported Python construct at tail position.

```python
# illustrative — class definition
class UnsupportedConstructError(ImplicitReturnError):
  pass
```

---

## 📝 Guard Registry Functions

Methods on `GuardRegistry` (imported from `modgud.infrastructure.guarded_expr`) for managing custom guard registration and retrieval. `CommonGuards` are auto-registered under the `'common'` namespace.

### GuardRegistry.register

Register a custom guard factory. A duplicate name in the same namespace raises `ValueError`.

```python
# illustrative — signature only
GuardRegistry.register(
  name: str,
  guard_factory: Callable[..., GuardFunction],
  namespace: str | None = None,
) -> None
```

**Example:**
```python
from modgud.infrastructure.guarded_expr import GuardRegistry


def positive_int(param_name='value', position=0):
  def check(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else None)
    return (isinstance(value, int) and value > 0) or 'Must be a positive integer'

  return check


GuardRegistry.register('positive_int', positive_int, namespace='validators')
```

---

### GuardRegistry.get

Retrieve a registered guard factory.

```python
# illustrative — signature only
GuardRegistry.get(name: str, namespace: str | None = None) -> Callable[..., GuardFunction] | None
```

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import GuardRegistry


def positive_int(param_name='value', position=0):
  def check(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else None)
    return (isinstance(value, int) and value > 0) or 'Must be a positive integer'

  return check


GuardRegistry.register('positive_int', positive_int, namespace='validators')
positive_int_guard = GuardRegistry.get('positive_int', namespace='validators')


@guarded_expression(positive_int_guard('count'))
def process(count):
  count * 2
```

---

### GuardRegistry.has_guard

Check if a guard is registered.

```python
# illustrative — signature only
GuardRegistry.has_guard(name: str, namespace: str | None = None) -> bool
```

---

### GuardRegistry.list_guards

List all guards in a namespace.

```python
# illustrative — signature only
GuardRegistry.list_guards(namespace: str | None = None) -> list[str]
```

---

### GuardRegistry.list_namespaces

List all available namespaces (includes `'common'` for the built-in `CommonGuards`).

```python
# illustrative — signature only
GuardRegistry.list_namespaces() -> list[str]
```

---

### GuardRegistry.unregister

Remove a registered guard.

```python
# illustrative — signature only
GuardRegistry.unregister(name: str, namespace: str | None = None) -> bool
```

---

### GuardRegistry.instance

Get the singleton guard registry instance.

```python
# illustrative — signature only
GuardRegistry.instance() -> GuardRegistry
```

**Returns:** The global `GuardRegistry` singleton.

---

## 📐 Type Definitions

### GuardFunction

Type alias for guard validation functions.

```python
# illustrative — type alias
GuardFunction = Callable[..., bool | str]
```

A guard function:
- Receives `(*args, **kwargs)` from the decorated function
- Returns `True` if validation passes
- Returns an error-message string if validation fails

---

### GuardFailureEnum

Enum selecting how collected failures are dispatched. See the `guarded_expression` section above for the strategy × `on_failure` pairing table.

```python
# illustrative — enum definition
class GuardFailureEnum(IntEnum):
  ERROR_RAISE = auto()
  ERROR_RETURN = auto()
  RETURN_VALUE = auto()
  CALL_HANDLER = auto()
```

The `CALL_HANDLER` strategy invokes `on_failure(errors, *args, **kwargs)`, where `errors` is always a `list[str]` of the collected failure messages, `args`/`kwargs` are the original call arguments, and the return value becomes the decorated function's result.

---

[← Back to Documentation Hub](README.md) | [← How It Works](how-it-works.md)
