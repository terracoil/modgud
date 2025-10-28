"""Tests for function metadata preservation through decoration."""

from modgud import guarded_expression
from modgud.domain.models.errors import GuardClauseError


class TestMetadataPreservation:
  """Tests for function metadata preservation through decoration."""

  def test_metadata_preservation(self):
    """Function metadata should be preserved after decoration."""

    @guarded_expression(implicit_return=False, on_error=GuardClauseError)
    def documented_function(x: int) -> int:
      """Multiply input by two."""
      return x * 2

    assert documented_function.__name__ == 'documented_function'
    assert documented_function.__doc__ == 'Multiply input by two.'
    assert documented_function.__annotations__ == {'x': int, 'return': int}
