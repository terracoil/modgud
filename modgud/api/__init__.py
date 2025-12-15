"""
API layer - Public-facing utilities and tools.

This layer contains utilities and tools that provide programmatic access to
modgud functionality. These are intended for external consumption and provide
higher-level abstractions over the core infrastructure.

Following KLA (Kinetic Layer Architecture) principles:
- Dependencies flow downward: api -> infrastructure/domain/util
- No upward dependencies allowed
- Pure functions and immutable objects where possible

Primary modules:
  - geometry: Mathematical and geometric utilities (Vector, Lerper, Joinery)
  - tools: Specialized API tools (Ranger, TextUtil)
"""

# Re-export from geometry
from .geometry import Joinery, Lerper, LerpStrategy, Vector, VectorPath, VectorProtocol

# Re-export from tools
from .tools import Ranger, TextUtil

__all__ = [
  # Geometry exports
  'Joinery',
  'Lerper',
  'LerpStrategy',
  'Vector',
  'VectorPath',
  'VectorProtocol',
  # Tools exports
  'Ranger',
  'TextUtil',
]
