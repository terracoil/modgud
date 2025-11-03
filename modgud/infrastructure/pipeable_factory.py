"""
Pipeable factory for creating pipeable decorators and wrappers.

This module provides the PipeableFactory class for creating pipeable decorators,
following clean architecture principles by implementing domain protocols.
"""

from __future__ import annotations
from typing import Any, Callable, TypeVar
from ..domain.protocols import PipeableFactoryProtocol, PipeableProtocol
from .pipeable_wrapper import Pipeable

T = TypeVar('T')


class PipeableFactory(PipeableFactoryProtocol):
    """
    Factory for creating pipeable decorators and utilities.
    Provides clean interface for functional programming patterns.
    """

    def create_pipeable(self, func: Callable[..., Any]) -> PipeableProtocol:
        """
        Create a pipeable wrapper around a function.
        
        Args:
            func: The function to make pipeable
            
        Returns:
            PipeableProtocol: Pipeable wrapper around the function
        """
        # Handle built-in types that need special treatment
        if isinstance(func, type):
            # For types like str, int, float, create a converter function
            def type_converter(x):
                return func(x)
            type_converter.__name__ = func.__name__
            type_converter.__doc__ = f"Convert to {func.__name__}"
            return Pipeable(type_converter)
        
        return Pipeable(func)

    def pipeable_decorator(self, func: Callable[..., T]) -> PipeableProtocol:
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
        return self.create_pipeable(func)