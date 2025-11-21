"""
Ranger: Extended range functionality for multiple data types.

Provides range-like iteration for integers, floats, and strings,
eliminating the need for type-specific iteration boilerplate.
"""

import string
from collections.abc import Iterator
from typing import Any

RangeValueType = int | float | str
RangeType = RangeValueType | Any


class Ranger:
  """
  Range-like iterator supporting numeric and string types.

  Enables iteration over sequences of integers, floats, or strings
  where traditional range limitations don't apply.
  """

  _CHARSET: str = string.ascii_letters + string.digits + string.punctuation

  def __init__(
    self,
    start: RangeValueType,
    stop: RangeValueType | None = None,
    step: RangeValueType | None = None,
  ) -> None:
    """
    Initialize a Ranger instance.

    Provides range-like iteration for types beyond integers,
    avoiding the need for manual iteration logic in calling code.

    :param start: Starting value or stop value if only one argument
    :param stop: Ending value (exclusive)
    :param step: Step increment between values
    """
    start_norm: RangeValueType = self._normalize_value(start)
    stop_norm: RangeValueType = self._normalize_value(stop) if stop is not None else None

    if stop_norm is None:
      self._start = self._zero_value(start_norm)
      self._stop = start_norm
      self._step = self._unit_step(start_norm)
    elif step is None:
      self._start = start_norm
      self._stop = stop_norm
      self._step = self._unit_step(start_norm)
    else:
      self._start = start_norm
      self._stop = stop_norm
      self._step = step

  @staticmethod
  def _normalize_value(value: RangeValueType) -> RangeValueType:
    """Convert value to appropriate type for iteration."""
    return value if isinstance(value, (int, float, str)) else str(value)

  @staticmethod
  def _zero_value(value: RangeValueType) -> RangeValueType:
    """Return the zero/empty value for a given type."""
    return 0 if isinstance(value, (int, float)) else ''

  @staticmethod
  def _unit_step(value: RangeValueType) -> RangeValueType:
    """Return the unit step value for a given type."""
    return 1

  def _increment_string(self, s: str, count: int) -> str:
    """
    Increment a string by treating it as a base-N number.

    Enables string sequence generation without manual character manipulation
    in iteration logic.

    :param s: String to increment
    :param count: Number of increments to perform
    :return: Incremented string
    """
    result = s
    for _ in range(count):
      result = self._increment_once(result)
    return result

  def _increment_once(self, s: str) -> str:
    """Increment a string by one position in the character set."""
    if not s:
      return self._CHARSET[0]

    chars = list(s)
    carry = True
    pos = len(chars) - 1

    while carry and pos >= 0:
      char_idx = self._CHARSET.index(chars[pos])
      new_idx = char_idx + 1

      if new_idx < len(self._CHARSET):
        chars[pos] = self._CHARSET[new_idx]
        carry = False
      else:
        chars[pos] = self._CHARSET[0]
        pos -= 1

    result = (self._CHARSET[0] + ''.join(chars)) if carry else ''.join(chars)
    return result

  def __iter__(self) -> Iterator[RangeValueType]:
    """
    Iterate over the range.

    Yields successive values to avoid materializing the entire
    sequence in memory.

    :return: Iterator over range values
    """
    current = self._start

    if isinstance(current, (int, float)):
      ascending = self._step > 0
      while (ascending and current < self._stop) or (not ascending and current > self._stop):
        yield current
        current = current + self._step
    else:
      step_count = self._step if isinstance(self._step, int) else 1
      while current < self._stop:
        yield current
        current = self._increment_string(current, step_count)


if __name__ == '__main__':
  # Integer example
  print('Integers 0-5:')
  print(list(Ranger(5)))

  # Float example
  print('\nFloats 0.0-2.0 by 0.5:')
  print(list(Ranger(0.0, 2.0, 0.5)))

  # String example
  print("\nStrings from 'a' to 'd':")
  print(list(Ranger('a', 'd')))

  # String with step
  print("\nStrings from 'a' to 'f' with step 2:")
  print(list(Ranger('a', 'f', 2)))

  # String rollover example
  print('\nString rollover (last 5 of charset):')
  charset_demo = Ranger('', 'ab')
  print(list(charset_demo)[-10:])
