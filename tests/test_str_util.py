"""Tests for StrUtils utility class."""

from modgud.util.str_util import StrUtils


class TestCamelCase:
  """Test to_camel_case conversion."""

  def test_snake_to_camel(self) -> None:
    """Test snake_case to camelCase."""
    assert StrUtils.to_camel_case('hello_world') == 'helloWorld'

  def test_single_word(self) -> None:
    """Test single word stays lowercase."""
    assert StrUtils.to_camel_case('hello') == 'hello'

  def test_multiple_underscores(self) -> None:
    """Test multiple underscored words."""
    assert StrUtils.to_camel_case('one_two_three') == 'oneTwoThree'


class TestPascalCase:
  """Test to_pascal_case conversion."""

  def test_snake_to_pascal(self) -> None:
    """Test snake_case to PascalCase."""
    assert StrUtils.to_pascal_case('hello_world') == 'HelloWorld'

  def test_single_word(self) -> None:
    """Test single word gets capitalized."""
    assert StrUtils.to_pascal_case('hello') == 'Hello'


class TestSnakeCase:
  """Test to_snake_case conversion."""

  def test_camel_to_snake(self) -> None:
    """Test camelCase to snake_case."""
    assert StrUtils.to_snake_case('helloWorld') == 'hello_world'

  def test_pascal_to_snake(self) -> None:
    """Test PascalCase to snake_case."""
    assert StrUtils.to_snake_case('HelloWorld') == 'hello_world'


class TestToPctStr:
  """Test to_pct_str percentage string formatting."""

  def test_basic_percentage(self) -> None:
    """Test basic percentage formatting."""
    assert StrUtils.to_pct_str(0.5) == '50.0%'

  def test_zero(self) -> None:
    """Test zero value."""
    assert StrUtils.to_pct_str(0.0) == '0.0%'

  def test_full(self) -> None:
    """Test 100% value."""
    assert StrUtils.to_pct_str(1.0) == '100.0%'

  def test_precision_zero(self) -> None:
    """Test with zero decimal places."""
    assert StrUtils.to_pct_str(0.5, p=0) == '50%'

  def test_precision_two(self) -> None:
    """Test with two decimal places."""
    assert StrUtils.to_pct_str(0.12345, p=2) == '12.35%'

  def test_padding(self) -> None:
    """Test padding adds leading spaces."""
    result = StrUtils.to_pct_str(0.5, pad=3)
    # Should be right-justified with extra padding
    assert result.endswith('%')
    assert len(result) > len('50.0%')

  def test_small_value(self) -> None:
    """Test small fractional percentage."""
    assert StrUtils.to_pct_str(0.001) == '0.1%'
