# ADR-002: Guard Pattern Design Rationale

## Status
Accepted (2025-10-26)

## Context
Guard clauses need a consistent pattern for expressing validation success/failure. Traditional approaches use boolean returns with separate error handling, making guard functions less composable and requiring additional context for error messages.

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
- **Pythonic**: Leverages Python's truthiness and type flexibility
- **Readable**: Error messages defined at validation point, not elsewhere
- **Flexible**: Same guard works with exceptions, logging, or return values

### Negative
- **Type ambiguity**: Mixed return types require runtime type checking
- **String coupling**: Error messages are strings, not structured data
- **Truthy pitfall**: Must use `is not True` not just `if not result`
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
  return Ok(None) if x > 0 else Err("Must be positive")
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