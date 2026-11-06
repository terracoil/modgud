# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository. Humans are welcome to read it too; the rules are the same.

## 🧭 Project Overview

`modgud` is a Python library with two decorators. `guarded_expression` runs guard clauses before a function and, by default, rewrites the body so the last expression of each branch is the return value. `implicit_return` does only the rewrite. The point is a single return per function without the wall of `if` statements Python usually asks for.

- **Guards**: callables that return `True` or an error string. `CommonGuards` ships nine; `GuardRegistry` holds custom ones.
- **Failure handling**: `GuardFailureEnum` (`ERROR_RAISE` / `ERROR_RETURN` / `RETURN_VALUE` / `CALL_HANDLER`) paired with an `on_failure` payload. `continuance: int` caps how many guards past the first failure still run; several failures become an `ExceptionGroup`.
- **Layers**: `app/` (decorators, wired by Idunn, plus `CommonGuards` and `GuardRegistry`), `domain/` (passive types, enums, errors, `@Port` protocols), `infrastructure/` (`adapters/`, internal `ast/`). The full tree and the dependency table live in `project.md`.

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

Everything a user needs is `from modgud import ...`. Exactly 13 names, pinned by `tests/test_public_api.py`:

`CommonGuards`, `ExplicitReturnDisallowedError`, `GuardClauseError`, `GuardFailureEnum`, `GuardFunction`, `GuardRegistry`, `GuardPort`, `ImplicitReturnError`, `ImplicitReturnPort`, `MissingImplicitReturnError`, `UnsupportedConstructError`, `guarded_expression`, `implicit_return`.

| Tier | What | Where |
|---|---|---|
| Public | the 13 names above | `modgud` (also `modgud.domain`, 9 names, and `modgud.app`, 4 names) |
| Integration seam | the two ports, `runtime=` / `transformer=`, `IDUNN_ENV`, `Idunn().reset()` | `modgud`, `modgud.domain` or `modgud.domain.ports` |
| Internal | `GuardAdapter`, `ImplicitReturnAdapter`, the `ast` helpers | `modgud.infrastructure.adapters`, `modgud.infrastructure.ast` |

Rules, and what enforces them (`test_architecture.py` checks import edges; `test_public_api.py` checks `__all__` and identity; the import style is convention, reviewed by hand):
- The root facade uses absolute imports and an explicit `__all__`. `modgud.domain`, `modgud.app` and the leaf packages re-export with single-dot relative imports and `__all__`. `modgud.infrastructure` exports nothing: re-exporting the guards from it would point infrastructure at `app`.
- **Nothing inside `modgud/` imports a facade.** Inner modules import from the `modgud.domain.<owner>` that holds the symbol (`enums`, `errors`, `ports` or `types`). That rule is what makes import cycles impossible.
- Ports are re-exported by `modgud.domain`, so a port module must never import `modgud.domain`; it imports `modgud.domain.enums`, `.errors` or `.types` directly. Going through the facade only works while `.types` loads before `.ports` in its `__init__`, and ruff's import sort puts `.ports` first. Everything else under `modgud/` takes a port from `modgud.domain.ports`.
- `GuardFunction` lives in a module directly under `domain`, and the only package above it is the facade, so `from modgud.domain.types import GuardFunction` is the sanctioned exception to never importing from filenames; don't "fix" it.
- Tests import public names from `modgud`. Leaf imports stay only where the leaf is the subject: the two adapter unit tests, `test_public_api.py` (identity checks) and the architecture probes.

## 🔌 Ports, Adapters and Idunn

`GuardPort` and `ImplicitReturnPort` are `@Port` Protocols; the decorators depend on them only. `GuardAdapter` and `ImplicitReturnAdapter` subclass their port as `@Adapter(..., lifecycle=SINGLETON)`. Each decorator's `__init__` wears `@Invert(bootstrap='modgud')`: the first decoration that leaves a port to injection runs `Idunn().bootstrap('modgud')`, which discovers `modgud.domain.ports` and `modgud.infrastructure.adapters`, then `runtime` / `transformer` are injected. A caller-supplied `runtime=` / `transformer=` wins, which is the test seam; supply every port and nothing is discovered. There is no composition-root module: `Idunn(` appears nowhere under `modgud/`, and the architecture test keeps it that way. `Idunn().reset()` clears the bootstrap so the next decoration re-discovers.

Import-time side effects, so nobody is surprised: `import modgud` imports `idunn`, and `CommonGuards` registers its guards into the global `GuardRegistry`. Bootstrap itself waits for the first decoration.

## 🛡️ Behaviour to Preserve

**Single return point.** With `implicit_return=True` (default) the last expression in each branch is returned, explicit `return` is refused anywhere in the body (nested defs included), and a tail `match` must end in `case _:`. `@implicit_return()` above `@guarded_expression` raises `TypeError`. With `implicit_return=False` the body must end in one explicit `return`. Guards exit early from the wrapper, never from the body.

