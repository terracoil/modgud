"""Decorators for expression-oriented programming.

This sub-package contains all decorator implementations for modgud's
expression-oriented features.
"""

# Import bootstrap to ensure services are configured before decorators are loaded
from modgud.app.bootstrap import configure_dependencies

# Configure dependencies before importing decorators (intentional E402)
configure_dependencies()

from .chained_expression_decorator import ChainedExpressionDecorator  # noqa: E402
from .guarded_expression import guarded_expression  # noqa: E402
from .implicit_return_decorator import implicit_return  # noqa: E402
from .inject_decorator import DependencyInjectionError, Inject, inject, inject_auto  # noqa: E402
from .pipeable import pipeable  # noqa: E402
from .safe_expression_decorator import SafeExpressionDecorator  # noqa: E402

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
