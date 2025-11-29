"""Comprehensive tests for Lerper implementation."""


import pytest
from modgud.util import Lerper, LerpStrategy, Vector
from modgud.util.math_util import MathUtil


class TestLerperConstruction:
  """Test Lerper construction and validation."""

  def test_basic_construction(self) -> None:
    """Test basic Lerper construction with numeric values."""
    lerper = Lerper(start=0.0, stop=10.0)
    assert lerper.start == 0.0
    assert lerper.stop == 10.0
    assert lerper.strategy == LerpStrategy.LINEAR

  def test_construction_with_strategy(self) -> None:
    """Test Lerper construction with specific strategy."""
    lerper = Lerper(start=0, stop=100, strategy=LerpStrategy.SINE)
    assert lerper.start == 0
    assert lerper.stop == 100
    assert lerper.strategy == LerpStrategy.SINE

  def test_construction_without_stop(self) -> None:
    """Test Lerper construction without stop value."""
    lerper = Lerper(start=5.0)
    assert lerper.start == 5.0
    assert lerper.stop is None
    assert lerper.strategy == LerpStrategy.LINEAR

  def test_construction_with_vectors(self) -> None:
    """Test Lerper construction with Vector objects."""
    start = Vector(0, 0)
    stop = Vector(10, 10, 10, 10)
    lerper = Lerper(start=start, stop=stop)
    assert lerper.start is start
    assert lerper.stop is stop

  def test_invalid_start_type(self) -> None:
    """Test Lerper construction with invalid start type."""
    with pytest.raises(TypeError, match='start must be int, float, or VectorProtocol'):
      Lerper(start='invalid')  # type: ignore

  def test_mismatched_types(self) -> None:
    """Test Lerper construction with mismatched types."""
    with pytest.raises(TypeError, match='start and stop must be the same type'):
      Lerper(start=Vector(0, 0), stop=5.0)  # type: ignore

  def test_numeric_type_mixing_allowed(self) -> None:
    """Test that int and float can be mixed."""
    lerper = Lerper(start=0, stop=10.0)  # int and float mix
    assert lerper.start == 0
    assert lerper.stop == 10.0


class TestNumericLinearInterpolation:
  """Test linear interpolation with numeric values."""

  def test_float_linear_interpolation(self) -> None:
    """Test basic linear interpolation with floats."""
    lerper = Lerper(start=0.0, stop=10.0)
    assert lerper.lerp(0.0) == 0.0
    assert lerper.lerp(0.5) == 5.0
    assert lerper.lerp(1.0) == 10.0

  def test_int_linear_interpolation(self) -> None:
    """Test linear interpolation with integers."""
    lerper = Lerper(start=0, stop=10)
    assert lerper.lerp(0.0) == 0
    assert lerper.lerp(0.5) == 5
    assert lerper.lerp(1.0) == 10
    # Verify type preservation
    assert isinstance(lerper.lerp(0.5), int)

  def test_negative_values(self) -> None:
    """Test interpolation with negative values."""
    lerper = Lerper(start=-10.0, stop=10.0)
    assert lerper.lerp(0.0) == -10.0
    assert lerper.lerp(0.5) == 0.0
    assert lerper.lerp(1.0) == 10.0

  def test_reverse_interpolation(self) -> None:
    """Test interpolation from larger to smaller value."""
    lerper = Lerper(start=100.0, stop=0.0)
    assert lerper.lerp(0.0) == 100.0
    assert lerper.lerp(0.5) == 50.0
    assert lerper.lerp(1.0) == 0.0

  def test_small_range(self) -> None:
    """Test interpolation with very small range."""
    lerper = Lerper(start=0.0, stop=0.001)
    assert lerper.lerp(0.0) == 0.0
    assert lerper.lerp(0.5) == 0.0005
    assert lerper.lerp(1.0) == 0.001

  def test_large_values(self) -> None:
    """Test interpolation with large values."""
    lerper = Lerper(start=0.0, stop=1e10)
    assert lerper.lerp(0.0) == 0.0
    assert lerper.lerp(0.5) == 5e9
    assert lerper.lerp(1.0) == 1e10


