# Modgud

**Móðguðr** (*"Furious Battler"*) is the bridge guardian of Norse mythology who controls passage to the underworld, demanding that souls state "their name and business" before crossing the golden-roofed Gjallarbrú. Like her mythological namesake, this library stands guard at the boundaries of your functions—ensuring only valid inputs pass through while maintaining clean, predictable code flow with single return points.

**Modgud** provides Python decorators for guard clauses and implicit return validation, enforcing defensive programming patterns while keeping your code readable and maintainable.

## Features

- 🛡️ **Guard Clauses**: Validate function inputs with composable decorators
- 📏 **Single Return Point**: Maintain clean function architecture
- 🔧 **Common Guards**: Pre-built validators for typical scenarios
- ⚡ **Implicit Returns**: Automatically return the last assigned variable
- 🎯 **Flexible Error Handling**: Custom return values, handlers, or exceptions
- 📝 **Zero Dependencies**: Built on Python standard library only
- 🧪 **Fully Tested**: Comprehensive test suite with 100% coverage

## Installation

```bash
pip install modgud
```

**Requirements:** Python 3.13+

## Quick Start

### Guard Clauses

```python
from modgud import guard_clause, CommonGuards

# Basic guard clause
@guard_clause(
    lambda x: x > 0 or "Value must be positive",
    lambda x: x < 1000 or "Value too large"
)
def calculate_discount(amount):
    discount = amount * 0.1
    return discount

# Returns 10.0
result = calculate_discount(100)

# Returns None (guard failed)
result = calculate_discount(-50)
```

### Common Guards

```python
@guard_clause(
    CommonGuards.not_none("email"),
    CommonGuards.matches_pattern(r"^[\w\.-]+@[\w\.-]+\.\w+$", "email"),
    CommonGuards.positive("age"),
    CommonGuards.in_range(18, 120, "age")
)
def register_user(email, age):
    user_id = generate_user_id()
    return {"id": user_id, "email": email, "age": age}
```

### Custom Error Handling

```python
# Return custom values on failure
@guard_clause(
    CommonGuards.positive("amount"),
    on_error={"error": "Invalid amount", "code": 400}
)
def process_payment(amount):
    transaction_id = create_transaction(amount)
    return {"success": True, "transaction_id": transaction_id}

# Raise exceptions on failure
@guard_clause(
    CommonGuards.not_empty("username"),
    on_error=ValueError
)
def create_account(username):
    account = Account(username)
    return account

# Custom handler functions
def audit_failure(error_msg, *args, **kwargs):
    log_security_event(error_msg, args, kwargs)
    return {"error": "Access denied"}

@guard_clause(
    lambda api_key: validate_api_key(api_key) or "Invalid API key",
    on_error=audit_failure,
    log=True
)
def sensitive_operation(api_key):
    result = perform_operation()
    return result
```

### Implicit Returns

```python
from modgud import implicit_return

@implicit_return
def calculate_total(items):
    subtotal = sum(item.price for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax
    # Automatically returns 'total' (last assigned variable)

@implicit_return
def process_data(raw_data):
    cleaned = clean_data(raw_data)
    validated = validate_data(cleaned)
    result = transform_data(validated)
    # Returns 'result'
```

## API Reference

### Guard Clause Decorator

```python
@guard_clause(*guards, on_error=None, log=False)
```

**Parameters:**
- `*guards`: Guard functions that return `True` or error message string
- `on_error`: Failure behavior - value, callable, or exception class (default: `None`)
- `log`: Enable logging of guard failures (default: `False`)

### Common Guards

Pre-built guard functions for typical validation scenarios:

```python
CommonGuards.not_none(param_name, position=0)
CommonGuards.not_empty(param_name, position=None)
CommonGuards.positive(param_name, position=0)
CommonGuards.in_range(min_val, max_val, param_name, position=0)
CommonGuards.type_check(expected_type, param_name, position=0)
CommonGuards.matches_pattern(pattern, param_name, position=0)
```

### Error Handling Options

