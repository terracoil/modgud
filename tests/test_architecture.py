"""Architecture tests: enforce modgud's layering and its fenced dependency on Idunn.

Rows of the dependency table (see ``project.md``). An ``<owner>`` is one of the four names
directly under ``modgud.domain``: ``enums``, ``errors``, ``ports`` or ``types``.

- ``modgud.app`` imports ``modgud.domain.<owner>``; from idunn only ``Invert``. ``Idunn`` is never constructed anywhere under ``modgud/``:
  ``@Invert(bootstrap='modgud')`` on the decorators does the discovery.
- ``modgud.infrastructure.adapters`` imports ``modgud.domain.<owner>`` and
  ``modgud.infrastructure.ast``; from idunn only ``Adapter`` and ``LifecycleEnum``.
- ``modgud.infrastructure.ast`` imports itself and ``modgud.domain.<owner>`` only; no idunn.
  Only the adapters import it, and only as the package, never its underscore modules.
- ``modgud.domain.ports`` imports itself and the other three owners, never ``modgud.domain``:
  that would hang on the order of the imports in its ``__init__``. It alone may import
  ``idunn.Port``. ``enums``, ``errors`` and ``types`` import only themselves, so nothing below
  ``ports`` can reach it.
- Nothing outside ``modgud.infrastructure.adapters`` imports the adapters.
- No module imports an enclosing package (that re-enters a half-initialised ``__init__``).
- Facades: ``modgud`` imports ``modgud.app``, ``modgud.domain`` and ``modgud.domain.<owner>``;
  ``modgud.domain`` imports ``modgud.domain.<owner>``; ``modgud.infrastructure`` imports
  nothing. No facade imports idunn, and nothing inside
  ``modgud/`` imports a facade (that is what keeps cycles impossible).
"""

from __future__ import annotations

import ast
import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest
from idunn import Idunn

PACKAGE_ROOT = Path(__file__).resolve().parent.parent / 'modgud'
ROOT_PACKAGE = 'modgud'
ADAPTERS = 'modgud.infrastructure.adapters'
AST_HELPERS = 'modgud.infrastructure.ast'
ROOT_FACADE = 'modgud'
DOMAIN_FACADE = 'modgud.domain'
INFRA_FACADE = 'modgud.infrastructure'
DOMAIN_PORTS = 'modgud.domain.ports'
DOMAIN_OWNER = re.compile(r'^modgud\.domain\.(enums|errors|ports|types)$')
IDUNN_NAMES_ALLOWED = {
  'app': {('idunn', 'Invert')},
  'adapters': {('idunn', 'Adapter'), ('idunn', 'LifecycleEnum')},
  'ports': {('idunn', 'Port')},
}

Edge = tuple[str, tuple[str, ...]]  # (imported module, names pulled from it; () for `import x`)