**Guard signature.** `(*args, **kwargs) -> True | str`. On a method the guards receive the call's arguments without `self` / `cls`; `CALL_HANDLER` handlers receive the full list.

**Failure chain.** Guards run in order. `continuance=0` stops at the first failure; `continuance=N` collects up to `1+N`. A guard that raises propagates when nothing has failed yet, otherwise it ends collection. Then: `ERROR_RAISE` raises `on_failure(msg)` or `ExceptionGroup('Guards failed', [...])`; `ERROR_RETURN` returns the same; `RETURN_VALUE` returns `on_failure`; `CALL_HANDLER` returns `on_failure(errors, *args, **kwargs)`. The body never runs after a failure.

**Implicit-return rewrite.** `inspect.getsource()` → AST → decorators stripped → tail expressions assigned to `__implicit_result` → one `return` appended → compiled in a throwaway namespace, then re-bound to the function's *live* globals (the body sees names defined after decoration, including its own class). Methods are re-compiled inside stand-in classes named from `__qualname__`, so `self.__private` mangles correctly and `__qualname__` survives. Defaults and annotations are stripped from the re-compiled tree and reused from the original, so class-scope and module-scope names in them are fine. Refused at decoration time with `UnsupportedConstructError`: zero-argument `super()` and bare `__class__` (no cell after the rewrite). Instance, static, class and async methods all work, with modgud outside or inside `@staticmethod` / `@classmethod` (`modgud/app/method_descriptors.py`).

**Async.** A coroutine function gets an async wrapper: guards run when the coroutine runs, so a non-raising strategy's fallback comes back from `await`. Decorators placed *below* modgud are dropped by the re-compile (the source is read again); put modgud innermost, or use `implicit_return=False`.

**Python 3.14.** `functools.wraps` copies the lazy `__annotate__` hook, not `__annotations__`; the runtime and the transformer carry annotations in either form. Don't simplify that away.

## 🧪 Testing

Tests live in `tests/` (`test_*.py`). Decorated functions with implicit returns are re-compiled at module scope, so define them at module level (`tests/test_fixtures.py`, `tests/method_fixtures.py`) unless the test is about decoration-time errors. Closures over test locals are lost; source must exist on disk.

| File | Covers |
|---|---|
| `test_basic_guards.py`, `test_implicit_returns.py`, `test_edge_cases.py` | decorator behaviour end to end |
| `test_guard_adapter.py` | `GuardAdapter.check_guards` / `handle_failure` / `wrap_function`, continuance, cascade safety |
| `test_ast_transform.py` | the AST rewrite, unit level |
| `test_method_decoration.py` + `method_fixtures.py` | every method shape, metadata, the README classes verbatim |
| `test_ioc_wiring.py` | discovery on first use, injection, singletons, `reset()`, the fake `runtime=` / `transformer=` seam, no discovery when every port is supplied |
| `test_architecture.py` | AST-walks `modgud/` against the dependency table in `project.md`, with probe self-checks |
| `test_public_api.py` | the `__all__` lists, identity with the leaf objects, two fresh-process checks |
| `test_examples.py` | runs every file under `examples/` in a subprocess, checks the index and the classy rules |
| `test_docs.py` | executes every import line in the docs, checks links and banned wording |

## 🗂️ Examples

`examples/free_range/` holds module-level decorated functions and is exempt from the single-class-per-file and no-loose-functions rules; that is what the files demonstrate. `examples/classy/` holds one class per file, no module-level `def`, a `demo()` classmethod with the asserts. Same numbering in both trees, no `__init__.py`, nothing runnable under `modgud/` (Idunn imports everything there). Docs show excerpts of 12 lines or fewer and link to the full file.

## 📜 Configuration

- `ruff.toml`: Python 3.11 target, 2-space indent, 100 columns, single quotes; `src = ["modgud", "tests", "examples"]`.
- `pyproject.toml`: PEP 621 metadata, Poetry build, pytest with coverage on `modgud/`, strict mypy (`[tool.mypy]`), runtime dependency `idunn (>=2.0.0,<3.0.0)`, Python >=3.11. Until Idunn 2.0 is on PyPI, `[tool.poetry.dependencies]` points `idunn` at the sibling checkout `../idunn`; drop that table and re-lock before release.

## 📜 Import Examples

```python
from modgud import CommonGuards, GuardFailureEnum, guarded_expression


@guarded_expression(CommonGuards.positive('x'))
def double(x):
  x * 2  # implicit return


@guarded_expression(CommonGuards.positive('x'), strategy=GuardFailureEnum.RETURN_VALUE, on_failure=-1)
def safe_square(x):
  x * x


@guarded_expression(CommonGuards.positive('x'), CommonGuards.positive('y'), continuance=2)
def add(x, y):
  x + y
```

Full versions live in `examples/`. Error hierarchy: `GuardClauseError(Exception)`; `ImplicitReturnError(SyntaxError)` with `ExplicitReturnDisallowedError`, `MissingImplicitReturnError` and `UnsupportedConstructError`.
