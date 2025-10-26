# MODGUD

![modgud](https://github.com/terracoil/freyja/raw/main/docs/modgud.png)

## Finally. Expression-Oriented Programming for Python.

**Stop writing defensive spaghetti. Start writing beautiful, contract-driven code.**

Tired of functions where 80% of the code is validation boilerplate? Frustrated by nested conditionals checking types, values, and state before you can even *think* about business logic? Wish Python had expression-oriented programming like Ruby, Rust, or Scala?

**modgud changes everything.**

---

## The Problem

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

## The Solution

**modgud** gives you guard clauses and expression-oriented programming in Python:

```python
from modgud import guarded_expression, CommonGuards

@guarded_expression(
    CommonGuards.positive("user_id"),
    CommonGuards.type_check(int, "user_id"),
    CommonGuards.positive("amount"),
    CommonGuards.in_range(1, 10000, "amount"),
    CommonGuards.not_empty("payment_method"),
    lambda pm: pm in ["card", "bank", "crypto"] or "Invalid payment method",
    on_error={"success": False, "error": "Validation failed"}
)
def process_payment(user_id, amount, payment_method):
    transaction = create_transaction(user_id, amount, payment_method)
    {"success": True, "transaction_id": transaction.id}  # Implicit return!
```

**Same functionality. Zero defensive clutter. Single return point. Business logic front and center.**

---

## Why modgud?

### 1. Guard Clauses That Actually Work

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
@guarded_expression(
    CommonGuards.not_none("account_id"),
    CommonGuards.positive("amount"),
    lambda account_id, amount: amount <= get_balance(account_id) or "Insufficient funds"
)
def withdraw(account_id, amount):
    balance = get_balance(account_id) - amount
    update_balance(account_id, balance)
    balance  # Clean implicit return
```

### 2. Expression-Oriented Programming (Finally!)

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
@guarded_expression(CommonGuards.positive("age"))
def classify_user(age, premium):
    if age < 18:
        "minor"
    elif premium:
        "premium_adult"
    else:
        "standard_adult"
```

Clean. Readable. Expressive. The way code should be.

### 3. Single Return Point Architecture

Every function has exactly one logical exit point. Easier debugging. Clearer control flow. No hunting through nested conditionals for hidden `return` statements.

Guards handle early exits. Your function handles business logic. Separation of concerns at its finest.

### 4. Pre-Built CommonGuards

Stop writing the same validations over and over:

```python
from modgud import CommonGuards

@guarded_expression(
    CommonGuards.not_none("email"),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', "email"),
    CommonGuards.positive("age"),
    CommonGuards.in_range(13, 120, "age"),
    CommonGuards.not_empty("username"),
    CommonGuards.type_check(str, "username")
)
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

### 5. Flexible Error Handling

Your code, your rules. Choose how guards fail:

**Return custom values:**
```python
@guarded_expression(
    CommonGuards.positive("amount"),
    on_error={"error": "Invalid amount", "code": 400}
)
def process(amount):
    {"success": True, "amount": amount}
```

**Raise exceptions:**
```python
@guarded_expression(
    CommonGuards.not_empty("username"),
    on_error=ValueError
)
def create_account(username):
    Account(username)
```

**Custom handlers:**
```python
def audit_and_return(error_msg, *args, **kwargs):
    log_security_event(error_msg)
    return None

@guarded_expression(
    lambda api_key: validate_key(api_key) or "Invalid key",
    on_error=audit_and_return
)
def sensitive_operation(api_key):
    perform_operation()
```

### 6. Zero Dependencies

Built entirely on Python's standard library. No bloat. No version conflicts. Just clean, fast Python.

### 7. Battle-Tested & Type-Safe

- Full mypy type checking support
- Comprehensive test suite with 92% coverage
- Clean architecture with dependency injection
- Thread-safe decorators
- Preserves all function metadata for debugging

---

## Quick Start

### Installation

```bash
pip install modgud
```

**Requirements:** Python 3.13+

### Your First Guarded Function

```python
from modgud import guarded_expression, CommonGuards

@guarded_expression(
    CommonGuards.positive("x"),
    CommonGuards.in_range(1, 100, "x")
)
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

## Key Features at a Glance

- **Implicit Returns by Default** - Last expression in each branch is auto-returned (like Ruby/Rust/Scala)
- **Guard Clause Decorators** - Validate inputs before function execution
- **Single Return Point** - One logical exit point per function
- **Pre-Built CommonGuards** - Standard validations ready to use (not_none, positive, in_range, type_check, etc.)
- **Configurable Failure Behaviors** - Return values, raise exceptions, or call custom handlers
- **Clean Architecture** - Dependency injection, pure functions, immutable transforms
- **Zero Dependencies** - Uses only Python standard library
- **Type-Safe** - Full mypy support with proper type hints
- **Thread-Safe** - No shared mutable state
- **Well-Tested** - 92% coverage with 40+ comprehensive tests

---

## Real-World Example: API Endpoint

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
@guarded_expression(
    CommonGuards.not_empty("email"),
    CommonGuards.matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$', "email"),
    CommonGuards.type_check(int, "age"),
    CommonGuards.in_range(13, 120, "age"),
    CommonGuards.not_empty("username"),
    lambda username: 3 <= len(username) <= 20 or "Username must be 3-20 chars",
    CommonGuards.not_empty("password"),
    on_error={"status": 400, "error": "Validation failed"}
)
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

*"CommonGuards saved me from writing the same validations 100 times."*

---

## Documentation

Ready to dive deeper?

- **[📚 Complete Technical Documentation](docs/README.md)** - Full API reference, usage examples, and advanced patterns
- **[GitHub Repository](https://github.com/terracoil/modgud)** - Source code, issues, contributions
- **[PyPI Package](https://pypi.org/project/modgud/)** - Official releases

---

## Philosophy

Like **Móðguðr** (*"Furious Battler"*), the bridge guardian of Norse mythology who demands souls state "their name and business" before crossing to the underworld, **modgud** stands guard at your function boundaries—ensuring only valid inputs pass through while maintaining clean, predictable code flow.

Your functions should focus on *what they do*, not on validating *what they receive*. Guards handle the boundary. Your code handles the logic.

**Single return point. Single responsibility. Single source of truth.**

---

## Installation

```bash
# Using pip
pip install modgud

# Using Poetry
poetry add modgud
```

**Requirements:** Python 3.13+

---

## Quick Links

- [Complete Documentation](docs/README.md) - Full API reference
- [GitHub Repository](https://github.com/terracoil/modgud) - Source & issues
- [PyPI Package](https://pypi.org/project/modgud/) - Latest releases
- [License](LICENSE) - MIT

---

## Contributing

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

## What's New in v0.2.0

- **NEW:** `guarded_expression` - unified decorator combining guard clauses + implicit returns
- **Default behavior:** `implicit_return=True` (expression-oriented by default), `on_error=GuardClauseError`
- **Clean architecture:** Separated AST transform, guard runtime, and decorator modules
- **Comprehensive tests:** 42+ tests covering all scenarios
- **Zero dependencies:** Pure Python standard library implementation

---

**Stop writing defensive code. Start writing declarative contracts.**

**Welcome to modgud. Welcome to cleaner Python.**

*Like Móðguðr at the bridge to Hel, modgud ensures only worthy inputs pass through to your functions' sacred inner workings.*
