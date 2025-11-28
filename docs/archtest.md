# ArchGuard: Python Architecture Verification Library - Design Document

## Executive Summary

This document outlines the design and implementation plan for **ArchGuard**, a standalone Python library for architecture verification and governance. ArchGuard will provide ArchUnit-style capabilities for Python projects, enabling automated enforcement of architectural constraints, dependency rules, and design patterns. While initially inspired by the needs of the modgud project, ArchGuard is designed as a general-purpose tool suitable for any Python codebase.

## 1. Market Analysis & Positioning

### 1.1 Current Python Architecture Verification Landscape

The Python ecosystem currently lacks a comprehensive, mature architecture verification tool comparable to ArchUnit for Java. Existing solutions include:

1. **import-linter**:
   - **Strengths**: Mature, actively maintained, good CI/CD integration
   - **Limitations**: Limited to import rules, no class-level analysis, no archetype validation
   - **Use case**: Basic layer enforcement

2. **archunit-python**:
   - **Status**: Incomplete port, limited maintenance
   - **Limitations**: Poor documentation, missing features, uncertain future

3. **pylint plugins**:
   - **Strengths**: Extensible, widely adopted
   - **Limitations**: Focused on code style, not architecture patterns

4. **Manual code reviews**:
   - **Reality**: Most Python projects rely solely on manual architecture enforcement
   - **Problems**: Inconsistent, time-consuming, error-prone

### 1.2 The Gap in the Market

Python projects need a tool that can:
- Enforce architectural patterns (Clean, Hexagonal, Custom, Layered, etc.)
- Detect and prevent architectural drift
- Validate package structures and naming conventions
- Integrate seamlessly with modern Python workflows
- Support custom rules for project-specific needs
- Provide clear, actionable feedback

### 1.3 ArchGuard's Value Proposition

ArchGuard fills this gap by providing:

1. **Comprehensive Analysis**: Beyond imports - class dependencies, package structure, naming patterns
2. **Pattern Support**: Pre-built support for common architectures (Clean, Hexagonal, DDD, Layered)
3. **Extensibility**: Plugin system for custom rules and patterns
4. **Developer Experience**: Clear error messages, auto-fix capabilities, IDE integration
5. **Python-Native**: Built for Python's unique features and idioms
6. **Zero-Config Start**: Sensible defaults with progressive customization

## 2. Core Requirements & Design Principles

### 2.1 Design Principles

1. **Zero-to-Hero Experience**: Work out of the box with sensible defaults, progressively customizable
2. **Architecture-Agnostic**: Support any architecture pattern, not just one style
3. **Fast & Accurate**: AST-based analysis for speed and precision
4. **Developer-Friendly**: Clear error messages, suggested fixes, helpful documentation
5. **Extensible**: Plugin architecture for custom rules and patterns
6. **CI/CD Ready**: First-class support for automation and toolchain integration

### 2.2 Core Capabilities

1. **Dependency Analysis Engine**:
   - AST-based import extraction
   - Class and function dependency mapping
   - Package hierarchy analysis
   - Circular dependency detection (configurable levels)
   - Dynamic import handling

2. **Architecture Pattern Support**:
   - **Clean Architecture**: Concentric layer validation
   - **Hexagonal/Ports & Adapters**: Port/adapter boundary enforcement
   - **Layered Architecture**: Directional dependency rules
   - **Domain-Driven Design**: Bounded context isolation
   - **Microservice**: Inter-service dependency rules
   - **Custom Patterns**: Define your own via plugins

3. **Rule Types**:
   - **Import Rules**: Control what can import what
   - **Naming Conventions**: Package, module, class naming patterns
   - **Structure Rules**: Required/forbidden directories and files
   - **Archetype Validation**: Ensure packages follow expected patterns
   - **Complexity Rules**: Limit coupling, cohesion metrics
   - **Custom Rules**: Python-based rule definitions

4. **Integration Points**:
   - CLI tool for local development
   - Pre-commit hooks
   - CI/CD integrations (GitHub Actions, GitLab CI, etc.)
   - IDE plugins (VS Code, PyCharm)
   - Python API for programmatic use

## 3. ArchGuard Library Architecture

### 3.1 Package Structure

