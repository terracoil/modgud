"""Extracted shape classes with explicit parameters and type safety.

This package contains individual shape classes extracted from the monolithic
Quadrilateral class, each with only the parameters needed for that specific shape.
"""

from .base import ShapeBase
from .kite import Kite
from .parallelogram import Parallelogram
from .rectangle import Rectangle
from .rhombus import Rhombus
from .shape_factory import ShapeFactory
from .square import Square
from .trapezoid import Trapezoid

__all__ = [
  'ShapeBase',
  'ShapeFactory',
  'Square',
  'Rectangle',
  'Trapezoid',
  'Parallelogram',
  'Rhombus',
  'Kite',
]
