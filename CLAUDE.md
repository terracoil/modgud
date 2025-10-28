# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `modgud`, a Python library that provides guard clause decorators for implementing validation checks at function entry points. The library enforces single return point architecture and supports various failure behaviors including custom return values, exception raising, and handler functions.

**IMPORTANT: This is a NEW project with NO existing users. No backward compatibility requirements. Breaking changes are acceptable. Clean, simple architecture is prioritized over legacy support.**

**Core Architecture (v0.4.0 - LPA):**
- **Primary API**: `guarded_expression` - unified decorator combining guard validation + implicit returns
- **Implicit return by default**: `implicit_return=True` enables Ruby-style expression-oriented code
- **GuardClauseError by default**: `on_error=GuardClauseError` raises exception on guard failure
- **Failure handling**: Configurable via `on_error` parameter (exception classes, custom values, callables)
- **Pre-built guards**: `CommonGuards` class provides standard validation patterns (not_none, positive, type_check, etc.)
- **Layered Ports Architecture (LPA)**: Ports at every layer boundary (Domain↔Infrastructure and Infrastructure↔Application)
- **Strict Layer Isolation**: Application imports ONLY from Infrastructure gateway, never from Domain
- **NO LEGACY SUPPORT NEEDED**: Old `guard_clause` and `implicit_return` packages should be removed, not maintained as wrappers

## Development Commands

**IMPORTANT: Always use `poetry run` prefix** - This is a Poetry project. ALWAYS use `poetry run` before commands like `pytest`, `ruff`, `mypy`, etc. Do NOT use `.venv/bin/` paths directly.

### 🚨 MANDATORY LINTING REQUIREMENT 🚨

**CRITICAL**: You MUST run `bin/devtools build lint --fix` BEFORE:
- Making ANY code changes
- Performing code reviews
- Starting refactoring work.  If there are linting and/or mypy typing issues found, fix those first before refactoring.  
- Committing changes
- Creating pull requests

This command runs:
1. **Ruff linting** - catches code quality issues
2. **Ruff formatting** - ensures consistent code style
3. **MyPy type checking** - validates type annotations with strict settings

**FAILURE TO RUN LINTING = INVALID CODE SUBMISSION**

The `--fix` flag automatically corrects fixable issues. If linting fails after auto-fix, you MUST resolve all errors before proceeding. No exceptions.

### Package Management
**This is a Poetry project** - use Poetry for all dependency management:

