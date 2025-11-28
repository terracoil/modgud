"""Tests for LookupEnum mixin functionality."""

from __future__ import annotations

from enum import IntEnum, StrEnum, auto

import pytest
from modgud.domain.enums import OrdinalEnum
from modgud.domain.enums.lookup_enum import LookupEnum


# Test enums that inherit from LookupEnum
class SampleStringEnum(LookupEnum, StrEnum):
  """Test enum using StrEnum as base."""

  NONE = auto()
  FIRST = auto()
  SECOND = auto()
  THIRD = auto()

  # Aliases
  ONE = FIRST
  TWO = SECOND
  THREE = THIRD

  @classmethod
  def _get_default_value(cls) -> SampleStringEnum:
    """Return NONE as default."""
    return cls.NONE


class SampleIntEnum(LookupEnum, IntEnum):
  """Test enum using IntEnum as base."""

  ZERO = 0
  LOW = 1
  MEDIUM = 2
  HIGH = 3

  # Aliases
  L = LOW
  M = MEDIUM
  H = HIGH

  @classmethod
  def _get_default_value(cls) -> SampleIntEnum:
    """Return ZERO as default."""
    return cls.ZERO


class TestLookupEnum:
  """Test suite for LookupEnum functionality."""

  def test_from_string_exact_match(self):
    """Test from_string with exact uppercase matches."""
    assert SampleStringEnum.from_string('FIRST') == SampleStringEnum.FIRST
    assert SampleStringEnum.from_string('SECOND') == SampleStringEnum.SECOND
    assert SampleIntEnum.from_string('LOW') == SampleIntEnum.LOW
    assert SampleIntEnum.from_string('HIGH') == SampleIntEnum.HIGH

  def test_from_string_case_insensitive(self):
    """Test from_string with various case inputs."""
    assert SampleStringEnum.from_string('first') == SampleStringEnum.FIRST
    assert SampleStringEnum.from_string('First') == SampleStringEnum.FIRST
    assert SampleStringEnum.from_string('FIRST') == SampleStringEnum.FIRST
    assert SampleIntEnum.from_string('low') == SampleIntEnum.LOW
    assert SampleIntEnum.from_string('Low') == SampleIntEnum.LOW
    assert SampleIntEnum.from_string('LOW') == SampleIntEnum.LOW

  def test_from_string_aliases(self):
    """Test from_string with enum aliases."""
    assert SampleStringEnum.from_string('ONE') == SampleStringEnum.FIRST
    assert SampleStringEnum.from_string('two') == SampleStringEnum.SECOND
    assert SampleStringEnum.from_string('Three') == SampleStringEnum.THIRD
    assert SampleIntEnum.from_string('L') == SampleIntEnum.LOW
    assert SampleIntEnum.from_string('m') == SampleIntEnum.MEDIUM
    assert SampleIntEnum.from_string('H') == SampleIntEnum.HIGH

  def test_from_string_empty_none(self):
    """Test from_string with empty string and None returns default."""
    assert SampleStringEnum.from_string('') == SampleStringEnum.NONE
    assert SampleStringEnum.from_string(None) == SampleStringEnum.NONE
    assert SampleIntEnum.from_string('') == SampleIntEnum.ZERO
    assert SampleIntEnum.from_string(None) == SampleIntEnum.ZERO

  def test_from_string_invalid(self):
    """Test from_string with invalid values raises ValueError."""
    with pytest.raises(ValueError, match='is not a valid key for SampleStringEnum'):
      SampleStringEnum.from_string('INVALID')

    with pytest.raises(ValueError, match='is not a valid key for SampleIntEnum'):
      SampleIntEnum.from_string('INVALID')

    # Test that error message includes class name and key info
    with pytest.raises(ValueError, match='is not a valid key for SampleStringEnum'):
      SampleStringEnum.from_string('WRONG')

  def test_from_list(self):
    """Test from_list converts multiple values."""
    result = SampleStringEnum.from_list(['FIRST', 'second', 'THREE'])
    assert result == [SampleStringEnum.FIRST, SampleStringEnum.SECOND, SampleStringEnum.THIRD]

    result = SampleIntEnum.from_list(['LOW', 'M', 'high'])
    assert result == [SampleIntEnum.LOW, SampleIntEnum.MEDIUM, SampleIntEnum.HIGH]

  def test_from_list_empty(self):
    """Test from_list with empty list."""
    result = SampleStringEnum.from_list([])
    assert result == []

  def test_from_list_with_invalid(self):
    """Test from_list raises on any invalid name."""
    with pytest.raises(ValueError, match='is not a valid key for SampleStringEnum'):
      SampleStringEnum.from_list(['FIRST', 'INVALID', 'THIRD'])

  def test_parse_sides_string_comma_separated(self):
    """Test parse_sides_string with comma-separated values."""
    result = SampleStringEnum.parse_sides_string('FIRST,SECOND,THIRD')
    assert result == [SampleStringEnum.FIRST, SampleStringEnum.SECOND, SampleStringEnum.THIRD]

    result = SampleIntEnum.parse_sides_string('LOW,MEDIUM,HIGH')
    assert result == [SampleIntEnum.LOW, SampleIntEnum.MEDIUM, SampleIntEnum.HIGH]

  def test_parse_sides_string_space_separated(self):
    """Test parse_sides_string with space-separated values."""
    result = SampleStringEnum.parse_sides_string('FIRST SECOND THIRD')
    assert result == [SampleStringEnum.FIRST, SampleStringEnum.SECOND, SampleStringEnum.THIRD]

    result = SampleIntEnum.parse_sides_string('L M H')
    assert result == [SampleIntEnum.LOW, SampleIntEnum.MEDIUM, SampleIntEnum.HIGH]

  def test_parse_sides_string_mixed_separators(self):
    """Test parse_sides_string with mixed comma and space separators."""
    result = SampleStringEnum.parse_sides_string('FIRST, SECOND THIRD,ONE')
    assert result == [
      SampleStringEnum.FIRST,
      SampleStringEnum.SECOND,
      SampleStringEnum.THIRD,
      SampleStringEnum.FIRST,
    ]

  def test_parse_sides_string_case_insensitive(self):
    """Test parse_sides_string is case-insensitive."""
    result = SampleStringEnum.parse_sides_string('first,Second,THIRD')
    assert result == [SampleStringEnum.FIRST, SampleStringEnum.SECOND, SampleStringEnum.THIRD]

  def test_parse_sides_string_empty(self):
    """Test parse_sides_string with empty string."""
    result = SampleStringEnum.parse_sides_string('')
    assert result == []

  def test_parse_sides_string_whitespace_only(self):
    """Test parse_sides_string with whitespace only."""
    result = SampleStringEnum.parse_sides_string('   ')
    assert result == []


