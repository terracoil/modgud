# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `modgud`, a Python library that provides guard clause decorators for implementing validation checks at function entry points. The library enforces single return point architecture and supports various failure behaviors including custom return values, exception raising, and handler functions.

**Core Architecture (v2.0.0):**
- **Primary API**: `guarded_expression` - unified decorator combining guard validation + implicit returns
- **Expression decorator**: `implicit_return` (standalone)
- **Guard system**: Pre-built guards + `GuardRegistry` for custom validators
- **Failure handling**: Single `GuardFailureEnum` enum (`ERROR_RAISE` / `ERROR_RETURN` / `RETURN_VALUE` / `CALL_HANDLER`) paired with an `on_failure` payload; `continuance: int` caps how many guards past the first failure are evaluated. Multiple collected failures produce an `ExceptionGroup` for the error strategies.
- **Architecture**: Clean separation across `app/` (decorators wired by Idunn), `infrastructure/` (`adapters/` + `common/` + internal `ast/`), `domain/` (passive types/enums/exceptions + `@Port` protocols).

## Development Commands

**IMPORTANT: Always use `poetry run` prefix** - This is a Poetry project. ALWAYS use `poetry run` before commands like `pytest`, `ruff`, `mypy`, etc. Do NOT use `.venv/bin/` paths directly.

### 🚨 MANDATORY LINTING REQUIREMENT 🚨

**CRITICAL**: You MUST run linting BEFORE:
- Making ANY code changes
- Performing code reviews
- Starting refactoring work. If there are linting and/or mypy typing issues found, fix those first before refactoring.
- Committing changes
- Creating pull requests

Run these commands:
```bash
poetry run ruff check modgud/ --fix && poetry run ruff format modgud/ && poetry run mypy modgud/
```

This runs:
1. **Ruff linting** - catches code quality issues (with auto-fix)
2. **Ruff formatting** - ensures consistent code style
3. **MyPy type checking** - validates type annotations with strict settings

**FAILURE TO RUN LINTING = INVALID CODE SUBMISSION**

If linting fails after auto-fix, you MUST resolve all errors before proceeding. No exceptions.

### Package Management
**This is a Poetry project** - use Poetry for all dependency management:

```bash
# Install dependencies (Python 3.11+ required)
poetry install

# Install with test dependencies
poetry install --with test

# Install with development dependencies
poetry install --with dev
```

### Testing
```bash
# Run all tests with Poetry
poetry run pytest

# Run with coverage (configured in pyproject.toml)
poetry run pytest --cov=modgud --cov-report=term-missing --cov-report=html

# Run specific test file
poetry run pytest tests/test_specific.py

# Run tests with verbose output
poetry run pytest -v
```

### Code Quality
```bash
# Run ruff linting and formatting with Poetry
poetry run ruff check
poetry run ruff format

# Run mypy type checking
poetry run mypy modgud/

# Generate mypy reports (requires mypy[reports])
poetry run mypy modgud/ --html-report reports/mypy/ --linecount-report reports/mypy/ --linecoverage-report reports/mypy/
```

### Build and Distribution
```bash
# Build package with Poetry
poetry build

# Check package
poetry run twine check dist/*
```

## Code Architecture

Per-feature decomposition (see `project.md` at the repo root for the full dependency table, enforced by `tests/test_architecture.py`). Dependencies flow downward only: `app → domain.<feature>` and `domain.<feature>.ports`; `infrastructure.adapters → domain.<feature>`, its `ports`, `infrastructure.common` and `infrastructure.ast`; `infrastructure.common → domain.<feature>`; `infrastructure.ast → domain.<feature>`. The app layer never imports infrastructure, and infrastructure never imports app. The `domain` layer is self-contained (its shared `GuardFunction` type lives in `domain/guarded_expr/types.py`); its only third-party import is `idunn.Port`, and only inside `ports/` modules.

