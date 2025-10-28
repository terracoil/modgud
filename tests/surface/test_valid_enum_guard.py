"""Tests for valid_enum guard."""

from enum import Enum

import pytest
from modgud import guarded_expression, valid_enum
from modgud.domain.models.errors import GuardClauseError


class TestValidEnumGuard:
  """Tests for valid_enum guard."""

  def test_valid_enum_value(self):
    """Test guard passes for valid enum value."""

    class Color(Enum):
      RED = 'red'
      GREEN = 'green'
      BLUE = 'blue'

    @guarded_expression(valid_enum(Color, 'color'), implicit_return=False)
    def set_color(color: str):
      return f'Color set to {color}'

    result = set_color('red')
    assert 'Color set to' in result

  def test_enum_instance_passes(self):
    """Test guard passes when enum instance provided."""

    class Status(Enum):
      ACTIVE = 'active'
      INACTIVE = 'inactive'

    @guarded_expression(valid_enum(Status, 'status'), implicit_return=False)
    def set_status(status):
      return f'Status: {status.value if isinstance(status, Status) else status}'

    result = set_status(Status.ACTIVE)
    assert 'active' in result

  def test_invalid_enum_value_fails(self):
    """Test guard fails for invalid enum value."""

    class Priority(Enum):
      LOW = 'low'
      MEDIUM = 'medium'
      HIGH = 'high'

    @guarded_expression(valid_enum(Priority, 'priority'), implicit_return=False)
    def set_priority(priority: str):
      return f'Priority: {priority}'

    with pytest.raises(GuardClauseError, match='must be one of'):
      set_priority('urgent')

  def test_none_value_fails(self):
    """Test guard fails when None provided."""

    class Mode(Enum):
      DEBUG = 'debug'
      RELEASE = 'release'

    @guarded_expression(valid_enum(Mode, 'mode'), implicit_return=False)
    def set_mode(mode: str):
      return f'Mode: {mode}'

    with pytest.raises(GuardClauseError, match='is required'):
      set_mode(None)