class TestVectorInterpolation:
  """Test interpolation with Vector objects."""

  def test_basic_vector_interpolation(self) -> None:
    """Test basic vector interpolation."""
    start = Vector(0, 0, 0, 0)
    stop = Vector(10, 20, 30, 40)
    lerper = Lerper(start=start, stop=stop)

    mid = lerper.lerp(0.5)
    assert mid.x == 5.0
    assert mid.y == 10.0
    assert mid.z == 15.0
    assert mid.w == 20.0

  def test_vector_interpolation_endpoints(self) -> None:
    """Test vector interpolation at endpoints."""
    start = Vector(1, 2, 3, 4)
    stop = Vector(5, 6, 7, 8)
    lerper = Lerper(start=start, stop=stop)

    result_start = lerper.lerp(0.0)
    assert result_start.x == 1.0
    assert result_start.y == 2.0

    result_end = lerper.lerp(1.0)
    assert result_end.x == 5.0
    assert result_end.y == 6.0

  def test_vector_name_preservation(self) -> None:
    """Test that vector name is preserved from start vector."""
    start = Vector(0, 0, name='start_vector')
    stop = Vector(10, 10, name='stop_vector')
    lerper = Lerper(start=start, stop=stop)

    result = lerper.lerp(0.5)
    assert result.name == 'start_vector'

  def test_negative_vector_interpolation(self) -> None:
    """Test vector interpolation with negative coordinates."""
    start = Vector(-10, -20, -30, -40)
    stop = Vector(10, 20, 30, 40)
    lerper = Lerper(start=start, stop=stop)

    mid = lerper.lerp(0.5)
    assert mid.x == 0.0
    assert mid.y == 0.0
    assert mid.z == 0.0
    assert mid.w == 0.0


class TestInterpolationStrategies:
  """Test different interpolation strategies."""

  def test_sine_strategy(self) -> None:
    """Test sine interpolation strategy."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.SINE)
    # Sin(45°) ≈ 0.707
    result = lerper.lerp(0.5)
    assert abs(result - 0.7071) < 0.001
    # Sin(30°) = 0.5
    result = lerper.lerp(1 / 3)
    assert abs(result - 0.5) < 0.001

  def test_cosine_strategy(self) -> None:
    """Test cosine interpolation strategy."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.COSINE)
    # 1 - cos(45°) ≈ 0.293
    result = lerper.lerp(0.5)
    assert abs(result - 0.2929) < 0.001

  def test_squared_strategy(self) -> None:
    """Test squared interpolation strategy."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.SQUARED)
    assert lerper.lerp(0.0) == 0.0
    assert lerper.lerp(0.5) == 25.0  # 0.5² * 100 = 25
    assert lerper.lerp(1.0) == 100.0

  def test_cubed_strategy(self) -> None:
    """Test cubed interpolation strategy."""
    lerper = Lerper(start=0.0, stop=1000.0, strategy=LerpStrategy.CUBED)
    assert lerper.lerp(0.0) == 0.0
    assert lerper.lerp(0.5) == 125.0  # 0.5³ * 1000 = 125
    assert lerper.lerp(1.0) == 1000.0

  def test_sigmoid_strategy(self) -> None:
    """Test sigmoid interpolation strategy."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.SIGMOID)
    # Sigmoid should be ~0.5 at midpoint
    result = lerper.lerp(0.5)
    assert abs(result - 0.5) < 0.001
    # Should start slow
    assert lerper.lerp(0.1) < 0.01
    # Should end slow
    assert lerper.lerp(0.9) > 0.99

  def test_strategies_with_vectors(self) -> None:
    """Test that strategies work with vectors."""
    start = Vector(0, 0)
    stop = Vector(100, 100)

    # Linear
    lerper = Lerper(start=start, stop=stop, strategy=LerpStrategy.LINEAR)
    mid = lerper.lerp(0.5)
    assert mid.x == 50.0 and mid.y == 50.0

    # Squared
    lerper = Lerper(start=start, stop=stop, strategy=LerpStrategy.SQUARED)
    mid = lerper.lerp(0.5)
    assert mid.x == 25.0 and mid.y == 25.0


