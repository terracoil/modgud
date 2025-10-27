# MODGUD Technical Documentation Hub

![modgud](https://github.com/terracoil/modgud/raw/master/docs/modgud-github.png)

> **New to modgud?** Check out the [main introduction](../README.md) for a quick overview and compelling examples!

## 📚 Documentation Navigation

### Core Documentation
- **[🔮 How It Works](how-it-works.md)** - Deep dive into AST transformation, guard pipelines, and the magic behind implicit returns
- **[📖 API Reference](api-reference.md)** - Complete reference for all decorators, guards, and types
- **[🏛️ Architecture Overview](architecture/README.md)** - Clean architecture design principles

### Quick Links
- [← Back to Main README](../README.md)
- [GitHub Repository](https://github.com/terracoil/modgud)
- [PyPI Package](https://pypi.org/project/modgud/)

---

## Table of Contents

This document contains:
- [Overview](#overview) - What modgud is and why it exists
- [Installation](#installation) - Getting started with modgud
- [Usage Examples](#usage-examples) - Practical code examples
  - [Basic Guard Usage](#basic-guard-usage)
  - [Implicit Returns](#implicit-returns)
  - [Explicit Returns](#explicit-returns)
  - [Error Handling Strategies](#error-handling-strategies)
  - [CommonGuards Usage](#commonguards-usage)
  - [Advanced Patterns](#advanced-patterns)
- [Implicit Return Semantics](#implicit-return-semantics) - How implicit returns work
  - [If/Else Statements](#ifelse-statements)
  - [Try/Except Blocks](#tryexcept-blocks)
  - [Match/Case Statements](#matchcase-statements)
  - [Rules and Restrictions](#rules-and-restrictions)
- [Guard Function Signature](#guard-function-signature) - Writing custom guards
- [Configuration Options](#configuration-options) - Decorator parameters
- [Testing Considerations](#testing-considerations) - Testing with modgud
- [Migration Guide](#migration-guide) - Upgrading between versions
- [Architecture Details](#architecture-details) - Design principles

> **Looking for specific API details?** See the [Complete API Reference](api-reference.md) for detailed documentation of all functions and classes.

## Overview

**modgud** is a Python library that brings expression-oriented programming, single return point architecture, and guard clause decorators to Python 3.13+. It provides a clean, functional approach to validation and control flow that eliminates defensive coding clutter while maintaining code clarity and maintainability.

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
- Standardizing error handling approaches

## Installation

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

- Python 3.13 or higher
- No external runtime dependencies (uses only Python standard library)

## Complete API Reference

> **Note**: The complete API reference has been moved to a dedicated document for easier navigation.
>
> **[📖 View Complete API Reference](api-reference.md)**

Below is a quick overview. For detailed documentation including all parameters, return values, and examples, see the [full API reference](api-reference.md).

### guarded_expression Decorator

The primary API for modgud, providing unified guard validation and implicit return functionality.

```python
@guarded_expression(*guards, implicit_return=True, on_error=GuardClauseError, log=False)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | `()` | Variable number of guard functions that validate inputs |
| `implicit_return` | `bool` | `True` | Enable implicit return transformation |
| `on_error` | `Any` | `GuardClauseError` | Behavior when guard fails |
| `log` | `bool` | `False` | Enable logging of guard failures |

#### Parameter Details

**`*guards`**: Zero or more guard functions. Each guard is a callable that:
- Accepts `(*args, **kwargs)` matching the decorated function's signature
- Returns `True` if validation passes
- Returns a string error message if validation fails
- Guards are evaluated sequentially and fail fast on first failure

**`implicit_return`**: Controls return behavior:
- `True` (default): Last expression in each branch is auto-returned; explicit `return` statements are forbidden
- `False`: Traditional Python behavior; explicit `return` required as last statement

**`on_error`**: Defines failure behavior when a guard fails:
- Exception class (default: `GuardClauseError`): Instantiated with error message and raised
- Callable: Invoked as `handler(error_msg, *args, **kwargs)`, return value becomes function result
- Any other value: Returned directly as the function result
- `None`: Returns `None` on guard failure

**`log`**: Logging behavior:
- `True`: Logs guard failures using Python's `logging` module at WARNING level
- `False` (default): No logging

#### Return Value

Returns a decorated function that:
1. Evaluates all guards before function execution
2. Handles failures according to `on_error` parameter
3. Transforms function for implicit returns if enabled
4. Preserves original function metadata (`__name__`, `__doc__`, etc.)

### CommonGuards Class

Pre-built guard validators for common validation scenarios.

#### not_none

```python
CommonGuards.not_none(param_name='parameter', position=0) -> GuardFunction
```

Ensures parameter is not None.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
@guarded_expression(CommonGuards.not_none("user_id"))
def get_user(user_id):
    # user_id guaranteed not None
    fetch_from_db(user_id)
```

#### not_empty

```python
CommonGuards.not_empty(param_name='parameter', position=None) -> GuardFunction
```

Ensures collection/string parameter is not empty.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `Optional[int]` | `None` | Position in args tuple (None = first arg) |

**Example:**
```python
@guarded_expression(CommonGuards.not_empty("items", position=1))
def process_list(user, items):
    # items guaranteed to have length > 0
    [process(item) for item in items]
```

#### positive

```python
CommonGuards.positive(param_name='parameter', position=0) -> GuardFunction
```

Ensures numeric parameter is positive (> 0).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param_name` | `str` | `'parameter'` | Name for error messages and kwargs lookup |
| `position` | `int` | `0` | Position in args tuple (0-based) |

**Example:**
```python
@guarded_expression(CommonGuards.positive("amount"))
def calculate_tax(amount):
    # amount guaranteed > 0
    amount * 0.08
```

#### in_range

```python
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
@guarded_expression(CommonGuards.in_range(1, 100, "page"))
def get_page(page):
    # page guaranteed between 1 and 100
    fetch_page_data(page)
```

#### type_check

```python
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
@guarded_expression(CommonGuards.type_check(dict, "config"))
def load_config(config):
    # config guaranteed to be a dict
    {**defaults, **config}
```

#### matches_pattern

```python
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
@guarded_expression(
    CommonGuards.matches_pattern(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', "email")
)
def send_email(email):
    # email guaranteed to match email pattern
    smtp_client.send(email)
```

### Error Classes

#### GuardClauseError

```python
class GuardClauseError(Exception):
    """Raised when guard clause validation fails."""
```

Default exception raised when guards fail (if `on_error=GuardClauseError`).

**Example:**
```python
try:
    result = guarded_function(-5)  # Negative when positive required
except GuardClauseError as e:
    print(f"Validation failed: {e}")
```

#### ImplicitReturnError

```python
class ImplicitReturnError(SyntaxError):
    """Base class for implicit return transformation errors."""
```

Base exception for all implicit return transformation errors. Subclasses provide specific error types.

#### ExplicitReturnDisallowedError

```python
class ExplicitReturnDisallowedError(ImplicitReturnError):
    """Raised when explicit return found with implicit_return=True."""
```

Raised during function transformation when an explicit `return` statement is found in a function decorated with `implicit_return=True`.

**Example:**
```python
# This will raise ExplicitReturnDisallowedError at decoration time
@guarded_expression()  # implicit_return=True by default
def bad_function(x):
    return x * 2  # ERROR: explicit return not allowed
```

#### MissingImplicitReturnError

```python
class MissingImplicitReturnError(ImplicitReturnError):
    """Raised when code branch doesn't produce a value for implicit return."""
```

Raised when a code branch at tail position doesn't produce a value (e.g., missing else clause).

**Example:**
```python
# This will raise MissingImplicitReturnError at decoration time
@guarded_expression()
def incomplete(x):
    if x > 0:
        x * 2
    # ERROR: missing else clause at tail position
```

#### UnsupportedConstructError

```python
class UnsupportedConstructError(ImplicitReturnError):
    """Raised when unsupported AST construct found at tail position."""
```

Raised when the AST transformer encounters an unsupported construct at tail position (e.g., `with` statements, `async for`, etc.).

## Usage Examples

### Basic Guard Usage

#### Simple Validation

```python
from modgud import guarded_expression

@guarded_expression(
    lambda x: x > 0 or "x must be positive",
    lambda x: x < 100 or "x must be less than 100"
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

#### Multiple Parameters

```python
@guarded_expression(
    lambda x, y: x > 0 or "x must be positive",
    lambda x, y: y > 0 or "y must be positive",
    lambda x, y: x != y or "x and y must be different"
)
def calculate_ratio(x, y):
    x / y
```

### Implicit Returns

#### Basic Implicit Return

```python
@guarded_expression()  # No guards, just implicit return
def double(x):
    x * 2  # Last expression is returned

print(double(5))  # Returns 10
```

#### Implicit Return with Conditionals

```python
@guarded_expression(CommonGuards.not_none("value"))
def classify_number(value):
    if value > 0:
        "positive"
    elif value < 0:
        "negative"
    else:
        "zero"

print(classify_number(5))    # Returns "positive"
print(classify_number(-3))   # Returns "negative"
print(classify_number(0))    # Returns "zero"
```

#### Complex Expressions

```python
@guarded_expression()
def process_data(data):
    cleaned = data.strip().lower()
    tokens = cleaned.split()
    filtered = [t for t in tokens if len(t) > 2]
    " ".join(filtered)  # Implicit return of joined string
```

### Explicit Returns

When you need traditional Python return behavior:

```python
@guarded_expression(
    CommonGuards.positive("x"),
    implicit_return=False  # Disable implicit returns
)
def calculate(x):
    result = x * 2
    intermediate = result + 10
    final = intermediate / 2
    return final  # Explicit return required

print(calculate(5))  # Returns 10.0
```

### Error Handling Strategies

#### Return Custom Values

```python
# Return None on failure
@guarded_expression(
    CommonGuards.positive("x"),
    on_error=None
)
def safe_sqrt(x):
    import math
    math.sqrt(x)

print(safe_sqrt(4))   # Returns 2.0
print(safe_sqrt(-1))  # Returns None

# Return error dict
@guarded_expression(
    CommonGuards.not_empty("data"),
    on_error={"success": False, "error": "Invalid input"}
)
def process_data(data):
    {"success": True, "result": data.upper()}

print(process_data("hello"))  # Returns {"success": True, "result": "HELLO"}
print(process_data(""))       # Returns {"success": False, "error": "Invalid input"}
```

#### Custom Exception Classes

```python
class ValidationError(Exception):
    """Custom validation exception."""
    pass

@guarded_expression(
    CommonGuards.positive("amount"),
    on_error=ValidationError
)
def withdraw(amount):
    {"withdrawn": amount, "timestamp": "2024-01-01"}

try:
    withdraw(-100)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

#### Handler Functions

```python
def log_and_default(error_msg, *args, **kwargs):
    """Log error and return default value."""
    print(f"Guard failed: {error_msg}")
    print(f"Args: {args}, Kwargs: {kwargs}")
    return {"error": True, "message": error_msg}

@guarded_expression(
    CommonGuards.in_range(1, 10, "level"),
    on_error=log_and_default
)
def set_level(level):
    {"level": level, "success": True}

result = set_level(15)
# Prints: Guard failed: level must be between 1 and 10
# Prints: Args: (15,), Kwargs: {}
# Returns: {"error": True, "message": "level must be between 1 and 10"}
```

### CommonGuards Usage

#### Parameter Extraction

CommonGuards intelligently extract parameters from both positional and keyword arguments:

```python
@guarded_expression(
    CommonGuards.not_none("user_id"),      # First positional or kwargs["user_id"]
    CommonGuards.positive("amount"),        # Second positional or kwargs["amount"]
    CommonGuards.not_empty("description", position=2)  # Third positional
)
def create_transaction(user_id, amount, description=""):
    {"user": user_id, "amount": amount, "desc": description}

# Works with positional arguments
create_transaction(123, 50.0, "Payment")

# Works with keyword arguments
create_transaction(user_id=123, amount=50.0, description="Payment")

# Mixed arguments
create_transaction(123, amount=50.0, description="Payment")
```

#### Combining Multiple Guards

```python
@guarded_expression(
    # User validation
    CommonGuards.not_none("email"),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', "email"),

    # Age validation
    CommonGuards.type_check(int, "age", position=1),
    CommonGuards.in_range(13, 120, "age", position=1),

    # Password validation
    CommonGuards.not_empty("password", position=2),

    log=True  # Log all validation failures
)
def register_user(email, age, password):
    user = {
        "email": email,
        "age": age,
        "password_hash": hash_password(password)
    }
    save_to_db(user)
    user
```

### Advanced Patterns

#### Composable Guard Sets

```python
# Define reusable guard combinations
pagination_guards = [
    lambda page=1: page >= 1 or "Page must be at least 1",
    lambda page=1, limit=10: limit >= 1 or "Limit must be at least 1",
    lambda page=1, limit=10: limit <= 100 or "Limit cannot exceed 100"
]

auth_guards = [
    CommonGuards.not_none("api_key"),
    lambda api_key: validate_api_key(api_key) or "Invalid API key"
]

@guarded_expression(*auth_guards, *pagination_guards)
def get_user_posts(api_key, page=1, limit=10):
    posts = fetch_posts(page, limit)
    {"posts": posts, "page": page, "count": len(posts)}
```

#### Dynamic Guard Generation

```python
def max_length(max_len, param_name="param", position=0):
    """Create a guard for maximum string length."""
    def check_length(*args, **kwargs):
        value = kwargs.get(param_name, args[position] if position < len(args) else "")
        return len(str(value)) <= max_len or f"{param_name} exceeds max length {max_len}"
    return check_length

@guarded_expression(
    CommonGuards.not_empty("username"),
    max_length(20, "username"),
    max_length(100, "bio", position=1)
)
def create_profile(username, bio=""):
    {"username": username, "bio": bio}
```

#### Conditional Guards

```python
def conditional_guard(condition, guard):
    """Apply guard only if condition is met."""
    def check(*args, **kwargs):
        if condition(*args, **kwargs):
            return guard(*args, **kwargs)
        return True
    return check

@guarded_expression(
    CommonGuards.not_none("data"),
    conditional_guard(
        lambda data, validate=False, **kw: validate,
        CommonGuards.type_check(dict, "data")
    )
)
def process(data, validate=False):
    if validate:
        {"validated": True, "data": data}
    else:
        {"validated": False, "data": data}

# Without validation - accepts any non-None type
process("string data", validate=False)

# With validation - requires dict
process({"key": "value"}, validate=True)
```

#### Guard with Logging

```python
import logging

logging.basicConfig(level=logging.INFO)

@guarded_expression(
    CommonGuards.positive("amount"),
    CommonGuards.in_range(1, 10000, "amount"),
    log=True  # Enable automatic logging
)
def transfer_funds(amount):
    transaction_id = generate_id()
    {"id": transaction_id, "amount": amount, "status": "completed"}

# Failed guard will log:
# WARNING:root:Guard 'amount must be positive' failed with args (0,) kwargs {}
transfer_funds(0)
```

## Implicit Return Semantics

Implicit return transforms functions to automatically return the last expression in each code branch, similar to languages like Ruby, Rust, and Scala.

### If/Else Statements

#### Basic If/Else

```python
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
@guarded_expression()
def categorize(value, threshold=10):
    if isinstance(value, (int, float)):
        if value > threshold:
            "high"
        else:
            "low"
    else:
        "invalid"
```

#### Required Else Clause

At tail position (the end of the function), if statements must have an else clause:

```python
# ERROR: Missing else at tail position
@guarded_expression()
def bad_conditional(x):
    if x > 0:
        "positive"
    # MissingImplicitReturnError - no value for x <= 0

# CORRECT: All branches covered
@guarded_expression()
def good_conditional(x):
    if x > 0:
        "positive"
    else:
        "non-positive"
```

### Try/Except Blocks

#### Basic Try/Except

```python
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
print(safe_divide(10, "a"))  # Returns None
```

#### Try/Except/Else/Finally

```python
@guarded_expression()
def robust_operation(data):
    try:
        result = process(data)
    except ValueError:
        {"error": "invalid value"}
    except Exception as e:
        {"error": str(e)}
    else:
        {"success": True, "result": result}
    # finally clause executes but doesn't affect return
```

#### Nested Try Blocks

```python
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
    except Exception as e:
        None
```

### Match/Case Statements

Python 3.10+ pattern matching is fully supported:

```python
@guarded_expression()
def process_command(command):
    match command:
        case ["move", x, y]:
            {"action": "move", "x": x, "y": y}
        case ["rotate", angle]:
            {"action": "rotate", "angle": angle}
        case ["scale", factor]:
            {"action": "scale", "factor": factor}
        case _:
            {"action": "unknown", "command": command}

print(process_command(["move", 10, 20]))
# Returns: {"action": "move", "x": 10, "y": 20}

print(process_command(["rotate", 90]))
# Returns: {"action": "rotate", "angle": 90}

print(process_command(["invalid"]))
# Returns: {"action": "unknown", "command": ["invalid"]}
```

#### Pattern Matching with Guards

```python
@guarded_expression()
def classify_point(point):
    match point:
        case (0, 0):
            "origin"
        case (x, 0) if x > 0:
            "positive x-axis"
        case (x, 0) if x < 0:
            "negative x-axis"
        case (0, y) if y > 0:
            "positive y-axis"
        case (0, y) if y < 0:
            "negative y-axis"
        case (x, y) if x > 0 and y > 0:
            "quadrant I"
        case (x, y) if x < 0 and y > 0:
            "quadrant II"
        case (x, y) if x < 0 and y < 0:
            "quadrant III"
        case (x, y) if x > 0 and y < 0:
            "quadrant IV"
        case _:
            "unknown"
```

### Rules and Restrictions

#### No Explicit Returns

With `implicit_return=True` (default), explicit return statements are forbidden:

```python
# ERROR: Raises ExplicitReturnDisallowedError
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
# ERROR: for loop doesn't produce a value
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
@guarded_expression()
def outer(x):
    def inner(y):
        # Explicit return OK in nested function
        if y > 0:
            return y * 2
        return y * 3

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

## Guard Function Signature

### Basic Guard Structure

A guard function is any callable that:
1. Accepts the same arguments as the decorated function (`*args, **kwargs`)
2. Returns `True` if validation passes
3. Returns a string error message if validation fails

```python
def my_guard(*args, **kwargs):
    # Validation logic
    if condition_met:
        return True
    return "Error message describing the failure"
```

### Simple Guards

```python
# Lambda guard
lambda x: x > 0 or "Value must be positive"

# Named function guard
def is_even(x):
    return x % 2 == 0 or "Value must be even"

@guarded_expression(
    lambda x: x > 0 or "Must be positive",
    is_even
)
def process(x):
    x / 2
```

### Guards with Multiple Parameters

```python
def sum_less_than_100(x, y):
    total = x + y
    return total < 100 or f"Sum {total} exceeds maximum of 100"

@guarded_expression(sum_less_than_100)
def add_limited(x, y):
    x + y
```

### Guards with Keyword Arguments

```python
def validate_config(*args, **kwargs):
    # Can access specific kwargs
    if "timeout" in kwargs:
        timeout = kwargs["timeout"]
        if timeout <= 0:
            return "Timeout must be positive"

    # Can validate presence of required kwargs
    if "api_key" not in kwargs:
        return "api_key is required"

    return True

@guarded_expression(validate_config)
def api_call(endpoint, **kwargs):
    make_request(endpoint, **kwargs)
```

### Parameterized Guard Factories

```python
def min_length(min_len):
    """Factory that creates a minimum length guard."""
    def check_length(*args, **kwargs):
        # Assume first arg is the string to check
        value = args[0] if args else ""
        if len(value) >= min_len:
            return True
        return f"Must be at least {min_len} characters"
    return check_length

def max_value(limit):
    """Factory that creates a maximum value guard."""
    def check_max(*args, **kwargs):
        value = args[0] if args else 0
        return value <= limit or f"Value {value} exceeds limit {limit}"
    return check_max

@guarded_expression(
    min_length(3),
    max_value(100)
)
def constrained_process(value):
    value * 2
```

### Stateful Guards

Guards can maintain state (though this should be used carefully):

```python
class RateLimitGuard:
    def __init__(self, max_calls=10):
        self.calls = 0
        self.max_calls = max_calls

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if self.calls > self.max_calls:
            return f"Rate limit exceeded: {self.calls}/{self.max_calls}"
        return True

rate_limiter = RateLimitGuard(max_calls=5)

@guarded_expression(rate_limiter)
def limited_operation(data):
    process(data)
```

### Async Guards

For async functions, guards are still synchronous (evaluated before the async function runs):

```python
@guarded_expression(
    CommonGuards.not_none("url"),
    lambda url: url.startswith("https://") or "URL must use HTTPS"
)
async def fetch_secure(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await response.text()
```

## Configuration Options

### Decorator Parameters Summary

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | `()` | Guard validation functions |
| `implicit_return` | `bool` | `True` | Enable implicit returns |
| `on_error` | `Any` | `GuardClauseError` | Failure behavior |
| `log` | `bool` | `False` | Enable logging |

### Common Configuration Patterns

#### Validation-Only (No Implicit Returns)

```python
@guarded_expression(
    CommonGuards.positive("x"),
    implicit_return=False,
    on_error=None
)
def validate_only(x):
    # Traditional Python with guards
    result = x * 2
    return result
```

#### Expression-Oriented (No Guards)

```python
@guarded_expression()  # All defaults
def expression_oriented(x):
    # Pure implicit return, no validation
    x * 2 + 10
```

#### Safe Operations (Return Default on Error)

```python
DEFAULT_USER = {"id": 0, "name": "Guest"}

@guarded_expression(
    CommonGuards.positive("user_id"),
    on_error=DEFAULT_USER
)
def get_user(user_id):
    fetch_from_database(user_id)
```

#### Audit Trail (Custom Handler)

```python
def audit_handler(error_msg, *args, **kwargs):
    audit_log.write(f"Failed: {error_msg}, Args: {args}")
    return None

@guarded_expression(
    CommonGuards.not_none("sensitive_data"),
    on_error=audit_handler,
    log=True
)
def sensitive_operation(sensitive_data):
    process_sensitive(sensitive_data)
```

#### API Response Pattern

```python
@guarded_expression(
    CommonGuards.type_check(dict, "payload"),
    on_error={"status": 400, "error": "Invalid request"},
    log=True
)
def api_endpoint(payload):
    result = process_request(payload)
    {"status": 200, "data": result}
```

### Logging Configuration

When `log=True`, failures are logged using Python's standard logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@guarded_expression(
    CommonGuards.positive("value"),
    log=True  # Failures logged at WARNING level
)
def logged_function(value):
    value * 2

# This logs: WARNING:root:Guard 'value must be positive' failed with args (-5,) kwargs {}
logged_function(-5)
```

## Testing Considerations

### Module-Level Functions for Implicit Returns

Functions using `implicit_return=True` must be defined at module level because `inspect.getsource()` cannot extract source from nested functions:

```python
# test_fixtures.py - Define test functions here
from modgud import guarded_expression

@guarded_expression()
def fixture_with_implicit(x):
    if x > 0:
        "positive"
    else:
        "non-positive"
```

```python
# test_implicit.py - Import and test
from test_fixtures import fixture_with_implicit

def test_implicit_return():
    assert fixture_with_implicit(5) == "positive"
    assert fixture_with_implicit(-5) == "non-positive"
```

### Testing Guard Failures

```python
import pytest
from modgud import guarded_expression, CommonGuards, GuardClauseError

@guarded_expression(
    CommonGuards.positive("x"),
    on_error=GuardClauseError
)
def needs_positive(x):
    x * 2

def test_guard_success():
    assert needs_positive(5) == 10

def test_guard_failure():
    with pytest.raises(GuardClauseError, match="must be positive"):
        needs_positive(-5)
```

### Testing Different Error Behaviors

```python
@guarded_expression(
    CommonGuards.not_none("value"),
    on_error=None
)
def returns_none_on_failure(value):
    value.upper()

@guarded_expression(
    CommonGuards.not_none("value"),
    on_error={"error": True}
)
def returns_dict_on_failure(value):
    {"result": value.upper()}

def test_none_on_error():
    assert returns_none_on_failure(None) is None
    assert returns_none_on_failure("hello") == "HELLO"

def test_dict_on_error():
    assert returns_dict_on_failure(None) == {"error": True}
    assert returns_dict_on_failure("hello") == {"result": "HELLO"}
```

### Testing Custom Guards

```python
def custom_guard(x, y):
    return x < y or f"x ({x}) must be less than y ({y})"

@guarded_expression(custom_guard)
def compare(x, y):
    y - x

def test_custom_guard():
    assert compare(3, 5) == 2

    with pytest.raises(GuardClauseError, match="x \\(5\\) must be less than y \\(3\\)"):
        compare(5, 3)
```

### Mocking Guards

```python
from unittest.mock import Mock

def test_guard_evaluation_order():
    guard1 = Mock(return_value=True)
    guard2 = Mock(return_value="Guard 2 failed")
    guard3 = Mock(return_value=True)

    @guarded_expression(guard1, guard2, guard3, on_error=None)
    def test_func(x):
        x * 2

    result = test_func(5)

    # First guard called
    guard1.assert_called_once_with(5)

    # Second guard called and failed
    guard2.assert_called_once_with(5)

    # Third guard never called (fail fast)
    guard3.assert_not_called()

    # Function returned None due to guard2 failure
    assert result is None
```

## Migration Guide

### From v0.1.x to v0.2.0

Version 0.2.0 introduces the unified `guarded_expression` decorator as the primary API. The old separate decorators are no longer needed.

#### Old Style (v0.1.x)

```python
from modgud import guard_clause, implicit_return

# Separate decorators for guards and implicit return
@guard_clause(lambda x: x > 0 or "x must be positive")
@implicit_return
def old_style(x):
    x * 2
```

#### New Style (v0.2.0+)

```python
from modgud import guarded_expression

# Unified decorator with both features
@guarded_expression(
    lambda x: x > 0 or "x must be positive"
    # implicit_return=True by default
)
def new_style(x):
    x * 2
```

### Migration Patterns

#### Guards Only → guarded_expression

```python
# Old
@guard_clause(
    lambda x: x > 0 or "x must be positive",
    on_error=None
)
def validate(x):
    return x * 2

# New
@guarded_expression(
    lambda x: x > 0 or "x must be positive",
    implicit_return=False,  # Disable implicit return
    on_error=None
)
def validate(x):
    return x * 2
```

#### Implicit Return Only → guarded_expression

```python
# Old
@implicit_return
def calculate(x):
    x * 2

# New
@guarded_expression()  # No guards, implicit_return=True by default
def calculate(x):
    x * 2
```

#### Both Decorators → guarded_expression

```python
# Old
@guard_clause(CommonGuards.positive("x"))
@implicit_return
def process(x):
    x * 2

# New
@guarded_expression(CommonGuards.positive("x"))
def process(x):
    x * 2
```

### Feature Comparison

| Feature | v0.1.x | v0.2.0 |
|---------|--------|--------|
| Guard validation | `@guard_clause` | `@guarded_expression` |
| Implicit returns | `@implicit_return` | `@guarded_expression` |
| Combined usage | Stack decorators | Single decorator |
| Default behavior | Explicit returns | Implicit returns |
| Error handling | Configurable | Configurable |
| CommonGuards | Available | Available |
| Performance | Good | Better (single decorator) |

### Breaking Changes

1. **Removed packages**: `modgud.guard_clause` and `modgud.implicit_return` packages removed
2. **Import changes**: Import from `modgud` directly, not subpackages
3. **Default behavior**: Implicit return is now ON by default
4. **Single decorator**: Use `guarded_expression` for everything

### Compatibility Mode

If you need time to migrate, you can create compatibility wrappers:

```python
# compatibility.py - Temporary migration helpers
from modgud import guarded_expression

def guard_clause(*guards, on_error=None, log=False):
    """Compatibility wrapper for old guard_clause decorator."""
    def decorator(func):
        return guarded_expression(
            *guards,
            implicit_return=False,  # Old behavior
            on_error=on_error,
            log=log
        )(func)
    return decorator

def implicit_return(func):
    """Compatibility wrapper for old implicit_return decorator."""
    return guarded_expression()(func)
```

## Architecture Details

### Clean Architecture Principles

modgud follows clean architecture with clear separation of concerns:

1. **Pure Functions**: Core logic uses pure, composable functions
2. **Dependency Injection**: Decorators compose functions rather than creating dependencies
3. **Immutability**: Transformed functions preserve original metadata
4. **Functional Composition**: Guards are composable pure functions

### Module Structure

```
modgud/
├── __init__.py                 # Public API exports
├── guarded_expression/         # Primary decorator package
│   ├── __init__.py
│   ├── decorator.py           # Main guarded_expression class
│   ├── ast_transform.py       # Pure AST transformation functions
│   ├── guard_runtime.py       # Pure guard checking functions
│   └── common_guards.py       # Pre-built guard factories
└── shared/                     # Shared infrastructure
    ├── __init__.py
    ├── types.py               # Type definitions
    └── errors.py              # Exception classes
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

1. Guards evaluated sequentially before function execution
2. First guard returning non-True value triggers failure
3. Optional logging if `log=True`
4. Failure handling based on `on_error`:
   - Exception class: instantiate and raise
   - Callable: invoke with `(error_msg, *args, **kwargs)`
   - Other value: return directly
5. Success: execute wrapped function

### Performance Considerations

- **Single Decorator**: Reduced overhead vs. stacked decorators
- **Fail Fast**: Guards stop at first failure
- **Lazy Compilation**: AST transformation happens once at decoration time
- **Zero Runtime Dependencies**: Uses only Python standard library

### Type Safety

modgud is fully typed and mypy-compliant:

```python
from typing import Callable, Any, Union
from modgud import GuardFunction, FailureBehavior

# Guard functions are typed
def typed_guard(x: int) -> Union[bool, str]:
    return x > 0 or "Must be positive"

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
