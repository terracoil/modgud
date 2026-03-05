"""Tests for Color class and related enums."""

import pytest
from modgud.util.geo import (
  Color,
  GrayscaleAlgorithm,
  HarmonyMethod,
  HarmonyType,
  HexMetadata,
)


class TestColorConstruction:
  """Test Color construction from various inputs."""

  def test_float_components(self) -> None:
    """Test basic float construction."""
    c = Color(0.5, 0.3, 0.8)
    assert c.r == pytest.approx(0.5)
    assert c.g == pytest.approx(0.3)
    assert c.b == pytest.approx(0.8)
    assert c.a == pytest.approx(1.0)

  def test_float_with_alpha(self) -> None:
    """Test float construction with explicit alpha."""
    c = Color(0.1, 0.2, 0.3, 0.5)
    assert c.a == pytest.approx(0.5)

  def test_from_int_values(self) -> None:
    """Test construction from 0-255 integer values."""
    c = Color.from_int_values(255, 128, 0)
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(128 / 255.0)
    assert c.b == pytest.approx(0.0)
    assert c.a == pytest.approx(1.0)

  def test_from_int_values_with_alpha(self) -> None:
    """Test construction from 0-255 integer values with alpha."""
    c = Color.from_int_values(100, 150, 200, 128)
    assert c.a == pytest.approx(128 / 255.0)

  def test_validation_out_of_range(self) -> None:
    """Test that out-of-range float values raise errors."""
    with pytest.raises(AssertionError, match='Red'):
      Color(1.5, 0.0, 0.0)
    with pytest.raises(AssertionError, match='Green'):
      Color(0.0, -0.1, 0.0)
    with pytest.raises(AssertionError, match='Blue'):
      Color(0.0, 0.0, 2.0)


class TestHexParsing:
  """Test Color.from_hex_str parsing."""

  def test_six_digit_hash(self) -> None:
    """Test standard 6-digit hex with # prefix."""
    c = Color.from_hex_str('#FF5733')
    assert c.r == pytest.approx(255 / 255.0)
    assert c.g == pytest.approx(87 / 255.0)
    assert c.b == pytest.approx(51 / 255.0)

  def test_short_form(self) -> None:
    """Test 3-digit short form hex."""
    c = Color.from_hex_str('#FFF')
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(1.0)
    assert c.b == pytest.approx(1.0)

  def test_short_form_alpha(self) -> None:
    """Test 4-digit short form hex with alpha."""
    c = Color.from_hex_str('#FF08')
    assert c.r == pytest.approx(1.0)
    assert c.g == pytest.approx(1.0)
    assert c.b == pytest.approx(0.0)
    # alpha = 0x88 / 255
    assert c.a == pytest.approx(0x88 / 255.0)

  def test_eight_digit_alpha(self) -> None:
    """Test 8-digit hex with alpha channel."""
    c = Color.from_hex_str('#FF573380')
    assert c.a == pytest.approx(0x80 / 255.0)

  def test_0x_prefix(self) -> None:
    """Test 0x prefix parsing."""
    c = Color.from_hex_str('0xAABBCC')
    assert c.r == pytest.approx(0xAA / 255.0)
    assert c.g == pytest.approx(0xBB / 255.0)
    assert c.b == pytest.approx(0xCC / 255.0)

  def test_case_insensitive(self) -> None:
    """Test that parsing is case-insensitive."""
    c1 = Color.from_hex_str('#ff5733')
    c2 = Color.from_hex_str('#FF5733')
    assert c1.r == pytest.approx(c2.r)
    assert c1.g == pytest.approx(c2.g)
    assert c1.b == pytest.approx(c2.b)

  def test_invalid_length(self) -> None:
    """Test that invalid hex lengths raise errors."""
    with pytest.raises(ValueError, match='Invalid hex color format'):
      Color.from_hex_str('#12345')

  def test_no_prefix(self) -> None:
    """Test parsing without any prefix."""
    c = Color.from_hex_str('AABBCC')
    assert c.r == pytest.approx(0xAA / 255.0)


class TestHexRoundtrip:
  """Test to_hex_str preserves metadata."""

  def test_roundtrip_long_form_uppercase(self) -> None:
    """Test hex roundtrip preserves uppercase when input was uppercase."""
    c = Color.from_hex_str('#FF5733')
    assert c.to_hex_str() == '#FF5733'

  def test_roundtrip_long_form_lowercase(self) -> None:
    """Test hex roundtrip preserves lowercase when input was lowercase."""
    c = Color.from_hex_str('#ff5733')
    assert c.to_hex_str() == '#ff5733'

  def test_roundtrip_short_form(self) -> None:
    """Test hex roundtrip for short form."""
    c = Color.from_hex_str('#fff')
    hex_out = c.to_hex_str()
    assert hex_out == '#fff'

  def test_uppercase_preservation(self) -> None:
    """Test uppercase preference is preserved."""
    c = Color.from_hex_str('#FF5733')
    assert c.to_hex_str(uppercase=True) == '#FF5733'

  def test_prefix_override(self) -> None:
    """Test prefix override in output."""
    c = Color.from_hex_str('#AABBCC')
    assert c.to_hex_str(prefix='0x', uppercase=True).startswith('0x')

  def test_alpha_roundtrip(self) -> None:
    """Test 8-digit hex roundtrip with alpha."""
    c = Color.from_hex_str('#FF573380')
    hex_str = c.to_hex_str(uppercase=True)
    assert hex_str == '#FF573380'


