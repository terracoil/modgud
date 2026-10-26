**Parent**: [📚 Documentation Hub](README.md) | [🌉 Main README](../README.md) | [📖 API Reference](api-reference.md)

# How It Works: The Magic Behind Expression-Oriented Python

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

Welcome to the technical deep-dive into modgud's internals. This document explains how we transform Python from a statement-oriented language into one that embraces expression-oriented programming—all through the power of decorators and AST manipulation.

---

## 📋 Table of Contents

1. [💭 Introduction: Breaking Python's Rules (For Good)](#introduction-breaking-pythons-rules-for-good)
2. [🏛️ The Architecture: Clean, Functional, Powerful](#the-architecture-clean-functional-powerful)
3. [🛡️ The Guard Pipeline: Your Function's Bouncer](#the-guard-pipeline-your-functions-bouncer)
4. [🔮 AST Transformation: The Secret Sauce](#ast-transformation-the-secret-sauce)
5. [🎨 Implicit Return Mechanics: Expression Magic](#implicit-return-mechanics-expression-magic)
6. [⚡ Runtime Composition: Putting It All Together](#runtime-composition-putting-it-all-together)
7. [🚨 Error Handling: Graceful Failures](#error-handling-graceful-failures)
8. [🎓 Advanced Topics](#advanced-topics)

---

## 💭 Introduction: Breaking Python's Rules (For Good)

Python has always been a statement-oriented language. Every `if`, `for`, and `try` block is a statement that executes code but doesn't yield a value. This design choice has served Python well, but it also means we write more boilerplate than necessary.

Consider how other languages handle this:

```ruby
# Ruby - Everything is an expression
status = if user.active?
           user.premium? ? "premium" : "standard"
         else
           "inactive"
         end
```

```rust
// Rust - if is an expression
let status = if user.is_active {
    if user.is_premium { "premium" } else { "standard" }
} else {
    "inactive"
};
```

Python forces us into the statement paradigm:

```python
# Traditional Python - Statements everywhere
if user.is_active:
  if user.is_premium:
    status = 'premium'
  else:
    status = 'standard'
else:
  status = 'inactive'
```

### Enter modgud

With modgud, Python joins the expression-oriented revolution:

```python
from modgud.app import guarded_expression, implicit_return


@guarded_expression(implicit_return=False)
@implicit_return
def get_status(user):
  if user.is_active:
    'premium' if user.is_premium else 'standard'
  else:
    'inactive'
```

But how does this work? Let's dive in.

---

## 🏛️ The Architecture: Clean, Functional, Powerful

Modgud follows clean architecture principles with a per-feature decomposition across three layers. Dependencies flow downward only.

```
┌───────────────────────────────────────────┐
│                app/                        │
│   guarded_expression + implicit_return     │
│            (public functions)              │
├───────────────────────────────────────────┤
│            infrastructure/                 │
│  GuardRuntime, CommonGuards, GuardRegistry │
│      ImplicitReturnTransformer (AST)       │
├───────────────────────────────────────────┤
│                 domain/                    │
│  GuardFailureEnum, GuardClauseError,   │
│   GuardFunction, ImplicitReturn errors     │
└───────────────────────────────────────────┘
```

### Layer Responsibilities

**App layer (`modgud/app/`)**
- `guarded_expression.py`: the guard-validation decorator (a plain function) with optional implicit returns
- `implicit_return.py`: the standalone expression-oriented transform (a plain function)

**Infrastructure layer (`modgud/infrastructure/`)**
- `guarded_expr/guard_runtime.py`: guard evaluation + failure dispatch (`GuardRuntime`)
- `guarded_expr/common_guards.py`: pre-built validators (`CommonGuards`)
- `guarded_expr/guard_registry.py`: custom guard management (`GuardRegistry`)
- `implicit_ret/implicit_return_transformer.py`: the AST transformation engine

**Domain layer (`modgud/domain/`)**
- `guarded_expr/`: `GuardFailureEnum`, `GuardClauseError`, the `GuardFunction` type, and a runtime port
- `implicit_ret/`: the `ImplicitReturnError` hierarchy and a transformer port

### Why Clean Architecture?

1. **Testability**: Each layer can be tested independently
2. **Maintainability**: Changes don't cascade across boundaries
3. **Extensibility**: New features slot in cleanly
4. **Clarity**: Clear separation of concerns

---

## 🛡️ The Guard Pipeline: Your Function's Bouncer

When you decorate a function with `@guarded_expression`, here's what happens at runtime:

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards


# User code
@guarded_expression(
  CommonGuards.not_none('x'),
  on_failure=ValueError,
  implicit_return=False,
)
@implicit_return
def divide_100_by(x):
  100 / x


# What actually runs
divide_100_by(5)  # Call enters the pipeline
```

### The Pipeline Flow

```
Function Call
     ↓
[Guard Check 1] → Fail? → Collect failure
     ↓ Pass
[Guard Check 2] → Fail? → Collect failure
     ↓ Pass
[Guard Check N] → Fail? → Collect failure
     ↓
Any failures? → Dispatch via strategy / on_failure → Return/Raise
     ↓ None
Execute Function
     ↓
Return Result
```

By default (`continuance=0`) the pipeline stops at the first failing guard; a larger `continuance` keeps checking and collects up to `1 + continuance` failures.

### Guard Evaluation

Each guard is a callable that receives `(*args, **kwargs)` — the full argument tuple — and returns:
- `True`: Guard passed, continue
- String: Guard failed with this error message

```python
def positive_guard(param_name='value', position=0):
  def check(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else None)
    return value > 0 or f'{param_name} must be positive'

  return check
```

### Failure Handling

The `strategy` + `on_failure` pair determines what happens once one or more guards fail:

```python
# illustrative — strategy/on_failure mapping (fragments, not full defs)
from modgud.domain.guarded_expr import GuardFailureEnum

# Return None on failure
strategy = GuardFailureEnum.RETURN_VALUE, on_failure = None

# Return a custom value
strategy = GuardFailureEnum.RETURN_VALUE, on_failure = 'invalid'

# Call a handler — receives errors as a list[str]
strategy = GuardFailureEnum.CALL_HANDLER, on_failure = my_handler

# Raise an exception (default)
strategy = GuardFailureEnum.ERROR_RAISE, on_failure = ValueError
```

---

## 🔮 AST Transformation: The Secret Sauce

The real magic happens in the Abstract Syntax Tree (AST) transformation. When `implicit_return=True` (the default), modgud rewrites your function at the AST level.

### What is an AST?

An Abstract Syntax Tree represents code structure as a tree of nodes. Python can parse source code into an AST, manipulate it, and compile it back to bytecode.

```python
# illustrative — conceptual AST shape
# Original Python code
def get_value(x):
  if x > 0:
    x * 2
  else:
    0


# Simplified AST representation
FunctionDef(
  name='get_value',
  body=[
    If(
      test=Compare(left=Name('x'), ops=[Gt()], comparators=[Constant(0)]),
      body=[Expr(BinOp(left=Name('x'), op=Mult(), right=Constant(2)))],
      orelse=[Expr(Constant(0))],
    )
  ],
)
```

### The Transformation Process

1. **Source Extraction**: Get the function's source code
2. **Parse to AST**: Convert source to AST nodes
3. **Transform**: Modify AST to add implicit returns
4. **Compile**: Generate new bytecode
5. **Execute**: Create the transformed function

Here's what `ImplicitReturnTransformer` does:

```python
# illustrative — before/after conceptual shape
# Before transformation
def calculate(x, y):
  if x > y:
    x + y
  else:
    x - y


# After AST transformation (conceptually)
def calculate(x, y):
  __implicit_result = None
  if x > y:
    __implicit_result = x + y
  else:
    __implicit_result = x - y
  return __implicit_result
```

### Detecting Tail Positions

The transformer identifies "tail positions"—the last expression in each execution path:

```python
# illustrative — internal transformer sketch
class ImplicitReturnTransformer(ast.NodeTransformer):
  def visit_If(self, node):
    # Transform the last statement in each branch
    if node.body:
      node.body[-1] = self.transform_tail_expression(node.body[-1])
    if node.orelse:
      node.orelse[-1] = self.transform_tail_expression(node.orelse[-1])
    return node
```

### Handling Complex Structures

The transformer handles nested structures intelligently:

```python
from modgud.app import guarded_expression


@guarded_expression()
def complex_logic(x, y, z):
  if x > 0:
    if y > 0:
      x + y  # Tail position in nested if
    else:
      x - y  # Tail position in nested else
  else:
    try:
      z / x  # Tail position in try
    except ZeroDivisionError:
      0  # Tail position in except
```

---

## 🎨 Implicit Return Mechanics: Expression Magic

The implicit return system transforms Python statements into expressions by introducing a hidden accumulator variable.

### The `__implicit_result` Variable

Every function with implicit returns gets a hidden variable:

```python
# illustrative — before/after conceptual shape
# What you write
@guarded_expression()
def calculate(x):
  x * 2


# What runs (conceptually)
def calculate(x):
  __implicit_result = None
  __implicit_result = x * 2
  return __implicit_result
```

### Transforming Control Flow

Different Python constructs get different transformations:

#### If/Else Statements

```python
# illustrative — before/after conceptual shape
# Input
if condition:
  value1
else:
  value2

# Transformed
if condition:
  __implicit_result = value1
else:
  __implicit_result = value2
```

#### Try/Except Blocks

```python
# illustrative — before/after conceptual shape
# Input
try:
  risky_operation()
except Error:
  default_value

# Transformed
try:
  __implicit_result = risky_operation()
except Error:
  __implicit_result = default_value
```

#### Expression Statements

Not all statements are expressions. The transformer identifies expression statements:

```python
# illustrative — which statements become implicit returns
# These become implicit returns
x + y           # Binary operation
func()          # Function call
x if y else z   # Ternary expression
[x, y, z]       # List literal
{'a': 1}        # Dict literal

# These remain statements (no implicit return)
x = 5           # Assignment
del x           # Deletion
import foo      # Import
```

### Validation and Safety

The transformer validates that all paths yield values:

```python
# illustrative — raises MissingImplicitReturnError at decoration time
@guarded_expression()
def invalid_function(x):
  if x > 0:
    x * 2
  # Error: Missing else branch - not all paths return!
```

This raises `MissingImplicitReturnError` at decoration time, not runtime.

---

## ⚡ Runtime Composition: Putting It All Together

The `guarded_expression` decorator is a function that orchestrates the entire process. Conceptually it applies the implicit-return transform first (when enabled), then wraps the result with guard checking:

```python
# illustrative — conceptual decorator body
def guarded_expression(*guards, implicit_return=True, strategy=..., on_failure=..., continuance=0):
  def decorator(func):
    target = ImplicitReturnTransformer.transform_function(func) if implicit_return else func
    return GuardRuntime.wrap_function(target, guards, strategy, on_failure, continuance)

  return decorator
```

### Execution Order

1. **Decoration Time**:
   - Parse function source
   - Transform AST if implicit returns enabled
   - Compile new function
   - Wrap with guard checker

2. **Call Time**:
   - Check guards in order (collecting up to `1 + continuance` failures)
   - Dispatch any failures via `strategy` / `on_failure`
   - Execute transformed function
   - Return result

### Performance Considerations

- **AST transformation**: One-time cost at decoration
- **Guard checking**: Minimal overhead (simple function calls)
- **No runtime parsing**: Everything compiled at decoration time

### Thread Safety

Modgud is thread-safe:
- No global state modification during evaluation
- Guards are pure functions
- Each decorated function is independent

### The Composition Pattern

**Separation of Concerns:** modgud provides separate decorators that can be composed. When stacking, set `implicit_return=False` on the outer `@guarded_expression` and let the inner `@implicit_return` own the AST rewrite:

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.guarded_expr import CommonGuards


# Recommended pattern: Guard validation + expression transformation
@guarded_expression(
  CommonGuards.not_none('x'),
  CommonGuards.positive('x'),
  implicit_return=False,
)
@implicit_return
def process(x):
  result = x * 2
  result


# Guards only (traditional explicit returns)
@guarded_expression(CommonGuards.not_none('x'), implicit_return=False)
def calculate(x):
  return x * 2


# Expression transformation only
@implicit_return
def classify(status):
  'active' if status else 'inactive'
```

**Why Separate?** This composition pattern enables:
- **Flexibility**: Use guards without expression transformation or vice versa
- **Future Extensions**: New expression-oriented decorators can compose cleanly
- **Clarity**: Each decorator has a single, clear responsibility
- **Testability**: Each transformation can be tested independently

---

## 🚨 Error Handling: Graceful Failures

Modgud provides a rich error hierarchy for different failure modes:

### Guard Failures

```
GuardClauseError
    ├── Message: Human-readable error (or an ExceptionGroup for multiple)
    └── Raised (ERROR_RAISE) or returned (ERROR_RETURN) per strategy
```

### Transformation Errors

```
ImplicitReturnError (base)
    ├── ExplicitReturnDisallowedError
    │   └── "Explicit return not allowed with implicit returns"
    ├── MissingImplicitReturnError
    │   └── "Not all code paths yield a value"
    └── UnsupportedConstructError
        └── "Cannot transform this Python construct"
```

### Custom Error Handlers

You can provide custom handling logic via the `CALL_HANDLER` strategy. The handler receives `errors` as a `list[str]`:

```python
from modgud.app import guarded_expression, implicit_return
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.guarded_expr import CommonGuards


def my_error_handler(errors, *args, **kwargs):
  print(f'Guards failed: {errors}')
  return {'errors': errors, 'args': args}


@guarded_expression(
  CommonGuards.positive('amount'),
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=my_error_handler,
  implicit_return=False,
)
@implicit_return
def process_payment(amount):
  amount * 1.1  # With tax
```

---

## 🎓 Advanced Topics

### Custom Guard Registration

Register reusable guards in namespaces. Keep all imports at module top:

```python
import re

from modgud.infrastructure.guarded_expr import GuardRegistry


# Define custom guard
def valid_email(param_name='email', position=0):
  def check(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else None)
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, str(value))) or f'{param_name} must be a valid email'

  return check


# Register it
GuardRegistry.register('valid_email', valid_email, namespace='validators')
```

```python
import re

from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import GuardRegistry


def valid_email(param_name='email', position=0):
  def check(*args, **kwargs):
    value = kwargs.get(param_name, args[position] if position < len(args) else None)
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(value))) or f'{param_name} must be a valid email'

  return check


GuardRegistry.register('valid_email', valid_email, namespace='validators')

# Retrieve and use it anywhere
email_guard = GuardRegistry.get('valid_email', namespace='validators')


@guarded_expression(email_guard('user_email'))
def send_newsletter(user_email):
  f'Sending to {user_email}'
```

### Guard Namespaces

Organize guards by domain. The built-in `CommonGuards` live under the `'common'` namespace:

```python
from modgud.infrastructure.guarded_expr import CommonGuards, GuardRegistry


# Register domain-specific guards under their own namespaces.
# The second argument is any guard *factory* (a callable returning a GuardFunction).
GuardRegistry.register('valid_product_id', CommonGuards.matches_pattern, namespace='ecommerce')
GuardRegistry.register('valid_user_role', CommonGuards.not_empty, namespace='auth')
GuardRegistry.register('valid_api_key', CommonGuards.not_none, namespace='api')

# List available namespaces
namespaces = GuardRegistry.list_namespaces()
# e.g. ['common', 'ecommerce', 'auth', 'api'] — 'common' is always present
```

### Debugging Transformed Functions

To debug a transformed function, verify its behavior directly:

```python
from modgud.app import guarded_expression


@guarded_expression()
def my_function(x):
  if x > 0:
    x * 2
  else:
    0


# The source won't show the transformation (it's at AST level)
# But you can verify behavior:
assert my_function(5) == 10
assert my_function(-5) == 0
```

### Performance Optimization Tips

1. **Order guards by failure likelihood**: Put most likely to fail first
2. **Use specific handlers**: Avoid generic exception catching
3. **Compile once, run many**: Decoration cost is one-time
4. **Prefer pre-built guards**: Optimized implementations

```python
from modgud.app import guarded_expression
from modgud.infrastructure.guarded_expr import CommonGuards


# Optimized guard ordering
@guarded_expression(
  CommonGuards.not_none('data'),         # Fails fast on None
  CommonGuards.not_empty('data'),        # Then check if empty
  CommonGuards.type_check(list, 'data'),  # Finally validate type
)
def process_data(data):
  len(data) * 100
```

### Limitations

Currently, modgud doesn't support:
- **Async generators**: Complex async iteration patterns
- **Direct source modification**: Works at AST level, not source level
- **Tail-position loops / `with` / `async with`**: these can appear *inside* a function, just not as the final value-producing statement

Match/case statements (Python 3.10+) *are* fully supported at tail position.

---

## Conclusion

Modgud brings expression-oriented programming to Python through clever AST manipulation and clean architecture. By combining guard clauses with implicit returns, it enables a more functional, expressive coding style while maintaining Python's readability.

The magic isn't really magic—it's careful AST transformation, thoughtful architecture, and a deep respect for Python's design philosophy. We're not breaking Python's rules; we're extending them to embrace the best of both paradigms.

Happy guarding! 🛡️

---

[← Back to Documentation Hub](README.md) | [API Reference →](api-reference.md)
