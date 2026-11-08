![Modgud](https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg)

# modgud

Most functions that take input open the same way: a wall of `if`s, each with its own early `return`, and the real work somewhere near the bottom.

```python
def create_user(email, age, username, password):
  if not email:
    return {'status': 400, 'errors': ['email cannot be empty']}
  if not 13 <= age <= 120:
    return {'status': 400, 'errors': ['age must be between 13 and 120']}
  if not username:
    return {'status': 400, 'errors': ['username cannot be empty']}
  return {'status': 201, 'user_id': save_user(email, age, username, hash_password(password))}
```

Four exits. One of them does the job, and the caller only ever hears about the first bad field. modgud moves the checks into a decorator and lets the last expression be the return value:

```python
from modgud import Guards, GuardFailureEnum, guarded_expression

@guarded_expression(
  Guards.not_empty('email'),
  Guards.in_range(13, 120, 'age', position=1),
  Guards.not_empty('username', position=2),
  continuance=6,
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=bad_request,
)
def create_user(email, age, username, password):
  {'status': 201, 'user_id': save_user(email, age, username, hash_password(password))}
```

Full version: [examples/free_range/09_api_endpoint.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/09_api_endpoint.py)

`continuance=6` keeps checking after the first failure, so `bad_request` gets the whole list and the caller gets one 400 with every complaint in it.

The contract goes on top. The body does the work.

## 🧭 Overview

modgud gives Python two decorators. `@guarded_expression(...)` runs guard functions before the body and decides what happens when one fails. `@implicit_return()` rewrites the function so the last expression in each branch is returned, the way Ruby, Rust and Scala already behave. `@guarded_expression` does both by default.

Python made `if` a statement in 1991 and has wanted a `return` in every branch ever since. modgud rewrites the function once, at decoration time, so each branch ends on a value and the function keeps a single exit. Nothing is rewritten per call.

## 📦 Install

```bash
pip install modgud
```

