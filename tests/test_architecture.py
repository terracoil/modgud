"""Architecture tests: enforce modgud's layering and its fenced dependency on Idunn.

Rows of the dependency table (see ``project.md``):

- ``modgud.app`` imports ``modgud.domain.<feature>`` and ``modgud.domain.<feature>.ports``;
  from idunn only ``Invert``, plus ``Idunn`` / ``ReportMap`` in the composition root.
- ``modgud.infrastructure.adapters`` imports the domain, its ports,
  ``modgud.infrastructure.common`` and ``modgud.infrastructure.ast``; from idunn only
  ``Adapter`` and ``LifecycleEnum``.
- ``modgud.infrastructure.common`` imports ``modgud.domain.<feature>`` only; no idunn.
- ``modgud.infrastructure.ast`` imports itself and ``modgud.domain.<feature>`` only; no idunn.
  Only the adapters import it, and only as the package, never its underscore modules.
- ``modgud.domain.<feature>`` imports only its own feature; ``idunn.Port`` is allowed only in
  ``ports`` modules, and non-ports modules never import the ``ports`` subpackage (that cycle is
  why ports are imported from the 4-level path).
- Nothing outside ``modgud.infrastructure.adapters`` imports the adapters.
"""

from __future__ import annotations

import ast
import importlib
import re
import sys
from pathlib import Path

from idunn.internal import PortRegistry

PACKAGE_ROOT = Path(__file__).resolve().parent.parent / 'modgud'
COMPOSITION_ROOT = 'modgud.app.wiring'
ADAPTERS = 'modgud.infrastructure.adapters'
COMMON = 'modgud.infrastructure.common'
AST_HELPERS = 'modgud.infrastructure.ast'
DOMAIN_FEATURE = re.compile(r'^modgud\.domain\.([a-z_]+)$')
DOMAIN_FEATURE_OR_PORTS = re.compile(r'^modgud\.domain\.[a-z_]+(\.ports)?$')
IDUNN_NAMES_ALLOWED = {
  'app': {('idunn', 'Invert')},
  'adapters': {('idunn', 'Adapter'), ('idunn', 'LifecycleEnum')},
  'ports': {('idunn', 'Port')},
}
COMPOSITION_ROOT_IDUNN_NAMES = {('idunn', 'Idunn'), ('idunn.domain', 'ReportMap')}

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
    if module.startswith('modgud.app'):
      role = 'app'
    elif module.startswith(ADAPTERS):
      role = 'adapters'
    elif module.startswith(COMMON):
      role = 'common'
    elif module.startswith(AST_HELPERS):
      role = 'ast'
    elif len(parts) >= 3 and parts[1] == 'domain':
      role = 'ports' if len(parts) >= 4 and parts[3] == 'ports' else 'domain'
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
    feature_match = DOMAIN_FEATURE.match('.'.join(module.split('.')[:3]))
    own_feature: str = feature_match.group(0) if feature_match else ''
    in_own_feature: bool = bool(own_feature) and (
      target == own_feature or target.startswith(f'{own_feature}.')
    )
    allowed = False
    if role == 'app':
      allowed = target.startswith('modgud.app') or bool(DOMAIN_FEATURE_OR_PORTS.match(target))
    elif role == 'adapters':
      allowed = (
        target.startswith(ADAPTERS)
        or target in (COMMON, AST_HELPERS)
        or bool(DOMAIN_FEATURE_OR_PORTS.match(target))
      )
    elif role == 'common':
      allowed = target.startswith(COMMON) or bool(DOMAIN_FEATURE.match(target))
    elif role == 'ast':
      allowed = target.startswith(AST_HELPERS) or bool(DOMAIN_FEATURE.match(target))
    elif role == 'ports':
      allowed = in_own_feature
    elif role == 'domain':
      allowed = in_own_feature and not target.startswith(f'{own_feature}.ports')
    return [] if allowed else [f'{module} ({role}) must not import {target}']

  @classmethod
  def _idunn_violations(cls, module: str, target: str, names: tuple[str, ...]) -> list[str]:
    allowed_pairs: set[tuple[str, str]] = set(IDUNN_NAMES_ALLOWED.get(cls.role_of(module), set()))
    if module == COMPOSITION_ROOT:
      allowed_pairs |= COMPOSITION_ROOT_IDUNN_NAMES
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

  def test_idunn_is_only_constructed_in_the_composition_root(self) -> None:
    constructing = [
      ArchitectureProbe.module_of(path)
      for path in ArchitectureProbe.source_files()
      if ArchitectureProbe.idunn_constructions(path.read_text(encoding='utf-8'))
    ]
    assert constructing == [COMPOSITION_ROOT]

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
      'modgud.domain.guarded_expr.ports.guard_runtime_port': ['Port'],
      'modgud.domain.implicit_ret.ports.implicit_return_transformer_port': ['Port'],
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

  def test_no_modules_at_the_package_root_besides_init(self) -> None:
    assert ArchitectureProbe.stray_top_level_modules(PACKAGE_ROOT) == []


