"""
Tools and utilities for expression-oriented programming.

This sub-package contains utility classes and tools that support
expression-oriented programming but are not exposed as decorators.
"""

from .chainable_expression import ChainableExpression

__all__ = [
  'ChainableExpression',
]
