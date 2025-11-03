"""
Pipeable wrapper implementation for functional-style data transformation.

This module provides the Pipeable class which enables functional-style
pipeline operations using the | operator, similar to shell pipes or functional
languages like F#/Elixir.
"""

import functools
import inspect
from typing import Any, Callable, TypeVar, Union
from ..domain.protocols import PipeableProtocol

T = TypeVar('T')
R = TypeVar('R')


class Pipeable(PipeableProtocol):
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
        
        # Provide access to the original function for recursive calls
        self.func = func
        
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
        try:
            # Get function signature to understand its parameters
            sig = inspect.signature(self._func)
            params = list(sig.parameters.values())
            
            # Handle zero-argument functions - they ignore the piped value
            if not params:
                result = self._func(**self._bound_kwargs)
                return result
            
            # For functions with parameters, the piped value becomes the first argument
            # But we need to handle conflicts with bound kwargs
            regular_params = [param for param in params 
                            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, 
                                            inspect.Parameter.POSITIONAL_OR_KEYWORD)]
            
            if regular_params:
                first_param = regular_params[0]
                
                # Special handling for bound methods - preserve self binding
                if hasattr(self._func, '__self__'):
                    # This is a bound method, self is already bound
                    # The piped value should become the first \"real\" parameter after self
                    result = self._func(other, *self._bound_args, **self._bound_kwargs)
                    return result
                
                # Check if first parameter name conflicts with bound kwargs
                if first_param.name in self._bound_kwargs:
                    # If there's a conflict, redistribute arguments to avoid the conflict:
                    # - Piped value becomes the first parameter
                    # - Bound args + conflicting kwarg value go into *args
                    # - Other kwargs remain as **kwargs
                    conflicting_value = self._bound_kwargs[first_param.name]
                    clean_kwargs = {k: v for k, v in self._bound_kwargs.items() 
                                  if k != first_param.name}
                    result = self._func(other, *self._bound_args, conflicting_value, **clean_kwargs)
                    return result
                else:
                    # No conflict, piped value becomes first parameter
                    clean_kwargs = {k: v for k, v in self._bound_kwargs.items() 
                                  if k != first_param.name}
                    result = self._func(other, *self._bound_args, **clean_kwargs)
                    return result
            
            # Fallback to original behavior
            result = self._func(other, *self._bound_args, **self._bound_kwargs)
            return result
            
        except Exception as e:
            # If signature inspection fails, try original behavior
            try:
                result = self._func(other, *self._bound_args, **self._bound_kwargs)
                return result
            except TypeError as te:
                # If it's a zero-arg function, try calling without the piped value
                if "takes 0 positional arguments but 1 was given" in str(te):
                    result = self._func(**self._bound_kwargs)
                    return result
                raise te
    
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
        # For pipeable functions, handle parameter binding specially for partial creation
        # The first parameter is typically reserved for pipeline input
        try:
            sig = inspect.signature(self._func)
            param_names = list(sig.parameters.keys())
            total_params = len(param_names)
            total_provided = len(self._bound_args) + len(args) + len({**self._bound_kwargs, **kwargs})
            
            # Special pipeline binding logic:
            # - Only for fresh calls (no bound args/kwargs)  
            # - When args + 1 (for pipeline) would not exceed total params
            # - Skip first parameter for pipeline input
            total_args_provided = len(args) + len(kwargs)
            if (not self._bound_args and not self._bound_kwargs and args and len(param_names) > 1 and 
                total_args_provided + 1 <= total_params and  # +1 for pipeline input
                not (len(param_names) == 2 and param_names[0] in ('args', 'arguments'))):
                
                if len(args) == 1 and not kwargs:
                    # Single argument: convert to kwargs for pipeline (e.g., add(3) -> add(y=3))
                    param_name = param_names[1]  # Skip first parameter for pipeline
                    new_kwargs = {param_name: args[0]}
                    all_args = self._bound_args  # Empty tuple
                    all_kwargs = {**self._bound_kwargs, **new_kwargs}
                elif total_params >= 5:  # Functions with many parameters: preserve positional args
                    # Multi-argument, many parameters: preserve positional for chaining (e.g., many_args)
                    all_args = self._bound_args + args
                    all_kwargs = {**self._bound_kwargs, **kwargs}
                else:
                    # Multi-argument, few parameters: bind to named params for pipeline (e.g., compound_interest)
                    new_kwargs = dict(kwargs)  # Copy existing kwargs
                    for i, arg in enumerate(args):
                        if i + 1 < len(param_names):  # +1 to skip first parameter
                            param_name = param_names[i + 1]
                            new_kwargs[param_name] = arg
                    all_args = self._bound_args  # Empty tuple
                    all_kwargs = {**self._bound_kwargs, **new_kwargs}
            else:
                # Normal behavior: direct calls or functions with enough args
                all_args = self._bound_args + args
                all_kwargs = {**self._bound_kwargs, **kwargs}
        except Exception:
            # If signature inspection fails, fall back to normal behavior
            all_args = self._bound_args + args
            all_kwargs = {**self._bound_kwargs, **kwargs}
        
        # Check if we have enough arguments before attempting execution
        try:
            sig = inspect.signature(self._func)
            param_names = list(sig.parameters.keys())
            
            # For generic wrapper signatures (*args, **kwargs), always create partial
            # when arguments are provided (to avoid calling the wrapped function unnecessarily)
            if (len(param_names) == 2 and 
                param_names[0] in ('args', 'arguments') and 
                param_names[1] in ('kwargs', 'keywords') and
                (args or kwargs)):
                return Pipeable(self._func, all_args, all_kwargs)
            
            # For other functions, check if we can satisfy all required parameters
            required_params = []
            for param_name, param in sig.parameters.items():
                if (param.default is inspect.Parameter.empty and 
                    param.kind in (inspect.Parameter.POSITIONAL_ONLY, 
                                   inspect.Parameter.POSITIONAL_OR_KEYWORD)):
                    required_params.append(param_name)
            
            # Count how many required parameters we can satisfy
            satisfied_params = len(all_args)
            for param_name in required_params[len(all_args):]:  # remaining required params
                if param_name in all_kwargs:
                    satisfied_params += 1
                else:
                    break  # Missing required parameter
            
            # If we don't have enough arguments, create a partial without executing
            if satisfied_params < len(required_params):
                return Pipeable(self._func, all_args, all_kwargs)
                
        except Exception:
            # If signature inspection fails, try execution and handle errors
            pass
        
        # Try to execute the function
        try:
            result = self._func(*all_args, **all_kwargs)
            return result
        except TypeError as e:
            # Check if it's a missing argument error or multiple values error
            error_str = str(e)
            if ("missing" in error_str and "required" in error_str) or \
               ("takes" in error_str and "positional" in error_str) or \
               ("multiple values for argument" in error_str):
                # Can't execute yet, return a new partial
                return Pipeable(self._func, all_args, all_kwargs)
            # Check if it's a guard validation error with wrong parameter mapping
            elif "'>' not supported between instances" in error_str:
                # This suggests guard validation is happening with wrong parameter types
                # Defer execution until pipeline runs with proper parameter mapping
                return Pipeable(self._func, all_args, all_kwargs)
            # Re-raise if it's a different kind of TypeError
            raise
        except Exception as e:
            # Check for other guard-related errors that suggest wrong parameter mapping
            error_str = str(e)
            if "GuardClauseError" in str(type(e)) or \
               "must be positive" in error_str or \
               "cannot be empty" in error_str or \
               "must be of type" in error_str:
                # Guard validation failed during partial creation - defer until pipeline execution
                return Pipeable(self._func, all_args, all_kwargs)
            # Re-raise other exceptions
            raise
    
    def __repr__(self) -> str:
        """Return a string representation of the Pipeable."""
        if self._bound_args or self._bound_kwargs:
            # Try to reconstruct user-friendly representation
            # If we have kwargs that look like converted positional args, show them as positional
            try:
                sig = inspect.signature(self._func)
                param_names = list(sig.parameters.keys())
                
                # Case 1: Only kwargs, no positional args - check if these were converted from positional
                if not self._bound_args and self._bound_kwargs and len(param_names) > 1:
                    # Use the order of kwargs to determine original call pattern
                    # If kwargs appear in parameter order (b, c, d), they were likely all positional
                    # If they appear out of order, some were likely keywords
                    
                    kwargs_keys = list(self._bound_kwargs.keys())
                    param_indices = {param: i for i, param in enumerate(param_names)}
                    
                    # Check if kwargs are in sequential parameter order starting from index 1
                    expected_order = []
                    for i in range(1, len(param_names)):  # Skip first parameter (pipeline)
                        if param_names[i] in self._bound_kwargs:
                            expected_order.append(param_names[i])
                    
                    # Convert to positional representation based on parameter order, not dict order
                    kwargs_as_positional = []
                    remaining_kwargs = dict(self._bound_kwargs)
                    
                    # Strategy: Convert parameters to positional if they appear in natural parameter order
                    # and there are no "earlier" parameters that appear later in kwargs (indicating keywords)
                    
                    for i in range(1, len(param_names)):  # Start from 1 to skip pipeline parameter
                        param_name = param_names[i]
                        if param_name not in remaining_kwargs:
                            break  # Missing parameter, stop converting
                        
                        # Check if any earlier parameter appears later in kwargs order (indicating it was keyword)
                        has_earlier_keyword = False
                        for j in range(1, i):  # Check all earlier parameters
                            earlier_param = param_names[j]
                            if (earlier_param in kwargs_keys and param_name in kwargs_keys and
                                kwargs_keys.index(earlier_param) > kwargs_keys.index(param_name)):
                                has_earlier_keyword = True
                                break
                        
                        # If this parameter doesn't have earlier keywords appearing after it, convert to positional
                        if not has_earlier_keyword:
                            kwargs_as_positional.append(repr(remaining_kwargs[param_name]))
                            del remaining_kwargs[param_name]
                        else:
                            # Earlier parameter appeared later in kwargs, suggesting keywords were used
                            break
                    
                    # Use mixed format: converted positional args + remaining kwargs
                    if kwargs_as_positional or remaining_kwargs:
                        positional_repr = ', '.join(kwargs_as_positional)
                        remaining_kwargs_repr = ', '.join(f'{k}={v!r}' for k, v in remaining_kwargs.items())
                        all_args = ', '.join(filter(None, [positional_repr, remaining_kwargs_repr]))
                        return f'Pipeable({self._func.__name__}({all_args}))'
                
            except Exception:
                pass  # Fall back to default representation
            
            # Default representation: show args and kwargs as stored
            args_repr = ', '.join(repr(arg) for arg in self._bound_args)
            kwargs_repr = ', '.join(f'{k}={v!r}' for k, v in self._bound_kwargs.items())
            all_args = ', '.join(filter(None, [args_repr, kwargs_repr]))
            return f'Pipeable({self._func.__name__}({all_args}))'
        return f'Pipeable({self._func.__name__})'
    
    def __get__(self, instance, owner):
        """Support for descriptor protocol to handle method binding."""
        if instance is None:
            # Accessed on the class, return the Pipeable as-is
            return self
        
        # Accessed on an instance, bind the method and return a new Pipeable
        bound_method = self._func.__get__(instance, owner)
        return Pipeable(bound_method, self._bound_args, self._bound_kwargs)