class TestIdunnMarkers:
  """Ports are recorded in Idunn's PortRegistry, adapters carry their marker and inherit their port."""

  def test_ports_are_marked(self) -> None:
    for module, name in (
      ('modgud.domain.guarded_expr.ports', 'GuardRuntimePort'),
      ('modgud.domain.implicit_ret.ports', 'ImplicitReturnTransformerPort'),
    ):
      port = getattr(importlib.import_module(module), name)
      assert PortRegistry.is_port(port)

  def test_adapters_are_marked_and_inherit_their_port(self) -> None:
    adapters = importlib.import_module(ADAPTERS)
    for adapter_name, port_module, port_name in (
      ('GuardRuntime', 'modgud.domain.guarded_expr.ports', 'GuardRuntimePort'),
      (
        'ImplicitReturnTransformer',
        'modgud.domain.implicit_ret.ports',
        'ImplicitReturnTransformerPort',
      ),
    ):
      adapter = getattr(adapters, adapter_name)
      port = getattr(importlib.import_module(port_module), port_name)
      assert vars(adapter).get('__idunn_adapter__') is True
      assert issubclass(adapter, port)


class TestProbeSelfChecks:
  """Each probe flags a synthetic bad input, so a green run means something."""

  def test_relative_imports_resolve_against_the_package(self) -> None:
    edges = ArchitectureProbe.edges_from_source(
      'from .wiring import Wiring\nfrom . import guarded_expression\nimport os, sys',
      'modgud.app',
      is_package=True,
    )
    assert edges == [
      ('modgud.app.wiring', ('Wiring',)),
      ('modgud.app', ('guarded_expression',)),
      ('os', ()),
      ('sys', ()),
    ]
    module_edges = ArchitectureProbe.edges_from_source(
      'from .guard_registry import GuardRegistry', f'{COMMON}.common_guards', is_package=False
    )
    assert module_edges == [(f'{COMMON}.guard_registry', ('GuardRegistry',))]

  def test_app_importing_infrastructure_is_flagged(self) -> None:
    assert ArchitectureProbe.violations(
      'modgud.app.guarded_expression', [(ADAPTERS, ('GuardRuntime',))]
    )
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [(COMMON, ('X',))])

  def test_common_importing_adapters_or_ports_is_flagged(self) -> None:
    assert ArchitectureProbe.violations(f'{COMMON}.guard_registry', [(ADAPTERS, ('X',))])
    assert ArchitectureProbe.violations(
      f'{COMMON}.guard_registry', [('modgud.domain.implicit_ret.ports', ('X',))]
    )

  def test_ast_helpers_outside_their_fence_are_flagged(self) -> None:
    rewriter = f'{AST_HELPERS}._tail_rewriter'
    transformer = f'{ADAPTERS}.implicit_return_transformer'
    assert ArchitectureProbe.violations(f'{COMMON}.guard_registry', [(AST_HELPERS, ('X',))])
    assert ArchitectureProbe.violations('modgud.app.implicit_return', [(AST_HELPERS, ('X',))])
    assert ArchitectureProbe.violations(transformer, [(rewriter, ('TailRewriter',))])
    assert ArchitectureProbe.violations(rewriter, [(ADAPTERS, ('X',))])
    assert ArchitectureProbe.violations(rewriter, [(COMMON, ('X',))])
    assert ArchitectureProbe.violations(rewriter, [('modgud.domain.implicit_ret.ports', ('X',))])
    assert ArchitectureProbe.violations(rewriter, [('idunn', ('Port',))])
    assert not ArchitectureProbe.violations(transformer, [(AST_HELPERS, ('TailRewriter',))])
    assert not ArchitectureProbe.violations(rewriter, [('modgud.domain.implicit_ret', ('X',))])
    assert not ArchitectureProbe.violations(AST_HELPERS, [(rewriter, ('TailRewriter',))])

  def test_infrastructure_importing_app_is_flagged(self) -> None:
    assert ArchitectureProbe.violations(f'{ADAPTERS}.guard_runtime', [('modgud.app', ('X',))])
    assert ArchitectureProbe.violations(f'{COMMON}.guard_registry', [('modgud.app', ('X',))])

  def test_domain_crossing_features_or_layers_is_flagged(self) -> None:
    module = 'modgud.domain.guarded_expr.types'
    assert ArchitectureProbe.violations(module, [('modgud.domain.implicit_ret', ('X',))])
    assert ArchitectureProbe.violations(module, [(COMMON, ('X',))])
    assert ArchitectureProbe.violations(module, [('modgud.domain.guarded_expr.ports', ('X',))])
    assert ArchitectureProbe.violations(module, [('modgud.domain.guarded_exprs', ('X',))])
    assert not ArchitectureProbe.violations(module, [('modgud.domain.guarded_expr', ('X',))])

  def test_idunn_outside_its_fence_is_flagged(self) -> None:
    assert ArchitectureProbe.violations('modgud.domain.guarded_expr.types', [('idunn', ('Port',))])
    assert ArchitectureProbe.violations(
      'modgud.domain.guarded_expr.ports.guard_runtime_port', [('idunn', ('Idunn',))]
    )
    assert ArchitectureProbe.violations(f'{COMMON}.common_guards', [('idunn', ('Port',))])
    assert ArchitectureProbe.violations('modgud.app.guarded_expression', [('idunn', ('Idunn',))])
    assert ArchitectureProbe.violations('modgud.app.implicit_return', [('idunn', ())])
    assert not ArchitectureProbe.violations(COMPOSITION_ROOT, [('idunn', ('Idunn',))])
    assert not ArchitectureProbe.violations(
      'modgud.domain.guarded_expr.ports.guard_runtime_port', [('idunn', ('Port',))]
    )

  def test_third_party_imports_are_flagged(self) -> None:
    assert ArchitectureProbe.violations(f'{COMMON}.common_guards', [('requests', ())])
    assert not ArchitectureProbe.violations(f'{COMMON}.common_guards', [('re', ())])

  def test_idunn_construction_is_detected(self) -> None:
    assert ArchitectureProbe.idunn_constructions('Idunn().bootstrap("x")') == 1
    assert ArchitectureProbe.idunn_constructions('from idunn import Idunn') == 0

  def test_stray_top_level_module_is_detected(self, tmp_path: Path) -> None:
    (tmp_path / '__init__.py').write_text('', encoding='utf-8')
    (tmp_path / 'modgud.py').write_text('', encoding='utf-8')
    assert ArchitectureProbe.stray_top_level_modules(tmp_path) == ['modgud.py']
