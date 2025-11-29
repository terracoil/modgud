**Parent**: [📚 Documentation Hub](README.md) | [🌉 Main README](../README.md) | [📖 API Reference](api-reference.md)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     EXPRESSION-ORIENTED PROGRAMMING FEATURES                  ║
║                               FOR MODGUD v1.2.6+                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎯 CURRENT IMPLEMENTATION STATUS                                           │
│  ✅ = FULLY IMPLEMENTED    🚧 = IN PROGRESS    ❌ = NOT IMPLEMENTED YET      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔥 **Current modgud Features** (Python 3.13+)

**✅ IMPLEMENTED:**
- **`@guarded_expression` decorator**: ✅ Combines guard clauses with implicit returns using AST transformation
- **`CommonGuards` class**: ✅ Pre-built validators (not_none, positive, in_range, type_check, matches_pattern, not_empty)  
- **`@safe_expression` decorator**: ✅ Automatic Result wrapping for exception handling
- **`@chained_expression` decorator**: ✅ Fluent interfaces with method chaining
- **`Maybe`/`Result` types**: ✅ Full monadic operations with `Some`/`Nothing`, `Ok`/`Err`
- **`@Inject` decorator**: ✅ Automatic dependency injection
- **`@implicit_return` decorator**: ✅ Standalone implicit return transformation
- **`@pipeable` decorator**: ✅ Functional pipeline composition with `|` operator
- **`ChainableExpression`**: ✅ Method chaining for any value with `chain()` helper
- **Configurable error handling**: ✅ Can raise exceptions, return custom values, or call handler functions
- **Zero dependencies**: ✅ Built entirely on Python's standard library
- **Expression-oriented programming**: ✅ Implicit returns from the last expression in each branch (like Ruby/Rust/Scala)

```python
# ✅ IMPLEMENTED - Current modgud usage examples
from modgud import (
    guarded_expression, safe_expression, chained_expression, 
    positive, not_none, Maybe, Result, chain
)

# Guard clauses with implicit returns
@guarded_expression(positive('x'))
def process(x):
    result = x * 2
    result  # implicit return

# Safe error handling with Result types
@safe_expression
def safe_divide(a, b):
    return a / b  # Wrapped in Ok(result) or Err(exception)

# Method chaining with fluent interfaces
result = chain(42).map(lambda x: x * 2).filter(lambda x: x > 50).unwrap()

# Monadic operations with Maybe types
user_email = Maybe.from_value(user).map(lambda u: u.email).unwrap_or("unknown")
```

---

This comprehensive analysis catalogs **additional expression-oriented programming features** that would complement and extend modgud's existing capabilities, building upon its foundation of guard clauses and implicit returns.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     📋 FEATURE IMPLEMENTATION ROADMAP                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 **Pattern Matching & Destructuring Enhancements**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION STATUS: ❌ NOT IMPLEMENTED YET                               │
│  PYTHON COMPATIBILITY: 3.6+ (polyfills) | 3.10+ (native integration)       │
│  PRIORITY: HIGH - Natural extension of guard clauses                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ❌ **Expression-Based Pattern Matching**
Python 3.10 introduced structural pattern matching through PEP 634, but several enhancements could extend this into more powerful expression-oriented patterns. **Expression-based pattern matching** would allow match statements to return values directly, enabling functional-style code where pattern matching becomes part of expression chains rather than requiring statement blocks.

```python
# ❌ NOT IMPLEMENTED - Proposed @pattern_matched decorator
@pattern_matched
@guarded_expression
def describe_shape(shape):
    match shape:
        case Point(x, y): f"Point at ({x}, {y})"
        case Circle(_, radius): f"Circle with radius {radius}"
        case Rectangle(_, width, height): f"Rectangle {width}x{height}"
        case _: "Unknown shape"
```

### ❌ **Guard Combinators for Pattern Matching**
While Python 3.10 supports guards in match statements with `if` clauses, **dedicated guard combinators** could provide composable validation with modgud's existing guard system.

```python
# ❌ NOT IMPLEMENTED - Proposed guard combinator integration
from modgud import all_of, any_of, none_of, positive, less_than

@guarded_expression
def classify_point(point):
    match point:
        case Point(x, y) if all_of(positive, less_than(100))(x, y):
            "small positive quadrant"
        case Point(x, y) if any_of(lambda n: n < 0)(x, y):
            "has negative coordinate"
        case _:
            "other"
```

### ❌ **Destructuring Utilities**
**Destructuring utilities** for dictionaries, nested structures, and custom objects would complement pattern matching. Python's tuple unpacking works well for sequences, but deep nested extraction remains verbose.

```python
# ❌ NOT IMPLEMENTED - Proposed destructuring helpers
from modgud import pluck, destructure

@guarded_expression
def process_api_response(response):
    guard not response: return "No data"
    
    # Safe nested extraction with defaults
    user_name = pluck(response, 'user.profile.name', default='Anonymous')
    user_email = pluck(response, 'user.contact.email', default='')
    
    f"{user_name} <{user_email}>"

# Alternative destructuring syntax
@destructured
@guarded_expression  
def handle_config(config):
    {
        'database': {'host': db_host, 'port': db_port},
        'redis': {'url': redis_url}
    } = config
    
    f"DB: {db_host}:{db_port}, Redis: {redis_url}"
```

### ❌ **Pattern Matching Polyfills (Python 3.6-3.9)**
For backward compatibility, **pattern matching polyfills** would provide crucial support for older Python versions using modgud's AST transformation capabilities.

