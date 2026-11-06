**Parent**: [📚 Documentation Hub](README.md) | [🌉 Main README](../README.md) | [📖 API Reference](api-reference.md)

# How it works

A defensive Python function opens with a wall of `if x is None: raise ...` and ends with `return` statements scattered across every branch. modgud moves the wall into a decorator and, by default, rewrites the body so each branch's last expression is its value. Both jobs happen once, when the decorator is applied. A call pays for a wrapper and your guards. That's the bill.

Signatures and rules live in the [API reference](api-reference.md). This page is the machinery.

## 🏛️ Layers

Three layers, dependencies pointing down. `app/` holds the two decorators and the public `CommonGuards` and `GuardRegistry`. `domain/` holds the passive parts — `GuardFailureEnum`, the errors, the `GuardFunction` type and the two `@Port` protocols. `infrastructure/` holds the adapters behind those ports and the internal AST helpers in `infrastructure/ast/`.

The app layer never imports infrastructure. It knows the ports and nothing else. The package tree, the tiers and the dependency table are in [project.md](../project.md), and `tests/test_architecture.py` fails the run when an import crosses a line. Architecture diagrams drift; an AST walk in the test suite doesn't.

## 🔌 Ports, adapters and Idunn

Applying `@guarded_expression(...)` takes three steps. The first two happen inside `@Invert(bootstrap='modgud')` on the decorator's `__init__`.

1. If the caller left `runtime` or `transformer` out, Idunn runs `Idunn().bootstrap('modgud')`. The first call in a process discovers `modgud.domain.*.ports` and `modgud.infrastructure.adapters` and registers `GuardAdapter` and `ImplicitReturnAdapter` as singleton adapters. Later calls are a cache hit. A caller who passes both skips discovery altogether.
2. Idunn injects whichever of `runtime` and `transformer` the caller did not pass.
3. `__call__(func)` unwraps a `staticmethod` / `classmethod` if it got one, rewrites the function when `implicit_return=True`, wraps it with `runtime.wrap_function(...)`, sets an `__implicit_return__` marker, and puts the descriptor back.

`@implicit_return()` takes the same path with only the transformer. The marker is how `guarded_expression` knows a function was already rewritten, so a stacked pair never rewrites twice.

The bootstrap waits for the first decoration on purpose. Run from `modgud/__init__.py`, it would re-enter a half-imported package and create Idunn's container — which reads `IDUNN_ENV` — before the application had a chance to set it. A library that configures your process at import time is a library you end up pinning around.

### Import-time side effects

Importing modgud isn't free. Here's the whole receipt:

- `import modgud` imports `idunn`, the domain, the ports and the guard toolkit. It doesn't import the adapters or create Idunn's container.
- `CommonGuards` registers its nine factories in `GuardRegistry` under `'common'` as its module loads.
- Discovery, on the first decoration, imports every module under `modgud/`. That's why nothing runnable lives there and the examples sit in `examples/`.

## 🛡️ The guard pipeline

`GuardAdapter.wrap_function` builds one `functools.wraps` wrapper per decorated function, and every call goes through it:

```
call(*args, **kwargs)
  → drop the receiver (methods only)
  → run guards in order, collecting failures
  → no failures: call the body and return its result
  → failures:    dispatch them through strategy / on_failure
```

- **Receiver.** At wrap time, `inspect.signature` checks whether the first parameter is `self` or `cls`. If it is and the caller passed it positionally, guards get `args[1:]`. The handler still gets everything.
- **Collection.** The loop stops once it holds `1 + continuance` failures. `True` passes; a string is a failure message; any other return value becomes `'Guard clause failed'`. A guard that raises propagates when the list is empty and ends the loop when it isn't, so one bad input doesn't produce a stack of secondary crashes.
- **Dispatch.** The error strategies build `on_failure(message)`, or an `ExceptionGroup('Guards failed', [...])` for several; a non-class `on_failure` falls back to `GuardClauseError`. `RETURN_VALUE` returns the payload. `CALL_HANDLER` returns `on_failure(errors, *args, **kwargs)`.
- **Async.** A coroutine function gets an `async` wrapper. The guards run when the coroutine runs, not when it's created, and every strategy's result, fallback values included, comes back from the `await`. A handler is called, not awaited.

## ⚙️ The AST rewrite

Python decided long ago that `if` is a statement. The rewrite disagrees, one function at a time.

`ImplicitReturnAdapter.transform_function` does the work. It's an `@Adapter` subclass of `ImplicitReturnPort`, not an `ast.NodeTransformer`; the tree walking lives in three helpers under `infrastructure/ast/`.

