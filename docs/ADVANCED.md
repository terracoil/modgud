# modgud docs

**Parent**: [Main README](../README.md)

Each topic has one home. This page says which one, and where to start. An earlier version of this page tried to be every home at once and ran past five thousand words.

## 📚 What each document is for

- [README](../README.md): install, the quick start, a tour of the features, and the three limitations most people hit first.
- [API reference](api-reference.md): what to import, every signature and parameter table, the [`GuardFailureEnum`](api-reference.md#guardfailureenum) × `on_failure` table, the [`Guards`](api-reference.md#guards) and [`GuardRegistry`](api-reference.md#guardregistry) catalogues, the [implicit-return rules](api-reference.md#implicit_return), [method support](api-reference.md#methods) and the [integration seam](api-reference.md#integration-seam).
- [How it works](how-it-works.md): the layers, the Idunn wiring, the guard pipeline, the AST rewrite, [thread safety](how-it-works.md#thread-safety) and the full list of [limitations](how-it-works.md#limitations).
- [Class catalog](classes.md): every class in the package and the examples, what it is for, and which tier it belongs to.
- [Examples](../examples/README.md): runnable files in two trees, `free_range/` for module-level functions and `classy/` for methods.
- [project.md](../project.md): the package tree, the API tiers, and the dependency table the architecture test enforces.
- [ADRs](adr/README.md): why the big decisions went the way they did, and what each one cost.
- [CONTRIBUTING](../CONTRIBUTING.md): setup, the lint gate, and what the tests check.

## 🧭 Reading order

**First-time user.** The [README](../README.md), then the first four files in [`examples/free_range/`](../examples/free_range/), then the [API reference](api-reference.md) when you need a parameter.

**Integrator** (a custom runtime, a test fake, an existing Idunn container). The [integration seam](api-reference.md#integration-seam), then [How it works](how-it-works.md), then example `12_swapping_the_runtime.py`.

**Contributor.** [CONTRIBUTING](../CONTRIBUTING.md), then [project.md](../project.md), then [How it works](how-it-works.md) and the [ADRs](adr/README.md).

## 📜 API tiers

`from modgud import ...` is the public API: 13 names. The ports behind the integration seam are importable too but documented separately, and everything deeper is internal; [project.md](../project.md) has the tier table.

## 🧩 Expression forms, past the basics

The [README](../README.md#-feature-tour) shows the simplest use of `eop_cond`, `eop_case` and `eop_match`, and the [API reference](api-reference.md#-expression-forms) has their signatures. This section holds everything else: the pattern language, the rules borrowed from Elixir, where a form may appear, what it refuses, and how it types. The runnable originals are `examples/free_range/13_eop_cond.py` to `15_eop_match.py` and their `classy/` twins.

### The pattern language

A pattern is an ordinary expression that the rewrite reads as a pattern. This is the whole supported set.

| Written | Means | Becomes |
|---|---|---|
| `eop_var.name` | capture into `name` | a capture |
| `eop_var._` | match anything | `_` |
| `0`, `'text'`, `-1`, `None`, `True` | that literal | a literal or singleton pattern |
| `Color.RED` | equal to that dotted name | a value pattern |
| `limit` | equal to the value of that bare name | a capture plus an `==` test |
| `Point(0, eop_var.y)`, `Point(x=0, y=eop_var.y)` | an instance with those parts | a class pattern |
| `[first, eop_var.second]`, `(a, *eop_var.rest)` | a sequence, with at most one star | a sequence pattern |
| `{'key': eop_var.value, **eop_var.rest}` | a mapping with those keys | a mapping pattern |
| `eop_when(pattern, guard)` | the pattern, when the guard is exactly `True` | a pattern and a guard |

Four rules keep it predictable:

- **A call in pattern position is always a class pattern**, as in Python's `match`. Bind a computed value to a name first and use the bare name.
- **A bare name compares by value.** `eop_clause(limit, ...)` matches when the subject equals `limit`.
- **A class pattern must also be a valid constructor call**, because mypy reads it as one. `Point(x=0)` fails the type check when `y` is required; write `Point(0, eop_var._)`.
- **`eop_when` goes only at the top** of a clause test or of an `eop_match` pattern.

Not offered: `as` patterns, and alternatives such as `A | B`. Elixir has no alternatives either; write one clause per alternative. Anything else in pattern position raises `MarkerUsageError` at decoration.

Matching itself is Python's, because the forms lower to a real `match`: `1` matches `1.0` and `True`, a list pattern matches a tuple, and `str` and `bytes` are never sequences.

### Elixir's truth rule in `eop_cond`

An `eop_cond` test is true unless it is `None` or `False`. That is Elixir's rule, and it differs from `if`:

```python
eop_cond(eop_clause([], 'has items'), default='empty')   # -> 'has items'
eop_cond(eop_clause(0, 'nonzero'), default='zero')       # -> 'nonzero'
eop_cond(eop_clause(None, 'set'), default='unset')       # -> 'unset'
```

Comparisons, which are nearly every test, behave the same either way. When a test is a value rather than a comparison, say what you mean: `eop_clause(len(items) > 0, ...)`.

### Guards, and what happens when one raises

`eop_when(pattern, guard)` adds a guard to a pattern. Two rules come from Elixir:

- **A guard passes only when it is exactly `True`.** A non-empty list, `1` or any other truthy value does not pass.
- **A guard that raises counts as no match**, and the next clause is tried.

The second rule has a cost in Python that it does not have in Elixir, where guards are limited to a short list of safe functions. Here a guard is any expression, so a mistake inside one falls through silently:

```python
eop_case(
  point,
  eop_clause(eop_when(Point(eop_var.x, eop_var.y), eop_var.x > limt), 'right of the limit'),  # typo
  default='left of the limit',
)
# -> always 'left of the limit': the NameError inside the guard is a non-match, not an error
```

Keep guards to simple comparisons on captures and well-known names, and let the tests cover the clause that the guard selects. A guard may not contain `await`, `yield` or `:=`; each is refused at decoration, because the guard runs inside a generated function.

### Where a form may appear

A form is an expression, so it fits anywhere one goes: a tail, an assignment, a comprehension element or filter, a lambda body, a `while` test, a call argument, an operand. Two lowerings are used:

- When `eop_case` is the whole value of an assignment or an expression statement, it becomes a real `match` statement placed just before, at native speed.
- Anywhere else, each clause becomes a small generated function and the call becomes a chain of conditional expressions. `eop_match` always uses a generated function, and `eop_cond` always lowers in place.

A nested form inside a clause value or a subject is lowered first. A capture is visible only in its own clause's guard and value, never in `default` and never in another clause.

Both decorators lower the forms, in both modes. With `implicit_return=False` a function that uses no form is left exactly as it was, with no source read.

### What is refused at decoration

| Refused | Error |
|---|---|
| a missing `default=`, an unknown keyword, zero clauses, no subject | `MarkerUsageError` |
| a clause that is not a literal `eop_clause(...)` call, including `*clauses` or a variable | `MarkerUsageError` |
| a pattern outside the table above, a capture bound twice, two stars, a bare name as a mapping key | `MarkerUsageError` |
| `await`, `yield` or `:=` inside a guard | `MarkerUsageError` |
| `eop_var.name` outside the clause whose pattern binds it; `eop_clause` or `eop_when` outside a form; a marker referenced but not called | `MarkerUsageError` |
| a guard or bare-name pattern that reads a comprehension variable or lambda parameter, in the generated-function path | `MarkerPlacementError` |
| `eop_cond`, or `eop_case` in the generated-function path, inside a comprehension's first iterable | `MarkerPlacementError` |
| any form inside a class body nested in the decorated function | `MarkerPlacementError` |

And at call time: a form outside any modgud decorator raises `MarkerNotRewrittenError`, whose `.name` says which form. `eop_var.name` raises the same, so a stray capture never evaluates to a placeholder. Dunder lookups on `eop_var` raise `AttributeError`, so `hasattr` and `inspect` keep working.

### Typing

- `eop_cond` and `eop_case` have one generic signature each: `*clauses: eop_clause[T], default: D` returning `T | D`. Clauses of one value type infer precisely, and so does a different `default` type, so `str` clauses with `default=None` give `str | None`. Clauses of mixed types give `object` under mypy; `cast` or widen when that happens.
- Captured values are typed `Any`, so a clause value built from a capture has type `Any`.
- `eop_match` returns `bool` and does no narrowing.
- A missing `default=` is reported by mypy before the decorator ever runs.

### Aliases, modules and fakes

The rewrite recognises a form by the object a name refers to, not by its spelling. `from modgud import eop_cond as cond` and `modgud.eop_cond(...)` both work, and your own function called `eop_cond` is left alone. A name bound inside the decorated function is never a marker.

Each form is lowered by an adapter behind the `EopPort` protocol, chosen by its `EopFormEnum` key. Pass `eop_cond_port=`, `eop_case_port=` or `eop_match_port=` to either decorator to substitute one; `lower(call, *, hoistable, fresh)` returns the statements to hoist and the replacement expression, and `refuse()` raises for a plain call. See the [integration seam](api-reference.md#integration-seam).
