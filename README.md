
![Modgud](https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg)

**Parent**: [📚 Documentation Hub](docs/README.md) | [📖 API Reference](docs/api-reference.md) | [⚙️ How It Works](docs/how-it-works.md)

## Finally. Expression-Oriented Programming for Python.

**Stop writing defensive spaghetti. Start writing beautiful, contract-driven code.**

Tired of functions where 80% of the code is validation boilerplate? Frustrated by nested conditionals checking types, values, and state before you can even *think* about business logic? Wish Python had expression-oriented programming like Ruby, Rust, or Scala?

**modgud changes everything.**


---

## The Name: Móðguðr, Guardian of the Bridge

In Norse mythology, **Móðguðr** (*"Furious Battler"*) stands as guardian of Gjallarbrú—the golden-roofed bridge spanning the river Gjöll on the path to Hel. Every soul seeking passage must stop and state their name and business before crossing. She is the threshold keeper, the boundary enforcer, the one who demands identification before allowing entry to sacred ground.

This is exactly what `modgud` does for your functions. Just as Móðguðr guards the bridge to the underworld, our guard clauses protect your function boundaries—challenging invalid inputs before they can corrupt your logic. And yes, we're well aware that "modgud" sounds remarkably like **"mod-good"** or **"good mods"**. That's not accidental. 😊

After all, what are expression-oriented guard clauses if not *genuinely good modifications* to Python? You're literally adding **gud mods** to your functions. The Norse goddess would approve: proper guards at every threshold, allowing only the worthy to pass. Your code deserves both mythological protection *and* some really good enhancements.

---

