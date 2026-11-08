"""Run every example as a script, and keep the examples index and the two trees in step."""

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
EXAMPLES_DIR: Path = REPO_ROOT / 'examples'
EXAMPLES: list[Path] = sorted(EXAMPLES_DIR.glob('*/[0-9][0-9]_*.py'))
CLASSY: list[Path] = [path for path in EXAMPLES if path.parent.name == 'classy']


def example_id(path: Path) -> str:
  """Name a parametrized case after the example's tree and file."""
  return f'{path.parent.name}/{path.name}'


class TestExamples:
  @pytest.mark.parametrize('path', EXAMPLES, ids=example_id)
  def test_example_runs_cleanly(self, path: Path) -> None:
    completed: subprocess.CompletedProcess[str] = subprocess.run(
      [sys.executable, str(path)], capture_output=True, text=True, timeout=30, cwd=REPO_ROOT
    )
    assert completed.returncode == 0, completed.stderr

  def test_index_lists_every_example(self) -> None:
    readme: str = (EXAMPLES_DIR / 'README.md').read_text()
    listed: set[str] = set(re.findall(r'\(((?:free_range|classy)/\d\d_\w+\.py)\)', readme))
    on_disk: set[str] = {path.relative_to(EXAMPLES_DIR).as_posix() for path in EXAMPLES}
    assert on_disk, 'no examples found'
    assert listed == on_disk

  def test_every_classy_example_has_a_free_range_twin(self) -> None:
    orphans: list[str] = [
      path.name for path in CLASSY if not (EXAMPLES_DIR / 'free_range' / path.name).is_file()
    ]
    assert CLASSY and not orphans

  @pytest.mark.parametrize('path', CLASSY, ids=example_id)
  def test_classy_examples_obey_the_class_rules(self, path: Path) -> None:
    tree: ast.Module = ast.parse(path.read_text())
    classes: list[str] = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    loose: list[str] = [
      node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert len(classes) == 1, f'expected exactly one class, found {classes}'
    assert not loose, f'module-level functions: {loose}'