```
modgud/
  app/                                # public decorators (entry points)
    wiring.py                         # Wiring.ensure() — the single Idunn composition root (not re-exported)
    guarded_expression.py             # @guarded_expression(...) — class, @Invert() __init__
    implicit_return.py                # @implicit_return() — class, @Invert() __init__
  domain/                             # container package — no re-exports
    guarded_expr/
      enums/guard_failure_enum.py     # GuardFailureEnum (IntEnum)
      errors/guard_clause_error.py    # GuardClauseError
      types.py                        # GuardFunction (used by app + infra)
      ports/guard_runtime_port.py     # @Port GuardRuntimePort
    implicit_ret/
      errors/                         # one exception per module
        implicit_return_error.py      # ImplicitReturnError (base)
        explicit_return_disallowed_error.py
        missing_implicit_return_error.py
        unsupported_construct_error.py
      ports/implicit_return_transformer_port.py  # @Port ImplicitReturnTransformerPort
  infrastructure/                     # container package — no re-exports
    adapters/                         # @Adapter implementations, discovered by Idunn
      guard_runtime.py                # GuardRuntime(GuardRuntimePort) — guard eval + dispatch
      implicit_return_transformer.py  # ImplicitReturnTransformer(ImplicitReturnTransformerPort) — AST rewriter
    common/
      common_guards.py                # CommonGuards (pre-built validators)
      guard_registry.py               # GuardRegistry (custom guard registration)
    ast/                              # internal AST helpers, re-exported by its __init__ only
      _no_explicit_return_checker.py  # NoExplicitReturnChecker
      _tail_rewriter.py               # TailRewriter
      _top_level_transformer.py       # TopLevelTransformer
```

**Ports**: `GuardRuntimePort` and `ImplicitReturnTransformerPort` are `@Port` Protocols, and the app decorators depend on them only. Both adapters subclass their port and are `@Adapter(..., lifecycle=SINGLETON)`. On the first decoration, `__new__` calls `Wiring.ensure()` → `Idunn().bootstrap('modgud')`, which discovers `modgud.domain.*.ports` and `modgud.infrastructure.adapters`. `@Invert()` on each decorator's `__init__` then injects `runtime` / `transformer`; a caller-supplied `runtime=` / `transformer=` wins, which is the test seam. `Idunn(` appears only in `modgud/app/wiring.py`. `Idunn().reset()` clears the bootstrap cache, so the next decoration re-discovers.

**Ports import exception**: ports are imported from the 4-level path `modgud.domain.<feature>.ports`, not re-exported by the feature package, because re-exporting them there creates a circular import (each port module imports from its feature package). This is the one sanctioned exception to the 3-level import rule; don't "fix" it.

**Public API**: the package structure *is* the API — there is no flat top-level re-export. `modgud/__init__.py`, `modgud/domain/__init__.py`, and `modgud/infrastructure/__init__.py` are pure containers (docstring only; `modgud/__init__.py` also holds `__version__`). Import each symbol from the leaf subpackage that owns it: decorators from `modgud.app`; `GuardFailureEnum`/`GuardClauseError`/`GuardFunction` from `modgud.domain.guarded_expr`; the implicit-return errors from `modgud.domain.implicit_ret`; `CommonGuards`/`GuardRegistry` from `modgud.infrastructure.common`. `GuardRuntime`/`ImplicitReturnTransformer` live in `modgud.infrastructure.adapters`, which nothing in `modgud/` imports; only tests do. The guard validators are static methods on `CommonGuards` (e.g. `CommonGuards.positive('x')`). `@implicit_return()` takes parentheses.

### Key Design Patterns

**Single Return Point**: All decorated functions maintain single return semantics:
- With `implicit_return=True` (default): Last expression in each branch is auto-returned (no explicit `return` allowed)
- With `implicit_return=False`: Explicit `return` statement must be last line, not contained in any block
- Guard clauses handle early exits by returning from decorator wrapper

**Guard Function Signature**: Guards are callables that accept `(*args, **kwargs)` and return either `True` (pass) or a string error message (fail).

**Failure Behavior Chain**:
1. Guards are evaluated in order. Default `continuance=0` stops at the first failure; `continuance=N` collects up to `1+N` failures. A guard that *raises* propagates if no prior failures were recorded, otherwise it terminates collection (cascade safety).
2. Collected failure strings (`list[str]`) are dispatched through `GuardFailureEnum`:
   - `ERROR_RAISE` (default): raise `on_failure(msg)` for a single error, or `ExceptionGroup('Guards failed', [...])` for multiple.
   - `ERROR_RETURN`: same instances, but *returned* instead of raised.
   - `RETURN_VALUE`: return `on_failure` as-is.
   - `CALL_HANDLER`: return `on_failure(errors, *args, **kwargs)`. `errors` is always a list.
3. The wrapped function body is never executed when at least one failure was recorded.

**Implicit Return Transformation** (when `implicit_return=True`):
1. Function source code extracted via `inspect.getsource()`
2. AST parsed and decorators stripped to prevent re-application
3. Tail position expressions transformed to assign to hidden `__implicit_result` variable
4. Single `return __implicit_result` appended
5. Transformed AST compiled and exec'd in original function's global scope
6. Resulting function wrapped with guard checking logic

### Configuration Files