1. Read the source with `inspect.getsource` and dedent it. No source means `ValueError`.
2. Parse it. `TopLevelTransformer` finds the `def` by name and strips its decorators, so recompiling doesn't apply them twice.
3. Refuse zero-argument `super()` and bare `__class__` (nested classes excluded; they get their own cell).
4. `NoExplicitReturnChecker` walks the whole body for `return`, nested `def`s and classes included, and reports the first one.
5. `TailRewriter` turns the last statement of every block into an assignment to `__implicit_result` and appends one `return __implicit_result`.
6. For a method, nest the `def` inside empty stand-in classes named from `__qualname__`; the innermost one declares the PEP 695 type parameters the method closes over, and the rebuilt closure cells are pointed back at the originals. Drop the signature's defaults and annotations from the tree; the originals are reused, so nothing is re-evaluated out of scope.
7. Compile it and `exec` it in a throwaway namespace. Then rebuild the function with `types.FunctionType` on the original's live module globals, and copy over `__name__`, `__qualname__`, `__doc__`, `__dict__` and the annotations.

The `grade` function from the [implicit_return](api-reference.md#implicit_return) entry comes out shaped like this:

```python
def grade(score: int) -> str:
  if score >= 90:
    __implicit_result = 'A'
  elif score >= 75:
    __implicit_result = 'B'
  else:
    __implicit_result = 'C'
  return __implicit_result
```

The throwaway namespace keeps the stand-in classes out of your module. The rebuild matters more. Because the new function runs on the module's real globals, its body sees names defined after decoration, a `global` write lands in the module, `mock.patch` reaches inside, a recursive call goes back through the guards, and a method can name its own class. Late binding, the way Python intended. Default values are the exception: they're evaluated during the `exec`, so they can't see the class body.

On Python 3.14, `functools.wraps` copies the lazy `__annotate__` hook rather than `__annotations__`, so a function whose annotations were set eagerly would lose them. The transformer and the runtime both carry annotations across in whichever form the function has: the hook when there is one, the dictionary when there isn't.

### Methods

Methods were the hard part. Four small mechanisms cover them, each pinned by `tests/test_method_decoration.py`.

- **Descriptors.** `MethodDescriptors.unwrap` takes the function out of a `staticmethod` or `classmethod`, and `rewrap` puts the finished one back. That's what lets modgud sit on either side of them.
- **Receiver.** The pipeline drops `self` / `cls` before calling the guards, as above.
- **Class context.** The stand-in classes make `self.__secret` mangle to `_Cls__secret` as it did in the original class, and `__qualname__` is copied over. They exist only while compiling; at call time the body's globals are the module's, so the class's own name means the real class.
- **Refusals.** Zero-argument `super()` needs a `__class__` cell, and a stand-in class would give it the wrong one. A default value that names something in the class body is evaluated in the throwaway namespace, where it doesn't exist. Both raise `UnsupportedConstructError` at decoration time, where they used to surface as a `RuntimeError` on the first call or a bare `NameError`.

## ⚖️ Costs and limits

### Performance

With the rewrite on, decoration costs one `getsource`, one parse, one compile and one `exec` per function, paid at import. A call costs one extra Python frame, a tuple slice on methods, a loop over the guards, and each guard's own work. No per-call parsing, no signature binding. We haven't published benchmarks. If the overhead matters, time it in your own code; a number measured on someone else's laptop is a rumour.

### Thread safety

What's shared between threads, plainly:

- Decoration and guard evaluation keep no per-call shared state. The wrapper reads its closure, and `CommonGuards` guards are closures over their arguments.
- `GuardRegistry` and the Idunn container are process-wide singletons.
- Idunn's bootstrap is thread-safe: concurrent first decorations share one discovery, and a decoration that runs while a module is being imported discovers on its own rather than waiting, so it can't deadlock against another importing thread. Each adapter singleton is built once, under its own lock.
- `GuardRegistry` has no lock. Register guards at import time, before any threads start.
- Your own guards and handlers are yours: if they touch shared state, they need their own lock.

### Limitations

The gaps, in one place.

- Implicit returns need source on disk: module level or in a class, in a real file. No REPL, no `exec`.
- A function nested in another function loses its closure when rewritten; enclosing locals raise `NameError` at call time.
- Tail positions accept expressions, `if`/`else`, `try`, `match`, `pass` and `raise`. Loops, `with` and assignments are refused. A tail `match` must end in an irrefutable case (`case _:` or a bare capture, no guard); otherwise decoration raises `MissingImplicitReturnError`.
- Order matters: `@implicit_return()` goes under `guarded_expression`; above a guarded wrapper it raises `TypeError` at decoration time. Decorators placed below modgud are dropped by the re-compile, because the source is read again; put modgud innermost (`@staticmethod` / `@classmethod` excepted), or use `implicit_return=False`.
- Guards receive the call's positional arguments as given and its keyword arguments plus, by name, every parameter the caller left at its default. Positional values are still found by `position`, not by name, so `positive('y')` on `f(x, y)` called as `f(1, 2)` checks `x` unless you say `position=1`.
- Generators and async generators aren't tested.
- `implicit_return=False` doesn't enforce a single trailing `return`; that's convention.
- On methods: zero-argument `super()` and bare `__class__` are refused, and `@property`, `cached_property` and other descriptors aren't covered.
- The project is Beta. The public API is the 13 names in [What to import](api-reference.md); everything else may move.

---

[← Back to Documentation Hub](README.md) | [API Reference →](api-reference.md)