class TestReverseInterpolation:
  """Test reverse interpolation (rlerp)."""

  def test_numeric_rlerp(self) -> None:
    """Test basic numeric reverse interpolation."""
    lerper = Lerper(start=0.0, stop=100.0)
    assert abs(lerper.rlerp(0.0) - 0.0) < MathUtil.EPSILON
    assert abs(lerper.rlerp(50.0) - 0.5) < MathUtil.EPSILON
    assert abs(lerper.rlerp(100.0) - 1.0) < MathUtil.EPSILON

  def test_int_rlerp(self) -> None:
    """Test reverse interpolation with integers."""
    lerper = Lerper(start=0, stop=10)
    assert abs(lerper.rlerp(5) - 0.5) < MathUtil.EPSILON
    assert abs(lerper.rlerp(0) - 0.0) < MathUtil.EPSILON
    assert abs(lerper.rlerp(10) - 1.0) < MathUtil.EPSILON

  def test_negative_rlerp(self) -> None:
    """Test reverse interpolation with negative values."""
    lerper = Lerper(start=-100.0, stop=100.0)
    assert abs(lerper.rlerp(-100.0) - 0.0) < MathUtil.EPSILON
    assert abs(lerper.rlerp(0.0) - 0.5) < MathUtil.EPSILON
    assert abs(lerper.rlerp(100.0) - 1.0) < MathUtil.EPSILON

  def test_vector_rlerp(self) -> None:
    """Test reverse interpolation with vectors using magnitude."""
    start = Vector(0, 0, 0, 0)  # magnitude 0
    stop = Vector(3, 4, 0, 0)  # magnitude 5
    lerper = Lerper(start=start, stop=stop)

    # Test with vector at midpoint magnitude (2.5)
    mid = Vector(1.5, 2, 0, 0)  # magnitude 2.5
    result = lerper.rlerp(mid)
    assert abs(result - 0.5) < 0.01

  def test_rlerp_divide_by_zero(self) -> None:
    """Test rlerp with identical start and stop values."""
    lerper = Lerper(start=5.0, stop=5.0)
    with pytest.raises(ValueError, match='too close for reverse interpolation'):
      lerper.rlerp(5.0)

  def test_vector_rlerp_similar_magnitudes(self) -> None:
    """Test vector rlerp with similar magnitudes."""
    start = Vector(1, 0, 0, 0)
    stop = Vector(0, 1, 0, 0)  # Same magnitude, different direction
    lerper = Lerper(start=start, stop=stop)

    with pytest.raises(ValueError, match='similar magnitudes'):
      lerper.rlerp(Vector(0.5, 0.5, 0, 0))

  def test_rlerp_out_of_range(self) -> None:
    """Test rlerp with values outside range."""
    lerper = Lerper(start=0.0, stop=10.0)
    # Should clamp to [0, 1]
    assert lerper.rlerp(-5.0) == 0.0
    assert lerper.rlerp(15.0) == 1.0


