# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-10-28

### Added

- **Architecture Validation Tests** - Automated tests that enforce LPA compliance (`tests/general/test_architecture.py`):
  - Verifies surface layer never imports directly from domain (must use infrastructure gateway)
  - Enforces naming conventions (Adapter, Service, Port, Model suffixes)
  - Validates one public class per file rule (private helper classes allowed)
  - Ensures proper layer dependency flow (Surface → Infrastructure → Domain)
  - Confirms infrastructure gateway properly re-exports domain types/errors

- **Test Suite Reorganization** - Tests reorganized by architectural layer:
  - `tests/infrastructure/` - Infrastructure layer tests (7 files, 22 tests)
  - `tests/surface/` - Surface layer tests (6 files, 21 tests)
  - `tests/integration/` - Integration tests (8 files, 26 tests)
  - `tests/general/` - Multi-layer tests (9 files, 30 tests including architecture validation)
  - Each test class extracted to its own file (30 total test files, one class per file)

### Removed

- **BREAKING**: Removed all backward compatibility aliases (clean architecture prioritized over legacy support):
  - Removed `ErrorMessages` alias (use `ErrorMessagesModel` directly)
  - Removed `InfoMessages` alias (use `InfoMessagesModel` directly)
  - No deprecation warnings - clean break for simplicity

### Changed

- Test organization now mirrors LPA architecture for better discoverability
- Updated documentation to reflect v2.1.0 architecture improvements

---

## [2.0.0] - 2025-10-28

### BREAKING CHANGES

**Architecture refactoring to strict LPA (Layered Ports Architecture) compliance**

This release refactors the internal architecture while preserving the public API. Users importing from `modgud` package root will see **no breaking changes**. Advanced users importing from internal modules will need to update import paths.

#### Internal Architecture Changes

**Renamed Classes:**
- `DefaultGuardChecker` → `GuardCheckerAdapter`
- `DefaultAstTransformer` → `AstTransformerAdapter`
- `ErrorMessages` → `ErrorMessagesModel`
- `InfoMessages` → `InfoMessagesModel`

**Renamed Files:**
- `infrastructure/adapters/guard_checker.py` → `guard_checker_adapter.py`
- `infrastructure/adapters/ast_transformer.py` → `ast_transformer_adapter.py`

**Directory Restructure:**
- Domain models moved to `domain/models/` subpackage:
  - `domain/errors.py` → `domain/models/errors.py`
  - `domain/types.py` → `domain/models/types.py`
  - `domain/messages.py` extracted to separate model files:
    - `domain/models/error_messages_model.py` (ErrorMessagesModel)
    - `domain/models/info_messages_model.py` (InfoMessagesModel)
- Removed empty `__init__.py` files from `ports/`, `services/`, `adapters/` subdirectories
- Test helpers consolidated in `tests/helpers/` package

### Added

- `ErrorMessagesModel` - new name for ErrorMessages class
- `InfoMessagesModel` - new name for InfoMessages class
- `GuardCheckerAdapter` - renamed from DefaultGuardChecker (follows LPA naming)
- `AstTransformerAdapter` - renamed from DefaultAstTransformer (follows LPA naming)
- Improved layer isolation and testability through strict LPA architecture
- Test helpers package with unified imports

### Changed

- **Internal structure only** - public API unchanged
- Domain models organized in `models/` subpackage
- Infrastructure adapters follow "Adapter" suffix naming convention
- Direct imports from subpackages now required (no package-level `__init__.py` re-exports in subdirectories)

### Migration Guide

#### For Public API Users (99% of users) - NO CHANGES REQUIRED

All existing code continues to work unchanged:

```python
# ✅ All existing imports work:
from modgud import guarded_expression, CommonGuards
from modgud import positive, not_none, type_check
from modgud import GuardClauseError, ImplicitReturnError
```

#### For Advanced Users (internal module imports) - UPDATE REQUIRED

If you import from internal modules, update import paths:

**Domain Layer:**
```python
# OLD:
from modgud.domain.errors import GuardClauseError
from modgud.domain.types import GuardFunction
from modgud.domain.messages import ErrorMessages

# NEW:
from modgud.domain.models.errors import GuardClauseError
from modgud.domain.models.types import GuardFunction
from modgud.domain.models.error_messages_model import ErrorMessagesModel
```

**Infrastructure Layer:**
```python
# OLD:
from modgud.infrastructure.adapters import DefaultGuardChecker
from modgud.infrastructure.adapters import DefaultAstTransformer

# NEW:
from modgud.infrastructure.adapters.guard_checker_adapter import GuardCheckerAdapter
from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter
```

**Test Utilities:**
```python
# OLD:
from tests.test_fixtures import calculate, classify
from tests.helpers import assert_guard_fails

# NEW:
from tests.helpers import calculate, classify, assert_guard_fails
```

### Architecture Benefits

- **Full LPA compliance** with models/, ports/, services/, adapters/ organization
- **Strict naming conventions** - Port, Adapter, Service, Model suffixes
- **Layer isolation** maintained with infrastructure gateway pattern
- **One class per file** (except errors.py, types.py)
- **Improved testability** through port-based dependency injection
- **Cleaner imports** without nested package re-exports

### Next Steps

See `/Users/windfox/plans/modgud/lpa-refactoring-plan.md` for complete architectural documentation.

---

## [1.1.2] - 2025-10-27

Prior releases documented elsewhere. See git history for details.
