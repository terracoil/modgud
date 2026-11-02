**Parent**: [📋 ADR Index](README.md) | [📚 Documentation Hub](../README.md) | [📖 ADR-002](ADR-002-guard-pattern-design-rationale.md)

# ADR-001: Implicit Return Transformation Approach

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2025-10-26)

> **Update 2026-11-02.** The "module-level only" consequence below was too broad. The real constraint is that the source must be on disk and the body is re-compiled at module scope: closures over enclosing locals are lost, and a REPL or `exec` has no source to read. Methods work (instance, static, class, async); they are re-compiled inside stand-in classes named from `__qualname__` so private-name mangling survives. Zero-argument `super()` and class-scope defaults are refused at decoration time with `UnsupportedConstructError`.

## Context
Python is a statement language that keeps asking to be an expression language. It requires explicit return statements, unlike Ruby which returns the last evaluated expression. This creates verbose code with unnecessary return statements when implementing expression-oriented programming patterns. We needed a way to enable Ruby-style implicit returns while maintaining Python semantics and debugging capabilities.

## Decision
We chose AST (Abstract Syntax Tree) transformation at decoration time to convert implicit returns into explicit return statements. The transformation:
1. Extracts function source code using `inspect.getsource()`
2. Parses into AST and strips decorators to prevent re-application
3. Transforms tail position expressions to assign to `__implicit_result` variable
4. Appends single `return __implicit_result` statement
5. Compiles and executes transformed AST in original function's scope

## Consequences

### Positive
- **No per-call cost**: the rewrite runs once, at decoration; the call pays for a `return` it would have paid anyway
- **Full Python compatibility**: Generated code is standard Python with explicit returns
- **Debuggable**: stack traces show ordinary code with one return in it
- **Clean syntax**: Users write natural expression-oriented code without return statements
- **Composable**: Works with guard clauses and other decorators through wrapper pattern

### Negative
- **Source on disk**: the body is re-compiled at module scope. Closures over enclosing locals are lost; a REPL, `exec` or a `.pyc`-only install has nothing to read.
- **Complexity**: an AST rewrite is more code than a `return` statement. That is the trade.
- **Error messages**: syntax errors point at the rewritten code, not the file the author wrote.

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