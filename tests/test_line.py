"""Test the Line geometry class."""

import pytest
from modgud.util.geo import Line, SimplexNoise, Vector


class TestLine:
  """Test the Line class functionality."""

  def test_line_without_noise(self):
    """Test Line with no noise returns start and end points."""
    start = Vector(0, 0)
    end = Vector(10, 5)
    line = Line(start=start, stop=end)

    result = line.build_shape()

    assert len(result) == 2
    assert result[0] == start
    assert result[1] == end

  def test_line_with_noise(self):
    """Test Line with noise generates intermediate points."""
    start = Vector(0, 0)
    end = Vector(10, 5)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=1.0)
    line = Line(start=start, stop=end, noise=noise, noise_segments=10)

    result = line.build_shape()

    # Should have start + intermediate points + end
    assert len(result) == 12  # 10 segments + start + end
    assert result[0] == start
    assert result[-1] == end

  def test_line_smoothing(self):
    """Test Line with smoothing applied."""
    start = Vector(0, 0)
    end = Vector(10, 5)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=2.0)
    line = Line(start=start, stop=end, noise=noise, noise_segments=10, smoothing_factor=0.5)

    result = line.build_shape()

    # Should still have all points
    assert len(result) == 12
    assert result[0] == start
    assert result[-1] == end

  def test_line_zero_length(self):
    """Test Line with zero length (start == end)."""
    start = Vector(5, 5)
    end = Vector(5, 5)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=1.0)
    line = Line(start=start, stop=end, noise=noise, noise_segments=5)

    result = line.build_shape()

    # Should handle zero-length line gracefully
    assert len(result) == 7  # 5 segments + start + end
    assert result[0] == start
    assert result[-1] == end
    # All intermediate points should be at same position as start/end
    for point in result[1:-1]:
      assert point == start

  def test_line_parameters(self):
    """Test Line with different parameter combinations."""
    start = Vector(0, 0)
    end = Vector(20, 10)
    noise = SimplexNoise(seed=123, scale=0.2, amplitude=3.0)

    # Test with different segment counts
    line1 = Line(start=start, stop=end, noise=noise, noise_segments=5)
    result1 = line1.build_shape()
    assert len(result1) == 7  # 5 segments + start + end

    line2 = Line(start=start, stop=end, noise=noise, noise_segments=20)
    result2 = line2.build_shape()
    assert len(result2) == 22  # 20 segments + start + end

  def test_line_noise_perpendicular_displacement(self):
    """Test that noise is applied perpendicular to line direction."""
    # Horizontal line
    start = Vector(0, 5)
    end = Vector(10, 5)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=2.0)
    line = Line(start=start, stop=end, noise=noise, noise_segments=5)

    result = line.build_shape()

    # All points should have same x progression but varying y
    assert result[0].y == 5  # Start point
    assert result[-1].y == 5  # End point

    # Intermediate points should have different y values (due to noise)
    y_values = [point.y for point in result[1:-1]]
    # At least some points should be displaced from y=5
    assert any(abs(y - 5) > 0.1 for y in y_values)

  def test_line_smoothing_reduces_variation(self):
    """Test that smoothing reduces variation in the line."""
    start = Vector(0, 0)
    end = Vector(20, 0)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=5.0)

    # Line without smoothing
    line_rough = Line(start=start, stop=end, noise=noise, noise_segments=20, smoothing_factor=0.0)
    result_rough = line_rough.build_shape()

    # Line with smoothing
    line_smooth = Line(start=start, stop=end, noise=noise, noise_segments=20, smoothing_factor=0.8)
    result_smooth = line_smooth.build_shape()

    # Calculate variation (standard deviation of y values)
    rough_y_values = [p.y for p in result_rough[1:-1]]
    smooth_y_values = [p.y for p in result_smooth[1:-1]]

    rough_variation = sum(
      (y - sum(rough_y_values) / len(rough_y_values)) ** 2 for y in rough_y_values
    )
    smooth_variation = sum(
      (y - sum(smooth_y_values) / len(smooth_y_values)) ** 2 for y in smooth_y_values
    )

    # Smoothed line should have less variation
    assert smooth_variation < rough_variation

  def test_line_immutability(self):
    """Test that Line class is immutable."""
    start = Vector(0, 0)
    end = Vector(10, 5)
    noise = SimplexNoise(seed=42)
    line = Line(start=start, stop=end, noise=noise)

    # Should not be able to modify attributes (dataclass frozen=True)
    with pytest.raises(AttributeError):
      line.start = Vector(1, 1)  # type: ignore

    with pytest.raises(AttributeError):
      line.noise_segments = 200  # type: ignore

  def test_line_edge_cases(self):
    """Test Line with edge case parameters."""
    start = Vector(0, 0)
    end = Vector(10, 5)
    noise = SimplexNoise(seed=42, scale=0.1, amplitude=0.1)  # Very small amplitude

    # Very few segments
    line1 = Line(start=start, stop=end, noise=noise, noise_segments=1)
    result1 = line1.build_shape()
    assert len(result1) == 3  # start + 1 segment + end

    # Very high smoothing
    line2 = Line(start=start, stop=end, noise=noise, noise_segments=10, smoothing_factor=1.0)
    result2 = line2.build_shape()
    assert len(result2) == 12  # All points should still be there
