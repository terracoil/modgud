"""
Protocol defining the interface for 4D mathematical vectors.

This protocol establishes the contract for vector implementations supporting
2D/3D graphics operations and quaternion mathematics. The 4-component design
(x, y, z, w) enables unified handling of:
- 2D vectors (x, y with z=0, w=0)
- 3D vectors (x, y, z with w=0)
- Quaternions (x, y, z, w all used)
- Homogeneous coordinates for 4x4 matrix transformations
"""

from __future__ import annotations

from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class VectorProtocol(Protocol):
  """
  Interface for 4D mathematical vectors supporting geometric transformations.

  Vectors are immutable to ensure thread safety and predictable behavior in
  transformation pipelines. The protocol supports component-wise arithmetic
  operations essential for graphics programming and physics simulations.

  Attributes:
    x: X-axis component (required for all vectors)
    y: Y-axis component (required for all vectors)
    z: Z-axis component (0 for 2D vectors, used for 3D depth)
    w: W component (0 for standard vectors, non-zero for quaternions/homogeneous coords)
    name: Optional identifier for debugging transformation chains

    ZERO: Class constant representing the additive identity (origin point)
    IDENTITY: Class constant representing the multiplicative identity
    ATTRS: Tuple of component attribute names for iteration

  """

  x: float
  y: float
  z: float
  w: float
  name: str

  ZERO: ClassVar[VectorProtocol]
  IDENTITY: ClassVar[VectorProtocol]
  ATTRS: ClassVar[tuple[str, ...]]

  def as_tuple(self) -> tuple[float, float, float, float]:
    """
    Convert vector to tuple for interoperability with graphics APIs.

    Essential for passing vectors to OpenGL, numpy, or other libraries
    expecting tuple representations. Always returns 4-element tuple
    regardless of the vector's effective dimensionality.

    :returns: (x, y, z, w) tuple of float components
    """

  def format(self, dim: int = 2, precision: int = 4, name: bool = True) -> str:
    """
    Format vector for human-readable display with dimension control.

    Supports debugging by showing only relevant dimensions - useful when
    working with 2D vectors in a 4D implementation. The precision parameter
    helps when comparing vectors that should be equal but have floating
    point differences.

    :param dim: Number of dimensions to display (2, 3, or 4)
    :param precision: Decimal places for component rounding
    :param name: Whether to include vector name in output
    :returns: Formatted string like 'name:[1.0, 2.0]' or '[1.0, 2.0, 0.0]'
    """

  @classmethod
  def from_input(cls, t: Any) -> list[VectorProtocol]:
    """
    Parse various input formats into a list of vectors.

    Provides flexible vector creation from multiple sources, enabling
    batch operations and format conversion. Critical for loading vector
    data from files, user input, or external APIs with varying formats.

    Supported formats:
    - Single vector: dict, tuple, or VectorProtocol instance
    - Multiple vectors: list containing any of the above
    - Nested structures are recursively processed

    :param t: Input data in various formats
    :returns: List of Vector instances (always a list, even for single input)
    :raises ValueError: If input format is not recognized
    """

  @classmethod
  def from_dict(cls, args: dict[str, Any]) -> VectorProtocol | None:
    """
    Create vector from dictionary with named components.

    Enables vector creation from JSON/YAML data or keyword arguments.
    Returns None for invalid input to support optional vector creation
    in batch processing scenarios where some vectors may be incomplete.

    Required keys: 'x', 'y'
    Optional keys: 'z', 'w', 'name'
    Missing z/w default to 0.0

    :param args: Dictionary with coordinate keys
    :returns: Vector instance or None if required coordinates missing
    """

  @classmethod
  def from_tuple(cls, t: tuple[float, ...]) -> VectorProtocol:
    """
    Create vector from coordinate tuple.

    Supports variable-length tuples for dimension flexibility. Essential
    for numpy integration and graphics APIs that return coordinate tuples.
    Automatically pads missing dimensions with zeros.

    :param t: Tuple with 2-4 float values
    :returns: Vector instance with padded dimensions
    :raises ValueError: If tuple has fewer than 2 elements
    """

  @classmethod
  def zero(cls, name: str | None = None) -> VectorProtocol:
    """
    Create zero vector representing the origin point.

    The zero vector is the additive identity: v + zero = v for any vector v.
    Used as default starting point for accumulation operations and as
    the origin reference in coordinate systems.

    :param name: Optional identifier for debugging
    :returns: Vector(0, 0, 0, 0) instance
    """

  @classmethod
  def identity(cls, name: str | None = None) -> VectorProtocol:
    """
    Create multiplicative identity vector.

    Returns (1, 1, 0, 0) which preserves x,y components in multiplication.
    Note: This is NOT a unit vector, but rather the identity for component-wise
    multiplication. Consider if (1, 1, 1, 1) would be more appropriate for
    full 4D identity operations.

    :param name: Optional identifier for debugging
    :returns: Vector(1, 1, 0, 0) instance
    """

  def __add__(self, other: VectorProtocol) -> VectorProtocol:
    """
    Add vectors component-wise for translation operations.

    Vector addition represents translation in space. Each component is
    added independently: result = (x1+x2, y1+y2, z1+z2, w1+w2).
    Essential for moving objects in space and combining displacements.

    :param other: Vector to add
    :returns: New vector representing the sum
    """

  def __sub__(self, other: VectorProtocol) -> VectorProtocol:
    """
    Subtract vectors component-wise for displacement calculations.

    Vector subtraction finds the displacement from other to self.
    Used to calculate distances, directions, and relative positions.
    The result points from 'other' to 'self'.

    :param other: Vector to subtract
    :returns: New vector representing the difference
    """

  def __mul__(self, other: VectorProtocol) -> VectorProtocol:
    """
    Multiply vectors component-wise for scaling operations.

    Component-wise multiplication (Hadamard product) scales each axis
    independently. Used for non-uniform scaling, color mixing in graphics,
    and element-wise transformations. NOT the dot or cross product.

    :param other: Vector with scaling factors
    :returns: New vector with scaled components
    """

  def __truediv__(self, other: VectorProtocol) -> VectorProtocol:
    """
    Divide vectors component-wise for inverse scaling operations.

    Component-wise division inverts scaling operations. Each component
    is divided independently: result = (x1/x2, y1/y2, z1/z2, w1/w2).
    Useful for normalizing by a stop vector or reversing transformations.

    :param other: Vector with divisor components
    :returns: New vector with divided components
    :raises ZeroDivisionError: If any component of other is zero
    """

  def __repr__(self) -> str:
    """
    Return developer-friendly representation for debugging.

    Shows full constructor syntax enabling copy-paste recreation of vectors
    during debugging sessions. Includes all components and name.

    :returns: String like 'Vector(x=1.0, y=2.0, z=0.0, w=0.0, name="test")'
    """

  def __str__(self) -> str:
    """
    Return user-friendly string representation.

    More compact than repr(), suitable for logging and display to end users.
    Shows components in a readable format without constructor details.

    :returns: String like '[x=1.0, y=2.0, z=0.0, w=0.0, name="test"]'
    """

  def __eq__(self, other: object) -> bool:
    """
    Compare vectors by component equality.

    Vectors are equal if all components (x, y, z, w) match exactly.
    Name is intentionally excluded from comparison as it's metadata.
    Note: Uses exact floating-point comparison - consider adding an
    epsilon-based comparison method for geometric calculations.

    :param other: Object to compare with
    :returns: True if all components are exactly equal, False otherwise
    """

  def clone(
    self,
    x: float | None = None,
    y: float | None = None,
    z: float | None = None,
    w: float | None = None,
    name: str = '',
  ) -> VectorProtocol:
    """
    Create a copy of this vector with optional component overrides.

    Enables creation of modified vectors while preserving immutability.
    Any component not specified retains the value from the original vector.
    This method is essential for transformation chains and animation keyframes.

    :param x: Override x component (uses original if None)
    :param y: Override y component (uses original if None)
    :param z: Override z component (uses original if None)
    :param w: Override w component (uses original if None)
    :param name: Override name (uses original if empty string)
    :returns: New vector instance with specified modifications
    """

  def inverse(self) -> VectorProtocol:
    """
    Create the additive inverse (negation) of this vector.

    Returns a new vector with all components negated, representing the
    opposite direction. Essential for vector subtraction implementations
    and directional reversal operations in physics simulations.

    The inverse satisfies: v + v.inverse() = ZERO for any vector v.
    Used in collision response, force cancellation, and backtracking
    algorithms where directional reversal is required.

    :returns: New vector with negated components (-x, -y, -z, -w)
    """
