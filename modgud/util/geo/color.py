"""Color representation with RGBA float components and color theory operations."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Callable, ClassVar

from .types import HexMetadata, SimpleNum


class GrayscaleAlgorithm(StrEnum):
  """Algorithm for converting color to grayscale."""

  LIGHTNESS = auto()
  AVERAGE = auto()
  LUMINOSITY = auto()


class HarmonyType(StrEnum):
  """Color harmony scheme type."""

  COMPLEMENTARY = auto()  # 2 colors: 0, 180
  SPLIT_COMPLEMENTARY = auto()  # 3 colors: 0, 150, 210
  ANALOGOUS = auto()  # 3 colors: -30, 0, +30
  TRIADIC = auto()  # 3 colors: 0, 120, 240
  TETRADIC_SQUARE = auto()  # 4 colors: 0, 90, 180, 270
  TETRADIC_RECTANGULAR = auto()  # 4 colors: 0, 60, 180, 240


class HarmonyMethod(StrEnum):
  """Algorithm for calculating color harmonies."""

  STANDARD = auto()  # Simple hue rotation, preserve S/L
  PERCEPTUAL = auto()  # Adjust S/L based on hue perception (Itten's theory)


@dataclass
class Color:
  """Mutable color representation with RGBA float components (0.0-1.0)."""

  r: float
  g: float
  b: float
  a: float = 1.0
  hex_meta: HexMetadata = field(default_factory=HexMetadata)

  GAMMA: ClassVar[float] = 2.2
  ANSI_RESET: ClassVar[str] = '\033[0m'
  ALL_INCLUSIVE: ClassVar[tuple[bool, bool]] = (True, True)

  _RGBA_LABELS: ClassVar[dict[str, str]] = {
    'r': 'Red',
    'g': 'Green',
    'b': 'Blue',
    'a': 'Alpha',
  }

  def __setattr__(self, name: str, value: object) -> None:
    """Validate RGBA fields on every set (construction + mutation)."""
    label = self._RGBA_LABELS.get(name)
    if label is not None:
      if not isinstance(value, (int, float)):
        raise TypeError(f'{label} must be a number, got {type(value).__name__}')
      value = self._check_pct_arg(float(value), label)
    object.__setattr__(self, name, value)

  def __post_init__(self) -> None:
    """Coerce None hex_meta to default HexMetadata."""
    if self.hex_meta is None:
      object.__setattr__(self, 'hex_meta', HexMetadata())

  @classmethod
  def _check_num_range(
    cls,
    arg: SimpleNum,
    valid_range: tuple[SimpleNum, SimpleNum],
    label: str,
    inclusive: tuple[bool, bool] = (True, True),
  ) -> float:
    """Validate that arg is within valid_range.

    :param arg: Value to check
    :param valid_range: (min, max) tuple
    :param label: Label for error message
    :param inclusive: (include_min, include_max) - True means <=, False means <
    :return: The validated arg as float
    """
    lo_op: Callable = operator.ge if inclusive[0] else operator.gt
    hi_op: Callable = operator.le if inclusive[1] else operator.lt
    lo_bracket = '[' if inclusive[0] else '('
    hi_bracket = ']' if inclusive[1] else ')'
    assert lo_op(arg, valid_range[0]) and hi_op(arg, valid_range[1]), (
      f'{label} must be in {lo_bracket}{valid_range[0]}..{valid_range[1]}{hi_bracket}, got {arg}'
    )
    return float(arg)

  @classmethod
  def _check_pct_arg(cls, arg: float, label: str) -> float:
    """Validate arg is in [0.0, 1.0]."""
    return cls._check_num_range(arg, (0.0, 1.0), label)

  @classmethod
  def _check_int_arg(cls, arg: int, label: str) -> int:
    """Validate arg is in [0, 255]."""
    cls._check_num_range(arg, (0, 255), label)
    return arg

  @classmethod
  def from_hex_str(cls, hex_str: str) -> Color:
    """Parse hex color string into Color.

    :param hex_str: Hex string like "#FF5733", "0xAABBCC", "#FFF", etc.
    :return: Color instance
    """
    hex_digits, prefix = cls.parse_hex_str(hex_str)

    alpha_chars: list[str] = [c for c in hex_digits if c.isalpha()]
    is_uppercase: bool = any(c.isupper() for c in alpha_chars) if alpha_chars else False

    hex_digits = hex_digits.upper()
    length = len(hex_digits)
    is_short_form = length in (3, 4)

    if length in (3, 4):
      values = [int(c * 2, 16) for c in hex_digits]
    elif length in (6, 8):
      values = [int(hex_digits[i : i + 2], 16) for i in range(0, length, 2)]
    else:
      raise ValueError(f'Invalid hex color format: {hex_str}')

    r, g, b = values[:3]
    a = values[3] if len(values) == 4 else 255

    hex_meta = HexMetadata(prefix=prefix, short_form=is_short_form, uppercase=is_uppercase)
    return cls(r / 255.0, g / 255.0, b / 255.0, a / 255.0, hex_meta)

  @classmethod
  def parse_hex_str(cls, hex_str: str, prefix: str = '#') -> tuple[str, str]:
    """Parse hex string into digits and detected prefix.

    :param hex_str: Raw hex color string
    :param prefix: Default prefix if none detected
    :return: (hex_digits, prefix) tuple
    """
    hex_clean: str = hex_str.strip()
    if hex_clean.startswith(('0x', '0X')):
      prefix = hex_clean[:2]
      hex_digits = hex_clean[2:]
    elif hex_clean.startswith('#'):
      hex_digits = hex_clean[1:]
    else:
      hex_digits = hex_clean[0:]
    return hex_digits, prefix

  @classmethod
  def from_int_values(cls, r: int, g: int, b: int, a: int = 255) -> Color:
    """Create Color from integer RGB(A) values (0-255).

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :param a: Alpha component (0-255)
    :return: Color instance
    """
    cls._check_int_arg(r, 'Red')
    cls._check_int_arg(g, 'Green')
    cls._check_int_arg(b, 'Blue')
    cls._check_int_arg(a, 'Alpha')
    return cls(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

  def lightest(self) -> float:
    """Return the brightest RGB component value."""
    return max(self.r, self.g, self.b)

  def darkest(self) -> float:
    """Return the darkest RGB component value."""
    return min(self.r, self.g, self.b)

  def grayscale_lightness(self) -> float:
    """Calculate luminosity using average of lightest and darkest component."""
    return (self.lightest() + self.darkest()) / 2

  def grayscale_luminosity(self) -> float:
    """Calculate luminosity using weighted RGB (standard luminosity coefficients)."""
    return 0.21 * self.r + 0.72 * self.g + 0.07 * self.b

  def grayscale_mean(self) -> float:
    """Calculate grayscale using arithmetic mean of RGB components."""
    return (self.r + self.g + self.b) / 3

  def as_grayscale(self, algorithm: GrayscaleAlgorithm) -> Color:
    """Convert to grayscale using specified algorithm.

    :param algorithm: The grayscale algorithm to use
    :return: New grayscale Color
    """
    gray: float
    if algorithm == GrayscaleAlgorithm.LIGHTNESS:
      gray = self.grayscale_lightness()
    elif algorithm == GrayscaleAlgorithm.AVERAGE:
      gray = self.grayscale_mean()
    else:  # Defaults to LUMINOSITY
      gray = self.grayscale_luminosity()
    return Color(gray, gray, gray, self.a, self.hex_meta)

  def _srgb_to_linear(self, value: float) -> float:
    """Convert sRGB component to linear space."""
    return value**self.GAMMA

  def _linear_to_srgb(self, value: float) -> float:
    """Convert linear component back to sRGB."""
    return value ** (1.0 / self.GAMMA)

  def mix(self, other: Color | list[Color], weight: float | list[float] = 0.5) -> Color:
    """Mix this color with other color(s) using gamma-correct blending.

    :param other: Color or list of Colors to mix with
    :param weight: Total weight for other colors, or list of weights per color.
                   If single weight with multiple colors, weight is divided equally.
                   If list of weights, they must sum to <= 0.95 (leaving 5% for self).
    :return: New blended Color
    """
    # Normalize other to list
    others = other if isinstance(other, list) else [other]
    assert len(others) > 0, 'Must provide at least one color to mix'

    # Normalize weights to list
    weights: list[float]
    if isinstance(weight, list):
      weights = weight
      assert len(weights) == len(others), (
        f'Weight list length ({len(weights)}) must match color list length ({len(others)})'
      )
      total_weight = sum(weights)
      assert total_weight <= 0.95, (
        f'Sum of weights must be <= 0.95 to leave room for self, got {total_weight}'
      )
    else:
      # Single weight: divide equally among all others
      self._check_num_range(weight, (0.01, 0.99), 'weight')
      per_color_weight = weight / len(others)
      weights = [per_color_weight] * len(others)

    # Validate individual weights
    for i, w in enumerate(weights):
      self._check_num_range(w, (0.0, 1.0), f'weight[{i}]')

    total_other_weight = sum(weights)
    w1 = 1.0 - total_other_weight

    # Start with self's contribution in linear space
    r_linear = self._srgb_to_linear(self.r) * w1
    g_linear = self._srgb_to_linear(self.g) * w1
    b_linear = self._srgb_to_linear(self.b) * w1
    a_linear = self.a * w1

    # Add each other color's contribution
    for c, w in zip(others, weights, strict=True):
      r_linear += self._srgb_to_linear(c.r) * w
      g_linear += self._srgb_to_linear(c.g) * w
      b_linear += self._srgb_to_linear(c.b) * w
      a_linear += c.a * w

    # Convert back to sRGB
    return Color(
      self._linear_to_srgb(r_linear),
      self._linear_to_srgb(g_linear),
      self._linear_to_srgb(b_linear),
      a_linear,
      self.hex_meta,
    )

  def _can_use_short_form(self, value: int) -> bool:
    """Check if an int value (0-255) can be represented as short form."""
    high = value >> 4
    low = value & 0x0F
    return high == low

  def to_int_tuple(self) -> tuple[int, int, int, int]:
    """Return RGBA as integer tuple (0-255 each)."""
    return (
      round(self.r * 255),
      round(self.g * 255),
      round(self.b * 255),
      round(self.a * 255),
    )

  def to_hex_str(
    self,
    prefix: str | None = None,
    short_form: bool | None = None,
    uppercase: bool | None = None,
  ) -> str:
    """Convert to hex string.

    :param prefix: Override prefix ("#" or "0x"). None uses original.
    :param short_form: Override short form preference. None uses original.
    :param uppercase: Override case. None uses original.
    :return: Hex string representation
    """
    meta = self.hex_meta
    use_prefix = prefix if prefix is not None else meta.prefix
    prefer_short = short_form if short_form is not None else meta.short_form
    use_upper = uppercase if uppercase is not None else meta.uppercase

    r_int, g_int, b_int, a_int = self.to_int_tuple()
    has_alpha = a_int < 255

    # Determine if we can use short form
    use_short = (
      prefer_short
      and self._can_use_short_form(r_int)
      and self._can_use_short_form(g_int)
      and self._can_use_short_form(b_int)
      and (not has_alpha or self._can_use_short_form(a_int))
    )

    hex_str: str
    if use_short:
      r_s, g_s, b_s = r_int >> 4, g_int >> 4, b_int >> 4
      rgb_str = f'{use_prefix}{r_s:X}{g_s:X}{b_s:X}'
      hex_str = f'{rgb_str}{a_int >> 4:X}' if has_alpha else rgb_str
    else:
      rgb_str = f'{use_prefix}{r_int:02X}{g_int:02X}{b_int:02X}'
      hex_str = f'{rgb_str}{a_int:02X}' if has_alpha else rgb_str

    # Apply case: for # prefix, lowercase all; for 0x, keep prefix, lowercase hex digits
    if not use_upper:
      if use_prefix == '#':
        hex_str = hex_str.lower()
      else:
        hex_str = use_prefix + hex_str[len(use_prefix) :].lower()
    return hex_str

  def to_ansi_bg(self) -> str:
    """Return ANSI escape code for background color (24-bit true color)."""
    r, g, b, _ = self.to_int_tuple()
    return f'\033[48;2;{r};{g};{b}m'

  def to_ansi_fg(self) -> str:
    """Return ANSI escape code for foreground color (24-bit true color)."""
    r, g, b, _ = self.to_int_tuple()
    return f'\033[38;2;{r};{g};{b}m'

  def contrast_color(self) -> Color:
    """Return black or white Color for text contrast based on luminosity."""
    return (
      Color.from_int_values(0, 0, 0)
      if self.grayscale_luminosity() >= 0.5
      else Color.from_int_values(255, 255, 255)
    )

  def to_hsl(self) -> tuple[float, float, float]:
    """Convert RGB to HSL.

    :return: (hue 0-360, saturation 0-1, lightness 0-1)
    """
    r, g, b = self.r, self.g, self.b
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c

    # Lightness
    lt = (max_c + min_c) / 2

    # Saturation
    s = 0.0
    if delta != 0 and lt != 0 and lt != 1:
      s = delta / (1 - abs(2 * lt - 1))

    # Hue
    h = 0.0
    if delta != 0:
      if max_c == r:
        h = 60 * (((g - b) / delta) % 6)
      elif max_c == g:
        h = 60 * (((b - r) / delta) + 2)
      else:  # max_c == b
        h = 60 * (((r - g) / delta) + 4)

    return (h, s, lt)

  @classmethod
  def from_hsl(
    cls,
    h: float,
    s: float,
    lt: float,
    a: float = 1.0,
    hex_meta: HexMetadata | None = None,
  ) -> Color:
    """Create Color from HSL values.

    :param h: Hue (0-360, wraps automatically)
    :param s: Saturation (0.0-1.0)
    :param lt: Lightness (0.0-1.0)
    :param a: Alpha (0.0-1.0)
    :param hex_meta: Preserved hex metadata
    :return: Color instance
    """
    # Normalize hue to 0-360
    h = h % 360
    if h < 0:
      h += 360

    # Clamp s and lt
    s = max(0.0, min(1.0, s))
    lt = max(0.0, min(1.0, lt))

    c = (1 - abs(2 * lt - 1)) * s  # Chroma
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = lt - c / 2

    r1, g1, b1 = 0.0, 0.0, 0.0
    if 0 <= h < 60:
      r1, g1, b1 = c, x, 0
    elif 60 <= h < 120:
      r1, g1, b1 = x, c, 0
    elif 120 <= h < 180:
      r1, g1, b1 = 0, c, x
    elif 180 <= h < 240:
      r1, g1, b1 = 0, x, c
    elif 240 <= h < 300:
      r1, g1, b1 = x, 0, c
    else:  # 300 <= h < 360
      r1, g1, b1 = c, 0, x

    # Clamp to [0, 1] to prevent floating-point precision artifacts
    return cls(
      max(0.0, min(1.0, r1 + m)),
      max(0.0, min(1.0, g1 + m)),
      max(0.0, min(1.0, b1 + m)),
      a,
      hex_meta or HexMetadata(),
    )

  def darkening_headroom(self) -> float:
    """Return how much lightness is available for darkening (0.0-1.0)."""
    _, _, lt = self.to_hsl()
    return lt

  def darken(self, amount: float) -> Color:
    """Create darker Color by reducing HSL lightness.

    :param amount: Darkening factor (0.0=no change, 1.0=black)
    :return: New darker Color
    """
    clamped = max(0.0, min(1.0, amount))
    h, s, lt = self.to_hsl()
    new_lt = lt * (1.0 - clamped)
    return Color.from_hsl(h, s, new_lt, self.a, self.hex_meta)

  def rotate_hue(self, degrees: float) -> Color:
    """Create new Color with hue rotated by specified degrees.

    Preserves saturation, lightness, alpha, and hex metadata.

    :param degrees: Degrees to rotate (can be negative, wraps at 360)
    :return: New Color with rotated hue
    """
    h, s, lt = self.to_hsl()
    return Color.from_hsl(h + degrees, s, lt, self.a, self.hex_meta)

  # Itten's contrast of extension - relative perceived brightness by hue
  # Yellow (60) perceived brightest, violet (270) darkest
  # Values normalized: yellow=1.0 (brightest), violet=0.44 (darkest)
  ITTEN_HUE_WEIGHTS: ClassVar[dict[int, float]] = {
    0: 0.67,  # Red
    30: 0.78,  # Orange
    60: 1.0,  # Yellow (brightest)
    90: 0.89,  # Yellow-Green
    120: 0.78,  # Green
    150: 0.67,  # Blue-Green
    180: 0.56,  # Cyan
    210: 0.50,  # Blue
    240: 0.44,  # Violet (darkest)
    270: 0.44,  # Purple
    300: 0.56,  # Magenta
    330: 0.61,  # Red-Magenta
  }

  def _perceptual_adjust(self, target_hue: float) -> tuple[float, float]:
    """Adjust saturation/lightness for perceptual balance based on target hue."""
    _, s, lt = self.to_hsl()
    target_hue = target_hue % 360

    # Find nearest hue weights and interpolate
    hue_keys = sorted(self.ITTEN_HUE_WEIGHTS.keys())
    lower_hue = max([h for h in hue_keys if h <= target_hue], default=330)
    upper_hue = min([h for h in hue_keys if h >= target_hue], default=0)

    # Handle wraparound
    if upper_hue < lower_hue:
      upper_hue = hue_keys[0]
      lower_hue = hue_keys[-1]

    lower_weight = self.ITTEN_HUE_WEIGHTS.get(lower_hue, 0.67)
    upper_weight = self.ITTEN_HUE_WEIGHTS.get(upper_hue, 0.67)

    # Interpolate weight
    weight_range = (upper_hue - lower_hue) % 360 if upper_hue != lower_hue else 1
    position = (target_hue - lower_hue) % 360
    t = position / weight_range if weight_range > 0 else 0
    target_weight = lower_weight + (upper_weight - lower_weight) * t

    # Adjust lightness - bring toward middle based on weight difference
    # Brighter hues (weight > 0.7) get darkened slightly
    # Darker hues (weight < 0.7) get lightened slightly
    reference_weight = 0.67  # Red as reference
    weight_diff = target_weight - reference_weight
    lt_adjust = -weight_diff * 0.15  # Scale adjustment

    adjusted_lt = max(0.1, min(0.9, lt + lt_adjust))
    adjusted_s = s  # Keep saturation unchanged for now

    return (adjusted_s, adjusted_lt)

  def harmony(
    self,
    harmony_type: HarmonyType,
    method: HarmonyMethod = HarmonyMethod.STANDARD,
  ) -> list[Color]:
    """Generate a color harmony palette based on this color.

    :param harmony_type: The type of harmony to generate
    :param method: Calculation method (standard or perceptual)
    :return: List of Colors including self as first element
    """
    # Define rotation angles for each harmony type
    rotations: dict[HarmonyType, list[float]] = {
      HarmonyType.COMPLEMENTARY: [0, 180],
      HarmonyType.SPLIT_COMPLEMENTARY: [0, 150, 210],
      HarmonyType.ANALOGOUS: [-30, 0, 30],
      HarmonyType.TRIADIC: [0, 120, 240],
      HarmonyType.TETRADIC_SQUARE: [0, 90, 180, 270],
      HarmonyType.TETRADIC_RECTANGULAR: [0, 60, 180, 240],
    }

    angles = rotations[harmony_type]
    h, s, lt = self.to_hsl()

    # Handle edge cases: grayscale (s=0) or pure black/white
    if s < 0.01 or lt < 0.01 or lt > 0.99:
      # Return self for all positions - no meaningful hue rotation
      return [Color(self.r, self.g, self.b, self.a, self.hex_meta) for _ in angles]

    colors: list[Color] = []
    for angle in angles:
      target_hue = h + angle
      if method == HarmonyMethod.PERCEPTUAL:
        adj_s, adj_lt = self._perceptual_adjust(target_hue)
        colors.append(Color.from_hsl(target_hue, adj_s, adj_lt, self.a, self.hex_meta))
      else:
        colors.append(Color.from_hsl(target_hue, s, lt, self.a, self.hex_meta))

    return colors
