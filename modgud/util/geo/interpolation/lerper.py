"""Lerper: Extended interpolation functionality for multiple data types.

Provides interpolation iteration for integers, floats, and vectors,
eliminating the need for type-specific iteration boilerplate.
"""

import math
from dataclasses import dataclass

from modgud.domain.ports import VectorPort
from modgud.util.geo.vector import Vector
from modgud.util.math_util import MathUtil

from .lerp_strategy import LerpStrategy

LerpValueType = int | float | VectorPort


@dataclass
class Lerper[T: LerpValueType]:
  """Generic interpolation between two values.

  Supports numeric types (int, float) and VectorPort objects with
  various interpolation strategies for different animation curves.
  """

  start: T
  stop: T | None = None
  strategy: LerpStrategy = LerpStrategy.LINEAR

  def __post_init__(self) -> None:
    """Validate lerper configuration after initialization."""
    if not isinstance(self.start, (int, float, VectorPort)):
      raise TypeError(f'start must be int, float, or VectorPort, got {type(self.start)}')

    if self.stop is not None:
      if type(self.start) is not type(self.stop):
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

  def lerp(self, pct: float | VectorPort, clamp: bool = True) -> T:
    """Interpolate between start and stop values with optional extrapolation.

    Supports both uniform interpolation (using float) and component-wise interpolation
    (using VectorProtocol) for granular control over each vector component.

    :param pct: Interpolation percentage or component-wise percentages (VectorProtocol)
    :type pct: float | VectorPort
    :param clamp: If True, clamp pct to [0,1] range. If False, allow extrapolation beyond range
    :type clamp: bool
    :returns: Interpolated name
    :rtype: T
    :raises ValueError: If stop is None, or if clamp=True and pct is outside [0, 1] range
    :raises TypeError: If pct type is incompatible with start/stop types

    Examples:
        # Uniform interpolation (existing behavior)
        lerper = Lerper(start=Vector(0, 0), stop=Vector(100, 100))
        result = lerper.lerp(0.5)  # All components at 50%: Vector(50, 50)

        # Component-wise interpolation
        pct_vector = Vector(0.25, 0.75)  # x at 25%, y at 75%
        result = lerper.lerp(pct_vector)  # Vector(25, 75)

        # Extrapolation beyond [0,1] range
        result = lerper.lerp(1.5, clamp=False)  # Extrapolate 50% beyond stop

    """
    # Validation
    if self.stop is None:
      raise ValueError('stop name is required for interpolation')

    # Determine types once
    start_is_numeric = isinstance(self.start, (int, float))
    pct_is_numeric = isinstance(pct, (int, float))

    # Type validation with optional range checking
    if start_is_numeric:
      if not pct_is_numeric:
        raise TypeError('pct must be numeric when interpolating between numeric values')
      if clamp:
        self._check_zero_to_one(pct, 'pct')
    else:  # start is VectorPort
      if pct_is_numeric:
        if clamp:
          self._check_zero_to_one(pct, 'pct')
      elif isinstance(pct, VectorPort):
        if clamp:
          # Validate each component is in [0, 1] range only if clamping
          for component in ['x', 'y', 'z', 'w']:
            comp_val = getattr(pct, component)
            self._check_zero_to_one(comp_val, f'pct.{component}')
      else:
        raise TypeError('pct must be numeric or VectorPort when interpolating between vectors')

    # Apply strategy transformation
    transformed_pct: float | VectorPort
    if pct_is_numeric:
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
    if start_is_numeric:
      # Both start and stop must be numeric (validated in __post_init__)
      assert isinstance(self.stop, (int, float)), 'stop should be numeric when start is numeric'
      # In numeric branch, transformed_pct is always float due to logic above
      assert isinstance(transformed_pct, (int, float)), (
        'transformed_pct should be numeric in numeric branch'
      )
      interpolated = self._lerp_numeric(float(self.start), float(self.stop), float(transformed_pct))
      result = type(self.start)(interpolated) if isinstance(self.start, int) else interpolated  # type: ignore
    else:
      # Both start and stop must be VectorPort (validated in __post_init__)
      assert isinstance(self.stop, VectorPort), 'stop should be VectorPort when start is VectorPort'
      result = self._lerp_vector(self.start, self.stop, transformed_pct)  # type: ignore

    return result

  def scale(self, value: T, scale_factor: float | VectorPort, offset: T | None = None) -> T:
    """Apply scaling and optional offset transformation to a name.

    This performs the transformation: offset + name * scale_factor
    Useful for coordinate system conversion, viewport scaling, and data mapping.

    :param value: Value to transform
    :type value: T
    :param scale_factor: Scaling factor (uniform or component-wise)
    :type scale_factor: float | VectorPort
    :param offset: Optional offset to add after scaling
    :type offset: T | None
    :returns: Transformed name
    :rtype: T
    :raises TypeError: If name type is incompatible with scale_factor/offset types

    Examples:
        # Uniform scaling of vector
        lerper = Lerper(start=Vector.ZERO, stop=Vector(1, 1))
        result = lerper.scale(Vector(2, 3), 0.5)  # Vector(1, 1.5)

        # Component-wise scaling with offset
        scale_vec = Vector(2, 0.5)
        offset_vec = Vector(10, 20)
        result = lerper.scale(Vector(5, 10), scale_vec, offset_vec)  # Vector(20, 25)

        # Numeric scaling
        lerper = Lerper(start=0, stop=100)
        result = lerper.scale(42, 2.5, 10)  # 115.0

    """
    # Type validation
    if isinstance(value, (int, float)):
      if not isinstance(scale_factor, (int, float)):
        raise TypeError('scale_factor must be numeric when scaling numeric values')
      if offset is not None and not isinstance(offset, (int, float)):
        raise TypeError('offset must be numeric when scaling numeric values')

      # Numeric scaling
      scaled = float(value) * float(scale_factor)
      result = scaled + float(offset) if offset is not None else scaled
      return type(value)(result) if isinstance(value, int) else result  # type: ignore

    elif isinstance(value, VectorPort):
      # Vector scaling - support both uniform and component-wise
      if isinstance(scale_factor, (int, float)):
        # Uniform scaling
        scale_float = float(scale_factor)
        scaled_x = value.x * scale_float
        scaled_y = value.y * scale_float
        scaled_z = value.z * scale_float
        scaled_w = value.w * scale_float
      elif isinstance(scale_factor, VectorPort):
        # Component-wise scaling
        scaled_x = value.x * scale_factor.x
        scaled_y = value.y * scale_factor.y
        scaled_z = value.z * scale_factor.z
        scaled_w = value.w * scale_factor.w
      else:
        raise TypeError('scale_factor must be numeric or VectorPort when scaling vectors')

      # Apply offset if provided
      final_x = scaled_x + (offset.x if offset else 0)
      final_y = scaled_y + (offset.y if offset else 0)
      final_z = scaled_z + (offset.z if offset else 0)
      final_w = scaled_w + (offset.w if offset else 0)

      return Vector(x=final_x, y=final_y, z=final_z, w=final_w, name=value.name)  # type: ignore

    else:
      raise TypeError(f'Unsupported type for scaling: {type(value)}')

  @classmethod
  def from_transform(
    cls,
    scale: float | VectorPort,
    offset: T | None = None,
    strategy: LerpStrategy = LerpStrategy.LINEAR,
  ) -> 'Lerper[T]':
    """Create lerper for scaling and offset transformations without interpolation.

    This creates a Lerper instance optimized for scaling/offset operations rather than
    traditional interpolation. Uses the start name as a base and stop as None to indicate
    transformation-only mode.

    :param scale: Scaling factor (uniform or component-wise)
    :type scale: float | VectorPort
    :param offset: Optional offset base name
    :type offset: T | None
    :param strategy: Interpolation strategy (mostly for consistency, limited use in transform mode)
    :type strategy: LerpStrategy
    :returns: Lerper configured for transformation operations
    :rtype: Lerper[T]

    Examples:
        # Create transformer for 2x scaling with Vector(10, 20) offset
        transformer = Lerper.from_transform(scale=2.0, offset=Vector(10, 20))
        result = transformer.scale(Vector(5, 10), scale=2.0, offset=Vector(10, 20))

        # Create component-wise scaling transformer
        scale_vec = Vector(2, 0.5, 1, 1)
        transformer = Lerper.from_transform(scale=scale_vec, offset=Vector.ZERO)

    """
    # Use offset as start, with stop=None to indicate transform-only mode
    start_value = (
      offset if offset is not None else (Vector.ZERO if isinstance(scale, VectorPort) else 0)
    )  # type: ignore
    return cls(start=start_value, stop=None, strategy=strategy)  # type: ignore

  def rlerp(self, pos: T) -> T:
    """Inverse interpolate to find percentage for given position.

    :param pos: Position vector to find percentage for
    :type pos: T
    :returns: Percentage (0.0 to 1.0) representing position
    :rtype: float
    :raises ValueError: If stop is None or origin equals stop
    """
    # Validation
    if self.stop is None:
      raise ValueError('stop name is required for reverse interpolation')

    pct: T
    if isinstance(self.start, (int, float)) and isinstance(self.stop, (int, float)):
      # Reverse-lerp simple numeric:
      pct = self._rlerp_numeric(pos, self.start, self.stop)
    elif (
      isinstance(self.start, VectorPort)
      and isinstance(self.stop, VectorPort)
      and isinstance(pos, VectorPort)
    ):
      # Reverse-lerp Vector:
      if self.start == self.stop:
        raise ValueError('origin and stop vectors are very similar, cannot interpolate')

      pct = Vector(
        x=self._rlerp_numeric(pos.x, self.start.x, self.stop.x),
        y=self._rlerp_numeric(pos.y, self.start.y, self.stop.y),
        z=self._rlerp_numeric(pos.z, self.start.z, self.stop.z),
        w=self._rlerp_numeric(pos.w, self.start.w, self.stop.w),
        name=pos.name or self.start.name or self.stop.name,
      )
    else:
      raise TypeError(
        f'Type mismatch or unsupported type for reverse interpolation: type(pos)={type(pos)} should match type(start)={type(self.start)} and type(stop)={type(self.stop)}'
      )

    # Apply inverse strategy transformation
    return pct

  @classmethod
  def range(
    cls, start: T, stop: T, steps: int = 10, strategy: LerpStrategy = LerpStrategy.LINEAR
  ) -> list[T]:
    """Generate a range of interpolated values.

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

  @staticmethod
  def _check_zero_to_one(v, name):
    if not -MathUtil.EPSILON <= v <= 1.0 + MathUtil.EPSILON:
      raise ValueError(f'{name} must be between 0.0 and 1.0, got {v}')

  @classmethod
  def _lerp_numeric(cls, start: float, stop: float, pct: float) -> float:
    """Interpolate between numeric values."""
    return start + (stop - start) * pct

  def _rlerp_numeric(self, pos: int | float, start: int | float, stop: int | float) -> float:
    """Determine percentage for given position in numeric interpolation and apply inverse strategy."""
    if not isinstance(pos, (int, float)):
      raise TypeError(f'Type mismatch or unsupported type for reverse interpolation: {type(pos)}')
    if MathUtil.is_equal(stop, start):
      raise ValueError('origin and stop values are too close for reverse interpolation')

    linear_pct: float = (float(pos) - float(start)) / (float(stop) - float(start))
    return self._apply_inverse_strategy(linear_pct)

  @classmethod
  def _lerp_vector(cls, start: VectorPort, stop: VectorPort, pct: float | VectorPort) -> VectorPort:
    """Interpolate between vector values with scalar or vector percentage.

    :param start: Starting vector
    :param stop: Ending vector
    :param pct: Interpolation percentage (float) or component-wise percentages (VectorPort)
    :returns: Interpolated vector
    """
    if isinstance(pct, (int, float)):
      # Uniform interpolation - same percentage for all components
      pct_float = float(pct)
      return Vector(
        x=cls._lerp_numeric(start.x, stop.x, pct_float),
        y=cls._lerp_numeric(start.y, stop.y, pct_float),
        z=cls._lerp_numeric(start.z, stop.z, pct_float),
        w=cls._lerp_numeric(start.w, stop.w, pct_float),
        name=start.name,  # Preserve name from start vector
      )
    else:
      # Component-wise interpolation - different percentage per component
      return Vector(
        x=cls._lerp_numeric(start.x, stop.x, pct.x),
        y=cls._lerp_numeric(start.y, stop.y, pct.y),
        z=cls._lerp_numeric(start.z, stop.z, pct.z),
        w=cls._lerp_numeric(start.w, stop.w, pct.w),
        name=start.name,  # Preserve name from start vector
      )
