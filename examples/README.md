# Examples

Twenty-six small scripts that each prove one thing about modgud. Every one ends in `assert`s, so if it exits with code 0, the claim in its docstring holds on your machine. The `print`s are just there so you can see it happen.

## 🗂️ Two trees, same lessons

The examples come in two flavours. They share numbers and filenames, so `07` in one tree teaches the same thing as `07` in the other.

- **`free_range/`** puts decorated functions at module level, which is how most people meet a decorator. These files skip two of this repo's house rules (one class per file, no loose functions) so the lesson stays in view.
- **`classy/`** follows every house rule: one class per file, decorated static, class and instance methods, and a `demo()` classmethod holding the asserts.

Free-range functions roam the module wherever they like. Classy ones live in a class, keep a docstring on every method, and have exactly one way out.

Not every lesson needs both shapes, so `classy/` has 11 files to `free_range/`'s 15. Where a method version would only add ceremony, there isn't one.

## Running them

From the repo root:

```bash
poetry run python examples/free_range/01_quick_start.py
poetry run python examples/classy/01_quick_start.py
```

`tests/test_examples.py` runs all of them as part of `poetry run pytest`, so a broken example fails the suite.

## 🌱 The basics

| # | free_range | classy | What it shows |
|---|---|---|---|
| 01 | [01_quick_start.py](free_range/01_quick_start.py) | [01_quick_start.py](classy/01_quick_start.py) | One guard, an implicit return, and catching `GuardClauseError`. The classy file is the README's `DiscountCalculator`. |
| 02 | [02_common_guards.py](free_range/02_common_guards.py) | | All nine `Guards`, and how `position=` finds the argument to check. |
| 03 | [03_failure_strategies.py](free_range/03_failure_strategies.py) | [03_failure_strategies.py](classy/03_failure_strategies.py) | `ERROR_RAISE`, `ERROR_RETURN`, `RETURN_VALUE` and `CALL_HANDLER`, plus a custom exception class. |
| 04 | [04_implicit_returns.py](free_range/04_implicit_returns.py) | [04_implicit_returns.py](classy/04_implicit_returns.py) | `@implicit_return()` on if/elif/else, try/except/else and match/case, with a helper kept outside the body, since `return` is refused anywhere inside it. |
| 05 | [05_explicit_return_mode.py](free_range/05_explicit_return_mode.py) | | `implicit_return=False` with a single trailing `return`. |

## 🧰 Everyday tools

| # | free_range | classy | What it shows |
|---|---|---|---|
| 06 | [06_continuance.py](free_range/06_continuance.py) | [06_continuance.py](classy/06_continuance.py) | `continuance=N`, the resulting `ExceptionGroup`, `except*`, and cascade safety. |
| 07 | [07_custom_guards.py](free_range/07_custom_guards.py) | [07_custom_guards.py](classy/07_custom_guards.py) | Hand-written guards, a factory typed with `GuardFunction`, and `GuardRegistry`. |
| 08 | [08_async_functions.py](free_range/08_async_functions.py) | [08_async_functions.py](classy/08_async_functions.py) | Guards and implicit returns on `async def`. |
| 09 | [09_api_endpoint.py](free_range/09_api_endpoint.py) | [09_api_endpoint.py](classy/09_api_endpoint.py) | The README's API endpoint, finished: every failure comes back as one 400 payload. |

## 🔬 Under the hood

| # | free_range | classy | What it shows |
|---|---|---|---|
| 10 | [10_decorator_composition.py](free_range/10_decorator_composition.py) | [10_decorator_composition.py](classy/10_decorator_composition.py) | Free-range: stacking order, the right one and the `TypeError` for the wrong one, and the metadata that survives. Classy: every method shape, modgud on either side of `@staticmethod`/`@classmethod`, zero-argument `super()` refused, and `@implicit_return()` refused above a guarded method. |
| 11 | [11_decoration_errors.py](free_range/11_decoration_errors.py) | | The three `ImplicitReturnError` subclasses, raised when the decorator is applied. |
| 12 | [12_swapping_the_runtime.py](free_range/12_swapping_the_runtime.py) | | Fakes typed against `GuardPort` and `ImplicitReturnPort`, passed as `guard_port=` / `imp_return_port=`. |

## 🧩 Expression forms

| # | free_range | classy | What it shows |
|---|---|---|---|
| 13 | [13_eop_cond.py](free_range/13_eop_cond.py) | [13_eop_cond.py](classy/13_eop_cond.py) | `eop_cond`: ordered clauses as one expression, lazy values, Elixir's truth rule, use in a comprehension. |
| 14 | [14_eop_case.py](free_range/14_eop_case.py) | [14_eop_case.py](classy/14_eop_case.py) | `eop_case`: class, sequence and mapping patterns written as expressions, `eop_when` guards, captures that stay in their clause. |
| 15 | [15_eop_match.py](free_range/15_eop_match.py) | [15_eop_match.py](classy/15_eop_match.py) | `eop_match`: a pattern test that returns a `bool`, with a guard, as a comprehension filter. |

## Conventions

Imports are `from modgud import ...` plus the standard library, nothing deeper. Each file has a module docstring with its purpose, a `Run:` line and a `See:` link, and stays under 80 lines.
