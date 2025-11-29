"""
Pipeable decorator for the app layer.

This module provides the @pipeable decorator that uses dependency injection
to get the infrastructure implementation, maintaining clean architecture.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from ...domain.protocols import PipeableFactoryProtocol, PipeableProtocol
from ...infrastructure.pipeable_factory import PipeableFactory

T = TypeVar('T')

# Create factory instance (in production this would come from DI container)
_pipeable_factory: PipeableFactoryProtocol = PipeableFactory()


def pipeable(func: Callable[..., T]) -> PipeableProtocol:
  """
  Decorator that makes functions pipeable via | operator.

  This decorator wraps a function in a Pipeable instance, enabling it to be used
  in functional-style pipelines with the | operator. It supports partial application
  and preserves function metadata.

  Can also be used with built-in types and functions directly:
      result = 5 | pipeable(str) | pipeable(len)  # "5" -> 1

  Args:
      func: The function to make pipeable

  Returns:
      A Pipeable wrapper around the function

  Example:
      @pipeable
      def add(x, y):
          return x + y

      @pipeable
      def multiply(x, factor):
          return x * factor

      # Usage
      result = 5 | add(3) | multiply(2)  # Returns 16

      # Partial application
      add_ten = add(10)
      result = 5 | add_ten  # Returns 15

  """
  return _pipeable_factory.pipeable_decorator(func)


# For compatibility with the infrastructure, also provide the factory
def create_pipeable(func: Callable[..., Any]) -> PipeableProtocol:
  """
  Create a pipeable wrapper around a function.

  Args:
      func: The function to make pipeable

  Returns:
      PipeableProtocol: Pipeable wrapper around the function

  """
  return _pipeable_factory.create_pipeable(func)


# Export the Pipeable class for tests that need direct access
from ...infrastructure.pipeable_wrapper import Pipeable

__all__ = ['pipeable', 'create_pipeable', 'Pipeable']
