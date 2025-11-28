"""Strategy for interpolation curve shapes."""

from enum import Enum, auto


class LerpStrategy(Enum):
  """Strategy for interpolation curve shapes."""

  LINEAR = auto()  # Linear interpolation (constant speed)
  SINE = auto()  # Sine curve (slow origin, fast middle)
  COSINE = auto()  # Cosine curve (fast origin, slow end)
  SQUARED = auto()  # Quadratic curve (accelerating)
  CUBED = auto()  # Cubic curve (smooth acceleration)
  SIGMOID = auto()  # S-curve (smooth origin and end)