```bash
# Install dependencies (Python 3.13+ required)
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

### Core Module Structure (v0.4.0 - LPA)

modgud follows a 3-layer Layered Ports Architecture (LPA) with ports at every layer boundary for maximum flexibility and testability.

**Layer 1 - Domain (Innermost):**
- `modgud/domain/` - Core types, errors, messages, and port definitions
  - `types.py` - Type definitions (`GuardFunction`, `FailureBehavior`)
  - `errors.py` - All exception classes (`GuardClauseError`, `ImplicitReturnError`, etc.)
  - `messages.py` - Error message constants and info messages
  - `ports/` - Port interfaces that Infrastructure must implement
    - `guard_checker_port.py` - `GuardCheckerPort` interface
    - `ast_transformer_port.py` - `AstTransformerPort` interface

**Layer 2 - Infrastructure (Middle):**
- `modgud/infrastructure/` - System boundaries, services, and adapters
  - `ports/` - Port interfaces that Surface uses
    - `guard_service_port.py` - `GuardServicePort` interface
    - `transform_service_port.py` - `TransformServicePort` interface
    - `validation_service_port.py` - `ValidationServicePort` interface
  - `services/` - Service implementations (implement infrastructure ports)
    - `guard_service.py` - Guard validation service
    - `transform_service.py` - AST transformation service
    - `validation_service.py` - Validation orchestration service
  - `adapters/` - Low-level implementations (implement domain ports)
    - `guard_checker.py` - Guard checking adapter (implements `GuardCheckerPort`)
    - `ast_transformer.py` - AST transformation adapter (implements `AstTransformerPort`)
  - `__init__.py` - **Infrastructure Gateway** - Re-exports domain types/errors for Surface

**Layer 3 - Surface (Outermost):**
- `modgud/surface/` - Public API and decorator orchestration
  - `decorator.py` - Main `guarded_expression` decorator (uses infrastructure service ports)
  - `validators.py` - Pre-built guard factories (`CommonGuards` class)
  - `registry.py` - Custom guard registration (`GuardRegistry` class)

**Public API Exports:**
- `modgud/__init__.py` - Primary exports (`guarded_expression`, `CommonGuards`, error classes)

### Key Design Patterns

**Single Return Point**: All decorated functions maintain single return semantics:
- With `implicit_return=True` (default): Last expression in each branch is auto-returned (no explicit `return` allowed)
- With `implicit_return=False`: Explicit `return` statement must be last line, not contained in any block
- Guard clauses handle early exits by returning from decorator wrapper

**Guard Function Signature**: Guards are callables that accept `(*args, **kwargs)` and return either `True` (pass) or a string error message (fail).

**Failure Behavior Chain**:
1. Guard evaluates to non-True value
2. Optional logging occurs if `log=True`
3. Failure handling via `on_error` parameter:
   - Exception class → instantiate and raise
   - Callable → invoke with `(error_msg, *args, **kwargs)`, return value used
   - Any other value → return directly

**Implicit Return Transformation** (when `implicit_return=True`):
1. Function source code extracted via `inspect.getsource()`
2. AST parsed and decorators stripped to prevent re-application
3. Tail position expressions transformed to assign to hidden `__implicit_result` variable
4. Single `return __implicit_result` appended
5. Transformed AST compiled and exec'd in original function's global scope
6. Resulting function wrapped with guard checking logic

### Configuration Files

**ruff.toml**: Standalone ruff configuration
- Targets Python 3.13
- 2-space indentation, 100-character line length
- Single quote style for consistency
- Includes `modgud/` and `tests/` directories

**pyproject.toml**: Project metadata and tool configuration
- Uses PEP 621 project format with Poetry dependencies
- pytest configured for `tests/` directory with coverage for `modgud/`
- mypy configured with reports output to `reports/mypy/`
- Requires Python >=3.13

## Testing Strategy

Tests should be placed in `tests/` directory following pytest conventions (`test_*.py` or `*_test.py`). The library uses extensive examples in `modgud/README.md` which can guide test case development.

**Test Files:**
- `tests/test_guarded_expression.py` - Integration tests for the main decorator (30+ tests)
- `tests/test_ast_transform.py` - Unit tests for AST transformation logic
- `tests/test_guard_runtime.py` - Unit tests for guard checking and failure handling
- `tests/test_fixtures.py` - Module-level test fixtures for implicit return tests

**IMPORTANT:** Functions decorated with `implicit_return=True` must be defined at module level (not inside test functions) because `inspect.getsource()` cannot extract source from nested functions. Use `tests/test_fixtures.py` for these cases.

**Key test scenarios**:
- Guard success/failure paths
- Different `on_error` behaviors (None, values, callables, exceptions, GuardClauseError)
- Implicit return with various constructs (if/else, try/except, match/case)
- Explicit return disallowed with implicit_return=True
- Missing else clause detection
- Empty block detection
- Nested function handling (nested functions can use explicit returns)
- Logging functionality
- Guard parameter handling (positional vs named)
- Metadata preservation (__name__, __doc__, __signature__, __annotations__)

## Architecture Notes

### LPA Architecture Principles

The v0.4.0 architecture implements Layered Ports Architecture (LPA) with ports at every layer boundary:

1. **Port Layers**:
   - Domain defines ports for Infrastructure adapters (`GuardCheckerPort`, `AstTransformerPort`)
   - Infrastructure defines ports for Surface services (`GuardServicePort`, `TransformServicePort`, `ValidationServicePort`)
2. **Inner Layer Owns Ports**: Following Dependency Inversion Principle, inner layers define ports that outer layers implement
3. **Strict Layer Isolation**: Surface NEVER imports from Domain directly - all imports go through Infrastructure gateway
4. **Service Layer Pattern**: High-level abstractions (`GuardService`, `TransformService`) simplify Surface code
5. **Adapter Pattern**: Low-level implementations in `infrastructure/adapters/` implement domain ports
6. **Infrastructure Gateway**: `infrastructure/__init__.py` controls access and re-exports domain types/errors for Surface
7. **Dependency Injection**: Services accept optional port implementations via constructor, defaulting to concrete implementations
8. **Layered Dependencies**: Dependencies flow strictly inward (Surface → Infrastructure → Domain)
9. **Testability**: Port interfaces at every boundary enable comprehensive mocking and isolated testing
10. **Flexibility**: Can swap implementations at any boundary without modifying dependent layers

### Import Examples

**Primary API:**
```python
from modgud import guarded_expression, CommonGuards, GuardClauseError

# With guards and implicit return (default behavior)
@guarded_expression(
    CommonGuards.positive("x"),
    implicit_return=True,  # default
    on_error=GuardClauseError  # default
)
def process(x):
    result = x * 2
    result  # implicit return

# Multiple guards with different validators
@guarded_expression(
    CommonGuards.not_none("user"),
    CommonGuards.type_check(str, "name"),
    CommonGuards.positive("amount")
)
def create_transaction(user, name, amount):
    transaction = Transaction(user, name, amount)
    transaction.id

# Guards only, explicit return
@guarded_expression(
    CommonGuards.positive("x"),
    implicit_return=False,
    on_error=None
)
def calculate(x):
    return x * 2

# Implicit return only, no guards
@guarded_expression()
def compute(x):
    result = x * 2
    result  # implicit return

# Using infrastructure services directly (advanced usage)
from modgud.infrastructure import GuardService, TransformService

guard_service = GuardService()
transform_service = TransformService()

@guarded_expression(
    CommonGuards.not_none("x"),
    guard_service=guard_service,
    transform_service=transform_service
)
def advanced_function(x):
    x * 2
```

### Error Hierarchy

All errors inherit from appropriate base classes:
- `GuardClauseError(Exception)` - Raised when guards fail (configurable)
- `ImplicitReturnError(SyntaxError)` - Base for transformation errors
  - `ExplicitReturnDisallowedError` - Explicit return found with implicit_return=True
  - `MissingImplicitReturnError` - Block doesn't produce a value
  - `UnsupportedConstructError` - Unsupported AST construct at tail position
