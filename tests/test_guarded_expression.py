"""Integration tests for the guarded_expression decorator."""
import pytest
from modgud.guarded_expression import CommonGuards, guarded_expression
from modgud.guarded_expression.errors import ExplicitReturnDisallowedError, GuardClauseError


# Test basic guard clause functionality
def test_basic_guard_success():
  """Test that function executes when all guards pass."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    implicit_return=False
  )
  def double(x):
    return x * 2

  result = double(5)
  assert result == 10


def test_basic_guard_failure_default_error():
  """Test that GuardClauseError is raised by default on guard failure."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    implicit_return=False
  )
  def double(x):
    return x * 2

  with pytest.raises(GuardClauseError) as exc_info:
    double(-5)
  assert "Must be positive" in str(exc_info.value)


def test_guard_failure_custom_return_value():
  """Test returning custom value on guard failure."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    on_error={"error": "Invalid input"},
    implicit_return=False
  )
  def double(x):
    return x * 2

  result = double(-5)
  assert result == {"error": "Invalid input"}


def test_guard_failure_custom_exception():
  """Test raising custom exception on guard failure."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    on_error=ValueError,
    implicit_return=False
  )
  def double(x):
    return x * 2

  with pytest.raises(ValueError) as exc_info:
    double(-5)
  assert "Must be positive" in str(exc_info.value)


def test_guard_failure_custom_handler():
  """Test using custom handler function on guard failure."""
  def custom_handler(error_msg, *args, **kwargs):
    return f"Handled: {error_msg}"

  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    on_error=custom_handler,
    implicit_return=False
  )
  def double(x):
    return x * 2

  result = double(-5)
  assert result == "Handled: Must be positive"


def test_multiple_guards_all_pass():
  """Test that function executes when all guards pass."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
    implicit_return=False
  )
  def double(x):
    return x * 2

  result = double(50)
  assert result == 100


def test_multiple_guards_first_fails():
  """Test that first guard failure stops evaluation."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
    implicit_return=False
  )
  def double(x):
    return x * 2

  with pytest.raises(GuardClauseError) as exc_info:
    double(-5)
  assert "Must be positive" in str(exc_info.value)


def test_multiple_guards_second_fails():
  """Test that second guard failure is caught."""
  @guarded_expression(
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
    implicit_return=False
  )
  def double(x):
    return x * 2

  with pytest.raises(GuardClauseError) as exc_info:
    double(150)
  assert "Must be less than 100" in str(exc_info.value)


# Test implicit return functionality
def test_implicit_return_simple():
  """Test basic implicit return without branching."""
  from tests.test_fixtures import calculate

  result = calculate()
  assert result == 30


def test_implicit_return_with_if_else():
  """Test implicit return with if/else branching."""
  from tests.test_fixtures import classify

  assert classify(5) == "positive"
  assert classify(-5) == "non-positive"
  assert classify(0) == "non-positive"


def test_implicit_return_with_try_except():
  """Test implicit return with try/except."""
  from tests.test_fixtures import safe_divide

  assert safe_divide(10, 2) == 5.0
  assert safe_divide(10, 0) == 0


def test_implicit_return_disallows_explicit_return():
  """Test that explicit return raises error with implicit_return=True."""
  with pytest.raises(ExplicitReturnDisallowedError):
    @guarded_expression(implicit_return=True, on_error=GuardClauseError)
    def bad_function():
      x = 10
      return x  # Should raise error


# Test combined guard + implicit return
def test_combined_guard_and_implicit_return():
  """Test guard validation with implicit return."""
  from tests.test_fixtures import safe_divide_with_guard

  assert safe_divide_with_guard(2) == 50.0

  with pytest.raises(GuardClauseError) as exc_info:
    safe_divide_with_guard(-5)
  assert "Must be positive" in str(exc_info.value)


def test_common_guards_with_implicit_return():
  """Test CommonGuards with implicit return."""
  from tests.test_fixtures import double_with_guards

  assert double_with_guards(5) == 10

  with pytest.raises(GuardClauseError):
    double_with_guards(-5)


# Test CommonGuards
def test_common_guard_not_none():
  """Test CommonGuards.not_none."""
  @guarded_expression(
    CommonGuards.not_none("value"),
    implicit_return=False
  )
  def process(value):
    return value * 2

  assert process(5) == 10

  with pytest.raises(GuardClauseError):
    process(None)


def test_common_guard_positive():
  """Test CommonGuards.positive."""
  @guarded_expression(
    CommonGuards.positive("value"),
    implicit_return=False
  )
  def process(value):
    return value * 2

  assert process(5) == 10

  with pytest.raises(GuardClauseError):
    process(-5)


def test_common_guard_not_empty():
  """Test CommonGuards.not_empty."""
  @guarded_expression(
    CommonGuards.not_empty("text"),
    implicit_return=False
  )
  def process(text):
    return text.upper()

  assert process("hello") == "HELLO"

  with pytest.raises(GuardClauseError):
    process("")