```python
# ❌ NOT IMPLEMENTED - Proposed pattern matching backport
@pattern_matched  # Uses AST transformation for 3.6-3.9
@guarded_expression
def handle_response(response):
    match response:
        case {'status': 200, 'data': data}: 
            process_success(data)
        case {'status': int(code)} if 400 <= code < 500:
            handle_client_error(code)
        case {'status': int(code)} if code >= 500:
            handle_server_error(code)
        case _:
            "Invalid response format"
```

## 🧬 **Monadic Operations & Algebraic Data Types**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION STATUS: ✅ IMPLEMENTED (CORE TYPES)                         │
│  PYTHON COMPATIBILITY: 3.13+ (current implementation)                      │
│  PRIORITY: HIGH - Essential for functional error handling                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ✅ **Maybe/Option and Result/Either Types** (IMPLEMENTED!)
Foundation of type-safe error handling without exceptions. **Maybe monad** represents optional values (Some or Nothing), eliminating null checks. **Result types** encode success/failure with typed errors, enabling railway-oriented programming.

```python
# ✅ IMPLEMENTED - Current modgud Maybe/Option and Result types
from modgud import Maybe, Result, Some, Nothing, Ok, Err

# Maybe types - handle optional values safely
user = Maybe.from_value(fetch_user_by_id(123))  # Some(user) or Nothing()
email = Maybe.some("user@example.com")
empty = Maybe.nothing()

# Result types - railway-oriented programming  
@safe_expression
def safe_divide(a, b):
    return a / b  # Automatically wrapped in Ok(result) or Err(exception)

# Direct Result creation
success = Result.ok("Success!")
failure = Result.err("Something went wrong")

# Pattern matching integration (Python 3.10+)
@guarded_expression
def handle_result(result):
    match result:
        case Ok(value): f"Success: {value}"
        case Err(error): f"Error: {error}"
```

### ✅ **Composable Monadic Operations** (IMPLEMENTED!)
Methods like `map()`, `and_then()` (bind/flatMap), and `unwrap_or()` enable chaining operations on wrapped values without explicit unwrapping.

```python
# ✅ IMPLEMENTED - Current modgud monadic chaining
from modgud import Maybe, Result, Some, Nothing

# Maybe chaining with map and and_then
user_email = Some("user@example.com") \
    .map(str.lower) \
    .map(lambda email: f"processed_{email}") \
    .unwrap_or("default@example.com")

# Result chaining for railway-oriented programming  
@safe_expression
def process_data(input_data):
    # Result automatically wraps exceptions
    processed = parse_json(input_data)  # Returns Result[dict, Exception]
    validated = processed.map(validate_schema) 
    return validated.unwrap_or({})

# Chaining with and_then for monadic composition
def safe_divide(a, b):
    return Ok(a).and_then(lambda x: Ok(x / b) if b != 0 else Err("Division by zero"))
```

### ❌ **Do-Notation / Computation Expressions**
Syntactic sugar for monadic composition using decorators and generators to make sequential operations read imperatively while maintaining functional purity.

```python
# ❌ NOT IMPLEMENTED - Proposed do-notation decorator
@do_notation(Maybe)
def calculate_total(cart_id):
    cart = yield fetch_cart(cart_id)        # Maybe[Cart]
    items = yield get_cart_items(cart)      # Maybe[List[Item]]
    prices = yield calculate_prices(items)   # Maybe[List[Price]]
    total = sum(prices)                     # Direct calculation
    return total                            # Wrapped in Maybe automatically

# Equivalent to: fetch_cart(cart_id).bind(get_cart_items).bind(calculate_prices).map(sum)
```

### ❌ **Task and IO Monads**
Separate pure from impure code. **IO monad** wraps side effects without executing them immediately. **Tasks** represent asynchronous operations as values.

```python
# ❌ NOT IMPLEMENTED - Proposed IO and Task monads  
from modgud import IO, Task

@guarded_expression
def read_config():
    io_action = IO.of(lambda: open('config.json').read()) \
        .map(json.loads) \
        .map(validate_config)
    
    io_action.run()  # Only executes when explicitly run

@guarded_expression  
async def fetch_user_data(user_id):
    task = Task.of(fetch_user(user_id)) \
        .bind(lambda u: Task.of(fetch_profile(u.id))) \
        .map(merge_user_profile)
    
    await task.run()  # Composable before execution
```

### ❌ **Validation Applicative**
Accumulates errors rather than short-circuiting like Result. Perfect for form validation where you want all errors, not just the first failure.

```python
# ❌ NOT IMPLEMENTED - Proposed Validation applicative
from modgud import Validation, ValidationError

@guarded_expression
def create_user(name, email, age):
    # Collects ALL validation errors, doesn't short-circuit
    Validation.of(User) \
        .apply(validate_name(name)) \
        .apply(validate_email(email)) \
        .apply(validate_age(age)) \
        .fold(
            on_success=lambda user: f"Created: {user}",
            on_failure=lambda errors: f"Errors: {', '.join(errors)}"
        )

def validate_name(name):
    return Validation.success(name) if name else Validation.failure("Name required")
    
def validate_email(email):
    return Validation.success(email) if '@' in email else Validation.failure("Invalid email")
```

## 🔗 **Advanced Function Composition & Piping**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION STATUS: 🚧 PARTIALLY IMPLEMENTED                            │
│  PYTHON COMPATIBILITY: 3.6+ (all features)                                 │  
│  PRIORITY: MEDIUM - Enhances existing pipeable decorator                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ✅ **Pipe Operator (IMPLEMENTED)**
**Reverse composition operator** enables left-to-right data flow. modgud's `@pipeable` decorator already provides this functionality!

