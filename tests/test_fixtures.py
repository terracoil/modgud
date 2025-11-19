"""
Test fixtures for guarded_expression tests.

These functions are defined at module level so their source can be inspected
by the implicit_return transformer.
"""

from modgud import not_none, positive
from modgud.expression_oriented import guarded_expression
from modgud.expression_oriented.core.errors import GuardClauseError


# Simple implicit return
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def calculate():
  x = 10
  y = 20
  x + y


# Implicit return with if/else
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def classify(x):
  if x > 0:
    'positive'
  else:
    'non-positive'


# Implicit return with try/except
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def safe_divide(x, y):
  try:
    x / y
  except ZeroDivisionError:
    0


# Combined guard and implicit return
@guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=True)
def safe_divide_with_guard(x):
  result = 100 / x
  result


# CommonGuards with implicit return
@guarded_expression(not_none('x'), positive('x'), implicit_return=True)
def double_with_guards(x):
  x * 2


# No guards, implicit return true
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def simple_implicit(x):
  x * 2


# Async functions
import asyncio


@guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=True)
async def async_double(x):
  await asyncio.sleep(0)
  x * 2


@guarded_expression(not_none('x'), implicit_return=True)
async def async_classify(x):
  await asyncio.sleep(0)
  if x > 0:
    'positive'
  else:
    'non-positive'


@guarded_expression(implicit_return=False, on_error=None)
async def async_explicit_return(x):
  await asyncio.sleep(0)
  return x * 3


# Deeply nested control flow for edge case testing
@guarded_expression(implicit_return=True)
def deeply_nested_function(x):
  if x == 1:
    'one'
  elif x == 2:
    if True:
      'two-a'
    else:
      'two-b'
  elif x == 3:
    if True:
      if x < 4:
        'three-a-i'
      else:
        'three-a-ii'
    else:
      'three-b'
  elif x == 4:
    if True:
      if x > 3:
        'three-a-ii'
      else:
        'three-a-i'
    else:
      'three-b'
  elif x == 5:
    if False:
      'three-a'
    else:
      'three-b'
  else:
    'other'


# Edge case: no-op function with pass only
@guarded_expression(implicit_return=True)
def noop_function(x):
  """Test no-op function with only pass statement."""
  pass


# Edge case: exception-only function (no normal return path)
@guarded_expression(implicit_return=True)
def exception_only_function(x):
  """Test function that only raises exceptions in all paths."""
  if x < 0:
    raise ValueError('Negative value')
  else:
    raise RuntimeError('Non-negative value')


# Edge case: empty function (just docstring)
@guarded_expression(implicit_return=True)
def empty_function(x):
  """Test empty function with just docstring."""


# Edge case: conditionally no return value
@guarded_expression(implicit_return=True)
def conditional_noop(x):
  """Test function where some paths have values, some have pass."""
  if x > 0:
    x * 2
  elif x < 0:
    pass
  else:
    None