class TestStrategiesRoundTrip:
  """Test that lerp followed by rlerp returns original percentage."""

  def test_linear_round_trip(self) -> None:
    """Test linear strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.LINEAR)
    for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < MathUtil.EPSILON

  def test_sine_round_trip(self) -> None:
    """Test sine strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.SINE)
    for pct in [0.1, 0.3, 0.5, 0.7, 0.9]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < 0.001

  def test_cosine_round_trip(self) -> None:
    """Test cosine strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.COSINE)
    for pct in [0.1, 0.3, 0.5, 0.7, 0.9]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < 0.001

  def test_squared_round_trip(self) -> None:
    """Test squared strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.SQUARED)
    for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < MathUtil.EPSILON

  def test_cubed_round_trip(self) -> None:
    """Test cubed strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.CUBED)
    for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < 0.001

  def test_sigmoid_round_trip(self) -> None:
    """Test sigmoid strategy round trip."""
    lerper = Lerper(start=0.0, stop=100.0, strategy=LerpStrategy.SIGMOID)
    # Skip edge values for sigmoid due to numerical precision
    for pct in [0.2, 0.4, 0.5, 0.6, 0.8]:
      value = lerper.lerp(pct)
      recovered_pct = lerper.rlerp(value)
      assert abs(recovered_pct - pct) < 0.01


class TestValidation:
  """Test validation and error handling."""

  def test_lerp_without_stop(self) -> None:
    """Test lerp without stop value."""
    lerper = Lerper(start=0.0)
    with pytest.raises(ValueError, match='stop value is required'):
      lerper.lerp(0.5)

  def test_rlerp_without_stop(self) -> None:
    """Test rlerp without stop value."""
    lerper = Lerper(start=0.0)
    with pytest.raises(ValueError, match='stop value is required'):
      lerper.rlerp(5.0)

  def test_lerp_invalid_percentage(self) -> None:
    """Test lerp with percentage outside [0, 1]."""
    lerper = Lerper(start=0.0, stop=10.0)

    with pytest.raises(ValueError, match='pct must be between 0.0 and 1.0'):
      lerper.lerp(-0.1)

    with pytest.raises(ValueError, match='pct must be between 0.0 and 1.0'):
      lerper.lerp(1.1)

  def test_type_mismatch_in_operations(self) -> None:
    """Test type mismatch during operations."""
    lerper = Lerper(start=0.0, stop=10.0)

    # rlerp with wrong type
    with pytest.raises(TypeError, match='Type mismatch'):
      lerper.rlerp(Vector(5, 5))  # type: ignore


class TestRangeMethod:
  """Test the range class method."""

  def test_basic_range(self) -> None:
    """Test basic range generation."""
    values = Lerper.range(0, 10, steps=11)
    assert len(values) == 11
    assert values[0] == 0
    assert values[5] == 5
    assert values[10] == 10

  def test_range_with_strategy(self) -> None:
    """Test range generation with specific strategy."""
    values = Lerper.range(0.0, 1.0, steps=5, strategy=LerpStrategy.SQUARED)
    assert len(values) == 5
    assert values[0] == 0.0
    assert abs(values[1] - 0.0625) < 0.001  # (1/4)² = 0.0625
    assert abs(values[2] - 0.25) < 0.001  # (2/4)² = 0.25
    assert values[4] == 1.0

  def test_range_with_vectors(self) -> None:
    """Test range generation with vectors."""
    start = Vector(0, 0)
    stop = Vector(10, 20)
    values = Lerper.range(start, stop, steps=3)

    assert len(values) == 3
    assert values[0].x == 0.0 and values[0].y == 0.0
    assert values[1].x == 5.0 and values[1].y == 10.0
    assert values[2].x == 10.0 and values[2].y == 20.0

  def test_range_minimum_steps(self) -> None:
    """Test range with minimum steps."""
    values = Lerper.range(0, 10, steps=2)
    assert len(values) == 2
    assert values[0] == 0
    assert values[1] == 10

  def test_range_invalid_steps(self) -> None:
    """Test range with invalid step count."""
    with pytest.raises(ValueError, match='steps must be at least 2'):
      Lerper.range(0, 10, steps=1)


class TestEdgeCases:
  """Test edge cases and special scenarios."""

  def test_zero_range_interpolation(self) -> None:
    """Test interpolation when start equals stop."""
    lerper = Lerper(start=5.0, stop=5.0)
    assert lerper.lerp(0.0) == 5.0
    assert lerper.lerp(0.5) == 5.0
    assert lerper.lerp(1.0) == 5.0

  def test_type_preservation_rounding(self) -> None:
    """Test that int type is preserved even with rounding."""
    lerper = Lerper(start=0, stop=10)
    # 0.33 * 10 = 3.3, should round to 3
    result = lerper.lerp(0.33)
    assert isinstance(result, int)
    assert result == 3

  def test_large_number_precision(self) -> None:
    """Test precision with large numbers."""
    lerper = Lerper(start=1e15, stop=1e15 + 1000)
    result = lerper.lerp(0.5)
    assert abs(result - (1e15 + 500)) < 1.0

  def test_hex_word_values(self) -> None:
    """Test with hex word test data (project convention)."""
    # Using "words" made from hex digits
    lerper = Lerper(start=0xDEAD, stop=0xBEEF)
    mid = lerper.lerp(0.5)
    expected = (0xDEAD + 0xBEEF) / 2
    assert abs(mid - expected) < 1.0

  def test_inverse_strategy_edge_cases(self) -> None:
    """Test inverse strategy transformations at edges."""
    # Sigmoid at edges
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.SIGMOID)
    assert lerper._apply_inverse_strategy(0.0) == 0.0
    assert lerper._apply_inverse_strategy(1.0) == 1.0

    # Values are clamped
    assert lerper._apply_inverse_strategy(-0.1) == 0.0
    assert lerper._apply_inverse_strategy(1.1) == 1.0


class TestMathematicalCorrectness:
  """Test mathematical correctness of interpolation strategies."""

  def test_sine_curve_properties(self) -> None:
    """Test that sine curve has expected properties."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.SINE)

    # Should start at 0
    assert lerper._apply_strategy(0.0) == 0.0

    # Should end at 1
    assert abs(lerper._apply_strategy(1.0) - 1.0) < MathUtil.EPSILON

    # Should be monotonically increasing
    prev = 0.0
    for i in range(1, 11):
      curr = lerper._apply_strategy(i / 10)
      assert curr > prev
      prev = curr

  def test_cosine_curve_properties(self) -> None:
    """Test that cosine curve has expected properties."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.COSINE)

    # Should start at 0
    assert lerper._apply_strategy(0.0) == 0.0

    # Should end at 1
    assert abs(lerper._apply_strategy(1.0) - 1.0) < MathUtil.EPSILON

    # Cosine easing: slow start, fast end (derivative larger at end)
    # Using 1 - cos(x * π/2) means acceleration at the end
    d1 = lerper._apply_strategy(0.1) - lerper._apply_strategy(0.0)
    d2 = lerper._apply_strategy(1.0) - lerper._apply_strategy(0.9)
    assert d1 < d2  # Cosine has slow start, fast end

  def test_sigmoid_symmetry(self) -> None:
    """Test that sigmoid is symmetric around 0.5."""
    lerper = Lerper(start=0.0, stop=1.0, strategy=LerpStrategy.SIGMOID)

    # Test symmetry around midpoint
    for offset in [0.1, 0.2, 0.3, 0.4]:
      low = lerper._apply_strategy(0.5 - offset)
      high = lerper._apply_strategy(0.5 + offset)
      # Should be symmetric: low + high ≈ 1.0
      assert abs((low + high) - 1.0) < 0.01