class TestLuminosity:
  """Test luminosity calculation."""

  def test_black_luminosity(self) -> None:
    """Test black has zero luminosity."""
    assert Color(0, 0, 0).grayscale_luminosity() == pytest.approx(0.0)

  def test_white_luminosity(self) -> None:
    """Test white has full luminosity."""
    assert Color(1, 1, 1).grayscale_luminosity() == pytest.approx(1.0)

  def test_green_dominant(self) -> None:
    """Test green contributes most to luminosity (0.72 weight)."""
    pure_green = Color(0, 1, 0).grayscale_luminosity()
    pure_red = Color(1, 0, 0).grayscale_luminosity()
    pure_blue = Color(0, 0, 1).grayscale_luminosity()
    assert pure_green > pure_red > pure_blue


class TestGrayscale:
  """Test grayscale conversion algorithms."""

  def test_lightness_algorithm(self) -> None:
    """Test lightness algorithm: (max + min) / 2."""
    c = Color(0.8, 0.2, 0.5)
    gray = c.as_grayscale(GrayscaleAlgorithm.LIGHTNESS)
    expected = (0.8 + 0.2) / 2
    assert gray.r == pytest.approx(expected)
    assert gray.g == pytest.approx(expected)
    assert gray.b == pytest.approx(expected)

  def test_average_algorithm(self) -> None:
    """Test grayscale_mean algorithm: (r + g + b) / 3."""
    c = Color(0.6, 0.3, 0.9)
    gray = c.as_grayscale(GrayscaleAlgorithm.AVERAGE)
    expected = (0.6 + 0.3 + 0.9) / 3
    assert gray.r == pytest.approx(expected)

  def test_luminosity_algorithm(self) -> None:
    """Test luminosity algorithm matches direct luminosity call."""
    c = Color(0.5, 0.7, 0.3)
    gray = c.as_grayscale(GrayscaleAlgorithm.LUMINOSITY)
    assert gray.r == pytest.approx(c.grayscale_luminosity())

  def test_alpha_preserved(self) -> None:
    """Test alpha is preserved through grayscale conversion."""
    c = Color(0.5, 0.5, 0.5, 0.7)
    gray = c.as_grayscale(GrayscaleAlgorithm.AVERAGE)
    assert gray.a == pytest.approx(0.7)


class TestMix:
  """Test color mixing with gamma-correct blending."""

  def test_mix_two_colors(self) -> None:
    """Test basic mixing of two colors."""
    c1 = Color(1.0, 0.0, 0.0)
    c2 = Color(0.0, 0.0, 1.0)
    mixed = c1.mix(c2, 0.5)
    # Both contribute equally; result should have r and b components
    assert mixed.r > 0
    assert mixed.b > 0

  def test_mix_low_weight(self) -> None:
    """Test mixing with very low weight preserves most of self."""
    c1 = Color(1.0, 0.0, 0.0)
    c2 = Color(0.0, 1.0, 0.0)
    mixed = c1.mix(c2, 0.01)
    assert mixed.r > 0.9

  def test_mix_multiple_colors(self) -> None:
    """Test mixing with a list of colors."""
    base = Color(1.0, 0.0, 0.0)
    others = [Color(0.0, 1.0, 0.0), Color(0.0, 0.0, 1.0)]
    mixed = base.mix(others, 0.6)
    # All channels should have some value
    assert mixed.r > 0
    assert mixed.g > 0
    assert mixed.b > 0

  def test_mix_with_weight_list(self) -> None:
    """Test mixing with explicit per-color weights."""
    base = Color(1.0, 0.0, 0.0)
    others = [Color(0.0, 1.0, 0.0), Color(0.0, 0.0, 1.0)]
    mixed = base.mix(others, [0.3, 0.2])
    assert mixed.r > 0
    assert mixed.g > 0
    assert mixed.b > 0


