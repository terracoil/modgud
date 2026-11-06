**Parent**: [📚 Documentation Hub](ADVANCED.md) | [🌉 Main README](../README.md) | [⚙️ How It Works](how-it-works.md)

# API reference

Everything a caller needs comes from `modgud`. Entries stay terse; the why is in [How It Works](how-it-works.md), and every snippet has a runnable original in [`examples/`](../examples/).

## 📜 What to import

```python
from modgud import guarded_expression, implicit_return
from modgud import CommonGuards, GuardFunction, GuardRegistry
from modgud import GuardClauseError, GuardFailureEnum
from modgud import ExplicitReturnDisallowedError, ImplicitReturnError, MissingImplicitReturnError, UnsupportedConstructError
from modgud import GuardPort, ImplicitReturnPort  # integration seam only
```

Those 13 names are the public API. Everything else sits in a lower tier:

| Tier | What | Where | Promise |
|---|---|---|---|
| Public | the 13 names above | `modgud` | Documented on this page |
| Integration seam | the two ports, `guard_port=` / `imp_return_port=`, `IDUNN_ENV`, `Idunn().reset()` | `modgud` (ports also at `modgud.domain` and `modgud.domain.ports`) | For fakes and Idunn users; see [Integration seam](#integration-seam) |
| Internal | `GuardAdapter`, `ImplicitReturnAdapter`, `modgud.infrastructure.ast` | leaf packages | May move between releases |

`modgud.domain` (nine names) and `modgud.app` (four) are secondary paths to the same objects, there for the package's layering. `modgud.infrastructure` exports nothing. These docs teach one import path.

## 🛡️ Decorators

### guarded_expression

```python
guarded_expression(
  *guards: GuardFunction,
  implicit_return: bool = True,
  strategy: GuardFailureEnum = GuardFailureEnum.ERROR_RAISE,
  on_failure: Any = GuardClauseError,
  continuance: int = 0,
  guard_port: GuardPort,                 # injected by Idunn
  imp_return_port: ImplicitReturnPort,   # injected by Idunn
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*guards` | `GuardFunction` | none | Checks run in order before every call |
| `implicit_return` | `bool` | `True` | Rewrite the body so each branch's last expression is returned |
| `strategy` | `GuardFailureEnum` | `ERROR_RAISE` | What a failure turns into; see [GuardFailureEnum](#guardfailureenum) |
| `on_failure` | `Any` | `GuardClauseError` | The payload paired with `strategy` |
| `continuance` | `int` | `0` | How many more failures to collect after the first |
| `guard_port` | `GuardPort` | injected | Pass one only to substitute a fake |
| `imp_return_port` | `ImplicitReturnPort` | injected | Pass one only to substitute a fake |

Always applied with parentheses, even with no guards.

- The body never runs when a guard has failed.
- With `implicit_return=True` the function is rewritten once, at decoration time, under the [implicit_return](#implicit_return) rules. Unreadable source raises `ValueError`.
- With `implicit_return=False` nothing is rewritten or checked. One trailing `return` is your convention, and a bare tail expression returns `None`.
- `__name__`, `__qualname__`, `__doc__`, `__annotations__` and `inspect.signature` survive.
- On `async def` the result is still a coroutine function. Guards run when the coroutine runs, so a refusal, raised or returned, arrives at the `await`.

```python
from modgud import CommonGuards, GuardClauseError, guarded_expression

@guarded_expression(CommonGuards.positive('price'))
def discount(price: float) -> float:
  if price >= 50:
    price * 0.2
  else:
    price * 0.1

discount(75)   # 15.0
discount(-10)  # raises GuardClauseError('price must be positive')
```

Full version: [examples/free_range/01_quick_start.py](../examples/free_range/01_quick_start.py)

#### Collecting multiple failures

`continuance=N` collects up to `1 + N` failures. With several, the error strategies build `ExceptionGroup('Guards failed', [...])`, one `on_failure` instance per message; catch it with `except*`. A guard that raises propagates if nothing has failed yet, and otherwise ends collection quietly: tripping over input already known to be bad is fallout, not news. `CHECKS` below holds four guards.

```python
@guarded_expression(*CHECKS, continuance=3)  # up to 1 + 3 failures
def every_problem(qty: int, sku: str) -> str:
  f'{qty} x {sku}'

try:
  every_problem(-1, '')
except* GuardClauseError as group:
  collected = [str(error) for error in group.exceptions]  # four messages
```

Full version: [examples/free_range/06_continuance.py](../examples/free_range/06_continuance.py)

### GuardFailureEnum

Four `IntEnum` members, each giving `on_failure` a different job:

| `strategy` | `on_failure` is | One failure | Several failures |
|---|---|---|---|
| `ERROR_RAISE` (default) | an exception class | raises `on_failure(msg)` | raises the `ExceptionGroup` |
| `ERROR_RETURN` | an exception class | returns `on_failure(msg)` | returns the `ExceptionGroup` |
| `RETURN_VALUE` | any value | returns `on_failure` as-is | same |
| `CALL_HANDLER` | a callable | returns `on_failure(errors, *args, **kwargs)` | same; `errors` is always a `list[str]` |

- For the two error strategies, an `on_failure` that isn't a class falls back to `GuardClauseError`.
- A handler gets the call's full arguments, `self` or `cls` included.
- On `async def`, every strategy's result comes back from the `await`. Handlers are called, not awaited, so write them as plain functions.

```python
def explain(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
  return {'status': 400, 'errors': errors, 'args': args}

@guarded_expression(AMOUNT, strategy=GuardFailureEnum.CALL_HANDLER, on_failure=explain)
def charge_or_explain(amount: float) -> str | dict[str, Any]:
  f'charged {amount:.2f}'

charge_or_explain(-1)  # {'status': 400, 'errors': ['amount must be positive'], 'args': (-1,)}
```

Full version: [examples/free_range/03_failure_strategies.py](../examples/free_range/03_failure_strategies.py)

### implicit_return

```python
implicit_return(
  *,
  imp_return_port: ImplicitReturnPort,  # injected by Idunn
)
```

Applied as `@implicit_return()`, parentheses required. At decoration time it rewrites the function so the last statement of each block is the return value. What counts as a tail:

| Last statement of a block | Yields |
|---|---|
| An expression | its value |
| `if` / `elif` / `else` | each branch's tail; an `if` with no `else` raises `MissingImplicitReturnError` |
| `try` / `except` / `else` / `finally` | the body's tail, or the handler's; `else` replaces the body's value on success; `finally` never sets it |
| `match` / `case` | each case's tail; the last case must be `case _:` or a bare capture with no guard, else `MissingImplicitReturnError` |
| `pass`, or an empty block | `None` |
| `raise` | raises |
| anything else (assignment, `for`, `while`, `with`, `def`, ...) | `UnsupportedConstructError` |

- An explicit `return` anywhere in the body, nested `def`s included, raises `ExplicitReturnDisallowedError`. Keep helpers that need `return` outside the decorated function; a nested `def` without `return` yields `None`.
- Zero-argument `super()` raises `UnsupportedConstructError`; write `super(Cls, self)`.
- A leading docstring stays a docstring.

```python
from modgud import implicit_return

@implicit_return()
def grade(score: int) -> str:
  if score >= 90:
    'A'
  elif score >= 75:
    'B'
  else:
    'C'
```

Full version: [examples/free_range/04_implicit_returns.py](../examples/free_range/04_implicit_returns.py)

#### Decorator order

Stacked with guards, the standalone decorator goes underneath, with the rewrite switched off above it:

```python
@guarded_expression(CommonGuards.positive('x'), implicit_return=False)  # right: guards outside
@implicit_return()
def right(x: int) -> int:
  x * 2

@implicit_return()  # wrong: raises TypeError at decoration (the rewrite would drop the guard)
@guarded_expression(CommonGuards.positive('x'), implicit_return=False)
def wrong(x: int) -> int:
  x * 2
```

The reverse order raises `TypeError` at decoration time: the outer rewrite would re-read the original source and the guards would vanish. Other decorators go above modgud too; below it, the re-compile drops them. `@staticmethod` and `@classmethod` may go either side ([Methods](#methods)).

Full version: [examples/free_range/10_decorator_composition.py](../examples/free_range/10_decorator_composition.py)

### Methods

Instance, static, class and `async` methods all work, under either decorator or the stacked form. modgud may sit outside or inside `@staticmethod` / `@classmethod`.

- Guards see the arguments without the receiver (a first parameter named `self` or `cls`), so `positive('x')` checks `x`. `CALL_HANDLER` handlers get everything, receiver included.
- `self.__secret` name-mangling works, the body may name its own class, and `__qualname__` stays `Cls.method`.
- Defaults and annotations are reused from the original function, so a default that names a class attribute or a module global is fine.
- `UnsupportedConstructError` at decoration time: zero-argument `super()` and a bare `__class__`. The re-compiled body has no `__class__` cell; write `super(Cls, self)`.
- Not covered: `@property`, `functools.cached_property`, other descriptors.

```python
class Thermostat:
  @guarded_expression(CommonGuards.positive('by'))  # the guard sees ``by``, never ``self``
  def warmer(self, by: int) -> int:
    self.target + by

  @guarded_expression(CommonGuards.in_range(-58, 212, 'fahrenheit'))  # modgud outermost
  @staticmethod
  def to_celsius(fahrenheit: float) -> float:
    (fahrenheit - 32) * 5 / 9
```

Full version: [examples/classy/10_decorator_composition.py](../examples/classy/10_decorator_composition.py)

### Testing guarded code

- An implicit-return function needs its source in a file on disk, at module level or in a class. The REPL and `exec` have no source; decoration raises `ValueError`.
- Defined inside a test, it may not touch the test's locals: the re-compile drops the closure. Keep such fixtures in a module, like `tests/method_fixtures.py`.
- The rewritten body uses the module's live globals, so `mock.patch` reaches it.
- Guards-only functions have none of these limits.
- Guards are plain functions: `CommonGuards.positive('x')(5)` returns `True`.

## 🧰 Guard toolkit

### GuardFunction

`GuardFunction = Callable[..., bool | str]`. A guard receives the call's `*args, **kwargs` (minus the receiver on methods) and returns exactly `True` to pass, or a message to fail. Anything else, `False` included, fails as `'Guard clause failed'`; hence `return ok or 'message'`. Guards see what the caller passed, so a parameter left at its default isn't there.

### CommonGuards

Nine static factories, each returning a `GuardFunction`. A guard looks for `param_name` in the keyword arguments, then at `args[position]`. For any parameter after the first, pass `position`, or a positional call checks argument 0. A value that isn't found fails, except under `matches_pattern`, which checks `''`.

| Factory | Fails when | Message |
|---|---|---|
| `not_none(param_name='parameter', position=0)` | value is `None` | `{param_name} cannot be None` |
| `not_empty(param_name='parameter', position=None)` | `len()` is 0, or the value is falsy | `{param_name} cannot be empty` |
| `positive(param_name='parameter', position=0)` | not `> 0` | `{param_name} must be positive` |
| `in_range(min_val, max_val, param_name='parameter', position=0)` | outside `[min_val, max_val]` | `{param_name} must be between {min_val} and {max_val}` |
| `type_check(expected_type, param_name='parameter', position=0)` | not an instance | `{param_name} must be of type {name}` |
| `matches_pattern(pattern, param_name='parameter', position=0)` | `re.match` on `str(value)` fails | `{param_name} must match pattern {pattern}` |
| `valid_file_path(param_name='path', position=0, must_exist=True, must_be_file=False, must_be_dir=False)` | `None`, missing, not a file, not a directory | `{param_name} is required` / `does not exist: {value}` / `must be a file: {value}` / `must be a directory: {value}` |
| `valid_url(param_name='url', position=0, require_scheme=True, schemes=('http', 'https'))` | `None`, scheme not in `schemes`, neither host nor path | `{param_name} is required` / `must use one of http/https: {value}` / `is not a valid URL: {value}` |
| `valid_enum(enum_class, param_name='parameter', position=0)` | `None`, a string that isn't a member's value, any other non-member | `{param_name} is required` / `must be one of [values]: got {value}` / `must be a valid {Enum} name` |

`matches_pattern` anchors at the start only; add `$` for a full match. `valid_url` accepts `http` and `https` unless you pass `schemes=('ftp',)` or set `require_scheme=False`.

```python
@guarded_expression(
  CommonGuards.positive('qty'),
  CommonGuards.in_range(1, 10, 'qty'),
  CommonGuards.valid_enum(Color, 'color', position=1),
)
def order(qty: int, color: str) -> str:
  f'{qty} x {Color(color).name}'
```

Full version: [examples/free_range/02_common_guards.py](../examples/free_range/02_common_guards.py)

### GuardRegistry

A process-wide registry of guard factories, used through class methods. `namespace=None` is the global namespace, separate from the named ones, and `CommonGuards` fills `'common'` at import. No lock. Register at import time.

| Method | Returns | Notes |
|---|---|---|
| `register(name, guard_factory, namespace=None)` | `None` | `ValueError` if the name is taken in that namespace |
| `get(name, namespace=None)` | factory or `None` | |
| `has_guard(name, namespace=None)` | `bool` | |
| `list_guards(namespace=None)` | `list[str]` | |
| `list_namespaces()` | `list[str]` | includes `'common'` |
| `unregister(name, namespace=None)` | `bool` | removes a namespace once it's empty |
| `instance()` | `GuardRegistry` | the singleton the class methods delegate to |

```python
GuardRegistry.register('max_weight', max_weight, namespace='shipping')
registered = GuardRegistry.get('max_weight', namespace='shipping')

@guarded_expression(registered(30), fragile_ok)
def ship(kg: float, mode: str, fragile: bool = False) -> str:
  f'{kg} kg by {mode}{" (fragile)" if fragile else ""}'
```

Full version: [examples/free_range/07_custom_guards.py](../examples/free_range/07_custom_guards.py)

## Error classes

| Exception | Base | Raised when |
|---|---|---|
| `GuardClauseError` | `Exception` | a guard fails under the default `on_failure` |
| `ImplicitReturnError` | `SyntaxError` | never directly; the base of the three below |
| `ExplicitReturnDisallowedError` | `ImplicitReturnError` | the rewritten body contains `return` |
| `MissingImplicitReturnError` | `ImplicitReturnError` | a tail `if` has no `else`, or a tail `match` has no wildcard case |
| `UnsupportedConstructError` | `ImplicitReturnError` | an unsupported tail, zero-argument `super()`, a bare `__class__` |

The `ImplicitReturnError` family is raised at decoration time, with `lineno` counted from the function's first decorator line. Missing source raises `ValueError` instead.

## Integration seam

The decorators depend on two ports, not on the code behind them. Both are `typing.Protocol` classes marked `@Port` for [Idunn](https://pypi.org/project/idunn):

```python
from modgud import GuardPort, ImplicitReturnPort
from modgud.domain.ports import GuardPort, ImplicitReturnPort  # same objects
```

The ports declare ordinary instance methods, so a fake is a plain object that may keep state on `self`. `ImplicitReturnPort` has `transform_function(self, func)`, the bare rewrite of a plain function, and `transform(self, func)`, what `@implicit_return()` calls: it also unwraps a `staticmethod` / `classmethod`, marks the result and refuses a `guarded_expression` wrapper. `GuardPort` has one method, `transform(self, func, continuance, imp_return_port, implicit_return, guards, strategy, on_failure)`: it rewrites through `imp_return_port.transform_function` when asked, then wraps with the guards. Pass a fake as `guard_port=` or `imp_return_port=` and it beats the injected adapter, for that decorator only. Swapping the adapters process-wide isn't supported.

```python
class RecordingTransformer:
  def __init__(self) -> None:
    self.seen: list[str] = []

  def transform(self, func: F) -> F:
    self.seen.append(func.__name__)
    return func

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    self.seen.append(func.__name__)
    return func

RECORDER = RecordingTransformer()
IMP_RETURN_PORT: ImplicitReturnPort = RECORDER  # mypy checks the fake here

@guarded_expression(lambda x: x > 0 or 'x must be positive', guard_port=GUARD_PORT, imp_return_port=IMP_RETURN_PORT)
def halve(x: int) -> float:
  return x / 2
```

`GUARD_PORT`, in the full file, is an auditing fake that logs every verdict and blocks nothing: a bouncer who only takes notes.

Full version: [examples/free_range/12_swapping_the_runtime.py](../examples/free_range/12_swapping_the_runtime.py)

How the wiring behaves:

- The first decoration in a process that leaves a port to injection, not the import, runs `Idunn().bootstrap('modgud')`. The decorators declare that with `@Invert(bootstrap='modgud')`; modgud itself never constructs `Idunn()`.
- A decoration that passes every port it takes (`guard_port=` and `imp_return_port=` for `guarded_expression`, `imp_return_port=` for `implicit_return`) triggers no discovery.
- Idunn reads `IDUNN_ENV` when its container is first created. modgud's adapters declare no environment, so it matters only to your own.
- `Idunn().reset()` clears the whole container, yours included. The next decoration re-discovers modgud; earlier functions keep working. Fixtures call `Idunn().reset(environment=Idunn().environment)` to keep the environment.

---

[← Back to Documentation Hub](ADVANCED.md) | [How It Works →](how-it-works.md)
