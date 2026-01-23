"""Shape factory for creating shapes."""

from __future__ import annotations

from typing import Any

from modgud.domain.ports import ShapePort

from .kite import Kite
from .parallelogram import Parallelogram
from .rectangle import Rectangle
from .rhombus import Rhombus
from .square import Square
from .trapezoid import Trapezoid


class ShapeFactory:
  """Factory for creating shape instances from string-based API."""

  @classmethod
  def create_shape(cls, shape_type: str, **params: Any) -> ShapePort:
    """Create shape from new string-based API.

    Args:
      shape_type: String name of shape ('square', 'rectangle', 'trapezoid', etc.)
      **params: Shape-specific parameters

    Returns:
      Appropriate shape instance

    Raises:
      ValueError: If shape type is unknown

    """
    shape_classes = {
      'square': Square,
      'rectangle': Rectangle,
      'parallelogram': Parallelogram,
      'rhombus': Rhombus,
      'trapezoid': Trapezoid,
      'kite': Kite,
    }

    shape_class = shape_classes.get(shape_type.lower())
    if not shape_class:
      raise ValueError(f'Unknown shape type: {shape_type}. Available: {list(shape_classes.keys())}')

    return shape_class(**params)

  @classmethod
  def list_available_shapes(cls) -> list[str]:
    """List all available shape types for the new API.

    Returns:
      List of shape type strings

    """
    return ['square', 'rectangle', 'parallelogram', 'rhombus', 'trapezoid', 'kite']

  @classmethod
  def get_shape_parameters(cls, shape_type: str) -> dict[str, str]:
    """Get parameter information for a specific shape type.

    Args:
      shape_type: String name of shape

    Returns:
      Dictionary mapping parameter names to descriptions

    Raises:
      ValueError: If shape type is unknown

    """
    parameter_info = {
      'square': {'side': 'Length of all sides (float, 0 < side <= 1)'},
      'rectangle': {
        'width': 'Width of rectangle (float, 0 < width <= 1)',
        'height': 'Height of rectangle (float, 0 < height <= 1)',
      },
      'parallelogram': {
        'width': 'Base width (float, 0 < width <= 1)',
        'height': 'Perpendicular height (float, 0 < height <= 1)',
        'angle': 'Interior angle in radians (float, 0.1 < angle < π-0.1)',
        'slant': 'Optional: horizontal offset instead of angle (float)',
      },
      'rhombus': {
        'side': 'Length of all sides (float, 0 < side <= 1)',
        'angle': 'Interior angle in radians (float, 0.1 < angle < π-0.1)',
      },
      'trapezoid': {
        'w1': 'Bottom width (float, 0 < w1 <= 1)',
        'w2': 'Top width (float, 0 < w2 <= 1)',
        'h': 'Height (float, 0 < h <= 1)',
        'side_left': 'Optional: left side length constraint (float, >= h)',
      },
      'kite': {
        'diagonal1': 'First diagonal length (float, 0 < diagonal1 <= 1)',
        'diagonal2': 'Second diagonal length (float, 0 < diagonal2 <= 1)',
      },
    }

    info = parameter_info.get(shape_type.lower())
    if not info:
      raise ValueError(
        f'Unknown shape type: {shape_type}. Available: {list(parameter_info.keys())}'
      )

    return info
