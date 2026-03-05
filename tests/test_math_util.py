"""Tests for MathUtil.mean and MathUtil.weighted_mean."""

import pytest
from modgud.util.math_util import MathUtil


class TestMean:
  """Tests for MathUtil.mean."""

  def test_single_int(self):
    """Mean of a single int is that value as float."""
    assert MathUtil.mean(5) == 5.0

  def test_single_float(self):
    """Mean of a single float is that value."""
    assert MathUtil.mean(3.14) == 3.14

  def test_multiple_ints(self):
    """Mean of multiple ints."""
    assert MathUtil.mean(2, 4, 6) == 4.0

  def test_multiple_floats(self):
    """Mean of multiple floats."""
    assert MathUtil.mean(1.5, 2.5, 3.0) == pytest.approx(2.333333, rel=1e-5)

  def test_mixed_int_float(self):
    """Mean of mixed int and float arguments."""
    assert MathUtil.mean(1, 2.5, 4) == 2.5

  def test_negative_values(self):
    """Mean with negative values."""
    assert MathUtil.mean(-10, 10) == 0.0

  def test_all_same_values(self):
    """Mean of identical values equals that value."""
    assert MathUtil.mean(7, 7, 7, 7) == 7.0

  def test_all_zeros(self):
    """Mean of all zeros is zero."""
    assert MathUtil.mean(0, 0, 0) == 0.0

  def test_returns_float(self):
    """Mean always returns a float."""
    assert isinstance(MathUtil.mean(2, 4), float)

  def test_empty_args_raises(self):
    """Mean with no arguments raises ValueError."""
    with pytest.raises(ValueError, match='mean\\(\\) requires at least one argument'):
      MathUtil.mean()


class TestWeightedMean:
  """Tests for MathUtil.weighted_mean."""

  def test_basic_weighted_mean(self):
    """Weighted mean with simple weights."""
    assert MathUtil.weighted_mean(80, 90, weights=[0.3, 0.7]) == pytest.approx(87.0)

  def test_integer_weights(self):
    """Weighted mean with integer weights."""
    assert MathUtil.weighted_mean(10, 20, 30, weights=[1, 2, 3]) == pytest.approx(
      23.333333, rel=1e-5
    )

  def test_equal_weights_matches_mean(self):
    """Equal weights should produce the same result as arithmetic mean."""
    values = (3, 7, 11, 15)
    expected = MathUtil.mean(*values)

    assert MathUtil.weighted_mean(*values, weights=[1, 1, 1, 1]) == pytest.approx(expected)

  def test_single_value(self):
    """Weighted mean of a single value equals that value regardless of weight."""
    assert MathUtil.weighted_mean(42, weights=[5]) == pytest.approx(42.0)

  def test_zero_weight_excludes_value(self):
    """A zero-weighted value does not affect the result."""
    assert MathUtil.weighted_mean(100, 50, weights=[0, 1]) == pytest.approx(50.0)

  def test_mixed_int_float_values_and_weights(self):
    """Weighted mean with mixed numeric types in both values and weights."""
    assert MathUtil.weighted_mean(2, 3.5, weights=[0.5, 1.5]) == pytest.approx(3.125)

  def test_weights_as_tuple(self):
    """Weights can be any Sequence, not just list."""
    assert MathUtil.weighted_mean(10, 20, weights=(3, 7)) == pytest.approx(17.0)

  def test_returns_float(self):
    """Weighted mean always returns a float."""
    assert isinstance(MathUtil.weighted_mean(2, 4, weights=[1, 1]), float)

  def test_empty_args_raises(self):
    """Weighted mean with no arguments raises ValueError."""
    with pytest.raises(ValueError, match='weighted_mean\\(\\) requires at least one argument'):
      MathUtil.weighted_mean(weights=[1])

  def test_mismatched_weights_length_raises(self):
    """Weights length must match number of arguments."""
    with pytest.raises(ValueError, match='weights must have the same length as arguments'):
      MathUtil.weighted_mean(1, 2, 3, weights=[0.5, 0.5])

  def test_all_zero_weights_raises(self):
    """All-zero weights raises ValueError."""
    with pytest.raises(ValueError, match='sum of weights must be greater than zero'):
      MathUtil.weighted_mean(1, 2, weights=[0, 0])

  def test_near_zero_weight_sum_raises(self):
    """Weight sum below EPSILON raises ValueError."""
    tiny = MathUtil.EPSILON / 10
    with pytest.raises(ValueError, match='sum of weights must be greater than zero'):
      MathUtil.weighted_mean(1, 2, weights=[tiny, 0])
