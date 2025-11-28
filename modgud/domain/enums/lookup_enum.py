"""Lookup enum mixin for modgud domain layer.

Mixin class that provides string lookup functionality for enums,
supporting case-insensitive matching and aliases.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Sequence

if TYPE_CHECKING:
  from typing import Self, Type


class LookupEnum:
  """Mixin class providing string lookup functionality for enums.

  Subclasses must:
  1. Inherit from both LookupEnum and an Enum type (in that order)
  2. Implement _get_default_value() class method

  Provides case-insensitive string lookups and batch parsing utilities.
  """

  # Type hints for Enum attributes that will be mixed in
  __members__: ClassVar[dict[str, Any]]
  _valid_members: ClassVar[str]

  @classmethod
  def valid_members(cls) -> str:
    """Return and memoize a comma-separated list of valid enum member names."""
    if not cls._valid_members:
      cls._valid_members = ', '.join(sorted(cls.__members__.keys()))

    return cls._valid_members

  @classmethod
  def _get_default_value(cls) -> Enum:
    """Get the default enum name for None/empty string lookups.

    Default implementation returns the first enum name defined in the class.
    Subclasses can override this method to provide custom default behavior
    (e.g., returning a specific NONE or DEFAULT member).

    :returns: Default enum name (first enum member by default)
    :raises ValueError: If enum has no members
    """
    # Check if enum has any members
    if not cls.__members__:
      raise ValueError(
        f'Enum {cls.__name__} has no members to use as default. Define at least one enum member.'
      )

    # Get first enum name efficiently using iterator
    # This returns the first member in definition order
    default_value = next(iter(cls))  # type: ignore[arg-type]

    return default_value

  @classmethod
  def key(cls, name: str | None) -> str:
    """Check key for validity and return converted key.

    Converts to uppercase and validates against enum members.
    Returns default value's name if value is None/empty.

    :param name: String to check
    :returns: Valid uppercase key
    :raises ValueError: If key is not valid enum member
    """
    if not name:
      return cls._get_default_value().name
    else:
      key: str = str(name.strip()).upper()
    if key not in cls.__members__:
      raise ValueError(f'Key: {key} (from: {name}) is not a valid key for {cls.__name__}')

    return key

  @classmethod
  def from_string(cls: Type[Self], value: str) -> Self:
    """Convert string to enum name with case-insensitive matching.

    :param value: String representation
    :returns: Corresponding enum name
    :raises ValueError: If name doesn't match any enum member
    """
    key = cls.key(value.upper() if value else None)
    return cls[key]  # type: ignore[misc,index]

  @classmethod
  def from_list(cls: Type[Self], values: Sequence[str]) -> list[Self]:
    """Convert list of strings to enum list.

    :param values: List of string representations
    :returns: List of corresponding enum values
    :raises ValueError: If any name doesn't match
    """
    return [cls.from_string(value) for value in values]

  @classmethod
  def parse_sides_string(cls: Type[Self], sides_str: str) -> list[Self]:
    """Parse comma/space-separated enum values from string.

    :param sides_str: String containing enum values
    :returns: List of parsed enum values
    :raises ValueError: If any name is invalid
    """
    sides = sides_str.replace(',', ' ').split()
    return cls.from_list(sides)

  # def __getitem__(self, key: int) -> VectorPort | list[VectorPort]:
