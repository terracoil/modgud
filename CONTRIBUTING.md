# Contributing to modgud

The test suite checks more than behaviour. It polices the imports, runs the examples and reads the docs.

## 📦 Setup

```bash
git clone https://github.com/terracoil/modgud.git
cd modgud
poetry install --with dev
```

Without Poetry, `pip install -e . --group dev` does the same; it needs pip 25.1 or newer. Python 3.11+.

## 🧪 The gate

Run this before every pull request. It has to pass clean:

```bash
poetry run ruff check modgud/ tests/ examples/ --fix && poetry run ruff format modgud/ tests/ examples/ && poetry run mypy modgud/ examples/free_range/ && poetry run mypy examples/classy/
poetry run pytest
```

mypy runs once per example tree, since both trees share filenames.

Three checks in the default run have nothing to do with behaviour:

- `tests/test_architecture.py` walks the AST of `modgud/` and enforces the dependency table in [project.md](project.md). The app layer never imports infrastructure, and infrastructure never imports app.
- `tests/test_examples.py` runs every example in a subprocess and fails on a non-zero exit. It also checks that `examples/README.md` lists every file.
- `tests/test_docs.py` executes every `from modgud ... import` line in the docs and checks every relative link and anchor.

Functions that use implicit returns must be defined at module level in tests, because the rewrite reads source from disk. Put them in `tests/test_fixtures.py` or `tests/method_fixtures.py`.

## 🗂️ Example trees

- `examples/free_range/`: module-level functions. Exempt from the one-class-per-file and no-loose-functions rules; every other rule applies.
- `examples/classy/`: exactly one class per file and no module-level `def`. A `demo()` classmethod holds the asserts, and the file ends with `if __name__ == '__main__': XxxExample.demo()`. Each classy file has a free-range twin with the same number.
- Both: import from `modgud` and the stdlib only, 80 lines or fewer, `assert` for proof and `print` for the reader. Add new files to [examples/README.md](examples/README.md).

## 🤝 Pull requests

Branch from `main`, put tests in the same change, run the gate, open the pull request. Layering and import rules live in [project.md](project.md); arguing with the architecture test is allowed, but do it in the pull request description.