class ArchitectureProbe:
  """Collect each module's imports and judge them against the dependency table."""

  @staticmethod
  def module_of(path: Path) -> str:
    """Dotted module name of a source file under ``modgud/``."""
    parts = list(path.relative_to(PACKAGE_ROOT.parent).with_suffix('').parts)
    return '.'.join(parts[:-1] if parts[-1] == '__init__' else parts)

  @classmethod
  def edges(cls, path: Path) -> list[Edge]:
    """Return the imports made anywhere in the file, with relative imports resolved."""
    return cls.edges_from_source(
      path.read_text(encoding='utf-8'), cls.module_of(path), path.name == '__init__.py'
    )

  @staticmethod
  def edges_from_source(source: str, module: str, is_package: bool) -> list[Edge]:
    """Return the imports ``source`` makes when it is ``module`` (a package if ``is_package``)."""
    package: list[str] = module.split('.') if is_package else module.split('.')[:-1]
    edges: list[Edge] = []
    for node in ast.walk(ast.parse(source)):
      if isinstance(node, ast.Import):
        edges.extend((alias.name, ()) for alias in node.names)
      elif isinstance(node, ast.ImportFrom):
        base: list[str] = package[: len(package) - node.level + 1] if node.level else []
        target: str = '.'.join([*base, *(node.module.split('.') if node.module else [])])
        edges.append((target, tuple(alias.name for alias in node.names)))
    return edges

  @staticmethod
  def role_of(module: str) -> str:
    """Which row of the dependency table governs ``module``."""
    parts: list[str] = module.split('.')
    role = 'container'
    if module == ROOT_FACADE:
      role = 'facade'
    elif module == DOMAIN_FACADE:
      role = 'domain_facade'
    elif module == INFRA_FACADE:
      role = 'infrastructure_facade'
    elif module.startswith('modgud.app'):
      role = 'app'
    elif module.startswith(ADAPTERS):
      role = 'adapters'
    elif module.startswith(AST_HELPERS):
      role = 'ast'
    elif len(parts) >= 3 and parts[1] == 'domain':
      role = 'ports' if parts[2] == 'ports' else 'domain'
    return role

  @classmethod
  def violations(cls, module: str, edges: list[Edge]) -> list[str]:
    """Every edge of ``module`` the dependency table forbids, as readable messages."""
    found: list[str] = []
    for target, names in edges:
      top: str = target.split('.')[0]
      if top == 'modgud':
        found.extend(cls._internal_violations(module, target))
      elif top == 'idunn':
        found.extend(cls._idunn_violations(module, target, names))
      elif top not in sys.stdlib_module_names:
        found.append(f'{module} imports third-party {target}')
    return found

  @staticmethod
  def idunn_constructions(source: str) -> int:
    """Count ``Idunn(...)`` calls in ``source``."""
    return sum(
      1
      for node in ast.walk(ast.parse(source))
      if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'Idunn'
    )

  @staticmethod
  def source_files() -> list[Path]:
    """Every source file of the ``modgud`` package."""
    return sorted(PACKAGE_ROOT.rglob('*.py'))

  @staticmethod
  def stray_top_level_modules(root: Path) -> list[str]:
    """Modules directly under ``root`` other than ``__init__.py``."""
    return sorted(path.name for path in root.glob('*.py') if path.name != '__init__.py')

  @classmethod
  def _internal_violations(cls, module: str, target: str) -> list[str]:
    role: str = cls.role_of(module)
    own_package: str = '.'.join(module.split('.')[:3])
    in_own_package: bool = target == own_package or target.startswith(f'{own_package}.')
    is_ancestor: bool = module.startswith(f'{target}.')
    allowed = False
    if is_ancestor:
      allowed = False  # importing an enclosing package re-enters a half-initialised __init__
    elif role == 'facade':
      allowed = target in ('modgud.app', DOMAIN_FACADE) or bool(DOMAIN_OWNER.match(target))
    elif role == 'domain_facade':
      allowed = bool(DOMAIN_OWNER.match(target))
    elif role == 'app':
      allowed = target.startswith('modgud.app') or bool(DOMAIN_OWNER.match(target))
    elif role == 'adapters':
      allowed = (
        target.startswith(ADAPTERS) or target == AST_HELPERS or bool(DOMAIN_OWNER.match(target))
      )
    elif role == 'ast':
      allowed = target.startswith(AST_HELPERS) or bool(DOMAIN_OWNER.match(target))
    elif role == 'ports':
      allowed = in_own_package or bool(DOMAIN_OWNER.match(target))
    elif role == 'domain':
      allowed = in_own_package
    return [] if allowed else [f'{module} ({role}) must not import {target}']

  @classmethod
  def _idunn_violations(cls, module: str, target: str, names: tuple[str, ...]) -> list[str]:
    allowed_pairs: set[tuple[str, str]] = IDUNN_NAMES_ALLOWED.get(cls.role_of(module), set())
    pairs: list[tuple[str, str]] = [(target, name) for name in names] or [(target, '*module*')]
    return [
      f'{module} must not import {name} from {source}'
      for source, name in pairs
      if (source, name) not in allowed_pairs
    ]


