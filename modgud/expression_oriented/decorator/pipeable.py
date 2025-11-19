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
    bound_kwargs: dict[str, Any] | None = None,
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
      
    # Provide access to the underlying function for direct calls (useful for recursion)
    self.func = func

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
        f'Cannot pipe {self._func.__name__} directly to {other._func.__name__}. '
        'Pipeline must start with a value.'
      )

    # Other is a regular value - this shouldn't happen in normal usage
    # The __or__ is called on the LEFT operand, not the right
    raise TypeError(
      f'Invalid pipeline operation: {self._func.__name__} | {type(other).__name__}. '
      'Did you mean to use a value on the left side of the pipe?'
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
    import inspect

    # Handle parameter binding conflicts intelligently
    try:
      sig = inspect.signature(self._func)
      params = list(sig.parameters.keys())

      # Check if this is a bound method (has bound args and first param is likely 'self')
      is_bound_method = (
        self._bound_args
        and len(params) > 0
        and params[0] in ('self', 'cls')
        and hasattr(self._bound_args[0], '__class__')
      )

      if is_bound_method:
        # This is a bound method: self is in bound_args, piped value becomes next param
        final_args = self._bound_args + (other,)
        result = self._func(*final_args, **self._bound_kwargs)
      elif params and params[0] in self._bound_kwargs:
        # First parameter explicitly in kwargs - handle conflict
        first_param_value = self._bound_kwargs[params[0]]
        remaining_kwargs = {k: v for k, v in self._bound_kwargs.items() if k != params[0]}
        final_args = (first_param_value, other) + self._bound_args
        result = self._func(*final_args, **remaining_kwargs)
      elif self._bound_args:
        # Regular function with bound args: piped value goes first, then bound args
        final_args = (other,) + self._bound_args
        result = self._func(*final_args, **self._bound_kwargs)
      elif len(params) == 0:
        # Function takes no arguments: ignore piped value
        result = self._func(**self._bound_kwargs)
      else:
        # Standard case: piped value becomes first parameter
        result = self._func(other, **self._bound_kwargs)

    except TypeError as e:
      # Distinguish between parameter binding errors and function execution errors
      error_msg = str(e)
      if (
        'multiple values' in error_msg
        or 'takes' in error_msg
        and 'positional argument' in error_msg
        or 'unexpected keyword argument' in error_msg
        or 'required positional argument' in error_msg
      ):
        # This is a parameter binding error - provide helpful message
        raise TypeError(
          f'Pipeline parameter binding failed for {self._func.__name__}: {e}. '
          f'Check for parameter conflicts between piped value and bound arguments.'
        ) from e
      else:
        # This is likely a function execution error - let it propagate normally
        raise

    # If the result is a Pipeable, return it for further chaining
    # Otherwise return the raw result
    return result

  def __call__(self, *args: Any, **kwargs: Any) -> Union['Pipeable', Any]:
    """
    Execute the wrapped function or create a partial application.

    When called with enough arguments to satisfy the function signature,
    execute directly. Otherwise, create a partial application for pipeline usage.

    Args:
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Function result if fully satisfied, or Pipeable for partial application

    """
    import inspect

    # Special case: if no args and no kwargs, check if this is a no-argument function
    if not args and not kwargs:
      # Check if the function takes no arguments (excluding self for methods)
      sig = inspect.signature(self._func)
      params = list(sig.parameters.keys())
      
      # Filter out 'self' for methods
      non_self_params = [p for p in params if p not in ('self', 'cls')]
      
      if len(non_self_params) == 0 and not self._bound_args:
        # This is a no-argument function, execute it directly
        return self._func(**self._bound_kwargs)
      
      # Otherwise return self unchanged
      return self

    # Combine all arguments - bound args come first, then new args  
    all_args = self._bound_args + args
    all_kwargs = {**self._bound_kwargs, **kwargs}

    sig = inspect.signature(self._func)
    
    # Analyze function parameters
    params = list(sig.parameters.values())
    has_var_positional = any(p.kind == p.VAR_POSITIONAL for p in params)
    has_var_keyword = any(p.kind == p.VAR_KEYWORD for p in params)
    has_defaults = any(p.default != p.empty for p in sig.parameters.values())
    
    # Count regular parameters (excluding *args and **kwargs)
    regular_params = [p for p in params if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]
    required_params = [p for p in regular_params if p.default == p.empty]
    
    # Determine if this is a method and count provided arguments
    is_method = (
      self._bound_args 
      and len(sig.parameters) > 0 
      and list(sig.parameters.keys())[0] in ('self', 'cls')
    )
    
    if is_method:
      num_provided = len(all_args) - 1 + len(all_kwargs)
      num_required = max(0, len(required_params) - 1)
      total_regular = max(0, len(regular_params) - 1)
    else:
      num_provided = len(all_args) + len(all_kwargs)
      num_required = len(required_params)
      total_regular = len(regular_params)
    
    # Special case: decorator wrappers with *args, **kwargs and single argument
    # This prevents premature execution during partial application
    if has_var_positional and has_var_keyword and len(all_args) == 1 and not all_kwargs:
      return Pipeable(self._func, all_args, all_kwargs)
    
    # Decision logic
    if has_defaults:
      # Functions with defaults: only execute if ALL parameters provided
      if num_provided >= total_regular:
        try:
          sig.bind(*all_args, **all_kwargs)
          return self._func(*all_args, **all_kwargs)
        except TypeError:
          return Pipeable(self._func, all_args, all_kwargs)
      else:
        return Pipeable(self._func, all_args, all_kwargs)
    else:
      # Functions without defaults: execute if all required params satisfied
      if num_provided >= num_required:
        try:
          sig.bind(*all_args, **all_kwargs)
          return self._func(*all_args, **all_kwargs)
        except TypeError:
          return Pipeable(self._func, all_args, all_kwargs)
      else:
        return Pipeable(self._func, all_args, all_kwargs)

  def __get__(self, instance, owner):
    """
    Implement descriptor protocol for method binding.

    This allows @pipeable to work correctly with instance methods.
    When accessed as obj.method, it returns a new Pipeable with self pre-bound.
    """
    if instance is None:
      # Accessed from class, return unbound pipeable
      return self

    # Accessed from instance, bind self as first argument
    return Pipeable(self._func, (instance,) + self._bound_args, self._bound_kwargs)

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
  Make functions pipeable via | operator.

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
    type_converter.__doc__ = f'Convert to {func.__name__}'
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
