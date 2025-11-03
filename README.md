# !["Móðguðr"](https://github.com/terracoil/modgud/raw/master/docs/modgud-text-sm.png)

## Finally. Expression-Oriented Programming for Python.

**Stop writing defensive spaghetti. Start writing beautiful, contract-driven code.**

Tired of functions where 80% of the code is validation boilerplate? Frustrated by nested conditionals checking types, values, and state before you can even *think* about business logic? Wish Python had expression-oriented programming like Ruby, Rust, or Scala?

**modgud changes everything.**

![modgud](https://github.com/terracoil/modgud/raw/master/docs/modgud-github-md.png)

---

## The Name: Móðguðr, Guardian of the Bridge

In Norse mythology, **Móðguðr** (*"Furious Battler"*) stands as guardian of Gjallarbrú—the golden-roofed bridge spanning the river Gjöll on the path to Hel. Every soul seeking passage must stop and state their name and business before crossing. She is the threshold keeper, the boundary enforcer, the one who demands identification before allowing entry to sacred ground.

This is exactly what `modgud` does for your functions. Just as Móðguðr guards the bridge to the underworld, our guard clauses protect your function boundaries—challenging invalid inputs before they can corrupt your logic. And yes, we're well aware that "modgud" sounds remarkably like **"mod-good"** or **"good mods"**. That's not accidental. 😊

After all, what are expression-oriented guard clauses if not *genuinely good modifications* to Python? You're literally adding **gud mods** to your functions. The Norse goddess would approve: proper guards at every threshold, allowing only the worthy to pass. Your code deserves both mythological protection *and* some really good enhancements.

---

## 📍 Navigation

**You are here**: Main README (Project Overview)

**Children** (Full Documentation):
- [📚 Documentation Hub](docs/README.md) - Central documentation index
- [📖 API Reference](docs/api-reference.md) - Complete API documentation
- [⚙️ How It Works](docs/how-it-works.md) - Technical deep-dive into AST transformation

**External Links**:
- [🌐 GitHub Repository](https://github.com/terracoil/modgud) - Source code & issues
- [📦 PyPI Package](https://pypi.org/project/modgud/) - Official releases

---

## 📋 Table of Contents
- [🔥️ Why Modgud](#the-problem) - Why modgud is essential
- [⚠️ The Problem](#the-problem) - Why defensive programming gets messy
- [💡 The Solution](#the-solution) - How modgud changes everything
- [🔑 Features](#features) - Six compelling features
- [💡 Quick Start](#quick-start) - Get started in 60 seconds
- [🔑 Key Features at a Glance](#key-features-at-a-glance) - What makes modgud special
- [🌍 Real-World Example](#real-world-example-api-endpoint) - See it in action
- [📚 Documentation](#documentation) - Complete guides and references
- [📦 Installation](#installation) - How to install
- [🤝 Contributing](#contributing) - Join the project
- [✨ What's New](#whats-new-in-v11) - Latest changes

---
## 🔥 Why Modgud?

Despite Python's evolution toward more functional features (pattern matching in 3.10+, better type hints, etc.), modgud fills a critical gap: **making Python functions behave like expressions without changing Python's syntax**. This is uniquely valuable because:

### 1. **Zero-Syntax-Cost Expression Orientation**
While Python 3.10+ adds pattern matching, it's still statement-based. modgud's `@guarded_expression` transforms regular functions into expression-oriented code *today*, working seamlessly with Python 3.6+ codebases. You get Haskell-like guards and implicit returns without waiting for PEP acceptance or version upgrades.

### 2. **Gradual Adoption Path**
Unlike heavy functional libraries (PyMonad, toolz, etc.) that require wholesale architectural changes, modgud decorators can be applied selectively. Start with one critical function, see the benefits, expand gradually. This pragmatic approach reduces resistance in teams unfamiliar with FP.

### 3. **Pythonic Integration**
Rather than forcing Haskell or Scala idioms into Python, modgud enhances Python's existing decorator pattern. This feels natural to Python developers while delivering expression-oriented benefits. No new operators, no category theory, just cleaner functions.

### 4. **Performance Without Overhead**
Many FP libraries introduce abstraction penalties through wrapper objects and indirection. modgud's approach (presumably) operates at the function level with minimal runtime overhead, making it suitable for performance-sensitive code where other FP solutions might be rejected.

### 5. **Compatibility Story**
Working from Python 3.6+ means modgud supports the vast majority of production Python deployments. Enterprises stuck on older versions for stability can still adopt modern expression-oriented patterns without infrastructure changes.


## ⚠️ The Problem

Look familiar?

```python
def process_payment(user_id, amount, payment_method):
    # Validation hell begins...
    if user_id is None:
        return {"error": "User ID required"}

    if not isinstance(user_id, int):
        return {"error": "Invalid user ID type"}

    if user_id <= 0:
        return {"error": "User ID must be positive"}

    if amount is None or amount <= 0:
        return {"error": "Invalid amount"}

    if amount > 10000:
        return {"error": "Amount exceeds limit"}

    if not payment_method or payment_method == "":
        return {"error": "Payment method required"}

    if payment_method not in ["card", "bank", "crypto"]:
        return {"error": "Invalid payment method"}

    # Finally, the actual business logic (if you can find it)
    transaction = create_transaction(user_id, amount, payment_method)
    return {"success": True, "transaction_id": transaction.id}
```

**8 validation checks. 16 lines of defensive code. 2 lines of actual business logic.**

Multiple return points everywhere. Business logic buried at the bottom. Error handling inconsistent. This is what happens when validation and logic mix.

---

## 💡 The Solution

**modgud** gives you guard clauses and expression-oriented programming in Python:

```python
from modgud import guarded_expression, implicit_return, positive, type_check, in_range, not_empty

@guarded_expression(
    positive("user_id"),
    type_check(int, "user_id"),
    positive("amount"),
    in_range(1, 10000, "amount"),
    not_empty("payment_method"),
    lambda pm: pm in ["card", "bank", "crypto"] or "Invalid payment method",
    on_error={"success": False, "error": "Validation failed"}
)
@implicit_return
def process_payment(user_id, amount, payment_method):
    transaction = create_transaction(user_id, amount, payment_method)
    {"success": True, "transaction_id": transaction.id}  # Implicit return!
```

**Same functionality. Zero defensive clutter. Single return point. Business logic front and center.**

---

## 🔑 Features

### 1. 🛡️ Guard Clauses That Actually Work

Declare your function's contract upfront. Validations execute before your function runs. Guards fail fast. No more deeply nested if statements cluttering your business logic.

**Before:**
```python
def withdraw(account_id, amount):
    if account_id is None:
        raise ValueError("Account required")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > get_balance(account_id):
        raise ValueError("Insufficient funds")

    # Actual work hidden at the bottom
    balance = get_balance(account_id) - amount
    update_balance(account_id, balance)
    return balance
```

**After:**
```python
from modgud import guarded_expression, implicit_return, not_none, positive

@guarded_expression(
    not_none("account_id"),
    positive("amount"),
    lambda account_id, amount: amount <= get_balance(account_id) or "Insufficient funds"
)
@implicit_return
def withdraw(account_id, amount):
    balance = get_balance(account_id) - amount
    update_balance(account_id, balance)
    balance  # Clean implicit return
```

### 2. 🎨 Expression-Oriented Programming (Finally!)

The last expression in each branch is your return value. Just like Ruby, Rust, Scala, and every other modern language. No more cluttered `return` statements everywhere.

**Before:**
```python
def classify_user(age, premium):
    if age < 18:
        return "minor"
    elif premium:
        return "premium_adult"
    else:
        return "standard_adult"
```

**After:**
```python
from modgud import guarded_expression, implicit_return, positive

@guarded_expression(positive("age"))
@implicit_return
def classify_user(age, premium):
    if age < 18:
        "minor"
    elif premium:
        "premium_adult"
    else:
        "standard_adult"
```

Clean. Readable. Expressive. The way code should be.

### 3. 🎖️ Single Return Point Architecture

Every function has exactly one logical exit point. Easier debugging. Clearer control flow. No hunting through nested conditionals for hidden `return` statements.

Guards handle early exits. Your function handles business logic. Separation of concerns at its finest.

### 4. 🧩 Pre-Built Guards

Stop writing the same validations over and over:

```python
from modgud import guarded_expression, implicit_return, not_none, matches_pattern, positive, in_range, not_empty, type_check

@guarded_expression(
    not_none("email"),
    matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', "email"),
    positive("age"),
    in_range(13, 120, "age"),
    not_empty("username"),
    type_check(str, "username")
)
@implicit_return
def register_user(email, age, username):
    user_id = create_user_record(email, age, username)
    send_welcome_email(email)
    {"success": True, "user_id": user_id}
```

Built-in guards for:
- `not_none` - Ensure values exist
- `not_empty` - Validate collections/strings have content
- `positive` - Numeric validation
- `in_range` - Bounded value checking
- `type_check` - Runtime type validation
- `matches_pattern` - Regex pattern matching

Plus you can write custom guards in seconds.

### 5. 🎛️ Flexible Error Handling

Your code, your rules. Choose how guards fail:

**Return custom values:**
```python
from modgud import guarded_expression, implicit_return, positive

@guarded_expression(
    positive("amount"),
    on_error={"error": "Invalid amount", "code": 400}
)
@implicit_return
def process(amount):
    {"success": True, "amount": amount}
```

**Raise exceptions:**
```python
from modgud import guarded_expression, implicit_return, not_empty

@guarded_expression(
    not_empty("username"),
    on_error=ValueError
)
@implicit_return
def create_account(username):
    Account(username)
```

**Custom handlers:**
```python
from modgud import guarded_expression, implicit_return

def audit_and_return(error_msg, *args, **kwargs):
    log_security_event(error_msg)
    return None

@guarded_expression(
    lambda api_key: validate_key(api_key) or "Invalid key",
    on_error=audit_and_return
)
@implicit_return
def sensitive_operation(api_key):
    perform_operation()
```

### 6. 📦 Zero Dependencies

Built entirely on Python's standard library. No bloat. No version conflicts. Just clean, fast Python.

### 7. ✅ Battle-Tested & Type-Safe

- Full mypy type checking support
- Comprehensive test suite with 92% coverage
- Clean architecture with dependency injection
- Thread-safe decorators
- Preserves all function metadata for debugging

---

## 💡 Quick Start

### 📦 Installation

```bash
pip install modgud
```

**Requirements:** Python 3.13+

### Your First Guarded Function

```python
from modgud import guarded_expression, implicit_return, positive, in_range

@guarded_expression(
    positive("x"),
    in_range(1, 100, "x")
)
@implicit_return
def calculate_discount(x):
    if x >= 50:
        x * 0.2
    else:
        x * 0.1

print(calculate_discount(75))   # Returns 15.0
print(calculate_discount(25))   # Returns 2.5
print(calculate_discount(-10))  # Raises GuardClauseError
```

**That's it.** You're writing cleaner Python.

---

## 🔑 Key Features at a Glance

- **🎨 Implicit Returns by Default** - Last expression in each branch is auto-returned (like Ruby/Rust/Scala)
- **🛡️ Guard Clause Decorators** - Validate inputs before function execution
- **🎯 Single Return Point** - One logical exit point per function
- **🧩 Pre-Built Guards** - Standard validations ready to use (not_none, positive, in_range, type_check, etc.)
- **🎛️ Configurable Failure Behaviors** - Return values, raise exceptions, or call custom handlers
- **🏛️ Clean Architecture** - Dependency injection, pure functions, immutable transforms
- **📦 Zero Dependencies** - Uses only Python standard library
- **✅ Type-Safe** - Full mypy support with proper type hints
- **🔒 Thread-Safe** - No shared mutable state
- **🧪 Well-Tested** - 92% coverage with 40+ comprehensive tests

---

## 🌍 Real-World Example: API Endpoint

**Before modgud:**

```python
def create_user(email, age, username, password):
    # Validation nightmare
    if not email or email == "":
        return {"status": 400, "error": "Email required"}

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return {"status": 400, "error": "Invalid email format"}

    if age is None or not isinstance(age, int):
        return {"status": 400, "error": "Invalid age"}

    if age < 13 or age > 120:
        return {"status": 400, "error": "Age must be 13-120"}

    if not username or username == "":
        return {"status": 400, "error": "Username required"}

    if len(username) < 3 or len(username) > 20:
        return {"status": 400, "error": "Username must be 3-20 chars"}

    if not password or password == "":
        return {"status": 400, "error": "Password required"}

    # Finally, the actual work
    user_id = db.create_user(email, age, username, hash_password(password))
    return {"status": 200, "user_id": user_id}
```

**With modgud:**

```python
from modgud import guarded_expression, implicit_return, not_empty, matches_pattern, type_check, in_range

@guarded_expression(
    not_empty("email"),
    matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', "email"),
    type_check(int, "age"),
    in_range(13, 120, "age"),
    not_empty("username"),
    lambda username: 3 <= len(username) <= 20 or "Username must be 3-20 chars",
    not_empty("password"),
    on_error={"status": 400, "error": "Validation failed"}
)
@implicit_return
def create_user(email, age, username, password):
    user_id = db.create_user(email, age, username, hash_password(password))
    {"status": 200, "user_id": user_id}
```

**14 lines → 8 lines. Zero defensive clutter. 100% focus on business logic.**

---

## What Developers Say

*"I can't believe this isn't built into Python. Guard clauses should be standard."*

*"Finally! Expression-oriented programming in Python. My functions are half the size now."*

*"The single return point architecture makes debugging so much easier."*

*"Pre-built guards saved me from writing the same validations 100 times."*

---

## The Name: Why Móðguðr?

In Norse mythology, **Móðguðr** (*"Furious Battler"*) is the guardian of Gjallarbrú, the golden-roofed bridge spanning the river Gjöll on the path to Hel. She stands at this critical boundary, demanding that all who would cross must first state their name and business.

Just like this legendary guardian, `modgud` stands watch at your function boundaries—and yes, we know it also sounds like "good mods" for your Python code! 😊 After all, what better way to enhance your functions than with some good mods that guard them like a Norse goddess?

This ancient guardian embodies exactly what this library does:

- **Guards the Boundary**: Just as Móðguðr guards the bridge to the underworld, our guards protect function boundaries
- **Demands Identification**: Móðguðr requires travelers to identify themselves; our guards require parameters to validate themselves
- **Controls Passage**: Only the worthy may cross her bridge; only valid inputs enter your functions
- **Maintains Order**: She prevents chaos at the boundary; we prevent bad data from corrupting your logic

Your functions are sacred spaces. They deserve a guardian at the gate—and perhaps some good mods to make them even better!

---

## Expression-Oriented Programming: Finally in Python

Most modern languages have embraced [expression-oriented programming](https://en.wikipedia.org/wiki/Expression-oriented_programming_language):

- **Ruby**: Everything is an expression
- **Rust**: if, match, and blocks are expressions
- **Scala**: Unified expression model
- **Kotlin**: When expressions, if expressions
- Even **JavaScript**: Arrow functions with implicit returns

Python has been left behind—until now.

### What is Expression-Oriented Programming?

In [expression-oriented languages](https://en.wikipedia.org/wiki/Expression-oriented_programming_language), nearly every construct yields a value. This isn't just syntactic sugar—it's a fundamental paradigm shift that leads to:

- **Cleaner code**: No unnecessary intermediate variables
- **Better composability**: Everything can be chained and combined
- **Functional thinking**: Focus on transformations, not procedures
- **Less boilerplate**: The language works with you, not against you

### Why It Matters

Expression-oriented programming isn't about being clever—it's about writing code that expresses intent clearly:

```python
# Statement-oriented (traditional Python)
def get_status(user):
    if user.is_active:
        if user.is_premium:
            status = "premium_active"
        else:
            status = "standard_active"
    else:
        status = "inactive"
    return status

# Expression-oriented (with modgud)
from modgud import guarded_expression, implicit_return

@guarded_expression()
@implicit_return
def get_status(user):
    if user.is_active:
        "premium_active" if user.is_premium else "standard_active"
    else:
        "inactive"
```

The second version isn't just shorter—it's *clearer*. The code structure mirrors the logic structure. No hunting for return statements. No temporary variables. Just pure intent.

### Bringing Expressions to Python

With modgud, Python developers can finally write in an expression-oriented style:

- **Implicit Returns**: The last expression in each branch becomes the return value
- **Single Return Point**: One logical exit, multiple paths to get there
- **Clean Composition**: Guards handle preconditions, your code handles logic

```python
# Complex business logic, expression style
from modgud import guarded_expression, implicit_return, not_none, positive

@guarded_expression(
    not_none("order"),
    positive("discount_rate")
)
@implicit_return
def calculate_final_price(order, discount_rate, is_premium):
    base_price = order.total
    if is_premium:
        if base_price > 100:
            base_price * (1 - discount_rate * 1.5)  # Premium + bulk discount
        else:
            base_price * (1 - discount_rate * 1.2)  # Premium discount only
    else:
        if base_price > 100:
            base_price * (1 - discount_rate)        # Standard bulk discount
        else:
            base_price                               # No discount
```

Every branch yields a value. No `return` keywords cluttering the logic. The code reads like a mathematical expression, not a procedure.

---

## 📚 Documentation

Ready to dive deeper?

- **[⚙️ How It Works](docs/how-it-works.md)** - Deep dive into AST transformation and the magic behind implicit returns
- **[📖 API Reference](docs/api-reference.md)** - Complete API documentation for all decorators and guards
- **[📚 Full Documentation Hub](docs/README.md)** - Usage examples, migration guide, and advanced patterns
- **[🏛️ Architecture](docs/architecture/README.md)** - Clean architecture design principles
- **[GitHub Repository](https://github.com/terracoil/modgud)** - Source code, issues, contributions
- **[PyPI Package](https://pypi.org/project/modgud/)** - Official releases

---

## Philosophy

Like **Móðguðr** (*"Furious Battler"*), the bridge guardian of Norse mythology who demands souls state "their name and business" before crossing to the underworld, **modgud** stands guard at your function boundaries—ensuring only valid inputs pass through while maintaining clean, predictable code flow.

Your functions should focus on *what they do*, not on validating *what they receive*. Guards handle the boundary. Your code handles the logic.

**Single return point. Single responsibility. Single source of truth.**

---

## 🎯 New in v0.3.0: Composable Expression Decorators

**modgud now provides two complementary decorators that work beautifully together:**

### Recommended Pattern
```python
from modgud import guarded_expression, implicit_return

# Combine both decorators for full power
@guarded_expression(not_none("x"), positive("x"))
@implicit_return
def process(x):
    result = x * 2
    result  # Clean implicit return
```

### Individual Use Cases
```python
# Guards only (traditional explicit returns)
@guarded_expression(not_none("x"), positive("x"))
def calculate(x):
    return x * 2

# Expression-orientation only (no guards)
@implicit_return
def classify(status):
    if status == "active":
        "user_active"
    else:
        "user_inactive"
```

### Migration Path
The unified approach still works (with deprecation warning):
```python
# Legacy approach (deprecated but functional)
@guarded_expression(not_none("x"), implicit_return=True)  # ⚠️ Deprecated parameter
def legacy_function(x):
    x * 2
```

**Why the change?** This separation enables cleaner composition with future expression-oriented decorators and gives you more flexibility in how you structure your functions.

---

## 📦 Installation

```bash
# Using pip
pip install modgud

# Using Poetry
poetry add modgud
```

**Requirements:** Python 3.13+

---

## 🤝 Contributing

Contributions welcome! This is a young project with huge potential.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Add your changes with tests
4. Run the test suite: `poetry run pytest`
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ✨ What's New in v1.1

### 🏛️ Architecture Improvements

- **BREAKING:** Removed all deprecated module-level registry functions
  - Old: `register_guard()`, `get_guard()`, `list_custom_guards()`, etc.
  - New: Use `GuardRegistry.register()`, `GuardRegistry.get()`, `GuardRegistry.list_guards()`, etc.
- **NEW:** `GuardRegistry` now uses proper singleton pattern with `@classmethod` interface
- **NEW:** `CommonGuards._register_to_global_registry()` - encapsulated registration logic
- **IMPROVED:** Better code organization - all functionality properly encapsulated in classes
- **IMPROVED:** Test coverage increased from 94% to 96%

### Migration Guide

```python
# Old way (v0.2.x - REMOVED)
from modgud import register_guard, get_guard
register_guard('my_guard', factory_fn)
guard = get_guard('my_guard')

# New way (v1.1+)
from modgud import GuardRegistry
GuardRegistry.register('my_guard', factory_fn)
guard = GuardRegistry.get('my_guard')
```

---

**Stop writing defensive code. Start writing declarative contracts.**

**Welcome to modgud. Welcome to cleaner Python.**

*Like Móðguðr at the bridge to Hel, modgud ensures only worthy inputs pass through to your functions' sacred inner workings.*
