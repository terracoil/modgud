# modgud Architecture Diagrams

## Package Dependencies

The package dependency diagram shows the layered architecture of the modgud library:

![Package Dependencies](diagram.dependency.package.png)

### Architecture Layers

1. **API Layer** (`modgud/__init__.py`)
   - Public interface for the library
   - Exports main decorator and error classes
   - Depends on both Implementation and Shared layers

2. **Implementation Layer** (`guarded_expression/`)
   - Core decorator implementation
   - Contains:
     - `decorator.py` - Main guarded_expression decorator class
     - `ast_transform.py` - Pure AST transformation for implicit returns
     - `guard_runtime.py` - Pure guard checking and failure handling
     - `common_guards.py` - Pre-built guard factory methods
   - Depends on Shared layer for types and errors

3. **Shared Infrastructure Layer** (`shared/`)
   - Common types and error definitions
   - Contains:
     - `types.py` - Type definitions (GuardFunction, FailureBehavior)
     - `errors.py` - All exception classes
   - No dependencies (foundation layer)

### Clean Architecture Principles

The architecture follows clean architecture principles:
- **Dependency Rule**: Dependencies only point inward (API → Implementation → Shared)
- **No circular dependencies**: Clear unidirectional flow
- **Pure functions**: Core logic in ast_transform and guard_runtime are pure functions
- **Dependency injection**: Decorator composes pure functions rather than creating dependencies