```python
# ✅ IMPLEMENTED - Current modgud @pipeable decorator
from modgud import pipeable

@pipeable
def add(x, y):
    return x + y

@pipeable  
def multiply(x, factor):
    return x * factor

@pipeable
def format_result(x):
    return f"Result: {x}"

# Chaining with pipe operator
result = 5 | add(3) | multiply(2) | format_result()  # "Result: 16"
```

### ✅ **Chainable Expressions (IMPLEMENTED!)**
**Fluent interfaces** with method chaining for functional-style data transformation.

```python
# ✅ IMPLEMENTED - Current modgud chainable expressions
from modgud import chain, chained_expression, ChainableExpression

# Manual chainable wrapping
result = chain(42) \
    .map(lambda x: x * 2) \
    .filter(lambda x: x > 50) \
    .tap(print) \
    .unwrap_or(0)  # 84

# Decorator for automatic chaining
@chained_expression
def process_data(data):
    return data.upper()

# Returns ChainableExpression that can be chained
result = process_data("hello") \
    .map(lambda s: s + " WORLD") \
    .unwrap()  # "HELLO WORLD"
```

### ❌ **Automatic Currying and Partial Application**
Make composition more elegant by transforming functions to support partial application automatically.

```python
# ❌ NOT IMPLEMENTED - Proposed @curry decorator
from modgud import curry, pipeable

@curry
@pipeable
def add_three(a, b, c):
    return a + b + c

# Multiple calling styles enabled by currying
add_partial = add_three(1)           # Returns function waiting for b, c
add_more = add_partial(2)            # Returns function waiting for c  
result = add_more(3)                 # Returns 6

# Elegant pipeline composition without lambdas
numbers = [1, 2, 3, 4, 5]
result = numbers | map(add_three(10, 5)) | list()  # [16, 17, 18, 19, 20]
```

### ❌ **Compose and Flow Utilities**
Complement piping with function composition utilities for reusable transformation pipelines.

```python
# ❌ NOT IMPLEMENTED - Proposed compose/flow functions
from modgud import compose, flow, pipeable

@pipeable
def validate(data): return validated_data
@pipeable  
def normalize(data): return normalized_data
@pipeable
def save_to_db(data): return saved_data

# Right-to-left composition (mathematical)
process_user_rtl = compose(save_to_db, normalize, validate)

# Left-to-right composition (intuitive) 
process_user_ltr = flow(validate, normalize, save_to_db)

# Both create reusable transformation pipelines
result = process_user_ltr(user_data)
```

### ❌ **Point-Free Style Helpers**
Eliminate explicit arguments and reduce lambda usage with combinator utilities.

```python
# ❌ NOT IMPLEMENTED - Proposed point-free helpers
from modgud import identity, constant, flip, tap, method

users = [user1, user2, user3]

# Method helper converts methods to functions
emails = users | map(method('get_email')) | list()

# Tap executes side effect, returns original (debugging/logging)
result = data | tap(print) | process() | tap(log_result)

# Flip reverses argument order
divide = lambda a, b: a / b
divide_by = flip(divide)  # Now: divide_by(2, 10) == 10 / 2 == 5.0

# Identity and constant for composition
safe_process = flow(
    validate_input,
    when(is_empty, constant([])),  # Return empty list for empty input
    when(is_valid, identity),      # Pass through valid input unchanged
    process_data
)
```

### ❌ **Function Threading Macros**
Inspired by Clojure's `->` and `->>`, thread values through function chains with flexible argument positioning.

```python
# ❌ NOT IMPLEMENTED - Proposed threading macros
from modgud import thread_first, thread_last

# Thread-first: x becomes first argument of each function
result = thread_first(
    "hello world",
    str.title,                    # "Hello World"
    lambda s: s.replace(" ", "_"), # "Hello_World"  
    str.lower                     # "hello_world"
)

# Thread-last: x becomes last argument of each function  
result = thread_last(
    [1, 2, 3, 4, 5],
    lambda lst, x: filter(lambda n: n > x, lst), 2,  # [3, 4, 5]
    lambda lst, x: map(lambda n: n * x, lst), 10,    # [30, 40, 50]
    list                                              # [30, 40, 50]
)

# Useful for functions with inconsistent argument orders
process_data = thread_first(
    raw_data,
    parse_json,           # parse_json(raw_data)  
    validate_schema,      # validate_schema(parsed_data)
    enrich_with_metadata, # enrich_with_metadata(validated_data)
    save_to_cache        # save_to_cache(enriched_data)
)
```

## 🔄 **Lazy Evaluation & Infinite Sequences**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION STATUS: ❌ NOT IMPLEMENTED YET                               │
│  PYTHON COMPATIBILITY: 3.6+ (all features) | 3.8+ (cached_property)        │
│  PRIORITY: MEDIUM - Performance optimization for data processing            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ❌ **Lazy Sequence Type**
Wraps iterators with functional operations that don't execute until materialized. Unlike built-in map/filter, provides chainable methods for elegant composition.

```python
# ❌ NOT IMPLEMENTED - Proposed LazySeq class
from modgud import LazySeq

# Never creates a million-element list in memory
@guarded_expression
def find_large_primes():
    LazySeq(range(1000000)) \
        .filter(is_prime) \
        .filter(lambda n: n > 10000) \
        .take(10) \
        .to_list()  # Only materializes the final 10 results

# Chainable operations with method syntax
@guarded_expression  
def process_data_stream(data):
    LazySeq(data) \
        .map(parse_record) \
        .filter(is_valid) \
        .group_by(lambda r: r.category) \
        .map_values(lambda group: sum(r.value for r in group)) \
        .to_dict()
```

### ❌ **Memoization and Caching Decorators**
Enable lazy computation with sharing. Transform expensive recursive functions from exponential to linear time.

