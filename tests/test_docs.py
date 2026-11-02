"""Docs tests: every import in the docs runs, every link resolves, and the wording stays honest."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS: list[Path] = sorted(
  path
  for path in [
    REPO_ROOT / 'README.md',
    REPO_ROOT / 'CONTRIBUTING.md',
    REPO_ROOT / 'CLAUDE.md',
    REPO_ROOT / 'project.md',
    REPO_ROOT / 'examples' / 'README.md',
    *(REPO_ROOT / 'docs').rglob('*.md'),
  ]
  if path.exists()
)
USER_FACING: list[Path] = [REPO_ROOT / 'README.md', REPO_ROOT / 'docs' / 'README.md']
API_REFERENCE = REPO_ROOT / 'docs' / 'api-reference.md'
REPO_URL = 'https://github.com/terracoil/modgud/'
FENCE = re.compile(r'^```(\w*)\n(.*?)^```', re.M | re.S)
LINK = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)\)')
HEADING = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.M)
LEAF_IMPORT = re.compile(r'^\s*from modgud\.(app|domain|infrastructure)[\w.]* import', re.M)
DISHONEST = re.compile(
  r'zero[- ]?(?:runtime )?dependenc|no (?:runtime )?dependencies|dependency[- ]free|\.\[dev\]', re.I
)


class DocProbe:
  """Read one markdown file and pull out the things the tests check."""

  @staticmethod
  def code_blocks(text: str) -> list[tuple[str, str]]:
    """Return ``(language, body)`` for every fenced block."""
    return [(lang, body) for lang, body in FENCE.findall(text)]

  @staticmethod
  def prose(text: str) -> str:
    """Return the document with its fenced blocks removed."""
    return FENCE.sub('', text)

  @classmethod
  def modgud_imports(cls, text: str) -> list[str]:
    """Every ``import modgud...`` / ``from modgud... import ...`` statement in the code blocks."""
    statements: list[str] = []
    for lang, body in cls.code_blocks(text):
      if lang not in ('python', 'py', ''):
        continue
      try:
        tree = ast.parse(body)
      except SyntaxError:
        statements.extend(cls._regex_imports(body))
        continue
      for node in ast.walk(tree):
        is_modgud = (
          isinstance(node, ast.ImportFrom) and (node.module or '').split('.')[0] == 'modgud'
        ) or (
          isinstance(node, ast.Import) and any(a.name.split('.')[0] == 'modgud' for a in node.names)
        )
        if is_modgud:
          statements.append(ast.unparse(node))
    return list(dict.fromkeys(statements))

  @staticmethod
  def _regex_imports(body: str) -> list[str]:
    return re.findall(r'^\s*(?:from modgud[\w.]* import [^\n(]+|import modgud[\w.]*)$', body, re.M)

  @staticmethod
  def links(text: str) -> list[str]:
    """Every link and image target, fenced code excluded."""
    return LINK.findall(DocProbe.prose(text))

  @staticmethod
  def slug(heading: str) -> str:
    """GitHub's anchor for a heading: lower-case, punctuation and emoji dropped, spaces to hyphens."""
    cleaned = re.sub(r'[^\w\- ]', '', heading.replace('`', '').strip().lower())
    return re.sub(r' ', '-', cleaned)  # a leading emoji leaves a leading hyphen, as on GitHub

  @classmethod
  def anchors(cls, path: Path) -> set[str]:
    """Every heading slug in ``path``; duplicates get GitHub's ``-1``, ``-2`` suffixes."""
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    for heading in HEADING.findall(cls.prose(path.read_text(encoding='utf-8'))):
      base = cls.slug(heading)
      count = seen.get(base, 0)
      anchors.add(base if count == 0 else f'{base}-{count}')
      seen[base] = count + 1
    return anchors

  @classmethod
  def integration_seam_removed(cls, text: str) -> str:
    """``api-reference.md`` without its "Integration seam" section (ports are allowed there)."""
    return re.sub(
      r'^##+\s+[^\n]*Integration seam.*?(?=^##\s|\Z)', '', text, flags=re.M | re.S | re.I
    )


