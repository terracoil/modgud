"""
Lerper: Extended interpolation functionality for multiple data types.

Provides interpolation iteration for integers, floats, and vectors,
eliminating the need for type-specific iteration boilerplate.
"""

import math
from dataclasses import dataclass
from enum import Enum, auto

from .math_util import MathUtil
from .vector.vector import Vector
from .vector.vector_protocol import VectorProtocol

LerpValueType = int | float | VectorProtocol


class LerpStrategy(Enum):
  """Strategy for interpolation curve shapes."""

  LINEAR = auto()  # Linear interpolation (constant speed)
  SINE = auto()  # Sine curve (slow home, fast middle)
  COSINE = auto()  # Cosine curve (fast home, slow end)
  SQUARED = auto()  # Quadratic curve (accelerating)
  CUBED = auto()  # Cubic curve (smooth acceleration)
  SIGMOID = auto()  # S-curve (smooth home and end)


@dataclass
class Lerper[T: LerpValueType]:
  """
  Generic interpolation between two values.

  Supports numeric types (int, float) and VectorProtocol objects with
  various interpolation strategies for different animation curves.
  """

  start: T
  stop: T | None = None
  strategy: LerpStrategy = LerpStrategy.LINEAR

  def __post_init__(self) -> None:
    """Validate lerper configuration after initialization."""
    if not isinstance(self.start, (int, float, VectorProtocol)):
      raise TypeError(f'start must be int, float, or VectorProtocol, got {type(self.start)}')

    if self.stop is not None:
      if type(self.start) != type(self.stop):
        if not (isinstance(self.start, (int, float)) and isinstance(self.stop, (int, float))):
          raise TypeError('start and stop must be the same type or both numeric')

  def _apply_strategy(self, pct: float) -> float:
    """Apply strategy transformation to percentage."""
    result = pct  # Default linear

    if self.strategy == LerpStrategy.SINE:
      result = math.sin(pct * math.pi / 2)
    elif self.strategy == LerpStrategy.COSINE:
      result = 1 - math.cos(pct * math.pi / 2)
    elif self.strategy == LerpStrategy.SQUARED:
      result = pct * pct
    elif self.strategy == LerpStrategy.CUBED:
      result = pct * pct * pct
    elif self.strategy == LerpStrategy.SIGMOID:
      # Sigmoid curve: smoother acceleration/deceleration
      result = 1 / (1 + math.exp(-12 * (pct - 0.5)))

    return result

  def _apply_inverse_strategy(self, pct: float) -> float:
    """Apply inverse strategy transformation."""
    result = pct  # Default linear

    if self.strategy == LerpStrategy.SINE:
      result = math.asin(pct) * 2 / math.pi
    elif self.strategy == LerpStrategy.COSINE:
      result = math.acos(1 - pct) * 2 / math.pi
    elif self.strategy == LerpStrategy.SQUARED:
      result = math.sqrt(pct)
    elif self.strategy == LerpStrategy.CUBED:
      result = pct ** (1 / 3)
    elif self.strategy == LerpStrategy.SIGMOID:
      # Inverse sigmoid
      if pct <= 0 or pct >= 1:
        result = pct  # Clamp edge cases
      else:
        result = 0.5 - math.log((1 - pct) / pct) / 12

    return MathUtil.clamp(result, 0.0, 1.0)

  def _lerp_numeric(self, start: float, stop: float, pct: float) -> float:
    """Interpolate between numeric values."""
    return start + (stop - start) * pct

  def _lerp_vector(
    self, start: VectorProtocol, stop: VectorProtocol, pct: float | VectorProtocol
  ) -> VectorProtocol:
    """
    Interpolate between vector values with scalar or vector percentage.

    :param start: Starting vector
    :param stop: Ending vector
    :param pct: Interpolation percentage (float) or component-wise percentages (VectorProtocol)
    :returns: Interpolated vector
    """
    if isinstance(pct, (int, float)):
      # Uniform interpolation - same percentage for all components
      pct_float = float(pct)
      return Vector(
        x=self._lerp_numeric(start.x, stop.x, pct_float),
        y=self._lerp_numeric(start.y, stop.y, pct_float),
        z=self._lerp_numeric(start.z, stop.z, pct_float),
        w=self._lerp_numeric(start.w, stop.w, pct_float),
        name=start.name,  # Preserve name from start vector
      )
    else:
      # Component-wise interpolation - different percentage per component
      return Vector(
        x=self._lerp_numeric(start.x, stop.x, pct.x),
        y=self._lerp_numeric(start.y, stop.y, pct.y),
        z=self._lerp_numeric(start.z, stop.z, pct.z),
        w=self._lerp_numeric(start.w, stop.w, pct.w),
        name=start.name,  # Preserve name from start vector
      )

  def lerp(self, pct: float | VectorProtocol) -> T:
    """
    Interpolate between start and stop values.

    Supports both uniform interpolation (using float) and component-wise interpolation
    (using VectorProtocol) for granular control over each vector component.

    :param pct: Interpolation percentage (0.0 to 1.0) or component-wise percentages (VectorProtocol)
    :type pct: float | VectorProtocol
    :returns: Interpolated value
    :rtype: T
    :raises ValueError: If pct is outside [0, 1] range or stop is None
    :raises TypeError: If pct type is incompatible with start/stop types

    Examples:
        # Uniform interpolation (existing behavior)
        lerper = Lerper(start=Vector(0, 0), stop=Vector(100, 100))
        result = lerper.lerp(0.5)  # All components at 50%: Vector(50, 50)

        # Component-wise interpolation (new behavior)
        pct_vector = Vector(0.25, 0.75)  # x at 25%, y at 75%
        result = lerper.lerp(pct_vector)  # Vector(25, 75)

    """
    # Validation
    if self.stop is None:
      raise ValueError('stop value is required for interpolation')

    # Type validation
    if isinstance(self.start, (int, float)):
      if not isinstance(pct, (int, float)):
        raise TypeError('pct must be numeric when interpolating between numeric values')
      if not 0.0 <= pct <= 1.0:
        raise ValueError(f'pct must be between 0.0 and 1.0, got {pct}')
    elif isinstance(self.start, VectorProtocol):
      if isinstance(pct, (int, float)):
        if not 0.0 <= pct <= 1.0:
          raise ValueError(f'pct must be between 0.0 and 1.0, got {pct}')
      elif isinstance(pct, VectorProtocol):
        # Validate each component is in [0, 1] range
        for component in ['x', 'y', 'z', 'w']:
          comp_val = getattr(pct, component)
          if not 0.0 <= comp_val <= 1.0:
            raise ValueError(f'pct.{component} must be between 0.0 and 1.0, got {comp_val}')
      else:
        raise TypeError('pct must be numeric or VectorProtocol when interpolating between vectors')

    # Apply strategy transformation
    if isinstance(pct, (int, float)):
      transformed_pct = self._apply_strategy(float(pct))
    else:
      # Component-wise strategy application for vectors
      transformed_pct = Vector(
        x=self._apply_strategy(pct.x),
        y=self._apply_strategy(pct.y),
        z=self._apply_strategy(pct.z),
        w=self._apply_strategy(pct.w),
        name=pct.name,
      )

    # Type-specific interpolation
    result: T
    if isinstance(self.start, (int, float)) and isinstance(self.stop, (int, float)):
      interpolated = self._lerp_numeric(float(self.start), float(self.stop), transformed_pct)
      result = type(self.start)(interpolated) if isinstance(self.start, int) else interpolated  # type: ignore
    elif isinstance(self.start, VectorProtocol) and isinstance(self.stop, VectorProtocol):
      result = self._lerp_vector(self.start, self.stop, transformed_pct)  # type: ignore
    else:
      raise TypeError(
        f'Unsupported types for interpolation: {type(self.start)} and {type(self.stop)}'
      )

    return result

  def rlerp(self, pos: T) -> float:
    """
    Inverse interpolate to find percentage for given position.

    :param pos: Position vector to find percentage for
    :type pos: T
    :returns: Percentage (0.0 to 1.0) representing position
    :rtype: float
    :raises ValueError: If stop is None or home equals stop
    """
    # Validation
    if self.stop is None:
      raise ValueError('stop value is required for reverse interpolation')

    # Calculate linear percentage first
    linear_pct: float
    if isinstance(self.start, (int, float)) and isinstance(self.stop, (int, float)):
      if not isinstance(pos, (int, float)):
        raise TypeError(f'Type mismatch or unsupported type for reverse interpolation: {type(pos)}')
      if abs(float(self.stop) - float(self.start)) < MathUtil.EPSILON:
        raise ValueError('home and stop values are too close for reverse interpolation')
      linear_pct = (float(pos) - float(self.start)) / (float(self.stop) - float(self.start))
    elif (
      isinstance(self.start, VectorProtocol)
      and isinstance(self.stop, VectorProtocol)
      and isinstance(pos, VectorProtocol)
    ):
      # Use magnitude for vector rlerp
      start_mag = math.sqrt(self.start.x**2 + self.start.y**2 + self.start.z**2 + self.start.w**2)
      stop_mag = math.sqrt(self.stop.x**2 + self.stop.y**2 + self.stop.z**2 + self.stop.w**2)
      pos_mag = math.sqrt(pos.x**2 + pos.y**2 + pos.z**2 + pos.w**2)

      if abs(stop_mag - start_mag) < MathUtil.EPSILON:
        raise ValueError('home and stop vectors have similar magnitudes')
      linear_pct = (pos_mag - start_mag) / (stop_mag - start_mag)
    else:
      raise TypeError(f'Type mismatch or unsupported type for reverse interpolation: {type(pos)}')

    # Apply inverse strategy transformation
    result = self._apply_inverse_strategy(linear_pct)

    return result

  @classmethod
  def range(
    cls, start: T, stop: T, steps: int = 10, strategy: LerpStrategy = LerpStrategy.LINEAR
  ) -> list[T]:
    """
    Generate a range of interpolated values.

    :param start: Starting vector
    :param stop: Ending vector
    :param steps: Number of steps to generate (default: 10)
    :param strategy: Interpolation strategy (default: LINEAR)
    :returns: List of interpolated values
    """
    if steps < 2:
      raise ValueError('steps must be at least 2')

    lerper = cls(start=start, stop=stop, strategy=strategy)
    result = [lerper.lerp(i / (steps - 1)) for i in range(steps)]
    return result
