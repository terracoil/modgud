"""Type definitions for the modgud library.

The domain layer is passive and contains no business logic - only type
definitions and protocols used across the library.
"""

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

GuardFunction = Callable[..., bool | str]
T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
F = TypeVar('F', bound=Callable[..., Any])  # a decorated callable, handed back as the same type


@dataclass(frozen=True, slots=True)
class eop_clause(Generic[T_co]):  # noqa: N801 - spelled like the eop_ forms it belongs to
  """One test paired with the value it selects; Elixir's word for a branch.

  In ``eop_cond`` the test is a condition. In ``eop_case`` it is a pattern, optionally wrapped
  in ``eop_when``. A clause must be written inside the form call: one built earlier has already
  evaluated its value, so the rewrite refuses it.
  """

  test: object
  value: T_co