DOCS_WITH_IMPORTS: list[Path] = [
  doc for doc in DOCS if DocProbe.modgud_imports(doc.read_text(encoding='utf-8'))
]


class TestDocImports:
  def test_the_docs_with_imports_are_the_expected_ones(self) -> None:
    assert {doc.name for doc in DOCS_WITH_IMPORTS} >= {'README.md', 'api-reference.md'}

  @pytest.mark.parametrize('doc', DOCS_WITH_IMPORTS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
  def test_every_modgud_import_in_the_doc_runs(self, doc: Path) -> None:
    statements = DocProbe.modgud_imports(doc.read_text(encoding='utf-8'))
    result = subprocess.run(
      [sys.executable, '-c', '\n'.join(statements)],
      capture_output=True,
      text=True,
      timeout=60,
      cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f'{doc.name}:\n' + '\n'.join(statements) + '\n' + result.stderr


class TestDocLinks:
  @pytest.mark.parametrize(
    'example',
    sorted((REPO_ROOT / 'examples').glob('*/[0-9][0-9]_*.py')),
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
  )
  def test_example_see_lines_point_at_real_anchors(self, example: Path) -> None:
    targets = re.findall(r'^\s*See:\s*(\S+)', example.read_text(encoding='utf-8'), re.M)
    assert targets, 'every example names its doc anchor on a `See:` line'
    for target in targets:
      path_part, _, anchor = target.partition('#')
      resolved = (REPO_ROOT / path_part).resolve()
      assert resolved.exists(), target
      assert not anchor or anchor in DocProbe.anchors(resolved), target

  @pytest.mark.parametrize('doc', DOCS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
  def test_relative_links_and_anchors_resolve(self, doc: Path) -> None:
    broken: list[str] = []
    for target in DocProbe.links(doc.read_text(encoding='utf-8')):
      if target.startswith(('http://', 'https://', 'mailto:')):
        continue
      path_part, _, anchor = target.partition('#')
      resolved = (doc.parent / path_part).resolve() if path_part else doc
      if not resolved.exists():
        broken.append(f'{target}: missing file')
      elif anchor and resolved.suffix == '.md' and anchor not in DocProbe.anchors(resolved):
        broken.append(f'{target}: no heading with that anchor')
    assert not broken, f'{doc.relative_to(REPO_ROOT)}:\n' + '\n'.join(broken)

  def test_readme_links_are_absolute_for_pypi(self) -> None:
    offenders = [
      target
      for target in DocProbe.links((REPO_ROOT / 'README.md').read_text(encoding='utf-8'))
      if not target.startswith(('http://', 'https://', '#'))
    ]
    assert not offenders, 'README links must be absolute URLs: ' + ', '.join(offenders)

  def test_readme_repo_links_point_at_main(self) -> None:
    offenders = [
      target
      for target in DocProbe.links((REPO_ROOT / 'README.md').read_text(encoding='utf-8'))
      if target.startswith(REPO_URL) and '/blob/' in target and '/blob/main/' not in target
    ]
    assert not offenders, 'README repo links must use blob/main: ' + ', '.join(offenders)


class TestDocWording:
  @pytest.mark.parametrize('doc', USER_FACING, ids=lambda p: str(p.relative_to(REPO_ROOT)))
  def test_user_facing_docs_import_only_from_modgud(self, doc: Path) -> None:
    assert not LEAF_IMPORT.search(doc.read_text(encoding='utf-8'))

  def test_api_reference_shows_leaf_imports_only_in_the_integration_seam(self) -> None:
    text = DocProbe.integration_seam_removed(API_REFERENCE.read_text(encoding='utf-8'))
    assert not LEAF_IMPORT.search(text)

  @pytest.mark.parametrize('doc', DOCS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
  def test_no_dishonest_dependency_claims(self, doc: Path) -> None:
    hits = [m.group(0) for m in DISHONEST.finditer(doc.read_text(encoding='utf-8'))]
    assert not hits, f'{doc.relative_to(REPO_ROOT)}: {hits}'
