"""Test fixtures for guarded_expression tests.

These functions are defined at module level so their source can be inspected
by the implicit_return transformer.
"""
from modgud.guarded_expression import CommonGuards, guarded_expression
from modgud.shared.errors import GuardClauseError


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
    "positive"
  else:
    "non-positive"


# Implicit return with try/except
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def safe_divide(x, y):
  try:
    x / y
  except ZeroDivisionError:
    0


# Combined guard and implicit return
@guarded_expression(
  lambda x: x > 0 or "Must be positive",
  implicit_return=True
)
def safe_divide_with_guard(x):
  result = 100 / x
  result


# CommonGuards with implicit return
@guarded_expression(
  CommonGuards.not_none("x"),
  CommonGuards.positive("x"),
  implicit_return=True
)
def double_with_guards(x):
  x * 2


# No guards, implicit return true
@guarded_expression(implicit_return=True, on_error=GuardClauseError)
def simple_implicit(x):
  x * 2


# Async functions
import asyncio


@guarded_expression(
  lambda x: x > 0 or "Must be positive",
  implicit_return=True
)
async def async_double(x):
  await asyncio.sleep(0)
  x * 2


@guarded_expression(
  CommonGuards.not_none("x"),
  implicit_return=True
)
async def async_classify(x):
  await asyncio.sleep(0)
  if x > 0:
    "positive"
  else:
    "non-positive"


@guarded_expression(
  implicit_return=False,
  on_error=None
)
async def async_explicit_return(x):
  await asyncio.sleep(0)
  return x * 3
