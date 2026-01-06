"""Shape factory for creating shapes from legacy and new APIs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from modgud.domain.enums import QuadShapeEnum
from modgud.domain.ports import ShapePort

from .kite import Kite
from .parallelogram import Parallelogram
from .rectangle import Rectangle
from .rhombus import Rhombus
from .square import Square
from .trapezoid import Trapezoid

if TYPE_CHECKING:
  pass


class ShapeFactory:
  """
  Factory for creating shape instances from various input formats.

  Supports both legacy API (QuadShapeEnum + params dict) and new API (direct shape classes).
  Provides backward compatibility while enabling migration to cleaner architecture.
  """

  @classmethod
  def create_from_legacy(
    cls, quad_shape: QuadShapeEnum, params: dict[str, Any], **decoration_params: Any
  ) -> ShapePort:
    """
    Create shape from legacy API format.

    Args:
      quad_shape: The type of quadrilateral shape to create
      params: Dictionary of shape-specific parameters
      **decoration_params: Torn edge and notch parameters

    Returns:
      Appropriate shape instance

    Raises:
      ValueError: If shape type is unknown or parameters are invalid

    """
    # Map QuadShapeEnum to shape classes and parameter mappings
    shape_mappings = {
      QuadShapeEnum.SQUARE: cls._create_square_from_legacy,
      QuadShapeEnum.RECTANGLE: cls._create_rectangle_from_legacy,
      QuadShapeEnum.PARALLELOGRAM: cls._create_parallelogram_from_legacy,
      QuadShapeEnum.RHOMBUS: cls._create_rhombus_from_legacy,
      QuadShapeEnum.RIGHTANGLE_TRAPEZOID: cls._create_trapezoid_from_legacy,
      QuadShapeEnum.GENERAL_TRAPEZOID: cls._create_trapezoid_from_legacy,
      QuadShapeEnum.ISOSCELES_TRAPEZOID: cls._create_trapezoid_from_legacy,
      QuadShapeEnum.KITE: cls._create_kite_from_legacy,
    }

    factory_method = shape_mappings.get(quad_shape)
    if not factory_method:
      raise ValueError(f'Unknown shape type: {quad_shape}')

    return factory_method(params, decoration_params)

  @classmethod
  def _create_square_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Square:
    """Create Square from legacy parameters."""
    # Square expects: side
    side = params.get('side')
    if side is None:
      # Try common alternatives
      side = params.get('w', params.get('width', params.get('h', params.get('height'))))

    if side is None:
      raise ValueError('Square requires "side" parameter')

    return Square(side=side, **decoration_params)

  @classmethod
  def _create_rectangle_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Rectangle:
    """Create Rectangle from legacy parameters."""
    # Rectangle expects: width, height
    width = params.get('w', params.get('width'))
    height = params.get('h', params.get('height'))

    if width is None or height is None:
      raise ValueError('Rectangle requires "w" (width) and "h" (height) parameters')

    return Rectangle(width=width, height=height, **decoration_params)

  @classmethod
  def _create_parallelogram_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Parallelogram:
    """Create Parallelogram from legacy parameters."""
    # Parallelogram expects: width, height, angle
    width = params.get('w', params.get('width'))
    height = params.get('h', params.get('height'))
    angle = params.get('angle')
    slant = params.get('slant')  # Optional alternative to angle

    if width is None or height is None:
      raise ValueError('Parallelogram requires "w" (width) and "h" (height) parameters')

    if angle is None and slant is None:
      raise ValueError('Parallelogram requires either "angle" or "slant" parameter')

    # Use angle if provided, otherwise calculate from slant
    if angle is None:
      # Convert slant to angle: angle = arctan(height / slant)
      import math

      angle = math.atan2(height, slant) if slant != 0 else math.pi / 2

    return Parallelogram(width=width, height=height, angle=angle, slant=slant, **decoration_params)

  @classmethod
  def _create_rhombus_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Rhombus:
    """Create Rhombus from legacy parameters."""
    # Rhombus expects: side, angle
    side = params.get('side')
    angle = params.get('angle')

    if side is None:
      # Try to infer from width/height if angle is available
      if angle is not None:
        width = params.get('w', params.get('width'))
        if width is not None:
          side = width

    if side is None or angle is None:
      raise ValueError('Rhombus requires "side" and "angle" parameters')

    return Rhombus(side=side, angle=angle, **decoration_params)

  @classmethod
  def _create_trapezoid_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Trapezoid:
    """Create Trapezoid from legacy parameters (auto-detects variant)."""
    # Trapezoid expects: w1, w2, h, optional side_left
    w1 = params.get('w1')
    w2 = params.get('w2')
    h = params.get('h', params.get('height'))
    side_left = params.get('side_left')

    # Handle legacy parameter variations
    if w1 is None:
      w1 = params.get('width', params.get('w'))
    if w2 is None:
      # Some legacy code might use 'top_width' or similar
      w2 = params.get('top_width', params.get('width_top', w1 * 0.6 if w1 else None))

    if w1 is None or w2 is None or h is None:
      raise ValueError(
        'Trapezoid requires "w1" (bottom width), "w2" (top width), and "h" (height) parameters'
      )

    # Trapezoid class will auto-determine the variant from these parameters
    return Trapezoid(w1=w1, w2=w2, h=h, side_left=side_left, **decoration_params)

  @classmethod
  def _create_kite_from_legacy(
    cls, params: dict[str, Any], decoration_params: dict[str, Any]
  ) -> Kite:
    """Create Kite from legacy parameters."""
    # Kite expects: diagonal1, diagonal2
    diagonal1 = params.get('diagonal1', params.get('d1'))
    diagonal2 = params.get('diagonal2', params.get('d2'))

    # Try alternative parameter names
    if diagonal1 is None:
      diagonal1 = params.get('height', params.get('h'))
    if diagonal2 is None:
      diagonal2 = params.get('width', params.get('w'))

    if diagonal1 is None or diagonal2 is None:
      raise ValueError('Kite requires "diagonal1" and "diagonal2" parameters')

    return Kite(diagonal1=diagonal1, diagonal2=diagonal2, **decoration_params)

  @classmethod
  def create_shape(cls, shape_type: str, **params: Any) -> ShapePort:
    """
    Create shape from new string-based API.

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
    """
    List all available shape types for the new API.

    Returns:
      List of shape type strings

    """
    return ['square', 'rectangle', 'parallelogram', 'rhombus', 'trapezoid', 'kite']

  @classmethod
  def get_shape_parameters(cls, shape_type: str) -> dict[str, str]:
    """
    Get parameter information for a specific shape type.

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
