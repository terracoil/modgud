"""Vector Implementation."""

from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Iterable

from .vector_protocol import VectorProtocol

# Type aliases for flexible vector input handling
VectorSingularType = dict[str, Any] | VectorProtocol | tuple[float]  # Single vector representation
VectorInputType = list[VectorSingularType] | VectorSingularType  # Single or multiple vectors

# Sentinel object to distinguish between None and not provided
_NOT_PROVIDED = object()


@dataclass(frozen=True)
class Vector(VectorProtocol):
  """
  4D Vector implementation supporting 2D/3D graphics and quaternion operations.

  Provides mathematical operations for geometric transformations, with the w component
  enabling quaternion mathematics and homogeneous coordinate transformations.
  The frozen dataclass ensures immutability for safer concurrent operations.

  :param x: X coordinate
  :param y: Y coordinate
  :param z: Z coordinate (defaults to 0 for 2D compatibility)
  :param w: W coordinate (defaults to 0, used for quaternions/homogeneous coords)
  :param name: Optional name for debugging and path operations
  """

  x: float
  y: float
  z: float = 0  # Default 0 enables 2D vector usage
  w: float = 0  # Default 0 for standard 3D vectors, non-zero for quaternions
  name: str = ''

  # Component names for iteration and formatting
  ATTRS: ClassVar[tuple[str, ...]] = ('x', 'y', 'z', 'w')

  # Class-level constants defined after class (Python limitation)
  ZERO: ClassVar[VectorProtocol]
  IDENTITY: ClassVar[VectorProtocol]

  def __post_init__(self) -> None:
    """Convert numeric inputs to float. See VectorProtocol for coordinate details."""
    # Frozen dataclass requires special attribute setting
    object.__setattr__(self, 'x', float(self.x))
    object.__setattr__(self, 'y', float(self.y))
    object.__setattr__(self, 'z', float(self.z))
    object.__setattr__(self, 'w', float(self.w))

  def as_tuple(self) -> tuple[float, float, float, float]:
    """Convert to tuple. See VectorProtocol.as_tuple for details."""
    return self.x, self.y, self.z, self.w

  def magnitude(self) -> float:
    """Calculate magnitude. See VectorProtocol.magnitude for details."""
    return (self.x**2 + self.y**2 + self.z**2 + self.w**2) ** 0.5

  def format(self, dim: int = 2, precision: int = 4, name: bool = True) -> str:
    """Format for display. See VectorProtocol.format for details."""
    # Extract and format only requested dimensions
    f_vals: list[str] = [str(round(getattr(self, a), precision)) for a in self.ATTRS[:dim]]
    nm = f'{self.name}:' if name and self.name else ''
    return f'{nm}[{", ".join(f_vals)}]'

  @classmethod
  def from_input(cls, t: VectorInputType) -> list[VectorProtocol]:
    """Parse various inputs to vectors. See VectorProtocol.from_input for details."""
    results: list[VectorProtocol] = []

    if isinstance(t, dict):
      vector_from_dict = cls.from_dict(t)
      if vector_from_dict is not None:
        results.append(vector_from_dict)
    elif isinstance(t, Vector):
      results.append(t)
    elif isinstance(t, list):
      # Recursively process list elements
      for item in t:
        if isinstance(item, (dict, VectorProtocol, tuple)):
          results.extend(cls.from_input(item))
    elif isinstance(t, tuple):
      results.append(cls.from_tuple(t))
    else:
      raise ValueError(f'Unsupported type for input {type(t)}')

    return results

  @classmethod
  def from_dict(cls, args: dict[str, Any]) -> VectorProtocol | None:
    """Create from dict. See VectorProtocol.from_dict for details."""
    result = None
    if args and 'x' in args and 'y' in args:
      # Required coordinates
      x = float(args['x'])
      y = float(args['y'])
      # Optional coordinates with defaults
      z = float(args.get('z', 0.0))
      w = float(args.get('w', 0.0))
      name = args.get('name', '')  # Preserve name if provided, default to empty string
      result = cls(x, y, z, w, name=name)
    return result

  @classmethod
  def from_args(cls, args: dict[str, Any]) -> VectorProtocol | None:
    """Legacy method - delegates to from_dict."""
    return cls.from_dict(args)

  @classmethod
  def from_tuple(cls, t: tuple[float, ...]) -> VectorProtocol:
    """Create from tuple. See VectorProtocol.from_tuple for details."""
    result: VectorProtocol

    if isinstance(t, VectorProtocol):
      # Already a vector, return as-is
      result = t
    elif isinstance(t, Iterable):
      t_list = list(t)
      if len(t_list) < 2:
        raise ValueError(f'Vector tuple must have at least 2 elements, got {len(t_list)}')

      # Extract coordinates with defaults for missing dimensions
      x = float(t_list[0])
      y = float(t_list[1])
      z = float(t_list[2]) if len(t_list) > 2 else 0.0
      w = float(t_list[3]) if len(t_list) > 3 else 0.0
      result = cls(x, y, z, w)
    else:
      raise ValueError(f'Invalid input type for from_tuple: {type(t)}')

    return result

  @classmethod
  def zero(cls, name: str | None = None) -> VectorProtocol:
    """Create zero vector. See VectorProtocol.zero for details."""
    result = cls(0, 0, name=name) if name else cls.ZERO
    return result

  @classmethod
  def identity(cls, name: str | None = None) -> VectorProtocol:
    """Create identity vector. See VectorProtocol.identity for details."""
    # (1,1,0,0) preserves x,y in multiplication; consider (1,1,1,1) for full 4D
    result = cls(1, 1, name=name) if name else cls.IDENTITY
    return result

  def _transform(self, other: VectorProtocol, op: Callable) -> VectorProtocol:
    """Transform using given other Vector and operation. Preserves other.name per convention."""
    return Vector(
      x=op(self.x, other.x),
      y=op(self.y, other.y),
      z=op(self.z, other.z),
      w=op(self.w, other.w),
      name=other.name,
    )

  def __add__(self, other: VectorProtocol) -> VectorProtocol:
    """Add vectors. See VectorProtocol.__add__ for details."""
    return self._transform(other, operator.add)

  def __mul__(self, other: VectorProtocol) -> VectorProtocol:
    """Multiply component-wise. See VectorProtocol.__mul__ for details."""
    return self._transform(other, operator.mul)

  def __sub__(self, other: VectorProtocol) -> VectorProtocol:
    """Subtract vectors. See VectorProtocol.__sub__ for details."""
    return self._transform(other, operator.sub)

  def __truediv__(self, other: VectorProtocol) -> VectorProtocol:
    """Divide component-wise. See VectorProtocol.__truediv__ for details."""
    return self._transform(other, operator.truediv)

  def __repr__(self) -> str:
    """Developer representation. See VectorProtocol.__repr__ for details."""
    name_part = f', name={self.name!r}' if self.name else ", name=''"
    return f'Vector(x={self.x}, y={self.y}, z={self.z}, w={self.w}{name_part})'

  def __str__(self) -> str:
    """User-friendly format. See VectorProtocol.__str__ for details."""
    return self.format(dim=2, precision=2, name=True)

  def __eq__(self, other: object) -> bool:
    """Compare by components. See VectorProtocol.__eq__ for details."""
    from ...util.math_util import MathUtil

    result = False
    if isinstance(other, VectorProtocol):
      # Compare all components using epsilon-based equality, ignoring name
      result = (
        MathUtil.is_equal(self.x, other.x)
        and MathUtil.is_equal(self.y, other.y)
        and MathUtil.is_equal(self.z, other.z)
        and MathUtil.is_equal(self.w, other.w)
      )
    return result

  def clone(
    self,
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    w: float | None = None,
    name: str | object = _NOT_PROVIDED,
  ) -> VectorProtocol:
    """Create copy with optional overrides. See VectorProtocol.clone for details."""
    result = Vector(
      x if x is not None else self.x,
      y if y is not None else self.y,
      z if z is not None else self.z,
      w if w is not None else self.w,
      name=name if name is not _NOT_PROVIDED else self.name,  # type: ignore
    )
    return result

  def inverse(self) -> VectorProtocol:
    """Create additive inverse. See VectorProtocol.inverse for details."""
    result = Vector(
      x=-self.x,
      y=-self.y,
      z=-self.z,
      w=-self.w,
      name=self.name,
    )
    return result


# Initialize class constants after class definition (Python requires class to exist first)
Vector.ZERO = Vector(0, 0, name='origin')  # Additive identity: v + ZERO = v
Vector.IDENTITY = Vector(1, 1)  # Multiplicative identity for x,y: v * IDENTITY preserves x,y
