"""
Decorators for expression-oriented programming.

This sub-package contains all decorator implementations for modgud's
expression-oriented features.
"""

from .chained_expression_decorator import ChainedExpressionDecorator
from .guarded_expression import guarded_expression
from .implicit_return_decorator import implicit_return
from .inject_decorator import DependencyInjectionError, Inject, inject, inject_auto
from .pipeable import pipeable
from .safe_expression_decorator import SafeExpressionDecorator

__all__ = [
  'guarded_expression',
  'implicit_return',
  'pipeable',
  'SafeExpressionDecorator',
  'ChainedExpressionDecorator',
  'Inject',
  'inject',
  'inject_auto',
  'DependencyInjectionError',
]
