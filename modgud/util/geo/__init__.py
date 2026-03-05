"""Geometry API - Mathematical and geometric utilities for modgud.

This module provides geometry-related functionality including:
- Vector operations and path manipulation
- Linear interpolation (Lerper)
- Joinery calculations for woodworking joints
- Simplex noise generation with fractal Brownian motion
- Torn paper shapes with procedural edges
- SVG conversion utilities for backward compatibility
"""

from modgud.domain.ports import NoisePort, VectorPort

from .color import Color, GrayscaleAlgorithm, HarmonyMethod, HarmonyType
from .geo_util import GeoUtil
from .interpolation import Lerper, LerpStrategy
from .joinery import Joinery
from .line import Line
from .quadrilateral import Quadrilateral
from .simplex_noise import SimplexNoise
from .stackable_trapezoid import StackableTrapezoid
from .svg import JoineryResult, SVGConverter
from .torn_paper import TornPaper
from .types import HexMetadata
from .vector import Vector
from .vector_path import VectorPath

__all__ = [
  'Color',
  'GeoUtil',
  'GrayscaleAlgorithm',
  'HarmonyMethod',
  'HarmonyType',
  'HexMetadata',
  'JoineryResult',
  'Joinery',
  'Lerper',
  'LerpStrategy',
  'Line',
  'NoisePort',
  'Quadrilateral',
  'SVGConverter',
  'SimplexNoise',
  'StackableTrapezoid',
  'TornPaper',
  'Vector',
  'VectorPath',
  'VectorPort',
]
