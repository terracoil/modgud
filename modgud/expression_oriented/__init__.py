"""
Expression-oriented programming features for modgud.

This module provides decorators and types for functional-style programming patterns
including guard clauses, implicit returns, pipeable functions, monadic operations,
safe expressions, and method chaining. All classes follow the single class per file principle.

The package is organized into logical sub-packages:
- decorator/: All decorators (guarded_expression, pipeable, etc.)
- factory/: Factory classes for complex type creation
- results/: Result monad types (Ok, Err)
- maybe/: Maybe monad types (Some, Nothing)
- tool/: Utility classes and tools
"""

# Primary decorators
from .decorator.chained_expression_decorator import ChainedExpressionDecorator
from .decorator.guarded_expression import guarded_expression
from .decorator.implicit_return_decorator import implicit_return
from .decorator.inject_decorator import DependencyInjectionError, Inject, inject, inject_auto
from .decorator.pipeable import pipeable
from .decorator.safe_expression_decorator import SafeExpressionDecorator
from .factory.chained_expression_factory import ChainedExpressionFactory
from modgud.expression_oriented.maybe.maybe_factory import MaybeFactory

# Factory classes
from .factory.result_factory import ResultFactory
from .factory.safe_expression_factory import SafeExpressionFactory

# Maybe types
from ..domain.maybe_protocol import MaybeProtocol as Maybe
from .maybe.nothing_maybe import Nothing
from .maybe.some_maybe import Some
from .results.err_result import Err
from .results.ok_result import Ok

# Result types
from ..domain.result_protocol import ResultProtocol as Result

# Tools
from .tool.chainable_expression import ChainableExpression

# Convenient aliases for common usage patterns
safe_expression = SafeExpressionFactory.safe_expression
chained_expression = ChainedExpressionFactory.chained_expression
chain = ChainedExpressionFactory.chain

__all__ = [
  # Primary decorators
  'guarded_expression',
  'implicit_return',
  'pipeable',
  'SafeExpressionDecorator',
  'ChainedExpressionDecorator',
  'Inject',
  'inject',
  'inject_auto',
  'DependencyInjectionError',
  # Result types
  'Result',
  'Ok',
  'Err',
  'ResultFactory',
  # Maybe types
  'Maybe',
  'Some',
  'Nothing',
  'MaybeFactory',
  # Factory classes
  'SafeExpressionFactory',
  'ChainedExpressionFactory',
  # Tools
  'ChainableExpression',
  # Convenient decorator aliases
  'safe_expression',
  'chained_expression',
  'chain',
]
