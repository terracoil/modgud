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
    Then read the four barrels and their __all__: modgud/__init__.py (13 names),
    modgud/domain/__init__.py (9), modgud/app/__init__.py (4) and
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
    • RE-READ each active class's public methods (GuardRegistry, CommonGuards,
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

`modgud/__init__.py` is the barrel: it re-exports 13 names in its `__all__` and holds no logic beyond reading `__version__` from the installed metadata. Eleven are Public: the two decorators (`guarded_expression`, `implicit_return`), the guard toolkit (`CommonGuards`, `GuardRegistry`), `GuardFailureEnum`, the `GuardFunction` alias and the five exceptions. Two are Seam: `GuardPort` and `ImplicitReturnPort`.

Two secondary barrels reach the same objects: `modgud.domain` (9 names: the enum, the alias, the five exceptions, the two ports) and `modgud.app` (4 names: the decorators and the toolkit). `modgud.infrastructure` exports nothing. Everything else stays home: both adapters, `MethodDescriptors` and the three AST helpers, all under `infrastructure/`. `tests/test_public_api.py` pins all three `__all__` lists, so a name cannot join or leave by accident.

## 🛡️ Decorators: `app/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `guarded_expression` (`guarded_expression.py`) | Active | Class-based decorator applied with arguments. `__init__` wears `@Invert(bootstrap='modgud')` and captures `*guards`, `implicit_return`, `strategy`, `on_failure` and `continuance`; `guard_port` and `imp_return_port` are injected by Idunn unless the caller passes them, and passing both means nothing is discovered. `__call__` is a single call to `guard_port.transform(...)` with the captured configuration and the implicit-return port; everything else happens in the adapter. | Public | — |
| `implicit_return` (`implicit_return.py`) | Active | Class-based decorator applied with parentheses: `@implicit_return()`. `__init__` wears the same `@Invert` and takes only the keyword `imp_return_port`. `__call__` is a single call to `imp_return_port.transform(func)`; the adapter does the rewrite, the marking and the refusal to sit above `@guarded_expression`. | Public | — |

## 🧰 Guard toolkit: `app/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `CommonGuards` (`common_guards.py`) | Active | Nine static guard factories: `not_empty`, `not_none`, `positive`, `in_range`, `type_check`, `matches_pattern`, `valid_file_path`, `valid_url` and `valid_enum`. Each returns a `GuardFunction` that finds its argument by name in the keywords first, then by `position`. Importing the module registers all nine in `GuardRegistry` under the `common` namespace. | Public | — |
| `GuardRegistry` (`guard_registry.py`) | Active (state) | Process-wide registry of guard factories, global or namespaced, reached through classmethods: `register`, `get`, `has_guard`, `list_guards`, `list_namespaces` and `unregister`. `instance()` returns the singleton; constructing one directly raises `RuntimeError` once the singleton exists, and `_create_for_testing()` builds an isolated one for tests. It has no lock, so register at import time. | Public | Minor |

## 📜 Definitions and ports: `domain/`

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `GuardFunction` (`types.py`) | Passive | Type alias, not a class: `Callable[..., bool \| str]`. A guard returns `True` to pass or an error message to fail. Shared by `app/` and `infrastructure/`. | Public | — |
| `GuardFailureEnum` (`enums/guard_failure_enum.py`) | Passive | `IntEnum` naming what happens when guards fail: `ERROR_RAISE`, `ERROR_RETURN`, `RETURN_VALUE` and `CALL_HANDLER`. Each is paired with the decorator's `on_failure` payload. | Public | — |
| `GuardPort` (`ports/guard_port.py`) | Passive | `@Port` Protocol with one method, `transform(func, continuance, imp_return_port, implicit_return, guards, strategy, on_failure)`: rewrite through the implicit-return port when asked, then wrap with the guards, handling a `staticmethod` / `classmethod` either side. The contract a custom guard port must honour is in ADR-002: on a method the guards see the arguments without `self` / `cls`, a `CALL_HANDLER` handler still sees all of them, and a coroutine function is wrapped in a coroutine function. | Seam | — |
| `ImplicitReturnPort` (`ports/implicit_return_port.py`) | Passive | `@Port` Protocol with two methods. `transform_function(func)` returns the plain `func` rewritten so each branch's tail expression is its return value; a guard port calls it. `transform(func)` is what `@implicit_return()` calls: the same rewrite, plus descriptor handling, the `__implicit_return__` marker and a `TypeError` for a `guarded_expression` wrapper. | Seam | — |

## Exceptions: `domain/errors/`

One class per module. The `ImplicitReturnError` family is raised when the decorator is applied, not when the function is called, and carries `lineno` / `offset` like any `SyntaxError`. Missing source raises a plain `ValueError` instead.

| Class | Base | Raised when | Audience |
|-------|------|-------------|----------|
| `GuardClauseError` | `Exception` | A guard fails under the default `on_failure`. Several failures arrive as an `ExceptionGroup` of these. | Public |
| `ImplicitReturnError` | `SyntaxError` | Never directly; it is the base of the three below, and the one to catch for any of them. | Public |
| `ExplicitReturnDisallowedError` | `ImplicitReturnError` | The rewritten body contains a `return`, nested definitions included. | Public |
| `MissingImplicitReturnError` | `ImplicitReturnError` | A branch cannot yield a value: a tail `if` has no `else`, or a tail `match` has no wildcard case. | Public |
| `UnsupportedConstructError` | `ImplicitReturnError` | A tail statement is of an unsupported kind, or the body uses zero-argument `super()` or a bare `__class__`. | Public |

