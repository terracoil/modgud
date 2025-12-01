"""Vector Implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .vector_protocol import VectorProtocol

VectorSingularType = dict[str, Any] | VectorProtocol | tuple[float]
VectorInputType = list[VectorSingularType] | VectorSingularType


@dataclass(frozen=True)
class Vector(VectorProtocol):
  """Vector class with w (for quaternions and transformations."""

  x: float
  y: float
  z: float = 0
  w: float = 0
  name: str | None = None

  ATTRS = ['x', 'y', 'z', 'w']

  def __post_init__(self) -> None:
    """Ensure all coordinates are floats."""
    # Use object.__setattr__ since dataclass is frozen
    object.__setattr__(self, 'x', float(self.x))
    object.__setattr__(self, 'y', float(self.y))
    object.__setattr__(self, 'z', float(self.z))
    object.__setattr__(self, 'w', float(self.w))

  def as_tuple(self) -> tuple[float, float, float, float]:
    """Return as tuple."""
    return self.x, self.y, self.z, self.w

  def format(self, dim=2, precision: int = 4, name: bool = True) -> str:
    """Format vector as string."""
    f_vals: list[float] = [round(getattr(self, a), precision) for a in self.ATTRS[:dim]]
    nm = f'{self.name}:' if name else ''
    return f'{nm}[{", ".join(f_vals)}]'

  @classmethod
  def from_input(cls, t: VectorInputType) -> list[VectorProtocol]:
    """Create Vector from input."""
    results: list[VectorProtocol] = []

    if isinstance(t, dict):
      vector_from_dict = cls.from_dict(t)
      if vector_from_dict is not None:
        results.append(vector_from_dict)
    elif isinstance(t, Vector):
      results.append(t)
    elif isinstance(t, list):
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
    """Create Vector from args dictionary."""
    result = None
    if args and 'x' in args and 'y' in args:
      x = float(args['x'])
      y = float(args['y'])
      z = float(args.get('z', 0.0))
      w = float(args.get('w', 0.0))
      result = cls(x, y, z, w)
    return result

  @classmethod
  def from_tuple(cls, t: tuple[float, ...]) -> VectorProtocol:
    """Create Vector from tuple."""
    if isinstance(t, VectorProtocol):
      result = t
    elif isinstance(t, Iterable):
      t_list = list(t)
      if len(t_list) < 2:
        raise ValueError(f'Vector tuple must have at least 2 elements, got {len(t_list)}')

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
    """Create zero vector."""
    return cls(0, 0, name=name) if name else cls.ZERO

  @classmethod
  def identity(cls, name: str | None = None) -> VectorProtocol:
    """Create zero vector."""
    return cls(0, 0, name=name) if name else cls.IDENTITY

  @classmethod
  def from_args(cls, args: dict[str, Any]) -> VectorProtocol | None:
    """Legacy method - delegates to from_dict."""
    return cls.from_dict(args)

  def __add__(self, other: Vector) -> VectorProtocol:
    """Add two vectors."""
    return Vector(
      x=self.x + other.x,
      y=self.y + other.y,
      z=self.z + other.z,
      w=self.w + other.w,
      name=other.name,
    )

  def __sub__(self, other: Vector) -> VectorProtocol:
    """Subtract two vectors."""
    return Vector(
      x=self.x - other.x,
      y=self.y - other.y,
      z=self.z - other.z,
      w=self.w - other.w,
      name=other.name,
    )

  def __repr__(self) -> str:
    """Get string representation of Vector."""
    return f'Vector(x={self.x}, y={self.y}, z={self.z}, w={self.w}, name={self.name!r})'

  def __str__(self) -> str:
    """Get string representation of Vector."""
    return f'[x={self.x}, y={self.y}, z={self.z}, w={self.w}, name={self.name!r}]'

  def __eq__(self, other: object) -> bool:
    """Equality comparison."""
    result = False
    if isinstance(other, VectorProtocol):
      result = self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w
    return result


Vector.ZERO = Vector(0, 0)
Vector.IDENTITY = Vector(1, 1)
