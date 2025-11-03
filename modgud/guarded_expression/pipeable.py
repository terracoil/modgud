"""
Pipeline integration for functional-style data transformation.

This module provides the @pipeable decorator which enables functional-style
pipeline operations using the | operator, similar to shell pipes or functional
languages like F#/Elixir.

Example:
    from modgud import pipeable, guarded_expression, positive

    @pipeable 
    def add(x, y):
        return x + y

    @pipeable
    def multiply(x, factor):
        return x * factor

    @pipeable
    @guarded_expression(positive("x"))
    def add_tax(x, rate=0.1):
        return x * (1 + rate)

    # Pipeline usage
    result = 5 | add(3) | multiply(2) | add_tax(0.15)  # Returns 18.4
"""

import functools
from typing import Any, Callable, TypeVar, Union

T = TypeVar('T')
R = TypeVar('R')


class Pipeable:
  """
  Wrapper that enables pipeline operations via __or__ overloading.
  
  This class wraps functions to make them work with the | operator for
  functional-style pipeline composition. It supports partial application
  through functools.partial and preserves function metadata.
  
  Args:
      func: The function to make pipeable
      bound_args: Pre-bound positional arguments 
      bound_kwargs: Pre-bound keyword arguments
  """
  
  def __init__(
    self, 
    func: Callable[..., Any], 
    bound_args: tuple[Any, ...] = (), 
    bound_kwargs: dict[str, Any] | None = None
  ) -> None:
    """Initialize the Pipeable wrapper."""
    self._func = func
    self._bound_args = bound_args
    self._bound_kwargs = bound_kwargs or {}
    
    # Preserve function metadata
    functools.update_wrapper(self, func)
    
    # Proxy important attributes that other decorators might need
    if hasattr(func, '__globals__'):
      self.__globals__ = func.__globals__
    if hasattr(func, '__code__'):
      self.__code__ = func.__code__
    if hasattr(func, '__module__'):
      self.__module__ = func.__module__
    
  def __or__(self, other: Union['Pipeable', Any]) -> Any:
    """
    Enable x | func syntax for pipeline operations.
    
    When used with the | operator, this method applies the wrapped function
    to the left-hand operand. If the right operand is itself a Pipeable,
    it will continue the pipeline.
    
    Args:
        other: The next function in the pipeline or a value to pipe into
        
    Returns:
        The result of applying this function, potentially wrapped in the next Pipeable
    """
    # If other is a Pipeable, we need to apply ourselves first, then pipe to other
    if isinstance(other, Pipeable):
      # This handles chaining: value | func1 | func2
      # We can't apply ourselves without a value, so this is an error
      raise TypeError(
        f"Cannot pipe {self._func.__name__} directly to {other._func.__name__}. "
        "Pipeline must start with a value."
      )
    
    # Other is a regular value - this shouldn't happen in normal usage
    # The __or__ is called on the LEFT operand, not the right
    raise TypeError(
      f"Invalid pipeline operation: {self._func.__name__} | {type(other).__name__}. "
      "Did you mean to use a value on the left side of the pipe?"
    )
  
  def __ror__(self, other: Any) -> Any:
    """
    Enable value | func syntax (reverse or).
    
    This is called when the left operand doesn't support __or__ with our type.
    This is the main entry point for pipeline operations starting with a value.
    
    Args:
        other: The value to pipe into this function
        
    Returns:
        The result of applying the function to the value
    """
    # Apply the function with bound arguments
    result = self._func(other, *self._bound_args, **self._bound_kwargs)
    
    # If the result is a Pipeable, return it for further chaining
    # Otherwise return the raw result
    return result
  
  def __call__(self, *args: Any, **kwargs: Any) -> Union['Pipeable', Any]:
    """
    Execute the wrapped function or create a partial application.
    
    This method tries to execute the function with the provided arguments.
    If execution fails due to missing required arguments, it returns a 
    partial application (new Pipeable with bound arguments).
    
    Args:
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Either a new Pipeable with bound arguments or the function result
    """
    # Combine bound args with new args
    all_args = self._bound_args + args
    all_kwargs = {**self._bound_kwargs, **kwargs}
    
    # Try to execute the function
    try:
      result = self._func(*all_args, **all_kwargs)
      return result
    except TypeError as e:
      # Check if it's a missing argument error
      error_str = str(e)
      if ("missing" in error_str and "required" in error_str) or \
         ("takes" in error_str and "positional" in error_str):
        # Not enough arguments yet, return a new partial
        return Pipeable(self._func, all_args, all_kwargs)
      # Re-raise if it's a different kind of TypeError
      raise
  
  def __repr__(self) -> str:
    """Return a string representation of the Pipeable."""
    if self._bound_args or self._bound_kwargs:
      args_repr = ', '.join(repr(arg) for arg in self._bound_args)
      kwargs_repr = ', '.join(f'{k}={v!r}' for k, v in self._bound_kwargs.items())
      all_args = ', '.join(filter(None, [args_repr, kwargs_repr]))
      return f'Pipeable({self._func.__name__}({all_args}))'
    return f'Pipeable({self._func.__name__})'


def pipeable(func: Callable[..., T]) -> Pipeable:
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
  # Handle built-in types that need special treatment
  if isinstance(func, type):
    # For types like str, int, float, create a converter function
    def type_converter(x):
      return func(x)
    type_converter.__name__ = func.__name__
    type_converter.__doc__ = f"Convert to {func.__name__}"
    return Pipeable(type_converter)
  
  # If the function is already decorated (has wrapper attributes), we need to be careful
  # Check if this function will be wrapped by other decorators
  if hasattr(func, '__wrapped__'):
    # This function has already been decorated, wrap it normally
    return Pipeable(func)
  
  # For better decorator composition, we'll create a wrapper that can be 
  # further decorated by other decorators like @implicit_return
  def pipeable_wrapper(fn):
    """Inner wrapper that creates the actual Pipeable instance."""
    return Pipeable(fn)
  
  # If we're being used as @pipeable without parentheses on a function definition,
  # return a Pipeable directly
  return Pipeable(func)