"""
Placement enum for modgud domain layer.

Enumeration for cardinal directions and compound directions with enhanced lookup functionality.
"""

from __future__ import annotations

from enum import IntFlag, auto
from typing import TYPE_CHECKING

from .lookup_enum import LookupEnum

if TYPE_CHECKING:
  from typing import Self


class OrdinalEnum(LookupEnum, IntFlag):
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
  def _get_default_value(cls) -> Self:
    """Return NONE as default for empty/None lookups."""
    return cls.NONE

  # Override from_string to add docstring with OrdinalEnum-specific examples
  @classmethod
  def from_string(cls, value: str) -> Self:
    """
    Convert string to OrdinalEnum with comprehensive lookup support.

    Supports:
    - Full names: "North", "SOUTH", "northwest"
    - Single letters: "N", "S", "E", "W"
    - Compound directions: "NE", "SW", "nw", "se"
    - Special: "None"

    :param value: String representation
    :returns: Corresponding OrdinalEnum
    :raises ValueError: If name doesn't match any placement
    """
    return super().from_string(value)
