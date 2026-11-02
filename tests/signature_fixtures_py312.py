"""PEP 695 fixtures for the signature regression suite (Python 3.12+ syntax).

Kept apart from ``tests/signature_fixtures.py`` because Python 3.11 cannot even parse this
file; ``tests/conftest.py`` keeps it out of collection there. Each ``*_twin`` has the exact
signature and docstring of the decorated function above it. No ``from __future__ import
annotations``, for the same reason as in the 3.11 fixtures.
"""

from modgud import guarded_expression, implicit_return


def accept_all(*args: object, **kwargs: object) -> bool:
  """Guard that always passes; these cases are about type parameters, not validation."""
  return True


@guarded_expression(accept_all)
def identity[T](x: T) -> T:
  """Return x unchanged."""
  x  # noqa: B018


def identity_twin[T](x: T) -> T:
  """Return x unchanged."""
  return x


# Every kind of type parameter: bound, constrained, TypeVarTuple, ParamSpec.
@implicit_return()
def pair[K: str, V: (int, bytes), *Ts, **P](key: K, value: V, *rest: *Ts) -> tuple[K, V]:
  """Pair key with value and ignore the rest."""
  (key, value)  # noqa: B018


def pair_twin[K: str, V: (int, bytes), *Ts, **P](key: K, value: V, *rest: *Ts) -> tuple[K, V]:
  """Pair key with value and ignore the rest."""
  return (key, value)


@guarded_expression(accept_all, implicit_return=False)
def first[T](items: list[T], default: T | None = None) -> T | None:
  """Return the first item, or default when items is empty."""
  return items[0] if items else default


def first_twin[T](items: list[T], default: T | None = None) -> T | None:
  """Return the first item, or default when items is empty."""
  return items[0] if items else default


# The body itself names its type parameter, so the re-compiled body must see the same object.
@guarded_expression(accept_all)
def own_type_param[T](x: T) -> object:
  """Return the type parameter T as the body sees it."""
  T  # noqa: B018


def own_type_param_twin[T](x: T) -> object:
  """Return the type parameter T as the body sees it."""
  return T


class Box[T]:
  """Generic class whose method body names the class's type parameter."""

  def __init__(self, item: T) -> None:
    """Hold one item."""
    self.item: T = item

  @guarded_expression(accept_all)
  def get[D](self, default: D | None = None) -> T | D | None:
    """Return the item, or default when the item is None."""
    self.item if self.item is not None else default  # noqa: B018

  def get_twin[D](self, default: D | None = None) -> T | D | None:
    """Return the item, or default when the item is None."""
    return self.item if self.item is not None else default

  @guarded_expression(accept_all)
  def item_type(self) -> object:
    """Return the class type parameter T as the method body sees it."""
    T  # noqa: B018

  def item_type_twin(self) -> object:
    """Return the class type parameter T as the method body sees it."""
    return T
