class MathUtil:
  """Mathematical utility functions for clamping, min/max, and percentage calculations."""

  EPSILON: float = 1e-6
  Numeric = int | float

  @classmethod
  def clamp(cls, value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max bounds and return it.
      :value: The value to clamp
      :min_val: Minimum allowed value
      :max_val: Maximum allowed value.

    Examples:
        MathUtil.clamp(5, 0, 10) # 5
        MathUtil.clamp(-5, 0, 10) # 0
        MathUtil.clamp(15, 0, 10) # 10

    """
    return max(min_val, min(value, max_val))

  @classmethod
  def is_even(cls, val: int) -> bool:
    return val % 2 == 0

  @classmethod
  def minmax_range(
    cls, args: list[Numeric], negative_lower: bool = False
  ) -> tuple[Numeric, Numeric]:
    """Return min and max of arguments with optional negative lower bound."""
    lower, upper = cls.minmax(*args)

    return cls.safe_negative(lower, negative_lower), upper

  @classmethod
  def minmax(cls, *args: Numeric) -> tuple[Numeric, Numeric]:
    """
    Return the minimum and maximum of a dynamic number of arguments.
      :args: Variable number of int or float arguments.

    Raises:
        ValueError: If no arguments are provided

    """
    if not args:
      raise ValueError('minmax() requires at least one argument')

    return min(args), max(args)

  @classmethod
  def safe_negative(cls, value: Numeric, neg: bool = True) -> Numeric:
    """
    Return the negative of a dynamic number only if neg is True.
    :param value: Value to check and convert
    :param neg: Whether to convert to negative or not.
    """
    return -value if neg else value

  @classmethod
  def percent(cls, val: int | float, max_val: int | float) -> float:
    """Calculate percentage of val relative to max_val."""
    if max_val < cls.EPSILON:
      raise ValueError('max_val is too small; must be greater than 0.s')
    return val / float(max_val)

  @classmethod
  def is_equal(cls, v: float | int, value: float | int) -> bool:
    """Check if two floats are equal within epsilon (Anything less than EPSILON of difference)."""
    return abs(v - value) < cls.EPSILON

  @classmethod
  def is_zero(cls, v: float | int) -> bool:
    """Check if a float is close to zero.  (Anything less than EPSILON of difference)."""
    return cls.is_equal(v, 0.0)

  @classmethod
  def lt(cls, v: float | int, value: float | int) -> bool:
    """
    Check if v is definitely less than value (not within epsilon tolerance).

    Uses epsilon-aware comparison to determine if v is significantly less than value,
    accounting for floating-point precision limitations.

    :param v: The first value to compare
    :type v: float | int
    :param value: The second value to compare against
    :type value: float | int
    :returns: True if v is definitely less than value (v < value - EPSILON), False otherwise
    :rtype: bool
    """
    return v < (value - cls.EPSILON)

  @classmethod
  def gt(cls, v: float | int, value: float | int) -> bool:
    """
    Check if v is definitely greater than value (not within epsilon tolerance).

    Uses epsilon-aware comparison to determine if v is significantly greater than value,
    accounting for floating-point precision limitations.

    :param v: The first value to compare
    :type v: float | int
    :param value: The second value to compare against
    :type value: float | int
    :returns: True if v is definitely greater than value (v > value + EPSILON), False otherwise
    :rtype: bool
    """
    return v > (value + cls.EPSILON)

  @classmethod
  def lte(cls, v: float | int, value: float | int) -> bool:
    """
    Check if v is less than or approximately equal to value (within epsilon tolerance).

    Uses epsilon-aware comparison to determine if v is less than or close enough to value
    to be considered equal, accounting for floating-point precision limitations.

    :param v: The first value to compare
    :type v: float | int
    :param value: The second value to compare against
    :type value: float | int
    :returns: True if v is less than or approximately equal to value (v <= value + EPSILON), False otherwise
    :rtype: bool
    """
    return v <= (value + cls.EPSILON)

  @classmethod
  def gte(cls, v: float | int, value: float | int) -> bool:
    """
    Check if v is greater than or approximately equal to value (within epsilon tolerance).

    Uses epsilon-aware comparison to determine if v is greater than or close enough to value
    to be considered equal, accounting for floating-point precision limitations.

    :param v: The first value to compare
    :type v: float | int
    :param value: The second value to compare against
    :type value: float | int
    :returns: True if v is greater than or approximately equal to value (v >= value - EPSILON), False otherwise
    :rtype: bool
    """
    return v >= (value - cls.EPSILON)

  @classmethod
  def pct(cls, n: float | int, precision: int = 2) -> str:
    """Convert number to percentage string with specified precision."""
    return str(round(n * 100, precision))
