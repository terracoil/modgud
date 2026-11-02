**Parent**: [🌉 Main README](../README.md) | [📖 API Reference](api-reference.md) | [⚙️ How It Works](how-it-works.md)

> **v2 surface.** The current decorator signature is
> `guarded_expression(*guards, implicit_return=True, strategy=GuardFailureEnum.ERROR_RAISE, on_failure=GuardClauseError, continuance=0)`.
> The pre-2.0 `on_error` / `log` parameters were removed. See [`api-reference.md`](api-reference.md) for the full contract.

# MODGUD Technical Documentation Hub

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## 📋 Table of Contents

This document contains:
- [🗺️ Overview](#overview) - What modgud is and why it exists
- [📦 Installation](#installation) - Getting started with modgud
- [💻 Usage Examples](#usage-examples) - Practical code examples
  - [Basic Guard Usage](#basic-guard-usage)
  - [Implicit Returns](#implicit-returns)
  - [Explicit Returns](#explicit-returns)
  - [Failure Handling Strategies](#failure-handling-strategies)
  - [Pre-built Guards Usage](#pre-built-guards-usage)
  - [Advanced Patterns](#advanced-patterns)
- [🎨 Implicit Return Semantics](#implicit-return-semantics) - How implicit returns work
  - [If/Else Statements](#ifelse-statements)
  - [Try/Except Blocks](#tryexcept-blocks)
  - [Match/Case Statements](#matchcase-statements)
  - [Rules and Restrictions](#rules-and-restrictions)
- [✍️ Guard Function Signature](#guard-function-signature) - Writing custom guards
- [⚙️ Configuration Options](#configuration-options) - Decorator parameters
- [🧪 Testing Considerations](#testing-considerations) - Testing with modgud
- [🔄 Upgrading from Pre-2.0 Code](#upgrading-from-pre-20-code) - Mapping old snippets forward
- [🏛️ Architecture Details](#architecture-details) - Design principles

> **Looking for specific API details?** See the [Complete API Reference](api-reference.md) for detailed documentation of all functions and classes.

## 🗺️ Overview

**modgud** is a Python library that brings expression-oriented programming, single return point architecture, and guard clause decorators to Python 3.11+. It provides a clean, functional approach to validation and control flow that eliminates defensive coding clutter while maintaining code clarity and maintainability.

### What is modgud?

At its core, modgud provides the `guarded_expression` decorator, which combines two powerful programming concepts:

1. **Guard Clauses**: Validation checks at function entry that fail fast when preconditions aren't met
2. **Implicit Returns**: Expression-oriented programming where the last expression in each branch automatically becomes the return value

### Why modgud Exists

Python developers often struggle with:

- **Defensive Programming Clutter**: Functions filled with validation checks that obscure business logic
- **Multiple Return Points**: Early returns for validation make code flow harder to follow
- **Nested Conditionals**: Deep nesting from validation checks reduces readability
- **Boilerplate Code**: Repetitive validation patterns across functions
- **Inconsistent Error Handling**: Different approaches to validation failures across a codebase

modgud solves these problems by:

- Moving validation to the function boundary via decorators
- Enforcing single return point architecture
- Enabling expression-oriented programming (like Ruby, Rust, Scala)
- Providing composable, reusable guard functions
- Standardizing failure handling through a single strategy enum

## 📦 Installation

### Using Poetry (Recommended)

```bash
poetry add modgud
```

### Using pip

```bash
pip install modgud
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/terracoil/modgud.git
cd modgud

# Install with Poetry including development dependencies
poetry install --with dev

# Or install with pip in development mode
pip install -e ".[dev]"
```

### Requirements

- Python 3.11 or higher
- One runtime dependency: [Idunn](https://pypi.org/project/idunn), for port/adapter wiring


Below is a quick overview. For detailed documentation including all parameters, return values, and examples, see the [full API reference](api-reference.md).

### guarded_expression Decorator

The primary API for modgud, providing unified guard validation and implicit return functionality.

```python
# illustrative — signature only
guarded_expression(
  *guards,
  implicit_return=True,
  strategy=GuardFailureEnum.ERROR_RAISE,
  on_failure=GuardClauseError,
  continuance=0,
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | `()` | Variable number of guard functions that validate inputs |
| `implicit_return` | `bool` | `True` | Enable implicit return transformation |
| `strategy` | `GuardFailureEnum` | `ERROR_RAISE` | How collected failures are dispatched |
| `on_failure` | `Any` | `GuardClauseError` | Payload paired with `strategy` |
| `continuance` | `int` | `0` | Extra guards to evaluate past the first failure |

#### Parameter Details

**`*guards`**: Zero or more guard functions. Each guard is a callable that:
- Accepts `(*args, **kwargs)` matching the decorated function's signature
- Returns `True` if validation passes
- Returns a string error message if validation fails
- Guards are evaluated in order; `continuance` controls how many are checked past the first failure

**`implicit_return`**: Controls return behavior:
- `True` (default): Last expression in each branch is auto-returned; explicit `return` statements are forbidden
- `False`: Traditional Python behavior; explicit `return` required as last statement

**`strategy`** + **`on_failure`**: Together they decide what happens once one or more guards fail:
- `ERROR_RAISE` (default): raise `on_failure(message)`; multiple collected failures raise an `ExceptionGroup('Guards failed', [...])`
- `ERROR_RETURN`: build the same exception instance(s) but *return* them instead of raising
- `RETURN_VALUE`: return `on_failure` exactly as given (any value, e.g. `None`, `False`, a dict)
- `CALL_HANDLER`: return `on_failure(errors, *args, **kwargs)`, where `errors` is always a `list[str]`

**`continuance`**: Failure-collection budget:
- `0` (default): stop at the first failing guard
- `N > 0`: keep evaluating and collect up to `1 + N` failures before dispatching them through `strategy`

#### Return Value

Returns a decorated function that:
1. Evaluates guards before function execution
2. Handles failures according to `strategy` / `on_failure`
3. Transforms the function for implicit returns if enabled
4. Preserves original function metadata (`__name__`, `__doc__`, etc.)

### Pre-built Guard Validators

Pre-built guard validators for common validation scenarios.

#### not_none

```python
# illustrative — signature only
CommonGuards.not_none(param_name='parameter', position=0) -> GuardFunction
```

Ensures parameter is not None.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.not_none('user_id'))
def get_user(user_id):
  # user_id guaranteed not None
  fetch_from_db(user_id)
```

#### not_empty

```python
# illustrative — signature only
CommonGuards.not_empty(param_name='parameter', position=None) -> GuardFunction
```

Ensures collection/string parameter is not empty.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int \| None` | `None` | Position in args tuple (None = first arg) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.not_empty('items', position=1))
def process_list(user, items):
  # items guaranteed to have length > 0
  [process(item) for item in items]
```

#### positive

```python
# illustrative — signature only
CommonGuards.positive(param_name='parameter', position=0) -> GuardFunction
```

Ensures numeric parameter is positive (> 0).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.positive('amount'))
def calculate_tax(amount):
  # amount guaranteed > 0
  amount * 0.08
```

#### in_range

```python
# illustrative — signature only
CommonGuards.in_range(min_val, max_val, param_name='parameter', position=0) -> GuardFunction
```

Ensures parameter is within inclusive range [min_val, max_val].

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_val` | `float` | - | Minimum value (inclusive) |
| `max_val` | `float` | - | Maximum value (inclusive) |
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.in_range(1, 100, 'page'))
def get_page(page):
  # page guaranteed between 1 and 100
  fetch_page_data(page)
```

#### type_check

```python
# illustrative — signature only
CommonGuards.type_check(expected_type, param_name='parameter', position=0) -> GuardFunction
```

Ensures parameter matches expected type.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `expected_type` | `type` | - | Expected type for isinstance check |
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.type_check(dict, 'config'))
def load_config(config):
  # config guaranteed to be a dict
  {**defaults, **config}
```

#### matches_pattern

```python
# illustrative — signature only
CommonGuards.matches_pattern(pattern, param_name='parameter', position=0) -> GuardFunction
```

Ensures string parameter matches regex pattern.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern` | `str` | - | Regular expression pattern |
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.matches_pattern(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', 'email')
)
def send_email(email):
  # email guaranteed to match email pattern
  smtp_client.send(email)
```

### 🚨 Error Classes

#### GuardClauseError

```python
# illustrative — class definition
class GuardClauseError(Exception):
  """Raised when guard clause validation fails."""
```

Default exception raised when guards fail under `ERROR_RAISE` (the default `on_failure` is the `GuardClauseError` class).

**Example:**
```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.positive('x'))
def needs_positive(x):
  x * 2


try:
  needs_positive(-5)  # Negative when positive required
except GuardClauseError as e:
  print(f'Validation failed: {e}')
```

#### ImplicitReturnError

```python
# illustrative — class definition
class ImplicitReturnError(SyntaxError):
  """Base class for implicit return transformation errors."""
```

Base exception for all implicit return transformation errors. Subclasses provide specific error types.

#### ExplicitReturnDisallowedError

```python
# illustrative — class definition
class ExplicitReturnDisallowedError(ImplicitReturnError):
  """Raised when explicit return found with implicit_return=True."""
```

Raised during function transformation when an explicit `return` statement is found in a function decorated with `implicit_return=True`.

**Example:**
```python
# illustrative — raises ExplicitReturnDisallowedError at decoration time
@guarded_expression()  # implicit_return=True by default
def bad_function(x):
  return x * 2  # ERROR: explicit return not allowed
```

#### MissingImplicitReturnError

```python
# illustrative — class definition
class MissingImplicitReturnError(ImplicitReturnError):
  """Raised when a code branch doesn't produce a value for implicit return."""
```

Raised when a code branch at tail position doesn't produce a value (e.g., missing else clause).

**Example:**
```python
# illustrative — raises MissingImplicitReturnError at decoration time
@guarded_expression()
def incomplete(x):
  if x > 0:
    x * 2
  # ERROR: missing else clause at tail position
```

#### UnsupportedConstructError

```python
# illustrative — class definition
class UnsupportedConstructError(ImplicitReturnError):
  """Raised when an unsupported AST construct is found at tail position."""
```

Raised when the AST transformer encounters an unsupported construct at tail position (e.g., `with` statements, `async for`, etc.).

## 💻 Usage Examples

### Basic Guard Usage

#### Simple Validation

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError


@guarded_expression(
  lambda *args, **kwargs: args[0] > 0 or 'x must be positive',
  lambda *args, **kwargs: args[0] < 100 or 'x must be less than 100',
)
def process_value(x):
  result = x * 2 + 10
  result  # Implicit return


# Success case
print(process_value(5))  # Returns 20

# Failure case - raises GuardClauseError
try:
  process_value(-5)
except GuardClauseError as e:
  print(e)  # "x must be positive"
```

Custom lambda guards receive the *full* argument tuple, so they read `args[0]` (or a kwarg) rather than declaring a single named parameter.

#### Multiple Parameters

```python
from modgud.app import guarded_expression


@guarded_expression(
  lambda *args, **kwargs: args[0] > 0 or 'x must be positive',
  lambda *args, **kwargs: args[1] > 0 or 'y must be positive',
  lambda *args, **kwargs: args[0] != args[1] or 'x and y must be different',
)
def calculate_ratio(x, y):
  x / y
```

### Implicit Returns

#### Basic Implicit Return

```python
from modgud.app import guarded_expression


@guarded_expression()  # No guards, just implicit return
def double(x):
  x * 2  # Last expression is returned


print(double(5))  # Returns 10
```

#### Implicit Return with Conditionals

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.not_none('value'))
def classify_number(value):
  if value > 0:
    'positive'
  elif value < 0:
    'negative'
  else:
    'zero'


print(classify_number(5))   # Returns "positive"
print(classify_number(-3))  # Returns "negative"
print(classify_number(0))   # Returns "zero"
```

#### Complex Expressions

```python
from modgud.app import guarded_expression


@guarded_expression()
def process_data(data):
  cleaned = data.strip().lower()
  tokens = cleaned.split()
  filtered = [t for t in tokens if len(t) > 2]
  ' '.join(filtered)  # Implicit return of joined string
```

### Explicit Returns

When you need traditional Python return behavior:

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.positive('x'),
  implicit_return=False,  # Disable implicit returns
)
def calculate(x):
  result = x * 2
  intermediate = result + 10
  final = intermediate / 2
  return final  # Explicit return required


print(calculate(5))  # Returns 10.0
```

### Failure Handling Strategies

Every failure mode is selected by the `strategy` argument (a `GuardFailureEnum`) paired with an `on_failure` payload.

#### Return Custom Values (`RETURN_VALUE`)

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


# Return None on failure
@guarded_expression(
  CommonGuards.positive('x'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure=None,
)
def safe_sqrt(x):
  x ** 0.5


print(safe_sqrt(4))  # Returns 2.0
print(safe_sqrt(-1))  # Returns None


# Return error dict on failure
@guarded_expression(
  CommonGuards.not_empty('data'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure={'success': False, 'error': 'Invalid input'},
)
def process_data(data):
  {'success': True, 'result': data.upper()}


print(process_data('hello'))  # Returns {'success': True, 'result': 'HELLO'}
print(process_data(''))  # Returns {'success': False, 'error': 'Invalid input'}
```

#### Custom Exception Classes (`ERROR_RAISE`)

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class ValidationError(Exception):
  """Custom validation exception."""


@guarded_expression(
  CommonGuards.positive('amount'),
  on_failure=ValidationError,
)
def withdraw(amount):
  {'withdrawn': amount, 'timestamp': '2024-01-01'}


try:
  withdraw(-100)
except ValidationError as e:
  print(f'Validation failed: {e}')
```

#### Handler Functions (`CALL_HANDLER`)

The handler is invoked as `on_failure(errors, *args, **kwargs)`, where `errors` is always a `list[str]`:

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


def log_and_default(errors, *args, **kwargs):
  """Log the collected errors and return a default value."""
  print(f'Guards failed: {errors}')
  print(f'Args: {args}, Kwargs: {kwargs}')
  return {'error': True, 'messages': errors}


@guarded_expression(
  CommonGuards.in_range(1, 10, 'level'),
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=log_and_default,
)
def set_level(level):
  {'level': level, 'success': True}


set_level(15)
# Prints: Guards failed: ['level must be between 1 and 10']
# Prints: Args: (15,), Kwargs: {}
# Returns: {'error': True, 'messages': ['level must be between 1 and 10']}
```

### Pre-built Guards Usage

#### Parameter Extraction

Guard validators intelligently extract parameters from both positional and keyword arguments (value taken from `kwargs[param_name]` if present, else `args[position]`):

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.not_none('user_id'),                 # First positional or kwargs['user_id']
  CommonGuards.positive('amount', position=1),      # Second positional or kwargs['amount']
  CommonGuards.not_empty('description', position=2),  # Third positional
)
def create_transaction(user_id, amount, description=''):
  {'user': user_id, 'amount': amount, 'desc': description}


# Works with positional arguments
create_transaction(123, 50.0, 'Payment')

# Works with keyword arguments
create_transaction(user_id=123, amount=50.0, description='Payment')

# Mixed arguments
create_transaction(123, amount=50.0, description='Payment')
```

#### Combining Multiple Guards

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  # User validation
  CommonGuards.not_none('email'),
  CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email'),
  # Age validation
  CommonGuards.type_check(int, 'age', position=1),
  CommonGuards.in_range(13, 120, 'age', position=1),
  # Password validation
  CommonGuards.not_empty('password', position=2),
)
def register_user(email, age, password):
  user = {
    'email': email,
    'age': age,
    'password_hash': hash_password(password),
  }
  save_to_db(user)
  user
```

#### Collecting Multiple Failures with `continuance`

By default a guarded function stops at the first failing guard. Set `continuance` to collect more, which surfaces every problem at once as an `ExceptionGroup`:

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.not_empty('email'),
  CommonGuards.type_check(int, 'age', position=1),
  CommonGuards.not_empty('password', position=2),
  continuance=2,  # collect up to 1 + 2 = 3 failures
)
def register(email, age, password):
  {'email': email, 'age': age}


try:
  register('', 'not-an-int', '')
except* Exception as eg:
  for err in eg.exceptions:
    print(err)
```

### Advanced Patterns

#### Composable Guard Sets

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


# Define reusable guard combinations (guards accept the full argument tuple)
pagination_guards = [
  CommonGuards.in_range(1, 1_000_000, 'page', position=1),
  CommonGuards.in_range(1, 100, 'limit', position=2),
]

auth_guards = [
  CommonGuards.not_none('api_key'),
  lambda *args, **kwargs: validate_api_key(kwargs.get('api_key', args[0] if args else None))
  or 'Invalid API key',
]


@guarded_expression(*auth_guards, *pagination_guards)
def get_user_posts(api_key, page=1, limit=10):
  posts = fetch_posts(page, limit)
  {'posts': posts, 'page': page, 'count': len(posts)}
```

#### Dynamic Guard Generation

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


def max_length(max_len, param_name='param', position=0):
  """Create a guard for maximum string length."""
  def check_length(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else '')
    return len(str(value)) <= max_len or f'{param_name} exceeds max length {max_len}'

  return check_length


@guarded_expression(
  CommonGuards.not_empty('username'),
  max_length(20, 'username'),
  max_length(100, 'bio', position=1),
)
def create_profile(username, bio=''):
  {'username': username, 'bio': bio}
```

#### Conditional Guards

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


def conditional_guard(condition, guard):
  """Apply guard only if condition is met."""
  def check(*args, **kwargs):
    result = True
    if condition(*args, **kwargs):
      result = guard(*args, **kwargs)
    return result

  return check


@guarded_expression(
  CommonGuards.not_none('data'),
  conditional_guard(
    lambda *args, **kwargs: kwargs.get('validate', False),
    CommonGuards.type_check(dict, 'data'),
  ),
)
def process(data, validate=False):
  if validate:
    {'validated': True, 'data': data}
  else:
    {'validated': False, 'data': data}


# Without validation - accepts any non-None type
process('string data', validate=False)

# With validation - requires dict
process({'key': 'value'}, validate=True)
```

## 🎨 Implicit Return Semantics

Implicit return transforms functions to automatically return the last expression in each code branch, similar to languages like Ruby, Rust, and Scala.

### If/Else Statements

#### Basic If/Else

```python
from modgud.app import guarded_expression


@guarded_expression()
def sign(x):
  if x > 0:
    1
  elif x < 0:
    -1
  else:
    0


print(sign(5))   # Returns 1
print(sign(-3))  # Returns -1
print(sign(0))   # Returns 0
```

#### Nested Conditionals

```python
from modgud.app import guarded_expression


@guarded_expression()
def categorize(value, threshold=10):
  if isinstance(value, (int, float)):
    if value > threshold:
      'high'
    else:
      'low'
  else:
    'invalid'
```

#### Required Else Clause

At tail position (the end of the function), if statements must have an else clause:

```python
# illustrative — the first function raises MissingImplicitReturnError
@guarded_expression()
def bad_conditional(x):
  if x > 0:
    'positive'
  # MissingImplicitReturnError - no value for x <= 0


# CORRECT: All branches covered
@guarded_expression()
def good_conditional(x):
  if x > 0:
    'positive'
  else:
    'non-positive'
```

### Try/Except Blocks

#### Basic Try/Except

```python
from modgud.app import guarded_expression


@guarded_expression()
def safe_divide(x, y):
  try:
    x / y
  except ZeroDivisionError:
    float('inf')
  except TypeError:
    None


print(safe_divide(10, 2))    # Returns 5.0
print(safe_divide(10, 0))    # Returns inf
print(safe_divide(10, 'a'))  # Returns None
```

#### Try/Except/Else/Finally

```python
from modgud.app import guarded_expression


@guarded_expression()
def robust_operation(data):
  try:
    parsed = process(data)
    parsed  # the try body must end in an expression
  except ValueError:
    {'error': 'invalid value'}
  except Exception as e:
    {'error': str(e)}
  else:
    {'success': True, 'result': parsed}  # else replaces the try-body value on success
```

#### Nested Try Blocks

```python
from modgud.app import guarded_expression


@guarded_expression()
def nested_safety(x, y):
  try:
    try:
      x / y
    except ZeroDivisionError:
      try:
        y / x
      except ZeroDivisionError:
        0
  except Exception:
    None
```

### Match/Case Statements

Python 3.10+ pattern matching is fully supported:

```python
from modgud.app import guarded_expression


@guarded_expression()
def process_command(command):
  match command:
    case ['move', x, y]:
      {'action': 'move', 'x': x, 'y': y}
    case ['rotate', angle]:
      {'action': 'rotate', 'angle': angle}
    case ['stop', factor]:
      {'action': 'stop', 'factor': factor}
    case _:
      {'action': 'unknown', 'command': command}


print(process_command(['move', 10, 20]))
# Returns: {'action': 'move', 'x': 10, 'y': 20}

print(process_command(['rotate', 90]))
# Returns: {'action': 'rotate', 'angle': 90}

print(process_command(['invalid']))
# Returns: {'action': 'unknown', 'command': ['invalid']}
```

#### Pattern Matching with Guards

```python
from modgud.app import guarded_expression


@guarded_expression()
def classify_point(point):
  match point:
    case (0, 0):
      'origin'
    case (x, 0) if x > 0:
      'positive x-axis'
    case (x, 0) if x < 0:
      'negative x-axis'
    case (0, y) if y > 0:
      'positive y-axis'
    case (0, y) if y < 0:
      'negative y-axis'
    case (x, y) if x > 0 and y > 0:
      'quadrant I'
    case (x, y) if x < 0 and y > 0:
      'quadrant II'
    case (x, y) if x < 0 and y < 0:
      'quadrant III'
    case (x, y) if x > 0 and y < 0:
      'quadrant IV'
    case _:
      'unknown'
```

### Rules and Restrictions

#### No Explicit Returns

With `implicit_return=True` (default), explicit return statements are forbidden:

```python
# illustrative — the first function raises ExplicitReturnDisallowedError
@guarded_expression()
def with_explicit_return(x):
  if x > 0:
    return x * 2  # ERROR!
  else:
    x * 3


# CORRECT: Use expressions only
@guarded_expression()
def without_explicit_return(x):
  if x > 0:
    x * 2
  else:
    x * 3
```

#### All Branches Must Produce Values

Every code path must result in an expression:

```python
# illustrative — the first function raises MissingImplicitReturnError
@guarded_expression()
def bad_loop(items):
  for item in items:
    process(item)  # ERROR: loops don't return values


# CORRECT: Use list comprehension (produces a value)
@guarded_expression()
def good_loop(items):
  [process(item) for item in items]
```

#### Nested Functions

Nested functions within an implicit return function CAN use explicit returns:

```python
from modgud.app import guarded_expression


@guarded_expression()
def outer(x):
  def inner(y):
    # Explicit return OK in nested function
    result = y * 2 if y > 0 else y * 3
    return result

  inner(x) + 10  # Implicit return in outer
```

#### Unsupported Constructs

The following constructs cannot appear at tail position (end of function):

- `for` loops
- `while` loops
- `with` statements
- `async for` loops
- `async with` statements
- standalone `pass`, `break`, `continue`
- `assert` statements
- `del` statements
- `global`/`nonlocal` declarations

These can still be used elsewhere in the function:

```python
from modgud.app import guarded_expression


@guarded_expression()
def process_file(filename):
  # with statement OK here (not at tail)
  with open(filename) as f:
    data = f.read()

  # Process data
  cleaned = data.strip().upper()

  # Implicit return at tail position
  cleaned.split()
```

## ✍️ Guard Function Signature

### Basic Guard Structure

A guard function is any callable that:
1. Accepts the same arguments as the decorated function (`*args, **kwargs`)
2. Returns `True` if validation passes
3. Returns a string error message if validation fails

```python
def my_guard(*args, **kwargs):
  # Validation logic
  result = True
  if not condition_met(*args):
    result = 'Error message describing the failure'
  return result
```

### Simple Guards

Because a guard receives the *entire* argument tuple, read the value you want by position or by keyword:

```python
from modgud.app import guarded_expression


def is_even(*args, **kwargs):
  return args[0] % 2 == 0 or 'Value must be even'


@guarded_expression(
  lambda *args, **kwargs: args[0] > 0 or 'Must be positive',
  is_even,
)
def process(x):
  x / 2
```

### Guards with Multiple Parameters

```python
from modgud.app import guarded_expression


def sum_less_than_100(*args, **kwargs):
  total = args[0] + args[1]
  return total < 100 or f'Sum {total} exceeds maximum of 100'


@guarded_expression(sum_less_than_100)
def add_limited(x, y):
  x + y
```

### Guards with Keyword Arguments

```python
from modgud.app import guarded_expression


def validate_config(*args, **kwargs):
  result = True
  if 'timeout' in kwargs and kwargs['timeout'] <= 0:
    result = 'Timeout must be positive'
  elif 'api_key' not in kwargs:
    result = 'api_key is required'
  return result


@guarded_expression(validate_config)
def api_call(endpoint, **kwargs):
  make_request(endpoint, **kwargs)
```

### Parameterized Guard Factories

```python
from modgud.app import guarded_expression


def min_length(min_len):
  """Factory that creates a minimum length guard."""
  def check_length(*args, **kwargs):
    value = args[0] if args else ''
    return len(value) >= min_len or f'Must be at least {min_len} characters'

  return check_length


def max_value(limit):
  """Factory that creates a maximum value guard."""
  def check_max(*args, **kwargs):
    value = args[0] if args else 0
    return value <= limit or f'Value {value} exceeds limit {limit}'

  return check_max


@guarded_expression(
  min_length(3),
  max_value(100),
)
def constrained_process(value):
  value * 2
```

### Stateful Guards

Guards can maintain state (though this should be used carefully):

```python
from modgud.app import guarded_expression


class RateLimitGuard:
  def __init__(self, max_calls=10):
    self.calls = 0
    self.max_calls = max_calls

  def __call__(self, *args, **kwargs):
    self.calls += 1
    return self.calls <= self.max_calls or f'Rate limit exceeded: {self.calls}/{self.max_calls}'


rate_limiter = RateLimitGuard(max_calls=5)


@guarded_expression(rate_limiter)
def limited_operation(data):
  process(data)
```

### Async Guards

For async functions, guards are still synchronous (evaluated before the async function runs). Pair them with `implicit_return=False` so the async body keeps its explicit `return`:

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.not_none('url'),
  lambda *args, **kwargs: str(kwargs.get('url', args[0] if args else '')).startswith('https://')
  or 'URL must use HTTPS',
  implicit_return=False,
)
async def fetch_secure(url):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      return await response.text()
```

## ⚙️ Configuration Options

### Decorator Parameters Summary

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | `()` | Guard validation functions |
| `implicit_return` | `bool` | `True` | Enable implicit returns |
| `strategy` | `GuardFailureEnum` | `ERROR_RAISE` | How collected failures are dispatched |
| `on_failure` | `Any` | `GuardClauseError` | Payload paired with `strategy` |
| `continuance` | `int` | `0` | Extra guards to evaluate past the first failure |

### Common Configuration Patterns

#### Validation-Only (No Implicit Returns)

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.positive('x'),
  implicit_return=False,
)
def validate_only(x):
  # Traditional Python with guards
  result = x * 2
  return result
```

#### Expression-Oriented (No Guards)

```python
from modgud.app import guarded_expression


@guarded_expression()  # All defaults
def expression_oriented(x):
  # Pure implicit return, no validation
  x * 2 + 10
```

#### Safe Operations (Return Default on Failure)

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards

DEFAULT_USER = {'id': 0, 'name': 'Guest'}


@guarded_expression(
  CommonGuards.positive('user_id'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure=DEFAULT_USER,
)
def get_user(user_id):
  fetch_from_database(user_id)
```

#### Audit Trail (Custom Handler)

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


def audit_handler(errors, *args, **kwargs):
  audit_log.write(f'Failed: {errors}, Args: {args}')
  return None


@guarded_expression(
  CommonGuards.not_none('sensitive_data'),
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=audit_handler,
)
def sensitive_operation(sensitive_data):
  process_sensitive(sensitive_data)
```

#### API Response Pattern

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.type_check(dict, 'payload'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure={'status': 400, 'error': 'Invalid request'},
)
def api_endpoint(payload):
  result = process_request(payload)
  {'status': 200, 'data': result}
```

## 🧪 Testing Considerations

### Module-Level Functions for Implicit Returns

Functions using `implicit_return=True` must be defined at module level because `inspect.getsource()` cannot extract source from nested functions:

```python
# test_fixtures.py - Define test functions here
from modgud.app import guarded_expression


@guarded_expression()
def fixture_with_implicit(x):
  if x > 0:
    'positive'
  else:
    'non-positive'
```

```python
# illustrative — imports the sibling test_fixtures module shown above
from test_fixtures import fixture_with_implicit


def test_implicit_return():
  assert fixture_with_implicit(5) == 'positive'
  assert fixture_with_implicit(-5) == 'non-positive'
```

### Testing Guard Failures

```python
import pytest

from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError
from modgud.infrastructure.common import CommonGuards


@guarded_expression(CommonGuards.positive('x'))
def needs_positive(x):
  x * 2


def test_guard_success():
  assert needs_positive(5) == 10


def test_guard_failure():
  with pytest.raises(GuardClauseError, match='must be positive'):
    needs_positive(-5)
```

### Testing Different Failure Strategies

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.not_none('value'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure=None,
)
def returns_none_on_failure(value):
  value.upper()


@guarded_expression(
  CommonGuards.not_none('value'),
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure={'error': True},
)
def returns_dict_on_failure(value):
  {'result': value.upper()}


def test_none_strategy():
  assert returns_none_on_failure(None) is None
  assert returns_none_on_failure('hello') == 'HELLO'


def test_dict_strategy():
  assert returns_dict_on_failure(None) == {'error': True}
  assert returns_dict_on_failure('hello') == {'result': 'HELLO'}
```

### Testing Custom Guards

```python
import pytest

from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError


def custom_guard(*args, **kwargs):
  x, y = args[0], args[1]
  return x < y or f'x ({x}) must be less than y ({y})'


@guarded_expression(custom_guard)
def compare(x, y):
  y - x


def test_custom_guard():
  assert compare(3, 5) == 2
  with pytest.raises(GuardClauseError, match=r'x \(5\) must be less than y \(3\)'):
    compare(5, 3)
```

### Verifying Guard Evaluation Order

By default guards stop at the first failure, so later guards never run. `continuance` widens that window when you want to collect more:

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError
from modgud.infrastructure.common import CommonGuards


@guarded_expression(
  CommonGuards.positive('x'),          # fails first for x <= 0
  CommonGuards.in_range(1, 10, 'x'),   # never reached with continuance=0
)
def bounded(x):
  x * 2


def test_fail_fast():
  import pytest

  # Only the first guard's message surfaces (fail-fast default)
  with pytest.raises(GuardClauseError, match='must be positive'):
    bounded(-5)
```

## 🔄 Upgrading from Pre-2.0 Code

The v2 surface is the only supported API. If you have snippets written against an older `modgud`, map them across mechanically — there is no compatibility shim:

| Pre-2.0 | v2.0 |
|---------|------|
| `on_error=SomeException` | `strategy=GuardFailureEnum.ERROR_RAISE, on_failure=SomeException` (raise) or `ERROR_RETURN` to return the instance |
| `on_error=<value>` (dict / `None` / etc.) | `strategy=GuardFailureEnum.RETURN_VALUE, on_failure=<value>` |
| `on_error=<handler>` | `strategy=GuardFailureEnum.CALL_HANDLER, on_failure=<handler>` |
| `log=True` | removed — log from the call site or from a `CALL_HANDLER` |
| flat `from modgud import guarded_expression` | subpackage imports, e.g. `from modgud.app import guarded_expression` |
| handler signature `(error_msg, *args, **kwargs)` | `(errors, *args, **kwargs)` where `errors` is a `list[str]` |

## 🏛️ Architecture Details

### Clean Architecture Principles

modgud follows clean architecture with clear separation of concerns:

1. **Pure Functions**: Core logic uses pure, composable functions
2. **Immutability**: Transformed functions preserve original metadata
3. **Functional Composition**: Guards are composable pure functions

### Module Structure

Dependencies flow downward only: `app → domain.<feature>` (and its `ports`), `infrastructure.adapters → domain.<feature>` / `infrastructure.common`, `infrastructure.common → domain.<feature>`. The app layer never imports infrastructure: `guarded_expression` and `implicit_return` are **decorator classes** whose `@Invert()` constructors receive their implementations (adapters) through [Idunn](https://pypi.org/project/idunn), discovered on first use via `Idunn().bootstrap('modgud')`.

```
modgud/
  app/                                 # public decorators (entry points)
    wiring.py                          # Wiring.ensure() — the single Idunn composition root
    guarded_expression.py              # @guarded_expression(...) (class, @Invert() __init__)
    implicit_return.py                 # @implicit_return() (class, @Invert() __init__)
  domain/                              # passive types/enums/exceptions (no re-exports)
    guarded_expr/
      enums/guard_failure_enum.py      # GuardFailureEnum (IntEnum)
      errors/guard_clause_error.py     # GuardClauseError
      types.py                         # GuardFunction
      ports/                           # GuardRuntimePort (@Port)
    implicit_ret/
      errors/                          # one exception per module
        implicit_return_error.py       # ImplicitReturnError (base)
        explicit_return_disallowed_error.py
        missing_implicit_return_error.py
        unsupported_construct_error.py
      ports/                           # ImplicitReturnTransformerPort (@Port)
  infrastructure/                      # container package (no re-exports)
    adapters/                          # @Adapter implementations, discovered by Idunn
      guard_runtime.py                 # GuardRuntime — guard eval + dispatch
      implicit_return_transformer.py   # ImplicitReturnTransformer — AST rewriter
    common/
      common_guards.py                 # CommonGuards — pre-built validators
      guard_registry.py                # GuardRegistry — custom guard registration
    ast/
      _no_explicit_return_checker.py  # internal AST helpers used by the transformer adapter
      _tail_rewriter.py
      _top_level_transformer.py
```

### AST Transformation Process

For implicit returns, the transformation process:

1. Extract function source using `inspect.getsource()`
2. Parse source into AST using `ast.parse()`
3. Strip decorators to prevent re-application
4. Transform tail position expressions to assign to `__implicit_result`
5. Add single `return __implicit_result` at end
6. Compile transformed AST using `compile()`
7. Execute in original function's global scope
8. Wrap result with guard checking logic

### Guard Evaluation Pipeline

1. Guards are evaluated in order; `continuance` controls how many run past the first failure
2. Collected failure strings are dispatched through `strategy` / `on_failure`:
   - `ERROR_RAISE`: instantiate and raise `on_failure` (an `ExceptionGroup` when multiple failures)
   - `ERROR_RETURN`: instantiate `on_failure` but return it
   - `RETURN_VALUE`: return `on_failure` as-is
   - `CALL_HANDLER`: return `on_failure(errors, *args, **kwargs)` with `errors` as a `list[str]`
3. The wrapped function body runs only when no failure was recorded

### Performance Considerations

- **Single Decorator**: Reduced overhead vs. stacked decorators
- **Fail Fast**: Guards stop at the first failure by default (`continuance=0`)
- **Lazy Compilation**: AST transformation happens once at decoration time
- **One Tiny Runtime Dependency**: Idunn, used once per process to wire ports to adapters

### Type Safety

modgud is fully typed and mypy-compliant:

```python
from modgud.app import guarded_expression


# Guard functions are typed
def typed_guard(*args, **kwargs) -> bool | str:
  return args[0] > 0 or 'Must be positive'


# Decorated functions preserve type hints
@guarded_expression(typed_guard)
def typed_func(x: int) -> int:
  x * 2


# mypy correctly infers: typed_func(x: int) -> int
```

### Thread Safety

modgud decorators are thread-safe:
- No shared mutable state in decorators
- Function transformation happens at decoration time
- Guard evaluation uses only function arguments

Note: Stateful guards (not recommended) may require synchronization.

### Debugging Support

Functions preserve metadata for debugging:
- `__name__`: Original function name
- `__doc__`: Original docstring
- `__module__`: Original module
- `__annotations__`: Type hints
- `__wrapped__`: Reference to original function (before transformation)

---

## See Also

- **[⬅️ Main Introduction](../README.md)** - Quick overview and compelling use cases
- **[GitHub Repository](https://github.com/terracoil/modgud)** - Source code and issues
- **[PyPI Package](https://pypi.org/project/modgud/)** - Official releases

*For the latest updates and examples, visit the [modgud GitHub repository](https://github.com/terracoil/modgud).*
