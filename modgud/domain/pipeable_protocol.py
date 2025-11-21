"""
Pipeable protocol for the modgud domain layer.

This module defines the interface for pipeable objects that support
functional-style pipeline operations using the | operator with partial application.
"""

from __future__ import annotations
from typing import Any, Callable, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar('T')
R = TypeVar('R')


@runtime_checkable
class PipeableProtocol(Protocol):
    """
    Protocol for objects that support pipeline operations via | operator.
    
    This protocol defines the interface for pipeable objects that enable
    functional-style pipeline composition with partial application support.
    """
    
    def __or__(self, other: Union['PipeableProtocol', Any]) -> Any:
        """
        Enable func | func syntax for pipeline operations.
        
        Args:
            other: The next function in the pipeline
            
        Returns:
            Result of pipeline operation
        """
        ...
    
    def __ror__(self, other: Any) -> Any:
        """
        Enable value | func syntax (reverse or).
        
        This is the main entry point for pipeline operations starting with a value.
        
        Args:
            other: The value to pipe into this function
            
        Returns:
            The result of applying the function to the value
        """
        ...
    
    def __call__(self, *args: Any, **kwargs: Any) -> Union['PipeableProtocol', Any]:
        """
        Execute the wrapped function or create a partial application.
        
        This method tries to execute the function with the provided arguments.
        If execution fails due to missing required arguments, it returns a 
        partial application with bound arguments.
        
        Args:
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Either a new Pipeable with bound arguments or the function result
        """
        ...
    
    def __repr__(self) -> str:
        """Return a string representation of the Pipeable."""
        ...


@runtime_checkable
class PipeableFactoryProtocol(Protocol):
    """Interface for factories that create pipeable objects."""
    
    def create_pipeable(self, func: Callable[..., Any]) -> PipeableProtocol:
        """
        Create a pipeable wrapper around a function.
        
        Args:
            func: The function to make pipeable
            
        Returns:
            PipeableProtocol: Pipeable wrapper around the function
        """
        ...
    
    def pipeable_decorator(self, func: Callable[..., T]) -> PipeableProtocol:
        """
        Decorator that makes functions pipeable via | operator.
        
        Args:
            func: The function to make pipeable
            
        Returns:
            A Pipeable wrapper around the function
        """
        ...