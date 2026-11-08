# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository. Humans are welcome to read it too; the rules are the same.

## 🧭 Project Overview

`modgud` is a Python library with two decorators. `guarded_expression` runs guard clauses before a function and, by default, rewrites the body so the last expression of each branch is the return value. `implicit_return` does only the rewrite. The point is a single return per function without the wall of `if` statements Python usually asks for. Three Elixir-style expression forms, `eop_cond`, `eop_case` and `eop_match`, ride on the same rewrite.

- **Guards**: callables that return `True` or an error string. `Guards` ships nine (`CommonGuards` is its pre-2.1 name, kept as an alias); `GuardRegistry` holds custom ones.
- **Failure handling**: `GuardFailureEnum` (`ERROR_RAISE` / `ERROR_RETURN` / `RETURN_VALUE` / `CALL_HANDLER`) paired with an `on_failure` payload. `continuance: int` caps how many guards past the first failure still run; several failures become an `ExceptionGroup`.
- **Expression forms**: `eop_cond` (ordered clauses), `eop_case` (patterns written as expressions) and `eop_match` (a pattern test), with `eop_clause`, `eop_when` and `eop_var`. Markers in `app/` that the rewrite compiles away; one `EopPort` adapter per form, keyed by `EopFormEnum`. Rules that differ from plain Python are in `docs/ADVANCED.md`.
- **Layers**: `app/` (decorators and markers, wired by Idunn, plus `Guards` and `GuardRegistry`), `domain/` (passive types, enums, errors, `@Port` protocols), `infrastructure/` (`adapters/`, internal `ast/` and `internal/`). The full tree and the dependency table live in `project.md`.

## ⚙️ Development Commands

**Always prefix with `poetry run`.** This is a Poetry project; never call `.venv/bin/...` directly.

### 🚨 MANDATORY LINT GATE 🚨

Run this BEFORE any code change, review, refactor, commit or pull request, and again after:

```bash
poetry run ruff check modgud/ tests/ examples/ --fix && poetry run ruff format modgud/ tests/ examples/ && poetry run mypy modgud/ examples/free_range/ && poetry run mypy examples/classy/
```

Ruff lints and formats; mypy runs in strict mode (configured in `pyproject.toml`). mypy runs once per examples tree because the two trees share filenames. If the gate is red after auto-fix, fix it first. **No exceptions, and no "it's only a docstring".**

```bash
poetry install --with dev        # Python 3.11+; pip users: pip install -e . --group dev
poetry run pytest                # all tests, with coverage (configured in pyproject.toml)
poetry run pytest tests/test_x.py
poetry build && poetry run twine check dist/*
```

## 📦 Public API and Tiers

Everything a user needs is `from modgud import ...`. Exactly 24 names, pinned by `tests/test_public_api.py`:

`CommonGuards` (alias of `Guards`), `Guards`, `EopPort`, `ExplicitReturnDisallowedError`, `GuardClauseError`, `GuardFailureEnum`, `GuardFunction`, `GuardRegistry`, `GuardPort`, `ImplicitReturnError`, `ImplicitReturnPort`, `MarkerNotRewrittenError`, `MarkerPlacementError`, `MarkerUsageError`, `MissingImplicitReturnError`, `UnsupportedConstructError`, `eop_case`, `eop_clause`, `eop_cond`, `eop_match`, `eop_var`, `eop_when`, `guarded_expression`, `implicit_return`.