class TestPlacementEnumIntegration:
  """Test OrdinalEnum still works correctly with LookupEnum."""

  def test_placement_from_string_full_names(self):
    """Test OrdinalEnum from_string with full names."""
    assert OrdinalEnum.from_string('NORTH') == OrdinalEnum.NORTH
    assert OrdinalEnum.from_string('south') == OrdinalEnum.SOUTH
    assert OrdinalEnum.from_string('NorthEast') == OrdinalEnum.NORTHEAST

  def test_placement_from_string_aliases(self):
    """Test OrdinalEnum from_string with aliases."""
    assert OrdinalEnum.from_string('N') == OrdinalEnum.NORTH
    assert OrdinalEnum.from_string('s') == OrdinalEnum.SOUTH
    assert OrdinalEnum.from_string('ne') == OrdinalEnum.NORTHEAST
    assert OrdinalEnum.from_string('SW') == OrdinalEnum.SOUTHWEST

  def test_placement_from_string_none(self):
    """Test OrdinalEnum from_string with None/empty."""
    assert OrdinalEnum.from_string('') == OrdinalEnum.NONE
    assert OrdinalEnum.from_string(None) == OrdinalEnum.NONE
    assert OrdinalEnum.from_string('none') == OrdinalEnum.NONE
    assert OrdinalEnum.from_string('NULL') == OrdinalEnum.NULL

  def test_placement_parse_sides_string(self):
    """Test OrdinalEnum parse_sides_string."""
    result = OrdinalEnum.parse_sides_string('N,S,E,W')
    assert result == [
      OrdinalEnum.NORTH,
      OrdinalEnum.SOUTH,
      OrdinalEnum.EAST,
      OrdinalEnum.WEST,
    ]

    result = OrdinalEnum.parse_sides_string('northeast southwest')
    assert result == [OrdinalEnum.NORTHEAST, OrdinalEnum.SOUTHWEST]

  def test_placement_intflag_behavior(self):
    """Test that OrdinalEnum still works as IntFlag."""
    # Test bitwise operations
    combined = OrdinalEnum.NORTH | OrdinalEnum.EAST
    assert combined == OrdinalEnum.NORTHEAST

    # Test flag checking
    assert OrdinalEnum.NORTH in OrdinalEnum.NORTHEAST
    assert OrdinalEnum.EAST in OrdinalEnum.NORTHEAST
    assert OrdinalEnum.SOUTH not in OrdinalEnum.NORTHEAST


class TestMixinRequirement:
  """Test that LookupEnum requires _get_default_value implementation."""

  def test_enums_have_default_value_method(self):
    """Test that enum classes implement _get_default_value."""
    # Verify our test enums implement it
    assert hasattr(SampleStringEnum, '_get_default_value')
    assert hasattr(SampleIntEnum, '_get_default_value')
    assert hasattr(OrdinalEnum, '_get_default_value')

    # Verify they return the expected defaults
    assert SampleStringEnum._get_default_value() == SampleStringEnum.NONE
    assert SampleIntEnum._get_default_value() == SampleIntEnum.ZERO
    assert OrdinalEnum._get_default_value() == OrdinalEnum.NONE

  def test_missing_default_value_raises_error(self):
    """Test that using LookupEnum without _get_default_value raises NotImplementedError."""

    # Create a test enum that doesn't implement _get_default_value
    class BadEnum(LookupEnum, StrEnum):
      """Test enum missing _get_default_value."""

      ONE = auto()
      TWO = auto()

    # With new default behavior, should return first enum (ONE)
    assert BadEnum.from_string('') == BadEnum.ONE
    assert BadEnum.from_string(None) == BadEnum.ONE

    # Verify it's using the default implementation
    assert BadEnum._get_default_value() == BadEnum.ONE

  def test_empty_enum_raises_value_error(self):
    """Test that empty enum raises ValueError when getting default."""

    class EmptyEnum(LookupEnum, StrEnum):
      """Test enum with no members."""

      pass

    # Should raise ValueError for empty enum
    with pytest.raises(ValueError, match='Enum EmptyEnum has no members'):
      EmptyEnum._get_default_value()

    # Should also raise when trying to use from_string with empty name
    with pytest.raises(ValueError, match='Enum EmptyEnum has no members'):
      EmptyEnum.from_string('')