```python
# ❌ NOT IMPLEMENTED - Proposed memoization decorators
from modgud import memoize, lazy_property

@memoize
@guarded_expression
def fibonacci(n):
    guard n <= 1: return n
    fibonacci(n-1) + fibonacci(n-2)  # Exponential → Linear with memoization

class DataProcessor:
    @lazy_property
    def expensive_computation(self):
        # Computed once, cached thereafter
        return perform_heavy_calculation(self.data)
    
    @memoize(max_size=128, ttl=300)  # LRU cache with TTL
    @guarded_expression
    def process_item(self, item_id):
        guard item_id: return fetch_and_process(item_id)
        None
```

### ❌ **Stream Processing Utilities**
Enable infinite data structures through lazy evaluation and functional stream operations.

```python
# ❌ NOT IMPLEMENTED - Proposed Stream class
from modgud import Stream

# Infinite sequences with lazy evaluation
naturals = Stream.iterate(0, lambda x: x + 1)
fibonacci_stream = Stream.iterate((0, 1), lambda pair: (pair[1], pair[0] + pair[1])).map(lambda pair: pair[0])


@guarded_expression
def take_fibonacci(n):
  guard
  n > 0:
  return fibonacci_stream.take(n).to_list()
  []


# Stream composition and transformation
@guarded_expression
def process_event_stream(events):
  Stream.from_tuple(events)
    .filter(lambda e: e.severity >= WARNING)
    .buffer(size=100, timeout=5.0)
    .map(aggregate_events)
    .subscribe(send_alert)
```

### ❌ **Transducers**
Separate transformation essence from application method. Compose transformations without intermediate collections.

```python
# ❌ NOT IMPLEMENTED - Proposed transducer system
from modgud import transduce, mapping, filtering, taking

# Traditional approach - creates intermediate collections
def traditional_pipeline(data):
    return list(map(str.upper, filter(str.isalpha, data[:100])))

# Transducer approach - single pass, no intermediates
@guarded_expression
def transducer_pipeline(data):
    xform = compose(
        taking(100),      # Take first 100
        filtering(str.isalpha),  # Keep only alphabetic
        mapping(str.upper)       # Convert to uppercase
    )
    transduce(xform, list, data)  # Single pass transformation

# Reusable transformations
text_processor = compose(
    filtering(lambda s: len(s) > 3),
    mapping(str.strip),
    mapping(str.title)
)

# Apply to different collection types
result_list = transduce(text_processor, list, text_data)
result_set = transduce(text_processor, set, text_data)
```

### ❌ **Pull vs Push Streams**
Different laziness models for event processing and reactive programming patterns.

```python
# ❌ NOT IMPLEMENTED - Proposed Observable/Stream types
from modgud import Observable, Stream


# Pull streams (consumer-controlled)
@guarded_expression
def pull_stream_example():
  stream = Stream.from_tuple(data_source)
  stream.take_while(is_valid)
    .batch(10)
    .map(process_batch)
    .consume()  # Consumer pulls when ready


# Push streams (producer-controlled) 
@guarded_expression
def push_stream_example():
  observable = Observable.from_events(event_source)
  observable.filter(is_important)
    .debounce(1.0)
    .map(transform_event)
    .subscribe(handle_event)  # Producer pushes when data available


# Bridge between pull and push
@guarded_expression
def bridge_streams():
  pull_stream = Stream.from_generator(data_generator)
  push_observable = pull_stream.to_observable(buffer_size=1000)
  push_observable.subscribe(process_data)
```

## ⚡ **Expression-Based Control Flow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION STATUS: ❌ NOT IMPLEMENTED YET                               │
│  PYTHON COMPATIBILITY: 3.6+ (all features) | 3.8+ (walrus operator)        │
│  PRIORITY: HIGH - Natural extension of guard clauses and implicit returns   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ❌ **Multi-Branch Conditional Expressions**
Extend Python's ternary operator with clean multi-branch support that integrates with modgud's guard system.

```python
# ❌ NOT IMPLEMENTED - Proposed cond() function
from modgud import cond

@guarded_expression
def classify_number(x):
    cond(
        x < 0, "negative",
        x == 0, "zero", 
        x > 0 and x < 10, "small positive",
        x >= 10, "large positive"
    )  # Returns first matching condition

# Integration with existing guards
@guarded_expression  
def process_user_status(user):
    guard user: return "No user"
    
    cond(
        user.is_active, "active",
        user.is_suspended, "suspended", 
        user.is_pending, "pending",
        default="unknown"
    )
```

### ❌ **Enhanced Switch/Case Expression**
Pattern-like dispatching that works with Python 3.6+ and complements 3.10+ pattern matching.

```python
# ❌ NOT IMPLEMENTED - Proposed switch expression
from modgud import switch

@guarded_expression
def handle_http_status(status_code):
    switch(status_code) \
        .case(200, lambda: "OK") \
        .case(404, lambda: "Not Found") \
        .case(lambda x: 400 <= x < 500, lambda: "Client Error") \
        .case(lambda x: x >= 500, lambda: "Server Error") \
        .default(lambda: "Unknown Status")

# Type-based dispatching
@guarded_expression
def serialize_value(value):
    switch(type(value)) \
        .case(str, lambda v: f'"{v}"') \
        .case(int, lambda v: str(v)) \
        .case(list, lambda v: f"[{', '.join(map(serialize_value, v))}]") \
        .default(lambda v: repr(v))
```

### ❌ **Functional Guard Expressions**
Transform modgud's guard clauses into chainable expressions for more complex validation flows.