class TestHSL:
  """Test HSL conversion roundtrip."""

  def test_red_hsl(self) -> None:
    """Test pure red converts to H=0."""
    h, s, lt = Color(1.0, 0.0, 0.0).to_hsl()
    assert h == pytest.approx(0.0, abs=1.0)
    assert s == pytest.approx(1.0, abs=0.01)
    assert lt == pytest.approx(0.5, abs=0.01)

  def test_roundtrip(self) -> None:
    """Test HSL roundtrip preserves color."""
    original = Color(0.8, 0.3, 0.5)
    h, s, lt = original.to_hsl()
    recovered = Color.from_hsl(h, s, lt)
    assert recovered.r == pytest.approx(original.r, abs=0.01)
    assert recovered.g == pytest.approx(original.g, abs=0.01)
    assert recovered.b == pytest.approx(original.b, abs=0.01)

  def test_grayscale_zero_saturation(self) -> None:
    """Test grayscale has zero saturation."""
    _, s, _ = Color(0.5, 0.5, 0.5).to_hsl()
    assert s == pytest.approx(0.0, abs=0.01)


class TestHueRotation:
  """Test hue rotation."""

  def test_complementary_rotation(self) -> None:
    """Test 180-degree rotation gives complementary color."""
    original = Color(1.0, 0.0, 0.0)
    rotated = original.rotate_hue(180)
    # Complementary of red should be cyan-ish
    assert rotated.r < 0.5
    assert rotated.g > 0.5 or rotated.b > 0.5

  def test_full_rotation_identity(self) -> None:
    """Test 360-degree rotation returns same color."""
    original = Color(0.6, 0.3, 0.8)
    rotated = original.rotate_hue(360)
    assert rotated.r == pytest.approx(original.r, abs=0.01)
    assert rotated.g == pytest.approx(original.g, abs=0.01)
    assert rotated.b == pytest.approx(original.b, abs=0.01)


class TestHarmony:
  """Test color harmony generation."""

  @pytest.mark.parametrize('harmony_type', list(HarmonyType))
  def test_all_harmony_types_produce_colors(self, harmony_type: HarmonyType) -> None:
    """Test every harmony type produces non-empty color list."""
    c = Color(0.8, 0.3, 0.2)
    colors = c.harmony(harmony_type)
    assert len(colors) >= 2

  def test_complementary_returns_two(self) -> None:
    """Test complementary returns exactly 2 colors."""
    c = Color(0.8, 0.3, 0.2)
    colors = c.harmony(HarmonyType.COMPLEMENTARY)
    assert len(colors) == 2

  def test_triadic_returns_three(self) -> None:
    """Test triadic returns exactly 3 colors."""
    c = Color(0.8, 0.3, 0.2)
    colors = c.harmony(HarmonyType.TRIADIC)
    assert len(colors) == 3

  def test_tetradic_returns_four(self) -> None:
    """Test tetradic returns exactly 4 colors."""
    c = Color(0.8, 0.3, 0.2)
    colors = c.harmony(HarmonyType.TETRADIC_SQUARE)
    assert len(colors) == 4

  def test_perceptual_method(self) -> None:
    """Test perceptual method produces valid colors."""
    c = Color(0.8, 0.3, 0.2)
    colors = c.harmony(HarmonyType.TRIADIC, HarmonyMethod.PERCEPTUAL)
    assert len(colors) == 3
    for color in colors:
      assert 0 <= color.r <= 1
      assert 0 <= color.g <= 1
      assert 0 <= color.b <= 1

  def test_grayscale_harmony(self) -> None:
    """Test harmony on grayscale input returns self-like colors."""
    c = Color(0.5, 0.5, 0.5)
    colors = c.harmony(HarmonyType.COMPLEMENTARY)
    # All should be similar since there's no hue to rotate
    assert len(colors) == 2


class TestContrastColor:
  """Test contrast color calculation."""

  def test_light_color_returns_black(self) -> None:
    """Test light color returns black for contrast."""
    c = Color(1.0, 1.0, 1.0)
    contrast = c.contrast_color()
    assert contrast.r == pytest.approx(0.0)
    assert contrast.g == pytest.approx(0.0)
    assert contrast.b == pytest.approx(0.0)

  def test_dark_color_returns_white(self) -> None:
    """Test dark color returns white for contrast."""
    c = Color(0.0, 0.0, 0.0)
    contrast = c.contrast_color()
    assert contrast.r == pytest.approx(1.0)
    assert contrast.g == pytest.approx(1.0)
    assert contrast.b == pytest.approx(1.0)


class TestAnsiOutput:
  """Test ANSI escape code generation."""

  def test_ansi_bg(self) -> None:
    """Test ANSI background escape code format."""
    c = Color.from_int_values(255, 128, 0)
    bg = c.to_ansi_bg()
    assert bg.startswith('\033[48;2;')
    assert '255' in bg
    assert '128' in bg

  def test_ansi_fg(self) -> None:
    """Test ANSI foreground escape code format."""
    c = Color.from_int_values(100, 200, 50)
    fg = c.to_ansi_fg()
    assert fg.startswith('\033[38;2;')