```
archguard/
├── __init__.py           # Public API exports
├── __main__.py          # CLI entry point
│
├── core/                # Core analysis engine
│   ├── __init__.py
│   ├── analyzer.py      # AST-based dependency analyzer
│   ├── graph.py         # Dependency graph structures
│   ├── visitor.py       # AST visitor implementations
│   └── models.py        # Core data models
│
├── rules/               # Rule definitions and engine
│   ├── __init__.py
│   ├── base.py         # Abstract rule interfaces
│   ├── imports.py      # Import rule implementations
│   ├── naming.py       # Naming convention rules
│   ├── structure.py    # Structure validation rules
│   ├── complexity.py   # Complexity metrics rules
│   └── registry.py     # Rule registration system
│
├── patterns/           # Architecture pattern support
│   ├── __init__.py
│   ├── clean.py       # Clean Architecture rules
│   ├── hexagonal.py   # Hexagonal Architecture rules
│   ├── layered.py     # Layered Architecture rules
│   ├── ddd.py         # Domain-Driven Design rules
│   └── custom.py      # Custom pattern framework
│
├── config/            # Configuration management
│   ├── __init__.py
│   ├── loader.py      # Config file loading (YAML, TOML, Python)
│   ├── schema.py      # Configuration schema validation
│   └── defaults.py    # Default configurations
│
├── reporting/         # Violation reporting
│   ├── __init__.py
│   ├── console.py     # Terminal output formatting
│   ├── junit.py       # JUnit XML reports
│   ├── json.py        # JSON report format
│   └── html.py        # HTML report generation
│
├── cli/               # Command-line interface
│   ├── __init__.py
│   ├── main.py        # Main CLI application
│   ├── commands.py    # CLI command definitions
│   └── utils.py       # CLI utilities
│
├── plugins/           # Plugin system
│   ├── __init__.py
│   ├── base.py        # Plugin interfaces
│   ├── loader.py      # Plugin discovery and loading
│   └── examples/      # Example plugins
│
└── integrations/      # Third-party integrations
    ├── __init__.py
    ├── precommit.py   # Pre-commit hook support
    ├── pytest.py      # Pytest plugin
    └── ide/           # IDE integrations
```

### 3.2 Core Components Design

#### 3.2.1 Dependency Analyzer
```python
# archguard/core/analyzer.py
from ast import AST
from pathlib import Path
from typing import Dict, Set, List

class DependencyAnalyzer:
    """Core dependency analysis engine."""

    def analyze_project(self, root: Path) -> ProjectAnalysis:
        """Analyze entire Python project."""
        pass

    def analyze_module(self, path: Path) -> ModuleAnalysis:
        """Analyze single Python module."""
        pass

    def extract_imports(self, tree: AST) -> List[Import]:
        """Extract all imports from AST."""
        pass

    def build_dependency_graph(self, analysis: ProjectAnalysis) -> DependencyGraph:
        """Build complete dependency graph."""
        pass
```

#### 3.2.2 Rule Engine
```python
# archguard/rules/base.py
from abc import ABC, abstractmethod
from typing import List, Optional

class Rule(ABC):
    """Base class for all architecture rules."""

    @abstractmethod
    def check(self, context: AnalysisContext) -> List[Violation]:
        """Check rule against analysis context."""
        pass

    @abstractmethod
    def can_fix(self, violation: Violation) -> bool:
        """Determine if violation can be auto-fixed."""
        pass

    @abstractmethod
    def fix(self, violation: Violation) -> Optional[Fix]:
        """Generate fix for violation if possible."""
        pass

class RuleSet:
    """Collection of rules that work together."""

    def __init__(self, name: str, rules: List[Rule]):
        self.name = name
        self.rules = rules

    def check_all(self, context: AnalysisContext) -> List[Violation]:
        """Run all rules in the set."""
        violations = []
        for rule in self.rules:
            violations.extend(rule.check(context))
        return violations
```

#### 3.2.3 Pattern Support
```python
# archguard/patterns/clean.py
from archguard.patterns.base import ArchitecturePattern
from archguard.rules import ImportRule, NamingRule

class CleanArchitecture(ArchitecturePattern):
    """Clean Architecture pattern implementation."""

    LAYERS = ['entities', 'use_cases', 'adapters', 'frameworks']

    def __init__(self, **config):
        super().__init__('clean', **config)
        self.setup_rules()

    def setup_rules(self):
        """Configure Clean Architecture rules."""
        # Entities can't depend on anything
        self.add_rule(ImportRule(
            source='*.entities.*',
            forbidden=['*.use_cases.*', '*.adapters.*', '*.frameworks.*']
        ))

        # Use cases can only depend on entities
        self.add_rule(ImportRule(
            source='*.use_cases.*',
            allowed=['*.entities.*'],
            forbidden=['*.adapters.*', '*.frameworks.*']
        ))

        # ... more rules
```