## 🔌 Adapters and helpers: `infrastructure/`

The adapters are what Idunn discovers and injects into the decorators. The helpers under `ast/` (underscore modules) and `internal/` are re-exported only by their own package and imported only by the adapters.

| Class / Symbol | Nature | Purpose | Audience | Generic utility? |
|----------------|--------|---------|----------|------------------|
| `GuardAdapter` (`adapters/guard_adapter.py`) | Active | Singleton `@Adapter` for `GuardPort`. `transform` unwraps a descriptor, rewrites through the implicit-return port unless the rewrite is off or the function is already marked `__implicit_return__`, wraps with `wrap_function`, stamps `__modgud_guarded__` (and `__implicit_return__`) and rewraps. `wrap_function` builds a sync or async wrapper that runs the guards before the body; the guards see the call without the receiver and with unsupplied defaults filled in by name. The classmethod `check_guards` collects up to `1 + continuance` failures, and a guard that raises propagates only when nothing has failed yet. The classmethod `handle_failure` dispatches per `GuardFailureEnum`, building one exception or `ExceptionGroup('Guards failed', ...)`. Annotations are carried in either form for Python 3.14. | Internal | — |
| `ImplicitReturnAdapter` (`adapters/implicit_return_adapter.py`) | Active | Singleton `@Adapter` for `ImplicitReturnPort`. `transform` unwraps a descriptor, refuses a `guarded_expression` wrapper with `TypeError`, calls `transform_function`, marks the result and rewraps. `transform_function` reads the source, rewrites it, compiles it in a builtins-only namespace, then re-binds the code to the function's live globals with the original defaults, annotations, `__qualname__` and `__dict__`. Methods are re-compiled inside stand-in classes so private names mangle correctly. The classmethod `transform_function_ast` refuses zero-argument `super()`, `__class__` and any `return`, rewrites the tails and appends the single `return`; the classmethod `apply_implicit_return_transform` parses the source and applies that to the target function. | Internal | — |
| `MethodDescriptors` (`internal/method_descriptors.py`) | Active | Two static methods that let either adapter sit on either side of `@staticmethod` / `@classmethod`. `unwrap` returns the plain function and the descriptor type (`None` for a plain function); `rewrap` puts the finished function back into a descriptor of that type. The private `DescriptorKind` alias in the same module names that type. | Internal | Yes |
| `TailRewriter` (`ast/_tail_rewriter.py`) | Active | Replaces each tail expression with an assignment to the hidden result variable it is constructed with. `rewrite_block` and `rewrite_tail_stmt` handle a bare expression, `if`, `try` and `match`; a tail `match` must end in an irrefutable case. Raises `MissingImplicitReturnError` or `UnsupportedConstructError`. | Internal | — |
| `TopLevelTransformer` (`ast/_top_level_transformer.py`) | Active | `ast.NodeTransformer` that applies an injected rewrite to the one function named `target_name`, sync or async, and strips its decorators so the re-compile does not apply them twice. Takes the rewrite as a callable, so it does not depend on the adapter. | Internal | Minor |
| `NoExplicitReturnChecker` (`ast/_no_explicit_return_checker.py`) | Active | `ast.NodeVisitor` that records the line and column of the first `return` in `found`. It descends into nested `def`, `async def` and class bodies, because the whole body is re-compiled as one unit. | Internal | Yes |

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
| `free_range/02_common_guards.py` | `Color` | Passive | The `Enum` that `CommonGuards.valid_enum` checks against. |
| `free_range/03_failure_strategies.py` | `PaymentError` | Passive | A custom exception passed as `on_failure`, raised in place of `GuardClauseError`. |
| `free_range/12_swapping_the_runtime.py` | `AuditingRuntime` | Active (state) | A fake shaped like `GuardPort`, passed as `guard_port=`: it logs each call's guard verdicts and never blocks. |
| `free_range/12_swapping_the_runtime.py` | `RecordingTransformer` | Active (state) | A fake shaped like `ImplicitReturnPort`, passed as `imp_return_port=`: it notes each function it is handed and returns it untouched. |

## 📚 Reading the catalog

- **The public surface is small.** Thirteen names, of which eleven are for everyday use and two are the seam. Nothing public is defined in `infrastructure/`.
- **The seam is two Protocols.** `GuardPort` and `ImplicitReturnPort` are the whole contract between the decorators and the code that does the work. A fake needs one method and no base class; the two in `free_range/12_swapping_the_runtime.py` are the worked example.
- **Internal does not mean unreachable.** Both adapters, `MethodDescriptors` and the three AST helpers can all be imported from their leaf packages, and the adapter unit tests do exactly that. None of them is supported, and the underscore module names under `ast/` say so twice.
- **Reusable bits worth extracting.** `MethodDescriptors` and `NoExplicitReturnChecker` know nothing about modgud. `GuardRegistry`'s namespaced registry and `TopLevelTransformer`'s "rewrite this one function" are nearly as portable.
- **One class per file holds throughout `modgud/`.** The only module without a class is `domain/types.py`, which holds the `GuardFunction` alias.
