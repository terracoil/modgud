![Modgud](modgud-github.png)

# How It Works: The Magic Behind Expression-Oriented Python

---

## 📍 Navigation

**You are here**: How It Works (Technical Deep-Dive)

**Parent**: [📚 Documentation Hub](README.md) - Back to documentation index
**Grandparent**: [🌉 Main README](../README.md) - Project overview
**Sibling**: [📖 API Reference](api-reference.md) - Complete API documentation

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
        status = "premium"
    else:
        status = "standard"
else:
    status = "inactive"
```

### Enter modgud

With modgud, Python joins the expression-oriented revolution:

```python
from modgud import guarded_expression

@guarded_expression()
def get_status(user):
    if user.is_active:
        "premium" if user.is_premium else "standard"
    else:
        "inactive"
```

But how does this work? Let's dive in.

---

## 🏛️ The Architecture: LPA-Lite (Layered Ports Architecture)

Modgud follows **LPA-Lite** principles with three distinct layers and port-based contracts:

```
┌─────────────────────────────────────┐
│      Application Layer              │
│  (decorator, guard_checker,         │
│   validators, registry)             │
├─────────────────────────────────────┤
│    Infrastructure Layer             │
│  (ast_transformer)                  │
├─────────────────────────────────────┤
│       Domain Layer                  │
│  (types, errors, messages, ports)   │
└─────────────────────────────────────┘
         ↑ Dependencies flow inward ↑
```

### Layer Responsibilities

**Application Layer** (`modgud/application/`)
- `decorator.py`: Main `guarded_expression` decorator (public API)
- `guard_checker.py`: Implements `GuardCheckerPort` for guard validation
- `validators.py`: `CommonGuards` factory for pre-built validators
- `registry.py`: `GuardRegistry` for custom guard management

**Infrastructure Layer** (`modgud/infrastructure/`)
- `ast_transformer.py`: Implements `AstTransformerPort` for AST transformation

**Domain Layer** (`modgud/domain/`)
- `types.py`: Type definitions (`GuardFunction`, `FailureBehavior`)
- `errors.py`: Exception hierarchy
- `messages.py`: Error message templates
- `ports.py`: Port interfaces (`GuardCheckerPort`, `AstTransformerPort`)

### Why LPA-Lite Architecture?

1. **Explicit Contracts**: Port interfaces define clear boundaries between layers
2. **Dependency Injection**: Decorator accepts optional port implementations
3. **Testability**: Each layer can be tested independently via ports
4. **Maintainability**: Changes don't cascade across boundaries
5. **Extensibility**: New implementations can be injected without modifying decorator
6. **Clarity**: Clear separation of concerns with inward-flowing dependencies

---

## 🛡️ The Guard Pipeline: Your Function's Bouncer

When you decorate a function with `@guarded_expression`, here's what happens at runtime:

```python
from modgud import guarded_expression, not_none

# User code
@guarded_expression(
    not_none("x"),
    on_error=ValueError
)
def divide_100_by(x):
    100 / x

# What actually runs
divide_100_by(5)  # Call enters the pipeline
```

### The Pipeline Flow

```
Function Call
     ↓
[Guard Check 1] → Fail? → Handle Error → Return/Raise
     ↓ Pass
[Guard Check 2] → Fail? → Handle Error → Return/Raise
     ↓ Pass
[Guard Check N] → Fail? → Handle Error → Return/Raise
     ↓ Pass
Execute Function
     ↓
Return Result
```

### Guard Evaluation

Each guard is a callable that receives `(*args, **kwargs)` and returns:
- `True`: Guard passed, continue
- String: Guard failed with this error message

```python
def positive_guard(param_name="value", position=0):
    def check(*args, **kwargs):
        value = kwargs.get(param_name, args[position] if position < len(args) else None)
        return value > 0 or f"{param_name} must be positive"
    return check
```

### Failure Handling

The `on_error` parameter determines what happens when a guard fails:

```python
# Return None on failure
@guarded_expression(guard, on_error=None)

# Return custom value
@guarded_expression(guard, on_error="invalid")

# Call handler function
@guarded_expression(guard, on_error=lambda msg, *args, **kwargs: log_and_return_default(msg))

# Raise exception (default)
@guarded_expression(guard, on_error=ValueError)
```

---

## 🔮 AST Transformation: The Secret Sauce

The real magic happens in the Abstract Syntax Tree (AST) transformation. When `implicit_return=True` (the default), modgud rewrites your function at the AST level.

### What is an AST?

An Abstract Syntax Tree represents code structure as a tree of nodes. Python can parse source code into an AST, manipulate it, and compile it back to bytecode.

```python
# Original Python code
def get_value(x):
    if x > 0:
        x * 2
    else:
        0

# Simplified AST representation
FunctionDef(name='get_value',
    body=[
        If(test=Compare(left=Name('x'), ops=[Gt()], comparators=[Constant(0)]),
           body=[Expr(BinOp(left=Name('x'), op=Mult(), right=Constant(2)))],
           orelse=[Expr(Constant(0))])
    ])