def test_common_guard_type_check():
  """Test CommonGuards.type_check."""
  @guarded_expression(
    CommonGuards.type_check(str, "text"),
    implicit_return=False
  )
  def process(text):
    return text.upper()

  assert process("hello") == "HELLO"

  with pytest.raises(GuardClauseError):
    process(123)


def test_common_guard_in_range():
  """Test CommonGuards.in_range."""
  @guarded_expression(
    CommonGuards.in_range(0, 100, "value"),
    implicit_return=False
  )
  def process(value):
    return value * 2

  assert process(50) == 100

  with pytest.raises(GuardClauseError):
    process(150)


def test_common_guard_matches_pattern():
  """Test CommonGuards.matches_pattern."""
  @guarded_expression(
    CommonGuards.matches_pattern(r"^\d{3}-\d{4}$", "phone"),
    implicit_return=False
  )
  def process(phone):
    return phone.replace("-", "")

  assert process("555-1234") == "5551234"

  with pytest.raises(GuardClauseError):
    process("invalid")


# Test metadata preservation
def test_metadata_preservation():
  """Test that function metadata is preserved."""
  @guarded_expression(implicit_return=False, on_error=GuardClauseError)
  def documented_function(x: int) -> int:
    """This is a documented function."""
    return x * 2

  assert documented_function.__name__ == "documented_function"
  assert documented_function.__doc__ == "This is a documented function."
  assert documented_function.__annotations__ == {"x": int, "return": int}


# Test no guards case
def test_no_guards_implicit_return_false():
  """Test decorator with no guards and implicit_return=False."""
  @guarded_expression(implicit_return=False, on_error=GuardClauseError)
  def simple(x):
    return x * 2

  assert simple(5) == 10


def test_no_guards_implicit_return_true():
  """Test decorator with no guards and implicit_return=True."""
  from tests.test_fixtures import simple_implicit

  assert simple_implicit(5) == 10


# Test async functions
def test_async_with_guards_and_implicit_return():
  """Test async function with guards and implicit return."""
  import asyncio

  from tests.test_fixtures import async_double

  # Test success
  result = asyncio.run(async_double(5))
  assert result == 10

  # Test guard failure
  with pytest.raises(GuardClauseError):
    asyncio.run(async_double(-5))


def test_async_implicit_return_with_branching():
  """Test async function with implicit return and if/else."""
  import asyncio

  from tests.test_fixtures import async_classify

  assert asyncio.run(async_classify(5)) == "positive"
  assert asyncio.run(async_classify(-5)) == "non-positive"


def test_async_explicit_return():
  """Test async function with explicit return (implicit_return=False)."""
  import asyncio

  from tests.test_fixtures import async_explicit_return

  result = asyncio.run(async_explicit_return(5))
  assert result == 15


# CommonGuards edge case tests (coverage improvement)
def test_common_guards_kwargs_precedence():
  """Test kwargs take precedence over positional args."""
  @guarded_expression(
    CommonGuards.positive("value", position=1),  # Expects second positional
    implicit_return=False
  )
  def process(x, y, value=5):
    return value * 2

  # Positional arg at position 1 is 2, but kwarg value=10 takes precedence
  assert process(1, 2, value=10) == 20
  # Positional arg at position 1 is -5, but kwarg value=3 takes precedence
  assert process(1, -5, value=3) == 6
  # No kwarg provided, guard checks position 1 (y=-5), which is negative
  with pytest.raises(GuardClauseError):
    process(1, -5)


def test_extract_param_out_of_bounds():
  """Test _extract_param with invalid position returns default."""
  @guarded_expression(
    CommonGuards.positive("x", position=5),  # No 6th arg
    implicit_return=False
  )
  def process(a, b):
    return a + b

  # Only 2 args, position 5 doesn't exist, uses default=0, fails positive check
  with pytest.raises(GuardClauseError):
    process(1, 2)


def test_not_empty_with_object_lacking_len():
  """Test not_empty with object lacking __len__ method."""
  class NoLen:
    def __bool__(self):
      return False

  @guarded_expression(
    CommonGuards.not_empty("obj"),
    implicit_return=False
  )
  def process(obj):
    return "processed"

  # Object without __len__ falls back to bool() check
  with pytest.raises(GuardClauseError):
    process(NoLen())


# Decorator error handling tests (coverage improvement)
def test_decorator_source_unavailable():
  """Test decorator fails gracefully when source unavailable."""
  from modgud.guarded_expression.errors import UnsupportedConstructError

  # Create function from compiled code
  code = compile("def foo(): return 42", "<string>", "exec")
  env = {}
  exec(code, env)

  with pytest.raises(UnsupportedConstructError, match="Source unavailable"):
    guarded_expression(implicit_return=True)(env['foo'])