```python
# ❌ NOT IMPLEMENTED - Proposed functional guard syntax
from modgud import guard_chain

@guarded_expression
def process_payment(payment_data):
    guard_chain(payment_data) \
        .check(lambda p: p.amount > 0, "Amount must be positive") \
        .check(lambda p: p.currency in VALID_CURRENCIES, "Invalid currency") \
        .check(lambda p: p.card.is_valid(), "Invalid card") \
        .then(lambda p: charge_payment(p)) \
        .catch(lambda error: log_payment_error(error))
```

### ❌ **Let Bindings and Expression Blocks**
Scope temporary variables within expressions without polluting the namespace.

```python
# ❌ NOT IMPLEMENTED - Proposed let binding syntax
from modgud import let

@guarded_expression
def complex_calculation(x, y):
    let(
        a=expensive_calc_1(x),
        b=expensive_calc_2(y), 
        c=expensive_calc_3(x, y)
    ).in_(lambda a, b, c: (a + b) * c if c > 0 else a - b)

# Context manager style
@guarded_expression
def process_data(raw_data):
    with let(
        parsed=parse_data(raw_data),
        validated=validate_data(parsed),
        enriched=enrich_data(validated)
    ) as (parsed, validated, enriched):
        f"Processed {len(enriched)} items from {len(parsed)} raw items"
```

### ❌ **Try Expressions**
Wrap exception-prone code in expressions returning Result types for functional error handling.

```python
# ❌ NOT IMPLEMENTED - Proposed try expressions
from modgud import try_expr, Ok, Err

@guarded_expression
def safe_parse_int(value):
    try_expr(lambda: int(value)) \
        .map(lambda x: x * 2) \
        .fold(
            on_ok=lambda result: f"Success: {result}",
            on_error=lambda error: f"Parse error: {error}"
        )

# Chaining multiple try operations
@guarded_expression
def safe_divide_and_format(a_str, b_str):
    try_expr(lambda: int(a_str)) \
        .bind(lambda a: try_expr(lambda: int(b_str)).map(lambda b: (a, b))) \
        .bind(lambda pair: try_expr(lambda: pair[0] / pair[1]) if pair[1] != 0 else Err("Division by zero")) \
        .map(lambda result: f"Result: {result:.2f}") \
        .unwrap_or("Calculation failed")
```

## Immutability and Persistent Data Structures

**Frozen dataclasses and immutable builders** create clean immutable types. Python 3.7+ dataclasses with `frozen=True` provide value types, but builder patterns help with updates: `user.with_name("New Name")` returns a new instance. A `@immutable` decorator could enforce deep immutability and provide lens-based updates. Works in Python 3.7+ (3.6 with third-party dataclasses backport).

**Persistent data structures** (immutable collections with structural sharing) enable efficient immutable operations. While Python's built-in tuple and frozenset are immutable, they don't share structure on updates. A persistent vector allows O(log n) updates by sharing tree structure. Libraries like pyrsistent exist, but lightweight implementations focused on common use cases (list, dict, set) could integrate better. Works in Python 3.6+ but benefits from Python 3.10+ pattern matching.

**Lens and optics** provide functional getters/setters for nested immutable data. A lens focuses on a part of a structure, enabling updates without mutation: `user_lens.age.set(user, 30)` returns a new user with age changed. Prisms handle optional fields, traversals handle collections. While sophisticated, basic lens implementations work in Python 3.6+, with Python 3.10+ pattern matching enabling cleaner DSL syntax.

**Record types and named tuples** extended beyond stdlib namedtuple provide immutable records with type hints, defaults, and helper methods. Python 3.7+ dataclasses cover this well, but enhanced versions could add functional methods like `map_fields()`, `filter_fields()`, and `fold()` for operating on all fields. Works in Python 3.7+ (3.6 with backport).

## Protocol-Based Polymorphism and Type Classes

**Functors, applicatives, and monads as protocols** enable structural typing. Define abstract protocols (Python 3.8+) or ABCs (3.6+) for these patterns: `Functor` requires `map()`, `Monad` requires `bind()` and `unit()`. This allows generic functions operating on any monad: `def sequence[M: Monad](monads: list[M]) -> M[list]`. Works in Python 3.8+ with protocols, 3.6+ with ABCs.

**Higher-kinded types emulation** lets you abstract over type constructors. Python lacks true HKTs, but you can approximate them using protocols and clever typing. A `Container` protocol with `TypeVar` manipulation enables writing generic functions over Maybe, List, Result, etc. This requires type: ignore in places but works practically in Python 3.8+. Python 3.12+ improved generics make this cleaner.

**Type classes via decorators** register implementations for types. Similar to Haskell's type classes or Rust's traits, a `@typeclass` decorator registers functions for types: `@show.register(int)` defines how to show integers. Uses functools.singledispatch under the hood (Python 3.4+) but wraps it in friendlier FP syntax. Works in Python 3.6+.

## Integration with Python 3.10+ Features

**Pattern matching helpers** enhance native match expressions. Decorator-based pattern extractors enable custom patterns: `case Regex("\\d+") as digits:` could extract regex matches. Active patterns (functions returning bool and extracted values) enable sophisticated matching. These require Python 3.10+ and careful integration with the match protocol.

**Generic type utilities for 3.12+** leverage PEP 695's cleaner syntax. Helper types for functional patterns become more readable: `type Predicate[T] = Callable[[T], bool]`, `type Lens[S, A] = tuple[Callable[[S], A], Callable[[S, A], S]]`. Generic monadic types benefit enormously from the simplified syntax. Requires Python 3.12+.

## Async Functional Patterns

