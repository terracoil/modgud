"""Line geometry with optional noise application and smoothing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from modgud.domain.ports import NoisePort, ShapePort, VectorPort

from .vector import Vector


@dataclass(frozen=True)
class Line(ShapePort):
  """Line geometry class with support for noise application and optional smoothing."""

  start: VectorPort
  stop: VectorPort
  noise: NoisePort | None = None
  noise_segments: int = 100
  smoothing_factor: float = 0.0  # 0.0 = no smoothing, 1.0 = maximum smoothing

  def build_shape(self) -> Sequence[VectorPort]:
    """
    Build a line from start to stop with optional noise application and smoothing.

    :returns: Sequence of vectors representing the noisy line
    """
    if self.noise is None:
      return [self.start, self.stop]

    result: list[VectorPort] = [self.start]

    # Generate points along the line with noise applied
    for i in range(1, self.noise_segments + 1):
      t = i / (self.noise_segments + 1)

      # Linear interpolation between start and stop
      base_point = Vector(
        self.start.x + t * (self.stop.x - self.start.x),
        self.start.y + t * (self.stop.y - self.start.y),
        self.start.z + t * (self.stop.z - self.start.z),
        self.start.w + t * (self.stop.w - self.start.w),
      )

      # Apply noise displacement perpendicular to the line direction
      direction = Vector(
        self.stop.x - self.start.x,
        self.stop.y - self.start.y,
        self.stop.z - self.start.z,
        self.stop.w - self.start.w,
      )

      # Get perpendicular vector (2D case, rotate 90 degrees)
      if direction.magnitude() > 0:
        perpendicular = Vector(-direction.y, direction.x, direction.z, direction.w)

        # Normalize perpendicular vector
        perp_magnitude = perpendicular.magnitude()
        if perp_magnitude > 0:
          perpendicular = Vector(
            perpendicular.x / perp_magnitude,
            perpendicular.y / perp_magnitude,
            perpendicular.z / perp_magnitude,
            perpendicular.w / perp_magnitude,
          )

          # Apply noise
          noise_value = self.noise.noise2d(base_point.x, base_point.y)
          displacement = Vector(
            perpendicular.x * noise_value,
            perpendicular.y * noise_value,
            perpendicular.z * noise_value,
            perpendicular.w * noise_value,
          )

          noisy_point = base_point + displacement
          result.append(noisy_point)
        else:
          result.append(base_point)
      else:
        result.append(base_point)

    result.append(self.stop)

    # Apply smoothing if requested
    if self.smoothing_factor > 0.0:
      result = self._apply_smoothing(result)

    return result

  def _apply_smoothing(self, points: list[VectorPort]) -> list[VectorPort]:
    """
    Apply smoothing to the point sequence using moving average.

    :param points: Original points
    :returns: Smoothed points
    """
    if len(points) <= 2:
      return points

    smoothed: list[VectorPort] = [points[0]]  # Keep first point unchanged

    window_size = max(1, int(len(points) * self.smoothing_factor * 0.1))

    for i in range(1, len(points) - 1):
      # Calculate window bounds
      start_idx = max(0, i - window_size)
      end_idx = min(len(points), i + window_size + 1)

      # Calculate average position
      sum_x = sum_y = sum_z = sum_w = 0.0
      count = 0

      for j in range(start_idx, end_idx):
        sum_x += points[j].x
        sum_y += points[j].y
        sum_z += points[j].z
        sum_w += points[j].w
        count += 1

      if count > 0:
        smoothed_point = Vector(sum_x / count, sum_y / count, sum_z / count, sum_w / count)
        smoothed.append(smoothed_point)
      else:
        smoothed.append(points[i])

    smoothed.append(points[-1])  # Keep last point unchanged
    return smoothed