```

### The Transformation Process

1. **Source Extraction**: Get the function's source code
2. **Parse to AST**: Convert source to AST nodes
3. **Transform**: Modify AST to add implicit returns
4. **Compile**: Generate new bytecode
5. **Execute**: Create the transformed function

Here's what `ImplicitReturnTransformer` does:

```python
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
@guarded_expression()
def invalid_function(x):
    if x > 0:
        x * 2
    # Error: Missing else branch - not all paths return!
```

This raises `MissingImplicitReturnError` at decoration time, not runtime.

---

## ⚡ Runtime Composition: Putting It All Together

The `guarded_expression` decorator orchestrates the entire process:

```python
class guarded_expression:
    def __call__(self, func):
        # Step 1: Apply implicit return transformation (if enabled)
        if self.implicit_return_enabled:
            func = self._apply_implicit_return(func)

        # Step 2: Wrap with guard checking
        return self._wrap_with_guards(func)
```

### Execution Order

1. **Decoration Time**:
   - Parse function source
   - Transform AST if implicit returns enabled
   - Compile new function
   - Wrap with guard checker

2. **Call Time**:
   - Check all guards in order
   - Handle any failures per `on_error`
   - Execute transformed function
   - Return result

### Performance Considerations

- **AST transformation**: One-time cost at decoration
- **Guard checking**: Minimal overhead (simple function calls)
- **No runtime parsing**: Everything compiled at decoration time

### Thread Safety

Modgud is thread-safe:
- No global state modification
- Guards are pure functions
- Each decorated function is independent

---

## 🚨 Error Handling: Graceful Failures

Modgud provides a rich error hierarchy for different failure modes:

### Guard Failures

```python
GuardClauseError
    ├── Message: Human-readable error
    ├── Function: Which function failed
    └── Parameters: What was passed
```

### Transformation Errors

```python
ImplicitReturnError (base)
    ├── ExplicitReturnDisallowedError
    │   └── "Explicit return not allowed with implicit returns"
    ├── MissingImplicitReturnError
    │   └── "Not all code paths yield a value"
    └── UnsupportedConstructError
        └── "Cannot transform this Python construct"
```

### Custom Error Handlers

You can provide custom error handling logic:

```python
from modgud import guarded_expression, positive

def my_error_handler(error_msg, *args, **kwargs):
    logger.error(f"Guard failed: {error_msg}")
    return {"error": error_msg, "args": args}

@guarded_expression(
    positive("amount"),
    on_error=my_error_handler
)
def process_payment(amount):
    # Process payment logic
    amount * 1.1  # With tax
```

### Logging Integration

Enable built-in logging with `log=True`:

```python
from modgud import guarded_expression, not_none

@guarded_expression(
    not_none("user"),
    log=True  # Logs failures at INFO level
)
def greet_user(user):
    f"Hello, {user.name}!"
```

---

## 🎓 Advanced Topics

### Custom Guard Registration

Register reusable guards in namespaces:

```python
from modgud import register_guard

# Define custom guard
def valid_email(param_name="email", position=0):
    def check(*args, **kwargs):
        value = kwargs.get(param_name, args[position] if position < len(args) else None)
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, str(value))) or f"{param_name} must be a valid email"
    return check

# Register it
register_guard("valid_email", valid_email, namespace="validators")

# Use it anywhere
from modgud import get_guard

email_guard = get_guard("valid_email", namespace="validators")

@guarded_expression(email_guard("user_email"))
def send_newsletter(user_email):
    # Send email logic
    f"Sending to {user_email}"
```

### Guard Namespaces

Organize guards by domain:

```python
# Register domain-specific guards
register_guard("valid_product_id", product_id_guard, namespace="ecommerce")
register_guard("valid_user_role", role_guard, namespace="auth")
register_guard("valid_api_key", api_key_guard, namespace="api")

# List available namespaces
from modgud import list_guard_namespaces
namespaces = list_guard_namespaces()  # ['default', 'ecommerce', 'auth', 'api']
```

### Debugging Transformed Functions

To debug a transformed function, examine the generated code:

```python
import inspect
from modgud import guarded_expression

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
2. **Use specific error handlers**: Avoid generic exception catching
3. **Compile once, run many**: Decoration cost is one-time
4. **Prefer pre-built guards**: Optimized implementations

```python
from modgud import guarded_expression, not_none, not_empty, type_check

# Optimized guard ordering
@guarded_expression(
    not_none("data"),      # Fails fast on None
    not_empty("data"),     # Then check if empty
    type_check(list, "data"),  # Finally validate type
)
def process_data(data):
    len(data) * 100
```

### Limitations

Currently, modgud doesn't support:
- **Match/case statements** (Python 3.10+): Not yet implemented
- **Async generators**: Complex async iteration patterns
- **Direct source modification**: Works at AST level, not source level

---

## Conclusion

Modgud brings expression-oriented programming to Python through clever AST manipulation and clean architecture. By combining guard clauses with implicit returns, it enables a more functional, expressive coding style while maintaining Python's readability.

The magic isn't really magic—it's careful AST transformation, thoughtful architecture, and a deep respect for Python's design philosophy. We're not breaking Python's rules; we're extending them to embrace the best of both paradigms.

Happy guarding! 🛡️

---

[← Back to Documentation Hub](README.md) | [API Reference →](api-reference.md)