class TestDependencyTable:
  """The real ``modgud/`` tree obeys every row of the dependency table."""

  def test_every_import_respects_the_dependency_table(self) -> None:
    violations = [
      message
      for path in ArchitectureProbe.source_files()
      for message in ArchitectureProbe.violations(
        ArchitectureProbe.module_of(path), ArchitectureProbe.edges(path)
      )
    ]
    assert not violations, 'Dependency violations:\n' + '\n'.join(violations)

  def test_idunn_is_never_constructed_inside_modgud(self) -> None:
    constructing = [
      ArchitectureProbe.module_of(path)
      for path in ArchitectureProbe.source_files()
      if ArchitectureProbe.idunn_constructions(path.read_text(encoding='utf-8'))
    ]
    assert constructing == []

  def test_domain_imports_only_port_from_idunn_and_only_in_ports_modules(self) -> None:
    idunn_importers = {
      ArchitectureProbe.module_of(path): sorted(
        name
        for target, names in ArchitectureProbe.edges(path)
        if target.split('.')[0] == 'idunn'
        for name in names
      )
      for path in sorted((PACKAGE_ROOT / 'domain').rglob('*.py'))
    }
    importers = {module: names for module, names in idunn_importers.items() if names}
    assert importers == {
      'modgud.domain.ports.guard_port': ['Port'],
      'modgud.domain.ports.implicit_return_port': ['Port'],
    }

  def test_only_the_adapters_package_imports_the_adapters(self) -> None:
    importers = [
      ArchitectureProbe.module_of(path)
      for path in ArchitectureProbe.source_files()
      if not ArchitectureProbe.module_of(path).startswith(ADAPTERS)
      and any(target.startswith(ADAPTERS) for target, _ in ArchitectureProbe.edges(path))
    ]
    assert not importers

  def test_only_the_adapters_import_the_ast_helpers(self) -> None:
    importers = [
      ArchitectureProbe.module_of(path)
      for path in ArchitectureProbe.source_files()
      if not ArchitectureProbe.module_of(path).startswith((ADAPTERS, AST_HELPERS))
      and any(target.startswith(AST_HELPERS) for target, _ in ArchitectureProbe.edges(path))
    ]
    assert not importers

  @pytest.mark.parametrize(
    'module', [ArchitectureProbe.module_of(path) for path in ArchitectureProbe.source_files()]
  )
  def test_every_module_imports_first_in_a_fresh_process(self, module: str) -> None:
    result = subprocess.run(
      [sys.executable, '-c', f'import {module}'], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr

  def test_no_modules_at_the_package_root_besides_init(self) -> None:
    assert ArchitectureProbe.stray_top_level_modules(PACKAGE_ROOT) == []


class TestIdunnMarkers:
  """Idunn's bootstrap report (its public surface) lists both ports and both adapters."""

  def test_ports_are_registered(self) -> None:
    registered = set(Idunn().bootstrap(ROOT_PACKAGE)['registered_ports'])
    for module, name in (
      ('modgud.domain.ports.guard_port', 'GuardPort'),
      ('modgud.domain.ports.implicit_return_port', 'ImplicitReturnPort'),
    ):
      assert f'{module}.{name}' in registered

  def test_adapters_are_registered_and_inherit_their_port(self) -> None:
    registered = set(Idunn().bootstrap(ROOT_PACKAGE)['registered_adapters'])
    adapters = importlib.import_module(ADAPTERS)
    for adapter_name, port_module, port_name in (
      ('GuardAdapter', DOMAIN_PORTS, 'GuardPort'),
      ('ImplicitReturnAdapter', DOMAIN_PORTS, 'ImplicitReturnPort'),
    ):
      adapter = getattr(adapters, adapter_name)
      port = getattr(importlib.import_module(port_module), port_name)
      assert f'{adapter.__module__}.{adapter_name}' in registered
      assert issubclass(adapter, port)


class TestProbeSelfChecks:
  """Each probe flags a synthetic bad input, so a green run means something."""

  def test_relative_imports_resolve_against_the_package(self) -> None:
    edges = ArchitectureProbe.edges_from_source(
      'from .method_descriptors import MethodDescriptors\nfrom . import guarded_expression\nimport os, sys',
      'modgud.app',
      is_package=True,
    )
    assert edges == [
      ('modgud.app.method_descriptors', ('MethodDescriptors',)),
      ('modgud.app', ('guarded_expression',)),
      ('os', ()),
      ('sys', ()),
    ]
    module_edges = ArchitectureProbe.edges_from_source(
      'from .guard_registry import GuardRegistry', 'modgud.app.common_guards', is_package=False
    )
    assert module_edges == [('modgud.app.guard_registry', ('GuardRegistry',))]

  def test_app_importing_infrastructure_is_flagged(self) -> None:
    for module in ('guarded_expression', 'common_guards', 'guard_registry'):
      for target in (ADAPTERS, AST_HELPERS, INFRA_FACADE):
        assert ArchitectureProbe.violations(f'modgud.app.{module}', [(target, ('X',))])

  def test_ast_helpers_outside_their_fence_are_flagged(self) -> None:
    rewriter = f'{AST_HELPERS}._tail_rewriter'
    adapter = f'{ADAPTERS}.implicit_return_adapter'
    assert ArchitectureProbe.violations('modgud.app.implicit_return', [(AST_HELPERS, ('X',))])
    assert ArchitectureProbe.violations(adapter, [(rewriter, ('TailRewriter',))])
    assert ArchitectureProbe.violations(rewriter, [(ADAPTERS, ('X',))])
    assert ArchitectureProbe.violations(rewriter, [('modgud.app', ('X',))])
    assert ArchitectureProbe.violations(rewriter, [(f'{DOMAIN_PORTS}.guard_port', ('X',))])
    assert ArchitectureProbe.violations(rewriter, [('idunn', ('Port',))])
    assert not ArchitectureProbe.violations(adapter, [(AST_HELPERS, ('TailRewriter',))])
    assert not ArchitectureProbe.violations(rewriter, [('modgud.domain.errors', ('X',))])
    assert not ArchitectureProbe.violations(AST_HELPERS, [(rewriter, ('TailRewriter',))])

  def test_facade_edges_are_fenced(self) -> None:
    for target in (
      ADAPTERS,
      'modgud.app.guarded_expression',
      f'{DOMAIN_PORTS}.guard_port',
      INFRA_FACADE,
      AST_HELPERS,
    ):
      assert ArchitectureProbe.violations(ROOT_FACADE, [(target, ('X',))])
    for target in (f'{DOMAIN_PORTS}.guard_port', 'modgud.app'):
      assert ArchitectureProbe.violations(DOMAIN_FACADE, [(target, ('X',))])
    for target in (ADAPTERS, AST_HELPERS, 'modgud.app'):
      assert ArchitectureProbe.violations(INFRA_FACADE, [(target, ('X',))])
    for facade in (ROOT_FACADE, DOMAIN_FACADE, INFRA_FACADE):
      assert ArchitectureProbe.violations(facade, [('idunn', ('Invert',))])
    for target in (
      'modgud.app',
      DOMAIN_FACADE,
      'modgud.domain.errors',
    ):
      assert not ArchitectureProbe.violations(ROOT_FACADE, [(target, ('X',))])
    assert not ArchitectureProbe.violations(DOMAIN_FACADE, [('modgud.domain.errors', ('X',))])

  def test_inner_modules_importing_a_facade_are_flagged(self) -> None:
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [(ROOT_FACADE, ('X',))])
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [(DOMAIN_FACADE, ('X',))])
    assert ArchitectureProbe.violations('modgud.domain.types', [(DOMAIN_FACADE, ('X',))])
    assert ArchitectureProbe.violations('modgud.app.guard_registry', [(INFRA_FACADE, ('X',))])
    assert ArchitectureProbe.violations(f'{ADAPTERS}.guard_adapter', [(ROOT_FACADE, ('X',))])

  def test_importing_an_ancestor_package_is_flagged(self) -> None:
    enum_module = 'modgud.domain.enums.guard_failure_enum'
    assert ArchitectureProbe.violations(enum_module, [(DOMAIN_FACADE, ('X',))])
    assert ArchitectureProbe.violations(enum_module, [('modgud.domain.enums', ('X',))])
    assert ArchitectureProbe.violations(f'{AST_HELPERS}._tail_rewriter', [(AST_HELPERS, ('X',))])
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [('modgud.app', ('X',))])
    assert not ArchitectureProbe.violations(
      'modgud.app', [('modgud.app.method_descriptors', ('MethodDescriptors',))]
    )

  def test_infrastructure_importing_app_is_flagged(self) -> None:
    assert ArchitectureProbe.violations(f'{ADAPTERS}.guard_adapter', [('modgud.app', ('X',))])
    assert ArchitectureProbe.violations(f'{AST_HELPERS}._tail_rewriter', [('modgud.app', ('X',))])

  def test_a_port_importing_an_enclosing_package_is_flagged(self) -> None:
    port = f'{DOMAIN_PORTS}.guard_port'
    for target in (DOMAIN_FACADE, DOMAIN_PORTS):
      assert ArchitectureProbe.violations(port, [(target, ('X',))])
    for target in ('modgud.domain.enums', 'modgud.domain.errors', 'modgud.domain.types'):
      assert not ArchitectureProbe.violations(port, [(target, ('X',))])

  def test_ports_are_taken_from_the_ports_package(self) -> None:
    for module in (ROOT_FACADE, 'modgud.app.guarded_expression', f'{ADAPTERS}.guard_adapter'):
      assert ArchitectureProbe.violations(module, [(f'{DOMAIN_PORTS}.guard_port', ('GuardPort',))])
      assert not ArchitectureProbe.violations(module, [(DOMAIN_PORTS, ('GuardPort',))])

  def test_passive_owners_never_import_ports(self) -> None:
    for module in ('modgud.domain.types', 'modgud.domain.errors.guard_clause_error'):
      assert ArchitectureProbe.violations(module, [(DOMAIN_PORTS, ('X',))])
    assert not ArchitectureProbe.violations(DOMAIN_PORTS, [(f'{DOMAIN_PORTS}.guard_port', ('X',))])

  def test_domain_crossing_owners_or_layers_is_flagged(self) -> None:
    module = 'modgud.domain.types'
    assert ArchitectureProbe.violations(module, [('modgud.domain.errors', ('X',))])
    assert ArchitectureProbe.violations(module, [('modgud.app', ('X',))])
    assert ArchitectureProbe.violations(module, [('modgud.domain.typesx', ('X',))])
    assert ArchitectureProbe.violations(module, [(DOMAIN_FACADE, ('X',))])  # ancestor
    assert not ArchitectureProbe.violations(
      'modgud.domain.errors.missing_implicit_return_error',
      [('modgud.domain.errors.implicit_return_error', ('ImplicitReturnError',))],
    )

  def test_only_the_four_owners_are_importable_targets(self) -> None:
    for retired in ('modgud.domain.guarded_expr', 'modgud.domain.implicit_ret'):
      assert ArchitectureProbe.violations('modgud.app.guard_registry', [(retired, ('X',))])

  def test_idunn_outside_its_fence_is_flagged(self) -> None:
    assert ArchitectureProbe.violations('modgud.domain.types', [('idunn', ('Port',))])
    assert ArchitectureProbe.violations(f'{DOMAIN_PORTS}.guard_port', [('idunn', ('Idunn',))])
    assert ArchitectureProbe.violations('modgud.app.common_guards', [('idunn', ('Port',))])
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [('idunn', ('Idunn',))])
    assert ArchitectureProbe.violations('modgud.app.implicit_return', [('idunn', ())])
    assert ArchitectureProbe.violations('modgud.app.implicit_return', [('idunn', ('ReportMap',))])
    assert not ArchitectureProbe.violations(
      'modgud.app.guarded_expression', [('idunn', ('Invert',))]
    )
    assert not ArchitectureProbe.violations(f'{DOMAIN_PORTS}.guard_port', [('idunn', ('Port',))])

  def test_third_party_imports_are_flagged(self) -> None:
    assert ArchitectureProbe.violations('modgud.app.common_guards', [('requests', ())])
    assert not ArchitectureProbe.violations('modgud.app.common_guards', [('re', ())])

  def test_idunn_construction_is_detected(self) -> None:
    assert ArchitectureProbe.idunn_constructions('Idunn().bootstrap("x")') == 1
    assert ArchitectureProbe.idunn_constructions('from idunn import Idunn') == 0

  def test_stray_top_level_module_is_detected(self, tmp_path: Path) -> None:
    (tmp_path / '__init__.py').write_text('', encoding='utf-8')
    (tmp_path / 'modgud.py').write_text('', encoding='utf-8')
    assert ArchitectureProbe.stray_top_level_modules(tmp_path) == ['modgud.py']