**Return Custom Values:**
```python
on_error="INVALID"                    # Return string
on_error={"error": True}              # Return dict  
on_error=[]                           # Return empty list
on_error=42                           # Return number
```

**Use Handler Functions:**
```python
def custom_handler(error_msg, *args, **kwargs):
    # Log, audit, or transform error
    return processed_result

on_error=custom_handler
```

**Raise Exceptions:**
```python
on_error=ValueError                   # Built-in exceptions
on_error=GuardClauseError            # Custom exception class
```

## Real-World Examples

### User Registration System

```python
from modgud import guard_clause, CommonGuards

@guard_clause(
    CommonGuards.not_none("username"),
    CommonGuards.not_empty("username"),
    CommonGuards.in_range(3, 20, "username"),  # Length validation
    CommonGuards.matches_pattern(r"^[a-zA-Z0-9_]+$", "username"),
    CommonGuards.not_none("email"),
    CommonGuards.matches_pattern(r"^[\w\.-]+@[\w\.-]+\.\w+$", "email"),
    CommonGuards.positive("age"),
    CommonGuards.in_range(13, 120, "age"),
    on_error={"success": False, "error": "Validation failed"},
    log=True
)
def register_user(username, email, age):
    user_id = create_user_record(username, email, age)
    send_welcome_email(email)
    return {"success": True, "user_id": user_id}
```

### Payment Processing

```python
@guard_clause(
    CommonGuards.positive("amount"),
    lambda amount: amount <= 10000 or "Amount exceeds daily limit",
    CommonGuards.not_empty("card_number"),
    lambda card: validate_luhn(card) or "Invalid card number",
    on_error={"status": "failed", "code": "VALIDATION_ERROR"},
    log=True
)
def process_payment(amount, card_number, cvv):
    transaction = charge_card(amount, card_number, cvv)
    return {"status": "success", "transaction_id": transaction.id}
```

### API Endpoint Validation

```python
@guard_clause(
    CommonGuards.positive("user_id"),
    lambda page=1: page >= 1 or "Page must be at least 1",
    lambda limit=10: 1 <= limit <= 100 or "Limit must be 1-100",
    lambda sort="date": sort in ["date", "name", "status"] or "Invalid sort field",
    on_error={"error": "Bad Request", "status": 400}
)
def get_user_posts(user_id, page=1, limit=10, sort="date"):
    posts = fetch_posts(user_id, page, limit, sort)
    return {"posts": posts, "page": page, "total": len(posts)}
```

## Architecture Principles

### Single Return Point

All decorated functions maintain a single return statement as the last line:

```python
@guard_clause(CommonGuards.positive("x"))
def process_value(x):
    # Guard failures are handled by decorator
    # Function only executes if all guards pass
    intermediate = x * 2
    result = intermediate + 10
    return result  # Single return point
```

### Guard Evaluation Order

Guards are evaluated sequentially and fail fast:

```python
@guard_clause(
    cheap_validation,      # Fast checks first
    moderate_validation,   # Medium cost checks
    expensive_validation   # Expensive checks last
)
def optimized_function(data):
    return process(data)
```

### Composability

Guards can be combined and reused:

```python
# Define reusable guard combinations
user_validation = [
    CommonGuards.not_none("user_id"),
    CommonGuards.positive("user_id"),
    lambda user_id: user_exists(user_id) or "User not found"
]

@guard_clause(*user_validation, log=True)
def get_user_profile(user_id):
    return fetch_profile(user_id)

@guard_clause(*user_validation, log=True)  
def update_user_settings(user_id, settings):
    return save_settings(user_id, settings)
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[test]

# Run tests
pytest

# Run with coverage
pytest --cov=modgud --cov-report=html
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and ensure all tests pass.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`  
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### Version 0.1.0
- Initial release
- Guard clause decorators with single return point architecture
- Common guard utilities for typical validation patterns  
- Flexible error handling (return values, handlers, exceptions)
- Implicit return decorators
- Comprehensive test suite
- Zero dependencies (Python stdlib only)

---

*Like Móðguðr at the bridge to Hel, Modgud ensures only worthy inputs pass through to your functions' sacred inner workings.*