class TestToIntTuple:
  """Test integer tuple conversion."""

  def test_full_values(self) -> None:
    """Test conversion to 0-255 int tuple."""
    c = Color(1.0, 0.5, 0.0, 0.5)
    r, g, b, a = c.to_int_tuple()
    assert r == 255
    assert g == 128
    assert b == 0
    assert a == 128

  def test_black(self) -> None:
    """Test black converts to all zeros."""
    r, g, b, a = Color(0, 0, 0).to_int_tuple()
    assert r == 0
    assert g == 0
    assert b == 0
    assert a == 255


class TestDarken:
  """Test Color.darken() and darkening_headroom() methods."""

  def test_darken_zero_no_change(self) -> None:
    """Test amount=0.0 returns same color."""
    c = Color(0.8, 0.3, 0.5)
    darkened = c.darken(0.0)
    assert darkened.r == pytest.approx(c.r, abs=0.01)
    assert darkened.g == pytest.approx(c.g, abs=0.01)
    assert darkened.b == pytest.approx(c.b, abs=0.01)

  def test_darken_full_returns_black(self) -> None:
    """Test amount=1.0 returns black."""
    c = Color(0.8, 0.3, 0.5)
    darkened = c.darken(1.0)
    assert darkened.r == pytest.approx(0.0, abs=0.01)
    assert darkened.g == pytest.approx(0.0, abs=0.01)
    assert darkened.b == pytest.approx(0.0, abs=0.01)

  def test_darken_half(self) -> None:
    """Test amount=0.5 halves lightness."""
    c = Color(0.8, 0.3, 0.5)
    _, _, orig_lt = c.to_hsl()
    darkened = c.darken(0.5)
    _, _, new_lt = darkened.to_hsl()
    assert new_lt == pytest.approx(orig_lt * 0.5, abs=0.01)

  def test_darken_preserves_hue(self) -> None:
    """Test hue unchanged after darkening."""
    c = Color(0.8, 0.2, 0.3)
    orig_h, _, _ = c.to_hsl()
    darkened = c.darken(0.3)
    new_h, _, _ = darkened.to_hsl()
    assert new_h == pytest.approx(orig_h, abs=1.0)

  def test_darkening_headroom_black(self) -> None:
    """Test black has 0 headroom."""
    c = Color(0.0, 0.0, 0.0)
    assert c.darkening_headroom() == pytest.approx(0.0, abs=0.01)

  def test_darkening_headroom_white(self) -> None:
    """Test white has lightness=1.0 headroom."""
    c = Color(1.0, 1.0, 1.0)
    assert c.darkening_headroom() == pytest.approx(1.0, abs=0.01)

  def test_darken_preserves_alpha(self) -> None:
    """Test alpha unchanged after darkening."""
    c = Color(0.8, 0.3, 0.5, 0.7)
    darkened = c.darken(0.5)
    assert darkened.a == pytest.approx(0.7, abs=0.01)

  def test_darken_already_dark_color(self) -> None:
    """Test near-black returns near-black."""
    c = Color(0.02, 0.01, 0.01)
    darkened = c.darken(0.5)
    assert darkened.r < 0.02
    assert darkened.g < 0.01
    assert darkened.b < 0.01


class TestMutability:
  """Test mutable Color field assignment and validation."""

  def test_set_r_valid(self) -> None:
    """Test setting r to a valid value."""
    c = Color(0.5, 0.3, 0.8)
    c.r = 0.8
    assert c.r == pytest.approx(0.8)

  def test_set_r_out_of_range(self) -> None:
    """Test setting r out of range raises AssertionError."""
    c = Color(0.5, 0.3, 0.8)
    with pytest.raises(AssertionError, match='Red'):
      c.r = 1.5

  def test_set_negative_b(self) -> None:
    """Test setting b to negative raises AssertionError."""
    c = Color(0.5, 0.3, 0.8)
    with pytest.raises(AssertionError, match='Blue'):
      c.b = -0.1

  def test_set_non_numeric_raises_type_error(self) -> None:
    """Test setting r to a non-numeric value raises TypeError."""
    c = Color(0.5, 0.3, 0.8)
    with pytest.raises(TypeError, match='Red must be a number'):
      c.r = 'not_a_number'  # type: ignore[assignment]

  def test_hex_meta_none_coercion(self) -> None:
    """Test that hex_meta=None is coerced to default HexMetadata."""
    c = Color(0.5, 0.3, 0.8, hex_meta=None)  # type: ignore[arg-type]
    assert c.hex_meta == HexMetadata()

  def test_set_hex_meta(self) -> None:
    """Test direct hex_meta assignment works."""
    c = Color(0.5, 0.3, 0.8)
    custom_meta = HexMetadata(prefix='0x', short_form=True, uppercase=True)
    c.hex_meta = custom_meta
    assert c.hex_meta == custom_meta
