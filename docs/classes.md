<!--
═══════════════════════════════════════════════════════════════════════════════
  CLAUDE — SELF-UPDATE RECIPE FOR THIS FILE  (docs/classes.md)
  Hidden from rendered Markdown; meant only for the agent maintaining this doc.

  TRIGGER. When the user says "update classes.md", "update the class catalog",
  "regenerate the catalog", or anything equivalent, follow this recipe top to
  bottom. Re-scan the source EVERY time — never hand-patch from memory, because
  the whole point of this file is that it tracks the code, not the other way around.

  STEP 1 — SCAN. Enumerate every class / Protocol / Enum / exception / dataclass /
    TypedDict defined under modgud/ (all three layers: app/, domain/,
    infrastructure/) and under examples/. A quick sweep:
        grep -rnE '^\s*class ' modgud/ examples/ --include='*.py'
    Then read the four barrels and their __all__: modgud/__init__.py (23 names),
    modgud/domain/__init__.py (14), modgud/app/__init__.py (9) and
    modgud/infrastructure/__init__.py (none). Every class the sweep finds gets a
    row. Public names that are not classes (the GuardFunction alias) get a row
    too; private aliases and TypeVars are mentioned in a Purpose, not listed.

  STEP 2 — CLASSIFY each class on two axes, using plain words:
    • Audience:  Public   — in modgud/__init__.py __all__ and meant for everyday
                            use: imported, called, caught.
                 Seam     — in __all__, but there for integrators: the two @Port
                            Protocols behind guard_port= / imp_return_port=.
                 Internal — plumbing; importable, never supported. Being
                            re-exported by a leaf package (modgud.infrastructure.ast,
                            modgud.infrastructure.adapters) does not change that.
                 These are the three tiers in project.md and CLAUDE.md; if the
                 tier table there changes, change the marks here to match.
    • Nature:    Passive — enum / exception / Protocol / type alias / dataclass
                           (holds shape, not behavior).
                 Active  — validates / wraps / rewrites / registers / orchestrates.

  STEP 3 — GROUP into the sections below, keeping layer order app → domain →
    infrastructure: Public API surface · Decorators · Guard toolkit · Definitions
    and ports · Exceptions · Adapters and helpers · Examples. Add or drop a
    section only if a whole area appears or disappears in the code.

  STEP 4 — COLUMNS per library table: Class / Symbol | Nature | Purpose | Audience |
    Generic utility?
    • Purpose — one tight paragraph: WHAT it does + any load-bearing invariant.
    • Generic utility? — "Yes" (or "Minor") when (part of) it is a reusable,
                         project-agnostic helper; "—" otherwise.
    Exceptions use Class | Base | Raised when | Audience. Examples use
    File | Class | Nature | Purpose.

  STEP 5 — SYNC CHECK against the previous version of this file:
    • new classes → add rows; removed classes → delete rows; renamed → rename;
      moved → fix the path in the section heading or the File column.
    • if any __all__ changed, re-derive every Public / Seam / Internal mark and
      the counts in "Public API surface" (tests/test_public_api.py pins them).
    • RE-READ the two decorators' __init__ signatures so Purpose text matches the
      current parameters, and the port method signatures so the Seam rows do too.
    • RE-READ each active class's public methods (GuardRegistry, Guards,
      GuardAdapter, ImplicitReturnAdapter, TailRewriter) so the method lists in
      Purpose are complete.
    • compare the Exceptions table with "Error classes" in api-reference.md and
      the docstrings in modgud/domain/errors/; all three must agree.
    • spot-check the Examples section against examples/README.md and the files
      themselves: one row per class. free_range/ is mostly functions, which are
      not rows; it drifts most often.

  STEP 6 — Keep the Parent line, emoji only in the `##` headings (as the other
    modgud docs do, none in tables, the legend or bullets), the legend, and the
    "Reading the catalog" closing notes (refresh their wording if the story
    actually changed). KEEP THIS COMMENT BLOCK intact at the top so the next
    update is just as cheap.

  STEP 7 — VERIFY. tests/test_docs.py checks every relative link and anchor in
    this file, so finish with:
        poetry run pytest tests/test_docs.py

  SOURCES OF TRUTH to verify against:
    modgud/__init__.py · modgud/app/* · modgud/domain/types.py ·
    modgud/domain/enums/* · modgud/domain/errors/* · modgud/domain/ports/* ·
    modgud/infrastructure/adapters/* · modgud/infrastructure/ast/* ·
    examples/classy/* · examples/free_range/* · project.md (tiers) ·
    docs/api-reference.md (error table)
═══════════════════════════════════════════════════════════════════════════════
-->

**Parent**: [📚 Documentation Hub](ADVANCED.md) | [🌉 Main README](../README.md) | [📖 API Reference](api-reference.md)

# Class catalog

A map of every class defined in the `modgud/` package and the runnable `examples/`. Use it to tell at a glance what is part of the public contract, what is the integration seam, and what is plumbing. The package has three layers, `app/`, `domain/` and `infrastructure/`; the import directions between them are in [project.md](../project.md) and enforced by `tests/test_architecture.py`. Signatures and parameter tables live in the [API reference](api-reference.md); this page only says what each class is for.

> *This file is self-maintaining: say "update classes.md" and Claude re-scans the source and regenerates it from the recipe embedded at the top.*

## 🧭 Legend

| Mark | Audience: who is meant to see it |
|------|----------------------------------|
| **Public** | Part of the everyday API: exported from `modgud` and meant to be imported, called or caught. |
| **Seam** | Exported from `modgud`, but there for integrators: the two ports a custom `guard_port=` or `imp_return_port=` is typed against. |
| **Internal** | Plumbing. Importable from its leaf package, never supported, and free to move between releases. |

| Mark | Nature |
|------|--------|
| **Passive** | A definition: enum, exception, Protocol or type alias. Holds shape, not behavior. |
| **Active** | Does something: validates, wraps, rewrites, registers, orchestrates. |

- **Generic utility?** "Yes" when the class, or an extractable part of it, is a reusable, project-agnostic helper. "Minor" when only a small part is.

## 📦 Public API surface: `modgud/__init__.py`

`modgud/__init__.py` is the barrel: it re-exports 24 names in its `__all__` and holds no logic beyond reading `__version__` from the installed metadata. Twenty-one are Public: the two decorators (`guarded_expression`, `implicit_return`), the guard toolkit (`Guards`, its alias `CommonGuards`, `GuardRegistry`), `GuardFailureEnum`, the `GuardFunction` alias, the eight exceptions, the three forms (`eop_cond`, `eop_case`, `eop_match`) and their vocabulary (`eop_clause`, `eop_when`, `eop_var`). Three are Seam: `GuardPort`, `ImplicitReturnPort` and `EopPort`.

Two secondary barrels reach the same objects: `modgud.domain` (14 names: the enum, the alias, `eop_clause`, the eight exceptions, the three ports) and `modgud.app` (10 names: the decorators, the toolkit with its `CommonGuards` alias and the five markers). `modgud.infrastructure` exports nothing. Everything else stays home: the five adapters, `MethodDescriptors` and the AST helpers, all under `infrastructure/`. `tests/test_public_api.py` pins all three `__all__` lists, so a name cannot join or leave by accident.

## 🛡️ Decorators: `app/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `guarded_expression` (`guarded_expression.py`) | Active | Class-based decorator applied with arguments. `__init__` wears `@Invert(bootstrap='modgud')` and captures `*guards`, `implicit_return`, `strategy`, `on_failure` and `continuance`; `guard_port` and `imp_return_port` are injected by Idunn unless the caller passes them, and passing both means nothing is discovered. `__call__` is a single call to `guard_port.transform(...)` with the captured configuration and the implicit-return port; everything else happens in the adapter. | Public | — |
| `implicit_return` (`implicit_return.py`) | Active | Class-based decorator applied with parentheses: `@implicit_return()`. `__init__` wears the same `@Invert` and takes the keywords `imp_return_port`, `eop_cond_port`, `eop_case_port` and `eop_match_port`, the last three chosen by their `EopFormEnum` key. `__call__` is a single call to `imp_return_port.transform(func, forms=...)`; the adapter does the rewrite, the form lowering, the marking and the refusal to sit above `@guarded_expression`. | Public | — |

## 🧩 Expression forms: `app/`

The markers are typed stand-ins whose calls the rewrite compiles away. Each carries its `EopFormEnum` in `__modgud_eop_form__`, which is how the resolver recognises it without `infrastructure` ever importing `app`.

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `EopCond` / `eop_cond` (`eop_cond.py`) | Active | Elixir's `cond`: `__call__(*clauses: eop_clause[T], default: D) -> T \| D`. Outside a decorated function it delegates to the injected `EopPort` through a private `@Invert(bootstrap='modgud', keys=...)` helper, which refuses with `MarkerNotRewrittenError`. The module constant `eop_cond` is the instance users import. | Public | — |
| `EopCase` / `eop_case` (`eop_case.py`) | Active | Elixir's `case`: `__call__(subject, *clauses: eop_clause[T], default: D) -> T \| D`. Same refusal path, keyed `EopFormEnum.CASE`. | Public | — |
| `EopMatch` / `eop_match` (`eop_match.py`) | Active | Elixir's `match?`: `__call__(pattern, value) -> bool`. Same refusal path, keyed `EopFormEnum.MATCH`. | Public | — |
| `EopWhen` / `eop_when` (`eop_when.py`) | Passive | `__call__(pattern, guard) -> object`, a pattern with a guard. Pattern vocabulary with no adapter behaviour, so a plain call raises `MarkerNotRewrittenError` directly. | Public | — |
| `EopVar` / `eop_var` (`eop_var.py`) | Passive | The capture object: `__getattr__` stands for a capture, raising `MarkerNotRewrittenError` for any plain use and `AttributeError` for dunder lookups so `hasattr` and `inspect` keep working. | Public | — |

## 🧰 Guard toolkit: `app/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `Guards` (`guards.py`) | Active | Nine static guard factories: `not_empty`, `not_none`, `positive`, `in_range`, `type_check`, `matches_pattern`, `valid_file_path`, `valid_url` and `valid_enum`. Each returns a `GuardFunction` that finds its argument by name in the keywords first, then by `position`. Importing the module registers all nine in `GuardRegistry` under the `common` namespace. `CommonGuards` is the former name, kept as an alias. | Public | — |
| `GuardRegistry` (`guard_registry.py`) | Active (state) | Process-wide registry of guard factories, global or namespaced, reached through classmethods: `register`, `get`, `has_guard`, `list_guards`, `list_namespaces` and `unregister`. `instance()` returns the singleton; constructing one directly raises `RuntimeError` once the singleton exists, and `_create_for_testing()` builds an isolated one for tests. It has no lock, so register at import time. | Public | Minor |

## 📜 Definitions and ports: `domain/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `GuardFunction` (`types.py`) | Passive | Type alias, not a class: `Callable[..., bool \| str]`. A guard returns `True` to pass or an error message to fail. Shared by `app/` and `infrastructure/`. The same module holds the `T`, `T_co` and `F` type variables. | Public | — |
| `eop_clause` (`types.py`) | Passive | Frozen, slotted, generic dataclass pairing a `test` with the `value` it selects; Elixir's word for a branch. Lowercase because it is spelled like the forms it belongs to. Recognised by identity, so the rewrite reads it only when written inside a form call. | Public | — |
| `EopFormEnum` (`enums/eop_form_enum.py`) | Passive | `StrEnum` of the six `eop_` names. The three forms double as Idunn adapter keys for `EopPort`; all six tag the app markers and name the reserved `@eop_` identifiers the resolver substitutes. Exported by `modgud.domain.enums` only. | Internal | — |
| `GuardFailureEnum` (`enums/guard_failure_enum.py`) | Passive | `IntEnum` naming what happens when guards fail: `ERROR_RAISE`, `ERROR_RETURN`, `RETURN_VALUE` and `CALL_HANDLER`. Each is paired with the decorator's `on_failure` payload. | Public | — |
| `GuardPort` (`ports/guard_port.py`) | Passive | `@Port` Protocol with one method, `transform(func, continuance, imp_return_port, implicit_return, guards, strategy, on_failure)`: rewrite through the implicit-return port when asked, then wrap with the guards, handling a `staticmethod` / `classmethod` either side. The contract a custom guard port must honour is in ADR-002: on a method the guards see the arguments without `self` / `cls`, a `CALL_HANDLER` handler still sees all of them, and a coroutine function is wrapped in a coroutine function. | Seam | — |
| `ImplicitReturnPort` (`ports/implicit_return_port.py`) | Passive | `@Port` Protocol with two methods. `transform_function(func, *, forms, implicit_return=True)` returns the plain `func` with every `eop_` form lowered through `forms` and, in implicit mode, each branch's tail expression as its return value; a guard port calls it. `transform(func, *, forms)` is what `@implicit_return()` calls: the same rewrite, plus descriptor handling, the `__implicit_return__` marker and a `TypeError` for a `guarded_expression` wrapper. | Seam | — |
| `EopPort` (`ports/eop_port.py`) | Passive | `@Port` Protocol shared by the three forms, told apart by key. `lower(call, *, hoistable, fresh)` returns the statements to place before the enclosing statement and the expression that replaces the call; `refuse()` raises `MarkerNotRewrittenError` for a plain call. It is the one domain port that speaks `ast` types. | Seam | — |

## Exceptions: `domain/errors/`

One class per module. The `ImplicitReturnError` family is raised when the decorator is applied, not when the function is called, and carries `lineno` / `offset` like any `SyntaxError`. Missing source raises a plain `ValueError` instead.

| Class | Base | Raised when | Audience |
|-------|------|-------------|----------|
| `GuardClauseError` | `Exception` | A guard fails under the default `on_failure`. Several failures arrive as an `ExceptionGroup` of these. | Public |
| `ImplicitReturnError` | `SyntaxError` | Never directly; it is the base of the three below, and the one to catch for any of them. | Public |
| `ExplicitReturnDisallowedError` | `ImplicitReturnError` | The rewritten body contains a `return`, nested definitions included. | Public |
| `MissingImplicitReturnError` | `ImplicitReturnError` | A branch cannot yield a value: a tail `if` has no `else`, or a tail `match` has no wildcard case. | Public |
| `UnsupportedConstructError` | `ImplicitReturnError` | A tail statement is of an unsupported kind, or the body uses zero-argument `super()` or a bare `__class__`. | Public |
| `MarkerUsageError` (`errors/marker_usage_error.py`) | Passive | `ImplicitReturnError` raised at decoration for a malformed `eop_` form: a missing `default=`, a pattern outside the subset, a capture used outside its clause, vocabulary outside a form. | Public | — |
| `MarkerPlacementError` (`errors/marker_placement_error.py`) | Passive | `ImplicitReturnError` raised at decoration for a well-formed `eop_` form in a place it cannot be lowered: a comprehension's first iterable, a nested class body, a guard that reads a comprehension variable. | Public | — |
| `MarkerNotRewrittenError` (`errors/marker_not_rewritten_error.py`) | Passive | `RuntimeError` raised at call time when an `eop_` marker runs as a plain call because no decorator rewrote it. Takes the form's name as a `str`, kept in `.name`, so `domain/errors` needs nothing from `domain/enums`. | Public | — |

## 🔌 Adapters and helpers: `infrastructure/`

The adapters are what Idunn discovers and injects into the decorators. The helpers under `ast/` (underscore modules) and `internal/` are re-exported only by their own package and imported only by the adapters.

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `GuardAdapter` (`adapters/guard_adapter.py`) | Active | Singleton `@Adapter` for `GuardPort`. `transform` unwraps a descriptor, rewrites through the implicit-return port unless the rewrite is off or the function is already marked `__implicit_return__`, wraps with `wrap_function`, stamps `__modgud_guarded__` (and `__implicit_return__`) and rewraps. `wrap_function` builds a sync or async wrapper that runs the guards before the body; the guards see the call without the receiver and with unsupplied defaults filled in by name. The classmethod `check_guards` collects up to `1 + continuance` failures, and a guard that raises propagates only when nothing has failed yet. The classmethod `handle_failure` dispatches per `GuardFailureEnum`, building one exception or `ExceptionGroup('Guards failed', ...)`. Annotations are carried in either form for Python 3.14. | Internal | — |
| `ImplicitReturnAdapter` (`adapters/implicit_return_adapter.py`) | Active | Singleton `@Adapter` for `ImplicitReturnPort`. `transform` unwraps a descriptor, refuses a `guarded_expression` wrapper with `TypeError`, calls `transform_function`, marks the result and rewraps. `transform_function` reads the source, rewrites it, compiles it in a builtins-only namespace, then re-binds the code to the function's live globals with the original defaults, annotations, `__qualname__` and `__dict__`. Methods are re-compiled inside stand-in classes so private names mangle correctly. The classmethod `transform_function_ast` refuses zero-argument `super()`, `__class__` and any `return`, rewrites the tails and appends the single `return`; the classmethod `apply_implicit_return_transform` parses the source and applies that to the target function. | Internal | — |
| `EopCondAdapter` (`adapters/eop_cond_adapter.py`) | Active | Singleton `@Adapter` for `EopPort` under key `EopFormEnum.COND`. `lower` reads the clauses with `ClauseReader` and returns no prelude and one right-nested `IfExp`; each test becomes `(t := test) is not None and t is not False`, Elixir's truth rule, with one temporary per call. `refuse` raises `MarkerNotRewrittenError('eop_cond')`. | Internal | — |
| `EopCaseAdapter` (`adapters/eop_case_adapter.py`) | Active | Singleton `@Adapter` for `EopPort` under key `EopFormEnum.CASE`. With `hoistable=True` it returns a real `ast.Match` assigning a temporary, captures renamed `@mg_cap_<i>_<name>` and each guard as a generated function; otherwise one generated matcher per clause and a chain of conditional expressions over `(caps := matcher(subject)) is not None`. Shares `PatternTranslator`, `MatcherBuilder` and `CaptureSubstituter`. | Internal | — |
| `EopMatchAdapter` (`adapters/eop_match_adapter.py`) | Active | Singleton `@Adapter` for `EopPort` under key `EopFormEnum.MATCH`. `lower` returns one generated matcher returning `True` / `False` and a call of it; no temporary, so it fits even where a walrus is illegal. | Internal | — |
| `MethodDescriptors` (`internal/method_descriptors.py`) | Active | Two static methods that let either adapter sit on either side of `@staticmethod` / `@classmethod`. `unwrap` returns the plain function and the descriptor type (`None` for a plain function); `rewrap` puts the finished function back into a descriptor of that type. The private `DescriptorKind` alias in the same module names that type. | Internal | Yes |
| `TailRewriter` (`ast/_tail_rewriter.py`) | Active | Replaces each tail expression with an assignment to the hidden result variable it is constructed with. `rewrite_block` and `rewrite_tail_stmt` handle a bare expression, `if`, `try` and `match`; a tail `match` must end in an irrefutable case. Raises `MissingImplicitReturnError` or `UnsupportedConstructError`. | Internal | — |
| `TopLevelTransformer` (`ast/_top_level_transformer.py`) | Active | `ast.NodeTransformer` that applies an injected rewrite to the one function named `target_name`, sync or async, and strips its decorators so the re-compile does not apply them twice. Takes the rewrite as a callable, so it does not depend on the adapter. | Internal | Minor |
| `NoExplicitReturnChecker` (`ast/_no_explicit_return_checker.py`) | Active | `ast.NodeVisitor` that records the line and column of the first `return` in `found`. It descends into nested `def`, `async def` and class bodies, because the whole body is re-compiled as one unit. | Internal | Yes |
| `MarkerResolver` (`ast/_marker_resolver.py`) | Active | `ast.NodeTransformer` built from the function's scope (builtins, globals, closure). `normalise` replaces every reference to an `eop_` marker, bare or through module attributes, with its reserved `@eop_` name and reports the forms seen; a name bound anywhere in the function is never a marker. `references` answers the explicit-mode probe from a code object's names without reading source. `form_of` and `bound_names` are the shared helpers. | Internal | — |
| `FormLowerer` (`ast/_form_lowerer.py`) | Active | Walks every statement list of the function, lowers each statement's form calls through a `FormCallLowerer`, and places the prelude in the same block before the statement. Decides `hoistable` (the call is the whole value of an assignment or expression statement), refuses forms in nested class bodies, and refuses any reserved name left over. Supplies the `@mg_<kind>_<n>` temporaries. | Internal | — |
| `FormCallLowerer` (`ast/_form_call_lowerer.py`) | Active | `ast.NodeTransformer` for one statement: lowers form calls innermost first through their `EopPort`, collects the prelude, and enforces two placement rules while tracking comprehension and lambda scopes: no walrus-based lowering in a comprehension's first iterable, and no generated function reading a name those scopes bind. | Internal | — |
| `PatternTranslator` (`ast/_pattern_translator.py`) | Active | Turns a pattern written as an expression into a real `ast.pattern`: captures, wildcards, literals, dotted and bare names, class, sequence and mapping patterns. Records the captures in order and the equality tests a bare name turns into; captures are renamed through a callback. Anything outside the subset raises `MarkerUsageError`. | Internal | — |
| `MatcherBuilder` (`ast/_matcher_builder.py`) | Active | Builds the generated functions: a guard function that returns `True` only when the guard is exactly `True` and did not raise, and a one-case matcher that returns a hit value or a miss value. Both carry the Elixir guard rules in the `try` they emit. | Internal | — |
| `ClauseReader` (`ast/_clause_reader.py`) | Active | Validates a form call's shape and returns `(subject, [(test, value), ...], default)`; `split_when` takes `eop_when(pattern, guard)` apart and refuses `await`, `yield` and `:=` inside the guard. | Internal | — |
| `CaptureSubstituter` (`ast/_capture_substituter.py`) | Active | `ast.NodeTransformer` that swaps `@eop_var.<name>` for the expression holding that capture, leaving names outside its mapping for an enclosing clause to bind. | Internal | — |

## 🗂️ Examples: `examples/`

Teaching code: Public as documentation, but not part of the importable library or the wheel. Two trees with matching numbers, importing only from `modgud` and the standard library. `tests/test_examples.py` runs every file. The [examples index](../examples/README.md) says what each file teaches.

### `classy/`: one class per file

Every class ends with a `demo()` classmethod holding the asserts.

| File | Class | Nature | Purpose |
|------|-------|--------|---------|
| `classy/01_quick_start.py` | `DiscountCalculator` | Active | The README's class: a guarded static `calculate` with an implicit return. |
| `classy/03_failure_strategies.py` | `Checkout` | Active | Four `charge` methods, one per `GuardFailureEnum` strategy, with the static `explain` as the `CALL_HANDLER` handler. |
| `classy/04_implicit_returns.py` | `Gradebook` | Active | `@implicit_return()` on instance, static and class methods, with the `with_tax` helper kept outside the rewritten bodies. |
| `classy/06_continuance.py` | `Warehouse` | Active | `reserve` and `try_reserve` collect several failures with `continuance=3`; `reserve_safely` shows cascade safety when a later guard would raise. |
| `classy/07_custom_guards.py` | `ShippingGuards` | Active | A hand-written guard (`fragile_ok`), a guard factory typed with `GuardFunction` (`max_weight`), and a static `quote` guarded by both. |
| `classy/08_async_functions.py` | `UserService` | Active | Guarded `async def` methods, `fetch` and `fetch_all`, over an injected directory. |
| `classy/09_api_endpoint.py` | `UserApi` | Active (state) | `create_user` writes to an injected store, or returns the static `bad_request` handler's 400 payload listing every failure. |
| `classy/10_decorator_composition.py` | `Thermostat` | Active | Every method shape modgud decorates, with modgud on either side of `@staticmethod` / `@classmethod`, plus the refusals applied in `demo`. |

### `free_range/`: module-level functions

Functions are not classes, so most of this tree has no rows. Three files define classes to support their functions.

| File | Class | Nature | Purpose |
|------|-------|--------|---------|
| `free_range/02_common_guards.py` | `Color` | Passive | The `Enum` that `Guards.valid_enum` checks against. |
| `free_range/03_failure_strategies.py` | `PaymentError` | Passive | A custom exception passed as `on_failure`, raised in place of `GuardClauseError`. |
| `free_range/12_swapping_the_runtime.py` | `AuditingRuntime` | Active (state) | A fake shaped like `GuardPort`, passed as `guard_port=`: it logs each call's guard verdicts and never blocks. |
| `free_range/12_swapping_the_runtime.py` | `RecordingTransformer` | Active (state) | A fake shaped like `ImplicitReturnPort`, passed as `imp_return_port=`: it notes each function it is handed and returns it untouched. |

## 📚 Reading the catalog

- **The public surface is small.** Thirteen names, of which eleven are for everyday use and two are the seam. Nothing public is defined in `infrastructure/`.
- **The seam is two Protocols.** `GuardPort` and `ImplicitReturnPort` are the whole contract between the decorators and the code that does the work. A fake needs one method and no base class; the two in `free_range/12_swapping_the_runtime.py` are the worked example.
- **Internal does not mean unreachable.** Both adapters, `MethodDescriptors` and the three AST helpers can all be imported from their leaf packages, and the adapter unit tests do exactly that. None of them is supported, and the underscore module names under `ast/` say so twice.
- **Reusable bits worth extracting.** `MethodDescriptors` and `NoExplicitReturnChecker` know nothing about modgud. `GuardRegistry`'s namespaced registry and `TopLevelTransformer`'s "rewrite this one function" are nearly as portable.
- **One class per file holds throughout `modgud/`.** The only module without a class is `domain/types.py`, which holds the `GuardFunction` alias.
