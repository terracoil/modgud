"""Architecture validation tests for LPA compliance."""

import ast
import re
from pathlib import Path
from typing import Set


class TestArchitectureCompliance:
  """Tests that verify LPA (Layered Ports Architecture) compliance."""

  @staticmethod
  def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

  @staticmethod
  def get_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    with open(file_path) as f:
      content = f.read()

    imports = set()
    try:
      tree = ast.parse(content)
      for node in ast.walk(tree):
        if isinstance(node, ast.Import):
          for alias in node.names:
            imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
          if node.module:
            imports.add(node.module)
    except SyntaxError:
      pass

    return imports

  def test_surface_layer_no_direct_domain_imports(self):
    """Test that surface layer never imports directly from domain layer."""
    project_root = self.get_project_root()
    surface_dir = project_root / 'modgud' / 'surface'

    violations = []
    for py_file in surface_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      imports = self.get_imports_from_file(py_file)
      for imp in imports:
        # Check for direct domain imports
        if imp.startswith('modgud.domain.') or imp == 'modgud.domain':
          # Verify it's not going through infrastructure
          if not imp.startswith('modgud.domain.ports'):
            violations.append(f'{py_file.name}: {imp}')

    assert not violations, (
      'Surface layer has direct domain imports (should use infrastructure gateway):\n'
      + '\n'.join(violations)
    )

  def test_adapter_naming_convention(self):
    """Test that all PUBLIC adapter classes end with 'Adapter' suffix."""
    project_root = self.get_project_root()
    adapters_dir = project_root / 'modgud' / 'infrastructure' / 'adapters'

    violations = []
    for py_file in adapters_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      # Find class definitions (skip private classes starting with _)
      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        # Skip private classes (start with _)
        if class_name.startswith('_'):
          continue
        if not class_name.endswith('Adapter'):
          violations.append(f'{py_file.name}: class {class_name}')

    assert not violations, 'Public adapter classes must end with "Adapter" suffix:\n' + '\n'.join(
      violations
    )

  def test_service_naming_convention(self):
    """Test that all service classes end with 'Service' suffix."""
    project_root = self.get_project_root()
    services_dir = project_root / 'modgud' / 'infrastructure' / 'services'

    violations = []
    for py_file in services_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      # Find class definitions
      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        # Skip private classes (starting with underscore)
        if class_name.startswith('_'):
          continue
        if not class_name.endswith('Service'):
          violations.append(f'{py_file.name}: class {class_name}')

    assert not violations, 'Service classes must end with "Service" suffix:\n' + '\n'.join(
      violations
    )

  def test_port_naming_convention(self):
    """Test that all port classes end with 'Port' suffix."""
    project_root = self.get_project_root()

    violations = []
    # Check domain ports
    domain_ports_dir = project_root / 'modgud' / 'domain' / 'ports'
    for py_file in domain_ports_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        if not class_name.endswith('Port'):
          violations.append(f'domain/{py_file.name}: class {class_name}')

    # Check infrastructure ports
    infra_ports_dir = project_root / 'modgud' / 'infrastructure' / 'ports'
    for py_file in infra_ports_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        if not class_name.endswith('Port'):
          violations.append(f'infrastructure/{py_file.name}: class {class_name}')

    assert not violations, 'Port classes must end with "Port" suffix:\n' + '\n'.join(violations)

  def test_model_naming_convention(self):
    """Test that domain model classes end with 'Model' suffix (except errors/types)."""
    project_root = self.get_project_root()
    models_dir = project_root / 'modgud' / 'domain' / 'models'

    violations = []
    # Skip errors.py and types.py as they contain grouped collections
    skip_files = {'errors.py', 'types.py', '__init__.py'}

    for py_file in models_dir.glob('*.py'):
      if py_file.name in skip_files:
        continue

      with open(py_file) as f:
        content = f.read()

      # Find class definitions
      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        if not class_name.endswith('Model'):
          violations.append(f'{py_file.name}: class {class_name}')

    assert not violations, 'Model classes must end with "Model" suffix:\n' + '\n'.join(violations)

  def test_no_infrastructure_imports_in_domain(self):
    """Test that domain layer never imports from infrastructure or surface."""
    project_root = self.get_project_root()
    domain_dir = project_root / 'modgud' / 'domain'

    violations = []
    for py_file in domain_dir.rglob('*.py'):
      imports = self.get_imports_from_file(py_file)
      for imp in imports:
        if imp.startswith('modgud.infrastructure') or imp.startswith('modgud.surface'):
          rel_path = py_file.relative_to(project_root)
          violations.append(f'{rel_path}: {imp}')

    assert not violations, (
      'Domain layer must not import from infrastructure or surface:\n' + '\n'.join(violations)
    )

  def test_no_surface_imports_in_infrastructure(self):
    """Test that infrastructure layer never imports from surface."""
    project_root = self.get_project_root()
    infrastructure_dir = project_root / 'modgud' / 'infrastructure'

    violations = []
    for py_file in infrastructure_dir.rglob('*.py'):
      imports = self.get_imports_from_file(py_file)
      for imp in imports:
        if imp.startswith('modgud.surface'):
          rel_path = py_file.relative_to(project_root)
          violations.append(f'{rel_path}: {imp}')

    assert not violations, 'Infrastructure layer must not import from surface:\n' + '\n'.join(
      violations
    )

  def test_infrastructure_gateway_exists(self):
    """Test that infrastructure __init__.py acts as gateway for surface."""
    project_root = self.get_project_root()
    gateway_file = project_root / 'modgud' / 'infrastructure' / '__init__.py'

    assert gateway_file.exists(), 'Infrastructure gateway (__init__.py) must exist'

    with open(gateway_file) as f:
      content = f.read()

    # Verify it re-exports domain types/errors
    assert 'from ..domain.models.errors import' in content, (
      'Infrastructure gateway must re-export domain errors'
    )
    assert 'from ..domain.models.types import' in content, (
      'Infrastructure gateway must re-export domain types'
    )

  def test_one_class_per_file_in_adapters(self):
    """Test that adapter files contain exactly one PUBLIC class (private helpers OK)."""
    project_root = self.get_project_root()
    adapters_dir = project_root / 'modgud' / 'infrastructure' / 'adapters'

    violations = []
    for py_file in adapters_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      # Count PUBLIC class definitions (not starting with _)
      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      public_classes = [
        match.group(1)
        for match in re.finditer(class_pattern, content, re.MULTILINE)
        if not match.group(1).startswith('_')
      ]

      if len(public_classes) > 1:
        violations.append(f'{py_file.name}: {len(public_classes)} public classes')

    assert not violations, (
      'Adapter files should contain exactly one public class (private helpers OK):\n'
      + '\n'.join(violations)
    )

  def test_one_class_per_file_in_services(self):
    """Test that service files contain exactly one PUBLIC class (private helpers OK)."""
    project_root = self.get_project_root()
    services_dir = project_root / 'modgud' / 'infrastructure' / 'services'

    violations = []
    for py_file in services_dir.glob('*.py'):
      if py_file.name == '__init__.py':
        continue

      with open(py_file) as f:
        content = f.read()

      # Count PUBLIC class definitions (not starting with _)
      class_pattern = r'^class\s+(\w+)\s*[\(:]'
      public_classes = [
        match.group(1)
        for match in re.finditer(class_pattern, content, re.MULTILINE)
        if not match.group(1).startswith('_')
      ]

      if len(public_classes) > 1:
        violations.append(f'{py_file.name}: {len(public_classes)} public classes')

    assert not violations, (
      'Service files should contain exactly one public class (private helpers OK):\n'
      + '\n'.join(violations)
    )
