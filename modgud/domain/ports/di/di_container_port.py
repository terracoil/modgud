"""Port definition for dependency injection container operations."""

from typing import Protocol, Type, TypeVar, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class DIContainerPort(Protocol):
  """Port for dependency injection container operations."""

  def resolve(self, interface_type: Type[T], name: str = 'default') -> T:
    """
    Resolve a dependency by interface type.

    :param interface_type: The interface/protocol type to resolve
    :param name: Named instance identifier
    :return: The resolved implementation instance
    :raises KeyError: If no implementation is registered
    """
    ...

  def register(self, interface_type: Type[T], implementation: T, name: str = 'default') -> None:
    """
    Register an implementation for an interface.

    :param interface_type: The interface/protocol type
    :param implementation: The implementation instance
    :param name: Named instance identifier
    """
    ...

  def has_registration(self, interface_type: Type[T], name: str = 'default') -> bool:
    """
    Check if an implementation is registered.

    :param interface_type: The interface/protocol type
    :param name: Named instance identifier
    :return: True if registered, False otherwise
    """
    ...

  def clear_registrations(self) -> None:
    """Clear all registered implementations."""
    ...
