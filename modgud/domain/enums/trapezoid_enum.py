"""Trapezoid variant enumeration with auto-detection capabilities."""

from __future__ import annotations

from enum import Enum


class TrapezoidEnum(Enum):
  """Enumeration of trapezoid variants based on geometric properties."""

  GENERAL = 'general'
  ISOSCELES = 'isosceles'
  RIGHT_ANGLE = 'right_angle'

  @classmethod
  def from_params(
    cls, w1: float, w2: float, h: float, side_left: float | None = None, tolerance: float = 1e-6
  ) -> TrapezoidEnum:
    """Automatically determine trapezoid variant from parameters.

    Args:
      w1: Bottom width
      w2: Top width
      h: Height
      side_left: Optional left side length constraint
      tolerance: Floating point comparison tolerance

    Returns:
      The appropriate TrapezoidEnum variant

    Algorithm:
      1. RIGHT_ANGLE: When side_left == h (90° left angle)
      2. ISOSCELES: When trapezoid is symmetric (no side_left constraint or creates symmetry)
      3. GENERAL: All other cases

    """
    # Right angle trapezoid: left side creates 90° angle
    if side_left is not None and abs(side_left - h) < tolerance:
      return cls.RIGHT_ANGLE

    # Isosceles trapezoid: symmetric shape
    # When no side constraint is given, assume isosceles (symmetric)
    # When side constraint matches the calculated symmetric side length
    if side_left is None:
      return cls.ISOSCELES

    # Calculate what the left side length would be for an isosceles trapezoid
    # In isosceles, both sides have equal length and angle
    width_diff = abs(w1 - w2)
    calculated_side = (width_diff**2 / 4 + h**2) ** 0.5

    if abs(side_left - calculated_side) < tolerance:
      return cls.ISOSCELES

    # Default: General trapezoid
    return cls.GENERAL

  def __str__(self) -> str:
    """Return human-readable string representation."""
    return self.value.replace('_', ' ').title()
