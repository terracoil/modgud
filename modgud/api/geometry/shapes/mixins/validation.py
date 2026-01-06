"""Validation mixin for shape parameter checking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modgud.domain.enums import OrdinalEnum

if TYPE_CHECKING:
  pass


class ValidationMixin:
  """
  Mixin providing parameter validation capabilities for shape classes.

  Handles validation of:
  - Dimensional parameters (width, height, side length, etc.)
  - Torn edge configuration
  - Notch configuration
  - Noise parameters
  """

  def _validate_params(self) -> None:
    """
    Validate all shape parameters.

    This method should be called in __post_init__ of dataclasses to ensure
    all parameters are valid before shape construction begins.

    Raises:
      ValueError: If any parameter is invalid

    """
    self._validate_dimensions()
    self._validate_torn_edges()
    self._validate_notches()

  def _validate_dimensions(self) -> None:
    """
    Validate dimensional parameters are positive and within acceptable range.

    Each shape class should override this if they have specific validation needs.
    Default implementation validates common attributes if they exist.
    """
    # Check common dimensional attributes if they exist
    for attr_name in ['side', 'width', 'height', 'w', 'h', 'w1', 'w2', 'diagonal1', 'diagonal2']:
      if hasattr(self, attr_name):
        value = getattr(self, attr_name)
        if isinstance(value, (int, float)) and value <= 0:
          raise ValueError(f'{attr_name.title()} must be positive, got {value}')

    # Validate side_left if it exists
    if hasattr(self, 'side_left') and hasattr(self, 'h'):
      side_left = self.side_left
      h = self.h
      if side_left is not None and side_left < h:
        raise ValueError(f'side_left ({side_left}) must be >= height ({h})')

  def _validate_torn_edges(self) -> None:
    """
    Validate torn edge configuration.

    Checks that:
    - torn_sides is a valid list of OrdinalEnum values
    - noise is provided when torn_sides is specified
    - noise parameters are reasonable
    """
    if not hasattr(self, 'torn_sides'):
      return

    torn_sides = getattr(self, 'torn_sides', [])
    noise = getattr(self, 'noise', None)

    # Check for valid torn sides specification
    if torn_sides and any(side != OrdinalEnum.NONE for side in torn_sides):
      self._validate_torn_sides_enum(torn_sides)

      # Noise is required for torn edges
      if not noise:
        raise ValueError('noise parameter required when torn_sides is specified')

      # Validate noise parameters
      amplitude = getattr(self, 'noise_amplitude', 5.0)
      segments = getattr(self, 'noise_segments', 100)

      if amplitude <= 0:
        raise ValueError(f'noise_amplitude must be positive, got {amplitude}')
      if segments <= 0:
        raise ValueError(f'noise_segments must be positive, got {segments}')

  def _validate_notches(self) -> None:
    """
    Validate notch configuration.

    Checks that:
    - notch_sides is a valid list of OrdinalEnum values
    - notch parameters are reasonable
    """
    if not hasattr(self, 'notch_sides'):
      return

    notch_sides = getattr(self, 'notch_sides', [])

    if notch_sides and any(side != OrdinalEnum.NONE for side in notch_sides):
      self._validate_notch_sides_enum(notch_sides)

      # Validate notch parameters
      notch_size = getattr(self, 'notch_size', 0.1)
      notch_depth = getattr(self, 'notch_depth', 0.0)
      notch_offset = getattr(self, 'notch_offset', 0.0)

      if not (0 < notch_size <= 1):
        raise ValueError(f'notch_size must be in (0, 1], got {notch_size}')
      if notch_depth < 0:
        raise ValueError(f'notch_depth must be non-negative, got {notch_depth}')
      if not (-1 <= notch_offset <= 1):
        raise ValueError(f'notch_offset must be in [-1, 1], got {notch_offset}')

  def _validate_torn_sides_enum(self, torn_sides: list[OrdinalEnum]) -> None:
    """
    Validate that torn_sides contains valid OrdinalEnum values.

    Args:
      torn_sides: List of sides to apply torn effects

    Raises:
      ValueError: If invalid torn side specified

    """
    valid_sides = {
      OrdinalEnum.NORTH,
      OrdinalEnum.SOUTH,
      OrdinalEnum.EAST,
      OrdinalEnum.WEST,
      OrdinalEnum.NONE,
    }

    for side in torn_sides:
      if side not in valid_sides:
        raise ValueError(f'Invalid torn side: {side}. Must be one of {valid_sides}')

  def _validate_notch_sides_enum(self, notch_sides: list[OrdinalEnum]) -> None:
    """
    Validate that notch_sides contains valid OrdinalEnum values.

    Args:
      notch_sides: List of sides to apply notches

    Raises:
      ValueError: If invalid notch side specified

    """
    valid_sides = {
      OrdinalEnum.NORTH,
      OrdinalEnum.SOUTH,
      OrdinalEnum.EAST,
      OrdinalEnum.WEST,
      OrdinalEnum.NONE,
    }

    for side in notch_sides:
      if side not in valid_sides:
        raise ValueError(f'Invalid notch side: {side}. Must be one of {valid_sides}')