## 4. Configuration & Usage

### 4.1 Configuration Formats

ArchGuard supports multiple configuration formats for maximum flexibility:

#### 4.1.1 YAML Configuration (Recommended)
```yaml
# .archguard.yaml
version: "1.0"

# Use a pre-defined architecture pattern
pattern: clean  # or: hexagonal, layered, ddd, microservice

# Override or extend pattern rules
layers:
  entities:
    allowed_imports: []  # Can't import anything
  use_cases:
    allowed_imports: ["entities"]
  adapters:
    allowed_imports: ["entities", "use_cases"]
  frameworks:
    allowed_imports: ["entities", "use_cases", "adapters"]

# Custom import rules
import_rules:
  - source: "myapp.api.*"
    forbidden: ["myapp.database.*"]  # API can't directly access DB

  - source: "myapp.*.tests.*"
    allowed: ["*"]  # Tests can import anything

# Naming conventions
naming:
  packages:
    - pattern: "*.models"
      must_contain: ["model", "entity", "dto"]

  classes:
    - pattern: "*Repository"
      must_inherit: ["BaseRepository", "ABC"]

# Circular dependency settings
circular_dependencies:
  check_packages: true
  check_classes: true
  check_functions: false  # Optional, can be expensive

# Reporting
reporting:
  format: console  # console, json, junit, html
  verbose: true
  max_violations: 50  # Stop after N violations

# Plugins
plugins:
  - mycompany.archguard.plugins.SecurityRules
  - mycompany.archguard.plugins.PerformanceRules
```

#### 4.1.2 TOML Configuration
```toml
# .archguard.toml
version = "1.0"
pattern = "layered"

[layers]
presentation = ["application", "domain", "infrastructure"]
application = ["domain", "infrastructure"]
domain = ["infrastructure"]
infrastructure = []

[[import_rules]]
source = "myapp.web.*"
forbidden = ["myapp.db.*"]

[naming.packages]
"*.repositories" = { type = "repository", suffix = "Repository" }
"*.services" = { type = "service", suffix = "Service" }
```

#### 4.1.3 Python Configuration
```python
# .archguard.py
from archguard import Config, LayeredPattern, ImportRule, NamingRule

config = Config(
    pattern=LayeredPattern(
        layers={
            'web': ['service', 'repository', 'model'],
            'service': ['repository', 'model'],
            'repository': ['model'],
            'model': []
        }
    ),

    rules=[
        ImportRule(
            source='myapp.web.*',
            forbidden=['myapp.repository.*']
        ),

        NamingRule(
            pattern='*Controller',
            must_be_in=['myapp.web.controllers']
        )
    ],

    # Use Python for dynamic configuration
    exclude_paths=[
        'tests/',
        'migrations/',
        '__pycache__/',
        '.venv/'
    ] + get_generated_paths()  # Dynamic exclusions
)
```

### 4.2 CLI Usage

```bash
# Install ArchGuard
pip install archguard

# Quick start - analyze with auto-detected pattern
archguard

# Specify configuration file
archguard --config .archguard.yaml

# Run with specific pattern (no config file needed)
archguard --pattern clean

# Generate configuration from existing code
archguard init --analyze

# Check specific paths
archguard src/ lib/

# Output formats
archguard --format json > violations.json
archguard --format junit > test-results.xml
archguard --format html > report.html

# Fix violations (where possible)
archguard --fix

# Strict mode - fail on any violation
archguard --strict

# Watch mode - run on file changes
archguard --watch

# Show dependency graph
archguard --graph
archguard --graph --format dot > deps.dot
```

### 4.3 Python API Usage

```python
from archguard import ArchGuard, CleanArchitecture, ImportRule

# Quick check with pre-defined pattern
guard = ArchGuard(pattern=CleanArchitecture())
violations = guard.check('src/')

# Custom configuration
guard = ArchGuard()
guard.add_rule(ImportRule(
    source='myapp.api.*',
    forbidden=['myapp.database.*']
))

# Check and get detailed results
result = guard.analyze('src/')
print(f"Found {len(result.violations)} violations")
for violation in result.violations:
    print(f"- {violation.rule}: {violation.message}")
    print(f"  File: {violation.file}:{violation.line}")

# Auto-fix violations
for violation in result.violations:
    if violation.can_fix:
        violation.apply_fix()

# Export results
result.export('violations.json', format='json')
result.export('report.html', format='html')
```

