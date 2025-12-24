"""Stackable trapezoid shape generator for nested geometric shapes."""

from __future__ import annotations

import math

from .vector import Vector
from .vector_path import VectorPath


class StackableTrapezoid:
  """Generate stackable trapezoid shapes with bottom notch for nesting."""

  def calculate_trapezoid(
    self,
    angle: float = 70,
    notch_height: float = 0.2,
    width: float = 100,
    height: float = 100,
    invert: bool = False,
  ) -> dict[str, list[str]]:
    """
    Calculate coordinates for a symmetric stackable trapezoid with centered bottom notch.

    The trapezoid has:
    - Perfectly symmetric angled sides
    - Centered rectangular notch at bottom for stacking
    - Mathematical precision ensuring proper closure

    :param angle: Side angle in degrees from vertical (10-80)
    :param notch_height: Notch depth as percentage of height (0.1-0.4)
    :param width: Width of trapezoid base
    :param height: Height of trapezoid
    :param invert: Whether to invert (notch at top)
    :returns: Dictionary with 'shape' SVG path array
    """
    # Validate parameters
    if angle < 70 or angle > 85:
      raise ValueError('angle should be between 70° and 85°')

    if notch_height < 0.1 or notch_height > 0.4:
      raise ValueError('stackable_pct should be between 10% and 40%')

    # Convert to radians and calculate slope
    rad_angle = math.radians(angle)

    # For a trapezoid with sides at 'angle' degrees from vertical:
    # The horizontal offset per unit height is 1/tan(angle) = cot(angle)
    # This is because we want horizontal_offset / height = cot(angle)
    slope_offset = 1.0 / math.tan(rad_angle)

    # In normalized coordinates (0-1), the trapezoid has:
    # - Bottom width: 1.0 (from x=0 to x=1)
    # - Top width: 1.0 - 2*slope_offset (centered)
    # - Height: 1.0
    top_width = 1.0 - 2 * slope_offset

    # Ensure top width is reasonable
    if top_width < 0.2:
      raise ValueError(f'Angle {angle}° is too steep - reduces top width to {top_width:.2f}')

    # Notch dimensions - must fit the TOP of another identical trapezoid
    notch_depth = notch_height  # How far up the notch cuts

    if not invert:
      # Normal trapezoid: notch should fit the top edge of another trapezoid
      # The top width of this trapezoid is what needs to fit in the notch
      notch_top_width = top_width  # Width at the top of the notch (narrow part)
      notch_bottom_width = (
        notch_top_width + 2 * notch_depth * slope_offset
      )  # Width at bottom of notch (wide part)
    else:
      # Inverted trapezoid: notch at bottom should be 90% of the narrow bottom edge
      # For inverted, the "top_width" is actually at the bottom (narrow end)
      notch_bottom_width = top_width * 0.9  # 90% of the narrow bottom edge
      notch_top_width = notch_bottom_width + 2 * notch_depth * slope_offset  # Wider at top of notch

    # Key coordinates (in normalized 0-1 space):
    # Bottom: (0,1) to (1,1) with centered notch
    # Top: (slope_offset, 0) to (1-slope_offset, 0)

    path_name = f'trapezoid_{angle:.0f}°_{notch_height:.1f}'

    if not invert:
      # Build trapezoid path - start at the actual top-left corner, go clockwise
      path = VectorPath(
        name=path_name,
        rel_segments=[
          # Start at top-left corner (slope_offset, 0) in normalized coordinates
          Vector(slope_offset, 0, name='origin'),
          # Draw top edge (horizontal to the right)
          Vector(top_width, 0, name='topEdge'),
          # Draw right angled side down to bottom-right (1, 1)
          Vector(slope_offset, 1.0, name='rightSide'),
          # Move left along bottom to start of notch (right side)
          Vector(-((1.0 - notch_bottom_width) / 2), 0, name='toNotchRight'),
          # Draw notch: angled down (matching trapezoid slope), across narrow top, angled up
          Vector(-notch_depth * slope_offset, -notch_depth, name='notchRightSide'),
          Vector(-notch_top_width, 0, name='notchBottom'),
          Vector(-notch_depth * slope_offset, notch_depth, name='notchLeftSide'),
          # Move left along bottom to bottom-left corner (0, 1)
          Vector(-((1.0 - notch_bottom_width) / 2), 0, name='toBottomLeft'),
          # Draw left angled side back to top-left corner (closes the path)
          Vector(slope_offset, -1.0, name='leftSide'),
        ],
      )
    else:
      # Inverted trapezoid: narrow at bottom, wide at top, notch at narrow bottom
      # Key insight: bottom edge goes from (slope_offset, 1) to (1-slope_offset, 1)
      path = VectorPath(
        name=path_name,
        rel_segments=[
          Vector(0, 0, name='origin'),  # Start at top-left (0, 0) - wide edge
          Vector(1.0, 0, name='topEdge'),  # Top edge (wide) to top-right (1, 0)
          Vector(-slope_offset, 1.0, name='rightSide'),  # Right side down to (1-slope_offset, 1)
          # Move left along narrow bottom to start of notch
          Vector(-((top_width - notch_bottom_width) / 2), 0, name='toNotchRight'),
          # Draw notch: angled up, across narrow top, angled down
          Vector(notch_depth * slope_offset, -notch_depth, name='notchRightSide'),
          Vector(-notch_bottom_width, 0, name='notchBottom'),
          Vector(notch_depth * slope_offset, notch_depth, name='notchLeftSide'),
          # Move left along narrow bottom to (slope_offset, 1)
          Vector(-((top_width - notch_bottom_width) / 2), 0, name='toBottomLeft'),
          # Left side up to top-left (0, 0)
          Vector(-slope_offset, -1.0, name='leftSide'),
        ],
      )

    # Scale to actual dimensions
    path.transform_all(Vector(width, height))

    # Generate SVG paths
    result = {'shape': list(path.svg_path())}

    return result

  def calculate_nesting_demo(
    self,
    count: int = 3,
    angle: float = 70,
    stackable_pct: float = 0.2,
    width: float = 100,
    height: float = 100,
  ) -> dict[str, list[list[str]]]:
    """
    Generate a demonstration of nested trapezoids.

    Creates multiple trapezoids positioned to show how they stack together.

    :param count: Number of trapezoids to generate (2-5)
    :param angle: Side angle in degrees
    :param stackable_pct: Depth of notch as percentage
    :param width: Width of the base trapezoid
    :param height: Height of the base trapezoid
    :returns: Dictionary with 'shapes' containing list of SVG paths
    """
    if count < 2 or count > 5:
      raise ValueError('count should be between 2 and 5')

    shapes = []

    # Calculate offset for nesting based on the stackable percentage
    vertical_offset = height * stackable_pct * 0.9  # 0.9 to ensure proper fit

    for i in range(count):
      # All trapezoids are the same size in this stacking design
      trap_dict = self.calculate_trapezoid(
        angle=angle, notch_height=stackable_pct, width=width, height=height, invert=False
      )

      # Get the shape path
      shape_path = trap_dict['shape']

      # If this isn't the first trapezoid, we need to offset it vertically
      if i > 0:
        offset = i * vertical_offset
        # Create a new list with modified paths
        modified_paths = []
        for line in shape_path:
          if '<move' in line or '<line' in line:
            # Simple string replacement for y values
            # This is a basic approach - in production you'd use proper XML parsing
            import re

            y_match = re.search(r'y="([^"]+)"', line)
            if y_match:
              y_val = float(y_match.group(1))
              new_y = y_val - offset  # Negative because SVG y-axis goes down
              line = re.sub(r'y="[^"]+"', f'y="{new_y}"', line)
          modified_paths.append(line)
        shapes.append(modified_paths)
      else:
        shapes.append(shape_path)

    return {'shapes': shapes}
