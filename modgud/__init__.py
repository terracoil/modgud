"""Modgud - guard clauses + implicit returns for Python.

The package structure *is* the public API - import each symbol from the leaf
subpackage that owns it rather than from the top-level ``modgud`` namespace:

- ``from modgud.app import guarded_expression, implicit_return`` - the decorators.
- ``from modgud.domain.guarded_expr import GuardFailureStrategy, GuardClauseError``
  - failure-dispatch enum and guard error.
- ``from modgud.domain.implicit_ret import ImplicitReturnError`` (and its three
  subclasses) - implicit-return transformation errors.
- ``from modgud.infrastructure.guarded_expr import CommonGuards, GuardRegistry``
  - pre-built guard validators (as ``CommonGuards`` static methods) and the
  custom-guard registry.

Example::

    from modgud.app import guarded_expression
    from modgud.domain.guarded_expr import GuardFailureStrategy
    from modgud.infrastructure.guarded_expr import CommonGuards


    @guarded_expression(CommonGuards.positive('x'))
    def double(x):
      x * 2  # implicit return


    @guarded_expression(
      CommonGuards.positive('x'),
      strategy=GuardFailureStrategy.RETURN_VALUE,
      on_failure=-1,
    )
    def safe_square(x):
      x * x


    # Collect up to two extra failures past the first:
    @guarded_expression(
      CommonGuards.positive('x'),
      CommonGuards.positive('y'),
      continuance=2,
    )
    def add(x, y):
      x + y
"""

__version__ = '2.0.0'