| Tier | What | Where |
|---|---|---|
| Public | the 24 names above | `modgud` (also `modgud.domain`, 14 names, and `modgud.app`, 10 names) |
| Integration seam | the three ports, `guard_port=` / `imp_return_port=` / `eop_cond_port=` / `eop_case_port=` / `eop_match_port=`, `IDUNN_ENV`, `Idunn().reset()` | `modgud`, `modgud.domain` or `modgud.domain.ports` |
| Internal | the five adapters, the `ast` helpers, `MethodDescriptors` | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast`, `modgud.infrastructure.internal` |

Rules, and what enforces them (`test_architecture.py` checks import edges; `test_public_api.py` checks `__all__` and identity; the import style is convention, reviewed by hand):
- The root facade uses absolute imports and an explicit `__all__`. `modgud.domain`, `modgud.app` and the leaf packages re-export with single-dot relative imports and `__all__`. `modgud.infrastructure` exports nothing: re-exporting the guards from it would point infrastructure at `app`.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the `modgud.domain.<owner>` that holds the symbol (`enums`, `errors`, `ports` or `types`). That rule is what makes import cycles impossible.
- Ports are re-exported by `modgud.domain`, so a port module must never import `modgud.domain`; it imports `modgud.domain.enums`, `.errors` or `.types` directly. Going through the facade only works while `.types` loads before `.ports` in its `__init__`, and ruff's import sort puts `.ports` first. Everything else under `modgud/` takes a port from `modgud.domain.ports`.
- `GuardFunction` lives in a module directly under `domain`, and the only package above it is the facade, so `from modgud.domain.types import GuardFunction` is the sanctioned exception to never importing from filenames; don't "fix" it.
- Tests import public names from `modgud`. Leaf imports stay only where the leaf is the subject: the two adapter unit tests, `test_public_api.py` (identity checks) and the architecture probes.

## 🔌 Ports, Adapters and Idunn

`GuardPort`, `ImplicitReturnPort` and `EopPort` are `@Port` Protocols; the decorators depend on them only. `GuardAdapter` and `ImplicitReturnAdapter` subclass their port as `@Adapter(..., lifecycle=SINGLETON)`; `EopCondAdapter`, `EopCaseAdapter` and `EopMatchAdapter` subclass `EopPort` under their `EopFormEnum` key. Each decorator's `__init__` wears `@Invert(bootstrap='modgud', keys=...)`: the first decoration that leaves a port to injection runs `Idunn().bootstrap('modgud')`, which discovers `modgud.domain.ports` and `modgud.infrastructure.adapters`, then `guard_port` / `imp_return_port` / `eop_*_port` are injected. A caller-supplied port wins, which is the test seam; supply every port and nothing is discovered. The decorators only delegate: `guarded_expression.__call__` is one call to `GuardPort.transform(...)`, which rewrites (through the implicit-return port) and wraps; `implicit_return.__call__` is one call to `ImplicitReturnPort.transform(...)`. Both pass the three form ports along as `forms`, and the transformer lowers each form through its port. A marker called outside a decorated function reaches its port the same way, through a private `@Invert` helper, and is refused. Descriptor handling, the `__modgud_guarded__` / `__implicit_return__` markers and the stacking `TypeError` all live in the adapters. There is no composition-root module: `Idunn(` appears nowhere under `modgud/`, and `Invert` is imported only in `app`; the architecture test keeps it that way. `Idunn().reset()` clears the bootstrap so the next decoration re-discovers.

Import-time side effects, so nobody is surprised: `import modgud` imports `idunn`, and `Guards` registers its guards into the global `GuardRegistry`. Bootstrap itself waits for the first decoration.

## 🛡️ Behaviour to Preserve

**Single return point.** With `implicit_return=True` (default) the last expression in each branch is returned, explicit `return` is refused anywhere in the body (nested defs included), and a tail `match` must end in `case _:`. `@implicit_return()` above `@guarded_expression` raises `TypeError`. With `implicit_return=False` the body must end in one explicit `return`. Guards exit early from the wrapper, never from the body.

**Guard signature.** `(*args, **kwargs) -> True | str`. On a method the guards receive the call's arguments without `self` / `cls`; `CALL_HANDLER` handlers receive the full list.

**Failure chain.** Guards run in order. `continuance=0` stops at the first failure; `continuance=N` collects up to `1+N`. A guard that raises propagates when nothing has failed yet, otherwise it ends collection. Then: `ERROR_RAISE` raises `on_failure(msg)` or `ExceptionGroup('Guards failed', [...])`; `ERROR_RETURN` returns the same; `RETURN_VALUE` returns `on_failure`; `CALL_HANDLER` returns `on_failure(errors, *args, **kwargs)`. The body never runs after a failure.

**Implicit-return rewrite.** `inspect.getsource()` → AST → decorators stripped → `eop_` markers resolved by object identity and lowered through their ports (innermost first, preludes placed before the statement) → tail expressions assigned to `__implicit_result` → one `return` appended → compiled in a throwaway namespace, then re-bound to the function's *live* globals (the body sees names defined after decoration, including its own class). Methods are re-compiled inside stand-in classes named from `__qualname__`, so `self.__private` mangles correctly and `__qualname__` survives. Defaults and annotations are stripped from the re-compiled tree and reused from the original, so class-scope and module-scope names in them are fine. Refused at decoration time with `UnsupportedConstructError`: zero-argument `super()` and bare `__class__` (no cell after the rewrite). Instance, static, class and async methods all work, with modgud outside or inside `@staticmethod` / `@classmethod` (`modgud/infrastructure/internal/method_descriptors.py`).

**Expression forms.** `eop_cond` lowers in place to nested conditional expressions with Elixir's truth rule (only `None` and `False` are false). `eop_case` becomes a hoisted real `match` when the call is a whole statement's value, else one generated matcher per clause; `eop_match` is always a generated matcher returning `bool`. Captures are renamed `@mg_cap_<i>_<name>` in the hoisted path and never leak. A guard passes only when exactly `True` and a raising guard is a non-match, through a generated `try`. `default=` is mandatory. A bare name in a pattern compares by value; a call is always a class pattern; no `as` or `A | B`. Both modes lower the forms; in explicit mode a form-free function is returned untouched from a `co_names` probe. Malformed → `MarkerUsageError`; misplaced (comprehension first iterable, nested class body, a guard reading a comprehension variable) → `MarkerPlacementError`; a plain call → `MarkerNotRewrittenError`. `ast/` holds the shared engine (`MarkerResolver`, `FormLowerer`, `FormCallLowerer`, `PatternTranslator`, `MatcherBuilder`, `ClauseReader`, `CaptureSubstituter`); `infrastructure/internal/` is for shared code that is not AST work.

**Async.** A coroutine function gets an async wrapper: guards run when the coroutine runs, so a non-raising strategy's fallback comes back from `await`. Decorators placed *below* modgud are dropped by the re-compile (the source is read again); put modgud innermost, or use `implicit_return=False`.

**Python 3.14.** `functools.wraps` copies the lazy `__annotate__` hook, not `__annotations__`; the runtime and the transformer carry annotations in either form. Don't simplify that away.

## 🧪 Testing

Tests live in `tests/` (`test_*.py`). Decorated functions with implicit returns are re-compiled at module scope, so define them at module level (`tests/test_fixtures.py`, `tests/method_fixtures.py`) unless the test is about decoration-time errors. Closures over test locals are lost; source must exist on disk.

| File | Covers |
|---|---|
| `test_basic_guards.py`, `test_implicit_returns.py`, `test_edge_cases.py` | decorator behaviour end to end |
| `test_guard_adapter.py` | `GuardAdapter.check_guards` / `handle_failure` / `wrap_function` (the guard-only step under `transform`), continuance, cascade safety |
| `test_ast_transform.py` | the AST rewrite, unit level |
| `test_method_decoration.py` + `method_fixtures.py` | every method shape, metadata, the README classes verbatim |
| `test_ioc_wiring.py` | discovery on first use, injection, singletons, `reset()`, the fake `guard_port=` / `imp_return_port=` / `eop_*_port=` seam, keyed form adapters, no discovery when every port is supplied |
| `test_eop_cond.py`, `test_eop_match.py`, `test_eop_case.py` + `eop_fixtures.py` | each form end to end, both lowering paths of `eop_case` against handwritten `match` oracles, laziness, Elixir rules, positions, modes, methods, async |
| `test_eop_patterns.py`, `test_eop_adapters.py` | `PatternTranslator` row by row; the three adapters at unit level with a deterministic `fresh` |
| `test_eop_refusals.py` | every `MarkerUsageError` and `MarkerPlacementError` case, and each marker refusing outside a decorator |
| `test_architecture.py` | AST-walks `modgud/` against the dependency table in `project.md`, with probe self-checks |
| `test_public_api.py` | the `__all__` lists, identity with the leaf objects, two fresh-process checks |
| `test_examples.py` | runs every file under `examples/` in a subprocess, checks the index and the classy rules |
| `test_docs.py` | executes every import line in the docs, checks links and banned wording |

## 🗂️ Examples

`examples/free_range/` holds module-level decorated functions and is exempt from the single-class-per-file and no-loose-functions rules; that is what the files demonstrate. `examples/classy/` holds one class per file, no module-level `def`, a `demo()` classmethod with the asserts. Same numbering in both trees, no `__init__.py`, nothing runnable under `modgud/` (Idunn imports everything there). Docs show excerpts of 12 lines or fewer and link to the full file.

## 📜 Configuration

- `ruff.toml`: Python 3.11 target, 2-space indent, 100 columns, single quotes; `src = ["modgud", "tests", "examples"]`.
- `pyproject.toml`: PEP 621 metadata, Poetry build, pytest with coverage on `modgud/`, strict mypy (`[tool.mypy]`), runtime dependency `idunn (>=2.0.0,<3.0.0)` from PyPI, Python >=3.11. A commented-out `[tool.poetry.dependencies]` line can point `idunn` at the sibling checkout `../idunn` while developing both; never release with it enabled.

## 📜 Import Examples

```python
from modgud import Guards, GuardFailureEnum, guarded_expression


@guarded_expression(Guards.positive('x'))
def double(x):
  x * 2  # implicit return


@guarded_expression(Guards.positive('x'), strategy=GuardFailureEnum.RETURN_VALUE, on_failure=-1)
def safe_square(x):
  x * x


@guarded_expression(Guards.positive('x'), Guards.positive('y'), continuance=2)
def add(x, y):
  x + y
```

Full versions live in `examples/`. Error hierarchy: `GuardClauseError(Exception)`; `ImplicitReturnError(SyntaxError)` with `ExplicitReturnDisallowedError`, `MissingImplicitReturnError` and `UnsupportedConstructError`.
