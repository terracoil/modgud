**Parent**: [📋 ADR Index](README.md) | [📖 ADR-001](ADR-001-implicit-return-transformation-approach.md) | [📖 ADR-003](ADR-003-registry-system-architecture.md)

# ADR-002: Guard Pattern Design Rationale

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2025-10-26)

> **Update 2026-11-02.** One addition to the contract, decided while making methods work (ADR-004 era, plan decision S3): when the decorated callable is a method (defined in a class body, first positional parameter named `self` or `cls`), guards receive the call's arguments **without** the receiver, so `positive('x')` on `def m(self, x)` checks `x`. `CALL_HANDLER` handlers still get everything. The rule is stated on `GuardPort.wrap_function`, so a custom `runtime=` is expected to honour it. Detection is by name and defining scope, not by descriptor type: a `@staticmethod` whose first parameter is called `cls` has its first argument skipped too.

## Context
A validator that returns `False` has told you something went wrong and nothing else, which is also what a toddler does. Guard clauses need a consistent pattern for expressing validation success/failure. Traditional approaches use boolean returns with separate error handling, making guard functions less composable and requiring additional context for error messages.

## Decision
Guard functions return `True` for success or a string error message for failure. This pattern enables:
- Self-describing failures without external error mappings
- Composable guards that carry their own context
- Natural Python truthiness evaluation (`if guard_result is not True`)
- Direct error message propagation to exceptions or logs

Guard signature: `Callable[..., Union[Literal[True], str]]`

## Consequences

### Positive
- **Self-contained**: Each guard carries its own failure context
- **Composable**: Guards can be chained without losing error information
- **Pythonic**: rides on Python's truthiness instead of inventing a result type
- **Readable**: Error messages defined at validation point, not elsewhere
- **Flexible**: Same guard works with exceptions, logging, or return values

### Negative
- **Type ambiguity**: a `bool | str` return means a runtime check at every guard
- **String coupling**: Error messages are strings, not structured data
- **Truthy pitfall**: compare with `is not True`; `if not result` waves error strings through
- **No metadata**: Can't attach additional context beyond error string

## Alternatives Considered

### 1. Boolean with Separate Errors
Guards return `bool`, errors in separate dictionary/mapping.
```python
def positive(x): return x > 0  # Where does error come from?
```
- **Rejected**: Requires external error mapping, less composable

### 2. Exception Raising
Guards raise exceptions directly on failure.
```python
def positive(x):
  if x <= 0: raise ValueError("Must be positive")
```
- **Rejected**: Can't compose with non-exception failure modes, forces exception handling

### 3. Result/Either Monad
Return `Result[None, Error]` or similar monadic type.
```python
def positive(x):
  return Ok(None) if x > 0 else ErrResult("Must be positive")
```
- **Rejected**: Adds dependency, verbose for simple validations

### 4. Validation Objects
Return validation result objects with status and message.
```python
def positive(x):
  return ValidationResult(x > 0, "Must be positive")
```
- **Rejected**: Heavyweight for simple guards, additional abstraction

## Implementation Notes

Guards must ALWAYS return exactly `True` (not truthy values) or a string:
```python
# CORRECT
return True  # Explicit True
return "Error message"  # String message

# INCORRECT
return 1  # Truthy but not True
return None  # Falsy but not string
return False  # Should return error string instead
```

## References
- Railway-oriented programming patterns
- Erlang guard sequences
- Design by Contract (DbC) principles
