# ADR-001: Implicit Return Transformation Approach

## Status
Accepted (2025-10-26)

## Context
Python requires explicit return statements, unlike Ruby which returns the last evaluated expression. This creates verbose code with unnecessary return statements when implementing expression-oriented programming patterns. We needed a way to enable Ruby-style implicit returns while maintaining Python semantics and debugging capabilities.

## Decision
We chose AST (Abstract Syntax Tree) transformation at decoration time to convert implicit returns into explicit return statements. The transformation:
1. Extracts function source code using `inspect.getsource()`
2. Parses into AST and strips decorators to prevent re-application
3. Transforms tail position expressions to assign to `__implicit_result` variable
4. Appends single `return __implicit_result` statement
5. Compiles and executes transformed AST in original function's scope

## Consequences

### Positive
- **Zero runtime overhead**: Transformation happens once at decoration time, not per-call
- **Full Python compatibility**: Generated code is standard Python with explicit returns
- **Debugging friendly**: Stack traces show transformed code with clear return points
- **Clean syntax**: Users write natural expression-oriented code without return statements
- **Composable**: Works with guard clauses and other decorators through wrapper pattern

### Negative
- **Module-level only**: Functions must be defined at module level (not nested) due to `inspect.getsource()` limitations
- **Source dependency**: Requires access to source code, won't work with compiled .pyc files
- **Complexity**: AST transformation adds implementation complexity
- **Error messages**: Syntax errors reference transformed code, not original

## Alternatives Considered

### 1. Runtime Bytecode Manipulation
Modify bytecode to inject RETURN_VALUE instructions at runtime.
- **Rejected**: Platform-specific, fragile across Python versions, poor debugging

### 2. Exec/Eval with String Manipulation
Parse source as strings and inject return statements via regex.
- **Rejected**: Error-prone, poor handling of edge cases, security concerns

### 3. Context Manager with Exception
Use exception raising to simulate returns from context manager.
- **Rejected**: Performance overhead, unnatural syntax, debugging nightmare

### 4. Metaclass Magic
Use metaclasses to transform methods at class creation time.
- **Rejected**: Only works for methods not functions, adds metaclass complexity

## References
- Python AST documentation: https://docs.python.org/3/library/ast.html
- Ruby implicit return semantics
- Similar projects: MacroPy, Coconut language