**ruff.toml**: Standalone ruff configuration
- Targets Python 3.11
- 2-space indentation, 100-character line length
- Single quote style for consistency
- Includes `modgud/` and `tests/` directories

**pyproject.toml**: Project metadata and tool configuration
- Uses PEP 621 project format with Poetry dependencies
- pytest configured for `tests/` directory with coverage for `modgud/`
- mypy configured with reports output to `reports/mypy/`
- Requires Python >=3.11
- Runtime dependency: `idunn (>=1.0.1,<2.0.0)` from PyPI.

## Testing Strategy

Tests should be placed in `tests/` directory following pytest conventions (`test_*.py` or `*_test.py`). The library uses extensive examples in `modgud/README.md` which can guide test case development.

**Test Files:**
- `tests/test_basic_guards.py` - Core guarded_expression behavior
- `tests/test_ast_transform.py` - Unit tests for AST transformation logic
- `tests/test_guard_runtime.py` - Unit tests for `check_guards` / `handle_failure` / `wrap_function`
- `tests/test_fixtures.py` - Module-level test fixtures for implicit return tests
- `tests/test_ioc_wiring.py` - Idunn wiring: bootstrap report, port injection, singletons, `reset()`, fake `runtime=`/`transformer=` seam
- `tests/test_architecture.py` - AST-walks `modgud/` and enforces the dependency table in `project.md` (with probe self-checks)

**IMPORTANT:** Functions decorated with `implicit_return=True` must be defined at module level (not inside test functions) because `inspect.getsource()` cannot extract source from nested functions. Use `tests/test_fixtures.py` for these cases.

**Key test scenarios**:
- Guard success / failure paths
- Each `GuardFailureEnum` (ERROR_RAISE / ERROR_RETURN / RETURN_VALUE / CALL_HANDLER) with and without a custom `on_failure`
- `continuance` budget: collecting multiple failures, ExceptionGroup shape, cascade-safety when a guard raises mid-window
- Implicit return with various constructs (if/else, try/except, match/case)
- Explicit return disallowed with implicit_return=True
- Missing else clause / empty block detection
- Nested function handling (nested functions can use explicit returns)
- Guard parameter handling (positional vs named)
- Metadata preservation (__name__, __doc__, __signature__, __annotations__)

## Architecture Notes

### Clean Architecture Principles

The layering is ports-and-adapters wired by Idunn:

1. **Ports and adapters**: the app decorators depend only on the `@Port` protocols in `modgud.domain.<feature>.ports`; the `@Adapter` classes in `modgud.infrastructure.adapters` (`GuardRuntime`, `ImplicitReturnTransformer`) are discovered by `Wiring.ensure()` and injected through `@Invert()`, so no decorator-specific logic leaks into infrastructure
2. **Immutability**: All transformed functions preserve original function metadata
3. **Functional Composition**: Guard functions are composable - they're pure functions returning True or error messages

### Import Examples

**Primary API:**

```python
from modgud.app import guarded_expression
from modgud.domain.guarded_expr import GuardClauseError, GuardFailureEnum
from modgud.infrastructure.common import CommonGuards


# Defaults: ERROR_RAISE, on_failure=GuardClauseError, continuance=0, implicit_return=True
@guarded_expression(CommonGuards.positive("x"))
def process(x):
  result = x * 2
  result  # implicit return


# Multiple guards, collect up to 3 failures total (1 + continuance=2)
@guarded_expression(
  CommonGuards.not_none("user"),
  CommonGuards.type_check(str, "name"),
  CommonGuards.positive("amount"),
  continuance=2,
)
def create_transaction(user, name, amount):
  Transaction(user, name, amount).id  # implicit return


# Return a fallback value instead of raising
@guarded_expression(
  CommonGuards.positive("x"),
  implicit_return=False,
  strategy=GuardFailureEnum.RETURN_VALUE,
  on_failure=None,
)
def calculate(x):
  return x * 2


# Custom handler that sees the full errors list
def explain(errors, *args, **kwargs):
  return {"errors": errors, "args": args}


@guarded_expression(
  CommonGuards.positive("x"),
  strategy=GuardFailureEnum.CALL_HANDLER,
  on_failure=explain,
)
def report(x):
  x * 2
```

### Error Hierarchy

All errors inherit from appropriate base classes:
- `GuardClauseError(Exception)` - Raised when guards fail (configurable)
- `ImplicitReturnError(SyntaxError)` - Base for transformation errors
  - `ExplicitReturnDisallowedError` - Explicit return found with implicit_return=True
  - `MissingImplicitReturnError` - Block doesn't produce a value
  - `UnsupportedConstructError` - Unsupported AST construct at tail position