Python 3.11 or newer. One runtime dependency: [Idunn](https://pypi.org/project/idunn), which wires the decorators to their implementations.

## 🌱 Quick start

```python
from modgud import Guards, guarded_expression, implicit_return


class DiscountCalculator:
  @staticmethod
  @guarded_expression(
    Guards.positive('x'),
    Guards.in_range(1, 100, 'x'),
  )
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1


DiscountCalculator.calculate(75)  # 15.0
DiscountCalculator.calculate(25)  # 2.5
DiscountCalculator.calculate(-10)  # raises GuardClauseError: x must be positive
```

Same function, two decorators, one job each. Guards go on the outside and the rewrite sits closest to the `def`; the other order quietly skips the guards:

```python
class DiscountCalculatorV2:
  @staticmethod
  @guarded_expression(
    Guards.positive('x'),
    Guards.in_range(1, 100, 'x'),
    implicit_return=False,
  )
  @implicit_return()
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1
```

Full version: [examples/classy/01_quick_start.py](https://github.com/terracoil/modgud/blob/main/examples/classy/01_quick_start.py)

## 🛡️ Feature tour

**Pre-built guards.** `Guards` (formerly `CommonGuards`, which still works) has nine: `not_none`, `not_empty`, `positive`, `in_range`, `type_check`, `matches_pattern`, `valid_file_path`, `valid_url` and `valid_enum`. Each finds its parameter by name in the keyword arguments, else by `position` (0 by default), which is why the second and third parameters above say `position=1` and `position=2`. See [Guards](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#guards) and [02_common_guards.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/02_common_guards.py).

**Custom guards.** A guard is any callable that takes `(*args, **kwargs)` and returns `True` to pass or a message string to fail. No base class, no registration.

```python
from modgud import guarded_expression


def fragile_ok(*args, **kwargs):
  mode = kwargs.get('mode', args[1] if len(args) > 1 else '')
  fragile = kwargs.get('fragile', args[2] if len(args) > 2 else False)
  return not (fragile and mode == 'sea') or 'fragile parcels cannot go by sea'


@guarded_expression(fragile_ok)
def ship(kg, mode, fragile=False):
  f'{kg} kg by {mode}'
```

Full version: [examples/free_range/07_custom_guards.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/07_custom_guards.py)

When the same guard shows up in five modules, `GuardRegistry` stores its factory by name, in an optional namespace. See [GuardRegistry](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#guardregistry).

**When a guard fails.** `strategy` picks the behaviour and `on_failure` is its payload:

| `strategy` | The caller gets |
|---|---|
| `ERROR_RAISE` (default) | `on_failure(message)` raised; `GuardClauseError` unless you name another class |
| `ERROR_RETURN` | the same exception, returned instead of raised |
| `RETURN_VALUE` | `on_failure`, as-is |
| `CALL_HANDLER` | whatever `on_failure(errors, *args, **kwargs)` returns |

The body never runs once a guard has failed. Details: [GuardFailureEnum](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#guardfailureenum) and [03_failure_strategies.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/03_failure_strategies.py).

**More than one failure.** Guards stop at the first failure. `continuance=N` keeps checking up to `N` more, so a form with three bad fields reports three, not one per round trip. The error strategies then hand back an `ExceptionGroup` for `except*` to take apart. See [06_continuance.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/06_continuance.py).

**Implicit returns.** The tail of every branch must produce a value: `if`/`elif`/`else`, `try`/`except`/`else` and `match`/`case` all work; a tail `match` must end in `case _:`. A `return` anywhere in the decorated function, nested functions included, or a branch that ends without a value, is refused at decoration time. Import time, in practice, not the first call in production. Pass `implicit_return=False` to keep explicit returns and use the guards alone. See [implicit_return](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#implicit_return) and [04_implicit_returns.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/04_implicit_returns.py).

**Expression forms.** Three Elixir-style forms turn ordered conditions and pattern matching into expressions, so they fit in a tail, an assignment or a comprehension. Each one needs a modgud decorator on the function.

```python
from modgud import eop_case, eop_clause, eop_cond, eop_match, eop_var, implicit_return


@implicit_return()
def sign(x):
  eop_cond(eop_clause(x < 0, 'negative'), eop_clause(x == 0, 'zero'), default='positive')


@implicit_return()
def first_two(values):
  eop_case(values, eop_clause([eop_var.a, eop_var.b, *eop_var._], (eop_var.a, eop_var.b)), default=None)
```

`eop_match(pattern, value)` is the same matching as a `bool`. See [Expression forms](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#expression-forms), [13_eop_cond.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/13_eop_cond.py), [14_eop_case.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/14_eop_case.py) and [15_eop_match.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/15_eop_match.py). The rules that differ from plain Python, such as Elixir's truth rule and guards, are in the [docs hub](https://github.com/terracoil/modgud/blob/main/docs/ADVANCED.md#-expression-forms-past-the-basics).

**Methods and async.** Instance methods, `@staticmethod`, `@classmethod` and `async def` all work, with modgud on either side of the built-in decorator. When the first parameter is named `self` or `cls`, guards see the arguments without it. Two shapes are refused at decoration time: zero-argument `super()` and a bare `__class__`; write `super(Cls, self)` instead. Defaults that name class attributes are fine. `@property` and descriptors are not covered. See [Methods](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#methods), [classy/10_decorator_composition.py](https://github.com/terracoil/modgud/blob/main/examples/classy/10_decorator_composition.py) and [08_async_functions.py](https://github.com/terracoil/modgud/blob/main/examples/free_range/08_async_functions.py).

## 🗂️ Examples

The [examples](https://github.com/terracoil/modgud/blob/main/examples/README.md) come in two trees. In `free_range/`, decorated functions roam the module at top level, unfenced. In `classy/`, they live indoors: one class per file, instance, static and class methods, every house rule obeyed. Each classy file has a free-range twin with the same number. The test suite runs all of them, so an example that stops working fails the build.

```bash
poetry run python examples/free_range/01_quick_start.py
```

## ⚖️ Limitations

- Implicit returns need the function's source on disk; modgud can't rewrite what `inspect` can't read. Functions typed into a REPL or built with `exec` get the guards with `implicit_return=False`, but not the rewrite.
- `GuardRegistry` and the Idunn container are process-wide singletons. `GuardRegistry` has no lock, so register guards at import time, not from worker threads.
- The `eop_` forms are rewritten at decoration time, so they work only inside a function decorated with `guarded_expression` or `implicit_return`. Called anywhere else they raise `MarkerNotRewrittenError`.
- The status is Beta. The 23 names in `from modgud import ...` are the supported surface; anything deeper may move.

The rest are in [How it works: Limitations](https://github.com/terracoil/modgud/blob/main/docs/how-it-works.md#limitations), with what is shared between threads under [Thread safety](https://github.com/terracoil/modgud/blob/main/docs/how-it-works.md#thread-safety).

## 🌉 The name

In Norse myth, Móðguðr guards Gjallarbrú, the bridge over the river Gjöll on the road to Hel. Every traveller stops and states a name and business before crossing. modgud asks the same of your arguments, with milder consequences for the ones that fail. It also reads as "mod gud". That part was on purpose.

## 📚 Documentation

- [Docs hub](https://github.com/terracoil/modgud/blob/main/docs/ADVANCED.md): which document covers what, and where to start.
- [API reference](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md): signatures, parameter tables, errors, and the integration seam for swapping the runtime in tests ([Integration seam](https://github.com/terracoil/modgud/blob/main/docs/api-reference.md#integration-seam)).
- [How it works](https://github.com/terracoil/modgud/blob/main/docs/how-it-works.md): the guard pipeline, the AST rewrite and the Idunn wiring.

## 🤝 Contributing

Install with `poetry install --with dev`, run the lint gate and `poetry run pytest`, and open a pull request with tests.
The default suite also polices the layering, runs every example and checks the docs' imports and links.
Details: [CONTRIBUTING.md](https://github.com/terracoil/modgud/blob/main/CONTRIBUTING.md).

## 📜 License

MIT. See [LICENSE](https://github.com/terracoil/modgud/blob/main/LICENSE).
