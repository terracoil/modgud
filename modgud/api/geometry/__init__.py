"""
Geometry API - Mathematical and geometric utilities for modgud.

This module provides geometry-related functionality including:
- Vector operations and path manipulation
- Linear interpolation (Lerper)
- Joinery calculations for woodworking joints
- Simplex noise generation with fractal Brownian motion
- Torn paper shapes with procedural edges
- SVG conversion utilities for backward compatibility
"""

from ...domain.ports.noise_port import NoisePort
from ...domain.ports.vector_port import VectorPort
from .joinery import Joinery
from .lerper import Lerper, LerpStrategy
from .line import Line
from .simplex_noise import SimplexNoise
from .stackable_trapezoid import StackableTrapezoid
from .svg_converter import JoineryResult, SVGConverter, migrate_shape_result
from .torn_paper import TornPaper
from .vector import Vector
from .vector_path import VectorPath

__all__ = [
  'JoineryResult',
  'Joinery',
  'Lerper',
  'LerpStrategy',
  'Line',
  'NoisePort',
  'SVGConverter',
  'SimplexNoise',
  'StackableTrapezoid',
  'TornPaper',
  'Vector',
  'VectorPath',
  'VectorPort',
  'migrate_shape_result',
]
