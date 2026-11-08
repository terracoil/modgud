**Parent**: [📋 ADR Index](README.md) | [📖 ADR-005](ADR-005-idunn-ports-and-adapters.md) | [📚 Documentation Hub](../ADVANCED.md)

# ADR-006: Elixir Expression Forms

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

## Status
Accepted (2026-11-06)

## Context
modgud already turns the tail of a function into its value. Two things still forced a statement where the rest of the body was expressions: an ordered chain of conditions, which Python only offers as nested ternaries, and structural matching, which Python only offers as the `match` statement. Elixir has both as expressions, `cond` and `case`, plus `match?` for a boolean test. The research behind this record (in the plans folder, "Expression oriented Elixir forms for modgud") showed that a source rewriter can deliver all three on Python 3.11 to 3.14, and that the real constraints are what mypy, pyright and ruff can see, not what the interpreter can run.

## Decision
Three forms, `eop_cond`, `eop_case` and `eop_match`, with the vocabulary `eop_clause`, `eop_when` and `eop_var`. Each is a typed marker object whose calls the implicit-return rewrite compiles away. The decisions, taken one at a time:

1. **Names are `eop_` plus the Elixir name.** `eop_match` stands for `match?`, which Python cannot spell. Standalone names rather than an `EOP` class, because `EOP.with` would be a `SyntaxError` for the form that comes next, and because a bare `match` or `case` is shadowed by ordinary code.
2. **A pattern is written as an expression with a capture object:** `Point(0, eop_var.y)`. It is the only expression spelling that passes mypy, pyright and ruff, and it keeps class names visible to tools. The cost is that a class pattern must also be a valid constructor call, so a partial pattern needs `eop_var._` for each remaining field.
3. **Two lowerings for `eop_case`, both a real `match`.** A hoisted `match` statement where the call is a whole statement's value, at native speed; a generated matcher function per clause everywhere else, so the form works in comprehensions, lambdas and operands. The matching semantics are therefore Python's, and the test suite checks both against handwritten `match` statements.
4. **`default=` is mandatory** on `eop_cond` and `eop_case`. It is the only exhaustiveness rule a type checker enforces, and it matches the existing rule that a tail `match` must end in `case _:`. Elixir raises instead.
5. **A form outside a decorated function refuses** with `MarkerNotRewrittenError`, through its port. Every form has one meaning everywhere; there is no eager fallback.
6. **Guards are `eop_when(pattern, guard)`**, Elixir's own word and position, the same in `eop_case` and `eop_match`.
7. **One generic signature per form.** Mixed clause types give `object` under mypy; overloads can be added later without touching call sites.
8. **`eop_clause(test, value)` is a lowercase frozen dataclass**, Elixir's word for a branch, in the style of the forms it belongs to.
9. **Follow Elixir where it is free, Python where Elixir's rule would need a hand-written matcher.** Elixir: `eop_match(pattern, value)` argument order, only `None` and `False` are false in `eop_cond`, a guard passes only when exactly `True`, a guard that raises counts as no match, captures are private to their clause, no `A | B` alternatives. Python: `1` matches `1.0`, a list pattern matches a tuple.
10. **Architecture.** One `EopPort` in `modgud.domain.ports` with `lower` and `refuse`; one adapter per form in `modgud.infrastructure.adapters`, chosen by its `EopFormEnum` key; the shared pattern engine in `modgud.infrastructure.ast`. The two decorators receive the three form ports through their existing `@Invert` constructor and pass them to the transformer as `forms`, the same way `guarded_expression` already passes `imp_return_port`. `@Invert` stays in `app`. The markers carry their form in `__modgud_eop_form__`, so the resolver recognises them without `infrastructure` importing `app`.
11. **Both modes lower the forms.** With `implicit_return=False` the transformer lowers the forms and keeps the explicit `return`; a function with no form is returned untouched, decided from its code object without reading source.
12. **Two decoration-time errors**, `MarkerUsageError` for a malformed form and `MarkerPlacementError` for a misplaced one, both children of `ImplicitReturnError`.

## Consequences
- The public API grows from 13 names to 23. `modgud.domain` has 14 and `modgud.app` 9.
- `ImplicitReturnPort.transform`, `ImplicitReturnPort.transform_function` and `GuardPort.transform` gain a `forms` keyword, and `transform_function` a mode flag. A hand-written fake must accept them.
- The raising-guard rule has a cost Elixir does not pay, because Elixir limits guards to safe functions. A typo inside a Python guard falls through to `default` silently. It is documented in the `eop_when` docstring and in the docs hub, with the advice to keep guards to simple comparisons.
- Elixir's truth rule means `eop_clause([], ...)` is true. It is documented beside every example and in the `eop_cond` docstring.
- `EopPort` is the one domain port that speaks `ast` types. The architecture test permits the standard library everywhere, and the alternative would have left the lowering outside any port.
- Captures are typed `Any`, and no form narrows.

## Alternatives Considered
1. **An `EOP` namespace class.** Rejected: `EOP.with` cannot be spelled, a bound classmethod is a new object on every access, and it saves nothing a prefix does not.
2. **Pattern strings with lambda arms.** The full pattern grammar, but opaque to every tool: ruff reports a class used only inside a pattern as unused and the lint gate's `--fix` would delete the import.
3. **Bare capture names**, `(Point(x=0, y=y), y + 1)`. Closest to Elixir, and refused by mypy, pyright and ruff alike.
4. **A real `match` inside a decorated block.** The only shape with typed captures, and statement-only, which gives up the point.
5. **Runtime evaluation outside a decorator.** `eop_cond` would evaluate every clause eagerly and `eop_case` cannot work at all, since a pattern is a constructor call before the adapter sees it.
6. **Elixir's no-match raise and a final `true ->` clause.** Each has evidence; `default=` won because a type checker enforces it.
7. **Three ports, one per form.** Identical protocols; one keyed port removed the duplication and two public names.
8. **`@Invert` on the transformer adapter's constructor.** Less code, but it would have loosened the rule that only `app` injects, and the decorators pass a port along already.