### 4.4 Integration Examples

#### 4.4.1 Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/archguard/archguard-python
    rev: v1.0.0
    hooks:
      - id: archguard
        args: ['--config', '.archguard.yaml', '--strict']
```

#### 4.4.2 GitHub Actions
```yaml
# .github/workflows/architecture.yml
name: Architecture Check

on: [push, pull_request]

jobs:
  archguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install ArchGuard
        run: pip install archguard

      - name: Run Architecture Checks
        run: archguard --config .archguard.yaml --format junit > test-results.xml

      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results.xml
```

#### 4.4.3 Pytest Integration
```python
# conftest.py
import pytest
from archguard import ArchGuard

@pytest.fixture(scope="session")
def architecture_guard():
    return ArchGuard(config='.archguard.yaml')

def test_architecture(architecture_guard):
    """Ensure architecture rules are followed."""
    violations = architecture_guard.check('src/')
    assert not violations, f"Architecture violations: {violations}"
```

#### 4.4.4 Integration with Modgud
```yaml
# modgud/.archguard.yaml
version: "1.0"
pattern: layered

layers:
  app:
    path: "modgud/app"
    allowed_imports: ["modgud.infrastructure", "modgud.domain", "modgud.util"]

  infrastructure:
    path: "modgud/infrastructure"
    allowed_imports: ["modgud.domain", "modgud.util"]

  domain:
    path: "modgud/domain"
    allowed_imports: ["modgud.util"]

  util:
    path: "modgud/util"
    allowed_imports: []  # Leaf layer

import_rules:
  - source: "modgud.domain.*"
    forbidden: ["modgud.app.*", "modgud.infrastructure.*"]
    reason: "Domain must not depend on outer layers"

naming:
  classes:
    - pattern: "*Protocol"
      must_be_in: ["*.protocols", "*.ports"]

    - pattern: "*Error"
      must_be_in: ["*.exceptions", "*.errors"]
```

## 5. Plugin System

### 5.1 Plugin Architecture

```python
# archguard/plugins/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class ArchGuardPlugin(ABC):
    """Base class for all ArchGuard plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def get_rules(self) -> List[Rule]:
        """Return list of rules provided by this plugin."""
        pass

    def get_patterns(self) -> Dict[str, ArchitecturePattern]:
        """Return architecture patterns provided by this plugin."""
        return {}

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure plugin with user settings."""
        pass
```

### 5.2 Example Plugin

```python
# mycompany/archguard_plugins/domain_rules.py
from archguard.plugins import ArchGuardPlugin
from archguard.rules import Rule, ImportRule, NamingRule

class DomainDrivenDesignPlugin(ArchGuardPlugin):
    """Plugin for Domain-Driven Design architecture rules."""

    name = "ddd-rules"
    version = "1.0.0"

    def get_rules(self) -> List[Rule]:
        return [
            # Aggregates should not depend on other aggregates
            ImportRule(
                source="*.domain.aggregates.*",
                forbidden=["*.domain.aggregates.*"],
                allow_same_module=True
            ),

            # Value objects must be immutable
            ImmutabilityRule(
                pattern="*.domain.value_objects.*",
                require_frozen=True
            ),

            # Domain events must inherit from DomainEvent
            InheritanceRule(
                pattern="*.domain.events.*",
                must_inherit=["DomainEvent"]
            ),

            # Repositories must be interfaces
            InterfaceRule(
                pattern="*.domain.repositories.*",
                must_be_protocol=True
            )
        ]
