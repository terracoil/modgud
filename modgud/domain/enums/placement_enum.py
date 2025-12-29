"""
Placement enum for modgud domain layer.

Enumeration for cardinal directions and compound directions with enhanced lookup functionality.
"""
from __future__ import annotations
from enum import IntFlag, auto, nonmember
from typing import Sequence


class PlacementEnum(IntFlag):
  """
  Placement enumeration for cardinal and compound directions.

  Uses bitmask pattern for cardinal directions (powers of 2) allowing
  compound directions to be created by combining values.
  """

  # Ordinal Values:
  NONE = 0
  NORTH = auto()
  SOUTH = auto()
  EAST = auto()
  WEST = auto()

  # Sub-ordinal Values:
  NORTHEAST = NORTH | EAST
  NORTHWEST = NORTH | WEST
  SOUTHEAST = SOUTH | EAST
  SOUTHWEST = SOUTH | WEST

  # Enum aliases
  NULL = NONE
  N = NORTH
  S = SOUTH
  E = EAST
  W = WEST
  NE = NORTHEAST
  NW = NORTHWEST
  SE = SOUTHEAST
  SW = SOUTHWEST

  @classmethod
  def __dir__(cls):
    return cls.__members__.keys()

  @classmethod
  def _check_key(cls, value: str | None) -> str:
    """ Check key for validity and return converted key; (name.upper() || NONE.name())."""
    key: str = str(value).upper() if value else cls.NONE.name
    if not key in cls:
      raise ValueError(f"String: {key}(arg:{value}) is not a valid PlacementEnum: [{', '.join(dir(cls))}]")

    return key

  @classmethod
  def from_string(cls, value: str) -> PlacementEnum:
    """
    Convert string to PlacementEnum with comprehensive lookup support.

    Supports:
    - Full names: "North", "SOUTH", "northwest"
    - Single letters: "N", "S", "E", "W"
    - Compound directions: "NE", "SW", "nw", "se"
    - Special: "None"

    :param value: String representation
    :returns: Corresponding PlacementEnum
    :raises ValueError: If value doesn't match any placement
    """

    key: str = cls._check_key(value)
    return cls[key]

  @classmethod
  def from_list(cls, values: Sequence[str]) -> list['PlacementEnum']:
    """
    Convert list of strings to PlacementEnum list.

    :param values: List of string representations
    :returns: List of corresponding PlacementEnum values
    :raises ValueError: If any value doesn't match
    """
    return [cls.from_string(value) for value in values]

  @classmethod
  def parse_sides_string(cls, sides_str: str) -> list['PlacementEnum']:
    """
    Parse comma/space separated sides string into PlacementEnum list.

    :param sides_str: String like "NORTH,SOUTH" or "N S" or "north, south"
    :returns: List of PlacementEnum values
    :raises ValueError: If any side is invalid
    """
    sides:list[str]=sides_str.replace(',', ' ').split()
    return cls.from_list(sides)
