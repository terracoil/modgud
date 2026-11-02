# modgud docs

**Parent**: [Main README](../README.md)

Each topic has one home. This page says which one, and where to start. An earlier version of this page tried to be every home at once and ran past five thousand words.

## 📚 What each document is for

- [README](../README.md): install, the quick start, a tour of the features, and the three limitations most people hit first.
- [API reference](api-reference.md): what to import, every signature and parameter table, the [`GuardFailureEnum`](api-reference.md#guardfailureenum) × `on_failure` table, the [`CommonGuards`](api-reference.md#commonguards) and [`GuardRegistry`](api-reference.md#guardregistry) catalogues, the [implicit-return rules](api-reference.md#implicit_return), [method support](api-reference.md#methods) and the [integration seam](api-reference.md#integration-seam).
- [How it works](how-it-works.md): the layers, the Idunn wiring, the guard pipeline, the AST rewrite, [thread safety](how-it-works.md#thread-safety) and the full list of [limitations](how-it-works.md#limitations).
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