## 📋 Table of Contents
- [🔥️ Why Modgud](#why-modgud) - Why modgud is essential
- [⚠️ The Problem](#the-problem) - Why defensive programming gets messy
- [💡 The Solution](#the-solution) - How modgud changes everything
- [🔑 Features](#features) - Six compelling features
- [🌀 Quick Start](#quick-start) - Get started in 60 seconds
- [🔑 Key Features at a Glance](#key-features-at-a-glance) - What makes modgud special
- [🌍 Real-World Example](#real-world-example-api-endpoint) - See it in action
- [📚 Documentation](#documentation) - Complete guides and references
- [📦 Installation](#installation) - How to install
- [🤝 Contributing](#contributing) - Join the project

---
## 🔥 Why Modgud?

Despite Python's evolution toward more functional features (pattern matching in 3.10+, better type hints, etc.), modgud fills a critical gap: **making Python functions behave like expressions without changing Python's syntax**. This is uniquely valuable because:

### 1. **Zero-Syntax-Cost Expression Orientation**
While Python 3.10+ adds pattern matching, it's still statement-based. modgud's `@guarded_expression` transforms regular functions into expression-oriented code *today*, running on Python 3.11+ codebases. You get Haskell-like guards and implicit returns without waiting for PEP acceptance or version upgrades.

### 2. **Gradual Adoption Path**
Unlike heavy functional libraries (PyMonad, toolz, etc.) that require wholesale architectural changes, modgud decorators can be applied selectively. Start with one critical function, see the benefits, expand gradually. This pragmatic approach reduces resistance in teams unfamiliar with FP.

### 3. **Pythonic Integration**
Rather than forcing Haskell or Scala idioms into Python, modgud enhances Python's existing decorator pattern. This feels natural to Python developers while delivering expression-oriented benefits. No new operators, no category theory, just cleaner functions.

### 4. **Performance Without Overhead**
Many FP libraries introduce abstraction penalties through wrapper objects and indirection. modgud does its AST rewrite once at decoration time, so guarded functions run with minimal runtime overhead—suitable for performance-sensitive code where other FP solutions might be rejected.

### 5. **Modern Python Baseline**
Targeting Python 3.11+ means modgud leans on `ExceptionGroup`, structural pattern matching, and precise typing—giving you modern expression-oriented patterns without dragging along legacy compatibility shims.


## ⚠️ The Problem

Look familiar?

```python
class PaymentProcessor:
  @staticmethod
  def process_payment(user_id, amount, payment_method):
    # Validation hell begins...
    if user_id is None:
      return {'error': 'User ID required'}

    if not isinstance(user_id, int):
      return {'error': 'Invalid user ID type'}

    if user_id <= 0:
      return {'error': 'User ID must be positive'}

    if amount is None or amount <= 0:
      return {'error': 'Invalid amount'}

    if amount > 10000:
      return {'error': 'Amount exceeds limit'}

    if not payment_method or payment_method == '':
      return {'error': 'Payment method required'}

    if payment_method not in ['card', 'bank', 'crypto']:
      return {'error': 'Invalid payment method'}

    # Finally, the actual business logic (if you can find it)
    transaction = create_transaction(user_id, amount, payment_method)
    return {'success': True, 'transaction_id': transaction.id}
```

**7 validation checks. A wall of defensive code. 2 lines of actual business logic.**

Multiple return points everywhere. Business logic buried at the bottom. Error handling inconsistent. This is what happens when validation and logic mix.

---

## 💡 The Solution

**modgud** gives you guard clauses and expression-oriented programming in Python:

```python
from enum import Enum

from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


class PaymentMethod(Enum):
  CARD = 'card'
  BANK = 'bank'
  CRYPTO = 'crypto'


class PaymentProcessor:
  @staticmethod
  @guarded_expression(
    CommonGuards.type_check(int, 'user_id'),
    CommonGuards.positive('user_id'),
    CommonGuards.in_range(1, 10000, 'amount', position=1),
    CommonGuards.valid_enum(PaymentMethod, 'payment_method', position=2),
    strategy=GuardFailureEnum.RETURN_VALUE,
    on_failure={'success': False, 'error': 'Validation failed'},
  )
  def process_payment(user_id, amount, payment_method):
    transaction = create_transaction(user_id, amount, payment_method)
    {'success': True, 'transaction_id': transaction.id}  # Implicit return!
```

**Same functionality. Zero defensive clutter. Single return point. Business logic front and center.**

Note the `position=` offsets: `CommonGuards` reads the first positional argument by default, so guards on the second and third parameters declare `position=1` and `position=2`.

---

## 🔑 Features

### 1. 🛡️ Guard Clauses That Actually Work

Declare your function's contract upfront. Validations execute before your function runs. Guards fail fast. No more deeply nested if statements cluttering your business logic.

**Before:**
```python
class Account:
  @staticmethod
  def withdraw(account_id, amount):
    if account_id is None:
      raise ValueError('Account required')
    if amount <= 0:
      raise ValueError('Amount must be positive')
    if amount > get_balance(account_id):
      raise ValueError('Insufficient funds')

    # Actual work hidden at the bottom
    balance = get_balance(account_id) - amount
    update_balance(account_id, balance)
    return balance
```

**After:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class AccountGuards:
  @staticmethod
  def sufficient_funds(*args, **kwargs):
    account_id = kwargs.get('account_id', args[0] if args else None)
    amount = kwargs.get('amount', args[1] if len(args) > 1 else 0)
    return amount <= get_balance(account_id) or 'Insufficient funds'


class Account:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('account_id'),
    CommonGuards.positive('amount', position=1),
    AccountGuards.sufficient_funds,
  )
  def withdraw(account_id, amount):
    balance = get_balance(account_id) - amount
    update_balance(account_id, balance)
    balance  # Clean implicit return
```

Custom guards receive the *full* argument tuple as `(*args, **kwargs)`, so they pull the values they need by name or position and return `True` (pass) or an error `str` (fail).

### 2. 🎨 Expression-Oriented Programming (Finally!)

The last expression in each branch is your return value. Just like Ruby, Rust, Scala, and every other modern language. No more cluttered `return` statements everywhere.

**Before:**
```python
class UserClassifier:
  @staticmethod
  def classify(age, premium):
    if age < 18:
      return 'minor'
    elif premium:
      return 'premium_adult'
    else:
      return 'standard_adult'
```

**After:**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class UserClassifier:
  @staticmethod
  @guarded_expression(CommonGuards.positive('age'))
  def classify(age, premium):
    if age < 18:
      'minor'
    elif premium:
      'premium_adult'
    else:
      'standard_adult'
```

Clean. Readable. Expressive. The way code should be.

### 3. 🎖️ Single Return Point Architecture

Every function has exactly one logical exit point. Easier debugging. Clearer control flow. No hunting through nested conditionals for hidden `return` statements.

Guards handle early exits. Your function handles business logic. Separation of concerns at its finest.

### 4. 🧩 Pre-Built Guards

Stop writing the same validations over and over:

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class Registration:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('email'),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email'),
    CommonGuards.in_range(13, 120, 'age', position=1),
    CommonGuards.not_empty('username', position=2),
  )
  def register_user(email, age, username):
    user_id = create_user_record(email, age, username)
    send_welcome_email(email)
    {'success': True, 'user_id': user_id}
```

Built-in guards for:
- `not_none` - Ensure values exist
- `not_empty` - Validate collections/strings have content
- `positive` - Numeric validation
- `in_range` - Bounded value checking
- `type_check` - Runtime type validation
- `matches_pattern` - Regex pattern matching
- `valid_file_path` / `valid_url` / `valid_enum` - Richer domain checks

Plus you can write custom guards in seconds.

#### Creating Custom Guards

Register your own reusable guards. Guard factories live as static methods (no loose functions), and the guard they return accepts the full argument tuple:

```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import GuardRegistry


class AgeGuards:
  @staticmethod
  def valid_age(min_age=0, max_age=150, param_name='age', position=0):
    def check(*args, **kwargs):
      age = kwargs.get(param_name, args[position] if position < len(args) else None)
      result = True
      if not isinstance(age, int):
        result = f'{param_name} must be an integer'
      elif not (min_age <= age <= max_age):
        result = f'{param_name} must be between {min_age} and {max_age}'
      return result

    return check


# Register it for reuse
GuardRegistry.register('valid_age', AgeGuards.valid_age)


class Voting:
  @staticmethod
  @guarded_expression(GuardRegistry.get('valid_age')(min_age=18, max_age=120))
  def can_vote(age):
    age >= 18
```

### 5. 🎛️ Flexible Error Handling

Your code, your rules. A single `GuardFailureEnum` enum, paired with an `on_failure` payload, chooses how guards fail:

**Return custom values (`RETURN_VALUE`):**

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


class Billing:
  @staticmethod
  @guarded_expression(
    CommonGuards.positive('amount'),
    strategy=GuardFailureEnum.RETURN_VALUE,
    on_failure={'error': 'Invalid amount', 'code': 400},
  )
  def process(amount):
    {'success': True, 'amount': amount}
```

**Raise exceptions (`ERROR_RAISE`, the default):**
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class Accounts:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_empty('username'),
    on_failure=ValueError,
  )
  def create_account(username):
    Account(username)
```

**Custom handlers (`CALL_HANDLER`):** the handler is invoked as `on_failure(errors, *args, **kwargs)`, where `errors` is always a `list[str]`:

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


class SecurityAudit:
  @staticmethod
  def record(errors, *args, **kwargs):
    log_security_event(errors)
    return None


class SensitiveOps:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_empty('api_key'),
    strategy=GuardFailureEnum.CALL_HANDLER,
    on_failure=SecurityAudit.record,
  )
  def run(api_key):
    perform_operation()
```

### 6. 📦 One Tiny Dependency

Apart from the standard library, modgud depends only on [Idunn](https://pypi.org/project/idunn), a tiny constructor-time IoC toolkit that wires the decorators to their implementations. No other bloat, no version tangles.

### 7. ✅ Battle-Tested & Type-Safe

- Full mypy type checking support (strict settings)
- Comprehensive test suite (135 passing tests)
- Clean architecture with separation of concerns
- Thread-safe decorators
- Preserves all function metadata for debugging

---

## 🌀 Quick Start

### 📦 Installation

```bash
pip install modgud
```

**Requirements:** Python 3.11+

### Your First Guarded Function

```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.common import CommonGuards


# Option 1: Unified approach (recommended for simple cases)
class DiscountCalculator:
  @staticmethod
  @guarded_expression(
    CommonGuards.positive('x'),
    CommonGuards.in_range(1, 100, 'x'),
  )
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1


# Option 2: Separate decorators (for complex compositions)
class DiscountCalculatorV2:
  @staticmethod
  @guarded_expression(
    CommonGuards.positive('x'),
    CommonGuards.in_range(1, 100, 'x'),
    implicit_return=False,
  )
  @implicit_return()
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1


DiscountCalculator.calculate(75)  # Returns 15.0
DiscountCalculator.calculate(25)  # Returns 2.5
# DiscountCalculator.calculate(-10) would raise GuardClauseError
```

**That's it.** You're writing cleaner Python.

---

## 🔑 Key Features at a Glance

- **🎨 Implicit Returns by Default** - Last expression in each branch is auto-returned (like Ruby/Rust/Scala)
- **🛡️ Guard Clause Decorators** - Validate inputs before function execution
- **🎯 Single Return Point** - One logical exit point per function
- **🧩 Pre-Built Guards** - Standard validations ready to use (not_none, positive, in_range, type_check, etc.)
- **📝 Custom Guard Registry** - Create and register reusable validation guards
- **🎛️ Configurable Failure Strategies** - Raise, return an exception, return a value, or call a handler
- **📊 Failure Collection** - `continuance` gathers multiple failures into an `ExceptionGroup`
- **🏛️ Clean Architecture** - Per-feature decomposition with ports + adapters
- **📦 One Tiny Dependency** - Standard library plus [Idunn](https://pypi.org/project/idunn) for port/adapter wiring
- **✅ Type-Safe** - Full mypy support with proper type hints
- **🔒 Thread-Safe** - No shared mutable state
- **🧪 Well-Tested** - 135 passing tests across the guard runtime, AST transformer, wiring and architecture

---

## 🌍 Real-World Example: API Endpoint

**Before modgud:**

```python
class UserApi:
  @staticmethod
  def create_user(email, age, username, password):
    # Validation nightmare
    if not email or email == '':
      return {'status': 400, 'error': 'Email required'}

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
      return {'status': 400, 'error': 'Invalid email format'}

    if age is None or not isinstance(age, int):
      return {'status': 400, 'error': 'Invalid age'}

    if age < 13 or age > 120:
      return {'status': 400, 'error': 'Age must be 13-120'}

    if not username or username == '':
      return {'status': 400, 'error': 'Username required'}

    if len(username) < 3 or len(username) > 20:
      return {'status': 400, 'error': 'Username must be 3-20 chars'}

    if not password or password == '':
      return {'status': 400, 'error': 'Password required'}

    # Finally, the actual work
    user_id = db.create_user(email, age, username, hash_password(password))
    return {'status': 200, 'user_id': user_id}
```

**With modgud:**

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


class UserGuards:
  @staticmethod
  def username_length(*args, **kwargs):
    username = kwargs.get('username', args[2] if len(args) > 2 else '')
    return 3 <= len(username) <= 20 or 'Username must be 3-20 chars'


class UserApi:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_empty('email'),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email'),
    CommonGuards.type_check(int, 'age', position=1),
    CommonGuards.in_range(13, 120, 'age', position=1),
    CommonGuards.not_empty('username', position=2),
    UserGuards.username_length,
    CommonGuards.not_empty('password', position=3),
    strategy=GuardFailureEnum.RETURN_VALUE,
    on_failure={'status': 400, 'error': 'Validation failed'},
  )
  def create_user(email, age, username, password):
    user_id = db.create_user(email, age, username, hash_password(password))
    {'status': 200, 'user_id': user_id}
```

**A wall of defensive checks collapses into a declarative contract. Zero clutter. 100% focus on business logic.**

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
class StatusService:
  @staticmethod
  def get_status(user):
    if user.is_active:
      if user.is_premium:
        status = 'premium_active'
      else:
        status = 'standard_active'
    else:
      status = 'inactive'
    return status
```

```python
# Expression-oriented (with modgud)
from modgud.app import guarded_expression


class StatusService:
  @staticmethod
  @guarded_expression()
  def get_status(user):
    if user.is_active:
      'premium_active' if user.is_premium else 'standard_active'
    else:
      'inactive'
```

The second version isn't just shorter—it's *clearer*. The code structure mirrors the logic structure. No hunting for return statements. No temporary variables. Just pure intent.

### Bringing Expressions to Python

With modgud, Python developers can finally write in an expression-oriented style:

- **Implicit Returns**: The last expression in each branch becomes the return value
- **Single Return Point**: One logical exit, multiple paths to get there
- **Clean Composition**: Guards handle preconditions, your code handles logic

```python
# Complex business logic, expression style
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


class Pricing:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('order'),
    CommonGuards.positive('discount_rate', position=1),
  )
  def calculate_final_price(order, discount_rate, is_premium):
    base_price = order.total
    if is_premium:
      if base_price > 100:
        base_price * (1 - discount_rate * 1.5)  # Premium + bulk discount
      else:
        base_price * (1 - discount_rate * 1.2)  # Premium discount only
    else:
      if base_price > 100:
        base_price * (1 - discount_rate)  # Standard bulk discount
      else:
        base_price  # No discount
```

Every branch yields a value. No `return` keywords cluttering the logic. The code reads like a mathematical expression, not a procedure.

---

## 📚 Documentation

Ready to dive deeper?

- **[⚙️ How It Works](docs/how-it-works.md)** - Deep dive into AST transformation and the magic behind implicit returns
- **[📖 API Reference](docs/api-reference.md)** - Complete API documentation for all decorators and guards
- **[📚 Full Documentation Hub](docs/README.md)** - Usage examples and advanced patterns
- **[🏛️ Architecture](docs/architecture/README.md)** - Clean architecture design principles
- **[GitHub Repository](https://github.com/terracoil/modgud)** - Source code, issues, contributions
- **[PyPI Package](https://pypi.org/project/modgud/)** - Official releases

---

## Philosophy

Like **Móðguðr** (*"Furious Battler"*), the bridge guardian of Norse mythology who demands souls state "their name and business" before crossing to the underworld, **modgud** stands guard at your function boundaries—ensuring only valid inputs pass through while maintaining clean, predictable code flow.

Your functions should focus on *what they do*, not on validating *what they receive*. Guards handle the boundary. Your code handles the logic.

**Single return point. Single responsibility. Single source of truth.**

---

## 🎯 Usage Patterns: Two Equally Valid Approaches

**modgud supports two patterns for combining guards with implicit returns. Choose based on your needs:**

### Pattern 1: Unified Parameter (Simple, All-in-One)
```python
from modgud.app import guarded_expression
from modgud.infrastructure.common import CommonGuards


# Everything configured in one decorator (implicit_return=True is the default)
class Processor:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('x'),
    CommonGuards.positive('x'),
  )
  def process(x):
    result = x * 2
    result  # Clean implicit return
```

**Best for:**
- Simple functions with guards and implicit returns
- When you want all configuration in one place
- Teaching/learning scenarios
- Functions where the transformation is core to the function's identity

### Pattern 2: Separate Decorators (Flexible, Composable)
```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.common import CommonGuards


# Separate concerns with multiple decorators
class Processor:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('x'),
    CommonGuards.positive('x'),
    implicit_return=False,
  )
  @implicit_return()
  def process(x):
    result = x * 2
    result  # Clean implicit return
```

**Best for:**
- Complex decorator compositions
- When implicit return is optional/conditional
- Reusable decorator stacks
- Maximum flexibility

### ⚠️ Composition Order Warning

When stacking `@guarded_expression` (with `implicit_return=False`) on top of `@implicit_return()`, **order matters** — guards go on the outside, the implicit-return transform closest to the `def`:

```python
# ✅ CORRECT: Guards wrap the implicit-return transform
# illustrative — shows correct vs incorrect stacking order
@guarded_expression(CommonGuards.positive('x'), implicit_return=False)
@implicit_return()
def correct(x):
  x * 2

# ❌ PROBLEMATIC: Implicit-return outermost may bypass guards
@implicit_return()
@guarded_expression(CommonGuards.positive('x'))
def problematic(x):
  x * 2
```

### Individual Use Cases
```python
from modgud.app import guarded_expression, implicit_return
from modgud.infrastructure.common import CommonGuards


# Guards only (traditional explicit returns)
class Calc:
  @staticmethod
  @guarded_expression(
    CommonGuards.not_none('x'),
    CommonGuards.positive('x'),
    implicit_return=False,
  )
  def calculate(x):
    return x * 2


# Expression-orientation only (no guards)
class Classifier:
  @staticmethod
  @implicit_return()
  def classify(status):
    if status == 'active':
      'user_active'
    else:
      'user_inactive'
```

**Both patterns are first-class citizens in modgud. Choose the one that best fits your use case!**

---

## 📦 Installation

```bash
# Using pip
pip install modgud

# Using Poetry
poetry add modgud
```

**Requirements:** Python 3.11+

### 🔌 Idunn Interop

modgud wires its decorators to their implementations through [Idunn](https://pypi.org/project/idunn). A few things follow from that:

- The first `@guarded_expression(...)` or `@implicit_return()` lazily creates the process-wide `Idunn()` singleton and discovers modgud's ports and adapters. Later `Idunn(environment=...)` arguments are ignored, so pick an environment with `IDUNN_ENV` or `Idunn().reset(environment=...)` *before* the first decoration. modgud re-discovers itself on the next decoration after any `reset()`.
- An invalid `IDUNN_ENV` (Idunn accepts `[a-z0-9][a-z0-9.-]*` after normalising) makes decoration fail with Idunn's error.
- `@implicit_return()` now takes parentheses, like `@guarded_expression(...)`; the bare `@implicit_return` form is gone.
- Both decorators accept their implementation as a keyword (`transformer=`, and `runtime=` on `guarded_expression`) so tests can pass a fake.

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

**Stop writing defensive code. Start writing declarative contracts.**

**Welcome to modgud. Welcome to cleaner Python.**

*Like Móðguðr at the bridge to Hel, modgud ensures only worthy inputs pass through to your functions' sacred inner workings.*