```

## 6. Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-2)
1. **Project Setup**
   - Create GitHub repository
   - Set up Poetry project structure
   - Configure CI/CD pipeline
   - Create documentation skeleton

2. **Core Analysis Engine**
   - Implement AST-based dependency analyzer
   - Build dependency graph structures
   - Create module and class visitors
   - Add import extraction logic

3. **Basic Rule Engine**
   - Define Rule abstract base class
   - Implement Violation model
   - Create RuleContext for analysis data
   - Build basic rule execution framework

### Phase 2: Essential Rules (Weeks 3-4)
1. **Import Rules**
   - Layer dependency enforcement
   - Package boundary rules
   - Wildcard pattern matching
   - Circular dependency detection

2. **Basic Patterns**
   - Layered Architecture support
   - Clean Architecture support
   - Configuration loading (YAML/TOML)

3. **CLI Development**
   - Basic command structure
   - Configuration discovery
   - Console reporting

### Phase 3: Advanced Features (Weeks 5-6)
1. **Extended Rule Types**
   - Naming convention rules
   - Structure validation rules
   - Complexity metrics
   - Archetype validation

2. **Additional Patterns**
   - Hexagonal Architecture
   - Domain-Driven Design
   - Microservice patterns

3. **Reporting Enhancements**
   - JSON/JUnit output formats
   - HTML report generation
   - Dependency visualization

### Phase 4: Integration & Polish (Weeks 7-8)
1. **Tool Integration**
   - Pre-commit hook package
   - GitHub Action
   - Pytest plugin
   - Basic IDE extensions

2. **Plugin System**
   - Plugin discovery mechanism
   - Plugin API finalization
   - Example plugins

3. **Documentation & Examples**
   - Comprehensive user guide
   - Architecture pattern guides
   - Migration guides from other tools
   - Example configurations

### Phase 5: Launch Preparation (Week 9)
1. **Quality Assurance**
   - Comprehensive test suite
   - Performance optimization
   - Security audit

2. **Community Preparation**
   - PyPI package setup
   - Documentation website
   - GitHub issue templates
   - Contributing guidelines

## 7. Success Metrics

### 7.1 Technical Metrics
- **Performance**: Analyze 100K LOC in < 10 seconds
- **Accuracy**: Zero false positives for import rules
- **Coverage**: Support 90% of common Python patterns
- **Extensibility**: < 50 lines to add a new rule type

### 7.2 Adoption Metrics
- **Downloads**: 10K+ downloads in first 6 months
- **GitHub Stars**: 500+ stars in first year
- **Active Plugins**: 20+ community plugins
- **Enterprise Users**: 5+ companies using in production

### 7.3 Quality Metrics
- **Test Coverage**: > 95% code coverage
- **Documentation**: 100% public API documented
- **Response Time**: < 48h for critical issues
- **Compatibility**: Python 3.8+ support

## 8. Competitive Advantages

### 8.1 vs import-linter
- **Comprehensive**: Beyond imports - naming, structure, complexity
- **Pattern-Aware**: Built-in architecture patterns
- **Extensible**: Full plugin system
- **Better UX**: Clear errors, auto-fix support

### 8.2 vs Manual Reviews
- **Consistent**: Same rules every time
- **Fast**: Instant feedback
- **Educational**: Teaches architecture patterns
- **Enforceable**: CI/CD integration

### 8.3 vs Custom Scripts
- **Maintained**: Regular updates and fixes
- **Documented**: Comprehensive guides
- **Tested**: Extensive test suite
- **Supported**: Active community

## 9. Future Vision

### 9.1 Short Term (6-12 months)
- **IDE Integration**: Real-time architecture feedback
- **Auto-refactoring**: Guided architecture migration
- **Learning Mode**: Infer rules from existing code
- **Performance Mode**: Incremental analysis

### 9.2 Long Term (1-2 years)
- **AI-Powered Suggestions**: ML-based architecture recommendations
- **Cross-Language Support**: Analyze Python calling Java/JS
- **Architecture Evolution**: Track architecture changes over time
- **Enterprise Features**: Multi-repo analysis, compliance reports

## 10. Conclusion

ArchGuard represents a significant opportunity to fill a critical gap in the Python ecosystem. By providing comprehensive, extensible, and user-friendly architecture verification, it can become the standard tool for maintaining architectural integrity in Python projects.

The combination of:
- Strong technical foundation (AST-based analysis)
- Great developer experience (clear errors, auto-fix)
- Extensibility (plugins, patterns)
- Community focus (open source, well-documented)

...positions ArchGuard to become the "pytest of architecture testing" - the obvious choice for any team serious about maintaining their architecture.

### Next Steps

1. **Validate Demand**: Survey Python developers about architecture pain points
2. **Build MVP**: Focus on core features that solve real problems
3. **Early Adopters**: Work with 3-5 projects to refine the tool
4. **Community Building**: Create Discord/Slack for early users
5. **Iterate**: Rapid releases based on user feedback

The path from concept to essential tool is clear. With focused execution and community engagement, ArchGuard can transform how Python developers think about and maintain their architecture.