**Async monads** wrap async operations in composable structures. An `AsyncResult` or `AsyncMaybe` enables functional composition of awaitable values: `await user.map_async(fetch_profile).map_async(enrich_data)`. This requires Python 3.5+ for async/await, but really shines in 3.7+ with better async support.

**Effect systems** track side effects in types. While Python lacks true effect systems, a lightweight implementation could distinguish pure, IO, and async operations at the type level using protocols and decorators. `@pure` marks functions without side effects, `@io_effect` marks I/O operations, enabling static analysis. Works in Python 3.8+ with protocols.

## Python Version Compatibility Matrix

**Note**: modgud currently requires Python 3.13+ due to its use of modern AST features for implicit return transformation. However, many of the proposed additional features could be implemented with broader compatibility if needed:

**Python 3.13+ (modgud's current requirement)**: All features benefit from the latest Python improvements including free-threading for pure functions, JIT compilation for functional patterns, and improved error messages

**Python 3.10-3.12 (with minor modgud adjustments)**: Native pattern matching, union types, PEP 695 generic syntax would integrate beautifully with modgud's guard system

**Python 3.6-3.9 (if backward compatibility desired)**: Function composition, piping via operator overload, lazy sequences, memoization, monadic types (Option/Result), currying, immutable patterns, lens basics, protocol-based polymorphism (ABCs) could all be added as separate modules

## Implementation Priorities

Start with **core monadic types** (Maybe, Result) in Python 3.6+ compatible form—these provide immediate value with minimal dependencies. Add **pipe operator and composition utilities** next, as these dramatically improve code readability. **Pattern matching polyfills** for 3.6-3.9 extend reach, while **native 3.10+ pattern integration** serves modern users.

**Lazy sequences** and **currying** unlock functional patterns without breaking changes. **Immutable helpers** (frozen builders, simple lenses) enable functional data manipulation. **Protocol-based polymorphism** creates extensible abstractions without forcing inheritance.

Advanced features like **transducers**, **effect tracking**, and **higher-kinded type emulation** serve power users but require careful API design to avoid complexity explosion. **Async functional patterns** matter for real-world applications but should build on solid sync foundations first.

The key insight: start with practical, familiar patterns (piping, monads, immutability) that solve real problems, then gradually introduce more sophisticated concepts. Python programmers will adopt expression-oriented patterns when they make code cleaner and more maintainable, not because of abstract purity.

---

## Why modgud Remains Essential

Despite Python's evolution toward more functional features (pattern matching in 3.10+, better type hints, etc.), modgud fills a critical gap: **making Python functions behave like expressions without changing Python's syntax**. This is uniquely valuable because:

### 1. **Zero-Syntax-Cost Expression Orientation**
While Python 3.10+ adds pattern matching, it's still statement-based. modgud's `@guarded_expression` transforms regular functions into expression-oriented code *today*, working seamlessly with Python 3.13+ codebases. You get Haskell-like guards and implicit returns without waiting for PEP acceptance or version upgrades.

### 2. **Gradual Adoption Path**
Unlike heavy functional libraries (PyMonad, toolz, etc.) that require wholesale architectural changes, modgud decorators can be applied selectively. Start with one critical function, see the benefits, expand gradually. This pragmatic approach reduces resistance in teams unfamiliar with FP.

### 3. **Pythonic Integration**
Rather than forcing Haskell or Scala idioms into Python, modgud enhances Python's existing decorator pattern. This feels natural to Python developers while delivering expression-oriented benefits. No new operators, no category theory, just cleaner functions.

### 4. **Performance Without Overhead**
Many FP libraries introduce abstraction penalties through wrapper objects and indirection. modgud's AST transformation approach operates at the function level with minimal runtime overhead, making it suitable for performance-sensitive code where other FP solutions might be rejected.

### 5. **Clean Architecture Focus**
modgud already demonstrates clean architecture principles with dependency injection and separation of concerns (AST transformation, guard runtime, decorator modules). This makes it an excellent foundation for additional functional features.

## Additional Features to Complement modgud's Existing Capabilities

Given that modgud already provides `@guarded_expression` with guard clauses and implicit returns via AST transformation, here are features that would naturally extend its expression-oriented philosophy:

### 1. **Conditional Chaining with `@chained_expression`**
```python
@chained_expression
def process_user(user):
    return (
        validate_user(user)
        .when(is_active, activate_features)
        .when(needs_notification, send_email)
        .unless(is_blocked, apply_restrictions)
        .finally(save_to_db)
    )
```
**Implementation**: Return a chainable wrapper from decorated functions that accumulates transformations lazily, executing them in sequence with conditional application.

### 2. **Pattern Extraction with `@destructured`**
```python
@destructured
def calculate_area(shape):
    with match:
        Point(x, y): 0
        Circle(_, radius): pi * radius ** 2
        Rectangle(_, width, height): width * height
        {type: "triangle", base: b, height: h}: 0.5 * b * h
```
**Implementation**: For Python 3.6-3.9, use AST transformation to convert the specialized syntax into if/elif chains with isinstance checks and attribute extraction. For 3.10+, enhance native match statements with automatic returns.

### 3. **Memoized Guards with `@cached_guards`**
```python
@cached_guards
def expensive_classify(data):
    guard is_cached(data): return cached_result(data)
    guard is_simple(data): return quick_process(data)
    guard is_complex(data): return heavy_computation(data)
```
**Implementation**: Wrap guard conditions in an LRU cache, particularly useful when guards involve expensive computations. Track which guards have been evaluated for given inputs.

### 4. **Async Expression Support with `@async_expression`**
```python
@async_expression
async def fetch_user_data(user_id):
    guard not user_id: return None
    guard cached := await get_cache(user_id): return cached
    
    user = await fetch_user(user_id)
    profile = await fetch_profile(user_id)
    return merge(user, profile)
```
**Implementation**: Extend the guard syntax to handle async conditions and ensure implicit returns work with coroutines. Handle await expressions within guard conditions.

### 5. **Pipeline Integration with `@pipeable`**
```python
@pipeable
def add(x, y):
    return x + y

@pipeable  
def multiply(x, y):
    return x * y

result = 5 | add(3) | multiply(2)  # Returns 16
```
**Implementation**: Create a `Pipeable` wrapper class with `__or__` overloading. Use partial application to enable clean syntax. The decorator handles converting regular functions into pipeable ones.

### 6. **Effect Tracking with `@pure` and `@effect`**
```python
@pure
@guarded_expression
def calculate(x, y):
    guard x < 0: return 0
    return x * y

@effect("io")
def save_result(value):
    with open("output.txt", "w") as f:
        f.write(str(value))
```
**Implementation**: Decorators that mark and track side effects. In development mode, `@pure` functions could be automatically tested for referential transparency. Effect decorators could integrate with type checkers via type hints.

### 7. **Implicit Error Handling with `@safe_expression`**
```python
@safe_expression(default=0)
def risky_calculation(x, y):
    return x / y  # Division by zero returns default

@safe_expression(returns=Result)
def parse_data(text):
    return json.loads(text)  # Returns Result.Ok or Result.Err
```
**Implementation**: Wrap function bodies in try/except, converting exceptions to monadic types (Result/Option) or default values. Integrate with modgud's implicit return to ensure clean error propagation.

### 8. **Lazy Evaluation with `@lazy_expression`**
```python
@lazy_expression
def expensive_compute(data):
    guard is_trivial(data): return 0
    return heavy_calculation(data)

result = expensive_compute(big_data)  # Not computed yet
value = result.force()  # Now it computes
```
**Implementation**: Return a thunk (zero-argument lambda) that captures the computation. Provide a `.force()` method or make it callable. Can combine with memoization for call-by-need semantics.

### 9. **Multi-Clause Functions with `@clauses`**
```python
@clauses
def factorial(n):
    clause(0): 1
    clause(1): 1
    clause(n): n * factorial(n - 1)
```
**Implementation**: Similar to Erlang/Elixir function clauses. Parse multiple clause definitions and dispatch based on pattern matching or equality. More readable than guards for certain recursive patterns.

### 10. **Contract Programming with `@contracted`**
```python
@contracted(
    requires=lambda x: x > 0,
    ensures=lambda result: result >= 0,
    invariant=lambda self: self.balance >= 0
)
@guarded_expression
def square_root(x):
    guard x == 0: return 0
    guard x == 1: return 1
    return x ** 0.5
```
**Implementation**: Decorators that check preconditions, postconditions, and invariants. In production, these could be disabled for performance. Development/testing modes would enforce contracts strictly.

### 11. **AST-Based Pattern Matching for Pre-3.10 Python**
Since modgud already uses AST transformation, it could provide pattern matching syntax for older Python versions:
```python
@pattern_matched
def describe(value):
    match value:
        case 0: "zero"
        case int(n) if n > 0: f"positive: {n}"
        case int(n): f"negative: {n}"
        case str(s): f"string: {s}"
        case _: "unknown"
```
**Implementation**: Transform match/case into if/elif chains during AST processing, similar to how implicit returns work.

### 12. **Where Clauses (Post-Conditions)**
Complement guards (pre-conditions) with where clauses for post-conditions:
```python
@guarded_expression
def calculate_discount(price, customer_type):
    guard price > 0
    
    discount = price * get_rate(customer_type)
    
    where discount <= price  # Ensures we never give money back
    where discount >= 0      # Ensures discount is never negative
    
    discount
```
**Implementation**: Use AST transformation to inject assertions after the main logic but before the return.

### 13. **Let Bindings via AST**
Since modgud transforms AST, it could provide true let-binding syntax:
```python
@expression_with_let
def complex_calc(x, y):
    let a = expensive_compute(x)
    let b = another_compute(y)
    let c = a + b
    in c * c if c > 0 else 0
```
**Implementation**: Transform let/in syntax into proper Python with local variables during AST processing.

### Implementation Strategy

1. **Start with `@pipeable`** - It's immediately useful and combines well with existing `@guarded_expression`
2. **Add `@safe_expression`** - Error handling is a common pain point that expression-orientation solves elegantly
3. **Implement `@chained_expression`** - Natural extension of guard concepts into a fluent interface
4. **Build async support** - Critical for real-world Python applications
5. **Layer in advanced features** - Pattern extraction, clauses, contracts based on user demand

Each feature should:
- Work independently or composed with others
- Maintain backward compatibility
- Provide clear error messages
- Include type hints for IDE support
- Offer escape hatches for when magic isn't wanted

The key is maintaining modgud's philosophy: practical expression-orientation without forcing users to learn category theory or rewrite their entire codebase.

## Unique Opportunities with AST Transformation

Since modgud already uses AST transformation for implicit returns, it has unique opportunities that decorator-only libraries can't match:

### **Syntax Extensions Without Language Changes**
modgud could introduce new expression forms that compile to standard Python:
- **Guard syntax**: Already implemented with special guard statements
- **Pattern matching**: Backport 3.10+ match/case to older Pythons
- **Do notation**: Transform generator-like syntax into monadic chains
- **Pipeline operator**: Parse `|>` in comments and transform to method calls

### **Compile-Time Optimizations**
AST transformation enables optimizations impossible at runtime:
- **Tail call optimization**: Transform recursive functions into loops
- **Constant folding**: Pre-compute expressions with literal values
- **Dead code elimination**: Remove unreachable branches after guards
- **Inline expansion**: Replace simple function calls with their bodies

### **Advanced Type Checking**
With AST access, modgud could provide:
- **Effect tracking**: Mark functions as pure/impure at compile time
- **Exhaustiveness checking**: Ensure all pattern cases are covered
- **Guard completeness**: Verify guards cover all input domains
- **Return type inference**: Deduce types from implicit returns

### **Development Tools**
AST transformation enables powerful development features:
- **Automatic documentation**: Extract guards as function contracts
- **Test generation**: Create test cases from guard conditions
- **Debugging aids**: Inject logging at expression boundaries
- **Coverage analysis**: Track which guards/branches execute

The combination of guard clauses, implicit returns, and AST transformation makes modgud uniquely positioned to bring expression-oriented programming to Python without waiting for language changes. It's not just a library—it's a bridge to Python's functional future.

---

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      📊 COMPREHENSIVE FEATURE SUMMARY                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 **Implementation Status Overview**

| **Feature Category** | **Status** | **Priority** | **Python Compat** | **Description** |
|---------------------|------------|--------------|-------------------|-----------------|
| **Core Guard System** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | `@guarded_expression`, `CommonGuards`, error handling |
| **Implicit Returns** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | AST transformation for expression-oriented functions |
| **Pipeline Composition** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | `@pipeable` decorator with `\|` operator |
| **Chainable Expressions** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | `@chained_expression`, `chain()`, fluent interfaces |
| **Monadic Operations** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | `Maybe`/`Result` types, `Some`/`Nothing`, `Ok`/`Err` |
| **Safe Error Handling** | ✅ **IMPLEMENTED** | HIGH | 3.13+ | `@safe_expression` decorator with Result wrapping |
| **Dependency Injection** | ✅ **IMPLEMENTED** | MEDIUM | 3.13+ | `@Inject` decorator for automatic resolution |
| **Pattern Matching** | ❌ **NOT IMPLEMENTED** | HIGH | 3.6+ / 3.10+ | Enhanced destructuring and pattern matching |
| **Function Composition** | 🚧 **PARTIAL** | MEDIUM | 3.6+ | Currying, compose/flow utilities, point-free style |
| **Lazy Evaluation** | ❌ **NOT IMPLEMENTED** | MEDIUM | 3.6+ | LazySeq, memoization, stream processing |
| **Control Flow** | ❌ **NOT IMPLEMENTED** | HIGH | 3.6+ | Multi-branch conditionals, try expressions |
| **Immutable Data** | ❌ **NOT IMPLEMENTED** | MEDIUM | 3.7+ | Persistent data structures, lens operations |
| **Type Classes** | ❌ **NOT IMPLEMENTED** | LOW | 3.8+ | Protocol-based polymorphism |
| **Async Patterns** | ❌ **NOT IMPLEMENTED** | MEDIUM | 3.7+ | Async monads, effect systems |

---

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🚀 RECOMMENDED IMPLEMENTATION ROADMAP                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **✅ Phase 1: Core Foundation** (COMPLETED!)
1. ✅ **Guard System** - `@guarded_expression` with pre-built validators
2. ✅ **Implicit Returns** - Ruby-style expression-oriented functions  
3. ✅ **Pipeline Composition** - `@pipeable` with `|` operator
4. ✅ **Monadic Types** - `Maybe`/`Result` with full monadic operations
5. ✅ **Safe Error Handling** - `@safe_expression` with Result wrapping
6. ✅ **Chainable Expressions** - Fluent interfaces with method chaining

### **Phase 2: Enhanced Control Flow** (Next Priority)
1. **Multi-Branch Conditionals** (`cond`, `switch`) - Natural extension of guards  
2. **Try Expressions** - Functional exception handling without `@safe_expression`
3. **Pattern Matching Helpers** - Backport 3.10+ features to older Python
4. **Let Bindings** - Scoped temporary variables in expressions

### **Phase 3: Advanced Composition** (Medium Priority)  
5. **Currying & Partial Application** - Complete the piping story
6. **Compose/Flow Utilities** - Reusable transformation pipelines
7. **Point-Free Style Helpers** - Eliminate lambda expressions

### **Phase 4: Performance & Advanced Features** (Low Priority)
8. **Lazy Evaluation** - Performance optimizations for data processing
9. **Immutable Data Structures** - Functional data manipulation
10. **Async Patterns** - Real-world application support

---

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        💡 WHY MODGUD REMAINS ESSENTIAL                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

Despite Python's evolution toward more functional features, **modgud fills a critical gap**:

### **🎯 Zero-Syntax-Cost Expression Orientation**
While Python 3.10+ adds pattern matching, it's still statement-based. modgud's `@guarded_expression` transforms regular functions into expression-oriented code *today*, working seamlessly with Python 3.13+ codebases.

### **📈 Gradual Adoption Path**  
Unlike heavy functional libraries that require architectural changes, modgud decorators can be applied selectively. Start with one function, see benefits, expand gradually.

### **🐍 Pythonic Integration**
Rather than forcing Haskell idioms, modgud enhances Python's decorator pattern. Natural to Python developers while delivering expression-oriented benefits.

### **⚡ Performance Without Overhead**
AST transformation operates at function level with minimal runtime overhead, suitable for performance-sensitive code where other FP solutions might be rejected.

### **🏗️ Clean Architecture Foundation**
Already demonstrates clean architecture with dependency injection and separation of concerns, making it an excellent foundation for additional functional features.

---

**modgud isn't just a library—it's Python's bridge to expression-oriented programming.**
